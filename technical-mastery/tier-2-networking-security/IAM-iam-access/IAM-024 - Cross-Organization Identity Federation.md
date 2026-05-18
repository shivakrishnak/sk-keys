---
id: IAM-024
title: "Cross-Organization Identity Federation"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-009, IAM-010, IAM-014
used_by: IAM-028, IAM-031
related: IAM-010, IAM-014, OAU-005
tags:
  - iam
  - security
  - identity
  - federation
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/iam/cross-organization-identity-federation/
---

⚡ TL;DR - Cross-organization identity federation allows
users from Organization A to authenticate using their
Organization A credentials to access resources in
Organization B - without creating accounts in B's
directory. Federation standards: SAML 2.0 (enterprise
SSO, established), OIDC (modern, API-friendly), WS-Federation
(legacy Microsoft). Trust is established via metadata
exchange (IdP publishes metadata; SP imports it).
Use cases: B2B SaaS vendor access, partner portal
access, M&A identity integration, contractor access
from partner organizations.

---

### 🔥 The Problem This Solves

Company A (Acme Corp) partners with Company B (Globex)
on a joint project. Globex engineers need access to
Acme's project collaboration tools. Without federation:

- Acme creates guest accounts for each Globex engineer
- Acme IT manages password resets for Globex employees
  (who don't remember their Acme passwords)
- Globex employees have two separate identities:
  Globex corporate and Acme guest account
- When the project ends, Acme IT must manually revoke
  all Globex guest accounts (often forgotten)

With federation:
- Globex engineers log in with their Globex corporate
  credentials
- Globex's IdP vouches for the identity to Acme's SP
- Account lifecycle is managed by Globex:
  when a Globex engineer leaves, their Globex account
  is deprovisioned, and they automatically lose Acme access

---

### 📘 Textbook Definition

Cross-organization identity federation is the
configuration of trust relationships between separate
organizations' identity systems, enabling users from
one organization's IdP (the home organization) to
authenticate and access resources at another
organization's SP (the partner organization) without
requiring separate account creation.

**Federation trust model:**

**Bilateral (point-to-point):** Org A trusts Org B's
IdP. Org B configures Org A's SP. Direct metadata
exchange between two parties. Simple but scales poorly
(N-org federation requires N*(N-1) bilateral relationships).

**Hub-and-spoke (Identity Broker):** All organizations
trust a central identity broker (hub). Users authenticate
to the hub, which translates and proxies assertions to
target SPs. One configuration per organization.
Examples: InCommon (higher education), eduGAIN
(research federations), identity broker products.

**Circle of Trust (CoT):** Multiple organizations
agree to trust a shared metadata aggregate. Each member
publishes its metadata to the aggregate; all members
trust the aggregate. Scales better than bilateral.
Used in enterprise identity federations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cross-org federation lets Globex employees log into
Acme's systems using their Globex passwords, with
Globex's identity system vouching for them.

**One analogy:**
> International driving license recognition:
>
> - Driver's license issued by UK (home org/IdP)
> - Country B (partner org/SP) recognizes UK licenses
>   (established trust via international agreement)
> - UK citizen can drive in Country B without getting
>   a local license (no account creation in B)
> - If UK revokes the license: automatic in Country B
>   (account lifecycle managed by home org)
>
> Trust framework:
> - Formal agreement between UK and Country B
>   (metadata exchange / SAML trust establishment)
> - Country B verifies UK license format/signature
>   (IdP metadata: signing certificate, issuer)

**One insight:**
Cross-org federation solves the account proliferation
problem: without federation, each B2B relationship
creates a new population of guest accounts in each
organization's directory. With federation, identity
remains in the home organization. This is also a
security benefit: when an employee leaves Organization A,
deprovisioning in A automatically revokes access to
all federated SPs without any action from the SP organizations.

---

### 🔩 First Principles Explanation

**The trust establishment problem:**

Federation requires trust: how does Acme know that
a SAML assertion claiming "user is alice@globex.com"
actually came from Globex's IdP and was not forged?

The answer is pre-established cryptographic trust:
1. Globex's IdP publishes metadata including its
   signing certificate's public key
2. Acme imports this metadata into its SP configuration
3. When Acme receives a SAML assertion claiming to
   be from Globex's IdP, it verifies the signature
   using the pre-imported public key
4. Valid signature = assertion genuinely from Globex's IdP

This is a one-time, out-of-band trust establishment:
both parties exchange metadata (usually a URL pointing
to the IdP metadata XML). After this, assertions can
flow without further coordination.

**Attribute mapping challenge:**

Globex's IdP sends user attributes in Globex's schema:
{globexId: "AG-12345", givenName: "Alice", dept: "ENG-EU"}.
Acme's SP expects: {username: "alice@globex.com", groups: "engineering"}.

Attribute mapping is required: either at the IdP
(Globex configures which attributes to release and
in what format) or at the SP (Acme maps incoming
attributes to its own schema). Attribute mapping
mismatches are the #1 cause of federation integration
failures. Standardized attribute schemas (SAML Core,
OIDC standard claims) reduce this problem.

---

### 🧪 Thought Experiment

**B2B SaaS with multi-tenant federation:**

```
Your SaaS product has 50 enterprise customers.
Each wants to use their own corporate SSO.

Architecture: CIAM with SAML federation hub

Customer A (Acme, Azure AD):
  - Registers your app in Azure AD as SAML Enterprise App
  - Provides: entityId, signing cert, SSO endpoint URL
  - Your CIAM: imports Acme's IdP metadata
  - Maps: Acme's azureADGroups attribute -> your product roles

Customer B (Globex, Okta):
  - Registers your app in Okta
  - Provides: entityId, signing cert, SSO endpoint URL
  - Your CIAM: imports Globex's IdP metadata
  - Maps: Globex's groups attribute -> your product roles

User flow (Acme employee):
  1. Opens your SaaS app: app.yourproduct.com
  2. Enter email: alice@acme.com
  3. App: email domain = acme.com -> route to Acme tenant
  4. SP-initiated SAML flow: redirect to Azure AD
  5. Alice authenticates with Acme MFA
  6. Azure AD issues SAMLResponse (claims: alice's groups)
  7. Your SP validates, maps groups to product roles
  8. Alice is in your product as an Acme tenant user

User flow (Globex employee):
  Same flow, routed to Okta federation instead of Azure AD
  No Globex account in your SaaS user database

Scale:
  50 customers = 50 federation configurations
  Auth0 Organizations / Okta Customer Identity
  manage these as separate tenant configs
  No code change per new customer federation
```

---

### 🧠 Mental Model / Analogy

> Cross-org federation is like a university ID system
> for consortium libraries:
>
> - Harvard (home org/IdP) issues student IDs
> - All consortium libraries (partner SPs) trust Harvard IDs
> - Trust established via consortium agreement
>   (metadata exchange)
> - Harvard student walks into MIT library:
>   scans Harvard ID -> MIT library system:
>   - Validates Harvard ID format and signature
>   - Grants library access (per consortium policy)
> - When student graduates: Harvard deactivates ID
>   -> MIT library access automatically revoked
>   -> No MIT IT action required

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Cross-org federation lets employees from Company B
log in to Company A's systems using Company B's login,
without Company A creating separate accounts for them.

**Level 2 (junior developer):**
Setting up SAML federation with a partner organization:
1. Get the partner IdP's metadata XML (URL or file)
2. Import into your SP (configure entityID, SSO endpoint,
   signing certificate)
3. Register your SP with the partner IdP
   (provide your entityID, ACS URL)
4. Map the partner's user attributes to your application's
   user model
5. Test with SAML-tracer or samltool.com

**Level 3 (mid engineer):**
OIDC cross-org federation via identity broker: instead
of SAML bilateral, configure your application as an
OIDC Relying Party (RP) to an identity broker (Okta,
Auth0). The identity broker handles SAML/OIDC federation
with each partner organization. Your application
only speaks OIDC to the broker. The broker manages
all partner federation configurations. This abstraction
reduces your integration complexity: N partner federations
= one broker + N broker federation configurations
(not N application-level integration changes).

**Level 4 (senior/staff):**
SAML federation key rotation at scale: when a partner
IdP rotates its signing key, all SPs that have imported
the old certificate must update their configuration.
If the partner IdP publishes metadata at a well-known
URL, SPs that poll this URL can auto-update.
If not, the rotation requires manual coordination:
partner sends new metadata, you update your SP config.
Key rotation outage window: typically a few minutes
of assertion rejection (signature validation fails with
old key) until all SPs update. Mitigation: partner
publishes BOTH old and new key in metadata during transition
period; your SP tries both keys until the old one expires.

**Level 5 (distinguished):**
Large-scale identity brokering (higher education InCommon):
InCommon federation has 1200+ member organizations
(universities, research institutions). Each member
publishes its IdP or SP metadata to the InCommon
aggregate. All members import the aggregate: one import,
1200+ trusted organizations. When a researcher at
Stanford accesses a resource at MIT:
1. MIT SP consults InCommon aggregate: Stanford IdP metadata
2. Stanford IdP authenticates researcher
3. SAMLResponse validated using Stanford's key from aggregate
4. No bilateral coordination between Stanford and MIT
This model scales to thousands of organizations - impossible
with bilateral point-to-point federation.

---

### ⚙️ How It Works (Mechanism)

```
SAML Cross-Organization Federation Setup:

Step 1: IdP (Globex, Okta) publishes metadata:
  GET https://globex.okta.com/app/saml/sso/metadata
  Returns XML with:
  - entityID: https://globex.okta.com
  - SSO URL: https://globex.okta.com/app/.../sso/saml
  - X.509 signing cert (base64)

Step 2: SP (Acme) imports Globex metadata:
  In Acme's IAM system (Auth0/Okta/custom SAML SP):
  POST /idp/configure
  {
    "entityId": "https://globex.okta.com",
    "ssoUrl": "https://globex.okta.com/app/.../sso/saml",
    "certificate": "MIIDpDCCAoygAwIBAgI...",
    "attributeMapping": {
      "globexUserId": "sub",
      "globexEmail": "email",
      "globexGroups": "roles"
    }
  }

Step 3: Globex registers Acme SP:
  In Globex's Okta: add SAML application
  - SP entity ID: https://acme.com/saml/sp
  - ACS URL: https://acme.com/saml/acs
  - Attribute statements:
    globexUserId -> user.login
    globexEmail -> user.email
    globexGroups -> appuser.groups

Authentication flow:
  1. Globex user navigates to acme.com/app
  2. Acme SP: unknown user, route to federation login
  3. User enters alice@globex.com
  4. Acme SP: email domain = globex.com
     -> AuthnRequest to Globex Okta SSO URL
  5. Globex Okta: authenticate alice (Globex MFA)
  6. Globex Okta: issue SAMLResponse signed with Globex cert
  7. Acme SP: validate signature with Globex cert from metadata
  8. Acme SP: map attributes, create/update user session
  9. Alice accesses Acme app - no Acme password required
```

---

### ⚖️ Comparison Table

| Federation Model | Complexity | Scale | Best For |
|:---|:---|:---|:---|
| Bilateral SAML/OIDC | Per-partnership setup | Low (N*(N-1)) | Small # of partners |
| Identity Broker | Medium (one broker config) | High (N+1) | SaaS with many customers |
| Federation Aggregate (InCommon) | Medium (join process) | Very high (1000+ orgs) | Higher ed, research |
| Azure B2B | Low (invitation-based) | Medium | Microsoft-ecosystem partners |
| JIT Provisioning | Low (per-federation rule) | Medium | B2B with diverse IdPs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "Federation creates guest accounts" | JIT provisioning creates local profile records (for RBAC), but these are shadow accounts synced from the partner IdP - not independent accounts with separate passwords. The authoritative identity stays in the home IdP. |
| "OIDC is always better than SAML for federation" | OIDC is better for modern apps. For enterprise customers who only support SAML (legacy SaaS, on-prem systems), SAML is required. Identity brokers handle both, exposing OIDC outward while speaking SAML to legacy partners. |
| "Federation solves authorization" | Federation handles authentication only: "is this person who they claim to be?" Authorization ("what can this person do?") must be configured separately, typically via group/role attribute mapping from the partner IdP. |
| "Metadata once = forever" | Metadata contains certificates and endpoints that change. IdPs rotate certificates; endpoints may change with upgrades. Poll metadata URLs periodically to detect changes before they cause outages. |

---

### 🚨 Failure Modes & Diagnosis

**Certificate rotation breaks federation**

```bash
# Partner IdP rotated their signing cert
# All their users get signature validation failure on your SP

# Verify: decode the incoming SAMLResponse assertion
echo "$SAML_RESPONSE" | base64 -d | xmllint --format - | \
  grep -A5 "ds:X509Certificate"
# Compare the cert fingerprint in the assertion vs
# what your SP has configured

# Get the partner's new metadata:
curl https://partner.okta.com/saml/metadata | xmllint --format -
# Look for the new KeyDescriptor in the metadata

# Update your SP with the new certificate
# If partner published dual-key metadata during transition:
# your SP should try both keys on validation

# Prevention: subscribe to partner's maintenance notifications
# Auto-poll: set SP metadata refresh interval to 24h
```

**Attribute mapping failure: user gets wrong role**

```bash
# User from partner org logs in successfully but
# gets default (minimal) access instead of expected role

# Decode SAMLResponse to check attributes:
echo "$SAML_RESPONSE" | base64 -d | xmllint --format - | \
  grep -A3 "saml:AttributeStatement"
# Check what attributes the partner IdP is actually sending
# vs what your attribute mapping expects

# Common issues:
# - Attribute Name format mismatch
#   (partner sends: urn:oid:1.3.6.1.4.1... your rule expects: groups)
# - Groups not included (not configured in partner IdP)
# - Value format difference (string vs array)

# Fix: update attribute mapping in your SP config
# or ask partner IdP admin to adjust attribute release policy
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-009` - Single Sign-On Concepts
- `IAM-010` - Identity Federation Basics
- `IAM-014` - SAML 2.0 and Enterprise SSO

**Builds On This:**
- `IAM-028` - Federated Identity at Enterprise Scale
- `IAM-031` - IAM Specification Convergence

**Related:**
- `IAM-010` - Identity Federation Basics: concepts
- `OAU-005` - OIDC: OIDC as alternative to SAML for federation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ CROSS-ORG FEDERATION CHECKLIST                       │
├────────────────────────────────────────────────────── ┤
│ 1. Exchange IdP metadata (URL or XML file)           │
│ 2. Map partner attributes to your user model         │
│ 3. Configure JIT provisioning rules (auto-create     │
│    shadow profile on first login)                    │
│ 4. Configure access policies for partner users       │
│    (which apps/roles they get)                       │
│ 5. Test with SAML-tracer or samltool.com             │
│ 6. Schedule metadata polling (daily refresh)         │
│ 7. Deprovisioning: confirm auto-revoke on partner    │
│    IdP deactivation (test it!)                       │
└──────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"Cross-org federation lets users from Organization A
authenticate to Organization B's resources using A's
credentials. Trust is established via metadata exchange
(IdP publishes metadata; SP imports cert and SSO endpoint).
SAML 2.0 is the enterprise standard; OIDC for modern
apps. JIT provisioning creates shadow profiles on first
login; account lifecycle remains in the home organization."

---

### 💎 Transferable Wisdom

Cross-org federation solves the account proliferation
problem by keeping authoritative identity in the home
system while delegating authentication proofs via
cryptographic assertions. The same "delegate proof,
not credentials" pattern appears in: certificate pinning
(trust the cert, not the domain name system), code
signing (trust the publisher's signature, not the
download URL), and API key rotation (trust the key
at validation time, not at distribution time). The
common principle: move trust to verifiable proofs
(cryptographic signatures on assertions) rather than
shared secrets distributed to every relying party.

---

### ✅ Mastery Checklist

1. **CONFIGURE** Walk through the complete SAML
   federation setup between a partner organization's
   Okta IdP and your application's SP. Include all
   required configuration steps on both sides and the
   expected behavior for a user's first login via JIT
   provisioning.

2. **DIAGNOSE** A partner organization rotated their
   SAML signing certificate. Your application is
   rejecting all their users' assertions with "invalid
   signature." Describe the resolution steps and how
   to prevent this outage in future certificate rotations.

3. **ARCHITECT** You are building a B2B SaaS with 100
   enterprise customers, each requiring corporate SSO
   federation. Compare a bilateral SAML integration
   approach vs. an identity broker approach. Which
   would you choose and what are the operational
   considerations?

---

*Identity & Access Management | IAM-024 | v5.0*