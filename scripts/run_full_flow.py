from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys
from pathlib import Path as _Path

# Ensure project root is on sys.path for `src` imports
ROOT_DIR = _Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.pipeline import run_full_flow


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full strategy-sync pipeline")
    parser.add_argument("strategic_path", type=str, help="Path to strategic.json")
    parser.add_argument("action_path", type=str, help="Path to action.json")
    parser.add_argument(
        "--ground_truth_path",
        type=str,
        default=None,
        help="Optional ground truth mapping JSON",
    )
    parser.add_argument("--top_k", type=int, default=5, help="Top-K retrieval")
    parser.add_argument(
        "--rebuild_index",
        action="store_true",
        help="Recreate ChromaDB index by clearing persistent dir",
    )
    args = parser.parse_args()

    result = run_full_flow(
        strategic_path=args.strategic_path,
        action_path=args.action_path,
        ground_truth_path=args.ground_truth_path,
        top_k=args.top_k,
        rebuild_index=args.rebuild_index,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
