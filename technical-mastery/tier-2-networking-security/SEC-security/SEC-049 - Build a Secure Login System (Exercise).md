---
id: SEC-049
title: "Build a Secure Login System (Exercise)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-014, SEC-016, SEC-018, SEC-034, SEC-035, SEC-039, SEC-040, SEC-041, SEC-042, SEC-043
used_by: SEC-067, SEC-077
related: SEC-014, SEC-016, SEC-018, SEC-034, SEC-035, SEC-039, SEC-040, SEC-045, SEC-046
tags:
  - security
  - authentication
  - login
  - exercise
  - bcrypt
  - csrf
  - session
  - rate-limiting
  - audit-logging
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/sec/secure-login-exercise/
---

⚡ TL;DR - A secure login system requires combining multiple
independent security controls. Each one is insufficient alone;
together they create defense-in-depth. This entry provides a
complete, production-ready secure login implementation in Python.

**The eight security controls in a secure login:**
1. **Bcrypt** for password verification (adaptive hashing)
2. **Rate limiting** (prevent brute force)
3. **CSRF token** (prevent cross-site request forgery)
4. **HttpOnly + Secure + SameSite cookie** (prevent token theft)
5. **Session regeneration on login** (prevent session fixation)
6. **Generic error messages** (prevent user enumeration)
7. **Constant-time comparison** (prevent timing oracle)
8. **Audit logging** of login attempts

---

| #049 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Authentication, JWT, Session Security, CSRF Prevention, Bcrypt, API Security, Security Code Review, Error Handling, IDOR | |
| **Used by:** | Business Logic Vulnerabilities, Security Testing in CI/CD | |
| **Related:** | Authentication Decision Tree, Hardcoded Credentials, Session Security | |

---

### 🔥 The Problem This Solves

**WHY TYPICAL LOGIN IMPLEMENTATIONS ARE INSECURE:**

```
COMMON VULNERABILITIES IN LOGIN IMPLEMENTATIONS:

1. PLAIN TEXT PASSWORD STORAGE:
   db.users.insert({email: email, password: password})
   → Password stolen in DB breach → all passwords exposed.
   Fix: bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

2. NO RATE LIMITING:
   for password in wordlist:
       post('/login', {username: 'admin', password: password})
   → Iterate millions of passwords per minute.
   Fix: max 5 attempts per IP per 15 minutes.

3. USER ENUMERATION VIA ERROR MESSAGE:
   if not user: return "User not found"      # BAD: reveals username validity
   if not valid_pass: return "Wrong password" # BAD: reveals user exists
   Fix: "Invalid username or password" for both cases.

4. CSRF ON LOGIN FORM:
   Attacker creates page: <form action="https://target.com/login" ...>
   User visits attacker's page → login form submitted cross-site.
   If user has active session from old account → session fixation.
   Fix: CSRF token validates the request came from your login page.

5. SESSION FIXATION:
   GET /login → session_id=known_id (set before auth)
   POST /login → still session_id=known_id (not regenerated!)
   Attacker who knew pre-auth session ID now has authenticated session.
   Fix: regenerate session ID immediately on successful login.

6. INSECURE SESSION COOKIE:
   Set-Cookie: session=abc123 (no Secure, no HttpOnly, no SameSite)
   → Network sniffing, JavaScript XSS, CSRF can steal/use session.
   Fix: Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
```

---

### 📘 Textbook Definition

**Defense in Depth for Authentication:** Combining multiple
independent security controls such that a single failure in any
one control does not result in a breach. A login system with:
- Bcrypt alone (no rate limiting): brute-forceable given enough time
- Rate limiting alone (no bcrypt): stolen hash database leaks passwords
- CSRF token alone (no session regeneration): fixation still possible
- All eight controls: each attack requires defeating multiple controls simultaneously

**Authentication vs Authorization:**
Authentication: "Who are you?" (verified by login)
Authorization: "What can you do?" (checked on each resource access)
Login systems handle authentication. Authorization (IDOR checks,
role-based access) must be implemented separately on every
resource endpoint.

