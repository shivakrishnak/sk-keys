---
layout: default
title: "CSRF"
parent: "HTTP & APIs"
nav_order: 242
permalink: /http-apis/csrf/
number: "0242"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, Browser Security Model, Cookies, Session Management
used_by: Web Application Security, API Security
related: XSS, CORS, SameSite Cookie, API Authentication, JWT
tags:
  - security
  - csrf
  - browser
  - cookies
  - owasp
  - intermediate
---

# 242 — CSRF (Cross-Site Request Forgery)

⚡ TL;DR — CSRF is an attack where a malicious website tricks a victim's browser into making an authenticated request to a target site using the victim's existing cookies; prevented by synchronizer CSRF tokens (a secret per-session token that a cross-site form can't know), `SameSite=Strict` cookies, or stateless JWT-in-header authentication (which browsers don't auto-send cross-site).

| #242 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, Browser Security Model, Cookies, Session Management | |
| **Used by:** | Web Application Security, API Security | |
| **Related:** | XSS, CORS, SameSite Cookie, API Authentication, JWT | |

---

### 🔥 The Problem This Solves (The Threat)

**THE ATTACK:**
User is logged into their bank at `bank.com`. A session cookie `session=abc123` is
stored in the browser (automatically sent with every request to bank.com).
User visits `evil.com`, which contains:

```html
<form action="https://bank.com/transfer" method="POST" id="f">
  <input name="to" value="attacker-account" />
  <input name="amount" value="10000" />
</form>
<script>
  document.getElementById("f").submit();
</script>
```

The browser submits this form to bank.com, automatically including the session cookie.
bank.com sees: authenticated request (valid session) → processes transfer.
User's money is transferred without their knowledge or consent.

**WHY IT WORKS:**
Browsers automatically include cookies with requests to a domain, regardless of which
page triggered the request. A bank.com session cookie is sent with ANY request to bank.com —
whether initiated by bank.com's own JavaScript or by evil.com's hidden form.

---

### 📘 Textbook Definition

**CSRF (Cross-Site Request Forgery)**, also called XSRF or "sea surf," is an attack
(OWASP Top 10 #1 before 2017) where a malicious website, email, or page causes a
victim's browser to make an unintended authenticated request to a target web application
in which the victim has an active session. The attack exploits the browser's automatic
inclusion of cookies with cross-origin requests — the target server sees a valid session
credential and processes the request as if the user intended it. CSRF exploits trust
the server has in the user's browser. Prevention strategies: **Synchronizer Token Pattern**
(a secret CSRF token verified server-side), **Double Submit Cookie** (CSRF token in
both cookie and form field), **SameSite cookie attribute** (`SameSite=Strict` prevents
cross-site cookie sending), and **Custom request headers** (cross-site forms can't set
custom headers — `Authorization: Bearer` header causes CORS preflight which blocks the attack).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CSRF exploits the fact that browsers automatically send cookies with cross-origin requests
— letting an attacker's site trigger authenticated actions on your behalf without your knowledge.

**One analogy:**

> CSRF is like someone slipping a forged check into a stack of papers you're signing.
> You're an authorized signer (authenticated session). Someone puts a check made out
> to them among real documents. You don't read each one before signing (browser
> auto-sends cookies). The bank (server) sees your signature (valid session) and
> processes the check.

