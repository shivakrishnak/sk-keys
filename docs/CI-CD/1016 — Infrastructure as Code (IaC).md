---
layout: default
title: "Infrastructure as Code (IaC)"
parent: "CI/CD"
nav_order: 1016
permalink: /ci-cd/infrastructure-as-code/
number: "1016"
category: CI/CD
difficulty: ★★☆
depends_on: CI/CD Pipeline, Cloud, Deployment Pipeline, Git
used_by: Terraform, Pulumi, Ansible, GitOps, Environment Promotion
related: Terraform, Pulumi, Ansible, GitOps, Configuration Management
tags:
  - cicd
  - devops
  - cloud
  - intermediate
  - bestpractice
---

# 1016 — Infrastructure as Code (IaC)

⚡ TL;DR — Infrastructure as Code provisions and manages servers, networks, and cloud resources through versioned code files rather than manual clicks or scripts, making infrastructure reproducible and reviewable.

| #1016 | Category: CI/CD | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CI/CD Pipeline, Cloud, Deployment Pipeline, Git | |
| **Used by:** | Terraform, Pulumi, Ansible, GitOps, Environment Promotion | |
| **Related:** | Terraform, Pulumi, Ansible, GitOps, Configuration Management | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A startup grows from 2 to 20 engineers. The original infrastructure was created by one engineer clicking through the AWS console over a Saturday afternoon. That engineer left 8 months ago. Now nobody knows: exactly which VPC configuration was chosen, why security group rule 37 exists on port 8080, what the RDS instance was sized to (`db.t3.medium` or `db.t3.large`?), or how to recreate the entire setup if the account is compromised. Staging was set up by a different engineer who "did roughly the same thing." Staging and production have diverged silently over 18 months.

**THE BREAKING POINT:**
Manual infrastructure provisioning creates snowflake environments — each unique, none reproducible. A disaster recovery exercise reveals it would take 3 weeks and multiple tribal knowledge holders to recreate production from scratch. An AWS bill anomaly investigation requires 2 days of forensic log analysis because no one knows the complete inventory of running resources.

**THE INVENTION MOMENT:**
This is exactly why Infrastructure as Code exists: capture all infrastructure decisions in version-controlled code files — making infrastructure reproducible, auditable, reviewable, and deployable as reliably as application code.

---

### 📘 Textbook Definition

**Infrastructure as Code (IaC)** is the practice of managing and provisioning computing resources (servers, networks, databases, load balancers, DNS records, IAM policies) through machine-readable configuration or declarative definition files stored in version control, rather than through manual configuration or interactive CLI commands. IaC tools execute these definitions against cloud provider APIs to create, update, or delete resources. There are two primary paradigms: **declarative** (you describe the desired end state; the tool figures out how to achieve it — Terraform, Pulumi, AWS CloudFormation) and **imperative** (you describe the exact sequence of steps — Ansible, shell scripts, AWS CLI). IaC integrates with CI/CD pipelines to automate infrastructure deployments alongside application deployments, enabling environment parity, disaster recovery, and infrastructure change management through pull requests.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write code to describe your servers and networks so they can be created from scratch identically every time.

**One analogy:**
> Infrastructure as Code is like an IKEA instruction manual for your servers. With the manual (the code), anyone can assemble the same bookshelf (infrastructure) correctly, in the same sequence, with the same parts — even if the original assembler is on holiday. Without the manual, you're staring at a pile of parts hoping you remember where everything goes.

**One insight:**
The transformative shift is treating infrastructure change like software change: all modifications go through pull requests, get reviewed by peers, pass automated linting and tests, are documented in commit messages, and can be reverted with `git revert`. The security group rule added by the engineer who left 8 months ago is permanently in git history with their name on it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Infrastructure state is complex and interdependent — changes to one resource (VPC CIDR) can cascade to dozens of others (subnets, route tables, security groups).
2. Manual operations are not reproducible — the same human following the same ClickOps runbook will produce subtly different results each time.
3. Auditability requires a record — without a record of infrastructure changes, diagnosing failures and attributing problems is guesswork.

