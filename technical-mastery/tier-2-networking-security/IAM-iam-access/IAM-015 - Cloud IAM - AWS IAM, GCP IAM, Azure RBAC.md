---
id: IAM-015
title: "Cloud IAM - AWS IAM, GCP IAM, Azure RBAC"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-006, IAM-013
used_by: IAM-022, IAM-026, IAM-027
related: IAM-013, IAM-022, ATZ-002
tags:
  - iam
  - security
  - cloud
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/iam/cloud-iam-aws-iam-gcp-iam-azure-rbac/
---

⚡ TL;DR - Cloud IAM governs access to cloud provider
APIs and resources. AWS IAM uses JSON policies with
explicit Allow/Deny evaluated per API call. GCP IAM uses
role bindings at resource hierarchy levels with inherited
permissions. Azure RBAC uses role assignments scoped to
management groups, subscriptions, or resource groups.
All three share: default-deny, role-based principal
grouping, and service account equivalents for workloads.

---

### 🔥 The Problem This Solves

Cloud environments have thousands of resources (EC2
instances, S3 buckets, DynamoDB tables, Lambda functions)
and hundreds of principals (engineers, DevOps teams,
automated services, CI/CD pipelines). Without IAM:

- Every engineer has root/admin access "for convenience"
- CI/CD pipeline secrets are hardcoded in config files
- Any compromised account = entire cloud environment
  accessible

Cloud IAM provides the access control layer for every
cloud API call: before any action executes, the cloud
provider evaluates whether the caller's identity has
the necessary permissions. Zero implicit trust.

---

### 📘 Textbook Definition

**AWS IAM:** Identity and Access Management service for
AWS. Controls access to 300+ AWS services via JSON policy
documents. Key concepts: IAM Users, Groups, Roles,
Policies (managed/inline), Permission Boundaries,
Service Control Policies (Organizations), IAM Identity
Center (SSO). Default: all actions denied.

**GCP IAM:** Manages access to Google Cloud resources
via role bindings. Key concepts: principal (Google
account, service account, group), role (predefined/custom),
resource (project, bucket, VM), binding {principal, role}
at resource. Hierarchy: organization > folder > project
> resource. Permissions inherit downward.

**Azure RBAC (Role-Based Access Control):** Controls
access to Azure resources via role assignments.
Key concepts: security principal (user, group, service
principal, managed identity), role definition (set of
allowed operations), scope (management group,
subscription, resource group, resource), role
assignment {principal, role, scope}.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cloud IAM is the access control system for cloud APIs.
Every API call is authorized before it executes.

**One analogy:**
> A cloud provider is a city of government buildings
> (services). IAM is the city-wide access control
> system: every door has a reader, every person has
> an ID, every door has a list of who may enter.
> Before any door opens, the reader checks the list.
> No list entry = door stays closed.

**One insight:**
The critical difference between cloud IAM and traditional
IAM: in cloud IAM, the identity (IAM role) is assumed
dynamically for the task duration. An EC2 instance
"becomes" a role; a Lambda function runs "as" a role.
There are no standing credentials - just-in-time credential
issuance is built into the model.

---

### 🔩 First Principles Explanation

**The service account model for workloads:**

In all three cloud providers, workloads authenticate
via service identity - not static API keys:

- **AWS:** IAM Role assumed by EC2 instance profile,
  Lambda execution role, ECS task role, or IRSA for K8S.
  Credentials issued by EC2 metadata service / IMDS.
  Short-lived (1-12 hours max). Auto-renewed by SDK.

- **GCP:** Service Account email used as a workload's
  identity. VM instance service account. Workload
  identity for GKE. Credentials from metadata server.

- **Azure:** Managed Identity (system-assigned or
  user-assigned). Azure IMDS issues access tokens.
  No credential management needed.

All three: no long-term API key required for workloads.
Credential lifecycle is fully managed by the platform.

**Resource hierarchy and inheritance:**

- **GCP:** permissions set at org/folder/project level
  cascade to all children. Setting a role at the project
  level grants it to all resources in the project.

- **Azure:** role assignments at management group scope
  apply to all subscriptions beneath. Resource group
  scope applies to all resources in the group.

- **AWS:** no implicit hierarchy - everything is explicit.
  S3 bucket policies, KMS key policies, VPC endpoint
  policies all evaluated independently. SCPs enforce
  guardrails organization-wide.

---

### 🧪 Thought Experiment

**Five microservices, each needs different S3 access:**

```
Service A: reads from s3://logs-bucket
Service B: writes to s3://uploads-bucket
Service C: reads from s3://reports-bucket
Service D: reads from both logs and reports
Service E: full access (archive service) to all

AWS Implementation:
  role/logs-reader   -> s3:GetObject, s3://logs-bucket/*
  role/uploads-writer -> s3:PutObject, s3://uploads-bucket/*
  role/reports-reader -> s3:GetObject, s3://reports-bucket/*
  role/multi-reader  -> s3:GetObject, s3://logs-bucket/*
                        s3:GetObject, s3://reports-bucket/*
  role/archiver      -> s3:*, s3://logs-bucket/*
                        s3:*, s3://uploads-bucket/*
                        s3:*, s3://reports-bucket/*

Each service assumes its role via IRSA or instance profile.
No long-term keys anywhere.
Audit: CloudTrail shows exactly which role, which action.
```

