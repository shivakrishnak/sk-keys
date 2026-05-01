---
layout: default
title: "Singleton Pattern"
parent: "Design Patterns"
nav_order: 766
permalink: /design-patterns/singleton-pattern/
number: "766"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Dependency Injection Pattern"
used_by: "Configuration objects, Logger, Connection pools, Thread pools"
tags: #intermediate, #design-patterns, #creational, #oop, #concurrency
---

# 766 — Singleton Pattern

`#intermediate` `#design-patterns` `#creational` `#oop` `#concurrency`

⚡ TL;DR — **Singleton** ensures a class has only one instance throughout the application's lifetime and provides a global access point to it — useful for shared resources (config, logging, connection pools) but often overused and misunderstood as a pattern for global state.

| #766 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Dependency Injection Pattern | |
| **Used by:** | Configuration objects, Logger, Connection pools, Thread pools | |

---

### 📘 Textbook Definition

**Singleton** (GoF — "Design Patterns: Elements of Reusable Object-Oriented Software," Gamma et al., 1994): a creational design pattern that ensures a class has exactly one instance and provides a global point of access to it. Use cases: shared resources that must be globally accessible and where multiple instances would cause problems (incorrect behavior, inconsistent state, wasted resources). Implementation contract: (1) private constructor (prevents external instantiation); (2) private static instance variable; (3) public static method returning the single instance. Challenges: thread safety during lazy initialization; testability (global state); subclassing restrictions; serialization creating new instances.

---

### 🟢 Simple Definition (Easy)

A country's government. There can only be ONE government at a time (one instance). You don't create "a government" — you access THE government (global access point). Any agency or department that needs the government accesses the same one. There's no mechanism to create a second government.

---

### 🔵 Simple Definition (Elaborated)

An application config: `AppConfig.getInstance()`. All classes that need configuration use the same instance. Creating a new `AppConfig` object for each class would be wasteful (re-reads config file each time) and inconsistent (each instance might have a different view). The Singleton ensures one config, loaded once, accessible everywhere. Connection pool: one pool manages all DB connections — multiple pool instances would over-provision connections. Logger: all log entries go to one centralized logger — multiple loggers would fragment log streams.

---

### 🔩 First Principles Explanation

**Thread-safe Singleton implementations and why naive ones fail:**

