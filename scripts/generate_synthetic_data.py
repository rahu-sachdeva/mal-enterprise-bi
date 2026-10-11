"""Generate synthetic Mal bank KPI datasets for the BI prototype. Local only."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RNG = np.random.default_rng(42)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2025-07-01", "2026-03-31", freq="D")
    n = len(dates)
    markets = ["UAE", "KSA"]

    rows = []
    for market in markets:
        base_apps = 420 if market == "UAE" else 380
        for i, d in enumerate(dates):
            season = 1 + 0.08 * np.sin(i / 18)
            noise = RNG.normal(1, 0.04)
            apps = max(80, int(base_apps * season * noise))
            # Credit's local formula tends to be looser (higher approval)
            credit_approved = int(apps * (0.62 + RNG.normal(0, 0.02)))
            # Certified uses stricter underwriting + KYC complete
            certified_approved = int(apps * (0.54 + RNG.normal(0, 0.015)))
            booked = int(certified_approved * (0.78 + RNG.normal(0, 0.03)))
            disbursed_aed = booked * (1850 + RNG.normal(0, 120))
            outstanding = 12_500_000 + i * (42_000 if market == "UAE" else 36_000) + RNG.normal(0, 80_000)
            fpd_amt = disbursed_aed * (0.028 + abs(RNG.normal(0, 0.004)))
            due_amt = disbursed_aed * 0.22
            dpd30_outstanding = outstanding * (0.035 + abs(RNG.normal(0, 0.004)))
            payment_attempts = int(booked * 1.4 + RNG.integers(50, 120))
            payment_success = int(payment_attempts * (0.91 + RNG.normal(0, 0.015)))
            savings_new = int(35 + i * 0.05 + RNG.integers(0, 15))
            savings_aum = 4_200_000 + i * 18_000 + RNG.normal(0, 40_000)
            # Revenue definitions diverge
            finance_revenue = booked * 42 + savings_new * 8 + payment_success * 0.35
            product_revenue = booked * 55 + savings_new * 12  # includes deferred / projected
            # Active customers — three conflicting definitions
            product_active = int(18_000 + i * 22 + RNG.integers(-40, 60))  # 30d app login
            finance_active = int(14_200 + i * 15 + RNG.integers(-30, 40))  # 90d revenue txn
            credit_active = int(9_800 + i * 11 + RNG.integers(-20, 30))  # open loan on CBS
            # Certified: open product relationship (loan OR savings) AND not closed/fraud
            certified_active = int(max(credit_active, finance_active * 0.92) + savings_new * 40)

            rows.append(
                {
                    "date": d.date().isoformat(),
                    "market": market,
                    "credit_applications": apps,
                    "credit_approved_credit_formula": credit_approved,
                    "credit_approved_certified": certified_approved,
                    "credit_booked": booked,
                    "disbursed_amount_aed": round(disbursed_aed, 2),
                    "portfolio_outstanding_aed": round(max(outstanding, 0), 2),
                    "fpd_amount_aed": round(fpd_amt, 2),
                    "first_instalment_due_aed": round(due_amt, 2),
                    "dpd30_outstanding_aed": round(max(dpd30_outstanding, 0), 2),
                    "payment_attempts": payment_attempts,
                    "payment_successful": max(0, payment_success),
                    "savings_new_accounts": savings_new,
                    "savings_aum_aed": round(max(savings_aum, 0), 2),
                    "revenue_finance_aed": round(finance_revenue, 2),
                    "revenue_product_aed": round(product_revenue, 2),
                    "active_customers_product_30d_login": product_active,
                    "active_customers_finance_90d_txn": finance_active,
                    "active_customers_credit_open_loan": credit_active,
                    "active_customers_certified": certified_active,
                }
            )

    daily = pd.DataFrame(rows)
    daily.to_csv(DATA / "daily_enterprise_kpis.csv", index=False)

    # Funnel grain for Credit domain dashboard
    funnel = daily[
        [
            "date",
            "market",
            "credit_applications",
            "credit_approved_certified",
            "credit_booked",
            "disbursed_amount_aed",
            "portfolio_outstanding_aed",
            "fpd_amount_aed",
            "first_instalment_due_aed",
            "dpd30_outstanding_aed",
        ]
    ].copy()
    funnel["approval_rate_certified"] = (
        funnel["credit_approved_certified"] / funnel["credit_applications"]
    )
    funnel["booking_rate"] = funnel["credit_booked"] / funnel["credit_approved_certified"]
    funnel["fpd_rate"] = funnel["fpd_amount_aed"] / funnel["first_instalment_due_aed"]
    funnel["dpd30_rate"] = (
        funnel["dpd30_outstanding_aed"] / funnel["portfolio_outstanding_aed"]
    )
    funnel.to_csv(DATA / "credit_funnel_daily.csv", index=False)

    # Latest snapshot for conflict view
    latest = daily.sort_values("date").groupby("market").tail(1)
    conflict_rows = []
    for _, r in latest.iterrows():
        conflict_rows.extend(
            [
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Active Customers",
                    "definition_owner": "Product",
                    "definition_label": "Exploratory — Product",
                    "status": "exploratory",
                    "value": int(r["active_customers_product_30d_login"]),
                    "formula": "COUNT DISTINCT customers with app login in last 30 days",
                    "why_it_diverges": "Includes browsers who never open a financial product",
                },
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Active Customers",
                    "definition_owner": "Finance",
                    "definition_label": "Exploratory — Finance",
                    "status": "exploratory",
                    "value": int(r["active_customers_finance_90d_txn"]),
                    "formula": "COUNT DISTINCT customers with a revenue-recognised transaction in last 90 days",
                    "why_it_diverges": "Excludes dormant savers and newly approved not-yet-booked borrowers",
                },
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Active Customers",
                    "definition_owner": "Credit",
                    "definition_label": "Exploratory — Credit",
                    "status": "exploratory",
                    "value": int(r["active_customers_credit_open_loan"]),
                    "formula": "COUNT DISTINCT customers with open loan status on CBS (active book)",
                    "why_it_diverges": "Ignores savings-only and payments-only customers",
                },
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Active Customers",
                    "definition_owner": "BI (Certified)",
                    "definition_label": "CERTIFIED — Enterprise",
                    "status": "certified",
                    "value": int(r["active_customers_certified"]),
                    "formula": (
                        "COUNT DISTINCT customers with at least one open product relationship "
                        "(active loan on CBS OR open savings account OR active card) "
                        "AND KYC complete AND not fraud-blocked"
                    ),
                    "why_it_diverges": "Reconciled enterprise definition for all executive reporting",
                },
            ]
        )
    pd.DataFrame(conflict_rows).to_csv(DATA / "metric_conflict_active_customers.csv", index=False)

    # Approval rate conflict (Credit vs Certified)
    approval_conflict = []
    for _, r in latest.iterrows():
        approval_conflict.extend(
            [
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Credit Approval Rate",
                    "definition_owner": "Credit",
                    "definition_label": "Exploratory — Credit",
                    "status": "exploratory",
                    "value": round(
                        r["credit_approved_credit_formula"] / r["credit_applications"], 4
                    ),
                    "formula": "approved_flag (Credit decision engine) / applications",
                    "why_it_diverges": "Counts soft-approvals before KYC / affordability complete",
                },
                {
                    "market": r["market"],
                    "as_of_date": r["date"],
                    "metric": "Credit Approval Rate",
                    "definition_owner": "BI (Certified)",
                    "definition_label": "CERTIFIED — Enterprise",
                    "status": "certified",
                    "value": round(
                        r["credit_approved_certified"] / r["credit_applications"], 4
                    ),
                    "formula": "final credit approve after KYC + affordability / applications",
                    "why_it_diverges": "Used on Executive Dashboard; aligns with booked funnel",
                },
            ]
        )
    pd.DataFrame(approval_conflict).to_csv(
        DATA / "metric_conflict_approval_rate.csv", index=False
    )

    write_kpi_dictionary()
    write_datasets_catalog()
    print(f"Wrote synthetic data to {DATA}")


def write_kpi_dictionary() -> None:
    metrics = [
        # Credit
        ("KPI-C01", "Credit Applications", "Credit", "Count of credit applications submitted", "COUNT(applications)", "CBS / Loan origination events", "Daily", "certified", "Enterprise + Credit dashboards"),
        ("KPI-C02", "Credit Approval Rate (Certified)", "Credit", "Share of applications receiving final credit approval after KYC and affordability", "final_approved / applications", "CBS + Underwriting", "Daily", "certified", "Executive + Credit"),
        ("KPI-C03", "Credit Approval Rate (Credit-local)", "Credit", "Share of applications approved by Credit decision engine before final KYC gates", "soft_approved / applications", "Credit decision engine", "Daily", "exploratory", "Conflict view only — not for exec"),
        ("KPI-C04", "Booking Rate", "Credit", "Share of certified-approved applications that are disbursed/booked on CBS", "booked / final_approved", "CBS m_loan / disbursement events", "Daily", "certified", "Executive + Credit"),
        ("KPI-C05", "Disbursed Amount (AED)", "Credit", "Sum of principal disbursed on booking date", "SUM(disbursed_principal)", "CBS", "Daily", "certified", "Executive + Credit"),
        ("KPI-C06", "Portfolio Outstanding (AED)", "Credit", "Sum of outstanding principal on active loans (CBS system of record)", "SUM(principal_outstanding)", "CBS", "Daily", "certified", "Executive + Credit"),
        ("KPI-C07", "FPD Rate", "Credit", "First-payment-default amount as % of first instalment due", "fpd_amount / first_instalment_due", "CBS repayment schedule + collections", "Daily", "certified", "Credit risk indicator"),
        ("KPI-C08", "DPD30 Rate", "Credit", "Outstanding in DPD≥30 as % of portfolio outstanding (amount-weighted)", "dpd30_outstanding / portfolio_outstanding", "CBS delinquency snapshot", "Daily", "certified", "Executive + Credit"),
        # Finance
        ("KPI-F01", "Recognised Revenue (AED)", "Finance", "Revenue recognised under Finance policy (fees + profit accrued in period)", "SUM(recognised_revenue)", "GL / Finance warehouse", "Daily", "certified", "Executive — Finance SoT"),
        ("KPI-F02", "Product-Reported Revenue (AED)", "Finance", "Product's broader revenue view including deferred/projected items", "SUM(product_revenue_estimate)", "Product analytics", "Daily", "exploratory", "Conflict appendix — not exec"),
        ("KPI-F03", "Savings AUM (AED)", "Finance", "Total savings balances on CBS/savings ledger", "SUM(savings_balance)", "CBS / Savings ledger", "Daily", "certified", "Executive"),
        ("KPI-F04", "New Savings Accounts", "Finance", "Count of savings accounts opened", "COUNT(new_savings_accounts)", "Savings product events", "Daily", "certified", "Executive"),
        # Product
        ("KPI-P01", "Active Customers (Certified)", "Product", "Customers with ≥1 open product relationship (loan OR savings OR card), KYC complete, not fraud-blocked", "COUNT DISTINCT certified_active_customers", "Customer 360 (CBS + Savings + Cards)", "Daily", "certified", "Executive — enterprise SoT"),
        ("KPI-P02", "Active Customers (Product 30d login)", "Product", "Customers with app login in last 30 days", "COUNT DISTINCT login_30d", "Product analytics / app events", "Daily", "exploratory", "Conflict view"),
        ("KPI-P03", "Active Customers (Finance 90d txn)", "Product", "Customers with revenue-recognised txn in last 90 days", "COUNT DISTINCT revenue_txn_90d", "GL / Payments", "Daily", "exploratory", "Conflict view"),
        ("KPI-P04", "Active Customers (Credit open loan)", "Product", "Customers with open loan on CBS", "COUNT DISTINCT open_loan_customers", "CBS", "Daily", "exploratory", "Conflict view"),
        # Payments
        ("KPI-Pay01", "Payment Success Rate", "Payments", "Successful payment captures / payment attempts (excl. test)", "successful_attempts / attempts", "Payments platform", "Daily", "certified", "Executive"),
        ("KPI-Pay02", "Payment Attempts", "Payments", "Count of customer payment attempts", "COUNT(attempts)", "Payments platform", "Daily", "certified", "Ops / Product"),
        # Cross-cutting
        ("KPI-X01", "CBS ↔ Warehouse Recon Break Rate", "BI / Finance", "Share of critical loan/balance keys failing OMS/CBS vs warehouse checks", "break_keys / checked_keys", "Recon framework", "Daily", "certified", "Integrity (Phase-1 control)"),
        ("KPI-X02", "Avg Ticket Size (AED)", "Credit", "Average disbursed amount per booked loan", "disbursed_amount / booked", "CBS", "Daily", "certified", "Credit domain"),
    ]
    cols = [
        "kpi_id",
        "name",
        "domain_owner",
        "business_definition",
        "formula",
        "data_source",
        "refresh_cadence",
        "status",
        "where_used",
    ]
    pd.DataFrame(metrics, columns=cols).to_csv(DATA / "kpi_dictionary.csv", index=False)


def write_datasets_catalog() -> None:
    catalog = [
        {
            "dataset": "certified.daily_enterprise_kpis",
            "domain": "Enterprise",
            "description": "Daily certified KPIs across Credit, Finance, Product, Payments, Savings",
            "grain": "date × market",
            "access": "Domain analysts — request via #bi-access",
            "sla": "Daily by 08:00 GST; P1 break response < 4 business hours",
            "status": "certified",
        },
        {
            "dataset": "certified.credit_funnel_daily",
            "domain": "Credit",
            "description": "Application → approval → booking funnel with FPD and DPD30",
            "grain": "date × market",
            "access": "Credit + Risk — request via #bi-access",
            "sla": "Daily by 08:00 GST",
            "status": "certified",
        },
        {
            "dataset": "certified.dim_kpi_dictionary",
            "domain": "BI Governance",
            "description": "Enterprise KPI dictionary with certified vs exploratory status",
            "grain": "kpi_id",
            "access": "All staff (read); edits via KPI Change Request only",
            "sla": "Updated within 2 business days of approved change",
            "status": "certified",
        },
        {
            "dataset": "exploratory.metric_conflict_snapshots",
            "domain": "BI Governance",
            "description": "Side-by-side conflicting definitions for education and governance",
            "grain": "as_of × market × definition",
            "access": "All analysts (read)",
            "sla": "Refreshed with daily enterprise pack",
            "status": "exploratory",
        },
        {
            "dataset": "certified.customer_360_active",
            "domain": "Product / Credit / Finance",
            "description": "Customer-level flags for certified active relationship (loan/savings/card)",
            "grain": "customer_id × as_of_date",
            "access": "Request + manager approval (PII)",
            "sla": "Access granted within 2 business days; daily refresh",
            "status": "certified",
        },
    ]
    pd.DataFrame(catalog).to_csv(DATA / "self_service_datasets.csv", index=False)


if __name__ == "__main__":
    main()
