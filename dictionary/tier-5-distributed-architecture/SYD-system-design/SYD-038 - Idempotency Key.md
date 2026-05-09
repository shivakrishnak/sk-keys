---
id: SYD-038
title: Idempotency Key
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-037, SYD-039
used_by: SYD-044, SYD-047, SYD-048
related: SYD-037, SYD-039, SYD-041
tags:
  - architecture
  - distributed
  - reliability
  - pattern
  - bestpractice
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /syd/idempotency-key/
---

# SYD-038 - Idempotency Key

⚡ TL;DR - An idempotency key lets clients safely retry failed operations without risk of duplicate side effects - the server uses the key to detect and skip repeated requests.

| SYD-038         | Category: System Design          | Difficulty: ★★☆ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | SYD-037, SYD-039                 |                 |
| **Used by:**    | SYD-044, SYD-047, SYD-048       |                 |
| **Related:**    | SYD-037, SYD-039, SYD-041       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Networks fail. Servers crash. Clients time out mid-request. Without a mechanism to detect duplicate submissions, retrying a payment results in two charges. Retrying an order creates two orders. Every retry is a gamble between losing the operation and duplicating it.

**THE BREAKING POINT:**
In distributed systems, "exactly-once delivery" is provably impossible at the network layer. But "exactly-once processing" at the application layer is achievable - if and only if the server can detect repeated requests. Without this, clients must choose between data loss (no retry) and duplicates (retry).

**THE INVENTION MOMENT:**
The idempotency key pattern formalizes a contract: the client generates a unique key per operation and sends it with the request. The server stores the key + result. On duplicate request with same key, return the stored result without re-executing.

**EVOLUTION:**
Early databases used unique constraints to prevent duplicate inserts. Payment systems evolved idempotency keys as a first-class API concept. Stripe popularized the `Idempotency-Key` header in REST APIs. Modern event queues, message brokers, and gRPC services all implement variations of this pattern.

---

### 📘 Textbook Definition

An **idempotency key** is a unique client-generated identifier attached to a mutating API request. The server uses this key to deduplicate: if the same key is received again, the server returns the previously computed result without re-executing the operation. Idempotency guarantees that applying the same request multiple times has the same effect as applying it once.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A unique ticket that says "I already asked this - return my previous answer, don't do it again."

**One analogy:**

> An idempotency key is like submitting an expense report with a unique reference number. If your accountant receives it twice, they recognize the reference and don't reimburse you twice.

**One insight:**
Idempotency is not about immutability - it is about recognizing repeated intent and short-circuiting repeated execution. The operation may be destructive; the key makes retries safe.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Networks are unreliable - requests can fail after the server has already processed them.
2. Clients cannot know whether a timeout means the server failed before, during, or after processing.
3. Retrying without deduplication produces duplicate side effects.
4. The client is the only party that can generate a truly unique request intent identifier.

**DERIVED DESIGN:**
Client generates UUID per logical operation. Sends it in `Idempotency-Key` header or request body. Server: (a) checks if key exists in idempotency store, (b) if yes, return stored response, (c) if no, execute operation + store key + result atomically.

**THE TRADE-OFFS:**
**Gain:** Safe retries with no duplicate side effects; decouples network reliability from business correctness.
**Cost:** Server must maintain idempotency store (storage cost + lookup on every request); key storage must outlive the retry window; race conditions between concurrent requests with same key.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The server must distinguish first execution from retry. This requires state.
**Accidental:** TTL management, concurrent lock acquisition, store replication for HA.

---

### 🧪 Thought Experiment

**SETUP:** A user clicks "Pay $100" and the request times out after 3 seconds.

**WHAT HAPPENS WITHOUT IDEMPOTENCY KEY:**
The client retries. The server charges $100 again. The user sees two $100 charges. Support ticket filed. Trust eroded. Even with a unique constraint on transaction ID, if the first request completed and the response was lost in transit, the second request fails with "duplicate transaction" - which looks like an error, not a success - so the client doesn't know the payment succeeded.

**WHAT HAPPENS WITH IDEMPOTENCY KEY:**
Client generates `idem_key = "pay_abc123"`. Sends first request - server processes, stores `{key: "pay_abc123", result: {charge_id: "ch_xyz", status: "success"}}`. Response times out. Client retries with same `idem_key`. Server finds stored result, returns `{charge_id: "ch_xyz", status: "success"}` without charging again. Client receives success. User is charged once.

**THE INSIGHT:**
Idempotency keys shift the correctness burden from "did the network deliver this?" to "did the client retry with the same key?" - which is entirely within the client's control. The server becomes a content-addressable response cache keyed on client intent.

