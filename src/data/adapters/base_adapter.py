"""Base adapter contract for mapping raw source data into canonical observations.

Enforces uniform interface across all publisher-specific parsers. Ensures
rejected records are tracked with explicit error reasons rather than silently dropped.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.data.schema import CANONICAL_COLUMNS, REQUIRED_COLUMNS


@dataclass
class AdapterResult:
    """Standardized output produced by a source-specific adapter."""

    source_id: str
    observations: pd.DataFrame
    raw_row_count: int
    parsed_observation_count: int
    rejected_records: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_rejections(self) -> bool:
        """Returns True if any rows or records could not be parsed."""
        return len(self.rejected_records) > 0


class BaseSourceAdapter(ABC):
    """Abstract base class for all regional dataset ingestion adapters."""

    def __init__(self, source_id: str) -> None:
        """Initializes adapter with its corresponding registry source identifier.

        Args:
            source_id: Registered source ID (e.g. 'SRC_CENSUS_2011_TN').
        """
        self.source_id = source_id

    @abstractmethod
    def parse(self, raw_path: Path) -> AdapterResult:
        """Parses an immutable raw dataset file into canonical long-form observations.

        Args:
            raw_path: Absolute or relative Path to raw input file.

        Returns:
            AdapterResult containing canonical observations and rejected record diagnostics.
        """
        raise NotImplementedError

    @staticmethod
    def format_district_id(state_code: str, district_code: Any) -> str:
        """Constructs standardized composite regional ID e.g. '33_602'.

        Args:
            state_code: Two-digit state code (e.g. '33' for Tamil Nadu).
            district_code: District numeric or alphanumeric code.

        Returns:
            Standardized string identifier.
        """
        clean_state = str(state_code).strip().zfill(2)
        clean_dist = str(district_code).strip()
        return f"{clean_state}_{clean_dist}"

    @staticmethod
    def ensure_canonical_structure(df: pd.DataFrame) -> pd.DataFrame:
        """Ensures all canonical columns exist in the DataFrame in proper sequence."""
        for col in CANONICAL_COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[CANONICAL_COLUMNS].copy()
