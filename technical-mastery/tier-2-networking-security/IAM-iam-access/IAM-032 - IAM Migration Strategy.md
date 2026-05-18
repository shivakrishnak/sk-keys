---
id: IAM-032
title: "IAM Migration Strategy"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★★
depends_on: IAM-008, IAM-009, IAM-010, IAM-026
used_by: IAM-034
related: IAM-026, IAM-028, IAM-031
tags:
  - iam
  - security
  - migration
  - strategy
  - advanced
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/iam/iam-migration-strategy/
---

⚡ TL;DR - Migrating from legacy IAM (ADFS, custom LDAP,
no SSO) to modern IAM (Okta, Entra ID, Ping Identity)
is a high-risk infrastructure project with a blast
radius equal to every application in the enterprise.
The migration phases: (1) audit current state - all
applications, authentication methods, trust relationships;
(2) stand up new IdP in parallel (never cut over in place);
(3) migrate applications in waves by risk tier (low-risk
internal apps first, SaaS next, critical-path last);
(4) implement SCIM provisioning to replace manual account
management; (5) decommission legacy after all apps migrated
and rollback period expires. Zero-downtime cutover requires
blue-green IdP with dual-IdP federation during transition.
Realistic timeline: 6-18 months for a large enterprise.

---

### 🔥 The Problem This Solves

"Our ADFS cluster is 8 years old, runs on Windows Server
2012, the only engineer who understood it left last year,
and Gartner just said ADFS is end-of-life strategic
direction. We need to migrate to Okta." This conversation
happens in every enterprise. The risks are severe:
botch the migration and every employee cannot log in
to any application. Take too long and the legacy system
fails in production with no fallback.

IAM migration is uniquely dangerous because identity
is a dependency of everything else. It is not like
migrating a database: there, only the applications
using that database are affected. An IAM migration
affects every application that uses identity - which
is every application.

---

### 📘 Textbook Definition

IAM migration is the process of transitioning an
organization's identity and access management
infrastructure from a legacy system (ADFS, custom
LDAP directory, proprietary SSO, or no SSO) to a
modern IAM platform, while maintaining continuous
authentication availability throughout.

**Common migration patterns:**

**ADFS to Entra ID (Microsoft ecosystem):**
On-premises ADFS -> Azure AD Connect -> Entra ID.
Replace SAML/WS-Federation relying parties with
Entra ID application registrations. Existing
on-premises Active Directory remains as user store
initially; sync to cloud via Azure AD Connect.

**Custom LDAP/On-prem to Okta:**
Replace on-premises directory with Okta Universal
Directory. Use Okta AD Agent or LDAP Interface during
migration. SCIM to provision downstream apps.
Migrate SAML SPs to Okta SAML app catalog.

**Legacy SSO (CA SiteMinder, IBM Access Manager)
to modern IdP:**
Header-based authentication proxy apps require
conversion to SAML or OIDC. Often requires app
code changes. Most complex migration type.

**No SSO to SSO:**
Greenfield IdP deployment. No existing trust
relationships to migrate. App-by-app integration
project. Easier than migration but requires business
alignment on which apps are in scope and when.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
IAM migration moves from legacy to modern identity
infrastructure by running both systems in parallel
(blue-green IdP) and migrating applications in waves,
never doing a big-bang cutover.

**One analogy:**
> IAM migration is like replacing a load-bearing wall
> in a house while people are living in it:
>
> - You cannot remove the old wall until the new
>   support structure is fully in place and tested
> - You work room by room (app by app), not all at once
> - Each room gets temporary bracing (dual-IdP federation)
>   before the old wall section is removed
> - Structural engineers (security architects) plan
>   every step before any work begins
> - Emergency rollback plan: the old wall sections
>   are kept on-site until the new structure is
>   certified load-bearing
>
> "Big bang" IAM cutover = removing all load-bearing
> walls simultaneously. Never do this.

---

