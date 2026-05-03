---
layout: default
title: "API Keys"
parent: "HTTP & APIs"
nav_order: 238
permalink: /http-apis/api-keys/
number: "0238"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP, REST, Authentication
used_by: API Gateway, OAuth2, API Rate Limiting
related: OAuth2, JWT, HMAC
tags:
  - api
  - security
  - foundational
  - http-apis
  - authentication
---

# 0238 — API Keys

⚡ TL;DR — An API key is a shared secret string that identifies and authenticates a caller to an API — simpler than OAuth2 but limited to server-to-server contexts because the key is a long-lived credential that cannot be safely embedded in client-side code.

| #0238           | Category: HTTP & APIs                  | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------- | :-------------- |
| **Depends on:** | HTTP, REST, Authentication             |                 |
| **Used by:**    | API Gateway, OAuth2, API Rate Limiting |                 |
| **Related:**    | OAuth2, JWT, HMAC                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An API is open to the internet. Any code that can reach the URL can call it. You have no way to know who is calling, no way to enforce rate limits per caller, no way to revoke access for a misbehaving client, and no way to bill customers by usage. The API is a public free-for-all.

**THE BREAKING POINT:**
A scraper hits your public API 10,000 times per second. Your server falls over. You have no idea who is doing it and no mechanism to block them. Even if you identify their IP, they rotate IPs. You need a mechanism that identifies every caller, allows you to throttle or revoke per caller, and requires minimal integration effort from the API consumer.

**THE INVENTION MOMENT:**
API keys were invented as the simplest possible authentication mechanism for machine-to-machine API access. They are: a long random string, issued per client, passed in every request, checked by the server. This is exactly why API keys exist — they are the minimal viable identity mechanism for API callers.

---

### 📘 Textbook Definition

**API key:** A long, randomly generated string (typically 32–128 characters) issued by an API provider to an API consumer as a shared secret. The consumer includes the key in every API request (typically in a header or query parameter). The provider validates the key to authenticate the request, identify the caller, and apply per-caller policies (rate limits, quotas, access controls).

**Key rotation:** The process of replacing an existing API key with a new one, typically to limit the blast radius of a compromised key or as a scheduled security practice.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An API key is a password for your code — a secret string that proves to an API who you are.

**One analogy:**

> An API key is like a library card. The library (the API server) gave you the card (the key). Every time you visit (make a request), you show the card at the desk. The librarian checks it's valid, notes which books you check out (which API calls you make), and stops you if you're over your limit. Anyone who steals your library card can use it as if they were you — so you keep it safe and can report it lost to get a new one.

**One insight:**
The critical difference between API keys and OAuth2/JWT tokens is scope and lifetime. API keys are long-lived (months/years) and broad-scoped (often full API access). This makes them powerful but dangerous: a leaked key grants full access until revoked. OAuth tokens are short-lived (minutes/hours) and narrow-scoped. This makes OAuth right for user-facing apps; API keys right for server-to-server integrations where the key can be safely stored in environment variables.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An API key is a shared secret — the provider knows it; the consumer knows it; nobody else should.
2. The key identifies the caller — it binds a request to a specific registered consumer.
3. The key is checked on every request — it is a per-request credential, not a session token.
4. Long-lived keys must be revocable — the provider must be able to invalidate a key instantly.

**HOW API KEY VALIDATION WORKS:**

```
Client Request:
  GET /api/data
  X-API-Key: sk_live_aBcD1234...

Server-side validation:
  1. Extract key from header (or query param)
  2. Hash the key: SHA-256(received_key)
  3. Look up hash in key store (DB/Redis)
  4. If not found → 401 Unauthorized
  5. If found → load associated caller metadata:
       - caller_id, plan, rate_limit, scopes
  6. Apply rate limit check for this caller_id
  7. Check requested endpoint against scopes
  8. If all pass → forward request
```

Note: **never store API keys in plain text** — store a hash (SHA-256 or bcrypt). The original key is shown to the user once at creation; the server only ever stores and compares hashes.

**THE TRADE-OFFS:**

**Gain:** Dead-simple integration — add one header, works immediately. No OAuth flows, no token refresh, no expiry handling.

