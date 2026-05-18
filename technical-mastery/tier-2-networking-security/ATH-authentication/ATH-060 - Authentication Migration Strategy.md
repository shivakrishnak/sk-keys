---
id: ATH-060
title: "Authentication Migration Strategy"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★★
depends_on: ATH-007, ATH-008, ATH-022, ATH-056
used_by: ATH-065
related: ATH-056, ATH-057, ATH-065
tags:
  - security
  - authentication
  - migration
  - strategy
  - advanced
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 60
permalink: /technical-mastery/authentication/authentication-migration-strategy/
---

⚡ **TL;DR** - Migrating authentication - from custom auth to
a dedicated IdP, from MD5 passwords to bcrypt, or from session
cookies to JWT - is high-risk because a mistake locks out all
users. The safe pattern: run both old and new systems in parallel
during a transition window, migrate users gradually (on next
login, re-hash the password using the new scheme), verify before
cutting over, and maintain a rollback path. Never do a "big bang"
auth migration - it always causes incidents.

---

### 📊 Entry Metadata

| #060 | Category: Authentication | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATH-007 Password Hashing, ATH-008 Session-Based, ATH-022 OIDC, ATH-056 Enterprise | |
| **Used by:** | ATH-065 | |
| **Related:** | ATH-056 Enterprise Arch, ATH-057 IdP Design, ATH-065 Trust Chain | |

---

### 📘 Textbook Definition

Authentication migration is the process of transitioning an
existing system from one authentication mechanism to another
with minimal disruption to active users. Common scenarios:
(1) password hashing algorithm upgrade (MD5/SHA1 to bcrypt/Argon2),
(2) session-based to token-based (from cookies to JWT),
(3) custom auth to dedicated IdP (Okta, Keycloak),
(4) single-factor to multi-factor (adding MFA to existing
password auth), (5) proprietary SSO to standards-based OIDC.
Each migration requires: parallel running (dual auth paths),
gradual rollout (not all users at once), verification at each
stage, user communication, and a tested rollback procedure.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authentication Migration Patterns              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PATTERN 1: On-Login Rehashing                         │
│  (MD5 -> bcrypt upgrade)                               │
│  1. Add `hash_version` column to users table           │
│  2. Login attempt with old hash:                       │
│     - Verify using MD5 (old scheme)                    │
│     - If valid: re-hash with bcrypt, store new hash    │
│     - Set hash_version = 2                             │
│  3. Over time: all active users migrated               │
│  4. After N months: force-expire unmigrated accounts   │
│  Zero downtime, transparent to users                   │
│                                                        │
│  PATTERN 2: IdP Migration (custom -> Okta)             │
│  1. Configure Okta with all existing users (SCIM sync) │
│  2. New users: create in Okta only                     │
│  3. Add Okta OIDC login path alongside existing        │
│  4. Feature flag: 10% of users -> Okta login           │
│  5. Monitor error rates, increase gradually            │
│  6. 100% on Okta: remove old auth code path            │
│  7. Decommission old auth database                     │
│                                                        │
│  PATTERN 3: Session -> JWT                             │
│  1. Issue both: session cookie + JWT on login          │
│  2. Services: accept both, prefer JWT                  │
│  3. Gradually shift clients to use JWT                 │
│  4. Remove session cookie issuance                     │
│  5. Remove session middleware                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - On-login password rehashing migration**

```java
@Service
public class LegacyAwareAuthService {

    public boolean authenticate(String email,
                                 String rawPassword) {
        User user = userRepo.findByEmail(email)
            .orElseThrow(() ->
                new BadCredentialsException("Invalid"));

        if (user.getHashVersion() == 1) {
            // LEGACY: MD5 hash (insecure)
            if (!legacyMd5Matches(rawPassword,
                    user.getPasswordHash())) {
                return false;
            }
            // Transparently upgrade to bcrypt
            // User sees nothing - just logs in normally
            user.setPasswordHash(
                bcryptEncoder.encode(rawPassword));
            user.setHashVersion(2);
            userRepo.save(user);
            log.info("Migrated user {} to bcrypt",
                email);
        } else {
            // CURRENT: bcrypt
            if (!bcryptEncoder.matches(rawPassword,
                    user.getPasswordHash())) {
                return false;
            }
        }
        return true;
    }
    // After 6 months: force-expire users still on v1
    // (they haven't logged in - likely inactive accounts)
    // Send email: "Please reset your password"
}
```

---

*Authentication category: ATH | Entry: ATH-060 | v5.0*