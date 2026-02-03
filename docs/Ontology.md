# Ontology and Knowledge Graph for Strategy–Action Synchronization

This document explains the ontology and knowledge graph design used to represent strategies, actions, and their relationships in the Strategy–Action Synchronization AI system. It covers goals, modeling decisions, RDF/Turtle implementation, integration with the alignment engine, and practical ways to inspect and query the graph.

## Why a Knowledge Graph?

A knowledge graph complements embedding-based retrieval by offering a structured representation of relationships and attributes. It enables:

- **Explicit links** from strategies to actions (`hasAction`).
- **Attributes** like ownership and timelines for actions.
- **Auditable provenance**: you can trace why a strategy is linked to an action.
- **Visualization and analytics**: graph queries reveal coverage, gaps, and dependencies.

Using an ontology ensures consistent semantics of classes and properties and supports tooling like Protégé and SPARQL.

## Modeling Overview

The ontology is minimal and pragmatic, tailored to the current dataset and system goals. It’s implemented in RDF/Turtle in `docs/ontology.ttl`.

### Core Classes

- **Strategy**: A strategic objective with a label and optional KPI relations.
- **ActionTask**: An actionable task with label, owner, start and end dates.

### Properties

- **hasAction** (`Strategy → ActionTask`): Links a strategy to actions intended to deliver it.
- **ownedBy** (`ActionTask → xsd:string`): Captures task ownership (team or person).
- **startDate / endDate** (`ActionTask → xsd:date`): Timeline attributes.
- **relatesToKPI** (`Strategy → xsd:string`): Associates strategies with KPI labels.
- **broader** (`Strategy → Strategy`): Optional hierarchical relation for strategy roll-ups (similar to SKOS `broader`).

These choices keep the graph compact while enabling useful queries. You can introduce additional properties (e.g., `dependsOn`, `riskLevel`, `category`) as the project evolves.

## Implementation in the Repository

- **Ontology file**: `docs/ontology.ttl`
- **Graph builder**: `src/ontology.py` contains functions to load the base ontology, add instances from JSON (`load_strategies`, `load_actions`), and link strategies to actions.
- **Runner scripts**: `scripts/build_graph.py` builds the graph and saves `outputs/strategy_graph.ttl`; `scripts/query_graph.py` prints counts and samples.

URIs are minting as:
- Strategies: `http://example.org/strategy-sync/strategy/{strategy_id}`
- Actions: `http://example.org/strategy-sync/action/{action_id}`

The base namespace is `http://example.org/strategy-sync#` (prefix `ss:`).

## Linking Strategies to Actions

The scaffold currently links all strategies to all actions to demonstrate end-to-end graph functionality. In production, you should replace this with top-K links from the `AlignmentEngine`:

1. Embed each strategy and retrieve top-K actions (as done in alignment).
2. Add `ss:hasAction` edges only for those matches (optionally thresholded by similarity).
3. Optionally encode similarity as a data property (e.g., `ss:hasSimilarity`) or as edge attributes in a property graph if exporting to Neo4j.

This integration ensures the graph reflects actual alignment results and can be audited against evaluation metrics.

## Inspecting and Querying the Graph

### Protégé

- Open both `docs/ontology.ttl` and `outputs/strategy_graph.ttl`.
- Check Individuals for `ss:Strategy` and `ss:ActionTask`.
- Verify property assertions like `ss:hasAction`, `ss:ownedBy`, `ss:startDate`, `ss:endDate`.

### SPARQL Examples

List strategies and their actions:
```sparql
PREFIX ss: <http://example.org/strategy-sync#>
SELECT ?strategy ?action WHERE {
  ?strategy ss:hasAction ?action .
} LIMIT 20
```

Count actions per strategy:
```sparql
PREFIX ss: <http://example.org/strategy-sync#>
SELECT ?strategy (COUNT(?action) AS ?n) WHERE {
  ?strategy ss:hasAction ?action .
} GROUP BY ?strategy ORDER BY DESC(?n)
```

Find actions with owners and timelines:
```sparql
PREFIX ss: <http://example.org/strategy-sync#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?action ?label ?owner ?start ?end WHERE {
  ?action a ss:ActionTask ;
          rdfs:label ?label ;
          ss:ownedBy ?owner .
  OPTIONAL { ?action ss:startDate ?start }
  OPTIONAL { ?action ss:endDate ?end }
} LIMIT 20
```

These queries help verify graph completeness and expose coverage issues (e.g., actions without owners or dates).

## Design Rationale

- **RDF/Turtle**: Interoperable, simple text format, excellent tooling (rdflib, Protégé) for MSc/IR workflows.
- **Minimal Schema**: Avoid over-modeling early; add fields incrementally as needed. The graph is primarily a traceability and auditing layer for alignment results.
- **Human-Readable Labels**: Use `rdfs:label` for display-friendly names; keep URIs stable.
- **Dates and Ownership**: Critical operational attributes for governance and aligning timelines to strategic milestones.

## Export and Visualization

- **Neo4j Export**: Convert TTL to CSVs (nodes and edges) or script with `py2neo` to import into Neo4j; then use Bloom or Graph Data Science for visualization and analytics.
- **PyVis/Graphviz**: For lightweight local visualization, export to an HTML network graph; color nodes by class and size by degree.
- **Dashboards**: Summaries from SPARQL can feed the Streamlit UI to show action coverage and ownership distribution.

## Integration with Evaluation

Graph structure can support evaluation beyond IR metrics:

- **Coverage**: Percentage of strategies with at least N linked actions.
- **Degree Distribution**: Strategies with too few actions highlight delivery risks; overly connected strategies may indicate action duplication.
- **Temporal Alignment**: Compare strategy timelines (if modeled) with action dates to flag scheduling conflicts.

Combining IR metrics with graph analytics yields a richer picture of system quality.

## Future Enhancements

- **Graded Relevance**: Store relevance levels as data properties or reification to support graded NDCG.
- **Provenance**: Add metadata (e.g., `ss:derivedFrom`) to explain why links exist (embedding score, human review).
- **Taxonomies**: Introduce categories (e.g., finance, operations) as SKOS concepts; link strategies/actions to concepts for faceted exploration.
- **Constraints**: Shape validation (SHACL) to enforce required properties (owner, timelines) and flag incomplete entries.

## How to Use in This Project

1. Build the graph:
   ```bash
   /Users/lahirumunasinghe/Documents/DataScience/strategy-sync-ai/.venv/bin/python main.py graph
   ```
2. Query sample stats:
   ```bash
   /Users/lahirumunasinghe/Documents/DataScience/strategy-sync-ai/.venv/bin/python main.py graph-query
   ```
3. Inspect in Protégé by loading `docs/ontology.ttl` and `outputs/strategy_graph.ttl`.
4. (Optional) Integrate with alignment results by linking only top-K actions per strategy.

## Summary

The ontology and knowledge graph provide a structured, inspectable backbone for the Strategy–Action Synchronization AI. They make relationships explicit, support auditing and visualization, and can evolve with the system’s complexity. By integrating graph links with alignment outputs and evaluation metrics, you create a robust, explainable system that satisfies academic rigor and practical governance needs.
