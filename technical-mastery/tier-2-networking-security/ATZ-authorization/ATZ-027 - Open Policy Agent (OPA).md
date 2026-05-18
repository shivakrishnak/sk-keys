---
id: ATZ-027
title: "Open Policy Agent (OPA)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-026, ATZ-029
used_by: ATZ-029, ATZ-030, ATZ-039, ATZ-048, ATZ-053
related: ATZ-026, ATZ-029, ATZ-030
tags:
  - security
  - authorization
  - opa
  - policy
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/authorization/open-policy-agent-opa/
---

⚡ **TL;DR** - Open Policy Agent (OPA) is a general-purpose policy
engine used to externalize authorization from application code.
Policies are written in Rego (ATZ-029). OPA can enforce access
control in Kubernetes (admission control), API gateways, microservices,
and CI/CD pipelines from a single policy engine. The key insight:
any system that sends a JSON authorization request to OPA gets a
consistent allow/deny response without each system implementing its
own authorization logic.

---

### 📊 Entry Metadata

| #027 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-026 PBAC, ATZ-029 Rego | |
| **Used by:** | ATZ-029, ATZ-030, ATZ-039, ATZ-048, ATZ-053 | |
| **Related:** | ATZ-026 PBAC, ATZ-029 Rego, ATZ-030 Externalized Auth | |

---

### 📘 Textbook Definition

Open Policy Agent (OPA, CNCF graduated project) is a lightweight,
general-purpose policy engine that decouples authorization logic
from application code. Applications send authorization requests
as JSON to OPA; OPA evaluates the request against policies written
in the Rego language and returns a structured JSON decision.
OPA is used for: Kubernetes admission control (via Gatekeeper),
HTTP API authorization (via Envoy external authz), Terraform
policy validation, CI/CD policy enforcement, and microservice
authorization. OPA is stateless (policies are loaded separately
from decisions) and embeds directly into services or runs as a
sidecar/daemon.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            OPA Architecture                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Three inputs to OPA:                                  │
│  1. Policies (Rego code) - loaded at startup or        │
│     updated via Bundle API                             │
│  2. Data (external data: user DB, resource metadata)   │
│     - loaded separately from policies                  │
│  3. Input (authorization request) - per-request JSON   │
│                                                        │
│  Flow:                                                 │
│  App -> POST /v1/data/authz/allow {input: {...}}       │
│  OPA evaluates policies against (data + input)         │
│  Returns: {"result": true} or {"result": false}        │
│                                                        │
│  Deployment modes:                                     │
│  - Embedded library (Go applications)                  │
│  - Sidecar (K8s: one OPA per pod)                      │
│  - Daemon (centralized, shared by multiple services)   │
│  - Envoy plugin (external authorization filter)        │
│                                                        │
│  Bundle API: OPA polls a bundle server every N seconds │
│  for policy + data updates. Policy changes take effect │
│  without restarting the OPA process.                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA authorization call from Java**

```java
@Service
public class OpaAuthorizationService {

    private final RestTemplate rest;
    private final String opaUrl;

    public boolean isAuthorized(String userId,
                                 String resource,
                                 String action) {
        // Build OPA input document
        Map<String, Object> input = Map.of(
            "user_id", userId,
            "resource", resource,
            "action", action
        );
        Map<String, Object> body = Map.of("input", input);

        try {
            // POST to OPA's data API
            ResponseEntity<Map> response = rest.postForEntity(
                opaUrl + "/v1/data/authz/allow",
                body, Map.class);
            // OPA returns {"result": true/false}
            return Boolean.TRUE.equals(
                response.getBody().get("result"));
        } catch (Exception e) {
            // Fail closed: deny on OPA error
            log.error("OPA unreachable, denying request", e);
            return false;
        }
    }
}
```

**Example - Kubernetes admission control with OPA Gatekeeper**

```yaml
# ConstraintTemplate: no containers running as root
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8snoroot
spec:
  crd:
    spec:
      names:
        kind: K8sNoRoot
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8snoroot
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.runAsNonRoot != true
          msg := sprintf("Container %v must not run as root",
                          [container.name])
        }
---
# Apply constraint to all namespaces
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sNoRoot
metadata:
  name: require-non-root
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

---

*Authorization category: ATZ | Entry: ATZ-027 | v5.0*