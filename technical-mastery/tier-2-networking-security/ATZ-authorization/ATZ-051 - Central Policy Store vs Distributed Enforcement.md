---
id: ATZ-051
title: "Central Policy Store vs Distributed Enforcement"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-027, ATZ-030, ATZ-040, ATZ-046, ATZ-049
used_by: ATZ-052, ATZ-053, ATZ-054
related: ATZ-030, ATZ-049, ATZ-053
tags:
  - security
  - authorization
  - policy
  - distributed
  - architecture
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/authorization/central-policy-store-vs-distributed-enforcement/
---

⚡ **TL;DR** - Authorization architecture has two orthogonal
dimensions: where policies are stored and where they are
evaluated. Centralized policy store means a single source of
truth for policy definitions (one place to update, one place
to audit). Distributed enforcement means policies are evaluated
close to the resource (in-process or sidecar), not in a remote
PDP. The production-proven pattern: centralize storage (Git-
backed policy repo), distribute enforcement (OPA sidecar per
service). Never centralize both: remote PDP per request = latency
spike + SPOF.

---

### 📊 Entry Metadata

| #051 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-027 OPA, ATZ-030 Externalized Authz, ATZ-040 Distributed Authz, ATZ-046 Performance, ATZ-049 Microservices | |
| **Used by:** | ATZ-052, ATZ-053, ATZ-054 | |
| **Related:** | ATZ-030 Externalized Authz, ATZ-049 Microservices Fleet, ATZ-053 Policy-as-Code | |

---

### 📘 Textbook Definition

The central vs. distributed decision in authorization
architecture determines how policy logic is managed and where
access decisions are computed. Centralized enforcement means
all services call a single PDP cluster for every authorization
decision - guaranteeing consistency but adding network latency
and a critical SPOF. Distributed enforcement means policy logic
runs within each service (OPA sidecar, embedded library), with
periodic synchronization of policy bundles from a central store.
Policy Administration Point (PAP): always centralized (one source
of truth for policies). Policy Decision Point (PDP): distributed
(evaluated locally for performance). Policy Enforcement Point
(PEP): at each service boundary. Policy Information Point (PIP):
per-request attribute fetching, often from centralized sources.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│     Central Policy Store + Distributed Enforcement     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  CONTROL PLANE (centralized):                          │
│  Git repo -> CI: opa test -> bundle server             │
│  Bundle server: hosts versioned policy bundles         │
│  Policy changes: propagate within 30-60s               │
│                                                        │
│  DATA PLANE (distributed, per service):                │
│  OPA sidecar: polls bundle server every 30s            │
│  Service: POST localhost:8181/v1/data/authz/allow      │
│  Latency: 1-5ms (localhost, no network hop)            │
│  Bundle server unreachable: OPA uses cached bundle     │
│  OPA sidecar down: fail-closed (deny)                  │
│                                                        │
│  ALTERNATIVE PATTERNS:                                 │
│  1. Fully centralized PDP:                             │
│     All services -> one PDP cluster                    │
│     Latency: +50-200ms per request                     │
│     SPOF: PDP down = all services fail                 │
│     Use only for: low-traffic, high-stakes decisions   │
│                                                        │
│  2. Fully distributed (no central store):              │
│     Policy code deployed WITH service                  │
│     Latency: 0ms overhead                              │
│     Problem: policy drift, no single audit point       │
│     No way to enforce org-wide policy changes          │
│                                                        │
│  3. Hybrid (recommended):                              │
│     Central PAP (Git) + bundle distribution            │
│     OPA sidecar per service (local eval)               │
│     Central decision log aggregation for audit         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA bundle server with versioned policies**

```bash
# Policy repo structure:
# policies/
#   authz/
#     allow.rego          <- main allow rule
#     data.json           <- static reference data
#   tests/
#     allow_test.rego     <- unit tests

# CI pipeline: build bundle and push to bundle server
# opa build -b policies/ -o bundle-v1.2.0.tar.gz
# opa test policies/ (must pass before bundle is published)

# Bundle server config for OPA agents:
# bundles.authz.resource = /bundles/authz/bundle.tar.gz
# bundles.authz.polling.min_delay_seconds = 30
# bundles.authz.polling.max_delay_seconds = 60

# OPA agent pulls new bundle within 30-60 seconds
# Old policy: cached in OPA memory until new bundle pulled
# Policy rollback: publish previous bundle version
# Emergency: publish deny-all bundle if compromised

# Check current bundle version loaded by OPA:
curl http://localhost:8181/v1/bundles/authz
# Returns: {"result":{"revision":"v1.2.0","active":true}}
```

---

*Authorization category: ATZ | Entry: ATZ-051 | v5.0*