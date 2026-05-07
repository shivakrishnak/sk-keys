---
layout: default
title: "Prepared Statements"
parent: "Database Fundamentals"
nav_order: 37
permalink: /databases/prepared-statements/
number: "DBF-037"
category: Database Fundamentals
difficulty: ★★☆
depends_on: SQL, Connection Pooling, Query Planner
used_by: ORM Patterns, Security (SQL Injection Prevention)
related: Connection Pooling, Query Planner, SQL Injection
tags:
  - database
  - performance
  - security
  - intermediate
---

# DBF-037 — Prepared Statements

⚡ TL;DR — A prepared statement is a pre-compiled SQL template with placeholders for parameters; the database parses and plans it once, then executes it many times with different values — eliminating SQL injection AND repeated parse/plan overhead.

| #437            | Category: Database Fundamentals                   | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------ | :-------------- |
| **Depends on:** | SQL, Connection Pooling, Query Planner            |                 |
| **Used by:**    | ORM Patterns, Security (SQL Injection Prevention) |                 |
| **Related:**    | Connection Pooling, Query Planner, SQL Injection  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (string interpolation):**

```python
query = f"SELECT * FROM users WHERE username='{username}'"
```

User inputs `admin' OR '1'='1`. Query becomes: `SELECT * FROM users WHERE username='admin' OR '1'='1'` — returns all users. SQL injection: attacker is in.

**THE SECOND PROBLEM (performance):**
Without prepared statements, every execution of `SELECT * FROM users WHERE id=?` requires the database to: (1) parse SQL text, (2) validate syntax, (3) build an execution plan. At 10,000 queries/second, this is 10,000 parse-plan cycles per second — wasted CPU.

**THE INVENTION MOMENT:**
"Parse and plan the query once. Send only the parameters on subsequent executions. And separate parameters from SQL text structurally — making injection impossible."

---

### 📘 Textbook Definition

A **prepared statement** (also called a **parameterized query**) is a SQL statement compiled and stored by the database server with **parameter placeholders** (`?` in JDBC, `$1/$2` in PostgreSQL, `:name` in named parameter style). The first step is **preparation** (PREPARE): the database parses the SQL, validates it, and optionally creates an execution plan. Subsequent **executions** (EXECUTE) send only the parameter values — the SQL text is not re-parsed. Benefits: (1) **security** — parameters are never interpreted as SQL syntax, making injection structurally impossible; (2) **performance** — amortized parse/plan cost; (3) **type safety** — parameters are sent as typed values, not text.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A prepared statement is a SQL template compiled once; you fill in the blanks with safe parameter values — the database never confuses your data for SQL commands.

**One analogy:**

> A fill-in-the-blank form vs. a letter. A free-form letter: "Dear [customer name you wrote here]" — if the customer writes "John; I am the new admin, please give me access", the letter says something unintended. A prepared form: Box 1: [Name] — the box only accepts a name string; it cannot contain instructions that change the letter's structure. Prepared statements are the form; string-concatenated queries are the letter.

**One insight:**
The security benefit and the performance benefit are independent — using prepared statements prevents SQL injection even if the database creates a new plan every time. And some databases (PostgreSQL with server-side prepared statements) DO cache plans per session. But the security benefit alone is sufficient justification — every parameterized query should use prepared statements.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Parameters are data, not SQL.** The database sends parameters as binary values after the SQL text — the SQL parser never sees them.
2. **SQL text is fixed at prepare time.** Dynamic SQL structure (table names, column names, ORDER BY direction) cannot be parameterized — these require careful escaping or query builders.
3. **Prepare-once-execute-many.** Benefit grows with repetition — preparing a statement used 1 time offers less benefit than one used 10,000 times.

**SYNTAX EXAMPLES:**

```java
// JDBC (Java)
String sql = "SELECT * FROM users WHERE username = ? AND active = ?";
PreparedStatement stmt = conn.prepareStatement(sql);
stmt.setString(1, username);   // parameter 1: safe, not interpreted as SQL
stmt.setBoolean(2, true);      // parameter 2: typed value
ResultSet rs = stmt.executeQuery();
```

