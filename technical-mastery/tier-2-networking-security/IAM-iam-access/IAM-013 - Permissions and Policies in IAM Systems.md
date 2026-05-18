---
id: IAM-013
title: "Permissions and Policies in IAM Systems"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-006, IAM-012
used_by: IAM-015, IAM-019, IAM-025
related: IAM-012, ATZ-002, ATZ-003
tags:
  - iam
  - security
  - identity
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/iam/permissions-and-policies-in-iam-systems/
---

⚡ TL;DR - Permissions specify what actions a principal
can take on which resources. Policies are the containers
that group permissions and attach them to principals or
resources. Different IAM systems use different policy
languages: AWS IAM uses JSON policies with Allow/Deny
and condition keys; GCP uses IAM bindings with predefined
roles; Azure uses RBAC role assignments with JSON role
definitions. The critical pattern across all: explicit
Deny always overrides Allow.

---

### 🔥 The Problem This Solves

Without a formal permission model, access control is
implemented as scattered `if` statements across application
code: `if user.role == "admin" && user.department == "IT"`.
This approach is:

- Non-auditable: permissions live in code, not in a
  central repository
- Non-delegatable: granting access requires a code
  deployment
- Non-reviewable: "who has access to delete users?"
  requires code analysis across the entire codebase
- Fragile: refactoring breaks permission logic silently

IAM policy systems externalize permissions from code
into a managed, queryable, auditable policy store.

---

### 📘 Textbook Definition

**Permission:** A single authorization unit specifying
that a principal may (or may not) perform an action on
a resource. Example: `s3:GetObject on bucket-reports/*`.

**Policy:** A document that groups one or more permissions
and attaches them to principals (identity-based policies)
or resources (resource-based policies). Policies are
the unit of IAM management.

**AWS IAM policy model:**
- Effect: Allow or Deny
- Action: specific AWS API operations (s3:GetObject)
- Resource: specific ARNs (or wildcard)
- Condition: contextual constraints (MfaPresent=true)
- Explicit Deny overrides any Allow
- No explicit Allow = implicit deny (default-deny)

**GCP IAM model:**
- Predefined roles (curated sets of permissions)
- Resource hierarchy: org > folder > project > resource
- IAM binding: {principal, role} attached at any level
- Inheritance: permissions at higher levels apply to lower

**Azure RBAC model:**
- Role definition: set of allowed operations
- Role assignment: {principal, role, scope}
- Scope: management group > subscription > resource group > resource
- Explicit deny assignments override role assignments

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Permissions say "who can do what on which resource."
Policies group permissions and attach them to identities.
Every IAM system uses some variant of this model.

**One analogy:**
> Permission = a line in a keycard rule book:
> "Badge #1234 can open Server Room B between 9am-5pm."
>
> Policy = the whole rule book for a role:
> "On-call engineers: Server Room A (24/7),
>  Server Room B (business hours), not Server Room C."
>
> Attaching a policy to a user = giving them that
> rule book. The badge reader enforces it.

**One insight:**
The most important rule in IAM policy evaluation:
explicit Deny always wins. If any policy explicitly
denies an action, it is denied regardless of how many
other policies allow it. This enables safe "block
by exception" models: default allow for broad roles
with explicit denies for specific sensitive resources.

---

### 🔩 First Principles Explanation

**The policy evaluation algorithm:**

All IAM systems use a variant of the same evaluation:

```
1. Collect all applicable policies for this request
   (identity-based + resource-based + session policies)
2. IF any policy has explicit Deny -> DENY (stop)
3. IF any policy has explicit Allow -> ALLOW
4. Default: DENY (implicit deny)
```

Default-deny is a security invariant: a new principal
with no policies attached can do nothing. Every
permission must be explicitly granted. This is correct
security posture - you start with nothing and add.

**Identity-based vs resource-based policies:**

- Identity-based: attached to a principal. "Alice can
  do X." Evaluated for any resource Alice touches.
- Resource-based: attached to a resource (S3 bucket
  policy, KMS key policy). "This resource allows
  role/payments-svc." Evaluated for any principal
  accessing the resource.
- Effective permission = intersection: identity policy
  AND resource policy must both allow (for cross-account).
  Within same account: either identity OR resource policy
  can allow.

**Conditions add context-dependent control:**

