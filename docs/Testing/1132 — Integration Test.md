---
layout: default
title: "Integration Test"
parent: "Testing"
nav_order: 1132
permalink: /testing/integration-test/
---
# 1132 — Integration Test

`#testing` `#intermediate` `#java` `#spring`

⚡ TL;DR — A test that verifies multiple components working together, using real or near-real dependencies.

| #1132 | category: Testing
|:---|:---|:---|
| **Depends on:** | Unit Test, Spring Boot Test, Testcontainers | |
| **Used by:** | Test Pyramid, CI/CD, Contract Test | |

---

### 📘 Textbook Definition

An integration test verifies that multiple components interact correctly when combined — testing the integration points between modules, services, and external systems (databases, message queues, caches). Unlike unit tests, integration tests use real or realistic implementations of dependencies rather than test doubles.

---

### 🟢 Simple Definition (Easy)

Integration tests check that **different pieces of your system work together correctly** — your service actually talks to a real database and the data comes back as expected.

---

### 🔵 Simple Definition (Elaborated)

Where unit tests verify logic in isolation, integration tests verify that the connections between components work. A Spring Boot integration test boots the full application context, connects to a real (or containerized) database, and exercises the full stack from controller to repository. They are slower than unit tests but catch a different class of bugs — wiring, query, and configuration errors that mocks cannot reveal.

---

### 🔩 First Principles Explanation

**The core problem:**
All unit tests pass, but the system fails in production. Why? The integration points — database queries, HTTP clients, message consumers — were mocked in unit tests and never tested with real implementations.

**The insight:**
> "Mocks lie. They return what you configured them to return — not what the real system would return. Integration tests test reality."

```
Unit test: mock returns { userId: 1, name: "Alice" }
Integration test: real DB query returns { userId: 1, name: "alice" }
                                         ^ lowercase — bug in DB constraint
```

---

### ❓ Why Does This Exist (Why Before What)

Unit tests cannot catch: SQL query bugs, JPA mapping errors, Spring bean wiring failures, serialization mismatches, or cache/queue configuration problems. Integration tests exist to catch the class of bugs that only emerge at the boundaries between components.

---

### 🧠 Mental Model / Analogy

> Integration tests are like a test drive of a newly assembled car. Unit tests verified each part (engine OK, brakes OK, steering OK). The test drive confirms the parts actually work together — the gear shift connects to the transmission, the brakes respond to the pedal, the car is complete.

---

### ⚙️ How It Works (Mechanism)

```
Spring Boot Integration Test scope:

  @SpringBootTest: boots full application context
  @DataJpaTest:    spins up JPA + in-memory DB (H2) — no full context
  @WebMvcTest:     tests controller layer + MockMvc — no service/repo

  Real dependencies via Testcontainers:
    - PostgreSQL in Docker container → identical to production
    - Kafka, Redis, MySQL — any dependency containerized

  Test database strategies:
    - @Transactional on test → rolls back after each test (no cleanup needed)
    - @DirtiesContext        → fresh context for each test (slow)
    - Flyway/Liquibase       → migrate schema before tests run
```

---

### 🔄 How It Connects (Mini-Map)

```
[Unit Test]  <-- tests logic in isolation
      ↓
[Integration Test]  <-- tests components together (DB, HTTP, queue)
      ↓
[Contract Test]  <-- tests API contracts between services
      ↓
[E2E Test]  <-- tests full user journey
```

---

### 💻 Code Example

```java
// Spring Boot integration test with Testcontainers
@SpringBootTest
@Testcontainers
@Transactional  // rolls back after each test — no cleanup code needed
class OrderServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired OrderService orderService;
    @Autowired OrderRepository orderRepository;

    @Test
    void placedOrderIsPersisted() {
        // Arrange
        Order order = new Order(customerId: 1L, items: List.of(new Item("book", 29.99)));

        // Act — calls real service → real repository → real PostgreSQL
        orderService.placeOrder(order);

        // Assert — verify it's actually in the database
        List<Order> savedOrders = orderRepository.findByCustomerId(1L);
        assertThat(savedOrders).hasSize(1);
        assertThat(savedOrders.get(0).getItems()).hasSize(1);
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Integration tests replace unit tests | They complement: unit tests find logic bugs; integration finds wiring bugs |
| @SpringBootTest is too slow to use | Testcontainers + proper scoping makes integration tests fast enough |
| H2 in-memory database is fine for integration tests | H2 is not PostgreSQL — use Testcontainers for production-faithful tests |
| Integration tests need real external services | Testcontainers provides real containerized services locally |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using H2 Instead of the Real Database**
H2 SQL dialect differs from PostgreSQL — tests pass but the same query fails in production.
Fix: always use Testcontainers with the same database version as production.

**Pitfall 2: Slow Context Startup**
Each test class starts a fresh Spring context — multiplied by 50 test classes = 10+ minute build.
Fix: use `@DirtiesContext` sparingly; share application context via static containers.

**Pitfall 3: Test Data Bleeding Between Tests**
One test inserts data that breaks the next test's assertions.
Fix: annotate integration tests with `@Transactional` to roll back after each test.

---

### 🔗 Related Keywords

- **Unit Test** — faster, more isolated; integration tests complement them
- **Testcontainers** — the library that provides real Docker-based dependencies for tests
- **Spring Boot Test** — the testing support framework for Spring applications
- **Contract Test** — tests the API contract between two services
- **Test Pyramid** — integration tests sit in the middle layer

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Verify that components work together using     │
│              │ real dependencies, not mocks                  │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Testing DB queries, service wiring, HTTP      │
│              │ clients, message consumers                    │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Testing pure logic — use a faster unit test   │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Mocks lie — integration tests tell the truth  │
│              │  about how components work together"          │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Testcontainers --> Contract Test --> E2E Test  │
└─────────────────────────────────────────────────────────────┘
```

### 🧠 Think About This Before We Continue

**Q1.** What class of bugs can integration tests catch that unit tests with mocks cannot?  
**Q2.** Why should you use the same database engine (PostgreSQL) in tests as in production?  
**Q3.** How does `@Transactional` on a test method avoid the need for manual test data cleanup?

