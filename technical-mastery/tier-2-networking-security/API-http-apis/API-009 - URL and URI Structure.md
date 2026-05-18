---
id: API-009
title: "URL and URI Structure"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★☆☆
depends_on: API-003, API-006
used_by: API-012, API-015, API-029
related: API-007, API-008, API-019
tags:
  - http
  - url
  - uri
  - rest
  - routing
  - foundational
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/api/url-and-uri-structure/
---

⚡ TL;DR - A URL is the address of a resource on the web;
its structure (scheme + authority + path + query + fragment)
is the coordinate system of the internet, and understanding
each component explains why API design, routing, caching,
and security work the way they do.

---

| #009 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP Protocol, HTTP Request Structure | |
| **Used by:** | Query Parameters, API Endpoint Design, API Versioning | |
| **Related:** | HTTP Methods, HTTP Status Codes, RESTful Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before URLs, Internet resources were accessed with host-
specific commands, file paths, or protocol-specific syntax.
FTP had its own addressing. Gopher had its own. Email had
its own. There was no universal addressing scheme that
could identify any resource on any server using any protocol
with a single format that all systems could parse.

**THE BREAKING POINT:**
Tim Berners-Lee in 1989 faced a specific problem: CERN needed
to link documentation across different computers. Each
computer had its own filesystem, its own protocol. A link
from document A (on machine X) to document B (on machine Y)
required knowing both machines' specific addressing syntax.
There was no portable address format that would work on any
machine, through any network, to any server.

**THE INVENTION MOMENT:**
The URL was designed as a universal resource identifier -
a single string format that encoded all the information
needed to retrieve any resource: how to connect (scheme),
where to connect (host/port), what to request (path),
and with what parameters (query). The format was designed
to be human-readable, copy-pasteable, and parseable by
any software that implemented the standard.

**EVOLUTION:**
URL (1991) - web. URI (1994) - generalization. URN (1994) -
names without location. RFC 3986 (2005) formalized the
generic URI syntax. Internationalized Resource Identifiers
(IRI, RFC 3987) added Unicode support. Today, URLs are
the universal addressing mechanism for REST APIs, WebSockets,
gRPC services, OAuth redirects, DNS resolution, and every
web browser address bar.

---

### 📘 Textbook Definition

A URI (Uniform Resource Identifier) is a compact sequence
of characters that identifies a resource. A URL (Uniform
Resource Locator) is a type of URI that specifies the
location and retrieval mechanism for a resource. The URL
syntax defined in RFC 3986 consists of: scheme (protocol),
authority (host + optional port), path (resource location
on host), query (key-value parameters), and fragment
(client-side sub-resource reference). Percent-encoding
allows arbitrary characters to be safely included in URLs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A URL is a uniquely structured address: scheme identifies
how, host identifies where, path identifies what, query
adds filters, and fragment references a sub-section.

**One analogy:**
> A URL is like a physical mailing address with extra
> information. "https" is the postal service (how to deliver).
> "api.example.com:443" is the street and building (where
> to deliver). "/users/42/orders" is the specific office
> and mailbox (what to look for). "?status=pending&page=2"
> is a note to the recipient ("only the pending ones, page 2").
> "#section-3" is a Post-it note on top saying "open to
> page 3 when you arrive" - handled entirely by the recipient,
> never sent to the mail carrier.

**One insight:**
The fragment (`#section`) is the one part of a URL that
is never sent to the server. The browser uses it entirely
on the client side. This single fact explains how Single
Page Applications routing works (changing `#/dashboard` does
not trigger a server request), why `#` is used for client-
side routing, and why Fragment Identifier Leakage is an
OWASP security issue.

---

### 🔩 First Principles Explanation

**URL ANATOMY:**

```
https://api.example.com:443/v1/users/42/orders?status=active&page=2#results

└─┬──┘  └──────┬──────┘└┬┘└────────┬────────┘└────────┬─────────┘└──┬───┘
scheme    host        port    path              query             fragment
```

