"""KPI Dictionary — 15+ metrics with governance fields."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.data import load_dictionary

st.set_page_config(page_title="KPI Dictionary | Mal BI", layout="wide")
st.title("KPI Dictionary")
st.caption(
    "Enterprise metric registry · name · domain owner · definition · formula · source · cadence · certified vs exploratory"
)

df = load_dictionary()
status = st.sidebar.multiselect(
    "Status", ["certified", "exploratory"], default=["certified", "exploratory"]
)
domain = st.sidebar.multiselect(
    "Domain owner",
    sorted(df["domain_owner"].unique()),
    default=sorted(df["domain_owner"].unique()),
)

view = df[df["status"].isin(status) & df["domain_owner"].isin(domain)].copy()
st.metric("Metrics in view", len(view))
st.dataframe(view, use_container_width=True, hide_index=True)

st.markdown(
    """
### Governance rules
| Rule | Detail |
|------|--------|
| Certified | Allowed on Executive Dashboard, OKRs, board packs |
| Exploratory | Local analysis / conflict education only |
| Change control | KPI Change Request + domain owner + BI + Finance (for revenue/balance metrics) |
| Conflict | If two teams disagree, BI convenes a 30-min definition workshop; outcome logged here |

### Consistency guarantee
Every KPI ID on Executive and Credit dashboards maps to a **certified** row in this dictionary.
Exploratory metrics appear only on the Conflict Resolution page (and this registry).
"""
)

st.download_button(
    "Download KPI dictionary (CSV)",
    data=view.to_csv(index=False),
    file_name="mal_kpi_dictionary.csv",
    mime="text/csv",
)
