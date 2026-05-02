---
layout: default
title: "Postman / REST Assured"
parent: "Testing"
nav_order: 1171
permalink: /testing/postman-rest-assured/
number: "1171"
category: Testing
difficulty: ★★☆
depends_on: API Testing, HTTP & APIs, REST
used_by: Developers, QA Engineers
related: API Testing, REST Assured, MockMvc, Integration Test, OpenAPI
tags:
  - testing
  - api-testing
  - postman
  - rest-assured
  - tools
---

# 1171 — Postman / REST Assured

⚡ TL;DR — Postman is a GUI tool for manual and automated API testing via collections; REST Assured is a Java DSL for fluent HTTP API assertions in code — both are the primary tools for API test automation at different levels of the stack.

| #1171           | Category: Testing                                             | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | API Testing, HTTP & APIs, REST                                |                 |
| **Used by:**    | Developers, QA Engineers                                      |                 |
| **Related:**    | API Testing, REST Assured, MockMvc, Integration Test, OpenAPI |                 |

---

### 🔥 The Problem This Solves

MANUAL API TESTING DOESN'T SCALE:
Manually testing APIs with curl or a GUI tool after every deployment is error-prone and time-consuming. These tools exist to: (1) make ad-hoc API exploration fast (Postman), (2) turn manual tests into automated, repeatable collections (Postman Newman), and (3) write API tests as first-class code with fluent assertions in the same codebase as the application (REST Assured).

---

### 📘 Textbook Definition

**Postman** is a GUI-based HTTP client and API testing platform. It allows sending HTTP requests, organizing them into **Collections** (groups of related requests), adding **test scripts** (JavaScript) to validate responses, and running collections via **Newman** (CLI) in CI pipelines. **REST Assured** is a Java DSL (domain-specific language) library for writing HTTP API tests as code, integrated with JUnit/TestNG. It provides a fluent `given().when().then()` syntax for constructing requests, sending them, and asserting responses — natively integrated into the Java test ecosystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Postman = GUI-first API testing (great for exploration + collections); REST Assured = code-first API testing (integrates with Java test suite).

**One analogy:**

> Postman is the **workshop for building and testing API requests** — you tinker interactively until the request is right, then save it as a recipe. REST Assured is the **factory floor** — you codify the recipes as automated tests that run at scale, every build, without a human.

---

### 🔩 First Principles Explanation

POSTMAN:

{% raw %}
```
COLLECTION STRUCTURE:
  Collection: "Order Service API"
  └── Folder: "Orders"
      ├── POST Create Order
      ├── GET Get Order by ID
      ├── PATCH Update Order Status
      └── DELETE Cancel Order
  └── Folder: "Users"
      ├── POST Register
      └── POST Login

TEST SCRIPTS (JavaScript, runs in Postman sandbox):
  pm.test("Status code is 201", function() {
    pm.response.to.have.status(201);
  });

  pm.test("Response has orderId", function() {
    const json = pm.response.json();
    pm.expect(json.orderId).to.not.be.undefined;
  });

  // Extract value for subsequent request
  pm.environment.set("orderId", pm.response.json().orderId);

ENVIRONMENT VARIABLES:
  {{baseUrl}}    = https://api.staging.myapp.com
  {{authToken}}  = eyJhbGci...

  Different environments: local, staging, production
  Same collection, different base URLs

NEWMAN (CLI — CI pipeline):
  npm install -g newman
  newman run "Order_Service.postman_collection.json" \
    --environment staging.postman_environment.json \
    --reporters cli,junit \
    --reporter-junit-export results.xml
```
{% endraw %}

REST ASSURED:

```java
// Setup (global)
@BeforeAll
static void setup() {
    RestAssured.baseURI = "http://localhost";
    RestAssured.port = 8080;
    RestAssured.basePath = "/api/v1";

    // Request logging for debugging
    RestAssured.enableLoggingOfRequestAndResponseIfValidationFails();
}

// Test
@Test
void createOrder_validRequest_returns201() {
    String orderId =
      given()
        .header("Authorization", "Bearer " + getTestToken())
        .contentType(ContentType.JSON)
        .body("""
            {
              "productId": "PROD-001",
              "quantity": 2,
              "shippingAddress": {
                "street": "123 Test St",
                "city": "Test City"
              }
            }
            """)
      .when()
        .post("/orders")
      .then()
        .log().ifValidationFails()
        .statusCode(201)
        .header("Content-Type", containsString("application/json"))
        .body("orderId", not(emptyString()))
        .body("status", equalTo("PENDING"))
        .body("items.size()", equalTo(1))
      .extract()
        .path("orderId");

    // Use extracted orderId in subsequent verification
    given()
      .header("Authorization", "Bearer " + getTestToken())
    .when()
      .get("/orders/{id}", orderId)
    .then()
      .statusCode(200)
      .body("status", equalTo("PENDING"));
}

// Reusable specs (DRY)
RequestSpecification authSpec = new RequestSpecBuilder()
    .setBaseUri("http://localhost:8080")
    .setBasePath("/api/v1")
    .addHeader("Authorization", "Bearer " + token)
    .setContentType(ContentType.JSON)
    .build();

ResponseSpecification successSpec = new ResponseSpecBuilder()
    .expectStatusCode(200)
    .expectHeader("Content-Type", containsString("application/json"))
    .build();
```

