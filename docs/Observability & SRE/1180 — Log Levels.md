---
layout: default
title: "Log Levels"
parent: "Observability & SRE"
nav_order: 1180
permalink: /observability/log-levels/
number: "1180"
category: Observability & SRE
difficulty: ★☆☆
depends_on: "Logging"
used_by: "Structured Logging, Log Aggregation, Observability"
tags: #observability, #log-levels, #debug, #info, #warn, #error, #trace
---

# 1180 — Log Levels

`#observability` `#log-levels` `#debug` `#info` `#warn` `#error` `#trace`

⚡ TL;DR — **Log levels** classify the severity and purpose of log messages. Standard levels (lowest to highest): TRACE → DEBUG → INFO → WARN → ERROR → FATAL. Production systems typically log at INFO and above. DEBUG is enabled temporarily for troubleshooting. Choosing the wrong level creates either noise (too much INFO) or silence (real errors logged at DEBUG). Getting log levels right is fundamental to useful observability.

| #1180           | Category: Observability & SRE                      | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Logging                                            |                 |
| **Used by:**    | Structured Logging, Log Aggregation, Observability |                 |

---

### 📘 Textbook Definition

**Log levels** (log severity levels): a hierarchy of classifications for log messages indicating their importance, urgency, and purpose. Standard levels in Java (SLF4J/Logback): **TRACE** (finest detail, disabled in production), **DEBUG** (detailed debugging information, disabled in production), **INFO** (normal business events and flow, the production baseline), **WARN** (unexpected but handled situations, potential problems), **ERROR** (failures that affect functionality, require attention), and effectively **FATAL** (Logback maps to ERROR; Log4j2 has FATAL for unrecoverable failures). The level hierarchy: logging at level X includes all messages at level X and above. If the log level is set to INFO: INFO, WARN, and ERROR messages are emitted; TRACE and DEBUG messages are suppressed. This enables: (1) **Production efficiency**: suppress verbose DEBUG logs in production (performance, noise, cost); (2) **Selective verbosity**: enable DEBUG for specific packages when troubleshooting without flooding all logs; (3) **Alerting integration**: alert on ERROR logs automatically; monitor WARN for trend analysis. The challenge is consistency: different developers use different levels for the same situations, making alerting on ERROR unreliable. Establishing team-wide log level conventions is as important as the technical configuration.

---

### 🟢 Simple Definition (Easy)

Log levels are like email priority flags. TRACE/DEBUG = internal notes only relevant to the developer who wrote the code. INFO = normal business updates everyone should know. WARN = something is off but we handled it — keep an eye on it. ERROR = something broke and needs to be fixed. In production you only show INFO, WARN, ERROR — not the internal notes (DEBUG/TRACE) which would be overwhelming noise.

---

### 🔵 Simple Definition (Elaborated)

**Level reference guide**:

| Level   | When to use                        | Production?                 | Example                                                       |
| ------- | ---------------------------------- | --------------------------- | ------------------------------------------------------------- |
| `TRACE` | Step-by-step internal method calls | Never                       | `"Entering calculateDiscount(), params: ..."`                 |
| `DEBUG` | Diagnostic flow detail             | Only during troubleshooting | `"Cart items validated: 3 items, total $149.99"`              |
| `INFO`  | Normal business events             | ✓ Always                    | `"Order 456 created for user 123, total $49.99"`              |
| `WARN`  | Handled anomalies, degraded mode   | ✓ Always                    | `"Inventory service unreachable; using cached data"`          |
| `ERROR` | Failures requiring attention       | ✓ Always                    | `"Payment processing failed for order 456: card declined"`    |
| `FATAL` | Unrecoverable system failures      | ✓ Always (rare)             | `"Cannot connect to database after 5 retries; shutting down"` |

**The key question for each log**: "If I'm on-call and this message appears at 3 AM, do I need to wake up?"

- ERROR → you might need to wake up (failed operation)
- WARN → probably not now, but investigate in the morning
- INFO → expected behavior, no action needed
- DEBUG → never wake up for this

**Common mistakes**:

- Log every retry attempt at ERROR → too many non-actionable alerts
- Log successful operations at WARN → confusing, creates noise
- Catch and silently swallow exceptions (log at DEBUG) → real errors invisible
- Log all method entries at INFO → performance impact and noise

---

### 🔩 First Principles Explanation

