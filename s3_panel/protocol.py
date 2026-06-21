"""串口文本协议解析。"""

import re
from dataclasses import dataclass
from urllib.parse import unquote_plus



LOCAL_SCAN_RE = re.compile(r"^LOCAL_SCAN:(?P<uid>\d+)$")
NODE_SCAN_RE = re.compile(r"^NODE_SCAN:MAC=(?P<mac>[0-9A-Fa-f]{12}),NODE=(?P<node_id>\d+),UID=(?P<uid>\d+)$")
NODE_SCAN_ID_RE = re.compile(r"^NODE_SCAN:(?P<node_id>\d+),(?P<uid>\d+)$")
NODE_SCAN_MAC_RE = re.compile(r"^NODE_SCAN:(?P<mac>[0-9A-Fa-f]{12}),(?P<uid>\d+)$")
NODE_ACK_RE = re.compile(r"^NODE_ACK:MAC=(?P<mac>[0-9A-Fa-f]{12}),NODE=(?P<node_id>\d+),SEQ=(?P<seq>\d+),CMD=(?P<cmd>[A-Z_]+),OK=(?P<ok>[01]),MSG=(?P<msg>.*)$")
NODE_STATUS_RE = re.compile(r"^NODE_STATUS:MAC=(?P<mac>[0-9A-Fa-f]{12}),NODE=(?P<node_id>\d+),NTP=(?P<ntp>[01]),BAT=(?P<bat>\d+),TIME=(?P<ts>\d+)$")
ESPNOW_RX_TIME_REQUEST_RE = re.compile(r"^ESPNOW_RX:TYPE=TIME_REQUEST,FROM=(?P<from_mac>[0-9A-Fa-f]{12})$")
ESPNOW_RX_STATUS_REPORT_RE = re.compile(r"^ESPNOW_RX:TYPE=STATUS_REPORT,FROM=(?P<from_mac>[0-9A-Fa-f]{12}),MAC=(?P<mac>[0-9A-Fa-f]{12}),ROLE=(?P<role>\d+),SYNC_OK=(?P<sync_ok>[01]),RTC=(?P<rtc>\d+),LAST_SYNC=(?P<last_sync>\d+),BAT=(?P<bat>\d+)$")
ESPNOW_TX_TIME_RESPONSE_RE = re.compile(r"^ESPNOW_TX:TYPE=TIME_RESPONSE,MODE=(?P<mode>[A-Z]+),(?:TO=(?P<to_mac>[0-9A-Fa-f]{12}),UNIX=(?P<unix>\d+)|COUNT=(?P<count>\d+),UNIX=(?P<unix_count>\d+))$")
ESPNOW_ERR_RE = re.compile(r"^ESPNOW_ERR:(?:MODE=(?P<mode>[A-Z]+),)?FROM=(?P<from_mac>[0-9A-Fa-fA-Z]+),LEN=(?P<len>\d+),REASON=(?P<reason>[^,]+)(?:,NODE_MAC=(?P<node_mac>[0-9A-Fa-f]{12}))?$")
CARD_INFO_RE = re.compile(r"^CARD_INFO:UID=(?P<uid>\d+),TYPE=(?P<card_type>.+)$")
SYS_MODE_RE = re.compile(r"^SYS_MODE:(?P<mode>[A-Z_]+)$")
SYS_MSG_RE = re.compile(r"^SYS_MSG:(?P<msg>.+)$")
STATUS_RE = re.compile(r"^STATUS:WIFI=(?P<wifi>[01]),SSID=(?P<ssid>.*),TIME=(?P<ts>\d+)$")
HEARTBEAT_RE = re.compile(r"^HEARTBEAT:time=(?P<time>[^,]+),unix=(?P<unix>\d+)$")
HEARTBEAT_NOT_SYNCED_RE = re.compile(r"^HEARTBEAT:time_not_synced,unix=(?P<unix>\d+)$")
READOUT_RE = re.compile(r"^READOUT:UID=(?P<uid>\d+),PUNCHES=\[(?P<punches>.*)\]$")
WRITE_OK_RE = re.compile(r"^WRITE_OK:(?P<uid>\d+)$")
WRITE_FAIL_RE = re.compile(r"^WRITE_FAIL(?::(?P<uid>\d+))?$")


@dataclass
class ParsedEvent:
    """串口文本协议解析后的统一事件对象。"""

    event_type: str
    payload: dict



