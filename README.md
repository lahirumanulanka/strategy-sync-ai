# Strategy–Action Synchronization AI

An MSc coursework project that evaluates how well an Action Plan aligns with a Strategic Plan using sentence embeddings, cosine similarity, and a persistent vector store. The system provides strategy-wise and overall synchronization metrics, weak-area identification, and rule-based recommendations — presented via a Streamlit dashboard.

## Problem Statement
Organizations often have well-written strategies but struggle to ensure execution truly aligns with intended outcomes. This project quantifies alignment between strategic objectives and action tasks, surfaces coverage gaps, and recommends improvements that are deterministic, explainable, and fit for academic evaluation.

## System Architecture
- **Data Layer**: JSON input for strategies and actions; persistent vector store in ChromaDB.
- **Embedding Layer**: SentenceTransformers (`all-MiniLM-L6-v2`) to create fixed-length text embeddings.
- **Alignment Engine**: Cosine similarity search over action embeddings; per-strategy top-K matching, averaged top-3 alignment, and coverage.
- **Recommendations**: Rule-based suggestions tailored to alignment strength (Weak/Medium/Strong).
- **UI**: Streamlit app with Plotly visualizations, multi-tab dashboard, and JSON/CSV export.

```
strategic.json + action.json → models → text_utils → embeddings → ChromaDB → alignment → recommendations → Streamlit UI
```

## AI Techniques Used
- **Text Embeddings**: SentenceTransformers for semantically meaningful vectorization.
- **Vector Search**: ChromaDB persistent collection with cosine distance.
- **Deterministic Rules**: Threshold-based labels (Strong/Medium/Weak) and rule-based recommendations for explainability.

## How Synchronization Is Calculated
- **Strategy-to-Action Matching**: For each strategy, generate embedding and query top-K similar action embeddings.
- **Per-Strategy Average**: Average of the top-3 similarity scores → `avg_top3_similarity`.
- **Labels**: `Strong (≥0.75)`, `Medium (≥0.55)`, else `Weak`.
- **Overall Score**: Mean of per-strategy averages scaled to 0–100.
- **Coverage**: Percentage of strategies with at least 2 actions labeled `Strong`.

Rationale: Top-3 averaging balances noise and outliers, providing a stable estimate of practical alignment to multiple actionable tasks.

## Project Structure
```
app/
  streamlit_app.py
src/
  models.py
  text_utils.py
  vector_store.py
  alignment.py
  recommendations.py
data/
  strategic.json
  action.json
outputs/
chroma_db/
requirements.txt
README.md
.gitignore
```

## How to Run
1. Create and activate a Python 3.10+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```
3. Launch the Streamlit app:

```bash
streamlit run app/streamlit_app.py
```
4. Use sample data or upload your own JSON arrays; click **Run Synchronization** to view results and download the output JSON.

## Visualizations & Dashboard
- **Overview Tab**: Gauge charts for Overall Score and Coverage; bar chart of per-strategy average similarity; pie chart of alignment labels; heatmap of top-match similarities; owner workload bar.
- **Strategy Explorer Tab**: Ranked strategy table and long-form matches table; per-strategy expanders with top-match details.
- **RAG Suggestions Tab**: Optional LLM recommendations (if enabled) or deterministic rule-based suggestions.
- **Data Export Tab**: Download combined JSON plus CSVs for strategies and matches.

## Future Improvements
- **Model Choice**: Configurable embedding models and accuracy/latency trade-offs.
- **Weighting**: KPI-weighted similarity or strategy priority weighting.
- **Temporal Logic**: Advanced schedule alignment (e.g., critical path coverage).
- **Explainability**: Salient phrase extraction to justify match scores.
- **Data Validations**: Schema checks and user feedback for malformed inputs.
- **Ops**: Containerization and small CI checks (lint/type).

## MSc Submission Tips
- **Screenshots**: 
  - Home screen with description and toggles
  - Strategy-wise alignment table
  - A few expanders showing detailed matches
  - Metrics for Overall Score and Coverage
  - Recommendations section
  - Download prompt + saved JSON file in `outputs/`
- **Outputs**: Include one exported JSON and a short narrative interpreting results.
- **Explanations**: Emphasize deterministic thresholds, average-of-top-3 reasoning, and coverage definition; discuss model limitations and proposed mitigations.
