---
version: 2
layout: default
title: "Terraform Cloud  Enterprise"
parent: "CI/CD"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/ci-cd/terraform-cloud-enterprise/
id: CCD-064
category: CI/CD
difficulty: ★★★
depends_on: Terraform Overview, Terraform State Backend, CI-CD
used_by: CI-CD, Sentinel (Terraform Policy)
related: Terraform Overview, Atlantis, GitHub Actions
tags:
  - cicd
  - devops
  - advanced
  - cloud
---

⚡ **TL;DR -** Terraform Cloud and Enterprise are managed platforms that add remote state, governed remote execution, team access controls, policy enforcement, and audit logging to the open-source Terraform CLI.

| Field | Value |
|-------|-------|
| **Depends on** | Terraform Overview, Terraform State Backend, CI-CD |
| **Used by** | CI-CD, Sentinel (Terraform Policy) |
| **Related** | Terraform Overview, Atlantis, GitHub Actions |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Terraform state lives in an S3 bucket - or worse, a local `terraform.tfstate` file on a developer's laptop. Two engineers run `terraform apply` simultaneously and corrupt the state. The staging apply runs on a developer's machine with their personal AWS credentials. Nobody knows what was applied last, by whom, or when. Rollback means diffing state files in a text editor.

**THE BREAKING POINT:** A new engineer accidentally runs `terraform destroy` on the staging environment from their local terminal. The state file on their laptop is now the authoritative record. The team rebuilds staging manually over two days. There is no audit log, no approval gate, no way to enforce that destructive operations require review.

**THE INVENTION MOMENT:** If Terraform execution is moved to a centralised, managed service, every apply becomes observable, governed, and auditable. Terraform Cloud/Enterprise is that service - it wraps the open-source CLI with the operational scaffolding that enterprises need.

---

### 📘 Textbook Definition

**Terraform Cloud** is HashiCorp's managed SaaS platform, and **Terraform Enterprise** is its self-hosted equivalent, that provide: remote Terraform execution in managed runners, centralised and encrypted state storage with locking, team-based access control, VCS integration with auto-triggered runs, Sentinel policy evaluation, audit logging, private module and provider registries, and run triggers for workspace dependency orchestration.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Terraform Cloud takes the Terraform CLI and adds everything an enterprise needs: remote execution, state locking, access control, policy gates, and audit logs.

> Think of Terraform Cloud as the difference between cooking at home (open-source Terraform) and a commercial kitchen (Terraform Cloud). The same recipes (configs) and techniques (CLI) apply - but the commercial kitchen adds industrial equipment, health inspections, staff access controls, order logging, and fire suppression. You can feed 1,000 people instead of 10.

**One insight:** The core architectural shift is **workspace-as-the-unit-of-governance**. In open-source Terraform, a workspace is just a directory. In Terraform Cloud, a workspace is a managed entity with its own state, execution history, access controls, variable set bindings, and policy set attachments - the primitive around which all governance is built.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Terraform state is the authoritative record of managed resources; it must be stored centrally, locked during writes, and encrypted at rest.
2. Execution outside an audited environment is ungoverned; every apply must have an owner, a trigger, and a log.
3. Access to infrastructure change capability must be scoped to teams, not individuals with shared credentials.
4. Policy must be enforced in the execution path, not applied after the fact.

**DERIVED DESIGN:** Terraform Cloud models infrastructure work as Runs (plan + apply pairs) within Workspaces (environment-scoped execution contexts). Runs are triggered by VCS push, API, or manually. State is managed per workspace with ACID-style locking. Teams are granted workspace permissions (read, plan, apply, admin) not resource-level credentials. Sentinel policies are evaluated between plan and apply.

**THE TRADE-OFFS:**

**Gain:** Centralised governance, state safety, audit trail, policy enforcement, and team collaboration without building any of this infrastructure yourself.

**Cost:** Terraform Cloud is commercial (free tier limited; Team plan required for Sentinel). Terraform Enterprise requires self-hosted infrastructure and operational overhead. VCS coupling means pipeline changes require platform team involvement. Lock-in to HashiCorp ecosystem.

---

### 🧪 Thought Experiment

**SETUP:** Your team uses open-source Terraform with state in S3. Three engineers can run `terraform apply` from their local terminals using their personal IAM roles. There is no approval workflow.

**WHAT HAPPENS WITHOUT TERRAFORM CLOUD:** Engineer A and Engineer B both run `terraform plan` concurrently on the same workspace. Engineer A runs `apply` first, changing the security group. Engineer B's plan is now stale but they apply anyway - overwriting Engineer A's change with an older state. The security group reverts. An incident follows. There is no audit record of who ran what.

