# EconLens AI — Multi-Stage Development Roadmap

This document outlines the systematic, controlled multi-stage engineering plan for **EconLens AI**. Each stage represents a discrete milestone with explicit deliverables, acceptance criteria, and quality gates.

---

## Roadmap Overview| Stage | Milestone | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Engineering Foundation & Skeleton** | **Completed** | Project structure, config, logging, tests, work log, base app. |
| **Stage 2A** | **Data Architecture & Dataset Readiness** | **Completed** | Canonical observation schema, source registry, safe loader, validator, preprocessor, synthetic fixtures. |
| **Stage 2B** | **Study Geography & Real Dataset Ingestion** | **Completed** | Tamil Nadu pilot (32 districts), 4 genuine datasets acquired, 448 canonical observations, CLI pipeline, coverage report. |
| **Stage 3** | **Exploratory Regional Data Analysis** | **Completed** | Reusable EDA pipeline, 14-indicator summary statistics, regional rankings, correlation matrices, Plotly charts, markdown & JSON reports, 156 passed tests. |
| **Stage 4** | **Regional Opportunity Scoring & Ranking** | Scheduled | Multi-dimensional index, weight calibration, choropleth maps, factor breakdown. |
| **Stage 5** | **Bottleneck & Deficit Detection** | Scheduled | Benchmark gap analytics, critical constraint ranking, diagnostic alerts. |
| **Stage 6** | **Forecasting, Scenario Simulation & Reporting**| Scheduled | Time-series forecasting, what-if simulator, automated PDF/HTML reports. |

---

## Detailed Stage Breakdown

### Stage 1: Professional Project Skeleton & Engineering Foundation (Completed)
* **Goal:** Establish a clean, maintainable modular monolith, centralized configuration, structured logging, testing suite, and development tracking.
* **Deliverables:**
  - Project directory hierarchy with `.gitkeep` placeholders.
  - Centralized settings in `config/settings.py` with cross-platform path handling.
  - Reusable logging in `src/utils/logging_config.py`.
  - Foundational contracts in `src/data/`, `src/analytics/`, `src/intelligence/`, `src/dashboard/`.
  - Runnable Streamlit base application in `app.py`.
  - Comprehensive documentation (`README.md`, `ARCHITECTURE.md`, `DEVELOPMENT_PLAN.md`, `DATA_DICTIONARY.md`, `DECISIONS.md`).
  - Automated test suite in `tests/`.
  - Permanent development work log in `PROJECT_WORKLOG.md`.

---

### Stage 2A: Data Architecture & Dataset Readiness (Completed)
* **Goal:** Establish robust, reusable data contracts, canonical long-form schema, dataset source registry, safe loading, schema validation, safe preprocessing, and quality reporting without fabricating or collecting external data prematurely.
* **Deliverables:**
  - Canonical long-form observation model and composite primary key in `src/data/schema.py`.
  - Dataset Source Registry and provenance tracking in `src/data/source_registry.py` and `data/metadata/source_registry.json`.
  - Reusable, immutable file loader (`load_csv`, `load_json`, `DataLoader`) with granular exception types in `src/data/data_loader.py`.
  - Schema, bounds, geographic hierarchy, and duplicate key validator in `src/data/validation.py`.
  - Safe preprocessing, text trimming, numeric coercion, and `wide_to_long_observations` with strict anti-imputation policy in `src/data/preprocessing.py`.
  - Data quality and readiness summary generator in `src/data/quality_report.py`.
  - Deterministic synthetic test fixture in `data/sample/synthetic_district_observations.csv`.
  - Comprehensive automated test suite in `tests/`.

---

### Stage 2B: Study Geography Selection & Real Dataset Ingestion (Completed)
* **Goal:** Establish a reliable, reproducible real-data pipeline grounded in Tamil Nadu (32 districts), acquiring, validating, and standardizing genuine multi-domain datasets across demographics, enterprise formalization, banking, and infrastructure.
* **Key Deliverables:**
  1. Pilot study geography established: Tamil Nadu (32 baseline districts, State Code `33`).
  2. Four genuine official datasets acquired and preserved in `data/raw/`:
     - `census_2011_tn_pca.csv` (Census 2011 Primary Census Abstract)
     - `udyam_msme_2022_23_tn.csv` (Ministry of MSME Udyam Portal)
     - `rbi_slbc_cd_ratio_2020_21_tn.csv` (RBI / SLBC Banking Statistics)
     - `tn_does_infrastructure_2020_21.csv` (TN Department of Economics & Statistics)