**DERIVED DESIGN:**
The declarative approach emerged as the dominant IaC model because it addresses the reproducibility invariant directly: you declare what you want (`resource "aws_instance" "web" { instance_type = "t3.medium" }`), and the tool computes the diff between desired state and actual state, then executes only the required changes. This idempotency property means running the same IaC definition twice produces the same result — applying it on already-correct infrastructure is a no-op.

State management is the critical design challenge. Terraform stores actual resource state in a **state file** (`terraform.tfstate`) — a JSON record of every managed resource and its current attributes. This state file is the ground truth for change computation. Without it, Terraform cannot know what already exists and would try to recreate everything. The state file must be stored remotely (S3 + DynamoDB, Terraform Cloud) and shared among all team members — making it both a coordination mechanism and a critical security artifact (it contains resource IDs and potentially sensitive attributes).

**THE TRADE-OFFS:**
**Gain:** Reproducible environments; infrastructure change management via PRs; disaster recovery in minutes not weeks; environment parity; complete audit trail.
**Cost:** Learning curve (HCL, Terraform state management); state file management complexity; IaC code that drifts from actual state when manual changes are made (configuration drift); long `terraform apply` times for large infrastructure.

---

### 🧪 Thought Experiment

**SETUP:**
A production database instance is accidentally deleted. The team needs to restore the complete RDS instance with the exact same configuration: instance class, parameter group, security groups, subnet group, multi-AZ setting, backup retention.

**WHAT HAPPENS WITHOUT IaC:**
Engineer opens AWS console. They check the backup (if it exists). They try to remember the instance class — was it `db.m5.large` or `db.m5.xlarge`? They check Slack history. They find a message from 6 months ago saying "we upgraded to xlarge" — but did that also happen in staging? Security groups for the new instance need to be manually assigned. After 4 hours of configuration archaeology, the new instance is probably correct. The team isn't sure.

**WHAT HAPPENS WITH IaC:**
Engineer checks the Terraform configuration in git. `aws_db_instance.main` has `instance_class = "db.m5.xlarge"`, all parameter groups, security groups, and subnet group explicitly declared. `terraform apply` recreates the instance with the exact configuration. Full restoration takes 25 minutes (Terraform execution time), not 4 hours of guesswork.

**THE INSIGHT:**
IaC's disaster recovery value alone justifies its adoption. The ability to recreate any environment from code eliminates the "snowflake infrastructure" problem and makes the team resilient to both accidents and personnel turnover.

---

### 🧠 Mental Model / Analogy

> Infrastructure as Code is like version-controlling your home's blueprints. A contractor can rebuild your home identically from blueprints — correct room dimensions, electrical layout, plumbing routes. Changes to the blueprints (add a bathroom) go through an architect's review (PR review), are documented with a reason (commit message), and the revised blueprint is the authoritative record (git history). ClickOps is like rebuilding from memory — each contractor makes slightly different decisions.

- "Blueprints" → Terraform/Pulumi configuration files
- "Contractor building from blueprints" → `terraform apply`
- "Architect's review" → PR review of IaC changes
- "Blueprint revision history" → git commit history
- "Rebuild from scratch" → disaster recovery via `terraform apply`
- "Two homes built from same blueprints" → staging/production parity

Where this analogy breaks down: blueprints are passive — they don't track whether the built house matches the blueprint after the builder makes changes. Terraform's state file tracks the live infrastructure state and detects drift from the declared code.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of clicking through website menus to create servers and databases, you write a file that describes what you want, and a tool creates it automatically. If you delete the file and run again, you get the exact same result. Other team members can see and review your infrastructure changes before they happen.

**Level 2 — How to use it (junior developer):**
Create a `main.tf` file with your Terraform resources. Run `terraform init` (downloads providers), `terraform plan` (shows what will change), `terraform apply` (makes the changes). Store the state file remotely: configure an S3 backend with DynamoDB for locking. Never modify infrastructure manually in the cloud console after IaC is set up — it creates drift. Use `terraform import` to bring existing resources under IaC management.

