# Portfolio preparation verification

**Checked on 8 October 2026.** This records checks actually executed against the supplied submission and the curated copy. It is not a CI badge, a Docker certification or a new model evaluation.

## Results

| Check | Observed result |
|---|---|
| Included submitted-file integrity | 110 mapped copies matched their submitted SHA-256 values |
| Dataset structure | Six filings, 48 cases, 16 cases per label, 96 paired queue/output/telemetry entries |
| Original locked-input validation | PASS |
| Original submitted unit tests | **6 passed** |
| Full prompt reconstruction | All 96 payloads regenerated; the complete JSONL matched the submitted full-live payload byte-for-byte |
| Prompt audit tables | `prompt_hashes.csv` and `prompt_size_summary.csv` matched byte-for-byte |
| Original scorer replay | `scored_predictions.csv`, `condition_metrics.csv` and `confusion_matrix.csv` matched byte-for-byte |
| Independent headline metric checks | 41/48 correct, 85.42% accuracy, 84.68% macro F1 for Long_Context; 42/48, 87.50%, 87.28% for RAG |
| Telemetry checks | Per-condition call counts, token totals, historic token-derived cost and latency aggregates agreed with retained tables |
| Error-pattern checks | 13 incorrect outputs across eight cases; 12 Insufficient Evidence → Contradicted errors; all 13 reported High confidence |
| Original evidence exporter | PASS; nine expected evidence files copied, plus generated index |
| Added standalone verifier | Passed with Python site packages disabled (`python -S`); no API key or third-party package required |
| Added response-restoration helper | Fresh restore passed; repeat restore passed; different existing output was refused without overwriting it |
| Public PDF | 50 pages; registration-number line removed; pages 2–50 identical in extracted text and rendered pixels at 72 dpi |

The redacted cover and selected result/source-register pages were also rendered and visually inspected. This is a bounded privacy change; the research chapters were not rewritten.

## Execution environment and boundaries

The checks above ran in **Linux with Python 3.13.5** and **pytest 9.0.2**, not in the original submission-time environment. The original CLI's offline stage functions were invoked with explicit host-path settings. Socket connections were disabled for that replay. No OpenAI SDK was installed in this review environment; the original source's optional-import/lazy-client behaviour allowed the offline stages to run without it.

Docker was not available for this review. **The submitted `python:3.11-slim` image was not rebuilt, the Compose commands were not executed, Windows was not tested, no embedding calls were made, and no live model calls were made.** No new API cost was incurred by the executed verification. The Docker instructions are derived from the submitted Dockerfile, Compose file, CLI and path configuration, rather than a claimed fresh Docker run.

The original `requirements.txt` specifies minimum versions, not a complete historical lockfile. The verification environment must not be advertised as the original experiment's dependency environment. Native success does not by itself establish cross-platform or container-build success.

## Exact-match scope

The full request-payload JSONL and its two audit CSVs matched the original retained full-live request evidence. Three original scoring CSVs matched exactly. Newly generated runtime manifests, logs and output-path fields may differ by time and machine and were not claimed to be identical. The exporter was checked for the expected file set, not for a universally deterministic ZIP file.

The main-run request used the model alias and parameters recorded in the submission. Reconstructing a request is not equivalent to reproducing provider-side model inference. Results here are archived evidence replay, not a statistically independent repeat.

## Audit trail

[Source integrity manifest](provenance/source-integrity.json) identifies the supplied archive hash, each unchanged file's source path, the public PDF's original/new hashes, and the omitted regenerable payload's hash and byte count. [Publication notes](PUBLICATION_NOTES.md) distinguish post-submission portfolio additions from the submitted application.

Run `python tools/portfolio_verify.py` to repeat the current-file and archived-score checks. After prompt reconstruction, add `--check-generated-payloads`. The submitted tests remain under `tests/`.

The pattern-based privacy/credential review is not a security certification, dependency vulnerability assessment, proof of university publication permission, or exhaustive examination of text hidden in every image. These publication checks do not establish that no possible sensitive content can remain.
