# EconLens AI — Dataset Inventory & Coverage Report

> **Generated:** `2026-10-11 14:27:47 UTC`  
> **Milestone:** Stage 2B — Real Dataset Acquisition & Source Verification  
> **Pilot Geography:** Tamil Nadu (32 Baseline Districts)  

---

## 1. Executive Summary

- **Total Registered Datasets:** `6`
- **Genuine Datasets Acquired:** `4`
- **Genuine Datasets Validated:** `4`
- **Datasets Requiring Manual Extraction:** `1`
- **Total Standardized Observations:** `448`
- **Distinct Regional Entities:** `32` districts
- **Unique Economic Indicators:** `14` indicators
- **Reference Periods Covered:** `2011, 2020-21, 2022-23`

---

## 2. Acquired & Verified Real Datasets

| Dataset ID | Title & Publisher | Coverage | Period | Records | Status | Indicators |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SRC_CENSUS_2011_TN` | **Census of India 2011 - Primary Census Abstract (Tamil Nadu)**<br>_Office of the Registrar General & Census Commissioner, India (ORGI)_ | Tamil Nadu (32 Districts) (district) | `2011` | `160` | **VALIDATED** | `POPULATION_TOT`, `LIT_RATE_TOT`, `LIT_RATE_FEM`, `WPR_TOT`, `WPR_FEM` |
| `SRC_UDYAM_MSME_TN_2023` | **Ministry of MSME - Udyam Registration District Statistics (Tamil Nadu)**<br>_Ministry of Micro, Small and Medium Enterprises, Government of India_ | Tamil Nadu (32 Districts) (district) | `2022-23` | `128` | **VALIDATED** | `MSME_MICRO_COUNT`, `MSME_SMALL_COUNT`, `MSME_MEDIUM_COUNT`, `MSME_TOTAL_COUNT` |
| `SRC_RBI_BANKING_TN_2021` | **RBI & SLBC Tamil Nadu - District Credit and Deposit Statistics**<br>_Reserve Bank of India & State Level Bankers' Committee (SLBC) Tamil Nadu_ | Tamil Nadu (32 Districts) (district) | `2020-21` | `96` | **VALIDATED** | `CREDIT_DEPOSIT_RATIO`, `BANK_CREDIT_AMT`, `BANK_DEPOSIT_AMT` |
| `SRC_TN_DOES_INFRA_2021` | **Department of Economics & Statistics - District Road Infrastructure (Tamil Nadu)**<br>_Department of Economics and Statistics (DoES), Government of Tamil Nadu_ | Tamil Nadu (32 Districts) (district) | `2020-21` | `64` | **VALIDATED** | `ROAD_SURFACED_KM`, `ROAD_DENSITY` |
| `SRC_PLANNED_PLFS_NSSO_2022` | **Periodic Labour Force Survey (PLFS) Annual Report (Candidate Source)**<br>_National Sample Survey Office (NSSO), MoSPI_ | India / Tamil Nadu (state) | `2021-22` | `0` | **PLANNED** | `WPR_TOT`, `FLFPR_TOT` |

---

## 3. Geographic & Administrative Integrity

### 3.1 Pilot Study Geography: Tamil Nadu Districts
- **Baseline District Count:** 32 districts (aligned with Census 2011 Primary Census Abstract, State Code `33`).
- **District Identifier Schema:** Composite identifier `33_<census_code>` (e.g. `33_602` for Thiruvallur to `33_633` for Tiruppur).
- **Parent Administrative Unit:** `33` (Tamil Nadu state).

### 3.2 Boundary Harmonization & Comparability Disclosure
> [!WARNING]
> **District Bifurcation Advisory (ADR 010):**  
> Between 2018 and 2020, 6 new districts were carved out in Tamil Nadu:  
> 1. *Tenkasi* (from Tirunelveli)  
> 2. *Chengalpattu* (from Kancheepuram)  
> 3. *Tirupathur* and *Ranipet* (from Vellore)  
> 4. *Kallakurichi* (from Viluppuram)  
> 5. *Mayiladuthurai* (from Nagapattinam)  
> 
> **Platform Enforcement:** To prevent temporal incomparability and false missingness, all datasets are harmonized to the verified 32-district baseline. Post-2018 portal statistics (e.g. Udyam MSME) for bifurcated units are aggregated back to parent boundaries. No unweighted cross-temporal joins are permitted without explicit boundary mapping.

---

## 4. Indicator Catalog & Temporal Coverage

| Domain | Indicator Code | Indicator Name | Unit | Bounds | Reference Period | Source ID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Demographics | `POPULATION_TOT` | Total Resident Population | `count` | `[1.0, None)` | `2011` | `SRC_CENSUS_2011_TN` |
| Demographics | `LIT_RATE_TOT` | Effective Literacy Rate (Total) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |
| Demographics | `LIT_RATE_FEM` | Effective Literacy Rate (Female) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |
| Labor Force | `WPR_TOT` | Worker Population Ratio (Total) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |
| Labor Force | `WPR_FEM` | Worker Population Ratio (Female) | `percentage` | `[0.0, 100.0]` | `2011` | `SRC_CENSUS_2011_TN` |
| Enterprise | `MSME_MICRO_COUNT` | Registered Micro Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |
| Enterprise | `MSME_SMALL_COUNT` | Registered Small Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |
| Enterprise | `MSME_MEDIUM_COUNT` | Registered Medium Enterprises | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |
| Enterprise | `MSME_TOTAL_COUNT` | Total Registered MSME Units | `count` | `[0.0, None)` | `2022-23` | `SRC_UDYAM_MSME_TN_2023` |
| Financial | `CREDIT_DEPOSIT_RATIO` | Credit-Deposit Ratio (Commercial Banks) | `percentage` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |
| Financial | `BANK_CREDIT_AMT` | Total Bank Credit | `crore_inr` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |
| Financial | `BANK_DEPOSIT_AMT` | Total Bank Deposits | `crore_inr` | `[0.0, None)` | `2020-21` | `SRC_RBI_BANKING_TN_2021` |
| Infrastructure | `ROAD_SURFACED_KM` | Length of Surfaced Roadways | `km` | `[0.0, None)` | `2020-21` | `SRC_TN_DOES_INFRA_2021` |
| Infrastructure | `ROAD_DENSITY` | Surfaced Road Density | `km_per_sq_km` | `[0.0, None)` | `2020-21` | `SRC_TN_DOES_INFRA_2021` |

---

## 5. Provenance & Official Source Citations

1. **Census of India 2011 — Primary Census Abstract (PCA):**  
   - Publisher: Office of the Registrar General & Census Commissioner, India (ORGI), Ministry of Home Affairs  
   - Official Portal: [https://censusindia.gov.in](https://censusindia.gov.in)  
   - License: Open Government Data License - India (OGDL)  

2. **Ministry of MSME — Udyam Registration Portal:**  
   - Publisher: Ministry of Micro, Small and Medium Enterprises, Government of India  
   - Official Portal: [https://dashboard.msme.gov.in](https://dashboard.msme.gov.in)  
   - License: Open Government Data License - India (OGDL)  

3. **Reserve Bank of India & SLBC Tamil Nadu — Banking Statistics:**  
   - Publisher: Reserve Bank of India (DSIM) & State Level Bankers' Committee Tamil Nadu (Indian Overseas Bank)  
   - Official Portal: [https://data.rbi.org.in](https://data.rbi.org.in) / [https://www.slbctn.com](https://www.slbctn.com)  
   - License: RBI Public Data Dissemination  

4. **Department of Economics & Statistics (DoES), Tamil Nadu — Road Infrastructure:**  
   - Publisher: Department of Economics and Statistics, Government of Tamil Nadu  
   - Official Portal: [https://www.tn.gov.in/deptst](https://www.tn.gov.in/deptst)  
   - Reference: *Statistical Hand Book of Tamil Nadu*, Table 23.1 Length of Roads  
   - License: Government Open Statistical Publication  

---

## 6. Known Incompatibilities & Planned Manual Datasets

### 6.1 Periodic Labour Force Survey (PLFS) District Estimates Barrier
- **Status:** `planned` (Candidate Source `SRC_PLANNED_PLFS_NSSO_2022`)
- **Issue:** Annual PLFS reports published by MoSPI/NSSO do not report district-level work participation rates due to small sampling clusters at the district tier. Only State and NSS-Region aggregates are officially published.
- **Remedy:** District-level extraction requires custom processing of unit-level microdata files (DDI format). In accordance with our anti-fabrication mandate (ADR 003), we refuse to generate synthetic district numbers for PLFS and mark it as requiring manual extraction.

---

## 7. Synthetic & Demonstration Fixtures Isolation

- **`SRC_EXAMPLE_SYNTHETIC`:** Isolated exclusively under `data/sample/`. Clearly labeled as synthetic test fixture and strictly excluded from production data counts and economic analysis.
