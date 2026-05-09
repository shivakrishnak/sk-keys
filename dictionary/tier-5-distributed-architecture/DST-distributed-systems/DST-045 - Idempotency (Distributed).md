---
id: DST-045
title: "Idempotency (Distributed)"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-044, DST-037
related: DST-044, DST-037, DST-029, DST-033
tags:
  - distributed
  - reliability
  - pattern
  - foundational
  - deep-dive
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /distributed-systems/idempotency/
---

# DST-045 - Idempotency (Distributed)

⚡ TL;DR - An idempotent operation produces the same result whether executed once or N times — the property that makes retry with backoff safe for write operations, eliminating double-processing in at-least-once delivery systems.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-044, DST-037                   |     |
| **Related:**    | DST-044, DST-037, DST-029, DST-033 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user clicks "Pay Now" in an e-commerce app. The HTTP request reaches the payment service. The payment is processed ($100 charged). The response travels back — and the network drops the connection. The client receives a timeout. Was the payment made? The client doesn't know. It retries. Payment is charged again. The user is charged $200 for one purchase. This is the "exactly once" problem: the client wants to send the payment exactly once, but the network can only provide at-least-once delivery (the client may retry). Without idempotency: at-least-once delivery = potential double-processing.

**THE BREAKING POINT:**
In distributed systems, at-least-once delivery is the only practical guarantee. Exactly-once delivery requires distributed consensus on every message — too expensive for high-throughput systems. The practical solution: at-least-once delivery + idempotent receivers. If the receiver can handle duplicates without side effects: at-least-once is effectively exactly-once from the business perspective.

**THE INVENTION MOMENT:**
The mathematical concept of idempotence (f(f(x)) = f(x)) comes from abstract algebra. Applied to distributed systems: Stripe pioneered the Idempotency Key header in 2014 — a client-generated UUID sent with every payment request. Stripe stores the result of the first execution and returns it on any duplicate request. The payment is charged once, regardless of how many times the client retries. This pattern solved the "safe retry" problem for payment APIs and became the industry standard.

**EVOLUTION:**
1970s: HTTP GET/PUT/DELETE defined as idempotent in the HTTP specification. 2014: Stripe introduces Idempotency Key header for payment APIs. 2015+: PayPal, Square, Braintree adopt the pattern. 2016: AWS SQS advises idempotent consumers for at-least-once delivery. 2018: gRPC retry policy requires idempotent method annotation. 2020+: Event sourcing and outbox pattern (DST-033) rely on idempotent message consumers as a core design constraint.

---

### 📘 Textbook Definition

**Idempotency** (f: X → Y is idempotent if f(f(x)) = f(x) for all x ∈ X) in distributed systems means: executing an operation multiple times with the same input produces the same result and the same side effects as executing it once. **Natural idempotency:** some operations are inherently idempotent. GET (read: same result every time). PUT (set resource to value V: already V after first call). DELETE (delete: already deleted after first call). **Surrogate idempotency:** non-idempotent operations made idempotent via an **Idempotency Key** — a client-generated UUID sent with the request. The server stores (idempotency_key → result) and returns the stored result on duplicate requests. **At-least-once + idempotent = effectively exactly-once:** message queues (SQS, Kafka) guarantee at-least-once delivery. If message processing is idempotent: duplicate messages cause no additional side effects → business semantics = exactly-once.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Same input → same outcome, whether you call it once or a hundred times.

> Idempotent operations are like light switches with a label "ON" and "OFF" instead of a toggle. If you press "ON" three times: the light is on — same result as pressing once. The label ensures: the OUTCOME (light state) determines the result, not the NUMBER of presses.

