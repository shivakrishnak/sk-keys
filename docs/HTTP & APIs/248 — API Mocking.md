---
layout: default
title: "API Mocking"
parent: "HTTP & APIs"
nav_order: 248
permalink: /http-apis/api-mocking/
number: "0248"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP, OpenAPI/Swagger
used_by: Frontend Development, Contract Testing, Integration Testing, API Design
related: API Contract Testing, OpenAPI/Swagger, Stubbing, WireMock
tags:
  - api
  - mocking
  - wiremock
  - stub
  - testing
  - intermediate
---

# 248 — API Mocking

⚡ TL;DR — API mocking creates a fake implementation of an API that returns predefined responses, enabling frontend/consumer development without a running backend, isolating services for testing, and simulating error conditions and edge cases that are difficult to reproduce with real services.

| #248 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP, OpenAPI/Swagger | |
| **Used by:** | Frontend Development, Contract Testing, Integration Testing, API Design | |
| **Related:** | API Contract Testing, OpenAPI/Swagger, Stubbing, WireMock | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Frontend team starts building the UI. Backend API isn't ready for 3 more weeks.
Frontend team is blocked — or must write hardcoded fake data directly in the UI code,
then rip it out later. QA can't test error handling because the real payment gateway
never actually fails in staging. Integration tests are flaky because the third-party
SMS service is slow and sometimes returns 500. Rate limits on the Stripe test API
cause CI to fail intermittently. All of these problems stem from being locked to
real APIs that are unavailable, unreliable, or too expensive to use freely.

**THE INVENTION MOMENT:**
API mocking decouples the consumer's development cycle from the provider's readiness.
WireMock (2011) popularized stub HTTP servers for Java test environments. MockServer,
Prism (from OpenAPI specs), and Mockoon (UI-based) followed. For Pact: the consumer
pact test automatically spins up a mock server, making mocks a byproduct of writing
consumer contract tests — one tool, two benefits (isolated test + contract generation).

---

### 📘 Textbook Definition

**API Mocking** is the practice of creating a simulated API that mimics the behavior
of a real service by returning predefined responses to known requests. A **mock** returns
canned responses regardless of implementation logic; a **stub** is similar but may have
minimal state; a **fake** has working implementation logic but not production-ready
(e.g., in-memory database). In testing contexts, **WireMock** is the dominant Java
library for stubbing HTTP interactions — it starts an embedded HTTP server, stubs
request-response pairs, and verifies that expected requests were made. For API design,
**Prism** generates a mock server directly from an OpenAPI specification, enabling
frontend teams to develop against the spec before the real API is built.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API mocking is a fake server that says "when you call this endpoint, I'll return THIS
response" — enabling development and testing of consumers without the real API running.

**One analogy:**

> API mocking is like a flight simulator.
> Trainee pilots (consumer developers) need to practice flying (call APIs) without
> crashing a real plane (hitting production services). The simulator (mock server)
> responds exactly like a real plane would — including engine failures (500 errors),
> instrument readings (response payloads), and radar signals (third-party responses).
> All training happens in isolation. No real system is at risk.

**One insight:**
The most overlooked use of mocks is simulating failure modes: what happens when the
payment API returns HTTP 503? When the auth service times out? Real services rarely
fail in test environments. Mocks let you explicitly inject failures to verify your
error handling is correct — before production does it for you.

---

### 🔩 First Principles Explanation

**TYPES OF TEST DOUBLES:**

```
Test doubles (Martin Fowler taxonomy):

  DUMMY:   Object passed around, never actually used.
           Example: null value passed to satisfy parameter requirement.

  STUB:    Returns canned answers to calls made during test.
           Example: WireMock stub: GET /users/1 → 200 {"id":1,"name":"Alice"}

  MOCK:    Pre-programmed with expectations, verifies behavior.
           Example: WireMock verify: "was GET /users/1 called exactly once?"

  FAKE:    Working implementation (not production-ready).
           Example: H2 in-memory database instead of PostgreSQL.

  SPY:     Real implementation but records interactions for assertion.
           Example: Mockito spy wrapping a real service.

For API MOCKING:  we use stubs + verification (WireMock) or pure stubs (Prism/Mockoon).
```

**WIREMOCK STUB ANATOMY:**

