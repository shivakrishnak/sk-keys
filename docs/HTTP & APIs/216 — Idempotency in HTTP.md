---
layout: default
title: "Idempotency in HTTP"
parent: "HTTP & APIs"
nav_order: 216
permalink: /http-apis/idempotency-in-http/
number: "0216"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP Methods (GET, POST, PUT, PATCH, DELETE), REST, HTTP Status Codes
used_by: API Design Best Practices, Retry Strategy, Idempotency Key
related: REST, API Rate Limiting, Retry with Backoff
tags:
  - api
  - http
  - protocol
  - intermediate
  - bestpractice
---

# 216 — Idempotency in HTTP

⚡ TL;DR — An idempotent HTTP operation produces the same result no matter how many times it is called, making it safe to retry without fear of duplicate side effects.

| #216 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP Methods (GET, POST, PUT, PATCH, DELETE), REST, HTTP Status Codes | |
| **Used by:** | API Design Best Practices, Retry Strategy, Idempotency Key | |
| **Related:** | REST, API Rate Limiting, Retry with Backoff | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Networks are unreliable. A client sends a `POST /orders` request and gets
no response — the connection timed out. Did the server receive the request?
Was the order created? The client has no idea. If it retries, it risks creating
a duplicate order. If it doesn't retry, the user's order might be lost.
Without idempotency guarantees, every timeout or network error forces a
painful decision: retry and risk duplication, or give up and risk data loss.

**THE BREAKING POINT:**
A payment service processes a charge. The client POSTs the charge, the server
deducts the money, then crashes before sending the response. The client retries.
Now the customer is charged twice. Support tickets flood in. Trust is destroyed.
Without idempotency, distributed systems become unreliable under any failure.

**THE INVENTION MOMENT:**
This is exactly why **idempotency in HTTP** is a first-class design concern:
define which operations can be retried safely, and for non-safe ones (like payments),
build explicit idempotency mechanisms using tokens.

---

### 📘 Textbook Definition

**Idempotency** in HTTP means that making the same request multiple times
produces the same server state as making it once. HTTP/1.1 (RFC 7231) defines
GET, HEAD, PUT, and DELETE as idempotent; POST and PATCH are not idempotent
by default. "Safe" methods (GET, HEAD) additionally have no server side effects.
Idempotency is a guarantee on _server state_, not on _response_ — a DELETE may
return 200 on first call and 404 on second, yet both calls leave the server in
the same state (resource absent).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Idempotency means pressing the elevator button ten times has the same result as pressing it once.

**One analogy:**

> Pressing an elevator button is idempotent: no matter how many times you press it,
> the elevator will come once. But submitting a payment form is NOT idempotent:
> each submission charges you again. APIs need to be designed like elevator buttons
> for anything that can be retried over a network.

**One insight:**
Idempotency is about server _state_, not the response code. DELETE `/items/42`
is idempotent: first call removes the item (200), second call finds nothing to
remove (404). Different response, same server state. This distinction matters
for retry logic — clients can safely retry all idempotent methods on timeout.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Networks can fail at any point — request may arrive 0, 1, or N times.
2. Safe retry is only possible when repeated execution is side-effect-free.
3. For non-idempotent operations, the client must know whether the first request succeeded.
4. Explicit idempotency keys convert non-idempotent operations into idempotent ones.

**DERIVED DESIGN — HTTP Method Idempotency Map:**

```
Method   | Idempotent | Safe | Notes
---------|------------|------|-------------------------------
GET      | ✓          | ✓    | Read-only, no side effects
HEAD     | ✓          | ✓    | Like GET but no body
PUT      | ✓          | ✗    | Full replace: PUT same body = same result
DELETE   | ✓          | ✗    | Delete twice = still deleted
POST     | ✗          | ✗    | Creates new resource each call
PATCH    | ✗          | ✗    | Partial update — depends on impl
OPTIONS  | ✓          | ✓    | Metadata query
```

**Making POST Idempotent:**
The `Idempotency-Key` header pattern: client generates a unique UUID per
logical operation. Server stores the key + result. On retry with same key,
server returns cached result without re-executing the operation.

**THE TRADE-OFFS:**

- Gain: safe retry on any network failure → better reliability.
- Cost: idempotency key storage requires shared state (Redis, DB) — adds latency.
- Gain: reduces duplicate side effects (charges, emails, orders).
- Cost: key expiry management — how long to store idempotency results.

---

### 🧪 Thought Experiment

