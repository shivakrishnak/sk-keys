---
layout: default
title: "IAM Roles  Policies"
parent: "Cloud — AWS"
nav_order: 28
permalink: /cloud-aws/iam-roles-policies/
id: AWS-028
category: "Cloud — AWS"
difficulty: "★★☆"
depends_on: ["IAM (Identity and Access Management)"]
used_by: ["EC2", "Lambda", "EKS", "ECS / Fargate", "CloudFormation"]
related:
  [
    "IAM (Identity and Access Management)",
    "AWS Security Best Practices",
    "EKS",
    "Lambda",
  ]
tags:
  [
    aws,
    iam,
    roles,
    policies,
    sts,
    assume-role,
    least-privilege,
    security,
    cloud,
  ]
---

# IAM Roles / Policies

## ⚡ TL;DR

**IAM Role**: assumable identity with temporary credentials (via STS). No username/password. Anyone/anything with permission can AssumeRole. **IAM Policy**: JSON document defining allowed/denied actions on resources. Attach policies to roles (or users/groups). Best practice: roles for everything; least-privilege policies with specific resources and conditions.

---

## 🔥 Problem This Solves

Long-term access keys (IAM User credentials) stored in apps = credential leak risk. Roles solve this: temporary credentials rotated automatically, scoped to minimum needed, auditable via CloudTrail, revocable immediately. Policies define exactly what a role can do — least privilege without managing individual user permissions.

---

## 📘 Textbook Definition

An **IAM Role** is an identity with specific permissions that can be assumed by AWS services, users from other accounts, or federated identities. It has no long-term credentials; instead, STS issues short-lived tokens. An **IAM Policy** is a JSON document that defines permissions (Allow/Deny) for specific actions on specific resources with optional conditions.

---

## ⏱️ 30 Seconds

```
Role trust policy:  WHO can assume this role
  "Principal": {"Service": "lambda.amazonaws.com"}  → Lambda can assume
  "Principal": {"AWS": "arn:aws:iam::ACCOUNT:role/X"} → role X can assume

Role permissions policy: WHAT this role can do
  "Action": "s3:GetObject"
  "Resource": "arn:aws:s3:::my-bucket/*"

STS: AssumeRole returns:
  AccessKeyId (temporary)
  SecretAccessKey (temporary)
  SessionToken
  Expiration (15min → 12hr, default 1hr)
```

---

## 🔩 First Principles

- **Two-policy model**: trust policy (who can assume) + permissions policy (what they can do)
- **STS tokens**: temporary credentials; automatically refreshed by AWS SDKs
- **Policy evaluation order**: SCP → Resource-based → Permissions boundary → Identity-based → Session policy
- **Managed vs inline**: AWS Managed (AWS maintains), Customer Managed (you maintain), Inline (embedded in user/role — not reusable)
- **ARN structure**: `arn:aws:iam::123456789012:role/my-role`

---

## 🧪 Thought Experiment

A Lambda function needs to read from DynamoDB and publish to SQS. Without roles: store access keys in environment variables → leaked in logs, hard to rotate. With roles: Lambda execution role with exactly `dynamodb:GetItem` on one table + `sqs:SendMessage` on one queue → no credentials to leak, auto-rotated, CloudTrail logs every action.

---

## 🧠 Mental Model / Analogy

IAM Role = a **costume** you can put on temporarily. The costume (role) has specific capabilities (policies). A detective (Lambda) wears the detective costume (role) — it can interrogate witnesses (DynamoDB) but not make arrests (delete items). When the detective's shift ends, they take off the costume (credentials expire). Anyone can wear the costume if they're authorized (trust policy).

---

## 📶 Gradual Depth

**Level 1 — Beginner**: Create a role for each service (Lambda role, EC2 role). Attach AWS Managed Policies to start (e.g., `AmazonS3ReadOnlyAccess`). Never hardcode credentials.

**Level 2 — Practitioner**: Use Customer Managed Policies with specific ARNs instead of wildcards. Separate roles per application, per environment. Use `aws:RequestedRegion` conditions. Instance profiles for EC2; execution roles for Lambda; task roles for ECS.

**Level 3 — Advanced**: Cross-account role assumption: Account A role trusted by Account B. Permission boundaries: limit max permissions delegate can grant. Role session tags: pass business context (project, cost-center) into session for ABAC policies. External ID in trust policy prevents confused deputy attack.

**Level 4 — Expert**: ABAC with PrincipalTag: `Condition: {"StringEquals": {"aws:ResourceTag/Project": "${aws:PrincipalTag/Project}"}}` — role can only access resources tagged with its own project. Service-linked roles: AWS creates automatically for specific services (cannot edit trust policy). Roles Anywhere: use X.509 certificates from on-prem PKI to assume IAM roles (extends roles beyond AWS environment). Identity Center: manage permission sets (role templates) centrally, provisioned to member accounts automatically.

---

## ⚙️ How It Works

### Complete Role + Policy Example (Terraform)

