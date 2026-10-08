"""Output schemas define the structured evidence expected from GPT-5.5."""
from __future__ import annotations


class OutputSchemaRegistry:
    """Provides the JSON schema used for strict model-output validation."""

    def get_claim_classification_schema(self) -> dict:
        """Returns the SEC 10-K claim-classification schema for both conditions."""
        return {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "case_id",
                "predicted_label",
                "evidence_references",
                "reasoning_summary",
                "confidence",
            ],
            "properties": {
                "case_id": {"type": "string"},
                "predicted_label": {
                    "type": "string",
                    "enum": ["Supported", "Contradicted", "Insufficient Evidence"],
                },
                "evidence_references": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["reference", "evidence_role"],
                        "properties": {
                            "reference": {"type": "string"},
                            "evidence_role": {"type": "string"},
                        },
                    },
                },
                "reasoning_summary": {"type": "string"},
                "confidence": {"type": "string", "enum": ["High", "Medium", "Low"]},
            },
        }
