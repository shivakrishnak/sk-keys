---
layout: default
title: "Terraform"
parent: "CI/CD"
nav_order: 1017
permalink: /ci-cd/terraform/
number: "1017"
category: CI/CD
difficulty: ★★★
depends_on: Infrastructure as Code, Cloud, Git, CI/CD Pipeline
used_by: GitOps, Environment Promotion, Pulumi, Ansible
related: Pulumi, Ansible, AWS CloudFormation, OpenTofu
tags:
  - cicd
  - devops
  - cloud
  - deep-dive
  - infrastructure
---

# 1017 — Terraform

⚡ TL;DR — Terraform is the dominant declarative IaC tool that provisions any cloud resource using HCL configuration files, tracks infrastructure state, and plans changes before applying them.

| #1017 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Infrastructure as Code, Cloud, Git, CI/CD Pipeline | |
| **Used by:** | GitOps, Environment Promotion, Pulumi, Ansible | |
| **Related:** | Pulumi, Ansible, AWS CloudFormation, OpenTofu | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform team manages infrastructure across AWS, GCP, and GitHub for 15 microservices. They use a combination of AWS CloudFormation (AWS only), gcloud CLI scripts (GCP), Bash scripts (GitHub Actions config), and manual console clicks for anything too complex to script. Each tool has a different syntax, different state model, different error messages. A new hire joining the platform team must learn 4 different tools. A cross-cloud infrastructure change requires coordinating across all 4 tools simultaneously.

**THE BREAKING POINT:**
Multi-provider infrastructure management without a single tool becomes an operational taxonomy nightmare: 4 tools × 15 services × 3 environments = hundreds of configuration artefacts in incompatible formats. Onboarding is expensive. Cross-provider dependencies (AWS IAM role that grants access to GCP bucket) require manually orchestrated multi-tool workflows with zero automated dependency tracking.

**THE INVENTION MOMENT:**
This is exactly why Terraform was created: a single declarative language (HCL) and a multi-provider plugin architecture that lets you manage AWS, GCP, Azure, Kubernetes, GitHub, Cloudflare, and 1000+ other APIs using identical patterns, unified state management, and automated dependency resolution.

---

### 📘 Textbook Definition

**Terraform** (HashiCorp, open-source) is a declarative Infrastructure as Code tool that provisions and manages cloud resources across multiple providers using HashiCorp Configuration Language (HCL). Terraform operates through four phases: `init` (download providers), `plan` (compute desired-vs-actual diff), `apply` (execute changes), and `destroy` (remove resources). It maintains a **state file** (`terraform.tfstate`) that records the mapping between declared resources and their real-world identifiers. Terraform's **provider plugin architecture** enables management of any API-backed system through community or vendor-maintained providers. Terraform supports **modules** for reusable component encapsulation. The fork **OpenTofu** (Linux Foundation, 2023) is a fully compatible open-source alternative created after HashiCorp relicensed Terraform from MPL-2.0 to BSL-1.1.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write what infrastructure you want; Terraform figures out what to create, change, or delete to get there.

**One analogy:**
> Terraform is like a GPS navigator with a live traffic view of your infrastructure. You tell it the destination (desired infrastructure state). It shows you the route (the plan: what changes it will make). You approve, and it drives there — sensing the actual roads (AWS/GCP state), rerouting around obstacles (API errors, dependency ordering), and tracking your current position (state file) so it always knows where you are relative to where you want to be.

**One insight:**
The power of `terraform plan` is that it separates intent from execution — you see exactly what will change (create, update, destroy), including the precise attribute values, before anything is touched. In ClickOps or shell scripts, you can't preview a full diff before applying. The plan phase converts infrastructure changes from "hope it's right" to "verified before executing."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Cloud provider APIs accept create/read/update/delete operations but don't offer a "desired state" endpoint — the tool must compute deltas.
2. Resources have dependencies (EC2 instance needs a subnet, subnet needs a VPC) — changes must be applied in the correct order.
3. Infrastructure changes can take minutes (DB provisioning), not milliseconds — the tool must handle partial success and be safe to re-run.

