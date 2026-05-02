---
layout: default
title: "Declarative Programming"
parent: "CS Fundamentals — Paradigms"
nav_order: 2
permalink: /cs-fundamentals/declarative-programming/
number: "0002"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming, Functions
used_by: Functional Programming, Reactive Programming, SQL
related: Imperative Programming, Functional Programming, Domain-Specific Languages
tags:
  - foundational
  - pattern
  - mental-model
  - first-principles
---

# 002 — Declarative Programming

⚡ TL;DR — Declarative programming means telling the computer WHAT you want, not HOW to get it — you describe the goal, the system figures out the steps.

| #002 | Category: CS Fundamentals — Paradigms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Imperative Programming, Functions | |
| **Used by:** | Functional Programming, Reactive Programming, SQL | |
| **Related:** | Imperative Programming, Functional Programming, Domain-Specific Languages | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Imagine querying a database imperatively: you'd have to open the
file, iterate every row, compare each field manually, collect
matches, sort them yourself, and handle pagination by hand. For a
query involving 3 tables and 5 conditions, that's hundreds of
lines of code — all of which you'd rewrite for every new query.

THE BREAKING POINT:
When the "how" of fetching data is identical every time (scan,
filter, sort, project), writing it out manually wastes effort and
introduces inconsistency. The "what" — give me all users over 30
in London sorted by name — is always the interesting part.

THE INVENTION MOMENT:
This is exactly why Declarative Programming was created. SQL in
1974 let programmers say `SELECT name FROM users WHERE age > 30`
— describing the desired result. The database engine figures out
the execution plan. HTML lets you say "this is a heading" — the
browser figures out how to render it.

### 📘 Textbook Definition

Declarative programming is a paradigm in which programs specify
WHAT computation should be performed rather than HOW to perform it.
The programmer expresses the desired outcome or properties of the
result; the underlying engine, runtime, or compiler determines the
optimal execution strategy. SQL, HTML, CSS, Prolog, and functional
languages (when used without explicit recursion patterns) are
canonical examples.

### ⏱️ Understand It in 30 Seconds

**One line:**
Describe the outcome you want; let the system work out the steps.

**One analogy:**

> Ordering at a restaurant is declarative: you say "I'll have the
> salmon, medium rare." You don't tell the chef how to cook it —
> step by step, knife by knife. You declare the desired result.

**One insight:**
Declarative code is often shorter and more readable than its
imperative equivalent because it removes the accidental complexity
of HOW — loops, counters, temporary variables — and leaves only
the essential complexity of WHAT. The trade-off is less control
over performance.

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. The program describes a relationship or desired state — not
   the procedure to achieve it.
2. The execution strategy is delegated — a query planner,
   runtime, or compiler determines the steps.
3. Declarative code is often closer to the problem domain —
   SQL looks like English because the "how" is abstracted away.

DERIVED DESIGN:
If the execution strategy can be standardised (for databases:
always scan-filter-project; for UI: always diff-then-patch), then
it makes sense to build an engine that handles the "how" once,
and expose a declarative API for the "what." This design pays off
when:

- The engine can optimise (SQL query planner picks the best index)
- The "how" is mechanical (HTML rendering algorithm)
- The domain maps cleanly to a declarative vocabulary

THE TRADE-OFFS:
Gain: Conciseness, readability, engine-level optimisation, less
code to maintain, queries that survive schema changes.
Cost: Less control over execution; harder to express irregular
procedural logic; debugging requires understanding the engine.

### 🧪 Thought Experiment

SETUP:
You want all product names with price under £50, sorted alphabetically,
from a table of 10 million products.

WHAT HAPPENS WITHOUT DECLARATIVE (imperative SQL-equivalent):

1. Open table file
2. Allocate result list
3. For each row, parse fields, compare price field to 50
4. If match, append name to result list
5. After full scan, sort result list alphabetically
6. Return first N items

10 million iterations. No index usage. Sort is O(n log n).
Code: ~50 lines. Duplicated for every new query variation.

