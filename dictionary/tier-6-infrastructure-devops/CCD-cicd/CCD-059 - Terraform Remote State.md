---
layout: default
title: "Terraform Remote State"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 59
permalink: /ci-cd/terraform-remote-state/
id: CCD-059
category: CI/CD
difficulty: ★★★
depends_on: Terraform State Backend, Terraform State
used_by: Terraform Module
related: Terraform State Backend, Terraform Module, Cross-Stack References
tags:
  - cicd
  - devops
  - advanced
---

# CCD-059 - Terraform Remote State

⚡ **TL;DR -** Terraform remote state lets one configuration read output values from another configuration's state file without coupling their code.

| Field | Value |
|---|---|
| **Depends on** | Terraform State Backend, Terraform State |
| **Used by** | Terraform Module |
| **Related** | Terraform State Backend, Terraform Module, Cross-Stack References |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A networking team manages VPCs. A compute team manages EC2 instances that must go in those VPCs. Either: (1) the compute team hardcodes VPC IDs, breaking when IDs change, or (2) both teams live in one giant Terraform configuration, creating a blast radius where a compute mistake can destroy networking.

**THE BREAKING POINT:** Hardcoded IDs in a 50-service organization means 50 files to update every time a VPC is recreated. One missed update causes a deployment failure or resources placed in the wrong network.

**THE INVENTION MOMENT:** `terraform_remote_state` data source reads another configuration's state outputs directly. The networking team exports `vpc_id`; the compute team reads it as a data source. No hardcoding. No coupling.

---

### 📘 Textbook Definition

**Terraform remote state** is a data source (`data "terraform_remote_state"`) that reads the output values from a separate Terraform configuration's state file stored in a remote backend. It enables cross-configuration references, allowing independent Terraform roots to share infrastructure information without merging into a single monolithic configuration or hardcoding values.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Remote state lets you read another team's Terraform outputs like a read-only API call.

> Remote state is like a bulletin board: the networking team posts the VPC ID on the board (state outputs); the compute team reads it from the board without needing to know how the VPC was built or calling the networking team directly.

**One insight:** Remote state creates a **read dependency**, not a code dependency. If the networking team changes their VPC, the compute team's next plan will automatically read the new VPC ID from state - no manual coordination needed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Only `output` values are readable via remote state - all other state details are private.
2. The reading configuration has no authority over the remote state it reads.
3. Remote state access requires read permission on the backend (S3 IAM policy).
4. Remote state is read at plan time, not apply time.

**DERIVED DESIGN:** The networking configuration declares outputs for any values consumer configurations need. Consumers declare `data "terraform_remote_state"` pointing to the backend location. The data source exposes `data.<name>.outputs.<output_name>`.

**THE TRADE-OFFS:**
**Gain:** Loose coupling between configurations; automatic propagation of changes.
**Cost:** Creates a runtime dependency - if the remote state is unavailable or the output doesn't exist, plans fail; tight implicit contracts between teams.

---

### 🧪 Thought Experiment

**SETUP:** You have separate Terraform configs for networking (VPC, subnets) and application (ECS tasks, ALBs).

**WHAT HAPPENS WITHOUT REMOTE STATE:** The application team either: hardcodes `subnet-0abc12345` (breaks when recreated), or checks out and reads networking Terraform output files manually (fragile), or both teams merge into one config (blast radius nightmare).

**WHAT HAPPENS WITH REMOTE STATE:** Networking config outputs `subnet_ids`. Application config reads `data.terraform_remote_state.network.outputs.subnet_ids`. When networking team recreates subnets (new IDs), application team's next plan automatically picks up the new IDs from state. No manual update required.

**THE INSIGHT:** Remote state creates a typed, version-controlled contract between teams. The networking team's `output` blocks are a public API that consumers depend on.

---

### 🧠 Mental Model / Analogy

> Remote state is like a shared configuration register in a microservice architecture: Service A publishes its endpoint URL to a service registry (state outputs); Service B reads from the registry at startup (plan time). Neither service knows the other's internal implementation.

