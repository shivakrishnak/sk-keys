---
version: 2
layout: default
title: "Karate Framework (API Testing)"
parent: "Testing"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /testing/karate-framework/
id: TST-052
category: Testing
difficulty: ★★★
depends_on: API Contract Testing, Testing, HTTP & APIs
used_by: CI-CD, Testing
related: REST Assured, Postman, API Contract Testing
tags:
  - testing
  - api
  - advanced
---

# TST-052 - Karate Framework (API Testing)

⚡ **TL;DR -** A DSL-first API testing framework where feature files replace Java code, enabling non-developers to write, read, and run HTTP assertions.

| Field      | Value                                         |
|------------|-----------------------------------------------|
| Depends on | API Contract Testing, Testing, HTTP & APIs    |
| Used by    | CI-CD, Testing                                |
| Related    | REST Assured, Postman, API Contract Testing   |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** API tests require Java (or Python/JS) boilerplate: HTTP client setup, request building, response parsing, JSON path extraction, assertion chaining. Business analysts define the expected behaviour; engineers translate it into code. The translation gap introduces drift, and only engineers can maintain the tests.

**THE BREAKING POINT:** A microservices platform has 30 APIs. Every integration test suite is a separate Java project with HTTP client dependencies, response deserialisers, and bespoke assertion utilities. Running them in parallel requires custom thread management. The maintenance cost rivals the application code itself.

**THE INVENTION MOMENT:** Karate (by Peter Thomas, 2017) unified HTTP client, assertion engine, mock server, and performance test runner into a single Gherkin-compatible DSL. A feature file *is* the test - no step-definition glue code required, no Java compilation step between writing and running.

---

### 📘 Textbook Definition

**Karate** is an open-source API test automation framework built on top of Cucumber-JVM that replaces step-definition glue code with a built-in DSL. Feature files written in Gherkin-extended syntax describe HTTP calls, JSON/XML assertions, chained scenario variables, and mock server behaviours directly. The runtime provides parallel execution, a built-in `karate.mock()` contract mock server, JSON/JsonPath/XML/XPath assertions, and a Gatling adapter for performance mode - all without writing a single Java class for the test logic.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Write HTTP tests as plain-text feature files - no Java glue code needed.

> Karate is like a universal remote that controls the TV (HTTP client), reads the on-screen guide (JSON assertions), and also simulates the broadcast signal (mock server) - all from one device.

**One insight:** By embedding the HTTP client, assertion engine, and mock server into the DSL runtime, Karate eliminates the "plumbing layer" that makes API test projects balloon in size.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Tests should be readable by the person who defined the requirement, not only the person who implemented it.
2. An API test is: configure → send request → assert response. Everything else is ceremony.
3. Parallelism is a runtime concern, not a test-design concern.

**DERIVED DESIGN:** A DSL runtime absorbs HTTP client, assertion, and data management responsibilities. Feature files remain pure declarations. The runner handles parallelism behind a simple `parallel(5)` option. Mock servers share the same DSL, so contract mocks use identical syntax to integration tests.

**THE TRADE-OFFS:**
- **Gain:** Drastically reduced boilerplate; non-engineers can contribute tests; one framework covers integration, contract, and performance testing.
- **Cost:** Karate's DSL is non-standard - expertise does not transfer to other frameworks; deep custom logic still requires embedded JavaScript or Java interop (`karate.call()`), adding a cognitive seam.

---

### 🧪 Thought Experiment

**SETUP:** You need to test a `POST /orders` endpoint: authenticate, send a JSON body, assert the response status and a nested JSON field, then use the returned `orderId` in a second `GET /orders/{id}` call.

**WHAT HAPPENS WITHOUT Karate:** You write a Java test class: instantiate `RestTemplate` or `RestAssured`, build auth headers, serialise the request body, parse the response, extract `orderId` via Jackson/JSONPath, store it in a field, and wire it into the next request. The test is ~40 lines; half is boilerplate.

