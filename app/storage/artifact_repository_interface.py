"""Artefact repository abstraction keeps the apparatus datastore ignorant."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ArtifactRepositoryInterface(Protocol):
    """Defines storage operations needed by validation, execution, and export."""

    def read_text(self, relative_artifact_path: str) -> str:
        """Reads a text artefact from the configured backing store."""
        raise NotImplementedError

    def write_text(self, relative_artifact_path: str, text_value: str) -> Path:
        """Writes a text artefact and returns its resolved path."""
        raise NotImplementedError

    def exists(self, relative_artifact_path: str) -> bool:
        """Checks whether an artefact exists without exposing storage details."""
        raise NotImplementedError
