import datetime
import struct

from math import ceil


def parse_c3_record(hex_data):
    """解析 10 字节原始足迹记录。"""
    if isinstance(hex_data, str):
        cleaned = hex_data.replace(" ", "").replace(":", "")
        hex_data = bytes.fromhex(cleaned)

    raw = bytes(hex_data)
    if len(raw) < 10:
        raise ValueError("足迹记录至少需要 10 字节")

    mac_bytes = raw[:6]
    timestamp = struct.unpack("<I", raw[6:10])[0]
    mac_compact = "".join(f"{b:02X}" for b in mac_bytes)
    mac_text = ":".join(f"{b:02X}" for b in mac_bytes)
    dt_text = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "mac": mac_text,
        "mac_key": mac_compact,
        "time": dt_text,
        "raw_ts": timestamp,
    }


def build_footprint_rows(records, location_map=None):
    """把足迹记录标准化为按时间排序的展示行。"""
    location_map = location_map or {}
    normalized = []

    for record in records or []:
        try:
            index = int(record.get("index"))
            timestamp = int(record.get("timestamp"))
        except (TypeError, ValueError, AttributeError):
            continue

        mac_key = str(record.get("mac") or "").upper()
        if not mac_key:
            continue

        normalized.append(
            {
                "uid": str(record.get("uid") or ""),
                "index": index,
                "mac": mac_key,
                "location": location_map.get(mac_key, mac_key),
                "timestamp": timestamp,
                "time_text": datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    normalized.sort(key=lambda item: (item["timestamp"], item["index"]))

    prev = None
    for row in normalized:
        if prev is None:
            row["delta_seconds"] = None
        else:
            row["delta_seconds"] = max(0, row["timestamp"] - prev["timestamp"])
        prev = row

    return normalized


def _normalize_punches(punches):
    """标准化 punches 列表。

    输入通常为 [(mac, ts), ...]，这里会：
    1) MAC 统一大写；
    2) 时间戳转 int，无法转换的记录直接丢弃；
    3) 按时间升序排序。
    """
    normalized = []
    for mac, ts in punches:
        if not mac:
            continue
        try:
            normalized.append((str(mac).upper(), int(ts)))
        except (TypeError, ValueError):
            continue
    normalized.sort(key=lambda x: x[1])
    return normalized


def _dedupe_consecutive(punches, threshold_seconds=2):
    """去重相邻重复打卡。

    同一 MAC 在短时间内连续上报通常是抖动/重复触发，
    默认在 2 秒窗口内只保留第一条。
    """
    if not punches:
        return []

    out = [punches[0]]
    for mac, ts in punches[1:]:
        prev_mac, prev_ts = out[-1]
        if mac == prev_mac and ts - prev_ts <= threshold_seconds:
            continue
        out.append((mac, ts))
    return out


def _find_start_finish(punches, checkpoints_map):
    """根据检查点角色定位起终点时间。

    - 起点取首个 is_start 的时间。
    - 终点取最后一个 is_finish 的时间。
    """
    start_ts = None
    finish_ts = None
    for mac, ts in punches:
        cp = checkpoints_map.get(mac)
        if not cp:
            continue
        if cp.get("is_start") and start_ts is None:
            start_ts = ts
        if cp.get("is_finish"):
            finish_ts = ts
    return start_ts, finish_ts


def _calc_standard(route_details, punch_macs):
    """标准赛判定（顺序通过）。

    以 route_details 中 seq_order 形成期望序列 expected，
    然后用单指针在选手打卡序列中按顺序匹配：
    - 全部匹配成功 => OK
    - 否则 => MP（漏点/顺序不完整）
    """
    expected = [
        detail["cp_mac"].upper()
        for detail in sorted(
            (d for d in route_details if d.get("seq_order") is not None),
            key=lambda x: x["seq_order"],
        )
    ]

    if not expected:
        return "OK"

    idx = 0
    for mac in punch_macs:
        if idx < len(expected) and mac == expected[idx]:
            idx += 1
    return "OK" if idx == len(expected) else "MP"


def _calc_score(route_info, route_details, punch_macs):
    """积分赛基础得分计算。

    每个点仅记一次分（同点重复打卡不叠加），
    只返回基础分，不含超时罚分。
    """
    score_map = {}
    for detail in route_details:
        score_map[detail["cp_mac"].upper()] = int(detail.get("score_value") or 0)

    seen = set()
    base_score = 0
    for mac in punch_macs:
        if mac in score_map and mac not in seen:
            base_score += score_map[mac]
            seen.add(mac)

    return base_score


def _to_int(value, default=0):
    """宽松转 int：None/空串/非法值回退到 default。"""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def calculate_result(uid, punches, runner_info, route_info, route_details, checkpoints_map):
    """统一结算入口。

    返回结构：
    - uid/start_time/finish_time/total_seconds/status/final_score

    状态机：
    - DNS：未出发（既无起点也无任何打卡）
    - DSQ：终点早于起点等异常，或有打卡但定位不到起点
    - DNF：有起点但无终点（未完赛）
    - OT ：完赛但超过关门时限（time_limit_min）
    - SCORE：基础分 - 超时罚分（按分钟向上取整）；超时则状态标 OT
    - STANDARD：按顺序判定 OK/MP；OK 但超时则标 OT

    起点时间来源：runner_info.start_time（手动发车）优先，否则取物理 is_start 打卡。
    """
    runner_info = runner_info or {}
    normalized = _normalize_punches(punches)
    deduped = _dedupe_consecutive(normalized)
    phys_start, finish_ts = _find_start_finish(deduped, checkpoints_map)

    manual_start = runner_info.get("start_time")
    manual_start = _to_int(manual_start, default=None) if manual_start not in (None, "") else None
    start_ts = manual_start if manual_start is not None else phys_start

    result = {
        "uid": uid,
        "start_time": str(start_ts) if start_ts is not None else None,
        "finish_time": str(finish_ts) if finish_ts is not None else None,
        "total_seconds": None,
        "status": "DSQ",
        "final_score": None,
    }

    has_punch = bool(deduped)
    if start_ts is None and finish_ts is None and not has_punch:
        result["status"] = "DNS"
        return result
    if start_ts is not None and finish_ts is not None and finish_ts < start_ts:
        result["status"] = "DSQ"
        return result
    if start_ts is None:
        # 有打卡但找不到起点（缺起点配置/未打起点）
        result["status"] = "DSQ"
        return result
    if finish_ts is None:
        result["status"] = "DNF"
        return result

    total_seconds = finish_ts - start_ts
    result["total_seconds"] = int(total_seconds)

    punch_macs = [mac for mac, _ in deduped]
    race_type = (route_info.get("race_type") or "STANDARD").upper()
    time_limit_min = _to_int(route_info.get("time_limit_min"))
    overtime = time_limit_min > 0 and total_seconds > time_limit_min * 60

    if race_type == "SCORE":
        base_score = _calc_score(route_info, route_details, punch_macs)
        penalty_per_min = _to_int(route_info.get("penalty_per_min"))

        # 超时分钟按向上取整处理，例如超时 1 秒也计 1 分钟。
        overtime_seconds = max(0, total_seconds - time_limit_min * 60) if time_limit_min > 0 else 0
        overtime_minutes = ceil(overtime_seconds / 60) if overtime_seconds > 0 else 0
        penalty = overtime_minutes * penalty_per_min

        result["status"] = "OT" if overtime else "OK"
        result["final_score"] = int(base_score - penalty)
        return result

    base_status = _calc_standard(route_details, punch_macs)
    result["status"] = "OT" if (base_status == "OK" and overtime) else base_status
    return result


def _spread_by_key(items, key):
    """把 items 按 key 尽量分散（标准「相邻不相同」排布）。

    返回 (排好序的列表, warning_bool)。当某个 key 数量 > ceil(n/2) 时无法
    完全避免相邻相同，warning=True，但仍给出尽量分散的结果。
    """
    from collections import defaultdict

    buckets = defaultdict(list)
    for it in items:
        buckets[key(it)].append(it)
    order = sorted(buckets.keys(), key=lambda k: (-len(buckets[k]), str(k)))
    n = len(items)
    max_size = max((len(v) for v in buckets.values()), default=0)
    warn = max_size > (n + 1) // 2
    positions = list(range(0, n, 2)) + list(range(1, n, 2))
    result = [None] * n
    pi = 0
    for k in order:
        for it in buckets[k]:
            result[positions[pi]] = it
            pi += 1
    return result, warn


def generate_start_list(runners, channel, algorithm="random", rng=None):
    """生成出发时刻表。

    - runners：dict 列表，需含 uid / unit_id / group_id。
    - channel：dict，含 first_start_time(unix)/interval_sec/empty_slots。
    - algorithm：random（完全随机）/ unit_spread（同单位不相邻）/ group_unit_spread（同组别同单位不相邻）。
    返回 (assignments, warning)；assignments=[{uid, batch, start_time}]。
    出发时间 = 首发时间 + 批次×间隔；空位数量在批次号前预留。
    """
    import random as _random

    rng = rng or _random.Random()
    items = list(runners or [])
    if not items:
        return [], ""

    warning = ""
    algo = (algorithm or "random").lower()
    if algo == "random":
        rng.shuffle(items)
    elif algo == "unit_spread":
        items, warn = _spread_by_key(items, lambda r: r.get("unit_id"))
        if warn:
            warning = "部分单位人数过多，无法完全避免相邻同单位，已尽量分散。"
    elif algo == "group_unit_spread":
        from collections import OrderedDict

        grouped = OrderedDict()
        for r in items:
            grouped.setdefault(r.get("group_id"), []).append(r)
        ordered, warn_any = [], False
        for members in grouped.values():
            spread, warn = _spread_by_key(members, lambda r: r.get("unit_id"))
            ordered.extend(spread)
            warn_any = warn_any or warn
        items = ordered
        if warn_any:
            warning = "部分组别内单位人数过多，无法完全避免相邻同单位，已尽量分散。"

    interval = channel.get("interval_sec") or 0
    first = channel.get("first_start_time")
    empty = channel.get("empty_slots") or 0
    assignments = []
    for i, runner in enumerate(items):
        batch = empty + i
        start_time = (first + batch * interval) if (first is not None and interval) else None
        assignments.append({"uid": runner.get("uid"), "batch": batch, "start_time": start_time})
    return assignments, warning


def assign_ranks(rows, key, rankable=None):
    """对已排序成绩分配名次（标准竞赛式并列：1,2,2,4）。

    - rows：已按名次顺序排好的成绩列表。
    - key：取「名次可比字段」的函数；相邻 key 相等者并列同名次。
    - rankable：判定该行是否参与排名（如仅 OK/OT），不参与者名次为 None。
    返回与 rows 等长的名次列表（int 或 None）。
    """
    if rankable is None:
        def rankable(_row):
            return True

    ranks = []
    counted = 0
    position = 0
    prev_key = object()
    for row in rows:
        if not rankable(row):
            ranks.append(None)
            continue
        counted += 1
        current = key(row)
        if current != prev_key:
            position = counted
            prev_key = current
        ranks.append(position)
    return ranks
