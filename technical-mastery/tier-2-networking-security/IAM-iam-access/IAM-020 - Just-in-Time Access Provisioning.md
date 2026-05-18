---
id: IAM-020
title: "Just-in-Time Access Provisioning"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-012, IAM-016
used_by: IAM-021, IAM-026, IAM-027
related: IAM-016, IAM-019, IAM-021
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
nav_order: 20
permalink: /technical-mastery/iam/just-in-time-access-provisioning/
---

⚡ TL;DR - Just-in-Time (JIT) access provisioning grants
elevated access exactly when needed and revokes it
automatically when the time window expires, eliminating
standing privilege. The threat model: standing privileged
access is the #1 attack surface for lateral movement and
insider threats. JIT patterns: PAM tools (CyberArk JIT
elevation), cloud IAM (AWS IAM Identity Center permission
set approval), Zero Standing Privilege (ZSP - no human
has standing elevated access to any system), and dynamic
database credentials (HashiCorp Vault - credentials
created on demand, auto-expired).

---

### 🔥 The Problem This Solves

Standing privilege is the security industry's "always-
loaded gun" problem. When a senior engineer has permanent
production admin access:

- If their laptop is compromised: attacker has production
  admin access immediately
- If they are a malicious insider: they have persistent,
  unmonitored elevated access
- If they leave the company: off-boarding must catch and
  revoke that access (often missed)

Standing access accumulates silently. Over 5 years,
an engineer may hold 12+ elevated access grants they
do not actively use. Each is a standing attack surface.

JIT access eliminates standing privilege: at rest,
the engineer has no elevated access. They obtain it
for a task, use it, and it expires. Compromise between
tasks = minimal blast radius.

---

### 📘 Textbook Definition

Just-in-Time (JIT) access provisioning is the practice
of granting elevated access rights only for the specific
timeframe required to complete a task, with automatic
expiry and revocation after the time window.

**JIT access components:**

**Approval Workflow:** Engineer requests elevated access
(specifying scope, justification, duration). Policy
engine or human approver evaluates the request. Access
granted only on approval.

**Time-Boxed Grant:** Access is tied to a TTL (time
to live). When TTL expires, access is automatically
revoked by the IAM/PAM system - no human intervention
required for revocation.

**Audit Trail:** Every JIT access event is logged:
who requested, what justification, who approved, what
was accessed, when access expired. This is the forensic
record for incident investigation and compliance.

**Break-Glass:** Emergency JIT access for P0 incidents
when normal approval workflows are unavailable or
too slow. Break-glass access has enhanced monitoring
and mandatory post-incident review.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JIT access means you have no keys until you need them,
you borrow them for exactly as long as the task takes,
and they are automatically returned when you are done.

**One analogy:**
> Borrowing from a library instead of buying:
> - No standing collection of books "just in case"
> - Borrow exactly the book you need, exactly when you need it
> - 2-week loan period - book is automatically due back
> - No renewal needed by default; explicitly request extension
> - Librarian records every checkout: who borrowed what and when
> - At the end of the year: you hold no books you did not use

**One insight:**
The security gain of JIT is not the approval workflow
(though that adds value). The security gain is that
the attack surface between tasks is zero. An attacker
compromising an account with no current elevated access
has no elevated access - regardless of how powerful
that account could be when needed.

---

### 🔩 First Principles Explanation

**Why standing privileges persist despite being dangerous:**

1. **Convenience:** SSH to production immediately is
   faster than requesting access, waiting for approval,
   then SSHing. Speed is the counter-force against JIT.

2. **Operational risk (perceived):** "What if we can't
   get access during an incident?" is the most common
   objection to JIT. Break-glass procedures address
   this (emergency access available within minutes).

3. **Tool immaturity:** Organizations without PAM tools
   cannot implement JIT. JIT requires the infrastructure:
   approval workflow, automated provisioning/deprovisioning,
   session recording.

**JIT vs just-enough-access:**

