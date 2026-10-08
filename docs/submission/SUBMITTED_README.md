# SEC 10-K Dissertation Experiment Apparatus

This repository contains the containerized command-line apparatus used for the dissertation experiment on evidence-grounded cross-section inconsistency detection in SEC Form 10-K filings. The apparatus supports validation of locked inputs, prompt-payload construction, controlled live execution, scoring, telemetry capture and Appendix E evidence export.

The codebase is not a public product. It is the reproducibility environment for the controlled dissertation experiment. The reported results are reproduced from locked artefacts, not by regenerating the evaluation dataset from live external sources.

## 1. Package role

Within the final submission package, this codebase is submitted at:

```text
04_Codebase/CS958-ROUS04-Codebase.zip
```

The main empirical evidence is submitted separately under:

```text
03_Main_Run_Evidence/
```

The primary route for reviewing the dissertation remains the report and readable appendices. This codebase supports implementation review and reproducibility checks.

## 2. Repository layout

```text
app/                     Controlled apparatus source code
tests/                   Unit tests for validation, prompting, scoring and configuration
tools/                   Packaging and input-bootstrap support scripts
inputs/                  Locked experiment inputs used by the reported study
outputs/                 Local output area for validation, prompt dry-run, scoring and export stages
.env.example             Example runtime configuration; no key or secret value is included
Dockerfile               Container build definition
docker-compose.yml       Container execution configuration
requirements.txt         Python dependency list
```

Key locked inputs are retained under:

```text
inputs/claims/claim_case_manifest_v1_locked_amendment001.csv
inputs/queue/api_execution_queue_locked_v1_amendment001.csv
inputs/scoring/scoring_key_locked_v1_amendment001.csv
inputs/rag/rag_retrieved_contexts_locked_v1.jsonl
inputs/clean_text/
inputs/manifests/run_manifest_locked_v1_amendment001.json
```

## 3. Reproducibility modes and execution routes

The apparatus supports three routes. Route 1 is the default no-cost route for reproducing the reported scoring from locked artefacts. Route 2 re-runs live model calls and therefore requires a configured API key and cost acceptance. Route 3 is provenance/rebuild support and is not the default route for reproducing the reported results.

### Route 1: Reproduce reported scoring without API cost

Use this route to validate locked inputs, rebuild prompt payloads without live calls, score archived full-live outputs and export Appendix E evidence files.

From a clean extracted copy of the codebase:

```bash
cd CS958-ROUS04-HarjinderSingh
cp .env.example .env
```

Ensure live calls remain disabled in `.env`:

```text
ENABLE_LIVE_MODEL_CALLS=false
```

Build the container:

```bash
docker compose build
```

Restore the archived full-live outputs from the final submission evidence folder. When working inside the extracted codebase folder within the submission package, the command is:

```bash
unzip -o ../../03_Main_Run_Evidence/Locked_Source_Zips/main_run_full_live_outputs_locked_v1.zip
```

Then run the no-cost validation, dry-run, scoring and evidence-export route:

```bash
docker compose run --rm experiment-runner validate
docker compose run --rm experiment-runner prompt-dry-run
docker compose run --rm experiment-runner score
docker compose run --rm experiment-runner export-evidence
```

Expected outputs include:

```text
outputs/validation/validation_report.md
outputs/prompt_payloads/prompt_hashes.csv
outputs/prompt_payloads/prompt_size_summary.csv
outputs/scoring/scored_predictions.csv
outputs/scoring/condition_metrics.csv
outputs/scoring/confusion_matrix.csv
outputs/scoring/error_taxonomy_template.csv
outputs/appendix_e/
outputs/appendix_e_evidence_pack.zip
```

This route does not perform live model calls. It reproduces scoring and export from locked inputs and archived full-live outputs.

### Route 2: Re-run the live experiment

This route re-runs the 96 strategy-level calls. It requires a configured provider API key, live-call enablement and cost acceptance. Use a fresh extracted copy or an intentionally controlled output directory so that previous evidence is not mixed with a new live run.

Prepare the environment:

```bash
cd CS958-ROUS04-HarjinderSingh
cp .env.example .env
```

Populate the empty provider API-key variable in `.env`, then deliberately enable live calls:

```text
ENABLE_LIVE_MODEL_CALLS=true
```

Build and validate first:

```bash
docker compose build
docker compose run --rm experiment-runner validate
docker compose run --rm experiment-runner prompt-dry-run
```

