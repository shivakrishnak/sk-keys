---
layout: default
title: "API Testing"
parent: "Testing"
nav_order: 1170
permalink: /testing/api-testing/
number: "1170"
category: Testing
difficulty: ★★☆
depends_on: HTTP & APIs, Integration Test, REST
used_by: Developers, QA Engineers
related: Integration Test, Contract Test, Postman, REST Assured, WireMock, Pact
tags:
  - testing
  - api-testing
  - rest
  - http
---

# 1170 — API Testing

⚡ TL;DR — API testing validates HTTP API behavior — status codes, response schemas, business logic, error handling, authentication, and performance — directly at the API layer, without a UI, faster and more reliable than E2E UI tests.

| #1170           | Category: Testing                                                      | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | HTTP & APIs, Integration Test, REST                                    |                 |
| **Used by:**    | Developers, QA Engineers                                               |                 |
| **Related:**    | Integration Test, Contract Test, Postman, REST Assured, WireMock, Pact |                 |

---

### 🔥 The Problem This Solves

UI TESTS ARE SLOW AND BRITTLE:
Selenium/Playwright tests drive a browser, wait for page loads, interact with UI elements. They're slow (1-5 minutes per test), brittle (UI changes break tests), and can only test what the UI exposes. API tests bypass the UI entirely: send HTTP requests, verify responses. They're fast (milliseconds), stable (APIs change less than UIs), and can test all API behaviors — including those not exposed via the UI.

BACKEND VERIFICATION WITHOUT FRONTEND:
The frontend team is still building the UI. Backend APIs are done. How do you verify the backend is correct? API testing — test the API contract directly without waiting for the UI.

---

### 📘 Textbook Definition

**API testing** is the practice of testing application programming interfaces (APIs) — primarily HTTP/REST APIs — by sending requests and verifying responses, without the involvement of a UI layer. API tests verify: (1) **functional correctness** — does the API return the expected data for given inputs? (2) **contract adherence** — does the response schema match the API specification (OpenAPI)? (3) **error handling** — does the API return correct HTTP status codes and error messages for invalid inputs? (4) **security** — does the API enforce authentication, authorization, and input validation? (5) **performance** — does the API respond within acceptable latency? Tools: REST Assured (Java), Postman/Newman (JavaScript/collections), HTTPie, curl.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
API testing = verify HTTP APIs directly (no UI) — faster, more stable, and broader coverage than UI tests.

**One analogy:**

> API testing is **calling a restaurant kitchen directly** (rather than going through the dining room): you speak directly to the chef, order a specific dish, and verify what comes out of the kitchen — without waiting for a waiter, table setting, or menu. You can test the kitchen's output faster, more accurately, and test things the dining room experience never would (kitchen safety, ingredient quality, preparation time).

---

### 🔩 First Principles Explanation

WHAT TO TEST IN AN API:

```
1. HAPPY PATH:
   GET /users/123
   Expected: 200 OK, body = { "id": 123, "name": "Alice", "email": "alice@example.com" }

2. VALIDATION ERRORS:
   POST /users with missing required field "email"
   Expected: 400 Bad Request, body = { "error": "email is required" }

   POST /users with invalid email format
   Expected: 400 Bad Request, body = { "error": "email format is invalid" }

3. NOT FOUND:
   GET /users/99999 (doesn't exist)
   Expected: 404 Not Found

4. AUTHORIZATION:
   GET /admin/users without auth token
   Expected: 401 Unauthorized

   GET /admin/users with non-admin token
   Expected: 403 Forbidden

5. BUSINESS LOGIC:
   POST /orders with quantity=-1
   Expected: 400 Bad Request (not a 500!)

   POST /orders for out-of-stock product
   Expected: 409 Conflict or 422 Unprocessable Entity

6. PERFORMANCE:
   GET /users?page=1&size=100
   Expected: response time < 200ms

7. SCHEMA VALIDATION:
   All responses should match the OpenAPI specification
   No extra fields, no missing required fields, correct types

HTTP STATUS CODE SEMANTICS:
  200 OK            → successful GET, PUT, PATCH
  201 Created       → successful POST that creates a resource
  204 No Content    → successful DELETE
  400 Bad Request   → client validation error (malformed input)
  401 Unauthorized  → not authenticated (no/invalid token)
  403 Forbidden     → authenticated but not authorized
  404 Not Found     → resource doesn't exist
  409 Conflict      → state conflict (duplicate, out-of-stock)
  422 Unprocessable → semantically invalid (valid JSON, wrong business rules)
  429 Too Many Req  → rate limit exceeded
  500 Server Error  → never expected; always indicates a bug
```

