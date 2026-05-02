---
layout: default
title: "ETL vs ELT"
parent: "Data Fundamentals"
nav_order: 530
permalink: /data-fundamentals/etl-vs-elt/
number: "0530"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Data Warehouse, Data Lake, OLTP vs OLAP, Data Quality, Data Lineage
used_by: Data Lakehouse, Data Mesh, Data Quality, Data Governance
related: Data Lake, Data Warehouse, OLTP vs OLAP, Data Quality, Schema Evolution (Data)
tags:
  - dataengineering
  - architecture
  - intermediate
  - tradeoff
  - bigdata
---

# 530 — ETL vs ELT

⚡ TL;DR — ETL transforms data before loading into the destination; ELT loads raw data first then transforms inside the destination — the shift reflects the rise of cheap cloud storage and powerful in-warehouse SQL engines.

| #530 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Data Warehouse, Data Lake, OLTP vs OLAP, Data Quality, Data Lineage | |
| **Used by:** | Data Lakehouse, Data Mesh, Data Quality, Data Governance | |
| **Related:** | Data Lake, Data Warehouse, OLTP vs OLAP, Data Quality, Schema Evolution (Data) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In the early 2000s, storage was expensive and compute was the warehouse appliance (Teradata). All transformation happened before the data entered the warehouse — a dedicated ETL server extracted raw records, applied business logic in custom Java code, and loaded only clean, structured output. The ETL server was the bottleneck. A new transformation requirement meant writing new Java ETL code, testing it, deploying it, re-running history. If a raw field was discarded during transformation — because nobody thought anyone would need it — it was gone forever.

**THE BREAKING POINT:**
ETL's fundamental constraint: transformation before load means the raw data is not preserved. And the ETL server is a single point of compute bottleneck for all transformation work. As cloud data warehouses (BigQuery, Snowflake, Redshift) offered massively parallel SQL engines, and cloud storage (S3) became effectively free, the constraint inverted: **store everything raw, transform with the warehouse's own compute**.

**THE INVENTION MOMENT:**
This is exactly why ELT emerged — load raw data into cheap storage first, then use the destination system's own parallel SQL engine (not a separate ETL server) to transform it. The transformation becomes a dbt model, a `CREATE TABLE AS SELECT`, or a Spark SQL job — executed at warehouse scale.

---

### 📘 Textbook Definition

**ETL (Extract, Transform, Load)** is a data integration pipeline pattern where data is extracted from source systems, transformed (cleaned, reshaped, business logic applied) outside the destination on a dedicated compute platform, and only then loaded into the destination in its final, clean form. **ELT (Extract, Load, Transform)** inverts the last two steps: raw data is extracted and immediately loaded into the destination storage (data lake or warehouse), and then transformed in-place using the destination's own compute capabilities. The choice between ETL and ELT is driven by: the cost and capability of the destination's compute, the value of retaining raw data, and the need for intermediate transformation isolation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ETL transforms before storing; ELT stores first then transforms — ELT won because storage got cheap and warehouses got powerful.

**One analogy:**
> ETL is like a restaurant prep kitchen where all ingredients are washed, peeled, and portioned before going into the main kitchen. ELT is like a new modern kitchen where you store whole unprepared ingredients in a giant walk-in fridge (cheap cloud storage) and use powerful industrial equipment (warehouse SQL engine) to prep them as needed. Old kitchens had tiny storage and powerful prep teams (ETL server). New kitchens have enormous storage and powerful in-kitchen equipment (warehouse compute).

**One insight:**
ELT's key advantage is that the destination system's compute (Snowflake, BigQuery) is often the most scalable and cost-effective compute available — far more so than a dedicated ETL server. Why pay for a separate transformation engine when the warehouse can do it at scale for free (relative to storage)?

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Data must move from source to destination at some point — extraction is always required.
2. Some transformation of data is always needed before it is analytically useful.
3. The question is not whether to transform but WHERE: in transit (ETL) or at destination (ELT).

**DERIVED DESIGN:**

**ETL Architecture:**
```
Source → Extract → [Transform: ETL Server/Spark/Python]
      → Load: only clean data → Destination (warehouse/store)
```
The transformation step can include: schema mapping, business logic (taxation rules, currency conversion), deduplication, PII masking. The destination receives only validated, final-form data.

**ELT Architecture:**
```
Source → Extract → Load: raw data → Destination (lake/warehouse)
      → [Transform: SQL/dbt/Spark running inside destination]
      → Clean/aggregated tables in same destination
```
The destination holds both raw data and transformed views/tables simultaneously. Transformation is SQL (dbt models, CTAS) executed on the warehouse's MPP engine.

**THE TRADE-OFFS:**