```java
// WireMock stub: define what to match, what to return
stubFor(get(urlEqualTo("/api/v1/users/1"))
    .withHeader("Accept", containing("application/json"))
    .willReturn(aResponse()
        .withStatus(200)
        .withHeader("Content-Type", "application/json")
        .withBody("""
            {
              "id": 1,
              "name": "Alice",
              "email": "alice@example.com"
            }
        """)
    )
);

// Request matching options:
// urlEqualTo("/exact/path")
// urlMatching("/users/[0-9]+")  ← regex
// urlPathMatching(...)           ← path only (ignore query params)
// withQueryParam("page", equalTo("1"))
// withRequestBody(matchingJsonPath("$.email"))  ← JSON path match

// Response options:
// withStatus(503)  ← simulate failure
// withFixedDelay(2000)  ← simulate latency (2 seconds)
// withBodyFile("__files/users.json")  ← load from file
// withFault(Fault.CONNECTION_RESET_BY_PEER)  ← simulate network fault
```

---

### 🧪 Thought Experiment

**SCENARIO:** Testing a checkout service that calls payment API + inventory API.

```
REAL SERVICES IN TESTS:
  Bank holiday → payment API returns 503 intermittently
  Inventory API is shared with production → tests consume real inventory
  Rate limits hit after 50 CI runs → builds fail
  Can't test "payment declined" scenario without real declined card

WITH WIREMOCK:
  Stub 1: payment success
    POST /payments → 201 {"transactionId": "TXN-123", "status": "approved"}
  Stub 2: payment declined
    POST /payments → 402 {"code": "CARD_DECLINED", "message": "Insufficient funds"}
  Stub 3: payment timeout
    POST /payments → (withFixedDelay(30000)) → timeout triggers
  Stub 4: payment service outage
    POST /payments → withFault(Fault.CONNECTION_RESET_BY_PEER)

  Tests for each scenario:
  checkout.process(cart) → verify order status = "confirmed" (success)
  checkout.process(cart) → verify OrderFailedException thrown, reason = "CARD_DECLINED"
  checkout.process(cart) → verify timeout handling, circuit breaker opens
  checkout.process(cart) → verify graceful degradation, retry logic

  All tests deterministic, fast, isolated. No external dependencies.
```

---

### 🧠 Mental Model / Analogy

> API mocking is like a film studio backlot.
> Movies (applications) need to appear to interact with real environments: New York streets,
> hospital operating rooms, busy airports. Building real sets is expensive and uncontrollable.
> The backlot (mock server) has facades that look exactly like the real thing to the camera (your code).
> The director (test engineer) can control every detail: "now make it rain" (inject 503),
> "make the car explode" (trigger timeout), "make it sunny" (success response).
> Full control. Complete isolation. No real New York required.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
API mocking is a pretend server that answers API calls with fake responses you control.
Your app thinks it's talking to the real payment service, but it's actually talking to
a fake one you set up for testing purposes.

**Level 2 — How to use it (junior developer):**
Add `wiremock-spring-boot` dependency. In `@SpringBootTest`: WireMock automatically
starts. Use `stubFor(get(...).willReturn(...))` to define responses. Run tests — they
call WireMock's port, not the real service. Use `@WireMockTest` annotation for test
class. For standalone mock server during frontend development: `docker run wiremock/wiremock`
and POST stub definitions to `/__admin/mappings`.

**Level 3 — How it works (mid-level engineer):**
WireMock starts an embedded Jetty server on a configured port. Stubs are stored as
`StubMapping` objects with request matchers (URL, headers, body patterns) and response
definitions. For each incoming request: WireMock evaluates stub matchers by priority
(highest priority first); first match wins; returns defined response. Request journal
records all received requests for later verification (`verify(getRequestedFor(urlEqualTo(...)))`).
For Spring Boot: `WireMock.configureFor(port)` connects the client to the embedded
server. State machine scenarios (WireMock Scenarios) enable stateful stubs: stub A
returns "empty cart" and transitions to state "item added"; stub B returns "cart with item."
Record-and-playback mode lets WireMock proxy real API calls, record them as stub files,
and replay for offline testing.

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental value of API mocking in production-grade systems isn't just "isolated
tests" — it's test determinism and failure scenario coverage. Real external APIs are
non-deterministic: rate limits, network latency, schema changes, data state. Tests
against real APIs are flaky, slow to run, and can't cover the full failure matrix.
WireMock's design philosophy (from Tom Akehurst's original Groovy implementation) was
to make HTTP stubbing as declarative as possible, matching how developers think about
HTTP interactions. The key architectural decision: request matching by matchers (flexible)
rather than exact bytes (brittle), enabling mocks to be resilient to irrelevant request
variations while catching meaningful changes. For contract testing (Pact): the mock
server IS a byproduct of the consumer test — the interaction the consumer tested against
the mock becomes the pact file. One test run → both a passing consumer test AND a
generated contract.

