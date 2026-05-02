---
layout: default
title: "Data Modeling"
parent: "Data Fundamentals"
nav_order: 512
permalink: /data-fundamentals/data-modeling/
number: "512"
category: Data Fundamentals
difficulty: ★★☆
depends_on: Data Warehouse, OLTP vs OLAP, Database Fundamentals
used_by: Star Schema, Snowflake Schema, Data Vault, Dimensional Modeling, Fact Table vs Dimension Table
tags:
  - data
  - warehouse
  - architecture
  - intermediate
---

# 512 — Data Modeling

`#data` `#warehouse` `#architecture` `#intermediate`

⚡ TL;DR — Data modeling is the process of defining how data is structured, related, and stored to optimise for a specific workload — OLTP models normalise for write efficiency; OLAP models denormalise for query performance.

| #512 | Category: Data Fundamentals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Data Warehouse, OLTP vs OLAP, Database Fundamentals | |
| **Used by:** | Star Schema, Snowflake Schema, Data Vault, Dimensional Modeling, Fact Table vs Dimension Table | |

---

### 📘 Textbook Definition

**Data modeling** is the discipline of creating an abstract representation of how data is organised, stored, and related within a system. Three levels: **Conceptual model** (business entities and relationships, technology-agnostic), **Logical model** (entities, attributes, relationships with data types — no physical storage), and **Physical model** (actual table/column definitions, indexes, partitions for a specific database). Key paradigms: **3NF/normalised** (eliminates redundancy, optimised for OLTP write throughput), **Dimensional modeling** (denormalised star/snowflake schemas, optimised for OLAP query performance), and **Data Vault** (hub-link-satellite pattern for auditability and historisation).

### 🟢 Simple Definition (Easy)

Data modeling is deciding how to organise your data tables — which fields go where, how tables relate to each other, and what structure makes queries fast.

### 🔵 Simple Definition (Elaborated)

Every database system requires decisions: should orders and customers be in one table or separate, linked by a foreign key? Should you store the city name in every order row (redundant but fast to query) or store it once in a customers table and join when needed (clean but slower)? These structural decisions — data modeling — determine query performance, storage cost, data integrity, and ease of analysis. OLTP systems (order processing, banking) normalise to avoid redundancy and ensure write consistency. OLAP systems (analytics, reporting) deliberately denormalise to avoid expensive joins.

### 🔩 First Principles Explanation

**Three normal forms (OLTP baseline):**

```
Unnormalised (bad):
  Orders: [order_id, customer_name, customer_email, product_name,
           product_price, qty, order_date, city, country]
  Problem: customer_name repeated in every order → update anomaly

1NF: each cell = atomic value; no repeating groups
2NF: every non-key attribute depends on WHOLE primary key
3NF: no non-key attribute depends on another non-key attribute

Normalised (3NF):
  Customers: [customer_id, name, email, city_id]
  Cities:    [city_id, city, country]
  Products:  [product_id, name, price]
  Orders:    [order_id, customer_id, order_date]
  OrderItems:[order_id, product_id, qty]
  
Benefits: no redundancy, no update anomalies
Drawback: 5-way JOIN to reconstruct an order → slow analytics
```

**Dimensional modeling (OLAP/data warehouse):**

```
Denormalised for queries:
  Fact table (transactions): fact_sales
  [sale_id, date_id, customer_id, product_id, quantity, amount]
  → rows = measurable events (facts)
  → FKs to dimension tables

  Dimension tables: dim_customer, dim_product, dim_date
  [customer_id, name, email, city, country]  ← redundancy allowed
  → full context pre-joined for fast query

Query: "Total sales by country this year"
  SELECT d.country, SUM(f.amount)
  FROM fact_sales f
  JOIN dim_date d_date ON f.date_id = d_date.date_id
  JOIN dim_customer c ON f.customer_id = c.customer_id
  WHERE d_date.year = 2026
  GROUP BY c.country;
  ← Only 2 joins; no city→country lookup; fast column scan
```

**Conceptual → Logical → Physical progression:**

```
Conceptual:    Customer places Order which contains Products
                  (entity boxes and relationship lines)

Logical:       Customer(id, name, email)
               Order(id, date, customer_id FK)
               Product(id, name, price)
               OrderLine(order_id FK, product_id FK, qty)

Physical:      CREATE TABLE customers (
                 customer_id BIGINT NOT NULL,
                 name VARCHAR(100),
                 email VARCHAR(255),
                 PRIMARY KEY (customer_id)
               ) PARTITION BY HASH(customer_id);
               CREATE INDEX idx_cust_email ON customers(email);
```

**Modeling choices by use case:**

