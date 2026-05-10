---
id: DST-052
title: "Correlation ID"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-051
related: DST-051, DST-045
tags:
  - distributed
  - observability
  - pattern
  - foundational
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /distributed-systems/correlation-id/
---

# DST-052 - Correlation ID

⚡ TL;DR - A correlation ID is a unique identifier attached to a request at its entry point and propagated through every system it touches, enabling all logs, events, and records from one user operation to be linked together across service boundaries.

| Metadata        |                  |     |
| :-------------- | :--------------- | :-- |
| **Depends on:** | DST-051          |     |
| **Related:**    | DST-051, DST-045 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
User reports: "My payment failed at 2:47 PM." Support engineer searches logs: `grep "payment failed" payment.log` → 247 results, 12 concurrent payment failures at 2:47 PM. Which one was this user? `grep "userId=12345" payment.log` → 83 results (user made multiple payment attempts over days). `grep "userId=12345" payment.log | grep "2:47"` → 3 results, all at 2:47 PM. Which attempt? Cross-referencing with order service logs, notification logs, audit logs — same problem. 45 minutes to reconstruct one user's 3-second interaction.

**THE BREAKING POINT:**
In any system with multiple services, log messages from different requests intermix. Every service writes logs independently. The only natural link between log entries is: shared identifiers (userId, orderId) OR timestamp proximity. Identifiers are not unique to one request (same user makes multiple requests). Timestamps are unreliable under concurrent load. Without a request-unique identifier: log correlation is manual, slow, and error-prone.

**THE INVENTION MOMENT:**
Enterprise integration patterns (Hohpe & Woolf, 2004) described the Correlation Identifier pattern: when a request enters a system, assign it a unique ID. Pass this ID with every message, log entry, and service call that is part of the same request. Any developer who has that ID can instantly find everything related to that request across all systems. This is the simplest possible observability primitive — predates distributed tracing by years.

**EVOLUTION:**
2004: Hohpe & Woolf — Correlation Identifier enterprise integration pattern. 2010+: HTTP header standardization (`X-Correlation-ID`, `X-Request-ID`). 2015+: Microservices adopt corr ID as minimum viable observability. 2018: Logging frameworks (Logback MDC, Log4j2 ThreadContext) — automatic corr ID inclusion in every log line. 2019: W3C `traceparent` header — corr ID extended with span timing (distributed tracing context). Today: Correlation ID is the minimum; distributed tracing (DST-051) is the complete solution. Systems often start with corr ID and graduate to full tracing.

---

### 📘 Textbook Definition

**Correlation ID** (also: Request ID, Transaction ID, Trace ID) is a globally unique identifier generated for each request at the system's entry point (API gateway, load balancer, or first service). It is: (1) propagated through every service call (HTTP header, message queue header, event payload), (2) included in every log line related to the request (via logging framework's MDC/ThreadContext), (3) returned to the client in the HTTP response (as `X-Correlation-ID` header), so the client can provide it in support tickets. **Relationship to distributed tracing:** distributed tracing's `traceId` is a correlation ID plus timing (span) data per service. A correlation ID system with MDC is a lighter-weight precursor to full distributed tracing — same propagation, no timing instrumentation.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Give every request a unique ID — attach it to every log line, every service call, every event.

> A correlation ID is like a case number in customer support. When you call with a problem, the agent creates a case number. Every note, action, and communication about your problem gets that case number. Any agent who receives your follow-up call can pull the complete history instantly — by case number. Without case numbers: every agent must ask "what happened? when? what did the previous agent do?" — reconstructing context from scratch.

**One insight:** A correlation ID is free to implement (generate a UUID, set MDC, propagate a header). The value — instant cross-service log correlation — is disproportionate to the cost. It is the minimum viable observability investment.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Generated once, at the outermost entry point.** The first system that receives the request (API gateway, load balancer) generates the correlation ID. If the client provides one: honor it (useful for idempotency and tracking retries). Otherwise: generate a new UUID.
2. **Propagated through EVERY call.** Every HTTP call, every message queue publish, every async thread must carry the correlation ID forward. A single missed propagation breaks the chain.
3. **Included in EVERY log line.** Via MDC/ThreadContext: every log statement in the service automatically includes the correlation ID. No per-log code change. Structural: `{"msg": "...", "correlationId": "abc-123"}`.
4. **Returned to the caller.** HTTP response header: `X-Correlation-ID: abc-123`. Client logs this. When reporting an issue: provide the correlation ID. Support immediately has the full picture.

