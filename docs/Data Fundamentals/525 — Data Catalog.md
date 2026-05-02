---
layout: default
title: "Data Catalog"
parent: "Data Fundamentals"
nav_order: 525
permalink: /data-fundamentals/data-catalog/
number: "0525"
category: Data Fundamentals
difficulty: ★★★
depends_on: Data Lake, Data Warehouse, Data Lineage, Data Governance, Schema Registry
used_by: Data Governance, Data Fabric, Data Quality, Data Mesh
related: Data Lineage, Data Governance, Data Quality, Data Fabric, Schema Registry
tags:
  - dataengineering
  - architecture
  - advanced
  - observability
  - database
---

# 525 — Data Catalog

⚡ TL;DR — A Data Catalog is the searchable, self-describing inventory of all datasets in an organisation — the Google search engine for your company's data.

| #525 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Data Lake, Data Warehouse, Data Lineage, Data Governance, Schema Registry | |
| **Used by:** | Data Governance, Data Fabric, Data Quality, Data Mesh | |
| **Related:** | Data Lineage, Data Governance, Data Quality, Data Fabric, Schema Registry | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A data analyst joins a company and needs to find the table that contains customer purchase history. They ask four people — three give different table names. They check Confluence (outdated). They grep the codebase for "customer_purchases" and find six tables across three databases with similar names. Which is authoritative? Which is fresh? Is `customer_order_history` the same as `cust_purchase_log`? The analyst spends 3 days before getting to any analysis. Meanwhile, a compliance officer needs to know which datasets contain PII — there is no system that answers this. They manually audit 200 tables across 6 systems over 3 weeks. A GDPR request arrives and no one knows all the places a deleted user's data lives.

**THE BREAKING POINT:**
As data estates grow — dozens of databases, hundreds of tables, multiple clouds — data findability collapses. Without a catalog, every analyst wastes hours on discovery. Every governance action requires manual survey. Every new hire loses days learning the data landscape.

**THE INVENTION MOMENT:**
This is exactly why the Data Catalog was created — a central, searchable, auto-populated index of all datasets, their schemas, quality, ownership, lineage, and classification.

---

### 📘 Textbook Definition

A **Data Catalog** is a metadata management system that provides an organised, searchable inventory of all data assets in an organisation. It stores technical metadata (schema, data types, column statistics, row counts), business metadata (definitions, ownership, domain classification, tags), operational metadata (last updated, pipeline job, freshness), and governance metadata (PII classification, access policies, retention rules). A modern active catalog auto-populates metadata via crawlers and lineage pipelines rather than relying solely on manual curation. It is the foundational enabler of data governance, discovery, and data quality at scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Data Catalog is the company-wide index that makes every dataset findable, understandable, and trustworthy in seconds.

**One analogy:**
> A Data Catalog is like a library catalogue system. Without it, the library has thousands of books but no index — a patron wanting "books about machine learning published after 2020" must physically browse every shelf. The catalog system (Dewey Decimal, MARC record, online search) gives every book a metadata record: author, title, subject, location, edition, availability. One search returns the right shelf. A Data Catalog does the same for datasets: one search returns the right table with its schema, owner, freshness, and quality score.

**One insight:**
The difference between a useful catalog and a museum piece is curation vs automation. A catalog populated manually decays within weeks — schemas change, owners leave, descriptions go stale. A catalog with automated crawlers, lineage integration, and ML-powered suggestions stays alive. Automation is not optional; it is the defining feature of a production-grade catalog.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Data is worthless if it cannot be found and understood — findability is a prerequisite to analysis.
2. Metadata decays faster than data — owner changes, schemas evolve, quality degrades daily.
3. The catalog is the namespace for data governance — no governance policy can be applied without first knowing what data exists and where.

**DERIVED DESIGN:**
A Data Catalog stores metadata in a structured repository (graph DB or relational DB). Four metadata planes:

