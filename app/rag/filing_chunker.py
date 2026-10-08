"""Chunking reproduces the RAG condition's fixed filing segmentation policy."""
from __future__ import annotations

from pathlib import Path

from app.common.jsonl_table import write_jsonl_records


class FilingChunker:
    """Splits clean 10-K filings into overlapping word chunks for retrieval."""

    def build_chunk_records_for_clean_texts(
        self,
        clean_text_directory: Path,
        chunk_word_count: int,
        overlap_word_count: int,
    ) -> list[dict[str, object]]:
        """Creates chunk metadata from every locked clean filing text file."""
        chunk_records: list[dict[str, object]] = []
        step_word_count = max(1, chunk_word_count - overlap_word_count)
        for clean_text_file_path in sorted(clean_text_directory.glob("*.txt")):
            filing_identifier = clean_text_file_path.stem.split("_")[0]
            filing_words = clean_text_file_path.read_text(encoding="utf-8", errors="replace").split()
            chunk_index = 1
            for word_start in range(0, len(filing_words), step_word_count):
                word_end = min(word_start + chunk_word_count, len(filing_words))
                chunk_words = filing_words[word_start:word_end]
                if not chunk_words:
                    continue
                chunk_records.append(
                    {
                        "filing_id": filing_identifier,
                        "source_file": clean_text_file_path.name,
                        "chunk_id": f"{filing_identifier}_CH{chunk_index:04d}",
                        "word_start": word_start,
                        "word_end": word_end,
                        "text": " ".join(chunk_words),
                    }
                )
                chunk_index += 1
                if word_end >= len(filing_words):
                    break
        return chunk_records

    def write_chunk_manifest(self, output_jsonl_path: Path, chunk_records: list[dict[str, object]]) -> None:
        """Writes chunk metadata used to validate RAG preparation evidence."""
        write_jsonl_records(output_jsonl_path, chunk_records)
