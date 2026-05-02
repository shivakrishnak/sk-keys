---
layout: default
title: "Native Image"
parent: "Java & JVM Internals"
nav_order: 305
permalink: /java/native-image/
number: "0305"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - GraalVM
  - AOT (Ahead-of-Time Compilation)
  - JVM
  - Bytecode
used_by:
  - GC Tuning
related:
  - GraalVM
  - AOT (Ahead-of-Time Compilation)
  - JIT Compiler
  - Tiered Compilation
tags:
  - jvm
  - graalvm
  - performance
  - java-internals
  - deep-dive
---

# 0305 — Native Image

⚡ TL;DR — GraalVM Native Image compiles Java ahead-of-time to a self-contained native executable: no JVM required, millisecond startup, and dramatically lower memory — at the cost of closed-world build constraints.

| #0305 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | GraalVM, AOT (Ahead-of-Time Compilation), JVM, Bytecode | |
| **Used by:** | GC Tuning | |
| **Related:** | GraalVM, AOT Compilation, JIT Compiler, Tiered Compilation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every Java application requires a JVM to run. The JVM startup sequence: load JVM native libraries, initialize GC, load core classes (200–500 classes before `main()` runs), start daemon threads, and then begin executing user code. This costs 500ms–5 seconds depending on the framework. For CLIs, batch tools, and serverless functions, this startup cost is paid on every invocation — making Java an impractical choice.

**THE BREAKING POINT:**
A developer writes a Java CLI tool that converts file formats. Running it takes 1.8 seconds, of which 1.6 seconds is JVM startup, and 0.2 seconds is actual work. Users notice the delay. The same tool in Go: 5ms. The Java version gets replaced. Java lost a market — CLIs — not because of the language but because of the runtime cost.

**THE INVENTION MOMENT:**
This is exactly why **Native Image** was created — to produce a self-contained compiled binary from Java code, with no JVM startup overhead, sub-100ms startup, and a compact memory footprint, making Java competitive with Go and Rust in deployment environments where a JVM is unacceptable.

---

### 📘 Textbook Definition

**Native Image** is a GraalVM technology that performs ahead-of-time compilation of Java bytecode to a native platform executable using the closed-world assumption. The `native-image` build tool runs points-to analysis to determine all reachable code, compiles it with the Graal AOT compiler, links it with SubstrateVM (a minimal Java runtime providing GC, thread management, and JNI), and produces a standalone binary. The binary contains the compiled application code, a pre-initialized heap (the "image heap"), and the SubstrateVM runtime, requiring no external JVM installation to execute.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Package your entire Java application — code, libraries, and tiny runtime — into a single native binary that starts instantly.

**One analogy:**
> Making a native image is like freeze-drying a fully cooked meal: all the work is done in advance (cooking → compilation), the result is compact (package weight → binary size), and serving is instant (add hot water → run binary). The limitation: you cannot change the ingredients after freeze-drying (closed world → no dynamic class loading). But for known meals, it is dramatically faster to serve.

**One insight:**
The "image heap" is Native Image's secret weapon for framework startup performance. In JVM mode, Spring Boot's `ApplicationContext` initialization builds thousands of bean definitions, proxy classes, and component graphs at runtime. With Native Image, Spring Boot performs this initialization at build time and serializes the result into the image heap. When the binary starts, it reads that pre-computed data directly from memory — 3 seconds of work becomes 20ms of I/O.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A native binary needs no interpreter layer — the CPU executes instructions directly at full speed from byte zero.
2. Pre-initializing application state at build time avoids re-computing it on every invocation.
3. Static reachability analysis can eliminate dead code, shrinking the binary and improving startup.

**DERIVED DESIGN:**
Native Image's build process follows five phases:

**Phase 1 — Analysis:**
Points-to analysis from all entry points. This is an iterative fixed-point computation: starting from main, trace all method calls, field accesses, and object allocations. Done when no new reachable elements are found. Result: reachability set (typically 60–80% of code is unreachable and excluded).

**Phase 2 — Build-time initialization:**
Configurable classes can be initialized at build time (their `<clinit>` runs during image build). The resulting static state is baked into the image heap. Spring Boot, Quarkus, and Micronaut use this extensively.

**Phase 3 — Compilation:**
All reachable methods compiled by the Graal AOT compiler. The same optimization phases as Graal JIT, but without profile data (unless PGO is used — see GraalVM 21+ PGO support).

**Phase 4 — Image heap serialization:**
Runtime constants, pre-initialized objects, and class metadata are written to the binary's data segment. This image heap is memory-mapped on startup — instant access, no reconstruction.