**Component meanings:**

**Scheme (`https://`):**
The protocol for retrieving the resource. Also: `http`,
`ftp`, `mailto`, `ws` (WebSocket), `wss` (WebSocket Secure).
Determines the default port (https=443, http=80, ftp=21).

**Authority (`api.example.com:443`):**
- Host: DNS name or IP address of the server
- Port: optional if using the scheme default (443 for https)
- Optional userinfo (`user:password@host`): deprecated for
  HTTP due to credential leakage in logs and proxy servers

**Path (`/v1/users/42/orders`):**
Resource hierarchy on the server. The server interprets
the path - it is not a filesystem path. In REST APIs, the
path represents the resource being operated on.

**Query (`?status=active&page=2`):**
Key-value pairs for additional request parameters.
- Begins with `?`
- Pairs separated by `&`
- Key and value separated by `=`
- Values are percent-encoded if they contain special chars

**Fragment (`#results`):**
Sub-resource reference. **Never sent to the server.**
Used by the browser (or client) after receiving the response.

**PERCENT-ENCODING:**
Characters not allowed in URLs must be percent-encoded:
a `%` followed by two hex digits representing the byte value.
- Space → `%20`
- `/` in a value → `%2F`
- `&` in a value → `%26`
- `+` → `%2B` (note: `+` in query strings means space in
  some legacy conventions - use `%20` for portability)

---

### 🧪 Thought Experiment

**SETUP:**
A user searches for `C++ programming`. Your API endpoint
is `/search?q=C++ programming`. What does the server receive?

**WHAT HAPPENS WITHOUT ENCODING:**
The `+` character in a URL query string has ambiguous
meaning: some servers interpret `+` as a space (form
encoding), others as a literal `+`. The space in "C++ programming"
would need to be encoded. The unencoded URL is:
`/search?q=C++ programming` which most parsers would
reject or misparse.

**WHAT HAPPENS WITH ENCODING:**
Correctly encoded: `/search?q=C%2B%2B%20programming`
`%2B` is `+`, `%20` is space. The server receives the
exact bytes `C++ programming` after decoding.

**THE INSIGHT:**
Every component of a URL has a reserved character set.
Characters outside that set must be percent-encoded.
This is not optional - it is the only way to distinguish
between a `&` that separates query parameters and a `&`
that is part of a parameter value. Frameworks encode and
decode this automatically, but understanding it is essential
when building URLs manually, debugging misencoded requests,
or dealing with double-encoding bugs.

---

### 🧠 Mental Model / Analogy

> Think of a URL as a structured phone number:
> the country code (scheme) identifies the phone system,
> the area code (host) identifies the region and exchange,
> the extension (path) identifies the specific person,
> and extra digits after the call connects (query) are
> like pressing 1 for billing, 2 for support. The note
> you scribble for yourself after hanging up (fragment)
> is just for you - the phone company never sees it.

Mapping:
- "Country code" → scheme (protocol)
- "Area code + number" → host + port
- "Extension" → path (specific resource)
- "Press 1 for billing" → query parameters
- "Your personal note" → fragment (client-only)

Where this analogy breaks down: unlike phone numbers, URLs
must encode their characters to avoid ambiguity with
structural characters (`/`, `?`, `&`, `=`, `#`). Phone
numbers use a closed numeric alphabet that does not need
escaping.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A URL is a web address. "https://google.com/search?q=cats"
means: use the secure web protocol, go to google.com, look
at /search, with the query "cats." Every part tells the
network something different about where to go and what to look for.

**Level 2 - How to use it (junior developer):**
Build URLs carefully. Path segments (`/users/42`) identify
the resource. Query parameters (`?status=active`) filter or
modify. Never put sensitive data (passwords, tokens) in URLs
- they appear in browser history, server logs, and proxy
logs. Use HTTPS for all API URLs.