REST ASSURED (Java) — FLUENT API TEST:

```java
given()
    .header("Authorization", "Bearer " + token)
    .contentType(ContentType.JSON)
    .body(new CreateOrderRequest("product-001", 2))
.when()
    .post("/api/v1/orders")
.then()
    .statusCode(201)
    .body("orderId", notNullValue())
    .body("status", equalTo("PENDING"))
    .body("items.size()", equalTo(1))
    .body("items[0].productId", equalTo("product-001"))
    .body("items[0].quantity", equalTo(2))
    .header("Location", containsString("/api/v1/orders/"));
```

---

### 🧪 Thought Experiment

THE API THAT RETURNS 200 FOR EVERYTHING:

```
Terrible API design (but it exists):
  POST /createUser { "name": "Alice" }
  Response: 200 OK, { "success": false, "error": "email is required" }

  The API returns 200 even when the operation FAILED.
  Clients must parse the body to determine success/failure.
  API tests: checking statusCode(200) passes even for errors.

  Correct design:
  POST /users { "name": "Alice" }  (missing email)
  Response: 400 Bad Request, { "error": "email is required" }

  API test: statusCode(400) — unambiguous failure signal.

  Lesson: API tests enforce HTTP semantics contract.
  If your API always returns 200, tests lose their signal value.
```

---

### 🧠 Mental Model / Analogy

> API testing is a **contract enforcement conversation**: "I'll send you this input; you must respond with that output." The API test is the contract; the API implementation is the party that must honor it. Any deviation — wrong status code, wrong schema, wrong business logic — is a contract breach.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Send an HTTP request to your API, verify the status code and response body. Use REST Assured (Java) or Postman. Faster and more stable than UI tests. Test status codes: 200, 201, 400, 401, 403, 404, 500.

