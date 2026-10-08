"""Run controller executes dry-run, smoke-live, and full-live experiment stages."""
from __future__ import annotations

from pathlib import Path

from app.common.jsonl_table import append_jsonl_record, write_jsonl_records
from app.config.runtime_settings import ExperimentRuntimeSettings
from app.execution.cost_guard import CostGuard
from app.execution.model_client_interface import ModelClientInterface
from app.execution.retry_policy import RetryPolicy
from app.execution.telemetry_logger import TelemetryLogger
from app.prompts.long_context_prompt_assembler import LongContextPromptAssembler
from app.prompts.output_schema_registry import OutputSchemaRegistry
from app.prompts.prompt_payload_writer import PromptPayloadWriter
from app.prompts.prompt_template_registry import PromptTemplateRegistry
from app.prompts.rag_prompt_assembler import RagPromptAssembler
from app.rag.rag_context_loader import RagContextLoader
from app.validation.answer_key_leakage_checker import AnswerKeyLeakageChecker


class ExperimentRunController:
    """Coordinates prompt assembly, leakage checking, live calls, and evidence capture."""

    def __init__(
        self,
        runtime_settings: ExperimentRuntimeSettings,
        model_client: ModelClientInterface | None,
    ) -> None:
        self.runtime_settings = runtime_settings
        self.model_client = model_client
        self.prompt_template_registry = PromptTemplateRegistry()
        self.rag_context_loader = RagContextLoader()
        self.long_context_prompt_assembler = LongContextPromptAssembler(self.prompt_template_registry)
        self.rag_prompt_assembler = RagPromptAssembler(self.prompt_template_registry, self.rag_context_loader)
        self.output_schema_registry = OutputSchemaRegistry()
        self.prompt_payload_writer = PromptPayloadWriter()
        self.leakage_checker = AnswerKeyLeakageChecker()
        self.cost_guard = CostGuard(runtime_settings)
        self.retry_policy = RetryPolicy(runtime_settings.max_retry_attempts)

    def run_prompt_dry_run(self, queue_records: list[dict[str, str]], output_directory: Path) -> dict:
        """Builds payloads for selected rows without performing model calls."""
        model_request_payloads = self._build_model_request_payloads(queue_records)
        for model_request_payload in model_request_payloads:
            self.leakage_checker.assert_model_payload_contains_no_scoring_fields(model_request_payload)
        written_paths = self.prompt_payload_writer.write_payloads_and_hashes(output_directory, model_request_payloads)
        telemetry_logger = TelemetryLogger()
        for model_request_payload in model_request_payloads:
            user_prompt = model_request_payload["messages"][1]["content"]
            telemetry_logger.add_record(
                {
                    "run_id": model_request_payload["run_id"],
                    "case_id": model_request_payload["case_id"],
                    "condition": model_request_payload["condition"],
                    "status": "DRY_RUN_PAYLOAD_BUILT",
                    "elapsed_seconds": "0",
                    "input_tokens": "",
                    "output_tokens": "",
                    "estimated_call_cost_usd": "0",
                    "retry_attempts_used": "0",
                    "error_message": f"user_prompt_characters={len(user_prompt)}",
                }
            )
        telemetry_logger.write_csv(output_directory / "main_run_telemetry.csv")
        return {"status": "PASS", "payload_count": len(model_request_payloads), "written_paths": {k: str(v) for k, v in written_paths.items()}}

    def run_live_execution(self, queue_records: list[dict[str, str]], output_directory: Path) -> dict:
        """Runs live model calls for smoke or full execution after safety gates pass."""
        if not self.runtime_settings.feature_toggles.enable_live_model_calls:
            raise RuntimeError("ENABLE_LIVE_MODEL_CALLS must be true for smoke-live or full-live execution.")
        if self.model_client is None:
            raise RuntimeError("A model client is required for live execution.")

        output_directory.mkdir(parents=True, exist_ok=True)
        raw_output_jsonl_path = output_directory / "raw_model_outputs.jsonl"
        parsed_output_jsonl_path = output_directory / "parsed_model_outputs.jsonl"
        telemetry_logger = TelemetryLogger()
        output_json_schema = self.output_schema_registry.get_claim_classification_schema()
        model_request_payloads = self._build_model_request_payloads(queue_records)
        self.prompt_payload_writer.write_payloads_and_hashes(output_directory / "request_payloads", model_request_payloads)

        for model_request_payload in model_request_payloads:
            self.leakage_checker.assert_model_payload_contains_no_scoring_fields(model_request_payload)
            try:
                model_result = self.retry_policy.execute_with_retries(
                    model_request_payload["run_id"],
                    lambda payload=model_request_payload: self.model_client.classify_claim(payload, output_json_schema),
                )
                usage_record = model_result.get("usage", {})
                estimated_call_cost_usd = self.cost_guard.record_usage_and_assert_within_limits(usage_record)
                append_jsonl_record(
                    raw_output_jsonl_path,
                    {
                        "run_id": model_request_payload["run_id"],
                        "case_id": model_request_payload["case_id"],
                        "condition": model_request_payload["condition"],
                        "raw_response": model_result.get("raw_response", {}),
                    },
                )
                parsed_output = model_result.get("parsed_output", {})
                append_jsonl_record(
                    parsed_output_jsonl_path,
                    {
                        "run_id": model_request_payload["run_id"],
                        "case_id": model_request_payload["case_id"],
                        "condition": model_request_payload["condition"],
                        "parsed_output": parsed_output,
                    },
                )
                telemetry_logger.add_record(
                    {
                        "run_id": model_request_payload["run_id"],
                        "case_id": model_request_payload["case_id"],
                        "condition": model_request_payload["condition"],
                        "status": "LIVE_CALL_COMPLETED",
                        "elapsed_seconds": model_result.get("elapsed_seconds", ""),
                        "input_tokens": usage_record.get("input_tokens") or usage_record.get("prompt_tokens") or "",
                        "output_tokens": usage_record.get("output_tokens") or usage_record.get("completion_tokens") or "",
                        "estimated_call_cost_usd": f"{estimated_call_cost_usd:.6f}",
                        "retry_attempts_used": model_result.get("retry_attempts_used", 0),
                        "error_message": "",
                    }
                )
            except Exception as execution_error:  # noqa: BLE001 - stored as run evidence.
                telemetry_logger.add_record(
                    {
                        "run_id": model_request_payload["run_id"],
                        "case_id": model_request_payload["case_id"],
                        "condition": model_request_payload["condition"],
                        "status": "LIVE_CALL_FAILED",
                        "elapsed_seconds": "",
                        "input_tokens": "",
                        "output_tokens": "",
                        "estimated_call_cost_usd": "",
                        "retry_attempts_used": "",
                        "error_message": str(execution_error),
                    }
                )
                raise
        telemetry_logger.write_csv(output_directory / "main_run_telemetry.csv")
        return {"status": "PASS", "executed_rows": len(model_request_payloads), "output_directory": str(output_directory)}

    def _build_model_request_payloads(self, queue_records: list[dict[str, str]]) -> list[dict]:
        """Builds provider-neutral model request payloads for LC and RAG rows."""
        rag_contexts_by_run_id = self.rag_context_loader.load_context_records_by_run_id(
            self.runtime_settings.rag_contexts_jsonl_path
        )
        system_instruction = self.prompt_template_registry.get_system_instruction()
        model_request_payloads: list[dict] = []
        for queue_record in queue_records:
            condition = queue_record.get("condition", "")
            if condition == "Long_Context":
                user_prompt = self.long_context_prompt_assembler.assemble_user_prompt(
                    queue_record, self.runtime_settings.clean_text_directory
                )
            elif condition == "RAG":
                context_record = rag_contexts_by_run_id.get(queue_record.get("run_id", ""))
                if context_record is None:
                    raise ValueError(f"Missing RAG context for {queue_record.get('run_id')}")
                user_prompt = self.rag_prompt_assembler.assemble_user_prompt(queue_record, context_record)
            else:
                raise ValueError(f"Unknown condition: {condition}")
            model_request_payloads.append(
                self.prompt_payload_writer.build_model_request_payload(
                    run_id=queue_record.get("run_id", ""),
                    case_id=queue_record.get("case_id", ""),
                    condition=condition,
                    system_instruction=system_instruction,
                    user_prompt=user_prompt,
                )
            )
        return model_request_payloads