**Phase 5 — Linking:**
Compiled code + SubstrateVM GC/threading + image heap → platform binary (ELF on Linux, Mach-O on macOS, PE on Windows).

```
┌────────────────────────────────────────────────────┐
│           Native Image Binary Layout               │
│                                                    │
│  .text section:                                    │
│    [Compiled application code]                     │
│    [SubstrateVM runtime code]                      │
│    [JNI stubs, signal handlers]                    │
│                                                    │
│  .data section:                                    │
│    [Image heap: pre-initialized Java objects]      │
│    [Class metadata, string constants]              │
│    [Pre-built application context (framework)]     │
│                                                    │
│  .rodata section:                                  │
│    [String literals, method tables]                │
└────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** <100ms startup; 50–80% lower memory; no JVM installation required; smaller attack surface; deterministic performance.
**Cost:** Build time 2–15 minutes; dynamic Java features restricted (reflection, dynamic proxies, classpath scanning must be declared); peak throughput may be 10–20% below JIT without PGO; debugging harder (no bytecode-level tooling unless DWARF debug info included).

---

### 🧪 Thought Experiment

**SETUP:**
Deploy a REST API endpoint that receives a POST request, validates JSON, queries a database, and returns a response. Compare cold start and steady-state behavior.

JVM (Spring Boot, standard):
- Container starts: 0ms overhead (always warm in production with readiness probes).
- But during rollout: pod starts, 3.5s before `READY`, 30s before fully warmed JIT.
- Memory: 512MB (JVM + heap + metaspace + code cache).
- Steady state throughput: 12,000 req/s (fully JIT-warmed).

Native Image (Spring Boot 3 native):
- Container starts: 70ms to `READY`. Zero warmup.
- First request: 4ms. Same performance as steady state.
- Memory: 100MB (native heap only, no JVM overhead).
- Steady state throughput: 10,000 req/s (no JIT adaptation).

On AWS Lambda (invoked every 5 minutes):
JVM cold start: 3,500ms (charged/penalized).
Native Image cold start: 70ms (100ms Lambda response).
Result: Native Image is the only viable Java option for this deployment pattern.

**THE INSIGHT:**
Native Image's value is deployment-pattern-specific. For always-on services with stationary traffic, JIT wins at peak. For any environment with cold starts, scale-to-zero, or strict startup SLAs, Native Image is the only viable Java approach.

---

### 🧠 Mental Model / Analogy

> Think of a native image as a pre-packaged meal-kit vs a restaurant kitchen. The JVM is a fully-equipped restaurant kitchen: capable of cooking anything, but needs setup time. Native Image is a vacuum-sealed meal-kit: everything is pre-assembled for the specific meal, requires only 2 minutes to heat (startup), uses minimal counter space (memory), but cannot make dishes not in the kit (no dynamic class loading). For home delivery (serverless/edge), the meal-kit wins. For a busy restaurant (high-volume always-on service), the full kitchen wins.

- "Vacuum-sealed kit" → native binary with pre-compiled code and image heap.
- "2 minutes to heat" → 70ms startup time.
- "Minimal counter space" → 100MB memory footprint vs 512MB JVM.
- "Only dishes in the kit" → closed-world: only classes reachable at build time.

Where this analogy breaks down: Unlike a meal-kit that cannot be modified, GraalVM Native Image supports some runtime dynamism through explicit configuration — it is not entirely static, just explicitly bounded.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A native image is a single file that contains your entire Java program, ready to run on any compatible computer without installing Java. It starts almost instantly — like a native app on your phone, not a Java app with a startup spinner.

**Level 2 — How to use it (junior developer):**
Use GraalVM's `native-image` tool or framework plugins:
```bash
# With Spring Boot 3+:
mvn -Pnative native:compile
./target/myapp  # starts in 70ms

# With Quarkus:
./mvnw package -Pnative
./target/myapp-runner

