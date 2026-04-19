"""Topology diagnostics: extract structural issues from a frame's topology.

Translates the abstract topological signals (permanent H₁ bars, permanent H₀ bars,
antichain schemas, long-lived bars) into concrete actionable issues for human review.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass, field, asdict
from typing import Any

import gudhi
import networkx as nx

from .frame_engine import compute_all_atom_sets
from .topology import (
    FrameComplex,
    FiltrationResult,
    LearnerScenario,
    build_frame_complex,
    build_mastery_filtration,
    compute_persistence,
    load_prereq_graph,
)


# ── Issue data structures ──


@dataclass
class SuggestedAction:
    label: str
    action_type: str  # 'create_schema' | 'create_edge' | 'annotate' | 'dismiss' | 'edit_schema'
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class TopologyIssue:
    id: str
    issue_type: str  # 'permanent_h1' | 'permanent_h0' | 'antichain_schema' | 'long_h1'
    severity: str  # 'high' | 'medium' | 'low' | 'info'
    summary: str
    involved_kcs: list[str]
    involved_schemas: list[str]
    extra: dict[str, Any] = field(default_factory=dict)
    suggested_actions: list[SuggestedAction] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def _make_id(issue_type: str, *parts: Any) -> str:
    """Create a stable hash id for an issue."""
    raw = f"{issue_type}:" + ":".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


# ── Helpers ──


def _kc_to_schemas(frame_id: str, conn: sqlite3.Connection) -> dict[str, list[str]]:
    """Map each KC id to the list of (leaf) schemas containing it directly."""
    rows = conn.execute(
        """SELECT sk.kc_id, sk.schema_id FROM schema_kcs sk
           JOIN schemas s ON sk.schema_id = s.id
           WHERE s.frame_id = ?""",
        (frame_id,),
    ).fetchall()
    out: dict[str, list[str]] = {}
    for r in rows:
        out.setdefault(r["kc_id"], []).append(r["schema_id"])
    return out


def _schema_parents(frame_id: str, conn: sqlite3.Connection) -> dict[str, str | None]:
    rows = conn.execute(
        "SELECT id, parent_schema_id FROM schemas WHERE frame_id = ?",
        (frame_id,),
    ).fetchall()
    return {r["id"]: r["parent_schema_id"] for r in rows}


def _ancestor_schemas(schema_id: str, parents: dict[str, str | None]) -> set[str]:
    """All ancestors of `schema_id` in the schema-nesting tree (inclusive)."""
    out = {schema_id}
    cur = parents.get(schema_id)
    while cur:
        out.add(cur)
        cur = parents.get(cur)
    return out


def _shared_parent_schema(
    kcs: list[str],
    kc_schemas: dict[str, list[str]],
    parents: dict[str, str | None],
) -> str | None:
    """Find a schema that contains all of the given KCs (transitively, via nesting)."""
    if not kcs:
        return None
    # Compute, for each KC, all ancestor schemas containing it
    kc_anc: list[set[str]] = []
    for kc in kcs:
        leaf_schemas = kc_schemas.get(kc, [])
        anc: set[str] = set()
        for s in leaf_schemas:
            anc |= _ancestor_schemas(s, parents)
        kc_anc.append(anc)
    if not kc_anc:
        return None
    common = set.intersection(*kc_anc) if kc_anc else set()
    if not common:
        return None
    # Pick the smallest (most specific) common ancestor
    return min(common, key=lambda s: len(_ancestor_schemas(s, parents)))


# ── Permanent H₁ extraction ──


def _cycle_representative(
    birth_edge: tuple[str, str], graph: nx.Graph,
) -> list[str]:
    """Find a cycle in `graph` going through `birth_edge`.

    Removes the edge, finds a shortest path between its endpoints in the
    remainder, and returns path + edge as the cycle vertex sequence.
    """
    u, v = birth_edge
    if not graph.has_edge(u, v):
        return [u, v]
    G2 = graph.copy()
    G2.remove_edge(u, v)
    try:
        path = nx.shortest_path(G2, u, v)
        return list(path)  # closed by going back through u,v
    except nx.NetworkXNoPath:
        return [u, v]


def find_permanent_h1_issues(
    complex: FrameComplex,
    prereq_graph: nx.Graph,
    kc_schemas: dict[str, list[str]],
    parents: dict[str, str | None],
) -> list[TopologyIssue]:
    """Extract issues for each permanent H₁ bar.

    A permanent H₁ bar is a cycle in the 1-skeleton not bounded by triangles
    in the clique complex. Pedagogically: 3+ KCs are pairwise prereq-connected
    but no schema declares them as an integrated unit (the filling triangle).
    """
    st = complex.simplex_tree
    st.compute_persistence()
    gens = st.flag_persistence_generators()
    # gens = (h0_regular, [higher_regular_per_dim], h0_essential_vertices, [higher_essential_per_dim])
    _, _, _, higher_essential = gens

    issues: list[TopologyIssue] = []

    # higher_essential[0] is for H₁ (essential = permanent)
    if len(higher_essential) >= 1:
        h1_essential = higher_essential[0]  # shape (k, 2): vertex indices
        for row in h1_essential:
            u_idx, v_idx = int(row[0]), int(row[1])
            u = complex.index_to_vertex[u_idx]
            v = complex.index_to_vertex[v_idx]
            cycle = _cycle_representative((u, v), prereq_graph)
            cycle_set = list(dict.fromkeys(cycle))  # dedup, preserve order
            cycle_edges = [
                (cycle[i], cycle[(i + 1) % len(cycle)])
                for i in range(len(cycle))
            ]

            # Determine severity and involved schemas
            shared = _shared_parent_schema(cycle_set, kc_schemas, parents)
            involved_schemas = sorted({
                s for kc in cycle_set for s in kc_schemas.get(kc, [])
            })

            if shared and len(cycle_set) <= 4:
                severity = "high"
            elif shared:
                severity = "medium"
            else:
                severity = "low"

            n = len(cycle_set)
            schema_label = f" within schema {shared}" if shared else ""
            summary = (
                f"{n}-cycle of pairwise-connected KCs{schema_label} "
                f"with no integrative schema."
            )

            actions = [
                SuggestedAction(
                    label="Create integrative schema",
                    action_type="create_schema",
                    payload={
                        "atom_kcs": cycle_set,
                        "parent_schema_id": shared,
                        "suggested_name": (
                            f"Integration of {', '.join(cycle_set[:3])}"
                            + ("..." if len(cycle_set) > 3 else "")
                        ),
                    },
                ),
                SuggestedAction(
                    label="Mark as intentional gap",
                    action_type="annotate",
                    payload={"reason": "intentional"},
                ),
            ]

            issue = TopologyIssue(
                id=_make_id("permanent_h1", *sorted(cycle_set)),
                issue_type="permanent_h1",
                severity=severity,
                summary=summary,
                involved_kcs=cycle_set,
                involved_schemas=involved_schemas,
                extra={
                    "cycle_edges": cycle_edges,
                    "birth_edge": [u, v],
                    "shared_parent_schema": shared,
                },
                suggested_actions=actions,
            )
            issues.append(issue)

    return issues


# ── Permanent H₀ extraction ──


def find_permanent_h0_issues(
    complex: FrameComplex,
    prereq_graph: nx.Graph,
    kc_schemas: dict[str, list[str]],
    parents: dict[str, str | None],
) -> list[TopologyIssue]:
    """Each connected component beyond the first contributes a permanent H₀ bar.

    Pedagogically: a cluster of KCs that is never reached from the main body
    by any prereq edge or shared schema. This is structural fragmentation.
    """
    # Compute connected components of the 1-skeleton (which equals connected
    # components of the prereq graph, since vertices in the complex match)
    components = list(nx.connected_components(prereq_graph))
    # Sort by size (largest first); each non-largest is an issue
    components.sort(key=lambda c: -len(c))

    issues: list[TopologyIssue] = []
    if len(components) <= 1:
        return issues

    # Singletons are common (parallel-modality KCs not connected) — group them
    largest = components[0]
    minor = components[1:]

    for i, comp in enumerate(minor):
        comp_kcs = sorted(comp)
        involved_schemas = sorted({
            s for kc in comp_kcs for s in kc_schemas.get(kc, [])
        })
        shared = _shared_parent_schema(comp_kcs, kc_schemas, parents)

        if shared:
            severity = "high"
            summary = (
                f"{len(comp_kcs)} KCs in schema {shared} are disconnected "
                f"from the rest of the frame."
            )
        elif len(comp_kcs) == 1:
            severity = "low"
            summary = (
                f"KC {comp_kcs[0]} has no prereq edges; "
                f"isolated from the rest of the frame."
            )
        else:
            severity = "medium"
            summary = (
                f"{len(comp_kcs)} KCs form an isolated cluster "
                f"with no edges to the rest of the frame."
            )

        actions = [
            SuggestedAction(
                label="Add prereq edge to main component",
                action_type="create_edge",
                payload={"source_candidates": comp_kcs[:5]},
            ),
            SuggestedAction(
                label="Create bridging schema",
                action_type="create_schema",
                payload={"atom_kcs": comp_kcs[:3]},
            ),
            SuggestedAction(
                label="Mark as intentional",
                action_type="annotate",
                payload={"reason": "intentional"},
            ),
        ]

        issues.append(TopologyIssue(
            id=_make_id("permanent_h0", *comp_kcs),
            issue_type="permanent_h0",
            severity=severity,
            summary=summary,
            involved_kcs=comp_kcs,
            involved_schemas=involved_schemas,
            extra={
                "component_size": len(comp_kcs),
                "shared_parent_schema": shared,
                "rank": i + 1,
            },
            suggested_actions=actions,
        ))

    return issues


# ── Antichain schemas ──


def find_antichain_schemas(
    frame_id: str, conn: sqlite3.Connection, prereq_graph: nx.Graph,
) -> list[TopologyIssue]:
    """Schemas whose atom set has no internal prereq edges.

    Often intentional (parallel modalities), but may indicate a missing
    integration structure.
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)
    schemas_meta = {
        r["id"]: dict(r) for r in conn.execute(
            "SELECT id, name, parent_schema_id FROM schemas WHERE frame_id = ?",
            (frame_id,),
        )
    }

    issues: list[TopologyIssue] = []
    for sid, atoms in atom_sets.items():
        if len(atoms) < 2:
            continue
        sub = prereq_graph.subgraph(atoms)
        if sub.number_of_edges() == 0:
            schema_info = schemas_meta.get(sid, {})
            sname = schema_info.get("name", sid)

            actions = [
                SuggestedAction(
                    label="Confirm parallel modalities",
                    action_type="annotate",
                    payload={"reason": "parallel_intentional"},
                ),
                SuggestedAction(
                    label="Add prereq edges within schema",
                    action_type="create_edge",
                    payload={"source_candidates": sorted(atoms)},
                ),
            ]

            issues.append(TopologyIssue(
                id=_make_id("antichain_schema", sid),
                issue_type="antichain_schema",
                severity="info",
                summary=(
                    f"Schema '{sname}' ({sid}) has {len(atoms)} KCs with "
                    f"no internal prereq edges — parallel modalities or "
                    f"missing integration?"
                ),
                involved_kcs=sorted(atoms),
                involved_schemas=[sid],
                extra={
                    "schema_name": sname,
                    "atom_count": len(atoms),
                },
                suggested_actions=actions,
            ))

    return issues


