"""成绩页：裁判改判与改判审计。"""

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk


AUTO_STATUS = "（自动判定）"
JUDGE_STATUS_OPTIONS = [AUTO_STATUS, "OK", "MP", "OT", "DNF", "DNS", "DSQ"]


class ResultsPageMixin:
    def _build_results_page(self, parent):
        page = ctk.CTkScrollableFrame(parent, fg_color="#f5f5f7", corner_radius=0, border_width=0)
        page.pack(fill="both", expand=True)

        # ---- 成绩列表 ----
        table_card, table_inner = self._make_soft_card(page, "成绩列表", "选中一条成绩后在下方裁判面板手动改判；改判结果会即时反映到排行榜。")
        table_card.pack(fill="both", expand=True, padx=8, pady=(0, 20))
        section, toolbar, shell, self.judge_empty_label = self._make_table_section(
            table_inner, "全部成绩", "状态/得分/用时均为合并后的最终口径，「改」列标记被裁判改判过。", "当前赛事还没有成绩"
        )
        section.pack(fill="both", expand=True, pady=(14, 0))
        self._build_search_bar(toolbar, self.result_search_var, "搜索号码 / 姓名 / 组别 / 状态", self._refresh_judge_table, row=0)
        self.judge_table = ttk.Treeview(
            shell, columns=("bib", "name", "category", "status", "score", "total", "flag"), show="headings", style="Dark.Treeview", height=10
        )
        for col, text, width, anchor in (
            ("bib", "参赛号", 90, "center"),
            ("name", "姓名", 130, "w"),
            ("category", "组别", 120, "w"),
            ("status", "最终状态", 100, "center"),
            ("score", "得分", 80, "center"),
            ("total", "用时", 110, "center"),
            ("flag", "改", 50, "center"),
        ):
            self.judge_table.heading(col, text=text)
            self.judge_table.column(col, width=width, anchor=anchor)
        self.judge_table.bind("<<TreeviewSelect>>", self._on_judge_select)
        self._mount_treeview(self.judge_table, shell, self.judge_empty_label)

        # ---- 裁判改判面板 ----
        judge_card, judge_inner = self._make_soft_card(page, "裁判改判", "留空表示沿用自动判定；时间格式 YYYY-MM-DD HH:MM:SS。")
        judge_card.pack(fill="x", padx=8, pady=(0, 20))
        form = ctk.CTkFrame(judge_inner, fg_color="transparent", border_width=0)
        form.pack(fill="x", pady=(14, 10))
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form, text="选手 UID", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        ctk.CTkLabel(form, textvariable=self.judge_uid_var, text_color="#1d1d1f", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=0, column=1, sticky="w", pady=6)
        ctk.CTkLabel(form, text="改判状态", text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=0, column=2, sticky="w", padx=(0, 10), pady=6)
        ctk.CTkComboBox(form, variable=self.judge_status_var, values=JUDGE_STATUS_OPTIONS, height=38, corner_radius=12, fg_color="#F8FAFC", text_color="#1d1d1f", border_width=0, button_color="#409eff", button_hover_color="#337ecc").grid(row=0, column=3, sticky="ew", pady=6)

        self._judge_entry(form, 1, 0, "加减分/罚时", self.judge_penalty_var, "整数，SCORE 加减分 / 计时赛加减秒")
        self._judge_entry(form, 1, 2, "备注", self.judge_note_var, "改判理由")
        self._judge_entry(form, 2, 0, "手动起点时间", self.judge_start_var, "可空，覆盖起点")
        self._judge_entry(form, 2, 2, "手动终点时间", self.judge_finish_var, "可空，覆盖终点")

        btns = ctk.CTkFrame(judge_inner, fg_color="transparent", border_width=0)
        btns.pack(fill="x", pady=(4, 6))
        ctk.CTkButton(btns, text="保存改判", width=120, height=38, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.apply_result_override).pack(side="left")
        ctk.CTkButton(btns, text="清除改判", width=120, height=38, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.clear_result_override).pack(side="left", padx=10)

        # ---- 改判记录 ----
        log_card, log_inner = self._make_soft_card(page, "改判记录", "本赛事所有手动改判的可追溯审计流水（最新在上）。")
        log_card.pack(fill="both", expand=True, padx=8, pady=(0, 20))
        self.adjustment_log_box = ctk.CTkTextbox(log_inner, height=180, fg_color="#f5f5f7", text_color="#1d1d1f", border_width=0, corner_radius=14, font=("Consolas", 12))
        self.adjustment_log_box.pack(fill="both", expand=True, pady=(14, 0))
        self.adjustment_log_box.configure(state="disabled")

        self._refresh_judge_table()
        self._refresh_adjustment_log()
    def _judge_entry(self, parent, row, col, label, variable, placeholder):
        ctk.CTkLabel(parent, text=label, text_color="#64748B", font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold")).grid(row=row, column=col, sticky="w", padx=(0, 10), pady=6)
        ctk.CTkEntry(parent, textvariable=variable, placeholder_text=placeholder, height=38, corner_radius=12, fg_color="#F8FAFC", border_width=0).grid(row=row, column=col + 1, sticky="ew", pady=6)
    def _refresh_judge_table(self):
        if not hasattr(self, "judge_table"):
            return
        query = self.result_search_var.get().strip().lower()
        for item in self.judge_table.get_children():
            self.judge_table.delete(item)
        rows = sorted(self._merged_results(), key=self._result_sort_key)
        for row in rows:
            total = row.get("total_seconds")
            total_text = self._format_duration(total) if total is not None else "--"
            values = (
                row.get("bib_number") or "-",
                row.get("name") or "-",
                row.get("category") or "-",
                row.get("status") or "-",
                row.get("final_score") if row.get("final_score") is not None else "-",
                total_text,
                "改" if row.get("overridden") else "",
            )
            if query and not any(query in str(v).lower() for v in values):
                continue
            self.judge_table.insert("", tk.END, iid=str(row.get("uid")), values=values)
    def _on_judge_select(self, _event=None):
        selected = self.judge_table.selection()
        if not selected:
            return
        uid = selected[0]
        result = self.store.get_result(uid)
        if not result:
            return
        self.judge_uid_var.set(uid)
        self.judge_status_var.set(result.get("manual_status") or AUTO_STATUS)
        penalty = result.get("penalty_adjust")
        self.judge_penalty_var.set("" if penalty in (None, "") else str(penalty))
        self.judge_start_var.set(self._format_start_time(result.get("manual_start_time")))
        self.judge_finish_var.set(self._format_start_time(result.get("manual_finish_time")))
        self.judge_note_var.set(result.get("judge_note") or "")
    def apply_result_override(self):
        uid = self.judge_uid_var.get().strip()
        if not uid:
            messagebox.showwarning("提示", "请先在成绩列表选择一名选手")
            return
        existing = self.store.get_result(uid)
        if not existing:
            messagebox.showwarning("提示", "未找到该选手的成绩记录")
            return

        status_choice = self.judge_status_var.get()
        new_status = None if status_choice == AUTO_STATUS else status_choice
        pen_text = self.judge_penalty_var.get().strip()
        try:
            new_penalty = int(pen_text) if pen_text else None
        except ValueError:
            messagebox.showwarning("提示", "加减分/罚时必须是整数")
            return
        try:
            new_start = self._parse_start_time(self.judge_start_var.get())
            new_finish = self._parse_start_time(self.judge_finish_var.get())
        except ValueError:
            messagebox.showwarning("提示", "时间格式应为 YYYY-MM-DD HH:MM:SS 或留空")
            return
        note = self.judge_note_var.get().strip()

        changes = [
            ("manual_status", existing.get("manual_status"), new_status),
            ("penalty_adjust", existing.get("penalty_adjust"), new_penalty),
            ("manual_start_time", existing.get("manual_start_time"), new_start),
            ("manual_finish_time", existing.get("manual_finish_time"), new_finish),
        ]
        logged = 0
        for field, old, new in changes:
            if (old if old not in ("",) else None) != (new if new not in ("",) else None):
                self.store.add_result_adjustment(uid, field, old, new, note)
                logged += 1

        self.store.update_result_overrides(uid, new_status, new_penalty, new_start, new_finish, note)
        self._append_terminal(f"[JUDGE] UID={uid} 改判完成，记录 {logged} 项变更")
        self._refresh_leaderboard()
        self._refresh_adjustment_log()
    def clear_result_override(self):
        uid = self.judge_uid_var.get().strip()
        if not uid:
            messagebox.showwarning("提示", "请先在成绩列表选择一名选手")
            return
        if not messagebox.askyesno("清除改判", f"确认清除 UID={uid} 的全部改判覆盖？"):
            return
        self.store.add_result_adjustment(uid, "ALL", "(overrides)", "(cleared)", "清除改判")
        self.store.update_result_overrides(uid, None, None, None, None, None)
        self.judge_status_var.set(AUTO_STATUS)
        self.judge_penalty_var.set("")
        self.judge_start_var.set("")
        self.judge_finish_var.set("")
        self.judge_note_var.set("")
        self._append_terminal(f"[JUDGE] UID={uid} 已清除改判")
        self._refresh_leaderboard()
        self._refresh_adjustment_log()
    def _refresh_adjustment_log(self):
        if not hasattr(self, "adjustment_log_box"):
            return
        lines = []
        for r in self.store.list_result_adjustments():
            old = r.get("old_value")
            new = r.get("new_value")
            note = f"  // {r['note']}" if r.get("note") else ""
            lines.append(f"[{r['created_at']}] UID={r['uid']} {r['field']}: {old} -> {new}{note}")
        self.adjustment_log_box.configure(state="normal")
        self.adjustment_log_box.delete("1.0", tk.END)
        self.adjustment_log_box.insert("1.0", "\n".join(lines) if lines else "暂无改判记录\n")
        self.adjustment_log_box.configure(state="disabled")
