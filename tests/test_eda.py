"""Comprehensive test suite for Stage 3 Exploratory Data Analysis.

Tests cover: descriptive statistics, missing-value calculations, duplicate
detection, regional comparison calculations, ranking with missing values,
time-series checks, correlation analysis with insufficient observations,
unit and geographic-level compatibility, empty datasets, missing columns,
report generation, and filtering behaviour.

All tests use small, deterministic synthetic test fixtures clearly labelled
as non-real data. No internet access required.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

from src.analytics.exploratory_analysis import (
    CorrelationResult,
    DataQualityProfile,
    DatasetOverview,
    ExploratoryAnalyzer,
    IndicatorStats,
    RegionalComparison,
    SummaryStatistics,
    MIN_CORRELATION_SAMPLE_SIZE,
    MIN_STATS_SAMPLE_SIZE,
)
from src.analytics.eda_report import (
    generate_eda_report_markdown,
    generate_eda_summary_json,
    generate_regional_summary_table,
)


# ==============================================================================
# Fixtures
# ==============================================================================

def _make_canonical_df(
    n_regions: int = 5,
    indicators: List[str] = None,
    period: str = "2021",
    geo_level: str = "district",
    source_id: str = "SRC_TEST",
) -> pd.DataFrame:
    """Creates a deterministic synthetic canonical DataFrame.

    SYNTHETIC TEST FIXTURE — NOT REAL DATA.
    """
    if indicators is None:
        indicators = ["IND_A", "IND_B", "IND_C"]

    rows = []
    for i in range(n_regions):
        region_id = f"99_{600 + i}"
        region_name = f"TestRegion_{i}"
        for j, ind in enumerate(indicators):
            rows.append({
                "region_id": region_id,
                "region_name": region_name,
                "parent_region_id": "99",
                "geographic_level": geo_level,
                "indicator_code": ind,
                "indicator_name": f"Test Indicator {ind}",
                "value": float(10 * (i + 1) + j),
                "unit": "percentage" if "RATE" in ind else "count",
                "reference_period": period,
                "source_id": source_id,
                "source_record_id": f"REC_{i:03d}",
                "collection_date": "2026-01-01",
                "quality_status": "validated",
                "notes": "SYNTHETIC TEST FIXTURE",
            })
    return pd.DataFrame(rows)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """5-region, 3-indicator synthetic fixture."""
    return _make_canonical_df()


@pytest.fixture
def multi_period_df() -> pd.DataFrame:
    """Fixture with 2 reference periods for time-series tests."""
    df1 = _make_canonical_df(n_regions=3, period="2011")
    df2 = _make_canonical_df(n_regions=3, period="2021")
    # Slightly different values for second period
    df2["value"] = df2["value"].apply(lambda x: x * 1.1)
    return pd.concat([df1, df2], ignore_index=True)


@pytest.fixture
def analyzer(sample_df: pd.DataFrame) -> ExploratoryAnalyzer:
    """Pre-configured analyzer with sample data."""
    return ExploratoryAnalyzer(df=sample_df)


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Empty DataFrame with canonical columns."""
    return pd.DataFrame(columns=[
        "region_id", "region_name", "parent_region_id", "geographic_level",
        "indicator_code", "indicator_name", "value", "unit",
        "reference_period", "source_id", "source_record_id",
        "collection_date", "quality_status", "notes",
    ])


# ==============================================================================
# A. Dataset Overview Tests
# ==============================================================================

class TestDatasetOverview:
    """Tests for compute_dataset_overview."""

    def test_overview_basic_counts(self, analyzer: ExploratoryAnalyzer) -> None:
        overview = analyzer.compute_dataset_overview()
        assert isinstance(overview, DatasetOverview)
        assert overview.total_observations == 15  # 5 regions × 3 indicators
        assert overview.valid_observations == 15
        assert overview.distinct_regions == 5
        assert overview.distinct_indicators == 3
        assert overview.distinct_reference_periods == 1
        assert "2021" in overview.reference_periods

    def test_overview_source_tracking(self, analyzer: ExploratoryAnalyzer) -> None:
        overview = analyzer.compute_dataset_overview()
        assert "SRC_TEST" in overview.source_ids
        assert "district" in overview.geographic_levels

    def test_overview_empty_dataset(self, empty_df: pd.DataFrame) -> None:
        a = ExploratoryAnalyzer(df=empty_df)
        overview = a.compute_dataset_overview()
        assert overview.total_observations == 0
        assert overview.distinct_regions == 0

    def test_overview_quality_statuses(self, analyzer: ExploratoryAnalyzer) -> None:
        overview = analyzer.compute_dataset_overview()
        assert "validated" in overview.quality_statuses
        assert overview.quality_statuses["validated"] == 15


