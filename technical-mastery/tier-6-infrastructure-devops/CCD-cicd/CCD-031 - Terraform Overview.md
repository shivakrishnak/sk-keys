---
version: 2
layout: default
title: "Terraform Overview"
parent: "CI/CD"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/ci-cd/terraform-overview/
id: CCD-022
category: CI/CD
difficulty: ★★☆
depends_on: Infrastructure as Code, HashiCorp Configuration Language (HCL), Cloud - AWS
used_by: Terraform Provider, Terraform State, CI-CD
related: AWS CloudFormation, Pulumi, Ansible
tags:
  - cicd
  - devops
  - intermediate
  - cloud
  - aws
---

⚡ **TL;DR -** Terraform provisions and manages cloud infrastructure declaratively using HCL config files, a provider plugin system, and a state file.

| Field | Value |
|---|---|
| **Depends on** | Infrastructure as Code, HashiCorp Configuration Language (HCL), Cloud - AWS |
| **Used by** | Terraform Provider, Terraform State, CI-CD |
| **Related** | AWS CloudFormation, Pulumi, Ansible |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Engineers provision infrastructure by clicking cloud consoles. No record exists of what was created, why, or how to recreate it. Disaster recovery means re-clicking from memory while the business burns.

**THE BREAKING POINT:** A team of ten engineers makes ad-hoc console changes to AWS. Nobody knows the true current state. Two environments that should be identical diverge silently. A failing prod resource can't be recreated because the person who built it left the company.

**THE INVENTION MOMENT:** HashiCorp releases Terraform in 2014. Infrastructure becomes text files - committed to Git, reviewed in pull requests, applied by a machine. The console becomes read-only by policy.

---

### 📘 Textbook Definition

**Terraform** is an open-source Infrastructure as Code (IaC) tool by HashiCorp that enables engineers to define, provision, and manage cloud and on-premises infrastructure resources using a declarative configuration language (HCL). Terraform tracks the current state of managed infrastructure in a state file and computes the minimum change set needed to reconcile the actual state with the desired configuration.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Declare the infrastructure you want; Terraform figures out what to create, change, or delete.

> Terraform is a recipe for your cloud: you write which dishes you want, and Terraform checks what's already on the stove, adjusts what needs changing, and removes what's no longer needed.

**One insight:** The power is not in creation - it's in the **diff**. Terraform knows what *already exists* (via state) and computes *only the delta needed*. That delta is the `plan`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Infrastructure state is a function of declared configuration, not manual actions.
2. The desired state (HCL) must always be reconcilable with the actual state (cloud APIs).
3. Every resource is represented by a lifecycle: create → read → update → delete.
4. State is the authoritative record of what Terraform manages.

**DERIVED DESIGN:** Terraform builds a directed acyclic graph (DAG) from resource declarations, queries provider APIs for current state, diffs desired vs actual, then executes changes in topological order respecting dependencies.

**THE TRADE-OFFS:**

**Gain:** Repeatable, reviewable, version-controlled infrastructure; DR from `terraform apply`.

**Cost:** State file is a critical piece of shared infrastructure that must be protected and managed.

---

### 🧪 Thought Experiment

**SETUP:** You need 3 AWS VPCs, 6 subnets, 2 RDS clusters, and an EKS cluster for your platform team.

**WHAT HAPPENS WITHOUT TERRAFORM:** You click through the console. Weeks later a colleague needs to replicate the environment for staging. They ask what you clicked. Some of it was written down. The second environment is 80% similar but mysteriously different in ways that only surface at 2 AM during an incident.

**WHAT HAPPENS WITH TERRAFORM:** You write HCL. Both environments are created from the same code with different variable values. A `terraform plan` on either shows exactly what would change. A new engineer can read the code and understand the entire infrastructure in one sitting.

**THE INSIGHT:** Terraform doesn't just provision infrastructure - it makes infrastructure *auditable*, *reproducible*, and *collaborative*.

