---
id: ATH-016
title: "Authentication Error Messages (Not Leaking Clues)"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★☆☆
depends_on: ATH-005, ATH-006
used_by: ATH-021, ATH-017
related: ATH-005, ATH-017, ATH-021
tags:
  - security
  - authentication
  - error-messages
  - enumeration
  - foundational
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/authentication/authentication-error-messages-not-leaking-clues/
---

⚡ **TL;DR** - Authentication error messages should never reveal whether
a login failed because the username does not exist or the password was
wrong. Specific messages ("Email not found" vs "Incorrect password")
enable account enumeration: attackers can confirm valid usernames
before launching targeted attacks. The correct message for any login
failure: "Invalid email or password" - identical wording, identical
HTTP timing.

---

### 📊 Entry Metadata

| #016 | Category: Authentication | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | ATH-005, ATH-006 | |
| **Used by:** | ATH-021, ATH-017 | |
| **Related:** | ATH-005 Attack Landscape, ATH-017 Rate Limiting, ATH-021 Enumeration | |

---

### 🔥 The Problem This Solves

**ACCOUNT ENUMERATION:**

An attacker trying to break into user accounts needs two
pieces of information: a valid username and a matching
password. If the login form says "Email address not found"
for unknown emails, the attacker can confirm which emails
are registered by trying thousands of email addresses and
observing the responses. This is called account enumeration.

Once the attacker has a list of confirmed valid usernames,
they can:
- Launch targeted credential stuffing (try leaked password
  databases against confirmed accounts)
- Launch targeted phishing (send convincing emails to
  confirmed users of the specific service)
- Sell the confirmed account list

---

### 📘 Textbook Definition

Authentication error message security refers to the practice
of returning identical error messages for all authentication
failure conditions (unknown user, wrong password, locked
account) to prevent attackers from inferring whether a given
email or username exists in the system. This practice prevents
account enumeration and is required by OWASP Authentication
Security Guidelines and GDPR's user identity protection
recommendations. The implementation must also normalize response
timing to prevent timing attacks that distinguish user existence
from password failure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Say the same thing regardless of whether the email is
unknown or the password is wrong - never reveal which.

**Correct vs incorrect messages:**

```
LOGIN FAILURE - WRONG MESSAGE DESIGN:
  "Email address not found"      ← reveals: email not registered
  "Incorrect password"           ← reveals: email IS registered
  "Account locked after 5 attempts" ← reveals: email exists AND
                                      they are under attack

LOGIN FAILURE - CORRECT MESSAGE DESIGN:
  For ALL failure cases: "Invalid email or password"
  Status code: 401 (identical for all cases)
  Response time: normalized (same regardless of db lookup)
```

---

### ⚙️ How It Works (Mechanism)

**Timing attack prevention:**

Even with identical messages, response timing can reveal
information. If the server responds in 2ms for unknown users
(short circuit: user not found) and 150ms for wrong passwords
(user found, password hash compared), an attacker can
distinguish the two cases by timing alone.

```
┌────────────────────────────────────────────────────────┐
│           Timing Side-Channel Prevention               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  VULNERABLE:                                           │
│  unknown email → DB miss → return 401 immediately      │
│  Response time: ~2ms (no hash computation)             │
│                                                        │
│  wrong password → DB hit → compute bcrypt → return 401 │
│  Response time: ~150ms (bcrypt is slow by design)      │
│                                                        │
│  Attacker: measures response time → knows if email     │
│            exists (even without reading the message)   │
│                                                        │
│  FIX: Always compute a hash even for unknown users     │
│  unknown email → DB miss → hash dummy value anyway     │
│               → return 401 after same delay            │
│  Response time: ~150ms in both cases                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - BAD vs GOOD: authentication error messages**

```java
// BAD: specific error messages reveal account existence
@PostMapping("/login")
public ResponseEntity<?> login(
        @RequestBody LoginRequest req) {
    User user = userRepo.findByEmail(req.email());
    if (user == null) {
        return ResponseEntity.status(401)
            .body("Email not found");  // leaks: not registered
    }
    if (!passwordEncoder.matches(req.password(),
            user.getPasswordHash())) {
        return ResponseEntity.status(401)
            .body("Incorrect password"); // leaks: email valid
    }
    return ResponseEntity.ok(issueSession(user));
}

// GOOD: identical message, timing-normalized
@PostMapping("/login")
public ResponseEntity<?> login(
        @RequestBody LoginRequest req) {
    User user = userRepo.findByEmail(req.email());

    // Always compute the hash comparison, even if user
    // doesn't exist. This normalizes response timing.
    String hashToCompare = user != null
        ? user.getPasswordHash()
        : "$2a$12$dummyhashvaluetopreventtimingattackX";
    boolean passwordMatches = passwordEncoder
        .matches(req.password(), hashToCompare);

    if (user == null || !passwordMatches) {
        return ResponseEntity.status(401)
            .body("Invalid email or password"); // same always
    }
    return ResponseEntity.ok(issueSession(user));
}
```

**Example - FAILURE: verbose error in password reset**

```
Vulnerable password reset flow:
  POST /reset-password {"email": "victim@gmail.com"}
  
  Response if email not registered:
    HTTP 404: "No account found for this email address"
  
  Response if email registered:
    HTTP 200: "Reset link sent to your email"

  Impact: attacker enumerates registered emails at
  scale - thousands of requests to /reset-password
  with email lists → confirmed account list

Fix: always return the same response for /reset-password
  HTTP 200: "If an account exists for this email,
             a reset link will be sent."
  Never 404, never distinguish found vs not-found.
  Log the attempt server-side for rate limiting.
```

---

### ⚠️ Additional Leak Points

| Leak point | What it reveals | Fix |
|---|---|---|
| "Account locked" message | Email is registered and targeted | Same generic message |
| Registration: "Email already in use" | Email is registered | Sign-in link instead, or send email |
| Forgot password 404 | Email not registered | Always 200 |
| Timing difference | User existence via timing side-channel | Dummy hash computation |
| Different HTTP status codes | 404 vs 401 for not-found | Always 401 for auth failures |

---

*Authentication category: ATH | Entry: ATH-016 | v5.0*