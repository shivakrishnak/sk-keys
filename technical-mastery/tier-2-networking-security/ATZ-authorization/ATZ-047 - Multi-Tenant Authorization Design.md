---
id: ATZ-047
title: "Multi-Tenant Authorization Design"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-013, ATZ-019, ATZ-030, ATZ-040
used_by: ATZ-049, ATZ-050, ATZ-052
related: ATZ-019, ATZ-040, ATZ-049
tags:
  - security
  - authorization
  - multi-tenant
  - saas
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/authorization/multi-tenant-authorization-design/
---

⚡ **TL;DR** - In multi-tenant systems (SaaS), authorization must
prevent tenant A from accessing tenant B's data (tenant isolation),
while also supporting each tenant's own RBAC within their tenant
(tenant-scoped roles: user can be admin in tenant A but read-only
in tenant B). The risk is "cross-tenant data leakage" - OWASP's
most severe authorization failure for SaaS. Every database query,
every API endpoint, and every policy evaluation must scope to the
current tenant.

---

### 📊 Entry Metadata

| #047 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-013 RBAC Patterns, ATZ-019 Row-Level Security, ATZ-030 Externalized Authz, ATZ-040 Distributed Authz | |
| **Used by:** | ATZ-049, ATZ-050, ATZ-052 | |
| **Related:** | ATZ-019 Row-Level Security, ATZ-040 Distributed Authz, ATZ-049 Microservices | |

---

### 📘 Textbook Definition

Multi-tenant authorization requires two orthogonal dimensions
of isolation: between tenants (no tenant sees another's data
or resources) and within a tenant (users have different roles
and permissions within the tenant). Implementation approaches
range from database-level isolation (separate schemas per
tenant) through row-level security (shared schema, tenant_id
column, automatic WHERE clause injection) to application-level
enforcement (every query explicitly includes the tenant scope).
Authorization systems must understand tenant context at policy
evaluation time, meaning the JWT or session must carry a
tenant_id claim, and policies must use this claim as a
mandatory filter.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Multi-Tenant Authorization Layers              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  JWT structure for multi-tenant:                       │
│  {                                                     │
│    "sub": "user-123",                                  │
│    "tenant_id": "tenant-abc",                          │
│    "roles": ["admin"],  <- TENANT-scoped roles         │
│    "permissions": ["users:read","users:write"]         │
│  }                                                     │
│  "admin" in tenant-abc != "admin" in tenant-xyz        │
│                                                        │
│  Database layer (PostgreSQL RLS):                      │
│  CREATE POLICY tenant_isolation ON documents           │
│    USING (tenant_id = current_setting('app.tenant_id'))│
│  SET app.tenant_id = :tenantId before each request     │
│  Every query: WHERE tenant_id = 'tenant-abc' added     │
│  Accidental cross-tenant query: returns empty result   │
│  NOT: returns wrong tenant's data                      │
│                                                        │
│  Failure mode:                                         │
│  Shared DB, no RLS                                     │
│  Query: SELECT * FROM documents WHERE id = 123         │
│  Returns document for tenant-xyz                       │
│  (user is in tenant-abc - cross-tenant leak)           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Tenant context injection in Spring**

```java
@Component
public class TenantContextFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain chain) throws Exception {
        // Extract tenant from JWT claim
        String tenantId = extractTenantFromJwt(
            request.getHeader("Authorization"));

        if (tenantId == null) {
            response.sendError(
                HttpServletResponse.SC_UNAUTHORIZED,
                "Tenant context required");
            return;
        }
        // Set thread-local tenant context
        TenantContext.setCurrentTenant(tenantId);
        try {
            chain.doFilter(request, response);
        } finally {
            TenantContext.clear(); // CRITICAL: prevent leak
        }
    }
}

// Repository: automatically scoped to current tenant
@Repository
public class DocumentRepository {

    public List<Document> findAll() {
        String tenantId =
            TenantContext.getCurrentTenant();
        // Query ALWAYS includes tenant filter
        return entityManager.createQuery(
            "SELECT d FROM Document d " +
            "WHERE d.tenantId = :tenantId",
            Document.class)
            .setParameter("tenantId", tenantId)
            .getResultList();
        // If tenantId is null: throw, never return all docs
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-047 | v5.0*