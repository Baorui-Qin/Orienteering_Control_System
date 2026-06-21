"""赛前准备：单位、组别与通道管理。"""

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from calculation import generate_start_list

from .theme import FONT_FAMILY, PALETTE

GROUP_START_MODES = ["个人计时", "统一出发", "追逐赛"]


class OrgPageMixin:
    # ------------------------------------------------------------------
    # 单位
    # ------------------------------------------------------------------
    def _build_units_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        card, inner = self._make_soft_card(parent, "单位管理", "录入参赛单位；删除单位会自动解除选手关联。")
        card.grid(row=0, column=0, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(inner, fg_color="transparent", border_width=0)
        form.grid(row=0, column=0, sticky="ew", pady=(12, 12))
        form.grid_columnconfigure(1, weight=1)
        self._grid_entry_field(form, 0, 0, "单位名称", self.unit_name_var, "如 北京队")
        actions = ctk.CTkFrame(form, fg_color="transparent", border_width=0)
        actions.grid(row=0, column=2, padx=(18, 0))
        ctk.CTkButton(actions, text="保存单位", width=110, height=38, corner_radius=10, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.save_unit).pack(side="left")
        ctk.CTkButton(actions, text="清空", width=80, height=38, corner_radius=10, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.clear_unit_form).pack(side="left", padx=8)

        section, toolbar, shell, self.unit_empty_label = self._make_table_section(inner, "单位列表", "按单位统计选手数。", "当前还没有单位")
        section.grid(row=1, column=0, sticky="nsew")
        self._build_search_bar(toolbar, self.unit_search_var, "搜索单位名称", self.refresh_units, row=0, trailing_buttons=[("删除所选", self.delete_selected_unit, "danger")])
        self.unit_table = ttk.Treeview(shell, columns=("name", "count"), show="headings", style="Dark.Treeview", height=12)
        self.unit_table.heading("name", text="单位名称")
        self.unit_table.heading("count", text="运动员数")
        self.unit_table.column("name", width=280, anchor="w")
        self.unit_table.column("count", width=120, anchor="center")
        self.unit_table.bind("<<TreeviewSelect>>", self._on_unit_select)
        self._mount_treeview(self.unit_table, shell, self.unit_empty_label)
        self.refresh_units()

    def clear_unit_form(self):
        self._selected_unit_id = None
        self.unit_name_var.set("")
        if hasattr(self, "unit_table"):
            self.unit_table.selection_remove(self.unit_table.selection())

    def _on_unit_select(self, _event=None):
        sel = self.unit_table.selection()
        if not sel:
            return
        self._selected_unit_id = int(sel[0])
        values = self.unit_table.item(sel[0]).get("values") or []
        if values:
            self.unit_name_var.set(str(values[0]))

    def save_unit(self):
        name = self.unit_name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "单位名称不能为空")
            return
        self.store.upsert_unit(name, unit_id=self._selected_unit_id)
        self.clear_unit_form()
        self.refresh_units()
        self._refresh_runner_org_options()

    def delete_selected_unit(self):
        sel = self.unit_table.selection() if hasattr(self, "unit_table") else ()
        if not sel:
            messagebox.showwarning("提示", "请先选择一个单位")
            return
        self.store.delete_unit(int(sel[0]))
        self.clear_unit_form()
        self.refresh_units()
        self._refresh_runner_org_options()

    def refresh_units(self):
        if not hasattr(self, "unit_table"):
            return
        query = self.unit_search_var.get().strip().lower()
        counts = self.store.count_runners_by_unit()
        for item in self.unit_table.get_children():
            self.unit_table.delete(item)
        for u in self.store.list_units():
            if query and query not in (u["name"] or "").lower():
                continue
            self.unit_table.insert("", tk.END, iid=str(u["unit_id"]), values=(u["name"], counts.get(u["unit_id"], 0)))

    # ------------------------------------------------------------------
    # 组别 & 通道
    # ------------------------------------------------------------------
    def _build_groups_page(self, parent):
        page = ctk.CTkScrollableFrame(parent, fg_color=PALETTE["content_bg"], corner_radius=0, border_width=0)
        page.pack(fill="both", expand=True)

        # 组别
        gcard, ginner = self._make_soft_card(page, "组别列表", "组别可关联路线、限时、起点模式与通道。")
        gcard.pack(fill="x", padx=4, pady=(0, 16))
        gform = ctk.CTkFrame(ginner, fg_color="transparent", border_width=0)
        gform.pack(fill="x", pady=(12, 12))
        gform.grid_columnconfigure((1, 3), weight=1)
        self._grid_entry_field(gform, 0, 0, "组别名称", self.group_name_var, "如 男子精英组")
        self.group_route_combo = self._org_combo(gform, 0, 3, self.group_route_var)
        ctk.CTkLabel(gform, text="路线", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(row=0, column=2, sticky="w", padx=(12, 8), pady=6)
        self._grid_entry_field(gform, 1, 0, "限时(分钟)", self.group_limit_var, "可空")
        ctk.CTkLabel(gform, text="起点模式", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(row=1, column=2, sticky="w", padx=(12, 8), pady=6)
        ctk.CTkComboBox(gform, variable=self.group_mode_var, values=GROUP_START_MODES, height=36, corner_radius=8, fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"], button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"]).grid(row=1, column=3, sticky="ew", padx=(0, 8), pady=6)
        ctk.CTkLabel(gform, text="通道", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=6)
        self.group_channel_combo = self._org_combo(gform, 2, 1, self.group_channel_var)
        gactions = ctk.CTkFrame(gform, fg_color="transparent", border_width=0)
        gactions.grid(row=2, column=2, columnspan=2, sticky="e", pady=6)
        ctk.CTkButton(gactions, text="保存组别", width=110, height=36, corner_radius=10, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.save_group).pack(side="left")
        ctk.CTkButton(gactions, text="清空", width=80, height=36, corner_radius=10, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.clear_group_form).pack(side="left", padx=8)

        gsection, gtoolbar, gshell, self.group_empty_label = self._make_table_section(ginner, "组别", "选中可编辑；删除会解除选手关联。", "当前还没有组别")
        gsection.pack(fill="both", expand=True, pady=(8, 0))
        self._build_search_bar(gtoolbar, self.group_search_var, "搜索组别名称", self.refresh_groups, row=0, trailing_buttons=[("删除所选", self.delete_selected_group, "danger")])
        self.group_table = ttk.Treeview(gshell, columns=("name", "route", "limit", "mode", "channel"), show="headings", style="Dark.Treeview", height=8)
        for c, t, w in (("name", "名称", 180), ("route", "路线", 140), ("limit", "限时(分)", 90), ("mode", "起点模式", 120), ("channel", "通道", 140)):
            self.group_table.heading(c, text=t)
            self.group_table.column(c, width=w, anchor="w" if c in ("name", "route", "channel") else "center")
        self.group_table.bind("<<TreeviewSelect>>", self._on_group_select)
        self._mount_treeview(self.group_table, gshell, self.group_empty_label)

        # 通道
        ccard, cinner = self._make_soft_card(page, "通道列表", "通道决定出发首发时间、间隔与空位。")
        ccard.pack(fill="x", padx=4, pady=(0, 16))
        cform = ctk.CTkFrame(cinner, fg_color="transparent", border_width=0)
        cform.pack(fill="x", pady=(12, 12))
        cform.grid_columnconfigure((1, 3), weight=1)
        self._grid_entry_field(cform, 0, 0, "通道名称", self.channel_name_var, "如 通道A")
        self._grid_entry_field(cform, 0, 2, "首发时间", self.channel_first_var, "YYYY-MM-DD HH:MM:SS")
        self._grid_entry_field(cform, 1, 0, "出发间隔(秒)", self.channel_interval_var, "如 60")
        self._grid_entry_field(cform, 1, 2, "空位数量", self.channel_slots_var, "默认 0")
        cactions = ctk.CTkFrame(cform, fg_color="transparent", border_width=0)
        cactions.grid(row=0, column=4, rowspan=2, padx=(18, 0))
        ctk.CTkButton(cactions, text="保存通道", width=110, height=36, corner_radius=10, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.save_channel).pack(fill="x", pady=(0, 8))
        ctk.CTkButton(cactions, text="清空", width=110, height=36, corner_radius=10, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=self.clear_channel_form).pack(fill="x")

        csection, ctoolbar, cshell, self.channel_empty_label = self._make_table_section(cinner, "通道", "选中可编辑。", "当前还没有通道")
        csection.pack(fill="both", expand=True, pady=(8, 0))
        ctk.CTkLabel(ctoolbar, text="", fg_color="transparent").grid(row=0, column=0)
        self.channel_table = ttk.Treeview(cshell, columns=("name", "first", "interval", "slots"), show="headings", style="Dark.Treeview", height=6)
        for c, t, w in (("name", "名称", 180), ("first", "首发时间", 200), ("interval", "出发间隔(秒)", 130), ("slots", "空位数量", 110)):
            self.channel_table.heading(c, text=t)
            self.channel_table.column(c, width=w, anchor="w" if c in ("name", "first") else "center")
        self.channel_table.bind("<<TreeviewSelect>>", self._on_channel_select)
        self._mount_treeview(self.channel_table, cshell, self.channel_empty_label)

        self.refresh_channels()
        self.refresh_groups()

    def _org_combo(self, parent, row, col, variable):
        combo = ctk.CTkComboBox(parent, variable=variable, values=["（无）"], height=36, corner_radius=8, fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"], button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"], dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"])
        combo.grid(row=row, column=col, sticky="ew", padx=(0, 8), pady=6)
        return combo

    # ---- 组别逻辑 ----
    def clear_group_form(self):
        self._selected_group_id = None
        self.group_name_var.set("")
        self.group_route_var.set("（无）")
        self.group_limit_var.set("")
        self.group_mode_var.set(GROUP_START_MODES[0])
        self.group_channel_var.set("（无）")
        if hasattr(self, "group_table"):
            self.group_table.selection_remove(self.group_table.selection())

    def _on_group_select(self, _event=None):
        sel = self.group_table.selection()
        if not sel:
            return
        g = self.store.get_group(int(sel[0]))
        if not g:
            return
        self._selected_group_id = g["group_id"]
        self.group_name_var.set(g["name"] or "")
        self.group_route_var.set(self._label_for_id(self.group_route_option_map, g["route_id"]))
        self.group_limit_var.set("" if g["limit_min"] is None else str(g["limit_min"]))
        self.group_mode_var.set(g["start_mode"] or GROUP_START_MODES[0])
        self.group_channel_var.set(self._label_for_id(self.group_channel_option_map, g["channel_id"]))

    def save_group(self):
        name = self.group_name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "组别名称不能为空")
            return
        try:
            limit = int(self.group_limit_var.get().strip()) if self.group_limit_var.get().strip() else None
        except ValueError:
            messagebox.showwarning("提示", "限时必须是整数分钟")
            return
        route_id = self.group_route_option_map.get(self.group_route_var.get())
        channel_id = self.group_channel_option_map.get(self.group_channel_var.get())
        self.store.upsert_group(name, route_id=route_id, limit_min=limit, start_mode=self.group_mode_var.get(), channel_id=channel_id, group_id=self._selected_group_id)
        self.clear_group_form()
        self.refresh_groups()
        self._refresh_runner_org_options()

    def delete_selected_group(self):
        sel = self.group_table.selection() if hasattr(self, "group_table") else ()
        if not sel:
            messagebox.showwarning("提示", "请先选择一个组别")
            return
        self.store.delete_group(int(sel[0]))
        self.clear_group_form()
        self.refresh_groups()
        self._refresh_runner_org_options()

    def refresh_groups(self):
        if not hasattr(self, "group_table"):
            return
        self._refresh_org_option_maps()
        query = self.group_search_var.get().strip().lower()
        for item in self.group_table.get_children():
            self.group_table.delete(item)
        for g in self.store.list_groups():
            if query and query not in (g["name"] or "").lower():
                continue
            route_label = self._label_for_id(self.group_route_option_map, g["route_id"])
            channel_label = self._label_for_id(self.group_channel_option_map, g["channel_id"])
            self.group_table.insert("", tk.END, iid=str(g["group_id"]), values=(
                g["name"], "" if route_label == "（无）" else route_label,
                "" if g["limit_min"] is None else g["limit_min"], g["start_mode"] or "",
                "" if channel_label == "（无）" else channel_label,
            ))

    # ---- 通道逻辑 ----
    def clear_channel_form(self):
        self._selected_channel_id = None
        self.channel_name_var.set("")
        self.channel_first_var.set("")
        self.channel_interval_var.set("")
        self.channel_slots_var.set("")
        if hasattr(self, "channel_table"):
            self.channel_table.selection_remove(self.channel_table.selection())

    def _on_channel_select(self, _event=None):
        sel = self.channel_table.selection()
        if not sel:
            return
        for ch in self.store.list_channels():
            if ch["channel_id"] == int(sel[0]):
                self._selected_channel_id = ch["channel_id"]
                self.channel_name_var.set(ch["name"] or "")
                self.channel_first_var.set(self._format_start_time(ch["first_start_time"]))
                self.channel_interval_var.set("" if ch["interval_sec"] is None else str(ch["interval_sec"]))
                self.channel_slots_var.set("" if ch["empty_slots"] is None else str(ch["empty_slots"]))
                break

    def save_channel(self):
        name = self.channel_name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "通道名称不能为空")
            return
        try:
            first = self._parse_start_time(self.channel_first_var.get())
        except ValueError:
            messagebox.showwarning("提示", "首发时间格式应为 YYYY-MM-DD HH:MM:SS 或留空")
            return
        try:
            interval = int(self.channel_interval_var.get().strip()) if self.channel_interval_var.get().strip() else None
            slots = int(self.channel_slots_var.get().strip()) if self.channel_slots_var.get().strip() else 0
        except ValueError:
            messagebox.showwarning("提示", "出发间隔与空位数量必须是整数")
            return
        self.store.upsert_channel(name, first, interval, slots, channel_id=self._selected_channel_id)
        self.clear_channel_form()
        self.refresh_channels()
        self.refresh_groups()

    def refresh_channels(self):
        if not hasattr(self, "channel_table"):
            return
        for item in self.channel_table.get_children():
            self.channel_table.delete(item)
        for ch in self.store.list_channels():
            self.channel_table.insert("", tk.END, iid=str(ch["channel_id"]), values=(
                ch["name"], self._format_start_time(ch["first_start_time"]),
                "" if ch["interval_sec"] is None else ch["interval_sec"],
                "" if ch["empty_slots"] is None else ch["empty_slots"],
            ))

    # ------------------------------------------------------------------
    # 选项映射 / 跨页刷新
    # ------------------------------------------------------------------
    @staticmethod
    def _label_for_id(option_map: dict, value):
        for label, val in option_map.items():
            if val == value:
                return label
        return "（无）"

    def _refresh_org_option_maps(self):
        self.group_route_option_map = {"（无）": None}
        for r in self.store.list_routes():
            self.group_route_option_map[f"{r['route_id']} {r.get('route_name') or ''}".strip()] = r["route_id"]
        self.group_channel_option_map = {"（无）": None}
        for ch in self.store.list_channels():
            self.group_channel_option_map[ch["name"]] = ch["channel_id"]
        if hasattr(self, "group_route_combo"):
            self.group_route_combo.configure(values=list(self.group_route_option_map))
        if hasattr(self, "group_channel_combo"):
            self.group_channel_combo.configure(values=list(self.group_channel_option_map))

    def _refresh_runner_org_options(self):
        self.runner_unit_option_map = {"（无）": None}
        for u in self.store.list_units():
            self.runner_unit_option_map[u["name"]] = u["unit_id"]
        self.runner_group_option_map = {"（无）": None}
        for g in self.store.list_groups():
            self.runner_group_option_map[g["name"]] = g["group_id"]
        if hasattr(self, "runner_unit_combo"):
            self.runner_unit_combo.configure(values=list(self.runner_unit_option_map))
        if hasattr(self, "runner_group_combo"):
            self.runner_group_combo.configure(values=list(self.runner_group_option_map))

    def _refresh_org_views(self):
        self.refresh_units()
        self.refresh_channels()
        self.refresh_groups()
        self._refresh_runner_org_options()
        self._refresh_start_channel_options()
        self.refresh_starttime()

    # ------------------------------------------------------------------
    # 出发时刻 / 发车表
    # ------------------------------------------------------------------
    def _build_starttime_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        card, inner = self._make_soft_card(parent, "出发时刻 / 发车表", "按通道生成出发批次与时间；可选随机算法避免同单位相邻。")
        card.grid(row=0, column=0, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(2, weight=1)

        ctrl = ctk.CTkFrame(inner, fg_color="transparent", border_width=0)
        ctrl.grid(row=0, column=0, sticky="ew", pady=(12, 6))
        ctk.CTkLabel(ctrl, text="通道", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.start_channel_combo = ctk.CTkComboBox(ctrl, variable=self.start_channel_var, values=["（请选择通道）"], width=200, height=34, corner_radius=8, fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"], button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"], dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"])
        self.start_channel_combo.pack(side="left", padx=(0, 12))
        ctk.CTkButton(ctrl, text="导出出发时刻表", width=140, height=34, corner_radius=8, fg_color=PALETTE["success"], hover_color=PALETTE["success_hover"], command=self.export_start_list).pack(side="right")

        algo = ctk.CTkFrame(inner, fg_color="transparent", border_width=0)
        algo.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(algo, text="有条件随机算法：", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(algo, text="同批次同单位不相邻", height=34, corner_radius=8, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=lambda: self.generate_start_list_ui("unit_spread")).pack(side="left", padx=4)
        ctk.CTkButton(algo, text="同组别同单位不相邻", height=34, corner_radius=8, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=lambda: self.generate_start_list_ui("group_unit_spread")).pack(side="left", padx=4)
        ctk.CTkButton(algo, text="完全随机", height=34, corner_radius=8, fg_color=PALETTE["primary_soft"], hover_color=PALETTE["primary_soft_hover"], text_color=PALETTE["primary"], command=lambda: self.generate_start_list_ui("random")).pack(side="left", padx=4)

        shell = ctk.CTkFrame(inner, fg_color=PALETTE["card_bg"], corner_radius=10, border_width=1, border_color=PALETTE["border"])
        shell.grid(row=2, column=0, sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)
        self.starttime_table = ttk.Treeview(shell, columns=("bib", "name", "group", "unit", "channel", "batch", "time"), show="headings", style="Dark.Treeview", height=14)
        for c, t, w in (("bib", "参赛号", 90), ("name", "姓名", 130), ("group", "组别", 130), ("unit", "单位", 130), ("channel", "通道", 120), ("batch", "出发批次", 90), ("time", "出发时间", 180)):
            self.starttime_table.heading(c, text=t)
            self.starttime_table.column(c, width=w, anchor="w" if c in ("name", "group", "unit") else "center")
        self.starttime_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._refresh_start_channel_options()
        self.refresh_starttime()

    def _refresh_start_channel_options(self):
        self.start_channel_option_map = {}
        for ch in self.store.list_channels():
            self.start_channel_option_map[ch["name"]] = ch["channel_id"]
        labels = list(self.start_channel_option_map) or ["（请选择通道）"]
        if hasattr(self, "start_channel_combo"):
            self.start_channel_combo.configure(values=labels)
        if self.start_channel_var.get() not in self.start_channel_option_map and labels:
            self.start_channel_var.set(labels[0])

    def generate_start_list_ui(self, algorithm):
        channel_id = self.start_channel_option_map.get(self.start_channel_var.get())
        if channel_id is None:
            messagebox.showwarning("提示", "请先选择一个通道（在「组别 & 通道」页创建）")
            return
        channel = next((c for c in self.store.list_channels() if c["channel_id"] == channel_id), None)
        if not channel:
            return
        # 选取「组别关联到该通道」的选手；若没有匹配则用全部选手
        group_channel = {g["group_id"]: g["channel_id"] for g in self.store.list_groups()}
        all_runners = self.store.list_runners()
        runners = [r for r in all_runners if group_channel.get(r.get("group_id")) == channel_id]
        if not runners:
            runners = all_runners
        if not runners:
            messagebox.showwarning("提示", "当前赛事没有可排发车的选手")
            return
        assignments, warning = generate_start_list(runners, channel, algorithm)
        for a in assignments:
            self.store.set_runner_start(a["uid"], a["start_time"], a["batch"])
        self.refresh_starttime()
        self._refresh_leaderboard()
        msg = f"已为 {len(assignments)} 名选手生成发车时刻。"
        if warning:
            msg += "\n⚠ " + warning
        messagebox.showinfo("发车表", msg)

    def refresh_starttime(self):
        if not hasattr(self, "starttime_table"):
            return
        units = {u["unit_id"]: u["name"] for u in self.store.list_units()}
        groups = {g["group_id"]: g for g in self.store.list_groups()}
        channels = {c["channel_id"]: c["name"] for c in self.store.list_channels()}
        rows = [r for r in self.store.list_runners() if r.get("start_batch") is not None]
        rows.sort(key=lambda r: (r.get("start_batch") if r.get("start_batch") is not None else 0))
        for item in self.starttime_table.get_children():
            self.starttime_table.delete(item)
        for r in rows:
            g = groups.get(r.get("group_id")) or {}
            channel_name = channels.get(g.get("channel_id"), "")
            self.starttime_table.insert("", tk.END, values=(
                r.get("bib_number") or "-", r.get("name") or "-",
                g.get("name") or (r.get("category") or "-"),
                units.get(r.get("unit_id"), "-"), channel_name or "-",
                r.get("start_batch"), self._format_start_time(r.get("start_time")),
            ))

    def export_start_list(self):
        from tkinter import filedialog

        from openpyxl import Workbook

        rows = self.starttime_table.get_children() if hasattr(self, "starttime_table") else ()
        if not rows:
            messagebox.showwarning("提示", "没有可导出的发车数据")
            return
        out = filedialog.asksaveasfilename(title="导出出发时刻表", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if not out:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "StartList"
        ws.append(["参赛号", "姓名", "组别", "单位", "通道", "出发批次", "出发时间"])
        for iid in rows:
            ws.append(list(self.starttime_table.item(iid)["values"]))
        wb.save(out)
        messagebox.showinfo("导出完成", f"已导出到\n{out}")
