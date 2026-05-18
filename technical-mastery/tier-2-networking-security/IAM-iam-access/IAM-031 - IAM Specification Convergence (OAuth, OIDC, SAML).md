---
id: IAM-031
title: "IAM Specification Convergence (OAuth, OIDC, SAML)"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★★
depends_on: IAM-009, IAM-010, IAM-014
used_by: IAM-026, IAM-034
related: IAM-014, OAU-001, OAU-011
tags:
  - iam
  - security
  - oauth
  - oidc
  - saml
  - protocols
  - advanced
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/iam/iam-specification-convergence/
---

⚡ TL;DR - OAuth 2.0, OIDC, SAML 2.0, and SCIM are
four complementary identity specifications that cover
different planes: OAuth 2.0 is delegated authorization
(access tokens for APIs); OIDC is authentication
built on OAuth 2.0 (ID tokens, userinfo); SAML 2.0 is
enterprise SSO using XML assertions (legacy app
integration); SCIM is identity provisioning (create/
update/delete users across systems). Modern IAM
platforms (Okta, Entra ID, Ping Identity) implement
all four simultaneously: OIDC for consumer/developer
apps, SAML for enterprise apps, SCIM for provisioning,
and OAuth 2.0 for API authorization. The convergence
is in the Identity Provider (IdP) - one system that
speaks all protocols toward a unified identity store.

---

### 🔥 The Problem This Solves

An enterprise has 300 applications: 50 legacy
enterprise apps (SAP, Workday, Salesforce) that speak
SAML; 100 modern web and mobile apps that use OIDC;
150 internal microservices that use OAuth 2.0 for
API-to-API authorization; and a HR system that needs
to provision users via SCIM. The question is: does
this require four different identity systems? No - one
converged IAM platform (Okta, Entra ID, Ping) is the
single Identity Provider that speaks all four protocols.
Understanding which protocol to use for which scenario,
and how they interact, is core IAM architecture knowledge.

---

### 📘 Textbook Definition

**Four specifications, four problems:**

**OAuth 2.0 (RFC 6749):**
Framework for delegated authorization. A user
(resource owner) grants a client application limited
access to a resource server, mediated by an
Authorization Server. Issues access tokens (opaque
or JWT). Does NOT define authentication - only
authorization delegation. Questions answered:
"Can this app access this API on behalf of this user?"

**OpenID Connect 1.0 (OIDC):**
Authentication layer on top of OAuth 2.0. Adds an
ID Token (JWT with user identity claims: sub, email,
name, iss, aud, exp). Also defines the UserInfo
endpoint (GET /userinfo with access token -> returns
user claims). Questions answered: "Who is this user?
Are they authenticated?" Uses OAuth 2.0 flows
(Authorization Code, Implicit deprecated, PKCE).

**SAML 2.0 (OASIS standard):**
XML-based federation protocol for enterprise SSO.
Defines three roles: Identity Provider (IdP), Service
Provider (SP), and user. Uses XML Assertions
(authentication statements, attribute statements).
Browser-based: POST binding redirects SAML assertions
via browser. Not suitable for API/mobile - designed
for web browser SSO. Questions answered: "Has this
enterprise user authenticated with their corporate IdP?
What attributes does the IdP assert about them?"

**SCIM 2.0 (RFC 7642-7644):**
REST-based provisioning protocol. Standardizes the
create/read/update/delete/list of identity entities
(Users, Groups) across systems. Uses a JSON schema.
The IdP is the SCIM client (pushes user data); the
application is the SCIM server (receives and stores
user data). Questions answered: "How do I automatically
keep user accounts synchronized across all systems?"

---

### ⏱️ Understand It in 30 Seconds

**One line:**
OAuth 2.0 = authorization; OIDC = authentication;
SAML = enterprise SSO; SCIM = provisioning.
One IdP speaks all four simultaneously.

