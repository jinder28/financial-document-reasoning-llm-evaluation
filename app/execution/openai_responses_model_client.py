"""OpenAI Responses API implementation for GPT-5.5 classification calls."""
from __future__ import annotations

import json
import time

from app.config.runtime_settings import ExperimentRuntimeSettings
from app.execution.model_client_interface import ModelClientInterface


class OpenAIResponsesModelClient(ModelClientInterface):
    """Executes one structured-output claim-classification request."""

    def __init__(self, runtime_settings: ExperimentRuntimeSettings) -> None:
        from openai import OpenAI

        self.runtime_settings = runtime_settings
        self.openai_client = OpenAI()

    def classify_claim(self, model_request_payload: dict, output_json_schema: dict) -> dict:
        """Calls GPT-5.5 and returns raw, parsed, usage, and timing evidence."""
        started_at = time.time()
        response = self.openai_client.responses.create(
            model=self.runtime_settings.openai_model_id,
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": model_request_payload["messages"][0]["content"]}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": model_request_payload["messages"][1]["content"]}
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "sec10k_claim_classification_schema_v1_0_final",
                    "schema": output_json_schema,
                    "strict": True,
                }
            },
            reasoning={"effort": self.runtime_settings.openai_reasoning_effort},
            max_output_tokens=self.runtime_settings.openai_max_output_tokens,
        )
        elapsed_seconds = time.time() - started_at
        raw_response = response.model_dump() if hasattr(response, "model_dump") else dict(response)
        output_text = getattr(response, "output_text", "") or self._extract_output_text(raw_response)
        parsed_output = json.loads(output_text) if output_text else {}
        return {
            "raw_response": raw_response,
            "parsed_output": parsed_output,
            "usage": raw_response.get("usage", {}),
            "elapsed_seconds": elapsed_seconds,
        }

    def _extract_output_text(self, raw_response: dict) -> str:
        """Extracts text from response structures when SDK convenience text is absent."""
        collected_text_parts: list[str] = []
        for output_item in raw_response.get("output", []) or []:
            for content_item in output_item.get("content", []) or []:
                text_value = content_item.get("text") or content_item.get("output_text")
                if text_value:
                    collected_text_parts.append(text_value)
        return "".join(collected_text_parts)
