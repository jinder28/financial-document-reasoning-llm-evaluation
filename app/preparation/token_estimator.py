"""Token estimator provides lightweight prompt-size evidence without API calls."""
from __future__ import annotations


class TokenEstimator:
    """Estimates token counts for dry-run feasibility checks."""

    def estimate_tokens_from_text(self, text_value: str) -> int:
        """Approximates tokens from characters for conservative planning evidence."""
        return max(1, len(text_value) // 4)