3. Decoupled adapter classes in `src/data/adapters/`: `CensusTNAdapter`, `UdyamTNAdapter`, `BankingTNAdapter`, `InfrastructureTNAdapter`.
  4. Secure network fetcher with strict SSL verification in `src/data/acquisition/fetcher.py`.
  5. 448 validated canonical long-form observations in `data/processed/canonical_observations_tn.csv`.
  6. Machine-readable inventory (`data_inventory.json`) and coverage report (`data_coverage_report.md`).
  7. Reproducible CLI pipeline runner (`scripts/manage_data.py` & `src/data/pipeline.py`).
  8. Automated test suite expanded to 94 tests with 100% pass rate.

---

### Stage 3: Exploratory Regional Data Analysis & Disparity Profiling (Completed)
* **Goal:** Enable rigorous, reproducible exploratory data analysis of the validated Tamil Nadu canonical observations, generate analytical outputs, and establish dashboard visual specifications without asserting unvalidated causal claims.
* **Key Deliverables:**
  1. Reusable, modular analytics engine in `src/analytics/exploratory_analysis.py`:
     - `compute_dataset_overview`, `compute_data_quality`, `compute_indicator_statistics`, `compute_regional_rankings`, `compute_regional_comparisons`, `compute_time_series_availability`, `compute_indicator_correlations`, `filter_observations`.
  2. Publication-grade dark-themed chart builders in `src/analytics/eda_charts.py`:
     - Regional comparison horizontal bar charts, box plots, histograms, bivariate scatter plots, correlation heatmaps, and missingness visualizations.
  3. Reproducible reporting pipeline in `src/analytics/eda_report.py` and CLI orchestrator `scripts/run_eda.py`:
     - Machine-readable summary: `data/processed/eda_summary.json`.
     - Cross-sectional regional wide table: `data/processed/regional_summary_tn.csv` (32 districts × 14 indicators).
     - Analytical diagnostic report: `docs/EDA_REPORT.md`.
  4. Comprehensive Dashboard Visual & UX Design Specification: `docs/DASHBOARD_SPEC.md`.
  5. Architectural Decision Record: ADR 012 in `docs/DECISIONS.md`.
  6. Automated test suite expanded to **156 tests** (62 new tests in `tests/test_eda.py` and `tests/test_imports.py`) with 100% pass rate.
* **Acceptance Criteria Verified:**
  - Zero missing values, zero infinite values, and zero duplicate keys across 448 verified observations.
  - Transparent non-causal disclosures accompanying all bivariate correlations.
  - Zero synthetic observations presented as real data.

---

### Stage 4: Multi-Dimensional Regional Opportunity Scoring & Ranking (Scheduled)
* **Goal:** Calculate transparent, explainable composite opportunity scores across regions.
* **Key Tasks:**
  1. Implement indicator normalization (Min-Max / Z-score / Percentile) in `src/data/preprocessing.py`.
  2. Implement composite index calculation in `src/analytics/opportunity_scoring.py` with configurable dimension weights:
     - Infrastructure & Connectivity
     - Human Capital & Labor Skills
     - Business Dynamism & Enterprise Density
     - Socioeconomic Health
  3. Provide full factor decomposition and confidence notes for each district.
  4. Build the "Opportunity Explorer" page with interactive ranking tables and comparative choropleths.
* **Acceptance Criteria:**
  - Opportunity score formulas and weights are fully transparent and user-inspectable.
  - UI explicitly states that opportunity scores are comparative indices and do not guarantee growth.

---

### Stage 5: Potential Bottleneck Detection & Diagnostic Diagnostics (Scheduled)
* **Goal:** Automatically identify structural constraints and development deficits across regions.
* **Key Tasks:**
  1. Implement benchmark gap heuristics in `src/intelligence/bottleneck_detection.py`.
  2. Classify bottleneck severity (High, Moderate, Low) with evidence traceability.
  3. Build the "Bottleneck Analysis" page with diagnostic cards and targeted intervention recommendations.
* **Acceptance Criteria:**
  - Every detected bottleneck links directly to underlying empirical metrics.
  - Clear explanations of the benchmark threshold used for deficit classification.

---

### Stage 6: Forecasting, Scenario Simulation & Comprehensive Reporting (Scheduled)
* **Goal:** Provide longitudinal time-series forecasting (where panel data permits), interactive what-if simulations, and exportable intelligence dossiers.
* **Key Tasks:**
  1. Implement time-series projection with confidence intervals in `src/intelligence/forecasting.py`.
  2. Implement mathematical sensitivity simulation in `src/intelligence/scenario_analysis.py`.
  3. Build the "Forecasting" and "Scenario Simulator" pages with interactive shock controls.
  4. Implement report generation (PDF / CSV / Summary dossiers).
* **Acceptance Criteria:**
  - All forecasts disclose underlying model assumptions and prediction uncertainty intervals.
  - Scenario simulation outputs are visibly watermarked as hypothetical mathematical projections.
