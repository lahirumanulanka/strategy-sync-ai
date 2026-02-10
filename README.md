---
title: Strategy Sync AI
emoji: 📊
colorFrom: blue
colorTo: purple
sdk: streamlit
app_file: app/streamlit_app.py
pinned: false
---

# Strategy–Action Synchronization AI  
### Intelligent Strategic Plan Synchronization System (ISPS)

---

## 1. Introduction

This project is developed as part of the **MSc in Computer Science – Information Retrieval** coursework (2024 Batch).

Organizations typically document **Strategic Plans** (long-term goals) and **Action Plans** (operational tasks) as separate artifacts. Due to differences in abstraction level, terminology, and document structure, it becomes difficult to objectively verify whether execution genuinely supports strategy.

The **Strategy–Action Synchronization AI (ISPS)** system addresses this gap by applying **Information Retrieval (IR)** and **Natural Language Processing (NLP)** techniques to automatically evaluate how well an organization’s action plans align with its strategic objectives.

The system leverages:
- Sentence embeddings for semantic understanding
- Vector similarity search for alignment detection
- Deterministic scoring logic for academic reproducibility
- Optional Retrieval-Augmented Generation (RAG) for recommendations
- Interactive dashboards for explainability and decision support

---

## 2. Problem Background

Organizations face multiple challenges when aligning strategy and execution:

- Strategic objectives are high-level and abstract
- Action plans are operational and detailed
- Manual alignment reviews are subjective and error-prone
- Large documents are difficult to analyze consistently
- Keyword-based matching fails due to vocabulary mismatch

Traditional text matching techniques are insufficient because:
- Different wording may express the same intent
- Semantic relationships are ignored
- Important contextual meaning is lost

This project adopts **semantic similarity-based alignment** instead of keyword overlap, enabling a more robust and explainable evaluation.

---

## 3. System Objectives

The primary objectives of the ISPS system are:

1. Quantitatively measure alignment between Strategic and Action Plans  
2. Analyze alignment at both global and per-strategy levels  
3. Identify weakly supported or unsupported strategies  
4. Generate explainable improvement recommendations  
5. Visualize insights through an interactive dashboard  
6. Maintain deterministic and reproducible behavior suitable for academic evaluation  

---

## 4. Updated System Architecture (End-to-End)

The system follows a **layered and pipeline-driven architecture**, ensuring modularity, transparency, and extensibility.

### 4.1 High-Level Pipeline Flow

Strategic Plan (JSON / PDF)  
+  
Action Plan (JSON / PDF)  
↓  
Text Preprocessing & Normalization  
↓  
Sentence Embedding Generation  
↓  
Vector Database (ChromaDB)  
↓  
Strategy–Action Similarity Retrieval (Top-K)  
↓  
Alignment Scoring & Coverage Computation  
↓  
Recommendation Generation (LLM or Deterministic)  
↓  
Graph Construction (Strategy–Action Relationships)  
↓  
Evaluation Against Ground Truth (Optional)  
↓  
Streamlit Dashboard & Exportable Reports  

---

### 4.2 Architectural Benefits

This architecture provides:

- Clear separation of concerns  
- Reusability across CLI, UI, and batch pipelines  
- Explainability for academic assessment  
- Support for both AI-driven and deterministic logic  
- Easy extension toward knowledge graphs and ontologies  

---

## 5. Project Directory Structure

strategy-sync-ai/
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── alignment.py
│   ├── models.py
│   ├── text_utils.py
│   ├── vector_store.py
│   ├── recommendations.py
│   ├── rag_engine.py
│   ├── pdf_to_json.py
│   ├── pipeline.py
│   ├── viz.py
│   └── io_utils.py
│
├── data/
│   ├── strategic.json
│   └── action.json
│
├── chroma_db/
│
├── outputs/
│
├── scripts/
│   ├── check_openai.py
│   └── run_alignment.py
│   └── run_full_flow.py
│
├── tests/
│
├── docs/
│   ├── Ontology.md
│   ├── Evaluation.md
│   ├── System_Architecture.md
│   └── ontology.ttl
│
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore

---

## 6. Component-Level Explanation

