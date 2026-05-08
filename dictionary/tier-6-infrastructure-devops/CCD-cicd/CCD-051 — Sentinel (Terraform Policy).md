---
layout: default
title: "Sentinel (Terraform Policy)"
parent: "CI/CD"
nav_order: 51
permalink: /ci-cd/sentinel-terraform-policy/
id: CCD-051
category: CI/CD
difficulty: ★★★
depends_on: Policy as Code, Terraform Cloud  Enterprise, Terraform Overview
used_by: CI-CD
related: Open Policy Agent (OPA), Policy as Code, Terraform Cloud  Enterprise
tags:
  - cicd
  - devops
  - security
  - advanced
---

# CCD-051 — Sentinel (Terraform Policy)

⚡ **TL;DR —** Sentinel is HashiCorp's policy-as-code framework embedded in Terraform Cloud and Enterprise that enforces organisational rules on infrastructure before `terraform apply` executes.

| Field | Value |
|-------|-------|
| **Depends on** | Policy as Code, Terraform Cloud / Enterprise, Terraform Overview |
| **Used by** | CI-CD |
| **Related** | Open Policy Agent (OPA), Policy as Code, Terraform Cloud / Enterprise |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Terraform is used across 20 teams. Each team applies their own tagging conventions, chooses their own instance sizes, and occasionally creates publicly accessible S3 buckets. A central platform team tries to enforce standards through documentation and Slack reminders. Non-compliance is discovered in quarterly audits, months after the resource was created.

**THE BREAKING POINT:** A publicly accessible RDS instance is created by a developer who didn't read the security guidelines. It is discovered in a penetration test six weeks later. The remediation requires a maintenance window, data migration, and a security incident report. The cost of post-hoc enforcement is 100× the cost of pre-apply prevention.

**THE INVENTION MOMENT:** If Terraform Cloud manages every apply, then the platform can intercept every apply and evaluate it against policy before it executes. Sentinel is the engine that makes the interception configurable, versioned, and testable — turning Terraform Cloud into an enforced governance layer, not just a remote execution environment.

---

### 📘 Textbook Definition

**Sentinel** is HashiCorp's embedded policy-as-code framework available in Terraform Cloud and Terraform Enterprise. It evaluates policy files written in the Sentinel language (an HCL-adjacent, imperative DSL) against Terraform plan data, state, configuration, and run metadata at three enforcement levels: `advisory` (log only), `soft-mandatory` (blockable by override), and `hard-mandatory` (always enforced, no override). Sentinel integrates natively into the Terraform run lifecycle and requires no external tooling.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Sentinel lets platform teams encode "what Terraform is allowed to do" and enforces it at every apply — natively, inside Terraform Cloud.

> Think of Sentinel as the loan approval policy system at a bank. A customer (engineer) submits a loan application (Terraform plan). The bank's policy system (Sentinel) automatically checks every application against credit rules, risk limits, and compliance requirements before a human ever sees it — no exceptions, no discretion, fully auditable.

**One insight:** Sentinel's three enforcement levels — `advisory`, `soft-mandatory`, `hard-mandatory` — are not just severity labels. They are a **policy rollout workflow**: introduce a policy in advisory mode to measure its impact, promote to soft-mandatory to enable guided self-service with overrides, then hard-mandatory when all teams are compliant.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every Terraform apply is a state transition with security and compliance implications.
2. The Terraform plan is the complete, machine-readable description of that transition before it executes.
3. Evaluating policy against the plan (not the resulting state) is the only way to prevent violations — post-state evaluation is remediation, not prevention.
4. Enforcement level must be tunable during rollout; hard blocking before teams understand the policy creates friction that causes workarounds.

**DERIVED DESIGN:** Terraform Cloud captures the plan as structured data (accessible as `tfplan`, `tfconfig`, `tfstate`, `tfrun` imports in Sentinel). Sentinel policies are evaluated against these imports after plan, before apply. The result determines whether the run proceeds. Policy sets are attached to workspaces or applied globally; they are versioned in a VCS repository and auto-synced.

