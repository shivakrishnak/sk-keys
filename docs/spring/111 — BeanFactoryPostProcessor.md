---
layout: default
title: "BeanFactoryPostProcessor"
parent: "Spring Framework"
nav_order: 111
permalink: /spring/beanfactorypostprocessor/
---

`#spring` `#internals` `#advanced`

⚡ TL;DR — BeanFactoryPostProcessor runs after bean definitions are loaded but BEFORE any bean is instantiated — letting you modify, add, or remove bean definitions programmatically.
## 📘 Textbook Definition
`BeanFactoryPostProcessor` is a Spring extension interface that allows modification of the application context's bean definitions (BeanDefinition objects) after they have been loaded into the container but before any bean instances are created. The most important built-in implementation is `PropertySourcesPlaceholderConfigurer` which resolves `${...}` placeholders.
## 🟢 Simple Definition (Easy)
BeanFactoryPostProcessor says "Before you create ANY objects, let me look at the blueprints (bean definitions) and change them if needed." It's how `@Value("${server.port}")` gets resolved — the placeholder is replaced with the actual value before the bean is created.
## 🔵 Simple Definition (Elaborated)
While BeanPostProcessor works on bean *instances*, BeanFactoryPostProcessor works on bean *definitions* (the metadata/blueprints). It receives the `ConfigurableListableBeanFactory`, giving you access to every registered BeanDefinition to inspect or modify them — changing property values, changing the implementation class, or even registering new bean definitions programmatically.
## 🔩 First Principles Explanation
**Execution order vs BeanPostProcessor:**
```
1. @Configuration classes processed               (BFPP phase)
2. BeanDefinitions registered in BeanFactory       (BFPP phase)
3. BeanFactoryPostProcessors run ← THIS            (BFPP phase)
   - PropertySourcesPlaceholderConfigurer
   - ConfigurationClassPostProcessor
4. BeanPostProcessors registered
5. Singleton beans instantiated + DI               (BPP phase)
6. BeanPostProcessors run on each bean             (BPP phase)
```
## 🧠 Mental Model / Analogy
> BeanFactoryPostProcessor is an **architect reviewing blueprints before construction begins**. They can update the plans, fix mistakes, and even add new rooms — but only while it's still on paper. Once building starts (bean instantiation), it's too late.
## 💻 Code Example
```java
// Custom BFPP — change a property value in a bean definition
@Component
public class CustomBeanFactoryPostProcessor implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) {
        BeanDefinition def = bf.getBeanDefinition("dataSource");
        // Modify a property value before instantiation
        def.getPropertyValues().add("maxPoolSize", 50);
        System.out.println("Modified dataSource maxPoolSize to 50");
    }
}
// Built-in: PropertySourcesPlaceholderConfigurer resolves ${...} placeholders
// This is how @Value("${spring.datasource.url}") works
@Configuration
public class AppConfig {
    @Bean
    public static PropertySourcesPlaceholderConfigurer placeholderConfigurer() {
        return new PropertySourcesPlaceholderConfigurer(); // must be static!
    }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| BFPP and BPP run at the same time | BFPP runs before bean creation; BPP runs after each bean is created |
| BFPP can inject dependencies via @Autowired | Full DI is not available in BFPP; it runs before other beans exist |
| BFPP @Bean method can be non-static | BFPP @Bean methods MUST be static to allow early instantiation |
## 🔗 Related Keywords
- **[BeanPostProcessor](./110 — BeanPostProcessor.md)** — works on instances after creation
- **[ApplicationContext](./105 — ApplicationContext.md)** — invokes BFPPs during refresh()
- **[Auto-Configuration](./133 — Auto-Configuration.md)** — relies on BFPPs for condition evaluation
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Modify bean definitions BEFORE any bean is created  |
+------------------------------------------------------------------+
| RUNS        | After definitions loaded, before instantiation       |
+------------------------------------------------------------------+
| KEY IMPL    | PropertySourcesPlaceholderConfigurer, ConfigurationClassPostProcessor |
+------------------------------------------------------------------+
| @BEAN       | MUST be static to avoid early container initialization |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** Why must a `@Bean` method that returns a `BeanFactoryPostProcessor` be declared `static`?
**Q2.** `ConfigurationClassPostProcessor` is a `BeanFactoryPostProcessor`. What does it do — and why must it run as a BFPP rather than a BPP?
**Q3.** What is the difference between `BeanDefinitionRegistryPostProcessor` and `BeanFactoryPostProcessor`?
