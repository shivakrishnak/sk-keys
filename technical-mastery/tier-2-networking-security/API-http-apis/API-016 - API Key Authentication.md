---
id: API-016
title: "API Key Authentication"
category: "HTTP & APIs"
tier: tier-2-networking-security
folder: API-http-apis
difficulty: ★☆☆
depends_on: API-010, API-009
used_by: API-022, API-025, API-061
related: API-023, API-024, API-058
tags:
  - authentication
  - api-keys
  - security
  - authorization
  - foundational
status: complete
version: 4
layout: default
parent: "HTTP & APIs"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/api/api-key-authentication/
---

⚡ TL;DR - API keys are opaque tokens issued to clients
that identify and authenticate the caller on every request;
they are simple to implement but have critical security
properties that teams frequently get wrong: keys must be
treated as secrets, sent in headers not URLs, rotatable
without downtime, and scoped to minimal required permissions.

---

| #016 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Request Headers, URL Structure | |
| **Used by:** | Authentication Schemes, Rate Limiting, API Gateway | |
| **Related:** | JWT, OAuth 2.0, JWT Security | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An API without any authentication is open to anyone on
the internet. Without knowing who is making each request,
the API cannot enforce rate limits per caller, cannot
bill usage, cannot track which client is causing errors,
and cannot revoke access for a bad actor without taking
the entire API offline.

**THE BREAKING POINT:**
The simplest solution developers reach for first is "put
the username and password in the request." This works
for human users at a browser login page, but for
machine-to-machine API calls, it is problematic: the
client must store the credentials somewhere, and if the
password needs to change, every client must update their
stored password simultaneously. There is also no way
to grant limited access - the client either has the
password (full access) or not.

**THE INVENTION MOMENT:**
API keys solve the machine-to-machine credential problem
by issuing separate tokens per client. The key is not
the actual account password; it is an independent
credential scoped to a specific client, purpose, and
level of access. Revoking a key does not affect other
clients. Rotating a key can be done with zero downtime
by temporarily allowing both old and new keys. This model
was popularized by early web API providers: Google Maps
API (2005), Twitter API (2006), and Stripe (2011) made
API key auth the default for third-party API access.

---

### 📘 Textbook Definition

API key authentication is a mechanism where the API issues
a unique opaque token (the API key) to each client
application. The client includes this key in every API
request (typically in an HTTP header). The server validates
the key against its key store, identifies the client
associated with the key, and either permits or rejects
the request. API keys serve dual purposes: authentication
(proving who the client is) and authorization (enforcing
what the client is allowed to do, often through scopes
or permissions attached to the key).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An API key is a secret token that identifies your application
to an API - like a badge that says who you are and what
you are allowed to do.

**One analogy:**
> API keys are like hotel keycards. When you check in
> (register your app), the hotel (API provider) gives
> you a unique keycard (API key) that only opens your
> room (your allowed resources). If you lose the keycard
> (key compromise), the hotel deactivates just that card
> and gives you a new one - without changing the locks
> on every door. Other guests are unaffected. The keycard
> itself does not contain your identity - it is just
> a token the hotel's system looks up to find your booking.

**One insight:**
The most common API key security mistake is putting the
key in the URL: `GET /api/data?api_key=sk_live_xxxx`.
URLs are logged by proxies, CDNs, web servers, browsers,
and monitoring tools. A key in a URL is a key that is
almost certainly in someone's log file in plain text.
Always send API keys in the `Authorization` header or
a custom header (`X-API-Key`), never as a query parameter.

---

### 🔩 First Principles Explanation

**ANATOMY OF API KEY AUTHENTICATION:**

```
1. Client registration:
   Developer signs up → API provider generates key
   sk_live_YOUR_STRIPE_KEY_HERE

2. Client stores key:
   Securely in environment variables or secrets manager
   Never in source code or version control

3. Client sends key with every request:
   GET /data
   Authorization: Bearer sk_live_YOUR_STRIPE_KEY_HERE
   
   OR (Stripe, SendGrid style):
   Authorization: Bearer sk_live_...
   
   OR (custom header):
   X-API-Key: sk_live_...

4. Server validates:
   a) Extract key from request
   b) Look up key in key store (database, cache)
   c) Check: key exists? not revoked? not expired?
   d) Load associated client and permissions
   e) Check rate limits for this client
   f) Allow or reject request

5. Response:
   200 OK + data            (valid key, authorized)
   401 Unauthorized         (invalid/missing key)
   403 Forbidden            (valid key, no permission)
   429 Too Many Requests    (valid key, rate limited)
```

