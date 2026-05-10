---
version: 2
layout: default
title: "Terraform Module"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /ci-cd/terraform-module/
id: CCD-061
category: CI/CD
difficulty: ★★★
depends_on: Terraform Resource, Terraform Overview
used_by: Terraform Reusable Module Pattern
related: Terraform Reusable Module Pattern, Terraform Remote State, Terraform Registry
tags:
  - cicd
  - devops
  - advanced
  - pattern
---

# CCD-061 - Terraform Module

⚡ **TL;DR -** A Terraform module is a reusable package of HCL resources with defined inputs (variables) and outputs, callable from other configurations.

| Field | Value |
|---|---|
| **Depends on** | Terraform Resource, Terraform Overview |
| **Used by** | Terraform Reusable Module Pattern |
| **Related** | Terraform Reusable Module Pattern, Terraform Remote State, Terraform Registry |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every team that needs an S3 bucket with versioning, encryption, public access blocking, and lifecycle policies copies those 40 lines of HCL into their configuration. Six months later, the security team finds a missing policy. They must find and fix all 23 copies across the organization.

**THE BREAKING POINT:** A copy-paste security vulnerability in infrastructure code, now duplicated across 23 repositories, is discovered in a security audit. Patching takes weeks because each team has slightly customized their copy.

**THE INVENTION MOMENT:** Terraform modules encapsulate HCL resources behind a clean interface of input variables and output values. Callers invoke the module with their specific parameters. The implementation lives in one place. Security patches to the module propagate to all callers on version upgrade.

---

### 📘 Textbook Definition

A **Terraform module** is a directory of `.tf` files with declared input variables and output values, designed to be instantiated from a parent configuration (the "root module") or from other modules. Modules are called via `module` blocks with source references (local path, Git URL, or Terraform Registry address) and version constraints. Each module call creates an isolated namespace of resources. Every Terraform configuration is itself a module (the root module).

---

### ⏱️ Understand It in 30 Seconds

**One line:** A module is a function for infrastructure: inputs go in, resources get created, outputs come back.

> A Terraform module is like a Lego set: you get a self-contained package with defined connection points (input variables). You plug it into your build where you need it without caring how the internal pieces fit together.

**One insight:** Every Terraform configuration is already a module - the "root module." Calling a child module is just nesting modules. There is no fundamental difference between root and child modules except invocation context.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A module is a directory with `.tf` files - it has no magic syntax of its own.
2. Modules communicate via input variables (the interface) and outputs (the return values).
3. Module instances are isolated namespaces - resource addresses inside a module are prefixed with `module.<name>`.
4. Modules have no access to their caller's resources unless explicitly passed as variables.

**DERIVED DESIGN:** Module versioning uses Git tags or the Terraform Registry's semantic versioning. Version constraints (e.g. `~> 1.0`) prevent unexpected breaking changes. The module's `variables.tf`, `outputs.tf`, and `main.tf` form the public interface.

**THE TRADE-OFFS:**
**Gain:** DRY infrastructure code; centralized security patching; standardized resource patterns.
**Cost:** Module abstraction can hide complexity; over-modularization creates indirection that makes debugging harder; module version upgrades require coordination.

---

### 🧪 Thought Experiment

**SETUP:** Your organization creates 50 VPCs across 15 teams. Each needs the same security: flow logs enabled, DHCP options set, DNS hostnames enabled, and specific NACL rules.

**WHAT HAPPENS WITHOUT MODULES:** Each of the 15 teams copies the VPC HCL. When the security team adds a required NACL rule, they open 15 pull requests, argue with 15 teams, and spend three weeks on a two-line change.

**WHAT HAPPENS WITH A MODULE:** One `terraform-aws-vpc` module. All 15 teams call it with their CIDR and tag values. The security team adds the NACL rule in one PR to the module. Teams upgrade to the new module version on their schedule. Zero arguments about the security requirement.

**THE INSIGHT:** Modules are not just about DRY code - they're about *governance*. The module owner can enforce organizational standards that callers cannot opt out of.

---

### 🧠 Mental Model / Analogy

> A Terraform module is like a function with named parameters and a return value. `variables.tf` defines the function signature; `outputs.tf` defines the return type; `main.tf` is the function body.

