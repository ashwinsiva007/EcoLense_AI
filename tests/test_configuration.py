"""Tests for configuration management, path resolution, and environment overrides."""

from pathlib import Path
import pytest
from config.settings import Settings, get_settings


def test_default_settings_values() -> None:
    """Verifies default values of Settings."""
    settings = Settings()
    assert settings.app_name == "EconLens AI"
    assert settings.app_env in ("development", "dev")
    assert settings.log_level == "INFO"
    assert settings.is_development is True
    assert settings.is_production is False
    assert isinstance(settings.base_dir, Path)
    assert settings.data_dir == settings.base_dir / "data"
    assert settings.raw_data_dir == settings.base_dir / "data" / "raw"
    assert settings.processed_data_dir == settings.base_dir / "data" / "processed"
    assert settings.sample_data_dir == settings.base_dir / "data" / "sample"
    assert settings.model_dir == settings.base_dir / "models"
    assert settings.log_dir == settings.base_dir / "logs"


def test_settings_singleton_and_reload() -> None:
    """Verifies get_settings returns singleton and supports reloading."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

    s3 = get_settings(reload=True)
    assert isinstance(s3, Settings)


def test_environment_variable_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that environment variables correctly override configuration."""
    monkeypatch.setenv("APP_NAME", "CustomEconLens")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_DIR", "custom_data")

    custom_settings = Settings()
    assert custom_settings.app_name == "CustomEconLens"
    assert custom_settings.app_env == "production"
    assert custom_settings.is_production is True
    assert custom_settings.log_level == "DEBUG"
    assert custom_settings.data_dir_name == "custom_data"


def test_ensure_directories(tmp_path: Path) -> None:
    """Verifies that ensure_directories creates all required folders."""
    test_settings = Settings(
        base_dir=tmp_path,
        data_dir_name="data",
        model_dir_name="models",
        log_dir_name="logs",
    )
    test_settings.ensure_directories()

    assert (tmp_path / "data" / "raw").exists()
    assert (tmp_path / "data" / "processed").exists()
    assert (tmp_path / "data" / "sample").exists()
    assert (tmp_path / "models").exists()
    assert (tmp_path / "logs").exists()
