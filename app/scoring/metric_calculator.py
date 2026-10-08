"""Metric calculation supports LC/RAG comparison after the main experiment."""
from __future__ import annotations

from collections import Counter, defaultdict


class MetricCalculator:
    """Calculates accuracy and label metrics for dissertation results tables."""

    labels = ["Supported", "Contradicted", "Insufficient Evidence"]

    def calculate_condition_metrics(self, scored_prediction_records: list[dict[str, str]]) -> list[dict[str, object]]:
        """Calculates condition-level accuracy for LC and RAG outputs."""
        records_by_condition: dict[str, list[dict[str, str]]] = defaultdict(list)
        for scored_record in scored_prediction_records:
            records_by_condition[scored_record["condition"]].append(scored_record)
        metric_records: list[dict[str, object]] = []
        for condition, condition_records in sorted(records_by_condition.items()):
            correct_count = sum(1 for record in condition_records if record["is_correct"] == "YES")
            total_count = len(condition_records)
            metric_records.append(
                {
                    "condition": condition,
                    "correct_count": correct_count,
                    "total_count": total_count,
                    "accuracy": correct_count / total_count if total_count else 0,
                }
            )
        return metric_records

    def calculate_confusion_matrix_records(self, scored_prediction_records: list[dict[str, str]]) -> list[dict[str, object]]:
        """Builds confusion-matrix records by condition and expected/predicted label."""
        confusion_counter = Counter(
            (
                record["condition"],
                record["expected_label"],
                record["predicted_label"],
            )
            for record in scored_prediction_records
        )
        confusion_records: list[dict[str, object]] = []
        for condition in sorted({record["condition"] for record in scored_prediction_records}):
            for expected_label in self.labels:
                for predicted_label in self.labels:
                    confusion_records.append(
                        {
                            "condition": condition,
                            "expected_label": expected_label,
                            "predicted_label": predicted_label,
                            "count": confusion_counter[(condition, expected_label, predicted_label)],
                        }
                    )
        return confusion_records