**Level 3 — How it works (mid-level engineer):**
Terraform's execution model: parse HCL → build dependency graph → call provider API to read current state → compute diff against state file and desired config → execute changes in dependency order (create VPC before subnets, subnets before instances). The state file records each managed resource's attributes after successful apply. Plan phase simulates changes without executing — showing `+` create, `~` update, `-` destroy. Critical: `terraform plan` against real infrastructure requires read permissions on all managed resources. In CI, use `terraform plan` on PRs and `terraform apply` only on merge to main.

**Level 4 — Why it was designed this way (senior/staff):**
The declarative IaC model was pioneered by AWS CloudFormation (2011) and popularised by Terraform (2014). Terraform's multi-provider design (one tool for AWS, GCP, Azure, Kubernetes, DNS, GitHub) became its killer feature — infrastructure teams could use a single language across heterogeneous environments. The HCL (HashiCorp Configuration Language) was designed as a human-readable superset of JSON, deliberately simpler than general-purpose languages. The emerging trend is towards general-purpose language IaC (Pulumi, AWS CDK) — using TypeScript/Python/Go for infrastructure, enabling type safety, test frameworks, and real abstraction patterns. This reflects the maturation of IaC from "better ClickOps" to "software engineering applied to infrastructure."

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  TERRAFORM EXECUTION MODEL                  │
├─────────────────────────────────────────────┤
│                                             │
│  IaC Code (main.tf, variables.tf)           │
│         ↓                                  │
│  INIT: download provider plugins            │
│  (aws, google, kubernetes providers)        │
│         ↓                                  │
│  PLAN:                                      │
│  1. Read state file (S3/TF Cloud)           │
│  2. Call provider API: read current state   │
│  3. Compare: desired vs actual              │
│  4. Compute: dependency-ordered change set  │
│  Output:                                    │
│  + aws_vpc.main (will create)               │
│  ~ aws_instance.web (will update: t3→t3.med)│
│  - aws_security_group.old (will destroy)    │
│         ↓ (human/CI approves plan)          │
│  APPLY:                                     │
│  Execute changes in dependency order:       │
│  1. Create VPC (others depend on it)        │
│  2. Create subnets (depends on VPC)         │
│  3. Create security groups                  │
│  4. Create EC2 instances                    │
│  5. Update state file                       │
│                                             │
│  STATE FILE (terraform.tfstate):            │
│  JSON: every managed resource +             │
│  its current attributes + provider ID       │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Engineer needs new S3 bucket + CloudFront distribution
  → Creates/modifies .tf files in Git branch
  → PR opened
  → CI: terraform plan [← YOU ARE HERE]
     Shows: + aws_s3_bucket.assets (create)
            + aws_cloudfront_distribution.cdn (create)
  → Peer reviews plan output in PR
  → PR merged to main
  → CI: terraform apply
  → Resources created in AWS
  → Outputs (bucket name, CDN URL) stored
  → Application config updated with new values
```

**FAILURE PATH:**
```
terraform apply fails mid-execution
  (VPC created, subnet creation fails)
  → Partial state in state file
  → terraform.tfstate updated for created resources
  → Re-running apply: resumes from partial state
  → Resolves root cause (quota limit, policy issue)
  → apply again: only creates missing resources
  (Partial apply scenario is recoverable via re-apply)
```

**WHAT CHANGES AT SCALE:**
At 100+ engineers managing IaC, a monolithic `main.tf` becomes unmanageable. Teams adopt Terraform modules (reusable components: `terraform-aws-eks`, `terraform-aws-vpc`) and workspace separation. Large organisations use Atlantis (Terraform automation server) or Terraform Cloud to manage plan/apply workflows at scale — auto-generating plan comments on PRs, serialising applies to prevent concurrent state modifications. State locking (DynamoDB) prevents two engineers from simultaneously applying against the same infrastructure.

---

### 💻 Code Example

**Example 1 — Basic Terraform AWS resources:**
```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Remote state: prevents state file in local git
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name        = "main-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# EC2 instance referencing VPC
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public.id
  # Reference: Terraform builds dependency graph automatically
  # aws_subnet must exist before aws_instance
}
```

**Example 2 — Terraform in CI (GitHub Actions):**
```yaml
# .github/workflows/terraform.yml
name: Terraform
on:
  pull_request:
  push:
    branches: [main]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan (on PRs)
        if: github.event_name == 'pull_request'
        run: terraform plan -out=tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Terraform Apply (on main merge)
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**Example 3 — Variable and output patterns:**
```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment (dev/staging/prod)"
  type        = string
  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )
    error_message = "Must be dev, staging, or prod."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

# outputs.tf
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "web_public_ip" {
  description = "Public IP of the web server"
  value       = aws_instance.web.public_ip
}
```

