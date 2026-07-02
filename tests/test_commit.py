"""Tests for the staging commit pipeline (Step 7)."""

import pytest
from fastapi.testclient import TestClient

from living_map.app import app


@pytest.fixture
def client(tmp_path):
    """Create a test client with a fresh temporary database."""
    db_path = tmp_path / "test.db"
    app.state.db_path = str(db_path)
    with TestClient(app) as c:
        yield c


SESSION = "lf-test"
REQ = {
    "frame_id": "lf-test-v1",
    "frame_name": "LF Test v1",
    "id_prefix_from": "STAGE-LF-",
    "id_prefix_to": "LF-",
}


def build_session(client, assign_kc_ids=None, extra_edges=None):
    """Create a small committable session: 3 KCs, 2 confirmed edges, root+leaf schemas."""
    resp = client.post("/api/staging", json={"id": SESSION, "topic_name": "LF Test"})
    assert resp.status_code == 201
    kcs = [
        {"id": "STAGE-LF-001", "short_description": "KC one", "kc_type": "Skill",
         "language_demands": ["Reading"], "stage_status": "schema_assigned"},
        {"id": "STAGE-LF-002", "short_description": "KC two", "kc_type": "Principle",
         "stage_status": "schema_assigned"},
        {"id": "STAGE-LF-003", "short_description": "KC three",
         "stage_status": "schema_assigned"},
    ]
    assert client.post(f"/api/staging/{SESSION}/kcs", json=kcs).status_code == 201
    edges = [
        {"source_kc_id": "STAGE-LF-001", "target_kc_id": "STAGE-LF-002", "status": "confirmed"},
        {"source_kc_id": "STAGE-LF-002", "target_kc_id": "STAGE-LF-003", "status": "confirmed"},
    ] + (extra_edges or [])
    assert client.post(f"/api/staging/{SESSION}/edges", json=edges).status_code == 201
    assert client.post(f"/api/staging/{SESSION}/schemas", json={
        "id": "root", "name": "Root", "status": "confirmed"}).status_code == 201
    assert client.post(f"/api/staging/{SESSION}/schemas", json={
        "id": "leaf", "name": "Leaf", "parent_schema_id": "root",
        "status": "confirmed"}).status_code == 201
    if assign_kc_ids is None:
        assign_kc_ids = ["STAGE-LF-001", "STAGE-LF-002", "STAGE-LF-003"]
    resp = client.post(f"/api/staging/{SESSION}/schemas/leaf/kcs", json={"kc_ids": assign_kc_ids})
    assert resp.status_code == 201


class TestPrecommit:
    def test_ready_session_passes(self, client):
        build_session(client)
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["blockers"] == []
        assert r["validation"]["valid"] is True
        assert r["ready"] is True
        assert r["counts"] == {
            "kcs": 3, "edges": 2, "schemas": 2, "memberships": 3,
            "proposed_edges_excluded": 0,
        }
        assert r["id_map_sample"]["STAGE-LF-001"] == "LF-001"

    def test_unassigned_kc_blocks(self, client):
        build_session(client, assign_kc_ids=["STAGE-LF-001", "STAGE-LF-002"])
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["ready"] is False
        assert any("no schema" in b for b in r["blockers"])

    def test_unreviewed_kc_blocks(self, client):
        build_session(client)
        client.post(f"/api/staging/{SESSION}/kcs", json={
            "id": "STAGE-LF-004", "short_description": "unreviewed",
            "stage_status": "proposed"})
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["ready"] is False
        assert any("not fully reviewed" in b for b in r["blockers"])

    def test_cycle_fails_validation(self, client):
        build_session(client, extra_edges=[
            {"source_kc_id": "STAGE-LF-003", "target_kc_id": "STAGE-LF-001",
             "status": "confirmed"}])
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["validation"]["checks"]["acyclic"] is False
        assert r["ready"] is False

    def test_proposed_edges_warn_but_dont_block(self, client):
        build_session(client, extra_edges=[
            {"source_kc_id": "STAGE-LF-001", "target_kc_id": "STAGE-LF-003",
             "status": "proposed"}])
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["ready"] is True
        assert r["counts"]["edges"] == 2
        assert r["counts"]["proposed_edges_excluded"] == 1
        assert any("NOT be committed" in w for w in r["warnings"])

    def test_id_collision_blocks(self, client):
        build_session(client)
        client.post("/api/kcs", json={"id": "LF-002", "short_description": "existing"})
        r = client.post(f"/api/staging/{SESSION}/precommit", json=REQ).json()
        assert r["ready"] is False
        assert any("already exist" in b for b in r["blockers"])

    def test_unknown_session_404(self, client):
        assert client.post("/api/staging/nope/precommit", json=REQ).status_code == 404


