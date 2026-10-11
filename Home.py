"""Mal Enterprise BI — Self-Service Landing Page (entry point)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.data import load_catalog, load_dictionary

st.set_page_config(
    page_title="Mal Enterprise BI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Mal Enterprise BI Foundation")
st.caption(
    "Solo BI Lead prototype · Synthetic data only · Credit · Payments · Savings launch"
)

st.info(
    """
**How to navigate**
1. **01 Executive Dashboard** — 8+ enterprise KPIs (certified definitions only)
2. **02 Credit & Lending** — approval funnel, portfolio quality, risk indicators
3. **03 Metric Conflict Resolution** — Active Customers & Approval Rate defined 3 ways + certified definition
4. **04 KPI Dictionary** — 20 metrics with owner, formula, source, cadence, certified vs exploratory
5. **This page** — self-service datasets, access process, SLAs
"""
)

st.header("Self-Service Landing")
st.markdown(
    """
### What is available
Certified datasets are the only sources allowed in executive and board reporting.
Exploratory datasets may be used for discovery but **must not** be quoted as Mal truth.

### How to request access
1. Post in **#bi-access** (or email bi-platform@mal.bank) with: dataset name, use case, manager, PII need (Y/N).
2. BI reviews against data classification (Public / Internal / Confidential).
3. Access granted within **2 business days** for Internal; Confidential requires Risk/Compliance co-approval.

### SLA
| Priority | Definition | Response |
|----------|------------|----------|
| P1 | Certified KPI wrong / dashboard down / recon break blocking close | < 4 business hours |
| P2 | New certified metric request | Definition workshop in 5 business days |
| P3 | Exploratory sandbox / training | Best effort within 10 business days |

### KPI change control
Certified metrics change only via **KPI Change Request** (owner + Finance/Credit + BI sign-off).
Do not redefine `Active Customers`, `Approval Rate`, or `Recognised Revenue` in local spreadsheets.
"""
)

st.subheader("Certified & exploratory datasets")
st.dataframe(load_catalog(), use_container_width=True, hide_index=True)

st.subheader("Quick link — certified metrics only")
dict_df = load_dictionary()
st.dataframe(
    dict_df[dict_df["status"] == "certified"][
        ["kpi_id", "name", "domain_owner", "refresh_cadence"]
    ],
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")
st.caption(
    "Illustrative synthetic data for Mal assessment · Not real customer or bank data · "
    "Stack: Streamlit + Plotly + CSV marts"
)
