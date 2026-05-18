---
id: SEC-021
title: "Secure Coding Practices - First Principles"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-006, SEC-007, SEC-018
used_by: SEC-025, SEC-045, SEC-116
related: SEC-001, SEC-006, SEC-007, SEC-018, SEC-025, SEC-045, SEC-116
tags:
  - security
  - secure-coding
  - design-principles
  - owasp
  - sdlc
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/sec/secure-coding-practices-first-principles/
---

⚡ TL;DR - Secure coding is not a checklist of rules - it
is a set of durable design principles that apply across
languages, frameworks, and domains. The core principles
from Saltzer and Schroeder (1975) remain foundational:

1. **Least privilege** - components get only the permissions they need
2. **Economy of mechanism** - keep security-critical code simple
3. **Fail-safe defaults** - default to denial, not permission
4. **Complete mediation** - check every access, not just first
5. **Open design** - security should not depend on secrecy of mechanism
6. **Least common mechanism** - minimize shared state between components
7. **Psychological acceptability** - secure behavior should be easy behavior
8. **Defense in depth** - multiple independent layers

Applied in practice: validate all input, encode all output,
use parameterized queries, fail closed (deny on error),
never trust the client, keep secrets out of code,
log security events. These are the tactical expressions
of the underlying principles.

---

| #021 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, Developer Responsibility, Defense in Depth, Least Privilege | |
| **Used by:** | Security Mindset, Security Code Review, DevSecOps | |
| **Related:** | Security Problem, Defense in Depth, Least Privilege, DevSecOps, Security Code Review | |

---

### 🔥 The Problem This Solves

**THE SECURITY TRAINING PARADOX:**
Security training typically covers: "Don't do SQL injection.
Don't do XSS. Validate input. Encode output." These are
specific rules for specific vulnerabilities. But new
vulnerability classes emerge constantly: SSRF, deserialization,
prototype pollution, XXE. A developer trained only on rules
cannot recognize vulnerabilities they haven't specifically
learned about.

**PRINCIPLES VS RULES:**
A developer who understands the principle "never trust
input, process it as data not code" will recognize SQLi
AND XSS AND template injection AND command injection -
because they all violate the same underlying principle.
A developer who only knows "use parameterized queries"
for SQLi may miss template injection in a new framework
they haven't specifically been warned about.

Principles are the underlying theory. Rules are specific
applications of principles. Learning principles gives you
the ability to derive the rules in new contexts.

---

### 📘 Textbook Definition

**Saltzer and Schroeder (1975) - Eight Design Principles:**
The most cited security design principles paper. Still fully
applicable to modern web/cloud applications.

**1. Least Privilege:** Every component should have the minimum
access required. Covered in depth at SEC-018.

**2. Economy of Mechanism:**
Security-critical code should be as simple as possible.
Complex security mechanisms are hard to reason about and
more likely to have vulnerabilities. "Complexity is the
enemy of security." Prefer simple, auditable security
controls over complex ones.

**3. Fail-Safe Defaults:**
Access should be denied by default. Grant access explicitly.
If a decision cannot be made (error, unexpected input):
default to deny, not allow. "If in doubt, block it."
Application: return 403 on authorization error, not 200.
Close database connections on error, don't leave them open.

**4. Complete Mediation:**
Every access to every resource must be checked. Not just
the first access. Caching must not skip authorization.
Application: authorize on each API call, not just on login.
Resource retrieval: check ownership on every request.
(The IDOR bug is often a complete mediation failure.)

**5. Open Design:**
The security of a system should not depend on the secrecy
of its mechanism. Kerckhoffs' principle (1883): cryptographic
algorithms should be secure even if everything about the
system is public knowledge except the key. Apply: don't
hide your JWT algorithm or URL patterns as "security."
Security through obscurity fails when the secret leaks.

**6. Separation of Privilege:**
Two conditions should be required for access to sensitive
operations. Application: two-factor authentication. "Four-eyes
principle" for production deployments. Dual-key systems.

**7. Least Common Mechanism:**
Minimize shared resources between components. Shared state
creates attack surface. If one component is compromised
and it shares memory/filesystem/network with another:
the attack can spread. Application: per-service database users,
process isolation, container sandboxing.

**8. Psychological Acceptability:**
Security mechanisms should not make legitimate use harder.
If secure behavior is inconvenient: users will bypass it.
Application: auto-escaping templates (secure by default),
password managers (make strong passwords easy), HTTPS
everywhere (makes HTTP exception rather than default).
The principle: "make the secure choice the easy choice."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Secure coding principles give you a mental model to recognize
vulnerabilities in any context - not just the specific
vulns you've been trained on. The core: never trust inputs,
fail closed, validate everything, minimum permissions,
keep it simple.

