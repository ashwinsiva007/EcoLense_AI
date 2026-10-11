"""Data Quality and Pipeline Readiness Reporting for EconLens AI.

Summarizes dataset completeness, distinct geographical entities, indicator coverage,
source registry alignment, missingness distribution, and structural validity
before data enters exploratory analysis or opportunity scoring.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from src.data.source_registry import SourceRegistry
from src.data.validation import DataValidator, ValidationResult
from src.utils.logging_config import get_logger

logger = get_logger("data.quality_report")


def generate_quality_report(
    df: pd.DataFrame,
    source_registry: Optional[SourceRegistry] = None,
    validator: Optional[DataValidator] = None,
) -> Dict[str, Any]:
    """Generates a comprehensive dataset quality and readiness summary.

    Args:
        df: Input DataFrame (canonical long-form or raw).
        source_registry: Optional SourceRegistry instance for provenance auditing.
        validator: Optional DataValidator instance. If None, instantiates default validator.

    Returns:
        Dict[str, Any]: Structured quality diagnostic report.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

    active_validator = validator or DataValidator(source_registry=source_registry)
    val_result: ValidationResult = active_validator.validate_canonical(df)

    rows, cols = df.shape

    # Geographic coverage
    distinct_regions: List[str] = []
    if "region_id" in df.columns:
        distinct_regions = sorted(df["region_id"].dropna().astype(str).unique().tolist())

    # Indicator coverage
    distinct_indicators: List[str] = []
    if "indicator_code" in df.columns:
        distinct_indicators = sorted(df["indicator_code"].dropna().astype(str).unique().tolist())

    # Temporal coverage
    distinct_periods: List[str] = []
    if "reference_period" in df.columns:
        distinct_periods = sorted(df["reference_period"].dropna().astype(str).unique().tolist())

    # Missing values per column
    missing_by_col = {
        col: int(df[col].isna().sum())
        for col in df.columns
        if int(df[col].isna().sum()) > 0
    }

    # Numeric observation check
    numeric_stats: Dict[str, Any] = {}
    if "value" in df.columns:
        converted = pd.to_numeric(df["value"], errors="coerce")
        valid_numeric_count = int(converted.notna().sum())
        null_or_invalid_count = rows - valid_numeric_count
        numeric_stats = {
            "valid_numeric_observations": valid_numeric_count,
            "missing_or_unparseable_observations": null_or_invalid_count,
            "min_observed_value": float(converted.min()) if valid_numeric_count > 0 else None,
            "max_observed_value": float(converted.max()) if valid_numeric_count > 0 else None,
            "mean_observed_value": float(converted.mean()) if valid_numeric_count > 0 else None,
        }

    # Source provenance audit
    source_audit: Dict[str, Any] = {}
    if "source_id" in df.columns:
        source_ids_found = sorted(df["source_id"].dropna().astype(str).unique().tolist())
        registered_status: Dict[str, str] = {}
        for s_id in source_ids_found:
            if source_registry and source_registry.has(s_id):
                src_obj = source_registry.get(s_id)
                registered_status[s_id] = src_obj.verification_status if src_obj else "unknown"
            else:
                registered_status[s_id] = "unregistered"
        source_audit = {
            "source_ids_found": source_ids_found,
            "source_statuses": registered_status,
        }

    readiness_status = "READY" if val_result.is_valid else "NEEDS_REVISION"

    report = {
        "readiness_status": readiness_status,
        "total_rows": rows,
        "total_columns": cols,
        "distinct_region_count": len(distinct_regions),
        "distinct_regions": distinct_regions,
        "distinct_indicator_count": len(distinct_indicators),
        "distinct_indicators": distinct_indicators,
        "distinct_period_count": len(distinct_periods),
        "distinct_reference_periods": distinct_periods,
        "missing_values_by_column": missing_by_col,
        "duplicate_observation_keys": val_result.duplicate_count,
        "numeric_summary": numeric_stats,
        "source_audit": source_audit,
        "validation_errors": val_result.errors,
        "validation_warnings": val_result.warnings,
        "is_valid": val_result.is_valid,
    }

    return report


def format_quality_report_markdown(report: Dict[str, Any]) -> str:
    """Formats a quality report dictionary into clean Markdown text."""
    lines = [
        f"### 📋 Dataset Quality & Readiness Report: **{report['readiness_status']}**",
        "",
        f"- **Rows & Columns:** {report['total_rows']} rows x {report['total_columns']} columns",
        f"- **Distinct Regions:** {report['distinct_region_count']} ({', '.join(report['distinct_regions'][:5])}{'...' if len(report['distinct_regions']) > 5 else ''})",
        f"- **Distinct Indicators:** {report['distinct_indicator_count']} ({', '.join(report['distinct_indicators'][:5])}{'...' if len(report['distinct_indicators']) > 5 else ''})",
        f"- **Reference Periods:** {report['distinct_period_count']} ({', '.join(report['distinct_reference_periods'])})",
        f"- **Duplicate Observation Keys:** {report['duplicate_observation_keys']}",
    ]

    if report["missing_values_by_column"]:
        lines.append("- **Missing Value Distribution:**")
        for col, count in report["missing_values_by_column"].items():
            lines.append(f"  - `{col}`: {count} missing")
    else:
        lines.append("- **Missing Values:** None (100% complete across required fields)")

    if report["validation_errors"]:
        lines.append("")
        lines.append("#### ❌ Validation Errors:")
        for err in report["validation_errors"]:
            lines.append(f"- {err}")

    if report["validation_warnings"]:
        lines.append("")
        lines.append("#### ⚠️ Validation Warnings:")
        for warn in report["validation_warnings"]:
            lines.append(f"- {warn}")

    return "\n".join(lines)
