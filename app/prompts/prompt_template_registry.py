"""Prompt templates keep LC and RAG condition instructions consistent."""
from __future__ import annotations


class PromptTemplateRegistry:
    """Supplies model-facing instructions for evidence-grounded classification."""

    def get_system_instruction(self) -> str:
        """Defines the model role for SEC 10-K inconsistency detection."""
        return (
            "You are evaluating SEC 10-K filing evidence for a controlled academic experiment. "
            "Classify the claim using only the provided filing evidence. Do not use outside knowledge. "
            "Return only valid JSON matching the required schema."
        )

    def get_long_context_user_template(self) -> str:
        """Provides the full-filing prompt template for the long-context condition."""
        return (
            "Experiment condition: Long_Context\n"
            "Case ID: {case_id}\n"
            "Filing ID: {filing_id}\n"
            "Company: {company}\n"
            "Report date: {report_date}\n\n"
            "Claim to classify:\n{claim_text}\n\n"
            "Allowed labels:\n"
            "- Supported: the filing evidence supports the claim.\n"
            "- Contradicted: the filing evidence conflicts with the claim.\n"
            "- Insufficient Evidence: the provided filing evidence does not establish the claim.\n\n"
            "Full cleaned SEC 10-K filing evidence:\n{context_text}\n\n"
            "Return JSON only."
        )

    def get_rag_user_template(self) -> str:
        """Provides the retrieved-chunk prompt template for the RAG condition."""
        return (
            "Experiment condition: RAG\n"
            "Case ID: {case_id}\n"
            "Filing ID: {filing_id}\n"
            "Company: {company}\n"
            "Report date: {report_date}\n\n"
            "Claim to classify:\n{claim_text}\n\n"
            "Allowed labels:\n"
            "- Supported: the retrieved filing evidence supports the claim.\n"
            "- Contradicted: the retrieved filing evidence conflicts with the claim.\n"
            "- Insufficient Evidence: the retrieved filing evidence does not establish the claim.\n\n"
            "Retrieved SEC 10-K evidence chunks:\n{context_text}\n\n"
            "Return JSON only."
        )
