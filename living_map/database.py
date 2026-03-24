"""SQLite database schema and connection management."""

import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent / "living_map.db"

SCHEMA_SQL = """
-- Knowledge Components
CREATE TABLE IF NOT EXISTS knowledge_components (
    id                TEXT PRIMARY KEY,
    short_description TEXT NOT NULL,
    long_description  TEXT,
    is_quotient_node  INTEGER DEFAULT 0,
    source_schema_id  TEXT,
    metadata_status   TEXT DEFAULT 'authored'
        CHECK (metadata_status IN ('authored', 'computed', 'confirmed')),
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Language Demands (reference table)
CREATE TABLE IF NOT EXISTS language_demands (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT NOT NULL UNIQUE,
    description TEXT
);

-- KC <-> Language Demand (many-to-many)
CREATE TABLE IF NOT EXISTS kc_language_demands (
    kc_id             TEXT    NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
    language_demand_id INTEGER NOT NULL REFERENCES language_demands(id) ON DELETE CASCADE,
    is_computed        INTEGER DEFAULT 0,
    PRIMARY KEY (kc_id, language_demand_id)
);

-- Mathematical Structure Map: concepts
CREATE TABLE IF NOT EXISTS math_concepts (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Mathematical Structure Map: edges
CREATE TABLE IF NOT EXISTS math_concept_edges (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id  TEXT NOT NULL REFERENCES math_concepts(id) ON DELETE CASCADE,
    target_id  TEXT NOT NULL REFERENCES math_concepts(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (source_id, target_id)
);

-- KC <-> Math Concept bridge
CREATE TABLE IF NOT EXISTS kc_math_contexts (
    kc_id          TEXT NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
    math_concept_id TEXT NOT NULL REFERENCES math_concepts(id) ON DELETE CASCADE,
    role           TEXT DEFAULT 'primary'
        CHECK (role IN ('primary', 'secondary')),
    PRIMARY KEY (kc_id, math_concept_id)
);

-- Prerequisite Edges (Knowledge Map)
CREATE TABLE IF NOT EXISTS prerequisite_edges (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    source_kc_id TEXT NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
    target_kc_id TEXT NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (source_kc_id, target_kc_id)
);

-- Annotations (polymorphic)
CREATE TABLE IF NOT EXISTS annotations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL
        CHECK (entity_type IN ('kc', 'edge', 'schema', 'frame', 'math_concept')),
    entity_id       TEXT NOT NULL,
    annotation_type TEXT NOT NULL
        CHECK (annotation_type IN (
            'editorial_note', 'open_question', 'provenance',
            'proposed_revision', 'rationale', 'kc_type'
        )),
    content         TEXT NOT NULL,
    author          TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    resolved_at     TEXT
);

-- Frames
CREATE TABLE IF NOT EXISTS frames (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    description  TEXT,
    frame_type   TEXT NOT NULL
        CHECK (frame_type IN ('internal', 'alignment')),
    is_reference INTEGER DEFAULT 0,
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Schemas
CREATE TABLE IF NOT EXISTS schemas (
    id               TEXT PRIMARY KEY,
    frame_id         TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    name             TEXT NOT NULL,
    description      TEXT,
    parent_schema_id TEXT REFERENCES schemas(id) ON DELETE SET NULL,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Schema <-> KC membership
CREATE TABLE IF NOT EXISTS schema_kcs (
    schema_id TEXT NOT NULL REFERENCES schemas(id) ON DELETE CASCADE,
    kc_id     TEXT NOT NULL REFERENCES knowledge_components(id) ON DELETE CASCADE,
    PRIMARY KEY (schema_id, kc_id)
);

-- Framework alignment items
CREATE TABLE IF NOT EXISTS framework_items (
    id              TEXT PRIMARY KEY,
    frame_id        TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    item_text       TEXT NOT NULL,
    hierarchy_path  TEXT NOT NULL,
    parent_item_id  TEXT REFERENCES framework_items(id) ON DELETE SET NULL,
    metadata        TEXT,  -- JSON
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Alignment mappings
CREATE TABLE IF NOT EXISTS alignment_mappings (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_item_id TEXT NOT NULL REFERENCES framework_items(id) ON DELETE CASCADE,
    target_type       TEXT NOT NULL CHECK (target_type IN ('kc', 'schema')),
    target_id         TEXT NOT NULL,
    mapping_type      TEXT CHECK (mapping_type IN ('exact', 'partial', 'broader', 'narrower')),
    confidence        TEXT CHECK (confidence IN ('confirmed', 'tentative', 'disputed')),
    notes             TEXT,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Alignment tensions
CREATE TABLE IF NOT EXISTS alignment_tensions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_item_id TEXT NOT NULL REFERENCES framework_items(id) ON DELETE CASCADE,
    tension_type      TEXT NOT NULL
        CHECK (tension_type IN (
            'convexity_violation', 'laminarity_violation',
            'grain_size_mismatch', 'missing_prerequisite',
            'framework_incoherence'
        )),
    description       TEXT NOT NULL,
    resolution_status TEXT DEFAULT 'open'
        CHECK (resolution_status IN (
            'open', 'resolved_dag_update', 'resolved_framework_issue',
            'resolved_grain_size', 'deferred'
        )),
    resolution_notes  TEXT,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_prereq_source ON prerequisite_edges(source_kc_id);
CREATE INDEX IF NOT EXISTS idx_prereq_target ON prerequisite_edges(target_kc_id);
CREATE INDEX IF NOT EXISTS idx_annotations_entity ON annotations(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_schema_kcs_kc ON schema_kcs(kc_id);
CREATE INDEX IF NOT EXISTS idx_schema_frame ON schemas(frame_id);
CREATE INDEX IF NOT EXISTS idx_kc_math_ctx ON kc_math_contexts(math_concept_id);
CREATE INDEX IF NOT EXISTS idx_kc_lang ON kc_language_demands(language_demand_id);

-- ═══════════════════════════════════════════════════════
-- Staging Area (Moderated Bulk Add)
-- ═══════════════════════════════════════════════════════

-- Staging Sessions: a topic DAG in progress
CREATE TABLE IF NOT EXISTS staging_sessions (
    id                TEXT PRIMARY KEY,
    topic_name        TEXT NOT NULL,
    description       TEXT,
    source_documents  TEXT,  -- JSON array of source file references
    status            TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'tier2_review', 'committed', 'abandoned')),
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Staged KCs: draft KCs within a staging session
CREATE TABLE IF NOT EXISTS staged_kcs (
    id                  TEXT PRIMARY KEY,
    session_id          TEXT NOT NULL REFERENCES staging_sessions(id) ON DELETE CASCADE,
    short_description   TEXT,
    long_description    TEXT,
    source_text         TEXT,
    source_reference    TEXT,
    stage_status        TEXT NOT NULL DEFAULT 'proposed'
        CHECK (stage_status IN (
            'proposed', 'grain_approved', 'formulated',
            'edges_confirmed', 'schema_assigned', 'stale', 'flagged'
        )),
    language_demands    TEXT,  -- JSON array of demand labels
    kc_type             TEXT,  -- annotation: Fact, Skill, Definition, etc.
    math_contexts       TEXT,  -- JSON array of {math_concept_id, role}
    reviewer_comments   TEXT,  -- JSON array of {author, timestamp, text}
    ai_correctness_note TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Staged Edges: draft prerequisite edges within a staging session
CREATE TABLE IF NOT EXISTS staged_edges (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id        TEXT NOT NULL REFERENCES staging_sessions(id) ON DELETE CASCADE,
    source_kc_id      TEXT NOT NULL,
    target_kc_id      TEXT NOT NULL,
    ai_reasoning      TEXT,
    status            TEXT NOT NULL DEFAULT 'proposed'
        CHECK (status IN ('proposed', 'confirmed', 'rejected', 'stale')),
    reviewer_comments TEXT,  -- JSON array of {author, timestamp, text}
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Staged Schemas: draft schema groupings within a staging session
CREATE TABLE IF NOT EXISTS staged_schemas (
    id                TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL REFERENCES staging_sessions(id) ON DELETE CASCADE,
    name              TEXT NOT NULL,
    description       TEXT,
    parent_schema_id  TEXT REFERENCES staged_schemas(id) ON DELETE SET NULL,
    status            TEXT NOT NULL DEFAULT 'proposed'
        CHECK (status IN ('proposed', 'confirmed', 'stale')),
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Staged Schema <-> KC membership
CREATE TABLE IF NOT EXISTS staged_schema_kcs (
    schema_id TEXT NOT NULL REFERENCES staged_schemas(id) ON DELETE CASCADE,
    kc_id     TEXT NOT NULL REFERENCES staged_kcs(id) ON DELETE CASCADE,
    PRIMARY KEY (schema_id, kc_id)
);

-- KC Conversations (grain review chat)
CREATE TABLE IF NOT EXISTS staged_kc_conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES staging_sessions(id) ON DELETE CASCADE,
    kc_id       TEXT NOT NULL REFERENCES staged_kcs(id) ON DELETE CASCADE,
    messages    TEXT NOT NULL DEFAULT '[]',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (session_id, kc_id)
);

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_staged_kcs_session ON staged_kcs(session_id);
CREATE INDEX IF NOT EXISTS idx_staged_kcs_status ON staged_kcs(stage_status);
CREATE INDEX IF NOT EXISTS idx_staged_edges_session ON staged_edges(session_id);
CREATE INDEX IF NOT EXISTS idx_staged_edges_status ON staged_edges(status);
CREATE INDEX IF NOT EXISTS idx_staged_schemas_session ON staged_schemas(session_id);
CREATE INDEX IF NOT EXISTS idx_staged_schema_kcs_kc ON staged_schema_kcs(kc_id);
CREATE INDEX IF NOT EXISTS idx_staged_kc_conv_session ON staged_kc_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_staged_kc_conv_kc ON staged_kc_conversations(kc_id);
"""

SEED_LANGUAGE_DEMANDS = [
    ("Speaking", "Productive oral language"),
    ("Listening", "Receptive oral language"),
    ("Reading", "Receptive written language"),
    ("Writing", "Productive written language"),
    ("Interpreting a mathematical representation", "Receptive — interpreting representations"),
    ("Producing a mathematical representation", "Productive — producing representations"),
]


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = get_connection(db_path)
    conn.executescript(SCHEMA_SQL)
    # Seed language demands
    for label, desc in SEED_LANGUAGE_DEMANDS:
        conn.execute(
            "INSERT OR IGNORE INTO language_demands (label, description) VALUES (?, ?)",
            (label, desc),
        )
    conn.commit()
    return conn
