---
id: ATZ-044
title: "Forced Browsing and Missing Function Level Access"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-025, ATZ-042, ATZ-043
used_by: ATZ-050, ATZ-054
related: ATZ-041, ATZ-042, ATZ-043
tags:
  - security
  - authorization
  - forced-browsing
  - function-level-access
  - owasp
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 44
permalink: /technical-mastery/authorization/forced-browsing-and-missing-function-level-access/
---

⚡ **TL;DR** - Forced browsing: an attacker directly navigates to
a URL that the application does not link to from the normal UI
(admin pages, config pages, old backup files). Missing function-
level access control: the server does not check whether the user
has the right to invoke that function - it only hides the link.
Both have the same root cause: access control enforced by the UI
(don't show the link = secure), not by the server. Every endpoint,
regardless of how it is discovered, must enforce authorization
server-side.

---

### 📊 Entry Metadata

| #044 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-025 Testing, ATZ-042 Broken Access, ATZ-043 IDOR | |
| **Used by:** | ATZ-050, ATZ-054 | |
| **Related:** | ATZ-041 PrivEsc, ATZ-042 Broken Access, ATZ-043 IDOR | |

---

### 📘 Textbook Definition

Forced browsing (also called direct browsing or insecure
navigation) is an attack where an adversary manually navigates
to an application resource by crafting or guessing URLs,
bypassing the intended navigation flow. Missing function-level
access control (OWASP A01 subcategory) is the server-side
failure: the application assumes that if a link is hidden
from the UI, the endpoint is inaccessible. Commonly vulnerable
endpoints: admin panels at `/admin/`, debug endpoints, API
routes exposed but undocumented, backup files (`.bak`, `.sql`),
and old version paths (`/v1/endpoint` with looser security
than `/v2/endpoint`).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Forced Browsing Attack Surface                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  COMMON TARGETS:                                       │
│  /admin/           <- admin panel, role check missing  │
│  /actuator/        <- Spring Boot, full system info    │
│  /api/internal/    <- internal API exposed publicly    │
│  /api/v1/users     <- old version, weaker auth         │
│  /backup.sql       <- database backup, no auth         │
│  /.env             <- environment variables w/ secrets │
│  /config.php.bak   <- config backup file               │
│  /swagger-ui.html  <- API docs, info disclosure        │
│                                                        │
│  DISCOVERY METHODS (attacker):                         │
│  - Directory brute force (dirbuster, gobuster)         │
│  - JavaScript source analysis (hidden API calls)       │
│  - Google dorking (site:example.com inurl:admin)       │
│  - API documentation review                            │
│  - HTTP response headers (X-Powered-By, etc.)          │
│                                                        │
│  PREVENTION:                                           │
│  - Every route: explicit auth check at the handler     │
│  - Deny-by-default framework configuration             │
│  - Never rely on URL obscurity for access control      │
│  - Remove backup files, debug endpoints from prod      │
│  - Security audit: map ALL endpoints vs access rules   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Securing all endpoints with deny-by-default**

```java
// Spring Security: deny all, explicitly allow specific paths
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(
            HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
            // Public endpoints: explicitly listed
            .requestMatchers("/login", "/register",
                "/api/health", "/static/**").permitAll()
            // Admin endpoints: ADMIN role required
            .requestMatchers("/admin/**",
                "/api/admin/**").hasRole("ADMIN")
            // Actuator: only from localhost or admin
            .requestMatchers("/actuator/**")
                .hasIpAddress("127.0.0.1")
            // ALL other requests: must be authenticated
            // This is DENY-BY-DEFAULT
            .anyRequest().authenticated()
        );
        return http.build();
    }
}
// If a new endpoint is added and not explicitly permitted:
// default is "authenticated" - not publicly accessible
// If it's added to permitAll() without reviewing: problem
// Regular audit: list all routes + their auth requirement
```

---

*Authorization category: ATZ | Entry: ATZ-044 | v5.0*