# Testing & Evaluation Results

## Summary
The current test suite passed (`2 passed`). A fresh alignment run was generated for evaluation:
- Overall Score: **57.64**
- Coverage Percent: **0.00**
- Artifact: see the latest alignment output in `outputs/` (e.g., `outputs/alignment_cli_20260202-160912.json`).

## Methodology
- Unit tests:
  - `tests/test_smoke.py`: basic import/run verification for app components
  - `tests/test_alignment_rag.py`: alignment and RAG behaviors
- Data: sample JSON from `data/strategic.json` and `data/action.json`
- Embeddings: `all-MiniLM-L6-v2` with normalization
- Vector store: ChromaDB persistent collection

## Metrics
- **Overall Score:** Mean of per-strategy top-3 similarities × 100
- **Coverage:** Percent of strategies with ≥ 2 “Strong” matches
- **Labels:** Weak/Medium/Strong via thresholds (0.55/0.75)

## Interpretation
- Score ~58 suggests moderate alignment across the portfolio; improvements are viable.
- Coverage 0% indicates few strategies reach ≥ 2 strong action matches with current sample; RAG suggestions or targeted actions should be added.

## Validation Steps
1. Run tests:
   - `pytest -q`
2. Produce an evaluation run:
   - `python scripts/run_alignment.py`
3. Inspect dashboard and exports:
   - `streamlit run app/streamlit_app.py`
4. Review per-strategy details and owner workload to identify gaps.

## Acceptance Criteria
- All tests pass in CI
- Alignment score and coverage meet thresholds defined in the strategic plan
- Recommendations generated within acceptable latency

## Next Actions
- Enrich action plan descriptions and owners for stronger matches
- Iterate thresholds after stakeholder review
- Add filters to analyze weak labels by owner and timeline

---

## Extended Testing & Evaluation (Comprehensive)

### Objectives
This section provides a comprehensive, step-by-step description of the testing and evaluation approach for the Strategy–Action Synchronization AI (SAS-AI). The objectives of evaluation are to:
- Verify end-to-end correctness of data ingestion, embedding, indexing, retrieval, scoring, visualization, and export flows.
- Quantify alignment quality using defensible, reproducible metrics (Overall Score and Coverage). 
- Assess recommendation generation (RAG and deterministic fallback) for clarity, relevance, and actionability.
- Establish acceptance criteria and baselines that are practical for governance and iterative improvement.

### Data and Assumptions
- Source data: Sample strategic and action plans located in `data/strategic.json` and `data/action.json`. These are representative, not exhaustive, and include titles, optional descriptions, owner fields, and timeline hints.
- Format: JSON lists of objects. The app can also accept PDFs which are converted to structured JSON via the PDF parser; however, the tests use the JSON variants to minimize nondeterminism.
- Scope: Strategies are matched against actions via semantic similarity (embeddings). No numerical optimization or constraint satisfaction is currently performed.
- Privacy: No personally identifiable information is required. Owners are role-like labels (e.g., “Operations”, “Finance Ops”).

### Environment and Reproducibility
- Python: 3.13 (virtual environment configured).
- Dependencies: Pinned in `requirements.txt` (e.g., `sentence-transformers==2.6.1`, `chromadb==0.5.23`, `transformers==4.46.3`).
- Embedding Model: `sentence-transformers/all-MiniLM-L6-v2` (default), selected for balanced speed–quality; normalized embeddings are used to bound similarity behavior.
- Vector Store: ChromaDB with persistent storage in `chroma_db/` to stabilize retrieval performance over runs.
- RAG Model: Azure OpenAI-compatible OpenAI client; model name can be configured (default `gpt-4o-mini`). If no API key is present, deterministic fallback suggestions are used.
- Seeds: While embeddings may utilize multithreading under-the-hood, input and pipeline order are deterministic for a fixed dataset. If strict reproducibility is needed, disable parallel tokenizers with `TOKENIZERS_PARALLELISM=false` and use single-threaded execution.

### Test Suite Structure
- `tests/test_smoke.py`: Validates import paths, basic object construction, and simple run invocations without exercising external services.
- `tests/test_alignment_rag.py`: Focuses on alignment outputs and the presence of RAG outputs or fallback suggestions; ensures labels and fields are well-formed.

These tests are intentionally minimal yet representative. They serve as a rapid signal that changes did not break foundational behaviors and data contracts.

### End-to-End Evaluation Procedure
1. Install dependencies and run tests:
   - `pytest -q` ensures no regressions were introduced.
2. Produce an alignment run using the sample dataset:
   - `python scripts/run_alignment.py` generates a fresh JSON artifact under `outputs/`, including `result`, `rag_recommendations` (if API key available), and deterministic `recommendations`.
3. Launch the Streamlit app to visualize outcomes:
   - `streamlit run app/streamlit_app.py` provides gauges, bars, pies, heatmaps, and tables for inspection.
4. Validate exports:
   - Download CSVs (strategies/matches) and ensure schema consistency; verify JSON payload structure and timestamps.

### Metrics: Definitions and Rationale
1. Overall Score: For each strategy, take the top-3 retrieved action similarities, average them, and then average across all strategies; multiply by 100 to present as a percentage. Rationale: Top-3 average provides robustness to outliers while still focusing on the strongest matches.
2. Coverage Percent: Percentage of strategies that have at least two “Strong” matches (similarity ≥ 0.75). Rationale: Ensures breadth of high-confidence mapping rather than isolated wins.
3. Alignment Label: Based on per-strategy average top-3 similarity, thresholds categorize as Weak (<0.55), Medium (≥0.55 and <0.75), Strong (≥0.75). Rationale: Simple, transparent rules suitable for governance and stakeholder communication.

