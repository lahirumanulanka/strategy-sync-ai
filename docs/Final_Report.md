# Final Report: Strategy–Action Synchronization AI

Date: 2026-02-02  
Author: Project Team

## Overview
This report consolidates the strategic and action plans, architecture, dashboard design, and testing evaluations for the Strategy–Action Synchronization AI. The app quantifies alignment between strategic objectives and operational actions, visualizes insights, and generates improvement recommendations.

## Contents
- Strategic Plan: `docs/Strategic_Plan.md`
- Action Plan: `docs/Action_Plan.md`
- System Architecture: `docs/System_Architecture.md` and `.azure/architecture.copilotmd`
- Dashboard Design: `docs/Dashboard_Design.md`
- Testing & Evaluation: `docs/Testing_and_Evaluation.md`

## Key Results
- Tests: 2 passed
- Latest alignment run:
  - Overall Score: 57.64
  - Coverage Percent: 0.00
  - Output JSON saved in `outputs/`

## RAG & Recommendations
- RAG integrated with Azure OpenAI (if keys present); deterministic fallback ensures resilience.
- Suggestions include actions, KPIs, timelines, risks per strategy.

## Data & Exports
- JSON and CSV artifacts are saved under `outputs/` and available via the app.

## Deployment Options
- Streamlit Cloud (fastest path) or Azure Container Apps with Application Insights, Key Vault, and Storage bindings.
- Hosted link will be added upon deployment completion.

---

## Executive Summary
The Strategy–Action Synchronization AI (SAS-AI) was developed to bridge the gap between strategic goals and operational execution. It leverages sentence embeddings to quantify the similarity between strategic objectives and action tasks, yielding interpretable labels (Weak, Medium, Strong) and portfolio-level indicators such as Overall Score and Coverage. A Retrieval-Augmented Generation (RAG) component, when enabled, produces tailored improvement recommendations complete with KPIs, timelines, and risks. The project delivers an end-to-end experience: ingesting data, computing alignment, visualizing findings, and exporting artifacts suitable for governance and continuous improvement.

The current baseline run indicates moderate alignment (Overall Score ≈ 57.64) with limited breadth of “Strong” matches (Coverage 0%). These results are consistent with a compact, illustrative dataset and offer a clear path for improvement: enrich action descriptions, reinforce ownership and timelines, calibrate thresholds, and scale the catalog of actions. The system is engineered for both classroom and production contexts, with a deterministic core and optional cloud integrations for observability and security.

## Objectives & Scope
SAS-AI aims to provide a reliable, data-driven mechanism for measuring strategy-to-execution alignment and accelerating corrective action planning. The scope includes:
- Ingestion of strategic and action plans from JSON and PDF sources.
- Embedding, persistent indexing, and top-K retrieval of action tasks per strategy.
- Computation of per-strategy averages, Overall Score, Coverage, and categorical labels.
- Optional RAG/LLM integration for recommendations; deterministic fallback when LLM is unavailable.
- Visual analytics and exports to facilitate steering meetings, dashboards, and reporting.

Non-goals for this phase include complex constraint optimization (e.g., resource capacity or budgets) and full portfolio management. The focus remains on semantic alignment, interpretability, and extensibility.

## Methodology Summary
The alignment methodology centers on normalized sentence embeddings using a well-established model (`all-MiniLM-L6-v2`). Actions are embedded and upserted into a persistent ChromaDB collection. For each strategy, the system computes an embedding and queries the vector store for similar actions. The Top-3 similarities per strategy are averaged to derive a strategy-level alignment score; Overall Score takes the mean of these averages across all strategies and scales to percentage (×100). Coverage reflects the share of strategies with ≥ 2 “Strong” matches (similarity ≥ 0.75).

Thresholds (0.55/0.75) provide a transparent mapping from similarity to labels, creating clear signals for governance. While these defaults are sensible for embeddings, calibration against stakeholder expectations or annotated ground truth is recommended over time.

## Architecture Overview
The architecture is documented in [docs/System_Architecture.md](docs/System_Architecture.md) and a Mermaid diagram in [.azure/architecture.copilotmd](.azure/architecture.copilotmd). Key components include:
- `strategy-sync-app` (Streamlit): the UI that drives ingestion, alignment runs, visualization, recommendations, and exports.
- `AlignmentEngine`: embedding, indexing, retrieval, labeling, and metrics computation.
- `RAGEngine`: prompt building and OpenAI client integration (Azure OpenAI-compatible); deterministic fallback ensures recommendations are always produced.
- Vector store (ChromaDB): persistent index, metadata-aware retrieval; durable across runs.
- Optional Azure integrations: Application Insights (telemetry), Key Vault (secrets), Storage Account (durable storage), Container Registry (images).

The design emphasizes modularity, determinism, and deployability across local and cloud environments.

