"""Tests for data loading module, file validation, format routing, and error handling."""

from pathlib import Path
import pandas as pd
import pytest

from config.settings import Settings
from src.data.data_loader import (
    DataLoader,
    DataLoaderError,
    DatasetMetadata,
    DatasetNotFoundError,
    EmptyDatasetError,
    MalformedDataError,
    UnsupportedFormatError,
    load_csv,
    load_json,
)


def test_load_valid_sample_csv() -> None:
    """Verifies that the synthetic sample CSV loads cleanly into a DataFrame."""
    sample_path = Path("data/sample/synthetic_district_observations.csv")
    assert sample_path.exists()

    df = load_csv(sample_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6
    assert "region_id" in df.columns
    assert "indicator_code" in df.columns
    assert "value" in df.columns


def test_load_nonexistent_file(tmp_path: Path) -> None:
    """Verifies that loading a non-existent file raises DatasetNotFoundError."""
    missing_file = tmp_path / "does_not_exist.csv"
    with pytest.raises(DatasetNotFoundError) as exc_info:
        load_csv(missing_file)
    assert "File not found" in str(exc_info.value)


def test_load_unsupported_extension(tmp_path: Path) -> None:
    """Verifies that unsupported file extensions raise UnsupportedFormatError."""
    text_file = tmp_path / "data.txt"
    text_file.write_text("region_id,value\nD01,10", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError) as exc_info:
        load_csv(text_file)
    assert "Expected a .csv file" in str(exc_info.value)


def test_load_empty_file(tmp_path: Path) -> None:
    """Verifies that a 0-byte file raises EmptyDatasetError."""
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()

    with pytest.raises(EmptyDatasetError) as exc_info:
        load_csv(empty_file)
    assert "empty" in str(exc_info.value).lower()


def test_load_header_only_file(tmp_path: Path) -> None:
    """Verifies that a CSV with headers but no observations raises EmptyDatasetError."""
    header_only = tmp_path / "header_only.csv"
    header_only.write_text("region_id,region_name,value\n", encoding="utf-8")

    with pytest.raises(EmptyDatasetError) as exc_info:
        load_csv(header_only)
    assert "zero data rows" in str(exc_info.value).lower()


def test_load_malformed_csv(tmp_path: Path) -> None:
    """Verifies that severely malformed CSV contents raise MalformedDataError."""
    # 1. Jagged irregular columns trigger ParserError
    jagged_csv = tmp_path / "jagged.csv"
    jagged_csv.write_text("col1,col2\n1,2\n3,4,5,6\n", encoding="utf-8")

    with pytest.raises(MalformedDataError):
        load_csv(jagged_csv, encoding="utf-8")

    # 2. Corrupted byte sequences trigger UnicodeDecodeError
    corrupt_bytes = tmp_path / "corrupt_bytes.csv"
    corrupt_bytes.write_bytes(b"\xff\xfe\x00\x80\x81")

    with pytest.raises(MalformedDataError):
        load_csv(corrupt_bytes, encoding="utf-8")


def test_load_json_valid_and_errors(tmp_path: Path) -> None:
    """Verifies loading JSON records and error conditions."""
    valid_json = tmp_path / "valid.json"
    valid_json.write_text('[{"region_id": "D01", "value": 100}]', encoding="utf-8")

    df = load_json(valid_json)
    assert len(df) == 1
    assert df.iloc[0]["region_id"] == "D01"

    empty_json = tmp_path / "empty.json"
    empty_json.write_text("", encoding="utf-8")
    with pytest.raises(EmptyDatasetError):
        load_json(empty_json)

    corrupt_json = tmp_path / "corrupt.json"
    corrupt_json.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(MalformedDataError):
        load_json(corrupt_json)


def test_data_loader_manager_load_dataset(tmp_path: Path) -> None:
    """Verifies DataLoader class load_dataset with DatasetMetadata."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("region_id,value\nD01,42.5\n", encoding="utf-8")

    meta = DatasetMetadata(
        name="test_data",
        path=csv_file,
        file_format="csv",
        is_synthetic=True,
    )

    settings = Settings(base_dir=tmp_path)
    loader = DataLoader(settings)
    df = loader.load_dataset(meta)
    assert len(df) == 1
    assert df.iloc[0]["value"] == 42.5


def test_preserves_raw_file_integrity(tmp_path: Path) -> None:
    """Ensures that loading a raw file does not modify its content or timestamp."""
    raw_file = tmp_path / "immutable.csv"
    original_content = "region_id,region_name,value\nD01,District Alpha,99.9\n"
    raw_file.write_text(original_content, encoding="utf-8")

    mtime_before = raw_file.stat().st_mtime_ns
    df = load_csv(raw_file)
    assert len(df) == 1

    mtime_after = raw_file.stat().st_mtime_ns
    assert mtime_before == mtime_after
    assert raw_file.read_text(encoding="utf-8") == original_content