**Cost:** Long-lived and broad-scoped — a leaked key has a large blast radius. Not suitable for client-side use (browser/mobile apps where the key would be visible). No native concept of "user" — an API key identifies a service, not a person.

---

### 🧪 Thought Experiment

**SETUP:**
A weather API serves 1,000 B2B customers. Each customer has a paid plan with a daily request limit.

**WITHOUT API KEYS:**
All requests look identical. Server cannot tell Customer A (1,000 req/day plan) from Customer B (10,000 req/day plan). Cannot enforce limits. Cannot send invoices. When a customer's integration has a bug and hammers the API, the server falls over for everyone.

**WITH API KEYS:**
Customer A has key `sk_a_1234`. Customer B has key `sk_b_5678`. Every request carries the caller's key. Server looks up the key → finds the plan → checks daily counter → enforces limit. Bug in Customer A's code: their counter hits 1,000 → their requests return 429; everyone else is unaffected. At month end, the server exports a CSV of request counts per key → generates invoices automatically.

**THE INSIGHT:**
API keys convert an anonymous public API into a metered, accountable, policy-enforced API — with minimal integration complexity on both sides.

---

### 🧠 Mental Model / Analogy

> An API key is a hotel key card. The hotel (API provider) issues cards to registered guests (API consumers). Every door (API endpoint) checks the card. The card doesn't say your name out loud — it just proves you're a registered guest. The hotel can deactivate your card instantly if lost (key revocation). Different card types have different access (scopes) — a conference attendee card doesn't open guest rooms.

Explicit mapping:

- "hotel key card" → the API key string
- "hotel issuing the card" → API provider generating and storing the key
- "checking the card at each door" → server-side key validation on every request
- "deactivating a card instantly" → key revocation (delete/flag key in the store)
- "different card types" → API key scopes (read-only vs. read-write vs. admin)

Where this analogy breaks down: hotel key cards encode minimal information and don't track which guest used which door. API keys are tied to rich metadata (plan, rate limits, scopes) and produce an audit trail of every request — far more powerful than a physical key card.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API key is a long secret string you include in your code when calling an API. It's like a password that tells the API who you are. The API provider gives you the key, and you keep it secret — if someone else gets it, they can make API calls in your name.

**Level 2 — How to use it (junior developer):**
Pass the API key in the `Authorization` header (preferred) or `X-API-Key` header — never in the URL query string (URLs appear in logs, browser history, and server logs). Store the key in an environment variable, not in source code. Rotate keys periodically. Handle `401 Unauthorized` (invalid key) and `429 Too Many Requests` (rate limit exceeded) in your error handling.

**Level 3 — How it works (mid-level engineer):**
On the provider side: generate the key as a cryptographically random string (at least 32 bytes from `SecureRandom`). Store only a SHA-256 hash — never the plain key. On validation: hash the incoming key, look up in the key store (Redis for performance, DB for persistence). Attach caller metadata (plan, rate limits, scopes) and apply per-caller rate limiting using a token bucket or sliding window counter keyed on `caller_id`. Log every request with the `caller_id` for audit trails.

**Level 4 — Why it was designed this way (senior/staff):**
API keys are intentionally primitive — they solve exactly one problem (identifying a server-side caller) without the complexity of OAuth2's authorization code flows, token refresh, or scope delegation. The design trade-off is: simplicity for server-to-server integrations at the cost of being inappropriate for delegated user access. The correct mental model is "API key = service identity; OAuth2 = user identity." Modern API platforms (Stripe, Twilio, GitHub) use API keys for service accounts and OAuth for user-facing integrations — precisely because the access pattern is different. A key mistake is choosing API keys for mobile or browser apps where the key would be embedded in client code and trivially extractable.

---

### ⚙️ How It Works (Mechanism)