WHAT HAPPENS WITH DECLARATIVE (SQL):

```sql
SELECT name FROM products
WHERE price < 50
ORDER BY name;
```

The query planner sees an index on `price`, uses it to skip 95%
of rows, and uses a merge sort on the already-indexed key.
Code: 3 lines. Result is the same.

THE INSIGHT:
Declarative abstraction lets the engine exploit knowledge you
don't have — index structures, statistics, parallelism — to
execute far better than hand-written imperative code would.

### 🧠 Mental Model / Analogy

> Declarative programming is like filing a tax form. You fill in the
> boxes: income, deductions, dependants. You declare the facts. The
> tax authority's system calculates the result using rules you
> never see. You described WHAT is true about your situation — the
> HOW is the government's problem.

"Filling in the boxes" → writing declarative statements
"The tax form fields" → the declarative API/schema
"The tax calculation engine" → the runtime/query planner
"Your tax bill" → the computed result

Where this analogy breaks down: unlike tax forms, declarative
programs can compose and nest — you can build complex pipelines
from simple declarative expressions.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Declarative programming is telling the computer what you want, not
how to get it. Like asking a librarian for "the three most recent
sci-fi novels" — you don't explain how they should search the
shelves.

**Level 2 — How to use it (junior developer):**
SQL is declarative: write `WHERE`, `ORDER BY`, `GROUP BY` and let
the database handle it. HTML is declarative: write `<button>` and
the browser renders it. In React, you declare what the UI should
look like given the current state — React handles the DOM updates.

**Level 3 — How it works (mid-level engineer):**
Declarative systems separate the specification from the execution
engine. A SQL query is parsed into a logical plan (relational
algebra), then a query optimizer rewrites it into a physical plan
(choosing indexes, join algorithms), then an executor runs it.
The same SELECT can execute 100x faster with a different physical
plan — the declarative interface is stable while the engine evolves.

