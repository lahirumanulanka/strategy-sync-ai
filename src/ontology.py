from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any, List, Tuple, cast

from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef
from rdflib.namespace import XSD

from .models import StrategicObjective, ActionTask

# Base namespace for the project
SS = Namespace("http://example.org/strategy-sync#")


def _strategy_uri(s: StrategicObjective) -> URIRef:
    return URIRef(f"http://example.org/strategy-sync/strategy/{s.id}")


def _action_uri(a: ActionTask) -> URIRef:
    return URIRef(f"http://example.org/strategy-sync/action/{a.id}")


def build_graph_from_alignment(
    strategies: Iterable[StrategicObjective],
    actions: Iterable[ActionTask],
    alignment_result: Dict[str, Any],
) -> Graph:
    """Construct an RDF graph capturing strategies, actions and matched links.

    Creates:
    - Classes: ss:Strategy, ss:ActionTask
    - Properties: ss:hasAction, ss:ownedBy, ss:startDate, ss:endDate
    - Edge attributes: ss:hasSimilarity, ss:hasLabel on Strategy→ActionTask link
    """
    g = Graph()
    g.bind("ss", SS)

    # Index actions by id for quick lookup
    action_index = {a.id: a for a in actions}

    # Add all strategies and actions as nodes with labels
    for s in strategies:
        s_uri = _strategy_uri(s)
        g.add((s_uri, RDF.type, SS.Strategy))
        g.add((s_uri, RDFS.label, Literal(s.title)))

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

    # Create hasAction links for top-k matches per strategy with attributes
    for sres in alignment_result.get("strategy_results", []):
        sid = sres.get("strategy_id")
        s_uri = URIRef(f"http://example.org/strategy-sync/strategy/{sid}")
        for m in sres.get("top_matches", []):
            aid = m.get("action_id")
            a = action_index.get(aid)
            if not a:
                continue
            a_uri = _action_uri(a)
            # Link
            g.add((s_uri, SS.hasAction, a_uri))
            # Edge attributes as reified properties on the action node (simple literal encoding)
            # Alternatively, attach them as direct literals with a composite predicate
            g.add((s_uri, SS.hasSimilarity, Literal(float(m.get("similarity", 0.0)))))
            g.add((s_uri, SS.hasLabel, Literal(str(m.get("alignment_label", "Weak")))))

    return g


def save_graph(g: Graph, out_path: str | Path, fmt: str = "turtle") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(out_path), format=fmt)
    return out_path


def query_graph_stats(g: Graph) -> Dict[str, Any]:
    """Run SPARQL queries to produce explainability stats.

    - actions_per_strategy: count of ss:hasAction per strategy
    - strategies with zero matched actions
    - owner workload counts (actions per owner)
    """
    actions_per_strategy: Dict[str, int] = {}
    zero_action_strategies: List[str] = []
    owner_workload: Dict[str, int] = {}

    # SPARQL prefixes
    prefix = """
        PREFIX ss: <http://example.org/strategy-sync#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    """

    # Actions per strategy via COUNT
    q_actions_per_strategy = (
        prefix
        + """
        SELECT ?label (COUNT(?a) AS ?cnt)
        WHERE {
            ?s rdf:type ss:Strategy .
            ?s rdfs:label ?label .
            OPTIONAL { ?s ss:hasAction ?a }
        }
        GROUP BY ?label
    """
    )
    for label_lit, cnt_lit in cast(
        Iterable[Tuple[Any, Any]], g.query(q_actions_per_strategy)
    ):
        label = str(label_lit)
        cnt = int(cnt_lit)
        actions_per_strategy[label] = cnt
        if cnt == 0:
            zero_action_strategies.append(label)

    # Owner workload
    q_owner_workload = (
        prefix
        + """
        SELECT ?owner (COUNT(?a) AS ?cnt)
        WHERE {
            ?a rdf:type ss:ActionTask .
            ?a ss:ownedBy ?owner .
        }
        GROUP BY ?owner
    """
    )
    for owner_lit, cnt_lit in cast(
        Iterable[Tuple[Any, Any]], g.query(q_owner_workload)
    ):
        owner = str(owner_lit)
        cnt = int(cnt_lit)
        owner_workload[owner] = cnt

    return {
        "actions_per_strategy": actions_per_strategy,
        "zero_action_strategies": zero_action_strategies,
        "owner_workload": owner_workload,
    }
