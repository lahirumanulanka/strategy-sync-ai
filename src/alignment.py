from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import os

from sentence_transformers import SentenceTransformer

from .models import StrategicObjective, ActionTask
from .text_utils import strategy_to_text, action_to_text
from .vector_store import ActionVectorStore


@dataclass
class Thresholds:
    strong: float = 0.75
    medium: float = 0.55


class AlignmentEngine:
    """Compute alignment between strategies and actions using embeddings + ChromaDB."""

    def __init__(
        self,
        model_name: str | None = None,
        persist_directory: str = "chroma_db",
        thresholds: Thresholds | None = None,
    ) -> None:
        self.model_name = (
            model_name
            or os.environ.get("EMBEDDING_MODEL")
            or "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.embedder = SentenceTransformer(self.model_name)
        self.store = ActionVectorStore(persist_directory=persist_directory)
        self.thresholds = thresholds or Thresholds()

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Ensure plain Python floats (not numpy scalar types) for ChromaDB
        arr = self.embedder.encode(texts, normalize_embeddings=True)
        return [[float(x) for x in vec] for vec in arr]

    def index_actions(
        self, actions: List[ActionTask]
    ) -> Tuple[List[str], List[str], List[List[float]]]:
        action_ids = [a.id for a in actions]
        action_docs = [action_to_text(a) for a in actions]
        action_embs = self._embed_texts(action_docs)
        metadatas = [
            {
                "title": a.title,
                "owner": a.owner,
                "start_date": str(a.start_date) if a.start_date else None,
                "end_date": str(a.end_date) if a.end_date else None,
            }
            for a in actions
        ]
        self.store.upsert_actions(
            ids=action_ids,
            documents=action_docs,
            embeddings=action_embs,
            metadatas=metadatas,
        )
        return action_ids, action_docs, action_embs

    def _label_for_score(self, score: float) -> str:
        if score >= self.thresholds.strong:
            return "Strong"
        if score >= self.thresholds.medium:
            return "Medium"
        return "Weak"

    def align(
        self,
        strategies: List[StrategicObjective],
        actions: List[ActionTask],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        # Ensure index
        self.index_actions(actions)

        strategy_results: List[Dict[str, Any]] = []
        avg_scores: List[float] = []
        strong_counts: List[int] = []

        for s in strategies:
            s_text = strategy_to_text(s)
            s_emb = self._embed_texts([s_text])[0]
            matches = self.store.query_by_embedding(s_emb, top_k=top_k)

            # Prepare match details with labels
            match_details: List[Dict[str, Any]] = []
            for m in matches:
                label = self._label_for_score(m["similarity"])
                meta = m.get("metadata", {}) or {}
                match_details.append(
                    {
                        "action_id": m["id"],
                        "title": meta.get("title"),
                        "owner": meta.get("owner"),
                        "start_date": meta.get("start_date"),
                        "end_date": meta.get("end_date"),
                        "similarity": m["similarity"],
                        "alignment_label": label,
                    }
                )

            # Strategy-wise average: top 3 similarities
            top3 = sorted([m["similarity"] for m in matches], reverse=True)[:3]
            avg = sum(top3) / max(1, len(top3))
            avg_scores.append(avg)

            strong_count = sum(
                1 for m in match_details if m["alignment_label"] == "Strong"
            )
            strong_counts.append(strong_count)

            strategy_results.append(
                {
                    "strategy_id": s.id,
                    "strategy_title": s.title,
                    "avg_top3_similarity": avg,
                    "alignment_label": self._label_for_score(avg),
                    "top_matches": match_details,
                }
            )

        overall = (sum(avg_scores) / max(1, len(avg_scores))) * 100.0
        coverage = (
            sum(1 for c in strong_counts if c >= 2) / max(1, len(strategies))
        ) * 100.0

        return {
            "model": self.model_name,
            "thresholds": {
                "strong": self.thresholds.strong,
                "medium": self.thresholds.medium,
            },
            "overall_score": round(overall, 2),
            "coverage_percent": round(coverage, 2),
            "strategy_results": strategy_results,
        }
