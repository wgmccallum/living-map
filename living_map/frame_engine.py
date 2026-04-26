"""Frame and Quotient Engine — constraint validation and quotient computation.

Implements the formal definitions from the Knowledge Frame Architecture paper:
  - Convexity check (Def 2.6)
  - Downward closure (Axiom F2)
  - Frame acyclicity (Axiom F3)
  - Laminarity (Def 2.12)
  - Quotient of a DAG by a convex set (Def 2.13)
  - Quotient of a frame by a schema (Def 2.19)
  - Iterated/partial quotient (Thm 2.25)
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from typing import Any

import networkx as nx

from .graph_store import GraphStore


# ── Atom Set Computation ──


def compute_atom_set(frame_id: str, schema_id: str, conn: sqlite3.Connection) -> set[str]:
    """Compute At(σ) — the full atom set of a schema, including all nested children.

    At(σ) = direct KCs of σ  ∪  At(child₁)  ∪  At(child₂)  ∪  ...

    Recursion stays within `frame_id` — child schemas in other frames are not
    followed (each frame is its own schema tree).
    """
    direct = {
        r["kc_id"]
        for r in conn.execute(
            "SELECT kc_id FROM schema_kcs WHERE frame_id = ? AND schema_id = ?",
            (frame_id, schema_id),
        )
    }
    children = [
        r["id"]
        for r in conn.execute(
            "SELECT id FROM schemas WHERE frame_id = ? AND parent_schema_id = ?",
            (frame_id, schema_id),
        )
    ]
    result = set(direct)
    for child_id in children:
        result |= compute_atom_set(frame_id, child_id, conn)
    return result


def compute_all_atom_sets(frame_id: str, conn: sqlite3.Connection) -> dict[str, set[str]]:
    """Compute atom sets for all schemas in a frame."""
    schemas = [
        r["id"]
        for r in conn.execute(
            "SELECT id FROM schemas WHERE frame_id = ?", (frame_id,)
        )
    ]
    return {sid: compute_atom_set(frame_id, sid, conn) for sid in schemas}


# ── Constraint Validators ──


def check_convexity(kc_set: set[str], dag: nx.DiGraph) -> dict[str, Any]:
    """Check if a set of KCs is convex in the DAG.

    A set C is convex if whenever x, y ∈ C and x ≺ z ≺ y, then z ∈ C.
    Returns {"status": "valid"} or {"status": "violation", "missing_nodes": [...]}.
    """
    if not kc_set:
        return {"status": "valid"}

    # Nodes in kc_set that are actually in the graph
    present = kc_set & set(dag.nodes)
    if not present:
        return {"status": "valid"}

    # Descendants of any set member
    desc: set[str] = set()
    for v in present:
        desc |= nx.descendants(dag, v)
    desc |= present

    # Ancestors of any set member
    anc: set[str] = set()
    for v in present:
        anc |= nx.ancestors(dag, v)
    anc |= present

    # Nodes on a path between two set members
    between = desc & anc
    missing = between - kc_set

    if not missing:
        return {"status": "valid"}
    return {"status": "violation", "missing_nodes": sorted(missing)}


def check_schema_convexity(
    frame_id: str, conn: sqlite3.Connection, dag: nx.DiGraph
) -> dict[str, Any]:
    """Check convexity of all schemas in a frame."""
    atom_sets = compute_all_atom_sets(frame_id, conn)
    violations = []
    for schema_id, atoms in atom_sets.items():
        result = check_convexity(atoms, dag)
        if result["status"] == "violation":
            violations.append({
                "schema_id": schema_id,
                "missing_nodes": result["missing_nodes"],
            })
    if not violations:
        return {"status": "valid"}
    return {"status": "violation", "violations": violations}


def check_downward_closure(frame_id: str, conn: sqlite3.Connection) -> dict[str, Any]:
    """Check downward closure (Axiom F2): all sub-schemas must be in the frame.

    Since nesting is explicit via parent_schema_id and singletons are implicit,
    this checks that every schema's parent chain stays within the frame.
    """
    schemas_in_frame = {
        r["id"]
        for r in conn.execute(
            "SELECT id FROM schemas WHERE frame_id = ?", (frame_id,)
        )
    }
    violations = []
    for sid in schemas_in_frame:
        children = conn.execute(
            "SELECT id FROM schemas WHERE frame_id = ? AND parent_schema_id = ?",
            (frame_id, sid),
        ).fetchall()
        for child in children:
            if child["id"] not in schemas_in_frame:
                violations.append({
                    "missing": child["id"],
                    "parent": sid,
                })
    if not violations:
        return {"status": "valid"}
    return {"status": "violation", "violations": violations}


def check_frame_acyclicity(
    frame_id: str, conn: sqlite3.Connection, dag: nx.DiGraph
) -> dict[str, Any]:
    """Check frame acyclicity (Axiom F3).

    Build the schema-level DAG where σ ≺ τ iff ∃ u ∈ At(σ), v ∈ (At(τ) \ At(σ))
    such that u ≺ v in G. Check that this DAG is acyclic.
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)
    schema_ids = list(atom_sets.keys())
    schema_dag = nx.DiGraph()
    schema_dag.add_nodes_from(schema_ids)

    for i, s1 in enumerate(schema_ids):
        at_s1 = atom_sets[s1]
        for s2 in schema_ids[i + 1:]:
            at_s2 = atom_sets[s2]
            # Check s1 ≺ s2: ∃ u ∈ At(s1), v ∈ (At(s2) \ At(s1)) with u ≺ v
            diff_s2_s1 = at_s2 - at_s1
            if diff_s2_s1 and _has_edge_between(at_s1, diff_s2_s1, dag):
                schema_dag.add_edge(s1, s2)
            # Check s2 ≺ s1
            diff_s1_s2 = at_s1 - at_s2
            if diff_s1_s2 and _has_edge_between(at_s2, diff_s1_s2, dag):
                schema_dag.add_edge(s2, s1)

    if nx.is_directed_acyclic_graph(schema_dag):
        return {"status": "valid", "schema_dag_edges": list(schema_dag.edges())}
    cycles = list(nx.simple_cycles(schema_dag))
    return {
        "status": "violation",
        "cycles": [list(c) for c in cycles[:10]],
    }


