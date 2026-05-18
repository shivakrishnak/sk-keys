---
id: IAM-004
title: "The IAM Landscape (Tools, Standards, Vendors)"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-001, IAM-002, IAM-003
used_by: IAM-008, IAM-015, IAM-019
related: IAM-005, OAU-001, ATH-001
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
nav_order: 4
permalink: /technical-mastery/iam/the-iam-landscape-tools-standards-vendors/
---

⚡ TL;DR - The IAM ecosystem spans five layers: protocols
(OAuth, OIDC, SAML, SCIM, LDAP), identity providers (Okta,
Auth0, Azure AD, Keycloak), access management platforms
(AWS IAM, GCP IAM, Azure RBAC), privileged access tools
(CyberArk, BeyondTrust), and governance tools (SailPoint,
Saviynt). Understanding which layer a tool lives in prevents
the common mistake of conflating an IdP with a PAM tool.

---

### 🔥 The Problem This Solves

New engineers encounter "IAM" and face a wall of acronyms:
Okta, LDAP, SAML, OAuth, Azure AD, SailPoint, CyberArk,
Keycloak, AWS IAM. Are these competing products? Layers of
a stack? Substitutes or complements? Without a mental map
of the landscape, engineers:

- Deploy Okta for SSO and then wonder why AWS resource
  access still needs separate configuration (different
  layer: Okta handles authentication; AWS IAM handles
  cloud resource authorization)

- Use OAuth 2.0 for user login when they need OIDC
  (OAuth alone has no identity layer)

- Buy a PAM tool thinking it replaces their IdP (it
  manages privileged credentials, not user identity)

The IAM landscape is fragmented by historical evolution.
Understanding the five layers maps each tool to its problem.

---

### 📘 Textbook Definition

The IAM landscape is organized into five functional layers:

**Layer 1 - Protocols and Standards:** The open
specifications tools implement. OAuth 2.0 (authorization
delegation), OIDC (identity on top of OAuth), SAML 2.0
(enterprise SSO assertions), LDAP (directory protocol),
SCIM (provisioning protocol), FIDO2 (passwordless
authentication), Kerberos (network authentication).

**Layer 2 - Identity Providers (IdP):** Systems that
authenticate users and issue identity assertions. Okta,
Auth0, Microsoft Azure AD / Entra ID, Google Workspace,
Ping Identity, AWS Cognito (consumer), Keycloak
(open source self-hosted).

**Layer 3 - Cloud IAM Platforms:** Cloud-native access
management for cloud resources. AWS IAM (policies,
roles, service accounts), GCP IAM (service accounts,
project-level bindings), Azure RBAC (role assignments
on resource groups). These are access control systems
for cloud APIs, not general IdPs.

**Layer 4 - Privileged Access Management (PAM):** Tools
managing high-privilege credentials (root, admin,
service passwords). CyberArk, BeyondTrust, Delinea
(Thycotic/Centrify). PAM vaults secrets, enforces
just-in-time access to admin accounts, and records
all privileged session activity.

**Layer 5 - Identity Governance and Administration (IGA):**
Tools automating the identity lifecycle: access
certifications, role mining, segregation-of-duty
enforcement. SailPoint, Saviynt, Omada. IGA orchestrates
joiners/movers/leavers workflows and produces audit
reports for SOC 2 / ISO 27001 compliance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The IAM landscape has five layers: protocols (how),
identity providers (who proves who they are), cloud IAM
(what cloud resources are accessible), PAM (who has
privileged access), and IGA (who should have access
and is the audit correct).

**One analogy:**
> A hospital's physical security works in the same five
> layers: security standards (fire codes, regulations),
> the front desk that checks IDs (IdP), the door access
> system for each floor (cloud IAM), the pharmacy key
> safe for controlled substances (PAM), and the admin
> office that reviews who has which keys quarterly (IGA).
> Each is a different department with different tools -
> yet all together form the hospital's access control.

**One insight:**
Most small teams need layers 1 + 2 only. Enterprises need
all five. PAM and IGA are often absent until a breach or
compliance audit forces the investment.

---

### 🔩 First Principles Explanation

The fragmentation of the IAM landscape follows from
the fragmented history of computing access control:

- **LDAP/Kerberos (1990s):** enterprise directories
  for on-premises networks. Built for corporate LAN.

