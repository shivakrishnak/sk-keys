---
layout: default
title: "BeanFactoryPostProcessor"
parent: "Spring Core"
nav_order: 379
permalink: /spring/beanfactorypostprocessor/
number: "0379"
category: Spring Core
difficulty: ★★★
depends_on: BeanFactory, BeanDefinition, ApplicationContext, Bean Lifecycle
used_by: Configuration Classes, Property Placeholders, Auto-Configuration
related: BeanPostProcessor, BeanDefinitionRegistryPostProcessor, PropertySourcesPlaceholderConfigurer
tags:
  - spring
  - internals
  - advanced
  - deep-dive
  - architecture
---

# 379 — BeanFactoryPostProcessor

⚡ TL;DR — BeanFactoryPostProcessor modifies bean definitions (metadata) before any beans are instantiated — it rewrites the blueprint, not the house.

| #379            | Category: Spring Core                                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | BeanFactory, BeanDefinition, ApplicationContext, Bean Lifecycle                              |                 |
| **Used by:**    | Configuration Classes, Property Placeholders, Auto-Configuration                             |                 |
| **Related:**    | BeanPostProcessor, BeanDefinitionRegistryPostProcessor, PropertySourcesPlaceholderConfigurer |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine your `DataSource` bean definition has a hardcoded JDBC URL in the source code. To change environments (dev → staging → production), you must recompile or edit Java/XML files. Worse, the database password is in plaintext in the code. When you add environment-specific configuration support, every team invents their own approach: some use system properties, some use environment variables, some read files. The bean definition layer has no standard way to accept externalized configuration.

**THE BREAKING POINT:**
Bean definitions are written at compile time but need values that are only known at runtime (database URLs, API keys, feature flags). Without a post-processing step on the definitions themselves, you can't resolve `${db.url}` placeholders into real values before beans are created. You also can't conditionally register beans based on runtime environment, cannot rename beans, and cannot merge or filter configurations dynamically.

**THE INVENTION MOMENT:**
"This is exactly why BeanFactoryPostProcessor was created."

---

### 📘 Textbook Definition

**BeanFactoryPostProcessor** is a Spring interface with a single method: `postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory)`. It is called once, after all `BeanDefinition` objects have been registered (via component scan or `@Bean` methods) but _before_ any bean instances are created. The processor receives the full `BeanFactory` and can read, modify, add, or remove `BeanDefinition` objects. Common implementations include `PropertySourcesPlaceholderConfigurer` (resolves `${property}` placeholders in definitions), `ConfigurationClassPostProcessor` (processes `@Configuration` and `@Bean` annotations), and `EventListenerMethodProcessor`. Spring Boot's auto-configuration system heavily uses `BeanDefinitionRegistryPostProcessor` (a subinterface) to conditionally register beans.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BeanFactoryPostProcessor is Spring's last chance to edit the recipe book before cooking begins.

**One analogy:**

> A recipe book (BeanDefinitions) is written by chefs (developers). Before the kitchen (BeanFactory) starts cooking, a sous-chef (BeanFactoryPostProcessor) reviews every recipe and makes adjustments: substituting ingredients based on what's in the pantry (resolving property placeholders), adding or removing dishes based on the day's menu (conditional bean registration), or replacing one dish with an upgraded version (redefining a bean class).

