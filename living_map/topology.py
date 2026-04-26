"""Simplicial complex, mastery filtration, and persistent homology for knowledge frames.

Implements the constructions from Sections 4–5 of the Knowledge Frame Architecture paper:
  - Frame complex KF (Definition 4.1)
  - Mastery function and cascading weights (Definitions 4.4–4.5)
  - Mastery filtration (Definition 4.6)
  - Persistent homology via GUDHI
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

import gudhi
import networkx as nx

from .frame_engine import compute_all_atom_sets, compute_atom_set


# ── Prerequisite graph (clique complex foundation) ──


def load_prereq_graph(frame_id: str, conn: sqlite3.Connection) -> nx.Graph:
    """Load the undirected prerequisite graph restricted to KCs in the frame.

    The clique complex construction only allows simplices on cliques of this graph,
    so two KCs in the same schema must have a direct prereq edge (in either direction)
    to form an edge in the complex.
    """
    frame_kcs = {
        r["id"] for r in conn.execute(
            """SELECT DISTINCT kc.id FROM knowledge_components kc
               JOIN schema_kcs sk ON kc.id = sk.kc_id
               WHERE sk.frame_id = ?""",
            (frame_id,),
        )
    }
    G = nx.Graph()
    G.add_nodes_from(frame_kcs)
    for r in conn.execute("SELECT source_kc_id, target_kc_id FROM prerequisite_edges"):
        if r["source_kc_id"] in frame_kcs and r["target_kc_id"] in frame_kcs:
            G.add_edge(r["source_kc_id"], r["target_kc_id"])
    return G


def maximal_cliques_in_atoms(
    atoms: set[str] | frozenset[str], prereq_graph: nx.Graph,
) -> list[frozenset[str]]:
    """Find all maximal cliques of prereq_graph restricted to `atoms`.

    Each maximal clique becomes a maximal simplex in the schema's contribution
    to the frame complex.  Isolated vertices in `atoms` count as 0-cliques.
    """
    sub = prereq_graph.subgraph(atoms)
    cliques = [frozenset(c) for c in nx.find_cliques(sub)]
    # find_cliques returns at least the singleton for each isolated vertex
    seen_atoms: set[str] = set()
    for c in cliques:
        seen_atoms |= c
    for v in atoms:
        if v not in seen_atoms:
            cliques.append(frozenset({v}))
    return cliques


# ── Data Structures ──


@dataclass
class MasteryBreakpoint:
    """A (time, value) pair defining one knot of a piecewise-linear mastery curve."""
    time: float
    value: float  # in [0, 1]


@dataclass
class MasteryFunction:
    """Per-vertex mastery curve, piecewise-linear between breakpoints.

    Breakpoints must be sorted by time.  The first breakpoint is typically (0, 0)
    per axiom (M1), but this is not enforced to allow modeling partial prior knowledge.
    """
    vertex_id: str
    breakpoints: list[MasteryBreakpoint] = field(default_factory=list)

    def evaluate(self, t: float) -> float:
        """Linearly interpolate mastery at time t."""
        if not self.breakpoints:
            return 0.0
        # Before first breakpoint
        if t <= self.breakpoints[0].time:
            return self.breakpoints[0].value
        # After last breakpoint
        if t >= self.breakpoints[-1].time:
            return self.breakpoints[-1].value
        # Find bracketing interval
        for i in range(len(self.breakpoints) - 1):
            bp0 = self.breakpoints[i]
            bp1 = self.breakpoints[i + 1]
            if bp0.time <= t <= bp1.time:
                if bp1.time == bp0.time:
                    return bp1.value
                frac = (t - bp0.time) / (bp1.time - bp0.time)
                return bp0.value + frac * (bp1.value - bp0.value)
        return self.breakpoints[-1].value


@dataclass
class LearnerScenario:
    """A complete specification of a learner's trajectory through a frame."""
    name: str
    mastery_functions: dict[str, MasteryFunction] = field(default_factory=dict)
    theta: float = 0.7  # mastery threshold