**One insight:** Idempotency doesn't mean the operation does nothing on the second call — it means the OUTCOME is the same. A DELETE that's already deleted should return success (not 404), because the desired outcome (resource deleted) is achieved.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Outcome-based, not execution-based:** an idempotent operation is defined by its OUTCOME (desired state), not by how many times it runs. `setBalance($100)` is idempotent. `deductBalance($100)` is not.
2. **Idempotency key uniqueness:** the key must uniquely identify one logical operation (not one request). Client generates UUID per user action (per button click), not per retry attempt. Same UUID for all retries of the same operation.
3. **Idempotency key storage:** server must store (key → result) durably, with TTL. Stripe: 24-hour TTL for payment keys. After TTL: duplicate detection disabled (operation may run again).
4. **Concurrent duplicate handling:** two requests with the same key arriving simultaneously must be serialized. Only one processes; the other waits for the result. Requires distributed locking (DST-037) or database UNIQUE constraint.

**DERIVED DESIGN:**

```
Server-side idempotency:
  receive(request + idempotency_key):
    if key in store:
      return store[key]  // duplicate: return cached result
    else:
      acquire_lock(key)  // prevent concurrent duplicates
      if key in store:
        return store[key]  // race: another worker got there
      result = process(request)
      store[key] = result  // persist result
      release_lock(key)
      return result
```

**THE TRADE-OFFS:**
**Gain:** Safe retries (at-least-once → effectively exactly-once). User experience (no double charges, no duplicate orders). Simplified client logic (retry freely).
**Cost:** Storage for (key → result) map (grows with request volume). TTL management (too short: duplicate detection fails; too long: storage bloat). Locking overhead for concurrent duplicates. Key generation burden on client.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Storing idempotency key results requires durable, queryable storage — inherently adds latency. The concurrent duplicate case requires coordination — inherently adds complexity.
**Accidental:** Database UNIQUE constraint vs Redis vs distributed lock (DST-037). Different implementations, same semantics. Database UNIQUE constraint is simplest and most durable.

---

### 🧪 Thought Experiment

**SETUP:** User clicks "Buy" on a $100 item. Client generates idempotency key: `UUID = "abc-123"`. Sends POST /payment with key. Network is unreliable.

**SCENARIO A — Response lost (client retries):**

- T=0: POST /payment {"amount": 100, "key": "abc-123"} → server processes, stores result, response drops.
- T=5s: client retries: POST /payment {"amount": 100, "key": "abc-123"} → server checks: key "abc-123" found in store → returns stored result (CHARGED: $100 on 2024-01-15T10:00:00Z). No second charge.
- User: one charge on statement. Correct.

**SCENARIO B — Without idempotency:**

- T=0: POST /payment → charged $100. Response drops.
- T=5s: client retries: POST /payment → charged $100 again.
- User: two charges ($200). Wrong.

**SCENARIO C — Concurrent requests (race condition):**

- T=0: Two HTTP requests arrive simultaneously with same key "abc-123".
- Thread 1 and Thread 2 both check: key not found. Both proceed to charge.
- Without coordination: $200 charged. With UNIQUE constraint: one INSERT succeeds, one gets constraint violation. The constrained request waits, re-reads stored result, returns it.

**THE INSIGHT:** Idempotency key + durable storage converts at-least-once delivery into effectively-once business semantics. The key is a contract: "I promise this key represents exactly one logical operation."

---

### 🧠 Mental Model / Analogy

> Idempotency is like a hotel key card. Whether you tap the card once or 10 times, the door opens exactly once (on the first successful tap). The door doesn't open 10 times. The OUTCOME (door state = open) is the same. The key card encodes the identity of the operation (who is entering), not the number of taps.

**Mapping:**

- **Key card tap** → API request with idempotency key
- **Door opening state** → operation outcome (payment charged)
- **Tapping 10 times** → 10 retries with the same key
- **Door opening only once** → payment charged only once
- **Hotel key card = unique per guest** → UUID = unique per user action

