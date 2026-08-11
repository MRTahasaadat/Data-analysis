# ============================================================
# app.py — نقطه ورود اصلی برنامه
#
# وظایف این فایل:
#   ۱. مقداردهی اولیه دیتابیس SQLite
#   ۲. sync اولیه از code.xlsx (اگر وجود داشته باشد)
#   ۳. ساخت instance برنامه Dash
#   ۴. ثبت layout و callback ها
#   ۵. راه‌اندازی سرور
#
# برای اجرا:
#   python app.py
# ============================================================

import os
import dash
import dash_bootstrap_components as dbc
from config import (
    APP_TITLE,
    APP_PORT,
    APP_HOST,
    DEBUG_MODE,
    EXCEL_FILE,
    DB_PATH)
import database as db
from layout import build_main_layout
from callbacks import register_callbacks


# ──────────────────────────────────────────────
# مقداردهی اولیه دیتابیس
# ──────────────────────────────────────────────

def startup_init() -> None:
    """
    عملیات راه‌اندازی قبل از شروع سرور:
      ۱. ساخت جداول SQLite اگر وجود نداشته باشند
      ۲. sync خودکار از code.xlsx اگر:
            - دیتابیس خالی باشد، یا
            - فایل اکسل وجود داشته باشد

    این تابع هرگز برنامه را متوقف نمی‌کند؛
    خطاها لاگ می‌شوند و برنامه ادامه می‌یابد.
    """
    print("=" * 60)
    print(f"  {APP_TITLE} — Starting Up")
    print("=" * 60)

    # ── ساخت اسکیما ──────────────────────────────────────
    try:
        db.initialize_db()
        print(f"  [DB]  Schema initialized at: {DB_PATH}")
    except Exception as exc:
        print(f"  [DB]  Schema init failed: {exc}")
        return

    # ── sync خودکار از code.xlsx ──────────────────────────
    stats = db.get_db_stats()
    excel_exists = os.path.isfile(EXCEL_FILE)

    if stats["total_skus"] == 0 and excel_exists:
        # دیتابیس خالی است — sync اولیه
        print(f"  [SYNC] DB empty. Syncing from '{EXCEL_FILE}' ...")
        result = db.sync_excel_to_db(filepath=EXCEL_FILE)
        if result.success:
            print(f"  [SYNC] Done — Added: {result.rows_added} rows.")
            if result.warnings:
                for w in result.warnings:
                    print(f"  [WARN] {w}")
        else:
            for e in result.errors:
                print(f"  [ERR]  {e}")
    elif not excel_exists:
        print(f"  [SYNC] '{EXCEL_FILE}' not found — skipping auto-sync.")
        print("         Upload a catalog via the UI to populate the database.")
    else:
        print(f"  [DB]  {stats['total_skus']} products in {stats['category_count']} categories.")

    print(f"  [APP] Running at http://localhost:{APP_PORT}")
    print("=" * 60)


# ──────────────────────────────────────────────
# ساخت برنامه Dash
# ──────────────────────────────────────────────

def create_app() -> dash.Dash:
    """
    یک instance از برنامه Dash می‌سازد و آن را برمی‌گرداند.
    این تابع جدا از startup_init است تا تست‌پذیری حفظ شود.
    """
    application = dash.Dash(
        __name__,
        external_stylesheets=[
            # تم Bootstrap برای grid و کامپوننت‌های DBC
            dbc.themes.BOOTSTRAP,
            # آیکون‌های Bootstrap
            dbc.icons.BOOTSTRAP,
        ],
        title=APP_TITLE,
        # جلوگیری از خطای callback برای IDهایی که در تب‌های پنهان هستند
        suppress_callback_exceptions=True,
        # Meta tag برای responsive design
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )

    # ثبت layout
    application.layout = build_main_layout()

    # ثبت تمام callback ها
    register_callbacks(application)

    return application


# ──────────────────────────────────────────────
# نقطه ورود
# ──────────────────────────────────────────────

# ساخت برنامه در سطح module (برای سازگاری با gunicorn/waitress)
startup_init()
app = create_app()
server = app.server  # برای deploy با WSGI servers مانند gunicorn

if __name__ == "__main__":
    app.run(
        debug=DEBUG_MODE,
        host=APP_HOST,
        port=APP_PORT,
    )