@dataclass
class FrameComplex:
    """The simplicial complex KF built from a frame's schemas (Definition 4.1).

    Vertices = KC ids.  A subset S is a simplex iff S ⊆ At(σ) for some schema σ.
    Internally stored as a GUDHI SimplexTree with integer-indexed vertices.
    """
    vertices: list[str]
    maximal_simplices: list[frozenset[str]]  # atom sets that are inclusion-maximal
    vertex_to_index: dict[str, int]
    index_to_vertex: dict[int, str]
    _simplex_tree: gudhi.SimplexTree = field(default_factory=gudhi.SimplexTree, repr=False)

    @property
    def simplex_tree(self) -> gudhi.SimplexTree:
        return self._simplex_tree

    def num_simplices(self) -> int:
        return self._simplex_tree.num_simplices()

    def num_vertices(self) -> int:
        return self._simplex_tree.num_vertices()

    def dimension(self) -> int:
        return self._simplex_tree.dimension()

    def simplex_counts_by_dimension(self) -> dict[int, int]:
        """Count simplices in each dimension."""
        counts: dict[int, int] = {}
        for simplex, _ in self._simplex_tree.get_simplices():
            dim = len(simplex) - 1
            counts[dim] = counts.get(dim, 0) + 1
        return counts

    def index_simplex(self, kc_ids: frozenset[str]) -> list[int]:
        """Convert a set of KC string ids to sorted integer indices."""
        return sorted(self.vertex_to_index[v] for v in kc_ids)


@dataclass
class FiltrationResult:
    """Persistence diagrams and Betti curves from the mastery filtration."""
    persistence_pairs: list[tuple[int, tuple[float, float]]]
    betti_curves: dict[int, list[tuple[float, int]]]
    time_range: tuple[float, float]

    def permanent_bars(self, dimension: int = 0) -> list[float]:
        """Return birth times of bars that persist to infinity."""
        return [
            birth for dim, (birth, death) in self.persistence_pairs
            if dim == dimension and death == float("inf")
        ]

    def finite_bars(self, dimension: int = 0) -> list[tuple[float, float]]:
        """Return (birth, death) of bars with finite lifetime."""
        return [
            (birth, death) for dim, (birth, death) in self.persistence_pairs
            if dim == dimension and death != float("inf")
        ]


# ── Frame Complex Construction ──


def build_frame_complex(
    frame_id: str, conn: sqlite3.Connection,
) -> FrameComplex:
    """Build the frame complex K_F from a frame using the clique complex.

    A subset S ⊆ V is a simplex of K_F iff:
      (i) S ⊆ At(σ) for some schema σ ∈ F, AND
      (ii) S is a clique in the undirected prerequisite graph.

    This is a refinement of Definition 4.1 of the parent paper.  The schema
    membership condition (i) groups KCs into coherent units, while the clique
    condition (ii) ensures simplices reflect actual pairwise integration
    rather than parallel groupings of independent skills.
    """
    atom_sets = compute_all_atom_sets(frame_id, conn)
    prereq_graph = load_prereq_graph(frame_id, conn)

    # Collect all vertices appearing in any schema or in the prereq graph
    all_vertices = set(prereq_graph.nodes)
    for atoms in atom_sets.values():
        all_vertices |= atoms

    vertices = sorted(all_vertices)
    v2i = {v: i for i, v in enumerate(vertices)}
    i2v = {i: v for v, i in v2i.items()}

    # For each schema, find maximal cliques in the prereq subgraph on At(σ).
    # Collect all such cliques, then deduplicate to inclusion-maximal across the frame.
    candidate_cliques: list[frozenset[str]] = []
    seen: set[frozenset[str]] = set()
    for atoms in atom_sets.values():
        if not atoms:
            continue
        for clique in maximal_cliques_in_atoms(atoms, prereq_graph):
            if clique not in seen:
                seen.add(clique)
                candidate_cliques.append(clique)

    # Inclusion-maximal across all schemas
    maximal: list[frozenset[str]] = []
    for c in candidate_cliques:
        if not any(c < other for other in candidate_cliques):
            maximal.append(c)

    # Build simplex tree — insert each maximal simplex (GUDHI adds all faces)
    st = gudhi.SimplexTree()
    for ms in maximal:
        idx = sorted(v2i[v] for v in ms)
        st.insert(idx)

    # Ensure every vertex is present
    for v in vertices:
        st.insert([v2i[v]])

    return FrameComplex(
        vertices=vertices,
        maximal_simplices=maximal,
        vertex_to_index=v2i,
        index_to_vertex=i2v,
        _simplex_tree=st,
    )


# ── Cascading Weight Computation (Definition 4.5) ──


def _ramp(x: float, theta: float) -> float:
    """Ramp function φ(x) = max(0, x - θ) / (1 - θ)."""
    if x <= theta:
        return 0.0
    return (x - theta) / (1.0 - theta)