**One analogy:**
> Security principles are like engineering principles
> (load distribution, failure modes, redundancy). An engineer
> who understands load distribution can design any load-bearing
> structure correctly - not just bridges they've specifically
> studied. An engineer who only knows "use X-type beam for
> bridges" struggles with novel structures. Security principles
> are the load distribution of software: internalize them
> and you can reason about new vulnerability classes from
> first principles.

---

### 🔩 First Principles Explanation

**Why "never trust the client" is foundational:**

```
CLIENT-SERVER SECURITY MODEL:

THE CLIENT IS AN ADVERSARY (worst-case design):
  The client is a browser/mobile app/curl command.
  The server has zero control over what code runs on the client.
  Attacker can:
    - Modify JavaScript in the browser (DevTools)
    - Intercept and modify HTTP requests (Burp Suite)
    - Send arbitrary HTTP requests (curl, Postman, Python)
    - Bypass client-side validation entirely

CLIENT-SIDE VALIDATION = USER EXPERIENCE, NOT SECURITY:
  HTML form: <input required minlength="8" pattern="[A-Z]+">
  User benefit: immediate feedback, no round trip.
  Security value: ZERO. Any attacker sends:
    curl -X POST /submit -d "field="
  Bypasses the HTML validation entirely.
  Server receives the empty value and processes it.

COMPLETE MEDIATION (Saltzer-Schroeder principle 4):
  Every single request must be validated server-side.
  Not just the first one. Not "the client already validated."
  Not "this comes from our mobile app so it's safe."
  
  The pattern: server assumes NOTHING about client behavior.
  Server validates: is this data within expected constraints?
  Server authorizes: does this user have permission for THIS resource?
  Server processes: uses parameterized queries, safe APIs.

ECONOMY OF MECHANISM (principle 2) IN PRACTICE:
  Security code should be short, simple, auditable.
  
  BAD: 200-line custom authentication middleware
    Hard to audit. Likely has edge cases.
  
  GOOD: Use battle-tested library (Passport, Spring Security)
    Thousands of users. Professionally audited. Known issues
    are public and patched.
  
  Custom crypto: never (see Cryptographic Agility vs Custom).
  Custom authentication: almost never.
  Use established, audited implementations.
  Complexity budget: spend it on business logic, not security plumbing.

FAIL-SAFE DEFAULTS (principle 3):
  Default to denial. Explicit allowance.
  
  BAD pattern:
    if user.role == "admin":
        allow_access()
    else:
        allow_access()  # Default: allow (fail-open)
    # Programmer forgot to handle non-admin case. Everyone can access.
  
  GOOD pattern:
    if user.role not in ALLOWED_ROLES:
        raise Forbidden()  # Default: deny (fail-safe)
    allow_access()
    # New role added? Denied until explicitly added to ALLOWED_ROLES.
```

---

### 🧪 Thought Experiment

**SCENARIO: Applying principles to discover a new vulnerability**

```
SCENARIO: Developer uses a new template engine they haven't
been specifically warned about. Template code:
  result = template.render(f"Hello, {user_name}!")

DEVELOPER'S RULE-BASED THINKING:
  "I've been trained on SQL injection. Is this SQL? No.
   I've been trained on XSS. Does this go into HTML? Not directly.
   Is there an OWASP rule about template engines? Not sure.
   Probably safe."

DEVELOPER'S PRINCIPLE-BASED THINKING:
  Principle: "User data should never be treated as code."
  
  Analysis: "This user_name value is being interpolated INTO
  a template string before passing to the template engine.
  The template engine will parse this interpolated result.
  
  If user_name = '{{7*7}}' (Jinja2 syntax):
  Template string becomes: 'Hello, {{7*7}}!'
  Template engine evaluates: '{{7*7}}' → 49
  Result: 'Hello, 49!'
  
  User input was executed as template code.
  This is SSTI (Server-Side Template Injection).
  Attacker can: execute arbitrary Python code on the server.
  
  FIX: Pass user_name as a variable, not interpolated into template:
  result = template.render('Hello, {{ name }}!', name=user_name)
  Template renders name as a value, not as template syntax."

PRINCIPLE APPLIED: User input is data, not code.
  If user input is concatenated into any language (SQL, HTML,
  shell, template syntax) before parsing: injection is possible.
  The specific language doesn't matter. The principle identifies the risk.
```

---

### 🧠 Mental Model / Analogy