**WHAT HAPPENS WITH TERRAFORM CLOUD:** Both engineers trigger runs in the same workspace. TFC serialises them - only one run executes at a time via workspace locking. Run B is queued. Engineer A's apply completes and the state is updated. Engineer B's run automatically re-plans against the new state. Each run is logged with the triggering identity, the plan output, the apply result, and the timing. The entire history is queryable.

**THE INSIGHT:** Terraform Cloud's core value is not the remote execution - it is the **serialisation and observability** of infrastructure change. Every apply is a ledger entry: who, what, when, why, and what happened.

---

### 🧠 Mental Model / Analogy

> Think of Terraform Cloud as a **managed bank vault with a transaction ledger**. The vault (remote state) holds the most important data (infrastructure truth). Every access (Terraform run) is logged, requires authentication, uses two-person control for large withdrawals (approval gates), and is serialised to prevent concurrent corruption. The bank (HashiCorp) maintains the vault so you do not have to.

- The vault = remote state storage (TFC-managed, encrypted, locked)
- Transaction = a Terraform run (plan + apply)
- Ledger = run history and audit logs
- Bank teller = workspace-scoped executor
- Access card = team-based workspace permissions
- Two-person control = apply approval workflow
- Safety deposit box policies = Sentinel policies

Where this analogy breaks down: A bank vault stores static assets; Terraform state is dynamic and changes with every apply, requiring locking semantics that a physical vault does not need.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Terraform Cloud is a website and service where your team runs Terraform together. Instead of everyone running it from their laptops with their own settings, it runs in one shared place, keeps a history of every change, and controls who is allowed to do what.

**Level 2 - How to use it (junior developer):**
Connect your Terraform Git repository to a Terraform Cloud workspace. Every push to the `main` branch triggers a run: Terraform Cloud plans and (if auto-apply is enabled) applies the change. State is stored automatically in TFC - no S3 backend configuration needed. Variables (including secrets) are stored in TFC workspaces and injected into runs, so credentials never touch developer laptops.

**Level 3 - How it works (mid-level engineer):**
A TFC workspace is configured with a VCS repository, a working directory, and Terraform variables. A push triggers a webhook that creates a new Run. The Run executes `terraform init` and `terraform plan` in a managed runner. The plan output is captured. Sentinel policies evaluate the plan. If policies pass and the workspace is set to require approval, the run waits for a user with `apply` permission to confirm. `terraform apply` then executes. State is updated transactionally and stored in TFC's encrypted backend. All this is accessible via the TFC API and auditable via the audit trail API.

**Level 4 - Why it was designed this way (senior/staff):**
The workspace-per-environment design (rather than workspace-per-service or workspace-per-team) reflects a deliberate blast-radius isolation decision. If staging and production share a workspace, a misconfigured variable (e.g., wrong AWS region) could cause a plan against production when staging was intended. Workspace-per-environment gives independent state, independent variables, independent access control, and independent policy set attachments. The Run Triggers feature (workspace B reruns automatically when workspace A applies successfully) was designed to model infrastructure dependency graphs (e.g., networking workspace must be applied before compute workspace) without encoding those dependencies in a monolithic configuration. This mirrors the decomposition principle of IaC: compose small workspaces rather than maintain one giant state.

---

### ⚙️ How It Works (Mechanism)

```
VCS Push (git push main)
    │  webhook
    ▼
┌──────────────────────────────────────┐
│  Terraform Cloud                     │
│  ┌─────────────────────────────────┐ │
│  │  Workspace                      │ │
│  │  terraform init + plan           │ │
│  │  (managed runner, locked state) │ │
│  └────────────┬────────────────────┘ │
│               │ plan artifact        │
│               ▼                      │
│  ┌─────────────────────────────────┐ │
│  │  Sentinel Policy Evaluation     │ │
│  │  PASS / FAIL                    │ │
│  └────────────┬────────────────────┘ │
│               │ PASS                 │
│               ▼                      │
│  ┌─────────────────────────────────┐ │
│  │  Apply Gate                     │ │
│  │  auto-apply OR manual approval  │ │
│  └────────────┬────────────────────┘ │
│               │ approved             │
│               ▼                      │
│  terraform apply → state updated     │
│  audit log entry written             │
└──────────────────────────────────────┘
```

**Workspace model:**

| Pattern | Workspace per | State isolation | Blast radius |
|---------|--------------|-----------------|--------------|
| Env-per-workspace | environment | Full | Per environment |
| Service-per-workspace | service+env | Full | Per service |
| Mono-workspace | repo | None | Full infrastructure |
| Module workspace | reusable module | N/A | Consumers only |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Developer pushes Terraform code to main
    │  GitHub webhook fires
    ▼
TFC: Run triggered ← YOU ARE HERE
    │
    ▼
terraform init (providers downloaded)
    │
    ▼
terraform plan (state locked)
    │  plan diff: +2 resources, ~1 resource
    ▼
Sentinel policies evaluated: PASS
    │
    ▼
