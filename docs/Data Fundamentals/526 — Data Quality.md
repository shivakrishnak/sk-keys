---
layout: default
title: "Data Quality"
parent: "Data Fundamentals"
nav_order: 526
permalink: /data-fundamentals/data-quality/
number: "0526"
category: Data Fundamentals
difficulty: ★★★
depends_on: Data Catalog, Data Lineage, ETL vs ELT, Data Governance, Schema Registry
used_by: Data Governance, Master Data Management, Data Catalog, Data Fabric
related: Data Governance, Data Lineage, Data Catalog, Master Data Management, Schema Evolution (Data)
tags:
  - dataengineering
  - architecture
  - advanced
  - reliability
  - production
---

# 526 — Data Quality

⚡ TL;DR — Data Quality is the discipline of measuring and enforcing how fit data is for its intended use — covering dimensions like accuracy, completeness, freshness, and consistency.

| #526 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Data Catalog, Data Lineage, ETL vs ELT, Data Governance, Schema Registry | |
| **Used by:** | Data Governance, Master Data Management, Data Catalog, Data Fabric | |
| **Related:** | Data Governance, Data Lineage, Data Catalog, Master Data Management, Schema Evolution (Data) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A financial services company launches a new credit scoring model trained on 2 years of customer transaction data. Three months after deployment, the risk team notices the model's approval rate is 23% higher than expected. Investigation reveals: 18% of training records had `income` values that were NULL (default-filled with $0 during a 6-month ETL bug), inflating the "low income" population the model was trained on. The model never should have been deployed with this data. No one caught it because no automated data quality checks existed. The cost: a credit portfolio adjustment, regulatory scrutiny, and an $8M provision charge.

**THE BREAKING POINT:**
Data quality problems are invisible until they cause business failures. ETL bugs introduce silent corruption. Schema changes cause type mismatches that produce NULLs or wrong values. Source systems change without notification. Without proactive measurement, bad data propagates silently until it causes a decision failure.

**THE INVENTION MOMENT:**
This is exactly why Data Quality frameworks were formalised — systematic, automated measurement of data against quality dimensions, integrated into every data pipeline as a mandatory gate, not an afterthought.

---

### 📘 Textbook Definition

**Data Quality** is the degree to which data is fit for its intended use, measured across six standard dimensions: **Completeness** (no missing required values), **Accuracy** (values are correct relative to reality), **Consistency** (same entity has same values across systems), **Timeliness/Freshness** (data is available when needed and represents the intended point in time), **Validity** (values conform to defined format, type, and range constraints), and **Uniqueness** (no duplicate records where none should exist). Data quality management encompasses defining quality rules for each dimension, measuring them continuously, alerting on violations, and triggering remediation workflows.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data Quality is the automated health check for your data — measuring if it is correct, complete, fresh, and consistent before it is used for decisions.

**One analogy:**
> Data Quality is like food safety inspection for a restaurant kitchen. A health inspector doesn't wait for a customer to get sick to learn the kitchen has a problem — they proactively check: temperature compliance, expiry dates, hygiene standards. Each check has a pass/fail criterion. Failing a check stops the food from reaching the customer. Data quality checks are the health inspector for your data pipeline — they run before data reaches analysts, models, or reports.

**One insight:**
Data quality must be measured at every stage of the pipeline, not just at the end. A quality problem caught at the source costs $1 to fix; caught at the BI dashboard it costs $100; caught after a business decision is made it costs $10,000. Quality must be "shifted left" into the ingestion and transformation layer.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A quality problem is always either a *measurement* problem (we are not measuring the right dimension) or a *enforcement* problem (we measure but do not act on violations).
2. Data is high quality only relative to a specific use case — "good enough for operational reporting" may be insufficient for a credit scoring model.
3. Quality measurement without lineage is incomplete — a quality violation in a derived table has a root cause upstream that must be traced.

**DERIVED DESIGN:**
A complete data quality system has four components:

