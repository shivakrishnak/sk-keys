---
version: 1
layout: default
title: "Terraform Sentinel Policy"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /ci-cd/terraform-sentinel-policy/
id: CCD-069
category: CI/CD
difficulty: ★★★
depends_on: Sentinel (Terraform Policy), Terraform Cloud  Enterprise
used_by: CI-CD
related: Sentinel (Terraform Policy), Open Policy Agent (OPA), Policy as Code
tags:
  - cicd
  - devops
  - security
  - advanced
---

# CCD-069 - Terraform Sentinel Policy

⚡ **TL;DR -** Terraform Sentinel policies enforce compliance rules on infrastructure plans before apply, blocking non-compliant changes using a programmable policy-as-code framework.

| Field | Value |
|---|---|
| **Depends on** | Sentinel (Terraform Policy), Terraform Cloud  Enterprise |
| **Used by** | CI-CD |
| **Related** | Sentinel (Terraform Policy), Open Policy Agent (OPA), Policy as Code |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every Terraform apply goes directly to infrastructure. A junior engineer deploys an S3 bucket with `acl = "public-read"`. A developer provisions a production instance as `t2.micro` instead of the required `m5.large`. A configuration creates an RDS instance without encryption. The policy exists in a wiki somewhere - but Terraform doesn't know about it.

**THE BREAKING POINT:** A compliance audit reveals 12 S3 buckets have public access enabled and 8 RDS instances lack encryption. All were created via Terraform. The IaC pipeline had no guardrails. The engineers didn't violate policy intentionally - they just didn't know.

**THE INVENTION MOMENT:** Sentinel injects a policy evaluation step between `terraform plan` and `terraform apply`. Policies are code. They're version-controlled, tested, and enforced automatically. Non-compliant plans are blocked before infrastructure changes.

---

### 📘 Textbook Definition

**Terraform Sentinel** is HashiCorp's policy-as-code framework integrated into Terraform Cloud and Terraform Enterprise. Sentinel policies are written in the Sentinel language (a domain-specific, Go-like language) and are evaluated against Terraform plan data before an apply is permitted. Policies have three enforcement levels: `advisory` (warn only), `soft-mandatory` (can be overridden by privileged users), and `hard-mandatory` (cannot be overridden). Policies are organized into policy sets and applied to workspaces.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Sentinel policies automatically block Terraform applies that violate your infrastructure compliance rules.

> Sentinel is like a customs officer between plan and apply: every plan is inspected against a rulebook before the "shipment" (infrastructure change) is allowed through.

**One insight:** Sentinel operates on the **plan data**, not on running infrastructure. It catches non-compliance before any resource is created or modified - at the fastest, cheapest point to fix a compliance issue: before it's real.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Sentinel evaluates the plan JSON - the same data `terraform show -json` produces.
2. Policies are evaluated after plan, before apply.
3. `hard-mandatory` policies cannot be overridden; they're absolute enforcement gates.
4. Policies can access resource types, attributes, planned changes, and provider information.

**DERIVED DESIGN:** A Sentinel policy imports `tfplan/v2` (the plan data), navigates to the resource type of interest, checks attributes against rules, and returns `true` (compliant) or `false` (blocked). The policy engine runs all policies in the applicable policy set and reports violations.

**THE TRADE-OFFS:**
**Gain:** Automated compliance enforcement; catch violations before they're real; audit evidence of policy checks.
**Cost:** Sentinel is Terraform Cloud/Enterprise only; Sentinel language has a learning curve; complex policies require testing infrastructure.

---

### 🧪 Thought Experiment

**SETUP:** Your organization's security policy requires all S3 buckets to have `block_public_acls = true`. There are 5 teams deploying buckets.

**WHAT HAPPENS WITHOUT SENTINEL:** Policy is documented in a wiki. Teams create buckets. Some engineers read the wiki; some don't. Six months later, 3 of the 5 teams have compliant buckets; 2 don't. A pentest finds the public bucket. Remediation takes 2 weeks.

