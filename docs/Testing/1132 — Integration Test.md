---
layout: default
title: "Integration Test"
parent: "Testing"
nav_order: 1132
permalink: /testing/integration-test/
number: "1132"
category: Testing
difficulty: ★★☆
depends_on: Unit Test, Database Fundamentals, HTTP and APIs
used_by: Test Pyramid, CI-CD, Spring Boot Testing
related: Testcontainers, WireMock, @SpringBootTest, Embedded DB
tags:
  - testing
  - integration
  - spring
  - databases
---

# 1132 — Integration Test

⚡ TL;DR — An integration test verifies that multiple components work together correctly — typically involving a real database, real HTTP calls, or a real message broker, not mocks.

| #1132           | Category: Testing                                      | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Database Fundamentals, HTTP and APIs        |                 |
| **Used by:**    | Test Pyramid, CI-CD, Spring Boot Testing               |                 |
| **Related:**    | Testcontainers, WireMock, @SpringBootTest, Embedded DB |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Unit tests verify each function in isolation — mocking the database. But in production, the SQL query has a syntax error that only PostgreSQL 14 (not H2 in-memory) detects. The ORM mapping fails on a specific column type. A transaction boundary is in the wrong place — the rollback doesn't happen as expected. All unit tests pass. The bug only manifests when the code touches a real database. Without integration tests, you discover this in production.

THE BREAKING POINT:
Mocks lie. They return what you told them to return — not what the real system does. An integration test with a real PostgreSQL container (via Testcontainers) catches: SQL errors, type mapping issues, constraint violations, transaction semantics, N+1 queries, index usage. These bugs are invisible to unit tests but critical in production.

THE INVENTION MOMENT:
Spring's `@SpringBootTest` (2014) and Testcontainers (2016) made integration testing practical: spin up a real Spring context with a real Docker-containerised database in the test lifecycle. Previously, integration tests required a maintained shared database — slow, fragile, environment-dependent. Testcontainers isolated each test suite with a fresh, real database in a Docker container.

---

### 📘 Textbook Definition

An **integration test** verifies that two or more components (classes, services, layers) work correctly together. Unlike unit tests (which mock dependencies), integration tests use **real implementations** of one or more dependencies — real databases, real HTTP clients, real message queues. Integration tests are slower than unit tests (seconds, not milliseconds) but catch a class of bugs that unit tests cannot: **integration bugs** — mismatches between how components expect to interact.

In practice, "integration test" has two distinct meanings: (1) **component integration test**: tests multiple internal layers (service → repository → real database) with external infrastructure mocked by test containers; (2) **service integration test**: tests the interaction between two deployed services (one real, one WireMocked or containerised).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Integration test = real database + real Spring context + real SQL — no mocks for infrastructure.

**One analogy:**

