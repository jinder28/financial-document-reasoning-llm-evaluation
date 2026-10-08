"""Error taxonomy template supports qualitative analysis after scoring."""
from __future__ import annotations

from pathlib import Path

from app.common.csv_table import write_csv_records


class ErrorTaxonomyTemplateWriter:
    """Creates the manual coding template for LC/RAG error pattern analysis."""

    def write_error_taxonomy_template(self, output_csv_path: Path) -> None:
        """Writes predefined error categories aligned with Chapter 3 methodology."""
        error_type_records = [
            {"error_code": "missed_inconsistency", "description": "Model failed to identify a contradiction."},
            {"error_code": "false_inconsistency", "description": "Model marked a supported claim as contradicted."},
            {"error_code": "unsupported_claim_acceptance", "description": "Model accepted a claim lacking filing support."},
            {"error_code": "unsupported_causal_inference", "description": "Model inferred causal explanation not established by filing evidence."},
            {"error_code": "numeric_mismatch", "description": "Model mishandled a disclosed number, date, or period."},
            {"error_code": "hallucinated_justification", "description": "Model cited or invented support not present in supplied evidence."},
            {"error_code": "over_cautious_insufficient_evidence", "description": "Model abstained despite sufficient supplied filing evidence."},
            {"error_code": "schema_failure", "description": "Model output failed the required JSON schema."},
            {"error_code": "reference_invalidity", "description": "Model evidence reference did not point to supplied filing evidence."},
            {"error_code": "retrieval_miss", "description": "RAG retrieval omitted necessary evidence."},
            {"error_code": "retrieval_noise", "description": "RAG retrieval included distracting or weakly relevant evidence."},
            {"error_code": "chunk_boundary_fragmentation", "description": "RAG chunk boundaries split needed evidence."},
            {"error_code": "long_context_attention_failure", "description": "Long-context condition had evidence but failed to use it."},
            {"error_code": "long_context_position_sensitivity", "description": "Long-context failure plausibly linked to evidence position."},
        ]
        write_csv_records(output_csv_path, error_type_records, ["error_code", "description"])
