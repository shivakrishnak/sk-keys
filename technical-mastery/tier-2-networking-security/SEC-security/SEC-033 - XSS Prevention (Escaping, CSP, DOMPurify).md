---
id: SEC-033
title: "XSS Prevention (Escaping, CSP, DOMPurify)"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-012, SEC-017, SEC-019, SEC-031
used_by: SEC-063, SEC-067, SEC-088
related: SEC-012, SEC-017, SEC-019, SEC-031, SEC-063, SEC-067, SEC-088
tags:
  - security
  - xss
  - output-encoding
  - dompurify
  - csp
  - escaping
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/sec/xss-prevention-escaping-csp-dompurify/
---

⚡ TL;DR - XSS prevention requires context-aware output
encoding as the primary defense, with CSP as the second layer.

**The three rules of XSS prevention:**
1. Never insert untrusted data into the page without encoding.
2. HTML-encode when inserting into HTML context.
3. Match the encoding to the context: HTML, JavaScript,
   URL, CSS, and attribute each require different encoding rules.

**Practical tools:**
- **Modern frameworks** (React, Vue, Angular): auto-escape by default.
  The danger is escape hatches (`dangerouslySetInnerHTML`,
  `v-html`, `bypassSecurityTrustHtml`).
- **DOMPurify:** When you MUST render user HTML (rich text editor,
  Markdown renderer). DOMPurify sanitizes HTML to remove script
  elements while preserving safe formatting. Not a substitute for
  encoding - only for HTML that must stay HTML.
- **CSP with nonces:** Second layer. Even if injection occurs,
  CSP blocks script execution.

---

| #033 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | XSS, Input Validation vs Output Encoding, Security Headers, CSP | |
| **Used by:** | SAST, Business Logic Vulnerabilities, CORS Misconfiguration | |
| **Related:** | XSS, CSP, Input Validation vs Output Encoding, Advanced XSS | |

---

### 🔥 The Problem This Solves

**WHY OUTPUT ENCODING IS THE PRIMARY FIX:**
XSS occurs when user-supplied data is placed into an HTML page
in a way that the browser interprets some of it as code (script).
Output encoding converts data into a representation the browser
cannot misinterpret as code: `<` becomes `&lt;`, which the
browser displays as the `<` character but NEVER treats as
HTML tag opening syntax.

