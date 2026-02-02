from __future__ import annotations

import os
from pathlib import Path

from src.models import load_actions, load_strategies, StrategicObjective
from src.alignment import AlignmentEngine
from src.rag_engine import RAGEngine


def test_alignment_and_rag_generate():
    # Load sample data
    strategies = load_strategies(Path("data/strategic.json"))
    actions = load_actions(Path("data/action.json"))

    # Run alignment
    engine = AlignmentEngine()
    result = engine.align(strategies=strategies, actions=actions, top_k=3)

    # Basic shape checks
    assert 0.0 <= result["overall_score"] <= 100.0
    assert 0.0 <= result["coverage_percent"] <= 100.0
    assert isinstance(result["strategy_results"], list) and result["strategy_results"]

    # Prepare RAG input for first strategy
    first = result["strategy_results"][0]
    s_obj = next(
        (s for s in strategies if s.id == first["strategy_id"]),
        StrategicObjective(
            id=first["strategy_id"],
            title=first["strategy_title"],
            description="",
            kpis=[],
        ),
    )
    retrieved_actions = [
        {
            "title": m.get("title"),
            "owner": m.get("owner"),
            "similarity": float(m.get("similarity", 0.0)),
        }
        for m in first.get("top_matches", [])
    ]

    # Ensure we use fallback (no external API)
    os.environ.pop("OPENAI_API_KEY", None)
    rag = RAGEngine()
    out = rag.generate(
        strategy=s_obj,
        current_score=float(first.get("avg_top3_similarity", 0.0)),
        retrieved_actions=retrieved_actions,
    )

    # Check RAG JSON shape
    assert set(out.keys()) >= {
        "explanation",
        "suggested_actions",
        "kpis",
        "timeline_and_ownership",
        "risks",
    }
    assert (
        isinstance(out["suggested_actions"], list)
        and len(out["suggested_actions"]) >= 3
    )
    assert isinstance(out["kpis"], list) and len(out["kpis"]) >= 2
    assert isinstance(out["timeline_and_ownership"], dict)
    assert isinstance(out["risks"], list) and len(out["risks"]) >= 1
