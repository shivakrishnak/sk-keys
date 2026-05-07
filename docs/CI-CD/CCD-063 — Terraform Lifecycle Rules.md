---
layout: default
title: "Terraform Lifecycle Rules"
parent: "CI/CD"
nav_order: 63
permalink: /ci-cd/terraform-lifecycle-rules/
number: "CCD-063"
category: CI/CD
difficulty: ★★★
depends_on: Terraform Resource, Terraform State
used_by: CI-CD
related: Terraform Resource, Terraform Plan  Apply  Destroy, Terraform Drift Detection
tags:
  - cicd
  - devops
  - advanced
---

# CCD-063 — Terraform Lifecycle Rules

⚡ **TL;DR —** Lifecycle rules override Terraform's default resource management behavior — controlling creation order, deletion protection, change ignoring, and replacement triggers.

| Field | Value |
|---|---|
| **Depends on** | Terraform Resource, Terraform State |
| **Used by** | CI-CD |
| **Related** | Terraform Resource, Terraform Plan  Apply  Destroy, Terraform Drift Detection |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** By default, Terraform destroys a resource before creating its replacement. For a production database or load balancer, this means downtime during every recreation. There's no way to tell Terraform "never destroy this" or "ignore external changes to this attribute."

**THE BREAKING POINT:** Terraform wants to replace an RDS instance because of a subnet group change. Default behavior: destroy existing instance → downtime + data loss risk → create new instance. There must be a way to say "create the new one first, then destroy the old one."

**THE INVENTION MOMENT:** The `lifecycle` meta-argument gives engineers fine-grained control over resource lifecycle: prevent accidental deletion, reverse the destroy/create order, ignore external attribute changes, and define when replacement should be triggered.

---

### 📘 Textbook Definition

The **`lifecycle` meta-argument** in a Terraform resource block controls how Terraform manages changes to that resource. It supports five settings: `create_before_destroy` (create replacement before destroying original), `prevent_destroy` (error if plan includes destroying the resource), `ignore_changes` (list of attributes whose external changes Terraform should ignore), `replace_triggered_by` (force replacement when referenced attributes change), and `precondition`/`postcondition` blocks (contract assertions evaluated at plan/apply time).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Lifecycle rules tell Terraform how to handle replacement, deletion, and drift for a specific resource.

> Lifecycle rules are like a contract rider for a celebrity: "I'll work with you (Terraform), but under these specific conditions: don't destroy my dressing room before my new one is ready (`create_before_destroy`), never cancel my booking without asking me (`prevent_destroy`), and don't renegotiate my shirt color preference (`ignore_changes`)."

**One insight:** `prevent_destroy = true` is a *static safeguard*, not a runtime lock. It catches the dangerous plan before any API calls are made. But it can be bypassed by removing the lifecycle block from the HCL — so it's a reminder, not an absolute protection.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `create_before_destroy` reverses the default destroy-then-create order for that resource.
2. `prevent_destroy` makes Terraform error if any plan would destroy the resource.
3. `ignore_changes` accepts external modifications for the listed attributes; drift is not remediated.
4. `replace_triggered_by` adds explicit replacement triggers beyond ForceNew attributes.
5. `precondition`/`postcondition` blocks validate correctness at plan and apply time respectively.

**DERIVED DESIGN:** Lifecycle rules compensate for cases where Terraform's default behavior would cause downtime, data loss, or unintended state changes. They're surgical overrides, not general policies.

**THE TRADE-OFFS:**
**Gain:** Zero-downtime replacements; accidental deletion prevention; stable management of externally-managed attributes.
**Cost:** `ignore_changes` suppresses drift alerts for the ignored attributes; `prevent_destroy` can block legitimate teardown; `create_before_destroy` can fail if the provider doesn't support two concurrent instances.

---

### 🧪 Thought Experiment

**SETUP:** You manage an AWS Certificate Manager (ACM) certificate. The certificate has DNS validation records. After creation, the domain registrar updates the validation status — an attribute Terraform can't control.

