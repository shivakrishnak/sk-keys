---
layout: default
title: "IAM (Identity and Access Management)"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /cloud-aws/iam/
id: AWS-027
category: "Cloud - AWS"
difficulty: "★★☆"
depends_on: ["AWS Global Infrastructure"]
used_by: ["IAM Roles / Policies", "VPC", "EC2", "EKS", "Lambda"]
related:
  [
    "IAM Roles / Policies",
    "AWS Security Best Practices",
    "Service Account",
    "RBAC (K8s)",
  ]
tags:
  [
    aws,
    iam,
    identity,
    access-management,
    security,
    authentication,
    authorization,
    cloud,
  ]
---

# IAM (Identity and Access Management)

## ⚡ TL;DR

AWS IAM controls **who** (identity) can do **what** (actions) on **which** resources. Identities: Users, Groups, Roles, Service Accounts (via Roles). Permissions expressed as JSON policies. **Root account = emergency only**; never use for daily operations. Best practice: Roles for everything (human SSO via Identity Center, services via IAM Roles). No shared credentials.

---

## 🔥 Problem This Solves

Without IAM: everyone uses the root account, a credential leak = full account takeover, no audit trail of who did what, no way to grant temporary access. IAM provides fine-grained, auditable, least-privilege access control for every AWS resource.

---

## 📘 Textbook Definition

AWS Identity and Access Management (IAM) is a global service that enables you to manage access to AWS services and resources securely. IAM lets you create and manage AWS users, groups, and roles, and use policies to allow or deny their access to AWS resources. IAM is eventually consistent and global (not region-specific).

---

## ⏱️ 30 Seconds

```
IAM principals:
  Root:    First account; has everything; protect with MFA + never use daily
  User:    Human with long-term credentials (access key + password)
  Group:   Collection of users (e.g., Developers, Ops) - attach policies here
  Role:    Assumed identity with temporary credentials; no long-term keys

Policy types:
  Identity-based:   attached to User/Group/Role (grants permissions)
  Resource-based:   attached to resource (e.g., S3 bucket policy)
  SCP:              Organization-level guardrails (AWS Organizations)
  Permission boundary: max permissions a role can grant

Decision logic: Deny wins. Default = implicit deny. Explicit allow needed.
```

---

## 🔩 First Principles

- **Authentication** (are you who you say you are): password/access keys/MFA/federation
- **Authorization** (are you allowed): policies evaluated → allow/deny
- **Deny precedence**: explicit Deny > explicit Allow > implicit Deny (default)
- **Global**: IAM is not region-specific; one IAM entity works in all regions
- **IAM is free**: no charge for IAM itself; pay for AWS service calls
- **Temporary credentials**: always prefer roles (STS: AssumeRole → time-limited token)

---

## 🧪 Thought Experiment

A developer's access key is committed to GitHub accidentally. Without IAM hygiene: attacker uses key to create EC2 instances for crypto mining, exfiltrate S3 data, create backdoor IAM users. With good IAM: key has minimal permissions (read-only to one S3 bucket), CloudTrail alerts on the leak within minutes, key is immediately revoked, damage is limited.

---

## 🧠 Mental Model / Analogy

IAM is a **corporate security badge system**: the root account is the building's master key (keep in a safe). Users are employees with badge access. Groups are departments (Marketing = can access CRM, not server room). Roles are temporary visitor badges (contractors assume a specific role for the day, return it when done). Access is audited (CloudTrail = badge swipe logs).

---

## 📶 Gradual Depth

**Level 1 - Beginner**: Never use root account. Create IAM users for humans. Attach IAM policies via Groups. Enable MFA everywhere.

**Level 2 - Practitioner**: Use IAM Roles instead of Users for applications and services. Use AWS Identity Center (SSO) for humans → roles assumed via federation, not long-term keys. Rotate access keys regularly. Use `aws sts get-caller-identity` to know what identity you're using.

**Level 3 - Advanced**: Policy evaluation logic: SCP (org) → then Resource-based → then Identity-based → then Permission boundary → then Session policies. `aws:RequestedRegion` condition key: restrict operations to specific regions. IAM Access Analyzer: find overly permissive policies and external resource sharing. Role chaining for cross-account access.

**Level 4 - Expert**: ABAC (Attribute-Based Access Control) with tags: `aws:ResourceTag/Project` == `aws:PrincipalTag/Project` → dynamic permissions without updating policies. Service Control Policies (SCPs): guardrails for entire org units (can't delete CloudTrail, can't leave org). Permission boundaries: limit max permissions a role can have (useful for delegating IAM administration safely). IAM Conditions: `aws:SourceIp`, `aws:MultiFactorAuthPresent`, `aws:CurrentTime` for contextual authorization.

---

## ⚙️ How It Works

### IAM Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadForMyBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    },
    {
      "Sid": "DenyDeleteS3",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    }
  ]
}
```

### Least Privilege User Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Team": "${aws:PrincipalTag/Team}"
        }
      }
    }
  ]
}
```

