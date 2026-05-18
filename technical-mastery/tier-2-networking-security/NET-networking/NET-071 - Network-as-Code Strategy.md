---
id: NET-071
title: "Network-as-Code Strategy"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-052, NET-069
used_by: NET-075
related: NET-052, NET-069, NET-075
tags:
  - networking
  - infrastructure-as-code
  - terraform
  - automation
  - gitops
  - network-automation
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 71
permalink: /technical-mastery/net/network-as-code-strategy/
---

**⚡ TL;DR** - Network-as-Code (NaC) applies infrastructure-
as-code principles to network configuration: define VPCs,
subnets, security groups, firewall rules, DNS records,
and load balancer configs in version-controlled code
(Terraform, Pulumi, Crossplane). Benefits: reproducibility
(same infra in any region), auditability (git log shows
who changed what firewall rule), and disaster recovery
(recreate entire network in minutes). The failure pattern
is having code describe current state but manual drift
happening over time - prevent with enforcement tooling.

| #071 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Network Segmentation (NET-052), Multi-Region Network Architecture (NET-069) | |
| **Used by:** | Build a Secure Network Platform (NET-075) | |
| **Related:** | Network Segmentation, Multi-Region Architecture, Build a Secure Network Platform | |

---

### 🔥 The Problem Without NaC

```
Before NaC:
  Network admin: SSH into router, type commands
  Security engineer: click through AWS console, add SG rule
  Results: 
    No audit trail: "who added this firewall rule?"
    No reproducibility: "rebuild this VPC after disaster"
    Config drift: console changes not reflected in Terraform
    Peer review: no review process for network changes
    Testing: no way to test a firewall rule change before prod
    
After NaC:
  All network changes: pull request, reviewed, merged, applied
  Audit trail: git blame shows who changed the firewall rule
  Reproducibility: terraform apply creates identical environment
  Drift detection: CI pipeline detects out-of-band changes
  Testing: plan output reviewed before apply
```

---

### ⚙️ Core Tools

```
Terraform (most common):
  HashiCorp HCL, declarative: "what should exist"
  Providers: AWS, Azure, GCP, Cloudflare, PagerDuty, etc.
  State: remote state (S3 + DynamoDB lock) for teams
  Plan: shows what will change before applying
  Apply: makes the changes
  
Pulumi:
  Same concept as Terraform but uses real languages
  Python, TypeScript, Go, Java - no HCL
  Better for complex logic (loops, conditionals, abstraction)
  Less ecosystem than Terraform currently
  
Crossplane:
  Kubernetes-native: manage cloud resources via K8s CRDs
  GitOps: ArgoCD/Flux syncs to K8s, K8s provisions cloud
  Best for: teams already using K8s and GitOps
  
Ansible (for device configuration):
  Imperative + idempotent
  Configures actual network devices: routers, switches
  Good for: BGP configs, VLAN configs on physical hardware
  NAPALM: Ansible plugin for network device abstraction
  
Cloud-native:
  AWS CDK: Python/TypeScript to CloudFormation
  Azure Bicep: ARM template replacement
  GCP Deployment Manager: similar concept
```

---

### ⚙️ Terraform Network Example

```hcl
# Complete network layer: VPC, subnets, security groups
# This file: all network infrastructure for a production env

# ─────────────────────────────────────────
# VPC
# ─────────────────────────────────────────
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr    # "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = "platform"
  }
}

# ─────────────────────────────────────────
# Subnets (3 AZs × 3 tiers = 9 subnets)
# ─────────────────────────────────────────
locals {
  azs              = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_cidrs     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_cidrs    = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  database_cidrs   = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

resource "aws_subnet" "public" {
  count             = length(local.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.public_cidrs[count.index]
  availability_zone = local.azs[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.environment}-public-${local.azs[count.index]}"
    Tier = "public"
  }
}

resource "aws_subnet" "private" {
  count             = length(local.azs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_cidrs[count.index]
  availability_zone = local.azs[count.index]
  
  tags = {
    Name = "${var.environment}-private-${local.azs[count.index]}"
    Tier = "private"
  }
}

# ─────────────────────────────────────────
# Security Groups with explicit rules
# ─────────────────────────────────────────
resource "aws_security_group" "app" {
  name        = "${var.environment}-app-sg"
  description = "Application servers: allow from ALB only"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    # NOT from 0.0.0.0/0 - only from the ALB SG
  }
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name        = "${var.environment}-app-sg"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

---

### ⚙️ Drift Detection and Prevention

```bash
# Problem: someone manually changed a security group in console
# Terraform doesn't know → state diverges from reality

