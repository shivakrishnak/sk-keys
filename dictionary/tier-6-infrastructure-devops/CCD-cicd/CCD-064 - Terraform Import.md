---
version: 2
layout: default
title: "Terraform Import"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /ci-cd/terraform-import/
id: CCD-064
category: CI/CD
difficulty: ★★★
depends_on: Terraform State, Terraform Resource
used_by: CI-CD
related: Terraform State, Terraform Plan  Apply  Destroy, Terraform Drift Detection
tags:
  - cicd
  - devops
  - advanced
---

# CCD-064 - Terraform Import

⚡ **TL;DR -** Terraform import brings existing cloud resources under Terraform management by mapping them to state entries without recreating them.

| Field | Value |
|---|---|
| **Depends on** | Terraform State, Terraform Resource |
| **Used by** | CI-CD |
| **Related** | Terraform State, Terraform Plan  Apply  Destroy, Terraform Drift Detection |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Your organization has 200 manually-created AWS resources. You want to manage them with Terraform. Without import, Terraform has two options: (1) destroy and recreate everything - impossible for stateful resources with data, or (2) pretend these resources don't exist and create duplicates alongside them.

**THE BREAKING POINT:** A security audit requires all infrastructure to be managed by IaC. But there are production databases, VPCs, and security groups that can't be recreated. Terraform cannot manage what it doesn't know about.

**THE INVENTION MOMENT:** `terraform import` reads an existing cloud resource's current state via the provider API and writes it into the state file. Now Terraform knows the resource exists. The next `terraform plan` shows the diff between the resource's current configuration and your desired HCL.

---

### 📘 Textbook Definition

**Terraform import** is the process of adding an existing real-world infrastructure object into Terraform's state file, establishing Terraform management over a resource that was created outside of Terraform. The classic CLI import (`terraform import <address> <id>`) requires pre-written HCL. The newer **`import` block** (Terraform 1.5+) is declarative and integrates into the normal plan/apply workflow. In Terraform 1.5+, `-generate-config-out` can auto-generate the HCL configuration for an imported resource.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Import tells Terraform "this real resource is yours now - start tracking it."

> Import is like adding an existing house to your property management system: the house was already built, but you're now recording it in your books, assigning it a property number, and bringing it under standard maintenance contracts.

**One insight:** Import does NOT write HCL for you (before TF 1.5). After a CLI import, running `terraform plan` will show the diff between the empty HCL stub and the actual resource. You must write matching HCL to make the plan show zero changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Import writes to state only - it does not modify the real resource.
2. After import, `terraform plan` will show diffs if the HCL doesn't match the actual resource.
3. Import requires the resource's cloud ID (not the Terraform resource address).
4. The `import` block (TF 1.5+) is idempotent and declarative - safe to commit and re-run.

**DERIVED DESIGN:** The classic `terraform import` CLI command is imperative and not tracked in source. The new `import` block is declarative - committed to HCL, reviewed in PRs, and part of the plan/apply workflow. This is the preferred approach for Terraform 1.5+.

**THE TRADE-OFFS:**
**Gain:** Existing resources brought under IaC control without recreation; gradual migration from manual infrastructure.
**Cost:** Writing accurate matching HCL is labor-intensive; complex resources with many attributes require careful review; one mistake means unexpected updates on the next apply.

---

### 🧪 Thought Experiment

**SETUP:** You have a production RDS cluster created six months ago manually. You want to manage it with Terraform. The database has 500 GB of production data.

**WHAT HAPPENS WITHOUT IMPORT:** You write the HCL and apply. Terraform tries to create a new RDS cluster. Either it conflicts with the existing one (name collision) or creates a second empty one. You can't just delete the old one - it has the data.

**WHAT HAPPENS WITH IMPORT:** You write the HCL stub for `aws_db_cluster.main`, import the existing cluster by ARN, then run `terraform plan`. Plan shows all the attribute diffs between your HCL and the real cluster's config. You update the HCL until plan shows zero changes. Now Terraform fully manages the existing cluster.

**THE INSIGHT:** Import is a migration tool. The goal is not just to import, but to *converge*: get to a state where `terraform plan` shows zero changes, meaning HCL fully and accurately describes the existing resource.

---

### 🧠 Mental Model / Analogy

> Import is like registering a car you bought privately: the car already exists and runs (real resource), but the DMV (Terraform state) doesn't know you own it. Registration (import) adds it to the official record. Now you can legally drive it, but you still need to pass inspection (plan shows zero diffs) to confirm everything is in order.

