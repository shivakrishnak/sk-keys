---
version: 2
layout: default
title: "Policy as Code"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /ci-cd/policy-as-code/
id: CCD-043
category: CI/CD
difficulty: ★★★
depends_on: Infrastructure as Code, CI-CD, Security
used_by: Open Policy Agent (OPA), Sentinel (Terraform Policy)
related: Open Policy Agent (OPA), Sentinel, Compliance-Oriented SDLC
tags:
  - cicd
  - devops
  - security
  - advanced
  - bestpractice
---

# CCD-032 - Policy as Code

⚡ **TL;DR -** Policy as Code encodes compliance, security, and operational rules as machine-executable files that are version-controlled and enforced automatically in CI/CD pipelines.

| Field | Value |
|-------|-------|
| **Depends on** | Infrastructure as Code, CI-CD, Security |
| **Used by** | Open Policy Agent (OPA), Sentinel (Terraform Policy) |
| **Related** | Open Policy Agent (OPA), Sentinel, Compliance-Oriented SDLC |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Security and compliance rules live in Word documents, Confluence pages, and the memory of a senior engineer who joined seven years ago. Developers guess whether their Terraform change will pass a security review. The review happens after build - slowing delivery by days. A misconfigured S3 bucket reaches production because nobody checked the policy document against the code.

**THE BREAKING POINT:** An audit finds 47 violations across 200 infrastructure resources. Each violation requires manual review. The security team cannot scale their review bandwidth to match the pace of infrastructure changes. The company fails its SOC 2 audit because it cannot demonstrate that controls were consistently enforced.

**THE INVENTION MOMENT:** If infrastructure is code (IaC), then the rules governing that infrastructure must also be code - version-controlled, testable, automatically enforced at every stage of the pipeline - not manual checkpoints that can be skipped.

---

### 📘 Textbook Definition

**Policy as Code** is the practice of expressing operational, security, and compliance policies as machine-readable, version-controlled code files that are automatically evaluated against infrastructure configuration, application deployments, or API requests - enabling automated enforcement, testability, auditability, and consistent application across environments without human intervention.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Encode your rules as code so they are enforced automatically and can never be accidentally skipped.

> Think of Policy as Code like a spell-checker for compliance. Instead of having a grammar teacher review every document manually, you encode the grammar rules in software that runs instantly and catches every violation - consistently, at scale, before the document is published.

**One insight:** The critical shift is **shift-left enforcement** - policies evaluated in a developer's IDE or in the CI pipeline (where fixing violations is cheap) rather than in a manual security review before production (where fixing violations is expensive and blocks delivery).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A policy is a function: given a resource configuration, it returns allow or deny with a reason.
2. Any function that can be expressed in prose can, in principle, be expressed in code.
3. Automated enforcement is consistent; human enforcement is probabilistic.
4. A policy that cannot be tested cannot be trusted to behave correctly at the boundary cases.

**DERIVED DESIGN:** Policies are written in a declarative language (Rego, HCL, YAML) expressing invariants over input documents (Terraform plans, Kubernetes manifests, API requests). A policy engine evaluates the policy against the input at the enforcement point (CI gate, admission webhook, API gateway). Results are deterministic, logged, and auditable.

**THE TRADE-OFFS:**
**Gain:** Consistent enforcement at scale; shift-left security; automated audit evidence; policy as pull-request-reviewable code.
**Cost:** Policy authoring requires learning DSLs (Rego is particularly non-trivial). Policies must be maintained as infrastructure evolves. False positives block legitimate changes. Policy testing infrastructure adds pipeline complexity.

---

### 🧪 Thought Experiment

**SETUP:** Your organisation has a policy: all S3 buckets must have server-side encryption enabled and public access blocked. There are 15 developers creating infrastructure in Terraform.

**WHAT HAPPENS WITHOUT POLICY AS CODE:** The policy is in Confluence. 12 of 15 developers know it exists. 3 are new. Of the 12 who know, 2 forget for a specific edge case. Two buckets reach production without encryption. The next AWS Config report flags them. The security team schedules a remediation sprint. This takes two weeks.

**WHAT HAPPENS WITH POLICY AS CODE:** A Rego policy runs in the CI pipeline against every `terraform plan` output. The three new developers' PRs fail with: "DENY: S3 bucket 'user-uploads' has public access enabled. Add `block_public_acls = true`." The violation is fixed before the PR is merged. No manual review was required. The fix took 3 minutes.