**SETUP:**
A payment API endpoint `POST /v1/charges` processes a $100 charge.
The client has a 5-second timeout. The network is unreliable.

**WITHOUT IDEMPOTENCY:**
Request sent → server processes charge → network drops response → client times
out → client retries → server processes ANOTHER $100 charge → customer charged
$200 → chaos.

**WITH IDEMPOTENCY KEY:**
Client sends `POST /v1/charges` with header `Idempotency-Key: uuid-abc-123`.
Server processes charge, stores `{uuid-abc-123: {status: 200, charge_id: ch_99}}`.
Network drops response. Client retries with SAME `Idempotency-Key: uuid-abc-123`.
Server finds key in store → returns cached `{status: 200, charge_id: ch_99}`.
No second charge. Customer charged exactly once.

**THE INSIGHT:**
The idempotency key converts a stateless HTTP verb into a stateful operation
with a deduplication guarantee. The client controls the key; the server provides
the guarantee. This is the foundation of reliable distributed payments.

---

### 🧠 Mental Model / Analogy

> Think of idempotency like a light switch vs a doorbell. A light switch is
> idempotent: flipping it "on" when it's already on has no effect. A doorbell
> is NOT idempotent: pressing it 3 times rings 3 times. Good API design makes
> everything a light switch where possible — and adds a "don't ring twice"
> mechanism for doorbells.

- "Light switch" → idempotent operations: PUT, DELETE, GET
- "Doorbell" → POST without idempotency key
- "Don't ring twice mechanism" → Idempotency-Key header + server-side dedup store
- "Checking if already on" → server looks up idempotency key before processing

**Where this analogy breaks down:** A real light switch has physical state.
HTTP idempotency is a logical guarantee — the server must actively implement it
for POST operations. The HTTP spec only guarantees idempotency for PUT/DELETE/GET.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Idempotency means you can click "submit" multiple times and the action only
happens once. It's the property that makes retrying safe — like re-sending an
email where the server knows to ignore duplicates.

**Level 2 — How to use it (junior developer):**
Use GET for reads (always idempotent). Use PUT for full resource replacement
(idempotent). Use DELETE for removal (idempotent). Avoid using POST where PUT
works. For unavoidable POSTs (payments, email sends), add an `Idempotency-Key`
header using a UUID generated client-side before the first attempt.

**Level 3 — How it works (mid-level engineer):**
Server-side idempotency key implementation: before processing, check Redis/DB
for the key. If found, return cached response. If not found, process, store
`{key: response}` atomically, return response. Key TTL: 24h–7d depending on
retry window. Stripe uses this pattern. The `Idempotency-Key` is a de facto
standard header (RFC 8725 candidate). Implementation must be atomic: check-then-act
must not race with a concurrent request with the same key.

**Level 4 — Why it was designed this way (senior/staff):**
The HTTP spec's idempotency definitions (PUT, DELETE) are _semantic contracts_,
not technical enforcement. The spec says "a server SHOULD BE idempotent" —
nothing prevents a broken PUT implementation from creating duplicates. The
real value is as a contract for intermediaries (proxies, CDNs, load balancers):
an idempotent request can be safely retried by any intermediary that receives
no response. This is why GET requests are sometimes automatically retried by
HTTP clients, but POST requests never are. For payments and stateful POSTs,
the idempotency key pattern emerged from Stripe's API design (circa 2013)
and has become the industry standard, though it remains outside the HTTP spec.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│    IDEMPOTENCY KEY FLOW                                 │
├─────────────────────────────────────────────────────────┤
│  Client: generate UUID before first attempt             │
│  key = "550e8400-e29b-41d4-a716-446655440000"          │
│                    ↓                                    │
│  POST /charges                                          │
│  Idempotency-Key: 550e8400-...                         │
│  {"amount": 100, "currency": "USD"}                    │
│                    ↓                                    │
│  Server checks key store (Redis):                      │
│   key found? → return cached response (no processing)  │
│   key not found? → process + store + return response  │
│                    ↓                                    │
│  Network drops — client gets no response (timeout)     │
│                    ↓                                    │
│  Client RETRIES with SAME Idempotency-Key              │
│                    ↓                                    │
│  Server finds key → returns cached 200 + charge_id     │
│  No second charge processed                            │
└─────────────────────────────────────────────────────────┘
```

**Atomicity concern:** The check-and-store must be atomic:

```
// WRONG: TOCTOU race condition
if (!redis.exists(key)) {
    result = processCharge();  // two concurrent requests both get here
    redis.set(key, result);
}

