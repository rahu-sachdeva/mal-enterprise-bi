# Build Mal Enterprise BI in Looker Studio (Question 1)

**Platform:** https://datastudio.google.com/navigation/reporting  
(Looker Studio — formerly Google Data Studio)

This is often the fastest way to get a **public URL with no login** for reviewers.

---

## What you need

1. Google account  
2. Data in Google Sheets (we create/upload this for you)  
3. ~45–60 minutes to build 5 pages in one report  

---

## A) Open the data spreadsheet

Use the Google Sheet linked in the repo README (title):

**Mal Enterprise BI Foundation - Synthetic Data (Looker Studio)**

Tabs you will use:

| Tab | Use for |
|-----|---------|
| `executive_kpi_cards` | Executive KPI scorecards |
| `monthly_trends` | Executive trend charts |
| `credit_funnel_daily` | Credit funnel + risk |
| `conflict_active_customers` | Active Customers conflict |
| `conflict_approval_rate` | Approval Rate conflict |
| `kpi_dictionary` | Dictionary table |
| `self_service_datasets` | Dataset catalogue |
| `self_service_landing` | Access / SLA copy |

Share setting for the Sheet: **Anyone with the link → Viewer** (so Looker Studio can read it).

---

## B) Create the Looker Studio report

1. Open https://datastudio.google.com/navigation/reporting  
2. **Create → Report**  
3. **Add data → Google Sheets**  
4. Select the Mal spreadsheet → pick tab `executive_kpi_cards` → **Add**  
5. When prompted to add to report → **Add to report**

You will add more data sources (other tabs) via **Resource → Manage added data sources → Add a data source**.

---

## C) Page 1 — Executive Dashboard

### Scorecards (8 KPIs)

1. Filter control: add **Drop-down list** on `market` (include All)  
2. For each KPI, add a **Scorecard**:
   - Metric: `value`  
   - Filter on chart: `kpi_id` equals one of:  
     `KPI-P01`, `KPI-C02`, `KPI-C04`, `KPI-C06`, `KPI-F01`, `KPI-F03`, `KPI-Pay01`, `KPI-C08`  
   - Title the scorecard with the KPI name + ID  
   - Format rates as **Percent** (C02, C04, Pay01, C08)

### Trends (add data source `monthly_trends`)

Add 4 time series charts:

| Chart | Dimension | Metric |
|-------|-----------|--------|
| Active Customers | `month` | `active_customers_certified` (AVG) |
| Approval Rate | `month` | `approval_rate_certified` (AVG) → % |
| Outstanding | `month` | `portfolio_outstanding_aed` (AVG) |
| Recognised Revenue | `month` | `revenue_finance_aed` (SUM) |

Header text:

```
Mal Enterprise BI — Executive Dashboard
Certified KPIs only · Synthetic data · Credit · Finance · Product · Payments · Savings
```

Rename page tab: **01 Executive**

---

## D) Page 2 — Credit & Lending

**Page → New page** → name **02 Credit**

Add data source: `credit_funnel_daily`

1. **Filter** on `market`  
2. **Bar / funnel-style chart** (latest day):
   - Create a filter on `date` = max date, or use a date range control set to end of data  
   - Metrics: `credit_applications`, `credit_approved_certified`, `credit_booked`  
   - Or use a table with those three columns for the latest date  
3. **Time series — rates:**
   - Dimension: `date`  
   - Metrics: `approval_rate_certified`, `booking_rate` (Percent)  
4. **Time series — risk:**
   - Metrics: `fpd_rate`, `dpd30_rate` (Percent)  
5. **Outstanding:** `portfolio_outstanding_aed` over `date`

Text note:

```
Uses certified approval rate (KPI-C02), not Credit soft-approval.
Risk: FPD (KPI-C07) and DPD30 (KPI-C08).
```

---

## E) Page 3 — Metric Conflict Resolution

**New page** → **03 Conflict**

### Active Customers

Data source: `conflict_active_customers`

1. Filter: `market`  
2. **Bar chart**
   - Dimension: `definition_owner`  
   - Metric: `value`  
   - Breakdown / color dimension: `status`  
   - Style: certified vs exploratory (green vs orange if possible)  
3. **Table** with: `definition_label`, `definition_owner`, `value`, `status`, `formula`, `why_it_diverges`

### Approval Rate

Data source: `conflict_approval_rate`  
Same layout; format `value` as Percent.

Top text box:

```
CERTIFIED Active Customers (KPI-P01):
Customers with ≥1 open product relationship (active loan OR open savings OR active card),
KYC complete, and not fraud-blocked.

Green/certified = enterprise number for Executive packs.
Orange/exploratory = local analysis only (Product login / Finance revenue / Credit open loan).
```

---

## F) Page 4 — KPI Dictionary

**New page** → **04 Dictionary**

Data source: `kpi_dictionary`

Add a **Table** with columns:

`kpi_id`, `name`, `domain_owner`, `business_definition`, `formula`, `data_source`, `refresh_cadence`, `status`, `where_used`

Add filter controls on `status` and `domain_owner`.

Text: “Certified = Executive/board. Exploratory = local analysis / conflict education only.”

---

## G) Page 5 — Self-Service Landing

**New page** → **05 Self-Service** (put this first if you want — or keep order 01–05)

1. Table from `self_service_landing` (`section`, `detail`)  
2. Table from `self_service_datasets` (all columns)  

Header:

```
Mal Enterprise BI — Self-Service
How to request access, SLAs, and certified datasets
```

---

## H) Make the report public (assessment URL)

1. Top right: **Share**  
2. **Manage access** → turn on **Anyone with the link** can **View**  
3. Copy link — looks like:  
   `https://lookerstudio.google.com/reporting/xxxxxxxx`  
4. Open that link in an **incognito** window (logged out) — must load without sign-in  
5. Optional: **File → Embed report** if you need an embed, but the reporting URL is enough for the form  

Also set the **Google Sheet** to Anyone with the link → Viewer so the report does not break for reviewers.

---

## I) Submit

| Deliverable | What to paste |
|-------------|----------------|
| Deployed BI Dashboard | Your Looker Studio report URL (incognito-tested) |
| GitHub | https://github.com/rahu-sachdeva/mal-enterprise-bi |

Update the Live dashboard row in README once you have the URL.

---

## Tips

- Use **page navigation** left side so reviewers can switch Executive / Credit / Conflict / Dictionary / Self-Service.  
- Keep titles short; put KPI IDs on scorecards.  
- If a chart is blank, check the data source tab is the right sheet and date filter is not excluding all rows.  
- Never submit only https://datastudio.google.com/navigation/reporting — that is the home page, not your report.