Approval gate: engineer reviews plan
    │  confirms: "Apply"
    ▼
terraform apply (state updated)
    │  +2 resources created, 1 updated
    ▼
State written to TFC encrypted backend
    │
    ▼
Run Trigger: downstream workspace reruns
    │  (e.g., compute workspace reruns
    │   after networking workspace applies)
    ▼
Audit log: full run recorded
```

**FAILURE PATH:**
```
terraform plan: drift detected
  1 resource deleted externally (console)
    │
    ▼
Plan shows: +1 to re-create deleted resource
    │
    ▼
Sentinel: hard-mandatory policy FAIL
  "EC2 instance missing required tag 'owner'"
    │
    ▼
Run blocked - apply cannot proceed
    │
    ▼
Engineer fixes tag → new run triggered
```

**WHAT CHANGES AT SCALE:**
At scale, workspace count reaches hundreds; workspace-as-code becomes necessary (managing workspace configs in Terraform using the TFC provider). Variable Sets share common variables (AWS region, org tags) across all workspaces without copy-paste. Run Triggers model workspace dependency graphs. Terraform Enterprise with a clustering model handles high run throughput. Private Module Registry becomes the internal Terraform module catalogue with versioned, validated modules.

---

### 💻 Code Example

**BAD - local state, no governance:**
```hcl
# BAD: local state - anyone can apply from any machine
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
# No locking, no audit, no team access control
```

**GOOD - Terraform Cloud backend with workspace:**
```hcl
# terraform/backend.tf
terraform {
  cloud {
    organization = "my-org"
    workspaces {
      name = "production-networking"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

**GOOD - Workspace-as-code using TFC provider:**
```hcl
# admin/workspaces.tf - manage workspaces in Terraform
resource "tfe_workspace" "networking_prod" {
  name         = "production-networking"
  organization = var.org_name
  auto_apply   = false
  # VCS integration
  vcs_repo {
    identifier     = "myorg/infra-repo"
    branch         = "main"
    oauth_token_id = var.vcs_token_id
  }
  # Attach Sentinel policy set
}

resource "tfe_policy_set" "required_tags" {
  name          = "required-tags"
  organization  = var.org_name
  policy_ids    = [tfe_policy.require_tags.id]
  workspace_ids = [tfe_workspace.networking_prod.id]
}
```

---

### ⚖️ Comparison Table

| Feature | Terraform Cloud | Terraform Enterprise | Atlantis | Raw CI (GitHub Actions) |
|---------|----------------|---------------------|----------|------------------------|
| **State management** | Managed | Managed (self-hosted) | External (S3) | External (S3) |
| **Remote execution** | Managed runners | Self-hosted runners | Self-hosted | CI runners |
| **Sentinel policies** | Yes (Team+) | Yes | No | Via Conftest/OPA |
| **Team access control** | Yes | Yes | GitHub permissions | CI org access |
| **Private registry** | Yes | Yes | No | No |
| **Run triggers** | Yes | Yes | No | Workflow triggers |
| **Audit trail** | API-accessible | API-accessible | Git history | CI logs |
| **Cost** | Free tier + paid | $$$ (self-hosted) | Free | CI compute cost |
| **Ops overhead** | None | High | Medium | Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Terraform Cloud is just a state backend" | Remote state is one of many features. TFC also provides remote execution, team permissions, policy enforcement, audit logs, VCS integration, and module registry - far beyond what an S3 backend provides. |
| "Workspace-per-environment = one workspace per org" | The recommended pattern is one workspace per environment per service boundary (e.g., `prod-networking`, `staging-compute`). One global workspace creates a blast radius across all infrastructure. |
| "Auto-apply is always better for speed" | Auto-apply in production is a significant risk. Any pushed code applies immediately with no human review. Use auto-apply in dev/staging; require manual approval in production. |
| "Terraform Enterprise is just the self-hosted version" | TFE includes additional features for large enterprises: SAML SSO, audit logging endpoints, clustering for high throughput, and custom CA support - not just self-hosting. |
| "Run Triggers replace CI/CD pipelines" | Run Triggers orchestrate workspace-to-workspace dependencies within TFC. They do not replace a CI pipeline for testing, linting, or building application artifacts. They are infrastructure orchestration, not application CI. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: State lock stuck after failed run**
**Symptom:** All new runs fail with "Error acquiring the state lock" - no run is actively executing.

**Root Cause:** A previous run failed mid-apply; TFC failed to release the state lock due to runner failure or network partition.

**Diagnostic:**
```bash
# Check lock status via API
curl -H "Authorization: Bearer $TFC_TOKEN" \
  "https://app.terraform.io/api/v2/workspaces/\
${WORKSPACE_ID}/current-state-version" \
  | jq '.data.attributes.locked'

# Force-unlock via API (requires admin)
curl -X POST \
  -H "Authorization: Bearer $TFC_TOKEN" \
  "https://app.terraform.io/api/v2/workspaces/\
${WORKSPACE_ID}/actions/force-unlock"
```
**Fix:**
BAD - Delete the workspace state and start fresh.
GOOD - Use the force-unlock API (requires owner-level permission in TFC). Investigate why the previous run failed to release the lock before unlocking to prevent data corruption.

**Prevention:** Monitor workspace lock duration; alert if locked for more than 30 minutes with no active run. TFC automatically releases locks after run completion in most failure scenarios - persistent locks indicate a platform issue.

**Failure Mode 2: VCS-triggered run applies wrong workspace config**
**Symptom:** A push to the `staging` branch triggers an apply in the `production` workspace.

**Root Cause:** Multiple workspaces are connected to the same VCS repository; workspace VCS branch filter was not configured, so all branches trigger all workspaces.

**Diagnostic:**
```bash
# Check workspace VCS config
curl -H "Authorization: Bearer $TFC_TOKEN" \
  "https://app.terraform.io/api/v2/workspaces/\
${WORKSPACE_ID}" \
  | jq '.data.attributes["vcs-repo"]'
# Look for trigger-prefixes or branch setting
```
**Fix:**
BAD - Remove VCS integration and use manual applies.
GOOD - Configure each workspace with an explicit `branch` filter in the VCS settings. Staging workspace monitors `staging` branch; production workspace monitors `main` branch with required PR review.

**Prevention:** Enforce workspace-branch binding as code in the TFC provider config. Code review of workspace configurations before creating new workspaces.

**Failure Mode 3: State drift causes cascading apply failures**
**Symptom:** Consecutive runs in the same workspace alternate between plan showing additions and deletions for the same resources.

**Root Cause:** Manual changes were made in the AWS console (or by another team's Terraform), creating drift between TFC state and actual cloud state.

**Diagnostic:**
```bash
# Run a refresh-only plan to detect drift
curl -X POST \
  -H "Authorization: Bearer $TFC_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{"data":{"attributes":{"refresh-only":true,
  "auto-apply":false},"type":"runs"}}' \
  "https://app.terraform.io/api/v2/runs"
# Review plan output for out-of-band changes
```
**Fix:**
BAD - Run `terraform apply` and override the drift.
GOOD - Identify the cause of drift; import manually created resources (`terraform import`); establish a policy that all infrastructure changes must go through TFC, enforced by IAM policy denying direct console writes for managed resources.

**Prevention:** Enforce least-privilege IAM: service accounts used by TFC have write access; human IAM roles are read-only. Alert on CloudTrail events for manual writes to Terraform-managed resources.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Terraform Overview - the CLI tool TFC wraps and extends
- Terraform State Backend - the state management problem TFC solves
- CI-CD - the pipeline pattern TFC embeds for infrastructure workflows

**Builds On This (learn these next):**
- Sentinel (Terraform Policy) - the policy engine embedded in TFC for governance
- Atlantis - open-source alternative for PR-based Terraform automation
- Crossplane - Kubernetes-native alternative to TFC for infrastructure management

**Alternatives / Comparisons:**
- Atlantis - open-source, self-hosted, PR-based Terraform automation; no Sentinel, no private registry
- Spacelift - commercial alternative to TFC with multi-IaC support (Terraform, Pulumi, Ansible)
- GitHub Actions + S3 backend - DIY equivalent; more flexible, requires building governance yourself

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS     │ Managed platform wrapping Terraform │
│                │ with governance and collaboration    │
│ PROBLEM        │ Local applies = no audit, no lock,  │
│                │ no access control, no policy        │
│ KEY INSIGHT    │ Workspace = governed IaC unit       │
│ USE WHEN       │ Teams sharing Terraform state+runs  │
│ AVOID WHEN     │ Solo dev, open-source workflows     │
│ TRADE-OFF      │ Governance + safety vs vendor lock  │
│ ONE-LINER      │ Remote exec + state + policy + logs │
│ NEXT EXPLORE   │ Sentinel, Atlantis, Crossplane      │
└─────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(Design Trade-off)** Workspace-per-environment maximises blast-radius isolation but multiplies the number of workspaces to manage. At what scale does workspace sprawl become unmanageable - and what automation (workspace-as-code, dynamic workspaces) would you implement to address it?

2. **(System Interaction)** When a Terraform Cloud run fails mid-apply (e.g., after creating 3 of 5 resources), the state reflects only the partial change. How does TFC handle partial applies, and what manual recovery steps are necessary to resolve the resulting state inconsistency?

3. **(Scale)** Your organisation's Terraform Enterprise instance processes 2,000 runs per day across 300 workspaces. A network partition between TFE and the AWS provider lasts 20 minutes. How many runs are affected, what is their final state, and what runbook steps should be defined in advance to recover safely?
