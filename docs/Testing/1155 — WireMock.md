---
layout: default
title: "WireMock"
parent: "Testing"
nav_order: 1155
permalink: /testing/wiremock/
number: "1155"
category: Testing
difficulty: ★★★
depends_on: Integration Test, HTTP and APIs, Stubbing
used_by: Java Developers, API Integration Testers
related: Stubbing, Testcontainers, Mockito, Contract Test, HTTP Client Testing
tags:
  - testing
  - wiremock
  - http-stubbing
  - integration-testing
---

# 1155 — WireMock

⚡ TL;DR — WireMock is a programmable HTTP server used in tests to simulate external APIs and services — enabling integration tests that test your HTTP client code without calling real external services.

| #1155 | Category: Testing | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Integration Test, HTTP and APIs, Stubbing | |
| **Used by:** | Java Developers, API Integration Testers | |
| **Related:** | Stubbing, Testcontainers, Mockito, Contract Test, HTTP Client Testing | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
`PaymentService.charge()` makes an HTTP call to Stripe. To test your service, you need: Stripe API keys, internet access, test card numbers, Stripe's sandbox environment to be up. In CI, these calls are slow (500ms+), may be rate-limited, can fail due to network issues, and require secrets management. With Mockito, you can mock the HTTP client interface — but you're not testing your HTTP serialization, your request headers, your error handling code for HTTP 429 rate limits, or your retry logic.

WireMock fills the gap: it's a real HTTP server that runs in your test, returns exactly what you tell it to, and records all requests — so you can verify your service sends the correct HTTP requests.

### 📘 Textbook Definition

**WireMock** is a mock HTTP server library for Java (and available standalone) that: (1) **stubs HTTP responses** — program specific URLs to return specific status codes, headers, and response bodies; (2) **records requests** — capture all incoming requests for later verification; (3) **verifies requests** — assert that specific HTTP requests were made; (4) **simulates fault conditions** — inject delays, connection resets, chunked encoding errors. WireMock can run embedded in JUnit tests or as a standalone server for manual testing.

### ⏱️ Understand It in 30 Seconds

**One line:**
WireMock = fake HTTP server in your test — program it like a mock, but for real HTTP calls.

**One analogy:**
> WireMock is a **traffic roundabout** redirecting your service's outbound HTTP calls: instead of reaching Stripe's servers, the call is intercepted by WireMock, which returns a scripted response. Your service code doesn't know the difference — it sent a real HTTP request and got a real HTTP response.

### 🔩 First Principles Explanation

WIREMOCK VS MOCKITO — WHAT EACH TESTS:
```
Mockito mock of StripeClient.charge():
  Tests: does your service call charge() with the right arguments?
  Does NOT test: how the HttpClient builds the request URL
                 are the Authorization headers correct?
                 does your code handle HTTP 429 (rate limit) correctly?
                 does retry-with-backoff work?

WireMock stub of POST /v1/charges:
  Tests ALL of the above:
    → HTTP method + URL: did your code POST to /v1/charges?
    → Headers: is "Authorization: Bearer sk_test_..." set?
    → Body: is the amount encoded as form data (amount=5000¤cy=usd)?
    → Error handling: what happens when WireMock returns 429?
    → Retry: does your client retry after 429?
```

WIREMOCK JUNIT 5 SETUP:
```java
@SpringBootTest
@WireMockTest  // starts WireMock server on random port
class StripePaymentServiceTest {
    
    @Test
    void charge_successfulPayment_returnsTransactionId(WireMockRuntimeInfo wm) {
        // STUB: program WireMock response
        stubFor(post("/v1/charges")
            .withHeader("Authorization", matching("Bearer sk_.*"))
            .withRequestBody(containing("amount=5000"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBody("""
                    {"id": "ch_123", "status": "succeeded", "amount": 5000}
                """)));
        
        // ACT: call service that makes real HTTP to WireMock server
        PaymentResult result = stripeService.charge("tok_test", 50.00, "USD");
        
        // ASSERT result
        assertThat(result.getTransactionId()).isEqualTo("ch_123");
        
        // VERIFY request was made correctly
        verify(postRequestedFor(urlEqualTo("/v1/charges"))
            .withRequestBody(containing("amount=5000"))
            .withRequestBody(containing("currency=usd")));
    }
    
    @Test
    void charge_rateLimited_retriesAndSucceeds(WireMockRuntimeInfo wm) {
        stubFor(post("/v1/charges")
            .inScenario("rate-limit-then-success")
            .whenScenarioStateIs(STARTED)
            .willReturn(aResponse().withStatus(429).withHeader("Retry-After", "1"))
            .willSetStateTo("second-attempt"));
        
        stubFor(post("/v1/charges")
            .inScenario("rate-limit-then-success")
            .whenScenarioStateIs("second-attempt")
            .willReturn(aResponse().withStatus(200)
                .withBody("{\"id\":\"ch_456\",\"status\":\"succeeded\"}")));
        
        // Verify: service retries after 429 and succeeds on second attempt
        PaymentResult result = stripeService.charge("tok_test", 50.00, "USD");
        assertThat(result.getTransactionId()).isEqualTo("ch_456");
        verify(2, postRequestedFor(urlEqualTo("/v1/charges")));  // called TWICE
    }
}
```

