"""Data inventory and coverage reporting engine for EconLens AI.

Generates machine-readable inventory (JSON) and comprehensive human-readable
coverage reports (Markdown) documenting provenance, geographic scope, indicator
catalog, validation status, and boundary limitations.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from config.settings import Settings, get_settings
from src.data.source_registry import SourceRegistry
from src.data.validation import DataValidator, ValidationResult
from src.utils.logging_config import get_logger

logger = get_logger("data.inventory")


@dataclass
class DatasetInventoryEntry:
    """Detailed metadata and audit state for an individual dataset."""

    dataset_id: str
    title: str
    publisher: str
    source_url: str
    local_filename: Optional[str]
    acquisition_status: str  # acquired, planned, unavailable
    validation_status: str   # validated, partially_validated, raw, planned, rejected
    license: str
    geographic_coverage: str
    geographic_level: str
    reference_period: str
    indicators_supplied: List[str]
    record_count: int
    missing_value_count: int
    duplicate_key_count: int
    last_retrieval_date: Optional[str]
    known_limitations: str
    requires_manual_download: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Converts entry to dictionary."""
        return asdict(self)


class DataInventoryManager:
    """Manages generation of machine-readable inventory and coverage reports."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.validator = DataValidator()

    def build_inventory(
        self,
        registry: SourceRegistry,
        observations_df: Optional[pd.DataFrame] = None,
    ) -> List[DatasetInventoryEntry]:
        """Builds dataset inventory entries by cross-referencing registry and physical files."""
        entries: List[DatasetInventoryEntry] = []

        # Indicators supplied map for known sources
        known_indicators = {
            "SRC_CENSUS_2011_TN": [
                "POPULATION_TOT",
                "LIT_RATE_TOT",
                "LIT_RATE_FEM",
                "WPR_TOT",
                "WPR_FEM",
            ],
            "SRC_UDYAM_MSME_TN_2023": [
                "MSME_MICRO_COUNT",
                "MSME_SMALL_COUNT",
                "MSME_MEDIUM_COUNT",
                "MSME_TOTAL_COUNT",
            ],
            "SRC_RBI_BANKING_TN_2021": [
                "CREDIT_DEPOSIT_RATIO",
                "BANK_CREDIT_AMT",
                "BANK_DEPOSIT_AMT",
            ],
            "SRC_TN_DOES_INFRA_2021": [
                "ROAD_SURFACED_KM",
                "ROAD_DENSITY",
            ],
            "SRC_PLANNED_PLFS_NSSO_2022": [
                "WPR_TOT",
                "FLFPR_TOT",
            ],
            "SRC_EXAMPLE_SYNTHETIC": [
                "LIT_RATE_TOT",
                "WPR_TOT",
                "ROAD_DENSITY",
                "MSME_DENSITY",
            ],
        }

        limitations_map = {
            "SRC_CENSUS_2011_TN": (
                "Decennial baseline from 2011. Pre-dates subsequent district bifurcations "
                "(6 new districts formed after 2011: Tenkasi, Chengalpattu, Tirupathur, "
                "Ranipet, Kallakurichi, Mayiladuthurai)."
            ),
            "SRC_UDYAM_MSME_TN_2023": (
                "Measures formalized registrations on the Udyam portal. Does not capture "
                "unregistered informal enterprises. Aggregated to the 32 parent district baseline."
            ),
            "SRC_RBI_BANKING_TN_2021": (
                "Includes Scheduled Commercial Banks only; cooperative and informal credit "
                "not covered. CD ratio in metro districts reflects corporate credit concentration."
            ),
            "SRC_TN_DOES_INFRA_2021": (
                "Road density calculated based on surfaced roads maintained by Highways and Rural Local Bodies. "
                "Forest roads and private corridors excluded."
            ),
            "SRC_PLANNED_PLFS_NSSO_2022": (
                "MoSPI PLFS published reports suppress district-level estimates due to survey sample size. "
                "District indicators require unit-level microdata extraction (DDI manual workflow)."
            ),
            "SRC_EXAMPLE_SYNTHETIC": (
                "SYNTHETIC TEST FIXTURE ONLY: Not real economic data; isolated for automated test suites."
            ),
        }

        for source in registry.list_sources():
            s_id = source.source_id
            local_file = source.file_path
            is_planned = source.verification_status == "planned"
            is_synthetic = "SYNTHETIC" in s_id

            # Determine physical file existence
            file_exists = False
            rec_count = 0
            missing_count = 0
            dupe_count = 0

            if local_file:
                target_path = self.settings.base_dir / local_file
                if target_path.exists():
                    file_exists = True
                    try:
                        df_temp = pd.read_csv(target_path)
                        rec_count = len(df_temp)
                        missing_count = int(df_temp.isna().sum().sum())
                    except Exception:
                        pass

            # If standardized observations DataFrame provided, check observations count
            if observations_df is not None and not observations_df.empty:
                src_obs = observations_df[observations_df["source_id"] == s_id]
                if not src_obs.empty:
                    rec_count = len(src_obs)
                    missing_count = int(src_obs["value"].isna().sum())
                    # Check duplicate primary keys
                    dupes = src_obs.duplicated(subset=["region_id", "indicator_code", "reference_period"])
                    dupe_count = int(dupes.sum())

            # Determine acquisition & validation statuses
            if is_planned:
                acq_status = "planned"
                val_status = "planned"
                requires_manual = True
            elif file_exists:
                acq_status = "acquired"
                val_status = "validated" if source.verification_status == "validated" else "partially_validated"
                requires_manual = False
            else:
                acq_status = "unavailable"
                val_status = "unavailable"
                requires_manual = False

            entry = DatasetInventoryEntry(
                dataset_id=s_id,
                title=source.dataset_name,
                publisher=source.publisher,
                source_url=source.source_url,
                local_filename=local_file,
                acquisition_status=acq_status,
                validation_status=val_status,
                license=source.license,
                geographic_coverage=source.geographic_coverage,
                geographic_level=source.geographic_level,
                reference_period=source.reference_period,
                indicators_supplied=known_indicators.get(s_id, []),
                record_count=rec_count,
                missing_value_count=missing_count,
                duplicate_key_count=dupe_count,
                last_retrieval_date=source.retrieval_date,
                known_limitations=limitations_map.get(s_id, source.notes or "None documented"),
                requires_manual_download=requires_manual,
            )
            entries.append(entry)

        return entries

    def export_inventory_json(
        self,
        entries: List[DatasetInventoryEntry],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Saves machine-readable inventory to JSON."""
        target = output_path or (self.settings.metadata_data_dir / "data_inventory.json")
        target.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_datasets": len(entries),
            "acquired_count": sum(1 for e in entries if e.acquisition_status == "acquired"),
            "validated_count": sum(1 for e in entries if e.validation_status == "validated"),
            "planned_count": sum(1 for e in entries if e.acquisition_status == "planned"),
            "datasets": [e.to_dict() for e in entries],
        }

        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved data inventory JSON to: %s", target)
        return target

    def generate_coverage_report_markdown(
        self,
        entries: List[DatasetInventoryEntry],
        observations_df: Optional[pd.DataFrame] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """Generates comprehensive human-readable Markdown data coverage report."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Distinct regions, indicators, periods
        dist_regions: List[str] = []
        dist_indicators: List[str] = []
        dist_periods: List[str] = []
        total_obs = 0

        if observations_df is not None and not observations_df.empty:
            total_obs = len(observations_df)
            dist_regions = sorted(observations_df["region_id"].dropna().unique().tolist())
            dist_indicators = sorted(observations_df["indicator_code"].dropna().unique().tolist())
            dist_periods = sorted(observations_df["reference_period"].dropna().unique().tolist())

        acquired_real = [
            e for e in entries
            if e.acquisition_status == "acquired" and "SYNTHETIC" not in e.dataset_id
        ]
        planned = [e for e in entries if e.acquisition_status == "planned"]

        md_lines = [
            "# EconLens AI — Dataset Inventory & Coverage Report",
            "",
            f"> **Generated:** `{now_str}`  ",
            "> **Milestone:** Stage 2B — Real Dataset Acquisition & Source Verification  ",
            "> **Pilot Geography:** Tamil Nadu (32 Baseline Districts)  ",
            "",
            "---",
            "",
            "## 1. Executive Summary",
            "",
            f"- **Total Registered Datasets:** `{len(entries)}`",
            f"- **Genuine Datasets Acquired:** `{len(acquired_real)}`",
            f"- **Genuine Datasets Validated:** `{sum(1 for e in acquired_real if e.validation_status == 'validated')}`",
            f"- **Datasets Requiring Manual Extraction:** `{len(planned)}`",
            f"- **Total Standardized Observations:** `{total_obs:,}`",
            f"- **Distinct Regional Entities:** `{len(dist_regions)}` districts",
            f"- **Unique Economic Indicators:** `{len(dist_indicators)}` indicators",
            f"- **Reference Periods Covered:** `{', '.join(dist_periods) if dist_periods else 'None'}`",
            "",
            "---",
            "",
            "## 2. Acquired & Verified Real Datasets",
            "",
            "| Dataset ID | Title & Publisher | Coverage | Period | Records | Status | Indicators |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for e in entries:
            if "SYNTHETIC" in e.dataset_id:
                continue
            indicators_str = ", ".join(f"`{i}`" for i in e.indicators_supplied)
            md_lines.append(
                f"| `{e.dataset_id}` | **{e.title}**<br>_{e.publisher}_ | "
                f"{e.geographic_coverage} ({e.geographic_level}) | `{e.reference_period}` | "
                f"`{e.record_count}` | **{e.validation_status.upper()}** | {indicators_str} |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## 3. Geographic & Administrative Integrity",
            "",
            "### 3.1 Pilot Study Geography: Tamil Nadu Districts",
            "- **Baseline District Count:** 32 districts (aligned with Census 2011 Primary Census Abstract, State Code `33`).",
            "- **District Identifier Schema:** Composite identifier `33_<census_code>` (e.g. `33_602` for Thiruvallur to `33_633` for Tiruppur).",
            "- **Parent Administrative Unit:** `33` (Tamil Nadu state).",
            "",
            "### 3.2 Boundary Harmonization & Comparability Disclosure",
            "> [!WARNING]",
            "> **District Bifurcation Advisory (ADR 010):**  ",
            "> Between 2018 and 2020, 6 new districts were carved out in Tamil Nadu:  ",
            "> 1. *Tenkasi* (from Tirunelveli)  ",
            "> 2. *Chengalpattu* (from Kancheepuram)  ",
            "> 3. *Tirupathur* and *Ranipet* (from Vellore)  ",
            "> 4. *Kallakurichi* (from Viluppuram)  ",
            "> 5. *Mayiladuthurai* (from Nagapattinam)  ",
            "> ",
            "> **Platform Enforcement:** To prevent temporal incomparability and false missingness, all datasets are harmonized to the verified 32-district baseline. Post-2018 portal statistics (e.g. Udyam MSME) for bifurcated units are aggregated back to parent boundaries. No unweighted cross-temporal joins are permitted without explicit boundary mapping.",
            "",
            "---",
            "",
            "## 4. Indicator Catalog & Temporal Coverage",
            "",
            "| Domain | Indicator Code | Indicator Name | Unit | Bounds | Reference Period | Source ID |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            "| Demographics | `POPULATION_TOT` | Total Resident Population | `count` | `[1.0, None)` | `2011` | `SRC_CENSUS_2011_TN` |",
            "| Demographics | `LIT_RATE_TOT` | Effective Literacy Rate (Total) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |",
            "| Demographics | `LIT_RATE_FEM` | Effective Literacy Rate (Female) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |",
            "| Labor Force | `WPR_TOT` | Worker Population Ratio (Total) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |",
            "| Labor Force | `WPR_FEM` | Worker Population Ratio (Female) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |",
            "| Enterprise | `MSME_MICRO_COUNT` | Registered Micro Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |",
            "| Enterprise | `MSME_SMALL_COUNT` | Registered Small Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |",
            "| Enterprise | `MSME_MEDIUM_COUNT` | Registered Medium Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |",
            "| Enterprise | `MSME_TOTAL_COUNT` | Total Registered MSME Units | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |",
            "| Financial | `CREDIT_DEPOSIT_RATIO` | Credit-Deposit Ratio (Commercial Banks) | `percentage` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |",
            "| Financial | `BANK_CREDIT_AMT` | Total Bank Credit | `crore_inr` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |",
            "| Financial | `BANK_DEPOSIT_AMT` | Total Bank Deposits | `crore_inr` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |",
            "| Infrastructure | `ROAD_SURFACED_KM` | Length of Surfaced Roadways | `km` | `[0.0, None)` | `2020-21` | `SRC_TN_DOES_INFRA_2021` |",
            "| Infrastructure | `ROAD_DENSITY` | Surfaced Road Density | `km_per_sq_km` | `[0.0, None)` | `2020-21` | `SRC_TN_DOES_INFRA_2021` |",
            "",
            "---",
            "",
            "## 5. Provenance & Official Source Citations",
            "",
            "1. **Census of India 2011 — Primary Census Abstract (PCA):**  ",
            "   - Publisher: Office of the Registrar General & Census Commissioner, India (ORGI), Ministry of Home Affairs  ",
            "   - Official Portal: [https://censusindia.gov.in](https://censusindia.gov.in)  ",
            "   - License: Open Government Data License - India (OGDL)  ",
            "",
            "2. **Ministry of MSME — Udyam Registration Portal:**  ",
            "   - Publisher: Ministry of Micro, Small and Medium Enterprises, Government of India  ",
            "   - Official Portal: [https://dashboard.msme.gov.in](https://dashboard.msme.gov.in)  ",
            "   - License: Open Government Data License - India (OGDL)  ",
            "",
            "3. **Reserve Bank of India & SLBC Tamil Nadu — Banking Statistics:**  ",
            "   - Publisher: Reserve Bank of India (DSIM) & State Level Bankers' Committee Tamil Nadu (Indian Overseas Bank)  ",
            "   - Official Portal: [https://data.rbi.org.in](https://data.rbi.org.in) / [https://www.slbctn.com](https://www.slbctn.com)  ",
            "   - License: RBI Public Data Dissemination  ",
            "",
            "4. **Department of Economics & Statistics (DoES), Tamil Nadu — Road Infrastructure:**  ",
            "   - Publisher: Department of Economics and Statistics, Government of Tamil Nadu  ",
            "   - Official Portal: [https://www.tn.gov.in/deptst](https://www.tn.gov.in/deptst)  ",
            "   - Reference: *Statistical Hand Book of Tamil Nadu*, Table 23.1 Length of Roads  ",
            "   - License: Government Open Statistical Publication  ",
            "",
            "---",
            "",
            "## 6. Known Incompatibilities & Planned Manual Datasets",
            "",
            "### 6.1 Periodic Labour Force Survey (PLFS) District Estimates Barrier",
            "- **Status:** `planned` (Candidate Source `SRC_PLANNED_PLFS_NSSO_2022`)",
            "- **Issue:** Annual PLFS reports published by MoSPI/NSSO do not report district-level work participation rates due to small sampling clusters at the district tier. Only State and NSS-Region aggregates are officially published.",
            "- **Remedy:** District-level extraction requires custom processing of unit-level microdata files (DDI format). In accordance with our anti-fabrication mandate (ADR 003), we refuse to generate synthetic district numbers for PLFS and mark it as requiring manual extraction.",
            "",
            "---",
            "",
            "## 7. Synthetic & Demonstration Fixtures Isolation",
            "",
            "- **`SRC_EXAMPLE_SYNTHETIC`:** Isolated exclusively under `data/sample/`. Clearly labeled as synthetic test fixture and strictly excluded from production data counts and economic analysis.",
            "",
        ])

        report_content = "\n".join(md_lines)
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_content, encoding="utf-8")
            logger.info("Saved coverage report Markdown to: %s", output_path)

        return report_content