# Detection: CI pipeline runs terraform plan on a schedule
# Any diff = drift alert

# GitHub Actions drift detection:
cat > .github/workflows/drift-detection.yml << 'EOF'
name: Terraform Drift Detection
on:
  schedule:
    - cron: "0 */6 * * *"  # every 6 hours

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: ${{ secrets.TF_ROLE_ARN }}
          aws-region: us-east-1
          
      - name: Terraform plan
        id: plan
        run: |
          cd infrastructure/network
          terraform init -backend-config="bucket=my-tf-state"
          terraform plan -detailed-exitcode -out=plan.out 2>&1
        continue-on-error: true
        
      - name: Alert on drift
        if: steps.plan.outputs.exitcode == '2'
        # exit code 2 = changes needed (drift)
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: "DRIFT DETECTED: Network infrastructure changed manually",
              body: "Terraform plan detected drift. Review and reconcile.",
              labels: ["infrastructure-drift", "network"]
            })
EOF

# Prevention: enforce via OPA (Open Policy Agent) or
# SCPs (Service Control Policies) in AWS
# Block: console-based changes to production security groups
# Allow: only CI/CD role to modify network resources
```

---

### ⚙️ Wrong vs Right: Hardcoded vs Parameterized

```hcl
# BAD: hardcoded values, environment-specific, not reusable
resource "aws_security_group" "db" {
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.11.0/24"]  # hardcoded app subnet
    # What if app subnet changes? Manual update needed
    # Not reusable across environments (staging, prod)
  }
}

# BAD: no description on rules (who added this and why?)
resource "aws_security_group" "web" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SSH open to world!
  }
}

# GOOD: parameterized, documented, least-privilege
resource "aws_security_group" "db" {
  name        = "${var.environment}-db-sg"
  description = "Database: allow PostgreSQL from app tier only"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "PostgreSQL from app servers"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    # References SG ID - follows the resource, not the IP
  }
  
  # SSH: no direct SSH - use AWS SSM Session Manager instead
  # SSM: no inbound rule needed, no exposed port
}
```

---

### 📐 Scale Considerations

```
Single team (< 5 engineers):
  Monorepo for all Terraform
  One state file per environment: simple
  
Multiple teams (5-20 engineers):
  Module-based Terraform: shared modules, local state
  "Network" module: owned by platform team
  "App" module: owned by app teams
  Interface: module input/output variables
  
Platform org (100+ engineers):
  Terraform modules published to private registry
  Separation: network module (platform) vs app module (app team)
  Policy-as-code: OPA or Sentinel gates all Terraform changes
  Drift detection: automated CI runs plan checks every 6 hours
  
GitOps model:
  Crossplane + ArgoCD: network changes via K8s manifests
  All changes: Git PR → ArgoCD detects → applies to cluster
  Cluster provisions cloud resources via Crossplane
  Fully auditable: every change a Git commit
  
State management at scale:
  One state file per (environment, region, component):
  path: us-east-1/production/network/terraform.tfstate
  Never one giant state file (lock contention, blast radius)
  Terragrunt: DRY wrapper for multiple Terraform modules
```

---

### 🧭 Decision Guide

```
Tool selection:

Single cloud, small team:
  Terraform: best ecosystem, most documentation
  
Multi-language team, complex logic:
  Pulumi: Python/TypeScript more expressive than HCL
  Loops, conditionals, abstractions are cleaner
  
Kubernetes-centric org:
  Crossplane: manages cloud resources as K8s CRDs
  ArgoCD/Flux: GitOps - push to Git, auto-applies
  
Network device configuration (physical hardware):
  Ansible + NAPALM: abstracts network OS differences
  Nornir: Python network automation framework
  
Starting NaC adoption:
  1. Import existing infra to Terraform (terraform import)
  2. Don't change anything, just codify current state
  3. Add tagging and documentation to existing resources
  4. Add CI validation (fmt, validate, plan) on PR
  5. Add drift detection after state is stable
  6. Only after step 5: start making changes via code only
  
  Biggest failure: "Let's write Terraform for everything in a sprint"
  No audit trail of what existing infra actually does
  Result: Terraform plan destroys prod because state != reality
```
permalink: /technical-mastery/net/network-as-code-strategy/
---