from __future__ import annotations

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List

import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Ensure project root is on sys.path for `src` imports when running from app/
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.models import StrategicObjective, ActionTask, load_actions, load_strategies
from src.alignment import AlignmentEngine
from src.recommendations import generate_recommendations
from src.rag_engine import RAGEngine
from src.viz import (
    fig_overall_gauge,
    fig_coverage_gauge,
    fig_strategy_bar,
    fig_alignment_pie,
    fig_top_match_heatmap,
    fig_owner_workload,
)
from src.io_utils import strategies_dataframe, matches_long_dataframe

APP_TITLE = "Strategy–Action Synchronization AI"
APP_DESC = (
    "An MSc-level Streamlit app that measures alignment between a Strategic Plan "
    "and an Action Plan using sentence embeddings, cosine similarity, and a "
    "persistent vector store."
)
DATA_DIR = Path("data")
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_uploaded_json_list(upload) -> List[dict]:
    data = json.load(upload)
    if not isinstance(data, list):
        raise ValueError("Uploaded JSON must be an array of objects.")
    return data


def _build_strategy_objects(data: List[dict]) -> List[StrategicObjective]:
    return [StrategicObjective(**d) for d in data]


def _build_action_objects(data: List[dict]) -> List[ActionTask]:
    return [ActionTask(**d) for d in data]


load_dotenv()
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.write(APP_DESC)

# Maintenance/disable flag
if os.getenv("DISABLE_ALL_SERVICES", "").lower() in {"1", "true", "yes"}:
    st.warning("The application is currently disabled by administrator.")
    st.stop()

with st.sidebar:
    st.header("Data Sources")
    use_sample = st.checkbox("Use sample data", value=True)
    st.caption("Toggle off to upload your own JSON arrays.")
    use_llm = st.checkbox("Use LLM (RAG) for suggestions if available", value=False)
    uploaded_strategic = None
    uploaded_action = None
    if not use_sample:
        uploaded_strategic = st.file_uploader("Upload Strategic JSON", type=["json"])
        uploaded_action = st.file_uploader("Upload Action JSON", type=["json"])

auto_run = os.getenv("AUTO_RUN_SAMPLE", "").lower() in {"1", "true", "yes"}
run = st.button("Run Synchronization") or auto_run

