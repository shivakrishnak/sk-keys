---
version: 2
layout: default
title: "Terraform Data Source"
parent: "CI/CD"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /ci-cd/terraform-data-source/
id: CCD-067
category: CI/CD
difficulty: ★★★
depends_on: Terraform Provider, Terraform Overview
used_by: Terraform Resource
related: Terraform Provider, Terraform Remote State
tags:
  - cicd
  - devops
  - advanced
---

# CCD-067 - Terraform Data Source

⚡ **TL;DR -** A Terraform data source reads existing infrastructure values from a provider API without creating or managing any resources.

| Field | Value |
|---|---|
| **Depends on** | Terraform Provider, Terraform Overview |
| **Used by** | Terraform Resource |
| **Related** | Terraform Provider, Terraform Remote State |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** To reference an AWS AMI ID or an existing VPC, you hardcode it: `ami = "ami-0abc12345"`. The AMI ID changes when Amazon releases a new Amazon Linux version. Your configuration breaks or deploys the old, unpatched AMI without warning.

**THE BREAKING POINT:** A team discovers their EC2 instances are running a six-month-old AMI because the ID was hardcoded when the configuration was first written. They were deploying the old AMI on every scale-out event. Security patches weren't being applied.

**THE INVENTION MOMENT:** Data sources query the cloud API at plan time to retrieve current values - the latest AMI ID, the ID of an existing VPC, current account ID. Values are always fresh. No hardcoding required.

---

### 📘 Textbook Definition

A **Terraform data source** is a `data` block that calls a provider's read-only API to fetch information about existing infrastructure objects not managed by the current Terraform configuration. Data sources are refreshed on every `terraform plan`, their values are not stored in state as managed resources, and their results can be referenced throughout the configuration. Data sources complement resources: where `resource` blocks create infrastructure, `data` blocks read it.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Data sources are read-only queries to the cloud API - fetch values without creating or managing anything.

> A data source is like a `SELECT` query against a cloud API: you describe what you're looking for (filters), and the provider returns the matching record's attributes (ID, ARN, endpoint) for use in your configuration.

**One insight:** The key distinction: data sources are **not in state as managed resources**. If you delete the data block, nothing in the cloud changes. If you delete a resource block, Terraform plans to destroy the real infrastructure.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Data sources call provider Read APIs; they never call Create, Update, or Delete.
2. Data source results are not persisted in state as managed resources.
3. Data sources are evaluated at plan time; results can be used in resource arguments.
4. Data sources can create implicit dependencies - resources that reference data source attributes are planned after the data source query.

**DERIVED DESIGN:** Data sources bridge the gap between resources managed by the current configuration and everything else (resources managed externally, AWS-provided values like account IDs, latest AMIs). They prevent hardcoding while keeping configurations self-contained.

**THE TRADE-OFFS:**
**Gain:** Always-current values (AMI IDs, VPC IDs); no hardcoding; query external state without managing it.
**Cost:** Data sources add API calls at plan time; filter bugs can silently match wrong resources; data source failures block all plans.

---

### 🧪 Thought Experiment

**SETUP:** You need to deploy EC2 instances using the latest Amazon Linux 2023 AMI. AMI IDs are region-specific and change with every security patch release.

**WHAT HAPPENS WITHOUT DATA SOURCE:** You hardcode `ami = "ami-0abcdef1234567890"`. Two months later, a new patched AMI is released. Your instances still deploy the old AMI. Security team flags it. You manually look up the new AMI ID. Six engineers across six regions each need to update their hardcoded value.

**WHAT HAPPENS WITH DATA SOURCE:** `data "aws_ami" "amazon_linux"` filters for the latest Amazon Linux 2023 AMI matching your criteria. Every `terraform plan` fetches the current latest AMI ID from AWS. Deployments always use the patched version automatically. Zero manual updates.

**THE INSIGHT:** Data sources turn point-in-time lookups (when you first wrote the code) into always-current queries (every time you plan). They remove the maintenance burden of keeping reference values fresh.

---

### 🧠 Mental Model / Analogy

> A data source is like a live lookup in a phonebook rather than a saved phone number: instead of saving "John Smith: 555-1234" (hardcoding) and hoping it doesn't change, you look up "John Smith" every time (data source) and always get the current number.

- Data source block → phonebook lookup query
- Filter arguments → search criteria
- Provider API → the phonebook
- Result attributes → the returned phone number
- `data.aws_ami.latest.id` → the number you dialed

