---
id: SPR-066
title: Spring Native and GraalVM Integration
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-003, SPR-044, SPR-064
used_by:
related: SPR-065, SPR-067, SPR-073
tags:
  - spring
  - java
  - advanced
  - deep-dive
  - internals
  - first-principles
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 66
permalink: /spr/spring-native-and-graalvm-integration/
---

# SPR-066 - Spring Native and GraalVM Integration

⚡ TL;DR - GraalVM AOT compiles a Spring Boot application to a self-contained native binary; startup drops from seconds to milliseconds at the cost of build time and dynamic feature restrictions.

| Field          | Value                                                                                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-003 - Why Spring Boot Changed Java Development]], [[SPR-044 - Spring Boot Auto-configuration Deep Dive]], [[SPR-064 - Spring Framework Internals Deep Dive]]  |
| **Used by**    | -                                                                                                                                                                   |
| **Related**    | [[SPR-065 - Spring Reactive Model (Project Reactor Internals)]], [[SPR-067 - Spring Specification and Extension Points]], [[SPR-073 - Spring Boot AOT Compilation]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Spring Boot applications start in 3-15 seconds. In serverless (AWS Lambda, Azure Functions), this means cold starts add 3-15 seconds of latency to the first request after scale-to-zero. In autoscaling scenarios, new pod startup time limits how fast a cluster can respond to traffic spikes. Memory footprint of a JVM application is 200-500MB minimum.

**THE BREAKING POINT:**

For serverless workloads with frequent cold starts, and for microservices architectures with hundreds of pods, the JVM warm-up cost becomes a significant infrastructure cost (more persistent instances required) and UX issue (user waits for cold start).

**THE INVENTION MOMENT:**

GraalVM native image uses AOT (Ahead-Of-Time) compilation to analyse the entire application's reachable code at build time, compile it to native machine code, and embed the heap and Java standard library into a self-contained binary. No JVM required at runtime. Result: 50-100ms startup, 50-80% memory reduction.

**EVOLUTION:**

- **2016:** GraalVM project announced at Oracle Labs
- **2019:** `spring-graalvm-native` experimental project started
- **2021:** Spring Native 0.10 - first practical Spring Boot native image support
- **2022:** Spring Boot 3.0 + Spring Framework 6.0 - native image support first-class (no separate Spring Native dependency)
- **2023:** Spring Boot 3.1 - optimised AOT with `@BeanFactoryInitializationAotProcessor`; GraalVM CE 23 included in JDK distributions

---

### 📘 Textbook Definition

**GraalVM native image** compiles a Java application to a native executable using **Ahead-Of-Time (AOT) compilation**. The **closed-world assumption** requires that all reachable code is known at build time - dynamic class loading, reflection, serialisation, and JNI must be declared via **reachability metadata** (`reflect-config.json`, `resource-config.json`, `proxy-config.json`). **Spring Boot AOT processing** (run during `mvn package` or `gradle nativeBuild`) analyses the `BeanDefinition` graph at build time and generates source code (`BeanFactory.java`) and reachability metadata, replacing runtime reflection with pre-generated registration code.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Native image builds the entire application into a single native binary at package time, so at runtime there is no JVM to start and no classes to JIT-compile.

> Building a native image is like pre-cooking an entire meal and vacuum-sealing it. Traditional Java starts from raw ingredients (JVM + JARs) and cooks everything fresh (JIT compilation). Native image pre-cooks everything at package time. The meal is ready in seconds, not 15 minutes - but you can't change the recipe after sealing (no dynamic class loading).

**One insight:** The closed-world assumption is not a limitation of GraalVM - it is a _design choice_ that enables complete static analysis. Every dynamic feature Spring uses (reflection, proxies, `@Configuration` processing) must be converted to static code to cross the closed-world boundary.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All reachable code must be known at build time (closed-world assumption)
2. Reflection, serialisation, and resource loading require explicit metadata registration
3. Dynamic class loading (`ClassLoader.loadClass()`) is impossible at runtime
4. CGLIB dynamic subclass proxies cannot be created at runtime - all proxies must be pre-generated
5. Build time is measured in minutes; startup time is measured in milliseconds

**DERIVED DESIGN:**

From invariant 1+2 → Spring Boot AOT generates `reflect-config.json` for every Spring-managed class that uses reflection (nearly all of them), replacing runtime introspection with pre-computed metadata.
From invariant 4 → Spring Framework 6.0 switched from CGLIB proxies to **interface-based JDK proxies** for all cases where an interface is present. Where CGLIB is required (no interface), Spring pre-generates the subclass at AOT time.
From invariant 5 → The build pipeline: `mvn package` runs `SpringApplicationAotProcessor`, which simulates Phase 1 of the application context to discover all beans, then generates source code and metadata before `native-image` compilation begins.

**THE TRADE-OFFS:**

**Gain:** Sub-100ms startup; 50-80% memory reduction; no JVM required in container; no JIT warm-up period.

**Cost:** 3-15 minute build time (vs 10-30 seconds for JVM JAR); no dynamic class loading; debugging is harder (no JVM tooling); JIT optimisations like profile-guided optimisation are absent; GraalVM Enterprise adds cost.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Analysing all reachable code at build time to produce a closed-world compilation genuinely requires knowing everything statically - dynamic features must be declared.

**Accidental:** Spring's heavy use of reflection, CGLIB proxies, and runtime `BeanDefinition` processing in previous versions made native compilation nearly impossible. Spring Framework 6 + Boot 3 eliminated most accidental complexity by shifting to AOT-compatible patterns.

---

### 🧪 Thought Experiment

**SETUP:** A Spring Boot app is deployed on AWS Lambda, invoked 100 times per day but with traffic arriving in 5-minute bursts every hour.

**WITHOUT native image:**

Lambda keeps the JVM container warm for ~15 minutes after last invocation. Each burst beyond that incurs a cold start: 3-8 second Lambda cold start (JVM startup + Spring context refresh). First user in each burst waits 3-8 seconds. 24 bursts/day × 8 seconds = 192 seconds of cold start latency paid by real users.

**WITH native image:**

Lambda cold start = 50-200ms. First user in each burst waits 200ms instead of 8 seconds. Lambda can also scale to zero more aggressively (the penalty for cold start is now negligible), reducing infrastructure cost by 60-80% for sporadic workloads.

**THE INSIGHT:**

Native image does not make a warm Spring application faster (JIT-compiled JVM code may be faster for throughput). It eliminates the _startup tax_ that makes the JVM unsuitable for short-lived workloads.

---

### 🧠 Mental Model / Analogy

> Traditional JVM Java is like a restaurant that cooks to order: the kitchen (JVM) starts from scratch for each order, heats up (class loading), learns the menu by experience (JIT compilation), and eventually becomes fast. GraalVM native image is like a meal kit delivery service: everything is pre-prepared at the factory (AOT compilation) and arrives ready to heat in 30 seconds (sub-100ms startup). The trade-off: you cannot customise your meal after packaging (no runtime dynamic loading), and the factory prep takes hours (long build time).

**Element mapping:**

- Restaurant kitchen → JVM runtime
- Heating up / learning the menu → class loading + JIT compilation
- Meal kit factory → GraalVM `native-image` build process
- Pre-prepared meal → native executable
- Cannot customise after packaging → closed-world assumption
- Factory prep time → 3-15 minute build time
- Arriving ready to eat → sub-100ms startup

Where this analogy breaks down: the JVM can sometimes exceed native image peak throughput because JIT compilation generates profile-guided optimised machine code at runtime that AOT cannot match without runtime profiling data.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of shipping a Java program that needs a JVM to run, you compile it into a direct machine-code program (like a C or Go program). It starts almost instantly and uses less memory, but takes much longer to build and you can't load new code at runtime.

**Level 2 - How to use it (junior developer):**
Add `org.graalvm.buildtools:native-maven-plugin`. Run `mvn -Pnative package`. This produces a native executable in `target/`. For Docker: use `paketobuildpacks/builder:tiny` (Spring Boot's default native builder). Test the native image: `./target/myapp` - starts in under 1 second. For Lambda: `bootstrap` file is the native binary.

**Level 3 - How it works (mid-level engineer):**
`mvn package` with the native profile triggers `SpringApplicationAotProcessor` as a Maven step before `native-image`. The AOT processor starts the Spring `ApplicationContext` in a _simulation mode_ (does not start web server), traverses the `BeanDefinition` graph, calls `BeanRegistrationAotProcessor` on each bean, and writes: (1) `reflect-config.json` for all reflected classes, (2) `BeanFactory.java` pre-generating all bean creation code, (3) `proxy-config.json` for all needed JDK proxy interfaces. Then `native-image` performs static analysis using these inputs, tracing all reachable code and compiling to native. The resulting binary contains the application heap snapshot.

**Level 4 - Why it was designed this way (senior/staff):**
The Spring Framework 6 team made a deliberate architectural shift: `@Configuration` classes, previously processed via reflection and CGLIB at runtime, are now converted to explicit `BeanDefinition` registrations and factory methods by the AOT processor. This is the `@Configuration(proxyBeanMethods=false)` default shift combined with AOT-generated `BeanFactory`. The choice to generate Java source code (not bytecode) for the AOT output was intentional: source code is debuggable, inspectable, and compatible with all JVM and native compilation paths. The generated code can be inspected in `target/spring-aot/main/sources/`.

**Expert Thinking Cues:**

- `@NativeHints`, `@TypeHint`, `@ResourceHint`, `@JdkProxyHint` are the extension points for library authors to register metadata
- `RuntimeHintsRegistrar` is the programmatic API for registering hints from library code
- The GraalVM `native-image-agent` can generate reachability metadata by _running the JVM application_ with `-agentlib:native-image-agent=config-output-dir=...`

---

### ⚙️ How It Works (Mechanism)

```
Build phase (mvn -Pnative package):
  1. Spring AOT Processing
     ├─ SpringApplicationAotProcessor.main()
     ├─ Simulates ApplicationContext refresh
     │   (Phase 1 only - no web server)
     ├─ BeanRegistrationAotProcessor per bean
     │   ├─ Generates BeanFactory.java
     │   ├─ Registers reflect-config.json entries
     │   └─ Pre-generates CGLIB subclasses
     └─ Writes to target/spring-aot/

  2. native-image compilation
     ├─ Reads all source + reflect-config.json
     ├─ Static reachability analysis
     │   ├─ Traces all reachable classes/methods
     │   └─ Eliminates unreachable code (DCE)
     ├─ AOT compiles reachable code to machine code
     └─ Embeds initial heap snapshot
     Output: target/myapp (native executable)

Runtime phase (./target/myapp):
  1. OS loads native binary: ~10ms
  2. Restore embedded heap snapshot
  3. Run pre-generated BeanFactory.java
     (no reflection, no BeanFactoryPostProcessor)
  4. Start embedded web server
  Total: 50-200ms
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Developer: mvn -Pnative package]
     |
     ├─ Spring AOT: simulate context
     |    └─ Generate BeanFactory.java
     |       + reflect-config.json
     |         ← YOU ARE HERE (AOT output)
     |
     ├─ native-image compiler
     |    ├─ Static analysis (5-15 min)
     |    └─ Machine code compilation
     |
[./target/myapp (native binary)]
     |
     ├─ 50ms: OS loads binary
     ├─ Restore heap snapshot
     ├─ Pre-generated BeanFactory runs
     └─ HTTP server ready
[First request served at ~100ms]
```

**FAILURE PATH:**

- Reflection used without hint → `ClassNotFoundException` or `NullPointerException` at runtime in native (succeeds on JVM)
- CGLIB proxy needed but not pre-generated → `CannotCreateProxyException`
- External config file loaded at runtime via `ClassLoader.getResourceAsStream()` → returns null unless declared in `resource-config.json`

**WHAT CHANGES AT SCALE:**

In a Kubernetes HPA scenario: native pods auto-scale to 10 pods in 5 seconds (100ms startup × 10). JVM pods take 30-150 seconds (3-15s startup × 10). For event-driven autoscaling (KEDA), native image makes scale-from-zero practical because the first request penalty is milliseconds.

---

### 💻 Code Example

**BAD - reflection at runtime without hints, fails in native:**

```java
// Works on JVM, fails in native image
@Service
public class DynamicSerializer {
    public Map<String, Object> serialize(Object obj) {
        Map<String, Object> map = new HashMap<>();
        // Reflection without hint registration
        for (Field field :
                obj.getClass().getDeclaredFields()) {
            field.setAccessible(true);  // fails native
            map.put(field.getName(),
                field.get(obj));
        }
        return map;
    }
}
```

**GOOD - register hints for reflection:**

```java
// RuntimeHintsRegistrar registered via
// META-INF/spring/aot.factories
public class DomainHints
        implements RuntimeHintsRegistrar {
    @Override
    public void registerHints(
            RuntimeHints hints, ClassLoader loader) {
        // Register all domain classes for reflection
        hints.reflection()
            .registerType(Order.class,
                MemberCategory.INVOKE_PUBLIC_METHODS,
                MemberCategory.DECLARED_FIELDS)
            .registerType(User.class,
                MemberCategory.INVOKE_PUBLIC_METHODS,
                MemberCategory.DECLARED_FIELDS);
    }
}

// Or use Jackson's native support (Spring Boot 3+)
// Jackson registers hints automatically for
// @JsonProperty-annotated classes
@JsonAutoDetect(fieldVisibility = ANY)
public record Order(Long id, String item) {}
```

**Test native hints in JVM mode:**

```java
@Test
void domainHintsCoversOrder() {
    RuntimeHints hints = new RuntimeHints();
    new DomainHints().registerHints(hints, getClass()
        .getClassLoader());

    assertThat(RuntimeHintsPredicates.reflection()
        .onType(Order.class)
        .withMemberCategories(
            MemberCategory.DECLARED_FIELDS))
        .accepts(hints);
}
```

---

### ⚖️ Comparison Table

| Dimension        | JVM (jar)                  | Native Image     | GraalVM JIT (EE)       |
| ---------------- | -------------------------- | ---------------- | ---------------------- |
| Startup time     | 3-15 seconds               | 50-200ms         | 3-15 seconds           |
| Peak throughput  | High (JIT optimised)       | Medium (AOT)     | Very high              |
| Memory (idle)    | 150-500MB                  | 30-100MB         | 150-500MB              |
| Build time       | 10-30 seconds              | 3-15 minutes     | 10-30 seconds          |
| Dynamic features | Full                       | Restricted       | Full                   |
| Debugging        | JVM tools (JFR, heap dump) | Limited (gdb)    | JVM tools              |
| Best for         | Long-running services      | Serverless, CLIs | Latency-sensitive SaaS |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                          |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Native image is faster at everything"            | Native image excels at startup and memory. JIT-compiled JVM can outperform native for sustained high throughput because JIT uses runtime profiling.                              |
| "Spring Boot 3 native 'just works'"               | Spring Boot 3 handles Spring's own reflection automatically. Third-party libraries without native hints will fail at runtime. `native-image-agent` helps discover missing hints. |
| "You can't use reflection at all in native image" | You can use reflection, but must register types via `RuntimeHints` or `reflect-config.json` at build time. Unregistered reflection throws at runtime.                            |
| "Native images can't be profiled"                 | GraalVM supports profiling with `async-profiler` for native images. JVM Flight Recorder is not available, but alternatives exist.                                                |
| "CGLIB proxies don't work in native"              | `@Configuration(proxyBeanMethods=false)` removes the need for CGLIB. For AOP, Spring Framework 6 pre-generates proxy classes at AOT time for native compatibility.               |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Missing reflection hint causes ClassNotFoundException in native**

**Symptom:** Application starts normally on JVM but throws `ClassNotFoundException` or returns null in native image; typically in serialisation, custom factory methods, or third-party library init.

**Root Cause:** A class is accessed via reflection at runtime but was not included in `reflect-config.json` during build. The native image static analyser could not trace the reflective access and excluded the class.

**Diagnostic:**

```bash
# Run with native-image-agent to capture
# all runtime reflection
java -agentlib:native-image-agent=\
  config-output-dir=src/main/resources/META-INF/\
  native-image \
  -jar target/myapp.jar
# Exercise all code paths, then build native
mvn -Pnative package
```

**Fix:** Register the class in `RuntimeHintsRegistrar` or `reflect-config.json`.

**Prevention:** Run native image integration tests in CI (`@NativeTest` Spring Boot test slice) to catch missing hints before production.

---

**Mode 2: Long native image build in CI blows pipeline budget**

**Symptom:** `mvn -Pnative package` takes 12 minutes in CI; pipeline budget is 10 minutes; build fails on timeout.

**Root Cause:** GraalVM `native-image` static analysis has O(n²) complexity in reachable code size; large Spring applications with many libraries take proportionally longer.

**Diagnostic:**

```bash
# Profile native image build time
# GraalVM build report (GraalVM 22.3+)
-H:+BuildReport
# Shows which phases take the longest
```

**Fix:** Exclude unused Spring dependencies (remove `spring-boot-starter-web` if using `spring-boot-starter-webflux`). Use `@SpringBootApplication(exclude={...})` to exclude unused auto-configurations. Use GraalVM Enterprise (2-3× faster AOT compilation).

**Prevention:** Measure binary size and build time as CI metrics; set alerts when either grows beyond thresholds.

---

**Mode 3: Secrets loaded via reflection at runtime expose credentials (Security failure mode)**

**Symptom:** A custom `Environment` post-processor loads secrets from an external system at startup using reflection. In native, the reflective loader fails silently; secrets fall back to defaults hardcoded in application.yml.

**Root Cause:** Native image fails to load the secret-fetching class via reflection; no hint was registered; fallback default credentials used silently.

**Diagnostic:**

```bash
# Add -Djava.security.debug=access in native
# to see security manager access failures
./myapp -Djava.security.debug=access 2>&1 \
  | grep "access denied"
# Compare environment values in native vs JVM mode
curl http://localhost:8080/actuator/env \
  | jq '.propertySources[] | .name'
```

**Fix:** Register secret-loader class with `RuntimeHints`. Add native image integration tests that assert secrets are non-default values. Never provide non-empty default values for credentials in `application.yml`.

**Prevention:** Fail-fast: configure `spring.config.import=optional:vault://...` with `fail-on-empty-location=true` so missing secrets cause startup failure in native, not silent fallback.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-003 - Why Spring Boot Changed Java Development]] - the auto-configuration model being extended
- [[SPR-064 - Spring Framework Internals Deep Dive]] - Phase 1 (BeanDefinition) that AOT processes
- [[SPR-044 - Spring Boot Auto-configuration Deep Dive]] - what auto-configuration registers that AOT must handle

