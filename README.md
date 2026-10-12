# Mal Enterprise BI Foundation — Build Challenge (Part 1)

**Role context:** Sole BI hire at Mal (Sharia-compliant digital bank)  
**Scenario:** Credit, Payments, and Savings launching together — no KPI dictionary, no BI platform, domain teams reporting different numbers  
**Data:** Synthetic / illustrative only — no real bank or customer data

This repository is the **working prototype** for the Enterprise BI Foundation assessment.

---

## Public access

| Item | Link |
|------|------|
| **GitHub repository** | https://github.com/rahu-sachdeva/mal-enterprise-bi — **Public** (anyone can view, no login required) |
| **Live dashboard (Google Sheets)** | https://docs.google.com/spreadsheets/d/1ag8hwKSlCm_GwLQvL-EeB2gJeLRqImkE4VmvklMJERc/edit?usp=sharing |

**Google Sheets report** — full Part 1 prototype in one workbook (Executive KPIs, Credit & Lending, Metric Conflict Resolution, KPI Dictionary, Self-Service Landing, plus supporting data tabs). Synthetic data only.

**Sharing (required for reviewers):** In the Sheet → **Share** → **Anyone with the link** → **Viewer**. Test in an **incognito** window while logged out of Google.

**Supporting materials in this repo:**
- Data CSVs / Excel: [`looker_studio/data/`](looker_studio/data/), [`looker_studio/Mal_Enterprise_BI_LookerStudio_Data.xlsx`](looker_studio/Mal_Enterprise_BI_LookerStudio_Data.xlsx)
- Optional Looker Studio build: [`looker_studio/`](looker_studio/)
- Optional Tableau Public pack: [`tableau/`](tableau/)
- Optional Streamlit app: `Home.py` + `pages/`

---

## Problem this prototype solves

Finance, Product, and Credit each define core metrics differently (e.g. Active Customers, Approval Rate, Revenue). Leadership cannot align on a single number. This prototype establishes:

1. A small **certified** metric layer for executive decisions  
2. A visible **conflict resolution** view so disagreements are explicit  
3. A **KPI dictionary** and **self-serve landing** so analysts know what is trusted vs exploratory  

---

## Prototype pages (requirements checklist)

| Requirement | Page |
|-------------|------|
| Executive Dashboard (≥8 KPIs across Credit, Finance, Product) | `pages/01_Executive_Dashboard.py` |
| Credit & Lending domain (funnel, portfolio quality, risk) | `pages/02_Credit_Lending.py` |
| Metric Conflict Resolution (same metric, 3 definitions + certified) | `pages/03_Metric_Conflict_Resolution.py` |
| KPI Dictionary (≥15 metrics with required fields) | `pages/04_KPI_Dictionary.py` + `data/kpi_dictionary.csv` (20 metrics) |
| Self-Service Landing (datasets, access, SLA) | `Home.py` |

---

## Stack choice

| Layer | Choice | Why |
|-------|--------|-----|
| App | **Streamlit** (multi-page) | Public URL without reviewer login; room for narrative + tables on conflict/dictionary pages |
| Charts | **Plotly** | Clear funnel and trends for executive and credit audiences |
| Data | **Generated CSV marts** | Transparent, reproducible; stand in for warehouse certified tables |
| Language | Python | Easy to regenerate data and keep definitions consistent with the dictionary |

In production at Mal I would expect the same logical model behind Power BI / Looker / Metabase, with warehouse tables and proper access control. For this challenge, the goal is governance and consistency — not tool preference.

---

## Data model

**Grain for enterprise KPIs:** `date × market` (`UAE`, `KSA`)

```
scripts/generate_synthetic_data.py
              │
              ▼
data/daily_enterprise_kpis.csv     ← certified measures + conflicting variants
              │
              ├── credit_funnel_daily.csv
              ├── metric_conflict_active_customers.csv
              ├── metric_conflict_approval_rate.csv
              ├── kpi_dictionary.csv
              └── self_service_datasets.csv
```

