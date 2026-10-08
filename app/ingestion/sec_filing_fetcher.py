"""SEC filing fetcher supports reproducible source acquisition when enabled."""
from __future__ import annotations

from pathlib import Path
import requests

from app.config.runtime_settings import ExperimentRuntimeSettings
from app.ingestion.filing_download_manifest import FilingDownloadManifest


class SecFilingFetcher:
    """Downloads source SEC filing files from an explicit manifest of URLs."""

    def __init__(self, runtime_settings: ExperimentRuntimeSettings) -> None:
        self.runtime_settings = runtime_settings
        self.download_manifest = FilingDownloadManifest()

    def fetch_filings_from_manifest(self, manifest_csv_path: Path, output_directory: Path) -> dict:
        """Fetches filings only when the feature toggle permits acquisition."""
        if not self.runtime_settings.feature_toggles.enable_sec_fetch:
            raise RuntimeError("ENABLE_SEC_FETCH must be true to fetch SEC filings.")
        output_directory.mkdir(parents=True, exist_ok=True)
        downloaded_files: list[str] = []
        for download_request in self.download_manifest.load_download_requests(manifest_csv_path):
            response = requests.get(
                download_request.source_url,
                headers={"User-Agent": "academic-dissertation-contact@example.com"},
                timeout=60,
            )
            response.raise_for_status()
            target_file_path = output_directory / download_request.target_file_name
            target_file_path.write_bytes(response.content)
            downloaded_files.append(str(target_file_path))
        return {"status": "PASS", "downloaded_files": downloaded_files}
