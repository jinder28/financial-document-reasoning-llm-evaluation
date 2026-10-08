"""Cost guard prevents uncontrolled live API spend during the main experiment."""
from __future__ import annotations

from dataclasses import dataclass

from app.config.runtime_settings import ExperimentRuntimeSettings


@dataclass
class CostAccumulator:
    """Tracks estimated cost across smoke and full-live calls."""

    estimated_cost_usd: float = 0.0


class CostGuard:
    """Stops live execution if cost exceeds configured dissertation limits."""

    def __init__(self, runtime_settings: ExperimentRuntimeSettings) -> None:
        self.runtime_settings = runtime_settings
        self.cost_accumulator = CostAccumulator()

    def record_usage_and_assert_within_limits(self, usage_record: dict) -> float:
        """Adds one call estimate and enforces warning/hard ceilings."""
        input_tokens = int(usage_record.get("input_tokens") or usage_record.get("prompt_tokens") or 0)
        output_tokens = int(usage_record.get("output_tokens") or usage_record.get("completion_tokens") or 0)
        call_cost_usd = (
            input_tokens / 1_000_000 * self.runtime_settings.input_cost_usd_per_million_tokens
            + output_tokens / 1_000_000 * self.runtime_settings.output_cost_usd_per_million_tokens
        )
        self.cost_accumulator.estimated_cost_usd += call_cost_usd
        if self.runtime_settings.feature_toggles.enable_cost_guard:
            if self.cost_accumulator.estimated_cost_usd > self.runtime_settings.cost_hard_limit_usd:
                raise RuntimeError(
                    f"Hard cost limit exceeded: {self.cost_accumulator.estimated_cost_usd:.2f} USD"
                )
        return call_cost_usd
