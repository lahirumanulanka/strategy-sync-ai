from __future__ import annotations

from typing import Any, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def fig_overall_gauge(overall_score: float) -> go.Figure:
    value = float(overall_score or 0.0)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": "Overall Synchronization Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#4CAF50"},
                "steps": [
                    {"range": [0, 55], "color": "#ffdddd"},
                    {"range": [55, 75], "color": "#fff3cd"},
                    {"range": [75, 100], "color": "#ddffdd"},
                ],
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def fig_coverage_gauge(coverage_percent: float) -> go.Figure:
    value = float(coverage_percent or 0.0)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": "Coverage Percent"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2196F3"},
                "steps": [
                    {"range": [0, 30], "color": "#ffdddd"},
                    {"range": [30, 60], "color": "#fff3cd"},
                    {"range": [60, 100], "color": "#ddffdd"},
                ],
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def fig_strategy_bar(strategy_results: List[dict]) -> go.Figure:
    df = pd.DataFrame(strategy_results)
    if df.empty:
        df = pd.DataFrame(
            {
                "strategy_title": ["No data"],
                "avg_top3_similarity": [0.0],
            }
        )
    df = df.sort_values("avg_top3_similarity", ascending=False)
    fig = px.bar(
        df,
        x="strategy_title",
        y="avg_top3_similarity",
        title="Average Top-3 Similarity per Strategy",
        labels={"strategy_title": "Strategy", "avg_top3_similarity": "Avg Similarity"},
    )
    fig.update_layout(
        height=400, xaxis_tickangle=-30, margin=dict(l=10, r=10, t=40, b=80)
    )
    fig.update_traces(marker_color="#6C63FF")
    return fig


def fig_alignment_pie(strategy_results: List[dict]) -> go.Figure:
    df = pd.DataFrame(strategy_results)
    if df.empty:
        df = pd.DataFrame({"alignment_label": ["No data"], "count": [1]})
    else:
        df = df["alignment_label"].fillna("Unknown").value_counts().reset_index()
        df.columns = ["alignment_label", "count"]
    fig = px.pie(
        df,
        names="alignment_label",
        values="count",
        title="Alignment Label Distribution",
        color="alignment_label",
        color_discrete_map={
            "Weak": "#ff6b6b",
            "Medium": "#ffd166",
            "Strong": "#06d6a0",
            "Unknown": "#cccccc",
            "No data": "#cccccc",
        },
    )
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=40, b=10))
    return fig


def fig_top_match_heatmap(strategy_results: List[dict], top_n: int = 5) -> go.Figure:
    rows = []
    for s in strategy_results:
        title = s.get("strategy_title", s.get("strategy_id", ""))
        matches = s.get("top_matches") or []
        # sort by similarity desc
        matches = sorted(
            matches, key=lambda m: float(m.get("similarity", 0.0)), reverse=True
        )[:top_n]
        # fill to top_n
        sims = [float(m.get("similarity", 0.0)) for m in matches]
        if len(sims) < top_n:
            sims.extend([0.0] * (top_n - len(sims)))
        rows.append(
            {"strategy": title, **{f"rank_{i + 1}": sims[i] for i in range(top_n)}}
        )
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            {"strategy": ["No data"], **{f"rank_{i + 1}": [0.0] for i in range(top_n)}}
        )
    # Heatmap matrix
    z = df[[f"rank_{i + 1}" for i in range(top_n)]].to_numpy(dtype=float)
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=[f"Rank {i + 1}" for i in range(top_n)],
            y=df["strategy"].tolist(),
            colorscale="Viridis",
            zmin=0.0,
            zmax=1.0,
            colorbar=dict(title="Similarity"),
        )
    )
    fig.update_layout(
        title="Top Matches Similarity Heatmap",
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return fig


def fig_owner_workload(strategy_results: List[dict]) -> go.Figure:
    owners: list[str] = []
    for s in strategy_results:
        for m in s.get("top_matches") or []:
            owners.append(m.get("owner") or "Unknown")
    df = pd.DataFrame({"owner": owners})
    if df.empty:
        df = pd.DataFrame({"owner": ["No data"], "count": [1]})
    else:
        df = df["owner"].value_counts().reset_index()
        df.columns = ["owner", "count"]
    fig = px.bar(
        df,
        x="owner",
        y="count",
        title="Owner Workload (Top Matches Count)",
        labels={"owner": "Owner", "count": "Count"},
    )
    fig.update_layout(
        height=400, xaxis_tickangle=-30, margin=dict(l=10, r=10, t=40, b=80)
    )
    fig.update_traces(marker_color="#00bcd4")
    return fig
