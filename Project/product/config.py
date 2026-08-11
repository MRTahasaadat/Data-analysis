# ============================================================
# config.py — تنظیمات مرکزی برنامه
#
# تمام مقادیر ثابت، مسیرها، رنگ‌ها، نقش‌ها، و نگاشت‌های
# ستون‌های اکسل در این فایل تعریف می‌شوند.
# برای گسترش برنامه در آینده، فقط این فایل را ویرایش کنید.
# ============================================================

import os

# ──────────────────────────────────────────────
# مسیرهای فایل
# ──────────────────────────────────────────────

# پوشه ریشه پروژه (کنار این فایل)
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

# مسیر فایل اکسل پیش‌فرض (منبع import اولیه)
EXCEL_FILE: str = os.path.join(BASE_DIR, "code.xlsx")

# مسیر پایگاه داده SQLite
DB_PATH: str = os.path.join(BASE_DIR, "catalog.db")

# پوشه موقت برای ذخیره فایل‌های آپلودشده
UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# تنظیمات برنامه Dash
# ──────────────────────────────────────────────

APP_TITLE: str = "Product Catalog Pro"
APP_PORT: int = 8050
APP_HOST: str = "127.0.0.1"
DEBUG_MODE: bool = True  # در محیط تولید False کنید

# ──────────────────────────────────────────────
# نگاشت ستون‌های اکسل (اولویت‌بندی شده)
# هر لیست به ترتیب اولویت بررسی می‌شود
# ──────────────────────────────────────────────

# ستون اجباری — شیت بدون این ستون رد می‌شود
COL_PRODUCT_NAME: list[str] = ["product_name", "name", "product", "item_name"]

# ستون کد/SKU محصول
COL_PRODUCT_CODE: list[str] = ["product_code", "code", "sku", "item_code", "part_number"]

# ستون توضیحات
COL_DESCRIPTION: list[str] = ["description", "desc", "details", "product_description", "info"]

# ستون موجودی انبار
COL_STOCK_QTY: list[str] = ["stock_qty", "qty", "quantity", "stock", "inventory", "موجودی"]

# ستون آدرس/مکان انبار
COL_WAREHOUSE: list[str] = [
    "warehouse_location", "location", "warehouse", "shelf",
    "storage", "انبار", "آدرس_انبار", "مکان"
]

# ──────────────────────────────────────────────
# پالت رنگی SaaS — آبی تیره / آبی روشن / کرم
# ──────────────────────────────────────────────

COLORS: dict[str, str] = {
    # رنگ‌های اصلی برند
    "dark_blue":        "#0D2B55",   # هدر، sidebar، اکسنت اصلی
    "mid_blue":         "#1A4A8A",   # گرادیان، دکمه‌های primary
    "light_blue":       "#4A90D9",   # لینک‌ها، بج‌ها
    "accent_blue":      "#5DADE2",   # هایلایت، hover
    "navy_soft":        "#162D4E",   # sidebar background

    # پس‌زمینه‌ها
    "cream":            "#F8F5EE",   # پس‌زمینه اصلی صفحه
    "cream_dark":       "#EDE8DC",   # کارت‌های داخلی، stripe جدول
    "white":            "#FFFFFF",   # کارت‌های اصلی

    # متن
    "text_primary":     "#1C2B3A",
    "text_secondary":   "#4A6078",
    "text_muted":       "#7A96B0",
    "text_light":       "#B8CCD8",
    "text_white":       "#FFFFFF",

    # خطوط و سایه
    "border":           "#D4CEBE",
    "border_light":     "#E8E4DA",
    "shadow_sm":        "rgba(13, 43, 85, 0.08)",
    "shadow_md":        "rgba(13, 43, 85, 0.14)",
    "shadow_lg":        "rgba(13, 43, 85, 0.22)",

    # وضعیت‌ها
    "success":          "#1B7A4A",
    "success_bg":       "#EAF7F0",
    "success_border":   "#9ED4B8",
    "warning":          "#7A5A00",
    "warning_bg":       "#FFFBF0",
    "warning_border":   "#E8D8A0",
    "error":            "#8B2020",
    "error_bg":         "#FFF4F4",
    "error_border":     "#E8BBBB",
    "info":             "#1A4A8A",
    "info_bg":          "#EEF4FB",
    "info_border":      "#A8C4E0",

    # KPI کارت‌ها
    "kpi_1":            "#0D2B55",   # آبی تیره — Total SKUs
    "kpi_2":            "#1A4A8A",   # آبی میانی — Total Stock
    "kpi_3":            "#4A90D9",   # آبی روشن — Categories
    "kpi_4":            "#C0392B",   # قرمز — Missing Data
}

# ──────────────────────────────────────────────
# نقش‌های کاربری
# ──────────────────────────────────────────────

# تعریف سطوح دسترسی به صورت دیکشنری
# کلید: نام نقش | مقدار: دیکشنری مجوزها
USER_ROLES: dict[str, dict] = {
    "guest": {
        "label":        "👤 Guest",
        "can_browse":   True,
        "can_compare":  True,
        "can_upload":   False,
        "can_export":   True,
        "can_reset_db": False,
        "description":  "Read-only access — browse and compare products.",
    },
    "editor": {
        "label":        "✏️ Editor",
        "can_browse":   True,
        "can_compare":  True,
        "can_upload":   True,   # می‌تواند فایل اکسل آپلود کند
        "can_export":   True,
        "can_reset_db": False,
        "description":  "Can upload new catalogs and refresh data.",
    },
    "admin": {
        "label":        "🔑 Admin",
        "can_browse":   True,
        "can_compare":  True,
        "can_upload":   True,
        "can_export":   True,
        "can_reset_db": True,   # می‌تواند دیتابیس را پاک کند
        "description":  "Full access including database management.",
    },
}

DEFAULT_ROLE: str = "guest"

# ──────────────────────────────────────────────
# ثابت‌های جدول محصولات
# ──────────────────────────────────────────────

# تعداد ردیف نمایش‌داده‌شده در هر صفحه جدول جستجو
TABLE_PAGE_SIZE: int = 15

# حداکثر تعداد محصول برای مقایسه
MAX_COMPARE_PRODUCTS: int = 3

# حداکثر اندازه فایل آپلود (بایت) — ۱۰ مگابایت
MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024

# ──────────────────────────────────────────────
# ستون‌های نمایشی جدول جستجو
# هر tuple: (نام ستون DB، عنوان نمایشی، عرض)
# ──────────────────────────────────────────────

SEARCH_TABLE_COLUMNS: list[dict] = [
    {"id": "category",           "name": "Category",          "width": "120px"},
    {"id": "product_name",       "name": "Product Name",      "width": "200px"},
    {"id": "product_code",       "name": "Code / SKU",        "width": "110px"},
    {"id": "description",        "name": "Description",       "width": "260px"},
    {"id": "stock_qty",          "name": "Stock Qty",         "width": "90px"},
    {"id": "warehouse_location", "name": "Warehouse",         "width": "120px"},
]