class TestCommit:
    def test_commit_creates_frame_kcs_edges(self, client):
        build_session(client)
        r = client.post(f"/api/staging/{SESSION}/commit", json=REQ).json()
        assert r["committed"] is True
        assert r["frame_validation"]["valid"] is True

        frame = client.get("/api/frames/lf-test-v1").json()
        assert frame["name"] == "LF Test v1"
        leaf = next(s for s in frame["schemas"] if s["id"] == "leaf")
        assert sorted(leaf["kc_ids"]) == ["LF-001", "LF-002", "LF-003"]
        root = next(s for s in frame["schemas"] if s["id"] == "root")
        assert leaf["parent_schema_id"] == "root" and root["parent_schema_id"] is None

        assert client.get("/api/kcs/LF-001").status_code == 200
        edges = client.get("/api/kcs/LF-002/edges").json()
        pairs = {(e["source_kc_id"], e["target_kc_id"]) for e in edges}
        assert ("LF-001", "LF-002") in pairs and ("LF-002", "LF-003") in pairs

        anns = client.get("/api/annotations", params={"entity_type": "kc", "entity_id": "LF-001"}).json()
        by_type = {a["annotation_type"]: a["content"] for a in anns}
        assert by_type["kc_type"] == "Skill"
        assert "staging session lf-test" in by_type["provenance"]

        session = client.get(f"/api/staging/{SESSION}").json()
        assert session["status"] == "committed"

    def test_commit_requires_frame_name(self, client):
        build_session(client)
        req = {**REQ, "frame_name": None}
        assert client.post(f"/api/staging/{SESSION}/commit", json=req).status_code == 422

    def test_recommit_blocked(self, client):
        build_session(client)
        assert client.post(f"/api/staging/{SESSION}/commit", json=REQ).json()["committed"] is True
        r2 = client.post(f"/api/staging/{SESSION}/commit", json={**REQ, "frame_id": "lf-test-v2"}).json()
        assert r2["committed"] is False
        assert any("already been committed" in b for b in r2["blockers"])

    def test_blocked_commit_writes_nothing(self, client):
        build_session(client, assign_kc_ids=["STAGE-LF-001", "STAGE-LF-002"])
        r = client.post(f"/api/staging/{SESSION}/commit", json=REQ).json()
        assert r["committed"] is False
        assert client.get("/api/frames/lf-test-v1").status_code == 404
        assert client.get("/api/kcs/LF-001").status_code == 404
        assert client.get(f"/api/staging/{SESSION}").json()["status"] == "active"

    def test_stale_kcs_and_rejected_edges_excluded(self, client):
        build_session(client)
        client.post(f"/api/staging/{SESSION}/kcs", json={
            "id": "STAGE-LF-099", "short_description": "tombstone",
            "stage_status": "stale"})
        r = client.post(f"/api/staging/{SESSION}/commit", json=REQ).json()
        assert r["committed"] is True
        assert r["counts"]["kcs"] == 3
        assert client.get("/api/kcs/LF-099").status_code == 404