**Level 3 - How it works (mid-level engineer):**
The URL parser splits on structural characters: `://`
separates scheme from authority, `/` starts the path, `?`
starts the query, `#` starts the fragment. Each component
has its own character rules and encoding requirements.
The authority component is case-insensitive (domain names
are case-insensitive). The path and query are case-sensitive
on most servers. Fragment is never transmitted to the server.

**Level 4 - Why it was designed this way (senior/staff):**
The URL structure solves two problems simultaneously:
human readability (you can read `GET /users/42/orders` and
know what it does) and machine parseability (structured
delimiters make regex/parser implementation deterministic).
The design choice to put `?` between path and query enables
caching systems to use the full URL including query as a
cache key. The fragment's client-only nature enables SPA
routing without server round-trips. These are not accidents
- each design decision has specific consequences that the
web relies on.

**Level 5 - Mastery (distinguished engineer):**
URL structure has three critical security implications at
scale. First: URLs appear in `Referer` (sic) headers when
a user clicks a link - any sensitive data in URLs leaks to
third-party sites. This is the OWASP "Sensitive Information
in URL" vulnerability (OAuth tokens in redirect URLs, session
IDs in query parameters). Second: URL normalization attacks -
`/admin` vs `/Admin` vs `/admin/` vs `%61dmin` may all
resolve to the same resource but bypass case-sensitive
security checks. Third: Server-Side Request Forgery (SSRF)
exploits URL parsing inconsistencies between an application
and its URL validator to make the server fetch attacker-
controlled URLs. All three are in the OWASP Top 10 and
all three are rooted in URL structure.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│           URL Component Parsing Reference            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Full URL:                                           │
│  https://alice:pass@api.ex.com:443/v1/u?q=1#sec-2   │
│                                                      │
│  Component    │ Value        │ Notes                 │
│  ─────────────┼──────────────┼───────────────────── │
│  scheme       │ https        │ determines port 443   │
│  userinfo     │ alice:pass   │ DEPRECATED - avoid    │
│  host         │ api.ex.com   │ case-insensitive DNS  │
│  port         │ 443          │ omit if = scheme default│
│  path         │ /v1/u        │ case-sensitive, /sep  │
│  query        │ q=1          │ key=val, & separated  │
│  fragment     │ sec-2        │ NEVER sent to server  │
│                                                      │
│  Encoding rules:                                     │
│  path: encode space→%20, but keep / literal          │
│  query val: encode space→%20 or +, & → %26           │
│  fragment: encode space→%20                          │
└──────────────────────────────────────────────────────┘
```

```mermaid
flowchart LR
    U[URL String] --> S[Scheme]
    U --> A[Authority: host + port]
    U --> P[Path]
    U --> Q[Query]
    U --> F[Fragment]
    S -- sent --> SRV[Server]
    A -- sent --> SRV
    P -- sent --> SRV
    Q -- sent --> SRV
    F -- NOT sent --> CL[Client Only]
```

**URL resolution (relative URLs):**

```
Base URL: https://api.example.com/v1/users/42
Relative: ../orders
Resolved: https://api.example.com/v1/orders

Base URL: https://api.example.com/v1/users/42
Relative: /v2/users/42
Resolved: https://api.example.com/v2/users/42
(absolute path replaces entire path)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**How a URL travels through the network:**

```
Client builds URL:
  https://api.example.com/users/42?include=orders

1. DNS lookup: api.example.com → 93.184.216.34
2. TCP connect to 93.184.216.34:443
3. TLS handshake (scheme = https)
4. HTTP request sent:
   GET /users/42?include=orders HTTP/1.1
   Host: api.example.com
   (fragment is NOT included in request)
5. Server routes on path (/users/42)
   and reads query (?include=orders)
6. Response returned
7. Browser handles fragment if present (#section)
   AFTER rendering the response
```

**What CDN uses as cache key:**
`https://api.example.com/users/42?include=orders`
(full URL including query, excluding fragment)

**What gets logged (security risk if tokens in query):**

