from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_daily() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "daily_enterprise_kpis.csv", parse_dates=["date"])
    return df


def load_credit() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "credit_funnel_daily.csv", parse_dates=["date"])


def load_dictionary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "kpi_dictionary.csv")


def load_conflict_active() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "metric_conflict_active_customers.csv")


def load_conflict_approval() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "metric_conflict_approval_rate.csv")


def load_catalog() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "self_service_datasets.csv")


def filter_market(df: pd.DataFrame, market: str) -> pd.DataFrame:
    if market == "All":
        return df
    return df[df["market"] == market].copy()


def latest_as_of(df: pd.DataFrame) -> str:
    return pd.to_datetime(df["date"]).max().date().isoformat()
