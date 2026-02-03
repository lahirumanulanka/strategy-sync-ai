# System Architecture Overview

See the full topology diagram in `.azure/architecture.copilotmd` for a renderable Mermaid diagram and detailed data-flow notes.

## Components
- `strategy-sync-app` (Streamlit): UI, orchestration, exports
- `AlignmentEngine`: sentence embeddings, vector store indexing/query
- `RAGEngine`: prompt construction, optional Azure OpenAI invocation, deterministic fallback
- Persistent storage: outputs JSON/CSV; optional cloud storage
- Telemetry: Application Insights (optional)
- Secrets: Key Vault (optional)

## Data Flow Summary
1. Ingest strategic and action plans (JSON/PDF)  
2. Embed and index actions; compute top-K matches per strategy  
3. Derive per-strategy averages, overall score, coverage  
4. Generate recommendations (RAG or fallback)  
5. Visualize in dashboard; export results

---

## Extended Architecture (Comprehensive)

### Purpose and Design Principles
The Strategy–Action Synchronization AI (SAS-AI) architecture is designed to reliably translate strategic intents into measurable execution signals. It does this by combining semantic similarity techniques, a persistent vector store, and optional Retrieval-Augmented Generation (RAG) to generate actionable recommendations. Key principles guiding the architecture include:
- **Modularity:** Clear separation between UI, alignment computation, storage, and recommendation logic enables focused iteration and testing.
- **Deterministic Core:** Even without an LLM, the system provides deterministic recommendations and stable alignment outputs to support governance and reproducibility.
- **Observability:** Instrumentation points (optional Application Insights) support monitoring of performance, usage, and anomalies.
- **Security & Secrets:** Environment variables and optional Azure Key Vault safeguard credentials and configuration.
- **Deployability:** The app can run locally, in Streamlit Cloud, or in containerized environments (e.g., Azure Container Apps). This supports both rapid prototyping and production hardening.

### Component Overview
- **`strategy-sync-app` (Streamlit):** The user interface orchestrates ingestion of strategic and action plans, triggers alignment runs, renders visualizations (gauges, bars, pie charts, heatmaps), and provides export options. It also toggles RAG usage and handles uploaded PDFs via conversion.
- **`AlignmentEngine`:** Handles embedding and indexing of actions, followed by query-time retrieval based on strategy text. It applies thresholds to derive categorical labels (Weak, Medium, Strong) and computes quantitative metrics (Overall Score, Coverage %). The engine isolates the scoring logic and the persistence interactions with the vector store, keeping it testable.
- **`RAGEngine`:** Encapsulates prompt construction and optional calls to Azure OpenAI via the OpenAI Python client. It enforces a structured response format. If the LLM is unavailable or errors occur, it provides deterministic fallback suggestions, ensuring that recommendations are always present.
- **Vector Store (ChromaDB):** Stores action embeddings in a persistent collection using HNSW for efficient approximate nearest neighbor search. This preserves indexing work across runs, improves query latency, and supports incremental updates.
- **Data Layer & Exports:** Inputs come from JSON or PDF; the app writes outputs (alignment results and recommendations) to `outputs/` with timestamped filenames. CSV exports for strategies and matches facilitate analysis in spreadsheet tools or BI platforms.
- **Observability (optional):** Azure Application Insights can be used to gather telemetry on usage, latency, and errors. This supports performance tuning and reliability improvements.
- **Secrets Management (optional):** Azure Key Vault secures API keys and sensitive configuration. The app accesses secrets through environment variables or managed identities in production.

### Data Ingestion and Schema
The app supports two main ingestion paths:
1. **JSON Uploads:** Users can upload structured JSON lists for both strategic objectives and action tasks. These are validated to ensure list shape and key presence. The code constructs domain objects (`StrategicObjective`, `ActionTask`) with fields like `id`, `title`, `description`, `owner`, `start_date`, and `end_date`.
2. **PDF Uploads:** When PDFs are uploaded, the app invokes parsers (`parse_strategic_pdf`, `parse_action_pdf`) to convert the documents into JSON-like structures. This creates an ingestion path for real-world content while preserving downstream consistency.

