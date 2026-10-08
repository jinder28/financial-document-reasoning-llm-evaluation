"""RAG context builder reproduces retrieved evidence for RAG-condition prompts."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from app.common.jsonl_table import write_jsonl_records
from app.rag.embedding_client_interface import EmbeddingClientInterface
from app.rag.vector_store_interface import VectorStoreInterface


class RagContextBuilder:
    """Builds top-k retrieved contexts from chunk records and claim texts."""

    def __init__(self, embedding_client: EmbeddingClientInterface, vector_store_factory) -> None:
        self.embedding_client = embedding_client
        self.vector_store_factory = vector_store_factory

    def build_context_records(
        self,
        queue_records: list[dict[str, str]],
        chunk_records: list[dict[str, object]],
        top_k: int,
        embedding_model_id: str,
    ) -> list[dict[str, object]]:
        """Creates retrieved-context records for every RAG row in the queue."""
        chunk_records_by_filing_id: dict[str, list[dict[str, object]]] = defaultdict(list)
        for chunk_record in chunk_records:
            chunk_records_by_filing_id[str(chunk_record.get("filing_id", ""))].append(chunk_record)

        rag_context_records: list[dict[str, object]] = []
        for filing_id, filing_chunk_records in chunk_records_by_filing_id.items():
            vector_store: VectorStoreInterface = self.vector_store_factory()
            chunk_texts = [str(chunk_record["text"]) for chunk_record in filing_chunk_records]
            chunk_embeddings = self.embedding_client.embed_texts(chunk_texts)
            vector_store.add_vectors(
                [
                    {**chunk_record, "embedding": chunk_embedding}
                    for chunk_record, chunk_embedding in zip(filing_chunk_records, chunk_embeddings)
                ]
            )
            rag_rows_for_filing = [
                queue_record
                for queue_record in queue_records
                if queue_record.get("condition") == "RAG" and queue_record.get("filing_id") == filing_id
            ]
            claim_embeddings = self.embedding_client.embed_texts([row.get("claim_text", "") for row in rag_rows_for_filing])
            for queue_record, claim_embedding in zip(rag_rows_for_filing, claim_embeddings):
                retrieved_chunks = []
                for rank_index, retrieved_record in enumerate(vector_store.search(claim_embedding, top_k), start=1):
                    retrieved_chunks.append({"rank": rank_index, **retrieved_record})
                rag_context_records.append(
                    {
                        "run_id": queue_record.get("run_id"),
                        "case_id": queue_record.get("case_id"),
                        "filing_id": filing_id,
                        "top_k": top_k,
                        "embedding_model": embedding_model_id,
                        "retrieved_chunks": retrieved_chunks,
                    }
                )
        return sorted(rag_context_records, key=lambda record: str(record.get("run_id", "")))

    def write_context_records(self, output_jsonl_path: Path, rag_context_records: list[dict[str, object]]) -> None:
        """Writes retrieved contexts as locked JSONL evidence for the RAG condition."""
        write_jsonl_records(output_jsonl_path, rag_context_records)
