"""Corpus lock validator prevents silent replacement of locked filing inputs."""
from __future__ import annotations

from pathlib import Path


class CorpusLockValidator:
    """Checks that clean-text source files match queue-declared file names."""

    def assert_locked_source_files_present(self, source_file_names: set[str], clean_text_directory: Path) -> None:
        """Stops preparation when a locked source file is missing."""
        missing_source_files = sorted(source_file_name for source_file_name in source_file_names if not (clean_text_directory / source_file_name).exists())
        if missing_source_files:
            raise FileNotFoundError(f"Missing locked clean text files: {missing_source_files}")