def compute_weight(
    simplex: frozenset[str],
    t: float,
    scenario: LearnerScenario,
    cache: dict[frozenset[str], float] | None = None,
) -> float:
    """Compute the cascading weight w_S(t) for a simplex S at time t.

    (W1) If S = {v}, then w_S(t) = µ_v(t).
    (W2) If dim(S) ≥ 1, then w_S(t) = φ(min over codim-1 faces T of w_T(t)).
    """
    if cache is not None and simplex in cache:
        return cache[simplex]

    if len(simplex) == 1:
        v = next(iter(simplex))
        mf = scenario.mastery_functions.get(v)
        val = mf.evaluate(t) if mf else 0.0
        if cache is not None:
            cache[simplex] = val
        return val

    # Compute weights of all codimension-1 faces
    vertices = sorted(simplex)
    min_face_weight = float("inf")
    for i in range(len(vertices)):
        face = frozenset(vertices[:i] + vertices[i + 1:])
        fw = compute_weight(face, t, scenario, cache)
        if fw < min_face_weight:
            min_face_weight = fw

    val = _ramp(min_face_weight, scenario.theta)
    if cache is not None:
        cache[simplex] = val
    return val


def compute_all_weights(
    complex: FrameComplex,
    t: float,
    scenario: LearnerScenario,
) -> dict[frozenset[str], float]:
    """Compute weights for all simplices in the complex at time t."""
    cache: dict[frozenset[str], float] = {}
    for idx_simplex, _ in complex.simplex_tree.get_simplices():
        kc_ids = frozenset(complex.index_to_vertex[i] for i in idx_simplex)
        compute_weight(kc_ids, t, scenario, cache)
    return cache


# ── Mastery Filtration (Definition 4.6) ──


def _find_birth_time(
    simplex: frozenset[str],
    scenario: LearnerScenario,
    t_max: float,
    tol: float = 1e-4,
) -> float:
    """Binary search for the earliest t where w_S(t) > 0."""
    cache: dict[frozenset[str], float] = {}
    if compute_weight(simplex, t_max, scenario, cache) <= 0:
        return float("inf")

    lo, hi = 0.0, t_max
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        cache.clear()
        if compute_weight(simplex, mid, scenario, cache) > 0:
            hi = mid
        else:
            lo = mid
    return hi


def _find_threshold_time(
    simplex: frozenset[str],
    scenario: LearnerScenario,
    threshold: float,
    t_max: float,
    tol: float = 1e-4,
) -> float:
    """Binary search for the earliest t where w_S(t) >= threshold.

    Used for realization criterion: a schema is "realized" when every
    maximal clique in it has weight >= θ (the same θ used in the cascade).
    """
    cache: dict[frozenset[str], float] = {}
    if compute_weight(simplex, t_max, scenario, cache) < threshold:
        return float("inf")

    lo, hi = 0.0, t_max
    while hi - lo > tol:
        mid = (lo + hi) / 2.0
        cache.clear()
        if compute_weight(simplex, mid, scenario, cache) >= threshold:
            hi = mid
        else:
            lo = mid
    return hi


def build_mastery_filtration(
    complex: FrameComplex,
    scenario: LearnerScenario,
    t_max: float = 5.0,
) -> gudhi.SimplexTree:
    """Build a filtered simplicial complex with birth times from the mastery model.

    For each simplex S in KF, computes the earliest time t at which w_S(t) > 0
    and assigns that as the filtration value.
    """
    st = gudhi.SimplexTree()

    for idx_simplex, _ in complex.simplex_tree.get_simplices():
        kc_ids = frozenset(complex.index_to_vertex[i] for i in idx_simplex)
        birth = _find_birth_time(kc_ids, scenario, t_max)
        st.insert(idx_simplex, filtration=birth)

    st.make_filtration_non_decreasing()
    return st


# ── Persistent Homology ──


