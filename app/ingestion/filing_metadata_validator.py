"""Filing metadata validation supports corpus-selection reproducibility checks."""
from __future__ import annotations

from collections import Counter


class FilingMetadataValidator:
    """Checks that corpus metadata remains one row per locked filing."""

    def validate_unique_filing_ids(self, filing_records: list[dict[str, str]]) -> list[str]:
        """Reports duplicate filing IDs before corpus preparation proceeds."""
        filing_id_counts = Counter(record.get("filing_id", "") for record in filing_records)
        return [filing_id for filing_id, count in filing_id_counts.items() if count > 1]