## Dashboard & Visual Analytics
The dashboard design (see [docs/Dashboard_Design.md](docs/Dashboard_Design.md)) provides quick insight into alignment health:
- Gauges for Overall Score and Coverage.
- Bar chart for Average Top-3 Similarity per Strategy.
- Pie chart for label distribution.
- Heatmap for top-match similarity spread.
- Owner workload view to highlight distribution across roles.
- Strategy explorer tables and detailed per-strategy match listings.

This visual language supports both executive summaries and analyst deep-dives, with consistent color coding and readable labels.

## Testing & Evaluation Highlights
As detailed in [docs/Testing_and_Evaluation.md](docs/Testing_and_Evaluation.md), the test suite passed (2 tests), confirming foundational behaviors for ingestion, alignment, and recommendation generation (RAG/fallback). A fresh evaluation run produced the following:
- Overall Score: 57.64
- Coverage: 0.00
- Output artifact located under `outputs/` with timestamped filename

These metrics provide a baseline for iterative improvement and are expected to increase as action catalogs grow and descriptions become more precise.

## RAG & Recommendations Assessment
When an LLM is available, the `RAGEngine` uses a structured prompt with SYSTEM/CONTEXT/INSTRUCTIONS/RESPONSE_FORMAT to encourage consistent JSON outputs containing: an explanation, suggested actions, KPIs, timeline/ownership, and risks. In practice, RAG outputs should be reviewed for relevance and actionability; latency should be monitored and managed with caching or batching if necessary. When keys are absent or calls fail, deterministic templates ensure that recommendations remain available, supporting continuity in governance workflows.

## Data & Governance
Artifacts are saved to `outputs/` (JSON and CSV) and available via the app for download. Governance recommendations include:
- Establish a cadence (weekly/bi-weekly) to review alignment results and target weak/medium labels for improvement.
- Define KPI thresholds and acceptance criteria; monitor changes over time.
- Maintain a versioned catalog of strategic objectives and actions to enhance reproducibility and traceability.
- Consider role-based controls for production environments and centralize secrets management.

## Deployment Options & Hosted Prototype
SAS-AI is designed for rapid deployment:
- **Streamlit Cloud:** Easiest path for a functional hosted link. Push the repo, set the entrypoint to `app/streamlit_app.py`, configure secrets in the platform, and share the URL.
- **Azure Container Apps:** Containerize the app and bind optional services (Application Insights, Key Vault, Storage Account, Azure OpenAI, Container Registry) as modeled in the architecture diagram. This path supports production observability, security, and scaling.

Supported hosting technologies include appservice, function, containerapp, staticwebapp, and aks. If you prefer a different topology (e.g., App Service), component boundaries remain consistent; deployment automation and environment configuration will differ.

## Risks & Mitigations
- **Data Quality:** Vague titles or missing descriptions reduce similarity scores. Mitigation: strengthen authoring standards and schema validation.
- **Threshold Sensitivity:** Small changes may alter label distributions. Mitigation: calibrate thresholds with stakeholder input and trend analysis.
- **LLM Variability:** Model updates can affect outputs. Mitigation: pin versions, monitor results, rely on fallback when necessary.
- **Cost/Latency:** Cloud inference introduces cost and latency. Mitigation: cache, batch requests, and enforce rate limits; fallback maintains functionality.
- **Security:** Secrets must not be committed. Mitigation: use Key Vault or platform secrets; apply RBAC and managed identities.

## Roadmap & Future Work
1. **Data Enrichment:** Expand the action plan catalog; improve narrative detail and ownership/timelines for stronger matches.
2. **Threshold Calibration:** Review label distributions and stakeholder feedback; adjust thresholds to reflect business expectations and ground truth.
3. **Hybrid Retrieval:** Combine lexical search (BM25) with dense embeddings and reranking models for improved precision.
4. **Filters & Facets:** Add owner/label/date filters to target weak areas; enable search by title.
5. **Time-Series Analytics:** Compare results across outputs to visualize trends in Overall Score and Coverage; add KPI cards and variance tracking.
6. **Human-in-the-Loop:** Collect annotated pairs of strategies/actions; evaluate precision/recall and optimize decision thresholds.
7. **Operationalization:** Integrate with governance calendars; automate weekly exports and summaries for leadership.

## Conclusion
SAS-AI delivers a practical and extensible framework for measuring and improving strategy-to-execution alignment. The deterministic core ensures reproducible metrics and charts; the optional RAG layer accelerates corrective planning with structured, action-oriented suggestions. Current metrics are a realistic baseline given the sample dataset and provide a clear path for uplift through data enrichment and threshold tuning. The application is ready for hosted prototype deployment and subsequent production hardening with observability, security, and scalable storage.

As the dataset grows and governance routines mature, we expect measurable improvements in both Overall Score and Coverage. Continued iteration—embedding upgrades, hybrid retrieval, filters, and KPI dashboards—will deepen insights and help teams prioritize work effectively. The project demonstrates that a balanced approach—semantic alignment, clear metrics, and practical recommendations—can make strategy execution more transparent, actionable, and data-driven.
