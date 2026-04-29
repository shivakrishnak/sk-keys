---
layout: default
title: "Auto-Configuration"
parent: "Spring Framework"
nav_order: 133
permalink: /spring/auto-configuration/
---

`#springboot` `#spring` `#internals` `#foundational`

⚡ TL;DR — Auto-Configuration is Spring Boot's mechanism that automatically configures beans and settings based on what's on the classpath and what you haven't already configured — "convention over configuration."
## 📘 Textbook Definition
Spring Boot Auto-Configuration is a mechanism driven by `@EnableAutoConfiguration` (included in `@SpringBootApplication`) that automatically creates and configures Spring beans by processing classes listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot 3+) or `spring.factories` (Boot 2.x). Each auto-configuration class uses `@Conditional` annotations to activate only when specific classes, beans, or properties are present.
## 🟢 Simple Definition (Easy)
Auto-Configuration means Spring Boot sees you added `spring-boot-starter-data-jpa` to your project and automatically sets up a DataSource, EntityManager, and TransactionManager — without you writing any config. As soon as you provide your own, Boot backs off.
## 🔵 Simple Definition (Elaborated)
Each starter jar ships with auto-configuration classes that declare: "If `DataSource.class` is on the classpath AND no `DataSource` bean is already defined, create a default one." These conditions are evaluated at startup, and matching configs are applied — giving you a working app with zero configuration. You override defaults by defining your own beans; Boot's `@ConditionalOnMissingBean` backs off automatically.
## 🔩 First Principles Explanation
**How it works:**
```
1. @SpringBootApplication includes @EnableAutoConfiguration
2. AutoConfigurationImportSelector reads:
   META-INF/spring/...AutoConfiguration.imports
   (lists ~140 auto-config classes)
3. Each auto-config class evaluated: @Conditional passes?
   DataSourceAutoConfiguration:
     @ConditionalOnClass(DataSource.class)     → is Hikari/JDBC on classpath?
     @ConditionalOnMissingBean(DataSource.class) → user hasn't defined one?
   → YES? → create default DataSource bean
4. Result: beans wired without any user config
```
**Key @Conditional types:**
```
@ConditionalOnClass       — certain class must be on classpath
@ConditionalOnMissingBean — user has NOT defined this bean
@ConditionalOnProperty    — specific property is set
@ConditionalOnBean        — specific bean IS defined
@ConditionalOnWebApplication — is a web app?
```
## 💻 Code Example
```java
// Auto-config you get for FREE when adding spring-boot-starter-data-jpa:
// - DataSource (HikariCP)
// - EntityManagerFactory (Hibernate)
// - JpaTransactionManager
// - Spring Data repositories
// app.properties — just supply DB connection details:
// spring.datasource.url=jdbc:h2:mem:test
// spring.datasource.username=sa
// Override: define your own DataSource → Boot backs off
@Bean
public DataSource myCustomDataSource() {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl("jdbc:postgresql://prod-db:5432/mydb");
    ds.setMaximumPoolSize(50);
    return ds; // DataSourceAutoConfiguration's @ConditionalOnMissingBean skips
}
// Debug which auto-configs were applied:
// application.properties:
// logging.level.org.springframework.boot.autoconfigure=DEBUG
// Or: spring-boot actuator /actuator/conditions endpoint
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Auto-config is magic — can't be controlled | Fully conditional and overridable; `@ConditionalOnMissingBean` is the key |
| Defining your own bean breaks everything | Defining your own bean causes Boot's default to back off gracefully |
| Auto-config slows startup | Condition checks are fast; unused configs are skipped entirely |
## 🔗 Related Keywords
- **[Spring Boot Startup Lifecycle](./135 — Spring Boot Startup Lifecycle.md)** — when auto-config runs
- **[BeanFactoryPostProcessor](./111 — BeanFactoryPostProcessor.md)** — mechanism for condition evaluation
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Classpath-driven zero-config bean setup              |
+------------------------------------------------------------------+
| MECHANISM   | @Conditional annotations on auto-config classes      |
+------------------------------------------------------------------+
| OVERRIDE    | Define your own bean → Boot backs off                |
+------------------------------------------------------------------+
| DEBUG       | logging.level...autoconfigure=DEBUG or /actuator/conditions |
+------------------------------------------------------------------+
```
