---
layout: default
title: "Flyway"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /databases/flyway/
id: DBF-010
category: Database Fundamentals
difficulty: ★★★
depends_on: Database Change Management, SQL, JDBC
used_by: CI-CD, Spring Boot, Database Fundamentals
related: Liquibase, Database Change Management, Schema Design Best Practices
tags:
  - database
  - devops
  - advanced
  - cicd
---

# DBF-010 — Flyway

⚡ TL;DR — Flyway applies versioned SQL migration scripts in strict order, tracking which scripts have run in a `flyway_schema_history` table so each script executes exactly once per database.

| Field        | Value |
|--------------|-------|
| Depends on   | Database Change Management, SQL, JDBC |
| Used by      | CI-CD, Spring Boot, Database Fundamentals |
| Related      | Liquibase, Database Change Management, Schema Design Best Practices |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A startup has five developers. Each creates their own local SQL scripts. On Monday, developer A drops a column. On Tuesday, developer B adds an index on that column. In staging, both scripts run — but B's runs first because of alphabetical file naming. The deployment fails silently. Production has a different schema than staging because no one tracked which scripts ran where.

**THE BREAKING POINT:** Without a migration history table, there is no reliable answer to "what is the current schema state of this database?" Manual runbooks, sticky notes, and tribal knowledge fill the gap — until they don't.

**THE INVENTION MOMENT:** Axel Fontaine created Flyway in 2010 with a radical simplicity principle: migration files are plain SQL, named with a version number prefix (`V1__`, `V2__`), applied in strict order, and recorded in a history table. No XML. No YAML. Just SQL and a naming convention.

---

### 📘 Textbook Definition

**Flyway** is an open-source database migration tool that applies versioned SQL (or Java-based) migration scripts in strict version order. It maintains a `flyway_schema_history` table (formerly `schema_version`) recording each applied migration's version, description, checksum, execution timestamp, and success status. Migrations are classified as **versioned** (`V<version>__<description>.sql`), **repeatable** (`R__<description>.sql`, re-run when content changes), or **undo** (`U<version>__<description>.sql`, Pro only). Flyway enforces linear version ordering and prevents out-of-order application by default.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Flyway applies numbered SQL files in order, exactly once each, tracking state in a history table — simple enough to understand in five minutes.

> Think of Flyway as a construction project punch list. Each task (SQL script) is numbered, assigned to a day (version), and checked off when complete. A new site (database) starts from scratch and works through every unchecked item. A resumed site picks up where it left off.

**One insight:** Flyway's power is its simplicity: migrations are plain SQL files, version-controlled with your application code, applied automatically on startup. The naming convention IS the API.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Migrations are applied in strict ascending version order; Flyway will never apply `V3` before `V2`.
2. Applied migrations are checksummed; any modification to an applied migration script causes a checksum failure.
3. Each migration runs in a database transaction (if the database supports transactional DDL); failure rolls back the migration and records it as failed in history.
4. Repeatable migrations (`R__`) run every time their checksum changes; they are applied after all versioned migrations.

**DERIVED DESIGN:**
- Versioned migrations: `V<version>__<description>.sql` — the primary migration type for schema changes.
- Repeatable migrations: `R__<description>.sql` — ideal for views, stored procedures, and functions that should always reflect the latest file content.
- `flyway_schema_history`: the authoritative state table; never manually modify this.
- `baseline`: marks an existing database at a specific version so Flyway can manage it going forward.

**THE TRADE-OFFS:**

**Gain:** Zero learning curve for SQL developers; plain SQL is database-native; version numbering makes ordering unambiguous; Spring Boot auto-configures Flyway with zero extra code.

**Cost:** Versioned migrations are append-only — you cannot fix an applied migration by editing it; out-of-order migration from parallel branches is not supported by default (requires `outOfOrder=true`); rollback requires manual SQL in Community edition; complex conditional logic requires Java-based migrations.

---

### 🧪 Thought Experiment

**SETUP:** Two developers work on separate feature branches. Developer A adds column `email_verified` (V5). Developer B adds column `phone_number` (also V5). Both merge to main.

**WITHOUT FLYWAY:** Both SQL scripts are run in whatever order they appear in the deployment. If both create a `V5` file, the second one fails silently or overrides the first. The result is unpredictable.

**WITH FLYWAY:** Flyway detects a checksum mismatch between the applied V5 and the new V5 file from the merged branch. It refuses to proceed and throws an error: `Migration checksum mismatch for migration version 5`. The conflict is caught in CI, before production.