**Level 4 — Why it was designed this way (senior/staff):**
The declarative paradigm emerged from formal logic (Prolog) and
relational algebra (Codd's 1970 paper). The key insight: if you
have a closed-world model (complete data), you can derive all
answers from declared facts and rules. The trade-off accepted is
loss of execution control for gain in correctness and optimisability.
Modern systems like Apache Spark DataFrames and TensorFlow graphs
adopt declarative APIs precisely to enable distributed execution
optimisation invisible to the user.

### ⚙️ How It Works (Mechanism)

The execution pipeline for a declarative system typically has
three distinct phases:

```
┌──────────────────────────────────────────────────┐
│      DECLARATIVE EXECUTION PIPELINE              │
├──────────────────────────────────────────────────┤
│                                                  │
│  [Declarative Statement]                         │
│       ↓                                          │
│  [Parser] → Abstract Syntax Tree                 │
│       ↓                                          │
│  [Semantic Analysis / Binding]                   │
│       ↓                                          │
│  [Logical Plan] (what operations)                │
│       ↓                                          │
│  [Optimiser] ← YOU ARE HERE                      │
│       ↓  (rewrites to physical plan)             │
│  [Physical Plan] (how to execute)                │
│       ↓                                          │
│  [Executor] → Result                             │
└──────────────────────────────────────────────────┘
```

**Parsing:** The declarative statement is tokenised and parsed into
an AST — a structural representation of the query's meaning.

**Optimisation:** This is the declarative paradigm's superpower.
The optimiser applies algebraic transformations: push filters down
(reduce data early), choose join order (smaller table first),
pick access paths (index scan vs. full scan). None of this is
visible to the programmer.

**Execution:** The physical plan is executed, potentially in parallel
across nodes in a distributed system. The declarative interface
remains unchanged regardless of whether execution is local or
distributed across 100 nodes.

**Happy path:** The optimiser finds a good plan and execution is
efficient. The programmer's simple declaration outperforms naive
imperative code.

**Failure path:** When statistics are stale or the schema is unusual,
the optimiser picks a bad plan. A filter that matches 80% of rows
gets pushed down, but it's slower than a full scan. Performance
degrades invisibly because the programmer has no control.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:

```
[Developer writes SELECT/HTML/JSX]
  → [Parser produces AST]
  → [Binder resolves names to schema]
  → [Logical plan: relational algebra]
  → [Optimiser rewrites plan ← YOU ARE HERE]
  → [Physical plan: index scan, hash join]
  → [Executor runs plan]
  → [Result returned to application]
```

FAILURE PATH:
[Stale statistics → bad plan → full scan instead of index]
→ [Query runs 100x slower]
→ [Observable: slow query log, high I/O metrics]

WHAT CHANGES AT SCALE:
At 10x data volume, the optimiser's choice of join order matters
exponentially — a wrong join order on 10M rows vs 1M rows
increases cost by 100x. At 100x, declarative frameworks like Spark
transparently distribute execution across a cluster while the
`DataFrame.filter().groupBy()` API stays identical to single-node.

### 💻 Code Example

**Example 1 — Imperative vs Declarative: filter and sort (Python):**

```python
products = [
    {"name": "Mouse", "price": 25},
    {"name": "Keyboard", "price": 75},
    {"name": "Monitor", "price": 45},
]

# BAD (imperative): manual loop, sort, filter
result = []
for p in products:
    if p["price"] < 50:
        result.append(p["name"])
result.sort()

# GOOD (declarative style with comprehension):
result = sorted(
    p["name"] for p in products if p["price"] < 50
)
# Output: ['Monitor', 'Mouse']
```

**Example 2 — SQL declarative query:**

```sql
-- BAD: trying to be "imperative" in SQL (cursor-based)
DECLARE cursor FOR SELECT * FROM orders;
OPEN cursor;
FETCH cursor INTO @row;
WHILE @@FETCH_STATUS = 0 BEGIN
  IF @row.total > 100 INSERT INTO large_orders...
  FETCH cursor INTO @row;
END

-- GOOD: let the engine optimise
INSERT INTO large_orders
SELECT * FROM orders WHERE total > 100;
```

**Example 3 — React declarative UI:**

{% raw %}
```jsx
// BAD (imperative DOM manipulation):
document.getElementById("btn").style.color = "red";
document.getElementById("count").textContent = count + 1;

// GOOD (declarative React):
function Counter({ count }) {
  return (
    <div>
      <button style={{ color: count > 0 ? "red" : "black" }}>
        Count: {count}
      </button>
    </div>
  );
}
// React diffs and updates the DOM — we declare WHAT, not HOW
```
{% endraw %}

### ⚖️ Comparison Table

| Style           | Control | Optimisable | Readability | Best For                |
| --------------- | ------- | ----------- | ----------- | ----------------------- |
| **Declarative** | Low     | High        | High        | Queries, UI, config     |
| Imperative      | High    | Low         | Medium      | Algorithms, system code |
| Functional      | Medium  | Medium      | High        | Data transforms         |
| Procedural      | High    | Low         | Medium      | Scripts, simple flows   |

How to choose: Use declarative when the engine can optimise better
than you can, or when expressing WHAT is more stable than HOW.
Switch to imperative when you need precise control over every step.

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                       |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Declarative code doesn't execute imperatively | Under the hood, all declarative code compiles to imperative CPU instructions — the declarative layer is an abstraction                        |
| Declarative is always slower than imperative  | A SQL query planner often beats hand-written loops because it exploits indexes and statistics you can't see                                   |
| HTML is a programming language                | HTML is declarative markup — it describes structure, not computation — but the distinction matters less than understanding what it expresses  |
| Declarative programming means no state        | SQL queries operate on stateful tables; React components have state — declarative describes the EXPRESSION of logic, not the absence of state |

### 🚨 Failure Modes & Diagnosis

**1. Query Plan Regression**

Symptom:
A query that ran in 50ms now takes 30 seconds after a data load.
No code change was made.

Root Cause:
The query optimiser's statistics are stale. After loading 50M new
rows, the optimiser still thinks the table has 100K rows and
chooses a full scan instead of an index seek.

Diagnostic:

```sql
-- PostgreSQL: show actual plan
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;

-- MySQL: check optimizer trace
SET optimizer_trace="enabled=on";
SELECT ...;
SELECT * FROM information_schema.OPTIMIZER_TRACE;
```

Fix:

```sql
-- Update statistics so optimiser has accurate data
ANALYZE TABLE orders;          -- MySQL
ANALYZE orders;                -- PostgreSQL
UPDATE STATISTICS orders;      -- SQL Server
```

Prevention: Schedule regular statistics updates after bulk loads;
monitor slow query logs for plan regressions.

**2. N+1 Query Problem**

Symptom:
Loading 100 users takes 101 database queries. Page loads slowly;
database connection pool exhausted.

Root Cause:
Declarative ORM code that looks like "get users, then for each
user get their orders" issues one query per user instead of a join.

Diagnostic:

```bash
# Enable query logging in Spring Boot application.properties
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql=TRACE
# Count queries in output — 100 users = 100+ SELECT statements
```

Fix:

```java
// BAD: N+1 — one query per user
List<User> users = userRepo.findAll();
for (User u : users) {
    List<Order> orders = orderRepo.findByUser(u); // N queries
}

// GOOD: single JOIN query via eager fetch
@Query("SELECT u FROM User u JOIN FETCH u.orders")
List<User> findAllWithOrders();
```

Prevention: Always check generated SQL when using ORM; use
`JOIN FETCH` or `@BatchSize` annotations proactively.

**3. Over-Abstraction Hiding Bugs**

Symptom:
Declarative pipeline produces wrong results; difficult to trace
which step in the pipeline introduced the error.

Root Cause:
Long chains of declarative transformations make it hard to
inspect intermediate state; a filter condition has a logic error
that's invisible until the final result.

Diagnostic:

```python
# Break the pipeline to inspect intermediate state
result = (
    df.filter(df.price < 50)    # add .show() here to debug
    .groupBy("category")
    .agg({"price": "avg"})
)

# Debugging step: materialise intermediate result
filtered = df.filter(df.price < 50)
filtered.show(10)  # inspect before aggregation
```

Prevention: Add intermediate checkpoints during development;
write unit tests for each stage of a declarative pipeline.

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Imperative Programming` — understanding HOW clarifies why WHAT is valuable
- `Functions` — declarative style often uses function composition

**Builds On This (learn these next):**

- `Functional Programming` — the discipline of declarative code in general-purpose languages
- `Reactive Programming` — declarative event stream composition
- `SQL` — the canonical real-world declarative language

**Alternatives / Comparisons:**

- `Imperative Programming` — the contrasting paradigm; explicit HOW
- `Domain-Specific Languages` — extreme form of declarative design for one domain
- `Logic Programming` — fully declarative using rules and unification (Prolog)

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS │ Describing WHAT you want, not HOW to get │
│ │ it — the engine figures out the steps │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT │ Removing accidental complexity of "how" │
│ SOLVES │ from domain logic; enabling optimisation │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT │ The engine often optimises better than │
│ │ hand-written imperative code │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN │ Query data, describe UI, configure │
│ │ infrastructure, express transformations │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN │ Precise execution control is required; │
│ │ the engine's abstraction hides bugs │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF │ Conciseness + optimisability vs. loss of │
│ │ control over execution strategy │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER │ "Order at a restaurant — describe what │
│ │ you want; the kitchen figures out how." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Functional → SQL → Reactive Programming │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A React component re-renders every second because a parent
passes a new object reference even though the data is identical.
Trace step-by-step how React's declarative reconciliation algorithm
determines what changed — and at what point does the declarative
abstraction break down, requiring you to reach for `useMemo` or
`React.memo` as an imperative override?

**Q2.** A SQL query planner chooses a full table scan over an
available index on a column with 5 distinct values out of 1 million
rows. Why is this the CORRECT declarative decision — and what does
it reveal about the fundamental contract between a declarative
programmer and a query engine?
