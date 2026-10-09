# EconLens AI — Regional Economic Intelligence Platform

[![Stage](https://img.shields.io/badge/Stage-1%20Engineering%20Foundation-blue.svg)](#current-implementation-status)
[![Python](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](#environment-setup)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#)

**EconLens AI** is an explainable regional economic intelligence platform designed to uncover economic growth opportunities and identify structural development bottlenecks across geographical districts and sub-regions.

---

## 1. Problem Statement

Regional economic planners, local industry leaders, researchers, and policy analysts often struggle with fragmented datasets scattered across disconnected domains—including demographics, infrastructure, labor skills, financial depth, and industry density. Without unified data integration, explainable comparative metrics, and transparent diagnostics, regional development strategies risk relying on guesswork or black-box predictions that lack empirical grounding.

---

## 2. Proposed Solution

EconLens AI provides a unified, evidence-based analytical system that:
* Ingests, harmonizes, and validates multi-domain regional indicators.
* Computes transparent, explainable **Regional Opportunity Scores** across infrastructure, human capital, business dynamism, and socioeconomic health.
* Diagnoses critical **Regional Bottlenecks** by identifying deficits against state and national benchmarks.
* Provides **Interactive What-If Scenario Simulations** and longitudinal forecasting where panel data exists.
* Upholds strict analytical honesty: clearly distinguishing empirical facts from hypothetical model simulations, and rejecting black-box causal claims.

---

## 3. Main Planned Capabilities

1. **Regional Data Ingestion & Validation:** Schema enforcement, missing data auditing, and geographic alignment.
2. **Exploratory Data Analysis (EDA):** Disparity indices, statistical distributions, and correlation matrices.
3. **Opportunity Scoring & Ranking:** Multi-dimensional opportunity index with user-calibrated weights and factor decomposition.
4. **Bottleneck Diagnostics:** Benchmark gap detection and prioritized intervention roadmaps.
5. **Longitudinal Forecasting:** Time-series projection with explicit confidence intervals and assumption disclosures.
6. **Scenario Simulator:** Sensitivity modeling for hypothetical policy and capital investment shocks.
7. **Interactive Dashboard & Dossier Export:** Visual choropleths, comparison tables, and downloadable summary reports.

---

## 4. Technology Stack

* **Language:** Python 3.11+
* **User Interface:** [Streamlit](https://streamlit.io/)
* **Data Processing & Numerical Computing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Interactive Visualizations:** [Plotly](https://plotly.com/python/)
* **Machine Learning & Modeling (Planned):** [Scikit-learn](https://scikit-learn.org/), [Joblib](https://joblib.readthedocs.io/)
* **Geospatial Processing (Planned):** [GeoPandas](https://geopandas.org/), [Shapely](https://shapely.readthedocs.io/)
* **Testing & Quality Assurance:** [Pytest](https://pytest.org/)
* **Environment & Logging:** Python standard `logging`, `python-dotenv`, `pathlib`

---

## 5. Project Directory Structure

```
econlens-ai/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Direct dependencies with version constraints
├── README.md                   # Project documentation and quickstart guide
├── PROJECT_WORKLOG.md          # Permanent chronological engineering work log
├── .gitignore                  # Git exclusions for secrets, venvs, and cache
├── .env.example                # Template for environment configuration
│
├── config/                     # Centralized settings & path management
│   ├── __init__.py
│   └── settings.py
│
├── src/                        # Core source packages
│   ├── __init__.py
│   ├── data/                   # Ingestion, validation, preprocessing contracts
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── preprocessing.py
│   │   └── validation.py
│   ├── analytics/              # Exploratory analysis & opportunity scoring contracts
│   │   ├── __init__.py
│   │   ├── exploratory_analysis.py
│   │   └── opportunity_scoring.py
│   ├── intelligence/           # Bottlenecks, forecasting, scenario simulation
│   │   ├── __init__.py
│   │   ├── bottleneck_detection.py
│   │   ├── forecasting.py
│   │   └── scenario_analysis.py
│   ├── dashboard/              # Streamlit UI layouts and reusable components
│   │   ├── __init__.py
│   │   ├── layout.py
│   │   └── components.py
│   └── utils/                  # Logging and utility helpers
│       ├── __init__.py
│       └── logging_config.py
│
├── data/                       # Data tiers (excluded from Git, preserved with .gitkeep)
│   ├── raw/                    # Raw external datasets
│   ├── processed/              # Normalized, validated datasets
│   └── sample/                 # Isolated synthetic demonstration datasets
│
├── models/                     # Serialized model artifacts and scalers
│
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_imports.py
│   ├── test_configuration.py
│   └── test_app_helpers.py
│
├── docs/                       # Technical architecture & specifications
│   ├── ARCHITECTURE.md         # System design and component data flow
│   ├── DEVELOPMENT_PLAN.md     # Multi-stage roadmap and deliverables
│   ├── DATA_DICTIONARY.md      # Dataset schema specification template
│   └── DECISIONS.md            # Architectural Decision Records (ADRs)
│
└── logs/                       # Application runtime logs
```

---

## 6. Environment Setup & Quickstart

### Prerequisites
* Python 3.11 or higher installed on your system.
* Git for version control.

### Step 1: Clone or Open the Workspace
```bash
git clone <repo-url>
cd ecolense_ai
```

### Step 2: Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment (Optional)
```bash
cp .env.example .env
```

---

## 7. Running the Application & Test Suite

### Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your web browser at `http://localhost:8501`.

### Run Automated Tests
```bash
pytest -v
```

---

## 8. Current Implementation Status

| Feature / Module | Status | Notes |
| :--- | :--- | :--- |
| **Project Skeleton & Directory Structure** | ✅ Completed | Fully initialized with strict package boundaries |
| **Configuration (`config/settings.py`)** | ✅ Completed | Dataclass settings with env override & pathlib |
| **Structured Logging (`src/utils/`)** | ✅ Completed | Idempotent console & file logging handlers |
| **Data Contracts (`src/data/`)** | ✅ Completed | Interfaces defined; concrete ingestion in Stage 2 |
| **Analytics Contracts (`src/analytics/`)** | ✅ Completed | Interfaces defined; concrete scoring in Stage 4 |
| **Intelligence Contracts (`src/intelligence/`)** | ✅ Completed | Interfaces defined; bottleneck heuristics in Stage 5 |
| **Streamlit Base UI (`app.py`, `src/dashboard/`)** | ✅ Completed | Dark-oriented theme, navigation, welcome state |
| **Automated Test Suite (`tests/`)** | ✅ Completed | Unit tests for imports, configuration, helpers |
| **Technical Documentation (`docs/`)** | ✅ Completed | Architecture, roadmap, data dictionary, ADRs |
| **Permanent Work Log (`PROJECT_WORKLOG.md`)** | ✅ Active | Initialized for Stage 1 tracking |
| **Study Geography & Real Dataset Ingestion** | ⏳ Scheduled | Scheduled for **Stage 2** |
| **Opportunity Scoring Algorithm** | ⏳ Scheduled | Scheduled for **Stage 4** |
| **Bottleneck Diagnostics Engine** | ⏳ Scheduled | Scheduled for **Stage 5** |
| **Longitudinal Forecasting & Scenarios** | ⏳ Scheduled | Scheduled for **Stage 6** |
