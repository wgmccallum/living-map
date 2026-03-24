"""Tests for the Moderated Bulk Add staging area (tables, DAL, API)."""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from living_map.app import app
from living_map.database import init_db


@pytest.fixture
def client(tmp_path):
    """Create a test client with a fresh temporary database."""
    db_path = tmp_path / "test.db"
    app.state.db_path = str(db_path)
    with TestClient(app) as c:
        yield c


# ═══════════════════════════════════════════════════════
# Staging Sessions
# ═══════════════════════════════════════════════════════


class TestStagingSessions:
    def test_create_session(self, client):
        resp = client.post("/api/staging", json={
            "id": "fractions-2026-03",
            "topic_name": "Fractions",
            "description": "KCs for fraction concepts, grades 3-5",
            "source_documents": ["CCSS-fractions.docx"],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "fractions-2026-03"
        assert data["topic_name"] == "Fractions"
        assert data["status"] == "active"
        assert data["source_documents"] == ["CCSS-fractions.docx"]
        assert data["statistics"]["total_kcs"] == 0

    def test_list_sessions(self, client):
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        client.post("/api/staging", json={"id": "s2", "topic_name": "Topic 2"})
        resp = client.get("/api/staging")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_session(self, client):
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        resp = client.get("/api/staging/s1")
        assert resp.status_code == 200
        assert resp.json()["topic_name"] == "Topic 1"

    def test_get_session_not_found(self, client):
        resp = client.get("/api/staging/nonexistent")
        assert resp.status_code == 404

    def test_update_session(self, client):
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        resp = client.patch("/api/staging/s1", json={"status": "tier2_review"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "tier2_review"

    def test_delete_active_session(self, client):
        """Active sessions can be deleted directly."""
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        resp = client.delete("/api/staging/s1")
        assert resp.status_code == 204
        resp = client.get("/api/staging/s1")
        assert resp.status_code == 404

    def test_delete_session_force(self, client):
        """Force-delete works on sessions in any status."""
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        client.patch("/api/staging/s1", json={"status": "committed"})
        # Without force, committed sessions can't be deleted
        resp = client.delete("/api/staging/s1")
        assert resp.status_code == 409
        # With force, it works
        resp = client.delete("/api/staging/s1?force=true")
        assert resp.status_code == 204

    def test_delete_session_cascades(self, client):
        """Deleting a session removes all its KCs, edges, and schemas."""
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        client.post("/api/staging/s1/kcs", json={
            "id": "KC-001", "source_text": "Test KC 1", "stage_status": "proposed"
        })
        client.post("/api/staging/s1/kcs", json={
            "id": "KC-002", "source_text": "Test KC 2", "stage_status": "proposed"
        })
        client.post("/api/staging/s1/edges", json={
            "source_kc_id": "KC-001", "target_kc_id": "KC-002"
        })
        client.post("/api/staging/s1/schemas", json={
            "id": "SCH-001", "name": "Test Schema"
        })
        # Verify data exists
        assert len(client.get("/api/staging/s1/kcs").json()) == 2
        assert len(client.get("/api/staging/s1/edges").json()) == 1
        # Delete session
        resp = client.delete("/api/staging/s1")
        assert resp.status_code == 204
        # Session is gone
        assert client.get("/api/staging/s1").status_code == 404

    def test_duplicate_session_id(self, client):
        client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 1"})
        resp = client.post("/api/staging", json={"id": "s1", "topic_name": "Topic 2"})
        assert resp.status_code == 409


# ═══════════════════════════════════════════════════════
# Staged KCs
# ═══════════════════════════════════════════════════════


class TestStagedKCs:
    def _create_session(self, client):
        client.post("/api/staging", json={"id": "test-session", "topic_name": "Test"})

    def test_create_and_get_kc(self, client):
        self._create_session(client)
        resp = client.post("/api/staging/test-session/kcs", json={
            "id": "STAGE-TST-001",
            "short_description": "Count to 10",
            "source_text": "CCSS.MATH.K.CC.1",
            "language_demands": ["Speaking", "Listening"],
            "kc_type": "Skill",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "STAGE-TST-001"
        assert data["session_id"] == "test-session"
        assert data["stage_status"] == "proposed"
        assert data["language_demands"] == ["Speaking", "Listening"]

    def test_list_kcs_with_filter(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={
            "id": "STAGE-TST-001", "stage_status": "proposed",
        })
        client.post("/api/staging/test-session/kcs", json={
            "id": "STAGE-TST-002", "stage_status": "grain_approved",
        })
        # All
        resp = client.get("/api/staging/test-session/kcs")
        assert len(resp.json()) == 2
        # Filtered
        resp = client.get("/api/staging/test-session/kcs?stage_status=proposed")
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == "STAGE-TST-001"

    def test_update_kc(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        resp = client.patch("/api/staging/test-session/kcs/STAGE-TST-001", json={
            "short_description": "Updated description",
            "stage_status": "grain_approved",
        })
        assert resp.status_code == 200
        assert resp.json()["short_description"] == "Updated description"
        assert resp.json()["stage_status"] == "grain_approved"

    def test_batch_update_kcs(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-002"})
        resp = client.post("/api/staging/test-session/kcs/batch-update", json={
            "kc_ids": ["STAGE-TST-001", "STAGE-TST-002"],
            "updates": {"stage_status": "formulated"},
        })
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 2
        assert all(r["stage_status"] == "formulated" for r in results)

    def test_delete_kc(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        resp = client.delete("/api/staging/test-session/kcs/STAGE-TST-001")
        assert resp.status_code == 204
        resp = client.get("/api/staging/test-session/kcs/STAGE-TST-001")
        assert resp.status_code == 404

    def test_add_comment(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        resp = client.post("/api/staging/test-session/kcs/STAGE-TST-001/comment", json={
            "author": "reviewer1",
            "text": "This should be split into two KCs",
        })
        assert resp.status_code == 201
        comments = resp.json()["reviewer_comments"]
        assert len(comments) == 1
        assert comments[0]["author"] == "reviewer1"
        assert comments[0]["text"] == "This should be split into two KCs"

    def test_flag_kc(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        resp = client.post("/api/staging/test-session/kcs/STAGE-TST-001/flag")
        assert resp.status_code == 200
        assert resp.json()["stage_status"] == "flagged"

    def test_session_statistics(self, client):
        self._create_session(client)
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        client.post("/api/staging/test-session/kcs", json={
            "id": "STAGE-TST-002", "stage_status": "grain_approved",
        })
        resp = client.get("/api/staging/test-session")
        stats = resp.json()["statistics"]
        assert stats["total_kcs"] == 2
        assert stats["by_stage"]["proposed"] == 1
        assert stats["by_stage"]["grain_approved"] == 1


# ═══════════════════════════════════════════════════════
# Staged Edges
# ═══════════════════════════════════════════════════════


class TestStagedEdges:
    def _setup(self, client):
        client.post("/api/staging", json={"id": "test-session", "topic_name": "Test"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-002"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-003"})

    def test_create_and_list_edges(self, client):
        self._setup(client)
        resp = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-001",
            "target_kc_id": "STAGE-TST-002",
            "ai_reasoning": "Counting is prerequisite to addition",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["source_kc_id"] == "STAGE-TST-001"
        assert data["status"] == "proposed"

        resp = client.get("/api/staging/test-session/edges")
        assert len(resp.json()) == 1

    def test_confirm_edge(self, client):
        self._setup(client)
        resp = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-001",
            "target_kc_id": "STAGE-TST-002",
        })
        edge_id = resp.json()["id"]
        resp = client.patch(f"/api/staging/test-session/edges/{edge_id}", json={
            "status": "confirmed",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    def test_cycle_detection_on_confirm(self, client):
        self._setup(client)
        # Create A -> B and B -> C
        r1 = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-001", "target_kc_id": "STAGE-TST-002",
        })
        r2 = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-002", "target_kc_id": "STAGE-TST-003",
        })
        # Confirm both
        client.patch(f"/api/staging/test-session/edges/{r1.json()['id']}", json={"status": "confirmed"})
        client.patch(f"/api/staging/test-session/edges/{r2.json()['id']}", json={"status": "confirmed"})
        # Try to confirm C -> A (creates cycle)
        r3 = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-003", "target_kc_id": "STAGE-TST-001",
        })
        resp = client.patch(f"/api/staging/test-session/edges/{r3.json()['id']}", json={
            "status": "confirmed",
        })
        assert resp.status_code == 409

    def test_validate_edges(self, client):
        self._setup(client)
        r1 = client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-001", "target_kc_id": "STAGE-TST-002",
        })
        client.patch(f"/api/staging/test-session/edges/{r1.json()['id']}", json={"status": "confirmed"})
        resp = client.post("/api/staging/test-session/edges/validate")
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_filter_edges_by_status(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-001", "target_kc_id": "STAGE-TST-002",
        })
        client.post("/api/staging/test-session/edges", json={
            "source_kc_id": "STAGE-TST-002", "target_kc_id": "STAGE-TST-003",
            "status": "confirmed",
        })
        # Note: setting status on create doesn't trigger cycle check (only on update to confirmed)
        resp = client.get("/api/staging/test-session/edges?status=proposed")
        assert len(resp.json()) == 1


# ═══════════════════════════════════════════════════════
# Staged Schemas
# ═══════════════════════════════════════════════════════


class TestStagedSchemas:
    def _setup(self, client):
        client.post("/api/staging", json={"id": "test-session", "topic_name": "Test"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-001"})
        client.post("/api/staging/test-session/kcs", json={"id": "STAGE-TST-002"})

    def test_create_and_list_schemas(self, client):
        self._setup(client)
        resp = client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001",
            "name": "Basic Counting",
            "description": "Fundamental counting skills",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] == "STAGE-TST-S001"
        assert data["name"] == "Basic Counting"
        assert data["status"] == "proposed"
        assert data["kc_ids"] == []

        resp = client.get("/api/staging/test-session/schemas")
        assert len(resp.json()) == 1

    def test_add_kcs_to_schema(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001", "name": "Basic Counting",
        })
        resp = client.post("/api/staging/test-session/schemas/STAGE-TST-S001/kcs", json={
            "kc_ids": ["STAGE-TST-001", "STAGE-TST-002"],
        })
        assert resp.status_code == 201
        assert set(resp.json()["kc_ids"]) == {"STAGE-TST-001", "STAGE-TST-002"}

    def test_remove_kc_from_schema(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001", "name": "Basic Counting",
        })
        client.post("/api/staging/test-session/schemas/STAGE-TST-S001/kcs", json={
            "kc_ids": ["STAGE-TST-001", "STAGE-TST-002"],
        })
        resp = client.delete("/api/staging/test-session/schemas/STAGE-TST-S001/kcs/STAGE-TST-001")
        assert resp.status_code == 204
        resp = client.get("/api/staging/test-session/schemas")
        assert resp.json()[0]["kc_ids"] == ["STAGE-TST-002"]

    def test_nested_schemas(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001", "name": "Parent Schema",
        })
        resp = client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S002", "name": "Child Schema",
            "parent_schema_id": "STAGE-TST-S001",
        })
        assert resp.status_code == 201
        assert resp.json()["parent_schema_id"] == "STAGE-TST-S001"

    def test_validate_schemas(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001", "name": "Schema 1", "status": "confirmed",
        })
        client.post("/api/staging/test-session/schemas/STAGE-TST-S001/kcs", json={
            "kc_ids": ["STAGE-TST-001"],
        })
        resp = client.post("/api/staging/test-session/schemas/validate")
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_validate_catches_empty_schemas(self, client):
        self._setup(client)
        client.post("/api/staging/test-session/schemas", json={
            "id": "STAGE-TST-S001", "name": "Empty Schema", "status": "confirmed",
        })
        resp = client.post("/api/staging/test-session/schemas/validate")
        data = resp.json()
        assert data["valid"] is False
        assert "STAGE-TST-S001" in data["empty_schemas"]