**THE INSIGHT:** Flyway's versioning scheme enforces the same discipline as Git branch merging: conflicts are detected and must be resolved, not silently overwritten.

---

### 🧠 Mental Model / Analogy

> Flyway is like a stamp-collecting album with numbered slots. Each SQL script is a stamp for a specific slot. Stamps are inserted in order. Once a stamp is in its slot, you cannot replace it (checksum lock). If you want to correct a mistake in slot 5, you don't remove stamp 5 — you add a correction stamp in slot 6.

- **Album** = database schema over time
- **Numbered slot** = version number (`V5`, `V6`)
- **Stamp** = SQL migration script
- **Glue in the slot** = checksum (locks the stamp in place)
- **Album history page** = `flyway_schema_history` table
- **Correction stamp** = new versioned migration to fix a mistake

Where this analogy breaks down: Stamps can't reference each other. SQL migrations can — and must — be written with an understanding of the schema state left by all previous migrations.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Flyway is a tool that runs your SQL files in numbered order. Each file runs exactly once per database. If you need a new change, you add a new numbered file.

**Level 2 — How to use it (junior developer):**
Create `src/main/resources/db/migration/V1__Create_customers.sql`. Add `spring.flyway.enabled=true` to `application.yml`. On startup, Flyway runs V1 and records it. Add `V2__Add_loyalty_tier.sql` later — on next startup, V2 runs automatically.

**Level 3 — How it works (mid-level engineer):**
On startup, Flyway scans the configured locations for migration files, resolves them by version, and queries `flyway_schema_history` for already-applied versions. It computes a CRC32 checksum of each pending migration file and verifies applied migrations' checksums haven't changed. Pending migrations execute in a transaction where supported. Repeatable migrations are re-run if their checksum differs from the recorded checksum. `flyway.baselineOnMigrate=true` creates the history table and baselines an existing database at a specified version.

**Level 4 — Why it was designed this way (senior/staff):**
Flyway's design philosophy is "convention over configuration." The version number in the filename IS the ordering — no configuration file needed. This design trades flexibility (no conditional logic, no rollback in Community) for reliability and zero onboarding friction. The choice to use plain SQL as the primary format was deliberate: SQL is the universal language of database engineers, and database-agnostic XML abstractions introduce bugs when they miss database-specific syntax. The checksum scheme (CRC32 of file contents) detects accidental modification — protecting production from "quick fixes" that were applied to a script after deployment.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│           Flyway Migration Flow             │
│                                             │
│  Scan locations for V*.sql, R*.sql files    │
│    │                                        │
│    ▼                                        │
│  Sort versioned migrations by version       │
│    │                                        │
│    ▼                                        │
│  Query flyway_schema_history                │
│    │                                        │
│    ▼                                        │
│  For each pending migration:                │
│    ├── Begin transaction                    │
│    ├── Execute SQL                          │
│    ├── Record in flyway_schema_history      │
│    └── Commit (or rollback on failure)      │
│    │                                        │
│  Apply repeatable migrations (R__):         │
│    └── Re-run if checksum changed           │
└─────────────────────────────────────────────┘
```

**Naming convention:**
```
Versioned:   V{version}__{description}.sql
             V1__Create_customers_table.sql
             V2.1__Add_loyalty_tier.sql

Repeatable:  R__{description}.sql
             R__Create_views.sql

Undo (Pro):  U{version}__{description}.sql
             U2.1__Undo_add_loyalty_tier.sql
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes V5__Add_email_verified.sql
  │
  ▼
Commits to source control (PR + code review)
  │
  ▼
CI pipeline triggers app build
  │
  ▼
Spring Boot starts → Flyway.migrate() called
       ← YOU ARE HERE
  │
  ▼
flyway_schema_history consulted:
  V1–V4 already applied, checksums OK
  V5 pending → execute SQL → record
  │
  ▼
Application proceeds with updated schema
```

**FAILURE PATH:**
- **Checksum mismatch:** `ERROR: Migration checksum mismatch for migration version 5` → migration file was edited after being applied. Never edit applied files.
- **Failed migration in history:** If a migration fails mid-execution (non-transactional DB), it is recorded with `success=false`. Flyway will not proceed. Fix requires manual repair (`flyway repair`) or database rollback.
- **Out-of-order migration:** `V4` appears after `V5` was applied. Flyway detects this and fails unless `outOfOrder=true` is configured.

**WHAT CHANGES AT SCALE:**
- Microservices with per-service databases: each service ships its own `db/migration/` folder; Flyway is independent per service.
- Large teams: version number conflicts on parallel branches are caught in CI when branch A's `V10` and branch B's `V10` are both present after merge.
- Zero-downtime deployments: migrations must be backward-compatible (additive). Use `flyway.outOfOrder=false` to enforce linear history.

---

### 💻 Code Example

**Directory structure:**
```
src/main/resources/
  db/migration/
    V1__Create_customers.sql
    V2__Create_orders.sql
    V3__Add_customer_region.sql
    V4__Create_indexes.sql
    V5__Add_loyalty_tier.sql
    R__Create_customer_summary_view.sql
