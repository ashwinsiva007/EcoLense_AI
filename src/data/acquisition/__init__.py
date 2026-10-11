"""Network-safe data acquisition utilities for EconLens AI.

Enforces strict SSL certificate verification, explicit timeouts, and provenance
auditing. Never fabricates data or disables SSL on network failure.
"""

from src.data.acquisition.fetcher import DataFetcher, FetchResult

__all__ = ["DataFetcher", "FetchResult"]
