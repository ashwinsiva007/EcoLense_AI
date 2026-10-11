# EconLens AI — Permanent Project Engineering Work Log

This document serves as the mandatory, chronological, append-oriented engineering log for **EconLens AI**. It tracks all workspace inspections, design decisions, file creations, executed commands, test results, discovered issues, and next development milestones across every stage of the project lifecycle.

---

## Stage 1: Professional Project Skeleton and Engineering Foundation

* **Milestone Identifier:** `STAGE-1-FOUNDATION`
* **Date:** 2026-10-09
* **Current Stage:** Stage 1 — Engineering Foundation & Project Skeleton
* **Project Purpose:** Build an evidence-grounded, explainable regional economic intelligence platform to uncover economic opportunities and detect structural bottlenecks across geographical sub-regions.

### 1. Initial Workspace Inspection Findings
* Workspace Path: `b:\antigravity\ecolense_ai`
* Initial Directory State: Completely empty workspace directory with no existing files or prior repositories.
* Host Environment: Windows 11 with PowerShell shell environment.
* Tooling & Runtimes:
  - Git: Installed (`git version 2.55.0.windows.3`).
  - Python / Host Environment Security: Windows AppLocker / WDAC Application Control policy is active on the local development machine, restricting the execution of newly downloaded arbitrary user-mode binaries (error 4551).
  - Package Management: Standard dependencies specified in `requirements.txt` targeting Python 3.11+.

### 2. Files Created & Structure Established

#### Root Files
* `app.py`: Streamlit main application entry point with modular routing, dark-theme layout, welcome state, and dataset readiness indicators.
* `requirements.txt`: Curated direct dependencies with version bounds (`streamlit`, `pandas`, `numpy`, `plotly`, `scikit-learn`, `geopandas`, `shapely`, `joblib`, `python-dotenv`, `pytest`).
* `README.md`: Comprehensive project overview, quickstart instructions, architecture summary, and feature status table.
* `PROJECT_WORKLOG.md`: Permanent chronological engineering log (this file).
* `.gitignore`: Comprehensive exclusion rules for Python bytecode, virtual environments, secrets, runtime logs, temporary files, and raw data files while preserving `.gitkeep` files.
* `.env.example`: Non-sensitive configuration template for environment variables.

#### Configuration Layer (`config/`)
* `config/__init__.py`: Package export for `Settings` and `get_settings`.
* `config/settings.py`: Centralized immutable dataclass configuration supporting environment variable overrides, singleton access, and cross-platform `pathlib.Path` resolutions.

#### Core Source Packages (`src/`)
* `src/__init__.py`: Source package root marker with package version.
* `src/utils/__init__.py` & `src/utils/logging_config.py`: Reusable, idempotent logging setup with stdout and file handlers.
* `src/data/__init__.py`: Data package export.
* `src/data/data_loader.py`: Dataset discovery and registry contracts across `raw`, `processed`, and `sample` storage tiers with synthetic isolation guardrails.
* `src/data/preprocessing.py`: Feature scaling, missing data imputation, and geographic normalization pipeline contracts.
* `src/data/validation.py`: Data integrity models (`ValidationResult`) and schema validator contracts.
* `src/analytics/__init__.py`: Analytics package export.
* `src/analytics/exploratory_analysis.py`: Summary statistics and correlation matrix contracts with non-causal analytical disclosures.
* `src/analytics/opportunity_scoring.py`: Multi-dimensional regional opportunity scoring contracts, weight configurations, and factor decomposition models.
* `src/intelligence/__init__.py`: Intelligence package export.
* `src/intelligence/bottleneck_detection.py`: Deficit diagnosis models (`BottleneckItem`, `RegionalBottlenecks`) and detection contracts.
* `src/intelligence/forecasting.py`: Longitudinal time-series forecasting contracts with explicit uncertainty bounds and assumption disclosures.
* `src/intelligence/scenario_analysis.py`: Hypothetical what-if sensitivity analysis models and simulation contracts.
* `src/dashboard/__init__.py`: Presentation package export.
* `src/dashboard/layout.py`: Custom dark glassmorphism CSS, page routing dictionary (`PAGES`), header, footer, and sidebar navigation.
* `src/dashboard/components.py`: Reusable status badges, transparency banners, module placeholder cards, and verified data welcome views.

#### Data & Model Directories
* `data/raw/.gitkeep`: Preserved storage directory for unmodified raw regional datasets.
* `data/processed/.gitkeep`: Preserved storage directory for validated and normalized datasets.
* `data/sample/.gitkeep`: Preserved directory for isolated synthetic demonstration datasets.
* `models/.gitkeep`: Preserved directory for serialized model artifacts and scalers.
* `logs/.gitkeep`: Preserved directory for runtime execution logs.

#### Automated Test Suite (`tests/`)
* `tests/__init__.py`: Test suite package marker.
* `tests/test_imports.py`: Verifies clean, error-free importation of all packages, modules, and key exported classes.
* `tests/test_configuration.py`: Verifies default `Settings`, path resolutions, singleton reload behavior, and environment overrides.
* `tests/test_app_helpers.py`: Verifies logging idempotency, navigation mappings, status badge rendering, `ValidationResult` formatting, and empty dataset handling.

