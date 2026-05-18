---
id: SEC-019
title: "Security Headers (HTTP)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-012, SEC-014
used_by: SEC-025, SEC-047, SEC-048
related: SEC-001, SEC-012, SEC-014, SEC-025, SEC-047, SEC-048, SEC-063
tags:
  - security
  - http-headers
  - csp
  - hsts
  - xss
  - web-security
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/sec/security-headers-http/
---

⚡ TL;DR - HTTP security headers are server-sent directives
that instruct browsers to enforce specific security policies.
They are the easiest high-value security improvement:
add them to your server config, and browsers enforce
protection for all visitors automatically. The seven
essential headers:

- `Content-Security-Policy`: limits which scripts/styles/
  resources can load. Primary XSS defense at browser level.
- `Strict-Transport-Security`: tells browsers to always
  use HTTPS for this domain. Prevents protocol downgrade.
- `X-Frame-Options` / `frame-ancestors` in CSP: prevents
  your pages from being embedded in iframes (clickjacking).
- `X-Content-Type-Options: nosniff`: prevents MIME type
  sniffing attacks.
- `Referrer-Policy`: controls what URL is sent in the
  Referrer header (privacy + info leak).
- `Permissions-Policy`: limits browser features
  (camera, microphone, geolocation) the page can use.

Testing: securityheaders.com (free, instant grade).

---

| #019 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, XSS, HTTP vs HTTPS | |
| **Used by:** | Security Mindset, XSS Prevention, CSP Deep Dive | |
| **Related:** | XSS, HTTP vs HTTPS, CSP, HSTS, Security Mindset | |

---

### 🔥 The Problem This Solves

**Without security headers:**
- Browser loads your page and then loads a script from
  evil.com because no CSP restricts it.
- User visits your HTTPS site once, then their DNS is
  poisoned → connects over HTTP → credentials stolen.
  HSTS would have prevented the downgrade.
- Attacker puts your login form in an invisible iframe
  on their site. User thinks they're on your site,
  but they're clicking on the attacker's page underneath
  (clickjacking). X-Frame-Options prevents this.
- Your error page returns a JSON response with a wrong
  MIME type. Browser sniffs it as HTML, renders it,
  script in the JSON executes. X-Content-Type-Options
  prevents sniffing.

Security headers: browser-level security that doesn't
require application code changes. Add to your reverse
proxy / web server config. Takes 30 minutes. Significant
security improvement.

---

### 📘 Textbook Definition

**Security Headers:** HTTP response headers that web
servers include to instruct browsers to apply specific
security policies. They are the browser's security
configuration interface.

**The Seven Essential Headers:**

