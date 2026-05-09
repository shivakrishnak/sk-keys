---
id: DPT-065
title: Patterns in Distributed Systems
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-064, DPT-053, DPT-054
used_by: DPT-071, DPT-069
related: DST-001, MSV-001, SAP-018
tags:
  - pattern
  - distributed
  - advanced
  - architecture
  - reliability
status: complete
version: 1
layout: default
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 65
permalink: /dpt/patterns-in-distributed-systems/
---

# DPT-065 - Patterns in Distributed Systems

⚡ TL;DR - Distributed systems introduce forces (partial failure, network unreliability, consistency vs. availability) that require a dedicated pattern vocabulary beyond GoF — covering communication, resilience, data management, and observability.

| DPT-065 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-064, DPT-053, DPT-054 | |
| **Used by:** | DPT-071, DPT-069 | |
| **Related:** | DST-001, MSV-001, SAP-018 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team builds a microservices system using GoF patterns, which were designed for single-process, in-memory object graphs. Network calls are treated like method calls. There is no retry logic, no circuit breaker, no idempotency key, no distributed tracing. The first time a downstream service slows down, the calling service's thread pool fills with blocked threads and the entire system cascades to a halt. The team learns distributed systems failure modes one incident at a time.

**THE BREAKING POINT:**
Black Friday peak load. Service A calls Service B, which calls Service C. Service C has a 5-second GC pause. Service B's thread pool fills up. Service A's thread pool fills up. Within 45 seconds, the entire platform is returning 503s. A known distributed systems pattern — Circuit Breaker — would have fail-fast isolated the fault at Service B in under 1 second.

**THE INVENTION MOMENT:**
Michael Nygard's "Release It!" (2007) was the practitioner's first comprehensive taxonomy of distributed systems failure patterns and their countermeasures. Netflix's Hystrix library operationalised Circuit Breaker at scale. Gregor Hohpe and Bobby Woolf's "Enterprise Integration Patterns" (2003) catalogued messaging patterns. Together these established a distributed systems pattern vocabulary that complemented GoF's in-process catalogue.

**EVOLUTION:**
The pattern vocabulary has expanded continuously: Saga (2-phase commit alternative), Outbox (reliable event publishing), Sidecar/Service Mesh (cross-cutting concerns as injected proxy), CQRS (asymmetric read/write architecture), Event Sourcing (immutable event as source of truth). Cloud-native computing has added Infrastructure-as-Code patterns, health endpoint patterns, and zero-trust security patterns.

---

### 📘 Textbook Definition

**Patterns in Distributed Systems** are reusable solutions to recurring structural and behavioural challenges specific to multi-process, networked computing environments. Unlike GoF patterns (which address in-process object collaboration), distributed systems patterns address: partial failure (process or network failure that affects some but not all nodes), network unreliability (latency, packet loss, ordering violations), consistency vs. availability trade-offs (CAP theorem consequences), observability gaps (state is distributed across services), and cross-service coordination (choreography vs. orchestration).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Distributed systems patterns solve forces that GoF patterns cannot — partial failure, network unreliability, and consistency vs. availability trade-offs.

> Think of it like the difference between rules for working alone vs. rules for a team. Working alone, you have rules about how you organise your own work (GoF patterns). Working as a distributed team across time zones with unreliable communication channels, you need completely different rules: what happens when a team member goes offline? How do you avoid doing the same work twice? How do you know the whole team has agreed on a decision? Distributed systems patterns are the team communication and coordination rules.

**One insight:** The critical distinction from GoF: in a distributed system, any operation can fail partially — the request is sent but the response is never received. GoF patterns have no concept of partial failure. Every distributed systems pattern accounts for it.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Networks are unreliable: messages can be lost, delayed, reordered, or duplicated. Every distributed pattern must handle at least one network failure mode.
2. Partial failure is the rule, not the exception: in a system of N services, the probability that at least one is degraded approaches 1 as N grows.
3. There is no globally consistent clock: timestamps from different services cannot be safely compared for ordering. Patterns must handle temporal uncertainty.
4. The CAP theorem constrains every distributed data pattern: partition tolerance is mandatory; consistency and availability must be traded off explicitly.

