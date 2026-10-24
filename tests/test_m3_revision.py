"""
Unit tests for CognitionRevisionEngine.
"""

import pytest
from src.ecr_neuromemory.interfaces import EngramNode, SynapticEdge
from src.ecr_neuromemory.core.spreading import EngramGraph, SpreadingActivationEngine
from src.ecr_neuromemory.core.revision import CognitionRevisionEngine


def test_cognition_revision_and_inhibition():
    graph = EngramGraph()
    n_old = EngramNode(id="engram_old", content="The capital of Australia is Sydney", activation=0.5)
    n_ctx = EngramNode(id="engram_ctx", content="Geography Facts Australia", activation=1.0)
    
    graph.add_node(n_old)
    graph.add_node(n_ctx)
    graph.add_edge(SynapticEdge(source_id="engram_ctx", target_id="engram_old", weight=0.9))

    revision_engine = CognitionRevisionEngine(default_inhibitory_weight=-0.9)
    res = revision_engine.revise(
        graph,
        contradiction_query="capital Australia Sydney",
        new_fact="The capital of Australia is Canberra",
    )

    assert res.contradiction_detected is True
    assert "engram_old" in res.inhibited_engram_ids
    assert len(res.new_engram_ids) == 1
    new_id = res.new_engram_ids[0]

    # Verify new node exists in graph
    assert new_id in graph.nodes
    assert graph.nodes[new_id].content == "The capital of Australia is Canberra"

    # Verify inhibitory edge: new_id -> engram_old
    outbound_new = graph.get_outbound_edges(new_id)
    assert len(outbound_new) == 1
    assert outbound_new[0].target_id == "engram_old"
    assert outbound_new[0].weight < 0  # Inhibitory

    # Test spreading activation after revision:
    # Seed new_id and engram_ctx. new_id should remain high, engram_old should be suppressed.
    spreading = SpreadingActivationEngine(decay_rate=0.1, transmission_factor=0.8, max_hops=2)
    scores, distances = spreading.spread(graph, initial_seeds={new_id: 1.0, "engram_ctx": 0.8})

    assert new_id in scores
    # engram_old received negative incoming activation from new_id, so its activation should be suppressed below threshold
    assert scores.get("engram_old", 0.0) < 0.3