**OWASP ASVS (Application Security Verification Standard):**
Level 1 (basic) login requirements: bcrypt/Argon2, account lockout,
generic error messages, CSRF token, session regeneration, secure cookies.
Level 2 (standard): + audit logging, anomaly detection.
Level 3 (advanced): + MFA, phishing-resistant credentials (WebAuthn).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A secure login isn't one feature - it's eight security controls
working together. If you implement six of them correctly and
miss two, those two represent distinct attack vectors.

**One analogy:**
> Secure login is like a bank vault with multiple locks.
> Bcrypt (heavy vault door), rate limiting (alarm on too many
> wrong combinations), CSRF token (key that only the bank has),
> session regeneration (change the combination after use),
> secure cookies (keep the key in a locked case, not visible to passers-by),
> generic error messages (vault says "denied", not "wrong digit 3 of 4").
> Audit logging (every attempt on camera). Each lock is necessary.
> A vault with six of eight locks is still vulnerable to
> attacks that target the two missing ones.

---

### 🔩 First Principles Explanation

**Security controls and the attacks they prevent:**

```
CONTROL → ATTACK IT PREVENTS → HOW FAILURE LOOKS

1. BCRYPT (adaptive password hashing):
   Attack: offline dictionary attack on stolen hash database
   Failure: MD5/SHA256 hashed passwords → 14B MD5 hashes/sec on GPU.
     10,000 user accounts cracked in minutes.
   Protection: bcrypt at cost=12 → 100 attempts/sec max.
     10,000 user accounts → 100 seconds.
     PLUS: per-user salt → rainbow tables useless.
     PLUS: adaptive: increase cost as hardware improves.

2. RATE LIMITING (per-IP or per-account):
   Attack: brute force login from single IP or distributed botnet
   Failure without: 1M password attempts per minute (automated).
   Protection: 5 attempts per account per 15 minutes.
     After 5 failures: lock account for 15 minutes.
     Returns same error as wrong password (no lockout confirmation = no enumeration).

3. CSRF TOKEN:
   Attack: cross-site form submission (CSRF)
   Failure without: attacker can create a page that submits
     your login form (or logout form, or password change form).
   Protection: form contains unique token tied to user's session.
     Cross-site form cannot know the token. Submission rejected.

4. HTTPONLY + SECURE + SAMESITE COOKIE:
   Attack: XSS token theft, network sniffing, CSRF
   Failure without:
     Missing HttpOnly: JavaScript XSS → document.cookie → steal token
     Missing Secure: HTTP request sends session cookie → sniffing
     Missing SameSite: cross-site requests include session cookie → CSRF
   Protection:
     HttpOnly: JavaScript cannot read cookie
     Secure: cookie only sent over HTTPS
     SameSite=Lax: cookie not sent on cross-site POST requests

5. SESSION REGENERATION ON LOGIN:
   Attack: session fixation
   Failure without: attacker injects known session ID (via URL or cookie
     injection), victim logs in with that session ID, attacker now
     has authenticated access with the known session ID.
   Protection: on successful login → delete old session → create new session
     with new session ID → attacker's known ID is invalidated.

6. GENERIC ERROR MESSAGES:
   Attack: user enumeration
   Failure without: "User not found" → attacker knows which usernames exist.
     Username list → target for credential stuffing, phishing.
   Protection: "Invalid username or password" for ALL failures.
     Attacker cannot distinguish wrong username from wrong password.

7. CONSTANT-TIME COMPARISON:
   Attack: timing oracle on CSRF token or password comparison
   Failure without: early-exit string comparison leaks timing info.
     'AAAA' == 'AAAB' → 4 character iterations before finding difference.
     Attacker measures response time to infer correct characters.
   Protection: hmac.compare_digest() or bcrypt.checkpw() for all
     security-sensitive comparisons. Always constant time.
     (Note: bcrypt.checkpw handles timing for passwords;
      for CSRF tokens: use hmac.compare_digest)

8. AUDIT LOGGING:
   Attack: undetected brute force, account takeover
   Failure without: attacks leave no trace. SIEM cannot alert.
     Incident response has no evidence.
   Protection: log all login attempts (success + failure) with:
     timestamp, IP, username (not password), result (success/failure).
     Rate limiting based on this log.
     SIEM alert on unusual patterns.
```

---

### 🧪 Thought Experiment

