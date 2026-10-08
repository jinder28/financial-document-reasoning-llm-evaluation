"""CLI entry point for the controlled SEC 10-K dissertation apparatus."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - container installs python-dotenv.
    load_dotenv = None

from app.common.csv_table import read_csv_records
from app.common.logging_setup import configure_dissertation_logger
from app.config.runtime_settings import ExperimentRuntimeSettings
from app.execution.experiment_queue_loader import ExperimentQueueLoader
from app.execution.experiment_run_controller import ExperimentRunController
from app.execution.openai_responses_model_client import OpenAIResponsesModelClient
from app.export.appendix_e_exporter import AppendixEExporter
from app.export.evidence_pack_builder import EvidencePackBuilder
from app.export.run_manifest_exporter import RunManifestExporter
from app.ingestion.sec_filing_fetcher import SecFilingFetcher
from app.preparation.filing_text_cleaner import FilingTextCleaner
from app.preparation.section_inventory_builder import SectionInventoryBuilder
from app.rag.filing_chunker import FilingChunker
from app.rag.faiss_vector_store import InMemoryCosineVectorStore
from app.rag.openai_embedding_client import OpenAIEmbeddingClient
from app.rag.rag_context_builder import RagContextBuilder
from app.scoring.classification_scorer import ClassificationScorer
from app.scoring.error_taxonomy_template_writer import ErrorTaxonomyTemplateWriter
from app.validation.answer_key_leakage_checker import AnswerKeyLeakageChecker
from app.validation.input_artifact_validator import InputArtifactValidator


def main() -> int:
    """Parses CLI arguments and dispatches the requested apparatus command."""
    if load_dotenv is not None:
        load_dotenv()
    parser = build_argument_parser()
    parsed_arguments = parser.parse_args()
    runtime_settings = ExperimentRuntimeSettings.from_environment()
    logger = configure_dissertation_logger(runtime_settings.output_directory / "logs" / f"{parsed_arguments.command}.log")

    try:
        command_result = dispatch_command(parsed_arguments, runtime_settings)
        logger.info(json.dumps(command_result, indent=2, ensure_ascii=False))
        print(json.dumps(command_result, indent=2, ensure_ascii=False))
        return 0 if command_result.get("status") in {"PASS", "SKIPPED"} else 1
    except Exception as command_error:  # noqa: BLE001 - command failure is written as run evidence.
        logger.exception("Command failed: %s", command_error)
        print(json.dumps({"status": "FAIL", "error": str(command_error)}, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1


def build_argument_parser() -> argparse.ArgumentParser:
    """Defines stage-specific commands for the dissertation experiment lifecycle."""
    parser = argparse.ArgumentParser(description="SEC 10-K dissertation main-run apparatus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate locked Step 3A inputs before execution")
    subparsers.add_parser("prompt-dry-run", help="Build all prompt payloads without live model calls")

    smoke_parser = subparsers.add_parser("smoke-live", help="Run one live GPT-5.5 smoke call")
    smoke_parser.add_argument("--run-id", required=True, help="Exact queue run ID such as MR001_LC or MR001_RAG")

    full_live_parser = subparsers.add_parser("full-live", help="Run the full 96-call main experiment")
    full_live_parser.add_argument("--confirm-main-run", action="store_true", help="Required explicit full-live confirmation")

    score_parser = subparsers.add_parser("score", help="Score parsed live outputs against hidden scoring key")
    score_parser.add_argument("--parsed-output-jsonl", default="", help="Optional parsed output JSONL path")

    subparsers.add_parser("export-evidence", help="Export Appendix E evidence files")
    subparsers.add_parser("build-section-inventory", help="Build section coverage report from clean texts")
    subparsers.add_parser("build-rag-chunks", help="Build RAG chunk manifest from clean texts")
    subparsers.add_parser("build-rag-contexts", help="Optionally rebuild RAG contexts using embeddings")

    fetch_parser = subparsers.add_parser("fetch-sec-filings", help="Optionally download SEC source filings from manifest")
    fetch_parser.add_argument("--manifest", required=True, help="CSV manifest with source_url and target_file_name")

    clean_parser = subparsers.add_parser("clean-filings", help="Optionally clean raw filing files")
    clean_parser.add_argument("--source-dir", required=True, help="Directory of raw HTML/TXT filing files")

    return parser


def dispatch_command(parsed_arguments: argparse.Namespace, runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Routes the requested command to the matching apparatus stage."""
    if parsed_arguments.command == "validate":
        return run_validate_command(runtime_settings)
    if parsed_arguments.command == "prompt-dry-run":
        return run_prompt_dry_run_command(runtime_settings)
    if parsed_arguments.command == "smoke-live":
        return run_smoke_live_command(runtime_settings, parsed_arguments.run_id)
    if parsed_arguments.command == "full-live":
        return run_full_live_command(runtime_settings, parsed_arguments.confirm_main_run)
    if parsed_arguments.command == "score":
        parsed_output_path = Path(parsed_arguments.parsed_output_jsonl) if parsed_arguments.parsed_output_jsonl else runtime_settings.output_directory / "full_live" / "parsed_model_outputs.jsonl"
        return run_score_command(runtime_settings, parsed_output_path)
    if parsed_arguments.command == "export-evidence":
        return run_export_evidence_command(runtime_settings)
    if parsed_arguments.command == "build-section-inventory":
        return run_build_section_inventory_command(runtime_settings)
    if parsed_arguments.command == "build-rag-chunks":
        return run_build_rag_chunks_command(runtime_settings)
    if parsed_arguments.command == "build-rag-contexts":
        return run_build_rag_contexts_command(runtime_settings)
    if parsed_arguments.command == "fetch-sec-filings":
        return run_fetch_sec_filings_command(runtime_settings, Path(parsed_arguments.manifest))
    if parsed_arguments.command == "clean-filings":
        return run_clean_filings_command(runtime_settings, Path(parsed_arguments.source_dir))
    raise ValueError(f"Unknown command: {parsed_arguments.command}")