**WHAT HAPPENS WITH Karate:**
```gherkin
Given url baseUrl + '/orders'
And header Authorization = 'Bearer ' + token
And request { item: 'book', qty: 2 }
When method POST
Then status 201
And match response.orderId == '#notnull'
* def orderId = response.orderId

Given url baseUrl + '/orders/' + orderId
When method GET
Then status 200
And match response.status == 'PENDING'
```
That is the entire test - 10 lines, no Java class, directly readable by the business analyst.

**THE INSIGHT:** The DSL collapses the distinction between "test script" and "test documentation". The feature file is both.

---

### 🧠 Mental Model / Analogy

> Karate is like a smart contract template for APIs. You fill in the blanks (URL, body, expected fields) and the runtime enforces the agreement - the same way a legal template handles the boilerplate while you focus on the deal terms.

- **Template clauses** → built-in Karate keywords (`Given`, `When`, `Then`, `match`, `request`)
- **Deal terms** → your specific URLs, JSON bodies, and assertions
- **Enforcement engine** → Karate runtime (HTTP client + JsonPath + assertion engine)
- **Witness / auditor** → parallel HTML report generated automatically

Where this analogy breaks down: legal templates are static; Karate feature files can contain dynamic JavaScript expressions and conditionals, making them Turing-complete when needed.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Karate lets you describe "call this API, send this data, check this response" in plain English-like text files. You don't need to know Java to write or read the tests.

**Level 2 - How to use it (junior developer):**
Create a `.feature` file under `src/test/resources`. Use `Given url`, `And request`, `When method POST`, `Then status 201`, `And match response.field == 'value'`. Run with a JUnit 5 runner class or `mvn test`. Use `* def var = response.field` to pass data between steps.

**Level 3 - How it works (mid-level engineer):**
Karate's runner parses feature files using a Cucumber parser but substitutes its own step executor that maps all DSL keywords to internal `ScenarioEngine` actions. The HTTP engine wraps Apache HttpClient; JSON operations use a forked JsonPath library with Karate-specific match semantics (`#notnull`, `#regex`, `#[]` array matchers). The `karate.mock()` call spawns a Netty-based HTTP mock server on a dynamic port, configurable via the same DSL. Parallel execution spawns `ScenarioRuntime` instances in a thread pool managed by `KarateRunner`.

**Level 4 - Why it was designed this way (senior/staff):**
Karate deliberately avoided the Cucumber step-definition model (where Gherkin sentences map to annotated Java methods) to eliminate the "two-file problem": every feature line requires a corresponding Java method, creating a maintenance coupling. By making the DSL self-contained, Karate trades the extensibility of arbitrary Java step definitions for the productivity of zero-glue tests. The embedded JavaScript engine (GraalVM or Nashorn depending on version) provides an escape hatch for complex logic without requiring a full Java compilation cycle - a deliberate balance between power and accessibility.

---

### ⚙️ How It Works (Mechanism)

```
Feature File (.feature)
  │
  ▼
KarateRunner (JUnit 5 / CLI)
  │  parse Gherkin + Karate DSL
  ▼
ScenarioEngine (per thread)
  ├── HTTP Engine (Apache HttpClient)
  │     request build → send → response capture
  ├── Assertion Engine
  │     match / contains / #schema matchers
  ├── JS Engine (GraalVM JS)
  │     karate.call() / embedded expressions
  └── Mock Server (Netty, optional)
        karate.mock('mock.feature', port)

Parallel Execution:
  ThreadPool → N × ScenarioRuntime
  └── Results merged → HTML + JSON report
```

**Key built-in match semantics:**

