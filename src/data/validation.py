"""Data validation and integrity auditing module for EconLens AI.

Ensures incoming regional datasets adhere to defined schemas, valid geographic
identifiers, expected data types, acceptable indicator bounds, and consistent units.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import pandas as pd

from src.data.schema import (
    CANONICAL_COLUMNS,
    OPTIONAL_COLUMNS,
    PRIMARY_KEY_COLUMNS,
    REQUIRED_COLUMNS,
    VALID_GEOGRAPHIC_LEVELS,
    get_indicator_bounds,
    is_valid_geographic_level,
    is_valid_reference_period,
)
from src.data.source_registry import SourceRegistry
from src.utils.logging_config import get_logger

logger = get_logger("data.validation")


@dataclass
class ValidationResult:
    """Outcome of a dataset validation pass with comprehensive metrics."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    duplicate_count: int = 0
    missing_value_counts: Dict[str, int] = field(default_factory=dict)
    type_conversion_failures: Dict[str, int] = field(default_factory=dict)
    invalid_value_counts: Dict[str, int] = field(default_factory=dict)
    schema_details: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Returns a concise human-readable validation summary."""
        status = "PASSED" if self.is_valid else "FAILED"
        return (
            f"Validation {status}: {self.row_count} rows, {self.column_count} columns. "
            f"Errors: {len(self.errors)}, Warnings: {len(self.warnings)}."
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the result to a serializable dictionary."""
        return {
            "is_valid": self.is_valid,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_count": self.duplicate_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "missing_value_counts": self.missing_value_counts,
            "type_conversion_failures": self.type_conversion_failures,
            "invalid_value_counts": self.invalid_value_counts,
            "schema_details": self.schema_details,
        }


