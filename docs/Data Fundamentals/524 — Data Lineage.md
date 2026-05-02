---
layout: default
title: "Data Lineage"
parent: "Data Fundamentals"
nav_order: 524
permalink: /data-fundamentals/data-lineage/
number: "0524"
category: Data Fundamentals
difficulty: ★★★
depends_on: ETL vs ELT, Data Catalog, Data Governance, Data Lake, Data Warehouse
used_by: Data Governance, Data Quality, Data Fabric, Data Catalog
related: Data Catalog, Data Governance, Data Quality, Data Fabric, Master Data Management
tags:
  - dataengineering
  - architecture
  - advanced
  - observability
  - tradeoff
---

# 524 — Data Lineage

⚡ TL;DR — Data Lineage tracks the complete journey of data — from origin through every transformation to final consumption — so you can answer "where did this number come from and what touched it?"

| #524 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ETL vs ELT, Data Catalog, Data Governance, Data Lake, Data Warehouse | |
| **Used by:** | Data Governance, Data Quality, Data Catalog, Data Fabric | |
| **Related:** | Data Catalog, Data Governance, Data Quality, Data Fabric, Master Data Management | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A CFO asks: "Why did our Q3 revenue report show $142M last week but $138M this week after the pipeline re-ran?" No one knows. There are 14 ETL pipelines, 6 intermediate tables, and 3 BI reports connected in an undocumented web. Engineers spend two days tracing backwards through SQL scripts, trying to find which pipeline touched which table. They eventually find a bug — a currency conversion rate table was accidentally updated with the wrong rate — but cannot tell how many other reports are also affected or which historical reports are now wrong. A regulator audit request arrives: "Provide documentation of how the capital ratio figure on page 7 of the annual report was calculated." No one can answer it.

**THE BREAKING POINT:**
Data pipelines are chains of transformations. Without a record of those chains, any data anomaly triggers a manual forensic investigation. Regulatory requirements (BCBS 239 for banks, GDPR right-to-explanation, SOX for public companies) increasingly require provenance documentation as a legal obligation, not a nice-to-have.

**THE INVENTION MOMENT:**
This is exactly why Data Lineage systems were created — a durable, queryable graph that records every origin, every transformation, and every consumer of every dataset, automatically.

---

### 📘 Textbook Definition