# ==============================================================================
# B. Data Quality Tests
# ==============================================================================

class TestDataQuality:
    """Tests for compute_data_quality."""

    def test_quality_no_missing_values(self, analyzer: ExploratoryAnalyzer) -> None:
        quality = analyzer.compute_data_quality()
        assert isinstance(quality, DataQualityProfile)
        # No missing values in the clean fixture
        assert quality.missing_by_region == {}
        assert quality.missing_by_indicator == {}
        assert quality.duplicate_count == 0

    def test_quality_with_missing_values(self) -> None:
        df = _make_canonical_df(n_regions=3)
        df.loc[0, "value"] = None  # Introduce a missing value
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        assert "value" in quality.missing_by_column
        assert quality.missing_by_column["value"] == 1

    def test_quality_missing_by_region(self) -> None:
        df = _make_canonical_df(n_regions=3)
        df.loc[0, "value"] = None
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        # Region 99_600 should have 1 missing value
        assert "99_600" in quality.missing_by_region

    def test_quality_missing_by_indicator(self) -> None:
        df = _make_canonical_df(n_regions=3)
        df.loc[0, "value"] = None  # First row is IND_A
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        assert "IND_A" in quality.missing_by_indicator

    def test_quality_duplicate_detection(self) -> None:
        df = _make_canonical_df(n_regions=3)
        # Create a duplicate row
        dupe = df.iloc[[0]].copy()
        df = pd.concat([df, dupe], ignore_index=True)
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        assert quality.duplicate_count > 0

    def test_quality_non_numeric_detection(self) -> None:
        df = _make_canonical_df(n_regions=3)
        df["value"] = df["value"].astype(object)
        df.loc[0, "value"] = "not_a_number"
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        assert quality.invalid_numeric_count >= 1

    def test_quality_coverage_matrix(self, analyzer: ExploratoryAnalyzer) -> None:
        quality = analyzer.compute_data_quality()
        assert quality.coverage_matrix is not None
        assert quality.coverage_matrix.shape[0] == 5  # 5 regions
        assert quality.coverage_matrix.shape[1] == 3  # 3 indicators

    def test_quality_empty_dataset(self, empty_df: pd.DataFrame) -> None:
        a = ExploratoryAnalyzer(df=empty_df)
        quality = a.compute_data_quality()
        assert quality.total_rows == 0
        assert quality.notes == "Dataset is empty."

    def test_missing_pct_calculation(self) -> None:
        df = _make_canonical_df(n_regions=4)
        df.loc[0, "value"] = None
        df.loc[3, "value"] = None
        a = ExploratoryAnalyzer(df=df)
        quality = a.compute_data_quality()
        # 2 missing out of 12 rows = 16.67%
        assert abs(quality.missing_pct_by_column["value"] - (2 / 12 * 100)) < 0.1


# ==============================================================================
# C. Indicator Statistics Tests
# ==============================================================================

