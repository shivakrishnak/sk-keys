---
id: IAM-009
title: "Single Sign-On (SSO) Concepts"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★☆☆
depends_on: IAM-003, IAM-008
used_by: IAM-010, IAM-014, IAM-024
related: IAM-010, IAM-014, OAU-001
tags:
  - iam
  - security
  - identity
  - protocol
  - foundational
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/iam/single-sign-on-sso-concepts/
---

⚡ TL;DR - Single Sign-On (SSO) allows users to authenticate
once with a central Identity Provider and then access
multiple applications without re-entering credentials.
The IdP issues a session that applications trust. Benefits:
reduced password fatigue, centralized offboarding, and
a single audit trail. Risk: the IdP becomes a critical
single point of failure and a high-value attack target.

---

### 🔥 The Problem This Solves

A company with 50 SaaS apps (Salesforce, GitHub, Jira,
Slack, AWS, Workday...) requires employees to maintain
50 separate passwords if each app manages its own
authentication. The reality:

- Users choose weak, reused passwords for less important
  apps ("Jira123!" shared across five tools)
- Onboarding takes days (manually create accounts in all 50)
- Offboarding fails (accounts in forgotten apps persist)
- Audit: who accessed what? Fragmented across 50 logs

SSO consolidates authentication to one IdP. Users
authenticate once; the IdP vouches for them to all
50 apps via signed assertions or tokens. Onboarding
creates one account in the IdP. Offboarding deactivates
one account. Audit is in one place.

---

### 📘 Textbook Definition

Single Sign-On (SSO) is an authentication pattern in
which a user authenticates once to a central Identity
Provider (IdP) and is then automatically authenticated
to multiple Service Providers (SPs) - applications and
services that trust the IdP - without re-entering
credentials for each.

**SSO session:** After authenticating, the IdP creates
an SSO session (typically a session cookie scoped to
the IdP domain). When the user attempts to access an
SP, the SP redirects to the IdP. The IdP checks for
an active SSO session; if valid, it issues an assertion
(SAML) or token (OIDC) to the SP without prompting
for credentials again.

**Service Provider (SP):** The application that delegates
authentication to the IdP. The SP trusts assertions
from the IdP.

**IdP-initiated SSO:** User starts at the IdP dashboard
(Okta, portal.azure.com) and clicks an app. IdP
pushes the assertion to the SP directly.

**SP-initiated SSO:** User navigates to the SP URL.
SP detects no active session, redirects to IdP.
IdP authenticates (or checks SSO session), issues
assertion, redirects back to SP.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Log in once to the IdP; get into all apps without
re-entering credentials. The IdP tells each app
"I verified this user."

**One analogy:**
> A theme park wristband:
> - You identify yourself at the entrance gate (authenticate)
> - The gate issues you a wristband (SSO session)
> - At every ride, you show the wristband - no re-
>   identification required (SSO access to apps)
> - The wristband expires at park closing (session timeout)
> - If you lose the wristband (session revocation), you
>   go back to the gate for a new one

**One insight:**
SSO trades individual application authentication for
a dependency on the IdP. If the IdP is down, no user
can authenticate to any application. This is the
SSO availability trade-off that must be engineered for.

---

### 🔩 First Principles Explanation

**Why SSO is worth the IdP dependency:**

