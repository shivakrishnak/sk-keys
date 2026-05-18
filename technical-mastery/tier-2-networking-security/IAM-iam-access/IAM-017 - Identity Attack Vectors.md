---
id: IAM-017
title: "Identity Attack Vectors"
category: "Identity & Access Management"
tier: tier-2-networking-security
folder: IAM-iam-access
difficulty: ★★☆
depends_on: IAM-003, IAM-012, IAM-016
used_by: IAM-021, IAM-023, IAM-030
related: IAM-023, SEC-007, SEC-008
tags:
  - iam
  - security
  - identity
  - threat
  - intermediate
status: complete
version: 5
layout: default
parent: "Identity & Access Management"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/iam/identity-attack-vectors/
---

⚡ TL;DR - Identity attack vectors target authentication
and authorization: credential stuffing (leaked password
lists against login endpoints), phishing (fake login
pages capturing credentials), MFA fatigue (spamming MFA
push notifications until user accepts), SAML XML
Signature Wrapping (forging SAML assertions), OAuth token
theft (intercepting OAuth tokens), session hijacking
(stealing session cookies), and privilege escalation
(exploiting misconfigured IAM policies). Identity is
the #1 attack vector in cloud breaches.

---

### 🔥 The Problem This Solves

In 2023, 80%+ of breaches involved compromised credentials
(Verizon DBIR). The cloud perimeter has dissolved:
applications are internet-accessible. Traditional network-
based defenses (firewall, VPN, network segmentation)
do not stop an attacker with valid credentials. Identity
is now the primary security perimeter.

Understanding identity attack vectors is required to:
build effective defenses (which MFA types resist phishing),
detect attacks in progress (impossible travel, credential
stuffing patterns), and design IAM systems that are
resilient to specific attack classes.

---

### 📘 Textbook Definition

**Credential Stuffing:**
Using lists of leaked username/password pairs (from
data breaches) against login endpoints. Automated attacks
test millions of credential pairs against target apps.
Success rate: 0.1-2% - sufficient at scale.

**Phishing:**
Fraudulent communications (email, SMS, voice) that
direct victims to attacker-controlled login pages
mimicking legitimate services. Steals credentials
directly. Advanced variants (AiTM - Adversary in the
Middle) proxy the real site and steal MFA tokens in
real-time by forwarding authentication requests.

**MFA Fatigue (Push Bombing):**
Attackers who have already obtained a victim's password
spam the victim with MFA push notifications at unusual
hours. Some victims accidentally approve; some approve
to stop the notifications. Bypassable by: number matching
MFA (user confirms a displayed number), phishing-resistant
FIDO2/hardware keys.

**XML Signature Wrapping (XSW):**
SAML-specific attack. Attacker captures a valid SAML
assertion, wraps it in an XML envelope with forged
identity claims, submits to SP. If the SP validates
the signature on the original (inner) assertion but
reads identity from the outer (unsigned) wrapper,
attacker impersonates any user. Affected: GitHub (2012),
Salesforce (2012), AWS (2017).

**OAuth Token Theft:**
OAuth access tokens grant API access without passwords.
Stolen tokens (via XSS, open redirect, malicious app)
provide API access for the token lifetime. Mitigated by:
short token lifetimes, token binding, PKCE (public clients),
detecting suspicious token usage patterns.

**Session Hijacking:**
Stolen session cookies grant web application access.
Vectors: XSS, network interception (non-HTTPS), malware.
AiTM phishing captures session tokens in real-time.
Mitigated by: HttpOnly + Secure cookie flags, HTTPS-only,
session binding to IP/device fingerprint.

**Privilege Escalation via IAM Misconfiguration:**
An attacker with low-privilege access exploits overly
permissive IAM policies (s3:PutBucketPolicy allows
attacker to grant themselves bucket admin; iam:PassRole
allows attacker to attach admin role to EC2).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Identity attacks work by obtaining, forging, or
elevating credentials/tokens/sessions - bypassing
authentication without triggering normal defenses.

