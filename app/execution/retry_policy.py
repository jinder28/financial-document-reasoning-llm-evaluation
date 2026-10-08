"""Retry policy limits reruns to technical failures, not unexpected labels."""
from __future__ import annotations

import time
from typing import Callable


class RetryPolicy:
    """Retries transport/schema failures while preserving experimental integrity."""

    def __init__(self, maximum_retry_attempts: int) -> None:
        self.maximum_retry_attempts = maximum_retry_attempts

    def execute_with_retries(self, operation_name: str, operation: Callable[[], dict]) -> dict:
        """Executes an operation with bounded retries and explicit failure reason."""
        last_exception: Exception | None = None
        for attempt_index in range(self.maximum_retry_attempts + 1):
            try:
                result_record = operation()
                result_record["retry_attempts_used"] = attempt_index
                return result_record
            except Exception as operation_error:  # noqa: BLE001 - logged as evidence by caller.
                last_exception = operation_error
                if attempt_index >= self.maximum_retry_attempts:
                    break
                time.sleep(2 * (attempt_index + 1))
        raise RuntimeError(f"{operation_name} failed after retries: {last_exception}") from last_exception
