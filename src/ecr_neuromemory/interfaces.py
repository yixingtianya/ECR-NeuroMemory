"""
Core data models and abstract interfaces for DSH Memory Plugin.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time


@dataclass
class Message:
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngramNode:
    id: str
    content: str
    embedding: List[float] = field(default_factory=list)
    activation: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_accessed_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynapticEdge:
    source_id: str
    target_id: str
    weight: float = 1.0  # >0 Excitatory, <0 Inhibitory
    stability: float = 1.0  # tau value
    edge_type: str = "excitatory"  # 'excitatory', 'inhibitory', 'hierarchical'
    last_reinforced_at: float = field(default_factory=time.time)


@dataclass
class MemoryContext:
    session_id: str
    messages: List[Message] = field(default_factory=list)
    active_engrams: List[EngramNode] = field(default_factory=list)


@dataclass
class RecallResult:
    query: str
    retrieved_engrams: List[EngramNode] = field(default_factory=list)
    activation_scores: Dict[str, float] = field(default_factory=dict)
    hop_distances: Dict[str, int] = field(default_factory=dict)


@dataclass
class CompressionResult:
    original_message_count: int
    compressed_engram_count: int
    tokens_saved_estimate: int
    new_engrams: List[EngramNode] = field(default_factory=list)


@dataclass
class RevisionResult:
    contradiction_detected: bool
    inhibited_engram_ids: List[str] = field(default_factory=list)
    new_engram_ids: List[str] = field(default_factory=list)
    rewired_edge_count: int = 0


class IDSHMemoryPlugin(ABC):
    """
    Abstract interface for DeepSeek Host (DSH) Memory Plugin.
    """

    @abstractmethod
    def on_session_start(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Called when a new conversation session begins."""
        pass

    @abstractmethod
    def process_message(self, session_id: str, message: Message) -> None:
        """Incorporate a new message into session context and active memory."""
        pass

    @abstractmethod
    def recall_memory(self, query: str, top_k: int = 5) -> RecallResult:
        """Perform associative recall over the engram network given a query."""
        pass

    @abstractmethod
    def compress_context(self, session_id: str, max_tokens: int = 2000) -> CompressionResult:
        """Compress old context turns into engram nodes."""
        pass

    @abstractmethod
    def revise_cognition(self, contradiction_query: str, new_fact: str) -> RevisionResult:
        """Revise cognitive graph when conflicting or updated information arrives."""
        pass

    @abstractmethod
    def on_session_end(self, session_id: str) -> None:
        """Called when a session ends, triggering consolidation and decay."""
        pass