```
# Server access log - full URL including query params:
93.184.1.1 GET /users/42?token=MYSECRETTOKEN 200 85ms

# Bad practice: token in URL appears in:
# - Server access logs
# - Proxy logs
# - Browser history
# - Referer header when user navigates to another page
```

---

### 💻 Code Example

**Example 1 - BAD: Sensitive data in URL, bad encoding**

```python
# BAD: API key in URL query parameter - appears in logs
import requests

api_key = "sk-secret-1234"
# WRONG: key in URL → logged by server, proxy, CDN
response = requests.get(
    f"https://api.example.com/data?api_key={api_key}"
)

# BAD: manual URL construction without encoding
user_query = "C++ programming"
# WRONG: unencoded + and space - ambiguous parse
url = f"https://api.example.com/search?q={user_query}"
```

**Example 1 - GOOD: Token in header, proper URL encoding**

```python
# GOOD: API key in Authorization header, not URL
import requests
from urllib.parse import urlencode, quote

api_key = "sk-secret-1234"
# CORRECT: token in header - not in logs or proxied URL
response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {api_key}"}
)

# GOOD: proper URL encoding with urllib
user_query = "C++ programming"
params = {"q": user_query, "page": 2}
# urlencode handles encoding correctly
url = "https://api.example.com/search?" + urlencode(params)
# Result: ?q=C%2B%2B+programming&page=2
```

---

**Example 2 - URL parsing and component access**

```python
from urllib.parse import urlparse, urlencode, parse_qs

url = (
    "https://api.example.com:8080"
    "/v1/users/42/orders"
    "?status=active&page=2"
    "#results"
)

parsed = urlparse(url)
print(parsed.scheme)    # "https"
print(parsed.netloc)    # "api.example.com:8080"
print(parsed.hostname)  # "api.example.com"
print(parsed.port)      # 8080
print(parsed.path)      # "/v1/users/42/orders"
print(parsed.query)     # "status=active&page=2"
print(parsed.fragment)  # "results"

# Parse query string into dict
params = parse_qs(parsed.query)
print(params)  # {"status": ["active"], "page": ["2"]}

# Note: parse_qs returns lists for multi-value params
# e.g. ?tag=a&tag=b → {"tag": ["a", "b"]}
```

---

**Example 3 - SSRF prevention in URL validation**

```python
# OWASP A10: SSRF - attacker passes internal URL as input

import ipaddress
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"https", "http"}
# Block internal ranges to prevent SSRF
BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0",
    "169.254.169.254",  # AWS metadata service
    "metadata.google.internal"
}

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        # Scheme must be http or https
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False

        # Block empty host
        if not parsed.hostname:
            return False

        # Block known internal hostnames
        if parsed.hostname.lower() in BLOCKED_HOSTS:
            return False

        # Block internal IP ranges
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if (ip.is_private or ip.is_loopback
                    or ip.is_link_local):
                return False
        except ValueError:
            pass  # hostname, not IP - OK

        return True
    except Exception:
        return False

# Usage
user_url = request.json.get("webhook_url")
if not is_safe_url(user_url):
    return jsonify({"error": "Invalid URL"}), 400
```

---

### ⚖️ Comparison Table

| Concept | URI | URL | URN |
|:---|:---|:---|:---|
| **Full name** | Uniform Resource Identifier | Uniform Resource Locator | Uniform Resource Name |
| **Purpose** | Identifies a resource | Locates AND identifies | Names a resource (no location) |
| **Example** | `isbn:978-0-596-51774-8` | `https://example.com/book` | `urn:isbn:978-0-596-51774-8` |
| **Contains location?** | May or may not | Always | Never |
| **Used in HTTP?** | Request-URI in HTTP spec | href, src, API paths | Rare (namespaces) |

