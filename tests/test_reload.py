"""Tests for the POST /api/reload admin route.

Direct-sqlite edits bypass the DAL, so the in-memory NetworkX graphs go stale
until reloaded. These tests simulate a direct edit with a second connection
and verify /api/reload brings graph-backed endpoints back in sync.
"""

import sqlite3

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


def _direct_insert_edge(db_path, source, target):
    """Insert a prerequisite edge outside the DAL, as sqlite3 CLI edits would."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO prerequisite_edges (source_kc_id, target_kc_id) VALUES (?, ?)",
            (source, target),
        )
        conn.commit()
    finally:
        conn.close()


class TestReload:
    def test_reload_picks_up_direct_sqlite_edits(self, client, tmp_path):
        _mk_kc(client, "KC-1")
        _mk_kc(client, "KC-2")
        _direct_insert_edge(tmp_path / "base.db", "KC-1", "KC-2")
        # Graph-backed stats still see the pre-edit wiring.
        assert client.get("/api/stats").json()["knowledge_map"]["edge_count"] == 0

        resp = client.post("/api/reload")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "reloaded"
        assert body["knowledge_nodes"] == 2
        assert body["knowledge_edges"] == 1

        assert client.get("/api/stats").json()["knowledge_map"]["edge_count"] == 1

    def test_reload_noop_when_graph_already_fresh(self, client):
        _mk_kc(client, "KC-1")
        body = client.post("/api/reload").json()
        assert body == {
            "status": "reloaded",
            "knowledge_nodes": 1,
            "knowledge_edges": 0,
            "math_nodes": 0,
            "math_edges": 0,
        }

    def test_reload_is_sandbox_scoped(self, client, tmp_path):
        _mk_kc(client, "KC-1")
        _mk_kc(client, "KC-2")
        sid = client.post("/api/sandboxes", json={"name": "exp"}).json()["id"]
        H = {"X-Sandbox-Id": sid}
        _direct_insert_edge(tmp_path / "sandboxes" / f"{sid}.db", "KC-1", "KC-2")

        body = client.post("/api/reload", headers=H).json()
        assert body["knowledge_edges"] == 1
        assert client.get("/api/stats", headers=H).json()["knowledge_map"]["edge_count"] == 1
        # The base map's graphs are untouched.
        assert client.get("/api/stats").json()["knowledge_map"]["edge_count"] == 0
