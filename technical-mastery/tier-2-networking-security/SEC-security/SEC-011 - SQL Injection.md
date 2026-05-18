---
id: SEC-011
title: "SQL Injection"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-004, SEC-010
used_by: SEC-034, SEC-035
related: SEC-001, SEC-004, SEC-010, SEC-034, SEC-035, SEC-021, SEC-057
tags:
  - security
  - sql-injection
  - owasp
  - injection
  - web-security
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/sec/sql-injection/
---

⚡ TL;DR - SQL Injection occurs when user-controlled input
is concatenated into a SQL query rather than passed as a
parameter. The attacker's input is interpreted as SQL syntax,
not data. Result: the attacker controls the query structure.
They can bypass WHERE clauses (`' OR '1'='1`), dump entire
tables (`UNION SELECT`), or delete data (`; DROP TABLE`).
In ORM-based applications: nearly eliminated if ORMs are
used correctly (parameterized queries by default). The
persistent risk: raw SQL in performance-critical queries,
legacy code, dynamic column names (cannot be parameterized),
and stored procedures that construct queries with string
concatenation. Prevention is simple and complete:
parameterized queries (prepared statements) make SQL
injection structurally impossible - user input is always
treated as a literal value, never as SQL syntax.

---

| #011 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, OWASP Top 10, Hashing vs Encryption vs Encoding | |
| **Used by:** | SQL Injection Prevention, SAST | |
| **Related:** | OWASP Top 10, XSS, CSRF, Input Validation, SAST, SQL Injection Prevention | |

---

### 🔥 The Problem This Solves

**WORLD WITH THE VULNERABILITY (classic example):**
Login form: username and password fields. Backend query:
```sql
SELECT * FROM users
WHERE username = '[user input]' AND password = '[user input]'
```
Attacker submits: username = `admin' --`, password = anything.
Query becomes:
```sql
SELECT * FROM users
WHERE username = 'admin' --' AND password = 'ignored'
```
The `--` comments out the rest of the SQL. Query returns
the admin user record without password verification.
Attacker is now logged in as admin. This is a 1990s attack
that is still found in production applications in 2024.
Not because developers don't know about it - but because
SQL string concatenation looks natural and ORMs aren't
always used for every query.

---

### 📘 Textbook Definition

**SQL Injection:** A code injection attack where malicious
SQL statements are inserted into an entry field that is then
interpreted by a SQL engine. It exploits insufficient input
validation or the use of string concatenation to build SQL
queries. Category: OWASP A03:2021 Injection.

**Injection occurs when:**
- User-supplied data is included in a SQL query
- The data is not separated from the SQL syntax (not parameterized)
- The SQL engine cannot distinguish user data from SQL commands

**Types:**
- **In-band SQLi (Classic):** Results returned directly in the
  response (UNION-based: appends additional query; Error-based:
  extracts data via error messages).
- **Blind SQLi:** No direct output. Attacker infers answers from:
  True/False responses (Boolean-based: different behavior based
  on true/false condition), Time delays (Time-based: `SLEEP(5)`
  if condition is true).
- **Out-of-band SQLi:** Data exfiltrated via different channel
  (DNS queries, HTTP requests from database server). Rare, requires
  specific database features enabled.

**Impact:** Authentication bypass, data exfiltration (entire
database), data modification, data deletion, command execution
(via `xp_cmdshell` in MSSQL, `LOAD_FILE`/`INTO OUTFILE` in MySQL).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SQL injection = user input interpreted as SQL commands instead
of data, because the query is built by string concatenation.
Fix: parameterized queries - input can never be SQL syntax.

**One analogy:**
> Imagine a script reading: "Add a star to [movie name]'s
> review." Someone sends movie name = `"Terminator 2" AND delete
> all bad reviews`. The script blindly runs it: "Add a star to
> Terminator 2's review AND delete all bad reviews." SQL injection
> is the software equivalent: input is treated as a command,
> not as a value. Parameterized queries prevent this by treating
> everything from the user as a quoted literal value.

---

### 🔩 First Principles Explanation

**Why string concatenation breaks the data/code boundary:**

```
SQL PARSING MODEL:

A SQL parser reads characters and classifies them:
  - SQL keywords: SELECT, WHERE, AND, OR, UNION, DROP...
  - Identifiers: table names, column names
  - Literals: 'string', 123, TRUE
  - Delimiters: ', ", ;, --, /*

When you write:
  query = "SELECT * FROM users WHERE name = '" + user_input + "'"