**Builds On This (learn these next):**

- [[SPR-073 - Spring Boot AOT Compilation]] - the Spring-specific AOT layer detail
- [[SPR-067 - Spring Specification and Extension Points]] - writing `RuntimeHintsRegistrar`

**Alternatives / Comparisons:**

- Micronaut native - compile-time DI from the start; simpler native path (no reflection by design)
- Quarkus native - similar GraalVM integration; strong Kubernetes-native story
- Virtual threads (Java 21) - alternative to native for startup improvement in Kubernetes; JVM with near-native startup when combined with Spring Boot CDS (Class Data Sharing)

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | AOT compilation to native binary via     |
|               | GraalVM; no JVM at runtime               |
| PROBLEM       | JVM startup time (3-15s) unacceptable for|
|               | serverless, autoscaling, CLI tools       |
| KEY INSIGHT   | Closed-world assumption: all reachable   |
|               | code known at build time; dynamic = hint |
| USE WHEN      | Serverless, frequent cold starts, CLIs,  |
|               | memory-constrained containers            |
| AVOID WHEN    | JIT throughput needed; heavy dynamic     |
|               | class loading; 3rd-party libs lack hints |
| TRADE-OFF     | Startup/memory vs build time + dynamic   |
|               | feature restrictions                     |
| ONE-LINER     | mvn -Pnative package: 15min build →      |
|               | 100ms startup; reflect-config required   |
| NEXT EXPLORE  | SPR-073 (AOT Compilation Detail)         |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Native image = closed-world: reflection, CGLIB, and dynamic loading must be declared via `RuntimeHints` at build time
2. Spring Boot 3 AOT processor handles Spring's own reflection; third-party libraries may need manual hints
3. Use `native-image-agent` on a JVM run to auto-discover all missing hints before native build

