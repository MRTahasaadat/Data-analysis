# ============================================================
# layout.py — ساخت رابط کاربری داشبورد
#
# این فایل تمام بخش‌های UI را به صورت توابع مستقل می‌سازد:
#   - هدر و انتخاب نقش کاربری
#   - KPI کارت‌ها (آمار کلی)
#   - جستجوی global با جدول نتایج
#   - مرور محصولات بر اساس دسته‌بندی
#   - ابزار مقایسه محصولات
#   - پانل آپلود و مدیریت دیتابیس (Editor/Admin)
#   - Export دکمه‌ها
#
# قانون: این فایل هیچ منطق تجاری یا DB query ندارد.
# تمام داده‌ها از callbacks تزریق می‌شوند.
# ============================================================

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from config import (
    COLORS,
    USER_ROLES,
    DEFAULT_ROLE,
    SEARCH_TABLE_COLUMNS,
    MAX_COMPARE_PRODUCTS,
    APP_TITLE,
)


# ──────────────────────────────────────────────
# Helpers — اجزای UI کوچک و قابل استفاده مجدد
# ──────────────────────────────────────────────

def _font(size: str = "0.9rem", weight: str = "400", color: str = COLORS["text_primary"]) -> dict:
    """یک دیکشنری استایل فونت می‌سازد."""
    return {
        "fontFamily": "'Segoe UI', system-ui, -apple-system, sans-serif",
        "fontSize":   size,
        "fontWeight": weight,
        "color":      color,
    }


def _card(children, style: dict = None, className: str = "") -> html.Div:
    """کارت سفید با سایه و گوشه گرد می‌سازد."""
    base = {
        "background":    COLORS["white"],
        "borderRadius":  "16px",
        "padding":       "24px",
        "boxShadow":     f"0 4px 20px {COLORS['shadow_md']}",
        "marginBottom":  "24px",
    }
    if style:
        base.update(style)
    return html.Div(children, style=base, className=className)


def _section_title(text: str, icon: str = "") -> html.Div:
    """عنوان بخش با خط جداکننده زیر آن."""
    return html.Div(
        style={"marginBottom": "18px"},
        children=[
            html.H5(
                f"{icon} {text}".strip(),
                style={
                    **_font("1rem", "700", COLORS["dark_blue"]),
                    "margin": "0 0 10px 0",
                    "letterSpacing": "-0.2px",
                },
            ),
            html.Hr(style={
                "border":     "none",
                "borderTop":  f"2px solid {COLORS['border_light']}",
                "margin":     "0",
            }),
        ]
    )


def _badge(text: str, color: str = COLORS["light_blue"]) -> html.Span:
    """یک بج رنگی کوچک."""
    return html.Span(
        text,
        style={
            "background":    color,
            "color":         COLORS["white"],
            "borderRadius":  "20px",
            "padding":       "2px 10px",
            "fontSize":      "0.72rem",
            "fontWeight":    "600",
            "letterSpacing": "0.04em",
            "marginLeft":    "8px",
            "verticalAlign": "middle",
        }
    )


def _alert(message: str, kind: str = "info") -> html.Div:
    """
    بنر اعلان (info / success / warning / error).
    kind: یکی از 'info', 'success', 'warning', 'error'
    """
    cfg = {
        "info":    ("ℹ️",  COLORS["info_bg"],    COLORS["info_border"],    COLORS["info"]),
        "success": ("✅",  COLORS["success_bg"], COLORS["success_border"], COLORS["success"]),
        "warning": ("⚠️",  COLORS["warning_bg"], COLORS["warning_border"], COLORS["warning"]),
        "error":   ("🚫", COLORS["error_bg"],   COLORS["error_border"],   COLORS["error"]),
    }.get(kind, ("ℹ️", COLORS["info_bg"], COLORS["info_border"], COLORS["info"]))

    icon, bg, border, text_col = cfg
    lines = str(message).strip().split("\n")

    return html.Div(
        style={
            "background":    bg,
            "border":        f"1.5px solid {border}",
            "borderRadius":  "10px",
            "padding":       "12px 16px",
            "display":       "flex",
            "gap":           "10px",
            "alignItems":    "flex-start",
        },
        children=[
            html.Span(icon, style={"fontSize": "1.1rem", "flexShrink": "0"}),
            html.Div(
                [html.Span(l) for l in lines],
                style={**_font("0.87rem", "400", text_col), "lineHeight": "1.6"},
            ),
        ]
    )