- **Technical metadata:** schema definitions, column types, primary keys, row counts, null rates, value distributions — populated by automated crawlers.
- **Business metadata:** human-readable definitions ("revenue_usd = gross transaction value before refunds"), business glossary terms, domain ownership, steward contacts — populated by humans or ML suggestions.
- **Operational metadata:** last_run timestamp, pipeline job ID, freshness SLA, historical run counts — populated by lineage and ETL systems.
- **Governance metadata:** PII classification, data classification (public/internal/confidential/restricted), access policy links, retention schedules — populated by policy engine + human approval.

Discovery layer: full-text search over all metadata fields + faceted filtering (domain, data type, freshness, owner). ML-powered suggestions: "this table is similar to the one you searched last week."

**THE TRADE-OFFS:**
**Gain:** Eliminates redundant discovery work; enables governance at scale; provides a single source of truth for metadata; accelerates onboarding.
**Cost:** Building and maintaining a catalog is non-trivial — crawlers must be maintained, business metadata must be curated, the catalog must be integrated with every new data source. Without cultural adoption (engineers actually using the catalog), it becomes a compliance checkbox rather than a working tool.

---

### 🧪 Thought Experiment

**SETUP:**
A new engineer joins a data team and needs to build a customer churn prediction model. They need 12 months of customer behaviour data.

**WHAT HAPPENS WITHOUT A DATA CATALOG:**
The engineer asks teammates where to find customer data. Gets conflicting answers. Finds `customer_activity` and `user_events` tables. Are they the same? Which is fresher? Are there PII columns they need to handle? Is `customer_activity` still actively updated or deprecated? Four Slack conversations, two Confluence pages (one 2 years old), and a direct database query to check `COUNT(*) WHERE date = TODAY`. Two days lost. Discovers PII columns are present only after running the model — compliance review flags it, delaying launch by 2 weeks.

**WHAT HAPPENS WITH A DATA CATALOG:**
Engineer searches catalog for "customer activity behaviour." Two results: `customer_activity_raw` (deprecated, 3 years old) and `silver.customer_events` (active, refreshed hourly, 99.8% completeness score, owner: platform team). Clicks on `silver.customer_events`. Sees: schema, sample data, PII columns marked (handled automatically), lineage showing it derives from `raw.app_events`, 12 months of history available. Requests access via catalog UI. Access granted in 4 hours. Model built in 2 days total.

**THE INSIGHT:**
The catalog collapses the distance between "I need data" and "I have the right data, with confidence." Every day of wasted discovery work represents value lost. At 100 analysts, a catalog paying back 1 hour per analyst per week = 5,200 engineering-hours saved per year.

---

### 🧠 Mental Model / Analogy

> A Data Catalog is like a well-run airport departure board. Every flight (dataset) is listed with: destination (schema), gate (storage location), departure time (last refresh), on-time status (data quality), airline (owning team), and boarding status (access). You don't need to call the airline — you just look at the board. When a flight is cancelled (dataset deprecated), it shows immediately. The board is updated in real time, not by hand.

**Mapping:**
- "Flight listing" → catalog entry for a dataset
- "Destination / gate" → schema and physical path
- "Departure time" → last refresh timestamp
- "On-time status" → freshness and quality score
- "Airline" → owning team / data steward
- "Real-time updates" → automated crawler + lineage integration

**Where this analogy breaks down:** An airport board only shows current status; a Data Catalog also needs historical context (schema evolution history, past quality metrics) and semantic search — it is a departure board and a library reference system combined.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Data Catalog is a searchable directory of all the data a company has — like a library catalogue but for databases and files. You type "customer purchase history" and immediately find which tables have that data, how fresh it is, and who owns it.

**Level 2 — How to use it (junior developer):**
When you need data, open the catalog (Alation, Collibra, dbt Catalog, Microsoft Purview, Datahub). Search for what you need. Review the dataset profile: schema, sample data, quality score, owner. Check if it has PII columns that need special handling. Request access if needed. When you build a pipeline that produces data, register it in the catalog with a description and schema contract.

