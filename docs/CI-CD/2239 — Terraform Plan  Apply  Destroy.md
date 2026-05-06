---
layout: default
title: "Terraform Plan / Apply / Destroy"
parent: "CI/CD"
nav_order: 2239
permalink: /ci-cd/terraform-plan-apply-destroy/
number: "2239"
category: CI/CD
difficulty: ★★☆
depends_on: Terraform Overview, Terraform State
used_by: CI-CD, Terraform Drift Detection
related: Terraform State, Terraform Import, CI-CD
tags:
  - cicd
  - devops
  - intermediate
---

# 2239 — Terraform Plan / Apply / Destroy

⚡ **TL;DR —** Plan previews changes, apply executes them, and destroy removes all managed infrastructure — the three core operations of every Terraform workflow.

| Field | Value |
|---|---|
| **Depends on** | Terraform Overview, Terraform State |
| **Used by** | CI-CD, Terraform Drift Detection |
| **Related** | Terraform State, Terraform Import, CI-CD |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Infrastructure changes are applied blindly. Engineers run `aws cloudformation deploy` and hope for the best. There's no preview of what will change, no approval gate, and no way to see that a variable typo will replace a production database instead of updating it.

**THE BREAKING POINT:** An engineer updates an RDS subnet group in CloudFormation without previewing. The update requires resource replacement. RDS deletes the database instance before creating the new one. Two hours of data loss. The change would have been caught in a preview.

**THE INVENTION MOMENT:** Terraform separates infrastructure modification into three distinct phases. `plan` shows what will change before touching anything. `apply` executes with explicit confirmation. `destroy` safely removes all managed resources with a separate safety gate.

---

### 📘 Textbook Definition

**`terraform plan`** computes the difference between the current state and the desired configuration, outputting a human-readable list of changes (create/update/delete) and optionally saving a plan file. **`terraform apply`** executes the plan (either interactively from a new plan or from a saved plan file), applies changes to real infrastructure, and updates state. **`terraform destroy`** generates and applies a plan that deletes all resources managed by the configuration; it is equivalent to removing all resources from HCL and running `apply`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Plan = diff; apply = commit; destroy = delete all — the three-phase lifecycle of Terraform operations.

> Plan/apply/destroy is like surgical prep: `plan` is the pre-op imaging that shows exactly what the surgeon will do; `apply` is the surgery itself; `destroy` is the decision to remove the entire structure.

**One insight:** The critical safety feature is the **plan file** (`terraform plan -out=tfplan`). When you apply a saved plan file, you execute exactly what was reviewed — not a fresh plan that may have changed since review. This eliminates the "plan approved but apply did something different" failure mode.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Plan is read-only with respect to real infrastructure (it may update state during refresh).
2. Apply is always preceded by a plan — either live or from a saved plan file.
3. Destroy is a plan that sets the desired count of all resources to zero.
4. Saved plan files are binary and must be applied before expiry or state changes.

**DERIVED DESIGN:** CI/CD pipelines separate plan (runs on PR creation) from apply (runs on merge to main). The plan output becomes the PR review artifact — engineers approve the infrastructure diff, not just the code diff.

**THE TRADE-OFFS:**
**Gain:** Human-approval gate before infrastructure mutation; audit trail; no-surprises deploys.
**Cost:** Two-phase workflow adds latency; plan can be invalidated between review and apply if state changes concurrently.

---

### 🧪 Thought Experiment

**SETUP:** You change an RDS instance's `db_subnet_group_name` from `private` to `private-v2`.

**WHAT HAPPENS WITHOUT PLAN:** You run apply. AWS decides this change requires instance replacement (delete → create). Your production database is gone for 20 minutes while a new one creates. You had no warning.

**WHAT HAPPENS WITH PLAN:** `terraform plan` shows: `# aws_db_instance.main must be replaced`. The word `replaced` is the warning. You read the plan, understand the risk, schedule a maintenance window, and take a snapshot before applying.

**THE INSIGHT:** `terraform plan` doesn't just show *what* will change — it shows *how* (in-place update vs replacement). The distinction between `~` (update), `-/+` (replace), and `-` (destroy) is critical operational information.

---

### 🧠 Mental Model / Analogy

> Plan/apply/destroy is like a database migration tool: `plan` shows the diff script, `apply` runs the migration, `destroy` drops all tables. You would never drop a production table without reading the migration script first.