**DERIVED DESIGN:**
Terraform's provider plugins wrap cloud provider APIs and define resource schemas — the set of input attributes and computed output attributes for each resource type. Plugin authors define the CRUD operations for each resource type, and the Terraform core engine handles state management, dependency resolution, and plan execution.

The state file is the critical data structure: a JSON document mapping each declared resource (e.g., `aws_instance.web`) to its provider-assigned ID (e.g., `i-0abc123`) and all current attributes. This enables Terraform to: (1) read back the current state of a resource by ID, (2) compute what attributes need to change, and (3) call the correct provider API with the delta.

**Dependency graph construction:** Terraform parses all `*.tf` files and builds a directed acyclic graph where edges represent references (`aws_instance.web.subnet_id = aws_subnet.public.id` creates an edge from instance to subnet). Apply respects topological order — dependencies before dependents.

**THE TRADE-OFFS:**
**Gain:** Unified multi-provider management; plan-before-apply safety; automatic dependency ordering; large provider ecosystem; extensive community modules.
**Cost:** State file is a single point of failure requiring careful management. HCL is a DSL with limited programming capability (loops are HCL-idiomatic but complex logic is awkward). Provider upgrades can require state migration. `terraform apply` is not transactional — partial applies leave infrastructure in a partially updated state.

---

### 🧪 Thought Experiment

**SETUP:**
A team needs to create an AWS RDS database inside a VPC with a security group. Three resources, two dependencies. No Terraform.

**WHAT HAPPENS WITHOUT TERRAFORM:**
Engineer creates VPC in AWS console. Creates subnet inside VPC (remembers to reference VPC ID). Creates security group inside VPC. Creates RDS: must remember to reference the subnet group and security group. Three weeks later, needs to create identical staging environment. Starts from scratch. Makes subtly different choices. Production and staging diverge.

**WHAT HAPPENS WITH TERRAFORM:**
```hcl
resource "aws_vpc" "main" { cidr_block = "10.0.0.0/16" }
resource "aws_subnet" "db" {
  vpc_id     = aws_vpc.main.id   # dependency declared
  cidr_block = "10.0.1.0/24"
}
resource "aws_db_instance" "main" {
  db_subnet_group_name = aws_db_subnet_group.main.name
  instance_class = "db.t3.medium"
}
```
`terraform plan` shows: create VPC → create subnet → create RDS. `terraform apply` executes in order. For staging: same files, different `environment` variable. `terraform workspace new staging` + `terraform apply` — identical infrastructure.

**THE INSIGHT:**
Terraform's dependency graph transforms infrastructure creation from a sequence of manual steps held in human memory to a declarative specification where the tool infers and executes the correct sequence automatically, every time.

---

### 🧠 Mental Model / Analogy

