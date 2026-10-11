"""EDA Report Generator for EconLens AI.

Produces machine-readable (JSON) and human-readable (Markdown) EDA reports
from canonical long-form observation data. Reports capture dataset overview,
data quality, indicator statistics, and analytical metadata with full
source provenance.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.analytics.exploratory_analysis import (
    DatasetOverview,
    DataQualityProfile,
    ExploratoryAnalyzer,
    IndicatorStats,
    RegionalComparison,
)
from src.utils.logging_config import get_logger

logger = get_logger("analytics.eda_report")


def generate_eda_summary_json(
    analyzer: ExploratoryAnalyzer,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Generates a machine-readable EDA summary.

    Args:
        analyzer: Configured ExploratoryAnalyzer with data loaded.
        output_path: Optional path to save JSON file.

    Returns:
        Dict containing the complete EDA summary.
    """
    logger.info("Generating EDA summary JSON")

    overview = analyzer.compute_dataset_overview()
    quality = analyzer.compute_data_quality()
    indicator_stats = analyzer.compute_indicator_statistics()

    summary = {
        "generated_at": datetime.now().isoformat(),
        "stage": "Stage 3 — Exploratory Data Analysis",
        "overview": {
            "total_observations": overview.total_observations,
            "valid_observations": overview.valid_observations,
            "distinct_regions": overview.distinct_regions,
            "distinct_indicators": overview.distinct_indicators,
            "reference_periods": overview.reference_periods,
            "source_ids": overview.source_ids,
            "geographic_levels": overview.geographic_levels,
            "quality_statuses": overview.quality_statuses,
        },
        "quality": {
            "total_rows": quality.total_rows,
            "total_columns": quality.total_columns,
            "missing_by_column": quality.missing_by_column,
            "missing_pct_by_column": quality.missing_pct_by_column,
            "duplicate_count": quality.duplicate_count,
            "invalid_numeric_count": quality.invalid_numeric_count,
            "infinite_count": quality.infinite_count,
        },
        "indicator_statistics": [
            {
                "indicator_code": s.indicator_code,
                "indicator_name": s.indicator_name,
                "unit": s.unit,
                "reference_period": s.reference_period,
                "geographic_level": s.geographic_level,
                "count": s.count,
                "mean": s.mean,
                "median": s.median,
                "std": s.std,
                "min": s.min_val,
                "max": s.max_val,
                "q25": s.q25,
                "q75": s.q75,
                "iqr": s.iqr,
                "source_id": s.source_id,
                "notes": s.notes,
            }
            for s in indicator_stats
        ],
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info("EDA summary saved to %s", output_path)

    return summary


def generate_eda_report_markdown(
    analyzer: ExploratoryAnalyzer,
    output_path: Optional[Path] = None,
) -> str:
    """Generates a human-readable Markdown EDA report.

    Args:
        analyzer: Configured ExploratoryAnalyzer with data loaded.
        output_path: Optional path to save Markdown file.

    Returns:
        Markdown string of the complete EDA report.
    """
    logger.info("Generating EDA Markdown report")

    overview = analyzer.compute_dataset_overview()
    quality = analyzer.compute_data_quality()
    indicator_stats = analyzer.compute_indicator_statistics()

    lines: List[str] = []

    # Header
    lines.append("# EconLens AI — Exploratory Data Analysis Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Stage:** 3 — Exploratory Data Analysis")
    lines.append(f"**Study Geography:** Tamil Nadu (32 Baseline Districts)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 1. Dataset Overview
    lines.append("## 1. Dataset Overview")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|:---|:---|")
    lines.append(f"| Total Observations | {overview.total_observations:,} |")
    lines.append(f"| Valid Numeric Observations | {overview.valid_observations:,} |")
    lines.append(f"| Distinct Regions | {overview.distinct_regions} |")
    lines.append(f"| Distinct Indicators | {overview.distinct_indicators} |")
    lines.append(f"| Reference Periods | {', '.join(overview.reference_periods)} |")
    lines.append(f"| Geographic Levels | {', '.join(overview.geographic_levels)} |")
    lines.append(f"| Data Sources | {', '.join(overview.source_ids)} |")
    lines.append("")

    if overview.quality_statuses:
        lines.append("**Quality Status Distribution:**")
        for status, count in overview.quality_statuses.items():
            lines.append(f"- `{status}`: {count} observations")
        lines.append("")

    # 2. Data Quality
    lines.append("## 2. Data Quality Profile")
    lines.append("")
    lines.append(f"- **Total Rows:** {quality.total_rows:,}")
    lines.append(f"- **Total Columns:** {quality.total_columns}")
    lines.append(f"- **Duplicate Observation Keys:** {quality.duplicate_count}")
    lines.append(f"- **Non-Numeric Values:** {quality.invalid_numeric_count}")
    lines.append(f"- **Infinite Values:** {quality.infinite_count}")
    lines.append("")

    if quality.missing_by_column:
        lines.append("### Missing Values by Column")
        lines.append("")
        lines.append("| Column | Missing Count | Missing % |")
        lines.append("|:---|---:|---:|")
        for col, count in quality.missing_by_column.items():
            pct = quality.missing_pct_by_column.get(col, 0)
            lines.append(f"| `{col}` | {count} | {pct:.1f}% |")
        lines.append("")
    else:
        lines.append("**Missing Values:** None detected (100% complete across all columns).")
        lines.append("")

    # 3. Indicator Statistics
    lines.append("## 3. Indicator Descriptive Statistics")
    lines.append("")

    if indicator_stats:
        lines.append("| Indicator | Unit | Period | N | Mean | Median | Std | Min | Max | IQR |")
        lines.append("|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|")
        for s in indicator_stats:
            mean_s = f"{s.mean:,.2f}" if s.mean is not None else "—"
            med_s = f"{s.median:,.2f}" if s.median is not None else "—"
            std_s = f"{s.std:,.2f}" if s.std is not None else "—"
            min_s = f"{s.min_val:,.2f}" if s.min_val is not None else "—"
            max_s = f"{s.max_val:,.2f}" if s.max_val is not None else "—"
            iqr_s = f"{s.iqr:,.2f}" if s.iqr is not None else "—"
            lines.append(
                f"| `{s.indicator_code}` | {s.unit} | {s.reference_period} | "
                f"{s.count} | {mean_s} | {med_s} | {std_s} | {min_s} | {max_s} | {iqr_s} |"
            )
        lines.append("")
    else:
        lines.append("No indicator statistics computed.")
        lines.append("")

    # 4. Time-Series Availability
    lines.append("## 4. Time-Series Analysis Availability")
    lines.append("")
    periods = overview.reference_periods
    if len(periods) > 1:
        lines.append(f"**{len(periods)} reference periods detected:** {', '.join(periods)}")
        lines.append("")
        lines.append(
            "Time-series analysis is possible for indicators with observations across "
            "multiple periods. Changes between periods may reflect genuine trends, "
            "data revisions, or changes in measurement methodology."
        )
    else:
        lines.append(
            "**Time-series analysis unavailable.** The current dataset contains observations "
            f"from {'only ' + periods[0] if periods else 'no'} reference period. "
            "Longitudinal trend analysis requires observations from at least 2 distinct periods."
        )
    lines.append("")

    # 5. Caveats
    lines.append("## 5. Analytical Caveats and Limitations")
    lines.append("")
    lines.append("- All statistics are computed from validated canonical observations only.")
    lines.append("- Missing values are preserved as NaN (not replaced with zero per ADR 008).")
    lines.append("- Correlation measures linear association and does not establish causation.")
    lines.append("- Rankings compare districts within the same period and geographic level only.")
    lines.append("- Census 2011 indicators reflect 2011 values; newer datasets reflect 2020-23.")
    lines.append("- Boundary harmonization follows the 32-district Census 2011 baseline (ADR 010).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by EconLens AI — Stage 3 EDA Pipeline*")

    report_text = "\n".join(lines)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        logger.info("EDA Markdown report saved to %s", output_path)

    return report_text


def generate_regional_summary_table(
    analyzer: ExploratoryAnalyzer,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Creates a wide-format regional summary table.

    Pivots canonical observations so rows = regions, columns = indicators.

    Args:
        analyzer: Configured ExploratoryAnalyzer with data loaded.
        output_path: Optional path to save CSV.

    Returns:
        Wide-format DataFrame.
    """
    df = analyzer._ensure_data()
    logger.info("Generating regional summary table")

    df_copy = df.copy()
    df_copy["_numeric_value"] = pd.to_numeric(df_copy["value"], errors="coerce")

    try:
        wide = df_copy.pivot_table(
            index=["region_id", "region_name"],
            columns="indicator_code",
            values="_numeric_value",
            aggfunc="first",
        )
        wide = wide.reset_index()
        wide.columns.name = None  # Clean column name
    except Exception as exc:
        logger.error("Failed to create regional summary table: %s", exc)
        return pd.DataFrame()

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wide.to_csv(output_path, index=False)
        logger.info("Regional summary table saved to %s", output_path)

    return wide
