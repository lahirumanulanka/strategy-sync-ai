# Dashboard Design

## Goals
- Communicate alignment health quickly (overall score, coverage)
- Enable drill-down from strategies to matched actions
- Reveal workload distribution and similarity spread

## Views
- Overview:
  - Overall Gauge (0–100)
  - Coverage Gauge (0–100)
  - Avg Top-3 Similarity per Strategy (bar)
  - Alignment Label Distribution (pie)
  - Top Matches Similarity Heatmap
  - Owner Workload Bar
- Strategy Explorer:
  - Table of strategies with averages and labels
  - Detailed per-strategy matches table (similarity, owner, dates)
- RAG Suggestions:
  - Per-strategy recommendations: actions, KPIs, timelines, risks
- Data Export:
  - Results JSON; strategies/matches CSV downloads; converted PDFs

## Interaction & Usability
- Sidebar toggles for sample data and RAG
- Expander per strategy for details
- Auto-save of results to `outputs/`

## Visual Language
- Color-coded gauge steps (weak/medium/strong)
- Consistent plotly theme; readable labels; rotation for long titles

## Future Enhancements
- Filter by owner/label; search by strategy title
- Time-series comparison across saved runs
- KPI trend cards and thresholds editor

---

## Extended Dashboard Design (Comprehensive)

### Design Principles
The Strategy–Action Synchronization AI (SAS-AI) dashboard is built to surface alignment insights quickly while supporting deeper analysis and governance workflows. The design follows four guiding principles:
1. Clarity: Present headline metrics prominently and use consistent color coding to reduce cognitive load.
2. Drill-down: Enable users to move from portfolio-level indicators to per-strategy and per-action details.
3. Actionability: Highlight areas of weakness and ownership distribution to inform corrective planning.
4. Reliability: Render sensible defaults and placeholders when data is sparse or missing.

### Information Architecture
The dashboard consists of four main views: Overview, Strategy Explorer, RAG Suggestions, and Data Export. The Overview emphasizes portfolio health through gauges and charts. Strategy Explorer provides sortable tables and per-strategy expansions. RAG Suggestions list improvement recommendations with KPIs and timelines. Data Export exposes JSON and CSV downloads to support governance artifacts and external analysis.

### Metric Semantics and Visual Mapping
- Overall Synchronization Score (Gauge): Reflects the mean of per-strategy top-3 similarities, scaled to 0–100. The gauge includes stepped color bands (weak/medium/strong) to provide immediate context. Rationale: A single headline score helps leadership understand aggregate alignment.
- Coverage Percent (Gauge): Shows the percentage of strategies with ≥ 2 “Strong” matches (similarity ≥ 0.75). This gauge complements the overall score by indicating breadth of strong alignment rather than isolated peaks.
- Avg Top-3 Similarity per Strategy (Bar): Plots a bar for each strategy, sorted descending. Rationale: Ranking surfaces which strategies are most aligned and which need attention.
- Alignment Label Distribution (Pie): Displays counts of Weak, Medium, Strong labels (with Unknown or No Data when applicable). Rationale: A categorical distribution aids quick scanning for weakness prevalence.
- Top Matches Similarity Heatmap: Presents Rank 1..N similarities per strategy in a heatmap, providing a sense of spread and consistency across the top matches.
- Owner Workload Bar: Counts top matches by owner to reveal workload distribution and potential bottlenecks.

### Gauge Design Considerations
Gauges use steps with color-coded ranges to improve interpretability:
- Overall Synchronization Score: Red (0–55), Amber (55–75), Green (75–100). These ranges align with threshold boundaries and provide intuitive semantics (weak, medium, strong).
- Coverage Percent: Red (0–30), Amber (30–60), Green (60–100). These are conservative bounds intended to motivate progress across strategies.

Gauges suppress chart clutter by minimizing margins and keeping titles concise. Numeric values are shown prominently, and the gauge axis range is fixed to 0–100 to standardize across runs.

### Bar Chart Rationale
The per-strategy bar chart is sorted by average similarity to bring high and low performers to the fore. Long strategy titles are addressed with angled ticks (e.g., −30 degrees) for readability. The color choice is distinct from gauges to prevent visual blending. The chart aligns with the decision-making flow: identify low performers → inspect details → assign owners and actions.

### Pie Chart Semantics
The pie chart reflects label distribution based on thresholds. It includes Unknown and No Data categories when applicable. Color mapping follows established semantics: Weak (red), Medium (amber), Strong (green), Unknown/No Data (gray), ensuring consistency across the UI.

### Heatmap Detail and Usage
The heatmap shows similarities of Rank 1..N per strategy (default N=5). It provides a quick visual sense of whether top matches cluster at high similarities or taper off. A uniform green-to-purple (Viridis) gradient is used to avoid misinterpretation and keep the focus on numeric differences.