**DERIVED DESIGN:**

```
Gateway:
  correlationId = req.header("X-Correlation-ID")
    ?? UUID.randomUUID().toString()
  MDC.put("correlationId", correlationId)
  [all log lines now include correlationId automatically]
  forward to Service A with X-Correlation-ID: {correlationId}
  response: set X-Correlation-ID: {correlationId}

Service A:
  correlationId = req.header("X-Correlation-ID")
  MDC.put("correlationId", correlationId)
  outgoing calls: add X-Correlation-ID: {correlationId} header
```

**THE TRADE-OFFS:**
**Gain:** Instant cross-service log correlation. Free (UUID + MDC + header propagation). Works with existing logging infrastructure (no trace backend needed).
**Cost:** No timing data per service (correlation only, not performance profiling). No call tree structure (only "same request" not "A called B called C"). Must be implemented in every service or correlation breaks.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Propagating context through async thread boundaries requires explicit code — there is no automatic mechanism for arbitrary thread handoffs.
**Accidental:** Spring's `OncePerRequestFilter` vs Jakarta Servlet filter. `X-Correlation-ID` vs `X-Request-ID` vs `traceparent` header name — implementation details, same concept.

---

### 🧪 Thought Experiment

**SETUP:** User report: "My order failed at 3:15 PM, order ID 67890." Support engineer has correlation ID: `req-abc-123-xyz`.

**WITHOUT CORRELATION ID:**

```
grep "order 67890" order-service.log   → 3 results
grep "order 67890" payment-service.log → 1 result
grep "order 67890" audit.log           → 5 results
# Which of these belong to the same REQUEST?
# 3:15 PM ± 30 seconds? Too broad under load.
# Manual cross-referencing: 30 minutes.
```

**WITH CORRELATION ID:**

```bash
grep "req-abc-123-xyz" order-service.log
grep "req-abc-123-xyz" payment-service.log
grep "req-abc-123-xyz" audit.log
# Or in ELK: filter by correlationId="req-abc-123-xyz"
# All log entries across all services for this one request.
# Complete picture: 30 seconds.
```

**THE INSIGHT:** Correlation ID converts a manual log archaeology problem into a single grep. The investment: generate UUID at gateway, propagate in header, add to MDC. Time to implement: 2 hours. Time saved per incident: 30-45 minutes. Every incident.

---

### 🧠 Mental Model / Analogy

> Correlation ID is like a hospital wristband. When a patient is admitted: they receive a unique wristband with their patient ID. Every nurse, doctor, pharmacist, and lab technician who interacts with the patient records their patient ID alongside their notes. The patient's chart (correlation ID search) shows everything: vitals every hour, medications administered, lab results, physician notes — all linked by the same patient ID. Without wristbands: cross-referencing events requires knowing the patient's name + date of birth + room number — error-prone and slow.

**Mapping:**

- **Patient wristband (patient ID)** → correlation ID
- **Different hospital departments** → different microservices
- **Nurses, doctors, pharmacists recording notes** → log lines in each service
- **Patient's complete chart** → search results for correlationId in ELK
- **Wristband worn by patient throughout stay** → corr ID propagated through entire request

Where this analogy breaks down: a hospital patient moves physically from department to department (sequential). HTTP requests can fan out to many services simultaneously (parallel). The correlation ID works for both cases — parallel calls all carry the same ID and their logs are all retrievable via the same search.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When your request enters the system, it gets a unique "ticket number." Every service that handles your request writes that ticket number on every note it makes. When something goes wrong: look up the ticket number — all the notes from all services instantly appear. No ticket number: you'd have to search through all notes from all services and guess which ones belong to your request.

**Level 2 - How to use it (junior developer):**
Spring Boot: `OncePerRequestFilter` that sets MDC + propagates header. Logback: `%X{correlationId}` in pattern. That's it.

```java
// Filter: runs on every incoming request
@Component
public class CorrelationIdFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req,
        HttpServletResponse res, FilterChain chain)
        throws ServletException, IOException {
        String corrId = Optional.ofNullable(
            req.getHeader("X-Correlation-ID"))
            .orElse(UUID.randomUUID().toString());
        MDC.put("correlationId", corrId);
        res.setHeader("X-Correlation-ID", corrId);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.remove("correlationId");
        }
    }
}
```