```
Use Case              Model          Key technique
──────────────────────────────────────────────────────
OLTP (transactions)   3NF            Normalisation, FK integrity
OLAP (BI dashboards)  Star schema    Denormalised dims, columnar storage
History/audit         Data Vault     Hub/satellite patterns, immutable
Semi-structured data  Document model Nested JSON/Avro, schema-on-read
Graph relationships   Graph model    Nodes and edges, adjacency lists
Time series           Time-series    Sorted by time, rollup aggregates
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT intentional data modeling:
- "God table" anti-pattern: 200 columns in one table, most NULL.
- Analytics queries fail: 12-table joins on normalised OLAP tables take minutes instead of seconds.
- Data quality issues: customer city stored in three different tables with three different spellings.
- Schema drift: same concept called "user", "customer", "account" in different tables.

WITH good data modeling:
→ BI queries on star schema run in seconds (pre-joined, columnar access).
→ Update anomalies eliminated (3NF ensures one source of truth).
→ Reporting teams can self-serve without understanding complex joins.

### 🧠 Mental Model / Analogy

> Data modeling is like designing a supermarket layout. Normalised design is the warehouse: every product in one place, no duplicates — efficient for stocking (writes) but shoppers must walk to multiple sections for a full meal. Dimensional modeling is the customer-facing layout: pre-arranged "meal kits" section (star schema) where everything needed is co-located — efficient for shopping (queries) but requires duplicating items. A data vault is like a meticulous archive with full history — who received what shelf item and when.

### ⚙️ How It Works (Mechanism)

**Star schema example:**

```sql
-- Fact table: one row per transaction
CREATE TABLE fact_orders (
    order_id      BIGINT,
    date_id       INT,         -- FK to dim_date
    customer_id   INT,         -- FK to dim_customer
    product_id    INT,         -- FK to dim_product
    quantity      INT,
    revenue       DECIMAL(10,2)
) PARTITION BY (date_id);

-- Dimension tables: descriptive attributes
CREATE TABLE dim_date (
    date_id   INT PRIMARY KEY,
    full_date DATE,
    year      INT, quarter INT, month INT, week INT, day INT,
    is_weekend BOOLEAN
);

CREATE TABLE dim_customer (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100), email VARCHAR(255),
    city VARCHAR(100), country VARCHAR(50), segment VARCHAR(50)
);
```

### 🔄 How It Connects (Mini-Map)

```
Business requirements (what questions to answer)
        ↓ shapes
Data Modeling ← you are here
  (conceptual → logical → physical)
        ↓ implementations
Star Schema (OLAP, simple joins)
Snowflake Schema (OLAP, normalised dims)
Data Vault (auditability, history)
3NF (OLTP, write efficiency)
        ↓ stored in
Data Warehouse | Data Lake | OLTP Database
```

### 💻 Code Example

```sql
-- Build a star schema for e-commerce analytics

-- Dimension: products with SCD Type 2 history
CREATE TABLE dim_product (
    product_sk    BIGINT PRIMARY KEY,  -- surrogate key
    product_id    INT,                  -- business key
    product_name  VARCHAR(200),
    category      VARCHAR(100),
    price         DECIMAL(10,2),
    valid_from    DATE,
    valid_to      DATE,                -- NULL = current version
    is_current    BOOLEAN
);

-- Fact: transactional grain (one row per order line)
CREATE TABLE fact_sales (
    sale_sk       BIGINT PRIMARY KEY,
    order_id      BIGINT,
    date_sk       INT REFERENCES dim_date(date_sk),
    customer_sk   INT REFERENCES dim_customer(customer_sk),
    product_sk    BIGINT REFERENCES dim_product(product_sk),
    quantity      INT,
    unit_price    DECIMAL(10,2),
    revenue       DECIMAL(10,2),
    -- Store pre-calculated metrics to avoid repeated computation
    margin        DECIMAL(10,2)
);
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Normalisation is always better | Normalisation optimises write efficiency and eliminates redundancy. For read-heavy analytics, deliberate denormalisation (star schema) dramatically improves query performance. |
| Star schema is outdated for modern data warehouses | Most modern cloud warehouses (Snowflake, BigQuery, Redshift) are optimised for star schema patterns. Columnar storage + MPP makes star schema the standard for OLAP. |
| Data modeling is only for relational databases | Data modeling applies to NoSQL (document structure), data lakes (Parquet schema), event streams (Avro schema), and graph databases. The principles transcend the technology. |

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ OLTP (writes)  → Normalised (3NF) → eliminate redundancy │
│ OLAP (reads)   → Star schema → pre-joined dimensions     │
│ Audit/history  → Data Vault → immutable, time-stamped    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Data modeling: structure your data for   │
│              │ the questions you need to answer."        │
└──────────────────────────────────────────────────────────┘
```

