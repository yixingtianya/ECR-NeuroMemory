"""
Context Compression Engine: Summarizes conversation history into engram clusters.
"""

from typing import List, Tuple, Dict, Any
import time
from ..interfaces import Message, EngramNode, SynapticEdge, CompressionResult
from .spreading import EngramGraph


class ContextCompressionEngine:
    """
    Compresses conversation context turns into abstracted engram clusters.
    """

    def __init__(self, turns_per_cluster: int = 4):
        self.turns_per_cluster = turns_per_cluster

    def compress(
        self,
        session_id: str,
        messages: List[Message],
        graph: EngramGraph,
        max_tokens: int = 2000,
    ) -> CompressionResult:
        if not messages:
            return CompressionResult(0, 0, 0, [])

        total_msgs = len(messages)
        new_engrams: List[EngramNode] = []

        # Process messages in chunks of turns_per_cluster
        for i in range(0, total_msgs, self.turns_per_cluster):
            chunk = messages[i : i + self.turns_per_cluster]
            chunk_text = " | ".join([f"{m.role}: {m.content}" for m in chunk])

            engram_id = f"engram_{session_id}_c{i//self.turns_per_cluster}_{int(time.time())}"
            summary_content = f"Summary Cluster ({len(chunk)} turns): {chunk_text[:120]}..."

            engram = EngramNode(
                id=engram_id,
                content=summary_content,
                activation=1.0,
                metadata={"session_id": session_id, "start_turn": i, "end_turn": i + len(chunk)},
            )
            graph.add_node(engram)
            new_engrams.append(engram)

            # Connect sequential engram clusters with excitatory synaptic edges
            if len(new_engrams) > 1:
                prev_engram = new_engrams[-2]
                edge = SynapticEdge(
                    source_id=prev_engram.id,
                    target_id=engram.id,
                    weight=0.75,
                    edge_type="sequential",
                )
                graph.add_edge(edge)

        raw_tokens = sum(len(m.content.split()) for m in messages)
        compressed_tokens = sum(len(e.content.split()) for e in new_engrams)
        tokens_saved = max(10, raw_tokens * 4 - compressed_tokens)

        return CompressionResult(
            original_message_count=total_msgs,
            compressed_engram_count=len(new_engrams),
            tokens_saved_estimate=tokens_saved,
            new_engrams=new_engrams,
        )
