"""Regional economic indicator forecasting module for EconLens AI.

Provides longitudinal time-series forecasting where historical data is available,
accompanied by uncertainty intervals and assumption disclosures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.utils.logging_config import get_logger

logger = get_logger("intelligence.forecasting")


@dataclass
class ForecastResult:
    """Output of a regional time-series forecast run."""

    region_id: str
    indicator_name: str
    historical_periods: List[str]
    forecast_periods: List[str]
    predicted_values: List[float]
    lower_bound_95: List[float] = field(default_factory=list)
    upper_bound_95: List[float] = field(default_factory=list)
    model_name: str = "Unspecified"
    model_assumptions: List[str] = field(default_factory=list)
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    disclaimer: str = (
        "Forecasts are mathematical extrapolations conditioned on historical trends "
        "and stated assumptions. They do not guarantee future economic outcomes."
    )


class RegionalForecaster:
    """Generates longitudinal forecasts with explicit uncertainty boundaries."""

    def __init__(self, horizon_periods: int = 5) -> None:
        self.horizon_periods = horizon_periods

    def fit_and_predict(
        self, historical_data: Any, indicator_name: str
    ) -> ForecastResult:
        """Trains a time-series model on historical data and projects future values.

        NOTE: Concrete statistical and ML forecasting algorithms (ARIMA/ETS/GBM)
        are scheduled for future intelligence milestones when longitudinal datasets exist.
        """
        logger.info(
            "Request to forecast indicator '%s' over %d periods",
            indicator_name,
            self.horizon_periods,
        )
        raise NotImplementedError(
            "Forecasting logic is scheduled for future stages requiring longitudinal panel data."
        )
