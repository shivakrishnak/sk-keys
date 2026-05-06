---
layout: default
title: "Terragrunt"
parent: "CI/CD"
nav_order: 2246
permalink: /ci-cd/terragrunt/
number: "2246"
category: CI/CD
difficulty: ★★★
depends_on: Terraform Overview, Terraform Module, Terraform State Backend
used_by: CI-CD
related: Terraform Module, Terraform Reusable Module Pattern, Atlantis
tags:
  - cicd
  - devops
  - advanced
  - bestpractice
---

# 2246 — Terragrunt

⚡ **TL;DR —** Terragrunt is a thin wrapper around Terraform that eliminates DRY violations in multi-environment, multi-account infrastructure configurations through include blocks and dependency management.

| Field | Value |
|---|---|
| **Depends on** | Terraform Overview, Terraform Module, Terraform State Backend |
| **Used by** | CI-CD |
| **Related** | Terraform Module, Terraform Reusable Module Pattern, Atlantis |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** You have 3 environments (dev/staging/prod) × 3 regions × 10 services = 90 Terraform configurations. Each needs identical backend configuration (S3 bucket, DynamoDB table, key path). Each needs the same provider version constraints. You copy-paste backend config 90 times. When the S3 bucket name changes, you update 90 files.

**THE BREAKING POINT:** Backend configuration in Terraform cannot use variables or expressions — it must be literal values. For 90 environments, this means 90 nearly-identical blocks that silently drift apart as engineers make typos or skip files during updates.

**THE INVENTION MOMENT:** Terragrunt introduces `terragrunt.hcl` files with `include` blocks. A root `terragrunt.hcl` contains the backend template with interpolated paths. All 90 child configurations include it with one line. Change the backend template once — all 90 environments update.

---

### 📘 Textbook Definition

**Terragrunt** is an open-source thin wrapper for Terraform (by Gruntwork) that provides DRY backend configurations via `include` blocks, cross-configuration dependencies via `dependency` blocks, multi-module orchestration via `run-all`, remote state backends auto-configured from folder structure, and code generation via `generate` blocks. Terragrunt is configured via `terragrunt.hcl` files and is designed to complement Terraform modules at the organizational deployment layer.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Terragrunt keeps Terraform configurations DRY across dozens of environments and accounts using inheritance and dependency management.

> Terragrunt is like an application framework on top of a library: Terraform is the library (resource management), Terragrunt is the framework (project structure, configuration inheritance, orchestration).

**One insight:** Terragrunt doesn't replace Terraform — it generates Terraform configurations and calls Terraform. The actual `terraform plan` and `apply` are still executed by Terraform itself. Terragrunt handles the configuration layer above Terraform.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `terragrunt.hcl` is the unit of configuration; `include` provides inheritance.
2. Terragrunt generates backend config + provider config from templates at runtime.
3. `dependency` blocks declare inter-configuration dependencies and fetch their outputs.
4. `run-all` executes a Terraform command across multiple configurations in parallel, respecting dependency order.

**DERIVED DESIGN:** Folder structure encodes environment/account/region/service hierarchy. Root `terragrunt.hcl` at the top level contains global config. Leaf `terragrunt.hcl` files include the root and add service-specific config. The folder path itself generates the unique S3 state key.

**THE TRADE-OFFS:**
**Gain:** DRY infrastructure configuration at scale; automatic state key generation from folder structure; dependency-aware multi-module orchestration.
**Cost:** Another tool to learn; debugging requires understanding Terragrunt's config merging; adds indirection between what you write and what Terraform sees.

---

### 🧪 Thought Experiment

**SETUP:** You have 50 environments across dev/staging/prod, each with 20 Terraform modules. Backend configuration must be unique per environment/module combination. Each `terraform` block requires a unique S3 key.

**WHAT HAPPENS WITHOUT TERRAGRUNT:** 50 × 20 = 1,000 `terraform` blocks with unique S3 keys. When the S3 bucket name changes (e.g., company rebrand), update 1,000 files. Miss one, and that environment points to a non-existent bucket. One merge conflict during the update and you have a corrupted state path.

