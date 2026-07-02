"""Tests for frame deletion (cleanup of frame-exclusive KCs, edges, annotations)."""

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


def build_frames(client):
    """Two frames: f1 owns KC-A/KC-B (KC-B shared with f2), f2 owns KC-B/KC-C."""
    for kc in ["KC-A", "KC-B", "KC-C"]:
        assert client.post("/api/kcs", json={
            "id": kc, "short_description": kc}).status_code == 201
    assert client.post("/api/edges", json={
        "source_kc_id": "KC-A", "target_kc_id": "KC-B"}).status_code == 201
    assert client.post("/api/edges", json={
        "source_kc_id": "KC-B", "target_kc_id": "KC-C"}).status_code == 201
    for fid in ["f1", "f2"]:
        assert client.post("/api/frames", json={
            "id": fid, "name": fid, "frame_type": "internal"}).status_code == 201
        assert client.post(f"/api/frames/{fid}/schemas", json={
            "id": "leaf", "name": "Leaf"}).status_code == 201
    client.post("/api/frames/f1/schemas/leaf/kcs", json={"kc_ids": ["KC-A", "KC-B"]})
    client.post("/api/frames/f2/schemas/leaf/kcs", json={"kc_ids": ["KC-B", "KC-C"]})
    client.post("/api/annotations", json={
        "entity_type": "kc", "entity_id": "KC-A",
        "annotation_type": "kc_type", "content": "Skill"})


class TestDeleteFrame:
    def test_deletes_exclusive_kcs_keeps_shared(self, client):
        build_frames(client)
        report = client.delete("/api/frames/f1")
        assert report.status_code == 200
        body = report.json()
        assert body["kcs_deleted"] == 1      # KC-A only; KC-B shared with f2
        assert body["schemas_deleted"] == 1

        assert client.get("/api/kcs/KC-A").status_code == 404
        assert client.get("/api/kcs/KC-B").status_code == 200
        assert client.get("/api/kcs/KC-C").status_code == 200
        assert client.get("/api/frames/f1").status_code == 404
        assert client.get("/api/frames/f2").status_code == 200

        # KC-A's edge is gone, KC-B -> KC-C survives
        edges = client.get("/api/kcs/KC-B/edges").json()
        pairs = {(e["source_kc_id"], e["target_kc_id"]) for e in edges}
        assert pairs == {("KC-B", "KC-C")}

        # KC-A's annotations are gone
        anns = client.get("/api/annotations", params={
            "entity_type": "kc", "entity_id": "KC-A"}).json()
        assert anns == []

    def test_reference_frame_refused(self, client):
        assert client.post("/api/frames", json={
            "id": "ref", "name": "Reference", "frame_type": "internal",
            "is_reference": True}).status_code == 201
        resp = client.delete("/api/frames/ref")
        assert resp.status_code == 409
        assert client.get("/api/frames/ref").status_code == 200

    def test_unknown_frame_404(self, client):
        assert client.delete("/api/frames/nope").status_code == 404
