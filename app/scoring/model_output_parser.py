"""Output parser normalizes saved model JSON for scoring and reporting."""
from __future__ import annotations

from pathlib import Path

from app.common.jsonl_table import read_jsonl_records


class ModelOutputParser:
    """Loads parsed model outputs created by smoke-live or full-live execution."""

    def load_prediction_records(self, parsed_output_jsonl_path: Path) -> list[dict[str, str]]:
        """Extracts case ID, condition, and predicted label from parsed outputs."""
        prediction_records: list[dict[str, str]] = []
        for output_record in read_jsonl_records(parsed_output_jsonl_path):
            parsed_output = output_record.get("parsed_output", {})
            prediction_records.append(
                {
                    "run_id": output_record.get("run_id", ""),
                    "case_id": parsed_output.get("case_id") or output_record.get("case_id", ""),
                    "condition": output_record.get("condition", ""),
                    "predicted_label": parsed_output.get("predicted_label", ""),
                    "confidence": parsed_output.get("confidence", ""),
                    "reasoning_summary": parsed_output.get("reasoning_summary", ""),
                }
            )
        return prediction_records
