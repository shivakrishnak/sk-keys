---
layout: default
title: "Fact Table vs Dimension Table"
parent: "Data Fundamentals"
nav_order: 517
permalink: /data-fundamentals/fact-table-vs-dimension-table/
number: "0517"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Dimensional Modeling, Star Schema, Data Modeling, OLTP vs OLAP
used_by: Star Schema, Snowflake Schema, Data Warehouse, SCD
related: Star Schema, Dimensional Modeling, SCD, Data Warehouse, OLTP vs OLAP
tags:
  - dataengineering
  - intermediate
  - database
  - mental-model
  - architecture
---

# 517 — Fact Table vs Dimension Table

⚡ TL;DR — A fact table records business events with numeric measures; a dimension table describes the who/what/when/where context of those events.

| #517 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Dimensional Modeling, Star Schema, Data Modeling, OLTP vs OLAP | |
| **Used by:** | Star Schema, Snowflake Schema, Data Warehouse, SCD | |
| **Related:** | Star Schema, Dimensional Modeling, SCD, Data Warehouse, OLTP vs OLAP | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An analyst is handed a single `orders` table with 80 columns:
customer name, customer address, product name, product category,
brand, order date, ship date, order amount, discount, tax,
store name, store city, store country... all in one table.
Query: "Monthly revenue by product category and country."
The table has NULL in `store_city` for online orders.
`category` contains both "Laptops", "laptop", "LAPTOP".
`discount` is sometimes a decimal, sometimes a percentage string.
The data is technically there but practically unusable.

**THE BREAKING POINT:**
Without a clear separation between "what happened (numbers)"
and "who/what/when/where (descriptions)", every analytical table
becomes an unmaintainable mess. Analysts waste 80% of their time
cleaning and joining — not analysing.

**THE INVENTION MOMENT:**
The fact/dimension separation is exactly Kimball's central insight.
Separating facts (narrow, many rows, numeric) from dimensions
(wide, few rows, descriptive) creates predictable structure that
any analyst can navigate and any BI tool can understand.

---

### 📘 Textbook Definition

A **fact table** stores the quantitative measurements (facts) of
business events. It is narrow (few columns), tall (many rows),
and contains: a surrogate primary key, foreign keys to all
dimension tables, and additive numeric measures (revenue, quantity,
duration). A **dimension table** stores the descriptive attributes
(context) of business entities. It is wide (many columns), short
(fewer rows), and contains: a surrogate primary key, a business
key (natural key from source), and all descriptive attributes
denormalised into one flat table. Together, a fact table with
its surrounding dimension tables form a **star schema**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Facts are "what was measured — numbers"; dimensions are
"the context — descriptions."

**One analogy:**

> A receipt has two parts. The line items (product name, quantity,
> price) are the facts — specific, numeric, tied to that purchase.
> The receipt header (store name, address, date, cashier) is the
> dimension context — descriptive, shared across many receipts.
> You store the header info once in a dimension; receipts reference
> it. If the store moves, update the dimension — not every receipt.

**One insight:**
The single most important rule: MEASURES go in the fact table,
DESCRIPTIONS go in dimension tables. A violation — storing a
text attribute (product_name) in a fact table — guarantees that
every product name change requires updating millions of fact rows.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Facts are measurements tied to an event at a specific point
   in time — they are immutable once loaded.
2. Dimensions describe entities that persist beyond any single
   event — they can change over time (SCD).
3. Measures must be additive or their additivity must be documented.

**FACT TABLE CHARACTERISTICS:**
- **Grain**: the exact unit of one row. "One row = one order
  line item." Must be declared and enforced.
- **Foreign keys**: integer surrogate keys to each dimension.
- **Additive measures**: can SUM across any dimension.
  `revenue`, `quantity`, `discount`.
- **Semi-additive measures**: can SUM across some but not all
  dimensions. `account_balance` can SUM across accounts but
  not across time (summing daily balances is nonsensical).
- **Non-additive**: ratios, percentages. Never store —
  derive at query time.
- **Degenerate dimension**: a key that has no separate dimension
  table (e.g., `order_id` — an identifier but not a full entity).
  Stored directly in the fact table as-is.

**DIMENSION TABLE CHARACTERISTICS:**
- **Surrogate key**: integer PK, not the source business key.
  Needed for SCD Type 2 (multiple rows per entity over time).
- **Business key**: the original source system identifier
  (product_sku, customer_email). Used for ETL lookups.
