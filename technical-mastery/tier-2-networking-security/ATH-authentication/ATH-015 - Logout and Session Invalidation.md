---
id: ATH-015
title: "Logout and Session Invalidation"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-008, ATH-014
used_by: ATH-046, ATH-054
related: ATH-008, ATH-014, ATH-046
tags:
  - security
  - authentication
  - sessions
  - logout
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 15
permalink: /technical-mastery/authentication/logout-and-session-invalidation/
---

⚡ **TL;DR** - Correct logout has three mandatory steps: (1) invalidate
the server-side session record, (2) clear the session cookie, and
(3) invalidate any refresh/remember-me tokens. Skipping step 1 means
the session ID still works even after the cookie is cleared - accessible
via browser history or cached requests. For token-based (JWT) auth,
logout is architecturally harder: tokens cannot be invalidated
server-side without maintaining a revocation list.

---

### 📊 Entry Metadata

| #015 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-008, ATH-014 | |
| **Used by:** | ATH-046, ATH-054 | |
| **Related:** | ATH-008 Sessions, ATH-014 Remember Me, ATH-046 Token Theft | |

---

### 📘 Textbook Definition

Logout (session invalidation) is the process of terminating
an authenticated session so that the session identifiers
(session ID, refresh token, remember-me token) cannot be
used to authenticate subsequent requests. A correct logout
implementation invalidates all server-side session state
associated with the current session (and optionally all
sessions for the user), then clears client-side identifiers.
For JWT-based systems without server state, logout requires
either token short expiry or an explicit revocation mechanism
(token denylist).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Delete the server-side session first - clearing the cookie
alone is not logout.

**The complete logout checklist:**

```
Server side (MANDATORY):
  1. Delete session record from session store (Redis DEL)
  2. Delete remember-me token from persistent_logins table
  3. Optionally: revoke all sessions (devices) for this user

Client side (necessary but insufficient alone):
  4. Set-Cookie: SESSIONID=; Max-Age=0; HttpOnly; Secure
     (removes cookie from browser)
  5. If SPA: clear in-memory access token
  6. If SPA: clear refresh token from HttpOnly cookie
```

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│               Logout Attack Surface                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  INCOMPLETE LOGOUT (cookie-only):                      │
│  Server: (nothing)                                     │
│  Client: clears cookie                                 │
│  Result: session record still exists in Redis          │
│          Browser history shows old Set-Cookie header   │
│          Attacker with old session ID can still auth   │
│                                                        │
│  INCOMPLETE LOGOUT (server-only, no cookie clear):     │
│  Server: DEL sessions:abc123                           │
│  Client: (nothing)                                     │
│  Result: cookie persists in browser                    │
│          Next visit: session lookup fails → 401        │
│          User experience: broken (seems logged out     │
│          but gets login error, not login page)         │
│                                                        │
│  CORRECT LOGOUT:                                       │
│  Server: DEL sessions:abc123                           │
│          DELETE FROM persistent_logins WHERE ...       │
│  Client: Set-Cookie: SESSIONID=; Max-Age=0             │
│  Result: no valid server state + no valid cookie       │
│          Session is completely terminated              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security logout configuration**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http,
        PersistentTokenRepository tokenRepo) throws Exception {
    http.logout(logout -> logout
        .logoutUrl("/logout")
        .logoutSuccessUrl("/login?logout")
        // Invalidate HTTP session
        .invalidateHttpSession(true)
        // Clear Spring Security context
        .clearAuthentication(true)
        // Clear session cookie
        .deleteCookies("SESSIONID", "REMEMBER_ME")
        // Delete persistent (remember-me) token from DB
        .addLogoutHandler(
            new PersistentTokenBasedRememberMeServices(
                "key", userDetailsService, tokenRepo))
    );
    return http.build();
}
```

**Example - BAD vs GOOD: server-side invalidation**

```java
// BAD: only clear the cookie (client-side only)
@PostMapping("/logout")
public ResponseEntity<?> logout(
        HttpServletResponse response) {
    Cookie cookie = new Cookie("SESSIONID", "");
    cookie.setMaxAge(0);
    response.addCookie(cookie);
    return ResponseEntity.ok().build();
    // Session record still exists in Redis!
    // Old session ID from browser cache still works.
}

// GOOD: invalidate server-side first, then clear cookie
@PostMapping("/logout")
public ResponseEntity<?> logout(
        HttpServletRequest request,
        HttpServletResponse response) {
    // Step 1: invalidate the server-side session
    HttpSession session = request.getSession(false);
    if (session != null) {
        session.invalidate(); // removes from session store
    }
    // Step 2: clear the cookie
    ResponseCookie cookie = ResponseCookie
        .from("SESSIONID", "")
        .maxAge(0)
        .path("/")
        .httpOnly(true)
        .secure(true)
        .build();
    response.addHeader(HttpHeaders.SET_COOKIE,
        cookie.toString());
    return ResponseEntity.ok().build();
}
```

**Example - JWT logout (token revocation)**

```java
// JWTs cannot be "deleted" - they are self-contained.
// Logout must add the token to a denylist (short TTL).

@PostMapping("/logout")
public ResponseEntity<?> logout(
        @RequestHeader("Authorization") String authHeader) {
    String token = authHeader.replace("Bearer ", "");
    Claims claims = jwtService.parse(token);

    // Add to denylist until token naturally expires
    long ttl = claims.getExpiration().getTime()
        - System.currentTimeMillis();
    if (ttl > 0) {
        // Redis: key expires when token expires
        redis.set("revoked:" + claims.getId(), "1",
            ttl, TimeUnit.MILLISECONDS);
    }
    return ResponseEntity.ok().build();
}

// In JWT validation middleware: check denylist
boolean isRevoked = redis.hasKey("revoked:" + jti);
if (isRevoked) throw new TokenRevokedException();
// Note: this reintroduces server state into stateless JWT
// Token short expiry (15 min) often preferred over denylist
```

---

*Authentication category: ATH | Entry: ATH-015 | v5.0*