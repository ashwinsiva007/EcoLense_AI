"""Tests for DataPipeline execution in EconLens AI."""

from pathlib import Path
import pytest

from src.data.pipeline import DataPipeline
from src.data.schema import PRIMARY_KEY_COLUMNS


def test_pipeline_status_check() -> None:
    """Pipeline check_status should report registered sources and file counts."""
    pipeline = DataPipeline()
    status = pipeline.check_status()

    assert "total_sources" in status
    assert status["total_sources"] >= 5
    assert status["raw_file_count"] >= 4


def test_pipeline_validate_raw() -> None:
    """Pipeline validate_raw should succeed when required raw CSVs are present."""
    pipeline = DataPipeline()
    is_valid, errors = pipeline.validate_raw()

    assert is_valid is True
    assert len(errors) == 0


def test_pipeline_standardize_datasets() -> None:
    """Pipeline standardize_datasets should generate valid canonical observations."""
    pipeline = DataPipeline()
    merged_df, val_res = pipeline.standardize_datasets()

    assert val_res.is_valid is True
    assert len(val_res.errors) == 0
    assert val_res.duplicate_count == 0
    # 4 datasets: 160 + 128 + 96 + 64 = 448 observations
    assert len(merged_df) >= 448
    assert merged_df["value"].notna().all()

    # Check primary key uniqueness
    assert not merged_df.duplicated(subset=PRIMARY_KEY_COLUMNS).any()


def test_pipeline_generate_reports(tmp_path: Path) -> None:
    """Pipeline generate_reports should produce inventory JSON and coverage report."""
    pipeline = DataPipeline()
    json_path, md_path = pipeline.generate_reports()

    assert json_path.exists()
    assert md_path.exists()
