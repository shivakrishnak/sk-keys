---
layout: default
title: "Integration Test"
parent: "Testing"
nav_order: 1132
permalink: /testing/integration-test/
number: "1132"
category: Testing
difficulty: ★★☆
depends_on: "Unit Test, Maven Lifecycle"
used_by: "Contract Test, E2E Test, Testcontainers, Spring Boot Test"
tags: #testing, #integration-test, #testcontainers, #spring-boot-test, #database-testing
---

# 1132 — Integration Test

`#testing` `#integration-test` `#testcontainers` `#spring-boot-test` `#database-testing`

⚡ TL;DR — An **integration test** verifies that multiple components work together correctly — typically testing a service with its real database, real HTTP clients, or real message broker. Slower than unit tests (seconds to minutes) but catches issues that unit tests can't: SQL query correctness, ORM mapping errors, real network behavior. In Java/Spring Boot: `@SpringBootTest` + Testcontainers (real PostgreSQL in Docker during tests).

| #1132           | Category: Testing                                         | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, Maven Lifecycle                                |                 |
| **Used by:**    | Contract Test, E2E Test, Testcontainers, Spring Boot Test |                 |

---

### 📘 Textbook Definition

**Integration test**: an automated test that verifies the interaction between two or more components, modules, or systems — testing them in combination rather than in isolation. Scope: can range from testing a service with its real database (narrow integration test) to testing a full HTTP request through the entire Spring Boot application stack (broad integration test). Characteristics: uses real or near-real implementations of dependencies (real PostgreSQL, real Kafka, real Redis — typically via Docker/Testcontainers); slower than unit tests (seconds to minutes for startup + test execution); fewer in number (testing pyramid: fewer integration tests than unit tests); catches issues that mocks can't: SQL errors, ORM mapping bugs, serialization/deserialization issues, network protocol correctness, transaction boundary behavior. In Java/Spring Boot: `@SpringBootTest` loads the full application context; `@DataJpaTest` loads only JPA layer; `@WebMvcTest` loads only web layer. Maven: `maven-failsafe-plugin` runs integration tests (`*IT.java`) in the `integration-test` phase (after `package`).

---

### 🟢 Simple Definition (Easy)

Unit tests mock the database — so they never test your actual SQL queries. Integration tests use a REAL database (via Testcontainers — a real PostgreSQL running in Docker). You write an order to the database and read it back. Does your JPA mapping work? Does your query return the right results? Does your transaction roll back on error? Integration tests answer these questions that unit tests can't.

---

### 🔵 Simple Definition (Elaborated)

Integration tests live between unit tests and E2E tests:

- **Unit test**: mock everything → fast, but tests logic in isolation from infrastructure
- **Integration test**: use real infrastructure (real DB, real cache, real queue) → slower but tests real behavior
- **E2E test**: full production-like environment with real UI/API → slowest but most realistic

**What integration tests catch that unit tests miss**:

- SQL query bugs (wrong joins, missing indexes, constraint violations)
- JPA mapping errors (wrong column names, type mismatches)
- Transaction behavior (does rolling back actually undo the inserts?)
- Real serialization (does your Jackson configuration actually serialize correctly to JSON?)
- Real HTTP (does your Spring MVC controller return the right status code for each input?)
- Real Kafka (does your consumer actually consume messages in order?)

**The cost**: each integration test may take 1-30 seconds (vs 1ms for unit tests). Spring application context startup alone can take 10-30 seconds for large apps (mitigated by context caching between tests in the same test suite).

---

### 🔩 First Principles Explanation

