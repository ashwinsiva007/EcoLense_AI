"""Tests for data preprocessing, column standardization, text trimming, and reshaping."""

import pandas as pd
import pytest

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


def test_standardize_column_names() -> None:
    """Verifies that arbitrary column names are safely converted to snake_case."""
    df = pd.DataFrame(columns=["Region ID", "Worker Population Ratio (%)", "Road-Density", "already_clean"])
    standardized_df, rename_map = standardize_column_names(df)

    assert "region_id" in standardized_df.columns
    assert "worker_population_ratio" in standardized_df.columns
    assert "roaddensity" in standardized_df.columns or "road_density" in standardized_df.columns
    assert "already_clean" in standardized_df.columns
    assert len(rename_map) >= 3


def test_trim_text_columns() -> None:
    """Verifies whitespace trimming across text columns and count accuracy."""
    df = pd.DataFrame({
        "region_id": ["  D01  ", "D02", " D03 "],
        "region_name": ["District Alpha  ", "  District Beta", "District Gamma"],
        "num_val": [10, 20, 30],
    })

    cleaned_df, trimmed_count = trim_text_columns(df)
    assert cleaned_df["region_id"].tolist() == ["D01", "D02", "D03"]
    assert cleaned_df["region_name"].tolist() == ["District Alpha", "District Beta", "District Gamma"]
    assert trimmed_count == 4


def test_coerce_numeric_column() -> None:
    """Verifies coercion of numbers and non-numeric strings."""
    df = pd.DataFrame({
        "value": ["42.5", "100", "invalid_str", None, "78.2"],
    })

    cleaned_df, num_fails = coerce_numeric_column(df, "value")
    assert num_fails == 1  # 'invalid_str' coerced to NaN
    assert cleaned_df.loc[0, "value"] == 42.5
    assert pd.isna(cleaned_df.loc[2, "value"])
    assert pd.isna(cleaned_df.loc[3, "value"])


def test_parse_reference_period() -> None:
    """Verifies parsing of valid reference periods and rejection of invalid formats."""
    assert parse_reference_period("2011") == "2011"
    assert parse_reference_period("2021-22") == "2021-22"
    assert parse_reference_period("2021 - 22") == "2021-22"
    assert parse_reference_period("2021-2022") == "2021-22"
    assert parse_reference_period("Q1-2023") == "Q1-2023"

    with pytest.raises(ValueError):
        parse_reference_period("not_a_year")

    with pytest.raises(ValueError):
        parse_reference_period("199")


def test_wide_to_long_observations() -> None:
    """Verifies wide-to-long transformation into the canonical schema."""
    wide_df = pd.DataFrame({
        "region_id": ["D01", "D02"],
        "region_name": ["Alpha", "Beta"],
        "parent_region_id": ["S01", "S01"],
        "lit_rate": [75.0, 82.5],
        "wpr": [40.2, 38.1],
    })

    indicator_mapping = {
        "lit_rate": {
            "indicator_code": "LIT_RATE_TOT",
            "indicator_name": "Total Literacy Rate",
            "unit": "percentage",
        },
        "wpr": {
            "indicator_code": "WPR_TOT",
            "indicator_name": "Worker Population Ratio",
            "unit": "percentage",
        },
    }

    long_df = wide_to_long_observations(
        df=wide_df,
        id_vars=["region_id", "region_name"],
        indicator_mapping=indicator_mapping,
        reference_period="2021-22",
        source_id="SRC_TEST",
        default_geo_level="district",
    )

    assert len(long_df) == 4
    assert set(long_df.columns).issuperset({
        "region_id", "region_name", "indicator_code", "value", "unit", "reference_period", "source_id"
    })
    assert set(long_df["indicator_code"].unique()) == {"LIT_RATE_TOT", "WPR_TOT"}
    assert long_df.loc[long_df["indicator_code"] == "LIT_RATE_TOT", "value"].tolist() == [75.0, 82.5]


def test_anti_fabrication_no_zero_replacement() -> None:
    """Ensures missing values are preserved as NaN and NEVER converted to zero."""
    df = pd.DataFrame({
        "region_id": ["D01", "D02"],
        "value": [None, 50.0],
    })

    pipeline = PreprocessingPipeline()
    cleaned_df, report = pipeline.clean(df)

    assert pd.isna(cleaned_df.loc[0, "value"])
    assert cleaned_df.loc[0, "value"] != 0
    assert report.missing_value_summary.get("value") == 1


def test_pipeline_idempotency() -> None:
    """Ensures repeated pipeline execution produces deterministic identical outputs."""
    df = pd.DataFrame({
        "region_id": [" D01 "],
        "region_name": ["District Alpha "],
        "value": ["85.4"],
        "reference_period": ["2021-2022"],
    })

    pipeline = PreprocessingPipeline()
    cleaned_once, _ = pipeline.clean(df)
    cleaned_twice, _ = pipeline.clean(cleaned_once)

    pd.testing.assert_frame_equal(cleaned_once, cleaned_twice)
