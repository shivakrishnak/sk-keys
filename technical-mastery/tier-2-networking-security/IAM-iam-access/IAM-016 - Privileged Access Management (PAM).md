---
id: IAM-016
title: "Privileged Access Management (PAM)"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-006, IAM-012
used_by: IAM-020, IAM-026, IAM-030
related: IAM-012, IAM-020, SEC-028
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
nav_order: 16
permalink: /technical-mastery/iam/privileged-access-management-pam/
---

⚡ TL;DR - Privileged Access Management (PAM) controls
access to the highest-privilege accounts in an organization:
root/admin accounts, database admin credentials, domain
admin, production SSH keys, and API credentials with
unrestricted access. PAM vaults these credentials (so
they are never seen in plaintext), enforces just-in-time
access (temporary, task-scoped elevation), and records
privileged sessions (video replay of what the privileged
user did). CyberArk, BeyondTrust, and Delinea are the
dominant vendors.

---

### 🔥 The Problem This Solves

The most dangerous accounts in any organization are
not compromised user accounts - they are the accounts
with unilateral power to do anything: AWS root account,
production database admin, Active Directory domain admin,
Jenkins service account with production deploy rights.

Traditional problems:
- Root password stored in a shared spreadsheet
- Production SSH keys distributed to everyone "just in case"
- Database admin credentials hardcoded in a config file
- No record of who used an admin account and what they did

When these accounts are compromised (insider threat,
phishing, credential theft), there is no limit to the
damage: databases wiped, all customer data exfiltrated,
production environment destroyed. PAM closes this gap.

---

### 📘 Textbook Definition

Privileged Access Management (PAM) is the set of
cybersecurity strategies and technologies for controlling,
monitoring, securing, and auditing privileged access
to critical systems and accounts.

**Core PAM capabilities:**

**Credential Vaulting:** Privileged credentials are stored
encrypted in a PAM vault (HSM-backed). Humans never see
plaintext passwords. The PAM system injects credentials
into sessions automatically (password injection, SSH
key injection). Credentials are rotated automatically
after every use (or on a scheduled cycle).

**Just-in-Time (JIT) Access:** Privileged access is not
standing. Engineers request elevated access for a specific
task. A manager or automated policy approves. The PAM
tool grants temporary access (typically 1-4 hours) and
revokes it automatically when the time window expires.

**Privileged Session Management (PSM):** All privileged
sessions are proxied through the PAM tool. Sessions are
recorded (keystrokes + video screen capture). Session
recordings are available for forensic review. Live
sessions can be terminated by security operations.

**Least Privilege for Privileged Accounts:** PAM enforces
that even privileged access is task-scoped. An engineer
fixing a production database issue gets read access
to the specific schema they need, not full DBA rights
for the entire database.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
PAM locks away the most powerful credentials, lets
people borrow them only when needed and only for as
long as needed, and records everything they did.

**One analogy:**
> A gun safe analogy:
> - Powerful weapons (privileged credentials) are locked
>   in a safe, not distributed to everyone
> - To use one, you submit a request and state the reason
> - You get access for 2 hours with a recorded checkout
> - The safe re-locks automatically when time expires
> - A log records: who checked out what, when, for how long,
>   and a recording of what they did with it

**One insight:**
PAM's most important security property is break-glass
with full audit: in a genuine emergency, elevated access
is available quickly (without waiting for business-hours
approval), but every emergency access event is logged,
investigated, and reviewed post-incident.

---

### 🔩 First Principles Explanation

**The insider threat problem:**

External attackers need to compromise systems from
outside the perimeter. Insider threats (malicious
employees, compromised contractor accounts) have
direct access to systems. Standing privileged accounts
mean that any compromised insider account has unlimited
destructive capability.

PAM's defense: eliminate standing privileged access.
When there are no standing admin credentials distributed
to individuals, insider threat capability is constrained
to the minimal session window granted by PAM for
legitimate tasks.

**The auditing imperative:**

When a production incident occurs and something was
changed or deleted: "who did this and when?" is the
first forensic question. Without PAM session recording,
the answer is "someone with admin access, we don't know
who or exactly what they did." With PAM: exact keystroke
log, video replay, session metadata (who, when, from
where, for how long).

**Technical architecture:**

PAM works via session proxying: the engineer's SSH
or RDP session connects to the PAM proxy, not directly
to the target system. The PAM proxy authenticates to
the target with vaulted credentials (invisible to the
engineer) and records the full session stream. The
engineer never receives the actual password.

---

### 🧪 Thought Experiment

**Scenario: Engineer needs to fix a production database**

**Without PAM:**
1. Engineer asks on Slack for the prod DB password
2. Another engineer pastes it in a private message
3. Password is now in Slack history, visible to Slack admins
4. Engineer fixes the issue
5. Password is never rotated (too hard to update in all places)
6. Three months later: password rotates during a different
   incident, breaks the hardcoded config in 4 services