**One analogy:**
> Think of international air travel identity system:
>
> - **SCIM:** Immigration department creates your entry
>   record when your visa is approved (provisioning:
>   user account created in destination system)
>
> - **SAML:** Showing your passport at the border
>   (IdP assertion: "this person is who they say they are,
>   here are their attributes"). Paper-based, formal,
>   trusted by enterprise (legacy app integration).
>
> - **OIDC:** Using your phone's biometric to pass
>   through the fast lane (modern authentication:
>   ID token proves identity, works with apps/APIs).
>
> - **OAuth 2.0:** Customs declaration ("I authorize
>   this airline to access my baggage allowance on
>   my behalf"). Scoped delegation, not authentication.
>
> One border agency (IdP) handles all four interactions
> for the same person.

---

### 🔩 First Principles Explanation

**Why four specifications instead of one?**

They evolved independently to solve different problems
at different times:

- SAML 2.0 (2005): Enterprise Web SSO, pre-smartphone,
  XML era. Still the only viable option for many legacy
  enterprise apps that were built to SAML spec.
- OAuth 2.0 (2012): API economy era. Mobile apps
  needed to access APIs on behalf of users without
  sharing credentials. SAML could not solve this.
- OIDC (2014): Recognized that developers were
  incorrectly using OAuth 2.0 for authentication.
  OIDC formalized authentication on top of the OAuth
  2.0 infrastructure.
- SCIM 2.0 (2015): Each IdP vendor had proprietary
  provisioning APIs. Okta had one, Azure AD had another.
  SCIM standardized the provisioning interface.

Each spec is a pragmatic solution to its era's
problem. They coexist because you cannot migrate 30
years of enterprise software to a new protocol by
deprecating the old one.

**The convergence:**

Modern IAM platforms implement all four because
enterprise customers have all four scenarios.
The unifying concept is the Identity Provider:

```
One IdP, four protocol planes:

            [Okta / Entra ID / Ping]
                      |
         ┌────────────┼─────────────┐
         |            |             |
   SAML SP      OIDC Client   OAuth Client
  (Salesforce)  (Mobile App)  (Internal API)

         SCIM: provisioning to ALL apps
```

The IdP maintains one user record (the authoritative
identity). When a user authenticates, the IdP issues
the appropriate assertion (SAML XML assertion for
SAML SPs, OIDC ID token for OIDC clients, OAuth 2.0
access token for API clients).

---

### 🧪 Thought Experiment

**Protocol selection decision tree:**

```
New application integration at an enterprise:

Scenario 1: Salesforce CRM
  -> Legacy enterprise SaaS
  -> Already configured for SAML 2.0
  -> Enterprise IT expects SAML
  Decision: Use SAML 2.0

Scenario 2: New React web app + REST API
  -> Developer-owned application
  -> Needs user authentication (who is the user?)
  -> Needs to call protected APIs
  -> Mobile app also in scope
  Decision: Use OIDC (Authorization Code + PKCE)
  for authentication + OAuth 2.0 for API authorization

Scenario 3: AWS Lambda calls internal HR API
  -> No user involved (machine-to-machine)
  -> Lambda needs to call HR API with scoped access
  -> 15-minute token is fine
  Decision: Use OAuth 2.0 Client Credentials grant
  (no user, no OIDC needed, just service token)

Scenario 4: New employee's account needs to be
  in Slack, Jira, GitHub, and AWS
  -> User was created in Okta (from HRIS)
  -> Needs to propagate to all 4 apps
  Decision: SCIM provisioning from Okta to
  each application (not SSO - this is provisioning)

Scenario 5: Need SSO for scenario 4 apps
  -> After SCIM provisioned the accounts
  -> User should log in once (Okta) and access all
  -> Slack, GitHub, Jira support SAML and OIDC
  Decision:
  - Slack: SAML 2.0 (legacy enterprise pattern)
  - GitHub: SAML 2.0 (enterprise GitHub SSO)
  - Jira Cloud: SAML 2.0 or OIDC (both supported)

Note: SCIM provisioning is separate from SSO.
SCIM creates the account. SSO handles authentication.
Both are needed for complete lifecycle management.
```

---

### 🧠 Mental Model / Analogy

> The four specs are like four departments in a hotel:
>
> - **SCIM (Reservations):** Creates your booking
>   before you arrive. Your profile exists in the
>   hotel system (provisioning). When Okta creates
>   a user and SCIMs them to Salesforce -> reservations.
>
> - **SAML (Front Desk - Legacy):** You show your
>   passport, they check the reservation, issue a
>   room key (assertion). Formal, paper-heavy, but
>   trusted and works with all the old locks.
>
> - **OIDC (Mobile Check-In):** App-based check-in.
>   Faster, smartphone-compatible, returns a digital
>   key (ID token). Same reservation (identity) as SAML.
>
> - **OAuth 2.0 (Room Service Authorization):**
>   Your digital key authorizes room service to
>   charge your room. Scoped delegation: the waiter
>   (client app) can charge your room (resource server)
>   because you delegated that permission. Not the same
>   as authentication - the waiter does not know who you
>   are, just that you authorized the charge.
>
> One hotel (IdP), four departments, one guest record.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Four identity protocols exist because different types
of applications need different things: enterprise
apps use SAML, modern apps use OIDC, APIs use OAuth
2.0, and user account sync uses SCIM. One identity
system (like Okta) speaks all four.

**Level 2 (junior developer):**
For a new web application: use OIDC (not SAML, not
raw OAuth 2.0). OIDC gives you: a standard login
flow, an ID token (JWT) with user identity, a
UserInfo endpoint, and logout support. Library
support: `passport-openidconnect` (Node.js), Spring
Security OAuth2 Client (Java), `python-social-auth`
(Python). SAML is for enterprise apps with legacy
constraints, not for new development.

**Level 3 (mid engineer):**
SAML vs. OIDC technical difference in the SSO flow:
SAML uses HTTP POST binding - the IdP returns an HTML
form with a Base64-encoded XML assertion; the browser
auto-submits the form to the SP. OIDC uses HTTP
redirect with authorization code - the IdP redirects
back with a code; the client exchanges the code for
tokens at the token endpoint. OIDC works for SPAs and
mobile (PKCE). SAML does not (no PKCE, requires browser,
XML parsing required). This is why OIDC replaced SAML
for new apps.

**Level 4 (senior/staff):**
Implementing a service that speaks both SAML and OIDC
(multi-protocol SP): some large SaaS products (Salesforce,
Workday) support both SAML and OIDC SSO. Customers choose
based on their IdP capabilities. For SAML: register SP
metadata (entityID, ACS URL, X.509 cert). For OIDC:
register client application (client_id, redirect_uri,
response_type). Both authenticate to the same user
session in the app, just via different assertion formats.
Important: verify the issuer in both cases to prevent
substitution attacks (wrong IdP assertion accepted).

**Level 5 (distinguished):**
Protocol translation gateways: some enterprises use
a SAML-to-OIDC bridge (Azure AD Application Proxy,
Okta SAML App) to SSO-enable legacy SAML-only apps
via an OIDC-fronted reverse proxy. The proxy:
(1) authenticates the user via OIDC; (2) generates a
SAML assertion on behalf of the user toward the legacy
app. This enables the enterprise to maintain OIDC as
the sole client protocol while supporting SAML
backends. Security implication: the proxy becomes
a high-value target (it can generate assertions for
any user toward any SAML SP). PAM protection required.

---

### ⚙️ How It Works (Mechanism)

```
Okta as Multi-Protocol IdP - Concurrent Flows:

Flow A: SAML 2.0 (Salesforce login)
  User -> Salesforce (/myapp) 
    -> Salesforce: redirect to Okta SAML SSO URL
    GET https://company.okta.com/app/salesforce/
        sso/saml?SAMLRequest=<deflated+encoded>
    -> Okta: authenticates user (if not already)
    -> Okta: generates XML SAMLResponse
      <samlp:Response>
        <saml:Assertion>
          <saml:AuthnStatement .../>
          <saml:AttributeStatement>
            <saml:Attribute Name="email">
              <saml:AttributeValue>alice@co.com
              </saml:AttributeValue>
            </saml:Attribute>
          </saml:AttributeStatement>
        </saml:Assertion>
      </samlp:Response>
    -> Browser POST to Salesforce ACS URL
    -> Salesforce validates signature, creates session

Flow B: OIDC (Mobile App login)
  App -> Authorization Server:
    GET /oauth2/v1/authorize?
      client_id=mobile-app&
      response_type=code&
      scope=openid email profile&
      code_challenge=PKCE-challenge&
      redirect_uri=app://callback
  -> Okta: authenticates user (same session as SAML)
  -> Redirect: app://callback?code=AUTH_CODE
  -> App: POST /oauth2/v1/token {code, verifier}
  -> Okta: returns
      {access_token, id_token, refresh_token}
  -> App: decode id_token (JWT):
      {sub:"00u1a2b3", email:"alice@co.com", ...}
  -> App: call API with Authorization: Bearer access_token

Flow C: OAuth 2.0 Client Credentials (Service-to-Service)
  Lambda -> POST /oauth2/v1/token
    {grant_type:client_credentials,
     client_id:svc-hr-api,
     client_secret:...,
     scope:hr-api.read}
  -> Okta: returns {access_token, expires_in:900}
  -> Lambda: GET /api/employee/alice
      Authorization: Bearer access_token
  -> HR API: validate token, return data

Flow D: SCIM Provisioning (Workday -> Okta -> Apps)
  Workday HRIS: new hire event
  -> Workday SCIM client:
    POST https://company.okta.com/scim/v2/Users
    {"userName":"alice","emails":[...],"active":true}
  -> Okta: creates user in Okta universal directory
  -> Okta SCIM client -> Salesforce:
    POST https://salesforce.com/services/scim/v2/Users
    {"userName":"alice@co.com",...}
  -> Okta SCIM client -> GitHub:
    POST https://api.github.com/scim/v2/organizations/co/Users
  -> Alice now exists in: Okta + Salesforce + GitHub
  -> SSO (SAML/OIDC) now available for all three
```

---

### ⚖️ Comparison Table

| Spec | Problem Solved | Token Format | Transport | Best For |
|:---|:---|:---|:---|:---|
| SAML 2.0 | Enterprise browser SSO | XML Assertion | Browser POST/redirect | Legacy SaaS, enterprise apps |
| OIDC | Authentication for modern apps | JWT (ID Token) | OAuth 2.0 flows | Web, mobile, SPA apps |
| OAuth 2.0 | API authorization delegation | Opaque or JWT (access token) | HTTPS REST | API access, service-to-service |
| SCIM 2.0 | User/Group provisioning | JSON REST | HTTPS REST | Account lifecycle sync |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "OIDC replaces SAML" | OIDC is better for new apps but SAML is still required for most legacy enterprise SaaS integrations (SAP, legacy Salesforce configs, custom enterprise portals). Both coexist in every enterprise IAM platform. |
| "OAuth 2.0 authenticates users" | OAuth 2.0 is an authorization framework. It issues access tokens for resource access, not identity assertions. Using an access token to determine user identity is an anti-pattern (use OIDC ID token instead). |
| "SCIM is optional if you have SSO" | SSO handles authentication (login). SCIM handles provisioning (account creation, updates, deactivation). Without SCIM, user accounts in downstream apps must be created manually. With SCIM, deprovisioning is automatic - critical for offboarding SLA. |
| "JWT is an OIDC thing" | JWT (RFC 7519) is a token format independent of OIDC. OAuth 2.0 access tokens can be JWT. OIDC ID tokens are always JWT. SAML assertions are XML (not JWT). JWT is a format, OIDC/OAuth 2.0/SAML are protocols. |

---

### 🚨 Failure Modes & Diagnosis

**SAML assertion replay attack**

```
Problem: Stolen SAML assertion reused to authenticate
to a different service provider.

SAML assertions have:
  NotBefore / NotOnOrAfter -> time validity window
  InResponseTo -> ties assertion to specific AuthnRequest

Replay prevention requires:
1. InResponseTo validation (SP checks assertion is
   response to its specific AuthnRequest ID)
2. One-time use cache: SP stores seen assertion IDs
   within the validity window; reject duplicates
3. Short validity window (< 5 minutes recommended)

Diagnosis:
  SP access log: same assertion ID appearing twice
  {
    time: "2024-11-01T10:00:05Z",
    assertionId: "_abc123...",
    outcome: "SUCCESS"
  },
  {
    time: "2024-11-01T10:00:07Z",
    assertionId: "_abc123...",  <- same ID
    outcome: "REJECTED - assertion already seen"
  }

Fix: verify SP has assertion replay cache enabled
```

**OIDC token substitution attack**

```
Problem: Access token from App A is used to call App B,
because App B does not validate the `aud` (audience) claim.

JWT access token:
{
  "sub": "alice@company.com",
  "aud": ["app-a"],         <- intended for App A only
  "scope": "read:orders",
  "exp": 1701388800
}

App B without aud validation:
  -> Accepts token (only validates signature + expiry)
  -> Alice (or attacker) can use App A token for App B

Fix: always validate aud claim in token validation:
  if (!token.aud.includes("app-b")) {
    throw new Error("Invalid audience");
  }

RFC 7519 requires: if aud is present, validator
MUST verify the aud claim includes the intended
recipient. Many JWT libraries do not enforce this
by default.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-009` - SSO Concepts: the foundation these specs build on
- `IAM-010` - Identity Federation: the federation concepts
- `IAM-014` - SAML 2.0 and Enterprise SSO: SAML detail

**Related OAuth/OIDC Detail:**
- `OAU-001` - OAuth 2.0 Fundamentals
- `OAU-011` - OpenID Connect

**Builds On This:**
- `IAM-026` - Enterprise IAM Architecture
- `IAM-034` - Identity as the New Perimeter

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ PROTOCOL SELECTION GUIDE                             │
├──────────────────────────────────────────────────────┤
│ New web/mobile app needing auth: -> OIDC (PKCE)      │
│ Legacy enterprise SaaS (SAP/Salesforce): -> SAML 2.0 │
│ Service-to-service API access: -> OAuth 2.0 CC       │
│ User account sync across systems: -> SCIM 2.0        │
│ User delegates API access to app: -> OAuth 2.0 Auth  │
│                                       Code + OIDC    │
├──────────────────────────────────────────────────────┤
│ COMMON ANTI-PATTERNS:                                │
│  Using OAuth 2.0 access token for identity -> use    │
│  OIDC ID token                                       │
│  Manual provisioning when SCIM available -> use SCIM │
│  SAML for new mobile/SPA app -> use OIDC + PKCE      │
│  Missing aud claim validation in JWT -> security hole │
└──────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"OAuth 2.0 is API authorization delegation; OIDC adds
authentication (ID tokens) on top of OAuth 2.0; SAML 2.0
is browser-based enterprise SSO using XML assertions
(required for legacy enterprise apps); SCIM 2.0 is
REST-based user provisioning. Modern IdPs (Okta, Entra ID)
implement all four simultaneously: one identity store,
four protocol planes. Protocol selection: new apps use
OIDC; legacy enterprise apps use SAML; APIs use OAuth 2.0;
account sync uses SCIM."

---

### 💎 Transferable Wisdom

The coexistence of SAML, OIDC, OAuth 2.0, and SCIM
illustrates a principle common to all mature domains:
specifications are not replaced, they accumulate.
New specifications address new problems without
invalidating existing ones. The smart architect
treats this as an integration problem, not a
replacement problem. The same pattern appears in:
database protocols (JDBC coexists with JPA coexists
with reactive drivers); messaging (JMS coexists with
AMQP coexists with Kafka protocol); data formats
(CSV coexists with JSON coexists with Avro/Parquet).
The long-lived enterprise is the one that treats
legacy protocols as first-class citizens while
adopting modern ones for new workloads - not the
one that mandates a single protocol and struggles
to integrate the 20-year-old system it cannot replace.

---

### ✅ Mastery Checklist

1. **DECIDE** For each of the following scenarios, state
   the correct protocol and explain why: (a) React SPA
   with an ASP.NET Core backend API; (b) SAP S/4HANA
   enterprise SSO; (c) Lambda function calling an
   internal HR REST API; (d) Workday HRIS synchronizing
   new employees to Slack and GitHub; (e) iOS mobile app
   accessing user photos from a photo API.

2. **EXPLAIN** What is the technical difference between
   SAML 2.0 HTTP POST binding and OIDC Authorization
   Code flow? Why is OIDC preferred for mobile apps?
   What specific feature (PKCE) makes OIDC secure for
   public clients?

3. **SECURE** An OIDC access token is being used to
   authenticate to App B, but it was issued for App A.
   Describe the attack, the specific claim that prevents
   it, and how to validate that claim correctly in JWT
   validation code.

---

*Identity & Access Management | IAM-031 | v5.0*