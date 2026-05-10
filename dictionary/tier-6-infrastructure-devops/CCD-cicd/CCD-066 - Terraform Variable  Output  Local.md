---
version: 2
layout: default
title: "Terraform Variable  Output  Local"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 66
permalink: /ci-cd/terraform-variable-output-local/
id: CCD-066
category: CI/CD
difficulty: ★★☆
depends_on: Terraform Overview
used_by: Terraform Module, Terraform Remote State
related: Terraform Module, Terraform Data Source
tags:
  - cicd
  - devops
  - intermediate
---

# CCD-066 - Terraform Variable  Output  Local

⚡ **TL;DR -** Variables are configuration inputs, outputs are exported values, and locals are computed expressions - the three building blocks of Terraform's parameterization system.

| Field | Value |
|---|---|
| **Depends on** | Terraform Overview |
| **Used by** | Terraform Module, Terraform Remote State |
| **Related** | Terraform Module, Terraform Data Source |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every environment (dev, staging, prod) requires a separate, nearly-identical copy of the entire HCL configuration with hardcoded values changed. Instance types, CIDR ranges, and environment names are scattered throughout 500 lines of HCL. Changing "dev" to "staging" means a grep-and-replace across 50 files.

**THE BREAKING POINT:** A production CIDR is changed in one file but missed in another. A security group rule references the wrong CIDR. An outage ensues from a misconfiguration that a parameterized design would have made impossible.

**THE INVENTION MOMENT:** Terraform variables allow the same HCL to be instantiated with different values. Locals compute derived values once and reference them everywhere. Outputs export values to callers or other configurations.

---

### 📘 Textbook Definition

**Input variables** (`variable` blocks) define configurable parameters for a Terraform configuration or module, with optional type constraints, default values, validation rules, and sensitivity markers. **Output values** (`output` blocks) export computed values for display, use by parent modules, or consumption via `terraform_remote_state`. **Local values** (`locals` block) define named computed expressions that reduce repetition and centralize complex logic within a configuration.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Variables are inputs, locals are intermediate computations, outputs are return values.

> In a Terraform configuration, variables are the arguments you pass to a function, locals are the temporary variables inside the function body, and outputs are the values the function returns.

**One insight:** The **precedence order** for variable values matters in practice: CLI flags override environment variables override `.tfvars` files override defaults. In CI/CD, environment variables (`TF_VAR_name`) are the most common injection mechanism.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Input variables are immutable during a single plan/apply cycle.
2. Locals are re-evaluated on each plan - they are expressions, not persistent values.
3. Output values are written to state and accessible to parent modules and `terraform_remote_state`.
4. Sensitive values marked `sensitive = true` are redacted in plan/apply output but still exist in state.

**DERIVED DESIGN:** Variables + locals + outputs form a complete parameterization system. Variables are the public interface; locals are the private implementation; outputs are the published results. This mirrors function signature + body + return value.

**THE TRADE-OFFS:**
**Gain:** DRY configurations; environment-specific parameters without code duplication; clean module interfaces.
**Cost:** Too many variables create cognitive load; complex local expressions can be hard to debug; sensitive outputs in state require secure backend.

---

### 🧪 Thought Experiment

**SETUP:** You have a VPC module used by dev, staging, and prod environments. The only differences are the CIDR block, instance sizes, and whether flow logs are enabled.

**WHAT HAPPENS WITHOUT VARIABLES:** Three copies of the VPC HCL, 95% identical. A security patch requires changes to all three. One copy gets missed. Dev has a different flow log configuration than prod. Six months later, you can't tell if the differences are intentional.

**WHAT HAPPENS WITH VARIABLES:** One VPC module. Three sets of `.tfvars` files. The security patch is applied once to the module. All three environments get it on their next upgrade. The differences are documented explicitly in variables - no guessing.

**THE INSIGHT:** Variables make the configuration's *intention* explicit. What changes between environments is declared; what doesn't change is implicit. This is far more readable than three nearly-identical copies.

---

### 🧠 Mental Model / Analogy

> Variables, locals, and outputs are like the three-tier structure of a well-designed function: the function signature (variables) defines what can be customized; the function body (locals) contains the implementation logic; the return value (outputs) defines what the caller receives.

- `variable "cidr" {}` → function parameter
- `locals { env_prefix = "${var.env}-${var.region}" }` → local variable
- `output "vpc_id" {}` → return value
- `.tfvars` file → function call arguments
- `sensitive = true` → secret parameter (not printed)

