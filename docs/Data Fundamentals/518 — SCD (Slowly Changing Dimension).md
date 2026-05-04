---
layout: default
title: "SCD (Slowly Changing Dimension)"
parent: "Data Fundamentals"
nav_order: 518
permalink: /data-fundamentals/scd-slowly-changing-dimension/
number: "0518"
category: Data Fundamentals
difficulty: ★★★
depends_on: Dimensional Modeling, Fact Table vs Dimension Table, Star Schema, Data Modeling
used_by: Data Warehouse, BI Tools, Data Lakehouse
related: Fact Table vs Dimension Table, Star Schema, Dimensional Modeling, Data Vault, Data Warehouse
tags:
  - dataengineering
  - advanced
  - database
  - architecture
  - tradeoff
---

# 518 — SCD (Slowly Changing Dimension)

⚡ TL;DR — SCD is the set of strategies for handling dimension attribute changes over time — Type 1 overwrites history, Type 2 preserves full history, Type 6 combines both.

| #518 | Category: Data Fundamentals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Dimensional Modeling, Fact Table vs Dimension Table, Star Schema, Data Modeling | |
| **Used by:** | Data Warehouse, BI Tools, Data Lakehouse | |
| **Related:** | Fact Table vs Dimension Table, Star Schema, Dimensional Modeling, Data Vault, Data Warehouse | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A customer upgrades from Bronze to Gold loyalty tier in March.
The `dim_customer` table is simply updated: `UPDATE dim_customer
SET loyalty_tier = 'Gold' WHERE customer_id = 'C001'`.

Now every report asks: "What was the revenue from Bronze customers
last year?" — and all of C001's 2023 orders now look like Gold
orders because the dimension was overwritten. The historical
record is destroyed. A loyalty programme cannot be evaluated
fairly. The data doesn't match what actually happened.

**THE BREAKING POINT:**
Dimensions are not static — customers change segments, products
change categories, stores change regions. Yet fact tables record
events that happened at a specific point in time with the entity
as it existed THEN. If you overwrite the dimension, you break
the historical accuracy of every fact that references the old
entity state. Auditors, regulators, and marketing analysts all
need to know what the entity looked like at the time of each event.

**THE INVENTION MOMENT:**
This is exactly why Slowly Changing Dimension strategies were
formalised by Ralph Kimball. SCD provides a controlled vocabulary
of techniques to handle dimension change — each with explicit
trade-offs between storage cost. historical accuracy, and
query complexity.

---

### 📘 Textbook Definition

A **Slowly Changing Dimension (SCD)** is a dimension whose
attribute values change gradually over time, requiring a defined
strategy to preserve accuracy of historical analytics. The most
widely used SCD types are:
**Type 1** — overwrite the changed attribute; no history kept;
always reflects current state.
**Type 2** — add a new row for each change with `effective_from`,
`effective_to` dates and `is_current` flag; full history preserved.
**Type 3** — add a `previous_value` column to store the one prior
value; only one prior state kept.
**Type 4** — separate current attributes into a mini-dimension
or outrigger table.
**Type 6** — hybrid of 1+2+3; current value in all rows + full
versioned history rows.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When a dimension attribute changes, you choose: overwrite it
(Type 1), add a new version row (Type 2), or keep one previous
value (Type 3).

**One analogy:**

> Imagine updating a patient's medical record when their
> diagnosis changes. Type 1: cross out the old diagnosis and
> write the new one — clean but old diagnosis lost. Type 2:
> keep the old entry with its date, write a new entry with today's
> date — complete history, larger file. Type 3: add a "previous
> diagnosis" field to each page — one step back only, compact.
> Type 6: each page shows both "current diagnosis" (always
> current) AND keeps the dated history (full audit trail).

**One insight:**
SCD Type 2 is the most powerful but most expensive. The surrogate
key is what makes Type 2 work: by having a unique integer key
for each VERSION of an entity (not just each entity), fact rows
can point to the HISTORICAL version of the dimension that was
current at the time of the event — preserving temporal accuracy
forever.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A fact row records an event that happened at a specific time
   with an entity as it existed at that time.
2. Dimension attributes can change after facts that reference
   them are loaded.
3. There is always a trade-off between storage cost and historical
   accuracy.

**SCD TYPE 1 — Overwrite:**
Simply update the changed attribute. Historical accuracy of
old facts: LOST (all historical facts now join to the new value).
Use when: history doesn't matter for the changed attribute
(e.g., a corrected typo in a product name).