**URL vs Path vs Endpoint:**
- URL: the full string including scheme and host
- Path: just the `/v1/users/42` portion
- Endpoint: the combination of method + path that the server handles

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| URL and URI are the same | A URL is a type of URI. All URLs are URIs, but not all URIs are URLs. In practice, "URL" is used colloquially for both. |
| Fragment is part of the HTTP request | Fragment is never sent to the server - the browser resolves it locally after receiving the response |
| URLs are case-insensitive | Only the scheme and host are case-insensitive; path, query, and fragment are typically case-sensitive (server-dependent) |
| `+` in query strings means plus | `+` in form-encoded query strings means space (from HTML form submission); `%2B` is a literal `+`. Use `%20` for portability. |
| Putting tokens in URLs is equivalent to headers | URL tokens appear in server logs, proxy logs, browser history, and `Referer` headers. Header tokens do not. This is a critical security difference. |

---

### 🚨 Failure Modes & Diagnosis

**Sensitive data exposed in server logs via URL**

**Symptom:** OAuth tokens, API keys, or session IDs appear
in server access logs. Third-party services receive tokens
via `Referer` headers. Security audit flags credential exposure.

**Root Cause:** Application puts sensitive values in URL
query parameters instead of headers or POST body.

**Diagnostic Command / Tool:**

```bash
# Scan access logs for patterns that look like tokens in URLs
grep -E '\?(token|api_key|access_token|key)=' \
  /var/log/nginx/access.log | head -20

# Check if OAuth tokens appear in Referer headers
grep "Referer:.*access_token" \
  /var/log/nginx/access.log | wc -l
```

**Fix:** Move all sensitive values to HTTP headers
(`Authorization: Bearer ...`) or request body (POST).
Rotate any exposed tokens immediately.

---

**Double-encoding corruption**

**Symptom:** URL parameters with encoded characters are
corrupted. `%2F` becomes `%252F`. Path traversal attempts
(`../`) get double-encoded and pass security filters.

**Root Cause:** URL encoder is called twice on the same
value. First pass: `a/b` → `a%2Fb`. Second pass: `a%2Fb`
→ `a%252Fb`. Or: URL is decoded twice by two layers of
middleware, where the second decode interprets `%25` as
a literal `%`, then `2F` as `F` - potentially allowing
path traversal bypasses.

**Diagnostic Command / Tool:**

```python
# Detect double-encoding in URL parameters
from urllib.parse import unquote, unquote_plus

def check_double_encode(value):
    once = unquote(value)
    twice = unquote(once)
    if once != twice:
        print(f"WARNING: double-encoded: {value}")
        print(f"  Once decoded: {once}")
        print(f"  Twice decoded: {twice}")
```

**Fix:** Encode exactly once before sending. Decode exactly
once after receiving. Never encode an already-encoded string.

---

**SSRF via URL parsing inconsistency**

**Symptom:** Internal service URLs are fetched by the
application. AWS metadata endpoint (`169.254.169.254`)
is accessed. Internal admin API returns data to external users.

**Root Cause:** Application validates the URL with one parser
but fetches with another. The two parsers interpret edge
cases differently, allowing an attacker to pass validation
but route to an internal IP.

**Diagnostic Command / Tool:**

```bash
# Test if metadata endpoint is accessible from application
# (run from application server)
curl -s http://169.254.169.254/latest/meta-data/
# If this returns data, SSRF risk is confirmed

# Check for SSRF in web app with safe targets first
# Use ssrf-sheriff or similar tool in controlled environments
```

**Fix:** Use an explicit allowlist of permitted domains,
not a blocklist. Resolve the hostname to IP before checking
and validate the resolved IP is not in a private range.
See code example 3 above for implementation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HTTP Protocol` - the protocol that URLs are used in
- `HTTP Request Structure` - how the URL appears in the
  request line

**Builds On This (learn these next):**
- `Query Parameters and Path Parameters` - the two ways
  to pass data via URLs
- `API Endpoint Design Basics` - how to design clean,
  consistent URL paths for APIs
- `API Versioning Strategies` - how versioning appears in
  the URL path or as a query parameter

**Alternatives / Comparisons:**
- `gRPC and Protocol Buffers` - uses service + method names
  in the HTTP/2 path; the URL structure is protocol-defined
  not user-designed
- `WebSocket Basics` - begins as an HTTP upgrade request
  with a URL; `ws://` and `wss://` are URL schemes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Structured address for any internet       │