ETL **Gains:** Destination receives only clean data; PII masking at pipeline boundary (raw PII never lands in warehouse); transformation logic in a controlled compute environment.
ETL **Costs:** Raw data lost if discarded during transformation; dedicated ETL compute adds cost; transformation bottleneck; harder to reprocess history when logic changes.

ELT **Gains:** Raw data always preserved (reprocessable); transformation logic as SQL in version-controlled dbt models; leverage warehouse's MPP compute; no separate ETL server.
ELT **Costs:** Raw PII lands in destination (governance risk); destination must be large enough to hold raw + transformed; transformation errors are downstream, not caught at ingestion.

---

### 🧪 Thought Experiment

**SETUP:**
A product team decides they need a new metric: "first purchase within 24 hours of signup." This metric requires the raw signup timestamp and first order timestamp from the events table.

**WHAT HAPPENS WITH ETL (old approach):**
The ETL pipeline was built 18 months ago. The transformation step extracted only `user_id`, `order_total`, and `product_category` from the events table — the signup and first-order timestamps were deemed "unnecessary" at the time and were discarded during transformation. They are gone. To get the new metric, the team must: re-extract 18 months of raw events from the source OLTP system (if it still has them), re-write the ETL to include timestamps, re-run the historical backfill. Time to metric: 6 weeks.

**WHAT HAPPENS WITH ELT (modern approach):**
The raw events were loaded to S3/Snowflake staging with all fields preserved (ELT default: load everything). The transformation layer is a dbt model. The team writes a new dbt model:
```sql
SELECT user_id, MIN(order_ts) - signup_ts AS time_to_first_purchase
FROM raw.events WHERE event_type IN ('SIGNUP', 'ORDER')
GROUP BY user_id, signup_ts
```
Run the model. 18 months of history backfilled in 4 minutes. Time to metric: 1 day.

**THE INSIGHT:**
The field that was "unnecessary" today becomes the most valuable field tomorrow. ELT's "store raw, transform later" philosophy eliminates the risk of premature field discarding. Every field is potentially valuable — storage is cheap enough to keep them all.

---

### 🧠 Mental Model / Analogy

> ETL is like a customs agent who opens every shipment, removes prohibited items, and only lets the approved items through. ELT is like an airport warehouse that receives every shipment first, stores it all, and then customs officers process it using the warehouse's own facilities. The ETL country has a strict border; the ELT country has a large warehouse and customs happen inside.

**Mapping:**
- "Customs agent at border" → ETL transformation engine (external to destination)
- "Cleared goods only" → only transformed/valid data in destination
- "Airport warehouse" → data lake / staging area in destination
- "Customs inside warehouse" → dbt/Spark SQL transformation inside destination
- "Prohibited items seized at border" → raw data discarded during ETL transformation

**Where this analogy breaks down:** In customs, prohibited items are blocked for safety; in ETL, discarded fields are not "dangerous" — they just weren't deemed valuable at the time. This makes ETL's discard decision far more regrettable in retrospect.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
ETL: clean the data before putting it in storage. ELT: put all the raw data in storage first, then clean it later when needed. Modern systems prefer ELT because storage is cheap and the cleaning tools inside the warehouse are very powerful.

**Level 2 — How to use it (junior developer):**
In a modern ELT setup, you use Fivetran or Airbyte to extract and load raw data from sources (CRM, ERP, databases) directly into Snowflake/BigQuery. Then dbt models define the transformations as SQL SELECT statements that are run as scheduled jobs inside Snowflake. The raw tables (prefixed `raw_`) coexist with the dbt-transformed clean tables (`stg_`, `dim_`, `fact_`). You never touch the raw tables in production queries — only dbt models do.

**Level 3 — How it works (mid-level engineer):**
An ELT pipeline has: (1) **Extract:** Fivetran / custom connector reads source records. Supports CDC (change data capture) via DB log reading for near-real-time updates. (2) **Load:** raw records written to staging area (S3 or warehouse staging tables) with all fields including schema metadata, usually in Parquet or JSON. (3) **Transform:** dbt SQL models run as `CREATE TABLE AS SELECT` or `INSERT OVERWRITE` statements on the warehouse. Incremental dbt models use `WHERE loaded_at > last_run` to process only new records. A dbt DAG defines the dependency order of models — from raw → staging → intermediate → mart.

