# Fast track — Tableau Public in ~45 minutes

Use this if you want the assessment URL today. Data file:

`/Users/rahul.sachdeva/Downloads/Mal_Enterprise_BI_Tableau_Data.xlsx`

Platform: https://public.tableau.com/app/discover

---

## A) Install / open Tableau Public Desktop (free)

1. Go to https://public.tableau.com/app/discover  
2. Sign up / Sign in  
3. Download **Tableau Public** (free Desktop) if you do not already have it  
4. Open Tableau Public Desktop  

> If you already use Tableau Desktop (paid): you can build there, then use  
> **Server → Tableau Public → Save to Tableau Public…**  
> If that menu item is missing, use free Tableau Public Desktop instead.

---

## B) Connect the data (2 minutes)

1. **Connect → To a File → Microsoft Excel**  
2. Choose `Mal_Enterprise_BI_Tableau_Data.xlsx`  
3. On the left, you will see sheets. Double-click **`executive_kpi_cards`** to open Sheet 1  
4. Rename Sheet 1 → `KPI Card Setup` (optional)

You will switch sheets/connections as you build. Easiest approach: **Data → New Data Source** for each Excel sheet when needed, OR use one connection and switch the table in Data Source tab.

**Simplest for speed:** one Excel connection, then in Data Source drag the sheet you need for each viz (replace table), OR keep multiple data sources:

| For this dashboard | Use Excel sheet |
|--------------------|-----------------|
| Executive cards | `executive_kpi_cards` |
| Executive trends | `monthly_trends` |
| Credit | `credit_funnel_daily` |
| Conflict | `conflict_active_customers` + `conflict_approval_rate` |
| Dictionary | `kpi_dictionary` |
| Self-serve | `self_service_datasets` + `self_service_landing` |

---

## C) Build 5 dashboards (core)

### 1) Executive — KPI cards (10 min)

1. New Sheet → name `Exec Cards`  
2. Data: `executive_kpi_cards`  
3. Drag **market** to Filters → select **All**  
4. Drag **kpi_name** to Rows  
5. Drag **value** to Text → use **SUM** (or AVG if duplicates)  
6. Marks: change to **Shape** or keep **Text**/automatic bar — for big numbers: Marks → **Text**, put `value` on Text  
7. Format % KPIs: right-click value → Format → Percentage for rows where format=percent  
   - Faster: create two sheets — one for rates, one for amounts — or leave as numbers for now  

**Dashboard:** Dashboard → New Dashboard → name `01 Executive`  
- Drag title text: `Mal Enterprise BI — Executive (Certified KPIs) | Synthetic data`  
- Drag `Exec Cards`  
- Add 1–2 trend sheets from `monthly_trends` (month on Columns, measure on Rows):
  - `AVG(active_customers_certified)`  
  - `AVG(approval_rate_certified)` (format %)  
  - `SUM(revenue_finance_aed)`  
  - `AVG(portfolio_outstanding_aed)`  

You need **at least 8 KPIs** — the cards sheet already has them if all `kpi_id`s show.

---

### 2) Credit & Lending (8 min)

1. New data source / sheet using `credit_funnel_daily`  
2. Sheet `Credit Funnel`:
   - Create calculated fields (Analysis → Create Calculated Field):

```
Apps
SUM([credit_applications])
```

```
Approved
SUM([credit_approved_certified])
```

```
Booked
SUM([credit_booked])
```

   - Or put Measure Names / Measure Values with those three fields  
   - Filter **date** to the latest date (dropdown → Special → or sort and keep max)

3. Sheet `Credit Risk`:
   - Columns: `date`  
   - Rows: `AVG(fpd_rate)`, `AVG(dpd30_rate)` — format as %  
   - (If rates not in sheet, use: `SUM(fpd_amount_aed)/SUM(first_instalment_due_aed)`)

4. Dashboard `02 Credit` — funnel + risk + optional outstanding line

---

### 3) Metric Conflict (10 min) — important for scoring

1. Sheet using `conflict_active_customers`  
2. Columns: `definition_owner`  
3. Rows: `SUM(value)`  
4. Color: `status` → Edit colors: **certified = green**, **exploratory = orange**  
5. Label: show values  
6. Filter: `market` = UAE (or show filter)  

7. Second sheet: `conflict_approval_rate`  
   - Same layout; format value as %  

8. Dashboard `03 Conflict`  
   - Add **Text** object at top:

```
CERTIFIED Active Customers (KPI-P01):
Open product relationship (loan OR savings OR card) + KYC complete + not fraud-blocked.

Green = certified (use on Executive). Orange = exploratory (local analysis only).
```

---

### 4) KPI Dictionary (5 min)

1. Sheet from `kpi_dictionary`  
2. Put these on Rows as discrete (blue pills):  
   `kpi_id`, `name`, `domain_owner`, `business_definition`, `formula`, `data_source`, `refresh_cadence`, `status`  
3. Dashboard `04 Dictionary` — full table + filter on `status`

---

### 5) Self-Service Landing (5 min)

1. Sheet from `self_service_landing` — table of `section`, `detail`  
2. Sheet from `self_service_datasets` — table of dataset fields  
3. Dashboard `05 Self-Service` — both tables + title

---

## D) Publish (5 min)

1. **Server → Tableau Public → Save to Tableau Public…**  
   (In Tableau Public Desktop this may be **Save to Tableau Public** under the File/Server menu)  
2. Sign in  
3. Name: `Mal Enterprise BI Foundation`  
4. ☑ **Show sheets as tabs**  
5. Save  
6. Browser opens → copy the URL  

**Test:** open that URL in Chrome/Safari **Incognito** while logged out of Tableau.

Your URL should look like:

`https://public.tableau.com/app/profile/YOURNAME/viz/MalEnterpriseBIFoundation/01Executive`

**Do not** submit only: `https://public.tableau.com/app/discover`

---

## E) After you have the URL

1. Paste into the assessment form  
2. Paste here in chat → I will update GitHub README and push  

Also keep submitting GitHub: https://github.com/rahu-sachdeva/mal-enterprise-bi  

---

## Stuck? Common fixes

| Problem | Fix |
|---------|-----|
| No “Tableau Public” under Server | Install free Tableau Public Desktop; open File → Export Packaged Workbook from Desktop, open `.twbx` in Public, then publish |
| Wrong numbers / many nulls | Check you used the sheet names in the table above |
| Incognito asks for login | Workbook may be private — republish and ensure Public visibility |
| Too slow | Ship 5 dashboards with simple tables/bars first; polish later |

---

## Backup if Tableau blocks you tonight

The Streamlit app in the same GitHub repo already meets the Part 1 structure. You can deploy it on Streamlit Cloud from https://github.com/rahu-sachdeva/mal-enterprise-bi (`Home.py`) for a public URL while you finish Tableau.
