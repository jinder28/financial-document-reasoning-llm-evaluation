"""Hashing records which frozen artefacts produced the dissertation evidence."""
from __future__ import annotations

import hashlib
from pathlib import Path


def calculate_file_sha256(file_path: Path) -> str:
    """Calculates a SHA256 digest for a locked input or output artefact."""
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as binary_file:
        for file_chunk in iter(lambda: binary_file.read(1024 * 1024), b""):
            sha256_hash.update(file_chunk)
    return sha256_hash.hexdigest()


def calculate_text_sha256(text_value: str) -> str:
    """Calculates a prompt hash without storing hidden execution state elsewhere."""
    return hashlib.sha256(text_value.encode("utf-8")).hexdigest()


def build_hash_manifest(named_file_paths: dict[str, Path]) -> list[dict[str, str]]:
    """Builds the artefact hash manifest used as a run-readiness control."""
    hash_records: list[dict[str, str]] = []
    for artefact_name, file_path in sorted(named_file_paths.items()):
        hash_records.append(
            {
                "artefact_name": artefact_name,
                "path": str(file_path),
                "exists": str(file_path.exists()),
                "sha256": calculate_file_sha256(file_path) if file_path.exists() and file_path.is_file() else "",
            }
        )
    return hash_records