And user_input = "admin":
  Query = "SELECT * FROM users WHERE name = 'admin'"
  Parser sees: SELECT (keyword), ... WHERE (keyword), name (identifier),
    = (operator), 'admin' (string literal). ✓ Correct.

When user_input = "admin' OR '1'='1":
  Query = "SELECT * FROM users WHERE name = 'admin' OR '1'='1'"
  Parser sees: ... WHERE name = 'admin' (end of string literal),
    OR (keyword), '1' = '1' (always true condition). ← SQLi!

THE PROBLEM: The SQL parser has NO WAY to know that the
  second ' was injected by the user rather than written by the
  developer. It is just text to the parser.

PARAMETERIZED QUERY FIX:
  query = "SELECT * FROM users WHERE name = ?"
  cursor.execute(query, ["admin' OR '1'='1"])
  
  The SQL engine pre-compiles the query template.
  Then substitutes the parameter VALUE (not SQL text).
  The string "admin' OR '1'='1" is treated as a single
  literal value - the single quote inside it is never
  interpreted as SQL syntax. The parser CANNOT be confused
  because it never sees the user's data as SQL text.
```

---

### 🧪 Thought Experiment

**SCENARIO: What can an attacker extract via UNION-based SQLi?**

```
VULNERABLE ENDPOINT: GET /products?category=Electronics

Legitimate use:
  SELECT name, price FROM products WHERE category = 'Electronics'
  Returns: [{name: "TV", price: 999}...]

Attacker determines: 2 columns returned (from normal response)
  Sends: category=Electronics' UNION SELECT null,null --
  If returns normally: confirmed 2 columns, both nullable.

Attacker extracts database version:
  category=Electronics' UNION SELECT version(), null --
  Response includes: "PostgreSQL 14.2 on x86_64-pc-linux-gnu"
  Attacker now knows: PostgreSQL 14.2, Linux host.

Attacker lists all tables:
  category=Electronics' UNION SELECT table_name, null
  FROM information_schema.tables
  WHERE table_schema='public' --
  Response: products, users, orders, payment_cards, admin_users

Attacker dumps users table:
  category=Electronics' UNION SELECT username, password_hash
  FROM users --
  Response: [(admin, $2b$12$...), (user1, $2b$12$...), ...]
  With bcrypt: passwords not directly usable.
  Attacker targets weak passwords via offline cracking.

Attacker looks for payment data:
  category=Electronics' UNION SELECT card_number, cvv
  FROM payment_cards --
  If columns exist and app is not using tokenization:
  Response: full card numbers and CVVs. Immediate fraud.

WHAT PARAMETERIZED QUERY PREVENTS:
  SELECT name, price FROM products WHERE category = ?
  With value: "Electronics' UNION SELECT..."
  The entire value is treated as a string literal.
  SQL engine: WHERE category = 'Electronics'' UNION SELECT...'
  (The single quote is escaped as '' in the literal).
  Query returns: no results (no category with that exact name).
  Attack: completely blocked. No data extracted.
```

---

### 🧠 Mental Model / Analogy

> SQL injection is a "confused deputy" attack: the database
> server is the "deputy" (it executes what you tell it).
> Normally: you (the developer) tell it what to do (the query).
> With SQLi: the attacker tells it what to do (by injecting
> their commands into your instructions). The deputy cannot
> tell the difference between your commands and the attacker's
> injected commands - because they look identical to the parser.
> Parameterized queries: you hand the deputy a pre-written
> instructions template with blank spaces for values. The
> deputy fills in the blanks with the user's data - but the
> template structure is fixed and cannot be altered by the
> user's data.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SQL injection happens when a hacker types SQL commands into
a form field and the server runs those commands. For example,
typing `' OR 1=1 --` in a login box can bypass the password
check entirely. Fix: never put user input directly into SQL
queries - use "parameterized queries" that keep user data
and SQL code separate.

**Level 2 - How to use it (junior developer):**
Use your ORM (Hibernate, SQLAlchemy, Sequelize) for all
queries - they use parameterized queries by default. When
you must write raw SQL: use `cursor.execute("SELECT * FROM
users WHERE id = ?", [user_id])` - NEVER string formatting
(`f"SELECT * FROM users WHERE id = {user_id}"`). If you
see string formatting or concatenation in a SQL query: it
is almost certainly vulnerable.

**Level 3 - How it works (mid-level engineer):**
Parameterized queries work at the protocol level: the SQL
statement and the parameters are sent to the database
server as separate messages. The database pre-parses the
query template (building the execution plan), then binds
the parameter values after parsing. The parser never sees
the values as SQL text. Even a value containing SQL keywords
or special characters (`'; DROP TABLE users; --`) is treated
as a string literal during execution.

