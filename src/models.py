from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

try:
    # Pydantic v2
    from pydantic import ConfigDict  # type: ignore
except Exception:  # pragma: no cover
    ConfigDict = None  # type: ignore


class StrategicObjective(BaseModel):
    """Typed representation of a strategic objective.

    Fields: id, title, description, kpis, priority.
    Extra fields are allowed to support flexible academic datasets.
    """

    id: str
    title: str
    description: str
    kpis: List[str] = Field(default_factory=list)
    priority: str | int | None = None

    if ConfigDict is not None:
        model_config = ConfigDict(extra="allow")


class ActionTask(BaseModel):
    """Typed representation of an action/task entry.

    Fields: id, title, description, owner, start_date, end_date, outputs.
    Extra fields are allowed.
    """

    id: str
    title: str
    description: str
    owner: str
    start_date: date | None = None
    end_date: date | None = None
    outputs: List[str] = Field(default_factory=list)

    if ConfigDict is not None:
        model_config = ConfigDict(extra="allow")


def _load_json_array(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array at '" + str(path) + "'.")
    return data


def load_strategies(path: str | Path) -> List[StrategicObjective]:
    """Load strategic objectives from a JSON array file."""
    path = Path(path)
    records = _load_json_array(path)
    return [StrategicObjective(**rec) for rec in records]


def load_actions(path: str | Path) -> List[ActionTask]:
    """Load action tasks from a JSON array file."""
    path = Path(path)
    records = _load_json_array(path)
    return [ActionTask(**rec) for rec in records]