**With PAM (CyberArk / HashiCorp Vault):**
1. Engineer opens PAM portal, requests "prod-db-admin"
   access for "investigating replication lag issue"
2. On-call manager approves via Slack integration
3. PAM grants 2-hour window, injects DB credentials
   into engineer's session without showing password
4. Session is recorded: every query, every result
5. 2-hour window expires: access automatically revoked
6. Post-incident: security team reviews session recording
   to confirm only replication-related queries were run
7. Credential automatically rotated after session closes

---

### 🧠 Mental Model / Analogy

> PAM is the evidence room at a police station:
>
> - Evidence (privileged credentials) is locked, catalogued,
>   and accessible only through a formal checkout process
> - Checkout requires a reason, a case number, and a supervisor
>   signature (approval workflow)
> - Every item checked out is logged: who, when, duration
> - The checkout window is time-limited; evidence returns
>   automatically
> - Evidence is inspected and re-sealed after return
>   (credential rotation)
> - All activity with evidence is documented for the case
>   file (session recording for audit)

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
PAM is a secure locker for the most powerful system
passwords. You can borrow them temporarily with a reason,
and everything you do while using them is recorded.

**Level 2 (junior developer):**
In a PAM-enabled environment: to access a production
server, you submit an access request via the PAM console.
After approval, a proxy session opens (SSH via PAM).
You never see the server password. The session closes
after your approved time window.

**Level 3 (mid engineer):**
HashiCorp Vault as a lightweight PAM alternative: Vault
stores database credentials in a "dynamic secrets" engine.
When a user requests database credentials, Vault creates
a temporary database user with time-limited credentials
(TTL: 1 hour). After TTL expiry, the database user is
automatically deleted. No standing credentials, automatic
rotation, audit log per credential request.

**Level 4 (senior/staff):**
PAM for cloud resources: AWS IAM Identity Center with
permission set approval workflows provides PAM-like
JIT for AWS console access. Users request elevated
permission sets (PowerUser, AdministratorAccess) for
a time-limited session. Approval can be automated via
policy (auto-approve for specific conditions) or require
manual approval. Session is recorded in CloudTrail.

**Level 5 (distinguished):**
Zero Standing Privilege (ZSP) architecture: the target
state where no human has any standing privileged access
to any production system. All access is JIT. All sessions
are recorded. Break-glass procedures exist for true
emergencies (IdP is down; PAM is unavailable) with
enhanced monitoring and post-incident mandatory review.
Achieving ZSP requires: PAM for human access, SPIFFE/SPIRE
for service-to-service (no hardcoded service credentials),
cloud workload identity for all automated processes.
The security benefit: zero standing credentials = zero
credential theft of standing admin accounts.

---

### ⚙️ How It Works (Mechanism)

```
PAM Session Proxy Architecture:

Engineer's terminal:
  ssh admin@pam-proxy.company.com

PAM Proxy:
  1. Authenticate engineer (corporate SSO / MFA required)
  2. Check active access request (approved? within time window?)
  3. Retrieve target credentials from vault
  4. Open SSH session to target: ssh prod-db-01 (using vaulted key)
  5. Proxy all I/O bidirectionally between engineer and target
  6. Record: keystroke log + screen capture to tamper-evident store
  7. On time expiry: terminate session, revoke credentials

HashiCorp Vault Dynamic Secrets:
  1. App requests database credentials:
     GET /v1/database/creds/readonly-role
     Headers: X-Vault-Token: <app-token>
  2. Vault creates temporary DB user:
     CREATE USER 'v-app-read-1234' IDENTIFIED BY '...'
     GRANT SELECT ON app_db.* TO 'v-app-read-1234'
  3. Vault returns: username, password, lease_id, lease_duration
  4. App uses credentials (TTL: 1 hour)
  5. After TTL: Vault deletes user:
     DROP USER 'v-app-read-1234'
  6. No standing credentials at any point

AWS JIT with IAM Identity Center:
  User requests "PowerUser" permission set for account 123
  -> Approval workflow triggers (manager in Slack)
  -> On approval: session (8 hour max) issued
  -> CloudTrail records all API calls under session
  -> Session expires automatically
```

---

### ⚖️ Comparison Table

| Solution | Best For | Credential Type | Session Recording | Complexity |
|:---|:---|:---|:---|:---|
| CyberArk | Enterprise PAM (Windows, Unix, DB) | All credential types | Yes (PSM) | Very High |
| BeyondTrust | Enterprise PAM, remote access | All types | Yes | High |
| HashiCorp Vault | Dev/DevOps teams, cloud credentials | Secrets + dynamic | No (audit log) | Medium |
| AWS Secrets Manager | AWS-centric secrets management | API keys, DB passwords | No | Low |
| AWS IAM Identity Center | AWS console/API JIT access | AWS session credentials | Via CloudTrail | Low-Medium |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "PAM and secrets management are the same" | Secrets management (Vault, AWS Secrets Manager) stores and rotates credentials. PAM adds session proxying, session recording, and JIT approval workflows. PAM is a superset. |
| "PAM is only for large enterprises" | HashiCorp Vault and AWS IAM Identity Center provide PAM-like capabilities accessible to any organization. The commercial PAM suites (CyberArk) are enterprise-grade. |
| "JIT access slows down engineers" | Properly designed JIT workflows (auto-approve for low-risk, Slack-notification approval for high-risk) add seconds to minutes of overhead. The security benefit justifies this for production access. |
| "PAM prevents insider threats" | PAM detects and investigates insider threats via session recording. It does not prevent them - a malicious engineer with approved access can still do damage within their approved window. |