**WHAT HAPPENS WITH SENTINEL:** A `hard-mandatory` Sentinel policy checks every plan for `aws_s3_bucket_public_access_block` resources. If the resource is missing or `block_public_acls = false`, the apply is blocked. Engineers see: `Policy check failed: S3 public access not blocked`. They fix the HCL before applying. Zero non-compliant buckets reach production.

**THE INSIGHT:** Sentinel moves compliance from a post-hoc audit finding to a pre-apply enforcement gate. The cost of compliance drops from "remediation after discovery" to "fix before merge."

---

### 🧠 Mental Model / Analogy

> Sentinel is like a building inspector who must sign off on every construction project before the walls go up: the architect submits plans (terraform plan), the inspector checks against building codes (Sentinel policies), and only approved plans get built (terraform apply). Hard-mandatory codes cannot be waived; soft-mandatory codes can be overridden by the head of planning (privileged user).

- Architect's plans → terraform plan JSON
- Building inspector → Sentinel policy evaluation
- Building codes → Sentinel policy rules
- Approval/rejection → pass/fail verdict
- Head of planning override → soft-mandatory override

Where this analogy breaks down: unlike a physical building inspector, Sentinel can check thousands of configurations simultaneously and never misses a rule - there's no human fatigue or inconsistency.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Sentinel is a compliance checker that runs automatically between Terraform's plan and apply steps. It blocks deployments that violate your organization's rules.

**Level 2 - How to use it (junior developer):** Policies are written in the Sentinel language. They import the plan data (`tfplan/v2`), navigate to the resources they care about, check attributes, and return true/false. Policies are grouped into policy sets and applied to Terraform Cloud workspaces.

**Level 3 - How it works (mid-level engineer):** After `terraform plan` generates a plan in Terraform Cloud, the plan JSON is passed to the Sentinel evaluation engine. Each applicable policy is evaluated. A `hard-mandatory` failure blocks the apply immediately. A `soft-mandatory` failure blocks apply unless a privileged team member overrides. The result is logged for audit.

**Level 4 - Why it was designed this way (senior/staff):** Sentinel's position in the workflow (post-plan, pre-apply) is critical. Post-plan means all resource attributes and planned changes are known - Sentinel can make rich compliance decisions. Pre-apply means no real infrastructure is affected by a non-compliant plan. The three enforcement levels (advisory/soft/hard) give organizations a graduated rollout path: start with advisory to understand violations, then escalate to hard-mandatory once teams are trained.

---

### ⚙️ How It Works (Mechanism)

**Sentinel workflow in Terraform Cloud:**
```
1. Pull request → Terraform Cloud triggers plan
2. Plan JSON generated
3. Sentinel policies in applicable policy sets are evaluated
4. Policy results:
   - All pass → Apply allowed
   - Soft-mandatory fail → Apply blocked; override available
   - Hard-mandatory fail → Apply blocked; no override
5. Results logged to audit trail
```

**Policy imports:**
- `import "tfplan/v2"` - plan data (resource changes)
- `import "tfconfig/v2"` - configuration (HCL values)
- `import "tfstate/v2"` - current state
- `import "tfrun"` - run metadata (workspace, trigger)

---

### 🔄 The Complete Picture - End-to-End Flow

**SENTINEL ENFORCEMENT FLOW:**
```
  terraform plan → plan JSON
           │
  Terraform Cloud: Policy Check
           │
  For each policy in policy set:
  ┌─────────────────────────────┐
  │ Sentinel evaluates policy   │← YOU ARE HERE
  │ against plan JSON           │
  │                             │
  │ Result: PASS or FAIL        │
  └─────────────────────────────┘
           │
  All PASS → Apply button available
           │
  Soft-mandatory FAIL →
    Blocked; admin can override
           │
  Hard-mandatory FAIL →
    Blocked; no override possible
    Engineer must fix HCL + re-plan
```

**FAILURE PATH:** Policy has a bug - it blocks all plans because of a logic error. CI is fully blocked. Fix requires updating the policy, which must go through its own review and deployment process. Always test policies with mock data before applying to workspaces.