**One analogy:**
> An identity attack is like gaining entry to a
> restricted building without breaking the locks:
>
> - **Credential stuffing:** trying every duplicate key
>   from other buildings until one works
> - **Phishing:** building a fake front desk that copies
>   everyone's badge as they scan it
> - **MFA fatigue:** ringing the door buzzer repeatedly
>   until a distracted employee buzzes you in
> - **Privilege escalation:** walking in as a janitor
>   and finding a manager's unlocked office with their
>   keycard sitting on the desk

**One insight:**
Most identity attacks do not exploit technical
vulnerabilities in protocols - they exploit human factors
(phishing, MFA fatigue) or misconfigurations (overly
permissive policies, stale credentials). Protocol-level
attacks (XSW, JWT alg:none) are rarer but catastrophic.

---

### 🔩 First Principles Explanation

**Why passwords fail at scale:**

Password authentication has a fundamental weakness:
credentials can be captured, reused, and distributed.
A leaked database from Site A provides working credentials
for Site B if users reuse passwords. At scale, attackers
maintain credential lists of billions of leaked pairs
and test them automatically. The only defenses: MFA
(second factor not in leaked DB), rate limiting (slow
down testing), breach password checking (HaveIBeenPwned
API integration in login).

**Why MFA does not always save you:**

TOTP and SMS MFA can be phished in real-time (AiTM attacks).
Attacker proxy: user enters credentials at fake site ->
fake site forwards to real site -> real site requests MFA
-> fake site asks user for MFA code -> user enters code ->
fake site forwards to real site -> session token captured.
FIDO2 hardware keys (YubiKey) resist this: the
authentication response is bound to the origin (site URL).
A fake site cannot forge the correct origin, so the
FIDO2 response only works on the real site.

---

### 🧪 Thought Experiment

**Detecting credential stuffing in AWS CloudFront logs:**

```bash
# Credential stuffing shows: high volume, low success,
# many different source IPs, targeting POST /login

# CloudFront logs (WAF enabled):
aws logs filter-log-events \
  --log-group-name /aws/cloudfront/distribution \
  --filter-pattern '{ $.cs-uri-stem = "/auth/login"
    && $.sc-status = 401 }' \
  --start-time $(date -d '1 hour ago' +%s000) | \
  jq '.events[].message' | \
  python3 -c "
import sys, json
from collections import Counter
ips = []
for line in sys.stdin:
    fields = line.strip('\"').split('\t')
    ips.append(fields[4])  # c-ip column
c = Counter(ips)
for ip, count in c.most_common(20):
    print(f'{count:5d} requests from {ip}')
"
# > 100 401s from single IP in 5 minutes = stuffing

# Mitigation: WAF rate rule, CAPTCHA after N failures,
# HaveIBeenPwned password check, block known bad IPs
```

---

### 🧠 Mental Model / Analogy

> Identity attack vectors form a spectrum by technical
> sophistication vs. detection difficulty:
>
> Low sophistication, easy to detect:
>   - Credential stuffing: detectable via rate limiting
>   - Brute force: detectable via account lockout
>
> Medium sophistication, harder to detect:
>   - Phishing: detectable via impossible travel after breach
>   - MFA fatigue: detectable via anomalous MFA attempts
>
> High sophistication, very hard to detect:
>   - AiTM phishing: indistinguishable from real login
>     until session behavior analysis kicks in
>   - Privilege escalation via IAM: looks like legitimate
>     IAM API calls unless cloud trail is actively analyzed
>
> Low frequency, catastrophic impact:
>   - SAML XSW: requires intercepted assertion + SAML expertise
>   - JWT alg:none: only if library misimplemented

---

### 📶 Gradual Depth - Five Levels

**Level 1 (anyone):**
Attackers try to get into systems by stealing or guessing
passwords, tricking people into revealing credentials,
or exploiting mistakes in permission settings.

**Level 2 (junior developer):**
Common mitigations: MFA on all accounts, rate limiting
on login endpoints (10 failed attempts = temporary
lockout + CAPTCHA), breach password detection (check
against HaveIBeenPwned on password creation), short
session TTL with re-authentication for sensitive actions.

**Level 3 (mid engineer):**
IAM privilege escalation paths in AWS: (1) iam:CreatePolicyVersion
allows creating a new policy version with admin access;
(2) iam:PassRole + ec2:RunInstances: launch EC2 with an
admin role - if you can SSH to that EC2, you have admin
access; (3) lambda:CreateFunction + iam:PassRole: create
Lambda with admin execution role. Enumerate these paths
using tools like PMapper and Cloudsplaining.