Conditions make permissions conditional on context:
- Only allow from specific IP ranges (network trust)
- Only allow when MFA is present (authentication strength)
- Only allow during business hours (time-based control)
- Only allow for specific resource tags (data classification)

---

### 🧪 Thought Experiment

**Scenario: allow read-only access to S3 except
sensitive data, regardless of user roles.**

**Without conditions:**
```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::company-data/*"
}
```
Every user with this policy can read ALL data including
"sensitive/" prefix files.

**With resource-based policy on the sensitive prefix:**
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::company-data/sensitive/*",
  "Condition": {
    "StringNotEquals": {
      "aws:PrincipalTag/DataClassification": "Confidential"
    }
  }
}
```
Explicit Deny on sensitive/* for anyone without the
DataClassification=Confidential tag. Override wins
regardless of identity-based Allow policies.

The lesson: resource-based denies are the correct
mechanism for protecting sensitive data across all
principals - you do not need to modify every identity
policy.

---

### 🧠 Mental Model / Analogy

> IAM policy evaluation is a legal court system:
>
> - **Explicit Deny** = court order. Cannot be overridden
>   by any other rule. "This person is restrained from
>   accessing this resource" wins over any permission.
>
> - **Explicit Allow** = license or permit. "This
>   person is authorized to do this."
>
> - **Implicit Deny (default)** = no permit issued.
>   "We have no record of authorization; access denied."
>
> - **Policy** = the legal code: the collection of
>   rules that a judge (policy engine) applies to
>   decide the case.
>
> Multiple conflicting rules? The court order (Deny)
> wins. Always.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Permissions say "you are allowed to do X." Policies
group these allowances. The rule: if anything says
"NO," the answer is NO regardless of all the "YES"
rules.

**Level 2 (junior developer):**
Write IAM policies with the minimum required actions
and specific resource ARNs. Test with the AWS IAM
Policy Simulator. Remember: deny beats allow. Resource-
based bucket policies can grant access that identity
policies did not.

**Level 3 (mid engineer):**
Policy types in AWS: managed policies (reusable,
attached to multiple identities), inline policies
(embedded in one identity, one-to-one relationship).
Use managed policies for standard roles; inline for
identity-specific exceptions. Permission boundaries
set the maximum permissions ceiling; effective
permissions = identity policy ∩ boundary.

**Level 4 (senior/staff):**
Service Control Policies (SCPs) in AWS Organizations
apply at the organization/OU level and are evaluated
before any account-level policy. An SCP Deny cannot
be overridden by any account-level Allow. SCPs enforce
organization-wide guardrails (no IAM users with long-
term keys in production accounts, no public S3 buckets
in any account, all resources must be in approved regions).

**Level 5 (distinguished):**
Policy evaluation at scale introduces performance
considerations. AWS IAM evaluates all applicable policies
synchronously per API call. At 1M requests/second across
a large AWS organization, policy evaluation is a hot
path. AWS evaluates policies locally at each service
(not via a central policy service) using cached policy
data. Custom policy engines (OPA) must be deployed as
sidecars or local processes to achieve sub-millisecond
evaluation. The policy data consistency vs evaluation
latency trade-off is the same as the JWT revocation
trade-off: cache policy for performance; accept
propagation delay for updates.

---

### ⚙️ How It Works (Mechanism)

```
AWS IAM Policy Evaluation Logic:

Request: {principal: alice, action: s3:GetObject,
          resource: arn:aws:s3:::bucket/file.txt}

Step 1: Collect all policies
  - Identity policies attached to alice's user/groups/roles
  - Resource-based policies on the S3 bucket
  - Session policies (if assuming a role)
  - Permission boundaries (if set)
  - SCPs (if in an AWS Organization)

Step 2: Is there an explicit Deny?
  Check ALL policy types for explicit Deny on this action+resource
  IF YES -> DENY (evaluation stops)

Step 3: Is there an explicit Allow?
  Check identity-based + resource-based policies
  For same-account: either Allow -> ALLOW
  For cross-account: BOTH must Allow -> ALLOW

Step 4: Default -> DENY

AWS Policy JSON structure:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReportsBucketRead",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::reports-bucket",
        "arn:aws:s3:::reports-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

---

### ⚖️ Comparison Table

| IAM System | Policy Language | Deny Behavior | Resource Policy |
|:---|:---|:---|:---|
| AWS IAM | JSON (Effect, Action, Resource, Condition) | Explicit Deny wins always; SCP Deny wins over account | Yes (bucket, KMS, role trust) |
| GCP IAM | Binding {principal, role} | Deny policies (newer feature); no implicit cross-resource | Limited (resource-level bindings) |
| Azure RBAC | Role definition JSON + role assignment | Deny assignments override role assignments | Via ABAC conditions on assignments |
| Kubernetes RBAC | YAML Rule {verbs, resources} | Default deny; no explicit deny rule (only Allow) | ClusterRole vs Role scoping |
| OPA/Rego | Policy-as-code | Default deny; custom logic | Full policy language |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Two Allow policies combine to give more access" | Policies are OR'd for Allow: either policy granting allows. But an Explicit Deny from any policy overrides all Allows. |
| "Resource policies are optional" | For cross-account access in AWS, both identity AND resource policies must allow the action. Identity-only Allow is insufficient cross-account. |
| "Permission boundaries restrict what you can access" | Permission boundaries restrict the maximum permissions an identity can have, not the resources it can access directly. They are guardrails, not fine-grained access control. |
| "SCPs grant permissions" | SCPs only deny; they cannot grant permissions. They restrict the maximum permissions available in an AWS account, not grant additional ones. |

---

### 🚨 Failure Modes & Diagnosis

**403 Access Denied despite correct Allow policy**

```bash
# AWS: simulate a policy for specific action/resource
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:role/my-role \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Output: AllowedOrExplicitDeny or implicitDeny
# Look for: EvalDecision, MatchedStatements, MissingContextValues

# Check for SCP interference:
aws organizations list-policies-for-target \
  --target-id ACCOUNT_ID \
  --filter SERVICE_CONTROL_POLICY

# Check resource-based policy:
aws s3api get-bucket-policy --bucket my-bucket
```

**Fix:** Use IAM Policy Simulator to identify which
policy layer is blocking. SCPs are often the invisible
deny source in organization accounts.

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-006` - IAM Principals: who the policies apply to
- `IAM-012` - Principle of Least Privilege

**Builds On This:**
- `IAM-015` - Cloud IAM: AWS/GCP/Azure policy implementations
- `IAM-019` - IGA: policy lifecycle management
- `IAM-025` - Role-Based Access in IAM Systems Overview

**Related:**
- `ATZ-002` - RBAC Fundamentals
- `ATZ-003` - ABAC: attribute-based policies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ POLICY EVALUATION RULES                              │
├───────────────────────────────────────────────────── ┤
│ Priority 1: Explicit Deny -> DENY (always wins)      │
│ Priority 2: Explicit Allow -> ALLOW                  │
│ Priority 3: No Allow -> DENY (implicit default)      │
├──────────────────────────────────────────────────────┤
│ AWS: SCP Deny > account policy > resource policy     │
│ GCP: Parent role bindings inherited by children      │
│ Azure: Deny assignment > role assignment             │
├──────────────────────────────────────────────────────┤
│ Cross-account AWS: identity AND resource must Allow  │
│ Same-account AWS: identity OR resource may Allow     │
└──────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"Permissions specify allowed actions on resources;
policies group and attach them. Evaluation rule: explicit
Deny overrides all Allows; no Allow = implicit Deny.
In AWS, SCPs restrict maximum account permissions;
they cannot grant."

---

### 💎 Transferable Wisdom

The deny-beats-allow pattern is a security invariant
that appears whenever multiple overlapping permission
systems coexist. Linux file permissions: if group
write is denied for a file, individual user execute
allowance does not override it. Firewall rules: a
deny rule with lower priority number (higher precedence)
blocks traffic regardless of allow rules. The universal
principle: when in doubt, the restriction wins over
the permission.

---

### ✅ Mastery Checklist

1. **WRITE** An AWS IAM policy that allows EC2 instances
   to read from a specific S3 bucket only when MFA is
   present and the source IP is in the corporate range.

2. **DEBUG** A Lambda function is getting 403 Access
   Denied on a DynamoDB table. The Lambda's execution
   role has a DynamoDB Allow policy. Walk through the
   IAM policy evaluation steps to identify where the
   Deny could be coming from.

3. **EXPLAIN** When two Allow policies both grant access,
   why an SCP Deny overrides them both, and why this
   is the correct security behavior for organization
   guardrails.

---

*Identity & Access Management | IAM-013 | v5.0*