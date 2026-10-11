"""Metric Conflict Resolution — show 3 definitions + certified."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.data import load_conflict_active, load_conflict_approval

st.set_page_config(page_title="Metric Conflict Resolution | Mal BI", layout="wide")
st.title("Metric Conflict Resolution")
st.caption(
    "Same metric, three domain definitions — plus the reconciled certified definition for enterprise reporting"
)

active = load_conflict_active()
approval = load_conflict_approval()
market = st.sidebar.selectbox("Market", ["UAE", "KSA"], index=0)

st.header("1) Active Customers — three ways + certified")
a = active[active["market"] == market].copy()
st.markdown(
    f"**As of {a['as_of_date'].iloc[0]} · {market}** — "
    "Finance, Product, and Credit each reported a different 'active' number at launch."
)

# Highlight certified
def style_status(row):
    return ["background-color: #d4edda" if row["status"] == "certified" else "" for _ in row]


display_cols = [
    "definition_label",
    "definition_owner",
    "value",
    "status",
    "formula",
    "why_it_diverges",
]
st.dataframe(
    a[display_cols].style.apply(
        lambda r: [
            "background-color: #c8e6c9; font-weight: 600" if r["status"] == "certified" else ""
            for _ in r
        ],
        axis=1,
    ),
    use_container_width=True,
    hide_index=True,
)

fig = px.bar(
    a,
    x="definition_owner",
    y="value",
    color="status",
    color_discrete_map={"certified": "#2e7d32", "exploratory": "#ef6c00"},
    title=f"Active Customers by definition — {market}",
    text="value",
)
st.plotly_chart(fig, use_container_width=True)

st.success(
    """
**CERTIFIED decision (KPI-P01):** Count distinct customers with ≥1 open product relationship
(active loan on CBS **OR** open savings **OR** active card), KYC complete, not fraud-blocked.

**Why this wins:** Aligns Finance (economic relationship), Credit (CBS book), and Product (platform)
without inflating via login-only users or excluding savings-only customers.
**Executive Dashboard uses only this number.**
"""
)

st.header("2) Credit Approval Rate — Credit-local vs certified")
ap = approval[approval["market"] == market].copy()
st.dataframe(ap[display_cols], use_container_width=True, hide_index=True)
fig2 = px.bar(
    ap,
    x="definition_owner",
    y="value",
    color="status",
    color_discrete_map={"certified": "#2e7d32", "exploratory": "#ef6c00"},
    title=f"Approval Rate by definition — {market}",
    text=ap["value"].map(lambda x: f"{x:.1%}"),
)
fig2.update_yaxes(tickformat=".0%")
st.plotly_chart(fig2, use_container_width=True)

st.success(
    """
**CERTIFIED decision (KPI-C02):** Final credit approve after KYC + affordability / applications.

Credit-local soft-approvals remain available as **exploratory KPI-C03** for Credit Ops tuning,
but must not appear on Executive or board packs.
"""
)

st.markdown(
    """
### How to interpret this view
1. Orange / exploratory bars = domain-local definitions (valid for local analysis, not enterprise truth).
2. Green / certified bar = sole number allowed on Executive Dashboard and leadership OKRs.
3. Gap between bars = governance risk if left unresolved (conflicting OKRs, wrong capital narrative).
4. Full formulas live in **04 KPI Dictionary** with owner and change-control status.
"""
)
