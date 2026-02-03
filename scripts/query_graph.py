from pathlib import Path

from rdflib import Graph, Namespace, RDF

ROOT = Path(__file__).resolve().parent.parent
TTL = ROOT / "outputs" / "strategy_graph.ttl"
SS = Namespace("http://example.org/strategy-sync#")


def main() -> None:
    g = Graph()
    g.parse(str(TTL), format="turtle")
    print(f"Loaded: {TTL}")
    print(f"Total triples: {len(g)}")

    strategies = list(g.subjects(RDF.type, SS.Strategy))
    actions = list(g.subjects(RDF.type, SS.ActionTask))
    links = list(g.triples((None, SS.hasAction, None)))

    print(f"Strategies: {len(strategies)}")
    print(f"Actions:    {len(actions)}")
    print(f"hasAction links: {len(links)}")

    # Show a couple of examples
    print("\nSample Strategy URIs:")
    for s in strategies[:3]:
        print(f"- {s}")

    print("\nSample Action URIs:")
    for a in actions[:3]:
        print(f"- {a}")

    print("\nSample links (Strategy -> Action):")
    for s, _, a in links[:5]:
        print(f"- {s} -> {a}")


if __name__ == "__main__":
    main()
