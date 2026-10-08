"""Download manifest records which SEC filings are used for corpus preparation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.common.csv_table import read_csv_records


@dataclass(frozen=True)
class FilingDownloadRequest:
    """Represents one SEC filing source URL for optional reproducibility fetching."""

    filing_id: str
    company: str
    accession_number: str
    source_url: str
    target_file_name: str


class FilingDownloadManifest:
    """Loads optional SEC source acquisition instructions from a CSV manifest."""

    def load_download_requests(self, manifest_csv_path: Path) -> list[FilingDownloadRequest]:
        """Reads filing source URLs without changing the locked experiment corpus."""
        return [
            FilingDownloadRequest(
                filing_id=record.get("filing_id", ""),
                company=record.get("company", ""),
                accession_number=record.get("accession_number", ""),
                source_url=record.get("source_url", ""),
                target_file_name=record.get("target_file_name", ""),
            )
            for record in read_csv_records(manifest_csv_path)
        ]