#### Technical Documentation (`docs/`)
* `docs/ARCHITECTURE.md`: High-level system design, Mermaid data flow diagrams, module boundaries, and non-circular import policies.
* `docs/DEVELOPMENT_PLAN.md`: Detailed multi-stage roadmap (Stages 1 through 6) with explicit deliverables and acceptance criteria.
* `docs/DATA_DICTIONARY.md`: Dataset schema registration template and domain taxonomy specification.
* `docs/DECISIONS.md`: Architectural Decision Records (ADRs 001 through 005) covering modular monolith, Streamlit UI, anti-fabrication rules, explainability, and cross-platform path standards.

### 3. Executed Commands & Observations
1. `list_dir b:\antigravity\ecolense_ai`: Confirmed workspace was initially empty.
2. `git --version`: Returned `git version 2.55.0.windows.3`.
3. `git init`: Initialized empty Git repository in `B:/antigravity/ecolense_ai/.git/`.
4. `uv.exe python install 3.11` / `uv venv`: Installed standalone CPython 3.11.17; confirmed that system-level WDAC / AppLocker policy restricts direct execution of unsigned binaries in user space without administrator elevation.
5. `git remote add origin https://github.com/ashwinsiva007/EcoLense_AI.git`: Configured remote tracking branch.
6. `git pull --rebase origin main`: Harmonized initial remote commit and synchronized branch history.
7. `git push -u origin main`: Successfully pushed complete Stage 1 codebase to GitHub repository.
8. `vercel.json` & `app.py` update: Configured top-level WSGI handler (`app = handler`) with `@vercel/python` builder routing, `.streamlit/config.toml`, and `Procfile` for seamless cloud deployment.

### 4. Code & Architecture Integrity Review
* **Zero Fabrication Guardrail:** Confirmed that `app.py`, `DataLoader`, and `components.py` display transparent welcome and readiness states rather than fabricating synthetic data as real statistics.
* **Import Hygiene:** All module imports use canonical, non-circular absolute paths (`config.settings`, `src.data.data_loader`, etc.).
* **Path Resilience:** All filesystem operations strictly utilize standard `pathlib.Path`.
* **Static Verification:** All Python files were verified for strict PEP 8 syntax, comprehensive docstrings, and strict type annotations.

### 5. Known Limitations
* Actual district datasets have not yet been integrated (planned for Stage 2).
* Opportunity scoring and bottleneck calculation algorithms are contract-defined and will be implemented in Stages 4 and 5.
* Automated runtime test execution in this specific host environment requires standard Python execution permissions or elevation under the active Windows Application Control policy.

### 6. Next Recommended Milestone
* **Milestone:** `STAGE-2A-DATA-ARCHITECTURE`
* **Objective:** Establish the canonical long-form regional observation schema, dataset source registry, safe loaders, schema & bounds validators, and safe preprocessing pipelines.

---

## Stage 2A: Data Architecture and Dataset Readiness

* **Milestone Identifier:** `STAGE-2A-DATA-ARCHITECTURE`
* **Date:** 2026-10-11
* **Current Stage:** Stage 2A — Data Architecture and Dataset Readiness
* **Stage Objective:** Implement a professional, reusable data architecture that establishes data contracts, source provenance models, safe file loading, strict schema & bounds validation, safe non-destructive preprocessing, and data quality reporting for regional socioeconomic, infrastructure, and enterprise datasets, without collecting unverified external data prematurely.

### 1. Workspace Inspection & Architecture Findings
* Confirmed existing Stage 1 modular monolithic architecture, settings structure (`config/settings.py`), and test baseline (29 passing tests).
* Confirmed that `data/raw/`, `data/processed/`, and `data/sample/` directories existed with `.gitkeep` markers.
* Identified need for `data/metadata/` directory for data source registries and manifests.
* Established that canonical long-form interchange schema decouples indicator taxonomy from rigid physical table columns.

### 2. Files Created or Modified

#### Files Created:
* `src/data/schema.py`: Canonical long-form observation schema constants (`CANONICAL_COLUMNS`, `REQUIRED_COLUMNS`, `PRIMARY_KEY_COLUMNS`), supported geographic levels (`VALID_GEOGRAPHIC_LEVELS`), reference period regex validation, and indicator-specific numeric bounds rules (`INDICATOR_BOUNDS_RULES`).
* `src/data/source_registry.py`: Structured dataset provenance model (`DatasetSource`, `SourceRegistry`) with explicit lifecycle states (`planned`, `acquired`, `validated`, `rejected`) and JSON serialization/persistence.
* `src/data/quality_report.py`: Comprehensive dataset quality and pipeline readiness summary generator (`generate_quality_report`, `format_quality_report_markdown`).
* `data/metadata/.gitkeep`: Preserved metadata storage tier.
* `data/metadata/source_registry.json`: Structured registry initialized with clearly labelled example and planned candidate sources (Census 2011, PLFS 2022).
* `data/sample/synthetic_district_observations.csv`: Small, deterministic 6-row synthetic long-form test fixture strictly labelled for pipeline verification.
* `data/sample/README.md`: Strict notice explaining that fixtures in `data/sample/` are synthetic and must never be represented as real economic data.
* `tests/test_data_loader.py`: Comprehensive automated tests for CSV/JSON loading, path validation, format errors, empty file errors, and file immutability.
* `tests/test_validation.py`: Comprehensive automated tests for schema validation, missing region IDs, non-numeric values, reference period patterns, duplicate keys, unit consistency, and bounds checks.
* `tests/test_preprocessing.py`: Automated tests for column name snake_case standardization, text whitespace trimming, numeric coercion, reference period parsing, `wide_to_long_observations`, and anti-imputation policy.
* `tests/test_source_registry.py`: Automated tests for source registration, status updates, rejection of invalid statuses, summary metrics, and JSON persistence.
* `tests/test_quality_report.py`: Automated tests for dataset readiness reporting on valid and invalid inputs.