**KEY PROPERTIES:**

| Property | Good Practice |
|:---|:---|
| **Format** | Cryptographically random, opaque, min 32 bytes |
| **Prefix** | `sk_live_` / `sk_test_` (Stripe) for type identification |
| **Storage (server)** | Hashed (SHA-256), not plaintext |
| **Storage (client)** | Environment variable or secrets manager |
| **Transmission** | HTTPS only, in header not URL |
| **Scope** | Minimal permissions per key |
| **Expiry** | Optional but recommended for security posture |
| **Rotation** | Overlap period: old key valid during transition |

---

### 🧪 Thought Experiment

**SETUP:**
You run a weather API. A customer integrates your API
into their production mobile app and embeds the API key
in the app's source code. The app is reverse-engineered.
The API key is extracted. Someone publishes the key on
a forum.

**WHAT HAPPENS (with proper key management):**
1. You detect the abuse through rate limiting and
   anomalous usage patterns (request volume spikes,
   geographic anomaly)
2. You generate a new API key for the customer
3. The customer deploys the updated app with the new key
4. You set the old key to expire in 48 hours (grace period
   for users who have not updated)
5. After 48 hours, the old key is revoked
6. Other customers are completely unaffected

**WHAT HAPPENS (without key management):**
If the key is a shared master key for all customers, or if
revocation is not implemented, you must either:
- Take the service offline to change credentials, or
- Accept that the compromised key will be abused indefinitely

**THE INSIGHT:**
API key design is primarily about revoking and rotating
keys without downtime. A key that cannot be revoked
independently of all other clients is not a real API key -
it is a shared password with extra steps.

---

### 🧠 Mental Model / Analogy

> API keys are like physical building access cards in a
> corporate office. Each employee (client) has their own
> unique card (API key). The card gets them into specific
> areas (permissions/scopes) - not necessarily everywhere.
> If an employee leaves (client deregisters) or a card is
> lost (key compromised), security deactivates just that
> card. Other employees are unaffected. The security system
> knows who accessed which door and when (audit log).
> No two cards are alike. The card itself does not say who
> you are - it just has a unique ID that the security
> system looks up.

Mapping:
- "Employee" → API client/application
- "Access card" → API key
- "Specific areas" → API scopes/permissions
- "Deactivating a card" → revoking an API key
- "Door access log" → API request audit log

Where this analogy breaks down: API keys are digital and
can be copied exactly. A physical access card cannot be
trivially duplicated. Once an API key is known to an
attacker, they have a perfect copy, which is why
transmission security (HTTPS, headers not URLs) matters.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An API key is a long password for your application. When
your app calls a weather API or payment API, it sends
this key with every request so the API knows which app
is calling. If you lose it or someone else gets it,
you can get a new one without affecting anyone else.

**Level 2 - How to use it (junior developer):**
Store the key in an environment variable (`API_KEY`),
never in code. Send it in the `Authorization` header as
`Bearer {key}` or in `X-API-Key: {key}`. Always use HTTPS.
Never put it in URLs - logs capture URLs. When the API
returns 401, the key is invalid or missing; 403 means
the key is valid but lacks permission.

**Level 3 - How it works (mid-level engineer):**
Server receives request, extracts key from header. Looks
up key in a hash table or database (Redis for speed).
Compares against stored hash (SHA-256 of the raw key;
never store raw keys). Loads client metadata: name,
permissions, rate limit tier. Applies rate limiting before
processing. Returns 401 for unknown keys, 403 for known
keys that lack the required permission. Every request
path has this validation applied, typically as middleware.

**Level 4 - Why it was designed this way (senior/staff):**
API keys trade security complexity for operational
simplicity. They are stateless on the client (no OAuth
flow, no token refresh, no PKCE) and require only one
lookup per request on the server (cacheable in Redis
with TTL). The trade-off: keys are long-lived (OAuth
access tokens expire in 1 hour; API keys may last years).
Long-lived credentials increase the blast radius of a
compromise. Mitigation: scoped keys, expiration policies,
key rotation tooling, and anomaly detection. Stripe's
model (live vs test key prefixes, webhook-specific keys,
restricted keys with field-level permissions) shows how
far key granularity can be taken.