**Level 3 — How it works (mid-level engineer):**
The catalog backend has: (1) a metadata store (typically Elasticsearch for search + relational DB for entity graph); (2) automated crawlers that connect to source systems (JDBC for databases, API calls for data warehouses, S3 discovery for lakes) and extract schema + statistics; (3) a lineage integration that pulls from the lineage server (Marquez/Atlas) and links pipeline jobs to dataset entities; (4) a search engine that indexes all metadata fields for full-text and faceted search; (5) a governance integration that links policy records to dataset entities.

**Level 4 — Why it was designed this way (senior/staff):**
Early catalogs (Hive Metastore, Apache Atlas) were designed as technical registries — schemas for query engines. The shift to business metadata and discovery happened when data teams realised that query engines knowing schema locations was insufficient for human findability. Modern catalogs (Alation, Collibra, DataHub) focus on "data trust" — providing quality scores, active certification, and usage popularity metrics to help analysts choose between competing datasets. The ML layer (auto-classification, relationship suggestions) emerged to address the impossible economics of manually maintaining thousands of catalog entries. DataHub (LinkedIn open-source) pioneered the push architecture — metadata is emitted by producers rather than pulled by crawlers, giving sub-minute freshness.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              DATA CATALOG ARCHITECTURE                   │
├──────────────────────────────────────────────────────────┤
│  DATA SOURCES                                            │
│  Snowflake │ S3 │ PostgreSQL │ Kafka │ dbt models        │
│       ↓         via crawlers / push metadata            │
├──────────────────────────────────────────────────────────┤
│  METADATA INGESTION LAYER                                │
│  Technical crawlers: schema, stats, row counts           │
│  Lineage events: OpenLineage / dbt artifacts             │
│  Usage logs: query logs → popular/unused tables          │
│  ML enrichment: PII tagging, glossary term matching      │
├──────────────────────────────────────────────────────────┤
│  CATALOG STORAGE                                         │
│  Entity graph: tables, columns, users, tags, glossary    │
│  Search index (Elasticsearch): full-text + facets        │
│  Metadata store (relational): structured metadata        │
├──────────────────────────────────────────────────────────┤
│  DISCOVERY LAYER                                         │
│  Search UI: keyword + filter (domain/type/freshness)     │
│  Dataset page: schema + lineage + quality + history      │
│  Glossary: business term ↔ column mapping               │
│  Stewardship: curation UI for business metadata          │
├──────────────────────────────────────────────────────────┤
│  GOVERNANCE INTEGRATION                                  │
│  Policy engine: applies rules based on tags/classification│
│  Access control: request → approval → provisioned        │
│  Compliance reports: PII inventory for GDPR/HIPAA        │
└──────────────────────────────────────────────────────────┘
```

**Crawler run:** A JDBC crawler connects to Snowflake, enumerates all tables and views, extracts column names and types, computes row counts and null rates, and writes metadata records to the catalog store. This runs on a schedule (hourly for frequently-changing sources, daily for stable ones).

**Push path (DataHub model):** When a dbt model runs, it emits a metadata event (schema, lineage, run status) directly to the DataHub Metadata Service. The catalog is updated in seconds, not hours. This is the modern preferred approach.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Dataset created → Crawler runs → [DATA CATALOG ← YOU ARE HERE]
              → Metadata stored → ML enrichment
              → Search index updated → User discovers dataset
              → Access requested → Access granted → Data used
```

**FAILURE PATH:**
```
Crawler credentials expire → metadata not updated
→ catalog shows stale schema → analyst builds on wrong schema
→ observable: dataset page shows "last crawled: 14 days ago"
→ missing freshness indicator alerts catalog admin
```

