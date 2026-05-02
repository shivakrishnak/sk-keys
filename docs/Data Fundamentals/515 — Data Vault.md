---
layout: default
title: "Data Vault"
parent: "Data Fundamentals"
nav_order: 515
permalink: /data-fundamentals/data-vault/
number: "0515"
category: Data Fundamentals
difficulty: ★★★
depends_on: Star Schema, Data Modeling, Database Fundamentals, OLTP vs OLAP
used_by: Data Warehouse, Data Governance, Data Lake
related: Star Schema, Snowflake Schema, Dimensional Modeling, Data Governance, Data Lineage
tags:
  - dataengineering
  - advanced
  - database
  - architecture
  - distributed
---

# 515 — Data Vault

⚡ TL;DR — Data Vault is an enterprise data warehouse modeling methodology that separates business keys, relationships, and descriptive attributes into distinct table types to enable auditable, source-agnostic historical data storage.

| #515 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Star Schema, Data Modeling, Database Fundamentals, OLTP vs OLAP | |
| **Used by:** | Data Warehouse, Data Governance, Data Lake | |
| **Related:** | Star Schema, Snowflake Schema, Dimensional Modeling, Data Governance, Data Lineage | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A global bank has 12 source systems: core banking, CRM, fraud
detection, credit scoring, external data feeds. Each system
has its own notion of "customer" — some use SSN, some use
account number, some use email, some use a proprietary
customer_id. The DWH team wants to integrate all 12 sources.
The star schema they built 8 years ago was designed for 3 sources.
Now each new source addition requires rearchitecting the entire
fact and dimension model to accommodate the new customer identity
scheme. When the CRM source system is decommissioned and replaced,
all historical data tied to its keys is at risk.

**THE BREAKING POINT:**
Enterprise data warehouses built on star schemas break under three
specific pressures: (1) source system changes require rescheduling
the entire ETL chain; (2) adding new data sources forces the model
to change; (3) regulatory auditors demand proof of when each piece
of data entered the warehouse and from which system. Star schemas
are excellent for query performance but poor for source-system
independence and auditability.

**THE INVENTION MOMENT:**
This is exactly why Dan Linstedt developed Data Vault in the
early 2000s. Data Vault separates concerns radically: business
keys go in Hub tables, relationships go in Link tables, and
descriptive attributes go in Satellite tables. Adding a new
source system adds new Satellite tables — no existing tables
are modified. History is inherent — every change creates a new
row with a load timestamp and source system. Auditors get a
complete chain-of-custody for every data point.

---

### 📘 Textbook Definition

**Data Vault** (Data Vault 2.0 is the current specification) is
a detail-oriented, historical tracking, uniquely linked,
normalised data modeling methodology for enterprise data
warehousing. It consists of three primary component types:
**Hubs** (store unique business keys and their hash keys — no
descriptive attributes); **Links** (store many-to-many
relationships between Hubs as sets of Hub hash keys — no
descriptive attributes); and **Satellites** (store descriptive
attributes of a Hub or Link, with full historisation via
`load_date` and `record_source` metadata). Every row in every
table carries mandatory metadata: `load_date`, `record_source`,
and a `hash_key` (MD5 or SHA-256 hash of the business key).
Satellites can be source-specific (one per source system) or
consolidated, enabling source isolation and late change capture.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data Vault keeps "what exists" (Hub), "how things relate" (Link),
and "what they look like now and historically" (Satellite)
completely separate.

**One analogy:**

> Think of Data Vault as a police evidence archive. The hub is the
> evidence register — "this case ID exists." The link is the
> chain of custody log — "case ID connected to suspect ID connected
> to location ID." The satellite is the case file itself — all
> descriptive details, each version stamped with date and
> source. You can always prove what the evidence said at any
> point in time and which investigator recorded it.

**One insight:**
Data Vault solves the enterprise problem that dimensional modeling
cannot: how do you integrate 20 source systems, each with its own
key scheme, into a single versioned, auditable store without
rewriting historical data or losing source provenance? The answer
is: separate the "key" from the "description" from the "relationship."
Each concern evolves independently.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Business keys (customer ID, product SKU) are immutable —
   they identify an entity across all time.
2. Relationships between entities change — a customer can be
   linked to different accounts over time.
3. Descriptive attributes change — a customer's address changes.
4. Every change must be auditable: who changed it, when, from
   which source.

**DERIVED DESIGN:**

*Hub (satisfies invariant 1):*
One Hub per business concept. Contains: hash_key (surrogate),
business_key, load_date (when first seen), record_source (which
system). Deliberately NO descriptive attributes. Immutable after
loading — a key once loaded is never updated.