**One insight:**
The key distinction from `BeanPostProcessor`: `BeanFactoryPostProcessor` works on _definitions_ (recipes — before anything is made), while `BeanPostProcessor` works on _instances_ (the cooked dishes — after they're made). Modifying a definition is cheap; it happens once. Creating instances is expensive; it happens at runtime. A `BeanFactoryPostProcessor` that adds a new bean definition has effectively changed what the entire application will contain.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `BeanFactoryPostProcessors` run _before_ any non-infrastructure bean is instantiated.
2. They have full access to every `BeanDefinition` in the registry — add, modify, or remove.
3. They run exactly once, during `ApplicationContext.refresh()`, at the `invokeBeanFactoryPostProcessors()` step.

**DERIVED DESIGN:**
Bean definitions are mutable during this phase. Once `finishBeanFactoryInitialization()` starts, definitions are typically frozen. This ordering constraint is why `ConfigurationClassPostProcessor` must be a `BeanFactoryPostProcessor` — it needs to add new `BeanDefinition` objects (from `@Bean` methods) before the factory starts creating them.

**BeanDefinitionRegistryPostProcessor** (a sub-interface) adds an earlier hook: `postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry)` runs before even the `postProcessBeanFactory()` phase. This is where Spring Boot's auto-configuration actually registers conditional beans.

**THE TRADE-OFFS:**

**Gain:** Full control over the application's object model before it starts. Property externalization, conditional bean registration, and dynamic configuration all live here.

**Cost:** Complex to implement correctly. A `BeanFactoryPostProcessor` that creates a bean instance while modifying definitions causes "bean created too early" warnings and may not receive full post-processing. The processor itself cannot depend on beans that need factory post-processing — it must be self-sufficient.

---

### 🧪 Thought Experiment

**SETUP:**
Your `DataSource` bean definition references `${db.url}`, `${db.username}`, and `${db.password}` as property placeholders. Without processing, these literal strings would be passed to the JDBC driver, causing an immediate connection failure.

**WHAT HAPPENS WITHOUT BeanFactoryPostProcessor:**

1. `DataSource` bean definition is registered: `url="${db.url}"`.
2. Factory creates `DataSource` instance.
3. `jdbcUrl = "${db.url}"` is passed to HikariCP.
4. HikariCP tries to connect to a server named literally `${db.url}`.
5. `UnknownHostException: ${db.url}`.
6. Application fails to start.

**WHAT HAPPENS WITH `PropertySourcesPlaceholderConfigurer`:**

1. `DataSource` bean definition registered: `url="${db.url}"`.
2. `PropertySourcesPlaceholderConfigurer.postProcessBeanFactory()` runs.
3. It scans all `BeanDefinitions` for `${...}` patterns.
4. Looks up `db.url` in `application.properties` → finds `jdbc:postgresql://localhost/app`.
5. Replaces `${db.url}` with `jdbc:postgresql://localhost/app` in the definition.
6. Factory creates `DataSource` with the resolved URL.
7. Connection succeeds.

**THE INSIGHT:**
`BeanFactoryPostProcessor` makes bean definitions _dynamic_ — they can reference external configuration that is resolved just-in-time, at startup, before any instances are created.

---

### 🧠 Mental Model / Analogy

> `BeanFactoryPostProcessor` is like a film script doctor called in before production begins. The script (BeanDefinitions) is written. Before cameras roll (bean instantiation), the script doctor (BFPP) reviews every scene (BeanDefinition) and can rewrite dialogue (property values), add new scenes (@Bean methods from @Configuration), or cut scenes (remove bean definitions). Once filming starts, the script is locked.

- "Script" → BeanDefinition registry
- "Script doctor" → BeanFactoryPostProcessor implementation
- "Rewriting dialogue" → resolving `${property}` placeholders
- "Adding new scenes" → `ConfigurationClassPostProcessor` adding `@Bean` definitions
- "Cameras roll" → `finishBeanFactoryInitialization()` starts

**Where this analogy breaks down:** Unlike a film where the script doctor finishes before filming, Spring's `BeanFactoryPostProcessors` can be ordered and multiple processors run in sequence — each sees the modifications made by previous processors. It's more like a series of script passes than a single review.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Before Spring creates any objects, it runs BeanFactoryPostProcessor implementations first. These can edit the recipes (definitions) for all the objects that will be created. The most common use is swapping `${db.password}` placeholders for real values from configuration files.

**Level 2 — How to use it (junior developer):**
You rarely write `BeanFactoryPostProcessors` directly. Spring Boot auto-configuration handles the complex cases. What you interact with are the effects: `@Value("${property}")` works because of `PropertySourcesPlaceholderConfigurer`. Conditional beans (`@ConditionalOnClass`, `@ConditionalOnMissingBean`) work because of `AutoConfigurationImportSelector`. To write your own, implement `BeanFactoryPostProcessor` and register as a Spring bean.

**Level 3 — How it works (mid-level engineer):**
During `AbstractApplicationContext.refresh()`, step 5 is `invokeBeanFactoryPostProcessors()`. This calls `PostProcessorRegistrationDelegate.invokeBeanFactoryPostProcessors()`, which first finds `BeanDefinitionRegistryPostProcessors` (ordered by `PriorityOrdered` → `Ordered` → rest) and runs `postProcessBeanDefinitionRegistry()`, then runs all `BeanFactoryPostProcessors` (including non-registry ones) in the same order. `ConfigurationClassPostProcessor` (a `BeanDefinitionRegistryPostProcessor`) runs first with `PriorityOrdered`, processing all `@Configuration` classes and registering their `@Bean` definitions before any other BFPP runs.

**Level 4 — Why it was designed this way (senior/staff):**
The split between `BeanDefinitionRegistryPostProcessor` and `BeanFactoryPostProcessor` reflects a real sequencing need. Adding new definitions (what `BeanDefinitionRegistryPostProcessor` does) must complete before modifying existing definitions (what `BeanFactoryPostProcessor` does), because you can't modify a definition that hasn't been registered yet. Spring Boot's auto-configuration chain exploits this: `AutoConfigurationImportSelector` (via `BeanDefinitionRegistryPostProcessor`) registers auto-configuration candidates, then `@ConditionalOn*` conditions evaluate which ones to keep (in a subsequent BFPP pass). The two-phase design makes this ordered composition possible.

---

### ⚙️ How It Works (Mechanism)

**Execution sequence within `refresh()`:**

```
ApplicationContext.refresh()
    ↓
invokeBeanFactoryPostProcessors()
  │
  ├─ Phase 1: BeanDefinitionRegistryPostProcessors
  │    - PriorityOrdered first:
  │      ConfigurationClassPostProcessor
  │      → scans @Configuration, @Component, @ComponentScan
  │      → registers all @Bean definitions
  │    - Ordered next
  │    - Unordered last
  │
  └─ Phase 2: BeanFactoryPostProcessors
       - PriorityOrdered first:
         PropertySourcesPlaceholderConfigurer
         → resolves ${...} in all BeanDefinitions
       - Ordered next
       - Unordered last
         ↓
finishBeanFactoryInitialization()  // NOW create instances
```

**What `PropertySourcesPlaceholderConfigurer` does:**

```
postProcessBeanFactory(beanFactory):
    for each BeanDefinition in factory:
        for each PropertyValue in definition:
            if value contains "${...}":
                resolve from PropertySources chain:
                    1. System properties
                    2. Environment variables
                    3. application.properties
                    4. @PropertySource files
                replace placeholder with resolved value
```

**Registering a custom BFPP:**

```java
@Component  // registered as a Spring bean
public class EnvironmentAwareBeanDefinitionProcessor
        implements BeanFactoryPostProcessor {

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory beanFactory) {

        // Example: add a property value to a bean definition
        BeanDefinition def = beanFactory
            .getBeanDefinition("dataSource");
        MutablePropertyValues props = def.getPropertyValues();
        props.addPropertyValue("maximumPoolSize",
            System.getProperty("pool.size", "10"));
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Component scan completes
    ↓
All @Configuration classes detected
    ↓
BeanDefinitionRegistryPostProcessors run:
  ConfigurationClassPostProcessor adds @Bean definitions
    ↓
BeanFactoryPostProcessors run:
  PropertySourcesPlaceholderConfigurer resolves ${...}
   ← YOU ARE HERE (definitions are being finalized)
    ↓
Definitions frozen
    ↓
finishBeanFactoryInitialization() — create instances
    ↓
Application ready
```

**FAILURE PATH:**

```
Property placeholder ${db.url} not found in any source
    ↓
PropertySourcesPlaceholderConfigurer throws
    IllegalArgumentException:
    "Could not resolve placeholder 'db.url'"
    ↓
invokeBeanFactoryPostProcessors() aborts
    ↓
refresh() fails → application exits
```

**WHAT CHANGES AT SCALE:**
`BeanFactoryPostProcessors` run once at startup and have no runtime impact. However, `ConfigurationClassPostProcessor` scanning hundreds of `@Configuration` classes can take seconds on large codebases. The reflection-based scanning is where Spring Boot's auto-configuration "conditions" evaluation happens — 200+ conditions evaluated during startup. GraalVM native compilation moves all this to build time, eliminating it from startup entirely.

---

### 💻 Code Example

**Example 1 — Understanding what BFPP does for @Value:**

```java
// What you write:
@Service
public class PaymentService {
    @Value("${stripe.api.key}")
    private String apiKey;  // will be "sk_live_..." after BFPP runs
}

// In application.properties:
// stripe.api.key=sk_live_xyz123

// Under the hood, PropertySourcesPlaceholderConfigurer resolves
// the ${stripe.api.key} placeholder in the BeanDefinition's
// property value BEFORE PaymentService is instantiated.
```

**Example 2 — Custom BFPP: marking beans as lazy by pattern:**

```java
@Component
public class LazyByPackageBeanFactoryPostProcessor
        implements BeanFactoryPostProcessor, PriorityOrdered {

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory beanFactory) {

        for (String beanName : beanFactory.getBeanDefinitionNames()) {
            BeanDefinition def = beanFactory.getBeanDefinition(beanName);
            String className = def.getBeanClassName();
            // Mark all reporting beans as lazy
            if (className != null &&
                    className.startsWith("com.example.reporting")) {
                def.setLazyInit(true);
            }
        }
    }

    @Override
    public int getOrder() {
        return Ordered.LOWEST_PRECEDENCE;
    }
}
```

**Example 3 — BeanDefinitionRegistryPostProcessor for dynamic bean registration:**

```java
@Component
public class PluginBeanRegistrar
        implements BeanDefinitionRegistryPostProcessor {

    @Override
    public void postProcessBeanDefinitionRegistry(
            BeanDefinitionRegistry registry) throws BeansException {

        // Scan external plugin JARs and register their beans
        ServiceLoader<Plugin> plugins = ServiceLoader.load(Plugin.class);
        for (Plugin plugin : plugins) {
            GenericBeanDefinition def = new GenericBeanDefinition();
            def.setBeanClass(plugin.getClass());
            def.setScope(BeanDefinition.SCOPE_SINGLETON);
            registry.registerBeanDefinition(
                plugin.getClass().getSimpleName(), def);
            log.info("Registered plugin: {}", plugin.getClass());
        }
    }

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory factory) {
        // No-op — registration done above
    }
}
```

---

### ⚖️ Comparison Table

| Processor                           | Operates On             | When Runs              | Can Add Beans         | Use Case                              |
| ----------------------------------- | ----------------------- | ---------------------- | --------------------- | ------------------------------------- |
| **BeanFactoryPostProcessor**        | BeanDefinitions         | Before instantiation   | Yes (modify registry) | Property resolution, metadata tweaks  |
| BeanDefinitionRegistryPostProcessor | BeanDefinition registry | Earliest (before BFPP) | Yes (add to registry) | Auto-config, conditional registration |
| BeanPostProcessor                   | Bean instances          | After instantiation    | No                    | AOP, @Autowired, @PostConstruct       |

**How to choose:** Use `BeanDefinitionRegistryPostProcessor` to add new bean definitions (e.g., plugin loading, auto-config). Use `BeanFactoryPostProcessor` to modify existing definitions (e.g., property resolution, scope changes). Use `BeanPostProcessor` to enhance bean instances after they're created.

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                        |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| BeanFactoryPostProcessor and BeanPostProcessor are similar              | Different phases: BFPP modifies definitions before any instantiation; BPP modifies instances after. Never confuse them.                                                        |
| You can safely call getBean() inside a BFPP                             | Calling getBean() in a BFPP instantiates a bean before BeanPostProcessors are registered — the bean won't receive @Autowired injection or AOP proxying. Spring logs a warning. |
| @Value works without any BFPP                                           | @Value resolution requires PropertySourcesPlaceholderConfigurer (a BFPP). Spring Boot auto-registers it. Without it, @Value fields get literal "${property.key}" strings.      |
| BeanDefinitionRegistryPostProcessor runs after BeanFactoryPostProcessor | Registry processors run FIRST (they're a sub-interface); factory processors run after.                                                                                         |

---

### 🚨 Failure Modes & Diagnosis

**"Unsatisfied dependency" caused by early bean creation in BFPP**

**Symptom:**
`WARNING: Bean 'dataService' is not eligible for getting processed by all BeanPostProcessors (for example: not eligible for auto-proxying)`

**Root Cause:**
A `BeanFactoryPostProcessor` implementation calls `beanFactory.getBean("dataService")` to read some configuration. This forces `dataService` to be instantiated before `BeanPostProcessors` are registered. The bean is created without `@Autowired` injection or AOP proxy wrapping.

**Diagnostic Command / Tool:**

```bash
logging.level.org.springframework.context.support=DEBUG
# Look for: "Bean 'X' is not eligible for getting processed
# by all BeanPostProcessors"
```

**Fix:**

```java
// BAD: getting a bean inside a BFPP
@Component
public class MyBFPP implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory factory) {
        // Forces early instantiation — bad!
        DataService svc = factory.getBean(DataService.class);
        String config = svc.getConfig();
        // ...use config to modify definitions
    }
}

// GOOD: read configuration from Environment, not beans
@Component
public class MyBFPP implements BeanFactoryPostProcessor,
        EnvironmentAware {
    private Environment env;

    @Override
    public void setEnvironment(Environment env) {
        this.env = env;  // Environment is available early
    }

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory factory) {
        String config = env.getProperty("my.config");
        // ...use config to modify definitions
    }
}
```

**Prevention:** Never call `getBean()` inside a `BeanFactoryPostProcessor`. Use `Environment`, `@Value` on the BFPP itself (resolved early), or read files directly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `BeanFactory` — BFPP receives the BeanFactory to modify
- `BeanDefinition` — the object BFPP reads and modifies
- `Bean Lifecycle` — BFPP operates in the first phase before instantiation

**Builds On This (learn these next):**

- `Auto-Configuration` — Spring Boot's auto-configuration is a BeanDefinitionRegistryPostProcessor pattern
- `@Conditional annotations` — condition evaluation happens inside BFPPs during auto-configuration
- `BeanPostProcessor` — the complementary extension point for bean instances

**Alternatives / Comparisons:**

- `BeanPostProcessor` — post-creation instance hook (complementary, not alternative)
- `ImportBeanDefinitionRegistrar` — another way to register bean definitions programmatically from `@Import`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A hook that runs before bean creation     │
│              │ to modify or add BeanDefinitions          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Bean definitions need runtime values      │
│ SOLVES       │ (${property}) and conditional registration│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ BFPP edits the RECIPE; BPP edits the      │
│              │ COOKED DISH — completely different phases │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ You need to modify bean metadata, add     │
│              │ beans dynamically, or resolve properties  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never call getBean() inside a BFPP —      │
│              │ forces early, un-post-processed creation  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full pre-instantiation control vs         │
│              │ complexity; mistakes cause hard-to-debug  │
│              │ "bean created too early" warnings         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Edit the blueprint before building —     │
│              │  not the building after it's built."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor → Auto-Configuration → │
│              │ @Conditional                              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ConfigurationClassPostProcessor` is a `BeanDefinitionRegistryPostProcessor` with `PriorityOrdered` — it runs first among all post-processors. It processes `@Configuration` classes and registers `@Bean` method definitions. If someone writes a custom `BeanDefinitionRegistryPostProcessor` that also uses `PriorityOrdered`, there are now two processors at the same priority level. How does Spring decide which one runs first? And if the custom processor adds a `@Bean` that conflicts with one registered by `ConfigurationClassPostProcessor`, which wins?

**Q2.** Spring Boot's `@ConditionalOnMissingBean` allows auto-configuration beans to be overridden by user-defined beans. This works by evaluating conditions inside a `BeanDefinitionRegistryPostProcessor`. But the condition must know what beans already exist to determine "is there a missing bean?" — and not all user beans may have been registered yet at that point. How does Spring Boot's condition evaluation handle this ordering problem without forcing all user beans to be registered before auto-configuration runs?
