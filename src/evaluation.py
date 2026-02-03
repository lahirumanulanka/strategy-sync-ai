from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Set

import math

from .alignment import AlignmentEngine
from .models import StrategicObjective, ActionTask


@dataclass
class EvalConfig:
    top_k: int = 5


def precision_recall_at_k(
    pred_ids: List[str], truth_ids: Set[str], k: int
) -> Tuple[float, float]:
    preds = pred_ids[:k]
    hits = sum(1 for pid in preds if pid in truth_ids)
    precision = hits / max(1, len(preds))
    recall = hits / max(1, len(truth_ids))
    return precision, recall


def average_precision(pred_ids: List[str], truth_ids: Set[str]) -> float:
    hits = 0
    ap_sum = 0.0
    for i, pid in enumerate(pred_ids, start=1):
        if pid in truth_ids:
            hits += 1
            ap_sum += hits / i
    return ap_sum / max(1, hits)


def ndcg_at_k(pred_ids: List[str], truth_ids: Set[str], k: int) -> float:
    # Relevance is binary: 1 if in truth, else 0
    dcg = 0.0
    for i, pid in enumerate(pred_ids[:k], start=1):
        rel = 1.0 if pid in truth_ids else 0.0
        dcg += rel / math.log2(i + 1)
    # Ideal DCG assumes all relevant items are ranked first
    ideal_rel_count = min(len(truth_ids), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_rel_count + 1))
    return dcg / idcg if idcg > 0 else 0.0


@dataclass
class StrategyEval:
    strategy_id: str
    precision_at_k: float
    recall_at_k: float
    ap: float
    ndcg: float


@dataclass
class EvalSummary:
    top_k: int
    macro_precision: float
    macro_recall: float
    map: float
    mean_ndcg: float
    per_strategy: List[StrategyEval]


def evaluate_alignment(
    engine: AlignmentEngine,
    strategies: Iterable[StrategicObjective],
    actions: Iterable[ActionTask],
    ground_truth: Dict[str, List[str]],
    config: EvalConfig | None = None,
) -> EvalSummary:
    cfg = config or EvalConfig()
    # Run alignment retrieval
    result = engine.align(
        strategies=list(strategies), actions=list(actions), top_k=cfg.top_k
    )

    per_strategy: List[StrategyEval] = []
    p_list: List[float] = []
    r_list: List[float] = []
    ap_list: List[float] = []
    ndcg_list: List[float] = []

    for sres in result["strategy_results"]:
        sid = sres["strategy_id"]
        preds = [m["action_id"] for m in sres.get("top_matches", [])]
        truth = set(ground_truth.get(sid, []))
        p, r = precision_recall_at_k(preds, truth, cfg.top_k)
        ap = average_precision(preds, truth)
        nd = ndcg_at_k(preds, truth, cfg.top_k)

        per_strategy.append(
            StrategyEval(
                strategy_id=sid,
                precision_at_k=p,
                recall_at_k=r,
                ap=ap,
                ndcg=nd,
            )
        )
        p_list.append(p)
        r_list.append(r)
        ap_list.append(ap)
        ndcg_list.append(nd)

    summary = EvalSummary(
        top_k=cfg.top_k,
        macro_precision=sum(p_list) / max(1, len(p_list)),
        macro_recall=sum(r_list) / max(1, len(r_list)),
        map=sum(ap_list) / max(1, len(ap_list)),
        mean_ndcg=sum(ndcg_list) / max(1, len(ndcg_list)),
        per_strategy=per_strategy,
    )
    return summary