- State outputs → service registry entries
- `terraform_remote_state` data source → registry read call
- Backend location → registry address
- Output name → registry key

Where this analogy breaks down: unlike a live service registry, remote state is a point-in-time snapshot. If the networking team applies a change, consumers don't auto-update - they read the new value on their *next* plan.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Remote state lets one Terraform project read the outputs of another Terraform project, so teams don't have to hardcode IDs or merge everything into one big project.

**Level 2 - How to use it (junior developer):** In the "producer" config, add `output` blocks for any values you want to share. In the "consumer" config, add a `data "terraform_remote_state"` block pointing to the producer's backend location. Access values via `data.<name>.outputs.<output_name>`.

**Level 3 - How it works (mid-level engineer):** During plan, Terraform reads the remote state file from the backend, parses the `outputs` section, and makes those values available as a map. No API calls are made to the actual cloud - it's purely a state file read. The data source is treated as a dependency in the DAG.

**Level 4 - Why it was designed this way (senior/staff):** Remote state implements the "outputs as API" pattern without requiring a separate service or coordination mechanism. The contract is enforced at plan time: if the expected output doesn't exist, the plan fails clearly rather than silently using stale data. Sensitive output values are marked `sensitive = true` to prevent them from appearing in plan output.

---

### ⚙️ How It Works (Mechanism)

During `terraform plan`:
1. Terraform encounters `data "terraform_remote_state" "network" { ... }`
2. Connects to the backend specified (S3, Terraform Cloud, etc.)
3. Downloads the state file JSON
4. Parses the `outputs` key
5. Exposes `data.terraform_remote_state.network.outputs.*`

The consumer configuration never sees non-output state data (resource IDs, attributes). Only `output` values are surfaced.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  PRODUCER CONFIG (networking)
  ┌─────────────────────────┐
  │ resource "aws_vpc" ...  │
  │ output "vpc_id" {       │
  │   value = aws_vpc.id    │
  │ }                       │
  └────────────┬────────────┘
               │ terraform apply
               ▼
  S3: networking/terraform.tfstate
               │
  CONSUMER CONFIG (application)    ← YOU ARE HERE
  ┌────────────────────────────────┐
  │ data "terraform_remote_state"  │
  │   "network" {                  │
  │   backend = "s3"               │
  │   config = { key = "net/..." } │
  │ }                              │
  │ resource "aws_ecs_service" {   │
  │   subnets = data.              │
  │     terraform_remote_state.    │
  │     network.outputs.subnet_ids │
  │ }                              │
  └────────────────────────────────┘
```

**FAILURE PATH:** Producer output renamed → consumer plan fails: `Unsupported attribute: outputs.old_name`. Teams must coordinate output name changes as breaking API changes.

**WHAT CHANGES AT SCALE:** With many consumers, the producer's outputs become a stable API surface. Use semantic versioning conventions for output names. Consider Terraform modules with published interfaces as an alternative for tighter version control.

---

### 💻 Code Example

```hcl
# --- PRODUCER CONFIG (networking/main.tf) ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "private" {
  for_each          = toset(["us-east-1a", "us-east-1b"])
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet("10.0.0.0/16", 8, index(
    tolist(toset(["us-east-1a", "us-east-1b"])), each.key))
  availability_zone = each.key
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "Main VPC ID for consumer configs"
}

output "private_subnet_ids" {
  value       = values(aws_subnet.private)[*].id
  description = "Private subnet IDs"
}

