---
layout: default
title: "Correlation ID"
parent: "Distributed Systems"
nav_order: 612
permalink: /distributed-systems/correlation-id/
number: "0612"
category: Distributed Systems
difficulty: ★★☆
depends_on: Distributed Tracing, Logging, HTTP & APIs, Microservices
used_by: Distributed Tracing, Observability, API Gateway, Service Mesh
related: Distributed Tracing, Idempotency (Distributed), Request-Response Pattern, Logging
tags:
  - distributed
  - observability
  - debugging
  - pattern
---

# 612 — Correlation ID

⚡ TL;DR — A correlation ID is a unique identifier attached to a request at its entry point and propagated through every service it touches, enabling engineers to search all logs and traces for that single ID and reconstruct the complete path of the request across the distributed system.

| #612 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Distributed Tracing, Logging, HTTP & APIs, Microservices | |
| **Used by:** | Distributed Tracing, Observability, API Gateway, Service Mesh | |
| **Related:** | Distributed Tracing, Idempotency (Distributed), Request-Response Pattern, Logging | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
User reports: "My order #45678 is stuck." Engineer looks at Order Service logs — thousands of log lines with no way to identify which log lines belong to order #45678's request. Searches for `orderId=45678` — finds 30 log lines in Order Service. None indicate failure. Checks Payment Service logs — no way to find the specific log line for THIS invocation (there have been 500 payment calls in the last hour, all logged as "payment processed"). Spends 2 hours cross-referencing timestamps across 5 services. Eventually gives up and blames a "transient error."

**WITH CORRELATION ID:**
Every request creates one UUID at the edge (API Gateway). Every log line in every service includes `correlationId=f47ac10b-58cc-4372-a567-0e02b2c3d479`. The engineer does one log search: `grep "f47ac10b" *.log`. All 8 log lines from all 5 services for THIS specific request appear immediately. Root cause found in 30 seconds.

---

### 📘 Textbook Definition

A **correlation ID** (also called request ID, trace ID in simple systems) is a unique identifier — typically a UUID — generated at the entry point of a request (API gateway, frontend, or first service) and propagated through all downstream service calls, message queue headers, and log entries. It enables **log correlation**: searching for the correlation ID in aggregated logs returns all log entries for that specific request journey, regardless of how many services it touched. **Standard HTTP header**: `X-Correlation-ID`, `X-Request-ID`, or the W3C `traceparent` header (in distributed tracing frameworks). **Scope**: a single correlation ID spans one "logical operation" — one API call, one message processing, one batch item. **Relationship to distributed tracing**: correlation ID is the simplest form of distributed tracing (one ID per request, no timing tree); proper distributed tracing (OpenTelemetry) adds span hierarchy, timing, and attributes on top of this foundation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Generate one UUID per request at the entry point and include it in every log line and every downstream call — then search all your logs with that one ID to reconstruct what happened.

**One analogy:**
> Correlation ID is like a hospital wristband. Every patient gets one unique ID at admission. Every test result, medication record, X-ray, and doctor's note goes on the chart under that patient's ID. If you need to look up everything that happened to a patient, you search by wristband ID — you don't have to correlate by name (which might be duplicated) or by time (which overlaps with other patients).

**One insight:**
The correlation ID is only valuable if it appears in EVERY log line throughout the entire request's journey. A service that logs "Payment processed successfully" without the correlation ID breaks the chain — that log line becomes unlinatable to the original request. The correlation ID must be propagated to thread pools, async executors, message headers, and every log statement.

---

### 🔩 First Principles Explanation

**PROPAGATION CHAIN:**
```
Client → API Gateway → Service A → Service B → Service C
                                             → Database (connection comment)
                              → Kafka message header
         API Gateway generates correlationId = "uuid-abc123"
         API Gateway: logs "request received uuid-abc123"
         API Gateway: adds header X-Correlation-ID: uuid-abc123 to request to Service A
         
         Service A: extracts correlation ID from header
         Service A: puts in SLF4J MDC (Mapped Diagnostic Context)
         Service A: logs "processing order" → MDC auto-appends correlationId=uuid-abc123
         Service A: calls Service B with header X-Correlation-ID: uuid-abc123
         Service A: sends Kafka message with header correlationId=uuid-abc123
         
         Service B: extracts from header, puts in MDC, logs with same ID
         Service C: extracts from header, puts in MDC, logs with same ID
         
Result: grep "uuid-abc123" in any service's logs → all log lines for this request
```