### Embeddings, Indexing, and Retrieval
SAS-AI uses `sentence-transformers/all-MiniLM-L6-v2`, a compact and well-established model offering strong semantic performance at minimal computational cost. The `AlignmentEngine` normalizes embeddings to support stable cosine similarity behavior.

Actions are upserted into the ChromaDB collection with a durable `persist_directory` (`chroma_db/`). Metadata such as title, owner, and dates are included to enrich the query response. HNSW indexing yields fast approximate nearest neighbor results with favorable memory characteristics.

At query time, each strategy is embedded, and the vector store is queried for top-K matches. The app captures similarity scores for each match, and the engine applies thresholds to label each match. This is the foundation for the labels displayed in the dashboard and the quantitative metrics reported.

### Alignment Metrics and Thresholding
The architecture implements two complementary metrics:
- **Per-Strategy Average (Top-3):** For each strategy, the app takes the three highest similarity scores and computes an average. This average emphasizes the strongest alignments and reduces sensitivity to noise from weaker matches.
- **Overall Score:** The mean of per-strategy averages multiplied by 100 for a percentage-like presentation. This provides leadership with a single headline indicator of alignment health.
- **Coverage Percent:** The percentage of strategies with at least two “Strong” matches (similarity ≥ 0.75). This reflects the breadth of strong alignment across the portfolio, avoiding a focus solely on the highest-scoring strategies.

Thresholds are configurable and default to 0.55 (Medium) and 0.75 (Strong). Governance can recalibrate thresholds based on human judgment, distribution analyses, or ground-truth labels if collected later.

### RAG/LLM Flow
When RAG is enabled and credentials are available, `RAGEngine` builds a structured prompt that contains:
- **SYSTEM:** Role definition to steer the model toward business analysis.
- **CONTEXT:** Strategy title/description, current alignment score and label, and a ranked list of retrieved actions with similarities.
- **INSTRUCTIONS:** Explicit tasks: explanation, suggested actions, KPIs, timeline/ownership, and risks.
- **RESPONSE_FORMAT:** A strict JSON schema specifying keys and value types.

This structured approach improves reliability and reduces the chance of off-format or generic answers. If the LLM call fails or is disabled, the deterministic fallback returns domain-specific suggestions and KPIs to maintain continuity.

### Data Flow (Detailed)
1. **Input:** Users select sample data or upload their own JSON/PDF. PDFs are parsed and converted into arrays of objects.
2. **Object Construction:** The app converts inputs into domain objects (`StrategicObjective`, `ActionTask`).
3. **Indexing:** Action tasks are embedded and stored in ChromaDB with metadata.
4. **Querying:** For each strategy, an embedding is computed; ChromaDB returns top-K action matches with similarity scores.
5. **Scoring & Labeling:** The app computes per-strategy averages, overall score, coverage, and assigns labels based on thresholds.
6. **Recommendations:** RAG/LLM generates structured improvements (or fallback suggestions). KPIs and timelines provide measurable and time-bound guidance.
7. **Visualization:** Dashboards render gauges, bars, pies, heatmaps, and tables. Users can inspect per-strategy expansions and owner workload distribution.
8. **Export:** Results are saved to `outputs/` with a timestamp; CSVs and JSON downloads are offered in the UI.

### Deployment Options
**Local Development:** The app runs via `streamlit run app/streamlit_app.py`, using local persistence for ChromaDB. This is ideal for iterative testing and debugging.

**Streamlit Cloud:** For rapid prototyping and sharing, deploy the repository to Streamlit Community Cloud. Configure the entrypoint to `app/streamlit_app.py`, set environment variables (e.g., `OPENAI_API_KEY`) as secrets, and share the hosted URL.

**Azure Container Apps:** The architecture in `.azure/architecture.copilotmd` models the app as a containerized service hosted on Azure Container Apps (ACA), bound to optional dependencies:
- **Azure OpenAI:** For RAG capabilities via secrets.
- **Application Insights:** For observability via system identity.
- **Storage Account:** For durable storage integration via system identity.
- **Container Registry:** For image hosting via secrets.
- **Key Vault:** For secrets management via system identity.

