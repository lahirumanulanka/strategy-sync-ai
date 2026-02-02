from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import StrategicObjective

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionUserMessageParam


def _alignment_label(score: float) -> str:
    if score >= 0.75:
        return "Strong"
    if score >= 0.55:
        return "Medium"
    return "Weak"


class RAGEngine:
    """Retrieval-Augmented Generation (RAG) helper for improvement suggestions.

    Responsibilities:
    - Accept a strategic objective, current alignment score, and top-K retrieved action tasks
    - Build a structured prompt with clear SYSTEM / CONTEXT / INSTRUCTIONS sections
    - Optionally call an LLM (OpenAI API via env vars) and parse structured JSON
    - Fallback to deterministic, rule-based suggestions if LLM is unavailable
    """

    def __init__(self, model: Optional[str] = None) -> None:
        # Model name can be overridden via env var OPENAI_MODEL
        # Use a widely supported default; allow override via env or arg
        self.model = model or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
        self.api_key = os.environ.get("OPENAI_API_KEY")

    # ------------------------- Prompt Construction -------------------------
    def build_prompt(
        self,
        strategy: StrategicObjective,
        current_score: float,
        retrieved_actions: List[Dict[str, Any]],
    ) -> ChatCompletionUserMessageParam:
        system = "You are an AI business analyst."

        actions_lines = []
        for i, a in enumerate(retrieved_actions, start=1):
            title = a.get("title") or a.get("metadata", {}).get("title") or "Action"
            sim = a.get("similarity")
            actions_lines.append(f"{i}. {title} (similarity: {sim:.2f})")
        actions_block = "\n".join(actions_lines) if actions_lines else "(none)"

        context = (
            f"Strategic Objective:\n\n{strategy.title}\n\n"
            f"Description:\n\n{strategy.description}\n\n"
            f"Current Alignment Score:\n{current_score:.2f} ({_alignment_label(current_score)})\n\n"
            f"Retrieved Action Tasks:\n{actions_block}"
        )

        instructions = (
            "- Explain why alignment is at the current level\n"
            "- Suggest 3 new action tasks\n"
            "- Suggest 2 measurable KPIs\n"
            "- Suggest timeline and ownership\n"
            "- Keep suggestions realistic for AutoBridge"
        )

        response_format = (
            "Respond in strict JSON with keys: "
            "explanation (string), suggested_actions (string[3]), "
            "kpis (string[2]), timeline_and_ownership (object with keys: owner, start, end), "
            "risks (string[1..3])."
        )

        content = (
            "SYSTEM:\n"
            + system
            + "\n\n"
            + "CONTEXT:\n"
            + context
            + "\n\n"
            + "INSTRUCTIONS:\n"
            + instructions
            + "\n\n"
            + "RESPONSE_FORMAT:\n"
            + response_format
        )

        return {
            "role": "user",
            "content": content,
        }

    # ------------------------- LLM Invocation -------------------------
    def _call_openai(self, user_msg: ChatCompletionUserMessageParam) -> Optional[str]:
        if not self.api_key:
            print("RAGEngine: OPENAI_API_KEY not set; using fallback.")
            return None
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=self.api_key)
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI business analyst.",
                    },
                    user_msg,
                ],
            )
            print(f"RAGEngine: OpenAI call succeeded (model={self.model}).")
            return completion.choices[0].message.content
        except Exception as e:
            print(f"RAGEngine: OpenAI call failed: {e!r}; using fallback.")
            return None

    # ------------------------- Parsing and Fallback -------------------------
    def _parse_json(self, text: Optional[str]) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        # Try to locate first JSON object in text
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = text[start : end + 1]
            try:
                return json.loads(snippet)
            except Exception:
                pass
        # Last resort
        try:
            return json.loads(text)
        except Exception:
            return None

    def _fallback_rule_based(
        self,
        strategy: StrategicObjective,
        current_score: float,
        retrieved_actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        label = _alignment_label(current_score)
        # Simple templates for MSc-friendly determinism
        if label == "Weak":
            expl = (
                "Current actions only partially address the strategy's outcomes; coverage is sparse "
                "and lacks clear ownership/timelines, resulting in low similarity scores."
            )
            actions = [
                "Publish a standardized landed-cost breakdown with supplier lane mapping",
                "Automate ingestion of duties/freight/insurance components with validations",
                "Launch monthly variance review with supplier scorecards and corrective actions",
            ]
            kpis = [
                "Cost variance across lanes < 3%",
                "Data coverage of cost components ≥ 90% of SKUs",
            ]
            timeline = {
                "owner": "Finance Ops",
                "start": "2026-02-15",
                "end": "2026-05-31",
            }
            risks = [
                "Supplier data quality or delays may limit transparency",
                "Insufficient engineering capacity for integrations",
            ]
        elif label == "Medium":
            expl = (
                "Alignment is improving but gaps remain in data completeness and process rigor; "
                "consolidation and clearer deliverables would strengthen coverage."
            )
            actions = [
                "Unify overlapping cost tools into a single authoritative calculator",
                "Backfill historical cost data and set validation thresholds",
                "Define escalation playbooks for clearance delays and exceptions",
            ]
            kpis = [
                "Audit pass rate ≥ 95%",
                "Average clearance time < 24h",
            ]
            timeline = {
                "owner": "Operations",
                "start": "2026-03-01",
                "end": "2026-06-30",
            }
            risks = [
                "Fragmented ownership across finance and operations",
            ]
        else:  # Strong
            expl = (
                "Actions strongly map to the strategy. Focus on monitoring, risk management, and "
                "sustaining improvements through governance routines."
            )
            actions = [
                "Introduce quarterly retrospectives with supplier and ops stakeholders",
                "Automate anomaly detection for lane cost spikes",
                "Publish transparency dashboards for leadership review",
            ]
            kpis = [
                "Early-warning alerts resolved within 48h",
                "Quarterly savings achieved vs. target",
            ]
            timeline = {
                "owner": "Data Science",
                "start": "2026-03-15",
                "end": "2026-07-31",
            }
            risks = [
                "Model drift or changing tariffs impacting reliability",
            ]

        return {
            "explanation": expl,
            "suggested_actions": actions,
            "kpis": kpis,
            "timeline_and_ownership": timeline,
            "risks": risks,
        }

    # ------------------------- Public API -------------------------
    def generate(
        self,
        strategy: StrategicObjective,
        current_score: float,
        retrieved_actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        user_msg = self.build_prompt(strategy, current_score, retrieved_actions)
        text = self._call_openai(user_msg)
        parsed = self._parse_json(text)
        if parsed:
            return parsed
        return self._fallback_rule_based(strategy, current_score, retrieved_actions)
