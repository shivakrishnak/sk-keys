---
layout: default
title: "Spring Boot Testing"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /spring/spring-boot-testing/
id: SPR-058
category: Spring Core
difficulty: ★★☆
depends_on: JUnit, Mockito, Spring Context
used_by: Integration Testing, Slice Testing, CI/CD
related: "@MockBean, @WebMvcTest, TestContainers"
tags:
  - spring
  - testing
  - java
  - intermediate
---

# SPR-058 - Spring Boot Testing

⚡ TL;DR - Spring Boot Testing provides slice annotations (`@WebMvcTest`, `@DataJpaTest`) that load only the relevant context slice for fast focused tests, plus `@SpringBootTest` for full integration tests - eliminating the need to manually wire test contexts.

| #410            | Category: Spring Core                     | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | JUnit, Mockito, Spring Context            |                 |
| **Used by:**    | Integration Testing, Slice Testing, CI/CD |                 |
| **Related:**    | @MockBean, @WebMvcTest, TestContainers    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Writing an integration test for a Spring REST controller without Spring Boot Testing: manually create `AnnotationConfigWebApplicationContext`, register your controller class, configure a `MockMvc` bean, set up a test dispatcher servlet, register your `@ExceptionHandler`, configure Jackson `ObjectMapper`, register security filters, configure message converters... 80 lines of test setup before testing a single endpoint.

**THE BREAKING POINT:**
The test setup code becomes larger than the test itself. When the production context configuration changes, test setup breaks. Teams stop writing integration tests because they're too hard to maintain.

**THE INVENTION MOMENT:**
"This is exactly why Spring Boot Test slices were created."

---

### 📘 Textbook Definition

**Spring Boot Testing** is a module (`spring-boot-test`, `spring-boot-test-autoconfigure`) that simplifies testing Spring Boot applications. Key features: `@SpringBootTest` loads the full application context for end-to-end integration tests; slice annotations (`@WebMvcTest`, `@DataJpaTest`, `@WebFluxTest`, `@RestClientTest`, `@JsonTest`) load only the application context slice relevant to the test (e.g., only web layer, only persistence layer); `@MockBean` and `@SpyBean` integrate Mockito mocks into the Spring context, replacing real beans for isolation; `TestRestTemplate` and `MockMvc` provide HTTP-level testing without a running server or with one respectively. Spring Boot Test builds on JUnit 5 and uses `@ExtendWith(SpringExtension.class)` (included automatically in slice annotations).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`@WebMvcTest` loads just your controller layer; `@DataJpaTest` loads just your database layer; `@SpringBootTest` loads everything - choose the smallest slice that covers your test.

**One analogy:**

> Testing a car: you don't put the full car on a dynamometer to test if the radio works. You test the radio in isolation on a bench. Spring Boot slices are test benches - `@WebMvcTest` is the web layer bench, `@DataJpaTest` is the database bench. `@SpringBootTest` is the full car test on the road.

**One insight:**
The smallest context that covers your test assertion is the right choice. Smaller contexts start faster, have fewer moving parts to mock, and fail more meaningfully when something breaks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Slice annotations filter `@ComponentScan` and auto-configuration to only include components relevant to the tested layer.
2. `@MockBean` creates a Mockito mock and registers it as a Spring bean, replacing any existing bean of the same type in the test context.
3. `@SpringBootTest` with no parameters loads the full application context - same configuration as production, with the selected `WebEnvironment`.

**DERIVED DESIGN:**
Each slice annotation is annotated with `@AutoConfigureX` annotations that restrict which auto-configurations are active. `@WebMvcTest` activates: `MockMvcAutoConfiguration`, `SpringSecurityAutoConfiguration` (if on classpath), `WebMvcAutoConfiguration`. It does NOT activate: `DataSourceAutoConfiguration`, `JpaRepositoriesAutoConfiguration`. So a `@WebMvcTest` for `OrderController` loads the controller, its `@ControllerAdvice`, security, and MVC config - but repositories, services, and datasources must be mocked with `@MockBean`.

This is intentional: the slice tests the web layer in isolation. Slow components (database, external services) are mocked. Tests run in milliseconds.

