---
id: ATH-034
title: "Session Fixation Attack"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-008, ATH-009
used_by: ATH-044, ATH-046
related: ATH-008, ATH-015, ATH-044
tags:
  - security
  - authentication
  - session-fixation
  - attack
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/authentication/session-fixation-attack/
---

⚡ **TL;DR** - Session fixation: the attacker sets the victim's
session ID before login, then the server promotes that same ID
to an authenticated session. When the victim logs in, the attacker
already knows the session ID and is effectively authenticated too.
The fix is one line: regenerate the session ID on login. Every web
framework supports this. Missing it in 2024 is inexcusable.

---

### 📊 Entry Metadata

| #034 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-008 Session Auth, ATH-009 Cookie Mechanics | |
| **Used by:** | ATH-044, ATH-046 | |
| **Related:** | ATH-008 Session Auth, ATH-015 Logout, ATH-044 Account Takeover | |

---

### 📘 Textbook Definition

Session fixation is an attack where the attacker obtains a valid
pre-authentication session ID (unauthenticated) and tricks the
victim into using that session ID when logging in. If the
server does not regenerate the session ID at login, the
attacker's pre-known session ID becomes authenticated after the
victim logs in. The attacker can then use the session ID they
already possess to act as the authenticated user. Session
fixation is distinct from session hijacking: in hijacking, the
attacker steals an existing authenticated session; in fixation,
the attacker plants the session ID before authentication.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│            Session Fixation Attack                     │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Attacker visits login page                         │
│     Server issues pre-auth session: SID=FIXED123       │
│  2. Attacker sends victim a URL:                       │
│     https://bank.com/login?SID=FIXED123                │
│     (or via meta-refresh, subdomain cookie)            │
│  3. Victim logs in with SID=FIXED123 in their browser  │
│  4. Server: authenticates victim, but...               │
│     VULNERABLE: keeps same session SID=FIXED123        │
│     SAFE: regenerates session -> SID=NEW456            │
│  5. Attacker now uses SID=FIXED123                     │
│     VULNERABLE: gets authenticated session             │
│     SAFE: SID=FIXED123 is invalid after login          │
│                                                        │
│  FIX:                                                  │
│  Regenerate session ID immediately after login         │
│  Old SID must be invalidated                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Session regeneration in Spring Security**

```java
@Configuration
@EnableWebSecurity
public class SessionSecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http)
            throws Exception {
        http
            .sessionManagement(session -> session
                // IF_REQUIRED: creates session only when needed
                .sessionCreationPolicy(
                    SessionCreationPolicy.IF_REQUIRED)
                // REGENERATE: invalidates old session, creates
                // new one with same attributes after login
                // This fixes session fixation automatically
                .sessionFixation()
                    .changeSessionId() // Servlet 3.1+ - 
                    // preferred over migrateSession()
                    // or newSession()
            );
        return http.build();
    }
}
// changeSessionId(): assigns new session ID to existing session
//   (most efficient, preserves session data)
// migrateSession(): creates new session, copies attributes
// newSession(): creates new session, discards old attributes
// none(): VULNERABLE - does NOT change session ID on login
```

**Example - BAD: no session regeneration on login**

```java
// BAD: manual session handling that forgets to regenerate
@PostMapping("/login")
public ResponseEntity<?> login(
        @RequestBody LoginRequest req,
        HttpSession session) {
    User user = authenticate(req.getEmail(),
        req.getPassword());
    // VULNERABLE: using the existing pre-auth session
    // without changing the session ID
    session.setAttribute("user", user);
    return ResponseEntity.ok(new LoginResponse(user));
}

// GOOD: invalidate old session, create new one
@PostMapping("/login")
public ResponseEntity<?> login(
        @RequestBody LoginRequest req,
        HttpServletRequest request) {
    User user = authenticate(req.getEmail(),
        req.getPassword());
    // Invalidate old session to prevent fixation
    HttpSession old = request.getSession(false);
    if (old != null) old.invalidate();
    // Create new session with new ID
    HttpSession newSession = request.getSession(true);
    newSession.setAttribute("user", user);
    return ResponseEntity.ok(new LoginResponse(user));
}
```

---

*Authentication category: ATH | Entry: ATH-034 | v5.0*