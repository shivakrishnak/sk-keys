---
layout: default
title: "Liquibase"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /databases/liquibase/
id: DBF-009
category: Database Fundamentals
difficulty: ★★★
depends_on: Database Change Management, SQL, JDBC
used_by: CI-CD, Spring Boot, Database Fundamentals
related: Flyway, Database Change Management, Schema Design Best Practices
tags:
  - database
  - devops
  - advanced
  - cicd
---

# DBF-009 - Liquibase

⚡ TL;DR - Liquibase tracks, versions, and applies database schema changes via XML/YAML/SQL changesets, enabling repeatable, audited, and rollback-capable database migrations.

| Field        | Value |
|--------------|-------|
| Depends on   | Database Change Management, SQL, JDBC |
| Used by      | CI-CD, Spring Boot, Database Fundamentals |
| Related      | Flyway, Database Change Management, Schema Design Best Practices |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Teams deploy application code updates and then manually run SQL scripts against each environment. Scripts run out of order, get applied twice, or are forgotten entirely. One DBA runs a column rename in staging; no one documents it; production breaks two weeks later during deployment.

**THE BREAKING POINT:** A release involves 12 SQL change scripts. In staging, script 7 fails due to a constraint violation. It is manually fixed and re-run. In production, the fixed version is applied but script 8 was accidentally skipped. The production database is now in an undocumented state that no one can reproduce.

**THE INVENTION MOMENT:** Nathan Voxland created Liquibase in 2006 to solve exactly this: database changes tracked in source control, with a checksum-verified history table preventing double-application, and rollback logic specified alongside each change.

---

### 📘 Textbook Definition

**Liquibase** is an open-source database schema change management tool. It processes a **changelog** (XML, YAML, JSON, or SQL file) containing ordered **changesets** - each uniquely identified by `id` + `author` + `file`. Liquibase maintains a `DATABASECHANGELOG` table in the target database recording every applied changeset with its MD5 checksum. It applies only changesets not yet recorded, making schema deployment idempotent and auditable. Changes can include rollback instructions, preconditions, and context/label filtering for environment-specific deployment.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Liquibase is `git` for your database schema - every change is tracked, versioned, and reproducible.

> Imagine a recipe book where each page (changeset) records exactly what was added to the pot and in what order, and a chef's log (DATABASECHANGELOG table) records which pages have been cooked. A new kitchen only cooks unchecked pages - never the same page twice.

**One insight:** The `DATABASECHANGELOG` table IS the migration state. If you manually modify the database outside Liquibase, the table won't reflect it - and Liquibase will either skip the change or fail a checksum validation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every changeset is identified by a unique `(id, author, filename)` triple - not by sequence number.
2. A changeset is applied exactly once per database (tracked by `DATABASECHANGELOG`).
3. Liquibase computes an MD5 checksum of each applied changeset; if the changeset is later modified, Liquibase detects the mismatch and refuses to run (protecting against silent drift).
4. Rollback must be specified explicitly (except for simple DDL that Liquibase can auto-generate).

**DERIVED DESIGN:**
- `databaseChangeLog` → top-level container (include files, define preconditions).
- `changeSet` → atomic unit of change (one or more `change` tags or `sql` blocks).
- `rollback` → SQL/change tags to undo the changeset.
- `preconditions` → guard conditions (`tableExists`, `columnExists`, etc.) before applying.
- `contexts` and `labels` → filter which changesets apply to which environments.

**THE TRADE-OFFS:**

**Gain:** Declarative, database-agnostic change definitions; full audit trail; rollback instructions co-located with change; CI/CD integration via Maven/Gradle plugin or CLI.

**Cost:** Changesets are immutable once applied (modifying applied changesets breaks checksums); XML/YAML abstraction adds verbosity; complex multi-step rollbacks require careful manual authoring; no support for purely procedural DDL across all databases.

---

### 🧪 Thought Experiment

**SETUP:** You have five environments (dev, test, staging, uat, production). A feature requires adding a `loyalty_tier` column to the `customers` table.

**WITHOUT LIQUIBASE:** Each developer runs the ALTER TABLE manually in dev. The DBA runs it in staging on a different day. UAT is forgotten. Production deployment: "Which SQL script do I run? Was it applied to test already?"

**WITH LIQUIBASE:**
```xml
<changeSet id="2024-06-01-add-loyalty-tier"
           author="dev-team">
  <addColumn tableName="customers">
    <column name="loyalty_tier" type="VARCHAR(20)"
            defaultValue="STANDARD"/>
  </addColumn>
  <rollback>
    <dropColumn tableName="customers"
                columnName="loyalty_tier"/>
  </rollback>
</changeSet>
```
Every environment runs `liquibase update`. Liquibase checks `DATABASECHANGELOG` - applies only where it hasn't been applied. Idempotent across all five environments.