**WHAT HAPPENS WITHOUT `ignore_changes`:** Every plan shows the `domain_validation_options` attribute as drifted because the external DNS validation status doesn't match what Terraform last recorded. Drift alerts fire constantly. Engineers spend time investigating non-issues.

**WHAT HAPPENS WITH `ignore_changes = [domain_validation_options]`:** Terraform creates the certificate, writes initial state, then never concerns itself with subsequent changes to validation options. The drift alert is silenced for this externally-managed attribute. Engineers can focus on real drift.

**THE INSIGHT:** `ignore_changes` is a deliberate acknowledgment: "This attribute is managed externally and I accept that." It's not ignoring a problem — it's documenting a boundary of responsibility.

---

### 🧠 Mental Model / Analogy

> Lifecycle rules are like surgical care instructions: `create_before_destroy` = "install the new pacemaker before removing the old one"; `prevent_destroy` = "DNR — do not remove without consent"; `ignore_changes` = "patient manages their own blood pressure, don't adjust it"; `replace_triggered_by` = "replace the device if the battery changes."

- `create_before_destroy` → replacement sequencing instruction
- `prevent_destroy` → deletion prohibition
- `ignore_changes` → externally-managed attribute boundary
- `replace_triggered_by` → explicit replacement trigger
- `precondition` → pre-op health check

Where this analogy breaks down: unlike surgical instructions, lifecycle rules in Terraform are evaluated at plan time for every change — not just once at a critical moment.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):** Lifecycle rules are instructions that tell Terraform to handle a resource differently from its default behavior — like "create the new version before deleting the old" or "never delete this."

**Level 2 — How to use it (junior developer):** Add a `lifecycle {}` block inside the resource block. Use `prevent_destroy = true` for databases. Use `create_before_destroy = true` for resources where downtime during replacement is unacceptable. Use `ignore_changes = [tags["LastModified"]]` for externally-managed tags.

**Level 3 — How it works (mid-level engineer):** `create_before_destroy` propagates to all resources that depend on the annotated resource (via `depends_on` or attribute references). `prevent_destroy` makes the plan computation fail immediately if destroy is required. `ignore_changes` causes Terraform to treat the current state value as the desired value for the listed attributes, so no diff is generated.

**Level 4 — Why it was designed this way (senior/staff):** The `lifecycle` block was designed as an escape hatch for the cases where Terraform's declarative model doesn't capture the operational requirements correctly. `precondition`/`postcondition` blocks (TF 1.2+) extend this model further: they add contract-based assertions that fail clearly at plan/apply time instead of silently producing incorrect infrastructure.

---

### ⚙️ How It Works (Mechanism)

**`create_before_destroy` propagation:**
When resource A has `create_before_destroy = true`, any resource B that references A's attributes also gets the constraint (because B can only be created after the new A exists). This propagation can cause unexpected behaviors in deep dependency chains.

**`prevent_destroy` evaluation:**
Evaluated during plan generation. If the computed plan includes a destroy action for the resource, Terraform returns an error and aborts. The plan never reaches the confirmation stage.

**`ignore_changes` semantics:**
For each listed attribute, Terraform uses the *current state value* as the *desired value* for that attribute. External changes to ignored attributes are absorbed into state on refresh but never generate a diff.

**`replace_triggered_by` semantics:**
References a resource attribute or resource as a whole. When the referenced value changes between plans, the annotated resource is forced to replace even if its own attributes haven't changed.

---

### 🔄 The Complete Picture — End-to-End Flow

**`create_before_destroy` FLOW:**
```
  Normal destroy-then-create (DEFAULT):
  1. Destroy old resource          ← DOWNTIME
  2. Create new resource

  With create_before_destroy:
  1. Create new resource           ← YOU ARE HERE
  2. Update references to new resource
  3. Destroy old resource
  (zero downtime for LBs, certs, etc.)
```

