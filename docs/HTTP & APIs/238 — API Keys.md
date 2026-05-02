---
layout: default
title: "API Keys"
parent: "HTTP & APIs"
nav_order: 238
permalink: /http-apis/api-keys/
number: "0238"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP, HTTPS
used_by: Developer APIs, Server-to-Server Integration, Webhooks
related: API Authentication, HMAC, JWT, Rate Limiting
tags:
  - api
  - api-keys
  - authentication
  - developer
  - beginner
---

# 238 — API Keys

⚡ TL;DR — An API key is a long, random secret string assigned to an API client (developer or application) that is sent with every request to identify and authenticate the caller; the server validates it against a database lookup and uses it to enforce rate limits, track usage, and control access — simpler than JWT but lacking expiry, scoping, and user identity.

┌──────────────────────────────────────────────────────────────────────────┐
│ #238 │ Category: HTTP & APIs │ Difficulty: ★☆☆ │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on: │ HTTP, HTTPS │ │
│ Used by: │ Developer APIs, S2S Integration, │ │
│ │ Webhooks │ │
│ Related: │ API Authentication, HMAC, JWT, │ │
│ │ Rate Limiting │ │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer wants to integrate with Google Maps or Stripe. The simplest mechanism would
be: no authentication (anyone can use the API — unacceptable), Basic Auth (username/password
each request), or OAuth2 (complex flow for a simple server-side integration). For
machine-to-machine integrations where there's no human user in the flow and you just
need to identify "which developer/application is calling me", OAuth2 is overkill and
session-based auth doesn't apply. You need something simple: a unique identifier the
developer can paste into their code.

**THE INVENTION MOMENT:**
API keys emerged from the developer platform era (2005–2010) when Google Maps,
Twitter, and AWS popularized public APIs with usage-based access control. The insight:
issue each registered developer a long, random string (like a password for their
application). They send it with every request. You validate it, identify their account,
track their usage, and enforce their rate limit tier.

---

### 📘 Textbook Definition

An **API key** is an opaque, randomly-generated string credential issued to an API client
(typically a developer account or application) that serves as both an identifier and
an authentication token. The client transmits the API key with every request — typically
in a custom header (`X-API-Key: ...`), the `Authorization` header, or (less preferably)
as a query parameter. The server validates the key by looking it up in a database
(or its cache) and, upon finding a match, identifies the associated account, applies
rate limits and access controls for that account, and tracks usage for billing and
analytics. API keys are shared secrets: unlike JWTs, they carry no embedded claims
and require no cryptographic validation — just a database lookup. They are typically
long-lived (until manually rotated), opaque, unique per client, and revocable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An API key is a long, random password for your application — sent with every API
request to identify your app and unlock access.

**One analogy:**

> An API key is like a library card number. When you want to borrow a book (make
> an API call), you show your library card (API key). The librarian (server) looks
> up your card in the system, confirms you're a registered patron, checks your
> borrowing limit (rate limit), and hands over the book. No authentication ceremony,
> no login flow — just show the card.

**One insight:**
API keys identify the APPLICATION, not the user. All users of your mobile app going
through "your" Stripe integration use YOUR Stripe API key. The key says "this request
came from ProjectA's server" — not "this request was made by user Alice." For
per-user identity, you need JWTs or OAuth2.

---

### 🔩 First Principles Explanation

**API KEY ANATOMY:**

```
A well-designed API key:
sk_live_EXAMPLE_KEY_REDACTED

Components:
  sk_        = prefix indicating type (secret key)
  live_      = environment indicator (vs test_)
  abc1234... = 32+ bytes of random data, URL-safe Base62 or hex encoded

Why prefix?:
  - "sk_" → secret key (don't log this!)
  - "pk_" → public key (safe to expose in browser)
  - "wh_" → webhook secret
  - Prefixes enable secret scanning tools (GitHub secret scanning, truffleHog)
    to detect leaked keys in code repositories automatically

Why long?:
  128+ bits of entropy → brute force is computationally infeasible
  At 1 billion guesses/second: 2^128 / 10^9 ≈ 3.4×10^29 seconds
  → Not guessable
```

**STORAGE — CRITICAL SECURITY:**