**SLF4J MDC PROPAGATION (JAVA/SPRING):**
```java
// Spring Web Filter — extracts/generates correlation ID:
@Component
public class CorrelationIdFilter extends OncePerRequestFilter {
    
    private static final String CORRELATION_ID_HEADER = "X-Correlation-ID";
    private static final String MDC_KEY = "correlationId";
    
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws IOException, ServletException {
        String correlationId = request.getHeader(CORRELATION_ID_HEADER);
        if (correlationId == null || correlationId.isBlank()) {
            correlationId = UUID.randomUUID().toString();  // Generate if not present
        }
        
        MDC.put(MDC_KEY, correlationId);  // Thread-local: auto-appended to all log lines
        response.setHeader(CORRELATION_ID_HEADER, correlationId); // Echo back to client
        
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.remove(MDC_KEY);  // Clean up after request
        }
    }
}

// Logback config — include MDC in log pattern:
// <pattern>%d{ISO8601} [%thread] %-5level %logger{36} [correlationId=%X{correlationId}] - %msg%n</pattern>

// Log output:
// 2024-01-15T10:30:45.123 [http-9] INFO PaymentService [correlationId=uuid-abc123] - Payment processed
```

**ASYNC THREAD POOL PROPAGATION:**
```java
// PROBLEM: MDC does not propagate across thread boundaries automatically:
ExecutorService executor = Executors.newFixedThreadPool(10);
executor.submit(() -> {
    // ← MDC.get("correlationId") is NULL here — different thread!
    log.info("Async processing"); // No correlationId in this log line!
});

// SOLUTION: Capture MDC before submitting, restore in the new thread:
Map<String, String> mdcContext = MDC.getCopyOfContextMap();
executor.submit(() -> {
    try {
        MDC.setContextMap(mdcContext); // Restore MDC in async thread
        log.info("Async processing"); // correlationId now present
        asyncOperation();
    } finally {
        MDC.clear();
    }
});

// BETTER SOLUTION: Use Spring's TaskDecorator:
@Bean
public ThreadPoolTaskExecutor asyncExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setTaskDecorator(runnable -> {
        Map<String, String> mdc = MDC.getCopyOfContextMap();
        return () -> {
            MDC.setContextMap(mdc != null ? mdc : Collections.emptyMap());
            try { runnable.run(); } finally { MDC.clear(); }
        };
    });
    return executor;
}
```

**KAFKA MESSAGE HEADER PROPAGATION:**
```java
// Producer: include correlation ID in Kafka message headers:
ProducerRecord<String, OrderEvent> record = new ProducerRecord<>("orders", event);
String correlationId = MDC.get("correlationId");
record.headers().add("X-Correlation-ID", correlationId.getBytes());

// Consumer: extract and set in MDC:
@KafkaListener(topics = "orders")
public void processOrder(ConsumerRecord<String, OrderEvent> record) {
    Header header = record.headers().lastHeader("X-Correlation-ID");
    if (header != null) {
        MDC.put("correlationId", new String(header.value()));
    }
    try {
        processOrderEvent(record.value());
    } finally {
        MDC.remove("correlationId");
    }
}
```

---

### 🧪 Thought Experiment

**CORRELATION ID vs. TRACE ID — WHEN TO USE WHICH:**

Simple monolith with 2 services:
→ Correlation ID is sufficient. One UUID, grep it in aggregated logs. No need for span hierarchy.

50-service microservices platform:
→ Distributed tracing (OpenTelemetry) is needed. Trace ID + span tree + timing data. Correlation ID alone can't show which service's sub-call was slow.

**CORRELATION ID IS THE FOUNDATION:**
Distributed tracing frameworks use the trace_id as their correlation ID. The trace_id in OpenTelemetry's `traceparent` header IS the correlation ID — it's just standardized and comes with a span hierarchy built on top. You don't choose between them; distributed tracing is a superset of correlation ID.

---

### 🧠 Mental Model / Analogy

> Correlation ID is the simplest possible federated tracking system: one sticky label that follows a piece of work everywhere it goes. Like a FedEx tracking number: the label goes on the package at origin, each hub scans it and logs its arrival/departure. Search the tracking number: see the complete journey. No timing tree, no fancy visualization — just the ability to find all log entries for one request in one search.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Generate a UUID per request at the entry point. Include it in every log line. Pass it to every downstream service via HTTP header. Grep it in aggregated logs to find the complete request path.

**Level 2:** SLF4J MDC for auto-appending to log lines. Spring Filter for extraction/generation. Async thread pool propagation using TaskDecorator. Kafka header propagation. Return correlation ID to client in response header so they can report it.