**Level 4 (senior/staff):**
AiTM phishing (Adversary-in-the-Middle) detection:
impossible travel analysis (user logged in from London,
then 5 minutes later a token was used from Romania),
device fingerprint mismatch (session cookie used from
unexpected browser/OS), anomalous API patterns after
authentication (immediate data download, credential
enumeration). Microsoft Entra ID and Okta provide risk
scores that can require step-up authentication or block
sessions based on these signals.

**Level 5 (distinguished):**
SAML XSW at enterprise scale: in 2017, an AWS SAML
implementation was found vulnerable to XSW. An attacker
who could obtain any SAML assertion (even their own
legitimate assertion from the same IdP) could wrap it
to assert any other user's identity to AWS. Full account
takeover for all identities in the federation. Fix:
validate that signed element ID resolves to the element
used for identity decisions, not just that some element
is signed. AWS issued patches; industry-wide review
of SAML implementations followed.

---

### ⚙️ How It Works (Mechanism)

```
SAML XML Signature Wrapping Attack:

Original valid assertion (user: alice@company.com):
  <samlp:Response>
    <saml:Assertion ID="ASSERTION_1" ...>
      <saml:Subject>
        <saml:NameID>alice@company.com</saml:NameID>
      </saml:Subject>
      <ds:Signature>...signs ASSERTION_1...</ds:Signature>
    </saml:Assertion>
  </samlp:Response>

Attacker wraps it:
  <samlp:Response>
    <saml:Assertion ID="FORGED_ASSERTION">
      <!-- Forged: attacker wants admin@company.com -->
      <saml:Subject>
        <saml:NameID>admin@company.com</saml:NameID>
      </saml:Subject>
    </saml:Assertion>
    <saml:Assertion ID="ASSERTION_1" ...>
      <!-- Original, with valid signature -->
      <saml:Subject>
        <saml:NameID>alice@company.com</saml:NameID>
      </saml:Subject>
      <ds:Signature>...signs ASSERTION_1...</ds:Signature>
    </saml:Assertion>
  </samlp:Response>

Vulnerable SP behavior:
  1. Validates signature on ASSERTION_1 -> Valid!
  2. Reads identity from first Assertion element
     -> admin@company.com
  3. Grants admin access

Secure SP behavior:
  1. Validates signature on ASSERTION_1 -> Valid!
  2. ONLY uses the element that was signed:
     -> alice@company.com
  3. Rejects any assertion not covered by signature

OAuth Token Theft via Open Redirect:
  1. Attacker finds: https://app.com/redirect?url=
  2. Crafts: https://app.com/oauth?
      redirect_uri=https://app.com/redirect?url=
      https://attacker.com/steal
  3. After OAuth flow, code delivered to attacker.com
  4. Attacker exchanges code for access token
  Fix: exact redirect_uri match validation (no partial)
```

---

### ⚖️ Comparison Table

| Attack | Technical Complexity | Impact | Defense |
|:---|:---|:---|:---|
| Credential stuffing | Low | Medium | Rate limiting, MFA, breach detection |
| Phishing | Low | High | Security awareness, FIDO2, email filtering |
| MFA fatigue | Low | Medium-High | Number matching, context, FIDO2 |
| AiTM phishing | Medium | High | FIDO2 (origin-bound), session risk signals |
| SAML XSW | High | Critical | Secure XML processing, signed-element ID validation |
| OAuth token theft | Medium | High | PKCE, short TTL, token binding |
| Privilege escalation | Medium | Critical | Least privilege, IAM analyzer, Cloudsplaining |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "MFA stops all identity attacks" | TOTP/SMS MFA can be bypassed by phishing and AiTM attacks. Only FIDO2/passkeys provide phishing-resistant MFA. |
| "Breached passwords mean compromised accounts" | Only if those passwords are reused. Password managers + unique passwords reduce credential stuffing impact to zero for that account. |
| "OAuth with HTTPS is safe from token theft" | OAuth tokens can be stolen via XSS (client-side), malicious OAuth clients, open redirects, and phishing flows. HTTPS prevents network interception only. |
| "Our company is too small for sophisticated attacks" | Credential stuffing and phishing are fully automated. Every internet-accessible login endpoint is targeted regardless of organization size. |