Run the full live execution only when the run is deliberately intended:

```bash
docker compose run --rm experiment-runner full-live --confirm-main-run
```

After the run, disable live calls again in `.env`:

```text
ENABLE_LIVE_MODEL_CALLS=false
```

Then score and export evidence:

```bash
docker compose run --rm experiment-runner score
docker compose run --rm experiment-runner export-evidence
```

A new live run may differ from the submitted reported evidence because provider-hosted model execution is not claimed to be deterministically repeatable. The reported dissertation findings are based on the retained locked main-run outputs submitted under `03_Main_Run_Evidence/`.

### Route 3: Rebuild preprocessing and RAG artefacts

This route is provenance/rebuild support. It is not the default route for reproducing the reported results because the reported experiment is defined by the locked Amendment001 artefacts.

Source acquisition requires an explicit manifest CSV containing the source URLs and target filenames:

```bash
docker compose run --rm experiment-runner fetch-sec-filings --manifest <manifest_csv_path>
```

Clean-text preparation requires an explicit source directory:

```bash
docker compose run --rm experiment-runner clean-filings --source-dir <raw_filing_directory>
```

Section inventory and chunk construction can then be rebuilt from the configured clean-text directory:

```bash
docker compose run --rm experiment-runner build-section-inventory
docker compose run --rm experiment-runner build-rag-chunks
```

RAG context rebuilding is disabled by default. To rebuild retrieved contexts, enable the rebuild flag in `.env` and ensure a provider API key is configured because embeddings are required:

```text
ENABLE_RAG_CONTEXT_REBUILD=true
```

Then run:

```bash
docker compose run --rm experiment-runner build-rag-contexts
```

Rebuilt preprocessing or retrieval artefacts are provenance outputs. They do not replace the locked inputs used for the reported dissertation findings unless a new experiment version is intentionally defined, validated and documented.

## 4. Dataset and claim-case boundary

Claim-case construction is a controlled evaluation-dataset activity rather than a fully automated regeneration step. The reproducibility basis is the submitted locked dataset and scoring material, including:

```text
claim-case manifest
claim anchors
expected labels
rationales
scoring key
selection criteria
amendment record
validation report
```

A reviewer can inspect the claim cases, evidence anchors and scoring key, then rerun scoring against the retained outputs. The apparatus is not expected to recreate the same 48 human-designed claim-cases automatically from raw filings.

## 5. Methodological controls supported by the codebase

| Methodological requirement | Codebase support |
|---|---|
| Replicability | Container, locked inputs, README commands, prompt templates, scoring key and output schema. |
| Reliability | Paired same-model design, fixed prompt assembly, raw/parsed output preservation and telemetry capture. |
| Validity | Hidden scoring key, claim anchors, label definitions, pilot/pre-main-run calibration boundary and consistent scoring logic. |
| Transferability boundary | Results are bounded to SEC Form 10-K filings, the selected API model, six filings, 48 claim-cases and the locked context-delivery configuration. |

The fair-test control is that both context-delivery strategies use the same selected model, filing corpus, claim-case set, output schema, scoring key and evaluation process wherever feasible.

## 6. Live-call and cost controls

Live calls are disabled by default:

```text
ENABLE_LIVE_MODEL_CALLS=false
```

The full live route also requires the explicit confirmation flag:

```bash
docker compose run --rm experiment-runner full-live --confirm-main-run
```

Cost guard settings are configured in `.env.example` and can be reviewed before any live execution. API keys and private credentials are not included in this package.

## 7. Evidence relationship

The codebase can reproduce validation, prompt payloads, scoring and Appendix E export from locked artefacts. The final empirical evidence used in the dissertation is retained separately under:

```text
03_Main_Run_Evidence/Appendix_E_Evidence_Pack/
03_Main_Run_Evidence/Derived_Analysis/
03_Main_Run_Evidence/Locked_Source_Zips/
```

The locked source ZIPs preserve the full-live outputs, scoring outputs and Appendix E evidence-pack material. The codebase should be read together with those evidence folders when checking reproducibility.

## 8. Expected default review path

For most review purposes, use Route 1:

```bash
docker compose build
docker compose run --rm experiment-runner validate
docker compose run --rm experiment-runner prompt-dry-run
docker compose run --rm experiment-runner score
docker compose run --rm experiment-runner export-evidence
```

This is the default route because it checks the reported experiment from locked inputs and retained outputs without new live calls or additional cost.