**Level 3 - How it works (mid-level engineer):**
MDC (Mapped Diagnostic Context) in Logback/Log4j2 is a `ThreadLocal<Map<String,String>>`. When `MDC.put("correlationId", id)` is called: all subsequent log statements on that thread include `correlationId` in the log record. This is why `MDC.remove("correlationId")` in `finally` is critical — without removal, the ID stays in the ThreadLocal for the next request on the same thread (thread pool reuse), causing log pollution. For async operations: MDC must be copied explicitly to the new thread. Spring's `@Async`: use `DelegatingSecurityContextAsyncTaskExecutor` or custom `MDCCopyTaskDecorator`.

**Level 4 - Why it was designed this way (senior/staff):**
The W3C `traceparent` header (`00-<traceId>-<spanId>-<flags>`) is a superset of the correlation ID. The `traceId` component IS the correlation ID — 128-bit UUID. The `spanId` adds per-service identity. The `flags` add sampling decision. Choosing between `X-Correlation-ID` (simple UUID) and `traceparent` (full OTel context): if you plan to add distributed tracing later, use `traceparent` from the start — your correlation ID infrastructure becomes the propagation mechanism for tracing. No migration needed. The cost: parsing `traceparent` format instead of passing raw UUID. Always worth it.

**Expert Thinking Cues:**

- "Correlation ID disappears in async Kafka consumers" → MDC is thread-local. Kafka consumer runs on a separate thread (consumer thread pool). MDC from the producer thread is not available. Fix: store correlationId in Kafka message header. Consumer extracts it and sets MDC. Or: pass as part of message payload (less clean).
- "Different services generate their own IDs instead of propagating the incoming one" → Service B received the correlation ID from A but created a new UUID for its own outgoing calls. Now: A's logs link to B, but B's calls to C have a different ID. Trace breaks at B. Fix: propagation rule must be enforced: ALWAYS use the incoming `X-Correlation-ID`. Only generate a new one if there is none (gateway-level). Code review: reject any `UUID.randomUUID()` in request filters that doesn't first check for existing header.
- "Client-side correlation ID (client generates and sends in request)" → Allowing clients to set the correlation ID is useful for retries (same ID → idempotency + correlation). Security concern: clients could inject IDs that look like internal IDs or spoof other users' IDs. Mitigation: validate the format (UUID4 only, no special characters). Never trust the client-provided ID for security decisions — only for logging correlation.

---

### ⚙️ How It Works (Mechanism)

**Correlation ID propagation:**

```
Client  API Gateway  Service A  Service B  Kafka  Service C
  │         │            │          │         │        │
  │─POST────▶ [no X-Corr-ID]        │         │        │
  │          │ generate UUID         │         │        │
  │          │ correlationId=abc     │         │        │
  │          │ MDC.put(corr=abc)     │         │        │
  │          │─forward──────────────▶│         │        │
  │          │  X-Correlation-ID:abc │         │        │
  │          │            │ MDC.put(corr=abc)   │        │
  │          │            │─call────▶│         │        │
  │          │            │ X-Correlation-ID:abc│        │
  │          │            │         │ MDC.put  │        │
  │          │            │─publish──────────────▶       │
  │          │            │  header: corr=abc    │        │
  │          │            │                      │ consumer extracts
  │          │            │                      │ MDC.put(corr=abc)
  │◀─200─────│            │          │         │ [logs: corr=abc]
  │ X-Corr-ID: abc        │          │         │        │
```

**MDC lifecycle (critical):**

```java
// Thread-safe MDC lifecycle:
MDC.put("correlationId", id); // set at request start
try {
  chain.doFilter(req, res);   // all logs include id
} finally {
  MDC.remove("correlationId"); // MUST clear for thread pool
  // Without this: next request on same thread has old ID
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SUPPORT DEBUGGING WITH CORRELATION ID:**

```
User  API GW  OrderSvc  PaymentSvc  ELK Stack
  │     │        │          │           │
  │─buy─▶        │          │           │
  │      │ genID: abc       │           │
  │      │─order─▶│          │           │
  │      │        │ log: INFO {"msg":"...","corrId":"abc"}
  │      │        │─charge──▶│           │
  │      │        │          │ log: ERROR {"corrId":"abc"}
  │◀─500─│        │          │           │ ← YOU ARE HERE
  │ X-Corr: abc   │          │           │ [user reports abc]
                             │           │
  [Support: search corrId=abc in ELK]    │
  [ELK returns all logs from all services]