---

### 🧠 Mental Model / Analogy

> An idempotency key is like a check number at a bank. If you write check #1042, the bank processes it once. If you accidentally write two checks with number #1042, the bank flags the second as duplicate and returns it. The check number is the idempotency key.

- **Check number** = idempotency key UUID
- **Writing the check** = sending the API request
- **Bank processes the check** = server executes the operation
- **Duplicate detection** = server's idempotency store lookup
- **Return to sender** = returning the cached response

Where this analogy breaks down: banks have strong legal infrastructure for duplicate detection; in distributed systems you must implement this yourself, including handling concurrent duplicates.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you retry a payment because your app froze, you don't want to be charged twice. An idempotency key is a unique number you attach to your request so the server knows "this is the same payment I sent before - don't charge again."

**Level 2 - How to use it (junior developer):**
Generate a UUID per operation (not per request). Send it as `Idempotency-Key: <uuid>` header. Store it before sending. On timeout or network error, retry with the same key. Do not generate a new key on retry - that defeats the purpose.

**Level 3 - How it works (mid-level engineer):**
Server receives request + idempotency key. Before executing, checks distributed cache / DB for existing result. If found, returns cached. If not, executes operation and atomically stores key + result. Two concurrent requests with same key: use distributed lock or DB unique constraint to prevent double execution. Set TTL on stored keys (typically 24h-7d).

**Level 4 - Why it was designed this way (senior/staff):**
The atomic write of {key + result} is the hardest part. It must be atomic to prevent race conditions (two threads process the same key simultaneously). Options: DB transaction with unique constraint on key column, Redis SET NX (set if not exists), or optimistic locking. The idempotency store must be on the same transactional boundary as the operation (same DB) or you risk a partial write where the operation succeeds but the key is never stored - causing double-execution on retry.

**Expert Thinking Cues:**
- Ask: "What is our idempotency key TTL, and what happens after it expires?"
- Ask: "Is our key store on the same transactional boundary as the operation?"
- Red flag: generating a new UUID on every retry
- Red flag: idempotency store in a separate DB from the operation - split-brain risk

---

### ⚙️ How It Works (Mechanism)

```
Client:
  key = uuid()
  store key locally (for retry)
  POST /payments {amount: 100, idempotency_key: key}

Server (first request):
  1. BEGIN TRANSACTION
  2. SELECT result FROM idem_store WHERE key = ?
     -> NULL (first time)
  3. Execute payment operation
  4. INSERT INTO idem_store (key, result, expires_at)
     VALUES (?, ?, NOW() + INTERVAL 24 HOURS)
  5. COMMIT
  6. Return result to client

Server (retry with same key):
  1. BEGIN TRANSACTION
  2. SELECT result FROM idem_store WHERE key = ?
     -> {charge_id: "ch_xyz", status: "success"}
  3. Return cached result (skip payment execution)
  4. COMMIT (no-op)
```

**Concurrent requests with same key:**
```
Thread A         Thread B
  |                |
  INSERT key     INSERT key
  (succeeds)     (fails: UNIQUE violation)
  |                |
  Execute op     Wait for A to commit
  |                |
  COMMIT         Read A's result
  |                |
  Return A's     Return A's result
  result
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Client generates UUID key]
         |
         v
[POST /charge {key: uuid}]   <- YOU ARE HERE
         |
         v
[Server: check idem store]
         |
     NOT FOUND
         |
         v
[Execute + store result atomically]
         |
         v
[Return result to client]
         |
         v
[Client stores success state]
```

**FAILURE PATH (timeout + retry):**
```
[Client sends request with key K]
         |
   [Network timeout - response lost]
         |
         v
[Client retries with SAME key K]
         |
         v
[Server: check idem store -> FOUND]
         |
         v
[Return stored result (no re-execution)]
         |
         v
[Client receives success]
```

**WHAT CHANGES AT SCALE:**
Idempotency store becomes a hot table at high RPS. Use Redis with TTL for the store - not the primary DB. Partition the store by key prefix if needed. The unique constraint query must be fast (indexed on key column).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent retries with same key must not both execute the operation. Use `INSERT ... ON CONFLICT DO NOTHING` + check return or `SET NX` in Redis. The window between "key not found" and "key inserted" is the critical section - protect with a distributed lock or atomic conditional insert.

---

### 💻 Code Example

