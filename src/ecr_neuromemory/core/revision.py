"""
Cognition Revision Engine: Detects contradictions, rewires synapses, and applies inhibitory plasticity.
"""

from typing import List, Optional, Tuple, Dict, Any, Set
import time
import re
from ..interfaces import EngramNode, SynapticEdge, RevisionResult
from .spreading import EngramGraph


def tokenize_text(text: str) -> Set[str]:
    """
    Tokenizes text with support for both CJK characters and space-separated words,
    stripping punctuation and normalizing to lowercase.
    """
    text_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text.lower())
    tokens = set()
    
    # Extract English/numeric words
    words = re.findall(r'[a-z0-9]+', text_clean)
    stop_words = {"the", "is", "of", "a", "an", "and", "or", "in", "on", "at", "to", "are", "was", "were"}
    for w in words:
        if w not in stop_words:
            tokens.add(w)
            
    # Extract CJK characters (unigrams and bigrams)
    cjk_chars = re.findall(r'[\u4e00-\u9fff]', text)
    for ch in cjk_chars:
        tokens.add(ch)
    for i in range(len(cjk_chars) - 1):
        tokens.add(cjk_chars[i] + cjk_chars[i+1])

    return tokens


class CognitionRevisionEngine:
    """
    Handles belief updates and knowledge graph revision when contradictions are detected.
    """

    def __init__(self, default_inhibitory_weight: float = -0.85):
        self.default_inhibitory_weight = default_inhibitory_weight

    def find_conflicting_nodes(
        self,
        graph: EngramGraph,
        contradiction_query: str,
    ) -> List[EngramNode]:
        """
        Identifies existing engram nodes that conflict with the new query/fact.
        Requires significant semantic token overlap.
        """
        conflicts = []
        query_tokens = tokenize_text(contradiction_query)

        if not query_tokens:
            return []

        for node in graph.nodes.values():
            node_tokens = tokenize_text(node.content)
            overlap = query_tokens.intersection(node_tokens)
            
            if len(query_tokens) <= 2:
                if len(overlap) == len(query_tokens):
                    conflicts.append(node)
            else:
                if len(overlap) >= 2 and (len(overlap) / len(query_tokens)) >= 0.4:
                    conflicts.append(node)

        return conflicts

    def revise(
        self,
        graph: EngramGraph,
        contradiction_query: str,
        new_fact: str,
    ) -> RevisionResult:
        """
        Revises cognition by:
        1. Finding old conflicting engrams.
        2. Creating a new engram with updated fact.
        3. Adding an inhibitory edge from new engram to old engram(s).
        4. Converting existing positive edges to old engram into edges targeting the new engram.
        """
        conflicting_nodes = self.find_conflicting_nodes(graph, contradiction_query)
        if not conflicting_nodes:
            new_id = f"engram_rev_{int(time.time())}"
            new_node = EngramNode(id=new_id, content=new_fact, activation=1.0)
            graph.add_node(new_node)
            return RevisionResult(
                contradiction_detected=False,
                inhibited_engram_ids=[],
                new_engram_ids=[new_id],
                rewired_edge_count=0,
            )

        new_id = f"engram_rev_{int(time.time())}"
        new_node = EngramNode(id=new_id, content=new_fact, activation=1.0)
        graph.add_node(new_node)

        inhibited_ids = []
        rewired_count = 0

        for old_node in conflicting_nodes:
            inhibited_ids.append(old_node.id)

            inhibitory_edge = SynapticEdge(
                source_id=new_id,
                target_id=old_node.id,
                weight=self.default_inhibitory_weight,
                edge_type="inhibitory",
            )
            graph.add_edge(inhibitory_edge)
            rewired_count += 1

            for src_id, edges in graph.adjacency.items():
                if src_id == new_id or src_id == old_node.id:
                    continue
                for edge in edges:
                    if edge.target_id == old_node.id and edge.weight > 0:
                        new_edge = SynapticEdge(
                            source_id=src_id,
                            target_id=new_id,
                            weight=edge.weight,
                            edge_type=edge.edge_type,
                        )
                        graph.add_edge(new_edge)
                        edge.weight *= 0.2
                        rewired_count += 1

        return RevisionResult(
            contradiction_detected=True,
            inhibited_engram_ids=inhibited_ids,
            new_engram_ids=[new_id],
            rewired_edge_count=rewired_count,
        )
