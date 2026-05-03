---
layout: default
title: "API Keys"
parent: "HTTP & APIs"
nav_order: 238
permalink: /http-apis/api-keys/
number: "0238"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP Headers, REST, Authentication Basics, HTTPS
used_by: API Security Best Practices, Rate Limiting, Authorization, OAuth 2.0
related: OAuth 2.0, JWT, API Gateway, HMAC
tags:
  - security
  - authentication
  - api
  - http
  - beginner
  - credential
---

# 238 — API Keys

⚡ TL;DR — An API key is a secret string token that identifies and authenticates an API caller; the server validates it on every request to grant or deny access.

| #0238           | Category: HTTP & APIs                                                | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------- | :-------------- |
| **Depends on:** | HTTP Headers, REST, Authentication Basics, HTTPS                     |                 |
| **Used by:**    | API Security Best Practices, Rate Limiting, Authorization, OAuth 2.0 |                 |
| **Related:**    | OAuth 2.0, JWT, API Gateway, HMAC                                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You build a public weather API. Anyone who discovers the endpoint can call it unlimited times, scrape all your data, run up your infrastructure costs, and impersonate your legitimate users. You have no idea which client is which, which customer to bill, or who to block when abuse occurs.

**THE BREAKING POINT:**
Open APIs with no caller identity quickly become targets. Competitors scrape your data. Bots hammer your endpoints. Costs explode. Without a lightweight identity signal attached to every request, you can't enforce per-customer rate limits, audit usage, or rotate credentials after a breach.

**THE INVENTION MOMENT:**
The simplest solution: generate a long random string for each registered client, store it server-side, and require it on every API call. The client includes it in the request; the server looks it up in a database. Matched → allowed. Missing or unknown → rejected. This is an **API key**: lightweight, stateless from the client's perspective, and sufficient for most server-to-server scenarios where human password flows are impractical.

---

### 📘 Textbook Definition

An **API key** is a unique, secret string (typically 32–64 random characters) issued by an API provider to an authenticated developer or application. On every API request the client includes the key — in a header (`X-API-Key: <key>`), query parameter (`?api_key=<key>`), or request body. The server looks up the key in its store, confirms it is active and matches the intended scope, and either processes the request or returns `401 Unauthorized`. API keys authenticate **applications**, not individual end users. They are suitable for server-to-server calls where a human login flow is not possible, and for metering and rate-limiting by client identity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An API key is a secret password for programs — you include it in every request so the server knows who you are.

**One analogy:**

> An API key is like a library card. When you want to borrow a book (make an API call), you hand over your card. The librarian scans it, confirms you're a registered member, and lets you proceed. No card (missing API key) or an expired/cancelled card → access denied. The card doesn't say who you are as a person — it identifies your account. Anyone who steals your card can borrow books as if they were you.

**One insight:**
Because API keys travel with every request, they are stolen through HTTP logs, browser history, error messages, and version control. Rotation (regularly issuing new keys and revoking old ones) and scope restriction (each key grants access only to specific endpoints or methods) are the two most important mitigations.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An API key is a shared secret — both client and server hold it.
2. The server is the source of truth; the client proves identity by presenting the correct secret.
3. Any HTTP transport without TLS exposes the key to network interception — API keys REQUIRE HTTPS.
4. API keys authenticate applications (clients), not human users.

**DERIVED DESIGN:**

```
TYPICAL API KEY LIFECYCLE:

Developer Registration
    │
    ▼
POST /api/keys (authenticated as developer)
    │
Server generates: key = SecureRandom.nextBytes(32) → Base64URL
    │
Store: api_keys table
  (key_hash, developer_id, scope, rate_limit, created_at, status)
    │
Return key to developer (shown ONCE — store securely!)
    │

Request Flow:
Client                         Server
  │                              │
  │ GET /data                    │
  │ X-API-Key: sk-abc123xyz...   │
  │─────────────────────────────►│
  │                              │ Hash key, look up in DB
  │                              │ Check: active? scope? rate?
  │                              │
  │◄─────────────────────────────│
  │ 200 OK + data                │
```

**THE TRADE-OFFS:**

| Property           | API Key                   | OAuth 2.0                | JWT                    |
| ------------------ | ------------------------- | ------------------------ | ---------------------- |
| Simplicity         | Very high                 | Low                      | Medium                 |
| Revocability       | Immediate (delete DB row) | Immediate (revoke token) | Must wait for expiry   |
| User identity      | No (app only)             | Yes                      | Yes                    |
| Offline validation | No (requires DB lookup)   | No (token introspection) | Yes (verify signature) |
| Secret rotation    | Manual                    | Built-in refresh         | Re-issue               |