def run_validate_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Runs readiness validation and writes the validation report outputs."""
    validator = InputArtifactValidator(AnswerKeyLeakageChecker())
    validation_report = validator.validate_locked_inputs(runtime_settings)
    validator.write_validation_report(runtime_settings, validation_report)
    RunManifestExporter().write_run_manifest(
        runtime_settings,
        runtime_settings.output_directory / "validation" / "run_manifest_validation.json",
        "validate",
    )
    return validation_report


def run_prompt_dry_run_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Builds all 96 request payloads and hashes without live model calls."""
    validation_report = run_validate_command(runtime_settings)
    if validation_report["status"] != "PASS":
        raise RuntimeError("Validation must pass before prompt-dry-run.")
    queue_records = ExperimentQueueLoader().load_queue_records(runtime_settings.queue_csv_path)
    controller = ExperimentRunController(runtime_settings, model_client=None)
    result = controller.run_prompt_dry_run(queue_records, runtime_settings.output_directory / "prompt_payloads")
    RunManifestExporter().write_run_manifest(
        runtime_settings,
        runtime_settings.output_directory / "prompt_payloads" / "run_manifest_prompt_dry_run.json",
        "prompt-dry-run",
    )
    return result


def run_smoke_live_command(runtime_settings: ExperimentRuntimeSettings, requested_run_id: str) -> dict:
    """Runs one live call after validation and prompt assembly gates are satisfied."""
    validation_report = run_validate_command(runtime_settings)
    if validation_report["status"] != "PASS":
        raise RuntimeError("Validation must pass before smoke-live.")
    queue_records = ExperimentQueueLoader().select_queue_records(
        ExperimentQueueLoader().load_queue_records(runtime_settings.queue_csv_path), requested_run_id=requested_run_id
    )
    if len(queue_records) != 1:
        raise ValueError(f"Expected one queue row for {requested_run_id}, found {len(queue_records)}")
    controller = ExperimentRunController(runtime_settings, OpenAIResponsesModelClient(runtime_settings))
    return controller.run_live_execution(queue_records, runtime_settings.output_directory / "smoke_live" / requested_run_id)


def run_full_live_command(runtime_settings: ExperimentRuntimeSettings, confirm_main_run: bool) -> dict:
    """Runs the full 96-call experiment only with explicit confirmation."""
    if not confirm_main_run:
        raise RuntimeError("full-live requires --confirm-main-run.")
    validation_report = run_validate_command(runtime_settings)
    if validation_report["status"] != "PASS":
        raise RuntimeError("Validation must pass before full-live.")
    queue_records = ExperimentQueueLoader().load_queue_records(runtime_settings.queue_csv_path)
    controller = ExperimentRunController(runtime_settings, OpenAIResponsesModelClient(runtime_settings))
    return controller.run_live_execution(queue_records, runtime_settings.output_directory / "full_live")


