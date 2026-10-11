# Build Mal Enterprise BI on Tableau Public (Question 1)

You have **Tableau Desktop** installed. Use it to build, then **publish to Tableau Public** so reviewers get a no-login URL.

**Data file (already generated):**
- Repo: `tableau/Mal_Enterprise_BI_Tableau_Data.xlsx`
- Also copied to: `~/Downloads/Mal_Enterprise_BI_Tableau_Data.xlsx`

**Publish target:** [Tableau Public Discover](https://public.tableau.com/app/discover) — https://public.tableau.com/app/discover  

> **Important for the assessment form:** Do **not** submit the Discover home page URL.  
> After you publish, submit **your workbook / viz URL** (it will look like  
> `https://public.tableau.com/app/profile/<your-name>/viz/<WorkbookName>/<Dashboard>`).  
> Reviewers must open it in incognito with no login.

---

## 0) One-time setup

1. Create / sign in to a free Tableau Public account at https://public.tableau.com/app/discover (same account you will publish with).
2. Open **Tableau Desktop**.
3. **Connect → Microsoft Excel** → select `Mal_Enterprise_BI_Tableau_Data.xlsx`.
4. Drag these sheets into the canvas (or Union/relationships as below):
   - Prefer **separate data sources** per dashboard area if easier, OR one workbook with multiple connections.

**Recommended connections (simple):**

| Connection name | Sheet(s) |
|-----------------|----------|
| `exec_cards` | `executive_kpi_cards` |
| `monthly` | `monthly_trends` |
| `credit` | `credit_funnel_daily` |
| `conflict_active` | `conflict_active_customers` |
| `conflict_approval` | `conflict_approval_rate` |
| `dictionary` | `kpi_dictionary` |
| `catalog` | `self_service_datasets` |
| `landing` | `self_service_landing` |

Click **Sheet 1** when connected.

---

## 1) Executive Dashboard (8+ KPIs)

### Sheet: `Exec KPI Cards`
1. Data source: `executive_kpi_cards`
2. Filter: `market` = **All** (or show Market filter on dashboard)
3. Rows: `kpi_name` (or `kpi_id`)
4. Text: `SUM(value)` → use **AVG** if one row per KPI (should be 1 row per market/KPI)
5. Better: create **8 separate sheets** (one KPI each) for big number cards:
   - Filter each sheet to one `kpi_id` (e.g. KPI-P01)
   - Text: `SUM(value)` or `ATTR(value)`
   - Format percent KPIs as %; currency as AED / number

**8 required certified KPIs**

| kpi_id | Name | Format |
|--------|------|--------|
| KPI-P01 | Active Customers (Certified) | Number |
| KPI-C02 | Approval Rate (Certified) | % |
| KPI-C04 | Booking Rate | % |
| KPI-C06 | Portfolio Outstanding (AED) | Number |
| KPI-F01 | Recognised Revenue (AED) | Number |
| KPI-F03 | Savings AUM (AED) | Number |
| KPI-Pay01 | Payment Success Rate | % |
| KPI-C08 | DPD30 Rate | % |

### Sheet: `Exec Trend - Active`
- Data: `monthly_trends`
- Columns: `month`
- Rows: `AVG(active_customers_certified)`
- Color: `market` (optional)
- Title: Active Customers (Certified) — KPI-P01

### Sheet: `Exec Trend - Outstanding`
- Columns: `month`
- Rows: `AVG(portfolio_outstanding_aed)`
- Title: Portfolio Outstanding — KPI-C06

### Sheet: `Exec Trend - Approval`
- Columns: `month`
- Rows: `AVG(approval_rate_certified)` → format as %
- Title: Approval Rate (Certified) — KPI-C02

### Sheet: `Exec Trend - Revenue`
- Columns: `month`
- Rows: `SUM(revenue_finance_aed)`
- Title: Recognised Revenue — KPI-F01

### Dashboard: `01 Executive Dashboard`
1. Dashboard → New Dashboard → size **Desktop Browser (1000 × 800)** or Automatic  
2. Layout:
   - Top: title “Mal Enterprise BI — Executive Dashboard (Certified KPIs)”
   - Subtitle: “Synthetic data · Credit · Finance · Product · Payments · Savings”
   - Row of 8 KPI cards
   - 2×2 trends underneath
3. Add **Market** filter (from monthly or cards) → apply to all exec sheets  
4. Show caption: “All tiles use certified dictionary IDs only.”

---

## 2) Credit & Lending Domain Dashboard

### Sheet: `Credit Funnel`
- Data: `credit_funnel_daily`
- Filter to latest date: create calc `is_latest` = `[date] = {MAX([date])}` → filter True  
  OR use a relative date / parameter. Simplest: sort date desc and note as-of in title after you pick max date with filter.
- Measures for funnel (Tableau Funnel or bar):
  - `SUM(credit_applications)`
  - `SUM(credit_approved_certified)`
  - `SUM(credit_booked)`
- Use **Funnel** chart type if available, else horizontal bars in that order.

### Sheet: `Credit Rates`
- Columns: `date` (or month)
- Rows: `AVG(approval_rate_certified)`, `AVG(booking_rate)` (dual line or measure names)
- Format as %

### Sheet: `Credit Risk`
- Columns: `date`
- Rows: `AVG(fpd_rate)`, `AVG(dpd30_rate)`
- Format as %
- Title: Risk indicators — FPD (KPI-C07) & DPD30 (KPI-C08)

### Sheet: `Credit Outstanding`
- Columns: `date`
- Rows: `AVG(portfolio_outstanding_aed)`

### Dashboard: `02 Credit & Lending`
- Title + Market filter
- Funnel left / top
- Rates + Risk trends
- Note on dashboard text: “Uses certified approval rate (KPI-C02), not Credit soft-approval.”

---

## 3) Metric Conflict Resolution (critical page)

### Sheet: `Conflict Active Bars`
- Data: `conflict_active_customers`
- Filter: pick one Market (or put Market filter on dashboard)
- Columns: `definition_owner`
- Rows: `SUM(value)`
- Color: `status`  
  - Edit colors: `certified` = green, `exploratory` = orange
- Label: show value
- Sort so Certified is visible
- Title: Active Customers — three definitions + certified

### Sheet: `Conflict Active Table`
- Same data
- Rows: `definition_label`, `definition_owner`, `status`, `formula`, `why_it_diverges`
- Text: `SUM(value)`
- Highlight certified row (color on status)

### Sheet: `Conflict Approval Bars`
- Data: `conflict_approval_rate`
- Columns: `definition_owner`
- Rows: `SUM(value)` → format as %
- Color: `status` (green/orange)

### Dashboard: `03 Metric Conflict Resolution`
- Top text box (important):

```
Certified Active Customers (KPI-P01):
Customers with ≥1 open product relationship (active loan OR open savings OR active card),
KYC complete, and not fraud-blocked.

Executive packs use ONLY the green / certified definition.
Orange bars are valid for local analysis — not for leadership OKRs.
```

- Active bars + table
- Approval conflict section underneath
- Market filter

---

## 4) KPI Dictionary

### Sheet: `KPI Dictionary Table`
- Data: `kpi_dictionary`
- Rows: all fields as discrete:
  - `kpi_id`, `name`, `domain_owner`, `business_definition`, `formula`, `data_source`, `refresh_cadence`, `status`, `where_used`
- Optional filter: `status` (certified / exploratory)
- Fit width; enable scroll
- Title: Enterprise KPI Dictionary (20 metrics)

### Dashboard: `04 KPI Dictionary`
- Full-width table
- Filters for Status + Domain owner
- Text: “Certified = allowed on Executive/board. Exploratory = local analysis / conflict education only.”

---

## 5) Self-Service Landing

### Sheet: `Datasets Catalog`
- Data: `self_service_datasets`
- Table of: `dataset`, `domain`, `description`, `grain`, `access`, `sla`, `status`

### Sheet: `Landing Rules`
- Data: `self_service_landing`
- Table: `section`, `detail`

### Dashboard: `05 Self-Service Landing`
- Title: Mal Enterprise BI — Self-Service
- Landing rules on top
- Dataset catalogue below
- Text: how to request access + SLA (already in data)

---

## 6) Wire the story (optional but strong)

**Dashboard → New Story** named `Mal Enterprise BI Foundation`

Pages in order:
1. Self-Service Landing  
2. Executive Dashboard  
3. Credit & Lending  
4. Metric Conflict Resolution  
5. KPI Dictionary  

Caption each story point in one sentence.

---

## 7) Publish to Tableau Public (live URL, no login)

1. In Tableau Desktop: **Server → Tableau Public → Save to Tableau Public…**  
   (If you only see Tableau Cloud, use **Server → Tableau Public**)
2. Sign in with your Tableau Public account.
3. Workbook name: `Mal Enterprise BI Foundation`
4. Check **Show sheets as tabs** (so reviewers can open all dashboards).
5. Ensure **embedded data** / allow access (do not keep extract private).
6. After publish, open the URL in an **incognito** window (logged out).
7. Copy the public URL — it looks like:  
   `https://public.tableau.com/app/profile/<you>/viz/MalEnterpriseBIFoundation/<Dashboard>`

---

## 8) Paste URL into GitHub README + assessment form

Update the “Live dashboard URL” row in the repo README, commit, push.

Assessment form → Deployed BI Dashboard field → paste the Tableau Public link.

---

## Consistency checklist before you publish

- [ ] Executive cards use only certified KPIs (IDs visible in titles)  
- [ ] Conflict page shows Product / Finance / Credit + green Certified  
- [ ] Dictionary has ≥15 metrics with owner, definition, formula, source, cadence, status  
- [ ] Self-serve page shows datasets + access + SLA  
- [ ] Credit page has funnel + portfolio + at least one risk indicator (FPD or DPD30)  
- [ ] Incognito test works without login  
- [ ] Synthetic data disclaimer in dashboard subtitle  

---

## If “Save to Tableau Public” is missing

1. Install [Tableau Public Desktop](https://public.tableau.com/app/discover) (free) and rebuild by opening the same Excel, **or**  
2. From Tableau Desktop, confirm your license allows Public publish; otherwise export `.twbx` and open in Tableau Public Desktop → publish from there.

---

## Time box (about 60–90 minutes)

| Block | Minutes |
|-------|---------|
| Connect Excel + rename fields | 10 |
| Executive cards + 4 trends + dashboard | 25 |
| Credit dashboard | 15 |
| Conflict dashboard | 15 |
| Dictionary + Self-serve | 15 |
| Publish + incognito test | 10 |
