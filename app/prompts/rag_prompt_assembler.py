"""RAG prompt assembly limits GPT-5.5 context to retrieved filing chunks."""
from __future__ import annotations

from app.prompts.prompt_template_registry import PromptTemplateRegistry
from app.rag.rag_context_loader import RagContextLoader


class RagPromptAssembler:
    """Builds retrieved-context prompts for the RAG experimental condition."""

    def __init__(self, prompt_template_registry: PromptTemplateRegistry, rag_context_loader: RagContextLoader) -> None:
        self.prompt_template_registry = prompt_template_registry
        self.rag_context_loader = rag_context_loader

    def assemble_user_prompt(self, queue_record: dict[str, str], context_record: dict) -> str:
        """Creates one RAG prompt from the locked queue and frozen RAG context."""
        context_text = self.rag_context_loader.build_context_text_for_run(context_record)
        return self.prompt_template_registry.get_rag_user_template().format(
            case_id=queue_record.get("case_id", ""),
            filing_id=queue_record.get("filing_id", ""),
            company=queue_record.get("company", ""),
            report_date=queue_record.get("report_date", ""),
            claim_text=queue_record.get("claim_text", ""),
            context_text=context_text,
        )
