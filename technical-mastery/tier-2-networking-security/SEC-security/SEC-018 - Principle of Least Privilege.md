---
id: SEC-018
title: "Principle of Least Privilege"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-007, SEC-008
used_by: SEC-025, SEC-092, SEC-095
related: SEC-001, SEC-007, SEC-008, SEC-025, SEC-063, SEC-092, SEC-095
tags:
  - security
  - least-privilege
  - access-control
  - iam
  - zero-trust
  - authorization
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/sec/principle-of-least-privilege/
---

⚡ TL;DR - The Principle of Least Privilege (PoLP): every
user, service, process, and component should have ONLY the
permissions required to perform its function - nothing more.
If a process only reads from a database: it should not have
write permissions. If a microservice only serves customer
profiles: it should not have access to payment data. If a
build CI/CD pipeline only deploys to staging: it should not
have production credentials.

Why it matters: least privilege is the primary way to limit
blast radius when something goes wrong. When an SQL injection
vulnerability exists: a read-only DB user limits damage to
data exposure (severe). A read-write user allows data
destruction. A user with DROP TABLE permission allows
catastrophic data loss. The attack happened in both cases
- least privilege determines how bad the outcome is.

In practice: inventory all permissions, identify which are
actually required, remove the rest. Repeat regularly because
permissions accumulate (privilege creep). Use temporary
elevated access (just-in-time) for sensitive operations.

---

| #018 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, Defense in Depth, Authentication vs Authorization | |
| **Used by:** | Security Mindset, Privilege Escalation, AWS Security | |
| **Related:** | Defense in Depth, Authentication, Privilege Escalation, IAM, Zero Trust | |

---

### 🔥 The Problem This Solves

**2013 EDWARD SNOWDEN:**
NSA contractor with broad system access. Used his privileged
position to download classified documents from systems where
he had legitimate access - but far beyond his operational
need. The NSA had not applied least privilege to contractor
access: having access to SOME classified data granted access
to SIGNIFICANTLY more than required.

**2017 EQUIFAX:**
The struts vulnerability gave attackers code execution on a
web server. But the web server ran with extensive network
access and database permissions. Attackers used that access
to pivot to databases containing 147 million people's
records. If the web server had only had access to the
specific database tables it needed for its function (not
ALL tables in ALL databases), the breach impact would have
been dramatically reduced.

Least privilege does not prevent the initial compromise.
It limits how far an attacker can move after compromise.

---

### 📘 Textbook Definition

**Principle of Least Privilege (PoLP):** A security principle
from Saltzer and Schroeder (1975) stating that every component
of a system should be able to access only the information
and resources that are necessary for its legitimate purpose.

**Also known as:** Principle of minimal authority, Principle
of minimal privilege, Principle of least authority.

**Scope of application:**
- **Users:** Only the roles/permissions needed for their job.
  Developers don't have production access by default.
  DB admins don't have billing access.
- **Service accounts:** Database user for the reporting
  service has SELECT only on reporting tables. No INSERT,
  UPDATE, DELETE. No access to other databases.
- **Processes/applications:** Application process runs as
  a dedicated low-privilege OS user. Not root. Not admin.
- **Network access:** Service A can reach Service B's API.
  Service A cannot reach Service C's admin port.
- **Cloud IAM:** Lambda function can read from S3 bucket X.
  Cannot write. Cannot access S3 bucket Y. Cannot access RDS.
- **Temporary elevation:** Just-in-time (JIT) access grants
  elevated permissions for specific tasks with time limits
  and audit logs. Break-glass procedures for emergency access.

**Privilege creep:** The gradual accumulation of permissions
over time as job roles change but permissions are never
removed. Annual access reviews required to combat this.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every user, service, and process should have only the
permissions it actually needs - nothing extra. Extra
permissions = extra blast radius when something goes wrong.

**One analogy:**
> A hotel gives housekeeping staff keys only to rooms on
> their assigned floor - not a master key to every room
> in the hotel. If a housekeeper is coerced by an attacker,
> the attacker can only access rooms on that floor.
> The principle: limit the key, limit the damage.
> Privilege creep = housekeeper keeps floor 3 key even
> after being reassigned to floor 5. Now compromising
> floor 5's housekeeper gives access to floor 3 too.
> Access review = take back floor 3 key when reassigned.

---

### 🔩 First Principles Explanation

**Why least privilege is foundational to security:**

