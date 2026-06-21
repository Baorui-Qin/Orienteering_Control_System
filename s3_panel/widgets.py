"""通用 UI 控件与表格行为辅助。"""

import re
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk


class WidgetsMixin:
    def _create_form_row(
        self,
        parent_frame,
        label_text: str,
        placeholder: str,
        row_idx: int,
        width: int = 200,
        textvariable=None,
    ):
        lbl = ctk.CTkLabel(parent_frame, text=label_text, text_color="#1d1d1f", font=ctk.CTkFont(size=13, weight="bold"))
        lbl.grid(row=row_idx, column=0, sticky="e", padx=(12, 6), pady=7)
        entry = ctk.CTkEntry(parent_frame, placeholder_text=placeholder, width=width, height=34, textvariable=textvariable)
        entry.grid(row=row_idx, column=1, sticky="w", padx=(6, 12), pady=7)
        return entry
    def _normalize_checkpoint_mac_var(self, *_):
        self._normalize_hex_var(self.cp_mac_var)
    def _normalize_detail_cp_mac_var(self, *_):
        self._normalize_hex_var(self.detail_cp_mac_var)
    def _normalize_hex_var(self, string_var):
        if self._normalizing_vars:
            return
        current = string_var.get()
        normalized = re.sub(r"[^0-9A-Fa-f]", "", current).upper()
        if current == normalized:
            return
        self._normalizing_vars = True
        try:
            string_var.set(normalized)
        finally:
            self._normalizing_vars = False

    @staticmethod
    def _find_option_label(option_map: dict, raw_value: str):
        target = str(raw_value)
        for label, value in option_map.items():
            if str(value) == target:
                return label
        return ""

    @staticmethod
    def _select_tree_item_by_value(tree, value, column_index: int = 0):
        target = str(value)
        for item_id in tree.get_children():
            values = tree.item(item_id).get("values") or []
            if column_index < len(values) and str(values[column_index]) == target:
                tree.selection_set(item_id)
                tree.focus(item_id)
                tree.see(item_id)
                return item_id
        return None
    def _update_detail_editor_state(self):
        mode = (self.route_type_var.get().strip() or "STANDARD").upper()
        is_score = mode == "SCORE"
        if hasattr(self, "detail_score_entry"):
            self.detail_score_entry.configure(state="normal" if is_score else "disabled")
        if not is_score:
            self.detail_score_var.set("")
    @staticmethod
    def _checkpoint_role_text(checkpoint: dict):
        role_parts = []
        if checkpoint.get("is_start"):
            role_parts.append("起点")
        if checkpoint.get("is_finish"):
            role_parts.append("终点")
        return "/".join(role_parts) if role_parts else "普通点"
    def _card(self, master, title: str):
        frame = ctk.CTkFrame(master, fg_color="#ffffff", corner_radius=12, border_width=0)
        frame.pack(fill="x", padx=14, pady=8)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=15, weight="bold"), text_color="#1d1d1f").pack(
            anchor="w", padx=14, pady=(12, 8)
        )
        return frame
    def _build_config_page_header(self, parent, step_no: int, title: str, subtitle: str):
        header = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=10, border_width=0)
        header.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            header,
            text=f"步骤 {step_no}/4 · {title}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1d1d1f",
        ).pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(
            header,
            text=subtitle,
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

    @staticmethod
    def _build_rule_hint(parent, text: str):
        hint = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0, border_width=0)
        hint.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(
            hint,
            text=text,
            text_color="#86868b",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
            wraplength=900,
        ).pack(anchor="w", padx=0, pady=4)
    def _build_conn_card(self):
        card = self._card(self.sidebar, "串口连接中心")

        self.port_combo = ctk.CTkComboBox(card, variable=self.port_var, values=[""], width=190)
        self.port_combo.pack(padx=12, pady=4, anchor="w")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(padx=12, pady=4, anchor="w")
        ctk.CTkLabel(row, text="Baud", text_color="#86868b").pack(side="left", padx=(0, 6))
        ctk.CTkEntry(row, textvariable=self.baud_var, width=120).pack(side="left")

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(padx=12, pady=6, fill="x")
        ctk.CTkButton(btn_row, text="刷新", width=70, fg_color="#409eff", hover_color="#337ecc", command=self.refresh_ports).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btn_row, text="连接读卡器", width=90, fg_color="#2b8a3e", hover_color="#237032", command=self.connect_serial).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(btn_row, text="断开连接", width=90, fg_color="#c92a2a", hover_color="#a61e1e", command=self.disconnect_serial).pack(
            side="left"
        )

        ctk.CTkLabel(card, textvariable=self.conn_state, text_color="#86868b").pack(anchor="w", padx=12, pady=(2, 10))
    def _build_wifi_card(self):
        card = self._card(self.sidebar, "动态网络配置")
        ctk.CTkLabel(card, text="WiFi 名称 (SSID)", text_color="#1d1d1f").pack(anchor="w", padx=12, pady=(2, 0))
        ctk.CTkEntry(card, textvariable=self.ssid_var, placeholder_text="在此输入 WiFi 名称").pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(card, text="WiFi 密码", text_color="#1d1d1f").pack(anchor="w", padx=12, pady=(2, 0))
        ctk.CTkEntry(card, textvariable=self.pwd_var, placeholder_text="在此输入 WiFi 密码", show="*").pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(card, text="上面第一行填名称，第二行填密码。", text_color="#86868b").pack(anchor="w", padx=12, pady=(0, 4))
        ctk.CTkButton(card, text="下发网络配置", fg_color="#409eff", hover_color="#337ecc", command=self.send_wifi_config).pack(
            fill="x", padx=12, pady=(6, 10)
        )
    def _build_card_ops(self):
        card = self._card(self.sidebar, "发放管理员卡")
        ctk.CTkButton(card, text="制作校时卡 ", fg_color="#409eff", hover_color="#337ecc", command=lambda: self.send_cmd("CMD:MAKE_SYNC")).pack(
            fill="x", padx=12, pady=4
        )
        ctk.CTkButton(card, text="制作汇报卡 ", fg_color="#409eff", hover_color="#337ecc", command=lambda: self.send_cmd("CMD:MAKE_REPORT")).pack(
            fill="x", padx=12, pady=4
        )
        ctk.CTkButton(card, text="恢复网关监听", fg_color="#409eff", hover_color="#337ecc", command=lambda: self.send_cmd("CMD:RESET_MODE")).pack(
            fill="x", padx=12, pady=(4, 10)
        )
    def _build_write_card(self):
        card = self._card(self.sidebar, "制卡功能")
        ops = [
            ("制作普通人员卡", "CMD:MAKE_NORMAL", "普通人员卡"),
            ("制作起点配置卡", "CMD:MAKE_START", "起点配置卡"),
            ("制作途经配置卡", "CMD:MAKE_MID", "途经配置卡"),
            ("制作终点配置卡", "CMD:MAKE_END", "终点配置卡"),
            ("制作清除卡", "CMD:MAKE_CLEAR", "清除卡"),
        ]

        for text, cmd, label in ops:
            ctk.CTkButton(
                card,
                text=text,
                fg_color="#409eff",
                hover_color="#337ecc",
                command=lambda c=cmd, l=label: self.send_make_card_cmd(c, l),
            ).pack(fill="x", padx=12, pady=4)

        ctk.CTkLabel(card, textvariable=self.write_state, text_color="#86868b", wraplength=260, justify="left").pack(
            anchor="w", padx=12, pady=(4, 10)
        )

        ctk.CTkLabel(card, text="最近写卡记录", text_color="#1d1d1f").pack(anchor="w", padx=12, pady=(0, 4))
        self.write_history_box = ctk.CTkTextbox(
            card,
            height=108,
            fg_color="#f5f9ff",
            text_color="#1d1d1f",
            border_width=1,
            font=("Consolas", 12),
        )
        self.write_history_box.pack(fill="x", padx=12, pady=(0, 10))
        self.write_history_box.insert(tk.END, "暂无记录\n")
        self.write_history_box.configure(state="disabled")
    def _build_custom_cmd(self):
        card = self._card(self.sidebar, "自定义命令")
        ctk.CTkEntry(card, textvariable=self.custom_var, placeholder_text="CMD:...").pack(fill="x", padx=12, pady=4)
        ctk.CTkButton(card, text="发送命令", fg_color="#409eff", hover_color="#337ecc", command=self.send_custom).pack(fill="x", padx=12, pady=(4, 10))
    def _build_status_chip(self, parent, column: int, title: str, variable):
        chip = ctk.CTkFrame(parent, fg_color="#f5f9ff", corner_radius=10, border_width=0)
        chip.grid(row=0, column=column, sticky="ew", padx=8, pady=8)
        ctk.CTkLabel(chip, text=title, text_color="#86868b", font=ctk.CTkFont(size=11, weight="bold")).pack(
            anchor="w", padx=10, pady=(8, 2)
        )
        ctk.CTkLabel(chip, textvariable=variable, text_color="#1d1d1f", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", padx=10, pady=(0, 8)
        )
    def _add_pack_toolbar(self, host, before_widget, search_var, placeholder: str, on_search, buttons: list):
        bar = ctk.CTkFrame(host, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=(6, 0), before=before_widget)
        entry = ctk.CTkEntry(bar, textvariable=search_var, placeholder_text=placeholder, width=280)
        entry.pack(side="left", padx=(0, 8))
        entry.bind("<KeyRelease>", lambda _event: on_search())
        ctk.CTkButton(bar, text="清空搜索", width=88, fg_color="transparent", hover_color="#f5f5f7", text_color="#409eff", command=lambda: self._clear_search(search_var, on_search)).pack(
            side="left", padx=(0, 8)
        )
        for text, command, style in buttons:
            kwargs = {"width": 96}
            if style == "danger":
                kwargs.update({"fg_color": "#c92a2a", "hover_color": "#a61e1e"})
            else:
                kwargs.update({"fg_color": "transparent", "hover_color": "#f5f5f7", "text_color": "#409eff"})
            ctk.CTkButton(bar, text=text, command=command, **kwargs).pack(side="right", padx=(8, 0))
    def _add_grid_toolbar(self, host, row: int, search_var, placeholder: str, on_search, buttons: list):
        host.grid_rowconfigure(row + 1, weight=1)
        if host == self.detail_table.master:
            self.detail_table.grid(row=row + 1, column=0, sticky="nsew", padx=10, pady=10)
        elif host == self.monitor_table.master:
            self.monitor_table.grid(row=row + 1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        elif host == self.table.master:
            self.table.grid(row=row + 1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        bar = ctk.CTkFrame(host, fg_color="transparent")
        bar.grid(row=row, column=0, sticky="ew", padx=10 if host == self.detail_table.master else 12, pady=(0, 6))
        bar.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(bar, textvariable=search_var, placeholder_text=placeholder)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<KeyRelease>", lambda _event: on_search())
        ctk.CTkButton(bar, text="清空搜索", width=88, fg_color="transparent", hover_color="#f5f5f7", text_color="#409eff", command=lambda: self._clear_search(search_var, on_search)).grid(
            row=0, column=1, padx=(0, 8)
        )
        base_col = 2
        for idx, (text, command, style) in enumerate(buttons):
            kwargs = {"width": 96}
            if style == "danger":
                kwargs.update({"fg_color": "#c92a2a", "hover_color": "#a61e1e"})
            else:
                kwargs.update({"fg_color": "transparent", "hover_color": "#f5f5f7", "text_color": "#409eff"})
            ctk.CTkButton(bar, text=text, command=command, **kwargs).grid(row=0, column=base_col + idx, padx=(8, 0))
    def _clear_search(self, variable, on_search):
        variable.set("")
        on_search()
    def _configure_sortable_tree(self, tree, numeric_columns=None):
        numeric_columns = set(numeric_columns or set())
        tree_id = str(tree)
        self._tree_sort_state.setdefault(tree_id, {"column": None, "reverse": False, "numeric": numeric_columns})
        for column in tree["columns"]:
            tree.heading(column, command=lambda c=column, t=tree: self._sort_treeview(t, c))
    def _reapply_tree_sort(self, tree):
        state = self._tree_sort_state.get(str(tree))
        if not state or not state.get("column"):
            return
        self._sort_treeview(tree, state["column"], toggle=False)
    def _row_matches_query(self, values: list, query: str):
        if not query:
            return True
        text = " ".join("" if value is None else str(value) for value in values).lower()
        return query in text
    def _setup_treeview_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            style.theme_use("default")

        style.configure(
            "Dark.Treeview",
            background="#f8fbff",
            foreground="#14293D",
            fieldbackground="#f8fbff",
            rowheight=40,
            borderwidth=0,
            relief="flat",
            font=("Microsoft YaHei UI", 10),
        )
        style.map(
            "Dark.Treeview",
            background=[("selected", "#409eff")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#ecf5ff",
            foreground="#2b6cb0",
            font=("Microsoft YaHei UI", 10, "bold"),
            borderwidth=0,
            relief="flat",
            padding=(14, 10),
        )
        style.map(
            "Dark.Treeview.Heading",
            background=[("active", "#d9ecff")],
            foreground=[("active", "#1f5c99")],
        )
    def _grid_entry_field(self, parent, row: int, column: int, label: str, variable, placeholder: str):
        ctk.CTkLabel(parent, text=label, text_color="#86868b").grid(row=row, column=column, sticky="w", pady=(0 if row == 0 else 10, 4), padx=(0, 8))
        entry = ctk.CTkEntry(parent, textvariable=variable, placeholder_text=placeholder, fg_color="#f5f5f7", border_width=0, height=38, corner_radius=12)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(0, 16), pady=(0 if row == 0 else 10, 4))
        return entry
    def _make_soft_card(self, parent, title: str, subtitle: str | None = None, padding=(25, 25)):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=0)
        shell = ctk.CTkFrame(card, fg_color="transparent", border_width=0)
        shell.pack(fill="both", expand=True, padx=padding[0], pady=padding[1])
        ctk.CTkLabel(
            shell,
            text=title,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=20, weight="bold"),
            text_color="#409eff",
            anchor="w",
        ).pack(fill="x", anchor="w")
        if subtitle:
            ctk.CTkLabel(
                shell,
                text=subtitle,
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
                text_color="#64748B",
                anchor="w",
                justify="left",
            ).pack(fill="x", anchor="w", pady=(4, 0))
        inner = ctk.CTkFrame(shell, fg_color="transparent", border_width=0)
        inner.pack(fill="both", expand=True, pady=(0, 0))
        return card, inner
    def _pack_entry_row(self, parent, label: str, variable, placeholder: str, pady=(0, 12)):
        row = ctk.CTkFrame(parent, fg_color="transparent", border_width=0)
        row.pack(fill="x", pady=pady)
        ctk.CTkLabel(
            row,
            text=label,
            width=100,
            anchor="e",
            text_color="#64748B",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"),
        ).pack(side="left", padx=(0, 14))
        entry = ctk.CTkEntry(
            row,
            textvariable=variable,
            placeholder_text=placeholder,
            fg_color="#F8FAFC",
            border_width=0,
            height=40,
            corner_radius=12,
        )
        entry.pack(side="left", fill="x", expand=True)
        return entry
    def _build_table_stat_chip(self, parent, column: int, title: str, variable, accent: str):
        chip = ctk.CTkFrame(parent, fg_color="#f5f9ff", corner_radius=16, border_width=0)
        chip.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        ctk.CTkLabel(
            chip,
            text=title,
            text_color="#64748B",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=11, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            chip,
            textvariable=variable,
            text_color=accent,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=18, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(0, 12))
    def _make_table_section(self, parent, title: str, subtitle: str, empty_text: str):
        section = ctk.CTkFrame(parent, fg_color="#f5f9ff", corner_radius=18, border_width=1, border_color="#e6f1fc")
        ctk.CTkLabel(
            section,
            text=title,
            text_color="#1f5c99",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=15, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            section,
            text=subtitle,
            text_color="#64748B",
            justify="left",
            wraplength=860,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        ).pack(fill="x", padx=18)

        content = ctk.CTkFrame(section, fg_color="transparent", border_width=0)
        content.pack(fill="both", expand=True, padx=18, pady=(14, 18))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(content, fg_color="transparent", border_width=0)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        table_shell = ctk.CTkFrame(content, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#ecf5ff")
        table_shell.grid(row=1, column=0, sticky="nsew")
        table_shell.grid_columnconfigure(0, weight=1)
        table_shell.grid_rowconfigure(0, weight=1)

        empty_label = ctk.CTkLabel(
            table_shell,
            text=empty_text,
            text_color="#94A3B8",
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
        )
        return section, toolbar, table_shell, empty_label
    def _mount_treeview(self, tree, table_shell, empty_label):
        tree.grid(row=0, column=0, sticky="nsew", padx=(14, 0), pady=(14, 0))
        y_scroll = ctk.CTkScrollbar(
            table_shell,
            orientation="vertical",
            command=tree.yview,
            fg_color="#f0f7ff",
            button_color="#a3cfff",
            button_hover_color="#79b8ff",
            corner_radius=999,
            width=12,
        )
        y_scroll.grid(row=0, column=1, sticky="ns", padx=(10, 12), pady=(14, 0))
        x_scroll = ctk.CTkScrollbar(
            table_shell,
            orientation="horizontal",
            command=tree.xview,
            fg_color="#f0f7ff",
            button_color="#a3cfff",
            button_hover_color="#79b8ff",
            corner_radius=999,
            height=12,
        )
        x_scroll.grid(row=1, column=0, sticky="ew", padx=(14, 0), pady=(10, 12))
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self._update_table_empty_state(tree, empty_label)
    def _update_table_empty_state(self, tree, empty_label):
        if tree is None or empty_label is None:
            return
        if tree.get_children():
            empty_label.place_forget()
        else:
            empty_label.place(relx=0.5, rely=0.56, anchor="center")
            empty_label.lift()
    def _configure_tree_tags(self, tree):
        tree.tag_configure("oddrow", background="#f8fbff")
        tree.tag_configure("evenrow", background="#f5f9ff")
        tree.tag_configure("missing", background="#FFF4D6", foreground="#8A4B08")
    def _restripe_tree(self, tree):
        for index, item_id in enumerate(tree.get_children()):
            tags = [tag for tag in tree.item(item_id, "tags") if tag not in {"oddrow", "evenrow"}]
            tags.insert(0, "evenrow" if index % 2 == 0 else "oddrow")
            tree.item(item_id, tags=tuple(tags))
    def _sort_treeview(self, tree, column: str, toggle: bool = True):
        tree_id = str(tree)
        state = self._tree_sort_state.setdefault(tree_id, {"column": None, "reverse": False, "numeric": set()})
        reverse = False
        if toggle and state["column"] == column:
            reverse = not state["reverse"]
        elif not toggle:
            reverse = state["reverse"]
        numeric_columns = state.get("numeric", set())

        def sort_key(item_id):
            value = tree.set(item_id, column)
            if column in numeric_columns:
                try:
                    return (0, float(value))
                except (TypeError, ValueError):
                    return (1, float("inf"))
            return (0, value.lower() if isinstance(value, str) else str(value).lower())

        items = list(tree.get_children(""))
        items.sort(key=sort_key, reverse=reverse)
        for index, item_id in enumerate(items):
            tree.move(item_id, "", index)
        state["column"] = column
        state["reverse"] = reverse
        self._restripe_tree(tree)
    def _build_search_bar(self, parent, variable, placeholder: str, on_search, row: int, trailing_buttons=None):
        trailing_buttons = trailing_buttons or []
        bar = ctk.CTkFrame(parent, fg_color="#f0f7ff", corner_radius=16, border_width=0)
        bar.grid(row=row, column=0, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(
            bar,
            textvariable=variable,
            placeholder_text=placeholder,
            fg_color="#FFFFFF",
            border_width=0,
            height=40,
            corner_radius=14,
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(10, 8), pady=10)
        entry.bind("<KeyRelease>", lambda _event: on_search())
        ctk.CTkButton(
            bar,
            text="清空",
            width=72,
            height=40,
            corner_radius=14,
            fg_color="#FFFFFF",
            hover_color="#F8FAFC",
            text_color="#409eff",
            command=lambda: self._clear_search(variable, on_search),
        ).grid(row=0, column=1, padx=(0, 8), pady=10)
        for idx, (text, command, style) in enumerate(trailing_buttons, start=2):
            kwargs = {"text": text, "command": command, "width": 100, "height": 40, "corner_radius": 14}
            if style == "danger":
                kwargs.update({"fg_color": "#EF4444", "hover_color": "#DC2626", "text_color": "#FFFFFF"})
            else:
                kwargs.update({"fg_color": "#ecf5ff", "hover_color": "#d9ecff", "text_color": "#409eff"})
            ctk.CTkButton(bar, **kwargs).grid(row=0, column=idx, padx=(8, 10 if idx == len(trailing_buttons) + 1 else 0), pady=10)
        return bar
    def _install_modern_tree_behaviors(self):
        trees = [
            getattr(self, "runner_table", None),
            getattr(self, "cp_table", None),
            getattr(self, "route_table", None),
            getattr(self, "available_cp_table", None),
            getattr(self, "detail_table", None),
            getattr(self, "monitor_table", None),
        ]
        for tree in trees:
            if tree is not None:
                self._configure_tree_tags(tree)

        if hasattr(self, "runner_table"):
            self.runner_table.configure(selectmode="extended")
            self._configure_sortable_tree(self.runner_table, numeric_columns={"route"})
        if hasattr(self, "cp_table"):
            self.cp_table.configure(selectmode="extended")
            self._configure_sortable_tree(self.cp_table)
        if hasattr(self, "route_table"):
            self.route_table.configure(selectmode="extended")
            self._configure_sortable_tree(self.route_table, numeric_columns={"route_id", "limit", "penalty"})
        if hasattr(self, "available_cp_table"):
            self.available_cp_table.configure(selectmode="browse")
            self._configure_sortable_tree(self.available_cp_table)
        if hasattr(self, "detail_table"):
            self.detail_table.configure(selectmode="extended")
            self._configure_sortable_tree(self.detail_table, numeric_columns={"index", "score"})
        if hasattr(self, "monitor_table"):
            self.monitor_table.configure(selectmode="browse")
            self._configure_sortable_tree(self.monitor_table)