---

### 🧠 Mental Model / Analogy

> Terraform is like Git for your cloud: HCL files are the source code (what you want), the state file is the index (what Terraform thinks exists), and `terraform apply` is the commit that reconciles the world with your intent.

- HCL files → source code (desired state)
- State file → Git index (tracked reality)
- Provider plugin → language runtime (cloud API adapter)
- `terraform plan` → `git diff` (what will change)
- `terraform apply` → commit + push (make it real)

Where this analogy breaks down: unlike Git, the state file is not human-editable and must be treated as a database, not a text file.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Terraform is a tool that creates cloud infrastructure (servers, databases, networks) from a text file. You describe what you want and it builds it - consistently, every time.

**Level 2 - How to use it (junior developer):** Write `.tf` files with resource blocks in HCL. Run `terraform init` to download providers. Run `terraform plan` to preview changes. Run `terraform apply` to execute. Run `terraform destroy` to tear everything down.

**Level 3 - How it works (mid-level engineer):** Terraform builds a DAG of resources, calls each provider plugin to read current state, diffs desired vs actual state, then executes creates/updates/deletes in topological order. The state file is updated atomically after each operation.

**Level 4 - Why it was designed this way (senior/staff):** The declarative model separates *intent* from *execution*. The plan/apply split gives operators a human-approval gate before mutation. Provider plugins decouple the core engine from cloud-specific API knowledge, enabling one workflow across 3,000+ providers. External state enables team collaboration without configuration coupling.

---

### ⚙️ How It Works (Mechanism)

Terraform operates in four phases during a plan/apply cycle:

1. **Init** - Download provider plugins and modules; configure backend.
2. **Refresh** - Call provider Read APIs to discover current resource state; reconcile with stored state.
3. **Plan** - Diff desired configuration (HCL) against refreshed state; generate ordered create/update/delete operations; output human-readable plan.
4. **Apply** - Execute operations respecting DAG dependency order; call provider Create/Update/Delete APIs; write updated state to backend atomically.

Provider plugins are Go binaries communicating with Terraform core via gRPC using the Terraform Plugin Protocol v6. Each provider implements `Create`, `Read`, `Update`, `Delete`, and `Import` for every resource type.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Engineer writes .tf files
           │
  git commit → PR review
           │
  CI: terraform init
           │
  CI: terraform plan      ← YOU ARE HERE
           │
  Plan output reviewed/approved
           │
  CI: terraform apply
           │
  State written to S3 backend
           │
  Resources live in cloud
```

**FAILURE PATH:** Apply fails mid-run. Some resources created, others not. Terraform marks the failed resource as `tainted`. Next plan shows it for replacement. Partially created resources (e.g. VPC with no subnets) may need manual cleanup.

**WHAT CHANGES AT SCALE:** State contention requires locking (DynamoDB). Large state files slow plans. Separate state roots per team or service isolate blast radius. Atlantis or Terraform Cloud add PR-based approval workflows.

---

### 💻 Code Example

```hcl
# BAD: ad-hoc, undocumented, unreviewed console clicks
# (no record of what was created or how)

