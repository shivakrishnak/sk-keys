---
id: ATZ-023
title: "Service Account Permissions"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★☆
depends_on: ATZ-004, ATZ-013, ATZ-022
used_by: ATZ-040, ATZ-049, ATZ-050
related: ATZ-022, ATZ-030, ATZ-033
tags:
  - security
  - authorization
  - service-accounts
  - least-privilege
  - intermediate
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/authorization/service-account-permissions/
---

⚡ **TL;DR** - Service accounts are non-human identities for
applications, daemons, and automation. The failure mode is
permission creep: service accounts accumulate permissions over time
and are never audited. A compromised service account with admin
permissions is as dangerous as a compromised human admin - and
service accounts don't have MFA. Apply least privilege strictly:
scope per service, per environment, time-limit where possible,
rotate credentials, and audit usage regularly.

---

### 📊 Entry Metadata

| #023 | Category: Authorization | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATZ-004 Least Privilege, ATZ-013 RBAC, ATZ-022 Delegation | |
| **Used by:** | ATZ-040, ATZ-049, ATZ-050 | |
| **Related:** | ATZ-022 Delegation, ATZ-030 Externalized Auth, ATZ-033 Cross-Service | |

---

### 📘 Textbook Definition

A service account is a non-human identity used by an application,
microservice, batch job, or automation script to authenticate and
perform actions on behalf of the service (not a specific user).
Service accounts authenticate via API keys, client certificates,
or platform-managed identity (AWS IAM role, GCP service account,
Azure managed identity). Permission design for service accounts
follows the same least-privilege principle as human accounts, with
additional constraints: no interactive login, credentials must be
rotatable, permissions must be auditable, and access must be
restricted to the specific resources the service legitimately needs.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Service Account Permission Scoping             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ANTI-PATTERN: shared service account                  │
│  order-service, payment-service, reporting-service     │
│  all use: backend-service-account                      │
│  Permissions: read+write ALL databases                 │
│  Compromise: attacker pivots to all services           │
│                                                        │
│  PATTERN: per-service, scoped accounts                 │
│  order-service:    read orders-db, write orders-db     │
│                    read products-db (no write)         │
│  payment-service:  read+write payments-db              │
│                    read orders-db (no write)           │
│  reporting-service: read-only replicas ONLY            │
│                                                        │
│  PLATFORM-MANAGED IDENTITY (preferred):                │
│  AWS: IAM roles for EC2/Lambda/ECS - no long-lived key │
│  GCP: Workload Identity for GKE pods                   │
│  Azure: Managed Identity for VMs/AKS                  │
│  Benefit: credentials are ephemeral, auto-rotated,     │
│  bound to workload identity (not bearer token)         │
│                                                        │
│  AUDIT CHECKLIST:                                      │
│  □ Service account per service (not shared)            │
│  □ Permissions scoped to minimum needed resources      │
│  □ No human-accessible login for service accounts      │
│  □ Credentials rotated (or use platform-managed)       │
│  □ Last-used timestamp monitored                       │
│  □ Unused accounts disabled after 30 days of inactivity│
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - GCP Workload Identity binding (Kubernetes)**

```yaml
# kubernetes/service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service
  namespace: production
  annotations:
    # Bind Kubernetes SA to GCP SA (no static keys)
    iam.gke.io/gcp-service-account: order-service@project.iam.gserviceaccount.com
---
# GCP IAM binding (gcloud or Terraform)
# Grants only the specific permissions needed
resource "google_project_iam_member" "order_service_db" {
  project = var.project_id
  role    = "roles/cloudsql.client" # NOT roles/cloudsql.admin
  member  = "serviceAccount:order-service@project.iam.gserviceaccount.com"
}
```

**Example - AWS IAM role with least privilege for Lambda**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789:table/Orders"
    }
  ]
}
```

**Example - BAD: overpermissioned service account**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
// This is AdministratorAccess - the most common finding
// in AWS penetration tests.
// A single Lambda function should NEVER have this policy.
// Attack: XSS in web app -> SSRF to 169.254.169.254
//         -> steal Lambda's IAM credentials
//         -> admin access to all AWS resources
```

---

*Authorization category: ATZ | Entry: ATZ-023 | v5.0*