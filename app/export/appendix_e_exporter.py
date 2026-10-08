"""Appendix E exporter gathers run evidence into dissertation-ready files."""
from __future__ import annotations

import shutil
from pathlib import Path

from app.config.runtime_settings import ExperimentRuntimeSettings


class AppendixEExporter:
    """Creates the Appendix E evidence folder from validation, run, and scoring outputs."""

    def export_appendix_e_evidence(self, runtime_settings: ExperimentRuntimeSettings) -> dict:
        """Copies key evidence tables and writes an Appendix E index file."""
        if not runtime_settings.feature_toggles.enable_appendix_e_export:
            raise RuntimeError("ENABLE_APPENDIX_E_EXPORT must be true to export Appendix E evidence.")
        appendix_e_output_directory = runtime_settings.output_directory / "appendix_e"
        appendix_e_output_directory.mkdir(parents=True, exist_ok=True)
        copied_files: list[str] = []
        candidate_paths = [
            runtime_settings.output_directory / "validation" / "validation_report.md",
            runtime_settings.output_directory / "validation" / "artifact_hash_manifest.csv",
            runtime_settings.output_directory / "prompt_payloads" / "prompt_hashes.csv",
            runtime_settings.output_directory / "prompt_payloads" / "prompt_size_summary.csv",
            runtime_settings.output_directory / "full_live" / "main_run_telemetry.csv",
            runtime_settings.output_directory / "scoring" / "scored_predictions.csv",
            runtime_settings.output_directory / "scoring" / "condition_metrics.csv",
            runtime_settings.output_directory / "scoring" / "confusion_matrix.csv",
            runtime_settings.output_directory / "scoring" / "error_taxonomy_template.csv",
        ]
        for candidate_path in candidate_paths:
            if candidate_path.exists():
                target_path = appendix_e_output_directory / candidate_path.name
                shutil.copy2(candidate_path, target_path)
                copied_files.append(target_path.name)
        index_lines = ["# Appendix E Evidence Index", "", "Copied evidence files:"]
        index_lines.extend([f"- {file_name}" for file_name in copied_files] or ["- No files copied yet."])
        (appendix_e_output_directory / "Appendix_E_Evidence_Index.md").write_text("\n".join(index_lines), encoding="utf-8")
        return {"status": "PASS", "copied_files": copied_files}
