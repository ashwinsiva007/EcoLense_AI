"""Tests for application helper functions, logging, validation models, and UI mapping."""

from pathlib import Path
import logging
from config.settings import Settings
from src.dashboard.components import render_status_badge
from src.dashboard.layout import PAGES
from src.data.data_loader import DataLoader
from src.data.validation import ValidationResult
from src.utils.logging_config import setup_logging, get_logger


def test_pages_definition() -> None:
    """Verifies that navigation pages contain all required modules."""
    expected_pages = [
        "Overview",
        "Opportunity Explorer",
        "Bottleneck Analysis",
        "Forecasting",
        "Scenario Simulator",
        "Data and Sources",
    ]
    for page in expected_pages:
        assert page in PAGES
        assert "icon" in PAGES[page]
        assert "description" in PAGES[page]
        assert "stage" in PAGES[page]


def test_status_badge_html() -> None:
    """Verifies that render_status_badge produces valid HTML markup."""
    badge = render_status_badge("Active", "active")
    assert "status-badge" in badge
    assert "badge-active" in badge
    assert "Active" in badge


def test_validation_result_summary() -> None:
    """Verifies ValidationResult formatting."""
    valid_res = ValidationResult(is_valid=True, row_count=100, column_count=15)
    assert "PASSED" in valid_res.summary()
    assert "100 rows" in valid_res.summary()

    invalid_res = ValidationResult(
        is_valid=False,
        row_count=50,
        column_count=5,
        errors=["Missing column 'region_id'"],
    )
    assert "FAILED" in invalid_res.summary()
    assert "Errors: 1" in invalid_res.summary()


def test_data_loader_initial_state(tmp_path: Path) -> None:
    """Verifies that DataLoader accurately reflects empty dataset directories."""
    empty_settings = Settings(base_dir=tmp_path)
    empty_settings.ensure_directories()
    loader = DataLoader(empty_settings)

    assert loader.list_available_raw_datasets() == []
    assert loader.list_available_processed_datasets() == []
    assert loader.list_available_sample_datasets() == []
    assert loader.has_verified_datasets() is False


def test_logging_setup_idempotency(tmp_path: Path) -> None:
    """Verifies setup_logging configures logger and does not duplicate handlers."""
    logger1 = setup_logging(log_level="DEBUG", log_to_file=False, log_dir=tmp_path)
    handler_count_1 = len(logger1.handlers)

    logger2 = setup_logging(log_level="INFO", log_to_file=False, log_dir=tmp_path)
    handler_count_2 = len(logger2.handlers)

    assert logger1 is logger2
    assert handler_count_1 == handler_count_2

    child_logger = get_logger("test_module")
    assert child_logger.name == "econlens_ai.test_module"