**1. Quality rules (what to measure):**
- Schema / type rules: column `revenue_usd` must be DECIMAL(12,2), non-NULL
- Range rules: `age` must be between 0 and 150
- Uniqueness: `order_id` must be unique per day
- Referential integrity: `product_key` must exist in `dim_product`
- Distribution shift: row count for today's partition must be within ±20% of 7-day average
- Freshness: `last_updated` must be < 2 hours ago

**2. Measurement (when and how):** Quality checks run as pipeline stages (dbt tests, Great Expectations), scheduled jobs (Monte Carlo), or streaming checks on each micro-batch write.

**3. Alerting and escalation:** Rule violations → alert → pipeline blocked or warning-only → paged to owning team.

**4. Remediation:** Root cause via lineage → fix at source → re-process affected partitions.

**THE TRADE-OFFS:**
**Gain:** Silent data corruption caught before business impact; regulatory compliance; audit defensibility; analyst trust in data.
**Cost:** Quality checks add pipeline latency; defining good quality rules requires domain knowledge; overly strict rules cause false-positive pipeline failures; maintaining rules as schemas evolve requires ongoing effort.

---

### 🧪 Thought Experiment

**SETUP:**
A daily ETL job loads `silver.customer_events` from `raw.app_logs`. Yesterday's source had a schema bug: `event_type` was accidentally typed as an integer instead of a string. The pipeline ran, loaded 500,000 rows, and a downstream ML model retrained on the polluted data.

**WHAT HAPPENS WITHOUT DATA QUALITY CHECKS:**
The schema mismatch caused all `event_type` values to be cast to NULL (default integer→string cast failed silently). The ML model retrained on data where 100% of event_type values are NULL. Model predictions degrade silently — no alert fires. 3 weeks later, a product manager notices conversion rates are down 18%. A 6-hour postmortem traces the issue back to the data bug buried in 3 weeks of now-corrupted history.

**WHAT HAPPENS WITH DATA QUALITY CHECKS:**
A schema validation check runs immediately after load: `ASSERT TYPE(event_type) = STRING`. It fails. The pipeline halts. An alert fires to the data platform team. The raw source team is notified. The silver table is left with the last-known-good data. The ML model is NOT retrained. The bug is fixed, the source is re-exported, the pipeline re-runs. Total blast radius: zero downstream impact, resolved in 4 hours.

**THE INSIGHT:**
A quality gate at the pipeline boundary is the firewall between a data bug and a business impact. Every hour a quality problem lives in production is a multiplicative risk.

---

### 🧠 Mental Model / Analogy

> Data Quality is like a multi-stage assembly line quality gate. In car manufacturing, sensors check every component at each assembly stage — the chassis weld at station 2, the engine fit at station 7, the final paint at station 22. A defect detected at station 2 costs minutes to fix. A defect detected at final inspection costs days (rework the paint, re-inspect everything). A defect that reaches the customer costs millions (recall). Data pipelines have the same economics: check quality at every stage of transformation, not just at delivery.

**Mapping:**
- "Assembly line stages" → ETL pipeline stages (raw → staging → silver → gold)
- "Assembly line sensors" → data quality checks (dbt tests, Great Expectations suites)
- "Component spec" → quality rule definition (type, range, uniqueness, freshness)
- "Halt the line on defect" → pipeline block on quality violation
- "Customer recall" → data error discovered after a business decision is made

**Where this analogy breaks down:** An assembly line produces output from scratch; data pipelines carry historical data — a defect caught late may require re-processing months of history, not just the defective batch.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Data Quality means making sure the data used for decisions is correct, complete, and up-to-date. It is a system of automatic checks that runs in every data pipeline to catch problems before they affect reports or models.

**Level 2 — How to use it (junior developer):**
In a dbt project, you define quality tests in YAML: `not_null`, `unique`, `accepted_values`, `relationships`. These run after every dbt build and fail loudly if violated. In Great Expectations, you define an Expectation Suite (a collection of quality rules) and run it as a pipeline step. A violation returns a failure result that stops the downstream load.

