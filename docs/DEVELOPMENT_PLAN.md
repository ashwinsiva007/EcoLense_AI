# EconLens AI — Multi-Stage Development Roadmap

This document outlines the systematic, controlled multi-stage engineering plan for **EconLens AI**. Each stage represents a discrete milestone with explicit deliverables, acceptance criteria, and quality gates.

---

## Roadmap Overview

| Stage | Milestone | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Engineering Foundation & Skeleton** | **ACTIVE (Completed)** | Project structure, config, logging, tests, work log, base app. |
| **Stage 2** | **Data Ingestion & Validation** | Scheduled | Geography finalization, data loader, schema validator, data dictionary. |
| **Stage 3** | **Exploratory Regional Data Analysis** | Scheduled | Summary stats, disparity indices, correlation matrices, Plotly charts. |
| **Stage 4** | **Regional Opportunity Scoring & Ranking** | Scheduled | Multi-dimensional index, weight calibration, choropleth maps, factor breakdown. |
| **Stage 5** | **Bottleneck & Deficit Detection** | Scheduled | Benchmark gap analytics, critical constraint ranking, diagnostic alerts. |
| **Stage 6** | **Forecasting, Scenario Simulation & Reporting**| Scheduled | Time-series forecasting, what-if simulator, automated PDF/HTML reports. |

---

## Detailed Stage Breakdown

### Stage 1: Professional Project Skeleton & Engineering Foundation (CURRENT)
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

### Stage 2: Study Geography Selection, Data Ingestion & Validation
* **Goal:** Select target study geography (e.g. states/districts), curate official open datasets, implement schema validation, and populate the data dictionary.
* **Key Tasks:**
  1. Define the initial target region (e.g., specific state districts or national sample).
  2. Collect official open datasets across socioeconomic, infrastructure, labor, and business domains.
  3. Implement concrete `DataLoader` methods in `src/data/data_loader.py`.
  4. Implement schema and boundary validation in `src/data/validation.py`.
  5. Build the "Data and Sources" dashboard page with data quality reports.
* **Acceptance Criteria:**
  - Real datasets are validated against documented schemas.
  - No synthetic data is presented as real.
  - Missing value audit and data dictionary entries are fully completed.

---

### Stage 3: Exploratory Data Analysis & Spatial Disparity Profiling
* **Goal:** Enable interactive exploration of regional indicators, statistical distributions, and spatial patterns without asserting unvalidated causal claims.
* **Key Tasks:**
  1. Implement univariate and multivariate analysis in `src/analytics/exploratory_analysis.py`.
  2. Build interactive Plotly distribution charts, scatter plots, and correlation heatmaps.
  3. Integrate basic geographic visualizations using GeoPandas and Plotly Choropleth.
  4. Display explicit analytical transparency disclaimers regarding correlation vs. causation.
* **Acceptance Criteria:**
  - Users can filter and compare indicators across selected districts.
  - Statistical summaries accurately compute mean, median, IQR, and regional disparities.

---

### Stage 4: Multi-Dimensional Regional Opportunity Scoring & Ranking
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

### Stage 5: Potential Bottleneck Detection & Diagnostic Diagnostics
* **Goal:** Automatically identify structural constraints and development deficits across regions.
* **Key Tasks:**
  1. Implement benchmark gap heuristics (e.g., district indicator vs. state/national benchmark) in `src/intelligence/bottleneck_detection.py`.
  2. Classify bottleneck severity (High, Moderate, Low) with evidence traceability.
  3. Build the "Bottleneck Analysis" page with diagnostic cards and targeted intervention recommendations.
* **Acceptance Criteria:**
  - Every detected bottleneck links directly to underlying empirical metrics.
  - Clear explanations of the benchmark threshold used for deficit classification.

---

### Stage 6: Forecasting, Scenario Simulation & Comprehensive Reporting
* **Goal:** Provide longitudinal time-series forecasting (where panel data permits), interactive what-if simulations, and exportable intelligence dossiers.
* **Key Tasks:**
  1. Implement time-series projection with confidence intervals in `src/intelligence/forecasting.py`.
  2. Implement mathematical sensitivity simulation in `src/intelligence/scenario_analysis.py`.
  3. Build the "Forecasting" and "Scenario Simulator" pages with interactive shock controls.
  4. Implement report generation (PDF / CSV / Summary dossiers).
* **Acceptance Criteria:**
  - All forecasts disclose underlying model assumptions and prediction uncertainty intervals.
  - Scenario simulation outputs are visibly watermarked as hypothetical mathematical projections.