**WHAT CHANGES AT SCALE:**
At 10,000+ datasets, full-text search performance degrades without tuned Elasticsearch mappings and sharding. Crawler scheduling must be prioritised (high-change tables crawled hourly, archive tables weekly). The business metadata contribution model must be incentivised — at scale, curating descriptions for 10,000 columns requires ML assistance (auto-generated descriptions from column name + statistics + similar columns).

---

### 💻 Code Example

Example 1 — DataHub Python SDK: emit metadata:
```python
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass, OwnershipClass,
    OwnerClass, OwnershipTypeClass
)

emitter = DatahubRestEmitter("http://datahub:8080")

# Emit dataset properties
emitter.emit_mcp(
    MetadataChangeProposalWrapper(
        entityUrn="urn:li:dataset:(urn:li:dataPlatform:snowflake,"
                  "company.silver.orders,PROD)",
        aspect=DatasetPropertiesClass(
            description="Silver-zone order events, refreshed hourly",
            customProperties={
                "team": "data-platform",
                "sla_freshness_minutes": "60"
            }
        )
    )
)
```

Example 2 — Search and discover via DataHub REST API:
```bash
# Search for datasets related to "customer"
curl -X POST "http://datahub:8080/entities?action=search" \
     -H "Content-Type: application/json" \
     -d '{
       "input": "customer purchase history",
       "entity": "dataset",
       "start": 0,
       "count": 10,
       "filters": [{"field":"origin","value":"PROD"}]
     }' | jq '.value.entities[].entity.urn'
```

Example 3 — Automated PII tagging via Purview classification rules:
```python
# Azure Purview: apply custom classification to column patterns
classification_rule = {
    "name": "CustomEmailRule",
    "kind": "RegexClassificationRule",
    "classificationName": "MICROSOFT.PERSONAL.EMAIL",
    "rulePatterns": [
        {"pattern": "[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.\\w{2,}"}
    ],
    "minimumPercentageMatch": 60.0
}
# Purview applies this rule during each scan,
# auto-tagging any matching column with the PII classification
```

---

### ⚖️ Comparison Table

| Tool | Type | Strength | Weakness | Best For |
|---|---|---|---|---|
| **DataHub (OSS)** | Push-based catalog | Real-time, open source | UI less polished | Tech teams, cloud-native stacks |
| Apache Atlas | Graph-based catalog | Hadoop ecosystem integration | Complex to operate | Hadoop/Hive environments |
| Alation | AI-assisted catalog | Strong BI + SQL intelligence | Expensive | SQL-heavy analytics teams |
| Collibra | Governance-first catalog | Policy + stewardship workflows | Very expensive | Regulated industries |
| Microsoft Purview | Cloud-native catalog | Azure integration, PII scanning | Azure-centric | Microsoft cloud shops |
| dbt Catalog | dbt-native | Auto from dbt models, free | dbt-only | Teams using dbt |

**How to choose:** Use dbt Catalog for pure dbt shops at low cost. Use DataHub for polyglot stacks needing an open-source, push-based approach. Use Collibra/Alation for regulated industries needing deep governance workflows and stewardship management.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A Data Catalog is just a list of table names | A catalog stores schema, lineage, quality, PII classification, ownership, and usage — "list of tables" is a schema registry, not a catalog |
| Once set up, the catalog maintains itself | Without ongoing curation, crawler maintenance, and cultural adoption, catalogs decay into inaccurate indexes |
| Business metadata can be fully auto-generated | ML can suggest business descriptions but human verification is required for accuracy — auto-generated descriptions are hypotheses, not facts |
| A catalog replaces documentation | A catalog and human documentation complement each other; the catalog provides structured searchable metadata, documentation provides context and reasoning |
| All catalog tools work with all data sources | Each catalog tool has different connector support; verify coverage for your specific data stack before selecting |

---

### 🚨 Failure Modes & Diagnosis

**Adoption Failure (Catalog Not Used)**

**Symptom:** Catalog is deployed and populated but engineers continue to ask teammates about data locations on Slack.