```

**WHAT CHANGES AT SCALE:**
At scale: correlation IDs enable ELK (Elasticsearch-Logstash-Kibana) to become a powerful debugging tool. Filter: `correlationId: "abc-123"` → instant cross-service timeline. At 10,000 req/s: 10,000 unique correlation IDs per second → each uniquely searchable. Elasticsearch full-text index on `correlationId` field makes this O(log n) per search.

---

### 💻 Code Example

**BAD - No correlation ID, sequential grep debugging:**

```java
// BAD: logs have timestamp + userId, no request ID
// Debugging: search by timestamp + userId
// Under load: many requests overlap → ambiguous
log.info("Processing order for user: {}", userId);
log.error("Payment failed for user: {}", userId);
// Which payment failure belongs to which order attempt?
// Must correlate by timestamp ± tolerance = unreliable
```

**GOOD - Correlation ID with Spring Boot filter + MDC:**

```java
// GOOD: every log line automatically includes correlationId

// Step 1: Filter sets MDC once per request
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class CorrelationIdFilter extends OncePerRequestFilter {
    private static final String HEADER = "X-Correlation-ID";

    @Override
    protected void doFilterInternal(HttpServletRequest req,
        HttpServletResponse res, FilterChain chain)
        throws ServletException, IOException {
        String corrId = Optional
            .ofNullable(req.getHeader(HEADER))
            .filter(s -> !s.isBlank())
            .orElse(UUID.randomUUID().toString());
        MDC.put("correlationId", corrId);
        res.setHeader(HEADER, corrId);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.remove("correlationId"); // CRITICAL
        }
    }
}

// Step 2: Logback pattern includes correlationId
// logback-spring.xml:
// <pattern>%d{ISO8601} [%X{correlationId}] %-5level %msg%n</pattern>

// Step 3: RestTemplate propagation (client side)
@Bean
public RestTemplate restTemplate() {
    RestTemplate rt = new RestTemplate();
    rt.getInterceptors().add((req, body, exec) -> {
        String corrId = MDC.get("correlationId");
        if (corrId != null) {
            req.getHeaders().add("X-Correlation-ID", corrId);
        }
        return exec.execute(req, body);
    });
    return rt;
}

// Step 4: Async propagation
@Bean("asyncExecutor")
public Executor asyncExecutor() {
    ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
    ex.setTaskDecorator(runnable -> {
        Map<String, String> ctx = MDC.getCopyOfContextMap();
        return () -> {
            if (ctx != null) MDC.setContextMap(ctx);
            try { runnable.run(); }
            finally { MDC.clear(); }
        };
    });
    ex.initialize();
    return ex;
}
```

---

### ⚖️ Comparison Table

|                       | Correlation ID             | Distributed Tracing (DST-051)                 |
| :-------------------- | :------------------------- | :-------------------------------------------- |
| What it provides      | "All logs for request X"   | "All logs + timing per service for request X" |
| Infrastructure needed | Logging only (ELK)         | OTel Collector + Jaeger/Zipkin                |
| Implementation cost   | Hours                      | Days                                          |
| Per-service timing    | No                         | Yes (per span)                                |
| Call tree visibility  | No                         | Yes (parent-child)                            |
| Sampling              | N/A (all requests)         | Yes (required at scale)                       |
| Debugging workflow    | Search by ID → filter logs | Query trace → click span → view timeline      |

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                                                                                                                                                                                                                                 |
| :----------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Correlation ID is enough — distributed tracing is overkill"       | Correlation ID answers "what happened for request X?" Distributed tracing additionally answers "which service was slow?" and "what was the call tree?" For systems with 3+ services where performance matters (SLO tracking), distributed tracing is necessary. Correlation ID is the minimum; tracing is the complete solution.        |
| "MDC automatically propagates to async threads"                    | MDC is thread-local. A new thread (Executor, CompletableFuture, `@Async`) starts with an EMPTY MDC. Must explicitly copy MDC to new thread using a TaskDecorator. Without this: all log lines in async tasks show no correlationId — the async portion of the request is invisible.                                                     |
| "Just add correlationId to the log message text — no need for MDC" | Adding correlationId as a log message parameter (`log.info("CorrId={} ...", corrId)`) requires passing `corrId` to every method that logs. MDC is cleaner: set ONCE at request boundary, included in EVERY log line automatically. If any method forgets to pass corrId: the log line loses correlation. MDC is structural, not manual. |
| "Different correlation ID per service call is fine"                | Each service call should reuse the SAME correlation ID from the incoming request. Creating a new UUID for outgoing calls breaks the chain: A→B works (same ID). But B→C has a new ID: C's logs are unrelated to A's. The correlation ID must be THE SAME UUID for the entire request tree.                                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: MDC Not Cleared Between Requests**

**Symptom:** Logs show the wrong correlation ID for some requests. Request A's ID appears in Request B's logs. Support debugging with correlation ID returns results from different users' requests — privacy incident.
**Root Cause:** `MDC.remove("correlationId")` is not called in the `finally` block of the request filter. Thread is returned to the pool with Request A's correlation ID in MDC. Request B runs on the same thread — its logs show A's ID. Logs are cross-contaminated.
**Diagnostic:**

```bash
# Check if same correlationId appears in logs
# for different userIds:
grep "correlationId=abc-123" app.log | \
  grep -oP 'userId=\K[^ ]+' | sort | uniq
