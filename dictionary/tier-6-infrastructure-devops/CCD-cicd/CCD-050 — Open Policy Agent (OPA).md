---
layout: default
title: "Open Policy Agent (OPA)"
parent: "CI/CD"
nav_order: 50
permalink: /ci-cd/open-policy-agent-opa/
id: CCD-050
category: CI/CD
difficulty: ★★★
depends_on: Policy as Code, Security, Kubernetes
used_by: CI-CD, Kubernetes
related: Policy as Code, Sentinel (Terraform Policy), Gatekeeper
tags:
  - cicd
  - devops
  - security
  - advanced
  - kubernetes
---

# CCD-050 — Open Policy Agent (OPA)

⚡ **TL;DR —** OPA is a general-purpose, open-source policy engine that evaluates Rego policies against any JSON input to produce allow/deny decisions across infrastructure, APIs, and Kubernetes.

| Field | Value |
|-------|-------|
| **Depends on** | Policy as Code, Security, Kubernetes |
| **Used by** | CI-CD, Kubernetes |
| **Related** | Policy as Code, Sentinel (Terraform Policy), Gatekeeper |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every system that needs policy enforcement builds its own: the API gateway has custom auth middleware, Kubernetes admission uses a bespoke webhook, Terraform pipelines have shell script checks. Each is in a different language, with different test patterns, maintained by different teams, and none of them are auditable in a unified way.

**THE BREAKING POINT:** A policy change (e.g., new data residency requirement) must be applied to the API gateway, the K8s admission webhook, the CI pipeline, and the monitoring alerting rules — all separately, in different code, by different teams. Two systems implement the policy correctly. Two do not. A compliance incident occurs in one of the gaps.

**THE INVENTION MOMENT:** Decouple policy from the systems that enforce it. One language (Rego), one engine (OPA), one bundle server — deployed as a sidecar or service wherever decisions are needed. Systems query OPA; OPA owns the policy logic. Policy changes propagate centrally.

---

### 📘 Textbook Definition

**Open Policy Agent (OPA)** is a CNCF-graduated, open-source general-purpose policy engine that decouples policy decision-making from policy enforcement. It accepts structured data (JSON) as input, evaluates Rego policies against that data, and returns policy decisions. OPA is deployed as a service or library and integrates with Kubernetes (via Gatekeeper), API gateways, CI pipelines (via Conftest), microservices, and infrastructure-as-code tools.

---

### ⏱️ Understand It in 30 Seconds

**One line:** OPA is a universal policy decision engine — feed it JSON, get back allow/deny with reasons.

> Think of OPA as an airport security screening system. Every passenger (request) goes through the same checkpoints (policies) regardless of which airline or terminal they use. The rules are centralised and updated once. No airline maintains its own screening procedure.

**One insight:** OPA's power comes from **decoupling**: the system enforcing the decision (Kubernetes, your API, Terraform) does not contain any policy logic — it delegates the question "is this allowed?" to OPA, which answers based on versioned, testable Rego policies. Changing a policy requires no code change in the enforcing system.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A policy decision is a pure function: (policy, input, data) → decision.
2. Separating the decision function from the enforcement point enables independent evolution.
3. A declarative, side-effect-free language guarantees termination and safe evaluation in critical paths.
4. Policy decisions must be auditable — every decision must be explainable from policy + input alone.

**DERIVED DESIGN:** OPA implements Rego, a Datalog-derived logic programming language, as the policy language. The OPA engine evaluates Rego against a JSON input document and an optional context data document. Results are JSON. OPA exposes a REST API and an embedded Go library. Policies are loaded as bundles from a bundle server (OCI registry, S3, or file system) and refreshed on a configurable interval.

**THE TRADE-OFFS:**
**Gain:** Centralised, consistent, testable policy across heterogeneous systems. One policy change propagates everywhere via bundle update. Rego's logic model makes complex relational policies expressible in few lines.
**Cost:** Rego has a steep learning curve — its unification model is unfamiliar to engineers from imperative backgrounds. OPA adds a network hop (or library call) to the critical path of every decision. Debugging Rego requires the OPA REPL or tracing output.

---

### 🧪 Thought Experiment