JIT is the time dimension: access for limited duration.
Just-enough-access (JEA) is the permission scope dimension:
access with minimum necessary permissions.
Combination: JIT + JEA = time-limited, scope-limited
access. Example: "access to read logs on prod-db-01
only, for 2 hours, for the purpose of diagnosing
replication lag." Both time and scope are constrained.

**The database credential version:**

HashiCorp Vault dynamic secrets is JIT for database
credentials: instead of distributing a long-lived
database password, Vault creates a temporary database
user when an application or engineer requests one.
The user exists for the TTL (e.g., 1 hour). After TTL,
Vault deletes the user. No standing database credentials.

---

### 🧪 Thought Experiment

**Implementing JIT for production SSH access:**

```
Goal: no engineer has standing SSH access to production.
      Production SSH requires JIT approval.

Architecture options:

Option 1: PAM (CyberArk / BeyondTrust)
  - Engineer requests access: "Fix DB replication lag"
  - On-call manager approves via Slack integration
  - CyberArk opens SSH session via proxy
  - Engineer never sees SSH key or password
  - Session recorded: keystrokes + commands
  - Session terminates after 2 hours automatically

Option 2: Short-lived SSH certificates (HashiCorp Vault)
  - SSH CA configured on all production hosts
  - Engineer requests SSH certificate:
    vault write ssh/sign/prod-users \
      public_key=@~/.ssh/id_rsa.pub \
      valid_principals="ubuntu" \
      ttl="2h"
  - Vault issues signed certificate (valid 2 hours)
  - Engineer SSHs normally: cert auto-presented
  - After 2 hours: certificate expired, SSH fails
  - Audit: every certificate request logged in Vault
  - No need to distribute SSH keys to servers

Option 3: AWS Systems Manager (SSM) Session Manager
  - No port 22 open on production instances
  - Access via AWS Console or CLI:
    aws ssm start-session --target i-1234567890
  - Requires IAM permission (time-limited via JIT policy)
  - All commands logged to CloudTrail + CloudWatch
  - Session terminates with IAM permission expiry
```

---

### 🧠 Mental Model / Analogy

> JIT access is like a hotel key card system:
>
> - When you check in (access request), you get a key
>   card for your specific room for your specific stay duration
> - Key card deactivates at checkout (TTL expiry)
> - No one holds "master key" credentials indefinitely
> - Hotel tracks: who had which key card and when
> - If a guest needs to extend (renew access request):
>   explicit extension at front desk (re-approval)
> - Master key (break-glass) exists but only for hotel
>   operations team, with strict usage logging

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
JIT means engineers ask for access when they need it,
use it for the task, and it automatically disappears
when they are done. No one holds "permanent admin access"
between tasks.

**Level 2 (junior developer):**
With AWS IAM Identity Center JIT: request a permission
set (e.g., PowerUser) for a specific AWS account and
duration. On approval, you receive temporary AWS
credentials valid for that duration. After expiry,
the credentials stop working and the permission
assignment is removed.

**Level 3 (mid engineer):**
HashiCorp Vault dynamic database credentials for
application access: configure a database secrets engine
with a read-only role. Application code requests
credentials at startup. Vault creates a temporary
DB user with TTL matching deployment lifecycle
(e.g., 24 hours). App uses the credentials. When
deployment rolls over, old credentials expire, new
deployment gets fresh credentials. No static DB
passwords in environment variables or config maps.

**Level 4 (senior/staff):**
Zero Standing Privilege (ZSP) rollout strategy for
a 200-person engineering organization:
Phase 1: Production break-glass inventory (identify
all standing admin access). Phase 2: PAM tool
deployment with session proxy for critical systems.
Phase 3: JIT policy enforcement - remove standing
admin. Phase 4: Monitor and tune approval times.
Phase 5: Extend JIT to all privileged access (not
just production). Measure: mean time to access (MTTA)
for JIT workflows. Target: < 5 minutes for approved
patterns, < 15 minutes for novel requests.