def parse_line(line: str) -> ParsedEvent:
    """把一行串口文本解析为结构化事件。

    解析失败不会抛错，统一返回 event_type="raw" 交给上层记录。
    """
    line = line.strip()
    if not line:
        return ParsedEvent("empty", {})

    m = STATUS_RE.match(line)
    if m:
        return ParsedEvent(
            "status",
            {"wifi": int(m.group("wifi")), "ssid": m.group("ssid"), "timestamp": int(m.group("ts"))},
        )

    m = LOCAL_SCAN_RE.match(line)
    if m:
        return ParsedEvent("local_scan", {"uid": m.group("uid")})

    m = NODE_SCAN_RE.match(line)
    if m:
        return ParsedEvent(
            "node_scan",
            {"mac": m.group("mac").upper(), "node_id": m.group("node_id"), "uid": m.group("uid")},
        )

    m = NODE_SCAN_ID_RE.match(line)
    if m:
        return ParsedEvent("node_scan", {"node_id": m.group("node_id"), "uid": m.group("uid")})

    m = NODE_SCAN_MAC_RE.match(line)
    if m:
        return ParsedEvent("node_scan", {"mac": m.group("mac").upper(), "uid": m.group("uid")})

    m = NODE_ACK_RE.match(line)
    if m:
        return ParsedEvent(
            "node_ack",
            {
                "mac": m.group("mac").upper(),
                "node_id": m.group("node_id"),
                "seq": int(m.group("seq")),
                "cmd": m.group("cmd"),
                "ok": int(m.group("ok")),
                "msg": _decode_url_text(m.group("msg")),
            },
        )

    m = NODE_STATUS_RE.match(line)
    if m:
        return ParsedEvent(
            "node_status",
            {
                "mac": m.group("mac").upper(),
                "node_id": m.group("node_id"),
                "ntp": int(m.group("ntp")),
                "battery": int(m.group("bat")),
                "timestamp": int(m.group("ts")),
            },
        )

    m = ESPNOW_RX_TIME_REQUEST_RE.match(line)
    if m:
        return ParsedEvent("espnow_rx", {"msg_type": "TIME_REQUEST", "from_mac": m.group("from_mac").upper()})

    m = ESPNOW_RX_STATUS_REPORT_RE.match(line)
    if m:
        return ParsedEvent(
            "espnow_rx",
            {
                "msg_type": "STATUS_REPORT",
                "from_mac": m.group("from_mac").upper(),
                "mac": m.group("mac").upper(),
                "role": int(m.group("role")),
                "last_sync_ok": int(m.group("sync_ok")),
                "rtc_timestamp": int(m.group("rtc")),
                "last_sync_timestamp": int(m.group("last_sync")),
                "battery_mv": int(m.group("bat")),
            },
        )

    m = ESPNOW_TX_TIME_RESPONSE_RE.match(line)
    if m:
        payload = {
            "msg_type": "TIME_RESPONSE",
            "mode": m.group("mode"),
            "unix": int(m.group("unix") or m.group("unix_count")),
        }
        if m.group("to_mac"):
            payload["to_mac"] = m.group("to_mac").upper()
        if m.group("count"):
            payload["count"] = int(m.group("count"))
        return ParsedEvent("espnow_tx", payload)

    m = ESPNOW_ERR_RE.match(line)
    if m:
        payload = {
            "mode": (m.group("mode") or "UNKNOWN").upper(),
            "from_mac": m.group("from_mac").upper(),
            "length": int(m.group("len")),
            "reason": m.group("reason"),
        }
        if m.group("node_mac"):
            payload["node_mac"] = m.group("node_mac").upper()
        return ParsedEvent("espnow_err", payload)

    m = CARD_INFO_RE.match(line)
    if m:
        return ParsedEvent("card_info", {"uid": m.group("uid"), "card_type": m.group("card_type")})

    m = SYS_MODE_RE.match(line)
    if m:
        return ParsedEvent("sys_mode", {"mode": m.group("mode")})

    m = SYS_MSG_RE.match(line)
    if m:
        return ParsedEvent("sys_msg", {"msg": m.group("msg")})

    m = HEARTBEAT_RE.match(line)
    if m:
        return ParsedEvent("heartbeat", {"time": m.group("time"), "unix": m.group("unix")})

    m = HEARTBEAT_NOT_SYNCED_RE.match(line)
    if m:
        return ParsedEvent("heartbeat", {"time": "not_synced", "unix": m.group("unix")})

    m = READOUT_RE.match(line)
    if m:
        return ParsedEvent("readout", {"uid": m.group("uid"), "punches": _parse_punches(m.group("punches"))})

    m = WRITE_OK_RE.match(line)
    if m:
        return ParsedEvent("write_ok", {"uid": m.group("uid")})

    m = WRITE_FAIL_RE.match(line)
    if m:
        payload = {}
        if m.group("uid"):
            payload["uid"] = m.group("uid")
        return ParsedEvent("write_fail", payload)

    if line.startswith("MAKE_SUCCESS:"):
        return ParsedEvent("make_success", {"msg": line})

    if line.startswith("MAKE_FAIL:"):
        return ParsedEvent("make_fail", {"msg": line})

    return ParsedEvent("raw", {"line": line})


def _parse_punches(punches_text: str):
    """解析 READOUT 中的 punches 字段，输出 [(MAC, ts), ...]。"""
    punches = []
    if not punches_text.strip():
        return punches

    for item in punches_text.split(","):
        token = item.strip()
        if not token or ":" not in token:
            continue
        mac, ts = token.split(":", 1)
        mac = mac.strip().upper()
        ts = ts.strip()
        if not mac:
            continue
        try:
            punches.append((mac, int(ts)))
        except ValueError:
            continue
    return punches


def _decode_url_text(value: str) -> str:
    try:
        return unquote_plus(value or "")
    except Exception:  # noqa: BLE001
        return value or ""