**1. Content-Security-Policy (CSP)**
The most powerful and complex security header.
Whitelist of approved sources for each resource type.
```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' https://trusted-cdn.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  object-src 'none'
```
Effect: browser blocks any resource not matching the policy.
Inline scripts (potential XSS vectors) blocked if not
explicitly allowed. Even if XSS injection succeeds: browser
blocks execution of injected scripts (they're not in the whitelist).

**2. Strict-Transport-Security (HSTS)**
```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```
Effect: browser only contacts this domain over HTTPS for the
duration of max-age (63072000 seconds = 2 years). Even if
user types `http://`, browser upgrades to `https://` silently.
`includeSubDomains`: applies to all subdomains.
`preload`: site can be added to browser's HSTS preload list
(browsers ship with this list hardcoded - protection even
on first visit).

**3. X-Frame-Options**
```
X-Frame-Options: DENY
# OR:
X-Frame-Options: SAMEORIGIN
```
Replaced by CSP `frame-ancestors` directive (more flexible),
but X-Frame-Options is still widely supported.
Effect: prevents your page from being embedded in iframes
on other domains. Stops clickjacking attacks.

**4. X-Content-Type-Options**
```
X-Content-Type-Options: nosniff
```
Effect: tells browser to not sniff the MIME type. Browser
must use the declared Content-Type. Prevents attackers from
uploading a script file with a non-script MIME type (e.g.,
`image/jpeg`) and then triggering execution by loading it
in a script context.

**5. Referrer-Policy**
```
Referrer-Policy: strict-origin-when-cross-origin
```
Effect: controls what URL is sent in the `Referer` header.
`strict-origin-when-cross-origin`: same-origin requests
send full URL, cross-origin requests send only origin
(https://example.com not https://example.com/user/123/profile).
Prevents sensitive URL paths (containing session IDs, tokens)
from being leaked to third-party domains.

**6. Permissions-Policy (formerly Feature-Policy)**
```
Permissions-Policy: camera=(), microphone=(), geolocation=()
```
Effect: disables specified browser features for the page
and its sub-resources. `()` = deny all origins. Prevents
malicious third-party scripts from accessing camera, mic, etc.

**7. Cross-Origin headers (CORP, COEP, COOP)**
Advanced headers for Spectre mitigation and cross-origin
isolation. Required to use SharedArrayBuffer and high-resolution
timers. Less universally applicable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Security headers are browser instructions sent by your server
that enforce security policies client-side - CSP blocks
unauthorized scripts, HSTS forces HTTPS, X-Frame-Options
stops clickjacking. Add them to your web server config
for instant, broad security improvement.

**One analogy:**
> Security headers are like house rules you post on the
> front door for visitors. "No one enters without verifying
> with the host first" (CSP), "always use the secure
> entrance" (HSTS), "don't let strangers put a frame
> over the door" (X-Frame-Options). Visitors (browsers)
> read and follow these rules automatically. You post the
> rules once (server config) - they apply to everyone.
> Without the rules: visitors follow browser defaults
> (permissive).

---

### 🔩 First Principles Explanation

**Why CSP is the most powerful XSS defense:**

```
WITHOUT CSP:
  Browser's default behavior: execute ALL JavaScript that appears
  in the page, regardless of where it came from.
  Inline script: <script>code</script> → executes
  External script: <script src="https://evil.com/x.js"> → executes
  
  XSS injection: attacker injects <script>evil()</script> into
  the page. Browser executes it. XSS succeeds.

WITH CSP: script-src 'self'
  Browser's policy: only execute JavaScript from the same origin.
  Any other script source: blocked.
  
  Inline script: blocked (not from 'self' - inline is treated
    as different origin unless 'unsafe-inline' is specified)
  External script from evil.com: blocked (not 'self')
  
  XSS injection: attacker injects <script>evil()</script>
  Browser: CSP says no inline scripts. Block. XSS fails.
  
  Even if attacker injects: <script src="https://evil.com/x.js">
  Browser: evil.com is not in script-src. Block. XSS fails.

WHY 'unsafe-inline' BREAKS CSP:
  Many legacy apps use inline JavaScript (onclick handlers,
  <script> blocks in HTML). Adding 'unsafe-inline' allows
  all inline scripts → completely bypasses inline XSS protection.
  90% of CSPs in the wild have 'unsafe-inline' (Google Security Blog).
  
THE BETTER ALTERNATIVE TO 'unsafe-inline': NONCE
  Server generates a random nonce per request:
    Content-Security-Policy: script-src 'nonce-abc123'
  HTML: <script nonce="abc123">legitimate script</script>
  Browser: only execute scripts with nonce="abc123"
  
  Injected script (no nonce): <script>evil()</script>
  Browser: no nonce attribute. Blocked.
  
  Even with 'unsafe-inline' in CSP with nonce:
    The nonce takes precedence - inline scripts blocked unless
    they have the correct nonce (which attacker cannot know,
    because nonce is server-generated per request).
```

---

### 🧪 Thought Experiment

**SCENARIO: Clickjacking without X-Frame-Options**

```
TARGET: Online banking - "Transfer Funds" button.

ATTACK SETUP:
  evil.com creates:
    <iframe src="https://bank.com/transfer?to=attacker&amount=500"
            style="opacity: 0; position: absolute; top: 0; left: 0;
                   width: 100%; height: 100%">
    </iframe>
    
    <p>Click here for a free iPhone!</p>
    (button placed exactly where "Confirm Transfer" button is
     in the hidden iframe)

EXECUTION:
  Victim visits evil.com (phishing link, ads, etc.)
  Victim sees: "Click here for a free iPhone!" button.
  Victim clicks: actually clicks "Confirm Transfer" on
    the invisible bank.com iframe.
  Browser: sends request to bank.com with session cookie.
  Bank: processes transfer. $500 to attacker.
  Victim: sees nothing. No confirmation on evil.com.

PREVENTION:
  bank.com adds: X-Frame-Options: DENY
  
  Victim visits evil.com. Browser downloads the iframe.
  Browser checks: the iframe has X-Frame-Options: DENY.
  Response from bank.com cannot be displayed in any iframe.
  Browser blocks the iframe. evil.com shows nothing useful.
  Clickjacking fails.
  
  CSP frame-ancestors is equivalent and more flexible:
  Content-Security-Policy: frame-ancestors 'none'
  Same effect. Can also specify specific domains that ARE
  allowed to embed (e.g., frame-ancestors 'self' for same-origin iframes).
```

---

### 🧠 Mental Model / Analogy

> Security headers are the configuration panel for your
> visitor management system. Default settings are permissive
> (any visitor, any access). Security headers let you
> configure specific rules:
> - CSP: "only let in guests I explicitly invited (whitelisted scripts)"
> - HSTS: "visitors must always use the secure door (HTTPS)"
> - X-Frame-Options: "don't put a glass window over our front
>   door (no iframing)"
> - X-Content-Type-Options: "trust the label on packages
>   (don't sniff MIME types)"
> - Referrer-Policy: "don't reveal which floor someone came from
>   to outside visitors (limit referrer info)"
> You configure once (server config). Every visitor gets
> the same security treatment. No application code changes.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Security headers are settings in your website's responses
that tell browsers to be extra careful. They're like posting
safety rules: "only load code from approved sources,"
"always use secure connection," "don't let other websites
embed our pages." Browsers follow these rules automatically.
Adding them is like posting a "no trespassing" sign that
browsers enforce.

**Level 2 - How to use it (junior developer):**
Add security headers to your web server config (Nginx,
Apache, or reverse proxy). Check results at securityheaders.com.
For HTTPS: add HSTS after confirming HTTPS works on all
pages. For CSP: start with report-only mode, see violations,
then enable. These headers don't require backend code changes.

**Level 3 - How it works (mid-level engineer):**
Each security header value is a browser directive.
Browser parses the header on response receipt. CSP is the
most complex: parse the policy (default-src, script-src,
etc.), build a whitelist, check every resource load and
script execution against it. Violations can be:
- Blocked (enforced CSP)
- Reported to a URI (report-only mode: `Content-Security-Policy-Report-Only`)
  without blocking - good for auditing before enforcement.
HSTS is stored in browser's HSTS store. Subsequent requests
to the domain bypass HTTP → are upgraded to HTTPS by the
browser, before connecting to the network.

**Level 4 - Why it was designed this way (senior/staff):**
Security headers represent a deliberate design to make
security configurable at the transport layer rather than
requiring application changes. CSP in particular was a
direct response to the XSS epidemic: instead of fixing
XSS individually in millions of applications, browsers
could enforce a "no unauthorized scripts" policy at the
browser level. The tradeoff: CSP requires significant
effort to configure for complex applications (many third-party
scripts, legacy inline JavaScript), which is why adoption
has been slow. 2023 HTTP Archive: only 9% of sites have
a CSP. The alternative, CSP-with-nonces (one of the Trusted
Types proposals), makes CSP compatible with dynamic content
while maintaining security.

**Level 5 - Mastery (distinguished engineer):**
Cross-Origin headers (COOP, COEP, CORP) were introduced
to mitigate Spectre (CPU side-channel attacks via SharedArrayBuffer
and high-resolution timing). Spectre attacks require cross-origin
resources in the same process. COOP (Cross-Origin-Opener-Policy)
isolates browsing contexts (popups can't access opener).
COEP (Cross-Origin-Embedder-Policy) requires all sub-resources
to explicitly allow cross-origin embedding. Together they
enable cross-origin isolation, required for SharedArrayBuffer.
Most application developers don't need to configure these
unless using SharedArrayBuffer for performance-critical
operations (WebAssembly, WebGL). They represent the
tension between web's cross-origin model and OS-level
security in multi-process architectures.

---

### ⚙️ How It Works (Mechanism)

**Complete security header example - request and response:**

```
1. Browser requests: GET https://bank.com/dashboard

2. Server responds with security headers:
   HTTP/1.1 200 OK
   Content-Type: text/html; charset=utf-8
   Content-Security-Policy: 
     default-src 'self'; 
     script-src 'self' 'nonce-Abc123Xyz' https://cdn.bank.com;
     style-src 'self' 'unsafe-inline';
     img-src 'self' data:;
     object-src 'none';
     base-uri 'self';
     frame-ancestors 'none'
   Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
   X-Content-Type-Options: nosniff
   Referrer-Policy: strict-origin-when-cross-origin
   Permissions-Policy: camera=(), microphone=(), geolocation=()
   Cache-Control: no-store, max-age=0

3. Browser processes headers:
   HSTS: store "bank.com → HTTPS only, max-age=2y, includeSubDomains"
         Future requests to http://bank.com → auto-upgraded to https://
   
   CSP: build policy:
     default-src = only same-origin
     script-src = same-origin + nonce-Abc123Xyz + cdn.bank.com
     frame-ancestors = deny all framing

4. Browser processes HTML body:
   <script nonce="Abc123Xyz">/* bank's own script */</script>
   → nonce matches CSP → ALLOWED to execute
   
   <script>injected_by_xss()</script>
   → no nonce, inline → BLOCKED by CSP
   
   <script src="https://evil.com/x.js"></script>
   → not in script-src → BLOCKED by CSP
   
   <img src="https://evil.com/tracker.gif">
   → img-src is 'self' data: only → BLOCKED by CSP
```

---

### 💻 Code Example

**Adding security headers in common frameworks:**

```nginx
# Nginx: Add security headers to all responses

server {
    listen 443 ssl http2;
    server_name app.example.com;
    
    # HTTPS setup (omitted)
    
    # Security Headers
    add_header Strict-Transport-Security 
        "max-age=63072000; includeSubDomains; preload" always;
    
    add_header X-Content-Type-Options "nosniff" always;
    
    add_header X-Frame-Options "DENY" always;
    
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    add_header Permissions-Policy 
        "camera=(), microphone=(), geolocation=()" always;
    
    # CSP: Start with report-only to audit, then enforce
    add_header Content-Security-Policy-Report-Only
        "default-src 'self'; script-src 'self'; report-uri /csp-report"
        always;
    # When ready to enforce, change to:
    # add_header Content-Security-Policy "..." always;
    
    location / {
        proxy_pass http://backend:8080;
    }
}

# HTTP redirect (needed for HSTS to work correctly)
server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

```python
# Python/Flask: Security headers middleware
from flask import Flask, g

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    """Apply security headers to every response."""
    
    # HSTS: HTTPS-only for 2 years
    response.headers['Strict-Transport-Security'] = (
        'max-age=63072000; includeSubDomains; preload'
    )
    
    # No MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # No iframing
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Minimal referrer info cross-origin
    response.headers['Referrer-Policy'] = (
        'strict-origin-when-cross-origin'
    )
    
    # Disable unneeded browser features
    response.headers['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=()'
    )
    
    # CSP: in production, generate nonce per request
    # nonce = g.csp_nonce  (generated per request)
    # response.headers['Content-Security-Policy'] = (
    #     f"default-src 'self'; script-src 'self' 'nonce-{nonce}'"
    # )
    
    return response
```

---

### ⚖️ Comparison Table

| Header | Attack Prevented | Complexity | Can it break existing functionality? |
|:---|:---|:---|:---|
| **Strict-Transport-Security** | HTTPS downgrade, HSTS stripping | Low | Yes, if HTTP is needed (set max-age low initially) |
| **X-Content-Type-Options: nosniff** | MIME type sniffing attacks | None | Rarely |
| **X-Frame-Options: DENY** | Clickjacking | Low | If you legitimately use iframes (use SAMEORIGIN) |
| **Referrer-Policy** | Referrer information leakage | Low | If analytics depends on full referrer URL |
| **Permissions-Policy** | Malicious script accessing browser features | Low | If page legitimately uses camera/mic/geo |
| **Content-Security-Policy** | XSS (script injection), data injection | Very High | Yes, frequently (inline scripts, third-party resources) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Adding CSP will immediately break our site | CSP can break existing functionality if you have inline JavaScript, third-party scripts, or dynamically loaded resources. But: Content-Security-Policy-Report-Only lets you deploy CSP in audit mode first. The browser reports violations to a `/csp-report` endpoint without blocking anything. Run in report-only mode, collect violations, update the policy to allow legitimate sources, then switch to enforcement mode. This two-phase approach prevents the "CSP broke everything" scenario. |
| Security headers alone are sufficient for XSS prevention | Headers are defense-in-depth, not complete prevention. CSP prevents injected scripts from executing even if XSS exists. But a weak CSP (`'unsafe-inline'`) provides no XSS protection. A missing CSP: application-level prevention (output encoding) is the only defense. Security headers and application-level defenses are complementary layers. |

---

### 🚨 Failure Modes & Diagnosis

**Check and fix security header configuration:**

```bash
# Quick check: curl for security headers
curl -I https://app.example.com 2>/dev/null \
  | grep -iE "strict-transport|content-security|x-frame|x-content-type|referrer|permissions"

# Expected output includes all headers. Missing = not configured.

# Free online scanner (comprehensive grading):
# https://securityheaders.com/?q=https://app.example.com

# Check CSP violations (set up a report endpoint first):
# Content-Security-Policy: default-src 'self'; report-uri /csp-report

# Python endpoint to collect CSP violation reports:
from flask import request, jsonify
import logging

@app.post('/csp-report')
def csp_report():
    """Receive and log CSP violation reports."""
    report = request.get_json(force=True, silent=True) or {}
    violation = report.get('csp-report', {})
    logging.warning(f"CSP violation: {violation}")
    # In production: send to SIEM / alerting system
    return '', 204

# Common CSP violations and fixes:
# Violation: "Refused to load script from 'https://cdn.third-party.com'"
# Fix: add to script-src: script-src 'self' https://cdn.third-party.com

# Violation: "Refused to execute inline script"
# Fix option 1 (preferred): add nonce to the specific script
# Fix option 2 (less secure): add 'unsafe-inline' to script-src
# Fix option 3: move inline script to external file

# HSTS pre-registration check:
# https://hstspreload.org - check and submit for preload list
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `XSS` - what CSP defends against
- `HTTP vs HTTPS` - what HSTS enforces

**Builds on this:**
- `Content Security Policy` - CSP deep dive
- `HSTS` - HSTS preload list, subdomain implications
- `XSS Prevention` - CSP + output encoding

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MUST-HAVE    │ Strict-Transport-Security (HSTS)          │
│              │ X-Content-Type-Options: nosniff           │
│              │ X-Frame-Options: DENY (or CSP equivalent) │
│              │ Referrer-Policy                           │
├──────────────┼───────────────────────────────────────────┤
│ HIGH VALUE   │ Content-Security-Policy                   │
│              │ Start with Report-Only, then enforce      │
│              │ Use nonces instead of 'unsafe-inline'     │
├──────────────┼───────────────────────────────────────────┤
│ TESTING      │ securityheaders.com (free grade)         │
│              │ curl -I https://app.example.com           │
├──────────────┼───────────────────────────────────────────┤
│ CSP PITFALL  │ 'unsafe-inline' in script-src             │
│              │ Completely defeats inline XSS protection  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Server instructions → browser policies. │
│              │  CSP: approved script sources only.       │
│              │  HSTS: HTTPS always.                      │
│              │  X-Frame-Options: no clickjacking."       │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security defaults should be the easy path." Security headers
embody this: by adding a few lines to your server configuration,
you get browser-level enforcement across all visitors. You don't
have to audit every line of application code or hunt for
vulnerabilities. The harder question is: why aren't secure
defaults built-in? HSTS requires an explicit opt-in because
setting it incorrectly can lock out HTTP access to your site.
X-Frame-Options is not the default because some legitimate
uses require framing. CSP is not the default because most
existing websites would break (inline scripts are ubiquitous).
The engineering insight: default security vs. default compatibility
is a constant tension. Understanding why a security feature
is opt-in rather than default helps you set your own defaults
appropriately.

---

### 💡 The Surprising Truth

HSTS preloading is a one-way door. Once you submit your
domain to the HSTS preload list (hstspreload.org), your
domain is hardcoded into Chrome, Firefox, Safari, and Edge
as "HTTPS-only." This takes effect immediately for new
browser versions and persists long after your max-age expires.
If you ever need to serve HTTP from that domain (for any
reason): you cannot, unless you submit a removal request
(which takes months to process and propagate). The preload
list has entries that are effectively permanent. Several
companies have discovered this after doing domain migrations
and needing HTTP temporarily - they were locked out.
Lesson: HSTS preloading is a deliberate, permanent commitment
to HTTPS. Only preload if you are certain the domain will
be HTTPS-only forever. The preload list includes `includeSubDomains`
- so ALL current and future subdomains must also be HTTPS.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **LIST** the five essential security headers and what
   attack each prevents.
2. **EXPLAIN** CSP: how script-src works, what 'unsafe-inline'
   defeats, and how nonces fix the inline script problem.
3. **DEPLOY** security headers to a web server config
   and verify with securityheaders.com.
4. **EXPLAIN** HSTS preloading: what it does and why it's
   a one-way commitment requiring careful consideration.

---

### 🎯 Interview Deep-Dive

**Q: What security headers would you add to a web application
and what does each one do?**

*Why they ask:* Tests breadth of security knowledge. Good
candidates know the specific headers. Great candidates
know the edge cases (HSTS preloading risk, CSP report-only
rollout).

*Strong answer includes:*
- HSTS: HTTPS-only for duration. `includeSubDomains`. Preload
  list consideration (one-way door - commit carefully).
- CSP: whitelist of allowed script sources. Prevents XSS
  (even if injection occurs, script won't execute if source
  not whitelisted). `'unsafe-inline'` defeats inline protection.
  Use nonces. Deploy with Report-Only first to audit.
- X-Frame-Options/frame-ancestors: clickjacking prevention.
  Attacker can't put your page in a transparent iframe.
- X-Content-Type-Options: nosniff prevents MIME sniffing.
  Prevents serving a file with wrong Content-Type from executing.
- Referrer-Policy: prevent URL leakage to third parties.
  Especially important if URLs contain user IDs, tokens.
- Test: securityheaders.com gives A-F grade.
- Operational: security headers are add-to-server-config,
  not code changes. Highest ROI per hour of security work.