```
hub_customer:
  customer_hash_key | customer_id | load_date | record_source
  MD5("CUST-001")   | CUST-001    | 2024-01-01| CRM
```

*Link (satisfies invariant 2):*
Junction table of Hub hash keys. Represents a relationship.
No descriptive attributes in the Link itself. New relationships
add new rows — existing Link rows are immutable.

```
link_order_customer:
  link_hash_key              | order_hash_key | customer_hash_key | load_date
  MD5(order+cust hash combo) | MD5("ORD-001") | MD5("CUST-001")   | 2024-01-15
```

*Satellite (satisfies invariants 3+4):*
Descriptive attributes for a Hub or Link. Insert-only (every
change adds a new row, never updates). Contains: parent_hash_key
(FK to Hub or Link), load_date, end_date (NULL = current),
record_source, all attributes.

```
sat_customer_crm:
  customer_hash_key | load_date   | end_date   | name  | loyalty_tier | record_source
  MD5("CUST-001")   | 2024-01-01  | 2024-06-01 | Alice | Silver       | CRM
  MD5("CUST-001")   | 2024-06-01  | NULL       | Alice | Gold         | CRM
```

**THE TRADE-OFFS:**
**Gain:** Fully auditable with chain-of-custody; adding new
source systems adds Satellite tables without changing existing
structures; source-system isolation (each source has its own
Satellite); any change is traceable to exact timestamp and source.
**Cost:** Extremely complex queries (Hub + Link + Satellite joins
for any useful attribute); requires information marts (star schema
views or materialised tables) for BI consumption; high ETL
complexity; requires specialist Data Vault expertise.

---

### 🧪 Thought Experiment

**SETUP:**
Two source systems both identify the same real-world customer:
CRM uses `customer_id = CUST-001`, banking uses `account_id =
ACC-98765`. They are the same person, discovered via a data
matching process.

**WITHOUT DATA VAULT:**
Star schema has one `dim_customer` with a surrogate key. You
must decide which business key to use as the canonical ID.
When you map CRM → DWH and banking → DWH, one system's key
becomes the master; the other is an attribute. If CRM is
decommissioned, you lose the canonical key. Historical reports
tied to the CRM key break.

**WITH DATA VAULT:**
Two separate Hubs: `hub_crm_customer` (CUST-001) and
`hub_bank_account` (ACC-98765). After identity resolution, a
Bridge table or a dedicated `link_customer_identity` links
both hash keys to the same real entity. Each source's complete
history is preserved independently. CRM decommissioned?
`hub_crm_customer` and its Satellites remain intact — historical
queries still work. Banking data remains under `hub_bank_account`.

**THE INSIGHT:**
Data Vault acknowledges that source systems are impermanent but
business keys are not. By modelling source systems as independent
pillars, it insulates the data warehouse from organisational
technology changes. This is critical for regulated industries
(banking, healthcare, government) where historical data must
remain intact for 7–10 years regardless of how many times the
source systems are replaced.

---

### 🧠 Mental Model / Analogy

> Data Vault models an enterprise like a detective's case board.
> The Hub is the person record: "this individual exists, known
> by ID #X." The Link is the connection string: "this person
> was connected to this company at this location during this
> period." The Satellite is the dossier: "here's what we knew
> about this person on Monday, here's what changed by Friday,
> here's what each source told us." Every piece of information
> has a timestamp and a source attribution. Nothing is ever
> erased — only superseded with a new entry.

- "Person record (with ID)" → Hub
- "Connection string on the board" → Link
- "Dossier pages with dates" → Satellite rows
- "Source attribution (FBI/CIA/local PD)" → record_source column
- "Nothing erased, new entry added" → insert-only Satellites

**Where this analogy breaks down:** A real detective board can
have speculative connections. Data Vault Hubs and Links contain
only facts that were loaded from actual source systems — no
inference. Inference and business rule application happen in the
Information Mart layer above Data Vault.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Data Vault is a very organised way of storing company data in
a data warehouse, specifically designed to handle data from many
different source systems while keeping a complete history of every
change. It separates "who exists" from "how they're connected"
from "what they look like" — so each part can grow and change
without breaking the others.

**Level 2 — How to use it (junior developer):**
Data Vault is implemented in three tables per business concept:
(1) Hub table with unique business key + metadata.
(2) Link table for each relationship between Hubs.
(3) Satellite table(s) for descriptive attributes with history.
ETL load order: load Hubs first (check if already exists),
then load Links, then load Satellites. Use Hash Diffs
(hash of all Satellite attributes) to detect changes —
insert Satellite row only when Hash Diff changes.
Always add `load_date` and `record_source` to every row.