**Data Lineage** is the documentation and tracking of the full lifecycle of data — from its source of origin, through every transformation, enrichment, and movement, to its ultimate consumption point — represented as a directed acyclic graph (DAG) of data entities and operations. Lineage can be captured at three granularities: **table-level** (which tables feed which tables), **column-level** (which source column's value contributes to which target column), and **value-level** (which specific record value came from which source record). Column-level lineage is the standard production requirement for most governance and debugging use cases.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data Lineage is the complete audit trail of how any piece of data moved, changed, and arrived at its current state.

**One analogy:**
> Think of data lineage like the provenance certificate for a painting. When you buy a famous artwork, the certificate documents every owner since creation: "Painted in 1923 → sold to gallery in 1940 → auctioned in 1967 → private collector → museum, 2005." If the painting's value is disputed, you trace the certificate. If a data figure is disputed, you trace the lineage graph. Without the certificate, the painting's history is unverifiable. Without lineage, your data's history is unverifiable.

**One insight:**
Column-level lineage is what separates useful lineage from decorative lineage. Knowing that `fact_orders` comes from `stg_orders` (table-level) is helpful. Knowing that `fact_orders.revenue_usd` is derived from `stg_orders.price * stg_fx_rates.usd_rate` (column-level) is what enables you to pinpoint a bug in 5 minutes instead of 2 days.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every piece of data started somewhere (a source system) — there is always an origin.
2. Every transformation preserves some relationship between inputs and outputs — even complex transformations can be mapped.
3. Data lineage is a DAG: sources are roots, derived datasets are nodes, transformations are edges, consumers are leaves.

**DERIVED DESIGN:**
A lineage system captures: (1) **entity nodes** — tables, columns, files, reports; (2) **operation edges** — ETL job, SQL transformation, ML training run, dbt model; (3) **metadata** on each edge: timestamp, job ID, row count, schema version. The graph is traversable in both directions: **forward lineage** (impact analysis — "if I change this source table, what breaks?") and **backward lineage** (root cause analysis — "where did this column value come from?").

Detection methods:
- **Static analysis:** Parse SQL, dbt model, or Spark code to extract `INSERT INTO target SELECT expr FROM source` — no runtime required.
- **Runtime capture:** Hook into the execution engine (Spark listener, Airflow operator) to capture actual runs.
- **Log-based:** Parse query logs from BigQuery, Snowflake, or Athena.

Column-level lineage from SQL: `SELECT a.x + b.y AS z` → column `z` is derived from inputs `a.x` and `b.y`.

**THE TRADE-OFFS:**
**Gain:** Impact analysis in seconds; root-cause debugging in minutes; regulatory compliance; automatic documentation.
**Cost:** Capturing column-level lineage across complex SQL (CTEs, window functions, dynamic SQL) is technically hard and often incomplete. Lineage graphs become enormous at enterprise scale — thousands of nodes, millions of edges — requiring dedicated graph storage and querying infrastructure.

---

### 🧪 Thought Experiment

**SETUP:**
A data quality alert fires: the `kpi_dashboard.monthly_active_users` metric dropped 22% overnight.

**WHAT HAPPENS WITHOUT LINEAGE:**
An engineer opens the pipeline codebase. `monthly_active_users` is in `gold.kpi_metrics`. The engineer searches upstream tables: `gold.kpi_metrics` joins `silver.user_sessions`. Where does `silver.user_sessions` come from? Grepping through 40 Airflow DAGs... 90 minutes later: `silver.user_sessions` is loaded from `raw.app_events`. `raw.app_events` had a schema change yesterday — `event_type` column values changed. The fix is clear but discovering it took 90 minutes of detective work and required knowledge of the entire pipeline topology.

**WHAT HAPPENS WITH LINEAGE:**
The engineer opens the lineage graph for `kpi_dashboard.monthly_active_users`. Three clicks upstream: `gold.kpi_metrics → silver.user_sessions → raw.app_events`. The lineage tool shows: `raw.app_events` was last written at 02:00 AM by job `ingest_app_events_v3` (yesterday's run). There is a "schema change detected" annotation on yesterday's edge. The engineer clicks it: `event_type` column changed from ENUM to free-text STRING yesterday, causing downstream `WHERE event_type = 'SESSION_START'` filters to return zero rows. Root cause found in 3 minutes.

**THE INSIGHT:**
Lineage transforms debugging from archaeology (digging through undocumented pipelines) to GPS navigation (follow the route back to the origin point).

---

### 🧠 Mental Model / Analogy

> Data lineage is like the supply chain tracking system for a manufactured product. A car's VIN traceability system records every component — where the engine came from, when the gearbox was installed, who assembled it, when it was tested. When there is a safety recall, engineers instantly know which VIN numbers are affected by a faulty part. Data lineage does the same: when a source data quality issue is found, engineers instantly know which downstream reports and models are affected.

**Mapping:**
- "VIN tracking system" → lineage graph database
- "Car components" → source tables and columns
- "Assembly steps" → ETL transformations / SQL operations
- "Safety recall impact list" → forward lineage impact analysis
- "Component origin trace" → backward lineage root-cause trace

**Where this analogy breaks down:** A car's components are physical and discrete; data lineage must handle non-obvious derivations like `COALESCE(a, b, c)` (output derives from one of three inputs, dependent on which is NULL), making completeness genuinely hard.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Data Lineage is the story of where a number came from. If a report says revenue was $5M, lineage is what lets you trace that $5M back to every sales transaction that contributed to it, and every transformation it went through on the way.

**Level 2 — How to use it (junior developer):**
You access lineage through a Data Catalog UI (Alation, Collibra, dbt docs, Microsoft Purview). Click on any table or column to see its upstream sources (where data came from) and downstream consumers (what uses this data). When your pipeline breaks, trace backwards. When you want to understand impact before a schema change, trace forwards.

**Level 3 — How it works (mid-level engineer):**
Lineage can be captured statically (parse dbt model SQL, extract FROM/JOIN sources and SELECT computed columns) or dynamically (Spark OpenLineage listener emits lineage events to a lineage server at runtime). The lineage server stores the DAG in a graph database (Neo4j) or specialised lineage store (OpenLineage/Marquez). Column-level lineage parsing requires SQL AST (abstract syntax tree) analysis — tools like SQLGlot parse SQL into a tree and extract column-to-column derivation. Complex expressions (window functions, CTEs) are handled differently by different tools — not all implement them fully.

**Level 4 — Why it was designed this way (senior/staff):**
Column-level lineage was historically impractical because SQL parsing is hard (dialect variations, dynamic SQL, procedural code) and the storage graph would be enormous. The shift to code-as-data (dbt, Apache Spark) made static lineage extraction viable — the transformation code is now structured and parseable. OpenLineage (CNCF standard) emerged to provide a vendor-neutral event schema for runtime lineage emission, solving the fragmentation problem where every tool used a proprietary format. The remaining hard problem: lineage in ML pipelines (model training creates lineage between training data and model artefact, and between model and predictions) — this is the frontier of MLOps lineage.

---

### ⚙️ How It Works (Mechanism)

```
┌───────────────────────────────────────────────────────┐
│              DATA LINEAGE CAPTURE                     │
├───────────────────────────────────────────────────────┤
│  METHOD 1: STATIC ANALYSIS                            │
│  dbt model SQL → SQL parser (SQLGlot) →              │
│  AST extraction → column-level derivation map        │
│                                                       │
│  Example:                                             │
│  SELECT a.revenue * b.fx_rate AS revenue_usd          │
│  FROM fact_orders a JOIN fx_rates b                   │
│  → revenue_usd derives from: a.revenue, b.fx_rate    │
│                                                       │
│  METHOD 2: RUNTIME CAPTURE (OpenLineage)             │
│  Spark Job starts → OpenLineage listener →            │
│  START event emitted (inputs, outputs)               │
│  Spark Job ends  → COMPLETE event (row counts, schema)│
│       ↓                                              │
├───────────────────────────────────────────────────────┤
│  LINEAGE SERVER (Marquez / Atlas / OpenMetadata)      │
│  → Stores DAG in graph: nodes=datasets, edges=jobs   │
│  → Column-level derivation per edge                  │
│  → Run metadata (timestamp, row counts)              │
│       ↓                                              │
├───────────────────────────────────────────────────────┤
│  LINEAGE GRAPH (queryable)                            │
│                                                       │
│  raw.orders ──[ingest_job]──► stg.orders             │
│  raw.fx     ──[ingest_job]──► stg.fx_rates           │
│  stg.orders ┐                                         │
│  stg.fx     ┴─[transform]──► gold.orders_usd         │
│  gold.orders_usd ──[dbt]──► kpi.revenue_dashboard    │
│       ↓                                              │
├───────────────────────────────────────────────────────┤
│  CONSUMERS                                            │
│  Impact analysis: "what breaks if I drop stg.fx?"    │
│  Root-cause: "why is kpi.revenue wrong?"             │
│  Compliance: "show all data that touched PII column" │
└───────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Source DB → ETL job → [DATA LINEAGE captured here ← YOU ARE HERE]
         → Staging table → Transform →  Gold table → BI report
         [lineage edges created at each step]
```

**FAILURE PATH:**
```
ETL job fails → lineage run record shows FAILED status
→ downstream tables have "last successful run: yesterday"
→ impact analysis: 3 dashboards showing stale data
→ observable: lineage server run log + freshness alerts
```

**WHAT CHANGES AT SCALE:**
At petabyte-scale data estates with thousands of pipelines, lineage graphs can have millions of nodes and billions of edges. Graph query performance for large-hop traversal (e.g., "find all datasets 10 hops downstream of this source") becomes the bottleneck. Partitioning the lineage graph by domain, caching frequently-traversed paths, and limiting transitive closure depth (max 5 hops for interactive queries) are required optimisations.

---

### 💻 Code Example

Example 1 — dbt column-level lineage (automatic via docs):
```sql
-- models/gold/orders_usd.sql
-- dbt auto-generates column lineage from this SQL
SELECT
    o.order_id,
    o.customer_id,
    o.price * fx.usd_rate AS revenue_usd,  -- derived from 2 cols
    o.order_date
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('stg_fx_rates') }} fx
  ON o.currency = fx.currency_code
     AND o.order_date = fx.rate_date;
-- Run: dbt docs generate && dbt docs serve
-- → interactive lineage graph in browser
```

Example 2 — OpenLineage emission from Spark:
```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import (
    RunEvent, RunState, Run, Job,
    Dataset, InputDataset, OutputDataset
)
import uuid

client = OpenLineageClient.from_environment()

run_id = str(uuid.uuid4())
# Emit START
client.emit(RunEvent(
    eventType=RunState.START,
    eventTime="2024-06-15T10:00:00Z",
    run=Run(runId=run_id),
    job=Job(namespace="payments", name="transform_orders"),
    inputs=[InputDataset(namespace="s3://lake",
                         name="raw/orders")],
    outputs=[OutputDataset(namespace="s3://lake",
                           name="silver/orders")]
))
```

Example 3 — Query lineage graph (Marquez REST API):
```bash
# Get upstream lineage for a dataset (5 hops max)
curl "https://marquez:5000/api/v1/lineage?nodeId=\
dataset:s3://lake:silver/orders&depth=5"

# Output: JSON graph of upstream sources and operations
# Use to answer: "where did silver/orders come from?"
```

---

### ⚖️ Comparison Table

| Lineage Type | Granularity | Capture Method | Use Case | Completeness |
|---|---|---|---|---|
| Table-level | Table → Table | Catalog crawl / ETL log | High-level impact analysis | High |
| **Column-level** | Column → Column | SQL parsing / OpenLineage | Debugging, compliance | Medium (complex SQL gaps) |
| Value-level | Row → Row | Custom instrumentation | Audit, forensics | Low (expensive) |
| Runtime | Actual execution paths | Spark/Airflow hooks | Cross-engine accuracy | High (but overhead) |

**How to choose:** Column-level lineage from static SQL analysis is the right baseline for most organisations. Supplement with runtime lineage (OpenLineage) for cross-engine workflows. Value-level lineage is only justified for financial audit or healthcare compliance where individual record provenance must be proven.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Lineage is just documentation you write once | Lineage must be auto-captured and kept current — manual lineage docs decay to inaccuracy within weeks of schema changes |
| Table-level lineage is sufficient for debugging | Column-level lineage is required to identify which specific transformation introduced a bug; table-level only tells you the approximate location |
| All lineage tools capture the same information | Tools vary enormously — some only do dbt models, some only Spark, some are multi-engine. Verify coverage for your specific pipeline technology before committing |
| Lineage is only useful for regulatory compliance | Root-cause debugging is the highest-frequency use case; compliance is important but data teams use lineage daily for operational debugging |
| Adding lineage has no performance cost | Runtime lineage capture (OpenLineage events) adds overhead per job; static analysis adds CI/CD time; graph query infrastructure adds operational cost |

---

### 🚨 Failure Modes & Diagnosis

**Lineage Graph Staleness**

**Symptom:** Lineage graph shows a pipeline last run 3 weeks ago; actual pipeline runs daily but recent runs are not reflected.

**Root Cause:** OpenLineage emission was broken after a Spark version upgrade changed the listener API.

**Diagnostic Command / Tool:**
```bash
# Check Marquez for recent events
curl "https://marquez:5000/api/v1/jobs?namespace=payments&limit=10" \
  | jq '.[].latestRun.state'
# All showing "COMPLETE" from 3 weeks ago = emission broken
```

**Fix:** Redeploy the OpenLineage Spark listener with the correct version. Validate emission with a test job.

**Prevention:** Add a lineage freshness check: if a DAG's latest recorded run is more than 2× its schedule interval old, alert the platform team.

---

**Incomplete Column-Level Lineage**

**Symptom:** Column-level lineage graph shows some columns have no upstream; analysts cannot trace origin of computed metrics.

**Root Cause:** Dynamic SQL or procedural logic (stored procedures, Python UDFs) cannot be parsed by the static SQL analyser — these are "lineage black boxes."

**Diagnostic Command / Tool:**
```sql
-- Find columns with no upstream lineage in catalog
SELECT column_name, table_name
FROM lineage_catalog.columns
WHERE upstream_count = 0
  AND is_derived = TRUE
ORDER BY table_name;
```

**Fix:** For black-box transformations, add manual lineage annotations in the catalog. For Python UDFs, add explicit `OpenLineage.add_column_lineage()` calls in the transformation code.

**Prevention:** Avoid dynamic SQL and stored procedures for transformations that require lineage. Prefer dbt or Spark which have better static analysis support.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `ETL vs ELT` — lineage tracks the transformations ETL/ELT pipelines perform
- `Data Catalog` — lineage is typically surfaced through the catalog UI

**Builds On This (learn these next):**
- `Data Governance` — uses lineage to enforce data policies at each transformation step
- `Data Quality` — lineage identifies which upstream source caused a downstream quality issue

**Alternatives / Comparisons:**
- `Data Fabric` — active metadata layer that includes automated lineage as one of its capabilities
- `Application Tracing (OpenTelemetry)` — code lineage analogy; same directed-graph concept applied to service call chains

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Directed graph tracking data origin,     │
│              │ every transformation, and every consumer │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No way to debug data anomalies or prove  │
│ SOLVES       │ regulatory provenance without it         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Column-level lineage enables 5-minute    │
│              │ root cause vs 2-day manual investigation │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Debugging data quality; impact analysis; │
│              │ regulatory compliance (BCBS 239, SOX)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Value-level lineage for non-regulated    │
│              │ use cases — too expensive for low ROI   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Debugging speed + compliance vs          │
│              │ infrastructure cost + maintenance burden │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The audit trail that turns data         │
│              │  forensics from archaeology into GPS"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Catalog → Data Governance →         │
│              │ Data Quality                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your company's BCBS 239 audit requires you to prove, for any risk figure in any report, the complete chain of data from source system to final number — including every transformation step, every join, and every aggregation, at column level. Your current stack has: Oracle OLTP → PL/SQL stored procedures → Hadoop → Spark → Hive → Tableau. Which parts of this chain are addressable by existing lineage tools and which are "lineage black boxes"? Design the minimum viable lineage architecture that achieves auditability across this specific stack.

**Q2.** A data engineer proposes deleting the `stg.raw_transactions` table to save storage cost ($4,000/month). Impact analysis using your lineage graph shows 47 downstream datasets depend on it — spanning 3 data warehouses, 12 dashboards, and 2 ML models. However, the lineage graph was last fully updated 6 months ago. How do you validate whether the lineage graph is complete and accurate before making this deletion decision, and what is your go/no-go framework?