def compute_persistence(
    filtered_tree: gudhi.SimplexTree,
    max_dimension: int = 3,
    t_max: float = 5.0,
    betti_resolution: int = 200,
) -> FiltrationResult:
    """Compute persistent homology and Betti curves from a filtered simplex tree."""
    filtered_tree.compute_persistence()
    raw_pairs = filtered_tree.persistence()

    # Convert to our format
    pairs: list[tuple[int, tuple[float, float]]] = []
    for dim, (birth, death) in raw_pairs:
        if dim > max_dimension:
            continue
        pairs.append((dim, (birth, death)))

    # Compute Betti curves by sampling
    times = [t_max * i / betti_resolution for i in range(betti_resolution + 1)]
    betti_curves: dict[int, list[tuple[float, int]]] = {}

    for d in range(max_dimension + 1):
        dim_pairs = [(b, de) for dim, (b, de) in pairs if dim == d]
        curve: list[tuple[float, int]] = []
        for t in times:
            count = sum(
                1 for b, de in dim_pairs
                if b <= t and (de == float("inf") or t < de)
            )
            curve.append((t, count))
        betti_curves[d] = curve

    return FiltrationResult(
        persistence_pairs=pairs,
        betti_curves=betti_curves,
        time_range=(0.0, t_max),
    )


# ── End-to-end pipeline ──


def analyze_learner(
    frame_id: str,
    scenario: LearnerScenario,
    conn: sqlite3.Connection,
    t_max: float = 5.0,
) -> tuple[FrameComplex, FiltrationResult]:
    """Full pipeline: frame → complex → filtration → persistence."""
    complex = build_frame_complex(frame_id, conn)
    filtered = build_mastery_filtration(complex, scenario, t_max=t_max)
    result = compute_persistence(filtered, t_max=t_max)
    return complex, result


# ── Mastery function builders ──


def make_linear_mastery(
    vertex_id: str,
    rate: float,
    plateau: tuple[float, float] | None = None,
) -> MasteryFunction:
    """Create a mastery function that grows linearly at `rate`, capped at 1.0.

    If plateau is given as (t_start, t_end), mastery freezes at its current
    value during that interval and resumes growing afterward.
    """
    t_cap = 1.0 / rate if rate > 0 else float("inf")
    breakpoints = [MasteryBreakpoint(0.0, 0.0)]

    if plateau is None:
        breakpoints.append(MasteryBreakpoint(t_cap, 1.0))
    else:
        p_start, p_end = plateau
        if p_start >= t_cap:
            # Already at 1.0 before plateau starts
            breakpoints.append(MasteryBreakpoint(t_cap, 1.0))
        else:
            val_at_start = rate * p_start
            breakpoints.append(MasteryBreakpoint(p_start, val_at_start))
            breakpoints.append(MasteryBreakpoint(p_end, val_at_start))
            remaining = 1.0 - val_at_start
            if remaining > 0 and rate > 0:
                t_resume_cap = p_end + remaining / rate
                breakpoints.append(MasteryBreakpoint(t_resume_cap, 1.0))

    return MasteryFunction(vertex_id=vertex_id, breakpoints=breakpoints)


# ── Paper proof-of-concept scenarios (Section 5) ──
#
# These use the simplified 21-node "Counting to 20" frame from the paper,
# with node IDs matching Table 1: 5100, 412, 518, 519, 7100, 8100, etc.
# To use with the actual Living Map data, map these to CNM-prefixed IDs.


# Node rates from Section 5
_PHASE1_NODES = {
    "5100": 1.00, "412": 0.90, "518": 0.80, "519": 0.85,
    "7100": 1.10, "8100": 1.20,
}
_PHASE1_TO_2_NODES = {
    "518": 0.80, "519": 0.85,
}
_PHASE2_NODES = {
    "5200": 0.60, "413": 0.65, "528": 0.55, "529": 0.50,
    "7200": 0.70, "8200": 0.65,
}
_PHASE3_NODES = {
    "5300": 0.40, "539": 0.38, "540": 0.35,
    "7300": 0.42, "8300": 0.40,
}
_TERMINAL_NODES = {
    "601": 0.30, "602": 0.29, "603": 0.28, "604": 0.28,
}

_ALL_RATES: dict[str, float] = {}
_ALL_RATES.update(_PHASE1_NODES)
_ALL_RATES.update(_PHASE2_NODES)
_ALL_RATES.update(_PHASE3_NODES)
_ALL_RATES.update(_TERMINAL_NODES)


def build_paper_scenario_a() -> LearnerScenario:
    """Student A from Section 5: constant rates, no disruption."""
    mfs = {
        nid: make_linear_mastery(nid, rate)
        for nid, rate in _ALL_RATES.items()
    }
    return LearnerScenario(name="Student A", mastery_functions=mfs, theta=0.7)