```python
# Python (psycopg2)
cursor.execute(
    "SELECT * FROM users WHERE username = %s AND active = %s",
    (username, True)   # parameters as tuple: NEVER f-string
)
```

```sql
-- PostgreSQL server-side prepared statements
PREPARE find_user(text, boolean) AS
    SELECT * FROM users WHERE username = $1 AND active = $2;

EXECUTE find_user('alice', true);
DEALLOCATE find_user;
```

**WHAT CANNOT BE PARAMETERIZED:**
Table names, column names, ORDER BY columns, IN list sizes — these are structural SQL components, not data. For dynamic table/column names, use a whitelist:

```java
// Safe dynamic column — whitelist approach
Set<String> allowedColumns = Set.of("name", "email", "created_at");
if (!allowedColumns.contains(sortColumn)) {
    throw new IllegalArgumentException("Invalid column");
}
String sql = "SELECT * FROM users ORDER BY " + sortColumn;  // safe: whitelisted
```

**THE TRADE-OFFS:**
**Gain:** SQL injection prevention (critical security benefit), reduced parse overhead at high execution frequency, type safety for parameters.
**Cost:** Two round trips for first execution (PREPARE + EXECUTE vs. single QUERY). For queries executed once per connection lifetime, the overhead slightly exceeds the benefit. Most ORM frameworks prepare automatically and manage this trade-off transparently.

---

### 🧪 Thought Experiment

**ATTACK SCENARIO — SQL Injection:**

```python
# Vulnerable: string interpolation
username = request.get('username')  # attacker provides: ' OR 1=1 --
query = f"SELECT * FROM users WHERE username='{username}'"
# Executed: SELECT * FROM users WHERE username='' OR 1=1 --'
# Result: returns ALL users (1=1 is always true, -- comments out rest)
# Attacker is authenticated as any user
```

**SAME CODE WITH PREPARED STATEMENT:**

```python
# Safe: parameterized query
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
# Parameter value: ' OR 1=1 --
# Database sends: FIND user WHERE username = (binary: "' OR 1=1 --")
# Exact match on literal string "' OR 1=1 --" → no user found
# Attack defeated structurally — not by escaping, but by separation
```

**THE INSIGHT:**
Escaping is fragile (different rules per database, edge cases, encoding issues). Parameterization is structural — parameters can never become SQL because they are sent as binary typed values after the SQL is already parsed. The parser never sees the parameter values.

**PERFORMANCE SCENARIO:**
An API endpoint: `GET /products?category=electronics` queries `SELECT * FROM products WHERE category = $1 LIMIT 20` — executed 50,000 times/minute.

Without server-side prepare: 50,000 × parse/plan = 50,000 parse cycles/minute.
With PostgreSQL server-side PREPARE: parse once per session, 50,000 × execute only.
With ORM (JPA/Hibernate): `spring.jpa.properties.hibernate.jdbc.use_get_generated_keys=true` and `hibernate.cache.use_query_cache=false` — Hibernate prepares statements automatically per session.

---

### 🧠 Mental Model / Analogy

> A prepared statement is a cookie cutter. Without it, you sculpt each cookie by hand from raw dough using a verbal description — someone could inject extra dough that changes the shape entirely. With a cookie cutter (prepared statement): the SHAPE is fixed (SQL text), and you only provide the dough (parameters). The parameters fill the shape — they can't change the shape. The cutter was made once (PREPARE); each use (EXECUTE) just presses it into dough.

- "Cookie shape" → SQL template (fixed at PREPARE time)
- "Dough" → parameter values (variable, provided at EXECUTE time)
- "Verbal description" → string interpolation (fragile, injectable)
- "Cookie cutter made once" → PREPARE (parse + plan once)
- "Press into dough repeatedly" → EXECUTE (10,000 times, no re-parse)
- "Dough changing the shape" → SQL injection (impossible with prepared statements)