Supported hosting technologies include `appservice`, `function`, `containerapp`, `staticwebapp`, and `aks`. If your topology targets a different compute (e.g., Azure App Service or AKS), the same component boundaries apply, with changes to how images and environment variables are managed.

### Security Considerations
- **Secrets:** API keys (e.g., OpenAI) should be stored in Key Vault and referenced via environment variables or managed identities rather than committed to source.
- **Data Handling:** Uploaded files are processed in memory; if persistence beyond `outputs/` is needed, use a storage account with appropriate access controls.
- **Telemetry:** Log only necessary operational signals; avoid sensitive payloads.
- **Role-Based Access (RBAC):** For cloud resources, use RBAC to restrict access to storage, insights, and key vault to the app identity.

### Observability and Monitoring
With Application Insights, capture:
- **Request Latency:** Track the time spent embedding, querying, and rendering.
- **Error Rates:** Observe RAG failures and fallback usage.
- **Traffic Patterns:** Identify peak hours and high-usage features.

Use dashboards and alerts to ensure the app remains responsive and reliable. For local deployments, basic logging in the app suffices; cloud deployments benefit from centralized insights.

### Scalability and Performance
- **Batching & Caching:** Precompute and cache action embeddings; batch index large datasets to reduce startup time.
- **Top-K Tuning:** Adjust `top_k` based on the number of actions per strategy; a larger `top_k` improves exploration but increases query cost.
- **Model Selection:** For larger deployments, consider higher-capacity models (e.g., `all-mpnet-base-v2`) if latency budgets permit. Otherwise, stay with `all-MiniLM-L6-v2` for responsive interactions.
- **Parallelism:** Tokenizers and embedding pipelines can leverage multiple threads. Manage parallelism with environment variables to avoid deadlocks or noisy warnings.

### Reliability and Fallbacks
- **RAG Fallback:** Deterministic templates guarantee recommendations even if the LLM is unreachable, rate-limited, or misconfigured.
- **Graceful Degradation:** Charts render defaults when datasets are empty or sparse; UI provides warnings rather than hard failures.
- **Persistent Store:** ChromaDB persistence ensures the index endures restarts; recovery is straightforward.

### Testing and Validation Hooks
- **Unit Tests:** Smoke and alignment tests validate core behaviors. CI can run `pytest -q` on push to main.
- **Manual QA:** Use the dashboard to inspect strategy-level matches and ensure labels match expectations.
- **Acceptance Metrics:** Review Overall Score and Coverage over time. Aim for steady improvements with data enrichment and threshold tuning.

### Extensibility and Future Directions
- **Hybrid Retrieval:** Combine lexical (BM25) and dense embeddings with reranking for improved precision.
- **Human-in-the-Loop:** Gather labeled pairs of strategies/actions for threshold calibration and to evaluate precision/recall.
- **Filters and Facets:** Add owner, label, and date filters to support targeted analysis.
- **Time-Series Analytics:** Track alignment trends across saved outputs; add visual trendlines and KPIs.
- **Multi-Tenant Support:** Partition indexes by portfolio or business unit; enforce data isolation policies.

### Risks and Mitigations
- **Data Quality:** Incomplete descriptions or vague titles lower similarity scores. Mitigation: enforce schema quality checks and authoring guidelines.
- **Threshold Sensitivity:** Small shifts can change label assignments. Mitigation: governance reviews and calibration cycles.
- **LLM Variability:** Model updates can change outputs. Mitigation: pin models, monitor responses, and rely on fallback templates when needed.
- **Cost and Latency:** Cloud inference introduces cost and latency. Mitigation: cache, batch, and apply rate limits; fall back when appropriate.

### Summary
This architecture balances practicality and rigor. The deterministic alignment core and persistent vector store ensure stability, while optional RAG enriches recommendations for weak or medium alignments. The system fits both classroom and production contexts: simple enough to run locally, and robust enough to host in Azure with proper observability and security. Over time, data enrichment, threshold calibration, and retrieval upgrades will increase Overall Score and Coverage, delivering a more transparent and effective strategy-to-execution pipeline.
