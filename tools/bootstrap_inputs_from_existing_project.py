"""Copies frozen Step 3A dissertation inputs into the container app layout."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import zipfile


def main() -> int:
    """Copies current authoritative artefacts from the existing project root."""
    parser = argparse.ArgumentParser(description="Bootstrap Step 3A frozen inputs into main_run_container_app")
    parser.add_argument("--project-root", required=True, help="Existing sec10k_filing_smoke_test_harness_v1 root")
    parser.add_argument("--app-root", required=True, help="main_run_container_app root")
    parsed_arguments = parser.parse_args()

    project_root = Path(parsed_arguments.project_root).resolve()
    app_root = Path(parsed_arguments.app_root).resolve()
    copy_file(project_root / "api_execution_queue_locked_v1_amendment001.csv", app_root / "inputs/queue/api_execution_queue_locked_v1_amendment001.csv")
    copy_file(project_root / "scoring_key_locked_v1_amendment001.csv", app_root / "inputs/scoring/scoring_key_locked_v1_amendment001.csv")
    copy_file(project_root / "claim_case_manifest_v1_locked_amendment001.csv", app_root / "inputs/claims/claim_case_manifest_v1_locked_amendment001.csv")
    copy_file(project_root / "run_manifest_locked_v1_amendment001.json", app_root / "inputs/manifests/run_manifest_locked_v1_amendment001.json")

    clean_text_source_directory = project_root / "outputs/smoke_test_run/clean_text"
    clean_text_target_directory = app_root / "inputs/clean_text"
    clean_text_target_directory.mkdir(parents=True, exist_ok=True)
    for clean_text_file_path in sorted(clean_text_source_directory.glob("*.txt")):
        copy_file(clean_text_file_path, clean_text_target_directory / clean_text_file_path.name)

    rag_context_source_path = project_root / "outputs/main_run/rag/rag_retrieved_contexts_locked_v1.jsonl"
    if not rag_context_source_path.exists() and (project_root / "rag_contexts_live_v1_locked_full.zip").exists():
        with zipfile.ZipFile(project_root / "rag_contexts_live_v1_locked_full.zip") as zip_file:
            for member_name in zip_file.namelist():
                if member_name.endswith("rag_retrieved_contexts_locked_v1.jsonl"):
                    target_path = app_root / "inputs/rag/rag_retrieved_contexts_locked_v1.jsonl"
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_bytes(zip_file.read(member_name))
                    break
    else:
        copy_file(rag_context_source_path, app_root / "inputs/rag/rag_retrieved_contexts_locked_v1.jsonl")

    print("Bootstrap complete. Run: docker compose run --rm experiment-runner validate")
    return 0


def copy_file(source_path: Path, target_path: Path) -> None:
    """Copies one artefact while failing fast when the expected source is absent."""
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source artefact: {source_path}")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)


if __name__ == "__main__":
    raise SystemExit(main())