│              │ resource: scheme+authority+path+query+    │
│              │ fragment                                  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Universal addressing for resources across │
│ SOLVES       │ any server, protocol, or network          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fragment is never sent to server - it is  │
│              │ client-only; this enables SPA routing     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always - every HTTP operation uses URLs   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put sensitive data in URL (tokens,  │
│              │ passwords, PII) - appears in logs         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Token in query parameter: ?token=xxx      │
│              │ Unencoded special chars in query values   │
│              │ Manual URL string concatenation           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ URL readability vs security: descriptive  │
│              │ URLs expose resource structure (trade-off │
│              │ with enumeration attack surface)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fragment never reaches the server.       │
│              │ Tokens don't belong in URLs."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Query Parameters → API Endpoint Design →  │
│              │ SSRF and API Security                     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. URL = scheme + authority + path + query + fragment.
   Fragment is never sent to the server.
2. Never put secrets (tokens, passwords, API keys) in URLs.
   They appear in server logs, proxy logs, and Referer headers.
3. Always use URL encoding for user-controlled values in
   URLs. Use a library - never build URLs by manual string
   concatenation with user input.

**Interview one-liner:**
"A URL has five components: scheme (how), authority (where),
path (what resource), query (filtering parameters), and
fragment (client-side section reference, never sent to
server). The key security rule is that secrets must never
go in URLs - they appear in server logs, proxy logs, and
Referer headers, which are almost always unencrypted even
in HTTPS environments."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Structured addressing formats encode both identity and
access method in a single portable string. The URL's
design - human-readable path hierarchy with protocol-encoded
scheme - enables the same string to be meaningful to both
humans (who read it) and machines (that parse and route on
it). This dual-legibility is why URLs became the universal
resource addressing mechanism, while binary addressing
schemes (FTP data connections, raw IP + port) remained
protocol-specific. Design your systems' resource identifiers
with both humans and machines in mind.

**Where else this pattern appears:**
- AWS ARN (Amazon Resource Name): structured identifier
  encoding service, region, account, and resource type
  (`arn:aws:s3:::my-bucket`) - similar hierarchical address
  that machines can parse and route on
- Kafka topics: cluster + topic + partition forms a
  hierarchical address for message streams
- JNDI/LDAP URLs: `ldap://host/DN` follows the same
  scheme-authority-path structure

**Industry applications:**
- Google's URL normalization for indexing: Googlebot
  normalizes URLs (remove default ports, lowercase scheme
  and host, resolve relative paths) before storing - same
  URL accessed in different forms is treated as one resource
- CDN cache keys: CDN vendors let you define the cache key
  as a subset of the URL (exclude certain query params
  that do not affect the response content, like tracking
  parameters `?utm_source=...`)

---

### 💡 The Surprising Truth

The `Referer` (sic) header - which leaks URL tokens to
third-party sites - was misspelled in the original HTTP
spec. The correct English spelling is "referrer" but the
original RFC author made a typo that was caught too late
to fix. Today, every HTTP implementation in the world has
a misspelled "Referer" header as part of the protocol
standard. The misspelling is permanent - changing it would
break every existing implementation. This is why standards
matter: once a typo is standardized, it lives forever in
billions of lines of code.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Draw the five components of a URL and explain
   what each part tells the browser, server, and CDN - and
   which part is never transmitted to the server.
2. **DEBUG** Given a server log showing `?token=abc123` in
   the access log, explain what immediate security action
   is required and how to prevent it from happening again.