**Gain:** Dead-simple to implement; no OAuth flows, no token refresh logic.

**Cost:** Shared secret — leaks are catastrophic. No built-in expiry. Not user-aware. Requires secure storage by the client.

---

### 🧪 Thought Experiment

**SETUP:**
You publish an API key in a public GitHub repository by accident. The key is `sk-prod-abc123def456`. It's live for 15 minutes before you notice. What is the blast radius?

**WITHOUT ROTATION CAPABILITY:**
Anyone who found the key (GitHub search engines index within minutes) can call your API as your most privileged client. They can read your customers' data, trigger expensive operations, exhaust your rate limits, or delete resources — depending on scope. You have no way to identify which calls were malicious vs legitimate. Even after you delete the code, the git history retains the key.

**WITH ROTATION + SCOPED KEYS:**
You immediately revoke the key in your dashboard (one DB update). All subsequent requests with that key return `401`. You issue a new key. You audit the audit log for calls made during the 15-minute window — since each key carries a client identity, you can see exactly what the exposed key did. If the key had read-only scope, the attacker could only read, not modify.

**THE INSIGHT:**
API key security is not about making keys impossible to leak — it's about minimising blast radius when they do. Scope restriction, automatic rotation policies, and comprehensive audit logging transform a catastrophic breach into a containable incident.

---

### 🧠 Mental Model / Analogy

> An API key is a hotel key card. The hotel issues you a card for your stay. Every time you swipe it, the door reader checks with the server: "Is this card valid for this room at this time?" Your card only works for your room (scope). The hotel can deactivate your card instantly if you lose it. Anyone who finds your card can enter your room until it's deactivated.

- "Hotel key card" → API key string
- "Room number access" → API key scope
- "Deactivate at front desk" → revoke key in DB
- "Finds your card" → key leak via logs/git/network
- "Only works during stay" → key expiry policy

Where this analogy breaks down: hotel key cards are physically unique per stay; API keys can be shared across multiple clients (though this is bad practice and removes identity clarity).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API key is a secret password string that a program sends with every request to an API. The API checks the password and either lets you in or blocks you. It's how the API knows which customer is calling.

**Level 2 — How to use it (junior developer):**
Generate your API key in the provider's dashboard. Store it in an environment variable or secrets manager — never hardcode it. Send it in the `Authorization: Bearer <key>` header or `X-API-Key: <key>` header (check provider docs). Do not log it. Do not commit it to git. Rotate it if you suspect leakage by generating a new key and revoking the old one.

**Level 3 — How it works (mid-level engineer):**
Server-side: on key issuance, generate `key = Base64URL(SecureRandom.nextBytes(32))`. Store only the hash (`SHA-256(key)`) in the database alongside `client_id`, `scopes`, `rate_limit`, `is_active`. On each request, hash the presented key and compare with stored hash — never store the raw key. Return `401` if missing/invalid; `403` if valid but insufficient scope; `429` if rate limit exceeded. Always check scope even for valid keys.

**Level 4 — Why it was designed this way (senior/staff):**
API keys solve the bootstrap problem: OAuth 2.0 requires a prior authenticated session to issue tokens; API keys are issued through an out-of-band developer registration flow. This makes them ideal for machine-to-machine (M2M) authentication in CI/CD pipelines, backend services, and CLI tools. The weakness — shared secret with no intrinsic expiry — is mitigated by treating API keys as long-lived credentials subject to rotation policies similar to TLS certificates. Enterprise patterns use API keys scoped to environments (dev/staging/prod), combined with IP allowlisting and per-method permission grants to limit exposure.

---

### ⚙️ How It Works (Mechanism)

```
API KEY VALIDATION FLOW:
┌─────────────────────────────────────────────────────────┐
│               API KEY LIFECYCLE                         │
├────────────────┬────────────────────────────────────────┤
│ ISSUANCE       │ Server generates random bytes,         │
│                │ Base64URL-encodes, stores only hash    │
├────────────────┼────────────────────────────────────────┤
│ CLIENT USE     │ Client sends key in X-API-Key header   │
├────────────────┼────────────────────────────────────────┤
│ VALIDATION     │ Hash incoming key → lookup in DB →     │
│                │ check active + scope + rate limit      │
├────────────────┼────────────────────────────────────────┤
│ REVOCATION     │ Set is_active=false in DB →            │
│                │ next request returns 401 immediately   │
└────────────────┴────────────────────────────────────────┘

REQUEST FLOW:
Client → [GET /resource] [X-API-Key: sk-abc123]
                              │
                    hash(sk-abc123) = SHA256...
                              │
                    DB lookup: WHERE key_hash = ?
                              │
               ┌──────────────┴──────────────┐
             found                       not found
               │                             │
        check is_active=true            return 401
               │
        check scope includes            return 403
        this endpoint
               │
        check rate_limit OK             return 429
               │
        proceed with request            return 200
```