**Level 5 - Mastery (distinguished engineer):**
At scale, API key validation is a hot path that cannot
afford a database round-trip on every request. The canonical
solution: cache key metadata in Redis with a TTL of
5-60 minutes. On cache miss, fetch from DB and populate
cache. On key revocation, publish an invalidation event
to all cache nodes. This creates eventual consistency
between revocation and enforcement. The gap (TTL duration)
is the maximum time a revoked key remains valid. For
high-security APIs, key rotation and revocation can be
made near-real-time using distributed caches with pub/sub
invalidation. For very high-throughput APIs, key validation
moves into the API gateway or sidecar proxy to avoid
adding a cache round-trip to every application handler.

---

### ⚙️ How It Works (Mechanism)

**Key validation flow:**

```
Request arrives:
  GET /data
  Authorization: Bearer sk_live_4xT9m2...

           │
           ▼
  Auth Middleware:
  1. Extract key from header
  2. Compute: token_hash = SHA256(key)

           │
           ▼
  Cache Lookup (Redis):
  key: "apikey:{token_hash}"
  hit → client metadata (id, scopes, rate limit tier)
  miss → DB lookup → populate cache with TTL=60min

           │
           ▼
  Validation:
  - Key found? (else 401)
  - Key not revoked? (else 401)
  - Key not expired? (else 401)
  - Required scope granted? (else 403)

           │
           ▼
  Rate Limiter:
  - Check requests in current window for this client
  - Over limit? 429 Too Many Requests
  - Under limit? increment counter

           │
           ▼
  Request Handler (business logic)
  → 200 OK + response
```

```mermaid
flowchart TD
    REQ[Request + Authorization: Bearer KEY] --> MW[Auth Middleware]
    MW --> HASH[Compute SHA256 of key]
    HASH --> CACHE{Redis Cache Hit?}
    CACHE -- Yes --> META[Load client metadata]
    CACHE -- No --> DB[Lookup in DB]
    DB --> CACHE_WRITE[Write to Redis cache TTL=60min]
    CACHE_WRITE --> META
    META --> VALID{Valid + Not Revoked?}
    VALID -- No --> 401[401 Unauthorized]
    VALID -- Yes --> SCOPE{Has required scope?}
    SCOPE -- No --> 403[403 Forbidden]
    SCOPE -- Yes --> RATE{Under rate limit?}
    RATE -- No --> 429[429 Too Many Requests]
    RATE -- Yes --> HANDLER[Business Logic → 200 OK]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Full API key lifecycle:**

```
1. PROVISIONING:
   Developer registers → System generates:
   raw_key = "sk_live_" + random_bytes(32).hex()
   hash = SHA256(raw_key)
   Store: {hash, client_id, scopes, created_at}
   Show raw_key to user ONCE (never store raw)

2. CLIENT STORAGE:
   Developer stores in:
   .env file: API_KEY=sk_live_...
   Or: AWS Secrets Manager, HashiCorp Vault

3. REQUEST:
   curl https://api.example.com/data \
     -H "Authorization: Bearer $API_KEY"

4. VALIDATION:
   Server validates on every request (see mechanism above)

5. ROTATION:
   a) User requests new key
   b) New key generated, old key marked "rotating" (still valid)
   c) Client updates stored key
   d) Old key revoked (24-48 hour grace period)
   e) No downtime; no coordination needed

6. REVOCATION:
   User or admin revokes key
   Key status set to "revoked" in DB
   Cache entries expire within TTL
   Future requests with this key → 401
```

---

### 💻 Code Example

**Example 1 - BAD: Key in URL (logged in plain text)**

```python
# BAD: API key in URL - will appear in server logs

@app.route("/data")
def get_data():
    api_key = request.args.get("api_key")  # from URL
    if not api_key:
        return jsonify({"error": "missing key"}), 401
    # URL is logged: GET /data?api_key=sk_live_xxxx
    # Key is now in your nginx log, CloudFront log,
    # browser history, and any proxy in between
```

**Example 1 - GOOD: Key in Authorization header**

```python
# GOOD: API key in Authorization header

@app.route("/data")
def get_data():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "missing key"}), 401

    api_key = auth.removeprefix("Bearer ").strip()
    if not api_key:
        return jsonify({"error": "invalid key"}), 401

    client = validate_api_key(api_key)
    if client is None:
        return jsonify({"error": "invalid key"}), 401

    return jsonify(fetch_data(client.id))