### 6.1 User Interface Layer (`app/`)

**File:** `streamlit_app.py`

- Implements the interactive dashboard using Streamlit
- Allows users to:
  - Upload strategic and action data
  - Run synchronization analysis
  - View charts and tables
  - Download results as JSON or CSV

This layer only **displays results** and does not perform AI logic.

---

### 6.2 Data Modeling & Preprocessing (`src/models.py`, `src/text_utils.py`)

- Structured inputs (title, description, KPIs) are converted into **clean sentences**
- This improves embedding quality and reduces noise
- Ensures consistent text representation

---

### 6.3 Embedding Layer (`SentenceTransformers`)

- Uses `all-MiniLM-L6-v2`
- Converts each strategy and action into a numerical vector
- Captures semantic meaning rather than keywords

---

### 6.4 Vector Storage Layer (`src/vector_store.py`)

- Uses **ChromaDB** as a persistent vector database
- Stores action embeddings
- Enables fast cosine similarity search
- Avoids recomputation across multiple runs

---

### 6.5 Synchronization & Alignment Engine (`src/alignment.py`)

For each strategy:
1. Generate embedding
2. Retrieve top-K similar actions
3. Select top 3 matches
4. Compute average similarity score

#### Alignment Labels

| Score Range | Label  |
|------------|--------|
| ≥ 0.75     | Strong |
| ≥ 0.55     | Medium |
| < 0.55     | Weak   |

#### Overall Metrics
- **Overall Score:** Mean of strategy scores (scaled to 0–100)
- **Coverage:** Percentage of strategies supported by at least two strong actions

This logic is **deterministic and explainable**, which is important for academic evaluation.

---

### 6.5b End-to-End Pipeline (`src/pipeline.py`)

The unified orchestrator `run_full_flow(strategic_path, action_path, ground_truth_path=None, top_k=5, rebuild_index=False)` executes alignment, builds the RDF graph, computes SPARQL-based stats, and (optionally) runs evaluation when ground truth is provided. CLI access via `python main.py full-run ...`.

---

### 6.6 Recommendation Layer (`src/recommendations.py`, `src/rag_engine.py`)

The system supports **two recommendation modes**:

#### LLM-Based Mode
- Uses OpenAI API (if available)
- Generates structured improvement suggestions
- Uses retrieved context (RAG-style)

#### Deterministic Fallback Mode
- Rule-based logic
- Works without any external API
- Ensures reproducibility and fairness

Suggestions include:
- Missing actions
- Weak KPI coverage
- Timeline or ownership gaps

---

### 6.7 PDF to JSON Conversion (`src/pdf_to_json.py`)

- Allows strategic and action plans to be uploaded as PDFs
- Extracts text and converts it into structured JSON
- Bridges real-world documents with AI processing

---

## 7. Visualization Layer (`src/viz.py`)

The dashboard includes:
- Overall synchronization gauge
- Strategy-wise bar charts
- Alignment distribution pie chart
- Heatmaps of similarity scores
- Expandable strategy–action mappings

These visualizations help non-technical users understand results easily.

---

## 8. Running the System

### 8.1 Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

8.2 Run Dashboard
streamlit run app/streamlit_app.py

8.3 Run CLI Mode
python scripts/run_alignment.py

8.4 End-to-End Full Pipeline (Graph + Evaluation)

Run the unified pipeline that orchestrates alignment, graph construction, and optional evaluation:

```
python main.py full-run data/strategic.json data/action.json --ground_truth_path data/ground_truth.json --top_k 5
```

Outputs:
- Final report JSON in `outputs/` (includes overall score, coverage, per-strategy results, graph stats, and optional evaluation)
- RDF/Turtle graph: `outputs/strategy_graph.ttl`
- Optional `evaluation` section in the final report when ground truth is provided

Streamlit Tabs:
- Overview and Strategy Explorer
- Graph (shows TTL path and SPARQL-based stats)
- Evaluation (macro + per-strategy metrics if ground truth is supplied)

---

## 9. Features

