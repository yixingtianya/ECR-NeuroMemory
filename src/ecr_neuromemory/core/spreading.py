"""
Engram-Synapse Memory Graph Data Structure and Spreading Activation Engine.
"""

from typing import Dict, List, Set, Tuple, Optional
import math
from ..interfaces import EngramNode, SynapticEdge


class EngramGraph:
    """
    Manages engram nodes and directed synaptic edges.
    """

    def __init__(self):
        self.nodes: Dict[str, EngramNode] = {}
        # Adjacency list: source_id -> list of SynapticEdge
        self.adjacency: Dict[str, List[SynapticEdge]] = {}

    def add_node(self, node: EngramNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self.adjacency:
            self.adjacency[node.id] = []

    def add_edge(self, edge: SynapticEdge) -> None:
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError(f"Both nodes ({edge.source_id}, {edge.target_id}) must exist in graph.")
        
        # Check if edge already exists, update if so
        existing_edges = self.adjacency[edge.source_id]
        for idx, e in enumerate(existing_edges):
            if e.target_id == edge.target_id:
                existing_edges[idx] = edge
                return
        existing_edges.append(edge)

    def get_outbound_edges(self, node_id: str) -> List[SynapticEdge]:
        return self.adjacency.get(node_id, [])

    def reset_activations(self) -> None:
        for node in self.nodes.values():
            node.activation = 0.0


class SpreadingActivationEngine:
    """
    Implements multi-hop spreading activation over an EngramGraph.
    Formula:
      A_j(t+1) = clamp( A_j(t)*(1 - delta) + sum_{i in Pred(j)} A_i(t) * w_ij * alpha, 0.0, 1.0 )
    """

    def __init__(self, decay_rate: float = 0.15, transmission_factor: float = 0.8, max_hops: int = 3):
        self.decay_rate = decay_rate
        self.transmission_factor = transmission_factor
        self.max_hops = max_hops

    def spread(
        self,
        graph: EngramGraph,
        initial_seeds: Dict[str, float],
        activation_threshold: float = 0.3,
    ) -> Tuple[Dict[str, float], Dict[str, int]]:
        """
        Executes spreading activation starting from seed nodes.
        Returns:
          activation_scores: node_id -> final activation score
          hop_distances: node_id -> minimum hop distance from seeds
        """
        graph.reset_activations()
        current_activations: Dict[str, float] = {node_id: 0.0 for node_id in graph.nodes}
        hop_distances: Dict[str, int] = {}

        # Set initial seed activations
        for node_id, score in initial_seeds.items():
            if node_id in graph.nodes:
                current_activations[node_id] = min(1.0, max(0.0, score))
                graph.nodes[node_id].activation = current_activations[node_id]
                hop_distances[node_id] = 0

        for hop in range(1, self.max_hops + 1):
            next_activations: Dict[str, float] = {}

            # Calculate retained baseline activation after decay
            for node_id in graph.nodes:
                retained = current_activations[node_id] * (1.0 - self.decay_rate)
                # Seed nodes receive continuous stimulation during spreading phase
                if node_id in initial_seeds:
                    retained = max(retained, initial_seeds[node_id])
                next_activations[node_id] = retained

            # Accumulate incoming signals from predecessors
            for src_id, edges in graph.adjacency.items():
                src_act = current_activations[src_id]
                if src_act <= 0.0:
                    continue

                for edge in edges:
                    target_id = edge.target_id
                    # Transmitted signal = A_src * weight * alpha
                    incoming_signal = src_act * edge.weight * self.transmission_factor
                    next_activations[target_id] += incoming_signal

                    # Record minimum hop distance if significant signal was transferred
                    if incoming_signal > 0.05 and target_id not in hop_distances:
                        hop_distances[target_id] = hop

            # Clamp activations to [0, 1]
            for node_id in next_activations:
                clamped = min(1.0, max(0.0, next_activations[node_id]))
                next_activations[node_id] = clamped
                graph.nodes[node_id].activation = clamped

            current_activations = next_activations

        # Filter nodes above activation_threshold
        result_scores = {
            node_id: score
            for node_id, score in current_activations.items()
            if score >= activation_threshold
        }

        return result_scores, hop_distances