FAULT INJECTION WITH WIREMOCK:
```java
// Simulate network failure
stubFor(post("/v1/charges")
    .willReturn(aResponse().withFault(Fault.CONNECTION_RESET_BY_PEER)));

// Simulate slow response (timeout test)
stubFor(post("/v1/charges")
    .willReturn(aResponse().withFixedDelay(5000)));  // 5 second delay

// Simulate chunked response corruption
stubFor(get("/api/data")
    .willReturn(aResponse().withFault(Fault.RANDOM_DATA_THEN_CLOSE)));
```

### 🧪 Thought Experiment

FINDING THE HEADER BUG WITH WIREMOCK:
```
Without WireMock: Mockito mocks StripeClient.charge(token, amount)
  Unit tests pass: charge() is called with correct arguments
  
Deploy to staging: payments fail
  Debug: Stripe returns 401 Unauthorized
  Root cause: Authorization header is "Bearer " + apiKey
    but apiKey was accidentally double-encoded → "Bearer%20sk_test_..."
    Stripe rejects the malformed header
    
This bug is INVISIBLE to Mockito (which mocks the Java method call)
WireMock would have caught it:
  verify(...).withHeader("Authorization", equalTo("Bearer sk_test_123"))
  → FAILS with "found: Authorization: Bearer%20sk_test_123"
  → Bug found in test, not in staging
```

### 🧠 Mental Model / Analogy

> WireMock is a **flight simulator for HTTP clients**: the pilot (your service code) sends real control inputs (HTTP requests), the simulator (WireMock) responds with realistic feedback (HTTP responses), including failures (turbulence = 500 errors, out of fuel = 429 rate limits). The pilot learns and adapts (retry logic tested) without any real aircraft (external API) being involved.

### 📶 Gradual Depth — Four Levels

**Level 1:** WireMock is a fake HTTP server in your test. You tell it "when POST /charges is called, return this JSON." Your code makes a real HTTP call to WireMock, gets the scripted response.

**Level 2:** Add `wiremock-spring-boot` dependency. Annotate with `@WireMockTest`. Use `stubFor(get("/api/path").willReturn(aResponse().withStatus(200).withBody("{...}")))`. Verify with `verify(getRequestedFor(urlEqualTo("/api/path")))`. Configure your Spring property for the external API URL to point to WireMock's URL (`wm.getRuntimeInfo().getHttpBaseUrl()`).

**Level 3:** Scenarios (stateful stubs): use `inScenario()` / `whenScenarioStateIs()` / `willSetStateTo()` to model stateful sequences (first call returns one thing, subsequent calls return another). Request templating: return dynamic responses based on request content (Handlebars templates). Recording: WireMock can record real API calls to generate stubs automatically (`record/playback` mode — hit real Stripe once, save the response, use saved response in all future tests).

**Level 4:** WireMock in microservices: each service has its own WireMock stubs for its downstream dependencies. This creates a risk: if Stripe changes their API, WireMock stubs stay the same — tests pass but production fails. Solution: Consumer-Driven Contract Testing (Pact) combined with WireMock — stubs are generated from Pact contracts, ensuring they match the real API. WireMock Cloud: SaaS version of WireMock for non-Java teams. WireMock Standalone: run as a Docker container for manual testing / cross-service integration environments.

### 💻 Code Example