**`prevent_destroy` FLOW:**
```
  Plan includes destroy of aws_db_instance.main
           │
  Terraform checks lifecycle rules
           │
  prevent_destroy = true → PLAN ERROR
  "Error: Instance cannot be destroyed"
           │
  No destroy API call ever made
  Engineer must update HCL to remove
  prevent_destroy before destroying
```

**WHAT CHANGES AT SCALE:** Lifecycle rules in modules are inherited by callers. A module that sets `create_before_destroy` on a resource forces all dependent resources in the caller to also use create-before-destroy. Document this behavior in module READMEs.

---

### 💻 Code Example

```hcl
# create_before_destroy: zero-downtime ACM cert replacement
resource "aws_acm_certificate" "api" {
  domain_name       = "api.example.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# prevent_destroy: guard against accidental RDS deletion
resource "aws_db_instance" "production" {
  identifier        = "prod-db"
  engine            = "postgres"
  instance_class    = "db.r6g.large"
  allocated_storage = 100

  lifecycle {
    prevent_destroy = true
  }
}

# ignore_changes: handle externally-managed attributes
resource "aws_autoscaling_group" "app" {
  name                = "app-asg"
  desired_capacity    = 3
  min_size            = 2
  max_size            = 10

  lifecycle {
    # Autoscaler manages desired_capacity; don't revert
    ignore_changes = [desired_capacity]
    # Create new ASG before destroying old (rolling replace)
    create_before_destroy = true
  }
}

# ignore_changes: external tagging pipeline
resource "aws_instance" "app" {
  ami           = data.aws_ami.al2023.id
  instance_type = "t3.medium"

  tags = {
    Name = "app-server"
  }

  lifecycle {
    # External patching tool adds LastPatched tag; ignore it
    ignore_changes = [tags["LastPatched"], tags["PatchGroup"]]
  }
}

# replace_triggered_by: force replacement when config changes
resource "aws_launch_template" "app" {
  name_prefix   = "app-"
  image_id      = data.aws_ami.al2023.id
  instance_type = "t3.medium"
}

resource "aws_autoscaling_group" "app_v2" {
  name = "app-asg-v2"
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  min_size         = 2
  max_size         = 10
  desired_capacity = 3

  lifecycle {
    # Force ASG replacement when launch template changes
    replace_triggered_by = [aws_launch_template.app]
    create_before_destroy = true
  }
}

# precondition/postcondition (TF 1.2+)
resource "aws_instance" "app_checked" {
  ami           = var.ami_id
  instance_type = var.instance_type

  lifecycle {
    precondition {
      condition     = contains(["t3.micro", "t3.medium", "m5.large"], var.instance_type)
      error_message = "Instance type must be from approved list."
    }

    postcondition {
      condition     = self.public_ip == null || self.public_ip == ""
      error_message = "Instances must not have public IPs in production."
    }
  }
}
```

---

### ⚖️ Comparison Table

| Rule | Default Behavior | With Rule |
|---|---|---|
| **create_before_destroy** | Destroy → Create (downtime) | Create → Destroy (zero downtime) |
| **prevent_destroy** | Plan succeeds, destroy executed | Plan fails with error immediately |
| **ignore_changes** | External changes generate diffs | External changes absorbed silently |
| **replace_triggered_by** | Only ForceNew attrs trigger replace | Reference change also triggers replace |
| **precondition** | No validation at plan time | Plan fails with clear error message |
| **postcondition** | No validation at apply time | Apply fails with clear assertion error |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`prevent_destroy` is permanent protection" | It can be bypassed by removing the lifecycle block from HCL. It's a safety reminder, not an absolute lock. |
| "`create_before_destroy` always works" | Some resources require unique names; you can't have two simultaneously (name collision). The provider must support it. |
| "`ignore_changes = all` is safe" | Ignoring all changes means Terraform will never reconcile any external modifications. Use only for specific known attributes. |
| "`replace_triggered_by` works with any expression" | It accepts only resource references or resource attribute references, not arbitrary expressions. |
| "Lifecycle rules in modules are invisible to callers" | `create_before_destroy = true` propagates through dependency chains and can affect resources in the calling configuration. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `create_before_destroy` Name Collision**
- **Symptom:** `Error: Error creating resource: already exists` during replacement
- **Root Cause:** Resource type requires a unique name; old and new can't coexist
- **Diagnostic:**
```bash
terraform plan 2>&1 | grep "forces replacement"
# Check if resource uses name (not name_prefix)
```
- **Fix — BAD:** Remove `create_before_destroy` (causes downtime).
- **Fix — GOOD:** Switch from `name` to `name_prefix` which generates a unique name per instance.
- **Prevention:** Use `name_prefix` for resources that use `create_before_destroy`.

