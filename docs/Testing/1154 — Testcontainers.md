---
layout: default
title: "Testcontainers"
parent: "Testing"
nav_order: 1154
permalink: /testing/testcontainers/
number: "1154"
category: Testing
difficulty: ★★★
depends_on: Docker, Integration Test, Containers
used_by: Java Developers, Spring Boot Teams
related: Docker, Integration Test, Faking, WireMock, H2 Database
tags:
  - testing
  - testcontainers
  - integration-testing
  - docker
---

# 1154 — Testcontainers

⚡ TL;DR — Testcontainers is a Java library that starts real Docker containers (PostgreSQL, Redis, Kafka, etc.) programmatically in tests — giving you real database/service behavior in integration tests without a persistent external setup.

| #1154           | Category: Testing                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Docker, Integration Test, Containers                    |                 |
| **Used by:**    | Java Developers, Spring Boot Teams                      |                 |
| **Related:**    | Docker, Integration Test, Faking, WireMock, H2 Database |                 |

---

### 🔥 The Problem This Solves

THE H2 FALLACY:
Team uses H2 in-memory database for integration tests. Tests pass. In production with PostgreSQL: a native query using `::jsonb` type cast fails (H2 doesn't support it). A `RETURNING` clause query fails. An `ON CONFLICT DO UPDATE` upsert fails. The integration tests gave false confidence — H2 is a different database engine. The code was tested against a fake that diverges from reality.

THE SHARED DATABASE PROBLEM:
Alternative: "just use a shared dev PostgreSQL database." Problems: (1) developers step on each other (Test A creates user "alice"; Test B assumes no alice); (2) CI pipeline needs network access to shared DB; (3) schema migrations in CI break shared DB for all developers; (4) CI tests are non-deterministic (depend on shared state). Testcontainers solves both: real PostgreSQL, isolated per test run.

---

### 📘 Textbook Definition

**Testcontainers** is a Java library (also available for other languages) that provides lightweight, throwaway instances of common databases, message brokers, web browsers, and any Docker container as part of integration tests. Each test (or test class) can start a fresh container, run tests against it, and destroy the container when tests finish. Containers are managed automatically through the JUnit lifecycle. This enables testing against the exact same database engine used in production, with complete isolation and no persistent external infrastructure.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Testcontainers = start a real PostgreSQL (or Redis, Kafka, etc.) Docker container in your test, use it, discard it.

**One analogy:**

> Testcontainers is like **renting a hotel room for each test**: you get a fresh, real room (real database), use it for your test, and check out (container destroyed). Compare to the H2 fake — using a cardboard cutout of a hotel room. The real room has all the real properties (real plumbing = real SQL engine); the cardboard room looks similar but isn't.

---

### 🔩 First Principles Explanation

TESTCONTAINERS BASIC USAGE:

```java
@Testcontainers
@SpringBootTest
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private UserRepository repo;

    @Test
    void saveAndFindUser() {
        User user = new User("alice@example.com");
        repo.save(user);
        Optional<User> found = repo.findByEmail("alice@example.com");
        assertThat(found).isPresent();
    }
}
```

CONTAINER LIFECYCLE OPTIONS:

```java
// Option 1: Static container — shared across all tests in the class
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");
// Started before first test, stopped after last test in the class
// Isolation: use @Transactional rollback or @BeforeEach deleteAll()

// Option 2: Instance container — new container per test method
@Container
PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");
// Maximum isolation; very slow (new container per test)
// Use only for tests that modify schema (migrations)

// Option 3: Reuse mode — container shared across test classes
@Container
static PostgreSQLContainer<?> postgres =
    new PostgreSQLContainer<>("postgres:15").withReuse(true);
// Container survives across test class restarts
// Requires explicit cleanup (@BeforeEach deleteAll or TRUNCATE)
```

AVAILABLE CONTAINERS:

```
Databases:  PostgreSQLContainer, MySQLContainer, MongoDBContainer,
            OracleContainer, CassandraContainer
Messaging:  KafkaContainer, RabbitMQContainer, ActiveMQContainer
Caching:    GenericContainer("redis:7")
Search:     ElasticsearchContainer
Browser:    BrowserWebDriverContainer (Selenium)
Custom:     GenericContainer("any-image:tag")
```

---

### 🧪 Thought Experiment

THE KAFKA CONSUMER TEST:

```java
@Testcontainers
class OrderEventConsumerTest {

    @Container
    static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.4.0"));

    @Test
    void consumer_processesOrderPlacedEvent() throws Exception {
        // Configure consumer to connect to test Kafka
        OrderEventConsumer consumer = new OrderEventConsumer(kafka.getBootstrapServers());

        // Produce a test event to real Kafka
        KafkaProducer<String, String> producer = createProducer(kafka.getBootstrapServers());
        producer.send(new ProducerRecord<>("orders", "order-123",
            "{\"orderId\":\"123\",\"status\":\"PLACED\"}")).get();

        // Verify consumer processes it
        await().atMost(5, SECONDS).untilAsserted(() ->
            assertThat(orderRepository.findById("123")).isPresent()
                .hasValueSatisfying(o -> assertThat(o.getStatus()).isEqualTo(PLACED)));
    }

    // Tests against REAL Kafka — same serialization, same partition behavior,
    // same consumer group semantics as production
}
```

---

### 🧠 Mental Model / Analogy

> Testcontainers is the difference between **testing a recipe on the real stove** vs. testing it in a cooking simulator. The simulator (H2) looks similar but doesn't burn things the same way, doesn't have the same heat distribution, and can't handle the same cookware. The real stove (PostgreSQL in Docker) is exactly what your recipe will encounter in the restaurant (production). Testcontainers brings the real stove into your test kitchen.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Testcontainers starts a real Docker container (PostgreSQL, Redis, Kafka) when your tests run and shuts it down after. Your tests run against the real software, not a fake.

**Level 2:** Add to Maven: `testcontainers:junit-jupiter` + `testcontainers:postgresql`. Annotate test class with `@Testcontainers`. Declare container with `@Container static PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:15")`. Use `@DynamicPropertySource` to set Spring datasource URL. For cleanup: add `@Transactional` on tests (automatic rollback).

**Level 3:** Performance optimization: container startup is slow (5-30s). Use static containers (`static PostgreSQLContainer`) to share across test methods in a class — one startup per class. Use `withReuse(true)` to share containers across test classes — one startup per JVM run. Spring Boot 3.1+: `@ServiceConnection` annotation automatically configures datasource from container properties without `@DynamicPropertySource`. Parallel test safety: each test uses `@Transactional` rollback or unique schemas to isolate when sharing a container.

**Level 4:** Testcontainers and CI: Docker daemon must be available in CI. GitHub Actions: Docker is available by default. Kubernetes-based CI (Jenkins on k8s): requires Docker-in-Docker (DinD) or a Docker socket mount — both have security implications. Alternative: Ryuk (Testcontainers cleanup service) ensures containers are removed even if tests crash. Production-parity principle: if production runs PostgreSQL 15, test with PostgreSQL 15 container — never test with a different version. Schema migration testing: run Flyway/Liquibase migrations inside the test container before tests — ensures migrations work against the real DB engine.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              TESTCONTAINERS LIFECYCLE                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  JUnit: test class loaded                               │
│    → @Container → Testcontainers starts container       │
│    → docker pull postgres:15 (if not cached)            │
│    → docker run -p 5432:{random-port} postgres:15       │
│    → wait for health check (JDBC connection succeeds)   │
│                                                          │
│  @DynamicPropertySource: sets spring.datasource.url     │
│    → points to localhost:{random-port}                  │
│                                                          │
│  Tests run against real PostgreSQL                      │
│                                                          │
│  All tests complete:                                    │
│    → docker stop + docker rm (Ryuk cleanup)             │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Spring Boot app: UserService with PostgreSQL

Test strategy (with Testcontainers):
  Unit tests: Mockito, no container (fast)
  Integration tests: Testcontainers PostgreSQL (real SQL)

Integration test run:
  1. Maven: mvn test
  2. JUnit starts UserRepositoryTest class
  3. @Container: docker run postgres:15 → ready in 8s
  4. @DynamicPropertySource: datasource.url = jdbc:postgresql://localhost:54321/test
  5. Flyway runs migrations against test PostgreSQL
  6. @BeforeEach: truncate tables
  7. @Test saveUser(): INSERT + SELECT → PASS (real SQL, real constraints)
  8. @Test duplicateEmail(): INSERT twice → DataIntegrityViolationException PASS
  9. All 20 tests run → container stopped
  10. Total time: 12s (8s container start + 4s tests)

vs H2 alternative: 2s but misses PostgreSQL-specific behavior
vs shared DB: non-deterministic, requires network
```

---

### 💻 Code Example

```java
// Spring Boot 3.1+ with @ServiceConnection (cleanest approach)
@SpringBootTest
@Testcontainers
class OrderRepositoryTest {

    @Container
    @ServiceConnection  // auto-configures datasource — no @DynamicPropertySource needed
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired OrderRepository repo;

    @Test
    @Transactional  // auto-rollback after test
    void findByStatus_returnsMatchingOrders() {
        repo.save(new Order(UUID.randomUUID(), PENDING, BigDecimal.valueOf(50)));
        repo.save(new Order(UUID.randomUUID(), CONFIRMED, BigDecimal.valueOf(75)));

        List<Order> pending = repo.findByStatus(PENDING);
        assertThat(pending).hasSize(1);
        assertThat(pending.get(0).getTotal()).isEqualByComparingTo("50");
    }

    @Test
    @Transactional
    void jsonb_queryWorks() {
        // This fails with H2! PostgreSQL-specific JSONB query
        repo.save(new Order(UUID.randomUUID(), PENDING, BigDecimal.valueOf(100),
            Map.of("source", "mobile")));  // stored as JSONB

        List<Order> mobileOrders = repo.findByMetadataSource("mobile");
        assertThat(mobileOrders).hasSize(1);
    }
}
```

---

### ⚖️ Comparison Table

|                     | H2 In-Memory           | Testcontainers            | Shared Dev DB         |
| ------------------- | ---------------------- | ------------------------- | --------------------- |
| Isolation           | Good (per-JVM)         | Excellent (per-run)       | Poor (shared)         |
| Production parity   | Low (different engine) | Exact (same Docker image) | High                  |
| Speed               | Fast (no startup)      | Medium (8-30s startup)    | Fast                  |
| CI setup            | Zero                   | Docker required           | Network access needed |
| Dialect differences | High risk              | Zero risk                 | Zero risk             |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| "Testcontainers requires a running Docker daemon" | Yes — this is a CI requirement; Docker is available in GitHub Actions, GitLab CI by default |
| "Use Testcontainers for every unit test"          | Testcontainers is for integration tests; unit tests should use mocks/fakes                  |
| "withReuse=true makes tests non-isolated"         | Reuse containers, but isolate data with @Transactional or TRUNCATE in @BeforeEach           |

---

### 🚨 Failure Modes & Diagnosis

**1. Container Starts Too Slowly in CI → Test Timeout**

Cause: Docker image not cached in CI; slow CI network.
**Fix:** Pre-pull image in CI warm-up step. Use `withStartupTimeout(Duration.ofMinutes(2))`.

**2. Tests Pass Locally, Fail in CI**

Cause: Local Docker Desktop vs. CI Linux Docker have different behavior (usually file permissions or networking).
**Fix:** Test with `docker run` in CI to replicate locally. Check if CI uses Docker-in-Docker (privilege issues).

---

### 🔗 Related Keywords

- **Prerequisites:** Docker, Integration Test
- **Related:** WireMock, H2 Database, Spring Boot Test, Flyway, Liquibase

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Real Docker containers for integration  │
│              │ tests — same engine as production       │
├──────────────┼───────────────────────────────────────────┤
│ ANNOTATIONS  │ @Testcontainers, @Container,            │
│              │ @ServiceConnection (Boot 3.1+)          │
├──────────────┼───────────────────────────────────────────┤
│ LIFECYCLE    │ static → per-class; instance → per-test  │
├──────────────┼───────────────────────────────────────────┤
│ VS H2        │ No dialect differences; JSONB, native   │
│              │ queries, extensions all work            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Real service, real behavior, no mess"  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Testcontainers' `withReuse(true)` flag keeps the container alive across test class runs in the same JVM session — dramatically reducing startup overhead. But it requires careful test isolation since state can leak between test classes. Describe the tradeoffs: (1) when `withReuse=true` is safe (read-only tests, tests that explicitly TRUNCATE before each test class), (2) the `@DirtiesContext` + Testcontainers interaction (context restart reuses or restarts the container?), (3) the `TC_REUSE_ENABLE=true` environment variable for CI reuse, and (4) the "Testcontainers Desktop" tool that enables container reuse in development — and why this is different from CI reuse.

**Q2.** Testcontainers for microservice integration tests: you have OrderService that calls PaymentService (HTTP) and publishes to Kafka. You could use: (A) WireMock stub for PaymentService + Testcontainers Kafka; (B) Testcontainers for both PaymentService (as a Docker container) and Kafka; (C) Mock PaymentService at code level + Testcontainers Kafka. For each: what does the test verify, what can it NOT verify, and what is the test execution time cost? Which approach would you choose for the critical path of order placement, and why?
