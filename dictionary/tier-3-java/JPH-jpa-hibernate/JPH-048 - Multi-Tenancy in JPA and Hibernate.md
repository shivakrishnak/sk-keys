---
id: JPH-048
title: Multi-Tenancy in JPA and Hibernate
category: JPA & Hibernate
tier: tier-3-java
folder: JPH-jpa-hibernate
difficulty: ★★★
depends_on: JPH-006, JPH-011, JPH-012, JPH-013, JPH-026, JPH-047
used_by: JPH-054, JPH-061
related: JPH-040, JPH-043, JPH-047, JPH-061
tags:
  - java
  - jpa
  - database
  - advanced
status: complete
version: 4
layout: default
parent: "JPA & Hibernate"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /jpa-hibernate/multi-tenancy/
---

# JPH-048 - Multi-Tenancy in JPA and Hibernate

⚡ **TL;DR** - Multi-tenancy lets a single app serve
multiple customers (tenants) while keeping their data
isolated. Three strategies: **SEPARATE_DATABASE** (one DB
per tenant, maximum isolation, high resource cost),
**SEPARATE_SCHEMA** (one schema per tenant in one DB, good
balance), **DISCRIMINATOR** (one table, tenant_id column,
cheapest, lowest isolation). Hibernate implements via
`MultiTenantConnectionProvider` (provides connections per
tenant) and `CurrentTenantIdentifierResolver` (determines
tenant from request context). Spring Boot: use
`AbstractRoutingDataSource` for schema/database strategies.

| #048 | Category: JPA & Hibernate | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Entity Basics, EntityManager, JPA Lifecycle, @Transactional, Connection Pooling | |
| **Used by:** | JPA at Scale, JPA with Multiple Databases | |
| **Related:** | Inheritance Mapping, Specifications, Connection Pooling, Multiple Databases | |

---

### 🔥 The Problem This Solves

**THE MULTI-TENANT DATA ISOLATION CHALLENGE:**
You're building a SaaS CRM serving 500 customers. Each
customer's data must be completely isolated - customer A
cannot see customer B's contacts. You have three choices:

1. **SEPARATE_DATABASE** - 500 databases. Total isolation.
   500 connection pools. 500 schema migration runs. $$$
2. **SEPARATE_SCHEMA** - 500 schemas in 1 database. Good isolation.
   500 schema migrations. Moderate resource use.
3. **DISCRIMINATOR** - 1 schema, `tenant_id` column everywhere.
   Simple. Must add `WHERE tenant_id = ?` to EVERY query.
   SQL injection of tenant ID = data breach for all 500 customers.

Hibernate provides built-in support for all three strategies,
automating the tenant routing transparently.

---

### 📘 Textbook Definition

**Multi-tenancy** is an architecture where a single
application instance serves multiple tenants (customers,
organizations, accounts) with isolated data.

**Hibernate multi-tenancy strategies (`MultiTenancyStrategy`):**

| Strategy | Hibernate Enum | Isolation | Resource Cost | Use Case |
|---|---|---|---|---|
| Separate Database | `DATABASE` | Maximum | High | Healthcare, Finance (strict compliance) |
| Separate Schema | `SCHEMA` | High | Medium | Most SaaS apps |
| Shared Table (discriminator) | `DISCRIMINATOR` | Low | Low | Small apps, low-sensitivity data |

**Key interfaces:**
- `CurrentTenantIdentifierResolver` - extracts tenant ID from
  request context (thread-local, JWT, header)
- `MultiTenantConnectionProvider` - provides a JDBC connection
  for the given tenant ID (switches schema/database)

---

### ⏱️ Understand It in 30 Seconds

**One line:** Multi-tenancy routes database connections
or queries to tenant-specific isolation boundaries
(database, schema, or row-level filter).

**One analogy:**
> Multi-tenancy is like a hotel. **SEPARATE_DATABASE**:
> each guest has a separate building (total isolation; very
> expensive). **SEPARATE_SCHEMA**: each guest has a
> separate floor (good isolation; shared infrastructure).
> **DISCRIMINATOR**: all guests share the same rooms but
> every piece of furniture is tagged with the guest's
> name (cheapest; data breach risk if tagging fails).
> Hibernate is the hotel concierge that routes each guest
> to the right floor/room automatically.