**DERIVED DESIGN:**
Distributed patterns cluster by the force they address: (a) Resilience patterns (Circuit Breaker, Retry, Bulkhead, Timeout) address partial failure. (b) Communication patterns (Outbox, Saga, Event-Driven) address reliable coordination. (c) Data patterns (CQRS, Event Sourcing, Eventual Consistency) address distributed state. (d) Observability patterns (Distributed Tracing, Health Endpoint) address visibility.

**THE TRADE-OFFS:**

**Gain:** Systems that degrade gracefully under failure rather than cascading. Decoupled services that can scale independently. Explicit consistency models that prevent silent data corruption.

**Cost:** Every distributed pattern adds latency, complexity, or both. Circuit Breaker adds state machine overhead. Outbox adds a DB table and polling. Saga adds compensating transaction logic. The cost is justified only when the force is present.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Partial failure, network unreliability, and consistency trade-offs are inherent to distributed computing. Patterns that address these are essential complexity management.

**Accidental:** Applying all resilience patterns to every inter-service call regardless of failure probability and consequence adds overhead that is not justified by the actual risk profile.

---

### 🧪 Thought Experiment

**SETUP:** Service A calls Service B synchronously (HTTP). Service B calls Service C synchronously (HTTP). Average response time is 200ms. What happens when Service C has a 30-second timeout?

**WITHOUT RESILIENCE PATTERNS:** Service B waits 30s for C. Service A waits 30s+ for B. A's thread pool has 50 threads. If 50 concurrent requests reach A during C's outage, all 50 threads are blocked waiting for B. A is now effectively down. Downstream consumers of A see same 30-second delay. Cascading failure across 3 services in under 2 minutes.

**WITH CIRCUIT BREAKER + TIMEOUT + BULKHEAD:**
- Timeout on B→C: fail after 5 seconds
- Circuit Breaker on B→C: after 5 failures, open circuit, fail immediately
- Bulkhead on A→B: limit C-related calls to a dedicated thread pool of 10; other A requests unaffected

**Outcome:** C's outage is isolated to B→C path. B returns cached or degraded response in <1 second. A's 50-thread pool serves requests normally. 40 threads handle other logic. Only C-dependent features degrade — everything else remains fully functional.

**THE INSIGHT:** Resilience patterns don't prevent failures — they contain them. The difference between cascading failure (total outage) and graceful degradation (partial outage) is whether isolation patterns are in place.

---

### 🧠 Mental Model / Analogy

> Distributed systems patterns are like the safety systems in a nuclear power plant. Normal operation uses standard engineering principles (GoF-level patterns = basic engineering). But a nuclear plant adds safety layers specifically for failure modes: redundant cooling loops (Bulkhead), automatic shutdown triggers (Circuit Breaker), containment vessels (Bulkhead isolation), emergency procedures (Saga compensation). No single safety system handles all failure modes — they layer and compose. When a failure occurs, the safety systems contain it locally rather than letting it propagate to the reactor core.

- **Redundant cooling loops** = Bulkhead (isolate failure paths so they cannot consume shared resources)
- **Automatic shutdown trigger** = Circuit Breaker (fail fast when downstream is unhealthy)
- **Containment vessel** = service isolation boundary (failures do not propagate cross-service)
- **Emergency procedures** = Saga compensating transactions (rollback when distributed workflow fails)
- **Normal engineering principles** = GoF patterns (for logic within each service)

Where this analogy breaks down: nuclear plant safety is binary (safe / unsafe). Distributed system degradation is gradual and partial — which makes the "how degraded is acceptable?" question always contextual.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When many computers need to work together but their network connections are unreliable, new problems arise: what if a message gets lost? What if one computer slows down and blocks all the others? Distributed systems patterns are the solutions engineers have found to these specific problems — ways to keep the overall system working even when individual parts fail.

