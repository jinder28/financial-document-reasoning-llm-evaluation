"""Section inventory builder checks 10-K structure coverage for each filing."""
from __future__ import annotations

import re
from pathlib import Path

from app.common.csv_table import write_csv_records


class SectionInventoryBuilder:
    """Locates major 10-K Item sections in clean filing text."""

    section_patterns = {
        "Item 1": r"\bItem\s+1\.?\s+Business\b",
        "Item 1A": r"\bItem\s+1A\.?\s+Risk Factors\b",
        "Item 7": r"\bItem\s+7\.?\s+Management",
        "Item 7A": r"\bItem\s+7A\.?\s+Quantitative",
        "Item 8": r"\bItem\s+8\.?\s+Financial Statements",
    }

    def build_section_inventory_records(self, clean_text_directory: Path) -> list[dict[str, object]]:
        """Creates section-position evidence for each clean 10-K filing."""
        inventory_records: list[dict[str, object]] = []
        for clean_text_file_path in sorted(clean_text_directory.glob("*.txt")):
            clean_text = clean_text_file_path.read_text(encoding="utf-8", errors="replace")
            filing_id = clean_text_file_path.stem.split("_")[0]
            for section_name, section_pattern in self.section_patterns.items():
                match = re.search(section_pattern, clean_text, flags=re.IGNORECASE)
                inventory_records.append(
                    {
                        "filing_id": filing_id,
                        "source_file": clean_text_file_path.name,
                        "section_name": section_name,
                        "found": "YES" if match else "NO",
                        "char_start": match.start() if match else "",
                    }
                )
        return inventory_records

    def write_section_inventory(self, output_csv_path: Path, inventory_records: list[dict[str, object]]) -> None:
        """Writes section coverage evidence for methodology audit."""
        write_csv_records(output_csv_path, inventory_records, ["filing_id", "source_file", "section_name", "found", "char_start"])
