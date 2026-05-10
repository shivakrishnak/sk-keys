---
version: 2
layout: default
title: "Terraform Resource"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 56
permalink: /ci-cd/terraform-resource/
id: CCD-056
category: CI/CD
difficulty: ★★☆
depends_on: Terraform Provider, Terraform Overview
used_by: Terraform Module, Terraform State
related: Terraform Provider, Terraform Data Source, Terraform Module
tags:
  - cicd
  - devops
  - intermediate
---

# CCD-056 - Terraform Resource

⚡ **TL;DR -** A Terraform resource block declares a single infrastructure object that Terraform creates, reads, updates, and deletes through a provider.

| Field | Value |
|---|---|
| **Depends on** | Terraform Provider, Terraform Overview |
| **Used by** | Terraform Module, Terraform State |
| **Related** | Terraform Provider, Terraform Data Source, Terraform Module |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Infrastructure components would need to be described in prose, scripts, or configuration files that different tools interpret differently. There is no universal unit of infrastructure that tooling can reason about.

**THE BREAKING POINT:** A Bash script that creates an EC2 instance is imperative: `aws ec2 run-instances …`. If the instance already exists, the script creates a duplicate. The script cannot update an existing instance. The script leaves no record of what it manages.

**THE INVENTION MOMENT:** Terraform introduces the `resource` block: a declarative, named, typed unit of infrastructure. The tool manages the full lifecycle. One definition, idempotent behavior.

---

### 📘 Textbook Definition

A **Terraform resource** is a block in HCL that declares a single infrastructure object of a specific type, managed by a provider. The resource block specifies the type (e.g. `aws_vpc`), a local name, and configuration arguments. Terraform tracks the resource in its state file and is responsible for creating, reading, updating, and deleting the actual infrastructure object to match the declared configuration.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A resource block is a named declaration of one infrastructure object and its desired configuration.

> A resource is like a row in a database schema: the type is the table name, the arguments are the column values, and Terraform is the ORM that ensures the database matches your object definition.

**One insight:** The resource's **address** (`aws_vpc.main`) is its identity in state. If you rename a resource in HCL, Terraform sees a delete + create - not a rename - unless you use `terraform state mv`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each resource block maps to exactly one real infrastructure object.
2. Resources have types (defined by providers) and local names (defined by the engineer).
3. Resource arguments are inputs; computed attributes are outputs readable after creation.
4. Resource addresses (`<type>.<name>`) are globally unique within a configuration.

**DERIVED DESIGN:** Terraform builds an implicit dependency graph from resource attribute references (`aws_subnet.main.vpc_id = aws_vpc.main.id`). Resources without references to each other are created in parallel; dependent resources are created in topological order.

**THE TRADE-OFFS:**
**Gain:** Declarative, idempotent infrastructure objects with full lifecycle management.
**Cost:** Every resource must be in state; large configurations with hundreds of resources create state management challenges.

---

### 🧪 Thought Experiment

**SETUP:** You declare `resource "aws_s3_bucket" "logs"` and apply. Then you rename it to `resource "aws_s3_bucket" "audit_logs"`.

**WHAT HAPPENS WITHOUT UNDERSTANDING RESOURCE IDENTITY:** You rename and apply. Terraform deletes the old bucket (including data) and creates a new empty bucket with the new name. Your audit logs are gone.

**WHAT HAPPENS WITH UNDERSTANDING:** Before renaming, you run `terraform state mv aws_s3_bucket.logs aws_s3_bucket.audit_logs`. Now Terraform knows the renamed resource is the same object. The apply shows zero changes.

**THE INSIGHT:** Resource *address* is identity in Terraform's world. Configuration changes that alter the address without state migration are destructive by default.

---

### 🧠 Mental Model / Analogy

> A resource block is like a row in a Git-tracked spreadsheet for your cloud: each row is a typed object with named columns, and Terraform's job is to ensure the live cloud "database" matches every row in your spreadsheet.

