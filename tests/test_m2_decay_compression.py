"""
Unit tests for decay engine and context compression engine.
"""

import pytest
import time
from src.ecr_neuromemory.interfaces import EngramNode, SynapticEdge, Message
from src.ecr_neuromemory.core.spreading import EngramGraph
from src.ecr_neuromemory.core.decay import CrossSessionDecayEngine
from src.ecr_neuromemory.core.compression import ContextCompressionEngine


def test_ebbinghaus_decay_and_pruning():
    graph = EngramGraph()
    n1 = EngramNode(id="n1", content="Recent Fact")
    n2 = EngramNode(id="n2", content="Weak Fact")
    graph.add_node(n1)
    graph.add_node(n2)

    # Strong edge with high stability vs weak edge with low stability
    edge_strong = SynapticEdge(source_id="n1", target_id="n2", weight=0.8, stability=10.0)
    edge_weak = SynapticEdge(source_id="n2", target_id="n1", weight=0.08, stability=0.0)

    graph.add_edge(edge_strong)
    graph.add_edge(edge_weak)

    decay_engine = CrossSessionDecayEngine(base_decay_rate=0.1, prune_weight_threshold=0.05)

    # Simulate decay over 5 time units
    pruned = decay_engine.apply_decay(graph, elapsed_time_units=5.0)

    # Weak edge should drop below 0.05 and be pruned
    assert ("n2", "n1") in pruned
    assert len(graph.get_outbound_edges("n2")) == 0

    # Strong edge should remain
    assert ("n1", "n2") not in pruned
    assert len(graph.get_outbound_edges("n1")) == 1


def test_ltp_plasticity_reinforcement():
    graph = EngramGraph()
    n1 = EngramNode(id="n1", content="Concept A", activation=0.9)
    n2 = EngramNode(id="n2", content="Concept B", activation=0.9)
    graph.add_node(n1)
    graph.add_node(n2)

    edge = SynapticEdge(source_id="n1", target_id="n2", weight=0.5, stability=1.0)
    graph.add_edge(edge)

    decay_engine = CrossSessionDecayEngine(learning_rate=0.2)
    decay_engine.apply_plasticity(graph, ["n1", "n2"])

    updated_edge = graph.get_outbound_edges("n1")[0]
    assert updated_edge.weight > 0.5
    assert updated_edge.stability > 1.0


def test_context_compression():
    graph = EngramGraph()
    messages = [
        Message(role="user", content="Turn 1 user message"),
        Message(role="assistant", content="Turn 1 assistant answer"),
        Message(role="user", content="Turn 2 user message"),
        Message(role="assistant", content="Turn 2 assistant answer"),
        Message(role="user", content="Turn 3 user message"),
    ]

    comp_engine = ContextCompressionEngine(turns_per_cluster=2)
    res = comp_engine.compress("sess_101", messages, graph)

    assert res.original_message_count == 5
    assert res.compressed_engram_count == 3
    assert len(res.new_engrams) == 3

    # Verify nodes were added to graph
    for engram in res.new_engrams:
        assert engram.id in graph.nodes

    # Verify sequential synaptic edge between engram 0 and engram 1
    e0_id = res.new_engrams[0].id
    e1_id = res.new_engrams[1].id
    outbound = graph.get_outbound_edges(e0_id)
    assert len(outbound) == 1
    assert outbound[0].target_id == e1_id
