from __future__ import annotations

from typing import Any, Dict, List


def generate_recommendations(alignment_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate professional, business-oriented recommendations per strategy.

    Rules:
    - Weak: suggest missing actions, KPIs, ownership, timelines
    - Medium: suggest strengthening or refinement
    - Strong: suggest monitoring and review cadence
    """
    recs: List[Dict[str, Any]] = []

    for s in alignment_result.get("strategy_results", []):
        label = s.get("alignment_label", "Weak")
        title = s.get("strategy_title", "Strategy")
        content: List[str] = []

        if label == "Weak":
            content.append(
                "Define at least two actionable workstreams directly mapped to the strategy's outcomes."
            )
            content.append(
                "Introduce 2–3 specific KPIs (leading and lagging) with baselines and quarterly targets."
            )
            content.append(
                "Assign clear ownership (single accountable lead) and set start/end dates with interim milestones."
            )
            content.append(
                "Prioritize quick wins that increase early traction; schedule a governance review in 4–6 weeks."
            )
        elif label == "Medium":
            content.append(
                "Strengthen alignment by refining scope, clarifying deliverables, and ensuring data availability."
            )
            content.append(
                "Consolidate overlapping tasks and add one high-impact initiative to increase coverage."
            )
            content.append(
                "Validate KPI definitions, ownership, and cross-functional dependencies; confirm timelines."
            )
            content.append(
                "Set a monthly review cadence with a risk/issue log and corrective actions."
            )
        else:  # Strong
            content.append(
                "Maintain momentum: monitor KPI performance, track risks, and ensure stakeholder communications."
            )
            content.append(
                "Run quarterly retrospectives to capture learnings and adjust resourcing or scope as needed."
            )
            content.append(
                "Confirm sustainability: verify process handoffs and long-term ownership beyond pilot phases."
            )

        recs.append(
            {
                "strategy_id": s.get("strategy_id"),
                "strategy_title": title,
                "alignment_label": label,
                "suggestions": content,
            }
        )

    return recs
