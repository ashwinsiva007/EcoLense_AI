# EconLens AI — Data Dictionary & Canonical Schema Specification

> **Stage 2A Milestone Status:**  
> This document specifies the official canonical long-form regional observation schema, composite primary keys, geographic hierarchy, reference period standards, and indicator bounds rules for **EconLens AI**. All ingested tabular data must be transformed into and validated against this contract before proceeding to analytics.

---

## 1. Canonical Long-Form Observation Schema

EconLens AI adopts a **long-form observation model** as its canonical interchange format. This model decouples indicator definitions from physical table schemas, accommodating diverse reference periods, missing observations, multiple geographic resolutions, and varying reporting frequencies without structural schema drift.

### Observation Key (Composite Primary Key)
An observation is uniquely identified by the 3-tuple:
$$\text{Observation Key} = (\text{region\_id}, \text{indicator\_code}, \text{reference\_period})$$

Duplicate observation keys are strictly flagged during validation. Conflicting duplicate observations are never silently discarded.

---

## 2. Field Specifications

| Field Name | Type | Nullable? | Category | Description & Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `region_id` | String | **No** | Required | Stable geographical identifier (e.g. Census 2011 code, LGD code, or ISO alpha code). Must not be empty or whitespace. | `"29_572"`, `"KA_BLR"` |
| `region_name` | String | **No** | Required | Official human-readable region label. Title case. | `"Bengaluru Urban"` |
| `parent_region_id` | String | Yes | Contextual | Identifier of parent administrative unit (e.g., state code for district). | `"ST_KA"`, `"29"` |
| `geographic_level` | String | **No** | Required | Administrative level. Allowed: `district`, `state`, `block`, `subdistrict`, `national`. | `"district"` |
| `indicator_code` | String | **No** | Required | Stable machine identifier for the indicator. Uppercase alphanumeric with underscores. | `"LIT_RATE_TOT"` |
| `indicator_name` | String | **No** | Required | Human-readable name of the measured indicator. | `"Total Literacy Rate"` |
| `value` | Float | Yes* | Required | Numeric observation. Kept purely numeric. Cannot contain strings or non-finite values (`inf`). Missing observations must be explicit `NaN`. | `78.5` |
| `unit` | String | **No** | Required | Uniform unit of measurement. Must be consistent for all rows sharing an `indicator_code`. | `"percentage"`, `"km_per_sq_km"` |
| `reference_period` | String | **No** | Required | Standardized reference period string. Must match accepted period formats. | `"2021-22"`, `"2011"` |
| `source_id` | String | **No** | Required | Foreign key reference to the Dataset Source Registry (`data/metadata/source_registry.json`). | `"SRC_CENSUS_2011"` |
| `source_record_id` | String | Yes | Contextual | Original source row identifier or table row index for provenance traceability. | `"REC_042"`, `"LINE_120"` |
| `collection_date` | String | Yes | Contextual | Retrieval date formatted as ISO `YYYY-MM-DD`. | `"2026-10-11"` |
| `quality_status` | String | Yes | Contextual | Validation classification: `raw`, `provisional`, `validated`, or `synthetic`. | `"validated"` |
| `notes` | String | Yes | Contextual | Qualitative interpretation notes, caveats, or definition variations. | `"Computed from PCA Table A-5"` |

*\*Note on Nullability of `value`: While the column itself is required, individual observation values may be null (`NaN`) when an indicator was not measured for that region in that reference period. Missing values are never silently replaced with zero.*

---

## 3. Reference Period Format Standards

All reference periods must adhere to one of the following validated formats:

| Format Pattern | Regular Expression | Description | Example |
| :--- | :--- | :--- | :--- |
| **Annual / Decennial** | `^\d{4}$` | Single calendar or census year | `2011`, `2021` |
| **Short Fiscal / Survey** | `^\d{4}-\d{2}$` | Two-year fiscal or survey cycle (Standard) | `2021-22`, `2022-23` |
| **Long Fiscal / Survey** | `^\d{4}-\d{4}$` | Full four-digit end year (auto-standardized to short) | `2021-2022` |
| **Quarterly (Prefix)** | `^Q[1-4]-\d{4}$` | Quarterly economic accounts | `Q1-2023` |
| **Quarterly (Suffix)** | `^\d{4}-Q[1-4]$` | Alternative quarterly reporting | `2023-Q1` |

