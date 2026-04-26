"""Data access layer — CRUD operations backed by SQLite + NetworkX sync."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from .graph_store import CycleError, GraphStore
from .models import (
    AnnotationCreate,
    AnnotationResponse,
    EdgeCreate,
    EdgeResponse,
    KCCreate,
    KCResponse,
    KCUpdate,
    MathConceptCreate,
    MathConceptEdgeCreate,
    MathConceptEdgeResponse,
    MathConceptResponse,
    MathConceptUpdate,
    MathContextLink,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class DAL:
    def __init__(self, conn: sqlite3.Connection, graphs: GraphStore):
        self.conn = conn
        self.graphs = graphs

    # ── Knowledge Components ──

    def create_kc(self, kc: KCCreate) -> KCResponse:
        now = _now()
        self.conn.execute(
            "INSERT INTO knowledge_components (id, short_description, long_description, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (kc.id, kc.short_description, kc.long_description, now, now),
        )
        self.graphs.add_kc(kc.id)
        # Language demands
        for label in kc.language_demands:
            row = self.conn.execute(
                "SELECT id FROM language_demands WHERE label = ?", (label,)
            ).fetchone()
            if row:
                self.conn.execute(
                    "INSERT OR IGNORE INTO kc_language_demands (kc_id, language_demand_id) VALUES (?, ?)",
                    (kc.id, row["id"]),
                )
        # Math contexts
        for ctx in kc.math_contexts:
            self.conn.execute(
                "INSERT OR IGNORE INTO kc_math_contexts (kc_id, math_concept_id, role) VALUES (?, ?, ?)",
                (kc.id, ctx.math_concept_id, ctx.role),
            )
        self.conn.commit()
        return self.get_kc(kc.id)

    def get_kc(self, kc_id: str) -> KCResponse | None:
        row = self.conn.execute(
            "SELECT * FROM knowledge_components WHERE id = ?", (kc_id,)
        ).fetchone()
        if not row:
            return None
        demands = [
            r["label"]
            for r in self.conn.execute(
                "SELECT ld.label FROM kc_language_demands kld "
                "JOIN language_demands ld ON ld.id = kld.language_demand_id "
                "WHERE kld.kc_id = ?",
                (kc_id,),
            )
        ]
        contexts = [
            MathContextLink(math_concept_id=r["math_concept_id"], role=r["role"])
            for r in self.conn.execute(
                "SELECT math_concept_id, role FROM kc_math_contexts WHERE kc_id = ?",
                (kc_id,),
            )
        ]
        return KCResponse(
            id=row["id"],
            short_description=row["short_description"],
            long_description=row["long_description"],
            is_quotient_node=bool(row["is_quotient_node"]),
            source_schema_id=row["source_schema_id"],
            metadata_status=row["metadata_status"],
            language_demands=demands,
            math_contexts=contexts,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_kcs(
        self,
        offset: int = 0,
        limit: int = 100,
        language_demand: str | None = None,
        math_context: str | None = None,
        search: str | None = None,
        is_quotient_node: bool | None = None,
    ) -> list[KCResponse]:
        query = "SELECT DISTINCT kc.id FROM knowledge_components kc"
        joins = []
        wheres = []
        params: list = []

        if language_demand:
            joins.append(
                "JOIN kc_language_demands kld ON kld.kc_id = kc.id "
                "JOIN language_demands ld ON ld.id = kld.language_demand_id"
            )
            wheres.append("ld.label = ?")
            params.append(language_demand)

        if math_context:
            joins.append(
                "JOIN kc_math_contexts kmc ON kmc.kc_id = kc.id"
            )
            wheres.append("kmc.math_concept_id = ?")
            params.append(math_context)

        if search:
            wheres.append(
                "(kc.short_description LIKE ? OR kc.long_description LIKE ?)"
            )
            params.extend([f"%{search}%", f"%{search}%"])

        if is_quotient_node is not None:
            wheres.append("kc.is_quotient_node = ?")
            params.append(int(is_quotient_node))

        if joins:
            query += " " + " ".join(joins)
        if wheres:
            query += " WHERE " + " AND ".join(wheres)
        query += " ORDER BY kc.id LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        ids = [r["id"] for r in self.conn.execute(query, params)]
        return [self.get_kc(kc_id) for kc_id in ids]

    def update_kc(self, kc_id: str, update: KCUpdate) -> KCResponse | None:
        existing = self.get_kc(kc_id)
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
        if update.metadata_status is not None:
            sets.append("metadata_status = ?")
            params.append(update.metadata_status)
        params.append(kc_id)
        self.conn.execute(
            f"UPDATE knowledge_components SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_kc(kc_id)

    def add_math_context(self, kc_id: str, math_concept_id: str, role: str = "primary") -> KCResponse | None:
        existing = self.get_kc(kc_id)
        if not existing:
            return None
        mc = self.conn.execute("SELECT id FROM math_concepts WHERE id = ?", (math_concept_id,)).fetchone()
        if not mc:
            raise ValueError(f"Math concept '{math_concept_id}' not found")
        self.conn.execute(
            "INSERT OR IGNORE INTO kc_math_contexts (kc_id, math_concept_id, role) VALUES (?, ?, ?)",
            (kc_id, math_concept_id, role),
        )
        self.conn.commit()
        return self.get_kc(kc_id)

    def remove_math_context(self, kc_id: str, math_concept_id: str) -> KCResponse | None:
        existing = self.get_kc(kc_id)
        if not existing:
            return None
        self.conn.execute(
            "DELETE FROM kc_math_contexts WHERE kc_id = ? AND math_concept_id = ?",
            (kc_id, math_concept_id),
        )
        self.conn.commit()
        return self.get_kc(kc_id)

    def update_kc_language_demands(self, kc_id: str, demands: list[str]) -> "KCResponse | None":
        existing = self.get_kc(kc_id)
        if not existing:
            return None
        # Replace all language demands
        self.conn.execute("DELETE FROM kc_language_demands WHERE kc_id = ?", (kc_id,))
        for d in demands:
            # Look up the demand ID by label
            row = self.conn.execute(
                "SELECT id FROM language_demands WHERE label = ?", (d,)
            ).fetchone()
            if row:
                demand_id = row["id"]
            else:
                # Insert new demand if it doesn't exist
                cur = self.conn.execute(
                    "INSERT INTO language_demands (label) VALUES (?)", (d,)
                )
                demand_id = cur.lastrowid
            self.conn.execute(
                "INSERT INTO kc_language_demands (kc_id, language_demand_id) VALUES (?, ?)",
                (kc_id, demand_id),
            )
        self.conn.execute(
            "UPDATE knowledge_components SET updated_at = ? WHERE id = ?",
            (_now(), kc_id),
        )
        self.conn.commit()
        return self.get_kc(kc_id)

    def delete_kc(self, kc_id: str) -> bool:
        # Check for referencing edges
        ref = self.conn.execute(
            "SELECT COUNT(*) as c FROM prerequisite_edges WHERE source_kc_id = ? OR target_kc_id = ?",
            (kc_id, kc_id),
        ).fetchone()
        if ref["c"] > 0:
            return False
        self.conn.execute("DELETE FROM knowledge_components WHERE id = ?", (kc_id,))
        self.conn.commit()
        self.graphs.remove_kc(kc_id)
        return True

    # ── Prerequisite Edges ──

    def create_edge(self, edge: EdgeCreate) -> EdgeResponse:
        # Acyclicity check via NetworkX
        self.graphs.add_prerequisite_edge(edge.source_kc_id, edge.target_kc_id)
        try:
            now = _now()
            self.conn.execute(
                "INSERT INTO prerequisite_edges (source_kc_id, target_kc_id, created_at) VALUES (?, ?, ?)",
                (edge.source_kc_id, edge.target_kc_id, now),
            )
            self.conn.commit()
            row = self.conn.execute(
                "SELECT * FROM prerequisite_edges WHERE source_kc_id = ? AND target_kc_id = ?",
                (edge.source_kc_id, edge.target_kc_id),
            ).fetchone()
            return EdgeResponse(
                id=row["id"],
                source_kc_id=row["source_kc_id"],
                target_kc_id=row["target_kc_id"],
                created_at=row["created_at"],
            )
        except Exception:
            # Rollback graph change on DB error
            self.graphs.remove_prerequisite_edge(edge.source_kc_id, edge.target_kc_id)
            raise

    def list_edges(
        self, offset: int = 0, limit: int = 100,
        source_kc_id: str | None = None, target_kc_id: str | None = None,
    ) -> list[EdgeResponse]:
        query = "SELECT * FROM prerequisite_edges"
        wheres = []
        params: list = []
        if source_kc_id:
            wheres.append("source_kc_id = ?")
            params.append(source_kc_id)
        if target_kc_id:
            wheres.append("target_kc_id = ?")
            params.append(target_kc_id)
        if wheres:
            query += " WHERE " + " AND ".join(wheres)
        query += " ORDER BY id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [
            EdgeResponse(
                id=r["id"],
                source_kc_id=r["source_kc_id"],
                target_kc_id=r["target_kc_id"],
                created_at=r["created_at"],
            )
            for r in self.conn.execute(query, params)
        ]

    def delete_edge(self, edge_id: int) -> bool:
        row = self.conn.execute(
            "SELECT * FROM prerequisite_edges WHERE id = ?", (edge_id,)
        ).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM prerequisite_edges WHERE id = ?", (edge_id,))
        self.conn.commit()
        self.graphs.remove_prerequisite_edge(row["source_kc_id"], row["target_kc_id"])
        return True

    def kc_edges(self, kc_id: str) -> list[EdgeResponse]:
        rows = self.conn.execute(
            "SELECT * FROM prerequisite_edges WHERE source_kc_id = ? OR target_kc_id = ?",
            (kc_id, kc_id),
        )
        return [
            EdgeResponse(
                id=r["id"],
                source_kc_id=r["source_kc_id"],
                target_kc_id=r["target_kc_id"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    # ── Math Concepts ──

    def create_math_concept(self, mc: MathConceptCreate) -> MathConceptResponse:
        now = _now()
        self.conn.execute(
            "INSERT INTO math_concepts (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (mc.id, mc.name, mc.description, now, now),
        )
        self.conn.commit()
        self.graphs.add_math_concept(mc.id)
        return self.get_math_concept(mc.id)

    def get_math_concept(self, concept_id: str) -> MathConceptResponse | None:
        row = self.conn.execute(
            "SELECT * FROM math_concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if not row:
            return None
        return MathConceptResponse(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def list_math_concepts(self, offset: int = 0, limit: int = 100) -> list[MathConceptResponse]:
        rows = self.conn.execute(
            "SELECT * FROM math_concepts ORDER BY id LIMIT ? OFFSET ?", (limit, offset)
        )
        return [
            MathConceptResponse(
                id=r["id"], name=r["name"], description=r["description"],
                created_at=r["created_at"], updated_at=r["updated_at"],
            )
            for r in rows
        ]

    def update_math_concept(self, concept_id: str, update: MathConceptUpdate) -> MathConceptResponse | None:
        existing = self.get_math_concept(concept_id)
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        if update.name is not None:
            sets.append("name = ?")
            params.append(update.name)
        if update.description is not None:
            sets.append("description = ?")
            params.append(update.description)
        params.append(concept_id)
        self.conn.execute(
            f"UPDATE math_concepts SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_math_concept(concept_id)

    def delete_math_concept(self, concept_id: str) -> bool:
        ref = self.conn.execute(
            "SELECT COUNT(*) as c FROM kc_math_contexts WHERE math_concept_id = ?",
            (concept_id,),
        ).fetchone()
        if ref["c"] > 0:
            return False
        self.conn.execute("DELETE FROM math_concepts WHERE id = ?", (concept_id,))
        self.conn.commit()
        self.graphs.remove_math_concept(concept_id)
        return True

    def math_concept_kcs(self, concept_id: str) -> list[KCResponse]:
        ids = [
            r["kc_id"]
            for r in self.conn.execute(
                "SELECT kc_id FROM kc_math_contexts WHERE math_concept_id = ?",
                (concept_id,),
            )
        ]
        return [self.get_kc(kc_id) for kc_id in ids]

    # ── Math Concept Edges ──

    def create_math_concept_edge(self, edge: MathConceptEdgeCreate) -> MathConceptEdgeResponse:
        self.graphs.add_math_concept_edge(edge.source_id, edge.target_id)
        try:
            now = _now()
            self.conn.execute(
                "INSERT INTO math_concept_edges (source_id, target_id, created_at) VALUES (?, ?, ?)",
                (edge.source_id, edge.target_id, now),
            )
            self.conn.commit()
            row = self.conn.execute(
                "SELECT * FROM math_concept_edges WHERE source_id = ? AND target_id = ?",
                (edge.source_id, edge.target_id),
            ).fetchone()
            return MathConceptEdgeResponse(
                id=row["id"], source_id=row["source_id"],
                target_id=row["target_id"], created_at=row["created_at"],
            )
        except Exception:
            self.graphs.remove_math_concept_edge(edge.source_id, edge.target_id)
            raise

    def delete_math_concept_edge(self, edge_id: int) -> bool:
        row = self.conn.execute(
            "SELECT * FROM math_concept_edges WHERE id = ?", (edge_id,)
        ).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM math_concept_edges WHERE id = ?", (edge_id,))
        self.conn.commit()
        self.graphs.remove_math_concept_edge(row["source_id"], row["target_id"])
        return True

    # ── Annotations ──

    def create_annotation(self, ann: AnnotationCreate) -> AnnotationResponse:
        now = _now()
        cur = self.conn.execute(
            "INSERT INTO annotations (entity_type, entity_id, annotation_type, content, author, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ann.entity_type, ann.entity_id, ann.annotation_type, ann.content, ann.author, now),
        )
        self.conn.commit()
        return self.get_annotation(cur.lastrowid)

    def get_annotation(self, ann_id: int) -> AnnotationResponse | None:
        row = self.conn.execute(
            "SELECT * FROM annotations WHERE id = ?", (ann_id,)
        ).fetchone()
        if not row:
            return None
        return AnnotationResponse(
            id=row["id"], entity_type=row["entity_type"], entity_id=row["entity_id"],
            annotation_type=row["annotation_type"], content=row["content"],
            author=row["author"], created_at=row["created_at"], resolved_at=row["resolved_at"],
        )

    def list_annotations(
        self, entity_type: str | None = None, entity_id: str | None = None,
    ) -> list[AnnotationResponse]:
        query = "SELECT * FROM annotations"
        wheres = []
        params: list = []
        if entity_type:
            wheres.append("entity_type = ?")
            params.append(entity_type)
        if entity_id:
            wheres.append("entity_id = ?")
            params.append(entity_id)
        if wheres:
            query += " WHERE " + " AND ".join(wheres)
        query += " ORDER BY id"
        return [
            AnnotationResponse(
                id=r["id"], entity_type=r["entity_type"], entity_id=r["entity_id"],
                annotation_type=r["annotation_type"], content=r["content"],
                author=r["author"], created_at=r["created_at"], resolved_at=r["resolved_at"],
            )
            for r in self.conn.execute(query, params)
        ]

    def update_annotation(self, ann_id: int, content: str | None = None, resolved_at: str | None = None) -> AnnotationResponse | None:
        existing = self.get_annotation(ann_id)
        if not existing:
            return None
        sets = []
        params: list = []
        if content is not None:
            sets.append("content = ?")
            params.append(content)
        if resolved_at is not None:
            sets.append("resolved_at = ?")
            params.append(resolved_at)
        if not sets:
            return existing
        params.append(ann_id)
        self.conn.execute(
            f"UPDATE annotations SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return self.get_annotation(ann_id)

    def delete_annotation(self, ann_id: int) -> bool:
        row = self.conn.execute("SELECT id FROM annotations WHERE id = ?", (ann_id,)).fetchone()
        if not row:
            return False
        self.conn.execute("DELETE FROM annotations WHERE id = ?", (ann_id,))
        self.conn.commit()
        return True

    # ── Frames ──

    def create_frame(self, frame) -> dict:
        now = _now()
        self.conn.execute(
            "INSERT INTO frames (id, name, description, frame_type, is_reference, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (frame.id, frame.name, frame.description, frame.frame_type,
             int(frame.is_reference), now, now),
        )
        self.conn.commit()
        return self.get_frame(frame.id)

    def get_frame(self, frame_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM frames WHERE id = ?", (frame_id,)).fetchone()
        if not row:
            return None
        schemas = [
            self.get_schema(r["id"])
            for r in self.conn.execute(
                "SELECT id FROM schemas WHERE frame_id = ? ORDER BY id", (frame_id,)
            )
        ]
        return {
            "id": row["id"], "name": row["name"], "description": row["description"],
            "frame_type": row["frame_type"], "is_reference": bool(row["is_reference"]),
            "created_at": row["created_at"], "updated_at": row["updated_at"],
            "schemas": schemas,
        }

    def list_frames(self) -> list[dict]:
        rows = self.conn.execute("SELECT id FROM frames ORDER BY id").fetchall()
        return [self.get_frame(r["id"]) for r in rows]

    def update_frame(self, frame_id: str, update) -> dict | None:
        existing = self.conn.execute("SELECT id FROM frames WHERE id = ?", (frame_id,)).fetchone()
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        if update.name is not None:
            sets.append("name = ?")
            params.append(update.name)
        if update.description is not None:
            sets.append("description = ?")
            params.append(update.description)
        params.append(frame_id)
        self.conn.execute(f"UPDATE frames SET {', '.join(sets)} WHERE id = ?", params)
        self.conn.commit()
        return self.get_frame(frame_id)

    def delete_frame(self, frame_id: str) -> bool:
        existing = self.conn.execute("SELECT id FROM frames WHERE id = ?", (frame_id,)).fetchone()
        if not existing:
            return False
        self.conn.execute("DELETE FROM frames WHERE id = ?", (frame_id,))
        self.conn.commit()
        return True

    # ── Schemas ──

    def create_schema(self, frame_id: str, schema) -> dict:
        now = _now()
        self.conn.execute(
            "INSERT INTO schemas (id, frame_id, name, description, parent_schema_id, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (schema.id, frame_id, schema.name, schema.description,
             schema.parent_schema_id, now, now),
        )
        self.conn.commit()
        return self.get_schema(schema.id)

    def get_schema(self, schema_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM schemas WHERE id = ?", (schema_id,)).fetchone()
        if not row:
            return None
        kc_ids = [
            r["kc_id"]
            for r in self.conn.execute(
                "SELECT kc_id FROM schema_kcs WHERE schema_id = ? ORDER BY kc_id",
                (schema_id,),
            )
        ]
        return {
            "id": row["id"], "frame_id": row["frame_id"], "name": row["name"],
            "description": row["description"], "parent_schema_id": row["parent_schema_id"],
            "kc_ids": kc_ids,
            "created_at": row["created_at"], "updated_at": row["updated_at"],
        }

    def list_schemas(self, frame_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id FROM schemas WHERE frame_id = ? ORDER BY id", (frame_id,)
        ).fetchall()
        return [self.get_schema(r["id"]) for r in rows]

    def update_schema(self, schema_id: str, update) -> dict | None:
        existing = self.conn.execute("SELECT id FROM schemas WHERE id = ?", (schema_id,)).fetchone()
        if not existing:
            return None
        sets = ["updated_at = ?"]
        params: list = [_now()]
        provided = update.model_fields_set
        if "name" in provided:
            sets.append("name = ?")
            params.append(update.name)
        if "description" in provided:
            sets.append("description = ?")
            params.append(update.description)
        if "parent_schema_id" in provided:
            sets.append("parent_schema_id = ?")
            params.append(update.parent_schema_id)
        params.append(schema_id)
        self.conn.execute(f"UPDATE schemas SET {', '.join(sets)} WHERE id = ?", params)
        self.conn.commit()
        return self.get_schema(schema_id)

    def delete_schema(self, schema_id: str) -> bool:
        existing = self.conn.execute("SELECT id FROM schemas WHERE id = ?", (schema_id,)).fetchone()
        if not existing:
            return False
        self.conn.execute("DELETE FROM schemas WHERE id = ?", (schema_id,))
        self.conn.commit()
        return True

    def add_kcs_to_schema(self, schema_id: str, kc_ids: list[str]) -> dict | None:
        existing = self.conn.execute("SELECT id FROM schemas WHERE id = ?", (schema_id,)).fetchone()
        if not existing:
            return None
        for kc_id in kc_ids:
            self.conn.execute(
                "INSERT OR IGNORE INTO schema_kcs (schema_id, kc_id) VALUES (?, ?)",
                (schema_id, kc_id),
            )
        self.conn.commit()
        return self.get_schema(schema_id)

    def remove_kc_from_schema(self, schema_id: str, kc_id: str) -> bool:
        row = self.conn.execute(
            "SELECT * FROM schema_kcs WHERE schema_id = ? AND kc_id = ?",
            (schema_id, kc_id),
        ).fetchone()
        if not row:
            return False
        self.conn.execute(
            "DELETE FROM schema_kcs WHERE schema_id = ? AND kc_id = ?",
            (schema_id, kc_id),
        )
        self.conn.commit()
        return True

    def kc_schemas(self, kc_id: str) -> list[dict]:
        """All schemas containing this KC (across all frames)."""
        rows = self.conn.execute(
            "SELECT schema_id FROM schema_kcs WHERE kc_id = ? ORDER BY schema_id",
            (kc_id,),
        ).fetchall()
        return [self.get_schema(r["schema_id"]) for r in rows]

    # ── Bulk Import ──

    def bulk_import(self, data) -> dict:
        """Transactional bulk import. All or nothing."""
        counts = {"math_concepts": 0, "math_concept_edges": 0,
                  "knowledge_components": 0, "prerequisite_edges": 0,
                  "annotations": 0, "frames": 0, "schemas": 0}
        try:
            # Math concepts first (KCs may reference them)
            for mc in data.math_concepts:
                self.create_math_concept(mc)
                counts["math_concepts"] += 1

            for mce in data.math_concept_edges:
                self.create_math_concept_edge(mce)
                counts["math_concept_edges"] += 1

            # KCs
            for kc in data.knowledge_components:
                self.create_kc(kc)
                counts["knowledge_components"] += 1

            # Prerequisite edges
            for edge in data.prerequisite_edges:
                self.create_edge(edge)
                counts["prerequisite_edges"] += 1

            # Annotations
            for ann in data.annotations:
                self.create_annotation(ann)
                counts["annotations"] += 1

            # Frames
            for frame in data.frames:
                now = _now()
                self.conn.execute(
                    "INSERT INTO frames (id, name, description, frame_type, is_reference, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (frame.id, frame.name, frame.description, frame.frame_type,
                     int(frame.is_reference), now, now),
                )
                counts["frames"] += 1

            # Schemas (must be inserted in order respecting parent references)
            # First pass: schemas without parents, second pass: with parents
            remaining = list(data.schemas)
            inserted = set()
            max_passes = len(remaining) + 1
            for _ in range(max_passes):
                if not remaining:
                    break
                next_remaining = []
                for schema in remaining:
                    if schema.parent_schema_id and schema.parent_schema_id not in inserted:
                        next_remaining.append(schema)
                        continue
                    now = _now()
                    self.conn.execute(
                        "INSERT INTO schemas (id, frame_id, name, description, parent_schema_id, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (schema.id, schema.frame_id, schema.name, schema.description,
                         schema.parent_schema_id, now, now),
                    )
                    for kc_id in schema.kc_ids:
                        self.conn.execute(
                            "INSERT OR IGNORE INTO schema_kcs (schema_id, kc_id) VALUES (?, ?)",
                            (schema.id, kc_id),
                        )
                    inserted.add(schema.id)
                    counts["schemas"] += 1
                remaining = next_remaining

            self.conn.commit()
            return {"status": "ok", "counts": counts}
        except Exception as e:
            self.conn.rollback()
            self.graphs.reload()
            raise

    # ── Export ──

    def export_all(self) -> dict:
        kcs = self.list_kcs(limit=100000)
        edges = self.list_edges(limit=100000)
        concepts = self.list_math_concepts(limit=100000)
        annotations = self.list_annotations()

        mc_edges = [
            MathConceptEdgeResponse(
                id=r["id"], source_id=r["source_id"],
                target_id=r["target_id"], created_at=r["created_at"],
            )
            for r in self.conn.execute("SELECT * FROM math_concept_edges ORDER BY id")
        ]

        return {
            "knowledge_components": [kc.model_dump() for kc in kcs],
            "prerequisite_edges": [e.model_dump() for e in edges],
            "math_concepts": [mc.model_dump() for mc in concepts],
            "math_concept_edges": [mce.model_dump() for mce in mc_edges],
            "annotations": [a.model_dump() for a in annotations],
        }
