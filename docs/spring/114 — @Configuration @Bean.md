---
layout: default
title: "@Configuration / @Bean"
parent: "Spring & Spring Boot"
nav_order: 114
permalink: /spring/configuration-bean/
number: "114"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "ApplicationContext, Bean, IoC, BeanFactory"
used_by: "Auto-Configuration, @Import, @Conditional, @Profile, Spring Boot"
tags: #java, #spring, #springboot, #intermediate, #pattern
---

# 114 — @Configuration / @Bean

`#java` `#spring` `#springboot` `#intermediate` `#pattern`

⚡ TL;DR — `@Configuration` declares a class as a source of bean definitions; `@Bean` marks a factory method whose return value Spring registers as a managed bean.

| #114 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | ApplicationContext, Bean, IoC, BeanFactory | |
| **Used by:** | Auto-Configuration, @Import, @Conditional, @Profile, Spring Boot | |

---

### 📘 Textbook Definition

`@Configuration` is a class-level annotation that marks a class as a configuration source — a replacement for XML `<beans>` configuration. Methods inside a `@Configuration` class annotated with `@Bean` are factory methods: Spring calls them at startup, registers the returned objects as beans, and manages their lifecycle. A critical implementation detail: `@Configuration` classes are enhanced by CGLIB at startup — inter-bean method calls within the same `@Configuration` class are intercepted by the proxy to return the existing singleton bean rather than creating a new instance. `@Configuration` classes are themselves beans and can be injected with `@Value`, participate in `@Profile`, and be imported with `@Import`.

---

### 🟢 Simple Definition (Easy)

`@Configuration` marks a class as "this is my Spring setup." Inside it, `@Bean` methods tell Spring "call this method to create a bean and manage it for me."

---

### 🔵 Simple Definition (Elaborated)

Before `@Configuration`, Spring was configured with verbose XML files. `@Configuration` brought configuration into Java — type-safe, refactorable, IDE-navigable. A `@Bean` method is a factory method: Spring calls it once at startup, takes the returned object, gives it a name (the method name by default), injects dependencies, runs lifecycle callbacks, and registers it in the context. The CGLIB enhancement is the subtle but important part: if `@Bean` method A calls another `@Bean` method B inside the same `@Configuration` class, Spring intercepts that call and returns the singleton bean rather than creating a new instance.

---

### 🔩 First Principles Explanation

**Why @Bean methods exist alongside @Component scanning:**

Component scanning works for your own classes — you control their source. But third-party classes (`DataSource`, `ObjectMapper`, `RestTemplate`) can't be annotated. `@Bean` factory methods solve this:

```java
// Can't add @Component to HikariDataSource (third party)
// → Use a @Bean factory method to register it
@Configuration
public class InfraConfig {
  @Bean
  DataSource dataSource(DataSourceProperties props) {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl(props.getUrl());
    ds.setMaximumPoolSize(props.getPoolSize());
    return ds; // Spring registers this as a bean
  }
}
```

**The CGLIB singleton guarantee:**

Without CGLIB enhancement, calling another @Bean method would create a new instance every time. The CGLIB proxy intercepts and redirects to the container:

```
┌───────────────────────────────────────────────────┐
│  @Configuration CGLIB INTERCEPTION                │
│                                                   │
│  @Configuration class → enhanced by CGLIB proxy  │
│                                                   │
│  bean1() calls bean2() internally:                │
│  → Call intercepted by CGLIB proxy                │
│  → Proxy calls ctx.getBean("bean2")               │
│  → Returns EXISTING singleton (not new instance)  │
│  → Singleton contract maintained                  │
│                                                   │
│  @Configuration(proxyBeanMethods=false) (Lite):   │
│  → No CGLIB proxy                                 │
│  → Inter-bean calls create NEW instances          │
│  → Only use when NO inter-bean calls needed       │
└───────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT @Configuration/@Bean:**

```
Without Java configuration:

  XML-only:
    <bean id="ds" class="com.zaxxer.hikari.HikariDataSource">
      <property name="jdbcUrl" value="${db.url}"/>
    </bean>
    → No compile-time check
    → Refactor class name → XML silently broken
    → IDE can't navigate to bean definition
    → No @Profile, no @Conditional in XML (Spring 3)

  @Component only:
    Third-party beans can't be registered
    → Can't create DataSource, ObjectMapper, etc.
    → Complex construction logic impossible in annotations
    → Multiple beans of same type impossible
