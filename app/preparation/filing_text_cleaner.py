"""Text cleaner prepares SEC filing text for section and prompt processing."""
from __future__ import annotations

import re
from pathlib import Path
from bs4 import BeautifulSoup

from app.config.runtime_settings import ExperimentRuntimeSettings


class FilingTextCleaner:
    """Converts raw filing HTML/TXT into normalized clean text files."""

    def __init__(self, runtime_settings: ExperimentRuntimeSettings) -> None:
        self.runtime_settings = runtime_settings

    def clean_source_directory(self, source_directory: Path, output_directory: Path) -> dict:
        """Cleans source files only when the cleaning toggle is enabled."""
        if not self.runtime_settings.feature_toggles.enable_text_cleaning:
            raise RuntimeError("ENABLE_TEXT_CLEANING must be true to clean filings.")
        output_directory.mkdir(parents=True, exist_ok=True)
        cleaned_files: list[str] = []
        for source_file_path in sorted(source_directory.glob("*")):
            if not source_file_path.is_file():
                continue
            raw_text = source_file_path.read_text(encoding="utf-8", errors="replace")
            clean_text = self.clean_filing_text(raw_text)
            target_file_path = output_directory / f"{source_file_path.stem}.txt"
            target_file_path.write_text(clean_text, encoding="utf-8")
            cleaned_files.append(str(target_file_path))
        return {"status": "PASS", "cleaned_files": cleaned_files}

    def clean_filing_text(self, raw_text: str) -> str:
        """Removes markup and normalizes whitespace for downstream evidence use."""
        if "<" in raw_text and ">" in raw_text:
            raw_text = BeautifulSoup(raw_text, "html.parser").get_text(" ")
        normalized_text = re.sub(r"\s+", " ", raw_text)
        return normalized_text.strip()