# ═══════════════════════════════════════════════════════
# Integration: Full Workflow
# ═══════════════════════════════════════════════════════


class TestSplitKC:
    def test_split_kc(self, client):
        """Splitting a KC creates children and marks parent stale."""
        client.post("/api/staging", json={"id": "split-test", "topic_name": "Split"})
        client.post("/api/staging/split-test/kcs", json={
            "id": "STAGE-SP-001", "source_text": "Count to 20", "stage_status": "proposed"
        })
        resp = client.post("/api/staging/split-test/kcs/STAGE-SP-001/split", json={
            "children": ["Count to 10", "Count from 11 to 20"]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["parent_status"] == "stale"
        assert len(data["children"]) == 2
        assert data["children"][0]["id"] == "STAGE-SP-001-a"
        assert data["children"][1]["id"] == "STAGE-SP-001-b"
        # Verify parent is stale
        parent = client.get("/api/staging/split-test/kcs/STAGE-SP-001").json()
        assert parent["stage_status"] == "stale"
        # Verify children exist with grain_approved status
        all_kcs = client.get("/api/staging/split-test/kcs").json()
        ids = [k["id"] for k in all_kcs]
        assert "STAGE-SP-001-a" in ids
        assert "STAGE-SP-001-b" in ids
        child_a = next(k for k in all_kcs if k["id"] == "STAGE-SP-001-a")
        assert child_a["stage_status"] == "grain_approved"

    def test_split_requires_two_children(self, client):
        client.post("/api/staging", json={"id": "split-test2", "topic_name": "Split2"})
        client.post("/api/staging/split-test2/kcs", json={
            "id": "STAGE-SP2-001", "source_text": "Something", "stage_status": "proposed"
        })
        resp = client.post("/api/staging/split-test2/kcs/STAGE-SP2-001/split", json={
            "children": ["Only one"]
        })
        assert resp.status_code == 400


class TestMergeKC:
    def _setup_merge_session(self, client):
        """Helper: create a session with two KCs ready to merge."""
        client.post("/api/staging", json={"id": "merge-test", "topic_name": "Merge"})
        client.post("/api/staging/merge-test/kcs", json={
            "id": "STAGE-MG-001", "source_text": "Count forward by ones", "stage_status": "proposed"
        })
        client.post("/api/staging/merge-test/kcs", json={
            "id": "STAGE-MG-002", "source_text": "Count forward starting from 1", "stage_status": "proposed"
        })

    def test_merge_keep_mode(self, client):
        """Merge in keep mode: survivor stays, other becomes stale."""
        self._setup_merge_session(client)
        resp = client.post("/api/staging/merge-test/merge", json={
            "mode": "keep",
            "source_ids": ["STAGE-MG-001", "STAGE-MG-002"],
            "survivor_id": "STAGE-MG-001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "keep"
        assert data["survivor_id"] == "STAGE-MG-001"
        assert data["retired_ids"] == ["STAGE-MG-002"]
        # Verify statuses
        kc1 = client.get("/api/staging/merge-test/kcs/STAGE-MG-001").json()
        kc2 = client.get("/api/staging/merge-test/kcs/STAGE-MG-002").json()
        assert kc1["stage_status"] == "proposed"  # survivor unchanged
        assert kc2["stage_status"] == "stale"

    def test_merge_create_mode(self, client):
        """Merge in create mode: new KC created, both sources become stale."""
        self._setup_merge_session(client)
        resp = client.post("/api/staging/merge-test/merge", json={
            "mode": "create",
            "source_ids": ["STAGE-MG-001", "STAGE-MG-002"],
            "description": "Count forward by ones starting from any number",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "create"
        assert data["merged_kc"]["id"] == "STAGE-MG-001-merged"
        assert len(data["retired_ids"]) == 2
        # Verify both sources are stale
        kc1 = client.get("/api/staging/merge-test/kcs/STAGE-MG-001").json()
        kc2 = client.get("/api/staging/merge-test/kcs/STAGE-MG-002").json()
        assert kc1["stage_status"] == "stale"
        assert kc2["stage_status"] == "stale"
        # Verify merged KC exists
        merged = client.get("/api/staging/merge-test/kcs/STAGE-MG-001-merged").json()
        assert merged["stage_status"] == "proposed"
        assert "Count forward by ones starting from any number" in merged["source_text"]

    def test_merge_requires_two_sources(self, client):
        """Merge with fewer than 2 sources should fail."""
        client.post("/api/staging", json={"id": "merge-test2", "topic_name": "Merge2"})
        client.post("/api/staging/merge-test2/kcs", json={
            "id": "STAGE-MG2-001", "source_text": "Solo KC", "stage_status": "proposed"
        })
        resp = client.post("/api/staging/merge-test2/merge", json={
            "mode": "keep",
            "source_ids": ["STAGE-MG2-001"],
            "survivor_id": "STAGE-MG2-001",
        })
        assert resp.status_code == 400

    def test_merge_invalid_survivor(self, client):
        """Survivor must be one of the source IDs."""
        self._setup_merge_session(client)
        resp = client.post("/api/staging/merge-test/merge", json={
            "mode": "keep",
            "source_ids": ["STAGE-MG-001", "STAGE-MG-002"],
            "survivor_id": "STAGE-MG-999",
        })
        assert resp.status_code == 400

    def test_merge_invalid_mode(self, client):
        self._setup_merge_session(client)
        resp = client.post("/api/staging/merge-test/merge", json={
            "mode": "invalid",
            "source_ids": ["STAGE-MG-001", "STAGE-MG-002"],
        })
        assert resp.status_code == 400


class TestStagingWorkflow:
    def test_full_session_lifecycle(self, client):
        """Simulate a mini topic DAG through all stages."""
        # 1. Create session
        client.post("/api/staging", json={
            "id": "mini-test",
            "topic_name": "Mini Test Topic",
            "source_documents": ["test.tex"],
        })

        # 2. Add proposed KCs (Stage 1 output)
        for i in range(1, 4):
            client.post("/api/staging/mini-test/kcs", json={
                "id": f"STAGE-MT-{i:03d}",
                "source_text": f"Standard {i}",
                "source_reference": f"TEST.{i}",
            })

        # 3. Approve grain size (Stage 2)
        client.post("/api/staging/mini-test/kcs/batch-update", json={
            "kc_ids": ["STAGE-MT-001", "STAGE-MT-002", "STAGE-MT-003"],
            "updates": {"stage_status": "grain_approved"},
        })

        # 4. Formulate KCs (Stage 3)
        for i in range(1, 4):
            client.patch(f"/api/staging/mini-test/kcs/STAGE-MT-{i:03d}", json={
                "short_description": f"KC {i} description",
                "long_description": f"Detailed behavioral definition for KC {i}",
                "language_demands": ["Speaking"],
                "kc_type": "Skill",
                "stage_status": "formulated",
            })

        # 5. Add prerequisite edges (Stage 4)
        r1 = client.post("/api/staging/mini-test/edges", json={
            "source_kc_id": "STAGE-MT-001",
            "target_kc_id": "STAGE-MT-002",
            "ai_reasoning": "KC 1 is foundational for KC 2",
        })
        r2 = client.post("/api/staging/mini-test/edges", json={
            "source_kc_id": "STAGE-MT-002",
            "target_kc_id": "STAGE-MT-003",
            "ai_reasoning": "KC 2 builds toward KC 3",
        })
        # Confirm edges
        client.patch(f"/api/staging/mini-test/edges/{r1.json()['id']}", json={"status": "confirmed"})
        client.patch(f"/api/staging/mini-test/edges/{r2.json()['id']}", json={"status": "confirmed"})
        # Update KC statuses
        client.post("/api/staging/mini-test/kcs/batch-update", json={
            "kc_ids": ["STAGE-MT-001", "STAGE-MT-002", "STAGE-MT-003"],
            "updates": {"stage_status": "edges_confirmed"},
        })

        # 6. Assign to schema (Stage 5)
        client.post("/api/staging/mini-test/schemas", json={
            "id": "STAGE-MT-S001",
            "name": "Mini Topic Schema",
        })
        client.post("/api/staging/mini-test/schemas/STAGE-MT-S001/kcs", json={
            "kc_ids": ["STAGE-MT-001", "STAGE-MT-002", "STAGE-MT-003"],
        })
        client.post("/api/staging/mini-test/kcs/batch-update", json={
            "kc_ids": ["STAGE-MT-001", "STAGE-MT-002", "STAGE-MT-003"],
            "updates": {"stage_status": "schema_assigned"},
        })

        # 7. Check final state
        resp = client.get("/api/staging/mini-test")
        session = resp.json()
        stats = session["statistics"]
        assert stats["total_kcs"] == 3
        assert stats["by_stage"]["schema_assigned"] == 3
        assert stats["edges"]["confirmed"] == 2

        # 8. Move to tier2_review
        client.patch("/api/staging/mini-test", json={"status": "tier2_review"})
        resp = client.get("/api/staging/mini-test")
        assert resp.json()["status"] == "tier2_review"
