"""Data loading and dataset registry module for EconLens AI.

Responsible for discovering, loading, and isolating regional datasets across
raw, processed, sample, and metadata storage layers with strict path validation,
error classification, and format support.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from config.settings import Settings, get_settings
from src.utils.logging_config import get_logger

logger = get_logger("data.data_loader")

# Supported file formats
SUPPORTED_EXTENSIONS = {".csv", ".json"}


# ==============================================================================
# Custom Exceptions for Granular Diagnostic Feedback
# ==============================================================================
class DataLoaderError(Exception):
    """Base exception for all data loading failures."""


class DatasetNotFoundError(DataLoaderError, FileNotFoundError):
    """Raised when the requested dataset file does not exist on disk."""


class UnsupportedFormatError(DataLoaderError, ValueError):
    """Raised when an unsupported file extension or format is supplied."""


class EmptyDatasetError(DataLoaderError, ValueError):
    """Raised when a dataset file is completely empty or contains zero rows."""


class MalformedDataError(DataLoaderError, ValueError):
    """Raised when a dataset file contains unparseable or corrupted content."""


# ==============================================================================
# Dataset Metadata Container (Backward-Compatible)
# ==============================================================================
@dataclass(frozen=True)
class DatasetMetadata:
    """Metadata describing an ingested regional dataset."""

    name: str
    path: Path
    file_format: str
    is_synthetic: bool
    description: str = ""
    geographic_level: str = "district"
    reference_year: Optional[int] = None


# ==============================================================================
# Standalone Read-Only File Loading Functions
# ==============================================================================
def load_csv(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    **kwargs,
) -> pd.DataFrame:
    """Safely loads a CSV file into a pandas DataFrame.

    Validates file existence, format, non-emptiness, and preserves raw file integrity.

    Args:
        file_path: Path to the CSV file.
        encoding: File character encoding (default 'utf-8').
        **kwargs: Additional parameters passed to pd.read_csv.

    Returns:
        pd.DataFrame: The loaded tabular data.

    Raises:
        DatasetNotFoundError: If the file does not exist.
        UnsupportedFormatError: If the file extension is not .csv.
        EmptyDatasetError: If the file has 0 bytes or zero data rows.
        MalformedDataError: If the CSV syntax is corrupted or unparseable.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        logger.error("Dataset file not found at %s", path)
        raise DatasetNotFoundError(f"File not found: {path}")

    if not path.is_file():
        logger.error("Path is a directory, not a file: %s", path)
        raise DataLoaderError(f"Path is not a regular file: {path}")

    if path.suffix.lower() != ".csv":
        logger.error("Unsupported file extension '%s' for CSV loader: %s", path.suffix, path)
        raise UnsupportedFormatError(
            f"Expected a .csv file, got '{path.suffix}'. Supported extensions: {SUPPORTED_EXTENSIONS}"
        )

    if path.stat().st_size == 0:
        logger.error("File is 0 bytes (empty): %s", path)
        raise EmptyDatasetError(f"Dataset file is empty (0 bytes): {path}")

    try:
        df = pd.read_csv(path, encoding=encoding, **kwargs)
    except pd.errors.EmptyDataError as exc:
        logger.error("CSV file contains no readable data: %s", path)
        raise EmptyDatasetError(f"CSV contains no readable columns or rows: {path}") from exc
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
        logger.error("Malformed CSV data in %s: %s", path, exc)
        raise MalformedDataError(f"Failed to parse CSV file '{path.name}': {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error while reading CSV file %s", path)
        raise DataLoaderError(f"Unexpected error reading {path.name}: {exc}") from exc

    if df.empty:
        logger.warning("CSV file '%s' has headers but 0 observation rows.", path.name)
        raise EmptyDatasetError(f"CSV file contains headers but zero data rows: {path.name}")

    logger.debug("Successfully loaded CSV '%s' with %d rows and %d columns.", path.name, len(df), len(df.columns))
    return df


