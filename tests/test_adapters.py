"""Tests for source-specific dataset adapters in EconLens AI."""

from pathlib import Path
import pandas as pd
import pytest

from src.data.adapters.base_adapter import BaseSourceAdapter, AdapterResult
from src.data.adapters.census_adapter import CensusTNAdapter
from src.data.adapters.udyam_adapter import UdyamTNAdapter
from src.data.adapters.banking_adapter import BankingTNAdapter
from src.data.adapters.infrastructure_adapter import InfrastructureTNAdapter
from src.data.schema import CANONICAL_COLUMNS, REQUIRED_COLUMNS


@pytest.fixture
def sample_dir() -> Path:
    """Returns path to data/sample directory."""
    return Path(__file__).resolve().parent.parent / "data" / "sample"


def test_district_id_formatting() -> None:
    """BaseSourceAdapter should format district IDs with 2-digit state prefix."""
    assert BaseSourceAdapter.format_district_id("33", "602") == "33_602"
    assert BaseSourceAdapter.format_district_id(33, 603) == "33_603"
    assert BaseSourceAdapter.format_district_id("3", "42") == "03_42"


def test_census_adapter_parses_sample_fixture(sample_dir: Path) -> None:
    """CensusTNAdapter should parse Census raw fixture into canonical observations."""
    fixture_path = sample_dir / "sample_census_tn_raw.csv"
    adapter = CensusTNAdapter()
    result = adapter.parse(fixture_path)

    assert isinstance(result, AdapterResult)
    assert result.source_id == "SRC_CENSUS_2011_TN"
    assert result.raw_row_count == 3
    # 3 districts * 5 indicators = 15 observations
    assert result.parsed_observation_count == 15
    assert not result.has_rejections

    df_obs = result.observations
    assert list(df_obs.columns) == CANONICAL_COLUMNS
    for req_col in REQUIRED_COLUMNS:
        assert req_col in df_obs.columns
        assert df_obs[req_col].notna().all()

    # Check indicator codes
    expected_indicators = {"POPULATION_TOT", "LIT_RATE_TOT", "LIT_RATE_FEM", "WPR_TOT", "WPR_FEM"}
    assert set(df_obs["indicator_code"].unique()) == expected_indicators
    assert (df_obs["reference_period"] == "2011").all()
    assert (df_obs["geographic_level"] == "district").all()
    assert "33_602" in df_obs["region_id"].values


def test_udyam_adapter_parses_sample_fixture(sample_dir: Path) -> None:
    """UdyamTNAdapter should parse MSME raw fixture into canonical observations."""
    fixture_path = sample_dir / "sample_udyam_tn_raw.csv"
    adapter = UdyamTNAdapter()
    result = adapter.parse(fixture_path)

    assert result.source_id == "SRC_UDYAM_MSME_TN_2023"
    assert result.raw_row_count == 3
    # 3 districts * 4 indicators = 12 observations
    assert result.parsed_observation_count == 12
    assert not result.has_rejections

    df_obs = result.observations
    expected_indicators = {"MSME_MICRO_COUNT", "MSME_SMALL_COUNT", "MSME_MEDIUM_COUNT", "MSME_TOTAL_COUNT"}
    assert set(df_obs["indicator_code"].unique()) == expected_indicators
    assert (df_obs["reference_period"] == "2022-23").all()


def test_banking_adapter_parses_sample_fixture(sample_dir: Path) -> None:
    """BankingTNAdapter should parse banking raw fixture into canonical observations."""
    fixture_path = sample_dir / "sample_banking_tn_raw.csv"
    adapter = BankingTNAdapter()
    result = adapter.parse(fixture_path)

    assert result.source_id == "SRC_RBI_BANKING_TN_2021"
    assert result.raw_row_count == 3
    # 3 districts * 3 indicators = 9 observations
    assert result.parsed_observation_count == 9

    df_obs = result.observations
    expected_indicators = {"CREDIT_DEPOSIT_RATIO", "BANK_CREDIT_AMT", "BANK_DEPOSIT_AMT"}
    assert set(df_obs["indicator_code"].unique()) == expected_indicators
    assert (df_obs["reference_period"] == "2020-21").all()


def test_infrastructure_adapter_parses_sample_fixture(sample_dir: Path) -> None:
    """InfrastructureTNAdapter should parse road raw fixture into canonical observations."""
    fixture_path = sample_dir / "sample_infra_tn_raw.csv"
    adapter = InfrastructureTNAdapter()
    result = adapter.parse(fixture_path)

    assert result.source_id == "SRC_TN_DOES_INFRA_2021"
    assert result.raw_row_count == 3
    # 3 districts * 2 indicators = 6 observations
    assert result.parsed_observation_count == 6

    df_obs = result.observations
    expected_indicators = {"ROAD_SURFACED_KM", "ROAD_DENSITY"}
    assert set(df_obs["indicator_code"].unique()) == expected_indicators
    assert (df_obs["reference_period"] == "2020-21").all()


def test_adapter_records_rejected_rows_on_missing_id(tmp_path: Path) -> None:
    """Adapters must record rejected records when district_code or district_name is missing."""
    malformed_csv = tmp_path / "malformed_census.csv"
    malformed_csv.write_text(
        "district_code,district_name,total_population,literacy_rate\n"
        "602,Thiruvallur,3728104,84.03\n"
        ",MissingCodeDistrict,100000,75.0\n"
        "604,,200000,80.0\n",
        encoding="utf-8",
    )

    adapter = CensusTNAdapter()
    result = adapter.parse(malformed_csv)

    assert result.raw_row_count == 3
    assert len(result.rejected_records) == 2
    assert result.has_rejections
    assert result.rejected_records[0]["row_index"] == 1
    assert "district_code" in result.rejected_records[0]["reason"]
    assert result.rejected_records[1]["row_index"] == 2
    assert "district_name" in result.rejected_records[1]["reason"]


def test_adapter_raises_on_missing_file() -> None:
    """Adapter should raise FileNotFoundError when file does not exist."""
    adapter = CensusTNAdapter()
    with pytest.raises(FileNotFoundError):
        adapter.parse(Path("non_existent_census_file.csv"))
