---
id: ATH-019
title: "Password Policy Design"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-006, ATH-007
used_by: ATH-020, ATH-035
related: ATH-006, ATH-007, ATH-020
tags:
  - security
  - authentication
  - password-policy
  - nist
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/authentication/password-policy-design/
---

⚡ **TL;DR** - NIST 800-63B (2017, updated 2024) reversed decades of
password policy guidance: complexity rules (uppercase + number +
symbol) and mandatory periodic rotation are now NOT RECOMMENDED.
They result in predictable patterns (P@ssw0rd1!) and password reuse.
The new guidance: maximum length (64+ characters), breach-password
rejection, no forced rotation (unless breached), no complexity rules.
Length beats complexity every time.

---

### 📊 Entry Metadata

| #019 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-006, ATH-007 | |
| **Used by:** | ATH-020, ATH-035 | |
| **Related:** | ATH-006 Username/Password Auth, ATH-007 Password Hashing, ATH-020 Reset | |

---

### 🔥 The Problem This Solves

**WHY TRADITIONAL POLICY FAILS:**

Old policy: minimum 8 chars, uppercase, number, special char,
change every 90 days.

Human behavior under this policy:
- "Password1!" satisfies all requirements
- Next rotation: "Password2!"
- Post-it note with password stuck to monitor
- Same password with `1` incremented

The policy generates predictable patterns that password
cracking tools know. An attacker with a hashed password
database runs `[word][Number][Symbol]` patterns first.

NIST finding: complexity rules reduce the search space
less than they increase user friction.

---

### 📘 Textbook Definition

Password policy defines the rules governing password creation,
length, composition, and rotation. NIST SP 800-63B Digital
Identity Guidelines (Section 5.1.1) specifies evidence-based
requirements: (1) minimum 8 characters, maximum at least 64;
(2) check against known-breached password lists at creation
and change; (3) no mandatory periodic rotation unless evidence
of compromise; (4) no complexity rules; (5) allow all printable
ASCII and Unicode characters; (6) no password hints or
security questions. These rules optimize for actual security
outcomes rather than compliance theater.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Long and unique beats complex and frequently changed.
Stop forcing rotation; start rejecting breached passwords.

**NIST rules at a glance:**

```
DO:
  - Minimum 8 characters (enforce)
  - Maximum 64+ characters (allow long passwords)
  - Check against breach databases (HaveIBeenPwned)
  - Allow all character types (spaces, Unicode, emoji)
  - Only require change if: evidence of compromise

DO NOT:
  - Require uppercase + number + special char combos
  - Force periodic rotation (90/180-day cycles)
  - Show password hints
  - Use security questions (all guessable/searchable)
  - Truncate passwords silently (at 20 chars, etc.)
```

---

### ⚙️ How It Works (Mechanism)

**Why length matters more than complexity:**

```
┌────────────────────────────────────────────────────────┐
│         Password Strength: Length vs Complexity        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PASSWORD SEARCH SPACE:                                │
│  8-char, lower+upper+num+symbol (95 chars):            │
│  95^8 = 6.6 trillion combinations                      │
│  (modern GPU: cracks in minutes offline)               │
│                                                        │
│  20-char, lowercase only (26 chars):                   │
│  26^20 = 19.9 septillion combinations                  │
│  (billions of years to crack)                          │
│                                                        │
│  CONCLUSION: length exponentially increases search     │
│  space. A 20-char lowercase passphrase is vastly       │
│  stronger than an 8-char "complex" password.           │
│                                                        │
│  CORRECT METRIC: entropy, not complexity requirements  │
│  Passphrase "correct horse battery staple" = 44 bits   │
│  Random 8-char complex "R@ndm!8" = ~47 bits            │
│  But: "R@ndm!8" is harder to remember → reuse         │
│  Passphrase: memorable + high entropy + no reuse       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - Breach password check (HaveIBeenPwned k-anonymity)**

```java
@Service
public class BreachedPasswordChecker {

    /**
     * Check password against HaveIBeenPwned API
     * using k-anonymity (only 5-char prefix sent)
     */
    public boolean isBreached(String password) {
        try {
            // SHA-1 hash of the password
            MessageDigest sha1 = MessageDigest
                .getInstance("SHA-1");
            byte[] hashBytes = sha1.digest(
                password.getBytes(StandardCharsets.UTF_8));
            String hash = HexFormat.of()
                .formatHex(hashBytes).toUpperCase();

            // Send only first 5 chars of hash (k-anonymity)
            // The full password never leaves the server
            String prefix = hash.substring(0, 5);
            String suffix = hash.substring(5);

            // HIBP API returns all hashes matching prefix
            String response = hibpClient.get(
                "/range/" + prefix);

            // Check if our suffix appears in the response
            return response.lines().anyMatch(line ->
                line.startsWith(suffix));
        } catch (Exception e) {
            // Fail open: don't block registration if API down
            log.warn("HIBP check failed, allowing password");
            return false;
        }
    }
}
```

**Example - BAD vs GOOD: complexity vs length enforcement**

```java
// BAD: traditional complexity rules
public void validatePassword(String password) {
    if (password.length() < 8 || password.length() > 20) {
        // BUG: max 20 chars truncates password managers
        throw new InvalidPasswordException(
            "Must be 8-20 chars");
    }
    if (!password.matches(
            ".*[A-Z].*") // uppercase required
        || !password.matches(".*[0-9].*")  // number required
        || !password.matches(".*[!@#$].*")) { // symbol required
        throw new InvalidPasswordException(
            "Must have uppercase, number, and symbol");
    }
    // Result: users choose P@ssw0rd1! every time
}

// GOOD: NIST-compliant policy
public void validatePassword(String password) {
    if (password.length() < 8) {
        throw new InvalidPasswordException(
            "Minimum 8 characters");
    }
    if (password.length() > 64) {
        throw new InvalidPasswordException(
            "Maximum 64 characters");
    }
    // Check against breach database
    if (breachChecker.isBreached(password)) {
        throw new InvalidPasswordException(
            "This password appears in a data breach. " +
            "Choose a different password.");
    }
    // No complexity rules. No rotation requirement.
    // Allow all characters including spaces and Unicode.
}
```

---

*Authentication category: ATH | Entry: ATH-019 | v5.0*