# Looker Studio — do this now (fastest public URL)

Home: https://datastudio.google.com/navigation/reporting  
(same product as Looker Studio)

---

## Step 1 — Put data in Google Sheets (5 min)

### Option A (easiest)

1. Go to https://sheets.google.com → **Blank spreadsheet**  
2. Name it: `Mal Enterprise BI Foundation - Data`  
3. **File → Import → Upload**  
4. Upload from your Mac:  
   `/Users/rahul.sachdeva/Downloads/Mal_Enterprise_BI_LookerStudio_Data.xlsx`  
5. Import location: **Create new spreadsheet** or replace — choose **Replace spreadsheet** if blank  
6. You should see multiple tabs (executive_kpi_cards, monthly_trends, etc.)

If Excel import only loads one tab: import each CSV from the GitHub folder  
`looker_studio/data/*.csv` as a separate sheet (File → Import → Upload → insert new sheet).

### Share the Sheet

**Share → General access → Anyone with the link → Viewer → Copy link**

---

## Step 2 — Create the report (2 min)

1. Open https://datastudio.google.com/navigation/reporting  
2. **Create → Report**  
3. Connect **Google Sheets** → your Mal spreadsheet → tab `executive_kpi_cards` → **Add**  
4. **Add to report**

---

## Step 3 — Build 5 pages (follow LOOKER_STUDIO_BUILD.md)

Minimum pages:

1. **01 Executive** — 8 scorecards from `executive_kpi_cards` + trends from `monthly_trends`  
2. **02 Credit** — funnel + FPD/DPD30 from `credit_funnel_daily`  
3. **03 Conflict** — bars from `conflict_active_customers` (+ approval sheet)  
4. **04 Dictionary** — table from `kpi_dictionary`  
5. **05 Self-Service** — tables from `self_service_landing` + `self_service_datasets`

Full click steps: `LOOKER_STUDIO_BUILD.md`

---

## Step 4 — Public link (critical)

1. Report → **Share**  
2. **Anyone with the link can View**  
3. Copy report URL (`https://lookerstudio.google.com/reporting/...`)  
4. Test in **incognito** (logged out)  
5. Paste into assessment form + send URL here for README update  

**Do not submit** only https://datastudio.google.com/navigation/reporting — that is the home page.

---

## Step 5 — GitHub (already done)

https://github.com/rahu-sachdeva/mal-enterprise-bi