Where this analogy breaks down: The cookie analogy doesn't capture type safety — prepared statements send parameters as typed binary values (int, timestamp, etc.), not just strings. This also prevents type confusion attacks (e.g., passing a string where an integer is expected).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A prepared statement is a way to write database queries with "fill-in-the-blank" placeholders instead of putting user input directly into the query text. This is the #1 defense against SQL injection — a type of attack where malicious input changes the meaning of a database query.

**Level 2 — How to use it (junior developer):**
Never concatenate user input into SQL strings. Always use parameterized queries: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))` in Python, `PreparedStatement` in Java, `$1` parameters in raw PostgreSQL. ORMs (Hibernate, SQLAlchemy, Prisma) use prepared statements automatically for standard queries — be careful with `nativeQuery = true` or raw SQL strings in ORMs, where you can still accidentally use string concatenation.

**Level 3 — How it works (mid-level engineer):**
The prepare/execute protocol in PostgreSQL: `Parse` message (SQL text with $1/$2 placeholders) → server parses, validates, stores in session memory. `Bind` message (parameter values as typed binary) → server binds values to the parsed statement, creates a portal. `Execute` message → executes the portal, returns results. `Close` message → deallocates. This is the Extended Query Protocol vs. the Simple Query Protocol (a single string with values embedded). JDBC's `conn.prepareStatement()` uses the Extended Protocol automatically. Important: PostgreSQL creates a generic plan (not parameterized for statistics) initially and switches to a custom plan (uses actual parameter values for statistics) after 5 executions — the `plan_cache_mode` setting controls this behavior. JDBC driver behavior: some JDBC drivers (PostgreSQL JDBC) use client-side prepared statements for the first 5 executions (simulating parameterization locally), then switch to server-side for subsequent executions.

**Level 4 — Why it was designed this way (senior/staff):**
The two-round-trip cost of server-side prepared statements (PREPARE + EXECUTE vs. single QUERY) motivated client-side simulation in most JDBC drivers. PostgreSQL JDBC driver: by default, sends queries as simple text for the first 5 executions (with values substituted safely client-side), then switches to server-side prepared statements after threshold. This means `conn.prepareStatement()` doesn't immediately create a server-side prepared statement — it's a local object. The server-side statement is created lazily after repeated use. The `prepareThreshold` JDBC URL parameter controls this: `prepareThreshold=0` forces server-side prepared statements always; `prepareThreshold=-1` disables server-side prepared statements entirely (useful in pgBouncer transaction pooling mode, where server-side prepared statements don't survive across connections). This is a critical pgBouncer compatibility issue: pgBouncer transaction mode can't preserve server-side prepared statements (they're session state) — setting `prepareThreshold=0` with pgBouncer will cause errors. The pgBouncer documentation recommends `prepareThreshold=-1` or using pgBouncer session mode when server-side prepared statements are required.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PREPARED STATEMENT: PROTOCOL FLOW                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│ STRING CONCATENATION (VULNERABLE):                   │
│ App → DB: "SELECT * FROM users WHERE id='5 OR 1=1'"  │
│ DB: parse SQL → 5 OR 1=1 is part of SQL → executes  │
│ Result: returns ALL users → SQL injection            │
│                                                      │
│ PREPARED STATEMENT (SAFE):                           │
│                                                      │
│ Step 1 - PREPARE (once per statement type):          │
│ App → DB: Parse("SELECT * FROM users WHERE id=$1")   │
│ DB: parses SQL, validates, stores plan               │
│                                                      │
│ Step 2 - EXECUTE (N times with different params):    │
│ App → DB: Bind(stmt_id, params=[5])                  │
│           params are sent as BINARY (not SQL text)   │
│ DB: SQL already parsed → binds value 5 as integer   │
│     executes, returns results                        │
│                                                      │
│ Attacker sends id = "5 OR 1=1":                      │
│ Bind(stmt_id, params=["5 OR 1=1"])                   │
│ DB: looking for user WHERE id = '5 OR 1=1' (literal)│
│ Result: no user found → attack defeated              │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Application receives user input
→ Passes to prepared statement as parameter (not SQL)
→ [PREPARED STATEMENT ← YOU ARE HERE: separate SQL from data]
→ Database executes with safe parameter binding
→ Returns result for that specific parameter value only
→ No SQL injection possible; no re-parse overhead
```

