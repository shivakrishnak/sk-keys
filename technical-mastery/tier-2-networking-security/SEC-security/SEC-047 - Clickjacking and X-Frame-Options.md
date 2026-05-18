---
id: SEC-047
title: "Clickjacking and X-Frame-Options"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-016, SEC-020, SEC-031
used_by: SEC-067, SEC-080
related: SEC-001, SEC-016, SEC-020, SEC-031, SEC-067
tags:
  - security
  - clickjacking
  - x-frame-options
  - content-security-policy
  - frame-ancestors
  - ui-redressing
  - headers
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/sec/clickjacking-and-x-frame-options/
---

⚡ TL;DR - Clickjacking embeds your site in an invisible iframe
on an attacker's page. When users think they're clicking the
attacker's button, they're actually clicking YOUR button
(transferring money, deleting accounts, granting permissions).
Prevention: tell browsers your page cannot be framed.

**Two headers that prevent framing (use frame-ancestors):**
```
# Older approach (X-Frame-Options):
X-Frame-Options: DENY

# Modern approach (CSP frame-ancestors - more flexible):
Content-Security-Policy: frame-ancestors 'none';

# Allow only same origin (for your own iframes):
Content-Security-Policy: frame-ancestors 'self';

# Allow specific origin (e.g., for embedded dashboards):
Content-Security-Policy: frame-ancestors https://dashboard.partner.com;
```

**Priority:** Prefer `frame-ancestors` (CSP) over `X-Frame-Options`.
CSP is the current W3C standard; X-Frame-Options is the legacy approach.
Use both for browser compatibility.

---

| #047 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Headers, HTTP Fundamentals, Content Security Policy | |
| **Used by:** | Business Logic Vulnerabilities, CORS Misconfiguration | |
| **Related:** | Content Security Policy, Security Headers, CSRF Prevention | |

---

### 🔥 The Problem This Solves

**THE CLICKJACKING ATTACK:**

```
ATTACKER'S PAGE (evil.com/free-prize):

  +--------------------------------------------------+
  |  evil.com - You Won a Free Prize!               |
  |                                                  |
  |  Congratulations! Click below to claim:          |
  |                                                  |
  |  ┌──────────────┐   ← VISIBLE button            |
  |  │  CLAIM PRIZE │                               |
  |  └──────────────┘                               |
  |                                                  |
  +--------------------------------------------------+
  
  BEHIND THE VISIBLE BUTTON (invisible iframe overlay):
  
  +--------------------------------------------------+
  |  bank.com/transfer                              |  opacity: 0.0
  |                                                  |  (invisible!)
  |  Transfer $500 to: [attacker account]            |
  |                                                  |
  |  ┌──────────────┐   ← THE REAL BUTTON           |
  |  │   CONFIRM    │     (perfectly aligned         |
  |  └──────────────┘      under "CLAIM PRIZE")     |
  |                                                  |
  +--------------------------------------------------+

  User thinks: clicking "CLAIM PRIZE" on attacker's site.
  Reality: clicking "CONFIRM" on bank.com (inside invisible iframe).
  
  If user is already logged in to bank.com:
  → Their authenticated session confirms the transfer.
  → $500 transferred to attacker.

HTML THAT CREATES THIS ATTACK:

  <body>
    <!-- Attacker's visible content -->
    <div class="fake-button">CLAIM PRIZE</div>
    
    <!-- Bank's page, invisible, perfectly positioned -->
    <iframe
      src="https://bank.com/transfer?to=attacker&amount=500"
      style="
        position: absolute;
        top: 200px;
        left: 150px;
        opacity: 0.0;       /* Invisible */
        pointer-events: all;/* Still receives clicks */
        z-index: 999;       /* On top of attacker's content */
        width: 200px;
        height: 60px;
      "
    ></iframe>
  </body>

CRITICAL: The browser loads bank.com including the user's session
  cookies (since cookies are sent with the bank.com request).
  If bank.com doesn't prevent framing: the user is fully authenticated
  in the iframe. Their click on the invisible iframe confirms
  whatever action is on that page.
```

**FACEBOOK LIKE-JACKING (2010):**
Attackers created pages that said "Click here to see shocking video."
The "Click here" link was actually an invisible iframe over a Facebook
Like button for the attacker's page. Millions of users "liked"
the page without knowing. The "like" action appeared in friends'
feeds, spreading the attack virally. Facebook fixed this by:
(1) X-Frame-Options: SAMEORIGIN on the Like button, and
(2) requiring visible confirmation for like actions in iframes.

