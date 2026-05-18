---
id: ATH-018
title: "Account Lockout Policy"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-017
used_by: ATH-035, ATH-044
related: ATH-017, ATH-019, ATH-021
tags:
  - security
  - authentication
  - lockout
  - account-security
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/authentication/account-lockout-policy/
---

⚡ **TL;DR** - Account lockout blocks access after repeated failed
authentication attempts, limiting brute force. The trade-off: hard
lockout (permanent until manual unlock) creates a denial-of-service
vector - attackers deliberately trigger lockouts to disable accounts.
Modern guidance (NIST 800-63B) recommends progressive delays and
soft lockouts (temporary, self-resetting) over hard lockouts.

---

### 📊 Entry Metadata

| #018 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-017 Rate Limiting | |
| **Used by:** | ATH-035, ATH-044 | |
| **Related:** | ATH-017 Rate Limiting, ATH-019 Password Policy, ATH-021 Enumeration | |

---

### 📘 Textbook Definition

Account lockout policy defines the conditions under which a
user account is temporarily or permanently restricted from
authentication following repeated failed attempts. Parameters
include: lockout threshold (number of failures), lockout
duration (temporary/permanent), observation window (time
period for counting failures), and reset mechanism (automatic
timeout, manual admin unlock, or user self-service via email).
Policy design must balance security (limit guessing) against
availability (prevent DoS against legitimate users).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Too many wrong passwords = account temporarily blocked,
but "permanently blocked" is a DoS weapon for attackers.

**The lockout spectrum:**

```
NO LOCKOUT ←────────────────────────────→ HARD LOCKOUT
           Unlimited     Progressive    Admin-only
           attempts      delay          unlock
           (brute-force  (delays        (DoS risk:
           friendly)     increase)      attackers
                         (NIST-         lock accounts
                         recommended)   on purpose)
```

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│        Account Lockout Types and Trade-offs            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  HARD LOCKOUT (traditional):                           │
│  After N failures → account locked permanently         │
│  Unlock: admin action required                         │
│  Pro: simple, strong brute-force protection            │
│  Con: DoS vector (attacker locks accounts with 5       │
│       bad guesses; no correct password needed)         │
│       Help desk load: every lockout needs a ticket     │
│                                                        │
│  SOFT LOCKOUT (time-based):                            │
│  After N failures → account locked for T minutes       │
│  Unlock: automatic after timeout                       │
│  Pro: limits DoS impact (only blocks for minutes)      │
│  Con: patient attacker waits out the timeout           │
│                                                        │
│  PROGRESSIVE DELAY (NIST-recommended):                 │
│  After 1-3 failures: normal                            │
│  After 4-5: 1-second delay enforced server-side        │
│  After 6-7: 5-second delay + CAPTCHA                   │
│  After 8+: 30-second delay (not a lock - still usable) │
│  Pro: no DoS vector (account never fully disabled)     │
│  Con: requires more code; delays vs lockouts harder    │
│       to communicate to users                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Soft lockout with progressive delay (Redis)**

```java
@Service
public class AccountLockoutService {

    private final RedisTemplate<String, String> redis;

    private static final int SOFT_LOCK_THRESHOLD = 10;
    private static final long SOFT_LOCK_DURATION_MINS = 15;

    public LockStatus checkLockStatus(String email) {
        String lockKey = "locked:" + email.toLowerCase();
        String attemptsKey =
            "attempts:" + email.toLowerCase();

        // Check if account is in soft lockout period
        if (Boolean.TRUE.equals(redis.hasKey(lockKey))) {
            Long ttl = redis.getExpire(lockKey,
                TimeUnit.SECONDS);
            return LockStatus.lockedFor(ttl);
        }

        Long attempts = Optional
            .ofNullable(redis.opsForValue().get(attemptsKey))
            .map(Long::parseLong).orElse(0L);
        return LockStatus.available(attempts);
    }

    public void recordFailure(String email) {
        String attemptsKey =
            "attempts:" + email.toLowerCase();
        Long attempts = redis.opsForValue()
            .increment(attemptsKey);
        if (attempts == 1) {
            redis.expire(attemptsKey, 30, TimeUnit.MINUTES);
        }

        if (attempts >= SOFT_LOCK_THRESHOLD) {
            // Soft lock: auto-unlocks after 15 minutes
            redis.set("locked:" + email.toLowerCase(), "1",
                SOFT_LOCK_DURATION_MINS, TimeUnit.MINUTES);
        }
    }

    public void recordSuccess(String email) {
        // Reset on successful login
        redis.delete("attempts:" + email.toLowerCase());
        redis.delete("locked:" + email.toLowerCase());
    }
}
```

**Example - BAD: hard lockout creates DoS vector**

```java
// BAD: permanent lock on 5 failures
@Transactional
public void recordLoginFailure(String email) {
    User user = userRepo.findByEmail(email)
        .orElseThrow();
    user.setFailedAttempts(user.getFailedAttempts() + 1);
    if (user.getFailedAttempts() >= 5) {
        user.setLocked(true); // PERMANENT lock
        // Attack: submit 5 bad passwords for every account
        // → everyone locked out; attacker didn't need
        //   correct password for any account
    }
    userRepo.save(user);
}

// GOOD: soft lock with auto-unlock + notify
// After threshold: lock for 15 min, not permanently
// Send email: "Unusual activity on your account. 
//              If this was not you, reset your password."
```

---

### 📏 NIST 800-63B Guidance

NIST does not mandate a specific lockout threshold but:
- Requires monitoring for repeated authentication failures
- Recommends against lockout policies that create DoS
- Recommends limiting the rate of failed attempts
- MFA adoption reduces need for aggressive lockout
  (attacker needs second factor even with correct password)

Modern approach: MFA + progressive delay + anomaly detection
is preferred over hard lockout in most production systems.

---

*Authentication category: ATH | Entry: ATH-018 | v5.0*