"""Tests for dataset source registry, provenance modeling, and status transitions."""

from pathlib import Path
import pytest

from src.data.source_registry import DatasetSource, SourceRegistry


def test_source_lifecycle_and_registration() -> None:
    """Verifies registering a source and updating its verification status."""
    registry = SourceRegistry()

    source = DatasetSource(
        source_id="SRC_TEST_01",
        dataset_name="Test Economic Survey",
        publisher="State Directorate of Economics",
        source_url="https://example.gov/data",
        geographic_coverage="State Alpha",
        geographic_level="district",
        reference_period="2020-21",
        verification_status="planned",
    )

    registry.register(source)
    assert registry.has("SRC_TEST_01") is True
    assert registry.get("SRC_TEST_01").verification_status == "planned"

    # Status transition to acquired
    registry.update_status("SRC_TEST_01", "acquired", notes="Downloaded raw CSV")
    assert registry.get("SRC_TEST_01").verification_status == "acquired"
    assert "Downloaded raw CSV" in registry.get("SRC_TEST_01").notes

    # Status transition to validated
    registry.update_status("SRC_TEST_01", "validated", notes="Schema and bounds verified")
    assert registry.get("SRC_TEST_01").verification_status == "validated"


def test_invalid_status_rejected() -> None:
    """Verifies that unauthorized verification statuses are rejected."""
    with pytest.raises(ValueError):
        DatasetSource(
            source_id="BAD_STATUS",
            dataset_name="Bad Source",
            publisher="Test",
            source_url="",
            geographic_coverage="",
            geographic_level="district",
            reference_period="2021",
            verification_status="arbitrary_unverified_status",
        )

    registry = SourceRegistry()
    valid_source = DatasetSource(
        source_id="S01",
        dataset_name="Valid Source",
        publisher="Test",
        source_url="",
        geographic_coverage="",
        geographic_level="district",
        reference_period="2021",
        verification_status="planned",
    )
    registry.register(valid_source)

    with pytest.raises(ValueError):
        registry.update_status("S01", "unapproved_status")


def test_status_summary_and_filtering() -> None:
    """Verifies registry summary counts and status filtering."""
    s1 = DatasetSource(
        source_id="S1", dataset_name="N1", publisher="P", source_url="",
        geographic_coverage="C", geographic_level="district", reference_period="2021",
        verification_status="planned",
    )
    s2 = DatasetSource(
        source_id="S2", dataset_name="N2", publisher="P", source_url="",
        geographic_coverage="C", geographic_level="district", reference_period="2021",
        verification_status="validated",
    )
    s3 = DatasetSource(
        source_id="S3", dataset_name="N3", publisher="P", source_url="",
        geographic_coverage="C", geographic_level="district", reference_period="2021",
        verification_status="rejected",
    )

    registry = SourceRegistry([s1, s2, s3])
    summary = registry.get_status_summary()

    assert summary["planned"] == 1
    assert summary["validated"] == 1
    assert summary["rejected"] == 1
    assert summary["acquired"] == 0

    assert len(registry.list_sources(status="validated")) == 1
    assert len(registry.list_sources()) == 3


def test_disk_save_and_load(tmp_path: Path) -> None:
    """Verifies saving registry to JSON and loading it back."""
    registry_file = tmp_path / "metadata" / "test_registry.json"

    source = DatasetSource(
        source_id="PERSIST_01",
        dataset_name="Persistent Registry Test",
        publisher="Test Publisher",
        source_url="https://test.org",
        geographic_coverage="National",
        geographic_level="state",
        reference_period="2019-20",
        verification_status="acquired",
    )

    reg = SourceRegistry([source])
    reg.save_to_file(registry_file)
    assert registry_file.exists()

    loaded_reg = SourceRegistry.load_from_file(registry_file)
    assert loaded_reg.has("PERSIST_01")
    assert loaded_reg.get("PERSIST_01").dataset_name == "Persistent Registry Test"


def test_load_existing_project_registry() -> None:
    """Verifies that the project source_registry.json loads and contains example entries."""
    proj_registry_path = Path("data/metadata/source_registry.json")
    assert proj_registry_path.exists()

    reg = SourceRegistry.load_from_file(proj_registry_path)
    assert reg.has("SRC_EXAMPLE_SYNTHETIC")
    example_src = reg.get("SRC_EXAMPLE_SYNTHETIC")
    assert example_src.verification_status == "validated"
    assert "EXAMPLE ONLY" in example_src.notes