**Level 5 (distinguished):**
JIT for service-to-service access: SPIFFE/SPIRE (CNCF)
provides workload identity JIT for microservices.
Each workload gets a SPIFFE ID (URI format: spiffe://
trust-domain/path) backed by a short-lived X.509
SVID (SPIFFE Verifiable Identity Document) with TTL
typically 1 hour. Certificate is auto-renewed by the
SPIRE agent before expiry. Service mesh (Istio/Linkerd)
uses SVIDs for mTLS between services. No standing
service certificates: all certificates JIT-issued and
auto-expired.

---

### ⚙️ How It Works (Mechanism)

```
AWS IAM Identity Center JIT Permission Set:

1. Permission Set: "PowerUser" (AdministratorAccess minus
   iam:CreateUser, iam:DeleteUser)
   Duration: 8 hours max

2. Engineer requests via IAM Identity Center portal:
   Account: prod-account-123456
   Permission Set: PowerUser
   Duration: 2 hours
   Justification: "Investigating Lambda latency spike"

3. Approval workflow:
   Notified: on-call lead (Slack webhook)
   Auto-approve if: within business hours + low-risk tag
   Require human if: outside business hours or high-risk account

4. On approval: IAM Identity Center creates account assignment:
   POST /accounts/assignments/create
   {
     "accountId": "123456",
     "permissionSetArn": "arn:aws:sso:::permissionSet/ps-PowerUser",
     "principalType": "USER",
     "principalId": "alice-user-id"
   }

5. Alice receives temporary credentials:
   aws sso login --profile prod-poweruser
   # Valid for 2 hours; refreshed in memory only

6. After 2 hours: IAM Identity Center automatically
   removes the account assignment
   CloudTrail: all API calls under the session logged
   with "principalId": "alice@company.com"

HashiCorp Vault SSH Certificate JIT:

vault write ssh/sign/prod-ops \
  public_key=@~/.ssh/id_rsa.pub \
  ttl=2h \
  extensions='permit-pty=,permit-user-rc='
  
# Returns:
{
  "signed_key": "ecdsa-sha2-nistp256-cert-v01@... CERT",
  "serial_number": "2749334871234567",
  "lease_duration": 7200
}

# SSH using certificate (auto-expires after 2h):
ssh -i ~/.ssh/id_rsa-cert.pub alice@prod-db-01
```

---

### ⚖️ Comparison Table

| Approach | Mechanism | Session Recording | Complexity | Best For |
|:---|:---|:---|:---|:---|
| PAM JIT (CyberArk) | Session proxy + vaulted creds | Yes | High | Enterprise privileged access |
| AWS IAM Identity Center JIT | Permission set TTL | Via CloudTrail | Medium | AWS-centric environments |
| Vault SSH Certificates | Short-lived cert | Via Vault audit log | Medium | Kubernetes/cloud SSH |
| Vault Dynamic DB Creds | Temp DB user | Via Vault audit log | Low-Medium | Database credentials |
| SPIFFE/SPIRE | Short-lived X.509 SVID | Via service mesh telemetry | High | Service-to-service (K8S) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "JIT approval slows down incident response" | Well-designed break-glass + auto-approve policies make JIT < 5 minutes for most cases. The overhead is real but manageable; the security benefit outweighs it. |
| "JIT is only for human access" | JIT is critical for service credentials too. Dynamic database credentials (Vault) and workload identity certificates (SPIFFE) are JIT for machine-to-machine access. |
| "Short TTL means frequent re-authentication" | Short TTL is mitigated by auto-renewal: Vault agents, SDKs, and SPIRE agents renew credentials before expiry without user interaction. The engineer sees no interruption. |
| "JIT prevents all insider threats" | JIT constrains the time window of insider threat. A malicious insider can still cause damage within an approved JIT window. Session recording and behavioral analytics are the companion controls. |

---

### 🚨 Failure Modes & Diagnosis

**JIT approval workflow stuck: access not granted**

