"""Run manifest exporter records the execution environment and artefact paths."""
from __future__ import annotations

import json
from pathlib import Path

from app.config.runtime_settings import ExperimentRuntimeSettings


class RunManifestExporter:
    """Writes a compact run manifest for Appendix E and reproducibility notes."""

    def write_run_manifest(self, runtime_settings: ExperimentRuntimeSettings, output_path: Path, stage_name: str) -> None:
        """Writes configuration selected for one validation/execution/export stage."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_record = {
            "stage_name": stage_name,
            "experiment_run_id": runtime_settings.experiment_run_id,
            "model_provider": runtime_settings.model_provider,
            "openai_model_id": runtime_settings.openai_model_id,
            "openai_embedding_model_id": runtime_settings.openai_embedding_model_id,
            "queue_csv_path": str(runtime_settings.queue_csv_path),
            "scoring_key_csv_path": str(runtime_settings.scoring_key_csv_path),
            "rag_contexts_jsonl_path": str(runtime_settings.rag_contexts_jsonl_path),
            "clean_text_directory": str(runtime_settings.clean_text_directory),
            "feature_toggles": runtime_settings.feature_toggles.__dict__,
        }
        output_path.write_text(json.dumps(manifest_record, indent=2, ensure_ascii=False), encoding="utf-8")