Recommended workflow:
1. Scan for rows with low gradients (overall weak matches).
2. Investigate strategies where Rank 1 is strong but subsequent ranks degrade sharply, suggesting limited viable action coverage.
3. Use this insight to prioritize data enrichment or targeted action creation.

### Owner Workload Interpretation
The owner workload bar visualizes count totals for top matches by owner. This helps answer:
- Which owners have many matched actions (potential bandwidth constraints)?
- Are some owners underrepresented (possible gaps in accountability or data completeness)?

Actions:
- Shift or reassign ownership to balance workload.
- Enrich action descriptions for underrepresented owners to improve matching.

### Strategy Explorer Interaction
The Strategy Explorer shows two tables:
- The strategy summary (`strategies_dataframe`): Each row includes title, average similarity, and label.
- The matches table (`matches_long_dataframe`): A long-form view of strategy–action pairs with similarity and owner.

Each strategy has an expander showing a focused table with match details (action title, owner, start/end dates, similarity, and label). This design streamlines deep dives without cluttering the main view.

### Usability and Accessibility
- Distinct color palettes reduce ambiguity; color is paired with numeric values and labels for users with color vision considerations.
- Tables support scrolling; large datasets benefit from future paging and filtering.
- Icons are avoided to minimize noise; emphasis is on data clarity.
- Download buttons include clear labels and predictable filenames.

### Performance Considerations
- Plotly charts are efficient for moderate datasets. For large datasets, consider reducing top-N in heatmaps, lazy loading tables, and enabling server-side filtering.
- Embeddings and retrieval are handled before charts render, keeping visualization performant. Any heavy computations should run outside of the UI thread where possible.

### State and Persistence
- Results are saved automatically to `outputs/` with timestamped filenames, enabling historical comparisons.
- When PDFs are uploaded and converted, the app exposes JSON downloads so users can reuse structured data without re-parsing.

### Export Semantics
- Results JSON: Contains alignment metrics, per-strategy results, and recommendations (RAG or fallback). This file is the canonical artifact for governance.
- CSVs: Two downloads—strategies and matches—allow analysts to slice and pivot data externally (e.g., in spreadsheets or BI tools).

### Roadmap for Interactivity
- Filters: Owner, label, and date range filters in Overview and Strategy Explorer.
- Search: Title search with partial matching; optional fuzzy matching.
- Sorting: Multi-column sorts in tables (e.g., by owner then similarity).
- Tooltips: Inline tooltips for chart points to display owners and dates.

### Time-Series and Trendlines
Add a view to compare outputs across runs, showing:
- Overall Score and Coverage trendlines.
- Distribution shifts in labels (stacked area chart).
- Delta tables for top strategies moving from Weak → Medium → Strong.

### KPI Cards and Thresholds Editor
- KPI Cards: Small tiles showing current Overall Score, Coverage, count of Weak strategies, and action creation rate. Optionally show variance from previous run.
- Thresholds Editor: Admin-only controls to adjust label thresholds (e.g., 0.55/0.75), with preview simulations and safeguards.

### Testing the Dashboard
- Unit tests assert that `src/viz.py` functions return figures with expected structure and that placeholders are used when data is empty.
- Manual tests verify that toggles (Use LLM, Use Sample Data) behave as expected, export buttons generate correct files, and charts render without errors.
- Latency tests measure time-to-first-paint after an alignment run; target sub-second chart rendering for moderate datasets.

### Instrumentation and Observability (Optional)
- Application Insights: Track chart render times, export clicks, and RAG invocation counts.
- Logging: Record alignment metrics and download events for governance.

### Edge Cases and Error Handling
- Empty Datasets: Charts render neutral placeholders (“No data”) to avoid confusing blanks.
- Missing Metadata: Owners set to “Unknown”, dates set to “None” in tables.
- Parse Failures: PDF parsing errors surface warnings; users can upload JSON directly.

### Internationalization and Localization (Future)
- Support localized labels and date formats.
- Provide currency and unit settings where relevant to KPIs.

### Security and Privacy
- Avoid embedding sensitive information in charts; display only necessary fields (titles, owners, dates).
- Keep secrets in environment variables or secure stores; never render keys on-screen.

### Implementation Notes
- Charts are implemented in `src/viz.py` using Plotly (express and graph objects). Gauge functions (`fig_overall_gauge`, `fig_coverage_gauge`) and other visual components share consistent layout settings.
- The Streamlit app (`app/streamlit_app.py`) orchestrates tabs, toggles, and saving/export logic. It calls visualization functions with computed alignment results.

### Summary
The SAS-AI dashboard provides a coherent, interpretable, and actionable view of alignment health. By combining headline gauges, distribution charts, similarity heatmaps, ownership insights, and detailed per-strategy tables, users can identify weak spots, plan corrective actions, and track progress. With upcoming enhancements—filters, search, time-series comparisons, and KPI cards—the dashboard will evolve into a decision-support hub for strategy execution, backed by clear metrics and exportable evidence.
