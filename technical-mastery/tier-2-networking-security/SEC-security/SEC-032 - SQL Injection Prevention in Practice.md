---
id: SEC-032
title: "SQL Injection Prevention in Practice"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-011, SEC-017, SEC-018, SEC-025
used_by: SEC-063, SEC-067
related: SEC-011, SEC-017, SEC-025, SEC-063, SEC-067
tags:
  - security
  - sql-injection
  - parameterized-queries
  - orm
  - prevention
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/sec/sql-injection-prevention-in-practice/
---

⚡ TL;DR - Preventing SQL injection requires SEPARATING SQL
CODE from DATA. The single most effective technique:
parameterized queries (prepared statements). Every other
technique is defense-in-depth, not a replacement.

**The fix:** Never concatenate user input into SQL strings.
Use parameterized queries with `?` or named placeholders.
The database processes code and data separately, so user
input can NEVER be interpreted as SQL syntax.

**Why ORMs aren't automatically safe:** Most ORMs generate
parameterized queries for standard CRUD, but provide raw
query escapes for complex cases. `raw()`, `execute()`, `extra()`,
`textQuery()` - all are potential injection points if they
include user input without parameterization.

**Defense in depth (not replacements):**
- Stored procedures (if they use parameterization internally)
- Input validation (allowlists reject clearly invalid data early)
- Least privilege DB users (limits damage if injection occurs)
- WAF rules (detect, not prevent - bypassed by obfuscation)

---

| #032 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | SQL Injection, Input Validation vs Output Encoding, Least Privilege, Attacker Mindset | |
| **Used by:** | SAST, Business Logic Vulnerabilities | |
| **Related:** | SQL Injection, SAST, Input Validation vs Output Encoding, Least Privilege | |

---

### 🔥 The Problem This Solves

**SQL INJECTION IS STILL #3 ON OWASP 2021:**
Despite being a solved problem with known, easy fixes:
SQL injection remains one of the most prevalent critical
vulnerabilities in production applications. The cause:
developers who understand the concept continue writing
string concatenation in SQL queries because "it works"
during development and the vulnerability is invisible
without adversarial testing. This entry is about: making
the correct pattern a reflex, recognizing the wrong pattern
immediately in code review, and understanding ALL injection
vectors (not just the simple login bypass).

---

### 📘 Textbook Definition

**SQL Injection Prevention:** The set of techniques that
eliminate or mitigate SQL injection vulnerabilities.
Prevention requires ARCHITECTURAL controls (parameterized
queries), not just INPUT FILTERING (which can be bypassed).

**Parameterized Query (Prepared Statement):** A query
template with placeholders for values, processed in two
phases: (1) the database parses the SQL structure (with
placeholders, no user data), (2) user values are bound
to placeholders as DATA only. User input can never be
interpreted as SQL syntax regardless of its content.

**Named Parameters:** Parameterized queries using named
placeholders (`:username`, `@username`, `%(username)s`)
instead of positional `?`. More readable, reduces positional
errors.

**Stored Procedures:** Pre-compiled SQL stored in the database.
Secure IF they use parameterization internally. Vulnerable
if they construct dynamic SQL from their parameters using
concatenation.

**ORM (Object-Relational Mapper):** Library that generates
SQL from object operations. Standard ORM operations (`.filter()`,
`.where()`) typically generate parameterized queries.
Raw/escape hatches (`.raw()`, `.execute()`) may not.

