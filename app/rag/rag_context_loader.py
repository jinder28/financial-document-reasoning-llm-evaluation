"""RAG context loading uses frozen retrieved chunks for the RAG condition."""
from __future__ import annotations

from pathlib import Path

from app.common.jsonl_table import read_jsonl_records


class RagContextLoader:
    """Loads prebuilt top-k retrieved contexts without exposing the scoring key."""

    def load_context_records_by_run_id(self, rag_contexts_jsonl_path: Path) -> dict[str, dict]:
        """Indexes frozen RAG context records by run ID for prompt assembly."""
        context_records_by_run_id: dict[str, dict] = {}
        for context_record in read_jsonl_records(rag_contexts_jsonl_path):
            run_id = context_record.get("run_id")
            if run_id:
                context_records_by_run_id[run_id] = context_record
        return context_records_by_run_id

    def build_context_text_for_run(self, context_record: dict) -> str:
        """Formats retrieved chunks as model-facing evidence for one RAG prompt."""
        retrieved_chunks = context_record.get("retrieved_chunks", [])
        formatted_chunks: list[str] = []
        for retrieved_chunk in retrieved_chunks:
            rank = retrieved_chunk.get("rank", "")
            chunk_id = retrieved_chunk.get("chunk_id", "")
            score = retrieved_chunk.get("score", "")
            chunk_text = retrieved_chunk.get("text", "")
            formatted_chunks.append(f"[Retrieved chunk rank={rank} chunk_id={chunk_id} score={score}]\n{chunk_text}")
        return "\n\n".join(formatted_chunks)
