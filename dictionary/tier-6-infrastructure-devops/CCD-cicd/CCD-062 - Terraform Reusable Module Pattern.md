---
layout: default
title: "Terraform Reusable Module Pattern"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /ci-cd/terraform-reusable-module-pattern/
id: CCD-062
category: CI/CD
difficulty: ★★★
depends_on: Terraform Module, Terraform Overview
used_by: CI-CD
related: Terraform Module, Terraform Registry, DRY Principle
tags:
  - cicd
  - devops
  - advanced
  - pattern
  - bestpractice
---

# CCD-062 - Terraform Reusable Module Pattern

⚡ **TL;DR -** The reusable module pattern structures Terraform modules as versioned, opinionated libraries with stable interfaces, enabling DRY infrastructure across teams.

| Field | Value |
|---|---|
| **Depends on** | Terraform Module, Terraform Overview |
| **Used by** | CI-CD |
| **Related** | Terraform Module, Terraform Registry, DRY Principle |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Every engineer writes their own version of an S3 bucket, VPC, or EKS cluster. Configurations share no common structure. Security requirements are applied inconsistently. Reviewing 20 different VPC implementations for the same compliance requirement is impossible.

**THE BREAKING POINT:** A compliance audit finds that 8 of 23 S3 buckets across the organization don't have versioning or encryption enabled. The configurations are all slightly different. There's no single place to fix this.

**THE INVENTION MOMENT:** The platform team publishes `terraform-aws-secure-s3`. It enforces encryption, versioning, and access logging. All bucket callers use it with a two-line `module` block. The next compliance check passes automatically.

---

### 📘 Textbook Definition

The **Terraform Reusable Module Pattern** is an architectural approach where Terraform modules are designed as independent, versioned libraries with a stable public interface (defined by `variables.tf` and `outputs.tf`), opinionated defaults that enforce organizational standards, and independent testing and release pipelines. Modules are published to a registry (public or private) and consumed by caller configurations via version-pinned `module` blocks.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Treat Terraform modules like software packages: versioned, tested, published, and consumed via a registry.

> Reusable modules are like npm packages for infrastructure: the platform team publishes `@company/aws-vpc@2.1.0`; every team installs it rather than reinventing the wheel. Security patches release as version `2.1.1`, and teams upgrade on their schedule.

**One insight:** The key word is *reusable*, not just *modular*. A reusable module has: a stable interface contract, opinionated security defaults callers can't override, semantic versioning, and a test suite that runs on every PR.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Module interface (variables + outputs) is a public API - changes are breaking or non-breaking.
2. Required variables should be minimal; optional variables should have safe defaults.
3. Security and compliance requirements are non-overridable internal implementation details.
4. Module versions are immutable; `v1.0.0` always means the same thing.

**DERIVED DESIGN:** The module repository has its own CI pipeline: `terraform fmt` + `terraform validate` + Terratest integration tests. It publishes to a private or public Terraform Registry. Callers pin to minor versions (`~> 2.1`) to receive patches automatically.

**THE TRADE-OFFS:**
**Gain:** Organizational standards enforced at the infrastructure layer; security patches applied centrally; reduced cognitive load for callers.
**Cost:** Module abstraction can hide complexity; over-engineered modules become harder to customize than writing from scratch; governance overhead.

---

### 🧪 Thought Experiment

**SETUP:** You're a platform engineer. You publish `terraform-aws-rds v1.0.0` with default encryption but no automated backups.

**WHAT HAPPENS WITHOUT VERSIONING:** You add automated backups to the module. Callers running `terraform init` get the new version automatically. Their next `terraform plan` shows a backup window change on all production databases. Unexpected changes in production - the worst kind.

**WHAT HAPPENS WITH VERSIONING:** You publish `v1.1.0` with backups as an optional, default-off feature. You document the changelog. Callers upgrade from `~> 1.0` to `~> 1.1` deliberately, review the plan, and apply. No surprises.

**THE INSIGHT:** Module versioning is not a luxury - it's the mechanism that makes it safe to evolve a module that is used by many teams without causing incidents.

---

### 🧠 Mental Model / Analogy

> A reusable Terraform module is like a standardized building code: the building code (module) specifies the minimum requirements (encryption, logging). Architects (engineers) can choose floor layouts (resource-specific variables) but cannot override fire safety rules (mandatory security resources).

