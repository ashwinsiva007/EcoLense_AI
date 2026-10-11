"""Data ingestion, validation, and preprocessing package for EconLens AI."""

from src.data.data_loader import (
    DataLoader,
    DataLoaderError,
    DatasetMetadata,
    DatasetNotFoundError,
    EmptyDatasetError,
    MalformedDataError,
    UnsupportedFormatError,
    load_csv,
    load_json,
)
from src.data.preprocessing import (
    CleaningReport,
    PreprocessingConfig,
    PreprocessingPipeline,
    coerce_numeric_column,
    parse_reference_period,
    standardize_column_names,
    trim_text_columns,
    wide_to_long_observations,
)
from src.data.quality_report import (
    format_quality_report_markdown,
    generate_quality_report,
)
from src.data.schema import (
    CANONICAL_COLUMNS,
    OPTIONAL_COLUMNS,
    PRIMARY_KEY_COLUMNS,
    REQUIRED_COLUMNS,
    VALID_GEOGRAPHIC_LEVELS,
    is_valid_geographic_level,
    is_valid_reference_period,
)
from src.data.source_registry import DatasetSource, SourceRegistry
from src.data.validation import DataValidator, ValidationResult

__all__ = [
    # Data Loading
    "DataLoader",
    "DatasetMetadata",
    "load_csv",
    "load_json",
    "DataLoaderError",
    "DatasetNotFoundError",
    "UnsupportedFormatError",
    "EmptyDatasetError",
    "MalformedDataError",
    # Schema
    "CANONICAL_COLUMNS",
    "REQUIRED_COLUMNS",
    "OPTIONAL_COLUMNS",
    "PRIMARY_KEY_COLUMNS",
    "VALID_GEOGRAPHIC_LEVELS",
    "is_valid_reference_period",
    "is_valid_geographic_level",
    # Validation
    "DataValidator",
    "ValidationResult",
    # Preprocessing
    "PreprocessingPipeline",
    "PreprocessingConfig",
    "CleaningReport",
    "standardize_column_names",
    "trim_text_columns",
    "coerce_numeric_column",
    "parse_reference_period",
    "wide_to_long_observations",
    # Source Registry
    "DatasetSource",
    "SourceRegistry",
    # Quality Report
    "generate_quality_report",
    "format_quality_report_markdown",
]