**WHAT HAPPENS WITH TERRAGRUNT:** One root `terragrunt.hcl` with a backend template using `path_relative_to_include()` to generate the unique key from the folder structure. The key for `environments/prod/us-east-1/vpc/terragrunt.hcl` automatically becomes `prod/us-east-1/vpc/terraform.tfstate`. Change the bucket name in one place. Done.

**THE INSIGHT:** Terragrunt converts the folder structure from an organizational convenience into a functional configuration generator. The path *is* the configuration.

---

### 🧠 Mental Model / Analogy

> Terragrunt is like a class hierarchy in OOP applied to infrastructure configuration: the root `terragrunt.hcl` is the base class defining backend, provider, and global defaults; leaf `terragrunt.hcl` files are subclasses that inherit everything and override only what's specific to that service/environment.

- Root `terragrunt.hcl` → abstract base class
- `include "root"` block → class inheritance
- `inputs` block → method override
- `dependency` block → object composition
- `run-all` → batch operation on all instances

Where this analogy breaks down: unlike class inheritance, Terragrunt `include` merges configurations — there's no method resolution order, and conflicts are resolved by deep-merge rules that must be explicitly understood.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):** Terragrunt is a tool that lets you reuse Terraform backend and provider configuration across many environments without copy-pasting it everywhere.

**Level 2 — How to use it (junior developer):** Create a `terragrunt.hcl` in each service directory. Point `terraform.source` at the Terraform module to use. Include a root config for shared backend settings. Run `terragrunt plan/apply` instead of `terraform plan/apply`.

**Level 3 — How it works (mid-level engineer):** Terragrunt reads `terragrunt.hcl`, merges included configs, generates a temporary directory with the merged config, calls `terraform init` (with generated backend config), then calls `terraform plan/apply`. The generated backend config uses interpolated functions like `path_relative_to_include()` to compute unique state paths.

**Level 4 — Why it was designed this way (senior/staff):** Terragrunt was created to solve the limitations of Terraform's backend configuration (no variables allowed) and module source (no version inheritance). By generating Terraform config files at runtime, Terragrunt bypasses these limitations without forking Terraform. The `run-all` command with dependency-aware parallelism enables CI/CD workflows across 100+ configurations without custom orchestration scripts.

---

### ⚙️ How It Works (Mechanism)

**Terragrunt directory structure:**
```
infra-live/
├── terragrunt.hcl           ← root config (backend template)
├── dev/
│   ├── account.hcl          ← account-level config
│   └── us-east-1/
│       ├── region.hcl       ← region-level config
│       └── vpc/
│           └── terragrunt.hcl  ← leaf (includes root)
└── prod/
    ├── account.hcl
    └── us-east-1/
        └── vpc/
            └── terragrunt.hcl
```

**Key Terragrunt functions:**
- `path_relative_to_include()` → relative path from root to current config
- `find_in_parent_folders()` → locate parent configs
- `read_terragrunt_config()` → read a sibling config file
- `get_env()` → read environment variables
- `run_cmd()` → execute shell commands for dynamic values

---

### 🔄 The Complete Picture — End-to-End Flow

**SINGLE MODULE FLOW:**
```
  cd infra-live/prod/us-east-1/vpc/
  terragrunt plan
           │
  Terragrunt reads terragrunt.hcl ← YOU ARE HERE
  Merges with included root config
           │
  Generates backend config:
  key = "prod/us-east-1/vpc/terraform.tfstate"
           │
  Generates provider config
  (from root template)
           │
  Creates temp working dir
  Calls: terraform init -backend-config=...
  Calls: terraform plan
           │
  Plan output shown to engineer
```

**MULTI-MODULE FLOW (`run-all`):**
```
  cd infra-live/prod/
  terragrunt run-all plan
           │
  Discovers all terragrunt.hcl files
  Builds dependency graph
           │
  Parallel plans (respecting deps):
  vpc → subnets → security-groups → eks
           │
  All plan outputs shown
```

