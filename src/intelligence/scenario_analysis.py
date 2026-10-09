"""Interactive what-if scenario simulation module for EconLens AI.

Models the potential comparative impact of hypothetical policy interventions,
capital investments, or infrastructure shocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.utils.logging_config import get_logger

logger = get_logger("intelligence.scenario_analysis")


@dataclass
class ScenarioIntervention:
    """Defines a hypothetical modification to an indicator."""

    indicator_name: str
    percentage_change: float = 0.0
    absolute_change: Optional[float] = None
    affected_regions: List[str] = field(default_factory=list)


@dataclass
class ScenarioOutcome:
    """Simulated result of an intervention on opportunity and bottleneck profiles."""

    scenario_name: str
    interventions: List[ScenarioIntervention]
    simulated_impacts_by_region: Dict[str, Dict[str, float]]
    simulation_notes: str = ""
    is_hypothetical: bool = True
    disclaimer: str = (
        "Scenario simulation outputs represent hypothetical mathematical responses "
        "under model assumptions and do not constitute guaranteed causal outcomes."
    )


class ScenarioSimulator:
    """Evaluates the mathematical sensitivity of regional scores to simulated inputs."""

    def __init__(self, simulation_name: str = "Baseline Scenario") -> None:
        self.simulation_name = simulation_name

    def simulate(
        self, baseline_data: Any, interventions: List[ScenarioIntervention]
    ) -> ScenarioOutcome:
        """Simulates hypothetical outcomes given baseline data and interventions.

        NOTE: Concrete scenario propagation and sensitivity analysis are scheduled
        for future intelligence milestones.
        """
        logger.info(
            "Executing scenario simulation '%s' with %d interventions",
            self.simulation_name,
            len(interventions),
        )
        raise NotImplementedError(
            "Scenario simulation engine is scheduled for future stages."
        )