**Input Validation:** Allowlisting or rejecting clearly
invalid inputs before processing. Defense-in-depth, not
a replacement for parameterization. You can reject inputs
containing SQL characters, but: (1) you'll generate false
positives for legitimate inputs (names with apostrophes:
O'Brien), (2) obfuscated SQLi bypasses character filters,
(3) second-order injection bypasses runtime validation
(stored then retrieved and used later).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use parameterized queries. Never concatenate user input
into SQL strings. ORMs are safe for standard operations,
dangerous for raw query escapes. Least privilege DB users
contain blast radius if injection occurs.

**One analogy:**
> Parameterized queries separate the floor plan (SQL query
> structure) from the furniture (data values). Without
> parameterization: giving someone your floor plan AND
> allowing them to add structural walls wherever they want.
> They can change your rooms into something you didn't intend.
> With parameterization: the structural walls (SQL syntax)
> are fixed and compiled. The user only places furniture
> (data values) in predefined positions. No matter what
> "furniture" they bring: it can't change the walls.

---

### 🔩 First Principles Explanation

**WHY PARAMETERIZATION WORKS:**

```
SQL INJECTION ROOT CAUSE:
  The database interpreter doesn't know where SQL code ends
  and user data begins when both are concatenated in a string.

CONCATENATION (vulnerable):
  Python:
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
  
  Attacker input: "' OR '1'='1"
  
  Result: "SELECT * FROM users WHERE name = '' OR '1'='1'"
  Database sees: [WHERE clause with] (name = '') OR ('1'='1')
  = all rows returned. Authentication bypass.

PARAMETERIZATION (secure):
  Python:
    cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
    # OR with named parameter:
    cursor.execute("SELECT * FROM users WHERE name = :name",
                   {"name": user_input})
  
  What the database does:
    Phase 1: Parse SQL structure: "SELECT * FROM users WHERE name = ?"
    Phase 2: Bind user_input as DATA to the ? position.
    
  Attacker input: "' OR '1'='1"
  
  Database: "I need a row where name EQUALS THE STRING ' OR '1'='1'"
  There's no such row. Returns 0 results.
  
  THE KEY DIFFERENCE:
    Concatenation: database gets ONE string, must parse code and data together.
    Parameterization: database gets SQL structure FIRST (compiled, locked),
    THEN receives data as a separate value. Data CANNOT contain SQL syntax
    because the parsing phase is complete. User input is always treated
    as a literal value, never as code.

SECOND-ORDER INJECTION (often missed):
  Data sanitized at input, stored in database.
  Later retrieved and used in another SQL query via concatenation.
  
  User registers: username = "admin'--"
  Stored: "admin'--" in database (valid storage)
  
  Later, password reset function:
    username = db.get_username(user_id)  # Returns "admin'--"
    # Developer assumes: "this came from my own DB, it's safe"
    query = "UPDATE users SET password = ? WHERE username = '" + username + "'"
    # Result: UPDATE users SET password = ? WHERE username = 'admin'--'
    # Comment operator (--) comments out rest of query
    # Updates ALL admin users' passwords!
  
  Prevention: ALWAYS use parameterized queries, even with data
    from your own database. The source of data doesn't make it safe.
```

---

### 🧪 Thought Experiment

**SCENARIO: Code review exercise - find all injection points**

```
CODE TO REVIEW (Python Flask app):

def get_product(product_id):
    conn = get_db()
    # SAFE: product_id from URL parameter
    result = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )
    return result.fetchone()

def search_products(search_term, category, order_by):
    conn = get_db()
    
    # VULNERABLE 1: direct concatenation in WHERE clause
    query = (
        "SELECT * FROM products "
        "WHERE name LIKE '%" + search_term + "%'"
    )
    
    # VULNERABLE 2: ORDER BY clause cannot be parameterized
    # (column names can't be bound as parameters)
    query += " ORDER BY " + order_by
    
    # "SAFE-ish" 3: category with parameterization (good)
    if category:
        query += " AND category = ?"
        result = conn.execute(query, (category,))
    else:
        result = conn.execute(query)
    
    return result.fetchall()

ANALYSIS:
  Line 1 (get_product): SAFE. Parameterized query. ✓
  
  Line 2 (search_term): VULNERABLE. String concatenation.
    Attacker: search_term = "%'; DROP TABLE products;--"
    Fix: query += " WHERE name LIKE ?", use ("%" + search_term + "%",)
    
  Line 3 (order_by): VULNERABLE. ORDER BY cannot use parameters.
    (Database requires column names in ORDER BY, not string values)
    This is a legitimate limitation.
    Fix: ALLOWLIST for order_by column names:
      ALLOWED_ORDER_COLUMNS = {"name", "price", "created_at"}
      if order_by not in ALLOWED_ORDER_COLUMNS:
          raise ValueError("Invalid sort column")
      query += f" ORDER BY {order_by}"  # Safe after allowlist check
    
  Line 4 (category): SAFE. Parameterized. ✓

KEY LESSON:
  SQL injection prevention is not "use parameterization everywhere."
  For dynamic column names (ORDER BY, table names): parameterization
  is not possible. Use allowlists for those specific cases.
  Allowlist = explicitly enumerate valid values. If not in list: reject.
  Never use a denylist (filter out "bad" characters) for column names.
```

---

### 🧠 Mental Model / Analogy

> Parameterized queries are like a bank wire transfer form
> with pre-printed fields. The form structure (FROM account,
> TO account, AMOUNT fields) is pre-printed and fixed.
> The user fills in VALUES but cannot change the form structure.
> Even if a user writes "and also transfer from everyone
> else's account" in the AMOUNT field: the bank treats it
> as an invalid amount, not as a new instruction. String
> concatenation is like accepting hand-written letters
> where users can write any instruction they want in
> whatever format they choose, and you'll execute whatever
> you read. The bank (database) doesn't know the form
> structure if you let users write the letter.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Never build SQL queries by gluing strings together with
user input. Use the database library's parameterized query
feature where `?` or `:name` holds the place for user data.
The database treats the user's data as a VALUE, not as
part of the command. This prevents users from inserting
SQL commands into their input that the database would execute.

**Level 2 - How to use it (junior developer):**
Every database library in every language has parameterized query support:
Python `cursor.execute("SELECT * FROM t WHERE id = ?", (id,))`,
Java `PreparedStatement.setInt(1, id)`, Node `db.query("SELECT * FROM t WHERE id = $1", [id])`,
PHP `$stmt->bind_param("i", $id)`. The pattern is always:
query template with placeholders + separate values array/tuple.
When using an ORM: standard methods are safe. Avoid `.raw()`,
`.execute()` with string formatting, `.extra()` unless you
understand they require explicit parameterization.

**Level 3 - How it works (mid-level engineer):**
Edge cases requiring special handling: (1) ORDER BY column
names - use allowlists. (2) Table names in multi-tenant
schemas - use allowlists or generate programmatically from
validated constants. (3) IN clauses with variable length -
most libraries require programmatic placeholder generation:
`"WHERE id IN (" + ",".join(["?"] * len(ids)) + ")"` then
pass `ids` as values. (4) LIKE wildcards - escape `%` and `_`
in the VALUE, not in the query template:
`"%%" + value.replace("%", "\\%") + "%%"`. (5) Dynamic
search queries built from optional filter parameters -
build query programmatically with consistent parameterization.

**Level 4 - Why it was designed this way (senior/staff):**
Prepared statements work because modern databases compile
query plans from the SQL template BEFORE receiving parameter
values. The compilation phase locks the query semantics.
When values arrive later: they're treated as data points
for an already-finalized query plan. This also provides
performance benefits: the same prepared statement can be
reused with different values without re-compilation. The
performance and security benefits come from the same source:
code/data separation at the database level. Stored procedures
achieve the same separation WHEN they don't use dynamic SQL
internally. Unfortunately, stored procedures that build
queries with string concatenation internally are just as
vulnerable as application-level concatenation.

**Level 5 - Mastery (distinguished engineer):**
Comprehensive SQL injection prevention at scale includes:
application-level parameterization (primary), ORM wrapper
enforcement (code review, SAST rules for `.raw()` usage),
database-level controls (stored procedures with definer rights,
application-level users without DROP TABLE privileges), WAF
rules (detect, alert, not primary prevention), and monitoring
(unusual query patterns, query volume spikes). Static analysis
(SAST) tools with taint tracking: follow user input from HTTP
parameter through application code to SQL execution - flag
any path where user data reaches a SQL execution function
without parameterization. This automates code review for
this specific vulnerability class at scale.

---

### ⚙️ How It Works (Mechanism)

**Parameterized query processing at the database level:**

```
WITHOUT PARAMETERIZATION:
  Application sends: SELECT * FROM users WHERE name = 'O' OR 1=1--'
  Database: parses string → sees: WHERE name='O' OR 1=1 (SQL syntax!)
  Executes the malicious query. Attacker wins.

WITH PARAMETERIZATION:
  Phase 1 (query compilation):
    Application sends to database: SELECT * FROM users WHERE name = ?
    Database: parse SQL structure, create execution plan
    The ? is compiled as "data placeholder for a scalar value"
  
  Phase 2 (data binding):
    Application sends: bind ? = "O' OR 1=1--"
    Database: "I need a row where name equals the string O' OR 1=1--"
    Database treats entire value as a literal string
    No SQL parsing of the bound value
    Returns 0 results (no such username)
  
  DATABASE DRIVER IMPLEMENTATION:
    The database driver handles encoding of parameter values.
    Special characters in values are escaped at the protocol level.
    The application doesn't need to manually escape values.
    (Manual escaping is error-prone and a common vulnerability source)

COMMON MISUNDERSTANDING:
  "I escaped the apostrophe, so it's safe."
  Manual escaping is fragile. It must be applied correctly
  to every value in every query in every code path.
  Parameterization applies automatically. No manual escaping needed.
  Escaping is also character-encoding-dependent: escaping
  in UTF-8 may not work correctly in UTF-16 or other encodings.
  Parameterization works regardless of character encoding.
```

---

### 💻 Code Example

**SQL injection prevention patterns across common scenarios:**

```python
import sqlite3
import psycopg2  # PostgreSQL

# PATTERN 1: Basic parameterized query
# BAD: String concatenation
def get_user_bad(username: str):
    conn = sqlite3.connect('app.db')
    # VULNERABLE: attacker controls WHERE clause
    result = conn.execute(
        f"SELECT * FROM users WHERE username = '{username}'"
    )
    return result.fetchone()

# GOOD: Parameterized query
def get_user_good(username: str):
    conn = sqlite3.connect('app.db')
    result = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)  # Tuple with one element - note comma
    )
    return result.fetchone()

# PATTERN 2: Multiple parameters
def search_users(name: str, role: str, limit: int):
    conn = sqlite3.connect('app.db')
    return conn.execute(
        "SELECT id, name, role FROM users "
        "WHERE name LIKE ? AND role = ? LIMIT ?",
        ("%" + name + "%", role, limit)  # LIKE wildcard in app, not query
    ).fetchall()

# PATTERN 3: Dynamic ORDER BY (cannot parameterize column names)
ALLOWED_SORT_COLUMNS = frozenset({"name", "email", "created_at"})
ALLOWED_SORT_DIRS = frozenset({"ASC", "DESC"})

def get_users_sorted(sort_col: str, sort_dir: str):
    # ALLOWLIST: only accept known column names
    if sort_col not in ALLOWED_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_col}")
    if sort_dir.upper() not in ALLOWED_SORT_DIRS:
        raise ValueError(f"Invalid sort direction: {sort_dir}")
    
    # Safe: column names from validated allowlist only
    query = f"SELECT * FROM users ORDER BY {sort_col} {sort_dir}"
    conn = sqlite3.connect('app.db')
    return conn.execute(query).fetchall()

# PATTERN 4: Dynamic IN clause
def get_users_by_ids(user_ids: list[int]):
    if not user_ids:
        return []
    conn = sqlite3.connect('app.db')
    # Build correct number of placeholders dynamically
    placeholders = ", ".join(["?"] * len(user_ids))
    query = f"SELECT * FROM users WHERE id IN ({placeholders})"
    return conn.execute(query, user_ids).fetchall()

# PATTERN 5: SQLAlchemy ORM (safe by default)
from sqlalchemy import text
from sqlalchemy.orm import Session

# GOOD: ORM-generated SQL (parameterized automatically)
def get_user_orm(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()

# BAD: Raw query with format string in ORM
def get_user_orm_bad(session: Session, username: str):
    # VULNERABLE: same as concatenation
    return session.execute(
        text(f"SELECT * FROM users WHERE username = '{username}'")
    ).fetchone()

# GOOD: Raw query with named parameters in ORM
def get_user_orm_raw(session: Session, username: str):
    return session.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": username}  # Bound parameter
    ).fetchone()

# PATTERN 6: PostgreSQL with psycopg2 (named parameters)
def get_product_pg(conn, product_id: int, category: str):
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, name, price FROM products
           WHERE id = %(id)s AND category = %(category)s""",
        {"id": product_id, "category": category}
    )
    return cursor.fetchone()
```

---

### ⚖️ Comparison Table

| Prevention Technique | Prevents SQLi? | Notes |
|:---|:---|:---|
| **Parameterized queries** | Yes (primary fix) | Use everywhere. Language-native support. |
| **ORM standard methods** | Yes (if correctly used) | Raw query escapes may not be safe |
| **Stored procedures** | If parameterized internally | Still vulnerable if they use concatenation |
| **Input validation** | Partially | False positives (O'Brien), bypass via encoding |
| **Output encoding** | No | Not relevant for SQLi prevention |
| **WAF rules** | Detect, not prevent | Bypassed by obfuscation, encoding |
| **Least privilege DB user** | No prevention, limits damage | Drop table user can't run DROP TABLE |
| **Manual escaping** | Fragile | Library parameterization is safer |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| ORMs make SQL injection impossible | ORMs generate parameterized SQL for standard operations (`.filter()`, `.where()`, `.find()`). But every popular ORM provides raw query escapes for complex queries, performance optimization, or database-specific features: SQLAlchemy `text()`, Django `raw()` and `extra()`, Hibernate `createNativeQuery()`, ActiveRecord `find_by_sql()`. These are legitimate features but require explicit parameterization. The ORM doesn't protect you from your own raw queries. SAST rules targeting these specific methods in your codebase find the remaining injection vectors. |
| Input validation is sufficient to prevent SQL injection | Input validation that rejects characters like `'`, `"`, `;`, `--` will catch simple SQL injection and is a useful defense layer. But: (1) Legitimate data contains these characters (O'Brien, don't--worry). Denylist causes false positives and poor UX. (2) Attackers bypass character filters using SQL encoding (`CHAR(39)` for apostrophe), hex encoding (`0x27`), or Unicode tricks. (3) Second-order injection: value is validated at input, stored safely, retrieved and used in a concatenated query later without revalidation. Parameterization is not affected by encoding tricks because the binding happens at the database driver level, after the query structure is fixed. |

---

### 🚨 Failure Modes & Diagnosis

**Finding SQL injection vulnerabilities in a codebase:**

```
MANUAL CODE REVIEW:
  Search patterns (grep/IDE) that may indicate vulnerabilities:
  
  Pattern: string formatting in SQL-like context:
    f"SELECT ... {variable}"     # Python f-string
    "SELECT ... " + variable     # String concatenation
    String.format("SELECT ... %s", variable)  # Java
    sprintf("SELECT ... %s", $var)  # PHP
    `SELECT ... ${variable}`     # JS template literal
  
  False positives: query string with only literals (no variables).
  True positives: any variable included in the SQL string without
    going through a parameterized binding.

SAST TOOLS FOR AUTOMATED DETECTION:
  - Semgrep: rules for SQL injection taint tracking
    (semgrep.dev/p/sql-injection)
  - SonarQube: java.sql.Statement usage with string concat
  - Bandit (Python): detects cursor.execute with string formatting
  - CodeQL: taint analysis from HTTP params to SQL execution
  
  SAST limitation: may miss second-order injection and complex
    control flow. Manual review for high-risk components.

DYNAMIC TESTING (DAST):
  - SQLMap: automated SQL injection testing tool
    sqlmap -u "http://target.com/search?q=test" --dbs
    Detects: error-based, blind, time-based, UNION-based SQLi
  - Burp Suite: manual testing with Repeater
    Inject: ', --, ; in each parameter
    Observe: database errors, different response sizes/timing
  - OWASP ZAP: passive + active scanning for SQLi patterns

SECOND-ORDER INJECTION TESTING:
  1. Register/create a user with payload in name:
     username = "admin'--"
  2. Use the application normally to trigger code paths
     that retrieve and use your username in SQL
  3. Observe: do actions fail? Do you see unexpected data?
     Does another user's data appear?
  Manual test: necessary because automated tools often
    don't test stored-then-retrieved injection paths.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `SQL Injection` - the vulnerability itself
- `Input Validation vs Output Encoding` - related prevention techniques
- `Principle of Least Privilege` - database user permissions

**Builds on this:**
- `SAST` - automated code scanning for injection
- `Business Logic Vulnerabilities` - related authorization flaws

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRIMARY FIX  │ Parameterized queries (prepared statements)│
│              │ query("...WHERE id = ?", [user_input])    │
├──────────────┼───────────────────────────────────────────┤
│ NEVER        │ String concatenation with user input       │
│              │ f"... WHERE name = '{user_input}'"        │
├──────────────┼───────────────────────────────────────────┤
│ ORM SAFETY   │ Standard filter/where: safe               │
│              │ .raw(), .execute(), text(): check each    │
├──────────────┼───────────────────────────────────────────┤
│ ORDER BY     │ Cannot parameterize column names          │
│              │ Use explicit allowlist: {"col1", "col2"}  │
├──────────────┼───────────────────────────────────────────┤
│ DEPTH        │ DB user without DROP/ALTER (least priv)   │
│              │ WAF to detect/alert (not sole defense)    │
│              │ Input validation (reject garbage early)   │
├──────────────┼───────────────────────────────────────────┤
│ SAST         │ Scan for concatenation in SQL context     │
│              │ Semgrep, Bandit, SonarQube, CodeQL        │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Separate code from data at every boundary." SQL injection
is the classic example, but the same principle prevents:
OS command injection (shell=True with user input), LDAP
injection (building LDAP filter strings), XPath injection,
template injection (user input in template strings),
SSRF (user-controlled URLs). In every case: code (the
query structure, the command, the template) must be defined
by the developer. Data (user values) must be bound separately
through a mechanism that ensures they're treated as data,
not code. "Parameterization" is the database-specific
name for this pattern. Look for the equivalent mechanism
in every system where user input flows into an interpreter.

---

### 💡 The Surprising Truth

Parameterized queries were available in database libraries
since the 1990s. SQL injection was described as a serious
vulnerability in 1998 (Jeff Forristal). Every language,
every framework, every database has had parameterized query
support for decades. Yet SQL injection remains in the
OWASP Top 10 in 2021, still causing major breaches (British Airways,
Heartland Payment Systems, Talk Talk). The Equifax-scale
impact of SQL injection - which could have been prevented
with a single code change replacing string concatenation
with `?` placeholders - demonstrates that awareness of
a vulnerability and fixing it in production are very
different problems. The lesson: security vulnerabilities
persist not because solutions are unknown or complex, but
because fixing them requires: identifying all instances
(comprehensive code review or SAST), prioritizing the fix
(competing with feature development), and having automated
tests that catch regressions. Investment in SAST tooling
and security regression tests pays for itself many times over
when measured against breach costs.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **WRITE** a parameterized query in at least two languages/ORMs
   for simple, multi-parameter, IN clause, and LIKE scenarios.
2. **IDENTIFY** in code review: every place user input reaches
   SQL without parameterization, including ORM raw() methods.
3. **HANDLE** the dynamic ORDER BY case correctly with allowlists.
4. **EXPLAIN** second-order injection and test for it manually.

---

### 🎯 Interview Deep-Dive

**Q: Walk me through how you would find and fix SQL injection
in a legacy codebase.**

*Why they ask:* SQL injection is common in legacy code.
Tests practical skills in discovery and remediation.

*Strong answer includes:*
- Discovery: SAST tool (Semgrep/Bandit) with SQL injection
  rules to find string concatenation in SQL contexts. Review
  all results (SAST has false positives). Manual review for
  high-risk: authentication queries, admin functions, search.
- Dynamic testing: run SQLMap against staging against each
  parameterized endpoint. Manual Burp testing for complex flows.
- Specific ORM audit: search for `.raw()`, `.execute()`,
  `.extra()`, `text()`, and every other raw escape hatch.
  Each requires review.
- Fix: replace concatenation with parameterized queries
  (`?` or named). For ORDER BY: implement allowlists.
  Update ORM raw queries to use bound parameters.
- Regression tests: add automated security regression tests
  for each fixed endpoint: inject `' OR '1'='1` and verify
  the endpoint returns 0 results / expected behavior.
- Defense in depth: least privilege DB users (application
  user should not have DROP, CREATE). WAF rules to detect
  patterns and alert.
- Second-order injection: specifically test: register with
  payload username, trigger all code paths that use username
  in SQL. Harder to find with SAST - requires manual testing
  or integration tests that exercise the stored-then-retrieved path.