- **Denormalised attributes**: all descriptive attributes
  flattened into one table, including hierarchy attributes
  (category, subcategory both in dim_product).
- **No measures**: dimension tables never contain numeric metrics.
  The presence of a numeric column in a dimension table is a
  design error.

**THE TRADE-OFFS:**
**Fact table wide (many measures):** every query returns all
needed measures without additional joins. But adding a new measure
requires an ETL change.
**Dimension table wide (many attributes):** analysts can slice
by any attribute. But wide dimensions with many rarely-used
attributes waste storage and complicate ETL.

---

### 🧪 Thought Experiment

**SETUP:**
A data engineer is building a DWH for hotel bookings.
They must decide: where does `hotel_star_rating` go —
in the fact table or in `dim_hotel`?

**IF `hotel_star_rating` IN FACT TABLE:**
Every booking row carries `hotel_star_rating = 4`. A hotel
gets renovated and upgraded to 5 stars. Now 10 million historical
booking fact rows contain `hotel_star_rating = 4` — the old
rating. Updating 10 million fact rows is expensive and loses
history. Additionally: `hotel_star_rating` is not a measure
(it's not additive), so summing it produces meaningless results.

**IF `hotel_star_rating` IN `dim_hotel`:**
`dim_hotel` has one row per hotel. `hotel_star_rating = 4`
stored once. Hotel upgraded: update one row in `dim_hotel`
(SCD Type 1 for current state OR SCD Type 2 for full history).
Query: join `fact_bookings` to `dim_hotel` → filter on
`hotel_star_rating = 5`. Zero fact table changes needed.

**THE INSIGHT:**
Any attribute that describes an ENTITY (hotel, product, customer)
belongs in the entity's dimension. Any number that describes
an EVENT (how many nights, how much revenue, how many guests)
belongs in the fact table. When in doubt: "Is this number
measuring something that happened, or describing something
that exists?" Measurement → fact. Description → dimension.

---

### 🧠 Mental Model / Analogy

> Think of a time-stamped news article. The fact table is the
> abstract of the article — the 5Ws reduced to numbers: "On date
> X (date_key), company Y (company_key) in sector Z (sector_key)
> had stock price = $124.50, volume = 2.1M shares." The dimension
> tables are the reference encyclopedias: Company Y's full profile
> (sector, CEO, founded year, HQ city), the date's context
> (trading day? holiday? fiscal quarter?). The encyclopedia never
> has the stock price — the news abstract never has the CEO name.

- "News abstract (numbers)" → fact table row
- "Encyclopedia entry" → dimension table row
- "Date key" → FK to dim_date
- "Company key" → FK to dim_company
- "Stock price and volume" → additive measures in fact table
- "CEO name, sector" → descriptive attributes in dim_company

**Where this analogy breaks down:** Unlike an encyclopedia that
is authoritative and stable, dimension tables can change over
time — a company changes sector, a CEO changes, HQ moves. This
is the Slowly Changing Dimension (SCD) problem.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Fact tables store numbers tied to events (like rows in a
spreadsheet with sales amounts). Dimension tables store
descriptions of the people and things involved (like a lookup
sheet that tells you what each customer name means). The two
types of tables work together — the fact table points to the
dimension tables for all the context.

**Level 2 — How to use it (junior developer):**
When building a dbt model, prefix fact tables with `fct_`
and dimension tables with `dim_`. Fact tables should have
numeric (INT/DECIMAL) measure columns and INTEGER FK columns.
No VARCHAR description columns in fact tables. Dimension tables
should have many VARCHAR/datetime description columns. Test for
grain integrity: validate `COUNT(*) = COUNT(DISTINCT grain_key)`
in every `fct_` model after each dbt run.

**Level 3 — How it works (mid-level engineer):**
Performance implications:
- Fact tables are partitioned by date (most recent data accessed
  most often; partition pruning skips old partitions).
- Dimensions are broadcast-joined in Spark/BigQuery (small enough
  to copy to each executor).
- Fact table column count should be minimised (10–20 columns):
  fewer columns = fewer bytes per row = more rows per disk block
  = better cache efficiency for full scans.
- Dimension tables can be wide (50+ descriptive columns):
  accessed as point lookups, not scanned for aggregations.
- Clustered/sorted keys on fact tables: `(date_key, product_key)`
  grouping means range scans touch fewer disk blocks.

**Level 4 — Why it was designed this way (senior/staff):**
The fact/dimension separation is a physical manifestation of
the data normalisation principle applied to an analytical context.
It's the answer to: "How do you store a billion rows of events
while keeping query JOINs fast?" The answer: make the JOIN side
(dimensions) as small as possible while making the scanned side
(fact) as narrow as possible. In a modern columnar DWH, the
fact table is stored as compressed column chunks — a 1-billion-row
fact table with 15 columns and Snappy compression might be only
40 GB (4 bytes per row per column × 15 columns × 1B rows × 0.6
compression = 36 GB). That 40 GB can be scanned at 1 GB/s →
40 seconds for a full scan. Add predicate pushdown from row
group statistics → 4 seconds. This is only possible because the
fact table contains no fat VARCHAR descriptions that would bloat
the scan.

---

### ⚙️ How It Works (Mechanism)

```
FACT TABLE (fact_hotel_bookings) — narrow, many rows:
┌──────────────────────────────────────────────────────┐
│booking_key│date_key│hotel_key│customer_key│nights│rev│
│1          │20240115│42       │8901        │3     │450│
│2          │20240115│42       │8902        │1     │150│
│3          │20240115│57       │8903        │7     │840│
│...        │...     │...      │...         │...   │...│
│1 billion rows × 7 columns × ~28 bytes = ~28 GB       │
└──────────────────────────────────────────────────────┘

DIMENSION TABLE (dim_hotel) — wide, few rows:
┌──────────────────────────────────────────────────────┐
│hotel_key│hotel_id│name           │city │country│stars│
│42       │H-NYC-01│Park Hyatt NYC │NYC  │USA    │5    │
│57       │H-LON-03│Savoy London   │London│UK    │5    │
│...      │...     │...            │...  │...    │...  │
│10,000 rows × 30 columns × ~120 bytes = 1.2 MB        │
└──────────────────────────────────────────────────────┘
```

**Query execution (BigQuery/Spark broadcast join):**
```
Query: SELECT city, SUM(revenue) GROUP BY city

1. Read fact_hotel_bookings: hotel_key, revenue columns only
   (column pruning) → ~14 GB read

2. dim_hotel (1.2 MB) → broadcast to ALL executors
   Each executor holds dim_hotel in memory

3. Each executor probes dim_hotel hash table per fact row:
   hotel_key → city (O(1) memory lookup)

4. Local aggregation: each executor sums revenue by city

5. Final aggregation: combine executor results

Total I/O: ~14 GB (fact required columns only)
dim_hotel never touches disk on read side
```

---

### 💻 Code Example

```sql
-- Correct fact table: narrow, FK references, numeric measures
CREATE TABLE fact_hotel_bookings (
  booking_key     BIGINT PRIMARY KEY,  -- surrogate
  check_in_key    INT REFERENCES dim_date(date_key),
  hotel_key       INT REFERENCES dim_hotel(hotel_key),
  customer_key    BIGINT REFERENCES dim_customer(customer_key),
  booking_source_key INT,              -- dim_booking_source FK
  booking_id      VARCHAR(20),         -- degenerate dimension
  nights          INT,
  room_rate       DECIMAL(10,2),       -- additive fact
  total_revenue   DECIMAL(10,2),       -- additive fact
  extras_revenue  DECIMAL(10,2),       -- additive fact
  discount_amount DECIMAL(10,2)        -- additive fact
  -- NO: hotel_name (belongs in dim_hotel)
  -- NO: customer_email (belongs in dim_customer)
  -- NO: profit_margin_pct (not additive — compute at query time)
);

-- Correct dimension table: wide, descriptive
CREATE TABLE dim_hotel (
  hotel_key     INT PRIMARY KEY,      -- surrogate
  hotel_id      VARCHAR(20),          -- business key
  hotel_name    VARCHAR(100),         -- description
  brand         VARCHAR(50),          -- description
  star_rating   INT,                  -- attribute (NOT a measure!)
  city          VARCHAR(50),          -- attribute
  country       VARCHAR(50),          -- attribute
  region        VARCHAR(50),          -- denormalised from sub-dim
  is_boutique   BOOLEAN,              -- junk/flag
  opened_year   INT                   -- attribute
  -- NO: total_revenue (measure — belongs in fact table)
  -- NO: avg_nightly_rate (derived — compute at query)
);
```

---

### ⚖️ Comparison Table

| Characteristic | Fact Table | Dimension Table |
|---|---|---|
| **Row count** | Billions | Thousands to millions |
| **Column count** | Narrow (10–20) | Wide (20–50+) |
| **Column types** | FK integers + numeric measures | VARCHAR, dates, booleans |
| **Mutability** | Append-only (immutable after load) | Updated via SCD |
| **Partition strategy** | By date | Not partitioned |
| **Join type** | Scanned (large side) | Broadcast (small side) |
| **Grain** | Explicitly declared | N/A (one row per entity) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Numeric columns belong in fact tables | Numeric descriptive attributes (hotel_star_rating, product_weight) belong in dimension tables — only EVENT MEASURES (what was transacted) belong in facts |
| Dimension tables are always small | A customer dimension with 500M customers is not small — but it is still narrow (few columns per row) and still a dimension, not a fact |
| Fact tables can contain text | Fact tables should contain only INTEGER keys, numeric measures, and at most one degenerate dimension (transaction ID). Any text description belongs in a dimension |
| Surrogate keys are optional | Natural/business keys as PKs in dimensions fail for SCD Type 2 which requires multiple rows per entity. Surrogate integer keys are mandatory |
| One dimension table per concept | A concept (customer) can have multiple dimension tables — one per source system (SCD handling) or one for current state + one for historical states |

---

### 🚨 Failure Modes & Diagnosis

**Descriptive Columns in Fact Table**

**Symptom:**
`fact_orders` has `product_name VARCHAR(100)` column. A product
is renamed. 20 million fact rows show the old name. Reports
are inconsistent — some queries return old names, some new.

**Root Cause:**
Product name was stored denormalised in the fact table. There
is no single source of truth for the current product name.

**Diagnostic Command / Tool:**
```sql
-- Find non-numeric, non-key columns in fact tables
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'fact_orders'
AND data_type IN ('varchar','char','text')
AND column_name NOT LIKE '%_key'
AND column_name NOT LIKE '%_id';
-- Any result = potential design violation
```

**Fix:**
Migrate product_name to `dim_product`. Back-fill `product_key`
in fact table using source data lookup.

**Prevention:**
Code review gate: any PR adding a VARCHAR/TEXT column to a
`fct_` table requires explicit sign-off justifying it.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dimensional Modeling` — the broader methodology that
  defines what facts and dimensions are
- `Star Schema` — the pattern that uses facts and
  dimensions together
- `Data Modeling` — the overall discipline within which
  facts and dimensions are a specific paradigm

**Builds On This (learn these next):**
- `SCD (Slowly Changing Dimension)` — how to handle changes
  to dimension attributes over time
- `Data Warehouse` — the storage system that houses
  fact and dimension tables
- `OLTP vs OLAP` — the fundamental workload distinction
  that explains WHY fact/dimension separation exists

**Alternatives / Comparisons:**
- `OLTP tables` — normalised tables in operational databases;
  the design opposite of the fact/dimension model
- `Wide Table (OBT)` — everything in one table; no facts/dims
  separation; simpler but harder to maintain

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fact: event measurements (numeric).       │
│              │ Dimension: entity descriptions (text)     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Mixed tables blend what-happened with     │
│ SOLVES       │ who-did-it → unmaintainable analytics     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ "Is this measuring an event, or           │
│              │  describing an entity?" → fact or dim     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building any analytics data model in any  │
│              │ data warehouse or lakehouse               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ OLTP transactional applications — use 3NF │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Query simplicity + BI compatibility vs    │
│              │ some dimension storage redundancy         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Facts are what happened, counted.        │
│              │  Dimensions are who was there, described."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SCD → Data Warehouse → Data Lakehouse     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A data engineer proposes storing `customer_lifetime_value`
(a computed dollar amount) as a column in `dim_customer`. Another
engineer says it should be in `fact_customer_snapshot` (a periodic
snapshot fact table). Both are numeric — but one design is clearly
better. Explain which design is correct, why the other violates
the fact/dimension contract, and what the correct grain for the
periodic snapshot fact table would be.

**Q2.** A `fact_clickstream` table has 5 trillion rows. An analyst
asks: "What is the average session duration for users in Germany
who clicked our checkout page?" The query joins `fact_clickstream`
to `dim_user` (50M users) and `dim_page` (10K pages). Describe
exactly which tables are broadcast-joined vs scan-joined, how
predicate pushdown reduces the fact table scan, and why storing
`user_country` directly in the fact table (denormalisation) would
help or hurt this query.

