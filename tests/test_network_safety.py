"""Tests for network-safety, timeouts, and anti-fabrication fetcher guarantees."""

from pathlib import Path
import pytest

from src.data.acquisition.fetcher import DataFetcher, FetchResult


def test_fetcher_skips_existing_file_when_not_overwrite(tmp_path: Path) -> None:
    """Fetcher should skip network call when destination file already exists."""
    existing_file = tmp_path / "existing_dataset.csv"
    existing_file.write_text("col_a,col_b\n1,2\n", encoding="utf-8")

    fetcher = DataFetcher(timeout=5.0)
    # Using an intentionally unresolvable URL to prove no network call is made
    result = fetcher.fetch_to_file(
        url="https://non-existent-domain-that-does-not-resolve-12345.org/data.csv",
        destination_path=existing_file,
        overwrite=False,
    )

    assert isinstance(result, FetchResult)
    assert result.success is True
    assert result.status_code == 200
    assert result.bytes_downloaded > 0
    assert result.sha256_hash is not None
    assert existing_file.read_text(encoding="utf-8") == "col_a,col_b\n1,2\n"


def test_fetcher_handles_connection_failure_without_fabrication(tmp_path: Path) -> None:
    """Fetcher must record failure explicitly on network error without fabricating data."""
    dest_file = tmp_path / "network_test_non_existent.csv"
    fetcher = DataFetcher(timeout=2.0)

    result = fetcher.fetch_to_file(
        url="https://invalid-non-existent-domain-xyz987654.gov/file.csv",
        destination_path=dest_file,
        overwrite=True,
    )

    assert result.success is False
    assert result.status_code is None
    assert result.error_message is not None
    assert "Connection failure" in result.error_message or "Unexpected error" in result.error_message
    # Critical Anti-Fabrication Guarantee: Destination file must NOT be created with fake data!
    assert not dest_file.exists()


def test_fetcher_user_agent_configured() -> None:
    """Fetcher must identify as EconLens AI research platform in User-Agent header."""
    fetcher = DataFetcher()
    assert "EconLensAI" in fetcher.USER_AGENT