### 🔩 First Principles Explanation

**The dependency graph problem:**

Before migrating IAM, build a complete dependency map:

```
Application Inventory:
  350 applications total
  - 120: Okta SAML app catalog (pre-built connectors)
  - 80: Custom SAML SP (need individual config)
  - 50: Active Directory integrated (Kerberos/NTLM)
  - 60: No SSO (local accounts only)
  - 40: Custom auth (OAuth 2.0, basic auth, certs)

Authentication dependencies:
  - 50% of apps: ADFS as IdP
  - 30%: Custom LDAP
  - 20%: Application-local auth

Risk tiers:
  - Tier 1 (business critical): 25 apps
    (ERP, payroll, core banking)
  - Tier 2 (business important): 75 apps
  - Tier 3 (low-risk internal): 250 apps
```

**Migrate in reverse risk order:**
Tier 3 first (lowest blast radius), Tier 1 last
(most time to learn, most tested process).

**Zero-downtime IdP strategy:**

During migration, the organization runs two IdPs:
legacy (ADFS/old Okta) and new (Okta/Entra ID).
Applications in Tier 3 trust new IdP.
Applications still in queue trust old IdP.
Bridge: new IdP federates upstream to old IdP
for users not yet migrated. This allows gradual
migration without a flag-day cutover.

---

### 🧪 Thought Experiment

**ADFS to Okta migration - Phase plan:**

```
Phase 0: Discovery and Planning (4-6 weeks)
  Deliverable: Application inventory spreadsheet
    - App name, authentication method, users, risk tier,
      SAML metadata (if applicable), app owner contact
  
  Tools:
    - Microsoft Entra ID Connect Health: ADFS relying party list
    - Okta: Pre-built connectors for 350+ SaaS apps
    - Network scan: discover LDAP consumers
    - Interview app owners for custom auth apps
  
  Decision gate: apps with no app owner -> flag as risk
  Do NOT proceed to Phase 1 until inventory is complete.

Phase 1: New IdP Setup (2-4 weeks)
  - Stand up Okta org (production, not sandbox)
  - Configure Okta AD Agent (sync from existing AD)
    -> Users authenticated by Okta but sourced from AD
    -> No user migration required initially
  - Enable MFA enforcement (starting with IT/security teams)
  - Configure Okta <-> ADFS federation bridge:
      ADFS trusts Okta as additional IdP
      Okta trusts ADFS for legacy app relaying
  
  DO NOT migrate apps yet. IdP is in place, ready.

Phase 2: Wave 1 - Low-Risk Apps (6-8 weeks)
  Scope: 50 internal low-risk apps (wikis, dev tools, HR tools)
  Process per app:
    1. Register app in Okta (SAML metadata exchange)
    2. Test with 5 volunteer users
    3. Migrate app IdP config from ADFS to Okta
    4. 2-week parallel period (ADFS still trusted)
    5. Remove ADFS trust
    6. Document lessons learned
  
  Success metric: < 1 auth failure per 1000 logins
  Rollback: re-add ADFS trust (< 15 minutes)

Phase 3: Wave 2 - SaaS Apps (4-6 weeks)
  Scope: 80 SaaS apps (Salesforce, Jira, Slack, GitHub)
  Most have Okta pre-built connectors
  Configure SCIM provisioning (Okta -> each SaaS app)
  Replace ADFS-based SSO with Okta SSO

Phase 4: Wave 3 - Business Critical Apps (8-12 weeks)
  Scope: 25 Tier 1 apps (ERP, payroll, etc.)
  Additional requirements:
    - Change freeze window: migrate during maintenance
    - Parallel period: 4 weeks (not 2) before removing ADFS
    - Runbook rehearsal: test rollback procedure in staging
    - Executive sign-off required before cutover
    - On-call SRE during cutover weekend

Phase 5: AD-Integrated Apps + Legacy (8-12 weeks)
  - Apps using Kerberos/NTLM -> evaluate options:
      a. Keep AD as auth, Okta as MFA broker
      b. Migrate to modern auth (high effort)
  - Apps with no SSO -> evaluate:
      a. Okta SWA (password vaulting) as interim
      b. App modernization project (long-term)

Phase 6: Decommission (4 weeks)
  - Confirm: 0 apps still trusting ADFS
  - Confirm: Okta is sole IdP for all apps
  - Decommission ADFS servers
  - Keep AD (still user directory for on-premises apps)
```