class TestIndicatorStatistics:
    """Tests for compute_indicator_statistics."""

    def test_statistics_computed(self, analyzer: ExploratoryAnalyzer) -> None:
        stats = analyzer.compute_indicator_statistics()
        assert isinstance(stats, list)
        assert len(stats) > 0
        for s in stats:
            assert isinstance(s, IndicatorStats)
            assert s.count > 0

    def test_statistics_mean_median(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_X"])
        # Values: 10, 20, 30, 40, 50
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_X")
        assert len(stats) == 1
        s = stats[0]
        assert s.count == 5
        assert s.mean == 30.0
        assert s.median == 30.0

    def test_statistics_std_and_quartiles(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_X"])
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_X")
        s = stats[0]
        assert s.std is not None
        assert s.std > 0
        assert s.q25 is not None
        assert s.q75 is not None
        assert s.iqr is not None
        assert s.iqr == s.q75 - s.q25

    def test_statistics_min_max(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_X"])
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_X")
        s = stats[0]
        assert s.min_val == 10.0
        assert s.max_val == 50.0

    def test_statistics_single_observation(self) -> None:
        df = _make_canonical_df(n_regions=1, indicators=["IND_X"])
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_X")
        s = stats[0]
        assert s.count == 1
        assert s.std is None
        assert "1 observation" in s.notes

    def test_statistics_filter_by_period(self, analyzer: ExploratoryAnalyzer) -> None:
        stats = analyzer.compute_indicator_statistics(reference_period="2021")
        assert len(stats) > 0
        for s in stats:
            assert s.reference_period == "2021"

    def test_statistics_filter_by_geo_level(self, analyzer: ExploratoryAnalyzer) -> None:
        stats = analyzer.compute_indicator_statistics(geographic_level="district")
        assert len(stats) > 0
        for s in stats:
            assert s.geographic_level == "district"

    def test_statistics_empty_after_filter(self, analyzer: ExploratoryAnalyzer) -> None:
        stats = analyzer.compute_indicator_statistics(indicator_code="NONEXISTENT")
        assert stats == []

    def test_statistics_preserves_unit(self) -> None:
        df = _make_canonical_df(n_regions=3, indicators=["LIT_RATE_TOT"])
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics()
        s = stats[0]
        assert s.unit == "percentage"

    def test_statistics_with_missing_values(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_X"])
        df.loc[0, "value"] = None  # 4 valid observations
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_X")
        s = stats[0]
        assert s.count == 4  # Only valid values counted


# ==============================================================================
# D. Regional Comparison Tests
# ==============================================================================

class TestRegionalComparison:
    """Tests for compute_regional_comparison."""

    def test_comparison_basic(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A", total_expected_regions=5)
        assert isinstance(result, RegionalComparison)
        assert result.regions_included == 5
        assert result.regions_missing == 0
        assert len(result.rankings) == 5

    def test_comparison_rankings_ordered(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A")
        # Rankings should be descending
        values = [r["value"] for r in result.rankings]
        assert values == sorted(values, reverse=True)

    def test_comparison_highest_lowest(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A")
        assert result.highest is not None
        assert result.lowest is not None
        assert result.highest["value"] >= result.lowest["value"]

    def test_comparison_group_mean(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A")
        assert result.group_mean is not None
        assert result.group_median is not None

    def test_comparison_missing_regions(self) -> None:
        df = _make_canonical_df(n_regions=3, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A", total_expected_regions=5)
        assert result.regions_included == 3
        assert result.regions_missing == 2
        assert "3 of 5" in result.notes

    def test_comparison_nonexistent_indicator(self, analyzer: ExploratoryAnalyzer) -> None:
        result = analyzer.compute_regional_comparison("NONEXISTENT")
        assert result.regions_included == 0
        assert "No observations" in result.notes

    def test_comparison_deviation_from_mean(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A")
        for r in result.rankings:
            assert "deviation_from_mean" in r
            assert r["deviation_from_mean"] is not None

    def test_comparison_with_missing_values(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A"])
        df.loc[0, "value"] = None
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_A", total_expected_regions=5)
        # One region lost due to missing value
        assert result.regions_included == 4
        assert result.regions_missing == 1


# ==============================================================================
# E. Time-Series Tests
# ==============================================================================

class TestTimeAnalysis:
    """Tests for compute_time_analysis."""

    def test_single_period_unavailable(self, analyzer: ExploratoryAnalyzer) -> None:
        result = analyzer.compute_time_analysis("IND_A")
        assert result["time_series_available"] is False
        assert result["period_count"] == 1
        assert "single cross-sectional snapshot" in result["notes"]

    def test_multi_period_available(self, multi_period_df: pd.DataFrame) -> None:
        a = ExploratoryAnalyzer(df=multi_period_df)
        result = a.compute_time_analysis("IND_A")
        assert result["time_series_available"] is True
        assert result["period_count"] == 2
        assert "2011" in result["periods_available"]
        assert "2021" in result["periods_available"]

    def test_multi_period_summaries(self, multi_period_df: pd.DataFrame) -> None:
        a = ExploratoryAnalyzer(df=multi_period_df)
        result = a.compute_time_analysis("IND_A")
        assert "period_summaries" in result
        assert len(result["period_summaries"]) == 2


# ==============================================================================
# F. Correlation Tests
# ==============================================================================

class TestCorrelation:
    """Tests for compute_correlation_matrix."""

    def test_correlation_matrix_computed(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A", "IND_B"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        assert result["correlation_matrix"] is not None
        assert result["sample_size"] == 10
        assert len(result["pairwise_results"]) == 1

    def test_correlation_insufficient_sample(self) -> None:
        df = _make_canonical_df(n_regions=2, indicators=["IND_A", "IND_B"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        # With 2 regions < MIN_CORRELATION_SAMPLE_SIZE (5)
        pr = result["pairwise_results"][0]
        assert isinstance(pr, CorrelationResult)
        assert pr.is_sufficient is False
        assert "Insufficient" in pr.notes

    def test_correlation_single_indicator(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        assert result["correlation_matrix"] is None
        assert "Need at least 2 indicators" in result["notes"]

    def test_correlation_non_causal_disclaimer(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A", "IND_B"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        assert "causation" in result["notes"].lower()

    def test_correlation_pairwise_result_fields(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A", "IND_B", "IND_C"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        # 3 indicators = 3 pairwise combinations
        assert len(result["pairwise_results"]) == 3
        for pr in result["pairwise_results"]:
            assert pr.sample_size > 0


# ==============================================================================
# G. Scatter Data Tests
# ==============================================================================

class TestScatterData:
    """Tests for compute_pairwise_scatter_data."""

    def test_scatter_data_structure(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_A", "IND_B"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_pairwise_scatter_data("IND_A", "IND_B")
        assert result["sample_size"] == 5
        assert len(result["x_values"]) == 5
        assert len(result["y_values"]) == 5
        assert len(result["regions"]) == 5

    def test_scatter_no_overlap(self) -> None:
        df = _make_canonical_df(n_regions=3, indicators=["IND_A"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_pairwise_scatter_data("IND_A", "IND_NONEXISTENT")
        assert result["sample_size"] == 0


# ==============================================================================
# H. Unit and Geographic Level Compatibility
# ==============================================================================

class TestCompatibilityChecks:
    """Tests for unit and geographic level filtering."""

    def test_filter_by_geographic_level(self) -> None:
        df1 = _make_canonical_df(n_regions=3, indicators=["IND_A"], geo_level="district")
        df2 = _make_canonical_df(n_regions=2, indicators=["IND_A"], geo_level="state")
        df2["region_id"] = ["ST_1", "ST_2"]
        combined = pd.concat([df1, df2], ignore_index=True)
        a = ExploratoryAnalyzer(df=combined)

        stats = a.compute_indicator_statistics(geographic_level="district")
        for s in stats:
            assert s.geographic_level == "district"

    def test_regional_comparison_geographic_filter(self) -> None:
        df1 = _make_canonical_df(n_regions=3, indicators=["IND_A"], geo_level="district")
        df2 = _make_canonical_df(n_regions=1, indicators=["IND_A"], geo_level="state")
        df2["region_id"] = ["ST_99"]
        combined = pd.concat([df1, df2], ignore_index=True)
        a = ExploratoryAnalyzer(df=combined)

        result = a.compute_regional_comparison("IND_A", geographic_level="district", total_expected_regions=3)
        assert result.regions_included == 3  # Only district-level

    def test_correlation_geographic_filter(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A", "IND_B"], geo_level="district")
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix(geographic_level="district")
        assert result["sample_size"] == 10

        result_state = a.compute_correlation_matrix(geographic_level="state")
        assert result_state["sample_size"] == 0


# ==============================================================================
# I. Input Validation and Error Handling
# ==============================================================================

class TestInputValidation:
    """Tests for error handling with invalid or unusual inputs."""

    def test_none_data_raises(self) -> None:
        a = ExploratoryAnalyzer()
        with pytest.raises(ValueError, match="No data loaded"):
            a.compute_dataset_overview()

    def test_non_dataframe_raises(self) -> None:
        with pytest.raises(TypeError, match="Expected pandas DataFrame"):
            ExploratoryAnalyzer(df="not_a_dataframe")

    def test_missing_columns_raises(self) -> None:
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        with pytest.raises(ValueError, match="missing required columns"):
            ExploratoryAnalyzer(df=df)

    def test_set_data_replaces(self, analyzer: ExploratoryAnalyzer) -> None:
        new_df = _make_canonical_df(n_regions=2, indicators=["NEW_IND"])
        analyzer.set_data(new_df)
        overview = analyzer.compute_dataset_overview()
        assert overview.distinct_regions == 2
        assert "NEW_IND" in overview.indicator_codes


# ==============================================================================
# J. Summary Statistics (Backward Compatibility)
# ==============================================================================

class TestSummaryStatistics:
    """Tests for compute_summary_statistics backward compatibility."""

    def test_summary_returns_dataclass(self, analyzer: ExploratoryAnalyzer) -> None:
        result = analyzer.compute_summary_statistics()
        assert isinstance(result, SummaryStatistics)
        assert result.total_regions == 5
        assert len(result.indicator_names) == 3
        assert len(result.metrics_by_indicator) > 0


# ==============================================================================
# K. EDA Report Generation Tests
# ==============================================================================

class TestReportGeneration:
    """Tests for JSON and Markdown report generation."""

    def test_json_report_structure(self, analyzer: ExploratoryAnalyzer) -> None:
        result = generate_eda_summary_json(analyzer)
        assert "overview" in result
        assert "quality" in result
        assert "indicator_statistics" in result
        assert "generated_at" in result
        assert result["overview"]["total_observations"] == 15

    def test_json_report_saved_to_file(self, analyzer: ExploratoryAnalyzer, tmp_path: Path) -> None:
        out = tmp_path / "eda_summary.json"
        generate_eda_summary_json(analyzer, output_path=out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["overview"]["distinct_regions"] == 5

    def test_markdown_report_content(self, analyzer: ExploratoryAnalyzer) -> None:
        md = generate_eda_report_markdown(analyzer)
        assert "Exploratory Data Analysis Report" in md
        assert "Dataset Overview" in md
        assert "Data Quality Profile" in md
        assert "Indicator Descriptive Statistics" in md
        assert "Analytical Caveats" in md
        assert "ADR 008" in md

    def test_markdown_report_saved_to_file(self, analyzer: ExploratoryAnalyzer, tmp_path: Path) -> None:
        out = tmp_path / "eda_report.md"
        generate_eda_report_markdown(analyzer, output_path=out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "EconLens AI" in content

    def test_regional_summary_table(self, analyzer: ExploratoryAnalyzer) -> None:
        table = generate_regional_summary_table(analyzer)
        assert isinstance(table, pd.DataFrame)
        assert len(table) == 5  # 5 regions
        assert "region_id" in table.columns

    def test_regional_summary_table_saved(self, analyzer: ExploratoryAnalyzer, tmp_path: Path) -> None:
        out = tmp_path / "regional_summary.csv"
        generate_regional_summary_table(analyzer, output_path=out)
        assert out.exists()

    def test_full_eda_report_generation(self, analyzer: ExploratoryAnalyzer) -> None:
        report = analyzer.generate_eda_report()
        assert report["overview"] is not None
        assert report["quality"] is not None
        assert len(report["indicator_statistics"]) > 0
        assert report["metadata"]["total_observations"] == 15


# ==============================================================================
# L. Edge Cases
# ==============================================================================

class TestEdgeCases:
    """Edge cases: all-NaN values, single region, zero-variance indicators."""

    def test_all_nan_values(self) -> None:
        df = _make_canonical_df(n_regions=3, indicators=["IND_A"])
        df["value"] = None
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics()
        for s in stats:
            assert s.count == 0

    def test_single_region_single_indicator(self) -> None:
        df = _make_canonical_df(n_regions=1, indicators=["IND_SOLO"])
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_regional_comparison("IND_SOLO", total_expected_regions=1)
        assert result.regions_included == 1
        assert result.regions_missing == 0
        assert len(result.rankings) == 1

    def test_zero_variance_indicator(self) -> None:
        df = _make_canonical_df(n_regions=5, indicators=["IND_FLAT"])
        df["value"] = 42.0  # All same value
        a = ExploratoryAnalyzer(df=df)
        stats = a.compute_indicator_statistics(indicator_code="IND_FLAT")
        s = stats[0]
        assert s.std == 0.0
        assert s.iqr == 0.0
        assert s.mean == 42.0

    def test_correlation_zero_variance_no_crash(self) -> None:
        df = _make_canonical_df(n_regions=10, indicators=["IND_A", "IND_B"])
        df.loc[df["indicator_code"] == "IND_A", "value"] = 5.0  # Zero variance
        a = ExploratoryAnalyzer(df=df)
        result = a.compute_correlation_matrix()
        # Should not crash even with zero variance
        assert result is not None