---

### ⚖️ Comparison Table

| Tool | Language | Paradigm | Multi-Cloud | State Mgmt | Best For |
|---|---|---|---|---|---|
| **Terraform** | HCL | Declarative | Yes (1000+ providers) | State file | Multi-cloud, large orgs |
| Pulumi | TS/Python/Go/C# | Declarative | Yes | State file | Developers, testing, abstraction |
| Ansible | YAML | Imperative | Yes | Stateless | Config mgmt, existing servers |
| AWS CDK | TS/Python/Java | Declarative | AWS only | CloudFormation | AWS-focused teams |
| CloudFormation | JSON/YAML | Declarative | AWS only | Native AWS | AWS-locked, no new tooling |
| Pulumi ESC | TS/Python/Go | Declarative | Yes | State file | Strong typing, test frameworks |

How to choose: Use **Terraform** as the default for its maturity, community (Terraform Registry), and broad provider support. Use **Pulumi** when your team wants to use real programming languages (TypeScript/Python) for infrastructure logic, enabling loops, conditions, and unit tests. Use **Ansible** for configuration management of existing servers and for tasks that are inherently procedural (run this command on these hosts).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| IaC means you can never touch the console | You can make manual changes, but they create "drift" — Terraform's state will conflict with actual state on next `plan`. Use `terraform import` for intentional manual resources; treat console-only changes as a code smell. |
| `terraform destroy` is safe to run in production | `terraform destroy` deletes ALL managed resources permanently, including databases and load balancers. It is almost never the right command in production. Use targeted `terraform destroy -target=...` if needed. |
| IaC eliminates all infrastructure bugs | IaC eliminates the class of bugs from manual provisioning. It introduces a new class: HCL logic bugs, state drift, and race conditions from concurrent applies. |
| The state file is just a cache | The state file is the source of truth for Terraform's understanding of infrastructure. If it's lost or corrupted, Terraform loses track of all managed resources. It must be treated as a critical, backed-up, access-controlled file. |

---

### 🚨 Failure Modes & Diagnosis

**1. Terraform State Drift — Manual Changes Break Apply**

**Symptom:** `terraform plan` shows resources being destroyed that should exist. An EC2 instance was manually resized in the console; Terraform wants to restore the originally declared size.

**Root Cause:** Manual console change created drift between actual state and IaC code. Terraform's state file records the original size; real infrastructure has a different size; Terraform sees a discrepancy and will "fix" it by applying the declared value.

**Diagnostic:**
```bash
# Show drift between state and actual infra
terraform plan -detailed-exitcode
# Exit code 2 = plan has changes = drift detected

# See exact drift per resource
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan | \
  jq '.resource_changes[] |
  select(.change.actions[] | contains("update")) |
  {address, before: .change.before, after: .change.after}'
```

**Fix:**
```bash
# Option A: update .tf file to match actual state (accept drift)
# Change instance_type to match actual

# Option B: refresh state from reality
terraform refresh
# Updates state file to reflect actual infrastructure
# Does NOT change .tf files

# Option C: import the modified resource
terraform import aws_instance.web i-1234567890abcdef0
```

**Prevention:** Enforce "no console changes" policy for IaC-managed resources. Use AWS Config Rules or GCP Organization Policies to alert on manual changes to IaC-managed resources. All changes go through `terraform apply`.

---

**2. Concurrent Apply Corruption**

**Symptom:** Two engineers run `terraform apply` simultaneously. One apply succeeds; the other errors with "Error acquiring state lock" — or in the worst case (no locking), state file corruption.

**Root Cause:** No state locking configured. State file stored in S3 without DynamoDB locking table.