class DataValidator:
    """Validates raw and processed regional economic datasets."""

    def __init__(
        self,
        required_columns: Optional[List[str]] = None,
        expected_geo_level: Optional[str] = None,
        source_registry: Optional[SourceRegistry] = None,
        custom_bounds_rules: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes the validator with configurable schema rules.

        Args:
            required_columns: Override of mandatory columns. Defaults to canonical REQUIRED_COLUMNS.
            expected_geo_level: If specified, enforces that all rows belong to this level.
            source_registry: Optional SourceRegistry instance for validating source_ids.
            custom_bounds_rules: Optional indicator-specific numeric bounds overrides.
        """
        self.required_columns = required_columns or list(REQUIRED_COLUMNS)
        self.expected_geo_level = expected_geo_level
        self.source_registry = source_registry
        self.custom_bounds_rules = custom_bounds_rules or {}

    def validate_schema(self, data: Any) -> ValidationResult:
        """Validates that a dataset conforms to required structural schemas.

        Maintains backwards compatibility with Stage 1 validator while delegating
        to full canonical integrity checks.
        """
        return self.validate_canonical(data)

    def validate_canonical(self, df: Any) -> ValidationResult:
        """Executes full diagnostic validation on a canonical regional dataset.

        Performs:
        1. DataFrame structure and emptiness check.
        2. Required columns existence check.
        3. Schema drift detection (unexpected columns).
        4. Missing region identifier detection (region_id).
        5. Missing indicator code detection (indicator_code).
        6. Missing value auditing across all columns.
        7. Numeric validity and finite check for 'value' column.
        8. Geographic level validity check against supported hierarchy.
        9. Reference period format validation.
        10. Primary key duplicate detection (region_id, indicator_code, reference_period).
        11. Indicator unit consistency audit (same indicator having conflicting units).
        12. Source registry identifier verification.
        13. Indicator-specific value bounds validation.

        Args:
            df: The pandas DataFrame to validate.

        Returns:
            ValidationResult: Detailed diagnostic report.
        """
        errors: List[str] = []
        warnings: List[str] = []
        missing_value_counts: Dict[str, int] = {}
        type_failures: Dict[str, int] = {}
        invalid_value_counts: Dict[str, int] = {}
        schema_details: Dict[str, Any] = {}

        # 1. Type and empty checks
        if not isinstance(df, pd.DataFrame):
            errors.append(f"Expected pandas DataFrame, got {type(df).__name__}.")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                row_count=0,
                column_count=0,
            )

        row_count, column_count = df.shape
        if row_count == 0:
            errors.append("Dataset contains 0 rows (empty dataset).")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                row_count=0,
                column_count=column_count,
            )

        df_cols = list(df.columns)
        schema_details["columns_found"] = df_cols

        # 2. Required columns check
        missing_required = [c for c in self.required_columns if c not in df_cols]
        if missing_required:
            errors.append(f"Missing mandatory required column(s): {missing_required}")

        # 3. Schema drift / unexpected columns
        unexpected_cols = [c for c in df_cols if c not in CANONICAL_COLUMNS]
        if unexpected_cols:
            warnings.append(
                f"Dataset contains unexpected extra column(s) not in canonical schema: {unexpected_cols}"
            )
            schema_details["unexpected_columns"] = unexpected_cols

        # 4. Missing optional columns (informational warning)
        missing_optional = [c for c in OPTIONAL_COLUMNS if c not in df_cols]
        if missing_optional:
            warnings.append(f"Optional contextual column(s) omitted: {missing_optional}")
            schema_details["omitted_optional_columns"] = missing_optional

        # If required columns are missing, we cannot perform row-level column checks reliably
        if missing_required:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                row_count=row_count,
                column_count=column_count,
                schema_details=schema_details,
            )

        # 5. Missing value audit across all present columns
        for col in df_cols:
            null_count = int(df[col].isna().sum())
            if null_count > 0:
                missing_value_counts[col] = null_count
                if col in self.required_columns and col not in ("value",):
                    errors.append(f"Required column '{col}' contains {null_count} null/missing value(s).")

        # 6. Missing region identifiers (region_id)
        if "region_id" in df_cols:
            empty_region_mask = (
                df["region_id"].isna()
                | (df["region_id"].astype(str).str.strip() == "")
                | (df["region_id"].astype(str).str.lower() == "nan")
            )
            empty_regions = int(empty_region_mask.sum())
            if empty_regions > 0:
                errors.append(f"Column 'region_id' contains {empty_regions} blank or null identifier(s).")
                invalid_value_counts["region_id_blank"] = empty_regions

        # 7. Missing indicator codes (indicator_code)
        if "indicator_code" in df_cols:
            empty_ind_mask = (
                df["indicator_code"].isna()
                | (df["indicator_code"].astype(str).str.strip() == "")
                | (df["indicator_code"].astype(str).str.lower() == "nan")
            )
            empty_inds = int(empty_ind_mask.sum())
            if empty_inds > 0:
                errors.append(f"Column 'indicator_code' contains {empty_inds} blank or null code(s).")
                invalid_value_counts["indicator_code_blank"] = empty_inds

        # 8. Numeric validity and finite check for 'value' column
        if "value" in df_cols:
            non_numeric_count = 0
            infinite_count = 0
            null_value_count = int(df["value"].isna().sum())

            # Attempt numeric conversion to inspect invalid values
            converted_vals = pd.to_numeric(df["value"], errors="coerce")
            coerced_nan_count = int(converted_vals.isna().sum())
            non_numeric_count = coerced_nan_count - null_value_count

            # Check for infinite numbers
            infinite_mask = converted_vals.apply(lambda x: math.isinf(x) if pd.notna(x) else False)
            infinite_count = int(infinite_mask.sum())

            if non_numeric_count > 0:
                errors.append(f"Column 'value' contains {non_numeric_count} non-numeric string value(s).")
                type_failures["value_non_numeric"] = non_numeric_count

            if infinite_count > 0:
                errors.append(f"Column 'value' contains {infinite_count} non-finite infinite value(s).")
                invalid_value_counts["value_infinite"] = infinite_count

            if null_value_count > 0:
                # We record missing values as warning/audit rather than silent 0 replacement
                warnings.append(
                    f"Column 'value' contains {null_value_count} missing observation(s). "
                    "These must not be silently imputed or converted to zero."
                )

        # 9. Geographic level validation
        if "geographic_level" in df_cols:
            invalid_geo_levels = set()
            for val in df["geographic_level"].dropna().unique():
                val_str = str(val).strip().lower()
                if not is_valid_geographic_level(val_str):
                    invalid_geo_levels.add(str(val))
                elif self.expected_geo_level and val_str != self.expected_geo_level.strip().lower():
                    errors.append(
                        f"Row geographic level '{val_str}' does not match expected level '{self.expected_geo_level}'."
                    )

            if invalid_geo_levels:
                errors.append(
                    f"Unsupported geographic level(s) found: {sorted(invalid_geo_levels)}. "
                    f"Supported levels are: {sorted(VALID_GEOGRAPHIC_LEVELS)}"
                )
                invalid_value_counts["invalid_geographic_levels"] = len(invalid_geo_levels)

        # 10. Reference period format validation
        if "reference_period" in df_cols:
            invalid_periods = set()
            for val in df["reference_period"].dropna().unique():
                val_str = str(val).strip()
                if not is_valid_reference_period(val_str):
                    invalid_periods.add(str(val))

            if invalid_periods:
                errors.append(
                    f"Invalid reference period format(s) detected: {sorted(invalid_periods)}. "
                    "Accepted formats include 'YYYY', 'YYYY-YY', 'YYYY-YYYY', or 'QX-YYYY'."
                )
                invalid_value_counts["invalid_reference_periods"] = len(invalid_periods)

        # 11. Duplicate observation keys (region_id, indicator_code, reference_period)
        pk_cols = [c for c in PRIMARY_KEY_COLUMNS if c in df_cols]
        duplicate_count = 0
        if len(pk_cols) == len(PRIMARY_KEY_COLUMNS):
            # Find duplicate rows based on primary key
            pk_series = df.duplicated(subset=pk_cols, keep=False)
            duplicate_count = int(pk_series.sum())
            if duplicate_count > 0:
                sample_dupes = (
                    df[pk_series][pk_cols]
                    .drop_duplicates()
                    .head(3)
                    .to_dict(orient="records")
                )
                errors.append(
                    f"Duplicate observation key(s) detected across {duplicate_count} rows. "
                    f"Primary key: {pk_cols}. Examples: {sample_dupes}"
                )

        # 12. Indicator unit consistency audit
        if "indicator_code" in df_cols and "unit" in df_cols:
            unit_grouped = df.groupby("indicator_code")["unit"].nunique()
            inconsistent_units = unit_grouped[unit_grouped > 1]
            if not inconsistent_units.empty:
                bad_indicators = inconsistent_units.index.tolist()
                errors.append(
                    f"Inconsistent measurement units detected for indicator(s): {bad_indicators}. "
                    "Each indicator code must use a single uniform measurement unit."
                )
                invalid_value_counts["inconsistent_indicator_units"] = len(bad_indicators)

        # 13. Source registry ID verification
        if "source_id" in df_cols and self.source_registry:
            dataset_source_ids = set(df["source_id"].dropna().astype(str).unique())
            unrecognized_sources = [
                s_id for s_id in dataset_source_ids if not self.source_registry.has(s_id)
            ]
            if unrecognized_sources:
                warnings.append(
                    f"Source ID(s) {unrecognized_sources} are not registered in the Source Registry. "
                    "Register all candidate datasets to maintain verified provenance."
                )
                schema_details["unrecognized_source_ids"] = unrecognized_sources

        # 14. Indicator-specific numeric bounds validation
        if "indicator_code" in df_cols and "unit" in df_cols and "value" in df_cols:
            out_of_bounds_count = 0
            for idx, row in df.iterrows():
                ind_code = str(row["indicator_code"]).strip()
                unit = str(row["unit"]).strip()
                raw_val = row["value"]

                try:
                    num_val = float(raw_val)
                    if pd.isna(num_val) or math.isnan(num_val):
                        continue
                except (ValueError, TypeError):
                    continue

                min_b, max_b = get_indicator_bounds(ind_code, unit)
                # Check user override if present
                if ind_code in self.custom_bounds_rules:
                    min_b, max_b = self.custom_bounds_rules[ind_code]

                if min_b is not None and num_val < min_b:
                    out_of_bounds_count += 1
                    errors.append(
                        f"Out-of-bounds value {num_val} for indicator '{ind_code}' (unit: '{unit}'). "
                        f"Expected value >= {min_b}."
                    )
                    break  # Avoid flood of repeated messages

                if max_b is not None and num_val > max_b:
                    out_of_bounds_count += 1
                    errors.append(
                        f"Out-of-bounds value {num_val} for indicator '{ind_code}' (unit: '{unit}'). "
                        f"Expected value <= {max_b}."
                    )
                    break

            if out_of_bounds_count > 0:
                invalid_value_counts["out_of_bounds_values"] = out_of_bounds_count

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            row_count=row_count,
            column_count=column_count,
            duplicate_count=duplicate_count,
            missing_value_counts=missing_value_counts,
            type_conversion_failures=type_failures,
            invalid_value_counts=invalid_value_counts,
            schema_details=schema_details,
        )
