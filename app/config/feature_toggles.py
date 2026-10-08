"""Feature toggles keep preparation, execution, and export stages controlled."""
from __future__ import annotations

from dataclasses import dataclass
import os


def _environment_flag(environment_variable_name: str, default_value: bool) -> bool:
    raw_value = os.getenv(environment_variable_name)
    if raw_value is None:
        return default_value
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class FeatureToggles:
    """Enables or disables apparatus capabilities without changing code."""

    enable_sec_fetch: bool
    enable_text_cleaning: bool
    enable_rag_context_rebuild: bool
    enable_prompt_payload_capture: bool
    enable_full_prompt_text_storage: bool
    enable_prompt_hashing: bool
    enable_live_model_calls: bool
    enable_cost_guard: bool
    enable_retry_policy: bool
    enable_appendix_e_export: bool
    enable_local_file_storage: bool
    enable_vector_store_faiss: bool

    @staticmethod
    def from_environment() -> "FeatureToggles":
        """Loads feature switches from environment variables for 12-Factor config."""
        return FeatureToggles(
            enable_sec_fetch=_environment_flag("ENABLE_SEC_FETCH", False),
            enable_text_cleaning=_environment_flag("ENABLE_TEXT_CLEANING", False),
            enable_rag_context_rebuild=_environment_flag("ENABLE_RAG_CONTEXT_REBUILD", False),
            enable_prompt_payload_capture=_environment_flag("ENABLE_PROMPT_PAYLOAD_CAPTURE", True),
            enable_full_prompt_text_storage=_environment_flag("ENABLE_FULL_PROMPT_TEXT_STORAGE", True),
            enable_prompt_hashing=_environment_flag("ENABLE_PROMPT_HASHING", True),
            enable_live_model_calls=_environment_flag("ENABLE_LIVE_MODEL_CALLS", False),
            enable_cost_guard=_environment_flag("ENABLE_COST_GUARD", True),
            enable_retry_policy=_environment_flag("ENABLE_RETRY_POLICY", True),
            enable_appendix_e_export=_environment_flag("ENABLE_APPENDIX_E_EXPORT", True),
            enable_local_file_storage=_environment_flag("ENABLE_LOCAL_FILE_STORAGE", True),
            enable_vector_store_faiss=_environment_flag("ENABLE_VECTOR_STORE_FAISS", False),
        )
