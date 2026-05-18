---
id: IAM-006
title: "IAM Principals - Users, Groups, Roles, Service Accounts"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-001, IAM-002
used_by: IAM-007, IAM-012, IAM-013
related: IAM-002, IAM-003, ATZ-002
tags:
  - iam
  - security
  - identity
  - foundational
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 6
permalink: /technical-mastery/iam/iam-principals-users-groups-roles-service-accounts/
---

⚡ TL;DR - An IAM principal is any entity that can be
authenticated and authorized. The four principal types are:
users (humans), groups (collections for bulk policy),
roles (permission sets to be assumed, not assigned), and
service accounts (non-human identities for machines and
workloads). Each has different lifecycle requirements,
credential types, and security implications.

---

### 🔥 The Problem This Solves

A team deploys a new microservice and needs it to read from
an S3 bucket. They do the wrong thing: create a user called
"service-account-payments" with a username and password,
store the credentials in config, and hardcode them in the
deployment. Now:

- The credentials never rotate (too complex to update)
- They are exposed in plaintext config files
- If the team member who created them leaves, the account
  is an orphan nobody owns
- Audit logs show "service-account-payments" doing things,
  but that name maps to a dozen different services

The correct solution is a service account or IAM role
assumed by the service. Understanding principal types
prevents the most common IAM anti-patterns.

---

### 📘 Textbook Definition

An **IAM principal** is any identity that can authenticate
to a system and be granted or denied access to resources.

**User:** A human principal with personal credentials
(password, MFA, biometric). Lifecycle tied to employment.
Example: alice@company.com in Okta or Azure AD.

**Group:** A named collection of users. Policies attached
to a group apply to all members. Groups do not authenticate
directly - they are a mechanism for bulk policy assignment.
Example: "finance-team" group; all members inherit the
finance read-access policy.

**Role (IAM model):** A named set of permissions that can
be assumed by a principal, not permanently assigned to one.
AWS IAM roles: an EC2 instance assumes a role to get
temporary credentials. GCP service accounts are analogous.
A role is like a hat: different principals put it on for
different tasks.

**Role (RBAC model):** In RBAC, a role is a job function
label assigned to a user ("editor", "admin") that maps
to a set of permissions. Different from the IAM "assume
role" model.

**Service Account:** A non-human identity for applications,
scripts, and automation. Created specifically for machine-
to-machine access. Credentials are not typed by a human
- they are issued programmatically and rotated by the
platform. Example: Kubernetes service account, GCP service
account, AWS IAM role for EC2 instance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Users are people, groups are collections of people,
roles are collections of permissions (or temporary
permission hats), service accounts are machine identities.

**One analogy:**
> At a film studio:
> - **User:** a named employee with a badge (Alice, Bob)
> - **Group:** "Props Department" - everyone in it gets
>   access to the props store automatically
> - **Role (IAM):** "Director on Set" - a temporary hat
>   that grants elevated access during a shoot; taken
>   off when the shoot ends
> - **Service Account:** the security camera system - it
>   has its own credentials and accesses video storage
>   without being any particular person

---

### 🔩 First Principles Explanation

**Why roles are better than long-term user credentials
for service access:**

A user's credentials persist indefinitely unless revoked.
A role assumption generates time-limited credentials
(AWS STS: 1-12 hour max). If credentials leak:

- Long-term key: attacker has indefinite access until
  detected and manually rotated
- STS session token: expires within hours automatically

**Why groups exist:**

Managing 500 users individually is O(users * apps).
Groups make it O(groups + users-in-groups). When a new
SaaS app is added, grant access to the "finance" group
once instead of individually managing 200 finance users.
When an employee moves teams, change one group membership.

**Why service accounts must not be shared:**

One service account shared by multiple services makes
audit logs unactionable: "service-account-infra did a
DeleteObject" - which of the six services using that
account did it? One service account per service enables
precise attribution and per-service permission scoping.

---

### 🧪 Thought Experiment

**Scenario:** Three teams need S3 access.
- Team A reads from bucket-reports
- Team B writes to bucket-uploads
- Team C reads from both

**Wrong approach:**
Create user "s3-access-user" with full S3 access, share
credentials across all three teams.
Problems: over-privileged, no attribution, credential
sharing, impossible to rotate without coordinating
three teams.

**Right approach:**
```
# IAM roles (AWS) - no long-term credentials
role/reports-reader    -> s3:GetObject on bucket-reports
role/uploads-writer    -> s3:PutObject on bucket-uploads

# Service A assumes reports-reader role via instance profile
# Service B assumes uploads-writer role via instance profile
# Service C assumes both roles via role chaining

# Audit log: "role/reports-reader (EC2 instance i-abc) GetObject"
# Precise attribution, time-limited credentials, no sharing
```

**The insight:** Roles are assumed, not assigned. Time-
limited credential issuance is built into the model.

---

### 🧠 Mental Model / Analogy

> **Users** = people with permanent employee badges.
> **Groups** = departments printed on the badge holder.
> **Roles (IAM)** = visitor lanyards: anyone can pick
>   one up, wear it, and return it when done. The lanyard
>   grants specific access while worn; no one person
>   permanently "has" the lanyard.
> **Service Accounts** = robot worker IDs: the assembly
>   robot has its own badge for the door it needs to
>   open. Not a person. Not shared. Purpose-built.

