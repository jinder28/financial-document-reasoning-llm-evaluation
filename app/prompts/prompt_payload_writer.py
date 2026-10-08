"""Prompt payload writing freezes model-facing inputs before live execution."""
from __future__ import annotations

import json
from pathlib import Path

from app.common.csv_table import write_csv_records
from app.common.file_hashing import calculate_text_sha256
from app.common.jsonl_table import write_jsonl_records


class PromptPayloadWriter:
    """Writes prompt payload JSONL and hashes for dissertation audit evidence."""

    def build_model_request_payload(
        self,
        run_id: str,
        case_id: str,
        condition: str,
        system_instruction: str,
        user_prompt: str,
    ) -> dict:
        """Builds the provider-neutral request payload for one queue row."""
        return {
            "run_id": run_id,
            "case_id": case_id,
            "condition": condition,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
        }

    def write_payloads_and_hashes(
        self,
        output_directory: Path,
        model_request_payloads: list[dict],
    ) -> dict[str, Path]:
        """Persists full request payloads and prompt hashes for all selected rows."""
        output_directory.mkdir(parents=True, exist_ok=True)
        payload_jsonl_path = output_directory / "full_model_request_payloads.jsonl"
        prompt_hashes_csv_path = output_directory / "prompt_hashes.csv"
        prompt_size_summary_csv_path = output_directory / "prompt_size_summary.csv"

        write_jsonl_records(payload_jsonl_path, model_request_payloads)

        hash_records = []
        size_records = []
        for model_request_payload in model_request_payloads:
            serialized_payload = json.dumps(model_request_payload, ensure_ascii=False, sort_keys=True)
            user_prompt = model_request_payload["messages"][1]["content"]
            hash_records.append(
                {
                    "run_id": model_request_payload["run_id"],
                    "case_id": model_request_payload["case_id"],
                    "condition": model_request_payload["condition"],
                    "payload_sha256": calculate_text_sha256(serialized_payload),
                    "user_prompt_sha256": calculate_text_sha256(user_prompt),
                }
            )
            size_records.append(
                {
                    "run_id": model_request_payload["run_id"],
                    "case_id": model_request_payload["case_id"],
                    "condition": model_request_payload["condition"],
                    "payload_characters": len(serialized_payload),
                    "user_prompt_characters": len(user_prompt),
                    "approximate_user_prompt_words": len(user_prompt.split()),
                }
            )

        write_csv_records(
            prompt_hashes_csv_path,
            hash_records,
            ["run_id", "case_id", "condition", "payload_sha256", "user_prompt_sha256"],
        )
        write_csv_records(
            prompt_size_summary_csv_path,
            size_records,
            ["run_id", "case_id", "condition", "payload_characters", "user_prompt_characters", "approximate_user_prompt_words"],
        )
        return {
            "payload_jsonl_path": payload_jsonl_path,
            "prompt_hashes_csv_path": prompt_hashes_csv_path,
            "prompt_size_summary_csv_path": prompt_size_summary_csv_path,
        }