```java
// Complete WireMock setup with Spring Boot
@SpringBootTest(webEnvironment = RANDOM_PORT)
@WireMockTest
class WeatherServiceTest {
    
    @Autowired
    private WeatherService weatherService;
    
    @DynamicPropertySource
    static void configure(DynamicPropertyRegistry registry) {
        // Point service to WireMock server
        registry.add("weather.api.url",
            () -> "http://localhost:" + wireMockPort);
    }
    
    @Test
    void getCurrentWeather_returnsTemperature(@WireMockRuntimeInfo wm) {
        stubFor(get(urlPathEqualTo("/weather/current"))
            .withQueryParam("city", equalTo("London"))
            .withHeader("X-API-Key", equalTo("test-key"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBodyFile("weather-london.json")));  // file in __files/
        
        WeatherData result = weatherService.getCurrent("London");
        
        assertThat(result.getTemperature()).isEqualTo(20.5);
        assertThat(result.getCondition()).isEqualTo("Cloudy");
    }
    
    @Test
    void getCurrentWeather_serviceDown_throwsWeatherException() {
        stubFor(get(urlPathEqualTo("/weather/current"))
            .willReturn(aResponse().withStatus(503)));
        
        assertThatThrownBy(() -> weatherService.getCurrent("London"))
            .isInstanceOf(WeatherServiceException.class)
            .hasMessage("Weather service unavailable");
    }
}
```

### ⚖️ Comparison Table

| | Mockito Mock | WireMock |
|---|---|---|
| Level | Java interface | HTTP transport |
| Tests HTTP headers/URL | ✗ | ✓ |
| Tests serialization | ✗ | ✓ |
| Tests retry/timeout logic | ✗ | ✓ |
| Speed | Microseconds | Milliseconds |
| Use case | Internal dependencies | External HTTP APIs |

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "WireMock replaces Mockito" | They operate at different layers; use both: Mockito for domain logic, WireMock for HTTP boundaries |
| "WireMock stubs are always up-to-date" | Stubs can drift from real APIs; use contract tests (Pact) to keep stubs synchronized |
| "WireMock requires a running server" | WireMock can run embedded in JUnit — no separate server needed |

### 🚨 Failure Modes & Diagnosis

**1. Service Uses Wrong URL in Tests → WireMock Not Called**

Cause: `@DynamicPropertySource` doesn't override the URL; service still calls real API.
Fix: Verify `spring.datasource.url` / `api.url` property is set to WireMock URL. Log the URL on application startup.

**2. WireMock Stubs Drift From Real API → False Confidence**

Cause: Stripe updated their API response format; WireMock stubs still return old format.
Fix: Use Pact consumer-driven contract testing to generate stubs, or run a periodic "stub freshness check" against the real API in a separate job.

### 🔗 Related Keywords

- **Prerequisites:** Integration Test, HTTP and APIs
- **Related:** Testcontainers, Pact, Contract Test, MockMvc, HttpClient

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Programmable fake HTTP server for tests  │
├──────────────┼───────────────────────────────────────────┤
│ ANNOTATIONS  │ @WireMockTest (Spring Boot)              │
│              │ stubFor(...), verify(...)                │
├──────────────┼───────────────────────────────────────────┤
│ UNIQUE VALUE │ Tests HTTP headers, URL, serialization,  │
│              │ retry logic, error handling              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Mockito for HTTP: stub responses,       │
│              │  verify requests"                        │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** WireMock's record-playback mode allows recording real API calls to generate stubs automatically. The workflow: (1) point your service at WireMock in proxy mode (WireMock forwards requests to real API, records responses); (2) run your service against the real API once; (3) WireMock saves all requests/responses as stub files; (4) future tests use saved stubs. Describe: (a) the security risk of recording (API keys, PII in responses get saved to files — how to sanitize?); (b) when recorded stubs go stale (real API changes); (c) how to combine record-playback with Pact consumer tests to maintain stub freshness; (d) the "contract test as stub generator" pattern.

**Q2.** WireMock vs. MockMvc: MockMvc tests your Spring MVC controllers as an HTTP server (testing your own app as the server). WireMock stubs external HTTP servers that your app calls as a client. Describe a full integration test scenario for an Order service that: (1) accepts a POST /orders request (tested via MockMvc), (2) calls PaymentService HTTP API (stubbed via WireMock), (3) publishes to Kafka (Testcontainers), (4) saves to PostgreSQL (Testcontainers). Map each component to the testing tool, describe the request flow through all four components, and identify what bugs each tool catches that the others miss.
