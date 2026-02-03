from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.models import load_strategies, load_actions  # noqa: E402
from src.alignment import AlignmentEngine  # noqa: E402
from src.evaluation import evaluate_alignment, EvalConfig  # noqa: E402

STRATEGY_JSON = ROOT / "data" / "strategic.json"
ACTION_JSON = ROOT / "data" / "action.json"
GROUND_TRUTH_JSON = ROOT / "data" / "ground_truth.json"


def main() -> None:
    # Load inputs
    strategies = load_strategies(STRATEGY_JSON)
    actions = load_actions(ACTION_JSON)

    if not GROUND_TRUTH_JSON.exists():
        print(f"Ground truth not found at {GROUND_TRUTH_JSON}.")
        print("Please create it based on data/ground_truth.example.json")
        return

    with GROUND_TRUTH_JSON.open("r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    # Align and evaluate
    engine = AlignmentEngine()
    summary = evaluate_alignment(
        engine, strategies, actions, ground_truth, EvalConfig(top_k=5)
    )

    print("Evaluation Summary:")
    print(f"- Top-K:           {summary.top_k}")
    print(f"- Macro Precision: {summary.macro_precision:.3f}")
    print(f"- Macro Recall:    {summary.macro_recall:.3f}")
    print(f"- MAP:             {summary.map:.3f}")
    print(f"- Mean NDCG:       {summary.mean_ndcg:.3f}")

    print("\nPer-strategy metrics:")
    for s in summary.per_strategy:
        print(
            f"  {s.strategy_id}: P@{summary.top_k}={s.precision_at_k:.3f} | R@{summary.top_k}={s.recall_at_k:.3f} | AP={s.ap:.3f} | NDCG={s.ndcg:.3f}"
        )


if __name__ == "__main__":
    main()