**SCD TYPE 2 — Add new row (with versioning):**
On change: close the current row (`effective_to = today`,
`is_current = false`), insert a new row with the new attribute
value (`effective_from = today`, `is_current = true`).
The fact table's `product_key` (surrogate) points to the
specific version of the product that existed at transaction time.
Historical accuracy: FULLY PRESERVED.
Use when: attribute changes affect historical reporting
(customer segment, product category, manager of sales region).

Storage cost: dimension table grows by one row per change event.
Active customers × 3 changes/year × 10 years = 30 rows per customer.

**SCD TYPE 3 — Add column:**
Adds `previous_value` and `change_date` column. On change:
move current `loyalty_tier` to `prev_loyalty_tier`, update
`loyalty_tier` to new value.
Historical accuracy: ONE prior state only.
Use when: only one prior state matters (e.g., "was this customer
previously Gold?"). Compact but limited.

**SCD TYPE 6 — Hybrid (1+2+3):**
Each version row (like Type 2) ALSO carries the CURRENT attribute
value as a separate column. Old version rows have `loyalty_tier`
(historical at that time) AND `current_loyalty_tier` (today's value).
This allows: "Show me customers' revenue by what they were
THEN (`loyalty_tier`) AND by what they are NOW (`current_loyalty_tier`)"
in the same query without a self-join. Power at cost of complexity.

**THE TRADE-OFFS:**
**Type 1:** Simple ETL, no storage growth, no historical reporting.
**Type 2:** Full history, complex ETL, storage grows with changes.
**Type 3:** Minimal storage, one prior state, simple ETL.
**Type 6:** Best of both worlds analytically, most complex ETL.

---

### 🧪 Thought Experiment

**SETUP:**
Customer Alice starts as Bronze in Jan 2023. Upgrades to Silver
in Jun 2023. Upgrades to Gold in Mar 2024.
Fact table has 50 orders: 20 in Bronze period, 20 in Silver,
10 in Gold.

**WITH SCD TYPE 1:**
`dim_customer.loyalty_tier = 'Gold'` (current only).
Report: "Revenue by loyalty tier last year." ALL 50 orders
join to 'Gold'. Alice's Bronze and Silver history is gone.
Report: completely wrong — all 50 orders look like Gold orders.

**WITH SCD TYPE 2:**
`dim_customer`:
- Row 1: customer_key=100, loyalty_tier='Bronze', eff=Jan 2023,
  exp=Jun 2023, is_current=false
- Row 2: customer_key=101, loyalty_tier='Silver', eff=Jun 2023,
  exp=Mar 2024, is_current=false
- Row 3: customer_key=102, loyalty_tier='Gold', eff=Mar 2024,
  exp=NULL, is_current=true

Fact table:
- Jan-May 2023 orders: customer_key=100 (Bronze)
- Jun-Feb 2024 orders: customer_key=101 (Silver)
- Mar 2024+ orders: customer_key=102 (Gold)

Report: "Revenue by loyalty tier last year." Perfectly correct
— each order period joined to the right tier.

**THE INSIGHT:**
Type 2 works because the fact table's FK points to a dimension
VERSION, not a dimension ENTITY. The key isn't "who is Alice" —
it's "who was Alice at the time of this order." Without versioning,
this temporal precision is impossible.

---

### 🧠 Mental Model / Analogy

> SCD Type 2 is like a passport stamp system, not a replace-the-
> photo system. When a traveller changes their appearance (gets
> a new photo), instead of replacing the old photo in the passport,
> the passport office adds a new page: "From date X, this is the
> photo. From date Y, new photo." The visa entries (fact rows)
> reference the specific page that was current when the visa was
> issued. Full history. Zero data loss.

- "Passport page" → dimension row version (one per SCD change)
- "Visa entry" → fact table row (references specific passport page)
- "Adding a new page" → SCD Type 2 insert
- "Effective_from / effective_to" → page validity dates
- "is_current = true" → the photo on today's page
- "Replacing the photo" → SCD Type 1 (history lost)

**Where this analogy breaks down:** Real passports don't have
an `effective_to` — pages stay valid until the passport expires.
SCD Type 2 closes the `effective_to` when a new version is
created, making the history range queryable.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When information about a customer, product, or other entity
changes over time, SCD determines whether to keep the old
information or replace it. Type 1 replaces it (simple but loses
history). Type 2 keeps both the old and new versions (complex but
perfectly accurate for historical reports).

**Level 2 — How to use it (junior developer):**
Default to SCD Type 2 for any attribute that affects historical
analysis (customer tier, product category, sales region, territory
manager). Use SCD Type 1 for corrections of errors (wrong
postcode entered). When you detect a change in the ETL:
(a) UPDATE current dim row: set `is_current = FALSE`,
`effective_to = current_date - 1`.
(b) INSERT new dim row with new attribute, `is_current = TRUE`,
`effective_from = current_date`, `effective_to = NULL`.
Always ensure the fact table loads the CURRENT version's
surrogate key for new events.

**Level 3 — How it works (mid-level engineer):**
ETL implementation considerations:

*Change detection*: use Hash Diff (hash of all tracked columns)
to detect changes efficiently — one comparison per row.

*Surrogate key assignment*: use a sequence or identity column for
`dim_customer.customer_key`. Never reuse a surrogate key.

*Effective date precision*: for intraday changes, use TIMESTAMP
not DATE for `effective_from`/`effective_to`.

*Partial history*: if source system doesn't provide change history
(only current state), you can only capture changes from ETL start
date forward — pre-ETL history is unrecoverable.

*Late-arriving dimension changes*: if a dim change arrives after
fact data was already loaded for the transition period —
re-key those fact rows to the new surrogate. This requires a
"Dimension Repair" ETL step.

**Level 4 — Why it was designed this way (senior/staff):**
SCD Type 2's use of surrogate keys as version identifiers is
an elegant engineering solution to the temporal database problem.
SQL doesn't natively support bi-temporal queries (as of + valid
time + transaction time). SCD Type 2 encodes temporal validity
directly as rows and uses the relational model's natural join
mechanism to link facts to their historical dimension context.
The alternative — bi-temporal tables with `valid_from/to` and
`transaction_from/to` — is more theoretically correct but
requires complex query patterns. SCD Type 2 trades theoretical
purity for practical SQL simplicity: `is_current = TRUE` is
the most common pattern; a date-range join handles historical
lookups. SCD Type 6's "current fill" is a performance optimisation:
by redundantly storing the current value in every historical row,
it eliminates a self-join frequently required in Type 2 queries.
dbt's `dbt_utils.surrogate_key()` and `dbt-scd2` packages have
made SCD Type 2 implementation in dbt pipelines standard practice.

---

### ⚙️ How It Works (Mechanism)

**SCD Type 2 — Timeline of Alice's customer dimension:**
```
dim_customer table state over time:

Date: 2023-01-01 (Alice joins as Bronze):
│ cust_key │ cust_id │ tier   │ eff_from   │ eff_to     │ current │
│ 1001     │ C001    │ Bronze │ 2023-01-01 │ NULL       │ TRUE    │

Date: 2023-06-15 (Alice upgrades to Silver):
│ cust_key │ cust_id │ tier   │ eff_from   │ eff_to     │ current │
│ 1001     │ C001    │ Bronze │ 2023-01-01 │ 2023-06-14 │ FALSE   │ ← closed
│ 1002     │ C001    │ Silver │ 2023-06-15 │ NULL       │ TRUE    │ ← new

Date: 2024-03-01 (Alice upgrades to Gold):
│ cust_key │ cust_id │ tier   │ eff_from   │ eff_to     │ current │
│ 1001     │ C001    │ Bronze │ 2023-01-01 │ 2023-06-14 │ FALSE   │
│ 1002     │ C001    │ Silver │ 2023-06-15 │ 2024-02-28 │ FALSE   │ ← closed
│ 1003     │ C001    │ Gold   │ 2024-03-01 │ NULL       │ TRUE    │ ← new

fact_orders rows for Alice:
│ order_key │ cust_key │ order_date │ revenue │
│ 5001      │ 1001     │ 2023-02-05 │ $120    │ ← Bronze era
│ 5089      │ 1002     │ 2023-08-10 │ $200    │ ← Silver era
│ 5203      │ 1003     │ 2024-04-01 │ $450    │ ← Gold era
```

**SCD Type 2 SQL query (historical accuracy):**
```sql
-- Revenue by tier AT TIME OF PURCHASE (historical)
SELECT dc.tier, SUM(f.revenue) AS revenue
FROM fact_orders f
JOIN dim_customer dc ON f.cust_key = dc.cust_key
GROUP BY dc.tier;
-- Returns: Bronze=$120, Silver=$200, Gold=$450 ← CORRECT

-- Revenue by tier CURRENT (what tier customers are now)
SELECT dc.tier, SUM(f.revenue) AS revenue
FROM fact_orders f
JOIN dim_customer dc
  ON CAST(f.cust_key / 1 AS INT) = dc.cust_id_lookup
  AND dc.is_current = TRUE
GROUP BY dc.tier;
-- Needs a customer_id join through current dim
-- Returns: Gold=$770 for all 3 orders ← shows current tier
```

---

### 💻 Code Example

**Example 1 — dbt SCD Type 2 snapshot:**
{% raw %}
```yaml
# snapshots/dim_customer_scd2.yml
{% snapshot dim_customer_snapshot %}
{{
  config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['loyalty_tier', 'segment', 'region']
  )
}}
SELECT
  customer_id,
  name,
  email,
  loyalty_tier,
  segment,
  region
FROM {{ source('crm', 'customers') }}
{% endsnapshot %}
```
{% endraw %}
```
-- dbt generates:
-- dbt_scd_id (hash of unique_key + dbt_updated_at)
-- dbt_updated_at (load timestamp)
-- dbt_valid_from (eff_from)
-- dbt_valid_to (eff_to, NULL for current)
```

**Example 2 — Manual SCD Type 2 ETL:**
```sql
-- Step 1: Detect changed records
WITH incoming AS (
  SELECT customer_id, loyalty_tier,
    MD5(loyalty_tier || COALESCE(segment,'') || COALESCE(region,''))
    AS hash_diff
  FROM staging_customers
),
current_dim AS (
  SELECT customer_id, hash_diff
  FROM dim_customer WHERE is_current = TRUE
)
SELECT i.*
FROM incoming i
JOIN current_dim c USING (customer_id)
WHERE i.hash_diff != c.hash_diff;  -- only changed rows

-- Step 2: Close old current rows
UPDATE dim_customer
SET is_current = FALSE,
    effective_to = CURRENT_DATE - 1
WHERE customer_id IN (SELECT customer_id FROM changed_rows)
  AND is_current = TRUE;

-- Step 3: Insert new rows
INSERT INTO dim_customer (customer_key, customer_id,
  loyalty_tier, is_current, effective_from, effective_to)
SELECT nextval('customer_key_seq'), customer_id, loyalty_tier,
  TRUE, CURRENT_DATE, NULL
FROM changed_rows;
```

---

### ⚖️ Comparison Table

| SCD Type | History Preserved | Storage Growth | Query Complexity | When to Use |
|---|---|---|---|---|
| **Type 1** | None | None | Simple (no join for history) | Error corrections, unimportant attrs |
| **Type 2** | Full | 1 row per change | Medium (filter is_current or date range) | Tier, category, segment changes |
| **Type 3** | One prior value | 1 extra column | Simple | When only "previous" matters |
| **Type 4** | Full (mini-dim) | Moderate | Medium | Ragged hierarchy |
| **Type 6** | Full + current fill | 2 rows per change | Low (current fill avoids self-join) | Large DWH with both analyses needed |

**How to choose:** Type 2 for most analytical dimensions where
historical accuracy matters. Type 1 for fields that can be
safely overwritten (typo corrections, phone number format). Type 6
when analysts frequently query both "as it was" and "as it is now"
in the same report.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Type 2 wastes storage | A customer with 3 tier changes over 10 years = 4 dim rows. Compared to billions of fact rows, this is negligible |
| SCD only applies to customer and product dims | SCD applies to any slowly changing attribute: sales territories (reassigned quarterly), managers (changed annually), product pricing tiers, regulatory classifications |
| Type 2 requires querying with complex date ranges | With `is_current = TRUE`, current queries are simple. Historical queries use effective date ranges only when needed — most BI queries are current-state |
| Type 1 is always wrong | Type 1 is correct for error corrections (typo in product name) and for attributes where history genuinely doesn't matter (updated phone number) |
| Surrogate keys aren't needed for SCD | Without surrogate keys, SCD Type 2 fails — you cannot have two rows with the same business key as the PK. Surrogate keys make multiple version rows per entity possible |

---

### 🚨 Failure Modes & Diagnosis

**All Historical Reports Show Current Attributes (Type 1 on Historical Dimension)**

**Symptom:**
A loyalty programme analysis shows higher Gold revenue than
expected for periods before the Gold tier was launched.
Historical reports are unreliable.

**Root Cause:**
`dim_customer` is SCD Type 1. When customers upgraded, their
current tier overwrote all historical. All historical fact rows
now join to customer's current state.

**Diagnostic Command / Tool:**
```sql
-- Check if dim_customer is SCD Type 2
SELECT COUNT(*) FROM (
  SELECT customer_id
  FROM dim_customer
  GROUP BY customer_id HAVING COUNT(*) > 1
) t;
-- Result = 0: SCD Type 1 (no versions)
-- Result > 0: SCD Type 2 exists
```

**Fix:**
Rebuild dim_customer as SCD Type 2 from source system change logs.
If source doesn't have change history: accept lost history, apply
Type 2 going forward.

**Prevention:**
Classify all dimension attributes as Type 1, 2, or 3 BEFORE
initial data load. Implement Type 2 for all analytically sensitive
attributes before any fact records are created.

---

**Late-Arriving Dimension Change (Fact Loaded Before Dim Updated)**

**Symptom:**
Sales reports for March show some orders under Bronze tier even
though the customer was upgraded to Silver on March 1.

**Root Cause:**
The fact table ETL ran at 1 AM March 2 using cust_key=1001
(Bronze). The dim_customer ETL loaded the Silver upgrade at
2 AM March 2. The March 1 orders were already processed with
the Bronze surrogate key.

**Diagnostic Command / Tool:**
```sql
-- Find fact rows that reference closed (old) dim versions
-- for events that occurred after the dim change
SELECT f.order_id, f.order_date, d.tier, d.effective_to
FROM fact_orders f
JOIN dim_customer d ON f.cust_key = d.cust_key
WHERE d.effective_to IS NOT NULL  -- closed version
  AND f.order_date > d.effective_to;  -- event after dim closed
```

**Fix:**
Re-key affected fact rows:
```sql
UPDATE fact_orders f
SET cust_key = (
  SELECT min(cust_key) FROM dim_customer dc
  WHERE dc.customer_id = (
    SELECT customer_id FROM dim_customer
    WHERE cust_key = f.cust_key
  )
  AND dc.effective_from <= f.order_date
  AND (dc.effective_to >= f.order_date OR dc.effective_to IS NULL)
)
WHERE f.cust_key IN (SELECT cust_key FROM affected_fact_rows);
```

**Prevention:**
Load dimension ETL BEFORE fact ETL in the same pipeline.
Add SCD key validation: a SCD Type 2 check at fact load time
to ensure the surrogate key's effective period covers the fact's
event date.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Dimensional Modeling` — SCD is a core technique within
  Kimball's dimensional modeling methodology
- `Fact Table vs Dimension Table` — SCD addresses how
  dimension tables change; understanding dimensions first
- `Star Schema` — the full pattern that SCD dimensions
  participate in

**Builds On This (learn these next):**
- `Data Vault` — uses Satellite tables with load_date/end_date
  to implement full historisation natively
- `Data Warehouse` — the enterprise system where SCD is
  most commonly needed
- `ETL vs ELT` — the pipeline patterns used to detect and
  implement SCD changes

**Alternatives / Comparisons:**
- `Data Vault Satellites` — the alternative to SCD
  for enterprise data warehouses requiring full auditability
- `Event Sourcing` — application-level pattern for recording
  all state changes as events; similar concept at app layer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Strategies for handling dimension         │
│              │ attribute changes over time               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Overwriting dimension attributes destroys │
│ SOLVES       │ historical accuracy of all linked facts   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Surrogate keys enable versioning: FK in   │
│              │ fact points to entity AT THAT TIME        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any attribute that affects historical     │
│              │ reporting (tier, category, region)        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Type 1 for error corrections; Type 2 for  │
│              │ frequently-changed low-category attrs     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Historical accuracy vs storage growth and │
│              │ ETL complexity                            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Type 1 overwrites the truth.             │
│              │  Type 2 versiones it."                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Data Lake → Data Warehouse →              │
│              │ Data Lakehouse                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A financial institution uses SCD Type 2 on `dim_account`
to track account classification changes. After 10 years, a single
account has 47 version rows. An analyst asks: "What was this
account's classification on every day for the past year?" This
requires 365 calendar date lookups against the SCD Type 2 rows.
Describe the SQL pattern (joining dim to a calendar table) that
answers this, the performance challenge with 47-version lookup,
and two approaches to optimise it.

**Q2.** A large retailer uses SCD Type 6 on `dim_product` to
support two analyses simultaneously: (a) "Revenue by the product
category AT TIME OF SALE" and (b) "Revenue by product's CURRENT
category" for merchandising. Explain what columns SCD Type 6
adds compared to Type 2, how the `current_category` column is
maintained when a product changes category (tracing the
exact UPDATE statement across all existing version rows), and
what happens when the THIS current_category fill is not maintained
atomically — what data inconsistency emerges.