# --- CONSUMER CONFIG (application/main.tf) ---
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "my-company-tf-state"
    key    = "networking/prod/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_ecs_service" "api" {
  name            = "api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2

  network_configuration {
    subnets = data.terraform_remote_state.network.outputs.private_subnet_ids
    security_groups = [aws_security_group.api.id]
  }
}
```

---

### ⚖️ Comparison Table

| Approach | Remote State | Hardcoded IDs | SSM Parameter Store | Terraform Module |
|---|---|---|---|---|
| **Coupling** | Loose (output contract) | Very tight | Loose | Tight (shared code) |
| **Auto-update** | On next plan | Never | On next plan | N/A |
| **Type safety** | Partial | None | None | Full |
| **Access control** | Backend IAM | N/A | IAM policy | N/A |
| **Sensitive values** | Possible (risky) | Avoid | ✅ SecureString | Via outputs |
| **Best for** | Cross-team state share | Never | Config sharing | Code reuse |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Remote state reads live cloud data" | It reads the state file - a snapshot from the last apply. It does not call cloud APIs. |
| "Remote state is bidirectional" | It's read-only. The consumer cannot write to the producer's state. |
| "Sensitive outputs are hidden in remote state" | Sensitive outputs are present in the state file. Consumers can read them. Protect via backend IAM policies. |
| "Remote state updates automatically when producer applies" | Consumers get new values on their *next* plan - not automatically. |
| "Remote state and modules solve the same problem" | Remote state shares *values* (runtime data). Modules share *code* (configuration patterns). Different tools for different problems. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Output Renamed / Removed in Producer**
- **Symptom:** `Error: Unsupported attribute: data.terraform_remote_state.X.outputs.old_name`
- **Root Cause:** Producer team removed or renamed an output that consumer depends on
- **Diagnostic:** Check the producer's current outputs:
```bash
cd networking/
terraform output -json | jq 'keys'
```
- **Fix:** Add back the old output name as an alias pointing to the new value, or update all consumers simultaneously.
- **Prevention:** Treat output names as a versioned API. Require consumer review before removing outputs.

**Mode 2: Backend Access Denied**
- **Symptom:** `Error: failed to read state: AccessDenied`
- **Root Cause:** Consumer's IAM role lacks read permission on producer's S3 bucket/key
- **Diagnostic:**
```bash
aws s3 cp s3://my-company-tf-state/networking/prod/terraform.tfstate /tmp/
```
- **Fix:** Add S3 `GetObject` permission for the specific key to consumer's IAM role.
- **Prevention:** Define cross-team state access policies as part of the backend bootstrap infra.

**Mode 3: Circular Remote State References**
- **Symptom:** Configuration A reads remote state from B; B reads remote state from A - plans deadlock
- **Root Cause:** Circular dependency between configurations
- **Diagnostic:** Map the dependency graph of all remote state data sources across configurations.
- **Fix:** Extract shared values to a dedicated "base" configuration that neither A nor B owns but both can read.
- **Prevention:** Design a layered architecture: base → networking → compute → application.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform State, Terraform State Backend, Terraform Overview

**Builds On This (learn these next):** Terraform Module, Terragrunt (dependency blocks)

**Alternatives / Comparisons:** SSM Parameter Store for config sharing, Terraform module outputs, hardcoded values (antipattern)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Data source reading another config's │
│               │ state outputs                        │
│ PROBLEM       │ Hardcoded cross-team IDs break       │
│ KEY INSIGHT   │ Outputs = public API between configs │
│ USE WHEN      │ Cross-team infrastructure references │
│ AVOID WHEN    │ Sensitive secrets; use SSM instead   │
│ TRADE-OFF     │ Loose coupling vs implicit contracts │
│ ONE-LINER     │ data "terraform_remote_state" { }    │
│ NEXT EXPLORE  │ Terraform Module, Terragrunt         │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A consumer configuration reads `subnet_ids` from a producer's remote state. The networking team destroys and recreates their subnets (new IDs). The consumer team hasn't run `terraform plan` yet. What is the exact state of the consumer's infrastructure during the window between producer apply and consumer apply?

2. **(Scale)** An organization has 30 Terraform configurations arranged in a dependency tree using remote state. A "base" configuration's output changes trigger a cascade of required re-plans across all 30 configurations. How would you design an automation system to detect and orchestrate this cascading refresh?

3. **(Design Trade-off)** Remote state creates an implicit, weakly-typed contract between teams (output names as strings, no schema). What are the failure modes of this approach at scale, and how do Terraform module interfaces or SSM Parameter Store solve these problems differently?