def _dropdown(id: str, options: list = None, placeholder: str = "Select…",
               value=None, multi: bool = False, disabled: bool = False) -> dcc.Dropdown:
    """Dropdown با استایل یکسان در کل برنامه."""
    return dcc.Dropdown(
        id=id,
        options=options or [],
        value=value,
        placeholder=placeholder,
        multi=multi,
        disabled=disabled,
        clearable=True,
        style={
            "borderRadius":  "10px",
            "border":        f"1.5px solid {COLORS['border']}",
            "background":    COLORS["white"],
            "fontSize":      "0.9rem",
            "color":         COLORS["text_primary"],
        },
    )


def _label(text: str) -> html.Div:
    """برچسب فرم."""
    return html.Div(
        text,
        style={
            **_font("0.73rem", "700", COLORS["text_muted"]),
            "textTransform": "uppercase",
            "letterSpacing": "0.08em",
            "marginBottom":  "6px",
        }
    )


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────

def build_header() -> html.Div:
    """
    هدر اصلی داشبورد با گرادیان آبی.
    شامل عنوان برنامه و انتخابگر نقش کاربری.
    """
    role_options = [
        {"label": v["label"], "value": k}
        for k, v in USER_ROLES.items()
    ]

    return html.Div(
        style={
            "background":    f"linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['mid_blue']} 55%, {COLORS['light_blue']} 100%)",
            "padding":       "22px 36px",
            "display":       "flex",
            "alignItems":    "center",
            "justifyContent": "space-between",
            "flexWrap":      "wrap",
            "gap":           "16px",
            "boxShadow":     f"0 4px 24px {COLORS['shadow_lg']}",
        },
        children=[
            # عنوان برنامه
            html.Div(
                children=[
                    html.H1(
                        APP_TITLE,
                        style={
                            **_font("1.55rem", "700", COLORS["white"]),
                            "margin":        "0 0 3px 0",
                            "letterSpacing": "-0.5px",
                        }
                    ),
                    html.P(
                        "Inventory • Search • Compare • Export",
                        style={**_font("0.8rem", "400", COLORS["accent_blue"]), "margin": "0"},
                    ),
                ]
            ),

            # انتخاب نقش کاربری
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "12px"},
                children=[
                    html.Span(
                        "Access Level:",
                        style=_font("0.82rem", "600", COLORS["text_light"]),
                    ),
                    dcc.Dropdown(
                        id="role-selector",
                        options=role_options,
                        value=DEFAULT_ROLE,
                        clearable=False,
                        style={
                            "width":      "160px",
                            "fontSize":   "0.85rem",
                            "fontWeight": "600",
                            "borderRadius": "8px",
                        },
                    ),
                    # نمایش توضیح نقش
                    html.Div(
                        id="role-description",
                        style=_font("0.78rem", "400", COLORS["text_light"]),
                    ),
                ]
            ),
        ]
    )


# ──────────────────────────────────────────────
# KPI Cards
# ──────────────────────────────────────────────

