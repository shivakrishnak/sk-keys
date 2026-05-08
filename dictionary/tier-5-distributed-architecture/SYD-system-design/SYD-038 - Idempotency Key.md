---
layout: default
title: "Idempotency Key"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /system-design/idempotency-key/
id: SYD-038
category: System Design
difficulty: ★★★
depends_on: HTTP APIs, Retries, Distributed Systems
used_by: Payment APIs, Order Creation, Webhooks
related: Idempotency, Polling vs Webhooks, Exactly-Once Semantics
tags:
  - apis
  - reliability
  - advanced
  - retries
  - distributed-systems
---

# SYD-038 - Idempotency Key

⚡ TL;DR - An idempotency key lets clients safely retry a request without creating duplicate side effects. The server stores the first successful result for a unique key and returns the same outcome for repeated requests with that key.

| #713            | Category: System Design                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | HTTP APIs, Retries, Distributed Systems                  |                 |
| **Used by:**    | Payment APIs, Order Creation, Webhooks                   |                 |
| **Related:**    | Idempotency, Polling vs Webhooks, Exactly-Once Semantics |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Client sends `POST /payments`, times out, retries, and accidentally charges the card twice.

**SOLUTION:**
Attach a unique request key so the server recognizes retries as the same operation.

---

### 📘 Textbook Definition

**Idempotency Key:** Client-generated unique identifier associated with a side-effecting request so servers can detect retries of the same logical operation and avoid performing the action more than once.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Same key means same operation, even if the request is retried multiple times.

**One analogy:**

> Giving a cashier a claim ticket. If the printer glitches and you ask again with the same ticket, the cashier hands you the same receipt instead of charging twice.

**One insight:**
Idempotency is a server-side deduplication contract, not just a client retry trick.

---

### 🧠 Mental Model

```
Client request:
  POST /payments
  Idempotency-Key: abc-123

Server logic:
  if key unseen:
    execute side effect
    store response
  else:
    return stored response
```

---

### 📶 Gradual Depth

**Level 1:** Retrying the same key should not repeat the side effect.

**Level 2:** Use idempotency for non-idempotent actions like payments, order creation, and webhook consumption.

**Level 3:** Store `(key, request fingerprint, response, status, expiration)` and reject mismatched payloads for reused keys.

**Level 4:** Idempotency is essential because networks fail in ambiguous ways: client timeout does not mean server failure. The key bridges that ambiguity.

---

### ⚙️ How It Works

```
1. Client generates UUID key per logical action
2. Server checks idempotency store
3. If absent:
     mark in-progress or lock row
     execute business operation
     persist canonical response
4. If present:
     return stored response
5. Expire old keys after retention window

Important edge case:
  Same key + different request body
    => reject as misuse
```

---

### 💻 Code Example

```python
class IdempotencyStore:
    def __init__(self):
        self.items = {}

    def process(self, key, payload_hash, action):
        existing = self.items.get(key)
        if existing:
            if existing["payload_hash"] != payload_hash:
                raise ValueError("Key reused with different payload")
            return existing["response"]

        response = action()
        self.items[key] = {
            "payload_hash": payload_hash,
            "response": response,
        }
        return response
```

---

### ⚖️ Comparison Table

| Technique               | Prevents duplicates | Handles ambiguous timeouts | Complexity |
| ----------------------- | ------------------- | -------------------------- | ---------- |
| Client retry alone      | No                  | No                         | Low        |
| Idempotency key         | Yes                 | Yes                        | Medium     |
| Distributed transaction | Sometimes           | Partially                  | High       |

---

### ⚠️ Common Misconceptions

| Misconception                  | Reality                                                                                |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| "POST cannot be safe to retry" | It can if the API supports idempotency keys.                                           |
| "Just use request body hash"   | Different legitimate requests may share similar shapes; keys represent logical intent. |

---

### 🚨 Failure Modes

**Failure Mode 1: Key reused for different operation**

**Symptom:**
Client accidentally reuses an old key for a different payment.

**Prevention:**
Store payload fingerprint and reject mismatches.

---

**Failure Mode 2: Race on first insert**

**Symptom:**
Two identical retries arrive simultaneously and both execute.

**Prevention:**
Unique constraint on key plus transactional insert or distributed lock.

---

### 📌 Quick Reference

```
Idempotency key:
  Purpose: safe retries for side-effecting operations
  Store: key + payload hash + canonical response
  Must handle: duplicates, races, expiration, payload mismatch
```

---

### 🧠 Questions

**Q1.** Should idempotency keys be global, per endpoint, or per customer?

**Q2.** If the first request is still in progress, what should the retry return?
