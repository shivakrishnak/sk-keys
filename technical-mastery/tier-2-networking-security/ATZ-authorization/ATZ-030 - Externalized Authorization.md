---
id: ATZ-030
title: "Externalized Authorization"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-026, ATZ-027, ATZ-028
used_by: ATZ-039, ATZ-040, ATZ-048, ATZ-049, ATZ-050
related: ATZ-027, ATZ-028, ATZ-040
tags:
  - security
  - authorization
  - externalized
  - policy-engine
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/authorization/externalized-authorization/
---

⚡ **TL;DR** - Externalized authorization moves access control
decisions out of application code and into a dedicated policy
engine (OPA, Cedar, SpiceDB). Instead of `if (user.role == 'admin')
return allowed`, the application asks a policy service "is this
request authorized?" and enforces the response. The benefit:
policy changes don't require code redeployment. The tradeoff:
the policy engine is now a critical-path dependency - if it goes
down or responds slowly, every request fails. Requires caching
and fail-open/fail-closed decisions.

---

### 📊 Entry Metadata

| #030 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-027 OPA, ATZ-028 Cedar | |
| **Used by:** | ATZ-039, ATZ-040, ATZ-048, ATZ-049, ATZ-050 | |
| **Related:** | ATZ-027 OPA, ATZ-028 Cedar, ATZ-040 Distributed Auth Architecture | |

---

### 📘 Textbook Definition

Externalized authorization is an architectural pattern where
authorization decisions are delegated to a dedicated, external
authorization service (the Policy Decision Point, PDP) rather
than embedded in application code. The application acts as a
Policy Enforcement Point (PEP): it intercepts requests,
constructs an authorization request, sends it to the PDP,
and enforces the decision. This decoupling enables: policy
changes without code deployment, consistent authorization
across multiple services, centralized audit logging of
decisions, and independent scaling of the authorization tier.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Externalized Authorization Architecture        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PEP = Policy Enforcement Point (your application)     │
│  PDP = Policy Decision Point (OPA, Cedar, SpiceDB)     │
│  PAP = Policy Administration Point (policy editor UI)  │
│  PIP = Policy Information Point (user/resource data)   │
│                                                        │
│  Flow:                                                 │
│  1. User -> PEP: GET /documents/doc-001                │
│  2. PEP -> PDP: {user: alice, action: read,            │
│                   resource: doc-001}                   │
│  3. PDP -> PIP: fetch alice's roles, doc-001 attrs     │
│  4. PDP evaluates policies                             │
│  5. PDP -> PEP: {allow: true}                          │
│  6. PEP enforces: serve or reject                      │
│                                                        │
│  LATENCY CONCERN:                                      │
│  Local OPA sidecar: <1ms (in-process evaluation)       │
│  Remote OPA daemon: 1-5ms (network call)               │
│  Remote SpiceDB: 2-10ms (relationship lookup)          │
│  Cache PDP decisions: TTL 30-60s for stable resources  │
│                                                        │
│  FAIL BEHAVIOR:                                        │
│  PDP unreachable: fail closed (deny all) for sensitive │
│  PDP unreachable: fail open (allow) for low-risk       │
│  Document your choice explicitly per service           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Externalized authorization interceptor (Spring)**

```java
@Component
public class AuthorizationInterceptor
        implements HandlerInterceptor {

    private final AuthorizationClient pdp;
    private final Cache<String, Boolean> decisionCache;

    @Override
    public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response,
            Object handler) throws Exception {
        String userId = extractUserId(request);
        String resource = extractResource(request);
        String action = mapMethodToAction(
            request.getMethod());

        // Check cache first
        String cacheKey = userId + ":" + action + ":"
            + resource;
        Boolean cached = decisionCache.getIfPresent(cacheKey);
        if (cached != null) {
            if (!cached) response.sendError(403);
            return cached;
        }

        boolean allowed;
        try {
            allowed = pdp.isAuthorized(
                userId, action, resource);
        } catch (PdpUnavailableException e) {
            log.error("PDP unavailable - failing closed");
            response.sendError(503);
            return false; // fail closed
        }

        // Cache decision for 30 seconds
        decisionCache.put(cacheKey, allowed,
            Duration.ofSeconds(30));

        if (!allowed) response.sendError(403);
        return allowed;
    }
}
```

**Example - BAD: baking authorization logic into services**

```java
// BAD: authorization logic in application code
// Changing this rule requires redeploying all services
@GetMapping("/documents/{id}")
public Document getDocument(@PathVariable String id,
                              Principal user) {
    Document doc = docRepo.findById(id).orElseThrow();
    // This logic is embedded, duplicated across services,
    // and changes require finding every copy
    if (!user.getName().equals(doc.getOwnerId())
            && !userService.hasRole(user, "ADMIN")) {
        throw new ForbiddenException();
    }
    return doc;
}

// GOOD: PEP pattern - enforce externally decided result
@GetMapping("/documents/{id}")
public Document getDocument(@PathVariable String id,
                              Principal user) {
    // Authorization already enforced by interceptor/filter
    // This method only runs if access was granted
    return docRepo.findById(id).orElseThrow();
}
```

---

*Authorization category: ATZ | Entry: ATZ-030 | v5.0*