```bash
# Engineer waiting > 15 minutes for JIT approval
# Common causes: approver notification not delivered,
# approver is OOO, approval system degraded

# Check: IAM Identity Center assignment status
aws sso-admin list-account-assignments \
  --instance-arn $SSO_INSTANCE_ARN \
  --account-id $ACCOUNT_ID \
  --permission-set-arn $PERMISSION_SET_ARN

# If stuck in pending:
# 1. Escalate to secondary approver
# 2. Activate break-glass procedure if P0 incident
# 3. Post-incident: review approval notification path

# Break-glass procedure:
# 1. Declare incident (PagerDuty/Slack)
# 2. Access break-glass vault (2-person integrity)
# 3. Log: break-glass-used, incident-ID, accessor, timestamp
# 4. Post-incident: security review of break-glass access
```

**Vault lease expiry during long-running migration job**

```bash
# Job started with Vault dynamic DB creds
# 3 hours in: credentials expire, job fails
# Vault lease duration was set to 2 hours

# Prevention: set lease TTL >= expected job duration
vault write database/roles/migration-role \
  default_ttl="6h" \
  max_ttl="12h"

# Or: use Vault lease renewal from job
# Python/Go Vault SDK auto-renews leases
# before expiry if configured

# Recovery: renew lease manually if job is running
vault lease renew $LEASE_ID
# Or: get new credentials, pass to running job
# (application must support hot credential refresh)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-012` - Principle of Least Privilege
- `IAM-016` - Privileged Access Management (PAM)

**Builds On This:**
- `IAM-021` - Zero Trust Identity: JIT as core Zero Trust pattern
- `IAM-026` - Enterprise IAM Architecture
- `IAM-027` - IAM Platform Design at Scale

**Related:**
- `IAM-019` - IGA: recertification as periodic JIT governance
- `IAM-021` - Zero Trust: never trust, always verify requires JIT

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ JIT ACCESS PATTERN LIBRARY                           │
├──────────────────────┬───────────────────────────────┤
│ Production SSH       │ Vault SSH certs (TTL: 1-4h)  │
│                      │ or PAM session proxy          │
├──────────────────────┼───────────────────────────────┤
│ Database access      │ Vault dynamic secrets         │
│                      │ (temp user, auto-deleted)     │
├──────────────────────┼───────────────────────────────┤
│ AWS console/API      │ IAM Identity Center           │
│                      │ permission set TTL            │
├──────────────────────┼───────────────────────────────┤
│ Service-to-service   │ SPIFFE/SPIRE SVIDs            │
│                      │ (X.509 cert TTL: 1h, auto-renewed)│
├──────────────────────┼───────────────────────────────┤
│ Break-glass          │ PAM vault + 2-person integrity│
│                      │ + mandatory post-review       │
└──────────────────────┴───────────────────────────────┘
```

**Interview one-liner:**
"JIT access eliminates standing privilege by granting
elevated access only for the duration of a specific
task and revoking it automatically on expiry. Patterns:
PAM session proxy, AWS IAM Identity Center permission
set TTL, Vault SSH certificates, Vault dynamic database
credentials. Zero Standing Privilege is the target state."

---

### 💎 Transferable Wisdom

JIT access is the security application of the
Just-in-Time manufacturing principle: eliminate
inventory (standing privilege) that is not currently
needed. Inventory has carrying costs (standing attack
surface). The same pattern is applied to: database
connections (connection pool - create when needed,
return when done), thread pools (acquire for task,
release after), and cloud infrastructure (spin up
capacity when needed, tear down when idle). In each
domain, standing resources create waste or risk;
dynamic acquisition eliminates both.

---

### ✅ Mastery Checklist

1. **DESIGN** Implement JIT SSH access for 50
   production servers without a commercial PAM tool.
   Describe the HashiCorp Vault SSH certificate CA
   setup, the request/approval/issuance flow, and
   how you audit every session.

2. **CONFIGURE** An application needs database
   credentials that expire automatically. Show the
   HashiCorp Vault database secrets engine configuration
   for a PostgreSQL database, including TTL settings,
   role creation SQL, and the application credential
   request code.

3. **OPERATE** A P0 production incident occurs at 2am.
   Your JIT system requires manager approval but the
   on-call manager is unreachable. Describe the
   break-glass procedure, the security controls that
   should be active during break-glass, and the
   mandatory post-incident review steps.

---

*Identity & Access Management | IAM-020 | v5.0*