def build_kpi_cards() -> html.Div:
    """
    چهار KPI کارت برای نمایش آمار کلی دیتابیس.
    مقادیر توسط callback پر می‌شوند.
    """
    card_defs = [
        ("kpi-total-skus",   "Total SKUs",      "🏷️",  COLORS["kpi_1"]),
        ("kpi-total-stock",  "Total Stock Qty", "📦",  COLORS["kpi_2"]),
        ("kpi-categories",   "Categories",      "📂",  COLORS["kpi_3"]),
        ("kpi-missing",      "Missing Data",    "⚠️",  COLORS["kpi_4"]),
    ]

    cards = []
    for card_id, label, icon, accent in card_defs:
        cards.append(
            html.Div(
                style={
                    "background":   COLORS["white"],
                    "borderRadius": "14px",
                    "padding":      "20px 22px",
                    "boxShadow":    f"0 4px 18px {COLORS['shadow_md']}",
                    "flex":         "1",
                    "minWidth":     "160px",
                    "borderLeft":   f"5px solid {accent}",
                    "display":      "flex",
                    "alignItems":   "center",
                    "gap":          "16px",
                },
                children=[
                    html.Div(
                        icon,
                        style={"fontSize": "2rem", "lineHeight": "1"},
                    ),
                    html.Div([
                        html.Div(
                            id=card_id,
                            children="—",
                            style={**_font("1.7rem", "700", accent), "lineHeight": "1.1"},
                        ),
                        html.Div(
                            label,
                            style=_font("0.75rem", "600", COLORS["text_muted"]),
                        ),
                    ]),
                ]
            )
        )

    return html.Div(
        style={
            "display":  "flex",
            "gap":      "18px",
            "flexWrap": "wrap",
            "marginBottom": "24px",
        },
        children=cards,
    )


# ──────────────────────────────────────────────
# Global Search Panel
# ──────────────────────────────────────────────

def build_search_panel() -> html.Div:
    """
    پانل جستجوی global با فیلتر دسته‌بندی و جدول نتایج.
    شامل دکمه‌های Export به Excel و CSV.
    """
    return _card([
        _section_title("Global Search", "🔍"),

        # ── ردیف ورودی‌های جستجو ──────────────────────────
        html.Div(
            style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "16px"},
            children=[
                html.Div(
                    style={"flex": "3", "minWidth": "220px"},
                    children=[
                        _label("Search by name, code, or description"),
                        dcc.Input(
                            id="search-input",
                            type="text",
                            placeholder="Type to search…",
                            debounce=True,
                            style={
                                "width":        "100%",
                                "padding":      "10px 14px",
                                "borderRadius": "10px",
                                "border":       f"1.5px solid {COLORS['border']}",
                                "fontSize":     "0.92rem",
                                "outline":      "none",
                                "boxSizing":    "border-box",
                            },
                        ),
                    ]
                ),
                html.Div(
                    style={"flex": "2", "minWidth": "180px"},
                    children=[
                        _label("Filter by category"),
                        _dropdown(
                            id="search-category-filter",
                            placeholder="All categories…",
                        ),
                    ]
                ),
            ]
        ),

        # ── نتایج جستجو ───────────────────────────────────
        html.Div(
            id="search-result-count",
            style={
                **_font("0.8rem", "600", COLORS["text_muted"]),
                "marginBottom": "10px",
            },
        ),

        dash_table.DataTable(
            id="search-results-table",
            columns=[
                {"name": col["name"], "id": col["id"]}
                for col in SEARCH_TABLE_COLUMNS
            ],
            data=[],
            page_size=15,
            page_action="native",
            sort_action="native",
            filter_action="none",
            row_selectable="multi",
            selected_rows=[],
            style_table={"overflowX": "auto"},
            style_header={
                "background":    COLORS["dark_blue"],
                "color":         COLORS["white"],
                "fontWeight":    "700",
                "fontSize":      "0.78rem",
                "letterSpacing": "0.04em",
                "border":        "none",
                "padding":       "10px 14px",
                "textTransform": "uppercase",
            },
            style_cell={
                "fontSize":      "0.86rem",
                "color":         COLORS["text_primary"],
                "padding":       "9px 14px",
                "border":        f"1px solid {COLORS['border_light']}",
                "fontFamily":    "'Segoe UI', system-ui, sans-serif",
                "overflow":      "hidden",
                "textOverflow":  "ellipsis",
                "maxWidth":      "260px",
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": COLORS["cream"],
                },
                {
                    "if": {"state": "selected"},
                    "backgroundColor": COLORS["info_bg"],
                    "border":          f"1px solid {COLORS['light_blue']}",
                },
            ],
            tooltip_delay=0,
            tooltip_duration=None,
        ),

        # ── دکمه‌های Export ───────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "10px", "marginTop": "16px", "flexWrap": "wrap"},
            children=[
                dcc.Download(id="download-excel"),
                dcc.Download(id="download-csv"),
                html.Button(
                    "⬇️ Export to Excel",
                    id="btn-export-excel",
                    n_clicks=0,
                    style=_btn_style(COLORS["mid_blue"]),
                ),
                html.Button(
                    "⬇️ Export to CSV",
                    id="btn-export-csv",
                    n_clicks=0,
                    style=_btn_style(COLORS["text_secondary"]),
                ),
            ]
        ),
    ])