**Level 4 — Why it was designed this way (senior/staff):**
ETL was the only option in the 1990s when warehouse storage was $1,000+/GB (Teradata appliances) — you could not afford to store raw data. The ETL pattern encoded business logic in integration code (COBOL then Java) rather than SQL, which made it hard for data analysts to modify. The dbt revolution (2016+) codified that transformation should be SQL by analysts, not Java by engineers, living in version-controlled repositories. ELT + dbt has become the dominant modern pattern because: storage is $0.02/GB/month on S3; warehouse SQL is MPP-scalable; dbt gives analysts ownership over transformation logic; raw data is preserved for reprocessing; and the whole transformation dependency tree is documented as code.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  ETL ARCHITECTURE                                        │
│                                                          │
│  Source DB ──► ETL Server (Java/Python/Spark) ──►       │
│                [Transform in transit]                    │
│                  - clean records only                    │
│                  - PII masked at boundary                │
│                  - raw data NOT stored                   │
│              ──► Destination Warehouse (clean only)      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ELT ARCHITECTURE                                        │
│                                                          │
│  Source DB ──► Fivetran/Airbyte/Kafka ──►               │
│                  Load: all fields, raw format            │
│              ──► raw.orders (Snowflake staging)          │
│                                                          │
│  dbt runs inside Snowflake:                              │
│  raw.orders → stg_orders (validated, typed)             │
│  stg_orders + stg_products → fact_orders (star schema)  │
│  fact_orders → mart_revenue (aggregated)                │
│                                                          │
│  BI Tool reads mart_revenue only                         │
│  Raw data remains available for backfills/ML            │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (ELT):**
```
Source (Postgres) → Fivetran (extract + load)
→ raw.orders in Snowflake ← YOU ARE HERE (Load step)
→ dbt run: stg_orders → fact_orders → mart_revenue
→ Looker reads mart_revenue → dashboard
```

**FAILURE PATH:**
```
dbt model fails → fact_orders not updated
→ mart_revenue shows stale data
→ raw.orders is unaffected (still current)
→ observable: dbt run failure in CI/CD log, Slack alert
→ fix the model, re-run dbt — raw data intact
```

**WHAT CHANGES AT SCALE:**
At petabyte-scale raw staging, COPY INTO / bulk load performance becomes the bottleneck. Parallel loads with partition-key routing, and micro-batch Snowpipe for streaming ingestion, are required. dbt incremental models must be carefully designed — a full refresh of a 10B-row fact table takes hours; incremental (load only new rows) is the only viable pattern. Schema evolution in sources (new columns, renamed fields) must be handled by the load layer — Fivetran handles this automatically with schema drift detection.

---

### 💻 Code Example

Example 1 — dbt staging model (ELT transformation):
```sql
-- models/staging/stg_orders.sql
-- Runs inside Snowflake (ELT: transform in warehouse)
WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),
renamed AS (
    SELECT
        order_id::VARCHAR AS order_id,
        customer_id::VARCHAR AS customer_id,
        -- Rename and clean
        TRIM(UPPER(status)) AS status,
        -- Type cast
        created_at::TIMESTAMP AS created_at,
        -- Handle nulls
        COALESCE(revenue_usd, 0) AS revenue_usd
    FROM source
    WHERE order_id IS NOT NULL  -- Remove bad rows
)
SELECT * FROM renamed
```

Example 2 — dbt incremental model (only process new rows):
```sql
-- models/marts/fact_orders.sql
{{ config(materialized='incremental',
          unique_key='order_id') }}

SELECT
    o.order_id,
    o.customer_id,
    dp.product_key,
    dt.time_key,
    o.revenue_usd
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('dim_product') }} dp ON o.product_id = dp.product_id
JOIN {{ ref('dim_time') }} dt ON o.created_at::DATE = dt.date

{% if is_incremental() %}
  WHERE o.created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

Example 3 — Traditional ETL transformation (Python — compare to ELT):
```python
# ETL: transformation runs OUTSIDE the destination
import pandas as pd

df = pd.read_sql("SELECT * FROM source.orders", source_conn)

# Transform: mask PII, clean, apply business logic
df["email"] = df["email"].apply(lambda e: hashlib.sha256(
    e.encode()).hexdigest())
df["revenue_usd"] = df["price"] * df["quantity"] * df["fx_rate"]
df = df[df["order_id"].notna()]   # raw NOT preserved in ETL

