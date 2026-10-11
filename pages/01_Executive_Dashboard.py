"""Executive Dashboard — certified enterprise KPIs only."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.data import filter_market, latest_as_of, load_daily

st.set_page_config(page_title="Executive Dashboard | Mal BI", layout="wide")
st.title("Executive Dashboard")
st.caption("Certified KPIs only · Credit · Finance · Product · Payments · Savings")

daily = load_daily()
market = st.sidebar.selectbox("Market", ["All", "UAE", "KSA"], index=0)
df = filter_market(daily, market)
as_of = latest_as_of(df)
st.markdown(f"**As of:** `{as_of}` · **Market:** `{market}` · Source: `certified.daily_enterprise_kpis`")

latest = df.sort_values("date").groupby("market").tail(1) if market == "All" else df.sort_values("date").tail(1)
# Aggregate latest across markets when All
if market == "All":
    snap = {
        "active": int(latest["active_customers_certified"].sum()),
        "apps": int(latest["credit_applications"].sum()),
        "approved": int(latest["credit_approved_certified"].sum()),
        "booked": int(latest["credit_booked"].sum()),
        "outstanding": float(latest["portfolio_outstanding_aed"].sum()),
        "revenue": float(latest["revenue_finance_aed"].sum()),
        "savings_aum": float(latest["savings_aum_aed"].sum()),
        "pay_ok": int(latest["payment_successful"].sum()),
        "pay_att": int(latest["payment_attempts"].sum()),
        "dpd30": float(latest["dpd30_outstanding_aed"].sum()),
        "fpd": float(latest["fpd_amount_aed"].sum()),
        "due": float(latest["first_instalment_due_aed"].sum()),
        "disbursed": float(latest["disbursed_amount_aed"].sum()),
        "savings_new": int(latest["savings_new_accounts"].sum()),
    }
else:
    r = latest.iloc[0]
    snap = {
        "active": int(r["active_customers_certified"]),
        "apps": int(r["credit_applications"]),
        "approved": int(r["credit_approved_certified"]),
        "booked": int(r["credit_booked"]),
        "outstanding": float(r["portfolio_outstanding_aed"]),
        "revenue": float(r["revenue_finance_aed"]),
        "savings_aum": float(r["savings_aum_aed"]),
        "pay_ok": int(r["payment_successful"]),
        "pay_att": int(r["payment_attempts"]),
        "dpd30": float(r["dpd30_outstanding_aed"]),
        "fpd": float(r["fpd_amount_aed"]),
        "due": float(r["first_instalment_due_aed"]),
        "disbursed": float(r["disbursed_amount_aed"]),
        "savings_new": int(r["savings_new_accounts"]),
    }

approval = snap["approved"] / snap["apps"] if snap["apps"] else 0
booking = snap["booked"] / snap["approved"] if snap["approved"] else 0
pay_rate = snap["pay_ok"] / snap["pay_att"] if snap["pay_att"] else 0
dpd30_rate = snap["dpd30"] / snap["outstanding"] if snap["outstanding"] else 0
fpd_rate = snap["fpd"] / snap["due"] if snap["due"] else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("KPI-P01 Active Customers (Certified)", f"{snap['active']:,}")
c2.metric("KPI-C02 Approval Rate (Certified)", f"{approval:.1%}")
c3.metric("KPI-C04 Booking Rate", f"{booking:.1%}")
c4.metric("KPI-C06 Portfolio Outstanding (AED)", f"{snap['outstanding']/1e6:.2f}M")

c5, c6, c7, c8 = st.columns(4)
c5.metric("KPI-F01 Recognised Revenue (AED)", f"{snap['revenue']:,.0f}")
c6.metric("KPI-F03 Savings AUM (AED)", f"{snap['savings_aum']/1e6:.2f}M")
c7.metric("KPI-Pay01 Payment Success Rate", f"{pay_rate:.1%}")
c8.metric("KPI-C08 DPD30 Rate", f"{dpd30_rate:.1%}")

st.caption(
    "All tiles use **certified** dictionary IDs. "
    "Product/Finance/Credit local definitions of Active Customers are on the Conflict page — not here."
)

# Trends
trend = df.copy()
if market == "All":
    trend = (
        trend.groupby("date", as_index=False)
        .agg(
            active_customers_certified=("active_customers_certified", "sum"),
            portfolio_outstanding_aed=("portfolio_outstanding_aed", "sum"),
            credit_booked=("credit_booked", "sum"),
            credit_approved_certified=("credit_approved_certified", "sum"),
            credit_applications=("credit_applications", "sum"),
            revenue_finance_aed=("revenue_finance_aed", "sum"),
            dpd30_outstanding_aed=("dpd30_outstanding_aed", "sum"),
        )
    )
trend["approval_rate"] = trend["credit_approved_certified"] / trend["credit_applications"]

left, right = st.columns(2)
with left:
    fig = px.line(
        trend,
        x="date",
        y="active_customers_certified",
        title="Active Customers (Certified) — KPI-P01",
    )
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.line(
        trend,
        x="date",
        y="portfolio_outstanding_aed",
        title="Portfolio Outstanding (AED) — KPI-C06",
    )
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    fig = px.line(trend, x="date", y="approval_rate", title="Approval Rate (Certified) — KPI-C02")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
with right2:
    fig = px.line(
        trend, x="date", y="revenue_finance_aed", title="Recognised Revenue (AED) — KPI-F01"
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"""
### Decision cues (as of {as_of})
- **Growth:** Booked {snap['booked']:,} loans · Disbursed AED {snap['disbursed']:,.0f} · New savings {snap['savings_new']:,}
- **Risk:** FPD rate {fpd_rate:.1%} (KPI-C07) · DPD30 {dpd30_rate:.1%} (KPI-C08)
- **Integrity rule:** Executive pack never mixes exploratory Product/Finance/Credit active-customer counts
"""
)
