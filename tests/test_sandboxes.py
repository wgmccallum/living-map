"""Tests for capability-URL per-sandbox databases."""

import pytest
from fastapi.testclient import TestClient

from living_map.app import app


@pytest.fixture
def client(tmp_path):
    app.state.db_path = str(tmp_path / "base.db")
    app.state.sandbox_dir = str(tmp_path / "sandboxes")
    with TestClient(app) as c:
        yield c


def _mk_kc(client, kc_id, headers=None):
    return client.post(
        "/api/kcs", json={"id": kc_id, "short_description": kc_id}, headers=headers or {}
    )


class TestSandboxes:
    def test_create_copies_base_and_isolates_writes(self, client):
        _mk_kc(client, "BASE-1")
        sb = client.post("/api/sandboxes", json={"name": "exp"}).json()
        assert sb["url"] == f"/staging?sandbox={sb['id']}"
        H = {"X-Sandbox-Id": sb["id"]}
        # The sandbox is a copy → it sees the base KC.
        assert [k["id"] for k in client.get("/api/kcs", headers=H).json()] == ["BASE-1"]
        # Writes in the sandbox stay in the sandbox.
        _mk_kc(client, "SBX-1", H)
        assert sorted(k["id"] for k in client.get("/api/kcs", headers=H).json()) == ["BASE-1", "SBX-1"]
        assert [k["id"] for k in client.get("/api/kcs").json()] == ["BASE-1"]

    def test_sandbox_is_a_snapshot(self, client):
        _mk_kc(client, "BASE-1")
        sid = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        _mk_kc(client, "BASE-2")  # added to base AFTER the sandbox was created
        ids = [k["id"] for k in client.get("/api/kcs", headers={"X-Sandbox-Id": sid}).json()]
        assert ids == ["BASE-1"]

    def test_two_sandboxes_independent(self, client):
        a = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        b = client.post("/api/sandboxes", json={"name": "b"}).json()["id"]
        _mk_kc(client, "A-ONLY", {"X-Sandbox-Id": a})
        assert [k["id"] for k in client.get("/api/kcs", headers={"X-Sandbox-Id": b}).json()] == []
        assert [k["id"] for k in client.get("/api/kcs", headers={"X-Sandbox-Id": a}).json()] == ["A-ONLY"]

    def test_unknown_sandbox_404(self, client):
        assert client.get("/api/kcs", headers={"X-Sandbox-Id": "nope"}).status_code == 404
        assert client.get("/api/kcs?sandbox=nope").status_code == 404

    def test_query_param_also_routes(self, client):
        _mk_kc(client, "BASE-1")
        sid = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        _mk_kc(client, "SBX", {"X-Sandbox-Id": sid})
        ids = sorted(k["id"] for k in client.get(f"/api/kcs?sandbox={sid}").json())
        assert ids == ["BASE-1", "SBX"]

    def test_list_and_delete(self, client):
        sid = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        lst = client.get("/api/sandboxes").json()
        assert len(lst) == 1 and lst[0]["id"] == sid and lst[0]["name"] == "a"
        assert client.delete(f"/api/sandboxes/{sid}").status_code == 204
        assert client.get("/api/sandboxes").json() == []
        assert client.get("/api/kcs", headers={"X-Sandbox-Id": sid}).status_code == 404
        assert client.delete(f"/api/sandboxes/{sid}").status_code == 404  # already gone

    def test_management_routes_ignore_sandbox_context(self, client):
        sid = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        # Listing with the sandbox header still hits the base registry (not scoped/404).
        lst = client.get("/api/sandboxes", headers={"X-Sandbox-Id": sid}).json()
        assert any(s["id"] == sid for s in lst)

    def test_staging_tables_are_isolated_too(self, client):
        client.post("/api/staging", json={"id": "base-sess", "topic_name": "T"})
        sid = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        H = {"X-Sandbox-Id": sid}
        client.post("/api/staging", json={"id": "sbx-sess", "topic_name": "T2"}, headers=H)
        base = {s["id"] for s in client.get("/api/staging").json()}
        sbx = {s["id"] for s in client.get("/api/staging", headers=H).json()}
        assert "base-sess" in base and "sbx-sess" not in base
        assert {"base-sess", "sbx-sess"} <= sbx

    def test_branch_from_another_sandbox(self, client):
        _mk_kc(client, "BASE-1")
        a = client.post("/api/sandboxes", json={"name": "a"}).json()["id"]
        _mk_kc(client, "A-ONLY", {"X-Sandbox-Id": a})
        # Branch b from a → b should contain a's edits.
        b = client.post("/api/sandboxes", json={"name": "b", "source": a}).json()["id"]
        ids = sorted(k["id"] for k in client.get("/api/kcs", headers={"X-Sandbox-Id": b}).json())
        assert ids == ["A-ONLY", "BASE-1"]

    def test_invalid_id_rejected(self, client):
        # path-traversal-ish id must not resolve to a file
        assert client.get("/api/kcs", headers={"X-Sandbox-Id": "../etc"}).status_code == 404
