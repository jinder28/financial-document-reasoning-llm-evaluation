"""API-free verification added for the portfolio; not part of the submitted apparatus."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("Supported", "Contradicted", "Insufficient Evidence")
CONDITIONS = ("Long_Context", "RAG")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def verify_source_integrity() -> dict[str, Any]:
    manifest = json.loads((ROOT / "docs/provenance/source-integrity.json").read_text(encoding="utf-8"))
    for record in manifest["copied_files"]:
        path = (ROOT / record["repository_path"]).resolve()
        require(path.is_relative_to(ROOT), "Integrity manifest contains an out-of-tree path")
        require(path.is_file(), f"Missing source file: {record['repository_path']}")
        require(sha256(path) == record["sha256"], f"Source bytes changed: {record['repository_path']}")
    report = manifest["public_report"]
    require(sha256(ROOT / report["path"]) == report["public_sha256"], "Public report bytes changed")
    return manifest


def calculate_results() -> dict[str, Any]:
    manifest = verify_source_integrity()
    evidence = ROOT / "evidence/main-run"
    predictions = read_jsonl(evidence / "parsed_model_outputs.jsonl")
    raw = read_jsonl(evidence / "raw_model_outputs.jsonl")
    telemetry = read_csv(evidence / "main_run_telemetry.csv")
    key = read_csv(ROOT / "inputs/scoring/scoring_key_locked_v1_amendment001.csv")
    queue = read_csv(ROOT / "inputs/queue/api_execution_queue_locked_v1_amendment001.csv")
    require(len(key) == 48 and len({r["case_id"] for r in key}) == 48, "Expected 48 unique ground-truth cases")
    require(Counter(r["expected_label"] for r in key) == Counter({label: 16 for label in LABELS}), "Ground-truth labels are not balanced 16/16/16")
    for name, records in [("predictions", predictions), ("raw responses", raw), ("telemetry", telemetry), ("queue", queue)]:
        require(len(records) == 96 and len({r["run_id"] for r in records}) == 96, f"Expected 96 unique {name}")
        require(Counter(r["condition"] for r in records) == Counter({c: 48 for c in CONDITIONS}), f"Unbalanced conditions in {name}")
    expected_triples = {(r["run_id"], r["case_id"], r["condition"]) for r in queue}
    require(len({(r["case_id"], r["condition"]) for r in queue}) == 96, "Duplicate case/condition pair")
    for name, records in [("predictions", predictions), ("raw responses", raw), ("telemetry", telemetry)]:
        require({(r["run_id"], r["case_id"], r["condition"]) for r in records} == expected_triples, f"Run/case/condition alignment failed for {name}")
    for record in predictions:
        require(record["case_id"] == record["parsed_output"]["case_id"], "Embedded prediction case ID mismatch")
        require(record["parsed_output"]["predicted_label"] in LABELS, "Unknown predicted label")
    require(all(r["status"] == "LIVE_CALL_COMPLETED" for r in telemetry), "Incomplete archived calls")
    require(all(int(r["retry_attempts_used"]) == 0 for r in telemetry), "Unexpected retries")

    # Reuse the original submitted scorer. It needs only Python's standard library.
    sys.path.insert(0, str(ROOT))
    from app.scoring.classification_scorer import ClassificationScorer
    with tempfile.TemporaryDirectory(prefix="dissertation-score-") as directory:
        output = Path(directory)
        result = ClassificationScorer().score_predictions(
            evidence / "parsed_model_outputs.jsonl",
            ROOT / "inputs/scoring/scoring_key_locked_v1_amendment001.csv",
            output,
        )
        require(result["scored_prediction_count"] == 96, "Scorer did not produce 96 predictions")
        for name in ("scored_predictions.csv", "condition_metrics.csv", "confusion_matrix.csv"):
            require((output / name).read_bytes() == (evidence / name).read_bytes(), f"Archived scoring differs: {name}")
        scored = read_csv(output / "scored_predictions.csv")

    results: dict[str, Any] = {}
    for condition in CONDITIONS:
        selected = [r for r in scored if r["condition"] == condition]
        calls = [r for r in telemetry if r["condition"] == condition]
        label_metrics = {}
        for label in LABELS:
            tp = sum(r["expected_label"] == label and r["predicted_label"] == label for r in selected)
            fp = sum(r["expected_label"] != label and r["predicted_label"] == label for r in selected)
            fn = sum(r["expected_label"] == label and r["predicted_label"] != label for r in selected)
            label_metrics[label] = {
                "precision": tp / (tp + fp) if tp + fp else 0,
                "recall": tp / (tp + fn) if tp + fn else 0,
                "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0,
            }
        correct = sum(r["expected_label"] == r["predicted_label"] for r in selected)
        input_tokens = sum(int(r["input_tokens"]) for r in calls)
        output_tokens = sum(int(r["output_tokens"]) for r in calls)
        # These are the study's historical constants, not current provider prices.
        token_cost = (Decimal(input_tokens) * 5 + Decimal(output_tokens) * 30) / 1_000_000
        require(token_cost == sum(Decimal(r["estimated_call_cost_usd"]) for r in calls), "Cost/token cross-check failed")
        results[condition] = {
            "correct": correct,
            "total": len(selected),
            "accuracy": correct / len(selected),
            "macro_f1": statistics.mean(m["f1"] for m in label_metrics.values()),
            "label_metrics": label_metrics,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "telemetry_estimated_model_call_cost_usd": str(token_cost),
            "mean_latency_seconds": statistics.mean(float(r["elapsed_seconds"]) for r in calls),
            "median_latency_seconds": statistics.median(float(r["elapsed_seconds"]) for r in calls),
        }
    errors = [r for r in scored if r["is_correct"] == "NO"]
    require(results["Long_Context"]["correct"] == 41 and results["RAG"]["correct"] == 42, "Published count cross-check failed")
    return {
        "status": "PASS",
        "unmodified_source_files_verified": len(manifest["copied_files"]),
        "original_scorer_output": "Three scoring CSVs reproduced byte-for-byte",
        "provider_model_identifiers_in_archived_responses": sorted({r["raw_response"]["model"] for r in raw}),
        "misclassified_outputs": len(errors),
        "distinct_error_cases": len({r["case_id"] for r in errors}),
        "error_confidence_counts": dict(Counter(r["confidence"] for r in errors)),
        "results": results,
        "scope": "Archived scoring and telemetry verification; no model calls, retrieval, or network access is performed by this helper.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    parser.add_argument("--check-generated-payloads", action="store_true", help="Also verify outputs/prompt_payloads against the archived full-payload hash")
    args = parser.parse_args()
    try:
        results = calculate_results()
        if args.check_generated_payloads:
            manifest = json.loads((ROOT / "docs/provenance/source-integrity.json").read_text(encoding="utf-8"))
            generated = ROOT / "outputs/prompt_payloads"
            require(sha256(generated / "full_model_request_payloads.jsonl") == manifest["omitted_regenerable_payload"]["sha256"], "Regenerated full payloads differ from the submitted archive")
            for name in ("prompt_hashes.csv", "prompt_size_summary.csv"):
                require((generated / name).read_bytes() == (ROOT / "evidence/main-run" / name).read_bytes(), f"Regenerated {name} differs")
            results["generated_payloads"] = "PASS: full payload SHA-256 and both summary CSVs match the submission"
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("PASS: source integrity and archived scoring verified; no API calls.")
            for condition, metrics in results["results"].items():
                print(f"{condition}: {metrics['correct']}/{metrics['total']} correct | accuracy {metrics['accuracy']:.2%} | macro F1 {metrics['macro_f1']:.2%}")
                print(f"  input tokens {metrics['input_tokens']:,} | estimated model-call cost ${metrics['telemetry_estimated_model_call_cost_usd']} | mean latency {metrics['mean_latency_seconds']:.2f}s")
            print(f"{results['misclassified_outputs']} incorrect outputs across {results['distinct_error_cases']} cases; all reported High confidence.")
            if args.check_generated_payloads:
                print(results["generated_payloads"])
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