**BAD - generating new UUID on every retry:**
```python
# BAD: new key on each attempt = no deduplication
def pay(amount):
    for attempt in range(3):
        key = str(uuid.uuid4())  # NEW UUID each time!
        resp = requests.post("/payments", json={
            "amount": amount,
            "idempotency_key": key
        })
        if resp.status_code == 200:
            return resp.json()
        time.sleep(2 ** attempt)
```

**GOOD - same key on all retries for same operation:**
```python
import uuid, time, requests

def pay(amount, idempotency_key=None):
    # Key generated ONCE per logical operation
    key = idempotency_key or str(uuid.uuid4())
    for attempt in range(3):
        try:
            resp = requests.post(
                "/payments",
                json={"amount": amount},
                headers={"Idempotency-Key": key},
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.Timeout:
            # Retry with SAME key
            time.sleep(2 ** attempt)
    raise Exception(f"Failed after 3 attempts: key={key}")
```

**GOOD - server-side idempotency store (PostgreSQL):**
```python
import psycopg2, json

def idempotent_charge(conn, idem_key, amount):
    with conn.cursor() as cur:
        # Atomic: insert or return existing
        cur.execute("""
            INSERT INTO idempotency_keys
              (key, result, expires_at)
            VALUES (%s, NULL, NOW() + INTERVAL '24h')
            ON CONFLICT (key) DO NOTHING
            RETURNING id
        """, (idem_key,))
        row = cur.fetchone()
        if row is None:
            # Key already exists - return cached result
            cur.execute(
                "SELECT result FROM idempotency_keys"
                " WHERE key = %s", (idem_key,)
            )
            return json.loads(cur.fetchone()[0])

        # First execution: process then update result
        charge = execute_charge(conn, amount)
        cur.execute("""
            UPDATE idempotency_keys
            SET result = %s
            WHERE key = %s
        """, (json.dumps(charge), idem_key))
        conn.commit()
        return charge
```

**How to test / verify correctness:**
- Submit same key twice concurrently - assert operation executes once, both calls return same result.
- Submit different key with same payload - assert operation executes twice.
- Submit same key after TTL expires - assert operation executes again (fresh state).

---

### ⚖️ Comparison Table

| Approach               | Mechanism          | Scope          | Failure mode          |
| ---------------------- | ------------------ | -------------- | --------------------- |
| Idempotency key        | Client-generated UUID | Per operation | Key not stored atomically |
| Unique constraint (DB) | DB UNIQUE index    | Single DB      | Fails across DB shards |
| Redis SET NX           | Atomic CAS         | Cross-service  | Redis unavailability  |
| Natural idempotency    | GET/PUT semantics  | HTTP methods   | Not valid for POST     |
| Conditional request    | ETag/If-Match      | Resource state | Complex client logic  |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Idempotency key = request ID" | A request ID tracks a single attempt. An idempotency key represents the logical operation and must stay constant across all retries of that operation. |
| "GET and PUT are already idempotent so I don't need keys" | True for pure HTTP GET/PUT. False for POST. Most business operations use POST and need explicit idempotency handling. |
| "Storing the key prevents double charges" | The key store must be on the same transactional boundary as the charge. A crashed server that completed the charge but failed to store the key will double-charge on retry. |
| "Idempotency keys make my API stateless" | The opposite: idempotency keys require the server to maintain state (the result cache) for the TTL window. They reduce duplication risk by adding intentional statefulness. |
| "24-hour TTL is always sufficient" | TTL must exceed your longest reasonable retry window. If clients retry for 48 hours, a 24-hour TTL creates a duplication window. Match TTL to your SLA. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Key not stored atomically with operation**

**Symptom:** Duplicate charges despite idempotency keys being used.

**Root Cause:** The operation committed but the key storage failed (separate transactions or crash between them).

**Diagnostic:**
```sql
-- Find charges without corresponding idem key
SELECT c.id, c.amount, c.created_at
FROM charges c
LEFT JOIN idempotency_keys k ON k.charge_id = c.id
WHERE k.id IS NULL AND c.created_at > NOW() - INTERVAL '1d';
```

**Fix:** Store key + result in the same DB transaction as the operation.

**Prevention:** Use `INSERT INTO idem_keys ... RETURNING id` in the same transaction as `INSERT INTO charges`.

---

**Failure Mode 2: New UUID generated on each retry**

**Symptom:** Customer charged multiple times for same payment attempt.

**Root Cause:** Developer generated new `uuid4()` on each retry call instead of reusing the key.

**Diagnostic:**
```python
# Check payment logs for same user_id + amount
# in short time window with different idem keys
SELECT user_id, amount, idempotency_key, created_at
FROM payments
WHERE user_id = ? AND created_at > NOW() - INTERVAL '10m';
```

