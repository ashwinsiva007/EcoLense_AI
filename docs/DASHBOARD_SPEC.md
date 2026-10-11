# EconLens AI — Dashboard Visual, Information Architecture & UX Specification

> **Milestone:** Stage 3 — Exploratory Data Analysis & Dashboard Design Foundation  
> **Status:** Approved Specification for Stage 4 Implementation  
> **Target Deployments:** Unified Vercel Single-Page Application (`index.html`) & Streamlit UI (`app.py`)

---

## 1. Executive Summary & Design Vision

**EconLens AI** is an evidence-grounded regional economic intelligence platform designed for analysts, researchers, and public decision-makers. The user experience must inspire confidence through institutional rigor, modern ergonomics, and zero ambiguity.

Rather than resembling an academic exercise or a default template, the interface reflects an **advanced telemetry console** tailored for spatial and macroeconomic inquiry. Visual hierarchy, consistent tokenization, restrained use of status colors, and uncompromising typographic clarity are foundational.

---

## 2. Design System & Visual Tokens

### 2.1 Color Palette
The interface is anchored in a deep midnight-charcoal dark mode, using luminance and saturation sparingly to direct analytical focus:

| Token Name | Hex Value | Purpose / Usage |
| :--- | :--- | :--- |
| `--bg-base` | `#070b14` | Primary viewport background; deep obsidian |
| `--surface-panel` | `#0e1526` | Card panels, sidebars, modal surfaces |
| `--surface-elevated` | `rgba(19, 29, 51, 0.75)` | Elevated glassmorphism surfaces with backdrop blur |
| `--surface-card` | `rgba(15, 23, 42, 0.85)` | Data container cards, KPI cards |
| `--border-subtle` | `rgba(255, 255, 255, 0.08)` | Default card and panel outlines |
| `--border-hover` | `rgba(56, 189, 248, 0.40)` | Interactive control focus and hover borders |
| `--accent-primary` | `#38bdf8` (Sky Cyan) | Primary action buttons, active tab indicators, key telemetry |
| `--accent-teal` | `#2dd4bf` (Teal) | Plotly chart traces, secondary highlights |
| `--accent-indigo` | `#818cf8` (Indigo) | Multi-series comparisons, category badges |
| `--accent-purple` | `#c084fc` (Purple) | Simulation overlays, counterfactual models |
| `--status-success` | `#10b981` (Emerald) | Validated datasets, positive differences, passing tests |
| `--status-warning` | `#f59e0b` (Amber) | Provisional data, moderate bottleneck flags, caveats |
| `--status-danger` | `#f43f5e` (Rose) | Critical bottlenecks, schema validation errors, missing data |
| `--text-primary` | `#f8fafc` | Headings, primary metrics, high-contrast labels |
| `--text-secondary` | `#94a3b8` | Body copy, secondary descriptions, axis labels |
| `--text-muted` | `#64748b` | Footers, field metadata, inactive states |

### 2.2 Typography Hierarchy
- **Primary Interface Font:** `'Plus Jakarta Sans'`, system-ui, sans-serif
  - Weights: `400` (Regular), `500` (Medium), `600` (Semi-bold), `700` (Bold), `800` (Extra-bold)
- **Code & Numerical Telemetry Font:** `'JetBrains Mono'`, monospace
  - Weights: `400` (Regular), `600` (Semi-bold)
  - Applied to: Observation keys, region IDs, statistical values, correlation coefficients ($r$), JSON dumps.

### 2.3 Spatial & Elevation Tokens
- **Border Radii:**
  - Badges / Pills: `9999px` (Full round)
  - Controls & Code blocks: `8px` (`--radius-sm`)
  - Content Cards & Tables: `14px` (`--radius-md`)
  - Major Feature Modals / Hero Banners: `20px` (`--radius-lg`)
- **Shadows:**
  - Ambient elevation: `0 10px 30px -10px rgba(0, 0, 0, 0.5)`
  - Active Cyan Glow: `0 0 35px -5px rgba(56, 189, 248, 0.20)`