---

### 🧠 Mental Model / Analogy

> IAM migration is like switching electricity providers
> while keeping your home powered:
>
> - Old utility: runs the current (legacy IdP: ADFS)
> - New utility: ready to provide power (new IdP: Okta)
> - Cannot flip the main switch at once (big bang)
>
> Instead:
> - Room by room: each circuit breaker is per-app
> - Connect room to new utility, test, switch off old
> - Dual power for each room during transition
> - Main house breaker only switched after all rooms done
>
> Emergency plan: old utility stays connected until
> every room is confirmed on new power.
> ADFS stays up until last app is migrated.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
IAM migration moves the login system from old to new.
It must be done gradually, app by app, with the old
system available as fallback, because every employee
login goes through it.

**Level 2 (junior developer):**
During an ADFS-to-Okta migration, developers must
re-configure their application's SAML Service Provider
settings. Change: SAML SSO URL and SAML Issuer (entityID)
from ADFS endpoint to Okta endpoint. Certificate:
import new Okta signing cert. Test in staging before
production cutover. The application code itself
typically does not change - only configuration.

**Level 3 (mid engineer):**
Dual-IdP migration federation: configure Okta to
trust ADFS as a SAML Identity Provider (Okta as SP,
ADFS as IdP). Okta passes authentication to ADFS for
users whose apps are not yet migrated. This enables
a single login experience: user logs into Okta, Okta
federates to ADFS if needed for a legacy app. Users
do not need two logins during migration.

**Level 4 (senior/staff):**
SCIM provisioning cutover during migration: initially,
apps in the new IdP have accounts provisioned manually
(imported from ADFS or AD). After SCIM is configured
and tested, flip to SCIM provisioning. The risk: SCIM
provisioning may have different attribute mappings
than the manual import (email format, group membership,
custom attributes). Before the SCIM cutover, run a
dry-run comparison: SCIM-provisioned attributes vs.
manually provisioned attributes for the same test
users. Any discrepancies = pre-cutover configuration
work.

**Level 5 (distinguished):**
IAM migration project governance: the technical
migration plan is necessary but not sufficient.
The organizational change management required:
(1) App owners must allocate engineer time for SAML
reconfiguration; (2) Business owners must approve
migration windows for Tier 1 apps; (3) Support teams
must be trained on new IdP troubleshooting (Okta
admin console, Okta event logs vs. ADFS trace logs);
(4) Rollback decision authority must be defined in
advance (who can trigger rollback, at what threshold
of auth failures?). Projects fail because of these
organizational dependencies, not the technical ones.
Technical ADFS-to-Okta migration is well-documented.
Getting 25 Tier 1 app owners to schedule their
migration window in the same quarter is the hard part.

---

### ⚙️ How It Works (Mechanism)