```java
// SPRING BOOT INTEGRATION TEST PATTERNS

// PATTERN 1: Full Spring Boot context + Testcontainers (most common)

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("testuser")
        .withPassword("testpass");

    @Container
    static GenericContainer<?> redis = new GenericContainer<>("redis:7-alpine")
        .withExposedPorts(6379);

    @DynamicPropertySource   // override Spring properties with container-specific values
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.redis.host", redis::getHost);
        registry.add("spring.redis.port", () -> redis.getMappedPort(6379));
    }

    @Autowired
    private TestRestTemplate restTemplate;  // real HTTP client to the running app

    @Autowired
    private OrderRepository orderRepository;

    @Test
    @DisplayName("POST /orders creates order and persists to database")
    void createOrder_persistsToDatabase() {
        // ACT: real HTTP call to the running Spring Boot app
        CreateOrderRequest request = new CreateOrderRequest("Widget", 2, 49.99);
        ResponseEntity<OrderResponse> response = restTemplate.postForEntity(
            "/orders", request, OrderResponse.class);

        // ASSERT: HTTP response
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getId()).isNotNull();

        // ASSERT: data actually persisted to real PostgreSQL
        Optional<Order> saved = orderRepository.findById(response.getBody().getId());
        assertThat(saved).isPresent();
        assertThat(saved.get().getProductName()).isEqualTo("Widget");
        assertThat(saved.get().getQuantity()).isEqualTo(2);
    }

    @Test
    @Transactional  // rollback after test
    void updateOrder_transactionRollback_onError() {
        // Test transaction boundary behavior
        Order order = orderRepository.save(new Order("Widget", 1, 49.99));

        // simulate error mid-transaction
        assertThatThrownBy(() -> orderService.updateOrderWithError(order.getId()))
            .isInstanceOf(ServiceException.class);

        // verify rollback: order status unchanged
        Order fromDb = orderRepository.findById(order.getId()).orElseThrow();
        assertThat(fromDb.getStatus()).isEqualTo(OrderStatus.PENDING);
    }
}

// PATTERN 2: Slice test (@DataJpaTest) - only JPA layer, faster
@DataJpaTest  // loads only JPA/Hibernate; auto-configures H2 or TestContainers
@Testcontainers
class OrderRepositoryIT {

    @Container
    @ServiceConnection  // Spring Boot 3.1+: auto-configures datasource from container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");

    @Autowired
    private OrderRepository orderRepository;

    @Test
    @DisplayName("findByCustomerId returns only that customer's orders")
    void findByCustomerId_returnsCorrectOrders() {
        // ARRANGE: insert test data
        orderRepository.save(new Order("customer-1", "Widget", 1));
        orderRepository.save(new Order("customer-1", "Gadget", 2));
        orderRepository.save(new Order("customer-2", "Thing", 3));

        // ACT
        List<Order> orders = orderRepository.findByCustomerId("customer-1");

        // ASSERT
        assertThat(orders).hasSize(2);
        assertThat(orders).extracting(Order::getProductName)
            .containsExactlyInAnyOrder("Widget", "Gadget");
    }
}

// PATTERN 3: @WebMvcTest - only web layer (controller + serialization)
@WebMvcTest(OrderController.class)
class OrderControllerIT {

    @Autowired
    private MockMvc mockMvc;       // MockMvc: HTTP requests without starting real server

    @MockBean
    private OrderService orderService;  // mock the service layer

    @Test
    void createOrder_invalidInput_returns400() throws Exception {
        // Test: controller validation + error response format
        mockMvc.perform(post("/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"quantity\": -1}"))  // invalid: negative quantity
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.error").exists());
    }

    @Test
    void createOrder_validInput_callsServiceAndReturns201() throws Exception {
        when(orderService.create(any()))
            .thenReturn(new Order(UUID.randomUUID(), "Widget", 1));

        mockMvc.perform(post("/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"productName\": \"Widget\", \"quantity\": 1}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists());
    }
}
```

```
INTEGRATION TEST SCOPE SPECTRUM:

  Narrow ←────────────────────────────────────→ Broad

  @DataJpaTest        @SpringBootTest(MOCK)        @SpringBootTest(RANDOM_PORT)
  (JPA only,         (full context,              (full context,
   no web,            MockMvc,                    real HTTP server,
   fastest)           medium speed)               slowest)

  Tests: SQL queries  Tests: MVC + service        Tests: full stack including
         ORM mapping         HTTP contract              actual HTTP
         transactions        serialization              multiple services

  TESTCONTAINERS BENEFIT:
  - Real PostgreSQL (not H2) → catches dialect-specific SQL
  - Real Redis → catches serialization, TTL, eviction behavior
  - Real Kafka → catches partition, consumer group behavior
  - Starts once per test class (static container); reused across tests

MAVEN CONVENTION:
  Unit tests:           *Test.java → maven-surefire-plugin → test phase
  Integration tests:    *IT.java  → maven-failsafe-plugin  → integration-test phase

  Run unit only:        mvn test
  Run all:              mvn verify
  Run integration only: mvn failsafe:integration-test (rarely done)
```

---

### ❓ Why Does This Exist (Why Before What)

Unit tests can't verify that your JPA `@Query` annotation has correct JPQL syntax, that your database schema migration matches your entity mapping, that your Redis cache correctly handles TTL expiration, or that your Kafka consumer handles offset commits correctly. These behaviors only emerge when the real systems interact. Integration tests exist to bridge the gap between "the logic is correct" (unit tests) and "the whole system works" (E2E tests) — they test the contract between your code and its infrastructure dependencies.

---

### 🧠 Mental Model / Analogy

> **Integration tests are like test-fitting components before final assembly**: a unit test is testing each gear individually (does this gear have 24 teeth and turn smoothly?). An integration test is test-fitting two gears together (do these two gears mesh correctly? Is there backlash? Do they bind?). An E2E test is running the whole clock mechanism. You need all three: a gear with the right specs (unit test passing) can still not mesh with another gear (integration test failing) — if the tolerances are different or the spacing is wrong.

