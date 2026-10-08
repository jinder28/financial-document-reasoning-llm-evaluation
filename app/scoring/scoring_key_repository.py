"""Scoring key repository isolates hidden labels from model execution code."""
from __future__ import annotations

from pathlib import Path

from app.common.csv_table import read_csv_records


class ScoringKeyRepository:
    """Loads hidden expected labels only during post-run scoring."""

    def load_scoring_records_by_case_id(self, scoring_key_csv_path: Path) -> dict[str, dict[str, str]]:
        """Indexes scoring-key rows by case ID after model outputs are saved."""
        return {record["case_id"]: record for record in read_csv_records(scoring_key_csv_path)}