**System-of-record rules in the model**

| Domain | Source of truth |
|--------|-----------------|
| Credit balances / outstanding / loan status | CBS |
| Recognised revenue | Finance / GL (not Product projected revenue) |
| Executive dashboard tiles | Certified dictionary IDs only |

---

## How to interpret the Metric Conflict Resolution view

Three teams bring three legitimate Active Customers definitions into the same meeting:

| Owner | Definition | Really measures |
|-------|------------|-----------------|
| Product | App login in last 30 days | Engagement |
| Finance | Revenue-recognised transaction in last 90 days | Monetisation |
| Credit | Open loan on CBS | Credit book size |

**Certified definition (KPI-P01)** — marked clearly on the page:

> Distinct customers with ≥1 open product relationship (active loan on CBS **OR** open savings **OR** active card) **AND** KYC complete **AND** not fraud-blocked.

**Certified Approval Rate (KPI-C02):** final approval after KYC + affordability / applications. Credit soft-approvals remain exploratory (`KPI-C03`).

- **Exploratory** (orange) = valid for local analysis  
- **Certified** (green) = only number allowed on the Executive Dashboard  

---

## Consistency rule

Every KPI on the Executive and Credit dashboards is `certified` in the dictionary and uses the same formula. Exploratory metrics appear on the Conflict page (and in the dictionary) so disagreement is visible — not hidden in three spreadsheets.

---

## Repository structure

```
mal-enterprise-bi/
├── Home.py                              # Self-service landing
├── pages/
│   ├── 01_Executive_Dashboard.py
│   ├── 02_Credit_Lending.py
│   ├── 03_Metric_Conflict_Resolution.py
│   └── 04_KPI_Dictionary.py
├── data/                                # Synthetic marts
├── scripts/generate_synthetic_data.py
├── lib/data.py
├── docs/Mal_Enterprise_BI_Strategy_Day1.md   # Part 2 (strategy)
├── requirements.txt
└── README.md
```

---

## Run locally

```bash
git clone <this-repo-url>
cd mal-enterprise-bi
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
streamlit run Home.py
```

Open `http://localhost:8501`.

---

## Deployed live dashboard — Google Sheets

**Primary deliverable for Part 1:**

https://docs.google.com/spreadsheets/d/1ag8hwKSlCm_GwLQvL-EeB2gJeLRqImkE4VmvklMJERc/edit?usp=sharing

Suggested tab structure in the workbook:

| Tab | Content |
|-----|---------|
| `00_Self_Service_Landing` | Datasets available, access request path, SLAs |
| `01_Executive_Dashboard` | 8+ certified enterprise KPIs (Credit / Finance / Product) |
| `02_Credit_Lending` | Approval funnel, portfolio quality, FPD / DPD30 |
| `03_Metric_Conflict` | Active Customers (and Approval Rate) defined 3 ways + certified |
| `04_KPI_Dictionary` | 15+ metrics with owner, definition, formula, source, cadence, status |
| Supporting data tabs | Raw/synthetic marts used by the views above |

**Assessment form:** paste the Google Sheets URL above as the Deployed BI Dashboard link.  
**GitHub form field:** https://github.com/rahu-sachdeva/mal-enterprise-bi

### Optional alternatives in this repo

- Looker Studio: [`looker_studio/`](looker_studio/)  
- Tableau Public: [`tableau/`](tableau/)  
- Streamlit: `streamlit run Home.py`

---

## Assumption

No production Mal datasets were provided for this assessment. I generated a practical synthetic daily dataset covering credit funnel, portfolio quality, payments, savings, recognised revenue, and the conflicting Active Customers / Approval Rate definitions needed to demonstrate KPI governance.

---

## License / disclaimer

Assessment artefact only. Synthetic data. Not affiliated with any real bank. Not for production use.
