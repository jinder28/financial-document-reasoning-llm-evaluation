"""Builds a portable release zip for the containerized dissertation apparatus."""
from __future__ import annotations

from pathlib import Path
import zipfile


def main() -> int:
    """Creates the apparatus zip while excluding generated outputs and secrets."""
    app_root = Path(__file__).resolve().parents[1]
    output_zip_path = app_root.parent / "main_run_container_app_v1.zip"
    excluded_names = {".env", "__pycache__", ".pytest_cache"}
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in sorted(app_root.rglob("*")):
            if file_path.is_dir():
                continue
            if any(part in excluded_names for part in file_path.parts):
                continue
            relative_path = file_path.relative_to(app_root.parent)
            zip_file.write(file_path, relative_path)
    print(output_zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
