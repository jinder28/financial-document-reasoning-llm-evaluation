"""Queue loading controls which locked claim-condition rows are executed."""
from __future__ import annotations

from pathlib import Path

from app.common.csv_table import read_csv_records


class ExperimentQueueLoader:
    """Loads and filters the locked 96-row main-run execution queue."""

    def load_queue_records(self, queue_csv_path: Path) -> list[dict[str, str]]:
        """Loads all queued LC/RAG runs from the locked execution queue."""
        return read_csv_records(queue_csv_path)

    def select_queue_records(
        self,
        queue_records: list[dict[str, str]],
        requested_run_id: str | None = None,
        maximum_records: int | None = None,
    ) -> list[dict[str, str]]:
        """Selects all rows, one run ID, or a limited prefix for controlled gates."""
        selected_queue_records = queue_records
        if requested_run_id:
            selected_queue_records = [record for record in selected_queue_records if record.get("run_id") == requested_run_id]
        if maximum_records is not None:
            selected_queue_records = selected_queue_records[:maximum_records]
        return selected_queue_records