**THE INSIGHT:** Policy as Code converts compliance from a periodic audit that finds violations after the fact into a real-time gate that prevents violations from existing in the first place. The audit evidence is the pipeline run log.

---

### 🧠 Mental Model / Analogy

> Think of Policy as Code as **building regulations encoded in planning software**. When an architect submits a blueprint, the software automatically checks every constraint - fire exit width, load-bearing requirements, ceiling height - and rejects non-compliant plans before they reach a human inspector. The code IS the building code.

- Building regulations = organisational compliance and security policies
- Blueprint = infrastructure configuration (Terraform plan, K8s manifest)
- Planning software = policy engine (OPA, Sentinel, Checkov)
- Automatic rejection = CI gate deny or admission webhook block
- Human inspector = reserved for novel edge cases, not routine checks
- Planning permission stamp = policy pass result in audit log

Where this analogy breaks down: Building regulations change slowly; software policies may need to change weekly as threats and compliance requirements evolve, requiring a fast policy review and release process of their own.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Policy as Code means you write down your company's IT rules in a special programming language, and a computer automatically checks everyone's work against those rules. Nobody can accidentally skip the check.

**Level 2 - How to use it (junior developer):**
You write a policy file (Rego or YAML) that says something like "no container should run as root." You add a step in your CI pipeline (using OPA or Conftest) that runs this policy against your Kubernetes manifests or Helm chart. If any container spec has `runAsRoot: true`, the pipeline fails with a clear message. The developer fixes it before the code is merged.

**Level 3 - How it works (mid-level engineer):**
A policy engine takes two inputs: the policy document (rules) and the data document (resource configuration). It evaluates the policy function against the data and returns a decision: `allow`, `deny`, or a set of violations with reasons. Enforcement points vary: in CI (Conftest against manifests/Terraform plans), at Kubernetes admission (OPA Gatekeeper webhook), or within a CD platform (Harness OPA integration, Sentinel in Terraform Cloud). Soft enforcement (warn but allow) and hard enforcement (block) are distinct modes with different use cases in policy rollout phases.

**Level 4 - Why it was designed this way (senior/staff):**
The declarative policy language design (Rego, Sentinel, Cedar) is intentional. Turing-complete languages (Python, Bash) could express any policy but would also enable side effects, non-termination, and unpredictable behaviour in the critical path of deployments. A declarative language with no side effects, no I/O, and guaranteed termination (Rego is Datalog-derived) is safe to evaluate in a synchronous admission webhook with a 30ms deadline. The separation of policy from data also enables policy testing with mock data - the same policy evaluated against a mock Terraform plan in unit tests as in production, with no environment dependency.

---

### ⚙️ How It Works (Mechanism)

```
Developer: terraform plan / kubectl apply
    │
    ▼
┌──────────────────────────────────────┐
│  CI Gate / Admission Webhook         │
│  policy_engine.eval(policy, input)   │
└──────────┬───────────────────────────┘
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
policy.rego    input.json
(rules)        (resource config)
     │            │
     └─────┬──────┘
           │ evaluation
           ▼
┌──────────────────────────────────────┐
│  Decision                            │
│  allow: {} → proceed                 │
│  deny: ["reason1","reason2"] → block │
└──────────────────────────────────────┘
```

**Enforcement modes:**

| Mode | Behaviour | Use Case |
|------|-----------|----------|
| Dry-run | Evaluate, log, never block | Policy development |
| Warn | Log violation, allow proceed | Rollout phase |
| Soft | Block in CI, allow with override | Pre-production |
| Hard | Block always, no override | Prod admission |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Developer writes Terraform change
    │
    ▼
terraform plan → plan.json
    │
    ▼ ← YOU ARE HERE
CI: conftest test --policy ./policies plan.json
    │
    ▼
Policies evaluated: encryption, tagging,
public-access, cost estimation
    │  all PASS
    ▼
PR merged → terraform apply (staging)
    │
    ▼
Kubernetes admission: OPA Gatekeeper
evaluates manifest on kubectl apply
    │  all PASS
    ▼
Resource created → audit log: policy PASS
    │
    ▼