**One insight:** DISCRIMINATOR is the easiest to implement
but the most dangerous. A missing `WHERE tenant_id = ?`
clause leaks all tenants' data. Hibernate 6 has experimental
`@TenantId` support to enforce discriminator filtering
automatically, but it's incomplete. For production SaaS
with real isolation requirements: SCHEMA or DATABASE.

---

### 🔩 First Principles Explanation

**SCHEMA STRATEGY - HOW IT WORKS:**

```
Request arrives with header: X-Tenant-Id: acme-corp

1. CurrentTenantIdentifierResolver
   -> extracts "acme-corp" from RequestAttributes
   -> stored in ThreadLocal (per-request)

2. @Transactional method begins
   -> Spring calls DataSource.getConnection()

3. MultiTenantConnectionProvider.getConnection("acme-corp")
   -> get a connection from pool
   -> execute: SET search_path TO acme_corp (PostgreSQL)
      or USE acme_corp (MySQL)
   -> return connection

4. All queries in this transaction go to the "acme_corp" schema
   -> SELECT * FROM orders   (implicitly: acme_corp.orders)

5. Transaction commits
   -> connection returned to pool
   -> schema context may need to be reset (depends on impl)

6. Next request with tenant "globex":
   -> Same process, SET search_path TO globex
```

---

### 🧪 Thought Experiment

**WHAT HAPPENS WHEN TENANT ID IS MISSING?**

```java
// BAD: tenant ID not set in context
@GetMapping("/orders")
public List<Order> getOrders() {
    // Request came in without X-Tenant-Id header
    // CurrentTenantIdentifierResolver returns null
    // MultiTenantConnectionProvider called with null
    // Result depends on implementation:
    //   -> if null schema: may query default schema
    //      (all tenants' data!) - CRITICAL DATA BREACH
    //   -> if null rejected: NullPointerException
    //      or explicit rejection (safe fail)

    return orderRepo.findAll(); // WHICH TENANT'S ORDERS?
}

// GOOD: always validate tenant before processing
@GetMapping("/orders")
public List<Order> getOrders(
    @RequestHeader("X-Tenant-Id") String tenantId) {
    // Header required; 400 if missing
    // CurrentTenantIdentifierResolver reads from
    // validated, authenticated JWT - not raw header
    return orderRepo.findAll();
}
```

**Key safety rule:** NEVER accept tenant ID from
an unauthenticated header. Extract from JWT claims
or authenticated session only. The tenant ID should
be validated against the authenticated user's allowed
tenants before being used.

---

### 🧠 Mental Model / Analogy

> Multi-tenancy is like a virtual private network (VPN)
> for data. Without VPN: all traffic on the same network
> (discriminator - all data in one table, isolation via
> software). With per-tenant VPN (schema strategy): each
> tenant's traffic is in its own encrypted tunnel - the
> tunnel is transparent to the application but provides
> hard isolation. The `MultiTenantConnectionProvider`
> is the VPN gateway - it routes each session to the
> right tunnel (schema/database) based on identity.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Multi-tenancy means one application serves many customers
with each customer's data kept separate.

**Level 2 - Three strategies (junior developer):**
- **Discriminator**: one table, add `tenant_id` column
- **Schema**: one DB, separate schema per tenant
  (`SET search_path TO tenant_schema`)
- **Database**: completely separate DB per tenant

**Level 3 - Hibernate interfaces (mid-level engineer):**
```java
@Component
public class TenantResolver
    implements CurrentTenantIdentifierResolver {

    @Override
    public String resolveCurrentTenantIdentifier() {
        // Read from security context (e.g., JWT claim)
        Authentication auth = SecurityContextHolder
            .getContext().getAuthentication();
        if (auth instanceof TenantAwareToken t) {
            return t.getTenantId();
        }
        throw new TenantResolutionException(
            "No tenant in security context");
    }

    @Override
    public boolean validateExistingCurrentSessions() {
        return true;
    }
}
```

**Level 4 - Schema routing with HikariCP (senior engineer):**
```java
@Component
public class SchemaPerTenantConnectionProvider
    implements MultiTenantConnectionProvider {

    private final DataSource dataSource;

    @Override
    public Connection getConnection(Object tenantId)
        throws SQLException {
        Connection conn = dataSource.getConnection();
        // PostgreSQL: switch schema
        conn.createStatement()
            .execute("SET search_path TO " + tenantId);
        return conn;
    }

    @Override
    public Connection getAnyConnection() throws SQLException {
        return dataSource.getConnection();
    }

    // ... release methods ...
}
```

