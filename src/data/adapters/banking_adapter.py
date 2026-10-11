"""Adapter for Reserve Bank of India & SLBC Tamil Nadu Banking Dataset.

Transforms district-level commercial bank credit, deposits, and Credit-Deposit (C-D)
ratios into canonical long-form regional observations for reference period '2020-21'.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.data.adapters.base_adapter import AdapterResult, BaseSourceAdapter
from src.utils.logging_config import get_logger

logger = get_logger("data.adapters.banking")


class BankingTNAdapter(BaseSourceAdapter):
    """Adapter for RBI / SLBC Tamil Nadu district banking credit & deposit dataset."""

    SOURCE_ID = "SRC_RBI_BANKING_TN_2021"
    REFERENCE_PERIOD = "2020-21"
    STATE_CODE = "33"
    PARENT_REGION_ID = "33"

    INDICATOR_MAP = {
        "credit_deposit_ratio": {
            "indicator_code": "CREDIT_DEPOSIT_RATIO",
            "indicator_name": "Credit-Deposit Ratio of Commercial Banks",
            "unit": "percentage",
        },
        "bank_credit_crores": {
            "indicator_code": "BANK_CREDIT_AMT",
            "indicator_name": "Total Outstanding Bank Credit",
            "unit": "crore_inr",
        },
        "bank_deposits_crores": {
            "indicator_code": "BANK_DEPOSIT_AMT",
            "indicator_name": "Total Aggregate Bank Deposits",
            "unit": "crore_inr",
        },
    }

    def __init__(self, source_id: str = SOURCE_ID) -> None:
        super().__init__(source_id=source_id)

    def parse(self, raw_path: Path) -> AdapterResult:
        """Parses raw RBI/SLBC Tamil Nadu CSV file into canonical observations."""
        raw_path = Path(raw_path)
        if not raw_path.exists():
            raise FileNotFoundError(f"Raw Banking file not found at: {raw_path}")

        df_raw = pd.read_csv(raw_path)
        raw_rows = len(df_raw)
        logger.info("Parsing Banking TN file with %d raw records: %s", raw_rows, raw_path.name)

        observations: List[Dict[str, Any]] = []
        rejected: List[Dict[str, Any]] = []

        for idx, row in df_raw.iterrows():
            dist_code = row.get("district_code")
            dist_name = row.get("district_name")

            if pd.isna(dist_code) or str(dist_code).strip() == "":
                rejected.append({
                    "row_index": idx,
                    "reason": "Missing or empty district_code",
                    "raw_data": row.to_dict(),
                })
                continue

            if pd.isna(dist_name) or str(dist_name).strip() == "":
                rejected.append({
                    "row_index": idx,
                    "reason": "Missing or empty district_name",
                    "raw_data": row.to_dict(),
                })
                continue

            region_id = self.format_district_id(self.STATE_CODE, dist_code)
            region_name = str(dist_name).strip()

            for col_name, ind_meta in self.INDICATOR_MAP.items():
                if col_name not in df_raw.columns:
                    continue

                raw_val = row.get(col_name)
                num_val = None
                if pd.notna(raw_val):
                    try:
                        num_val = float(str(raw_val).replace(",", "").strip())
                    except (ValueError, TypeError):
                        num_val = None

                observations.append({
                    "region_id": region_id,
                    "region_name": region_name,
                    "parent_region_id": self.PARENT_REGION_ID,
                    "geographic_level": "district",
                    "indicator_code": ind_meta["indicator_code"],
                    "indicator_name": ind_meta["indicator_name"],
                    "value": num_val,
                    "unit": ind_meta["unit"],
                    "reference_period": self.REFERENCE_PERIOD,
                    "source_id": self.source_id,
                    "source_record_id": f"REC_{idx:03d}",
                    "collection_date": "2026-10-11",
                    "quality_status": "validated",
                    "notes": f"RBI BSR / SLBC Tamil Nadu (Lead Bank Scheme {self.REFERENCE_PERIOD})",
                })

        obs_df = pd.DataFrame(observations)
        if not obs_df.empty:
            obs_df = self.ensure_canonical_structure(obs_df)
        else:
            obs_df = pd.DataFrame(columns=self.ensure_canonical_structure(pd.DataFrame()).columns)

        return AdapterResult(
            source_id=self.source_id,
            observations=obs_df,
            raw_row_count=raw_rows,
            parsed_observation_count=len(obs_df),
            rejected_records=rejected,
            diagnostics={
                "state_code": self.STATE_CODE,
                "reference_period": self.REFERENCE_PERIOD,
                "indicators_extracted": list(self.INDICATOR_MAP.keys()),
            },
        )