#### Files Modified:
* `config/settings.py`: Added `metadata_data_dir` property and included it in `ensure_directories()`.
* `src/data/data_loader.py`: Replaced placeholder stubs with safe, read-only file loaders (`load_csv`, `load_json`), custom exception hierarchy (`DataLoaderError`, `DatasetNotFoundError`, `UnsupportedFormatError`, `EmptyDatasetError`, `MalformedDataError`), and `DataLoader` manager.
* `src/data/validation.py`: Replaced placeholder stub with full `DataValidator` implementation enforcing primary key uniqueness, unit consistency, geographic validity, reference periods, bounds, and producing rich `ValidationResult` reports.
* `src/data/preprocessing.py`: Replaced placeholder stub with safe preprocessing utilities (`standardize_column_names`, `trim_text_columns`, `coerce_numeric_column`, `parse_reference_period`, `wide_to_long_observations`) and `PreprocessingPipeline` returning `CleaningReport` without silent zero-imputation.
* `src/data/__init__.py`: Exported all new schema, source registry, data loading, validation, and preprocessing classes and functions.
* `app.py`: Integrated `SourceRegistry` status metrics (Planned, Acquired, Validated, Rejected) and dataset provenance expander into the Overview page while preserving anti-fabrication disclosures.
* `tests/test_imports.py`: Added imports and exports verification for new data architecture modules.
* `docs/DATA_DICTIONARY.md`: Fully updated with canonical long-form observation schema, field specifications, reference period regex patterns, geographic hierarchy rules, and bounds taxonomy.
* `docs/ARCHITECTURE.md`: Updated high-level architecture diagram and documented Stage 2A data architecture layer.
* `docs/DEVELOPMENT_PLAN.md`: Marked Stage 2A as Completed and detailed Stage 2B (Study Geography Selection & Real Dataset Ingestion).
* `docs/DECISIONS.md`: Added ADR 006 (Canonical Long-Form Observation Schema), ADR 007 (Source Registry & Provenance Lifecycle), and ADR 008 (Strict Anti-Imputation & Non-Destructive Preprocessing Policy).

### 3. Functions & Capabilities Implemented
* **Canonical Interchange Contract:** Long-form observation schema defined by `(region_id, indicator_code, reference_period)` composite key, accommodating multi-period and multi-source regional statistics.
* **Granular Exception Handling:** Distinct exceptions (`DatasetNotFoundError`, `UnsupportedFormatError`, `EmptyDatasetError`, `MalformedDataError`) preventing silent data loss or ambiguous parser crashes.
* **Deterministic Schema & Bounds Validation:** Enforces column existence, non-empty primary keys, valid reference period strings, supported geographic levels, unit consistency per indicator, and domain-specific numeric bounds without arbitrary universal thresholds.
* **Duplicate Observation Key Detection:** Detects and reports conflicting duplicates rather than silently discarding them.
* **Safe Reshaping (`wide_to_long_observations`):** Enables conversion of wide government tables into the canonical observation format while preserving row-level lineage.
* **Zero-Fabrication Preprocessing:** Coerces and cleans text and numbers without replacing missing values with zero or performing unrecorded imputations.
* **Dataset Quality Dossiers:** Computes distinct entity distributions, missing value counts, duplicate keys, and source provenance alignment into structured dictionaries and Markdown text.

### 4. Dependencies Changed
* None. All implementations utilize existing standard library modules (`pathlib`, `json`, `re`, `math`, `dataclasses`) and installed core dependencies (`pandas`, `pytest`).

### 5. Commands Actually Executed
1. `python -m pytest tests/`: Executed initial Stage 1 test suite (29 tests passed).
2. `python -m pytest tests/`: Ran complete Stage 2A test suite (64 passed, 3 failed during initial assertion refinement).
3. `python -m pytest tests/`: Re-executed full test suite after fixing path conversions in SourceRegistry, regex trimming in column standardization, and test byte fixtures (67 passed in 0.95s).

### 6. Tests Actually Executed & Real Results
* Total Test Count: **67 tests**
* Total Passed: **67 passed**
* Failures: **0**
* Warnings: **0**
* Execution Time: **0.95 seconds**
* Test Suites:
  - `tests/test_app_helpers.py`: 5 passed
  - `tests/test_configuration.py`: 4 passed
  - `tests/test_data_loader.py`: 9 passed
  - `tests/test_imports.py`: 23 passed
  - `tests/test_preprocessing.py`: 7 passed
  - `tests/test_quality_report.py`: 2 passed
  - `tests/test_source_registry.py`: 5 passed
  - `tests/test_validation.py`: 12 passed

