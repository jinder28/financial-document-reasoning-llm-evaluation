"""OpenAI embedding implementation supports RAG context regeneration when enabled."""
from __future__ import annotations

from app.rag.embedding_client_interface import EmbeddingClientInterface


class OpenAIEmbeddingClient(EmbeddingClientInterface):
    """Creates embeddings for claim texts and SEC filing chunks."""

    def __init__(self, embedding_model_id: str) -> None:
        from openai import OpenAI

        self.embedding_model_id = embedding_model_id
        self.openai_client = OpenAI()

    def embed_texts(self, text_values: list[str]) -> list[list[float]]:
        """Calls the configured embedding model for retrieval preparation."""
        response = self.openai_client.embeddings.create(model=self.embedding_model_id, input=text_values)
        return [embedding_record.embedding for embedding_record in response.data]
