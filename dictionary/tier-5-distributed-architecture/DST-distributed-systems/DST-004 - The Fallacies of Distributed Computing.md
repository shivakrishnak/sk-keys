---
id: DST-004
title: The Fallacies of Distributed Computing
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - dst
  - foundational
  - mental-model
status: draft
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /dst/the-fallacies-of-distributed-computing/
---

# DST-004 - The Fallacies of Distributed Computing

⚡ TL;DR - The Eight Fallacies of Distributed Computing (Peter Deutsch, 1994) are the eight incorrect assumptions almost every engineer makes when first building distributed systems — each assumption leads to a class of production bugs when violated.

| DST-004         | Category: Distributed Systems      | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------- | :-------------- |
| **Depends on:** | DST-001, DST-002                   |                 |
| **Used by:**    | DST-003, DST-044                   |                 |
| **Related:**    | DST-002, DST-003, DST-046, DST-044 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers write distributed code as if it were local code:
no timeouts ("the call will return"), no retry logic
("it will succeed"), no circuit breakers ("the network
is fine"). These assumptions are wrong, and every one
produces a category of production failure.

**THE BREAKING POINT:**
Peter Deutsch at Sun Microsystems (1994) noticed that
every new engineer on distributed projects made the
same mistakes. He compiled the list of eight fallacies
as a teaching tool. L. Peter Deutsch and James Gosling
later expanded it. The fallacies are not opinions;
they are empirically observed repeated mistakes.

**THE INVENTION MOMENT:**
Deutsch (1994), expanded by Bill Joy, Dave Lyon, and
James Gosling. Published as "Fallacies of Distributed
Computing Explained" by Arnon Rotem-Gal-Oz (2006) with
full explanations and production consequences.

**EVOLUTION:**
The eight fallacies became a standard onboarding framework
for distributed systems. Modern cloud services (AWS,
GCP, Azure) validate every fallacy: regional outages
(network unreliable), VPC bandwidth limits (bandwidth
is not infinite), latency between regions (latency is
not zero). The fallacies are as relevant today as in 1994.

---

### 📘 Textbook Definition

The **Eight Fallacies of Distributed Computing**:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology doesn't change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

Each is a false assumption that produces a specific
category of system failure when violated in production.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Eight wrong assumptions almost every developer makes about distributed systems — every assumption produces a class of production bug when violated.

**One analogy:**

> The fallacies are like the "things you wish someone
> told you before moving to a new country." You assume
> your phone works the same way, the roads are safe,
> everyone speaks your language. When each assumption
> is violated, something breaks. The fallacies are the
> list of cultural shocks waiting for every distributed
> systems engineer.

**One insight:**
Every distributed systems pattern (circuit breaker,
retry, timeout, idempotency) exists as a direct response
to one or more fallacies. Understanding the fallacies
makes the patterns inevitable rather than arbitrary.

---

### 🔩 First Principles Explanation

**EACH FALLACY AND ITS PRODUCTION CONSEQUENCE:**

```
Fallacy 1: Network is reliable
  Truth: Packets are dropped, connections timeout,
    network partitions occur (AWS RDS failover ~30s)
  Consequence: Applications hang without timeout;
    data gets lost; users see blank screens
  Fix: Timeout + retry + circuit breaker

Fallacy 2: Latency is zero
  Truth: AWS same-region ~1ms; cross-region ~80ms;
    cross-continent ~150ms; network call >> local call
  Consequence: N+1 query problem: calling DB in a loop
    makes 100 slow calls instead of 1 batch
  Fix: Batch calls; cache; async

Fallacy 3: Bandwidth is infinite
  Truth: AWS inter-AZ bandwidth is charged and limited;
    serialize large payloads; pagination
  Consequence: Sending full object graph over API;
    OOM on response deserialization
  Fix: Pagination; projection (return only needed fields)

Fallacy 4: Network is secure
  Truth: Network is hostile; internal networks are
    compromised regularly (SolarWinds 2020)
  Consequence: Service-to-service calls unencrypted;
    internal APIs unauthenticated
  Fix: mTLS between services; zero-trust networking

Fallacy 5: Topology doesn't change
  Truth: Cloud instances are replaced; IP addresses
    change; services scale in/out
  Consequence: Hard-coded IPs; no service discovery;
    breaks on instance replacement
  Fix: Service discovery (Consul, K8s DNS)

Fallacy 6: There is one administrator
  Truth: Microservices: each team owns their service;
    cross-team coordination is needed for changes
  Consequence: Schema migrations break other teams;
    undocumented API changes cascade
  Fix: API versioning; consumer-driven contract testing

Fallacy 7: Transport cost is zero
  Truth: Serialisation CPU + AWS data transfer costs
    are real (egress: ~$0.09/GB from AWS)
  Consequence: Chatty microservices; high API call
    volume; unexpectedly large AWS bills
  Fix: Batch operations; async messaging; CDN

Fallacy 8: Network is homogeneous
  Truth: Multiple protocols, encodings, versions;
    mobile clients, IoT, old browsers all different
  Consequence: Protocol mismatch between services;
    older clients can't parse new response format
  Fix: API versioning; content negotiation; protocol buffers
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Network unreliability and latency are physics.
**Accidental:** Not handling them because an engineer assumed they wouldn't occur.

---

### 🧪 Thought Experiment

**SETUP:**
You're writing a function that calls an internal
inventory service to check stock before completing a sale.

**VIOLATING EACH FALLACY:**

```java
// FALLACY 1 violation: no timeout
bool inStock = inventoryService.check(productId);
// Hangs forever if service is slow/down

// FALLACY 2 violation: calling in a loop (N+1)
for (Product p : cart.getProducts()) {
    bool inStock = inventoryService.check(p.getId());
    // 50 cart items = 50 network calls = 50ms each = 2.5s
}

// FALLACY 4 violation: HTTP (not HTTPS) internal call
http://inventory-service/check  // NOT https://
// Internal network is not secure

// FALLACY 6 violation: calling inventory API directly
// without contract; inventory team changes response format
// -> NullPointerException on new field name
```

**FOLLOWING THE FALLACIES:**

```java
// FIX: timeout + retry + batch call + contract testing
List<Long> productIds = cart.getProductIds();
// BATCH call (not N+1): one network call for all products
Map<Long, Boolean> stockStatus =
    inventoryService.checkBatch(productIds)
        .timeout(Duration.ofMillis(500))
        .fallback(ids -> Map.of())  // graceful degradation
        .execute();
```

---

### 🧠 Mental Model / Analogy

> The eight fallacies are the eight items on a pre-flight
> checklist for distributed systems. A pilot who skips
> the checklist because "I've done this before" will
> eventually have an incident. An engineer who doesn't
> handle the fallacies because "it works in local dev"
> will eventually have a production outage.

**Element mapping:**

- Checklist item = one fallacy
- Pre-flight = code review / design review
- Skipping = assuming the fallacy is true
- Incident = production outage from unhandled fallacy

Where this analogy breaks down: pre-flight checklists
are binary (done/not done); fallacy handling has degrees
of robustness.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Eight things that look true when you write code on
your laptop but are false in production: the network
will fail, calls will be slow, the network is not
secure, and nothing stays the same.

**Level 2 - How to use it (junior developer):**
For every remote call you write, ask: What happens
if this times out? What if it returns stale data?
What if the endpoint changes? These questions correspond
to Fallacies 1, 2, 5. Answering them reveals what
error handling you need.

**Level 3 - How it works (mid-level engineer):**
The fallacies are a lens for code review: for every
outbound network call, check: timeout configured?
retry with backoff? circuit breaker? idempotency on
retry? batching instead of N+1? mTLS or at minimum HTTPS?
service discovery instead of hard-coded IP?

**Level 4 - Why it was designed this way (senior/staff):**
The fallacies explain why distributed systems have so
many seemingly redundant patterns (retry AND circuit
breaker AND timeout AND bulkhead). Each pattern exists
because one fallacy is false. Retry handles unreliable
networks. Timeout handles non-zero latency. Circuit
breaker handles topology changes (a node disappeared).
Bulkhead handles bandwidth and transport cost (isolate
slow-path callers). The patterns form a complete response
to the fallacies.

**Expert Thinking Cues:**

- In every code review: "Which fallacy is this code assuming is true?"
- Network partition != network failure: partition means split, not down.
- Fallacy 6 (one administrator) explains why API versioning and contract testing exist.

---

### ⚙️ How It Works (Mechanism)

**Pattern-to-fallacy mapping:**

```
Fallacy 1 (unreliable network):
  -> Timeout: don't wait forever
  -> Retry: attempt again on transient failure
  -> Circuit breaker: stop calling a failing service
  -> Idempotency: safe to retry

Fallacy 2 (latency not zero):
  -> Batch API calls (avoid N+1)
  -> Caching (avoid repeated calls)
  -> Async (don't block on slow call)
  -> Connection pooling (avoid connection overhead)

Fallacy 4 (network not secure):
  -> mTLS service-to-service
  -> API gateway authentication
  -> Zero-trust networking

Fallacy 5 (topology changes):
  -> Service discovery (K8s DNS, Consul)
  -> Health checks
  -> No hard-coded IPs
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Design review checklist (fallacies-based):**

```
For each outbound service call:      <- YOU ARE HERE
  |
  [F1] Timeout configured?
    |-> Yes: how long? justify the value
    |-> No: add timeout
  |
  [F2] Avoiding N+1 calls?
    |-> Batch where possible
  |
  [F3] Response size bounded?
    |-> Pagination on list endpoints
  |
  [F4] Communication encrypted?
    |-> HTTPS minimum; mTLS for inter-service
  |
  [F5] Using service discovery?
    |-> K8s DNS or Consul; no hard-coded IPs
  |
  [F6] Contract tested?
    |-> Consumer-driven contract test (Pact)
  |
  [F7] Call volume monitored?
    |-> Alert on unexpected RPS spikes
  |
  [F8] Protocol versioned?
    |-> API version header; backward compatible changes
```

---

### ⚖️ Comparison Table

| Fallacy                | Pattern That Addresses It         | Cost of Ignoring           |
| ---------------------- | --------------------------------- | -------------------------- |
| 1: Network unreliable  | Timeout + retry + circuit breaker | Hangs, cascading failures  |
| 2: Zero latency        | Batch calls, caching              | N+1; slow P99              |
| 3: Infinite bandwidth  | Pagination, projection            | OOM; AWS egress cost       |
| 4: Secure network      | mTLS, zero-trust                  | Data breach                |
| 5: Topology static     | Service discovery                 | Broken calls after scaling |
| 6: One admin           | API versioning, contracts         | Breaking changes cascade   |
| 7: Zero transport cost | Batching, async messaging         | High AWS bills             |
| 8: Homogeneous network | Protocol versioning               | Client incompatibility     |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                           |
| -------------------------------------------------------- | --------------------------------------------------------------------------------- |
| "These don't apply to Kubernetes"                        | K8s adds service discovery, but all 8 fallacies still apply in a K8s cluster      |
| "gRPC/Protobuf solves Fallacy 8"                         | Protobuf helps with homogeneity but doesn't eliminate version mismatches          |
| "Internal microservices don't need mTLS"                 | SolarWinds proved internal networks are not secure; zero-trust is mandatory       |
| "AWS SLAs mean the network is reliable"                  | AWS SLA is for service availability, not per-call reliability; packets still drop |
| "The fallacies were written in 1994; cloud is different" | Every AWS re:Invent post-mortem validates one of the 8 fallacies                  |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Thread Pool Exhaustion (Fallacy 1 + 2)**
**Symptom:** Service unresponsive; thread pool at 100% utilisation.
**Root Cause:** No timeout on outbound calls; slow downstream blocks threads.
**Diagnostic:**

```bash
curl -s http://service/actuator/metrics/executor.active
# Or: thread dump to see all threads blocking on HTTP call
```

**Fix:** Set `connectionTimeout` and `readTimeout` on all HTTP clients; circuit breaker.

**Mode 2: N+1 Query Problem (Fallacy 2)**
**Symptom:** API P99 spikes proportionally to collection size.
**Diagnostic:** Add APM tracing; look for repeated identical calls in a single request trace.
**Fix:** Batch API; DataLoader pattern (GraphQL); join in DB.

**Mode 3: Breaking Change Cascade (Fallacy 6)**
**Symptom:** After deployment of Service A, Service B starts throwing 500s.
**Root Cause:** Service A changed response schema; Service B parses it.
**Fix:** Consumer-driven contract tests (Pact); schema registry; backward-compatible changes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-001 - What Is a Distributed System]]
- [[DST-002 - Why Distribution Is Hard]]

