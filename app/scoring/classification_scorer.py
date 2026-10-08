"""Classification scoring compares predictions with the hidden answer key."""
from __future__ import annotations

from pathlib import Path

from app.common.csv_table import write_csv_records
from app.scoring.metric_calculator import MetricCalculator
from app.scoring.model_output_parser import ModelOutputParser
from app.scoring.scoring_key_repository import ScoringKeyRepository


class ClassificationScorer:
    """Scores LC and RAG predictions only after live outputs have been captured."""

    def __init__(self) -> None:
        self.model_output_parser = ModelOutputParser()
        self.scoring_key_repository = ScoringKeyRepository()
        self.metric_calculator = MetricCalculator()

    def score_predictions(
        self,
        parsed_output_jsonl_path: Path,
        scoring_key_csv_path: Path,
        output_directory: Path,
    ) -> dict:
        """Writes scored outputs, condition metrics, and confusion matrices."""
        prediction_records = self.model_output_parser.load_prediction_records(parsed_output_jsonl_path)
        scoring_records_by_case_id = self.scoring_key_repository.load_scoring_records_by_case_id(scoring_key_csv_path)
        scored_prediction_records: list[dict[str, str]] = []
        for prediction_record in prediction_records:
            scoring_record = scoring_records_by_case_id.get(prediction_record["case_id"], {})
            expected_label = scoring_record.get("expected_label", "")
            scored_prediction_records.append(
                {
                    **prediction_record,
                    "expected_label": expected_label,
                    "case_type": scoring_record.get("case_type", ""),
                    "is_correct": "YES" if prediction_record["predicted_label"] == expected_label else "NO",
                }
            )
        condition_metrics = self.metric_calculator.calculate_condition_metrics(scored_prediction_records)
        confusion_matrix_records = self.metric_calculator.calculate_confusion_matrix_records(scored_prediction_records)
        output_directory.mkdir(parents=True, exist_ok=True)
        write_csv_records(
            output_directory / "scored_predictions.csv",
            scored_prediction_records,
            [
                "run_id",
                "case_id",
                "condition",
                "predicted_label",
                "expected_label",
                "is_correct",
                "confidence",
                "case_type",
                "reasoning_summary",
            ],
        )
        write_csv_records(
            output_directory / "condition_metrics.csv",
            condition_metrics,
            ["condition", "correct_count", "total_count", "accuracy"],
        )
        write_csv_records(
            output_directory / "confusion_matrix.csv",
            confusion_matrix_records,
            ["condition", "expected_label", "predicted_label", "count"],
        )
        return {
            "status": "PASS",
            "prediction_count": len(prediction_records),
            "scored_prediction_count": len(scored_prediction_records),
        }