**WHY CONTEXT MATTERS:**
HTML encoding is correct for HTML body. But if the same data
goes into a JavaScript string: `&lt;` is wrong (JavaScript
doesn't understand HTML entities). If data goes into a URL:
`<` should become `%3C`. Using the wrong encoding for the
context either fails to prevent XSS or produces garbled output.
Context-aware encoding is not optional - it's the difference
between working prevention and broken prevention.

---

### 📘 Textbook Definition

**XSS Prevention:** Techniques that prevent attacker-controlled
data from being interpreted as executable code by the browser.

**Output Encoding:** Converting characters that have special
meaning in the target context into their safe equivalent
representation, so they are displayed but not executed.

**Encoding Contexts (OWASP XSS Prevention Rules):**

**Rule 1 - HTML Body Context:**
Characters: `&`, `<`, `>`, `"`, `'`, `/`
Encoding: HTML entities (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#x27;`, `&#x2F;`)
Library: `html.escape()` (Python), `StringEscapeUtils.escapeHtml4()` (Java),
Jinja2 `{{ variable }}` (auto), React JSX `{variable}` (auto)
Example: `<div>{{ user.name }}</div>` - auto-encoded in most template engines

**Rule 2 - HTML Attribute Context:**
Same characters as Rule 1, PLUS: quote/double-quote if not quoting attribute value
Always use quoted attributes: `<div class="{{ variable }}">` not `<div class={{ variable }}>`

**Rule 3 - JavaScript Context:**
Never insert untrusted data into JavaScript. If unavoidable:
JSON encoding only (not arbitrary string insertion).
Use `JSON.dumps(variable)` server-side for values that must
appear in JavaScript literals.

**Rule 4 - URL Context:**
URL-encode all characters except unreserved characters.
`urllib.parse.quote(variable)` (Python), `encodeURIComponent(variable)` (JS).
In `href`, `src`, `action`: validate that the URL scheme is allowed
(not `javascript:`, `data:`, `vbscript:`).

**Rule 5 - CSS Context:**
Avoid inserting user data into CSS values.
If necessary: CSS hex escaping. Consider CSS injection separately.

**Rule 6 - DOM Context:**
Using DOM APIs safely: prefer `textContent` over `innerHTML`.
`element.textContent = userInput` - safe (renders as text).
`element.innerHTML = userInput` - dangerous (renders as HTML).

**HTML Sanitization (DOMPurify):**
When user content MUST contain HTML (rich text, Markdown-rendered):
DOMPurify is a sanitization library that parses HTML with a
strict allowlist and removes anything dangerous (script tags,
event handlers, javascript: URLs). Output of DOMPurify
can be safely set to `innerHTML`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTML-encode user data before putting it in HTML pages. Use
`textContent` not `innerHTML` in JavaScript. For user HTML:
sanitize with DOMPurify, not raw innerHTML. CSP as second layer.

**One analogy:**
> Output encoding is like using quotation marks in text.
> Without quotes: a message saying "type QUIT to exit"
> might be executed as a command QUIT. With quotes: "type
> 'QUIT' to exit" is clearly data, not instruction. HTML
> encoding wraps user data in the HTML equivalent of quotes
> that the browser reads as "this is data, display it,
> don't interpret it." `&lt;script&gt;` is clearly data
> (display `<script>`). `<script>` is code (execute).

---

### 🔩 First Principles Explanation

**The five HTML contexts and why each needs different encoding:**

```
HTML DOCUMENT CONTEXTS WHERE USER DATA MAY APPEAR:

CONTEXT 1: HTML Element Body
  Example: <div>USER_DATA</div>
  Risk: <script>stealCookies()</script>
  Encoding: HTML entity encoding
    < → &lt;    > → &gt;    & → &amp;
    " → &quot;  ' → &#x27;
  Result: &lt;script&gt;stealCookies()&lt;/script&gt;
  Browser renders: <script>stealCookies()</script> (as text, not executed)

CONTEXT 2: HTML Attribute
  Example: <input value="USER_DATA">
  Risk: "><script>..., ' onmouseover='stealCookies()
  Encoding: HTML entity encoding (same as body)
  Additional: ALWAYS quote attributes (" or ')
  Unquoted: <input value=USER_DATA>
    Attacker: USER_DATA = 'onmouseover=stealCookies()'
    Result: <input value=onmouseover=stealCookies()>
    Browser: attribute misparse → event handler executes!

CONTEXT 3: JavaScript
  Example: var x = "USER_DATA";   (in a script block)
  Risk: USER_DATA = "; stealCookies(); //
  Result: var x = ""; stealCookies(); //"; → code injection
  
  CORRECT APPROACH: Don't put user data in JavaScript.
  If unavoidable: use JSON.dumps/json_encode to produce
    a properly escaped JSON string literal.
  BAD:  var x = "{{ user.name }}";  (template in script block)
  GOOD: var x = {{ user.name | tojson }};
        (tojson/JSON.dumps produces: "Alice" or "O'Brien" safely)

CONTEXT 4: URL Parameter
  Example: <a href="/search?q=USER_DATA">
  Risk: USER_DATA = javascript:stealCookies()
  Two-part fix:
    a) URL-encode the value: quote(user_input) → %3C...%3E
    b) Validate URL scheme for href/src: only http/https allowed
  BAD:  <a href="{{ url }}">  (url could be javascript:...)
  GOOD: <a href="{{ url | safe_url }}">
        (safe_url validates scheme AND URL-encodes parameters)

CONTEXT 5: DOM JavaScript (client-side)
  Example: element.innerHTML = userInput;
  Risk: <script> or <img onerror=...> in userInput
  
  SAFE ALTERNATIVES:
    element.textContent = userInput;    // Never HTML-parses
    element.setAttribute('data-val', userInput);  // Attribute
    element.insertAdjacentText('beforeend', userInput);
  
  WHEN innerHTML IS REQUIRED (user-generated HTML):
    element.innerHTML = DOMPurify.sanitize(userInput);
    // DOMPurify removes script, event handlers, javascript: URLs
    // while preserving safe formatting (b, i, p, a, etc.)
```

---

### 🧪 Thought Experiment

**SCENARIO: Building a comment system that supports Markdown**

```
REQUIREMENT: Users write comments in Markdown.
  Rendered output should show: bold, italic, links, code blocks.
  Must NOT execute JavaScript.

NAIVE APPROACH 1 (vulnerable):
  1. Accept Markdown text.
  2. Convert to HTML with marked.js.
  3. element.innerHTML = markedOutput;
  
  Attack: [click me](javascript:stealCookies())
  Result: marked.js generates <a href="javascript:stealCookies()">
  Element.innerHTML renders it. User clicks. XSS.

NAIVE APPROACH 2 (wrong fix):
  DOMPurify.sanitize(userMarkdown)  // Sanitize the Markdown TEXT
  Problem: DOMPurify sanitizes HTML, not Markdown.
    Markdown is not HTML yet. Sanitizing pre-converted
    Markdown achieves nothing useful.
    
CORRECT APPROACH:
  1. Accept Markdown text (validate: character limits, no null bytes).
  2. Convert to HTML with marked.js or remark.
     result = marked(userMarkdown);
  3. THEN sanitize the HTML output:
     safeHTML = DOMPurify.sanitize(result, {
       ALLOWED_TAGS: ['p', 'b', 'i', 'em', 'strong', 
                      'code', 'pre', 'a', 'ul', 'ol', 'li'],
       ALLOWED_ATTR: {'a': ['href']},
       // Validate href: DOMPurify rejects javascript: by default
       ALLOW_DATA_ATTR: false,
       FORCE_BODY: true,
     });
  4. element.innerHTML = safeHTML;
  
  Result: [click me](javascript:stealCookies())
    → marked() → <a href="javascript:stealCookies()">click me</a>
    → DOMPurify → <a>click me</a>  (href removed: javascript: scheme)
    Safe: clicking the link does nothing (no href).
  
  ADDITIONAL: Add CSP with nonce
    Even if a bypass exists in DOMPurify: CSP blocks script execution.
    Defense in depth: sanitization + CSP = two independent layers.
```

---

### 🧠 Mental Model / Analogy

> XSS prevention is like a border control that distinguishes
> tourists from terrorists based on what they're CARRYING,
> not who they are. All data (tourists) may enter, but anything
> that could be used as a weapon (executable code, script tags,
> event handlers) is confiscated at the border (encoding/sanitization).
> Output encoding = the confiscation process at the input side
> (encode before displaying). DOMPurify = the airport scanner
> at the exit (check HTML for weapons before rendering).
> CSP = the metal detector inside every room (even if something
> slips through, execution is blocked). Three independent checkpoints,
> each stopping a different attack vector.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When displaying user text on a webpage: convert special
characters like `<` and `>` into their display-only versions
(`&lt;` and `&gt;`). The browser shows them but doesn't
treat them as HTML. In React and most modern frameworks:
this happens automatically when you use `{variable}` in JSX.
The dangerous shortcut is `dangerouslySetInnerHTML` - which
bypasses encoding and should only be used with sanitized content.

**Level 2 - How to use it (junior developer):**
Using React/Vue/Angular: `{variable}` auto-encodes. Never use
`dangerouslySetInnerHTML`, `v-html`, or `[innerHTML]` with
user data unless you've sanitized it with DOMPurify first.
For server-side templates: use Jinja2/Thymeleaf/EJS auto-escaping
(`{{ variable }}` is auto-escaped, `{{ variable | safe }}`
is not - never use `safe` with user data). For rich text:
`DOMPurify.sanitize(content)` before rendering to `innerHTML`.

**Level 3 - How it works (mid-level engineer):**
Template engines escape by context: Jinja2's `{{ }}` applies
HTML entity encoding for HTML context. When rendering user
data in script blocks: `{{ value | tojson }}` is needed,
not `{{ value }}` (HTML entity encoding is wrong for JavaScript
context). URL context: `{{ url | urlencode }}` AND scheme validation.
DOM context: `textContent` is always safe. `innerHTML` requires
DOMPurify for user HTML. Attribute context: HTML encoding +
always use quoted attributes. The OWASP XSS Prevention Cheat Sheet
(cheatsheetseries.owasp.org) provides the complete rule set.

**Level 4 - Why it was designed this way (senior/staff):**
Web application security evolved alongside the browser.
Early web: static HTML, no user input rendered. As dynamic
content was added: developers used template engines that
rendered user input into HTML pages. The encoding requirement
emerged when injection attacks were discovered. Frameworks
that make encoding the DEFAULT (React's JSX auto-escaping,
Angular's template binding) prevent XSS more effectively
than frameworks that make encoding OPT-IN. The principle:
the safe operation (encoding) should be the default; the
dangerous operation (bypass encoding) should require explicit,
named, dangerous-sounding APIs (`dangerouslySetInnerHTML`).
The semantics of the API communicate the risk.

**Level 5 - Mastery (distinguished engineer):**
Browser-level protections have evolved: the X-XSS-Protection
header (now deprecated - caused more bypasses than it fixed),
CSP with nonces (strong, widely deployed), Trusted Types API
(newest: restricts which JavaScript can assign to dangerous
DOM properties). Trusted Types + CSP forms the strongest
XSS prevention stack: Trusted Types prevents script injection
via dangerous DOM APIs even if the developer uses innerHTML
(the policy requires a TrustedHTML object from the sanitizer,
not a raw string). This moves XSS prevention from "remember
to encode everything" to "the browser enforces that sanitization
happened." The adoption curve for Trusted Types is long:
requires updating all code that writes to innerHTML, and
many third-party libraries don't support it yet. Phased
adoption: enable Trusted Types in report-only mode, fix
violations, then enforce.

---

### ⚙️ How It Works (Mechanism)

**How DOMPurify sanitizes HTML:**

```
DOMPURIFY SANITIZATION ALGORITHM:

Input: "<b>Hello</b> <script>stealCookies()</script>"

Step 1: Parse with browser's HTML parser
  DOMPurify creates a sandboxed DOM from the input.
  This parsing is identical to what the browser would do.
  All tags and attributes are properly identified.

Step 2: Walk the DOM tree
  DOMPurify visits each node: elements, attributes, text.

Step 3: Apply allowlist
  For each element: is the tag in ALLOWED_TAGS?
    <b>: YES (allowed) → keep
    <script>: NO (not allowed) → REMOVE entire subtree
  
  For each attribute: is it in ALLOWED_ATTR for this tag?
    <a href="...">: href for a: YES → check value
    <a href="javascript:...">: javascript: scheme → REMOVE href
    <img onerror="...">: onerror event handler → REMOVE attribute

Step 4: Serialize back to HTML string
  Remaining (safe) nodes serialized to HTML.
  
Output: "<b>Hello</b> " (script removed, only safe b tag kept)

WHY DOMPURIFY IS BETTER THAN REGEX:
  Regex cannot parse HTML correctly.
  <script> has many representations:
    <SCRIPT>, <ScRiPt>, <script\n>, <script/>,
    <scr<script>ipt>, <!--[if IE]><script>...<![endif]-->
  DOMPurify uses the browser's own HTML parser:
  whatever the browser accepts → DOMPurify processes correctly.
  Regex XSS filters can be bypassed with unusual representations.
  DOMPurify cannot be bypassed this way (browser parses it first).
  
  KNOWN BYPASSES: DOMPurify has had bypasses in the past.
  Keep DOMPurify updated. Check their GitHub for known issues.
  Pin to a specific version in production, update deliberately.
```

---

### 💻 Code Example

**XSS prevention patterns for common scenarios:**

```javascript
// CONTEXT 1: JavaScript DOM - textContent vs innerHTML

// BAD: renders user input as HTML - executes scripts
function renderCommentBad(comment) {
  document.getElementById('comment').innerHTML = comment;
  // Attack: comment = '<script>stealCookies()</script>'
  // Result: script executes
}

// GOOD: textContent - always renders as text, never HTML
function renderCommentGood(comment) {
  document.getElementById('comment').textContent = comment;
  // Attack: same payload
  // Result: displays '<script>stealCookies()</script>' as text
}

// CONTEXT 2: When innerHTML IS required (user-generated rich text)
import DOMPurify from 'dompurify';

function renderRichContent(userHTML) {
  const sanitized = DOMPurify.sanitize(userHTML, {
    ALLOWED_TAGS: [
      'p', 'b', 'i', 'em', 'strong', 'u', 'br',
      'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a'
    ],
    ALLOWED_ATTR: {
      'a': ['href', 'title'],
      // Note: DOMPurify blocks javascript: in href by default
    },
    ALLOW_DATA_ATTR: false,  // No data-* attributes (can be misused)
  });
  
  document.getElementById('content').innerHTML = sanitized;
}

// CONTEXT 3: React - auto-escaped by default
// SAFE: JSX auto-encodes
function CommentDisplay({ userInput }) {
  return <div>{userInput}</div>;
  // userInput = '<script>steal()</script>'
  // Renders as: &lt;script&gt;steal()&lt;/script&gt;
  // Displayed as text, not executed
}

// BAD: dangerouslySetInnerHTML bypasses encoding
function CommentDisplayBad({ userInput }) {
  return (
    <div dangerouslySetInnerHTML={{ __html: userInput }} />
  );
  // DANGEROUS: executes HTML/JavaScript in userInput
}

// GOOD: dangerouslySetInnerHTML with DOMPurify
function CommentDisplaySanitized({ userHTML }) {
  const sanitized = DOMPurify.sanitize(userHTML);
  return (
    <div dangerouslySetInnerHTML={{ __html: sanitized }} />
  );
  // Only use when HTML must render (not plain text)
}

// CONTEXT 4: URL safety - prevent javascript: injection
function renderLink(url) {
  // BAD: directly render user-provided URL
  // element.href = url;  // Could be javascript:stealCookies()
  
  // GOOD: validate URL scheme before rendering
  const isAllowed = /^(https?:\/\/|\/)/i.test(url);
  if (!isAllowed) {
    console.warn('Blocked unsafe URL:', url);
    return;
  }
  element.href = url;  // Safe: http/https/relative only
}

// CONTEXT 5: Server-side Python Jinja2 template
// SAFE: {{ variable }} is auto-HTML-encoded by Jinja2
# template.html:
# <div>{{ user_comment }}</div>          ← Auto-encoded. Safe.
# <div>{{ user_comment | safe }}</div>   ← NOT encoded. Dangerous.
# <script>var x = {{ user_data | tojson }};</script>  ← JSON for JS context
```

---

### ⚖️ Comparison Table

| Technique | Protection | Use Case | Notes |
|:---|:---|:---|:---|
| **HTML encoding** | HTML/attribute context | Primary: any user data in HTML | Auto in React/Vue/Jinja2 |
| **textContent** | DOM context | Displaying user text in DOM | Never executes HTML |
| **DOMPurify** | User-generated HTML | Rich text, Markdown output | Must use allowlist |
| **URL validation** | href/src/action context | Links, form actions, redirects | Block javascript: scheme |
| **JSON encoding** | JavaScript context | Data in script blocks | Use tojson, not HTML entities |
| **CSP with nonce** | All contexts (second layer) | Defense in depth | Blocks execution if encoding fails |
| **Trusted Types** | DOM sinks | Advanced: require sanitized values | Chrome only (2024) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| HTML encoding is sufficient for all contexts | HTML encoding is correct for HTML body and attribute contexts only. JavaScript context requires JSON encoding (HTML entities are decoded in JS: `&lt;` in a JS string is literally `&lt;`, not `<`, so it doesn't prevent injection). URL context requires URL encoding (percent encoding). CSS context has its own escaping. Using HTML encoding for all contexts is wrong - it either prevents XSS (if it removes special chars) or causes garbled output without preventing XSS (if the wrong encoding is applied). |
| DOMPurify.sanitize() output can be used in any context | DOMPurify produces HTML-safe HTML. It is designed to be set to innerHTML. Using DOMPurify output in a JavaScript string or as a URL parameter would require different encoding on top of the DOMPurify output. DOMPurify is specifically for: user-provided HTML that will be set to innerHTML. For user text that should be DISPLAYED (not rendered as HTML): use textContent, which doesn't require DOMPurify. |

---

### 🚨 Failure Modes & Diagnosis

**Common XSS that bypasses naive prevention:**

```
BYPASS 1: Attribute injection without quotes
  Vulnerable: <div class={{ user.class_attr }}>
  (Jinja2 without quotes around attribute value)
  Attack: class_attr = "x onmouseover=stealCookies()"
  Result: <div class=x onmouseover=stealCookies()>
  Browser: parses multiple attributes, executes mouseover
  
  Fix: ALWAYS quote template attribute values:
    <div class="{{ user.class_attr }}">  (with quotes)

BYPASS 2: javascript: URL in href
  Vulnerable: <a href="{{ user.url }}">
  (URL is HTML-encoded but not scheme-validated)
  Attack: url = "javascript:stealCookies()"
  HTML encoding doesn't help (no special chars to encode)
  Browser: navigates to javascript: URL → executes code
  
  Fix: validate URL scheme server-side:
    if not (url.startswith('http://') or url.startswith('https://')
            or url.startswith('/')):
        url = '#'  # Replace invalid URLs with safe default

BYPASS 3: Double-decode attack
  Vulnerable: decode URL, then HTML-encode, then render
  Attack: %3Cscript%3E → decoded: <script> → HTML encoded: &lt;script&gt;
  If a second decode happens later: &lt; → < → XSS
  Fix: decode once, encode once, in the correct context.
    Don't encode/decode multiple times.

BYPASS 4: DOM XSS source to sink
  JavaScript: var x = location.hash; element.innerHTML = x;
  URL: #<img src=x onerror=stealCookies()>
  Server has no visibility into this (hash not sent to server).
  Server-side encoding doesn't help.
  Fix: element.textContent = location.hash; (or use DOMPurify)
  SAST: search for innerHTML, document.write, eval() receiving
    location.*, document.URL, URLSearchParams.

DIAGNOSIS TOOLS:
  - DOM Invader (Burp Suite extension): auto-detects DOM sources/sinks
  - XSS Hunter: detect blind XSS (stored in admin panel, fires when admin views)
  - PortSwigger Web Security Academy: DOM XSS labs
  - Browser DevTools: search for sink functions, trace DOM writes
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Cross-Site Scripting (XSS)` - the vulnerability
- `Input Validation vs Output Encoding` - the foundational principle
- `Content Security Policy (CSP)` - the second layer

**Builds on this:**
- `SAST` - automated scanning for XSS vulnerabilities
- `Advanced XSS` - DOM XSS, mutation XSS, CSP bypass

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HTML CONTEXT │ HTML-encode: &lt; &gt; &amp; &quot; &#x27;│
│              │ Auto in React {}, Jinja2 {{}}, Angular {{}}│
├──────────────┼───────────────────────────────────────────┤
│ JS CONTEXT   │ Use JSON.dumps/tojson. NEVER f-string in  │
│              │ script blocks with user data              │
├──────────────┼───────────────────────────────────────────┤
│ URL CONTEXT  │ urlencode() + validate scheme (http/https)│
│              │ Block javascript: data: vbscript:         │
├──────────────┼───────────────────────────────────────────┤
│ DOM CONTEXT  │ textContent (always safe)                 │
│              │ innerHTML = DOMPurify.sanitize() (if HTML)│
├──────────────┼───────────────────────────────────────────┤
│ DOMPURIFY    │ Use when user HTML must render as HTML     │
│              │ Use allowlist, keep updated               │
├──────────────┼───────────────────────────────────────────┤
│ SECOND LAYER │ CSP with nonces: blocks execution even    │
│              │ when encoding fails                       │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"The default operation should be the safe operation."
React's JSX encoding is enabled by default; you have to
opt OUT with `dangerouslySetInnerHTML`. Jinja2's auto-escaping
is enabled by default; you have to opt OUT with `| safe`.
This "safe by default" design is a critical security property.
When security requires active thought (remembering to encode),
it fails whenever a developer forgets. When safety is the
default and danger requires explicit naming, security holds
even under time pressure. Apply this pattern to your own
APIs: when designing functions that handle potentially
dangerous data, make the safe behavior the default and
require explicit, named opt-out for dangerous behavior.

---

### 💡 The Surprising Truth

DOMPurify has had security bypasses found in it. Attackers
specifically research DOMPurify bypass techniques because
they know it's widely deployed. The DOMPurify team fixes
them rapidly (check their GitHub releases). This creates
an important lesson: even a well-designed, actively maintained
sanitization library is not perfect. This is exactly why
defense in depth matters: CSP with nonces provides a second
layer that stops XSS execution even if DOMPurify is bypassed.
A bypass of DOMPurify against a page WITH CSP nonces:
the injected script doesn't have a matching nonce → the
browser blocks execution → the bypass fails. A bypass of
DOMPurify against a page WITHOUT CSP: game over. Two layers
surviving when one fails is the mathematical argument for
defense in depth.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** the correct encoding for HTML, JavaScript,
   URL, and DOM contexts and explain why each context differs.
2. **CONFIGURE** DOMPurify with an appropriate allowlist
   for a rich text comment system.
3. **EXPLAIN** why `textContent` is safer than `innerHTML`
   and when `innerHTML` + DOMPurify is the right choice.
4. **SPOT** in code review: `dangerouslySetInnerHTML`,
   `v-html`, or `innerHTML` with user data - and determine
   if sanitization is correctly applied.

---

### 🎯 Interview Deep-Dive

**Q: How do you prevent XSS in a web application that
supports user-generated rich text (bold, links, images)?**

*Why they ask:* Plain-text XSS prevention is straightforward.
Rich text requires real security thinking about sanitization.

*Strong answer includes:*
- For plain text display: textContent or auto-escaping templates.
  No rich text → no HTML in the rendered page → XSS impossible
  via this path.
- For rich text: markdown-to-HTML conversion (marked.js, remark)
  followed by HTML sanitization with DOMPurify.
  Order: (1) accept Markdown, (2) convert to HTML, (3) sanitize HTML.
  NOT: accept HTML directly, sanitize, render. (Parsing HTML from users
  is too dangerous a starting point.)
- DOMPurify configuration: explicit ALLOWED_TAGS allowlist (default
  is permissive). Restrict to needed tags only (b, i, p, a, code,
  pre, ul, ol, li). Restrict ALLOWED_ATTR. Allow href on a, but
  DOMPurify blocks javascript: by default.
- CSP as second layer: nonce-based CSP. Even if DOMPurify is
  bypassed: CSP nonces block unauthorized script execution.
- Server-side validation: validate user input length, character limits.
  Reject null bytes, invalid UTF-8. Not XSS prevention per se,
  but removes garbage before processing.
- DOMPurify updates: pin version, audit releases, update when
  security fixes are released. A known DOMPurify bypass without
  CSP is critical; with CSP it's mitigated.