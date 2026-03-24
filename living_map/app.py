"""FastAPI application — Living Map API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from .dal import DAL
from .database import DEFAULT_DB_PATH, init_db
from .graph_store import CycleError, GraphStore
from .frame_engine import (
    check_convexity,
    compute_atom_set,
    partial_quotient,
    quotient_frame_by_schema,
    save_quotient,
    validate_frame,
)
from .models import (
    AnnotationCreate,
    AnnotationUpdate,
    BulkImportData,
    EdgeCreate,
    ErrorResponse,
    FrameCreate,
    FrameUpdate,
    KCCreate,
    KCUpdate,
    MathConceptCreate,
    MathConceptEdgeCreate,
    MathConceptUpdate,
    QuotientRequest,
    QuotientSaveRequest,
    SchemaCreate,
    SchemaKCsAdd,
    SchemaUpdate,
    StagingSessionCreate,
    StagingSessionUpdate,
    StagedKCCreate,
    StagedKCUpdate,
    StagedKCBatchUpdate,
    StagedKCComment,
    StagedEdgeCreate,
    StagedEdgeUpdate,
    StagedSchemaCreate,
    StagedSchemaUpdate,
    StagedSchemaKCsAdd,
    AIBatchRequest,
    ConversationMessage,
    ConversationResponse,
    ConversationReply,
    ConversationSendRequest,
)
from .staging_dal import StagingDAL

# Module-level singletons set during lifespan
_dal: DAL | None = None
_graphs: GraphStore | None = None
_staging_dal: StagingDAL | None = None


def get_dal() -> DAL:
    assert _dal is not None
    return _dal


def get_graphs() -> GraphStore:
    assert _graphs is not None
    return _graphs


def get_staging_dal() -> StagingDAL:
    assert _staging_dal is not None
    return _staging_dal


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _dal, _graphs, _staging_dal
    db_path = Path(app.state.db_path) if hasattr(app.state, "db_path") else DEFAULT_DB_PATH
    conn = init_db(db_path)
    _graphs = GraphStore(conn)
    _dal = DAL(conn, _graphs)
    _staging_dal = StagingDAL(conn)
    yield
    conn.close()


app = FastAPI(title="Living Map API", version="0.1.0", lifespan=lifespan)


# ── Knowledge Components ──


@app.get("/api/kcs")
def list_kcs(
    offset: int = 0,
    limit: int = Query(default=100, le=1000),
    language_demand: str | None = None,
    math_context: str | None = None,
    search: str | None = None,
    is_quotient_node: bool | None = None,
):
    return get_dal().list_kcs(
        offset=offset, limit=limit,
        language_demand=language_demand, math_context=math_context,
        search=search, is_quotient_node=is_quotient_node,
    )


@app.get("/api/kcs/{kc_id}")
def get_kc(kc_id: str):
    kc = get_dal().get_kc(kc_id)
    if not kc:
        raise HTTPException(404, f"KC {kc_id} not found")
    return kc


@app.post("/api/kcs", status_code=201)
def create_kc(kc: KCCreate):
    try:
        return get_dal().create_kc(kc)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/kcs/{kc_id}")
def update_kc(kc_id: str, update: KCUpdate):
    result = get_dal().update_kc(kc_id, update)
    if not result:
        raise HTTPException(404, f"KC {kc_id} not found")
    return result


@app.patch("/api/kcs/{kc_id}/language-demands")
def update_kc_language_demands(kc_id: str, body: dict):
    demands = body.get("language_demands", [])
    result = get_dal().update_kc_language_demands(kc_id, demands)
    if not result:
        raise HTTPException(404, f"KC {kc_id} not found")
    return result


@app.delete("/api/kcs/{kc_id}", status_code=204)
def delete_kc(kc_id: str):
    if not get_dal().delete_kc(kc_id):
        raise HTTPException(
            409, f"Cannot delete KC {kc_id}: it has prerequisite edges referencing it"
        )


@app.get("/api/kcs/{kc_id}/ancestors")
def kc_ancestors(kc_id: str):
    graphs = get_graphs()
    if kc_id not in graphs.knowledge_graph:
        raise HTTPException(404, f"KC {kc_id} not found")
    return sorted(graphs.ancestors(kc_id))


@app.get("/api/kcs/{kc_id}/descendants")
def kc_descendants(kc_id: str):
    graphs = get_graphs()
    if kc_id not in graphs.knowledge_graph:
        raise HTTPException(404, f"KC {kc_id} not found")
    return sorted(graphs.descendants(kc_id))


@app.get("/api/kcs/{kc_id}/neighborhood")
def kc_neighborhood(kc_id: str, depth: int = Query(default=2, ge=1, le=10)):
    graphs = get_graphs()
    if kc_id not in graphs.knowledge_graph:
        raise HTTPException(404, f"KC {kc_id} not found")
    return sorted(graphs.neighborhood(kc_id, depth))


@app.get("/api/kcs/{kc_id}/edges")
def kc_edges(kc_id: str):
    return get_dal().kc_edges(kc_id)


@app.get("/api/kcs/{kc_id}/math-contexts")
def kc_math_contexts(kc_id: str):
    kc = get_dal().get_kc(kc_id)
    if not kc:
        raise HTTPException(404, f"KC {kc_id} not found")
    return kc.math_contexts


@app.post("/api/kcs/{kc_id}/math-contexts")
def add_kc_math_context(kc_id: str, body: dict):
    dal = get_dal()
    math_concept_id = body.get("math_concept_id")
    role = body.get("role", "primary")
    if not math_concept_id:
        raise HTTPException(400, "math_concept_id is required")
    try:
        result = dal.add_math_context(kc_id, math_concept_id, role)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not result:
        raise HTTPException(404, f"KC {kc_id} not found")
    return result


@app.delete("/api/kcs/{kc_id}/math-contexts/{math_concept_id}")
def remove_kc_math_context(kc_id: str, math_concept_id: str):
    dal = get_dal()
    result = dal.remove_math_context(kc_id, math_concept_id)
    if not result:
        raise HTTPException(404, f"KC {kc_id} not found")
    return result


# ── Prerequisite Edges ──


@app.get("/api/edges")
def list_edges(
    offset: int = 0,
    limit: int = Query(default=100, le=1000),
    source_kc_id: str | None = None,
    target_kc_id: str | None = None,
):
    return get_dal().list_edges(offset=offset, limit=limit,
                                source_kc_id=source_kc_id, target_kc_id=target_kc_id)


@app.post("/api/edges", status_code=201)
def create_edge(edge: EdgeCreate):
    try:
        return get_dal().create_edge(edge)
    except CycleError as e:
        raise HTTPException(409, str(e))
    except Exception as e:
        raise HTTPException(400, str(e))


@app.delete("/api/edges/{edge_id}", status_code=204)
def delete_edge(edge_id: int):
    if not get_dal().delete_edge(edge_id):
        raise HTTPException(404, f"Edge {edge_id} not found")


@app.get("/api/edges/path")
def edge_path(from_kc: str = Query(alias="from"), to_kc: str = Query(alias="to")):
    return get_graphs().all_paths(from_kc, to_kc)


# ── Math Concepts ──


@app.get("/api/math-concepts")
def list_math_concepts(offset: int = 0, limit: int = Query(default=100, le=1000)):
    return get_dal().list_math_concepts(offset=offset, limit=limit)


@app.get("/api/math-concepts/{concept_id}")
def get_math_concept(concept_id: str):
    mc = get_dal().get_math_concept(concept_id)
    if not mc:
        raise HTTPException(404, f"Math concept {concept_id} not found")
    return mc


@app.post("/api/math-concepts", status_code=201)
def create_math_concept(mc: MathConceptCreate):
    try:
        return get_dal().create_math_concept(mc)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/math-concepts/{concept_id}")
def update_math_concept(concept_id: str, update: MathConceptUpdate):
    result = get_dal().update_math_concept(concept_id, update)
    if not result:
        raise HTTPException(404, f"Math concept {concept_id} not found")
    return result


@app.delete("/api/math-concepts/{concept_id}", status_code=204)
def delete_math_concept(concept_id: str):
    if not get_dal().delete_math_concept(concept_id):
        raise HTTPException(
            409, f"Cannot delete {concept_id}: KCs reference it"
        )


@app.get("/api/math-concepts/{concept_id}/ancestors")
def math_concept_ancestors(concept_id: str):
    graphs = get_graphs()
    if concept_id not in graphs.math_graph:
        raise HTTPException(404, f"Math concept {concept_id} not found")
    return sorted(graphs.math_ancestors(concept_id))


@app.get("/api/math-concepts/{concept_id}/descendants")
def math_concept_descendants(concept_id: str):
    graphs = get_graphs()
    if concept_id not in graphs.math_graph:
        raise HTTPException(404, f"Math concept {concept_id} not found")
    return sorted(graphs.math_descendants(concept_id))


@app.get("/api/math-concepts/{concept_id}/kcs")
def math_concept_kcs(concept_id: str):
    mc = get_dal().get_math_concept(concept_id)
    if not mc:
        raise HTTPException(404, f"Math concept {concept_id} not found")
    return get_dal().math_concept_kcs(concept_id)


@app.get("/api/math-concept-edges")
def list_math_concept_edges():
    dal = get_dal()
    rows = dal.conn.execute(
        "SELECT id, source_id, target_id, created_at FROM math_concept_edges ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]


@app.post("/api/math-concept-edges", status_code=201)
def create_math_concept_edge(edge: MathConceptEdgeCreate):
    try:
        return get_dal().create_math_concept_edge(edge)
    except CycleError as e:
        raise HTTPException(409, str(e))
    except Exception as e:
        raise HTTPException(400, str(e))


@app.delete("/api/math-concept-edges/{edge_id}", status_code=204)
def delete_math_concept_edge(edge_id: int):
    if not get_dal().delete_math_concept_edge(edge_id):
        raise HTTPException(404, f"Math concept edge {edge_id} not found")


# ── Annotations ──


@app.get("/api/annotations")
def list_annotations(entity_type: str | None = None, entity_id: str | None = None):
    return get_dal().list_annotations(entity_type=entity_type, entity_id=entity_id)


@app.post("/api/annotations", status_code=201)
def create_annotation(ann: AnnotationCreate):
    return get_dal().create_annotation(ann)


@app.patch("/api/annotations/{ann_id}")
def update_annotation(ann_id: int, update: AnnotationUpdate):
    result = get_dal().update_annotation(ann_id, content=update.content, resolved_at=update.resolved_at)
    if not result:
        raise HTTPException(404, f"Annotation {ann_id} not found")
    return result


@app.delete("/api/annotations/{ann_id}", status_code=204)
def delete_annotation(ann_id: int):
    if not get_dal().delete_annotation(ann_id):
        raise HTTPException(404, f"Annotation {ann_id} not found")


@app.get("/api/kc-types")
def list_kc_types():
    """Return distinct KC type values used in annotations."""
    dal = get_dal()
    rows = dal.conn.execute(
        "SELECT DISTINCT content FROM annotations WHERE annotation_type = 'kc_type' ORDER BY content"
    ).fetchall()
    return [r[0] for r in rows]


@app.get("/api/schemas/{schema_id}/next-kc-id")
def next_kc_id(schema_id: str):
    """Generate the next KC ID for a given schema based on existing conventions."""
    dal = get_dal()
    # Get existing KCs in this schema
    rows = dal.conn.execute(
        "SELECT kc_id FROM schema_kcs WHERE schema_id = ?", (schema_id,)
    ).fetchall()
    existing_ids = [r[0] for r in rows]

    # Determine the prefix from the schema ID (e.g., "COP" from "COP-1500")
    prefix = schema_id.split("-")[0]

    if any("*KC." in kid for kid in existing_ids):
        # COP-style: {prefix}-{schema}*KC.{number}
        # Find the max KC number across ALL KCs with this prefix
        all_kcs = dal.conn.execute(
            "SELECT id FROM knowledge_components WHERE id LIKE ?", (f"{prefix}-%*KC.%",)
        ).fetchall()
        max_num = 0
        for r in all_kcs:
            try:
                num = int(r[0].split("*KC.")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
        next_num = max_num + 1
        return {"next_id": f"{schema_id}*KC.{next_num}"}
    else:
        # CNM-style: {prefix}-{number}
        # Find the max number across all KCs with this prefix
        all_kcs = dal.conn.execute(
            "SELECT id FROM knowledge_components WHERE id LIKE ?", (f"{prefix}-%",)
        ).fetchall()
        max_num = 0
        for r in all_kcs:
            try:
                num = int(r[0].split("-")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
        next_num = max_num + 1
        return {"next_id": f"{prefix}-{next_num}"}


# ── KC Schemas ──


@app.get("/api/kcs/{kc_id}/schemas")
def kc_schemas(kc_id: str):
    kc = get_dal().get_kc(kc_id)
    if not kc:
        raise HTTPException(404, f"KC {kc_id} not found")
    return get_dal().kc_schemas(kc_id)


# ── Frames ──


@app.get("/api/frames")
def list_frames():
    return get_dal().list_frames()


@app.get("/api/frames/{frame_id}")
def get_frame(frame_id: str):
    frame = get_dal().get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    return frame


@app.post("/api/frames", status_code=201)
def create_frame(frame: FrameCreate):
    try:
        return get_dal().create_frame(frame)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/frames/{frame_id}")
def update_frame(frame_id: str, update: FrameUpdate):
    result = get_dal().update_frame(frame_id, update)
    if not result:
        raise HTTPException(404, f"Frame {frame_id} not found")
    return result


@app.delete("/api/frames/{frame_id}", status_code=204)
def delete_frame(frame_id: str):
    if not get_dal().delete_frame(frame_id):
        raise HTTPException(404, f"Frame {frame_id} not found")


# ── Schemas ──


@app.get("/api/frames/{frame_id}/schemas")
def list_schemas(frame_id: str):
    return get_dal().list_schemas(frame_id)


@app.post("/api/frames/{frame_id}/schemas", status_code=201)
def create_schema(frame_id: str, schema: SchemaCreate):
    frame = get_dal().get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    try:
        return get_dal().create_schema(frame_id, schema)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/schemas/{schema_id}")
def update_schema(schema_id: str, update: SchemaUpdate):
    result = get_dal().update_schema(schema_id, update)
    if not result:
        raise HTTPException(404, f"Schema {schema_id} not found")
    return result


@app.delete("/api/schemas/{schema_id}", status_code=204)
def delete_schema(schema_id: str):
    if not get_dal().delete_schema(schema_id):
        raise HTTPException(404, f"Schema {schema_id} not found")


@app.post("/api/schemas/{schema_id}/kcs")
def add_kcs_to_schema(schema_id: str, body: SchemaKCsAdd):
    result = get_dal().add_kcs_to_schema(schema_id, body.kc_ids)
    if not result:
        raise HTTPException(404, f"Schema {schema_id} not found")
    return result


@app.delete("/api/schemas/{schema_id}/kcs/{kc_id}", status_code=204)
def remove_kc_from_schema(schema_id: str, kc_id: str):
    if not get_dal().remove_kc_from_schema(schema_id, kc_id):
        raise HTTPException(404, "Schema or KC membership not found")


@app.get("/api/schemas/{schema_id}/atoms")
def schema_atoms(schema_id: str):
    dal = get_dal()
    schema = dal.get_schema(schema_id)
    if not schema:
        raise HTTPException(404, f"Schema {schema_id} not found")
    atoms = compute_atom_set(schema_id, dal.conn)
    return sorted(atoms)


@app.get("/api/schemas/{schema_id}/check-convexity")
def schema_check_convexity(schema_id: str):
    dal = get_dal()
    schema = dal.get_schema(schema_id)
    if not schema:
        raise HTTPException(404, f"Schema {schema_id} not found")
    atoms = compute_atom_set(schema_id, dal.conn)
    return check_convexity(atoms, get_graphs().knowledge_graph)


# ── Frame Validation ──


@app.post("/api/frames/{frame_id}/validate")
def validate_frame_endpoint(frame_id: str):
    dal = get_dal()
    frame = dal.get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    return validate_frame(frame_id, dal.conn, get_graphs().knowledge_graph)


# ── Quotient ──


@app.post("/api/frames/{frame_id}/quotient")
def compute_quotient(frame_id: str, body: QuotientRequest):
    dal = get_dal()
    frame = dal.get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    try:
        return partial_quotient(
            frame_id, body.schema_ids, dal.conn, get_graphs().knowledge_graph
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/frames/{frame_id}/quotient/save")
def save_quotient_endpoint(frame_id: str, body: QuotientSaveRequest):
    dal = get_dal()
    frame = dal.get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    try:
        return save_quotient(
            frame_id, body.schema_ids, body.new_frame_name,
            dal.conn, get_graphs().knowledge_graph, get_graphs(),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/frames/{frame_id}/schema-dag")
def frame_schema_dag(frame_id: str):
    dal = get_dal()
    frame = dal.get_frame(frame_id)
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")
    from .frame_engine import check_frame_acyclicity
    result = check_frame_acyclicity(frame_id, dal.conn, get_graphs().knowledge_graph)
    return {
        "status": result["status"],
        "edges": result.get("schema_dag_edges", []),
        "cycles": result.get("cycles", []),
    }


# ── Bulk Operations ──


@app.post("/api/bulk/import")
def bulk_import(data: BulkImportData):
    try:
        return get_dal().bulk_import(data)
    except CycleError as e:
        raise HTTPException(409, str(e))
    except Exception as e:
        raise HTTPException(400, str(e))


@app.get("/api/bulk/export")
def bulk_export():
    return get_dal().export_all()


@app.get("/api/stats")
def stats():
    return get_graphs().stats()


# ── Staging Sessions (Moderated Bulk Add) ──


@app.get("/api/staging")
def list_staging_sessions():
    return get_staging_dal().list_sessions()


@app.post("/api/staging", status_code=201)
def create_staging_session(session: StagingSessionCreate):
    try:
        return get_staging_dal().create_session(session)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.get("/api/staging/{session_id}")
def get_staging_session(session_id: str):
    session = get_staging_dal().get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")
    return session


@app.patch("/api/staging/{session_id}")
def update_staging_session(session_id: str, update: StagingSessionUpdate):
    result = get_staging_dal().update_session(session_id, update)
    if not result:
        raise HTTPException(404, f"Staging session {session_id} not found")
    return result


@app.delete("/api/staging/{session_id}", status_code=204)
def delete_staging_session(session_id: str, force: bool = False):
    try:
        if not get_staging_dal().delete_session(session_id, force=force):
            raise HTTPException(404, f"Staging session {session_id} not found")
    except ValueError as e:
        raise HTTPException(409, str(e))


# ── Staged KCs ──


@app.get("/api/staging/{session_id}/kcs")
def list_staged_kcs(session_id: str, stage_status: str | None = None):
    return get_staging_dal().list_staged_kcs(session_id, stage_status=stage_status)


@app.post("/api/staging/{session_id}/kcs", status_code=201)
def create_staged_kcs(session_id: str, body: StagedKCCreate | list[StagedKCCreate]):
    sdal = get_staging_dal()
    # Verify session exists
    if not sdal.get_session(session_id):
        raise HTTPException(404, f"Staging session {session_id} not found")
    try:
        if isinstance(body, list):
            return sdal.create_staged_kcs_batch(session_id, body)
        return sdal.create_staged_kc(session_id, body)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.get("/api/staging/{session_id}/kcs/{kc_id}")
def get_staged_kc(session_id: str, kc_id: str):
    kc = get_staging_dal().get_staged_kc(session_id, kc_id)
    if not kc:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")
    return kc


@app.patch("/api/staging/{session_id}/kcs/{kc_id}")
def update_staged_kc(session_id: str, kc_id: str, update: StagedKCUpdate):
    result = get_staging_dal().update_staged_kc(session_id, kc_id, update)
    if not result:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")
    return result


@app.delete("/api/staging/{session_id}/kcs/{kc_id}", status_code=204)
def delete_staged_kc(session_id: str, kc_id: str):
    if not get_staging_dal().delete_staged_kc(session_id, kc_id):
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")


@app.post("/api/staging/{session_id}/kcs/{kc_id}/comment", status_code=201)
def add_staged_kc_comment(session_id: str, kc_id: str, body: StagedKCComment):
    result = get_staging_dal().add_kc_comment(session_id, kc_id, body.author, body.text)
    if not result:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")
    return result


@app.post("/api/staging/{session_id}/kcs/{kc_id}/flag")
def flag_staged_kc(session_id: str, kc_id: str):
    result = get_staging_dal().flag_kc(session_id, kc_id)
    if not result:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")
    return result


@app.post("/api/staging/{session_id}/kcs/batch-update")
def batch_update_staged_kcs(session_id: str, body: StagedKCBatchUpdate):
    return get_staging_dal().batch_update_staged_kcs(session_id, body.kc_ids, body.updates)


@app.post("/api/staging/{session_id}/kcs/{kc_id}/split")
def split_staged_kc(session_id: str, kc_id: str, body: dict):
    """Split a staged KC into multiple child KCs.

    Expects body: { "children": ["description 1", "description 2", ...] }
    The original KC is marked 'stale' and new child KCs are created as 'proposed'.
    """
    sdal = get_staging_dal()
    parent = sdal.get_staged_kc(session_id, kc_id)
    if not parent:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")

    children_desc = body.get("children", [])
    if len(children_desc) < 2:
        raise HTTPException(400, "Split requires at least 2 child descriptions")

    # Generate child IDs by appending letters to parent ID
    created = []
    for i, desc in enumerate(children_desc):
        suffix = chr(ord('a') + i)  # a, b, c, ...
        child_id = f"{kc_id}-{suffix}"
        child = StagedKCCreate(
            id=child_id,
            source_text=desc,
            source_reference=f"Split from {kc_id}: {parent.source_reference or ''}".strip(),
            stage_status="grain_approved",
        )
        created.append(sdal.create_staged_kc(session_id, child))

    # Mark parent as stale
    sdal.update_staged_kc(session_id, kc_id, StagedKCUpdate(stage_status="stale"))
    # Add a comment explaining the split
    sdal.add_kc_comment(
        session_id, kc_id, "system",
        f"Split into {len(created)} child KCs: {', '.join(c.id for c in created)}"
    )

    return {
        "parent_id": kc_id,
        "parent_status": "stale",
        "children": [c.model_dump() for c in created],
    }


@app.post("/api/staging/{session_id}/merge")
def merge_staged_kcs(session_id: str, body: dict):
    """Merge two or more staged KCs into one.

    Expects body:
      mode: "keep" or "create"
      survivor_id: (mode=keep) ID of the KC to keep
      source_ids: list of all KC IDs involved in the merge (including survivor for mode=keep)
      description: (mode=create, optional) description for the newly created KC
    """
    sdal = get_staging_dal()
    mode = body.get("mode")
    source_ids = body.get("source_ids", [])

    if len(source_ids) < 2:
        raise HTTPException(400, "Merge requires at least 2 KC IDs")

    # Validate all source KCs exist
    sources = []
    for sid in source_ids:
        kc = sdal.get_staged_kc(session_id, sid)
        if not kc:
            raise HTTPException(404, f"Staged KC {sid} not found in session {session_id}")
        sources.append(kc)

    if mode == "keep":
        survivor_id = body.get("survivor_id")
        if not survivor_id or survivor_id not in source_ids:
            raise HTTPException(400, "survivor_id must be one of the source_ids")

        # Mark non-survivors as stale
        retired = []
        for sid in source_ids:
            if sid != survivor_id:
                sdal.update_staged_kc(session_id, sid, StagedKCUpdate(stage_status="stale"))
                sdal.add_kc_comment(session_id, sid, "system",
                                    f"Merged into {survivor_id}")
                retired.append(sid)

        sdal.add_kc_comment(session_id, survivor_id, "system",
                            f"Absorbed merged KCs: {', '.join(retired)}")

        return {
            "mode": "keep",
            "survivor_id": survivor_id,
            "retired_ids": retired,
        }

    elif mode == "create":
        # Generate a new merged KC ID from the first source
        base_id = source_ids[0]
        merged_id = f"{base_id}-merged"
        # Combine source texts
        combined_source = "\n---\n".join(
            f"[{s.id}] {s.source_text or s.short_description or ''}"
            for s in sources
        )
        desc = body.get("description", combined_source)
        combined_refs = "; ".join(
            s.source_reference for s in sources if s.source_reference
        )

        merged = sdal.create_staged_kc(session_id, StagedKCCreate(
            id=merged_id,
            source_text=desc,
            source_reference=f"Merged from {', '.join(source_ids)}. {combined_refs}".strip(),
            stage_status="proposed",
        ))

        # Mark all sources as stale
        for sid in source_ids:
            sdal.update_staged_kc(session_id, sid, StagedKCUpdate(stage_status="stale"))
            sdal.add_kc_comment(session_id, sid, "system",
                                f"Merged into new KC {merged_id}")

        return {
            "mode": "create",
            "merged_kc": merged.model_dump(),
            "retired_ids": source_ids,
        }

    else:
        raise HTTPException(400, "mode must be 'keep' or 'create'")


# ── Staged Edges ──


@app.get("/api/staging/{session_id}/edges")
def list_staged_edges(
    session_id: str,
    status: str | None = None,
    source_kc_id: str | None = None,
    target_kc_id: str | None = None,
):
    return get_staging_dal().list_staged_edges(
        session_id, status=status,
        source_kc_id=source_kc_id, target_kc_id=target_kc_id,
    )


@app.post("/api/staging/{session_id}/edges", status_code=201)
def create_staged_edges(session_id: str, body: StagedEdgeCreate | list[StagedEdgeCreate]):
    sdal = get_staging_dal()
    if not sdal.get_session(session_id):
        raise HTTPException(404, f"Staging session {session_id} not found")
    try:
        if isinstance(body, list):
            return sdal.create_staged_edges_batch(session_id, body)
        return sdal.create_staged_edge(session_id, body)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/staging/{session_id}/edges/{edge_id}")
def update_staged_edge(session_id: str, edge_id: int, update: StagedEdgeUpdate):
    try:
        result = get_staging_dal().update_staged_edge(
            session_id, edge_id,
            status=update.status, ai_reasoning=update.ai_reasoning,
        )
    except ValueError as e:
        raise HTTPException(409, str(e))
    if not result:
        raise HTTPException(404, f"Staged edge {edge_id} not found in session {session_id}")
    return result


@app.delete("/api/staging/{session_id}/edges/{edge_id}", status_code=204)
def delete_staged_edge(session_id: str, edge_id: int):
    if not get_staging_dal().delete_staged_edge(session_id, edge_id):
        raise HTTPException(404, f"Staged edge {edge_id} not found in session {session_id}")


@app.post("/api/staging/{session_id}/edges/validate")
def validate_staged_edges(session_id: str):
    return get_staging_dal().validate_staged_edges(session_id)


# ── Staged Schemas ──


@app.get("/api/staging/{session_id}/schemas")
def list_staged_schemas(session_id: str, status: str | None = None):
    return get_staging_dal().list_staged_schemas(session_id, status=status)


@app.post("/api/staging/{session_id}/schemas", status_code=201)
def create_staged_schema(session_id: str, schema: StagedSchemaCreate):
    sdal = get_staging_dal()
    if not sdal.get_session(session_id):
        raise HTTPException(404, f"Staging session {session_id} not found")
    try:
        return sdal.create_staged_schema(session_id, schema)
    except Exception as e:
        raise HTTPException(409, str(e))


@app.patch("/api/staging/{session_id}/schemas/{schema_id}")
def update_staged_schema(session_id: str, schema_id: str, update: StagedSchemaUpdate):
    result = get_staging_dal().update_staged_schema(
        session_id, schema_id,
        name=update.name, description=update.description,
        parent_schema_id=update.parent_schema_id, status=update.status,
    )
    if not result:
        raise HTTPException(404, f"Staged schema {schema_id} not found in session {session_id}")
    return result


@app.delete("/api/staging/{session_id}/schemas/{schema_id}", status_code=204)
def delete_staged_schema(session_id: str, schema_id: str):
    if not get_staging_dal().delete_staged_schema(session_id, schema_id):
        raise HTTPException(404, f"Staged schema {schema_id} not found in session {session_id}")


@app.post("/api/staging/{session_id}/schemas/{schema_id}/kcs", status_code=201)
def add_kcs_to_staged_schema(session_id: str, schema_id: str, body: StagedSchemaKCsAdd):
    result = get_staging_dal().add_kcs_to_staged_schema(session_id, schema_id, body.kc_ids)
    if not result:
        raise HTTPException(404, f"Staged schema {schema_id} not found in session {session_id}")
    return result


@app.delete("/api/staging/{session_id}/schemas/{schema_id}/kcs/{kc_id}", status_code=204)
def remove_kc_from_staged_schema(session_id: str, schema_id: str, kc_id: str):
    if not get_staging_dal().remove_kc_from_staged_schema(session_id, schema_id, kc_id):
        raise HTTPException(404, "Staged schema or KC membership not found")


@app.post("/api/staging/{session_id}/schemas/validate")
def validate_staged_schemas(session_id: str):
    return get_staging_dal().validate_staged_schemas(session_id)


# ── Document Ingest ──


@app.post("/api/staging/{session_id}/ingest")
async def ingest_document(session_id: str, file: UploadFile = File(...)):
    """Ingest a source document into a staging session.

    Parses the document, extracts content chunks, and creates staged KCs
    with status 'proposed'. Returns a draft manifest for review.
    """
    from .document_parser import parse_document

    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    # Read file content
    content = await file.read()
    filename = file.filename or "uploaded_file"
    file_path = Path(filename)

    # Parse document
    try:
        chunks = parse_document(file_path, content=content)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(422, f"Failed to parse document: {e}")

    if not chunks:
        raise HTTPException(422, "No content could be extracted from the document")

    # Generate staged KC IDs based on session ID
    # Convention: STAGE-{PREFIX}-{NNN} where PREFIX is derived from session ID
    prefix = session_id.split("-")[0].upper()[:4] if "-" in session_id else session_id.upper()[:4]

    # Find the highest existing staged KC number for this session
    existing_kcs = sdal.list_staged_kcs(session_id)
    existing_nums = []
    for kc in existing_kcs:
        parts = kc.id.rsplit("-", 1)
        if len(parts) == 2:
            try:
                existing_nums.append(int(parts[1]))
            except ValueError:
                pass
    next_num = max(existing_nums, default=0) + 1

    # Create staged KCs from content chunks
    created_kcs = []
    manifest_items = []
    for i, chunk in enumerate(chunks):
        kc_id = f"STAGE-{prefix}-{next_num + i:03d}"
        kc = StagedKCCreate(
            id=kc_id,
            source_text=chunk.original_text,
            source_reference=chunk.source_reference,
            stage_status="proposed",
        )
        created = sdal.create_staged_kc(session_id, kc)
        created_kcs.append(created)
        manifest_items.append({
            "staged_kc_id": kc_id,
            "source_reference": chunk.source_reference,
            "original_text": chunk.original_text,
            "metadata": chunk.metadata,
        })

    # Update session source_documents
    docs = session.source_documents or []
    if filename not in docs:
        docs.append(filename)
        sdal.update_session(session_id, StagingSessionUpdate(source_documents=docs))

    return {
        "session_id": session_id,
        "filename": filename,
        "format": file_path.suffix.lower(),
        "chunks_extracted": len(chunks),
        "staged_kcs_created": len(created_kcs),
        "manifest": manifest_items,
    }


# ── AI Proposal Endpoints ──


@app.get("/api/ai/status")
def ai_status():
    from .ai_service import is_available
    available, message = is_available()
    return {"available": available, "message": message}


@app.post("/api/staging/{session_id}/ai/grain-review")
def ai_grain_review(session_id: str, body: AIBatchRequest):
    from .ai_service import grain_review
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    # Load the requested staged KCs
    staged_kcs = []
    for kc_id in body.kc_ids:
        kc = sdal.get_staged_kc(session_id, kc_id)
        if kc:
            staged_kcs.append(kc.model_dump())
    if not staged_kcs:
        raise HTTPException(400, "No valid KC IDs provided")

    # Load existing KCs for calibration
    dal = get_dal()
    existing = [kc.model_dump() for kc in dal.list_kcs(limit=20)]

    try:
        result = grain_review(staged_kcs, existing_kcs=existing)
        return {"session_id": session_id, "reviews": result}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI grain review failed: {e}")


@app.post("/api/staging/{session_id}/ai/formulate")
def ai_formulate(session_id: str, body: AIBatchRequest):
    from .ai_service import formulate_kcs
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    staged_kcs = []
    for kc_id in body.kc_ids:
        kc = sdal.get_staged_kc(session_id, kc_id)
        if kc:
            staged_kcs.append(kc.model_dump())
    if not staged_kcs:
        raise HTTPException(400, "No valid KC IDs provided")

    dal = get_dal()
    existing = [kc.model_dump() for kc in dal.list_kcs(limit=20)]

    try:
        result = formulate_kcs(staged_kcs, existing_kcs=existing)

        # Auto-apply formulations to staged KCs
        for formulation in result:
            kc_id = formulation.get("kc_id")
            if not kc_id:
                continue
            update = StagedKCUpdate(
                short_description=formulation.get("short_description"),
                long_description=formulation.get("long_description"),
                kc_type=formulation.get("kc_type"),
                ai_correctness_note=formulation.get("correctness_note"),
            )
            if formulation.get("language_demands"):
                update.language_demands = formulation["language_demands"]
            sdal.update_staged_kc(session_id, kc_id, update)

        return {"session_id": session_id, "formulations": result}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI formulation failed: {e}")


@app.post("/api/staging/{session_id}/ai/prerequisites")
def ai_prerequisites(session_id: str, body: AIBatchRequest):
    from .ai_service import propose_prerequisites
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    staged_kcs = []
    for kc_id in body.kc_ids:
        kc = sdal.get_staged_kc(session_id, kc_id)
        if kc:
            staged_kcs.append(kc.model_dump())
    if not staged_kcs:
        raise HTTPException(400, "No valid KC IDs provided")

    # Load existing confirmed edges
    existing_edges = [
        e.model_dump() for e in
        sdal.list_staged_edges(session_id, status="confirmed")
    ]

    try:
        result = propose_prerequisites(staged_kcs, existing_edges=existing_edges)

        # Auto-create proposed edges from the result
        edges_created = []
        proposed_edges = result.get("edges", result) if isinstance(result, dict) else result
        if isinstance(proposed_edges, list):
            for edge in proposed_edges:
                source = edge.get("source_kc_id")
                target = edge.get("target_kc_id")
                reasoning = edge.get("reasoning", "")
                if source and target:
                    try:
                        created = sdal.create_staged_edge(
                            session_id,
                            StagedEdgeCreate(
                                source_kc_id=source,
                                target_kc_id=target,
                                ai_reasoning=reasoning,
                            ),
                        )
                        edges_created.append(created.model_dump())
                    except Exception:
                        pass  # Skip duplicate or invalid edges

        return {
            "session_id": session_id,
            "proposals": result,
            "edges_created": len(edges_created),
        }
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI prerequisite proposal failed: {e}")


@app.post("/api/staging/{session_id}/ai/schemas")
def ai_schemas(session_id: str, body: AIBatchRequest):
    from .ai_service import propose_schemas
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    staged_kcs = []
    for kc_id in body.kc_ids:
        kc = sdal.get_staged_kc(session_id, kc_id)
        if kc:
            staged_kcs.append(kc.model_dump())
    if not staged_kcs:
        raise HTTPException(400, "No valid KC IDs provided")

    confirmed_edges = [
        e.model_dump() for e in
        sdal.list_staged_edges(session_id, status="confirmed")
    ]

    try:
        result = propose_schemas(staged_kcs, confirmed_edges)
        return {"session_id": session_id, "schema_proposals": result}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI schema proposal failed: {e}")


@app.post("/api/staging/{session_id}/ai/correctness-check")
def ai_correctness_check(session_id: str, body: AIBatchRequest):
    from .ai_service import correctness_check
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")

    staged_kcs = []
    for kc_id in body.kc_ids:
        kc = sdal.get_staged_kc(session_id, kc_id)
        if kc:
            staged_kcs.append(kc.model_dump())
    if not staged_kcs:
        raise HTTPException(400, "No valid KC IDs provided")

    try:
        result = correctness_check(staged_kcs)

        # Auto-apply correctness notes
        for check in result:
            kc_id = check.get("kc_id")
            if kc_id and check.get("issues"):
                note = "; ".join(check["issues"])
                sdal.update_staged_kc(
                    session_id, kc_id,
                    StagedKCUpdate(ai_correctness_note=note),
                )

        return {"session_id": session_id, "checks": result}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI correctness check failed: {e}")


# ── KC Conversations (Grain Review Chat) ──


@app.get("/api/staging/{session_id}/kcs/{kc_id}/conversation")
def get_kc_conversation(session_id: str, kc_id: str):
    sdal = get_staging_dal()
    kc = sdal.get_staged_kc(session_id, kc_id)
    if not kc:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")
    messages = sdal.get_conversation(session_id, kc_id)
    return ConversationResponse(
        kc_id=kc_id,
        session_id=session_id,
        messages=[ConversationMessage(**m) for m in messages] if messages else [],
    )


@app.post("/api/staging/{session_id}/kcs/{kc_id}/conversation")
def send_kc_conversation_message(session_id: str, kc_id: str, body: ConversationSendRequest):
    from .ai_service import grain_review_chat

    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")
    kc = sdal.get_staged_kc(session_id, kc_id)
    if not kc:
        raise HTTPException(404, f"Staged KC {kc_id} not found in session {session_id}")

    from datetime import datetime, timezone

    def _now_str():
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Load existing conversation or start fresh
    messages = sdal.get_conversation(session_id, kc_id) or []

    # Append user message
    user_msg = {"role": "user", "content": body.message, "timestamp": _now_str()}
    messages.append(user_msg)

    # Gather context
    all_kcs = [k.model_dump() for k in sdal.list_staged_kcs(session_id)]
    dal = get_dal()
    existing = [k.model_dump() for k in dal.list_kcs(limit=20)]

    try:
        ai_response_text, action = grain_review_chat(
            kc=kc.model_dump(),
            all_session_kcs=all_kcs,
            conversation_history=messages,
            existing_kcs=existing,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"AI conversation failed: {e}")

    ai_msg = {"role": "assistant", "content": ai_response_text, "timestamp": _now_str()}
    messages.append(ai_msg)

    sdal.save_conversation(session_id, kc_id, messages)

    return {
        "role": "assistant",
        "content": ai_response_text,
        "timestamp": ai_msg["timestamp"],
        "action": action,
        "full_history": [{"role": m["role"], "content": m["content"], "timestamp": m["timestamp"]} for m in messages],
    }


@app.get("/api/staging/{session_id}/conversations")
def list_session_conversations(session_id: str):
    sdal = get_staging_dal()
    session = sdal.get_session(session_id)
    if not session:
        raise HTTPException(404, f"Staging session {session_id} not found")
    kc_ids = sdal.list_conversations(session_id)
    return {"session_id": session_id, "kc_ids_with_conversations": kc_ids}


# ── Staging Dashboard ──

_dashboard_path = Path(__file__).parent / "staging_dashboard.html"


@app.get("/staging")
def staging_dashboard():
    content = _dashboard_path.read_text()
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# ── Static file serving (production) ──

_static_dir = Path(__file__).parent / "static"

if _static_dir.exists():
    # Serve the SPA index.html for any non-API route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept the staging dashboard route
        if full_path == "staging":
            return staging_dashboard()
        # Try to serve the file directly (JS, CSS, assets)
        file_path = _static_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Otherwise serve index.html (SPA client-side routing)
        return FileResponse(_static_dir / "index.html")