```
API KEY LIFECYCLE:

ISSUANCE:
  1. Consumer registers (email, org, plan)
  2. Provider generates: key = base64(SecureRandom(32 bytes))
  3. Provider stores: hash = SHA-256(key), metadata
  4. Provider shows key to consumer ONCE — never stored in plain text
  5. Consumer stores key in env var / secrets manager

REQUEST:
  1. Consumer: GET /data + Header: X-API-Key: <key>
  2. Provider: extract key from header
  3. Provider: hash = SHA-256(received_key)
  4. Provider: lookup hash in Redis/DB
  5. If miss → 401 Unauthorized (don't reveal reason)
  6. If hit → load caller metadata + apply policies
  7. Log: {timestamp, caller_id, endpoint, status}
  8. Forward request to handler

REVOCATION:
  1. Mark key as revoked in store (set status=REVOKED)
  2. All subsequent requests with this key → 401
  3. Propagate to CDN/cache within seconds (TTL-based)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Consumer registers → Provider issues API key
    ↓
Consumer stores key in env var (NEVER in code)
    ↓
Consumer code: adds key to every API request header
    ↓
[API KEY VALIDATION ← YOU ARE HERE]
Server hashes key → looks up in key store
    ↓
Hit: load caller metadata (plan, limits, scopes)
    ↓
Apply rate limiting → check scope → forward to handler
    ↓
Handler processes request → returns response
    ↓
Audit log: timestamp + caller_id + endpoint + status
```

**FAILURE PATH:**
Key leaked → attacker sends requests → provider sees unusual usage → admin revokes key → all requests with that key return 401 → consumer generates new key → updates env vars.

**WHAT CHANGES AT SCALE:**
At high scale, key validation must happen in O(1) time — Redis-backed key lookup with millisecond latency is standard. Key metadata is cached (TTL 60s) to avoid DB pressure. Rate limit counters are stored in Redis with atomic increment operations to prevent distributed counter races across multiple API server instances.

---

### 💻 Code Example

**Example 1 — Sending an API key (client side):**

```java
// BAD: key in URL query param — appears in access logs!
HttpRequest bad = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/data?apikey="
        + System.getenv("API_KEY")))
    .GET().build();

// GOOD: key in Authorization header
HttpRequest good = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/data"))
    .header("Authorization",
        "Bearer " + System.getenv("API_KEY"))
    .GET().build();
```

**Example 2 — Generating and storing an API key (server side):**

```java
import java.security.SecureRandom;
import java.util.Base64;
import java.security.MessageDigest;

public class ApiKeyService {

    // Generate: cryptographically random, URL-safe
    public String generateKey() {
        byte[] bytes = new byte[32]; // 256 bits
        new SecureRandom().nextBytes(bytes);
        return "sk_live_" + Base64.getUrlEncoder()
            .withoutPadding().encodeToString(bytes);
    }

    // Hash: store only the hash, never the plain key
    public String hashKey(String rawKey) throws Exception {
        MessageDigest digest =
            MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(rawKey.getBytes());
        return Base64.getEncoder().encodeToString(hash);
    }

    // Validate: hash incoming key, lookup in store
    public Optional<CallerMetadata> validate(
            String rawKey, KeyStore store) {
        try {
            String hash = hashKey(rawKey);
            return store.findByHash(hash); // O(1) lookup
        } catch (Exception e) {
            return Optional.empty();
        }
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism      | Lifetime                    | User identity         | Client-side safe | Complexity |
| -------------- | --------------------------- | --------------------- | ---------------- | ---------- |
| **API Key**    | Long-lived (months)         | Service identity only | No               | Very low   |
| JWT            | Short-lived (minutes)       | User + claims         | Yes (public key) | Medium     |
| OAuth2         | Short-lived (1hr) + refresh | Delegated user access | Yes              | High       |
| HMAC signature | Per-request                 | Service identity      | No               | Medium     |
| mTLS           | Session                     | Certificate identity  | No               | High       |

How to choose: use API keys for server-to-server integrations where the key can be stored securely in an env var or secrets manager. Use OAuth2 when the caller acts on behalf of a human user. Use HMAC when you need request integrity (payload signing) in addition to authentication.

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                             |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "API keys are fine for mobile apps"             | Mobile apps are distributed to end users — the binary can be reverse-engineered, exposing the key. Use OAuth2 + PKCE for mobile.                                                    |
| "Store API keys in source code with .gitignore" | .gitignore only prevents adding to git — it doesn't protect against accidental commits or secret scanning tools that check history. Use environment variables or a secrets manager. |
| "API keys in URL query params are fine"         | Query params appear in web server access logs, browser history, and HTTP Referer headers. Header is the only safe location.                                                         |
| "A long API key is equivalent to OAuth2"        | Length affects brute-force resistance. OAuth2's main advantage is short expiry and scoped delegation — neither of which API keys provide.                                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Leaked API Key in Source Code**

**Symptom:** Unexpected API usage from unknown IPs. Billing anomalies. GitHub/GitLab secret scanning alert.

**Root Cause:** Key committed to version control, exposed in a public repo, or logged in plaintext.

**Diagnostic:**

```bash
# Scan git history for secrets
git log --all --full-history -p | grep -E "sk_live_|apikey|api_key"

