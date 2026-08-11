# ============================================================
# database.py — لایه داده: SQLite3 + Pandas
#
# مسئولیت‌ها:
#   ۱. ساخت و نگهداری اسکیمای SQLite
#   ۲. sync از فایل اکسل به جدول products
#   ۳. توابع query برای جستجو، بازیابی، و آمار
#   ۴. شناسایی خودکار نام ستون‌های اکسل
#
# این لایه هیچ وابستگی‌ای به Dash ندارد و
# به تنهایی قابل تست و استفاده مجدد است.
# ============================================================

import sqlite3
import json
import os
import io
import base64
from contextlib import contextmanager
from typing import Optional

import pandas as pd

from config import (
    DB_PATH,
    COL_PRODUCT_NAME,
    COL_PRODUCT_CODE,
    COL_DESCRIPTION,
    COL_STOCK_QTY,
    COL_WAREHOUSE,
)

# ──────────────────────────────────────────────
# DDL — تعریف اسکیمای جدول‌ها
# ──────────────────────────────────────────────

_DDL_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    category           TEXT    NOT NULL,
    product_name       TEXT    NOT NULL,
    product_code       TEXT,
    description        TEXT,
    stock_qty          INTEGER DEFAULT 0,
    warehouse_location TEXT,
    extra_attributes   TEXT    DEFAULT '{}',
    -- کلید مرکب برای جلوگیری از ورودی تکراری هنگام sync
    UNIQUE (category, product_name, product_code)
);
"""

_DDL_SYNC_LOG = """
CREATE TABLE IF NOT EXISTS sync_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    synced_at   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    source_file TEXT,
    rows_added  INTEGER DEFAULT 0,
    rows_updated INTEGER DEFAULT 0,
    status      TEXT,
    message     TEXT
);
"""

_DDL_INDEX = """
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);
CREATE INDEX IF NOT EXISTS idx_products_code
    ON products (product_code);
"""

# ──────────────────────────────────────────────
# اتصال و Context Manager
# ──────────────────────────────────────────────

@contextmanager
def get_connection():
    """
    یک Context Manager برای اتصال امن به SQLite.
    در صورت خطا، تراکنش rollback می‌شود.
    """
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row          # دسترسی به ستون‌ها با نام
    conn.execute("PRAGMA journal_mode=WAL") # بهینه‌سازی برای write concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_db() -> None:
    """
    جداول و ایندکس‌های لازم را در SQLite می‌سازد.
    اگر قبلاً ساخته شده باشند، بدون خطا رد می‌شود (IF NOT EXISTS).
    این تابع در startup برنامه صدا زده می‌شود.
    """
    with get_connection() as conn:
        conn.executescript(_DDL_PRODUCTS)
        conn.executescript(_DDL_SYNC_LOG)
        conn.executescript(_DDL_INDEX)


def reset_db() -> None:
    """
    تمام داده‌های جدول products را پاک می‌کند (فقط Admin).
    ساختار جدول‌ها حفظ می‌شود.
    """
    with get_connection() as conn:
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM sync_log")


# ──────────────────────────────────────────────
# کشف ستون — Column Detection
# ──────────────────────────────────────────────

def _find_col(columns: list[str], candidates: list[str]) -> Optional[str]:
    """
    اولین ستون موجود از لیست کاندیداها را در columns پیدا می‌کند.
    مقایسه case-insensitive انجام می‌شود.

    Args:
        columns: لیست نام ستون‌های DataFrame
        candidates: نام‌های ممکن به ترتیب اولویت

    Returns:
        نام ستون در DataFrame یا None
    """
    col_lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in col_lower:
            return col_lower[cand.lower()]
    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    نام ستون‌های DataFrame را نرمال‌سازی می‌کند:
    - فاصله‌های اضافی حذف می‌شوند
    - به حروف کوچک تبدیل می‌شوند
    - فاصله با _ جایگزین می‌شود
    """
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df


# ──────────────────────────────────────────────
# پردازش یک DataFrame به ستون‌های استاندارد
# ──────────────────────────────────────────────

class SheetParseResult:
    """
    نتیجه پارس یک شیت اکسل را نگه می‌دارد.

    Attributes:
        df: DataFrame استانداردشده آماده برای insert
        warnings: هشدارهای غیربحرانی (ستون گم‌شده و ...)
        error: پیام خطای بحرانی (اگر شیت قابل استفاده نباشد)
    """
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.warnings: list[str] = []
        self.error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.df is not None