---

### ⚙️ How It Works (Mechanism)

```
WIREMOCK EMBEDDED IN SPRING BOOT TEST:

  Test JVM starts
  │
  ├─ @SpringBootTest launches Application Context
  │    └─ Payment service URL → "http://localhost:${wiremock.port}"
  │
  ├─ @WireMockTest annotation: WireMock embedded server starts on random port
  │
  ├─ Test method: stubFor(post("/payments").willReturn(ok().withBody("...")))
  │
  ├─ Test calls: checkoutService.processPayment(cart)
  │    └─ PaymentClient: POST http://localhost:${wiremock.port}/payments
  │    └─ WireMock: matches stub → returns predefined response
  │
  ├─ Assertions: result == expected behavior
  │
  └─ verify(postRequestedFor(urlEqualTo("/payments")).withRequestBody(
         matchingJsonPath("$.amount", equalTo("99.99"))
     ));

PRISM MOCK SERVER FROM OPENAPI SPEC:
  $ npx @stoplight/prism-cli mock openapi.yaml
  [3:30:12 PM] › [CLI] …  awaiting  Starting Prism…
  [3:30:12 PM] › [CLI] ✔  success   Prism is listening on http://127.0.0.1:4010

  GET http://127.0.0.1:4010/api/v1/users/1
  ← 200 {"id": "random-uuid", "name": "Alice", "email": "alice@example.com"}
  (generated from spec schema examples)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
FRONTEND PARALLEL DEVELOPMENT WITH PRISM:

  Week 1, Day 1:
  Backend: writes OpenAPI spec for user service
  Team review: approved

  Frontend team:
  → prism mock openapi.yaml → http://localhost:4010
  → Builds UI against mock: GET /users, POST /users, etc.
  → Spec has examples → realistic mock responses

  Backend team:
  → Implements real service against same spec

  Week 3: Backend service ready
  → Frontend: change BASE_URL from http://localhost:4010 to real service URL
  → Smoke test: if spec was honored, things just work

  INTEGRATION TESTS WITH WIREMOCK:
  Service A (checkout) tests:
  → WireMock stubs for payment-service, inventory-service, notification-service
  → All failure scenarios covered
  → Fast (no network), deterministic (no flakiness), zero external cost
```

---

### 💻 Code Example

```java
// WireMock Spring Boot integration test
@WireMockTest
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class CheckoutServiceIntegrationTest {

    @Autowired
    private CheckoutService checkoutService;

    @Test
    void processPayment_success(WireMockRuntimeInfo wmRuntimeInfo) {
        stubFor(post(urlEqualTo("/api/payments"))
            .withRequestBody(matchingJsonPath("$.amount"))
            .willReturn(aResponse()
                .withStatus(201)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {"transactionId": "TXN-001", "status": "APPROVED"}
                """)
            )
        );

        PaymentResult result = checkoutService.checkout(new Cart(BigDecimal.valueOf(99.99)));

        assertThat(result.getStatus()).isEqualTo("APPROVED");
        verify(postRequestedFor(urlEqualTo("/api/payments"))
            .withRequestBody(matchingJsonPath("$.amount", equalTo("99.99"))));
    }

    @Test
    void processPayment_gatewayTimeout_triggersCircuitBreaker(WireMockRuntimeInfo wmRuntimeInfo) {
        stubFor(post(urlEqualTo("/api/payments"))
            .willReturn(aResponse()
                .withFixedDelay(5000) // 5s delay — triggers 3s timeout
            )
        );

        assertThatThrownBy(() -> checkoutService.checkout(new Cart(BigDecimal.valueOf(99.99))))
            .isInstanceOf(PaymentTimeoutException.class);
    }

    @Test
    void processPayment_serviceDown_returnsFallback(WireMockRuntimeInfo wmRuntimeInfo) {
        stubFor(post(urlEqualTo("/api/payments"))
            .willReturn(aResponse()
                .withStatus(503)
                .withBody("""{"error": "Service Unavailable"}""")
            )
        );

        PaymentResult result = checkoutService.checkout(new Cart(BigDecimal.valueOf(99.99)));
        assertThat(result.getStatus()).isEqualTo("PENDING"); // fallback behavior
    }
}
```

