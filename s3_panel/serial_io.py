"""串口后台读写线程与生命周期管理。"""

import threading
import time

import serial


class SerialWorker:
    """串口后台线程。

    - connect/disconnect 管理串口生命周期
    - _read_loop 持续读取并通过回调上报
    - send 负责线程安全写入
    """

    def __init__(self, on_line, on_state):
        self._ser = None
        self._thread = None
        self._running = False
        self._on_line = on_line
        self._on_state = on_state
        self._lock = threading.Lock()

    @property
    def is_connected(self):
        return self._ser is not None and self._ser.is_open

    def connect(self, port: str, baudrate: int):
        if self.is_connected:
            return
        self._ser = serial.Serial(port=port, baudrate=baudrate, timeout=0.2)
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        self._on_state(True, f"Connected: {port} @ {baudrate}")

    def disconnect(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None
        self._on_state(False, "Disconnected")

    def send(self, line: str):
        if not self.is_connected:
            raise RuntimeError("Serial port is not connected")
        payload = line.strip()
        if not payload:
            return
        if not payload.endswith("\n"):
            payload += "\n"
        with self._lock:
            self._ser.write(payload.encode("utf-8", errors="ignore"))

    def _read_loop(self):
        while self._running and self._ser and self._ser.is_open:
            try:
                if self._ser.in_waiting > 0:
                    line = self._ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        self._on_line(line)
                else:
                    time.sleep(0.02)
            except Exception as exc:  # noqa: BLE001
                self._on_line(f"[SERIAL_ERROR] {exc}")
                break
        self._running = False
