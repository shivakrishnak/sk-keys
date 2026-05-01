---
layout: default
title: "Correlation ID"
parent: "Distributed Systems"
nav_order: 612
permalink: /distributed-systems/correlation-id/
number: "612"
category: Distributed Systems
difficulty: ★★☆
depends_on: "Distributed Tracing, Logging"
used_by: "Spring Cloud Sleuth, MDC, API Gateways, Log Aggregation"
tags: #intermediate, #distributed, #observability, #logging, #debugging
---

# 612 — Correlation ID

`#intermediate` `#distributed` `#observability` `#logging` `#debugging`

⚡ TL;DR — A **Correlation ID** is a unique identifier attached to every request at entry and propagated across all services, enabling you to filter all related log lines for a single user interaction across a distributed system.

| #612 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Distributed Tracing, Logging | |
| **Used by:** | Spring Cloud Sleuth, MDC, API Gateways, Log Aggregation | |

---

### 📘 Textbook Definition

**Correlation ID** (also: Request ID, Trace ID in simple form) is a unique identifier generated at the entry point of a system (API gateway, load balancer, or first service) and propagated through all downstream calls via HTTP headers, message headers, and log MDC (Mapped Diagnostic Context). Every log statement emitted by any service during the request lifetime includes this ID. Purpose: enable cross-service log correlation in a log aggregation system (ELK, Splunk, Datadog) by filtering all logs by correlation ID. Differs from full distributed tracing: correlation ID is a single flat ID (no span hierarchy, no timing data, no parent-child relationships). Simpler to implement; less powerful for latency analysis. Predecessor to full distributed tracing. The W3C `traceparent` header's traceId component IS effectively a correlation ID with standardized format.

---

### 🟢 Simple Definition (Easy)

Customer calls support: "My order ABC-123 is broken." Agent checks the logs: "SELECT * WHERE correlationId = 'request-xyz'." All log lines from all 10 services for that request appear in order. Without correlation ID: "The error was at 10:05:23.123... let me find that timestamp in OrderService logs... and InventoryService logs... and PaymentService logs..." — 30 minutes of manual log cross-referencing.

---

### 🔵 Simple Definition (Elaborated)

Implementation: API Gateway generates UUID on every request. Sets `X-Correlation-ID: uuid` header. Every downstream service: reads header, stores in thread-local (MDC). Every log statement: automatically includes `[correlationId=uuid]`. When calling other services: sets the same header on outgoing request. Log query: `correlationId = "abc-123"` → all services' logs for that request, sorted by timestamp. The upgrade path: Correlation ID → Distributed Tracing (add span IDs and timing → full request timeline, not just logs).

---

### 🔩 First Principles Explanation

**MDC-based correlation ID propagation in Java:**

