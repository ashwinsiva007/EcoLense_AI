"""Source-specific dataset adapters for EconLens AI.

Translates diverse publisher formats (Census PCA, Udyam MSME, RBI SLBC, TN DoES)
into canonical long-form regional observations while recording unparseable rows.
"""

from src.data.adapters.base_adapter import AdapterResult, BaseSourceAdapter
from src.data.adapters.banking_adapter import BankingTNAdapter
from src.data.adapters.census_adapter import CensusTNAdapter
from src.data.adapters.infrastructure_adapter import InfrastructureTNAdapter
from src.data.adapters.udyam_adapter import UdyamTNAdapter

__all__ = [
    "BaseSourceAdapter",
    "AdapterResult",
    "CensusTNAdapter",
    "UdyamTNAdapter",
    "BankingTNAdapter",
    "InfrastructureTNAdapter",
]
