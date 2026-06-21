import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import random

from calculation import assign_ranks, calculate_result, generate_start_list


class TestCalculateResult(unittest.TestCase):
    def setUp(self):
        self.runner = {
            "uid": "1001",
            "bib_number": "001",
            "name": "张三",
            "category": "A组",
            "route_id": 1,
        }
        self.checkpoints_map = {
            "AAAA00000001": {"cp_code": "S", "is_start": True, "is_finish": False},
            "AAAA00000002": {"cp_code": "31", "is_start": False, "is_finish": False},
            "AAAA00000003": {"cp_code": "45", "is_start": False, "is_finish": False},
            "AAAA00000004": {"cp_code": "F", "is_start": False, "is_finish": True},
        }

    def test_standard_ok(self):
        route = {"race_type": "STANDARD", "time_limit_min": None, "penalty_per_min": None}
        details = [
            {"cp_mac": "AAAA00000002", "seq_order": 1, "score_value": None},
            {"cp_mac": "AAAA00000003", "seq_order": 2, "score_value": None},
        ]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000003", 150),
            ("AAAA00000004", 200),
        ]

        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["total_seconds"], 100)

    def test_standard_mp_missing_cp(self):
        route = {"race_type": "STANDARD", "time_limit_min": None, "penalty_per_min": None}
        details = [
            {"cp_mac": "AAAA00000002", "seq_order": 1, "score_value": None},
            {"cp_mac": "AAAA00000003", "seq_order": 2, "score_value": None},
        ]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000004", 200),
        ]

        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        self.assertEqual(result["status"], "MP")

    def test_standard_dnf_missing_finish(self):
        # 有起点打卡但无终点 => DNF（未完赛）
        route = {"race_type": "STANDARD", "time_limit_min": None, "penalty_per_min": None}
        details = [{"cp_mac": "AAAA00000002", "seq_order": 1, "score_value": None}]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
        ]

        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        self.assertEqual(result["status"], "DNF")

    def test_score_with_penalty(self):
        route = {"race_type": "SCORE", "time_limit_min": 1, "penalty_per_min": 5}
        details = [
            {"cp_mac": "AAAA00000002", "seq_order": None, "score_value": 20},
            {"cp_mac": "AAAA00000003", "seq_order": None, "score_value": 30},
        ]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000003", 150),
            ("AAAA00000004", 240),
        ]

        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        # 关门 1 分钟、总用时 140s 超时 => 状态 OT
        self.assertEqual(result["status"], "OT")
        self.assertEqual(result["total_seconds"], 140)
        # base=50, overtime=80s => ceil(80/60)=2, penalty=10
        self.assertEqual(result["final_score"], 40)

    def test_dedupe_consecutive(self):
        route = {"race_type": "SCORE", "time_limit_min": 10, "penalty_per_min": 1}
        details = [{"cp_mac": "AAAA00000002", "seq_order": None, "score_value": 20}]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000002", 121),
            ("AAAA00000004", 160),
        ]

        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        self.assertEqual(result["final_score"], 20)

    def test_dns_no_punches(self):
        route = {"race_type": "STANDARD", "time_limit_min": None, "penalty_per_min": None}
        result = calculate_result("1001", [], self.runner, route, [], self.checkpoints_map)
        self.assertEqual(result["status"], "DNS")
        self.assertIsNone(result["total_seconds"])

    def test_manual_start_time_overrides_physical(self):
        # 选手手动发车时间=80，覆盖物理起点(100)，终点 200 => 用时 120
        route = {"race_type": "STANDARD", "time_limit_min": None, "penalty_per_min": None}
        details = [
            {"cp_mac": "AAAA00000002", "seq_order": 1, "score_value": None},
            {"cp_mac": "AAAA00000003", "seq_order": 2, "score_value": None},
        ]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000003", 150),
            ("AAAA00000004", 200),
        ]
        runner = dict(self.runner, start_time=80)
        result = calculate_result("1001", punches, runner, route, details, self.checkpoints_map)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["total_seconds"], 120)

    def test_standard_ot_over_time_limit(self):
        # 全部按顺序通过(OK) 但超过关门 1 分钟 => OT
        route = {"race_type": "STANDARD", "time_limit_min": 1, "penalty_per_min": None}
        details = [
            {"cp_mac": "AAAA00000002", "seq_order": 1, "score_value": None},
            {"cp_mac": "AAAA00000003", "seq_order": 2, "score_value": None},
        ]
        punches = [
            ("AAAA00000001", 100),
            ("AAAA00000002", 120),
            ("AAAA00000003", 150),
            ("AAAA00000004", 200),
        ]
        result = calculate_result("1001", punches, self.runner, route, details, self.checkpoints_map)
        self.assertEqual(result["total_seconds"], 100)
        self.assertEqual(result["status"], "OT")

    def test_assign_ranks_ties(self):
        # 用时 100/120/120/150 => 名次 1,2,2,4；非 OK 行不参与排名
        rows = [
            {"status": "OK", "total": 100},
            {"status": "OK", "total": 120},
            {"status": "OK", "total": 120},
            {"status": "OK", "total": 150},
            {"status": "DNF", "total": None},
        ]
        ranks = assign_ranks(
            rows,
            key=lambda r: r["total"],
            rankable=lambda r: r["status"] == "OK",
        )
        self.assertEqual(ranks, [1, 2, 2, 4, None])


class TestStartList(unittest.TestCase):
    CH = {"first_start_time": 1000, "interval_sec": 60, "empty_slots": 0}

    def _runners(self, units):
        return [{"uid": str(i), "unit_id": u, "group_id": 1} for i, u in enumerate(units)]

    def test_random_unique_times(self):
        runners = self._runners(["A", "B", "C", "D"])
        res, warn = generate_start_list(runners, self.CH, "random", rng=random.Random(7))
        assert warn == ""
        times = [a["start_time"] for a in res]
        self.assertEqual(len(set(times)), 4)
        for a in res:
            self.assertEqual(a["start_time"], 1000 + a["batch"] * 60)

    def test_unit_spread_no_adjacent(self):
        runners = self._runners(["A", "A", "B", "B", "C"])
        res, warn = generate_start_list(runners, self.CH, "unit_spread")
        self.assertEqual(warn, "")
        order = {a["uid"]: a["batch"] for a in res}
        seq = [r["unit_id"] for r in sorted(runners, key=lambda r: order[r["uid"]])]
        for a, b in zip(seq, seq[1:]):
            self.assertNotEqual(a, b)

    def test_unit_spread_no_solution_warns(self):
        runners = self._runners(["A", "A", "A", "B"])  # max 3 > ceil(4/2)=2
        res, warn = generate_start_list(runners, self.CH, "unit_spread")
        self.assertTrue(warn)
        self.assertEqual(len(res), 4)

    def test_empty_and_slots(self):
        self.assertEqual(generate_start_list([], self.CH, "random"), ([], ""))
        ch = dict(self.CH, empty_slots=2)
        res, _ = generate_start_list(self._runners(["A"]), ch, "random")
        self.assertEqual(res[0]["batch"], 2)
        self.assertEqual(res[0]["start_time"], 1000 + 2 * 60)


if __name__ == "__main__":
    unittest.main()
