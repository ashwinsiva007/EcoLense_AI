"""Run EDA pipeline against validated canonical observations.

STAGE 3 ANALYSIS SCRIPT — Generates EDA reports from real data.
"""

import sys
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd

from src.analytics.exploratory_analysis import ExploratoryAnalyzer
from src.analytics.eda_report import (
    generate_eda_report_markdown,
    generate_eda_summary_json,
    generate_regional_summary_table,
)

def main():
    """Execute the EDA pipeline against canonical observations."""
    data_file = project_root / "data" / "processed" / "canonical_observations_tn.csv"

    if not data_file.exists():
        print(f"ERROR: Canonical observations file not found: {data_file}")
        sys.exit(1)

    print(f"Loading canonical observations from: {data_file}")
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} observations")

    # Initialize analyzer
    analyzer = ExploratoryAnalyzer(df=df)

    # 1. Dataset Overview
    print("\n=== Dataset Overview ===")
    overview = analyzer.compute_dataset_overview()
    print(f"  Total observations:   {overview.total_observations:,}")
    print(f"  Valid numeric:        {overview.valid_observations:,}")
    print(f"  Distinct regions:     {overview.distinct_regions}")
    print(f"  Distinct indicators:  {overview.distinct_indicators}")
    print(f"  Reference periods:    {', '.join(overview.reference_periods)}")
    print(f"  Sources:              {', '.join(overview.source_ids)}")
    print(f"  Geographic levels:    {', '.join(overview.geographic_levels)}")

    # 2. Data Quality
    print("\n=== Data Quality Profile ===")
    quality = analyzer.compute_data_quality()
    print(f"  Total rows:           {quality.total_rows:,}")
    print(f"  Total columns:        {quality.total_columns}")
    print(f"  Duplicates:           {quality.duplicate_count}")
    print(f"  Invalid numeric:      {quality.invalid_numeric_count}")
    print(f"  Infinite values:      {quality.infinite_count}")
    if quality.missing_by_column:
        print(f"  Missing values:       {quality.missing_by_column}")
    else:
        print(f"  Missing values:       None (100% complete)")

    # 3. Indicator Statistics
    print("\n=== Indicator Statistics ===")
    stats = analyzer.compute_indicator_statistics()
    for s in stats:
        mean_s = f"{s.mean:,.2f}" if s.mean is not None else "N/A"
        med_s = f"{s.median:,.2f}" if s.median is not None else "N/A"
        std_s = f"{s.std:,.2f}" if s.std is not None else "N/A"
        print(
            f"  {s.indicator_code:25s} | N={s.count:3d} | "
            f"Mean={mean_s:>12s} | Median={med_s:>12s} | "
            f"Std={std_s:>10s} | {s.unit} | {s.reference_period}"
        )

    # 4. Time Analysis Check
    print("\n=== Time-Series Availability ===")
    for ind_code in overview.indicator_codes[:3]:
        time_result = analyzer.compute_time_analysis(ind_code)
        print(f"  {ind_code}: {time_result['period_count']} period(s) — "
              f"{'Available' if time_result['time_series_available'] else 'Unavailable'}")

    # 5. Correlation Analysis
    print("\n=== Correlation Analysis ===")
    corr_result = analyzer.compute_correlation_matrix()
    print(f"  Sample size: {corr_result['sample_size']} regions")
    print(f"  Indicators:  {len(corr_result.get('indicators', []))}")
    for pr in corr_result.get("pairwise_results", []):
        corr_str = f"{pr.correlation:.3f}" if pr.correlation is not None else "N/A"
        print(f"  {pr.indicator_a:25s} vs {pr.indicator_b:25s} | r={corr_str:>7s} | n={pr.sample_size}")

    # 6. Generate Reports
    output_dir = project_root / "data" / "processed"

    json_path = output_dir / "eda_summary.json"
    generate_eda_summary_json(analyzer, output_path=json_path)
    print(f"\n  JSON report saved to: {json_path}")

    md_path = project_root / "docs" / "EDA_REPORT.md"
    generate_eda_report_markdown(analyzer, output_path=md_path)
    print(f"  Markdown report saved to: {md_path}")

    csv_path = output_dir / "regional_summary_tn.csv"
    table = generate_regional_summary_table(analyzer, output_path=csv_path)
    print(f"  Regional summary table saved to: {csv_path}")
    print(f"  Table shape: {table.shape}")

    print("\n=== EDA Pipeline Complete ===")


if __name__ == "__main__":
    main()
