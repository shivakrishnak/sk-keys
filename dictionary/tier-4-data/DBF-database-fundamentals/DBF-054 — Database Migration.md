---
layout: default
title: "Database Migration"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 54
permalink: /databases/database-migration/
id: DBF-054
category: Database Fundamentals
difficulty: ★★☆
depends_on: Schema Evolution, SQL, Transactions
used_by: CI-CD, Microservices, DevOps
related: Schema Evolution, Flyway, Liquibase
tags:
  - database
  - migrations
  - devops
  - intermediate
---

# DBF-054 — Database Migration

⚡ TL;DR — Database migration is the practice of applying versioned, tracked schema changes to a database in a controlled, repeatable way — using tools like Flyway or Liquibase to ensure every environment runs exactly the same schema version, with no manual SQL scripts and no "who ran what on prod."

| #449            | Category: Database Fundamentals     | Difficulty: ★★☆ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | Schema Evolution, SQL, Transactions |                 |
| **Used by:**    | CI-CD, Microservices, DevOps        |                 |
| **Related:**    | Schema Evolution, Flyway, Liquibase |                 |

---

### 🔥 The Problem This Solves

**WITHOUT MIGRATION TOOLING:**
Developer A runs `ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)` on production manually. Developer B doesn't know. The staging environment doesn't have the column. Deployment fails because code expects the column but staging doesn't have it. QA passes on staging, fails on production (or vice versa). "Who ran what SQL scripts on which environment?" — no one knows. Database state is undocumented tribal knowledge.

**THE SOLUTION:**
Version-control every schema change as a migration script. Migration tool tracks which scripts have been applied. Automatically applies pending migrations on startup. Every environment (dev, staging, prod) always converges to the same schema version. No manual scripts. No tribal knowledge.

---

### 📘 Textbook Definition

**Database migration** (also called **schema migration**) is the process of incrementally evolving a database schema through versioned change scripts that are tracked, audited, and automatically applied. Tools: **Flyway** (Java; `.sql` scripts named `V1__create_users.sql`; tracks applied migrations in `flyway_schema_history` table; supports Java-based callbacks); **Liquibase** (Java; XML, YAML, JSON, or SQL changesets in a `changelog` file; supports rollback with `<rollback>` tags; generates SQL preview with `updateSQL`). Spring Boot auto-runs Flyway/Liquibase on startup via `spring.flyway.enabled=true`. Key concepts: migration = a single, numbered, immutable change; checksums prevent accidental modification of applied migrations; baselines allow introducing migration tooling into an existing database.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Database migrations are to schemas what Git commits are to code — each change is versioned, tracked, and reproducible across all environments.

**One analogy:**

> Building a house with a renovation log. Every contractor who makes changes logs it: "Week 3: added a bedroom wall. Week 7: installed plumbing. Week 12: upgraded electrical panel." Anyone taking over the house can read the log and know exactly what state the house is in. A new contractor runs all the logged changes they haven't done yet on their own model house (staging environment) before touching the real house (production). No guessing; no "I thought someone already did that."

- "Renovation log" → migration script history table (`flyway_schema_history`)
- "Each contractor's change" → one migration script (`V3__add_phone_number.sql`)
- "New contractor catches up" → Flyway applies pending migrations on startup
- "Model house" → staging environment
- "Real house" → production environment
- "Logging is mandatory" → migration files are committed to Git (schema changes in version control)

**One insight:**
The core discipline: never modify an already-applied migration script. Flyway stores a checksum of each applied migration. If you edit an applied script (even to fix a typo), Flyway will detect the checksum mismatch and **refuse to run** — protecting you from the "fix it on the fly and forget" anti-pattern that destroys reproducibility.

---

### 🔩 First Principles Explanation

**FLYWAY BASICS:**

```
Convention: V{version}__{description}.sql
Examples:
  V1__initial_schema.sql
  V2__add_users_table.sql
  V3__add_phone_number_to_users.sql
  V4__create_orders_index.sql

Flyway tracks in flyway_schema_history table:
  installed_rank | version | description          | type | script                      | checksum   | installed_by | installed_on | execution_time | success
  1              | 1       | initial schema       | SQL  | V1__initial_schema.sql      | 1234567890 | myapp        | 2024-01-01   | 45ms          | true
  2              | 2       | add users table      | SQL  | V2__add_users_table.sql     | 9876543210 | myapp        | 2024-01-02   | 23ms          | true
  3              | 3       | add phone number     | SQL  | V3__add_phone_number...sql  | 5432109876 | myapp        | 2024-01-15   | 12ms          | true

On startup: Flyway scans classpath for V*.sql files, checks which aren't in history → applies them.
```

