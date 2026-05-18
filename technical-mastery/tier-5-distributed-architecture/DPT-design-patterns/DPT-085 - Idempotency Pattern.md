---
id: DPT-085
title: Idempotency Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-084, DPT-065
used_on: []
related: DPT-084, DPT-038, DPT-086, DPT-065
tags:
  - pattern
  - distributed
  - advanced
  - idempotency
  - at-least-once
  - retry
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 85
permalink: /technical-mastery/design-patterns/idempotency-pattern/
---

⚡ TL;DR - An operation is idempotent if applying it
multiple times has the same effect as applying it once.
Idempotency is designed by ensuring operations are
safe to retry. The mechanism: idempotency keys that
track whether an operation has already completed,
preventing duplicate effects.

| #85 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-084, DPT-065 | |
| **Used by:** | N/A | |
| **Related:** | DPT-084, DPT-038, DPT-086, DPT-065 | |

---

### 🔥 The Problem This Solves

**THE RETRY PROBLEM:**
A client submits a payment of $99.99. The server
processes the payment successfully. The response
is lost in transit (network failure). The client
cannot distinguish:
- "Server received but network failed returning response"
- "Server never received the request"

The client retries. If the server has no idempotency
mechanism: the payment is processed twice. $199.98
charged. The customer disputes. The business loses trust.

This is not an edge case. Network failures, timeouts,
load balancer retries, and client-side retry logic
all create scenarios where the same request arrives
multiple times.

**THE IDEMPOTENCY SOLUTION:**
The client sends an idempotency key with the request.
The server records the key and the result. On retry:
the server finds the key, returns the original result.
The payment is processed exactly once regardless of
how many times the request arrives.

---

### 📘 Textbook Definition

**Idempotency** (from mathematics):
An operation f is idempotent if f(f(x)) = f(x).
Applying f twice has the same result as applying f once.

In distributed systems:
> An operation is idempotent if performing it multiple
> times produces the same result as performing it once,
> with no additional side effects.

**Natural idempotency (free):**
Some operations are idempotent by nature:
- `SET x = 5` (applying twice: same result)
- `DELETE WHERE id = 42` (deleting an already-deleted row: same result)
- `GET /users/1` (reading twice: same result, no side effects)
- HTTP GET, PUT, DELETE (RFC 7231: SHOULD be idempotent)

**Designed idempotency (requires implementation):**
Some operations are NOT naturally idempotent:
- `INSERT INTO payments (amount) VALUES (99.99)` (two inserts = two rows)
- `TRANSFER $99.99 FROM account_A TO account_B` (two transfers = $199.98 moved)
- `SEND email` (two sends = two emails received)
HTTP POST is NOT idempotent by definition.

**Idempotency key pattern:**
For non-natural idempotent operations: the client provides
a unique idempotency key (UUID) per logical operation.
The server uses the key to detect and handle retries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Same request, same effect, no matter how many times
it arrives. Idempotency keys are the mechanism: track
completed operations by key, skip duplicates.

**One analogy:**
> An elevator floor button.
>
> Pressing floor 5 once: elevator goes to floor 5.
> Pressing floor 5 ten more times: elevator still goes to
> floor 5. No additional effect.
>
> The button is idempotent: applying the "press" operation
> N times = same result as once.
>
> Contrast with a NON-idempotent elevator: each press
> sends the elevator to floor 5, back to ground floor,
> to floor 5 again, back... (10 presses = 10 trips).
>
> Safe, retry-friendly APIs work like the button.
> Dangerous, side-effect-multiplying APIs work like
> the non-idempotent elevator.

---

### 🔩 First Principles Explanation

**HTTP METHOD IDEMPOTENCY:**
RFC 7231 defines idempotency for HTTP methods:
- **GET**: idempotent (read only, no side effects)
- **PUT**: idempotent (set to value; setting twice = same)
- **DELETE**: idempotent (delete; deleting again = same)
- **POST**: NOT idempotent (create; creating twice = two resources)
- **PATCH**: not inherently idempotent (depends on semantics)

**IDEMPOTENCY KEY MECHANISM:**
For non-idempotent operations (POST/PATCH):

Client generates UUID: `idem_key = "550e8400-e29b-41d4-a716-446655440000"`
Client sends: `POST /payments { amount: 99.99 }` + header `Idempotency-Key: <uuid>`

Server logic:
1. Check if `idem_key` exists in `idempotency_records`.
2. If found: return stored result. Do NOT re-execute.
3. If not found:
   - Execute the payment.
   - Store `{ idem_key, result, completed_at }` in `idempotency_records`.
   - Return result.

On retry: step 2 returns the original result. One payment.

**KEY STORAGE REQUIREMENTS:**
- Keys must be stored in the SAME database as business data
  (transactional safety - same as Inbox Pattern DPT-084).
- Keys have a TTL: clients only retry within a window
  (24 hours is common). After TTL: key can be deleted.