Where this analogy breaks down: a hotel door has simple binary state (open/closed). Database idempotency must handle complex state (partial failures, concurrent updates, TTL expiry). The "door" may be in an inconsistent state mid-operation — idempotency keys must handle these cases (return in-progress status, or complete and return final result).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Idempotent means: you can do it twice and nothing bad happens. Pressing a crosswalk button is idempotent — press 10 times, the light still changes once. Buying a coffee is NOT idempotent — press 10 times on "Pay" and you're charged 10 times. Software systems that handle failures need idempotent operations so that retrying is safe.

**Level 2 - How to use it (junior developer):**
Client side: generate UUID per user action (not per request): `String idempotencyKey = UUID.randomUUID().toString();`. Store key across retries. Send as header: `X-Idempotency-Key: <uuid>`. Server side: check key in Redis/DB before processing. If found: return stored result. If not: process + store. Spring example: `@RequestHeader("X-Idempotency-Key") String key` in controller.

**Level 3 - How it works (mid-level engineer):**
Database-backed idempotency (most durable):

```sql
CREATE TABLE idempotency_keys (
  key VARCHAR(36) PRIMARY KEY,
  response_body TEXT NOT NULL,
  status_code INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL
);
```

On request: `INSERT INTO idempotency_keys (key, ...) VALUES (?, ...)`. If `DuplicateKeyException`: SELECT existing result and return it. UNIQUE constraint on `key` column enforces exactly-one semantics. Race: two concurrent requests with same key → one INSERT succeeds, one gets exception → exception handler re-reads and returns result. Transaction: INSERT + business operation + result storage must be in the SAME database transaction (otherwise partial failure leaves key without result).

**Level 4 - Why it was designed this way (senior/staff):**
Stripe's idempotency key design reveals three subtle choices: (1) Client-generated UUID (not server-generated) — the client controls the operation identity. This enables retry without coordination: client retries with same UUID, server detects duplicate. Server-generated keys would require the client to know the key before retrying — a circular dependency. (2) 24-hour TTL — long enough for retry windows (minutes to hours), short enough to prevent storage bloat. After 24 hours: the operation is assumed complete and retry risk is low (business semantics). (3) Key stored with result in the SAME database transaction as the business operation — ensures no key stored without result (partial failure leaves no key), and no result stored without key (no duplicate detection possible). This atomic pairing is the critical correctness property.

**Expert Thinking Cues:**

- "Client generates a new UUID on every retry instead of reusing the same key" → Idempotency breaks. Each retry appears as a new operation — duplicates processed. Fix: generate UUID once per user action (before any retry loop), store in request context, reuse across all retries.
- "Idempotency key collision (two different operations get the same key)" → UUID4 collision probability: ~1 in 2¹²² ≈ negligible. If using sequential IDs as keys (not UUIDs): collision risk is real. Always use UUID4 or equivalent random key. Also: scope keys by user ID + operation type to further reduce collision risk: `${userId}:payment:${uuid}`.
- "Message queue consumer needs idempotency but message has no idempotency key" → Use message's own ID as idempotency key (`MessageId` in SQS, `offset` in Kafka). Store processed IDs in a "processed messages" table. On duplicate: check table before processing. TTL: after retention period, duplicate detection disabled (message is past its redelivery window anyway).

---

### ⚙️ How It Works (Mechanism)

**Idempotency key flow with race condition handling:**

```
Client                     Server                  DB
  │                           │                     │
  │─POST /payment             │                     │
  │  X-Idempotency-Key: abc───▶                     │
  │                           │─SELECT key='abc'───▶│
  │                           │◀─0 rows─────────────│
  │                           │ [begin transaction]  │
  │                           │─INSERT key='abc'    │
  │                           │  status='PENDING'──▶│
  │                           │◀─OK─────────────────│
  │                           │─charge($100)────────▶│
  │                           │◀─OK─────────────────│
  │                           │─UPDATE key='abc'    │
  │                           │  status='COMPLETE'  │
  │                           │  result={charged}──▶│
  │                           │◀─OK─────────────────│
  │                           │ [commit]             │
  │◀─200 {charged}────────────│                     │

Client retries (network dropped response):
  │─POST /payment             │                     │
  │  X-Idempotency-Key: abc───▶                     │
  │                           │─SELECT key='abc'───▶│
  │                           │◀─{charged}──────────│
  │◀─200 {charged}────────────│ (no second charge)
```

