"""Canonical Regional Observation Data Schema for EconLens AI.

Defines the standard long-form observation model, field types, primary keys,
geographic levels, and indicator bound constraints across all datasets.
"""

from __future__ import annotations

import re
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

# All recognized canonical columns in order
CANONICAL_COLUMNS: List[str] = [
    "region_id",
    "region_name",
    "parent_region_id",
    "geographic_level",
    "indicator_code",
    "indicator_name",
    "value",
    "unit",
    "reference_period",
    "source_id",
    "source_record_id",
    "collection_date",
    "quality_status",
    "notes",
]

# Mandatory columns that must be present and non-null in any canonical dataset
REQUIRED_COLUMNS: List[str] = [
    "region_id",
    "region_name",
    "geographic_level",
    "indicator_code",
    "indicator_name",
    "value",
    "unit",
    "reference_period",
    "source_id",
]

# Optional contextual metadata columns
OPTIONAL_COLUMNS: List[str] = [
    "parent_region_id",
    "source_record_id",
    "collection_date",
    "quality_status",
    "notes",
]

# Composite primary key for unique observation resolution
PRIMARY_KEY_COLUMNS: List[str] = [
    "region_id",
    "indicator_code",
    "reference_period",
]

# Supported administrative / geographic hierarchy levels
VALID_GEOGRAPHIC_LEVELS: FrozenSet[str] = frozenset(
    [
        "district",
        "state",
        "block",
        "subdistrict",
        "national",
    ]
)

# Supported reference period regex patterns:
# - Single calendar/census year: '2011', '2021'
# - Short fiscal/survey year: '2021-22'
# - Long fiscal/survey year: '2021-2022'
# - Quarter prefix: 'Q1-2023'
# - Quarter suffix: '2023-Q1'
REFERENCE_PERIOD_PATTERN = re.compile(
    r"^(\d{4}|\d{4}-\d{2}|\d{4}-\d{4}|Q[1-4]-\d{4}|\d{4}-Q[1-4])$"
)

# ISO date regex (YYYY-MM-DD) for collection_date
COLLECTION_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Indicator-specific bounds rules.
# Key is either indicator_code or measurement unit.
# Value is a tuple of (min_bound, max_bound). None indicates unconstrained.
INDICATOR_BOUNDS_RULES: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    # Unit-level general rules
    "percentage": (0.0, 100.0),
    "percent": (0.0, 100.0),
    "ratio": (0.0, None),
    "count": (0.0, None),
    # Specific indicator rules
    "LIT_RATE_TOT": (0.0, 100.0),
    "LIT_RATE_FEM": (0.0, 100.0),
    "WPR_TOT": (0.0, 100.0),
    "WPR_FEM": (0.0, 100.0),
    "FLFPR_TOT": (0.0, 100.0),
    "ROAD_DENSITY": (0.0, None),
    "ROAD_SURFACED_KM": (0.0, None),
    "POPULATION_TOT": (1.0, None),
    "CREDIT_DEPOSIT_RATIO": (0.0, None),
    "BANK_CREDIT_AMT": (0.0, None),
    "BANK_DEPOSIT_AMT": (0.0, None),
    "MSME_MICRO_COUNT": (0.0, None),
    "MSME_SMALL_COUNT": (0.0, None),
    "MSME_MEDIUM_COUNT": (0.0, None),
    "MSME_TOTAL_COUNT": (0.0, None),
}


def is_valid_reference_period(period: Any) -> bool:
    """Checks whether a given reference period string matches accepted formats."""
    if not isinstance(period, str):
        return False
    return bool(REFERENCE_PERIOD_PATTERN.match(period.strip()))


def is_valid_geographic_level(geo_level: Any) -> bool:
    """Checks whether a geographic level is recognized by the platform."""
    if not isinstance(geo_level, str):
        return False
    return geo_level.strip().lower() in VALID_GEOGRAPHIC_LEVELS


def get_indicator_bounds(
    indicator_code: str, unit: str
) -> Tuple[Optional[float], Optional[float]]:
    """Returns (min_val, max_val) bounds for an indicator or unit if defined.

    Checks indicator_code first, then falls back to unit. If no specific
    rule applies, returns (None, None).
    """
    if indicator_code in INDICATOR_BOUNDS_RULES:
        return INDICATOR_BOUNDS_RULES[indicator_code]
    normalized_unit = unit.strip().lower()
    if normalized_unit in INDICATOR_BOUNDS_RULES:
        return INDICATOR_BOUNDS_RULES[normalized_unit]
    return (None, None)