Compliance report: 0 violations this sprint
```

**FAILURE PATH:**
```
conftest test: FAIL
  S3 bucket missing encryption (policy: s3-encrypt)
  EC2 instance uses public AMI (policy: no-public-ami)
    │
    ▼
Pipeline blocked - PR cannot merge
    │
    ▼
Developer sees violation + remediation hint
    │
    ▼
Fix committed → policy re-evaluated → PASS
```

**WHAT CHANGES AT SCALE:**
Policy sprawl becomes a risk - hundreds of policy files with overlapping and conflicting rules. A policy governance process (policy-as-PR, policy owners, semantic versioning for policies) is necessary. A centralised OPA bundle server distributes policies to all enforcement points; bundle updates are versioned and rolled out progressively. Policy performance becomes relevant at high Kubernetes admission webhook volumes - Rego evaluation latency matters when it sits in the critical path of pod scheduling.

---

### 💻 Code Example

**BAD - ad-hoc script with no structure or testing:**
```bash
# BAD: fragile, untestable, no audit trail
if terraform plan | grep -q "public_acls = false"; then
  echo "OK"
else
  echo "FAIL: public ACL not disabled"
  exit 1
fi
```

**GOOD - Rego policy with Conftest (OPA):**
```rego
# policies/s3_security.rego
package s3_security

import future.keywords.contains
import future.keywords.if

# DENY: S3 bucket must block all public access
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.after.block_public_acls == false
  msg := sprintf(
    "DENY: S3 bucket '%v' must have block_public_acls=true",
    [resource.address]
  )
}

# DENY: S3 bucket must have server-side encryption
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_server_side_encryption_configuration"
  count(resource.change.after.rule) == 0
  msg := sprintf(
    "DENY: S3 bucket '%v' missing encryption config",
    [resource.address]
  )
}
```

**CI integration (GitHub Actions):**
```yaml
- name: Policy Check
  run: |
    terraform plan -out=plan.tfplan
    terraform show -json plan.tfplan > plan.json
    conftest test --policy ./policies \
      --namespace s3_security plan.json
```

---

### ⚖️ Comparison Table

| Tool | Language | Scope | Enforcement Points | Ecosystem |
|------|----------|-------|-------------------|-----------|
| **OPA / Conftest** | Rego | Universal | CI, admission, API GW | CNCF, K8s, Terraform |
| **Sentinel** | HCL-like | Terraform | Terraform Cloud/Enterprise | HashiCorp-only |
| **Checkov** | YAML rules | IaC | CI (Terraform, CF, K8s) | Standalone/free |
| **Kyverno** | YAML | Kubernetes | K8s admission | K8s-native, no DSL |
| **AWS Config Rules** | Lambda/JSON | AWS resources | AWS runtime | AWS-only, post-deploy |
| **Cedar** | Cedar DSL | Authorization | API/app-level | AWS/OPAL |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Policy as Code is just security scanning" | Security scanning checks for known vulnerabilities in code/dependencies. Policy as Code enforces organisational rules on configuration, deployment, and resource shape - different problems, different tools. |
| "Rego is easy to learn" | Rego is a Datalog-derived logic programming language. Its evaluation model (unification, recursion) is non-obvious for engineers used to imperative languages. Budget real learning time. |
| "Soft enforcement is pointless" | Soft enforcement (warn, don't block) is the correct rollout phase before hard enforcement. It surfaces violations without breaking pipelines, allowing teams to fix the backlog before the gate goes hard. |
| "Policy as Code eliminates the need for security review" | PaC automates enforcement of known, expressible rules. Novel architectures, threat modelling, and compliance interpretation still require human judgment. PaC frees reviewers to focus on novel cases. |
| "One OPA instance handles all enforcement" | OPA runs as a sidecar or admission webhook per cluster; bundles federate policy to multiple instances. A single OPA instance is a single point of failure for all admission decisions in that cluster. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Policy false positive blocks legitimate changes**
**Symptom:** A valid Terraform resource is blocked by a policy that matches too broadly. Engineers start adding exceptions everywhere.
**Root Cause:** Policy uses a string contains check rather than exact resource type matching; unrelated resources match the condition.
**Diagnostic:**
```bash
# Test policy against a minimal mock input
conftest test --policy ./policies \
  --input test/fixtures/valid_bucket.json \
  --namespace s3_security

# Trace Rego evaluation with OPA REPL
opa eval -d policies/s3_security.rego \
  -i plan.json "data.s3_security.deny" --explain full