```java
// Server-side key validation (Spring Boot example)
@Component
public class ApiKeyFilter extends OncePerRequestFilter {

    private final ApiKeyRepository repo;

    @Override
    protected void doFilterInternal(HttpServletRequest req,
            HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {

        String rawKey = req.getHeader("X-API-Key");
        if (rawKey == null || rawKey.isBlank()) {
            res.sendError(401, "API key missing");
            return;
        }

        // Hash before DB lookup — never store raw key
        String keyHash = sha256Hex(rawKey);
        Optional<ApiKey> key = repo.findByKeyHash(keyHash);

        if (key.isEmpty() || !key.get().isActive()) {
            res.sendError(401, "Invalid or revoked API key");
            return;
        }

        chain.doFilter(req, res);
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW:
Developer registers → API key issued (stored hash only)
→ Client includes key in HTTP header
→ [API Key Validation ← YOU ARE HERE]
→ DB lookup (hash match + active check)
→ Scope/rate check → Request processed → 200 OK

FAILURE PATH:
Key leaked to public GitHub repo
→ Attacker uses key → Valid 200s (attacker is "authenticated")
→ Detect via: anomalous request patterns in audit log
→ Fix: immediately revoke key (DB is_active=false)
→ Issue new key; audit what was accessed during window

WHAT CHANGES AT SCALE:
At high request volume, DB lookup per request is a bottleneck.
Production systems cache key lookups in Redis (TTL: 30s–5min)
to avoid per-request DB hits. Cache must be invalidated
immediately on revocation — key the cache by hash, tombstone
on revoke instead of waiting for TTL expiry.
```

---

### 💻 Code Example

```java
// Example 1 — WRONG: Key in URL query parameter (logged everywhere)
// BAD
GET /api/data?api_key=sk-prod-abc123
// Key appears in server logs, browser history, proxy logs

// Example 1 — RIGHT: Key in header
// GOOD
GET /api/data
X-API-Key: sk-prod-abc123
// Or:
Authorization: Bearer sk-prod-abc123

// Example 2 — WRONG: Hardcoded in source code
// BAD
String API_KEY = "sk-prod-abc123def456"; // committed to git!

// Example 2 — RIGHT: From environment variable
// GOOD
String apiKey = System.getenv("MY_SERVICE_API_KEY");
if (apiKey == null) throw new IllegalStateException(
    "MY_SERVICE_API_KEY not set");

// Example 3 — Secure key generation (server-side)
import java.security.SecureRandom;
import java.util.Base64;

String generateApiKey() {
    byte[] bytes = new byte[32]; // 256 bits
    new SecureRandom().nextBytes(bytes);
    // URL-safe Base64, no padding → 43 char string
    return Base64.getUrlEncoder()
                 .withoutPadding()
                 .encodeToString(bytes);
}

// Example 4 — Hash before storing
import java.security.MessageDigest;

String hashKey(String rawKey) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    byte[] hash = digest.digest(rawKey.getBytes("UTF-8"));
    return HexFormat.of().formatHex(hash);
}
```

---

### ⚖️ Comparison Table

| Auth Method                  | Complexity | Revocable            | User Identity    | Best For                     |
| ---------------------------- | ---------- | -------------------- | ---------------- | ---------------------------- |
| **API Key**                  | Very low   | Yes (DB lookup)      | No (app only)    | M2M, simple server-to-server |
| OAuth 2.0 Client Credentials | Medium     | Yes                  | No (client only) | M2M with OAuth ecosystem     |
| JWT (Bearer token)           | Medium     | Not intrinsically    | Yes              | Stateless user auth          |
| mTLS                         | High       | Yes (CRL/OCSP)       | Yes (cert CN)    | High-security M2M            |
| Basic Auth                   | Very low   | No (password change) | Yes              | Legacy, internal only        |

