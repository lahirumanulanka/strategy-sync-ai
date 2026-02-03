# Evaluation of Strategy–Action Synchronization AI

This document presents a comprehensive, practitioner-focused evaluation of the Strategy–Action Synchronization AI system. It explains the rationale, metrics, methodology, and how results should be interpreted for both academic assessment and real-world use. The system aligns strategic objectives with action tasks using sentence embeddings, vector search (ChromaDB), and optional RAG-based recommendations, producing dashboards and JSON outputs that can be audited.

## Goals and Scope

- Assess the retrieval quality of the alignment engine that maps each strategy to its most relevant action tasks.
- Provide repeatable metrics (Precision@K, Recall@K, MAP, NDCG) that are standard in information retrieval courses and industry.
- Offer guidance on constructing ground truth, running evaluations, and understanding trade-offs.

This evaluation focuses on the core alignment capability implemented in the codebase, rather than business outcomes like cost savings or cycle-time improvements (these may be added later as KPI evaluations).

## Data and Ground Truth

The project includes sample JSON data under `data/`. To evaluate properly, you must supply ground truth relevance judgments — for each strategy ID, list the action IDs that are considered relevant in your domain context. A template is provided:

- `data/ground_truth.example.json` illustrates the expected structure: `{ "S1": ["A1", "A2"], ... }`.
- Create `data/ground_truth.json` from the template and edit mappings based on subject matter expertise, prior documentation, or stakeholder review.

Ground truth is binary relevance at present (an action is relevant or not). If you need graded relevance (e.g., highly relevant vs somewhat relevant), the evaluation module can be extended to accommodate graded labels for more nuanced metrics like NDCG with graded gains.

## Metrics

The following retrieval metrics are implemented in `src/evaluation.py` and reported both per-strategy and as macro averages:

- **Precision@K**: Of the top-K actions returned, what fraction are relevant? High precision indicates fewer false positives.
- **Recall@K**: Of all relevant actions, what fraction appear in the top-K? High recall indicates fewer false negatives.
- **Average Precision (AP) and MAP**: AP averages precision at each rank where a relevant item occurs; MAP is the mean AP over strategies. MAP rewards systems that rank relevant actions early.
- **NDCG@K**: Normalized Discounted Cumulative Gain at K using binary relevance (gain=1). This emphasizes early retrieval of relevant actions while normalizing by the best possible ranking.

These metrics together cover different aspects of ranking quality: accuracy at the top results (Precision), coverage of known relevant items (Recall), and overall ranking quality (MAP/NDCG).

## Methodology

1. **Embedding and Indexing**: The system uses `SentenceTransformer` to encode action tasks into normalized embeddings. It upserts them into a ChromaDB collection configured with cosine space.
2. **Retrieval**: For each strategy, the system embeds the strategy’s text and queries ChromaDB for top-K nearest neighbors by cosine distance (converted to similarity). The default K is 5; you can change it in evaluation config.
3. **Metric Calculation**:
   - Extract the ranked action IDs for each strategy.
   - Compare against ground truth action IDs for that strategy.
   - Compute P@K, R@K, AP, and NDCG per strategy; then average across strategies for macro scores.

This process isolates retrieval performance independently of downstream RAG suggestions, UI, or visualization.

## Running the Evaluation

The repository provides two convenient ways:

- From `main.py` subcommand:
  ```bash
  cp data/ground_truth.example.json data/ground_truth.json
  # Edit data/ground_truth.json to reflect true relevance
  /Users/lahirumunasinghe/Documents/DataScience/strategy-sync-ai/.venv/bin/python main.py eval
  ```

- Direct script:
  ```bash
  /Users/lahirumunasinghe/Documents/DataScience/strategy-sync-ai/.venv/bin/python scripts/run_evaluation.py
  ```

The output prints macro metrics and per-strategy lines like:
```
Top-K: 5
Macro Precision: 0.600
Macro Recall:    0.500
MAP:             0.550
Mean NDCG:       0.620

S1: P@5=0.600 | R@5=0.750 | AP=0.700 | NDCG=0.720
...
```
(Values are illustrative; actual numbers depend on your data and ground truth.)

## Interpreting Results

- **Precision vs Recall**: If precision is high but recall is low, the system is conservative (few false positives) but may miss relevant actions. If recall is high and precision low, it over-includes actions (requires filtering).
- **MAP and NDCG**: These summarize ranking quality. Improving embedding quality or domain-specific text representations (e.g., adding structured fields) should raise these scores.
- **Threshold Labels**: The alignment engine also maps continuous similarity to labels (Strong/Medium/Weak). These labels are not used directly in IR metrics but can be converted into classification metrics (e.g., confusion matrices) if you set thresholds tied to relevance.

## Design Choices and Trade-offs

- **Cosine Similarity**: Using cosine space is standard for sentence embeddings; converting distance to similarity (`1 - distance`) yields an intuitive 0–1 scale.
- **Top-K**: Defaults to 5 to keep evaluation tight; consider K=3 or K=10 depending on expected action set sizes.
- **Binary Relevance**: Simple to start; graded relevance captures richer reality. Extend `evaluation.py` to accept relevance weights (e.g., 0, 1, 2) and use graded gains in NDCG.
- **Text Representation**: Strategy and action text are built from fields like title, description, owner, and dates. Adding structured signals (KPIs, categories, tags) may improve retrieval quality.

## Improving Performance

- **Better Embeddings**: Try domain-specific models (e.g., `sentence-transformers/all-mpnet-base-v2`) or task-tuned models.
- **Prompt Augmentation**: Concatenate additional fields into the action text (e.g., outputs, milestones) to supply richer context to the encoder.
- **Vector Store Tuning**: Experiment with HNSW parameters or re-ranking with cross-encoders for better top-K ordering.
- **Calibrate Thresholds**: Derive Strong/Medium/Weak thresholds by analyzing metric distributions on your ground truth.
- **Error Analysis**: Inspect false positives and false negatives to identify patterns (ambiguous titles, missing descriptions) and improve data hygiene.

## Limitations

- **Small Dataset Bias**: With few strategies/actions, metrics can be volatile; consider bootstrapping or cross-validation.
- **Ground Truth Subjectivity**: Relevance varies by stakeholder; document your criteria and aim for consensus.
- **Cold Start**: New actions with sparse text can be hard to match; enrich descriptions.

## Future Extensions

- **MRR and Recall@{1,3,5}**: Add more point metrics for quick diagnostics.
- **Confusion Matrix**: If you adopt label-based relevance (e.g., Strong=Relevant), compute classification metrics alongside retrieval metrics.
- **Temporal and Ownership Signals**: Incorporate dates and owners into ranking, penalizing misaligned schedules or unclear ownership.
- **Graph-Aided Evaluation**: Evaluate coherence using the RDF graph (e.g., density of `hasAction` edges for each strategy) in addition to IR metrics.

## Summary

The evaluation framework provides a solid, transparent basis to judge alignment quality. With ground truth in place, you can run the evaluation repeatedly, track improvements, and justify design decisions. This approach aligns with MSc Information Retrieval expectations while remaining practical for production decision support.