# ── Long-lived H₁ bars (requires a learner scenario) ──


def find_long_lived_h1(
    complex: FrameComplex,
    filtration_result: FiltrationResult,
    prereq_graph: nx.Graph,
    kc_schemas: dict[str, list[str]],
    parents: dict[str, str | None],
    threshold_ratio: float = 0.3,
) -> list[TopologyIssue]:
    """H₁ bars whose lifetime is large relative to the filtration time horizon.

    These are pedagogical bottlenecks: structural holes that persist for a
    significant fraction of the learning trajectory.
    """
    t_min, t_max = filtration_result.time_range
    span = t_max - t_min
    if span <= 0:
        return []
    threshold = threshold_ratio * span

    finite_h1 = filtration_result.finite_bars(1)

    issues: list[TopologyIssue] = []
    for birth, death in finite_h1:
        lifetime = death - birth
        if lifetime < threshold:
            continue

        # We don't have a per-bar cycle representative without recomputing,
        # so we report the bar's quantitative info; involved_kcs left empty
        # for now (could enrich by finding cycles born at `birth` time)
        summary = (
            f"H₁ structural hole persisting from t={birth:.2f} to t={death:.2f} "
            f"(lifetime {lifetime:.2f}, {100*lifetime/span:.0f}% of horizon)."
        )
        severity = "medium" if lifetime > 0.5 * span else "low"

        actions = [
            SuggestedAction(
                label="Inspect mastery curves around this window",
                action_type="annotate",
                payload={"birth": birth, "death": death},
            ),
        ]

        issues.append(TopologyIssue(
            id=_make_id("long_h1", round(birth, 3), round(death, 3)),
            issue_type="long_h1",
            severity=severity,
            summary=summary,
            involved_kcs=[],
            involved_schemas=[],
            extra={
                "birth": birth,
                "death": death,
                "lifetime": lifetime,
                "horizon": span,
            },
            suggested_actions=actions,
        ))

    return issues