**SPRING BOOT INTEGRATION:**

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: ${DB_USER}
    password: ${DB_PASS}
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: false # true: use when adding Flyway to existing DB
    out-of-order: false # true: allow V3 to run before V4 (use with caution)
    validate-on-migrate: true # checksum validation; prevents edited migrations
```

**ZERO-DOWNTIME MIGRATION: EXPAND-CONTRACT PATTERN:**

```
Problem: ALTER TABLE users ADD COLUMN email NOT NULL causes full table lock
         Renames (ALTER TABLE RENAME COLUMN) break existing app code
         DROP COLUMN removes data referenced by older app versions
Solution: expand-contract (aka parallel-change) pattern

EXPAND PHASE (deploy new schema, keep old working):
  Migration: ALTER TABLE users ADD COLUMN email_new VARCHAR(255);
  App v1: writes to email_old only; email_new nullable so no failures
  App v2: writes to BOTH email_old AND email_new (dual-write)

CONTRACT PHASE (after all app versions use new column):
  Migration: run backfill: UPDATE users SET email_new = email_old WHERE email_new IS NULL
  Make email_new NOT NULL (after backfill)
  Remove email_old from app code
  Final migration: ALTER TABLE users DROP COLUMN email_old

RESULT: schema migrated with zero downtime; no app-schema incompatibility window
```

**LIQUIBASE ROLLBACK:**

```xml
<!-- changelog.xml (Liquibase) -->
<databaseChangeLog>
  <changeSet id="3" author="dev">
    <addColumn tableName="users">
      <column name="phone_number" type="VARCHAR(20)"/>
    </addColumn>
    <rollback>
      <!-- Explicit rollback: what to do if rollback command is run -->
      <dropColumn tableName="users" columnName="phone_number"/>
    </rollback>
  </changeSet>
</databaseChangeLog>
```

```bash
# Liquibase CLI: preview SQL before applying
liquibase updateSQL  # shows what SQL would be run; doesn't execute

# Apply migrations
liquibase update

# Rollback last 1 change
liquibase rollbackCount 1

# Rollback to specific tag
liquibase rollback my-tag
```

**CI/CD INTEGRATION:**

```
Git push → CI pipeline:
  1. Run tests (application + migrations applied to test DB in Docker container)
  2. Deploy to staging → Flyway auto-migrates staging DB on app startup
  3. Run integration tests on staging
  4. Deploy to prod → Flyway auto-migrates prod DB on app startup
  5. Production migration is automatic and tracked

Key principle: migrations run BEFORE app traffic (during deploy, not during request handling)
Blue-green deployments:
  Blue (old version) → still running
  Green (new version) → starts up → Flyway runs migration on shared DB
  Problem: if migration is destructive (DROP COLUMN), Blue app breaks
  Solution: expand-contract → migration is always backward compatible