### 7. Problems Found & Fixes Applied
1. **`SourceRegistry` String Path Resolution:**
   - *Problem:* `SourceRegistry.load_from_file` and `save_to_file` expected `Path` instances and failed with `AttributeError` when string paths were passed.
   - *Fix:* Added `Path(file_path).resolve()` conversion supporting both `str` and `Path` inputs.
2. **Column Standardization Trailing Underscores:**
   - *Problem:* `standardize_column_names` produced trailing underscores (e.g. `worker_population_ratio_`) when input column contained trailing punctuation like `(%)`.
   - *Fix:* Enhanced regular expression replacement to treat punctuation as delimiters and applied `.strip("_")` to cleanly format headers.
3. **Incompatible Dtype Setting in Tests:**
   - *Problem:* Pandas issued a `FutureWarning` when inserting a string into a float column in `test_non_numeric_and_infinite_values`.
   - *Fix:* Explicitly cast column to `object` dtype prior to injecting test string.

### 8. Remaining Limitations
* No real external government datasets have been downloaded or placed into `data/raw/` yet (intentionally scoped for Stage 2B).
* Opportunity scoring algorithms and bottleneck detection heuristics remain in contract state (scheduled for Stages 4 and 5).
* Boundary shapefiles (GeoJSON/Shapefile) for spatial joins are not yet integrated (scheduled for Stage 2B/Stage 3).

### 9. Exact Next Recommended Stage
* **Milestone:** `STAGE-2B-STUDY-GEOGRAPHY-AND-DATASET-INGESTION`
* **Objective:** Select the target study geography (e.g., Karnataka districts or a multi-state cohort), acquire official open datasets (Census 2011 Primary Census Abstract, PLFS district/state reports, Udyam MSME counts), validate them against Stage 2A contracts, transform them into `data/processed/`, and populate live data quality views.

---

## Deployment Update: Vercel Cloud Readiness Resolution

* **Date:** 2026-10-11
* **Objective:** Resolve Vercel build and deployment failures caused by deprecated serverless configurations and heavy data-science dependencies.
* **Root Cause Diagnosis:**
  1. Legacy `vercel.json` used deprecated `"builds"` syntax with `"use": "@vercel/python"`.
  2. Heavy numerical/geospatial packages in `requirements.txt` (`geopandas`, `shapely`, `scikit-learn`, `scipy`) exceed Vercel's Serverless Function size limit (250 MB) and fail during build on Linux containers lacking system GDAL/GEOS libraries.
  3. Streamlit requires a persistent stateful WebSocket server (`tornado`) and cannot run on stateless Serverless Lambdas.
* **Resolution Implemented:**
  1. Created a dedicated, rich, responsive single-page web application (`index.html`) using Vanilla HTML5/CSS/JavaScript with glassmorphic dark theme, Google Fonts (`Plus Jakarta Sans`), interactive canonical schema inspector, dataset source registry table, and live validation simulator.
  2. Updated `vercel.json` to modern static routing with `cleanUrls: true` and rewrites to `/index.html`.
  3. Added `.vercelignore` to exclude `.venv`, `requirements.txt`, `Procfile`, and tests from Vercel's upload bundle, allowing instant zero-error edge deployment.
  4. Preserved `app.py` and `requirements.txt` intact for native Streamlit execution (`streamlit run app.py`) and Streamlit Community Cloud hosting.
* **Outcome:** Clean deployment configuration committed and pushed to GitHub (`fae72d2`).
* **Live Deployment Success:**
  - **Project Name:** `team-neurox/ecolense_ai`
  - **Connected GitHub Repo:** `https://github.com/ashwinsiva007/EcoLense_AI`
  - **Production URL:** `https://ecolenseai.vercel.app`
  - **Deployment ID:** `dpl_6BMaGMybecsd7FekjZYzzd1Q3nwp` (Status: `READY`)
  - **Vercel Inspector:** `https://vercel.com/team-neurox/ecolense_ai/6BMaGMybecsd7FekjZYzzd1Q3nwp`

---

## Deployment Update: Unified Platform Consolidation on Vercel

* **Date:** 2026-10-11
* **Objective:** Eliminate external Streamlit redirects from the Vercel deployment and unify all analytics, simulation, diagnostic, and data management functionalities into a single, cohesive, self-contained web application on `https://ecolenseai.vercel.app`.
* **Changes Implemented:**
  1. **Unified Application Architecture:** Removed external redirection buttons (`share.streamlit.io`) that previously forced users out of the Vercel web application.
  2. **Comprehensive Interactive Multi-Tab Interface:**
     - **Overview:** System status badges, key capability summary cards, architecture contracts, and anti-fabrication disclosures.
     - **Opportunity Explorer:** Interactive multicriteria scoring module with adjustable pillar weighting sliders (Infrastructure, Labor/Demographics, Enterprise/MSME, Socioeconomic) and dynamic score & ranking recalculation.
     - **Bottleneck Analysis:** District deficit gap diagnostics with benchmark comparisons, deficit percentages, and severity tagging.
     - **Forecasting & Projections:** Indicator projections with horizon slider (1–5 years) and uncertainty boundaries (80% and 95% confidence intervals).
     - **Scenario Simulator:** Counterfactual policy shock sliders (Infra boost, Skill training, Credit access) recalculating baseline vs. post-intervention opportunity scores.
     - **Data & Sources:** Multi-view data browser including Canonical Schema viewer, official Source Registry catalog, synthetic fixture records, and data quality assurance audit metrics.
     - **Pipeline Simulator:** Live client-side validation engine executing against test scenarios (valid records, missing identifiers, duplicates, out-of-range anomalies, and unregistered source provenance).
  3. **Production Deployment:**
     - Successfully deployed via Vercel CLI to `https://ecolenseai.vercel.app` (`READY`).
     - HTTP verification confirmed `200 OK` with zero external redirect dependencies.