# ── Top-level orchestrator ──


def diagnose_frame(
    frame_id: str,
    conn: sqlite3.Connection,
    scenario: LearnerScenario | None = None,
    long_h1_threshold_ratio: float = 0.3,
) -> dict[str, Any]:
    """Run all diagnostic extractors and return a single sorted result.

    If `scenario` is provided, also runs the mastery filtration and includes
    long-lived-H₁ issues; otherwise only structural diagnostics are computed.
    """
    complex = build_frame_complex(frame_id, conn)
    prereq_graph = load_prereq_graph(frame_id, conn)
    kc_schemas = _kc_to_schemas(frame_id, conn)
    parents = _schema_parents(frame_id, conn)

    issues: list[TopologyIssue] = []
    issues += find_permanent_h1_issues(complex, prereq_graph, kc_schemas, parents)
    issues += find_permanent_h0_issues(complex, prereq_graph, kc_schemas, parents)
    issues += find_antichain_schemas(frame_id, conn, prereq_graph)

    if scenario is not None:
        filtered = build_mastery_filtration(complex, scenario)
        result = compute_persistence(filtered, max_dimension=2)
        issues += find_long_lived_h1(
            complex, result, prereq_graph, kc_schemas, parents,
            threshold_ratio=long_h1_threshold_ratio,
        )

    # Sort: severity (high → info), then issue_type, then summary
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    issues.sort(key=lambda i: (severity_order.get(i.severity, 9), i.issue_type, i.summary))

    summary_counts: dict[str, int] = {}
    for i in issues:
        summary_counts[i.issue_type] = summary_counts.get(i.issue_type, 0) + 1
        summary_counts[f"severity:{i.severity}"] = summary_counts.get(f"severity:{i.severity}", 0) + 1
    summary_counts["total"] = len(issues)

    return {
        "frame_id": frame_id,
        "issues": [i.to_dict() for i in issues],
        "summary": summary_counts,
        "scenario_name": scenario.name if scenario else None,
    }
