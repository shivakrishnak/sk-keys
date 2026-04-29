---
layout: default
title: "Bean"
parent: "Spring Framework"
nav_order: 107
permalink: /spring/bean/
---

`#spring` `#internals` `#foundational`

⚡ TL;DR — A Bean is any object whose lifecycle (creation, wiring, and destruction) is managed by the Spring IoC container.

---

## 📘 Textbook Definition

In Spring, a **bean** is an object that is instantiated, assembled, and otherwise managed by the Spring IoC container. Beans are defined through configuration metadata — annotations (`@Component`, `@Bean`), XML, or Java configuration — and the container is responsible for their lifecycle, dependency injection, and scope management.

---

## 🟢 Simple Definition (Easy)

A Bean is simply a Java object that Spring knows about and takes care of. Instead of you writing `new MyService()`, Spring creates the `MyService` object and registers it as a bean — making it available throughout your application.

---

## 🔵 Simple Definition (Elaborated)

Most objects in a Spring application are beans — services, repositories, controllers, configuration classes. What makes an object a "bean" is that Spring created it (via `new` internally), holds a reference to it, has wired all its dependencies, and will clean it up on shutdown. You declare beans using `@Component` (and its specializations `@Service`, `@Repository`, `@Controller`) or `@Bean` factory methods in `@Configuration` classes.

---

## 🔩 First Principles Explanation

**Three ways to register a bean:**

```java
// 1. Component scanning — automatic (preferred for application classes)
@Service
public class UserService { }        // Spring finds via @ComponentScan

// 2. @Bean method — explicit (preferred for 3rd-party or configured objects)
@Configuration
public class AppConfig {
    @Bean
    public DataSource dataSource() { // Spring manages this DataSource bean
        return DataSourceBuilder.create().url("jdbc:h2:mem:test").build();
    }
}

// 3. XML (legacy — avoid in new projects)
// <bean id="userService" class="com.example.UserService"/>
```

**Bean vs. plain object:**

```
Regular Java Object        Spring Bean
──────────────────         ──────────────────────────
new MyService()            @Service MyService
Self-created               Container-created
No automatic DI            Dependencies auto-injected
No lifecycle hooks         @PostConstruct / @PreDestroy
No AOP                     AOP proxies applied
No scope management        Singleton / Prototype / Request etc.
```

---

## ❓ Why Does This Exist (Why Before What)

Without beans, every component must manage its own instantiation and dependencies. As applications grow, this creates a tightly coupled "new-new-new" mess. Beans let the container handle all object management; your code focuses only on business logic.

---

## 🧠 Mental Model / Analogy

> A Bean is like an **employee registered with HR (the container)**. HR hired them (instantiation), knows who they report to (dependencies), gave them an employee ID (`beanName`), assigned a role (scope), and will process their termination (destroy). Self-employed contractors (regular objects via `new`) have none of that management — they're invisible to HR.

---

## ⚙️ How It Works (Mechanism)

```
Config metadata scanned
        ↓
BeanDefinition created (blueprint: class, scope, constructor, lazy?)
        ↓
At startup (or first request for lazy): instantiated by container
        ↓
Dependencies injected
        ↓
BeanPostProcessors applied (AOP proxy wrapping etc.)
        ↓
@PostConstruct called
        ↓
BEAN IS LIVE — can be injected everywhere
        ↓
On shutdown: @PreDestroy → bean discarded
```

---

## 🔄 How It Connects (Mini-Map)

```
         [Bean] ← registered in
        ↙    ↘
[ApplicationContext]  [BeanFactory]
        ↓
  [Bean Lifecycle] → init → use → destroy
        ↓
  [Bean Scope] → determines how many instances exist
        ↓
  [DI] → beans injected into other beans
```

---

## 💻 Code Example

```java
// ── Declaring beans ───────────────────────────────────────────────────────────
@Service                     // stereotype: business logic
public class UserService { }

@Repository                  // stereotype: data access
public class UserRepository { }

@Controller                  // stereotype: web layer (MVC)
public class UserController { }

@Component                   // generic: anything else
public class EmailValidator { }

// ── Bean with dependencies ─────────────────────────────────────────────────────
@Service
public class OrderService {
    private final UserRepository repo;
    private final PaymentService payment;

    public OrderService(UserRepository repo, PaymentService payment) {
        this.repo = repo;            // both are beans injected by Spring
        this.payment = payment;
    }
}

// ── Programmatic bean declaration ──────────────────────────────────────────────
@Configuration
public class InfraConfig {
    @Bean
    @Scope("prototype")              // new instance per injection (see Bean Scope)
    public HttpClient httpClient() {
        return HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();
    }
}

// ── Inspecting beans at runtime ───────────────────────────────────────────────
@Autowired ApplicationContext ctx;

void listBeans() {
    Arrays.stream(ctx.getBeanDefinitionNames())
          .forEach(System.out::println);
}
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Every Java object is a bean | Only objects managed by the Spring container are beans |
| `@Component` and `@Bean` are the same | `@Component` marks a class; `@Bean` is a method-level factory declaration |
| Beans are always singletons | Default scope is singleton, but prototype/request/session are also common |
| Creating a bean with `new` makes it a Spring bean | Objects created with `new` are invisible to Spring — not beans |
| All beans are eagerly created | `@Lazy` defers creation; prototype beans are always lazy |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Mixing `new` and Spring beans**
```java
// Bad: this bypasses Spring — no AOP, no @Autowired in MyService
MyService s = new MyService(); // NOT a bean!

// Good: always get from container (via @Autowired)
@Autowired MyService myService;
```

**Pitfall 2: Singleton beans with mutable shared state**
```java
// Bad: singleton bean has mutable field — shared across all threads
@Service
public class CounterService {
    private int count = 0; // RACE CONDITION in multithreaded app!
    public void increment() { count++; }
}

// Fix: use AtomicInteger or thread-local state
private final AtomicInteger count = new AtomicInteger(0);
```

---

## 🔗 Related Keywords

- **[Bean Lifecycle](./108 — Bean Lifecycle.md)** — how Spring manages bean init to destroy
- **[Bean Scope](./109 — Bean Scope.md)** — singleton, prototype, request, session
- **[DI (Dependency Injection)](./104 — DI (Dependency Injection).md)** — how beans receive their dependencies
- **[BeanPostProcessor](./110 — BeanPostProcessor.md)** — how beans get customized after creation
- **[ApplicationContext](./105 — ApplicationContext.md)** — the container that holds all beans

---

## 📌 Quick Reference Card

```
+------------------------------------------------------------------+
| KEY IDEA    | Spring-managed object: created, wired, destroyed    |
+------------------------------------------------------------------+
| DECLARE VIA | @Component/@Service/@Repository or @Bean method    |
+------------------------------------------------------------------+
| DEFAULT     | Singleton — one instance shared across the app      |
+------------------------------------------------------------------+
| ONE-LINER   | "Any object whose lifecycle Spring controls"         |
+------------------------------------------------------------------+
| NEXT EXPLORE| Bean Lifecycle → Bean Scope → BeanPostProcessor     |
+------------------------------------------------------------------+
```

---

## 🧠 Think About This Before We Continue

**Q1.** What is the difference between `@Component` and `@Bean`? When would you use one over the other?

**Q2.** If a singleton bean holds a reference to a prototype-scoped bean, how many instances of the prototype bean will exist? Is this a problem?

**Q3.** Spring beans are by default not thread-safe. What strategies would you use to make a singleton bean safe for concurrent access?

