from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import XSD

from .models import StrategicObjective, ActionTask, load_strategies, load_actions

# Base namespace for the project
SS = Namespace("http://example.org/strategy-sync#")


def load_base_ontology(ontology_path: str | Path) -> Graph:
    """Load the base ontology (TTL) and return an RDFLib graph."""
    g = Graph()
    g.parse(str(ontology_path), format="turtle")
    return g


def _strategy_uri(s: StrategicObjective) -> URIRef:
    return URIRef(f"http://example.org/strategy-sync/strategy/{s.id}")


def _action_uri(a: ActionTask) -> URIRef:
    return URIRef(f"http://example.org/strategy-sync/action/{a.id}")


def add_strategies(g: Graph, strategies: Iterable[StrategicObjective]) -> None:
    for s in strategies:
        s_uri = _strategy_uri(s)
        g.add((s_uri, RDF.type, SS.Strategy))
        g.add((s_uri, RDFS.label, Literal(s.title)))
        # KPIs as literals connected via relatesToKPI
        for kpi in s.kpis or []:
            g.add((s_uri, SS.relatesToKPI, Literal(kpi)))


def add_actions(g: Graph, actions: Iterable[ActionTask]) -> None:
    for a in actions:
        a_uri = _action_uri(a)
        g.add((a_uri, RDF.type, SS.ActionTask))
        g.add((a_uri, RDFS.label, Literal(a.title)))
        if a.owner:
            g.add((a_uri, SS.ownedBy, Literal(a.owner)))
        if a.start_date:
            g.add((a_uri, SS.startDate, Literal(str(a.start_date), datatype=XSD.date)))
        if a.end_date:
            g.add((a_uri, SS.endDate, Literal(str(a.end_date), datatype=XSD.date)))


def link_strategy_to_actions(
    g: Graph, strategies: Iterable[StrategicObjective], actions: Iterable[ActionTask]
) -> None:
    """Naive linking: if an action title mentions a strategy keyword, link via hasAction.

    This is a placeholder; you can replace with embedding-based mapping later.
    """
    # Simple keyword heuristic: link all actions to all strategies for scaffold
    for s in strategies:
        s_uri = _strategy_uri(s)
        for a in actions:
            a_uri = _action_uri(a)
            g.add((s_uri, SS.hasAction, a_uri))


def build_graph(
    ontology_path: str | Path,
    strategies: Iterable[StrategicObjective],
    actions: Iterable[ActionTask],
) -> Graph:
    g = load_base_ontology(ontology_path)
    add_strategies(g, strategies)
    add_actions(g, actions)
    link_strategy_to_actions(g, strategies, actions)
    return g


def build_graph_from_files(
    ontology_path: str | Path, strategy_json: str | Path, action_json: str | Path
) -> Graph:
    strategies = load_strategies(strategy_json)
    actions = load_actions(action_json)
    return build_graph(ontology_path, strategies, actions)


def save_graph(g: Graph, out_path: str | Path, fmt: str = "turtle") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(out_path), format=fmt)
    return out_path