**THE TRADE-OFFS:**
**Gain:** Zero-gap enforcement on all Terraform applies processed by Terraform Cloud/Enterprise. Native integration — no external webhook, no additional tool, no network hop. Audit trail included.
**Cost:** Sentinel is HashiCorp proprietary (not open source). Requires Terraform Cloud Team plan or Terraform Enterprise. Sentinel language is a custom DSL — teams must learn it. Policies are scoped to Terraform only; cross-platform enforcement requires OPA.

---

### 🧪 Thought Experiment

**SETUP:** Your company requires all AWS resources to be tagged with `environment`, `owner`, and `cost-centre` tags. This is enforced through a documented standard and quarterly tag-compliance audits.

**WHAT HAPPENS WITHOUT SENTINEL:** Three new engineers join the team this quarter. They are not aware of the tagging requirement. They create 15 untagged resources across five workspaces. The quarterly audit flags the violations. Remediation requires identifying each resource, applying tags manually, and submitting a corrective action report. Total cost: 2 days of engineer time, a compliance finding, and a slap on the wrist.

**WHAT HAPPENS WITH SENTINEL:** A `require-tags.sentinel` policy is attached to all workspaces in `hard-mandatory` mode. The three new engineers' `terraform apply` runs are blocked with: "FAIL: EC2 instance 'app-server' missing required tag 'owner'." They fix the tags in the same PR, before any resource is created. Compliance: 0 violations. Remediation cost: 0.

**THE INSIGHT:** Sentinel's value is not in the strictness of enforcement — it is in the **point in the lifecycle** where enforcement occurs. Blocking at plan time is prevention. Discovering at audit time is remediation. Prevention is always cheaper.

---

### 🧠 Mental Model / Analogy

> Think of Sentinel as **customs and border control at an airport**. Every passenger and piece of luggage (Terraform plan) is inspected before boarding. Prohibited items (policy violations) are confiscated before the flight (apply). The rules (Sentinel policies) are defined by the national authority (platform team), applied consistently by officers (Terraform Cloud), and fully logged. Some items trigger advisory notes; others ground the plane.

- Customs officers = Terraform Cloud Sentinel evaluation engine
- Prohibited items list = Sentinel policy files
- Passenger manifest = Terraform plan (`tfplan` import)
- Confiscation = hard-mandatory policy deny
- Conditional boarding = soft-mandatory with override
- Advisory note = advisory enforcement level
- Boarding pass = successful apply

Where this analogy breaks down: Customs rules change slowly; Sentinel policies may change weekly as new infrastructure standards are introduced, requiring a fast policy review cycle.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Sentinel is a rule system built into Terraform Cloud that automatically checks every Terraform plan against your company's rules before anything is actually created. If a rule is broken, the plan is blocked.

**Level 2 — How to use it (junior developer):**
You write a `.sentinel` file with rules like "all EC2 instances must use approved AMIs." You attach this file to your Terraform Cloud workspace as a policy set. When anyone runs `terraform apply` in that workspace, Terraform Cloud evaluates your policy against the plan. If the rule fails, the apply is blocked with a clear error message. You can test policies locally with `sentinel test` before publishing.

**Level 3 — How it works (mid-level engineer):**
Sentinel policies are evaluated after Terraform generates a plan and before `apply` executes. The policy accesses plan data through structured imports: `tfplan/v2` (planned resource changes), `tfconfig/v2` (configuration values), `tfstate/v2` (current state), and `tfrun` (run metadata). Policy files define `main` as the root rule; returning `false` from `main` fails the policy. Policy sets are version-controlled in a VCS repo and synced to Terraform Cloud. Enforcement levels control whether a failed policy blocks the run (`hard-mandatory`), prompts for override (`soft-mandatory`), or only logs (`advisory`).

