---
layout: default
title: "SQL Injection"
parent: "HTTP & APIs"
nav_order: 243
permalink: /http-apis/sql-injection/
number: "0243"
category: HTTP & APIs
difficulty: ★★☆
depends_on: SQL, Databases, HTTP, Input Validation
used_by: Backend APIs, Database-driven Applications
related: XSS, SSRF, API Security, Parameterized Queries, ORM
tags:
  - security
  - sql-injection
  - database
  - injection
  - owasp
  - intermediate
---

# 243 — SQL Injection

⚡ TL;DR — SQL Injection is an attack where untrusted user input is embedded directly into a SQL query, allowing the attacker to manipulate the query structure — bypassing authentication, extracting all data from the database, modifying records, or even executing OS commands on the database server; prevented by parameterized queries (prepared statements) and ORM use.

| #243 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SQL, Databases, HTTP, Input Validation | |
| **Used by:** | Backend APIs, Database-driven Applications | |
| **Related:** | XSS, SSRF, API Security, Parameterized Queries, ORM | |

---

### 🔥 The Problem This Solves (The Threat)

**THE ATTACK:**
Application builds a SQL query using URL parameters:

```java
// VULNERABLE:
String query = "SELECT * FROM users WHERE username='" + username
             + "' AND password='" + password + "'";
```

Attacker enters as username: `admin' --`
Resulting query: `SELECT * FROM users WHERE username='admin' --' AND password='...'`
`--` is a SQL comment. Everything after it is ignored. The password check is bypassed.
Attacker logs in as `admin` without knowing the password.

Or: username = `'; DROP TABLE users; --`
Resulting query: `SELECT * FROM users WHERE username=''; DROP TABLE users; --'`
All users deleted.

---

### 📘 Textbook Definition