**Level 4 - Why it was designed this way (senior/staff):**
SQL injection was first publicly documented in 1998 (Jeff
Forristal, phrack.org). Twenty-six years later it remains
in the OWASP Top 10 (A03:2021). Why? Three reasons:
(1) Legacy code: applications written before parameterized
queries were standard still run in production. (2) Dynamic
queries: column names and table names cannot be parameterized
(only values can). Dynamic column selection (`ORDER BY user_input`)
requires input validation or allowlisting. (3) Bypasses through
encoded input: WAFs that filter `' OR` can be bypassed with
`%27 OR` (URL encoding) or Unicode homoglyphs. Parameterized
queries are the only complete prevention.

**Level 5 - Mastery (distinguished engineer):**
Residual SQLi risks in parameterized-query codebases:
(1) Dynamic identifiers: `ORDER BY {column}` where column
comes from user input. Cannot parameterize identifiers.
Fix: allowlist valid column names. (2) ORM raw() queries:
Django's `User.objects.raw(f"SELECT * WHERE id={id}")` -
parameterized by default EXCEPT in `.raw()` with f-strings.
(3) Stored procedures that use EXECUTE or sp_executesql with
string concatenation internally: the procedure call is
parameterized but the internal dynamic SQL is not. (4) Second-
order injection: user data is first stored in database (safely
parameterized), then later retrieved and used in a SQL query
without re-escaping. The first insert is safe; the second
use creates the injection.

---

### ⚙️ How It Works (Mechanism)

**Database execution path for both vulnerable and safe queries:**

```
VULNERABLE PATH (string concatenation):

Developer code:
  user_input = "' OR '1'='1"
  query = "SELECT * FROM users WHERE id = '" + user_input + "'"
  db.execute(query)

What the database receives as a single string:
  "SELECT * FROM users WHERE id = '' OR '1'='1'"

Database SQL parser:
  - Tokenizes the entire string as SQL syntax
  - Parses: SELECT (keyword), *, FROM (keyword),
    users (identifier), WHERE (keyword), id (identifier),
    = (operator), '' (empty string literal), OR (keyword),
    '1' (string literal), = (operator), '1' (string literal)
  - Executes: returns ALL rows (OR '1'='1' is always true)

SAFE PATH (parameterized query):

Developer code:
  user_input = "' OR '1'='1"
  query = "SELECT * FROM users WHERE id = ?"
  db.execute(query, [user_input])  # parameter sent separately

What the database receives:
  Message 1 (Parse): "SELECT * FROM users WHERE id = ?"
  Message 2 (Bind): parameters = ["' OR '1'='1"]

Database SQL parser:
  - Parses Message 1 as SQL syntax: builds execution plan
  - At parameter binding: treats the value as a string literal
  - The single quote in the value is escaped: becomes ''
  - Executes: WHERE id = ''' OR ''1''=''1'
    (looking for a row where id EQUALS the literal string)
  - Returns: 0 rows (no match)

KEY: The database receives the query structure and parameters
as SEPARATE MESSAGES. The query is fully parsed before the
parameters are bound. Parsing cannot be affected by parameter values.
```

---

### 💻 Code Example

**Complete example showing vulnerable code, fix, and edge cases:**

```python
# BAD: String concatenation (vulnerable to SQLi)
# All of these are vulnerable:

# Pattern 1: Direct concatenation
def get_user_bad(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Pattern 2: String formatting (same vulnerability)
def search_products_bad(category):
    return db.execute(
        "SELECT * FROM products WHERE category = '%s'" % category
    )

# Pattern 3: ORM with raw injection (dangerous escape hatch)
def get_users_by_role_bad(role):
    return User.objects.raw(
        f"SELECT * FROM users WHERE role = '{role}'"
    )  # Django .raw() with f-string = SQLi

# GOOD: Parameterized queries (structurally prevents SQLi)

# Pattern 1: DB-API parameterized
def get_user_safe(username):
    return db.execute(
        "SELECT * FROM users WHERE username = ?", [username]
    )

# Pattern 2: ORM (parameterized by default)
def search_products_safe(category):
    return Product.objects.filter(category=category)
    # ORM generates: WHERE category = ? with category as param

# EDGE CASE: Dynamic identifiers (column names, table names)
# These CANNOT be parameterized. Use allowlisting instead.
ALLOWED_SORT_COLUMNS = {"name", "price", "created_at", "rating"}

def get_products_sorted_safe(sort_column: str):
    if sort_column not in ALLOWED_SORT_COLUMNS:
        raise ValueError(f"Invalid sort column: {sort_column}")
    # safe: sort_column has been validated against allowlist
    # Cannot use parameter here: ORDER BY ? is not valid SQL
    return db.execute(
        f"SELECT * FROM products ORDER BY {sort_column}"
    )

# EDGE CASE: Second-order injection
# Stored data used later in a query (dangerous pattern):
def register_user(username):
    # First insert: parameterized (safe)
    db.execute("INSERT INTO users (username) VALUES (?)", [username])

def generate_report(username):
    # Second use: WRONG - retrieving stored data and using in query
    user = db.execute("SELECT username FROM users WHERE id = ?",
                      [user_id]).fetchone()
    # BUG: user.username came from DB but originally from user input
    # If user registered as: admin' UNION SELECT...
    # This query is now vulnerable to second-order SQLi
    return db.execute(
        f"SELECT * FROM logs WHERE username = '{user.username}'"
    )
    # Fix: use parameterized query for the second use too
    return db.execute(
        "SELECT * FROM logs WHERE username = ?", [user.username]
    )
```

