from pathlib import Path

from app.rag.filing_chunker import FilingChunker


def test_filing_chunker_creates_overlapping_chunks(tmp_path: Path):
    clean_text_file_path = tmp_path / "F001_test.txt"
    clean_text_file_path.write_text(" ".join(f"word{i}" for i in range(20)), encoding="utf-8")
    chunk_records = FilingChunker().build_chunk_records_for_clean_texts(tmp_path, chunk_word_count=10, overlap_word_count=2)
    assert len(chunk_records) == 3
    assert chunk_records[0]["word_start"] == 0
    assert chunk_records[1]["word_start"] == 8
