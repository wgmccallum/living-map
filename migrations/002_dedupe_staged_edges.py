"""Collapse duplicate staged edges and add a UNIQUE index on (session, source, target).

Background: `staged_edges` had no uniqueness constraint, and prerequisite
regeneration inserted a fresh row per proposal. Re-running the proposal step
therefore created exact-duplicate edges (one per round). This migration removes
the existing duplicates (keeping confirmed status over proposed, then lowest id)
and adds a UNIQUE index so the DB enforces idempotency going forward.

Idempotent: skips if the unique index already exists.

Run: python migrations/002_dedupe_staged_edges.py path/to/db.sqlite [more.sqlite ...]
"""
from __future__ import annotations
import sqlite3
import sys
from pathlib import Path

# Higher wins when resolving a duplicate group. Confirmed = human-approved.
_STATUS_PRIORITY = {"confirmed": 3, "proposed": 2, "stale": 1, "rejected": 0}


def already_migrated(conn: sqlite3.Connection) -> bool:
    return bool(
        conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='index' AND name='uq_staged_edges_triple'"
        ).fetchone()
    )


def dedupe(conn: sqlite3.Connection) -> int:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, session_id, source_kc_id, target_kc_id, status "
        "FROM staged_edges ORDER BY id"
    ).fetchall()

    groups: dict[tuple[str, str, str], list[sqlite3.Row]] = {}
    for r in rows:
        key = (r["session_id"], r["source_kc_id"], r["target_kc_id"])
        groups.setdefault(key, []).append(r)

    removed = 0
    for members in groups.values():
        if len(members) < 2:
            continue
        winner = max(
            members,
            key=lambda m: (_STATUS_PRIORITY.get(m["status"], 0), -m["id"]),
        )
        for m in members:
            if m["id"] != winner["id"]:
                conn.execute("DELETE FROM staged_edges WHERE id = ?", (m["id"],))
                removed += 1
    return removed


def migrate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if already_migrated(conn):
            print(f"  {db_path}: already migrated, skipping")
            return
        conn.execute("BEGIN")
        removed = dedupe(conn)
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_staged_edges_triple "
            "ON staged_edges(session_id, source_kc_id, target_kc_id)"
        )
        conn.commit()
        print(f"  {db_path}: removed {removed} duplicate edge(s), unique index created")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        sys.exit(1)
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"  {path}: not found, skipping")
            continue
        migrate(path)