---

### 🚨 Failure Modes & Diagnosis

**PAM vault unavailable: engineers locked out of production**

```bash
# PAM is down: engineers cannot get production credentials
# Break-glass procedure must be documented and tested

# HashiCorp Vault: check seal status
vault status
# If sealed: unseal with threshold of unseal keys
vault operator unseal $UNSEAL_KEY_1
vault operator unseal $UNSEAL_KEY_2

# If Vault is in HA mode: check all nodes
curl -s https://vault1.internal/v1/sys/health | jq .
curl -s https://vault2.internal/v1/sys/health | jq .

# Emergency access: break-glass account in offline vault
# (separate system from primary PAM, accessible only
# to security ops, with 2-person integrity requirement)
```

**Session recording storage full: sessions not recorded**

```bash
# PAM: check session recording storage capacity
df -h /opt/pam/recordings/
# If > 90% full -> alerts should have fired before this

# Archive old recordings to S3:
aws s3 sync /opt/pam/recordings/ s3://pam-recordings-archive/ \
  --exclude "*.active"

# Configure retention policy: > 12 months to S3 Glacier
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-006` - IAM Principals: privileged account types
- `IAM-012` - Principle of Least Privilege

**Builds On This:**
- `IAM-020` - Just-in-Time Access Provisioning: JIT in PAM
- `IAM-026` - Enterprise IAM Architecture: PAM in enterprise stack
- `IAM-030` - IAM Observability: privileged session audit

**Related:**
- `SEC-028` - Insider Threat: PAM as mitigation
- `IAM-029` - IAM Compliance: PAM for SOC 2 / PCI requirements

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ PAM CORE CAPABILITIES                                │
├─────────────────────┬────────────────────────────────┤
│ Credential Vaulting │ Encrypted storage, no plaintext│
│                     │ injection (engineer never sees)│
├─────────────────────┼────────────────────────────────┤
│ JIT Access          │ Request -> Approve -> Use      │
│                     │ -> Auto-revoke on expiry        │
├─────────────────────┼────────────────────────────────┤
│ Session Recording   │ Keystroke + video capture      │
│                     │ Tamper-evident, forensic-ready │
├─────────────────────┼────────────────────────────────┤
│ Credential Rotation │ Auto-rotate after session      │
│                     │ No standing credentials        │
├─────────────────────┼────────────────────────────────┤
│ Break-Glass         │ Emergency access with enhanced │
│                     │ monitoring + post-review req   │
└─────────────────────┴────────────────────────────────┘
```

**If you remember 3 things:**

1. PAM vaults credentials so engineers never see them
   in plaintext. Credentials are injected into sessions
   automatically.

2. JIT access: request -> approve -> time-limited ->
   auto-revoke. No standing admin access.

3. Session recording is the forensic backbone. "Who
   did what in production" is answerable with PAM.

**Interview one-liner:**
"PAM manages privileged credentials by vaulting them
(no plaintext distribution), enforcing JIT access
(temporary, task-scoped, approved), and recording all
privileged sessions for forensic audit. CyberArk is
enterprise PAM; HashiCorp Vault provides dynamic
secrets for dev/cloud workloads."

---

### 💎 Transferable Wisdom

PAM's JIT pattern is the security embodiment of the
Just-in-Time inventory principle: do not hold standing
inventory (credentials) that you might need someday.
Acquire exactly what you need exactly when you need it.
This same pattern appears in cloud infrastructure (spot
instances on demand), database connections (pool acquired
when needed, returned when done), and thread pools
(threads created for task duration, not standing idle).
The security version: no standing credentials = no
standing attack surface.

---

### ✅ Mastery Checklist

1. **DESIGN** A JIT privileged access workflow for
   production database access: who can request, what
   information is required, who approves, how long is
   the window, what is recorded, and what happens when
   the window expires.

2. **COMPARE** HashiCorp Vault dynamic database
   credentials vs CyberArk Privileged Session Manager.
   When does each provide sufficient PAM controls
   and when does the other approach add value?

3. **RESPOND** During a production incident, PAM is
   unavailable. Describe the break-glass procedure,
   including how you would ensure the emergency access
   is audited after the fact and the incident is reviewed.

---

*Identity & Access Management | IAM-016 | v5.0*