3. **DECIDE** For a search API, decide whether to encode
   user input as a path segment (`/search/C++ programming`)
   or a query parameter (`/search?q=C%2B%2B+programming`)
   and explain the trade-offs of each.
4. **BUILD** Write a URL-safe function that takes a base URL
   and a dict of query parameters, handles encoding of
   special characters correctly, and does not double-encode
   if called on an already-built URL.
5. **EXTEND** Explain how SSRF exploits URL parsing
   inconsistencies, give an example of a bypass technique,
   and describe the defense.

---

### 🧠 Think About This Before We Continue

**Q1.** Your SPA uses hash-based routing (`/app#/dashboard`,
`/app#/settings`). A user copies the URL from their browser
and shares it with a colleague. The colleague opens it.
What does the server receive, and how does the SPA know
which page to render? What is the security implication of
sensitive data appearing in the fragment (does it appear
in server logs? In Referer headers when the user clicks
an external link from the `/app#/dashboard` page)?

*Hint: The fragment is never sent to the server and never
appears in the Referer header when navigating away. But
it IS visible in browser history and can be read by
JavaScript on the same page.*

**Q2.** CDN vendors allow "cache key normalization" - you
can tell the CDN to ignore certain query parameters when
building the cache key. For example, ignore `?utm_source=...`
and `?campaign_id=...`. What is the risk of incorrectly
ignoring a query parameter that DOES affect the response?
Give a concrete example.

*Hint: Think about `?page=2&status=active` - ignoring
`page` would cache page 1 as the result for page 2 requests.*

**Q3.** Build this: implement a URL builder function that
takes a base URL, path segments (as a list), and query
parameters (as a dict), constructs the correct URL with
proper encoding, and raises an error if the base URL
contains a fragment (since fragments should only be added
client-side, not constructed in server code).

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between a URI and a URL?
Is `mailto:user@example.com` a URL?**

*Why they ask:* Tests precision with foundational terminology -
signals whether the candidate learns from specs or from
vague tutorials.

*Strong answer includes:*
- URI (Uniform Resource Identifier): identifies a resource
  (may or may not tell you how to get it)
- URL (Uniform Resource Locator): identifies AND tells you
  how to access it (includes scheme/location)
- URN (Uniform Resource Name): identifies without location
- `mailto:user@example.com` is a URI and a URL (it identifies
  a resource and describes how to access it: via the mail
  protocol), but it does not locate a document
- Practical significance: in HTTP specs, "URI" is used
  precisely; in common usage "URL" is used for both

**Q2: Why should you never put authentication tokens or
API keys in URL query parameters?**

*Why they ask:* Tests security awareness around a very
common mistake in API client code.

*Strong answer includes:*
- URLs appear in server access logs (even on HTTPS servers,
  the path and query are logged in plaintext)
- URLs appear in proxy logs (corporate proxies log URLs)
- URLs appear in browser history
- URLs leak via `Referer` header when a user navigates
  from a page that has the token in the URL to an external
  page or resource
- HTTPS encrypts in transit, but the server logs the URL
  after decryption
- Fix: put tokens in `Authorization` header (not logged
  by default, not in Referer, not in browser history)

**Q3: What is SSRF and how is it related to URL parsing?**

*Why they ask:* SSRF is in the OWASP Top 10 and is
directly exploited through URL manipulation - tests security
depth beyond basic concepts.

*Strong answer includes:*
- SSRF (Server-Side Request Forgery): an attacker causes
  the server to make HTTP requests to attacker-controlled URLs
- Exploits URL parsing inconsistencies: an application
  validates a URL with one parser but fetches with another;
  the parsers handle edge cases differently (URL fragments,
  percent-encoding, IPv6 brackets, etc.)
- Classic example: AWS metadata endpoint at
  `169.254.169.254` - if an attacker can make the server
  fetch this URL, they get the instance's IAM credentials
- Prevention: resolve hostname to IP before validation;
  check resolved IP against blocklist of private ranges;
  prefer allowlist (only permitted domains) over blocklist