# GOOD: declarative, version-controlled Terraform config
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "my-tf-state-prod"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region to deploy into"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name      = "main-vpc"
    ManagedBy = "terraform"
  }
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "Main VPC ID"
}
```

---

### ⚖️ Comparison Table

| Feature | Terraform | AWS CloudFormation | Pulumi | Ansible |
|---|---|---|---|---|
| **Language** | HCL | JSON/YAML | Python/TS/Go | YAML |
| **Multi-cloud** | ✅ 3,000+ providers | ❌ AWS only | ✅ | ✅ |
| **State management** | Explicit (tfstate) | Managed by AWS | Explicit | Stateless |
| **Plan/preview** | `terraform plan` | Change sets | `pulumi preview` | `--check` |
| **Drift detection** | `terraform plan` | Native drift | `pulumi refresh` | Limited |
| **Maturity** | High (2014) | High (2011) | Medium (2018) | High (2012) |
| **Best for** | Multi-cloud IaC | AWS-only orgs | Dev-centric IaC | Config mgmt |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Terraform is idempotent by default" | Only for resources Terraform manages. Console changes create drift that plan detects but doesn't auto-remediate. |
| "The state file is just a cache" | State is authoritative. Losing it without backup means Terraform loses track of all managed resources. |
| "Destroying and recreating is always safe" | RDS, S3, and stateful resources hold data. `prevent_destroy` lifecycle guards must be set explicitly. |
| "Terraform applies all changes in parallel" | Only independent resources. Dependencies are applied sequentially per the computed DAG. |
| "`terraform plan` is completely read-only" | The refresh phase calls provider Read APIs and can update state entries if resources drifted. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: State Lock Not Released**
- **Symptom:** `Error acquiring the state lock` on every plan/apply attempt
- **Root Cause:** Previous apply crashed mid-run; DynamoDB lock record not cleaned up
- **Diagnostic:**
```bash
terraform force-unlock <LOCK_ID>
aws dynamodb scan --table-name terraform-lock
```
- **Fix - BAD:** Delete the DynamoDB lock item manually without investigation.
- **Fix - GOOD:** Confirm no apply is actually running, then `terraform force-unlock <LOCK_ID>`.
- **Prevention:** Monitor CI pipelines for crashed applies; set `LockTimeoutSeconds` in backend config.

**Mode 2: Configuration Drift**
- **Symptom:** `terraform plan` shows unexpected diffs despite no HCL changes
- **Root Cause:** Manual change made in AWS console or by another automation tool
- **Diagnostic:**
```bash
terraform plan -refresh-only
# Shows exactly which attributes drifted
```
- **Fix:** Update HCL to match intended state, then `terraform apply` to converge.
- **Prevention:** IAM SCPs blocking console writes; enforce all changes through Terraform.

**Mode 3: Provider API Rate Limiting**
- **Symptom:** `Error: rate limit exceeded` during large applies
- **Root Cause:** Default `-parallelism=10` floods provider APIs with concurrent calls
- **Diagnostic:**
```bash
terraform apply -parallelism=3
```
- **Fix:** Reduce parallelism; use `depends_on` to serialize critical resource groups.
- **Prevention:** Set parallelism per environment size; configure provider-level retry settings.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Infrastructure as Code, HashiCorp Configuration Language (HCL), Cloud - AWS

**Builds On This (learn these next):** Terraform Provider, Terraform State, Terraform Module, Terraform Plan / Apply / Destroy

**Alternatives / Comparisons:** AWS CloudFormation, Pulumi, Ansible

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Declarative IaC tool by HashiCorp    │
│ PROBLEM       │ Manual, untracked cloud infra        │
│ KEY INSIGHT   │ plan = diff(desired, actual state)   │
│ USE WHEN      │ Multi-cloud; team-managed infra      │
│ AVOID WHEN    │ One-off scripts; AWS-only + CFN      │
│ TRADE-OFF     │ State complexity vs reproducibility  │
│ ONE-LINER     │ terraform init && plan && apply      │
│ NEXT EXPLORE  │ Terraform State, Terraform Provider  │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** If two engineers run `terraform apply` simultaneously against the same state backend without locking, what specific failure modes can occur at the state file level, and how does Terraform's DynamoDB locking prevent each one?

2. **(Scale)** A platform team has 800 resources in a single Terraform state file. Plans take 12 minutes. What structural changes to the configuration would reduce plan times, and what new operational challenges does each approach introduce?

3. **(Design Trade-off)** Terraform can only manage resources it knows about via state. What are the risks of having unmanaged "shadow" resources in the same AWS account as Terraform-managed resources, and how should a team safely bring those resources under Terraform management?
