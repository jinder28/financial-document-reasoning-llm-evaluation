"""Local cosine vector store provides a lightweight FAISS-compatible boundary."""
from __future__ import annotations

import math
from app.rag.vector_store_interface import VectorStoreInterface


class InMemoryCosineVectorStore(VectorStoreInterface):
    """Stores embeddings locally for reproducible dissertation-scale retrieval."""

    def __init__(self) -> None:
        self.vector_records: list[dict] = []

    def add_vectors(self, vector_records: list[dict]) -> None:
        """Adds embedded filing chunks to the local vector store."""
        self.vector_records.extend(vector_records)

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        """Returns top-k chunks ranked by cosine similarity."""
        scored_records: list[dict] = []
        for vector_record in self.vector_records:
            score = self._cosine_similarity(query_vector, vector_record["embedding"])
            ranked_record = {key: value for key, value in vector_record.items() if key != "embedding"}
            ranked_record["score"] = score
            scored_records.append(ranked_record)
        return sorted(scored_records, key=lambda record: record["score"], reverse=True)[:top_k]

    @staticmethod
    def _cosine_similarity(left_vector: list[float], right_vector: list[float]) -> float:
        """Calculates similarity while avoiding datastore-specific dependencies."""
        dot_product = sum(left_value * right_value for left_value, right_value in zip(left_vector, right_vector))
        left_norm = math.sqrt(sum(left_value * left_value for left_value in left_vector))
        right_norm = math.sqrt(sum(right_value * right_value for right_value in right_vector))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot_product / (left_norm * right_norm)