```
CORRELATION ID LIFECYCLE:

  1. Client: sends HTTP request (no X-Correlation-ID header — first entry).
  
  2. API Gateway / entry service:
     a. No header present: generate new UUID: "req-7a3f9b2c".
     b. Header present (from trusted source/client SDK): use provided ID.
     c. Set MDC: MDC.put("correlationId", "req-7a3f9b2c").
     d. All log statements from this thread: auto-include correlationId.
     
  3. Service calls downstream (HTTP):
     RestTemplate / WebClient: adds header:
     X-Correlation-ID: req-7a3f9b2c
     
  4. Downstream service (OrderService):
     Filter/interceptor: reads X-Correlation-ID header.
     Sets MDC: MDC.put("correlationId", "req-7a3f9b2c").
     All logs: include correlationId automatically.
     
  5. OrderService calls InventoryService:
     Same: propagates X-Correlation-ID header.
     
  6. Log aggregation (ELK/Splunk):
     All services ship logs to central store.
     Query: correlationId="req-7a3f9b2c"
     Result: ALL log lines from ALL services, ordered by timestamp.
     
  7. Cleanup:
     MDC.clear() after request completes (or MDC.remove("correlationId")).
     IMPORTANT: thread pool reuse → MDC persists between requests without cleanup.
     Always clear MDC in finally block or request completion hook.

LOG FORMAT WITH CORRELATION ID:

  # Logback pattern:
  %d{ISO8601} [%thread] %-5level [correlationId=%X{correlationId}] %logger{36} - %msg%n
  
  Output:
  2024-01-15T10:05:23.123 [http-nio-8080-exec-1] INFO  [correlationId=req-7a3f9b2c] c.e.OrderService - Processing order for user 456
  2024-01-15T10:05:23.145 [http-nio-8080-exec-1] DEBUG [correlationId=req-7a3f9b2c] c.e.OrderRepo - Executing SQL: SELECT * FROM orders WHERE user_id=456
  2024-01-15T10:05:23.148 [http-nio-8080-exec-1] INFO  [correlationId=req-7a3f9b2c] c.e.InventoryClient - Calling InventoryService: GET /inventory/456
  
  # InventoryService (different process):
  2024-01-15T10:05:23.155 [http-nio-8081-exec-3] INFO  [correlationId=req-7a3f9b2c] c.e.InventoryService - Received request for user 456
  2024-01-15T10:05:23.158 [http-nio-8081-exec-3] ERROR [correlationId=req-7a3f9b2c] c.e.InventoryService - Item out of stock: item-999
  
  # Log aggregation query: correlationId=req-7a3f9b2c → all 5 lines, across 2 services.
  
THREAD POOLS AND ASYNC OPERATIONS (MDC PROPAGATION PROBLEM):

  MDC: thread-local. Async operations: different thread → MDC not inherited.
  
  PROBLEM:
    @Async method: MDC is empty → correlationId missing in async logs.
    CompletableFuture.supplyAsync(): new thread → no MDC.
    
  FIX (manual MDC copying):
    Map<String, String> mdc = MDC.getCopyOfContextMap(); // Capture before async.
    CompletableFuture.supplyAsync(() -> {
        MDC.setContextMap(mdc); // Restore in async thread.
        try {
            return doWork();
        } finally {
            MDC.clear();
        }
    }, executor);
    
  FIX (executor wrapper):
    // Wrap executor to auto-copy MDC context.
    public class MdcAwareExecutor implements Executor {
        private final Executor delegate;
        @Override
        public void execute(Runnable command) {
            Map<String, String> mdc = MDC.getCopyOfContextMap();
            delegate.execute(() -> {
                MDC.setContextMap(mdc != null ? mdc : Collections.emptyMap());
                try { command.run(); } finally { MDC.clear(); }
            });
        }
    }
    
KAFKA / MESSAGE QUEUE PROPAGATION:

  Producer: include correlationId in message headers.
    ProducerRecord<String, Event> record = new ProducerRecord<>("orders", event);
    String corrId = MDC.get("correlationId");
    if (corrId != null) {
        record.headers().add("X-Correlation-ID", corrId.getBytes());
    }
    
  Consumer: extract and set MDC.
    @KafkaListener(topics = "orders")
    public void consume(ConsumerRecord<String, Event> record) {
        Header corrHeader = record.headers().lastHeader("X-Correlation-ID");
        String corrId = corrHeader != null ? new String(corrHeader.value()) : UUID.randomUUID().toString();
        MDC.put("correlationId", corrId);
        try {
            processEvent(record.value());
        } finally {
            MDC.clear();
        }
    }
    
CORRELATION ID vs TRACE ID:

  Correlation ID:
    - Single flat UUID
    - No timing data
    - No span hierarchy
    - Used for: log correlation
    - Tool: MDC + log aggregation
    - Overhead: minimal (UUID generation + header propagation)
    
  Distributed Trace ID:
    - traceId + spanId + parentSpanId per service
    - Timing per span
    - Tree structure showing call hierarchy
    - Used for: latency analysis, dependency mapping
    - Tool: OpenTelemetry + Jaeger/Zipkin
    - Overhead: higher (span creation, reporting, sampling logic)
    
  The correlation ID IS the traceId in OpenTelemetry's W3C traceparent header.
  Migrating from correlation ID to full tracing: replace UUID generation with OTEL SDK.
  The existing X-Correlation-ID header: map to traceparent header.
  MDC: OTEL SDK auto-populates traceId/spanId in MDC when using bridge libraries.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT correlation ID:
- Log search for a failing request: timestamp-based grep across 10 service log files
- 30 minutes to reconstruct what happened for a single user complaint
- Race conditions in log timestamps make ordering unreliable

WITH correlation ID:
→ `grep correlationId="abc-123"` across all service logs → instant full picture
→ Customer support: self-service log lookup for any reported issue
→ Foundation for distributed tracing upgrade path

---

### 🧠 Mental Model / Analogy

> Crime scene investigation case number: every piece of evidence (log line) gets tagged with the case number. Any detective (service) working the case writes the case number on every report. The evidence room (log aggregation): "show me all evidence for case #7a3f9b2c" → every report from every detective, in order. Without case numbers: "look for evidence from Tuesday afternoon related to the blue car" — hours of manual sorting.

"Case number" = correlation ID UUID
"Detective's report" = log line with MDC
"Evidence room query" = ELK/Splunk query by correlationId

---

### ⚙️ How It Works (Mechanism)

```
SPRING BOOT FILTER (automatic correlation ID generation and propagation):

  @Component
  @Order(Ordered.HIGHEST_PRECEDENCE)
  public class CorrelationIdFilter extends OncePerRequestFilter {
      
      private static final String CORRELATION_ID_HEADER = "X-Correlation-ID";
      private static final String MDC_KEY = "correlationId";
      
      @Override
      protected void doFilterInternal(HttpServletRequest request,
              HttpServletResponse response, FilterChain chain)
              throws ServletException, IOException {
          
          String correlationId = request.getHeader(CORRELATION_ID_HEADER);
          if (correlationId == null || correlationId.isBlank()) {
              correlationId = UUID.randomUUID().toString();
          }
          
          MDC.put(MDC_KEY, correlationId);
          response.addHeader(CORRELATION_ID_HEADER, correlationId); // Echo back to client.
          
          try {
              chain.doFilter(request, response);
          } finally {
              MDC.remove(MDC_KEY); // CRITICAL: clear before thread returns to pool.
          }
      }
  }
