"""Local file storage is the dissertation default artefact repository."""
from __future__ import annotations

from pathlib import Path

from app.storage.artifact_repository_interface import ArtifactRepositoryInterface


class LocalFileArtifactRepository(ArtifactRepositoryInterface):
    """Stores experiment inputs and evidence in mounted local directories."""

    def __init__(self, repository_root_directory: Path) -> None:
        self.repository_root_directory = repository_root_directory

    def _resolve_artifact_path(self, relative_artifact_path: str) -> Path:
        """Resolves a repository-relative path without leaking filesystem logic."""
        return self.repository_root_directory / relative_artifact_path

    def read_text(self, relative_artifact_path: str) -> str:
        """Reads a text artefact from the mounted local repository."""
        return self._resolve_artifact_path(relative_artifact_path).read_text(encoding="utf-8")

    def write_text(self, relative_artifact_path: str, text_value: str) -> Path:
        """Writes dissertation evidence into the mounted output repository."""
        artifact_path = self._resolve_artifact_path(relative_artifact_path)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(text_value, encoding="utf-8")
        return artifact_path

    def exists(self, relative_artifact_path: str) -> bool:
        """Checks local artefact existence through the repository abstraction."""
        return self._resolve_artifact_path(relative_artifact_path).exists()