- `variables.tf` → function parameters (input)
- `outputs.tf` → return values (output)
- `main.tf` → function body (implementation)
- Module call block → function invocation
- Module version → function library version

Where this analogy breaks down: unlike a function, a module is not executed and returned - it declares persistent infrastructure objects. "Calling" a module creates real cloud resources that outlive the Terraform process.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** A module is a reusable Terraform "recipe" you can use in multiple projects. Like a shared template - you provide the custom parts (variables), it handles the details.

**Level 2 - How to use it (junior developer):** Create a `module "name" { source = "path" }` block with the module's required input variables. Run `terraform init` to download the module. Reference its outputs via `module.<name>.<output>`.

**Level 3 - How it works (mid-level engineer):** Module resources appear in state with addresses like `module.vpc.aws_vpc.main`. During `terraform init`, modules from the registry or Git are downloaded to `.terraform/modules/`. Module instances are isolated namespaces. The `count` and `for_each` meta-arguments on a `module` block create multiple instances.

**Level 4 - Why it was designed this way (senior/staff):** The module system gives Terraform composition without inheritance. Module interfaces (variables/outputs) are explicit and version-controlled. The Terraform Registry provides discoverability and provenance. The design intentionally limits module access to the caller's scope - modules can't "reach up" to access root-level variables, enforcing clean interfaces.

---

### ⚙️ How It Works (Mechanism)

**Module sources:**
- **Local path:** `source = "./modules/vpc"` - no download; used as-is
- **Registry:** `source = "hashicorp/consul/aws"` - downloaded from `registry.terraform.io`
- **Git URL:** `source = "git::https://github.com/org/module.git?ref=v1.2.0"`
- **GitHub shorthand:** `source = "github.com/org/module"`

**Module init flow:**
1. `terraform init` reads all `module` blocks
2. Downloads and caches modules to `.terraform/modules/`
3. Generates `.terraform/modules/modules.json` with resolved source + version

**Resource addressing:** `module.<module_call_name>.<resource_type>.<resource_name>`

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Root module: module "vpc" {
    source  = "app.terraform.io/org/vpc/aws"
    version = "~> 2.0"          ← YOU ARE HERE
    cidr    = "10.0.0.0/16"
  }
           │
  terraform init
  → downloads module to .terraform/modules/
           │
  terraform plan
  → expands module resources into DAG
  → module.vpc.aws_vpc.main
  → module.vpc.aws_subnet.private[*]
           │
  terraform apply
  → creates all module resources
  → module outputs available
           │
  output: module.vpc.vpc_id
```

**FAILURE PATH:** Module source is a Git URL without a version pin. Upstream module adds a breaking change. `terraform init` pulls the new breaking version. Plan fails with type errors or unexpected resource recreation. Always pin module versions.

**WHAT CHANGES AT SCALE:** A module registry (Terraform Cloud private registry or open-source alternatives) provides discoverability, versioning, and governance. Module owners publish changelogs. Callers upgrade on their cadence.

---

### 💻 Code Example

```hcl
# Module definition: modules/vpc/main.tf
variable "cidr_block" {
  type        = string
  description = "VPC CIDR block"
}

variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
}

variable "enable_flow_logs" {
  type    = bool
  default = true
}

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_flow_log" "this" {
  count           = var.enable_flow_logs ? 1 : 0
  vpc_id          = aws_vpc.this.id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow_log.arn
}

output "vpc_id" {
  value       = aws_vpc.this.id
  description = "VPC ID"
}

output "vpc_cidr" {
  value = aws_vpc.this.cidr_block
}
```

```hcl
# Root module: main.tf (calling the module)

# BAD: hardcoded resources with no reuse
resource "aws_vpc" "prod" {
  cidr_block = "10.0.0.0/16"
  # Missing: flow logs, DNS, tags standard
}

# GOOD: calling a versioned module
module "prod_vpc" {
  source  = "git::https://github.com/org/terraform-aws-vpc.git?ref=v2.1.0"
  # Or from Terraform Registry:
  # source  = "terraform-aws-modules/vpc/aws"
  # version = "~> 5.0"

  cidr_block       = "10.0.0.0/16"
  environment      = "prod"
  enable_flow_logs = true
}

