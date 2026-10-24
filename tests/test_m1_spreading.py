"""
Unit tests for EngramGraph and SpreadingActivationEngine.
"""

import pytest
from src.ecr_neuromemory.interfaces import EngramNode, SynapticEdge
from src.ecr_neuromemory.core.spreading import EngramGraph, SpreadingActivationEngine


def test_engram_graph_operations():
    graph = EngramGraph()
    n1 = EngramNode(id="n1", content="Python Programming")
    n2 = EngramNode(id="n2", content="Machine Learning")
    
    graph.add_node(n1)
    graph.add_node(n2)
    
    assert "n1" in graph.nodes
    assert "n2" in graph.nodes

    edge = SynapticEdge(source_id="n1", target_id="n2", weight=0.8)
    graph.add_edge(edge)

    outbound = graph.get_outbound_edges("n1")
    assert len(outbound) == 1
    assert outbound[0].target_id == "n2"
    assert outbound[0].weight == 0.8


def test_spreading_activation_multihop():
    """
    Test indirect associative recall across 2 hops:
    Seed (A) -> Synapse(0.9) -> (B) -> Synapse(0.8) -> (C)
    C should be activated even though it is not directly seeded.
    """
    graph = EngramGraph()
    nA = EngramNode(id="A", content="Artificial Intelligence")
    nB = EngramNode(id="B", content="Neural Networks")
    nC = EngramNode(id="C", content="Backpropagation Algorithm")
    
    graph.add_node(nA)
    graph.add_node(nB)
    graph.add_node(nC)

    graph.add_edge(SynapticEdge(source_id="A", target_id="B", weight=0.9))
    graph.add_edge(SynapticEdge(source_id="B", target_id="C", weight=0.8))

    engine = SpreadingActivationEngine(decay_rate=0.1, transmission_factor=0.8, max_hops=3)

    # Seed only node A
    seeds = {"A": 1.0}
    scores, distances = engine.spread(graph, seeds, activation_threshold=0.2)

    assert "A" in scores
    assert "B" in scores
    assert "C" in scores

    # Distance check
    assert distances["A"] == 0
    assert distances["B"] == 1
    assert distances["C"] == 2

    # Score progression check: A > B > C
    assert scores["A"] >= scores["B"]
    assert scores["B"] >= scores["C"]


def test_inhibitory_synapse_suppression():
    """
    Test that inhibitory synapses (weight < 0) reduce activation of target nodes.
    A -> (weight -0.8) -> B
    """
    graph = EngramGraph()
    nA = EngramNode(id="A", content="Contradiction Seed")
    nB = EngramNode(id="B", content="Old Belief")

    graph.add_node(nA)
    graph.add_node(nB)

    # B has an initial activation, A is heavily activated with inhibitory edge to B
    graph.add_edge(SynapticEdge(source_id="A", target_id="B", weight=-0.9, edge_type="inhibitory"))

    engine = SpreadingActivationEngine(decay_rate=0.1, transmission_factor=0.8, max_hops=2)

    seeds = {"A": 1.0, "B": 0.5}
    scores, distances = engine.spread(graph, seeds, activation_threshold=0.1)

    # Node B should be suppressed by negative incoming activation from A
    assert scores.get("B", 0.0) < 0.5
