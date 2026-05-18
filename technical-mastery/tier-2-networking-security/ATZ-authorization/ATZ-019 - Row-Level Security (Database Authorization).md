---
id: ATZ-019
title: "Row-Level Security (Database Authorization)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-007, ATZ-009, ATZ-015
used_by: ATZ-032, ATZ-047, ATZ-049
related: ATZ-009, ATZ-015, ATZ-043
tags:
  - security
  - authorization
  - database
  - row-level-security
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/authorization/row-level-security-database-authorization/
---

⚡ **TL;DR** - Row-Level Security (RLS) enforces authorization inside
the database engine: a policy attached to a table automatically filters
which rows a database role can see or modify. RLS is defense-in-depth
for data authorization: even if the application has an IDOR vulnerability
or a direct database connection is used, the database enforces the
access boundary. PostgreSQL, MySQL 8.0+, SQL Server, and Oracle support
native RLS policies.

---

### 📊 Entry Metadata

| #019 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-007, ATZ-009, ATZ-015 | |
| **Used by:** | ATZ-032, ATZ-047, ATZ-049 | |
| **Related:** | ATZ-009 Resource Policies, ATZ-015 ABAC, ATZ-043 IDOR | |

---

### 🔥 The Problem This Solves

**APPLICATION-LAYER AUTHORIZATION IS NOT ENOUGH:**

Application code checks if `user_id = current_user_id`.
But: what if a developer writes a bug?

```sql
-- Developer intends user-scoped query:
SELECT * FROM orders WHERE status = 'PENDING';
-- Forgot the AND user_id = :userId predicate
-- Returns ALL users' pending orders
```

This is an IDOR vulnerability. The application layer failed.

Without RLS: every query that touches multi-tenant data
must be manually written with the tenant filter. One
missed WHERE clause = data leak.

With RLS: the database engine automatically appends the
policy predicate to every query. Even the buggy query above
would only return the current user's orders.

---

### 📘 Textbook Definition

Row-Level Security (RLS) is a database access control feature
that allows policies to be defined on database tables to restrict
which rows individual database roles can access. The policy is
evaluated as an additional predicate automatically added to all
queries against the table by the database engine. RLS operates
at the database layer, independently of application code, providing
defense-in-depth: application authorization bugs cannot bypass RLS.
PostgreSQL implements RLS via `CREATE POLICY`; SQL Server via
`SECURITY POLICY` with predicates; Oracle via Virtual Private Database.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         PostgreSQL RLS Policy Evaluation               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  WITHOUT RLS:                                          │
│  SELECT * FROM orders WHERE status = 'PENDING'         │
│  → Returns: ALL pending orders from all users          │
│                                                        │
│  WITH RLS POLICY:                                      │
│  Policy: "users see only their own rows"               │
│  CREATE POLICY tenant_isolation ON orders              │
│    FOR ALL TO app_user                                 │
│    USING (user_id = current_setting(                   │
│           'app.current_user_id')::bigint);             │
│                                                        │
│  Query: SELECT * FROM orders WHERE status = 'PENDING'  │
│  DB rewrites to:                                       │
│    SELECT * FROM orders                                │
│    WHERE status = 'PENDING'                            │
│      AND user_id = 42  ← automatically added by RLS   │
│  → Returns only current user's pending orders          │
│                                                        │
│  The application never needs to add the predicate.     │
│  It is enforced by the DB engine on every query.       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - PostgreSQL RLS for multi-tenant SaaS**

```sql
-- Enable RLS on the orders table
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
-- FORCE applies even to table owner (prevents bypass)

-- Policy: users see only their own tenant's orders
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    TO app_role  -- only applies to this DB role
    USING (
        tenant_id = current_setting(
            'app.tenant_id', true)::uuid
    )
    WITH CHECK (  -- also enforces on INSERT/UPDATE
        tenant_id = current_setting(
            'app.tenant_id', true)::uuid
    );

-- Admin bypass: create a separate role
-- app_admin_role has BYPASS ROW LEVEL SECURITY privilege
-- Do not grant BYPASSRLS to the application user
```

**Example - Setting RLS context in application (JDBC)**

```java
@Repository
public class OrderRepositoryWithRLS {

    @Autowired
    private JdbcTemplate jdbc;

    // Set the RLS context variable before queries
    public List<Order> findPendingOrders(UUID tenantId) {
        // Set the session variable that the RLS policy uses
        jdbc.execute(
            "SET LOCAL app.tenant_id = '" + tenantId + "'"
        );
        // All subsequent queries in this transaction
        // are automatically filtered to this tenant
        return jdbc.query(
            "SELECT * FROM orders WHERE status = 'PENDING'",
            new OrderRowMapper()
        );
    }
}

// Spring JPA equivalent using EntityManager
@PersistenceContext
EntityManager em;

public void setRlsContext(UUID tenantId) {
    em.createNativeQuery(
        "SET LOCAL app.tenant_id = :tid")
        .setParameter("tid", tenantId.toString())
        .executeUpdate();
}
```

**Example - BAD vs GOOD: application-only vs RLS defense-in-depth**

```java
// BAD: single layer - application must always add predicate
@Repository
public class OrderRepo {
    // Every query must manually include user_id filter
    // One bug = data leak
    public List<Order> findPending(Long userId) {
        return jpa.createQuery(
            "FROM Order WHERE status='PENDING'") // BUG: missing AND userId=:u
            .getResultList(); // returns ALL users' orders
    }
}

// GOOD: RLS at DB layer as defense-in-depth
// Even if application forgets the filter, DB enforces it
// Also handles: reporting queries, data exports, migrations,
// direct DB connections - all subject to the same policy
```

---

### 🔭 At Scale

RLS performance: the policy predicate is added to every query.
If the RLS column is indexed, performance is near-identical to
manually filtering. The `tenant_id` column (or `user_id`) must
have an index for RLS to be performant at scale.

At very high scale (100M+ rows, 10K+ tenants): consider
partition-by-tenant in addition to RLS, so each tenant's data
is in a separate partition. This improves query performance
beyond what an index alone provides and also enables
tenant-specific maintenance (backup, purge) without affecting
other tenants.

---

*Authorization category: ATZ | Entry: ATZ-019 | v5.0*