```
THE BLAST RADIUS EQUATION:

Damage from a security incident = (exploit path) × (permissions available)

SCENARIO: SQL injection vulnerability exists in an endpoint.

Attacker exploits it. What happens next depends on DB permissions:

DB USER: full_access_user (GRANT ALL ON *.*)
  - Can read ALL tables in ALL databases
  - Can write/delete ALL records
  - Can create/drop tables
  - Can exec system commands (xp_cmdshell in MSSQL)
  DAMAGE: Complete database compromise + potential OS access

DB USER: app_user (SELECT, INSERT, UPDATE on app_db.*)
  - Can read/write app database
  - Cannot DROP tables (no DROP permission)
  - Cannot access other databases
  DAMAGE: Data breach (all app_db data). Severe but bounded.

DB USER: read_only_user (SELECT on app_db.users, app_db.orders)
  - Can only read specific tables
  - Cannot modify anything
  DAMAGE: Data read from two tables only. Contained.

SAME vulnerability. Radically different outcomes.
Least privilege converted a catastrophic breach into a
serious but manageable data exposure.

APPLICATION TO SERVICES (Equifax pattern):
  Web server has: network access to ALL internal services
  After exploit: attacker uses web server as pivot point
  - Reaches internal admin interfaces
  - Connects to ALL database clusters
  - Moves laterally across the network
  
  With least privilege:
  Web server has: access to ONLY the one database it serves
  After exploit: attacker's pivot is blocked at network layer
  - Cannot reach other services
  - Cannot access payment database (web server doesn't need it)
  - Blast radius: limited to web server's direct dependencies
```

---

### 🧪 Thought Experiment

**SCENARIO: Designing an e-commerce system's permission model**

```
SYSTEM COMPONENTS:
  - Product Service: serves product catalog
  - Order Service: creates and manages orders
  - Payment Service: processes payments
  - Reporting Service: generates sales reports
  - Admin Service: manages users and products

NAIVE DESIGN (single DB user for all services):
  All services connect with: admin_user (full DB access)
  Compromise of ANY service: full access to payment data, 
    order history, user credentials. Maximum blast radius.

LEAST PRIVILEGE DESIGN:

Product Service DB user:
  SELECT, INSERT, UPDATE on products, categories
  No access to: orders, payments, users

Order Service DB user:
  SELECT, INSERT, UPDATE on orders
  SELECT on products (read-only, create order needs product data)
  No access to: payments (raw card data), users (passwords)

Payment Service DB user:
  INSERT on payment_transactions
  SELECT on payment_transactions WHERE id = ?
  No access to: orders table, products, users
  (Payment service never reads others' data)

Reporting Service DB user:
  SELECT on orders, products, order_items
  Explicitly: no access to payments table (contains card data)
  No write permissions anywhere

Admin Service DB user:
  Full access to users, products, categories
  No access to: payment_transactions (PCI scope separation)

NETWORK POLICIES (add to DB permissions):
  Product Service: can only reach product_db
  Payment Service: isolated network segment, requires mTLS
  Reporting Service: read replica only (physically separate)

OUTCOME: Compromise of Product Service gives attacker
  access to product/category data only. No payment data.
  No user credentials. No order history. Blast radius: contained.
```

---

### 🧠 Mental Model / Analogy

> Least privilege is the security version of "need to know"
> in intelligence work. Analysts only receive intelligence
> relevant to their specific mission - not all available
> intelligence. This limits the damage from a compromised
> analyst. In software: services only have the permissions
> needed for their specific function. Compromising a service
> only gives attackers what that service could access - not
> everything the system contains. The attacker's access is
> bounded by the compromise point's permissions.
> 
> Privilege creep is like an analyst keeping access to
> previous project files after transferring to a new mission.
> Over time they accumulate access to everything.
> Access review is the intelligence world's "need to know"
> review - remove access to programs you no longer work on.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Give people and systems only the access they need for
their specific job. Your delivery person needs access to
the delivery entrance, not your master keys. If they're
compromised, the damage is limited. Same idea for software:
a service that reads products doesn't need to delete orders.

**Level 2 - How to use it (junior developer):**
When creating database users for services: start with
nothing, add only what the service actually calls.
Test it: run the service with the minimal-permission user.
If it fails: that reveals what permissions are actually needed.
Avoid: connecting to production with your personal admin
credentials from application code.

**Level 3 - How it works (mid-level engineer):**
Per-service database users with minimal permissions.
Service accounts for CI/CD pipelines (separate from
personal accounts, scoped to what CI needs). IAM roles
for cloud services (Lambda: only the S3 bucket it reads,
the SQS queue it polls, the DynamoDB table it writes).
Regular access reviews (quarterly): list all permissions
per service, identify unused ones, remove. Audit logs
on sensitive operations (who used what permission, when).

