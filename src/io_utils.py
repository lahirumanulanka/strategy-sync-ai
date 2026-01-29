from __future__ import annotations

from typing import Any, Dict, List, Tuple

import json
from pathlib import Path

import pandas as pd


def load_alignment_output(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Alignment output not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # Basic shape checks and safe defaults
    result = data.get("result", {}) if isinstance(data, dict) else {}
    metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
    strategy_results = (
        result.get("strategy_results", []) if isinstance(result, dict) else []
    )
    return {
        "raw": data,
        "result": result,
        "metrics": metrics,
        "strategy_results": strategy_results,
    }


def strategies_dataframe(strategy_results: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(strategy_results)
    # Ensure expected columns
    for col, default in [
        ("strategy_id", ""),
        ("strategy_title", ""),
        ("avg_top3_similarity", 0.0),
        ("alignment_label", "Unknown"),
    ]:
        if col not in df.columns:
            df[col] = default
    # Ranking
    df["rank"] = (
        df["avg_top3_similarity"].rank(method="min", ascending=False).astype(int)
    )
    df = df.sort_values(
        ["avg_top3_similarity", "strategy_title"], ascending=[False, True]
    )
    return df


def matches_long_dataframe(strategy_results: List[dict]) -> pd.DataFrame:
    rows: List[dict] = []
    for s in strategy_results:
        sid = s.get("strategy_id")
        stitle = s.get("strategy_title")
        for i, m in enumerate(s.get("top_matches") or []):
            rows.append(
                {
                    "strategy_id": sid,
                    "strategy_title": stitle,
                    "rank": i + 1,
                    "action_id": m.get("action_id"),
                    "action_title": m.get("action_title"),
                    "owner": m.get("owner"),
                    "due_date": m.get("due_date"),
                    "similarity": float(m.get("similarity", 0.0)),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            {
                "strategy_id": [],
                "strategy_title": [],
                "rank": [],
                "action_id": [],
                "action_title": [],
                "owner": [],
                "due_date": [],
                "similarity": [],
            }
        )
    return df


def export_csv(df: pd.DataFrame, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return p