> Terraform is like a professional moving company with a detailed floor plan. You give them the floor plan of your destination (HCL config: where everything should go). They photograph your current home (plan phase: read current state). They show you a plan ("we'll move the sofa first, then the bookcase"). You approve it. They execute in the correct order — sofa out before bookcase so the path is clear. And they keep a receipt of exactly what moved where (state file: every item's final location).

- "Floor plan" → HCL resource declarations
- "Photograph of current home" → provider API read of actual state
- "Showing the plan" → `terraform plan` output
- "Executing in order" → dependency-ordered `terraform apply`
- "Receipt" → `terraform.tfstate`
- "Multiple identical moves" → reusable Terraform modules

Where this analogy breaks down: moving companies can always see the physical items. Terraform can only see what's in its state file — manual console changes are invisible to Terraform until `terraform refresh` or `terraform import` syncs the state.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Terraform is a tool where you describe in text files what cloud servers and databases you want, and it creates (or updates or deletes) them automatically. You describe the end state; Terraform figures out the steps to get there.

**Level 2 — How to use it (junior developer):**
Write `resource` blocks in `.tf` files. Run `terraform init` → `terraform plan` → `terraform apply`. Use `terraform fmt` to auto-format code. Use `terraform validate` to check syntax. Store state in S3 with DynamoDB locking. Use variables (`var.region`) and outputs (`output "bucket_arn"`) to parameterise and expose values. Never commit `*.tfstate` or `*.tfvars` containing secrets to git.

**Level 3 — How it works (mid-level engineer):**
Providers are Go plugins implementing the CRUD for each resource type. `terraform init` downloads providers from the Terraform Registry into `.terraform/`. The lock file (`.terraform.lock.hcl`) pins provider versions — commit this to git. `terraform plan`: provider reads current state via API → Terraform computes diff against `.tfstate` + desired config → renders human-readable plan. `terraform apply -auto-approve` skips interactive confirmation (use in CI only). The `data` block (data sources) reads existing resources without managing them: `data "aws_ami" "ubuntu"` reads the latest Ubuntu AMI ID without Terraform managing it.

**Level 4 — Why it was designed this way (senior/staff):**
Terraform's HCL design deliberately avoided a general-purpose language for two reasons: (1) Turing-complete languages create infrastructure code that requires running to understand — HCL's declarative structure means you can analyse the config statically; (2) infrastructure definitions benefit from immutability and explicit typing. The choice was revisited with Terraform CDK (CDKTF, 2020), which compiles TypeScript/Python/Java to HCL — a compromise acknowledging that complex infrastructure logic in HCL loops (`for_each`) becomes unmaintainable. The 2023 BSL relicensing prompted the OpenTofu fork — a signal that the community considered Terraform's openness a structural dependency, not just a preference. Pulumi's success demonstrates demand for general-purpose language IaC, though Terraform retains dominance due to provider ecosystem breadth and accumulated community knowledge.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  TERRAFORM EXECUTION INTERNALS              │
├─────────────────────────────────────────────┤
│                                             │
│  INIT:                                      │
│  → Parse .tf files for required_providers   │
│  → Download provider plugins to .terraform/ │
│  → Configure backend (S3/TF Cloud)          │
│  → .terraform.lock.hcl: pin versions        │
│                                             │
│  PLAN:                                      │
│  1. Parse all *.tf → build resource graph   │
│  2. Load state file from S3 backend         │
│  3. For each managed resource:              │
│     → Call provider.Read(resource_id)       │
│     → Compare actual vs desired attributes  │
│  4. Build ordered change set:               │
│     + create (new resource)                 │
│     ~ update (attribute changed)            │
│     - destroy (removed from .tf)            │
│  5. Render plan output                      │
│                                             │
│  APPLY:                                     │
│  1. Walk dependency graph (topological)     │
│  2. For each change:                        │
│     + create → provider.Create()            │
│     ~ update → provider.Update()            │
│     - destroy → provider.Delete()           │
│  3. After each success: update state file   │
│  4. Release state lock                      │
│                                             │
│  STATE FILE:                                │
│  {                                          │
│    "resources": [{                          │
│      "type": "aws_instance",                │
│      "name": "web",                         │
│      "instances": [{                        │
│        "attributes": {                      │
│          "id": "i-0abc123",                 │
│          "instance_type": "t3.medium"       │
│        }                                    │
│      }]                                     │
│    }]                                       │
│  }                                          │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Engineer adds new resource to main.tf
  → git branch infra/add-rds → PR
  → CI: terraform plan [← YOU ARE HERE]
     GitHub Actions: terraform plan -out=tfplan
     → Shows: +2 resources to add
     → Plan attached as PR comment
  → Team reviews plan, approves PR
  → Merge to main
  → CI: terraform apply -auto-approve (on main)
     → Resources created in order
     → State file updated in S3
     → Outputs: db_endpoint, db_port
  → Application config picks up outputs
```

**FAILURE PATH:**
```
terraform apply fails mid-execution
  (VPC created, subnet fails: CIDR conflict)
  → State file updated for VPC (created)
  → Error displayed with resource + reason
  → Partial state: VPC exists, subnet does not
  → Fix: correct CIDR in .tf file
  → Re-run terraform apply
  → Terraform reads state: VPC already exists (no-op)
  → Attempts subnet again with corrected CIDR
  → Recovers cleanly
```

**WHAT CHANGES AT SCALE:**
At 100+ modules and 10+ engineers, a central Terraform monorepo becomes a bottleneck (state lock contention, plan × destroy times of 20+ minutes). Teams split state into per-service workspaces: `prod/services/user-service/terraform.tfstate`, `prod/services/order-service/terraform.tfstate`. Cross-service references use `terraform_remote_state` data sources. CD platforms (Atlantis, Spacelift, Terraform Cloud) automate plan/apply workflows with PR-level automation, policy checks (Sentinel, OPA), and cost estimation (Infracost).

---

### 💻 Code Example

**Example 1 — Module definition and usage:**
```hcl
# modules/vpc/main.tf (reusable module)
variable "cidr_block" { type = string }
variable "name" { type = string }

resource "aws_vpc" "this" {
  cidr_block = var.cidr_block
  tags = { Name = var.name }
}

output "vpc_id" {
  value = aws_vpc.this.id
}
```
```hcl
# Root module: use the VPC module
module "prod_vpc" {
  source     = "./modules/vpc"  # local module
  cidr_block = "10.0.0.0/16"
  name       = "production-vpc"
}

# Reference module output
resource "aws_subnet" "main" {
  vpc_id     = module.prod_vpc.vpc_id  # module output
  cidr_block = "10.0.1.0/24"
}
```

**Example 2 — for_each to create multiple resources:**
```hcl
# Create S3 buckets for multiple environments
variable "environments" {
  default = ["dev", "staging", "prod"]
}

resource "aws_s3_bucket" "env_buckets" {
  for_each = toset(var.environments)
  bucket   = "myapp-${each.key}-data"
  # each.key = "dev" | "staging" | "prod"
}
```

**Example 3 — Remote state reference (cross-service):**
```hcl
# In order-service: reference user-service VPC
data "terraform_remote_state" "user_svc" {
  backend = "s3"
  config = {
    bucket = "my-terraform-state"
    key    = "prod/user-service/terraform.tfstate"
    region = "us-east-1"
  }
}

# Use output from user-service state
resource "aws_db_instance" "orders" {
  db_subnet_group_name = data.terraform_remote_state
    .user_svc.outputs.db_subnet_group_name
}
```

**Example 4 — Atlantis PR automation (atlantis.yaml):**
```yaml
# atlantis.yaml — Atlantis reads this for PR workflows
version: 3
projects:
  - name: prod-infra
    dir: terraform/prod
    workspace: prod
    autoplan:
      when_modified:
        - "**/*.tf"
      enabled: true
    apply_requirements:
      - approved    # requires 1 PR approval before apply
      - mergeable   # PR must be mergeable (no conflicts)
```

---

### ⚖️ Comparison Table

| vs | Terraform | Pulumi | CloudFormation | Ansible |
|---|---|---|---|---|
| Language | HCL (DSL) | TS/Python/Go/C# | JSON/YAML | YAML |
| Paradigm | Declarative | Declarative | Declarative | Imperative |
| State Mgmt | External file | External file | AWS-native | Stateless |
| Multi-cloud | Yes (1000+ providers) | Yes (using TF providers) | AWS only | Yes (modules) |
| Testing | Limited (terratest) | Full unit test support | cfn-lint | Molecule |
| Onboarding | Medium | Developers love it | High (verbose) | Low |

How to choose: **Terraform** is the industry default for IaC — choose it unless you have a specific reason not to. Choose **Pulumi** when your team prefers real programming languages and wants unit testing of infrastructure logic. Use **CloudFormation** only if you're locked into AWS and want native integration. Use **Ansible** for configuration management of existing servers, not for provisioning new cloud resources.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `terraform apply` is safe to run without reviewing the plan | `terraform plan` may show a destroy action on a production database. Always review the plan. Use `terraform plan -out=tfplan` and `terraform apply tfplan` to apply exactly the reviewed plan. |
| OpenTofu is just a fork for political reasons | OpenTofu is a fully compatible, actively maintained alternative. It's the correct choice for organisations that need OSI-approved licensing for compliance reasons (many enterprises require MPL or Apache, not BSL). |
| Terraform modules are like functions — reusable anywhere | Terraform modules are closer to classes with side effects. They create real resources when called. They cannot be called in loops without `for_each`, and they have their own state within the parent state file. |
| `terraform refresh` is safe to run frequently | `terraform refresh` calls every managed resource's Read API. In large environments with 1000+ resources, this makes thousands of API calls — potentially hitting provider rate limits and causing throttling. |

---

### 🚨 Failure Modes & Diagnosis

**1. Accidental `terraform destroy` in Production**

**Symptom:** All production resources deleted. Terraform confirmed before executing — but the flag was set to `--auto-approve` in a CI script that was run against the wrong workspace.

**Root Cause:** No workspace or environment guards in CI. `terraform destroy -auto-approve` executed against production workspace.

**Diagnostic:**
```bash
# Check current workspace
terraform workspace show

# Check what will be destroyed BEFORE applying
terraform plan -destroy

# Audit CI job that ran terraform destroy
gh api /repos/{owner}/{repo}/actions/runs/{run_id}/jobs
```

**Fix:**
```bash
# Always verify workspace before destructive operations
terraform workspace show
# Must equal expected workspace

# Never allow terraform destroy in CI except in ephemeral
# environments. Use variable to prevent accidental destroy:
```
```hcl
variable "prevent_destroy" {
  default = true
}
resource "aws_db_instance" "main" {
  lifecycle {
    prevent_destroy = true
    # Terraform will error if this resource is in a destroy plan
  }
}
```

**Prevention:** Add `lifecycle { prevent_destroy = true }` to all stateful production resources (databases, S3 buckets). Enforce workspace-aware CI jobs that reject `destroy` against `prod` workspace.

---

**2. State Lock Stuck After Interrupted Apply**

**Symptom:** `terraform plan` errors: "Error: Error acquiring the state lock. Lock Info: ID: abc-123-xyz". Running apply fails. No active Terraform process is running.

**Root Cause:** A previous `terraform apply` was interrupted (Ctrl+C, CI job killed, network timeout). The DynamoDB lock record was not released.

**Diagnostic:**
```bash
# View lock information
terraform force-unlock --help

# Check the DynamoDB lock table directly
aws dynamodb scan \
  --table-name terraform-state-lock \
  --filter-expression "attribute_exists(LockID)"
```

**Fix:**
```bash
# ONLY after confirming no active apply is running
terraform force-unlock <LOCK_ID>
# LOCK_ID from the error message

# Verify state is consistent after orphaned lock
terraform plan
# Review carefully — partial apply may have created resources
```

**Prevention:** Use Terraform Cloud or Atlantis for apply management — they handle lock release automatically on job failure. Set CI apply timeout with `terraform apply -lock-timeout=5m`.

---

**3. Provider Version Upgrade Breaks Existing State**

**Symptom:** After upgrading `hashicorp/aws` provider from `4.x` to `5.x`, `terraform plan` shows massive changes across all resources, including `aws_s3_bucket` resources being recreated.

**Root Cause:** Terraform provider major version upgrades often include schema changes. The `aws_s3_bucket` resource was split across multiple resources in v5 (`aws_s3_bucket_versioning`, `aws_s3_bucket_acl`). The state file contains old schema; the new provider expects a different format.

**Diagnostic:**
```bash
# Check provider changelog before upgrading
# https://github.com/hashicorp/terraform-provider-aws/
#   blob/main/CHANGELOG.md

# Test upgrade in non-prod first
terraform init -upgrade
terraform plan -detailed-exitcode
# Review all changes, especially unexpected "destroy"

# Check provider version in lock file
cat .terraform.lock.hcl | grep -A 3 "aws"
```

**Fix:**
```bash
# For aws v4 → v5: use migration guide
# Split aws_s3_bucket into separate resource types
# Use: hashicorp/aws → upgrade guide v4→v5

# Pin provider versions to avoid surprise upgrades:
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # allows 5.x, blocks 6.x
    }
  }
}
```

**Prevention:** Pin provider versions with `~> MAJOR.MINOR`. Test provider upgrades in dev environment first. Read provider CHANGELOG before upgrading major versions. Use CI plan-on-upgrade to review diff before merge.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Infrastructure as Code` — Terraform is the leading IaC tool; understanding IaC concepts (declarative, state, idempotency) is required
- `Cloud` — Terraform provisions cloud resources; understanding cloud primitives (VPC, EC2, S3, IAM) is required
- `Git` — Terraform code lives in Git; PR-based change management is the standard workflow