**Level 3 — How it works (mid-level engineer):**
dbt tests generate queries that return rows on failure: `SELECT COUNT(*) FROM table WHERE column IS NULL` — a non-zero result is a failure. Great Expectations stores expectations as JSON configs, runs them against a Spark or Pandas DataFrame, and produces a validation result report. Monte Carlo (ML-based) detects distribution anomalies automatically — no rule authoring needed — by learning the "normal" distribution of row counts, column distributions, and freshness over time and alerting on statistically significant deviations.

**Level 4 — Why it was designed this way (senior/staff):**
Rule-based quality checks (dbt, Great Expectations) are necessary but insufficient at scale — writing and maintaining rules for thousands of columns is impossible. ML-based anomaly detection (Monte Carlo, Bigeye, Acceldata) fills the gap by learning from data patterns without explicit rules. The unsolved tension: ML anomaly detection has false positive rates typically around 5–15% — in a 1,000-column estate, that is 50–150 spurious alerts daily. Tuning sensitivity per table type (high-change tables need higher thresholds; slowly-changing dimensions need strict rules) is the current frontier. The ideal architecture combines both: rule-based for known constraints (schema, referential integrity), ML-based for unknown distribution shifts.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              DATA QUALITY FRAMEWORK                      │
├──────────────────────────────────────────────────────────┤
│  QUALITY DIMENSIONS                                      │
│  Completeness │ Accuracy │ Freshness │ Uniqueness        │
│  Validity     │ Consistency │ Distribution              │
│                                                          │
│  RULE TYPES                                             │
│  Schema     → column type, not-null, format checks      │
│  Range      → min/max value bounds                      │
│  Uniqueness → no duplicate keys                         │
│  Referential→ FK exists in dimension table              │
│  Freshness  → last-updated within SLA window            │
│  Distribution→ row count / value distribution in range  │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  MEASUREMENT LAYER                                       │
│  dbt tests      → SQL assertions, run after model build │
│  Great Expectations → Python, run in pipeline step      │
│  Monte Carlo    → ML anomaly detection, no rules needed │
│  Soda Core      → YAML-defined checks on any engine     │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  QUALITY GATE                                            │
│  PASS → pipeline continues → data promoted to next zone │
│  FAIL → pipeline halts → alert fired → team notified   │
│  WARNING → logged → pipeline continues (soft gate)      │
│                     ↓                                   │
├──────────────────────────────────────────────────────────┤
│  OBSERVABILITY                                           │
│  Quality score per dataset (% checks passing)           │
│  Trend over time (improving/degrading?)                 │
│  Root cause via lineage (which upstream source failed?) │
│  Incident history and remediation log                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Raw Ingest → [QUALITY GATE 1: schema+type checks]
           → Silver Transform → [QUALITY GATE 2: business rules]
           → Gold Aggregation → [QUALITY GATE 3: distribution checks]
           → BI / ML consumption
```

**FAILURE PATH:**
```
QUALITY GATE 1 fails → pipeline halted
→ alert to owning team
→ lineage traced to source bug
→ source fixed → pipeline re-run from raw
→ downstream tables unaffected (never promoted)
```

**WHAT CHANGES AT SCALE:**
At 10,000 columns across hundreds of tables, rule-based check authoring is infeasible. ML-based anomaly detection handles the unknown unknowns. Quality check execution must be parallelised; running all checks serially in a single pipeline step adds unacceptable latency. At petabyte scale, quality checks must use sampling (check 1% of rows for distribution checks) to remain economically viable — full-scan quality checks are too expensive.

---

### 💻 Code Example

Example 1 — dbt schema tests (YAML):
```yaml
# models/schema.yml
models:
  - name: silver_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      - name: revenue_usd
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 1000000
      - name: status
        tests:
          - accepted_values:
              values: ['PENDING', 'COMPLETE', 'CANCELLED']
      - name: product_key
        tests:
          - relationships:
              to: ref('dim_product')
              field: product_key
