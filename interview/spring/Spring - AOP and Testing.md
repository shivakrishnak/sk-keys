---
layout: default
title: "Spring - AOP and Testing"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 8
permalink: /interview/spring/aop-and-testing/
topic: Spring
subtopic: AOP and Testing
keywords:
  - Spring AOP
  - Spring Testing
  - Spring WebFlux
difficulty_range: mixed
status: in-progress
version: 3
---

**Keywords covered in this file:**

- [Spring AOP](#spring-aop)
- [Spring Testing](#spring-testing)
- [Spring WebFlux](#spring-webflux)

# Spring AOP

**TL;DR** - Spring AOP provides aspect-oriented programming through proxy-based interception, enabling cross-cutting concerns like logging, security, and transactions to be separated from business logic.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT AOP:**
Every service method has the same boilerplate: start transaction, check authorization, log entry, execute business logic, log exit, commit transaction, handle exceptions. You copy-paste this into 200 methods. When the logging format changes, you modify 200 files. Cross-cutting concerns pollute every business method.

**THE BREAKING POINT:**
Transaction management, security checks, logging, metrics, and caching all wrap business logic. Without AOP, these concerns tangle with the core code, making methods 80% infrastructure and 20% business logic.
---

### ⚙️ How It Works

```
WITHOUT AOP:
public void transferMoney(Account a, Account b) {
  log.info("Starting transfer");      // logging
  if (!auth.check(user)) throw ...;   // security
  tx.begin();                         // transaction
  // actual business logic (2 lines)
  a.debit(amount);
  b.credit(amount);
  tx.commit();                        // transaction
  metrics.record("transfer");         // metrics
  log.info("Transfer complete");      // logging
}

WITH AOP:
@Transactional        // aspect handles tx
@Secured("ROLE_ADMIN") // aspect handles auth
@Timed                 // aspect handles metrics
public void transferMoney(Account a, Account b) {
  a.debit(amount);    // pure business logic
  b.credit(amount);
}
```

**Core concepts:**

| Term           | Meaning                                      | Example                                |
| -------------- | -------------------------------------------- | -------------------------------------- |
| **Aspect**     | Module encapsulating a cross-cutting concern | `@Aspect` class LoggingAspect          |
| **Join Point** | Point in execution where aspect can apply    | Method execution                       |
| **Advice**     | Action taken at a join point                 | `@Before`, `@After`, `@Around`         |
| **Pointcut**   | Expression selecting join points             | `execution(* com.app.service.*.*(..))` |
| **Weaving**    | Linking aspects with target objects          | At runtime (Spring uses proxies)       |
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### First Principles

**CORE INVARIANTS:**

1. Cross-cutting concerns should be defined once, applied to many join points
2. Business logic must not know about the aspects applied to it
3. The proxy sits between the caller and the target - it intercepts the call

**ESSENTIAL vs ACCIDENTAL:**

- **Essential:** Separation of cross-cutting concerns from business logic
- **Accidental:** JDK dynamic proxy vs CGLIB proxy (implementation detail, not concept)
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - Anyone:** AOP lets you add behavior (logging, security, transactions) to methods without modifying them. It's like a wrapper that runs code before/after your methods automatically.

**Level 2 - Junior:** Spring creates a proxy around your bean. When someone calls a method, they actually call the proxy, which runs the advice (before/after/around), then delegates to the real method. `@Transactional` is the most common aspect.

**Level 3 - Mid-level:** Spring uses JDK dynamic proxies for interfaces and CGLIB for concrete classes. Because it's proxy-based: (1) self-invocation bypasses the proxy (calling `this.method()` inside the same class skips AOP), (2) only public methods can be advised, (3) final classes/methods can't be proxied by CGLIB.

**Level 4 - Senior+:** The proxy limitation is the most important thing to understand. When a `@Transactional` method calls another `@Transactional` method in the same class, the inner method's transaction annotation is ignored because the call doesn't go through the proxy. Solutions: extract to a separate bean, use `AopContext.currentProxy()`, or use AspectJ compile-time weaving for full AOP without proxy limitations.
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

```java
// BAD: Cross-cutting concerns tangled with logic
@Service
public class OrderService {
    public Order createOrder(OrderRequest req) {
        long start = System.currentTimeMillis();
        log.info("Creating order for {}",
            req.getUserId());
        try {
            // business logic buried in boilerplate
            Order order = processOrder(req);
            log.info("Order created in {}ms",
                System.currentTimeMillis() - start);
            metrics.increment("orders.created");
            return order;
        } catch (Exception e) {
            log.error("Order failed", e);
            metrics.increment("orders.failed");
            throw e;
        }
    }
}

// GOOD: AOP separates concerns
@Aspect
@Component
public class LoggingAspect {
    @Around("execution(* com.app.service.*.*(..))")
    public Object logMethod(
            ProceedingJoinPoint joinPoint)
            throws Throwable {
        String method =
            joinPoint.getSignature().getName();
        log.info("Entering {}", method);
        long start = System.nanoTime();
        try {
            Object result = joinPoint.proceed();
            log.info("{} completed in {}ms",
                method,
                (System.nanoTime() - start)
                    / 1_000_000);
            return result;
        } catch (Exception e) {
            log.error("{} failed: {}", method,
                e.getMessage());
            throw e;
        }
    }
}

@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest req) {
        // pure business logic - no boilerplate
        return processOrder(req);
    }
}
```
---

### The Self-Invocation Trap (Most Asked Interview Question)

```java
// BAD: Self-invocation bypasses proxy
@Service
public class UserService {
    @Transactional
    public void registerUser(User user) {
        saveUser(user);
        sendWelcomeEmail(user); // Direct call!
    }

    @Transactional(propagation = REQUIRES_NEW)
    public void sendWelcomeEmail(User user) {
        // This annotation is IGNORED because
        // registerUser() called it directly
        // (this.sendWelcomeEmail), not through
        // the proxy
        emailService.send(user.getEmail());
    }
}

// GOOD: Extract to separate bean
@Service
public class UserService {
    private final EmailService emailService;

    @Transactional
    public void registerUser(User user) {
        saveUser(user);
        emailService.sendWelcomeEmail(user);
        // Goes through EmailService's proxy
    }
}

@Service
public class EmailService {
    @Transactional(propagation = REQUIRES_NEW)
    public void sendWelcomeEmail(User user) {
        // Now works - called through proxy
        send(user.getEmail());
    }
}
```
---

### Advice Types

| Type            | Annotation        | Runs when               | Use case               |
| --------------- | ----------------- | ----------------------- | ---------------------- |
| Before          | `@Before`         | Before method           | Auth check, validation |
| After Returning | `@AfterReturning` | After successful return | Audit log              |
| After Throwing  | `@AfterThrowing`  | After exception         | Error alerting         |
| After (Finally) | `@After`          | Always after method     | Cleanup                |
| Around          | `@Around`         | Wraps entire method     | Timing, caching, tx    |
---

### Pointcut Expression Syntax

```java
// Match all methods in service package
@Pointcut("execution(* com.app.service.*.*(..))")

// Match methods with @Transactional
@Pointcut("@annotation(Transactional)")

// Match all public methods
@Pointcut("execution(public * *(..))")

// Combine with && || !
@Pointcut("execution(* com.app.service.*.*(..)) "
    + "&& !execution(* *.get*(..))")
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Spring AOP is proxy-based: self-invocation (`this.method()`) bypasses the proxy
2. `@Transactional`, `@Secured`, `@Cacheable` are all AOP-powered aspects
3. JDK proxy for interfaces, CGLIB for concrete classes; neither works on `final` or `private`

**Interview one-liner:**
"Spring AOP uses proxy-based interception to separate cross-cutting concerns from business logic - the critical limitation is self-invocation bypasses the proxy, which is why @Transactional on a method called by another method in the same class is silently ignored."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

Spring's `@Transactional` is the most widely used AOP feature, yet most developers don't realize it's AOP at all. When you see `@Transactional` silently failing, the root cause is almost always the self-invocation trap - and it's one of the top 5 most common Spring bugs in production, often going undetected for months because the code appears to work (it just doesn't have transaction boundaries where you expect them).
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Spring AOP. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: Explain how Spring AOP works under the hood. Why does self-invocation break @Transactional?**

_Why they ask:_ Tests understanding of the proxy mechanism, not just annotation usage.

**Answer:**
When Spring creates a bean with AOP advice, it wraps it in a proxy (JDK dynamic proxy for interfaces, CGLIB subclass for concrete classes). External callers get the proxy, not the real object. The proxy intercepts the call, runs advice (like starting a transaction), then delegates to the real method.

Self-invocation breaks this because when a method calls `this.anotherMethod()`, `this` refers to the actual object, not the proxy. The call goes directly to the target without interception:

```
External call:
  Caller -> Proxy -> Advice -> Target.method()

Self-invocation:
  Target.method1() -> this.method2()  // bypasses proxy
  (Advice on method2 is never triggered)
```

Solutions: (1) Extract the called method to a separate bean, (2) Inject the proxy via `@Lazy` self-injection, (3) Use `AopContext.currentProxy()` (requires `exposeProxy = true`), (4) Use AspectJ compile-time weaving.

**Q2: What's the difference between Spring AOP and full AspectJ? When would you use each?**

_Why they ask:_ Tests architectural decision-making.

**Answer:**
Spring AOP is proxy-based, limited to method execution join points, and works only on Spring beans. AspectJ does compile-time or load-time weaving, supports field access, constructor calls, and static methods, and works on any Java class.

Use Spring AOP (95% of cases): standard cross-cutting concerns on Spring beans - logging, transactions, security, caching. Use AspectJ: when you need to advise non-Spring objects, private methods, constructors, or field access. Performance-critical paths where proxy overhead matters. Libraries that require weaving into third-party code.

**Q3: How do you decide the order when multiple aspects apply to the same method?**

_Why they ask:_ Tests production experience with real multi-aspect scenarios.

**Answer:**
Use `@Order(n)` on the aspect class - lower numbers run first (outermost). For `@Around` advice, the lowest-order aspect wraps everything:

```
@Order(1) SecurityAspect  -> checks auth
  @Order(2) TransactionAspect -> starts tx
    @Order(3) LoggingAspect -> logs
      -> actual method
    <- LoggingAspect
  <- TransactionAspect commits/rollbacks
<- SecurityAspect
```

Without explicit ordering, the order is undefined. In production, the typical order is: Security (1) -> Transaction (2) -> Logging/Metrics (3).

**Q4: You have a @Cacheable method that's returning stale data after cache eviction. What's going wrong?**

_Why they ask:_ Tests debugging skills with AOP-related caching issues.

**Answer:**
Most likely self-invocation. If the method with `@Cacheable` is called from within the same class, the cache proxy is bypassed and the method always executes. Check: (1) Is the caller in the same class? Extract to a separate service bean. (2) Is the cache key correct? Duplicate keys return wrong cached values. (3) Is the cache manager configured? Missing `@EnableCaching` means all cache annotations are silently ignored. (4) Is the return type serializable? Some cache implementations require serializable values. (5) Is cache eviction happening in the right cache name/key?
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Spring Testing

**TL;DR** - Spring provides a layered testing framework with annotations like `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, and `@MockBean` that load only the context slices needed for each test type.
---

### 🔥 The Problem This Solves

Testing a Spring application without the framework's support means manually constructing beans, wiring dependencies, setting up embedded databases, and configuring mock servers. A simple controller test would require bootstrapping the entire application context.
---

### Testing Pyramid in Spring

```
            /  E2E  \     @SpringBootTest
           / (full)  \    + TestRestTemplate
          /____________\
         / Integration  \  @WebMvcTest
        /  (sliced ctx)  \ @DataJpaTest
       /__________________\
      /     Unit Tests      \  No Spring context
     /  Mockito + JUnit 5    \ Plain POJOs
    /__________________________\
```
---

### Test Slice Annotations

| Annotation        | What it loads                | Use for                   |
| ----------------- | ---------------------------- | ------------------------- |
| `@SpringBootTest` | Full application context     | Integration/E2E tests     |
| `@WebMvcTest`     | Controllers, filters, advice | REST controller tests     |
| `@DataJpaTest`    | JPA repos, EntityManager, H2 | Repository/query tests    |
| `@WebFluxTest`    | WebFlux controllers          | Reactive controller tests |
| `@JsonTest`       | Jackson ObjectMapper         | JSON serialization tests  |
| `@RestClientTest` | RestTemplate/WebClient       | HTTP client tests         |
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

```java
// UNIT TEST: No Spring context needed
class OrderServiceTest {
    @Mock OrderRepository orderRepo;
    @Mock PaymentService paymentService;
    @InjectMocks OrderService orderService;

    @Test
    void shouldCreateOrder() {
        when(orderRepo.save(any()))
            .thenReturn(testOrder());
        Order result =
            orderService.create(testRequest());
        assertThat(result.getStatus())
            .isEqualTo("CREATED");
        verify(paymentService).charge(any());
    }
}

// CONTROLLER TEST: @WebMvcTest (sliced context)
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired MockMvc mockMvc;
    @MockBean OrderService orderService;

    @Test
    void shouldReturn201() throws Exception {
        when(orderService.create(any()))
            .thenReturn(testOrder());
        mockMvc.perform(post("/orders")
            .contentType(APPLICATION_JSON)
            .content("{\"item\":\"book\"}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id")
                .value("ORD-001"));
    }
}

// REPOSITORY TEST: @DataJpaTest (H2 in-memory)
@DataJpaTest
class OrderRepositoryTest {
    @Autowired OrderRepository repo;
    @Autowired TestEntityManager em;

    @Test
    void shouldFindByStatus() {
        em.persist(new Order("PENDING"));
        em.persist(new Order("SHIPPED"));
        em.flush();
        List<Order> pending =
            repo.findByStatus("PENDING");
        assertThat(pending).hasSize(1);
    }
}

// FULL INTEGRATION: @SpringBootTest
@SpringBootTest(
    webEnvironment = RANDOM_PORT)
class OrderIntegrationTest {
    @Autowired TestRestTemplate restTemplate;

    @Test
    void shouldCreateAndRetrieveOrder() {
        ResponseEntity<Order> response =
            restTemplate.postForEntity(
                "/orders",
                testRequest(),
                Order.class);
        assertThat(response.getStatusCode())
            .isEqualTo(HttpStatus.CREATED);
    }
}
```
---

### @MockBean vs @Mock

```java
// @Mock (Mockito) - no Spring context
// Use in unit tests
@ExtendWith(MockitoExtension.class)
class ServiceTest {
    @Mock PaymentService paymentService;
    // Manually inject into the class under test
}

// @MockBean (Spring) - replaces bean in context
// Use in @WebMvcTest, @SpringBootTest
@WebMvcTest(OrderController.class)
class ControllerTest {
    @MockBean OrderService orderService;
    // Replaces real OrderService bean in context
}
```

**Key difference:** `@MockBean` pollutes the application context cache. Each unique combination of `@MockBean` creates a new context, slowing down your test suite. Prefer `@Mock` with unit tests where possible.
---

### TestContainers (Real Database Testing)

```java
@SpringBootTest
@Testcontainers
class OrderRepositoryIT {
    @Container
    static PostgreSQLContainer<?> postgres =
        new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb");

    @DynamicPropertySource
    static void configureProperties(
            DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url",
            postgres::getJdbcUrl);
        registry.add("spring.datasource.username",
            postgres::getUsername);
        registry.add("spring.datasource.password",
            postgres::getPassword);
    }

    @Test
    void shouldPersistOrder() {
        // Tests against real PostgreSQL
    }
}
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Use test slices (`@WebMvcTest`, `@DataJpaTest`) instead of `@SpringBootTest` for fast, focused tests
2. `@MockBean` replaces a bean in the Spring context; `@Mock` is plain Mockito (faster, preferred for unit tests)
3. TestContainers gives you real database testing without H2 compatibility issues

**Interview one-liner:**
"I follow the testing pyramid: unit tests with Mockito for business logic, @WebMvcTest for controllers with MockMvc, @DataJpaTest with H2 for repository queries, and @SpringBootTest with TestContainers for integration - preferring test slices over full context loading for speed."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Spring Testing. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: Your test suite takes 15 minutes to run. How do you speed it up?**

_Why they ask:_ Tests production testing experience, not just annotation knowledge.

**Answer:**

1. **Audit `@SpringBootTest` usage.** Replace with test slices (`@WebMvcTest`, `@DataJpaTest`) where full context isn't needed. Each slice loads only relevant beans.

2. **Reduce context cache pollution.** Every unique `@MockBean` combination creates a new cached context. Consolidate mocking patterns: create a `@TestConfiguration` with common mocks instead of per-test `@MockBean`.

3. **Move to unit tests.** If a test only validates business logic, it doesn't need Spring at all. Use `@Mock` + `@InjectMocks` with Mockito. These run in milliseconds.

4. **Parallelize.** Add `spring.test.constructor.autowire.mode=all` and enable JUnit 5 parallel execution. Ensure tests don't share state.

5. **Use `@DirtiesContext` sparingly.** It forces context reload. Instead, clean up test data explicitly with `@Sql` or `@Transactional` (auto-rollback).

6. **Share TestContainers.** Use `@Container` with `static` to share a single container across all tests in a class, or use Singleton containers across the suite.

**Q2: What's the difference between `@Transactional` on a test method vs in production code?**

_Why they ask:_ Tests understanding of test transaction behavior.

**Answer:**
In production, `@Transactional` commits on success and rolls back on exception. In tests, `@Transactional` **always rolls back** by default, regardless of success. This auto-cleanup ensures test isolation - each test starts with a clean database. If you need a test to actually commit (rare), use `@Commit` or `@Rollback(false)`.

Caveat: `@Transactional` test rollback only works with a single datasource and embedded transactions. If your code spawns a new thread, calls an external service, or uses `REQUIRES_NEW` propagation, those side effects won't roll back.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Spring WebFlux

**TL;DR** - Spring WebFlux is Spring's reactive web framework built on Project Reactor, using non-blocking I/O to handle high-concurrency workloads with fewer threads than the traditional servlet model.
---

### 🔥 The Problem This Solves

A traditional Spring MVC application uses one thread per request. With 500 concurrent requests, you need 500 threads. Each thread consumes ~1MB of stack memory. At 10,000 concurrent connections (chat apps, IoT, SSE streams), you run out of threads or memory.

WebFlux uses an event-loop model (like Node.js) with a small fixed thread pool (typically CPU cores x 2), handling thousands of concurrent connections without thread-per-request overhead.
---

### MVC vs WebFlux

```
SPRING MVC (thread-per-request):
[Request 1] -> [Thread-1] -> blocks on DB -> waits -> responds
[Request 2] -> [Thread-2] -> blocks on DB -> waits -> responds
[Request 3] -> [Thread-3] -> blocks on DB -> waits -> responds
  (200 threads for 200 concurrent requests)

SPRING WEBFLUX (event-loop):
[Request 1] -\
[Request 2] --> [Event Loop, 4 threads] -> non-blocking I/O
[Request 3] -/
  (4 threads for thousands of concurrent requests)
```

| Aspect         | Spring MVC           | Spring WebFlux              |
| -------------- | -------------------- | --------------------------- |
| Threading      | Thread-per-request   | Event loop                  |
| I/O model      | Blocking             | Non-blocking                |
| Reactive types | None                 | Mono / Flux                 |
| Server         | Tomcat, Jetty        | Netty, Undertow             |
| JDBC           | Supported            | Use R2DBC instead           |
| Debugging      | Stack traces         | Harder (async)              |
| Best for       | CRUD APIs, form apps | High-concurrency, streaming |
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

```java
// Spring MVC (blocking)
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    return userRepository.findById(id) // blocks
        .orElseThrow();
}

// Spring WebFlux (non-blocking)
@GetMapping("/users/{id}")
public Mono<User> getUser(@PathVariable Long id) {
    return userRepository.findById(id) // non-blocking
        .switchIfEmpty(
            Mono.error(new NotFoundException()));
}

// Streaming endpoint (WebFlux only)
@GetMapping(value = "/events",
    produces = TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<String>> streamEvents() {
    return Flux.interval(Duration.ofSeconds(1))
        .map(seq -> ServerSentEvent.<String>builder()
            .id(String.valueOf(seq))
            .data("heartbeat-" + seq)
            .build());
}
```
---

### When NOT to Use WebFlux

1. **Your I/O is mostly JDBC:** Traditional JDBC is blocking. WebFlux with JDBC wastes the event loop. Use R2DBC or stay with MVC.
2. **Simple CRUD APIs:** WebFlux adds complexity for no benefit at < 1000 concurrent connections.
3. **Team isn't ready:** Reactive programming has a steep learning curve. Debugging reactive chains is significantly harder.
4. **Blocking libraries:** If any library in your stack blocks (e.g., synchronous HTTP client, JDBC), it blocks the event loop thread and kills performance for all requests.
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. WebFlux = non-blocking event-loop model; MVC = blocking thread-per-request
2. Use WebFlux for high-concurrency (10K+ connections), streaming, SSE; stick with MVC for standard CRUD
3. Never mix blocking calls (JDBC, Thread.sleep) in WebFlux code - it blocks the event loop

**Interview one-liner:**
"Spring WebFlux uses Project Reactor's non-blocking event-loop model to handle thousands of concurrent connections with a small thread pool - I recommend it for streaming/SSE workloads, but for typical CRUD APIs with JDBC, MVC with virtual threads is simpler and equally performant."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Spring WebFlux. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]