**Root Cause:** The catalog is not integrated into the workflow — finding data via catalog is slower than asking a colleague; no incentive to contribute business metadata.

**Diagnostic Command / Tool:**
```bash
# DataHub: check search query volume over time
curl "http://datahub:8080/analytics/usageStats/timeseries" \
  | jq '.bins[].value' | tail -30
# If declining → adoption problem, not technical problem
```

**Fix:** Integrate catalog links into pipeline alerting emails, BI tool dataset pickers, and incident runbooks. Make catalog the first link in the data team's onboarding guide.

**Prevention:** Define "catalog registration" as a required step in the data pipeline deployment checklist. Tie data quality SLAs to catalog entries.

---

**Stale Metadata Causing Bad Decisions**

**Symptom:** Analyst builds pipeline on `stg.orders` version in the catalog; actual table has a new column `refund_amount` not reflected. Pipeline silently produces revenue figures that exclude refunds.

**Root Cause:** Snowflake table schema changed 2 weeks ago; crawler runs weekly; catalog is 11 days stale.

**Diagnostic Command / Tool:**
```sql
-- Compare catalog schema vs actual table schema
SELECT c.column_name AS catalog_col,
       s.column_name AS actual_col
FROM catalog.columns c
FULL OUTER JOIN information_schema.columns s
  ON c.column_name = s.column_name
  AND c.table_name = 'stg.orders'
  AND s.table_name = 'orders'
WHERE c.column_name IS NULL OR s.column_name IS NULL;
-- Mismatches indicate catalog drift
```

**Fix:** Switch to push-based metadata emission (DataHub MCPs) or increase crawler frequency to hourly for high-change tables.

**Prevention:** Add a schema drift check: if catalog schema differs from actual schema, alert the catalog admin and mark the dataset as "schema drift detected" in the UI.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Data Lake / Data Warehouse` — the storage systems the catalog indexes
- `Data Lineage` — lineage populates the operational metadata shown in the catalog

**Builds On This (learn these next):**
- `Data Governance` — uses the catalog as its namespace for policies
- `Data Quality` — quality scores are surfaced through the catalog UI

**Alternatives / Comparisons:**
- `Schema Registry` — stores only schema contracts for streaming data; much narrower scope than a catalog
- `Data Fabric` — an active metadata layer that extends catalog capabilities with AI-assisted integration

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Searchable metadata inventory of all     │
│              │ data assets: schema, lineage, quality    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Data is undiscoverable, ungovernable,    │
│ SOLVES       │ and untrustworthy without a central index│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Automation keeps it alive — manual-only  │
│              │ catalogs decay to uselessness in weeks   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ >20 tables, multi-team usage, governance │
│              │ requirements, analyst onboarding cost    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-team, <10 tables, all schemas     │
│              │ known to everyone — overhead exceeds ROI │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Discoverability + governance vs          │
│              │ maintenance overhead + adoption effort   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Google Search for your company's data   │
│              │  — but only if someone keeps it updated" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Governance → Data Quality →         │
│              │ Data Fabric                              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Data Catalog has 5,000 registered datasets. Business metadata (descriptions, glossary terms) has been filled for only 800 of them — the rest have auto-generated ML descriptions that are 70% accurate. A GDPR compliance audit requires a complete, accurate PII inventory within 30 days. You have 3 data stewards available. Design the exact strategy — prioritisation criteria, human vs ML work split, validation process — to achieve 95%+ accurate PII coverage in 30 days across 5,000 datasets.

**Q2.** Two engineers on the same team independently find "customer revenue" data via the catalog — one uses `gold.customer_revenue_v1` (last updated: 6 months ago, 99% quality score) and the other uses `gold.customer_ltv_metrics` (last updated: daily, 95% quality score). They produce a joint dashboard and the two "customer revenue" lines disagree by 12%. Describe exactly how the Data Catalog should have prevented this, what metadata fields are missing, and what design changes to the catalog registration policy would prevent this class of problem in the future.

