---
layout: default
title: "Snowflake Schema"
parent: "Data Fundamentals"
nav_order: 514
permalink: /data-fundamentals/snowflake-schema/
number: "0514"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Star Schema, Data Modeling, Database Fundamentals, Dimensional Modeling
used_by: Data Warehouse, Dimensional Modeling
related: Star Schema, Data Vault, Dimensional Modeling, Fact Table vs Dimension Table, OLTP vs OLAP
tags:
  - dataengineering
  - intermediate
  - database
  - architecture
---

# 514 — Snowflake Schema

⚡ TL;DR — A snowflake schema extends a star schema by normalising dimension tables into sub-dimensions, reducing storage redundancy at the cost of more joins per query.

| #514 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Star Schema, Data Modeling, Database Fundamentals, Dimensional Modeling | |
| **Used by:** | Data Warehouse, Dimensional Modeling | |
| **Related:** | Star Schema, Data Vault, Dimensional Modeling, Fact Table vs Dimension Table, OLTP vs OLAP | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A star schema's `dim_product` has 500,000 products. Each product
belongs to a `category` and `subcategory`. In the flat star
schema, `category` and `subcategory` strings are duplicated
in every product row. "Electronics" is stored 80,000 times
(once per electronics product), "Mobile" subcategory stored
30,000 times. When "Electronics" is renamed to "Consumer Electronics",
you must update 80,000 rows. Storage for this single dimension:
every row carries 20-byte `category` string × 500,000 rows =
10 MB just for one redundant column.

**THE BREAKING POINT:**
In large enterprise data warehouses with dimensions having high
cardinality and deeply hierarchical attributes (geographic
hierarchy: city → state → country → region; product hierarchy:
SKU → subcategory → category → department → division), flat star
schema dimensions accumulate significant redundancy. A geography
dimension with 10 million cities, each carrying the full country
name and continent, stores "United States" (13 bytes) 4 million
times. Update anomalies in dimension tables are a real problem.

**THE INVENTION MOMENT:**
This is exactly why the snowflake schema was created. By normalising
dimension hierarchies into separate sub-dimension tables (a
`product_category` lookup table, a `region` lookup table), each
higher-level attribute is stored once. The schema diagram looks
like a snowflake — fact table in the centre, dimension tables
around it, sub-dimension tables branching outward.

---

### 📘 Textbook Definition

A **snowflake schema** is a variation of the star schema in which
dimension tables are **normalised** into multiple related tables,
creating a hierarchical structure. Instead of a flat `dim_product`
containing `category`, `subcategory`, and `brand` directly,
a snowflake schema has `dim_product` containing foreign keys to
`dim_category`, `dim_subcategory`, and `dim_brand` tables.
This normalisation eliminates redundancy within dimension tables
and simplifies dimension maintenance (changing a category name
requires updating one row, not thousands). The trade-off is
additional JOINs per query: a query that previously joined 4
tables in a star schema now joins 6–8 tables (4 dimensions + their
sub-dimensions).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A snowflake schema is a star schema where the dimension tables
are further split up into smaller tables — like branches of a
snowflake.

**One analogy:**

> A star schema is a rolodex where each card lists full details
> about a contact — including their company's full address,
> their industry, their country. "Microsoft, One Microsoft Way,
> Redmond, Washington, USA, Technology" written on every card
> for every Microsoft employee. A snowflake schema is an
> address book where each card just says "works at MSFT" and
> "MSFT" is a separate entry with the full address. Less
> redundancy, but finding a person's country requires two lookups.

**One insight:**
Snowflake schema is only worth doing when dimension table size
is significant AND updates to shared attributes are expected.
For most BI tools and modern columnar DWH platforms, the extra
joins are handled efficiently, equalising performance between
star and snowflake. The decision is really about data quality
and maintainability, not query speed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Normalisation eliminates update anomalies: shared attributes
   stored once cannot be partially updated.
2. Every additional join has a cost (quantified by row count
   and index availability).
3. Dimension tables in a star schema are read-heavy (many query
   joins) and write-sparse (ETL loads).

**DERIVED DESIGN:**
A star schema's `dim_product` contains both `product_id`,
`product_name`, and all the hierarchical attributes
(`category_id`, `category_name`, `subcategory_id`,
`subcategory_name`, `brand`, `brand_parent_company`...).
In a snowflake: `dim_product` has FK → `dim_category`;
`dim_category` has FK → `dim_category_group`. Each level stores
its own attributes once.

Normalisation hierarchy:
- Star: all in one flat dimension (1–2 joins)
- Snowflake: normalised dimension hierarchy (3–5 joins per query)
- Fully normalised (3NF): each table single-theme, maximum joins