**THE TRADE-OFFS:**
**Gain:** Fast test execution; focused failure messages; no accidental cross-layer dependencies in tests; realistic serialization/deserialization testing without a running server.
**Cost:** Slices don't test the full wiring - a misconfiguration between layers is only caught in `@SpringBootTest`. `@MockBean` context caching issue - Spring creates a new context for each unique set of mocks, potentially creating many contexts in a large test suite.

---

### 🧪 Thought Experiment

**SETUP:**
A `OrderController` calls `OrderService` which calls `OrderRepository`. You want to test that `POST /orders` with invalid input returns 400 Bad Request.

**WITH `@SpringBootTest`:**
Full context loaded: database connection required, all auto-configurations apply, HikariCP pool started. Test takes 3–5 seconds to start. Test fails with `ConnectionException` if DB is not available. You're testing database connectivity when you only want to test HTTP validation.

**WITH `@WebMvcTest`:**
Only web layer loaded. `OrderService` must be `@MockBean`. No database, no HikariCP. Test starts in 0.3 seconds. Mocked `OrderService` never called (validation fails before reaching service). Test is fast, focused, and doesn't require a database. The test is about input validation - `@WebMvcTest` is exactly the right scope.

**THE INSIGHT:**
The right test scope is the smallest context that can prove the assertion. For validation testing: `@WebMvcTest`. For query testing: `@DataJpaTest`. For end-to-end flows: `@SpringBootTest`. Using a larger scope than needed makes tests slow and fragile.

---

### 🧠 Mental Model / Analogy

> Spring Boot test annotations are like different lab setups. `@WebMvcTest` is a chemistry lab (test chemical reactions - HTTP request/response). `@DataJpaTest` is a biology lab (test organisms - database queries). `@SpringBootTest` is a full environment chamber (test everything together). You use the right lab for the experiment. You don't test a chemical reaction in the biology lab - wrong tools, irrelevant complications.

- "Chemistry lab" → `@WebMvcTest` - just HTTP and controller layer
- "Biology lab" → `@DataJpaTest` - just JPA and persistence layer
- "Full environment chamber" → `@SpringBootTest` - full application
- "Lab equipment" → `MockMvc`, `TestEntityManager`, `TestRestTemplate`
- "Fake specimens" → `@MockBean` replacing real dependencies

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring Boot Testing gives you special annotations that set up just the right part of your application for testing - so you can test the web layer without needing a database, or test database queries without starting a web server.

**Level 2 - How to use it (junior developer):**
Use `@WebMvcTest(OrderController.class)` to test a controller with `MockMvc`. Add `@MockBean` for every dependency the controller needs. Use `mockMvc.perform(get("/orders"))` to simulate HTTP requests. Use `@DataJpaTest` to test repositories - Spring auto-configures an in-memory H2 database. Use `@SpringBootTest(webEnvironment = RANDOM_PORT)` for full integration tests with `TestRestTemplate`.

**Level 3 - How it works (mid-level engineer):**
`@WebMvcTest` is meta-annotated with `@BootstrapWith(WebMvcTestContextBootstrapper.class)` which sets the `WebApplicationContextLoader`. It includes `@OverrideAutoConfiguration(enabled=false)` (disables all auto-configs by default) and `@AutoConfigureWebMvc`, `@AutoConfigureMockMvc`, `@AutoConfigureCache`. Only `@Controller`, `@ControllerAdvice`, `@JsonComponent`, `Converter`, `Filter`, `WebMvcConfigurer`, and `HandlerMethodArgumentResolver` beans are scanned from your classpath. `@MockBean` is processed by `MockitoPostProcessor` which registers the mock in the `BeanDefinitionRegistry` before context initialization, so it's available for injection before any real bean is created.