---

### 📘 Textbook Definition

**Clickjacking (UI Redressing):** An attack where a malicious
page overlays a transparent or opaque iframe of a legitimate
website over a deceptive UI element. When users interact with
the visible content, they unknowingly interact with the hidden
legitimate site's actions.

**X-Frame-Options HTTP Header:**
- `DENY` - Page cannot be displayed in any frame (most restrictive)
- `SAMEORIGIN` - Page can only be framed by the same origin
- `ALLOW-FROM https://example.com` - Only specific origin allowed
  (deprecated in modern browsers, not universally supported)

Note: X-Frame-Options is defined in RFC 7034. It was widely
adopted before CSP's `frame-ancestors` directive existed.

**CSP frame-ancestors Directive:**
Part of Content Security Policy Level 2. Replaces X-Frame-Options
with a more powerful, flexible standard.
- `frame-ancestors 'none'` - Equivalent to X-Frame-Options: DENY
- `frame-ancestors 'self'` - Equivalent to SAMEORIGIN (+ supports multiple origins)
- `frame-ancestors 'self' https://trusted.com` - Multiple allowed origins
  (X-Frame-Options ALLOW-FROM supports only ONE origin; frame-ancestors supports multiple)

**Priority:** CSP `frame-ancestors` takes precedence over
`X-Frame-Options` in browsers that support both.
Use both headers for backward compatibility.

**Frame-busting JavaScript (deprecated technique):**
Before X-Frame-Options: JavaScript code to prevent framing:
```javascript
if (top !== self) { top.location.href = self.location.href; }
```
This is bypassable by the `sandbox` attribute on the iframe,
which prevents the framed page from running JavaScript.
Do NOT rely on JavaScript frame-busting. Use HTTP headers.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An attacker loads your site invisibly inside an iframe and
positions their fake buttons on top of your real buttons.
`X-Frame-Options: DENY` or `Content-Security-Policy: frame-ancestors 'none'`
tells browsers to refuse to load your site inside any iframe.

**One analogy:**
> Clickjacking is like placing a sheet of glass with printed
> labels over an ATM keypad. You press what the glass says is
> "Cancel" but the actual button beneath is "Confirm."
> You're interacting with the real ATM (your real bank account)
> but the attacker's glass layer deceives you about what you're clicking.
> The ATM manufacturer's defense: mark the keypad
> with "DO NOT PLACE COVERS OVER THIS KEYPAD" (X-Frame-Options).
> The browser enforces this: if a website says "don't frame me,"
> the browser refuses to load it inside an iframe, regardless
> of what the attacker's page says.

---

### 🔩 First Principles Explanation

**Why the browser is the only defense:**

```
WHY IFRAMES WORK FOR THIS ATTACK:

  Browser's Same-Origin Policy (SOP) applies to JavaScript:
    Attacker's JavaScript on evil.com CANNOT read the content
    of bank.com's iframe (different origin = blocked by SOP).
    But: attacker doesn't need to READ the content.
    Attacker only needs the user to CLICK on the iframe.
    SOP does not prevent CLICKING on cross-origin iframes.
    
  The click event flows to bank.com's iframe, authenticated
  by the user's session cookie for bank.com.

WHY SERVER-SIDE VALIDATION DOESN'T HELP:

  Bank.com receives a completely normal authenticated request.
  The Referer header might say evil.com - but:
    1. Referer can be suppressed (rel="noreferrer" on links,
       Referrer-Policy: no-referrer header on attacker page).
    2. Many legitimate embedded use cases involve cross-origin iframes.
  
  Server has no reliable way to distinguish
  "user clicked from bank.com" vs "user clicked in iframe from evil.com."
  The browser is the only entity that knows a frame is involved.

WHY HTTP HEADERS ARE THE CORRECT FIX:

  Browser receives bank.com response headers BEFORE rendering.
  If response contains:
    X-Frame-Options: DENY
  OR
    Content-Security-Policy: frame-ancestors 'none'
  
  Browser refuses to render bank.com inside ANY iframe.
  The attacker's iframe tag loads... nothing.
  The transparent iframe overlay attack fails completely.

FRAME-ANCESTORS vs X-FRAME-OPTIONS COMPARISON:

  FEATURE              X-Frame-Options   frame-ancestors (CSP)
  ──────────────────── ──────────────── ──────────────────────
  W3C Standard         No (RFC 7034)    Yes (CSP Level 2)
  Multiple origins     No (one only)    Yes (space-separated)
  Wildcard support     No               Yes ('self' + origins)
  Report-Only mode     No               Yes (CSP Report-Only)
  Browser support      Excellent (all)  Excellent (modern)
  Priority in browser  Lower            Higher (overrides XFO)
  Recommended          Legacy compat    Primary choice
  
  RECOMMENDATION:
    Include BOTH for maximum compatibility:
    X-Frame-Options: DENY
    Content-Security-Policy: frame-ancestors 'none';

WHEN SHOULD FRAMING BE ALLOWED?

  Legitimate use cases for iframes:
  1. Your own dashboard product where users embed your widgets
     → frame-ancestors 'self' https://customer.example.com
  2. Payment provider's iframe (Stripe Elements, Braintree)
     → The payment provider allows framing from your domain
  3. Maps, video players, social media embeds
     → Those services allow specific embedding

  For apps where framing is never needed (most apps):
    frame-ancestors 'none' (strictest, most secure)
```

