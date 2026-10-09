"""Centralized configuration and environment settings for EconLens AI.

Provides cross-platform path resolution, environment variable overrides,
and directory management without requiring external credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Gracefully attempt to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class Settings:
    """Immutable application settings container."""

    # Application Metadata
    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "EconLens AI")
    )
    app_env: str = field(
        default_factory=lambda: os.getenv("APP_ENV", "development").lower()
    )
    app_debug: bool = field(
        default_factory=lambda: os.getenv("APP_DEBUG", "true").lower()
        in ("true", "1", "yes")
    )

    # Logging
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )
    log_to_file: bool = field(
        default_factory=lambda: os.getenv("LOG_TO_FILE", "true").lower()
        in ("true", "1", "yes")
    )

    # Directory Paths
    base_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )
    data_dir_name: str = field(
        default_factory=lambda: os.getenv("DATA_DIR", "data")
    )
    model_dir_name: str = field(
        default_factory=lambda: os.getenv("MODEL_DIR", "models")
    )
    log_dir_name: str = field(
        default_factory=lambda: os.getenv("LOG_DIR", "logs")
    )

    @property
    def data_dir(self) -> Path:
        """Root data directory."""
        return self.base_dir / self.data_dir_name

    @property
    def raw_data_dir(self) -> Path:
        """Directory for raw, unverified datasets."""
        return self.data_dir / "raw"

    @property
    def processed_data_dir(self) -> Path:
        """Directory for cleaned, validated, normalized datasets."""
        return self.data_dir / "processed"

    @property
    def sample_data_dir(self) -> Path:
        """Directory for isolated synthetic demonstration datasets."""
        return self.data_dir / "sample"

    @property
    def model_dir(self) -> Path:
        """Directory for serialized models and scalers."""
        return self.base_dir / self.model_dir_name

    @property
    def log_dir(self) -> Path:
        """Directory for application log files."""
        return self.base_dir / self.log_dir_name

    @property
    def is_production(self) -> bool:
        """Returns True if the application environment is set to production."""
        return self.app_env in ("production", "prod")

    @property
    def is_development(self) -> bool:
        """Returns True if running in development mode."""
        return self.app_env in ("development", "dev")

    def ensure_directories(self) -> None:
        """Creates required directory paths if they do not already exist."""
        for directory in (
            self.raw_data_dir,
            self.processed_data_dir,
            self.sample_data_dir,
            self.model_dir,
            self.log_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


_SETTINGS_INSTANCE: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """Returns the singleton Settings instance.

    Args:
        reload: If True, recreates the Settings instance from the current environment.

    Returns:
        Settings: The active application settings instance.
    """
    global _SETTINGS_INSTANCE
    if _SETTINGS_INSTANCE is None or reload:
        _SETTINGS_INSTANCE = Settings()
    return _SETTINGS_INSTANCE
