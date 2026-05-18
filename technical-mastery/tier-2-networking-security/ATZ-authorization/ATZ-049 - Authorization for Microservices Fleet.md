---
id: ATZ-049
title: "Authorization for Microservices Fleet"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-033, ATZ-040, ATZ-046, ATZ-047, ATZ-048
used_by: ATZ-050, ATZ-051, ATZ-053
related: ATZ-033, ATZ-040, ATZ-051
tags:
  - security
  - authorization
  - microservices
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/authorization/authorization-for-microservices-fleet/
---

⚡ **TL;DR** - A microservices fleet has dozens or hundreds of
services, each with its own access control requirements. Central
policy + distributed enforcement (OPA sidecar pattern) is the
production-proven approach: policies are authored and stored
centrally, deployed to every service as sidecar agents, and
evaluated locally (in-process or sidecar). Services do not call
a remote PDP on every request. Policy changes propagate via a
bundle push to all sidecars, typically within seconds to minutes.

---

### 📊 Entry Metadata

| #049 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-033 Cross-Service, ATZ-040 Distributed Authz, ATZ-046 Performance, ATZ-047 Multi-Tenant, ATZ-048 Zero Trust | |
| **Used by:** | ATZ-050, ATZ-051, ATZ-053 | |
| **Related:** | ATZ-033 Cross-Service, ATZ-040 Distributed Authz, ATZ-051 Central vs Distributed | |

---

### 📘 Textbook Definition

Authorization for a microservices fleet must solve: consistent
policy enforcement across heterogeneous services (different
languages, frameworks), low-latency authorization in the hot
path, policy lifecycle management (author, test, version,
deploy, rollback), and auditability (who authorized what, when,
why). The OPA sidecar pattern (Open Policy Agent deployed as a
sidecar or library per service) is the de facto standard: a
central bundle server hosts policies, each OPA agent pulls and
caches policy bundles, and authorization decisions are made
locally. Services call `POST localhost:8181/v1/data/authz/allow`
and receive allow/deny decisions in 1-5ms without network hops.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│     Authorization for Microservices Fleet              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  CONTROL PLANE:                                        │
│  Policy repo (Git): Rego policies, version-controlled  │
│  CI pipeline: test, validate, bundle                   │
│  Bundle server: serves versioned policy bundles        │
│                                                        │
│  DATA PLANE (per service):                             │
│  OPA sidecar: pulls bundle every 30s                   │
│  Service -> POST localhost:8181/v1/data/authz/allow    │
│    Input: {principal, resource, action, context}       │
│    Output: {allow: true/false, reason: "..."}          │
│  Latency: 1-5ms (localhost, no network hop)            │
│  OPA sidecar down: fail-closed (deny)                  │
│                                                        │
│  POLICY LIFECYCLE:                                     │
│  PR in policy repo -> review -> merge                  │
│  CI: opa test (unit tests for all policies)            │
│  CD: build new bundle, push to bundle server           │
│  All OPA agents: pull new bundle within 30-60s         │
│  Rollback: revert commit, push previous bundle         │
│                                                        │
│  AUDIT:                                                │
│  OPA decision logs: every allow/deny with full input   │
│  Shipped to central log store for compliance           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Calling OPA sidecar from a Java service**

```java
@Service
public class OpaAuthzClient {

    private final RestTemplate restTemplate;

    public boolean isAllowed(AuthzRequest request) {
        // OPA sidecar: localhost:8181
        // Always co-located: no network latency
        OpaInput input = OpaInput.builder()
            .principal(request.getPrincipal())
            .resource(request.getResource())
            .action(request.getAction())
            .context(buildContext(request))
            .build();

        try {
            OpaResponse response = restTemplate.postForObject(
                "http://localhost:8181/v1/data/authz/allow",
                Map.of("input", input),
                OpaResponse.class);
            return response != null
                && Boolean.TRUE.equals(response.getResult());
        } catch (ResourceAccessException e) {
            // OPA sidecar unavailable: fail closed
            log.error("OPA unavailable - denying request: {}",
                request.getResource());
            return false; // DENY by default
        }
    }
}
```

**Example - OPA bundle server deployment**

```yaml
# Bundle server: serves policy bundles to all OPA agents
# OPA agents pull bundles every 30s (configurable)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa-bundle-server
spec:
  template:
    spec:
      containers:
        - name: bundle-server
          # Simple nginx serving /bundles/*.tar.gz
          image: nginx:latest
          volumeMounts:
            - name: bundles
              mountPath: /usr/share/nginx/html/bundles
      volumes:
        - name: bundles
          # Bundles built in CI and pushed to this PVC
          persistentVolumeClaim:
            claimName: policy-bundles-pvc
```

---

*Authorization category: ATZ | Entry: ATZ-049 | v5.0*