> Secure coding principles are like the immune system's
> pattern recognition. The immune system doesn't have a
> specific response pre-programmed for every pathogen that
> has ever existed. It recognizes patterns: "this molecular
> pattern is foreign." New pathogens are recognized because
> they match the "foreign" pattern, not because they're
> specifically listed.
> Security principles work the same way: "user data being
> executed as code" is the foreign pattern. SQL injection,
> XSS, template injection, command injection all match this
> pattern. Principles give you pattern recognition. Rules
> give you specific pathogen responses. You need both, but
> principles scale to unknown threats.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Secure coding means writing software with security in mind
from the start, not adding it later. Core ideas: don't trust
what users send you, check everything, use the least
permission possible, fail safely when something goes wrong,
keep security code simple and well-tested.

**Level 2 - How to use it (junior developer):**
Practice the 10 OWASP Proactive Controls. Especially:
define security requirements, use safe APIs (parameterized
queries, auto-escaping templates), encode output, implement
access controls, protect secrets. These are principle-based
and apply to any language or framework.

**Level 3 - How it works (mid-level engineer):**
The Saltzer-Schroeder principles map directly to specific
security controls: "fail-safe defaults" → whitelist allowlists
rather than blacklists, return 403 on error, close connections
on failure. "Complete mediation" → re-authorize on every request,
no auth caching without validation. "Psychological acceptability"
→ security must be friction-free for developers (auto-escaping
templates) and users (password managers, SSO).

**Level 4 - Why it was designed this way (senior/staff):**
Saltzer and Schroeder's 1975 paper predates the internet as
we know it - it was about OS design for Multics. The principles
were derived from studying OS security design failures.
Yet they apply almost perfectly to web application security
50 years later. Why? Because the fundamental problems are
the same: managing access to shared resources, handling
untrusted input, designing for failure, keeping mechanisms
simple. The universality of these principles is evidence
that security design has deep invariants. New attack techniques
emerge, but they almost always represent a violation of a
principle that could have predicted them.

**Level 5 - Mastery (distinguished engineer):**
The hardest principle in modern systems is "economy of
mechanism" - modern security systems are necessarily complex
(OAuth 2.0, TLS 1.3, multi-party authorization). The
resolution: complexity at the infrastructure level (handled
by specialized systems with formal analysis), simplicity
at the application level (application calls the security
service, security service is the complex part). Zero trust
architecture attempts this: simple per-request authorization
("is this token valid for this resource?") even though the
underlying verification is complex. The application doesn't
implement the complexity - it calls a well-audited service.
This pattern (delegate security complexity to specialized
components) is how large systems maintain "economy of
mechanism" despite overall system complexity.

---

### ⚙️ How It Works (Mechanism)

**Principles mapped to OWASP Proactive Controls:**

```
SALTZER-SCHROEDER → OWASP PROACTIVE CONTROLS MAPPING:

Fail-Safe Defaults:
  → C7: Enforce Access Controls
    Default: deny. Allow only explicitly.
    if user not in authorized_roles: return 403

Least Privilege:
  → C3: Secure Database Access
    Per-service DB users. Minimal permissions.
    Read-only replicas for read-only services.

Complete Mediation:
  → C7: Enforce Access Controls (every request)
  → C4: Encode and Escape Data (every output context)
    Not just on some endpoints. Every single access.

Economy of Mechanism:
  → C2: Use Security Frameworks and Libraries
    Don't implement your own auth. Use Spring Security,
    Passport, Django, etc. Battle-tested. Audited.

Open Design (Kerckhoffs):
  → C10: Handle All Errors and Exceptions
    Don't rely on "attackers don't know our URL structure."
    Security must hold even if mechanism is known.
    Exception messages: don't reveal system internals.

Psychological Acceptability:
  → C2: Use Security Frameworks
    Auto-escaping templates (secure by default).
    Parameterized query APIs (hard to use incorrectly).
    Make secure path friction-free.

PRACTICAL IMPLEMENTATION CHECKLIST:
  [ ] Input validation: allowlist, not denylist
  [ ] Output encoding: context-aware
  [ ] SQL: parameterized queries always
  [ ] Secrets: env vars / secrets manager, not code
  [ ] Auth: use established library, not custom
  [ ] Authz: check on every request
  [ ] Errors: fail closed, don't reveal internals
  [ ] Logging: log security events (login, authz failure)
  [ ] Dependencies: scan for known vulns (Snyk, Dependabot)
  [ ] HTTPS: all traffic, including internal
```

---

### 💻 Code Example

**Principles applied in Python:**

