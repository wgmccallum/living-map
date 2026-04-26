"""Migrate `schemas` PK from `id` to `(frame_id, id)`; add `frame_id` to `schema_kcs`.

Enables forking a frame into a sandbox where schemas keep their original IDs.

Idempotent: skips if `schema_kcs` already has a `frame_id` column.

Run: python migrations/001_composite_schema_pk.py path/to/db.sqlite
"""
from __future__ import annotations
import sqlite3
import sys
from pathlib import Path


def already_migrated(conn: sqlite3.Connection) -> bool:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(schema_kcs)")]
    return "frame_id" in cols


def migrate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        if already_migrated(conn):
            print(f"  {db_path}: already migrated, skipping")
            return

        # Sanity check: every schema_kcs row must point to an existing schema
        orphans = conn.execute("""
            SELECT count(*) FROM schema_kcs sk
            LEFT JOIN schemas s ON sk.schema_id = s.id
            WHERE s.id IS NULL
        """).fetchone()[0]
        if orphans:
            raise RuntimeError(f"{orphans} orphan schema_kcs rows; refuse to migrate")

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")

        conn.executescript("""
            -- 1. Stash schema_kcs data with frame_id resolved via join
            CREATE TEMP TABLE schema_kcs_stash AS
                SELECT s.frame_id AS frame_id, sk.schema_id AS schema_id, sk.kc_id AS kc_id
                FROM schema_kcs sk JOIN schemas s ON sk.schema_id = s.id;

            -- 2. Drop old tables (schema_kcs first because of FK)
            DROP TABLE schema_kcs;

            -- 3. Build new schemas table with composite PK
            CREATE TABLE schemas_new (
                id               TEXT NOT NULL,
                frame_id         TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
                name             TEXT NOT NULL,
                description      TEXT,
                parent_schema_id TEXT,
                created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                PRIMARY KEY (frame_id, id)
            );
            INSERT INTO schemas_new (id, frame_id, name, description, parent_schema_id, created_at, updated_at)
                SELECT id, frame_id, name, description, parent_schema_id, created_at, updated_at FROM schemas;
            DROP TABLE schemas;
            ALTER TABLE schemas_new RENAME TO schemas;

            -- 4. Build new schema_kcs with FK to the now-renamed schemas table
            CREATE TABLE schema_kcs (
                frame_id  TEXT NOT NULL,
                schema_id TEXT NOT NULL,
                kc_id     TEXT NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
                PRIMARY KEY (frame_id, schema_id, kc_id),
                FOREIGN KEY (frame_id, schema_id) REFERENCES schemas(frame_id, id) ON DELETE CASCADE
            );
            INSERT INTO schema_kcs (frame_id, schema_id, kc_id)
                SELECT frame_id, schema_id, kc_id FROM schema_kcs_stash;
            DROP TABLE schema_kcs_stash;

            -- 5. Indexes
            CREATE INDEX idx_schema_frame ON schemas(frame_id);
            CREATE INDEX idx_schema_kcs_kc ON schema_kcs(kc_id);
            CREATE INDEX idx_schema_kcs_schema ON schema_kcs(frame_id, schema_id);
        """)

        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")

        # Verify integrity
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"integrity_check failed: {result}")
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk_violations:
            raise RuntimeError(f"FK violations after migration: {fk_violations}")

        # Stats
        n_schemas = conn.execute("SELECT count(*) FROM schemas").fetchone()[0]
        n_kcs = conn.execute("SELECT count(*) FROM schema_kcs").fetchone()[0]
        print(f"  {db_path}: ok — {n_schemas} schemas, {n_kcs} schema_kcs rows")
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 001_composite_schema_pk.py <db_path> [<db_path>...]")
        sys.exit(1)
    for path in sys.argv[1:]:
        migrate(Path(path))