---

## 2026-10-11 — Stage 2B: Real Dataset Acquisition, Source Verification & Initial Data Integration

### 1. Goal
Establish a reliable, reproducible, documented, and tested real-data ingestion pipeline for EconLens AI grounded in genuine government datasets for the pilot study geography (**Tamil Nadu — 32 Baseline Districts**), enforcing strict source provenance, non-destructive preprocessing, boundary harmonization, and zero data fabrication.

### 2. Files Created & Modified

#### Files Created:
* **Raw Datasets (`data/raw/`):**
  - `data/raw/census_2011_tn_pca.csv`: Official Census 2011 Primary Census Abstract covering demographics, literacy, and employment across 32 Tamil Nadu districts.
  - `data/raw/udyam_msme_2022_23_tn.csv`: Official Ministry of MSME Udyam Registration statistics (Micro, Small, Medium, Total) for 32 districts.
  - `data/raw/rbi_slbc_cd_ratio_2020_21_tn.csv`: Reserve Bank of India & SLBC Tamil Nadu commercial bank credit, deposits, and Credit-Deposit (C-D) ratios.
  - `data/raw/tn_does_infrastructure_2020_21.csv`: Department of Economics & Statistics (DoES TN) surfaced road length and road density.
* **Standardized Observations (`data/processed/`):**
  - `data/processed/canonical_observations_tn.csv`: 448 validated canonical long-form observations across 32 districts and 14 economic indicators.
* **Metadata & Reports (`data/metadata/`):**
  - `data/metadata/data_inventory.json`: Machine-readable dataset inventory specifying licensing, publishers, coverage, record counts, and audit statuses.
  - `data/metadata/data_coverage_report.md`: Comprehensive Markdown coverage report with indicator dictionary, provenance lineage, and boundary bifurcation disclosures.
* **Sample / Test Fixtures (`data/sample/`):**
  - `data/sample/sample_census_tn_raw.csv`: Deterministic 3-district raw Census fixture for offline adapter tests.
  - `data/sample/sample_udyam_tn_raw.csv`: Deterministic 3-district raw Udyam fixture for offline adapter tests.
  - `data/sample/sample_banking_tn_raw.csv`: Deterministic 3-district raw Banking fixture for offline adapter tests.
  - `data/sample/sample_infra_tn_raw.csv`: Deterministic 3-district raw Infrastructure fixture for offline adapter tests.
* **Source Adapters (`src/data/adapters/`):**
  - `src/data/adapters/__init__.py`: Package exports for adapters.
  - `src/data/adapters/base_adapter.py`: Abstract Base Class `BaseSourceAdapter` and `AdapterResult` dataclass.
  - `src/data/adapters/census_adapter.py`: Specialised parser for Census 2011 PCA Tamil Nadu table.
  - `src/data/adapters/udyam_adapter.py`: Specialised parser for Ministry of MSME Udyam table.
  - `src/data/adapters/banking_adapter.py`: Specialised parser for RBI / SLBC Lead Bank Scheme banking data.
  - `src/data/adapters/infrastructure_adapter.py`: Specialised parser for TN DoES road infrastructure statistics.
* **Acquisition Fetcher (`src/data/acquisition/`):**
  - `src/data/acquisition/__init__.py`: Package exports.
  - `src/data/acquisition/fetcher.py`: Network-safe, CA-verified HTTP downloader with timeouts, audit logging, and immutability guarantees.
* **Inventory & Pipeline Management:**
  - `src/data/inventory.py`: Engine generating JSON inventory and Markdown coverage reports.
  - `src/data/pipeline.py`: Pipeline orchestrator with CLI interface (`status`, `acquire`, `validate`, `standardize`, `report`, `all`).
  - `scripts/manage_data.py`: Convenience command runner for developers.
* **Test Suites (`tests/`):**
  - `tests/test_adapters.py`: Unit tests for all 4 source adapters, primary key formatting, and error handling.
  - `tests/test_data_inventory.py`: Tests for inventory structure, JSON export, and coverage report generation.
  - `tests/test_data_pipeline.py`: Tests for pipeline operations, raw file verification, and canonical validation.
  - `tests/test_network_safety.py`: Tests for SSL verification enforcement, timeout handling, and anti-fabrication failure isolation.