```

---

**Example 2 - Server-side key validation with hashing**

```python
import hashlib
import secrets
import redis
from datetime import datetime

r = redis.Redis()

def generate_api_key(client_id: str,
                     scopes: list[str]) -> str:
    """Generate and store a new API key.
    Returns raw key (show once, then discard)."""
    raw_key = "sk_live_" + secrets.token_hex(32)
    key_hash = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

    # Store HASH only, never raw key
    db.api_keys.insert({
        "hash": key_hash,
        "client_id": client_id,
        "scopes": scopes,
        "created_at": datetime.utcnow(),
        "revoked": False
    })
    return raw_key  # shown to user once


def validate_api_key(raw_key: str) -> dict | None:
    """Validate key. Returns client dict or None."""
    key_hash = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

    # Check Redis cache first
    cache_key = f"apikey:{key_hash}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)  # cache hit

    # Cache miss: check DB
    record = db.api_keys.find(hash=key_hash)
    if not record or record["revoked"]:
        # Cache negative result for 60s
        r.setex(cache_key, 60, "invalid")
        return None

    client_data = {
        "client_id": record["client_id"],
        "scopes": record["scopes"]
    }
    # Cache for 5 minutes
    r.setex(cache_key, 300, json.dumps(client_data))
    return client_data


def revoke_api_key(key_hash: str) -> None:
    """Revoke key. Cache will expire naturally."""
    db.api_keys.update(
        {"hash": key_hash},
        {"revoked": True, "revoked_at": datetime.utcnow()}
    )
    # Delete from cache immediately
    r.delete(f"apikey:{key_hash}")
```

---

**Example 3 - Middleware for Flask**

```python
from functools import wraps

