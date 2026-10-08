"""Embedding client abstraction keeps retrieval preparation model-provider neutral."""
from __future__ import annotations

from typing import Protocol


class EmbeddingClientInterface(Protocol):
    """Defines embedding behaviour needed for optional RAG context rebuilding."""

    def embed_texts(self, text_values: list[str]) -> list[list[float]]:
        """Embeds texts for vector retrieval without tying callers to a vendor."""
        raise NotImplementedError