**WHAT CHANGES AT SCALE:** Global policy sets apply across all workspaces. Team-specific policy sets can allow exceptions. Policy-as-code repos use the same PR review process as application code. Sentinel Simulator allows local policy testing without a full Terraform Cloud workflow.

---

### 💻 Code Example

```python
# --- enforce-s3-public-access-blocked.sentinel ---
# Hard-mandatory: all S3 buckets must block public access

import "tfplan/v2" as tfplan

# Get all planned aws_s3_bucket_public_access_block resources
public_access_blocks = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_s3_bucket_public_access_block" and
  (rc.change.actions contains "create" or
   rc.change.actions contains "update")
}

# Get all planned aws_s3_bucket resources
s3_buckets = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_s3_bucket" and
  (rc.change.actions contains "create" or
   rc.change.actions contains "update")
}

# Rule: every S3 bucket must have a public access block
# with all flags set to true
check_public_access = rule {
  all s3_buckets as _, bucket {
    # Find the corresponding public access block
    any public_access_blocks as _, pab {
      pab.change.after.bucket is bucket.change.after.bucket and
      pab.change.after.block_public_acls is true and
      pab.change.after.block_public_policy is true and
      pab.change.after.ignore_public_acls is true and
      pab.change.after.restrict_public_buckets is true
    }
  }
}

# Main rule
main = rule {
  check_public_access
}
```

```python
# --- enforce-instance-types.sentinel ---
# Soft-mandatory: approved EC2 instance types only

import "tfplan/v2" as tfplan

approved_types = [
  "t3.micro", "t3.small", "t3.medium",
  "m5.large", "m5.xlarge", "m5.2xlarge",
  "r6g.large", "r6g.xlarge",
]

ec2_instances = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_instance" and
  rc.change.actions contains "create"
}

check_instance_types = rule {
  all ec2_instances as _, inst {
    inst.change.after.instance_type in approved_types
  }
}

# Print violation details for each non-compliant instance
violations = filter ec2_instances as addr, inst {
  inst.change.after.instance_type not in approved_types
}

main = rule {
  if not check_instance_types {
    print("Non-compliant instance types found:")
    for violations as addr, inst {
      print("  ", addr, ":", inst.change.after.instance_type)
    }
    false
  } else {
    true
  }
}
```

```hcl
# Policy set configuration (sentinel.hcl)
policy "enforce-s3-public-access-blocked" {
  source            = "./enforce-s3-public-access-blocked.sentinel"
  enforcement_level = "hard-mandatory"
}

policy "enforce-instance-types" {
  source            = "./enforce-instance-types.sentinel"
  enforcement_level = "soft-mandatory"
}
```

---

### ⚖️ Comparison Table

| Feature | Sentinel | OPA (Rego) | AWS Config Rules | Custom CI Checks |
|---|---|---|---|---|
| **Language** | Sentinel DSL | Rego | JSON / Lambda | Any |
| **Integration** | Terraform Cloud/Enterprise | Any (Terraform/K8s) | AWS-native | Bespoke |
| **Plan access** | ✅ Native | ✅ tfplan JSON | ❌ Post-deploy | ✅ tfplan JSON |
| **Enforcement levels** | 3 levels | Policy-defined | Detect only | Custom |
| **Audit trail** | ✅ Built-in | Policy-defined | ✅ AWS | Custom |
| **Cost** | TF Cloud/Enterprise | Open source | AWS Config cost | Engineering time |
| **Best for** | Terraform Cloud users | Multi-tool governance | AWS-centric | Custom workflows |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Sentinel works with open-source Terraform" | Sentinel is only available in Terraform Cloud and Terraform Enterprise. Open-source Terraform does not include it. |
| "Hard-mandatory policies can be overridden in emergencies" | No. Hard-mandatory policies require HCL fix + re-plan. For break-glass scenarios, use soft-mandatory with a privileged override role. |
| "Sentinel policies test all resources in state" | By default, Sentinel only evaluates *planned changes* in the current run, not all resources in state. Use `tfstate/v2` to evaluate existing resources. |
| "Passing Sentinel means the configuration is secure" | Sentinel only enforces the rules you've written. Gaps in policy coverage mean gaps in enforcement. |
| "OPA is a drop-in replacement for Sentinel" | OPA uses a different language (Rego) and integrates differently. Both are policy-as-code, but the toolchains and Terraform integration patterns differ significantly. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Policy Blocks All Plans Due to Bug**
- **Symptom:** All workspace plans fail Sentinel checks; no plans can be applied
- **Root Cause:** Sentinel policy has a logic error (e.g. `all` on empty set evaluates to `true` in some contexts)
- **Diagnostic:** Use Sentinel CLI with mock data to reproduce:
```bash
sentinel apply -trace enforce-s3-blocked.sentinel
```
- **Fix:** Debug with Sentinel Simulator using the actual plan JSON as mock data; fix logic error; update policy.
- **Prevention:** Test all policies with mock data covering edge cases before applying to production workspaces.

