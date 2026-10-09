"""Data loading and dataset registry module for EconLens AI.

Responsible for discovering, loading, and isolating regional datasets across
raw, processed, and sample storage layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from config.settings import Settings, get_settings
from src.utils.logging_config import get_logger

logger = get_logger("data.data_loader")


@dataclass(frozen=True)
class DatasetMetadata:
    """Metadata describing an ingested regional dataset."""

    name: str
    path: Path
    file_format: str
    is_synthetic: bool
    description: str = ""
    geographic_level: str = "district"  # e.g., district, state, national
    reference_year: Optional[int] = None


class DataLoader:
    """Manages discovery and loading of regional datasets."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def list_available_raw_datasets(self) -> List[Path]:
        """Lists files in the raw data directory."""
        if not self.settings.raw_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.raw_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep"
        ]

    def list_available_processed_datasets(self) -> List[Path]:
        """Lists files in the processed data directory."""
        if not self.settings.processed_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.processed_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep"
        ]

    def list_available_sample_datasets(self) -> List[Path]:
        """Lists files in the isolated sample demonstration directory."""
        if not self.settings.sample_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.sample_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep"
        ]

    def has_verified_datasets(self) -> bool:
        """Returns True if any verified processed or raw datasets exist."""
        return (
            len(self.list_available_processed_datasets()) > 0
            or len(self.list_available_raw_datasets()) > 0
        )

    def load_dataset(self, metadata: DatasetMetadata):
        """Loads a dataset from disk with verification guardrails.

        NOTE: Concrete parsing and transformation algorithms will be implemented
        in subsequent development stages once study geography and data schemas are finalized.
        """
        logger.info(
            "Request to load dataset '%s' (synthetic=%s) from %s",
            metadata.name,
            metadata.is_synthetic,
            metadata.path,
        )
        if not metadata.path.exists():
            raise FileNotFoundError(f"Dataset not found at {metadata.path}")

        # Future implementation will handle tabular, CSV, Parquet, and GeoJSON formats
        raise NotImplementedError(
            "Concrete dataset loading logic is scheduled for Stage 2 (Data Integration & Validation)."
        )
