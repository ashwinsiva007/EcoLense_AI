# EconLens AI — Architectural Decision Records (ADRs)

This document captures key architectural and technical decisions made during the design and development of **EconLens AI**.

---

## ADR 001: Modular Monolithic Architecture

* **Date:** 2026-10-09
* **Status:** Accepted
* **Context:**  
  EconLens AI is being developed as an explainable regional economic intelligence tool by a focused student engineering team. We need rapid development, ease of debugging, strong type contracts, and simple deployment without infrastructure overhead.
* **Decision:**  
  Adopt a modular monolith architecture organized into discrete packages: `config`, `src.data`, `src.analytics`, `src.intelligence`, `src.dashboard`, and `src.utils`.
* **Consequences:**  
  - Simplifies local development, test execution, and deployment.
  - Avoids microservices overhead, inter-service networking, and distributed failure modes.
  - Enforces strict one-way dependency boundaries to maintain modularity.

---

## ADR 002: UI Framework Selection (Streamlit) & Python 3.11+

* **Date:** 2026-10-09
* **Status:** Accepted
* **Context:**  
  The application requires interactive geographic maps, parameter sliders (for what-if scenarios), multi-tab navigation, and data tables while maintaining tight integration with scientific Python libraries (Pandas, Plotly, Scikit-learn).
* **Decision:**  
  Use **Streamlit** as the unified presentation layer paired with **Plotly** for responsive visualizations.
* **Consequences:**  
  - Eliminates the need for a separate frontend JavaScript framework (e.g. React/Vue) and backend REST API layer for this stage.
  - Allows rapid prototyping of data dashboards with pure Python.
  - Requires clean separation between presentation functions (`src.dashboard`) and core calculation modules to avoid coupling UI logic with analytics.

---

## ADR 003: Strict Prohibition of Silent Data Fabrication

* **Date:** 2026-10-09
* **Status:** Accepted
* **Context:**  
  In economic and regional analytics, presenting synthetic or randomized statistics as real regional metrics creates severe misinformation risks.
* **Decision:**  
  Enforce a strict anti-fabrication rule across the entire application:
  1. The platform will never silently generate fake data when real data is missing.
  2. In the absence of verified datasets, the application renders clear, informative empty/welcome states.
  3. Any demonstration or synthetic dataset used for unit tests or UI verification must reside exclusively under `data/sample/` and be visibly marked as synthetic in the interface.
* **Consequences:**  
  - Builds trust and ensures academic and professional integrity.
  - Requires robust data validation and empty-state UI handling.

---

## ADR 004: Explainable Scoring Models & Non-Causal Disclaimers

* **Date:** 2026-10-09
* **Status:** Accepted
* **Context:**  
  Machine learning models and composite indices are often treated as black-box predictors or mistaken for proof of causality.
* **Decision:**  
  All opportunity scoring, bottleneck detection, and forecasting modules must:
  1. Provide transparent factor decompositions showing exactly how an index was computed.
  2. Include explicit analytical disclosures stating that opportunity scores are heuristic comparative indices and do not guarantee economic growth or prove causal relationships.
  3. Clearly separate empirical findings from hypothetical what-if scenario simulations.
* **Consequences:**  
  - Prevents overclaiming and misinterpretation of analytical outputs.
  - Enforces rigorous metadata and explanation contracts in data structures.

---

## ADR 005: Cross-Platform Path Handling with `pathlib.Path`

* **Date:** 2026-10-09
* **Status:** Accepted
* **Context:**  
  Development takes place on Windows, while continuous integration and eventual deployment may run on Linux or macOS.
* **Decision:**  
  Use Python's standard `pathlib.Path` across all configuration, data loading, logging, and test routines. Forbid hardcoded string path separators (`\` or `/`).
* **Consequences:**  
  - Guarantees seamless compatibility across Windows, Linux, and macOS environments.

---

## ADR 006: Canonical Long-Form Observation Model for Regional Data

* **Date:** 2026-10-11
* **Status:** Accepted (Stage 2A)
* **Context:**  
  Regional economic datasets originate from diverse ministries, census departments, and statistical agencies with inconsistent tabular layouts (e.g. wide tables with indicators or years as column headers). A rigid wide table schema breaks whenever new indicators or survey cycles are introduced.
* **Decision:**  
  Standardize on a **long-form observation schema** as the universal data interchange format:
  `[region_id, region_name, parent_region_id, geographic_level, indicator_code, indicator_name, value, unit, reference_period, source_id, source_record_id, collection_date, quality_status, notes]`.
  The composite primary key is `(region_id, indicator_code, reference_period)`.
* **Consequences:**  
  - Accommodates arbitrary indicators, survey years, and geographic resolutions without schema migrations.
  - Provides a predictable target contract for wide-to-long transformation functions.
  - Requires pivot/unmelt steps when presenting wide comparative matrices to end users.

---

## ADR 007: Structured Dataset Source Registry & Provenance Lifecycle

* **Date:** 2026-10-11
* **Status:** Accepted (Stage 2A)
* **Context:**  
  Academic and policy intelligence tools must provide full lineage for every published statistic. Datasets should not be assumed verified merely because an open data portal URL exists.
* **Decision:**  
  Maintain an explicit JSON source registry (`data/metadata/source_registry.json`) with an enforceable four-stage verification lifecycle:
  1. `planned`: Identified candidate dataset; file not yet downloaded.
  2. `acquired`: Raw file obtained and preserved in `data/raw/`; unvalidated.
  3. `validated`: File passed schema, bounds, duplicate, and geographic checks.
  4. `rejected`: File failed validation checks or licensing is unsuitable.
* **Consequences:**  
  - Prohibits unverified data from silently entering production analytics.
  - Captures publisher citations, licensing terms, update frequency, and coverage notes.

---

## ADR 008: Strict Anti-Imputation and Safe Preprocessing Policy

* **Date:** 2026-10-11
* **Status:** Accepted (Stage 2A)
* **Context:**  
  Standard machine-learning pipelines routinely fill missing numerical values with zero, mean, or median. In regional economic analysis, replacing a missing district's literacy rate or credit ratio with zero creates catastrophic distortions.
* **Decision:**  
  1. Missing economic observations are strictly preserved as explicit `NaN` values.
  2. Automated zero-replacement of missing values is strictly forbidden.
  3. Imputation cannot occur during general data loading or preprocessing; any future imputation must be explicitly configurable, accompanied by transparency flags (`<indicator>_is_imputed`), and disclosed to the user.
  4. Preprocessing pipelines must be non-destructive: raw files are immutable, and cleaning summaries (`CleaningReport`) must document all transformations.
* **Consequences:**  
  - Preserves empirical integrity and prevents fabricated statistics.
  - Forces downstream analytics to handle missing data explicitly and transparently.