**Level 4 — Why it was designed this way (senior/staff):**
Sentinel's imperative DSL (unlike OPA's logic programming Rego) was designed for approachability — engineers familiar with Go or Python can read and write Sentinel policies without learning a new paradigm. The trade-off is that Sentinel lacks Rego's formal completeness guarantees and is harder to reason about for complex relational policies. The three-tier enforcement model was an intentional product decision: platforms teams routinely need a "warn before block" transition period when rolling out new policies to existing workspaces with non-compliant resources. The mock data system (testing with simulated plan JSON) enables policy CI without needing real Terraform runs, solving the "how do you test your tests" problem for policy-as-code.

---

### ⚙️ How It Works (Mechanism)

```
terraform plan (remote run in TFC)
    │
    ▼
┌──────────────────────────────────────┐
│  Terraform Cloud                     │
│  generates plan                      │
│        │                             │
│        ▼                             │
│  ┌─────────────────────────────────┐ │
│  │  Sentinel Evaluation            │ │
│  │  imports: tfplan, tfconfig,     │ │
│  │           tfstate, tfrun        │ │
│  │  policies: require-tags.sentinel│ │
│  │           approved-amis.sentinel│ │
│  │  evaluate main rule per policy  │ │
│  └────────────┬────────────────────┘ │
│               │                      │
│         ┌─────┴──────┐               │
│         │            │               │
│       PASS          FAIL             │
│         │            │               │
│         ▼            ▼               │
│    apply allowed  blocked/override   │
└──────────────────────────────────────┘
```

**Enforcement level behaviour:**

| Level | On FAIL | Override? | Use Case |
|-------|---------|-----------|----------|
| `advisory` | Log, proceed | N/A | Rollout: observe impact |
| `soft-mandatory` | Block run | Yes (admin) | Rollout: guided compliance |
| `hard-mandatory` | Block run | No | Production: enforce always |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
git push → VCS webhook → TFC run triggered
    │
    ▼
terraform init + plan ← YOU ARE HERE
    │  plan captured as tfplan JSON
    ▼
Sentinel evaluation (all attached policies)
    │
    │  require-tags: PASS
    │  approved-amis: PASS
    │  cost-limit ($500/mo): PASS
    ▼
Plan approved → apply queued
    │  (manual or auto-apply)
    ▼
terraform apply executes
    │
    ▼
State written → audit log: all policies PASS
```

**FAILURE PATH:**
```
Sentinel evaluation:
  approved-amis: FAIL
    EC2 instance uses ami-00000000 (not in list)
    enforcement: hard-mandatory
    │
    ▼
Run blocked — apply cannot proceed
    │
    ▼
Engineer notified: "Update AMI to approved list"
    │
    ▼
Code fixed → new run triggered → PASS → apply
```

**WHAT CHANGES AT SCALE:**
At scale, policy sets are organised by scope: global policy sets apply to all workspaces; team-scoped sets apply to a subset. Policy set versioning enables blue-green policy rollout (new policy set version in advisory mode while old hard-mandatory set remains active). Sentinel Remote Eval allows policies to call external HTTP APIs for dynamic data (e.g., query an approved AMI list from an internal registry rather than hardcoding it).

---

### 💻 Code Example

**BAD — no enforcement, documentation-only standard:**
```hcl
# BAD: tagging standard exists only in Confluence
# No automated check; violations found in quarterly audit
resource "aws_instance" "app" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  # Missing required tags — not caught until audit
}
```

**GOOD — Sentinel policy enforcing required tags:**
```python
# policies/require-tags.sentinel
import "tfplan/v2" as tfplan

# Required tags for all AWS resources
required_tags = ["environment", "owner", "cost-centre"]

# Get all AWS resources from the plan
aws_resources = filter tfplan.resource_changes as _, rc {
  rc.mode is "managed" and
  rc.type matches "aws_" and
  rc.change.actions contains "create"
}

# Check each resource has all required tags
violations = filter aws_resources as _, rc {
  tags = rc.change.after.tags else {}
  any required_tags as tag {
    not tags[tag]
  }
}