def build_paper_scenario_b() -> LearnerScenario:
    """Student B from Section 5: plateau on node 413 from t=0.8 to t=2.0.

    Only node 413 is directly modified.  The cascading weight model
    naturally propagates the delay to downstream simplices — edges and
    faces involving Phase 3 nodes appear later because the simplices
    containing 413 (via the phase 2 core schema) have delayed weights.

    For the node-level mastery of downstream nodes, the paper describes
    413's plateau as causing 5300 to be "learned at a reduced rate until
    t = 2.0" and Phase 3 nodes to be "correspondingly delayed."  We model
    this as a reduced rate on 5300 and a time-shifted start on Phase 3 nodes.
    """
    mfs: dict[str, MasteryFunction] = {}

    # Phase 3 and terminal nodes that are downstream of 413
    delayed = {"5300", "539", "540", "7300", "8300", "601", "602", "603", "604"}

    for nid, rate in _ALL_RATES.items():
        if nid == "413":
            mfs[nid] = make_linear_mastery(nid, rate, plateau=(0.8, 2.0))
        elif nid == "5300":
            # 5300 depends on 413; reduced rate until t=2.0, then normal
            mfs[nid] = MasteryFunction(
                vertex_id=nid,
                breakpoints=[
                    MasteryBreakpoint(0.0, 0.0),
                    MasteryBreakpoint(2.0, rate * 0.5 * 2.0),  # half rate for 2 time units
                    MasteryBreakpoint(2.0 + (1.0 - rate * 0.5 * 2.0) / rate, 1.0),
                ],
            )
        elif nid in delayed:
            # Other downstream nodes: delayed start, learning begins at t=1.0
            t_start = 1.0
            mfs[nid] = MasteryFunction(
                vertex_id=nid,
                breakpoints=[
                    MasteryBreakpoint(0.0, 0.0),
                    MasteryBreakpoint(t_start, 0.0),
                    MasteryBreakpoint(t_start + 1.0 / rate, 1.0),
                ],
            )
        else:
            mfs[nid] = make_linear_mastery(nid, rate)

    return LearnerScenario(name="Student B", mastery_functions=mfs, theta=0.7)


# ── Staged Quotient-Filtration Pipeline ──
#
# Processes the schema hierarchy bottom-up.  At each level, child schemas
# have already been collapsed to single quotient vertices, keeping the
# effective dimension small.  A dimension cap handles any remaining large
# schemas (standing in for sub-schemas not yet articulated in the frame).


@dataclass
class QuotientStage:
    """One level in the progressive quotient pipeline."""
    level: int
    schema_id: str
    schema_name: str
    effective_vertices: list[str]  # active vertex IDs (original + quotient)
    complex: FrameComplex
    filtration_result: FiltrationResult
    realization_time: float  # time when top simplex is born (inf if never)


@dataclass
class StagedResult:
    """Complete output of the staged quotient-filtration pipeline."""
    stages: list[QuotientStage]
    quotient_mastery: dict[str, MasteryFunction]  # schema_id → mastery of [σ]


def _compute_schema_levels(
    frame_id: str, conn: sqlite3.Connection,
) -> list[list[dict]]:
    """Compute bottom-up levels of the schema hierarchy.

    Returns a list of levels, each a list of schema dicts with keys:
    id, name, parent_schema_id, children (list of child schema IDs).
    Level 0 = leaf schemas, level 1 = their parents, etc.
    """
    rows = conn.execute(
        "SELECT id, name, parent_schema_id FROM schemas WHERE frame_id = ?",
        (frame_id,),
    ).fetchall()

    schemas = {r["id"]: dict(r) for r in rows}
    for s in schemas.values():
        s["children"] = []
    for s in schemas.values():
        pid = s["parent_schema_id"]
        if pid and pid in schemas:
            schemas[pid]["children"].append(s["id"])

    # Assign levels: leaves = 0, then parents of leaves = 1, etc.
    assigned: dict[str, int] = {}
    remaining = set(schemas.keys())

    while remaining:
        # Find schemas whose children are all assigned (or have no children)
        ready = [
            sid for sid in remaining
            if all(c in assigned for c in schemas[sid]["children"])
        ]
        if not ready:
            break  # shouldn't happen in a tree
        level = max((assigned[c] for sid in ready for c in schemas[sid]["children"]), default=-1) + 1
        # Group by their actual level
        for sid in ready:
            child_levels = [assigned[c] for c in schemas[sid]["children"]]
            assigned[sid] = (max(child_levels) + 1) if child_levels else 0
            remaining.discard(sid)

    # Group by level
    max_level = max(assigned.values(), default=0)
    levels: list[list[dict]] = [[] for _ in range(max_level + 1)]
    for sid, lvl in sorted(assigned.items(), key=lambda x: x[1]):
        levels[lvl].append(schemas[sid])

    return levels


