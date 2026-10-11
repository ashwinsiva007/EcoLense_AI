"""Analytics and regional indicator modeling package for EconLens AI."""

from src.analytics.exploratory_analysis import (
    CorrelationResult,
    DataQualityProfile,
    DatasetOverview,
    ExploratoryAnalyzer,
    IndicatorStats,
    RegionalComparison,
    SummaryStatistics,
)
from src.analytics.eda_report import (
    generate_eda_report_markdown,
    generate_eda_summary_json,
    generate_regional_summary_table,
)
from src.analytics.opportunity_scoring import OpportunityScorer

__all__ = [
    # Core EDA
    "ExploratoryAnalyzer",
    "SummaryStatistics",
    "DatasetOverview",
    "DataQualityProfile",
    "IndicatorStats",
    "RegionalComparison",
    "CorrelationResult",
    # Reports
    "generate_eda_summary_json",
    "generate_eda_report_markdown",
    "generate_regional_summary_table",
    # Scoring (future)
    "OpportunityScorer",
]