**Level 4 - Why it was designed this way (senior/staff):**
The slice approach was introduced in Spring Boot 1.4 after the Spring team observed that test suites in the wild fell into two anti-patterns: "no integration tests at all" (too hard to write) or "only full `@SpringBootTest`" (too slow to run). The slice concept was the middle ground - meaningful integration coverage without the cost of the full context. The `@MockBean` context caching behavior (a new context per unique mock combination) is a deliberate trade-off: strict context isolation vs. context reuse. Large test suites that overuse `@MockBean` in different combinations can create O(N) contexts, slowing CI. Best practice: use a shared base test class with a fixed set of `@MockBean`s to maximize context reuse.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ @WebMvcTest CONTEXT LOADING                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  @WebMvcTest(OrderController.class)                     │
│    │                                                    │
│    ├── @BootstrapWith(WebMvcTestContextBootstrapper)    │
│    ├── @OverrideAutoConfiguration(enabled=false)        │
│    ├── @AutoConfigureWebMvc  → DispatcherServlet etc.  │
│    ├── @AutoConfigureMockMvc → MockMvc bean             │
│    └── @AutoConfigureCache                             │
│                                                         │
│  Components INCLUDED:                                   │
│    ✅ @Controller, @RestController                      │
│    ✅ @ControllerAdvice                                 │
│    ✅ @JsonComponent                                    │
│    ✅ WebMvcConfigurer, Converter                       │
│    ✅ Spring Security (if on classpath)                 │
│                                                         │
│  Components EXCLUDED:                                   │
│    ❌ @Service, @Repository, @Component                 │
│    ❌ DataSource, JPA, Hibernate                        │
│    ❌ @Async, @Scheduled                                │
│                                                         │
│  @MockBean OrderService                                 │
│    → Mockito mock registered as Spring bean             │
│    → replaces real OrderService (if any) in context     │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - `@WebMvcTest` for controller layer:**

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockBean OrderService orderService; // required - not in slice

    @Test
    void createOrder_validInput_returns201() throws Exception {
        OrderRequest request = new OrderRequest("product-1", 3);
        Order created = new Order("order-1", "product-1", 3);

        when(orderService.create(any(OrderRequest.class)))
            .thenReturn(created);

        mockMvc.perform(post("/api/orders")
                .contentType(APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value("order-1"))
            .andExpect(jsonPath("$.quantity").value(3));

        verify(orderService).create(any(OrderRequest.class));
    }

    @Test
    void createOrder_invalidInput_returns400() throws Exception {
        // quantity = 0 is invalid
        OrderRequest invalid = new OrderRequest("product-1", 0);

        mockMvc.perform(post("/api/orders")
                .contentType(APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(invalid)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors[0]")
                .value("quantity must be greater than 0"));

        // Service should NOT be called - validation fails before it
        verifyNoInteractions(orderService);
    }

    @Test
    @WithMockUser(roles = "USER")
    void listOrders_authenticated_returns200() throws Exception {
        when(orderService.findAll()).thenReturn(List.of());

        mockMvc.perform(get("/api/orders"))
            .andExpect(status().isOk());
    }
}
```

**Example 2 - `@DataJpaTest` for repository layer:**

```java
@DataJpaTest
// Spring auto-configures H2 in-memory DB + Hibernate
class OrderRepositoryTest {

    @Autowired TestEntityManager em;
    @Autowired OrderRepository orderRepository;

    @Test
    void findByCustomerId_returnsMatchingOrders() {
        // Arrange: use TestEntityManager (not repository) to set up data
        Customer customer = em.persistFlushFind(
            new Customer("cust-1", "Alice"));
        em.persistAndFlush(
            new Order(null, customer, "product-1", 2));
        em.persistAndFlush(
            new Order(null, customer, "product-2", 1));

        // Act
        List<Order> orders = orderRepository
            .findByCustomerId("cust-1");

        // Assert
        assertThat(orders).hasSize(2);
        assertThat(orders)
            .extracting(Order::getProductId)
            .containsExactlyInAnyOrder("product-1", "product-2");
    }

    @Test
    void findByCustomerId_noOrders_returnsEmpty() {
        List<Order> orders = orderRepository
            .findByCustomerId("unknown-customer");
        assertThat(orders).isEmpty();
    }
}
```

**Example 3 - `@SpringBootTest` full integration test with TestContainers:**

```java
@SpringBootTest(webEnvironment = RANDOM_PORT)
@Testcontainers
class OrderIntegrationTest {

    // Real PostgreSQL in Docker - eliminates H2 divergence
    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(
            DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username",
            postgres::getUsername);
        registry.add("spring.datasource.password",
            postgres::getPassword);
    }

    @Autowired TestRestTemplate restTemplate;

    @Test
    void createAndRetrieveOrder() {
        // Create
        OrderRequest request = new OrderRequest("product-1", 2);
        ResponseEntity<Order> created = restTemplate.postForEntity(
            "/api/orders", request, Order.class);
        assertThat(created.getStatusCode())
            .isEqualTo(HttpStatus.CREATED);
        String orderId = created.getBody().getId();

        // Retrieve
        ResponseEntity<Order> retrieved = restTemplate.getForEntity(
            "/api/orders/" + orderId, Order.class);
        assertThat(retrieved.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(retrieved.getBody().getId()).isEqualTo(orderId);
    }
}
```

---

### ⚖️ Comparison Table

| Annotation        | Context Loaded     | Speed        | Use For                               |
| ----------------- | ------------------ | ------------ | ------------------------------------- |
| `@WebMvcTest`     | Web layer only     | Fast (~0.3s) | Controller, validation, serialization |
| `@DataJpaTest`    | JPA + H2 only      | Fast (~0.5s) | Repository queries, entity mapping    |
| `@WebFluxTest`    | WebFlux layer only | Fast         | Reactive controllers                  |
| `@RestClientTest` | HTTP client only   | Fast         | RestTemplate / WebClient              |
| `@JsonTest`       | Jackson only       | Very fast    | JSON serialization/deserialization    |
| `@SpringBootTest` | Full context       | Slow (3–10s) | End-to-end, cross-layer integration   |

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                                                      |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `@SpringBootTest` is the most thorough and therefore always best | For unit-level concerns (validation, query logic), `@SpringBootTest` is slower and noisier; slice tests are more focused and faster                          |
| `@MockBean` in any test class reuses the same context            | Any unique combination of `@MockBean` types causes Spring to create a new context; overusing `@MockBean` creates a new context per test class                |
| `@DataJpaTest` tests against the same DB as production           | Default `@DataJpaTest` uses H2 in-memory - dialect differences can hide bugs; use `@AutoConfigureTestDatabase(replace=NONE)` + Testcontainers for accuracy   |
| `@WebMvcTest` loads all controllers                              | By default yes - specify `@WebMvcTest(MyController.class)` to load only the controller under test                                                            |
| `verifyNoInteractions(mock)` is redundant with assertion         | Not redundant - verifies the mock was called with expected arguments; a missing `verify()` means the service might not be called at all and you'd still pass |

---

### 🚨 Failure Modes & Diagnosis

**1. `@WebMvcTest` Failing with UnsatisfiedDependencyException**

**Symptom:** `UnsatisfiedDependencyException: No qualifying bean of type 'OrderService'`; test fails to start.

**Root Cause:** Controller has a `@Autowired OrderService` but `@WebMvcTest` doesn't load services - `@MockBean OrderService` is missing from the test class.

**Fix:**

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @MockBean OrderService orderService; // required!
    @MockBean AuditService auditService; // any other dependency
    // ...
}
```

**Diagnostic tip:** Error message "expected at least 1 bean which qualifies as autowire candidate" always means a missing `@MockBean` in a slice test.

---

**2. `@DataJpaTest` Passes but `@SpringBootTest` Fails (H2 vs PostgreSQL)**

**Symptom:** `@DataJpaTest` tests pass; identical query in `@SpringBootTest` with PostgreSQL fails with `PSQLException: syntax error`.

**Root Cause:** H2's dialect accepted a query that PostgreSQL doesn't - e.g., PostgreSQL-specific JSONB operations, native SQL syntax differences.

**Diagnostic:**

```bash
# Enable SQL logging in @DataJpaTest
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG
# Compare generated SQL with what PostgreSQL expects
```

**Fix:**

```java
// Replace H2 with real PostgreSQL via Testcontainers
@DataJpaTest
@AutoConfigureTestDatabase(replace = NONE) // don't use H2
@Testcontainers
class OrderRepositoryTest {
    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15");
    // ...
}
```

**Prevention:** For any non-trivial queries, use Testcontainers with the real database engine in `@DataJpaTest`.

---

**3. Slow Test Suite from Context Explosion**

**Symptom:** CI runs take 20+ minutes; `--info` shows "creating new ApplicationContext" 50+ times; JVM heap warnings.

**Root Cause:** Each test class has a different combination of `@MockBean` types, forcing Spring to create a separate context for each unique combination.

**Diagnostic:**

```bash
# Run tests with INFO logging and count context creations
./mvnw test -Dspring.test.context.cache.maxSize=100 2>&1 | \
  grep "Refreshing" | wc -l

# Ideal: 1 context per slice type
# Problem: many contexts = @MockBean variety
```

**Fix:**

```java
// GOOD: shared base classes with fixed @MockBean set
// All controller tests extend this - same mocks = same context
@WebMvcTest
abstract class ControllerTestBase {
    @MockBean OrderService orderService;
    @MockBean UserService userService;
    @MockBean AuditService auditService;
    // Add ALL mocks needed by ANY controller test here
}

// Test classes extend base - reuses cached context
class OrderControllerTest extends ControllerTestBase {
    // Only add test-specific setup, not more @MockBean
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JUnit` - Spring Boot Testing builds on JUnit 5; understand `@Test`, `@BeforeEach`, assertions first
- `Mockito` - `@MockBean` integrates Mockito mocks into Spring context; understand `when()`/`verify()` first
- `Spring Context` - slice testing loads partial application contexts; understand what the full context is

**Builds On This (learn these next):**

- `TestContainers` - the complement to `@DataJpaTest` for real-database testing; eliminates H2 divergence
- `Spring Boot Actuator` - test Actuator endpoints with `@SpringBootTest` for production-readiness verification
- `CI/CD` - fast slice tests enable test parallelization and sub-minute feedback loops in CI

**Alternatives / Comparisons:**

- `Arquillian` - Java EE equivalent for integration testing; more complex, less Spring-native
- `Pure Mockito unit tests` - don't load any Spring context; fastest but don't test Spring wiring
- `RestAssured` - alternative to MockMvc; works with running server (`@SpringBootTest(webEnvironment=RANDOM_PORT)`)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @WebMvcTest  │ Web layer only; @MockBean all services    │
│              │ Use: controllers, validation, security    │
├──────────────┼───────────────────────────────────────────┤
│ @DataJpaTest │ JPA + H2 only; @Autowired repository      │
│              │ Use: queries, entity mapping              │
├──────────────┼───────────────────────────────────────────┤
│ @SpringBoot  │ Full context; TestRestTemplate            │
│ Test         │ Use: cross-layer flows, wiring checks     │
├──────────────┼───────────────────────────────────────────┤
│ @MockBean    │ Mockito mock registered in Spring context  │
│              │ Required for slice tests' missing deps    │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Use smallest scope that tests your logic  │
│              │ @WebMvcTest > @DataJpaTest > @SpringBoot  │
├──────────────┼───────────────────────────────────────────┤
│ PERFORMANCE  │ Too many unique @MockBean combos = slow   │
│              │ Use shared base classes to reuse contexts │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Test the right layer with the right      │
│              │  slice - don't use a sledgehammer for     │
│              │  every nail"                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TestContainers → WireMock →               │
│              │ Contract Testing (Pact)                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A - System Interaction) A `@WebMvcTest` for `UserController` uses `@MockBean UserService`. The test passes in isolation. In the CI pipeline, the full test suite runs 50 test classes in parallel, each with different `@MockBean` combinations. The CI run takes 18 minutes despite each individual test taking under 1 second. Using your knowledge of Spring's test context cache, explain exactly why this happens and design a test class hierarchy structure that reduces context creation to 3 total contexts for the entire web layer test suite.

**Q2.** (TYPE C - Design Trade-off) A team debates: "Should we test the `OrderRepository` with `@DataJpaTest` and H2, or with `@SpringBootTest` + TestContainers using real PostgreSQL?" The H2 approach runs in 0.5s; the TestContainers approach runs in 8s per test class. List the three specific test scenarios where the H2 approach gives a false pass (test passes but production fails) and the two scenarios where it gives a false fail (test fails but production would pass). Based on these, when should each approach be used?