**Level 4 - Why it was designed this way (senior/staff):**
Saltzer and Schroeder's 1975 paper "The Protection of
Information in Computer Systems" listed least privilege as
one of eight security design principles. 50 years later it
remains a foundational principle because it addresses a
fundamental problem: components fail (bugs, supply chain
compromise, insider threat). Limiting permissions bounds
the impact of failure. Modern implementations: IAM roles
(AWS, GCP, Azure) allow fine-grained permission sets per
service without shared credentials. Service mesh mTLS
(Istio, Linkerd) enforces service-to-service authorization
at the network layer. Zero trust architecture extends
least privilege to network access: services are not trusted
by default even if they are inside the perimeter.

**Level 5 - Mastery (distinguished engineer):**
Just-in-time (JIT) access: elevated permissions granted on
demand, for specific tasks, with time limits, automatically
revoked. No standing privilege: a DBA does not have
continuous production DB admin access. They request it,
it's approved (with audit trail), granted for 2 hours,
then automatically revoked. Tools: HashiCorp Vault dynamic
credentials (DB passwords generated on demand, auto-expire),
AWS IAM Identity Center time-limited role access, Microsoft
PIM (Privileged Identity Management). Break-glass procedures:
predefined emergency access path for crises, fully audited,
alerts on use, reviewed post-incident. The operational cost
of JIT: friction in routine operations - this friction is
intentional (it ensures every privileged action is deliberate
and documented).

---

### ⚙️ How It Works (Mechanism)

**Privilege escalation paths when least privilege fails:**

```
PRIVILEGE ESCALATION PATH (common pattern):

INITIAL POSITION: Attacker has low-privilege access
  (web server compromise via SQL injection)

WITHOUT LEAST PRIVILEGE:
  Web server runs as: root (or db_user with full access)
  Step 1: SQL injection → execute SQL as full DB user
  Step 2: LOAD_FILE / xp_cmdshell → OS command execution
  Step 3: As root → read /etc/shadow, /etc/passwd
  Step 4: Install backdoor, pivot to internal network
  Step 5: Internal network access → reach payment database
  Full system compromise. Root cause: excessive permissions.

WITH LEAST PRIVILEGE:
  Web server runs as: www-data (low OS privilege)
  DB user: SELECT on users, products ONLY
  Network: can reach only app_db, not internal network
  
  Step 1: SQL injection → can only SELECT users/products
  Step 2: No shell escape functions available (DB restricted)
  Step 3: Cannot read /etc/shadow (www-data has no access)
  Step 4: Cannot reach payment database (network policy)
  Attacker is contained. Damage: read-only user/product data.

PRINCIPLE: Each privilege boundary is a potential stop point.
  More boundaries = more stop points = smaller blast radius.

CLOUD IAM EXAMPLE (AWS):
  Lambda function needs:
    Read from: s3://data-bucket/uploads/
    Write to: sqs://processing-queue
    Write to: dynamodb://processing-results

  BAD IAM policy (overly broad):
    { "Effect": "Allow", "Action": "s3:*", "Resource": "*" }
    { "Effect": "Allow", "Action": "*", "Resource": "*" }
  If Lambda is compromised: attacker has full S3 + full AWS.

  GOOD IAM policy (least privilege):
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::data-bucket/uploads/*"
    },
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:us-east-1:123:processing-queue"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:PutItem"],
      "Resource": "arn:aws:dynamodb:us-east-1:123:table/processing-results"
    }
  If Lambda is compromised: attacker can only read from one
  S3 prefix, write to one queue, write to one DynamoDB table.
  Cannot read secrets, access other services, or elevate.
```

---

### 💻 Code Example

**Database user permissions - right-size per service:**