# With Micronaut:
mn create-app --features=graalvm myapp
./mvnw package -Dpackaging=native-image
```
Most reflection and proxy usage is handled automatically by framework AOT processors. You only need `reflect-config.json` for custom reflection you add yourself.

**Level 3 — How it works (mid-level engineer):**
The native-image tool runs points-to analysis in a single JVM process that can itself use 8–32GB of RAM and take 5–15 minutes. For each class, it computes: which constructors are called? Which methods are reachable? Which fields are accessed? Through what interfaces? The result is a reachability graph. Only elements in this graph are compiled. Classes with `@NativeImageHint`, `@RegisterForReflection`, or registered in `reflect-config.json` are explicitly added even if not statically reachable.

**Level 4 — Why it was designed this way (senior/staff):**
The image heap is the most architecturally interesting Native Image feature. In Java, class loading triggers `<clinit>` (static initializer) execution. In a JVM, this happens lazily at runtime. Native Image can execute `<clinit>` at build time and serialize the resulting object graph into the image heap — then the binary starts with those objects already in memory, as if they had run at startup. This is how Spring AOT achieves fast startup: the entire BeanFactory is constructed at build time and stored in the image heap. Runtime startup just reads the pre-built factory from a memory-mapped file segment. The tradeoff: build-time initialization must not depend on runtime state (no reading environment variables, no network calls, no file system paths that differ). Spring AOT processor validates this constraint.

---

### ⚙️ How It Works (Mechanism)

**Build Configuration:**
```bash
native-image \
  --no-fallback \                     # fail if features missing
  -H:+ReportExceptionStackTraces \   # better error messages
  -H:Name=myapp \
  -H:Class=com.example.Main \
  --initialize-at-build-time=\       # run <clinit> at build time
    com.example.config,\
    org.apache.logging \
  --initialize-at-run-time=\         # run <clinit> at runtime
    com.example.db.DataSource \
  --features=com.example.GraalFeature \  # custom setup hooks
  -jar myapp-fat.jar
