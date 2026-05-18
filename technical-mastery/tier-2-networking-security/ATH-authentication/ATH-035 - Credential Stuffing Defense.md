---
id: ATH-035
title: "Credential Stuffing Defense"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-017, ATH-018, ATH-007
used_by: ATH-044, ATH-050, ATH-052
related: ATH-005, ATH-017, ATH-044
tags:
  - security
  - authentication
  - credential-stuffing
  - attack-defense
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/authentication/credential-stuffing-defense/
---

⚡ **TL;DR** - Credential stuffing is not brute force: attackers use
real leaked username/password pairs from other breach databases
(billions available on dark web) and test them against your
application. Account lockout is useless - each credential is tried
once. Defense requires: rate limiting per IP/fingerprint, CAPTCHA
for suspicious traffic, Have I Been Pwned (HIBP) API to detect
known-compromised passwords at registration, MFA, and bot detection.
Detection signal: large spike in login failures across many accounts
with geographically diverse IPs.

---

### 📊 Entry Metadata

| #035 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-017 Rate Limiting, ATH-018 Lockout, ATH-007 Password Hashing | |
| **Used by:** | ATH-044, ATH-050, ATH-052 | |
| **Related:** | ATH-005 Attack Overview, ATH-017 Rate Limiting, ATH-044 Account Takeover | |

---

### 📘 Textbook Definition

Credential stuffing is an automated attack where adversaries
obtain large lists of leaked username/password combinations
(from data breaches of other services) and systematically
attempt to authenticate using those credentials against a
target application, exploiting password reuse. Unlike brute
force (guessing all combinations for one account), credential
stuffing uses valid credentials from real accounts - each
credential is typically tried once per target, bypassing
account lockout mechanisms. Attack velocity ranges from
thousands to millions of login attempts per hour using botnets
that distribute requests across IP addresses.

---

### ⚙️ How It Works (Mechanism)

**Defense layers:**

```
┌────────────────────────────────────────────────────────┐
│         Credential Stuffing Defense Layers             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Layer 1: Bot Detection (first line)                   │
│  - Browser fingerprinting (user-agent, JS behavior)    │
│  - CAPTCHA on suspicious login patterns                │
│  - Device fingerprint consistency check                │
│  - Behavioral biometrics (typing speed, mouse)         │
│                                                        │
│  Layer 2: Rate Limiting                                │
│  - Per-IP: max 10 failed logins/min per IP             │
│  - Per-account: max 5 failed logins/5min per account   │
│  - Global: alert if >1000 failures/min across all      │
│                                                        │
│  Layer 3: Compromised Credential Detection             │
│  - At registration: check password against HIBP API   │
│  - At login: detect if username+password appears in    │
│    known breach DB (HIBP k-anonymity model)            │
│                                                        │
│  Layer 4: MFA (strongest control)                      │
│  - Even if credential is valid: second factor blocks   │
│  - Attacker has leaked password but not user's phone   │
│                                                        │
│  Layer 5: Monitoring                                   │
│  - Alert: failure rate > 5x normal per hour            │
│  - Alert: >100 unique accounts with failures from      │
│    same /24 IP block in 1 minute                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - HIBP API check at registration (k-anonymity)**

```java
@Service
public class CompromisedPasswordChecker {

    // Uses HIBP k-anonymity: only first 5 chars of SHA1
    // sent to API - no full password ever leaves the client
    public boolean isCompromised(String password) {
        String sha1 = DigestUtils.sha1Hex(
            password.toUpperCase()).toUpperCase();
        String prefix = sha1.substring(0, 5);
        String suffix = sha1.substring(5);

        // API returns all hashes with that 5-char prefix
        String response = hibpClient.get()
            .uri("/range/" + prefix)
            .retrieve()
            .bodyToMono(String.class)
            .block();

        // Check if our suffix appears in the response
        return Arrays.stream(response.split("\n"))
            .map(line -> line.split(":")[0].trim())
            .anyMatch(hash -> hash.equals(suffix));
    }
}

// Usage at registration:
if (compromisedPasswordChecker.isCompromised(newPassword)) {
    throw new WeakPasswordException(
        "This password has appeared in a data breach. "
        + "Please choose a different password.");
}
```

**Example - Credential stuffing detection alert**

```java
@Service
public class CredentialStuffingDetector {

    private final MeterRegistry metrics;

    @EventListener
    public void onLoginFailure(LoginFailureEvent event) {
        // Track failures per IP per minute using Redis
        String key = "login:fail:" + event.getIpAddress()
            + ":" + (System.currentTimeMillis() / 60000);
        long count = redis.increment(key);
        redis.expire(key, Duration.ofMinutes(5));

        if (count > 20) {
            // Trigger CAPTCHA for this IP
            captchaRequiredIps.add(event.getIpAddress());
            metrics.counter("security.stuffing.ip.blocked")
                .increment();
        }

        // Check cross-account stuffing pattern
        long globalFailures = metrics
            .counter("auth.login.failure").count();
        if (globalFailures > normalBaseline * 5) {
            alertService.sendCriticalAlert(
                "Possible credential stuffing - "
                + globalFailures + " failures in last minute");
        }
    }
}
```

---

*Authentication category: ATH | Entry: ATH-035 | v5.0*