**SETUP:** You need to enforce the same data residency policy (EU data must not be processed in US regions) across: your Kubernetes admission (which region a pod's node selector targets), your API gateway (which backend a request routes to), and your Terraform pipeline (which AWS region a resource is created in).

**WHAT HAPPENS WITHOUT OPA:** Three teams implement the rule in three different systems: Kubernetes admission webhook in Go, API gateway rule in Lua, Terraform check in Bash. Within three months, the Bash check is outdated, Lua rule has a bug for a new route pattern, and only the Go webhook is correct. The EU data residency requirement is enforced in 1 of 3 enforcement points.

**WHAT HAPPENS WITH OPA:** One Rego package (`data_residency.rego`) expresses the rule. Three systems call `POST /v1/data/data_residency/allow` with their respective JSON inputs. When the rule changes, one Rego file is updated, bundle is republished, all three enforcement points receive the update on next poll. Policy coverage is uniform.

**THE INSIGHT:** OPA's core value is not the policy language — it is the **architectural pattern of centralised policy decision making**. Once OPA is the decision point, you get uniform coverage, single-source-of-truth policy, and auditable decisions without changing enforcement code.

---

### 🧠 Mental Model / Analogy

> Think of OPA as a **Supreme Court for your infrastructure**. Lower courts (Kubernetes, API gateway, CI pipeline) bring their cases (requests) to the Supreme Court, which applies the same body of law (Rego policies) to every case. The lower courts do not interpret the law themselves — they defer to the court's ruling. When the law changes, it changes for all courts simultaneously.

- Supreme Court = OPA engine
- Body of law = Rego policy bundle
- Lower courts = enforcement points (Gatekeeper, API GW, Conftest)
- Cases = JSON input documents (K8s object, API request, Terraform plan)
- Ruling = OPA decision response (allow/deny + reasons)
- Law amendment = policy bundle update

Where this analogy breaks down: A Supreme Court ruling takes months; OPA bundle updates propagate in seconds. The volume of decisions (thousands per minute) is also far beyond any court.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
OPA is a program you ask "is this allowed?" — you describe a situation in JSON, OPA checks it against your rules, and tells you yes or no. You write the rules once; every system that needs to enforce them asks OPA instead of duplicating the logic.

**Level 2 — How to use it (junior developer):**
Run OPA as a sidecar in your Kubernetes cluster. Write a Rego policy that checks container specs. In Kubernetes, OPA Gatekeeper intercepts every `kubectl apply` and calls your policy with the resource as input. If the policy denies it, the apply is rejected with your error message. Use Conftest (OPA wrapper) in CI to check Terraform plans and Kubernetes manifests before they are applied.

**Level 3 — How it works (mid-level engineer):**
OPA exposes a REST API: `POST /v1/data/<package>/<rule>` with a JSON body `{"input": {...}}`. OPA evaluates the named rule in the named package and returns `{"result": true/false}` or a set of violation strings. Policies are loaded from a bundle: a gzipped tarball containing `.rego` files and a `manifest.json`. OPA polls the bundle server for updates on a configurable interval and hot-reloads without restart. Decision logs are streamed to a configured endpoint for audit purposes.

**Level 4 — Why it was designed this way (senior/staff):**
Rego is based on Datalog (a restricted form of Prolog) rather than a general-purpose language for two reasons. First, Datalog evaluation is guaranteed to terminate in polynomial time regardless of policy complexity — essential for a webhook with a 30ms budget. Second, Datalog's monotonic semantics (adding data never invalidates a previous true result) make policy reasoning tractable. The document model (everything is JSON; policy, input, and data are all documents) was chosen to make OPA system-agnostic: any system that can produce and consume JSON can integrate with OPA without a dedicated SDK. This is why OPA integrates equally well with Kubernetes, Envoy, Terraform, and custom applications.

---

### ⚙️ How It Works (Mechanism)

```
System (Kubernetes/API/CI)
    │  POST /v1/data/pkg/rule
    │  {"input": <JSON resource>}
    ▼
┌──────────────────────────────────────┐
│  OPA Engine                          │
│  ┌────────────┐  ┌─────────────────┐ │
│  │ policy.rego│  │ data.json       │ │
│  │ (rules)    │  │ (context/lookup)│ │
│  └─────┬──────┘  └────────┬────────┘ │
│        └────────┬─────────┘          │
│             Rego eval                │
│             (unification)            │
└──────────────┬───────────────────────┘
               │
               ▼
{"result": {"allow": true}}
     or
{"result": {"deny": ["reason1"]}}
```

**Key OPA deployment patterns:**

| Pattern | Use Case | Latency |
|---------|----------|---------|
| K8s admission (Gatekeeper) | Validate K8s objects | ~5ms per webhook call |
| Envoy external authz | API gateway AuthZ | ~1ms (local sidecar) |
| Conftest (CI) | Lint IaC/manifests | offline, no latency |
| OPA library (embedded) | Go/Node.js app-level | sub-millisecond |
| REST API | Any language, any system | ~2ms LAN |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes Terraform / K8s manifest
    │
    ▼
CI: conftest test ← YOU ARE HERE
    │  OPA evaluates policy against plan.json
    │  PASS: no violations
    ▼
PR merged → kubectl apply
    │
    ▼
Gatekeeper admission webhook called
    │  OPA evaluates ConstraintTemplate
    │  PASS: object allowed
    ▼
Pod scheduled → running
    │
    ▼
OPA decision log entry written:
  {timestamp, input, policy_version, result}
    │
    ▼
Compliance report queries decision logs:
  "Show all K8s admission denies last 30 days"
```

**FAILURE PATH:**
```
kubectl apply deployment.yaml
    │
    ▼
Gatekeeper calls OPA
    │  policy: no-privileged-containers
    │  input: securityContext.privileged=true
    ▼
DENY: "Privileged containers not allowed"
    │
    ▼
kubectl apply returns Error:
  admission webhook denied the request
    │
    ▼
Decision logged for audit
```

**WHAT CHANGES AT SCALE:**
At scale, OPA bundle management becomes critical: bundles must be versioned, signed, and staged (test bundles in staging, prod bundles in prod OPA instances). Decision log volume requires a streaming pipeline (Kafka → Elasticsearch) for query performance. OPA status API enables monitoring policy freshness across all instances. Partial evaluation (OPA compiles policies to allow inline evaluation in Envoy) eliminates the network hop for high-throughput API gateways.

---

### 💻 Code Example

**BAD — policy logic embedded in application code:**
```go
// BAD: policy logic in app; no central governance
func isAllowed(user User, resource Resource) bool {
  if user.Role == "admin" {
    return true
  }
  if resource.Owner == user.ID {
    return true
  }
  // ... scattered conditions, untestable
  return false
}
```

**GOOD — Rego policy + OPA query:**
```rego
# policies/authz.rego
package authz

import future.keywords.if
import future.keywords.contains

default allow := false

# Admins can do anything
allow if {
  input.user.role == "admin"
}

# Owners can access their own resources
allow if {
  input.user.id == input.resource.owner_id
  input.action == "read"
}

# Deny reasons for audit
deny contains msg if {
  not allow
  msg := sprintf(
    "User '%v' denied '%v' on resource '%v'",
    [input.user.id, input.action, input.resource.id]
  )
}
```

**Application query (Go):**
```go
// Query OPA via REST API
resp, err := http.Post(
  "http://opa:8181/v1/data/authz/allow",
  "application/json",
  strings.NewReader(fmt.Sprintf(
    `{"input": {"user": %s, "resource": %s,
     "action": "%s"}}`,
    userJSON, resourceJSON, action,
  )),
)
// Parse result.result: true/false
```

**Conftest CI usage:**
```bash
# Check Terraform plan against all policies
conftest test \
  --policy ./policies \
  --namespace main \
  plan.json

# Check K8s manifests
conftest test \
  --policy ./policies/k8s \
  deployment.yaml
```

---

### ⚖️ Comparison Table

| Feature | OPA | Kyverno | Sentinel | AWS IAM |
|---------|-----|---------|----------|---------|
| **Policy language** | Rego (Datalog) | YAML | HCL-like DSL | JSON |
| **Scope** | Universal (any JSON) | Kubernetes only | Terraform only | AWS only |
| **K8s admission** | Via Gatekeeper | Native | No | No |
| **CI integration** | Conftest | CLI | Terraform CLI | AWS CLI |
| **Decision logging** | Built-in | Kubernetes events | Audit logs | CloudTrail |
| **Learning curve** | High (Rego) | Low (YAML) | Medium | Medium |
| **CNCF graduated** | Yes | Yes (incubating) | No | No |
| **Testing support** | `opa test` | `kyverno test` | Mock data | Limited |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "OPA is only for Kubernetes" | OPA is a general-purpose engine. It runs as an API gateway sidecar (Envoy), in CI pipelines (Conftest), as a Go/Python library, and in any system that can make HTTP calls or embed the OPA library. |
| "Rego is similar to other languages" | Rego is logic programming (Datalog). Variables are unified, not assigned. `x == 1` is a constraint, not an assignment. Engineers used to imperative or functional languages need to relearn their mental model. |
| "OPA adds significant latency" | Running OPA as a local sidecar adds ~1–2ms per decision. Conftest runs offline with zero added latency. The network hop only matters when OPA runs as a remote service. |
| "Gatekeeper IS OPA" | Gatekeeper is a Kubernetes-specific controller that wraps OPA for admission control. OPA itself is a standalone engine with no Kubernetes dependency. |
| "OPA decisions are cached" | OPA evaluates every query against the current policy+data state. Caching decisions externally can introduce stale data issues; OPA itself does not cache query results by default. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Rego policy always returns `undefined` instead of deny**
**Symptom:** Policy never blocks anything; `deny` always empty even for clearly invalid input.
**Root Cause:** Rego's `undefined` result is distinct from `false`. If the policy package is not queried by the correct path, or the rule has a typo, OPA returns `undefined` rather than a deny set — which most callers treat as "allow".
**Diagnostic:**
```bash
# Debug in OPA REPL with trace
opa eval -d policies/ \
  -i test/bad_input.json \
  --explain full \
  "data.k8s_security.deny"

# Verify package name matches query path
head -3 policies/k8s_security.rego
# Should show: package k8s_security
```
**Fix:**
BAD — Add `default deny = false` and treat undefined as allow.
GOOD — Add `default deny := set()` for deny-set policies; add a unit test asserting the deny set is non-empty for known-bad inputs; treat `undefined` as a misconfiguration error, not an allow.
**Prevention:** Every policy has companion `_test.rego` files with positive (should deny) and negative (should allow) test cases. Run `opa test ./policies` in CI.

**Failure Mode 2: Bundle update lag leaves OPA running stale policies**
**Symptom:** A policy change is deployed but violations continue to slip through for several minutes.
**Root Cause:** OPA bundle polling interval is set to 60 seconds; the new bundle takes one full interval to propagate to all instances.
**Diagnostic:**
```bash
# Query OPA status API for bundle revision
curl -s http://opa:8181/v1/status \
  | jq '.bundles.main.active_revision'

# Compare with expected bundle revision from CI
# (should match immediately after deploy + poll interval)
```
**Fix:**
BAD — Decrease polling interval to 1 second globally.
GOOD — Implement bundle push notification: CI triggers an OPA reload webhook after publishing a new bundle; use `--set=bundles.main.polling.min_delay_seconds=5` for near-realtime propagation.
**Prevention:** Monitor bundle revision across OPA instances. Alert when any instance's revision lags behind the latest published revision by more than 2 polling cycles.

**Failure Mode 3: Gatekeeper webhook failure blocks all pod scheduling**
**Symptom:** All `kubectl apply` operations fail with "failed calling webhook: context deadline exceeded."
**Root Cause:** OPA Gatekeeper pods are down or unresponsive; `failurePolicy: Fail` causes all admission requests to reject.
**Diagnostic:**
```bash
kubectl get pods -n gatekeeper-system
kubectl describe validatingwebhookconfiguration \
  gatekeeper-validating-webhook-configuration \
  | grep -A2 failurePolicy

kubectl top pods -n gatekeeper-system
```
**Fix:**
BAD — Delete the webhook configuration to restore scheduling.
GOOD — Scale Gatekeeper replicas; fix the underlying OPA issue; for non-critical namespaces, switch `failurePolicy` to `Ignore` so cluster operations can continue during policy engine downtime.
**Prevention:** Run ≥3 Gatekeeper replicas with pod disruption budget. Set `failurePolicy: Ignore` for system namespaces. Implement health checks and auto-restart on OPA sidecar pods.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Policy as Code — the paradigm OPA implements
- Security — the domain providing the requirements OPA enforces
- Kubernetes — the primary deployment environment for OPA/Gatekeeper

**Builds On This (learn these next):**
- Gatekeeper — the Kubernetes operator that deploys OPA as an admission controller
- Conftest — the CLI tool that uses OPA to evaluate policies in CI pipelines
- Sentinel (Terraform Policy) — HashiCorp's alternative PaC engine for Terraform workflows

**Alternatives / Comparisons:**
- Kyverno — Kubernetes-native alternative to Gatekeeper; YAML-based, no Rego required
- Sentinel — HashiCorp-specific, tighter Terraform integration but narrower scope than OPA
- AWS IAM — managed cloud-native authorisation; not a general-purpose policy engine

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ General-purpose policy engine       │
│                │ using Rego to evaluate JSON input    │
│ PROBLEM        │ Policy logic scattered across       │
│                │ every system in its own language     │
│ KEY INSIGHT    │ Decouple decision from enforcement  │
│ USE WHEN       │ Kubernetes admission, API AuthZ, CI │
│ AVOID WHEN     │ Simple yes/no auth in a single app  │
│ TRADE-OFF      │ Centralised consistency vs Rego DSL │
│ ONE-LINER      │ Input JSON + Rego → allow/deny      │
│ NEXT EXPLORE   │ Gatekeeper, Conftest, Kyverno       │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(First Principles)** OPA uses Datalog-derived logic (Rego) rather than a Turing-complete language. What operational guarantees does this provide — and what class of policies is fundamentally inexpressible in Rego that would require a Turing-complete language?

2. **(Scale)** When OPA sits in the critical path of Kubernetes admission for 500 pod schedulings per minute, what architectural pattern (sidecar vs. central service, partial evaluation, caching) minimises added latency while preserving policy consistency?

3. **(System Interaction)** A policy decision logged by OPA differs from the decision applied by the enforcement point because the enforcement point cached the result. What design contract must exist between OPA and the enforcement system to prevent decision staleness from creating a compliance gap?