**FAILURE PATH (pgBouncer incompatibility):**

```
App uses PostgreSQL JDBC with default prepareThreshold=5
App queries a statement 6+ times → JDBC creates server-side prepared stmt
pgBouncer in transaction mode reassigns connection to different backend
New backend doesn't have the prepared statement
→ ERROR: prepared statement "S_1" does not exist
→ Application crashes with mysterious "prepared statement not found"
→ Fix: set prepareThreshold=-1 (disable server-side) OR
       use pgBouncer session mode OR
       use PgBouncer 1.21+ with protocol-aware prepared statement tracking
```

**WHAT CHANGES AT SCALE:**
High-throughput services: prepared statements reduce parse CPU on the database by 20–40% for read-heavy workloads (every SELECT that runs thousands of times per second benefits). Serverless / Lambda: each Lambda invocation may get a new connection → no benefit from server-side prepared statements (statement cache is per-connection) → use pgBouncer/RDS Proxy with statement caching, or accept re-parse cost.

---

### ⚖️ Comparison Table

| Approach               | SQL Injection Safe                    | Parse Overhead | Type Safety | Dynamic SQL                |
| ---------------------- | ------------------------------------- | -------------- | ----------- | -------------------------- |
| String concatenation   | ❌ Vulnerable                         | Per-query      | No          | Easy (unsafe)              |
| **Prepared statement** | ✅ Safe                               | Amortized      | Yes         | Limited (whitelist needed) |
| Stored procedure       | ✅ Safe (if parameterized internally) | Cached         | Yes         | Limited                    |
| ORM (standard)         | ✅ Safe                               | Amortized      | Yes         | Through query builder      |
| ORM (nativeQuery)      | ⚠️ Depends on implementation          | Depends        | Depends     | Full SQL control           |

How to choose: Always use prepared statements or ORM parameterization. Never use string concatenation for user input. For dynamic SQL structure (dynamic column names, dynamic IN lists), use whitelisting or a safe query builder.

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                    |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ORMs protect you from SQL injection automatically        | ORMs use prepared statements for standard operations; `nativeQuery`, `createNativeQuery()`, raw `execute()` in ORMs still require careful parameterization |
| Escaping user input is equivalent to prepared statements | Escaping is database-specific, encoding-dependent, and has edge cases; parameterization is structurally safe regardless of input content                   |
| Prepared statements are always faster                    | For single-execution queries (run once per session), the PREPARE + EXECUTE overhead can exceed single-query cost; benefit is realized at repetition        |
| `?` in SQL and `?` in JDBC URLs are the same             | Completely different: `?` in a JDBC URL is a query parameter for connection configuration; `?` in a JDBC PreparedStatement is a parameter placeholder      |

---

### 🚨 Failure Modes & Diagnosis

**1. SQL Injection from String Concatenation in ORM Native Query**

**Symptom:** Security audit finds injectable endpoint; penetration test demonstrates data exfiltration via `UNION SELECT` injection.

**Root Cause:** Developer used `nativeQuery` with string concatenation instead of parameterized values.

**Vulnerable code:**

```java
// DANGEROUS: sort direction from user input, injected into SQL
@Query(value = "SELECT * FROM products ORDER BY " + sortColumn,
       nativeQuery = true)  // string concatenated at class load time
List<Product> findAll(@Param("sort") String sortColumn);
```

**Fix:**