```python
# PRINCIPLE: Fail-safe defaults
# BAD: allow on error (fail-open)
def get_user_data(user_id, requester_id):
    try:
        if not is_authorized(requester_id, user_id):
            return None
        return fetch_user(user_id)
    except DatabaseError:
        return fetch_user(user_id)  # BAD: error = allow access
        # Exception silently bypasses authorization check

# GOOD: deny on error (fail-closed)
def get_user_data(user_id: int, requester_id: int):
    """Fail-safe: any error results in denial, not access."""
    try:
        if not is_authorized(requester_id, user_id):
            raise PermissionError(f"Not authorized for user {user_id}")
        return fetch_user(user_id)
    except DatabaseError:
        raise PermissionError("Authorization check failed")
        # Error → deny. Attacker cannot trigger error to bypass auth.

# PRINCIPLE: Complete mediation
# BAD: cache authorization, skip re-check
_auth_cache = {}
def get_resource(resource_id, user_id):
    # Cache hit: skip authorization check
    if resource_id in _auth_cache.get(user_id, []):
        return fetch_resource(resource_id)
    if is_authorized(user_id, resource_id):
        _auth_cache.setdefault(user_id, []).append(resource_id)
        return fetch_resource(resource_id)
    raise PermissionError()
    # Problem: resource permissions can change. Cache is stale.
    # Revoked access still works while cache is valid.

# GOOD: check authorization on every request (with fast auth service)
def get_resource(resource_id: int, user_id: int):
    """Authorization checked on every request. No stale cache."""
    # Use a fast authorization service (e.g., OPA, Casbin)
    # that performs sub-millisecond decisions
    if not authz_service.can(user_id, 'read', resource_id):
        raise PermissionError()
    return fetch_resource(resource_id)

# PRINCIPLE: Economy of mechanism
# BAD: custom JWT implementation
def verify_jwt(token):
    parts = token.split('.')
    header = base64.decode(parts[0])
    # ... custom validation ...
    # Custom crypto is almost always wrong somewhere

# GOOD: use battle-tested library
import jwt  # PyJWT - well-audited, widely used
def verify_jwt(token: str, secret: str) -> dict:
    """Verify JWT using established library."""
    return jwt.decode(
        token,
        secret,
        algorithms=['HS256'],  # Explicit algorithm (prevents alg=none attack)
        options={"verify_exp": True}
    )
```

---

### ⚖️ Comparison Table

| Approach | When it matters | Security impact |
|:---|:---|:---|
| **Rules-based thinking** | Known, documented vulnerability classes | Catches specific known vulns. Misses novel variants. |
| **Principles-based thinking** | Any code, any context | Catches patterns. Can reason about unknown vulns. |
| **Frameworks + libraries** | Authentication, crypto, authorization | Leverage expert implementations. Economy of mechanism. |
| **Secure by default** | Template engines, API design | Reduces developer error rate. Psychological acceptability. |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| "We have a WAF so we don't need secure coding" | A WAF (Web Application Firewall) is a defense-in-depth layer that adds latency, requires rules maintenance, and can be bypassed. It is not a substitute for secure coding. The WAF sits in front of the application. If a vulnerability makes it past the WAF (and they do - WAFs are signature-based and can be bypassed), there is no second defense. Secure coding fixes vulnerabilities in the application itself. WAF reduces surface exposure. Both are needed for defense in depth. |
| "Security is hard, so only security specialists should think about it" | Security specialists cannot scale. A 5-person security team cannot review every PR from 200 developers. Security principles, embedded in development practice, scale with the team. When developers internalize "validate input, encode output, fail closed": security is built in, not bolted on. Security specialists provide oversight, tooling, and guidance - not complete coverage. |

---

### 🚨 Failure Modes & Diagnosis

**Common principle violations in code review:**

```python
# FLAG 1: Missing input validation at API boundary
@app.post('/api/users/<user_id>/role')
def update_role(user_id):
    role = request.json.get('role')  # No validation!
    # Fix: validate role against allowlist
    VALID_ROLES = {'viewer', 'editor', 'admin'}
    if role not in VALID_ROLES:
        return {'error': 'Invalid role'}, 400
    db.update_user_role(user_id, role)

# FLAG 2: Error revealing internals (open design violation)
@app.errorhandler(500)
def server_error(e):
    return str(e), 500  # Returns exception traceback to client!
    # Fix: log internally, return generic message
    # logging.exception("Server error")
    # return {'error': 'Internal server error'}, 500

# FLAG 3: Client-side-only validation (complete mediation failure)
@app.post('/api/transfer')
def transfer():
    # Comment in code: "Amount validated on client side"
    amount = request.json['amount']
    # No server-side validation. Attacker bypasses client.
    # Fix: validate amount is positive, within limits, etc.
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {'error': 'Invalid amount'}, 400
    if amount > 10000:
        return {'error': 'Exceeds daily limit'}, 400

# FLAG 4: Hardcoded secret (Kerckhoffs violation - but backwards:
# relying on secrecy of mechanism)
API_KEY = "abc123secret"  # Hardcoded in source code
# Fix: use environment variable or secrets manager
import os
API_KEY = os.environ['API_KEY']
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Problem` - why secure coding is necessary
- `Defense in Depth` - layered security principles
- `Principle of Least Privilege` - one of the core principles