**Builds On This (learn these next):**

- [[DST-042 - Circuit Breaker]]
- [[DST-044 - Retry with Backoff]]
- [[DST-046 - Timeout]]

**Alternatives / Comparisons:**

- Martin Fowler's "Patterns of Enterprise Application Architecture" (related patterns)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      8 wrong assumptions engineers make  |
|                 about distributed systems           |
| PROBLEM         Each assumption violated in prod ->  |
| IT SOLVES       one category of outage              |
| KEY INSIGHT     Every resilience pattern exists as  |
|                 a direct answer to one fallacy      |
| USE WHEN        Designing / reviewing any code that  |
|                 makes a network call                |
| AVOID           "We're on the same VPC; it's fine"  |
| TRADE-OFF       Engineering effort vs resilience     |
| ONE-LINER       8 lies your network tells you       |
| NEXT EXPLORE    DST-042, DST-044, DST-046, DST-043  |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Fallacy 1 (network unreliable) → every outbound call needs timeout + retry + circuit breaker.
2. Fallacy 2 (zero latency) → N+1 calls is a performance anti-pattern; batch or cache.
3. Fallacy 4 (secure network) → internal networks are not secure; mTLS is required between services.

**Interview one-liner:**
"The eight fallacies (Deutsch, 1994) are the incorrect assumptions: network is reliable, latency is zero, bandwidth infinite, network secure, topology static, one admin, zero transport cost, homogeneous — each explains a category of distributed systems failure and the pattern that fixes it."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Systems fail at their assumptions. Explicitly listing
assumptions (and verifying them) is a meta-engineering
skill: before designing any system, list what you're
assuming is true. Each assumption is a potential failure
mode. Distribute the fallacies list to every engineer
joining a distributed systems team.