Without SSO, each app authenticates independently.
N apps = N authentication systems. Security properties
vary per app (some have MFA, some don't). Offboarding
requires N revocations.

With SSO: N apps = 1 authentication system. Security
policy (MFA, password complexity, session timeout) is
enforced at the IdP uniformly. Offboarding = disable
1 IdP account.

**The trust model:**

SSO works because SPs trust the IdP's assertions:
"I, the IdP, assert that user alice@company.com
authenticated at 14:30 with MFA." The assertion is
cryptographically signed by the IdP's private key.
The SP verifies the signature with the IdP's public
key. No password flows to the SP.

**The revocation limitation:**

When the IdP issues an assertion (SAML) or token
(OIDC id_token), the SP caches authentication state
for the token's validity period. Revoking the IdP
session does not immediately revoke all SP sessions.
The SP continues to accept its cached session until
it expires or the SP is configured to validate against
the IdP on every request.

---

### 🧪 Thought Experiment

**User alice tries to access GitHub with OIDC SSO:**

1. Alice navigates to github.com
2. GitHub detects: no active GitHub session
3. GitHub redirects: `https://idp.company.com/auth?
   client_id=github&redirect_uri=https://github.com/callback`
4. IdP checks: does alice have an active SSO session?
   - **No:** Show login page. Alice authenticates with
     password + MFA. IdP creates SSO session (cookie).
   - **Yes (already logged in):** Skip authentication.
5. IdP issues authorization code back to GitHub
6. GitHub exchanges code for id_token + access_token
7. GitHub extracts: `{sub: alice, email: alice@co.com}`
8. GitHub creates a local GitHub session for alice
9. Alice is in GitHub - no password entered at GitHub

**Later:** Alice tries Salesforce (also OIDC SSO):
- Steps 1-6 repeat
- At step 4: IdP has active SSO session from GitHub login
- No login prompt shown - alice goes straight to Salesforce
- This is the "single sign-on" experience

---

### 🧠 Mental Model / Analogy

> **Without SSO:** entering a building complex with
> 50 different locks. You carry 50 keys. You insert
> a different key at each door. Some keys are the same
> (you reused them). Some you forgot. Some are expired.
>
> **With SSO:** a master keycard system. You authenticate
> at the front entrance once per day. The system
> records "Alice authenticated at 9am with fingerprint."
> Every interior door reader trusts the master system's
> record: if the system says Alice is cleared, the door
> opens. Alice never touches a different key again.
>
> **The single IdP failure risk:** if the master keycard
> system goes offline, no doors open for anyone.
> This is why IdP availability is critical infrastructure.

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
SSO means you log in once and can access all your
work tools without logging in separately to each one.
It is like a company badge that works in all buildings.

**Level 2 (junior developer):**
To implement SSO for your app: register your app as
an OIDC client with the IdP (get client_id, client_secret).
Add a login button that redirects to the IdP. Handle
the callback with the authorization code. Exchange
the code for tokens. Extract user identity from the
id_token. Create a local session. Most frameworks
have library support (passport.js, Spring Security,
etc.).

**Level 3 (mid engineer):**
SP-initiated OIDC SSO flow in detail: PKCE code
challenge prevents authorization code interception.
State parameter prevents CSRF. Nonce prevents id_token
replay. Access token is for calling APIs. id_token is
for user identity. Refresh token extends sessions
without re-authentication. IdP session cookie is
separate from SP session cookie; both must be managed.

**Level 4 (senior/staff):**
Back-channel logout (OIDC) vs front-channel logout:
front-channel sends logout to all SPs via browser
redirects (unreliable if SP is down). Back-channel
sends HTTP POST directly from IdP to SPs (reliable
but requires SP to expose a logout endpoint). CAEP
(Continuous Access Evaluation Protocol) extends this:
real-time session revocation events pushed to SPs
when identity context changes (password reset, account
lock, location anomaly).

**Level 5 (distinguished):**
Enterprise SSO at scale introduces token amplification
risk: one compromised IdP credential gives access to
all SPs. Defense: conditional access policies (deny
access from unknown locations or devices even with
valid credentials), risk-based authentication scores
(Okta ThreatInsight), and FIDO2 phishing-resistant
credentials that cannot be replayed. CAEP/SSF (Shared
Signals Framework) standardizes how IdPs push
security events to relying parties in real time.

---

### ⚙️ How It Works (Mechanism)

```
OIDC SSO - SP Initiated Flow:

1. User navigates to app.example.com
2. App has no session -> redirect to IdP:
   GET https://idp.co/authorize?
       client_id=app-client
       &response_type=code
       &scope=openid+email+profile
       &redirect_uri=https://app.example.com/callback
       &state=random-csrf-token
       &code_challenge=PKCE-hash
       &nonce=random-nonce

3. IdP checks SSO session cookie
   IF no active session:
     -> Show login form -> user authenticates
     -> Create SSO session (domain: idp.co)
   IF active session:
     -> Skip login prompt

4. IdP redirects back:
   GET https://app.example.com/callback?
       code=auth-code-xyz&state=random-csrf-token

5. App exchanges code (server-side):
   POST https://idp.co/token
   Body: code=auth-code-xyz
         &code_verifier=PKCE-original
         &client_secret=...
   Response: {access_token, id_token, refresh_token}

6. App validates id_token:
   - Verify signature with IdP's public key (JWKS)
   - Check iss (issuer), aud (audience=client_id)
   - Check exp (not expired), nonce (matches step 2)
   - Extract: sub (user ID), email, groups

7. App creates local session for user
   -> User is authenticated in app
```

---

### ⚖️ Comparison Table

| Protocol | Format | Best For | Complexity |
|:---|:---|:---|:---|
| SAML 2.0 | XML assertions | Enterprise legacy apps, browser SSO | High (XML, complex spec) |
| OIDC | JWT id_token | Modern web/mobile apps | Medium |
| Kerberos | Ticket Granting Ticket | Windows / AD environments | Low for clients, complex server |
| CAS | XML / JSON | University / open source systems | Medium |

**SAML vs OIDC: which to use:**

- **SAML:** existing enterprise apps that require it
  (legacy ERP, many SaaS apps). Not suited for mobile
  (requires browser redirect). XML parsing is complex.
- **OIDC:** new apps, APIs, mobile applications.
  JSON-based. OAuth 2.0 compatible. Preferred for
  all greenfield development.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| SSO eliminates all authentication | SSO eliminates per-app re-authentication. The initial IdP login still happens (and should include MFA). |
| Logging out of an app ends the SSO session | Logging out of an SP typically only ends the SP's local session. The IdP SSO session continues. User can silently re-access the app without re-authenticating. |
| SSO is only for web apps | OIDC supports native mobile and CLI apps via device flow and PKCE. Kerberos is native SSO for Windows. SSH certificate-based SSO exists for Linux. |
| SSO makes security easier by centralizing it | Centralization creates a higher-value target. IdP compromise = all applications compromised simultaneously. Security investment in the IdP must be proportional. |

---

### 🚨 Failure Modes & Diagnosis

**Redirect loop on SSO**

**Symptom:** Browser enters infinite loop between app
URL and IdP URL. 302 redirects cycling indefinitely.

**Root Cause:** App sets no local session cookie after
receiving the IdP callback, or session cookie domain
mismatch. App keeps redirecting to IdP; IdP keeps
redirecting back with assertion; app never accepts it.

**Diagnosis:**
```bash
# Open browser DevTools -> Network tab
# Follow redirect chain: app -> idp -> app -> idp...
# At the callback: does the Set-Cookie header appear?
# Is the callback URL exactly matching the registered
# redirect_uri? Even trailing slash mismatch causes failure

# Check IdP logs for successful token issuance
# Check app logs for "callback received" but no session created
```

**Fix:** Ensure the callback handler sets the session
cookie with the correct domain and path. Verify
redirect_uri matches exactly (no trailing slash diff).

---

**Logout leaves active IdP session**

**Symptom:** User clicks "logout" in the app, is
redirected to login page, but clicking "login" again
accesses the account without any credential prompt.

**Root Cause:** App-only logout did not terminate
the IdP SSO session. Only the SP session was cleared.

**Fix:** Implement RP-initiated logout: after clearing
local session, redirect to IdP logout endpoint:
```
GET https://idp.co/logout?
    post_logout_redirect_uri=https://app.co/logged-out
    &id_token_hint=eyJhbGci...
```
This terminates the IdP SSO session and prevents
silent re-authentication.

---

### 🔗 Related Keywords

**Prerequisites:**

- `IAM-003` - Authentication vs Authorization vs Identity
- `IAM-008` - Directory Services: LDAP/AD as IdP backend

**Builds On This:**

- `IAM-010` - Identity Federation Basics: cross-org SSO
- `IAM-014` - SAML 2.0 and Enterprise SSO: SAML SSO detail
- `OAU-001` - OAuth 2.0 Basics: the protocol SSO uses

**Related:**

- `ATH-002` - Session Management: SP session lifecycle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ SSO FLOW SUMMARY                                     │
├──────────────────────┬───────────────────────────────┤
│ User visits app      │ SP: no session -> redirect    │
├──────────────────────┼───────────────────────────────┤
│ IdP SSO session?     │ Yes: issue assertion, return  │
│                      │ No: show login, then issue    │
├──────────────────────┼───────────────────────────────┤
│ App receives token   │ Validate signature, extract   │
│                      │ identity, create local session │
├──────────────────────┼───────────────────────────────┤
│ Protocol options     │ SAML 2.0 (enterprise legacy)  │
│                      │ OIDC (modern / mobile / API)  │
├──────────────────────┼───────────────────────────────┤
│ Logout best practice │ RP-initiated logout to IdP    │
│                      │ + clear local session         │
├──────────────────────┼───────────────────────────────┤
│ Key risk             │ IdP down = all apps blocked   │
│                      │ IdP compromised = all apps     │
└──────────────────────┴───────────────────────────────┘
```

**If you remember 3 things:**

1. SSO moves authentication to the IdP. The SP trusts
   the IdP's signed assertion - no password reaches the SP.

2. Logging out of the SP does not log out of the IdP
   SSO session. Use RP-initiated logout.

3. IdP availability = all application availability.
   Treat IdP as Tier 0 infrastructure.

**Interview one-liner:**
"SSO allows users to authenticate once at the IdP and
access multiple applications via signed assertions.
The SP-initiated OIDC flow: SP redirects to IdP, IdP
checks SSO session, issues code, SP exchanges code for
tokens, creates local session."

---

### 💎 Transferable Wisdom

**Reusable Principle:**
SSO is the "verify once, trust everywhere" pattern. It
appears whenever multiple systems need to share trust
in a single verified entity: Kerberos TGT (verify once
with KDC, get service tickets for multiple services),
API gateway JWT (verify once at gateway, forward claims
to backend services), database connection proxy (verify
once, multiplex connections to DB without per-query
auth). The trade-off is always the same: efficiency
and centralized control vs single point of trust failure.

**Where else this appears:**

- CDN authentication: verify user once at edge, issue
  signed cookie trusted by all origin servers.

- Cloud metadata credentials: EC2 instance verified
  once to IAM, gets STS credentials accepted by all
  AWS services - SSO for cloud resources.

---

### 💡 The Surprising Truth

The most common SSO security failure is not in the
protocol design - it is in the RP-initiated logout
gap. A 2022 study of enterprise web applications
found that 78% of SSO-enabled applications did not
properly implement IdP logout on user sign-out. Users
who believed they logged out of a bank or healthcare
app still had an active IdP session that could silently
re-authenticate them. In shared device environments
(public kiosks, shared workstations), this is a direct
session hijacking vector requiring no technical exploit.
The fix (a single redirect to the IdP logout endpoint)
is trivial; the failure is widespread.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**

1. **EXPLAIN** The difference between an SP-local session
   and an IdP SSO session, and why clearing the SP
   session does not end the SSO session.

2. **IMPLEMENT** Describe the full OIDC SP-initiated SSO
   flow including PKCE, state, and nonce parameters -
   what each prevents and what breaks if each is missing.

3. **DIAGNOSE** Given a browser stuck in a redirect loop
   between an app and an IdP, identify the three most
   likely causes and the diagnostic steps for each.

---

*Identity & Access Management | IAM-009 | v5.0*