def _has_edge_between(source_set: set[str], target_set: set[str], dag: nx.DiGraph) -> bool:
    """Check if any node in source_set has a path to any node in target_set."""
    for u in source_set:
        if u not in dag:
            continue
        desc = nx.descendants(dag, u)
        if desc & target_set:
            return True
    return False


def check_laminarity(frame_id: str, conn: sqlite3.Connection) -> dict[str, Any]:
    """Check laminarity (Def 2.12): atom sets must be pairwise laminar.

    For all σ, τ: At(σ) ∩ At(τ) = ∅ or At(σ) ⊆ At(τ) or At(τ) ⊆ At(σ).
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)
    schema_ids = list(atom_sets.keys())
    violations = []

    for i, s1 in enumerate(schema_ids):
        a = atom_sets[s1]
        for s2 in schema_ids[i + 1:]:
            b = atom_sets[s2]
            intersection = a & b
            if intersection and intersection != a and intersection != b:
                violations.append({
                    "schema_a": s1,
                    "schema_b": s2,
                    "overlap": sorted(intersection),
                    "a_only": sorted(a - b),
                    "b_only": sorted(b - a),
                })

    if not violations:
        return {"status": "valid"}
    return {"status": "violation", "violations": violations}


def validate_frame(
    frame_id: str, conn: sqlite3.Connection, dag: nx.DiGraph
) -> dict[str, Any]:
    """Run all constraint checks and return a structured validation report."""
    return {
        "frame_id": frame_id,
        "checks": {
            "schema_convexity": check_schema_convexity(frame_id, conn, dag),
            "downward_closure": check_downward_closure(frame_id, conn),
            "frame_acyclicity": check_frame_acyclicity(frame_id, conn, dag),
            "laminarity": check_laminarity(frame_id, conn),
        },
        "valid": all(
            check["status"] == "valid"
            for check in [
                check_schema_convexity(frame_id, conn, dag),
                check_downward_closure(frame_id, conn),
                check_frame_acyclicity(frame_id, conn, dag),
                check_laminarity(frame_id, conn),
            ]
        ),
    }


# ── Quotient Engine ──


def quotient_dag(
    dag: nx.DiGraph, convex_set: set[str], collapsed_node_id: str
) -> nx.DiGraph:
    """Compute the quotient DAG G/S (Def 2.13).

    Collapse convex_set into collapsed_node_id. Redirect crossing edges,
    drop internal edges, remove self-loops and duplicates.
    """
    new_dag = nx.DiGraph()

    # Add nodes: everything outside S, plus the collapsed node
    for node in dag.nodes:
        if node not in convex_set:
            new_dag.add_node(node)
    new_dag.add_node(collapsed_node_id)

    # Add edges
    for u, v in dag.edges:
        u_in = u in convex_set
        v_in = v in convex_set
        if not u_in and not v_in:
            new_dag.add_edge(u, v)
        elif not u_in and v_in:
            if u != collapsed_node_id:  # no self-loops
                new_dag.add_edge(u, collapsed_node_id)
        elif u_in and not v_in:
            if collapsed_node_id != v:  # no self-loops
                new_dag.add_edge(collapsed_node_id, v)
        # else: both in S → drop (internal edge)

    return new_dag


def compute_quotient_metadata(
    convex_set: set[str], schema_name: str, conn: sqlite3.Connection
) -> dict[str, Any]:
    """Compute metadata for a collapsed node from its constituent KCs.

    Language demands: union of all constituent demands.
    Math context: union; most common primary becomes primary.
    """
    # Language demands — union
    demands = set()
    for kc_id in convex_set:
        for r in conn.execute(
            "SELECT ld.label FROM kc_language_demands kld "
            "JOIN language_demands ld ON ld.id = kld.language_demand_id "
            "WHERE kld.kc_id = ?",
            (kc_id,),
        ):
            demands.add(r["label"])

    # Math contexts — union with primary selection
    context_roles: dict[str, list[str]] = {}  # concept_id -> list of roles
    for kc_id in convex_set:
        for r in conn.execute(
            "SELECT math_concept_id, role FROM kc_math_contexts WHERE kc_id = ?",
            (kc_id,),
        ):
            context_roles.setdefault(r["math_concept_id"], []).append(r["role"])

    math_contexts = []
    if context_roles:
        # Count primary occurrences
        primary_counts = Counter()
        for cid, roles in context_roles.items():
            primary_counts[cid] = sum(1 for r in roles if r == "primary")
        most_common_primary = primary_counts.most_common(1)[0][0] if primary_counts else None

        for cid in context_roles:
            role = "primary" if cid == most_common_primary else "secondary"
            math_contexts.append({"math_concept_id": cid, "role": role})

    return {
        "short_description": schema_name,
        "long_description": f"[Quotient node] Collapsed from schema '{schema_name}'. Needs human-authored behavioral definition.",
        "language_demands": sorted(demands),
        "math_contexts": math_contexts,
        "is_computed": True,
    }


def quotient_frame_by_schema(
    frame_id: str,
    schema_id: str,
    conn: sqlite3.Connection,
    dag: nx.DiGraph,
) -> dict[str, Any]:
    """Compute quotient of a frame by one of its schemas (Def 2.19).

    Returns the quotient DAG and updated schema definitions as JSON.
    This is ephemeral — the result is not persisted unless explicitly saved.
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)
    if schema_id not in atom_sets:
        raise ValueError(f"Schema {schema_id} not found in frame {frame_id}")

    convex_set = atom_sets[schema_id]

    # Validate convexity first
    conv_check = check_convexity(convex_set, dag)
    if conv_check["status"] != "valid":
        raise ValueError(
            f"Schema {schema_id} is not convex. Missing nodes: {conv_check['missing_nodes']}"
        )

    # Get schema name for the collapsed node
    schema_row = conn.execute(
        "SELECT name FROM schemas WHERE frame_id = ? AND id = ?",
        (frame_id, schema_id),
    ).fetchone()
    schema_name = schema_row["name"] if schema_row else schema_id

    collapsed_id = f"[{schema_id}]"

    # Compute quotient DAG
    new_dag = quotient_dag(dag, convex_set, collapsed_id)

    # Compute metadata for collapsed node
    metadata = compute_quotient_metadata(convex_set, schema_name, conn)

    # Update other schemas' atom sets
    new_schemas = {}
    for sid, atoms in atom_sets.items():
        if sid == schema_id:
            new_schemas[sid] = [collapsed_id]
            continue
        new_atoms = atoms - convex_set
        if atoms & convex_set:
            new_atoms.add(collapsed_id)
        new_schemas[sid] = sorted(new_atoms)

    return {
        "quotient_dag": {
            "nodes": sorted(new_dag.nodes),
            "edges": sorted(new_dag.edges),
        },
        "collapsed_node": {
            "id": collapsed_id,
            "source_schema_id": schema_id,
            **metadata,
        },
        "updated_schemas": new_schemas,
        "original_node_count": dag.number_of_nodes(),
        "quotient_node_count": new_dag.number_of_nodes(),
        "original_edge_count": dag.number_of_edges(),
        "quotient_edge_count": new_dag.number_of_edges(),
    }