```
ADFS to Okta - Technical Cutover per App:

Pre-cutover state:
  App -> ADFS (IdP)
  ADFS -> Active Directory (user store)

Step 1: Register app in Okta
  Okta Admin: Applications -> Add Application
  -> SAML 2.0 template
  IdP: Single Sign-on URL: https://okta.com/.../sso/saml
  SP: ACS URL + EntityID from app's SAML metadata
  Attribute mapping:
    email -> user.email
    firstName -> user.firstName
    department -> user.department

Step 2: Add Okta as trusted IdP in App (parallel)
  App SAML config: add Okta cert as trusted issuer
  App now accepts assertions from: ADFS OR Okta
  Test: can log in via both paths? -> yes

Step 3: Migration weekend
  Friday 17:00: inform users of planned maintenance
  Saturday 02:00-04:00 maintenance window:
    -> Update app SAML IdP URL to Okta endpoint
    -> Remove ADFS as trusted issuer in app
    -> Test: 5 test accounts, all via Okta -> success
    -> Open to general users
  Monitor: Okta system log + app error log for 24h
  Rollback threshold: > 5% auth failure rate -> rollback

Rollback procedure:
  -> Re-add ADFS as trusted issuer in app
  -> Update app SAML IdP URL back to ADFS endpoint
  -> Estimated rollback time: 15 minutes
  -> Decision authority: IAM engineering lead

Post-cutover:
  Day 14: confirm ADFS relying party trust for this app
  still has 0 logins in ADFS audit log
  Day 30: remove ADFS relying party trust for this app
  
ADFS decommission gate:
  Confirm: ADFS relying party count = 0
  Confirm: ADFS audit log shows 0 logins last 30 days
  -> Schedule ADFS server decommission
```

---

### ⚖️ Comparison Table

| Migration Type | Complexity | Timeline | Key Risk |
|:---|:---|:---|:---|
| ADFS -> Entra ID (M365 org) | Medium | 3-9 months | WS-Federation to OIDC conversion for custom apps |
| On-prem LDAP -> Okta | High | 6-12 months | Custom LDAP schema mapping, Kerberos app migration |
| Legacy SSO (SiteMinder) -> Modern IdP | Very High | 12-24 months | Header-injection apps require code changes |
| No SSO -> New IdP | Medium | 6-12 months | App integration effort for each app |
| Okta -> Entra ID (or reverse) | Medium | 6-12 months | App re-registration, SCIM reconfiguration |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "We can migrate ADFS to Okta in a weekend" | Application inventory and wave migration for a large enterprise takes 6-18 months. The ADFS-to-Okta technical steps are fast; the organizational coordination (app owner alignment, maintenance windows, testing) takes months. |
| "Keeping AD means we can keep ADFS-based auth" | AD as a user directory (via Okta AD Agent or Azure AD Connect) is completely separate from ADFS as an authentication IdP. You can replace ADFS (auth) while retaining AD (directory). |
| "SCIM provisioning auto-migrates our users" | SCIM handles ongoing provisioning (new users, updates, deprovisioning). Migrating existing user accounts requires a bulk import operation (CSV import or directory sync), not SCIM. |
| "We can test the migration in a staging environment" | Staging environments rarely have all 350 apps connected. SAML metadata exchanges and app configurations must be tested with the real app (possibly in a test tenant). Budget time for app-level testing that cannot be done in a generic staging environment. |

---

### 🚨 Failure Modes & Diagnosis

**Auth outage during cutover - immediate diagnosis**

```
Symptom: Users cannot log into [App X] after IdP cutover
Error: "SAML Response signature validation failed"

Diagnosis tree:
1. Is the new Okta signing certificate in the app's
   trusted cert list?
   -> App SAML config: check Okta cert fingerprint
      vs. certificate loaded in app trust store

2. Is the SAML issuer URL correct?
   Old: https://adfs.company.com/adfs/services/trust
   New: https://company.okta.com
   -> App SAML config: check entityID/issuer setting

3. Is the ACS URL correct?
   -> Okta app config: check ACS URL matches app

4. Clock skew (SAML assertion time validation fails
   if clocks are more than 5 minutes apart):
   -> Check server time on both Okta and app server
      ntpdate -q 0.pool.ntp.org

Rollback trigger:
  > 10 consecutive auth failures -> trigger rollback
  Rollback time < 15 minutes
  Rollback decision: on-call IAM lead
```

**SCIM provisioning attribute mismatch**

