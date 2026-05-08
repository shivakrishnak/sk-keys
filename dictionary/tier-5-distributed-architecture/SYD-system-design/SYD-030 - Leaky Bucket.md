---
layout: default
title: "Leaky Bucket"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /system-design/leaky-bucket/
id: SYD-030
category: System Design
difficulty: ★★★
depends_on: Rate Limiting, Queue Data Structures
used_by: Traffic Shaping, Request Queuing
related: Token Bucket, Rate Limiting, FIFO
tags:
  - rate-limiting
  - queuing
  - advanced
  - smoothing
  - fairness
---

# SYD-030 - Leaky Bucket

⚡ TL;DR - Rate limiting algorithm using FIFO queue (bucket) with constant-rate drain (leak). Requests queue; processed at fixed rate. Smooths traffic, ensures fairness, prevents bursts from affecting processing time.

| #705            | Category: System Design              | Difficulty: ★★★ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Rate Limiting, Queue Data Structures |                 |
| **Used by:**    | Traffic Shaping, Request Queuing     |                 |
| **Related:**    | Token Bucket, Rate Limiting, FIFO    |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Token bucket allows bursts (drain bucket fast). Leaky bucket prevents bursts: queue all requests, process at fixed rate. Trade: requests wait, but processing smooth.

**COMPARISON:**

- Token bucket: bursty allowed, requests fast
- Leaky bucket: smooth processing, requests may wait

---

### 📘 Textbook Definition

**Leaky Bucket:** Rate limiting algorithm using FIFO queue (bucket). Requests queue in bucket; leak (process) at constant rate. If bucket full, new requests rejected. Ensures smooth, predictable processing rate.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Queue requests (FIFO). Process at 10 req/sec. Burst = all queued. Normal = processed immediately.

**One analogy:**

> Water: bucket fills from tap (requests). Drains at constant rate (processing). Burst fills bucket; sustained fills and leaks.

**One insight:**
Smooth processing, not bursty throughput.

---

### 🧠 Mental Model

Leaky bucket = physical water bucket:

```
[Incoming requests]
        ↓ (tap)
    [Queue/Bucket]
        ↓ (hole at bottom, constant leak rate)
    [Processed requests]
```

---

### ⚙️ How It Works

```
Algorithm:
──────────
1. Queue capacity = 100 requests
2. Leak rate = 10 req/sec
3. Current queue size = 0

On request arrival:
  1. If queue < capacity:
       - Add to queue
       - QUEUED
     Else:
       - Queue full
       - REJECTED

  2. Process queue at leak rate (10/sec):
       - Remove from front of queue
       - Process and respond
       - Latency = queue_depth / leak_rate

Example:
  Burst arrives: 50 requests in 1 sec
    - All 50 queued (capacity 100)
    - Processing starts at 10/sec
    - Request 1: processed immediately (queued 0)
    - Request 11: queued 10, latency = 10/10 = 1 sec
    - Request 50: queued 49, latency = 49/10 = 4.9 sec
```

---

### 💻 Code Example

```python
from collections import deque
from time import time, sleep
import threading

class LeakyBucket:
    def __init__(self, capacity, leak_rate_per_sec):
        self.capacity = capacity
        self.leak_rate = leak_rate_per_sec
        self.queue = deque()
        self.last_leak_time = time()
        self.lock = threading.Lock()

    def add_request(self, request):
        with self.lock:
            if len(self.queue) < self.capacity:
                self.queue.append(request)
                return True
            else:
                return False  # Queue full, reject

    def leak(self):
        """Process requests at leak rate"""
        while True:
            with self.lock:
                if self.queue:
                    request = self.queue.popleft()
                    print(f"Processing: {request}")

            # Sleep to maintain leak rate
            sleep(1.0 / self.leak_rate)

# Usage
bucket = LeakyBucket(capacity=100, leak_rate_per_sec=10)

# Start leaking thread
leak_thread = threading.Thread(target=bucket.leak, daemon=True)
leak_thread.start()

# Add requests
for i in range(50):
    if bucket.add_request(f"Request {i}"):
        print(f"Queued request {i}")
    else:
        print(f"REJECTED: request {i} (queue full)")
```

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                |
| ------------------------------------------ | -------------------------------------------------------------------------------------- |
| "Leaky bucket = token bucket with queuing" | Incorrect. Different trade-offs: leaky = smooth processing, token = smooth submission. |
| "Queuing requests is always better"        | No. Requests may timeout while queued. Trade-off between fairness and responsiveness.  |

---

### 🚨 Failure Modes

**Failure Mode: Queue Memory Exhaustion**

**Symptom:**
Queue fills beyond capacity (memory leak). Server crashes.

**Prevention:**
Set queue capacity. Reject excess. Monitor queue depth.

---

### 📌 Quick Reference

```
Leaky Bucket vs Token Bucket:

  Token Bucket:
    - Bursty throughput allowed
    - Fast response (no queuing)
    - Use: APIs, traffic that tolerates variation

  Leaky Bucket:
    - Smooth, predictable throughput
    - Requests may wait (queued)
    - Use: Network traffic shaping, load balancing
```

---

### 🧠 Questions

**Q1.** Bucket capacity 100, leak rate 10 req/sec. 100 requests arrive simultaneously. Latency of last request?

**Q2.** Leaky bucket queues requests. When is this better than immediate rejection?
