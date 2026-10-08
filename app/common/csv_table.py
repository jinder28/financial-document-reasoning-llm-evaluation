"""CSV helpers keep dissertation input tables explicit and auditable."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def read_csv_records(csv_file_path: Path) -> list[dict[str, str]]:
    """Loads a CSV file as named records for queue, claim, or scoring artefacts."""
    with csv_file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv_records(csv_file_path: Path, records: Iterable[dict[str, object]], field_names: list[str]) -> None:
    """Writes evidence tables with stable headers for Appendix E reuse."""
    csv_file_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_file_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        for record in records:
            writer.writerow({field_name: record.get(field_name, "") for field_name in field_names})
