# Deploy the HTML dashboard (Apps Script) on your Google Sheet

**Sheet:** https://docs.google.com/spreadsheets/d/1GH7L9fBI-CXky-bi59BN7HglxCalYA7CgiFjTEyKcc8/edit

This serves Question 1 as a live HTML page with charts that **read and refresh from the Sheet tabs**.

---

## 1) Open Apps Script

1. Open the Sheet above  
2. **Extensions → Apps Script**  
3. Delete any default `Code.gs` content  

---

## 2) Add the two project files

### File A — `Code.gs`
1. In the left file list, open `Code.gs`  
2. Paste everything from [`Code.gs`](Code.gs) in this folder  
3. Save (disk icon)

### File B — `Index.html`
1. Left panel **+** → **HTML** → name it exactly `Index`  
2. Paste everything from [`Index.html`](Index.html)  
3. Save

---

## 3) Deploy as a Web App (public URL)

1. Top right: **Deploy → New deployment**  
2. Gear icon → type **Web app**  
3. Settings:
   - Description: `Mal Enterprise BI Foundation`
   - Execute as: **Me**
   - Who has access: **Anyone**  
4. **Deploy**  
5. Authorize the app when Google asks (choose your account → Advanced → Go to … → Allow)  
6. Copy the **Web app URL**  
   (`https://script.google.com/macros/s/.../exec`)

---

## 4) Test for the assessment

1. Open the Web app URL in an **incognito** window (logged out)  
2. Confirm pages load:
   - Self-Service  
   - Executive (8 KPI cards + charts)  
   - Credit & Lending (funnel + risk charts)  
   - Metric Conflict (green certified vs orange exploratory)  
   - KPI Dictionary  
3. Change **Market** filter and click **Refresh from Sheet**

---

## 5) What to submit

| Field | Value |
|-------|--------|
| Deployed BI Dashboard | **Web app URL** (`script.google.com/.../exec`) |
| GitHub | https://github.com/rahu-sachdeva/mal-enterprise-bi |
| Optional | Sheet URL (data source) |

Also set the Sheet itself to **Anyone with the link → Viewer** if reviewers need to inspect tabs.

---

## Updating charts after data changes

Edit any data tab in the Sheet (`executive_kpi_cards`, `monthly_trends`, etc.) → open the Web app → click **Refresh from Sheet**.  
No redeploy needed unless you change `Code.gs` / `Index.html`.

If you change script code later: **Deploy → Manage deployments → Edit → New version → Deploy**.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blank page / permission error | Redeploy with **Anyone**; re-authorize |
| “Sheet is null” | Confirm tab names match exactly (see list below) |
| Charts empty | Check `monthly_trends` / `executive_kpi_cards` have rows for market All/UAE/KSA |
| Incognito asks to sign in | Access must be **Anyone**, not “Anyone in organisation” |

### Required tab names

`executive_kpi_cards`, `monthly_trends`, `credit_funnel_daily`, `conflict_active_customers`, `conflict_approval_rate`, `kpi_dictionary`, `self_service_datasets`, `self_service_landing`