**Level 5 - Isolation attack vectors (staff engineer):**
SCHEMA strategy risks: SQL injection in tenant ID ->
`SET search_path TO '; DROP SCHEMA acme_corp; --'`.
Mitigation: validate tenant ID against a whitelist
(alphanumeric + hyphen only, length limit). Use prepared
statements or `Pattern.matches("[a-z0-9_-]{1,64}", tenantId)`.
Also: connection pool per tenant vs shared pool trade-off.
Shared pool: efficient but `search_path` must be reset
reliably on return. Per-tenant pool: clean but 500 tenants
= 500 pools = resource pressure. Solution: shared pool +
always set `search_path` on borrow (not on return).

---

### ⚙️ How It Works (Mechanism)

**FULL SPRING BOOT SCHEMA MULTI-TENANCY CONFIGURATION:**

```java
// 1. Hibernate JPA configuration with multi-tenancy
@Configuration
public class HibernateMultiTenancyConfig {

    @Bean
    public LocalContainerEntityManagerFactoryBean emf(
        DataSource ds,
        TenantResolver tenantResolver,
        SchemaPerTenantConnectionProvider connProvider) {

        LocalContainerEntityManagerFactoryBean emf =
            new LocalContainerEntityManagerFactoryBean();
        emf.setDataSource(ds);
        emf.setPackagesToScan("com.example.domain");

        HibernateJpaVendorAdapter va =
            new HibernateJpaVendorAdapter();
        emf.setJpaVendorAdapter(va);

        Properties props = new Properties();
        props.put(AvailableSettings.MULTI_TENANT,
            MultiTenancyStrategy.SCHEMA);
        props.put(
            AvailableSettings.MULTI_TENANT_CONNECTION_PROVIDER,
            connProvider);
        props.put(
            AvailableSettings.MULTI_TENANT_IDENTIFIER_RESOLVER,
            tenantResolver);
        emf.setJpaProperties(props);
        return emf;
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DISCRIMINATOR STRATEGY WITH @TenantId (Hibernate 6+):**

```java
// Entity with tenant ID (Hibernate 6 experimental)
@Entity
@Table(name = "orders")
public class Order {

    @Id @GeneratedValue
    private Long id;

    @TenantId  // Hibernate 6 - auto-filtered
    private String tenantId;

    private String product;
    private BigDecimal amount;
}

// Hibernate 6 auto-adds WHERE tenant_id = :currentTenant
// to all SELECT, UPDATE, DELETE for annotated entities.
// On INSERT: automatically sets tenantId from resolver.

// WARNING: This feature is experimental in Hibernate 6.x.
// Test thoroughly; verify no queries bypass the filter.
// For production-critical isolation: use SCHEMA strategy.
```

---

### 💻 Code Example

**Example 1 - BAD: tenant ID from untrusted header:**

```java
// BAD: tenant from user-controlled header
// SQL injection risk: header value used in SET search_path
@Component
public class UnsafeTenantResolver
    implements CurrentTenantIdentifierResolver {

    @Override
    public String resolveCurrentTenantIdentifier() {
        ServletRequestAttributes attrs =
            (ServletRequestAttributes)
            RequestContextHolder.getRequestAttributes();
        // DANGER: user can send ANY value in this header
        return attrs.getRequest()
            .getHeader("X-Tenant-Id");
    }
}