# ──────────────────────────────────────────────
# Product Explorer (Browse by Category)
# ──────────────────────────────────────────────

def build_product_explorer() -> html.Div:
    """
    بخش مرور محصولات با dropdown دسته‌بندی و محصول.
    اطلاعات محصول انتخاب‌شده در کارت نمایش داده می‌شود.
    """
    return _card([
        _section_title("Product Explorer", "📋"),

        # dropdown ها
        html.Div(
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "200px"},
                    children=[
                        _label("Category"),
                        _dropdown(id="explorer-category-dd", placeholder="Select category…"),
                    ]
                ),
                html.Div(
                    style={"flex": "2", "minWidth": "240px"},
                    children=[
                        _label("Product"),
                        _dropdown(id="explorer-product-dd", placeholder="Select product…"),
                    ]
                ),
            ]
        ),

        # کارت نمایش محصول
        html.Div(id="explorer-product-card"),
    ])


def build_product_detail_card(info: dict) -> html.Div:
    """
    کارت جزئیات محصول را می‌سازد.
    این تابع از callback صدا زده می‌شود.

    Args:
        info: دیکشنری اطلاعات محصول از DB
    """
    if not info:
        return _empty_state("📦", "Select a category and product to view details.")

    extra: dict = info.get("extra_attributes", {}) or {}

    def row(label: str, value, accent: bool = False) -> html.Div:
        bg = COLORS["cream_dark"] if accent else COLORS["cream"]
        return html.Div(
            style={
                "display":      "flex",
                "marginBottom": "10px",
                "borderRadius": "10px",
                "overflow":     "hidden",
                "border":       f"1px solid {COLORS['border']}",
            },
            children=[
                html.Div(
                    label,
                    style={
                        **_font("0.76rem", "700", COLORS["white"]),
                        "background":    COLORS["dark_blue"],
                        "padding":       "10px 16px",
                        "minWidth":      "145px",
                        "maxWidth":      "145px",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.05em",
                        "flexShrink":    "0",
                    }
                ),
                html.Div(
                    str(value) if value else "—",
                    style={
                        **_font("0.9rem", "400", COLORS["text_primary"]),
                        "background":   bg,
                        "padding":      "10px 16px",
                        "flex":         "1",
                        "wordBreak":    "break-word",
                        "lineHeight":   "1.5",
                    }
                ),
            ]
        )

    rows = [
        row("Product Code",  info.get("product_code"),       accent=True),
        row("Description",   info.get("description")),
        row("Stock Qty",     info.get("stock_qty", 0),       accent=True),
        row("Warehouse",     info.get("warehouse_location")),
    ]

    # ستون‌های extra
    for k, v in extra.items():
        if v and str(v).strip() not in ("", "nan", "None"):
            rows.append(row(k.replace("_", " ").title(), v))

    return html.Div([
        # نوار گرادیان بالا
        html.Div(style={
            "height":       "5px",
            "background":   f"linear-gradient(90deg, {COLORS['dark_blue']}, {COLORS['accent_blue']})",
            "borderRadius": "12px 12px 0 0",
        }),
        html.Div(
            style={"padding": "24px"},
            children=[
                html.H3(
                    info.get("product_name", "—"),
                    style={**_font("1.3rem", "700", COLORS["dark_blue"]), "margin": "0 0 6px 0"},
                ),
                html.Div(
                    [
                        _badge(info.get("category", ""), COLORS["mid_blue"]),
                        _badge(f"ID: {info.get('id', '?')}", COLORS["text_muted"]),
                    ],
                    style={"marginBottom": "20px"},
                ),
                html.Hr(style={"border": "none", "borderTop": f"1px solid {COLORS['border']}", "margin": "0 0 18px 0"}),
                *rows,
            ]
        ),
    ], style={
        "background":   COLORS["white"],
        "borderRadius": "12px",
        "boxShadow":    f"0 2px 12px {COLORS['shadow_sm']}",
        "overflow":     "hidden",
    })