```
Symptom: Users migrated via SCIM cannot access app
Error in app: "User not found" or wrong permissions

Diagnosis:
  Okta SCIM provisioning log:
    Admin -> Applications -> [App] -> Provisioning -> Tasks
    Check last provisioning run -> look for errors
    Common: userName format mismatch
      ADFS: alice.smith
      Okta SCIM: alice.smith@company.com

  App user store: does alice.smith vs alice.smith@company.com
  matter for the app's user lookup?

Fix: adjust SCIM attribute mapping in Okta
  userName -> user.login (Okta login = alice.smith)
  OR
  Update app to accept full email as username

Prevention: run dry-run SCIM provisioning to 10 users
and compare attributes before bulk migration
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-008` - Directory Services: what you are migrating from
- `IAM-009` - SSO Concepts: what you are migrating to
- `IAM-026` - Enterprise IAM Architecture: the target state

**Related:**
- `IAM-028` - Federated Identity at Enterprise Scale
- `IAM-031` - IAM Specification Convergence

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IAM MIGRATION PHASES                                 │
├──────────────────────────────────────────────────────┤
│ 0: DISCOVER   All apps, auth methods, risk tiers     │
│ 1: SETUP      New IdP parallel (never in-place)      │
│ 2: WAVE 1     Low-risk apps first (Tier 3)           │
│ 3: WAVE 2     SaaS apps + SCIM provisioning          │
│ 4: WAVE 3     Business critical apps (Tier 1)        │
│ 5: LEGACY     AD-integrated + no-SSO apps            │
│ 6: DECOMMISSION After all apps migrated + confirmed  │
├──────────────────────────────────────────────────────┤
│ ROLLBACK DESIGN (non-negotiable):                    │
│  Define rollback authority before any cutover        │
│  Rollback < 15 minutes (re-add old IdP trust)        │
│  Trigger threshold: > 5% auth failure rate           │
└──────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"IAM migration (ADFS to Okta/Entra ID) uses a phased,
wave-based approach: audit all apps first, stand up
the new IdP in parallel (never in-place), migrate
Tier 3 apps first and Tier 1 apps last, run dual-IdP
federation during the transition period, and only
decommission legacy after all apps are migrated and
confirmed. Rollback must be < 15 minutes per app.
Timeline for a large enterprise: 6-18 months."

---

### 💎 Transferable Wisdom

IAM migration is a specific instance of the
parallel-run migration pattern: the correct approach
to any infrastructure replacement where continuous
availability is required. The same pattern applies
to: database migrations (run old and new DB in
parallel, dual-write, cutover read traffic, cutover
write traffic, decommission old); Kubernetes version
upgrades (blue-green cluster replacement, not in-place
upgrades for major versions); message queue migrations
(run Kafka and RabbitMQ in parallel, drain RabbitMQ
consumers, decommission after confirmed empty).
The invariant: never do a big-bang in-place cutover
for infrastructure that is a dependency of everything
else. The cost of the parallel period (duplicate
infrastructure costs, extra operational complexity)
is always less than the cost of a failed big-bang
cutover.

---

### ✅ Mastery Checklist

1. **PLAN** Design a wave migration plan for an enterprise
   with 200 applications (30 Tier 1, 70 Tier 2, 100 Tier 3)
   moving from ADFS to Okta. Define: phase structure,
   success criteria per wave, rollback procedure, and
   ADFS decommission criteria.

2. **DIAGNOSE** After an app cutover from ADFS to Okta,
   users report intermittent SAML authentication failures
   (1 in 10 logins fail). The error is "SAML assertion
   not yet valid." Identify the root cause, the specific
   SAML field involved, and the fix.

3. **GOVERN** What organizational (non-technical)
   blockers most commonly delay IAM migration projects?
   Describe the governance structure (steering committee,
   RACI, decision authorities) needed to complete a
   large enterprise IAM migration on schedule.

---

*Identity & Access Management | IAM-032 | v5.0*