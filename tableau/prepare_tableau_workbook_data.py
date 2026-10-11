"""Build a Tableau-friendly Excel workbook from synthetic CSVs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "Mal_Enterprise_BI_Tableau_Data.xlsx"


def main() -> None:
    daily = pd.read_csv(DATA / "daily_enterprise_kpis.csv", parse_dates=["date"])
    credit = pd.read_csv(DATA / "credit_funnel_daily.csv", parse_dates=["date"])
    conflict_a = pd.read_csv(DATA / "metric_conflict_active_customers.csv")
    conflict_r = pd.read_csv(DATA / "metric_conflict_approval_rate.csv")
    dictionary = pd.read_csv(DATA / "kpi_dictionary.csv")
    catalog = pd.read_csv(DATA / "self_service_datasets.csv")

    # Derived certified rates for Tableau (avoid messy calcs for reviewers)
    daily = daily.copy()
    daily["approval_rate_certified"] = (
        daily["credit_approved_certified"] / daily["credit_applications"]
    )
    daily["approval_rate_credit_local"] = (
        daily["credit_approved_credit_formula"] / daily["credit_applications"]
    )
    daily["booking_rate"] = daily["credit_booked"] / daily["credit_approved_certified"]
    daily["payment_success_rate"] = daily["payment_successful"] / daily["payment_attempts"]
    daily["fpd_rate"] = daily["fpd_amount_aed"] / daily["first_instalment_due_aed"]
    daily["dpd30_rate"] = (
        daily["dpd30_outstanding_aed"] / daily["portfolio_outstanding_aed"]
    )

    # Latest snapshot for KPI cards (one row per market + All)
    latest_date = daily["date"].max()
    latest = daily[daily["date"] == latest_date].copy()
    latest["as_of_date"] = latest_date.date().isoformat()

    all_row = {
        "date": latest_date,
        "market": "All",
        "as_of_date": latest_date.date().isoformat(),
        "credit_applications": latest["credit_applications"].sum(),
        "credit_approved_certified": latest["credit_approved_certified"].sum(),
        "credit_approved_credit_formula": latest["credit_approved_credit_formula"].sum(),
        "credit_booked": latest["credit_booked"].sum(),
        "disbursed_amount_aed": latest["disbursed_amount_aed"].sum(),
        "portfolio_outstanding_aed": latest["portfolio_outstanding_aed"].sum(),
        "fpd_amount_aed": latest["fpd_amount_aed"].sum(),
        "first_instalment_due_aed": latest["first_instalment_due_aed"].sum(),
        "dpd30_outstanding_aed": latest["dpd30_outstanding_aed"].sum(),
        "payment_attempts": latest["payment_attempts"].sum(),
        "payment_successful": latest["payment_successful"].sum(),
        "savings_new_accounts": latest["savings_new_accounts"].sum(),
        "savings_aum_aed": latest["savings_aum_aed"].sum(),
        "revenue_finance_aed": latest["revenue_finance_aed"].sum(),
        "revenue_product_aed": latest["revenue_product_aed"].sum(),
        "active_customers_product_30d_login": latest[
            "active_customers_product_30d_login"
        ].sum(),
        "active_customers_finance_90d_txn": latest[
            "active_customers_finance_90d_txn"
        ].sum(),
        "active_customers_credit_open_loan": latest[
            "active_customers_credit_open_loan"
        ].sum(),
        "active_customers_certified": latest["active_customers_certified"].sum(),
    }
    all_row["approval_rate_certified"] = (
        all_row["credit_approved_certified"] / all_row["credit_applications"]
    )
    all_row["approval_rate_credit_local"] = (
        all_row["credit_approved_credit_formula"] / all_row["credit_applications"]
    )
    all_row["booking_rate"] = (
        all_row["credit_booked"] / all_row["credit_approved_certified"]
    )
    all_row["payment_success_rate"] = (
        all_row["payment_successful"] / all_row["payment_attempts"]
    )
    all_row["fpd_rate"] = all_row["fpd_amount_aed"] / all_row["first_instalment_due_aed"]
    all_row["dpd30_rate"] = (
        all_row["dpd30_outstanding_aed"] / all_row["portfolio_outstanding_aed"]
    )
    exec_latest = pd.concat([latest, pd.DataFrame([all_row])], ignore_index=True)

    # Long format for executive KPI cards (easier Tableau)
    card_map = [
        ("KPI-P01", "Active Customers (Certified)", "active_customers_certified", "number"),
        ("KPI-C02", "Approval Rate (Certified)", "approval_rate_certified", "percent"),
        ("KPI-C04", "Booking Rate", "booking_rate", "percent"),
        ("KPI-C06", "Portfolio Outstanding (AED)", "portfolio_outstanding_aed", "currency"),
        ("KPI-F01", "Recognised Revenue (AED)", "revenue_finance_aed", "currency"),
        ("KPI-F03", "Savings AUM (AED)", "savings_aum_aed", "currency"),
        ("KPI-Pay01", "Payment Success Rate", "payment_success_rate", "percent"),
        ("KPI-C08", "DPD30 Rate", "dpd30_rate", "percent"),
    ]
    card_rows = []
    for _, r in exec_latest.iterrows():
        for kpi_id, name, col, fmt in card_map:
            card_rows.append(
                {
                    "as_of_date": r["as_of_date"],
                    "market": r["market"],
                    "kpi_id": kpi_id,
                    "kpi_name": name,
                    "value": r[col],
                    "format": fmt,
                    "status": "certified",
                    "domain": (
                        "Product"
                        if kpi_id.startswith("KPI-P")
                        else "Credit"
                        if kpi_id.startswith("KPI-C")
                        else "Finance"
                        if kpi_id.startswith("KPI-F")
                        else "Payments"
                    ),
                }
            )
    exec_cards = pd.DataFrame(card_rows)

    # Monthly trend (cleaner lines)
    daily["month"] = daily["date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        daily.groupby(["month", "market"], as_index=False)
        .agg(
            active_customers_certified=("active_customers_certified", "mean"),
            portfolio_outstanding_aed=("portfolio_outstanding_aed", "mean"),
            revenue_finance_aed=("revenue_finance_aed", "sum"),
            credit_applications=("credit_applications", "sum"),
            credit_approved_certified=("credit_approved_certified", "sum"),
            credit_booked=("credit_booked", "sum"),
            payment_successful=("payment_successful", "sum"),
            payment_attempts=("payment_attempts", "sum"),
            fpd_amount_aed=("fpd_amount_aed", "sum"),
            first_instalment_due_aed=("first_instalment_due_aed", "sum"),
            dpd30_outstanding_aed=("dpd30_outstanding_aed", "mean"),
        )
    )
    monthly["approval_rate_certified"] = (
        monthly["credit_approved_certified"] / monthly["credit_applications"]
    )
    monthly["booking_rate"] = (
        monthly["credit_booked"] / monthly["credit_approved_certified"]
    )
    monthly["payment_success_rate"] = (
        monthly["payment_successful"] / monthly["payment_attempts"]
    )
    monthly["fpd_rate"] = monthly["fpd_amount_aed"] / monthly["first_instalment_due_aed"]
    monthly["dpd30_rate"] = (
        monthly["dpd30_outstanding_aed"] / monthly["portfolio_outstanding_aed"]
    )

    # Landing page copy as a tiny table for Tableau text/dashboard
    landing = pd.DataFrame(
        [
            {
                "section": "How to request access",
                "detail": (
                    "Post in #bi-access (or email bi-platform@mal.bank) with dataset name, "
                    "use case, manager, and PII need (Y/N)."
                ),
            },
            {
                "section": "Access SLA",
                "detail": "L1/L2 access within 2 business days. P1 certified break: under 4 business hours.",
            },
            {
                "section": "Certified rule",
                "detail": (
                    "Certified datasets only for Executive, OKRs, and board packs. "
                    "Exploratory metrics are for local analysis and the Conflict view."
                ),
            },
            {
                "section": "KPI change control",
                "detail": (
                    "Certified metrics change only via KPI Change Request "
                    "(domain owner + BI + Finance for money metrics). Head of Data breaks ties."
                ),
            },
        ]
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT, engine="openpyxl") as xl:
        daily.to_excel(xl, sheet_name="daily_enterprise_kpis", index=False)
        monthly.to_excel(xl, sheet_name="monthly_trends", index=False)
        exec_cards.to_excel(xl, sheet_name="executive_kpi_cards", index=False)
        exec_latest.to_excel(xl, sheet_name="executive_latest", index=False)
        credit.to_excel(xl, sheet_name="credit_funnel_daily", index=False)
        conflict_a.to_excel(xl, sheet_name="conflict_active_customers", index=False)
        conflict_r.to_excel(xl, sheet_name="conflict_approval_rate", index=False)
        dictionary.to_excel(xl, sheet_name="kpi_dictionary", index=False)
        catalog.to_excel(xl, sheet_name="self_service_datasets", index=False)
        landing.to_excel(xl, sheet_name="self_service_landing", index=False)

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