**HTTP idempotency by method (RFC 7231):**

```
GET:    Idempotent (read-only)
HEAD:   Idempotent (read-only)
PUT:    Idempotent (set to value V; repeated = no change)
DELETE: Idempotent (delete; second call: already gone)
POST:   NOT idempotent by default
PATCH:  NOT idempotent (depends on operation)
OPTIONS: Idempotent
```

---

### 🔄 The Complete Picture - End-to-End Flow

**PAYMENT WITH AT-LEAST-ONCE DELIVERY:**

```
Browser → API Gateway → Payment Service → DB
  │             │              │           │
  │─POST /buy──▶│              │           │
  │             │─POST /charge─▶           │
  │             │  key: abc-123│           │
  │             │              │─INSERT────▶│
  │             │              │◀─OK────────│
  │             │◀─200────────│            │
  │  [network drops response]              │
  │─POST /buy──▶│ (retry)      │           │
  │             │─POST /charge─▶           │
  │             │  key: abc-123│           │
  │             │              │─SELECT────▶│ ← YOU ARE HERE
  │             │              │◀─RESULT────│ (found: charged)
  │             │◀─200────────│            │
  │◀─200 OK─────│ (same result, no second charge)
```

**WHAT CHANGES AT SCALE:**
At scale: idempotency key store is accessed on every request (read + conditional write). With 10,000 req/s: 10,000 reads/s on idempotency table. Optimization: cache recent keys in Redis with TTL (Redis as L1 cache, DB as L2 source of truth). 99% of requests (first-time, no duplicate): check Redis → miss → check DB → miss → process. 1% (retries): check Redis → hit → return result (no DB query for business operation).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent requests with same key: both check "key exists?" at T=0. Both see "not exists." Both attempt INSERT. One succeeds. One gets `DuplicateKeyException`. The duplicate handler: sleep briefly, re-select, return existing result. This is the "check-then-act" race — handled correctly by database UNIQUE constraint (atomic INSERT). Redis-based alternative: `SETNX key result EXPIRY` — atomic set-if-not-exists. First caller: sets key + processes. Second caller: SETNX fails → return existing value.

---

### 💻 Code Example

**BAD - No idempotency (double-processing on retry):**

```java
// BAD: no idempotency key check
@PostMapping("/payment")
public PaymentResult charge(@RequestBody PaymentRequest req) {
    // If client retries: charges again!
    return paymentProcessor.charge(
        req.getCustomerId(), req.getAmount());
    // No duplicate detection: retry = double charge
}
```

**GOOD - Idempotency key with database UNIQUE constraint:**

```java
@PostMapping("/payment")
public ResponseEntity<PaymentResult> charge(
    @RequestHeader("X-Idempotency-Key") String key,
    @RequestBody PaymentRequest req) {

    // Check for existing result (fast path):
    Optional<IdempotencyRecord> existing =
        idempotencyRepo.findByKey(key);
    if (existing.isPresent()) {
        // Duplicate request: return stored result
        return ResponseEntity
            .status(existing.get().getStatusCode())
            .body(existing.get().getResult());
    }

    // Process and store atomically:
    try {
        return transactionTemplate.execute(status -> {
            // Store key first (with PENDING status):
            idempotencyRepo.save(new IdempotencyRecord(
                key, null, null,
                Instant.now().plusSeconds(86400)));
            // UNIQUE constraint: second concurrent insert fails

            // Execute business logic:
            PaymentResult result = paymentProcessor.charge(
                req.getCustomerId(), req.getAmount());

            // Store final result:
            idempotencyRepo.updateResult(
                key, result, 200);

            return ResponseEntity.ok(result);
        });
    } catch (DuplicateKeyException e) {
        // Race: another request processed with same key
        IdempotencyRecord record =
            idempotencyRepo.findByKey(key)
                .orElseThrow();
        if (record.getResult() == null) {
            // Still processing: return 202 Accepted
            return ResponseEntity.accepted().build();
        }
        return ResponseEntity
            .status(record.getStatusCode())
            .body(record.getResult());
    }
}
```