**Builds on this:**
- `Security Mindset` - thinking like an attacker
- `Security Code Review Checklist` - applying principles in review
- `DevSecOps Pipeline Design` - principles in CI/CD

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 8 PRINCIPLES │ Least privilege, Economy of mechanism,    │
│ (Saltzer &   │ Fail-safe defaults, Complete mediation,   │
│ Schroeder)   │ Open design, Separation of privilege,     │
│              │ Least common mechanism, Psych. acceptab.  │
├──────────────┼───────────────────────────────────────────┤
│ PRACTICE     │ Validate input (allowlist), encode output │
│              │ Parameterized queries, fail closed        │
│              │ Secrets in env, not code                  │
│              │ Auth every request, not just first        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rules catch known vulns.                  │
│              │ Principles catch unknown vulns too.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "User data is data, never code.           │
│              │  Deny by default. Check everything.       │
│              │  Keep security simple. Use libraries."    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security properties are easier to maintain when the secure
path is the easy path." The principle of psychological
acceptability is actually an engineering efficiency insight:
if you design the API so that the WRONG approach requires
extra effort and the RIGHT approach is the default:
developers get security right by default. Auto-escaping
templates enforce this: the default (use `{{ variable }}`)
is secure. The insecure path (`{{ variable | safe }}`)
requires extra effort. This design eliminates an entire
class of security review burden. Applied to your own APIs:
make the input validation, the correct status codes, the
parameterized queries the natural, easy way to use your API.
Security through ergonomics scales better than security
through rules.

---

### 💡 The Surprising Truth

The eight Saltzer-Schroeder principles (1975) were written
for operating system design on timesharing systems. They
were derived from studying security failures in Multics
and other 1970s systems. Yet every OWASP Top 10 vulnerability
from 2023 is a direct violation of one or more of these
principles:
- A01 Broken Access Control: complete mediation + fail-safe defaults
- A02 Cryptographic Failures: economy of mechanism (custom crypto)
- A03 Injection: user data treated as code (open design inversion)
- A04 Insecure Design: principles not applied at design stage
- A08 Integrity Failures: open design (trusting unsigned data)

50 years have not changed the fundamental security problems.
The attack methods evolved. The underlying principles that
prevent them did not. When you internalize Saltzer and
Schroeder, you've internalized the principles that could
have prevented most CVEs from the past decade.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **NAME** and briefly describe the eight Saltzer-Schroeder
   principles and give a modern application for each.
2. **IDENTIFY** which principle is violated by a given
   vulnerability (IDOR = complete mediation, SQLi = user data
   as code/economy of mechanism failure, CSRF = no separation
   of privilege for state changes).
3. **APPLY** fail-safe defaults in code: default to deny,
   exception handling that doesn't grant access on error.
4. **EXPLAIN** why principles scale to novel vulnerabilities
   while rules don't.

---

### 🎯 Interview Deep-Dive

**Q: What are the core principles of secure software design?**

*Why they ask:* Distinguishes candidates who understand
security fundamentals from those who only know specific
vulnerability patches. Staff/principal engineering interviews.

*Strong answer includes:*
- Reference Saltzer and Schroeder (1975) - demonstrates depth.
- Key principles with practical examples:
  Least privilege: per-service DB users, scoped IAM roles.
  Fail-safe defaults: deny by default, return 403 on auth error.
  Complete mediation: re-authorize every request, not just login.
  Economy of mechanism: use established libraries (Spring Security,
  PyJWT) not custom auth. Complex custom code = complex attack surface.
  Psychological acceptability: make secure choice easy (auto-escaping,
  parameterized query default).
- The principle insight: rules catch known vulnerabilities.
  Principles allow you to reason about unknown vulnerability classes.
  SSTI is SQLi is XSS: all violate "user data is data, not code."
- Practical: OWASP Proactive Controls are the tactical
  expression of these principles. Know both the principle
  and its practical application.