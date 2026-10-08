"""Leakage checks protect the hidden scoring key from model-facing prompts."""
from __future__ import annotations


class AnswerKeyLeakageChecker:
    """Prevents ground-truth labels and rationales from entering model payloads."""

    forbidden_scoring_field_names = {
        "expected_label",
        "ground_truth_rationale",
        "scoring_key",
        "hidden_label",
        "expected_label_hidden_from_prompt",
        "filing_reference_anchors",
    }

    def assert_model_payload_contains_no_scoring_fields(self, model_request_payload: dict) -> None:
        """Stops execution if a request payload contains answer-key field names."""
        matched_forbidden_names: list[str] = []
        self._collect_forbidden_field_names(model_request_payload, matched_forbidden_names)
        if matched_forbidden_names:
            raise ValueError(f"Answer-key leakage risk detected: {sorted(set(matched_forbidden_names))}")

    def assert_queue_contains_no_hidden_expected_labels(self, queue_records: list[dict[str, str]]) -> None:
        """Confirms the execution queue does not contain hidden ground-truth labels."""
        for queue_record in queue_records:
            if "expected_label" in queue_record:
                raise ValueError("Execution queue contains expected_label field.")
            if queue_record.get("expected_label_visible_to_model") not in {"NO", "No", "no", ""}:
                raise ValueError(f"Expected label visibility is not safely marked NO for {queue_record.get('run_id')}")

    def _collect_forbidden_field_names(self, payload_value, matched_forbidden_names: list[str]) -> None:
        """Recursively scans payload keys for forbidden answer-key fields."""
        if isinstance(payload_value, dict):
            for payload_key, nested_payload_value in payload_value.items():
                if payload_key in self.forbidden_scoring_field_names:
                    matched_forbidden_names.append(payload_key)
                self._collect_forbidden_field_names(nested_payload_value, matched_forbidden_names)
        elif isinstance(payload_value, list):
            for nested_payload_value in payload_value:
                self._collect_forbidden_field_names(nested_payload_value, matched_forbidden_names)
