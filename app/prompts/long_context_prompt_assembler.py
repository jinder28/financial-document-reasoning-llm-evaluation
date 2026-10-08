"""Long-context prompt assembly exposes the full cleaned filing to GPT-5.5."""
from __future__ import annotations

from pathlib import Path

from app.prompts.prompt_template_registry import PromptTemplateRegistry


class LongContextPromptAssembler:
    """Builds full-filing prompts for the long-context experimental condition."""

    def __init__(self, prompt_template_registry: PromptTemplateRegistry) -> None:
        self.prompt_template_registry = prompt_template_registry

    def assemble_user_prompt(self, queue_record: dict[str, str], clean_text_directory: Path) -> str:
        """Creates one long-context prompt from the locked queue and clean filing."""
        source_file = queue_record.get("source_file", "")
        clean_text_file_path = clean_text_directory / source_file
        context_text = clean_text_file_path.read_text(encoding="utf-8", errors="replace")
        return self.prompt_template_registry.get_long_context_user_template().format(
            case_id=queue_record.get("case_id", ""),
            filing_id=queue_record.get("filing_id", ""),
            company=queue_record.get("company", ""),
            report_date=queue_record.get("report_date", ""),
            claim_text=queue_record.get("claim_text", ""),
            context_text=context_text,
        )