```
WRONG — Store raw API key in database:
  database: { api_key: "sk_live_abc123..." }
  Problem: database breach → all keys exposed → all accounts compromised

CORRECT — Store hash of API key:
  database: { key_hash: SHA256("sk_live_abc123..."), account_id: 42 }
  Validation: sha256(presented_key) == stored_hash? → lookup account

  WHY?
  Same reason you hash passwords: if the DB is breached,
  the attacker gets hashes, not raw keys. SHA256 is fast enough for
  API key hashing (unlike bcrypt for passwords — API keys are already
  high-entropy random strings, rainbow tables don't apply)

SHOW ONLY ONCE:
  On creation: return full key to user (once only)
  After that: show only last 4 chars ("...xyz0")
  User must rotate to get a new key
  (Stripe, GitHub, AWS all work this way)
```

**WHERE TO SEND THE KEY:**

```
PREFERRED — Custom header (clear intent):
  X-API-Key: sk_live_abc123...
  Advantage: doesn't appear in URL (not in server logs by default)

ALSO ACCEPTABLE — Authorization header:
  Authorization: ApiKey sk_live_abc123...

AVOID — Query parameter:
  GET /endpoint?api_key=sk_live_abc123...
  Problems: appears in server logs, browser history, Referer headers, nginx logs
  Only acceptable for webhook setup or OAuth redirect flows where header impossible
```

---

### 🧪 Thought Experiment

**SCENARIO:** API key leaked in GitHub commit.

```
Developer accidentally commits:
  config.yaml:
    stripe_key: "sk_live_abc123defghijklmn..."
  → pushes to public GitHub repo

Timeline:
  T+0s:   Git push to public repo
  T+30s:  Automated bots scan GitHub commits for "sk_live_" pattern → found!
  T+60s:  Attacker has the key; starts making API calls as the developer's account
  T+10m:  Developer notices → revokes key from Stripe dashboard
  T+10m:  Stripe: key revoked → all future requests return 401

Damage window: 10 minutes (if fast detection)
Harder case: private repo → public fork → exposed weeks later

LESSONS:
1. GitHub secret scanning (free for public repos): auto-detects common key prefixes
   and emails you within minutes
2. Use environment variables, not config files: STRIPE_KEY=sk_live_...
3. Rotate keys immediately on suspected exposure (don't wait to investigate)
4. Use test keys (sk_test_...) in any code that touches version control
5. Use scoped keys: read-only keys for read operations, full keys only in secure contexts
```

---

### 🧠 Mental Model / Analogy

> API keys are like hotel room key cards.
>
> When you check in (register as a developer), the hotel issues you a key card
> (API key). Unique to your stay (your account). The door reader (server) swipes it,
> looks up the database of valid cards, identifies your room number (account),
> and grants or denies entry.
>
> The key card doesn't contain your name — it's just an opaque credential.
> If you lose it, you get a new one issued (rotate); the old card deactivated.
> All cards for guests on the same floor might have the same access level (scopes).
> The hotel logs every door entry (API calls logged by key).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API key is a long unique code you get from an API provider. You include it in
your requests to prove you're allowed to use the API. The provider uses it to know
who's calling and to count your usage against your quota.

**Level 2 — How to use it (junior developer):**
Send in `X-API-Key` header (not query param). Store in environment variables (never
hardcode). Use different keys for test vs production. Rotate every 90 days or
immediately if exposed. The server: look up the key hash in DB (cache with Redis).
Apply rate limits and quotas by account.

**Level 3 — How it works (mid-level engineer):**
Secure API key system: generate 32-byte random key (crypto.randomBytes / SecureRandom),
prefix with type indicator. Hash with SHA256 for storage — store hash + account_id +
scopes + created_at + last_used_at. Show raw key only once at creation. For validation
performance: cache hash→account mapping in Redis (TTL 5min) — but invalidate cache
when key is rotated. Support scoped keys (read-only, write, admin) and
environment-specific keys (test, live). Emit metrics: per-key request count, error rate,
last-used timestamp (for identifying dead keys ready for rotation).