---

### 🚨 Failure Modes & Diagnosis

**MFA push bombing in progress**

```bash
# Okta System Log: multiple consecutive MFA failures
# then a success (user gave in)
curl -H "Authorization: SSWS $OKTA_TOKEN" \
  "https://company.okta.com/api/v1/logs?since=$SINCE
   &filter=eventType eq \"user.mfa.factor.attempt_fail\""

# Check if same user had success after many failures:
# "Multiple MFA failures followed by success"
# = possible push bombing acceptance

# Immediate action if confirmed:
# 1. Terminate active sessions for that user
# 2. Reset credentials + MFA
# 3. Force re-enrollment with number-matching MFA
# 4. Investigate what was accessed after the MFA approval
```

**Privilege escalation via iam:PassRole detected**

```bash
# CloudTrail: iam:PassRole + ec2:RunInstances by low-privilege user
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,
                       AttributeValue=RunInstances \
  --start-time $(date -d '24 hours ago' +%s) | \
  jq '.Events[] | select(.Username == "low-priv-user")'

# Check what role was passed:
# If admin role passed to EC2 -> privilege escalation
# Immediate: terminate EC2, revoke user's iam:PassRole,
# audit all API calls made from that EC2's role
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `IAM-003` - Authentication vs Authorization vs Identity
- `IAM-012` - Principle of Least Privilege
- `IAM-016` - Privileged Access Management

**Builds On This:**
- `IAM-021` - Zero Trust Identity Architecture: attack-driven design
- `IAM-023` - Identity Threat Detection and Response (ITDR)
- `IAM-030` - IAM Observability: detecting these attacks

**Related:**
- `SEC-007` - OWASP Top 10
- `SEC-008` - Threat Modeling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ IDENTITY ATTACK TAXONOMY                             │
├─────────────────────┬────────────────────────────────┤
│ Credential stuffing │ Lists + automation = detection │
│ Phishing            │ Social engineering = FIDO2     │
│ MFA fatigue         │ Push spam = number matching    │
│ AiTM phishing       │ Real-time proxy = FIDO2 only  │
│ SAML XSW            │ XML wrapping = signed-ID check │
│ OAuth token theft   │ Token intercept = PKCE + TTL  │
│ Session hijacking   │ Cookie theft = HttpOnly/Secure │
│ Priv escalation     │ IAM misconfig = IAM analyzer   │
└─────────────────────┴────────────────────────────────┘

Phishing-resistant MFA: FIDO2 / passkeys ONLY
(TOTP, SMS, push notifications can all be phished)
```

**Interview one-liner:**
"The major identity attack vectors are credential
stuffing (leaked passwords), phishing (AiTM can bypass
TOTP MFA), MFA fatigue (push bombing), SAML XSW (XML
partial signing exploit), OAuth token theft, session
hijacking, and IAM privilege escalation. Phishing-resistant
MFA (FIDO2) is the only defense against real-time
phishing attacks."

---

### 💎 Transferable Wisdom

The SAML XSW attack illustrates a universal security
principle: validate and consume at the same boundary.
This appears as: JWT libraries that validate signature
but allow algorithm switching (alg:none bypass);
SQL injection that validates input at the web tier
but concatenates at the database tier; HTTP header
injection where a proxy adds a trusted header that the
origin server reads without validating its source.
The principle: the system component that makes the
trust decision must be the one that validates the
evidence, with no transformation between validation
and decision.

---

### ✅ Mastery Checklist

1. **EXPLAIN** Why FIDO2/passkeys resist AiTM phishing
   attacks while TOTP, SMS, and push-notification MFA
   do not. What property of the FIDO2 protocol makes
   the difference?

2. **AUDIT** Walk through five AWS IAM privilege
   escalation paths (iam:CreatePolicyVersion,
   iam:PassRole, lambda:CreateFunction, etc.) and
   describe how to detect each path using AWS IAM
   Access Analyzer or Cloudsplaining.

3. **DETECT** Describe the CloudTrail/log signals that
   indicate a SAML-based identity attack is in progress
   and what immediate containment actions to take.

---

*Identity & Access Management | IAM-017 | v5.0*