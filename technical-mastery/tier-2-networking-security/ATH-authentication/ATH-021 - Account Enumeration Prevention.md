---
id: ATH-021
title: "Account Enumeration Prevention"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-016, ATH-017, ATH-020
used_by: ATH-035, ATH-044
related: ATH-016, ATH-017, ATH-035
tags:
  - security
  - authentication
  - enumeration
  - privacy
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/authentication/account-enumeration-prevention/
---

⚡ **TL;DR** - Account enumeration allows attackers to confirm which
email addresses or usernames are registered in a system by observing
response differences between "user not found" and "wrong password"
scenarios. Prevention requires: identical messages, identical HTTP
status codes, identical response timing, and identical behavior on
password reset, registration, and username lookup endpoints - not
just the login endpoint.

---

### 📊 Entry Metadata

| #021 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-016, ATH-017, ATH-020 | |
| **Used by:** | ATH-035, ATH-044 | |
| **Related:** | ATH-016 Error Messages, ATH-017 Rate Limiting, ATH-035 Credential Stuffing | |

---

### 📘 Textbook Definition

Account enumeration is an information disclosure vulnerability
where an application reveals whether a user account exists
based on differential responses to authentication or account
management operations. OWASP defines this as a security
misconfiguration. Enumeration vectors include: login
(different responses for known vs unknown accounts), password
reset (404 vs 200), registration ("email already in use"),
username checks (real-time availability), and timing
differences. Prevention requires consistent responses across
all code paths that touch user existence.

---

### ⚙️ How It Works (Mechanism)

**Every endpoint that touches user existence is an enumeration vector:**

```
┌────────────────────────────────────────────────────────┐
│       Account Enumeration Vectors Map                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LOGIN ENDPOINT:                                       │
│  "User not found" vs "Wrong password"  → VECTOR        │
│  404 vs 401 status code               → VECTOR        │
│  2ms vs 150ms response time           → VECTOR        │
│                                                        │
│  PASSWORD RESET ENDPOINT:                              │
│  "No account for this email" (404)    → VECTOR        │
│  vs "Check your email" (200)                           │
│  FIX: always return 200 "Check your email"             │
│                                                        │
│  REGISTRATION ENDPOINT:                                │
│  "Email already in use" on submit     → VECTOR        │
│  FIX: "If this email is not registered, we created     │
│        your account. Check your email to verify."      │
│                                                        │
│  USERNAME AVAILABILITY (real-time check):              │
│  AJAX: GET /api/check-username?u=alice → exists?       │
│  FIX: remove real-time availability check, or require  │
│       CAPTCHA before revealing availability            │
│                                                        │
│  OAUTH/SSO ERROR PAGES:                                │
│  "Unknown email in our system" on OIDC → VECTOR        │
│  FIX: generic "Authentication failed"                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - BAD vs GOOD: registration flow**

```java
// BAD: reveals email exists on registration attempt
@PostMapping("/register")
public ResponseEntity<?> register(
        @RequestBody RegisterRequest req) {
    if (userRepo.existsByEmail(req.email())) {
        return ResponseEntity.status(409)
            .body("This email is already registered");
        // Attacker learns: email IS registered
    }
    createUser(req);
    return ResponseEntity.ok("Registration successful");
}

// GOOD: silent no-op for existing accounts
// Send email notification instead of error message
@PostMapping("/register")
public ResponseEntity<?> register(
        @RequestBody RegisterRequest req) {
    boolean exists = userRepo.existsByEmail(req.email());
    if (exists) {
        // Send email: "Someone tried to register with
        //              your email. If this was you,
        //              sign in instead. If not, ignore this."
        emailService.sendAlreadyRegistered(req.email());
    } else {
        User user = createUser(req);
        emailService.sendVerification(req.email(),
            user.getVerificationToken());
    }
    // SAME response regardless of whether email existed
    return ResponseEntity.ok(
        "Check your email for next steps");
}
```

**Example - Rate-limited username availability check**

```java
// Some UX requires username availability check
// Mitigate enumeration with rate limiting and CAPTCHA

@GetMapping("/api/check-username")
@RateLimit(maxPerMinute = 5, key = "REMOTE_ADDR")
public ResponseEntity<Map<String, Boolean>> checkUsername(
        @RequestParam String username,
        @RequestHeader(value = "X-Captcha-Token",
                       required = false) String captchaToken) {
    // Require solved CAPTCHA before revealing availability
    if (!captchaService.verify(captchaToken)) {
        return ResponseEntity.status(429)
            .body(Map.of("available", false));
        // Don't confirm or deny - just block
    }
    boolean available = !userRepo.existsByUsername(username);
    return ResponseEntity.ok(
        Map.of("available", available));
}
```

---

### ⚠️ Timing Side-Channels at Scale

At millisecond precision, even "identical" code paths differ
in timing because database queries for existing users find a
row (index hit), while queries for non-existent users exhaust
the index (slightly longer). Under measurement at scale
(1000s of requests per account), these sub-millisecond
differences are statistically detectable.

Mitigation: add artificial random delay (1-5ms uniform
distribution) to authentication responses. This swamps the
signal in noise.

---

*Authentication category: ATH | Entry: ATH-021 | v5.0*