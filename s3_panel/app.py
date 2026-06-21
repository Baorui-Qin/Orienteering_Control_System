"""应用主窗口：深色分组侧栏 + 顶栏 + 浏览器式标签页 + 全宽内容（灰常风格）。"""

import math
import queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from .pages_analysis import AnalysisPageMixin
from .pages_event import EventPageMixin
from .pages_network import NetworkPageMixin
from .pages_org import OrgPageMixin
from .pages_overview import OverviewPageMixin
from .pages_results import ResultsPageMixin
from .pages_setup import SetupPageMixin
from .runtime import RuntimeMixin
from .serial_io import SerialWorker
from .storage import RaceDatabase
from .theme import FONT_FAMILY, PALETTE, apply_ttk_theme
from .widgets import WidgetsMixin


class AppMixin:
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Light")

        self.title("越野计时管理系统")
        self.geometry("1280x820")
        self.minsize(1180, 740)
        self.configure(fg_color=PALETTE["content_bg"])

        self.msg_q = queue.Queue()
        self.worker = SerialWorker(self._enqueue_line, self._enqueue_state)
        self.store = RaceDatabase(Path(__file__).resolve().parent.parent / "attendance.db")
        self.node_last_seen = {}
        self.node_status_map = {}
        self.node_option_map = {}
        self.event_option_map = {}

        self.hw_state = tk.StringVar(value="OFFLINE")
        self.mode_state = tk.StringVar(value="GATEWAY")
        self.wifi_state = tk.StringVar(value="WIFI DISCONNECTED")
        self.ntp_state = tk.StringVar(value="TIME UNKNOWN")
        self.conn_state = tk.StringVar(value="未连接")
        self.readout_state = tk.StringVar(value="等待读卡清算")
        self.write_state = tk.StringVar(value="制卡待命")
        self.last_heartbeat_var = tk.StringVar(value="--")
        self.write_history_records = []

        self.port_var = tk.StringVar(value="")
        self.baud_var = tk.StringVar(value="115200")
        self.ssid_var = tk.StringVar(value="")
        self.pwd_var = tk.StringVar(value="")
        self.custom_var = tk.StringVar(value="")
        self.node_target_var = tk.StringVar(value="")
        self.node_message_var = tk.StringVar(value="")
        self.category_filter_var = tk.StringVar(value="全部")

        self.runner_uid_var = tk.StringVar(value="")
        self.runner_bib_var = tk.StringVar(value="")
        self.runner_name_var = tk.StringVar(value="")
        self.runner_category_var = tk.StringVar(value="")
        self.runner_route_id_var = tk.StringVar(value="")
        self.runner_start_var = tk.StringVar(value="")
        self.current_event_var = tk.StringVar(value="")
        self.judge_uid_var = tk.StringVar(value="")
        self.judge_status_var = tk.StringVar(value="（自动判定）")
        self.judge_penalty_var = tk.StringVar(value="")
        self.judge_start_var = tk.StringVar(value="")
        self.judge_finish_var = tk.StringVar(value="")
        self.judge_note_var = tk.StringVar(value="")

        # 单位 / 通道 / 组别（阶段 3）
        self.unit_name_var = tk.StringVar(value="")
        self.unit_search_var = tk.StringVar(value="")
        self.channel_name_var = tk.StringVar(value="")
        self.channel_first_var = tk.StringVar(value="")
        self.channel_interval_var = tk.StringVar(value="")
        self.channel_slots_var = tk.StringVar(value="")
        self.group_name_var = tk.StringVar(value="")
        self.group_route_var = tk.StringVar(value="")
        self.group_limit_var = tk.StringVar(value="")
        self.group_mode_var = tk.StringVar(value="个人计时")
        self.group_channel_var = tk.StringVar(value="")
        self.group_search_var = tk.StringVar(value="")
        self.runner_unit_var = tk.StringVar(value="")
        self.runner_group_var = tk.StringVar(value="")
        self.start_channel_var = tk.StringVar(value="")
        self.start_channel_option_map = {}
        self.overview_category_var = tk.StringVar(value="全部")
        self.overview_merge_var = tk.BooleanVar(value=False)
        self.overview_topn_var = tk.StringVar(value="10")
        self._big_screen = None
        self._selected_unit_id = None
        self._selected_channel_id = None
        self._selected_group_id = None
        self.group_route_option_map = {}
        self.group_channel_option_map = {}
        self.runner_unit_option_map = {}
        self.runner_group_option_map = {}

        self.cp_mac_var = tk.StringVar(value="")
        self.cp_code_var = tk.StringVar(value="")
        self.cp_is_start_var = tk.BooleanVar(value=False)
        self.cp_is_finish_var = tk.BooleanVar(value=False)

        self.route_id_var = tk.StringVar(value="")
        self.route_name_var = tk.StringVar(value="")
        self.route_type_var = tk.StringVar(value="STANDARD")
        self.route_limit_var = tk.StringVar(value="")
        self.route_penalty_var = tk.StringVar(value="")
        self.route_mode_hint_var = tk.StringVar(value="标准赛按右侧列表顺序判定是否完成路线")
        self.runner_search_var = tk.StringVar(value="")
        self.checkpoint_search_var = tk.StringVar(value="")
        self.route_search_var = tk.StringVar(value="")
        self.detail_search_var = tk.StringVar(value="")
        self.monitor_search_var = tk.StringVar(value="")
        self.result_search_var = tk.StringVar(value="")

        self.detail_route_id_var = tk.StringVar(value="")
        self.detail_cp_mac_var = tk.StringVar(value="")
        self.detail_seq_var = tk.StringVar(value="")
        self.detail_score_var = tk.StringVar(value="")
        self.detail_route_choice_var = tk.StringVar(value="")
        self.detail_cp_choice_var = tk.StringVar(value="")
        self.detail_summary_var = tk.StringVar(value="请选择一条路线后再配置途经点")
        self.detail_selected_label_var = tk.StringVar(value="未选择检查点")
        self.route_option_map = {}
        self.checkpoint_option_map = {}
        self.readout_popup_enabled_var = tk.BooleanVar(value=True)
        self._pager_state = {}
        self._tree_sort_state = {}
        self._normalizing_vars = False
        self._detail_drag_item = None
        self._detail_drag_active = False
        self._readout_popup = None
        self.network_feedback_records = []

        self.cp_mac_var.trace_add("write", self._normalize_checkpoint_mac_var)
        self.detail_cp_mac_var.trace_add("write", self._normalize_detail_cp_mac_var)

        self._build_layout()
        self.refresh_ports()
        self._refresh_event_selector()
        self.refresh_all_setup_views()
        self._refresh_org_views()
        self._refresh_leaderboard()
        self.after(50, self._process_queue)
        self.after(1000, self._status_poller)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # 外壳布局
    # ------------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_treeview_style()
        apply_ttk_theme(ttk.Style(self))

        self.sidebar = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], corner_radius=0, border_width=0, width=180)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)

        self.main_shell = ctk.CTkFrame(self, fg_color=PALETTE["content_bg"], corner_radius=0, border_width=0)
        self.main_shell.grid(row=0, column=1, sticky="nsew")
        self.main_shell.grid_columnconfigure(0, weight=1)
        self.main_shell.grid_rowconfigure(2, weight=1)

        self.page_container = ctk.CTkFrame(self.main_shell, fg_color=PALETTE["content_bg"], corner_radius=0, border_width=0)
        self.page_container.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 12))
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self.nav_buttons = {}
        self.nav_group_state = {}
        self.open_tabs = []
        self.active_page_key = None
        self.breadcrumb_var = tk.StringVar(value="")
        self.live_segment_var = tk.StringVar(value="终端日志")

        self._page_meta = {
            "home": ("首页", "首页"),
            "events": ("赛事", "赛事"),
            "route": ("赛前准备", "路线"),
            "runners": ("赛前准备", "运动员"),
            "units": ("赛前准备", "单位"),
            "groups": ("赛前准备", "组别 & 通道"),
            "starttime": ("赛前准备", "出发时刻"),
            "live": ("竞赛日", "实时成绩"),
            "penalty": ("竞赛日", "选手判罚"),
            "overview_results": ("赛后分析", "成绩一览表"),
            "device": ("工具箱", "设备终端"),
            "network": ("工具箱", "网络"),
            "cardmake": ("工具箱", "制卡"),
        }
        self._nav_tree = [
            ("__top__", [("home", "🏠  首页"), ("events", "🗂  赛事")]),
            ("赛前准备", [("route", "路线"), ("runners", "运动员"), ("units", "单位"), ("groups", "组别 & 通道"), ("starttime", "出发时刻")]),
            ("竞赛日", [("live", "实时成绩"), ("penalty", "选手判罚")]),
            ("赛后分析", [("overview_results", "成绩一览表")]),
            ("工具箱", [("device", "设备终端"), ("network", "网络"), ("cardmake", "制卡")]),
        ]

        self._build_grouped_nav()
        self._build_top_bar()
        self._build_tab_strip()
        self._build_views()
        self._install_modern_tree_behaviors()
        self._open_tab("home")
        self.after(400, self._refresh_aside_visuals)

    # ------------------------------------------------------------------
    # 深色分组侧栏
    # ------------------------------------------------------------------
    def _build_grouped_nav(self):
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent", border_width=0)
        brand.grid(row=0, column=0, sticky="ew", padx=16, pady=(18, 12))
        ctk.CTkLabel(brand, text="◆ 越野计时", font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(brand, text="S3 控制台", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=PALETTE["sidebar_group_text"]).pack(anchor="w", pady=(2, 0))

        self.nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        self.nav_scroll.grid(row=1, column=0, sticky="nsew")
        self.nav_scroll.grid_columnconfigure(0, weight=1)

        for group_key, leaves in self._nav_tree:
            if group_key == "__top__":
                for key, label in leaves:
                    self._make_nav_button(self.nav_scroll, key, label, indent=False)
            else:
                self._make_nav_group(self.nav_scroll, group_key, leaves)

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent", border_width=0)
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=(8, 14))
        ctk.CTkLabel(footer, textvariable=self.conn_state, font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=PALETTE["sidebar_group_text"], wraplength=150, justify="left").pack(anchor="w")

    def _make_nav_group(self, parent, group_key, leaves):
        container = ctk.CTkFrame(parent, fg_color="transparent", border_width=0)
        container.pack(fill="x", pady=(6, 0))
        header = ctk.CTkButton(
            container,
            text="  " + group_key,
            anchor="w",
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=PALETTE["sidebar_bg_hover"],
            text_color=PALETTE["sidebar_group_text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=lambda g=group_key: self._toggle_nav_group(g),
        )
        header.pack(fill="x")
        body = ctk.CTkFrame(container, fg_color="transparent", border_width=0)
        body.pack(fill="x")
        self.nav_group_state[group_key] = {"body": body, "expanded": True}
        for key, label in leaves:
            self._make_nav_button(body, key, label, indent=True)

    def _toggle_nav_group(self, group_key):
        st = self.nav_group_state.get(group_key)
        if not st:
            return
        if st["expanded"]:
            st["body"].pack_forget()
            st["expanded"] = False
        else:
            st["body"].pack(fill="x")
            st["expanded"] = True

    def _make_nav_button(self, parent, key, label, indent):
        btn = ctk.CTkButton(
            parent,
            text=("      " if indent else "  ") + label,
            anchor="w",
            height=40,
            corner_radius=0,
            fg_color="transparent",
            hover_color=PALETTE["sidebar_bg_hover"],
            text_color=PALETTE["sidebar_text"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            command=lambda k=key: self._open_tab(k),
        )
        btn.pack(fill="x")
        self.nav_buttons[key] = btn

    # ------------------------------------------------------------------
    # 顶栏（面包屑 + 当前赛事 + 状态药丸）
    # ------------------------------------------------------------------
    def _build_top_bar(self):
        bar = ctk.CTkFrame(self.main_shell, fg_color=PALETTE["topbar_bg"], corner_radius=0, height=56, border_width=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(bar, textvariable=self.breadcrumb_var, font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=PALETTE["text"]).grid(row=0, column=0, sticky="w", padx=18, pady=12)

        right = ctk.CTkFrame(bar, fg_color="transparent", border_width=0)
        right.grid(row=0, column=2, sticky="e", padx=14)
        ctk.CTkLabel(right, text="当前赛事", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=PALETTE["text_muted"]).pack(side="left", padx=(0, 6))
        self.event_combo = ctk.CTkComboBox(
            right, variable=self.current_event_var, values=[""], width=150, height=32, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
            command=self._on_event_selected,
        )
        self.event_combo.pack(side="left", padx=(0, 8))
        ctk.CTkButton(right, text="新建", width=50, height=30, corner_radius=8, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.create_event_dialog).pack(side="left", padx=2)
        ctk.CTkButton(right, text="重命名", width=58, height=30, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.rename_event_dialog).pack(side="left", padx=2)
        ctk.CTkButton(right, text="归档", width=50, height=30, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.archive_current_event).pack(side="left", padx=(2, 12))
        self._build_status_pill(right, "串口", self.conn_state)
        self._build_status_pill(right, "网关", self.wifi_state)

    def _build_status_pill(self, parent, title, var):
        pill = ctk.CTkFrame(parent, fg_color=PALETTE["field_bg"], corner_radius=14, border_width=0)
        pill.pack(side="left", padx=4)
        ctk.CTkLabel(pill, text=title, font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"), text_color=PALETTE["text_muted"]).pack(side="left", padx=(10, 4), pady=5)
        ctk.CTkLabel(pill, textvariable=var, font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=PALETTE["text"], width=86, anchor="w").pack(side="left", padx=(0, 10), pady=5)

    # ------------------------------------------------------------------
    # 浏览器式标签页
    # ------------------------------------------------------------------
    def _build_tab_strip(self):
        self.tab_bar = ctk.CTkFrame(self.main_shell, fg_color=PALETTE["content_bg"], corner_radius=0, height=38, border_width=0)
        self.tab_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 0))

    def _refresh_tab_strip(self):
        for child in self.tab_bar.winfo_children():
            child.destroy()
        for key in self.open_tabs:
            _, leaf = self._page_meta.get(key, ("", key))
            active = key == self.active_page_key
            chip = ctk.CTkFrame(self.tab_bar, fg_color=PALETTE["card_bg"] if active else PALETTE["field_bg"], corner_radius=8, border_width=0)
            chip.pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                chip, text=leaf, height=28, corner_radius=8, fg_color="transparent",
                hover_color=PALETTE["primary_soft"], text_color=PALETTE["primary"] if active else PALETTE["text_muted"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=lambda k=key: self._show_page(k),
            ).pack(side="left", padx=(6, 0))
            if key != "home":
                ctk.CTkButton(
                    chip, text="✕", width=22, height=28, corner_radius=8, fg_color="transparent",
                    hover_color=PALETTE["primary_soft"], text_color=PALETTE["text_muted"],
                    font=ctk.CTkFont(family=FONT_FAMILY, size=11), command=lambda k=key: self._close_tab(k),
                ).pack(side="left", padx=(0, 4))

    def _open_tab(self, key):
        if key not in self.open_tabs:
            self.open_tabs.append(key)
        self._show_page(key)

    def _close_tab(self, key):
        if key in self.open_tabs:
            self.open_tabs.remove(key)
        if self.active_page_key == key:
            self._show_page(self.open_tabs[-1] if self.open_tabs else "home")
        else:
            self._refresh_tab_strip()

    # ------------------------------------------------------------------
    # 页面注册与切换
    # ------------------------------------------------------------------
    def _build_views(self):
        builders = {
            "home": self._build_overview_page,
            "events": self._build_events_page,
            "route": self._build_event_page,
            "runners": self._build_runners_page,
            "units": self._build_units_page,
            "groups": self._build_groups_page,
            "starttime": self._build_starttime_page,
            "live": self._build_live_page,
            "penalty": self._build_results_page,
            "overview_results": self._build_results_overview_page,
            "device": self._build_device_page,
            "network": self._build_network_page,
            "cardmake": self._build_cardmake_page,
        }
        for key, builder in builders.items():
            self._register_page(key, builder)

    def _register_page(self, key: str, builder):
        page = ctk.CTkFrame(self.page_container, fg_color=PALETTE["content_bg"], border_width=0, corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()
        self.pages[key] = page
        builder(page)

    def _show_page(self, key: str):
        if key not in self.pages:
            return
        for page_key, page in self.pages.items():
            if page_key == key:
                page.grid()
            else:
                page.grid_remove()
        self.active_page_key = key
        group, leaf = self._page_meta.get(key, ("", key))
        self.breadcrumb_var.set(leaf if group in ("首页", "赛事") else f"{group} / {leaf}")
        self._refresh_nav_highlight()
        if key not in self.open_tabs:
            self.open_tabs.append(key)
        self._refresh_tab_strip()

    def _refresh_nav_highlight(self):
        for page_key, button in self.nav_buttons.items():
            active = page_key == self.active_page_key
            button.configure(
                fg_color=PALETTE["sidebar_active"] if active else "transparent",
                hover_color=PALETTE["primary_hover"] if active else PALETTE["sidebar_bg_hover"],
                text_color=PALETTE["sidebar_text_active"] if active else PALETTE["sidebar_text"],
            )

    # ------------------------------------------------------------------
    # 设备终端页（原右侧面板内容）
    # ------------------------------------------------------------------
    def _build_device_page(self, parent):
        parent.grid_columnconfigure(0, weight=0, minsize=360)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.device_card, device_inner = self._make_soft_card(parent, "设备连接", "连接网关并随时查看当前运行状态。")
        self.device_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self._build_right_field(device_inner, "COM 端口")
        self.port_combo = ctk.CTkComboBox(
            device_inner, variable=self.port_var, values=[""], height=38, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
        )
        self.port_combo.pack(fill="x", pady=(0, 12))

        self._build_right_field(device_inner, "波特率")
        self.baud_combo = ctk.CTkComboBox(
            device_inner, variable=self.baud_var, values=["9600", "57600", "115200"], height=38, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
        )
        self.baud_combo.pack(fill="x", pady=(0, 14))

        action_row = ctk.CTkFrame(device_inner, fg_color="transparent", border_width=0)
        action_row.pack(fill="x", pady=(0, 14))
        ctk.CTkButton(action_row, text="连接", width=140, height=38, corner_radius=10, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.connect_serial).pack(side="left")
        ctk.CTkButton(action_row, text="断开", width=140, height=38, corner_radius=10, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.disconnect_serial).pack(side="right")

        self.conn_progress = ctk.CTkProgressBar(device_inner, height=8, corner_radius=999, fg_color=PALETTE["primary_soft"], progress_color=PALETTE["primary"])
        self.conn_progress.pack(fill="x", pady=(0, 14))
        self.conn_progress.set(0.08)

        status_grid = ctk.CTkFrame(device_inner, fg_color="transparent", border_width=0)
        status_grid.pack(fill="x")
        status_grid.grid_columnconfigure((0, 1), weight=1)
        self._build_status_tile(status_grid, 0, 0, "模式", self.mode_state)
        self._build_status_tile(status_grid, 0, 1, "连接", self.conn_state)
        self._build_status_tile(status_grid, 1, 0, "Wi-Fi", self.wifi_state)
        self._build_status_tile(status_grid, 1, 1, "NTP", self.ntp_state)
        self._build_status_tile(status_grid, 2, 0, "心跳", self.last_heartbeat_var)

        self.live_card, live_inner = self._make_soft_card(parent, "动态面板", "在终端日志与实时排名之间切换查看。")
        self.live_card.grid(row=0, column=1, sticky="nsew")
        self.live_segment = ctk.CTkSegmentedButton(
            live_inner, values=["终端日志", "实时排名"], variable=self.live_segment_var, height=40,
            fg_color=PALETTE["primary_soft"], selected_color=PALETTE["primary"], selected_hover_color=PALETTE["primary_hover"],
            unselected_color=PALETTE["primary_soft"], unselected_hover_color=PALETTE["primary_soft_hover"],
            text_color=PALETTE["text_label"], command=self._toggle_live_panel,
        )
        self.live_segment.pack(fill="x", pady=(0, 12))

        self.live_stack = ctk.CTkFrame(live_inner, fg_color="transparent", border_width=0)
        self.live_stack.pack(fill="both", expand=True)

        self.terminal_panel = ctk.CTkFrame(self.live_stack, fg_color="transparent", border_width=0)
        self.terminal_panel.pack(fill="both", expand=True)
        self.terminal_panel.grid_columnconfigure(0, weight=1)
        self.terminal_panel.grid_rowconfigure(0, weight=1)
        self.terminal = ctk.CTkTextbox(self.terminal_panel, fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=0, corner_radius=8, font=("Consolas", 12))
        self.terminal.grid(row=0, column=0, sticky="nsew")

        self.ranking_panel = ctk.CTkFrame(self.live_stack, fg_color="transparent", border_width=0)
        self.ranking_panel.grid_columnconfigure(0, weight=1)
        self.ranking_panel.grid_rowconfigure(1, weight=1)
        ranking_head = ctk.CTkFrame(self.ranking_panel, fg_color="transparent", border_width=0)
        ranking_head.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ranking_head.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(ranking_head, text="刷新", width=84, height=34, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self._refresh_leaderboard).grid(row=0, column=1, sticky="e")
        self.ranking_list = ctk.CTkScrollableFrame(self.ranking_panel, fg_color=PALETTE["card_bg"], corner_radius=0, border_width=0)
        self.ranking_list.grid(row=1, column=0, sticky="nsew")
        self._toggle_live_panel("终端日志")

    # ------------------------------------------------------------------
    # Element 风格分页页脚（客户端分页）
    # ------------------------------------------------------------------
    def _make_pager_footer(self, parent, name, refresh):
        state = {
            "page": 1,
            "size_var": tk.StringVar(value="20"),
            "total_var": tk.StringVar(value="共 0 条"),
            "page_var": tk.StringVar(value="1/1"),
            "refresh": refresh,
        }
        self._pager_state[name] = state
        bar = ctk.CTkFrame(parent, fg_color="transparent", border_width=0)
        ctk.CTkLabel(bar, textvariable=state["total_var"], text_color=PALETTE["text_muted"], font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left")
        ctk.CTkComboBox(
            bar, variable=state["size_var"], values=["10", "20", "50", "100"], width=88, height=30, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
            command=lambda _v, n=name: self._pager_size_changed(n),
        ).pack(side="left", padx=8)
        ctk.CTkButton(bar, text="上一页", width=70, height=30, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=lambda n=name: self._pager_step(n, -1)).pack(side="left", padx=2)
        ctk.CTkLabel(bar, textvariable=state["page_var"], width=56, anchor="center", text_color=PALETTE["text"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(side="left", padx=2)
        ctk.CTkButton(bar, text="下一页", width=70, height=30, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=lambda n=name: self._pager_step(n, 1)).pack(side="left", padx=2)
        return bar

    def _page_slice(self, name, items):
        """按当前分页状态切片；未注册分页器的表原样返回。"""
        state = self._pager_state.get(name)
        if not state:
            return items
        total = len(items)
        try:
            size = max(1, int(state["size_var"].get()))
        except (TypeError, ValueError):
            size = 20
        pages = max(1, math.ceil(total / size))
        state["page"] = min(max(1, state["page"]), pages)
        state["total_var"].set(f"共 {total} 条")
        state["page_var"].set(f"{state['page']}/{pages}")
        start = (state["page"] - 1) * size
        return items[start:start + size]

    def _pager_step(self, name, delta):
        state = self._pager_state.get(name)
        if not state:
            return
        state["page"] = max(1, state["page"] + delta)
        state["refresh"]()

    def _pager_size_changed(self, name):
        state = self._pager_state.get(name)
        if not state:
            return
        state["page"] = 1
        state["refresh"]()

    def _build_right_field(self, parent, label: str):
        ctk.CTkLabel(parent, text=label, text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w", pady=(0, 6))

    def _build_status_tile(self, parent, row: int, column: int, title: str, variable):
        tile = ctk.CTkFrame(parent, fg_color=PALETTE["content_bg"], corner_radius=12, border_width=0)
        tile.grid(row=row, column=column, sticky="ew", padx=4, pady=4)
        ctk.CTkLabel(tile, text=title, text_color=PALETTE["text_muted"], font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold")).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(tile, textvariable=variable, text_color=PALETTE["text"], wraplength=130, justify="left", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(anchor="w", padx=12, pady=(0, 10))

    # ------------------------------------------------------------------
    # 实时成绩页（排行榜）
    # ------------------------------------------------------------------
    def _build_live_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        card, inner = self._make_soft_card(parent, "实时成绩", "终点清算后实时刷新；名次与判罚口径一致。")
        card.grid(row=0, column=0, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(inner, fg_color="transparent", border_width=0)
        head.grid(row=0, column=0, sticky="ew", pady=(12, 8))
        head.grid_columnconfigure(0, weight=1)
        self.category_filter_combo = ctk.CTkComboBox(
            head, variable=self.category_filter_var, values=["全部"], width=150, height=34, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
            command=lambda _v: self._refresh_leaderboard(),
        )
        self.category_filter_combo.grid(row=0, column=1, sticky="e", padx=(0, 8))
        ctk.CTkButton(head, text="刷新", width=72, height=34, corner_radius=8, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self._refresh_leaderboard).grid(row=0, column=2, sticky="e")

        cols = ("rank", "bib", "name", "category", "status", "score", "total")
        self.table = ttk.Treeview(inner, columns=cols, show="headings", style="Dark.Treeview", height=16)
        for col, text, width, anchor in (
            ("rank", "排名", 60, "center"), ("bib", "参赛号", 90, "center"), ("name", "姓名", 140, "w"),
            ("category", "组别", 130, "w"), ("status", "状态", 100, "center"), ("score", "得分", 90, "center"),
            ("total", "总用时", 120, "center"),
        ):
            self.table.heading(col, text=text)
            self.table.column(col, width=width, anchor=anchor)
        self.table.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        pager = self._make_pager_footer(inner, "live", self._refresh_leaderboard)
        pager.grid(row=2, column=0, sticky="ew", pady=(0, 8))

    # ------------------------------------------------------------------
    # 占位页（阶段 3-5 填充）
    # ------------------------------------------------------------------
    def _placeholder_page(self, parent, title, note):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        card, inner = self._make_soft_card(parent, title, note)
        card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(inner, text="本模块将在后续阶段实现。", text_color=PALETTE["text_muted"], font=ctk.CTkFont(family=FONT_FAMILY, size=13)).pack(anchor="w", pady=24)

    def _build_events_page(self, parent):
        self._placeholder_page(parent, "赛事管理", "赛事的新增/切换/重命名/归档在右上角「当前赛事」处操作。")

    def _build_cardmake_page(self, parent):
        self._placeholder_page(parent, "制卡", "常用制卡动作目前集中在「首页」卡片。")


class S3ControlPanel(
    AppMixin,
    OverviewPageMixin,
    SetupPageMixin,
    EventPageMixin,
    ResultsPageMixin,
    OrgPageMixin,
    AnalysisPageMixin,
    NetworkPageMixin,
    RuntimeMixin,
    WidgetsMixin,
    ctk.CTk,
):
    """PC 端 S3 控制台主类。"""


def main():
    app = S3ControlPanel()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app._on_close()