- Module repository → building code authority
- `variables.tf` → allowed design choices
- Mandatory internal resources → non-overridable building codes
- Module version → code revision year
- Caller configuration → specific building design

Where this analogy breaks down: unlike a building code, a Terraform module doesn't just set constraints - it actively creates the resources that enforce the standards. Non-compliance is impossible by construction.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** The reusable module pattern is about writing Terraform modules that work like good software libraries: simple to use, hard to misuse, and easy to upgrade.

**Level 2 - How to use it (junior developer):** Structure each module with `variables.tf` (inputs), `outputs.tf` (outputs), `main.tf` (resources), `versions.tf` (provider requirements), and `README.md` (documentation). Pin versions with `~> X.Y`. Use opinionated defaults so callers don't need to know every security option.

**Level 3 - How it works (mid-level engineer):** The module uses `validation` blocks on variables to enforce constraints at plan time. Security-critical resources (encryption, logging) are created unconditionally inside the module - callers cannot disable them via variables. The module's test suite uses Terratest to deploy real AWS resources in an integration test account and verify they meet requirements.

**Level 4 - Why it was designed this way (senior/staff):** The reusable module pattern applies the same principles as library design to infrastructure. The "pit of success" design - where the easy thing is also the secure thing - means engineers get compliance for free. Versioning decouples the platform team's delivery cadence from callers'. Treating the module as a product (with users, changelogs, breaking change policies) is the key organizational shift.

---

### ⚙️ How It Works (Mechanism)

**Module repository structure:**
```
terraform-aws-secure-s3/
├── main.tf          # resource definitions
├── variables.tf     # input interface
├── outputs.tf       # output interface
├── versions.tf      # terraform + provider requirements
├── README.md        # auto-generated from variables/outputs
├── examples/
│   └── complete/    # working example for testing
└── test/
    └── s3_test.go   # Terratest integration tests
```

**Variable design principles:**
- Required: only what is inherently unique per instance (e.g. bucket name)
- Optional with defaults: environment, tags, retention periods
- No variable for: encryption (always on), access logging (always on), public access block (always blocked)

---

### 🔄 The Complete Picture - End-to-End Flow

**MODULE DEVELOPMENT LIFECYCLE:**
```
  Platform team writes module
           │
  PR: terraform fmt + validate
      + Terratest runs in AWS test account
           │
  Merge → tag v1.0.0            ← YOU ARE HERE
           │
  Publish to Terraform Registry
  (public or private)
           │
  Teams consume: source = "org/module"
                 version = "~> 1.0"
           │
  terraform init downloads module
           │
  terraform plan: module resources
  in plan output with module. prefix
           │
  terraform apply creates resources
  to standard spec
```

**FAILURE PATH:** Module has a breaking variable change in a minor version. Callers' plans fail. They're blocked from deploying. Fix: follow semantic versioning strictly - breaking changes require a major version bump.

**WHAT CHANGES AT SCALE:** Private Terraform Registry (Terraform Cloud or open-source alternatives like Spacelift). Automated version bump PRs to callers via tooling. Module deprecation process. CODEOWNERS for module PRs.

---

### 💻 Code Example

```hcl
# --- modules/secure-s3/variables.tf ---
variable "bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name"
  validation {
    condition     = length(var.bucket_name) >= 3
    error_message = "Bucket name must be at least 3 characters."
  }
}

variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev","staging","prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "retention_days" {
  type        = number
  default     = 90
  description = "Object lifecycle expiry in days"
}

# --- modules/secure-s3/main.tf ---
# Encryption: NOT a variable - always enforced
resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# Public access: NOT a variable - always blocked
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration { status = "Enabled" }
}

# --- modules/secure-s3/outputs.tf ---
output "bucket_id"  { value = aws_s3_bucket.this.id }
output "bucket_arn" { value = aws_s3_bucket.this.arn }

# --- modules/secure-s3/versions.tf ---
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}
```

```hcl
# Caller configuration
module "app_data" {
  source  = "app.terraform.io/myorg/secure-s3/aws"
  version = "~> 1.2"  # pin to minor; get patches automatically

  bucket_name    = "myapp-prod-data"
  environment    = "prod"
  retention_days = 365
}
```

---

### ⚖️ Comparison Table

