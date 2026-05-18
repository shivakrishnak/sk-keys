---
id: ATZ-040
title: "Distributed Authorization Architecture"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-030, ATZ-033, ATZ-035, ATZ-036
used_by: ATZ-046, ATZ-047, ATZ-048, ATZ-049, ATZ-050
related: ATZ-030, ATZ-033, ATZ-049
tags:
  - security
  - authorization
  - distributed
  - architecture
  - microservices
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 40
permalink: /technical-mastery/authorization/distributed-authorization-architecture/
---

⚡ **TL;DR** - In distributed systems, authorization is not a solved
problem at the edges. The fundamental challenge: how do you enforce
consistent access control across 50+ microservices when they all
have different data stores and make independent decisions? Options:
centralized PDP (single policy engine - consistency but latency),
sidecar PDP (each service has OPA sidecar - low latency but
synchronization lag), or API gateway enforcement (catch-all but
too coarse for fine-grained data access). Production systems
combine all three layers.

---

### 📊 Entry Metadata

| #040 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-030 Externalized, ATZ-033 Cross-Service, ATZ-035 Dynamic, ATZ-036 ReBAC | |
| **Used by:** | ATZ-046, ATZ-047, ATZ-048, ATZ-049, ATZ-050 | |
| **Related:** | ATZ-030 Externalized, ATZ-033 Cross-Service, ATZ-049 Microservices Fleet | |

---

### 📘 Textbook Definition

Distributed authorization architecture defines how access control
decisions are made, enforced, and synchronized across multiple
independent services in a distributed system. Key architectural
patterns: (1) Centralized PDP - all services call a single policy
decision point (high consistency, single point of failure risk),
(2) Distributed PDP with synchronized policy bundles - each
service runs its own OPA instance with policies pushed from a
central store (low latency, eventual consistency), (3) Service
mesh authorization - mTLS identity for service-to-service auth
with central policy enforcement in the mesh control plane,
(4) API Gateway - coarse-grained authorization at the ingress.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│      Distributed Authorization Topology                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LAYER 1: API Gateway                                  │
│  - Authentication: validate JWT/token                  │
│  - Coarse authorization: is this endpoint public?      │
│  - Rate limiting, DDoS protection                      │
│  - Does NOT: check ownership, row-level access         │
│                                                        │
│  LAYER 2: Service Mesh (mTLS)                          │
│  - Service-to-service identity (SPIFFE)                │
│  - Allow/deny service-to-service calls                 │
│  - Service A cannot call Service B if not permitted    │
│  - Does NOT: check user-level permissions             │
│                                                        │
│  LAYER 3: Per-Service PDP (OPA sidecar or lib)         │
│  - Fine-grained user-level authorization               │
│  - Evaluates roles, attributes, dynamic context        │
│  - Has policy bundle from central policy store         │
│  - Does NOT: persistent relationship data              │
│                                                        │
│  LAYER 4: Relationship DB (SpiceDB/OpenFGA) - optional │
│  - For sharing models (who can access doc-001?)        │
│  - Serves as source of truth for fine-grained access   │
│  - Called by service-level PDP for relevant checks     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA sidecar policy bundle distribution**

```yaml
# OPA sidecar config in Kubernetes pod spec
# Policy bundles are pulled from central bundle server
# Bundle server serves policies compiled from GitOps repo

containers:
  - name: app
    image: myapp:latest

  - name: opa-sidecar
    image: openpolicyagent/opa:latest
    args:
      - "run"
      - "--server"
      - "--addr=localhost:8181"
      - "--bundle"
      - "https://policy-server/bundles/prod" # central store
      - "--log-level=error"
    env:
      - name: OPA_BUNDLE_SIGNING_KEY
        valueFrom:
          secretKeyRef:
            name: opa-bundle-key
            key: public-key
    # Bundle refresh every 30 seconds
    # Policy updates propagate within 30s
    # No service restart needed
```

**Example - Multi-layer authorization check in Java**

```java
@Component
public class LayeredAuthorizationFilter
        extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain chain) throws Exception {
        // Layer 3: OPA local sidecar check
        // (Layer 1 + 2 already handled by gateway + mesh)
        String userId = extractUserId(request);
        String resource = extractResource(request);
        String action = mapMethod(request.getMethod());

        // OPA sidecar is on localhost - no network hop
        boolean allowed = opaClient.check(
            userId, resource, action);

        if (!allowed) {
            response.sendError(403, "Forbidden");
            return;
        }
        chain.doFilter(request, response);
    }
}
```

---

*Authorization category: ATZ | Entry: ATZ-040 | v5.0*