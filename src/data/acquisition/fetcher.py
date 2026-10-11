"""Safe, audited HTTP data fetcher for EconLens AI.

Enforces strict SSL certificate verification (ADR 003, Stage 2B guidelines),
configurable timeouts, meaningful error classification, and immutable saving
to data/raw/ without silently manufacturing data.
"""

from __future__ import annotations

import hashlib
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.logging_config import get_logger

logger = get_logger("data.acquisition.fetcher")


@dataclass
class FetchResult:
    """Outcome of an external file retrieval attempt."""

    source_url: str
    destination_path: Optional[Path]
    success: bool
    status_code: Optional[int]
    error_message: Optional[str]
    retrieval_timestamp: str
    bytes_downloaded: int = 0
    sha256_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts result to a dictionary for JSON reporting."""
        return {
            "source_url": self.source_url,
            "destination_path": str(self.destination_path) if self.destination_path else None,
            "success": self.success,
            "status_code": self.status_code,
            "error_message": self.error_message,
            "retrieval_timestamp": self.retrieval_timestamp,
            "bytes_downloaded": self.bytes_downloaded,
            "sha256_hash": self.sha256_hash,
        }


class DataFetcher:
    """Acquires remote datasets with strict security and provenance guarantees."""

    DEFAULT_TIMEOUT_SECONDS: float = 15.0
    USER_AGENT: str = "EconLensAI/2.0 (Research Platform; Academic Data Ingestion; +https://ecolenseai.vercel.app)"

    def __init__(self, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        """Initializes the fetcher with a mandatory network timeout.

        Args:
            timeout: Timeout in seconds for remote connections.
        """
        self.timeout = timeout

    def fetch_to_file(
        self,
        url: str,
        destination_path: Path,
        overwrite: bool = False,
    ) -> FetchResult:
        """Downloads a remote resource directly into an immutable raw file path.

        STRICT SAFETY GUARANTEES:
        1. Always enforces default SSL context with strict CA verification.
        2. Never disables certificate checking or accepts self-signed/forged certs.
        3. Never silently falls back to synthetic or fabricated data on failure.

        Args:
            url: Remote HTTP/HTTPS URL.
            destination_path: Target path under data/raw/.
            overwrite: If False and destination already exists, skips network download.

        Returns:
            FetchResult documenting retrieval outcome and SHA-256 provenance hash.
        """
        destination_path = Path(destination_path)
        timestamp = datetime.now(timezone.utc).isoformat()

        if destination_path.exists() and not overwrite:
            logger.info("Destination file already exists, skipping network fetch: %s", destination_path)
            content = destination_path.read_bytes()
            hasher = hashlib.sha256(content)
            return FetchResult(
                source_url=url,
                destination_path=destination_path,
                success=True,
                status_code=200,
                error_message=None,
                retrieval_timestamp=timestamp,
                bytes_downloaded=len(content),
                sha256_hash=hasher.hexdigest(),
            )

        destination_path.parent.mkdir(parents=True, exist_ok=True)

        req = urllib.request.Request(
            url,
            headers={"User-Agent": self.USER_AGENT},
        )

        # Enforce standard verified SSL context
        context = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=context) as response:
                status_code = response.getcode()
                content = response.read()

                destination_path.write_bytes(content)
                hasher = hashlib.sha256(content)

                logger.info(
                    "Successfully acquired %d bytes from %s to %s",
                    len(content),
                    url,
                    destination_path.name,
                )
                return FetchResult(
                    source_url=url,
                    destination_path=destination_path,
                    success=True,
                    status_code=status_code,
                    error_message=None,
                    retrieval_timestamp=timestamp,
                    bytes_downloaded=len(content),
                    sha256_hash=hasher.hexdigest(),
                )

        except urllib.error.HTTPError as exc:
            logger.error("HTTP error during acquisition of %s: %s (Status: %d)", url, exc.reason, exc.code)
            return FetchResult(
                source_url=url,
                destination_path=None,
                success=False,
                status_code=exc.code,
                error_message=f"HTTP {exc.code}: {exc.reason}",
                retrieval_timestamp=timestamp,
            )

        except urllib.error.URLError as exc:
            logger.error("Network connection error for %s: %s", url, exc.reason)
            return FetchResult(
                source_url=url,
                destination_path=None,
                success=False,
                status_code=None,
                error_message=f"Connection failure: {exc.reason}",
                retrieval_timestamp=timestamp,
            )

        except Exception as exc:
            logger.error("Unexpected error during acquisition for %s: %s", url, exc)
            return FetchResult(
                source_url=url,
                destination_path=None,
                success=False,
                status_code=None,
                error_message=f"Unexpected error: {str(exc)}",
                retrieval_timestamp=timestamp,
            )