# Collect violation messages
msgs = map violations as _, rc {
  "Resource '${rc.address}' missing required tags. " +
  "Required: ${required_tags}"
}

# Main rule
main = rule {
  length(violations) is 0
} else {
  print(msgs)
  false
}
```

**Mock test data (sentinel test):**
```json
{
  "mock": {
    "tfplan/v2": {
      "resource_changes": [{
        "address": "aws_instance.app",
        "mode": "managed",
        "type": "aws_instance",
        "change": {
          "actions": ["create"],
          "after": {
            "tags": {
              "environment": "prod",
              "owner": "team-platform"
            }
          }
        }
      }]
    }
  }
}
```

---

### ⚖️ Comparison Table

| Feature | Sentinel | OPA/Conftest | Checkov | Kyverno |
|---------|----------|--------------|---------|---------|
| **Scope** | Terraform only | Universal JSON | IaC static | K8s only |
| **Language** | Sentinel DSL | Rego | YAML/Python | YAML |
| **Enforcement point** | TFC/TFE apply gate | CI, K8s admission | CI static scan | K8s admission |
| **3-tier enforcement** | Yes (native) | Manual impl | No | No |
| **Mock testing** | Built-in | `opa test` | Limited | `kyverno test` |
| **Open source** | No (proprietary) | Yes (CNCF) | Yes | Yes (CNCF) |
| **Remote data calls** | Yes (Remote Eval) | Yes (OPA HTTP) | No | Limited |
| **Requires Terraform Cloud** | Yes | No | No | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Sentinel works with open-source Terraform" | Sentinel requires Terraform Cloud (Team plan or above) or Terraform Enterprise. It is not available in the open-source `terraform` CLI. Use Conftest+OPA or Checkov for local/open-source enforcement. |
| "soft-mandatory means the policy doesn't matter" | Soft-mandatory blocks the run unless an authorised user explicitly overrides. The override is logged. It is a real gate with an escape valve — not a suggestion. |
| "Sentinel policies run after apply" | Sentinel runs after plan generation, before apply. It is prevention, not detection. Post-state verification is a separate concern handled by Terraform audit logs or AWS Config. |
| "Sentinel replaces OPA" | They serve different scopes. Sentinel enforces Terraform-specific policies natively inside TFC. OPA enforces policies across any system that can produce JSON. Many organisations use both. |
| "Policy test mocks must match production plans exactly" | Mock data only needs to cover the fields your policy accesses. Minimal mocks are faster to write and easier to maintain. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Policy blocks all runs after an approved AMI list update**
**Symptom:** All workspace runs fail immediately after platform team updates the approved AMI list in a `hard-mandatory` Sentinel policy.
**Root Cause:** Policy update promoted directly to hard-mandatory; existing workspaces use AMIs that were approved under the old list but are not in the new list.
**Diagnostic:**
```bash
# In Terraform Cloud UI:
# Settings → Policy Sets → [set] → Policy Checks
# Identify which AMI IDs are triggering violations

# Or via API:
curl -H "Authorization: Bearer $TFC_TOKEN" \
  "https://app.terraform.io/api/v2/runs/${RUN_ID}/\
policy-checks" | jq '.data[].attributes'
```
**Fix:**
BAD — Remove the AMI restriction temporarily to unblock teams.
GOOD — Roll back to the previous policy set version; introduce new AMI requirements in `advisory` mode first; give teams a migration window (e.g., 2 sprints) to update AMIs; then promote to `soft-mandatory`, then `hard-mandatory`.
**Prevention:** Always introduce new restrictive policies in `advisory` mode. Monitor advisory violations before promoting. Use policy set versioning with staged rollout.

**Failure Mode 2: Sentinel policy passes but actual resource violates intent**
**Symptom:** Sentinel reports all policies passing, but a resource reaches production with a configuration the policy was designed to block.
**Root Cause:** Policy checks `after` values in `tfplan` but the violation is in a nested attribute (`tags` in a resource block vs. `tags` in an inline sub-resource). The nested attribute is not covered by the policy path.
**Diagnostic:**
```bash
# Export the actual plan JSON and inspect structure
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan \
  | jq '.resource_changes[] | select(.type=="aws_instance")'