**Diagnostic:**
```bash
# Check if state is currently locked
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "my-bucket/prod/terraform.tfstate"}}'
# Non-empty = locked by an active apply
```

**Fix:**
```hcl
# Configure S3 backend with DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock" # enables locking
    encrypt        = true
  }
}
```

**Prevention:** Always configure DynamoDB locking from day 1. In CI, serialise Terraform apply jobs so only one applies at a time per environment. Use Atlantis or Terraform Cloud to manage apply serialisation automatically.

---

**3. Sensitive Values in State File**

**Symptom:** Security audit finds RDS master password in plaintext inside `terraform.tfstate` committed to git.

**Root Cause:** Terraform state files contain the full attributes of every managed resource — including `password` fields of database resources. If the state file is committed to git or stored in an unencrypted S3 bucket, credentials are exposed.

**Diagnostic:**
```bash
# Check for sensitive values in state
terraform show -json | grep -i -E "(password|secret|key)"

# Check S3 bucket encryption
aws s3api get-bucket-encryption \
  --bucket my-terraform-state
# If error: no encryption configured
```

**Fix:**
- Add `*.tfstate` to `.gitignore` immediately
- Enable S3 server-side encryption on state bucket
- Use `sensitive = true` on variable/output declarations to redact from `plan` output
- Use AWS Secrets Manager for RDS passwords: `manage_master_user_password = true` in `aws_db_instance`
- Rotate any credentials that were in the exposed state file

**Prevention:** Never store state in git. Configure S3 encryption and IAM policies on state bucket from initial setup. Use `sensitive = true` for all secrets in Terraform code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Git` — IaC is code, and its power comes from being in version control; understanding branching and PR workflows is required
- `Cloud` — IaC manages cloud resources; understanding the resource concepts (VPC, EC2, S3) is required
- `CI/CD Pipeline` — IaC changes flow through CI pipelines; understanding pipeline structure is required for automating IaC safely

**Builds On This (learn these next):**
- `Terraform` — the dominant declarative IaC tool; deep exploration of HCL, providers, modules, and state management
- `Pulumi` — general-purpose language IaC as an evolution of Terraform
- `Ansible` — imperative configuration management complementing declarative IaC
- `GitOps` — applies IaC principles to application deployments; Flux and ArgoCD extend the IaC model to Kubernetes workloads

**Alternatives / Comparisons:**
- `ClickOps` — manual console provisioning; the opposite of IaC, discouraged for anything beyond prototyping
- `Configuration Management (Ansible, Chef)` — IaC for servers that already exist (provisioning config on running machines) vs IaC for provisioning new resources from scratch
- `Pulumi` — IaC using general-purpose languages (Python, TypeScript) instead of domain-specific HCL

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Managing servers and cloud resources      │
│              │ through versioned code, not console clicks│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Snowflake infrastructure: non-reproducible│
│ SOLVES       │ unpredictable, unauditable manual configs │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Infrastructure change = code change:      │
│              │ PR → review → apply → git history         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any cloud infrastructure beyond a single  │
│              │ one-time prototype experiment             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never avoid — but beware state file       │
│              │ management complexity in large teams      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reproducibility and auditability vs       │
│              │ state management overhead and HCL learning│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "IKEA manual for servers — anyone can     │
│              │  rebuild production from the instructions."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Terraform → Pulumi → GitOps →             │
│              │ Ansible → Policy as Code (OPA)            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team adopts Terraform for a new production environment. Six months in, engineers discover that a DBA manually resized 3 RDS instances in the console to handle a sudden load spike. These manual changes were never reflected in Terraform code. Now `terraform plan` shows Terraform wants to resize the instances back to their original sizes. How do you safely reconcile this drift — preserving the DBA's changes — and what process do you implement to prevent this class of problem going forward?

**Q2.** You are designing the IaC strategy for an organisation that has 5 teams, each owning 3–5 cloud environments (dev, staging, production). Each team wants independence to manage their infrastructure, but the security team requires central governance over IAM policies, VPC configurations, and network egress rules. How do you design the Terraform module and state file structure to give teams autonomy while enforcing security guardrails centrally — without creating a single-team bottleneck for all infrastructure changes?