- **SAML (2002):** cross-organizational browser-based
  SSO for enterprise web apps. XML-based, verbose,
  built for enterprises.

- **OAuth 2.0 / OIDC (2006/2014):** web and mobile
  authorization delegation. JSON-based, built for
  the web API era. OIDC added identity on top of OAuth.

- **SCIM (2015):** automated provisioning protocol.
  Built because every SaaS app had a different user
  import API.

- **FIDO2/WebAuthn (2019):** passwordless authentication.
  Built because passwords are the weakest link.

Each standard solved the pain of its era. Today, a
modern enterprise uses all of them simultaneously
because they target different scenarios, not because
of poor design.

---

### 🧪 Thought Experiment

**Company of 500 employees uses Office 365 and AWS:**

- **Layer 1 (protocols):** SAML for Office 365 SSO,
  OIDC for web apps, SCIM for automated user provisioning,
  LDAP for legacy apps.

- **Layer 2 (IdP):** Microsoft Entra ID authenticates all
  users. Issues SAML assertions for Office 365. Issues
  OIDC tokens for modern web apps.

- **Layer 3 (Cloud IAM):** AWS IAM controls which teams
  can access which AWS accounts. Engineers assume an IAM
  role (DevRole or ProdReadRole) via SAML federation with
  Entra ID - the user authenticates once to Entra,
  exchanges a SAML assertion for an AWS STS session.

- **Layer 4 (PAM):** CyberArk vaults the root AWS
  account credentials and all server admin passwords.
  Engineers request just-in-time access; CyberArk
  records the session.

- **Layer 5 (IGA):** SailPoint runs quarterly access
  reviews. Managers certify their team's access.
  Orphaned accounts from departures are auto-detected.

None of these five layers is redundant. Remove any one
and a compliance gap or attack surface opens.

---

### 🧠 Mental Model / Analogy

> The IAM landscape is like transportation infrastructure:
>
> - **Protocols** = road standards (lane width, traffic
>   signs, rules of the road)
> - **IdP** = passport and immigration control (who you are)
> - **Cloud IAM** = building access systems in each city
>   (what you can enter per location)
> - **PAM** = secure vault access for restricted areas
>   (controlled substances, weapon storage)
> - **IGA** = the transport ministry's audit department
>   (who has which licenses, are they still valid)
>
> The rules of the road (protocols) apply everywhere.
> Passport control is done once. Building access is
> managed per building. The vault has the highest control.
> The ministry audits it all.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
There are apps that verify who you are (IdPs like Google
or Okta), cloud systems that control what you can do in
AWS or Azure, special vaults for the most powerful admin
passwords (PAM), and governance tools that audit who has
what access (IGA). They use common protocols to talk.

**Level 2 (junior developer):**
For a web app: use an IdP (Auth0 or Keycloak) for
authentication with OIDC/OAuth. The IdP issues a JWT.
Your backend validates the JWT and checks user roles
(local authorization). You do not need cloud IAM or PAM
for a basic web app.

**Level 3 (mid engineer):**
Enterprise systems integrate IdP with cloud IAM via
SAML federation: users log in to the corporate IdP
(Okta/Entra), exchange the SAML assertion for cloud
provider credentials (AWS STS AssumeRoleWithSAML,
GCP workload identity). SCIM keeps user accounts
synchronized between the IdP and downstream SaaS apps
automatically.

**Level 4 (senior/staff):**
Cloud-native architectures use workload identity
(Layer 3 cloud IAM) extensively. Kubernetes pods get
service accounts that bind to cloud IAM roles (AWS
IRSA, GCP Workload Identity). No static credentials;
credentials are issued just-in-time by the cloud
metadata service. PAM becomes critical when any human
admin access to production must be time-boxed, recorded,
and auditable.

**Level 5 (distinguished):**
At large enterprise scale, the five layers overlap and
create governance challenges. Identities exist in
multiple directories (LDAP, Entra, AWS IAM, GCP IAM);
IGA must reconcile them all. Shadow IT creates rogue
IdPs and ungoverned OAuth apps. Zero Trust Architecture
(NIST SP 800-207) addresses this by treating every
request as untrusted regardless of network origin -
every access decision goes through the IAM stack even
inside the corporate network.

---

### ⚙️ How It Works (Mechanism)