def load_json(
    file_path: Union[str, Path],
    encoding: str = "utf-8",
    **kwargs,
) -> pd.DataFrame:
    """Safely loads a JSON file into a pandas DataFrame.

    Supports JSON arrays of records or record dictionaries.

    Args:
        file_path: Path to the JSON file.
        encoding: File character encoding (default 'utf-8').
        **kwargs: Additional parameters passed to pd.read_json or pd.DataFrame.

    Returns:
        pd.DataFrame: The loaded tabular data.

    Raises:
        DatasetNotFoundError: If the file does not exist.
        UnsupportedFormatError: If the file extension is not .json.
        EmptyDatasetError: If the file is empty.
        MalformedDataError: If JSON parsing fails.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        logger.error("JSON file not found at %s", path)
        raise DatasetNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise DataLoaderError(f"Path is not a regular file: {path}")

    if path.suffix.lower() != ".json":
        raise UnsupportedFormatError(
            f"Expected a .json file, got '{path.suffix}'. Supported extensions: {SUPPORTED_EXTENSIONS}"
        )

    if path.stat().st_size == 0:
        raise EmptyDatasetError(f"JSON file is empty (0 bytes): {path}")

    try:
        content = path.read_text(encoding=encoding).strip()
        if not content:
            raise EmptyDatasetError(f"JSON file contains empty string: {path}")
        data = json.loads(content)
        if isinstance(data, list):
            df = pd.DataFrame(data, **kwargs)
        elif isinstance(data, dict):
            # Check if dict of records (like registry) or column-oriented
            if all(isinstance(v, dict) for v in data.values()):
                df = pd.DataFrame(list(data.values()))
            else:
                df = pd.DataFrame([data])
        else:
            raise MalformedDataError(f"JSON structure must be an object or array: {path}")
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        raise MalformedDataError(f"Failed to parse JSON file '{path.name}': {exc}") from exc

    if df.empty:
        raise EmptyDatasetError(f"JSON file contains no observation rows: {path.name}")

    logger.debug("Successfully loaded JSON '%s' with %d rows and %d columns.", path.name, len(df), len(df.columns))
    return df


# ==============================================================================
# Unified DataLoader Manager
# ==============================================================================
class DataLoader:
    """Manages discovery and safe loading of regional datasets across storage tiers."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def list_available_raw_datasets(self) -> List[Path]:
        """Lists valid data files in the raw data directory."""
        if not self.settings.raw_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.raw_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep" and not p.name.startswith(".")
        ]

    def list_available_processed_datasets(self) -> List[Path]:
        """Lists valid data files in the processed data directory."""
        if not self.settings.processed_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.processed_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep" and not p.name.startswith(".")
        ]

    def list_available_sample_datasets(self) -> List[Path]:
        """Lists files in the isolated sample demonstration directory."""
        if not self.settings.sample_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.sample_data_dir.iterdir()
            if p.is_file()
            and p.name != ".gitkeep"
            and not p.name.startswith(".")
            and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    def list_available_metadata_files(self) -> List[Path]:
        """Lists files in the metadata directory."""
        if not self.settings.metadata_data_dir.exists():
            return []
        return [
            p
            for p in self.settings.metadata_data_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep" and not p.name.startswith(".")
        ]

    def has_verified_datasets(self) -> bool:
        """Returns True if any verified processed datasets exist."""
        return len(self.list_available_processed_datasets()) > 0

    def load_file(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8",
        **kwargs,
    ) -> pd.DataFrame:
        """Loads a file by detecting its extension (CSV or JSON).

        Args:
            file_path: Path to the target file.
            encoding: File character encoding.
            **kwargs: Extra arguments passed to loader.

        Returns:
            pd.DataFrame: Loaded DataFrame.
        """
        path = Path(file_path).resolve()
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return load_csv(path, encoding=encoding, **kwargs)
        if suffix == ".json":
            return load_json(path, encoding=encoding, **kwargs)

        raise UnsupportedFormatError(
            f"Unsupported file format '{suffix}'. Supported formats are: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    def load_dataset(
        self,
        metadata: DatasetMetadata,
        encoding: str = "utf-8",
        **kwargs,
    ) -> pd.DataFrame:
        """Loads a dataset from disk using DatasetMetadata guardrails.

        Args:
            metadata: Dataset metadata container.
            encoding: Character encoding.

        Returns:
            pd.DataFrame: Tabular dataset.
        """
        logger.info(
            "Loading dataset '%s' (synthetic=%s) from %s",
            metadata.name,
            metadata.is_synthetic,
            metadata.path,
        )
        return self.load_file(metadata.path, encoding=encoding, **kwargs)