```java
// LOG LEVEL GUIDELINES WITH EXAMPLES

@Slf4j
@Service
public class PaymentService {

    public PaymentResult processPayment(PaymentRequest request) {

        // TRACE: Method entry with all parameters
        // Use when: detailed method-level debugging needed
        // Production: NEVER (too noisy)
        log.trace("processPayment() called: orderId={}, amount={}, currency={}, provider={}",
            request.getOrderId(), request.getAmount(), request.getCurrency(),
            request.getProvider());

        // DEBUG: intermediate step with relevant state
        // Use when: diagnosing a specific flow issue
        // Production: disabled (logback config: logger level=INFO in production)
        log.debug("Payment request validated; sending to provider: provider={}, tokenized={}",
            request.getProvider(), request.isTokenized());

        try {
            PaymentResult result = stripeClient.charge(request);

            // INFO: successful business event
            // Use when: something meaningful and expected happened
            // Production: ALWAYS logged (business audit trail)
            log.info("Payment processed successfully",
                kv("orderId", request.getOrderId()),
                kv("paymentId", result.getPaymentId()),
                kv("amount", request.getAmount()),
                kv("provider", request.getProvider()),
                kv("event", "payment.processed")
            );

            return result;

        } catch (CardDeclinedException e) {
            // WARN: expected business error — card was declined (common, handled)
            // Use when: handled exception; not a system failure; expected to happen
            // Production: logged; should NOT trigger an alert on its own
            log.warn("Payment declined",
                kv("orderId", request.getOrderId()),
                kv("declineCode", e.getDeclineCode()),
                kv("event", "payment.declined")
            );
            // Don't log stack trace for expected business errors (noise)
            return PaymentResult.declined(e.getDeclineCode());

        } catch (PaymentProviderUnavailableException e) {
            // WARN: provider temporarily unavailable; will retry (handled, transient)
            log.warn("Payment provider unavailable; will retry in {}s",
                RETRY_DELAY_SECONDS,
                kv("provider", request.getProvider()),
                kv("attempt", e.getAttemptNumber()),
                kv("event", "payment.provider.unavailable")
            );
            throw e;  // retry logic in caller

        } catch (Exception e) {
            // ERROR: unexpected failure — system-level problem requiring investigation
            // Use when: unhandled exception; operation failed in unexpected way
            // Production: triggers alert; on-call engineer should investigate
            log.error("Unexpected payment processing failure",
                kv("orderId", request.getOrderId()),
                kv("provider", request.getProvider()),
                kv("event", "payment.failed.unexpected"),
                e  // ← include exception = log stack trace (critical for ERROR)
            );
            throw new PaymentServiceException("Payment failed", e);
        }
    }
}
```

```xml
<!-- logback-spring.xml: configuring log levels per package -->
<configuration>

  <!-- PRODUCTION: only INFO and above for most code -->
  <springProfile name="production">
    <root level="INFO"/>

    <!-- External frameworks: suppress their verbose INFO logs -->
    <logger name="org.springframework"     level="WARN"/>
    <logger name="org.hibernate"           level="WARN"/>
    <logger name="com.zaxxer.hikari"       level="WARN"/>

    <!-- Our code: INFO in production -->
    <logger name="com.company.orderservice" level="INFO"/>

    <!-- Temporary: enable DEBUG for specific package during incident investigation -->
    <!-- REMEMBER TO REMOVE AFTER INVESTIGATION! -->
    <!-- <logger name="com.company.orderservice.payment" level="DEBUG"/> -->
  </springProfile>

  <!-- DEVELOPMENT: DEBUG for our code; INFO for frameworks -->
  <springProfile name="!production">
    <root level="INFO"/>
    <logger name="com.company.orderservice" level="DEBUG"/>
  </springProfile>

</configuration>
```

```
LOG LEVEL DECISION TREE:

  Is this called on every request with no useful signal?
  → TRACE (disabled; method entry/exit logging)

  Is this internal implementation detail useful during debugging?
  → DEBUG (disabled in production; detailed state logging)

  Did a normal, expected business event occur?
  → INFO (enabled in production; business audit trail)

  Did something unexpected happen that was handled?
  Did a service degrade to a fallback mode?
  → WARN (enabled; worth monitoring for trends, but not alerting immediately)

  Did an operation FAIL unexpectedly?
  Will a user or business process be impacted?
  → ERROR (enabled; triggers alert; on-call should investigate)

  Is the APPLICATION itself unable to continue?
  → FATAL/ERROR with "shutting down" context (critical; page everyone)

  ANTI-PATTERNS:
  ✗ Using ERROR for card_declined (expected business failure → WARN)
  ✗ Using INFO for "entering method X" (too noisy → TRACE/DEBUG)
  ✗ Catching exception and logging at DEBUG (hides real failures → ERROR)
  ✗ Using WARN for all exceptions (hides severity → reserve WARN for handled cases)
```

---

### ❓ Why Does This Exist (Why Before What)

Without log levels, every log message is equal. In production with thousands of messages per second, a developer debugging an incident must scroll through millions of irrelevant lines to find error messages. Log levels exist to: (1) allow production systems to suppress verbose debugging logs (performance); (2) enable filtering — "show me only ERROR messages"; (3) drive alerting — "alert when ERROR count spikes"; (4) communicate priority — readers immediately see severity without reading the full message.

---

### 🧠 Mental Model / Analogy

