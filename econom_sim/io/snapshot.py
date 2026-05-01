"""Serialize snapshots to tabular formats."""

from __future__ import annotations

from typing import Any

import pandas as pd

from econom_sim.engine import PeriodSnapshot


def snapshot_to_citizen_df(snap: PeriodSnapshot) -> pd.DataFrame:
    rows = []
    for row in snap.citizen_rows:
        rows.append(dict(row))
    return pd.DataFrame(rows)


def snapshot_to_factory_df(snap: PeriodSnapshot) -> pd.DataFrame:
    rows = []
    for row in snap.factory_rows:
        rows.append(dict(row))
    return pd.DataFrame(rows)


def snapshots_to_parquet(snaps: list[PeriodSnapshot], base_path: str) -> tuple[str, str]:
    cit_parts = []
    fact_parts = []
    for s in snaps:
        cit_parts.append(snapshot_to_citizen_df(s))
        fact_parts.append(snapshot_to_factory_df(s))
    cit_df = pd.concat(cit_parts, ignore_index=True)
    fact_df = pd.concat(fact_parts, ignore_index=True)
    p_cit = base_path + "_citizens.parquet"
    p_fact = base_path + "_factories.parquet"
    cit_df.to_parquet(p_cit, index=False)
    fact_df.to_parquet(p_fact, index=False)
    return p_cit, p_fact


def snapshots_to_csv(snaps: list[PeriodSnapshot], base_path: str) -> tuple[str, str]:
    """Write combined citizen / factory snapshots as CSV (UTF-8)."""
    cit_parts = []
    fact_parts = []
    for s in snaps:
        cit_parts.append(snapshot_to_citizen_df(s))
        fact_parts.append(snapshot_to_factory_df(s))
    cit_df = pd.concat(cit_parts, ignore_index=True)
    fact_df = pd.concat(fact_parts, ignore_index=True)
    p_cit = base_path + "_citizens.csv"
    p_fact = base_path + "_factories.csv"
    cit_df.to_csv(p_cit, index=False, encoding="utf-8")
    fact_df.to_csv(p_fact, index=False, encoding="utf-8")
    return p_cit, p_fact


def snapshot_to_dict(snap: PeriodSnapshot) -> dict[str, Any]:
    return {
        "period": snap.period,
        "metrics": dict(snap.metrics),
        "citizen_rows": [dict(r) for r in snap.citizen_rows],
        "factory_rows": [dict(r) for r in snap.factory_rows],
    }
