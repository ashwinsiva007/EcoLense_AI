"""Dataset Source Registry and Provenance Tracking for EconLens AI.

Manages data provenance, publisher citations, licensing conditions,
geographic coverage, and explicit verification status lifecycle
(planned, acquired, validated, rejected) for all regional data sources.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.utils.logging_config import get_logger

logger = get_logger("data.source_registry")

# Recognized verification states
VALID_VERIFICATION_STATUSES: Set[str] = {
    "planned",
    "acquired",
    "validated",
    "rejected",
}


@dataclass
class DatasetSource:
    """Metadata representing an external data source and its verification state."""

    source_id: str
    dataset_name: str
    publisher: str
    source_url: str
    geographic_coverage: str
    geographic_level: str
    reference_period: str
    retrieval_date: Optional[str] = None
    file_path: Optional[str] = None
    license: str = "unknown"
    data_format: str = "csv"
    update_frequency: str = "unknown"
    verification_status: str = "planned"
    notes: str = ""

    def __post_init__(self) -> None:
        """Validates verification status."""
        self.verification_status = self.verification_status.strip().lower()
        if self.verification_status not in VALID_VERIFICATION_STATUSES:
            raise ValueError(
                f"Invalid verification status '{self.verification_status}'. "
                f"Must be one of {sorted(VALID_VERIFICATION_STATUSES)}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Converts source object to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DatasetSource:
        """Constructs DatasetSource from dictionary."""
        return cls(
            source_id=data["source_id"],
            dataset_name=data["dataset_name"],
            publisher=data["publisher"],
            source_url=data.get("source_url", ""),
            geographic_coverage=data.get("geographic_coverage", "unknown"),
            geographic_level=data.get("geographic_level", "district"),
            reference_period=data.get("reference_period", "unknown"),
            retrieval_date=data.get("retrieval_date"),
            file_path=data.get("file_path"),
            license=data.get("license", "unknown"),
            data_format=data.get("data_format", "csv"),
            update_frequency=data.get("update_frequency", "unknown"),
            verification_status=data.get("verification_status", "planned"),
            notes=data.get("notes", ""),
        )


class SourceRegistry:
    """In-memory registry and disk persistence for data sources."""

    def __init__(self, sources: Optional[List[DatasetSource]] = None) -> None:
        self._sources: Dict[str, DatasetSource] = {}
        if sources:
            for s in sources:
                self.register(s)

    def register(self, source: DatasetSource) -> None:
        """Registers a data source. Overwrites if source_id already exists."""
        self._sources[source.source_id] = source
        logger.debug("Registered source '%s' (status: %s)", source.source_id, source.verification_status)

    def get(self, source_id: str) -> Optional[DatasetSource]:
        """Retrieves a source by its identifier."""
        return self._sources.get(source_id)

    def has(self, source_id: str) -> bool:
        """Checks if a source ID is registered."""
        return source_id in self._sources

    def update_status(
        self, source_id: str, new_status: str, notes: Optional[str] = None
    ) -> None:
        """Updates the verification status and optional notes of a source."""
        source = self.get(source_id)
        if not source:
            raise KeyError(f"Source ID '{source_id}' not found in registry.")

        normalized_status = new_status.strip().lower()
        if normalized_status not in VALID_VERIFICATION_STATUSES:
            raise ValueError(
                f"Invalid verification status '{normalized_status}'. "
                f"Must be one of {sorted(VALID_VERIFICATION_STATUSES)}"
            )

        source.verification_status = normalized_status
        if notes:
            source.notes = f"{source.notes} | {notes}".strip(" |")
        logger.info("Updated source '%s' status to '%s'", source_id, normalized_status)

    def list_sources(self, status: Optional[str] = None) -> List[DatasetSource]:
        """Returns all sources, optionally filtered by verification status."""
        if status:
            target = status.strip().lower()
            return [s for s in self._sources.values() if s.verification_status == target]
        return list(self._sources.values())

    def get_status_summary(self) -> Dict[str, int]:
        """Returns counts of sources across each verification status."""
        summary = {st: 0 for st in sorted(VALID_VERIFICATION_STATUSES)}
        for s in self._sources.values():
            summary[s.verification_status] = summary.get(s.verification_status, 0) + 1
        return summary

    def to_json(self) -> str:
        """Serializes registry to a JSON string."""
        data = {s_id: s.to_dict() for s_id, s in self._sources.items()}
        return json.dumps(data, indent=2)

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Saves registry to a JSON file on disk."""
        target_path = Path(file_path).resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self.to_json(), encoding="utf-8")
        logger.info("Saved %d sources to %s", len(self._sources), target_path)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> SourceRegistry:
        """Loads registry from a JSON file on disk."""
        target_path = Path(file_path).resolve()
        if not target_path.exists():
            logger.warning("Source registry file not found at %s. Returning empty registry.", target_path)
            return cls()

        content = target_path.read_text(encoding="utf-8").strip()
        if not content:
            return cls()

        data = json.loads(content)
        sources: List[DatasetSource] = []
        for s_data in data.values():
            sources.append(DatasetSource.from_dict(s_data))
        return cls(sources=sources)