```sql
-- E-commerce database: least privilege user setup

-- BAD: single admin user for all services (avoid)
-- All services use: username=admin, password=...
-- Compromise of any service = full database access

-- GOOD: per-service users with minimal permissions

-- Product Service: reads/updates products only
CREATE USER 'product_svc'@'%' IDENTIFIED BY '<strong-random-password>';
GRANT SELECT, INSERT, UPDATE ON ecommerce.products TO 'product_svc'@'%';
GRANT SELECT, INSERT, UPDATE ON ecommerce.categories TO 'product_svc'@'%';
-- No access to: orders, payments, users

-- Order Service: manages orders, needs to read products
CREATE USER 'order_svc'@'%' IDENTIFIED BY '<strong-random-password>';
GRANT SELECT, INSERT, UPDATE ON ecommerce.orders TO 'order_svc'@'%';
GRANT SELECT ON ecommerce.products TO 'order_svc'@'%';
GRANT SELECT ON ecommerce.users WHERE id = 'current_user' TO 'order_svc'@'%';
-- No UPDATE/DELETE on users, no access to payments

-- Reporting Service: read-only, limited tables (no payment card data)
CREATE USER 'reporting_svc'@'reporting-host' IDENTIFIED BY '<password>';
GRANT SELECT ON ecommerce.orders TO 'reporting_svc'@'reporting-host';
GRANT SELECT ON ecommerce.products TO 'reporting_svc'@'reporting-host';
GRANT SELECT ON ecommerce.order_items TO 'reporting_svc'@'reporting-host';
-- EXPLICITLY NO ACCESS TO: payments table (PCI compliance)
-- Host restriction: only from reporting-host IP (network least privilege)

-- Verify permissions (periodic audit)
SHOW GRANTS FOR 'product_svc'@'%';
SELECT grantee, table_catalog, table_schema, table_name, 
       privilege_type, is_grantable
FROM information_schema.TABLE_PRIVILEGES
WHERE grantee LIKE "'product_svc'%";
```

```python
# Application code: enforce least privilege at service level
# Product service configuration - only provides read access to its DB

# BAD: connection string with admin credentials
DATABASE_URL = "postgresql://admin:password@db:5432/ecommerce"
# All DB operations run with full admin access

# GOOD: connection string with service-specific minimal user
DATABASE_URL = "postgresql://product_svc:password@db:5432/ecommerce"
# Only has SELECT/INSERT/UPDATE on products and categories

# Also: principle applied to external services
# BAD: S3 client with full access
import boto3
s3 = boto3.client('s3')  # Uses default credentials (may be admin)

# GOOD: Assume role with minimal permissions (Lambda/ECS task role)
# In AWS: set an IAM execution role on the Lambda/ECS task.
# The role policy specifies exactly what S3 operations are allowed.
# boto3 automatically uses the execution role - no explicit credentials.
# Principle applied at infrastructure level, not code level.
```

---

### ⚖️ Comparison Table

