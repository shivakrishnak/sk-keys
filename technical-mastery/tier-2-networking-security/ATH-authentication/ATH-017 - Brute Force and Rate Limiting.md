---
id: ATH-017
title: "Brute Force and Rate Limiting"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-005, ATH-006, ATH-016
used_by: ATH-018, ATH-021, ATH-035
related: ATH-016, ATH-018, ATH-035
tags:
  - security
  - authentication
  - brute-force
  - rate-limiting
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/authentication/brute-force-and-rate-limiting/
---

⚡ **TL;DR** - Brute force attacks submit rapid login attempts to guess
credentials. Rate limiting is the primary defense: restrict the number
of attempts allowed per unit of time, per account, or per IP. The
challenge is scope: per-IP limits are defeated by distributed attacks
(botnets); per-account limits risk denial-of-service against legitimate
users. The effective strategy combines per-account progressive delays,
CAPTCHA triggers, and anomaly detection - not just hard lockouts.

---

### 📊 Entry Metadata

| #017 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-005, ATH-006, ATH-016 | |
| **Used by:** | ATH-018, ATH-021, ATH-035 | |
| **Related:** | ATH-016 Error Messages, ATH-018 Lockout, ATH-035 Credential Stuffing | |

---

### 🔥 The Problem This Solves

**BRUTE FORCE THREAT MODELS:**

1. **Online brute force (same IP):** Attacker submits
   thousands of password guesses for a single account
   from one IP. Detectable by request volume.

2. **Distributed brute force (botnet):** Thousands of
   IPs each submit one guess. Per-IP rate limiting fails.
   Detectable by failed-login volume per target account.

3. **Password spraying:** Attacker tries one common
   password (Password1!) against thousands of accounts.
   Neither per-IP nor per-account detection catches this
   easily (low volume per account, low volume per IP).

4. **Credential stuffing:** Attacker uses known
   email/password pairs from data breaches. Valid
   credentials, distributed IPs. Very low failure rate.

---

### 📘 Textbook Definition

Brute force authentication attacks attempt to gain unauthorized
access by systematically exhausting possible credentials. Rate
limiting is a countermeasure that restricts the number of
authentication attempts allowed within a time window. Effective
defense uses layered controls: per-account attempt counting,
progressive delays (exponential backoff), CAPTCHA challenges,
and behavioral anomaly detection. NIST SP 800-63B Section 5.2.2
mandates monitoring and limiting repeated authentication failures.

---

### ⚙️ How It Works (Mechanism)

**Layered rate limiting strategy:**

```
┌────────────────────────────────────────────────────────┐
│          Layered Authentication Defense                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LAYER 1: Per-Account Progressive Delay                │
│  Attempt 1-3:  Normal response time (0ms extra)        │
│  Attempt 4-5:  1-second delay added                    │
│  Attempt 6-7:  5-second delay                          │
│  Attempt 8+:   CAPTCHA required OR soft lockout        │
│                                                        │
│  WHY PROGRESSIVE? Hard lockout (lock after 5 fails)    │
│  enables DoS: attacker locks every account by failing  │
│  5 times without needing correct credentials.          │
│                                                        │
│  LAYER 2: Per-IP Rate Limiting                         │
│  >30 requests/min from same IP → 429 Too Many Requests │
│  Defeats same-IP brute force. Fails against botnets.   │
│                                                        │
│  LAYER 3: Global Login Anomaly Detection               │
│  >1000 failed logins/min globally → alert security     │
│  Alert on: unusual failure rate spike, new IP ranges,  │
│  known-bad IP reputation lists                         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Redis-based rate limiting (Bucket4j / manual)**

```java
@Service
public class LoginRateLimiter {

    private final RedisTemplate<String, String> redis;

    // Per-account attempt tracking
    public boolean isRateLimited(String email) {
        String key = "login_attempts:" +
            email.toLowerCase();
        Long attempts = redis.opsForValue().increment(key);
        if (attempts == 1) {
            redis.expire(key, 15, TimeUnit.MINUTES);
        }
        return attempts > 10; // block after 10 attempts/15min
    }

    // Progressive delay based on attempt count
    public long getDelayMs(String email) {
        String key = "login_attempts:" +
            email.toLowerCase();
        Long attempts = Optional
            .ofNullable(redis.opsForValue().get(key))
            .map(Long::parseLong)
            .orElse(0L);
        if (attempts <= 3) return 0;
        if (attempts <= 5) return 1_000;
        if (attempts <= 7) return 5_000;
        return 30_000; // 30s delay after 7 attempts
    }

    public void resetAttempts(String email) {
        redis.delete("login_attempts:" + email.toLowerCase());
    }
}

@PostMapping("/login")
public ResponseEntity<?> login(
        @RequestBody LoginRequest req) throws Exception {
    String email = req.email().toLowerCase();

    if (rateLimiter.isRateLimited(email)) {
        return ResponseEntity.status(429)
            .header("Retry-After", "900")
            .body("Too many attempts. Try again later.");
    }

    long delay = rateLimiter.getDelayMs(email);
    if (delay > 0) {
        Thread.sleep(delay); // add delay before responding
    }

    User user = authService.authenticate(
        req.email(), req.password());
    if (user == null) {
        // DO NOT reveal if it was email or password mismatch
        return ResponseEntity.status(401)
            .body("Invalid email or password");
    }

    rateLimiter.resetAttempts(email); // clear on success
    return ResponseEntity.ok(issueSession(user));
}
```

**Example - BAD vs GOOD: hard lockout vs progressive delay**

```java
// BAD: hard lockout after 5 attempts
// Enables DoS: attacker locks all accounts in 5 requests
if (failedAttempts >= 5) {
    user.setLocked(true); // account permanently locked
    userRepo.save(user);
    return ResponseEntity.status(403)
        .body("Account locked");
    // Attacker submits 5 bad passwords for every account
    // All legitimate users are locked out
}

// GOOD: progressive delay + soft lockout
// DoS costs attacker time, not the legitimate user
// After 10 attempts: require CAPTCHA (not hard lock)
// After 50 attempts: temporary 15-minute soft lock
// User can always unlock via email verification
if (failedAttempts >= 10) {
    // Require CAPTCHA before next attempt
    session.setAttribute("require_captcha", true);
    return ResponseEntity.status(429)
        .body("Please complete CAPTCHA to continue");
}
```

**Example - FAILURE: distributed brute force bypasses per-IP limits**

```
Attack setup:
  10,000 bot IPs, each submitting 1 login attempt/hour
  Target: all 10,000 known user accounts
  Password list: top-1000 common passwords
  Rate: 1 attempt per IP per account per day

  Per-IP rate limit of 10/min: each IP sends 1 request
  → rate limit never triggers
  Per-account rate limit of 10/day: each account sees
  1 attempt per day from different IPs
  → if 10,000 IPs → 10,000 attempts per day per account
  → rate limit triggers on account, not IP

Fix:
  1. Per-account rate limit catches distributed attacks
  2. Monitor global failed login RATE (not just per-IP)
  3. CAPTCHA on suspicious patterns (many IPs, same ASN)
  4. Breach password detection: reject known-breached passwords
     (HaveIBeenPwned k-anonymity API integration)
```

---

*Authentication category: ATH | Entry: ATH-017 | v5.0*