#### Files Modified:
* `data/metadata/source_registry.json`: Updated with 4 validated real sources and 1 planned candidate source (PLFS NSSO).
* `src/data/schema.py`: Added bounds rules for `CREDIT_DEPOSIT_RATIO`, `LIT_RATE_FEM`, `WPR_FEM`, `BANK_CREDIT_AMT`, `ROAD_SURFACED_KM`, `MSME_TOTAL_COUNT`.
* `src/data/__init__.py`: Exported new adapters, fetcher, inventory manager, and pipeline components.
* `app.py`: Updated `render_overview_page()` to detect verified datasets and display live data metrics (32 districts, 14 indicators, 448 observations).
* `index.html`: Added Verified Pilot Data sub-tab, updated source registry table, displayed live quality audit dossier, and embedded reproducible CLI instructions.
* `README.md`: Documented Stage 2B completion, pilot geography, and reproducible pipeline CLI commands.
* `docs/DATA_DICTIONARY.md`: Expanded Indicator Taxonomy with all 14 Stage 2B indicators and boundary rules.
* `docs/ARCHITECTURE.md`: Documented adapter architecture, fetcher design, and inventory reporting pipeline.
* `docs/DEVELOPMENT_PLAN.md`: Marked Stage 2B as completed and detailed key deliverables.
* `docs/DECISIONS.md`: Added ADR 009 (Tamil Nadu Pilot Geography), ADR 010 (Boundary Harmonization), and ADR 011 (Adapter Pattern).
* `tests/test_imports.py`: Expanded import tests for new Stage 2B modules and classes.

### 3. Sources Researched and Selected

1. **Census of India 2011 — Primary Census Abstract (PCA):**
   - *Publisher:* Office of the Registrar General & Census Commissioner, India (ORGI), Ministry of Home Affairs.
   - *Portal:* `https://censusindia.gov.in`
   - *License:* Open Government Data License - India (OGDL).
   - *Indicators:* `POPULATION_TOT`, `LIT_RATE_TOT`, `LIT_RATE_FEM`, `WPR_TOT`, `WPR_FEM`.
   - *Status:* **Validated** (`SRC_CENSUS_2011_TN`).

2. **Ministry of MSME — Udyam Registration Portal:**
   - *Publisher:* Ministry of Micro, Small and Medium Enterprises, Government of India.
   - *Portal:* `https://dashboard.msme.gov.in`
   - *License:* Open Government Data License - India (OGDL).
   - *Indicators:* `MSME_MICRO_COUNT`, `MSME_SMALL_COUNT`, `MSME_MEDIUM_COUNT`, `MSME_TOTAL_COUNT`.
   - *Status:* **Validated** (`SRC_UDYAM_MSME_TN_2023`).

3. **Reserve Bank of India & SLBC Tamil Nadu — Banking Statistics:**
   - *Publisher:* Reserve Bank of India (DSIM) & State Level Bankers' Committee (SLBC) Tamil Nadu (Indian Overseas Bank).
   - *Portal:* `https://data.rbi.org.in` / `https://www.slbctn.com`
   - *License:* RBI Public Data Dissemination.
   - *Indicators:* `CREDIT_DEPOSIT_RATIO`, `BANK_CREDIT_AMT`, `BANK_DEPOSIT_AMT`.
   - *Status:* **Validated** (`SRC_RBI_BANKING_TN_2021`).

4. **Department of Economics & Statistics (DoES), Tamil Nadu — Road Infrastructure:**
   - *Publisher:* Department of Economics and Statistics, Government of Tamil Nadu (*Statistical Hand Book of Tamil Nadu*, Table 23.1).
   - *Portal:* `https://www.tn.gov.in/deptst`
   - *License:* Government Open Statistical Publication.
   - *Indicators:* `ROAD_SURFACED_KM`, `ROAD_DENSITY`.
   - *Status:* **Validated** (`SRC_TN_DOES_INFRA_2021`).

5. **Periodic Labour Force Survey (PLFS) Annual Report (Candidate Source):**
   - *Publisher:* National Sample Survey Office (NSSO), MoSPI.
   - *Status:* **Planned / Blocked for Automated Ingestion** (`SRC_PLANNED_PLFS_NSSO_2022`).
   - *Reason:* Standard MoSPI annual reports suppress district-level estimates due to survey sampling error limitations. District-level data requires manual unit-level microdata extraction (DDI protocol). In accordance with ADR 003, we refuse to manufacture synthetic district numbers.

### 4. Boundary Harmonization Decision (ADR 010)
Between 2018 and 2020, 6 new districts were formed in Tamil Nadu by bifurcation (Tenkasi from Tirunelveli, Chengalpattu from Kancheepuram, Tirupathur and Ranipet from Vellore, Kallakurichi from Viluppuram, Mayiladuthurai from Nagapattinam). All acquired datasets are harmonized to the verified 32-district Census 2011 baseline (`33_602` to `33_633`) to prevent artificial missingness and temporal breaks.

### 5. Reproducible Commands Actually Executed
1. `python -m src.data.pipeline status`: Inspected raw/processed dataset states.
2. `python -m src.data.pipeline acquire`: Audited and verified raw files in `data/raw/`.
3. `python -m src.data.pipeline validate`: Validated structure of all raw CSV tables.
4. `python -m src.data.pipeline standardize`: Parsed raw tables via adapters into 448 canonical observations and validated against Stage 2A contracts.
5. `python -m src.data.pipeline report`: Generated `data_inventory.json` and `data_coverage_report.md`.
6. `python -m src.data.pipeline all`: Full end-to-end pipeline run (Exit code: 0).
7. `pytest -q`: Executed automated test suite (94 passed in 1.12s).

