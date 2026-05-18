---
id: ATH-011
title: "HTTP Basic Authentication"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-006, ATH-010
used_by: ATH-022, ATH-031
related: ATH-010, ATH-031
tags:
  - security
  - authentication
  - http
  - basic-auth
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/authentication/http-basic-authentication/
---

⚡ **TL;DR** - HTTP Basic Authentication transmits a Base64-encoded
`username:password` string in the Authorization header on every
request. Base64 is encoding, not encryption - the credentials are
effectively cleartext unless HTTPS is used. Basic Auth is the
simplest possible auth scheme: zero state, zero session management,
universal browser support. It is appropriate for internal APIs
over HTTPS but never for user-facing web applications.

---

### 📊 Entry Metadata

| #011 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-006, ATH-010 | |
| **Used by:** | ATH-022, ATH-031 | |
| **Related:** | ATH-010 Token Auth, ATH-031 Bearer Token | |

---

### 📘 Textbook Definition

HTTP Basic Authentication (RFC 7617) is a challenge-response
authentication scheme where the client sends credentials as
a Base64-encoded `username:password` string in the
`Authorization: Basic <credentials>` request header.
The server challenges an unauthenticated request with
`WWW-Authenticate: Basic realm="..."`. Credentials are
transmitted on every request; there is no session or token
issued. Security is entirely dependent on transport security
(TLS/HTTPS), since Base64 encoding provides no confidentiality.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Send your username and password in every request, encoded
but not encrypted.

**The wire format:**

```
Authorization: Basic YWxpY2U6cGFzc3dvcmQxMjM=
                           ↑
                  base64("alice:password123")

Anyone who intercepts this header gets the credentials.
HTTPS is not optional - it is the only security mechanism.
```

**One analogy:**
> Showing your ID at every door of the building, rather
> than getting a visitor badge at the front desk. Every
> door check requires presenting the full credential.
> If the building has glass walls (HTTP), everyone can
> see your ID. If the building is sealed (HTTPS), only
> the door guard sees it.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│             HTTP Basic Auth Flow                       │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. CLIENT requests protected resource (no credentials)│
│     GET /api/data HTTP/1.1                             │
│                                                        │
│  2. SERVER challenges (optional; clients usually       │
│     pre-emptively include credentials):                │
│     HTTP/1.1 401 Unauthorized                          │
│     WWW-Authenticate: Basic realm="API"                │
│                                                        │
│  3. CLIENT encodes credentials:                        │
│     base64("alice:s3cr3t") = "YWxpY2U6czNjcjN0"       │
│     GET /api/data HTTP/1.1                             │
│     Authorization: Basic YWxpY2U6czNjcjN0             │
│                                                        │
│  4. SERVER decodes, verifies credentials               │
│     → return 200 OK with data                          │
│                                                        │
│  This happens on EVERY request.                        │
│  No session. No token. No state.                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Boot Basic Auth endpoint**

```java
@Configuration
@EnableWebSecurity
public class BasicAuthConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http)
            throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .anyRequest().authenticated()
            )
            .httpBasic(basic -> basic
                .realmName("Internal API")
            )
            // Stateless: no server session
            .sessionManagement(s -> s
                .sessionCreationPolicy(STATELESS)
            );
        return http.build();
    }

    @Bean
    public UserDetailsService users() {
        // In production: load from database/secrets manager
        // Never hardcode credentials in code
        UserDetails apiUser = User.builder()
            .username("service-account")
            .password(passwordEncoder().encode(
                System.getenv("API_PASSWORD")))
            .roles("API_CLIENT")
            .build();
        return new InMemoryUserDetailsManager(apiUser);
    }
}
```

**Example - BAD vs GOOD: Basic Auth over HTTP**

```bash
# BAD: Basic Auth over plain HTTP
# The Authorization header is visible to any network observer
curl http://api.internal.com/data \
  -H "Authorization: Basic YWxpY2U6czNjcjN0"
# Anyone with network access reads: alice:s3cr3t

# GOOD: Basic Auth only over HTTPS
curl https://api.internal.com/data \
  -u service-account:$(cat /run/secrets/api_password)
# TLS encrypts the entire request including headers
# Credentials are not visible to network observers
# Use environment vars or secret files, not inline strings
```

**Example - FAILURE: credentials logged by middleware**

```
Vulnerability:
  Server-side request logging (nginx, access.log) logs
  full request headers including Authorization.

  Log entry:
  "GET /api/orders" Authorization: Basic YWxpY2U6czNjcjN0
  ↓
  base64 decode: alice:s3cr3t

  If logs are accessible to log aggregation tools,
  SIEMs, or developers without security clearance,
  credentials are exposed in plaintext.

Fix:
  1. Configure log middleware to redact Authorization headers
  2. In nginx: proxy_set_header Authorization "";
     (strip before passing to upstream - only if upstream
      does not need it)
  3. In application logging: never log request headers
     that may contain credentials
     @ExchangeFilterFunction or logging interceptor should
     redact Authorization header before printing
```

---

### 📏 When to Use HTTP Basic Auth

| Appropriate | Not appropriate |
|---|---|
| Internal service-to-service over HTTPS | User-facing web applications |
| Simple admin tools with limited access | Public APIs (API keys are better) |
| Development/testing environments | Any HTTP (non-TLS) endpoint |
| Legacy system integration (no alternatives) | When session management is needed |

---

*Authentication category: ATH | Entry: ATH-011 | v5.0*