**Level 3:** Correlation ID is the minimum viable observability for distributed systems. Upgrade path: correlation ID (one UUID, flat log search) → distributed tracing (UUID + span tree + timing). Both should co-exist: use the trace_id as the correlation ID; log searches work AND tracing flamecharts work. APM tools (Datadog, Dynatrace) use correlation ID in error tracking: when an exception is reported, the correlation ID links the error report to the full trace.

**Level 4:** Security consideration: correlation IDs must not leak tenant isolation. In multi-tenant systems, a correlation ID should not allow one tenant to look up another tenant's request logs. Log access control must be scoped by tenant. Correlation IDs should not be guessable (use UUIDs, not sequential integers) to prevent a malicious actor from requesting a known correlation ID to look up another user's request information. For regulated systems (PCI-DSS, HIPAA), correlation IDs must be retained in audit logs for the compliance retention period (e.g., 7 years for financial transactions) alongside the full log entry they correlate.

---

### ⚙️ How It Works (Mechanism)

**Express.js Correlation ID Middleware:**
```javascript
const { v4: uuidv4 } = require('uuid');
const { createNamespace } = require('cls-hooked'); // Continuation Local Storage

const ns = createNamespace('request');

app.use((req, res, next) => {
    const correlationId = req.headers['x-correlation-id'] || uuidv4();
    res.setHeader('x-correlation-id', correlationId);
    
    // CLS propagates across async/await automatically:
    ns.run(() => {
        ns.set('correlationId', correlationId);
        next();
    });
});

// Logger reads from CLS:
const logger = {
    info: (msg, meta = {}) => console.log(JSON.stringify({
        level: 'info',
        message: msg,
        correlationId: ns.get('correlationId'),  // auto-included
        timestamp: new Date().toISOString(),
        ...meta
    }))
};
```

---

### ⚖️ Comparison Table

| Approach | Setup | Data Captured | Debug Power | Use When |
|---|---|---|---|---|
| No correlation | None | None | Cannot correlate | Never (for distributed systems) |
| Correlation ID | Low | Request path (flat) | Good (grep search) | Simple 2-3 service systems |
| Distributed Tracing | Medium | Request path + timing tree | Excellent | 4+ service systems |
| Full Observability | High | Traces + metrics + logs (linked) | Best | Production microservices |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Correlation ID automatically appears in all logs | Only if you put it in MDC and configure your log appender to include MDC. Log lines not going through SLF4J (e.g., System.out.println) won't have it |
| One correlation ID per service is enough | Correlation ID must be the SAME value across ALL services for one logical request. Using service-local IDs defeats the purpose |
| Correlation ID is only for debugging | Correlation ID is also used for: idempotency (same correlation ID = same logical operation), distributed tracing (base), security audit trail (who did what when) |

---

### 🚨 Failure Modes & Diagnosis

**Correlation ID Not Propagated to Async Workers**

Symptom: Service has correlation IDs in all synchronous log lines, but async Kafka
consumer log lines never have a correlationId. When debugging cross-service issues
that touch async processing, the trail goes cold the moment work is enqueued.

Cause: Kafka consumer is a separate thread; MDC is thread-local and not propagated.
Consumer log lines show `correlationId=null`.

Fix: Extract correlation ID from Kafka message header in consumer. Set MDC before
processing. Clear after. Add a lint check: any `@KafkaListener` method that doesn't
extract the correlation ID header fails the CI/CD pipeline (architectural fitness function).

---

### 🔗 Related Keywords

- `Distributed Tracing` — extends correlation ID with span hierarchy, timing, and attributes
- `Idempotency (Distributed)` — correlation ID can double as idempotency key for request deduplication
- `Observability` — correlation ID is the foundation of the "logs" pillar in observability
- `API Gateway` — the standard entry point for correlation ID generation in microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CORRELATION ID: one UUID per request, everywhere        │
│  Generate: at API Gateway / edge, if not provided        │
│  Propagate: X-Correlation-ID header → all downstream     │
│  Log: include in every log line via SLF4J MDC            │
│  Async: TaskDecorator or CLS to cross thread boundaries  │
│  Return: echo correlationId in response header           │
│  Evolve: correlation ID → trace ID in OpenTelemetry      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An engineer reports: "I added correlation ID propagation to all our HTTP calls between services, but when I search our aggregated logs by correlation ID, I can only find logs from 3 of our 5 services." List 5 possible reasons why 2 services might not have the correlation ID in their logs, and describe how you would diagnose each one.

**Q2.** A client calls your API and receives a 500 error. The response body contains: `{"error": "Internal Server Error", "correlationId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"}`. As the API client (not operator), how does having the correlation ID help you get faster support? As the API operator, what should your support runbook say to do with this correlation ID?