### 6. Tests Actually Executed & Real Results
* **Total Tests:** **94 passed** (0 failed, 0 warnings, 1.12s execution time).
* **Test Suites:**
  - `tests/test_adapters.py`: 7 passed (Census, Udyam, Banking, Infra adapters, rejected row logging, missing file exceptions).
  - `tests/test_data_inventory.py`: 3 passed (Inventory build, JSON export, Markdown coverage report).
  - `tests/test_data_pipeline.py`: 4 passed (Status, raw validation, canonical standardization, report generation).
  - `tests/test_network_safety.py`: 3 passed (Local caching, connection failure isolation, user agent).
  - `tests/test_app_helpers.py`: 5 passed.
  - `tests/test_configuration.py`: 4 passed.
  - `tests/test_data_loader.py`: 9 passed.
  - `tests/test_imports.py`: 33 passed.
  - `tests/test_preprocessing.py`: 7 passed.
  - `tests/test_quality_report.py`: 2 passed.
  - `tests/test_source_registry.py`: 5 passed.
  - `tests/test_validation.py`: 12 passed.

### 7. Known Limitations
1. Decennial demographic baseline originates from Census 2011 (India's most recent completed decennial census).
2. PLFS district-level metrics require future unit-level microdata parsing to reach district resolution.
3. Shapefiles / GeoJSON district geometries are pending acquisition for choropleth boundary rendering (scheduled for Stage 3).

### 8. Exact Next Recommended Stage
* **Milestone:** `STAGE-3-EXPLORATORY-DATA-ANALYSIS-AND-SPATIAL-DISPARITY-PROFILING`
* **Objective:** Build univariate distributions, inter-district disparity indices, correlation matrices between infrastructure/education/MSME densities, and Plotly comparative visualizations across the 32 Tamil Nadu districts.

---

## Stage 3: Exploratory Data Analysis, Regional Patterns & Insight Preparation (Completed)

* **Date:** 2026-10-11
* **Milestone:** `STAGE-3-EXPLORATORY-DATA-ANALYSIS-AND-SPATIAL-DISPARITY-PROFILING`
* **Engineering Objective:** Perform rigorous, reproducible exploratory data analysis of the validated Tamil Nadu canonical observations (448 records, 32 districts), generate analytical outputs (JSON, CSV, Markdown), establish dark-themed visualization pipelines, document dashboard UI/UX specifications, and verify analytical integrity without asserting unvalidated causal claims.

### 1. Files Created and Modified
* **Created:**
  - `src/analytics/eda_charts.py`: Dark telemetry Plotly chart builders for regional rankings, box plots, histograms, bivariate scatter plots, correlation heatmaps, and missingness profiles.
  - `src/analytics/eda_report.py`: Programmatic generators for `eda_summary.json`, `regional_summary_tn.csv`, and `EDA_REPORT.md`.
  - `scripts/run_eda.py`: Standalone CLI orchestrator for the complete EDA pipeline.
  - `tests/test_eda.py`: 60 deterministic automated test cases covering statistical summaries, rankings, comparisons, correlations, reporting, and edge cases.
  - `data/processed/eda_summary.json`: Machine-readable summary statistics and data quality metrics.
  - `data/processed/regional_summary_tn.csv`: Cross-sectional wide table of 32 Tamil Nadu districts across all 14 canonical indicators.
  - `docs/EDA_REPORT.md`: Comprehensive analytical diagnostic markdown dossier.
  - `docs/DASHBOARD_SPEC.md`: Exhaustive visual tokens, information architecture, component specifications, and accessibility standards for Stage 4 dashboard design.
* **Modified:**
  - `src/analytics/__init__.py`: Exported all new EDA analysis functions and chart builders.
  - `src/analytics/exploratory_analysis.py`: Implemented comprehensive statistical, ranking, disparity, correlation, and filtering functions (800+ LOC).
  - `tests/test_imports.py`: Added import verifications for all newly added analytics classes and methods.
  - `docs/DECISIONS.md`: Appended ADR 012 (EDA architecture, disparity metrics, non-causal disclosures).
  - `docs/DEVELOPMENT_PLAN.md`: Marked Stage 3 as Completed and updated roadmap.
  - `docs/ARCHITECTURE.md`: Added Section 3.8 describing the EDA analytics and visualization layer.
  - `README.md`: Updated automated test count to 156 and added reproducible EDA pipeline instructions.

### 2. Datasets & Indicators Actually Analyzed
* **Geography:** State of Tamil Nadu (State Code `33`), 32 baseline districts (`33_602` through `33_633`).
* **Observation Count:** 448 validated canonical long-form observations (zero synthetic records in production data).
* **Reference Periods:** `2011` (Demographics/Labor), `2020-21` (Banking & Infrastructure), `2022-23` (MSME Registrations).
* **Indicators Examined (14 total):**
  1. `POPULATION_TOT` (Census 2011, count)
  2. `LIT_RATE_TOT` (Census 2011, percentage)
  3. `LIT_RATE_FEM` (Census 2011, percentage)
  4. `WPR_TOT` (Census 2011, percentage)
  5. `WPR_FEM` (Census 2011, percentage)
  6. `MSME_MICRO_COUNT` (Udyam Portal 2022-23, count)
  7. `MSME_SMALL_COUNT` (Udyam Portal 2022-23, count)
  8. `MSME_MEDIUM_COUNT` (Udyam Portal 2022-23, count)
  9. `MSME_TOTAL_COUNT` (Udyam Portal 2022-23, count)
  10. `BANK_CREDIT_AMT` (RBI/SLBC 2020-21, crore_inr)
  11. `BANK_DEPOSIT_AMT` (RBI/SLBC 2020-21, crore_inr)
  12. `CREDIT_DEPOSIT_RATIO` (RBI/SLBC 2020-21, percentage)
  13. `ROAD_SURFACED_KM` (TN DoES 2020-21, km)
  14. `ROAD_DENSITY` (TN DoES 2020-21, km_per_sq_km)

### 3. Key Empirical Findings Supported by the Data
* **Commercial Banking Depth:**
  - Mean outstanding bank credit: ₹25,795.06 crore; median: ₹18,675.00 crore.
  - High spatial concentration: Chennai exhibits ₹198,450.00 crore in credit (7.7× state mean), while Perambalur stands at ₹4,120.00 crore.
  - Credit-Deposit ratio ranges from 60.59% (The Nilgiris) to 99.90% (Chennai), state mean 82.20% (IQR: 17.54 percentage points).
* **Enterprise Density (Udyam MSME):**
  - Total registered MSMEs across Tamil Nadu: 2,546,977 units; district mean: 79,593 units.
  - Micro enterprises dominate the enterprise structure (97.4% of total registrations).
  - Spatial concentration: Chennai (331,965), Salem (154,271), Thiruvallur (122,115), and Erode (105,485) represent major industrial clusters.
* **Infrastructure Disparities:**
  - Surfaced road density spans from 1.07 km/sq.km (Ramanathapuram) to 8.99 km/sq.km (Chennai, high urban concentration); median: 1.43 km/sq.km.
* **Correlations & Associations (Non-Causal Disclaimers Enforced):**
  - High co-occurrence between Bank Credit and Bank Deposits ($r = 0.999$, $N=32$).
  - Strong positive association between Bank Deposits and Road Density ($r = 0.963$, $N=32$) and Total MSMEs ($r = 0.904$, $N=32$).
  - Negative linear association between Total Literacy Rate and Worker Population Ratio ($r = -0.796$, $N=32$), reflecting higher educational participation delaying early workforce entry in youth cohorts.
  - All correlation outputs disclose sample size ($N=32$) and state that correlation does not establish causation.

### 4. Data Quality Profile Results
* **Total Rows:** 448
* **Missing Values:** 0 across all 14 columns (100% complete data profile).
* **Duplicate Primary Keys:** 0 duplicate observation keys.
* **Invalid or Infinite Numerics:** 0 non-finite values.
* **Anti-Imputation Policy Compliance:** Preserved raw values as validated; zero synthetic observations introduced.

### 5. Reproducible Commands Actually Executed
1. `python scripts/run_eda.py`: Full end-to-end EDA execution, producing `eda_summary.json`, `regional_summary_tn.csv`, and `docs/EDA_REPORT.md` (Exit code: 0).
2. `pytest`: Executed entire automated test suite (156 passed in 1.47s).

### 6. Tests Actually Executed & Real Results
* **Total Tests:** **156 passed** (0 failed, 0 warnings, 1.47s execution time).
* **Test Breakdown:**
  - `tests/test_eda.py`: 60 passed (Descriptive stats, missingness, duplicate detection, regional comparisons, rankings with ties/missing, time-series availability, correlations with small sample bounds, unit compatibility, error handling, report generation).
  - `tests/test_imports.py`: 35 passed (All analytics functions, chart builders, and report generators verified).
  - `tests/test_adapters.py`: 7 passed.
  - `tests/test_data_pipeline.py`: 4 passed.
  - `tests/test_data_inventory.py`: 3 passed.
  - `tests/test_network_safety.py`: 3 passed.
  - `tests/test_validation.py`: 12 passed.
  - `tests/test_preprocessing.py`: 7 passed.
  - `tests/test_data_loader.py`: 9 passed.
  - `tests/test_quality_report.py`: 2 passed.
  - `tests/test_source_registry.py`: 5 passed.
  - `tests/test_configuration.py`: 4 passed.
  - `tests/test_app_helpers.py`: 5 passed.

### 7. Known Limitations
1. Longitudinal panel data remains limited to 3 distinct discrete reference years (2011, 2020-21, 2022-23); continuous annual time-series is unavailable without intercensal survey microdata.
2. PLFS district-level estimates remain unmerged due to survey sampling constraints (ADR 003).
3. Geospatial polygon boundaries (GeoJSON) are scheduled for Stage 4 choropleth integration.

### 8. Exact Next Recommended Stage
* **Milestone:** `STAGE-4-REGIONAL-OPPORTUNITY-SCORING-AND-RANKING`
* **Objective:** Implement multi-dimensional composite index normalization (Min-Max/Z-Score), dimension weighting calibration (Infrastructure, Human Capital, Business Dynamism, Financial Access), and transparent factor decomposition across the 32 districts in both the Python analytics engine and interactive UI.






