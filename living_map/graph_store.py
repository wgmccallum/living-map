"""In-memory NetworkX graphs synced with SQLite.

Two DiGraph instances:
  - knowledge_graph: KCs as nodes, prerequisite edges
  - math_graph: math concepts as nodes, structural dependency edges
"""

from __future__ import annotations

import sqlite3
from typing import Any

import networkx as nx


class CycleError(Exception):
    pass


class GraphStore:
    """Dual-representation store: SQLite (persistent) + NetworkX (in-memory queries)."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.knowledge_graph = nx.DiGraph()
        self.math_graph = nx.DiGraph()
        self._load_from_db()

    def _load_from_db(self):
        """Load both graphs from SQLite."""
        # Knowledge Map
        self.knowledge_graph.clear()
        for row in self.conn.execute("SELECT id FROM knowledge_components"):
            self.knowledge_graph.add_node(row["id"])
        for row in self.conn.execute(
            "SELECT source_kc_id, target_kc_id FROM prerequisite_edges"
        ):
            self.knowledge_graph.add_edge(row["source_kc_id"], row["target_kc_id"])

        # Math Structure Map
        self.math_graph.clear()
        for row in self.conn.execute("SELECT id FROM math_concepts"):
            self.math_graph.add_node(row["id"])
        for row in self.conn.execute(
            "SELECT source_id, target_id FROM math_concept_edges"
        ):
            self.math_graph.add_edge(row["source_id"], row["target_id"])

    def reload(self):
        self._load_from_db()

    # --- Knowledge Map mutations ---

    def add_kc(self, kc_id: str):
        self.knowledge_graph.add_node(kc_id)

    def remove_kc(self, kc_id: str):
        if kc_id in self.knowledge_graph:
            self.knowledge_graph.remove_node(kc_id)

    def add_prerequisite_edge(self, source_id: str, target_id: str):
        """Add edge, raising CycleError if it would create a cycle."""
        if source_id == target_id:
            raise CycleError(f"Self-loop: {source_id}")
        if nx.has_path(self.knowledge_graph, target_id, source_id):
            raise CycleError(
                f"Adding edge {source_id} -> {target_id} would create a cycle: "
                f"{target_id} is already an ancestor of {source_id}"
            )
        self.knowledge_graph.add_edge(source_id, target_id)

    def remove_prerequisite_edge(self, source_id: str, target_id: str):
        if self.knowledge_graph.has_edge(source_id, target_id):
            self.knowledge_graph.remove_edge(source_id, target_id)

    # --- Math Structure Map mutations ---

    def add_math_concept(self, concept_id: str):
        self.math_graph.add_node(concept_id)

    def remove_math_concept(self, concept_id: str):
        if concept_id in self.math_graph:
            self.math_graph.remove_node(concept_id)

    def add_math_concept_edge(self, source_id: str, target_id: str):
        if source_id == target_id:
            raise CycleError(f"Self-loop: {source_id}")
        if nx.has_path(self.math_graph, target_id, source_id):
            raise CycleError(
                f"Adding edge {source_id} -> {target_id} would create a cycle"
            )
        self.math_graph.add_edge(source_id, target_id)

    def remove_math_concept_edge(self, source_id: str, target_id: str):
        if self.math_graph.has_edge(source_id, target_id):
            self.math_graph.remove_edge(source_id, target_id)

    # --- Knowledge Map queries ---

    def ancestors(self, kc_id: str) -> set[str]:
        return nx.ancestors(self.knowledge_graph, kc_id)

    def descendants(self, kc_id: str) -> set[str]:
        return nx.descendants(self.knowledge_graph, kc_id)

    def neighborhood(self, kc_id: str, depth: int = 2) -> set[str]:
        result = set()
        undirected = self.knowledge_graph.to_undirected()
        for node in nx.single_source_shortest_path_length(undirected, kc_id, cutoff=depth):
            result.add(node)
        result.discard(kc_id)
        return result

    def all_paths(self, from_id: str, to_id: str) -> list[list[str]]:
        try:
            return list(nx.all_simple_paths(self.knowledge_graph, from_id, to_id))
        except nx.NodeNotFound:
            return []

    def predecessors(self, kc_id: str) -> list[str]:
        return list(self.knowledge_graph.predecessors(kc_id))

    def successors(self, kc_id: str) -> list[str]:
        return list(self.knowledge_graph.successors(kc_id))

    # --- Math Structure Map queries ---

    def math_ancestors(self, concept_id: str) -> set[str]:
        return nx.ancestors(self.math_graph, concept_id)

    def math_descendants(self, concept_id: str) -> set[str]:
        return nx.descendants(self.math_graph, concept_id)

    # --- Stats ---

    def stats(self) -> dict[str, Any]:
        kg = self.knowledge_graph
        mg = self.math_graph
        km_components = (
            nx.number_weakly_connected_components(kg) if len(kg) > 0 else 0
        )
        mm_components = (
            nx.number_weakly_connected_components(mg) if len(mg) > 0 else 0
        )
        km_longest = nx.dag_longest_path_length(kg) if len(kg) > 0 else 0
        return {
            "knowledge_map": {
                "node_count": kg.number_of_nodes(),
                "edge_count": kg.number_of_edges(),
                "connected_components": km_components,
                "longest_path_length": km_longest,
            },
            "math_structure_map": {
                "node_count": mg.number_of_nodes(),
                "edge_count": mg.number_of_edges(),
                "connected_components": mm_components,
            },
        }