---

### 🧠 Mental Model / Analogy

> Cloud IAM is the key card system for the entire
> cloud data center:
>
> - **IAM Principal** = person with a key card
> - **IAM Role** = the job function on the card
>   (janitor, engineer, manager)
> - **IAM Policy / Role Definition** = the access rules
>   for that job function
> - **Resource** = a door in the data center
> - **Permission** = the rule: "engineers can open
>   server room doors but not the executive office"
>
> **AWS** = building where every door has its own lock
> rules (resource policies) PLUS job-function cards
> (identity policies). Both can grant access.
>
> **GCP** = building where job functions (roles) are
> defined organization-wide and inherited by all floors.
>
> **Azure** = building with management groups > floors
> > rooms. Role assigned at a floor = access to all rooms.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Cloud IAM answers "who is allowed to do what in
our cloud environment?" for every action taken by
every engineer, automation, and service.

**Level 2 (junior developer):**
AWS: attach an IAM policy to your Lambda execution
role. GCP: grant a service account role on the
resource. Azure: assign a role to a managed identity
at the resource group scope. All three: no long-term
API keys for services.

**Level 3 (mid engineer):**
AWS multi-account: assume a cross-account role using
STS AssumeRole. The role in Account B has a trust
policy allowing Account A's role to assume it. STS
returns temporary credentials (max 12 hours).
CloudTrail in Account B records the assumed role ARN
and the session name for attribution.

**Level 4 (senior/staff):**
Organization-level guardrails:
- AWS: SCPs (Organization Service Control Policies)
  enforce account-wide maximum permissions. Use SCPs
  to deny ec2:CreateDefaultVpc, s3:PutBucketPublicAccessBlock
  override (to prevent public buckets), iam:CreateUser
  (to enforce role-only IAM in production).
- GCP: Organization Policy constraints (restrictPublicIP,
  allowedResourceRegions).
- Azure: Policy (built-in and custom) enforced at
  management group scope.

**Level 5 (distinguished):**
Cross-cloud identity federation: GitHub Actions can
authenticate to AWS, GCP, and Azure without any static
secrets using OIDC WorkLoad Identity Federation.
GitHub's IdP issues an OIDC token for the workflow;
the cloud provider is configured to trust GitHub's
JWKS endpoint and exchange the token for short-lived
cloud credentials. This is identity federation applied
to CI/CD: no secrets in GitHub Actions workflows.

---

### ⚙️ How It Works (Mechanism)

```
AWS Role Assumption Flow (IRSA - Kubernetes):

1. Kubernetes ServiceAccount annotated:
   annotations:
     eks.amazonaws.com/role-arn: arn:aws:iam::ACCT:role/my-role

2. Pod starts: EKS injects projected OIDC token
   Mounted at: /var/run/secrets/amazonaws.com/serviceaccount/token

3. AWS SDK (boto3, aws-sdk):
   aws_web_identity_token_file = /var/run/.../token
   aws_role_arn = arn:aws:iam::ACCT:role/my-role

4. SDK calls STS:
   POST https://sts.amazonaws.com/
   AssumeRoleWithWebIdentity(
     RoleArn=..., WebIdentityToken=<projected OIDC token>)
   -> Returns: AccessKeyId, SecretAccessKey, SessionToken
              Expiry: 1 hour

5. SDK calls S3 with temporary credentials
   CloudTrail: {principalId: "IRSA:pod-name",
                role: arn:...,
                sourceIP: pod-IP}

GCP Workload Identity Federation (similar):
  KSA annotated with GCP service account email
  GCP metadata server issues OAuth access token
  No key files needed on any node
```

---

### ⚖️ Comparison Table

| Feature | AWS IAM | GCP IAM | Azure RBAC |
|:---|:---|:---|:---|
| Policy format | JSON (Allow/Deny) | Role bindings {principal, role} | Role assignments {principal, role, scope} |
| Default | Deny everything | Deny everything | Deny everything |
| Workload identity | IAM Roles (instance profile, IRSA) | Service Account + Workload Identity | Managed Identity |
| Org guardrails | SCPs | Org Policy constraints | Azure Policy |
| Resource hierarchy | Flat (explicit per resource) | org > folder > project > resource | mgmt group > sub > rg > resource |
| Explicit Deny | Yes (wins always) | Via Deny policies (2022+) | Via Deny assignments |
| Audit | CloudTrail | Cloud Audit Logs | Azure Activity Log |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Managed Identity is a service account" | In Azure, a Managed Identity IS the service account equivalent. In GCP, Service Account is the managed identity equivalent. In AWS, IAM Role is the equivalent. Names differ; concept is the same. |
| "GCP permissions inherit downward" | Yes, but explicit denials also propagate. A parent-level binding grants access to all children. This is a feature but also a risk: over-broad org-level role grants ripple to all projects. |
| "AWS long-term access keys are acceptable for CI/CD" | No. GitHub Actions OIDC, GitLab CI OIDC, and CircleCI OIDC all support keyless authentication to AWS. There is no legitimate use case for long-term AWS keys in CI/CD pipelines. |
| "SCPs grant permissions" | SCPs only restrict; they cannot grant. A SCP Allow is a maximum permission ceiling; the account-level IAM policy must also explicitly Allow. |