---

### 🧪 Thought Experiment

**SCENARIO: Video streaming site deciding on framing policy**

```
SITE: streaming.example.com (video streaming service)

REQUIREMENTS ANALYSIS:
  1. Users can embed video player on their blogs → NEED framing
  2. Account management pages (payments, settings) → MUST NOT frame
  3. Login page → MUST NOT frame (login form clickjacking)
  4. Public content pages → framing acceptable with restrictions

SOLUTION: Per-route framing policy

  nginx configuration:
  
  # Login and account pages: strict, no framing allowed
  location ~* ^/(login|account|settings|payment|profile)/ {
      add_header X-Frame-Options "DENY" always;
      add_header Content-Security-Policy "frame-ancestors 'none';" always;
  }
  
  # API routes: no framing (APIs shouldn't be embedded)
  location /api/ {
      add_header X-Frame-Options "DENY" always;
      add_header Content-Security-Policy "frame-ancestors 'none';" always;
  }
  
  # Video embed player: allow framing (this IS the embed product)
  location /embed/player/ {
      # Allow any domain to embed the player
      # (this is intentional - it's an embed product)
      # No X-Frame-Options or frame-ancestors restriction here.
      # Consider: add domain allowlisting if needed.
  }
  
  # All other pages: allow same-origin framing only
  location / {
      add_header X-Frame-Options "SAMEORIGIN" always;
      add_header Content-Security-Policy "frame-ancestors 'self';" always;
  }

ADDITIONAL PROTECTION FOR SENSITIVE ACTIONS (defense in depth):
  Even with frame-ancestors: add CSRF tokens on state-changing actions.
  Double defense: frame-ancestors prevents embedding,
  CSRF token prevents cross-origin form submissions.
  Attack would need to defeat both independently.
```

---

### 🧠 Mental Model / Analogy