# ──────────────────────────────────────────────
# Product Comparison
# ──────────────────────────────────────────────

def build_comparison_panel() -> html.Div:
    """
    پانل مقایسه حداکثر ۳ محصول کنار هم.
    کاربر از dropdown ها محصول انتخاب می‌کند.
    """
    selectors = []
    for i in range(1, MAX_COMPARE_PRODUCTS + 1):
        selectors.append(
            html.Div(
                style={"flex": "1", "minWidth": "180px"},
                children=[
                    _label(f"Product {i}"),
                    _dropdown(
                        id=f"compare-cat-{i}",
                        placeholder="Category…",
                    ),
                    html.Div(style={"height": "8px"}),
                    _dropdown(
                        id=f"compare-prod-{i}",
                        placeholder="Product…",
                    ),
                ]
            )
        )

    return _card([
        _section_title("Product Comparison", "⚖️"),
        html.P(
            "Select up to 3 products to compare their specs, stock, and location side-by-side.",
            style={**_font("0.85rem", "400", COLORS["text_secondary"]), "marginBottom": "18px"},
        ),

        # انتخاب‌گرها
        html.Div(
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "22px"},
            children=selectors,
        ),

        # کارت‌های مقایسه
        html.Div(
            id="comparison-grid",
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
        ),
    ])


def build_comparison_card(info: dict, slot: int) -> html.Div:
    """
    یک کارت مقایسه برای یک محصول می‌سازد.

    Args:
        info: اطلاعات محصول
        slot: شماره اسلات (۱، ۲، یا ۳)
    """
    accent_colors = [COLORS["kpi_1"], COLORS["kpi_2"], COLORS["kpi_3"]]
    accent = accent_colors[(slot - 1) % len(accent_colors)]

    if not info:
        return html.Div(
            style={
                "flex":         "1",
                "minWidth":     "200px",
                "borderRadius": "14px",
                "border":       f"2px dashed {COLORS['border']}",
                "padding":      "40px 20px",
                "textAlign":    "center",
            },
            children=[
                html.Div("➕", style={"fontSize": "2rem", "marginBottom": "8px"}),
                html.Div(f"Slot {slot} — not selected",
                         style=_font("0.82rem", "400", COLORS["text_muted"])),
            ]
        )

    extra: dict = info.get("extra_attributes", {}) or {}

    def cmp_row(label, value):
        return html.Div(
            style={
                "display":       "flex",
                "justifyContent": "space-between",
                "padding":       "7px 0",
                "borderBottom":  f"1px solid {COLORS['border_light']}",
                "gap":           "8px",
            },
            children=[
                html.Span(label, style=_font("0.75rem", "600", COLORS["text_muted"])),
                html.Span(
                    str(value) if value else "—",
                    style={**_font("0.85rem", "600", COLORS["text_primary"]), "textAlign": "right"},
                ),
            ]
        )

    rows = [
        cmp_row("Code",      info.get("product_code")),
        cmp_row("Category",  info.get("category")),
        cmp_row("Stock Qty", info.get("stock_qty", 0)),
        cmp_row("Warehouse", info.get("warehouse_location")),
    ]
    for k, v in extra.items():
        if v and str(v).strip() not in ("", "nan", "None"):
            rows.append(cmp_row(k.replace("_", " ").title(), v))

    return html.Div(
        style={
            "flex":         "1",
            "minWidth":     "210px",
            "background":   COLORS["white"],
            "borderRadius": "14px",
            "boxShadow":    f"0 3px 14px {COLORS['shadow_md']}",
            "overflow":     "hidden",
        },
        children=[
            # هدر رنگی کارت
            html.Div(
                style={
                    "background": accent,
                    "padding":    "14px 18px",
                    "color":      COLORS["white"],
                },
                children=[
                    html.Div(f"#{slot}", style=_font("0.7rem", "700", "rgba(255,255,255,0.6)")),
                    html.Div(
                        info.get("product_name", "—"),
                        style={**_font("0.95rem", "700", COLORS["white"]), "marginTop": "2px"},
                    ),
                ]
            ),
            # بدنه
            html.Div(
                style={"padding": "16px 18px"},
                children=rows,
            ),
            # توضیحات
            html.Div(
                style={
                    "background":  COLORS["cream"],
                    "padding":     "10px 18px",
                    "borderTop":   f"1px solid {COLORS['border_light']}",
                },
                children=[
                    html.Div("Description", style=_font("0.7rem", "700", COLORS["text_muted"])),
                    html.Div(
                        info.get("description") or "—",
                        style={**_font("0.82rem", "400", COLORS["text_secondary"]), "marginTop": "4px"},
                    ),
                ]
            ),
        ]
    )