# Or use a dedicated scanner:
trufflehog git file://. --only-verified
```

**Fix:** Immediately revoke the exposed key. Generate a new key. Store in environment variable or secrets manager (AWS Secrets Manager, HashiCorp Vault).

**Prevention:** Use a pre-commit hook (`detect-secrets`) that blocks commits containing secret patterns.

---

**2. No Key Rotation — Long-lived Key Compromise**

**Symptom:** Suspicious API calls over a long period that are hard to detect because usage looks similar to legitimate usage.

**Root Cause:** API keys used for months or years without rotation. Any historical exposure (leaked log file, old code, ex-employee) remains exploitable indefinitely.

**Diagnostic:**

```bash
# Review key age and last rotation
SELECT key_id, created_at, last_rotated_at, last_used_at
FROM api_keys
WHERE last_rotated_at < NOW() - INTERVAL '90 days';
```

**Fix:** Implement a key rotation policy. Rotate all keys older than 90 days. Automate rotation in CI/CD (most secrets managers support this).

**Prevention:** Set a maximum key lifetime (90–180 days). Send rotation reminder emails to API consumers 2 weeks before expiry.

---

**3. Missing Rate Limiting — Key Allows Unbounded Requests**

**Symptom:** A single caller consumes disproportionate resources. Server latency spikes. Other callers see degraded performance.

**Root Cause:** Rate limiting not applied per API key — all traffic treated as a global pool.

**Diagnostic:**

```bash
# Find top callers by request volume (last hour)
SELECT caller_id, COUNT(*) as requests
FROM api_access_log
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY caller_id
ORDER BY requests DESC
LIMIT 20;
```

**Fix:** Implement per-key rate limiting using Redis token bucket or sliding window. Return `429 Too Many Requests` with `Retry-After` header when limit exceeded.

**Prevention:** Rate limits should be configured at key issuance time (plan-based). Enforce at the API gateway layer before requests reach application servers.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP` — API keys are transmitted over HTTP/HTTPS; understanding request headers is required
- `REST` — API keys are most commonly used with REST APIs
- `Authentication` — API keys are one of several authentication mechanisms

**Builds On This (learn these next):**

- `API Rate Limiting` — API keys enable per-caller rate limiting
- `API Gateway` — gateways validate API keys before routing to backend services
- `OAuth2` — the next step up in API authentication for delegated user access

**Alternatives / Comparisons:**

- `OAuth2` — more complex but supports user identity and short-lived tokens; preferred for user-facing apps
- `JWT` — self-contained tokens that carry claims; can be validated without a database lookup
- `HMAC` — adds request signing on top of key identity, providing payload integrity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared secret string identifying an API   │
│              │ caller, passed in every request header    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Anonymous API callers → no rate limits,   │
│ SOLVES       │ no billing, no revocation                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Long-lived = simple but high blast radius. │
│              │ Leaked key = full access until revoked.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Server-to-server; key stored in env var   │
│              │ or secrets manager                        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Browser / mobile apps where key would be  │
│              │ exposed in client-side code               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple integration vs. long-lived secret  │
│              │ with large breach blast radius            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An API key is a password for your code   │
│              │ — treat it like one."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OAuth2 → JWT → API Gateway                │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A mobile app needs to call a third-party weather API. A junior developer proposes embedding the API key in the app's compiled binary (obfuscated with ProGuard). A senior developer objects. Trace the exact attack path by which this key could be extracted and abused. Then design a secure alternative architecture that allows the mobile app to access the weather API without exposing the key.

**Q2.** Your API platform has 50,000 registered API keys. You discover that your key validation is adding 12ms of latency to every request because it hits the database. Design a caching strategy that reduces this to under 1ms while ensuring that a revoked key stops working within 30 seconds of revocation. What are the exact consistency trade-offs in your design?
