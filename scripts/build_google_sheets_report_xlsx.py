"""Build a full Mal BI report workbook with charts for Google Sheets import."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "looker_studio" / "Mal_Enterprise_BI_Full_Report.xlsx"
DOWNLOADS = Path("/Users/rahul.sachdeva/Downloads/Mal_Enterprise_BI_Full_Report.xlsx")

HEADER = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE = Font(bold=True, size=16, color="1F4E79")
SUB = Font(size=10, color="44546A")
KPI_FILL = PatternFill("solid", fgColor="D6EAF8")
CERT_FILL = PatternFill("solid", fgColor="C6EFCE")
EXP_FILL = PatternFill("solid", fgColor="FCE4D6")
SECTION = Font(bold=True, size=12, color="1F4E79")
THIN = Border(
    left=Side(style="thin", color="B0B0B0"),
    right=Side(style="thin", color="B0B0B0"),
    top=Side(style="thin", color="B0B0B0"),
    bottom=Side(style="thin", color="B0B0B0"),
)


def style_header_row(ws, row=1, cols=10):
    for c in range(1, cols + 1):
        cell = ws.cell(row, c)
        cell.fill = HEADER
        cell.font = HEADER_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def autosize(ws, max_width=42):
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        length = 0
        for cell in col:
            if cell.value is not None:
                length = max(length, min(len(str(cell.value)), max_width))
        ws.column_dimensions[letter].width = max(12, length + 2)


def write_df(ws, df, start_row=1, start_col=1):
    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=start_row):
        for c_idx, val in enumerate(row, start=start_col):
            cell = ws.cell(r_idx, c_idx, val)
            cell.border = THIN
            if r_idx == start_row:
                cell.fill = HEADER
                cell.font = HEADER_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="center")
    return start_row + len(df)


def main():
    daily = pd.read_csv(DATA / "daily_enterprise_kpis.csv", parse_dates=["date"])
    credit = pd.read_csv(DATA / "credit_funnel_daily.csv", parse_dates=["date"])
    conflict_a = pd.read_csv(DATA / "metric_conflict_active_customers.csv")
    conflict_r = pd.read_csv(DATA / "metric_conflict_approval_rate.csv")
    dictionary = pd.read_csv(DATA / "kpi_dictionary.csv")
    catalog = pd.read_csv(DATA / "self_service_datasets.csv")

    daily["approval_rate_certified"] = (
        daily["credit_approved_certified"] / daily["credit_applications"]
    )
    daily["booking_rate"] = daily["credit_booked"] / daily["credit_approved_certified"]
    daily["payment_success_rate"] = daily["payment_successful"] / daily["payment_attempts"]
    daily["fpd_rate"] = daily["fpd_amount_aed"] / daily["first_instalment_due_aed"]
    daily["dpd30_rate"] = (
        daily["dpd30_outstanding_aed"] / daily["portfolio_outstanding_aed"]
    )
    daily["month"] = daily["date"].dt.to_period("M").dt.to_timestamp()

    latest_date = daily["date"].max()
    latest = daily[daily["date"] == latest_date]
    latest_all = {
        "as_of": latest_date.date().isoformat(),
        "market": "All (UAE+KSA)",
        "active_customers_certified": int(latest["active_customers_certified"].sum()),
        "approval_rate_certified": float(
            latest["credit_approved_certified"].sum() / latest["credit_applications"].sum()
        ),
        "booking_rate": float(
            latest["credit_booked"].sum() / latest["credit_approved_certified"].sum()
        ),
        "portfolio_outstanding_aed": float(latest["portfolio_outstanding_aed"].sum()),
        "revenue_finance_aed": float(latest["revenue_finance_aed"].sum()),
        "savings_aum_aed": float(latest["savings_aum_aed"].sum()),
        "payment_success_rate": float(
            latest["payment_successful"].sum() / latest["payment_attempts"].sum()
        ),
        "dpd30_rate": float(
            latest["dpd30_outstanding_aed"].sum() / latest["portfolio_outstanding_aed"].sum()
        ),
        "apps": int(latest["credit_applications"].sum()),
        "approved": int(latest["credit_approved_certified"].sum()),
        "booked": int(latest["credit_booked"].sum()),
        "fpd_rate": float(
            latest["fpd_amount_aed"].sum() / latest["first_instalment_due_aed"].sum()
        ),
    }

    monthly = (
        daily.groupby("month", as_index=False)
        .agg(
            active_customers_certified=("active_customers_certified", "mean"),
            portfolio_outstanding_aed=("portfolio_outstanding_aed", "mean"),
            revenue_finance_aed=("revenue_finance_aed", "sum"),
            approval_rate_certified=("approval_rate_certified", "mean"),
            booking_rate=("booking_rate", "mean"),
            fpd_rate=("fpd_rate", "mean"),
            dpd30_rate=("dpd30_rate", "mean"),
            credit_applications=("credit_applications", "sum"),
            credit_approved_certified=("credit_approved_certified", "sum"),
            credit_booked=("credit_booked", "sum"),
        )
    )
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")

    # Latest credit day for funnel
    credit_latest = credit[credit["date"] == credit["date"].max()]
    funnel = pd.DataFrame(
        {
            "stage": ["Applications", "Approved (Certified)", "Booked / Disbursed"],
            "count": [
                int(credit_latest["credit_applications"].sum()),
                int(credit_latest["credit_approved_certified"].sum()),
                int(credit_latest["credit_booked"].sum()),
            ],
        }
    )

    wb = Workbook()

    # ---------- 00 Self Service ----------
    ws = wb.active
    ws.title = "00_Self_Service_Landing"
    ws["A1"] = "Mal Enterprise BI Foundation — Self-Service Landing"
    ws["A1"].font = TITLE
    ws.merge_cells("A1:F1")
    ws["A2"] = (
        "Synthetic data only · Sole BI hire prototype · Credit · Payments · Savings launch · "
        f"As of {latest_all['as_of']}"
    )
    ws["A2"].font = SUB
    ws.merge_cells("A2:F2")

    ws["A4"] = "How to use this workbook"
    ws["A4"].font = SECTION
    bullets = [
        "01_Executive_Dashboard — certified enterprise KPIs for leadership (8+ metrics + charts)",
        "02_Credit_Lending — approval funnel, portfolio quality, FPD & DPD30 risk charts",
        "03_Metric_Conflict — Active Customers & Approval Rate defined 3 ways + CERTIFIED marked",
        "04_KPI_Dictionary — 20 metrics with owner, definition, formula, source, cadence, status",
        "Data_* tabs — source marts (do not use exploratory metrics on executive packs)",
    ]
    for i, b in enumerate(bullets, start=5):
        ws[f"A{i}"] = f"• {b}"

    ws["A11"] = "Access request process"
    ws["A11"].font = SECTION
    ws["A12"] = (
        "Post in #bi-access (or email bi-platform@mal.bank) with: dataset name, use case, "
        "manager, PII need (Y/N). L1/L2 access within 2 business days."
    )
    ws.merge_cells("A12:F12")
    ws["A13"] = "SLA"
    ws["A13"].font = SECTION
    ws["A14"] = (
        "P1 (certified KPI wrong / dashboard down): under 4 business hours. "
        "New certified metric workshop: within 5 business days."
    )
    ws.merge_cells("A14:F14")
    ws["A15"] = "Certified vs exploratory"
    ws["A15"].font = SECTION
    ws["A16"] = (
        "Certified = Executive / OKR / board only. Exploratory = local analysis + Conflict tab. "
        "Head of Data is final decision-maker on certified definitions."
    )
    ws.merge_cells("A16:F16")

    ws["A18"] = "Certified & exploratory datasets"
    ws["A18"].font = SECTION
    write_df(ws, catalog, start_row=19)
    autosize(ws)

    # ---------- 01 Executive ----------
    ws = wb.create_sheet("01_Executive_Dashboard")
    ws["A1"] = "Mal Enterprise BI — Executive Dashboard (Certified KPIs only)"
    ws["A1"].font = TITLE
    ws.merge_cells("A1:H1")
    ws["A2"] = (
        f"As of {latest_all['as_of']} · Market: {latest_all['market']} · "
        "Synthetic data · No exploratory metrics on this page"
    )
    ws["A2"].font = SUB
    ws.merge_cells("A2:H2")

    kpis = [
        ("KPI-P01 Active Customers (Certified)", latest_all["active_customers_certified"], "#,##0"),
        ("KPI-C02 Approval Rate (Certified)", latest_all["approval_rate_certified"], "0.0%"),
        ("KPI-C04 Booking Rate", latest_all["booking_rate"], "0.0%"),
        ("KPI-C06 Portfolio Outstanding (AED)", latest_all["portfolio_outstanding_aed"], "#,##0"),
        ("KPI-F01 Recognised Revenue (AED)", latest_all["revenue_finance_aed"], "#,##0"),
        ("KPI-F03 Savings AUM (AED)", latest_all["savings_aum_aed"], "#,##0"),
        ("KPI-Pay01 Payment Success Rate", latest_all["payment_success_rate"], "0.0%"),
        ("KPI-C08 DPD30 Rate", latest_all["dpd30_rate"], "0.0%"),
    ]
    ws["A4"] = "Enterprise KPI cards"
    ws["A4"].font = SECTION
    for i, (name, val, fmt) in enumerate(kpis):
        col = i + 1
        ws.cell(5, col, name).fill = KPI_FILL
        ws.cell(5, col).font = Font(bold=True, size=9)
        ws.cell(5, col).alignment = Alignment(wrap_text=True, horizontal="center")
        ws.cell(5, col).border = THIN
        cell = ws.cell(6, col, val)
        cell.number_format = fmt
        cell.font = Font(bold=True, size=14, color="1F4E79")
        cell.alignment = Alignment(horizontal="center")
        cell.fill = PatternFill("solid", fgColor="FFFFFF")
        cell.border = THIN
        ws.column_dimensions[get_column_letter(col)].width = 18

    # Monthly trend data starting row 9
    ws["A8"] = "Monthly trends (source for charts below)"
    ws["A8"].font = SECTION
    trend_cols = [
        "month",
        "active_customers_certified",
        "approval_rate_certified",
        "portfolio_outstanding_aed",
        "revenue_finance_aed",
    ]
    write_df(ws, monthly[trend_cols], start_row=9)
    n = len(monthly)

    # Chart 1 - Active customers
    c1 = LineChart()
    c1.title = "Active Customers (Certified) — KPI-P01"
    c1.style = 10
    c1.y_axis.title = "Customers"
    c1.x_axis.title = "Month"
    c1.height = 8
    c1.width = 15
    data = Reference(ws, min_col=2, min_row=9, max_row=9 + n, max_col=2)
    cats = Reference(ws, min_col=1, min_row=10, max_row=9 + n)
    c1.add_data(data, titles_from_data=True)
    c1.set_categories(cats)
    ws.add_chart(c1, "A20")

    # Chart 2 - Approval
    c2 = LineChart()
    c2.title = "Approval Rate (Certified) — KPI-C02"
    c2.style = 12
    c2.y_axis.title = "Rate"
    c2.height = 8
    c2.width = 15
    data = Reference(ws, min_col=3, min_row=9, max_row=9 + n, max_col=3)
    c2.add_data(data, titles_from_data=True)
    c2.set_categories(cats)
    ws.add_chart(c2, "E20")

    # Chart 3 - Outstanding
    c3 = LineChart()
    c3.title = "Portfolio Outstanding (AED) — KPI-C06"
    c3.style = 11
    c3.height = 8
    c3.width = 15
    data = Reference(ws, min_col=4, min_row=9, max_row=9 + n, max_col=4)
    c3.add_data(data, titles_from_data=True)
    c3.set_categories(cats)
    ws.add_chart(c3, "A36")

    # Chart 4 - Revenue
    c4 = LineChart()
    c4.title = "Recognised Revenue (AED) — KPI-F01"
    c4.style = 13
    c4.height = 8
    c4.width = 15
    data = Reference(ws, min_col=5, min_row=9, max_row=9 + n, max_col=5)
    c4.add_data(data, titles_from_data=True)
    c4.set_categories(cats)
    ws.add_chart(c4, "E36")

    ws["A52"] = (
        "Decision note: Executive pack uses certified dictionary IDs only. "
        "Active Customers and Approval Rate conflicts are resolved on tab 03_Metric_Conflict."
    )
    ws["A52"].font = SUB
    ws.merge_cells("A52:H52")

    # ---------- 02 Credit ----------
    ws = wb.create_sheet("02_Credit_Lending")
    ws["A1"] = "Credit & Lending Domain Dashboard"
    ws["A1"].font = TITLE
    ws.merge_cells("A1:F1")
    ws["A2"] = (
        f"As of {latest_all['as_of']} · Certified approval rate (KPI-C02) · "
        f"FPD {latest_all['fpd_rate']:.1%} · DPD30 {latest_all['dpd30_rate']:.1%}"
    )
    ws["A2"].font = SUB

    ws["A4"] = "Approval funnel (latest day)"
    ws["A4"].font = SECTION
    write_df(ws, funnel, start_row=5)

    chart = BarChart()
    chart.type = "bar"
    chart.title = "Credit approval funnel"
    chart.style = 10
    chart.y_axis.title = None
    chart.x_axis.title = "Count"
    chart.height = 8
    chart.width = 14
    data = Reference(ws, min_col=2, min_row=5, max_row=8)
    cats = Reference(ws, min_col=1, min_row=6, max_row=8)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.shape = 4
    ws.add_chart(chart, "D4")

    ws["A12"] = "KPI snapshot"
    ws["A12"].font = SECTION
    snap = pd.DataFrame(
        [
            ["Applications (KPI-C01)", latest_all["apps"]],
            ["Approved certified", latest_all["approved"]],
            ["Booked", latest_all["booked"]],
            ["Approval rate certified", latest_all["approval_rate_certified"]],
            ["Booking rate", latest_all["booking_rate"]],
            ["FPD rate (KPI-C07)", latest_all["fpd_rate"]],
            ["DPD30 rate (KPI-C08)", latest_all["dpd30_rate"]],
            ["Outstanding AED (KPI-C06)", latest_all["portfolio_outstanding_aed"]],
        ],
        columns=["metric", "value"],
    )
    write_df(ws, snap, start_row=13)
    ws["B17"].number_format = "0.0%"
    ws["B18"].number_format = "0.0%"
    ws["B19"].number_format = "0.0%"
    ws["B20"].number_format = "0.0%"
    ws["B21"].number_format = "#,##0"

    # Risk trend data
    ws["A24"] = "Monthly risk & funnel rates (chart source)"
    ws["A24"].font = SECTION
    risk = monthly[
        [
            "month",
            "approval_rate_certified",
            "booking_rate",
            "fpd_rate",
            "dpd30_rate",
            "portfolio_outstanding_aed",
        ]
    ]
    write_df(ws, risk, start_row=25)
    rn = len(risk)
    cats = Reference(ws, min_col=1, min_row=26, max_row=25 + rn)

    rc = LineChart()
    rc.title = "Approval & booking rates"
    rc.style = 10
    rc.height = 8
    rc.width = 14
    data = Reference(ws, min_col=2, min_row=25, max_row=25 + rn, max_col=3)
    rc.add_data(data, titles_from_data=True)
    rc.set_categories(cats)
    ws.add_chart(rc, "H24")

    rc2 = LineChart()
    rc2.title = "Risk indicators — FPD & DPD30"
    rc2.style = 12
    rc2.height = 8
    rc2.width = 14
    data = Reference(ws, min_col=4, min_row=25, max_row=25 + rn, max_col=5)
    rc2.add_data(data, titles_from_data=True)
    rc2.set_categories(cats)
    ws.add_chart(rc2, "H40")

    rc3 = LineChart()
    rc3.title = "Portfolio outstanding (AED)"
    rc3.style = 11
    rc3.height = 8
    rc3.width = 14
    data = Reference(ws, min_col=6, min_row=25, max_row=25 + rn, max_col=6)
    rc3.add_data(data, titles_from_data=True)
    rc3.set_categories(cats)
    ws.add_chart(rc3, "A40")

    ws["A56"] = (
        "Note: Credit soft-approval is exploratory only — see 03_Metric_Conflict. "
        "This dashboard uses certified final approval after KYC."
    )
    ws["A56"].font = SUB
    autosize(ws)

    # ---------- 03 Conflict ----------
    ws = wb.create_sheet("03_Metric_Conflict")
    ws["A1"] = "Metric Conflict Resolution"
    ws["A1"].font = TITLE
    ws.merge_cells("A1:G1")
    ws["A2"] = (
        "Same metric, multiple domain definitions — CERTIFIED definition is the only enterprise number"
    )
    ws["A2"].font = SUB

    ws["A4"] = "CERTIFIED Active Customers (KPI-P01)"
    ws["A4"].font = SECTION
    ws["A4"].fill = CERT_FILL
    ws["A5"] = (
        "Count distinct customers with ≥1 open product relationship "
        "(active loan on CBS OR open savings OR active card) AND KYC complete AND not fraud-blocked. "
        "Head of Data owns final certified decision; BI documents and enforces."
    )
    ws.merge_cells("A5:G5")
    ws["A5"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[5].height = 45

    # Aggregate conflict across markets for cleaner chart (or show UAE)
    conf = conflict_a[conflict_a["market"] == "UAE"].copy()
    if conf.empty:
        conf = conflict_a.copy()
    conf_view = conf[
        ["definition_owner", "definition_label", "status", "value", "formula", "why_it_diverges"]
    ]
    ws["A7"] = "Active Customers — UAE snapshot"
    ws["A7"].font = SECTION
    write_df(ws, conf_view, start_row=8)

    for r in range(9, 9 + len(conf_view)):
        status = ws.cell(r, 3).value
        fill = CERT_FILL if status == "certified" else EXP_FILL
        for c in range(1, 7):
            ws.cell(r, c).fill = fill

    bar = BarChart()
    bar.type = "col"
    bar.title = "Active Customers by definition (UAE)"
    bar.style = 10
    bar.height = 9
    bar.width = 14
    data = Reference(ws, min_col=4, min_row=8, max_row=8 + len(conf_view))
    cats = Reference(ws, min_col=1, min_row=9, max_row=8 + len(conf_view))
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.dataLabels = DataLabelList()
    bar.dataLabels.showVal = True
    ws.add_chart(bar, "A15")

    # Approval conflict
    apr = conflict_r[conflict_r["market"] == "UAE"].copy()
    if apr.empty:
        apr = conflict_r.copy()
    apr_view = apr[
        ["definition_owner", "definition_label", "status", "value", "formula", "why_it_diverges"]
    ]
    ws["A32"] = "Credit Approval Rate — UAE snapshot"
    ws["A32"].font = SECTION
    write_df(ws, apr_view, start_row=33)
    for r in range(34, 34 + len(apr_view)):
        status = ws.cell(r, 3).value
        fill = CERT_FILL if status == "certified" else EXP_FILL
        for c in range(1, 7):
            ws.cell(r, c).fill = fill
        ws.cell(r, 4).number_format = "0.0%"

    bar2 = BarChart()
    bar2.type = "col"
    bar2.title = "Approval Rate by definition (UAE)"
    bar2.style = 12
    bar2.height = 9
    bar2.width = 14
    data = Reference(ws, min_col=4, min_row=33, max_row=33 + len(apr_view))
    cats = Reference(ws, min_col=1, min_row=34, max_row=33 + len(apr_view))
    bar2.add_data(data, titles_from_data=True)
    bar2.set_categories(cats)
    bar2.dataLabels = DataLabelList()
    bar2.dataLabels.showVal = True
    ws.add_chart(bar2, "A38")

    ws["A50"] = "How to read this page"
    ws["A50"].font = SECTION
    ws["A51"] = (
        "Green rows = CERTIFIED (allowed on Executive / board). "
        "Orange rows = exploratory (Product 30d login / Finance 90d txn / Credit open loan / Credit soft-approve). "
        "Gap between bars = governance risk if left unresolved."
    )
    ws.merge_cells("A51:G51")
    autosize(ws)

    # ---------- 04 Dictionary ----------
    ws = wb.create_sheet("04_KPI_Dictionary")
    ws["A1"] = "Enterprise KPI Dictionary"
    ws["A1"].font = TITLE
    ws["A2"] = (
        "20 metrics · name · domain owner · business definition · formula · data source · "
        "refresh cadence · certified vs exploratory"
    )
    ws["A2"].font = SUB
    write_df(ws, dictionary, start_row=4)
    for r in range(5, 5 + len(dictionary)):
        if ws.cell(r, 8).value == "certified":
            ws.cell(r, 8).fill = CERT_FILL
        else:
            ws.cell(r, 8).fill = EXP_FILL
    autosize(ws, max_width=48)
    ws.row_dimensions[4].height = 30

    # ---------- Data tabs ----------
    for name, df in [
        ("Data_daily_kpis", daily.assign(date=daily["date"].dt.strftime("%Y-%m-%d"))),
        ("Data_credit_funnel", credit.assign(date=credit["date"].dt.strftime("%Y-%m-%d"))),
        ("Data_conflict_active", conflict_a),
        ("Data_conflict_approval", conflict_r),
        ("Data_monthly_trends", monthly),
    ]:
        ws = wb.create_sheet(name)
        # limit daily size for Sheets comfort - full data still useful
        write_df(ws, df)
        autosize(ws, max_width=28)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    wb.save(DOWNLOADS)
    print(f"Wrote {OUT}")
    print(f"Wrote {DOWNLOADS}")


if __name__ == "__main__":
    main()