- `terraform plan` → `flyway info` (show pending migrations)
- `terraform apply` → `flyway migrate` (execute)
- `terraform destroy` → `DROP TABLE ALL` (with confirmation)
- Saved plan file → migration file checked into source control
- `-target` flag → `flyway migrate -target=V2`

Where this analogy breaks down: unlike database migrations, Terraform plan files are binary and time-sensitive. A plan created against state serial N is invalid if another apply increments state to serial N+1.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):** Plan shows what Terraform will do without doing it. Apply does it. Destroy removes everything. Always run plan before apply.

**Level 2 — How to use it (junior developer):** Run `terraform plan -out=tfplan` to save the plan. Review the output — green `+` means create, yellow `~` means update, red `-` means destroy. Run `terraform apply tfplan` to execute exactly what you reviewed. Never use `--auto-approve` in production.

**Level 3 — How it works (mid-level engineer):** During plan, Terraform calls provider `PlanResourceChange` for each resource. The provider returns a diff and marks unknown values (`(known after apply)`). The plan is serialized to a binary protobuf format. During apply, Terraform calls `ApplyResourceChange` in DAG order. State is updated atomically after each resource.

**Level 4 — Why it was designed this way (senior/staff):** The plan/apply split maps to the "intention vs execution" separation in safe operations. The plan file ensures apply executes precisely what was reviewed, not a fresh computation that may differ due to state changes or configuration drift. The `-target` flag exists for emergency hotfixes but should never be a standard workflow — targeted applies can leave state in a partially converged condition.

---

### ⚙️ How It Works (Mechanism)

**Plan output symbols:**
| Symbol | Meaning |
|---|---|
| `+` | Resource will be created |
| `-` | Resource will be destroyed |
| `~` | Resource will be updated in-place |
| `-/+` | Resource will be destroyed then recreated |
| `<=` | Data source will be read |

**Plan file flow:**
1. `terraform plan -out=tfplan` → serialized binary protobuf file
2. `terraform show tfplan` → human-readable review
3. `terraform apply tfplan` → executes exactly the saved plan
4. Plan file is consumed after apply; cannot be reused

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL CI/CD FLOW:**
```
  PR opened: HCL change
           │
  CI: terraform plan -out=tfplan    ← YOU ARE HERE
  Plan output posted to PR as comment
           │
  Engineer reviews plan:
    + aws_s3_bucket.new (create)
    ~ aws_security_group.app (update)
           │
  PR approved → merged to main
           │
  CI: terraform apply tfplan
  (same plan file, no re-plan)
           │
  Resources updated; state written
```

**FAILURE PATH:** Plan saved at serial 42. Another team applies at serial 42 → serial becomes 43. Your `terraform apply tfplan` fails: `Error: state has changed since plan was generated`. Must re-plan.

**WHAT CHANGES AT SCALE:** Atlantis or Terraform Cloud shows plan output in PR comments automatically. Apply locks are managed per workspace. Plan/apply separation is enforced by the platform — developers cannot apply without a reviewed plan.

---

### 💻 Code Example

```bash
# WORKFLOW: safe CI/CD plan/apply pattern

# 1. Plan and save (in CI on PR)
terraform plan \
  -var-file="prod.tfvars" \
  -out=tfplan \
  -detailed-exitcode
# Exit code: 0=no changes, 1=error, 2=changes present

# 2. Convert to JSON for PR comment
terraform show -json tfplan | \
  jq '.resource_changes[] | {action: .change.actions, address}'

# 3. Apply saved plan (in CI on merge)
terraform apply tfplan

# BAD: auto-approve in production
terraform apply -auto-approve  # NEVER do this in prod

# BAD: targeted apply as routine
terraform apply -target=aws_instance.web  # partial state, debt

# GOOD: targeted apply only as emergency hotfix
terraform apply \
  -target=aws_security_group.emergency_rule \
  -auto-approve  # acceptable in break-glass scenario only

# Destroy workflow (with safety checks)
# BAD: destroy without plan review
terraform destroy -auto-approve

# GOOD: plan destroy first, review, then apply
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan  # review what will be deleted
terraform apply destroy.tfplan
```

---

### ⚖️ Comparison Table

