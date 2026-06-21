"""赛事页：路线途经点配置与成绩处理。"""

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk


class EventPageMixin:
    def _build_route_page(self, parent):
        self._build_route_page_v2(parent)
        return
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        route_frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        route_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self._build_config_page_header(
            route_frame,
            3,
            "路线配置",
            "标准赛按顺序清点，积分赛按分值与时限结算。",
        )

        route_form = ctk.CTkFrame(route_frame, fg_color="transparent")
        route_form.pack(fill="x", padx=12, pady=6)
        self._create_form_row(route_form, "路线 ID:", "整数编号，如 1", 0, textvariable=self.route_id_var)
        self._create_form_row(route_form, "路线名称:", "例如 A 线路", 1, textvariable=self.route_name_var)

        race_type_label = ctk.CTkLabel(
            route_form,
            text="赛制类型:",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        race_type_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=5)
        ctk.CTkComboBox(route_form, variable=self.route_type_var, values=["STANDARD", "SCORE"], width=200).grid(
            row=2, column=1, sticky="w", padx=(5, 10), pady=5
        )

        self._create_form_row(route_form, "时限 (分钟):", "仅积分赛使用", 3, textvariable=self.route_limit_var)
        self._create_form_row(route_form, "超时每分钟扣分:", "仅积分赛使用", 4, textvariable=self.route_penalty_var)

        btn_frame = ctk.CTkFrame(route_form, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=5, padx=30, sticky="n")
        ctk.CTkButton(
            btn_frame,
            text="配置途经点",
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.open_route_detail_page,
        ).pack(pady=4, fill="x")
        ctk.CTkButton(
            btn_frame,
            text="新建",
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.clear_route_form,
        ).pack(pady=4, fill="x")
        ctk.CTkButton(btn_frame, text="保存路线", fg_color="#409eff", hover_color="#337ecc", command=self.save_route).pack(pady=4, fill="x")
        ctk.CTkButton(btn_frame, text="删除所选", fg_color="#c92a2a", hover_color="#a61e1e", command=self.delete_selected_route).pack(
            pady=4, fill="x"
        )

        route_form.grid_columnconfigure(0, weight=0)
        route_form.grid_columnconfigure(1, weight=1)
        route_form.grid_columnconfigure(2, weight=0)

        self._build_rule_hint(
            route_frame,
            "填写规则：路线 ID 必须为整数且唯一；赛制选择 STANDARD 或 SCORE；时限与扣分仅在 SCORE 下生效。",
        )

        self.route_table = ttk.Treeview(
            route_frame,
            columns=("route_id", "name", "type", "limit", "penalty"),
            show="headings",
            style="Dark.Treeview",
            height=7,
        )
        self.route_table.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.route_table.heading("route_id", text="路线ID")
        self.route_table.heading("name", text="名称")
        self.route_table.heading("type", text="赛制")
        self.route_table.heading("limit", text="时限")
        self.route_table.heading("penalty", text="罚分")
        self.route_table.bind("<<TreeviewSelect>>", self._on_route_select)
    def _build_route_detail_page(self, parent):
        self._build_route_detail_page_v2(parent)
        return
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        detail_frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        detail_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self._build_config_page_header(
            detail_frame,
            4,
            "路线详情",
            "为每条路线逐点定义顺序或分值，支撑终点清算。",
        )

        detail_form = ctk.CTkFrame(detail_frame, fg_color="transparent")
        detail_form.pack(fill="x", padx=12, pady=6)
        quick_frame = ctk.CTkFrame(detail_frame, fg_color="#f5f9ff", corner_radius=10, border_width=0)
        quick_frame.pack(fill="x", padx=12, pady=(0, 6))
        quick_frame.grid_columnconfigure(1, weight=1)
        quick_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(
            quick_frame,
            text="快速选择路线",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=(12, 6))
        self.detail_route_combo = ctk.CTkComboBox(
            quick_frame,
            variable=self.detail_route_choice_var,
            values=[""],
            command=self._on_detail_route_choice,
            width=260,
        )
        self.detail_route_combo.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            quick_frame,
            text="快速选择节点",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=2, sticky="w", padx=(12, 8), pady=(12, 6))
        self.detail_cp_combo = ctk.CTkComboBox(
            quick_frame,
            variable=self.detail_cp_choice_var,
            values=[""],
            command=self._on_detail_checkpoint_choice,
            width=260,
        )
        self.detail_cp_combo.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            quick_frame,
            textvariable=self.detail_summary_var,
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 12))
        self._create_form_row(detail_form, "所属路线 ID:", "输入对应的路线编号", 0, textvariable=self.detail_route_id_var)
        self._create_form_row(detail_form, "打卡点 MAC:", "输入 12 位设备标识", 1, textvariable=self.detail_cp_mac_var)
        self._create_form_row(detail_form, "打卡顺序 (标准赛):", "数字 (如: 1, 2, 3)", 2, textvariable=self.detail_seq_var)
        self._create_form_row(detail_form, "获得分值 (积分赛):", "数字 (如: 10, 20)", 3, textvariable=self.detail_score_var)

        btn_frame = ctk.CTkFrame(detail_form, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=4, padx=30, sticky="n")
        ctk.CTkButton(
            btn_frame,
            text="新建",
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            width=100,
            corner_radius=6,
            command=self.clear_route_detail_form,
        ).pack(pady=6)

        ctk.CTkButton(btn_frame, text="新增", fg_color="#409eff", hover_color="#337ecc", width=100, corner_radius=6, command=self.add_route_detail).pack(pady=6)
        ctk.CTkButton(btn_frame, text="刷新", fg_color="transparent", hover_color="#f5f5f7", text_color="#409eff", width=100, corner_radius=6, command=self.refresh_route_details).pack(pady=6)
        ctk.CTkButton(
            btn_frame,
            text="删除",
            fg_color="#c92a2a",
            hover_color="#a61e1e",
            width=100,
            corner_radius=6,
            command=self.delete_selected_route_detail,
        ).pack(pady=6)

        detail_form.grid_columnconfigure(0, weight=0)
        detail_form.grid_columnconfigure(1, weight=1)
        detail_form.grid_columnconfigure(2, weight=0)

        self._build_rule_hint(
            detail_frame,
            "填写规则：所属路线 ID 必须已存在；打卡点 MAC 必须已在步骤 2 建立；标准赛优先填写顺序，积分赛优先填写分值。",
        )

        self.detail_table = ttk.Treeview(
            detail_frame,
            columns=("id", "route_id", "cp_code", "cp_mac", "seq", "score"),
            show="headings",
            style="Dark.Treeview",
            height=7,
        )
        self.detail_table.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.detail_table.heading("id", text="ID")
        self.detail_table.heading("route_id", text="路线ID")
        self.detail_table.heading("cp_code", text="点号")
        self.detail_table.heading("cp_mac", text="点MAC")
        self.detail_table.heading("seq", text="顺序")
        self.detail_table.heading("score", text="分值")
        self.detail_table.bind("<<TreeviewSelect>>", self._on_detail_select)
    def _build_route_page_v2(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        route_frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        route_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self._build_config_page_header(
            route_frame,
            3,
            "路线配置",
            "先明确路线模式，再填写这个模式下真正需要的规则。",
        )

        route_form = ctk.CTkFrame(route_frame, fg_color="transparent")
        route_form.pack(fill="x", padx=12, pady=6)
        self._create_form_row(route_form, "路线 ID:", "整数编号，如 1", 0, textvariable=self.route_id_var)
        self._create_form_row(route_form, "路线名称:", "例如 A 线路", 1, textvariable=self.route_name_var)

        race_type_label = ctk.CTkLabel(
            route_form,
            text="路线模式:",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        race_type_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=5)
        self.route_type_switch = ctk.CTkSegmentedButton(
            route_form,
            values=["STANDARD", "SCORE"],
            variable=self.route_type_var,
            command=self._on_route_type_change,
            width=220,
        )
        self.route_type_switch.grid(row=2, column=1, sticky="w", padx=(5, 10), pady=5)
        self.route_mode_hint_label = ctk.CTkLabel(
            route_form,
            textvariable=self.route_mode_hint_var,
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        )
        self.route_mode_hint_label.grid(row=3, column=1, sticky="w", padx=(5, 10), pady=(0, 8))

        btn_frame = ctk.CTkFrame(route_form, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=4, padx=30, sticky="n")
        ctk.CTkButton(
            btn_frame,
            text="配置途经点",
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.open_route_detail_page,
        ).pack(pady=4, fill="x")
        ctk.CTkButton(
            btn_frame,
            text="新建",
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.clear_route_form,
        ).pack(pady=4, fill="x")
        ctk.CTkButton(btn_frame, text="保存路线", fg_color="#409eff", hover_color="#337ecc", command=self.save_route).pack(pady=4, fill="x")
        ctk.CTkButton(btn_frame, text="删除所选", fg_color="#c92a2a", hover_color="#a61e1e", command=self.delete_selected_route).pack(
            pady=4, fill="x"
        )

        route_form.grid_columnconfigure(0, weight=0)
        route_form.grid_columnconfigure(1, weight=1)
        route_form.grid_columnconfigure(2, weight=0)

        score_rule_card = ctk.CTkFrame(route_frame, fg_color="#f5f9ff", corner_radius=10, border_width=0)
        score_rule_card.pack(fill="x", padx=12, pady=(0, 6))
        score_rule_card.grid_columnconfigure(1, weight=1)
        score_rule_card.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(
            score_rule_card,
            text="积分赛时限 (分钟)",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=(12, 6))
        self.route_limit_entry = ctk.CTkEntry(
            score_rule_card,
            textvariable=self.route_limit_var,
            placeholder_text="仅 SCORE 模式需要填写",
            width=180,
        )
        self.route_limit_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            score_rule_card,
            text="超时每分钟扣分",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=2, sticky="w", padx=(12, 8), pady=(12, 6))
        self.route_penalty_entry = ctk.CTkEntry(
            score_rule_card,
            textvariable=self.route_penalty_var,
            placeholder_text="仅 SCORE 模式需要填写",
            width=180,
        )
        self.route_penalty_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            score_rule_card,
            text="STANDARD 模式下系统会自动忽略积分赛规则；SCORE 模式下请完整填写时限与扣分。",
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 12))

        self._build_rule_hint(
            route_frame,
            "操作建议：先保存路线基本信息，再进入“配置途经点”页面可视化编排检查点。",
        )

        self.route_table = ttk.Treeview(
            route_frame,
            columns=("route_id", "name", "type", "limit", "penalty"),
            show="headings",
            style="Dark.Treeview",
            height=7,
        )
        self.route_table.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.route_table.heading("route_id", text="路线ID")
        self.route_table.heading("name", text="名称")
        self.route_table.heading("type", text="模式")
        self.route_table.heading("limit", text="时限")
        self.route_table.heading("penalty", text="罚分")
        self.route_table.bind("<<TreeviewSelect>>", self._on_route_select)
        self._apply_route_mode_ui()
    def _build_route_detail_page_v2(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        detail_frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        detail_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self._build_config_page_header(
            detail_frame,
            4,
            "路线详情",
            "把检查点加入路线后，可直接拖动右侧列表调整顺序。",
        )

        quick_frame = ctk.CTkFrame(detail_frame, fg_color="#f5f9ff", corner_radius=10, border_width=0)
        quick_frame.pack(fill="x", padx=12, pady=(0, 6))
        quick_frame.grid_columnconfigure(1, weight=1)
        quick_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(
            quick_frame,
            text="快速选择路线",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=(12, 6))
        self.detail_route_combo = ctk.CTkComboBox(
            quick_frame,
            variable=self.detail_route_choice_var,
            values=[""],
            command=self._on_detail_route_choice,
            width=260,
        )
        self.detail_route_combo.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            quick_frame,
            text="快速选择节点",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=2, sticky="w", padx=(12, 8), pady=(12, 6))
        self.detail_cp_combo = ctk.CTkComboBox(
            quick_frame,
            variable=self.detail_cp_choice_var,
            values=[""],
            command=self._on_detail_checkpoint_choice,
            width=260,
        )
        self.detail_cp_combo.grid(row=0, column=3, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            quick_frame,
            textvariable=self.detail_summary_var,
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 12))

        body = ctk.CTkFrame(detail_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            body,
            text="可用检查点",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(
            body,
            text="当前路线检查点",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=2, sticky="w", pady=(0, 6))

        library_wrap = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12, border_width=0)
        library_wrap.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        library_wrap.grid_columnconfigure(0, weight=1)
        library_wrap.grid_rowconfigure(0, weight=1)
        self.available_cp_table = ttk.Treeview(
            library_wrap,
            columns=("cp_code", "cp_mac", "role"),
            show="headings",
            style="Dark.Treeview",
            height=12,
        )
        self.available_cp_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.available_cp_table.heading("cp_code", text="点号")
        self.available_cp_table.heading("cp_mac", text="点MAC")
        self.available_cp_table.heading("role", text="角色")
        self.available_cp_table.bind("<<TreeviewSelect>>", self._on_available_checkpoint_select)
        self.available_cp_table.bind("<Double-1>", lambda _event: self.add_selected_checkpoint_to_route())

        action_wrap = ctk.CTkFrame(body, fg_color="transparent")
        action_wrap.grid(row=1, column=1, sticky="ns", padx=4)
        action_wrap.grid_rowconfigure(0, weight=1)
        action_inner = ctk.CTkFrame(action_wrap, fg_color="transparent")
        action_inner.grid(row=0, column=0, sticky="ns")
        ctk.CTkButton(
            action_inner,
            text="加入 >>",
            width=110,
            fg_color="#409eff",
            hover_color="#337ecc",
            command=self.add_selected_checkpoint_to_route,
        ).pack(pady=(10, 8))
        ctk.CTkButton(
            action_inner,
            text="<< 移除",
            width=110,
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.delete_selected_route_detail,
        ).pack(pady=8)
        ctk.CTkButton(
            action_inner,
            text="刷新",
            width=110,
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.refresh_route_details,
        ).pack(pady=8)
        ctk.CTkButton(
            action_inner,
            text="清空选中",
            width=110,
            fg_color="transparent",
            hover_color="#f5f5f7",
            text_color="#409eff",
            command=self.clear_route_detail_form,
        ).pack(pady=8)

        route_wrap = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12, border_width=0)
        route_wrap.grid(row=1, column=2, sticky="nsew", padx=(8, 0))
        route_wrap.grid_columnconfigure(0, weight=1)
        route_wrap.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            route_wrap,
            text="拖动右侧列表可以调整路线顺序，双击左侧检查点可以直接加入。",
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.detail_table = ttk.Treeview(
            route_wrap,
            columns=("seq", "cp_code", "cp_mac", "role", "score"),
            show="headings",
            style="Dark.Treeview",
            height=12,
        )
        self.detail_table.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.detail_table.heading("seq", text="顺序")
        self.detail_table.heading("cp_code", text="点号")
        self.detail_table.heading("cp_mac", text="点MAC")
        self.detail_table.heading("role", text="角色")
        self.detail_table.heading("score", text="分值")
        self.detail_table.bind("<<TreeviewSelect>>", self._on_detail_select)
        self.detail_table.bind("<Delete>", lambda _event: self.delete_selected_route_detail())
        self.detail_table.bind("<ButtonPress-1>", self._on_detail_drag_start)
        self.detail_table.bind("<B1-Motion>", self._on_detail_drag_motion)
        self.detail_table.bind("<ButtonRelease-1>", self._on_detail_drag_release)

        editor = ctk.CTkFrame(detail_frame, fg_color="#f5f9ff", corner_radius=10, border_width=0)
        editor.pack(fill="x", padx=12, pady=(0, 12))
        editor.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            editor,
            text="当前选中",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=(12, 8), pady=(12, 6))
        ctk.CTkLabel(
            editor,
            textvariable=self.detail_selected_label_var,
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(12, 6))
        ctk.CTkLabel(
            editor,
            text="积分赛分值",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=(0, 12))
        self.detail_score_entry = ctk.CTkEntry(
            editor,
            textvariable=self.detail_score_var,
            placeholder_text="仅 SCORE 模式可编辑",
            width=180,
        )
        self.detail_score_entry.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 12))
        ctk.CTkButton(
            editor,
            text="应用分值",
            width=110,
            fg_color="#409eff",
            hover_color="#337ecc",
            command=self.apply_selected_detail_score,
        ).grid(row=1, column=2, sticky="e", padx=(0, 12), pady=(0, 12))

        self._build_rule_hint(
            detail_frame,
            "STANDARD 模式下以右侧顺序为准；SCORE 模式下可在选中检查点后为其设置分值。",
        )
    def _build_event_page(self, parent):
        page = ctk.CTkScrollableFrame(parent, fg_color="#f5f5f7", corner_radius=0, border_width=0)
        page.pack(fill="both", expand=True)

        route_card, route_inner = self._make_soft_card(
            page,
            "赛事规则配置",
            "先确定赛事模式，再填写真正需要的规则；SCORE 模式会展开时限和超时扣分。",
        )
        route_card.pack(fill="x", padx=8, pady=(0, 20))

        form_wrap = ctk.CTkFrame(route_inner, fg_color="transparent", border_width=0)
        form_wrap.pack(fill="x", pady=(0, 20))
        self._pack_entry_row(form_wrap, "路线 ID", self.route_id_var, "整数编号")
        self._pack_entry_row(form_wrap, "路线名称", self.route_name_var, "例如 A 线", pady=(0, 12))

        self.mode_row = ctk.CTkFrame(form_wrap, fg_color="transparent", border_width=0)
        self.mode_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            self.mode_row,
            text="赛事模式",
            width=100,
            anchor="e",
            text_color="#64748B",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        ).pack(side="left", padx=(0, 14))
        self.route_type_switch = ctk.CTkSegmentedButton(
            self.mode_row,
            values=["STANDARD", "SCORE"],
            variable=self.route_type_var,
            height=40,
            width=260,
            corner_radius=12,
            fg_color="#ecf5ff",
            selected_color="#409eff",
            selected_hover_color="#337ecc",
            unselected_color="#F8FAFC",
            unselected_hover_color="#F1F5F9",
            text_color="#475569",
            command=self._on_race_type_change,
        )
        self.route_type_switch.pack(side="left")
        if not getattr(self, "_route_type_trace_bound", False):
            self.route_type_var.trace_add("write", self._on_route_type_var_write)
            self._route_type_trace_bound = True

        self.score_settings_row = ctk.CTkFrame(form_wrap, fg_color="transparent", border_width=0)
        limit_group = ctk.CTkFrame(self.score_settings_row, fg_color="transparent", border_width=0)
        limit_group.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(limit_group, text="关门时限", width=100, anchor="e", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).pack(side="left", padx=(0, 14))
        self.route_limit_entry = ctk.CTkEntry(limit_group, textvariable=self.route_limit_var, placeholder_text="分钟，例如 120", fg_color="#F8FAFC", border_width=0, height=40, corner_radius=12)
        self.route_limit_entry.pack(side="left", fill="x", expand=True)

        penalty_group = ctk.CTkFrame(self.score_settings_row, fg_color="transparent", border_width=0)
        penalty_group.pack(side="left", fill="x", expand=True, padx=(16, 0))
        ctk.CTkLabel(penalty_group, text="超时扣分", width=100, anchor="e", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).pack(side="left", padx=(0, 14))
        self.route_penalty_entry = ctk.CTkEntry(penalty_group, textvariable=self.route_penalty_var, placeholder_text="每分钟扣多少分", fg_color="#F8FAFC", border_width=0, height=40, corner_radius=12)
        self.route_penalty_entry.pack(side="left", fill="x", expand=True)

        self.route_mode_note = ctk.CTkLabel(route_inner, textvariable=self.route_mode_hint_var, text_color="#64748B", justify="left", wraplength=860)
        self.route_mode_note.pack(fill="x", pady=(0, 20))

        route_actions = ctk.CTkFrame(route_inner, fg_color="transparent", border_width=0)
        route_actions.pack(fill="x")
        ctk.CTkButton(route_actions, text="配置检查点", width=160, height=42, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.open_route_detail_page).pack(side="left")
        ctk.CTkButton(route_actions, text="清空表单", width=160, height=42, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.clear_route_form).pack(side="right")
        ctk.CTkButton(route_actions, text="保存路线配置", width=160, height=42, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.save_route).pack(side="right", padx=(0, 12))

        route_table_card, route_table_inner = self._make_soft_card(page, "路线列表", "把路线模式、关门时限和超时扣分固定显示在表头下，便于快速核对。")
        route_table_card.pack(fill="x", padx=8, pady=(0, 20))
        route_table_section, route_table_toolbar, route_table_shell, self.route_empty_label = self._make_table_section(route_table_inner, "路线配置总览", "支持搜索、排序与批量删除；SCORE 规则缺失会被高亮。", "当前还没有路线数据")
        route_table_section.pack(fill="both", expand=True, pady=(14, 0))
        self._build_search_bar(route_table_toolbar, self.route_search_var, "搜索路线 ID / 名称 / 模式", self.refresh_routes, row=0, trailing_buttons=[("删除所选", self.delete_selected_route, "danger"), ("路线模板", self.export_route_template, "ghost")])
        self.route_table = ttk.Treeview(route_table_shell, columns=("route_id", "name", "type", "limit", "penalty"), show="headings", style="Dark.Treeview", height=6)
        self.route_table.heading("route_id", text="路线 ID")
        self.route_table.heading("name", text="名称")
        self.route_table.heading("type", text="模式")
        self.route_table.heading("limit", text="关门时限")
        self.route_table.heading("penalty", text="超时扣分")
        self.route_table.column("route_id", width=110, anchor="center")
        self.route_table.column("name", width=200, anchor="w")
        self.route_table.column("type", width=110, anchor="center")
        self.route_table.column("limit", width=130, anchor="center")
        self.route_table.column("penalty", width=130, anchor="center")
        self.route_table.bind("<<TreeviewSelect>>", self._on_route_select)
        self._mount_treeview(self.route_table, route_table_shell, self.route_empty_label)

        detail_card, detail_inner = self._make_soft_card(page, "路线编排", "左侧选择候选检查点，右侧维护当前路线顺序；STANDARD 看顺序，SCORE 可附带分值。")
        detail_card.pack(fill="both", expand=True, padx=8, pady=(0, 20))
        detail_inner.grid_columnconfigure(0, weight=1)
        detail_inner.grid_columnconfigure(2, weight=1)
        detail_inner.grid_rowconfigure(1, weight=1)

        detail_top = ctk.CTkFrame(detail_inner, fg_color="transparent", border_width=0)
        detail_top.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        detail_top.grid_columnconfigure(1, weight=1)
        detail_top.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(detail_top, text="当前路线", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.detail_route_combo = ctk.CTkComboBox(detail_top, variable=self.detail_route_choice_var, values=[""], height=40, corner_radius=12, fg_color="#F8FAFC", border_width=0, button_color="#409eff", button_hover_color="#337ecc", command=self._on_detail_route_choice)
        self.detail_route_combo.grid(row=0, column=1, sticky="ew", padx=(0, 16))
        ctk.CTkLabel(detail_top, text="当前检查点", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.detail_cp_combo = ctk.CTkComboBox(detail_top, variable=self.detail_cp_choice_var, values=[""], height=40, corner_radius=12, fg_color="#F8FAFC", border_width=0, button_color="#409eff", button_hover_color="#337ecc", command=self._on_detail_checkpoint_choice)
        self.detail_cp_combo.grid(row=0, column=3, sticky="ew")
        ctk.CTkLabel(detail_top, textvariable=self.detail_summary_var, text_color="#64748B", justify="left", wraplength=860).grid(row=1, column=0, columnspan=4, sticky="ew", pady=(12, 0))

        available_section, available_toolbar, available_shell, self.available_cp_empty_label = self._make_table_section(detail_inner, "可用检查点", "从已建立的检查点库中选择候选点，支持按表头排序查看。", "当前还没有可用检查点")
        available_section.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        available_toolbar.grid_remove()
        self.available_cp_table = ttk.Treeview(available_shell, columns=("cp_code", "cp_mac", "role"), show="headings", style="Dark.Treeview", height=10)
        self.available_cp_table.heading("cp_code", text="点号")
        self.available_cp_table.heading("cp_mac", text="MAC")
        self.available_cp_table.heading("role", text="角色")
        self.available_cp_table.column("cp_code", width=90, anchor="center")
        self.available_cp_table.column("cp_mac", width=190, anchor="center")
        self.available_cp_table.column("role", width=120, anchor="center")
        self.available_cp_table.bind("<<TreeviewSelect>>", self._on_available_checkpoint_select)
        self._mount_treeview(self.available_cp_table, available_shell, self.available_cp_empty_label)

        editor_col = ctk.CTkFrame(detail_inner, fg_color="transparent", border_width=0)
        editor_col.grid(row=1, column=1, sticky="ns")
        ctk.CTkButton(editor_col, text="加入 >", width=120, height=40, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.add_selected_checkpoint_to_route).pack(pady=(40, 10))
        ctk.CTkButton(editor_col, text="< 删除", width=120, height=40, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.delete_selected_route_detail).pack(pady=10)
        ctk.CTkLabel(editor_col, text="分值", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).pack(anchor="w", pady=(18, 6))
        self.detail_score_entry = ctk.CTkEntry(editor_col, textvariable=self.detail_score_var, width=120, height=40, corner_radius=12, fg_color="#F8FAFC", border_width=0)
        self.detail_score_entry.pack(fill="x")
        ctk.CTkButton(editor_col, text="应用分值", width=120, height=40, corner_radius=14, fg_color="#F1F5F9", hover_color="#E2E8F0", text_color="#409eff", command=self.apply_selected_detail_score).pack(pady=(10, 0))
        ctk.CTkLabel(editor_col, text="提示：拖动右侧列表可调整顺序", text_color="#94A3B8", justify="center", wraplength=120).pack(pady=(14, 0))

        detail_section, detail_toolbar, detail_shell, self.detail_empty_label = self._make_table_section(detail_inner, "当前路线检查点", "顺序、角色和分值会固定显示；在 SCORE 模式下缺失分值会高亮。", "当前路线还没有配置检查点")
        detail_section.grid(row=1, column=2, sticky="nsew")
        detail_toolbar.grid_remove()
        self.detail_table = ttk.Treeview(detail_shell, columns=("index", "cp_code", "cp_mac", "role", "score"), show="headings", style="Dark.Treeview", height=10)
        self.detail_table.heading("index", text="顺序")
        self.detail_table.heading("cp_code", text="点号")
        self.detail_table.heading("cp_mac", text="MAC")
        self.detail_table.heading("role", text="角色")
        self.detail_table.heading("score", text="分值")
        self.detail_table.column("index", width=72, anchor="center")
        self.detail_table.column("cp_code", width=90, anchor="center")
        self.detail_table.column("cp_mac", width=190, anchor="center")
        self.detail_table.column("role", width=110, anchor="center")
        self.detail_table.column("score", width=90, anchor="center")
        self.detail_table.bind("<<TreeviewSelect>>", self._on_detail_select)
        self.detail_table.bind("<ButtonPress-1>", self._on_detail_drag_start)
        self.detail_table.bind("<B1-Motion>", self._on_detail_drag_motion)
        self.detail_table.bind("<ButtonRelease-1>", self._on_detail_drag_release)
        self._mount_treeview(self.detail_table, detail_shell, self.detail_empty_label)

        self._apply_route_mode_ui()
    def _on_available_checkpoint_select(self, _event=None):
        selected = self.available_cp_table.selection() if hasattr(self, "available_cp_table") else ()
        if not selected:
            return
        values = self.available_cp_table.item(selected[0]).get("values") or []
        if len(values) < 2:
            return
        self._set_detail_checkpoint(str(values[1]))
    def _collect_detail_rows_from_table(self):
        rows = []
        for index, item_id in enumerate(self.detail_table.get_children(), start=1):
            values = self.detail_table.item(item_id).get("values") or []
            if len(values) < 5:
                continue
            score_text = str(values[4]).strip()
            score_value = None
            if score_text not in ("", "-", "None"):
                try:
                    score_value = int(score_text)
                except ValueError:
                    score_value = None
            rows.append(
                {
                    "cp_mac": str(values[2]).upper(),
                    "seq_order": index,
                    "score_value": score_value,
                }
            )
        return rows
    def _save_route_detail_rows(self, route_id: int, rows: list, selected_cp_mac: str = ""):
        normalized_rows = []
        for index, row in enumerate(rows, start=1):
            normalized_rows.append(
                {
                    "cp_mac": str(row.get("cp_mac") or "").upper(),
                    "seq_order": index,
                    "score_value": row.get("score_value"),
                }
            )
        self.store.replace_route_details(route_id, normalized_rows)
        self.refresh_route_details()
        if selected_cp_mac and hasattr(self, "detail_table"):
            self._select_tree_item_by_value(self.detail_table, selected_cp_mac, column_index=2)
    def add_selected_checkpoint_to_route(self):
        route_id_text = self.detail_route_id_var.get().strip()
        if not route_id_text:
            messagebox.showwarning("提示", "请先选择一条路线")
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            messagebox.showwarning("提示", "路线ID 必须是整数")
            return

        route = self.store.get_route(route_id)
        if not route:
            messagebox.showwarning("提示", "请先保存路线，再配置检查点")
            return

        selected = self.available_cp_table.selection() if hasattr(self, "available_cp_table") else ()
        if not selected:
            cp_mac = self.detail_cp_mac_var.get().strip().upper()
            if not cp_mac:
                messagebox.showwarning("提示", "请先在左侧选择一个检查点")
                return
            cp_macs = [cp_mac]
        else:
            cp_macs = []
            for item_id in selected:
                values = self.available_cp_table.item(item_id).get("values") or []
                if len(values) >= 2:
                    cp_macs.append(str(values[1]).upper())

        existing_rows = self.store.list_route_details(route_id)
        existing_macs = {str(row.get("cp_mac") or "").upper() for row in existing_rows}
        updated_rows = [
            {
                "cp_mac": str(row.get("cp_mac") or "").upper(),
                "seq_order": row.get("seq_order"),
                "score_value": row.get("score_value"),
            }
            for row in existing_rows
        ]

        added_mac = ""
        for cp_mac in cp_macs:
            if not cp_mac or cp_mac in existing_macs:
                continue
            updated_rows.append(
                {
                    "cp_mac": cp_mac,
                    "seq_order": None,
                    "score_value": 0 if (route.get("race_type") or "STANDARD").upper() == "SCORE" else None,
                }
            )
            existing_macs.add(cp_mac)
            added_mac = cp_mac

        if not added_mac:
            messagebox.showwarning("提示", "所选检查点已在当前路线中")
            return

        self._save_route_detail_rows(route_id, updated_rows, selected_cp_mac=added_mac)
    def apply_selected_detail_score(self):
        route_id_text = self.detail_route_id_var.get().strip()
        if not route_id_text:
            messagebox.showwarning("提示", "请先选择一条路线")
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            messagebox.showwarning("提示", "路线ID 必须是整数")
            return

        route = self.store.get_route(route_id)
        if not route or (route.get("race_type") or "STANDARD").upper() != "SCORE":
            messagebox.showwarning("提示", "只有 SCORE 模式需要设置分值")
            return

        selected = self.detail_table.selection() if hasattr(self, "detail_table") else ()
        if not selected:
            messagebox.showwarning("提示", "请先在右侧选择一个检查点")
            return
        values = self.detail_table.item(selected[0]).get("values") or []
        if len(values) < 5:
            return
        cp_mac = str(values[2]).upper()

        score_text = self.detail_score_var.get().strip()
        try:
            score_value = int(score_text) if score_text else 0
        except ValueError:
            messagebox.showwarning("提示", "分值必须是整数")
            return

        rows = self._collect_detail_rows_from_table()
        for row in rows:
            if row["cp_mac"] == cp_mac:
                row["score_value"] = score_value
                break
        self._save_route_detail_rows(route_id, rows, selected_cp_mac=cp_mac)
    def _on_detail_drag_start(self, event):
        if not hasattr(self, "detail_table"):
            return
        item_id = self.detail_table.identify_row(event.y)
        if item_id:
            self._detail_drag_item = item_id
            self._detail_drag_active = True
    def _on_detail_drag_motion(self, event):
        if not self._detail_drag_active or not self._detail_drag_item:
            return
        target = self.detail_table.identify_row(event.y)
        if not target or target == self._detail_drag_item:
            return
        target_index = self.detail_table.index(target)
        self.detail_table.move(self._detail_drag_item, "", target_index)
    def _on_detail_drag_release(self, _event):
        if not self._detail_drag_active:
            return
        self._detail_drag_active = False
        dragged_item = self._detail_drag_item
        self._detail_drag_item = None
        route_id_text = self.detail_route_id_var.get().strip()
        if not route_id_text or not dragged_item:
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            return
        values = self.detail_table.item(dragged_item).get("values") or []
        selected_cp_mac = str(values[2]).upper() if len(values) >= 3 else ""
        rows = self._collect_detail_rows_from_table()
        self._save_route_detail_rows(route_id, rows, selected_cp_mac=selected_cp_mac)
    def delete_selected_route(self):
        selected = self.route_table.selection() if hasattr(self, "route_table") else ()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条路线")
            return
        item = self.route_table.item(selected[0])
        route_id = (item.get("values") or [""])[0]
        if route_id in ("", None):
            return
        try:
            self.store.delete_route(int(route_id))
        except (sqlite3.Error, ValueError) as exc:
            messagebox.showerror("删除失败", str(exc))
            return
        self.refresh_routes()
        if self.detail_route_id_var.get().strip() == str(route_id):
            self.clear_route_detail_form(keep_route=False)
        self.refresh_route_details()
        self.refresh_runners()
    def delete_selected_route_detail(self):
        selected = self.detail_table.selection() if hasattr(self, "detail_table") else ()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个路线检查点")
            return

        route_id_text = self.detail_route_id_var.get().strip()
        if not route_id_text:
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            return

        remove_macs = set()
        for item_id in selected:
            values = self.detail_table.item(item_id).get("values") or []
            if len(values) >= 3:
                remove_macs.add(str(values[2]).upper())
        if not remove_macs:
            return

        updated_rows = [row for row in self._collect_detail_rows_from_table() if row["cp_mac"] not in remove_macs]
        try:
            self.store.replace_route_details(route_id, updated_rows)
        except sqlite3.Error as exc:
            messagebox.showerror("删除失败", str(exc))
            return

        self.refresh_route_details()
        self.clear_route_detail_form(keep_route=True)
    def _on_route_select(self, _event=None):
        selected = self.route_table.selection() if hasattr(self, "route_table") else ()
        if not selected:
            return
        values = self.route_table.item(selected[0]).get("values") or []
        if len(values) < 5:
            return
        self.route_id_var.set(str(values[0]))
        self.route_name_var.set(str(values[1]))
        self.route_type_var.set(str(values[2]) if str(values[2]) else "STANDARD")
        self.route_limit_var.set("" if str(values[3]) in ("", "-") else str(values[3]))
        self.route_penalty_var.set("" if str(values[4]) in ("", "-") else str(values[4]))
        self._apply_route_mode_ui()
        self._set_detail_route(str(values[0]))
        self.refresh_route_details()
    def _on_detail_select(self, _event=None):
        selected = self.detail_table.selection() if hasattr(self, "detail_table") else ()
        if not selected:
            self.detail_selected_label_var.set("未选择检查点")
            return
        values = self.detail_table.item(selected[0]).get("values") or []
        if len(values) < 5:
            return
        self._set_detail_checkpoint(str(values[2]))
        self.detail_seq_var.set(str(values[0]))
        self.detail_score_var.set("" if str(values[4]) in ("", "-", "None") else str(values[4]))
        self.detail_selected_label_var.set(f"{values[1]} | {values[2]}")
    def _on_detail_route_choice(self, choice: str):
        route_id = self.route_option_map.get(choice, "")
        if not route_id:
            return
        self._set_detail_route(route_id)
        self.refresh_route_details()
    def _on_detail_checkpoint_choice(self, choice: str):
        cp_mac = self.checkpoint_option_map.get(choice, "")
        if cp_mac:
            self._set_detail_checkpoint(cp_mac)
    def _set_detail_route(self, route_id):
        route_text = "" if route_id in ("", None) else str(route_id)
        self.detail_route_id_var.set(route_text)
        if route_text:
            try:
                route = self.store.get_route(int(route_text))
            except ValueError:
                route = None
            if route:
                self.route_type_var.set((route.get("race_type") or "STANDARD").upper())
                self.route_limit_var.set("" if route.get("time_limit_min") is None else str(route.get("time_limit_min")))
                self.route_penalty_var.set("" if route.get("penalty_per_min") is None else str(route.get("penalty_per_min")))
                self._apply_route_mode_ui()
        if hasattr(self, "detail_route_combo"):
            label = self._find_option_label(self.route_option_map, route_text)
            self.detail_route_choice_var.set(label or route_text)
    def _set_detail_checkpoint(self, cp_mac: str):
        cp_text = (cp_mac or "").upper()
        self.detail_cp_mac_var.set(cp_text)
        if hasattr(self, "detail_cp_combo"):
            label = self._find_option_label(self.checkpoint_option_map, cp_text)
            self.detail_cp_choice_var.set(label or cp_text)
    def _refresh_detail_route_options(self):
        routes = self.store.list_routes()
        self.route_option_map = {}
        values = []
        for route in routes:
            route_id = route.get("route_id")
            if route_id in ("", None):
                continue
            label = f"{route_id} | {route.get('route_name') or 'Unnamed'} | {route.get('race_type') or 'STANDARD'}"
            self.route_option_map[label] = str(route_id)
            values.append(label)

        if hasattr(self, "detail_route_combo"):
            self.detail_route_combo.configure(values=values or [""])
        current = self.detail_route_id_var.get().strip()
        if current:
            self._set_detail_route(current)
        elif len(values) == 1:
            self._set_detail_route(self.route_option_map[values[0]])
        else:
            self.detail_route_choice_var.set("")
    def _refresh_detail_checkpoint_options(self):
        checkpoints = self.store.list_checkpoints()
        self.checkpoint_option_map = {}
        values = []
        for checkpoint in checkpoints:
            mac = (checkpoint.get("mac") or "").upper()
            if not mac:
                continue
            role_parts = []
            if checkpoint.get("is_start"):
                role_parts.append("起点")
            if checkpoint.get("is_finish"):
                role_parts.append("终点")
            role = "/".join(role_parts) if role_parts else "普通点"
            cp_code = checkpoint.get("cp_code") or "-"
            label = f"{cp_code} | {role} | {mac}"
            self.checkpoint_option_map[label] = mac
            values.append(label)

        if hasattr(self, "detail_cp_combo"):
            self.detail_cp_combo.configure(values=values or [""])
        current = self.detail_cp_mac_var.get().strip().upper()
        if current:
            self._set_detail_checkpoint(current)
        elif len(values) == 1:
            self._set_detail_checkpoint(self.checkpoint_option_map[values[0]])
        else:
            self.detail_cp_choice_var.set("")
    def _update_detail_summary(self, route_id_text: str, detail_rows=None):
        route_id_text = route_id_text.strip()
        if not route_id_text:
            self.detail_summary_var.set("请选择一条路线后再配置途经点")
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            self.detail_summary_var.set(f"路线 {route_id_text} 不是有效的数字 ID")
            return

        route = self.store.get_route(route_id)
        if not route:
            self.detail_summary_var.set(f"路线 {route_id_text} 尚未创建，请先保存路线基本信息")
            return

        rows = detail_rows if detail_rows is not None else self.store.list_route_details(route_id)
        race_type = route.get("race_type") or "STANDARD"
        route_name = route.get("route_name") or "未命名路线"
        self.detail_summary_var.set(f"当前路线：{route_name} ({race_type})，已配置 {len(rows)} 个节点")
    def clear_route_form(self):
        self.route_id_var.set("")
        self.route_name_var.set("")
        self.route_type_var.set("STANDARD")
        self.route_limit_var.set("")
        self.route_penalty_var.set("")
        self._apply_route_mode_ui()
        if hasattr(self, "route_table"):
            self.route_table.selection_remove(self.route_table.selection())
    def clear_route_detail_form(self, keep_route: bool = True):
        route_id = self.detail_route_id_var.get().strip() if keep_route else ""
        self.detail_seq_var.set("")
        self.detail_score_var.set("")
        self.detail_selected_label_var.set("未选择检查点")
        self.detail_cp_choice_var.set("")
        self.detail_cp_mac_var.set("")
        if not keep_route:
            self.detail_route_choice_var.set("")
            self.detail_route_id_var.set("")
        else:
            self._set_detail_route(route_id)
        if hasattr(self, "detail_table"):
            self.detail_table.selection_remove(self.detail_table.selection())
        if hasattr(self, "available_cp_table"):
            self.available_cp_table.selection_remove(self.available_cp_table.selection())
        self._update_detail_editor_state()
    def open_route_detail_page(self):
        route_id = self.route_id_var.get().strip()
        if not route_id and hasattr(self, "route_table"):
            selected = self.route_table.selection()
            if selected:
                values = self.route_table.item(selected[0]).get("values") or []
                if values:
                    route_id = str(values[0])
        if not route_id:
            messagebox.showwarning("提示", "请先选择或保存一条路线")
            return
        self._set_detail_route(route_id)
        self.refresh_route_details()
        self._show_page("event")
        if hasattr(self, "detail_route_combo"):
            self.detail_route_combo.focus_set()
    def save_route(self):
        route_id_text = self.route_id_var.get().strip()
        if not route_id_text:
            messagebox.showwarning("提示", "路线ID 不能为空")
            return

        mode = (self.route_type_var.get().strip() or "STANDARD").upper()
        limit_text = self.route_limit_var.get().strip()
        penalty_text = self.route_penalty_var.get().strip()
        try:
            route_id = int(route_id_text)
            if mode == "SCORE":
                if not limit_text or not penalty_text:
                    messagebox.showwarning("提示", "SCORE 模式必须填写时限和超时扣分")
                    return
                limit = int(limit_text)
                penalty = int(penalty_text)
            else:
                limit = None
                penalty = None
        except ValueError:
            messagebox.showwarning("提示", "路线ID/时限/罚分必须是整数")
            return

        try:
            self.store.upsert_route(
                route_id=route_id,
                route_name=self.route_name_var.get().strip(),
                race_type=mode,
                time_limit_min=limit,
                penalty_per_min=penalty,
            )
        except sqlite3.Error as exc:
            messagebox.showerror("保存失败", str(exc))
            return

        self.route_type_var.set(mode)
        if mode != "SCORE":
            self.route_limit_var.set("")
            self.route_penalty_var.set("")
        self._apply_route_mode_ui()
        self.refresh_routes()
        self._set_detail_route(route_id)
        self.refresh_route_details()
        if hasattr(self, "route_table"):
            self._select_tree_item_by_value(self.route_table, route_id)
    def add_route_detail(self):
        self.add_selected_checkpoint_to_route()
    def refresh_routes(self):
        if not hasattr(self, "route_table"):
            return
        current_route_id = self.route_id_var.get().strip()
        query = self.route_search_var.get().strip().lower()
        for item in self.route_table.get_children():
            self.route_table.delete(item)
        for row in self.store.list_routes():
            race_type = (row.get("race_type") or "STANDARD").upper()
            values = (
                row.get("route_id") if row.get("route_id") is not None else "",
                row.get("route_name") or "",
                race_type,
                row.get("time_limit_min") if race_type == "SCORE" and row.get("time_limit_min") is not None else "-",
                row.get("penalty_per_min") if race_type == "SCORE" and row.get("penalty_per_min") is not None else "-",
            )
            if not self._row_matches_query(list(values), query):
                continue
            missing_score_rule = race_type == "SCORE" and (values[3] == "-" or values[4] == "-")
            tags = ("missing",) if (not values[1] or missing_score_rule) else ()
            self.route_table.insert("", tk.END, values=values, tags=tags)
        self._refresh_detail_route_options()
        if current_route_id:
            self._select_tree_item_by_value(self.route_table, current_route_id)
        self._reapply_tree_sort(self.route_table)
        self._update_table_empty_state(self.route_table, getattr(self, "route_empty_label", None))
    def refresh_route_details(self):
        if not hasattr(self, "detail_table"):
            return

        current_cp_mac = self.detail_cp_mac_var.get().strip().upper()
        for item in self.detail_table.get_children():
            self.detail_table.delete(item)
        self._refresh_available_checkpoint_table()

        route_id_text = self.detail_route_id_var.get().strip()
        if not route_id_text:
            self._update_detail_summary("")
            self.detail_selected_label_var.set("未选择检查点")
            self._update_detail_editor_state()
            return
        try:
            route_id = int(route_id_text)
        except ValueError:
            self._update_detail_summary(route_id_text)
            self._update_detail_editor_state()
            return

        self._apply_route_mode_ui()
        checkpoints_map = self.store.get_checkpoints_map()
        rows = sorted(
            self.store.list_route_details(route_id),
            key=lambda row: (
                row.get("seq_order") is None,
                row.get("seq_order") if row.get("seq_order") is not None else 10**9,
                row.get("cp_mac") or "",
            ),
        )
        for index, row in enumerate(rows, start=1):
            cp_mac = (row.get("cp_mac") or "").upper()
            checkpoint = checkpoints_map.get(cp_mac) or {}
            self.detail_table.insert(
                "",
                tk.END,
                values=(
                    index,
                    checkpoint.get("cp_code") or "",
                    cp_mac,
                    self._checkpoint_role_text(checkpoint),
                    row.get("score_value") if row.get("score_value") is not None else "",
                ),
            )
        self._update_detail_summary(route_id_text, rows)
        if current_cp_mac:
            self._select_tree_item_by_value(self.detail_table, current_cp_mac, column_index=2)
        self._update_detail_editor_state()
    def _refresh_available_checkpoint_table(self):
        if not hasattr(self, "available_cp_table"):
            return
        current_mac = self.detail_cp_mac_var.get().strip().upper()
        for item in self.available_cp_table.get_children():
            self.available_cp_table.delete(item)
        for row in self.store.list_checkpoints():
            tags = ("missing",) if not (row.get("cp_code") or "") else ()
            self.available_cp_table.insert(
                "",
                tk.END,
                values=(
                    row.get("cp_code") or "",
                    (row.get("mac") or "").upper(),
                    self._checkpoint_role_text(row),
                ),
                tags=tags,
            )
        if current_mac:
            self._select_tree_item_by_value(self.available_cp_table, current_mac, column_index=1)
        self._reapply_tree_sort(self.available_cp_table)
        self._update_table_empty_state(self.available_cp_table, getattr(self, "available_cp_empty_label", None))
    def _on_race_type_change(self, choice: str):
        mode = (choice or "STANDARD").strip().upper()
        if mode not in {"STANDARD", "SCORE"}:
            mode = "STANDARD"
        self.route_type_var.set(mode)
        if hasattr(self, "route_type_switch"):
            try:
                self.route_type_switch.set(mode)
            except Exception:
                pass
        if hasattr(self, "route_type_menu"):
            try:
                self.route_type_menu.set(mode)
            except Exception:
                pass
        self._apply_route_mode_ui()
        if hasattr(self, "detail_table"):
            self.after_idle(self._update_detail_editor_state)
    def _on_route_type_var_write(self, *_args):
        if any(
            hasattr(self, attr)
            for attr in ("score_settings_row", "route_limit_entry", "route_type_switch", "route_type_menu")
        ):
            self.after_idle(self._apply_route_mode_ui)
    def _on_route_type_change(self, choice: str):
        self._on_race_type_change(choice)
    def _apply_route_mode_ui(self):
        mode = (self.route_type_var.get().strip() or "STANDARD").upper()
        if mode not in {"STANDARD", "SCORE"}:
            mode = "STANDARD"
            self.route_type_var.set(mode)
        is_score = mode == "SCORE"

        if hasattr(self, "route_type_switch"):
            try:
                if self.route_type_switch.get() != mode:
                    self.route_type_switch.set(mode)
            except Exception:
                pass
        if hasattr(self, "route_type_menu"):
            try:
                if self.route_type_menu.get() != mode:
                    self.route_type_menu.set(mode)
            except Exception:
                pass

        if is_score:
            if hasattr(self, "score_settings_row") and not self.score_settings_row.winfo_manager():
                self.score_settings_row.pack(fill="x", pady=(0, 10), after=self.mode_row)
            self.route_mode_hint_var.set("SCORE 模式会显示时限和超时扣分，并允许给右侧检查点设置分值。")
        else:
            if hasattr(self, "score_settings_row"):
                self.score_settings_row.pack_forget()
            self.route_limit_var.set("")
            self.route_penalty_var.set("")
            self.route_mode_hint_var.set("STANDARD 模式只看检查点顺序，右侧拖动排序即可。")
        self._update_detail_editor_state()
        if hasattr(self, "route_limit_entry"):
            self.route_limit_entry.configure(state="normal" if is_score else "disabled")
        if hasattr(self, "route_penalty_entry"):
            self.route_penalty_entry.configure(state="normal" if is_score else "disabled")
        if is_score and hasattr(self, "route_limit_entry"):
            self.after_idle(self.route_limit_entry.focus_set)
        self.update_idletasks()
    def export_route_template(self):
        self._export_template("路线模板", "RouteTemplate", ["RouteID", "RouteName", "Mode(STANDARD/SCORE)", "TimeLimitMin", "PenaltyPerMin"])