- Alignment Engine with semantic embeddings and cosine similarity
- Persistent vector store (ChromaDB) with resilient initialization
- RDF knowledge graph with `ss:Strategy`, `ss:ActionTask`, and `ss:hasAction`
- SPARQL stats for explainability (actions per strategy, owner workload, gaps)
- Evaluation metrics: Precision@K, Recall@K, MAP, NDCG
- Streamlit dashboard with interactive charts and exports
- Deterministic recommendations with optional LLM‑backed RAG

## 10. Evaluation Strategy

To ensure the correctness, reliability, and academic validity of the system, multiple evaluation approaches are considered.

### 9.1 Manual Ground-Truth Mapping
A subset of strategies and actions can be manually mapped by the student or a domain expert to establish a **ground-truth alignment**.  
The system-generated matches are then compared against this reference mapping to verify semantic correctness.

### 9.2 Expert Validation
Recommendations generated by the system, especially for weakly aligned strategies, can be reviewed by:
- Academic supervisors
- Industry practitioners
- Subject matter experts

This qualitative evaluation helps assess whether the suggested improvements are realistic and actionable.

### 9.3 Precision and Recall
Information Retrieval metrics are applied to strategy–action matching:
- **Precision** measures how many retrieved actions are truly relevant to a strategy.
- **Recall** measures how many relevant actions are successfully retrieved.

These metrics help evaluate the effectiveness of embedding-based similarity matching.

### 9.4 Stability of Similarity Scores
The system is tested across multiple runs using the same input data to confirm that:
- Similarity scores remain stable
- Alignment labels are consistent

This ensures deterministic behavior suitable for academic assessment.

---

## 11. Deployment

The application is designed to support both local execution and public deployment.

### 10.1 Supported Hosting Platforms
The system can be deployed using:
- **Hugging Face Spaces** (Streamlit-based hosting)
- **Streamlit Community Cloud**
- **Cloud Virtual Machines** (AWS, Azure, or similar platforms)

### 10.2 Public Deployment
The project is publicly hosted on Hugging Face Spaces at the following link:

🔗 **Live Application:**  
https://huggingface.co/spaces/hirumunasinghe/strategy-sync-ai

This hosted version allows evaluators to interact with the system without local setup.

### 10.3 Security Considerations
- API keys (e.g., OpenAI) are managed using **environment variables**
- Secrets are not hard-coded or committed to the repository
- This approach supports basic security and good software engineering practices

---

## 12. Academic Contribution

This project demonstrates several key academic and practical contributions:

- Practical application of **Information Retrieval techniques**
- Use of **semantic similarity through sentence embeddings**
- Integration of a **vector database** for efficient retrieval
- Design of an **explainable and deterministic AI system**
- Development of a **real-world decision support tool**

The system design, implementation, and evaluation align closely with the **MSc Information Retrieval coursework marking rubric**, particularly in system architecture, intelligent features, and dashboard usability.

---

## 13. Future Enhancements

Several enhancements can be explored to extend the system further:

- **Ontology-based strategy mapping** to capture hierarchical relationships
- **Knowledge graph visualization** for strategy–action dependencies
- **KPI-weighted similarity scoring** to prioritize critical objectives
- **Agentic AI reasoning layer** for autonomous improvement exploration
- **Temporal dependency analysis** to evaluate schedule and milestone alignment
 - **Ground truth validators** in UI to warn on unknown IDs
 - **One-click vector store reset** button for local troubleshooting

These improvements provide clear directions for future research and development.

---

## 14. Author

**Lahiru Munasinghe**  
MSc in Computer Science – Information Retrieval  
2024 Batch

---

Notes:
- ChromaDB telemetry is disabled by default for cleaner local runs.
- The vector store initialization includes tenant/database defaults and a fallback to a local client if persistent storage cannot be established (e.g., read-only sqlite environments), ensuring Streamlit and CLI runs remain resilient.

---

## Troubleshooting

- Prefer running in a virtual environment to avoid system package conflicts:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- If you see sqlite or tenant errors from ChromaDB, the app automatically falls back to a local (non-persistent) client so you can continue. For a clean rebuild locally, stop the app and remove the `chroma_db/` folder.
- If evaluation returns zeros, verify `data/ground_truth.json` IDs match your actions. Use `data/ground_truth.example.json` as a template.