```hcl
# Lambda function role with least-privilege policy
resource "aws_iam_role" "lambda_processor" {
  name = "payment-processor-lambda"

  # Trust policy: who can assume
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Permissions policy: what this role can do
resource "aws_iam_role_policy" "lambda_processor" {
  role = aws_iam_role.lambda_processor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBRead"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = [
          "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/payments",
          "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/payments/index/*"
        ]
      },
      {
        Sid    = "SQSSend"
        Effect = "Allow"
        Action = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.payment_events.arn
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:us-east-1:*:log-group:/aws/lambda/payment-processor:*"
      }
    ]
  })
}
```

### Cross-Account Role Assumption

```json
// In Account A (target): trust policy on role
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::ACCOUNT_B_ID:role/cicd-role"
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "unique-secret-id-12345"  // prevents confused deputy
      }
    }
  }]
}

// In Account B: permission for cicd-role to assume Account A role
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::ACCOUNT_A_ID:role/deploy-role"
}
```

### Permission Boundary (Limiting Delegate IAM Admin)

```json
// Permission boundary: developer can create roles,
// but those roles can't exceed these permissions
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "dynamodb:*",
        "lambda:*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser",
        "iam:DeleteRole",
        "organizations:*"
      ],
      "Resource": "*"
    }
  ]
}

// Attach as boundary when creating role:
aws iam create-role \
  --role-name developer-created-role \
  --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary
```

### ABAC Policy Example

```json
// Role can manage EC2 instances tagged with matching Team
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Team": "${aws:PrincipalTag/Team}",
          "ec2:ResourceTag/Environment": "${aws:PrincipalTag/Environment}"
        }
      }
    }
  ]
}
// Role tagged: Team=payments, Environment=prod
// → Can only manage EC2 instances tagged Team=payments + Environment=prod
```

---

## 🔄 E2E Flow: ECS Task IAM Role

```
1. Create task IAM role:
   - Trust policy: ecs-tasks.amazonaws.com
   - Permissions: DynamoDB:GetItem on payments table

2. ECS Task Definition references role ARN:
   "taskRoleArn": "arn:aws:iam::123:role/payment-task-role"

3. Task starts:
   - ECS Agent contacts Task Metadata Service
   - Container gets credentials via:
     curl http://169.254.170.2/v2/credentials/<id>

4. App uses AWS SDK (auto-discovers credentials from metadata)

5. SDK call: dynamodb.getItem(...)
   → Signs request with temporary credentials
   → DynamoDB validates signature
   → CloudTrail: "who: payment-task-role, action: GetItem, table: payments"

6. Credentials expire: SDK auto-refreshes via metadata endpoint
```

---

## ⚖️ Comparison Table

| Policy Type         | Attached To           | Managed By     | Use Case                               |
| ------------------- | --------------------- | -------------- | -------------------------------------- |
| AWS Managed         | User/Role/Group       | AWS            | Standard permissions (ReadOnly, Admin) |
| Customer Managed    | User/Role/Group       | You            | Custom least-privilege                 |
| Inline              | Specific User/Role    | You (embedded) | One-off, not reusable                  |
| Resource-based      | Resource (S3, SQS...) | You            | Cross-account access                   |
| SCP                 | Org/OU                | Org Admin      | Guardrails across accounts             |
| Permission Boundary | User/Role             | You            | Limit delegate IAM admins              |

---

## ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                            |
| ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| "IAM roles require an IAM user to assume them" | Roles can be assumed by AWS services, federated users, and users in other accounts |
| "More policies = more permissions"             | Policies are additive for Allow but one Deny overrides all Allows                  |
| "Trust policy = permissions policy"            | Trust policy = who can assume; permissions policy = what they can do               |
| "AWS Managed Policies are least privilege"     | AWS Managed Policies are broad by design; always prefer narrower Customer Managed  |

---

## 🔗 Related Keywords

- [IAM (Identity and Access Management)](/cloud-aws/iam/) — IAM overview and concepts
- [Lambda](/cloud-aws/lambda/) — execution roles for serverless functions
- [EKS](/cloud-aws/eks/) — IRSA for pod-level role assumption
- [AWS Security Best Practices](/cloud-aws/aws-security-best-practices/) — roles in security posture

---

## 📌 Quick Reference Card

```bash
# Create role
aws iam create-role \
  --role-name MyRole \
  --assume-role-policy-document file://trust-policy.json

# Attach managed policy
aws iam attach-role-policy \
  --role-name MyRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create custom policy
aws iam create-policy \
  --policy-name MyCustomPolicy \
  --policy-document file://policy.json

# Simulate policy
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/MyRole \
  --action-names s3:PutObject \
  --resource-arns arn:aws:s3:::my-bucket/mykey

# Assume role (returns temporary credentials)
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/MyRole \
  --role-session-name test-session

# List all policies attached to a role
aws iam list-attached-role-policies --role-name MyRole
aws iam list-role-policies --role-name MyRole  # inline only
```

---

## 🧠 Think About This

The "confused deputy" attack is a subtle IAM vulnerability worth understanding: a malicious user tricks a trusted service into performing actions on their behalf using the service's permissions. Example: attacker sets up a CloudFormation stack with a template that creates an IAM role trusting your cross-account assume-role service. Solution: always use `sts:ExternalId` in cross-account trust policies — this is an out-of-band shared secret that the assuming principal must know and present. AWS partners who assume roles in customer accounts must use ExternalId to prevent confused deputy. The ExternalId should be unique per customer/relationship and difficult to guess (UUID).