**Level 2 - How to use it (junior developer):**
For every inter-service call: add a timeout (prevent indefinite blocking), a retry with exponential backoff and jitter (handle transient failures), and an idempotency key (ensure retried operations produce the same result once). For critical downstream dependencies: add a Circuit Breaker (fail fast when downstream is unhealthy). These four patterns cover >80% of distributed call failure modes.

**Level 3 - How it works (mid-level engineer):**
Patterns group by phase of distributed interaction: at rest (Event Sourcing, CQRS), in flight (Retry, Circuit Breaker, Timeout, Bulkhead), coordination (Saga, Outbox), and visibility (Distributed Tracing, Health Endpoint, Correlation ID). Each group addresses a different distributed systems inevitability. Service mesh frameworks (Istio, Envoy) implement many communication patterns as infrastructure, removing them from application code.

**Level 4 - Why it was designed this way (senior/staff):**
Distributed patterns encode the lessons of the "fallacies of distributed computing" (network is reliable, latency is zero, bandwidth is infinite, topology doesn't change, etc.). Each fallacy produces a class of failure; each failure class has a pattern response. A staff engineer designs the service mesh configuration to enforce patterns as infrastructure policy rather than relying on every team's application-level implementation — policies applied at the platform level prevent teams from skipping resilience patterns under time pressure.

**Expert Thinking Cues:**
- Service mesh moves Retry, Circuit Breaker, and Timeout out of application code into infrastructure. Understand what your platform already provides before implementing these in code.
- Idempotency is the most under-implemented pattern. Every mutating operation must be idempotent if retries are in place.
- Event ordering is not guaranteed across partitions. Design patterns that tolerate message reordering rather than assuming ordered delivery.

---

### ⚙️ How It Works (Mechanism)

**Distributed Pattern Categories:**

```
RESILIENCE           COORDINATION         OBSERVABILITY
Circuit Breaker      Outbox               Distributed Trace
Retry + Backoff      Saga (Choreograph)   Correlation ID
Timeout              Saga (Orchestrate)   Health Endpoint
Bulkhead             Transactional Inbox  Log Aggregation
Rate Limiter         Idempotent Consumer  Metrics Collection

DATA MANAGEMENT      COMMUNICATION        DEPLOYMENT
CQRS                 API Gateway          Sidecar
Event Sourcing       Service Mesh         Ambassador
Eventual Consistency Anti-Corruption      Strangler Fig
Materialized View      Layer              Blue/Green
```

**Circuit Breaker state machine:**

```
         failure threshold
CLOSED ──────────────────► OPEN
  ▲                          │
  │ success                  │ timeout
  │                          ▼
HALF-OPEN ◄──────────── OPEN
  │ probe request success
  └───► CLOSED
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (with patterns applied):**

```
Client Request → API Gateway
          │
   Rate Limiter check
          │
Service A: Bulkhead allocates
  thread from B-specific pool
          │
Service A → Service B (HTTP)
  Timeout: 5s
  Retry: 3x with backoff
  Circuit Breaker: check state ← YOU ARE HERE
          │
   ┌──────┴──────┐
OPEN (CB)      CLOSED (CB)
   │              │
Fail fast       Call proceeds
Fallback resp   with tracing header
   │              │
   └──────┬───────┘
          │
Correlation ID propagated
Response returned / cached
```

**FAILURE PATH:**
Circuit Breaker opens → all B-dependent calls fail fast → A returns degraded response from cache → no thread pool exhaustion → other A features unaffected → B recovers → CB moves to HALF-OPEN → probe request succeeds → CB CLOSED → normal operation resumes automatically.

**WHAT CHANGES AT SCALE:**
At 10 services: implement patterns manually per service. At 50 services: service mesh (Istio, Linkerd) enforces resilience patterns in the infrastructure sidecar — application code is pattern-free. At 200 services: platform team owns mesh configuration; product teams own business logic.

---

### 💻 Code Example

**Circuit Breaker with Resilience4j (Java):**

```java
// BAD: No resilience pattern - direct HTTP call
// One slow downstream service blocks all threads
@Service
public class OrderService {

    @Autowired
    private RestTemplate restTemplate;

    public Inventory checkInventory(String sku) {
        // No timeout, no circuit breaker, no retry
        // Service B 5s GC pause = 5s block here
        return restTemplate.getForObject(
            "http://inventory-service/items/" + sku,
            Inventory.class
        );
    }
}
```

```java
// GOOD: Resilience4j Circuit Breaker + Retry
@Service
public class OrderService {

    // CB: open after 50% failures in 10-call window
    @CircuitBreaker(
        name = "inventoryService",
        fallbackMethod = "inventoryFallback")
    // Retry: 3 attempts, exponential backoff
    @Retry(name = "inventoryService")
    // Timeout: fail if no response within 2 seconds
    @TimeLimiter(name = "inventoryService")
    public CompletableFuture<Inventory> checkInventory(
            String sku) {
        return CompletableFuture.supplyAsync(() ->
            restTemplate.getForObject(
                "http://inventory-service/items/" + sku,
                Inventory.class));
    }

    // Fallback: return cached or degraded response
    public CompletableFuture<Inventory> inventoryFallback(
            String sku, Exception ex) {
        log.warn("Inventory CB open for {}: {}",
            sku, ex.getMessage());
        return CompletableFuture.completedFuture(
            Inventory.ofUnknownStock(sku));
    }
}
```

```yaml
# application.yml - Resilience4j config
resilience4j:
  circuitbreaker:
    instances:
      inventoryService:
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 30s
  retry:
    instances:
      inventoryService:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
```

**How to test / verify correctness:**
Unit test: mock RestTemplate to throw exception. Verify `inventoryFallback` is called. Integration test with WireMock: simulate 5 consecutive 500 errors, verify CB opens and subsequent calls return fallback immediately (< 10ms, not 2s). Chaos test: use Toxiproxy to inject 5s latency and verify timeout enforcement.

---

### ⚖️ Comparison Table

| Pattern | Force Addressed | When to Apply | Key Trade-off |
|---|---|---|---|
| Circuit Breaker | Cascading failure from slow dependencies | Always for external calls | State machine overhead |
| Retry + Backoff | Transient network errors | Idempotent operations only | Amplifies non-transient errors |
| Timeout | Indefinite blocking | Every remote call | Must match upstream SLA |
| Bulkhead | Thread pool exhaustion | High-volume, mixed criticality | Resource partitioning overhead |
| Outbox | Dual-write consistency | Event publishing with DB writes | Polling overhead |
| Saga | Long-running distributed transactions | Multi-service state change | Compensating transaction complexity |
| CQRS | Read/write load asymmetry | Read >3x write, complex queries | Two models to maintain |
| Sidecar | Cross-cutting concern injection | Polyglot service mesh | Proxy latency |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Retry handles all transient failures" | Retry without idempotency causes duplicate operations. Retry without backoff amplifies load on degraded services. Retry is safe only for idempotent operations with bounded retry counts and jitter. |
| "Circuit Breaker prevents failures" | CB prevents cascading failures — it does not prevent the underlying failure. A CB open state means the dependency is unhealthy; the CB is containing the blast radius. |
| "Service mesh replaces all resilience patterns" | Service mesh handles L7 network resilience (retry, CB, timeout). Application-level patterns (Outbox, Saga, idempotency) remain application responsibility. |
| "Eventual consistency means data is sometimes wrong" | Eventual consistency means data is temporarily inconsistent but will converge to a consistent state. Designing for eventual consistency means building systems that tolerate and resolve temporary inconsistency, not accept permanent incorrectness. |
| "More patterns = more resilient" | Each resilience pattern adds latency and complexity. Applying all patterns to every call is as wrong as applying none. Risk-profile each dependency and apply proportionate patterns. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cascading failure — no circuit breaker**

**Symptom:** One slow downstream service causes system-wide timeout. All services become unresponsive within 60-120 seconds.

**Root Cause:** No isolation between dependency failure and caller thread pool. Thread pool exhaustion propagates upstream.

**Diagnostic:**
```bash
# Check thread pool utilisation during incident
# (via JMX, Micrometer, or APM)
curl http://service:8080/actuator/metrics/\
  executor.pool.size | jq '.measurements'

# Look for: active=pool-size (pool saturated)
# In Grafana: jvm_threads_states_threads{state="blocked"}
```

**Fix:**
- BAD: Increase thread pool size.
- GOOD: Add Circuit Breaker + Bulkhead on all external dependencies. CLOSED pool should never exceed 50% under normal load.

**Prevention:** Platform-level policy: no external HTTP call without Circuit Breaker. Enforced via ArchUnit or service mesh policy.

---

**Failure Mode 2: Duplicate message processing — no idempotent consumer**

**Symptom:** Orders placed twice during retry storm. Payments charged twice. Inventory decremented twice.

**Root Cause:** Message consumer is not idempotent. Retry logic (correct for transient failures) causes duplicate processing on non-idempotent operations.

**Diagnostic:**
```sql
-- Find duplicate order IDs
SELECT order_id, COUNT(*) as count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Find duplicate payment charges
SELECT idempotency_key, COUNT(*)
FROM payment_charges
GROUP BY idempotency_key
HAVING COUNT(*) > 1;
```

**Fix:**
- BAD: Reduce retry count to 0.
- GOOD: Add idempotency key to all mutating message handlers. Before processing: check if `idempotency_key` already exists in `processed_messages` table. If exists: return cached result. If not: process and record.

**Prevention:** Team rule: any message handler that mutates state must implement idempotent consumer pattern. Verified in code review.

---

**Failure Mode 3: Saga compensation failure — partial rollback**

**Symptom:** Multi-step distributed transaction partially completes. Step 3 fails but steps 1 and 2 remain committed. System is in inconsistent state with no automatic recovery.

**Root Cause:** Saga implemented without compensating transactions, OR compensating transactions are not idempotent and fail on retry.

**Diagnostic:**
```bash
# Find sagas in non-terminal state older than SLA
SELECT saga_id, current_step, started_at
FROM saga_state
WHERE status NOT IN ('COMPLETED', 'COMPENSATED')
  AND started_at < NOW() - INTERVAL '10 minutes';
# Non-zero result = stuck sagas = inconsistent state
```

**Fix:**
- BAD: Manually intervene to correct each stuck saga.
- GOOD: Implement compensating transactions for every saga step. Compensating transactions must be idempotent. Saga coordinator retries compensation on failure with backoff.

**Prevention:** Saga design review: every step must have a named, idempotent compensating transaction before implementation is approved.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[DPT-064 - Pattern-Driven Architecture Design]] - patterns at architectural level
- [[DPT-053 - Outbox Pattern]] - messaging reliability pattern
- [[DPT-054 - Saga Pattern]] - distributed transaction pattern

**Builds On This (learn these next):**
- [[DPT-071 - Pattern Trade-off Framing]] - evaluating patterns against system constraints
- [[DPT-069 - Meta-Pattern Design]] - patterns about patterns at distributed level

**Alternatives / Comparisons:**
- [[DST-001 - Distributed Systems]] - the underlying theory
- [[MSV-001 - Microservices]] - the architectural context
- [[SAP-018 - CQRS Pattern]] - data management pattern for distributed reads/writes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS    │ Pattern vocabulary for forces    │
│               │ unique to distributed systems:   │
│               │ partial failure, network         │
│               │ unreliability, consistency       │
├───────────────┼──────────────────────────────────┤
│ PROBLEM       │ GoF patterns assume single-      │
│               │ process; distributed systems     │
│               │ add failure modes GoF ignores    │
├───────────────┼──────────────────────────────────┤
│ KEY INSIGHT   │ Partial failure is the rule;     │
│               │ every pattern must account for   │
│               │ "request sent, response lost"    │
├───────────────┼──────────────────────────────────┤
│ USE WHEN      │ Building any multi-process       │
│               │ networked system                 │
├───────────────┼──────────────────────────────────┤
│ AVOID WHEN    │ Single-process in-memory systems │
│               │ where GoF patterns suffice       │
├───────────────┼──────────────────────────────────┤
│ TRADE-OFF     │ Resilience complexity vs.        │
│               │ cascading failure risk           │
├───────────────┼──────────────────────────────────┤
│ ONE-LINER     │ Fail fast, isolate, compensate,  │
│               │ and observe                      │
├───────────────┼──────────────────────────────────┤
│ NEXT EXPLORE  │ DPT-057 Circuit Breaker          │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Apply timeout + retry + circuit breaker to every external call — these three cover >80% of distributed failure modes.
2. Retry is safe only on idempotent operations — add idempotency keys to all mutating calls.
3. Service mesh handles network-level patterns; application code handles data-level patterns (Outbox, Saga, idempotency).

**Interview one-liner:** "Distributed systems patterns address forces GoF cannot: partial failure, network unreliability, and consistency trade-offs — the essential vocabulary is Circuit Breaker, Retry+Idempotency, Saga, Outbox, and CQRS, each addressing a distinct distributed failure mode."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** In any system where components operate independently with unreliable communication channels, the cost of not anticipating failure is orders of magnitude higher than the cost of designing for it upfront. Resilience is not a feature to add later — it is a structural property that must be designed in from the first inter-component communication.

**Where else this pattern appears:**
- **Human organisations** - reliable communication in large organisations requires the same patterns: Circuit Breaker (escalation paths when a team is unresponsive), Bulkhead (separate projects don't share personnel), Retry (follow-up if no response within SLA), Saga (multi-department approvals with rollback capability).
- **Supply chain logistics** - Circuit Breaker = supplier qualify criteria (stop ordering from a failing supplier), Bulkhead = no single supplier for critical components, Retry = alternative routing when primary channel fails.
- **Financial clearing systems** - every inter-bank message includes idempotency keys and acknowledgment protocols — the 1970s SWIFT protocol exhibits all distributed systems pattern properties 50 years before the term was coined.

---

### 💡 The Surprising Truth

Netflix's Hystrix Circuit Breaker library, which popularised Circuit Breaker at scale and influenced virtually every subsequent resilience library, was deprecated by Netflix in 2018 — not because it was wrong, but because Netflix moved to a service mesh (Envoy) that implements the same patterns in the network infrastructure layer. The lesson: Hystrix was not the pattern, it was one implementation. The underlying Circuit Breaker pattern is now in every major service mesh. Engineers who understand the pattern use whatever implementation their platform provides; engineers who learned only the Hystrix API are confused about what "Circuit Breaker" even means when it is a mesh configuration, not a code annotation.

---

### 🧠 Think About This Before We Continue

**Question 1 (Design Trade-off):** Retry with exponential backoff is a standard resilience pattern. But in a high-traffic system, simultaneous retries from many clients can create "thundering herd" — all retrying at the same time and overwhelming a recovering service. What modification to the retry pattern prevents this — and what does that modification reveal about the interaction between individual service resilience and system-level stability?

*Hint:* Think about what "jitter" adds to exponential backoff — and why Twitter and AWS specifically wrote about this in their distributed systems engineering blogs.

**Question 2 (Scale):** A system with 200 microservices must enforce Circuit Breaker, Retry, and Timeout on all inter-service calls. Option A: each team implements these patterns in their service code. Option B: a service mesh (Istio) enforces these as infrastructure policy with central configuration. What are the failure modes of Option A that Option B prevents — and what failure modes does Option B introduce that Option A avoids?

*Hint:* Think about consistency of implementation across teams, visibility into pattern configuration, and what happens when mesh configuration is incorrect vs. when application code is incorrect.

**Question 3 (First Principles):** The Saga pattern solves distributed transactions by replacing ACID atomicity with eventual consistency and compensating transactions. This means that for a brief window, the system is in an inconsistent intermediate state. Under what business domain requirements is this acceptable — and under what requirements does it create regulatory or business logic problems that cannot be tolerated?

*Hint:* Think about financial transactions (double-spend prevention), medical record updates, and inventory reservation systems. Which of these can tolerate a 100ms window of inconsistency, and which cannot?
