"""Telemetry logging records latency, usage, status, and cost per run row."""
from __future__ import annotations

from pathlib import Path

from app.common.csv_table import write_csv_records


class TelemetryLogger:
    """Collects run telemetry for Appendix E cost and latency analysis."""

    telemetry_field_names = [
        "run_id",
        "case_id",
        "condition",
        "status",
        "elapsed_seconds",
        "input_tokens",
        "output_tokens",
        "estimated_call_cost_usd",
        "retry_attempts_used",
        "error_message",
    ]

    def __init__(self) -> None:
        self.telemetry_records: list[dict[str, object]] = []

    def add_record(self, telemetry_record: dict[str, object]) -> None:
        """Adds one queue-row telemetry record to the in-memory buffer."""
        self.telemetry_records.append(telemetry_record)

    def write_csv(self, telemetry_csv_path: Path) -> None:
        """Writes telemetry evidence for dry-run, smoke-live, or full-live stages."""
        write_csv_records(telemetry_csv_path, self.telemetry_records, self.telemetry_field_names)
