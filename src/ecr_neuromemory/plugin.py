"""
Integrated DSH NeuroMemory Plugin using spreading activation, cross-session decay, context compression, and cognition revision engines.
"""

from typing import Dict, List, Optional, Any
import time

from .interfaces import (
    IDSHMemoryPlugin,
    Message,
    EngramNode,
    SynapticEdge,
    MemoryContext,
    RecallResult,
    CompressionResult,
    RevisionResult,
)
from .core.spreading import EngramGraph, SpreadingActivationEngine
from .core.decay import CrossSessionDecayEngine
from .core.compression import ContextCompressionEngine
from .core.revision import CognitionRevisionEngine, tokenize_text


class DSHNeuroMemoryPlugin(IDSHMemoryPlugin):
    """
    Production-grade Long-Term Neural-Associative Memory Plugin for DSH Hosts.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.active_sessions: Dict[str, MemoryContext] = {}
        self.graph = EngramGraph()

        decay_rate = self.config.get("decay_rate", 0.15)
        transmission = self.config.get("transmission_factor", 0.8)
        max_hops = self.config.get("max_hops", 3)
        
        self.spreading_engine = SpreadingActivationEngine(
            decay_rate=decay_rate,
            transmission_factor=transmission,
            max_hops=max_hops,
        )
        self.decay_engine = CrossSessionDecayEngine(
            base_decay_rate=self.config.get("base_decay_rate", 0.05),
            prune_weight_threshold=self.config.get("prune_threshold", 0.05),
            learning_rate=self.config.get("learning_rate", 0.1),
        )
        self.compression_engine = ContextCompressionEngine(
            turns_per_cluster=self.config.get("turns_per_cluster", 4)
        )
        self.revision_engine = CognitionRevisionEngine(
            default_inhibitory_weight=self.config.get("inhibitory_weight", -0.85)
        )

        self.last_session_time: Optional[float] = None
        self.is_initialized = True

    def on_session_start(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = MemoryContext(
                session_id=session_id,
                messages=[],
                active_engrams=[],
            )

        now = time.time()
        if self.last_session_time is not None:
            elapsed_time_units = max(0.0, (now - self.last_session_time) / 3600.0)
            if elapsed_time_units > 0.01:
                self.decay_engine.apply_decay(self.graph, elapsed_time_units)

    def process_message(self, session_id: str, message: Message) -> None:
        if session_id not in self.active_sessions:
            self.on_session_start(session_id)
        
        self.active_sessions[session_id].messages.append(message)

        if len(message.content) > 5:
            engram_id = f"engram_msg_{session_id}_{len(self.active_sessions[session_id].messages)}_{int(time.time())}"
            node = EngramNode(
                id=engram_id,
                content=message.content,
                activation=0.8,
                metadata={"role": message.role, "session_id": session_id},
            )
            self.graph.add_node(node)
            self.active_sessions[session_id].active_engrams.append(node)

    def recall_memory(self, query: str, top_k: int = 5) -> RecallResult:
        query_tokens = tokenize_text(query)
        seed_nodes: Dict[str, float] = {}

        for node_id, node in self.graph.nodes.items():
            node_tokens = tokenize_text(node.content)
            overlap = query_tokens.intersection(node_tokens)
            if overlap:
                match_score = min(1.0, len(overlap) / float(max(1, len(query_tokens))))
                seed_nodes[node_id] = max(0.6, match_score)

        if not seed_nodes:
            return RecallResult(query=query, retrieved_engrams=[], activation_scores={}, hop_distances={})

        scores, distances = self.spreading_engine.spread(
            self.graph,
            initial_seeds=seed_nodes,
            activation_threshold=0.25,
        )

        retrieved_ids = list(scores.keys())
        if len(retrieved_ids) > 1:
            self.decay_engine.apply_plasticity(self.graph, retrieved_ids)

        sorted_ids = sorted(retrieved_ids, key=lambda nid: scores[nid], reverse=True)[:top_k]
        retrieved_nodes = [self.graph.nodes[nid] for nid in sorted_ids]

        return RecallResult(
            query=query,
            retrieved_engrams=retrieved_nodes,
            activation_scores={nid: scores[nid] for nid in sorted_ids},
            hop_distances={nid: distances.get(nid, 0) for nid in sorted_ids},
        )

    def compress_context(self, session_id: str, max_tokens: int = 2000) -> CompressionResult:
        context = self.active_sessions.get(session_id)
        if not context or not context.messages:
            return CompressionResult(0, 0, 0, [])

        res = self.compression_engine.compress(
            session_id=session_id,
            messages=context.messages,
            graph=self.graph,
            max_tokens=max_tokens,
        )
        return res

    def revise_cognition(self, contradiction_query: str, new_fact: str) -> RevisionResult:
        return self.revision_engine.revise(
            graph=self.graph,
            contradiction_query=contradiction_query,
            new_fact=new_fact,
        )

    def on_session_end(self, session_id: str) -> None:
        self.last_session_time = time.time()
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