// GOOD: tenant from validated JWT
@Component
public class SafeTenantResolver
    implements CurrentTenantIdentifierResolver {

    @Override
    public String resolveCurrentTenantIdentifier() {
        Authentication auth = SecurityContextHolder
            .getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new AccessDeniedException("No auth");
        }
        String tenantId = ((JwtAuthToken) auth)
            .getTenantId();
        // Validate format (prevent injection)
        if (!tenantId.matches("[a-z0-9_-]{1,64}")) {
            throw new InvalidTenantException(
                "Invalid tenant ID format");
        }
        return tenantId;
    }
}
```

---

### ⚖️ Comparison Table

| Strategy | Isolation | DB connections | Schema migrations | Compliance | Code complexity |
|---|---|---|---|---|---|
| SEPARATE_DATABASE | Maximum | 1 pool per tenant | Per-tenant Flyway | Best (GDPR, HIPAA) | High |
| SEPARATE_SCHEMA | High | Shared pool | Per-schema Flyway | Good | Medium |
| DISCRIMINATOR | Low | Shared pool | One migration | Poor | Low (but risky) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "DISCRIMINATOR is safe with Hibernate's `@TenantId`" | Hibernate 6's `@TenantId` is experimental. It filters at the Hibernate level, not the DB level. A native query, JDBC template query, or bug in Hibernate's filter could bypass it, exposing all tenants' data. SCHEMA or DATABASE strategies enforce isolation at the JDBC layer where Hibernate bugs cannot bypass it. |
| "Multi-tenancy requires separate application instances" | No - one application instance can serve all tenants. Multi-tenancy is a data isolation pattern, not a deployment pattern. Separate deployments are a valid strategy but bring higher operational complexity. |
| "Connection pool can be naively shared across schemas" | When using SEPARATE_SCHEMA, connections are reused across tenants. The schema must be explicitly set (SET search_path) on EVERY borrow. If schema is only set on connection creation (at pool initialization), pooled connections will serve the wrong schema after first use. Always set the schema at borrow time, not creation time. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode: Data Leakage Across Tenants**

**Symptom:** Tenant A can see Tenant B's data.
In DISCRIMINATOR: query returns rows with wrong tenant_id.
In SCHEMA: query returns rows from wrong schema.
**Root Cause (DISCRIMINATOR):** Missing
`CurrentTenantIdentifierResolver` registration; tenant
ID not being set in context for async threads; native
queries bypassing Hibernate filter.
**Root Cause (SCHEMA):** `search_path` not being set on
connection borrow; connection returned to pool with wrong
`search_path` and reused by another tenant.
**Diagnosis:**
```java
// Add audit log to resolver:
public String resolveCurrentTenantIdentifier() {
    String tenant = extractFromSecurityContext();
    log.debug("Tenant resolved: {}", tenant);
    if (tenant == null) {
        log.error("NULL tenant - potential data leak risk");
        throw new TenantResolutionException("No tenant");
    }
    return tenant;
}
```
**Fix:** Reject null tenant IDs at resolver level;
always set `search_path` on connection borrow (not on
creation); add integration test that verifies cross-tenant
data isolation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JPH-026 - @Transactional]] - transactions span
  one tenant's connection; multi-tenancy resolves at
  transaction boundary
- [[JPH-047 - Connection Pooling]] - connection pool
  shared across tenants in SCHEMA strategy; pool management
  is critical for multi-tenancy

**Builds On This (learn these next):**
- [[JPH-061 - JPA with Multiple Databases]] - SEPARATE_DATABASE
  strategy uses multiple DataSource routing

**Related:**
- [[JPH-043 - Spring Data Specifications]] - DISCRIMINATOR
  strategy uses Specifications to add tenant_id filters
- [[JPH-040 - Inheritance Mapping]] - tenant isolation
  in polymorphic hierarchies requires careful design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRATEGIES   │ DATABASE: separate DB per tenant           │
│              │ SCHEMA: separate schema per tenant         │
│              │ DISCRIMINATOR: tenant_id column            │
├──────────────┼───────────────────────────────────────────┤
│ KEY TYPES    │ CurrentTenantIdentifierResolver:           │
│              │   resolveCurrentTenantIdentifier()         │
│              │ MultiTenantConnectionProvider:             │
│              │   getConnection(tenantId)                  │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG KEY   │ hibernate.multiTenancy=SCHEMA              │
│              │ hibernate.multi_tenant_connection_provider │
│              │ hibernate.tenant_identifier_resolver       │
├──────────────┼───────────────────────────────────────────┤
│ SECURITY     │ NEVER accept tenant from unauthenticated   │
│              │ header; use JWT claims; validate format    │
├──────────────┼───────────────────────────────────────────┤
│ SCHEMA       │ SET search_path on BORROW (not creation)   │
│ GOTCHA       │ Shared pool - always route on each use     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hibernate multi-tenancy: DATABASE/SCHEMA/ │
│              │ DISCRIMINATOR strategies. Resolver extracts│
│              │ tenant from JWT; ConnectionProvider routes │
│              │ to correct schema/db."                     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three strategies: DATABASE (most isolated, most expensive),
   SCHEMA (good balance), DISCRIMINATOR (cheapest, riskiest)
2. Two interfaces: `CurrentTenantIdentifierResolver` (WHO is requesting)
   + `MultiTenantConnectionProvider` (WHERE to route them)
3. Security: always extract tenant ID from JWT (never from raw headers);
   validate format to prevent schema name injection

**Interview one-liner:** Hibernate multi-tenancy isolates data via
DATABASE (separate DB), SCHEMA (separate schema with
`SET search_path`), or DISCRIMINATOR (shared table with
tenant_id column). Two key interfaces: `CurrentTenantIdentifierResolver`
extracts tenant ID from JWT/security context; `MultiTenantConnectionProvider`
routes to the correct DB/schema. NEVER accept tenant ID from
unauthenticated input.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Data isolation boundaries
should be enforced at the deepest reliable layer possible.
For multi-tenancy: schema isolation enforced at the JDBC
connection level (SET search_path) is stronger than
application-level row filtering (WHERE tenant_id = ?).
A Hibernate bug, native query, or missing WHERE clause
breaks row-level isolation. Schema isolation requires a
compromised connection to break. This principle generalizes:
security controls at lower layers (OS, network, DB) are
more reliable than controls at higher layers (application
code). Defense in depth: use both.

**Where else this pattern appears:**
- **Row-Level Security (RLS)**: PostgreSQL RLS enforces
  row visibility at the DB level (like enhanced DISCRIMINATOR)
  without application code; can be combined with SCHEMA
  strategy for defense in depth
- **Kubernetes namespaces**: same concept - namespace
  isolates resources at the platform layer, not application layer

---

### 💡 The Surprising Truth

Hibernate's DISCRIMINATOR multi-tenancy strategy (the
simplest to implement) was NOT fully implemented in
Hibernate 5 - the `@TenantId` annotation to auto-filter
queries was only added as an experimental feature in
Hibernate 6. In Hibernate 5, using DISCRIMINATOR required
developers to manually add tenant filtering to every query
(JPQL, Criteria API, and Spring Data methods). This is why
so many production multi-tenant applications that use
Hibernate actually use SCHEMA strategy - not because the
DISCRIMINATOR schema is bad in theory, but because Hibernate
5 didn't automate it. Hibernate 6's `@TenantId` changes
this, but was released in 2022 and is still marked
experimental. For new projects: SCHEMA is the safe default;
use Hibernate 6's `@TenantId` only after thorough testing.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CHOOSE** the correct strategy (DATABASE/SCHEMA/DISCRIMINATOR)
   given isolation requirements and resource constraints
2. **IMPLEMENT** `CurrentTenantIdentifierResolver` that
   reads tenant ID from JWT and validates its format
3. **IMPLEMENT** `MultiTenantConnectionProvider` that
   sets `SET search_path` on connection borrow for SCHEMA strategy
4. **EXPLAIN** why tenant ID from unauthenticated headers is
   a data breach risk and how to prevent schema injection
5. **DESIGN** a connection pool strategy for SCHEMA multi-tenancy
   (shared pool + schema set on borrow vs per-tenant pools)

---

### 🎯 Interview Deep-Dive

**Q1: Your team is building a SaaS product for healthcare
organizations. Which multi-tenancy strategy would you choose
and why?**
*Why they ask:* Tests isolation vs cost trade-off analysis.
*Strong answer includes:*
- Healthcare (HIPAA): data isolation is a compliance requirement
- SEPARATE_DATABASE: maximum isolation; each organization's
  data in its own DB; a DB credential compromise only exposes
  one tenant's data; simplest compliance story
- Trade-offs: higher cost (one connection pool per tenant),
  more complex schema migrations (Flyway per DB), more infra
- SCHEMA is acceptable if DB-level isolation with RLS is added
- DISCRIMINATOR: NOT acceptable for HIPAA (risk of data leakage
  via missing filters; all tenants in same table)

**Q2: How do you ensure that a shared connection pool
correctly routes connections to the right tenant schema?**
*Why they ask:* Tests implementation correctness understanding.
*Strong answer includes:*
- Always set `SET search_path TO tenant_schema` on connection BORROW
  (in `MultiTenantConnectionProvider.getConnection(tenantId)`)
- NOT on connection creation (pool creates connections without tenant context)
- NOT on connection return (cannot assume next borrower wants to reset it)
- The `search_path` set during one tenant's request should not
  "leak" to the next tenant - always re-set on borrow
- Validate tenant ID format before using in SQL command
  (`[a-z0-9_-]{1,64}`) to prevent SQL injection