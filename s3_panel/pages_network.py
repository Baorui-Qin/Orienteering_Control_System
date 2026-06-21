"""Network page mixin for Wi-Fi and ESP-NOW controls."""

import re
import tkinter as tk
from datetime import datetime

import customtkinter as ctk


class NetworkPageMixin:
    def _build_right_aside(self):
        self._build_aside_connection_card()
        self._build_aside_status_card()
        self._build_aside_network_card()
        self._build_aside_action_card()

    def _aside_card(self, title: str, subtitle: str):
        card = ctk.CTkFrame(self.aside_panel, fg_color="#fcfaf6", corner_radius=24, border_width=0)
        card.pack(fill="x", padx=8, pady=(0, 12))
        ctk.CTkLabel(
            card,
            text=title,
            text_color="#14293d",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(18, 2))
        ctk.CTkLabel(
            card,
            text=subtitle,
            text_color="#7b8a98",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=18, pady=(0, 14))
        return card

    def _build_aside_connection_card(self):
        card = self._aside_card("设备连接", "把串口、波特率和连接状态集中放在这里。")
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(0, 10))
        self.port_combo = ctk.CTkComboBox(top, variable=self.port_var, values=[""], width=150, corner_radius=14)
        self.port_combo.pack(side="left", padx=(0, 8))
        self.baud_entry = ctk.CTkEntry(top, textvariable=self.baud_var, width=118, corner_radius=14, placeholder_text="115200")
        self.baud_entry.pack(side="left")

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(0, 12))
        ctk.CTkButton(btns, text="刷新", width=74, corner_radius=16, fg_color="#d9e5ef", hover_color="#c5d7e5", text_color="#17324d", command=self.refresh_ports).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="连接", width=92, corner_radius=16, fg_color="#17324d", hover_color="#294b6e", command=self.connect_serial).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="断开", width=92, corner_radius=16, fg_color="#d95f5f", hover_color="#c34f4f", command=self.disconnect_serial).pack(side="left")

        self.conn_state_label = ctk.CTkLabel(
            card,
            textvariable=self.conn_state,
            text_color="#17324d",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.conn_state_label.pack(anchor="w", padx=18, pady=(0, 10))
        self.conn_progress = ctk.CTkProgressBar(card, height=8, corner_radius=999, progress_color="#17324d", fg_color="#e9e2d7")
        self.conn_progress.pack(fill="x", padx=18, pady=(0, 18))
        self.conn_progress.set(0)

    def _build_aside_status_card(self):
        card = self._aside_card("系统状态", "把关键状态放到右侧附加面板，减少主区域负担。")
        self.wifi_status_label = self._aside_metric(card, "Wi-Fi", self.wifi_state)
        self.ntp_status_label = self._aside_metric(card, "NTP", self.ntp_state)
        self.mode_status_label = self._aside_metric(card, "模式", self.mode_state)
        self.hb_status_label = self._aside_metric(card, "最近心跳", self.last_heartbeat_var)
        self.status_meter = ctk.CTkProgressBar(card, height=8, corner_radius=999, progress_color="#a77b43", fg_color="#e9e2d7")
        self.status_meter.pack(fill="x", padx=18, pady=(6, 18))
        self.status_meter.set(0.15)

    def _aside_metric(self, parent, title: str, variable):
        row = ctk.CTkFrame(parent, fg_color="#f5efe5", corner_radius=18, border_width=0)
        row.pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkLabel(row, text=title, text_color="#7b8a98", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=14, pady=(10, 2))
        label = ctk.CTkLabel(row, textvariable=variable, text_color="#17324d", font=ctk.CTkFont(size=14, weight="bold"), justify="left", anchor="w")
        label.pack(anchor="w", padx=14, pady=(0, 10))
        return label

    def _build_aside_network_card(self):
        card = self._aside_card("网络下发", "在这里维护网关 Wi-Fi 名称与密码。")
        ctk.CTkEntry(card, textvariable=self.ssid_var, placeholder_text="Wi-Fi SSID", corner_radius=16).pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkEntry(card, textvariable=self.pwd_var, placeholder_text="Wi-Fi 密码", show="*", corner_radius=16).pack(fill="x", padx=18, pady=(0, 10))
        ctk.CTkButton(card, text="下发网络配置", corner_radius=16, fg_color="#17324d", hover_color="#294b6e", command=self.send_wifi_config).pack(fill="x", padx=18, pady=(0, 18))

    def _build_aside_action_card(self):
        card = self._aside_card("快捷操作", "制卡控制、命令发送和最近写卡状态都集中在这里。")
        quick = ctk.CTkFrame(card, fg_color="transparent")
        quick.pack(fill="x", padx=18, pady=(0, 10))
        ctk.CTkButton(quick, text="普通卡", width=94, corner_radius=16, fg_color="#17324d", hover_color="#294b6e", command=lambda: self.send_make_card_cmd("CMD:MAKE_NORMAL", "普通卡")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(quick, text="起点卡", width=94, corner_radius=16, fg_color="#c8a56a", hover_color="#b38f57", text_color="#14293d", command=lambda: self.send_make_card_cmd("CMD:MAKE_START", "起点卡")).pack(side="left", padx=(0, 8))
        ctk.CTkButton(quick, text="终点卡", width=94, corner_radius=16, fg_color="#d9e5ef", hover_color="#c5d7e5", text_color="#17324d", command=lambda: self.send_make_card_cmd("CMD:MAKE_END", "终点卡")).pack(side="left")
        ctk.CTkLabel(card, textvariable=self.write_state, text_color="#17324d", wraplength=290, justify="left").pack(anchor="w", padx=18, pady=(0, 10))
        ctk.CTkEntry(card, textvariable=self.custom_var, placeholder_text="CMD:...", corner_radius=16).pack(fill="x", padx=18, pady=(0, 8))
        ctk.CTkButton(card, text="发送自定义命令", corner_radius=16, fg_color="transparent", hover_color="#ece5d8", text_color="#17324d", command=self.send_custom).pack(fill="x", padx=18, pady=(0, 8))
        self.write_history_box = ctk.CTkTextbox(card, height=110, fg_color="#f5efe5", text_color="#17324d", border_width=0, corner_radius=18, font=("Consolas", 12))
        self.write_history_box.pack(fill="x", padx=18, pady=(0, 18))
        self.write_history_box.insert("1.0", "暂无记录\n")
        self.write_history_box.configure(state="disabled")

    def _refresh_aside_visuals(self):
        connected = self.worker.is_connected
        if hasattr(self, "conn_progress"):
            self.conn_progress.set(1.0 if connected else 0.08)
        if hasattr(self, "status_meter"):
            wifi_ok = "ONLINE" in self.wifi_state.get().upper()
            ntp_ok = self.ntp_state.get() not in ("TIME UNKNOWN", "0", "--")
            score = 0.18 + (0.28 if connected else 0.0) + (0.27 if wifi_ok else 0.0) + (0.27 if ntp_ok else 0.0)
            self.status_meter.set(min(1.0, score))
        self.after(600, self._refresh_aside_visuals)

    def _refresh_node_options(self):
        self.node_option_map = {}
        values = []
        for cp in self.store.list_checkpoints():
            mac = (cp.get("mac") or "").upper()
            if not mac:
                continue
            cp_code = cp.get("cp_code") or "--"
            label = f"{cp_code} | {mac}"
            self.node_option_map[label] = mac
            values.append(label)

        values = values or [""]
        if hasattr(self, "node_target_combo"):
            self.node_target_combo.configure(values=values)

        current = self.node_target_var.get().strip()
        if current in self.node_option_map or re.fullmatch(r"[0-9A-Fa-f]{12}", current):
            return
        self.node_target_var.set(values[0] if values[0] else "")

    def _selected_node_mac(self):
        value = self.node_target_var.get().strip()
        if value in self.node_option_map:
            return self.node_option_map[value]
        if re.fullmatch(r"[0-9A-Fa-f]{12}", value or ""):
            return value.upper()
        return None

    def _push_network_feedback(self, level: str, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{level}] {text}"
        self.network_feedback_records.append(line)
        self.network_feedback_records = self.network_feedback_records[-40:]

        if hasattr(self, "network_feedback_box"):
            self.network_feedback_box.configure(state="normal")
            self.network_feedback_box.delete("1.0", tk.END)
            for item in reversed(self.network_feedback_records):
                self.network_feedback_box.insert(tk.END, item + "\n")
            self.network_feedback_box.configure(state="disabled")

    def _build_network_page(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        wifi_card, wifi_inner = self._make_soft_card(parent, "Wi-Fi 配置", "向网关下发联网参数。")
        wifi_card.grid(row=0, column=0, sticky="nsew", padx=(8, 12), pady=(0, 12))
        ctk.CTkLabel(wifi_inner, text="SSID", text_color="#86868b").pack(anchor="w", pady=(14, 4))
        ctk.CTkEntry(wifi_inner, textvariable=self.ssid_var, placeholder_text="Wi-Fi 名称", fg_color="#f5f5f7", border_width=0, height=40, corner_radius=12).pack(fill="x")
        ctk.CTkLabel(wifi_inner, text="Password", text_color="#86868b").pack(anchor="w", pady=(12, 4))
        ctk.CTkEntry(wifi_inner, textvariable=self.pwd_var, show="*", placeholder_text="Wi-Fi 密码", fg_color="#f5f5f7", border_width=0, height=40, corner_radius=12).pack(fill="x")
        ctk.CTkButton(wifi_inner, text="下发配置", height=40, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.send_wifi_config).pack(fill="x", pady=(16, 0))

        control_card, control_inner = self._make_soft_card(parent, "ESP-NOW 控制", "支持单点校时、群发校时和持续广播校时。")
        control_card.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=(0, 12))
        ctk.CTkLabel(control_inner, text="目标节点", text_color="#86868b").pack(anchor="w", pady=(14, 4))
        self.node_target_combo = ctk.CTkComboBox(
            control_inner,
            variable=self.node_target_var,
            values=[""],
            height=40,
            corner_radius=12,
            fg_color="#f5f5f7",
            border_width=0,
            button_color="#409eff",
            button_hover_color="#337ecc",
            dropdown_fg_color="#ffffff",
            dropdown_hover_color="#f5f5f7",
        )
        self.node_target_combo.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            control_inner,
            text="使用提示：1. 先选择节点 2. 可先 Ping 或拉状态确认在线 3. 再校时或发送消息",
            text_color="#6b7280",
            justify="left",
            wraplength=360,
        ).pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(control_inner, fg_color="transparent", border_width=0)
        row1.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(row1, text="Ping", height=38, width=106, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.send_node_ping).pack(side="left")
        ctk.CTkButton(row1, text="拉状态", height=38, width=106, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.send_node_status_request).pack(side="right")

        row2 = ctk.CTkFrame(control_inner, fg_color="transparent", border_width=0)
        row2.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(row2, text="单点校时", height=38, width=106, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.send_node_sync_time).pack(side="left")
        ctk.CTkButton(row2, text="恢复监听", height=38, width=106, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_cmd("CMD:RESET_MODE")).pack(side="right")

        row3 = ctk.CTkFrame(control_inner, fg_color="transparent", border_width=0)
        row3.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(row3, text="群发校时", height=38, width=106, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.send_nodes_sync_time_all).pack(side="left")
        ctk.CTkButton(row3, text="开始持续广播校时", height=38, width=140, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=self.send_node_sync_time_broadcast).pack(side="right")

        row4 = ctk.CTkFrame(control_inner, fg_color="transparent", border_width=0)
        row4.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(row4, text="停止持续广播校时", height=38, width=140, corner_radius=14, fg_color="#f5f5f7", hover_color="#e6f1fc", text_color="#409eff", command=self.stop_node_sync_time_broadcast).pack(side="right")

        ctk.CTkLabel(
            control_inner,
            text="持续广播需要人工停止。可先启动广播，等现场 C3 的蜂鸣器与 LED 完成提示后再点击停止。",
            text_color="#6b7280",
            justify="left",
            wraplength=360,
        ).pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(control_inner, text="消息内容", text_color="#86868b").pack(anchor="w", pady=(4, 4))
        ctk.CTkEntry(control_inner, textvariable=self.node_message_var, placeholder_text="输入要发给节点的消息", fg_color="#f5f5f7", border_width=0, height=40, corner_radius=12).pack(fill="x")
        ctk.CTkButton(control_inner, text="发送消息", height=40, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.send_node_message).pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            control_inner,
            text="反馈说明：节点在线时通常会先收到 ACK；如果超时没有返回，会在右侧日志中显示 timeout。",
            text_color="#6b7280",
            justify="left",
            wraplength=360,
        ).pack(fill="x", pady=(10, 0))
        self._refresh_node_options()

        action_card, action_inner = self._make_soft_card(parent, "设备动作", "保留原有制卡和串口调试入口。")
        action_card.grid(row=1, column=0, sticky="nsew", padx=(8, 12), pady=(0, 8))
        ctk.CTkButton(action_inner, text="制作校时卡", height=40, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_cmd("CMD:MAKE_SYNC")).pack(fill="x", pady=(14, 8))
        ctk.CTkButton(action_inner, text="制作汇报卡", height=40, corner_radius=14, fg_color="#ecf5ff", hover_color="#d9ecff", text_color="#409eff", command=lambda: self.send_cmd("CMD:MAKE_REPORT")).pack(fill="x", pady=8)
        cmd_row = ctk.CTkFrame(action_inner, fg_color="transparent", border_width=0)
        cmd_row.pack(fill="x", pady=(16, 0))
        cmd_row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(cmd_row, textvariable=self.custom_var, placeholder_text="输入完整串口命令", fg_color="#f5f5f7", border_width=0, height=40, corner_radius=12).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(cmd_row, text="发送命令", width=96, height=40, corner_radius=14, fg_color="#409eff", hover_color="#337ecc", command=self.send_custom).grid(row=0, column=1, sticky="e")

        feedback_card, feedback_inner = self._make_soft_card(parent, "反馈日志", "按时间查看发送、ACK、状态和超时反馈。")
        feedback_card.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.network_feedback_box = ctk.CTkTextbox(
            feedback_inner,
            height=260,
            fg_color="#f5f5f7",
            text_color="#1d1d1f",
            border_width=0,
            corner_radius=12,
            font=("Consolas", 12),
        )
        self.network_feedback_box.pack(fill="both", expand=True, pady=(14, 0))
        self.network_feedback_box.insert("1.0", "暂无反馈\n")
        self.network_feedback_box.configure(state="disabled")
        if self.network_feedback_records:
            self._push_network_feedback("INFO", "ESP-NOW 控制面板已加载")