Where this analogy breaks down: unlike function parameters, Terraform variables can be set from multiple sources (files, env vars, CLI flags) with a defined precedence order that can cause surprises if not understood.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Variables let you reuse the same Terraform code with different settings. Outputs let you share computed values. Locals let you avoid repeating complex expressions.

**Level 2 - How to use it (junior developer):** Declare `variable "env" { type = string }`. Set it in `terraform.tfvars`: `env = "prod"`. Reference it as `var.env`. Create a `local` for repeated expressions: `locals { name_prefix = "${var.app}-${var.env}" }`. Declare `output "bucket_arn"` to export computed values.

**Level 3 - How it works (mid-level engineer):** Terraform evaluates variable values at the start of each plan using the precedence order. Locals are lazy-evaluated expressions, recomputed each plan. Outputs are written to state after apply; they're accessible in parent modules as `module.<name>.<output>` and via `terraform_remote_state`.

**Level 4 - Why it was designed this way (senior/staff):** Variable validation blocks run at plan time and provide clear error messages before any API calls. The `sensitive` marker was added specifically because secrets were being leaked in CI logs. The `nullable = false` constraint enforces that modules receive real values, not null. `precondition`/`postcondition` blocks add contract-based validation to resources and outputs - extending the concept of validation beyond inputs to correctness assertions about outputs.

---

### ⚙️ How It Works (Mechanism)

**Variable value precedence (highest to lowest):**
1. CLI flag: `-var="key=value"`
2. CLI var file: `-var-file=custom.tfvars`
3. `*.auto.tfvars` files (alphabetical)
4. `terraform.tfvars.json`
5. `terraform.tfvars`
6. Environment variables: `TF_VAR_<name>`
7. Default in `variable` block

**Sensitive variable handling:**
- Marked with `sensitive = true`
- Redacted as `(sensitive value)` in plan/apply output
- Still stored in state (plaintext in `terraform.tfstate`)
- Must protect backend storage

---

### 🔄 The Complete Picture - End-to-End Flow

**VARIABLE RESOLUTION FLOW:**
```
  terraform apply -var="env=prod"     ← YOU ARE HERE
           │
  Terraform resolves variable values:
  CLI flags > auto.tfvars > tfvars > env vars > defaults
           │
  Validation blocks run:
  error_message shown if invalid
           │
  Locals evaluated (lazy)
  locals { prefix = "${var.app}-${var.env}" }
           │
  Resources reference var.* and local.*
  throughout configuration
           │
  Apply completes → outputs written to state
           │
  Parent module: module.child.vpc_id
  Remote state: data.terraform_remote_state.X.outputs.vpc_id
```

**FAILURE PATH:** Variable passed as string but type constraint is `list(string)`. Plan fails immediately with type error - before any API calls. This is a feature: validate inputs early.

**WHAT CHANGES AT SCALE:** Large modules with 30+ variables become hard to use. Use variable grouping (objects instead of many flat variables), provide rich descriptions and examples, and generate documentation automatically with `terraform-docs`.

---

### 💻 Code Example

```hcl
# variables.tf - input interface
variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev","staging","prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}

variable "vpc_config" {
  type = object({
    cidr           = string
    azs            = list(string)
    enable_nat     = bool
  })
  description = "VPC configuration object"
}

variable "db_password" {
  type        = string
  sensitive   = true   # redacted in plan output; still in state
  description = "RDS master password"
}

variable "tags" {
  type    = map(string)
  default = {}
}

# locals.tf - derived computations (DRY)
locals {
  # Merge caller tags with mandatory org tags
  common_tags = merge(var.tags, {
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = "platform"
  })

  # Derived name prefix
  name_prefix = "myapp-${var.environment}"

  # Environment flag
  is_prod = var.environment == "prod"
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_config.cidr

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

resource "aws_nat_gateway" "main" {
  count         = local.is_prod ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
}

# outputs.tf - export interface
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID for consumer configurations"
}

output "vpc_cidr" {
  value       = aws_vpc.main.cidr_block
}

output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true  # redacted in plan output
}
```

```bash
# Setting variables - multiple methods
# Method 1: .tfvars file
cat prod.tfvars
# environment = "prod"
# vpc_config = { cidr = "10.0.0.0/16", azs = ["us-east-1a"], enable_nat = true }

terraform apply -var-file=prod.tfvars

# Method 2: Environment variable (CI/CD)
export TF_VAR_environment="prod"
export TF_VAR_db_password="$(aws secretsmanager get-secret-value ...)"
terraform apply

# Method 3: CLI flags (for one-off overrides)
terraform apply -var='environment=staging'
```