Where this analogy breaks down: unlike a phonebook lookup, data source results are computed at plan time - if the phonebook changes between plan and apply, the value used for apply was locked at plan time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** A data source looks something up in the cloud without creating anything. Like `SELECT` in SQL - query-only.

**Level 2 - How to use it (junior developer):** Write a `data "<type>" "<name>"` block with filter arguments. Reference its attributes as `data.<type>.<name>.<attribute>`. Common use cases: latest AMI ID, existing VPC ID, current AWS account ID.

**Level 3 - How it works (mid-level engineer):** During plan, Terraform calls the provider's `ReadDataSource` RPC. The provider calls the cloud API with your filter arguments, finds the matching resource, and returns its attributes. These attributes are available in the current plan computation. The data source result is not written to state as a managed resource.

**Level 4 - Why it was designed this way (senior/staff):** Data sources create a clean boundary between "what this configuration manages" and "what exists in the world." The separation prevents Terraform from accidentally destroying resources it only queried. The `depends_on` meta-argument on data sources handles the case where a resource must be created before a data source can successfully query it - an uncommon but important pattern for resources that affect discovery results.

---

### ⚙️ How It Works (Mechanism)

**Data source lifecycle during plan:**
1. Terraform encounters `data "aws_ami" "al2023"` block
2. Calls provider's `ReadDataSource` RPC
3. Provider calls AWS EC2 `DescribeImages` API with filter arguments
4. Provider returns matching attributes (id, name, creation_date, etc.)
5. Attributes available as `data.aws_ami.al2023.*` for the rest of the plan

**Data sources in state:**
Data sources ARE stored in state (in the `data` section) so Terraform can detect when filters change and re-query. But they're not managed resources - deleting the data block doesn't affect the queried resource.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  data "aws_ami" "al2023" {    ← YOU ARE HERE
    most_recent = true
    owners      = ["amazon"]
    filter {
      name   = "name"
      values = ["al2023-ami-2023*-x86_64"]
    }
  }
           │
  terraform plan
           │
  Provider: DescribeImages API call
  → Returns: ami-0abc1234 (latest match)
           │
  resource "aws_instance" "web" {
    ami = data.aws_ami.al2023.id  # "ami-0abc1234"
    ...
  }
           │
  EC2 instance created with current patched AMI
```

**FAILURE PATH:** Data source filter matches zero resources. Plan fails: `Error: no matching AMI found`. This is a design feature - fail loudly rather than hardcode a wrong value.

**WHAT CHANGES AT SCALE:** Data sources for frequently-changing values (latest AMIs) should have tight filters to avoid unexpected changes. For cross-team references, `terraform_remote_state` is preferable to querying raw AWS tags because it provides typed, versioned outputs.

---

### 💻 Code Example

```hcl
# BAD: hardcoded AMI ID that goes stale
resource "aws_instance" "web" {
  ami           = "ami-0abc12345"  # will be outdated
  instance_type = "t3.micro"
}

# GOOD: data source for always-current AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023*-x86_64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.micro"
}

# Data source: existing VPC (not managed here)
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["prod-vpc"]
  }
}

resource "aws_security_group" "app" {
  vpc_id = data.aws_vpc.existing.id
  name   = "app-sg"
}

# Data source: current AWS account and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  bucket_arn = "arn:aws:s3:::my-bucket"
}

# Data source: IAM policy document (HCL-rendered JSON)
data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

# Data source: depends_on (uncommon, needed for ordering)
resource "aws_iam_role_policy" "inline" {
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_assume.json
}

