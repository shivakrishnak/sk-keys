---
id: SEC-013
title: "Cross-Site Request Forgery (CSRF)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-004, SEC-008
used_by: SEC-036, SEC-049
related: SEC-001, SEC-004, SEC-008, SEC-012, SEC-024, SEC-036, SEC-049
tags:
  - security
  - csrf
  - owasp
  - web-security
  - cross-site
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 13
permalink: /technical-mastery/sec/cross-site-request-forgery-csrf/
---

⚡ TL;DR - CSRF (Cross-Site Request Forgery) tricks a
victim's browser into making an authenticated request to
a target site from a different origin. The browser automatically
includes cookies (including session tokens) with every request
to the target origin, regardless of where the request
originated. Attacker's evil site includes an image or form
that sends a request to bank.com. Victim's browser sends
the bank.com session cookie with the request. Bank processes
it as authenticated. Result: transfer funds without victim's
knowledge. Defense: synchronizer token pattern (server
includes a secret token in every form, verifies it on submit)
OR SameSite cookie attribute (browser only sends cookies
with same-site requests). SameSite=Lax is now the default
in Chrome (2020), which mitigates most CSRF. But: explicit
verification is required for security-critical endpoints
where cookie authentication is used.

---

| #013 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, OWASP Top 10, Authentication vs Authorization | |
| **Used by:** | CSRF Prevention, Session Security | |
| **Related:** | OWASP, XSS, Same-Origin Policy, CSRF Prevention, Session Security | |

---

### 🔥 The Problem This Solves

**WORLD WITH THE VULNERABILITY:**
User logs into bank.com. Session cookie set:
`session=abc123; Path=/; HttpOnly`. User then visits evil.com
(in another tab). evil.com's HTML includes:
```html
<img src="https://bank.com/api/transfer?to=attacker&amount=5000">
```
The `<img>` tag causes the browser to send:
```
GET https://bank.com/api/transfer?to=attacker&amount=5000
Cookie: session=abc123
```
The browser automatically includes the bank.com session cookie.
Bank.com sees: authenticated request from session abc123.
Processes the transfer. $5,000 sent to attacker.
No JavaScript required. No interaction from victim beyond
visiting evil.com. This is CSRF.

---

### 📘 Textbook Definition

**CSRF:** An attack where an attacker tricks an authenticated
user's browser into sending an unwanted HTTP request to a
server that the user is currently authenticated with. The
server, which trusts the session cookie, processes the
forged request as legitimate.

**Why browsers enable this:**
The browser's cookie design: cookies are sent to the origin
they belong to, regardless of which site initiated the request.
This was designed for convenience (persistent sessions). It
becomes a security problem when state-changing actions can
be triggered via GET requests or without additional verification.

**Attack requirements:**
1. Victim must be authenticated to the target site
2. The target site's action is triggered via a URL or form
3. The request carries no unpredictable parameters (no secret token)

**Attack vectors:**
- GET request: `<img src="https://target.com/action?param=evil">`
- POST request: hidden form with JavaScript auto-submit
- Pre-click: social engineering to click a link

**Defenses:**
1. **CSRF Token (Synchronizer Token Pattern):** Server generates
   per-session or per-form random token, includes in HTML form
   and verifies on submit. Attacker cannot know the token value
   (same-origin policy blocks reading from target site).
2. **SameSite Cookie Attribute:** Tells browser when to send cookies.
   `SameSite=Strict`: only send if navigation is from same site.
   `SameSite=Lax`: send on top-level navigation GETs, not on
   sub-resource requests or POST from cross-site.
   `SameSite=None; Secure`: send in all contexts (requires HTTPS).
3. **Origin/Referer Header Validation:** Verify that the request
   came from the expected origin. Can be bypassed in some configs.
4. **Custom Request Headers:** APIs: require custom header
   (e.g., `X-Requested-With: XMLHttpRequest`). Browsers don't
   include custom headers in simple cross-origin requests.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CSRF = attacker's site triggers an authenticated request to
your site because the browser automatically sends cookies.
Fix: CSRF token (secret random value the attacker cannot know)
or SameSite cookie attribute.

**One analogy:**
> Imagine your car automatically unlocks when it receives
> a radio signal with your car's VIN number. An attacker
> builds a device that broadcasts your car's VIN. Your car
> unlocks. CSRF is the same: the browser "unlocks" (sends
> your authentication cookie) automatically whenever a
> request goes to the target site, from ANY origin.
> CSRF tokens are like a second secret code required to
> actually start the car - the VIN alone (session cookie)
> is no longer sufficient.