def _build_local_clique_complex(
    vertices: list[str],
    atoms: frozenset[str],
    prereq_graph: nx.Graph,
    max_dim: int,
) -> FrameComplex:
    """Build a clique complex for a single schema's effective atom set.

    Maximal simplices = maximal cliques of prereq_graph restricted to `atoms`.
    Dim cap restricts to k-cliques with k <= max_dim + 1.
    """
    v2i = {v: i for i, v in enumerate(vertices)}
    i2v = {i: v for v, i in v2i.items()}

    cliques = maximal_cliques_in_atoms(atoms, prereq_graph)

    # Dedup and inclusion-maximal
    seen: set[frozenset[str]] = set()
    cand: list[frozenset[str]] = []
    for c in cliques:
        if c not in seen:
            seen.add(c)
            cand.append(c)
    maximal: list[frozenset[str]] = [c for c in cand if not any(c < o for o in cand)]

    st = gudhi.SimplexTree()
    for ms in maximal:
        ms_idx = sorted(v2i[v] for v in ms)
        if len(ms_idx) - 1 <= max_dim:
            st.insert(ms_idx)
        else:
            # Clique exceeds the cap — insert all faces up to max_dim
            for k in range(1, max_dim + 2):
                for combo in combinations(ms_idx, k):
                    st.insert(list(combo))

    for v in vertices:
        st.insert([v2i[v]])

    return FrameComplex(
        vertices=vertices,
        maximal_simplices=maximal,
        vertex_to_index=v2i,
        index_to_vertex=i2v,
        _simplex_tree=st,
    )


def _quotient_undirected_graph(
    G: nx.Graph, atoms: set[str], quotient_vertex: str,
) -> nx.Graph:
    """Contract `atoms` to a single vertex `quotient_vertex` in undirected graph G.

    External edges from any vertex in `atoms` to a vertex outside become edges
    from `quotient_vertex`.  Internal edges are dropped.  The resulting graph
    has one vertex per non-collapsed original vertex plus the quotient vertex.
    """
    H = nx.Graph()
    for v in G.nodes:
        if v not in atoms:
            H.add_node(v)
    H.add_node(quotient_vertex)
    for u, v in G.edges:
        u_in = u in atoms
        v_in = v in atoms
        if u_in and v_in:
            continue  # internal edge, drop
        if u_in:
            H.add_edge(quotient_vertex, v)
        elif v_in:
            H.add_edge(u, quotient_vertex)
        else:
            H.add_edge(u, v)
    return H


def _sample_weight_curve(
    simplex: frozenset[str],
    scenario: LearnerScenario,
    t_max: float,
    n_samples: int = 100,
) -> MasteryFunction:
    """Sample w_S(t) at n_samples points and return as a MasteryFunction.

    Used to create the mastery function for a quotient vertex [σ],
    where µ_[σ](t) = w_∆σ(t).
    """
    breakpoints = []
    for i in range(n_samples + 1):
        t = t_max * i / n_samples
        cache: dict[frozenset[str], float] = {}
        w = compute_weight(simplex, t, scenario, cache)
        breakpoints.append(MasteryBreakpoint(t, min(w, 1.0)))

    # Simplify: remove interior points of constant segments
    simplified = [breakpoints[0]]
    for i in range(1, len(breakpoints) - 1):
        prev_val = simplified[-1].value
        curr_val = breakpoints[i].value
        next_val = breakpoints[i + 1].value
        # Keep if slope changes
        if not (abs(curr_val - prev_val) < 1e-6 and abs(next_val - curr_val) < 1e-6):
            simplified.append(breakpoints[i])
    simplified.append(breakpoints[-1])

    vertex_id = "[" + ",".join(sorted(simplex)) + "]"
    return MasteryFunction(vertex_id=vertex_id, breakpoints=simplified)