---

### ⚖️ Comparison Table

| Prevention Method | Prevents Classic SQLi | Prevents Blind SQLi | Dynamic Identifiers | Performance |
|:---|:---|:---|:---|:---|
| **Parameterized queries** | YES | YES | No (use allowlist) | Same or better (query plan caching) |
| **ORM default** | YES | YES | Depends on raw() usage | Acceptable |
| **Input escaping** | Mostly | Mostly | No | Same | 
| **WAF** | Partially (evasion possible) | Partially | No | Adds latency |
| **Stored procedures** | Only if using parameters internally | Only if parameters | No | Same |
| **Allowlisting only** | Partial (complex rules) | Partial | YES | Same |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Input escaping/sanitization prevents SQL injection | Escaping user input (replacing `'` with `\'` or `''`) is fragile and incomplete. Bypass techniques: multi-byte character encodings where the escaping function does not handle all code points, second-order injection (data is stored escaped, then unescaped when retrieved), character set attacks (when database and application use different character sets). Parameterized queries are the ONLY complete prevention - escaping is a defense-in-depth measure, not a primary control. |
| WAFs prevent SQL injection | WAFs can block known SQLi signatures (`' OR 1=1`, `UNION SELECT`, `DROP TABLE`). But: attackers use encoding (URL encoding `%27 OR`, `%75NION`), comment variations (`/**/OR/**/1=1`), and case variations (`UnIoN SeLeCt`). A WAF provides defense-in-depth but cannot replace parameterized queries. OWASP lists WAF bypass techniques that work against every major WAF. A parameterized query bypasses 100% of WAF-evasion techniques because there is no SQL injection to bypass. |

---

### 🚨 Failure Modes & Diagnosis

**Detecting SQL injection attempts in logs:**

```python
# Pattern: Detect SQLi attempts in access logs
import re

SQLI_PATTERNS = [
    r"'\s*(OR|AND)\s+'?1'?\s*=\s*'?1",  # ' OR '1'='1
    r"UNION\s+(ALL\s+)?SELECT",           # UNION SELECT
    r";\s*(DROP|DELETE|UPDATE|INSERT)",   # ; DROP TABLE
    r"--\s*$",                             # SQL comment at end
    r"'\s*(OR|AND)\s+\d+\s*=\s*\d+",     # ' OR 1=1
    r"SLEEP\s*\(",                         # Time-based blind
    r"BENCHMARK\s*\(",                     # MySQL time-based
    r"WAITFOR\s+DELAY",                    # MSSQL time-based
    r"xp_cmdshell",                        # MSSQL command exec
    r"information_schema",                 # Schema enumeration
]

def detect_sqli_in_request(url_params: str) -> bool:
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, url_params, re.IGNORECASE):
            return True
    return False

# If DETECTED: log the attempt (IP, endpoint, payload),
# do NOT block silently (attackers know they're detected when
# they get no response - return 400 or 404 instead).
# Alert security team for investigation.
```

**Testing your own endpoints for SQLi:**
```bash
# Quick test: Does your endpoint respond differently to SQLi payload?
# If yes: potentially vulnerable.

# Normal request
curl "https://api.example.com/products?category=Electronics"
# → Returns 200 with products

# SQLi test
curl "https://api.example.com/products?category=Electronics%27"
# If 500 error: probably vulnerable (SQL syntax error from unmatched quote)
# If 200 (same as normal): likely parameterized (quote treated as literal)
# If 400: WAF or input validation caught it (good)

# For thorough testing: use SQLMap (automated SQLi detection)
# sqlmap -u "https://api.example.com/products?category=Electronics" --dbs
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10 Overview` - SQLi is A03
- `Hashing vs Encryption vs Encoding` - data handling context