| Pattern | Reusable Module | Inline Resources | Copied HCL |
|---|---|---|---|
| **DRY** | ✅ Maximum | ❌ Per-use | ❌ None |
| **Security enforcement** | ✅ Non-overridable | ❌ Per-engineer | ❌ Per-engineer |
| **Versioning** | ✅ Semver | N/A | Manual |
| **Testing** | ✅ Terratest | ❌ None | ❌ None |
| **Discoverability** | ✅ Registry | ❌ None | ❌ None |
| **Flexibility** | Medium (interface only) | High | High |
| **Overhead** | High setup, low use | Low | Low setup, high maint. |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Any Terraform module is a reusable module" | A reusable module follows a contract: versioned, tested, with a stable interface. A local module in the same repo is not the same thing. |
| "More variables = better module" | More variables = more cognitive load and more combinations to test. Fewer, well-chosen variables with safe defaults is better design. |
| "Module outputs should expose everything" | Expose only what callers need. Internal resource IDs they don't need shouldn't pollute the output interface. |
| "The module controls all resources it creates" | Callers can attach additional resources to module outputs (e.g. extra IAM policy on a module-created role). |
| "Breaking changes require a full rewrite" | Semver major bump with migration guide. Use deprecated outputs/variables before removal. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Module Variable Breaks Existing Callers**
- **Symptom:** After module upgrade, callers get `Error: Missing required argument: <new_var>`
- **Root Cause:** New required variable added in a minor version bump (should have been major)
- **Diagnostic:** `terraform plan` output shows missing argument
- **Fix - BAD:** Add default to the required variable retroactively (masks intent).
- **Fix - GOOD:** Publish patch release (`v1.2.1`) reverting to optional with default; document upgrade path.
- **Prevention:** Use `CHANGELOG.md`; breaking changes must be major version bumps.

**Mode 2: Module Test Coverage Gap**
- **Symptom:** Module change in encryption config passes Terratest but breaks prod due to KMS key policy
- **Root Cause:** Tests create resources but don't verify IAM/KMS access patterns
- **Diagnostic:** Review Terratest test cases for missing assertions.
- **Fix:** Add explicit test assertions for key access patterns.
- **Prevention:** Test both happy path and negative cases; include cross-account access tests.

**Mode 3: Module Abstraction Leaks**
- **Symptom:** Engineers bypass the module and add raw `aws_s3_bucket` resources because the module doesn't support their use case
- **Root Cause:** Module interface is too restrictive; governance is implemented as a lock rather than a contract
- **Diagnostic:** Search codebase for raw resource types that the module is supposed to replace.
- **Fix:** Add the needed escape hatch as a module variable; maintain the security invariants internally.
- **Prevention:** Treat module engineers as product teams; gather caller requirements regularly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Module, Terraform Overview, DRY Principle

**Builds On This (learn these next):** Terragrunt, CI-CD, Terraform Registry

**Alternatives / Comparisons:** Terraform Module (concept), CDK Constructs library, Pulumi ComponentResource pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Versioned, tested infra library      │
│ PROBLEM       │ Copy-paste infra with security drift │
│ KEY INSIGHT   │ Module = product; version = contract │
│ USE WHEN      │ Shared org patterns with standards   │
│ AVOID WHEN    │ One-off unique resources             │
│ TRADE-OFF     │ Governance vs flexibility            │
│ ONE-LINER     │ version = "~> 1.0" pins safely       │
│ NEXT EXPLORE  │ Terragrunt, Terraform Testing        │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A reusable module creates an S3 bucket and enforces encryption. An engineering team needs a bucket with server-side encryption using a customer-provided key (SSE-C) rather than KMS. The module doesn't support this. What are the options for the team, and what process should exist so the module evolves to meet legitimate use cases?

2. **(Scale)** Your organization has 50 modules, each used by an average of 8 teams. A critical security patch must be applied to 12 of those 50 modules within 24 hours. Callers are spread across 200 Terraform configurations. How would you design a system to track which configurations are running which module versions and automate upgrade PRs?

3. **(Design Trade-off)** Module abstraction hides implementation details from callers. This is a feature (simplicity, governance) but also a risk (callers can't audit what's being created). How do you design the transparency-vs-abstraction trade-off in a module, and what documentation and metadata practices help callers make informed decisions?
