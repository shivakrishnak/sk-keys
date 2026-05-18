---
id: ATZ-062
title: "Policy as Code Across Domains (Pattern Bridge)"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-026, ATZ-027, ATZ-053, ATZ-061
used_by: []
related: ATZ-053, ATZ-061
tags:
  - security
  - authorization
  - policy-as-code
  - pattern-bridge
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/authorization/policy-as-code-across-domains-pattern-bridge/
---

**TL;DR:** "Policy as Code" is not just an authorization pattern
- it is a cross-domain principle: infrastructure policy (Terraform
Sentinel, OPA/Conftest for k8s manifests), data governance
(row-level access policies), CI/CD gates (no deployment without
passing security scans), and API authorization are all instances
of the same pattern: express rules as code, test them, version
them, deploy them. The skill transfers directly across all domains.
OPA/Rego is the common language across all of them.

---

### Textbook Definition

Policy as Code (PaC) across domains is the recognition that
the same engineering discipline - encoding rules as executable,
testable, versionable code - applies to authorization policy
(who can access what), infrastructure policy (what cloud
configurations are permitted), compliance policy (what security
controls must be present), and data governance policy (what
data can be processed where). OPA (Open Policy Agent) is the
unifying platform: the same Rego language is used for Kubernetes
admission control, Terraform plan validation, CI/CD gate checks,
and runtime API authorization. The pattern bridge insight:
mastering policy language and the policy-as-code discipline
in one domain immediately transfers to all others.

---

### Cross-Domain Policy-as-Code

```
DOMAIN 1: API Authorization (runtime)
Tool: OPA sidecar
Policy: "Finance users may access /reports endpoint"
Test: opa test policies/authz/
Deploy: bundle server -> OPA agents

DOMAIN 2: Kubernetes Admission Control
Tool: OPA/Gatekeeper (Kubernetes webhook)
Policy: "All pods must have resource limits set"
       "No containers running as root (uid=0)"
Test: conftest test k8s/deployments/
Deploy: Gatekeeper policy, enforced on every kubectl apply

DOMAIN 3: Terraform / Infrastructure
Tool: OPA + conftest or Terraform Sentinel
Policy: "S3 buckets must not be public"
       "All VMs must be in approved regions"
Test: conftest verify terraform.plan.json
Deploy: CI gate (plan fails = PR blocked)

DOMAIN 4: CI/CD Gate
Tool: conftest + OPA
Policy: "Docker images must not have CRITICAL vulns"
       "All containers must use approved base images"
Test: conftest test Dockerfile
Deploy: CI step before build/push

COMMON STRUCTURE:
  Define: rules in Rego
  Input: context data (k8s manifest, Terraform plan, JWT)
  Output: allow | deny + reason
  Test: opa test (100% required before merge)
  Deploy: bundle / webhook / scan

SKILL TRANSFER:
Rego in API authz -> Rego in k8s admission -> same language
opa test in authz -> opa test in infra -> same workflow
Git PR for policies -> review in all domains -> same process
```

---

### Code Examples

**Example - Same OPA/Rego across API auth and k8s policy**

```rego
# DOMAIN 1: API Authorization (runtime)
# Evaluated by OPA sidecar on every API request
package api.authz

default allow = false

allow {
    input.principal.roles[_] == "admin"
}

allow {
    input.principal.roles[_] == "reader"
    input.method == "GET"
}
```

```rego
# DOMAIN 2: Kubernetes Admission Control
# Same Rego language, different input structure
# Gatekeeper runs this on every pod admission
package k8s.security

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container '%v' must run as non-root",
                    [container.name])
}

violation[{"msg": msg}] {
    container := input.review.object.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("Container '%v' missing CPU limit",
                    [container.name])
}
# opa test k8s/policies/ -v
# Same tooling: opa test, opa check, bundle build
```

```bash
# DOMAIN 3: Terraform plan validation (CI gate)
# conftest reads Terraform plan JSON, applies Rego policies
conftest test --policy policies/infra/ terraform.plan.json
# Policy: policies/infra/s3.rego
# Rule: S3 buckets must have block_public_access = true
# CI: if conftest fails -> PR blocked, no deployment

# Cross-domain skill: Rego + opa test + conftest
# works identically in all four domains
# Learn once, apply everywhere
```

---

*Authorization category: ATZ | Entry: ATZ-062 | v5.0*