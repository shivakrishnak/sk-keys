---
id: ATH-014
title: "Remember Me and Persistent Sessions"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-008, ATH-009
used_by: ATH-032, ATH-046
related: ATH-008, ATH-009, ATH-015
tags:
  - security
  - authentication
  - sessions
  - remember-me
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/authentication/remember-me-and-persistent-sessions/
---

⚡ **TL;DR** - "Remember Me" extends authentication beyond the browser
session using a long-lived token stored in a persistent cookie.
The challenge: long-lived tokens are high-value theft targets.
The secure implementation uses a one-time rotating token (each use
issues a new token, invalidates the old) so theft is detectable:
if the old token is presented after a legitimate use, someone stole
it - invalidate all sessions immediately.

---

### 📊 Entry Metadata

| #014 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-008, ATH-009 | |
| **Used by:** | ATH-032, ATH-046 | |
| **Related:** | ATH-008 Sessions, ATH-009 Cookies, ATH-015 Logout | |

---

### 📘 Textbook Definition

Persistent sessions ("Remember Me") extend authentication
state beyond a single browser session using a durable long-lived
token stored in a persistent cookie. The secure implementation
(Ambur-Eavesdropping defense) uses a rotating token series:
each use of the remember-me token issues a new token and
invalidates the current one. If a previously valid token is
presented (i.e., someone captured an old token and tried to
replay it), the server detects that a stored token was used
again - indicating theft - and invalidates all sessions for
that user as a precaution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A persistent cookie that logs you in automatically - but
each use rotates the token so theft is detectable.

**One analogy:**
> A single-use hotel key card for extended guests. When you
> use the card each day, it is reprogrammed with a new code
> for the next day. If your old card is used again after
> you used it (someone copied it), the system sees a card
> code it invalidated - theft detected, all your cards
> are deactivated.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│          Secure Remember-Me Flow (Rotating Token)      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ENROLLMENT (login with "Remember Me" checked):        │
│  1. Generate token series ID (random, identifies user) │
│  2. Generate token value (random, used once)           │
│  3. Store: persistent_tokens(series, hash(token),      │
│            user_id, last_used)                         │
│  4. Set cookie: REMEMBER=<series>:<token> (30-day TTL) │
│                                                        │
│  AUTO-LOGIN (browser revisit):                         │
│  1. Cookie REMEMBER=<series>:<token> presented         │
│  2. Look up series in DB                               │
│  3. Verify: hash(presented token) == stored hash?      │
│     YES: rotate → new token, update DB, re-auth user   │
│     NO (old token presented): THEFT DETECTED           │
│         → invalidate ALL sessions for this user        │
│         → require full re-authentication               │
│                                                        │
│  THEFT DETECTION SCENARIO:                             │
│  Attacker steals cookie: REMEMBER=S1:T1                │
│  Legitimate user visits: uses T1, gets T2 in cookie    │
│  Attacker later presents T1 (old token, now invalid):  │
│  Server detects reuse of old token → user is warned    │
│  All sessions invalidated (attacker session dies too)  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Spring Security persistent token repository**

```java
@Configuration
public class RememberMeConfig {

    @Bean
    public PersistentTokenRepository tokenRepository(
            DataSource dataSource) {
        JdbcTokenRepositoryImpl repo =
            new JdbcTokenRepositoryImpl();
        repo.setDataSource(dataSource);
        // Spring creates: persistent_logins(
        //   username, series, token, last_used)
        return repo;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http,
            PersistentTokenRepository repo) throws Exception {
        http.rememberMe(rm -> rm
            .tokenRepository(repo)  // DB-backed, rotating
            .tokenValiditySeconds(30 * 24 * 60 * 60) // 30d
            .key(System.getenv("REMEMBER_ME_KEY")) // HMAC key
        );
        return http.build();
    }
}
```

**Example - BAD vs GOOD: simple vs rotating token**

```sql
-- BAD: simple token, never rotated
-- Theft is undetectable until the 30-day expiry
CREATE TABLE remember_me_simple (
    token VARCHAR(64) PRIMARY KEY,   -- static token
    user_id BIGINT NOT NULL,
    expires_at TIMESTAMP NOT NULL
);
-- If token is stolen: attacker uses it silently for 30 days
-- Server has no way to know the token was used by two parties

-- GOOD: rotating series/token pair
CREATE TABLE persistent_logins (
    series VARCHAR(64) PRIMARY KEY,  -- identifies the session
    token  VARCHAR(64) NOT NULL,     -- rotated each use
    user_id BIGINT NOT NULL,
    last_used TIMESTAMP NOT NULL,
    INDEX (user_id)  -- for "invalidate all" lookup
);
-- Old token presented after rotation = theft signal
-- Rotate on every use = window for theft is one visit
```

---

### ⚠️ Common Failure Modes

**Remember-me bypasses MFA:**

```
Symptom: user enrolled MFA but remember-me token
logs them in silently without MFA prompt.

Root cause: auto-login from remember-me cookie skips
the MFA step (only verifies the possession factor -
the cookie - not the second factor).

Fix: remember-me should grant a limited session
(access to low-sensitivity operations). Full-privilege
access (admin, financial operations) requires
re-authentication including MFA regardless of
remember-me state.
```

---

*Authentication category: ATH | Entry: ATH-014 | v5.0*