```

**Reflection Configuration:**
```json
// reflect-config.json (auto-generated via agent)
[
  {
    "name": "com.example.ResponseDto",
    "allDeclaredFields": true,
    "allDeclaredMethods": true,
    "allDeclaredConstructors": true,
    "queryAllDeclaredMethods": true
  },
  {
    "name": "com.fasterxml.jackson.databind.ObjectMapper",
    "methods": [{"name": "<init>", "parameterTypes": []}]
  }
]
```

**JNI Configuration:**
```json
// jni-config.json
[
  {
    "name": "java.lang.System",
    "methods": [{"name": "gc", "parameterTypes": []}]
  }
]
```

**Serialization Configuration:**
```json
// serialization-config.json
[
  {"name": "com.example.Order"}
]
```

**Resource Configuration:**
```json
// resource-config.json
{
  "resources": {
    "includes": [
      {"pattern": "application.properties"},
      {"pattern": "\\QMETA-INF/services/\\E.*"}
    ]
  }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

BUILD TIME (CI):
```
[mvn package] → [fat JAR]
    → [native-image tool starts]  ← YOU ARE HERE
    → [Points-to analysis: ~5min]
    → [Build-time init: Spring AOT context]
    → [Graal AOT compilation: ~3min]
    → [Image heap serialization]
    → [SubstrateVM linking]
    → [./myapp binary: 60MB]
    → [Docker: FROM scratch; ADD myapp .]
    → [Image: 80MB vs 500MB JVM image]
```

RUNTIME:
```
[Container/Lambda cold-start]
    → [OS loads binary]
    → [SubstrateVM initializes thread model + GC]
    → [Image heap memory-mapped (pre-built objects ready)]
    → [Application main() called: 70ms after OS invocation]
    → [First HTTP request: 5ms (no warmup)]
```

**FAILURE PATH:**
```
[native-image build fails: unsupported feature]
    → [Error: "Unsupported feature: CGLIB proxy"]
    → [Fix: switch to interface-based proxy]
    → [Or: --features flag with custom substitute]

[Runtime: missing reflection entry]
    → [ClassNotFoundException: com.example.CustomHandler]
    → [Fix: add to reflect-config.json]
    → [Or: re-run agent to auto-capture]
```

**WHAT CHANGES AT SCALE:**
At scale, native image binary deployment in Kubernetes dramatically reduces pod startup time (70ms vs 3500ms) — enabling aggressive autoscaling without "pre-warming" buffers. Container images are smaller (80MB vs 500MB), reducing registry bandwidth and pull time. However, the build pipeline becomes more complex: each service needs a native image build step that takes 5–15 minutes. Teams with 50+ services adopt dedicated native image CI build caches and GraalVM reachability metadata management workflows.

---

### 💻 Code Example

Example 1 — Spring Boot 3 native image build and run:
```bash
# Prerequisites: GraalVM JDK 21+ or Docker BuildKit

# Build:
mvn -Pnative native:compile -DskipTests

# Or with Docker (no local GraalVM needed):
mvn spring-boot:build-image \
  -Dspring-boot.build-image.imageName=myapp:native

# Run (no JVM needed):
./target/myapp

# Output:
# Started MyApplication in 0.071 seconds (process running for 0.08)
```

Example 2 — Quarkus native image (fastest framework):
```bash
# Create native Quarkus app:
quarkus create app --extension=rest com.example:myapp

# Build native:
./mvnw package -Pnative

# Run:
./target/myapp-1.0.0-SNAPSHOT-runner
# Started in 0.019s (Quarkus is particularly fast native)
```

Example 3 — Auto-generating reflection config with agent:
```bash
# Run app with agent to capture all dynamic accesses:
java -agentlib:native-image-agent=\
  config-output-dir=src/main/resources/META-INF/native-image/ \
  -jar myapp.jar

# Run ALL code paths (unit tests, integration tests, API calls):
mvn test  # while agent is running

# Agent generates:
# - reflect-config.json
# - proxy-config.json
# - jni-config.json
# - resource-config.json
# - serialization-config.json

# Now build native image (it will use the generated configs):
native-image -jar myapp.jar
```

Example 4 — @RegisterForReflection annotation (Quarkus):
```java
import io.quarkus.runtime.annotations.RegisterForReflection;

// Explicitly register a class for reflection in native image
@RegisterForReflection
public class RequestDto {
    public String name;
    public int amount;
    // Jackson deserializes this via reflection —
    // must be registered for native image
}
```

Example 5 — Custom GraalVM Feature hook:
```java
import org.graalvm.nativeimage.hosted.Feature;
import org.graalvm.nativeimage.hosted.RuntimeReflection;

// Register programmatically during native image build:
public class MyFeature implements Feature {
    @Override
    public void duringSetup(DuringSetupAccess access) {
        Class<?> clazz = access.findClassByName(
            "com.example.dynamic.Handler");
        if (clazz != null) {
            RuntimeReflection.register(clazz);
            RuntimeReflection.register(
                clazz.getDeclaredConstructors());
        }
    }
}
```

---

### ⚖️ Comparison Table

| Metric | JVM (Spring Boot) | Native Image (Spring Boot 3) | Quarkus Native | Go Binary |
|---|---|---|---|---|
| Startup Time | 2–5s | 50–100ms | 10–50ms | 5–20ms |
| Memory (idle) | 400–600MB | 50–150MB | 30–100MB | 20–60MB |
| Peak Throughput | Very high (JIT) | High (no JIT adapt) | High | High |
| Build Time | 30s | 5–15min | 3–10min | 10s |
| Dynamic Features | Full | Restricted | Framework-level | N/A |
| Container Size | 400–500MB | 70–120MB | 40–80MB | 10–30MB |

How to choose: Native image for Kubernetes-native microservices, serverless, CLIs, and edge. JVM for services requiring maximum peak throughput, heavy use of dynamic frameworks, or where build time is a constraint.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Native Image can run any Java program without modification | Programs using unregistered reflection, dynamic class loading, or certain JVM APIs fail at runtime. Most production applications need some configuration adjustment |
| Native Image removes the GC | Native Image includes SubstrateVM's GC. By default it's Serial GC (single-thread, stop-the-world); GraalVM Enterprise includes G1GC for native image. GC pauses still happen |
| Native Image is always faster than JVM | Startup and memory are significantly better. Throughput with Serial GC can be worse than JIT-warmed JVM for GC-intensive workloads. With G1GC + PGO, native image matches JIT for most workloads |
| Building native image requires installing GraalVM locally | GraalVM provides Docker-based build containers and Maven/Gradle plugins that handle the build environment — no local GraalVM installation needed for CI |
| Once reflection-config.json is generated, it never changes | Config must be regenerated whenever a new library is added or new code paths are added that use reflection. Automated regeneration via CI agent runs is essential |
| Native Image doesn't support Spring Boot | Spring Boot 3+ has first-class native image support with AOT processing. The Spring AOT processor automatically generates reflection configs, proxy configs, and resource configs for the vast majority of Spring features |

---

### 🚨 Failure Modes & Diagnosis

**Slow Native Image Build (CI bottleneck)**

**Symptom:**
CI pipeline takes 20 minutes per service. Team has 30 services, each with optional native image builds. Pipeline capacity exhausted.

**Root Cause:**
Native image build involves a full JVM-heap points-to analysis (needs 8–16GB RAM) and multi-threaded AOT compilation. Build time scales roughly with application code size + dependency count.

**Diagnostic Command / Tool:**
```bash
# Profile the native image build:
native-image --verbose -jar myapp.jar 2>&1 | \
  grep "Analysis\|Compilation\|Linking"

# Monitor build resource usage:
# macOS/Linux: watch -n1 "ps aux | grep native-image"
```

**Fix:**
- Use GraalVM's build image cache: `-H:+UseClassInitializationBasedHeapSharing`
- Parallelize across multiple CI runners
- Cache GraalVM's analysis data: `-H:AnalysisResultsDump=analysis.json`
- Use `--quick-build` for non-release builds (faster, less optimized)

**Prevention:**
Only run native image builds for main branch and release tags, not every PR.

---

**GC Pressure in Native Image (Serial GC)**

**Symptom:**
Native image production service shows GC pause spikes under load. Latency P99 exceeds SLA.

**Root Cause:**
Default SubstrateVM GC is Serial GC — single-threaded, stop-the-world. Not suitable for latency-sensitive services with allocation rates > 100MB/s.

**Diagnostic Command / Tool:**
```bash
# Enable GC logging in native image:
./myapp -XX:+PrintGC

# Output:
# [GC (Allocation Failure) [Serial GC: 128M->45M]... pause 50ms]

# Check available GCs:
./myapp -XX:+PrintFlagsFinal 2>&1 | grep GC
```

**Fix:**
GraalVM Enterprise: use G1GC for native image:
```bash
native-image --gc=G1 -jar myapp.jar
```
GraalVM CE: reduce allocation rate; consider JVM mode instead.

**Prevention:**
Load test native image builds before production deployment. Measure GC pause time under peak load.

---

**Dynamic Proxy Not Available in Native Image**

**Symptom:**
Application uses Spring AOP or Mockito in production code. Native image build fails or produces runtime errors around proxied beans.

**Root Cause:**
CGLIB dynamic proxies generate bytecode at runtime — impossible in native image (no JVM class loader, no bytecode generation). Spring Boot 3+ uses AOT ahead-of-time proxy generation to work around this.

**Diagnostic Command / Tool:**
```bash
# In native image build output:
# "Error: CGLIB proxy generation is not supported"

# Check Spring AOT output:
ls target/spring-aot/main/sources/
# Should contain proxy class source files generated at build time
```

**Fix:**
Upgrade to Spring Boot 3+. Ensure `@EnableAspectJAutoProxy(proxyTargetClass=false)` — use JDK proxies where possible. For custom CGLIB use: replace with interface-based approach.

**Prevention:**
Spring Boot 3.x compatibility guide lists all supported and unsupported features for native image. Validate at project inception.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `GraalVM` — Native Image is a GraalVM tool; understanding GraalVM's architecture is prerequisite
- `AOT (Ahead-of-Time Compilation)` — Native Image is the practical implementation of Java AOT; understanding AOT concepts clarifies Native Image's design choices

**Builds On This (learn these next):**
- `GC Tuning` — Native Image uses SubstrateVM GC which has different tuning characteristics than HotSpot GC; separate tuning knowledge needed

**Alternatives / Comparisons:**
- `JIT Compiler` — the runtime alternative to AOT; the long-running service choice when peak throughput matters
- `GraalVM` — the broader project that Native Image is part of; Graal JIT is an alternative mode of GraalVM usage

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ GraalVM tool producing native binaries     │
│              │ from Java: no JVM, ms startup, low memory  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ JVM startup (1–5s) bars Java from CLIs,   │
│ SOLVES       │ serverless, and cold-start environments    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The image heap pre-serializes runtime      │
│              │ state (e.g., Spring context) into binary   │
│              │ data — making framework startup near-zero  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Serverless (Lambda), CLIs, Kubernetes      │
│              │ microservices, scale-to-zero deployments   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Heavy dynamic Java usage without framework │
│              │ support; when build time is a constraint;  │
│              │ when peak JIT throughput is critical       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Sub-100ms startup + low RAM vs slow build  │
│              │ time + closed-world constraints            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Freeze-dry your Java app — serve it       │
│              │  instantly, anywhere, without a kitchen"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GC Tuning (SubstrateVM) → TLAB → Safepoint │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates 20 Spring Boot services to native image for a Kubernetes platform. They achieve 70ms cold starts for most services, but one service — a critical order processor — takes 850ms to start as a native image. This is still faster than JVM mode (3.2s) but fails the team's 200ms readiness target. The service uses extensive Jackson polymorphic deserialization, multiple `@EventListener` classes, and a complex Flyway database migration at startup. Diagnose the likely causes for the slow native image startup, and describe the steps to profile and optimize it below 200ms.

**Q2.** GraalVM Native Image's SubstrateVM uses Serial GC by default. A native image service processing 50,000 requests/second creates approximately 80MB/s of short-lived objects. Serial GC performs a stop-the-world collection every ~160ms (when eden fills). Calculate the impact this has on P99 latency for a request that normally takes 5ms to process, and design the architectural options available to the team that would maintain sub-10ms P99 without switching to JVM mode.

