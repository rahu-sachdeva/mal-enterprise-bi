"""Credit & Lending domain dashboard."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.data import filter_market, latest_as_of, load_credit, load_daily

st.set_page_config(page_title="Credit & Lending | Mal BI", layout="wide")
st.title("Credit & Lending Domain Dashboard")
st.caption("Approval funnel · Portfolio quality · Risk indicators (certified definitions)")

credit = load_credit()
daily = load_daily()
market = st.sidebar.selectbox("Market", ["All", "UAE", "KSA"], index=0)
cdf = filter_market(credit, market)
ddf = filter_market(daily, market)
as_of = latest_as_of(cdf)
st.markdown(f"**As of:** `{as_of}` · **Market:** `{market}`")

latest = cdf.sort_values("date").groupby("market").tail(1) if market == "All" else cdf.sort_values("date").tail(1)
dlatest = ddf.sort_values("date").groupby("market").tail(1) if market == "All" else ddf.sort_values("date").tail(1)

apps = int(latest["credit_applications"].sum())
approved = int(latest["credit_approved_certified"].sum())
booked = int(latest["credit_booked"].sum())
outstanding = float(latest["portfolio_outstanding_aed"].sum())
fpd_rate = float(latest["fpd_amount_aed"].sum() / latest["first_instalment_due_aed"].sum())
dpd30_rate = float(latest["dpd30_outstanding_aed"].sum() / outstanding)
avg_ticket = float(latest["disbursed_amount_aed"].sum() / booked) if booked else 0
# Credit-local vs certified approval for awareness
credit_local_appr = int(dlatest["credit_approved_credit_formula"].sum())
credit_local_rate = credit_local_appr / apps if apps else 0
certified_rate = approved / apps if apps else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Applications (KPI-C01)", f"{apps:,}")
k2.metric("Approval Rate Certified (KPI-C02)", f"{certified_rate:.1%}")
k3.metric("Booking Rate (KPI-C04)", f"{(booked/approved if approved else 0):.1%}")
k4.metric("FPD Rate (KPI-C07)", f"{fpd_rate:.1%}")
k5.metric("DPD30 Rate (KPI-C08)", f"{dpd30_rate:.1%}")

st.warning(
    f"Credit-local approval rate would show **{credit_local_rate:.1%}** (soft approvals). "
    f"This dashboard uses certified **{certified_rate:.1%}** only. See Conflict Resolution page."
)

st.subheader("Approval funnel (latest day)")
fig = go.Figure(
    go.Funnel(
        y=["Applications", "Approved (Certified)", "Booked / Disbursed"],
        x=[apps, approved, booked],
        textinfo="value+percent initial",
    )
)
st.plotly_chart(fig, use_container_width=True)

trend = cdf.copy()
if market == "All":
    trend = (
        trend.groupby("date", as_index=False)
        .agg(
            credit_applications=("credit_applications", "sum"),
            credit_approved_certified=("credit_approved_certified", "sum"),
            credit_booked=("credit_booked", "sum"),
            portfolio_outstanding_aed=("portfolio_outstanding_aed", "sum"),
            fpd_amount_aed=("fpd_amount_aed", "sum"),
            first_instalment_due_aed=("first_instalment_due_aed", "sum"),
            dpd30_outstanding_aed=("dpd30_outstanding_aed", "sum"),
            disbursed_amount_aed=("disbursed_amount_aed", "sum"),
        )
    )
trend["approval_rate"] = trend["credit_approved_certified"] / trend["credit_applications"]
trend["booking_rate"] = trend["credit_booked"] / trend["credit_approved_certified"]
trend["fpd_rate"] = trend["fpd_amount_aed"] / trend["first_instalment_due_aed"]
trend["dpd30_rate"] = trend["dpd30_outstanding_aed"] / trend["portfolio_outstanding_aed"]

left, right = st.columns(2)
with left:
    melt = trend.melt(
        id_vars=["date"],
        value_vars=["approval_rate", "booking_rate"],
        var_name="metric",
        value_name="rate",
    )
    fig = px.line(melt, x="date", y="rate", color="metric", title="Funnel rates over time")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
with right:
    melt = trend.melt(
        id_vars=["date"],
        value_vars=["fpd_rate", "dpd30_rate"],
        var_name="metric",
        value_name="rate",
    )
    fig = px.line(
        melt, x="date", y="rate", color="metric", title="Risk indicators — FPD & DPD30"
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Portfolio quality")
q1, q2 = st.columns(2)
q1.metric("Outstanding (KPI-C06)", f"AED {outstanding:,.0f}")
q2.metric("Avg Ticket (KPI-X02)", f"AED {avg_ticket:,.0f}")
fig = px.area(
    trend, x="date", y="portfolio_outstanding_aed", title="Portfolio outstanding over time"
)
st.plotly_chart(fig, use_container_width=True)