def parse_sheet(df_raw: pd.DataFrame, sheet_name: str) -> SheetParseResult:
    """
    یک DataFrame خام از اکسل را به ساختار استاندارد products تبدیل می‌کند.

    ستون‌های شناسایی‌شده:
        product_name (اجباری), product_code, description,
        stock_qty, warehouse_location, extra_attributes (بقیه ستون‌ها)

    Args:
        df_raw: DataFrame خوانده‌شده از اکسل
        sheet_name: نام شیت برای ثبت در ستون category

    Returns:
        SheetParseResult با df استاندارد یا پیام خطا
    """
    result = SheetParseResult()
    df = _normalize_columns(df_raw.copy())
    df = df.dropna(how="all")  # حذف ردیف‌های کاملاً خالی

    if df.empty:
        result.error = f"Sheet '{sheet_name}' is empty."
        return result

    # ── ستون اجباری: product_name ─────────────────────────
    name_col = _find_col(df.columns.tolist(), COL_PRODUCT_NAME)
    if name_col is None:
        result.error = (
            f"Sheet '{sheet_name}' has no recognized product name column. "
            f"Expected one of: {COL_PRODUCT_NAME}"
        )
        return result

    # ── ستون‌های اختیاری با fallback به None ───────────────
    code_col  = _find_col(df.columns.tolist(), COL_PRODUCT_CODE)
    desc_col  = _find_col(df.columns.tolist(), COL_DESCRIPTION)
    qty_col   = _find_col(df.columns.tolist(), COL_STOCK_QTY)
    wh_col    = _find_col(df.columns.tolist(), COL_WAREHOUSE)

    if code_col is None:
        result.warnings.append(
            f"Sheet '{sheet_name}': no product code column found "
            f"(tried: {COL_PRODUCT_CODE}). Values will be empty."
        )
    if desc_col is None:
        result.warnings.append(
            f"Sheet '{sheet_name}': no description column found."
        )

    # ── ستون‌های "اضافه" که به JSON ذخیره می‌شوند ──────────
    known_cols = {
        c for c in [name_col, code_col, desc_col, qty_col, wh_col]
        if c is not None
    }
    extra_cols = [c for c in df.columns if c not in known_cols]

    # ── ساخت DataFrame استاندارد ────────────────────────────
    rows = []
    for _, row in df.iterrows():
        pname = str(row[name_col]).strip() if name_col else ""
        if not pname or pname.lower() in ("nan", "none", ""):
            continue   # رد کردن ردیف‌های بدون نام

        # موجودی را به عدد صحیح تبدیل می‌کنیم
        try:
            qty = int(float(str(row[qty_col]).replace(",", ""))) if qty_col else 0
        except (ValueError, TypeError):
            qty = 0

        # ساخت JSON از ستون‌های اضافی
        extra = {}
        for ec in extra_cols:
            val = row.get(ec, "")
            if str(val).lower() not in ("nan", "none", ""):
                extra[ec] = str(val)

        rows.append({
            "category":           sheet_name,
            "product_name":       pname,
            "product_code":       str(row[code_col]).strip() if code_col else "",
            "description":        str(row[desc_col]).strip() if desc_col else "",
            "stock_qty":          qty,
            "warehouse_location": str(row[wh_col]).strip() if wh_col else "",
            "extra_attributes":   json.dumps(extra, ensure_ascii=False),
        })

    if not rows:
        result.error = f"Sheet '{sheet_name}' has no valid product rows."
        return result

    result.df = pd.DataFrame(rows)
    return result


# ──────────────────────────────────────────────
# Sync: اکسل → SQLite
# ──────────────────────────────────────────────