**SQL Injection (SQLi)** is a code injection vulnerability (OWASP Top 10 #3, Injection)
in which an attacker inserts or "injects" malicious SQL code into a query constructed
from user-controlled input, causing the database to execute the attacker's commands.
SQL injection can result in: authentication bypass, unauthorized data access (data
exfiltration — including all rows in a table or entire database), data modification
or deletion, denial of service (drop tables), information disclosure (error messages
revealing schema), and in some configurations, remote code execution (via `xp_cmdshell`
in SQL Server or `LOAD_FILE`/`INTO OUTFILE` in MySQL). Prevention: **parameterized
queries / prepared statements** (the primary defense), ORMs (which use parameterized
queries internally), input allowlist validation, stored procedures (if parameters
are not re-concatenated), and principle of least privilege for database accounts.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SQL Injection happens when your application builds SQL by gluing user input into a
query string — the attacker's input becomes SQL code instead of data.

**One analogy:**

> SQL Injection is like a fill-in-the-blank form that someone fills in unexpectedly.
> Form: "List all movies by director: [blank]"
> Expected: "Spielberg"
> Attacker fills: "Spielberg'; SELECT \* FROM credit_cards WHERE '1'='1"
> The database executes the whole thing as a command.
> The blank was supposed to hold data. It held SQL code instead.

**One insight:**
The root cause is treating a SQL query template as a string concatenation problem.
The fix is to treat the query structure and the data as fundamentally separate:
parameterized queries send the query template to the DB, then bind data separately —
the DB engine NEVER confuses them, because they arrive through different channels.

---

### 🔩 First Principles Explanation

**CLASSIC ATTACK PATTERNS:**

```
PATTERN 1 — Authentication Bypass
  Query: "SELECT * FROM users WHERE user='" + user + "' AND pwd='" + pwd + "'"
  Input: user = "admin'--", pwd = (anything)
  Result: "SELECT * FROM users WHERE user='admin'--' AND pwd='anything'"
  Effect: comment eliminates password check → logs in as admin

PATTERN 2 — UNION-based Data Exfiltration
  Query: "SELECT name, price FROM products WHERE id=" + id
  Input: id = "1 UNION SELECT username, password_hash FROM users--"
  Result: "SELECT name,price FROM products WHERE id=1
           UNION SELECT username,password_hash FROM users--"
  Effect: response contains product data PLUS all usernames and password hashes

PATTERN 3 — Blind SQL Injection (no visible output)
  Query: "SELECT * FROM products WHERE id=" + id
  Input: id = "1 AND 1=1" → returns result (true)
  Input: id = "1 AND 1=2" → returns no result (false)

  Attacker: binary search by asking true/false questions:
  "1 AND (SELECT COUNT(*) FROM users) > 100"  → result? → yes/no
  "1 AND ASCII(SUBSTRING((SELECT password FROM users WHERE id=1),1,1)) > 64"
  → extract passwords character by character (slow but effective)

PATTERN 4 — Stacked Queries / Command Execution
  SQL Server: "SELECT * FROM users WHERE id=1; EXEC xp_cmdshell('whoami')"
  → executes OS command on database server
  → can install malware, exfiltrate files
  (requires high-privilege DB account — defense-in-depth: least privilege)
```

**WHY PARAMETERIZED QUERIES WORK:**

```
VULNERABLE — String concatenation:
  String query = "SELECT * FROM users WHERE id = " + userId;
  Statement stmt = conn.createStatement();
  ResultSet rs = stmt.executeQuery(query);

  Input: userId = "1 OR 1=1"
  Query: "SELECT * FROM users WHERE id = 1 OR 1=1" → returns ALL users!

SECURE — Parameterized query (prepared statement):
  String query = "SELECT * FROM users WHERE id = ?";  ← ? is a placeholder
  PreparedStatement stmt = conn.prepareStatement(query);
  stmt.setInt(1, userId);  ← userId bound as DATA, not SQL code
  ResultSet rs = stmt.executeQuery();

  Input: userId = "1 OR 1=1"
  Database receives: query template + parameter {1: "1 OR 1=1"}
  Database interprets "1 OR 1=1" as the LITERAL value of the id parameter
  Result: WHERE id = '1 OR 1=1' → no rows (no user with that id)
  The injection string is treated as data, not SQL syntax.

WHY:
  The query structure is compiled separately from the data
  Data is sent in binary parameter binding, not as SQL text
  The DB engine's SQL parser never sees the data — it's bound after parsing
  → structural injection is impossible
```

---

### 🧪 Thought Experiment

**ORM DOESN'T AUTOMATICALLY PROTECT YOU:**

```
JPA/Hibernate — Safe JPQL with parameters:
  @Query("SELECT u FROM User u WHERE u.username = :username")
  User findByUsername(@Param("username") String username);
  → SAFE: named parameter binding, equivalent to prepared statement

JPA/Hibernate — UNSAFE: native query with concatenation:
  @Query(value = "SELECT * FROM users WHERE username = '" + username + "'",
         nativeQuery = true)
  → UNSAFE: string concatenation in a native query = classic SQL injection

JPA/Hibernate — UNSAFE: JPQL with concatenation:
  String jpql = "SELECT u FROM User u WHERE u.username = '" + username + "'";
  em.createQuery(jpql).getResultList();
  → UNSAFE: JPQL injection possible, same vulnerability

String-based dynamic sorting — common XSS:
  // Developer writes: "safe to build ORDER BY from validated column name"
  String query = "SELECT * FROM products ORDER BY " + sortColumn;
  // sortColumn from request param: "price; DROP TABLE products--"
  // → SQL injection in ORDER BY clause (can't parameterize ORDER BY column)
  // Fix: allowlist validation: if (!ALLOWED_COLUMNS.contains(sortColumn)) throw;
```

---

### 🧠 Mental Model / Analogy

> SQL Injection is like telling someone to "mail a letter to John" and they write
> the entire instruction on the address line:
>
> Safe (parameterized): "Mail this letter [drops letter in mailbox labeled 'John']"
> The envelope structure (SQL) and the recipient data (parameter) are separate.
>
> Vulnerable (concatenation): "Mail a letter to [John]; send all letters TO ATTACKER instead"
> The instruction and the data are in the same string. The recipient can redefine
> the instruction.
>
> Parameterized queries: the postmaster receives the SQL template FIRST (parse phase),
> then receives the parameter bindings SEPARATELY. The recipient name (parameter)
> can NEVER change the mail routing instructions (SQL structure).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
SQL Injection means an attacker puts SQL code into an input field (like a search box
or login form). If the website directly uses that input in its database query, the
database executes the attacker's code, potentially revealing all your data or deleting it.

**Level 2 — How to prevent it (junior developer):**
ALWAYS use parameterized queries / prepared statements. Never concatenate user input
into SQL strings. Use JPA, Hibernate, or Spring Data JPA — they use parameterized
queries for JPQL/HQL. For dynamic SQL: use query builders (JPA Criteria API, jOOQ)
not string concatenation. For ORDER BY: validate against an allowlist of column names.

**Level 3 — How it works (mid-level engineer):**
The DB engine processes queries in two phases: parse (understanding the query structure)
and execute (running against data). Parameterized queries separate these phases: the
template is parsed first, and parameters are bound at execute time — the parser never
sees the user input. This structural separation makes injection impossible: the data
can't alter the already-parsed query structure. Second-order SQL injection: input is
sanitized on the way in but later used without sanitization in another query (e.g., a
stored procedure that builds dynamic SQL from stored values). Defense: use parameterized
queries at EVERY database interaction, not just the first point of entry.

**Level 4 — Why it persists (senior/staff):**
SQL injection has been known since the 1990s but persists because: (1) legacy code
bases contain thousands of concatenated queries that are expensive to refactor,
(2) ORMs create false confidence (developers believe ORM means safe, missing that
native queries and raw JPQL can still be vulnerable), (3) dynamic query construction
(search, filtering, sorting) remains hard to parameterize completely — ORDER BY
columns can't be parameterized, requiring allowlists, (4) stored procedures don't help
if they dynamically construct SQL internally using `EXEC` or `sp_executesql` with
concatenation. Defense-in-depth: parameterized queries + WAF (catch obvious attacks)

- least-privilege DB accounts (limit blast radius) + column-level encryption of
  sensitive data (even if extracted, data is encrypted) + network isolation (DB not
  directly accessible from internet).

---

### ⚙️ How It Works (Mechanism)

```
PREPARED STATEMENT INTERNALS:

Phase 1 — Parse (no user input):
  Client: conn.prepareStatement("SELECT * FROM users WHERE id = ?")
  Database: parses SQL text → builds query execution plan
             The "?" is a placeholder — means "parameter will come later"
             ← Query plan stored. No data evaluated yet.

Phase 2 — Bind (user input as raw bytes, not SQL text):
  Client: stmt.setInt(1, userId)  // userId = "1 OR 1=1"
  Database: receives parameter value as binary: {type: INTEGER, value: "1 OR 1=1"}
             Execution: WHERE id = '1 OR 1=1' (literal string!)
             No SQL parsing happens on the parameter value
             ← The query structure cannot change

WHY THIS IS SAFE:
  The DB engine NEVER parses user input as SQL
  User input is always treated as a typed data value
  "1 OR 1=1" as a VARCHAR is just a string — it doesn't mean OR in SQL anymore
```

---

### 🔄 The Complete Picture — End-to-End Protection

```
HTTP Request:
  GET /api/users/search?name=Alice';DROP+TABLE+users;--

Application (SAFE):
  String query = "SELECT * FROM users WHERE name LIKE ?";
  stmt.setString(1, "%" + name + "%");
  // name = "Alice';DROP TABLE users;--" → no injection possible
  // DB query: WHERE name LIKE '%Alice'';DROP TABLE users;--%'
  //   → LIKE treats the value literally → 0 results, no harm

Application (UNSAFE):
  String query = "SELECT * FROM users WHERE name LIKE '%" + name + "%'";
  // name = "Alice%'; DROP TABLE users;--"
  // query: WHERE name LIKE '%Alice%'; DROP TABLE users;--' → tables dropped!

ADDITIONAL DEFENSES:
  DB account: SELECT, INSERT only — no DROP, no EXEC
  → Even if injected: can't drop tables (no permission)
  WAF rule: block obvious SQLi patterns in request
  Error handling: return generic "internal error" not SQL error messages
  → SQL errors reveal table names, column names, DB version (information disclosure)
```

---

### 💻 Code Example

```java
// VULNERABLE — never do this:
@GetMapping("/users/search")
public List<User> searchVulnerable(@RequestParam String name, Connection conn) throws SQLException {
    // NEVER: string concatenation into SQL
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";
    Statement stmt = conn.createStatement();
    return mapResults(stmt.executeQuery(sql));
}

// SECURE — parameterized query (raw JDBC):
@GetMapping("/users/search")
public List<User> searchSafe(@RequestParam String name, Connection conn) throws SQLException {
    String sql = "SELECT * FROM users WHERE name = ?";
    PreparedStatement stmt = conn.prepareStatement(sql);
    stmt.setString(1, name);  // bound as data, never as SQL
    return mapResults(stmt.executeQuery());
}

// SECURE — Spring Data JPA (uses parameterized queries internally):
public interface UserRepository extends JpaRepository<User, Long> {
    // SAFE: JPQL with named parameter
    @Query("SELECT u FROM User u WHERE u.name = :name")
    List<User> findByName(@Param("name") String name);

    // SAFE: derived query (auto-parameterized by Spring Data)
    List<User> findByNameContainingIgnoreCase(String name);

    // UNSAFE: native query with concatenation — never do this:
    // @Query(value = "SELECT * FROM users WHERE name = '" + name + "'", nativeQuery = true)
}

// SAFE — dynamic ORDER BY (can't parameterize column names):
public List<User> findAllSorted(String sortField, String direction) {
    // Allowlist: reject any column name not in approved list
    Set<String> allowedColumns = Set.of("name", "email", "created_at", "role");
    Set<String> allowedDirs = Set.of("ASC", "DESC");

    if (!allowedColumns.contains(sortField) || !allowedDirs.contains(direction.toUpperCase())) {
        throw new IllegalArgumentException("Invalid sort parameter");
    }
    // Safe: sortField is validated against allowlist — not from raw input
    return jdbcTemplate.query(
        "SELECT * FROM users ORDER BY " + sortField + " " + direction,
        userRowMapper
    );
}
```

---

### ⚖️ Comparison Table

| Approach                              | SQLi Safe | Notes                           |
| ------------------------------------- | --------- | ------------------------------- |
| **String concatenation**              | ❌        | Classic vulnerability           |
| **`PreparedStatement` + `?`**         | ✅        | Primary defense                 |
| **Spring Data JPA derived queries**   | ✅        | Auto-parameterized              |
| **JPQL named parameters (`:param`)**  | ✅        | JPA standard                    |
| **Native query string concatenation** | ❌        | ORM doesn't protect this        |
| **`ORDER BY` + allowlist**            | ✅        | Only safe way for column names  |
| **Stored procedures (static SQL)**    | ✅        | Safe if no internal dynamic SQL |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                  |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ORM usage prevents SQL injection               | ORMs use parameterized queries by default for their standard methods — but native queries, JPQL with concatenation, and `@Query` with string building are still vulnerable               |
| Input validation/sanitization prevents SQLi    | Sanitization is fragile — encodings bypass it. Parameterized queries are the structural fix; sanitization is only defense-in-depth                                                       |
| SQL injection is old and rare                  | SQL injection remains in OWASP Top 10 every year. Automated scanners (sqlmap) make exploitation trivial; even one-line CVs in legacy code are critical vulnerabilities                   |
| Error messages help debugging so leave them in | SQL error messages in production responses reveal schema details, table names, column names — diagnostic gold for attackers. Use generic errors in production; log specifics server-side |

---

### 🚨 Failure Modes & Diagnosis

**Second-Order SQL Injection**

Symptom:
Security scanner finds no injection at signup (input is properly sanitized).
But a dormant payload stored in the database is later used unsafely in an admin query,
triggering SQL injection when an admin views a user record.

Root Cause:

```
1. Signup: username = "admin'--" → sanitized/escaped before insert → stored safely
2. Admin page query:
   String sql = "SELECT * FROM audit_log WHERE user='" + storedUsername + "'";
   // storedUsername read from DB: "admin'--" (stored safely but used unsafely)
   // Query: "...WHERE user='admin'--'" → comment breaks query
```

Diagnostic / Fix:

```java
// The fix is the same: use parameterized queries AT EVERY DB READ/QUERY,
// not just at the point of first input.
// Even values read FROM the database could be attacker-controlled.
String sql = "SELECT * FROM audit_log WHERE user = ?";
stmt.setString(1, storedUsername); // always parameterize, regardless of source
```

---

### 🔗 Related Keywords

- `XSS` — client-side injection (into HTML/JS) vs SQL injection (into database queries)
- `SSRF` — another injection/misuse: making the server fetch attacker-controlled URLs
- `Parameterized Queries` — the structural defense: the only reliable SQLi prevention
- `Principle of Least Privilege` — limits blast radius when SQLi does occur via low-privilege DB accounts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Attacker input interpreted as SQL code,  │
│              │ manipulating query structure              │
├──────────────┼───────────────────────────────────────────┤
│ PRIMARY FIX  │ Parameterized queries / PreparedStatement │
│              │ ALWAYS — even for values from DB         │
├──────────────┼───────────────────────────────────────────┤
│ ORM WARNING  │ ORM safe for JPQL named params, derived  │
│              │ queries; UNSAFE for native + concatenation│
├──────────────┼───────────────────────────────────────────┤
│ ORDER BY     │ Allowlist validate column name; can't    │
│              │ parameterize column names                 │
├──────────────┼───────────────────────────────────────────┤
│ DEPTH DEF    │ Low-priv DB account; WAF; encrypted cols │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Never concatenate user input into SQL"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SSRF → XSS → Parameterized Queries       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A legacy codebase has 3,000 SQL queries, approximately 200 of which your automated scanner flags as potentially involving string concatenation with request parameters. Remediating all 200 in one sprint is unrealistic. Design a risk triage strategy: how do you quickly identify which 10 are critical (high blast radius, reachable without authentication), which 90 are medium risk, and which 100 are low risk (internal tools, admin-only). What criteria drive this ranking and what's your remediation ordering?