> Think of the browser as a venue's security staff, and
> frame-ancestors/X-Frame-Options as a velvet rope policy.
>
> Your website says to the browser: "Only allow me to be shown
> in your establishment (any website) if they're on the approved
> guest list (frame-ancestors: specific origins, or 'self')."
>
> When evil.com tries to embed bank.com in an iframe:
> Browser acts as the bouncer. It checks bank.com's response headers.
> Bank.com says: "frame-ancestors 'none'" = no one is on the list.
> Browser refuses to display bank.com inside evil.com's iframe.
> The iframe loads... a blank space. Attack fails.
>
> JavaScript frame-busting is like the venue itself trying to
> throw out uninvited guests from another venue. The other venue
> (attacker's page) can just lock the door (sandbox attribute)
> so the attempts don't work. Only the bouncer (browser) enforcing
> the policy at the door (response headers) is reliable.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Clickjacking: attacker makes your site invisible and puts their fake button exactly where your real button is. When users click what looks like the attacker's button, they're actually clicking your button. Defense: tell the browser your site cannot be shown inside another site's iframe. Two lines in your web server config.

**Level 2 - How to use it (junior developer):**
Add to your nginx or Apache config: `add_header X-Frame-Options "DENY" always;` and `add_header Content-Security-Policy "frame-ancestors 'none';" always;`. Both headers together provide maximum compatibility. For Spring Boot: configure via `HttpSecurity.headers().frameOptions().deny()`. For Express: use `helmet()` which sets X-Frame-Options DENY and appropriate CSP. Verify with curl: `curl -I https://example.com | grep -i "x-frame\|frame-ancestors"`.

**Level 3 - How it works (mid-level engineer):**
Browser behavior when frame-ancestors is present: browser checks the response headers of the page being loaded inside an iframe. If frame-ancestors does not list the parent frame's origin (or is 'none'), browser cancels the load and does not render the content. The attacker's iframe shows a blank space. The check happens at the browser level before any JavaScript runs, so JavaScript frame-busting attempts by the embedded page are irrelevant. CSP frame-ancestors takes precedence over X-Frame-Options in browsers that support both. Old browsers (IE11) only support X-Frame-Options. Send both.

**Level 4 - Why it was designed this way (senior/staff):**
Clickjacking was a known attack vector before browsers had a defense mechanism. Early mitigation: JavaScript frame-busting. The fundamental flaw: JavaScript cannot be trusted in an iframe context because the embedding page controls the iframe's attributes. The `sandbox` attribute (HTML5) can restrict an iframe from running JavaScript at all - attacker embeds victim site in `<iframe sandbox>` → frame-busting JavaScript is blocked by sandbox → clickjacking still works. The correct architectural fix: HTTP response headers that the browser processes before any rendering, independent of JavaScript. Headers are a browser-server contract; the attacker's page cannot interfere with server headers or browser header processing.

**Level 5 - Mastery (distinguished engineer):**
Frame-ancestors integrates with CSP's broader protection model, allowing fine-grained origin control, wildcard subdomain matching, and Report-Only mode for testing (`Content-Security-Policy-Report-Only: frame-ancestors 'none'; report-uri /csp-report`). For product teams: the challenge is identifying legitimate embedding use cases before blanket denying. Enterprise dashboards, B2B SaaS with widget embeds, and payment flows (Stripe Elements embeds within partner sites) all require exceptions. Design the embedding policy as part of the product architecture, not as a post-launch security retrofit. Coordinate with the CSP policy: frame-ancestors controls who can embed you, while `default-src` and `frame-src` control what you can embed (separate, complementary controls).

---

### ⚙️ How It Works (Mechanism)

**Browser enforcement of frame-ancestors:**

```
REQUEST FLOW WITH frame-ancestors PROTECTION:

1. evil.com loads in user's browser
   HTML contains: <iframe src="https://bank.com/transfer?to=...">

2. Browser makes request to bank.com:
   GET /transfer?to=attacker&amount=500 HTTP/1.1
   Host: bank.com
   Cookie: session=<user's bank session>  ← User is authenticated!
   
3. bank.com server returns response with header:
   HTTP/1.1 200 OK
   Content-Type: text/html
   Content-Security-Policy: frame-ancestors 'none';
   X-Frame-Options: DENY
   
4. Browser checks: Is this response inside an iframe?
   YES - it's inside evil.com's iframe.
   Does bank.com's frame-ancestors allow evil.com?
   'none' = no origins allowed. evil.com is not allowed.
   
5. Browser CANCELS rendering.
   The iframe shows: blank white space.
   evil.com's attack fails.
   User sees: "CLAIM PRIZE" button but clicking it does nothing
   (the iframe beneath is blank/cancelled).

WITHOUT THE HEADER (vulnerable):

3. bank.com server returns response WITHOUT frame protection:
   HTTP/1.1 200 OK
   Content-Type: text/html
   [No X-Frame-Options or frame-ancestors header]
   
4. Browser: No framing restriction. Renders bank.com inside iframe.
   User is authenticated (session cookie sent with iframe request).
   Transfer confirmation page is fully loaded and invisible.
   
5. User clicks "CLAIM PRIZE" → clicks bank.com "CONFIRM".
   Transfer submitted. Attack succeeds.

NGINX CONFIGURATION:

  # Global (all responses): prevent any framing
  add_header X-Frame-Options "DENY" always;
  add_header Content-Security-Policy "frame-ancestors 'none';" always;
  
  # 'always' flag: applies to ALL responses including errors (4xx, 5xx)
  # Without 'always': header only on 200 responses (attacker
  # might exploit error pages that aren't protected)

SPRING BOOT CONFIGURATION:

  @Configuration
  @EnableWebSecurity
  public class SecurityConfig {
      @Bean
      public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
          http
              .headers(headers -> headers
                  .frameOptions(frame -> frame.deny())
                  // For CSP frame-ancestors:
                  .contentSecurityPolicy(csp ->
                      csp.policyDirectives("frame-ancestors 'none'")
                  )
              );
          return http.build();
      }
  }
```

---

### 💻 Code Example

**Multi-framework implementation:**

```
# nginx: global clickjacking protection for most pages
server {
    listen 443 ssl;
    server_name example.com;
    
    # Default: deny all framing (most pages)
    add_header X-Frame-Options "DENY" always;
    add_header Content-Security-Policy "frame-ancestors 'none';" always;
    
    # Exception: embed widget allowed from specific origins
    location /widgets/embed/ {
        # Remove global header for this location
        more_clear_headers X-Frame-Options;
        # Add permissive frame-ancestors for embed locations
        add_header Content-Security-Policy
            "frame-ancestors 'self' https://partner.com;" always;
    }
}
```

```python
# Flask: set headers via before_request
from flask import Flask, g, make_response, request

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    # Deny framing for all non-embed routes
    if not request.path.startswith('/embed/'):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = (
            "frame-ancestors 'none';"
        )
    return response
```

```javascript
// Express: use helmet (sets X-Frame-Options by default)
const helmet = require('helmet');
const express = require('express');
const app = express();

// helmet sets X-Frame-Options: SAMEORIGIN by default
// Override for stricter DENY:
app.use(
    helmet({
        frameguard: { action: 'deny' },
        contentSecurityPolicy: {
            directives: {
                frameAncestors: ["'none'"],
            },
        },
    })
);

// For embed routes: disable frameguard
app.use('/embed', (req, res, next) => {
    res.removeHeader('X-Frame-Options');
    res.setHeader(
        'Content-Security-Policy',
        "frame-ancestors 'self' https://trusted-partner.com"
    );
    next();
});
```

---

### ⚖️ Comparison Table

| Defense | Effectiveness | Complexity | Notes |
|:---|:---|:---|:---|
| **frame-ancestors 'none'** | Excellent | Very Low | Preferred; modern standard |
| **X-Frame-Options: DENY** | Excellent | Very Low | Legacy; use for IE11 compat |
| **Both headers** | Excellent | Very Low | Recommended: max compatibility |
| **JavaScript frame-busting** | Poor | Medium | Bypassable via sandbox attribute |
| **CSRF tokens (complement)** | Good complement | Medium | Doesn't prevent framing, but limits damage |
| **SameSite=Strict cookies** | Partial | Low | Limits session in cross-origin frames |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| JavaScript frame-busting (`if (top !== self)`) is sufficient | The `sandbox` attribute on an iframe prevents JavaScript from running in the framed page. Attacker uses `<iframe sandbox src="victim.com">`. Victim's frame-busting JavaScript is blocked by sandbox. Clickjacking still works. JavaScript frame-busting was always a workaround for the lack of HTTP header controls and is now definitively broken. Use HTTP headers exclusively. The only remaining use case for JavaScript frame-busting is as a defense-in-depth fallback for very old browsers that don't support X-Frame-Options (IE6 era) - essentially, no modern use case. |
| X-Frame-Options ALLOW-FROM allows multiple trusted origins | X-Frame-Options: ALLOW-FROM supports exactly ONE origin. If you need multiple trusted origins to embed your page, ALLOW-FROM cannot do this - you'd need to dynamically set the header based on the requesting origin (complex and error-prone). CSP `frame-ancestors` natively supports multiple origins: `frame-ancestors https://a.com https://b.com`. This is one reason frame-ancestors is preferred: it cleanly handles multi-origin embedding that ALLOW-FROM cannot. |

---

### 🚨 Failure Modes & Diagnosis

**Testing and verifying clickjacking protection:**

```
TESTING CLICKJACKING PROTECTION:

Method 1: Direct browser test
  Create test.html:
  <html><body>
    <iframe src="https://your-app.example.com/login" 
      width="800" height="600">
    </iframe>
  </body></html>
  
  Open test.html in browser (file:// or local server).
  Expected (protected): iframe shows blank or browser error.
  Vulnerable: iframe shows your login page.

Method 2: curl header inspection
  curl -I https://your-app.example.com/login | \
    grep -i "x-frame-options\|content-security-policy"
  
  Expected output includes:
    x-frame-options: DENY
    content-security-policy: frame-ancestors 'none';
  
  Missing: page is vulnerable to clickjacking.

Method 3: SecurityHeaders.com scanner
  Enter your URL at securityheaders.com
  Score A or A+: headers properly configured
  X-Frame-Options or frame-ancestors listed in results.

Method 4: ZAP passive scan
  OWASP ZAP automatically flags missing frame protection:
    Alert: "X-Frame-Options Header Not Set"
    Alert: "Missing Anti-clickjacking Header"

COMMON MISCONFIGURATION: 'always' missing in nginx
  WRONG:
    add_header X-Frame-Options "DENY";
    # Without 'always': only on 200 responses
    # 404, 500 error pages may not have the header!
  
  CORRECT:
    add_header X-Frame-Options "DENY" always;
    # 'always': applies to ALL response codes
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - security misconfiguration context
- `Security Headers` - HTTP security header overview
- `Content Security Policy` - CSP frame-ancestors directive
- `HTTP Fundamentals` - how HTTP headers work

**Builds on this:**
- `Business Logic Vulnerabilities` - UI redressing as business logic abuse
- `CORS Misconfiguration` - cross-origin iframe access control

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DENY ALL     │ X-Frame-Options: DENY                     │
│ FRAMING      │ CSP: frame-ancestors 'none';              │
├──────────────┼───────────────────────────────────────────┤
│ ALLOW SELF   │ X-Frame-Options: SAMEORIGIN               │
│ ONLY         │ CSP: frame-ancestors 'self';              │
├──────────────┼───────────────────────────────────────────┤
│ TRUSTED ONLY │ CSP: frame-ancestors 'self' https://x.com;│
│              │ (X-Frame-Options can't do multiple origins)│
├──────────────┼───────────────────────────────────────────┤
│ TEST         │ Create iframe pointing to your login page;│
│              │ Protected = blank; Vulnerable = page loads │
├──────────────┼───────────────────────────────────────────┤
│ JS FRAMEBUSTING│ INSECURE: bypassable via sandbox attr   │
│              │ Use HTTP headers only                     │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Security controls must be enforced at the layer that has
authority." JavaScript frame-busting tries to enforce an
origin policy from within the framed document - but the
embedding document has more authority (it controls the iframe
attributes including sandbox). The layer with authority over
whether a page can be framed is the HTTP response headers
processed by the browser. The browser is the enforcing agent;
HTTP headers are the policy expression. This principle applies
broadly: access controls should be enforced at the layer
that cannot be bypassed by the attacker. Server-side validation
(not client-side only), HTTP headers (not JavaScript), database
query filtering (not just UI hiding) - always enforce controls
at the authoritative layer.

---

### 💡 The Surprising Truth

Modern browsers (Chrome 85+, Firefox 79+) began implementing
`Sec-Fetch-Dest` and `Sec-Fetch-Mode` request headers that
allow servers to detect whether a request is coming from an
iframe context, even without the user's action. These headers
are "forbidden" headers (cannot be set by JavaScript) and
accurately report the fetch context: `Sec-Fetch-Dest: iframe`
when loaded in an iframe. This gives servers a secondary
detection mechanism for iframe embedding. However, this is
a detection mechanism, not a prevention mechanism: by the
time the server sees the header, it has already processed
the request. The prevention (X-Frame-Options and frame-ancestors)
happens at the browser level, before the iframe content is
displayed. Sec-Fetch headers are useful for server-side
logging and analytics about framing attempts, not as the
primary defense.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the clickjacking attack: invisible iframe overlay,
   user clicks attacker's visible element, actually clicks victim's
   hidden element.
2. **IMPLEMENT** both X-Frame-Options and frame-ancestors headers
   in a web server config (nginx, Apache, or application framework).
3. **TEST** clickjacking protection by creating a test HTML file
   with an iframe pointing to the protected page.
4. **EXPLAIN** why JavaScript frame-busting (`if (top !== self)`)
   is bypassable and why HTTP headers are the correct fix.

---

### 🎯 Interview Deep-Dive

**Q: What is clickjacking? How does it work and how do you prevent it?**

*Why they ask:* Tests understanding of browser security model and
HTTP header-based defenses. Common entry-level security question.

*Strong answer includes:*
- Mechanism: attacker embeds target site in invisible iframe,
  positions attacker's UI elements over target's interactive elements.
  User thinks they're clicking attacker's button;
  actually clicking target site's button (in an authenticated context).
- Example: Facebook Like-jacking 2010, or bank transfer scenario.
- Prevention: X-Frame-Options: DENY or CSP frame-ancestors: none.
  Browser sees the header, refuses to load the page inside any iframe.
- Header comparison: frame-ancestors (CSP) is the modern standard
  and supports multiple origins; X-Frame-Options is legacy.
  Use both for maximum browser compatibility.
- Why JavaScript frame-busting doesn't work: the `sandbox` iframe
  attribute prevents JavaScript execution in the framed page.
  HTTP headers are the only reliable defense.
- Additional context: for apps that need legitimate embedding
  (embed players, widgets), use frame-ancestors with specific
  trusted origins rather than DENY.