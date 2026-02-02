---
noteId: "1a39f870004b11f1b8fdb77554cd560f"
tags: []
title: "Strategy–Action Synchronization AI"
emoji: "🧭"
colorFrom: "indigo"
colorTo: "purple"
sdk: "streamlit"
app_file: "app/streamlit_app.py"
pinned: false

---

# Strategy–Action Synchronization AI

An MSc coursework project that evaluates how well an Action Plan aligns with a Strategic Plan using sentence embeddings, cosine similarity, and a persistent vector store. The system provides strategy-wise and overall synchronization metrics, weak-area identification, and rule-based recommendations — presented via a Streamlit dashboard.

## Explain Like I'm a Student (Step‑by‑Step)
- You give the app two lists in JSON: strategies and actions.
- We turn each strategy and action into a short, clean sentence (title + description + KPIs/outputs).
- We convert those sentences into vectors (lists of numbers) using an embedding model.
- We store all action vectors in a small database (ChromaDB) so we can search quickly.
- For each strategy, we search the most similar actions and compute an average score.
- We label alignment: Strong / Medium / Weak based on thresholds.
- We then generate suggestions in two ways:
  - If OpenAI API is available: call the LLM (e.g., GPT‑5) to produce structured recommendations.
  - If not: produce deterministic, rule‑based suggestions.
- Finally, we show results in a Streamlit dashboard and let you export JSON/CSVs.

## Problem Statement
Organizations often have well-written strategies but struggle to ensure execution truly aligns with intended outcomes. This project quantifies alignment between strategic objectives and action tasks, surfaces coverage gaps, and recommends improvements that are deterministic, explainable, and fit for academic evaluation.

## System Architecture
- **Data Layer**: JSON input for strategies and actions; persistent vector store in ChromaDB.
- **Embedding Layer**: SentenceTransformers (`all-MiniLM-L6-v2` by default) to create fixed‑length text embeddings.
- **Vector Store**: ChromaDB collection (`actions`) using cosine distance; converts to similarity.
- **Alignment Engine**: Per‑strategy top‑K retrieval, average of top‑3 similarities, label assignment, coverage.
- **RAG Suggestions**: Optional OpenAI call (if key present) that returns strict JSON; otherwise deterministic fallback.
- **UI/CLI**: Streamlit dashboard for exploration; Python CLI to batch‑run and save outputs.

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

## Run Locally (Step‑by‑Step)
1) Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```
3) (Optional) Enable OpenAI for RAG suggestions. Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-real-key
# Choose a model you have access to. Examples: gpt-5, gpt-4o, gpt-4o-mini
OPENAI_MODEL=gpt-5
```

Quick connectivity test:

```bash
python scripts/check_openai.py
```

4) Launch the Streamlit app:

```bash
streamlit run app/streamlit_app.py
```
Then, use the sample `data/strategic.json` and `data/action.json` or upload your own JSON arrays. Click “Run Synchronization” to view results and download outputs.

5) Run the CLI (batch, non‑UI) and save outputs:

```bash
python scripts/run_alignment.py
```
You’ll see overall metrics in the terminal, and a timestamped JSON under `outputs/`.

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

## Deploying to Hugging Face Spaces
- **Prereqs**: A Hugging Face account and a token with repo/Space create rights.
- **Auto-config**: This README includes the Spaces front matter (`sdk: streamlit`, `app_file: app/streamlit_app.py`).

### Via Web UI
- Create a Space at https://huggingface.co/new-space with SDK “Streamlit”.
- Upload the project files (requirements.txt, README.md, app/, src/, data/).
- Set Secrets in Space → Settings → Variables and secrets (e.g., `OPENAI_API_KEY`).

### Via CLI
Install and log in:

```bash
pip install -U huggingface_hub
hf auth login
```
Create the Space and push:

```bash
python -c "from huggingface_hub import create_repo; create_repo('YOUR_USERNAME/strategy-sync-ai', repo_type='space', space_sdk='streamlit', exist_ok=True)"
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/strategy-sync-ai
git push hf main
```

### Secrets to Configure
- `OPENAI_API_KEY`: Needed if LLM-based features are enabled.
- `OPENAI_MODEL`: Set to a model available to your account (e.g., `gpt-5`, `gpt-4o`, `gpt-4o-mini`).
- Additional keys referenced by `.env` should be added via Spaces Secrets, not committed.

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

## Troubleshooting
- 401 invalid_api_key: The key is missing/placeholder/revoked. Update `.env` and retry `python scripts/check_openai.py`.
- Unsupported parameter (temperature / max_tokens): Some models restrict params. The code avoids these in RAG and the check script.
- Proxy/network errors: Temporarily unset proxies: `unset HTTP_PROXY HTTPS_PROXY ALL_PROXY` and retry.
- Tokenizers fork warning: Set `TOKENIZERS_PARALLELISM=false` to silence.

## Dev Quick Commands
```bash
# Activate venv and install deps
source .venv/bin/activate
python -m pip install -r requirements.txt

# Run tests
python -m pip install pytest
python -m pytest -q

# Run alignment CLI (no API key → deterministic RAG)
python scripts/run_alignment.py
```