- Resource type → spreadsheet table name
- Resource local name → row identifier
- Arguments → cell values (your desired config)
- Computed attributes → auto-populated cells (e.g. ID assigned by AWS)
- State → the spreadsheet's last-known-good snapshot

Where this analogy breaks down: unlike a spreadsheet, computed attribute values are available for other resources to reference within the same configuration, enabling a declarative dependency graph.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** A resource block is Terraform's way of saying "I want this thing to exist." One block = one real-world infrastructure object.

**Level 2 - How to use it (junior developer):** Write a `resource "<type>" "<name>"` block with the required arguments from the provider documentation. Reference its attributes in other resources using `<type>.<name>.<attribute>`. Run `terraform plan` to see what will be created.

**Level 3 - How it works (mid-level engineer):** Terraform computes a DAG from resource references. During plan, it calls `provider.ReadResource` to get current state and diffs against desired. During apply, it calls `provider.ApplyResourceChange`. After apply, the resource's ID and all attributes are persisted in the state file.

**Level 4 - Why it was designed this way (senior/staff):** The resource block as a typed, named, addressed unit enables Terraform to maintain referential integrity across configurations. The separation of *arguments* (inputs you control) from *attributes* (outputs computed by the cloud API) maps cleanly to the provider's CRUD interface and allows cross-resource references to be resolved at plan time without calling the API.

---

### ⚙️ How It Works (Mechanism)

During `terraform apply`, for each resource in the plan:

1. **Provider lookup** - Terraform routes the operation to the correct provider instance.
2. **PlanResourceChange** - Provider receives proposed new state; computes what the apply will do (may mark unknown values).
3. **ApplyResourceChange** - Provider calls the cloud API (Create, Update, or Delete).
4. **State persistence** - Provider returns the new full state (including computed attributes like IDs). Terraform writes it to state.

Resource dependencies are encoded in the DAG. `depends_on` creates explicit edges for cases where the dependency is not visible through attribute references (e.g. IAM policy propagation delay).

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  resource "aws_vpc" "main" { ... }
  resource "aws_subnet" "a" {
    vpc_id = aws_vpc.main.id  # implicit dep
  }
           │
  Terraform builds DAG:
    aws_vpc.main → aws_subnet.a
           │
  terraform plan
           │
  aws_vpc.main created first     ← YOU ARE HERE
           │
  aws_subnet.a created after
  (vpc_id attribute now known)
           │
  Both in state with full attrs
```

**FAILURE PATH:** A resource creation fails (e.g. S3 bucket name already taken globally). Terraform marks it `tainted`. Dependent resources are not created. Next plan shows the tainted resource for replacement.

**WHAT CHANGES AT SCALE:** Hundreds of resources require `count` or `for_each` meta-arguments to avoid repetitive blocks. Large resource sets benefit from module encapsulation for readability and reuse.

---

### 💻 Code Example

```hcl
# BAD: no dependency, hardcoded values, no tags
resource "aws_subnet" "a" {
  vpc_id     = "vpc-0abc1234"  # hardcoded!
  cidr_block = "10.0.1.0/24"
}

# GOOD: implicit dependency via reference,
#       for_each for multiple subnets, tags
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { ManagedBy = "terraform" }
}

# for_each to avoid repetition
resource "aws_subnet" "public" {
  for_each = {
    "us-east-1a" = "10.0.1.0/24"
    "us-east-1b" = "10.0.2.0/24"
  }

  vpc_id            = aws_vpc.main.id  # implicit dep
  cidr_block        = each.value
  availability_zone = each.key

  tags = {
    Name      = "public-${each.key}"
    ManagedBy = "terraform"
  }
}

# Explicit depends_on for non-attribute dependencies
resource "aws_iam_role_policy_attachment" "worker" {
  role       = aws_iam_role.worker.name
  policy_arn = aws_iam_policy.worker.arn
}