```
1. EAGER INITIALIZATION (simplest, thread-safe):

   class DatabaseConnectionPool {
       // Created when class is loaded — before any thread calls getInstance():
       private static final DatabaseConnectionPool INSTANCE = new DatabaseConnectionPool();
       
       private DatabaseConnectionPool() {
           // Initialize pool: open connections, configure...
       }
       
       public static DatabaseConnectionPool getInstance() {
           return INSTANCE;
       }
   }
   
   ✓ Thread-safe: class loading is thread-safe (JVM handles it).
   ✓ Simple. No synchronization overhead.
   ✗ Created eagerly even if never used (wasteful if expensive to create).
   ✗ No lazy initialization (if constructor can fail: exception at class load time).
   
2. LAZY INITIALIZATION — BROKEN (non-thread-safe):

   class Config {
       private static Config instance;
       
       public static Config getInstance() {
           if (instance == null) {         // ← Thread A and B both see null
               instance = new Config();    // ← BOTH create an instance!
           }                               //   Two instances — Singleton broken.
           return instance;
       }
   }
   ✗ RACE CONDITION: Thread A checks instance == null (true). Context switch.
     Thread B checks instance == null (true). Both create instances. BROKEN.
   
3. SYNCHRONIZED METHOD (thread-safe but slow):

   public static synchronized Config getInstance() {
       if (instance == null) instance = new Config();
       return instance;
   }
   ✓ Thread-safe.
   ✗ Every call synchronizes — contention when many threads call frequently.
   
4. DOUBLE-CHECKED LOCKING (thread-safe, fast after initialization):

   class Config {
       private static volatile Config instance;  // volatile required!
       
       public static Config getInstance() {
           if (instance == null) {               // Check 1: avoid sync if initialized
               synchronized (Config.class) {     // Lock only for initialization
                   if (instance == null) {       // Check 2: another thread may have initialized
                       instance = new Config();
                   }
               }
           }
           return instance;
       }
   }
   ✓ Thread-safe (volatile prevents reordering + memory visibility issues).
   ✓ Fast after initialization (no sync on hot path).
   ✗ Complex. volatile required (Java Memory Model).
   
5. INITIALIZATION-ON-DEMAND HOLDER (preferred in Java):

   class Config {
       private Config() {}
       
       private static class Holder {
           // Class loaded lazily on first access to Holder.
           // Class loading is thread-safe. No explicit synchronization needed.
           static final Config INSTANCE = new Config();
       }
       
       public static Config getInstance() {
           return Holder.INSTANCE;  // triggers Holder class loading on first call
       }
   }
   ✓ Lazy: Holder class loaded only when getInstance() first called.
   ✓ Thread-safe: JVM guarantees class initialization is thread-safe.
   ✓ No synchronization overhead.
   ✓ Simpler than double-checked locking.
   
6. ENUM SINGLETON (serialization-safe, reflection-safe):

   enum AppConfig {
       INSTANCE;
       
       private final Properties props = loadProperties();
       
       public String get(String key) { return props.getProperty(key); }
   }
   
   // Usage: AppConfig.INSTANCE.get("db.url")
   
   ✓ Thread-safe by JVM.
   ✓ Serialization-safe (enum values are always the same instance across JVM boundaries).
   ✓ Reflection-safe (cannot call constructor via reflection).
   ✗ Unusual for non-simple singletons. Cannot extend a class.
   
SINGLETON ANTI-PATTERN CONCERNS:

  1. GLOBAL STATE:
     Singleton IS global state. Tests depend on each other through shared singleton state.
     One test modifies singleton. Next test gets polluted state. Tests are order-dependent.
     
  2. HIDDEN DEPENDENCY:
     Classes using Config.getInstance() have a HIDDEN dependency on Config.
     Like Service Locator: dependency not visible in constructor.
     Makes classes harder to test and harder to understand.
     
  3. FIX: Inject the singleton:
  
     // BAD: class uses singleton directly:
     class OrderService {
         void place(Order o) {
             String limit = AppConfig.getInstance().get("max.order");  // hidden dep
         }
     }
     
     // GOOD: inject singleton as a dependency:
     class OrderService {
         private final AppConfig config;
         OrderService(AppConfig config) { this.config = config; }  // visible dep
         // In tests: inject a test AppConfig with test values.
         // In production: Spring injects the Singleton bean.
     }
     
  Spring @Bean + @Scope("singleton") is the canonical modern Java Singleton:
  Spring manages lifecycle, injection, and thread safety.
  You don't implement Singleton pattern manually — Spring does it for you.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Singleton:
- Each class creates its own `AppConfig` — N config file reads, N inconsistent views
- Connection pool: 20 classes each create a pool of 10 connections = 200 connections (overloads DB)

WITH Singleton:
→ One config, loaded once, consistent view everywhere
→ One connection pool: all threads share and reuse the same pool

---

### 🧠 Mental Model / Analogy

> The President of a country. There can only be one at a time. Every government department accesses the same President. You can't "new President()" — there is a specific access mechanism. If there were multiple Presidents, government would be incoherent. The "access mechanism" (election, succession rules) ensures exactly one exists.

"One President" = one instance
"Every department accesses the same one" = global access point
"Can't new President()" = private constructor
"Election as access mechanism" = getInstance() method

---

### ⚙️ How It Works (Mechanism)

```
SINGLETON STRUCTURE:

  class Singleton {
      private static Singleton instance;  // 1. Private static field
      
      private Singleton() {}              // 2. Private constructor
      
      public static Singleton getInstance() {  // 3. Public static accessor
          if (instance == null) instance = new Singleton();
          return instance;
      }
  }
  
  MODERN JAVA: Use enum or Initialization-on-Demand Holder.
  SPRING: @Bean singleton scope (default) — Spring is your Singleton container.
```

---

### 🔄 How It Connects (Mini-Map)

```
Need for shared resource with single instance constraint
        │
        ▼
Singleton Pattern ◄──── (you are here)
(one instance, global access)
        │
        ├── Dependency Injection: inject the singleton rather than accessing globally
        ├── Service Locator: anti-pattern that often uses singletons as a global registry
        ├── Flyweight Pattern: shares instances to save memory (related, different intent)
        └── Multiton: variant where N named instances are allowed (e.g., per-locale)
```

---

### 💻 Code Example

```java
// BEST JAVA SINGLETON — Initialization-on-Demand Holder:
public class DatabaseConnectionPool {
    private final HikariDataSource dataSource;
    
    private DatabaseConnectionPool() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(System.getenv("DATABASE_URL"));
        config.setMaximumPoolSize(20);
        this.dataSource = new HikariDataSource(config);
    }
    
    private static class Holder {
        static final DatabaseConnectionPool INSTANCE = new DatabaseConnectionPool();
    }
    
    public static DatabaseConnectionPool getInstance() {
        return Holder.INSTANCE;
    }
    
    public Connection getConnection() throws SQLException {
        return dataSource.getConnection();
    }
}