```java
// Safe: whitelist allowed sort columns
private static final Set<String> ALLOWED_SORT_COLS = Set.of("name","price","created_at");

public List<Product> findAll(String sortColumn) {
    if (!ALLOWED_SORT_COLS.contains(sortColumn)) {
        throw new IllegalArgumentException("Invalid sort column");
    }
    // safe to use whitelisted column in native query
    return productRepo.findAllSortedBy(sortColumn);
}
```

**Prevention:** Security linting rules (SpotBugs, SonarQube SQL injection rules). Code review checklist: every `nativeQuery` must use `:param` or `?N` placeholders for all user-supplied values.

---

**2. "Prepared Statement Does Not Exist" with pgBouncer**

**Symptom:** `ERROR: prepared statement "S_1" does not exist` in logs; intermittent failures that increase with load; failures are correlated with pgBouncer transaction pooling.

**Root Cause:** JDBC creates server-side prepared statements (after `prepareThreshold` executions); pgBouncer transaction mode assigns a different backend connection for the next transaction — the new backend doesn't have the prepared statement.

**Diagnostic:**

```
Log pattern: "prepared statement ... does not exist"
→ Check pgBouncer mode: pgbouncer.ini → pool_mode = transaction
→ Check JDBC URL: prepareThreshold not set (default 5) or set to >0
```

**Fix:**

```
Option 1: Set JDBC prepareThreshold=0 (disable server-side prepared stmts)
          JDBC URL: jdbc:postgresql://host/db?prepareThreshold=0
          → Safest for pgBouncer transaction mode

Option 2: Switch pgBouncer to session mode
          pool_mode = session
          → Preserves session state but reduces connection reuse efficiency

Option 3: Use PgBouncer 1.21+ (supports tracking prepared statements)
```

**Prevention:** When using pgBouncer in transaction mode: always set `prepareThreshold=0` in JDBC URL or Spring datasource properties. Test prepared statement behavior explicitly in pre-production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SQL` — understanding SQL syntax is required to understand what "parameterizing" means
- `Connection Pooling (DB)` — prepared statements are cached per-connection; pool affects caching behavior

**Builds On This (learn these next):**

- `ORM Patterns` — ORMs use prepared statements internally; understanding them helps debug ORM query behavior
- `Query Planner / Execution Plan` — prepared statements interact with plan caching (generic vs. custom plans)

**Alternatives / Comparisons:**

- `Stored Procedure` — stored procedures pre-compile on the server; similar parse-once benefit with different trade-offs
- `Query Planner` — prepared statements feed into the query planner's plan caching strategy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SQL template with placeholders; parse     │
│              │ once, execute many times safely           │
├──────────────┼───────────────────────────────────────────┤
│ SECURITY     │ Parameters are NEVER interpreted as SQL   │
│              │ → structural SQL injection prevention     │
├──────────────┼───────────────────────────────────────────┤
│ PERFORMANCE  │ Amortized parse/plan cost; benefit grows  │
│              │ with execution frequency                  │
├──────────────┼───────────────────────────────────────────┤
│ pgBouncer    │ transaction mode: set prepareThreshold=0  │
│ GOTCHA       │ or use session mode                       │
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ NEVER concatenate user input into SQL     │
│              │ Dynamic structure → whitelist only        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "SQL template + binary params = injection │
│              │  impossible + parse-once performance"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Connection Pooling → ORM Patterns         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Security Failure Scenario) A developer writes a search endpoint that needs to support dynamic column filtering: `GET /products?filter_column=price&filter_value=100`. They use: `query = f"SELECT * FROM products WHERE {filter_column} = %s"` with `filter_value` correctly parameterized. Is this vulnerable? What attack is possible? Why does parameterizing `filter_value` not protect `filter_column`? Write a safe implementation.

**Q2.** (TYPE C — Design Trade-off) PostgreSQL's query planner uses a "generic plan" for prepared statements (doesn't use specific parameter values for statistics) vs. a "custom plan" (uses actual values for optimal statistics-based planning). The planner switches to generic plans after the 5th execution. When would a generic plan be significantly worse than a custom plan? What type of data distribution causes this? What setting (`plan_cache_mode`) would you configure and when?