### Threshold Calibration Approach
- Initial thresholds (0.55/0.75) were chosen to balance strictness with practicability, aligned with common cosine similarity heuristics for sentence embeddings.
- To calibrate: Plot similarity distributions per strategy; compute the fraction of matches above candidate thresholds; gather stakeholder feedback and adjust thresholds accordingly.
- Optional ROC-style analysis: If ground-truth labels are available later (human-annotated alignment), derive optimal decision thresholds that maximize true positives while controlling false positives.

### RAG Evaluation Methodology
When an LLM is available:
- Structure and JSON compliance: RAG responses must follow the requested schema (explanation, suggested_actions, kpis, timeline_and_ownership, risks).
- Relevance: Suggestions should relate directly to the strategy context and retrieved actions.
- Actionability: Proposed actions should be clear enough to schedule and assign.
- KPI Quality: KPIs should be measurable and time-bound; avoid vague metrics.
- Latency: Record the time-to-response; target < 5 seconds for a single prompt in a production setting (dev environments may differ).

Fallback Rule-Based Evaluation:
- Determinism and consistency across runs is preferred for baselining.
- Coverage of core categories (actions, KPIs, timeline, risks) must be satisfied by templates.
- Readability and specificity are reviewed by the team; improvements are made iteratively.

### Results Interpretation (Current Run)
- Overall Score ≈ 57.64 implies moderate similarity across strategies and available actions. This is not unexpected for a small, illustrative dataset that may lack detailed descriptions and strong owner/timeline signals.
- Coverage 0% indicates that few strategies currently have ≥ 2 strong matches (≥ 0.75). It is a pointer that data enrichment (better action descriptions, refined strategy narratives, consistent owner roles) would lift the distribution of similarities.
- Recommendation Quality: If Azure OpenAI keys were present, the RAG module produces contextual suggestions that can accelerate improvement planning. Otherwise, deterministic templates ensure a baseline set of actionable next steps.

### Error Handling and Edge Cases
- Missing fields: Owners, dates, or descriptions may be absent; the app handles these gracefully, e.g., marking “Unknown” owners.
- Empty datasets: Charts render with placeholder rows/labels.
- PDF conversions: Parsing issues fall back to warnings; users can upload JSON directly.
- Telemetry and noise: ChromaDB and transformers warnings are silenced to keep the UI clean and focus on user signals.

### Performance and Resource Considerations
- Embedding generation: For small to medium portfolios, `all-MiniLM-L6-v2` provides rapid inference with strong baseline quality. For larger datasets, consider batching and caching embeddings in the persistent store.
- Retrieval: ChromaDB with HNSW index scales well; ensure appropriate `top_k` based on typical action density per strategy.
- Visualization: Plotly charts are interactive and light-weight; avoid excessive table sizes by paging or filtering in future enhancements.

### Validation Artefacts and Logging
- Primary artefact: `outputs/alignment_cli_<timestamp>.json` containing alignment results and recommendations.
- Secondary artefacts: CSVs for strategies and matches produced from the Streamlit app.
- Logging: The CLI prints Overall Score, Coverage, and the path to the saved output; the app shows success messages for saved files.

### Acceptance Criteria (Detailed)
- CI tests pass with no failures.
- Overall Score improves over baselines after data enrichment or threshold tuning (e.g., target ≥ 65 within two iterations).
- Coverage moves toward the strategic target (e.g., ≥ 50% of strategies with at least two strong matches in phase two).
- Recommendations (RAG or fallback) remain schema-compliant, readable, and time-bound.

### Limitations
- Embedding-only alignment: Does not incorporate structured constraints like capacity limits or budget considerations; similarity is semantic, not operational feasibility.
- Dataset breadth: Sample data is intentionally small; coverage will naturally grow with real-world action inventories and detailed strategy narratives.
- Threshold sensitivity: Small shifts in descriptions or modeling can change label assignments; governance reviews should oversee threshold changes.

### Future Enhancements
- Advanced retrieval: Hybrid lexicon + dense search, reranking models for more precise top-K.
- Human-in-the-loop validation: Collect labeled pairs of strategies and actions to train or tune decision thresholds and measure precision/recall.
- Filtering and faceting: Owner-, label-, and date-based filters; search by title.
- Time-series comparisons: Track changes in score and coverage across versions in `outputs/` to visualize trendlines.
- KPI dashboards: Add cards showing progress toward KPI targets and variance over time.

### Step-by-Step Reproduction Guide
1. Setup:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Tests:
   ```bash
   pytest -q
   ```
3. Evaluation run:
   ```bash
   python scripts/run_alignment.py
   ```
4. Dashboard:
   ```bash
   streamlit run app/streamlit_app.py
   ```
5. Optional RAG:
   - Set `OPENAI_API_KEY` in environment or `.env`.
   - Re-run the app; check “Use LLM (RAG)” in the sidebar.

### Conclusion
The SAS-AI testing and evaluation approach emphasizes reproducibility, clarity, and governance readiness. Current metrics provide a baseline for improvement. As richer data and calibrated thresholds are introduced, both the Overall Score and Coverage are expected to increase. The combination of semantic alignment and recommendation generation (LLM or deterministic fallback) supports practical decision-making and prioritization routines for operations and program management.