**SCENARIO: Finding the weakest link in your existing login implementation**

```
SECURITY REVIEW CHECKLIST (self-assessment):

□ 1. PASSWORD STORAGE
  Command: SELECT password FROM users LIMIT 1;
  Good: starts with '$2b$12$' (bcrypt cost 12)
  Bad: MD5 (32 hex chars), SHA256 (64 hex chars), plaintext
  If bad: bcrypt migration required (re-hash on next login)

□ 2. RATE LIMITING
  Test: POST /login 10 times with wrong password in 10 seconds.
  Good: returns 429 Too Many Requests on attempt 5+.
  Bad: all 10 return 401 with no throttling.
  Check: is rate limit per-account or per-IP? Both is ideal.
    Per-IP only: distributed botnet bypasses it.
    Per-account: can lock out legitimate users (DOS risk).
    Both with progressive delay: best balance.

□ 3. CSRF TOKEN
  Test: POST /login with valid credentials but no CSRF token.
  Good: returns 403 CSRF token missing/invalid.
  Bad: returns 200 (successful login without CSRF token).
  Also: is the CSRF token unique per-request or per-session?
    Per-session: token reuse risk if page is cached.
    Per-request: better (regenerated on each page load).

□ 4. COOKIE ATTRIBUTES
  Check: Developer Tools → Application → Cookies → login cookie.
  Required: HttpOnly = yes, Secure = yes, SameSite = Lax or Strict.
  Also check: Session domain/path (not too broad).

□ 5. SESSION REGENERATION
  Test: 
    1. GET /login → note session cookie value (before login).
    2. POST /login (successful).
    3. Note new session cookie value (after login).
    4. Are they different? They MUST be different.
  Bad: session ID same before and after login = fixation vulnerability.

□ 6. ERROR MESSAGES
  Test: POST /login {username: "nonexistent@test.com", password: "wrong"}
  Test: POST /login {username: "real@user.com", password: "wrong"}
  Good: identical error message for both.
  Bad: different messages reveal whether username exists.

□ 7. TIMING
  Test: measure response time for existing vs non-existing user
    (with wrong password for both).
  Good: response times are indistinguishable (within ~50ms variance).
  Bad: >100ms difference = timing oracle (user enumeration via timing).

□ 8. AUDIT LOGGING
  Test: check application/server logs after failed login attempt.
  Good: log entry with: timestamp, IP, username, result=FAILURE.
  Bad: no log entry, or log entry missing IP or username.
```

---

### 🧠 Mental Model / Analogy

> Defense-in-depth in login security is like the security of
> a car: multiple independent systems (crumple zones, seatbelts,
> airbags, ABS, stability control) each designed for different
> failure scenarios. No single system is sufficient.
> Crumple zones work in head-on collision. Seatbelts work when
> crumple zones are insufficient force alone. Airbags supplement
> seatbelts. ABS prevents loss of control before collision.
> Stability control prevents the collision.
>
> Each system is independent: failing one doesn't fail others.
> ABS failure doesn't break seatbelts. Bcrypt failure (chosen
> wrong algorithm) doesn't disable rate limiting.
> Mutual reinforcement: each attacker layer requires defeating
> a different system. Rate limiting exhausted first (must spread
> attacks). Bcrypt slows verification. Session regeneration
> invalidates fixation. Generic errors prevent enumeration.
> All eight together require an attacker to defeat each one.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A secure login needs: a slow password hasher (bcrypt), a limit on how many wrong attempts are allowed (rate limiting), a way to verify the form came from your site (CSRF token), a properly secured cookie (HttpOnly, Secure, SameSite), same error message whether the username or password was wrong, and a log of all login attempts. Miss any one: a different type of attack still works.