```

---

### 🔄 How It Connects (Mini-Map)

```
Logging (structured logs per service — no cross-service linkage)
        │
        ▼ (correlation ID links logs across services)
Correlation ID ◄──── (you are here)
(single UUID → cross-service log correlation)
        │
        ▼ (add span hierarchy + timing → full observability)
Distributed Tracing (trace/span tree → latency analysis)
```

---

### 💻 Code Example

```java
// RestTemplate interceptor: auto-propagate correlation ID on outgoing calls.
@Bean
public RestTemplate restTemplate() {
    RestTemplate rt = new RestTemplate();
    rt.getInterceptors().add((request, body, execution) -> {
        String corrId = MDC.get("correlationId");
        if (corrId != null) {
            request.getHeaders().add("X-Correlation-ID", corrId);
        }
        return execution.execute(request, body);
    });
    return rt;
}

// WebClient (reactive): propagate via context.
@Bean
public WebClient webClient() {
    return WebClient.builder()
        .filter((request, next) -> {
            String corrId = MDC.get("correlationId");
            ClientRequest updated = corrId != null
                ? ClientRequest.from(request)
                    .header("X-Correlation-ID", corrId).build()
                : request;
            return next.exchange(updated);
        })
        .build();
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Correlation ID and Trace ID are the same thing | Correlation ID: simple UUID for log correlation. Trace ID: part of a full distributed trace (includes spans, timing, parent-child hierarchy). W3C traceparent uses a 128-bit traceId — technically a correlation ID with structure. OpenTelemetry's traceId IS a correlation ID that can also be used as MDC correlationId. But a bare correlation ID has no span hierarchy, timing, or observability tooling |
| MDC is automatically propagated to async threads | MDC is thread-local. CompletableFuture, @Async, reactive streams (Project Reactor), virtual threads — all require explicit MDC copying/restoration. Reactor: use `reactor.util.context.Context` and bridge with MDC. Forgetting this: async log lines lose correlationId → partial log correlation |
| The client should never set the Correlation ID | For trusted internal services and developer tools: clients CAN set the correlation ID to trace end-to-end including client-side operations. For external/public APIs: validate the format (UUID regex) and reject or replace malformed values to prevent injection attacks. Never blindly log user-provided values without sanitization |

---

### 🔥 Pitfalls in Production

**MDC leak between requests in thread pool:**

```
BAD: No MDC cleanup → previous request's correlationId bleeds into next request.

  @Component
  public class BadFilter extends OncePerRequestFilter {
      @Override
      protected void doFilterInternal(...) throws ... {
          String corrId = request.getHeader("X-Correlation-ID");
          if (corrId == null) corrId = UUID.randomUUID().toString();
          MDC.put("correlationId", corrId);
          chain.doFilter(request, response);
          // MISSING: MDC.remove()!
          // Thread returns to pool with old correlationId in MDC.
          // Next request on this thread: logs show WRONG correlationId.
      }
  }
  
  Symptom: Log aggregation shows request X's correlationId on log lines from request Y.
  Very confusing: "why does order-123 trace show inventory lookup for user-456?"
  
FIX: Always clear MDC in finally block:
  try {
      MDC.put("correlationId", corrId);
      chain.doFilter(request, response);
  } finally {
      MDC.remove("correlationId"); // Or MDC.clear() if you own all MDC keys.
  }
```

---

### 🔗 Related Keywords

- `Distributed Tracing` — the full upgrade: adds span hierarchy and timing to correlation ID
- `MDC (Mapped Diagnostic Context)` — the thread-local mechanism for attaching correlationId to all log lines
- `OpenTelemetry` — standardizes correlation ID as traceId in W3C traceparent header
- `Log Aggregation` — ELK/Splunk where correlation ID queries provide cross-service view
- `API Gateway` — the entry point responsible for generating correlation IDs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ UUID at entry → propagated in headers →  │
│              │ stored in MDC → appears in all log lines  │
│              │ → queryable across all services           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any multi-service system; baseline        │
│              │ observability before full distributed     │
│              │ tracing; customer support log lookup      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ There's nothing to avoid — always use it;│
│              │ if doing full OTel tracing: use traceId   │
│              │ as the correlationId (same thing)         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Case number on every piece of evidence: │
│              │  one ID → all clues, all services."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ MDC → Distributed Tracing → OpenTelemetry│
│              │ → Log Aggregation → API Gateway           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have correlation IDs in all services. A user reports an error: "Order failed at 2:15 PM." You query ELK: `correlationId="abc-xyz"` — 0 results. What are 5 reasons the logs might not be there? What is your systematic investigation approach?

**Q2.** Your API Gateway generates correlation IDs. A customer's mobile app SDK also generates a `X-Request-ID` header. Should you use the client-provided ID or replace it with a gateway-generated one? What are the security implications of trusting a client-provided correlation ID? Design a policy that allows trusted SDK clients to set their own IDs while preventing ID injection from untrusted sources.
