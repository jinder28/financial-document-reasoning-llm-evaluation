"""Runtime settings bind the apparatus to frozen dissertation artefacts."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from app.config.feature_toggles import FeatureToggles


def _environment_path(environment_variable_name: str, default_path: str) -> Path:
    return Path(os.getenv(environment_variable_name, default_path))


def _environment_float(environment_variable_name: str, default_value: float) -> float:
    return float(os.getenv(environment_variable_name, str(default_value)))


def _environment_integer(environment_variable_name: str, default_value: int) -> int:
    return int(os.getenv(environment_variable_name, str(default_value)))


@dataclass(frozen=True)
class ExperimentRuntimeSettings:
    """Central configuration for validating and executing the dissertation experiment."""

    model_provider: str
    openai_model_id: str
    openai_embedding_model_id: str
    openai_reasoning_effort: str
    openai_max_output_tokens: int
    openai_temperature: float
    queue_csv_path: Path
    scoring_key_csv_path: Path
    claim_manifest_csv_path: Path
    run_manifest_json_path: Path
    clean_text_directory: Path
    rag_contexts_jsonl_path: Path
    output_directory: Path
    experiment_run_id: str
    cost_warning_usd: float
    cost_hard_limit_usd: float
    input_cost_usd_per_million_tokens: float
    output_cost_usd_per_million_tokens: float
    max_retry_attempts: int
    rag_top_k: int
    rag_chunk_word_count: int
    rag_chunk_overlap_word_count: int
    feature_toggles: FeatureToggles

    @staticmethod
    def from_environment() -> "ExperimentRuntimeSettings":
        """Creates settings from environment variables and default container paths."""
        return ExperimentRuntimeSettings(
            model_provider=os.getenv("MODEL_PROVIDER", "openai"),
            openai_model_id=os.getenv("OPENAI_MODEL_ID", "gpt-5.5"),
            openai_embedding_model_id=os.getenv("OPENAI_EMBEDDING_MODEL_ID", "text-embedding-3-large"),
            openai_reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "medium"),
            openai_max_output_tokens=_environment_integer("OPENAI_MAX_OUTPUT_TOKENS", 1500),
            openai_temperature=_environment_float("OPENAI_TEMPERATURE", 0.0),
            queue_csv_path=_environment_path("QUEUE_CSV_PATH", "/workspace/inputs/queue/api_execution_queue_locked_v1_amendment001.csv"),
            scoring_key_csv_path=_environment_path("SCORING_KEY_CSV_PATH", "/workspace/inputs/scoring/scoring_key_locked_v1_amendment001.csv"),
            claim_manifest_csv_path=_environment_path("CLAIM_MANIFEST_CSV_PATH", "/workspace/inputs/claims/claim_case_manifest_v1_locked_amendment001.csv"),
            run_manifest_json_path=_environment_path("RUN_MANIFEST_JSON_PATH", "/workspace/inputs/manifests/run_manifest_locked_v1_amendment001.json"),
            clean_text_directory=_environment_path("CLEAN_TEXT_DIRECTORY", "/workspace/inputs/clean_text"),
            rag_contexts_jsonl_path=_environment_path("RAG_CONTEXTS_JSONL_PATH", "/workspace/inputs/rag/rag_retrieved_contexts_locked_v1.jsonl"),
            output_directory=_environment_path("OUTPUT_DIRECTORY", "/workspace/outputs"),
            experiment_run_id=os.getenv("EXPERIMENT_RUN_ID", "MAIN_RUN_001_AMENDMENT001_GPT55"),
            cost_warning_usd=_environment_float("COST_WARNING_USD", 90.0),
            cost_hard_limit_usd=_environment_float("COST_HARD_LIMIT_USD", 125.0),
            input_cost_usd_per_million_tokens=_environment_float("INPUT_COST_USD_PER_MILLION_TOKENS", 5.0),
            output_cost_usd_per_million_tokens=_environment_float("OUTPUT_COST_USD_PER_MILLION_TOKENS", 30.0),
            max_retry_attempts=_environment_integer("MAX_RETRY_ATTEMPTS", 1),
            rag_top_k=_environment_integer("RAG_TOP_K", 8),
            rag_chunk_word_count=_environment_integer("RAG_CHUNK_WORD_COUNT", 750),
            rag_chunk_overlap_word_count=_environment_integer("RAG_CHUNK_OVERLAP_WORD_COUNT", 100),
            feature_toggles=FeatureToggles.from_environment(),
        )