---

### 🔩 First Principles Explanation

**Why SameSite=Lax mitigates most CSRF:**

```
BROWSER COOKIE SENDING RULES (Chrome 80+, 2020):

Default behavior (SameSite=Lax):
  "Top-level navigation" + "safe methods" (GET, HEAD):
    → Cookie IS sent
    Example: User clicks a link from google.com to bank.com
    → bank.com receives session cookie (user navigating to site)
  
  "Sub-resource request" from cross-site:
    → Cookie NOT sent
    Example: evil.com has <img src="https://bank.com/...">
    → bank.com does NOT receive session cookie (attack prevented)
  
  Cross-site POST/PUT/DELETE:
    → Cookie NOT sent
    Example: evil.com form POSTs to bank.com
    → bank.com does NOT receive session cookie (attack prevented)

SameSite=Strict:
  Cookie ONLY sent when navigating directly to the site
  (or from the same site). More restrictive.
  Downside: breaks legitimate cross-site flows
  (e.g., user clicks link in email, lands on bank.com: 
   session cookie not sent, user appears logged out)

SameSite=None; Secure:
  Old behavior: cookie always sent (required for third-party cookies,
  embedded content, cross-site widgets). Requires HTTPS.

WHY LAX DOESN'T FULLY SOLVE CSRF:
  GET requests that cause state changes: if bank.com accepts
  GET /transfer?to=attacker (common mistake), Lax doesn't help
  because top-level navigation GETs DO send cookies.
  FIX: State-changing actions must require POST (or PUT/DELETE).
  CSRF tokens: still needed for sensitive operations + older browsers.
  Not all browsers have Lax as default.

CSRF TOKENS REMAIN REQUIRED FOR:
  - Legacy browsers without SameSite support
  - Applications where state changes happen via GET
  - Defense-in-depth (even if SameSite mitigates, token provides
    second layer)
  - APIs used from non-browser clients (where custom header suffices)
```

---

### 🧪 Thought Experiment

**SCENARIO: Can an attacker steal the CSRF token?**

```
ASSUMPTION: CSRF token is in a hidden form field.
  <input type="hidden" name="csrf_token" value="a3f9e2...">
  Server verifies this token on POST.

QUESTION: Can the attacker read the token from evil.com?

ATTEMPT 1: Attacker's JavaScript tries to fetch bank.com
  fetch('https://bank.com/transfer-form')
    .then(r => r.text())
    .then(html => {
      // BLOCKED by Same-Origin Policy:
      // JavaScript from evil.com CANNOT read the response
      // from bank.com. The fetch response is opaque.
    })
  RESULT: Same-Origin Policy blocks reading.
  Attacker cannot read the CSRF token.

ATTEMPT 2: Attacker exploits XSS on bank.com
  If attacker has XSS on bank.com:
    Script runs IN bank.com's context → CAN read CSRF token
    Can now forge requests with the token.
  IMPLICATION: XSS enables bypassing CSRF protection.
  "XSS beats CSRF tokens." Fix XSS first.

ATTEMPT 3: Token is in a cookie (Double Submit Cookie pattern)
  Token is in a cookie + required in request body/header.
  Attacker cannot read the token cookie (HttpOnly or SOP).
  But: if the cookie is accessible to JavaScript (not HttpOnly):
    XSS on bank.com can read the cookie value.
  RESULT: Same security model as hidden field. XSS beats it.

CONCLUSION:
  CSRF token is secure IF the attacker cannot read it.
  Same-Origin Policy prevents reading from cross-site.
  XSS bypasses Same-Origin Policy.
  Defense-in-depth: CSRF tokens + XSS prevention.
  Even with perfect CSRF tokens: XSS completely breaks it.
```

---

### 🧠 Mental Model / Analogy

> CSRF is a "confused deputy" attack (same term as SQLi, different
> context). The browser is the deputy: it carries your credentials
> (session cookie) and acts on your behalf. The attacker (evil.com)
> gives the deputy instructions (a crafted request) without your
> knowledge. The deputy carries the credentials to the bank, and
> the bank trusts the deputy. The synchronizer token pattern adds
> a passphrase: the bank only accepts requests if the deputy also
> presents a passphrase that the attacker cannot know. The SameSite
> cookie attribute tells the deputy: "only carry credentials when
> I'm actually giving you instructions directly - not when someone
> else tells you to run an errand."

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CSRF tricks your browser into doing things on websites where
you're logged in, without your knowledge. If you're logged
into your bank and visit an evil website, the evil website
can secretly tell your browser to transfer money. The bank
thinks it's you because your login cookie is automatically
sent.