**FAILURE PATH:** `dependency` block outputs not available because dependent module hasn't been applied yet. `terragrunt run-all apply` handles this: it applies in dependency order. Manual selective applies may skip deps.

**WHAT CHANGES AT SCALE:** Terragrunt stacks (multiple related configurations) enable atomic multi-service deployments. `--terragrunt-parallelism` limits concurrent applies. Integration with Atlantis provides PR-based Terragrunt workflows.

---

### 💻 Code Example

```hcl
# --- ROOT: infra-live/terragrunt.hcl ---
locals {
  account_vars = read_terragrunt_config(
    find_in_parent_folders("account.hcl"))
  region_vars = read_terragrunt_config(
    find_in_parent_folders("region.hcl"))

  account_id = local.account_vars.locals.account_id
  aws_region = local.region_vars.locals.aws_region
}

# Remote state backend — generated automatically
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = "mycompany-tf-state-${local.account_id}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = local.aws_region
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Provider generation — no copy-paste needed
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  assume_role {
    role_arn = "arn:aws:iam::${local.account_id}:role/terraform"
  }
}
EOF
}
```

```hcl
# --- ACCOUNT LEVEL: infra-live/prod/account.hcl ---
locals {
  account_id   = "123456789012"
  account_name = "prod"
}
```

```hcl
# --- REGION LEVEL: infra-live/prod/us-east-1/region.hcl ---
locals {
  aws_region = "us-east-1"
}
```

```hcl
# --- LEAF: infra-live/prod/us-east-1/vpc/terragrunt.hcl ---

# Include root config (inherits backend + provider)
include "root" {
  path = find_in_parent_folders()
}

# Point at the Terraform module
terraform {
  source = "git::https://github.com/myorg/terraform-aws-vpc.git?ref=v2.1.0"
}

# Input variables for this instance
inputs = {
  cidr_block       = "10.0.0.0/16"
  environment      = "prod"
  enable_flow_logs = true
}
```

```hcl
# --- LEAF WITH DEPENDENCY ---
# infra-live/prod/us-east-1/eks/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

# Declare dependency on VPC
dependency "vpc" {
  config_path = "../vpc"

  # Mock outputs for plan when vpc not yet applied
  mock_outputs = {
    vpc_id         = "vpc-mock123"
    private_subnet_ids = ["subnet-mock1", "subnet-mock2"]
  }
  mock_outputs_allowed_terraform_commands = ["plan", "validate"]
}

terraform {
  source = "git::https://github.com/myorg/terraform-aws-eks.git?ref=v3.0.0"
}

inputs = {
  cluster_name       = "prod-eks"
  vpc_id             = dependency.vpc.outputs.vpc_id
  subnet_ids         = dependency.vpc.outputs.private_subnet_ids
  kubernetes_version = "1.29"
}
```

---

### ⚖️ Comparison Table

