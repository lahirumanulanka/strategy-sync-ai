from pathlib import Path

from src.models import StrategicObjective, ActionTask, load_actions, load_strategies
from src.text_utils import strategy_to_text, action_to_text


def test_models_and_utils_smoke():
    strategies = load_strategies(Path("data/strategic.json"))
    actions = load_actions(Path("data/action.json"))
    assert len(strategies) >= 3
    assert len(actions) >= 6
    s_txt = strategy_to_text(strategies[0])
    a_txt = action_to_text(actions[0])
    assert isinstance(s_txt, str) and s_txt
    assert isinstance(a_txt, str) and a_txt