# If multiple userIds: MDC not cleared between requests

# Check filter code for MDC cleanup:
grep -A 20 "MDC.put\|MDC.remove" \
  src/main/java/filter/CorrelationIdFilter.java
# If MDC.remove is not in finally block: bug
```

**Fix:**
BAD: `MDC.put("correlationId", id)` without `MDC.remove()` in `finally`.
GOOD: Always clear MDC in the `finally` block of the filter: `MDC.remove("correlationId")` or `MDC.clear()`. This ensures the thread-local map is clean before returning to the pool.
**Prevention:** Unit test: run two requests sequentially on the same thread. Verify: second request's logs do not contain first request's correlationId. Code review rule: `MDC.put` must always have a corresponding `MDC.remove` or `MDC.clear` in a `finally` block.

**Failure Mode 2: Correlation ID Lost at Message Queue Boundary**

**Symptom:** Support engineer searches logs by correlationId. Finds logs in Services A, B, C. Service D (which processes async Kafka messages) shows no logs for this correlationId. Service D's activity is unlinked. Cannot determine if/when D processed the event from A's request.
**Root Cause:** Service A publishes a Kafka message but does not include the correlation ID in the message headers. Service D consumes the message and generates its own UUID as correlationId. Log chains break at the Kafka boundary.
**Diagnostic:**

```bash
# Check if Kafka messages include correlationId header:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic order-events --from-beginning --max-messages 5 \
  --property print.headers=true | grep -i corr
# If no correlationId header: producer not propagating

# Check producer code for header injection:
grep -r "ProducerRecord\|KafkaTemplate" \
  order-service/src/ | grep -A 5 "correlationId\|X-Corr"
# If not present: missing propagation
```

**Fix:**
BAD: `kafkaTemplate.send(topic, key, value)` — no headers.
GOOD:

```java
String corrId = MDC.get("correlationId");
ProducerRecord<String, Object> rec =
    new ProducerRecord<>(topic, key, value);
if (corrId != null) {
    rec.headers().add("X-Correlation-ID",
        corrId.getBytes(StandardCharsets.UTF_8));
}
kafkaTemplate.send(rec);
// Consumer: extract from headers, set MDC
```

**Prevention:** Kafka integration test: verify that published messages contain `X-Correlation-ID` header. Consume the message and verify MDC is set correctly in the consumer.

**Failure Mode 3: Security - Correlation ID Injection**

**Symptom:** Security audit reveals: a client submits a request with `X-Correlation-ID: admin-request-001`. The system uses this client-provided ID in logs and audit records. An attacker could submit IDs that look like internal system IDs, confuse log correlation, or inject IDs that match other users' existing correlation IDs (spoofing).
**Root Cause:** Client-provided correlation IDs are accepted without validation. Any string in the header becomes the correlation ID — including SQL injection attempts, newline injection (log forging), or spoofed internal IDs.
**Diagnostic:**

```bash
# Test: send a request with a malicious correlation ID:
curl -H "X-Correlation-ID: $'\n'FORGED LOG LINE" \
  https://api.example.com/orders
# Check logs: does a fake log line appear?
# If yes: newline injection in correlation ID