---

## 4. Geographic Hierarchy & Resolution Strategy

EconLens AI enforces an explicit geographic hierarchy:

$$\text{National} \longrightarrow \text{State} \longrightarrow \text{District} \longrightarrow \text{Block / Subdistrict}$$

### Key Rules for Geographic Consistency:
1. **Official Codes Over Names:** Regions must be joined using `region_id` (Census/LGD code), never by string matching on `region_name` alone. Regional names frequently vary across portals (e.g. "Bangalore Urban" vs "Bengaluru Urban").
2. **Boundary Stability Disclosures:** Administrative boundaries change over time (e.g., district bifurcations). Longitudinal joins must explicitly account for the reference year's district definitions.
3. **No Automatic Multi-Level Aggregation:** District-level metrics must not be averaged into state-level metrics without population or area weighting.

---

## 5. Indicator Taxonomy & Bounds Rules

Indicator bounds checks are applied specifically, not arbitrarily:

| Domain | Indicator Code | Default Unit | Acceptable Range | Interpretation Caveat |
| :--- | :--- | :--- | :--- | :--- |
| **Demographics** | `POPULATION_TOT` | `count` | `[1.0, None)` | Total resident population from Census 2011 PCA. |
| **Demographics** | `LIT_RATE_TOT` | `percentage` | `[0.0, 100.0]` | Effective literacy rate (population aged 7+). |
| **Demographics** | `LIT_RATE_FEM` | `percentage` | `[0.0, 100.0]` | Effective female literacy rate. |
| **Labor** | `WPR_TOT` | `percentage` | `[0.0, 100.0]` | Total Worker Population Ratio (Main + Marginal). |
| **Labor** | `WPR_FEM` | `percentage` | `[0.0, 100.0]` | Female Worker Population Ratio. |
| **Labor** | `FLFPR_TOT` | `percentage` | `[0.0, 100.0]` | Female Labor Force Participation Rate (PLFS benchmark). |
| **Enterprise** | `MSME_MICRO_COUNT` | `count` | `[0.0, None)` | Registered Micro Enterprises on Udyam portal. |
| **Enterprise** | `MSME_SMALL_COUNT` | `count` | `[0.0, None)` | Registered Small Enterprises on Udyam portal. |
| **Enterprise** | `MSME_MEDIUM_COUNT` | `count` | `[0.0, None)` | Registered Medium Enterprises on Udyam portal. |
| **Enterprise** | `MSME_TOTAL_COUNT` | `count` | `[0.0, None)` | Total registered MSME units on Udyam portal. |
| **Financial** | `CREDIT_DEPOSIT_RATIO` | `percentage` | `[0.0, None)` | Commercial bank credit-deposit ratio (can exceed 100%). |
| **Financial** | `BANK_CREDIT_AMT` | `crore_inr` | `[0.0, None)` | Total gross commercial bank credit outstanding. |
| **Financial** | `BANK_DEPOSIT_AMT` | `crore_inr` | `[0.0, None)` | Total aggregate commercial bank deposits. |
| **Infrastructure** | `ROAD_SURFACED_KM` | `km` | `[0.0, None)` | Total surfaced roadway length (Highways & Local Bodies). |
| **Infrastructure** | `ROAD_DENSITY` | `km_per_sq_km` | `[0.0, None)` | Surfaced road length per unit geographical area. |

---

## 6. Dataset Source Provenance & Registry Model

All data files must correspond to an entry in `data/metadata/source_registry.json`.

### Source Verification Lifecycle States:
- **`planned`**: A candidate dataset identified in research, but file has not yet been acquired.
- **`acquired`**: A source file has been retrieved and placed in `data/raw/`, but structural validation has not yet passed.
- **`validated`**: The dataset has passed schema checks, geographic verification, bounds audits, and unit consistency tests.
- **`rejected`**: The dataset failed quality checks or licensing terms are incompatible.

---

## 7. Data Storage Directory Conventions

- `data/raw/`: Immutable source files. Never modified in-place or overwritten by cleaning routines.
- `data/processed/`: Validated, standardized canonical long-form observations ready for analytics.
- `data/sample/`: Strictly isolated synthetic demonstration fixtures. Never mixed with real economic data.
- `data/metadata/`: Dataset source registry (`source_registry.json`), data dictionaries, and transformation manifests.