// RIGHT: Atomic lock-then-process
lock = redis.set(key, "PROCESSING", NX, EX, 30)
if (lock) {
    result = processCharge();
    redis.set(key, serialize(result), EX, 86400);
} else {
    // Poll/wait for result from the winning request
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────────────────┐
│  CLIENT                    SERVER                       │
├─────────────────────────────────────────────────────────┤
│  Generate key              Check key store             │
│  POST + key ──────────────→ [Key absent?]              │
│                             ↓ YES                      │
│                             Process operation          │
│                             ← YOU ARE HERE             │
│                             Store {key → result}       │
│  ← Response ───────────────  Return result            │
│                                                        │
│  RETRY (timeout/error):                               │
│  POST + SAME key ─────────→ [Key present?]            │
│                             ↓ YES                      │
│  ← Cached Response ────────  Return stored result     │
│                             No re-processing           │
└─────────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
If idempotency key store (Redis) fails → server falls back to processing
without dedup → duplicate risk. Mitigate: use DB transaction with unique
constraint on idempotency key as fallback.

**WHAT CHANGES AT SCALE:**
At 1M requests/second, idempotency key store becomes a hot path. Solution:
partition by key hash → distribute across Redis cluster. TTL becomes critical:
too long = unbounded storage growth; too short = retries after expiry create
duplicates.

---

### 💻 Code Example

```java
// Example 1 — Client: generate idempotency key before first attempt
public class PaymentClient {
    // Generate ONCE per logical operation, before first call
    private final String idempotencyKey = UUID.randomUUID().toString();

    public ChargeResponse chargeWithRetry(ChargeRequest req)
            throws Exception {
        int attempts = 0;
        while (attempts < 3) {
            try {
                return httpClient.post("/charges",
                    req,
                    Map.of("Idempotency-Key", idempotencyKey));
            } catch (TimeoutException | ConnectionException e) {
                attempts++;
                Thread.sleep(1000L * attempts); // backoff
            }
        }
        throw new ApiException("Failed after 3 attempts");
    }
}
```

```java
// Example 2 — Server: implement idempotency key handling
@RestController
public class ChargeController {

    @Autowired RedisTemplate<String, String> redis;
    @Autowired ChargeService chargeService;

    @PostMapping("/charges")
    public ResponseEntity<ChargeResponse> charge(
            @RequestHeader("Idempotency-Key") String key,
            @RequestBody ChargeRequest req) {

        String cacheKey = "idem:" + key;

        // Check for cached response
        String cached = redis.opsForValue().get(cacheKey);
        if (cached != null) {
            return ResponseEntity.ok(deserialize(cached));
        }

        // Atomic lock to prevent concurrent processing
        Boolean acquired = redis.opsForValue()
            .setIfAbsent(cacheKey, "PROCESSING",
                Duration.ofSeconds(30));

        if (!acquired) {
            // Another thread is processing — wait and return
            return pollForResult(cacheKey);
        }

        // Process and cache result
        ChargeResponse result = chargeService.process(req);
        redis.opsForValue().set(cacheKey,
            serialize(result), Duration.ofDays(1));
        return ResponseEntity.ok(result);
    }
}
```

```java
// Example 3 — PUT is naturally idempotent (no key needed)
// PUT fully replaces resource — same body = same state
PUT /users/42
{ "name": "Alice", "email": "alice@example.com" }

// Second identical PUT: no error, no duplication
// Server state: same as after first PUT
// Response may differ (200 vs 204) but state is identical

// PATCH is NOT idempotent by default:
PATCH /users/42
{ "loginCount": {"$increment": 1} }
// Each call increments counter — NOT idempotent
// To make PATCH idempotent: use absolute values, not deltas
PATCH /users/42
{ "loginCount": 5 }  // now idempotent
```

---

### ⚖️ Comparison Table

| HTTP Method | Idempotent | Safe | Typical Use     | Retry Safety   |
| ----------- | ---------- | ---- | --------------- | -------------- |
| **GET**     | ✓          | ✓    | Read resource   | Always safe    |
| **PUT**     | ✓          | ✗    | Full replace    | Safe to retry  |
| **DELETE**  | ✓          | ✗    | Remove resource | Safe to retry  |
| **POST**    | ✗          | ✗    | Create/action   | Needs Idem-Key |
| **PATCH**   | ✗          | ✗    | Partial update  | Needs Idem-Key |
| **HEAD**    | ✓          | ✓    | Metadata check  | Always safe    |

**How to choose:** Default to GET/PUT/DELETE for standard CRUD. Use POST only
for operations with side effects that cannot be modeled as resource replacement.
Always add `Idempotency-Key` support for POST endpoints that create resources
or trigger financial/email/notification side effects.

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                       |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Idempotent means same response every time        | Idempotent means same _server state_ — responses can differ (200 then 404 for DELETE)                         |
| POST can never be idempotent                     | POST can be made idempotent by implementing the Idempotency-Key pattern server-side                           |
| PATCH is always idempotent                       | PATCH is only idempotent if the operation uses absolute values; incremental patches are not idempotent        |
| GET requests never modify data                   | Many APIs break this — analytics tracking, audit logs. This violates the "safe" contract and prevents caching |
| Idempotency keys must be globally unique forever | Keys only need to be unique within their TTL window — typically 24h to 7 days                                 |

---

### 🚨 Failure Modes & Diagnosis

**Duplicate Charges from Missing Idempotency Key**

**Symptom:**
Customer support receives reports of duplicate charges. Database shows
two charge records with identical amounts and times per affected user.

**Root Cause:**
POST endpoint lacks idempotency key support. Client retry logic fires on
timeout, creating a second charge record.

**Diagnostic Command / Tool:**

```sql
-- Find duplicate charges within 60 seconds:
SELECT user_id, amount, COUNT(*) as count,
       MIN(created_at) as first, MAX(created_at) as last
FROM charges
GROUP BY user_id, amount,
         DATE_TRUNC('minute', created_at)
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

**Fix:**
Add `Idempotency-Key` header parsing + Redis dedup store to POST /charges.
Retroactively refund identified duplicates.

**Prevention:**
All POST endpoints with financial or notification side effects must require
`Idempotency-Key` header. Return 400 if header is missing.

---

**Race Condition in Idempotency Key Store**

**Symptom:**
Two identical requests with the same key arrive simultaneously (client
with concurrent workers). Both process, creating two records despite having
the same idempotency key.

**Root Cause:**
check-then-set is not atomic. Both requests check "key absent", both
proceed to process before either stores the result.

**Diagnostic Command / Tool:**

```bash
# Check Redis for duplicate processing markers:
redis-cli KEYS "idem:*" | head -20
redis-cli GET "idem:<your-key>"
# If value is "PROCESSING" for too long: stuck lock
```

**Fix:**
Use `SET key value NX EX seconds` (atomic set-if-not-exists with TTL).
Never use GET+SET as two separate operations.

**Prevention:**
Use the Lua script or `SETNX` pattern for atomic acquisition.
Test with concurrent load testing (k6, Gatling) with shared idempotency keys.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP Methods` — idempotency is defined per HTTP method; must know GET/PUT/POST/DELETE semantics
- `REST` — idempotency is a core REST constraint; RESTful APIs must respect method semantics
- `HTTP Status Codes` — 404 on second DELETE is correct idempotent behavior; must understand response codes

**Builds On This (learn these next):**

- `API Design Best Practices` — idempotency is a foundational principle of robust API design
- `Retry Strategy` — safe retry is only possible with idempotent operations or idempotency keys
- `Idempotency Key` — the mechanism for making non-idempotent operations safe to retry

**Alternatives / Comparisons:**

- `Retry with Backoff` — the retry mechanism that requires idempotency to be safe
- `API Rate Limiting` — related resilience concern; often accompanies retry/idempotency design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Property: same call N times = same effect  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Network retries create duplicate side      │
│ SOLVES       │ effects (charges, emails, orders)          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Idempotency is about server STATE, not     │
│              │ response — DELETE returning 404 is fine    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any POST with financial or irreversible    │
│              │ side effects; any op retried over network  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Read-only operations (GET is always safe)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Safety vs complexity of key store + TTL   │
│              │ management                                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Send it twice, charge once"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Retry Strategy → Idempotency Key           │
│              │ → API Design Best Practices                │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A distributed payment system retries failed requests using an
idempotency key stored in Redis. Redis goes down for 30 seconds during
peak traffic. What are the exact failure modes during the Redis outage,
what is the safest fallback strategy, and what invariants must hold to
ensure no customer is charged twice?

**Q2.** HTTP DELETE is defined as idempotent by the spec, yet many teams
implement it as non-idempotent (returning 500 if the resource is already
gone). Trace the downstream consequences of this violation: which HTTP
intermediaries, client retry libraries, and monitoring systems make
assumptions about DELETE's idempotency, and how does each break when
the assumption is violated?
