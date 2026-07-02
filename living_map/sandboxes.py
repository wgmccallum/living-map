"""Per-sandbox SQLite databases for collaborator experimentation.

A *sandbox* is a full, independent copy of the base database. Collaborators reach
one via a capability URL (an unguessable id in the link) and can edit anything —
KCs, edges, schemas, staging — without affecting production or each other.

Storage: each sandbox is ``<SANDBOX_DIR>/<id>.db``. On Railway this directory must
live on a persistent volume (see CLAUDE.md); otherwise sandboxes are wiped on
redeploy. Locally it defaults to ``living-map/sandboxes/`` (gitignored).

The manager owns the lifecycle (create/list/delete) and an LRU cache of open
"bundles" (connection + DAL + GraphStore + StagingDAL), one per active sandbox.
"""

from __future__ import annotations

import os
import re
import secrets
import sqlite3
import threading
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .dal import DAL
from .database import DEFAULT_DB_PATH, init_db
from .graph_store import GraphStore
from .staging_dal import StagingDAL

# Sandbox ids are minted with secrets.token_urlsafe → [A-Za-z0-9_-]. We validate
# every id received from a request against this to prevent path traversal.
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_META_DDL = (
    "CREATE TABLE IF NOT EXISTS sandbox_meta "
    "(id TEXT, name TEXT, created_at TEXT, source TEXT)"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _default_sandbox_dir() -> Path:
    env = os.environ.get("SANDBOX_DIR")
    if env:
        return Path(env)
    return Path(__file__).parent.parent / "sandboxes"


@dataclass
class Bundle:
    """An open sandbox: its connection and the three data-access objects."""
    conn: sqlite3.Connection
    dal: DAL
    graphs: GraphStore
    staging_dal: StagingDAL


class SandboxManager:
    def __init__(
        self,
        base_db_path: Path = DEFAULT_DB_PATH,
        sandbox_dir: Path | None = None,
        cache_cap: int = 8,
    ):
        self.base_db_path = Path(base_db_path)
        self.dir = Path(sandbox_dir) if sandbox_dir else _default_sandbox_dir()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cache_cap = cache_cap
        self._cache: "OrderedDict[str, Bundle]" = OrderedDict()
        self._lock = threading.RLock()

    # ── paths / validation ──

    @staticmethod
    def _valid_id(sandbox_id: str) -> bool:
        return bool(sandbox_id) and bool(_ID_RE.match(sandbox_id))

    def _path(self, sandbox_id: str) -> Path:
        if not self._valid_id(sandbox_id):
            raise ValueError(f"invalid sandbox id: {sandbox_id!r}")
        return self.dir / f"{sandbox_id}.db"

    def exists(self, sandbox_id: str) -> bool:
        return self._valid_id(sandbox_id) and self._path(sandbox_id).exists()

    # ── lifecycle ──

    def create(self, name: str, source: str = "base") -> dict:
        """Create a sandbox as a consistent copy of the base DB (or another sandbox).

        Uses the SQLite online-backup API, which copies a consistent snapshot
        including any WAL-resident commits (unlike a plain file copy).
        """
        if source and source != "base":
            source_path = self._path(source)
            if not source_path.exists():
                raise ValueError(f"source sandbox {source} does not exist")
        else:
            source = "base"
            source_path = self.base_db_path

        sandbox_id = secrets.token_urlsafe(16)
        dest_path = self._path(sandbox_id)

        src = sqlite3.connect(str(source_path))
        try:
            dst = sqlite3.connect(str(dest_path))
            try:
                src.backup(dst)  # consistent, WAL-aware snapshot
                dst.execute(_META_DDL)
                dst.execute(
                    "INSERT INTO sandbox_meta (id, name, created_at, source) VALUES (?, ?, ?, ?)",
                    (sandbox_id, name, _now(), source),
                )
                dst.commit()
            finally:
                dst.close()
        finally:
            src.close()

        return self._read_meta(dest_path) or {
            "id": sandbox_id, "name": name, "created_at": _now(), "source": source,
        }

    def delete(self, sandbox_id: str) -> bool:
        if not self.exists(sandbox_id):
            return False
        with self._lock:
            bundle = self._cache.pop(sandbox_id, None)
            if bundle is not None:
                bundle.conn.close()
        path = self._path(sandbox_id)
        for p in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        return True

    def list(self) -> list[dict]:
        out = []
        for path in sorted(self.dir.glob("*.db")):
            meta = self._read_meta(path)
            if meta is None:
                continue
            st = path.stat()
            meta["size_bytes"] = st.st_size
            meta["last_active"] = datetime.fromtimestamp(
                st.st_mtime, timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            out.append(meta)
        return out

    def _read_meta(self, path: Path) -> dict | None:
        try:
            conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            try:
                row = conn.execute(
                    "SELECT id, name, created_at, source FROM sandbox_meta LIMIT 1"
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error:
            return None
        if not row:
            return None
        return {k: row[k] for k in ("id", "name", "created_at", "source")}

    # ── open bundles (LRU cache) ──

    def bundle(self, sandbox_id: str) -> Bundle:
        if not self.exists(sandbox_id):
            raise KeyError(sandbox_id)
        with self._lock:
            cached = self._cache.get(sandbox_id)
            if cached is not None:
                self._cache.move_to_end(sandbox_id)
                return cached
            # init_db is idempotent (CREATE TABLE IF NOT EXISTS); it also ensures
            # newer indexes exist on older copies.
            conn = init_db(self._path(sandbox_id))
            graphs = GraphStore(conn)
            bundle = Bundle(
                conn=conn,
                graphs=graphs,
                dal=DAL(conn, graphs),
                staging_dal=StagingDAL(conn),
            )
            self._cache[sandbox_id] = bundle
            self._evict_if_needed()
            return bundle

    def _evict_if_needed(self) -> None:
        while len(self._cache) > self.cache_cap:
            _, evicted = self._cache.popitem(last=False)
            try:
                evicted.conn.close()
            except sqlite3.Error:
                pass

    def close_all(self) -> None:
        with self._lock:
            for bundle in self._cache.values():
                try:
                    bundle.conn.close()
                except sqlite3.Error:
                    pass
            self._cache.clear()