**Builds on this:**
- `SQL Injection Prevention` - parameterized queries and ORM deep dive
- `SAST` - automated detection of SQLi patterns
- `Input Validation vs Output Encoding` - companion control

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CAUSE        │ User input concatenated into SQL string   │
│              │ Parser treats input as SQL syntax          │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Parameterized queries (100% effective)    │
│              │ ORM by default (usually parameterized)    │
├──────────────┼───────────────────────────────────────────┤
│ TYPES        │ In-band (UNION/error), Blind (bool/time), │
│              │ Out-of-band (DNS exfil)                   │
├──────────────┼───────────────────────────────────────────┤
│ OWASP        │ A03:2021 Injection (was #1 in 2017)       │
├──────────────┼───────────────────────────────────────────┤
│ EDGE CASES   │ Dynamic identifiers: use allowlist        │
│              │ Second-order: parameterize all uses       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "String concat = user controls SQL syntax.│
│              │  Parameters = user controls only values.  │
│              │  The second is structural prevention."    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Separate code from data at every boundary." SQL injection
violates the code/data boundary: data (user input) is treated
as code (SQL syntax). The same principle applies to: OS
command injection (`subprocess.call("ls " + user_input)` -
data treated as shell command), template injection (user
data in a template engine evaluated as code), XXE (XML entity
definitions in user data executed by XML parser). In all
cases: the fix is the same - pass data as data, never as
code. Parameterized queries for SQL, shlex.quote() for shell,
sandboxed template rendering for templates.

---

### 💡 The Surprising Truth

SQL injection was first publicly described in 1998 and is
still found in 65% of web applications tested (Acunetix 2023).
But the surprising truth: parameterized queries were available
and widely supported in every major database driver since
the mid-1990s. SQL injection has had a complete, reliable,
easy fix for nearly 30 years. The reason it persists: tutorial
code (Stack Overflow, blog posts, YouTube videos) shows string
concatenation because it is shorter and easier to explain.
New developers copy tutorial patterns. Many frameworks
encouraged raw SQL for "performance" (premature optimization).
The ecosystem created the conditions for SQL injection to
persist a generation after the fix was known. This is why
OWASP Top 10 is ranked by frequency (how often it appears
in real applications), not by novelty. Old, well-known
vulnerabilities dominate because the fix requires changing
developer habits, not just knowing the vulnerability exists.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** SQL injection in code review: any query built
   with string concatenation or string formatting where any
   part is derived from user input.
2. **EXPLAIN** why parameterized queries are structurally
   immune (query is parsed before parameters are bound - parser
   never sees user data as SQL syntax).
3. **HANDLE** edge cases: dynamic column names (allowlist),
   second-order injection (parameterize all uses of stored data).
4. **TEST** an endpoint for SQLi: send a single quote in a
   parameter and check if the response differs (500 error or
   different content = potentially vulnerable).

---

### 🎯 Interview Deep-Dive

**Q: Explain SQL injection. How do you prevent it and are
there cases where parameterized queries don't help?**

*Why they ask:* SQL injection is one of the most well-known
security vulnerabilities. Tests both knowledge depth and
practical awareness of edge cases.

*Strong answer includes:*
- Explain: user input is concatenated into SQL string; SQL
  parser treats it as SQL syntax, not data; attacker controls
  query structure.
- Prevention: parameterized queries (prepared statements).
  Query template is parsed separately from parameters.
  Even SQL syntax in a parameter is treated as a string literal.
- Where parameterized queries don't help:
  (1) Dynamic identifiers: `ORDER BY column_name` - column
      names cannot be parameterized. Fix: allowlist of valid
      column names.
  (2) Second-order injection: data is stored (safely), then
      retrieved and used in a new query without parameterization.
      Fix: always parameterize the second use too.
  (3) ORM .raw() queries with f-strings: developers use the
      "escape hatch" incorrectly. Fix: use ORM properly.
  (4) Stored procedures with internal dynamic SQL: the call
      is parameterized but the procedure builds SQL internally.
      Fix: review stored procedure code.
- Defense in depth: SAST (Semgrep detects string-format SQL),
  WAF (blocks known signatures), least privilege DB user
  (SELECT only - cannot DROP TABLE).