**The critical distinction between role types:**

- **RBAC role** (Okta group / database role): assigned
  to users as a label. "Alice is an admin."

- **IAM assume-role** (AWS IAM role): a temporary hat.
  "EC2 instance wears the role for 1 hour, then the
  credentials expire."

Both are called "role" - understand which model is in
use for any given system.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Four types of things can log in to systems: people,
groups of people, services (programs), and temporary
permission sets. Each type has different rules.

**Level 2 (junior developer):**
Users have personal credentials. Groups let you set
permissions once for many users. Service accounts give
your app a credential so it can call APIs without using
anyone's personal account.

**Level 3 (mid engineer):**
AWS IAM roles are the preferred model for service
identity: no long-term keys, assume role returns
temporary STS credentials (max 12 hours), automatically
renewed by the SDK. Kubernetes uses service accounts
to mount projected tokens into pods via IRSA (IAM
Roles for Service Accounts) - the pod gets a signed
JWT it exchanges for AWS STS credentials.

**Level 4 (senior/staff):**
SPIFFE (Secure Production Identity Framework for
Everyone) standardizes service identity across
platforms using X.509 SVIDs (SPIFFE Verifiable Identity
Document). A microservice's identity is its SPIFFE ID
(spiffe://cluster.example.com/ns/payments/sa/payments-svc).
This identity travels in mTLS certificates, not API
keys. SPIRE (SPIFFE Runtime Environment) is the
reference implementation.

**Level 5 (distinguished):**
At large scale, service identity becomes a distributed
key management problem. SPIFFE/SPIRE issues short-lived
X.509 certificates (default 1 hour) that must be
renewed before expiry by all running workloads. The
renewal must be automatic, observable, and robust
to temporary SPIRE unavailability (cached certs
continue to work until expiry). This is the production
service identity problem: not just what identity to use,
but how to deliver, rotate, and revoke it at scale
across thousands of workloads.

---

### ⚙️ How It Works (Mechanism)

```
AWS IAM Role Assumption (service account equivalent):

EC2 instance starts:
  Instance profile -> attached IAM role (reports-reader)
  EC2 metadata service: GET http://169.254.169.254/...
    Returns: {AccessKeyId, SecretAccessKey, Token, Expiry}
  Expiry: ~1 hour; SDK auto-renews before expiry

Application calls S3:
  SDK uses temporary credentials from metadata service
  No hardcoded keys anywhere
  Audit: CloudTrail logs {role: reports-reader,
                          instance: i-abc123, action: GetObject}

Role assumption by a human (cross-account):
  aws sts assume-role \
    --role-arn arn:aws:iam::PROD_ACCOUNT:role/ReadOnly \
    --role-session-name alice-debug
  Returns: temporary credentials (1 hour)
  Use case: Alice (dev account) temporarily reads prod

Kubernetes service account -> AWS role (IRSA):
  Pod ServiceAccount annotated with role ARN
  Pod gets projected OIDC token (short-lived JWT)
  AWS STS validates token, returns credentials
  No node-level credentials shared across pods
```

---

### ⚖️ Comparison Table

| Principal Type | Credentials | Lifecycle | Best For | Anti-Pattern |
|:---|:---|:---|:---|:---|
| User | Password + MFA | HR-driven (JML) | Human access | Sharing user credentials |
| Group | None (collection) | Policy assignments | Bulk permission management | Using groups as roles |
| Role (RBAC) | Via user assignment | HR-driven | Job function access | Over-privileged "super-admin" role |
| Role (IAM assume) | Temporary (STS) | Request-scoped | Service/cross-account access | Long-lived role sessions |
| Service Account | Cert / token (rotated) | Service lifecycle | Automated/machine access | Shared service accounts |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Service account" and "IAM role" are the same | In AWS, an IAM role is assumed to get temporary credentials; in GCP, a service account IS the principal. Both achieve machine identity; different model. |
| Groups can authenticate | Groups cannot log in. Only users and service accounts authenticate. Groups are policy binding mechanisms, not principals. |
| One service account for all microservices is efficient | Shared service accounts eliminate per-service attribution in audit logs and over-privilege all services. One service account per service is the correct model. |
| Roles in RBAC and roles in AWS IAM are the same thing | RBAC roles are labels assigned to users. AWS IAM roles are temporary permission sets that are assumed. The word "role" covers two different concepts. |

---

### 🚨 Failure Modes & Diagnosis

**Hardcoded service credentials (IAM user key in config)**

**Symptom:** Long-term AWS access key in application
config or environment variables. Key is 3 years old.

**Root Cause:** Developer used an IAM user with long-term
credentials instead of an IAM role.

**Diagnosis:**
```bash
# Find hardcoded AWS keys in codebase (never commit these)
git secrets --scan  # or trufflehog for full history scan
grep -r "AKIA\|ASIA" --include="*.env" --include="*.conf" .

# AWS: audit IAM users with long-term access keys
aws iam list-users --query 'Users[*].UserName' | \
  xargs -I{} aws iam list-access-keys --user-name {}

# Check key age - any key > 90 days is a risk
aws iam get-credential-report --output text | \
  base64 -d | grep -v "N/A" | \
  awk -F, '$10 > 90 {print $1, $10}'
```

**Fix:** Replace IAM user credentials with IAM role
assumption (EC2 instance profile, Lambda execution role,
ECS task role, IRSA for Kubernetes).

---

**Overly broad group policy (permission creep)**

**Symptom:** "Engineering" group has admin access to
production. This was granted temporarily 18 months ago
for an incident and never revoked.

**Diagnosis:**
```bash
# AWS: list all policies attached to a group
aws iam list-attached-group-policies \
  --group-name engineering

# Check for admin policies
aws iam list-attached-group-policies \
  --group-name engineering \
  --query 'AttachedPolicies[?PolicyName==`AdministratorAccess`]'
```

**Fix:** Implement time-boxed role assumption for
emergency access. Remove permanent admin from groups.
Use AWS Access Analyzer to find overly permissive
group policies.

---

### 🔗 Related Keywords

**Prerequisites:**

- `IAM-001` - The Identity Problem
- `IAM-002` - What IAM Actually Manages

**Builds On This:**

- `IAM-007` - Identity Lifecycle Management: principal lifecycle
- `IAM-012` - Principle of Least Privilege: applied to principals
- `IAM-013` - Permissions and Policies: policy attachment to principals

**Related:**

- `ATZ-002` - RBAC Fundamentals: role-based model in depth
- `IAM-022` - IAM for Microservices: service account patterns at scale

---

### 📌 Quick Reference Card

```
┌───────────────────────────────────────────────────────┐
│ FOUR IAM PRINCIPAL TYPES                              │
├─────────────────┬─────────────────────────────────────┤
│ USER            │ Human principal                     │
│                 │ Credentials: password + MFA         │
│                 │ Lifecycle: JML (join/move/leave)    │
├─────────────────┼─────────────────────────────────────┤
│ GROUP           │ Collection of users                 │
│                 │ Does NOT authenticate               │
│                 │ For bulk policy assignment          │
├─────────────────┼─────────────────────────────────────┤
│ ROLE            │ Permission set (RBAC) or            │
│                 │ assumed permission hat (IAM)        │
│                 │ IAM roles: temporary credentials    │
├─────────────────┼─────────────────────────────────────┤
│ SERVICE ACCOUNT │ Machine/workload identity           │
│                 │ Credentials: cert / projected token │
│                 │ One per service, not shared         │
└─────────────────┴─────────────────────────────────────┘

RULE: Never use IAM user long-term keys for services.
Use IAM roles with assumed temporary credentials.
```

**If you remember 3 things:**

1. Service accounts are for machines. Never use a
   human user account for automated processes.

2. Groups do not authenticate. They are policy binding
   mechanisms only.

3. IAM roles (AWS model) generate temporary credentials.
   Prefer them over long-term keys for all service access.

**Interview one-liner:**
"Four IAM principal types: users (humans), groups
(bulk policy), roles (temporary permission assumption),
service accounts (machine identity). The critical rule:
one service account per service, no shared credentials."

---

### 💎 Transferable Wisdom

**Reusable Principle:**
Any system where multiple entities need different access
needs a principal type for each category. Kubernetes has
the same four types: User (human kubectl access), Group
(cluster role bindings to groups), Role/ClusterRole
(permission sets), ServiceAccount (pod identity). Linux
has: UID (user), GID (group), no IAM-style roles,
and system accounts for services. The category names
differ; the design pattern is identical.

**Where else this appears:**

- Database access: user (DBA), role (read-only analyst),
  service account (application DB user). Same principal
  taxonomy, same rules (no shared credentials).

- Kubernetes RBAC: ServiceAccount binds to Role or
  ClusterRole via RoleBinding. Direct analog of IAM
  role assumption for pod identity.

---

### 💡 The Surprising Truth

The most exploited principal type in cloud breaches is
the IAM user with long-term access keys - not because
IAM users are insecure by design, but because developers
creating service credentials take the path of least
resistance and create an IAM user with a 10-year key
that "just works." AWS documented that over 90% of
exposed cloud credentials on GitHub are IAM user access
keys. The technical solution (IAM roles with temporary
credentials) has existed since 2012 in AWS. The gap
is not technical knowledge - it is the absence of
enforcement policies (IAM Service Control Policies)
that block long-term key creation for services.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**

1. **EXPLAIN** The difference between assuming an IAM
   role (AWS model) and having an RBAC role assigned
   (Okta model), and why the IAM assume model is
   preferred for service-to-service access.

2. **DESIGN** A microservices architecture with five
   services that all need different S3 access. Describe
   the IAM principals, their types, and how credentials
   are issued to each service without long-term keys.

3. **AUDIT** Given a list of IAM users in an AWS account,
   identify which ones should be service accounts
   (and converted to IAM roles) versus legitimate
   human user accounts.

---

*Identity & Access Management | IAM-006 | v5.0*