| Feature | Terragrunt | Raw Terraform | Terraform Workspaces | Terraform Cloud |
|---|---|---|---|---|
| **DRY backend config** | ✅ | ❌ (manual per env) | Partial | ✅ |
| **Cross-module deps** | ✅ dependency blocks | Manual remote state | ❌ | Partial |
| **Multi-module apply** | ✅ run-all | Manual scripts | ❌ | Partial |
| **State path automation** | ✅ path_relative_to_include | Manual | Partial | ✅ |
| **Learning curve** | Medium | Low | Low | Low |
| **Open source** | ✅ | ✅ | ✅ | ❌ |
| **Best for** | Large multi-env orgs | Small teams | Simple envs | Managed SaaS |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Terragrunt replaces Terraform" | Terragrunt wraps and generates configs for Terraform. All `terraform` commands are still executed by Terraform itself. |
| "`run-all apply` is always safe" | `run-all apply` applies all configurations in the tree in dependency order. Use with care in production — scope with `--terragrunt-include-dir`. |
| "Terragrunt is maintained by HashiCorp" | Terragrunt is maintained by Gruntwork, an independent company. It is not an official HashiCorp product. |
| "Terragrunt and Terraform Cloud are alternatives" | They solve different problems and can be used together. Terragrunt handles config DRY; Terraform Cloud handles remote execution and state management. |
| "mock_outputs in dependency blocks are safe" | Mock outputs allow plans to run before dependencies are applied. Applying with mock outputs in place can create incorrect resources. Use `mock_outputs_allowed_terraform_commands` to restrict to plan/validate only. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `dependency` Output Not Available**
- **Symptom:** `Error: dependency output "vpc_id" not found` during `terragrunt apply`
- **Root Cause:** Dependent module (VPC) hasn't been applied yet; no real outputs available
- **Diagnostic:**
```bash
cd infra-live/prod/us-east-1/vpc
terragrunt output
```
- **Fix:** Apply the dependency first: `cd vpc && terragrunt apply`. Then apply the dependent config.
- **Prevention:** Use `terragrunt run-all apply` which handles dependency ordering automatically.

**Mode 2: Config Merge Conflict**
- **Symptom:** Backend config has wrong region; root `generate` block overridden unexpectedly
- **Root Cause:** Child config has a conflicting `generate "provider"` block that shadows root's
- **Diagnostic:**
```bash
terragrunt render-json  # shows merged config
```
- **Fix:** Remove conflicting blocks from child; use `inputs` for environment-specific values only.
- **Prevention:** Define strict conventions: root config owns backend and provider generation; children own module source and inputs only.

**Mode 3: `run-all` Partial Failure**
- **Symptom:** `terragrunt run-all apply` applies 40 of 50 modules, fails on 10, leaves state inconsistent
- **Root Cause:** Provider API error, permission denied, or configuration error in 10 modules
- **Diagnostic:**
```bash
terragrunt run-all apply 2>&1 | grep "Error"
# Review each failed module individually
```
- **Fix:** Apply failed modules individually to isolate and fix each error.
- **Prevention:** Run `terragrunt run-all plan` first; review all plans before `run-all apply`; use `--terragrunt-parallelism 1` for initial large deploys.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Overview, Terraform Module, Terraform State Backend

**Builds On This (learn these next):** Terraform Reusable Module Pattern, CI-CD, Atlantis

**Alternatives / Comparisons:** Terraform Workspaces, Terraform Cloud, Pulumi stacks, CDK pipelines

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ DRY wrapper for multi-env Terraform  │
│ PROBLEM       │ 90 copy-pasted backend config blocks │
│ KEY INSIGHT   │ Folder path generates state key;     │
│               │ include = config inheritance         │
│ USE WHEN      │ Multi-env/account at scale           │
│ AVOID WHEN    │ Single env; Terraform Cloud users    │
│ TRADE-OFF     │ DRY + orchestration vs extra tooling │
│ ONE-LINER     │ terragrunt run-all plan              │
│ NEXT EXPLORE  │ Atlantis, Terraform Reusable Modules │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** Terragrunt's `dependency` block fetches outputs from another module's state. If the dependency module's state is stored in a different AWS account, what IAM configuration is needed for the dependent module to read those outputs, and how does this cross-account access pattern interact with the provider `assume_role` configuration generated by Terragrunt's root config?

2. **(Scale)** An organization uses `terragrunt run-all apply` to deploy changes across 200 configurations. A bug in one leaf configuration causes it to destroy a production database. What process controls (plan review, blast radius limiting, apply scope restrictions) would you implement to prevent `run-all apply` from causing unintended widespread destruction?

3. **(Design Trade-off)** Terragrunt adds a layer of abstraction between the engineer and raw Terraform. When debugging a `terraform plan` error, the engineer must understand both Terragrunt's config merging and Terraform's plan computation. What are the specific debugging techniques and tools that reduce this cognitive burden, and what is the break-even point where Terragrunt's organizational benefits justify this complexity?