```

**WITH @Configuration/@Bean:**

```
→ Type-safe: compiler catches wrong return types
→ IDE-navigable: Cmd+Click to go to bean definition
→ @Conditional: register beans based on conditions
→ @Profile: different beans per environment
→ Third-party bean registration (DataSource, etc.)
→ Complex multi-step construction logic in Java
→ Auto-configuration: Spring Boot's 1000+ @Bean methods
```

---

### 🧠 Mental Model / Analogy

> `@Configuration` is like a **blueprint spec sheet** and `@Bean` methods are individual **room specifications** in that blueprint. The contractor (Spring) reads the spec sheet, calls each room spec method to determine what to build, manages construction (lifecycle), and connects rooms together (injection). Inter-@Bean method calls within the spec sheet hit the master blueprint first — which returns the already-built room, not a new one.

"Blueprint spec sheet" = @Configuration class
"Room specification method" = @Bean method
"Contractor executing the blueprint" = Spring container
"Returning already-built room" = CGLIB singleton interception
"Different spec sheets per project" = @Profile / @Conditional

---

### ⚙️ How It Works (Mechanism)

**Full @Bean lifecycle options:**

```java
@Configuration
public class AppConfig {
  // Basic bean
  @Bean
  ObjectMapper objectMapper() {
    return new ObjectMapper()
        .configure(FAIL_ON_UNKNOWN_PROPERTIES, false);
  }

  // With name, init, destroy
  @Bean(name = "taskScheduler",
        initMethod = "initialize",
        destroyMethod = "shutdown")
  ThreadPoolTaskScheduler scheduler() {
    ThreadPoolTaskScheduler s = new ThreadPoolTaskScheduler();
    s.setPoolSize(4);
    return s;
  }

  // @Bean with @Scope
  @Bean
  @Scope("prototype")
  CsvParser csvParser() {
    return new CsvParser();
  }

  // @Bean with @Conditional
  @Bean
  @ConditionalOnProperty("feature.new-algorithm.enabled")
  SearchAlgorithm newSearchAlgorithm() {
    return new BinarySearchAlgorithm();
  }

  @Bean
  @ConditionalOnMissingBean(SearchAlgorithm.class)
  SearchAlgorithm defaultSearchAlgorithm() {
    return new LinearSearchAlgorithm();
  }
}
```

**proxyBeanMethods=false (lightweight @Configuration):**

```java
// Spring Boot auto-configurations use this extensively
// for faster startup — no CGLIB proxy overhead
@Configuration(proxyBeanMethods = false)
public class WebMvcConfig {
  @Bean
  WebMvcConfigurer corsConfig() {
    return new WebMvcConfigurer() {
      @Override
      public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOrigins("https://app.example.com");
      }
    };
  }
  // No inter-@Bean calls needed here → safe to disable proxy
}
```

---

### 🔄 How It Connects (Mini-Map)

```
@SpringBootApplication triggers component scan
        ↓
  @CONFIGURATION / @BEAN (114)  ← you are here
  (Java-based bean definition source)
        ↓
  @Bean methods → BeanDefinitions registered
        ↓
  Processed by BeanFactoryPostProcessor (111)
  (conditions evaluated, placeholders resolved)
        ↓
  Beans instantiated via factory methods
        ↓
  Enables: @Profile, @Conditional, @Import
  Powers: Auto-Configuration (133)
```

---

### 💻 Code Example

**Example 1 — Inter-bean method calls and CGLIB singleton:**

```java
@Configuration
public class ServiceConfig {
  @Bean
  public UserRepository userRepository(DataSource ds) {
    return new JdbcUserRepository(ds);
  }

  @Bean
  public AuditRepository auditRepository(DataSource ds) {
    return new JdbcAuditRepository(ds);
  }

  // BAD if NOT @Configuration (proxyBeanMethods=true):
  // Both repos would get DIFFERENT DataSource instances!
  // With @Configuration proxy: both get the SAME singleton
  @Bean
  public DataSource dataSource() {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl("jdbc:postgresql://...");
    return ds;
  }
}
// Both userRepository and auditRepository receive
// the exact same DataSource bean — singleton guaranteed
```

**Example 2 — @Bean vs @Component — when to use which:**

```java
// USE @Component: your own class, simple construction
@Service
class UserService {
  UserService(UserRepository repo) {...}
}