def partial_quotient(
    frame_id: str,
    schema_ids: list[str],
    conn: sqlite3.Connection,
    dag: nx.DiGraph,
) -> dict[str, Any]:
    """Compute iterated quotient F/Σ (Thm 2.25).

    For a laminar subfamily, the result is order-independent.
    We find At-maximal elements and apply quotients sequentially.
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)

    # Validate all requested schemas exist
    for sid in schema_ids:
        if sid not in atom_sets:
            raise ValueError(f"Schema {sid} not found in frame {frame_id}")

    # Check that the selected schemas form a laminar subfamily
    selected_atoms = {sid: atom_sets[sid] for sid in schema_ids}
    for i, s1 in enumerate(schema_ids):
        a = selected_atoms[s1]
        for s2 in schema_ids[i + 1:]:
            b = selected_atoms[s2]
            intersection = a & b
            if intersection and intersection != a and intersection != b:
                raise ValueError(
                    f"Schemas {s1} and {s2} are not laminar — they partially overlap. "
                    f"Overlap: {sorted(intersection)}"
                )

    # Find At-maximal elements
    maximal = []
    for sid in schema_ids:
        is_maximal = True
        for other_sid in schema_ids:
            if sid != other_sid and selected_atoms[sid] < selected_atoms[other_sid]:
                is_maximal = False
                break
        if is_maximal:
            maximal.append(sid)

    # Restrict DAG to only the KCs in this frame
    frame_kc_ids: set[str] = set()
    for atoms in atom_sets.values():
        frame_kc_ids |= atoms
    current_dag = dag.subgraph(frame_kc_ids).copy()

    # Apply quotients sequentially
    all_collapsed = []
    all_removed: set[str] = set()

    for sid in maximal:
        convex_set = atom_sets[sid]
        # Adjust for previously collapsed nodes
        adjusted_set = convex_set - all_removed

        conv_check = check_convexity(adjusted_set, current_dag)
        if conv_check["status"] != "valid":
            raise ValueError(f"Schema {sid} lost convexity during iterated quotient")

        schema_row = conn.execute(
            "SELECT name FROM schemas WHERE frame_id = ? AND id = ?",
            (frame_id, sid),
        ).fetchone()
        schema_name = schema_row["name"] if schema_row else sid
        collapsed_id = f"[{sid}]"

        metadata = compute_quotient_metadata(convex_set, schema_name, conn)
        current_dag = quotient_dag(current_dag, adjusted_set, collapsed_id)

        all_collapsed.append({
            "id": collapsed_id,
            "source_schema_id": sid,
            **metadata,
        })
        all_removed |= convex_set

    # Compute updated atom sets for remaining schemas
    remaining_atom_sets = {}
    for sid, atoms in atom_sets.items():
        new_atoms = atoms - all_removed
        for collapsed in all_collapsed:
            source_atoms = atom_sets.get(collapsed["source_schema_id"], set())
            if atoms & source_atoms:
                new_atoms.add(collapsed["id"])
        remaining_atom_sets[sid] = sorted(new_atoms)

    return {
        "quotient_dag": {
            "nodes": sorted(current_dag.nodes),
            "edges": sorted(current_dag.edges),
        },
        "collapsed_nodes": all_collapsed,
        "updated_schemas": remaining_atom_sets,
        "schemas_collapsed": maximal,
        "original_node_count": dag.number_of_nodes(),
        "quotient_node_count": current_dag.number_of_nodes(),
        "original_edge_count": dag.number_of_edges(),
        "quotient_edge_count": current_dag.number_of_edges(),
    }


def save_quotient(
    frame_id: str,
    schema_ids: list[str],
    new_frame_name: str,
    conn: sqlite3.Connection,
    dag: nx.DiGraph,
    graphs: GraphStore,
) -> dict[str, Any]:
    """Compute a quotient and persist the result as a new frame.

    Creates new KCs for collapsed nodes (is_quotient_node=TRUE).
    """
    from .dal import DAL, _now
    from .models import KCCreate, MathContextLink

    result = partial_quotient(frame_id, schema_ids, conn, dag)
    dal = DAL(conn, graphs)

    now = _now()
    new_frame_id = new_frame_name.lower().replace(" ", "-")

    # Create new frame
    conn.execute(
        "INSERT INTO frames (id, name, description, frame_type, is_reference, created_at, updated_at) "
        "VALUES (?, ?, ?, 'internal', 0, ?, ?)",
        (new_frame_id, new_frame_name,
         f"Quotient of {frame_id} by schemas {schema_ids}", now, now),
    )

    # Create KCs for each collapsed node
    for collapsed in result["collapsed_nodes"]:
        kc_id = collapsed["id"]
        kc = KCCreate(
            id=kc_id,
            short_description=collapsed["short_description"],
            long_description=collapsed["long_description"],
            language_demands=collapsed["language_demands"],
            math_contexts=[
                MathContextLink(**ctx) for ctx in collapsed["math_contexts"]
            ],
        )
        dal.create_kc(kc)
        # Mark as quotient node
        conn.execute(
            "UPDATE knowledge_components SET is_quotient_node = 1, "
            "source_schema_id = ?, metadata_status = 'computed' WHERE id = ?",
            (collapsed["source_schema_id"], kc_id),
        )

    conn.commit()

    return {
        "new_frame_id": new_frame_id,
        **result,
    }
