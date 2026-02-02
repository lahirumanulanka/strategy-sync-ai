from __future__ import annotations

from typing import Iterable

from .models import StrategicObjective, ActionTask


def clean_text(text: str | None) -> str:
    """Simple, deterministic cleaner: collapse whitespace.

    - Keeps original casing
    - Removes extra spaces and newlines
    - Returns an empty string for None
    """
    if not text:
        return ""
    # Normalize whitespace deterministically
    return " ".join(str(text).split())


def _join_parts(parts: Iterable[str]) -> str:
    return clean_text(" | ".join([p for p in parts if p]))


def strategy_to_text(strategy: StrategicObjective) -> str:
    """Combine title, description, and KPIs into a single deterministic text."""
    kpi_text = "; ".join(strategy.kpis or [])
    return _join_parts(
        [
            clean_text(strategy.title),
            clean_text(strategy.description),
            clean_text(kpi_text),
        ]
    )


def action_to_text(action: ActionTask) -> str:
    """Combine title, description, and outputs into a single deterministic text."""
    outputs_text = "; ".join(action.outputs or [])
    return _join_parts(
        [
            clean_text(action.title),
            clean_text(action.description),
            clean_text(outputs_text),
        ]
    )