**Mode 2: Policy Doesn't Catch All Violation Paths**
- **Symptom:** Non-compliant S3 bucket created despite Sentinel policy
- **Root Cause:** Policy checks `create` actions but not `no-op` (resource existed before policy was added)
- **Diagnostic:** Check `rc.change.actions` coverage in the policy:
```python
# Must include no-op for existing resources
rc.change.actions contains "create" or
rc.change.actions contains "update" or
rc.change.actions contains "no-op"
```
- **Fix:** Expand action filter to cover all lifecycle actions including `no-op`.
- **Prevention:** Write policies that cover all action types; use `tfstate/v2` for existing-resource validation.

**Mode 3: Policy Set Applied to Wrong Workspaces**
- **Symptom:** Strict production policies are blocking development workspace plans
- **Root Cause:** Global policy set applied to all workspaces without scope filtering
- **Diagnostic:** Check policy set workspace assignments in Terraform Cloud UI.
- **Fix:** Create separate policy sets for dev/prod; use workspace tags to scope assignment.
- **Prevention:** Design policy hierarchy: global (security basics) + team/environment-specific policies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Cloud  Enterprise, Terraform Plan / Apply / Destroy, Policy as Code

**Builds On This (learn these next):** Open Policy Agent (OPA), CI-CD, Observability & SRE

**Alternatives / Comparisons:** OPA (Open Policy Agent), AWS Config Rules, Checkov (static analysis), tfsec

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Policy-as-code gate between plan     │
│               │ and apply in Terraform Cloud/Enterprise│
│ PROBLEM       │ Non-compliant infra reaches prod     │
│ KEY INSIGHT   │ hard-mandatory = no override ever    │
│ USE WHEN      │ Compliance, security, cost controls  │
│ AVOID WHEN    │ OSS Terraform (use OPA/Checkov)      │
│ TRADE-OFF     │ Enforcement strictness vs agility    │
│ ONE-LINER     │ enforcement_level = "hard-mandatory" │
│ NEXT EXPLORE  │ OPA, Policy as Code, Checkov         │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A Sentinel policy enforces that all S3 buckets must have encryption enabled. A `no-op` plan (no HCL changes, just a drift refresh) runs for a workspace that has a pre-existing unencrypted bucket. Does the Sentinel policy catch this violation? Why or why not, and what must be added to the policy to enforce compliance on existing resources?

2. **(Scale)** An organization has 200 workspaces across 3 Terraform Cloud organizations and needs to enforce 15 security policies globally while allowing 3 teams to have exceptions for specific policies. Design the policy set architecture that satisfies both the global requirement and the exception workflow.

3. **(Design Trade-off)** Sentinel (Terraform Cloud/Enterprise) and OPA (open-source) both implement policy-as-code for Terraform. What are the specific technical and organizational trade-offs of each for a team that: (a) uses both Kubernetes and Terraform, (b) is cost-sensitive, and (c) needs policies reviewable by security engineers who don't know Go or DSL languages?
