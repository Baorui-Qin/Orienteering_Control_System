"""基于 SQLite 的比赛数据持久层（多赛事 / event 隔离）。"""

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


SCHEMA_VERSION = 2
DEFAULT_EVENT_ID = 1


class RaceDatabase:
    """SQLite 持久层。

    负责赛事、选手、路线、检查点、清算结果、改判审计与原始扫描流水的 CRUD。
    所有业务数据按 ``event_id`` 隔离，默认作用于 ``self.current_event_id``。
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = OFF")
        # 迁移期间自管事务，保证一次性原子完成。
        self.conn.isolation_level = None
        self._migrate()
        self.conn.isolation_level = ""  # 恢复默认：DML 自动开启事务
        self.current_event_id = DEFAULT_EVENT_ID
        self._ensure_default_event()

    # ------------------------------------------------------------------
    # 迁移
    # ------------------------------------------------------------------
    def _migrate(self):
        version = self.conn.execute("PRAGMA user_version").fetchone()[0]
        if version >= SCHEMA_VERSION:
            return

        tables = {r["name"] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        legacy = "runners" in tables and not self._has_column("runners", "event_id")
        # 升级既有库（旧 schema 或已建过的版本库）前先备份；空白新库不备份。
        if legacy or (version >= 1 and version < SCHEMA_VERSION):
            self._backup_legacy_db()

        self.conn.execute("BEGIN")
        try:
            if version < 1:
                self._migrate_to_v1(tables)
            if version < 2:
                self._migrate_to_v2()
            self.conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def _migrate_to_v1(self, tables):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_date TEXT,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL
            )
            """
        )
        if "runners" not in tables:
            self._create_core_tables()
        elif "runners" in tables and not self._has_column("runners", "event_id"):
            self._migrate_legacy_core()
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS result_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                uid TEXT NOT NULL,
                field TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

    def _migrate_to_v2(self):
        """新增 单位 / 通道 / 组别 表，并给 runners 补出发相关列。"""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS units (
                event_id INTEGER NOT NULL DEFAULT 1,
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS channels (
                event_id INTEGER NOT NULL DEFAULT 1,
                channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                first_start_time INTEGER,
                interval_sec INTEGER,
                empty_slots INTEGER
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                event_id INTEGER NOT NULL DEFAULT 1,
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                route_id INTEGER,
                limit_min INTEGER,
                start_mode TEXT,
                channel_id INTEGER,
                seq_order INTEGER
            )
            """
        )
        for col, decl in (("unit_id", "INTEGER"), ("group_id", "INTEGER"), ("start_batch", "INTEGER"), ("gender", "TEXT")):
            if not self._has_column("runners", col):
                self.conn.execute(f"ALTER TABLE runners ADD COLUMN {col} {decl}")

    def _has_column(self, table: str, column: str) -> bool:
        cols = {r["name"] for r in self.conn.execute(f"PRAGMA table_info({table})")}
        return column in cols

    def _backup_legacy_db(self):
        if not self.db_path.exists():
            return
        backup = self.db_path.with_suffix(self.db_path.suffix + ".bak")
        try:
            shutil.copy2(self.db_path, backup)
        except OSError:
            # 备份失败不阻断迁移，但已尽量保护原库。
            pass

    def _create_core_tables(self):
        """在全新库上直接建 v1 结构。"""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL,
                node_id TEXT,
                uid TEXT NOT NULL,
                person_name TEXT,
                status TEXT NOT NULL,
                card_type TEXT
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runners (
                event_id INTEGER NOT NULL DEFAULT 1,
                uid TEXT NOT NULL,
                bib_number TEXT,
                name TEXT,
                category TEXT,
                route_id INTEGER,
                start_time INTEGER,
                PRIMARY KEY (event_id, uid)
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checkpoints (
                event_id INTEGER NOT NULL DEFAULT 1,
                mac TEXT NOT NULL,
                cp_code TEXT,
                is_start INTEGER NOT NULL DEFAULT 0,
                is_finish INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (event_id, mac)
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS routes (
                event_id INTEGER NOT NULL DEFAULT 1,
                route_id INTEGER NOT NULL,
                route_name TEXT,
                race_type TEXT NOT NULL,
                time_limit_min INTEGER,
                penalty_per_min INTEGER,
                PRIMARY KEY (event_id, route_id)
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS route_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL DEFAULT 1,
                route_id INTEGER NOT NULL,
                cp_mac TEXT NOT NULL,
                seq_order INTEGER,
                score_value INTEGER
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                event_id INTEGER NOT NULL DEFAULT 1,
                uid TEXT NOT NULL,
                start_time TEXT,
                finish_time TEXT,
                total_seconds INTEGER,
                status TEXT NOT NULL,
                final_score INTEGER,
                raw_data TEXT,
                updated_at TEXT NOT NULL,
                manual_status TEXT,
                penalty_adjust INTEGER,
                manual_start_time INTEGER,
                manual_finish_time INTEGER,
                judge_note TEXT,
                sync_warning TEXT,
                PRIMARY KEY (event_id, uid)
            )
            """
        )

    def _migrate_legacy_core(self):
        """把 v0 旧表（无 event_id）重建为 v1 结构，存量数据归入默认赛事。"""
        # runners / checkpoints / routes / results 主键变化，需重建。
        self.conn.execute("ALTER TABLE runners RENAME TO runners_old")
        self.conn.execute("ALTER TABLE checkpoints RENAME TO checkpoints_old")
        self.conn.execute("ALTER TABLE routes RENAME TO routes_old")
        self.conn.execute("ALTER TABLE results RENAME TO results_old")
        self._create_core_tables()
        self.conn.execute(
            "INSERT INTO runners(event_id, uid, bib_number, name, category, route_id, start_time) "
            "SELECT 1, uid, bib_number, name, category, route_id, NULL FROM runners_old"
        )
        self.conn.execute(
            "INSERT INTO checkpoints(event_id, mac, cp_code, is_start, is_finish) "
            "SELECT 1, mac, cp_code, is_start, is_finish FROM checkpoints_old"
        )
        self.conn.execute(
            "INSERT INTO routes(event_id, route_id, route_name, race_type, time_limit_min, penalty_per_min) "
            "SELECT 1, route_id, route_name, race_type, time_limit_min, penalty_per_min FROM routes_old"
        )
        self.conn.execute(
            "INSERT INTO results(event_id, uid, start_time, finish_time, total_seconds, status, final_score, raw_data, updated_at) "
            "SELECT 1, uid, start_time, finish_time, total_seconds, status, final_score, raw_data, updated_at FROM results_old"
        )
        self.conn.execute("DROP TABLE runners_old")
        self.conn.execute("DROP TABLE checkpoints_old")
        self.conn.execute("DROP TABLE routes_old")
        self.conn.execute("DROP TABLE results_old")
        # scans / route_details 仅需补列。
        self.conn.execute("ALTER TABLE scans ADD COLUMN event_id INTEGER NOT NULL DEFAULT 1")
        self.conn.execute("ALTER TABLE route_details ADD COLUMN event_id INTEGER NOT NULL DEFAULT 1")

    def _ensure_default_event(self):
        row = self.conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()
        if row["n"] == 0:
            self.conn.execute(
                "INSERT INTO events(event_id, name, event_date, status, created_at) VALUES (?, ?, ?, 'active', ?)",
                (DEFAULT_EVENT_ID, "默认赛事", None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            self.conn.commit()

    def _eid(self, event_id):
        return self.current_event_id if event_id is None else int(event_id)

    # ------------------------------------------------------------------
    # 赛事管理
    # ------------------------------------------------------------------
    def set_current_event(self, event_id: int):
        self.current_event_id = int(event_id)

    def list_events(self):
        cur = self.conn.execute(
            "SELECT event_id, name, event_date, status, created_at FROM events ORDER BY event_id ASC"
        )
        return [dict(r) for r in cur.fetchall()]

    def get_event(self, event_id: int):
        cur = self.conn.execute(
            "SELECT event_id, name, event_date, status, created_at FROM events WHERE event_id = ?",
            (int(event_id),),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def create_event(self, name: str, event_date=None) -> int:
        cur = self.conn.execute(
            "INSERT INTO events(name, event_date, status, created_at) VALUES (?, ?, 'active', ?)",
            (name, event_date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def rename_event(self, event_id: int, name: str, event_date=None):
        self.conn.execute(
            "UPDATE events SET name = ?, event_date = ? WHERE event_id = ?",
            (name, event_date, int(event_id)),
        )
        self.conn.commit()

    def set_event_status(self, event_id: int, status: str):
        self.conn.execute("UPDATE events SET status = ? WHERE event_id = ?", (status, int(event_id)))
        self.conn.commit()

    def archive_event(self, event_id: int):
        self.set_event_status(event_id, "archived")

    def delete_event(self, event_id: int):
        """删除赛事及其全部业务数据。"""
        eid = int(event_id)
        for table in ("scans", "runners", "checkpoints", "routes", "route_details", "results",
                      "result_adjustments", "units", "channels", "groups"):
            self.conn.execute(f"DELETE FROM {table} WHERE event_id = ?", (eid,))
        self.conn.execute("DELETE FROM events WHERE event_id = ?", (eid,))
        self.conn.commit()

    # ------------------------------------------------------------------
    # 扫描流水
    # ------------------------------------------------------------------
    def insert_scan(self, timestamp: str, node_id: str, uid: str, person_name: str, status: str, card_type: str, event_id=None):
        self.conn.execute(
            "INSERT INTO scans (event_id, timestamp, node_id, uid, person_name, status, card_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self._eid(event_id), timestamp, node_id, uid, person_name, status, card_type),
        )
        self.conn.commit()

    def list_all(self, event_id=None):
        cur = self.conn.execute(
            "SELECT timestamp, node_id, uid, person_name, status, card_type FROM scans WHERE event_id = ? ORDER BY id ASC",
            (self._eid(event_id),),
        )
        return cur.fetchall()

    # ------------------------------------------------------------------
    # 选手
    # ------------------------------------------------------------------
    _RUNNER_COLS = "uid, bib_number, name, category, route_id, start_time, unit_id, group_id, start_batch, gender"

    def get_runner(self, uid: str, event_id=None):
        cur = self.conn.execute(
            f"SELECT {self._RUNNER_COLS} FROM runners WHERE event_id = ? AND uid = ?",
            (self._eid(event_id), uid),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def upsert_runner(self, uid: str, bib_number: str, name: str, category: str, route_id, start_time=None,
                      unit_id=None, group_id=None, start_batch=None, gender=None, event_id=None):
        self.conn.execute(
            """
            INSERT INTO runners (event_id, uid, bib_number, name, category, route_id, start_time, unit_id, group_id, start_batch, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, uid) DO UPDATE SET
                bib_number = excluded.bib_number,
                name = excluded.name,
                category = excluded.category,
                route_id = excluded.route_id,
                start_time = excluded.start_time,
                unit_id = excluded.unit_id,
                group_id = excluded.group_id,
                start_batch = excluded.start_batch,
                gender = excluded.gender
            """,
            (self._eid(event_id), uid, bib_number, name, category, route_id, start_time, unit_id, group_id, start_batch, gender),
        )
        self.conn.commit()

    def list_runners(self, event_id=None):
        cur = self.conn.execute(
            f"SELECT {self._RUNNER_COLS} FROM runners WHERE event_id = ? ORDER BY bib_number ASC, uid ASC",
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def set_runner_start(self, uid: str, start_time, start_batch=None, event_id=None):
        """发车表回写：仅更新出发时间与批次。"""
        self.conn.execute(
            "UPDATE runners SET start_time = ?, start_batch = ? WHERE event_id = ? AND uid = ?",
            (start_time, start_batch, self._eid(event_id), uid),
        )
        self.conn.commit()

    def delete_runner(self, uid: str, event_id=None):
        self.conn.execute("DELETE FROM runners WHERE event_id = ? AND uid = ?", (self._eid(event_id), uid))
        self.conn.commit()

    # ------------------------------------------------------------------
    # 路线
    # ------------------------------------------------------------------
    def get_route(self, route_id: int, event_id=None):
        cur = self.conn.execute(
            "SELECT route_id, route_name, race_type, time_limit_min, penalty_per_min FROM routes WHERE event_id = ? AND route_id = ?",
            (self._eid(event_id), route_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def upsert_route(self, route_id: int, route_name: str, race_type: str, time_limit_min, penalty_per_min, event_id=None):
        self.conn.execute(
            """
            INSERT INTO routes (event_id, route_id, route_name, race_type, time_limit_min, penalty_per_min)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, route_id) DO UPDATE SET
                route_name = excluded.route_name,
                race_type = excluded.race_type,
                time_limit_min = excluded.time_limit_min,
                penalty_per_min = excluded.penalty_per_min
            """,
            (self._eid(event_id), route_id, route_name, race_type, time_limit_min, penalty_per_min),
        )
        self.conn.commit()

    def list_routes(self, event_id=None):
        cur = self.conn.execute(
            "SELECT route_id, route_name, race_type, time_limit_min, penalty_per_min FROM routes WHERE event_id = ? ORDER BY route_id ASC",
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def delete_route(self, route_id: int, event_id=None):
        eid = self._eid(event_id)
        self.conn.execute("DELETE FROM route_details WHERE event_id = ? AND route_id = ?", (eid, route_id))
        self.conn.execute("UPDATE runners SET route_id = NULL WHERE event_id = ? AND route_id = ?", (eid, route_id))
        self.conn.execute("DELETE FROM routes WHERE event_id = ? AND route_id = ?", (eid, route_id))
        self.conn.commit()

    def list_route_details(self, route_id: int, event_id=None):
        cur = self.conn.execute(
            "SELECT id, route_id, cp_mac, seq_order, score_value FROM route_details WHERE event_id = ? AND route_id = ?",
            (self._eid(event_id), route_id),
        )
        return [dict(r) for r in cur.fetchall()]

    def add_route_detail(self, route_id: int, cp_mac: str, seq_order, score_value, event_id=None):
        self.conn.execute(
            "INSERT INTO route_details (event_id, route_id, cp_mac, seq_order, score_value) VALUES (?, ?, ?, ?, ?)",
            (self._eid(event_id), route_id, cp_mac.upper(), seq_order, score_value),
        )
        self.conn.commit()

    def delete_route_detail(self, detail_id: int, event_id=None):
        self.conn.execute(
            "DELETE FROM route_details WHERE id = ? AND event_id = ?",
            (detail_id, self._eid(event_id)),
        )
        self.conn.commit()

    def replace_route_details(self, route_id: int, details: list, event_id=None):
        eid = self._eid(event_id)
        self.conn.execute("DELETE FROM route_details WHERE event_id = ? AND route_id = ?", (eid, route_id))
        for d in details:
            self.conn.execute(
                "INSERT INTO route_details (event_id, route_id, cp_mac, seq_order, score_value) VALUES (?, ?, ?, ?, ?)",
                (eid, route_id, d["cp_mac"].upper(), d.get("seq_order"), d.get("score_value")),
            )
        self.conn.commit()

    # ------------------------------------------------------------------
    # 检查点
    # ------------------------------------------------------------------
    def upsert_checkpoint(self, mac: str, cp_code: str, is_start: bool, is_finish: bool, event_id=None):
        self.conn.execute(
            """
            INSERT INTO checkpoints (event_id, mac, cp_code, is_start, is_finish)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(event_id, mac) DO UPDATE SET
                cp_code = excluded.cp_code,
                is_start = excluded.is_start,
                is_finish = excluded.is_finish
            """,
            (self._eid(event_id), mac.upper(), cp_code, int(bool(is_start)), int(bool(is_finish))),
        )
        self.conn.commit()

    def list_checkpoints(self, event_id=None):
        cur = self.conn.execute(
            "SELECT mac, cp_code, is_start, is_finish FROM checkpoints WHERE event_id = ? ORDER BY cp_code ASC, mac ASC",
            (self._eid(event_id),),
        )
        rows = []
        for r in cur.fetchall():
            rows.append(
                {
                    "mac": r["mac"],
                    "cp_code": r["cp_code"],
                    "is_start": bool(r["is_start"]),
                    "is_finish": bool(r["is_finish"]),
                }
            )
        return rows

    def delete_checkpoint(self, mac: str, event_id=None):
        self.conn.execute("DELETE FROM checkpoints WHERE event_id = ? AND mac = ?", (self._eid(event_id), mac.upper()))
        self.conn.commit()

    def get_checkpoints_map(self, event_id=None):
        cur = self.conn.execute(
            "SELECT mac, cp_code, is_start, is_finish FROM checkpoints WHERE event_id = ?",
            (self._eid(event_id),),
        )
        out = {}
        for row in cur.fetchall():
            out[row["mac"].upper()] = {
                "cp_code": row["cp_code"],
                "is_start": bool(row["is_start"]),
                "is_finish": bool(row["is_finish"]),
            }
        return out

    # ------------------------------------------------------------------
    # 成绩
    # ------------------------------------------------------------------
    def list_results_with_runner(self, event_id=None):
        cur = self.conn.execute(
            """
            SELECT
                results.uid,
                results.event_id,
                runners.bib_number,
                runners.name,
                runners.category,
                runners.route_id,
                runners.start_time AS runner_start_time,
                routes.race_type,
                routes.time_limit_min,
                routes.penalty_per_min,
                results.status,
                results.final_score,
                results.total_seconds,
                results.start_time,
                results.finish_time,
                results.raw_data,
                results.updated_at,
                results.manual_status,
                results.penalty_adjust,
                results.manual_start_time,
                results.manual_finish_time,
                results.judge_note,
                results.sync_warning
            FROM results
            LEFT JOIN runners ON runners.event_id = results.event_id AND runners.uid = results.uid
            LEFT JOIN routes ON routes.event_id = results.event_id AND routes.route_id = runners.route_id
            WHERE results.event_id = ?
            ORDER BY results.updated_at DESC
            """,
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_result(self, uid: str, event_id=None):
        cur = self.conn.execute(
            "SELECT * FROM results WHERE event_id = ? AND uid = ?",
            (self._eid(event_id), uid),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def upsert_result(self, result: dict, event_id=None):
        """写入/更新计算结果。仅触碰计算列，保留裁判改判列（manual_*）。"""
        self.conn.execute(
            """
            INSERT INTO results (event_id, uid, start_time, finish_time, total_seconds, status, final_score, raw_data, updated_at, sync_warning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, uid) DO UPDATE SET
                start_time = excluded.start_time,
                finish_time = excluded.finish_time,
                total_seconds = excluded.total_seconds,
                status = excluded.status,
                final_score = excluded.final_score,
                raw_data = excluded.raw_data,
                updated_at = excluded.updated_at,
                sync_warning = excluded.sync_warning
            """,
            (
                self._eid(event_id),
                result["uid"],
                result.get("start_time"),
                result.get("finish_time"),
                result.get("total_seconds"),
                result["status"],
                result.get("final_score"),
                result.get("raw_data"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                result.get("sync_warning"),
            ),
        )
        self.conn.commit()

    def update_result_overrides(self, uid: str, manual_status, penalty_adjust, manual_start_time, manual_finish_time, judge_note, event_id=None):
        """写入裁判改判覆盖列。"""
        self.conn.execute(
            """
            UPDATE results SET
                manual_status = ?,
                penalty_adjust = ?,
                manual_start_time = ?,
                manual_finish_time = ?,
                judge_note = ?,
                updated_at = ?
            WHERE event_id = ? AND uid = ?
            """,
            (
                manual_status,
                penalty_adjust,
                manual_start_time,
                manual_finish_time,
                judge_note,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self._eid(event_id),
                uid,
            ),
        )
        self.conn.commit()

    def add_result_adjustment(self, uid: str, field: str, old_value, new_value, note: str, event_id=None):
        self.conn.execute(
            "INSERT INTO result_adjustments (event_id, uid, field, old_value, new_value, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self._eid(event_id),
                uid,
                field,
                None if old_value is None else str(old_value),
                None if new_value is None else str(new_value),
                note,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        self.conn.commit()

    def list_result_adjustments(self, uid=None, event_id=None):
        if uid is None:
            cur = self.conn.execute(
                "SELECT id, uid, field, old_value, new_value, note, created_at FROM result_adjustments WHERE event_id = ? ORDER BY id DESC",
                (self._eid(event_id),),
            )
        else:
            cur = self.conn.execute(
                "SELECT id, uid, field, old_value, new_value, note, created_at FROM result_adjustments WHERE event_id = ? AND uid = ? ORDER BY id DESC",
                (self._eid(event_id), uid),
            )
        return [dict(r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # 单位
    # ------------------------------------------------------------------
    def list_units(self, event_id=None):
        cur = self.conn.execute(
            "SELECT unit_id, name FROM units WHERE event_id = ? ORDER BY name ASC",
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def upsert_unit(self, name: str, unit_id=None, event_id=None) -> int:
        eid = self._eid(event_id)
        if unit_id:
            self.conn.execute("UPDATE units SET name = ? WHERE event_id = ? AND unit_id = ?", (name, eid, int(unit_id)))
            self.conn.commit()
            return int(unit_id)
        cur = self.conn.execute("INSERT INTO units (event_id, name) VALUES (?, ?)", (eid, name))
        self.conn.commit()
        return int(cur.lastrowid)

    def delete_unit(self, unit_id: int, event_id=None):
        eid = self._eid(event_id)
        self.conn.execute("UPDATE runners SET unit_id = NULL WHERE event_id = ? AND unit_id = ?", (eid, int(unit_id)))
        self.conn.execute("DELETE FROM units WHERE event_id = ? AND unit_id = ?", (eid, int(unit_id)))
        self.conn.commit()

    def count_runners_by_unit(self, event_id=None):
        cur = self.conn.execute(
            "SELECT unit_id, COUNT(*) AS n FROM runners WHERE event_id = ? AND unit_id IS NOT NULL GROUP BY unit_id",
            (self._eid(event_id),),
        )
        return {r["unit_id"]: r["n"] for r in cur.fetchall()}

    # ------------------------------------------------------------------
    # 通道
    # ------------------------------------------------------------------
    def list_channels(self, event_id=None):
        cur = self.conn.execute(
            "SELECT channel_id, name, first_start_time, interval_sec, empty_slots FROM channels WHERE event_id = ? ORDER BY name ASC",
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def upsert_channel(self, name: str, first_start_time, interval_sec, empty_slots, channel_id=None, event_id=None) -> int:
        eid = self._eid(event_id)
        if channel_id:
            self.conn.execute(
                "UPDATE channels SET name = ?, first_start_time = ?, interval_sec = ?, empty_slots = ? WHERE event_id = ? AND channel_id = ?",
                (name, first_start_time, interval_sec, empty_slots, eid, int(channel_id)),
            )
            self.conn.commit()
            return int(channel_id)
        cur = self.conn.execute(
            "INSERT INTO channels (event_id, name, first_start_time, interval_sec, empty_slots) VALUES (?, ?, ?, ?, ?)",
            (eid, name, first_start_time, interval_sec, empty_slots),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def delete_channel(self, channel_id: int, event_id=None):
        eid = self._eid(event_id)
        self.conn.execute("UPDATE groups SET channel_id = NULL WHERE event_id = ? AND channel_id = ?", (eid, int(channel_id)))
        self.conn.execute("DELETE FROM channels WHERE event_id = ? AND channel_id = ?", (eid, int(channel_id)))
        self.conn.commit()

    # ------------------------------------------------------------------
    # 组别
    # ------------------------------------------------------------------
    def list_groups(self, event_id=None):
        cur = self.conn.execute(
            "SELECT group_id, name, route_id, limit_min, start_mode, channel_id, seq_order FROM groups WHERE event_id = ? ORDER BY seq_order ASC, group_id ASC",
            (self._eid(event_id),),
        )
        return [dict(r) for r in cur.fetchall()]

    def get_group(self, group_id: int, event_id=None):
        cur = self.conn.execute(
            "SELECT group_id, name, route_id, limit_min, start_mode, channel_id, seq_order FROM groups WHERE event_id = ? AND group_id = ?",
            (self._eid(event_id), int(group_id)),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def upsert_group(self, name: str, route_id=None, limit_min=None, start_mode=None, channel_id=None, seq_order=None, group_id=None, event_id=None) -> int:
        eid = self._eid(event_id)
        if group_id:
            self.conn.execute(
                "UPDATE groups SET name = ?, route_id = ?, limit_min = ?, start_mode = ?, channel_id = ?, seq_order = ? WHERE event_id = ? AND group_id = ?",
                (name, route_id, limit_min, start_mode, channel_id, seq_order, eid, int(group_id)),
            )
            self.conn.commit()
            return int(group_id)
        cur = self.conn.execute(
            "INSERT INTO groups (event_id, name, route_id, limit_min, start_mode, channel_id, seq_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eid, name, route_id, limit_min, start_mode, channel_id, seq_order),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def delete_group(self, group_id: int, event_id=None):
        eid = self._eid(event_id)
        self.conn.execute("UPDATE runners SET group_id = NULL WHERE event_id = ? AND group_id = ?", (eid, int(group_id)))
        self.conn.execute("DELETE FROM groups WHERE event_id = ? AND group_id = ?", (eid, int(group_id)))
        self.conn.commit()

    def close(self):
        self.conn.close()