if run:
    try:
        # Load data
        if use_sample:
            strategies = load_strategies(DATA_DIR / "strategic.json")
            actions = load_actions(DATA_DIR / "action.json")
        else:
            if not uploaded_strategic or not uploaded_action:
                st.warning("Please upload both Strategic and Action JSON files.")
                st.stop()
            s_data = _load_uploaded_json_list(uploaded_strategic)
            a_data = _load_uploaded_json_list(uploaded_action)
            strategies = _build_strategy_objects(s_data)
            actions = _build_action_objects(a_data)

        # Compute alignment
        engine = AlignmentEngine()
        result = engine.align(strategies=strategies, actions=actions, top_k=5)

        # Optional RAG vs deterministic recommendations
        rag_out_per_strategy = None
        recs = None
        if use_llm:
            rag = RAGEngine()
            rag_out_per_strategy = []
            for r in result["strategy_results"]:
                rag_json = rag.generate(
                    strategy=StrategicObjective(
                        id=r["strategy_id"],
                        title=r["strategy_title"],
                        description="",  # description not carried in result; keep empty
                        kpis=[],
                    ),
                    current_score=float(r.get("avg_top3_similarity", 0.0)),
                    retrieved_actions=[
                        {
                            "title": m.get("title"),
                            "owner": m.get("owner"),
                            "similarity": float(m.get("similarity", 0.0)),
                        }
                        for m in r.get("top_matches", [])
                    ],
                )
                rag_out_per_strategy.append(
                    {
                        "strategy_id": r["strategy_id"],
                        "strategy_title": r["strategy_title"],
                        "alignment_label": r["alignment_label"],
                        "rag": rag_json,
                    }
                )
        else:
            recs = generate_recommendations(result)

        # Build dataframes for display/exports
        sdf = strategies_dataframe(result["strategy_results"])
        mdf = matches_long_dataframe(result["strategy_results"])

        # Tabs: Overview | Strategy Explorer | RAG Suggestions | Data Export
        st.subheader("Dashboard")
        tab_overview, tab_strategy, tab_rag, tab_export = st.tabs(
            ["Overview", "Strategy Explorer", "RAG Suggestions", "Data Export"]
        )

        with tab_overview:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(
                    fig_overall_gauge(float(result.get("overall_score", 0.0))),
                    use_container_width=True,
                )
            with c2:
                st.plotly_chart(
                    fig_coverage_gauge(float(result.get("coverage_percent", 0.0))),
                    use_container_width=True,
                )

            st.plotly_chart(
                fig_strategy_bar(result["strategy_results"]), use_container_width=True
            )
            c3, c4 = st.columns(2)
            with c3:
                st.plotly_chart(
                    fig_alignment_pie(result["strategy_results"]),
                    use_container_width=True,
                )
            with c4:
                st.plotly_chart(
                    fig_owner_workload(result["strategy_results"]),
                    use_container_width=True,
                )
            st.plotly_chart(
                fig_top_match_heatmap(result["strategy_results"], top_n=5),
                use_container_width=True,
            )

        with tab_strategy:
            st.dataframe(sdf, use_container_width=True)
            st.dataframe(mdf, use_container_width=True)
            st.subheader("Details by Strategy")
            for r in result["strategy_results"]:
                with st.expander(r["strategy_title"], expanded=False):
                    matches_df = pd.DataFrame(
                        [
                            {
                                "Action": m["title"],
                                "Owner": m["owner"],
                                "Start": m["start_date"],
                                "End": m["end_date"],
                                "Similarity": round(m["similarity"], 3),
                                "Label": m["alignment_label"],
                            }
                            for m in r["top_matches"]
                        ]
                    )
                    st.dataframe(matches_df, use_container_width=True)

        with tab_rag:
            st.subheader("Improvement Recommendations")
            if use_llm and rag_out_per_strategy:
                for item in rag_out_per_strategy:
                    rj = item["rag"]
                    st.markdown(
                        f"**{item['strategy_title']}** — {item['alignment_label']}"
                    )
                    if rj.get("explanation"):
                        st.write(rj["explanation"])
                    if rj.get("suggested_actions"):
                        st.write("Suggested Actions:")
                        for s in rj["suggested_actions"]:
                            st.write(f"- {s}")
                    if rj.get("kpis"):
                        st.write("KPIs:")
                        for k in rj["kpis"]:
                            st.write(f"- {k}")
                    if rj.get("timeline_and_ownership"):
                        t = rj["timeline_and_ownership"]
                        st.write(
                            f"Timeline/Ownership: Owner={t.get('owner', '-')}, Start={t.get('start', '-')}, End={t.get('end', '-')}"
                        )
                    if rj.get("risks"):
                        st.write("Risks:")
                        for rk in rj["risks"]:
                            st.write(f"- {rk}")
            else:
                for rec in recs or []:
                    st.markdown(
                        f"**{rec['strategy_title']}** — {rec['alignment_label']}"
                    )
                    for s in rec.get("suggestions", []):
                        st.write(f"- {s}")

        with tab_export:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            out_path = OUTPUTS_DIR / f"alignment_result_{timestamp}.json"
            if use_llm and rag_out_per_strategy:
                payload = {
                    "result": result,
                    "rag_recommendations": rag_out_per_strategy,
                }
            else:
                payload = {"result": result, "recommendations": recs or []}
            # Save to outputs folder
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            st.success(f"Results saved to {out_path}")
            # Downloads
            st.download_button(
                label="Download Results JSON",
                data=json.dumps(payload, indent=2),
                file_name=f"alignment_result_{timestamp}.json",
                mime="application/json",
            )
            # CSVs
            st.download_button(
                label="Download Strategies CSV",
                data=sdf.to_csv(index=False),
                file_name="strategies.csv",
                mime="text/csv",
            )
            st.download_button(
                label="Download Matches CSV",
                data=mdf.to_csv(index=False),
                file_name="matches.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Error: {e}")
        st.exception(e)