**Interview one-liner:** "GraalVM native image uses AOT compilation with a closed-world assumption to produce a self-contained binary with sub-100ms startup; Spring Boot 3's AOT processor generates the required reflection metadata and pre-builds the BeanFactory to enable this for Spring applications."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Pay costs at build time rather than runtime to improve operational efficiency._ Any computation that can be determined statically (from source code and configuration) can be moved from runtime to build time. The trade-off is always the same: longer build, faster and more predictable runtime.

**Where else this pattern appears:**

- **TypeScript compilation** - type checking at build time (not runtime); runtime JavaScript has zero type overhead
- **Webpack tree shaking** - unused code eliminated at build time; bundle smaller at runtime
- **SQL prepared statements** - query plan computed once at prepare time, reused for each execution

---

### 💡 The Surprising Truth

GraalVM native image was not originally designed for microservices. It was created for **Truffle** - GraalVM's polyglot language framework - which needed to run Ruby, Python, and JavaScript programs on the JVM at near-native speed. The native image capability was a side project to make Truffle-based language runtimes distributable without requiring a JVM installation. Oracle Labs open-sourced native image in 2016 as part of the broader GraalVM project, not anticipating that the Java microservices community would adopt it as the primary motivation. The Spring team's decision to invest heavily in native compatibility (Spring Boot 3, Spring Framework 6) is the retrospective validation of a tool that was never designed for its primary use case.