**Where else this pattern appears:**

- **Security** — threat modelling lists assumptions (the user is authenticated; data is valid) and attacks them
- **Database design** — ACID guarantees are assumptions that can be violated in specific edge cases
- **API design** — client assumptions about response format become breaking change liabilities

---

### 💡 The Surprising Truth

Fallacy 4 (the network is secure) is the most
dangerous and the most frequently violated. The 2020
SolarWinds attack compromised the software supply chain
of 18,000 organisations including the US Treasury and
NASA — via their internal, "trusted" network.
Attackers moved laterally for months on "secure" internal
networks before detection. If you're relying on "we're
on the same VPC" as your security model, you've violated
Fallacy 4. Zero-trust networking (mTLS between every
service, authentication on every API call, even internal
ones) is the direct engineering response to this fallacy.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A payment service calls an inventory
service and an email service to complete an order.
The inventory call takes 3 seconds (normally 10ms).
The payment service has no timeout. Describe the failure
cascade, identifying which fallacy each step violates.

_Hint:_ F1: no timeout (assuming reliable, fast response).
F2: assuming zero latency. Thread blocks 3s. If payment
service has 100 threads and 33 concurrent orders,
all threads are blocked → thread exhaustion → cascading
failure for the email service call too.

**Q2 (Design Trade-off):** Fallacy 5 says topology
changes. In Kubernetes, pods are replaced constantly
(rolling updates, scaling, evictions). How does Kubernetes
DNS address Fallacy 5, and what limitations does K8s DNS
still have (when does Fallacy 5 still bite you in K8s)?

_Hint:_ K8s DNS resolves service names to ClusterIP (stable VIP)
that load balances to pods. Fallacy 5 still bites on:
DNS TTL caching (short-lived connections see stale IPs),
keep-alive connections bypass load balancer on scaling,
headless services expose pod IPs directly.

**Q3 (Scale):** At what point does Fallacy 7 (zero
transport cost) become a significant engineering concern?
Estimate the AWS data transfer cost for a microservices
architecture with 50 services each making 1,000 RPS
inter-service calls with 10KB average payload size.

_Hint:_ 50 services × 1,000 RPS × 10KB = 500MB/s inter-AZ traffic.
AWS inter-AZ = $0.01/GB. 500MB/s = 43TB/day = $430/day = ~$15k/month
just for inter-AZ data transfer. This is when Fallacy 7
becomes a budget line item.