**When snowflake wins over star:**
1. Dimension tables are very large (>10M rows) and high redundancy.
2. Dimension hierarchies change frequently (category restructures).
3. Storage is genuinely constrained (less common in 2024 cloud era).

**When star wins over snowflake:**
1. BI tools generate simpler SQL (many tools struggle with
   deep snowflake schemas).
2. Query performance is critical (fewer joins = faster analytics).
3. Teams prefer simplicity over theoretical normalisation purity.

**THE TRADE-OFFS:**
**Gain:** Storage savings (5–30% for redundant dimension hierarchies);
no update anomalies in dimension hierarchies; cleaner governance
when category/hierarchy trees change.
**Cost:** More JOINs per query; BI tool compatibility varies (some
tools explore star schemas better than snowflake); slightly
higher planning complexity.

---

### 🧪 Thought Experiment

**SETUP:**
`dim_product` in a star schema has 1,000,000 products.
Categories: 50. Subcategories: 200.

**STAR SCHEMA STORAGE:**
Each of 1,000,000 product rows stores:
- category_name: VARCHAR(40) × 1,000,000 = 40 MB
  (50 distinct values repeated 20,000 times each)
- subcategory_name: VARCHAR(50) × 1,000,000 = 50 MB
  (200 distinct values repeated 5,000 times each)
Total duplicated dimension data: ~90 MB (potentially much more
with deeper hierarchies).

**SNOWFLAKE SCHEMA STORAGE:**
- `dim_product`: no category text, just `category_key` INT
  × 1,000,000 rows = 4 MB.
- `dim_category`: 50 rows × 60 bytes = 3 KB.
- `dim_subcategory`: 200 rows × 70 bytes = 14 KB.
Total for same data: ~4 MB vs 90 MB. 22× less storage for
hierarchy attributes.

**QUERY IMPACT:**
Star query: `JOIN dim_product ON product_key` → 1 table.
Snowflake query: `JOIN dim_product ON product_key JOIN
dim_category ON category_key` → 2 tables.
Extra join on a 50-row table: < 1 ms overhead. Negligible
in practice.

**THE INSIGHT:**
The storage benefit of snowflake is real but shrinking — cloud
storage costs are low. The maintenance benefit (update one
category name in one row vs 20,000 rows) is the practical reason
to use snowflake today. The query overhead is negligible for
small sub-dimension tables.

---

### 🧠 Mental Model / Analogy

> Imagine a star schema as a detailed product catalogue where
> every page about a product repeats its entire category and
> subcategory description. The snowflake schema is an indexed
> catalogue: each product page says "see Category Index #42"
> and "see Subcategory Index #15" — the index has one entry
> for each category and subcategory. Less repetition, but you
> need to flip to the index page to read the full category name.

- "Category Index #42" → `dim_category` row (FK reference)
- "Product page" → `dim_product` row (with FK to dim_category)
- "Flip to index page" → JOIN to sub-dimension table
- "Updating one index entry" → updating category name once
- "Star: category name on every product page" → repeated in star dim

**Where this analogy breaks down:** Modern query engines with
good statistics and small sub-dimension tables join them faster
than flipping to a physical index page. The analogy overstates
the lookup cost — in practice, `dim_category` with 50 rows
fits in a single disk block.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A snowflake schema is a type of database design for analytics
that organises descriptions into smaller, linked tables instead
of one big table. Like a snowflake has branches — each branch
is a subtable of details. More organised, but you need to follow
more connections to get the full picture.

**Level 2 — How to use it (junior developer):**
Choose snowflake over star when your dimension has a clear
hierarchy (category → subcategory → item) where higher-level
attributes change independently. In dbt: create separate models
for `dim_product_category`, `dim_product_subcategory`, and
reference them in `dim_product` with FK columns. Use `ref()`
to maintain dependency order. Most BI tools (Tableau, Power BI,
Looker) handle snowflake schemas — just define the joins in
the semantic layer.

**Level 3 — How it works (mid-level engineer):**
The SQL transformation in a snowflake schema compared to a star:

Star query (product category in fact join):
```sql
JOIN dim_product p ON f.product_key = p.product_key
WHERE p.category = 'Electronics'  -- filter on flat dim
```

Snowflake query:
```sql
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_category c ON p.category_key = c.category_key
WHERE c.category_name = 'Electronics'  -- filter on sub-dim
```

Query optimisers handle this efficiently when `dim_category`
statistics and indices are available. Modern MPP optimisers
(BigQuery, Snowflake) automatically reorder joins and use
broadcast hash joins for small sub-dimensions — the SQL
complexity doesn't translate to execution complexity.