// USE @Bean: third-party class, complex construction,
// or multiple beans of same type needed
@Configuration
class SecurityConfig {
  @Bean
  BCryptPasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
  }

  @Bean
  @Primary
  ObjectMapper defaultMapper() {
    return JsonMapper.builder()
        .addModule(new JavaTimeModule())
        .build();
  }

  @Bean
  @Qualifier("strictMapper")
  ObjectMapper strictMapper() {
    return JsonMapper.builder()
        .configure(FAIL_ON_UNKNOWN_PROPERTIES, true)
        .build();
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Bean methods are called directly by application code | Spring intercepts @Bean calls via CGLIB in a @Configuration class — direct calls from outside return beans, not new instances |
| @Configuration is just a @Component with @Bean support | @Configuration classes are enhanced by CGLIB to proxy inter-bean method calls. @Component-annotated classes with @Bean methods are "lite" mode — no CGLIB, no inter-bean singleton guarantee |
| @Bean method name must match the interface name | @Bean method name becomes the default bean name — it can be anything. Use @Bean("customName") or @Bean(name = {...}) for explicit naming |
| proxyBeanMethods=false is always faster and should always be used | proxyBeanMethods=false is only safe when @Bean methods do NOT call each other. If they do, inter-bean calls create new instances, breaking singleton scope |

---

### 🔥 Pitfalls in Production

**1. @Component with @Bean methods — lite mode breaks singleton**

```java
// BAD: @Component with @Bean — NOT enhanced by CGLIB
@Component // NOT @Configuration!
public class ServiceConfig {
  @Bean
  DataSource dataSource() {
    return new HikariDataSource();
  }

  @Bean
  UserRepository userRepository() {
    return new JdbcUserRepository(dataSource()); // DIRECT CALL
    // dataSource() is NOT intercepted — creates NEW instance!
    // UserRepository gets a different DS than the registered bean
  }
}

// GOOD: use @Configuration to ensure proxy enhancement
@Configuration // CGLIB proxy applied
public class ServiceConfig {
  @Bean DataSource dataSource() {...}
  @Bean UserRepository userRepository() {
    return new JdbcUserRepository(dataSource()); // intercepted
  }
}
```

**2. Non-static @Bean for BeanFactoryPostProcessor**

```java
// BAD: non-static BFPP @Bean causes premature class loading
@Configuration
class AppConfig {
  @Bean
  public PropertySourcesPlaceholderConfigurer pspc() {
    return new PropertySourcesPlaceholderConfigurer();
  }
  // AppConfig instantiated before BFPPs run
  // → @Value in AppConfig NOT yet resolved!
}

// GOOD: BFPP @Bean methods must be static
@Configuration
class AppConfig {
  @Bean
  public static PropertySourcesPlaceholderConfigurer pspc() {
    return new PropertySourcesPlaceholderConfigurer();
  }
}
```

---

### 🔗 Related Keywords

- `Bean` — the object produced and registered by a `@Bean` factory method
- `ApplicationContext` — registers and manages all beans declared via @Configuration/@Bean
- `BeanFactoryPostProcessor` — @Bean BFPP methods must be static to avoid ordering issues
- `Auto-Configuration` — Spring Boot's auto-configs are all @Configuration classes with conditional @Bean methods
- `@Conditional` — gates @Bean registration on conditions evaluated at startup
- `@Profile` — activates @Configuration classes or @Bean methods based on active profiles

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ @Configuration = bean definition source;  │
│              │ @Bean = factory method → registered bean  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Third-party beans; complex construction;  │
│              │ conditional registration; multiple impls  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ proxyBeanMethods=false if @Bean methods   │
│              │ call each other (breaks singleton)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Configuration is the blueprint;         │
│              │  @Bean is the room specification."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circular Dependency (115) →               │
│              │ CGLIB Proxy (116) → Auto-Configuration (133)│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's Auto-Configuration uses hundreds of `@Configuration(proxyBeanMethods = false)` classes. Explain precisely what CGLIB enhancement Spring applies to a normal `@Configuration` class, what bytecode manipulation it performs, why `proxyBeanMethods = false` makes startup faster, and what the specific runtime risk is when a developer uses `proxyBeanMethods = false` on a `@Configuration` class that contains inter-`@Bean` method calls — including what incorrect behaviour manifests and why it's difficult to detect in tests.

**Q2.** `@Import` can import three types into a `@Configuration` class: another `@Configuration` class, an `ImportSelector` implementation, or a `BeanDefinitionRegistrar` implementation. For each type, explain what Spring does with the imported class — what phase of startup it runs, what it can and cannot do — and describe the specific scenario where `ImportSelector` combined with `@ImportAutoConfiguration` is more appropriate than `@ConditionalOnClass` for library authors.

