"""
Unit tests for M0 interface compliance and plugin lifecycle.
"""

import pytest
import time
from src.ecr_neuromemory.interfaces import (
    Message,
    EngramNode,
    SynapticEdge,
    MemoryContext,
    RecallResult,
    CompressionResult,
    RevisionResult,
    IDSHMemoryPlugin,
)
from src.ecr_neuromemory.plugin import DSHNeuroMemoryPlugin


def test_data_models():
    msg = Message(role="user", content="Hello world")
    assert msg.role == "user"
    assert msg.content == "Hello world"
    assert isinstance(msg.timestamp, float)

    node = EngramNode(id="n1", content="Fact 1", activation=0.5)
    assert node.id == "n1"
    assert node.activation == 0.5

    edge = SynapticEdge(source_id="n1", target_id="n2", weight=0.9, edge_type="excitatory")
    assert edge.weight == 0.9
    assert edge.edge_type == "excitatory"


def test_plugin_interface_subclass():
    plugin = DSHNeuroMemoryPlugin()
    assert isinstance(plugin, IDSHMemoryPlugin)


def test_session_lifecycle():
    plugin = DSHNeuroMemoryPlugin()
    session_id = "test_session_1"

    plugin.on_session_start(session_id)
    assert session_id in plugin.active_sessions

    msg1 = Message(role="user", content="What is the capital of France?")
    msg2 = Message(role="assistant", content="The capital of France is Paris.")
    plugin.process_message(session_id, msg1)
    plugin.process_message(session_id, msg2)

    context = plugin.active_sessions[session_id]
    assert len(context.messages) == 2
    assert context.messages[0].content == "What is the capital of France?"

    plugin.on_session_end(session_id)
    assert session_id not in plugin.active_sessions


def test_recall_and_compression_and_revision_skeletons():
    plugin = DSHNeuroMemoryPlugin()
    session_id = "test_session_2"

    plugin.on_session_start(session_id)
    plugin.process_message(session_id, Message(role="user", content="Paris is France's capital."))
    
    # Compression
    comp_res = plugin.compress_context(session_id)
    assert isinstance(comp_res, CompressionResult)
    assert comp_res.original_message_count == 1
    assert len(comp_res.new_engrams) == 1

    # Recall
    recall_res = plugin.recall_memory("Paris")
    assert isinstance(recall_res, RecallResult)
    assert len(recall_res.retrieved_engrams) >= 1

    # Revision
    rev_res = plugin.revise_cognition("Paris", "The capital of France is now Lyon.")
    assert isinstance(rev_res, RevisionResult)
    assert rev_res.contradiction_detected is True
    assert len(rev_res.new_engram_ids) == 1
