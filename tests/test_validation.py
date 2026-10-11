"""Tests for data validation module, schema enforcement, bounds, and duplicate detection."""

import pandas as pd
import pytest

from src.data.data_loader import load_csv
from src.data.source_registry import DatasetSource, SourceRegistry
from src.data.validation import DataValidator, ValidationResult


@pytest.fixture
def sample_canonical_df() -> pd.DataFrame:
    """Loads the canonical synthetic sample fixture."""
    return load_csv("data/sample/synthetic_district_observations.csv")


@pytest.fixture
def test_registry() -> SourceRegistry:
    """Provides a registry containing the synthetic sample source."""
    registry = SourceRegistry()
    registry.register(
        DatasetSource(
            source_id="SRC_EXAMPLE_SYNTHETIC",
            dataset_name="Test Synthetic Source",
            publisher="EconLens AI Tests",
            source_url="internal://test",
            geographic_coverage="Sample",
            geographic_level="district",
            reference_period="2021-22",
            verification_status="validated",
        )
    )
    return registry


def test_valid_canonical_dataset_passes(sample_canonical_df: pd.DataFrame, test_registry: SourceRegistry) -> None:
    """Verifies that the canonical sample dataset passes validation with 0 errors."""
    validator = DataValidator(source_registry=test_registry)
    result = validator.validate_canonical(sample_canonical_df)

    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.row_count == 6
    assert result.column_count == 14
    assert result.duplicate_count == 0


def test_missing_required_column(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that omitting a required column results in validation failure."""
    df_missing = sample_canonical_df.drop(columns=["indicator_code"])
    validator = DataValidator()
    result = validator.validate_canonical(df_missing)

    assert result.is_valid is False
    assert any("indicator_code" in err for err in result.errors)


def test_missing_region_id(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that blank or null region_id values are flagged as errors."""
    df_bad = sample_canonical_df.copy()
    df_bad.loc[0, "region_id"] = ""
    df_bad.loc[1, "region_id"] = None

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("region_id" in err for err in result.errors)
    assert result.invalid_value_counts.get("region_id_blank") == 2


def test_missing_indicator_code(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that blank or null indicator_code values are flagged as errors."""
    df_bad = sample_canonical_df.copy()
    df_bad.loc[2, "indicator_code"] = "   "

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("indicator_code" in err for err in result.errors)


def test_non_numeric_and_infinite_values(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies detection of non-numeric strings and infinite values in 'value'."""
    df_bad = sample_canonical_df.copy()
    df_bad["value"] = df_bad["value"].astype(object)
    df_bad.loc[0, "value"] = "not_a_number"
    df_bad.loc[1, "value"] = float("inf")

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("non-numeric" in err for err in result.errors)
    assert any("infinite" in err for err in result.errors)


def test_invalid_reference_period(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that unparseable reference period formats are flagged."""
    df_bad = sample_canonical_df.copy()
    df_bad.loc[0, "reference_period"] = "year_2021"

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("reference period" in err for err in result.errors)


def test_invalid_geographic_level(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that unsupported geographic levels are flagged."""
    df_bad = sample_canonical_df.copy()
    df_bad.loc[0, "geographic_level"] = "continent"

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("geographic level" in err for err in result.errors)


def test_duplicate_observation_keys_detected(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies detection of duplicate (region_id, indicator_code, reference_period) keys."""
    # Duplicate row 0
    dupe_row = sample_canonical_df.iloc[[0]].copy()
    df_with_dupe = pd.concat([sample_canonical_df, dupe_row], ignore_index=True)

    validator = DataValidator()
    result = validator.validate_canonical(df_with_dupe)

    assert result.is_valid is False
    assert result.duplicate_count >= 2
    assert any("Duplicate observation key" in err for err in result.errors)


def test_inconsistent_indicator_units(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that assigning multiple different units to the same indicator is flagged."""
    df_bad = sample_canonical_df.copy()
    # LIT_RATE_TOT normally percentage, set row 3 to 'count'
    mask = (df_bad["indicator_code"] == "LIT_RATE_TOT") & (df_bad["region_id"] == "DEMO_DIST_02")
    df_bad.loc[mask, "unit"] = "count"

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("Inconsistent measurement units" in err for err in result.errors)


def test_out_of_bounds_indicator_values(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies bounds checks on bounded indicators (e.g. percentage cannot exceed 100)."""
    df_bad = sample_canonical_df.copy()
    # LIT_RATE_TOT has bounds [0, 100]
    df_bad.loc[0, "value"] = 150.0

    validator = DataValidator()
    result = validator.validate_canonical(df_bad)

    assert result.is_valid is False
    assert any("Out-of-bounds" in err for err in result.errors)


def test_unrecognized_source_id_warning(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that unrecognized source IDs produce warnings rather than fatal errors."""
    empty_registry = SourceRegistry()
    validator = DataValidator(source_registry=empty_registry)
    result = validator.validate_canonical(sample_canonical_df)

    # Valid schema, but warning generated for unregistered source
    assert result.is_valid is True
    assert any("Source ID(s)" in w and "not registered" in w for w in result.warnings)


def test_optional_columns_omitted_are_warnings(sample_canonical_df: pd.DataFrame) -> None:
    """Verifies that omitting optional fields (e.g. notes) does not cause fatal error."""
    df_minimal = sample_canonical_df.drop(columns=["notes", "collection_date", "parent_region_id"])
    validator = DataValidator()
    result = validator.validate_canonical(df_minimal)

    assert result.is_valid is True
    assert any("Optional contextual column" in w for w in result.warnings)
