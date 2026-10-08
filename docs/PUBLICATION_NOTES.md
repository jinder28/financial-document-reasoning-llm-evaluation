# Publication notes and provenance

Prepared on 8 October 2026 from the author's submitted `Dissertation_Submission_Artefacts.7z`. This is a **curated public-facing copy**, not a replacement of the academic submission or a claim that the portfolio additions existed at submission time.

## Preserved from the submission

The active application, tests, original utilities, Docker configuration, dependency file, blank environment example and locked inputs are copied without source edits. The included final responses, telemetry, metrics, analysis workbook and readable appendices are also unchanged. **110 copied files** are mapped to their submitted paths and SHA-256 values in [source-integrity.json](provenance/source-integrity.json).

The original examiner-facing README is retained at [docs/submission/SUBMITTED_README.md](submission/SUBMITTED_README.md). Some paths there describe the larger submitted package and are intentionally not rewritten. Use the root README and [reproduction guide](REPRODUCIBILITY.md) for this public layout.

The retained `artifact_hash_manifest.csv` likewise belongs to the original run. The new provenance manifest maps the curated layout; it does not rewrite historic evidence to pretend the original directory layout was different.

## Disclosed changes

The public report removes the cover's student registration-number line using applied PDF redaction and clears document metadata. This is not a white rectangle hiding selectable text. The report retains 50 pages, the original title, author, declaration, chapters, results, references and appendices listed within it. Pages 2–50 were checked against the original for text and rendered-pixel equality.

Added for publication: the root recruiter-facing README; this note; reproduction and verification guides; third-party notices; `.gitignore`; `.gitattributes`; the provenance/source register; and `tools/portfolio_verify.py` and `tools/portfolio_restore.py`. These two named helpers do not change the original experimental algorithm. They enable evidence verification and safe restoration of archived responses.

`.gitattributes` preserves the bytes of frozen inputs/evidence when Git is used on Windows. `.gitignore` excludes local secrets, environments, caches, outputs, backup files and archives. Neither file can remove a secret already committed to Git history, and neither is a substitute for checking staged files.

## Deliberate omissions

Duplicate ZIPs, pilot/smoke-run output folders, pre-submission control bundles, a backup Python client, runtime logs and generated caches are omitted to keep the repository focused on the final study. The readable final appendices retain discussion of methodology and pilot work; the complete submitted archive remains the author's separate record.

The 38.6 MB full model-request payload JSONL is regenerable and omitted. Its submitted hash and byte count are retained in the provenance manifest, along with the original per-prompt hash and size CSVs. Full cleaned source texts and locked retrieved contexts remain included so prompt construction can be replayed exactly.

## Legacy utility warning

`tools/make_release_zip.py` is retained as submitted; **do not use it to package this public repository**. Its exclusion logic is not a complete public-distribution filter and does not implement the new `.gitignore` policy. In particular, generated outputs or future Git/workstation state may be included. Publish the reviewed Git tracked tree, not a fresh archive created indiscriminately from a working directory.

## What this copy does not assert

This package does not claim production readiness, independent ground-truth adjudication, statistical significance for a one-case accuracy difference, fresh provider inference, current API pricing, or a security certification. No university embargo or publication-clearance decision is made by the preparation process. No open-source licence has been selected on the author's behalf.