**Level 4 — Why it was designed this way (senior/staff):**
The snowflake vs star debate in the Kimball methodology is three
decades old. Kimball himself recommended star schema for most
cases because: (1) BI tools of the 1990s–2000s struggled with
complex join paths; (2) the query-time join cost on row-oriented
databases was real; (3) the data redundancy in dimensions was
acceptable given they are small relative to the fact table.
In 2024, the calculus changed: (1) modern MPP DWH optimisers
handle deep joins efficiently; (2) cloud storage is cheap
(redundancy cost is negligible); (3) the real cost is BI tool
ergonomics and analyst productivity. A snowflake schema in
Snowflake or BigQuery performs nearly identically to a star
schema — the remaining reason to prefer star is analyst familiarity
and BI tool semantic layer compatibility. The irony: the eponymous
cloud DWH platform "Snowflake" recommends using a star schema
in its own documentation.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│            SNOWFLAKE SCHEMA DIAGRAM                  │
│                                                      │
│  dim_brand◄──dim_product_subcategory◄──dim_category  │
│                     ↑                        ↑       │
│              dim_product──────────────────►fact_sales│
│                                        ┌────┘        │
│  dim_region◄──dim_state◄──dim_country  │  dim_date   │
│                     ↑             ↑   ↓     ↑        │
│               dim_store──────►fact_sales─────┘       │
│                                                      │
│  (Compare to star: all dim_product attributes in one │
│   flat table, no sub-dimensions)                     │
└──────────────────────────────────────────────────────┘
```

**Storage comparison:**
```
STAR dim_product (1M rows):
┌──────────┬──────────────────┬──────────────────┬──────┐
│product_id│category_name     │subcategory_name  │brand │
│1         │Electronics       │Mobile            │Apple │
│2         │Electronics       │Mobile            │Samsung│
│3         │Electronics       │Laptop            │Dell  │
│... (category_name repeated 80,000 times)              │
└──────────────────────────────────────────────────────┘

SNOWFLAKE dim_product + sub-dims:
dim_product:  product_id, category_key, subcategory_key, brand_key
dim_category: category_key=1, name="Electronics"  ← stored ONCE
dim_subcategory: subcategory_key=1, name="Mobile" ← stored ONCE
```

---

### 💻 Code Example

**Example 1 — Snowflake schema DDL:**
```sql
-- Sub-dimension tables
CREATE TABLE dim_category (
  category_key    INT PRIMARY KEY,
  category_name   VARCHAR(50),
  department      VARCHAR(50)
);

CREATE TABLE dim_subcategory (
  subcategory_key INT PRIMARY KEY,
  subcategory_name VARCHAR(60),
  category_key    INT REFERENCES dim_category(category_key)
);

-- Product dimension references sub-dimensions
CREATE TABLE dim_product (
  product_key     BIGINT PRIMARY KEY,
  product_id      VARCHAR(20),
  product_name    VARCHAR(100),
  subcategory_key INT REFERENCES dim_subcategory(subcategory_key),
  brand           VARCHAR(50),
  unit_cost       DECIMAL(10,2)
);

-- Fact table unchanged from star schema
CREATE TABLE fact_sales (
  sale_id      BIGINT PRIMARY KEY,
  product_key  BIGINT REFERENCES dim_product(product_key),
  date_key     INT,
  customer_key BIGINT,
  quantity     INT,
  revenue      DECIMAL(10,2)
);

-- Query with snowflake joins
SELECT
    c.category_name,
    SUM(f.revenue) AS revenue
FROM fact_sales f
JOIN dim_product      p  ON f.product_key     = p.product_key
JOIN dim_subcategory  sc ON p.subcategory_key  = sc.subcategory_key
JOIN dim_category     c  ON sc.category_key    = c.category_key
WHERE c.department = 'Technology'
GROUP BY c.category_name;
```

**Example 2 — dbt snowflake dimension:**
```sql
-- models/marts/dim_product.sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['p.product_id']) }} AS product_key,
    p.product_id,
    p.product_name,
    sc.subcategory_key,  -- FK to dim_subcategory
    p.brand,
    p.unit_cost
FROM {{ ref('stg_products') }} p
JOIN {{ ref('dim_subcategory') }} sc
  ON p.subcategory_id = sc.subcategory_id
