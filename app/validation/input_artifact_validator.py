"""Input validation confirms the locked dissertation artefacts are ready to run."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.common.csv_table import read_csv_records, write_csv_records
from app.common.file_hashing import build_hash_manifest
from app.common.jsonl_table import read_jsonl_records
from app.config.runtime_settings import ExperimentRuntimeSettings
from app.validation.answer_key_leakage_checker import AnswerKeyLeakageChecker


class InputArtifactValidator:
    """Validates queue, scoring key, clean filings, and RAG contexts before execution."""

    def __init__(self, leakage_checker: AnswerKeyLeakageChecker) -> None:
        self.leakage_checker = leakage_checker

    def validate_locked_inputs(self, runtime_settings: ExperimentRuntimeSettings) -> dict:
        """Runs all pre-execution gates against the frozen Step 3A inputs."""
        validation_issues: list[str] = []
        queue_records = self._safe_load_csv(runtime_settings.queue_csv_path, validation_issues, "queue")
        scoring_records = self._safe_load_csv(runtime_settings.scoring_key_csv_path, validation_issues, "scoring_key")
        rag_context_records = self._safe_load_jsonl(runtime_settings.rag_contexts_jsonl_path, validation_issues, "rag_contexts")

        self._validate_queue_records(queue_records, validation_issues)
        self._validate_scoring_records(scoring_records, validation_issues)
        self._validate_clean_text_files(queue_records, runtime_settings.clean_text_directory, validation_issues)
        self._validate_rag_context_records(queue_records, rag_context_records, validation_issues)
        self._validate_case_alignment(queue_records, scoring_records, validation_issues)

        try:
            self.leakage_checker.assert_queue_contains_no_hidden_expected_labels(queue_records)
        except ValueError as leakage_error:
            validation_issues.append(str(leakage_error))

        hash_manifest_records = build_hash_manifest(
            {
                "queue_csv": runtime_settings.queue_csv_path,
                "scoring_key_csv": runtime_settings.scoring_key_csv_path,
                "claim_manifest_csv": runtime_settings.claim_manifest_csv_path,
                "run_manifest_json": runtime_settings.run_manifest_json_path,
                "rag_contexts_jsonl": runtime_settings.rag_contexts_jsonl_path,
            }
        )

        validation_report = {
            "status": "PASS" if not validation_issues else "FAIL",
            "issues": validation_issues,
            "queue_rows": len(queue_records),
            "scoring_key_rows": len(scoring_records),
            "rag_context_rows": len(rag_context_records),
            "condition_counts": dict(Counter(record.get("condition", "") for record in queue_records)),
            "label_counts": dict(Counter(record.get("expected_label", "") for record in scoring_records)),
            "clean_text_file_count": len(list(runtime_settings.clean_text_directory.glob("*.txt"))) if runtime_settings.clean_text_directory.exists() else 0,
            "artifact_hash_manifest": hash_manifest_records,
        }
        return validation_report

    def write_validation_report(self, runtime_settings: ExperimentRuntimeSettings, validation_report: dict) -> None:
        """Writes JSON, Markdown, and hash manifest evidence for the readiness gate."""
        validation_output_directory = runtime_settings.output_directory / "validation"
        validation_output_directory.mkdir(parents=True, exist_ok=True)
        (validation_output_directory / "validation_report.json").write_text(
            json.dumps(validation_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        markdown_lines = [
            "# Main Run Input Validation Report",
            "",
            f"Status: **{validation_report['status']}**",
            f"Queue rows: {validation_report['queue_rows']}",
            f"Scoring key rows: {validation_report['scoring_key_rows']}",
            f"RAG context rows: {validation_report['rag_context_rows']}",
            f"Clean text files: {validation_report['clean_text_file_count']}",
            "",
            "## Issues",
        ]
        markdown_lines.extend([f"- {issue}" for issue in validation_report["issues"]] or ["- None"])
        (validation_output_directory / "validation_report.md").write_text("\n".join(markdown_lines), encoding="utf-8")
        write_csv_records(
            validation_output_directory / "artifact_hash_manifest.csv",
            validation_report["artifact_hash_manifest"],
            ["artefact_name", "path", "exists", "sha256"],
        )

    def _safe_load_csv(self, csv_path: Path, validation_issues: list[str], artefact_name: str) -> list[dict[str, str]]:
        """Loads a CSV artefact while recording a validation issue when missing."""
        if not csv_path.exists():
            validation_issues.append(f"Missing {artefact_name}: {csv_path}")
            return []
        return read_csv_records(csv_path)

    def _safe_load_jsonl(self, jsonl_path: Path, validation_issues: list[str], artefact_name: str) -> list[dict]:
        """Loads a JSONL artefact while recording a validation issue when missing."""
        if not jsonl_path.exists():
            validation_issues.append(f"Missing {artefact_name}: {jsonl_path}")
            return []
        return read_jsonl_records(jsonl_path)

    def _validate_queue_records(self, queue_records: list[dict[str, str]], validation_issues: list[str]) -> None:
        """Checks expected row and condition counts for the 96-call experiment."""
        if len(queue_records) != 96:
            validation_issues.append(f"Expected 96 queue rows, found {len(queue_records)}")
        condition_counts = Counter(record.get("condition", "") for record in queue_records)
        if condition_counts.get("Long_Context") != 48 or condition_counts.get("RAG") != 48:
            validation_issues.append(f"Expected 48 Long_Context and 48 RAG rows, found {dict(condition_counts)}")

    def _validate_scoring_records(self, scoring_records: list[dict[str, str]], validation_issues: list[str]) -> None:
        """Checks expected scoring-key row and label-balance counts."""
        if len(scoring_records) != 48:
            validation_issues.append(f"Expected 48 scoring key rows, found {len(scoring_records)}")
        label_counts = Counter(record.get("expected_label", "") for record in scoring_records)
        expected_label_counts = {"Supported": 16, "Contradicted": 16, "Insufficient Evidence": 16}
        if dict(label_counts) != expected_label_counts:
            validation_issues.append(f"Expected label balance {expected_label_counts}, found {dict(label_counts)}")

    def _validate_clean_text_files(self, queue_records: list[dict[str, str]], clean_text_directory: Path, validation_issues: list[str]) -> None:
        """Confirms each queued run can access its locked clean filing text."""
        for source_file in sorted({record.get("source_file", "") for record in queue_records if record.get("source_file")}):
            if not (clean_text_directory / source_file).exists():
                validation_issues.append(f"Missing clean text source file: {source_file}")

    def _validate_rag_context_records(self, queue_records: list[dict[str, str]], rag_context_records: list[dict], validation_issues: list[str]) -> None:
        """Confirms each RAG queue row has one frozen retrieved-context record."""
        rag_run_ids = {record.get("run_id") for record in queue_records if record.get("condition") == "RAG"}
        context_run_ids = {record.get("run_id") for record in rag_context_records}
        missing_context_run_ids = sorted(rag_run_ids - context_run_ids)
        if missing_context_run_ids:
            validation_issues.append(f"Missing RAG contexts for run IDs: {missing_context_run_ids[:10]}")
        if len(rag_context_records) != 48:
            validation_issues.append(f"Expected 48 RAG context records, found {len(rag_context_records)}")

    def _validate_case_alignment(
        self,
        queue_records: list[dict[str, str]],
        scoring_records: list[dict[str, str]],
        validation_issues: list[str],
    ) -> None:
        """Checks queue case IDs align with the hidden scoring-key case IDs."""
        queue_case_ids = {record.get("case_id") for record in queue_records}
        scoring_case_ids = {record.get("case_id") for record in scoring_records}
        if queue_case_ids != scoring_case_ids:
            validation_issues.append("Queue case IDs do not match scoring-key case IDs.")
