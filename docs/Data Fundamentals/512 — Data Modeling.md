---
layout: default
title: "Data Modeling"
parent: "Data Fundamentals"
nav_order: 512
permalink: /data-fundamentals/data-modeling/
number: "0512"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Database Fundamentals, Data Types, Structured vs Unstructured Data, OLTP vs OLAP
used_by: Star Schema, Snowflake Schema, Data Vault, Dimensional Modeling, Data Warehouse
related: Star Schema, Snowflake Schema, Dimensional Modeling, Entity-Relationship, Database Fundamentals
tags:
  - dataengineering
  - intermediate
  - database
  - mental-model
  - architecture
---

# 512 — Data Modeling

⚡ TL;DR — Data modeling is the process of defining how data is structured, related, and stored to best serve the queries and use cases of a system.

| #512 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Database Fundamentals, Data Types, Structured vs Unstructured Data, OLTP vs OLAP | |
| **Used by:** | Star Schema, Snowflake Schema, Data Vault, Dimensional Modeling, Data Warehouse | |
| **Related:** | Star Schema, Snowflake Schema, Dimensional Modeling, Entity-Relationship, Database Fundamentals | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer receives a requirement: "Track customer orders."
Without a data model, they create one massive `orders` table
with 60 columns: customer name, address, product name, product
category, price, discount, shipping address, billing address...
all duplicated in every row. After 1 million orders: changing
a customer's address requires updating 1 million rows. A customer
exists in the system only if they have an order. Joining becomes
unclear — "is the customer name in orders the same as in accounts?"

