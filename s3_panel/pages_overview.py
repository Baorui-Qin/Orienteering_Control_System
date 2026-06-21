"""总览页：设备状态与实时排名展示。"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk

from .runtime import STATUS_COLORS


class OverviewPageMixin:
    def _build_device_monitor_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        ctk.CTkLabel(top, text="设备状态监控", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="刷新状态", width=100, fg_color="#409eff", hover_color="#337ecc", command=self._refresh_device_monitor).pack(side="right")

        self.monitor_table = ttk.Treeview(
            frame,
            columns=("cp_code", "mac", "role", "last_seen", "ntp", "battery", "ready"),
            show="headings",
            style="Dark.Treeview",
        )
        self.monitor_table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.monitor_table.heading("cp_code", text="点号")
        self.monitor_table.heading("mac", text="MAC")
        self.monitor_table.heading("role", text="角色")
        self.monitor_table.heading("last_seen", text="最近活动")
        self.monitor_table.heading("ntp", text="NTP")
        self.monitor_table.heading("battery", text="电量")
        self.monitor_table.heading("ready", text="就绪")
        self.monitor_table.column("cp_code", width=100, anchor="center")
        self.monitor_table.column("mac", width=180, anchor="center")
        self.monitor_table.column("role", width=120, anchor="center")
        self.monitor_table.column("last_seen", width=150, anchor="center")
        self.monitor_table.column("ntp", width=100, anchor="center")
        self.monitor_table.column("battery", width=80, anchor="center")
        self.monitor_table.column("ready", width=100, anchor="center")

        self._refresh_device_monitor()
    def _build_export_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        ctk.CTkButton(frame, text="导出成绩总榜", width=180, fg_color="#409eff", hover_color="#337ecc", command=self.export_results_excel).pack(anchor="w", padx=16, pady=(16, 10))
        ctk.CTkButton(frame, text="导出分段成绩", width=180, fg_color="#409eff", hover_color="#337ecc", command=self.export_split_excel).pack(anchor="w", padx=16, pady=(0, 10))
        ctk.CTkButton(frame, text="导出原始流水", width=180, fg_color="#409eff", hover_color="#337ecc", command=self.export_raw_excel).pack(anchor="w", padx=16, pady=(0, 10))
        ctk.CTkLabel(
            frame,
            text="总榜按当前规则排序；分段由 READOUT 原始 punches 自动重建。",
            text_color="#86868b",
        ).pack(anchor="w", padx=16, pady=(0, 16))
    def _build_dashboard(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=1)

        banner = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        banner.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 8))
        banner.grid_columnconfigure(0, weight=1)
        banner.grid_columnconfigure(1, weight=0)
        ctk.CTkCheckBox(
            banner,
            text="刷卡时弹窗",
            variable=self.readout_popup_enabled_var,
            text_color="#1d1d1f",
        ).grid(row=0, column=1, sticky="e", padx=12, pady=(10, 4))
        ctk.CTkLabel(
            banner,
            text="最新读卡播报",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        self.readout_banner = ctk.CTkLabel(
            banner,
            textvariable=self.readout_state,
            text_color="#409eff",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
            justify="left",
        )
        self.readout_banner.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="ew", padx=18, pady=(2, 8))
        for i in range(4):
            wrap.grid_columnconfigure(i, weight=1)

        self.hw_card = self._dash_card(wrap, 0, "S3 硬件状态", self.hw_state, "#86868b")
        self.wifi_card = self._dash_card(wrap, 1, "网关 Wi-Fi 状态", self.wifi_state, "#86868b")
        self.time_card = self._dash_card(wrap, 2, "S3 NTP 时间", self.ntp_state, "#86868b")
        self.readout_card = self._dash_card(wrap, 3, "最新清算播报", self.readout_state, "#86868b")
    def _dash_card(self, parent, col, title, var, color):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        card.grid(row=0, column=col, sticky="ew", padx=8)
        ctk.CTkLabel(card, text=title, text_color="#86868b").pack(anchor="w", padx=12, pady=(10, 6))
        label = ctk.CTkLabel(card, textvariable=var, font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        label.pack(anchor="w", padx=12, pady=(0, 12))
        return label
    def _build_table(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=8)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))
        ctk.CTkLabel(top, text="实时排行榜", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        self.category_filter_combo = ctk.CTkComboBox(
            top,
            variable=self.category_filter_var,
            values=["全部"],
            width=130,
            command=lambda _: self._refresh_leaderboard(),
        )
        self.category_filter_combo.pack(side="right", padx=(6, 0))
        ctk.CTkButton(top, text="刷新", width=80, fg_color="#409eff", hover_color="#337ecc", command=self._refresh_leaderboard).pack(side="right", padx=(6, 0))
        ctk.CTkButton(top, text="导出总榜", width=110, fg_color="#409eff", hover_color="#337ecc", command=self.export_results_excel).pack(side="right")

        cols = ("rank", "bib", "name", "category", "status", "score", "total")
        self.table = ttk.Treeview(frame, columns=cols, show="headings", style="Dark.Treeview")
        self.table.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.table.heading("rank", text="排名")
        self.table.heading("bib", text="参赛号")
        self.table.heading("name", text="姓名")
        self.table.heading("category", text="组别")
        self.table.heading("status", text="状态")
        self.table.heading("score", text="得分")
        self.table.heading("total", text="总用时")

        self.table.column("rank", width=60, anchor="center")
        self.table.column("bib", width=90, anchor="center")
        self.table.column("name", width=140, anchor="w")
        self.table.column("category", width=130, anchor="w")
        self.table.column("status", width=110, anchor="center")
        self.table.column("score", width=90, anchor="center")
        self.table.column("total", width=120, anchor="center")

    def _build_terminal(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="#ffffff", border_width=0, corner_radius=12)
        frame.grid(row=3, column=0, sticky="nsew", padx=18, pady=(8, 16))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        self.terminal = ctk.CTkTextbox(frame, font=("Consolas", 13), fg_color="#ffffff", text_color="#1d1d1f", border_width=1)
        self.terminal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    def _refresh_leaderboard(self):
        """刷新实时排行榜，并应用组别筛选。"""
        if not hasattr(self, "table"):
            return
        rows = sorted(self._merged_results(), key=self._result_sort_key)

        categories = [r.get("category") for r in rows if r.get("category")]
        options = ["全部"] + sorted(set(categories))
        if hasattr(self, "category_filter_combo"):
            self.category_filter_combo.configure(values=options)
        if self.category_filter_var.get() not in options:
            self.category_filter_var.set("全部")

        selected = self.category_filter_var.get()
        if selected != "全部":
            rows = [r for r in rows if (r.get("category") or "") == selected]

        for item in self.table.get_children():
            self.table.delete(item)

        ranks = self._compute_ranks(rows)
        paired = list(zip(ranks, rows))
        paired = self._page_slice("live", paired)  # 客户端分页（仅影响 self.table 显示）
        for rank, row in paired:
            total_seconds = row.get("total_seconds")
            total_text = self._format_duration(total_seconds) if total_seconds is not None else "--"
            self.table.insert(
                "",
                tk.END,
                values=(
                    rank if rank is not None else "-",
                    row.get("bib_number") or "-",
                    row.get("name") or "-",
                    row.get("category") or "-",
                    row.get("status") or "-",
                    row.get("final_score") if row.get("final_score") is not None else "-",
                    total_text,
                ),
            )
        if hasattr(self, "judge_table"):
            self._refresh_judge_table()
        if hasattr(self, "overview_table"):
            self.refresh_results_overview()
    def _refresh_ranking_cards(self, rows: list):
        if not hasattr(self, "ranking_list"):
            return
        for child in self.ranking_list.winfo_children():
            child.destroy()

        if not rows:
            ctk.CTkLabel(self.ranking_list, text="暂无成绩数据", text_color="#86868b", font=ctk.CTkFont(family="Microsoft YaHei UI", size=13)).pack(fill="x", padx=4, pady=8)
            return

        ranks = self._compute_ranks(rows)
        for idx, (rank, row) in enumerate(zip(ranks, rows), start=1):
            status = (row.get("status") or "DSQ").upper()
            status_color = STATUS_COLORS.get(status, "#EF4444")
            total_seconds = row.get("total_seconds")
            total_text = self._format_duration(total_seconds) if total_seconds is not None else "--"
            score_value = row.get("final_score")
            right_text = total_text if score_value in (None, "") else f"{score_value} 分 / {total_text}"

            row_card = ctk.CTkFrame(self.ranking_list, fg_color="#f5f5f7", corner_radius=14, border_width=0)
            row_card.pack(fill="x", padx=4, pady=5)
            row_card.grid_columnconfigure(1, weight=1)
            rank_text = f"#{rank}" if rank is not None else "—"
            ctk.CTkLabel(row_card, text=rank_text, width=52, text_color="#409eff", font=ctk.CTkFont(family="Microsoft YaHei UI", size=18, weight="bold")).grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(14, 10), pady=12)
            ctk.CTkLabel(row_card, text=row.get("name") or "-", text_color="#1d1d1f", anchor="w", font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold")).grid(row=0, column=1, sticky="ew", pady=(12, 2))
            ctk.CTkLabel(row_card, text=f"{row.get('category') or '-'}  ·  {status}", text_color=status_color, anchor="w", font=ctk.CTkFont(family="Microsoft YaHei UI", size=11, weight="bold")).grid(row=1, column=1, sticky="ew", pady=(0, 12))
            ctk.CTkLabel(row_card, text=right_text, text_color="#1d1d1f", anchor="e", justify="right", font=ctk.CTkFont(family="Microsoft YaHei UI", size=13, weight="bold")).grid(row=0, column=2, rowspan=2, sticky="nse", padx=(12, 14), pady=12)
    def _readout_status_text(self, status: str):
        if status == "OK":
            return "有效"
        if status == "MP":
            return "待复核"
        return "无效"
    def _build_punch_display_rows(self, punches, checkpoints_map: dict):
        rows = []
        for mac, ts in sorted(punches or [], key=lambda item: item[1]):
            cp = checkpoints_map.get(str(mac).upper()) or {}
            cp_code = cp.get("cp_code") or str(mac).upper()
            try:
                time_text = datetime.fromtimestamp(int(ts)).strftime("%H:%M:%S")
            except (TypeError, ValueError, OSError):
                time_text = str(ts)
            rows.append(f"{cp_code}  {time_text}")
        return rows or ["无有效打卡记录"]
    def _show_readout_popup(self, title: str, lines: list, status: str):
        if not self.readout_popup_enabled_var.get():
            return
        if self._readout_popup is not None:
            try:
                if self._readout_popup.winfo_exists():
                    self._readout_popup.destroy()
            except Exception:
                pass

        popup = ctk.CTkToplevel(self)
        popup.title("刷卡结果")
        popup.geometry("520x460")
        popup.attributes("-topmost", True)
        popup.transient(self)
        popup.resizable(False, False)
        self._readout_popup = popup

        color = "#2b8a3e" if status == "OK" else "#409eff" if status == "MP" else "#c92a2a"
        frame = ctk.CTkFrame(popup, fg_color="#ffffff", corner_radius=0)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(
            frame,
            text=title,
            text_color=color,
            font=ctk.CTkFont(size=22, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(
            frame,
            text=f"成绩判定：{self._readout_status_text(status)}",
            text_color="#1d1d1f",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))
        textbox = ctk.CTkTextbox(frame, fg_color="#f5f9ff", text_color="#1d1d1f", border_width=0)
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        textbox.insert("1.0", "\n".join(lines))
        textbox.configure(state="disabled")
        ctk.CTkButton(frame, text="关闭", width=100, fg_color="#409eff", hover_color="#337ecc", command=popup.destroy).pack(
            anchor="e", padx=16, pady=(0, 16)
        )
        popup.after(12000, lambda: popup.destroy() if popup.winfo_exists() else None)
    def _build_overview_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0, minsize=300)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=1)

        hero_card, hero_inner = self._make_soft_card(parent, "赛事总览", "把关键播报、设备状态和导出动作收拢到一个页面，减少跨页切换。")
        hero_card.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 12))
        hero_inner.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.hw_card = self._build_overview_metric(hero_inner, 0, "设备状态", self.hw_state)
        self.wifi_card = self._build_overview_metric(hero_inner, 1, "Wi-Fi", self.wifi_state)
        self.time_card = self._build_overview_metric(hero_inner, 2, "NTP 时间", self.ntp_state)
        self.readout_card = self._build_overview_metric(hero_inner, 3, "最新成绩", self.readout_state)

        readout_card, readout_inner = self._make_soft_card(parent, "刷卡播报", "主站检测到刷卡后，会在这里显示最新结果，并保留弹窗切换。")
        readout_card.grid(row=1, column=0, sticky="ew", padx=(8, 12), pady=(0, 12))
        readout_head = ctk.CTkFrame(readout_inner, fg_color="transparent", border_width=0)
        readout_head.pack(fill="x", pady=(14, 0))
        readout_head.grid_columnconfigure(0, weight=1)
        ctk.CTkCheckBox(
            readout_head,
            text="刷卡时弹窗",
            variable=self.readout_popup_enabled_var,
            text_color="#1d1d1f",
            fg_color="#409eff",
            hover_color="#337ecc",
        ).grid(row=0, column=1, sticky="e")
        self.readout_banner = ctk.CTkLabel(
            readout_inner,
            textvariable=self.readout_state,
            text_color="#409eff",
            justify="left",
            wraplength=560,
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=26, weight="bold"),
        )
        self.readout_banner.pack(fill="x", pady=(8, 14))

        export_card, export_inner = self._make_soft_card(parent, "导出与工具", "成绩总表、分段成绩和原始流水都集中在这里。")
        export_card.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=(0, 12))
        ctk.CTkButton(export_inner, text="导出成绩总表", fg_color="#409eff", hover_color="#337ecc", corner_radius=14, height=40, command=self.export_results_excel).pack(fill="x", pady=(14, 8))
        ctk.CTkButton(export_inner, text="导出分段成绩", fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", corner_radius=14, height=40, command=self.export_split_excel).pack(fill="x", pady=8)
        ctk.CTkButton(export_inner, text="导出原始流水", fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", corner_radius=14, height=40, command=self.export_raw_excel).pack(fill="x", pady=8)
        ctk.CTkButton(export_inner, text="一键重算成绩", fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", corner_radius=14, height=40, command=self.recalculate_all_results).pack(fill="x", pady=(8, 0))

        write_card, write_inner = self._make_soft_card(parent, "制卡状态", "保留原有写卡历史与状态反馈，方便现场快速确认设备响应。")
        write_card.grid(row=2, column=1, rowspan=2, sticky="nsew", padx=(0, 8), pady=(0, 8))
        ctk.CTkLabel(write_inner, textvariable=self.write_state, text_color="#1d1d1f", wraplength=250, justify="left", font=ctk.CTkFont(family="Microsoft YaHei UI", size=14, weight="bold")).pack(fill="x", pady=(14, 10))
        ctk.CTkLabel(write_inner, text="常用制卡动作", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).pack(anchor="w", pady=(0, 8))

        quick_row_1 = ctk.CTkFrame(write_inner, fg_color="transparent", border_width=0)
        quick_row_1.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(quick_row_1, text="普通卡", width=116, height=38, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=lambda: self.send_make_card_cmd("CMD:MAKE_NORMAL", "普通卡")).pack(side="left")
        ctk.CTkButton(quick_row_1, text="起点卡", width=116, height=38, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_make_card_cmd("CMD:MAKE_START", "起点卡")).pack(side="right")

        quick_row_2 = ctk.CTkFrame(write_inner, fg_color="transparent", border_width=0)
        quick_row_2.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(quick_row_2, text="途经卡", width=116, height=38, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_make_card_cmd("CMD:MAKE_MID", "途经卡")).pack(side="left")
        ctk.CTkButton(quick_row_2, text="终点卡", width=116, height=38, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_make_card_cmd("CMD:MAKE_END", "终点卡")).pack(side="right")

        quick_row_3 = ctk.CTkFrame(write_inner, fg_color="transparent", border_width=0)
        quick_row_3.pack(fill="x", pady=(0, 12))
        ctk.CTkButton(quick_row_3, text="清除卡", width=116, height=38, corner_radius=14, fg_color="#F1F5F9", hover_color="#E2E8F0", text_color="#409eff", command=lambda: self.send_make_card_cmd("CMD:MAKE_CLEAR", "清除卡")).pack(side="left")
        ctk.CTkButton(quick_row_3, text="校时卡", width=116, height=38, corner_radius=14, fg_color="#F1F5F9", hover_color="#E2E8F0", text_color="#409eff", command=lambda: self.send_cmd("CMD:MAKE_SYNC")).pack(side="right")
        custom_row = ctk.CTkFrame(write_inner, fg_color="transparent", border_width=0)
        custom_row.pack(fill="x", pady=(0, 10))
        custom_row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(custom_row, textvariable=self.custom_var, placeholder_text="输入命令，例如 CMD:GET_STATUS", fg_color="#f5f5f7", border_width=0, height=38, corner_radius=12).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(custom_row, text="发送", width=72, height=38, corner_radius=12, fg_color="#409eff", hover_color="#337ecc", command=self.send_custom).grid(row=0, column=1, sticky="e")
        self.write_history_box = ctk.CTkTextbox(write_inner, height=220, fg_color="#f5f5f7", text_color="#1d1d1f", border_width=0, corner_radius=14, font=("Consolas", 12))
        self.write_history_box.pack(fill="both", expand=True, pady=(4, 0))
        self.write_history_box.insert("1.0", "暂无记录\n")
        self.write_history_box.configure(state="disabled")

        monitor_card, monitor_inner = self._make_soft_card(parent, "设备监控", "检查点在线情况、最近心跳和 NTP 同步状态都集中在这里查看。")
        monitor_card.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=(8, 12), pady=(0, 8))
        monitor_inner.pack_propagate(False)

        if not hasattr(self, "monitor_online_var"):
            self.monitor_online_var = tk.StringVar(value="0/0")
        if not hasattr(self, "monitor_synced_var"):
            self.monitor_synced_var = tk.StringVar(value="0/0")
        if not hasattr(self, "monitor_attention_var"):
            self.monitor_attention_var = tk.StringVar(value="0")

        summary_row = ctk.CTkFrame(monitor_inner, fg_color="transparent", border_width=0)
        summary_row.pack(fill="x", pady=(14, 0))
        summary_row.grid_columnconfigure((0, 1, 2), weight=1)
        self._build_table_stat_chip(summary_row, 0, "在线设备", self.monitor_online_var, "#2B8A3E")
        self._build_table_stat_chip(summary_row, 1, "已同步", self.monitor_synced_var, "#2563EB")
        self._build_table_stat_chip(summary_row, 2, "待关注", self.monitor_attention_var, "#C2410C")

        monitor_section, monitor_toolbar, monitor_table_shell, self.monitor_empty_label = self._make_table_section(
            monitor_inner,
            "设备状态表",
            "表头和状态列固定显示，可直接筛选点号、MAC、节点号和准备状态。",
            "当前还没有检查点数据",
        )
        monitor_section.pack(fill="both", expand=True, pady=(16, 0))
        self._build_search_bar(monitor_toolbar, self.monitor_search_var, "搜索点号 / MAC / 节点 / 状态", self._refresh_device_monitor, row=0)
        self.monitor_table = ttk.Treeview(
            monitor_table_shell,
            columns=("cp_code", "mac", "node", "role", "last_seen", "ntp", "battery", "ready"),
            show="headings",
            style="Dark.Treeview",
            height=12,
        )
        self.monitor_table.heading("cp_code", text="点号")
        self.monitor_table.heading("mac", text="MAC")
        self.monitor_table.heading("node", text="Node")
        self.monitor_table.heading("role", text="角色")
        self.monitor_table.heading("last_seen", text="最近上报")
        self.monitor_table.heading("ntp", text="NTP")
        self.monitor_table.heading("battery", text="电量")
        self.monitor_table.heading("ready", text="READY")
        self.monitor_table.column("cp_code", width=88, anchor="center")
        self.monitor_table.column("mac", width=160, anchor="center")
        self.monitor_table.column("node", width=74, anchor="center")
        self.monitor_table.column("role", width=96, anchor="center")
        self.monitor_table.column("last_seen", width=120, anchor="center")
        self.monitor_table.column("ntp", width=110, anchor="center")
        self.monitor_table.column("battery", width=90, anchor="center")
        self.monitor_table.column("ready", width=88, anchor="center")
        self._mount_treeview(self.monitor_table, monitor_table_shell, self.monitor_empty_label)
    def _build_overview_metric(self, parent, column: int, title: str, variable):
        card = ctk.CTkFrame(parent, fg_color="#f5f5f7", corner_radius=16, border_width=0)
        card.grid(row=0, column=column, sticky="ew", padx=6, pady=(14, 0))
        ctk.CTkLabel(card, text=title, text_color="#86868b", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).pack(anchor="w", padx=14, pady=(12, 2))
        value = ctk.CTkLabel(card, textvariable=variable, text_color="#1d1d1f", wraplength=180, justify="left", font=ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold"))
        value.pack(anchor="w", padx=14, pady=(0, 10))
        progress = ctk.CTkProgressBar(card, height=6, corner_radius=999, fg_color="#ecf5ff", progress_color="#409eff")
        progress.pack(fill="x", padx=14, pady=(0, 12))
        progress.set(0.18 if column < 3 else 0.22)
        return value
    def _toggle_live_panel(self, value: str):
        if value == "实时排名":
            self.terminal_panel.pack_forget()
            self.ranking_panel.pack(fill="both", expand=True)
        else:
            self.ranking_panel.pack_forget()
            self.terminal_panel.pack(fill="both", expand=True)