def staged_quotient_filtration(
    frame_id: str,
    scenario: LearnerScenario,
    conn: sqlite3.Connection,
    max_dim: int = 4,
    t_max: float = 5.0,
) -> StagedResult:
    """Progressive quotient-filtration pipeline using the clique complex.

    Processes the schema hierarchy bottom-up.  At each level:
    1. Child schemas have already been collapsed to single quotient vertices.
    2. The undirected prereq graph is contracted along those quotients.
    3. Build the local clique complex for this schema's effective atom set,
       restricted to the contracted prereq graph (dim-capped).
    4. Run the mastery filtration and compute persistence.
    5. Determine realization (all maximal cliques in the schema are realized).
    6. Create a mastery function for the quotient vertex [σ].
    """
    levels = _compute_schema_levels(frame_id, conn)
    all_atom_sets = compute_all_atom_sets(frame_id, conn)

    # Initial undirected prereq graph
    prereq_graph = load_prereq_graph(frame_id, conn)

    collapsed: dict[str, str] = {}
    quotient_mastery: dict[str, MasteryFunction] = {}
    stages: list[QuotientStage] = []

    working_scenario = LearnerScenario(
        name=scenario.name,
        mastery_functions=dict(scenario.mastery_functions),
        theta=scenario.theta,
    )

    for level_idx, level_schemas in enumerate(levels):
        for schema_info in level_schemas:
            sid = schema_info["id"]
            sname = schema_info["name"]
            original_atoms = all_atom_sets.get(sid, set())

            if not original_atoms:
                continue

            # Effective vertex set: replace collapsed KCs with quotient vertices
            effective_vertices: set[str] = set()
            for kc in original_atoms:
                if kc in collapsed:
                    effective_vertices.add(collapsed[kc])
                else:
                    effective_vertices.add(kc)

            eff_list = sorted(effective_vertices)
            eff_set = frozenset(eff_list)

            # Build the local clique complex restricted to the current prereq graph
            local_complex = _build_local_clique_complex(
                eff_list, eff_set, prereq_graph, max_dim,
            )

            # Run mastery filtration on the local complex
            filtered = build_mastery_filtration(local_complex, working_scenario, t_max)
            result = compute_persistence(filtered, max_dimension=max_dim, t_max=t_max)

            # Realization time: when ALL maximal cliques in the schema have
            # weight >= θ.  For a singleton {v}, this means µ_v >= θ
            # (the vertex is individually mastered to threshold).  For higher-
            # dim cliques, the cascading weight cascades through faces.
            max_thresholds = []
            for ms in local_complex.maximal_simplices:
                t_th = _find_threshold_time(
                    ms, working_scenario, working_scenario.theta, t_max,
                )
                max_thresholds.append(t_th)
            realization = max(max_thresholds) if max_thresholds else float("inf")

            stages.append(QuotientStage(
                level=level_idx,
                schema_id=sid,
                schema_name=sname,
                effective_vertices=eff_list,
                complex=local_complex,
                filtration_result=result,
                realization_time=realization,
            ))

            # Create quotient mastery: minimum weight across all maximal cliques
            qv_id = f"[{sid}]"
            qv_mastery = _sample_clique_complex_weight(
                local_complex.maximal_simplices, working_scenario, t_max,
            )
            qv_mastery.vertex_id = qv_id

            quotient_mastery[sid] = qv_mastery
            working_scenario.mastery_functions[qv_id] = qv_mastery

            # Contract the prereq graph: collapse the schema's effective atoms
            # to the quotient vertex
            prereq_graph = _quotient_undirected_graph(
                prereq_graph, set(eff_list), qv_id,
            )

            # Record the collapse for original KCs
            for kc in original_atoms:
                collapsed[kc] = qv_id

    return StagedResult(stages=stages, quotient_mastery=quotient_mastery)


def _sample_clique_complex_weight(
    maximal_simplices: list[frozenset[str]],
    scenario: LearnerScenario,
    t_max: float,
    n_samples: int = 100,
) -> MasteryFunction:
    """Quotient mastery for a clique complex: minimum weight across maximal cliques.

    The schema is realized when every maximal clique is realized; the quotient
    vertex's mastery reflects the slowest such clique.
    """
    if not maximal_simplices:
        return MasteryFunction(vertex_id="", breakpoints=[MasteryBreakpoint(0.0, 0.0)])

    breakpoints = []
    for i in range(n_samples + 1):
        t = t_max * i / n_samples
        cache: dict[frozenset[str], float] = {}
        weights = [compute_weight(ms, t, scenario, cache) for ms in maximal_simplices]
        min_w = min(weights)
        breakpoints.append(MasteryBreakpoint(t, min(min_w, 1.0)))

    simplified = [breakpoints[0]]
    for i in range(1, len(breakpoints) - 1):
        if not (abs(breakpoints[i].value - simplified[-1].value) < 1e-6
                and abs(breakpoints[i + 1].value - breakpoints[i].value) < 1e-6):
            simplified.append(breakpoints[i])
    simplified.append(breakpoints[-1])

    return MasteryFunction(vertex_id="", breakpoints=simplified)


