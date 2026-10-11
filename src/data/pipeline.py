"""Pipeline orchestration and reproducible CLI commands for EconLens AI Stage 2B.

Provides end-to-end management for checking dataset acquisition status, acquiring
candidate datasets, validating raw source formats, standardizing to the canonical
observation schema, and generating data inventories and coverage reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure stdout/stderr handles UTF-8 safely on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

import pandas as pd

from config.settings import Settings, get_settings
from src.data.acquisition.fetcher import DataFetcher, FetchResult
from src.data.adapters.banking_adapter import BankingTNAdapter
from src.data.adapters.census_adapter import CensusTNAdapter
from src.data.adapters.infrastructure_adapter import InfrastructureTNAdapter
from src.data.adapters.udyam_adapter import UdyamTNAdapter
from src.data.inventory import DataInventoryManager
from src.data.source_registry import SourceRegistry
from src.data.validation import DataValidator, ValidationResult
from src.utils.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger("data.pipeline")


class DataPipeline:
    """Orchestrates real data acquisition, validation, standardization, and reporting."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.settings.ensure_directories()
        self.registry_path = self.settings.metadata_data_dir / "source_registry.json"
        self.registry = (
            SourceRegistry.load_from_file(self.registry_path)
            if self.registry_path.exists()
            else SourceRegistry()
        )
        self.fetcher = DataFetcher(timeout=15.0)
        self.validator = DataValidator(source_registry=self.registry)
        self.inventory_manager = DataInventoryManager(self.settings)

    def check_status(self) -> Dict[str, Any]:
        """Checks and prints the current status of raw and processed datasets."""
        raw_files = list(self.settings.raw_data_dir.glob("*.csv"))
        processed_files = list(self.settings.processed_data_dir.glob("*.csv"))
        sources = self.registry.list_sources()

        print("\n" + "=" * 70)
        print("[STATUS] ECONLENS AI - DATA ACQUISITION & INTEGRATION STATUS")
        print("=" * 70)
        print(f"Total Registered Sources: {len(sources)}")
        print(f"Raw Datasets in data/raw/: {len(raw_files)}")
        print(f"Processed Datasets in data/processed/: {len(processed_files)}")
        print("-" * 70)

        status_rows: List[Dict[str, Any]] = []
        for s in sources:
            file_exists = False
            rec_count = 0
            if s.file_path:
                full_path = self.settings.base_dir / s.file_path
                file_exists = full_path.exists()
                if file_exists:
                    try:
                        rec_count = len(pd.read_csv(full_path))
                    except Exception:
                        pass

            state = "EXISTS" if file_exists else ("PLANNED" if s.verification_status == "planned" else "MISSING")
            print(f"[{state:<8}] {s.source_id:<26} | {s.dataset_name[:32]:<32} | Recs: {rec_count}")
            status_rows.append({
                "source_id": s.source_id,
                "dataset_name": s.dataset_name,
                "file_path": s.file_path,
                "exists": file_exists,
                "record_count": rec_count,
                "status": s.verification_status,
            })

        print("=" * 70 + "\n")
        return {
            "total_sources": len(sources),
            "raw_file_count": len(raw_files),
            "processed_file_count": len(processed_files),
            "sources": status_rows,
        }

    def acquire_datasets(self, force: bool = False) -> Dict[str, FetchResult]:
        """Acquires all configured datasets, verifying files in data/raw/."""
        results: Dict[str, FetchResult] = {}
        print("\n[ACQUISITION] Verifying candidate datasets...")

        for source in self.registry.list_sources():
            s_id = source.source_id
            if s_id.startswith("SRC_EXAMPLE"):
                continue

            if source.verification_status == "planned":
                print(f"  [SKIP] {s_id} (Status: PLANNED - Requires manual extraction)")
                continue

            if not source.file_path:
                print(f"  [WARN] No local path configured for {s_id}")
                continue

            dest_path = self.settings.base_dir / source.file_path
            fetch_res = self.fetcher.fetch_to_file(
                url=source.source_url,
                destination_path=dest_path,
                overwrite=force,
            )
            results[s_id] = fetch_res

            status_icon = "[OK]" if fetch_res.success else "[FAIL]"
            print(f"  {status_icon} [{s_id}] -> {dest_path.name} ({fetch_res.bytes_downloaded:,} bytes)")

        return results

    def validate_raw(self) -> Tuple[bool, List[str]]:
        """Validates all acquired raw CSV files for readable tabular structure."""
        errors: List[str] = []
        print("\n[VALIDATION] Validating raw datasets in data/raw/...")

        expected_files = {
            "census_2011_tn_pca.csv": ["district_code", "district_name", "total_population"],
            "udyam_msme_2022_23_tn.csv": ["district_code", "district_name", "total_msme"],
            "rbi_slbc_cd_ratio_2020_21_tn.csv": ["district_code", "district_name", "credit_deposit_ratio"],
            "tn_does_infrastructure_2020_21.csv": ["district_code", "district_name", "surfaced_road_km"],
        }

        for filename, expected_cols in expected_files.items():
            raw_path = self.settings.raw_data_dir / filename
            if not raw_path.exists():
                err = f"Raw file missing: {raw_path.name}"
                errors.append(err)
                print(f"  [FAIL] {err}")
                continue

            try:
                df = pd.read_csv(raw_path)
                missing_cols = [c for c in expected_cols if c not in df.columns]
                if missing_cols:
                    err = f"{filename} missing mandatory columns: {missing_cols}"
                    errors.append(err)
                    print(f"  [FAIL] {err}")
                else:
                    print(f"  [OK] {filename} passed structure check ({len(df)} rows, {len(df.columns)} cols)")
            except Exception as exc:
                err = f"Failed to read {filename}: {exc}"
                errors.append(err)
                print(f"  [FAIL] {err}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def standardize_datasets(self) -> Tuple[pd.DataFrame, ValidationResult]:
        """Standardizes all raw datasets into canonical long-form observations."""
        print("\n[STANDARDIZATION] Standardizing raw datasets to canonical observations...")

        adapters = [
            (CensusTNAdapter(), self.settings.raw_data_dir / "census_2011_tn_pca.csv"),
            (UdyamTNAdapter(), self.settings.raw_data_dir / "udyam_msme_2022_23_tn.csv"),
            (BankingTNAdapter(), self.settings.raw_data_dir / "rbi_slbc_cd_ratio_2020_21_tn.csv"),
            (InfrastructureTNAdapter(), self.settings.raw_data_dir / "tn_does_infrastructure_2020_21.csv"),
        ]

        all_observations: List[pd.DataFrame] = []

        for adapter, file_path in adapters:
            if not file_path.exists():
                logger.warning("Adapter file not found, skipping: %s", file_path.name)
                continue

            res = adapter.parse(file_path)
            print(f"  [OK] {adapter.source_id:<26}: Parsed {res.parsed_observation_count} observations from {res.raw_row_count} raw rows")
            if res.has_rejections:
                print(f"       [WARN] {len(res.rejected_records)} rows rejected")
            all_observations.append(res.observations)

        if not all_observations:
            raise RuntimeError("No observations were produced by any adapter.")

        merged_df = pd.concat(all_observations, ignore_index=True)

        # Validate canonical schema & bounds
        val_result = self.validator.validate_canonical(merged_df)

        print("\n[AUDIT] Canonical Integrity Validation Result:")
        print(f"  Status: {'PASSED [OK]' if val_result.is_valid else 'FAILED [FAIL]'}")
        print(f"  Total Observations: {val_result.row_count:,}")
        print(f"  Distinct Columns: {val_result.column_count}")
        print(f"  Duplicate Keys: {val_result.duplicate_count}")
        print(f"  Validation Errors: {len(val_result.errors)}")

        if val_result.errors:
            for err in val_result.errors[:5]:
                print(f"    - {err}")

        # Save to data/processed/
        output_path = self.settings.processed_data_dir / "canonical_observations_tn.csv"
        merged_df.to_csv(output_path, index=False)
        print(f"\n[SAVE] Standardized dataset saved to: {output_path}")

        return merged_df, val_result

    def generate_reports(self, observations_df: Optional[pd.DataFrame] = None) -> Tuple[Path, Path]:
        """Generates machine-readable inventory JSON and human-readable coverage Markdown."""
        print("\n[REPORTING] Generating inventory & coverage reports...")

        if observations_df is None:
            proc_path = self.settings.processed_data_dir / "canonical_observations_tn.csv"
            if proc_path.exists():
                observations_df = pd.read_csv(proc_path)

        entries = self.inventory_manager.build_inventory(
            registry=self.registry,
            observations_df=observations_df,
        )

        # Save JSON
        json_path = self.inventory_manager.export_inventory_json(entries)
        print(f"  [OK] Machine-readable inventory: {json_path}")

        # Save Markdown
        md_path = self.settings.metadata_data_dir / "data_coverage_report.md"
        self.inventory_manager.generate_coverage_report_markdown(
            entries=entries,
            observations_df=observations_df,
            output_path=md_path,
        )
        print(f"  [OK] Human-readable report: {md_path}")

        return json_path, md_path

    def run_all(self) -> int:
        """Executes full reproducible pipeline: status -> acquire -> validate -> standardize -> report."""
        print("\n[START] Executing complete reproducible data pipeline (Stage 2B)...")
        self.check_status()
        self.acquire_datasets()
        is_raw_valid, raw_errors = self.validate_raw()
        if not is_raw_valid:
            print("\n[FAIL] Raw dataset validation failed. Halting pipeline.")
            return 1

        obs_df, val_res = self.standardize_datasets()
        if not val_res.is_valid:
            print("\n[FAIL] Canonical observations validation failed. Halting pipeline.")
            return 1

        self.generate_reports(obs_df)
        print("\n[SUCCESS] Pipeline completed successfully! All datasets verified, standardized, and audited.\n")
        return 0


def main() -> None:
    """CLI entrypoint for data pipeline operations."""
    parser = argparse.ArgumentParser(
        description="EconLens AI — Regional Data Acquisition & Ingestion Pipeline"
    )
    parser.add_argument(
        "command",
        choices=["status", "acquire", "validate", "standardize", "report", "all"],
        default="status",
        nargs="?",
        help="Pipeline command to execute",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-acquisition of raw files",
    )

    args = parser.parse_args()
    pipeline = DataPipeline()

    if args.command == "status":
        pipeline.check_status()
        sys.exit(0)
    elif args.command == "acquire":
        pipeline.acquire_datasets(force=args.force)
        sys.exit(0)
    elif args.command == "validate":
        is_valid, _ = pipeline.validate_raw()
        sys.exit(0 if is_valid else 1)
    elif args.command == "standardize":
        _, val_res = pipeline.standardize_datasets()
        sys.exit(0 if val_res.is_valid else 1)
    elif args.command == "report":
        pipeline.generate_reports()
        sys.exit(0)
    elif args.command == "all":
        exit_code = pipeline.run_all()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