module "dev_vpc" {
  source = "git::https://github.com/org/terraform-aws-vpc.git?ref=v2.1.0"

  cidr_block       = "10.1.0.0/16"
  environment      = "dev"
  enable_flow_logs = false  # cost saving in dev
}

# Reference module outputs
output "prod_vpc_id" {
  value = module.prod_vpc.vpc_id
}
```

---

### ⚖️ Comparison Table

| Source Type | Local | Registry | Git URL |
|---|---|---|---|
| **Versioning** | None (path) | Semantic version | Git ref/tag |
| **Discoverability** | Internal only | Public registry | Repo browsing |
| **CI download** | Not needed | Yes | Yes |
| **Private use** | ✅ | Private registry | Private repo |
| **Best for** | Active development | Stable shared modules | Internal modules |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Modules have their own state files" | Modules share the root module's state file. Resources are addressed with the module prefix. |
| "You can pass resources between modules" | You can only pass primitive values and complex types via variables/outputs - not resource references. |
| "All `.tf` files in a directory are one module" | Correct - Terraform treats all `.tf` files in a directory as one module automatically. |
| "Module upgrades are always safe" | Module version upgrades can trigger resource recreation. Always run `terraform plan` before upgrading. |
| "`for_each` on modules is not supported" | It is supported since Terraform 0.13. `for_each` on a `module` block creates multiple instances. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Module Source Not Pinned**
- **Symptom:** Plan worked yesterday; today shows unexpected resource recreation after init
- **Root Cause:** Module source was a branch (`?ref=main`), not a version tag; upstream changed
- **Diagnostic:**
```bash
cat .terraform/modules/modules.json | jq '.Modules[] | .Source'
```
- **Fix:** Pin module source to a specific Git tag or registry version.
- **Prevention:** Enforce version pins in CI; run `terraform init -upgrade=false` except during deliberate upgrades.

**Mode 2: Circular Module Dependencies**
- **Symptom:** `Error: Module cycle detected`
- **Root Cause:** Module A calls module B which calls module A
- **Diagnostic:** Map module call graph; identify cycle.
- **Fix:** Extract shared resources into a separate module that neither A nor B depends on.
- **Prevention:** Design module hierarchy as a tree, not a graph.

**Mode 3: Module Output Not Exported**
- **Symptom:** `Error: Unsupported attribute: module.vpc.subnet_ids`
- **Root Cause:** Module creates subnets but doesn't declare a `subnet_ids` output
- **Diagnostic:**
```bash
cat modules/vpc/outputs.tf
```
- **Fix:** Add the required output block to the module's `outputs.tf`.
- **Prevention:** Design module outputs as part of the interface spec before implementation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Resource, Terraform Overview, Terraform Provider

**Builds On This (learn these next):** Terraform Reusable Module Pattern, Terraform Remote State, Terragrunt

**Alternatives / Comparisons:** Terraform Reusable Module Pattern (usage patterns), CDK constructs, Pulumi ComponentResource

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Reusable HCL package with interface  │
│ PROBLEM       │ Copy-paste infrastructure with drift  │
│ KEY INSIGHT   │ Modules = functions for infra        │
│ USE WHEN      │ Repeated infra patterns, governance  │
│ AVOID WHEN    │ One-off unique resources             │
│ TRADE-OFF     │ Reuse + governance vs abstraction    │
│ ONE-LINER     │ module "vpc" { source = "..." }      │
│ NEXT EXPLORE  │ Reusable Module Pattern, Terragrunt  │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A module creates an IAM role with an attached policy. A caller needs to add an additional policy attachment without modifying the module. What are the design patterns available (outputs + root-level resources, module variable for additional policies, etc.) and what are the trade-offs of each?

2. **(Scale)** An organization publishes 40 internal Terraform modules. Engineers complain that modules are a "black box" and they can't understand what resources they're creating or what the security implications are. What module design, documentation, and governance practices would address this concern?

3. **(Design Trade-off)** A module creates 15 resources. A caller needs to customize the behavior of 2 of those resources in a way the module author didn't anticipate. The module author is unavailable. What are your options (fork, wrapper module, conditional variables, etc.) and what are the long-term maintenance implications of each?