---

### ⚖️ Comparison Table

| Tool           | Use Case                       | Language         | OpenAPI Support | State Management |
| -------------- | ------------------------------ | ---------------- | --------------- | ---------------- |
| **WireMock**   | Java service integration tests | Java/JVM         | Partial         | Scenarios        |
| **Prism**      | Mock from OpenAPI spec         | Any (standalone) | Native          | Stateless        |
| **Mockoon**    | UI-based desktop mock          | Any (standalone) | Import          | Templating       |
| **MockServer** | Java/Node stubbing             | Java/Node        | Yes             | Expectations     |
| **Pact Mock**  | Consumer contract testing      | Multi-lang       | No (pact-based) | Per-pact         |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                             |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Mocks and stubs are the same thing               | Stubs return canned responses; mocks also verify behavior (e.g., "was this called?"). WireMock does both depending on usage         |
| Mocking means testing less                       | Mocking enables testing MORE scenarios (especially failures) that real services can't simulate reliably                             |
| WireMock replaces integration tests              | It enables better unit/integration isolation; full E2E tests against real services should still exist at higher test pyramid layers |
| Mock responses should be exact production copies | Use representative data, not production data. Sensitive PII must never appear in test/mock data                                     |

---

### 🚨 Failure Modes & Diagnosis

**Stub Not Matching — Returns 404 from WireMock**

Symptom:
Test fails with 404 from WireMock. Stub was defined. Request looks correct.

Root Cause (most common):
URL path mismatch (trailing slash, different casing, query param included in urlEqualTo).

Diagnostic:

```java
// WireMock Admin API — see all received requests:
List<LoggedRequest> requests = WireMock.getAllServeEvents().stream()
    .map(ServeEvent::getRequest)
    .collect(toList());
// Print what WireMock actually received:
requests.forEach(r -> System.out.println("URL: " + r.getUrl() + " Method: " + r.getMethod()));

// Also check WireMock's near-misses (requests that almost matched a stub):
List<NearMiss> nearMisses = WireMock.findNearMissesForAllUnmatchedRequests();
// Output explains: "expected /api/payments but received /api/payments/"
// (trailing slash mismatch)

// Fix:
// urlEqualTo("/api/payments") ← exact
// vs
// urlPathEqualTo("/api/payments") ← ignores query params
// vs
// urlMatching("/api/payments/?") ← regex: optional trailing slash
```

---

### 🔗 Related Keywords

- `API Contract Testing` — Pact consumer tests use a mock server internally
- `OpenAPI/Swagger` — Prism generates mock servers directly from OpenAPI specs
- `Stubbing` — related concept; WireMock stubs = HTTP service stubs
- `Test Pyramid` — mocking enables fast, isolated service-boundary tests

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Fake HTTP server returning predefined     │
│              │ responses for isolated testing/dev       │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOL    │ WireMock: @WireMockTest + stubFor(...)    │
├──────────────┼───────────────────────────────────────────┤
│ FROM SPEC    │ Prism: prism mock openapi.yaml            │
│              │        → localhost:4010                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY USES     │ Frontend parallel dev, failure injection, │
│              │ E2E isolation, contract test consumer stub│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Control every API response in tests"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Contract Testing → OpenAPI/Swagger   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A team argues that WireMock stubs are "lying to us" — the stub says the payments
API returns 201 with a specific body, but the real payments API might return 207 or a
different body structure. They want to use real services in all tests. You agree with
their concern but believe mocks are still the right tool. How do you reconcile the
"mocks lie" problem? What mechanism (hint: contract testing) bridges the gap, and what
does a complete trust model for API mocking look like in a CI/CD pipeline?
