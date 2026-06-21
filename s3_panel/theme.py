"""集中主题：Element 蓝色板、字体与 ttk 表格样式。

历史页面里散落的紫色硬编码（#601986 等）已统一替换为蓝系等价值；
新代码与外壳请优先从这里取 PALETTE，避免再写裸十六进制。
"""

FONT_FAMILY = "Microsoft YaHei UI"
MONO_FAMILY = "Consolas"

PALETTE = {
    # 主色（Element 蓝）
    "primary": "#409EFF",
    "primary_hover": "#337ECC",
    "primary_active": "#2B6CB0",
    "primary_soft": "#ECF5FF",        # 浅蓝底（原浅紫 #ede7f4）
    "primary_soft_hover": "#D9ECFF",  # 浅蓝 hover（原 #e4daef）
    # 语义色
    "success": "#67C23A",
    "success_hover": "#5BAA33",
    "warning": "#E6A23C",
    "danger": "#F56C6C",
    "danger_hover": "#DD5C5C",
    # 深色侧栏
    "sidebar_bg": "#1F2A3A",
    "sidebar_bg_hover": "#27344A",
    "sidebar_group_bg": "#19222F",
    "sidebar_active": "#409EFF",
    "sidebar_text": "#C0C7D1",
    "sidebar_text_active": "#FFFFFF",
    "sidebar_group_text": "#8A94A6",
    # 内容区
    "content_bg": "#F5F5F7",
    "card_bg": "#FFFFFF",
    "field_bg": "#F5F7FA",
    "border": "#E4E7ED",
    "topbar_bg": "#FFFFFF",
    # 文本
    "text": "#1D1D1F",
    "text_muted": "#86868B",
    "text_label": "#606266",
    # 表格
    "table_head_bg": "#F5F7FA",
    "table_sel_bg": "#ECF5FF",
    "table_row_bg": "#FFFFFF",
}

# 成绩状态配色（供排行榜/大屏/详情统一使用）
STATUS_COLORS = {
    "OK": "#2B8A3E",
    "OT": "#B8860B",
    "MP": "#409EFF",
    "DNF": "#C2410C",
    "DNS": "#86868B",
    "DSQ": "#C92A2A",
}


def apply_ttk_theme(style):
    """把 Element 风格套到 ttk.Treeview（沿用既有的 "Dark.Treeview" 样式名）。"""
    try:
        style.theme_use("clam")
    except Exception:  # noqa: BLE001
        pass
    style.configure(
        "Dark.Treeview",
        background=PALETTE["table_row_bg"],
        fieldbackground=PALETTE["table_row_bg"],
        foreground=PALETTE["text"],
        bordercolor=PALETTE["border"],
        borderwidth=0,
        rowheight=34,
        font=(FONT_FAMILY, 11),
    )
    style.map(
        "Dark.Treeview",
        background=[("selected", PALETTE["table_sel_bg"])],
        foreground=[("selected", PALETTE["text"])],
    )
    style.configure(
        "Dark.Treeview.Heading",
        background=PALETTE["table_head_bg"],
        foreground=PALETTE["text_label"],
        relief="flat",
        font=(FONT_FAMILY, 11, "bold"),
        padding=(8, 8),
    )
    style.map("Dark.Treeview.Heading", background=[("active", PALETTE["primary_soft"])])