```
Five-layer IAM stack interaction:

User logs in -> [LAYER 2: IdP authenticates]
    Okta verifies username + MFA
    Issues OIDC id_token + access_token (LAYER 1: OIDC protocol)

User accesses cloud resource -> [LAYER 3: Cloud IAM]
    SAML assertion from Okta -> AWS STS AssumeRoleWithSAML
    AWS returns temporary credentials (access key, secret, token)
    User's code calls AWS API with temporary credentials
    AWS IAM policy evaluated per API call

Admin needs root access -> [LAYER 4: PAM]
    Request submitted to CyberArk for just-in-time elevation
    Session recorded, time-limited credential issued
    Session video replay available for audit

Quarterly audit -> [LAYER 5: IGA]
    SailPoint queries all layers for current access state
    Managers receive certification tasks
    Orphaned/excessive access flagged for removal
    Audit report generated for SOC 2 audit

Protocol layer [LAYER 1] is used throughout:
  LDAP: directory queries
  SAML: enterprise SSO assertions
  OIDC: web app authentication
  SCIM: automated user sync between IdP and SaaS apps
  FIDO2: passwordless authentication at the IdP level
```

---

### ⚖️ Comparison Table

| Layer | Problem Solved | Key Tools | Protocol |
|:---|:---|:---|:---|
| Protocols / Standards | Interoperability between systems | N/A (standards bodies) | OAuth, OIDC, SAML, SCIM, LDAP |
| Identity Provider (IdP) | Authenticate users, issue tokens | Okta, Entra ID, Auth0, Keycloak | OIDC, SAML, LDAP |
| Cloud IAM | Authorize cloud resource access | AWS IAM, GCP IAM, Azure RBAC | Cloud-specific + SigV4/Bearer |
| PAM | Manage privileged/admin credentials | CyberArk, BeyondTrust, Delinea | LDAP + vendor-specific |
| IGA | Govern identity lifecycle + audit | SailPoint, Saviynt, Omada | SCIM + vendor-specific |

**Build vs Buy guidance:**

- **IdP:** Almost always buy (Okta/Auth0/Entra) unless
  you are building an IdP product. Rolling your own
  authentication is a security anti-pattern.

- **Cloud IAM:** Use the cloud provider's native IAM.
  Do not build your own cloud resource authorization.

- **PAM:** Buy at enterprise scale. At startup scale,
  a secrets manager (HashiCorp Vault, AWS Secrets
  Manager) covers the most critical use cases.

- **IGA:** Only needed at 500+ employees or for
  SOC 2 Type II / ISO 27001 compliance.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Okta IS IAM | Okta is an IdP (Layer 2). It handles authentication and SSO. It does not manage AWS resource policies (Layer 3) or vault privileged credentials (Layer 4). |
| AWS IAM = enterprise IAM | AWS IAM manages access to AWS APIs and resources. It is not a general-purpose IdP for user authentication in your applications. |
| OAuth is secure authentication | OAuth 2.0 is authorization delegation. It was never designed to authenticate users. Use OIDC for user authentication. |
| "Just use Active Directory for everything" | Active Directory is excellent for on-premises Windows environments. It is not designed for cloud-native workloads, mobile apps, or API authorization at scale. |

---

### 🚨 Failure Modes & Diagnosis

**Wrong tool for the job: using IdP as a policy engine**

**Symptom:** Fine-grained authorization logic embedded
in Okta groups ("okta-group-can-view-invoices-over-10k").
Group explosion: hundreds of Okta groups representing
application permissions.

**Root Cause:** Using the IdP (Layer 2) to manage
application authorization (should be Layer 3 / policy
engine). Okta groups should map to job functions, not
application-specific permissions.

**Fix:** Move fine-grained authorization to a policy
engine (OPA) or the application layer. Keep Okta groups
at the role/department level (coarse-grained identity).

---

**SCIM not configured: manual provisioning gap**

**Symptom:** New hire cannot access Salesforce, GitHub,
Jira, Slack for the first day. IT helpdesk must manually
create accounts in each SaaS app.

**Root Cause:** IdP (Okta/Entra) not connected to SaaS
apps via SCIM. No automated provisioning.

**Diagnosis:**
```bash
# Verify SCIM is configured for a SaaS app in Okta
# In Okta admin console: Applications -> App -> Provisioning
# Check: Import Users = enabled, Create Users = enabled

# Test SCIM provisioning endpoint directly
curl -H "Authorization: Bearer $SCIM_TOKEN" \
  https://app.example.com/scim/v2/Users
```