- Car → existing cloud resource
- DMV record → Terraform state entry
- Registration → `terraform import` operation
- Inspection → `terraform plan` showing zero diffs
- Title/HCL → your ownership declaration

Where this analogy breaks down: unlike car registration, if your HCL doesn't match the resource's actual configuration, Terraform will try to "fix" the mismatch on next apply - potentially modifying your production resource.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Import tells Terraform about infrastructure that was created without Terraform, so Terraform can start managing it.

**Level 2 - How to use it (junior developer):** Find the resource's cloud ID (e.g. EC2 instance ID: `i-1234567890`). Write a matching HCL `resource` block. Run `terraform import aws_instance.web i-1234567890`. Then run `terraform plan` to see what attributes differ from the actual resource, and update your HCL until the plan is clean.

**Level 3 - How it works (mid-level engineer):** During import, Terraform calls the provider's `ImportResourceState` and `ReadResource` RPCs, gets the full current state of the resource, and writes it to the state file. No API write calls are made. After import, the resource appears in state under the specified address.

**Level 4 - Why it was designed this way (senior/staff):** The `import` block (TF 1.5+) was designed to make import a first-class, reviewable workflow. The `-generate-config-out` flag produces a starting HCL template from the imported resource's state, dramatically reducing the labor of writing accurate HCL for complex resources. The declarative import block can be removed after the resource is stable under management, keeping configuration clean.

---

### ⚙️ How It Works (Mechanism)

**Classic CLI import (TF < 1.5):**
```
1. Write empty HCL resource block
2. terraform import <address> <cloud_id>
3. Provider: ImportResourceState → reads full state
4. State file updated with resource entry
5. terraform plan → shows diffs to fix
6. Update HCL until plan shows no changes
7. Remove import documentation (it's done)
```

**Import block (TF 1.5+):**
```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}
```
This block is committed to HCL and appears in `terraform plan` as an import operation. After apply, the block can be removed (or kept for documentation).

**Config generation (TF 1.5+):**
```bash
terraform plan -generate-config-out=generated.tf
```
Generates a starting HCL template based on the imported resource's current state. Review and clean up before committing.

---

### 🔄 The Complete Picture - End-to-End Flow

**IMPORT WORKFLOW (TF 1.5+ recommended):**
```
  Identify resource to import
  Find cloud resource ID
           │
  Write import block in HCL:   ← YOU ARE HERE
  import {
    to = aws_vpc.legacy
    id = "vpc-0abc12345"
  }
           │
  terraform plan -generate-config-out=gen.tf
  (TF generates HCL template from current state)
           │
  Review + refine gen.tf
  Move content to appropriate .tf files
           │
  terraform plan
  (should show: import + zero diffs)
           │
  terraform apply
  (resource added to state; no cloud changes)
           │
  Remove import block from HCL
  terraform plan → zero changes (verified)
```

**FAILURE PATH:** Import succeeds but HCL attributes don't match the real resource. `terraform plan` shows forced replacement. Applying would destroy the existing resource. Fix: update HCL to match actual; never apply until plan is clean.

**WHAT CHANGES AT SCALE:** Large-scale import projects (100+ resources) benefit from Terraformer or similar tools that can generate HCL + import commands from existing cloud resources. Still requires review before applying.

---

### 💻 Code Example

```hcl
# --- METHOD 1: Classic CLI import (pre-TF 1.5) ---
# Step 1: Write the resource block (empty args initially)
resource "aws_s3_bucket" "legacy_logs" {
  # attributes will be filled after import
}

# Step 2: Run CLI import command
# terraform import aws_s3_bucket.legacy_logs my-legacy-logs-bucket

# Step 3: After import, run plan and update HCL to match
# (plan will show diffs you need to resolve)

# --- METHOD 2: Import block (TF 1.5+ - preferred) ---
# import block (declare alongside resource)
import {
  to = aws_s3_bucket.legacy_logs
  id = "my-legacy-logs-bucket"
}

resource "aws_s3_bucket" "legacy_logs" {
  bucket = "my-legacy-logs-bucket"
  # Other attributes from: terraform plan -generate-config-out=gen.tf
}

# --- GENERATING CONFIG (TF 1.5+) ---
# terraform plan -generate-config-out=generated.tf
# This creates generated.tf with all current attributes:
resource "aws_s3_bucket" "legacy_logs" {
  bucket                      = "my-legacy-logs-bucket"
  force_destroy               = false
  object_lock_enabled         = false
  request_payer               = "BucketOwner"
  tags                        = { Environment = "legacy" }
  # ... many more auto-generated attributes
}

# After convergence: remove import block
# terraform plan should show: No changes.
```

---

### ⚖️ Comparison Table