**How to choose:** Use API keys for simple server-to-server integrations where developer UX matters. Use OAuth 2.0 client credentials for enterprise ecosystems with existing OAuth infrastructure. Never use Basic Auth over HTTP; never put API keys in URLs.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API keys provide authorization (what you can do) | API keys only provide authentication (who you are). Authorization requires additional scope/permission checks per endpoint                                                      |
| Storing the API key in the DB is safe            | Store only the hash (SHA-256). Raw key in DB means a DB breach exposes all clients. Only the client ever sees the raw key                                                       |
| API keys over HTTP are OK for internal services  | Internal networks are not trusted networks. Always use HTTPS. Lateral movement attacks frequently target internal API calls                                                     |
| Long API keys are more secure                    | A 32-byte (256-bit) random key from SecureRandom is already computationally unguessable. Length beyond 32 bytes adds no security — it just increases storage and transport cost |

---

### 🚨 Failure Modes & Diagnosis

**Key Leaked in Version Control**

**Symptom:** Security scanner alerts (GitHub Secret Scanning, truffleHog) fire; or anomalous API usage from unexpected IPs/user agents in audit log.

**Root Cause:** Developer hardcoded key in source file; committed to repo. Git history retains it even after deletion.

**Diagnostic Command:**

```bash
# Scan git history for secrets
trufflehog git file://. --since-commit HEAD~50

# GitHub audit log (API):
GET https://api.github.com/orgs/{org}/audit-log?phrase=secret
```

**Fix:** Immediately revoke key in dashboard. Issue new key. Scrub git history with `git filter-repo` or `BFG Repo Cleaner`. Rotate any secrets that shared the same commit window.

**Prevention:** Use `git-secrets` or `pre-commit` hooks to block commits containing key patterns before they reach the repo.

---

**Key Not Hashed in Database**

**Symptom:** DB breach exposes all API keys; attackers immediately authenticate as all clients.

**Root Cause:** Raw keys stored instead of hashes.

**Diagnostic Command:**

```sql
-- Check if keys are stored raw (should be unintelligible hashes):
SELECT key_value FROM api_keys LIMIT 5;
-- If you see recognisable "sk-" prefix patterns, they are raw
```

**Fix:** Migrate to `SHA-256(key)` storage. Force rotation of all keys (old raw-stored keys must be revoked).

**Prevention:** Store `key_hash = SHA256(rawKey)` at issuance; delete raw key from memory after returning it to user once.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP Headers` — API keys travel in headers; understand header anatomy first
- `HTTPS / TLS` — API keys are useless without transport encryption
- `Authentication Basics` — API keys are one authentication mechanism among many

**Builds On This (learn these next):**

- `OAuth 2.0` — the next layer: user-delegated authorization beyond simple app auth
- `API Security Best Practices` — comprehensive security model wrapping key management
- `Rate Limiting` — per-key rate limits enforce fair use and prevent abuse
- `API Gateway` — centralized enforcement of key validation, quota, and routing

**Alternatives / Comparisons:**

- `JWT` — self-contained token with claims; unlike API keys, verifiable without DB lookup
- `HMAC` — message authentication that signs each request with a shared secret
- `OAuth 2.0 Client Credentials` — token-based M2M auth with richer scope model

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Secret string that identifies an API      │
│              │ client on every request                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ APIs need to know which client is calling │
│ SOLVES       │ without a human login flow                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Store only the hash server-side; the raw  │
│              │ key is shown once and never stored again  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Server-to-server (M2M) API calls; CLI     │
│              │ tools; simple developer API access        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ User-facing auth (use OAuth/JWT); sending │
│              │ over plain HTTP (key exposed in transit)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simplicity vs security (shared secret,    │
│              │ no intrinsic expiry, single revocation)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A hotel key card: simple and revocable,  │
│              │  catastrophic if lost before deactivation"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ OAuth 2.0 → JWT → API Gateway Security    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An API key is a shared secret: the client knows the raw key, and the server knows its hash. If an attacker gains read access to the API key database, they cannot immediately authenticate (since they have hashes, not raw keys). But a brute-force attack on common key patterns could succeed. What specific properties of key generation prevent this attack, and how many bits of entropy are required to make brute-force computationally infeasible even with a stolen hash database?

**Q2.** Some high-traffic APIs (Stripe, Twilio) issue API keys that are themselves JWTs — self-describing tokens that embed scope and expiry but are validated by signature rather than DB lookup. What is the exact security trade-off between a database-backed API key (revocable in milliseconds) and a JWT-based API key (revocable only at expiry), and under what threat model does each approach win?
