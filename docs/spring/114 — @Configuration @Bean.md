---
layout: default
title: "@Configuration / @Bean"
parent: "Spring Framework"
nav_order: 114
permalink: /spring/configuration-bean/
---
⚡ TL;DR — @Configuration marks a class as a source of bean definitions; @Bean marks a method inside it as a factory that produces a Spring-managed bean.
## 📘 Textbook Definition
`@Configuration` is a class-level annotation indicating that the class declares one or more `@Bean` methods and may be processed by the Spring container to generate bean definitions and service requests at runtime. `@Bean` is a method-level annotation indicating that the annotated method produces a bean to be managed by the Spring container, with the method name serving as the default bean name.
## 🟢 Simple Definition (Easy)
`@Configuration` is "this class is Spring's recipe book." `@Bean` is "this method is one recipe." Spring calls the `@Bean` methods at startup and registers what they return as beans.
## 🔵 Simple Definition (Elaborated)
`@Configuration` + `@Bean` is the Java-based alternative to XML bean configuration. It enables type-safe, IDE-friendly bean registration with full refactoring support. The `@Configuration` class is itself a Spring bean (a CGLIB-enhanced proxy), so calling one `@Bean` method from another returns the container-managed singleton — not a new instance.
## 🔩 First Principles Explanation
**Why @Configuration classes are proxied:**
```java
@Configuration
public class AppConfig {
    @Bean
    public ServiceA serviceA() { return new ServiceA(serviceB()); }
    @Bean
    public ServiceB serviceB() { return new ServiceB(); }  // shared singleton!
}
// Spring proxies AppConfig: calling serviceB() from serviceA() returns the
// same singleton from the container, NOT a new instance.
// Without @Configuration (using @Component instead), serviceB() would
// create a NEW ServiceB each time — breaking singleton contract!
```
## 💻 Code Example
```java
@Configuration
@PropertySource("classpath:app.properties")
public class DatabaseConfig {
    @Value("${db.url}")
    private String dbUrl;
    @Value("${db.pool.size:10}")
    private int poolSize;
    @Bean  // bean name = "dataSource" (method name)
    public DataSource dataSource() {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl(dbUrl);
        ds.setMaximumPoolSize(poolSize);
        return ds;
    }
    @Bean  // depends on dataSource() — Spring calls the method, returns singleton
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource()); // dataSource() returns cached singleton
    }
    @Bean(name = "readonlyDataSource", 
          destroyMethod = "close")  // custom name + destroy hook
    @Conditional(ReadReplicaCondition.class)
    public DataSource readonlyDataSource() { ... }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| @Component and @Configuration are the same | @Configuration generates a CGLIB proxy; @Component does not |
| Calling @Bean method = new instance each time | In @Configuration class, Spring intercepts the call and returns the singleton |
| @Bean must have unique name | Multiple @Bean methods can share a name; the last one registered wins (risky) |
| @Configuration must import @ComponentScan | @Configuration and @ComponentScan are independent annotations |
## 🔗 Related Keywords
- **[Bean](./107 — Bean.md)** — what @Bean methods produce
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — @Configuration classes are CGLIB-proxied
- **[ApplicationContext](./105 — ApplicationContext.md)** — processes @Configuration classes
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| @CONFIGURATION | Source of bean definitions — class level        |
+------------------------------------------------------------------+
| @BEAN          | Factory method that returns a managed bean       |
+------------------------------------------------------------------+
| CGLIB PROXY    | @Configuration class proxied to ensure singletons|
+------------------------------------------------------------------+
| ONE-LINER      | "Java-code XML — readable, type-safe bean config" |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** What happens if you replace `@Configuration` with `@Component` on a config class that has `@Bean` methods calling each other? What breaks?
**Q2.** Can a `@Bean` method have parameters? How does Spring resolve them?
**Q3.** What is `@Import` and how does it complement `@Configuration`?