| Approach | CLI Import | Import Block | Terraformer |
|---|---|---|---|
| **TF Version** | All | 1.5+ | All (external tool) |
| **Declarative** | ❌ Imperative | ✅ | ✅ Generates HCL |
| **In PR review** | ❌ | ✅ | With review |
| **Config generation** | ❌ | ✅ (1.5+ -generate) | ✅ Auto |
| **Idempotent** | ❌ Re-running re-imports | ✅ | External |
| **Best for** | Single resources | Modern workflow | Bulk migration |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Import modifies the real resource" | Import only writes to state. No API create/update calls are made during import. |
| "After import, I'm done" | After import, `terraform plan` will show diffs. You must update HCL until plan is clean before applying. |
| "I can import any resource" | Only resources with `ImportResourceState` implemented in the provider can be imported. Check provider docs. |
| "Import block stays in HCL permanently" | Import blocks are consumed after apply. Remove them to keep HCL clean. |
| "`-generate-config-out` produces production-ready HCL" | Generated config is a starting point. It includes every attribute; you'll want to remove read-only computed ones and consolidate references. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Post-Import Plan Shows Forced Replace**
- **Symptom:** After successful import, `terraform plan` shows `-/+` (destroy + create) for the imported resource
- **Root Cause:** HCL attribute doesn't match the actual resource's current value for a ForceNew attribute
- **Diagnostic:**
```bash
terraform state show aws_db_instance.main
# Compare all attributes with your HCL
terraform plan 2>&1 | grep "forces replacement"
```
- **Fix - BAD:** Apply the plan - destroys the existing resource.
- **Fix - GOOD:** Update HCL to exactly match the resource's current value for the ForceNew attribute.
- **Prevention:** Use `-generate-config-out` to get a complete starting HCL; review all ForceNew attributes.

**Mode 2: Import ID Format Wrong**
- **Symptom:** `Error: Cannot import non-existent remote object` during import
- **Root Cause:** The import ID format varies by resource type; using the wrong format
- **Diagnostic:** Check provider documentation for the specific resource's import section. Some resources use complex IDs: `account_id/resource_id` or `region/resource_name`.
```bash
# Example: IAM role policy attachment uses compound key
terraform import aws_iam_role_policy_attachment.example \
  "role-name/arn:aws:iam::123456789012:policy/policy-name"
```
- **Fix:** Use the exact import ID format from the provider documentation.
- **Prevention:** Always check the "Import" section in Terraform Registry docs for the resource type.

**Mode 3: Bulk Import State Inconsistency**
- **Symptom:** After importing 50 resources, `terraform plan` shows 15 resources as needing replacement
- **Root Cause:** Generated HCL has incorrect attribute values for 15 resources (default values that don't match real config)
- **Diagnostic:** For each problematic resource: `terraform state show <address>` and compare with HCL
- **Fix:** Fix each attribute mismatch in HCL; run plan after each fix.
- **Prevention:** Never apply until `terraform plan` shows zero changes for all imported resources.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform State, Terraform Resource, Terraform Overview

**Builds On This (learn these next):** Terraform Drift Detection, Terraform Plan / Apply / Destroy

**Alternatives / Comparisons:** Terraformer (bulk import tool), `aws-nuke` (opposite: removal), CDK import

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Bringing existing resources into     │
│               │ Terraform state management           │
│ PROBLEM       │ Manually-created infra outside TF    │
│ KEY INSIGHT   │ Import = state write only; no API    │
│               │ changes; plan must show zero diffs   │
│ USE WHEN      │ Migrating manual infra to TF         │
│ AVOID WHEN    │ Plan shows replacement - fix HCL 1st │
│ TRADE-OFF     │ Migration effort vs IaC compliance   │
│ ONE-LINER     │ import { to = X  id = "cloud_id" }  │
│ NEXT EXPLORE  │ Drift Detection, Lifecycle Rules     │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Root Cause)** After importing a production RDS cluster and writing matching HCL, `terraform plan` still shows a forced replacement due to the `engine_version` attribute. The running version is `15.3` but your HCL says `15`. Why does this cause a forced replacement rather than an in-place update, and how do you resolve this without recreating the database?

2. **(Scale)** An organization has 400 manually-created AWS resources across 8 accounts that need to be imported into Terraform over 3 months. Design the process: how do you prioritize, batch, test, and safely import at this scale without disrupting production?

3. **(Design Trade-off)** The `import` block in TF 1.5+ is declarative and lives in source control, while the CLI `terraform import` is imperative and not tracked. What are the operational and audit implications of each approach when a colleague asks "how did this resource come to be managed by Terraform?"
