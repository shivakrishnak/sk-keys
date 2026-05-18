---
id: ATZ-046
title: "Authorization Performance at Scale"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-027, ATZ-030, ATZ-032, ATZ-039, ATZ-040
used_by: ATZ-049, ATZ-050, ATZ-051
related: ATZ-032, ATZ-039, ATZ-051
tags:
  - security
  - authorization
  - performance
  - scale
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/authorization/authorization-performance-at-scale/
---

⚡ **TL;DR** - Authorization is in the hot path of every request.
At scale, a naive "call the PDP on every API call" design adds
50-200ms latency per request and creates a single point of
failure. Solutions: in-process evaluation (bundle policy with
the service), aggressive caching (permission decisions cached
for 60-300s with invalidation on role change), local replicas
of the policy store, and pre-computed "effective permissions"
at login time for RBAC. The Google Zanzibar paper (2019) was
written specifically to address this problem at Google scale
(trillions of ACL checks per second).

---

### 📊 Entry Metadata

| #046 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-027 OPA, ATZ-030 Externalized Authz, ATZ-032 Permission Caching, ATZ-039 Policy Perf, ATZ-040 Distributed Authz | |
| **Used by:** | ATZ-049, ATZ-050, ATZ-051 | |
| **Related:** | ATZ-032 Caching, ATZ-039 Policy Evaluation, ATZ-051 Central vs Distributed | |

---

### 📘 Textbook Definition

Authorization performance becomes a critical engineering
concern when the authorization check is in the critical path
of every HTTP request and the system handles hundreds of
thousands to millions of requests per second. Performance
optimization strategies: in-process evaluation (embed OPA
or policy logic within the service binary, eliminating network
round trips), result caching (cache allow/deny decisions by
(principal, resource, action) with TTL-based expiry and event-
based invalidation), local policy store replicas (each service
has a local read-only copy of the policy store, updated by push),
and pre-computation (compute effective permission sets at
session creation, store in JWT claims or session store).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authorization Performance Strategies           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  OPTION 1: Remote PDP (naive)                          │
│  Service -> Network call -> PDP -> decision            │
│  Latency: +50-200ms per request                        │
│  Risk: PDP unavailable = full service outage           │
│  Use only for: infrequent high-stakes decisions        │
│                                                        │
│  OPTION 2: Sidecar PDP (OPA)                           │
│  Service -> localhost OPA -> decision                  │
│  OPA gets policy updates from control plane            │
│  Latency: +1-5ms (no network hop)                      │
│  Risk: per-pod policy sync lag                         │
│                                                        │
│  OPTION 3: In-process evaluation                       │
│  Policy compiled into service (OPA Rego -> WASM)       │
│  Latency: +0.1-0.5ms (function call)                   │
│  Risk: policy update requires redeploy                 │
│  Best for: stable policies (RBAC, fixed rules)         │
│                                                        │
│  OPTION 4: Pre-computed permissions                    │
│  At login: compute all permissions, store in JWT       │
│  Per-request: verify signature, read claims            │
│  Latency: +0ms (already in JWT)                        │
│  Risk: stale permissions until token expires           │
│  Best for: RBAC with few roles                         │
│                                                        │
│  OPTION 5: Zanzibar-style                              │
│  Relationship tuples in distributed store              │
│  Cache layer (namespace config + check cache)          │
│  Latency: 1-3ms at p99 for simple checks               │
│  Best for: ReBAC, complex object hierarchies           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA embedded as sidecar with caching**

```yaml
# Kubernetes sidecar: OPA runs per pod on localhost:8181
# Each service calls http://localhost:8181/v1/data/authz/allow
# Policy updates: OPA polls bundle server every 60s
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: app
          image: myapp:latest
        - name: opa
          image: openpolicyagent/opa:latest
          args:
            - "run"
            - "--server"
            - "--addr=localhost:8181"
            # Pull policy bundles from central store
            - "--set=services.authz.url=https://opa-bundle"
            - "--set=bundles.authz.resource=/bundles/authz"
            # Cache check results for 60s
            - "--set=decision_logs.console=true"
          ports:
            - containerPort: 8181
```

**Example - Local permission cache with invalidation**

```java
@Service
public class CachedAuthzService {

    // Cache: userId -> Map<resource, Set<actions>>
    // TTL: 60 seconds (accept slight staleness)
    private final Cache<String, PermissionSet> cache =
        Caffeine.newBuilder()
            .expireAfterWrite(60, TimeUnit.SECONDS)
            .maximumSize(10_000)
            .build();

    public boolean isAllowed(String userId,
                              String resource,
                              String action) {
        PermissionSet perms = cache.get(userId,
            k -> pdpClient.fetchPermissions(k));
        return perms.allows(resource, action);
    }

    // Invalidate on role/permission change event
    @EventListener
    public void onPermissionChanged(
            PermissionChangedEvent event) {
        cache.invalidate(event.getUserId());
        // Also: invalidate all sessions for this user
        // so next request re-fetches fresh permissions
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-046 | v5.0*