```

**V5 migration script:**
```sql
-- V5__Add_loyalty_tier.sql
-- BAD: no default value; fails NOT NULL on populated table
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(20) NOT NULL;
```

```sql
-- V5__Add_loyalty_tier.sql
-- GOOD: nullable first; backfill; add constraint later
ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(20);

UPDATE customers
SET loyalty_tier = 'STANDARD'
WHERE loyalty_tier IS NULL;
```

**V6 — add NOT NULL constraint after backfill:**
```sql
-- V6__Make_loyalty_tier_not_null.sql
ALTER TABLE customers
ALTER COLUMN loyalty_tier SET NOT NULL;
```

**Repeatable migration for view:**
```sql
-- R__Create_customer_summary_view.sql
-- Runs whenever this file changes
CREATE OR REPLACE VIEW customer_summary AS
SELECT c.id,
       c.name,
       c.loyalty_tier,
       COUNT(o.id) AS order_count,
       SUM(o.amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name, c.loyalty_tier;
```

**Spring Boot configuration (`application.yml`):**
```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: false
    out-of-order: false
    validate-on-migrate: true
    table: flyway_schema_history
```

**Flyway CLI commands:**
```bash
# Apply pending migrations
flyway migrate

# Check current migration state
flyway info

# Validate checksums without migrating
flyway validate

# Repair failed migration record
flyway repair

# Baseline existing database at version 5
flyway baseline -baselineVersion=5 \
  -baselineDescription="Baseline from legacy"

# Clean (DROP ALL — NEVER in production)
flyway clean
```

**Checking migration state in SQL:**
```sql
-- View migration history
SELECT version, description, type,
       installed_on, success, execution_time
FROM flyway_schema_history
ORDER BY installed_rank;
```

---

### ⚖️ Comparison Table

| Feature | Flyway Community | Flyway Pro | Liquibase Community |
|---|---|---|---|
| Migration format | SQL, Java | SQL, Java | XML, YAML, JSON, SQL |
| Rollback/undo | Manual SQL only | Undo migrations | `<rollback>` blocks |
| Repeatable migrations | Yes | Yes | `runOnChange="true"` |
| Dry run (preview SQL) | No | Yes | `updateSQL` command |
| Baseline existing DB | Yes | Yes | `changeLogSync` |
| Out-of-order support | Yes (flag) | Yes (flag) | Yes (always by design) |
| DB-agnostic DDL | No | No | Yes (change types) |
| Preconditions | No | No | Yes |
| Multi-schema support | Basic | Advanced | Yes |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "I can edit a migration to fix a typo after deployment" | Flyway checksums every applied migration. Editing it causes `ERROR: Migration checksum mismatch`. Always add a new migration (V{n+1}) to correct mistakes. |
| "`flyway clean` is a useful reset tool in production" | `flyway clean` drops ALL objects in the schema. It is intended for local development only. Running it in production destroys all data. Most teams disable it with `cleanDisabled=true`. |
| "Repeatable migrations run every time on startup" | Repeatable migrations run only when their checksum changes (i.e., the file content changes). If unchanged, they are skipped. |
| "Flyway handles rollback automatically" | Community edition has no automatic rollback. If a migration fails on a DB without transactional DDL (MySQL, Oracle), the partial change remains. Manual intervention is required. |
| "Version numbers must be integers" | Flyway supports dot notation: `V1.1`, `V2.3.1`, `V20240601`. This allows sub-versioning for hotfixes between major releases. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Failed Migration Blocks All Subsequent Deployments**

**Symptom:** Application cannot start. Logs show `Flyway: Found failed migration in flyway_schema_history`. All subsequent deployments also fail.

**Root Cause:** A migration failed mid-execution on a database that does not support transactional DDL (e.g., MySQL for some DDL statements). Flyway records the failure and refuses to proceed.

**Diagnostic:**
```sql
-- Find failed migrations
SELECT version, description, success, installed_on
FROM flyway_schema_history
WHERE success = 0;
```

**Fix:**
```bash
# Step 1: manually undo the partial change in the DB
-- (write the inverse SQL manually)

# Step 2: remove the failed record from history
DELETE FROM flyway_schema_history
WHERE version = '5' AND success = 0;

# Step 3: repair the history table
flyway repair

# Step 4: re-run the migration (after fixing the script)
flyway migrate
```

**Prevention:** Use transactional databases (PostgreSQL, SQL Server) where possible. Test migrations in a production-equivalent environment before deploying.

---

**Mode 2: Version Number Conflict from Parallel Branches**

**Symptom:** CI fails with `ERROR: Found more than one migration with version 7`.

**Root Cause:** Two developers on parallel feature branches both created `V7__*.sql`. Both branches merged to main. Flyway finds two files claiming version 7.

**Diagnostic:**
```bash
flyway info
# Shows: ERROR - Two resolved migrations have the same version: 7
```

**Fix:** Rename one migration to `V8__*.sql`. Update the other branch's reference if dependent. Communicate with the team about version allocation.

**Prevention:** Use a version number strategy based on timestamp or ticket number (`V20240601001__`, `V20240601002__`) rather than simple sequential integers. Reduces collision probability to near zero.

---

**Mode 3: Baseline Confusion on Existing Databases**

**Symptom:** Flyway fails on an existing database: `ERROR: Found non-empty schema without Flyway metadata table`. The database has tables but no `flyway_schema_history`.

**Root Cause:** Flyway was added to a project after the database already existed. Flyway sees a non-empty schema with no migration history and refuses to proceed.

**Diagnostic:**
```bash
flyway info
# ERROR: Found non-empty schema(s) "public" but no
# schema history table. Use baseline() or set
# baselineOnMigrate to true to initialize the schema
# history table.
```

**Fix:**
```bash
# Mark the current state as the baseline
flyway baseline -baselineVersion=1 \
  -baselineDescription="Initial existing schema"
# Then add V2, V3... for future changes
```

**Prevention:** Add Flyway from the start of any new project. For existing projects, create a baseline script (`V1__baseline.sql`) that reflects the current schema, baseline the existing databases, and add new migrations from V2 onward.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Database Change Management — the practice Flyway implements
- SQL — Flyway's primary migration language
- JDBC — the connection mechanism Flyway uses

**Builds On This (learn these next):**
- CI/CD — Flyway fits into pipelines as a pre-deployment step
- Spring Boot — auto-configures Flyway migrations at application startup
- Schema Design Best Practices — designing backward-compatible schema changes

**Alternatives / Comparisons:**
- Liquibase — more feature-rich alternative with XML/YAML/JSON support and rollback
- Database Change Management — the broader concept
- Schema Evolution — theory of evolving schemas over the application lifecycle

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════╗
║ WHAT IT IS     SQL-first DB migration tool  ║
║ PROBLEM SOLVED Schema drift; double-apply;  ║
║                "which scripts ran here?"    ║
║ KEY INSIGHT    Filename IS the version;     ║
║                checksum IS the lock         ║
║ USE WHEN       SQL-first teams; Spring Boot;║
║                simple linear history needed ║
║ AVOID WHEN     Complex rollback required;   ║
║                multi-database conditional   ║
║                logic needed (use Liquibase) ║
║ TRADE-OFF      Simplicity vs rollback and   ║
║                precondition support         ║
║ ONE-LINER      Never edit; always add V{n+1}║
║ NEXT EXPLORE   Liquibase, expand-contract   ║
╚══════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(C — Design Trade-off)** Flyway uses sequential version numbers for ordering, which makes conflicts explicit but requires coordination in team environments. Liquibase uses an `(id, author, file)` triple, which allows independent authoring but makes ordering less obvious. In a team of 20 developers all working on separate feature branches, which approach scales better — and what tooling or convention would you add to the weaker approach to mitigate its drawback?

2. **(A — System Interaction)** A Spring Boot application has `spring.flyway.enabled=true`. The application runs in Kubernetes with 3 replicas. All 3 pods start simultaneously. Describe the exact sequence of events at the database level, including locking, and whether data corruption is possible.

3. **(B — Scale)** You are migrating a 2TB PostgreSQL database. `V15__Add_index_on_orders_customer_id.sql` contains `CREATE INDEX CONCURRENTLY idx_orders_cust ON orders(customer_id)`. Flyway wraps each migration in a transaction. What conflict does this create, and how do you resolve it while keeping the migration tracked in Flyway?
