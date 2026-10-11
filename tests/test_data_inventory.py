"""Tests for DataInventoryManager and coverage reporting in EconLens AI."""

from pathlib import Path
import json
import pandas as pd
import pytest

from src.data.inventory import DataInventoryManager, DatasetInventoryEntry
from src.data.source_registry import SourceRegistry
from config.settings import get_settings


@pytest.fixture
def test_registry() -> SourceRegistry:
    """Loads source registry from project metadata."""
    settings = get_settings()
    reg_path = settings.metadata_data_dir / "source_registry.json"
    return SourceRegistry.load_from_file(reg_path)


def test_build_inventory_structure(test_registry: SourceRegistry) -> None:
    """DataInventoryManager should construct structured inventory entries."""
    mgr = DataInventoryManager()
    entries = mgr.build_inventory(test_registry)

    assert len(entries) >= 5
    dataset_ids = [e.dataset_id for e in entries]
    assert "SRC_CENSUS_2011_TN" in dataset_ids
    assert "SRC_UDYAM_MSME_TN_2023" in dataset_ids
    assert "SRC_RBI_BANKING_TN_2021" in dataset_ids
    assert "SRC_TN_DOES_INFRA_2021" in dataset_ids
    assert "SRC_PLANNED_PLFS_NSSO_2022" in dataset_ids

    # Planned entry check
    plfs_entry = next(e for e in entries if e.dataset_id == "SRC_PLANNED_PLFS_NSSO_2022")
    assert plfs_entry.acquisition_status == "planned"
    assert plfs_entry.requires_manual_download is True
    assert "PLFS" in plfs_entry.title


def test_export_inventory_json(tmp_path: Path, test_registry: SourceRegistry) -> None:
    """DataInventoryManager should export valid JSON inventory."""
    mgr = DataInventoryManager()
    entries = mgr.build_inventory(test_registry)
    output_json = tmp_path / "data_inventory_test.json"

    mgr.export_inventory_json(entries, output_json)

    assert output_json.exists()
    data = json.loads(output_json.read_text(encoding="utf-8"))
    assert "datasets" in data
    assert "total_datasets" in data
    assert data["total_datasets"] == len(entries)
    assert data["acquired_count"] >= 4


def test_generate_coverage_report_markdown(tmp_path: Path, test_registry: SourceRegistry) -> None:
    """Coverage report should include executive summary and boundary disclosures."""
    mgr = DataInventoryManager()
    entries = mgr.build_inventory(test_registry)
    output_md = tmp_path / "data_coverage_report_test.md"

    report_str = mgr.generate_coverage_report_markdown(entries, output_path=output_md)

    assert output_md.exists()
    assert "# EconLens AI — Dataset Inventory & Coverage Report" in report_str
    assert "Tamil Nadu" in report_str
    assert "District Bifurcation Advisory (ADR 010)" in report_str
    assert "POPULATION_TOT" in report_str
    assert "CREDIT_DEPOSIT_RATIO" in report_str
    assert "Periodic Labour Force Survey" in report_str