```
**Fix:**
BAD - Add a global exception list for the affected team.
GOOD - Narrow the policy condition with additional constraints; add unit test with the valid resource as input to prevent regression; document the intended boundary in policy comments.
**Prevention:** Every policy must have a test file with both a positive (should deny) and negative (should allow) case before merging.

**Failure Mode 2: OPA admission webhook timeout causes pod scheduling failures**
**Symptom:** Pod deployments time out sporadically; Kubernetes events show "failed calling webhook."
**Root Cause:** OPA Gatekeeper webhook is overloaded or policy evaluation is slow on large input documents.
**Diagnostic:**
```bash
kubectl get events --field-selector \
  reason=FailedCreate -n default

kubectl top pods -n gatekeeper-system

# Check webhook timeout config
kubectl get validatingwebhookconfigurations \
  -o jsonpath='{.items[*].webhooks[*].timeoutSeconds}'
```
**Fix:**
BAD - Set `failurePolicy: Ignore` globally to prevent scheduling failures.
GOOD - Profile slow Rego policies; increase webhook replicas; set `failurePolicy: Ignore` only for non-critical namespaces; use `namespaceSelector` to exclude system namespaces from enforcement.
**Prevention:** OPA webhook timeout should be ≤10s. Load-test the policy bundle before production deployment. Run ≥3 Gatekeeper replicas with HPA.

**Failure Mode 3: Policy drift - code diverges from enforcement**
**Symptom:** Compliance audit finds violations in production that the policy engine claims would be blocked.
**Root Cause:** Policies in CI check Terraform plan JSON; policies in the admission webhook are an older bundle version. A new resource type was covered in CI but not yet pushed to the OPA bundle server.
**Diagnostic:**
```bash
# Check bundle version on OPA instance
curl -s http://opa-service:8181/v1/data/system/bundle \
  | jq '.result.manifest.revision'

# Compare against CI policy repo tag
git -C policies-repo log --oneline -5
```
**Fix:**
BAD - Manually sync the bundle on each change.
GOOD - Automate bundle build and push on every merge to the policy repo; tag bundles with semantic versions; OPA instances poll for updates on a defined interval; CI and admission use the same bundle source.
**Prevention:** Treat the policy bundle as a versioned artifact. Policy repo CI publishes a new bundle on every merge; OPA instances use bundle revision labels for drift detection.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Infrastructure as Code - the resource definitions policies are evaluated against
- CI-CD - the pipeline where policy gates are inserted
- Security - the domain that defines the rules Policy as Code enforces

**Builds On This (learn these next):**
- Open Policy Agent (OPA) - the most widely used policy engine implementing PaC
- Sentinel (Terraform Policy) - HashiCorp's PaC implementation for Terraform workflows
- Supply Chain Security - extends PaC to artifact provenance and signing verification

**Alternatives / Comparisons:**
- Checkov - static analysis tool for IaC; simpler than OPA but less flexible
- Kyverno - Kubernetes-native policy engine using YAML rather than Rego
- AWS Config Rules - runtime enforcement of resource configuration (post-deploy, not shift-left)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ Compliance rules expressed as       │
│                │ version-controlled executable code   │
│ PROBLEM        │ Manual policy reviews don't scale  │
│ KEY INSIGHT    │ Shift-left: enforce at PR, not prod │
│ USE WHEN       │ Any team with IaC or K8s deploys    │
│ AVOID WHEN     │ Novel/interpretive compliance cases │
│ TRADE-OFF      │ Consistency + speed vs DSL overhead │
│ ONE-LINER      │ Policy = code = gate = audit proof  │
│ NEXT EXPLORE   │ OPA, Sentinel, Kyverno              │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** Policy as Code enforces known, expressible rules automatically. What category of security and compliance requirement is fundamentally not expressible as a policy function - and how should those requirements be handled in a shift-left program?

2. **(Scale)** As a platform grows to 500 policy files owned by different teams, how do you prevent conflicting policies from creating contradictions - and what governance model (policy owner, policy registry, semantic versioning) would you implement to manage this?

3. **(System Interaction)** A policy blocks a Kubernetes pod from deploying because it lacks a required label. The pod is a system component needed to restore service during an incident. What mechanism should exist to override the policy in a time-bounded, auditable way without permanently weakening the control?