# ──────────────────────────────────────────────
# Upload & Database Management Panel
# ──────────────────────────────────────────────

def build_data_management_panel() -> html.Div:
    """
    پانل آپلود فایل اکسل و مدیریت دیتابیس.
    نمایش/پنهان شدن این پانل توسط نقش کاربری کنترل می‌شود.
    """
    return _card(
        id_="data-management-panel",
        children=[
            _section_title("Data Management", "🗄️"),

            dbc.Row([
                # ── آپلود اکسل ─────────────────────────────
                dbc.Col([
                    _label("Upload New Excel Catalog"),
                    dcc.Upload(
                        id="upload-excel",
                        children=html.Div([
                            html.Div("📂", style={"fontSize": "2.5rem", "marginBottom": "8px"}),
                            html.Div("Drag & Drop or ", style=_font("0.9rem")),
                            html.A(
                                "Browse File",
                                style={
                                    **_font("0.9rem", "700", COLORS["light_blue"]),
                                    "cursor": "pointer",
                                    "textDecoration": "underline",
                                }
                            ),
                            html.Div(
                                ".xlsx files only, max 10 MB",
                                style=_font("0.75rem", "400", COLORS["text_muted"]),
                            ),
                        ], style={"textAlign": "center", "padding": "8px"}),
                        style={
                            "border":         f"2px dashed {COLORS['border']}",
                            "borderRadius":   "12px",
                            "padding":        "28px 20px",
                            "background":     COLORS["cream"],
                            "cursor":         "pointer",
                            "marginBottom":   "12px",
                        },
                        accept=".xlsx",
                        max_size=10 * 1024 * 1024,
                    ),
                    html.Div(id="upload-status"),
                ], md=6),

                # ── DB Actions ─────────────────────────────
                dbc.Col([
                    _label("Database Actions"),
                    html.Div(
                        style={"display": "flex", "flexDirection": "column", "gap": "10px"},
                        children=[
                            html.Button(
                                "🔄 Re-sync from code.xlsx",
                                id="btn-resync",
                                n_clicks=0,
                                style=_btn_style(COLORS["mid_blue"], full_width=True),
                            ),
                            # دکمه Reset فقط برای Admin
                            html.Div(
                                id="admin-reset-section",
                                children=[
                                    html.Hr(style={"border": "none", "borderTop": f"1px solid {COLORS['border']}"}),
                                    html.Div(
                                        "⚠️ Admin Zone",
                                        style={**_font("0.73rem", "700", COLORS["error"]), "marginBottom": "6px"},
                                    ),
                                    html.Button(
                                        "🗑️ Reset Database",
                                        id="btn-reset-db",
                                        n_clicks=0,
                                        style=_btn_style(COLORS["error"], full_width=True),
                                    ),
                                    html.Div(id="reset-db-status", style={"marginTop": "8px"}),
                                ]
                            ),
                        ]
                    ),

                    # لاگ آخرین sync
                    html.Div(
                        style={"marginTop": "18px"},
                        children=[
                            _label("Last Sync"),
                            html.Div(
                                id="last-sync-info",
                                style=_font("0.82rem", "400", COLORS["text_secondary"]),
                            ),
                        ]
                    ),
                ], md=6),
            ]),
        ],
    )


