"""Data access layer for the Moderated Bulk Add staging area."""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone

import networkx as nx

from .models import (
    ReviewerComment,
    StagedEdgeCreate,
    StagedEdgeResponse,
    StagedKCCreate,
    StagedKCResponse,
    StagedKCUpdate,
    StagedMathContext,
    StagedSchemaCreate,
    StagedSchemaResponse,
    StagingSessionCreate,
    StagingSessionResponse,
    StagingSessionUpdate,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_json_list(raw: str | None) -> list:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []


class StagingDAL:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ═══════════════════════════════════════════════════════
    # Staging Sessions
    # ═══════════════════════════════════════════════════════

    def create_session(self, session: StagingSessionCreate) -> StagingSessionResponse:
        now = _now()
        self.conn.execute(
            "INSERT INTO staging_sessions (id, topic_name, description, source_documents, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 'active', ?, ?)",
            (session.id, session.topic_name, session.description,
             json.dumps(session.source_documents), now, now),
        )
        self.conn.commit()
        return self.get_session(session.id)

    def get_session(self, session_id: str) -> StagingSessionResponse | None:
        row = self.conn.execute(
            "SELECT * FROM staging_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        stats = self._session_statistics(session_id)
        return StagingSessionResponse(
            id=row["id"],
            topic_name=row["topic_name"],
            description=row["description"],
            source_documents=_parse_json_list(row["source_documents"]),
            status=row["status"],
            statistics=stats,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_sessions(self) -> list[StagingSessionResponse]:
        rows = self.conn.execute(
            "SELECT id FROM staging_sessions ORDER BY created_at DESC"
        ).fetchall()
        return [self.get_session(r["id"]) for r in rows]

    def update_session(self, session_id: str, update: StagingSessionUpdate) -> StagingSessionResponse | None:
        existing = self.conn.execute(
            "SELECT id FROM staging_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        if update.topic_name is not None:
            sets.append("topic_name = ?")
            params.append(update.topic_name)
        if update.description is not None:
            sets.append("description = ?")
            params.append(update.description)
        if update.source_documents is not None:
            sets.append("source_documents = ?")
            params.append(json.dumps(update.source_documents))
        if update.status is not None:
            sets.append("status = ?")
            params.append(update.status)
        params.append(session_id)
        self.conn.execute(
            f"UPDATE staging_sessions SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_session(session_id)

    def delete_session(self, session_id: str, force: bool = False) -> bool:
        row = self.conn.execute(
            "SELECT status FROM staging_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return False
        if not force and row["status"] not in ("abandoned", "active"):
            raise ValueError("Can only delete sessions with status 'abandoned' or 'active' (use force=True to override)")
        # Cascade delete all associated data
        # staged_schema_kcs has no session_id — delete via schemas
        self.conn.execute(
            "DELETE FROM staged_schema_kcs WHERE schema_id IN "
            "(SELECT id FROM staged_schemas WHERE session_id = ?)", (session_id,)
        )
        self.conn.execute("DELETE FROM staged_schemas WHERE session_id = ?", (session_id,))
        self.conn.execute("DELETE FROM staged_edges WHERE session_id = ?", (session_id,))
        self.conn.execute("DELETE FROM staged_kc_conversations WHERE session_id = ?", (session_id,))
        self.conn.execute("DELETE FROM staged_kcs WHERE session_id = ?", (session_id,))
        self.conn.execute("DELETE FROM staging_sessions WHERE id = ?", (session_id,))
        self.conn.commit()
        return True

    def _session_statistics(self, session_id: str) -> dict:
        # KC counts by status
        kc_rows = self.conn.execute(
            "SELECT stage_status, COUNT(*) as c FROM staged_kcs "
            "WHERE session_id = ? GROUP BY stage_status",
            (session_id,),
        ).fetchall()
        kc_by_stage = {r["stage_status"]: r["c"] for r in kc_rows}
        total_kcs = sum(kc_by_stage.values())

        # Edge counts by status
        edge_rows = self.conn.execute(
            "SELECT status, COUNT(*) as c FROM staged_edges "
            "WHERE session_id = ? GROUP BY status",
            (session_id,),
        ).fetchall()
        edges = {r["status"]: r["c"] for r in edge_rows}

        # Schema counts by status
        schema_rows = self.conn.execute(
            "SELECT status, COUNT(*) as c FROM staged_schemas "
            "WHERE session_id = ? GROUP BY status",
            (session_id,),
        ).fetchall()
        schemas = {r["status"]: r["c"] for r in schema_rows}

        return {
            "total_kcs": total_kcs,
            "by_stage": kc_by_stage,
            "edges": edges,
            "schemas": schemas,
        }

    # ═══════════════════════════════════════════════════════
    # Staged KCs
    # ═══════════════════════════════════════════════════════

    def create_staged_kc(self, session_id: str, kc: StagedKCCreate) -> StagedKCResponse:
        now = _now()
        self.conn.execute(
            "INSERT INTO staged_kcs "
            "(id, session_id, short_description, long_description, source_text, source_reference, "
            "stage_status, language_demands, kc_type, math_contexts, ai_correctness_note, "
            "created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (kc.id, session_id, kc.short_description, kc.long_description,
             kc.source_text, kc.source_reference, kc.stage_status,
             json.dumps(kc.language_demands),
             kc.kc_type,
             json.dumps([ctx.model_dump() for ctx in kc.math_contexts]),
             kc.ai_correctness_note,
             now, now),
        )
        self.conn.commit()
        return self.get_staged_kc(session_id, kc.id)

    def create_staged_kcs_batch(self, session_id: str, kcs: list[StagedKCCreate]) -> list[StagedKCResponse]:
        results = []
        for kc in kcs:
            results.append(self.create_staged_kc(session_id, kc))
        return results

    def max_staged_kc_number(self, prefix: str) -> int:
        """Highest NNN among ALL ``STAGE-{prefix}-NNN`` ids, across every session.

        staged_kcs.id is a global primary key, so ingest numbering must be global
        per prefix — scoping it to one session restarts at 001 and collides with
        ids the same prefix already minted in other sessions.
        """
        rows = self.conn.execute(
            "SELECT id FROM staged_kcs WHERE id LIKE ?",
            (f"STAGE-{prefix}-%",),
        ).fetchall()
        mx = 0
        for r in rows:
            try:
                mx = max(mx, int(r["id"].rsplit("-", 1)[1]))
            except (ValueError, IndexError):
                pass
        return mx

    def get_staged_kc(self, session_id: str, kc_id: str) -> StagedKCResponse | None:
        row = self.conn.execute(
            "SELECT * FROM staged_kcs WHERE id = ? AND session_id = ?",
            (kc_id, session_id),
        ).fetchone()
        if not row:
            return None
        return self._kc_from_row(row)

    def list_staged_kcs(
        self, session_id: str, stage_status: str | None = None,
    ) -> list[StagedKCResponse]:
        query = "SELECT * FROM staged_kcs WHERE session_id = ?"
        params: list = [session_id]
        if stage_status:
            query += " AND stage_status = ?"
            params.append(stage_status)
        query += " ORDER BY id"
        rows = self.conn.execute(query, params).fetchall()
        return [self._kc_from_row(r) for r in rows]

    def update_staged_kc(self, session_id: str, kc_id: str, update: StagedKCUpdate) -> StagedKCResponse | None:
        existing = self.conn.execute(
            "SELECT id FROM staged_kcs WHERE id = ? AND session_id = ?",
            (kc_id, session_id),
        ).fetchone()
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        if update.short_description is not None:
            sets.append("short_description = ?")
            params.append(update.short_description)
        if update.long_description is not None:
            sets.append("long_description = ?")
            params.append(update.long_description)
        if update.source_text is not None:
            sets.append("source_text = ?")
            params.append(update.source_text)
        if update.source_reference is not None:
            sets.append("source_reference = ?")
            params.append(update.source_reference)
        if update.stage_status is not None:
            sets.append("stage_status = ?")
            params.append(update.stage_status)
        if update.language_demands is not None:
            sets.append("language_demands = ?")
            params.append(json.dumps(update.language_demands))
        if update.kc_type is not None:
            sets.append("kc_type = ?")
            params.append(update.kc_type)
        if update.math_contexts is not None:
            sets.append("math_contexts = ?")
            params.append(json.dumps([ctx.model_dump() for ctx in update.math_contexts]))
        if update.ai_correctness_note is not None:
            sets.append("ai_correctness_note = ?")
            params.append(update.ai_correctness_note)
        params.append(kc_id)
        self.conn.execute(
            f"UPDATE staged_kcs SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_staged_kc(session_id, kc_id)

    def batch_update_staged_kcs(
        self, session_id: str, kc_ids: list[str], update: StagedKCUpdate,
    ) -> list[StagedKCResponse]:
        results = []
        for kc_id in kc_ids:
            result = self.update_staged_kc(session_id, kc_id, update)
            if result:
                results.append(result)
        return results

    def delete_staged_kc(self, session_id: str, kc_id: str) -> bool:
        row = self.conn.execute(
            "SELECT id FROM staged_kcs WHERE id = ? AND session_id = ?",
            (kc_id, session_id),
        ).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM staged_kcs WHERE id = ?", (kc_id,))
        self.conn.commit()
        return True

    def add_kc_comment(self, session_id: str, kc_id: str, author: str, text: str) -> StagedKCResponse | None:
        row = self.conn.execute(
            "SELECT reviewer_comments FROM staged_kcs WHERE id = ? AND session_id = ?",
            (kc_id, session_id),
        ).fetchone()
        if not row:
            return None
        comments = _parse_json_list(row["reviewer_comments"])
        comments.append({
            "author": author,
            "timestamp": _now(),
            "text": text,
        })
        self.conn.execute(
            "UPDATE staged_kcs SET reviewer_comments = ?, updated_at = ? WHERE id = ?",
            (json.dumps(comments), _now(), kc_id),
        )
        self.conn.commit()
        return self.get_staged_kc(session_id, kc_id)

    def flag_kc(self, session_id: str, kc_id: str) -> StagedKCResponse | None:
        row = self.conn.execute(
            "SELECT id FROM staged_kcs WHERE id = ? AND session_id = ?",
            (kc_id, session_id),
        ).fetchone()
        if not row:
            return None
        self.conn.execute(
            "UPDATE staged_kcs SET stage_status = 'flagged', updated_at = ? WHERE id = ?",
            (_now(), kc_id),
        )
        self.conn.commit()
        return self.get_staged_kc(session_id, kc_id)

    def _kc_from_row(self, row: sqlite3.Row) -> StagedKCResponse:
        raw_contexts = _parse_json_list(row["math_contexts"])
        contexts = [StagedMathContext(**ctx) for ctx in raw_contexts]
        raw_comments = _parse_json_list(row["reviewer_comments"])
        comments = [ReviewerComment(**c) for c in raw_comments]
        return StagedKCResponse(
            id=row["id"],
            session_id=row["session_id"],
            short_description=row["short_description"],
            long_description=row["long_description"],
            source_text=row["source_text"],
            source_reference=row["source_reference"],
            stage_status=row["stage_status"],
            language_demands=_parse_json_list(row["language_demands"]),
            kc_type=row["kc_type"],
            math_contexts=contexts,
            reviewer_comments=comments,
            ai_correctness_note=row["ai_correctness_note"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    # ═══════════════════════════════════════════════════════
    # Staged Edges
    # ═══════════════════════════════════════════════════════

    def create_staged_edge(self, session_id: str, edge: StagedEdgeCreate) -> StagedEdgeResponse:
        # Idempotent: an edge is uniquely identified by (session, source, target).
        # If it already exists, return it rather than inserting a duplicate. This
        # makes prerequisite regeneration safe — re-proposing an existing edge is a
        # no-op instead of creating a second copy.
        existing = self.conn.execute(
            "SELECT id FROM staged_edges "
            "WHERE session_id = ? AND source_kc_id = ? AND target_kc_id = ?",
            (session_id, edge.source_kc_id, edge.target_kc_id),
        ).fetchone()
        if existing:
            return self.get_staged_edge(session_id, existing["id"])

        now = _now()
        cur = self.conn.execute(
            "INSERT INTO staged_edges "
            "(session_id, source_kc_id, target_kc_id, ai_reasoning, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, edge.source_kc_id, edge.target_kc_id,
             edge.ai_reasoning, edge.status, now, now),
        )
        self.conn.commit()
        return self.get_staged_edge(session_id, cur.lastrowid)

    def create_staged_edges_batch(self, session_id: str, edges: list[StagedEdgeCreate]) -> list[StagedEdgeResponse]:
        results = []
        for edge in edges:
            results.append(self.create_staged_edge(session_id, edge))
        return results

    # Priority for resolving duplicates / picking a "winner" per (source, target).
    # Higher wins. Confirmed edges represent human-approved work and are kept.
    _STATUS_PRIORITY = {"confirmed": 3, "proposed": 2, "stale": 1, "rejected": 0}

    def dedupe_staged_edges(self, session_id: str) -> dict:
        """Collapse duplicate (source, target) staged edges within a session.

        Keeps one row per (source, target) — preferring confirmed status, then
        proposed, breaking ties by lowest id — and deletes the rest. Returns a
        summary of how many groups were collapsed and rows removed.
        """
        rows = self.conn.execute(
            "SELECT id, source_kc_id, target_kc_id, status FROM staged_edges "
            "WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

        groups: dict[tuple[str, str], list[sqlite3.Row]] = {}
        for r in rows:
            groups.setdefault((r["source_kc_id"], r["target_kc_id"]), []).append(r)

        removed_ids: list[int] = []
        groups_collapsed = 0
        for members in groups.values():
            if len(members) < 2:
                continue
            groups_collapsed += 1
            # Pick the winner: highest status priority, then lowest id.
            winner = max(
                members,
                key=lambda m: (self._STATUS_PRIORITY.get(m["status"], 0), -m["id"]),
            )
            for m in members:
                if m["id"] != winner["id"]:
                    removed_ids.append(m["id"])

        for edge_id in removed_ids:
            self.conn.execute("DELETE FROM staged_edges WHERE id = ?", (edge_id,))
        if removed_ids:
            self.conn.commit()

        return {
            "groups_collapsed": groups_collapsed,
            "removed": len(removed_ids),
            "removed_ids": removed_ids,
        }

    def delete_proposed_edges_for_kcs(self, session_id: str, kc_ids: list[str]) -> int:
        """Delete AI-proposed (not confirmed) edges touching any of the given KCs.

        Used by 'replace' regeneration: clears the previous AI proposals among the
        KCs being re-analyzed while preserving confirmed (human-approved) edges.
        Returns the number of rows deleted.
        """
        if not kc_ids:
            return 0
        placeholders = ",".join("?" for _ in kc_ids)
        cur = self.conn.execute(
            f"DELETE FROM staged_edges WHERE session_id = ? AND status = 'proposed' "
            f"AND (source_kc_id IN ({placeholders}) OR target_kc_id IN ({placeholders}))",
            (session_id, *kc_ids, *kc_ids),
        )
        self.conn.commit()
        return cur.rowcount

    def get_staged_edge(self, session_id: str, edge_id: int) -> StagedEdgeResponse | None:
        row = self.conn.execute(
            "SELECT * FROM staged_edges WHERE id = ? AND session_id = ?",
            (edge_id, session_id),
        ).fetchone()
        if not row:
            return None
        return self._edge_from_row(row)

    def list_staged_edges(
        self, session_id: str, status: str | None = None,
        source_kc_id: str | None = None, target_kc_id: str | None = None,
    ) -> list[StagedEdgeResponse]:
        query = "SELECT * FROM staged_edges WHERE session_id = ?"
        params: list = [session_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        if source_kc_id:
            query += " AND source_kc_id = ?"
            params.append(source_kc_id)
        if target_kc_id:
            query += " AND target_kc_id = ?"
            params.append(target_kc_id)
        query += " ORDER BY id"
        rows = self.conn.execute(query, params).fetchall()
        return [self._edge_from_row(r) for r in rows]

    def update_staged_edge(self, session_id: str, edge_id: int, status: str | None = None, ai_reasoning: str | None = None) -> StagedEdgeResponse | None:
        existing = self.conn.execute(
            "SELECT * FROM staged_edges WHERE id = ? AND session_id = ?",
            (edge_id, session_id),
        ).fetchone()
        if not existing:
            return None

        # If confirming an edge, check for cycles among confirmed edges
        if status == "confirmed":
            self._check_staged_acyclicity(session_id, existing["source_kc_id"], existing["target_kc_id"], edge_id)

        sets = ["updated_at = ?"]
        params: list = [_now()]
        if status is not None:
            sets.append("status = ?")
            params.append(status)
        if ai_reasoning is not None:
            sets.append("ai_reasoning = ?")
            params.append(ai_reasoning)
        params.append(edge_id)
        self.conn.execute(
            f"UPDATE staged_edges SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_staged_edge(session_id, edge_id)

    def delete_staged_edge(self, session_id: str, edge_id: int) -> bool:
        row = self.conn.execute(
            "SELECT id FROM staged_edges WHERE id = ? AND session_id = ?",
            (edge_id, session_id),
        ).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM staged_edges WHERE id = ?", (edge_id,))
        self.conn.commit()
        return True

    def validate_staged_edges(self, session_id: str) -> dict:
        """Run acyclicity check on all confirmed edges in the session."""
        rows = self.conn.execute(
            "SELECT source_kc_id, target_kc_id FROM staged_edges "
            "WHERE session_id = ? AND status = 'confirmed'",
            (session_id,),
        ).fetchall()

        g = nx.DiGraph()
        for r in rows:
            g.add_edge(r["source_kc_id"], r["target_kc_id"])

        cycles = list(nx.simple_cycles(g))
        if cycles:
            return {
                "valid": False,
                "message": f"Found {len(cycles)} cycle(s) among confirmed edges",
                "cycles": [list(c) for c in cycles],
            }
        return {"valid": True, "message": "No cycles detected", "cycles": []}

    def _check_staged_acyclicity(self, session_id: str, source_kc_id: str, target_kc_id: str, exclude_edge_id: int | None = None):
        """Check if confirming this edge would create a cycle among confirmed edges."""
        query = "SELECT source_kc_id, target_kc_id FROM staged_edges WHERE session_id = ? AND status = 'confirmed'"
        params: list = [session_id]
        if exclude_edge_id is not None:
            query += " AND id != ?"
            params.append(exclude_edge_id)

        rows = self.conn.execute(query, params).fetchall()
        g = nx.DiGraph()
        for r in rows:
            g.add_edge(r["source_kc_id"], r["target_kc_id"])
        g.add_edge(source_kc_id, target_kc_id)

        try:
            cycle = nx.find_cycle(g, source=source_kc_id)
            cycle_nodes = [e[0] for e in cycle]
            raise ValueError(
                f"Confirming this edge would create a cycle: {' → '.join(cycle_nodes)}"
            )
        except nx.NetworkXNoCycle:
            pass  # No cycle — safe to confirm

    def _edge_from_row(self, row: sqlite3.Row) -> StagedEdgeResponse:
        raw_comments = _parse_json_list(row["reviewer_comments"])
        comments = [ReviewerComment(**c) for c in raw_comments]
        return StagedEdgeResponse(
            id=row["id"],
            session_id=row["session_id"],
            source_kc_id=row["source_kc_id"],
            target_kc_id=row["target_kc_id"],
            ai_reasoning=row["ai_reasoning"],
            status=row["status"],
            reviewer_comments=comments,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    # ═══════════════════════════════════════════════════════
    # Staged Schemas
    # ═══════════════════════════════════════════════════════

    @staticmethod
    def _slugify(name: str) -> str:
        """Mirror the frontend slugify so server-minted schema ids look the same."""
        s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")[:50]
        return s or "schema"

    def replace_proposed_schemas(self, session_id: str, proposals: list[dict]) -> list[StagedSchemaResponse]:
        """Persist AI schema proposals as status='proposed' schemas.

        Replaces any prior *proposed* schemas in the session (confirmed schemas are
        preserved), so re-running 'Propose Schemas' is idempotent. Proposals are
        dicts with name / description / kc_ids / parent_schema (parent referenced by
        name). Server-mints unique ids, resolves parents within the batch, and
        assigns only KCs that exist in the session.

        Persisting here (rather than returning browser-only proposals) means
        proposals survive reloads, appear in the Staged Schemas list, and render on
        the graph immediately; the existing 'Confirm All' step flips them to
        confirmed.
        """
        # Clear prior proposals (cascade removes their staged_schema_kcs rows).
        for r in self.conn.execute(
            "SELECT id FROM staged_schemas WHERE session_id = ? AND status = 'proposed'",
            (session_id,),
        ).fetchall():
            self.conn.execute("DELETE FROM staged_schemas WHERE id = ?", (r["id"],))

        existing_ids = {r["id"] for r in self.conn.execute("SELECT id FROM staged_schemas")}
        valid_kcs = {
            r["id"] for r in self.conn.execute(
                "SELECT id FROM staged_kcs WHERE session_id = ?", (session_id,)
            )
        }
        now = _now()
        name_to_id: dict[str, str] = {}
        created: list[tuple[str, dict]] = []

        # Pass 1: create each schema with a unique id.
        for p in proposals:
            name = p.get("name") or "schema"
            base = self._slugify(name)
            sid, i = base, 2
            while sid in existing_ids:
                sid = f"{base}-{i}"
                i += 1
            existing_ids.add(sid)
            name_to_id[name] = sid
            self.conn.execute(
                "INSERT INTO staged_schemas "
                "(id, session_id, name, description, parent_schema_id, status, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, 'proposed', ?, ?)",
                (sid, session_id, name, p.get("description"), None, now, now),
            )
            created.append((sid, p))

        # Pass 2: resolve parents (by name, within this batch) and assign KCs.
        for sid, p in created:
            parent_name = p.get("parent_schema")
            if parent_name and parent_name in name_to_id and name_to_id[parent_name] != sid:
                self.conn.execute(
                    "UPDATE staged_schemas SET parent_schema_id = ? WHERE id = ?",
                    (name_to_id[parent_name], sid),
                )
            for kc_id in (p.get("kc_ids") or []):
                if kc_id in valid_kcs:
                    self.conn.execute(
                        "INSERT OR IGNORE INTO staged_schema_kcs (schema_id, kc_id) VALUES (?, ?)",
                        (sid, kc_id),
                    )
        self.conn.commit()
        return [self.get_staged_schema(session_id, sid) for sid, _ in created]

    def create_staged_schema(self, session_id: str, schema: StagedSchemaCreate) -> StagedSchemaResponse:
        now = _now()
        self.conn.execute(
            "INSERT INTO staged_schemas "
            "(id, session_id, name, description, parent_schema_id, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (schema.id, session_id, schema.name, schema.description,
             schema.parent_schema_id, schema.status, now, now),
        )
        self.conn.commit()
        return self.get_staged_schema(session_id, schema.id)

    def get_staged_schema(self, session_id: str, schema_id: str) -> StagedSchemaResponse | None:
        row = self.conn.execute(
            "SELECT * FROM staged_schemas WHERE id = ? AND session_id = ?",
            (schema_id, session_id),
        ).fetchone()
        if not row:
            return None
        kc_ids = [
            r["kc_id"]
            for r in self.conn.execute(
                "SELECT kc_id FROM staged_schema_kcs WHERE schema_id = ? ORDER BY kc_id",
                (schema_id,),
            )
        ]
        return StagedSchemaResponse(
            id=row["id"],
            session_id=row["session_id"],
            name=row["name"],
            description=row["description"],
            parent_schema_id=row["parent_schema_id"],
            status=row["status"],
            kc_ids=kc_ids,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_staged_schemas(self, session_id: str, status: str | None = None) -> list[StagedSchemaResponse]:
        query = "SELECT id FROM staged_schemas WHERE session_id = ?"
        params: list = [session_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id"
        rows = self.conn.execute(query, params).fetchall()
        return [self.get_staged_schema(session_id, r["id"]) for r in rows]

    def update_staged_schema(self, session_id: str, schema_id: str, name: str | None = None, description: str | None = None, parent_schema_id: str | None = None, status: str | None = None) -> StagedSchemaResponse | None:
        existing = self.conn.execute(
            "SELECT id FROM staged_schemas WHERE id = ? AND session_id = ?",
            (schema_id, session_id),
        ).fetchone()
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        if name is not None:
            sets.append("name = ?")
            params.append(name)
        if description is not None:
            sets.append("description = ?")
            params.append(description)
        if parent_schema_id is not None:
            sets.append("parent_schema_id = ?")
            params.append(parent_schema_id)
        if status is not None:
            sets.append("status = ?")
            params.append(status)
        params.append(schema_id)
        self.conn.execute(
            f"UPDATE staged_schemas SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_staged_schema(session_id, schema_id)

    def delete_staged_schema(self, session_id: str, schema_id: str) -> bool:
        row = self.conn.execute(
            "SELECT id FROM staged_schemas WHERE id = ? AND session_id = ?",
            (schema_id, session_id),
        ).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM staged_schemas WHERE id = ?", (schema_id,))
        self.conn.commit()
        return True

    def add_kcs_to_staged_schema(self, session_id: str, schema_id: str, kc_ids: list[str]) -> StagedSchemaResponse | None:
        existing = self.conn.execute(
            "SELECT id FROM staged_schemas WHERE id = ? AND session_id = ?",
            (schema_id, session_id),
        ).fetchone()
        if not existing:
            return None
        for kc_id in kc_ids:
            self.conn.execute(
                "INSERT OR IGNORE INTO staged_schema_kcs (schema_id, kc_id) VALUES (?, ?)",
                (schema_id, kc_id),
            )
        self.conn.commit()
        return self.get_staged_schema(session_id, schema_id)

    def remove_kc_from_staged_schema(self, session_id: str, schema_id: str, kc_id: str) -> bool:
        row = self.conn.execute(
            "SELECT * FROM staged_schema_kcs sk "
            "JOIN staged_schemas s ON s.id = sk.schema_id "
            "WHERE sk.schema_id = ? AND sk.kc_id = ? AND s.session_id = ?",
            (schema_id, kc_id, session_id),
        ).fetchone()
        if not row:
            return False
        self.conn.execute(
            "DELETE FROM staged_schema_kcs WHERE schema_id = ? AND kc_id = ?",
            (schema_id, kc_id),
        )
        self.conn.commit()
        return True

    def validate_staged_schemas(self, session_id: str) -> dict:
        """Run laminarity and convexity checks on staged schemas.

        For now, returns basic validation. Full laminarity/convexity
        checks will use the frame_engine once schemas are being
        converted toward commit.
        """
        schemas = [s for s in self.list_staged_schemas(session_id) if s.status != "stale"]

        # Check for empty schemas. Leaf-only nesting: KCs belong only to leaf
        # schemas, and a parent's membership is the union of its descendants' —
        # so emptiness must count KCs anywhere in the subtree, not just direct members.
        children: dict[str, list] = {}
        for s in schemas:
            if s.parent_schema_id:
                children.setdefault(s.parent_schema_id, []).append(s)

        def _has_kcs(schema) -> bool:
            if schema.kc_ids:
                return True
            return any(_has_kcs(c) for c in children.get(schema.id, []))

        empty = [s.id for s in schemas if not _has_kcs(s)]

        # Check parent references
        schema_ids = {s.id for s in schemas}
        orphans = [
            s.id for s in schemas
            if s.parent_schema_id and s.parent_schema_id not in schema_ids
        ]

        valid = not empty and not orphans
        issues = []
        if empty:
            issues.append(f"Empty schemas: {', '.join(empty)}")
        if orphans:
            issues.append(f"Schemas with missing parent references: {', '.join(orphans)}")

        return {
            "valid": valid,
            "message": "All checks passed" if valid else "; ".join(issues),
            "empty_schemas": empty,
            "orphan_schemas": orphans,
        }

    # ═══════════════════════════════════════════════════════
    # KC Conversations (Grain Review Chat)
    # ═══════════════════════════════════════════════════════

    def get_conversation(self, session_id: str, kc_id: str) -> list[dict] | None:
        """Get conversation messages for a KC, or None if no conversation exists."""
        row = self.conn.execute(
            "SELECT messages FROM staged_kc_conversations "
            "WHERE session_id = ? AND kc_id = ?",
            (session_id, kc_id),
        ).fetchone()
        if not row:
            return None
        return _parse_json_list(row["messages"])

    def save_conversation(self, session_id: str, kc_id: str, messages: list[dict]) -> None:
        """Upsert conversation messages for a KC."""
        now = _now()
        self.conn.execute(
            "INSERT INTO staged_kc_conversations (session_id, kc_id, messages, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(session_id, kc_id) DO UPDATE SET messages = excluded.messages, updated_at = excluded.updated_at",
            (session_id, kc_id, json.dumps(messages), now, now),
        )
        self.conn.commit()

    def list_conversations(self, session_id: str) -> list[str]:
        """Return list of kc_ids that have active conversations in this session."""
        rows = self.conn.execute(
            "SELECT kc_id FROM staged_kc_conversations WHERE session_id = ?",
            (session_id,),
        ).fetchall()
        return [r["kc_id"] for r in rows]