resource "aws_instance" "worker" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.worker.name

  # IAM propagation delay not visible in attributes
  depends_on = [aws_iam_role_policy_attachment.worker]
}
```

---

### ⚖️ Comparison Table

| Concept | Resource | Data Source | Variable | Local |
|---|---|---|---|---|
| **Creates infra** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **In state file** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Mutable** | ✅ Yes | ❌ Read-only | ❌ Input | ❌ Computed |
| **API calls** | Create/Read/Update/Delete | Read only | None | None |
| **Address format** | `type.name` | `data.type.name` | `var.name` | `local.name` |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Renaming a resource in HCL renames it in the cloud" | Renaming the local name changes the address; Terraform plans delete + create. Use `terraform state mv`. |
| "`depends_on` is always implicit" | Only when you reference attributes. Non-attribute dependencies (IAM propagation, DNS TTLs) require explicit `depends_on`. |
| "Resources with `count = 0` are removed cleanly" | Changing `count` expressions can force replacement of all instances. Use `for_each` with stable keys instead. |
| "All arguments are required" | Each resource type has required and optional arguments. Check provider docs; optional args use provider defaults. |
| "Computed attributes are available during plan" | Computed attributes unknown before apply show as `(known after apply)` in plan output. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Accidental Resource Recreation**
- **Symptom:** Plan shows `- destroy` then `+ create` for a resource you only renamed
- **Root Cause:** Resource address changed because local name or type changed in HCL
- **Diagnostic:**
```bash
terraform state list | grep <resource_type>
terraform plan -out=tfplan && terraform show tfplan
```
- **Fix - BAD:** Accept the destroy/create plan without investigation.
- **Fix - GOOD:** Use `terraform state mv old_address new_address` before applying renamed HCL.
- **Prevention:** Treat resource addresses as stable identifiers; code review any renames.

**Mode 2: Orphaned Resources**
- **Symptom:** Resources in cloud that Terraform doesn't manage; `terraform plan` is clean but AWS console shows extra items
- **Root Cause:** Resources created outside Terraform, or removed from HCL without `terraform destroy`
- **Diagnostic:**
```bash
terraform state list
# Compare with AWS console or aws cli
```
- **Fix:** Import existing resources with `terraform import` or `import` blocks (TF 1.5+).
- **Prevention:** Enforce all resource creation through Terraform; use SCPs/policies.

**Mode 3: `for_each` Key Collisions**
- **Symptom:** `Error: Duplicate resource address` after changing for_each keys
- **Root Cause:** Two entries in the for_each map produce the same sanitized key
- **Diagnostic:** Review `for_each` map for duplicate or near-duplicate keys.
- **Fix:** Ensure for_each keys are unique and stable. Use `terraform state mv` to migrate if keys changed.
- **Prevention:** Use immutable business identifiers (IDs, ARNs) as for_each keys, never user-supplied strings.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Overview, Terraform Provider

**Builds On This (learn these next):** Terraform Module, Terraform State, Terraform Lifecycle Rules

**Alternatives / Comparisons:** Terraform Data Source (read-only), AWS CloudFormation Resource, CDK Construct

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Declarative infrastructure object    │
│ PROBLEM       │ Imperative scripts aren't idempotent │
│ KEY INSIGHT   │ Address = identity in state          │
│ USE WHEN      │ Any managed cloud object             │
│ AVOID WHEN    │ Read-only lookups (use data source)  │
│ TRADE-OFF     │ Full lifecycle control vs state mgmt │
│ ONE-LINER     │ resource "aws_vpc" "main" { ... }    │
│ NEXT EXPLORE  │ Terraform State, Lifecycle Rules     │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** When a resource has `for_each` with 50 items and you remove 3 items from the map, what exactly happens during plan/apply, and what are the risks if any of those 3 resources hold data?

2. **(Scale)** A configuration has 200 resources that all share the same `depends_on` chain. Plan and apply are serialized and very slow. What architectural refactoring would break this dependency chain without losing correctness?

3. **(Design Trade-off)** Terraform's resource model requires a provider to implement CRUD for every resource type. What are the implications for resources that the cloud API can create but never update (immutable resources), and how should Terraform and the engineer handle them?