- Key + result must be stored atomically with business logic.

**CLIENT KEY GENERATION:**
Clients should generate idempotency keys using UUID v4
(random). The key must be unique per logical operation,
not per request. If the same logical "create payment"
needs to be retried: use the SAME key. If starting a
NEW payment: generate a new key.

---

### 🧪 Thought Experiment

**PAYMENT GATEWAY RESILIENCE:**
Stripe uses idempotency keys. A client places a payment:
```
POST /v1/charges
Idempotency-Key: key_1234567890abcdef
{ amount: 999, currency: "usd" }
```
Network timeout. Client retries with the SAME key:
```
POST /v1/charges
Idempotency-Key: key_1234567890abcdef  ← same key
{ amount: 999, currency: "usd" }
```
Stripe detects the same key. Returns the original charge
result. One charge: $9.99. Safe retry.

Without idempotency keys: second POST creates a second
charge. Customer charged twice. Stripe has built this
idempotency key mechanism into its API design because
payment idempotency is business-critical.

---

### 🧠 Mental Model / Analogy

> Idempotency = "check if we've done this before."
>
> A check register in accounting.
> Every check written: recorded with a unique check number.
> Before writing a check: verify the number is not
> already in the register.
> If found: the check was already cashed - don't write another.
> If not found: write it, record it.
>
> Idempotency key = check number.
> Idempotency records table = check register.
> Business operation = writing the check.
>
> The discipline: clients must bring their own check
> number (idempotency key). Servers must honor the
> register (check for duplicates before processing).
> Together: exactly-once execution regardless of retries.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Natural idempotency:**
Design operations to be naturally idempotent where possible.
`UPDATE SET status = 'CANCELLED'` is idempotent.
`INSERT OR IGNORE INTO` (UPSERT) is idempotent.
`DELETE WHERE id = X` is idempotent.
Prefer these patterns over `INSERT` (not idempotent) or
`UPDATE SET count = count + 1` (not idempotent).

**Level 2 - Idempotency key implementation:**
For operations that cannot be naturally idempotent:
implement the idempotency key pattern. The key is a
client-provided UUID per logical operation. Store key
+ result in the same transaction as business logic.
On subsequent arrivals with the same key: return stored result.

**Level 3 - Conditional requests (HTTP ETags):**
HTTP ETags implement idempotency for resource updates:
`If-Match: "etag_abc123"` prevents applying an update
if the resource has changed since the client last read it.
This is optimistic concurrency - a related but distinct
mechanism. Idempotency keys handle retry-of-the-SAME-request.
ETags handle conflict-prevention for DIFFERENT requests
arriving out of order.

---

### ⚙️ How It Works (Mechanism)

```
Idempotency Key Pattern
┌─────────────────────────────────────────────────────────┐
│  Client                      Server                     │
│    │                            │                       │
│    │ POST /payments              │                      │
│    │ Idempotency-Key: KEY-1     │                       │
│    │ { amount: 99.99 }          │                       │
│    │────────────────────────►  │                       │
│    │                       CHECK: KEY-1 in idempotency_│
│    │                             records?              │
│    │                       NOT FOUND:                  │
│    │                         BEGIN TX                  │
│    │                           charge card $99.99      │
│    │                           INSERT idempotency_record│
│    │                             (KEY-1, result)       │
│    │                         COMMIT                    │
│    │  ◄─── HTTP 200 { chargeId: "ch_123" } ─────────   │
│    │                                                    │
│    │ (network fails before 200 received)               │
│    │ POST /payments (retry)                            │
│    │ Idempotency-Key: KEY-1     │                       │
│    │────────────────────────►  │                       │
│    │                       CHECK: KEY-1 FOUND!         │
│    │                       RETURN stored result:       │
│    │  ◄─── HTTP 200 { chargeId: "ch_123" } ─────────   │
│    │      (same response. No new charge.)              │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Idempotency key implementation:**

```java
// Idempotency records table entity:
@Entity
@Table(name = "idempotency_records")
class IdempotencyRecord {
    @Id
    private String idempotencyKey;
    private String responseBody;   // stored JSON response
    private int    responseStatus; // HTTP status code
    private Instant createdAt;
    private Instant expiresAt;
    // Constructors, getters omitted for brevity
}
```

```java
// Service with idempotency key support:
@Service
class PaymentService {

    private final IdempotencyRecordRepository idempotencyRepo;
    private final PaymentGateway gateway;
    private final PaymentRepository paymentRepo;

