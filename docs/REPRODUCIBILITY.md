# Reproducing the archived dissertation results

This guide separates **replaying the submitted evidence** from **running a new paid experiment**. A replay verifies the old experiment; it does not make new model requests or independently reproduce the provider's historic inference.

## 1. Fast, dependency-free verification

Prerequisite: Python 3.11 or later. Open a terminal in the repository root (the directory containing `README.md` and `app/`).

```bash
python tools/portfolio_verify.py
```

Use `py -3` on Windows or `python3` on Linux/macOS where that is the installed command. No API key, Docker, package installation or network connection is needed for this helper. It checks the retained-file hashes, the paired 96-output dataset, the original scorer's three CSV outputs, and the reported metrics and telemetry. It writes scoring work into a temporary directory, not into the retained evidence folder.

```bash
# Emit a machine-readable summary to stdout.
python tools/portfolio_verify.py --json
```

Expected headline results: **41/48 correct for Long_Context; 42/48 for RAG**. The original scoring CSVs must match byte-for-byte. A failed check exits nonzero and must be investigated, not bypassed by editing the expected hashes.

## 2. Restore the retained responses for the original CLI

This optional route exercises the submitted application's validation, prompt assembly, scoring and export stages. Start from a fresh working copy; `evidence/` is the retained record and `outputs/` is scratch space.

```bash
python tools/portfolio_restore.py
```

This copies `raw_model_outputs.jsonl`, `parsed_model_outputs.jsonl` and `main_run_telemetry.csv` from `evidence/main-run/` into `outputs/full_live/`. It is safe to repeat when the files are identical; it refuses to replace a different run. It does not restore secrets or request payloads.

### Prepare local configuration

In **PowerShell**, copy the empty example only when no `.env` exists:

```powershell
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
```

In a POSIX shell:

```bash
[ -f .env ] || cp .env.example .env
```

For this replay, keep `OPENAI_API_KEY` empty and these flags `false`: `ENABLE_LIVE_MODEL_CALLS`, `ENABLE_SEC_FETCH`, `ENABLE_TEXT_CLEANING` and `ENABLE_RAG_CONTEXT_REBUILD`. Retain the `/workspace/...` paths for Docker; they are container paths, not Windows paths.

### Run the submitted Docker workflow

Prerequisites: a working Docker installation with Compose. Building the image downloads a base image and packages, so that build is **not network-free**. These commands use the original submitted Dockerfile and Compose service. Stop after any command that fails.

```bash
# Build the application image; does not call an LLM.
docker compose build

# Validate the locked corpus, queue, scoring key and contexts.
docker compose run --rm experiment-runner validate

# Rebuild the 96 model-facing payloads without sending them.
docker compose run --rm experiment-runner prompt-dry-run

# Score the archived responses restored in the preceding step.
docker compose run --rm experiment-runner score

# Assemble the locally regenerated evidence pack.
docker compose run --rm experiment-runner export-evidence

# Verify that rebuilt payloads match the submitted main-run payload and hashes.
python tools/portfolio_verify.py --check-generated-payloads
```

The exporter should list **nine copied evidence files**, plus its generated index. A nominal exporter `PASS` alone is not a completeness check: inspect `copied_files`, because the original exporter skips missing files. The sequence above supplies all nine.

Expected scratch outputs:

| Directory | Purpose |
|---|---|
| `outputs/validation/` | Locked-input validation and artifact hashes |
| `outputs/prompt_payloads/` | 96 request payloads and prompt hash/size CSVs |
| `outputs/full_live/` | Restored historic responses and telemetry; no new inference |
| `outputs/scoring/` | Three scoring CSVs and the original blank error-taxonomy template |
| `outputs/appendix_e/` | Regenerated evidence export |

The reconstructed full payload file is about 38.6 MB (decimal). It is intentionally absent from the public snapshot because it can be regenerated from retained inputs. Its original SHA-256 is in [source-integrity.json](provenance/source-integrity.json). Runtime manifests contain new timestamps/local paths; **they are not claimed to be byte-identical to historic manifests**. The exact-match claims concern the full request payload file, its two summary CSVs, and the three scoring CSVs.

## 3. Unit tests

The submitted image does not copy `tests/` into the container. For a native Python test run, use an isolated environment with the dependencies in `requirements.txt` installed, then run:

```bash
python -m pytest -q tests
```

There are six submitted tests. They are unit tests, not evidence of production load testing or a fresh API integration run. The optional native application route also requires adapting the six input-path settings and `OUTPUT_DIRECTORY` from `/workspace/...` to actual host paths; the Docker route above avoids that host-path setup.

## 4. New live experiments are a separate operation

A live run is **not required to inspect this portfolio**. It needs a valid account/key, current model access, sufficient context/output limits and an independently chosen budget. The source defaults document a historical study configuration; they do not establish current model availability or prices.

Use a fresh working copy and fresh `outputs/` for any new run. Keep historic `inputs/` and `evidence/` unchanged; changed claims, retrieval, prompts or model settings define a new experiment, not a replay. A full run requires both the live-call feature flag and the explicit `--confirm-main-run` argument. Do not execute it merely to verify the README.

The recorded cost estimates use **$5 per million input tokens and $30 per million output tokens** from the submitted configuration. These are historic model-call accounting constants, not current prices or a complete RAG-system cost. The cost guard updates after a completed response; it is not a guaranteed prepaid limit and can exceed a threshold on the call that crosses it.

The legacy `OPENAI_TEMPERATURE=0` entry remains in the unmodified example file, but the submitted model client does **not** send `temperature` on this API path. Do not describe the live run as deterministic temperature-zero inference. Also, `faiss_vector_store.py` implements exact in-memory cosine ranking rather than FAISS.

## Verification boundary

The no-API helper, archived scoring, native prompt construction and six unit tests were checked during portfolio preparation. **Docker image builds, execution on Windows, fresh retrieval embeddings and live model calls were not rerun.** The submitted dependency file uses minimum versions rather than a fully pinned lockfile; a new container build is not guaranteed to reproduce the historic dependency environment. See [VERIFICATION.md](VERIFICATION.md).
