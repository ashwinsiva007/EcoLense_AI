"""Tests for dataset quality and pipeline readiness reporting."""

import pandas as pd
import pytest

from src.data.data_loader import load_csv
from src.data.quality_report import format_quality_report_markdown, generate_quality_report
from src.data.source_registry import SourceRegistry


def test_quality_report_on_valid_sample() -> None:
    """Verifies quality report generation on valid sample dataset."""
    df = load_csv("data/sample/synthetic_district_observations.csv")
    registry = SourceRegistry.load_from_file("data/metadata/source_registry.json")

    report = generate_quality_report(df, source_registry=registry)

    assert report["readiness_status"] == "READY"
    assert report["total_rows"] == 6
    assert report["total_columns"] == 14
    assert report["distinct_region_count"] == 2
    assert report["distinct_indicator_count"] == 3
    assert report["distinct_period_count"] == 1
    assert report["duplicate_observation_keys"] == 0
    assert report["numeric_summary"]["valid_numeric_observations"] == 6
    assert len(report["validation_errors"]) == 0

    md_text = format_quality_report_markdown(report)
    assert "Dataset Quality & Readiness Report: **READY**" in md_text
    assert "6 rows x 14 columns" in md_text


def test_quality_report_on_invalid_data() -> None:
    """Verifies quality report flags invalid schemas with 'NEEDS_REVISION'."""
    bad_df = pd.DataFrame({"region_id": ["D01"], "value": [10]})
    report = generate_quality_report(bad_df)

    assert report["readiness_status"] == "NEEDS_REVISION"
    assert report["is_valid"] is False
    assert len(report["validation_errors"]) > 0

    md_text = format_quality_report_markdown(report)
    assert "**NEEDS_REVISION**" in md_text
    assert "Validation Errors" in md_text