---

## 3. Information Architecture & Navigation

The platform organizes its analytical capabilities into six core views accessible through a persistent top navigation bar:

```
[ EconLens AI Header & Live Status Telemetry ]
   ├── 🗺️ Overview               (System readiness, dataset inventory, audit summaries)
   ├── 📊 EDA & Analytics        (Univariate distributions, spatial rankings, correlation matrix)
   ├── 📈 Opportunity Explorer   (Stage 4: Composite index, factor decomposition, rankings)
   ├── 🔍 Bottleneck Diagnostics (Stage 5: Benchmark deficit detection, critical constraints)
   ├── 📊 Forecasting Simulator  (Stage 6: Longitudinal projections & confidence bands)
   ├── 🎛️ Scenario Simulator     (Stage 6: Counterfactual policy shocks & elasticity models)
   ├── 📁 Data & Source Registry (Verifiable source provenance, licensing, dataset schemas)
   └── 🧪 Pipeline Simulator     (Interactive client-side contract validation & sanity testing)
```

---

## 4. Analytical Views Specification

### 4.1 View 1: System Overview & Data Health
- **Purpose:** Provide immediate situational awareness of data readiness, verified spatial coverage, and anti-fabrication guarantees.
- **Components:**
  - *Status Banner:* Live build badge (`Stage 3 Active`), verification count (`156/156 Tests Passed`), pilot geography (`Tamil Nadu • 32 Districts`).
  - *Anti-Fabrication Notice:* Explains ADR 003 and ADR 008 guarantees (no imputed zeroes, explicit NaNs).
  - *4 Core KPI Metric Cards:*
    1. Automated Tests Passed (156 tests, 0 regressions)
    2. Canonical Interchange Format (Long-form key: `region_id + indicator_code + period`)
    3. Verified Data Sources (4 official publishers: Census, Udyam, RBI, TN DoES)
    4. Canonical Observations (448 validated records across 32 districts)
  - *Quick-Action Module Navigator:* Direct links to launch specialized analyses.

### 4.2 View 2: Exploratory Data Analysis & Spatial Disparity Profiling
- **Purpose:** Interactive exploration of single and multi-indicator empirical distributions across the 32 Tamil Nadu districts.
- **Sections:**
  1. **Indicator Explorer & Distribution Analyzer:**
     - Dropdown filter to select any of the 14 verified indicators across Demographics, Enterprise, Banking, and Infrastructure.
     - 6-part statistical summary strip: `Count (N)`, `Mean`, `Median`, `Standard Deviation`, `Range (Min - Max)`, `Interquartile Range (IQR)`.
     - Horizontal bar chart ranking all 32 districts with a vertical reference line denoting the state mean.
  2. **Inter-District Disparity Profile:**
     - Highlights highest and lowest observed districts for the selected metric.
     - Displays disparity ratio ($\frac{\text{Max}}{\text{Min}}$) or spread with contextual notes.
  3. **Multi-Indicator Correlation Matrix:**
     - Heatmap matrix displaying Pearson correlation coefficients ($r$) between compatible indicators.
     - Filter to display only strong positive ($r > 0.6$) or strong negative ($r < -0.6$) associations.
     - Mandatory **Non-Causal Disclaimer Card**: Explicitly reiterates that correlation does not establish causation or policy direction.
  4. **Data Quality & Completeness Audit:**
     - Tabular audit showing missing value percentages (0.0% across all 14 indicators), zero infinite values, and zero duplicate keys.

### 4.3 View 3: Regional Opportunity Scoring (Stage 4 Preview)
- **Purpose:** Multi-dimensional index synthesis combining infrastructure, human capital, enterprise density, and banking access.
- **Controls:**
  - Interactive dimension weight sliders (0% to 100%, normalized to 100%).
  - Method selector (Equal weighting vs. Custom calibrated weights).