def require_api_key(required_scope: str = None):
    """Decorator: require valid API key."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({
                    "error": "unauthorized",
                    "message": "API key required in "
                               "Authorization: Bearer header"
                }), 401

            raw_key = auth.removeprefix("Bearer ").strip()
            client = validate_api_key(raw_key)

            if client is None:
                return jsonify({
                    "error": "unauthorized",
                    "message": "Invalid or revoked API key"
                }), 401

            if required_scope and \
               required_scope not in client["scopes"]:
                return jsonify({
                    "error": "forbidden",
                    "message": f"Scope '{required_scope}' "
                               "required"
                }), 403

            g.client_id = client["client_id"]
            g.scopes = client["scopes"]
            return f(*args, **kwargs)
        return decorated
    return decorator

# Usage:
@app.route("/orders")
@require_api_key(required_scope="orders:read")
def list_orders():
    return jsonify(db.orders.for_client(g.client_id))
```

---

### ⚖️ Comparison Table

| Auth Method | Mechanism | Expiry | Stateless? | Best For |
|:---|:---|:---|:---|:---|
| **API Key** | Opaque token in header | Long-lived (months/years) | Server lookup | M2M, simple integrations |
| **JWT** | Signed token with claims | Short-lived (minutes/hours) | Yes (verify signature) | User auth, microservices |
| **OAuth 2.0** | Access token + refresh token | Access: short; Refresh: long | Access: yes | Delegated user access |
| **mTLS** | Client certificate | Certificate expiry | Yes (cert verify) | High-security internal services |
| **Basic Auth** | Base64(user:pass) | Session-based | No | Legacy, simple internal APIs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| API keys are "less secure" than JWT | API keys and JWT serve different purposes. API keys are simpler to revoke (server-side lookup). JWT cannot be revoked without a denylist. API keys can be more secure when properly scoped and stored. |
| `X-API-Key` header is the standard | Both `Authorization: Bearer {key}` and `X-API-Key: {key}` are common. `Authorization: Bearer` is more semantically correct and aligns with OAuth 2.0 bearer token format. |
| API keys in `.env` files are safe in production | `.env` files are safe locally but must never be committed to version control. In production, use a secrets manager (AWS Secrets Manager, HashiCorp Vault, Kubernetes Secrets). |
| SHA-256 hashing API keys is optional | Storing raw API keys is equivalent to storing plaintext passwords. If your database is breached, all keys are compromised. Always store the SHA-256 hash of the key, like password hashing (but with SHA-256, not bcrypt - keys are already high entropy). |

---

### 🚨 Failure Modes & Diagnosis

**API key leaked in Git repository**

**Symptom:** Unexpected API usage, billing spikes, or
abuse alert. Security scan finds API key in commit history.

**Root Cause:** Developer committed a `.env` file or
hard-coded the key in source code. Git history preserves
the key even after removal.

**Diagnostic Command / Tool:**

```bash
# Scan git history for API key patterns
git log --all --full-history -- "*.env" "*.py" "*.js"
git diff --name-only $(git rev-list HEAD)

# Use git-secrets or truffleHog
trufflehog filesystem . --json | head -50
```

**Fix (immediate):**
1. Revoke the compromised key immediately
2. Issue a new key and update production config
3. If commits exist: `git-filter-repo` to rewrite history
   (destructive - coordinate with team)
4. Add `.env` to `.gitignore` and pre-commit hooks
   to scan for secrets

---

**Key in URL appearing in logs**

**Symptom:** Security audit finds API keys in web server
access logs, CDN logs, or monitoring dashboards.

**Root Cause:** Client sends key as a query parameter:
`/api/data?api_key=sk_live_...`. Server logs the full URL.

**Diagnostic Command / Tool:**

```bash
# Search access logs for API key patterns
grep -E 'api_key=sk_(live|test)_' \
  /var/log/nginx/access.log | head -5

# Check if logs contain Authorization header
# (they should not, if logs are configured correctly)
grep "Authorization" /var/log/nginx/access.log | head -3
```

**Fix:** Update the API to reject keys in query parameters.
Update clients to use `Authorization: Bearer` header.
Rotate any keys that appeared in logs.

---

**Key database breach exposes all client credentials**

**Symptom:** Database backup or export is compromised.
All API keys may be exposed if stored as plaintext.

**Diagnostic Command / Tool:**

```sql
-- Check if keys are stored as plaintext or hashed
SELECT key_value, length(key_value) FROM api_keys LIMIT 5;
-- Plaintext: "sk_live_4xT9m2..." (human-readable)
-- Hashed: "a3f7d9..." (64-char hex for SHA-256)
```

**Fix:** Immediately rotate all keys. Run a migration to
hash all stored keys (extract raw key, hash, replace in DB).
For future keys: always store hashed, show raw key only at
creation time.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Request Headers and Response Headers` - API keys
  travel in the `Authorization` header
- `URL and URI Structure` - why keys must be in headers,
  not URL query parameters (URL logging risk)

**Builds On This (learn these next):**
- `Authentication Schemes (Bearer Token, Basic Auth)` -
  API keys are one form; Bearer is the header convention
- `JWT (JSON Web Token)` - self-contained alternative
  to opaque API keys
- `OAuth 2.0 Flows` - delegated authorization using tokens,
  not static API keys

**Alternatives / Comparisons:**
- `JWT Security` - how JWT and API keys compare for
  different threat models

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Opaque token issued per client to         │
│              │ authenticate machine-to-machine API calls │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Who is calling my API? Allows per-client  │
│ SOLVES       │ rate limits, billing, and revocation      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Keys in URLs → keys in logs. Always use   │
│              │ Authorization: Bearer header over HTTPS   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ M2M API access, third-party integrations, │
│              │ simple API auth without user delegation   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need per-user delegation (use OAuth 2.0); │
│              │ need short-lived credentials (use JWT)    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Key in URL, key in source code, storing   │
│              │ raw key in database (hash it)             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Simple to use vs long-lived, server       │
│              │ lookup required per request               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "API keys in headers, hashed in DB,       │
│              │ rotatable per-client, scoped to minimum." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bearer Token Auth → JWT → OAuth 2.0       │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. NEVER put API keys in URLs. URLs are logged everywhere.
   Use `Authorization: Bearer {key}` in headers, always
   over HTTPS.
2. Store API key hashes (SHA-256), not raw keys. If your
   database leaks, raw keys are immediately usable by
   attackers. Hashes are not.
3. Keys must be independently revocable and rotatable
   with zero downtime. If revoking one key takes everything
   offline, your key design is wrong.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Credentials should be independently revocable. Any system
where revoking one set of credentials requires changing
credentials for all users is fragile - a single compromise
forces a disruptive global rotation. API keys solve this
by issuing independent tokens per client. The same principle
applies to: SSH authorized keys (revoke one key without
changing the server's host key), IAM roles (revoke one
role without affecting other roles), X.509 certificates
(revoke one certificate without changing the CA). The
pattern: issue separate credentials to each principal,
each independently revocable.

**Where else this pattern appears:**
- OAuth 2.0 refresh tokens: per-client, independently
  revocable
- AWS IAM access keys: per-user, can be rotated without
  affecting other users' keys
- SSH deploy keys: per-repository, per-service, independently
  revocable

---

### 💡 The Surprising Truth

The phrase "API key" is not defined by any standard.
The closest standard is RFC 6750 (Bearer Token Usage in
OAuth 2.0), which defines how opaque tokens should be
sent in HTTP requests. Many APIs call their tokens "API
keys" when they are technically OAuth 2.0 bearer tokens,
personal access tokens, or service account credentials.
The naming ambiguity causes real confusion: a Stripe "API
key" has very different rotation semantics from a GitHub
"personal access token" from a Google "service account
key." The underlying mechanism (opaque token in header,
validated server-side) is the same - but the management
lifecycle varies significantly. When a vendor says "API
key," always ask: what is the expiry? Can it be scoped?
How is rotation handled?

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** Why API keys must be sent in headers and
   not URLs, with specific reference to which systems
   log full URLs in plain text.
2. **DEBUG** Given a security audit finding API keys in
   nginx access logs, trace the root cause to the client
   sending keys as query parameters and propose the fix.
3. **DECIDE** Explain when to use an API key versus OAuth
   2.0 versus JWT, with specific criteria for each choice.
4. **BUILD** Implement API key generation (with prefix,
   random bytes), SHA-256 hashing for storage, Redis cache
   for validation, and scope checking - as a Flask middleware.
5. **EXTEND** Design a key rotation policy for a production
   API with 10,000 clients, including: grace period duration,
   dual-key acceptance window, cache TTL impact, and
   client notification mechanism.

---

### 🎯 Interview Deep-Dive

**Q1: A developer commits an API key to a public GitHub
repository. What steps do you take?**

*Why they ask:* Tests incident response and understanding
of the security blast radius.

*Strong answer includes:*
- Immediate: revoke the compromised key, issue a new one
- Determine exposure window: when was it committed? when
  was the repo made public? has the key been used since?
- Review audit logs for unexpected API usage during the
  exposure window
- If the key was used maliciously: assess what data was
  accessed and whether breach notification is required
- Clean the Git history (git-filter-repo or BFG Repo
  Cleaner), though the key was already public
- Add pre-commit hook or CI check to scan for secrets
  (git-secrets, detect-secrets) to prevent recurrence
- Update developer documentation with key storage policy

**Q2: How would you implement API key validation in a
high-traffic API that receives 50,000 requests per second?**

*Why they ask:* Tests understanding of the hot path
performance challenge and caching strategy.

*Strong answer includes:*
- Database lookup per request would be ~1-10ms per request
  = infeasible at 50k RPS (50k concurrent DB queries)
- Solution: Redis cache with key hash as the cache key
- Cache hit: ~0.1-0.5ms (in-memory, single round-trip)
- Cache miss: DB lookup + populate cache (TTL = 5-30 min)
- Revocation: delete from cache immediately; max lag =
  remaining TTL
- At extreme scale: move validation to API gateway layer
  (nginx module, Envoy external auth) to keep it out of
  application code entirely
- Key insight: cache TTL = eventual consistency window for
  revocation. Choose based on security requirements.

**Q3: What are the differences between API keys, JWT,
and OAuth 2.0 tokens? When would you choose each?**

*Why they ask:* Tests breadth of auth knowledge and
ability to match mechanism to use case.

*Strong answer includes:*
- API keys: opaque, long-lived, server-side lookup required.
  Best for M2M, third-party integrations, simple auth.
  Easy to revoke. Cannot be validated without a server
  round-trip.
- JWT: self-contained, signed, short-lived (15-60 min).
  Any service can validate by verifying signature
  (no DB lookup). Cannot be revoked without a denylist.
  Best for microservice auth, user sessions.
- OAuth 2.0: delegated access. Access token (short-lived)
  + refresh token (long-lived). Best when a third-party
  app needs to act on behalf of a user. The OAuth flow
  gives the user control over what access to grant.
- Choice: API key for simple M2M. JWT for user sessions
  or microservice auth where revocation is not critical.
  OAuth 2.0 for delegated user authorization.