| Marker        | Meaning                              |
|---------------|--------------------------------------|
| `#notnull`    | Value is present and not null        |
| `#string`     | Value is a JSON string               |
| `#number`     | Value is a number                    |
| `#[]`         | Value is an array                    |
| `#(expr)`     | Value matches embedded expression    |
| `#regex ...`  | Value matches regex pattern          |

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
 Developer writes orders.feature
 ┌──────────────────────────────────────┐
 │  Scenario: Create order              │
 │    Given url baseUrl + '/orders'     │
 │    And request { item: 'book' }      │
 │    When method POST          ← YOU ARE HERE
 │    Then status 201                   │
 │    And match response.id == '#uuid'  │
 └────────────────┬─────────────────────┘
                  │ KarateRunner.parallel(4)
          ┌───────┴──────────┐
    Thread 1            Thread 2
    Scenario A          Scenario B
    HTTP POST →         HTTP GET  →
    ← 201 assert        ← 200 assert
          └───────┬──────────┘
                  ▼
         Surefire + HTML Report
         karate-summary.html
```

**FAILURE PATH:** A `match` assertion fails → `ScenarioEngine` captures the actual vs. expected diff, logs the full HTTP request/response, marks the scenario `FAILED`, and continues remaining scenarios. Other threads are unaffected.

**WHAT CHANGES AT SCALE:** Enable Gatling performance mode via `KarateGatlingPlugin`. The same `.feature` file drives load test simulation - Karate replays scenarios at configurable RPS using Gatling's actor model, producing Gatling HTML reports alongside functional reports.

---

### 💻 Code Example

**BAD - Java REST Assured boilerplate for the same test:**
```java
@Test
void createOrder() {
    String token = getAuthToken(); // 10-line helper
    String body = "{\"item\":\"book\",\"qty\":2}";
    Response resp = given()
        .header("Authorization", "Bearer " + token)
        .contentType("application/json")
        .body(body)
        .when().post("/orders")
        .then().statusCode(201)
        .extract().response();
    String orderId = resp.jsonPath().getString("orderId");
    assertNotNull(orderId);
    // second call wiring omitted - another 10 lines
}
```

**GOOD - Karate feature file:**
```gherkin
Feature: Order API

Background:
  * url baseUrl
  * def token = karate.callSingle('auth.feature').token

Scenario: Create and retrieve order
  Given path '/orders'
  And header Authorization = 'Bearer ' + token
  And request { item: 'book', qty: 2 }
  When method POST
  Then status 201
  And match response == { orderId: '#uuid', status: 'PENDING' }
  * def orderId = response.orderId

  Given path '/orders/' + orderId
  When method GET
  Then status 200
  And match response.status == 'PENDING'
```

**GOOD - karate.mock() contract mock server:**
```gherkin
# mock.feature (server-side definition)
Scenario: pathMatches('/orders') && methodIs('post')
  * def response = { orderId: '123', status: 'PENDING' }
  * def responseStatus = 201

# consumer.feature (test using the mock)
* def mock = karate.mock('mock.feature', 8081)
* url 'http://localhost:8081'
Given path '/orders'
And request { item: 'book' }
When method POST
Then status 201
* mock.stop()
```

---

### ⚖️ Comparison Table

| Feature              | Karate         | REST Assured       | Postman/Newman  |
|----------------------|:--------------:|:------------------:|:---------------:|
| Language required    | None (DSL)     | Java               | None (GUI/JSON) |
| Built-in mock server | Yes            | No (WireMock sep.) | No              |
| Parallel execution   | Built-in       | TestNG/JUnit5      | CLI `--workers` |
| Performance mode     | Gatling adapter| No                 | No              |
| CI integration       | Maven/Gradle   | Maven/Gradle       | Newman CLI      |
| JSON schema match    | Built-in `#`   | External lib       | Limited         |
| Non-engineer access  | High           | Low                | High            |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Karate is just Cucumber for APIs" | Karate uses the Gherkin parser but eliminates step definitions entirely - the runner is fundamentally different. |
| "You can't use Karate for complex logic" | Embedded JavaScript and `karate.call()` Java interop handle arbitrarily complex scenarios. |
| "Karate replaces performance testing tools" | The Gatling adapter provides basic load testing; complex load profiles still benefit from dedicated Gatling scenarios. |
| "Feature files must follow Given/When/Then" | `*` prefix is valid for any step; Karate ignores the keyword semantically - it's cosmetic Gherkin. |
| "karate.mock() requires a separate server process" | It spawns an in-process Netty server on a dynamic port, no external process needed. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - `karate.callSingle()` not thread-safe in parallel runs**