**Level 2 - How to use it (junior developer):**
Use CSRF tokens in all forms that cause state changes (Django
includes them automatically with `{% csrf_token %}`). For APIs:
use the SameSite cookie attribute (SameSite=Lax is default
in Chrome). State-changing endpoints should use POST/PUT/DELETE,
never GET.

**Level 3 - How it works (mid-level engineer):**
CSRF token flow: server generates random token per session
(stored in session). Template includes `<input type="hidden"
name="csrf_token" value="{{token}}">`. On POST: server compares
submitted token with session token. Mismatch → reject. Attacker
cannot read the token (same-origin policy). Token must be:
unpredictable (cryptographically random), per-session (or
per-form), and validated server-side.

**Level 4 - Why it was designed this way (senior/staff):**
CSRF became less critical after Chrome made SameSite=Lax the
default in 2020, mitigating most cookie-based CSRF automatically.
But CSRF tokens remain important for: (1) APIs used by both
browser and mobile clients (mobile doesn't have SameSite),
(2) applications with GET-based state changes (bad practice
but common in legacy code), (3) applications needing defense-
in-depth against SameSite bypass techniques (cross-site redirect
chains, subdomain compromise), (4) SPA applications that use
token-based auth (JWT in Authorization header) do NOT have CSRF
vulnerability at all - CSRF requires cookies, not headers.

**Level 5 - Mastery (distinguished engineer):**
Modern SPA/API architecture with JWT in Authorization header
is naturally CSRF-immune: browsers do not automatically attach
Authorization headers to cross-origin requests. The CSRF
vulnerability only exists when authentication state is carried
in cookies. Therefore: SPAs that store auth tokens in
localStorage/sessionStorage and send as Authorization header
= no CSRF risk (but potentially vulnerable to XSS for token
theft). Cookie-based auth = CSRF risk but XSS cannot steal
HttpOnly cookies. These trade-offs determine the security
architecture: cookie-based auth requires CSRF protection +
XSS prevention; header-based auth (JWT) requires strong XSS
prevention (token theft) but no CSRF protection needed.

---

### ⚙️ How It Works (Mechanism)

**CSRF attack vs. CSRF token defense:**

```
WITHOUT CSRF PROTECTION:

evil.com HTML:
<form action="https://bank.com/api/transfer" method="POST">
  <input name="to" value="attacker_account">
  <input name="amount" value="5000">
  <input type="submit">
</form>
<script>document.forms[0].submit();</script>

Victim's browser sends:
POST https://bank.com/api/transfer
Cookie: session=abc123   ← browser auto-sends bank.com cookie
to=attacker_account&amount=5000
→ Bank processes transfer. Attack successful.

WITH CSRF TOKEN:

bank.com renders transfer form:
<form action="/api/transfer" method="POST">
  <input type="hidden" name="csrf_token" value="f8a3d92e...">
  <input name="to">
  <input name="amount">
  <input type="submit">
</form>

When user submits legitimately:
POST /api/transfer
Cookie: session=abc123
to=victim&amount=100&csrf_token=f8a3d92e...
→ Server verifies: csrf_token matches session? YES → Process.

evil.com tries to forge:
  Cannot read csrf_token from bank.com (Same-Origin Policy)
  Submits without token: csrf_token missing → Server rejects.
  Submits with wrong token: csrf_token mismatch → Server rejects.
→ Attack blocked.

WITH SameSite=Lax (Chrome 80+):

evil.com's <form> submits to bank.com:
  Browser: is this a cross-site POST? YES.
  SameSite=Lax: don't send session cookie on cross-site POST.
  Bank.com receives request WITHOUT session cookie.
  Bank.com: no authenticated session → 401. Attack blocked.
```

---

### 💻 Code Example

**CSRF protection implementation:**

```python
# Python/Flask: Manual CSRF token implementation
import secrets
from functools import wraps
from flask import session, request, abort

def generate_csrf_token():
    """Generate a CSRF token for the current session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def csrf_protect(func):
    """Decorator: verify CSRF token on state-changing requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            token = (
                request.form.get('csrf_token')
                or request.headers.get('X-CSRF-Token')
            )
            if not token or not secrets.compare_digest(
                token, session.get('csrf_token', '')
            ):
                abort(403, description="CSRF token validation failed")
        return func(*args, **kwargs)
    return decorated_function

@app.route('/transfer', methods=['POST'])
@csrf_protect
def transfer():
    """Protected transfer endpoint."""
    # CSRF verified by decorator
    to_account = request.form['to']
    amount = request.form['amount']
    process_transfer(to_account, amount)
    return {"status": "success"}

# Template (Jinja2):
# <form method="POST" action="/transfer">
#   <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
#   ...
# </form>

# Cookie setting (defense-in-depth):
# SameSite=Lax is now default in modern browsers.
# Explicitly set to ensure consistent behavior:
response.set_cookie(
    'session',
    value=session_token,
    httponly=True,     # Prevent XSS cookie theft
    secure=True,       # HTTPS only
    samesite='Lax'     # CSRF mitigation
)
```

```javascript
// SPA with JWT: no CSRF needed (header-based auth)
// JWT in Authorization header is NOT automatically sent by browser
// → immune to CSRF attacks

// BAD for CSRF purposes: storing JWT in cookie
document.cookie = "jwt=" + token + "; path=/"
// This creates CSRF vulnerability (browser sends cookie automatically)

// GOOD: store in memory or localStorage, send as header
const token = localStorage.getItem('jwt')
fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,  // Explicitly added - not auto-sent
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ to: accountId, amount: 100 })
})
// evil.com cannot forge this: cannot add Authorization header to
// a cross-origin request without CORS pre-flight approval from bank.com
```

---

### ⚖️ Comparison Table

| Defense | How It Works | Effectiveness | Caveats |
|:---|:---|:---|:---|
| **CSRF Token** | Random secret verified on submit | High (complete if token is secret) | Must generate securely; XSS bypasses it |
| **SameSite=Lax** | Browser won't send cookies on cross-site POST | High (modern browsers) | GET state changes still vulnerable |
| **SameSite=Strict** | Cookie only on direct navigation | Highest | Breaks some legitimate flows |
| **Origin header check** | Server validates Origin/Referer header | Medium | Can be bypassed via redirects |
| **Custom header (X-CSRF-Token)** | Browser blocks custom headers cross-origin | Good for APIs | Requires CORS configuration |
| **JWT in Authorization header** | Not a cookie - browser never auto-sends | Complete (no CSRF possible) | XSS can steal token |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| SPA using JWT is immune to all CSRF | Correct ONLY if the JWT is sent via Authorization header. If the JWT is stored in a cookie: the browser auto-sends it, and CSRF applies exactly the same as session cookies. Many SPAs store tokens in cookies for HttpOnly security (prevents XSS theft). These applications need CSRF protection. The anti-CSRF model: cookie auth → CSRF protection required. Header auth (Authorization: Bearer ...) → no CSRF risk. |
| HTTPS prevents CSRF | HTTPS encrypts the connection but does NOT prevent the browser from including cookies. The attacker's evil.com does not need to see the cookie - the browser automatically includes it for the target origin regardless of whether HTTPS is used. HTTPS protects against network eavesdroppers. It does not protect against the browser's cookie-sending behavior exploited by CSRF. |

---

### 🚨 Failure Modes & Diagnosis

**Common CSRF implementation mistakes:**

```python
# MISTAKE 1: CSRF token not regenerated after login
# (allows session fixation + CSRF token reuse)
def login(username, password):
    if authenticate(username, password):
        # BUG: reusing the same CSRF token from unauthenticated session
        session['user_id'] = user.id
        # SHOULD: session.regenerate() + generate new CSRF token

# MISTAKE 2: CSRF token in URL (logs, referrer header leakage)
# BAD: <a href="/transfer?csrf_token=secret&to=Alice">
# Referrer header sends the URL (including token) to the next site.
# Token in URL also appears in server access logs.

# MISTAKE 3: Using a predictable CSRF token
def bad_csrf_token(user_id):
    return hashlib.md5(f"csrf_{user_id}".encode()).hexdigest()
    # Predictable if attacker knows user_id. Not cryptographically random.

# MISTAKE 4: Not validating CSRF token server-side
@app.route('/transfer', methods=['POST'])
def transfer():
    # Looks like validation but actually just checks presence
    if not request.form.get('csrf_token'):
        abort(403)
    # BUG: any non-empty value passes. Attacker submits 'x'.
    # Fix: compare against session token with compare_digest.
    ...

# CORRECT:
def verify_csrf(submitted_token):
    return bool(
        submitted_token
        and secrets.compare_digest(
            submitted_token,
            session.get('csrf_token', '')
        )
    )
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Authentication vs Authorization vs Auditing` - sessions and cookies
- `Same-Origin Policy` - why CSRF tokens work

**Builds on this:**
- `CSRF Prevention` - complete implementation guide
- `Session Security` - cookies + SameSite + session management
- `XSS` - XSS bypasses CSRF token protection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ATTACK       │ Browser auto-sends cookies from ANY site. │
│ MECHANISM    │ Attacker triggers request from evil.com.  │
│              │ Bank sees authenticated request.          │
├──────────────┼───────────────────────────────────────────┤
│ DEFENSES     │ 1. CSRF token (random, session-bound)     │
│              │ 2. SameSite=Lax (default Chrome 80+)      │
│              │ 3. JWT in Authorization header (no CSRF)  │
├──────────────┼───────────────────────────────────────────┤
│ CSRF BEATS   │ → Always: state changes via GET requests  │
│ SameSite=Lax │ → Old browsers without SameSite support  │
├──────────────┼───────────────────────────────────────────┤
│ XSS BEATS    │ → XSS can steal/submit CSRF tokens       │
│ CSRF TOKENS  │ → Fix XSS first, CSRF tokens are layer 2 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cookie = auto-sent = forged request.     │
│              │  CSRF token = secret attacker can't read. │
│              │  SameSite=Lax = browser won't send on     │
│              │  cross-site POST."                        │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Authentication tokens are only as secure as their transport
mechanism." Cookies are automatically transported by the
browser to all matching origins - which enables CSRF. Headers
(Authorization: Bearer) are explicitly added by code - which
prevents CSRF. This transport mechanism choice determines the
security properties:
- Cookie transport: CSRF-vulnerable, XSS-resistant (HttpOnly), 
  works in server-rendered apps.
- Header transport: CSRF-immune, XSS-vulnerable (localStorage),
  requires JavaScript-driven apps.
Neither is universally better. The choice depends on the
threat model. Understanding the transport mechanism determines
which attacks are possible and which defenses are required.

---

### 💡 The Surprising Truth

CSRF was listed in every OWASP Top 10 from 2007 to 2017 -
then removed in 2021. Why? Chrome (2020) made SameSite=Lax
the default. Firefox and Safari followed. Modern browsers
now automatically block the most common CSRF attack patterns
(cross-site POST with cookies) WITHOUT any developer action.
CSRF went from a critical web vulnerability to a "mostly
mitigated by browser default" issue in a single browser
release cycle. This is the power of framework defaults and
browser defaults: changing the default behavior of millions
of deployments simultaneously. The same pattern: HTTPS Let's
Encrypt and browser "Not Secure" warnings dramatically increased
TLS adoption. Secure defaults at infrastructure level are more
effective at scale than application-level fixes.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the attack: browser auto-sends cookies to any
   origin that requests them, regardless of initiating site.
2. **IDENTIFY** when CSRF protection is needed: cookie-based
   auth + state-changing endpoints. JWT in header: not needed.
3. **IMPLEMENT** CSRF token: generate random per-session,
   include in form, verify with `compare_digest` on submit.
4. **EXPLAIN** why SameSite=Lax mitigates most CSRF and what
   residual risk remains (GET-based state changes).

---

### 🎯 Interview Deep-Dive

**Q: What is CSRF? How does it differ from XSS, and what are
the defenses?**

*Why they ask:* Tests understanding of cross-site attacks and
whether the candidate can distinguish the attack models.

*Strong answer includes:*
- CSRF: attacker tricks browser into making authenticated
  request. Victim's browser sends credentials automatically.
  Attacker never sees the response.
- XSS: attacker injects code that RUNS in victim's browser.
  Attacker can read responses, steal cookies, make requests.
  CSRF uses the browser as a weapon against the server.
  XSS uses the server as a weapon against the user.
- Difference: CSRF requires only that the user is authenticated
  (no code injection). XSS requires injecting code.
  CSRF exploits the browser's cookie-sending behavior.
  XSS exploits the browser's script-execution behavior.
- Defenses: CSRF tokens (attacker cannot read), SameSite cookie
  (browser won't send on cross-site POST), JWT in header (not
  cookie = no CSRF). Django/Rails/Spring auto-include CSRF tokens.
- Relationship: XSS can steal CSRF tokens → XSS must be fixed
  to make CSRF tokens effective. Defense-in-depth: both XSS
  prevention AND CSRF tokens are required.
