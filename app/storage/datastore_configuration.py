"""Datastore configuration isolates future storage choices from experiment logic."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatastoreConfiguration:
    """Records the active artefact-store implementation for reproducibility logs."""

    datastore_provider: str = "local_file"
    datastore_description: str = "Mounted local files are used for dissertation evidence capture."
