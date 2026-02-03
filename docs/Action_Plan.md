# Action Plan: Strategy–Action Synchronization AI

Version: 1.0  
Owner: Delivery Manager

## Overview
This action plan translates the strategic objectives into executable work packages with timelines, owners, and validation steps. It emphasizes incremental delivery and measurable outcomes.

## Workstreams
1. **WS1 – Data Ingestion & Modeling**  
   - Tasks:
     - Define JSON schemas for strategic and action items
     - Implement PDF-to-JSON parsing for uploads
     - Build embedding pipeline; enforce normalization
   - Owner: Data Science
   - Timeline: Feb–Mar 2026
   - Deliverables: Validated datasets; embeddings; store upsert routines

2. **WS2 – Alignment Engine & Persistence**  
   - Tasks:
     - Index action tasks in vector store (ChromaDB persistence)
     - Implement similarity queries; thresholds; labels
     - Compute overall score and coverage metrics
   - Owner: Engineering
   - Timeline: Feb–Mar 2026
   - Deliverables: Alignment results JSON; thresholds config

3. **WS3 – RAG Recommendations**  
   - Tasks:
     - Build structured prompts; include context and response format
     - Integrate OpenAI (Azure) with secure key access; fallback rules
   - Owner: Data Science
   - Timeline: Mar–Apr 2026
   - Deliverables: RAG suggestions; KPIs; timelines; risks

4. **WS4 – Dashboard & Exports**  
   - Tasks:
     - Implement overview gauges, bar charts, pie, heatmap, owner workload
     - Strategy explorer tables; CSV/JSON exports
   - Owner: Engineering
   - Timeline: Mar 2026
   - Deliverables: Streamlit dashboard; export buttons

5. **WS5 – Hosting & Observability**  
   - Tasks:
     - Containerize app or use managed hosting; bind Application Insights
     - Configure Key Vault and Storage bindings
   - Owner: Platform
   - Timeline: Apr 2026
   - Deliverables: Hosted URL; telemetry; secrets stored securely

6. **WS6 – Validation & Testing**  
   - Tasks:
     - Write smoke and RAG alignment tests; run in CI
     - Record metrics and acceptance thresholds
   - Owner: QA
   - Timeline: Continuous
   - Deliverables: Test reports; metric baselines

## Milestone Plan
- M1: Minimal viable alignment  
- M2: Full dashboard + export  
- M3: RAG integrated + fallback  
- M4: Hosted prototype with monitoring  

## Resource Plan
- 1 DS, 1 Eng, 1 Platform Eng, 1 QA, 0.5 PM  

## Acceptance Criteria
- App runs with sample data end-to-end  
- Exports produce valid JSON/CSV  
- Tests pass with defined thresholds  
- Hosted URL accessible and monitored  

## Risks & Contingencies
- Model drift or embedding changes → Pin versions; periodic review  
- Secrets leakage → Key Vault; env scoping; reviews  
- Data parsing edge cases → Strict validators; manual review workflow  

## Communication & Reporting
- Weekly status; dashboard snapshot; blockers raised in standups  

## Appendix: Task Breakdown
- Detailed subtasks per workstream kept in internal tracker; synchronized with repo structure and CI pipelines.
