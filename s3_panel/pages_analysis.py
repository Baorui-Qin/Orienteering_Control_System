"""赛后分析：成绩一览表 + 大屏滚动成绩。"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
from openpyxl import Workbook

from .theme import FONT_FAMILY, PALETTE

OVERVIEW_COLS = ("rank", "bib", "uid", "name", "category", "unit", "total", "valid", "reason", "start", "finish")


class AnalysisPageMixin:
    def _build_results_overview_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        card, inner = self._make_soft_card(parent, "成绩一览表", "按组别排名；可平行分组合并、导出与开大屏。")
        card.grid(row=0, column=0, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(1, weight=1)

        ctrl = ctk.CTkFrame(inner, fg_color="transparent", border_width=0)
        ctrl.grid(row=0, column=0, sticky="ew", pady=(12, 8))
        ctk.CTkLabel(ctrl, text="当前组别", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.overview_category_combo = ctk.CTkComboBox(
            ctrl, variable=self.overview_category_var, values=["全部"], width=160, height=34, corner_radius=8,
            fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"],
            button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"],
            dropdown_fg_color=PALETTE["card_bg"], dropdown_hover_color=PALETTE["primary_soft"],
            command=lambda _v: self.refresh_results_overview(),
        )
        self.overview_category_combo.pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(ctrl, text="平行分组合并", variable=self.overview_merge_var, text_color=PALETTE["text"], fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.refresh_results_overview).pack(side="left", padx=(0, 12))
        ctk.CTkButton(ctrl, text="导出全部成绩", width=130, height=34, corner_radius=8, fg_color=PALETTE["success"], hover_color=PALETTE["success_hover"], command=self.export_all_results).pack(side="right")
        ctk.CTkLabel(ctrl, text="前 N", text_color=PALETTE["text_label"], font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="right", padx=(0, 6))
        ctk.CTkComboBox(ctrl, variable=self.overview_topn_var, values=["3", "10", "20", "50"], width=72, height=34, corner_radius=8, fg_color=PALETTE["field_bg"], text_color=PALETTE["text"], border_width=1, border_color=PALETTE["border"], button_color=PALETTE["primary"], button_hover_color=PALETTE["primary_hover"]).pack(side="right", padx=(0, 8))
        ctk.CTkButton(ctrl, text="打开大屏", width=110, height=34, corner_radius=8, fg_color=PALETTE["primary"], hover_color=PALETTE["primary_hover"], command=self.open_big_screen).pack(side="right", padx=(0, 8))

        shell = ctk.CTkFrame(inner, fg_color=PALETTE["card_bg"], corner_radius=10, border_width=1, border_color=PALETTE["border"])
        shell.grid(row=1, column=0, sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(0, weight=1)
        self.overview_table = ttk.Treeview(shell, columns=OVERVIEW_COLS, show="headings", style="Dark.Treeview", height=16)
        for c, t, w in (
            ("rank", "排名", 60), ("bib", "参赛号", 80), ("uid", "指卡号", 110), ("name", "姓名", 120),
            ("category", "组别", 110), ("unit", "单位", 120), ("total", "用时", 100), ("valid", "有效性", 80),
            ("reason", "原因", 80), ("start", "起点时间", 160), ("finish", "终点时间", 160),
        ):
            self.overview_table.heading(c, text=t)
            self.overview_table.column(c, width=w, anchor="w" if c in ("name", "category", "unit") else "center")
        self.overview_table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.refresh_results_overview()

    def _overview_rows(self):
        """返回 [(rank, row)]，按当前组别/平行分组合并控制名次。row 含 _unit_name。"""
        rows = self._merged_results()
        units = {u["unit_id"]: u["name"] for u in self.store.list_units()}
        runner_unit = {r["uid"]: units.get(r.get("unit_id")) for r in self.store.list_runners()}
        for row in rows:
            row["_unit_name"] = runner_unit.get(row["uid"]) or "-"

        category = self.overview_category_var.get()
        if category and category != "全部":
            subset = sorted([r for r in rows if (r.get("category") or "") == category], key=self._result_sort_key)
            return list(zip(self._compute_ranks(subset), subset))
        if self.overview_merge_var.get():
            allr = sorted(rows, key=self._result_sort_key)
            return list(zip(self._compute_ranks(allr), allr))
        out = []
        for cat in sorted({(r.get("category") or "") for r in rows}):
            sub = sorted([r for r in rows if (r.get("category") or "") == cat], key=self._result_sort_key)
            out.extend(zip(self._compute_ranks(sub), sub))
        return out

    def refresh_results_overview(self):
        if not hasattr(self, "overview_table"):
            return
        all_rows = self._merged_results()
        cats = ["全部"] + sorted({(r.get("category") or "") for r in all_rows if r.get("category")})
        if hasattr(self, "overview_category_combo"):
            self.overview_category_combo.configure(values=cats)
        if self.overview_category_var.get() not in cats:
            self.overview_category_var.set("全部")

        for item in self.overview_table.get_children():
            self.overview_table.delete(item)
        for rank, row in self._overview_rows():
            total = row.get("total_seconds")
            total_text = self._format_duration(total) if total is not None else "--"
            status = (row.get("status") or "").upper()
            self.overview_table.insert("", tk.END, values=(
                rank if rank is not None else "-",
                row.get("bib_number") or "-",
                row.get("uid") or "-",
                row.get("name") or "-",
                row.get("category") or "-",
                row.get("_unit_name") or "-",
                total_text,
                self._readout_status_text(status),
                "" if status == "OK" else status,
                self._format_start_time(row.get("start_time")),
                self._format_start_time(row.get("finish_time")),
            ))

    def export_all_results(self):
        rows = self._overview_rows()
        if not rows:
            messagebox.showwarning("提示", "没有可导出的成绩")
            return
        out = filedialog.asksaveasfilename(title="导出全部成绩", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if not out:
            return
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        ws.append(["排名", "参赛号", "指卡号", "姓名", "组别", "单位", "用时(秒)", "有效性", "原因", "起点时间", "终点时间"])
        for rank, row in rows:
            status = (row.get("status") or "").upper()
            ws.append([
                rank if rank is not None else "-", row.get("bib_number") or "-", row.get("uid") or "-",
                row.get("name") or "-", row.get("category") or "-", row.get("_unit_name") or "-",
                row.get("total_seconds"), self._readout_status_text(status), "" if status == "OK" else status,
                self._format_start_time(row.get("start_time")), self._format_start_time(row.get("finish_time")),
            ])
        wb.save(out)
        messagebox.showinfo("导出完成", f"已导出到\n{out}")

    # ------------------------------------------------------------------
    # 大屏滚动成绩
    # ------------------------------------------------------------------
    def open_big_screen(self):
        if self._big_screen is not None:
            try:
                if self._big_screen.winfo_exists():
                    self._big_screen.destroy()
            except Exception:  # noqa: BLE001
                pass
        top = ctk.CTkToplevel(self)
        top.title("成绩大屏")
        top.configure(fg_color="#000000")
        top.geometry("1280x720")
        try:
            top.attributes("-fullscreen", True)
        except Exception:  # noqa: BLE001
            pass
        top.bind("<Escape>", lambda _e: top.destroy())
        self._big_screen = top

        try:
            topn = int(self.overview_topn_var.get())
        except (TypeError, ValueError):
            topn = 10

        text = tk.Text(top, bg="#000000", fg="#33FF99", font=(FONT_FAMILY, 26, "bold"), bd=0, highlightthickness=0, wrap="none")
        text.pack(fill="both", expand=True, padx=48, pady=48)
        lines = ["{:<5}{:<10}{:<14}{:<14}{:<12}".format("名次", "号码", "姓名", "组别", "用时")]
        lines.append("-" * 56)
        for rank, row in self._overview_rows():
            if rank is None or (topn and rank > topn):
                continue
            total = row.get("total_seconds")
            total_text = self._format_duration(total) if total is not None else "--"
            lines.append("{:<5}{:<10}{:<14}{:<14}{:<12}".format(
                rank, str(row.get("bib_number") or "-"), str(row.get("name") or "-"),
                str(row.get("category") or "-"), total_text,
            ))
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")
        self._scroll_big_screen(text)

    def _scroll_big_screen(self, text):
        if self._big_screen is None or not self._big_screen.winfo_exists():
            return
        try:
            if text.yview()[1] >= 1.0:
                text.yview_moveto(0.0)
            else:
                text.yview_scroll(1, "units")
        except Exception:  # noqa: BLE001
            return
        self._big_screen.after(450, lambda: self._scroll_big_screen(text))