**Level 4 — Why it was designed this way (senior/staff):**
API keys are the simplest possible authentication solution for machine-to-machine
integrations — and simplicity has value. They are specifically designed for scenarios
where: no human is present (no login flow possible), the client is a trusted server-side
process (not a browser), and access is being granted to an application identity (not a
user identity). The raw simplicity comes with constraints: no built-in expiry, no scoped
claims in the token itself (scopes stored server-side), no delegation model, revocation
is instant (server-side) but rotation requires client-side code changes. The key
design choice — opaque identifier requiring server-side lookup vs self-contained signed
token (JWT) — is a stateful vs stateless tradeoff. API keys are stateful (require DB/
cache lookup) but have instant revocation. JWTs are stateless (crypto verify) but
revocation requires additional infrastructure (revocation list). For developer-facing
APIs where keys are long-lived and revocation speed is critical, API keys remain the
simplest, most widely understood solution.

---

### ⚙️ How It Works (Mechanism)

```
API KEY VALIDATION FLOW:

Client:
  GET /api/v1/data
  X-API-Key: sk_live_abc123defghijklmn

Server:
  1. Extract key from X-API-Key header
  2. Redis cache lookup: key_hash → { accountId, scopes, tier }?
     → HIT: skip DB lookup (99% of requests)
     → MISS: compute SHA256(key) → DB lookup:
       SELECT account_id, scopes, tier
       FROM api_keys
       WHERE key_hash = $1 AND revoked = false
     → found: populate Redis cache (TTL 5min)
     → not found: return 401

  3. Check scopes: does this key have "data:read" permission
     for this endpoint? → if not: 403

  4. Rate limiting: INCR key:accountId:minute → above limit? 429

  5. Pass request to handler with account context
  6. After response: UPDATE api_keys SET last_used_at = NOW() WHERE id = ?
     (async, non-blocking)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Developer onboarding:
  1. Register account at developer portal
  2. Dashboard: "Create API Key" → server generates:
     raw = "sk_live_" + secureRandom(32bytes).base62()
     hash = SHA256(raw)
     INSERT api_keys (hash, account_id, scopes, created_at)
  3. Dashboard shows raw key ONCE with "Copy now — won't be shown again"
  4. Developer copies to environment variable: export MYAPI_KEY=sk_live_...

API call in production:
  client → GET /v1/products (X-API-Key: sk_live_...)
  gateway → validate key (Redis → DB) → rate limit check
  → service → response
  → gateway logs: key_id=42, path=/v1/products, status=200, latency=45ms
  → analytics: increment daily usage counter for account_id=42
```

---

### 💻 Code Example

```java
// API Key generation and storage
@Service
public class ApiKeyService {

    private static final String PREFIX = "sk_live_";
    private final SecureRandom secureRandom = new SecureRandom();
    private final RedisTemplate<String, String> redis;
    private final ApiKeyRepository repository;

    // Generate a new API key — call this once, show result once
    public ApiKeyCreateResult createKey(Long accountId, Set<String> scopes) {
        // Generate 32 bytes = 256 bits of random data → Base62 encode
        byte[] randomBytes = new byte[32];
        secureRandom.nextBytes(randomBytes);
        String rawKey = PREFIX + Base62.encode(randomBytes);

        // Hash for storage (never store raw key)
        String hash = Sha256.hash(rawKey);

        ApiKey keyRecord = new ApiKey();
        keyRecord.setKeyHash(hash);
        keyRecord.setAccountId(accountId);
        keyRecord.setScopes(scopes);
        keyRecord.setCreatedAt(Instant.now());
        repository.save(keyRecord);

        // Return raw key ONCE — caller must display to user immediately
        return new ApiKeyCreateResult(rawKey, keyRecord.getId());
    }

    // Validate an API key — used in authentication filter
    public Optional<ApiKeyContext> validate(String rawKey) {
        if (rawKey == null || !rawKey.startsWith("sk_")) {
            return Optional.empty();
        }
        String hash = Sha256.hash(rawKey);
        String cacheKey = "apikey:" + hash;

        // Check Redis cache first
        String cached = redis.opsForValue().get(cacheKey);
        if (cached != null) {
            return Optional.of(ApiKeyContext.deserialize(cached));
        }

        // DB lookup
        return repository.findByKeyHash(hash)
            .map(key -> {
                ApiKeyContext ctx = new ApiKeyContext(key.getAccountId(), key.getScopes());
                redis.opsForValue().set(cacheKey, ctx.serialize(), Duration.ofMinutes(5));
                return ctx;
            });
    }

    // Revoke a key — must also evict cache
    public void revokeKey(Long keyId, Long accountId) {
        ApiKey key = repository.findByIdAndAccountId(keyId, accountId)
            .orElseThrow(() -> new NotFoundException("Key not found"));
        String cacheKey = "apikey:" + key.getKeyHash();
        redis.delete(cacheKey);        // Immediate invalidation from cache
        key.setRevoked(true);
        repository.save(key);
    }
}
```

