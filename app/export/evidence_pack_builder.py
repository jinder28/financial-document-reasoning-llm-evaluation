"""Evidence pack builder creates a portable archive after export is complete."""
from __future__ import annotations

from pathlib import Path
import zipfile


class EvidencePackBuilder:
    """Compresses Appendix E evidence for dissertation storage and submission work."""

    def build_zip_pack(self, source_directory: Path, output_zip_path: Path) -> Path:
        """Creates a zip archive from the selected evidence directory."""
        output_zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for source_file_path in sorted(source_directory.rglob("*")):
                if source_file_path.is_file():
                    zip_file.write(source_file_path, source_file_path.relative_to(source_directory.parent))
        return output_zip_path