**Level 3 — How it works (mid-level engineer):**
Hash keys: Data Vault 2.0 mandates hash keys (`MD5` or `SHA-256`
of business keys) as surrogate keys. Reason: hash keys are
deterministic (same business key always produces same hash),
enabling parallel load without needing a sequence generator
(which creates contention in parallel ETL).

Hash Diff: a hash of all Satellite attribute values. Compare
Hash Diff of incoming record to current Satellite row. If equal:
duplicate (skip). If different: end-date current row and insert
new row. Avoids comparing dozens of columns individually.

Multi-Active Satellites: for entities with multiple concurrent
records (e.g., one customer has multiple phone numbers
simultaneously) — standard Satellites support only one current
row. Multi-Active Satellites use a sequence number within each
load_date to handle multiple concurrent valid records.

**Level 4 — Why it was designed this way (senior/staff):**
Dan Linstedt designed Data Vault based on lessons from large
US government and financial enterprise data warehouse failures
in the 1990s. The common failure pattern: star schema DWH tightly
coupled to source system structures. When the source changed,
the DWH broke. Linstedt's insight: decouple the DWH from source
system semantics by modelling only business keys (stable) and
raw attributes (source-faithful), deferring all business rule
application to an Information Mart layer. This is equivalent to
the Strangler Pattern in microservices — the Data Vault Raw
Vault is the "anti-corruption layer" between source systems and
business consumption. The Cost: Data Vault requires significantly
more SQL joins for any business query — hence the Information
Mart. Modern Data Vault 2.0 implementations use dbt to automate
the generation of Hub/Link/Satellite tables (dbt macros for
standard patterns), reducing the manual effort that made Data Vault
v1 impractical for teams without specialist expertise.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│             DATA VAULT ARCHITECTURE                  │
│                                                      │
│  SOURCE SYSTEMS → STAGING → RAW VAULT → INFO MART   │
│                                                      │
│  RAW VAULT:                                          │
│                                                      │
│  hub_customer        link_order_customer             │
│  ┌──────────────┐    ┌──────────────────────────┐    │
│  │cust_hash_key │    │link_hash_key             │    │
│  │customer_id   │◄───│customer_hash_key (FK)    │    │
│  │load_date     │    │order_hash_key    (FK)    │    │
│  │record_source │    │load_date                 │    │
│  └──────────────┘    │record_source             │    │
│                      └──────────────────────────┘    │
│  sat_customer_crm                                     │
│  ┌─────────────────────────────────────────────────┐ │
│  │cust_hash_key (FK) │load_date │rec_src │name│tier│ │
│  │MD5(CUST-001)      │2024-01-01│CRM     │Alice│Sil.│ │
│  │MD5(CUST-001)      │2024-06-01│CRM     │Alice│Gold│ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  INFO MART (star schema views for BI):               │
│  SELECT h.customer_id, s.name, s.loyalty_tier,...    │
│  FROM hub_customer h                                 │
│  JOIN sat_customer_crm s USING (cust_hash_key)       │
│  WHERE s.end_date IS NULL  -- current only           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 — Hub table DDL and load:**
```sql
-- Hub: business key only
CREATE TABLE hub_customer (
  customer_hash_key  CHAR(32)     NOT NULL PRIMARY KEY, -- MD5
  customer_id        VARCHAR(50)  NOT NULL,
  load_date          TIMESTAMP    NOT NULL,
  record_source      VARCHAR(100) NOT NULL
);

-- Hub load: INSERT IF NOT EXISTS (idempotent)
INSERT INTO hub_customer
SELECT
  MD5(customer_id) AS customer_hash_key,
  customer_id,
  CURRENT_TIMESTAMP AS load_date,
  'CRM_SALESFORCE'  AS record_source
FROM staging_crm_customers s
WHERE NOT EXISTS (
  SELECT 1 FROM hub_customer h
  WHERE h.customer_hash_key = MD5(s.customer_id)
);
```