POSTMAN vs REST ASSURED — WHEN TO USE WHICH:

```
POSTMAN:
  ✓ API exploration and development
  ✓ QA team (non-Java developers)
  ✓ Manual API verification
  ✓ Sharing API tests across teams (collection export)
  ✓ When tests should run against any environment
  ✗ Version control integration is clunky (JSON files)
  ✗ Less expressive than code for complex scenarios

REST ASSURED:
  ✓ Java projects (integrates natively with Maven/Gradle)
  ✓ Complex test scenarios requiring Java logic
  ✓ Integrated with JUnit test suite
  ✓ Better version control (code, not JSON)
  ✓ Can use Java test utilities (Testcontainers, Spring Test)
  ✗ Requires Java knowledge
  ✗ Less visual than Postman
```

---

### 🧪 Thought Experiment

FROM POSTMAN TO CI:

```
QA Engineer workflow:
  1. Manually tests API in Postman
  2. Adds JavaScript test scripts to each request
  3. Organizes requests into a Collection
  4. Exports collection as JSON
  5. Commits JSON to git repository
  6. CI pipeline: newman run collection.json --environment ci.json
  7. Newman output: JUnit XML → CI picks up test results

Result: Manual Postman testing converted to automated CI pipeline
         with minimal developer overhead.

Limitation: Collection JSON in git → merge conflicts are painful
             → large teams often migrate to REST Assured as codebase matures
```

---

### 🧠 Mental Model / Analogy

> Postman is to REST Assured as **Excel is to Python**: Excel is great for ad-hoc analysis, easy to use, visual, shareable. Python is better for complex automation, version control, integration with other systems, and scalability. You might start with Excel (Postman) and migrate to Python (REST Assured) as your needs grow.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Postman: send requests visually, add test scripts, save as collection, export for CI. REST Assured: `given().when().then()` fluent Java API — matches natural language ("given these headers, when I call this endpoint, then expect this response").

**Level 2:** Postman environments for different deployment targets (local, staging, prod). Newman for CI. REST Assured: `RequestSpecBuilder` for reusable auth headers and base URL. `ResponseSpecBuilder` for reusable assertions. `extract().path()` to pull values from response for chained requests.

**Level 3:** Postman Collections 2.1 format supports pre-request scripts (set auth token before each request), post-response scripts (extract and store values), and collection-level variables. REST Assured filter support: custom filters for logging, request signing (HMAC), OAuth token refresh. JSON path and XML path assertions: `body("data.users.findAll { it.role == 'admin' }.size()", equalTo(2))`.

**Level 4:** Postman at enterprise: API Governance — shared team collections, centralized test environments, API versioning in collections, integration with CI/CD via Newman. REST Assured in a microservices context: shared test utility library containing `RequestSpecBuilder` configurations, authentication helpers, and common response validators — used across all service test suites for consistency. Integration with contract testing: REST Assured tests serve as the consumer-side tests in Pact, generating pact files from REST Assured requests.

---

### 💻 Code Example

```java
// REST Assured — complete integration test example
@SpringBootTest(webEnvironment = RANDOM_PORT)
class OrderApiTest {

    @LocalServerPort int port;
    private String authToken;

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
        authToken = obtainAuthToken("testuser@test.invalid", "password");
    }

    @Test
    void orderLifecycle() {
        // 1. Create order
        String orderId = given()
            .auth().oauth2(authToken)
            .contentType(ContentType.JSON)
            .body(Map.of("productId", "PROD-001", "quantity", 2))
        .when()
            .post("/api/v1/orders")
        .then()
            .statusCode(201)
            .body("status", equalTo("PENDING"))
        .extract()
            .path("orderId");

        // 2. Confirm order
        given()
            .auth().oauth2(authToken)
        .when()
            .post("/api/v1/orders/{id}/confirm", orderId)
        .then()
            .statusCode(200)
            .body("status", equalTo("CONFIRMED"));

        // 3. Verify final state
        given()
            .auth().oauth2(authToken)
        .when()
            .get("/api/v1/orders/{id}", orderId)
        .then()
            .statusCode(200)
            .body("orderId", equalTo(orderId))
            .body("status", equalTo("CONFIRMED"))
            .body("items[0].productId", equalTo("PROD-001"));
    }
}
```