---

### ⚖️ Comparison Table

| Aspect           | API Key                     | JWT                      | OAuth2 Token               |
| ---------------- | --------------------------- | ------------------------ | -------------------------- |
| **Identifies**   | Application/account         | User + claims            | User + scopes              |
| **Verification** | DB/cache lookup             | Crypto (stateless)       | Depends on type            |
| **Expiry**       | Manual rotation             | Automatic (exp)          | Automatic                  |
| **Revocation**   | Instant                     | Hard (wait for exp)      | Instant (revoke at server) |
| **Complexity**   | Very low                    | Medium                   | High                       |
| **Best for**     | Developer integrations, S2S | User auth, microservices | Delegated access           |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                            |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| API keys provide strong authentication        | They provide identification and shared-secret auth — if the key is leaked, authentication is broken. Use HMAC-signed requests for higher assurance |
| API keys in query params are fine for testing | Even in testing, query params log the key in server logs, Nginx access logs, and browser history. Use headers                                      |
| Store API keys in .env files in the repo      | .env files get committed accidentally. Use a secret manager (Vault, AWS Secrets Manager) or OS environment variables outside the repo              |
| One API key per service is secure enough      | Use separate keys per integration/client with scoped permissions — least privilege applies to API keys too                                         |

---

### 🚨 Failure Modes & Diagnosis

**Key Leaked in Git History**

Symptom:
Security scan finds a hard-coded API key in git history (even after a "fix" commit
that removed it from the current version).

Root Cause:
API key committed to source code. Removing it in a later commit doesn't remove it
from git history — every `git clone` downloads the full history.

Diagnostic / Fix:

```bash
# 1. IMMEDIATELY revoke the leaked key (before anything else)
# 2. Audit API key usage logs for suspicious activity during exposure window
# 3. Remove key from git history using BFG Repo Cleaner or git-filter-repo:
git filter-repo --replace-text <(echo 'sk_live_abc123==>REMOVED')  # replaces in all history
# Warning: this rewrites history — coordinate with all collaborators

# 4. Prevent future leaks:
# .gitignore: add .env, config/secrets/*, *.key
# pre-commit hook: truffleHog or git-secrets to scan for key patterns
# GitHub: enable secret scanning + push protection (blocks push if key detected)
```

---

### 🔗 Related Keywords

- `API Authentication` — the broader category that API keys are one solution within
- `HMAC` — an enhancement adding request signing on top of API key authentication
- `Rate Limiting` — commonly implemented per API key to enforce quotas
- `Secret Management` — best practice for storing API keys securely (Vault, AWS SM)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Long random secret identifying an app;   │
│              │ sent with every request, validated via DB│
├──────────────┼───────────────────────────────────────────┤
│ WHERE        │ X-API-Key header (preferred over query   │
│ TO SEND      │ param to avoid log exposure)              │
├──────────────┼───────────────────────────────────────────┤
│ STORAGE      │ SHA256 hash in DB, never raw             │
│              │ Show raw key once at creation only       │
├──────────────┼───────────────────────────────────────────┤
│ FORMAT       │ prefix (type/env) + 32+ bytes random    │
│              │ e.g. sk_live_abc123... (128+ bit entropy) │
├──────────────┼───────────────────────────────────────────┤
│ ROTATION     │ Every 90 days; immediately on exposure   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A random password for your app, not user"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HMAC → JWT → Rate Limiting → Secret Mgmt │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You provide a developer API and your largest enterprise customer has 50 different teams, each running their own integration. They want: (a) per-team usage analytics, (b) per-team rate limits, (c) the ability to revoke one team's access without affecting others, (d) all traffic billed to one enterprise account. Design the API key model (hierarchy, scoping, metadata) that satisfies all four requirements, and specify the database schema.