---

### 🔄 How It Connects (Mini-Map)

```
Unit tests verify logic; integration tests verify component interactions
        │
        ▼
Integration Test ◄── (you are here)
(real DB, real cache, real queue; slower but catches infra issues)
        │
        ├── Unit Test: the foundation; integration tests build on top
        ├── Testcontainers: provides real Docker-based dependencies for integration tests
        ├── @SpringBootTest: Spring Boot's integration test annotation
        ├── Maven Lifecycle: failsafe plugin runs integration tests in integration-test phase
        └── Contract Test: specialized integration test for service-to-service contracts
```

---

### 💻 Code Example

```java
// Testcontainers @ServiceConnection (Spring Boot 3.1+: simplest approach)
@SpringBootTest
@Testcontainers
class ProductServiceIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine");
    // @ServiceConnection auto-configures spring.datasource.* from the container
    // No @DynamicPropertySource needed!

    @Container
    @ServiceConnection
    static RedisContainer redis = new RedisContainer("redis:7-alpine");

    @Autowired
    private ProductService productService;

    @Test
    void getProduct_cachesResult_reducesDbCalls() {
        // First call: hits database
        Product first = productService.getById("prod-123");
        // Second call: should hit Redis cache
        Product second = productService.getById("prod-123");

        assertThat(first).isEqualTo(second);
        // Verify caching worked: second call didn't go to DB
        // (verify via metrics or spy on the repository)
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Integration tests should always use an in-memory H2 database | H2 has different SQL dialect, different constraint behavior, different type handling than PostgreSQL/MySQL. Tests passing with H2 can fail with the real database. Testcontainers makes it easy to test with the actual database. Use H2 for ultra-fast smoke tests only when real DB behavior is not important. |
| `@SpringBootTest` is the only way to write integration tests | `@DataJpaTest`, `@WebMvcTest`, `@DataMongoTest` etc. are "slice tests" that load only the relevant layer. They start faster (smaller context) and are appropriate for testing specific layers. Use `@SpringBootTest` only when you need the full application context.                                            |
| All integration tests must test the full stack               | Integration tests exist on a spectrum. A repository test (`@DataJpaTest`) that tests SQL queries against a real database is an integration test, even without a web layer. Choose the appropriate scope: don't use `@SpringBootTest` (full context) when `@DataJpaTest` (JPA-only) is sufficient.                |

---

### 🔗 Related Keywords

- `Unit Test` — faster, isolated tests that unit integration tests build upon
- `Testcontainers` — Docker-based real dependencies for integration tests
- `Contract Test` — integration tests for service-to-service API contracts
- `E2E Test` — tests the full production-like stack
- `Maven Lifecycle` — integration tests run in the `integration-test` phase via Failsafe

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTEGRATION TEST = multiple components + real infra     │
│                                                          │
│ ANNOTATIONS (Spring Boot):                              │
│   @SpringBootTest(RANDOM_PORT) → full stack + HTTP      │
│   @SpringBootTest(MOCK) → full context + MockMvc        │
│   @DataJpaTest → JPA + DB only (fastest)                │
│   @WebMvcTest → Web layer + MockMvc (no DB)             │
│                                                          │
│ INFRA: Testcontainers (real PostgreSQL/Redis/Kafka)     │
│ MAVEN: *IT.java → failsafe → integration-test phase     │
│ RUN: mvn verify (runs unit + integration tests)         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@SpringBootTest` starts the full Spring application context including all beans, auto-configurations, and proxies. For a large application with 200+ beans, this takes 30-60 seconds. A test suite with 50 integration tests would take 25-50 minutes if each test restarted the context. Spring's context caching reuses the context across tests in the same JVM run — IF they use the same context configuration. What breaks context caching? (Answer: `@MockBean`, `@TestPropertySource`, different `webEnvironment` settings, `@DirtiesContext`.) Design a test architecture for a large Spring Boot project that maximizes context reuse while still allowing isolated test scenarios.

**Q2.** Testcontainers starts Docker containers for each test run. On a developer's machine with SSD and Docker: PostgreSQL container starts in ~3 seconds. In CI with resource-constrained runners and Docker-in-Docker: 15-30 seconds. Multiplied by 5 container types (Postgres, Redis, Kafka, Zookeeper, WireMock) per test suite = 75-150 seconds JUST for container startup, before any test runs. Testcontainers Reuse mode (`withReuse(true)`) keeps containers alive between runs. What are the trade-offs of container reuse? (Shared state between test runs, leftover data.) How do you implement clean state between test classes without restarting containers?