---

### 🚨 Failure Modes & Diagnosis

**403: Access Denied in AWS despite correct role**

```bash
# Step 1: identify the policy evaluation source
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCT:role/my-role \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Step 2: check for SCP interference
aws organizations list-policies-for-target \
  --target-id $ACCOUNT_ID \
  --filter SERVICE_CONTROL_POLICY

# Step 3: check resource-based policy
aws s3api get-bucket-policy --bucket my-bucket | \
  python3 -m json.tool

# Step 4: check permission boundary
aws iam get-role --role-name my-role | \
  jq '.Role.PermissionsBoundary'
```

**IRSA token not refreshed (pod gets expired credentials)**

```bash
# Check token expiry
cat /var/run/secrets/amazonaws.com/serviceaccount/token | \
  cut -d. -f2 | base64 -d | python3 -m json.tool
# Check exp field

# AWS SDK auto-refreshes if using standard credential chain
# Verify: export AWS_DEFAULT_REGION=us-east-1
# Run: aws sts get-caller-identity
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-006` - IAM Principals: role and service account types
- `IAM-013` - Permissions and Policies

**Builds On This:**
- `IAM-022` - IAM for Microservices: IRSA/Workload Identity at scale
- `IAM-026` - Enterprise IAM Architecture: multi-cloud IAM

**Related:**
- `AWS-001` - AWS IAM in depth
- `ATZ-002` - RBAC Fundamentals

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ CLOUD IAM - WORKLOAD IDENTITY (NO STATIC KEYS)      │
├───────────────────┬──────────────────────────────────┤
│ AWS               │ IAM Role via instance profile    │
│                   │ or IRSA (EKS) or Lambda exec role│
├───────────────────┼──────────────────────────────────┤
│ GCP               │ Service Account + Workload       │
│                   │ Identity Federation (GKE)        │
├───────────────────┼──────────────────────────────────┤
│ Azure             │ Managed Identity (system or user)│
│                   │ Assigned to VM / AKS node pool   │
├───────────────────┼──────────────────────────────────┤
│ ALL THREE         │ No long-term API keys in code    │
│                   │ Credential auto-renewed by SDK   │
│                   │ CloudTrail/Audit log per call    │
└───────────────────┴──────────────────────────────────┘
```

**If you remember 3 things:**

1. All three cloud providers support keyless workload
   identity. Use it. No API keys in config files.

2. AWS is flat (explicit per resource). GCP and Azure
   have resource hierarchy with inheritance.

3. SCPs (AWS) and Org Policy (GCP) and Azure Policy
   are organization-wide guardrails. They cannot grant
   permissions; they only restrict.

**Interview one-liner:**
"Cloud IAM governs access to cloud APIs. All three major
clouds support keyless workload identity: AWS IAM roles
via instance profiles/IRSA, GCP service accounts with
workload identity, Azure managed identities. Organization-
level guardrails (SCPs/Org Policy) enforce compliance
across all accounts."

---

### 💎 Transferable Wisdom

The "assume role for task duration, return it when done"
pattern is just-in-time privilege in cloud form. It
appears in operating systems (sudo: temporarily elevate
privilege, then return to regular user), Unix setuid
binaries (a program runs with the permissions of its
owner for a specific purpose, then returns to caller's
context), and PAM tools (CyberArk: check out a credential,
use it, check it back in). The common principle: standing
privilege is the attack surface; just-in-time privilege
is the mitigation.

---

### ✅ Mastery Checklist

1. **COMPARE** Explain the key difference between AWS
   IAM policy evaluation (per-call explicit Allow/Deny
   JSON) and GCP IAM binding inheritance, and when
   each model is easier to reason about.

2. **DESIGN** A CI/CD pipeline that deploys to AWS
   without any long-term access keys. Describe the
   OIDC federation setup, the IAM role trust policy,
   and how GitHub Actions gets temporary credentials.

3. **DIAGNOSE** A Lambda gets 403 Access Denied even
   though its execution role has a DynamoDB:GetItem
   Allow policy. Walk through the five possible policy
   sources that could be causing the denial.

---

*Identity & Access Management | IAM-015 | v5.0*