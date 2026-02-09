from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .models import StrategicObjective, ActionTask, load_strategies, load_actions
from .alignment import AlignmentEngine, Thresholds
from .ontology import build_graph_from_alignment, save_graph, query_graph_stats
from .recommendations import generate_recommendations
from .evaluation import run_evaluation


@dataclass
class PipelineConfig:
    """Config parameters for the full pipeline run."""

    model_name: Optional[str] = None
    persist_directory: str = "chroma_db"
    top_k: int = 5
    thresholds: Thresholds = field(default_factory=Thresholds)
    rebuild_index: bool = False


def run_full_flow(
    strategic_path: str | Path,
    action_path: str | Path,
    ground_truth_path: str | Path | None = None,
    top_k: int = 5,
    rebuild_index: bool = False,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the entire pipeline end-to-end and persist artifacts.

    Steps:
    A) Load JSON strategies/actions
    B) Preprocess/normalize texts (handled by text_utils during alignment)
    C) Generate embeddings with sentence-transformers
    D) Upsert actions into ChromaDB (persistent storage)
    E) Retrieve top_k actions per strategy, cosine similarity, label
    F) Compute alignment score per strategy + overall + coverage
    G) Build ontology graph (RDFLib) with classes & properties
    H) Run SPARQL queries for explainability stats
    I) Generate recommendations (deterministic fallback)
    J) Run evaluation if ground truth provided
    K) Save final report JSON consolidating all results
    """

    strategic_path = Path(strategic_path)
    action_path = Path(str(action_path))
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # A) Load
    strategies: List[StrategicObjective] = load_strategies(strategic_path)
    actions: List[ActionTask] = load_actions(action_path)

    # Optionally rebuild index by recreating persistent directory
    persist_dir = Path("chroma_db")
    if rebuild_index:
        try:
            import shutil

            if persist_dir.exists():
                shutil.rmtree(persist_dir, ignore_errors=True)
        except Exception:
            # Fall back to unlinking files
            if persist_dir.exists():
                for p in persist_dir.glob("**/*"):
                    if p.is_file():
                        try:
                            p.unlink()
                        except Exception:
                            pass
    persist_dir.mkdir(parents=True, exist_ok=True)

    # Orchestrate alignment engine
    engine = AlignmentEngine(model_name=model_name, persist_directory=str(persist_dir))

    # E/F) Alignment (includes B/C/D under the hood)
    alignment_result: Dict[str, Any] = engine.align(
        strategies=strategies, actions=actions, top_k=top_k
    )

    # G) Build ontology graph from alignment
    graph = build_graph_from_alignment(
        strategies=strategies, actions=actions, alignment_result=alignment_result
    )
    ttl_path = save_graph(graph, outputs_dir / "strategy_graph.ttl")

    # H) Graph stats
    graph_stats = query_graph_stats(graph)
    (outputs_dir / "graph_stats.json").write_text(
        __json_dump(graph_stats), encoding="utf-8"
    )

    # I) Recommendations (deterministic)
    recommendations = generate_recommendations(alignment_result)

    # J) Evaluation
    evaluation: Dict[str, Any] | None = None
    if ground_truth_path:
        gt_path_str = str(ground_truth_path)
        evaluation = run_evaluation(
            alignment_result=alignment_result,
            ground_truth_path=gt_path_str,
            top_k=top_k,
        )
        (outputs_dir / "evaluation.json").write_text(
            __json_dump(evaluation), encoding="utf-8"
        )

    # K) Final report
    final_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": {
            "top_k": top_k,
            "rebuild_index": rebuild_index,
            "model": alignment_result.get("model"),
            "thresholds": alignment_result.get("thresholds"),
        },
        "overall_score": alignment_result.get("overall_score"),
        "coverage_percent": alignment_result.get("coverage_percent"),
        "per_strategy": alignment_result.get("strategy_results", []),
        "recommendations": recommendations,
        "graph_stats": graph_stats,
        "evaluation": evaluation,
        "artifacts": {
            "ttl": str(ttl_path),
            "graph_stats": str(outputs_dir / "graph_stats.json"),
            "evaluation": str(outputs_dir / "evaluation.json"),
        },
    }
    (outputs_dir / "final_report.json").write_text(
        __json_dump(final_report), encoding="utf-8"
    )

    return final_report


def __json_dump(obj: Any) -> str:
    import json

    return json.dumps(obj, indent=2, ensure_ascii=False)
