"""JSONL helpers preserve model payloads and outputs as appendable evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def read_jsonl_records(jsonl_file_path: Path) -> list[dict]:
    """Loads JSONL evidence records while ignoring empty lines."""
    records: list[dict] = []
    if not jsonl_file_path.exists():
        return records
    with jsonl_file_path.open("r", encoding="utf-8") as jsonl_file:
        for line_number, line_text in enumerate(jsonl_file, start=1):
            stripped_line_text = line_text.strip()
            if not stripped_line_text:
                continue
            try:
                records.append(json.loads(stripped_line_text))
            except json.JSONDecodeError as json_error:
                raise ValueError(f"Invalid JSONL at {jsonl_file_path}:{line_number}: {json_error}") from json_error
    return records


def write_jsonl_records(jsonl_file_path: Path, records: Iterable[dict]) -> None:
    """Writes one JSON object per line for reproducible prompt/output capture."""
    jsonl_file_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_file_path.open("w", encoding="utf-8") as jsonl_file:
        for record in records:
            jsonl_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def append_jsonl_record(jsonl_file_path: Path, record: dict) -> None:
    """Appends one live-run record without rewriting prior experiment evidence."""
    jsonl_file_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_file_path.open("a", encoding="utf-8") as jsonl_file:
        jsonl_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