```

---

### ⚖️ Comparison Table

| Aspect | Star Schema | Snowflake Schema |
|---|---|---|
| **Dimension structure** | Flat (all attrs in one table) | Hierarchical (sub-dims per level) |
| **Number of joins** | 2–4 | 4–8 |
| **Storage** | More redundancy | Less redundancy |
| **Hierarchy updates** | Update many rows | Update one row |
| **BI tool compatibility** | Excellent | Good (extra join path config) |
| **Query complexity** | Simple | Moderate |
| **Best for** | Standard analytics, BI-heavy | Deep product/geo hierarchies |

**How to choose:** Star schema for standard BI-facing data marts.
Snowflake schema when dimensions have hierarchies >3 levels deep,
hierarchical attributes change frequently, or dimension tables
exceed 10 million rows. In practice, choose based on team
preference — modern DWH platforms make the performance difference
negligible.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Snowflake schema (data pattern) is related to Snowflake (the cloud DWH) | Purely coincidental naming — the snowflake schema pattern predates the company by 20+ years |
| Snowflake schema always performs worse than star | On modern MPP DWH systems (BigQuery, Snowflake, Redshift), well-structured snowflake schemas perform nearly identically to star schemas |
| More normalisation = always better | For OLAP, normalisation increases join count without proportional query correctness benefit — star schema is often the correct choice |
| Snowflake eliminates all redundancy | Snowflake only normalises dimension hierarchies. Fact tables still contain surrogate keys that duplicate dimension identity |
| You can easily convert a star to a snowflake | Converting requires migrating ETL processes, BI tool semantic layers, and all queries. It's a significant refactor, not a simple DBA change |

---

### 🚨 Failure Modes & Diagnosis

**Over-Snowflaking (Too Many Sub-Dimensions)**

**Symptom:**
BI analysts complain that building any report requires 12-table
joins. A simple "revenue by product brand" query takes 8 minutes
to plan in the BI tool.

**Root Cause:**
The data model is over-normalised — `dim_product` → `dim_brand`
→ `dim_brand_parent` → `dim_brand_country` → `dim_country` →
`dim_region`. Five extra joins for rarely-changed hierarchy that
could live in a flat `dim_product`.

**Diagnostic Command / Tool:**
```sql
-- Count joins required for a typical analytics query
EXPLAIN
SELECT c.region, SUM(f.revenue)
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_brand b ON p.brand_key = b.brand_key
JOIN dim_brand_parent bp ON b.parent_key = bp.parent_key
JOIN dim_country c ON bp.country_key = c.country_key
JOIN dim_region r ON c.region_key = r.region_key
GROUP BY r.region_name;
-- If > 4 extra dimension joins: consider flattening
```

**Fix:**
Flatten rarely-changed hierarchy levels into the primary
dimension table. Keep sub-dimensions only for large (>5M rows)
or frequently-updated hierarchies.

**Prevention:**
Apply a "3-join rule": if a common analytics query requires
more than 4 total joins (including fact), flatten the schema.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Star Schema` — snowflake schema is an extension of star;
  must understand star first
- `Data Modeling` — normalisation principles that drive the
  snowflake structure
- `Database Fundamentals` — referential integrity, FK
  constraints, join mechanics

**Builds On This (learn these next):**
- `Dimensional Modeling` — the full Kimball methodology
  that includes both star and snowflake as variants
- `SCD (Slowly Changing Dimension)` — dimension change
  management applies to both star and snowflake

**Alternatives / Comparisons:**
- `Star Schema` — denormalised alternative for simpler queries
- `Data Vault` — entirely different approach for enterprise
  EDW with strict auditability requirements
- `One Big Table` — extreme denormalisation for maximum
  query simplicity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Normalised star schema where dimension    │
│              │ tables reference sub-dimension tables     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Star schema redundancy in large dimension  │
│ SOLVES       │ hierarchies causes update anomalies       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Snowflake trades storage/query simplicity │
│              │ for update integrity in hierarchies       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Deep hierarchies (>3 levels) with frequent│
│              │ hierarchy attribute changes               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple analytics, BI-heavy workflows, or  │
│              │ when query simplicity is paramount        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Storage savings + update integrity vs     │
│              │ extra joins and BI complexity             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Snowflake is a star schema that          │
│              │  went to normalisation school."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Vault → Dimensional Modeling →       │
│              │ SCD (Slowly Changing Dimension)           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An enterprise data warehouse uses a snowflake schema
with 6 sub-dimension levels for the product hierarchy.
The most frequent query (`SELECT SUM(revenue) GROUP BY division`)
requires 7 joins. A new BI analyst reports that the same data is
achievable with a 2-join star schema if `division` is denormalised
into `dim_product`. What is the concrete cost/benefit analysis
comparing the snowflake schema vs denormalising `division` into
`dim_product`? What would cause you to prefer one over the other?

**Q2.** Snowflake (the company) and Databricks both internally
recommend star schemas for most workloads on their platforms,
even though the database platforms were named and designed for
schema flexibility. Given that both platforms use MPP columnar
execution, explain mechanistically why the extra joins in a
snowflake schema (vs star) should theoretically be negligible
on these platforms, but practical BI tool performance still
often favours star. What is the actual bottleneck in the BI
tool layer that causes the difference?

