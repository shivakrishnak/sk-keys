---
layout: default
title: "Infrastructure as Code (IaC)"
parent: "DevOps & SDLC"
nav_order: 455
permalink: /devops-sdlc/infrastructure-as-code-iac/
number: "455"
category: DevOps & SDLC
difficulty: ★★☆
depends_on: Version Control, CI/CD Pipeline
used_by: GitOps, Immutable Infrastructure, Cloud Provisioning
tags: #devops #sdlc #intermediate #iac
---

# 455 — Infrastructure as Code (IaC)

`#devops` `#sdlc` `#intermediate` `#iac`

⚡ TL;DR — Define and provision infrastructure (servers, networks, databases) through machine-readable configuration files instead of manual processes.

| #455 | Category: DevOps & SDLC | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Version Control, CI/CD Pipeline | |
| **Used by:** | GitOps, Immutable Infrastructure, Cloud Provisioning | |

---

### 📘 Textbook Definition

Infrastructure as Code (IaC) is the practice of managing and provisioning computing infrastructure through machine-readable definition files rather than through manual configuration or interactive tools. Infrastructure is described declaratively or imperatively in code, stored in version control, and applied through automated pipelines — enabling repeatable, consistent, and auditable infrastructure management.

---

### 🟢 Simple Definition (Easy)

IaC means **writing code to create your servers, networks, and databases** instead of clicking through a cloud console. Run the code, get the infrastructure — repeatable every time.

---

### 🔵 Simple Definition (Elaborated)

Before IaC, spinning up infrastructure meant clicking through cloud consoles, following runbooks, or SSHing into servers and running commands. This was slow, error-prone, inconsistent across environments, and impossible to audit. IaC treats infrastructure like application code: version-controlled, reviewed via pull requests, tested, and deployed automatically. Creating a new environment is as simple as running a tool against the code.

---

### 🔩 First Principles Explanation

**The core problem:**
Manually configured infrastructure is a "snowflake" — every server is subtly different. You cannot reproduce it exactly. Runbooks become stale. "It works in staging but not in prod" because they diverged.

**The insight:**
> "If you can describe your infrastructure in code, you can create identical copies, version it, review it, and destroy+recreate it at any time."

```
Without IaC:
  ClickOps: dev → staging → prod differ subtly → bugs
  Runbooks get stale → deployments fail → tribal knowledge

With IaC:
  Code describes: "3 VMs, 16GB RAM, in VPC X, with SG Y"
  Run once → dev environment
  Run again → identical staging environment
  Run again → identical production environment
```

---

### ❓ Why Does This Exist (Why Before What)

Without IaC, infrastructure is undocumented, non-reproducible, and owned by individuals with tribal knowledge. Disaster recovery means manually rebuilding what was running — facing memory errors and missing steps. IaC makes infrastructure reproducible, reviewable, and recoverable.

---

### 🧠 Mental Model / Analogy

> IaC is like an architectural blueprint for infrastructure. A blueprint lets you build the same building in any city — the construction team follows the same plan every time, producing identical buildings. Without blueprints, every building would be slightly different based on who built it that day.

---

### ⚙️ How It Works (Mechanism)

```
Two main approaches:

  Declarative (WHAT):
    Describe desired final state; tool figures out HOW to get there
    Examples: Terraform, CloudFormation, Pulumi (declarative mode)

    terraform.tf:
      resource "aws_instance" "web" {
        ami = "ami-12345"
        instance_type = "t3.medium"
      }
    → Terraform creates/modifies/destroys to match this state

  Imperative (HOW):
    Describe the exact steps to reach desired state
    Examples: Ansible playbooks, shell scripts, Chef recipes

    ansible.yml:
      - name: install nginx
        apt: name=nginx state=present
    → Ansible executes these steps in order

Terraform lifecycle:
  terraform init    -- download providers
  terraform plan    -- show what WILL change (dry run)
  terraform apply   -- apply changes
  terraform destroy -- tear down all resources
```

---

### 🔄 How It Connects (Mini-Map)

```
[IaC Code in Git]
       ↓ reviewed via PR
[CI/CD Pipeline]
       ↓ terraform plan (review)
       ↓ terraform apply (apply)
[Cloud Infrastructure provisioned]
       ↓ used by
[Application Deployment (GitOps)]
```

---

### 💻 Code Example

```hcl
# Terraform — provision AWS infrastructure
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" { region = "us-east-1" }

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "production-vpc" }
}

# EC2 instance
resource "aws_instance" "app" {
  count         = 3                        # 3 identical instances
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.medium"
  vpc_security_group_ids = [aws_security_group.app.id]
  tags = { Name = "app-server-${count.index}" }
}

# RDS database
resource "aws_db_instance" "main" {
  engine         = "postgres"
  engine_version = "15"
  instance_class = "db.t3.medium"
  allocated_storage = 100
  db_name        = "appdb"
  username       = "admin"
  password       = var.db_password          # from secrets, not hardcoded
  skip_final_snapshot = false
}
```

---

### 🔁 Flow / Lifecycle

```
1. Write IaC configuration files (Terraform, CloudFormation, etc.)
        ↓
2. Commit to git, open pull request
        ↓
3. CI runs: terraform validate + terraform plan (shows diff)
        ↓
4. Team reviews the plan output (what will be created/changed/destroyed)
        ↓
5. Merge PR → CI runs terraform apply
        ↓
6. Infrastructure provisioned/updated
        ↓
7. State stored in remote backend (S3, Terraform Cloud)
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| IaC = just YAML/JSON files | IaC includes real code with variables, modules, loops, conditions |
| Terraform is the only IaC tool | Terraform, Pulumi, CloudFormation, Ansible, CDK — many valid options |
| IaC eliminates all manual work | IaC automates provisioning; ops decisions still require human judgment |
| IaC state is optional | Remote state management is critical for team collaboration and drift detection |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Secrets Hardcoded in IaC**
Passwords or API keys committed to git in IaC files.
Fix: use variables + secrets manager (AWS Secrets Manager, Vault); never hardcode credentials.

**Pitfall 2: No Remote State / State Locking**
Two engineers run `terraform apply` simultaneously → state corruption.
Fix: always use remote backend (S3 + DynamoDB locking); never use local state in teams.

**Pitfall 3: Manual Changes (Snowflakes Return)**
Engineers SSH in and make changes outside IaC → configuration drift.
Fix: enforce IaC-only changes via policy; use GitOps to detect and revert drift.

---

### 🔗 Related Keywords

- **GitOps** — extends IaC principles; git is the source of truth for infra
- **Immutable Infrastructure** — IaC enables rebuilding infra from scratch instead of patching
- **CI/CD Pipeline** — the automation layer that runs `terraform apply`
- **Terraform** — the most widely used declarative IaC tool
- **Configuration Drift** — what IaC prevents; manual changes silently diverge from code

---

### 📌 Quick Reference Card

| #455 | Category: DevOps & SDLC | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Version Control, CI/CD Pipeline | |
| **Used by:** | GitOps, Immutable Infrastructure, Cloud Provisioning | |

---

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between declarative and imperative IaC approaches? When would you choose each?  
**Q2.** Why is remote state management with locking critical for team-based Terraform usage?  
**Q3.** How does IaC enable disaster recovery, and why is this more reliable than runbook-based recovery?