> Unit testing is testing each LEGO brick individually (it's the right shape). Integration testing is assembling the bricks and verifying they actually click together and the resulting structure holds weight. Some bricks might be perfectly shaped individually but fail to click together.

**One insight:**
The most common integration bug: unit test mocks `repo.save()` returning the saved entity; real repository does `save()` but the entity has a cascade mapping error so the returned entity is null. Unit test: passes (mock returns non-null). Integration test with real DB: fails immediately.

---

### 🔩 First Principles Explanation

WHAT TO USE REAL VS MOCK:

```
Integration test boundary choices:
├── Full Spring context (@SpringBootTest) — slowest, highest confidence
│   └── Real database (Testcontainers PostgreSQL) — catches SQL bugs
│   └── Real message broker (Testcontainers Kafka) — catches serialization
│   └── External HTTP → WireMock (real HTTP client, mocked server)
│
├── Slice tests (faster, partial context):
│   ├── @DataJpaTest — JPA layer only, embedded/containerized DB
│   ├── @WebMvcTest — controller layer only, service mocked
│   └── @JsonTest — Jackson serialization only
│
└── Unit test — everything mocked
```

SPRING BOOT SLICE TESTING:

```
@DataJpaTest:
  - Loads only JPA configuration, repositories, entities
  - No service beans, no controllers
  - Uses embedded H2 OR @AutoConfigureTestDatabase(replace=NONE)
    with Testcontainers for real DB
  - Each test wrapped in @Transactional + rollback → clean state

@WebMvcTest(UserController.class):
  - Loads only UserController + its direct Spring MVC wiring
  - Services auto-mocked (or @MockBean)
  - Tests HTTP request/response, serialization, validation
  - Fast (< 500ms), no database
```

THE TRADE-OFFS:
Gain: Catches integration bugs that unit tests miss; builds confidence for production; documents how layers interact.
Cost: Slow (1–30s per test); requires Docker for Testcontainers; test setup complexity; parallel execution requires isolated databases.

---

### 🧪 Thought Experiment

FINDING THE H2 VS POSTGRESQL BUG:

Unit test (passes with H2/mock):

```java
// Mock returns user, test passes
when(userRepo.findByEmail("alice@test.com")).thenReturn(Optional.of(user));
```

Integration test (fails with real PostgreSQL):

```sql
-- Actual query generated by JPA:
SELECT * FROM users WHERE email = 'alice@test.com'  -- fails!
-- Reason: column is 'email_address' in PostgreSQL, 'email' in entity mapping
-- H2 is lenient about case; PostgreSQL is strict
```

The integration test catches the mapping mismatch. The unit test never runs SQL.

---

### 🧠 Mental Model / Analogy

> Integration tests are like dress rehearsals: the full cast, real costumes, real stage — not the individual line-reading sessions (unit tests) or the full opening night with a paying audience (E2E). Dress rehearsals catch things that individual rehearsals miss: the door that sticks, the costume that doesn't fit the set, the lighting cue that fires too early.

> Testcontainers is the stage crew that sets up and tears down the stage for each rehearsal automatically.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Integration tests check that the pieces of your system work together — especially with real databases and real external services.

**Level 2:** Use `@SpringBootTest` + Testcontainers for full context tests. Use `@DataJpaTest` for repository-layer tests (faster). Use WireMock for external HTTP APIs. Annotate with `@Transactional` where you want rollback, but be aware: `@Transactional` in integration tests rolls back — which means async operations and events may not fire.

**Level 3:** Testcontainers' `@Container` with `@DynamicPropertySource` injects the container's port into Spring's `application.properties` at runtime. Singleton pattern: share one container across all tests in a class with `static` field + `Lifecycle.CLASS`. `@DataJpaTest` with `replace=NONE` uses the Testcontainers PostgreSQL, not H2 — this is strongly recommended for production-fidelity. Flyway/Liquibase migrations run in test context — catches migration SQL errors early.

**Level 4:** The integration test pyramid trade-off: full `@SpringBootTest` starts the entire Spring context (2–5s cold start). Multiple test classes each starting their own context = 10+ seconds overhead per class. Spring's `ApplicationContext` caching (`@TestConfiguration`, `@DirtiesContext` avoidance) is critical: if all tests share the same Spring context configuration, the context is built once and reused. `@DirtiesContext` (which forces context reload) should be used sparingly. This is why Spring slice tests (`@DataJpaTest`, `@WebMvcTest`) are faster — smaller context, reusable across more tests.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────────┐
│          SPRING BOOT INTEGRATION TEST LIFECYCLE              │
├──────────────────────────────────────────────────────────────┤
│  @SpringBootTest + Testcontainers:                          │
│                                                              │
│  Test class loading:                                        │
│    1. Testcontainers: docker pull postgres:16               │
│       docker run postgres:16 --port=5432:RANDOM            │
│    2. @DynamicPropertySource: inject                        │
│       spring.datasource.url=jdbc:postgresql://localhost:PORT│
│    3. Spring ApplicationContext starts (once, cached)       │
│       Flyway migrations run → schema created                │
│                                                              │
│  Per @Test:                                                 │
│    @BeforeEach: insert test data (or @Sql script)           │
│    Test executes with real DB, real Spring beans            │
│    @AfterEach: clean data (@Transactional rollback or       │
│                            @Sql("cleanup.sql"))             │
│                                                              │
│  End of test suite:                                         │
│    Testcontainers: docker stop → container removed          │
└──────────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

FULL INTEGRATION TEST EXAMPLE:

```
Test: POST /api/orders → verify order saved to DB + notification sent

1. Testcontainers: PostgreSQL (port 5432) + Kafka (port 9092) started
2. Spring context started, wired to both containers
3. Test:
   POST /api/orders (via MockMvc)
   → OrderController.createOrder()
   → OrderService.processOrder()
   → OrderRepository.save() → real INSERT in PostgreSQL
   → KafkaTemplate.send("orders") → real message in Kafka
4. Assertions:
   Response: 201 Created, body has orderId
   DB: SELECT COUNT(*) FROM orders WHERE id=? → 1 (real query)
   Kafka: KafkaConsumer.poll() → message received (real broker)
5. Cleanup: @Sql("DELETE FROM orders") or @Transactional rollback
```

---

### 💻 Code Example

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("test_db");

    @DynamicPropertySource
    static void configureDataSource(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired TestRestTemplate restTemplate;
    @Autowired OrderRepository orderRepository;

    @Test
    void createOrder_validRequest_savedInDatabase() {
        // Act
        ResponseEntity<OrderResponse> response = restTemplate.postForEntity(
            "/api/orders",
            new CreateOrderRequest("user1", List.of("item1", "item2")),
            OrderResponse.class
        );

        // Assert HTTP
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        String orderId = response.getBody().getId();

        // Assert DB (real query)
        Optional<Order> saved = orderRepository.findById(orderId);
        assertThat(saved).isPresent();
        assertThat(saved.get().getUserId()).isEqualTo("user1");
    }

    @Test
    @Sql(scripts = "/test-data/orders.sql", executionPhase = BEFORE_TEST_METHOD)
    @Sql(scripts = "/test-data/cleanup.sql", executionPhase = AFTER_TEST_METHOD)
    void getOrders_existingUser_returnsAllOrders() {
        ResponseEntity<List<OrderResponse>> response = restTemplate.exchange(
            "/api/orders?userId=user1",
            HttpMethod.GET, null,
            new ParameterizedTypeReference<>() {}
        );
        assertThat(response.getBody()).hasSize(3);
    }
}
```

---

### ⚖️ Comparison Table

| Approach                         | Speed   | Fidelity  | Use Case                          |
| -------------------------------- | ------- | --------- | --------------------------------- |
| Unit test + mocks                | <100ms  | Low       | Logic bugs, business rules        |
| @DataJpaTest + H2                | ~500ms  | Medium    | Repository queries (with caveats) |
| @DataJpaTest + Testcontainers    | ~2s     | High      | Real SQL, constraints, migrations |
| @SpringBootTest + Testcontainers | ~5–30s  | Very High | Full layer integration            |
| Deployed service test            | Minutes | Highest   | Post-deploy smoke test            |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                          |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| "H2 is equivalent to PostgreSQL for testing"    | H2 has different SQL dialect, different type support, different constraint enforcement — production bugs hide    |
| "@SpringBootTest is always the right choice"    | Slice tests (@DataJpaTest, @WebMvcTest) are faster and test specific layers; use SpringBootTest only when needed |
| "Integration tests replace unit tests"          | No — unit tests catch logic bugs faster; integration tests catch integration bugs; both are required             |
| "@Transactional in tests = production behavior" | @Transactional in tests ROLLS BACK after each test; it masks missing @Transactional in production code           |

---

### 🚨 Failure Modes & Diagnosis

**1. Tests Pass in IDE, Fail in CI (Port Conflict)**

Cause: Testcontainers assigns random ports; but if `application.properties` has hardcoded port → wrong container.
Fix: Always use `@DynamicPropertySource` to inject dynamic container ports.

**2. Slow Test Suite (30s+ per test class)**

Cause: `@DirtiesContext` on multiple test classes forces Spring context rebuild.
Fix: Share context by using identical configuration across tests. Remove unnecessary `@DirtiesContext`. Use `@MockBean` consistently (adding/removing `@MockBean` invalidates context cache).

---

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, JPA/Hibernate, HTTP and APIs
- **Builds on:** Testcontainers, WireMock, @SpringBootTest, Contract Test
- **Alternatives:** Unit Test (faster, less fidelity), E2E Test (full fidelity, much slower)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Test multiple components together with   │
│              │ real infrastructure (DB, HTTP, queues)   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Mocks lie; real DB catches SQL errors,   │
│              │ type mismatches, and constraint bugs      │
├──────────────┼───────────────────────────────────────────┤
│ TOOL         │ Testcontainers (real DB in Docker) +     │
│              │ WireMock (real HTTP client, mocked server)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Seconds (not ms) but catches real bugs   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Real DB, real HTTP, slow but honest"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Testcontainers → Contract Test → E2E     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Transactional` on a Spring integration test method causes the entire test to run inside a transaction that is rolled back after the test. This is convenient for test isolation but creates a subtle bug: if your production service method calls `entityManager.flush()` and checks that a `UNIQUE` constraint violation is raised, the test may pass (constraint checked on flush inside the transaction) but if the production service expects to catch `DataIntegrityViolationException` outside the transaction boundary, the test doesn't actually simulate the production behavior. Describe three scenarios where `@Transactional` in integration tests produces false positives (tests pass but production fails) and the correct fix for each.

**Q2.** Testcontainers' singleton pattern uses a `static` container field with `@Container`. This means the container starts once and is shared across all test methods in the class. But if two test classes are run in parallel (Maven Surefire with `forkCount=2`) and both create a `PostgreSQLContainer`, they each get their own container — doubling Docker overhead. Testcontainers' "Reuse" feature (`withReuse(true)`) creates a container that is NOT stopped after the test — it's reused across JVM restarts using a hash of the container configuration. Describe: (1) the test isolation risks of container reuse (dirty state between test runs), (2) why Testcontainers disables reuse by default, and (3) how to implement safe reuse using a shared abstract base class with `@BeforeAll` data cleanup.