**Fix:** Enable SCIM provisioning in both the IdP and
the SaaS app. Define provisioning rules (who gets which
app automatically on hire).

---

### 🔗 Related Keywords

**Prerequisites:**

- `IAM-001` - The Identity Problem: why IAM exists
- `IAM-002` - What IAM Actually Manages: the six objects
- `IAM-003` - Authentication vs Authorization vs Identity

**Builds On This:**

- `IAM-008` - Directory Services: LDAP and Active Directory detail
- `IAM-015` - Cloud IAM: AWS, GCP, Azure deep dive
- `IAM-019` - Identity Governance and Administration (IGA)

**Related:**

- `OAU-001` - OAuth 2.0 Basics: the authorization protocol
- `ATH-014` - SAML 2.0: the enterprise SSO standard
- `IAM-016` - Privileged Access Management: PAM detail

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ IAM LANDSCAPE - FIVE LAYERS                            │
├──────────────────┬─────────────────────────────────────┤
│ PROTOCOLS        │ OAuth, OIDC, SAML, SCIM, LDAP, FIDO2│
│ (standards)      │ Interoperability layer              │
├──────────────────┼─────────────────────────────────────┤
│ IDENTITY         │ Okta, Entra ID, Auth0, Keycloak     │
│ PROVIDER (IdP)   │ Authenticates, issues tokens        │
├──────────────────┼─────────────────────────────────────┤
│ CLOUD IAM        │ AWS IAM, GCP IAM, Azure RBAC        │
│                  │ Authorizes cloud resource access    │
├──────────────────┼─────────────────────────────────────┤
│ PAM              │ CyberArk, BeyondTrust, Delinea      │
│ (privileged)     │ Vaults and governs admin access     │
├──────────────────┼─────────────────────────────────────┤
│ IGA              │ SailPoint, Saviynt, Omada           │
│ (governance)     │ Lifecycle, certification, audit     │
└──────────────────┴─────────────────────────────────────┘

Rule: "Buy, don't build" for IdP. Build for authz logic.
```

**If you remember 3 things:**

1. Five layers: protocols, IdP, cloud IAM, PAM, IGA.
   Each solves a different problem. None is a substitute
   for the others.

2. Never build your own IdP. Buy Okta/Auth0/Keycloak.
   Rolling auth is where security disasters start.

3. OAuth 2.0 alone is not authentication. Add OIDC.

**Interview one-liner:**
"The IAM landscape has five layers: standards/protocols,
identity providers, cloud IAM platforms, privileged access
management, and identity governance - each solving a
different part of the access control problem."

---

### 💎 Transferable Wisdom

**Reusable Principle:**
Mature technology domains always stratify into protocol
layers (interoperability), infrastructure layers (shared
services), and governance layers (audit/compliance). The
IAM landscape stratification is the same pattern as
networking (L1-L7 OSI model) or cloud computing
(IaaS/PaaS/SaaS). Recognizing the layer prevents
misapplying tools across them.

**Where else this appears:**

- Network security: protocols (TLS, IPSec), firewalls
  (infrastructure), SIEM (governance). Same five-layer
  shape - different domain.

- Data governance: SQL/API standards (protocols), cloud
  data platforms (infrastructure), data catalog + data
  lineage tools (governance).

---

### 💡 The Surprising Truth

The IAM landscape is fragmented because identity was
never designed to be a platform - it grew as a side
effect of every application solving its own access
control independently. LDAP was invented for directory
lookups, not SSO. OAuth was invented for Twitter third-
party apps, not enterprise authentication. SAML was
designed for browser-based enterprise SSO in 2002
before mobile apps existed. The modern enterprise using
all five layers simultaneously is not over-engineered -
it is the result of 40 years of access control evolution
where each protocol solved the problem of its era.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**

1. **MAP** Given a tool (CyberArk, SailPoint, Okta,
   AWS IAM, LDAP), identify which of the five IAM
   layers it belongs to and what problem it solves.

2. **DECIDE** A startup with 50 engineers needs to
   handle login, AWS access, and offboarding. Which
   two or three layers do they actually need right
   now vs what they need at 500 employees?

3. **EXPLAIN** Why a company with Okta still needs
   AWS IAM configuration, and why those two systems
   are complementary rather than redundant.

---

*Identity & Access Management | IAM-004 | v5.0*