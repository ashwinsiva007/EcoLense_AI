"""Verifies that all core packages and modules can be imported without side-effects."""

import importlib
import pytest


MODULES_TO_TEST = [
    "config",
    "config.settings",
    "src",
    "src.utils",
    "src.utils.logging_config",
    "src.data",
    "src.data.data_loader",
    "src.data.preprocessing",
    "src.data.validation",
    "src.analytics",
    "src.analytics.exploratory_analysis",
    "src.analytics.opportunity_scoring",
    "src.intelligence",
    "src.intelligence.bottleneck_detection",
    "src.intelligence.forecasting",
    "src.intelligence.scenario_analysis",
    "src.dashboard",
    "src.dashboard.layout",
    "src.dashboard.components",
]


@pytest.mark.parametrize("module_name", MODULES_TO_TEST)
def test_module_import_cleanly(module_name: str) -> None:
    """Each core module should import without raising any exceptions."""
    module = importlib.import_module(module_name)
    assert module is not None


def test_core_classes_exported() -> None:
    """Verifies that key classes and functions are properly exported."""
    from config import Settings, get_settings
    from src.data import DataLoader, DataValidator, PreprocessingPipeline
    from src.analytics import ExploratoryAnalyzer, OpportunityScorer
    from src.intelligence import BottleneckDetector, RegionalForecaster, ScenarioSimulator
    from src.utils import get_logger, setup_logging

    assert Settings is not None
    assert callable(get_settings)
    assert DataLoader is not None
    assert DataValidator is not None
    assert PreprocessingPipeline is not None
    assert ExploratoryAnalyzer is not None
    assert OpportunityScorer is not None
    assert BottleneckDetector is not None
    assert RegionalForecaster is not None
    assert ScenarioSimulator is not None
    assert callable(get_logger)
    assert callable(setup_logging)