- **Outputs:**
  - Ranked leaderboard of districts with composite opportunity score (0 to 100).
  - Radar chart / factor breakdown displaying sub-scores per dimension.
  - Transparent formula disclosure.

### 4.4 View 4: Bottleneck Diagnostics (Stage 5 Preview)
- **Purpose:** Automated deficit identification relative to state medians and peer cohorts.
- **Outputs:**
  - Critical constraint alert pills (e.g. "Low Road Density", "Sub-Median CD Ratio", "Female Workforce Participation Deficit").
  - District diagnostic card explaining which factor contributes most negatively to the opportunity score.

### 4.5 View 5: Forecasting & Scenario Simulator (Stage 6 Preview)
- **Purpose:** Prospective simulation of infrastructure investments and enterprise formalization shocks.
- **Controls:**
  - Capital investment shock slider (+0% to +50%).
  - Time horizon selector (1 to 5 years).
- **Outputs:**
  - Simulated score trajectory with projected points gain.
  - Transparent model statement: hypothetical simulation, not guaranteed growth.

### 4.6 View 6: Data Inventory & Source Provenance
- **Purpose:** Uncompromising academic traceability for every single observation.
- **Components:**
  - Source registry table with Publisher, Portal, License, State, and Indicator mapping.
  - Canonical schema viewer and downloadable processed artifacts (`regional_summary_tn.csv`, `eda_summary.json`).

---

## 5. UI Component Guidelines

### 5.1 KPI Metric Cards
```
+------------------------------------------------+
| METRIC LABEL (Uppercase, muted, 12px)         |
| 25,795.06 crore_inr                           |  <- 28px bold, high contrast
| Mean outstanding commercial credit per dist.   |  <- 13px secondary text
| [State Median: 18,675.00]                     |  <- Subtle comparative context
+------------------------------------------------+
```
- Values must always display their physical unit (e.g., `crore_inr`, `percentage`, `km_per_sq_km`).
- Unavailable metrics must render an explicit `—` with an explanatory note rather than `0`.

### 5.2 Responsive Plotly Charts
- Background: `#161b22` (Paper), `#1c2333` (Plot area).
- Grid lines: Subtle `#ffffff0f` opacity (never harsh white).
- Font: `'Plus Jakarta Sans'` / `'Inter'`, size 11–12px.
- Tooltips: Glassmorphism hover cards with bold values, indicator units, and district labels.
- Prohibited chart types: 3D charts, gratuitous pie charts with >4 slices, truncated y-axes on non-zero baseline ratio charts.

### 5.3 Data Tables
- Sticky header row with dark translucent background.
- Left-aligned textual identifiers (`region_name`, `region_id`).
- Right-aligned numeric values with monospace formatting (`font-family: var(--font-mono)`).
- Hover highlights on individual rows (`background: rgba(255, 255, 255, 0.03)`).

---

## 6. Accessibility & Responsiveness Requirements

1. **Color Contrast:** All text-to-background combinations satisfy WCAG 2.1 AA standards (minimum contrast ratio 4.5:1 for normal text, 3:1 for large text).
2. **Non-Reliance on Color Alone:** Status badges combine distinct icons (e.g., `✓`, `⚠`, `✕`) with color indicators.
3. **Viewport Responsiveness:**
   - Desktop (1200px+): Multi-column grid layout with dual-panel side-by-side exploration.
   - Tablet (768px - 1199px): 2-column KPI cards and stacked chart panels.
   - Mobile (< 768px): Single-column stacked layout, horizontal scroll for tables, collapsed navigation.
4. **DOM Semantics:** Unique descriptive element IDs across all interactive filters, buttons, and chart containers to enable automated end-to-end testing.

---

## 7. Next Stage Roadmap Alignment

This specification governs the transition to **Stage 4: Regional Opportunity Scoring & Ranking**. The visual and structural foundation established here will directly host the composite multi-dimensional scoring models without redesigning the UI layout.