# Find where tags actually appear in the JSON tree
```
**Fix:**
BAD — Add a broader wildcard check.
GOOD — Navigate the exact JSON path from the plan export; add a unit test with a plan JSON that matches the failing pattern; fix the Sentinel path expression to reach the nested attribute.
**Prevention:** Always validate Sentinel paths against real plan JSON exports, not documentation. Add test cases for nested attribute patterns.

**Failure Mode 3: Sentinel Remote Eval call times out and blocks all applies**
**Symptom:** Terraform runs hang at policy evaluation step; timeout after 30 seconds; all runs blocked.
**Root Cause:** Sentinel policy uses Remote Eval to call an internal service for dynamic data (approved AMI list). The internal service is unreachable during a network incident.
**Diagnostic:**
```bash
# Sentinel policy run logs in TFC UI show:
# "Error: HTTP request timed out after 30s"
# Check internal service health:
curl -s https://internal-ami-registry/health
```
**Fix:**
BAD — Remove the Remote Eval call to unblock runs.
GOOD — Implement a fallback: if Remote Eval fails, Sentinel policy falls back to a hardcoded allow-list or returns advisory (not hard-mandatory) to allow runs to proceed. Add circuit-breaker logic.
**Prevention:** Remote Eval dependencies should be designed for high availability. Cache the remote data with a configurable TTL in the Sentinel policy. Consider inlining the allowed-values list and syncing it via a scheduled pipeline rather than a real-time call.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Policy as Code — the paradigm Sentinel implements within the HashiCorp ecosystem
- Terraform Cloud / Enterprise — the runtime environment that executes Sentinel policies
- Terraform Overview — the infrastructure tool whose plans Sentinel evaluates

**Builds On This (learn these next):**
- Open Policy Agent (OPA) — the universal alternative for multi-system policy enforcement
- Conftest — CLI tool for evaluating OPA policies against Terraform plans in CI (without TFC)
- Terraform Compliance — BDD-style Terraform policy testing for open-source workflows

**Alternatives / Comparisons:**
- OPA/Conftest — open-source, language-agnostic, not limited to Terraform or HashiCorp
- Checkov — static analysis for IaC, no enforcement enforcement level model
- AWS Config Rules — runtime state enforcement; post-deploy, not pre-apply

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ HashiCorp policy engine embedded    │
│                │ in Terraform Cloud / Enterprise      │
│ PROBLEM        │ Terraform creates non-compliant     │
│                │ resources before anyone notices      │
│ KEY INSIGHT    │ Enforce at plan time, not audit time│
│ USE WHEN       │ TFC/TFE with org-wide IaC standards │
│ AVOID WHEN     │ Open-source Terraform workflows     │
│ TRADE-OFF      │ Native TF integration vs proprietary│
│ ONE-LINER      │ Plan check → pass/block/override    │
│ NEXT EXPLORE   │ OPA, Conftest, Terraform Compliance │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** Sentinel's three enforcement levels (advisory → soft-mandatory → hard-mandatory) represent a rollout workflow. What metric would you use to decide when a policy is ready to promote from advisory to hard-mandatory — and what is the risk of promoting too early vs. too late?

2. **(System Interaction)** A Sentinel policy calls Remote Eval to retrieve a dynamic approved AMI list from an internal registry. The registry has a 99.9% SLA. What is the probability that a Sentinel policy relying on this service will introduce a blocking failure in a team running 500 Terraform applies per month — and how does that change your reliability design?

3. **(Scale)** With 200 Terraform workspaces across 30 teams, you have 50 Sentinel policy files. How would you structure policy sets to avoid duplication while giving individual teams the ability to extend (but not override) the global baseline policy?