### IAM Role for EC2 (Instance Profile)

```hcl
# Terraform: IAM role for EC2 to read from S3
resource "aws_iam_role" "app_role" {
  name = "app-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "app_s3_policy" {
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::${var.app_bucket}/*"
    }]
  })
}

resource "aws_iam_instance_profile" "app" {
  name = "app-instance-profile"
  role = aws_iam_role.app_role.name
}
```

### Cross-Account Role Assumption

```json
// Account A: Trust policy on Role
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::ACCOUNT-B-ID:root"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "Bool": { "aws:MultiFactorAuthPresent": "true" }
    }
  }]
}

// Account B user: assume the cross-account role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT-A-ID:role/CrossAccountRole \
  --role-session-name my-session
```

---

## 🔄 E2E Flow: Application Authentication to AWS

```
EKS Pod → AWS S3 (using IRSA)

1. EKS cluster has OIDC provider configured
2. Kubernetes ServiceAccount annotated with IAM Role ARN
3. Pod starts: K8s projects service account token (JWT)
4. AWS SDK in app: detects token at /var/run/secrets/...
5. SDK calls STS:AssumeRoleWithWebIdentity
6. STS validates OIDC token → returns temporary credentials (15min-1hr)
7. SDK uses temporary credentials to call S3
8. Credentials auto-refresh before expiry

Result: No access keys in code, no secrets in K8s Secrets.
        Credentials automatically rotated.
```

---

## ⚖️ Comparison Table

|                  | IAM User          | IAM Role                | Federation (Identity Center) |
| ---------------- | ----------------- | ----------------------- | ---------------------------- |
| **Credentials**  | Long-term keys    | Temporary (STS)         | Temporary (SAML/OIDC)        |
| **For**          | Legacy automation | Services, cross-account | Human users                  |
| **Key rotation** | Manual            | Automatic               | N/A                          |
| **Recommended**  | No                | Yes                     | Yes (for humans)             |
| **MFA support**  | Yes               | Can require             | Built-in                     |

---

## ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                              |
| ------------------------------------------- | ------------------------------------------------------------------------------------ |
| "Root = admin = OK for daily use"           | Root has privileges that can't be restricted; treat it like a nuclear launch code    |
| "Groups can be nested"                      | IAM Groups cannot contain other groups; only users                                   |
| "Deny isn't needed if you don't Allow"      | Correct for most cases, but explicit Deny overrides Allow grants from other policies |
| "IAM User = best practice for applications" | No - IAM Roles give temporary credentials; no long-term key to leak                  |

---

## 🚨 Failure Modes

| Failure                  | Symptom                    | Fix                                                                      |
| ------------------------ | -------------------------- | ------------------------------------------------------------------------ |
| AccessDenied errors      | App can't call AWS service | Check role has correct policy; use CloudTrail to see exact action denied |
| Credentials expired      | SDK throws expiry error    | Use roles (auto-refresh); not static keys                                |
| Policy too permissive    | Security audit flags       | Use IAM Access Analyzer; apply least privilege                           |
| Role circular dependency | Can't assume role          | Check trust policy allows the assuming entity                            |

---

## 🔗 Related Keywords

- [IAM Roles / Policies](/cloud-aws/iam-roles-policies/) - deep dive on role-based access
- [AWS Security Best Practices](/cloud-aws/aws-security-best-practices/) - IAM as part of overall posture
- [EKS](/cloud-aws/eks/) - IRSA for pod-level IAM roles
- [Lambda](/cloud-aws/lambda/) - Lambda execution roles

---

## 📌 Quick Reference Card

```bash
# Who am I?
aws sts get-caller-identity

# List users
aws iam list-users

# Simulate policy evaluation
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/developer \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/*

# Assume a role
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/MyRole \
  --role-session-name test

# List role policies
aws iam list-attached-role-policies --role-name MyRole
aws iam list-role-policies --role-name MyRole

# Find who has access to a resource (Access Analyzer)
aws accessanalyzer list-findings --analyzer-name my-analyzer

# Create access key (prefer roles!)
aws iam create-access-key --user-name my-user

# Rotate access key
aws iam update-access-key --access-key-id OLD_KEY --status Inactive
aws iam create-access-key --user-name my-user
aws iam delete-access-key --access-key-id OLD_KEY
```

---

## 🧠 Think About This

The most common IAM mistake is not over-permissioning individual actions - it's **wildcard Resource ARNs**. Policies like `"Resource": "*"` on DynamoDB actions mean the role can access every DynamoDB table in the account, not just yours. The fix is straightforward: use specific ARNs. But as systems grow, maintaining per-resource ARNs becomes operationally heavy. The elegant solution is ABAC: tag your resources and roles with matching project/environment tags, then write one policy: `allow if ResourceTag/Project == PrincipalTag/Project`. This scales to hundreds of teams without updating policies every time a new resource is created - only the resource needs the right tag.