**Client: generate key once per user action:**

```java
public class PaymentClient {
    public PaymentResult buyWithRetry(PaymentRequest req)
        throws MaxRetriesExceededException {
        // Generate key ONCE before retry loop
        String idempotencyKey = UUID.randomUUID().toString();
        // Key is REUSED across all retries:
        for (int attempt = 0; attempt < 3; attempt++) {
            try {
                return httpClient.post("/payment")
                    .header("X-Idempotency-Key",
                        idempotencyKey) // same key each retry
                    .body(req)
                    .execute(PaymentResult.class);
            } catch (NetworkException | Http5xxException e) {
                if (attempt < 2) {
                    Thread.sleep(fullJitter(attempt, 100, 5000));
                } else throw new MaxRetriesExceededException(e);
            }
        }
        throw new MaxRetriesExceededException("unreachable");
    }
}
```

---

### ⚖️ Comparison Table

| Delivery guarantee | System guarantee                    | Idempotency needed?         | Duplicate risk     |
| :----------------- | :---------------------------------- | :-------------------------- | :----------------- |
| At-most-once       | May lose messages                   | No (no retry)               | None (no retry)    |
| At-least-once      | May deliver duplicates              | YES — required              | High (retry loops) |
| Exactly-once       | One delivery (complex)              | No                          | None               |
| Effectively-once   | At-least-once + idempotent consumer | Idempotency IS the solution | Handled            |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                     |
| :---------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "HTTP GET is always safe to retry"                                | GET is idempotent per HTTP spec — calling it multiple times returns the same result. But many APIs violate this: `GET /ticket/next` (returns and increments a counter), `GET /user/activate-account` (side effect on first call). HTTP method idempotency is a contract, not a guarantee — verify per API.                                                                                                  |
| "DELETE should return 404 on the second call"                     | Per HTTP spec: DELETE is idempotent — the desired outcome (resource deleted) is achieved whether the resource existed or was already deleted. A correct idempotent DELETE returns 200/204 on subsequent calls (resource is deleted, as desired). Returning 404 breaks idempotency — client treats 404 as an error and may not retry safely.                                                                 |
| "Idempotency key must be the same as the operation's primary key" | Idempotency key and resource ID are separate concepts. Idempotency key: client-generated UUID for this REQUEST ATTEMPT. Resource ID: server-assigned ID for the created resource. Creating a payment: idempotency_key=UUID (prevents double charge). payment_id=server-assigned-ID (identifies the created payment). Both stored in the idempotency record: `{key: abc, payment_id: pay-123, amount: 100}`. |
| "Kafka exactly-once delivery replaces idempotency"                | Kafka exactly-once (DST-029 Kafka Transactions) ensures exactly-once DELIVERY to the Kafka topic. But if the consumer processes the message and writes to a database: the consumer must ALSO be idempotent (or use Kafka's transactional offset commit). Kafka exactly-once delivery doesn't guarantee exactly-once PROCESSING in the consumer's downstream systems.                                        |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Idempotency Key Not Persisted Atomically with Operation**

**Symptom:** Payment service occasionally processes payments twice. Investigation reveals: payment is processed, then the server crashes before the idempotency key is stored. On retry: no key found → payment processed again. Double charge.
**Root Cause:** Business operation (charge payment) and idempotency key storage are in SEPARATE transactions or separate stores. Server crash between them: payment committed, key not stored → retry succeeds again.
**Diagnostic:**

```bash
# Check if idempotency key storage is in same transaction:
grep -A 20 "idempotency\|idempotent" PaymentService.java | \
  grep "transaction\|@Transactional\|commit"
# If idempotency store and payment are in different
# method calls without shared transaction: not atomic

# Check for double charges in payment records:
SELECT customer_id, amount, created_at
FROM payments
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY customer_id, amount, date_trunc('minute', created_at)
HAVING count(*) > 1;
# Duplicates = double processing
```

**Fix:**
BAD: Process payment, THEN store idempotency key (two separate transactions).
GOOD: Store idempotency key (status=PENDING) + process payment + update key (status=COMPLETE) ALL in one database transaction. If server crashes after payment but before key update: on restart → key found (PENDING) → return in-progress status (or complete and update key).
**Prevention:** Code review rule: idempotency key INSERT must be in the same transaction as the business operation. Test: kill the process mid-transaction and verify retry returns correct result.

**Failure Mode 2: Key Expires Before Client Retries**

**Symptom:** User clicks "Buy" during a network outage. Client retries periodically. After 25 hours (TTL=24h): client retries with the original idempotency key. Server: key not found (expired) → processes payment again. Double charge.
**Root Cause:** Client retry window (25 hours) exceeds idempotency key TTL (24 hours). After expiry: duplicate detection disabled.
**Diagnostic:**

```bash
# Check TTL of idempotency keys:
SELECT key, created_at, expires_at,
  expires_at - created_at AS ttl
FROM idempotency_keys
WHERE key = '<problem-key>';
# If expires_at < NOW() and operation was retried: TTL too short

# Check client retry schedule:
# If max_retry_window > TTL: configuration mismatch
grep "maxWait\|maxRetry\|backoff.*cap" client-config.yaml
# Compare max_possible_retry_time vs key TTL
```

**Fix:**
BAD: TTL=24h, client retry window=25h.
GOOD: Client max retry window ≪ server key TTL. Rule: TTL ≥ max_client_retry_window × 2. Set TTL=48h if client may retry for up to 24h. Alternatively: expire keys by policy (idempotency window = 1h from first request) and require new key after 1h.
**Prevention:** Document the retry window contract: `X-Idempotency-Key` valid for N hours. Client must generate new key after N hours. TTL on server must be > N + buffer.

**Failure Mode 3: Security - Idempotency Key Replay Attack**

**Symptom:** An attacker intercepts a legitimate payment request (with idempotency key). Replays the request with the same key from a different session/user. Server returns the original payment result — revealing payment details (amount, timestamp, last 4 digits of card) to the attacker. Or: attacker generates an idempotency key that collides with a victim's in-progress payment and learns whether the victim's payment succeeded.
**Root Cause:** Idempotency keys are not scoped to the authenticated user. Any authenticated user can query any idempotency key — a data leakage vulnerability.
**Diagnostic:**

```bash
# Test: can User B query User A's idempotency key?
# POST /payment with User B's auth token but User A's key
curl -H "Authorization: Bearer USER_B_TOKEN" \
  -H "X-Idempotency-Key: USER_A_UUID" \
  https://api.example.com/payment
# If returns User A's payment result: data leakage
```

**Fix:**
BAD: Idempotency key lookup: `SELECT * FROM idempotency_keys WHERE key = ?`. No user scoping.
GOOD: Always scope keys to the authenticated user: `SELECT * FROM idempotency_keys WHERE key = ? AND user_id = ?`. Store `user_id` with each idempotency key. Reject if user doesn't match.
**Prevention:** Idempotency keys are per-user. Never allow cross-user key lookup. Include user_id in the key lookup query. Audit log for all idempotency key access (detect enumeration attacks).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-044 - Retry with Backoff (idempotency enables safe retry — understand retry before idempotency's motivation)
- DST-037 - Distributed Locking (concurrent duplicate requests require locking to serialize access)

**Builds On This (learn these next):**

- DST-029 - Kafka (at-least-once delivery requires idempotent consumers — next natural step)
- DST-033 - Outbox Pattern (outbox pattern relies on idempotent message consumers)

**Alternatives / Comparisons:**

- DST-044 - Retry with Backoff (retry is safe only with idempotent operations)
- DST-037 - Distributed Locking (alternative coordination mechanism for deduplication)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Property: same input → same    |
|                  | outcome, once or N times       |
|                  | (no additional side effects)   |
+------------------+--------------------------------+
| PROBLEM SOLVED   | At-least-once delivery causes  |
|                  | double-processing without      |
|                  | idempotent receivers           |
+------------------+--------------------------------+
| KEY INSIGHT      | Client-generated UUID per user |
|                  | action (not per request):      |
|                  | all retries share one key      |
+------------------+--------------------------------+
| USE WHEN         | Any at-least-once delivery;    |
|                  | any write operation with retry |
+------------------+--------------------------------+
| AVOID WHEN       | Truly stateless operations     |
|                  | (storage overhead not worth it)|
+------------------+--------------------------------+
| TRADE-OFF        | Safe retries + deduplication   |
|                  | vs storage + TTL management    |
+------------------+--------------------------------+
| ONE-LINER        | UUID per action + server stores|
|                  | result → retry-safe writes     |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-044 Retry with Backoff,    |
|                  | DST-033 Outbox Pattern         |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Idempotency key must be generated ONCE per user action (before the retry loop) and REUSED across all retries. A new key per retry defeats the purpose — each retry looks like a new operation.
2. Store the idempotency key and the operation result in the SAME database transaction. Split storage (process first, store key later) creates a window where a crash causes double-processing on retry.
3. Scope idempotency keys to the authenticated user. Unscoped keys are a data leakage vulnerability — any user could query another user's operation result.

**Interview one-liner:**
"Idempotent operations produce the same outcome whether executed once or N times — the property that makes retry safe in at-least-once delivery systems. Client-side: generate one UUID per user action (not per request) and send it as an idempotency key. Server-side: store (key → result) atomically with the business operation. On duplicate request: return stored result without re-processing. Stripe pioneered this with the `Idempotency-Key` header for payment APIs. Critical details: key must be user-scoped (security), key + result stored in one transaction (correctness), TTL must exceed client retry window (reliability)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Make operations describe DESIRED STATE, not ACTIONS. `setBalance($100)` is idempotent (desired state: balance=100). `deductBalance($100)` is not (action: subtract 100). HTTP PUT (set resource to this value) is idempotent. HTTP POST (perform this action) is not. When designing APIs, prefer state-setting semantics over action semantics for any operation that may be retried. This is also the foundation of Kubernetes controllers (desired state reconciliation) and Terraform (desired state vs imperative scripts).

**Where else this pattern appears:**

- **Kubernetes controller reconciliation loop:** Kubernetes controllers continuously compare desired state (spec) with current state (status). If they differ: the controller takes action to converge them. Applying the same manifest twice: the second apply is a no-op (desired state already matches current state). This is idempotent API design at the infrastructure level — `kubectl apply` can be safely run 100 times on the same manifest.
- **Database UPSERT operations:** `INSERT INTO table ... ON CONFLICT DO UPDATE SET ...` — inserts if row doesn't exist, updates if it does. The outcome (row has these values) is the same whether run once or 100 times. UPSERT is the database-native idempotent write primitive. Used for: idempotent message processing (upsert result with message ID as primary key), cache warming (upsert cache entries from source of truth).
- **Terraform infrastructure provisioning:** Terraform `apply` creates resources that don't exist, updates resources that do, ignores resources already in desired state. Running `apply` twice on the same config: second run is a no-op. Idempotent infrastructure changes: safe to retry on failure, safe to run in CI/CD pipelines. Compare with imperative scripts: running a bash script twice may create duplicate resources, fail on existing resources, or corrupt state.

---

### 💡 The Surprising Truth

HTTP DELETE is defined as idempotent by the HTTP specification — but most REST API implementations violate this by returning 404 Not Found when trying to delete an already-deleted resource. This is INCORRECT per the spec: the desired outcome (resource is deleted) is achieved whether the resource existed or not. A 404 response to a repeated DELETE causes problems for retry logic: clients see 404 as an error, don't retry, but the operation actually succeeded. The surprising truth: correct idempotent DELETE behavior (return 200/204 even if resource was already deleted) is counterintuitive to most developers, yet it's specified in RFC 7231 (HTTP/1.1 semantics). Stripe explicitly documents this in their API guide: "Sending two DELETE requests to the same resource should return the same success response." Most APIs get this wrong — creating subtle retry bugs that are hard to diagnose because the "error" (404) looks like a client bug, not a server idempotency violation.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** A checkout service sends a payment request to the Payment Service with idempotency key K. Payment Service processes the payment and stores the result. Then Checkout Service sends the result to the Order Service to create an order. Order Service fails. Checkout Service retries Order Service with a DIFFERENT idempotency key for the order creation. How many times might the payment be charged and the order be created? What is the correct design?
_Hint:_ Payment: idempotency key K → charged once (correct, idempotency works). Order creation: retry with NEW key each time → creates a new order each retry (not idempotent). Correct design: (1) Checkout Service generates one UUID for order creation BEFORE retry loop. Reuses same UUID across all retries to Order Service. (2) Or: use the outbox pattern (DST-033) — write payment success + order creation intent to the same DB transaction, let a background worker process the order creation with exactly-once semantics. The root issue: idempotency is per-operation, not per-workflow. Each operation (payment, order) needs its own idempotency key, but each key must be consistent across retries of THAT operation.

**Q2 (D - Root Cause):** A payment API shows occasional double charges (approximately 0.01% of payments). The service uses idempotency keys correctly: client generates one UUID per payment attempt, server stores result atomically. Logs show: payment processed → idempotency key stored → response sent. On investigation: the double-charged payments always occurred exactly 24 hours after the first payment. What is the likely cause?
_Hint:_ 24 hours = idempotency key TTL (Stripe uses 24h default). Scenario: client retries at exactly 24h (edge case in retry logic — maybe a scheduled job that retries failed-looking payments once daily). Server: key expired → key not found → processes payment again. Double charge. Root causes to investigate: (1) Check client-side retry schedule — does it retry payments after 24h? If yes: extend key TTL to 48h or 72h. (2) Check key TTL configuration — is it exactly 24h or slightly less than 24h (clock drift, timezone issues)? (3) Check if a batch job runs daily that "re-processes unpaid orders" without checking if the original idempotency key succeeded. Fix: extend key TTL, eliminate daily retry jobs that don't verify idempotency.

**Q3 (C - Design Trade-off):** Kafka provides "exactly-once delivery" (via Kafka Transactions). A team argues this means their Kafka consumers don't need to implement idempotency — Kafka already guarantees exactly-once. Is this correct? Where does Kafka's exactly-once guarantee end and the consumer's idempotency responsibility begin?
_Hint:_ Kafka exactly-once delivery: guarantees each message is written to the Kafka topic exactly once (no duplicates in the topic). It also ensures that offset commits and produced messages are committed atomically (transactional Kafka). Where it ends: Kafka's guarantee is about DELIVERY to the broker and OFFSET COMMIT atomicity. It does NOT guarantee exactly-once PROCESSING in the consumer's downstream systems (database writes, API calls, cache updates). Example: consumer reads message, writes to DB, then Kafka broker crashes before offset commit. On restart: message re-delivered (at-least-once). If consumer's DB write is not idempotent: duplicate DB write. Correct design: Kafka exactly-once for message broker semantics + idempotent consumer for external side effects (DB writes, API calls). They're complementary, not alternatives.