# ──────────────────────────────────────────────
# Helpers داخلی
# ──────────────────────────────────────────────

def _btn_style(color: str, full_width: bool = False) -> dict:
    """استایل دکمه."""
    s = {
        "background":    color,
        "color":         COLORS["white"],
        "border":        "none",
        "borderRadius":  "10px",
        "padding":       "10px 20px",
        "fontSize":      "0.87rem",
        "fontWeight":    "600",
        "cursor":        "pointer",
        "fontFamily":    "'Segoe UI', system-ui, sans-serif",
        "letterSpacing": "0.02em",
        "transition":    "opacity 0.15s",
    }
    if full_width:
        s["width"] = "100%"
    return s


def _empty_state(icon: str, message: str) -> html.Div:
    """حالت خالی — نمایش آیکون و پیام."""
    return html.Div(
        style={"textAlign": "center", "padding": "44px 20px"},
        children=[
            html.Div(icon, style={"fontSize": "2.8rem", "marginBottom": "12px"}),
            html.P(message, style=_font("0.92rem", "400", COLORS["text_muted"])),
        ]
    )


def _card(children, style: dict = None, id_: str = None, className: str = "") -> html.Div:
    """کارت سفید — overload با id_ اختیاری."""
    base = {
        "background":   COLORS["white"],
        "borderRadius": "16px",
        "padding":      "24px",
        "boxShadow":    f"0 4px 20px {COLORS['shadow_md']}",
        "marginBottom": "24px",
    }
    if style:
        base.update(style)
    kwargs = {"style": base, "className": className}
    if id_:
        kwargs["id"] = id_
    return html.Div(children, **kwargs)


# ──────────────────────────────────────────────
# Layout اصلی
# ──────────────────────────────────────────────

def build_main_layout() -> html.Div:
    """
    ساختار اصلی صفحه را برمی‌گرداند.
    همه بخش‌ها در یک صفحه با اسکرول عمودی قرار دارند.
    """
    return html.Div(
        style={
            "background":  COLORS["cream"],
            "minHeight":   "100vh",
            "fontFamily":  "'Segoe UI', system-ui, -apple-system, sans-serif",
        },
        children=[
            # هدر
            build_header(),

            # محتوای اصلی
            html.Div(
                style={
                    "maxWidth": "1280px",
                    "margin":   "0 auto",
                    "padding":  "28px 24px 60px",
                },
                children=[
                    # اعلان‌های سیستمی (خطا / موفقیت sync)
                    html.Div(id="system-notifications", style={"marginBottom": "8px"}),

                    # KPI کارت‌ها
                    build_kpi_cards(),

                    # تب‌ها
                    dbc.Tabs(
                        id="main-tabs",
                        active_tab="tab-search",
                        style={"marginBottom": "4px"},
                        children=[
                            dbc.Tab(
                                label="🔍 Search",
                                tab_id="tab-search",
                                children=[build_search_panel()],
                            ),
                            dbc.Tab(
                                label="📋 Explorer",
                                tab_id="tab-explorer",
                                children=[build_product_explorer()],
                            ),
                            dbc.Tab(
                                label="⚖️ Compare",
                                tab_id="tab-compare",
                                children=[build_comparison_panel()],
                            ),
                            dbc.Tab(
                                label="🗄️ Data",
                                tab_id="tab-data",
                                children=[build_data_management_panel()],
                            ),
                        ]
                    ),
                ]
            ),

            # فوتر
            html.Div(
                f"{APP_TITLE} — Powered by Dash · Pandas · SQLite3",
                style={
                    **_font("0.75rem", "400", COLORS["text_muted"]),
                    "textAlign":   "center",
                    "padding":     "20px",
                    "borderTop":   f"1px solid {COLORS['border']}",
                }
            ),

            # Store برای نگه داشتن وضعیت‌های میانی
            dcc.Store(id="store-role",        data=DEFAULT_ROLE),
            dcc.Store(id="store-search-query", data=""),
            dcc.Store(id="store-db-version",  data=0),  # افزایش آن باعث refresh callback ها می‌شود
        ]
    )
