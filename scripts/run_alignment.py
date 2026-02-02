from __future__ import annotations

import json
from datetime import datetime, UTC
import os
from pathlib import Path
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    # Ensure project root is on sys.path for 'src' imports
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # Load environment variables from .env if present (explicit path to avoid edge cases)
    load_dotenv(ROOT / ".env")

    # Maintenance/disable flag
    if os.getenv("DISABLE_ALL_SERVICES", "").lower() in {"1", "true", "yes"}:
        print("All services are disabled by administrator (DISABLE_ALL_SERVICES).")
        return 0

    from src.models import load_actions, load_strategies, StrategicObjective
    from src.alignment import AlignmentEngine
    from src.recommendations import generate_recommendations
    from src.rag_engine import RAGEngine

    strategies = load_strategies(DATA_DIR / "strategic.json")
    actions = load_actions(DATA_DIR / "action.json")

    engine = AlignmentEngine()
    result = engine.align(strategies=strategies, actions=actions, top_k=5)

    # Try RAG if key exists; fallback to rule-based recommendations
    rag = RAGEngine()
    rag_out_per_strategy = []
    for r in result["strategy_results"]:
        # We only have title in result; pull description from original object for a better prompt
        s_obj = next(
            (s for s in strategies if s.id == r["strategy_id"]),
            StrategicObjective(
                id=r["strategy_id"], title=r["strategy_title"], description="", kpis=[]
            ),
        )
        rag_json = rag.generate(
            strategy=s_obj,
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

    # Rule-based for comparison
    recs = generate_recommendations(result)

    payload = {
        "result": result,
        "rag_recommendations": rag_out_per_strategy,
        "recommendations": recs,
    }

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_path = OUTPUTS_DIR / f"alignment_cli_{timestamp}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"Coverage %: {result['coverage_percent']:.2f}")
    print(f"Saved output: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