// ────────────────────────────────────────────────────────────────────

// MODERN SPRING APPROACH (preferred in Spring apps — Spring manages singleton):
@Configuration
class DatabaseConfig {
    @Bean  // @Scope("singleton") is default — Spring ensures one instance
    DatabaseConnectionPool connectionPool() {
        return new DatabaseConnectionPool(env.getProperty("database.url"));
    }
}

@Service
class OrderRepository {
    // Spring INJECTS the singleton — not accessed via getInstance():
    @Autowired
    DatabaseConnectionPool pool;  // visible dependency, testable
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Singleton is the same as global variable | Singleton controls instantiation (one instance guaranteed). A global variable is just a variable that happens to be globally accessible — no instantiation control. Singleton adds: private constructor (no external creation), controlled access point, lazy/eager initialization logic |
| Singleton is always an anti-pattern | Singleton is overused, but not always wrong. Logger, application config, connection pool — genuinely benefit from one instance. The problem: Singleton is often used as a shortcut for global state when DI would be cleaner. Use Spring's singleton scope or inject the single instance rather than calling `getInstance()` directly in application code |
| Double-checked locking without volatile is safe in Java | Before Java 5 and the updated memory model, double-checked locking was broken. The `volatile` keyword on the instance field is REQUIRED in Java: without it, the JIT compiler or CPU can reorder the write to `instance` before the constructor finishes, causing another thread to see a partially constructed object via the non-null instance reference |

---

### 🔥 Pitfalls in Production

**Singleton state contamination in tests:**

```java
// ANTI-PATTERN: Singleton holds mutable state accessed directly:
class FeatureFlags {
    private static FeatureFlags instance = new FeatureFlags();
    private final Map<String, Boolean> flags = new HashMap<>();
    
    static FeatureFlags getInstance() { return instance; }
    void enable(String flag) { flags.put(flag, true); }
    boolean isEnabled(String flag) { return flags.getOrDefault(flag, false); }
}

// Test A: enables flag for its test
@Test void testA() {
    FeatureFlags.getInstance().enable("NEW_CHECKOUT");
    // ... test
}

// Test B: runs AFTER Test A — NEW_CHECKOUT is still enabled! Tests pollute each other.
@Test void testB() {
    assertFalse(FeatureFlags.getInstance().isEnabled("NEW_CHECKOUT")); // FAILS!
}

// FIX: Reset state between tests, OR inject FeatureFlags (not static):
@AfterEach void resetFlags() { FeatureFlags.getInstance().reset(); }

// BETTER FIX: Make FeatureFlags injectable; tests create their own instance:
class OrderService {
    OrderService(FeatureFlags flags) { ... }  // inject, not getInstance()
}
// Test: new OrderService(new FeatureFlags()) — fresh instance per test. No contamination.
```

---

### 🔗 Related Keywords

- `Dependency Injection` — inject the singleton; don't call `getInstance()` in application code
- `Service Locator` — anti-pattern that abuses singleton as a global service registry
- `Flyweight Pattern` — shares instances for memory efficiency (different motivation from Singleton)
- `Multiton` — variant allowing N named instances
- `Spring @Bean` — Spring's managed singleton scope (preferred over manual Singleton implementation)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Exactly one instance; global access point.│
│              │ Use for genuinely shared resources.       │
│              │ Inject it — don't call getInstance().     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Shared resource requiring single instance:│
│              │ config, logger, connection pool,          │
│              │ thread pool, registry                     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Used as shortcut for global mutable state;│
│              │ when DI can provide the single instance  │
│              │ without static global access             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One President — every department accesses│
│              │  the same one; can't elect two; can't    │
│              │  create one with 'new President()'.'"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Injection → Service Locator →  │
│              │ Flyweight Pattern → Spring @Bean          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Thread-local storage is sometimes described as a "per-thread singleton" — each thread has its own instance of the stored value. How does `ThreadLocal<T>` in Java relate to the Singleton pattern? In what scenarios (request-scoped data in web frameworks, transaction context propagation) is ThreadLocal used, and what memory leak risk must you manage when using it with thread pools?

**Q2.** In a Spring web application, a `@Service` class is by default singleton-scoped. But it serves thousands of concurrent HTTP requests. If the service has a mutable `List<String> log = new ArrayList<>()` field, what happens in a multi-threaded environment? What should you do with state that must be per-request rather than per-application? How does Spring's `@Scope("request")` address this?
