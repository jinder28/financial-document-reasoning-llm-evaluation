"""Model client abstraction keeps the experiment independent of one LLM vendor."""
from __future__ import annotations

from typing import Protocol


class ModelClientInterface(Protocol):
    """Defines the model-call behaviour needed by smoke and full execution."""

    def classify_claim(self, model_request_payload: dict, output_json_schema: dict) -> dict:
        """Classifies one claim using a provider-specific model implementation."""
        raise NotImplementedError
