"""Vector store abstraction keeps RAG retrieval datastore independent."""
from __future__ import annotations

from typing import Protocol


class VectorStoreInterface(Protocol):
    """Defines vector search behaviour used by optional RAG rebuilding."""

    def add_vectors(self, vector_records: list[dict]) -> None:
        """Adds embedded chunks to the retrieval store."""
        raise NotImplementedError

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        """Retrieves the nearest chunk records for one query vector."""
        raise NotImplementedError