# ── Standalone frame for the paper's proof of concept ──


def build_paper_frame_complex() -> FrameComplex:
    """Build the 21-node clique-complex frame from the paper's Section 5.

    21 vertices, 9 schemas forming a laminar family, with prerequisite edges
    encoding the natural pedagogical dependencies described in the paper.

    Uses the clique complex construction: a subset S is a simplex iff
    S ⊆ At(σ) for some schema σ AND S is a clique in the prereq graph.
    """
    vertices = sorted(_ALL_RATES.keys())
    v2i = {v: i for i, v in enumerate(vertices)}
    i2v = {i: v for v, i in v2i.items()}

    # Prerequisite edges from the paper's narrative.
    # Within each phase core, all KCs are pairwise dependent (forming a clique).
    # The bridging KCs connect adjacent phases.
    prereq_edges = [
        # Phase 1 core: all pairwise edges (forms a 4-clique → 3-simplex)
        ("5100", "412"), ("5100", "518"), ("5100", "519"),
        ("412", "518"), ("412", "519"),
        ("518", "519"),
        # Literacy 1-5: pair
        ("7100", "8100"),
        # 5100 → 7100, 8100 → 8200
        ("5100", "7100"), ("8100", "8200"),
        # Phase 2 core: all pairwise (4-clique)
        ("5200", "413"), ("5200", "528"), ("5200", "529"),
        ("413", "528"), ("413", "529"),
        ("528", "529"),
        # Cross-phase
        ("412", "5200"),
        # Literacy 5-10
        ("7200", "8200"),
        ("5200", "7200"), ("8200", "8300"),
        # Phase 3 core: all pairwise (5-clique → 4-simplex)
        ("5300", "539"), ("5300", "540"), ("5300", "7300"), ("5300", "8300"),
        ("539", "540"), ("539", "7300"), ("539", "8300"),
        ("540", "7300"), ("540", "8300"),
        ("7300", "8300"),
        # Cross-phase
        ("413", "5300"),
        ("5300", "7300"),
        # Terminal nodes (depend on Phase 3)
        ("8300", "601"), ("8300", "602"), ("8300", "603"), ("8300", "604"),
    ]

    G = nx.Graph()
    G.add_nodes_from(vertices)
    for u, v in prereq_edges:
        if u in v2i and v in v2i:
            G.add_edge(u, v)

    # Schemas from Section 5 (atom sets)
    schemas = {
        "bridge_1_5": frozenset({"518", "519"}),
        "bridge_5_10": frozenset({"528", "529"}),
        "bridge_10_20": frozenset({"539", "540"}),
        "literacy_1_5": frozenset({"7100", "8100"}),
        "literacy_5_10": frozenset({"7200", "8200"}),
        "literacy_10_20": frozenset({"7300", "8300"}),
        "phase1_core": frozenset({"5100", "412", "518", "519"}),
        "phase2_core": frozenset({"5200", "413", "528", "529"}),
        "phase3_core": frozenset({"5300", "539", "540", "7300", "8300"}),
    }

    # Build maximal cliques per schema, dedup, take inclusion-maximal
    candidate: list[frozenset[str]] = []
    seen: set[frozenset[str]] = set()
    for atoms in schemas.values():
        for clique in maximal_cliques_in_atoms(atoms, G):
            if clique not in seen:
                seen.add(clique)
                candidate.append(clique)
    maximal: list[frozenset[str]] = [c for c in candidate if not any(c < o for o in candidate)]

    st = gudhi.SimplexTree()
    for ms in maximal:
        idx = sorted(v2i[v] for v in ms)
        st.insert(idx)
    for v in vertices:
        st.insert([v2i[v]])

    return FrameComplex(
        vertices=vertices,
        maximal_simplices=maximal,
        vertex_to_index=v2i,
        index_to_vertex=i2v,
        _simplex_tree=st,
    )