**Level 2 - How to use it (junior developer):**
Use a security-focused authentication library where possible (Django's built-in auth, Spring Security, Passport.js). These implement most controls correctly. For custom implementation: `bcrypt.checkpw()` (always), `secrets.compare_digest()` for CSRF (never `==`), `session.regenerate()` on login, `Set-Cookie: HttpOnly; Secure; SameSite=Lax`, rate limiting middleware (Flask-Limiter, express-rate-limit), and structured logging for audit trail.

**Level 3 - How it works (mid-level engineer):**
The interdependencies matter: rate limiting prevents brute force against bcrypt's ~300ms verification time. Without bcrypt's slowness, rate limiting would need to be extremely aggressive. Without rate limiting, bcrypt gives only 10 seconds of protection before resource exhaustion. CSRF token must be compared constant-time (hmac.compare_digest) because even a correctly-generated CSRF token is vulnerable to timing attacks if compared with ==. Session regeneration prevents fixation attacks that exploit the gap between "session exists" and "session is authenticated." Generic error messages AND constant-time comparison must BOTH be implemented: if timing is constant but messages differ, enumeration is still possible; vice versa.

**Level 4 - Why it was designed this way (senior/staff):**
Authentication is an adversarial problem: attackers are specifically trying to defeat each control. Security controls must be designed with the attacker's perspective in mind (threat model). For each control: what does the attacker gain if this control is absent? How does the attacker defeat this control if it IS present? For bcrypt: absent → fast brute force; present → defeated by GPU farms (Argon2 is better but bcrypt is sufficient). For rate limiting: present but per-IP only → distributed botnet with many IPs. Defense: detect distributed attempts via behavior (many accounts, slow rate, different IPs → shared CAPTCHA). Each control has an adversarial bypass; defense-in-depth ensures bypassing one control is not sufficient.

**Level 5 - Mastery (distinguished engineer):**
Production authentication systems at scale add: risk-based authentication (normal user behavior vs anomalous → require MFA), device fingerprinting (new device → send email notification), passive velocity checks (user "logged in" from London at 2pm and New York at 2:03pm → impossible travel → flag), and integration with threat intelligence feeds (known bad IPs → challenge or block). Beyond username/password: WebAuthn/FIDO2 eliminates the password entirely - private key never leaves the device, phishing impossible (cryptographically bound to origin). The password-based login system implemented here is necessary knowledge for understanding what's being replaced - but the long-term direction is credential-free authentication.

---

### ⚙️ How It Works (Mechanism)

**Complete secure login flow:**

```
SECURE LOGIN - COMPLETE FLOW:

PRE-REQUEST (page load):
  User navigates to /login
  Server: generate CSRF token (stored in session or signed cookie)
  Server: render login form with CSRF token in hidden field
  Response: Set-Cookie: session=pre-auth-session; HttpOnly; Secure; SameSite=Lax

LOGIN ATTEMPT:
  User submits form:
    POST /login
    Cookie: session=pre-auth-session
    Body: {username, password, csrf_token}

SERVER PROCESSING:
  1. CSRF check:
     Retrieve expected token from session/signed cookie.
     hmac.compare_digest(expected_token, submitted_token)
     If mismatch: 403 FORBIDDEN. Log: CSRF validation failed.
  
  2. Rate limit check (before DB query):
     Redis: GET rate_limit:login:{ip}:{username}
     If >= 5 attempts: 429 TOO MANY REQUESTS.
     Log: Rate limit exceeded.
  
  3. Database lookup:
     user = db.get_user_by_email(username)  # Timing-normalized below
  
  4. Password verification (timing-normalized):
     stored_hash = user.password_hash if user else DUMMY_HASH
     valid = bcrypt.checkpw(password.encode(), stored_hash)
     # bcrypt.checkpw: constant-time comparison built-in
     # DUMMY_HASH: prevents timing difference for non-existent users
  
  5. Login result handling:
     If NOT (valid and user):
       Redis: INCR rate_limit:login:{ip}:{username}
       Redis: EXPIRE rate_limit:login:{ip}:{username} 900  # 15 min TTL
       Log: login_failed: {timestamp, ip, username}
       Return: 401 "Invalid username or password"  # SAME MESSAGE ALWAYS
     
     If valid and user:
       Log: login_success: {timestamp, ip, user_id}
       # SESSION REGENERATION (prevent fixation):
       session.invalidate()         # Delete old session
       session_id = secrets.token_urlsafe(32)  # New random ID
       session.create(session_id, {user_id: user.id, roles: user.roles})
       
       Response:
         Status: 302 Redirect to /dashboard
         Set-Cookie: session={session_id}; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
         # Old session ID no longer exists → fixation attack defeated.
```

---

### 💻 Code Example

**Complete FastAPI secure login implementation:**

```python
# Complete secure login - FastAPI + Redis + PostgreSQL

import hmac
import secrets
import logging
import bcrypt
from datetime import datetime

from fastapi import FastAPI, Form, Request, HTTPException, Response
from redis import Redis
from sqlalchemy import select
from models import User, db_session

app = FastAPI()
redis = Redis(host='localhost', port=6379, decode_responses=True)
logger = logging.getLogger("auth.audit")

# Pre-compute dummy hash to normalize timing for non-existent users
# (computed once at startup, not per request)
DUMMY_HASH = bcrypt.hashpw(b"dummy-normalize-timing", bcrypt.gensalt(12))

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes

@app.get("/login")
async def get_login_page(request: Request, response: Response):
    """Render login page with CSRF token."""
    csrf_token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = csrf_token  # Store in session
    # Return your HTML template with csrf_token in hidden field
    return {"csrf_token": csrf_token}

@app.post("/login")
async def post_login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    ip = request.client.host
    rate_key = f"rate_limit:login:{ip}:{username}"
    
    # 1. CSRF VALIDATION (constant-time)
    expected_csrf = request.session.get("csrf_token")
    if not expected_csrf:
        raise HTTPException(403, "Missing CSRF token")
    if not hmac.compare_digest(expected_csrf, csrf_token):
        logger.warning(f"CSRF_FAILED ip={ip} username={username}")
        raise HTTPException(403, "Invalid CSRF token")
    
    # 2. RATE LIMITING
    attempts = redis.get(rate_key)
    if attempts and int(attempts) >= MAX_ATTEMPTS:
        logger.warning(f"RATE_LIMIT_EXCEEDED ip={ip} username={username}")
        raise HTTPException(
            429,
            "Too many login attempts. Try again in 15 minutes."
        )
    
    # 3. USER LOOKUP (timing-normalized below)
    async with db_session() as db:
        result = await db.execute(
            select(User).where(User.email == username)
        )
        user = result.scalar_one_or_none()
    
    # 4. BCRYPT VERIFICATION (always run, even for non-existent user)
    stored_hash = user.password_hash if user else DUMMY_HASH
    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )
    
    # 5. AUTHENTICATION RESULT
    if not (password_valid and user):
        # Increment rate limit counter (failure)
        pipe = redis.pipeline()
        pipe.incr(rate_key)
        pipe.expire(rate_key, LOCKOUT_SECONDS)
        pipe.execute()
        
        # Audit log: failure
        logger.info(
            f"LOGIN_FAILED ip={ip} username={username} "
            f"ts={datetime.utcnow().isoformat()}"
        )
        
        # GENERIC MESSAGE (never reveal which part was wrong)
        raise HTTPException(401, "Invalid username or password")
    
    # 6. SESSION REGENERATION (prevent session fixation)
    old_session_id = request.session.session_id
    request.session.clear()          # Invalidate old session
    request.session.regenerate()     # New session ID
    
    # 7. SET AUTHENTICATED SESSION
    request.session["user_id"] = str(user.id)
    request.session["roles"] = user.roles
    
    # Clear rate limit on success
    redis.delete(rate_key)
    
    # 8. AUDIT LOG: success
    logger.info(
        f"LOGIN_SUCCESS ip={ip} user_id={user.id} "
        f"ts={datetime.utcnow().isoformat()}"
    )
    
    # Secure cookie set by session middleware (configured at app startup):
    # session_cookie: {httponly: true, secure: true, samesite: "lax"}
    return Response(
        status_code=302,
        headers={"Location": "/dashboard"}
    )

@app.post("/logout")
async def logout(request: Request, response: Response):
    """Invalidate session server-side on logout."""
    user_id = request.session.get("user_id")
    request.session.clear()  # Delete session from Redis
    logger.info(f"LOGOUT user_id={user_id}")
    return Response(status_code=302, headers={"Location": "/login"})
```

---

### ⚖️ Comparison Table

| Control | Attack Prevented | Without This Control |
|:---|:---|:---|
| **Bcrypt** | Offline dictionary attack on stolen hashes | All passwords cracked in minutes after breach |
| **Rate limiting** | Online brute force | 1M attempts/minute automated attack |
| **CSRF token** | Cross-site form submission | Attacker forces logout, login, actions |
| **HttpOnly cookie** | XSS session theft | XSS → steal session → account takeover |
| **Secure cookie** | Network sniffing | HTTP request → session visible on network |
| **SameSite cookie** | CSRF via session cookie | Cross-site requests use authenticated session |
| **Session regeneration** | Session fixation | Attacker with pre-auth session ID → auth session |
| **Generic errors** | User enumeration | Credential stuffing with valid username list |
| **Constant-time compare** | Timing oracle | Timing attack reveals correct CSRF characters |
| **Audit logging** | Undetected attack, no forensics | Incident response has no evidence |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Rate limiting per-IP is sufficient to prevent brute force | IP-based rate limiting is effective against naive brute force attacks from a single IP. Sophisticated attackers use botnets: thousands of IPs, each making 1-2 requests. The per-IP rate limit is never triggered. Per-account rate limiting (5 attempts per account regardless of IP) is more effective for credential stuffing. However, per-account lockout enables denial-of-service: attacker intentionally locks out accounts they don't own. Best approach: progressive delays (not hard lockout), account lockout notification via email, CAPTCHA after failures, and anomaly detection for distributed patterns. |
| Session regeneration only matters for web applications with URL-based sessions | Session fixation is relevant to any session-based system including mobile apps and APIs. In mobile apps: a fixation attack might be less practical (requires network-level injection), but regenerating session tokens on authentication is still best practice. In APIs with JWT: the "session" is the JWT itself. On login: always issue a fresh JWT (short-lived access + new refresh token), not reuse any existing token. The principle is the same: a new authentication event should produce a new, unpredictable credential, unrelated to any pre-authentication state. |

---

### 🚨 Failure Modes & Diagnosis

**Testing your login implementation security:**

```
AUTOMATED SECURITY TEST SUITE:

def test_login_security(client):
    
    # Test 1: Wrong password returns 401 (not 403 which reveals too much)
    resp = client.post('/login', data={
        'username': 'real@user.com',
        'password': 'wrongpassword',
        'csrf_token': get_csrf_token(client)
    })
    assert resp.status_code == 401
    
    # Test 2: Non-existent user returns same message as wrong password
    resp1 = client.post('/login', data={
        'username': 'notexist@test.com',
        'password': 'wrong',
        'csrf_token': get_csrf_token(client)
    })
    resp2 = client.post('/login', data={
        'username': 'real@user.com',
        'password': 'wrong',
        'csrf_token': get_csrf_token(client)
    })
    # Must be identical (same status code AND same response body)
    assert resp1.status_code == resp2.status_code
    assert resp1.json() == resp2.json()  # No user enumeration
    
    # Test 3: Rate limiting kicks in after 5 attempts
    for i in range(5):
        client.post('/login', data={
            'username': 'victim@user.com',
            'password': 'wrong' + str(i),
            'csrf_token': get_csrf_token(client)
        })
    resp = client.post('/login', data={
        'username': 'victim@user.com',
        'password': 'wrong',
        'csrf_token': get_csrf_token(client)
    })
    assert resp.status_code == 429  # Rate limited
    
    # Test 4: CSRF token required (submission without token rejected)
    resp = client.post('/login', data={
        'username': 'real@user.com',
        'password': 'correctpassword'
        # No csrf_token
    })
    assert resp.status_code in [400, 403]
    
    # Test 5: Session ID changes on successful login
    pre_session = client.cookies.get('session')
    client.post('/login', data={
        'username': 'real@user.com',
        'password': 'correctpassword',
        'csrf_token': get_csrf_token(client)
    })
    post_session = client.cookies.get('session')
    assert pre_session != post_session  # Session regenerated
    
    # Test 6: Session cookie has required attributes
    # Inspect Set-Cookie header from login response
    set_cookie = login_response.headers['Set-Cookie']
    assert 'HttpOnly' in set_cookie
    assert 'Secure' in set_cookie
    assert 'SameSite=Lax' in set_cookie or 'SameSite=Strict' in set_cookie
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication Fundamentals` - authentication concepts
- `JWT` - token-based alternative to sessions
- `CSRF Prevention` - CSRF token implementation
- `Bcrypt for Password Hashing` - password storage details
- `Session Security` - secure cookie configuration

**Builds on this:**
- `Business Logic Vulnerabilities` - applying login security to complex business logic
- `Security Testing in CI/CD` - automating these tests

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 8 CONTROLS   │ bcrypt, rate-limit, csrf, httponly+secure │
│              │ +samesite, regenerate session, generic err│
│              │ constant-time compare, audit log          │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ ALWAYS run bcrypt (DUMMY_HASH for nouser) │
│              │ hmac.compare_digest for CSRF tokens       │
├──────────────┼───────────────────────────────────────────┤
│ RATE LIMIT   │ Per-account AND per-IP; 5 attempts/15min  │
├──────────────┼───────────────────────────────────────────┤
│ COOKIE       │ HttpOnly; Secure; SameSite=Lax            │
├──────────────┼───────────────────────────────────────────┤
│ AUDIT LOG    │ All attempts: {ts, ip, username, result}  │
│              │ Never log the password                    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security through multiple independent controls, not one strong one."
Any single control can be bypassed: a sufficiently large botnet bypasses
per-IP rate limiting; a GPU cluster eventually defeats bcrypt;
CSRF tokens can be extracted by XSS; session fixation bypasses
session-based controls. But each control requires a DIFFERENT attack
technique. An attacker who can bypass rate limiting (botnet) cannot
use the same technique to bypass bcrypt (requires offline compute).
An attacker who can extract CSRF tokens (XSS) still needs to bypass
rate limiting to brute-force. Defense-in-depth requires attackers
to successfully execute multiple different attack techniques
simultaneously. Each additional layer multiplies the cost and
complexity of a successful attack.

---

### 💡 The Surprising Truth

A 2022 analysis of 10 million leaked passwords found that
password policies ("must contain uppercase, number, special character")
do not meaningfully improve security. Users respond predictably:
they capitalize the first letter, add "1!" at the end, and use
common words. "Password1!" is technically compliant with most
password policies but is in every wordlist. Password length (12+
characters) is far more important than complexity rules. The NIST
SP 800-63B guidelines (current federal standard) explicitly
recommend: check against known bad password lists (not complexity
rules), allow all characters, no mandatory rotation (rotation causes
predictable patterns: "password1" → "password2"), and recommend
long passphrases over complex short passwords. Most organizations
still enforce 2009-era complexity rules that are explicitly
not recommended by current security standards.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** all eight security controls in a login endpoint
   and explain why each is necessary.
2. **TEST** the login implementation with an automated security test
   suite that verifies: rate limiting, CSRF, session regeneration,
   cookie attributes, error message consistency, and timing.
3. **IDENTIFY** which controls are missing in a given login
   implementation during code review and explain the attack
   each missing control enables.

---

### 🎯 Interview Deep-Dive

**Q: What security considerations go into building a login system?
Walk me through all the controls you'd implement.**

*Why they ask:* Comprehensive security design question. Tests
depth of authentication security knowledge, not just awareness
of one or two controls.

*Strong answer structure (cover all 8 controls):*
1. **Password hashing:** bcrypt at cost 12+ (not MD5/SHA256 - those are fast, wrong for passwords). Why bcrypt: adaptive, slow, salted per-user.
2. **Rate limiting:** 5 attempts per account per 15 minutes. Both per-account and per-IP. Progressive delays vs hard lockout (hard lockout enables DOS).
3. **CSRF token:** hidden form field, validated server-side with constant-time compare (hmac.compare_digest).
4. **Secure cookies:** HttpOnly (no JS access), Secure (HTTPS only), SameSite=Lax (CSRF protection).
5. **Session regeneration:** new session ID on successful login (prevents fixation). Delete old session server-side.
6. **Generic errors:** "Invalid username or password" for ALL failures (no user enumeration). Same message whether wrong username or wrong password.
7. **Timing normalization:** always compute bcrypt even for non-existent users (DUMMY_HASH). Prevents timing oracle for user enumeration.
8. **Audit logging:** timestamp, IP, username, result for every attempt. Enables detection, forensics, rate limiting decisions.