# Test: send with very long ID:
curl -H "X-Correlation-ID: $(python3 -c 'print("A"*10000)')" \
  https://api.example.com/orders
# Check: does system handle gracefully?
```

**Fix:**
BAD: `String corrId = req.getHeader("X-Correlation-ID")` — no validation.
GOOD: Validate format and length: `UUID regex only, max 36 chars`. If invalid: generate a new UUID (don't use client-provided ID):

```java
String raw = req.getHeader("X-Correlation-ID");
String corrId = (raw != null && raw.matches(
    "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-"
    + "[89ab][0-9a-f]{3}-[0-9a-f]{12}$"))
    ? raw
    : UUID.randomUUID().toString();
```

**Prevention:** Always validate client-provided identifiers. Use UUID4 format validation. Reject (generate new) if invalid — don't log the invalid value. Limit header field lengths at the API gateway level.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-051 - Distributed Tracing (correlation ID is the simpler precursor — understand tracing to see how corr ID fits)

**Builds On This (learn these next):**

- DST-051 - Distributed Tracing (full tracing extends correlation ID with per-span timing)

**Alternatives / Comparisons:**

- DST-045 - Idempotency (idempotency key is a specialized correlation ID for safe retries)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | UUID per request, propagated   |
|                  | to every service, included     |
|                  | in every log line              |
+------------------+--------------------------------+
| PROBLEM SOLVED   | "Which log entries across 10   |
|                  | services belong to THIS one    |
|                  | user's request?"               |
+------------------+--------------------------------+
| KEY INSIGHT      | Free to implement; enormous    |
|                  | debugging value; use W3C       |
|                  | traceparent for future-proofing|
+------------------+--------------------------------+
| USE WHEN         | Any multi-service system;      |
|                  | minimum viable observability   |
+------------------+--------------------------------+
| AVOID WHEN       | Single service / monolith      |
|                  | (APM/profiler is more useful)  |
+------------------+--------------------------------+
| TRADE-OFF        | Minimal — cost is near zero;   |
|                  | value is incident debugging    |
+------------------+--------------------------------+
| ONE-LINER        | UUID at entry + MDC + header   |
|                  | propagation = cross-service log|
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-051 Distributed Tracing    |
|                  | (adds timing per service)      |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Generate at the OUTERMOST entry point (gateway/load balancer). Propagate inward. Never regenerate inside a service. Same UUID must appear in all logs across all services for one request.
2. MDC must be cleared in `finally` — not in try block. Thread pools reuse threads: if MDC is not cleared, the next request on the same thread inherits the previous request's correlation ID.
3. Validate client-provided correlation IDs to UUID4 format. Reject invalid values (generate a new UUID). Log injection and ID spoofing are real attack vectors when header values are blindly used.

**Interview one-liner:**
"A correlation ID is a UUID generated at the entry point for each incoming request and propagated through every service call (as HTTP header `X-Correlation-ID`) and included in every log line (via MDC/ThreadContext). This enables instant cross-service log aggregation: search by correlationId in ELK → all log lines from all services for that one request. Implementation: `OncePerRequestFilter` that reads or generates UUID, sets `MDC.put('correlationId', id)`, adds header to response and all outgoing calls, clears MDC in `finally`. The W3C `traceparent` header is a superset — using it future-proofs for distributed tracing."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Tag operations with a unique identifier at creation and carry that tag through the entire lifecycle. This principle — "identity propagation" — applies universally: bank transaction IDs (carried from initiation through settlement through reconciliation), Git commit SHAs (carried from commit through CI/CD through deployment), database transaction IDs (carried through WAL through replication), and UX session IDs (carried through analytics events through funnel analysis). Whenever an operation must be reconstructed from distributed records: assign it a unique identity at creation and propagate that identity everywhere.

**Where else this pattern appears:**

- **Idempotency key (DST-045):** An idempotency key IS a specialized correlation ID — it identifies one logical operation for deduplication purposes. The idempotency key is generated by the CLIENT (not the server) and sent with the request. The server correlates all attempts for the same logical operation. The difference: correlation ID is for observability (debugging). Idempotency key is for correctness (deduplication). Same propagation mechanism, different purpose.
- **Database write-ahead log (WAL) sequence numbers:** PostgreSQL's WAL assigns a Log Sequence Number (LSN) to every change. LSN is the correlation ID of the database — it links the change in the WAL to the corresponding page update, the replication stream to the replica, and the backup restore point. Postgres monitoring uses LSN to answer: "which changes have been replicated? Which changes are in this backup? Which transaction caused this page write?" The LSN is the correlation ID for the entire replication and recovery system.
- **Browser request IDs in Chrome DevTools:** Each HTTP request in Chrome DevTools has a request ID visible in the Network tab. This ID appears in Chrome's internal logs and can be used to correlate requests across browser processes (network stack, renderer, service worker). DevTools' "timeline" view uses these IDs to link a JavaScript fetch() call to its corresponding network request to its response. The correlation ID makes browser internals observable.

---

### 💡 The Surprising Truth

The simplest observability improvement in any distributed system is adding a correlation ID — but most engineering teams don't add it until AFTER their first major production incident that required 3 hours of log archaeology. The surprising truth: a correlation ID can be implemented in an afternoon (UUID + MDC + one filter), yet teams routinely operate distributed systems without it for months or years. The reason is not technical difficulty — it's that the value is invisible until you need it. When you need it (a production incident at 3 AM): the absence of a correlation ID multiplies debugging time by 10-30×. The lesson: implement correlation IDs before your first incident, not after. It is the highest-ROI observability investment in the first days of a new service. No other tool gives so much value for so little effort.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** A Java service receives an HTTP request, processes it synchronously, and then schedules an async task using `CompletableFuture.supplyAsync()` to send a notification. The `CompletableFuture` uses the default ForkJoinPool. The async task runs long after the HTTP response is returned. What happens to the MDC `correlationId` in the async task? How do you fix it?
_Hint:_ `CompletableFuture.supplyAsync()` with default ForkJoinPool runs on a different thread. MDC is thread-local. The ForkJoinPool thread has EMPTY MDC — no `correlationId`. The notification log lines have no correlationId — they are invisible in correlation ID searches. Fix: capture MDC at submission time (on the HTTP thread where MDC is set), pass to the async task: `Map<String,String> ctx = MDC.getCopyOfContextMap()`. Inside the lambda: `MDC.setContextMap(ctx)` at start, `MDC.clear()` in finally. Spring provides `TaskDecorator` to do this automatically for `@Async` executors — configure it on the `ThreadPoolTaskExecutor` bean.

**Q2 (D - Root Cause):** Support reports that correlation ID searches in ELK return incomplete results — some log lines from Service B appear under the correct correlationId, but others (specifically from the same B instance at the same time) appear under a DIFFERENT correlationId that doesn't match any other service's logs. What is the likely root cause?
_Hint:_ Service B is receiving requests without `X-Correlation-ID` header from some callers (not all callers propagate the header). When the header is absent: Service B generates a new UUID. This new UUID is unknown to any upstream service — it appears as an orphaned UUID with no cross-service correlation. The problem: some callers (maybe an internal cronjob, a batch process, or a new microservice) are not propagating the header. Diagnosis: check B's logs for the orphaned correlation IDs. Find the callers that generated those requests (check service name in logs, or IP, or User-Agent). Those callers are missing correlation ID propagation. Fix: add correlation ID propagation to all callers. Make generating a new ID (for missing header) emit a WARNING log — this signals a propagation gap.

**Q3 (C - Design Trade-off):** An architect proposes using the existing `orderId` as the correlation ID for all logs related to an order's processing — rather than generating a separate UUID. The argument: "orderId is already propagated everywhere, no need for another field." What are the arguments for and against this approach?
_Hint:_ For: (1) No additional field to propagate. (2) orderId is already meaningful (can cross-reference with order database). (3) Simpler implementation (no filter, no UUID generation). Against: (1) A single order may involve MULTIPLE requests (create order, update order, retry failed payment, customer queries order status). Each is a separate request with separate logs. orderId does NOT uniquely identify a REQUEST — it identifies a BUSINESS ENTITY. Searching by orderId returns ALL requests for that order (potentially many) — not the specific request you're debugging. (2) Not all requests have an orderId (pre-order steps, authentication calls, health checks). UUID correlation ID works universally; orderId only for order-related requests. (3) User-reported errors: "my order failed" → orderId may be unknown to the user (not shown in UI). correlationId = UUID is shown in error response → user can report it. Correct design: use BOTH. Include `correlationId` (unique per request) AND `orderId` (unique per business entity) in all logs. Each serves a different query: "what happened in this specific request?" (correlationId) vs "what happened to this order across all requests?" (orderId).

