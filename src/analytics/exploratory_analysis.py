"""Exploratory regional data analysis module for EconLens AI.

Provides dataset overview, data quality profiling, indicator distributions,
regional comparisons, time-series checks, and indicator relationship analysis
without asserting unverified causal links.

All computations operate on the canonical long-form observation schema defined
in src.data.schema (composite key: region_id, indicator_code, reference_period).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.data.schema import CANONICAL_COLUMNS, PRIMARY_KEY_COLUMNS, REQUIRED_COLUMNS
from src.utils.logging_config import get_logger

logger = get_logger("analytics.exploratory_analysis")

# Minimum observations required for correlation to be meaningful
MIN_CORRELATION_SAMPLE_SIZE = 5

# Minimum observations for descriptive statistics
MIN_STATS_SAMPLE_SIZE = 2


# ==============================================================================
# Result Data Classes
# ==============================================================================

@dataclass
class SummaryStatistics:
    """Statistical summary metadata for a set of regional indicators."""

    total_regions: int
    indicator_names: List[str]
    metrics_by_indicator: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    notes: str = ""


@dataclass
class DatasetOverview:
    """High-level summary of acquired datasets and observations."""

    total_observations: int = 0
    valid_observations: int = 0
    distinct_regions: int = 0
    distinct_indicators: int = 0
    distinct_reference_periods: int = 0
    reference_periods: List[str] = field(default_factory=list)
    source_ids: List[str] = field(default_factory=list)
    geographic_levels: List[str] = field(default_factory=list)
    region_names: List[str] = field(default_factory=list)
    indicator_codes: List[str] = field(default_factory=list)
    quality_statuses: Dict[str, int] = field(default_factory=dict)
    notes: str = ""


@dataclass
class DataQualityProfile:
    """Detailed data quality analysis results."""

    missing_by_column: Dict[str, int] = field(default_factory=dict)
    missing_pct_by_column: Dict[str, float] = field(default_factory=dict)
    missing_by_region: Dict[str, int] = field(default_factory=dict)
    missing_by_indicator: Dict[str, int] = field(default_factory=dict)
    missing_by_period: Dict[str, int] = field(default_factory=dict)
    duplicate_count: int = 0
    duplicate_keys: List[Dict[str, str]] = field(default_factory=list)
    invalid_numeric_count: int = 0
    infinite_count: int = 0
    total_rows: int = 0
    total_columns: int = 0
    coverage_matrix: Optional[pd.DataFrame] = None
    notes: str = ""


@dataclass
class IndicatorStats:
    """Descriptive statistics for a single indicator."""

    indicator_code: str
    indicator_name: str
    unit: str
    reference_period: str
    geographic_level: str
    count: int = 0
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    iqr: Optional[float] = None
    source_id: str = ""
    notes: str = ""


@dataclass
class RegionalComparison:
    """Comparison of a specific indicator across regions."""

    indicator_code: str
    indicator_name: str
    unit: str
    reference_period: str
    regions_included: int = 0
    regions_missing: int = 0
    rankings: List[Dict[str, Any]] = field(default_factory=list)
    group_mean: Optional[float] = None
    group_median: Optional[float] = None
    highest: Optional[Dict[str, Any]] = None
    lowest: Optional[Dict[str, Any]] = None
    notes: str = ""


@dataclass
class CorrelationResult:
    """Pairwise indicator correlation analysis result."""

    indicator_a: str
    indicator_b: str
    reference_period: str
    geographic_level: str
    sample_size: int = 0
    correlation: Optional[float] = None
    is_sufficient: bool = False
    notes: str = ""


# ==============================================================================
# Core EDA Engine
# ==============================================================================

class ExploratoryAnalyzer:
    """Calculates non-causal statistical summaries and analytical profiles.

    Operates on the canonical long-form observation DataFrame.
    """

    def __init__(
        self,
        df: Optional[pd.DataFrame] = None,
        indicators: Optional[List[str]] = None,
    ) -> None:
        self.df = df
        self.indicators = indicators or []
        self._validated = False

        if df is not None:
            self._validate_input(df)

    def _validate_input(self, df: pd.DataFrame) -> None:
        """Validates that the DataFrame has the minimal required columns."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        if df.empty:
            logger.warning("Input DataFrame is empty. Analyses will return empty results.")
        required = {"region_id", "indicator_code", "value", "unit", "reference_period"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Input DataFrame missing required columns: {sorted(missing)}")
        self._validated = True

    def set_data(self, df: pd.DataFrame) -> None:
        """Sets or replaces the analysis DataFrame."""
        self._validate_input(df)
        self.df = df

    def _ensure_data(self) -> pd.DataFrame:
        """Returns the DataFrame or raises if not set."""
        if self.df is None:
            raise ValueError("No data loaded. Call set_data() first.")
        return self.df

    # ------------------------------------------------------------------
    # A. Dataset Overview
    # ------------------------------------------------------------------

    def compute_dataset_overview(self) -> DatasetOverview:
        """Computes a high-level summary of all observations in the dataset."""
        df = self._ensure_data()
        logger.info("Computing dataset overview for %d rows", len(df))

        if df.empty:
            return DatasetOverview(notes="Dataset is empty.")

        # Coerce values to numeric for counting valid observations
        numeric_values = pd.to_numeric(df["value"], errors="coerce")
        valid_count = int(numeric_values.notna().sum())

        overview = DatasetOverview(
            total_observations=len(df),
            valid_observations=valid_count,
            distinct_regions=int(df["region_id"].nunique()),
            distinct_indicators=int(df["indicator_code"].nunique()),
            distinct_reference_periods=int(df["reference_period"].nunique()),
            reference_periods=sorted(df["reference_period"].dropna().unique().tolist()),
            indicator_codes=sorted(df["indicator_code"].dropna().unique().tolist()),
        )

        if "source_id" in df.columns:
            overview.source_ids = sorted(df["source_id"].dropna().unique().tolist())
        if "geographic_level" in df.columns:
            overview.geographic_levels = sorted(
                df["geographic_level"].dropna().unique().tolist()
            )
        if "region_name" in df.columns:
            overview.region_names = sorted(df["region_name"].dropna().unique().tolist())
        if "quality_status" in df.columns:
            overview.quality_statuses = (
                df["quality_status"]
                .fillna("unknown")
                .value_counts()
                .to_dict()
            )

        return overview

    # ------------------------------------------------------------------
    # B. Data Quality Analysis
    # ------------------------------------------------------------------

    def compute_data_quality(self) -> DataQualityProfile:
        """Analyzes missing values, duplicates, and coverage gaps."""
        df = self._ensure_data()
        logger.info("Computing data quality profile for %d rows", len(df))

        profile = DataQualityProfile(
            total_rows=len(df),
            total_columns=len(df.columns),
        )

        if df.empty:
            profile.notes = "Dataset is empty."
            return profile

        # Missing values by column
        for col in df.columns:
            miss_count = int(df[col].isna().sum())
            if miss_count > 0:
                profile.missing_by_column[col] = miss_count
                profile.missing_pct_by_column[col] = round(
                    100.0 * miss_count / len(df), 2
                )

        # Missing values by region (count missing 'value' per region)
        if "region_id" in df.columns and "value" in df.columns:
            val_numeric = pd.to_numeric(df["value"], errors="coerce")
            missing_mask = val_numeric.isna()
            if missing_mask.any():
                miss_by_region = (
                    df.loc[missing_mask]
                    .groupby("region_id")
                    .size()
                    .to_dict()
                )
                profile.missing_by_region = {str(k): int(v) for k, v in miss_by_region.items()}

        # Missing values by indicator
        if "indicator_code" in df.columns and "value" in df.columns:
            val_numeric = pd.to_numeric(df["value"], errors="coerce")
            missing_mask = val_numeric.isna()
            if missing_mask.any():
                miss_by_ind = (
                    df.loc[missing_mask]
                    .groupby("indicator_code")
                    .size()
                    .to_dict()
                )
                profile.missing_by_indicator = {str(k): int(v) for k, v in miss_by_ind.items()}

        # Missing values by period
        if "reference_period" in df.columns and "value" in df.columns:
            val_numeric = pd.to_numeric(df["value"], errors="coerce")
            missing_mask = val_numeric.isna()
            if missing_mask.any():
                miss_by_period = (
                    df.loc[missing_mask]
                    .groupby("reference_period")
                    .size()
                    .to_dict()
                )
                profile.missing_by_period = {str(k): int(v) for k, v in miss_by_period.items()}

        # Duplicate detection
        pk_cols = [c for c in PRIMARY_KEY_COLUMNS if c in df.columns]
        if len(pk_cols) == len(PRIMARY_KEY_COLUMNS):
            dupe_mask = df.duplicated(subset=pk_cols, keep=False)
            profile.duplicate_count = int(dupe_mask.sum())
            if profile.duplicate_count > 0:
                dupe_examples = (
                    df[dupe_mask][pk_cols]
                    .drop_duplicates()
                    .head(5)
                    .to_dict(orient="records")
                )
                profile.duplicate_keys = [
                    {str(k): str(v) for k, v in rec.items()} for rec in dupe_examples
                ]

        # Invalid / non-finite numeric values
        if "value" in df.columns:
            val_numeric = pd.to_numeric(df["value"], errors="coerce")
            profile.invalid_numeric_count = int(
                val_numeric.isna().sum() - df["value"].isna().sum()
            )
            inf_mask = val_numeric.apply(
                lambda x: math.isinf(x) if pd.notna(x) else False
            )
            profile.infinite_count = int(inf_mask.sum())

        # Coverage matrix: regions x indicators
        if "region_id" in df.columns and "indicator_code" in df.columns:
            try:
                coverage = df.pivot_table(
                    index="region_id",
                    columns="indicator_code",
                    values="value",
                    aggfunc="count",
                    fill_value=0,
                )
                profile.coverage_matrix = coverage
            except Exception as exc:
                logger.warning("Could not compute coverage matrix: %s", exc)

        return profile

    # ------------------------------------------------------------------
    # C. Indicator Distributions / Descriptive Statistics
    # ------------------------------------------------------------------

    def compute_indicator_statistics(
        self,
        indicator_code: Optional[str] = None,
        reference_period: Optional[str] = None,
        geographic_level: Optional[str] = None,
    ) -> List[IndicatorStats]:
        """Computes descriptive statistics for each indicator.

        Args:
            indicator_code: Optional filter for a specific indicator.
            reference_period: Optional filter for a specific period.
            geographic_level: Optional filter for a specific geographic level.

        Returns:
            List of IndicatorStats with count, mean, median, std, min, max, quartiles.
        """
        df = self._ensure_data()
        logger.info("Computing indicator statistics")

        if df.empty:
            return []

        filtered = df.copy()
        if indicator_code:
            filtered = filtered[filtered["indicator_code"] == indicator_code]
        if reference_period:
            filtered = filtered[filtered["reference_period"] == str(reference_period)]
        if geographic_level and "geographic_level" in filtered.columns:
            filtered = filtered[filtered["geographic_level"] == geographic_level]

        if filtered.empty:
            return []

        filtered["_numeric_value"] = pd.to_numeric(filtered["value"], errors="coerce")

        results: List[IndicatorStats] = []

        # Group by indicator, period, and geographic level for comparable stats
        group_cols = ["indicator_code"]
        if "reference_period" in filtered.columns:
            group_cols.append("reference_period")
        if "geographic_level" in filtered.columns:
            group_cols.append("geographic_level")

        for group_key, group_df in filtered.groupby(group_cols, dropna=False):
            if isinstance(group_key, str):
                ind_code = group_key
                period = filtered["reference_period"].mode().iloc[0] if "reference_period" in filtered.columns else "unknown"
                geo_level = filtered["geographic_level"].mode().iloc[0] if "geographic_level" in filtered.columns else "unknown"
            else:
                group_vals = list(group_key)
                ind_code = group_vals[0]
                period = group_vals[1] if len(group_vals) > 1 else "unknown"
                geo_level = group_vals[2] if len(group_vals) > 2 else "unknown"

            valid_values = group_df["_numeric_value"].dropna()
            count = len(valid_values)

            # Get indicator metadata
            ind_name_vals = group_df["indicator_name"].dropna().unique()
            ind_name = ind_name_vals[0] if len(ind_name_vals) > 0 else ind_code
            unit_vals = group_df["unit"].dropna().unique()
            unit = unit_vals[0] if len(unit_vals) > 0 else "unknown"
            source_vals = group_df["source_id"].dropna().unique() if "source_id" in group_df.columns else []
            source_id = source_vals[0] if len(source_vals) > 0 else ""

            stats = IndicatorStats(
                indicator_code=str(ind_code),
                indicator_name=str(ind_name),
                unit=str(unit),
                reference_period=str(period),
                geographic_level=str(geo_level),
                count=count,
                source_id=str(source_id),
            )

            if count >= MIN_STATS_SAMPLE_SIZE:
                stats.mean = round(float(valid_values.mean()), 4)
                stats.median = round(float(valid_values.median()), 4)
                stats.std = round(float(valid_values.std()), 4)
                stats.min_val = round(float(valid_values.min()), 4)
                stats.max_val = round(float(valid_values.max()), 4)
                stats.q25 = round(float(valid_values.quantile(0.25)), 4)
                stats.q75 = round(float(valid_values.quantile(0.75)), 4)
                stats.iqr = round(stats.q75 - stats.q25, 4)
            elif count == 1:
                val = float(valid_values.iloc[0])
                stats.mean = round(val, 4)
                stats.median = round(val, 4)
                stats.min_val = round(val, 4)
                stats.max_val = round(val, 4)
                stats.notes = "Only 1 observation; dispersion statistics unavailable."
            else:
                stats.notes = "Insufficient valid observations for statistics."

            results.append(stats)

        return results

    def compute_summary_statistics(self, data: Any = None) -> SummaryStatistics:
        """Computes univariate statistics across regions.

        Backward-compatible wrapper around compute_indicator_statistics.
        """
        if data is not None and isinstance(data, pd.DataFrame):
            self.set_data(data)

        df = self._ensure_data()
        indicator_stats = self.compute_indicator_statistics()

        metrics: Dict[str, Dict[str, float]] = {}
        for s in indicator_stats:
            key = f"{s.indicator_code}_{s.reference_period}"
            entry: Dict[str, Any] = {"count": s.count, "unit": s.unit}
            if s.mean is not None:
                entry["mean"] = s.mean
            if s.median is not None:
                entry["median"] = s.median
            if s.std is not None:
                entry["std"] = s.std
            if s.min_val is not None:
                entry["min"] = s.min_val
            if s.max_val is not None:
                entry["max"] = s.max_val
            metrics[key] = entry

        return SummaryStatistics(
            total_regions=int(df["region_id"].nunique()),
            indicator_names=sorted(df["indicator_code"].dropna().unique().tolist()),
            metrics_by_indicator=metrics,
            notes="Statistics computed from validated canonical observations.",
        )

    # ------------------------------------------------------------------
    # D. Regional Comparisons
    # ------------------------------------------------------------------

    def compute_regional_comparison(
        self,
        indicator_code: str,
        reference_period: Optional[str] = None,
        geographic_level: str = "district",
        total_expected_regions: int = 32,
    ) -> RegionalComparison:
        """Compares indicator values across regions for a given indicator/period.

        Rankings use comparable observations only. Missing regions are disclosed.

        Args:
            indicator_code: The indicator to compare.
            reference_period: Period to filter on (uses the most common if None).
            geographic_level: Geographic level to filter on.
            total_expected_regions: Total expected for computing missing count.

        Returns:
            RegionalComparison with rankings, mean, median, highest, lowest.
        """
        df = self._ensure_data()
        logger.info("Computing regional comparison for %s", indicator_code)

        filtered = df[df["indicator_code"] == indicator_code].copy()
        if geographic_level and "geographic_level" in filtered.columns:
            filtered = filtered[filtered["geographic_level"] == geographic_level]

        if reference_period:
            filtered = filtered[filtered["reference_period"] == str(reference_period)]
        elif not filtered.empty:
            # Use the most common reference period
            reference_period = str(filtered["reference_period"].mode().iloc[0])
            filtered = filtered[filtered["reference_period"] == reference_period]

        # Get indicator metadata
        ind_name = indicator_code
        unit = "unknown"
        if not filtered.empty:
            names = filtered["indicator_name"].dropna().unique()
            ind_name = names[0] if len(names) > 0 else indicator_code
            units = filtered["unit"].dropna().unique()
            unit = units[0] if len(units) > 0 else "unknown"

        result = RegionalComparison(
            indicator_code=indicator_code,
            indicator_name=str(ind_name),
            unit=str(unit),
            reference_period=str(reference_period or "unknown"),
        )

        if filtered.empty:
            result.notes = f"No observations found for {indicator_code}."
            return result

        # Convert values
        filtered["_numeric_value"] = pd.to_numeric(filtered["value"], errors="coerce")
        valid = filtered.dropna(subset=["_numeric_value"]).copy()

        if valid.empty:
            result.notes = "No valid numeric observations available."
            return result

        # Remove duplicates (keep first for each region)
        valid = valid.drop_duplicates(subset=["region_id"], keep="first")

        result.regions_included = len(valid)
        result.regions_missing = max(0, total_expected_regions - result.regions_included)
        result.group_mean = round(float(valid["_numeric_value"].mean()), 4)
        result.group_median = round(float(valid["_numeric_value"].median()), 4)

        # Build rankings (descending by value)
        valid_sorted = valid.sort_values("_numeric_value", ascending=False)

        rankings: List[Dict[str, Any]] = []
        for rank, (_, row) in enumerate(valid_sorted.iterrows(), start=1):
            region_name = str(row.get("region_name", row["region_id"]))
            val = round(float(row["_numeric_value"]), 4)
            deviation = round(val - result.group_mean, 4) if result.group_mean is not None else None

            rankings.append({
                "rank": rank,
                "region_id": str(row["region_id"]),
                "region_name": region_name,
                "value": val,
                "unit": str(unit),
                "deviation_from_mean": deviation,
            })

        result.rankings = rankings

        if rankings:
            result.highest = rankings[0]
            result.lowest = rankings[-1]

        if result.regions_missing > 0:
            result.notes = (
                f"Ranking includes {result.regions_included} of {total_expected_regions} "
                f"expected regions. {result.regions_missing} region(s) have no observation."
            )

        return result

    # ------------------------------------------------------------------
    # E. Time-Based Analysis
    # ------------------------------------------------------------------

    def compute_time_analysis(
        self,
        indicator_code: str,
        geographic_level: str = "district",
    ) -> Dict[str, Any]:
        """Analyzes temporal patterns for an indicator, if repeated observations exist.

        Returns:
            Dict with time_series_available, periods, per-region values, and changes.
        """
        df = self._ensure_data()
        logger.info("Computing time-based analysis for %s", indicator_code)

        filtered = df[df["indicator_code"] == indicator_code].copy()
        if geographic_level and "geographic_level" in filtered.columns:
            filtered = filtered[filtered["geographic_level"] == geographic_level]

        periods = sorted(filtered["reference_period"].dropna().unique().tolist())

        result: Dict[str, Any] = {
            "indicator_code": indicator_code,
            "geographic_level": geographic_level,
            "periods_available": periods,
            "period_count": len(periods),
            "time_series_available": len(periods) > 1,
        }

        if len(periods) <= 1:
            result["notes"] = (
                f"Only {len(periods)} reference period(s) available for {indicator_code}. "
                "Time-series analysis requires observations from at least 2 distinct periods. "
                "This indicator currently has a single cross-sectional snapshot."
            )
            return result

        # Multi-period analysis
        filtered["_numeric_value"] = pd.to_numeric(filtered["value"], errors="coerce")

        period_summaries: List[Dict[str, Any]] = []
        for period in periods:
            period_data = filtered[filtered["reference_period"] == period]["_numeric_value"].dropna()
            period_summaries.append({
                "period": period,
                "count": len(period_data),
                "mean": round(float(period_data.mean()), 4) if len(period_data) > 0 else None,
                "median": round(float(period_data.median()), 4) if len(period_data) > 0 else None,
            })

        result["period_summaries"] = period_summaries
        result["notes"] = (
            f"{len(periods)} reference periods available. "
            "Changes between periods may reflect genuine trends, data revisions, "
            "or changes in measurement methodology."
        )

        return result

    # ------------------------------------------------------------------
    # F. Indicator Relationships
    # ------------------------------------------------------------------

    def compute_correlation_matrix(
        self,
        indicator_codes: Optional[List[str]] = None,
        reference_period: Optional[str] = None,
        geographic_level: str = "district",
    ) -> Dict[str, Any]:
        """Calculates pairwise correlations between compatible numeric indicators.

        Correlation does NOT establish causation. Sample sizes and limitations
        are explicitly reported.

        Args:
            indicator_codes: Specific indicators to include (all if None).
            reference_period: Filter for a single period (uses most common if None).
            geographic_level: Filter for a specific geographic level.

        Returns:
            Dict with correlation_matrix (DataFrame), pairwise results, and metadata.
        """
        df = self._ensure_data()
        logger.info("Computing correlation matrix")

        filtered = df.copy()
        if geographic_level and "geographic_level" in filtered.columns:
            filtered = filtered[filtered["geographic_level"] == geographic_level]

        if reference_period:
            filtered = filtered[filtered["reference_period"] == str(reference_period)]

        if indicator_codes:
            filtered = filtered[filtered["indicator_code"].isin(indicator_codes)]

        if filtered.empty:
            return {
                "correlation_matrix": None,
                "pairwise_results": [],
                "sample_size": 0,
                "notes": "No matching observations for correlation analysis.",
            }

        # Convert to wide format for correlation
        filtered["_numeric_value"] = pd.to_numeric(filtered["value"], errors="coerce")

        # Pivot: rows = regions, columns = indicators
        try:
            wide = filtered.pivot_table(
                index="region_id",
                columns="indicator_code",
                values="_numeric_value",
                aggfunc="first",
            )
        except Exception as exc:
            logger.warning("Could not pivot data for correlation: %s", exc)
            return {
                "correlation_matrix": None,
                "pairwise_results": [],
                "sample_size": 0,
                "notes": f"Failed to pivot data: {exc}",
            }

        if wide.shape[1] < 2:
            return {
                "correlation_matrix": None,
                "pairwise_results": [],
                "sample_size": len(wide),
                "notes": "Need at least 2 indicators for correlation analysis.",
            }

        # Compute pairwise correlations
        pairwise_results: List[CorrelationResult] = []
        corr_indicators = list(wide.columns)

        for i, ind_a in enumerate(corr_indicators):
            for ind_b in corr_indicators[i + 1:]:
                pair_data = wide[[ind_a, ind_b]].dropna()
                sample_size = len(pair_data)
                is_sufficient = sample_size >= MIN_CORRELATION_SAMPLE_SIZE

                corr_val = None
                if is_sufficient and pair_data[ind_a].std() > 0 and pair_data[ind_b].std() > 0:
                    corr_val = round(float(pair_data[ind_a].corr(pair_data[ind_b])), 4)

                notes_str = ""
                if not is_sufficient:
                    notes_str = (
                        f"Insufficient sample size ({sample_size} < {MIN_CORRELATION_SAMPLE_SIZE}). "
                        "Correlation not computed."
                    )
                else:
                    notes_str = (
                        "Correlation measures linear association only and "
                        "does not establish causation."
                    )

                pairwise_results.append(CorrelationResult(
                    indicator_a=ind_a,
                    indicator_b=ind_b,
                    reference_period=reference_period or "mixed",
                    geographic_level=geographic_level,
                    sample_size=sample_size,
                    correlation=corr_val,
                    is_sufficient=is_sufficient,
                    notes=notes_str,
                ))

        # Full correlation matrix (only where sufficient data exists)
        corr_matrix = None
        if len(wide) >= MIN_CORRELATION_SAMPLE_SIZE:
            corr_matrix = wide.corr()

        return {
            "correlation_matrix": corr_matrix,
            "pairwise_results": pairwise_results,
            "indicators": corr_indicators,
            "sample_size": len(wide),
            "notes": (
                "Pearson correlation coefficients. "
                "Correlation does not establish causation. "
                f"Computed across {len(wide)} regions with {len(corr_indicators)} indicators."
            ),
        }

    def compute_pairwise_scatter_data(
        self,
        indicator_a: str,
        indicator_b: str,
        reference_period: Optional[str] = None,
        geographic_level: str = "district",
    ) -> Dict[str, Any]:
        """Prepares scatter plot data for two indicators across regions.

        Returns:
            Dict with x, y, region labels, sample_size, and metadata.
        """
        df = self._ensure_data()

        filtered = df.copy()
        if geographic_level and "geographic_level" in filtered.columns:
            filtered = filtered[filtered["geographic_level"] == geographic_level]

        if reference_period:
            filtered = filtered[filtered["reference_period"] == str(reference_period)]

        filtered["_numeric_value"] = pd.to_numeric(filtered["value"], errors="coerce")

        data_a = filtered[filtered["indicator_code"] == indicator_a][
            ["region_id", "region_name", "_numeric_value"]
        ].rename(columns={"_numeric_value": "x"})

        data_b = filtered[filtered["indicator_code"] == indicator_b][
            ["region_id", "_numeric_value"]
        ].rename(columns={"_numeric_value": "y"})

        merged = data_a.merge(data_b, on="region_id", how="inner").dropna()

        unit_a = "unknown"
        unit_b = "unknown"
        a_units = filtered.loc[filtered["indicator_code"] == indicator_a, "unit"].dropna().unique()
        b_units = filtered.loc[filtered["indicator_code"] == indicator_b, "unit"].dropna().unique()
        if len(a_units) > 0:
            unit_a = str(a_units[0])
        if len(b_units) > 0:
            unit_b = str(b_units[0])

        return {
            "indicator_a": indicator_a,
            "indicator_b": indicator_b,
            "unit_a": unit_a,
            "unit_b": unit_b,
            "regions": merged["region_name"].tolist() if "region_name" in merged.columns else merged["region_id"].tolist(),
            "x_values": merged["x"].tolist(),
            "y_values": merged["y"].tolist(),
            "sample_size": len(merged),
            "notes": (
                "Each point represents a district. "
                "Correlation does not establish causation."
            ),
        }

    # ------------------------------------------------------------------
    # Unified EDA Report Generation
    # ------------------------------------------------------------------

    def generate_eda_report(self) -> Dict[str, Any]:
        """Generates a comprehensive EDA report combining all analyses.

        Returns:
            Dict containing overview, quality, indicator_stats, and metadata.
        """
        df = self._ensure_data()
        logger.info("Generating full EDA report for %d observations", len(df))

        report: Dict[str, Any] = {
            "overview": None,
            "quality": None,
            "indicator_statistics": [],
            "time_analysis_available": False,
            "correlation_available": False,
            "metadata": {
                "total_observations": len(df),
                "analysis_notes": [],
            },
        }

        # Overview
        try:
            report["overview"] = self.compute_dataset_overview()
        except Exception as exc:
            logger.error("Failed to compute dataset overview: %s", exc)
            report["metadata"]["analysis_notes"].append(f"Overview failed: {exc}")

        # Quality
        try:
            report["quality"] = self.compute_data_quality()
        except Exception as exc:
            logger.error("Failed to compute data quality: %s", exc)
            report["metadata"]["analysis_notes"].append(f"Quality analysis failed: {exc}")

        # Indicator stats
        try:
            report["indicator_statistics"] = self.compute_indicator_statistics()
        except Exception as exc:
            logger.error("Failed to compute indicator statistics: %s", exc)
            report["metadata"]["analysis_notes"].append(f"Statistics failed: {exc}")

        # Time analysis availability
        if report.get("overview") and report["overview"].distinct_reference_periods > 1:
            report["time_analysis_available"] = True
        else:
            report["metadata"]["analysis_notes"].append(
                "Time-series analysis unavailable: insufficient reference periods."
            )

        # Correlation availability
        if report.get("overview") and report["overview"].distinct_indicators >= 2:
            report["correlation_available"] = True

        return report
