from __future__ import annotations

from pathlib import Path

from src.pipeline import run_full_flow


def test_full_flow_smoke(tmp_path: Path) -> None:
    data_dir = Path("data")
    strategic = data_dir / "strategic.json"
    action = data_dir / "action.json"
    gt = data_dir / "ground_truth.example.json"

    result = run_full_flow(
        strategic_path=str(strategic),
        action_path=str(strategic.parent / "action.json"),
        ground_truth_path=str(gt),
        top_k=5,
        rebuild_index=False,
    )

    outputs_dir = Path("outputs")
    final_report = outputs_dir / "final_report.json"
    ttl = outputs_dir / "strategy_graph.ttl"
    eval_json = outputs_dir / "evaluation.json"

    assert final_report.exists(), "final_report.json should be created"
    assert ttl.exists(), "TTL graph should be created"
    assert eval_json.exists(), "evaluation.json should be created when GT provided"
    assert isinstance(result.get("overall_score", None), (int, float)), (
        "Overall score present"
    )