> **Log levels are like a hospital triage system**: TRACE/DEBUG = a doctor's detailed clinical notes (important internally, not relevant to the ER triage team); INFO = a patient chart update (normal progress, for the record); WARN = a yellow flag (something to monitor, not critical yet); ERROR = a red flag (needs attention now); FATAL = a code blue (immediate emergency). Just as a hospital filters who sees which information based on urgency, log levels filter who (which monitoring system, which dashboard) sees which log messages.

---

### 🔄 How It Connects (Mini-Map)

```
Log messages need severity classification for production filtering and alerting
        │
        ▼
Log Levels ◄── (you are here)
(TRACE → DEBUG → INFO → WARN → ERROR → FATAL; production = INFO+)
        │
        ├── Logging: log levels are a core component of any logging framework
        ├── Structured Logging: log level is a standard field in every JSON log event
        ├── Log Aggregation: filter by level (query: level:"ERROR") in ELK/Loki
        └── Observability: error level drives alerting in monitoring tools
```

---

### 💻 Code Example

```java
// DYNAMIC LOG LEVEL CHANGE: enable DEBUG temporarily in production

// Spring Boot Actuator allows changing log levels at runtime via HTTP API
// No restart required! Very useful for temporary production troubleshooting.

// Step 1: Enable actuator loggers endpoint in application.yml:
management.endpoints.web.exposure.include: loggers

// Step 2: During incident, enable DEBUG for a specific class:
// POST /actuator/loggers/com.company.orderservice.payment
// Body: {"configuredLevel": "DEBUG"}

// Step 3: Reproduce the issue; collect DEBUG logs for diagnosis

// Step 4: IMPORTANT — revert after diagnosis!
// POST /actuator/loggers/com.company.orderservice.payment
// Body: {"configuredLevel": null}  (resets to default)

// WARNING: enabling DEBUG in production on a high-traffic service
// can generate gigabytes of logs per minute — don't forget to revert!
```

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| WARN means "investigate immediately"      | WARN means "something unexpected happened but it was handled." WARNs are worth monitoring for TRENDS (if WARN rate doubles, investigate), but a single WARN is often expected and benign (a retry succeeded, a fallback was used). Alerts should fire on WARN rate trends, not on individual WARN occurrences. Reserve immediate alerts for ERROR.                                                 |
| ERROR should always include a stack trace | Stack traces are essential for unexpected exceptions (bugs). But for expected business errors caught and re-thrown (e.g., `ValidationException`), a stack trace adds noise — the message and context fields tell the whole story. Rule: ERROR from an unexpected `catch (Exception e)` → include stack trace; ERROR from a known business failure → include relevant fields, skip the stack trace. |
| Log level changes require redeployment    | Spring Boot Actuator (and other frameworks' admin interfaces) allow changing log levels at runtime without restart. This is critical in production: enable DEBUG for the specific class you're troubleshooting, diagnose the issue, revert to INFO — all without deploying new code or restarting the service.                                                                                     |

---

### 🔗 Related Keywords

- `Logging` — log levels are part of every logging framework
- `Structured Logging` — level is a mandatory field in structured log schemas
- `Log Aggregation` — filter by level in aggregation tools; alert on ERROR spikes
- `Observability` — error rate (count of ERROR logs per minute) is a key metric

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOG LEVELS (lowest → highest severity):                │
│  TRACE  → detailed internal flow (dev only)            │
│  DEBUG  → diagnostic detail (disabled in production)  │
│  INFO   → normal business events ✓ PRODUCTION         │
│  WARN   → handled anomaly/fallback ✓ PRODUCTION       │
│  ERROR  → failed operation, needs investigation ✓     │
│  FATAL  → unrecoverable, application stopping ✓       │
│                                                          │
│ ALERT ON: ERROR rate threshold (not every ERROR)       │
│ MONITOR: WARN rate trends                              │
│ NEVER IN PRODUCTION: DEBUG/TRACE (unless troubleshooting)│
│ DYNAMIC CHANGE: Spring Actuator /actuator/loggers      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Alert fatigue from log-level-based alerts: if every ERROR log triggers a PagerDuty alert, teams start ignoring alerts because there are too many non-actionable ones. Common causes: retried operations logging ERROR even when eventually successful; expected business errors logged at ERROR instead of WARN; third-party library logging spurious ERRORs. Design an alert strategy based on log levels that minimizes alert fatigue while maintaining signal quality: should you alert on (a) any single ERROR log, (b) ERROR rate above a threshold (e.g., > 10 ERRORs/minute), (c) error RATE change (sudden spike vs baseline), or (d) specific ERROR event names? What combination gives you the best signal-to-noise ratio?

**Q2.** Log level conventions across a microservices org: with 15 teams each making their own decisions about log levels, the result is chaos. Team A logs circuit breaker activations at ERROR (so they get immediate alerts), Team B logs them at WARN (considered handled). The central SRE team's alerting is inconsistent. Design a company-wide log level convention document: for 8 common situations (expected business error, unexpected exception, external service timeout, retry attempts, fallback activation, service startup, health check, performance warning), define the correct log level and the rationale. How do you enforce this — code reviews? Shared library? Linting?