---

### 🧠 Think About This Before We Continue

**Question 1 (B - Scale):** A Spring Boot native image application is deployed in Kubernetes and uses HPA autoscaling. The native startup is 100ms. Kubernetes `readinessProbe` is configured with `initialDelaySeconds: 0` and `periodSeconds: 1`. The HPA is configured to scale from 1 to 50 pods when CPU > 70%. Describe the end-to-end scale-out sequence from traffic spike detection to all 50 pods serving traffic, including the timing windows involved.

_Hint:_ Consider HPA reaction time (~15-30s), pod scheduling time, container start time, native image startup, `readinessProbe` passing, Endpoints object update, `kube-proxy` / CNI rule propagation, and Spring's `Lifecycle.start()` completion.

**Question 2 (C - Design Trade-off):** A payment service is being migrated to native image. It uses a JAXB-generated XML marshaller for ISO 20022 payment messages. JAXB relies heavily on reflection to bind XML elements to generated Java classes. The generated classes total 500 classes. Describe two approaches to making this work in native image, and evaluate the build-time and maintenance trade-offs of each.

_Hint:_ Consider (a) running `native-image-agent` during a JAXB marshalling test to auto-generate `reflect-config.json` for all 500 classes, vs (b) registering hints programmatically in a `RuntimeHintsRegistrar` via class path scanning. Which is maintainable as the JAXB schema evolves?

**Question 3 (E - First Principles):** GraalVM's closed-world assumption means that all code reachable from `main()` must be included in the binary. However, Spring's auto-configuration registers beans conditionally based on classpath presence (`@ConditionalOnClass`). Explain how the Spring AOT processor reconciles these two facts: how does it determine which conditional beans to include in the native image when the conditions are evaluated at build time with a fixed classpath?

_Hint:_ The AOT processor runs a full Spring context simulation at build time using the _build-time classpath_ (which is fixed). All `@ConditionalOnClass` evaluations are performed during this simulation with the actual build classpath. The result is a `BeanDefinition` graph where all conditions have been evaluated and resolved - this resolved graph is what gets compiled into the native image.