**Example 2 — Satellite load with Hash Diff:**
```sql
CREATE TABLE sat_customer_crm (
  customer_hash_key  CHAR(32)     NOT NULL,
  load_date          TIMESTAMP    NOT NULL,
  end_date           TIMESTAMP,           -- NULL = current
  record_source      VARCHAR(100) NOT NULL,
  hash_diff          CHAR(32),            -- hash of attributes
  name               VARCHAR(100),
  email              VARCHAR(200),
  loyalty_tier       VARCHAR(20),
  PRIMARY KEY (customer_hash_key, load_date)
);

-- Satellite load: only insert if attributes changed
INSERT INTO sat_customer_crm
SELECT
  MD5(s.customer_id) AS customer_hash_key,
  CURRENT_TIMESTAMP  AS load_date,
  NULL               AS end_date,
  'CRM_SALESFORCE'   AS record_source,
  MD5(CONCAT(s.name, s.email, s.loyalty_tier)) AS hash_diff,
  s.name, s.email, s.loyalty_tier
FROM staging_crm_customers s
WHERE NOT EXISTS (
  SELECT 1 FROM sat_customer_crm sat
  WHERE sat.customer_hash_key = MD5(s.customer_id)
    AND sat.end_date IS NULL
    AND sat.hash_diff = MD5(CONCAT(s.name, s.email, s.loyalty_tier))
);
```

**Example 3 — Information Mart (current view for BI):**
```sql
-- Flatten Data Vault to a star-schema-like view for BI
CREATE OR REPLACE VIEW info_customer AS
SELECT
  h.customer_id,
  s_crm.name,
  s_crm.email,
  s_crm.loyalty_tier,
  COALESCE(s_bank.account_balance, 0) AS account_balance
FROM hub_customer h
LEFT JOIN sat_customer_crm  s_crm
  ON h.customer_hash_key = s_crm.customer_hash_key
  AND s_crm.end_date IS NULL   -- current attributes only
LEFT JOIN sat_customer_bank s_bank
  ON h.customer_hash_key = s_bank.customer_hash_key
  AND s_bank.end_date IS NULL;
-- Multiple sources unified in one view
```

---

### ⚖️ Comparison Table

| Feature | Data Vault | Star Schema | 3NF |
|---|---|---|---|
| **Historical tracking** | Full (insert-only Sats) | SCD Type 2 only | Manual versioning |
| **Source system independence** | Excellent | Poor | Poor |
| **Multi-source integration** | Excellent (separate Sats) | Difficult | Difficult |
| **Query complexity** | Very high (Hub+Link+Sat) | Low (2–4 join) | Medium (6–8 join) |
| **Regulatory auditability** | Full chain-of-custody | Partial | Partial |
| **BI tool compatibility** | Via Information Marts | Excellent direct | Poor |
| **Best for** | Enterprise EDW, regulatory | Standard analytics | OLTP |

**How to choose:** Large enterprise EDW with multiple source
systems and strict regulatory auditing → Data Vault (usually
with an Information Mart layer). Standard analytics BI DWH →
star schema. OLTP applications → 3NF. If in doubt, start with
star schema; add Data Vault when source-system independence
and auditability become requirements.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Data Vault is better than star schema for everything | Data Vault adds complexity that only pays off in specific scenarios: multiple source systems, regulatory auditability, long-term history. For simple analytics, star schema is better |
| Implementing Data Vault is straightforward | Data Vault requires specialist expertise and significantly more ETL development effort. Without experienced practitioners, it produces over-engineered complexity with no benefit |
| Data Vault replaces the need for a star schema | A pure Data Vault Raw Vault is too complex for BI tools. Information Marts (star schema views) are always built on top of Data Vault for actual consumption |
| Hash keys replace all business logic | Hubs use hash keys for technical reasons (parallel loads). The business key is still the source of truth — the hash is just a deterministic surrogate |
| Data Vault is only for large companies | Data Vault 2.0 with automated tooling (dbt-vault, Automate DV) has made it accessible to smaller teams — but the architectural complexity remains |

---

### 🚨 Failure Modes & Diagnosis

**Hub Proliferation Without Linkage**

**Symptom:**
The DWH has 400 Hub tables but only 200 Link tables. Many Hubs
have no Links connecting them. Analysts cannot create any useful
queries joining customers to products. The DWH "stores everything"
but answers nothing.

**Root Cause:**
Teams loaded Hubs from every source system but didn't complete
the Link tables to model relationships. The Raw Vault is incomplete.

**Diagnostic Command / Tool:**
```sql
-- Find Hubs with no Links
SELECT h.table_name
FROM information_schema.tables h
WHERE h.table_name LIKE 'hub_%'
AND NOT EXISTS (
  SELECT 1 FROM information_schema.tables l
  WHERE l.table_name LIKE 'link_%'
  AND l.table_name LIKE '%' || REPLACE(h.table_name,'hub_','') || '%'
);
```

**Fix:**
Build missing Link tables. Prioritise Links that serve highest-
priority Information Mart views requested by BI users.