```

---

### 🧪 Thought Experiment

**SCENARIO: Renaming a Column in Production**

You want to rename `users.username` to `users.display_name`. Bad approach:

```sql
-- V5__rename_username.sql
ALTER TABLE users RENAME COLUMN username TO display_name;
```

**WHAT HAPPENS DURING DEPLOYMENT:**

- Deploy: Flyway runs V5 → column renamed
- Old app version (still running during blue-green): `SELECT username FROM users` → ERROR: column "username" does not exist
- For the seconds/minutes between migration and full cutover: the old app is broken
- User-facing errors during deployment

**CORRECT APPROACH (Expand-Contract):**

```sql
-- V5__add_display_name.sql (EXPAND)
ALTER TABLE users ADD COLUMN display_name VARCHAR(255);
UPDATE users SET display_name = username;
-- App v2 deployed: reads display_name, writes both username + display_name
```

```sql
-- V6__backfill_display_name.sql (after all instances use v2)
UPDATE users SET display_name = username WHERE display_name IS NULL;
ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
-- App v3 deployed: reads/writes only display_name
```

```sql
-- V7__drop_username.sql (CONTRACT, after v3 fully deployed)
ALTER TABLE users DROP COLUMN username;
```

Three migration files. Three deployment cycles. Zero downtime. Always backward compatible.

---

### 🧠 Mental Model / Analogy

> Database migrations are like version control for your database schema — the same way Git tracks every code change with a commit hash and message, Flyway tracks every schema change with a version number, checksum, and timestamp. Just as you'd never directly edit a committed Git commit to fix it (you create a new commit), you never edit an applied migration (you create a new migration to fix the mistake). Just as everyone on the team clones the repo and gets the same code history, every environment runs the same migration history and converges to the same schema.

- "Git commit" → migration file (immutable once applied)
- "Commit hash" → migration checksum (detects tampering)
- "git log" → `flyway_schema_history` table
- "git apply / git pull" → Flyway running pending migrations
- "Create a new commit to fix" → create a new migration (V4) to fix V3's mistake
- "Everyone clones the repo" → all environments run the same migrations

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Every database change is written as a SQL file with a version number. When the app starts, Flyway checks which files haven't been run on this database yet and runs them in order. Every environment (dev, staging, prod) automatically gets the same database changes. No more "did you run that SQL on prod?"

**Level 2:** Use expand-contract for zero-downtime migrations: add new columns before removing old ones, never rename columns directly. Write every migration to be backward compatible with the currently deployed app version. Store migration files in `src/main/resources/db/migration/`. Never modify a migration file after it's been committed to Git. Use `flyway:validate` in CI to catch accidental edits.

**Level 3:** Performance considerations: large `ALTER TABLE` statements can lock production tables. PostgreSQL's `ADD COLUMN` with a default: before PG 11, rewrites the entire table (O(n)); PG 11+ stores the default separately (O(1)) for non-volatile defaults. For large tables (>100M rows), use `pg_repack` or add the column without a default first, then backfill in batches (`UPDATE ... WHERE id BETWEEN x AND y`), then add the NOT NULL constraint using PostgreSQL 12+'s `NOT VALID` → `VALIDATE CONSTRAINT` pattern (validates in background without full lock). Flyway callbacks (`beforeMigrate.sql`, `afterEachMigrate.sql`) allow pre/post-migration operations (e.g., disabling triggers before a large backfill, re-enabling after).

**Level 4:** The migration framework's checksum protection is a determinism guarantee: the schema at any database is the composition of all applied migrations in sequence. Because each migration's SQL is hashed and the hash is stored, the system can verify that `DB at version N` is identical regardless of which environment or when it was set up. This is the database equivalent of hermetic builds in software (reproducible, environment-independent output). The expand-contract pattern is a formalization of the Postel's Law principle applied to schema evolution: be conservative in what you produce (new schema), be liberal in what you accept (continue accepting old app queries). During the expansion phase, the schema accepts both old and new app query patterns. During the contraction phase (after all apps are updated), the schema removes the old compatibility surface.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ FLYWAY MIGRATION LIFECYCLE                               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  App starts                                             │
│     ↓                                                   │
│  Flyway.migrate()                                       │
│     ↓                                                   │
│  Scan classpath/filesystem for V*.sql files             │
│     ↓                                                   │
│  Read flyway_schema_history table                       │
│  (or create it if first run)                            │
│     ↓                                                   │
│  For each V*.sql file (sorted by version):              │
│    Already in history?                                  │
│      YES: validate checksum matches → if mismatch: FAIL │
│      NO:  this is a pending migration                   │
│     ↓                                                   │
│  Apply pending migrations in order (within transaction) │
│  Record in flyway_schema_history (version, checksum, ts)│
│     ↓                                                   │
│  App finishes startup → serves traffic                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**CI/CD MIGRATION FLOW:**

```
Developer:
  CREATE V5__add_email_to_users.sql:
    ALTER TABLE users ADD COLUMN email VARCHAR(255);
  git commit + push

CI Pipeline:
  → Start fresh PostgreSQL container
  → Run Flyway V1→V5 migrations on it
  → [DATABASE MIGRATION ← YOU ARE HERE: automated application]
  → Run all tests (schema verified at V5)
  → Build Docker image

Deploy to Staging:
  → New app container starts
  → Flyway: staging DB is at V4
  → Flyway: runs V5__add_email_to_users.sql
  → App serves traffic (now at V5)

Deploy to Production:
  → Same process: Flyway runs V5 on prod
  → All environments now at V5
  → Zero manual intervention