# Use depends_on when data source depends on a resource
# that must be created first (rare pattern)
data "aws_lambda_invocation" "config_fetch" {
  function_name = aws_lambda_function.config.function_name
  input         = jsonencode({ action = "fetch_config" })
  depends_on    = [aws_lambda_function.config]
}
```

---

### ⚖️ Comparison Table

| Approach | Data Source | Hardcoded | terraform_remote_state | Variable |
|---|---|---|---|---|
| **Always current** | ✅ | ❌ | ✅ (last apply) | ❌ (manual update) |
| **Manages resource** | ❌ | ❌ | ❌ | ❌ |
| **Typed contract** | Provider-defined | None | Output-defined | Variable-defined |
| **Cross-team** | Via tags/names | Via docs | Via state outputs | Via tfvars |
| **Failure mode** | Filter mismatch | Stale value | Output missing | Missing value |
| **Best for** | AWS-native lookups | Never | Cross-config refs | Config params |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Data sources are not in state" | Data sources ARE stored in state (in the `data` section) so Terraform can detect filter changes. But they are not managed resources. |
| "Deleting a data source destroys the queried resource" | No. Deleting a `data` block only removes the state entry for the lookup. The queried resource is unaffected. |
| "Data sources always reflect real-time values during apply" | Data source values are resolved at plan time. If the queried resource changes between plan and apply, the apply uses the plan-time value. |
| "`depends_on` is never needed for data sources" | Rare cases exist: if a data source queries a resource that must be created first (e.g. Lambda invocation), `depends_on` is required. |
| "Data source filters always return exactly one result" | A filter matching multiple resources returns an error (for single-result data sources). Use `most_recent` or sufficiently specific filters. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Filter Matches Multiple Resources**
- **Symptom:** `Error: multiple EC2 VPCs matched; use a more specific query`
- **Root Cause:** Data source filter is too broad; multiple resources match
- **Diagnostic:**
```bash
aws ec2 describe-vpcs --filters Name=tag:Name,Values="prod-vpc" \
  --query 'Vpcs[].VpcId'
```
- **Fix:** Add more specific filters (account ID, creation date, additional tags).
- **Prevention:** Use unique, deterministic tags. Name tags alone are not guaranteed unique.

**Mode 2: AMI Data Source Selects Unexpected New AMI**
- **Symptom:** After a routine plan, Terraform shows EC2 instance replacement because `data.aws_ami.latest.id` changed
- **Root Cause:** AWS released a new AMI matching your filter; `most_recent = true` selected it
- **Diagnostic:**
```bash
terraform plan 2>&1 | grep "ami-"
# Shows old vs new AMI ID
```
- **Fix:** For stable deployments, pin to a specific AMI name pattern (include version) rather than pure `most_recent`. Or use `lifecycle { ignore_changes = [ami] }` on instances.
- **Prevention:** Separate "AMI refresh" from "routine deployment" as a deliberate update with scheduled maintenance windows.

**Mode 3: Data Source Queries Before Resource Exists**
- **Symptom:** `Error: data source depends on a resource that doesn't exist yet`
- **Root Cause:** Data source queries AWS before a prerequisite resource is created
- **Diagnostic:** Review the resource dependency chain.
- **Fix:** Add `depends_on = [aws_resource.prerequisite]` to the data source block.
- **Prevention:** Make dependencies explicit when data source queries depend on resources in the same configuration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Terraform Provider, Terraform Overview, Terraform Resource

**Builds On This (learn these next):** Terraform Remote State, Terraform Variable / Output / Local

**Alternatives / Comparisons:** `terraform_remote_state` (cross-config references), hardcoded values (antipattern), AWS SSM Parameter Store

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Read-only query to provider API      │
│ PROBLEM       │ Hardcoded cloud IDs go stale         │
│ KEY INSIGHT   │ Data source ≠ managed resource;      │
│               │ deleting block ≠ deleting resource   │
│ USE WHEN      │ Latest AMI, existing VPC, account ID │
│ AVOID WHEN    │ Cross-team state refs (use remote     │
│               │ state instead)                       │
│ TRADE-OFF     │ Always-current vs plan-time snapshot  │
│ ONE-LINER     │ data "aws_ami" "latest" { ... }      │
│ NEXT EXPLORE  │ Terraform Remote State, Variables    │
└──────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** A data source using `most_recent = true` selects a new AMI during a plan. The new AMI is used in resource blocks that create EC2 instances. The plan shows instance replacement for all 50 running instances. How do you balance the desire for always-patched AMIs with the operational risk of replacing all instances simultaneously?

2. **(Root Cause)** A `data "aws_vpc" "main"` data source uses a tag filter to find an existing VPC. The VPC tag is renamed by another team. The next Terraform plan fails with "no matching VPC found." What process breakdown allowed this to happen, and how would you design cross-team dependencies to prevent this failure mode?

3. **(Design Trade-off)** For cross-team infrastructure references, you can use (a) `data` sources that query by tags/names, (b) `terraform_remote_state` that reads another config's outputs, or (c) AWS SSM Parameter Store that stores values out-of-band. What are the coupling characteristics, failure modes, and maintenance burdens of each approach, and when would you choose each?