```

Example 2 — Great Expectations validation (Python):
```python
import great_expectations as gx

context = gx.get_context()
ds = context.get_datasource("spark_datasource")
batch = ds.get_batch(path="s3://lake/silver/orders/")

# Run expectation suite
results = context.run_checkpoint(
    checkpoint_name="silver_orders_daily",
    batch_request=batch
)

if not results["success"]:
    raise ValueError(
        f"Data quality failed: "
        f"{results['statistics']['unsuccessful_expectations']} "
        f"checks failed. Halting pipeline."
    )
```

Example 3 — Soda Core check definition (YAML):
```yaml
# checks for silver_orders
checks for silver_orders:
  - row_count > 0
  - missing_count(order_id) = 0
  - duplicate_count(order_id) = 0
  - min(revenue_usd) >= 0
  - freshness(created_at) < 2h
  - anomaly score for row_count < default  # ML anomaly
```

Example 4 — Distribution shift detection query:
```sql
-- Compare today's row count to 7-day moving average
WITH daily_counts AS (
    SELECT DATE(created_at) AS dt,
           COUNT(*) AS row_count
    FROM silver_orders
    WHERE created_at >= CURRENT_DATE - 8
    GROUP BY dt
),
baseline AS (
    SELECT AVG(row_count) AS avg_count,
           STDDEV(row_count) AS std_count
    FROM daily_counts WHERE dt < CURRENT_DATE
)
SELECT
    d.row_count,
    b.avg_count,
    ABS(d.row_count - b.avg_count) / NULLIF(b.std_count, 0)
        AS z_score
FROM daily_counts d, baseline b
WHERE d.dt = CURRENT_DATE
  AND ABS(d.row_count - b.avg_count) / NULLIF(b.std_count, 0) > 3;
-- z_score > 3 → statistical anomaly → alert
```

---

### ⚖️ Comparison Table

| Tool | Approach | Rule Authoring | Best For | Weakness |
|---|---|---|---|---|
| **dbt tests** | SQL assertions | YAML + SQL | dbt model validation | No ML anomaly detection |
| Great Expectations | Python expectations | Python/JSON | Complex validation logic | Verbose config |
| Soda Core | YAML checks | YAML | Simple, readable checks | Less ML capability |
| Monte Carlo | ML anomaly detection | Auto-learned | Unknown distribution shifts | False positives |
| Bigeye | ML + rule-based | Hybrid | Full observability | Cost |

**How to choose:** Use dbt tests as the baseline for any dbt project — free and integrated. Add Soda or Great Expectations for complex business logic. Add Monte Carlo/Bigeye for anomaly detection on high-value tables where unknown issues are the risk.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Data quality checks slow down pipelines too much | Checks run asynchronously or on samples; the cost of a bad data incident dwarfs any pipeline latency added |
| If the source data is clean, quality checks are unnecessary | Even perfect source data can be corrupted by transformation bugs, schema mismatches, or ETL failures — checks belong on every stage |
| A high quality score means data is accurate | Quality scores measure rule compliance; a rule that says "revenue > 0" can pass while revenue values are systematically off by 10% due to a wrong FX conversion |
| Quality checks are only for analytics data | Operational data feeding ML models or real-time APIs needs quality checks even more urgently — operational failures are higher stakes |
| Data quality is a one-time project | Quality degrades continuously as sources change; quality management is ongoing operational work, not a project with an end date |

---

### 🚨 Failure Modes & Diagnosis

**Silent NULL Propagation**

**Symptom:** Revenue KPI drops 30% overnight; no pipeline failure alerts fired.

**Root Cause:** A source column changed from `NOT NULL DEFAULT 0` to nullable. ETL silently loaded NULLs. SUM(revenue) returns NULL propagated values. No `not_null` check existed for that column.

**Diagnostic Command / Tool:**
```sql
SELECT COUNT(*) AS null_count,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM silver_orders)
           AS null_pct
