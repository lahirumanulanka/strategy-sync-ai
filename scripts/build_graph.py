from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import ontology  # noqa: E402
try:
    build_graph_from_files = ontology.build_graph_from_files
except AttributeError:
    build_graph_from_files = ontology.build_graph
save_graph = ontology.save_graph

ONTOLOGY = ROOT / "docs" / "ontology.ttl"
STRATEGY_JSON = ROOT / "data" / "strategic.json"
ACTION_JSON = ROOT / "data" / "action.json"
OUTPUT_TTL = ROOT / "outputs" / "strategy_graph.ttl"


def main() -> None:
    g = build_graph_from_files(ONTOLOGY, STRATEGY_JSON, ACTION_JSON)
    out = save_graph(g, OUTPUT_TTL, fmt="turtle")
    print(f"Saved RDF graph to: {out}")
    print(f"Triples count: {len(g)}")


if __name__ == "__main__":
    main()
