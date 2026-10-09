# EconLens AI — Data Dictionary & Schema Registry Template

> **Notice on Current Status:**  
> In accordance with Stage 1 engineering principles, no external regional datasets have been collected or assumed verified yet. This data dictionary serves as the official specification template and audit standard for all datasets to be integrated in **Stage 2 (Data Ingestion & Validation)**.

---

## 1. Dataset Registration Template

When integrating a new regional dataset into `data/raw/` or `data/processed/`, add an entry adhering to the following schema:

```markdown
### [Dataset Identifier / Code] - [Dataset Title]
* **Source Organization / Portal:** (e.g., Census of India, Open Government Data Platform, Reserve Bank of India, NITI Aayog)
* **Source URL / Access Date:** 
* **License / Usage Terms:** (e.g., Open Government Data License, Public Domain, Creative Commons)
* **Geographic Resolution:** (District / Sub-district / State / National)
* **Reference Period / Frequency:** (e.g., 2021-2022 Annual, Census 2011)
* **File Format & Path:** (e.g., CSV / Parquet at `data/raw/<filename>.csv`)
* **Verification Status:** [Pending / Verified / Audited]

| Column Name | Field Description | Data Type | Unit | Allowed Range | Missing Value Strategy | Notes & Quality Flags |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `region_id` | Unique ISO/Census region identifier | String | N/A | Alphanumeric (e.g. 'D_0101') | None allowed (Primary Key) | Standardized district code |
| `region_name` | Official geographic region name | String | N/A | Text | None allowed | Normalized title case |
| `state_name` | Parent state / administrative territory | String | N/A | Text | None allowed | Standardized state name |
```

---

## 2. Standard Indicator Categories & Planned Schemas

The following indicator taxonomy will be populated during Stage 2:

### Domain A: Socioeconomic & Demographics
* Target Fields: Total Population, Urbanization Rate (%), Literacy Rate (%), Dependency Ratio, Median Household Consumption / Income.
* Primary Validation Rules: Urbanization Rate between 0-100%, Literacy between 0-100%, Population > 0.

### Domain B: Labor, Skills & Human Capital
* Target Fields: Worker Population Ratio (WPR), Female Labor Force Participation Rate (FLFPR), Higher Education Enrollment, Technical/Vocational Training Density.
* Primary Validation Rules: Ratios between 0-100%, Non-negative enrollment counts.

### Domain C: Infrastructure & Connectivity
* Target Fields: Paved Road Density (km/sq km), Power Reliability Index (hours/day), Broadband/Cellular Penetration (%), Commercial Rail/Freight Access.
* Primary Validation Rules: Percentages bounded 0-100%, Density >= 0.

### Domain D: Business Dynamism, Financial Access & Industry
* Target Fields: MSME Registration Density, Bank Credit-to-Deposit Ratio (CDR), Commercial Electricity Consumption per Capita, Industrial Cluster Presence.
* Primary Validation Rules: Non-negative financial counts, valid financial ratios.

---

## 3. Data Integrity & Missing Value Policy

1. **Explicit Null Encoding:** Missing values must be recorded as standard `NaN` or `None`. Sentinel values like `-999` or `N/A` strings must be sanitized during ingestion.
2. **Missingness Thresholds:** Columns with greater than 35% missing values across the study geography must not be used in composite opportunity scoring without explicit warning and imputation disclosure.
3. **No Silent Fabrication:** Imputed values must be explicitly tracked with a companion boolean indicator flag (e.g., `<column_name>_is_imputed`) to preserve analytical transparency.