FROM silver_orders
WHERE revenue_usd IS NULL;
-- Non-zero result confirms the issue
```

**Fix:** Add `not_null` check on all financial metric columns as a mandatory standard.

**Prevention:** Standardise: all numeric business metric columns must have `not_null` checks. Run `dbt test` as a required CI step before any pipeline is promoted.

---

**Distribution Anomaly Not Detected Until Report**

**Symptom:** Weekly report shows 3× normal number of orders for Tuesday.

**Root Cause:** A bug in the ingestion job caused Tuesday's data to be loaded three times (no idempotency enforcement). Row count tripled. No distribution check existed.

**Diagnostic Command / Tool:**
```sql
SELECT DATE(created_at), COUNT(*)
FROM silver_orders
WHERE created_at >= CURRENT_DATE - 7
GROUP BY 1 ORDER BY 1;
-- Tuesday's count is 3× other days → tripled data
```

**Fix:** Add a row count anomaly check (`z_score > 3 → alert`). Add idempotency to the ingestion job (deduplicate on primary key after load).

**Prevention:** All ingestion jobs must be idempotent. Add distribution checks to all high-value tables.

---

**Quality Check Failure Storm (Over-Sensitive Rules)**

**Symptom:** 300 quality check failures fire on Monday morning; data team is flooded with alerts; real issues are buried in noise.

**Root Cause:** Row count checks for the weekend have very low thresholds (`> 100 rows`); legitimately low weekend data volumes trigger them every Monday.

**Diagnostic Command / Tool:**
```bash
# Count alert volume by check type
dbt test --select silver_orders 2>&1 | grep "FAIL" | \
  sort | uniq -c | sort -rn | head -20
```

**Fix:** Set quality check thresholds based on historical data profiles (use 7-day moving average ± 2σ, not fixed thresholds). Separate weekday from weekend baselines.

**Prevention:** Review all quality rule thresholds quarterly and tune to reduce false positive rate below 5%.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `ETL vs ELT` — quality checks integrate into ETL/ELT pipeline stages
- `Data Lineage` — required for root-cause analysis of quality violations

**Builds On This (learn these next):**
- `Data Governance` — quality rules are governed policies; governance defines quality standards
- `Master Data Management` — MDM uses data quality checks to enforce golden record standards

**Alternatives / Comparisons:**
- `Data Observability` — extends quality monitoring with end-to-end pipeline health monitoring; superset of data quality
- `Schema Registry` — enforces schema validity (a subset of quality) for streaming data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Systematic measurement of data fitness:  │
│              │ completeness, accuracy, freshness, etc.  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Bad data propagates silently until it    │
│ SOLVES       │ causes a business or model failure       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Quality must be checked at every stage   │
│              │ not just at delivery — shift left        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every data pipeline should      │
│              │ have quality gates; no exceptions        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid overly strict rules that cause     │
│              │ false-positive alert storms              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Data trust + business protection vs      │
│              │ rule maintenance cost + pipeline latency │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The food safety inspector for your      │
│              │  data — before it reaches the customer"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Governance → Data Observability →   │
│              │ Master Data Management                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your ML team trains a churn prediction model nightly using the last 90 days of `silver.customer_events`. The data quality score for this table is 99.2% — 2 checks pass out of 250, failing on two minor referential integrity violations. The model's AUC drops from 0.87 to 0.71 over 3 months without any alert firing. What class of data quality problem is invisible to the existing rule-based checks, why does it not trigger quality failures, and what monitoring approach would detect it?

**Q2.** You have 1,200 tables in your data platform. Writing quality rules for each table requires approximately 30 minutes of a data engineer's time per table. That is 600 person-hours of rule authoring just for the initial setup, plus ongoing maintenance. Propose a feasible strategy to achieve 90% quality coverage across 1,200 tables within 60 days with a team of 3 data engineers — specifying exactly which tables get rule-based checks, which get ML-based monitoring, and what the triage criteria are.

