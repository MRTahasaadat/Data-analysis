# ============================================================
# callbacks.py — تمام منطق واکنشی Dash
#
# این فایل تمام @app.callback ها را تعریف می‌کند.
# توابع به گروه‌های منطقی سازماندهی شده‌اند:
#
#   ۱. Role & System Callbacks
#   ۲. KPI Cards
#   ۳. Global Search
#   ۴. Product Explorer (Browse)
#   ۵. Product Comparison
#   ۶. Data Management (Upload / Sync / Reset)
#   ۷. Export (Excel / CSV)
#
# قانون: هیچ HTML یا UI مستقیم در این فایل ساخته نمی‌شود،
# مگر اعلان‌های ساده. ساخت UI به layout.py واگذار می‌شود.
# ============================================================

import io
import base64

import pandas as pd
from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate

import database as db
from config import (
    USER_ROLES,
    DEFAULT_ROLE,
    MAX_COMPARE_PRODUCTS,
    COLORS,
)
from layout import (
    _alert,
    _empty_state,
    build_product_detail_card,
    build_comparison_card,
    _font,
)


def register_callbacks(app) -> None:
    """
    تمام callback ها را روی instance برنامه Dash ثبت می‌کند.
    این تابع یک بار در app.py صدا زده می‌شود.

    Args:
        app: instance اصلی برنامه Dash
    """

    # ══════════════════════════════════════════
    # ۱. نقش کاربری
    # ══════════════════════════════════════════

    @app.callback(
        Output("store-role",         "data"),
        Output("role-description",   "children"),
        Input("role-selector",       "value"),
    )
    def update_role(role: str):
        """
        وقتی نقش کاربری تغییر می‌کند:
        - مقدار را در Store ذخیره می‌کند
        - توضیح نقش را نمایش می‌دهد
        """
        role = role or DEFAULT_ROLE
        desc = USER_ROLES.get(role, {}).get("description", "")
        return role, f"— {desc}"


    @app.callback(
        Output("data-management-panel", "style"),
        Output("admin-reset-section",   "style"),
        Input("store-role",             "data"),
    )
    def update_panel_visibility(role: str):
        """
        نمایش/پنهان کردن پانل‌های حساس بر اساس نقش.
        - Guest: پانل مدیریت داده پنهان است
        - Editor: پانل آپلود نمایش داده می‌شود، Reset پنهان است
        - Admin: همه چیز نمایش داده می‌شود
        """
        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})

        # استایل پانل اصلی Data Management
        panel_style = {
            "background":   COLORS["white"],
            "borderRadius": "16px",
            "padding":      "24px",
            "boxShadow":    f"0 4px 20px {COLORS['shadow_md']}",
            "marginBottom": "24px",
        }
        if not perms.get("can_upload"):
            panel_style["display"] = "none"

        # استایل بخش Reset (فقط Admin)
        reset_style = {} if perms.get("can_reset_db") else {"display": "none"}

        return panel_style, reset_style


    # ══════════════════════════════════════════
    # ۲. KPI کارت‌ها
    # ══════════════════════════════════════════

    @app.callback(
        Output("kpi-total-skus",   "children"),
        Output("kpi-total-stock",  "children"),
        Output("kpi-categories",   "children"),
        Output("kpi-missing",      "children"),
        Output("last-sync-info",   "children"),
        Input("store-db-version",  "data"),
    )
    def refresh_kpi(db_version):
        """
        آمار KPI را از دیتابیس می‌خواند و به‌روز می‌کند.
        هر بار که store-db-version تغییر کند (بعد از sync/upload/reset)
        این callback فعال می‌شود.
        """
        stats = db.get_db_stats()
        missing = (stats.get("missing_code") or 0) + (stats.get("missing_desc") or 0)

        return (
            f"{stats.get('total_skus', 0):,}",
            f"{stats.get('total_stock', 0):,}",
            str(stats.get("category_count", 0)),
            str(missing),
            stats.get("last_sync", "Never"),
        )


    # ══════════════════════════════════════════
    # ۳. Global Search
    # ══════════════════════════════════════════

    @app.callback(
        Output("search-category-filter", "options"),
        Input("store-db-version",        "data"),
    )
    def refresh_search_category_options(db_version):
        """لیست دسته‌بندی‌ها را برای فیلتر جستجو به‌روز می‌کند."""
        cats = db.get_categories()
        return [{"label": c, "value": c} for c in cats]


    @app.callback(
        Output("search-results-table",  "data"),
        Output("search-result-count",   "children"),
        Input("search-input",           "value"),
        Input("search-category-filter", "value"),
        Input("store-db-version",       "data"),
    )
    def run_search(query: str, category: str, db_version):
        """
        جستجوی global را اجرا می‌کند و نتایج را در جدول نمایش می‌دهد.
        اگر query خالی باشد، جدول خالی نمایش داده می‌شود.
        """
        if not query or len(query.strip()) < 1:
            return [], "Enter a search term above to find products."

        results = db.search_products(query=query, category=category or None)
        count = len(results)
        count_text = (
            f"{count} result{'s' if count != 1 else ''} found"
            + (f" in '{category}'" if category else " across all categories")
        )
        return results, count_text


    # ══════════════════════════════════════════
    # ۴. Product Explorer
    # ══════════════════════════════════════════

    @app.callback(
        Output("explorer-category-dd", "options"),
        Input("store-db-version",      "data"),
    )
    def refresh_explorer_categories(db_version):
        """لیست دسته‌بندی‌ها را برای Explorer به‌روز می‌کند."""
        cats = db.get_categories()
        return [{"label": c, "value": c} for c in cats]


    @app.callback(
        Output("explorer-product-dd",  "options"),
        Output("explorer-product-dd",  "value"),
        Input("explorer-category-dd",  "value"),
        Input("store-db-version",      "data"),
    )
    def refresh_explorer_products(category: str, db_version):
        """
        وقتی دسته‌بندی تغییر می‌کند، لیست محصولات را به‌روز می‌کند.
        مقدار انتخاب‌شده قبلی ریست می‌شود.
        """
        if not category:
            return [], None

        products = db.get_products_by_category(category)
        options = [
            {
                "label": f"{p['product_name']}"
                         + (f" [{p['product_code']}]" if p.get("product_code") else ""),
                "value": p["id"],
            }
            for p in products
        ]
        return options, None


    @app.callback(
        Output("explorer-product-card", "children"),
        Input("explorer-product-dd",    "value"),
    )
    def show_product_detail(product_id):
        """
        وقتی محصول انتخاب می‌شود، کارت جزئیات را نمایش می‌دهد.
        """
        if product_id is None:
            return _empty_state("📦", "Select a category and product to view details.")

        info = db.get_product_by_id(int(product_id))
        return build_product_detail_card(info)


    # ══════════════════════════════════════════
    # ۵. Product Comparison
    # ══════════════════════════════════════════

    # callback برای پر کردن dropdown دسته‌بندی هر اسلات مقایسه
    for slot_i in range(1, MAX_COMPARE_PRODUCTS + 1):
        _slot = slot_i  # capture variable در closure

        @app.callback(
            Output(f"compare-cat-{_slot}", "options"),
            Input("store-db-version",       "data"),
        )
        def _refresh_compare_cats(db_version, _s=_slot):
            cats = db.get_categories()
            return [{"label": c, "value": c} for c in cats]

        @app.callback(
            Output(f"compare-prod-{_slot}",  "options"),
            Output(f"compare-prod-{_slot}",  "value"),
            Input(f"compare-cat-{_slot}",    "value"),
            Input("store-db-version",         "data"),
        )
        def _refresh_compare_prods(category: str, db_version, _s=_slot):
            if not category:
                return [], None
            products = db.get_products_by_category(category)
            options = [
                {
                    "label": f"{p['product_name']}"
                             + (f" [{p['product_code']}]" if p.get("product_code") else ""),
                    "value": p["id"],
                }
                for p in products
            ]
            return options, None


    @app.callback(
        Output("comparison-grid", "children"),
        [Input(f"compare-prod-{i}", "value") for i in range(1, MAX_COMPARE_PRODUCTS + 1)],
    )
    def update_comparison_grid(*product_ids):
        """
        کارت‌های مقایسه را بر اساس محصولات انتخاب‌شده می‌سازد.
        اسلات‌های خالی به صورت placeholder نمایش داده می‌شوند.
        """
        cards = []
        for slot_idx, pid in enumerate(product_ids, start=1):
            if pid is not None:
                info = db.get_product_by_id(int(pid))
            else:
                info = None
            cards.append(build_comparison_card(info, slot_idx))
        return cards


    # ══════════════════════════════════════════
    # ۶. Data Management
    # ══════════════════════════════════════════

    @app.callback(
        Output("upload-status",    "children"),
        Output("store-db-version", "data",     allow_duplicate=True),
        Input("upload-excel",      "contents"),
        State("upload-excel",      "filename"),
        State("store-db-version",  "data"),
        State("store-role",        "data"),
        prevent_initial_call=True,
    )
    def handle_upload(content: str, filename: str, db_version: int, role: str):
        """
        فایل اکسل آپلودشده را پردازش و به دیتابیس sync می‌کند.
        فقط Editor و Admin مجاز به آپلود هستند.
        """
        if not content:
            raise PreventUpdate

        # بررسی مجوز
        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})
        if not perms.get("can_upload"):
            return _alert("You don't have permission to upload files.", "error"), no_update

        # بررسی پسوند فایل
        if filename and not filename.lower().endswith(".xlsx"):
            return _alert("Only .xlsx files are supported.", "error"), no_update

        # sync به دیتابیس
        result = db.sync_excel_to_db(file_content_b64=content, filename=filename)

        if not result.success:
            msgs = "\n".join(result.errors)
            return _alert(f"Upload failed:\n{msgs}", "error"), no_update

        # پیام موفقیت
        msg_parts = [
            f"✅ '{filename}' synced successfully.",
            f"Added: {result.rows_added}  |  Updated: {result.rows_updated}",
        ]
        if result.skipped_sheets:
            msg_parts.append(f"Skipped sheets: {', '.join(result.skipped_sheets)}")
        if result.warnings:
            msg_parts.append("Warnings: " + " | ".join(result.warnings[:3]))

        return (
            _alert("\n".join(msg_parts), "success"),
            (db_version or 0) + 1,
        )


    @app.callback(
        Output("system-notifications", "children",  allow_duplicate=True),
        Output("store-db-version",     "data",      allow_duplicate=True),
        Input("btn-resync",            "n_clicks"),
        State("store-db-version",      "data"),
        State("store-role",            "data"),
        prevent_initial_call=True,
    )
    def resync_from_disk(n_clicks: int, db_version: int, role: str):
        """
        code.xlsx روی دیسک را دوباره به دیتابیس sync می‌کند.
        """
        if not n_clicks:
            raise PreventUpdate

        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})
        if not perms.get("can_upload"):
            return _alert("Permission denied.", "error"), no_update

        from config import EXCEL_FILE
        result = db.sync_excel_to_db(filepath=EXCEL_FILE)

        if not result.success:
            return _alert("Re-sync failed:\n" + "\n".join(result.errors), "error"), no_update

        msg = (
            f"Re-sync complete — Added: {result.rows_added}  |  "
            f"Updated: {result.rows_updated}"
        )
        if result.skipped_sheets:
            msg += f"\nSkipped: {', '.join(result.skipped_sheets)}"

        return _alert(msg, "success"), (db_version or 0) + 1


    @app.callback(
        Output("reset-db-status",  "children"),
        Output("store-db-version", "data",    allow_duplicate=True),
        Input("btn-reset-db",      "n_clicks"),
        State("store-db-version",  "data"),
        State("store-role",        "data"),
        prevent_initial_call=True,
    )
    def reset_database(n_clicks: int, db_version: int, role: str):
        """
        تمام داده‌های دیتابیس را پاک می‌کند (فقط Admin).
        """
        if not n_clicks:
            raise PreventUpdate

        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})
        if not perms.get("can_reset_db"):
            return _alert("Only Admins can reset the database.", "error"), no_update

        try:
            db.reset_db()
        except Exception as exc:
            return _alert(f"Reset failed: {exc}", "error"), no_update

        return _alert("Database wiped. Upload a new catalog to continue.", "warning"), (db_version or 0) + 1


    # ══════════════════════════════════════════
    # ۷. Export
    # ══════════════════════════════════════════

    @app.callback(
        Output("download-excel",         "data"),
        Input("btn-export-excel",        "n_clicks"),
        State("search-input",            "value"),
        State("search-category-filter",  "value"),
        State("store-role",              "data"),
        prevent_initial_call=True,
    )
    def export_excel(n_clicks: int, query: str, category: str, role: str):
        """
        نتایج جستجوی جاری (یا همه محصولات اگر query خالی باشد)
        را به Excel export می‌کند.
        """
        if not n_clicks:
            raise PreventUpdate

        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})
        if not perms.get("can_export"):
            raise PreventUpdate

        if query and query.strip():
            df = db.search_products_df(query=query, category=category or None)
            filename = f"search_results_{_safe_name(query)}.xlsx"
        else:
            df = db.get_all_products_df()
            filename = "product_catalog_full.xlsx"

        # نوشتن به buffer در حافظه
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Products")
            # تنظیم عرض ستون‌ها به صورت خودکار
            ws = writer.sheets["Products"]
            for col_cells in ws.columns:
                max_len = max((len(str(c.value or "")) for c in col_cells), default=10)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 50)
        buf.seek(0)

        return {
            "content":  base64.b64encode(buf.getvalue()).decode(),
            "filename": filename,
            "type":     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "base64":   True,
        }


    @app.callback(
        Output("download-csv",           "data"),
        Input("btn-export-csv",          "n_clicks"),
        State("search-input",            "value"),
        State("search-category-filter",  "value"),
        State("store-role",              "data"),
        prevent_initial_call=True,
    )
    def export_csv(n_clicks: int, query: str, category: str, role: str):
        """
        نتایج جستجو یا همه محصولات را به CSV export می‌کند.
        """
        if not n_clicks:
            raise PreventUpdate

        perms = USER_ROLES.get(role or DEFAULT_ROLE, {})
        if not perms.get("can_export"):
            raise PreventUpdate

        if query and query.strip():
            df = db.search_products_df(query=query, category=category or None)
            filename = f"search_results_{_safe_name(query)}.csv"
        else:
            df = db.get_all_products_df()
            filename = "product_catalog_full.csv"

        return {
            "content":  df.to_csv(index=False, encoding="utf-8-sig"),
            "filename": filename,
            "type":     "text/csv",
            "base64":   False,
        }


# ──────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────

def _safe_name(text: str) -> str:
    """
    یک رشته را برای استفاده در نام فایل ایمن می‌کند.
    کاراکترهای غیرمجاز حذف یا جایگزین می‌شوند.
    """
    import re
    return re.sub(r"[^\w\-]", "_", text.strip())[:40]