**Mode 2: `prevent_destroy` Blocking Legitimate Teardown**
- **Symptom:** `terraform destroy` fails in CI for environment teardown; `prevent_destroy` blocks it
- **Root Cause:** `prevent_destroy` is appropriate for prod but not for dev/staging environments
- **Diagnostic:**
```bash
terraform plan -destroy 2>&1 | grep "prevent_destroy"
```
- **Fix:** Parameterize the `prevent_destroy` flag: `prevent_destroy = var.environment == "prod"`. Note: this requires Terraform 1.3+ for dynamic lifecycle values.
- **Prevention:** Use workspace- or variable-driven lifecycle configuration for non-prod environments.

**Mode 3: `ignore_changes` Hiding Security Drift**
- **Symptom:** Security group rule changed manually; drift detection doesn't alert because `ignore_changes = [ingress]`
- **Root Cause:** `ignore_changes` set too broadly; security-sensitive attributes silently ignored
- **Diagnostic:** Audit all `ignore_changes` blocks in security-critical resources.
- **Fix:** Replace broad `ignore_changes` with specific attribute-level ignores. Never ignore `ingress`/`egress` wholesale.
- **Prevention:** Code review policy: `ignore_changes` on security group rules requires security team approval.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Resource, Terraform State, Terraform Plan / Apply / Destroy

**Builds On This (learn these next):** Terraform Drift Detection, CI-CD

**Alternatives / Comparisons:** AWS deletion protection (RDS, CloudFormation), Terraform `prevent_destroy` vs CloudFormation `DeletionPolicy`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Per-resource lifecycle behavior      │
│               │ overrides                            │
│ PROBLEM       │ Default destroy-then-create causes   │
│               │ downtime; accidental deletions       │
│ KEY INSIGHT   │ prevent_destroy is a plan-time guard,│
│               │ not a runtime lock                   │
│ USE WHEN      │ Stateful resources, zero-downtime    │
│               │ requirements, external attr mgmt     │
│ AVOID WHEN    │ ignore_changes on security attrs     │
│ TRADE-OFF     │ Safety/stability vs flexibility      │
│ ONE-LINER     │ lifecycle { create_before_destroy }  │
│ NEXT EXPLORE  │ Drift Detection, Terraform Import    │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A resource with `create_before_destroy = true` is being replaced. The resource has a downstream dependency (a security group rule referencing it). How does Terraform's DAG propagate the `create_before_destroy` constraint through dependencies, and what happens if a dependency in the chain doesn't support two concurrent instances?

2. **(Root Cause)** An engineer adds `ignore_changes = [tags]` to 50 resources to suppress drift alerts from an external tagging system. Six months later, the security team discovers that security group rules are also being silently ignored because someone added `ignore_changes = [ingress, egress, tags]` to a security group. What governance process should exist to prevent `ignore_changes` from being used to suppress security-relevant drift?

3. **(Design Trade-off)** `precondition` and `postcondition` blocks in `lifecycle` allow contract-based validation at plan and apply time. How do these differ from `variable` validation blocks in terms of what they can validate, when they run, and what errors they catch that the other mechanism cannot?