**THE BREAKING POINT:**
Without data modeling, data systems accumulate anomalies:
update anomaly (changing one fact requires updating many rows),
insertion anomaly (can't store a product until someone orders it),
deletion anomaly (deleting the last order for a customer deletes
the customer). These anomalies compound over years into a system
where nobody is sure what the data means or whether it's correct.

**THE INVENTION MOMENT:**
This is exactly why data modeling was formalised (E.F. Codd,
1970). Data modeling explicitly asks: what are the entities?
what are their attributes? how are they related? For operational
systems (OLTP), normalisation eliminates redundancy and anomalies.
For analytical systems (OLAP), deliberate denormalisation enables
fast aggregations. The model is the blueprint — without it,
the data structure drifts from reality.

---

### 📘 Textbook Definition

**Data modeling** is the process of creating a formal
representation of data structures, their relationships, and
constraints to meet the information requirements of a system.
Data models exist at three levels:
**Conceptual** — entity-level (what are the business concepts?
Customer buys Product);
**Logical** — attribute-level (Customer: id, name, email;
Product: id, SKU, category, price), with relationships and
cardinalities defined;
**Physical** — implementation-level (SQL table definitions,
indexes, data types, partitioning). For operational systems
(OLTP), a **normalised** model (1NF, 2NF, 3NF) eliminates
redundancy and enforces consistency. For analytical systems
(OLAP/DWH), **dimensional models** (star schema, snowflake)
deliberately denormalise for query performance. **Data Vault**
provides a historised, source-agnostic intermediate layer for
large enterprise data warehouses.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data modeling is designing the shape of your data before you
store it — so it means what you intend and queries work fast.

**One analogy:**

> Data modeling is to a database as architecture drawings are
> to a building. You don't pour concrete first and ask where
> the doors go later. You draw the blueprint — which rooms
> exist, how they connect, what goes in each room. The blueprint
> is the data model; the building is the database.

**One insight:**
Every data model is a bet on which queries will be common.
Normalised models bet on write-heavy OLTP: fast updates with
no redundancy. Star schemas bet on read-heavy OLAP: fast GROUP BY
and aggregations. The model that wins in one context loses in
the other — choosing the model is choosing the performance profile.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every fact should be stored once (normalisation) to prevent
   update anomalies.
2. Every entity should be stored separately from the events
   that involve it.
3. Analytical queries that aggregate across entities work
   faster when related data is pre-joined (denormalisation).

**TYPES OF DATA MODELS:**

*Third Normal Form (3NF) — OLTP standard:*
Each table stores facts about ONE entity type. No transitive
dependencies (column A → column B → column C means B and C
should be in separate tables). Eliminates: update anomalies,
insertion anomalies, deletion anomalies.

*Star Schema — analytical standard:*
One central fact table (orders, sales, events) + multiple
dimension tables (customer, product, date, geography). The fact
table contains only foreign keys + numeric measures (amount,
quantity). Dimensions contain descriptive attributes (name,
category, region). Query pattern: JOIN fact to 2–3 dimensions,
GROUP BY dimension attributes, SUM/AVG measures. One query,
few joins. Optimised for analytics.

*Snowflake Schema — normalised star:*
Dimension tables further normalised into sub-dimensions.
`Product → ProductCategory → ProductLine`. Reduces storage
redundancy vs star. Requires more joins per query. Trade-off:
storage vs query complexity.

*Data Vault — enterprise historised:*
Hub tables (business keys), Link tables (relationships), Satellite
tables (attributes + timestamps). Purpose: capture raw historical
state from multiple source systems without losing any data.
Designed for EDW (Enterprise Data Warehouses) where source systems
change over time and every change must be traceable.

**THE TRADE-OFFS:**
**3NF:** Clean, no redundancy, enforces consistency. Slow for
analytics (many joins). Right for OLTP.
**Star Schema:** Fast analytics. Data duplication in dimensions.
Dimensions may go stale. Right for OLAP.
**Data Vault:** Complete audit history, handles source system
changes gracefully. Complex to query, slower to load. Right for
large enterprises with strict regulatory auditability.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce company stores sales data. Analyst query:
"Monthly revenue by product category and region last year."

**WITH 3NF MODEL:**
Tables: `orders`, `order_items`, `products`, `product_categories`,
`customers`, `customer_addresses`.
Query requires: JOIN orders → order_items → products →
product_categories → customers → customer_addresses (6 tables).
SQL: 6-way join on 10 billion order_items rows. Takes 4 minutes.

**WITH STAR SCHEMA:**
Fact table: `fact_sales` (date_key, product_key, customer_key,
region_key, revenue, quantity). Dimension tables: `dim_date`,
`dim_product` (contains category), `dim_customer` (contains
region). Query: JOIN fact_sales → dim_product → dim_date.
3 tables. All dimension tables in memory (small). Fact table
is columnar (Parquet). Query: 8 seconds.

**THE INSIGHT:**
The 3NF model is correct (no redundancy, consistent). The star
schema is analytical (denormalised, fast to query). The same
underlying business data, modeled differently, produces a 30×
difference in analytical query time. Data modeling is a decision
about which operations to optimise — not about correctness alone.

---

### 🧠 Mental Model / Analogy

> Data modeling is like designing a filing system. A 3NF model
> is like a meticulously organised office: each document type in
> its own folder, nothing duplicated. Finding any document is
> precise. But answering "how much did we spend on supplies per
> department each quarter?" requires pulling from 6 folders and
> cross-referencing. A star schema is like a pre-built dashboard:
> the most common questions are answered by looking at one central
> report (fact table) that already references the department and
> category booklets (dimensions). Less rigorous, but the answers
> come instantly.

- "Meticulously organised office" → 3NF (normalised OLTP model)
- "Pre-built dashboard" → star schema (dimensional model)
- "Pulling from 6 folders" → 6-way SQL join
- "Department booklet" → dimension table
- "Central report" → fact table
- "Filing system design" → data modeling process

**Where this analogy breaks down:** Real data modeling involves
more than two archetypes. Data Vault, anchor modeling, and
hybrid models exist for specific enterprise needs. No single
model serves all purposes — the correct model depends entirely
on the workload.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Data modeling is deciding how to organise information before
storing it. Like designing the layout of rooms in a house before
building it — you think about what you need to store, how things
connect, and which questions you'll ask most often.

**Level 2 — How to use it (junior developer):**
Start with an Entity-Relationship Diagram (ERD): identify the
business entities (Customer, Product, Order), their attributes
(Customer: id, name, email), and their relationships (Customer
PLACES Order, Order CONTAINS Product). For OLTP: normalise to
3NF. For analytics/reporting: design a star schema with a central
fact table and dimension tables. Use tools: dbdiagram.io,
Lucidchart, dbt models for data warehouse modeling.

**Level 3 — How it works (mid-level engineer):**
Normalisation forms:
- 1NF: atomic values (no arrays in columns), each row unique.
- 2NF: 1NF + no partial dependencies (every non-key column
  depends on the ENTIRE primary key, not part of it).
- 3NF: 2NF + no transitive dependencies (no column A → B → C
  where B is not a key).
- BCNF: stricter 3NF for edge cases.

Dimensional modeling (Kimball methodology):
1. Identify business process (what happened? orders placed).
2. Declare grain (one row = one order line item).
3. Identify dimensions (who? customer, what? product, when? date).
4. Identify facts (measures: revenue, quantity).
5. Assign surrogate keys to dimensions (integer ID, not business key).
6. Handle slowly changing dimensions (SCD Type 1: overwrite;
   Type 2: add new row with effective dates; Type 6: hybrid).

**Level 4 — Why it was designed this way (senior/staff):**
Normalisation theory (Codd 1970) was a direct response to the
hierarchical and network database models (IMS, CODASYL) where
data was physically embedded in parent-child chains. Those models
forced traversal from parent to child — changing a relationship
required physical restructuring. The relational model separated
data from its access path: any join between relations was legal;
the query planner chose the path. Normalisation is the logical
consequence: if any two relations can be joined by the planner,
you should store atomic facts once in the relation where they
belong. Dimensional modeling (Kimball, 1996) reversed this
philosophy for analytics: the cost of joins in OLAP on pre-column-
store hardware was prohibitive. Denormalisation pre-computes
the joins. The 2020s addition: columnar stores (Parquet + Spark)
reduced the join cost so dramatically that the normalised vs
denormalised choice matters less for performance — but dimensional
models persist because they are a lingua franca between data
engineers and business analysts, providing predictable query
patterns even when the execution is fast either way.

---

### ⚙️ How It Works (Mechanism)

**3NF normalisation example:**
```sql
-- UNNORMALISED: data duplication
CREATE TABLE orders_raw (
  order_id       INT,
  customer_name  VARCHAR(100),  -- duplicated per order
  customer_email VARCHAR(100),  -- duplicated per order
  product_name   VARCHAR(100),  -- duplicated per order_item
  product_category VARCHAR(50), -- duplicates product data
  quantity       INT,
  price          DECIMAL(10,2)
);
-- Problem: change customer email → update every order row

-- 3NF NORMALISED:
CREATE TABLE customers (
  customer_id INT PRIMARY KEY,
  name        VARCHAR(100),
  email       VARCHAR(100)  -- stored ONCE
);
CREATE TABLE products (
  product_id INT PRIMARY KEY,
  name       VARCHAR(100),
  category   VARCHAR(50)   -- stored ONCE per product
);
CREATE TABLE orders (
  order_id    INT PRIMARY KEY,
  customer_id INT REFERENCES customers(customer_id),
  order_date  DATE
);
CREATE TABLE order_items (
  order_item_id INT PRIMARY KEY,
  order_id      INT REFERENCES orders(order_id),
  product_id    INT REFERENCES products(product_id),
  quantity      INT,
  price         DECIMAL(10,2)
);
-- Change customer email: update ONE row in customers table
```

**Star schema for the same data:**
```sql
-- STAR SCHEMA for analytics
CREATE TABLE fact_sales (
  sale_id      BIGINT PRIMARY KEY,
  date_key     INT    REFERENCES dim_date(date_key),
  product_key  INT    REFERENCES dim_product(product_key),
  customer_key INT    REFERENCES dim_customer(customer_key),
  quantity     INT,
  revenue      DECIMAL(10,2)
);
-- Dimensions contain denormalised descriptive data:
CREATE TABLE dim_product (
  product_key      INT PRIMARY KEY,
  product_id       INT,          -- source business key
  product_name     VARCHAR(100),
  category         VARCHAR(50),  -- denormalised from categories
  subcategory      VARCHAR(50),  -- denormalised
  brand            VARCHAR(50)
);
-- Query: "Revenue by category, Q1 2024"
-- → 2-table join: fact_sales + dim_product
-- → no need to traverse 4 3NF tables
```

---

### 💻 Code Example

**Example 1 — dbt dimensional model:**
```sql
-- dbt model: marts/finance/fct_orders.sql
WITH orders AS (
  SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
  SELECT * FROM {{ ref('dim_customers') }}
),
products AS (
  SELECT * FROM {{ ref('dim_products') }}
)
SELECT
  o.order_id,
  o.ordered_at,
  c.customer_key,
  c.loyalty_tier,
  p.product_key,
  p.category,
  o.quantity,
  o.unit_price,
  o.quantity * o.unit_price AS revenue
FROM orders o
JOIN customers c USING (customer_id)
JOIN products  p USING (product_id)
```

**Example 2 — Verify third normal form:**
```python
# Detect transitive dependencies (simplified)
# Functional dependency: order_id → customer_id → customer_name
# customer_name depends on customer_id, not on order_id directly
# → violation of 3NF → separate customers table

def check_3nf(df, primary_key, column_to_check):
    """Check if column_to_check is functionally dependent
       on primary_key directly (OK) or transitively (violation)"""
    grouped = df.groupby(primary_key)[column_to_check].nunique()
    violations = grouped[grouped > 1]
    if len(violations) > 0:
        print(f"VIOLATION: {column_to_check} has multiple values"
              f" for same {primary_key}")
    else:
        print(f"OK: {column_to_check} uniquely determined by {primary_key}")
```

---

### ⚖️ Comparison Table

| Model | Purpose | Normalisation | Join Complexity | Best For |
|---|---|---|---|---|
| **3NF** | OLTP, write-heavy | High | Many joins | Transactional apps |
| **Star Schema** | OLAP, read-heavy | Low | 2–4 joins | Analytics, DWH |
| **Snowflake Schema** | OLAP with normalised dims | Medium | More joins than star | Storage-constrained DWH |
| **Data Vault** | Enterprise EDW + historisation | Hub/Link/Sat | Complex | Large enterprise auditability |
| **One Big Table (OBT)** | Simple OLAP | None | No joins | Small-scale analytics |

**How to choose:** OLTP applications → 3NF. Analytics/BI →
Star schema (Kimball). Enterprise EDW with multiple source systems
and strict audit history → Data Vault. Simple reporting on a single
source system → OBT or star.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Data modeling is only for databases | Data models apply to APIs (OpenAPI schema), event streams (Avro schema), files (Parquet schema), and any structured data — not just SQL databases |
| More normalisation is always better | 3NF is optimal for OLTP, not OLAP. Over-normalised analytical schemas require 10+ joins for simple queries — the model must match the workload |
| A star schema is always denormalised | The fact table in a star schema is actually very normalised (foreign keys only). Only dimension tables are denormalised |
| Data Vault is the most advanced model | Data Vault is most complex, not most performant. It solves enterprise historisation problems; for simple analytics, star schema outperforms it dramatically |
| You only model data once | Data models evolve continuously. Schema evolution strategies (schema registry, SQL migrations) are the operational management of a living data model |

---

### 🚨 Failure Modes & Diagnosis

**Fan-Out Join Explosion (Wrong Grain)**

**Symptom:**
A `fact_sales` query returns 50× more rows than expected.
Revenue totals are inflated by 50×.

**Root Cause:**
The grain was defined incorrectly. `fact_sales` contains one row
per order, but `dim_promotions` has multiple promotions per order
(many-to-one violating the grain). The join explodes: order
with 3 promotions produces 3 fact rows.

**Diagnostic Command / Tool:**
```sql
-- Check for duplicate order_ids in the fact
SELECT order_id, COUNT(*) cnt
FROM fact_sales
GROUP BY order_id
HAVING cnt > 1;
-- Any result means grain violation
```

**Fix:**
Denormalise promotions into a comma-list or bridge table.
Or create a fact row per promotion with promotion allocation.

**Prevention:**
Document grain explicitly: "one row = one order line item."
Validate: `COUNT(*) = COUNT(DISTINCT grain_key)` after ETL.

---

**Slowly Changing Dimension Not Handled (SCD)**

**Symptom:**
A loyalty programme report shows incorrect current loyalty tier
for historical orders. All historical orders show the customer's
current loyalty tier, not the tier at time of order.

**Root Cause:**
Dimension table uses SCD Type 1 (overwrite). When a customer
moves from Silver to Gold tier, the dimension row is updated:
`loyalty_tier = 'Gold'`. All historical order lookups via
`customer_key` now return Gold, even for orders placed when
the customer was Silver.

**Diagnostic Command / Tool:**
```sql
-- Check if a dimension table has no historical records
SELECT customer_id, COUNT(*) cnt
FROM dim_customer
GROUP BY customer_id
HAVING cnt > 1;
-- Result: 0 rows = SCD Type 1 (no history)
-- Non-zero = SCD Type 2 (has history)
```

**Fix:**
Migrate to SCD Type 2: add `effective_from`, `effective_to`,
`is_current` columns. On each change, close the old row
(`effective_to = today, is_current = 0`) and insert a new row
(`effective_from = today, is_current = 1`).

**Prevention:**
Identify which dimension attributes change over time BEFORE
designing the model. Classify each attribute as Type 1/2/3
and implement accordingly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Database Fundamentals` — data modeling is built on
  relational algebra, tables, keys, and joins
- `OLTP vs OLAP` — the workload type drives the choice
  between normalised and dimensional models
- `Data Types` — every attribute in a data model has a
  defined type that determines storage and operations

**Builds On This (learn these next):**
- `Star Schema` — the primary dimensional modeling pattern
  for analytics and data warehouses
- `Snowflake Schema` — the normalised variant of the star
  schema for storage-constrained environments
- `Data Vault` — the enterprise-grade historised modeling
  approach for large EDW environments

**Alternatives / Comparisons:**
- `Dimensional Modeling` — the analytics-oriented data
  modeling paradigm (Kimball) using facts and dimensions
- `Entity-Relationship Model` — the conceptual modeling
  tool used to design normalised relational databases
- `Document Model` — MongoDB/Couchbase alternative to
  relational data modeling for semi-structured data

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The discipline of designing data structure │
│              │ before storage to match query workload    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Unmodelled data accumulates anomalies     │
│ SOLVES       │ that make it incorrect and unqueryable    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every model is a bet on which queries are │
│              │ common — 3NF bets on writes, star bets on │
│              │ analytics reads                           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Before any new database, data warehouse,  │
│              │ or stream schema is created               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Rapid prototyping with schema-on-read;    │
│              │ but plan to model before productionising  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Normalisation (write consistency) vs      │
│              │ denormalisation (read performance)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A data model is a bet. Make it consciously│
│              │  or the data will decide for you."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Star Schema → Snowflake Schema →          │
│              │ Dimensional Modeling                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce company's data model was designed 5 years
ago as a 3NF OLTP model. Today the business needs a real-time
analytics dashboard that queries across orders, products,
customers, and promotions. The 3NF model requires 8-way joins
on 20 billion rows. The team proposes "just adding more indexes."
Explain why indexes cannot solve the fundamental problem, what
the correct architectural solution is, and describe the data
pipeline design that keeps both the 3NF operational database
and the analytical star schema in sync.

**Q2.** A data vault model was chosen for a banking enterprise's
data warehouse 10 years ago. The model has 400 Hub, 600 Link,
and 1,200 Satellite tables. Business analysts take 3 weeks to
write a new report because the query pattern requires joining
23 tables. The team is debating whether to migrate to a star
schema. Explain the specific data vault properties that protect
the bank's regulatory auditability requirements, what would be
lost in a migration to a pure star schema, and design a hybrid
approach that preserves both goals.