**Level 2:** Test the full API behavior: happy path, validation errors, business logic errors, auth/authz. Use `@SpringBootTest(webEnvironment=RANDOM_PORT)` for integration API tests (real HTTP against a real Spring Boot app). Use `MockMvc` for faster slice tests (no real HTTP, but full Spring context). Validate response schema against OpenAPI specification (using Atlassian's `swagger-request-validator` or similar).

**Level 3:** API test organization: group by resource (UserApiTest, OrderApiTest). Use test data builders for request construction. Test non-functional aspects: response time assertions (`time(lessThan(200L))`), header presence (`Content-Type: application/json`), security headers (`Strict-Transport-Security`). Contract testing (Pact) is a specialized form of API testing focused on inter-service contracts.

**Level 4:** API testing in CI: Postman collections run via Newman (CLI) in CI pipeline. API test as documentation: Postman's published collections serve as living documentation of the API. OpenAPI validation: run `dredd` against the OpenAPI specification — ensures every documented endpoint actually behaves as specified. API testing for versioned APIs: test that v1 and v2 coexist correctly; test that deprecated v1 still functions during transition period.

---

### 💻 Code Example

```java
// Spring Boot API Test — MockMvc (fast, no HTTP overhead)
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean UserService userService;

    @Test
    void getUser_found_returns200() throws Exception {
        when(userService.findById(123L))
            .thenReturn(new User(123L, "Alice", "alice@example.com"));

        mockMvc.perform(get("/api/v1/users/123")
                .header("Authorization", "Bearer valid-token"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(123))
            .andExpect(jsonPath("$.name").value("Alice"))
            .andExpect(jsonPath("$.email").value("alice@example.com"));
    }

    @Test
    void getUser_notFound_returns404() throws Exception {
        when(userService.findById(999L)).thenThrow(new UserNotFoundException(999L));

        mockMvc.perform(get("/api/v1/users/999")
                .header("Authorization", "Bearer valid-token"))
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.error").value("User 999 not found"));
    }

    @Test
    void createUser_missingEmail_returns400() throws Exception {
        String requestBody = """
            { "name": "Alice" }
            """;

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors[0].field").value("email"))
            .andExpect(jsonPath("$.errors[0].message").value("must not be blank"));
    }

    @Test
    void getUser_unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/api/v1/users/123"))
            .andExpect(status().isUnauthorized());
    }
}
```

```java
// REST Assured — full HTTP integration test
@SpringBootTest(webEnvironment = RANDOM_PORT)
class UserApiIntegrationTest {

    @LocalServerPort int port;

    @BeforeEach
    void setUp() {
        RestAssured.port = port;
        RestAssured.basePath = "/api/v1";
    }

    @Test
    void createAndGetUser_fullCycle() {
        // Create
        String userId = given()
            .contentType("application/json")
            .body("""{"name":"Alice","email":"alice@test.invalid"}""")
        .when()
            .post("/users")
        .then()
            .statusCode(201)
            .body("name", equalTo("Alice"))
            .extract().path("id");

        // Retrieve
        given()
        .when()
            .get("/users/{id}", userId)
        .then()
            .statusCode(200)
            .body("name", equalTo("Alice"))
            .body("email", equalTo("alice@test.invalid"));
    }
}
```

---

### ⚖️ Comparison Table

|                       | Unit Test      | API Test (MockMvc)   | API Test (REST Assured) | E2E (Playwright)   |
| --------------------- | -------------- | -------------------- | ----------------------- | ------------------ |
| Layer                 | Business logic | HTTP layer + logic   | Full HTTP stack         | Full browser stack |
| Speed                 | Milliseconds   | Milliseconds         | Milliseconds            | Seconds            |
| Scope                 | Single class   | Controller + service | Full app stack          | Full app + browser |
| Brittle to UI changes | N/A            | N/A                  | No (no UI)              | Yes                |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| "API tests = E2E tests"              | API tests test the API layer; E2E tests drive a UI. API tests are faster and more stable                          |
| "Postman is just for manual testing" | Postman collections run via Newman in CI pipelines as automated API tests                                         |
| "200 status code = success"          | 200 only means HTTP-level success; business logic errors can return 200 (bad design) — test the response body too |

---

### 🚨 Failure Modes & Diagnosis

**1. Testing Implementation, Not Behavior**
Cause: API tests tied to internal field names that change with refactoring.
**Fix:** Test business behavior ("order status is PENDING") not implementation details ("statusCode is 1").

**2. Missing Error Path Tests**
Cause: Tests only cover happy path (200 responses); no tests for 400, 401, 403, 404.
Result: Error handling bugs shipped to production (wrong status codes, leaked stack traces).
**Fix:** Every API endpoint must have: at least one success test AND at least one error test (invalid input, missing auth).

**3. No Schema Validation**
Cause: Tests check specific fields but not the full response schema.
Result: API response adds unexpected fields or removes expected ones — clients break silently.
**Fix:** Validate response against OpenAPI schema in every API test.

---

### 🔗 Related Keywords

- **Prerequisites:** HTTP & APIs, Integration Test, REST
- **Related:** REST Assured, MockMvc, Postman, Newman, OpenAPI, Contract Test, Pact, WireMock

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Verify HTTP API behavior without UI      │
├──────────────┼───────────────────────────────────────────┤
│ TEST         │ Status codes, response schema, auth,     │
│ CHECKLIST    │ validation errors, business logic,       │
│              │ performance, error messages              │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOLS   │ MockMvc (fast, no HTTP) or REST Assured  │
│              │ (full HTTP, integration)                 │
├──────────────┼───────────────────────────────────────────┤
│ STATUS CODES │ 200/201 success, 400 invalid, 401 unauth,│
│              │ 403 forbidden, 404 not found, 500 = bug  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Skip the UI — test the API directly;    │
│              │  faster, stabler, broader coverage"      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** OpenAPI specification serves as both documentation and a contract for API testing. Describe: (1) how tools like `swagger-request-validator` validate that every API test request and response conforms to the OpenAPI spec (request validation: required params present, correct types; response validation: response schema matches the declared spec), (2) the "spec-first" vs. "code-first" debate — spec-first (write OpenAPI YAML → generate server stubs → implement) vs. code-first (implement → generate OpenAPI from annotations → validate), trade-offs of each, (3) how Dredd works — takes the OpenAPI spec and runs example requests from it against your real API, failing if responses don't match, effectively making the spec itself into a test suite, and (4) the challenge of keeping the OpenAPI spec in sync with the implementation (spec drift) — automated tools (`springdoc-openapi` in Spring Boot) that generate the spec from code annotations prevent drift by making the spec a build artifact.

**Q2.** API testing for versioned APIs introduces complex scenarios. Describe: (1) how to test API version coexistence (`/api/v1/` and `/api/v2/` running simultaneously) — separate test classes per version, shared test logic (inheritance or composition), (2) testing the deprecation contract — `Deprecation` response header, sunset dates, (3) the "non-breaking vs. breaking change" classification: adding a new optional field to a response is non-breaking; removing a field, changing a field's type, or changing status code semantics is breaking, (4) how consumer-driven contract tests (Pact) provide better protection than unit API tests for detecting breaking changes that affect real clients (Pact tests the changes against actual consumer contracts, not assumed contracts), and (5) testing API backwards compatibility automatically using tools like `openapi-diff` to detect breaking schema changes between spec versions in CI.