    @Transactional
    public PaymentResult processPayment(
            String idempotencyKey,
            PaymentRequest request) {

        // Step 1: Check for existing record.
        Optional<IdempotencyRecord> existing =
            idempotencyRepo.findById(idempotencyKey);

        if (existing.isPresent()) {
            // Duplicate request. Return stored result.
            return deserialize(existing.get().getResponseBody());
        }

        // Step 2: Process (within same transaction).
        PaymentResult result = gateway.charge(
            request.getAmount(),
            request.getCardToken());

        // Step 3: Record idempotency key + result atomically.
        idempotencyRepo.save(new IdempotencyRecord(
            idempotencyKey,
            serialize(result),
            200,
            Instant.now(),
            Instant.now().plus(Duration.ofDays(1))  // TTL: 24 hours
        ));

        // Step 4: Persist business result (same transaction).
        paymentRepo.save(new Payment(
            result.getChargeId(),
            request.getAmount(),
            "COMPLETED"));

        return result;
        // If anything throws: tx rolled back.
        // idempotency record NOT committed.
        // Next retry: treated as new request.
    }
}
```

```java
// REST controller passing idempotency key:
@RestController
@RequestMapping("/payments")
class PaymentController {

    private final PaymentService paymentService;

    @PostMapping
    public ResponseEntity<PaymentResult> createPayment(
            @RequestHeader(value = "Idempotency-Key",
                           required = true)
            String idempotencyKey,  // required header
            @RequestBody @Valid PaymentRequest request) {

        PaymentResult result = paymentService
            .processPayment(idempotencyKey, request);
        return ResponseEntity.ok(result);
    }
}
// Client responsibility: generate and send unique key per operation.
// Client should use the SAME key when retrying.
// Client should use a NEW key for a NEW payment.
```

---

### 🔥 Failure Scenarios

**WRONG SCOPE FOR IDEMPOTENCY KEY:**
```java
// BAD: Client generates new key on every retry.
// (Bug in client code: key not preserved across retries.)
String key = UUID.randomUUID().toString(); // new on every call
// Retry: new key every time. Server sees fresh request each time.
// No deduplication. Payment processed multiple times.

// CORRECT: Key generated once per logical operation,
// reused on all retries of the SAME operation.
String operationKey = UUID.randomUUID().toString(); // generated once
for (int attempt = 0; attempt < maxRetries; attempt++) {
    try {
        return client.post("/payments", request, operationKey);
    } catch (NetworkException e) {
        // Same operationKey used on retry.
        Thread.sleep(backoff(attempt));
    }
}
```

**IDEMPOTENCY RECORDS NOT CLEANED UP:**
```sql
SELECT COUNT(*) FROM idempotency_records;
-- 2.4 billion rows after 3 years
-- Payment check: 45-second full table scan
-- Service unavailable during lookup
```
Fix: `DELETE FROM idempotency_records WHERE expires_at < NOW()`
Run daily. Keep only within client retry window.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GET requests are always safe to retry | GET is idempotent (same result each time) but NOT always side-effect-free in practice. Some systems trigger operations on GET (logging, billing for reads, cache warming). True idempotency = same state transition, not necessarily zero side effects |
| Idempotency key in the URL is sufficient | URL-based keys (`/payments/KEY-1`) are for creating a specific resource. Idempotency keys in headers (`Idempotency-Key: KEY-1`) are for making a non-idempotent operation safe to retry. Different mechanisms for different purposes |
| Idempotency guarantees at-most-once semantics | Idempotency guarantees the EFFECT happens once. The OPERATION may run multiple times (retries). The design ensures multiple runs produce one effect. This is "effectively-once" not "at-most-once" (which would prevent retries entirely) |
| All services need idempotency keys | Read operations, naturally idempotent writes (SET x = 5, DELETE WHERE id = Y), and fire-and-forget analytics do not need idempotency keys. Keys are for operations that have destructive consequences when duplicated (payments, reservations, sends) |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Same operation, same effect, N times.   │
│              │ Idempotency keys prevent duplicate effect│
├──────────────┼──────────────────────────────────────────┤
│ NATURAL      │ GET, PUT, DELETE, SET x = 5, UPSERT     │
│              │ DELETE WHERE id = X                     │
├──────────────┼──────────────────────────────────────────┤
│ NOT NATURAL  │ POST, INSERT, TRANSFER, SEND (add key)  │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ Same logical op = same key.             │
│              │ New op = new key. SAME key on retries.  │
├──────────────┼──────────────────────────────────────────┤
│ ATOMICITY    │ Key storage + business logic: ONE tx.   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-086: Timeout and Deadline Pattern   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Idempotency = safe retry guarantee. The same operation
   applied N times has the same effect as applying it
   once. Idempotency keys make non-natural idempotent
   operations (POST, payment, email send) safe to retry.
2. Key scoping: the key must be the SAME for all retries
   of one logical operation; a NEW key for each new
   operation. Getting this wrong (new key per retry)
   defeats the entire mechanism.
3. Atomicity: store the idempotency key + result in
   the SAME database transaction as business logic.
   Key stored in a separate system (Redis) without
   transactional atomicity = not safe. The transaction
   boundary is the safety guarantee.