**Fix:** Generate key once, pass it through all retry attempts.

**Prevention:** Code review check: idempotency key generation must appear outside the retry loop.

---

**Failure Mode 3: Concurrent requests with same key both execute**

**Symptom:** Two threads with same key both see "key not found" and both execute the operation.

**Root Cause:** Race condition between SELECT (check) and INSERT (store).

**Diagnostic:**
```sql
-- Look for duplicate key violations in key store table
SELECT key, COUNT(*)
FROM idempotency_keys
GROUP BY key HAVING COUNT(*) > 1;
```

**Fix:** Use `INSERT ... ON CONFLICT DO NOTHING` + read back, or Redis `SET NX`.

**Prevention:** Never use SELECT then INSERT for idempotency check - use atomic operations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-037 - Polling vs Webhooks]] - context for where idempotency keys are required (webhook retries)
- [[SYD-039 - Distributed Locks]] - the mechanism used to protect idempotency key critical sections

**Builds On This (learn these next):**
- [[SYD-041 - Write-Ahead Logging (System)]] - WAL provides durability guarantees that support idempotency
- [[SYD-044 - Rate Limiter Design]] - rate limiting + idempotency together protect payment APIs
- [[SYD-047 - Notification System Design]] - notification retries require idempotent event consumers

**Alternatives / Comparisons:**
- [[SYD-039 - Distributed Locks]] - alternative for preventing duplicate execution via mutual exclusion

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Client-generated UUID that makes │
│              │ retries safe on server side      │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Retrying failed requests causes  │
│ IT SOLVES    │ duplicate operations (charges)   │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Generate key ONCE per logical    │
│              │ operation, reuse on ALL retries  │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Any POST that charges, sends     │
│              │ email, or mutates critical state │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Pure reads; operations where     │
│              │ duplicates are tolerable         │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Storage and lookup cost vs       │
│              │ duplicate operation risk         │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Same key = cached result,       │
│              │ not repeated execution."         │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-039 Distributed Locks        │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Generate the key once per logical operation - never inside the retry loop.
2. Store the key and result atomically with the operation in the same transaction.
3. Set TTL to exceed your longest reasonable retry window.

**Interview one-liner:** "An idempotency key is a client-generated UUID stored with the server result so retries return the cached response instead of re-executing - making at-most-once semantics achievable despite unreliable networks."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In unreliable systems, the party that generates intent (the client) must also supply the uniqueness token that prevents duplication. The server cannot guess client intent from payload alone - the same payload may be two different operations.

**Where else this pattern appears:**
- **Database UPSERT:** `INSERT ... ON CONFLICT UPDATE` is an idempotency pattern at the SQL layer.
- **Event sourcing:** Event IDs serve as idempotency keys - the event log deduplicates on ID.
- **Infrastructure as Code:** Terraform resource IDs ensure applying the same plan twice does not create duplicate cloud resources.

---

### 💡 The Surprising Truth

Idempotency keys solve a problem that "exactly-once delivery" cannot: even if the network delivers a message exactly once, the server can crash after processing it but before responding. To the client, this looks identical to "not delivered" - triggering a retry that truly is a second delivery. No messaging infrastructure can distinguish these cases; only application-level deduplication via a stored key can.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A payment service uses Redis for idempotency key storage and PostgreSQL for charges. A network partition isolates Redis for 30 seconds. What happens to payment requests during the partition, and what happens when Redis comes back?

*Hint:* Consider what the server does when it cannot check the idempotency store (fail open = duplicate risk, fail closed = availability loss). Then look at how Stripe handles Redis unavailability in their idempotency implementation.

**Q2 (Scale):** Your API processes 100K requests/sec. Each request has an idempotency key with a 24-hour TTL. How many keys are stored in your idempotency store at steady state, and what are the storage implications if the average key+result is 2KB?

*Hint:* Calculate total stored keys = RPS x TTL in seconds = 100K x 86400. Then calculate storage = keys x 2KB. Compare this to Redis costs and explore key compression strategies.

**Q3 (Design Trade-off):** A refund API uses idempotency keys. A customer calls support and the agent triggers a refund manually. The original idempotency key was lost. Should you generate a new key (risking duplicate refund) or require the original key (risking no refund)? What system design prevents this dilemma?

*Hint:* Look at how Stripe separates idempotency keys (client-generated, per-attempt) from idempotent resource IDs (server-generated, per-logical-operation), and consider whether the refund should have been initiated with a resource-level idempotency check rather than a key-based one.