class SyncResult:
    """خلاصه نتیجه عملیات sync."""
    def __init__(self):
        self.rows_added:   int = 0
        self.rows_updated: int = 0
        self.skipped_sheets: list[str] = []
        self.warnings:     list[str] = []
        self.errors:       list[str] = []
        self.source_file:  str = ""

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def sync_excel_to_db(
    filepath: Optional[str] = None,
    file_content_b64: Optional[str] = None,
    filename: Optional[str] = None,
) -> SyncResult:
    """
    فایل اکسل را می‌خواند و محتوا را به SQLite sync می‌کند.
    از دو روش ورودی پشتیبانی می‌کند:
      ۱. filepath: مسیر فایل روی دیسک
      ۲. file_content_b64: محتوای base64 (از dcc.Upload)

    منطق sync:
      - اگر ترکیب (category, product_name, product_code) وجود داشت → UPDATE
      - در غیر این صورت → INSERT

    Args:
        filepath: مسیر فایل اکسل روی دیسک
        file_content_b64: رشته base64 از dcc.Upload (شامل پیشوند data:...)
        filename: نام فایل آپلودشده برای ثبت در لاگ

    Returns:
        SyncResult با خلاصه عملیات
    """
    result = SyncResult()

    # ── بارگذاری فایل ─────────────────────────────────────
    try:
        if file_content_b64:
            # جداکردن header از base64 (فرمت: "data:...;base64,XXXX")
            _, b64_data = file_content_b64.split(",", 1)
            file_bytes = base64.b64decode(b64_data)
            workbook = pd.read_excel(
                io.BytesIO(file_bytes),
                sheet_name=None,
                dtype=str,
                keep_default_na=False,
            )
            result.source_file = filename or "uploaded_file.xlsx"
        elif filepath and os.path.isfile(filepath):
            workbook = pd.read_excel(
                filepath,
                sheet_name=None,
                dtype=str,
                keep_default_na=False,
            )
            result.source_file = os.path.basename(filepath)
        else:
            result.errors.append(
                f"Excel file not found: '{filepath}'. "
                "Upload a file via the UI or place 'code.xlsx' next to app.py."
            )
            _log_sync(result)
            return result
    except Exception as exc:
        result.errors.append(f"Failed to read Excel file: {exc}")
        _log_sync(result)
        return result

    if not workbook:
        result.errors.append("The Excel workbook contains no sheets.")
        _log_sync(result)
        return result

    # ── پردازش هر شیت ─────────────────────────────────────
    with get_connection() as conn:
        for sheet_name, df_raw in workbook.items():
            parse = parse_sheet(df_raw, sheet_name)
            result.warnings.extend(parse.warnings)

            if not parse.ok:
                result.skipped_sheets.append(sheet_name)
                result.warnings.append(parse.error or f"Skipped sheet '{sheet_name}'.")
                continue

            df = parse.df

            # ── INSERT OR REPLACE با UPSERT منطق ──────────
            for _, row in df.iterrows():
                # بررسی وجود رکورد با کلید مرکب
                cur = conn.execute(
                    "SELECT id FROM products "
                    "WHERE category=? AND product_name=? AND product_code=?",
                    (row["category"], row["product_name"], row["product_code"]),
                )
                existing = cur.fetchone()

                if existing:
                    conn.execute(
                        """
                        UPDATE products SET
                            description=?,
                            stock_qty=?,
                            warehouse_location=?,
                            extra_attributes=?
                        WHERE id=?
                        """,
                        (
                            row["description"],
                            row["stock_qty"],
                            row["warehouse_location"],
                            row["extra_attributes"],
                            existing["id"],
                        ),
                    )
                    result.rows_updated += 1
                else:
                    conn.execute(
                        """
                        INSERT INTO products
                            (category, product_name, product_code,
                             description, stock_qty, warehouse_location, extra_attributes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["category"],
                            row["product_name"],
                            row["product_code"],
                            row["description"],
                            row["stock_qty"],
                            row["warehouse_location"],
                            row["extra_attributes"],
                        ),
                    )
                    result.rows_added += 1

    _log_sync(result)
    return result


def _log_sync(result: SyncResult) -> None:
    """نتیجه sync را در جدول sync_log ثبت می‌کند."""
    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sync_log
                    (source_file, rows_added, rows_updated, status, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result.source_file,
                    result.rows_added,
                    result.rows_updated,
                    "success" if result.success else "error",
                    "; ".join(result.errors + result.warnings) or "OK",
                ),
            )
    except Exception:
        pass  # لاگ نباید باعث خراب شدن جریان اصلی شود


# ──────────────────────────────────────────────
# توابع Query
# ──────────────────────────────────────────────

def get_categories() -> list[str]:
    """
    لیست تمام دسته‌بندی‌های موجود در دیتابیس را برمی‌گرداند.
    برای پر کردن dropdown category استفاده می‌شود.
    """
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT category FROM products ORDER BY category"
        ).fetchall()
    return [r["category"] for r in rows]


def get_products_by_category(category: str) -> list[dict]:
    """
    تمام محصولات یک دسته‌بندی را برمی‌گرداند.
    برای پر کردن dropdown محصول استفاده می‌شود.

    Args:
        category: نام دسته‌بندی

    Returns:
        لیست دیکشنری با کلیدهای id, product_name, product_code
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, product_name, product_code
            FROM products
            WHERE category = ?
            ORDER BY product_name
            """,
            (category,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_product_by_id(product_id: int) -> Optional[dict]:
    """
    اطلاعات کامل یک محصول را با ID برمی‌گرداند.

    Args:
        product_id: کلید اصلی رکورد

    Returns:
        دیکشنری کامل محصول یا None
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    # تبدیل JSON extra_attributes به دیکشنری Python
    try:
        result["extra_attributes"] = json.loads(result.get("extra_attributes") or "{}")
    except (json.JSONDecodeError, TypeError):
        result["extra_attributes"] = {}
    return result


def search_products(
    query: str,
    category: Optional[str] = None,
    limit: int = 200,
) -> list[dict]:
    """
    جستجوی global با LIKE در ستون‌های product_name, product_code, description.
    امکان فیلتر کردن بر اساس category نیز وجود دارد.

    Args:
        query: رشته جستجو (حداقل ۱ کاراکتر)
        category: فیلتر اختیاری بر اساس دسته‌بندی
        limit: حداکثر تعداد نتایج

    Returns:
        لیست دیکشنری ردیف‌های مطابق
    """
    pattern = f"%{query.strip()}%"
    params: list = [pattern, pattern, pattern]

    sql = """
        SELECT id, category, product_name, product_code,
               description, stock_qty, warehouse_location
        FROM products
        WHERE (
            product_name       LIKE ? OR
            product_code       LIKE ? OR
            description        LIKE ?
        )
    """

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY category, product_name LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    return [dict(r) for r in rows]


def get_db_stats() -> dict:
    """
    آمار کلی دیتابیس را برای KPI کارت‌ها برمی‌گرداند.

    Returns:
        دیکشنری با کلیدهای:
            total_skus, total_stock, category_count,
            missing_code, missing_desc, last_sync
    """
    with get_connection() as conn:
        stats = conn.execute(
            """
            SELECT
                COUNT(*)                                    AS total_skus,
                COALESCE(SUM(stock_qty), 0)                AS total_stock,
                COUNT(DISTINCT category)                   AS category_count,
                SUM(CASE WHEN product_code = '' OR product_code IS NULL
                         THEN 1 ELSE 0 END)                AS missing_code,
                SUM(CASE WHEN description  = '' OR description  IS NULL
                         THEN 1 ELSE 0 END)                AS missing_desc
            FROM products
            """
        ).fetchone()

        last_sync_row = conn.execute(
            "SELECT synced_at FROM sync_log ORDER BY id DESC LIMIT 1"
        ).fetchone()

    result = dict(stats) if stats else {
        "total_skus": 0, "total_stock": 0, "category_count": 0,
        "missing_code": 0, "missing_desc": 0,
    }
    result["last_sync"] = last_sync_row["synced_at"] if last_sync_row else "Never"
    return result


def get_all_products_df() -> pd.DataFrame:
    """
    تمام محصولات را به صورت DataFrame برمی‌گرداند.
    برای Export به Excel/CSV استفاده می‌شود.
    """
    with get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT category, product_name, product_code,
                   description, stock_qty, warehouse_location
            FROM products
            ORDER BY category, product_name
            """,
            conn,
        )
    return df


def search_products_df(query: str, category: Optional[str] = None) -> pd.DataFrame:
    """
    نتایج جستجو را به صورت DataFrame برمی‌گرداند (برای Export).
    """
    rows = search_products(query=query, category=category, limit=5000)
    if not rows:
        return pd.DataFrame(columns=["category", "product_name", "product_code",
                                     "description", "stock_qty", "warehouse_location"])
    return pd.DataFrame(rows).drop(columns=["id"], errors="ignore")