---

### ⚖️ Comparison Table

| Concept | `variable` | `local` | `output` | `data` |
|---|---|---|---|---|
| **Direction** | Input (caller → module) | Internal | Output (module → caller) | External read |
| **In state** | ❌ | ❌ | ✅ | ❌ |
| **Can be sensitive** | ✅ | ❌ (derived from var) | ✅ | ❌ |
| **Validated** | ✅ validation blocks | ❌ | ✅ precondition | ❌ |
| **Scope** | Module-level | Module-level | Module-level + parent | Module-level |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Sensitive variables are encrypted in state" | `sensitive = true` only suppresses plan/apply output logging. State stores the value in plaintext. Secure your backend. |
| "Variables can reference other variables" | Variables cannot reference each other. Use `locals` for derived values. |
| "Outputs are always available immediately" | Outputs with `(known after apply)` values are only available after the apply completes. |
| "`terraform.tfvars` is automatically used" | Yes, but only if the file is named exactly `terraform.tfvars` or `*.auto.tfvars`. Other names require `-var-file`. |
| "Locals reduce plan time" | Locals are evaluated at plan time - they don't save API calls. They reduce HCL repetition, not execution time. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Sensitive Variable Leaked in CI Logs**
- **Symptom:** Database password appears in CI pipeline logs in plaintext
- **Root Cause:** Variable passed as `-var="db_password=..."` or not marked `sensitive = true`
- **Diagnostic:** Search CI logs for known secret patterns.
- **Fix:** Mark variable `sensitive = true`; inject via environment variable `TF_VAR_db_password`; use a secrets manager (AWS Secrets Manager → `data` source).
- **Prevention:** Never pass secrets via CLI flags; use OIDC + secrets manager for CI.

**Mode 2: Variable Validation Not Catching Invalid Input**
- **Symptom:** `environment = "production"` instead of `"prod"` causes subtle downstream bugs
- **Root Cause:** Validation block not defined or condition too permissive
- **Diagnostic:** Review `variable` blocks for missing `validation` blocks.
- **Fix:** Add explicit `validation` block with `contains()` or regex check.
- **Prevention:** Validate all variables that are used as conditional logic keys.

**Mode 3: Output Not Available to Parent Module**
- **Symptom:** `module.vpc.subnet_ids` returns an error in parent configuration
- **Root Cause:** Child module doesn't declare a `subnet_ids` output block
- **Diagnostic:**
```bash
cd modules/vpc
cat outputs.tf  # check output declarations
```
- **Fix:** Add the missing output block to the child module.
- **Prevention:** Design module outputs as part of the interface spec before implementation; document with `terraform-docs`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Overview, Terraform Resource

**Builds On This (learn these next):** Terraform Module, Terraform Remote State, Terraform Data Source

**Alternatives / Comparisons:** Ansible variables, CloudFormation parameters/outputs, Pulumi config

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Variables=input, locals=computed,    │
│               │ outputs=exported values              │
│ PROBLEM       │ Hardcoded values across environments │
│ KEY INSIGHT   │ sensitive=true ≠ encrypted in state  │
│ USE WHEN      │ Any parameterized configuration      │
│ AVOID WHEN    │ Excessive variables obscure intent   │
│ TRADE-OFF     │ Flexibility vs interface complexity  │
│ ONE-LINER     │ var.env  local.prefix  output.vpc_id │
│ NEXT EXPLORE  │ Terraform Module, Data Source        │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A module accepts a `db_password` variable marked `sensitive = true`. The password is stored in AWS Secrets Manager. What are the two approaches to getting the secret into Terraform (environment variable injection vs `data "aws_secretsmanager_secret_version"` data source), and what are the security and operational trade-offs of each?

2. **(First Principles)** Terraform's `sensitive = true` prevents values from appearing in plan/apply output but stores them in state in plaintext. Given this fundamental limitation, what is the complete set of controls an organization should implement to protect sensitive values that Terraform must handle?

3. **(Design Trade-off)** A Terraform module has 40 input variables because it tries to expose every configurable aspect of the underlying resources. A different module has 5 variables with opinionated defaults. What are the trade-offs between these two design philosophies in terms of usability, governance, and maintenance burden?