**Prevention:**
Design Links alongside Hubs from the start. Business process
analysis identifies relationships: Customer BUYS Product — this
relationship = a Link table that must exist.

---

**Missing Information Mart — BI Users Can't Query**

**Symptom:**
Data Vault is complete. BI tool generates queries. Every report
takes 5–10 minutes and the BI tool timeouts on small queries.

**Root Cause:**
BI users are querying the Raw Vault directly:
`hub_customer JOIN sat_customer JOIN link_order_customer JOIN hub_order JOIN sat_order...`
A typical report requires 15 joins across small tables with
many correlated subqueries for current-row filtering.

**Diagnostic Command / Tool:**
```sql
EXPLAIN
SELECT c.name, SUM(o.revenue)
FROM hub_customer h
JOIN sat_customer_crm s ON h.customer_hash_key = s.customer_hash_key AND s.end_date IS NULL
JOIN link_order_customer l ON h.customer_hash_key = l.customer_hash_key
JOIN hub_order ho ON l.order_hash_key = ho.order_hash_key
JOIN sat_order so ON ho.order_hash_key = so.order_hash_key AND so.end_date IS NULL
GROUP BY c.name;
-- Nested loop joins on many small tables = slow
```

**Fix:**
Build materialised Information Mart views (star schema):
```sql
CREATE MATERIALIZED VIEW mart_customer_orders AS
SELECT h.customer_id, s.name, s.loyalty_tier,
       oh.order_id, so.revenue, so.status
FROM hub_customer h
JOIN sat_customer_crm s ON ... AND s.end_date IS NULL
JOIN link_order_customer l ON ...
JOIN hub_order oh ON ...
JOIN sat_order so ON ... AND so.end_date IS NULL;
-- Refresh daily. BI tools query the mart, not the vault.
```

**Prevention:**
NEVER let BI tools query Raw Vault directly. Only Information
Marts are published to BI users. Design Information Marts
before launching the DWH to users.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Star Schema` — Data Vault information marts are star
  schemas; understanding star first clarifies the layered
  architecture
- `Data Modeling` — the full landscape of data modeling
  approaches puts Data Vault in context
- `Database Fundamentals` — hash keys, referential integrity,
  and normalisation underpin Data Vault's mechanics

**Builds On This (learn these next):**
- `Data Governance` — Data Vault's source tracking and
  chain-of-custody are pillars of data governance
- `Data Lineage` — tracing which source system contributed
  which data to which Satellite rows
- `Master Data Management` — Data Vault's Hub tables
  are natural repositories for business key mastering

**Alternatives / Comparisons:**
- `Star Schema` — simpler, faster for pure analytics; Data
  Vault is the right choice when multi-source auditability
  is required
- `Dimensional Modeling` — Kimball's methodology;
  complementary (Information Marts) not competing
- `Snowflake Schema` — normalised dimensional model; solves
  different problem than Data Vault

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Enterprise DWH modeling with Hubs (keys), │
│              │ Links (relations), Satellites (attributes)│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Star schemas break when source systems    │
│ SOLVES       │ change and cannot audit data provenance   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Separate keys from relations from         │
│              │ attributes — each evolves independently   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple source systems; regulatory audit │
│              │ requirements; 10+ year data history       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple analytics with one source; small   │
│              │ teams without Data Vault expertise        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full auditability + source independence   │
│              │ vs extreme query complexity               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Data Vault stores what happened; the     │
│              │  star schema tells you what it means."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dimensional Modeling → Data Governance →  │
│              │ Master Data Management                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A healthcare organisation uses Data Vault for their
enterprise data warehouse. After 6 years, they have 850 Satellite
tables. A regulatory audit requests: "Show us every change to
any patient's diagnosis data, when it changed, and from which
source system, for all patients admitted in 2019." Describe the
exact query pattern across Hub, Link, and Satellite tables to
answer this question, what metadata columns make this possible,
and what would make this query slow — and how would you optimise
it without compromising the Data Vault's auditability guarantees.

**Q2.** A company's Data Vault implementation has grown to 1,200
tables. The Information Mart layer has 80 dimensional views.
BI users query the Information Marts, but new mart views take
4–8 weeks to develop because each requires joining 20–30 Data
Vault tables. A new Data Vault 2.0 concept suggests using "Point-
in-Time" (PIT) tables and "Bridge" tables to pre-join Satellites
for faster mart development. Explain what a PIT table is, how
it solves the join complexity problem, what data it stores, and
the operational cost (storage + freshness) it introduces.

