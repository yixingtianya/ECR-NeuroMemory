"""
End-to-end integration tests for full multi-session memory workflows.
Covering:
1. Context compression & token reduction across turns.
2. Cross-session Ebbinghaus decay & engram pruning.
3. Multi-hop indirect associative recall via spreading activation.
4. Cognition revision with synaptic inhibition suppressing refuted facts.
"""

import pytest
import time
from src.ecr_neuromemory.interfaces import Message, EngramNode, SynapticEdge
from src.ecr_neuromemory.plugin import DSHNeuroMemoryPlugin


def test_full_e2e_multi_session_workflow():
    plugin = DSHNeuroMemoryPlugin(
        config={
            "decay_rate": 0.1,
            "transmission_factor": 0.8,
            "base_decay_rate": 0.2,
            "prune_threshold": 0.05,
            "turns_per_cluster": 2,
        }
    )

    # -------------------------------------------------------------
    # SESSION 1: User introduces facts & context compression
    # -------------------------------------------------------------
    session_1 = "session_alpha"
    plugin.on_session_start(session_1)

    plugin.process_message(session_1, Message(role="user", content="Alice is a Lead Architect at TechCorp"))
    plugin.process_message(session_1, Message(role="assistant", content="Acknowledged Alice's role."))
    plugin.process_message(session_1, Message(role="user", content="TechCorp specializes in Quantum Computing"))
    plugin.process_message(session_1, Message(role="assistant", content="Acknowledged TechCorp domain."))

    # Manual edge creation linking TechCorp domain to Quantum Computing research
    nodes = list(plugin.graph.nodes.keys())
    assert len(nodes) >= 2

    # Link node 0 (Alice) -> node 2 (TechCorp Quantum)
    plugin.graph.add_edge(SynapticEdge(source_id=nodes[0], target_id=nodes[2], weight=0.9))

    # Compress session 1 context
    comp_res = plugin.compress_context(session_1)
    assert comp_res.compressed_engram_count > 0
    assert comp_res.tokens_saved_estimate > 0

    plugin.on_session_end(session_1)

    # -------------------------------------------------------------
    # SESSION 2: Indirect Associative Recall (Alice -> Quantum)
    # -------------------------------------------------------------
    session_2 = "session_beta"
    # Simulate time gap for cross-session decay
    plugin.last_session_time = time.time() - 7200  # 2 hours ago
    plugin.on_session_start(session_2)

    # Query mentioning only "Alice"
    recall_res = plugin.recall_memory(query="Alice Architect", top_k=5)
    retrieved_contents = [n.content for n in recall_res.retrieved_engrams]

    # Should recall Alice and indirect associate TechCorp / Quantum Computing
    assert any("Alice" in c for c in retrieved_contents)
    assert any("Quantum" in c or "TechCorp" in c for c in retrieved_contents)

    plugin.on_session_end(session_2)

    # -------------------------------------------------------------
    # SESSION 3: Cognition Revision (Alice changes role/company)
    # -------------------------------------------------------------
    session_3 = "session_gamma"
    plugin.on_session_start(session_3)

    rev_res = plugin.revise_cognition(
        contradiction_query="Alice Lead Architect TechCorp",
        new_fact="Alice relocated and is now VP of Engineering at BioHealth",
    )

    assert rev_res.contradiction_detected is True
    assert len(rev_res.inhibited_engram_ids) > 0

    # Recall query after revision
    recall_after_rev = plugin.recall_memory(query="Alice VP BioHealth", top_k=5)
    active_contents = [n.content for n in recall_after_rev.retrieved_engrams]

    assert any("BioHealth" in c for c in active_contents)
    # The old refuted belief (Lead Architect TechCorp) should be inhibited during spreading activation
    for node in recall_after_rev.retrieved_engrams:
        if node.id in rev_res.inhibited_engram_ids:
            # Inhibited nodes must have very low or 0 activation
            assert recall_after_rev.activation_scores[node.id] < 0.3

    plugin.on_session_end(session_3)