**THE INSIGHT:** The changelog is the single source of truth for the database schema's evolution - checked into source control alongside application code.

---

### 🧠 Mental Model / Analogy

> Liquibase is like a notarized legal ledger for a property. Every modification to the property (schema change) is recorded as a notarized entry (changeset) with a unique reference number, date, and the notary's signature (checksum). A new owner of the property (new environment) receives a copy of the ledger and can reconstruct the exact state of the property by executing every entry in order. No entry is ever executed twice.

- **Property** = database schema
- **Notarized entry** = changeset (id + author + checksum)
- **Ledger** = `DATABASECHANGELOG` table
- **New owner catching up** = `liquibase update` on a new environment
- **Property modification outside ledger** = manual DDL (causes drift)

Where this analogy breaks down: Legal ledgers are append-only by law. Liquibase technically allows `clearCheckSums` to reset checksums - though this is strongly discouraged in production.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Liquibase keeps a list of database changes in a file (like a changelog). It makes sure each change is applied exactly once to each database, so every environment has the same structure.

**Level 2 - How to use it (junior developer):**
Add a changeset to `db/changelog/changes/001-add-loyalty-tier.xml`. Include it in `db/changelog/root.xml`. Run `liquibase update`. The `DATABASECHANGELOG` table is updated. Next `liquibase update` skips it because the checksum matches. Add `<rollback>` tags to support `liquibase rollbackCount 1`.

**Level 3 - How it works (mid-level engineer):**
Liquibase reads the changelog, builds an ordered list of changesets. For each changeset, it computes an MD5 hash of the change content. It queries `DATABASECHANGELOG` for already-applied changesets. Unmatched changesets are executed in a database transaction (if the DB supports transactional DDL). The `DATABASECHANGELOGLOCK` table provides a distributed lock - only one Liquibase process runs at a time per database. Preconditions are evaluated before each changeset; failure modes are configurable (`HALT`, `WARN`, `MARK_RAN`).

**Level 4 - Why it was designed this way (senior/staff):**
Liquibase chose the `(id, author, filename)` triple rather than sequential version numbers because sequential numbering breaks in team environments: two developers adding migration #12 creates a conflict. The triple allows merging without renaming. The checksum mechanism was added to prevent silent drift - a common source of production incidents. The choice to support XML/YAML/JSON/SQL formats reflects the reality that teams have different levels of SQL expertise and that database-agnostic DDL (via Liquibase's change types) trades portability for reduced control.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│         Liquibase Update Flow               │
│                                             │
│  root.changelog.xml                         │
│    ├── includes: 001-create-tables.xml       │
│    ├── includes: 002-add-indexes.xml         │
│    └── includes: 003-add-loyalty-tier.xml   │
│                         │                   │
│                         ▼                   │
│           DATABASECHANGELOGLOCK (lock)       │
│                         │                   │
│       For each changeset in order:          │
│         ┌───────────────┴──────────┐        │
│         │ In DATABASECHANGELOG?    │        │
│         │  YES → checksum match?  │        │
│         │    YES → skip           │        │
│         │    NO  → ERROR (drift)  │        │
│         │  NO  → run changeset    │        │
│         │        record in log    │        │
│         └─────────────────────────┘        │
│                                             │
│           DATABASECHANGELOGLOCK (unlock)    │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Developer writes changeset in XML/YAML/SQL
  │
  ▼
Commits to source control (PR review)
  │
  ▼
CI pipeline triggers liquibase update
       ← YOU ARE HERE
  │
  ▼
Liquibase acquires DATABASECHANGELOGLOCK
  │
  ▼
Reads changelog, compares to DATABASECHANGELOG
  │
  ▼
Applies new changesets (in DB transaction)
  │
  ▼
Records in DATABASECHANGELOG + releases lock
  │
  ▼
Application deployed alongside schema change
```

**FAILURE PATH:**
- **Checksum mismatch:** An applied changeset was modified. `ERROR: Validation Failed: 1 change set(s) check sum`. Fix: revert the modification or use `liquibase clearCheckSums` (dangerous - use only in dev).
- **Precondition fail:** e.g., `tableExists` check fails. Configurable: `HALT` (stop), `WARN` (continue), `MARK_RAN` (record without executing).
- **Lock stuck:** Previous run crashed; `DATABASECHANGELOGLOCK` remains locked. Fix: `liquibase releaseLocks`.

**WHAT CHANGES AT SCALE:**
- Multi-schema or multi-tenant environments: use Liquibase `<include>` with context/label filtering per tenant.
- Microservices: each service owns its own changelog. Schema changes in shared tables require cross-team coordination (expand-contract pattern).
- Zero-downtime deployments: changes must be backward-compatible (add column nullable first; backfill; add NOT NULL constraint later).

---

### 💻 Code Example

**Root changelog (`db/changelog/root.changelog.xml`):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
  xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.20.xsd">

  <include file="changes/001-initial-schema.xml"
           relativeToChangelogFile="true"/>
  <include file="changes/002-add-loyalty-tier.xml"
           relativeToChangelogFile="true"/>
</databaseChangeLog>
```