**One insight:**
CSRF is the opposite of XSS in terms of trust: XSS exploits the user's trust in the
site (injected code gets site's trust). CSRF exploits the SITE's trust in the user's
browser. No JavaScript injection needed — a hidden form is enough because cookies
are automatically sent.

---

### 🔩 First Principles Explanation

**WHY COOKIES ARE THE VULNERABILITY:**

```
Browser rule: "Send all cookies for domain D with every request to D"
This rule has no exception for "requests initiated by another origin"

Same-Origin Policy blocks: cross-origin JavaScript from READING the response
Same-Origin Policy does NOT block: cross-origin forms from SUBMITTING to the domain

So:
evil.com can: submit a form to bank.com (the request goes through + cookies sent)
evil.com CANNOT: read bank.com's response (blocked by SOP)
BUT: in CSRF, we don't need to read the response — we just need the ACTION to execute

For state-changing actions (transfer money, change password, delete account):
→ CSRF is deadly because the action doesn't require reading the response
```

**CSRF PREVENTION STRATEGIES:**

```
STRATEGY 1 — SYNCHRONIZER TOKEN PATTERN (classic)

Server: on session creation, generate random CSRF token: csrfToken = randomBytes(32)
  Store in session: session['csrf_token'] = csrfToken

HTML form:
  <form method="POST" action="/transfer">
    <input type="hidden" name="csrf_token" value="${session.csrf_token}">
    <input name="to" value="">
  </form>

Server validates: request.body.csrf_token == session.csrf_token? → allow
evil.com problem: evil.com cannot know the victim's csrf_token (it's in server-side session)
Reads are blocked by SOP. So evil.com can't forge the hidden field with the right value.
→ Cross-origin form submission missing csrf_token → rejected ✓

STRATEGY 2 — SAMESITE COOKIE ATTRIBUTE (modern, simplest)

session cookie: Set-Cookie: session=abc123; SameSite=Strict; HttpOnly; Secure

SameSite=Strict: browser NEVER sends this cookie on cross-site requests
  → evil.com form submission to bank.com → session cookie NOT sent
  → bank.com: no session → unauthenticated request → rejected ✓

SameSite=Lax (default in modern browsers):
  → blocks cross-site POST forms
  → allows cross-site GET navigations (clicking a link is OK)

SameSite=None: sends cookie cross-site (requires Secure flag)
  → Only for intentional cross-site scenarios (embedded iframes, OAuth redirects)

STRATEGY 3 — CUSTOM REQUEST HEADERS (for AJAX/SPAs)

CSRF-Token: <token> in AJAX request header
  Cross-site forms CAN'T set custom headers (browser restriction)
  Cross-site Ajax with custom headers triggers CORS preflight
  Preflight requires server to explicitly allow origin → server can reject untrusted origins

AKA: if your API uses Authorization: Bearer <JWT> in header:
  Browser won't auto-send this for cross-site requests
  A CSRF attacker's form has no way to add this header
  → No CSRF risk for header-based authentication (JWTs in headers are CSRF-safe)

STRATEGY 4 — DOUBLE SUBMIT COOKIE

Set CSRF token as a cookie (not HttpOnly): Set-Cookie: csrf_token=random123; Secure; SameSite=None
JavaScript reads it and includes in request header or body field
Server verifies: cookie value == request body/header value

evil.com problem: SOP blocks evil.com from reading bank.com cookies
→ evil.com can't read the token to forge the double-submit
→ Works for stateless APIs where session doesn't store CSRF token
```

---

### 🧪 Thought Experiment

**CSRF vs XSS — What Each Requires:**

```
CSRF attack:
  Requires: victim is logged into target site in the same browser
  Requires: target performs state changes via GET or cookie-auth forms
  Does NOT require: any vulnerability in the target site's code
  Does NOT require: JavaScript (hidden form with auto-submit works)
  Can attacker read responses? NO (SOP blocks cross-origin reads)
  Defense: SameSite=Strict cookies OR CSRF tokens OR JWT-in-header

XSS attack:
  Requires: injection vulnerability in the target site
  Attacker CAN: read responses, steal cookies, make API calls
  Defense: output encoding, CSP, HttpOnly cookies

WHY JWT-IN-HEADER BEATS CSRF:
  API: Bearer token in Authorization header
  Browser doesn't auto-include headers — the JavaScript must explicitly set it
  evil.com cannot set Authorization header on a cross-site POST (not a browser capability)
  → No CSRF: the attacker's form has no way to inject the Bearer token

  CONTRAST with cookie auth:
  Browser auto-sends cookies for the domain → CSRF possible
  Bearer token in header → CSRF not applicable
```

---

### 🧠 Mental Model / Analogy

> CSRF is like a remote button that unknowingly triggers your home alarm.
> You gave a trusted friend a remote (your browser session cookie). Your security
> company (the server) trusts anyone holding that remote. If your friend visits
> a malicious neighbor who displays a fake "Emergency" button, and your friend
> clicks it — it uses your friend's remote to trigger your alarm. Your friend
> didn't intend to do it. The alarm company can't tell the difference.
>
> Defense: require a second secret that only YOUR home panel knows (CSRF token)
> to confirm any remote command. Or: make the remote only work when physically
> present in the house (SameSite=Strict: only works from same origin).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CSRF tricks your browser into sending a request to another website using your login
session, without you knowing. The attacked website sees your valid login cookie and
processes the request as if you authorized it.

**Level 2 — How to fix it (junior developer):**
Spring Security: CSRF protection is enabled by default for form-based sessions.
For REST APIs using JWTs in headers: CSRF is not applicable (disable CSRF protection in
Spring Security for stateless JWT APIs — it's unnecessary overhead). Add `SameSite=Strict`
to session cookies. Don't put state-changing operations in GET requests.

**Level 3 — How it works (mid-level engineer):**
Spring Security's CSRF: uses the synchronizer token pattern by default. Token is in
a cookie (readable by JS) AND must be sent as a request header/form field. For SPAs:
Spring provides a `XSRF-TOKEN` cookie that Angular/Axios can read and automatically
set in request headers. For REST APIs with header-based auth (Bearer tokens): disable
CSRF entirely — `http.csrf(csrf -> csrf.disable())` — because header-based auth
is inherently CSRF-safe. State-changing via GET: never (CSRF doesn't apply to GET
with SameSite but it's bad REST practice).

**Level 4 — Why it was designed this way (senior/staff):**
CSRF is a browser architecture vulnerability, not an application vulnerability.
The browser's fundamental design — automatically sending cookies with requests — pre-dates
web security thinking. The SameSite attribute (Chrome default Lax since 2020) significantly
reduced CSRF risk for new sessions. Old sessions without SameSite remain vulnerable.
The shift to SPAs with JWT in headers effectively eliminated CSRF for modern API-first
architectures — this is one of the unintended security benefits of the JWT/header pattern.
The CSRF token is a proof-of-origin mechanism: only code running in the context of
the legitimate page can read the CSRF token (via session or readable cookie), and
only that code can include it in the request. This works because SOP allows cross-site
form submission but blocks cross-site reads.

---

### ⚙️ How It Works (Mechanism)

```
SYNCHRONIZER TOKEN FLOW:

USER VISITS bank.com/dashboard:
  Server: session['csrf_token'] = "abc123xyz789..."
  Response HTML includes:
  <form method="POST" action="/transfer">
    <input type="hidden" name="_csrf" value="abc123xyz789...">
    ...
  </form>
  + Cookie: Set-Cookie: session=def456; HttpOnly; SameSite=Strict

USER SUBMITS TRANSFER:
  POST /transfer
  Cookie: session=def456  (auto-sent)
  Body: to=friend&amount=100&_csrf=abc123xyz789...

  Server: validate session → retrieve session['csrf_token'] = "abc123xyz789..."
  Compare: body._csrf == session['csrf_token']? ✓ → process request

EVIL.COM ATTACK ATTEMPT:
  POST https://bank.com/transfer
  Cookie: session=def456  (auto-sent! browser includes cookies for bank.com)
  Body: to=attacker&amount=10000&_csrf=???

  evil.com CANNOT know the value of "abc123xyz789..."
  It's stored in bank.com's server-side session
  evil.com can't read bank.com's session or cookies (SOP blocks cross-origin reads)

  Server: _csrf missing or wrong → 403 Forbidden ✓
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Modern SPA architecture:
  Frontend: React SPA at app.company.com
  API: REST API with JWT Bearer tokens at api.company.com
  Auth: JWT in Authorization header

CSRF risk assessment:
  Request: fetch('/api/transfer', {
    method: 'POST',
    headers: { Authorization: 'Bearer eyJ...' },
    body: JSON.stringify({ to, amount })
  })

  CSRF risk: NONE
  Reason: Authorization header is not auto-sent by browser for cross-site requests
  evil.com cannot forge this header on behalf of the victim
  Spring Security: csrf.disable() for this API

Traditional server-rendered app:
  Session cookie authentication → CSRF risk exists → use CSRF tokens or SameSite=Strict
```

---

### 💻 Code Example

```java
// Spring Security — CSRF configuration
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // For cookie-based sessions: CSRF protection REQUIRED
    @Bean
    public SecurityFilterChain sessionBasedSecurity(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf
                // Use cookie-based CSRF token (for SPAs: JS can read, set in header)
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                // Cookie: XSRF-TOKEN (readable by JS)
                // Angular HttpClient automatically sends X-XSRF-TOKEN header
                // Axios: axios.defaults.xsrfCookieName = 'XSRF-TOKEN'
            );
        return http.build();
    }

    // For JWT Bearer token APIs: CSRF is NOT applicable — disable it
    @Bean
    public SecurityFilterChain jwtApiSecurity(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())  // Safe: no cookie-based sessions
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

```java
// Setting SameSite=Strict on session cookie
// application.properties:
// server.servlet.session.cookie.same-site=strict
// server.servlet.session.cookie.http-only=true
// server.servlet.session.cookie.secure=true

// Or programmatically (for Spring Boot < 2.6):
@Bean
public WebServerFactoryCustomizer<TomcatServletWebServerFactory> cookieConfig() {
    return factory -> factory.addContextCustomizers(context -> {
        Rfc6265CookieProcessor proc = new Rfc6265CookieProcessor();
        proc.setSameSiteCookies(SameSiteCookies.STRICT.getValue());
        context.setCookieProcessor(proc);
    });
}
```

---

### ⚖️ Comparison Table

| Auth Mechanism                       | CSRF Risk | Reason                                                         |
| ------------------------------------ | --------- | -------------------------------------------------------------- |
| **Session Cookie (no SameSite)**     | High      | Browser auto-sends cookies cross-site                          |
| **Session Cookie (SameSite=Strict)** | None      | Browser blocks cross-site cookie sending                       |
| **JWT in Authorization Header**      | None      | Browser doesn't auto-send headers cross-site                   |
| **JWT in Cookie (no SameSite)**      | High      | Cookie auto-sent, JWT in cookie treated same as session cookie |
| **Basic Auth**                       | None      | Browser doesn't auto-send in API requests                      |

---

### ⚠️ Common Misconceptions

| Misconception                    | Reality                                                                                                                                                                                |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CSRF requires JavaScript or XSS  | A simple HTML form with auto-submit (`onload`) performs CSRF — no script injection needed                                                                                              |
| CSRF and XSS are the same attack | Different attacks: XSS exploits user trust in site (injects code that runs as the site). CSRF exploits site trust in user's browser (sends authenticated requests without user intent) |
| HTTPS prevents CSRF              | HTTPS encrypts the channel but doesn't prevent auto-cookie inclusion. CSRF works on HTTPS sites                                                                                        |
| REST APIs are safe from CSRF     | REST APIs using cookie sessions ARE vulnerable. REST APIs using Bearer tokens in headers are NOT vulnerable                                                                            |

---

### 🚨 Failure Modes & Diagnosis

**CSRF Token Misconfiguration — Double-Submit Without SOP Enforcement**

Symptom:
Security test: an attacker sets their own cookie value for XSRF-TOKEN and sends the
same value in the header → request accepted. Double-submit cookie pattern bypassed.

Root Cause:
Double-submit cookie with same subdomain sharing. Subdomain `evil.company.com` can set
cookies for `.company.com`, allowing the attacker to override the CSRF cookie.

Diagnostic:

```
# Test for subdomain cookie injection:
# 1. Set XSRF-TOKEN=attacker123 via attacker-controlled subdomain
# 2. Include XSRF-TOKEN: attacker123 in request header
# 3. If accepted → vulnerable to subdomain CSRF bypass

# Fix: use server-side synchronizer token (not double-submit if you have subdomains)
# Or: compare cookie origin domain strictly (not wildcard subdomain match)
# Spring Security default (CsrfTokenRepository.htpOnly) stores token server-side → safe
```

---

### 🔗 Related Keywords

- `XSS` — different attack: injects code into the site vs CSRF which forges requests
- `SameSite Cookie` — the cookie attribute that largely eliminates CSRF risk
- `CORS` — CORS preflight provides indirect CSRF protection for AJAX cross-site requests
- `JWT` — using JWT in Authorization header naturally eliminates CSRF for APIs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Tricking browser into sending authed     │
│              │ request using victim's cookies           │
├──────────────┼───────────────────────────────────────────┤
│ REQUIRES     │ Victim logged into target site;          │
│              │ target uses cookie-based auth            │
├──────────────┼───────────────────────────────────────────┤
│ DEFEND WITH  │ SameSite=Strict cookie (best + simplest) │
│              │ OR CSRF token (synchronizer pattern)     │
│              │ OR JWT in Authorization header (APIs)    │
├──────────────┼───────────────────────────────────────────┤
│ JWT APIS     │ No CSRF risk if using Bearer token in    │
│              │ header (disable Spring CSRF for APIs)   │
├──────────────┼───────────────────────────────────────────┤
│ CANNOT READ  │ Attacker can forge requests but can't   │
│ RESPONSES    │ read response (SOP still applies)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Browser auto-sends cookies; attacker    │
│              │ exploits that for unintended actions"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ XSS → SameSite Cookie → CORS → JWT      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A legacy application uses server-side sessions with session cookies (no SameSite, no CSRF tokens). You cannot change the authentication system in this sprint. You have one week to significantly reduce CSRF risk using only changes deployable at the web server / load balancer / CDN level, without changing application code. What are your options, their tradeoffs, and their effectiveness? Then prioritize what an application code change in sprint 2 would add.
