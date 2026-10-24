"""
Cross-Session Ebbinghaus Memory Decay, LTP/LTD Synaptic Plasticity, and Pruning.
"""

import math
import time
from typing import List, Dict, Tuple
from ..interfaces import SynapticEdge, EngramNode
from .spreading import EngramGraph


class CrossSessionDecayEngine:
    """
    Handles Ebbinghaus exponential decay across session gaps and LTP/LTD plasticity.
    """

    def __init__(
        self,
        base_decay_rate: float = 0.05,
        prune_weight_threshold: float = 0.05,
        learning_rate: float = 0.1,
    ):
        self.base_decay_rate = base_decay_rate
        self.prune_weight_threshold = prune_weight_threshold
        self.learning_rate = learning_rate

    def apply_decay(
        self,
        graph: EngramGraph,
        elapsed_time_units: float,
    ) -> List[Tuple[str, str]]:
        """
        Applies exponential decay formula:
          w_{ij}(t + delta_t) = w_{ij}(t) * exp( - gamma * delta_t / (tau_{ij} + 1) )
        Prunes edges where |w_{ij}| < prune_weight_threshold.
        Returns list of pruned edge tuples: (source_id, target_id)
        """
        pruned_edges: List[Tuple[str, str]] = []

        for src_id, edges in graph.adjacency.items():
            remaining_edges: List[SynapticEdge] = []
            for edge in edges:
                decay_factor = math.exp(
                    -self.base_decay_rate * elapsed_time_units / (edge.stability + 1.0)
                )
                edge.weight *= decay_factor

                if abs(edge.weight) < self.prune_weight_threshold:
                    pruned_edges.append((edge.source_id, edge.target_id))
                else:
                    remaining_edges.append(edge)

            graph.adjacency[src_id] = remaining_edges

        return pruned_edges

    def apply_plasticity(
        self,
        graph: EngramGraph,
        activated_node_ids: List[str],
    ) -> None:
        """
        Applies Long-Term Potentiation (LTP) to co-activated engrams.
        Increases weight and stability factor tau.
        """
        node_set = set(activated_node_ids)
        for src_id in node_set:
            outbound = graph.get_outbound_edges(src_id)
            for edge in outbound:
                if edge.target_id in node_set:
                    # LTP reinforcement
                    src_act = graph.nodes[src_id].activation if src_id in graph.nodes else 1.0
                    tgt_act = graph.nodes[edge.target_id].activation if edge.target_id in graph.nodes else 1.0
                    delta_w = self.learning_rate * max(src_act, 0.5) * max(tgt_act, 0.5)
                    
                    if edge.weight >= 0:
                        edge.weight = min(1.0, edge.weight + delta_w)
                    else:
                        edge.weight = max(-1.0, edge.weight - delta_w)
                    
                    edge.stability += 0.5
                    edge.last_reinforced_at = time.time()