**Individual changeset (`002-add-loyalty-tier.xml`):**
```xml
<databaseChangeLog ...>
  <changeSet id="2024-06-01-add-loyalty-tier"
             author="alice">

    <preConditions onFail="MARK_RAN">
      <not>
        <columnExists tableName="customers"
                      columnName="loyalty_tier"/>
      </not>
    </preConditions>

    <addColumn tableName="customers">
      <column name="loyalty_tier"
              type="VARCHAR(20)"
              defaultValue="STANDARD">
        <constraints nullable="true"/>
      </column>
    </addColumn>

    <rollback>
      <dropColumn tableName="customers"
                  columnName="loyalty_tier"/>
    </rollback>
  </changeSet>
</databaseChangeLog>
```

**Raw SQL changeset (for complex DDL):**
```xml
<changeSet id="2024-06-15-create-materialized-view"
           author="bob"
           runOnChange="false"
           dbms="postgresql">
  <sql splitStatements="false">
    CREATE MATERIALIZED VIEW mv_customer_stats AS
    SELECT customer_id,
           COUNT(*) AS order_count,
           SUM(amount) AS total_spent
    FROM orders
    GROUP BY customer_id;
    CREATE UNIQUE INDEX ON mv_customer_stats(customer_id);
  </sql>
  <rollback>
    DROP MATERIALIZED VIEW IF EXISTS mv_customer_stats;
  </rollback>
</changeSet>
```

**Spring Boot integration (`application.yml`):**
```yaml
spring:
  liquibase:
    change-log: classpath:db/changelog/root.changelog.xml
    enabled: true
    default-schema: public
    contexts: ${SPRING_PROFILES_ACTIVE:dev}
```

**CLI commands:**
```bash
# Apply pending changes
liquibase update

# Preview SQL without applying
liquibase updateSQL

# Roll back last N changesets
liquibase rollbackCount 2

# Check status
liquibase status --verbose

# Release stuck lock
liquibase releaseLocks
```

---

### ⚖️ Comparison Table

| Feature | Liquibase | Flyway |
|---|---|---|
| Change format | XML, YAML, JSON, SQL | SQL (primary), Java |
| Changeset ID | `id + author + file` triple | Version number (V1__desc.sql) |
| Rollback support | Explicit `<rollback>` block | Manual (Community: none) |
| Preconditions | Yes (rich condition support) | No (Pro only limited) |
| Context/label filtering | Yes (flexible) | Placeholder substitution only |
| DB-agnostic DDL | Yes (change types) | No (raw SQL only) |
| Spring Boot integration | Yes | Yes |
| Community vs Pro | Apache 2.0 / Pro tier | Apache 2.0 / Pro tier |
| Checksum on change | MD5, configurable | CRC32 |
| Drift detection | Yes (checksum mismatch) | Yes (checksum mismatch) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "You can edit an applied changeset to fix a typo" | Editing an applied changeset changes its checksum. Next `liquibase update` fails with a validation error. Always add a new changeset to fix mistakes. |
| "Liquibase guarantees atomic rollback" | Rollback executes the `<rollback>` block. If the database doesn't support transactional DDL (e.g., MySQL ALTER TABLE), the rollback itself may partially fail. |
| "Liquibase handles data migrations automatically" | Liquibase applies structural DDL and SQL changesets. Complex data migration logic must be authored explicitly. It does not infer data transformations from schema diffs. |
| "runOnChange means it always re-runs" | `runOnChange="true"` re-runs the changeset only when its content changes (checksum differs). It is used for stored procedures and views that should be recreated on each change. |
| "Preconditions make changesets idempotent by default" | Preconditions guard execution; they don't make the changeset itself idempotent. An `addColumn` changeset without a `columnExists` precondition will fail if the column already exists. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Checksum Validation Failure**

**Symptom:** `liquibase update` fails: `ERROR: Validation Failed: 1 changeset(s) check sum`. Application startup fails in Spring Boot.

**Root Cause:** A changeset that was already applied to the database has been modified in source control (reformatted, comment added, whitespace changed).

**Diagnostic:**
```sql
-- Find the mismatched changeset
SELECT id, author, filename, md5sum, dateexecuted
FROM   databasechangelog
WHERE  id = '2024-06-01-add-loyalty-tier';
-- Compare md5sum with current file hash
```