**Symptom:** Intermittent NullPointerException or stale token errors when running scenarios in parallel.
**Root Cause:** `karate.callSingle()` caches the result globally per JVM; if the first call has not returned before a second thread reads the cache, the second thread receives a partial result.
**Diagnostic:**
```bash
# Enable Karate debug logging
mvn test -Dkarate.options="--tags @smoke" \
  -Dlogback.configurationFile=logback-test.xml \
  2>&1 | grep "callSingle"
```
**Fix:**
```gherkin
# BAD - called per-scenario in parallel
* def token = karate.call('auth.feature').token

# GOOD - callSingle in karate-config.js (runs once per JVM)
# karate-config.js:
function fn() {
  var token = karate.callSingle('auth.feature').token;
  return { token: token, baseUrl: 'http://api' };
}
```
**Prevention:** Move all shared auth/setup into `karate-config.js` using `karate.callSingle()`.

---

**Mode 2 - JSON match fails with `#notnull` on numeric zero**

**Symptom:** `match response.count == '#notnull'` fails when `count` is `0`.
**Root Cause:** Karate's `#notnull` considers `0` as falsy in certain match contexts in older versions; also confused with JavaScript truthiness.
**Diagnostic:**
```gherkin
* print 'count value:', response.count
* match response.count == '#present'
```
**Fix:**
```gherkin
# BAD - ambiguous for numeric 0
And match response.count == '#notnull'

# GOOD - explicit type check
And match response.count == '#number'
```
**Prevention:** Use `#present` (field exists) and `#number` / `#string` for type assertions rather than `#notnull` for non-nullable primitives.

---

**Mode 3 - Parallel report shows 0 tests when using wrong runner class**

**Symptom:** Maven Surefire reports `Tests run: 0` despite feature files being present.
**Root Cause:** JUnit 5 runner class not annotated with `@Karate.Test`, or feature file path not on the classpath (placed under `src/main/resources` instead of `src/test/resources`).
**Diagnostic:**
```bash
mvn test -Dsurefire.useFile=false \
  2>&1 | grep -E "Tests run|No tests"
find src -name "*.feature" | head -5
```
**Fix:**
```java
// BAD - plain JUnit 5 test, Karate not invoked
@Test void run() { Karate.run("classpath:features"); }

// GOOD - use @Karate.Test
@Karate.Test
Karate testAll() {
    return Karate.run("classpath:features")
                 .relativeTo(getClass());
}
```
**Prevention:** Use the Karate Maven archetype to scaffold runner classes; add a CI smoke-test that fails if `Tests run: 0`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** HTTP & APIs, Testing, API Contract Testing

**Builds On This (learn these next):** CI-CD, REST Assured, Postman

**Alternatives / Comparisons:** REST Assured, Postman/Newman, API Contract Testing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────┐
│ WHAT IT IS    │ DSL-first API test framework │
│ PROBLEM       │ Java boilerplate for HTTP    │
│ KEY INSIGHT   │ Feature file IS the test     │
│ USE WHEN      │ REST/SOAP APIs, BAs writing  │
│ AVOID WHEN    │ Complex stateful UI flows    │
│ TRADE-OFF     │ Productivity vs. portability │
│ ONE-LINER     │ match response == '#schema'  │
│ NEXT EXPLORE  │ karate.mock(), Gatling mode  │
└──────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** When Karate's `karate.mock()` mock server and a real downstream service both exist on localhost during a CI run, how would you ensure the consumer test always binds to the mock and never accidentally hits the real service?
2. **(Scale)** Karate's Gatling performance adapter replays the same feature file under load. What categories of real-world performance problems would this approach *miss* compared to a proper Gatling simulation, and why?
3. **(Design Trade-off)** Karate eliminates step-definition glue code for speed, but Cucumber retains it for reusability. Describe a project profile where the Cucumber model's higher setup cost is worth paying over Karate's zero-glue approach.