# Load only clean data
df.to_sql("clean_orders", dest_conn, if_exists="append")
# Note: raw fields (price, quantity, fx_rate) not loaded separately
```

---

### ⚖️ Comparison Table

| Dimension | ETL | ELT |
|---|---|---|
| Where transformation runs | External engine | Inside destination |
| Raw data preserved | No | Yes |
| PII at destination | No (masked pre-load) | Yes (needs governance) |
| Reprocessing history easy | Difficult | Easy (raw always available) |
| Tools | Informatica, SSIS, GlueETL | dbt, Spark SQL, BigQuery SQL |
| Cost model | ETL compute separate | Destination compute covers all |
| Best for | Strict PII boundaries; legacy | Modern cloud warehouses / lakes |

**How to choose:** Use ELT for all modern cloud data warehouse / data lake architectures — it is simpler, cheaper, and more flexible. Use ETL only when strict data isolation requirements mandate that raw PII must never land in the destination system (e.g., a warehouse shared with third-party analysts).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| ETL and ELT produce the same result | They may produce the same output tables but ETL discards raw data; ELT preserves it. The hidden cost of ETL is raw data loss. |
| ELT just means "load messy data" | ELT still requires clean transformation — it is just done inside the destination with dbt/SQL rather than a separate engine |
| ETL is always slower | ETL on a powerful Spark cluster can be faster than ELT on a small warehouse for specific workloads |
| ELT has no governance risks | Raw PII landing in the warehouse requires column masking and access controls — governance must be applied at the destination |
| dbt is ELT | dbt is the transformation layer (the T) of ELT. The E and L are done by tools like Fivetran, Airbyte, or Kafka Connect |

---

### 🚨 Failure Modes & Diagnosis

**Schema Drift in ELT Load**

**Symptom:** dbt model fails with `Invalid column name: new_column` — a source added a column the staging model doesn't handle.

**Root Cause:** Source team added `promo_code` column without notifying the data team. Fivetran auto-added it; dbt `SELECT *` picks it up but downstream model has explicit column references that break.

**Diagnostic Command / Tool:**
```bash
dbt run --select stg_orders 2>&1 | grep "Error"
# Shows which column reference failed
```

**Fix:** Use `{{ dbt_utils.star(from=ref('raw_orders'), except=['unnecessary_col']) }}` to explicit-select with exclusions. Handle schema evolution in staging models.

**Prevention:** Enable schema-change monitoring in Fivetran. Require source teams to notify before schema changes. Use dbt schema contracts to detect new columns automatically.

---

**ETL Data Loss (Field Discarded)**

**Symptom:** 6 months after launch, an analyst needs the `referral_source` field that was in the source — it does not exist in the warehouse.

**Root Cause:** The original ETL transformation was written to extract only known-needed fields. `referral_source` was not included.

**Diagnostic Command / Tool:**
```sql
-- Check source vs destination field coverage
-- (requires access to source system)
SELECT column_name FROM information_schema.columns
WHERE table_name = 'orders'
EXCEPT
SELECT column_name FROM warehouse.raw_orders;
-- Fields in source but not in warehouse = ETL discard list
```

**Fix:** Migrate to ELT — load `SELECT *` to raw staging, then transform selectively.

**Prevention:** Default ETL pipelines to `SELECT *` from sources. Apply column filtering only in the transformation stage, not the extraction stage.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Data Warehouse` — the destination structure that ELT transforms feed
- `OLTP vs OLAP` — ETL/ELT move data between these two workload types

**Builds On This (learn these next):**
- `Data Lineage` — tracks the transformations in the ETL/ELT pipeline
- `Data Quality` — quality checks integrate into each stage of ETL/ELT

**Alternatives / Comparisons:**
- `Streaming Ingestion (Kafka/Kinesis)` — real-time alternative to batch ETL/ELT
- `Data Virtualisation` — avoids movement entirely, serving reads from source systems directly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ ETL: transform then store.               │
│              │ ELT: store raw then transform in place   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ ETL discards raw data; ELT eliminates    │
│ SOLVES       │ ETL server bottleneck using warehouse MPP│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ELT won because cloud storage is cheap   │
│              │ and warehouse SQL is massively parallel  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ ELT: cloud warehouse + dbt (default now) │
│              │ ETL: PII must not land in destination    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ ETL: avoid when raw data must be kept    │
│              │ for ML, exploration, or reprocessing     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ ELT: flexibility + raw preserved vs PII  │
│              │ governance complexity at destination     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ETL: customs at the border.             │
│              │  ELT: customs inside the warehouse."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ dbt → Data Lineage → Data Quality        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are migrating your company from a legacy ETL architecture (Java ETL server → Oracle Data Warehouse) to a modern ELT architecture (Fivetran → Snowflake → dbt). During migration, you discover that 60 business logic rules are encoded inside the Java ETL code — currency conversion, tax jurisdiction assignment, customer tier calculation — and no one has documentation of these rules. What is your migration strategy for this "hidden logic" problem, specifically how you would verify the correctness of the new dbt models against the old ETL output?

**Q2.** In an ELT architecture, raw customer PII (email, address, SSN) lands in Snowflake before any transformation applies masking. A data engineer with `SYSADMIN` role can query the raw staging tables before the dbt masking models run. Design the complete security architecture that prevents this class of privileged raw-PII access, specifically addressing: what controls exist at the Snowflake level, what process controls exist around the ingest pipeline, and how you verify that no one has queried unmasked PII by examining the audit log.