**Fix:**
```bash
# In dev only: reset checksums and re-verify
liquibase clearCheckSums
liquibase validate

# NEVER use clearCheckSums in production
# Instead: revert the changeset modification in source control
```

**Prevention:** Treat applied changesets as immutable. Code review rule: never modify a changeset that has been merged to main.

---

**Mode 2: Stuck DATABASECHANGELOGLOCK**

**Symptom:** Application cannot start; `liquibase update` hangs indefinitely. Logs show "Waiting for changelog lock...".

**Root Cause:** A previous Liquibase run crashed (OOM kill, network failure) mid-migration. The lock row in `DATABASECHANGELOGLOCK` was never released.

**Diagnostic:**
```sql
-- Check lock status
SELECT id, locked, lockgranted, lockedby
FROM   databasechangeloglock;
-- If locked=1 and lockgranted is > N minutes ago → stuck
```

**Fix:**
```bash
liquibase releaseLocks
# Or manually:
# UPDATE databasechangeloglock SET locked=0,
#   lockgranted=NULL, lockedby=NULL WHERE id=1;
```

**Prevention:** Ensure Liquibase runs complete before the application starts (separate init container in Kubernetes, or `depends_on` health check in Docker Compose).

---

**Mode 3: Deployment Breaks Rolling Upgrade**

**Symptom:** During a rolling deployment (v1 pods still running), new schema change (column dropped) causes v1 pods to throw SQL errors on the now-missing column.

**Root Cause:** Schema change was not backward-compatible. Old application version references a column that no longer exists.

**Diagnostic:** Review the changelog for any `dropColumn`, `renameColumn`, or `modifyDataType` changesets deployed during a live rolling upgrade.

**Fix:** Use the expand-contract pattern:
```xml
<!-- Phase 1 (deploy with old app): add new column -->
<changeSet id="expand-add-new-col" author="ops">
  <addColumn tableName="orders">
    <column name="status_v2" type="VARCHAR(50)"/>
  </addColumn>
</changeSet>

<!-- Phase 2 (after all old pods gone): drop old col -->
<changeSet id="contract-drop-old-col" author="ops">
  <dropColumn tableName="orders"
              columnName="status"/>
</changeSet>
```

**Prevention:** Enforce backward-compatible migration policy in CI: additive changes only during rolling deployments; destructive changes only after full cutover.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Database Change Management - the practice Liquibase implements
- SQL - the language of Liquibase's SQL changesets
- JDBC - the connection layer Liquibase uses to communicate with databases

**Builds On This (learn these next):**
- CI/CD - how Liquibase fits into automated deployment pipelines
- Spring Boot - auto-runs Liquibase at startup via `spring.liquibase` configuration
- Schema Design Best Practices - designing changes to be backward-compatible

**Alternatives / Comparisons:**
- Flyway - simpler, SQL-first migration tool; fewer features, easier adoption
- Database Change Management - the broader concept and practice
- Schema Evolution - theory of managing schema changes over time

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════╗
║ WHAT IT IS     Versioned DB migration tool  ║
║ PROBLEM SOLVED Schema drift across envs;   ║
║                double-application of SQL    ║
║ KEY INSIGHT    DATABASECHANGELOG = state;   ║
║                checksum = drift guard       ║
║ USE WHEN       Team development; multi-env  ║
║                deployments; audit required  ║
║ AVOID WHEN     Simple solo project; Flyway  ║
║                SQL-only approach is enough  ║
║ TRADE-OFF      Audit + rollback vs immutable║
║                changesets + verbosity       ║
║ ONE-LINER      Never edit applied changeset;║
║                always add a new one         ║
║ NEXT EXPLORE   Flyway, expand-contract,     ║
║                Liquibase contexts/labels    ║
╚══════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(A - System Interaction)** Liquibase uses a `DATABASECHANGELOGLOCK` table to prevent concurrent migrations. In a Kubernetes deployment where 3 pods start simultaneously and each runs `liquibase update` on startup, describe exactly what happens - and why this is safe even without application-level coordination.

2. **(C - Design Trade-off)** Liquibase uses an `(id, author, filename)` triple for changeset identity instead of sequential version numbers. What specific team workflow problem does this solve that sequential numbers cannot, and what new problem does it introduce?

3. **(B - Scale)** You are managing a Liquibase changelog for 50 microservices, each with its own database schema, all stored in a monorepo. A shared `customers` table is owned by one service but referenced by FK in 20 others. A schema change to `customers` requires coordinated migration across all 20 services. How would you structure your changelogs and deployment pipeline to handle this without downtime?