```javascript
// Postman test script (JavaScript in "Tests" tab)
pm.test("Create order returns 201", () => {
  pm.response.to.have.status(201);
});

pm.test("Response has valid orderId", () => {
  const json = pm.response.json();
  pm.expect(json.orderId).to.match(/^ORD-[0-9]+$/);
});

pm.test("Status is PENDING", () => {
  pm.expect(pm.response.json().status).to.equal("PENDING");
});

// Store for subsequent requests
pm.environment.set("lastOrderId", pm.response.json().orderId);
```

---

### ⚖️ Comparison Table

|                 | Postman               | REST Assured       | MockMvc                   |
| --------------- | --------------------- | ------------------ | ------------------------- |
| Language        | JavaScript (scripts)  | Java               | Java                      |
| Real HTTP       | Yes                   | Yes                | No (in-process)           |
| Version control | JSON (difficult)      | Code (easy)        | Code (easy)               |
| CI integration  | Newman CLI            | JUnit/Maven        | JUnit/Maven               |
| Best for        | Exploration, QA teams | Java project tests | Fast unit-level API tests |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                               |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| "Postman is just a manual testing tool"  | Postman Collections + Newman provide full CI automation capability                                                    |
| "REST Assured replaces unit tests"       | REST Assured is for integration-level HTTP tests; unit tests (MockMvc or Mockito) are still needed for business logic |
| "REST Assured requires a running server" | Can use Spring Boot Test with `MockMvc` adapter for in-process testing with REST Assured's DSL                        |

---

### 🚨 Failure Modes & Diagnosis

**1. Postman Collection JSON Merge Conflicts**
Cause: Multiple developers editing the same collection — JSON format creates large diffs.
**Fix:** One collection owner per team; or migrate to REST Assured for code-controlled tests.

**2. REST Assured Tests Leaking State**
Cause: `RestAssured.baseURI` set statically; tests run in parallel with different base URIs.
**Fix:** Use `RequestSpecBuilder` per test class instead of static `RestAssured.` configuration.

---

### 🔗 Related Keywords

- **Prerequisites:** API Testing, HTTP & APIs, REST
- **Related:** Newman, Postman, REST Assured, MockMvc, OpenAPI, Pact, Integration Test

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ POSTMAN      │ GUI exploration → Collections →          │
│              │ Newman CLI → CI pipeline                 │
├──────────────┼───────────────────────────────────────────┤
│ REST ASSURED │ given().when().then() Java DSL           │
│              │ → integrated with JUnit, Maven           │
├──────────────┼───────────────────────────────────────────┤
│ CHOOSE       │ Postman: QA/exploration; REST Assured:   │
│              │ Java developer integration tests         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Postman for humans exploring APIs;      │
│              │  REST Assured for code automating them"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Postman's JavaScript test sandbox runs in a Node.js-like environment with access to `pm.*` APIs. Describe: (1) the `pm.sendRequest()` function — used within pre-request scripts to obtain an auth token and store it as an environment variable before each request runs, enabling fully automated OAuth 2.0 flows in Postman collections, (2) Postman's data-driven testing with CSV/JSON files — running the same request multiple times with different input values (like JUnit's `@ParameterizedTest`), (3) the Postman Flows visual builder (newer feature) for orchestrating complex API sequences with conditional logic, and (4) the corporate governance concern: Postman collections contain API credentials and base URLs — describe the security risk and how to mitigate it (never commit collections with real credentials; use environment variables; use Postman Vault for secrets).

**Q2.** REST Assured's JSON path is based on Groovy's GPath syntax. Describe: (1) the basic path syntax — `body("user.address.city", equalTo("London"))`, `body("items[0].price", greaterThan(9.99f))`, `body("items.size()", equalTo(3))`, (2) advanced GPath — `body("items.findAll { it.status == 'ACTIVE' }.size()", equalTo(2))` (filter a list), `body("items.collect { it.price }.sum()", equalTo(29.97f))` (aggregate), (3) why these Groovy closures work in a Java library (REST Assured delegates JSON path evaluation to the Groovy runtime embedded as a dependency), (4) the XML path alternative for SOAP/XML APIs using Hamcrest matchers, and (5) the `extract().as(MyClass.class)` pattern — deserializing the response body directly to a Java POJO using Jackson for more expressive assertions with `assertThat(order.getStatus()).isEqualTo(PENDING)`.