| Operation | `plan` | `apply` | `apply -destroy` | `apply -refresh-only` |
|---|---|---|---|---|
| **Modifies infra** | ❌ | ✅ | ✅ | ❌ |
| **Modifies state** | ❌ (refresh only) | ✅ | ✅ | ✅ |
| **Requires plan file** | Generates one | Accepts one | Accepts one | No |
| **Safe in prod** | ✅ Always | With plan file | With plan file | ✅ |
| **Use case** | Preview changes | Execute changes | Remove all | Sync drift |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`-auto-approve` is fine for simple changes" | Auto-approve skips all review gates. In CI, the plan should be the review artifact, not a reason to bypass it. |
| "Plan output is always accurate" | Plan can show `(known after apply)` values. Some update/replace decisions are only known after the apply starts. |
| "`-target` fixes things cleanly" | Targeted applies leave the rest of the state unconverged. Always follow with a full `terraform apply` to resolve residual drift. |
| "`terraform destroy` is reversible" | Resources are permanently deleted. Some providers have deletion protection; use `prevent_destroy`. |
| "Plan file is valid indefinitely" | Plan files are tied to a state serial. If state changes, the plan file is invalid and must be regenerated. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Plan Shows `-/+` Replace Unexpectedly**
- **Symptom:** `terraform plan` shows a resource will be destroyed and recreated; you only changed a tag
- **Root Cause:** Some argument changes force resource replacement (ForceNew attributes in provider schema)
- **Diagnostic:**
```bash
terraform plan | grep -A5 "must be replaced"
# Also check provider docs for the attribute's ForceNew flag
```
- **Fix:** Use `lifecycle { create_before_destroy = true }` to minimize downtime; review attribute documentation before changes.
- **Prevention:** Check provider docs for ForceNew attributes before planning changes to critical resources.

**Mode 2: Plan/Apply Divergence**
- **Symptom:** Apply shows different changes than the reviewed plan; colleagues see "plan changed" error
- **Root Cause:** Another team applied changes between when plan was generated and when apply runs
- **Diagnostic:**
```bash
terraform apply tfplan
# Error: state was changed after the plan was generated
```
- **Fix:** Re-run `terraform plan -out=tfplan` to get a fresh plan based on current state.
- **Prevention:** Use Terraform Cloud or Atlantis to serialize plan/apply within a single locked workflow.

**Mode 3: Partial Apply Leaves Inconsistent State**
- **Symptom:** Apply failed midway; some resources created, others not; next plan shows unexpected changes
- **Root Cause:** Provider API error, network timeout, or permission denied mid-apply
- **Diagnostic:**
```bash
terraform state list  # see what was created
terraform plan        # see what still needs to happen
```
- **Fix:** Review the state, remove any tainted/partial resources if needed, then re-apply.
- **Prevention:** Idempotent provider implementations handle partial applies gracefully; use `create_before_destroy` for critical services.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Overview, Terraform State, Terraform Provider

**Builds On This (learn these next):** Terraform Drift Detection, CI-CD, Terraform Import, Terraform Lifecycle Rules

**Alternatives / Comparisons:** AWS CloudFormation change sets, Pulumi preview, CDK diff

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Preview / execute / delete workflow  │
│ PROBLEM       │ Blind infra changes cause incidents  │
│ KEY INSIGHT   │ -out=tfplan = reviewed, safe apply   │
│ USE WHEN      │ Every infrastructure change          │
│ AVOID WHEN    │ Never skip plan in production        │
│ TRADE-OFF     │ Safety gate vs deployment latency    │
│ ONE-LINER     │ plan -out=f && show f && apply f     │
│ NEXT EXPLORE  │ Drift Detection, Lifecycle Rules     │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A saved plan file (`-out=tfplan`) is generated against state serial 15. Before apply runs, another team's apply increments state to serial 16. Terraform refuses to apply the plan file. What is the precise risk that this safety check prevents, and under what conditions would bypassing this check be acceptable?

2. **(Root Cause)** `terraform plan` shows that a change to an RDS `db_parameter_group_name` will force replacement of the database instance. The change is necessary. What are the options for applying this change with minimal data loss and downtime, and what Terraform constructs support each option?

3. **(Design Trade-off)** The `-target` flag allows applying changes to a subset of resources. What are the specific ways a targeted apply can leave Terraform state in an inconsistent condition, and what organizational policy should govern its use in production environments?
