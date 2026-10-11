"""Data preprocessing and harmonization module for EconLens AI.

Provides safe, transparent data cleaning, text trimming, numeric coercion,
reference period normalization, and wide-to-long transformation utilities.
Enforces strict anti-fabrication policies: missing values are never silently
replaced with zero or imputed without an explicit, disclosed policy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from src.data.schema import CANONICAL_COLUMNS, REQUIRED_COLUMNS, is_valid_reference_period
from src.utils.logging_config import get_logger

logger = get_logger("data.preprocessing")


# ==============================================================================
# Cleaning Report Container
# ==============================================================================
@dataclass
class CleaningReport:
    """Detailed summary of transformations applied during preprocessing."""

    original_rows: int = 0
    original_cols: int = 0
    final_rows: int = 0
    final_cols: int = 0
    columns_renamed: Dict[str, str] = field(default_factory=dict)
    trimmed_cells_count: int = 0
    numeric_coercion_failures: Dict[str, int] = field(default_factory=dict)
    missing_value_summary: Dict[str, int] = field(default_factory=dict)
    lineage_notes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Returns a human-readable summary of cleaning operations."""
        return (
            f"Cleaning Complete: {self.final_rows} rows x {self.final_cols} cols "
            f"(Original: {self.original_rows}x{self.original_cols}). "
            f"Renamed {len(self.columns_renamed)} cols, trimmed {self.trimmed_cells_count} cells, "
            f"numeric coercion issues: {sum(self.numeric_coercion_failures.values())}."
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to dictionary."""
        return {
            "original_rows": self.original_rows,
            "original_cols": self.original_cols,
            "final_rows": self.final_rows,
            "final_cols": self.final_cols,
            "columns_renamed": self.columns_renamed,
            "trimmed_cells_count": self.trimmed_cells_count,
            "numeric_coercion_failures": self.numeric_coercion_failures,
            "missing_value_summary": self.missing_value_summary,
            "lineage_notes": self.lineage_notes,
        }


# ==============================================================================
# Preprocessing Configuration
# ==============================================================================
@dataclass
class PreprocessingConfig:
    """Configuration parameters for dataset preprocessing."""

    standardize_column_names: bool = True
    trim_text_whitespace: bool = True
    coerce_numeric_values: bool = True
    preserve_raw_copy: bool = True
    allow_imputation: bool = False  # Strict default: NO silent imputation
    imputation_strategy: str = "none"
    scaling_method: str = "none"
    handle_outliers: bool = False
    normalize_geographic_names: bool = True
    feature_columns: List[str] = field(default_factory=list)
    id_columns: List[str] = field(
        default_factory=lambda: ["region_id", "region_name"]
    )


# ==============================================================================
# Pure Utility Functions
# ==============================================================================
def standardize_column_names(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Converts column names to lowercase, stripped, snake_case strings.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple of (new DataFrame with standardized column names, rename mapping dict).
    """
    cleaned_df = df.copy()
    rename_map: Dict[str, str] = {}

    for col in cleaned_df.columns:
        col_str = str(col).strip()
        # Replace non-alphanumeric characters with spaces, then consolidate into underscores
        normalized = re.sub(r"[^\w\s]", " ", col_str)
        snake_cased = re.sub(r"[\s_]+", "_", normalized).strip("_").lower()
        if snake_cased != col:
            rename_map[str(col)] = snake_cased

    if rename_map:
        cleaned_df = cleaned_df.rename(columns=rename_map)

    return cleaned_df, rename_map


def trim_text_columns(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, int]:
    """Trims leading and trailing whitespace from string/object columns.

    Args:
        df: Input DataFrame.
        columns: Specific columns to trim. If None, trims all object/string columns.

    Returns:
        Tuple of (new DataFrame with trimmed strings, total trimmed cells count).
    """
    cleaned_df = df.copy()
    target_cols = columns or [
        c for c in cleaned_df.columns if cleaned_df[c].dtype == "object"
    ]
    trimmed_count = 0

    for col in target_cols:
        if col not in cleaned_df.columns:
            continue

        def _trim_cell(val: Any) -> Any:
            nonlocal trimmed_count
            if isinstance(val, str):
                trimmed = val.strip()
                if trimmed != val:
                    trimmed_count += 1
                return trimmed
            return val

        cleaned_df[col] = cleaned_df[col].map(_trim_cell)

    return cleaned_df, trimmed_count


def coerce_numeric_column(
    df: pd.DataFrame,
    column: str,
) -> Tuple[pd.DataFrame, int]:
    """Safely converts a specified column to numeric (float), recording coercion failures.

    Missing values (NaN) remain NaN. Strings like 'N/A', '-', or malformed characters
    are coerced to NaN and counted.

    Args:
        df: Input DataFrame.
        column: Column name to convert.

    Returns:
        Tuple of (new DataFrame, count of unparseable coerced values).
    """
    cleaned_df = df.copy()
    if column not in cleaned_df.columns:
        return cleaned_df, 0

    initial_nulls = int(cleaned_df[column].isna().sum())
    coerced_series = pd.to_numeric(cleaned_df[column], errors="coerce")
    final_nulls = int(coerced_series.isna().sum())
    coerced_failures = max(0, final_nulls - initial_nulls)

    cleaned_df[column] = coerced_series
    return cleaned_df, coerced_failures


def parse_reference_period(period_str: Any) -> str:
    """Normalizes and validates reference period string representation.

    Accepts formats such as:
    - '2011' -> '2011'
    - '2021 - 2022' -> '2021-22' (standardized short form)
    - '2021-22' -> '2021-22'
    - 'Q1-2023' -> 'Q1-2023'

    Raises:
        ValueError: If the period format cannot be recognized.
    """
    if not isinstance(period_str, str):
        raise ValueError(f"Reference period must be string, got {type(period_str).__name__}")

    cleaned = period_str.strip()
    # Normalize spaced hyphens: e.g. '2021 - 22' -> '2021-22'
    cleaned = re.sub(r"\s*-\s*", "-", cleaned)

    # Convert full year range '2021-2022' to standard short form '2021-22' if second year is consecutive
    long_match = re.match(r"^(\d{4})-(\d{4})$", cleaned)
    if long_match:
        y1, y2 = int(long_match.group(1)), int(long_match.group(2))
        if y2 == y1 + 1:
            cleaned = f"{y1}-{str(y2)[2:]}"

    if not is_valid_reference_period(cleaned):
        raise ValueError(
            f"Invalid reference period '{period_str}'. Expected format like 'YYYY', 'YYYY-YY', or 'QX-YYYY'."
        )

    return cleaned


def wide_to_long_observations(
    df: pd.DataFrame,
    id_vars: List[str],
    indicator_mapping: Dict[str, Dict[str, str]],
    reference_period: str,
    source_id: str,
    default_geo_level: str = "district",
) -> pd.DataFrame:
    """Converts wide-format tables into the canonical long-form observation format.

    Args:
        df: Input wide-format DataFrame.
        id_vars: List of region identification columns (must contain at least 'region_id' and 'region_name').
        indicator_mapping: Dictionary mapping wide column name to indicator metadata dict:
            {
                "raw_col_name": {
                    "indicator_code": "LIT_RATE_TOT",
                    "indicator_name": "Total Literacy Rate",
                    "unit": "percentage"
                }
            }
        reference_period: Reference period for the observations (e.g. '2021-22').
        source_id: Registered source identifier (e.g. 'SRC_CENSUS_2011').
        default_geo_level: Geographic level (e.g. 'district').

    Returns:
        pd.DataFrame: Long-form canonical DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    for id_col in ["region_id", "region_name"]:
        if id_col not in id_vars or id_col not in df.columns:
            raise ValueError(f"id_vars must include '{id_col}' which must be present in the DataFrame.")

    target_cols = [c for c in indicator_mapping.keys() if c in df.columns]
    if not target_cols:
        raise ValueError("None of the columns specified in indicator_mapping were found in DataFrame.")

    rows: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        region_id = str(row["region_id"]).strip()
        region_name = str(row["region_name"]).strip()
        parent_region_id = (
            str(row["parent_region_id"]).strip()
            if "parent_region_id" in df.columns and pd.notna(row["parent_region_id"])
            else None
        )
        geo_level = (
            str(row["geographic_level"]).strip()
            if "geographic_level" in df.columns and pd.notna(row["geographic_level"])
            else default_geo_level
        )

        for raw_col in target_cols:
            raw_val = row[raw_col]
            meta = indicator_mapping[raw_col]

            # Coerce value
            try:
                num_val = float(raw_val) if pd.notna(raw_val) else None
            except (ValueError, TypeError):
                num_val = None

            obs = {
                "region_id": region_id,
                "region_name": region_name,
                "parent_region_id": parent_region_id,
                "geographic_level": geo_level,
                "indicator_code": meta["indicator_code"],
                "indicator_name": meta.get("indicator_name", meta["indicator_code"]),
                "value": num_val,
                "unit": meta.get("unit", "unknown"),
                "reference_period": reference_period,
                "source_id": source_id,
                "source_record_id": str(row.name),
                "collection_date": None,
                "quality_status": "raw",
                "notes": f"Converted from wide table column '{raw_col}'",
            }
            rows.append(obs)

    return pd.DataFrame(rows)


# ==============================================================================
# Preprocessing Pipeline
# ==============================================================================
class PreprocessingPipeline:
    """Reusable preprocessing and harmonization pipeline for regional data."""

    def __init__(self, config: Optional[PreprocessingConfig] = None) -> None:
        self.config = config or PreprocessingConfig()
        self._fitted_transformers: Dict[str, object] = {}

    def clean(self, raw_data: pd.DataFrame) -> Tuple[pd.DataFrame, CleaningReport]:
        """Applies configured cleaning transformations to a dataset without data loss.

        Returns:
            Tuple of (cleaned DataFrame, CleaningReport).
        """
        if not isinstance(raw_data, pd.DataFrame):
            raise TypeError(f"Expected DataFrame, got {type(raw_data).__name__}")

        orig_rows, orig_cols = raw_data.shape
        df = raw_data.copy()
        report = CleaningReport(
            original_rows=orig_rows,
            original_cols=orig_cols,
        )

        # 1. Standardize column names if enabled
        if self.config.standardize_column_names:
            df, rename_map = standardize_column_names(df)
            report.columns_renamed = rename_map
            if rename_map:
                report.lineage_notes.append(f"Standardized {len(rename_map)} column names.")

        # 2. Trim text columns
        if self.config.trim_text_whitespace:
            df, trimmed_count = trim_text_columns(df)
            report.trimmed_cells_count = trimmed_count
            if trimmed_count > 0:
                report.lineage_notes.append(f"Trimmed whitespace across {trimmed_count} text cells.")

        # 3. Numeric coercion on 'value' column if present
        if self.config.coerce_numeric_values and "value" in df.columns:
            df, num_fails = coerce_numeric_column(df, "value")
            if num_fails > 0:
                report.numeric_coercion_failures["value"] = num_fails
                report.lineage_notes.append(f"Coerced {num_fails} non-numeric values in 'value' column to NaN.")

        # 4. Standardize reference_period if present
        if "reference_period" in df.columns:
            normalized_periods = []
            for p in df["reference_period"]:
                if pd.notna(p):
                    try:
                        normalized_periods.append(parse_reference_period(str(p)))
                    except ValueError:
                        normalized_periods.append(str(p).strip())
                else:
                    normalized_periods.append(p)
            df["reference_period"] = normalized_periods

        # 5. Missing value audit (no silent zero replacement!)
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            if null_count > 0:
                report.missing_value_summary[col] = null_count

        report.final_rows, report.final_cols = df.shape
        logger.info(report.summary())
        return df, report

    def fit_transform(
        self, raw_data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, CleaningReport]:
        """Fits preprocessing parameters and cleans the input dataset."""
        return self.clean(raw_data)

    def transform(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Transforms incoming dataset using the configured cleaning pipeline."""
        cleaned_df, _ = self.clean(raw_data)
        return cleaned_df
