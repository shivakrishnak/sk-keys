---
id: ATH-030
title: "API Key Authentication Mechanics"
category: Authentication
tier: tier-2-networking-security
folder: ATH-authentication
difficulty: ★★☆
depends_on: ATH-010, ATH-031
used_by: ATH-031, ATH-047, ATH-048, ATH-055
related: ATH-010, ATH-031, ATH-048
tags:
  - security
  - authentication
  - api-key
  - machine-identity
  - intermediate
status: complete
version: 5
layout: default
parent: "Authentication"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/authentication/api-key-authentication-mechanics/
---

⚡ **TL;DR** - API keys authenticate machine-to-machine requests: the
caller includes a long random token in the request (header or query
param), the server validates it. Simple but high-maintenance: keys
must be hashed at rest (like passwords - never stored in plaintext),
rotated regularly, scoped to minimum permissions, and revocable.
The most common production failure: a key stored in a Git repository.
The second most common: a key with wildcard permissions that never
expires.

---

### 📊 Entry Metadata

| #030 | Category: Authentication | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ATH-010 Token Auth | |
| **Used by:** | ATH-031, ATH-047, ATH-048, ATH-055 | |
| **Related:** | ATH-010 Tokens, ATH-031 Bearer Tokens, ATH-048 Service Identity | |

---

### 📘 Textbook Definition

API key authentication uses a long-lived shared secret token to
identify and authenticate a client application or service. The
API key is sent with each request (typically in an Authorization
header or X-API-Key header) and validated by the server. Unlike
JWT, API keys are opaque: the server must look up the key in a
database to find the associated identity and permissions. Key
security requirements: cryptographically random generation (128+
bits), hashed storage (SHA-256 minimum), scoped to specific
operations, revocable individually, and rotated on a schedule.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│           API Key Lifecycle                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  GENERATION:                                           │
│  1. Generate random key (256-bit, url-safe base64)     │
│  2. Format: "sk_live_" + base64(32 random bytes)       │
│     (prefix helps scanners detect leaked keys)        │
│  3. Hash: store SHA-256(key) in database               │
│  4. Return raw key ONCE to caller                      │
│     (cannot retrieve it again - like a password)       │
│                                                        │
│  VALIDATION:                                           │
│  1. Extract key from request header                    │
│  2. Hash it: SHA-256(presented key)                    │
│  3. Look up hash in database                           │
│  4. Check: active, not expired, has required scope     │
│  5. Update: last_used_at timestamp                     │
│  6. Cache result in memory (avoid DB on every request) │
│     TTL: 30-60 seconds (balance perf vs revocation)    │
│                                                        │
│  ROTATION:                                             │
│  1. Generate new key, keep both active (overlap period)│
│  2. Notify caller to update their configuration        │
│  3. After confirming new key in use: revoke old key    │
│  4. Audit log both events                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - API key generation and validation**

```java
@Service
public class ApiKeyService {

    @Transactional
    public ApiKeyCreationResult createApiKey(
            String userId, String name,
            Set<String> scopes) {
        // Generate cryptographically random key
        byte[] bytes = new byte[32];
        new SecureRandom().nextBytes(bytes);
        String rawKey = "sk_live_" + Base64.getUrlEncoder()
            .withoutPadding().encodeToString(bytes);
        String keyHash = DigestUtils.sha256Hex(rawKey);

        ApiKey apiKey = new ApiKey(
            UUID.randomUUID().toString(),
            userId, name, keyHash, scopes,
            Instant.now().plus(90, ChronoUnit.DAYS));
        apiKeyRepo.save(apiKey);

        // Return raw key only once
        return new ApiKeyCreationResult(
            apiKey.getId(), rawKey); // NOT the hash
    }

    public Optional<ApiKey> validate(String rawKey,
                                      String requiredScope) {
        // Check cache first to avoid DB on every request
        String keyHash = DigestUtils.sha256Hex(rawKey);
        ApiKey key = cache.get(keyHash, () ->
            apiKeyRepo.findByKeyHash(keyHash).orElse(null));

        if (key == null || !key.isActive()
                || key.isExpired()
                || !key.getScopes().contains(requiredScope)) {
            return Optional.empty();
        }
        // Update last seen asynchronously
        asyncUpdater.updateLastUsed(key.getId());
        return Optional.of(key);
    }
}
```

**Example - BAD: storing API key in plaintext**

```java
// BAD: storing the raw key in the database
// If the database is breached: all API keys are compromised
apiKey.setKeyValue(rawKey); // storing plaintext
apiKeyRepo.save(apiKey);

// BAD: API key in URL query parameter
// Logged in proxy/server/CDN access logs
GET /api/v1/data?api_key=sk_live_abc123

// GOOD: store hash, send in header
apiKey.setKeyHash(DigestUtils.sha256Hex(rawKey));
// Header - not logged by most systems by default
Authorization: Bearer sk_live_abc123
// or
X-API-Key: sk_live_abc123
```

---

*Authentication category: ATH | Entry: ATH-030 | v5.0*