```

---

### ⚖️ Comparison Table

| Feature        | Flyway                               | Liquibase                        | Manual SQL Scripts |
| -------------- | ------------------------------------ | -------------------------------- | ------------------ |
| Format         | SQL only (or Java)                   | SQL, XML, YAML, JSON             | SQL                |
| Rollback       | Not built-in (create undo migration) | Built-in `<rollback>` tags       | Manual             |
| Preview        | `flyway info`                        | `liquibase updateSQL`            | None               |
| Spring Boot    | Auto-configured                      | Auto-configured                  | Manual             |
| Learning curve | Low (just SQL)                       | Medium (XML/YAML format)         | None               |
| Audit trail    | `flyway_schema_history` table        | `databasechangelog` table        | None               |
| Best for       | Simple schemas, SQL-fluent teams     | Complex rollback needs, multi-DB | Never (avoid)      |

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                  |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| You can edit a migration file to fix a typo                                | Never edit applied migrations — Flyway checksum will fail. Create a new migration (V5) that corrects the issue from V4                                                                                                   |
| Rollback is always possible with Flyway                                    | Flyway doesn't natively support rollback (unlike Liquibase). For destructive changes, the "undo migration" must be written manually. The expand-contract pattern avoids needing rollback                                 |
| Migrations run in parallel (one per service instance)                      | Flyway uses a database lock (`flyway_schema_history` table lock) to ensure only one instance runs migrations at startup — concurrent deployments queue safely                                                            |
| Large ALTER TABLE migrations are safe to run on prod during business hours | For tables with millions of rows, ALTER TABLE can hold locks for minutes, blocking all reads/writes. Run large migrations during off-peak, or use non-locking alternatives (ADD COLUMN DEFAULT in PG11+, batched UPDATE) |

---

### 🚨 Failure Modes & Diagnosis

**1. Failed Migration Leaves Database in Partially Applied State**

**Symptom:** App fails to start. Flyway error: `Migration V7 failed! Please restore backups and fix the migration script`. Half of V7's SQL ran before the failure.

**Root Cause:** V7's SQL errored partway through (e.g., a constraint violation on an `ALTER TABLE`). Flyway records V7 as failed in `flyway_schema_history` (success=false). On next startup, Flyway sees the failed migration and refuses to proceed.

**Diagnostic:**

```sql
SELECT * FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;
-- Look for success = false
```

**Fix:**

```sql
-- Option 1: Manual fix — undo the partial migration manually, then remove the failed entry
-- Manually run the inverse SQL (DROP column, etc.)
DELETE FROM flyway_schema_history WHERE version = '7' AND success = false;
-- Fix V7__migration.sql
-- Restart app — Flyway re-applies V7

-- Option 2: If migration was transactional (PostgreSQL wraps DDL in transactions):
-- PostgreSQL will have rolled back the partial migration automatically
-- Just remove the failed record + fix the script
```

**Prevention:** Write migrations to be idempotent where possible (`CREATE INDEX IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`). Test migrations on a production-sized dataset in staging. For large tables, use batched migrations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SQL` — migrations are SQL statements; must understand DDL (ALTER TABLE, CREATE INDEX)
- `Transactions` — migrations run in transactions (in PostgreSQL, DDL is transactional)
- `Schema Evolution` — migration is the tooling for managing schema evolution

**Builds On This (learn these next):**

- `Schema Evolution` — the higher-level practice; migration is the mechanism
- `CI-CD` — migrations integrated into deployment pipelines
- `Microservices` — each microservice owns and manages its own DB migrations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOOLS        │ Flyway (SQL-first), Liquibase (XML/YAML)  │
│              │ Spring Boot: auto-configured              │
├──────────────┼───────────────────────────────────────────┤
│ FILE NAMING  │ V{version}__{description}.sql             │
│              │ V1__create_users.sql (immutable once run) │
├──────────────┼───────────────────────────────────────────┤
│ TRACKING     │ flyway_schema_history table               │
│              │ version, checksum, success, timestamp     │
├──────────────┼───────────────────────────────────────────┤
│ ZERO-DOWNTIME│ Expand-contract pattern:                  │
│              │ Add new → dual-write → backfill → remove  │
├──────────────┼───────────────────────────────────────────┤
│ NEVER DO     │ Edit applied migration files              │
│              │ Run DDL manually on prod                  │
│              │ DROP/RENAME without backward compat phase │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Git for your database schema —           │
│              │  every change versioned, tracked, tested" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Schema Evolution (broader practice)       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) You're adding database migrations to a microservices system with 5 services, each with its own database. Service A's migration depends on Service B completing its migration first (shared reference data). How do you handle migration ordering across services? What happens if Service A deploys before Service B? Should cross-service migration dependencies even exist? What architectural refactoring would eliminate this coupling?

**Q2.** (TYPE D — Failure Scenario) Your Spring Boot app starts deploying to production. Flyway begins running V10\_\_add_order_total_index.sql — `CREATE INDEX CONCURRENTLY idx_orders_total ON orders(total_amount)`. 30 seconds into the migration, you notice the app health check is failing and Kubernetes is killing the pod (restart). What happens to the migration? Does `CREATE INDEX CONCURRENTLY` leave the index in a broken state? How does Flyway handle this? What should you do? What should you add to V11 to handle this scenario?