def run_score_command(runtime_settings: ExperimentRuntimeSettings, parsed_output_jsonl_path: Path) -> dict:
    """Scores model outputs after live execution has created parsed JSONL evidence."""
    scoring_result = ClassificationScorer().score_predictions(
        parsed_output_jsonl_path,
        runtime_settings.scoring_key_csv_path,
        runtime_settings.output_directory / "scoring",
    )
    ErrorTaxonomyTemplateWriter().write_error_taxonomy_template(
        runtime_settings.output_directory / "scoring" / "error_taxonomy_template.csv"
    )
    return scoring_result


def run_export_evidence_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Exports Appendix E evidence and builds a portable evidence archive."""
    export_result = AppendixEExporter().export_appendix_e_evidence(runtime_settings)
    EvidencePackBuilder().build_zip_pack(
        runtime_settings.output_directory / "appendix_e",
        runtime_settings.output_directory / "appendix_e_evidence_pack.zip",
    )
    return export_result


def run_build_section_inventory_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Builds a clean-text section inventory for corpus-preparation evidence."""
    inventory_builder = SectionInventoryBuilder()
    inventory_records = inventory_builder.build_section_inventory_records(runtime_settings.clean_text_directory)
    output_csv_path = runtime_settings.output_directory / "preparation" / "section_inventory.csv"
    inventory_builder.write_section_inventory(output_csv_path, inventory_records)
    return {"status": "PASS", "section_inventory_rows": len(inventory_records), "output_csv_path": str(output_csv_path)}


def run_build_rag_chunks_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Builds the chunk manifest using the dissertation RAG chunking policy."""
    chunker = FilingChunker()
    chunk_records = chunker.build_chunk_records_for_clean_texts(
        runtime_settings.clean_text_directory,
        runtime_settings.rag_chunk_word_count,
        runtime_settings.rag_chunk_overlap_word_count,
    )
    output_jsonl_path = runtime_settings.output_directory / "rag" / "rag_chunk_manifest.jsonl"
    chunker.write_chunk_manifest(output_jsonl_path, chunk_records)
    return {"status": "PASS", "chunk_rows": len(chunk_records), "output_jsonl_path": str(output_jsonl_path)}


def run_build_rag_contexts_command(runtime_settings: ExperimentRuntimeSettings) -> dict:
    """Optionally rebuilds retrieved contexts rather than using frozen contexts."""
    if not runtime_settings.feature_toggles.enable_rag_context_rebuild:
        return {"status": "SKIPPED", "reason": "ENABLE_RAG_CONTEXT_REBUILD is false; frozen Step 3A contexts remain authoritative."}
    queue_records = read_csv_records(runtime_settings.queue_csv_path)
    chunker = FilingChunker()
    chunk_records = chunker.build_chunk_records_for_clean_texts(
        runtime_settings.clean_text_directory,
        runtime_settings.rag_chunk_word_count,
        runtime_settings.rag_chunk_overlap_word_count,
    )
    context_builder = RagContextBuilder(
        OpenAIEmbeddingClient(runtime_settings.openai_embedding_model_id),
        InMemoryCosineVectorStore,
    )
    context_records = context_builder.build_context_records(
        queue_records,
        chunk_records,
        runtime_settings.rag_top_k,
        runtime_settings.openai_embedding_model_id,
    )
    output_jsonl_path = runtime_settings.output_directory / "rag" / "rag_retrieved_contexts_rebuilt.jsonl"
    context_builder.write_context_records(output_jsonl_path, context_records)
    return {"status": "PASS", "rag_context_rows": len(context_records), "output_jsonl_path": str(output_jsonl_path)}


def run_fetch_sec_filings_command(runtime_settings: ExperimentRuntimeSettings, manifest_csv_path: Path) -> dict:
    """Runs optional source acquisition from explicit SEC filing URLs."""
    return SecFilingFetcher(runtime_settings).fetch_filings_from_manifest(
        manifest_csv_path, runtime_settings.output_directory / "ingestion" / "sec_source"
    )


def run_clean_filings_command(runtime_settings: ExperimentRuntimeSettings, source_directory: Path) -> dict:
    """Runs optional clean-text preparation into the apparatus outputs folder."""
    return FilingTextCleaner(runtime_settings).clean_source_directory(
        source_directory, runtime_settings.output_directory / "preparation" / "clean_text"
    )


if __name__ == "__main__":
    raise SystemExit(main())