| Approach | Blast Radius | Operational Cost | Implementation |
|:---|:---|:---|:---|
| **Single admin credential (anti-pattern)** | Maximum (full system access on compromise) | Low (one credential) | Simple but dangerous |
| **Per-service minimal permissions** | Bounded (service's direct data access) | Medium (manage multiple credentials) | Per-service DB users, IAM roles |
| **Read replicas for read-only services** | Minimal (cannot modify data) | Medium (replica infra) | Database-level enforcement |
| **JIT elevated access** | Minimal (temporary, time-limited) | High (approval workflow) | HashiCorp Vault, AWS PIM |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Least privilege prevents attacks | Least privilege does NOT prevent attacks. A SQL injection exists regardless of whether the DB user is admin or read-only. What PoLP does: limits the IMPACT of the attack. The attack succeeds either way - but one case results in reading some data, the other in reading all data, destroying data, and potentially gaining OS access. PoLP is a "blast radius reduction" control, not an attack prevention control. Prevention is the responsibility of other controls (input validation, parameterized queries, etc.). |
| Production credentials only need to be restricted if the team is large | Credential scope is orthogonal to team size. A solo developer with admin access to a production database is as exposed as a large team. The threat model is external: an attacker who exploits a vulnerability gains the permissions of whatever account the code runs as. Team size doesn't change the risk; the permissions do. |

---

### 🚨 Failure Modes & Diagnosis

**Privilege creep detection and remediation:**

```bash
# Audit IAM/service account permissions

# AWS: find overly broad IAM policies
aws iam list-policies --scope Local \
  | jq '.Policies[].PolicyName'
  
# Find policies with wildcard actions (* in Action)
aws iam get-policy-version \
  --policy-arn arn:aws:iam::123456789:policy/MyPolicy \
  --version-id v1 \
  | jq '.PolicyVersion.Document.Statement[] | select(.Action == "*")'
# Any policy with Action: "*" or Resource: "*" is overly broad.

# Find Lambda functions with FullAccess policies (overly privileged)
aws lambda list-functions \
  | jq -r '.Functions[].FunctionName' \
  | xargs -I{} aws lambda get-function-configuration \
    --function-name {} \
  | jq '.Role'
# Then: aws iam list-attached-role-policies --role-name <role>
# Flag: any AWS managed FullAccess policy attached

# Database: find permissions beyond what's documented as needed
mysql> SHOW GRANTS FOR 'product_svc'@'%';
# Compare output against documented required permissions
# Any permission not in the documented list = unnecessary
# Revoke: REVOKE DELETE ON ecommerce.products FROM 'product_svc'@'%';

# Access review checklist (run quarterly):
# 1. List all service accounts and their permissions
# 2. For each permission: is it used? (query audit logs)
# 3. Permissions unused in 90 days: remove
# 4. Permissions that are broader than needed: narrow
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Defense in Depth` - least privilege as one defense layer
- `Authentication vs Authorization` - what privileges are being controlled

**Builds on this:**
- `Privilege Escalation` - what happens when PoLP is violated
- `Zero Trust Architecture` - PoLP extended to network access
- `AWS Security Services` - IAM roles and policies
- `Kubernetes Security Fundamentals` - RBAC + pod security

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE         │ Only permissions required for function.   │
│ PRINCIPLE    │ Nothing extra. Nothing "just in case."    │
├──────────────┼───────────────────────────────────────────┤
│ APPLIES TO   │ Users, service accounts, processes, network│
│              │ Cloud IAM roles, OS users, file permissions│
├──────────────┼───────────────────────────────────────────┤
│ PRIVILEGE    │ Permissions accumulate over time without  │
│ CREEP        │ removal. Annual review: remove unused.   │
├──────────────┼───────────────────────────────────────────┤
│ JIT ACCESS   │ Elevate temporarily. Auto-revoke.         │
│              │ All actions audited. Break-glass for emerg│
├──────────────┼───────────────────────────────────────────┤
│ DB EXAMPLE   │ Reporting user: SELECT only.              │
│              │ App user: SELECT/INSERT/UPDATE specific   │
│              │ tables. Never: admin or DROP TABLE.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Minimum required. Not minimum convenient. │
│              │  Blast radius = permissions × compromise." │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Design for failure: assume any component will be compromised.
Minimize what an attacker gains from that compromise."
Least privilege is an application of fault containment:
design so that any single failure point has bounded impact.
This same thinking appears in: bulkhead pattern in microservices
(failure in one service doesn't cascade to all), circuit
breakers (prevent cascade failure), rate limiting per tenant
(one tenant's burst doesn't degrade others). Security fault
containment: blast radius reduction. Availability fault
containment: bulkheads. The principle is identical: isolate,
bound, contain. The failure is inevitable - the design
determines how contained it is.

---

### 💡 The Surprising Truth

The most dangerous privileges in production systems are
often not the obvious ones (database admin, root). They
are the accumulated "helper" permissions: a service has
S3 access to read its config file → the policy says
`s3:GetObject` on `*` (all buckets). Now any compromise
of that service grants read access to every S3 bucket in
the account - including buckets with PII, credentials,
backups. The AWS "Policy Simulator" and "IAM Access Advisor"
tools show which permissions are actually used in practice.
In typical audits: 60-80% of IAM permissions are never used
(CloudKnox/Microsoft Entra Permission Management findings).
The gap between granted and used permissions is the
"privilege debt" - and it represents the attack surface
that's been silently accumulating. Regular remediation
of unused permissions is one of the highest-ROI security
activities with lowest developer disruption.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** PoLP as blast radius reduction, NOT attack
   prevention - and give a concrete example (SQL injection
   with read-only vs admin user).
2. **DESIGN** a permission model for a multi-service system:
   per-service DB users, per-service IAM roles.
3. **IDENTIFY** privilege creep and explain how to detect
   it (access review, audit logs of unused permissions).
4. **DESCRIBE** JIT access and when to use it (production
   maintenance, incident response, break-glass).

---

### 🎯 Interview Deep-Dive

**Q: What is the Principle of Least Privilege and how do
you apply it in practice?**

*Why they ask:* Foundational security principle. Tests whether
candidate understands security design, not just individual
vulnerabilities.

*Strong answer includes:*
- Definition: every component has only the permissions required
  for its function. No extra.
- Why it matters: blast radius reduction. Compromise of a
  low-privilege component has limited impact. Compromise of
  a high-privilege component is catastrophic.
- Concrete examples:
  DB users per service (read-only user for reporting, write
  only on specific tables for app), IAM roles per Lambda
  function (not "admin" or "full access"), service mesh
  authorization policies (service A can only reach service B's
  specific endpoints, not all of its network).
- Privilege creep: permissions accumulate, annual reviews needed.
  Unused permissions: remove them (AWS IAM Access Advisor shows
  last-used dates).
- JIT access: elevated permissions only when needed, auto-expire,
  every action audited. No standing privilege for production.
- The Equifax connection: the web server shouldn't have had
  access to unrelated databases. Least privilege would have
  contained the breach to the initially compromised web server's
  direct data access only.