**Builds On This (learn these next):**
- `Pulumi` — alternative IaC using general-purpose languages instead of HCL; understanding Terraform makes Pulumi conceptually straightforward
- `GitOps` — extends IaC principles to continuous reconciliation; Terraform is often the IaC tool in GitOps (alongside ArgoCD for Kubernetes)
- `OpenTofu` — the OSI-licensed Terraform fork; drop-in compatible for teams needing non-BSL licensing

**Alternatives / Comparisons:**
- `Pulumi` — same declarative IaC model but using TypeScript/Python instead of HCL; better for complex logic and unit testing
- `Ansible` — imperative configuration management; good for existing servers, weaker for cloud resource provisioning
- `AWS CloudFormation` — AWS-native IaC; more verbose than Terraform, tighter AWS integration, no multi-cloud support

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multi-provider declarative IaC tool using │
│              │ HCL: plan then apply cloud resource changes│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Fragmented multi-tool infrastructure      │
│ SOLVES       │ management with no unified state tracking │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ terraform plan shows the exact diff before│
│              │ anything changes — review before applying │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Provisioning new cloud resources or       │
│              │ managing multi-provider infrastructure    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Configuration management on existing      │
│              │ servers — use Ansible/Chef instead        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Unified multi-cloud management vs state   │
│              │ file management and HCL limitations       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "GPS for infrastructure — shows the route │
│              │  before you drive, tracks where you are." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pulumi → Terragrunt → OpenTofu →          │
│              │ Atlantis → OPA/Sentinel policy enforcement│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `terraform apply` creates 15 resources successfully, then fails on the 16th (an IAM policy attachment) due to a missing permission. Terraform's state file records the 15 created resources. You fix the IAM permissions issue. You now have two options: run `terraform apply` again (which will only attempt the failed resource, since completed ones are already in state), or run `terraform destroy` and start fresh to ensure a clean state. Trace the exact state file contents and provider API calls made in each option, and explain when each approach is correct and why.

**Q2.** Your organisation uses Terraform to manage 3,000 cloud resources across 50 modules and 8 workspaces. A policy change requires adding the tag `cost-center: engineering` to every single AWS resource. Describe at least three different implementation strategies using Terraform's built-in features (default tags, module input variables, `merge()`, provider `default_tags`), and explain the precise trade-off between each in terms of code volume, blast radius on `terraform plan`, and risk of accidental resource recreation.

