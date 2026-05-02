---
layout: default
title: "Native Image"
parent: "Java & JVM Internals"
nav_order: 305
permalink: /java/native-image/
number: "0305"
category: Java & JVM Internals
difficulty: ★★★
depends_on: GraalVM, AOT (Ahead-of-Time Compilation), JVM
used_by: Cloud — AWS, Microservices
related: AOT (Ahead-of-Time Compilation), GraalVM, TLAB (Thread Local Allocation Buffer)
tags:
  - java
  - jvm
  - internals
  - performance
  - graalvm
  - deep-dive
---

# 305 — Native Image

⚡ TL;DR — Native Image compiles an entire Java application to a self-contained native binary at build time, enabling sub-100ms startup with no JVM required at runtime.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #305 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ GraalVM, AOT Compilation, JVM │ │
│ Used by: │ Cloud — AWS, Microservices │ │
│ Related: │ AOT Compilation, GraalVM, │ │
│ │ TLAB │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Deploying a Java microservice to Kubernetes means: Docker image of 200MB+
(JRE base), 2–4s startup, 512MB minimum allocated memory. At scale with
100 services, that's: 20GB of container images, multiple seconds of unavailability
per restart, and $X,000/month in memory costs for JVM overhead alone.
For AWS Lambda: a Java function's cold start of 8+ seconds triggers timeouts,
frustrated users, and AWS gateway errors.

**THE BREAKING POINT:**
A fintech company builds a microservices architecture with 200 Java services.
Each service uses 512MB to 1GB of RAM just to run the JVM. Total: 100–200GB
of RAM just for JVM overhead across the cluster. Monthly cloud cost: $50k+
just for the memory floor. A Go/Rust competitor runs the equivalent stack
in 5GB total. Java isn't losing on features — it's losing on runtime economics.

**THE INVENTION MOMENT:**
This is exactly why **Native Image** was created: remove the JVM from the
equation entirely. Compile the Java application to a native binary, embed a
tiny GC, pre-initialize the heap at build time, and ship a 40–80MB binary
that starts in 50ms and uses 50MB of RAM at idle.

---

### 📘 Textbook Definition

GraalVM Native Image is a technology that compiles Java applications to
standalone native executables using ahead-of-time (AOT) compilation. The
`native-image` tool performs a static analysis (points-to analysis) of all
reachable code from application entry points, runs static initializers at
build time (heap snapshotting), compiles all reachable code to machine-specific
native instructions using the Graal compiler, and links the result with an
embedded substrate VM (a minimal runtime providing GC, thread management, and
signal handling) to produce a self-contained binary requiring no JRE at runtime.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Native Image bakes your Java application into a standalone binary — like a Go or Rust binary.

**One analogy:**

> A JVM application is like a LEGO model that comes with a factory (the JVM)
> that assembles it each time you want to play. Native Image is like getting
> the model pre-built — open the box and it's already assembled. Smaller box,
> no factory needed, instantly ready to play.

**One insight:**
The revolutionary aspect of Native Image isn't just speed — it's the economics.
Small binary + fast start + low memory = viable scale-to-zero. Serverless Java
was essentially impossible before Native Image. Now a Java Lambda function starts
in the same time as a Node.js function.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A JVM application requires JVM startup, class loading, and JIT warm-up before
   serving the first request.
2. These costs are fixed regardless of how small or simple the application is.
3. Native executable startup requires neither JVM, class loading, nor warm-up.
4. Static analysis can determine all reachable code given a known entry point
   and a closed-world assumption.

**DERIVED DESIGN:**
The `native-image` build process:

**Phase 1 — Analysis:**
Starting from `main()`, trace every reachable method, field, class. Build a
complete call graph. Identify all classes that could be instantiated. Mark all
others as "unreachable" — they won't be in the binary.

**Phase 2 — Heap Snapshotting:**
Run static initializers (class `<clinit>` methods) at build time. Capture the
resulting heap state — all those `static final Maps`, `List.of(...)` values,
Spring application context objects — into the binary's data section. At runtime,
this heap is memory-mapped directly from disk — no re-initialization needed.

**Phase 3 — Compilation:**
Graal compiler compiles all reachable methods to native code. Applies PGO
profiles if provided. Emits x86-64 or ARM64 machine code.

**Phase 4 — Linking:**
Links compiled code with SubstrateVM (the embedded runtime: GC, thread support,
signal handling, exception support). Produces a statically-linked binary.

**THE TRADE-OFFS:**

- Gain: ~50ms startup vs ~2s JVM. ~50MB RAM vs ~256MB JVM minimum.
- Gain: Self-contained binary (no JRE dependency).
- Cost: Closed-world — reflection, dynamic class loading require explicit config.
- Cost: JIT's runtime optimization absent — steady-state throughput ~5–15% lower.
- Cost: Build time: 1–5 minutes vs seconds for jar.
- Cost: Debugging harder — no jstack, jcmd, jmap on native images.

---

### 🧪 Thought Experiment

**SETUP:**
AWS Lambda function pricing: $0.0000166667 per GB-second. Java function:
1GB RAM, 500ms invocation time, 1 million invocations/day.
Go function: 128MB RAM, 100ms invocation time, same load.

**COST WITHOUT NATIVE IMAGE (Java JVM):**
Cost: 1M × 1GB × 500ms = 500K GB-seconds × $0.0000166667 = **$8.33/day**.
Java Lambda cold starts: 8s → users see timeouts → requires provisioned
concurrency → adds **$50+/day** fixed cost.

**COST WITH NATIVE IMAGE:**
Java Native Image performance approaches Go:
Cost: 1M × 128MB × 100ms = 12.8K GB-seconds × $0.0000166667 = **$0.21/day**.
Cold starts: 50ms → no provisioned concurrency needed.
Total: **$0.21/day** vs **$58.33/day** → **99.6% cost reduction**.

**THE INSIGHT:**
Native Image doesn't just make Java faster — it changes which deployment models
are economically viable. The difference between $0.21 and $58/day per function
is the gap between "Java is practical for serverless" and "use Go instead."

---

### 🧠 Mental Model / Analogy

> Think of a regular Java application as a flat-pack furniture kit (IKEA style).
> Every time you want a table, you open the box (JVM start), read the manual
> (class loading), assemble it (JIT warm-up) — only then can you eat dinner.
> Native Image is the same table, pre-assembled at the factory, shipped ready
> to use. You pay more at build time (longer factory build) but you save time
> every single time you need the table.

- "IKEA kit" → JVM-based Java (assemble on-demand)
- "Pre-assembled at factory" → Native Image build (build once)
- "Longer factory build" → longer CI/CD build time for native compilation
- "Save time every time" → 50ms vs 2,000ms startup for every pod restart

**Where this analogy breaks down:** Pre-assembled furniture can't be modified
after delivery. Native Image similarly can't load new classes at runtime.
But unlike furniture, you can rebuild the binary (factory) for each release.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Native Image turns your Java application into a regular program — like the ones
written in C++ or Rust. It starts instantly, uses less memory, and doesn't
need Java installed on the computer that runs it.

**Level 2 — How to use it (junior developer):**
Install GraalVM JDK. Run: `native-image -jar app.jar` for a simple JAR.
For Spring Boot 3: `./mvnw -Pnative native:compile`. For Quarkus:
`./mvnw package -DnativeImage`. The build takes 1–5 minutes. The output
is an OS-specific binary. You must use appropriate base Docker image
(`gcr.io/distroless/base` or `scratch` + static binary).

**Level 3 — How it works (mid-level engineer):**
The build pipeline: `native-image` calls GraalVM's points-to analysis
(`StaticAnalysis`), initializes heap, then invokes Graal's compilation pipeline
targeting the native backend (LIR → machine code). Reflection config
(`reflect-config.json`) tells the analysis which classes are accessed reflectively.
The SubstrateVM provides: Serial GC (default), G1 GC (opt-in), thread scheduling,
signal handling, JNI, VM intrinsics. Output binary: ELF (Linux), Mach-O (macOS),
PE (Windows). Build with `--static` for self-contained binary, `--libc=musl` for
Alpine compatibility.

**Level 4 — Why it was designed this way (senior/staff):**
Heap snapshotting (running static initializers at build time) is the key innovation
that enables Spring Boot to be fast with Native Image. Spring's `ApplicationContext`
builds involves creating thousands of bean instances, running AutoConfiguration
conditions, and setting up caches. In JVM mode, this happens at every startup
(3–5 seconds). In Native Image mode (Spring AOT), framework bootstrap is moved
to build time: the `ApplicationContext` is partially constructed at build time,
the result heap-snapshotted into the binary. At runtime, Spring just restores
the pre-built context — no scanning, no conditional evaluation. This "ahead-of-time
context initialization" is what makes Spring Native Image viable — without it,
spring startup would still be 3s even in native mode.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│         NATIVE IMAGE BUILD PIPELINE                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Input: app.jar + reflect-config.json + jni-config.json  │
│                       ↓                                  │
│  1. POINTS-TO ANALYSIS                                   │
│     - Traverse call graph from main()                    │
│     - Mark reachable: methods, fields, classes           │
│     - Apply config overrides (reflection, proxies)       │
│     ← YOU ARE HERE (build time analysis)                 │
│                       ↓                                  │
│  2. STATIC INITIALIZER EXECUTION                        │
│     - Run <clinit> for reachable classes                 │
│     - Capture resulting heap → image heap               │
│     (all static finals, constants, Spring beans)        │
│                       ↓                                  │
│  3. GRAAL AOT COMPILATION                               │
│     - Compile all reachable bytecode → native code       │
│     - Apply PGO profiles (if provided)                  │
│     - Emit x86-64 / ARM64 machine code                  │
│                       ↓                                  │
│  4. SUBSTRATE VM LINKING                                │
│     - Link compiled code + SubstrateVM runtime          │
│     - Embed initial heap snapshot                       │
│     - Produce native binary (ELF/Mach-O/PE)            │
│                       ↓                                  │
│  Output: ./myapp  (no JVM required!)                    │
└──────────────────────────────────────────────────────────┘
```

**Docker build pattern:**

```dockerfile
# Multi-stage: build native, then distroless runtime
FROM ghcr.io/graalvm/native-image:21 AS builder
WORKDIR /app
COPY mvnw pom.xml ./
COPY src ./src
RUN ./mvnw -Pnative native:compile -DskipTests

FROM gcr.io/distroless/base AS runtime
WORKDIR /app
COPY --from=builder /app/target/myapp .
ENTRYPOINT ["/app/myapp"]
# Image size: ~60MB vs ~350MB for JVM-based
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────────┐
│     JVM-BASED vs NATIVE IMAGE — LIFECYCLE               │
├──────────────────────┬───────────────────────────────────┤
│ JVM-BASED            │ NATIVE IMAGE                      │
├──────────────────────┼───────────────────────────────────┤
│ CI: javac (2s)        │ CI: native-image build (3min)     │
│ Image: 350MB          │ Image: 60MB                       │
│                      │                                   │
│ Deploy:               │ Deploy:                           │
│  JVM start: 500ms     │  Binary start: 50ms ← YOU HERE   │
│  ClassLoad: 1s        │  Heap restore: 10ms               │
│  Spring: 2s           │  Spring ctx: 100ms                │
│  JIT warm: 20s        │  READY: 160ms total               │
│  Total: 23.5s         │                                   │
│                      │                                   │
│ Steady state:         │ Steady state:                     │
│  ~C2 peak perf        │  ~85% of C2 peak perf            │
│  512MB RAM            │  50MB RAM                        │
└──────────────────────┴───────────────────────────────────┘
```

**FAILURE PATH:**
Missing reflection config → `ClassNotFoundException` at runtime. Prevention:
always run integration tests against the native binary, not just the JAR.

**WHAT CHANGES AT SCALE:**
At 1000 instances, Native Image saves: memory ($150k+/year), cold start latency
(enabling scale-to-zero $200k+/year), image pull time (smaller images = faster
scaling). Build time investment (3 min × releases) is typically < 1% of savings.

---

### 💻 Code Example

```bash
# Example 1 — Basic native image build
# Prerequisite: GraalVM JDK installed

# Build native image from jar
native-image \
  -jar app.jar \
  -H:Name=myapp \
  -H:+ReportExceptionStackTraces \
  --no-fallback  # fail if features unsupported, don't use JVM fallback

# Run the binary
./myapp  # starts in ~50ms
```

```bash
# Example 2 — Quarkus native build (highly recommended approach)
# Quarkus has excellent Native Image support out of the box

mvn quarkus:create \
  -DprojectGroupId=com.example \
  -DprojectArtifactId=my-service \
  -DclassName="com.example.GreetingResource" \
  -Dpath="/hello"

# Build native image
./mvnw package -Pnative

# Docker native image build
./mvnw package -Pnative -Dquarkus.native.container-build=true
```

```java
// Example 3 — Reflection configuration for Native Image
// Without config: ClassNotFoundException at runtime

// Option A: reflection-config.json
// [
//   {
//     "name": "com.example.MyEntity",
//     "allDeclaredFields": true,
//     "allDeclaredMethods": true,
//     "allDeclaredConstructors": true
//   }
// ]

// Option B: GraalVM annotation (@RegisterReflectionForBinding)
@RegisterReflectionForBinding(MyEntity.class)
@Configuration
public class NativeConfig { }

// Option C: Spring AOT hint
class MyRuntimeHints implements RuntimeHintsRegistrar {
    @Override
    public void registerHints(RuntimeHints hints, ClassLoader cl) {
        hints.reflection().registerType(
            MyEntity.class,
            MemberCategory.values()
        );
    }
}
```

---

### ⚖️ Comparison Table

| Metric            | JVM (HotSpot) | Native Image | Go Binary | Best For              |
| ----------------- | ------------- | ------------ | --------- | --------------------- |
| **Cold start**    | 2–5s          | 50–150ms     | 5–20ms    | Native/Go: serverless |
| **Throughput**    | 100%          | 85–95%       | 80–90%    | JVM: batch / compute  |
| **RAM at idle**   | 256MB+        | 30–80MB      | 10–20MB   | Native/Go: cost       |
| **Build time**    | 2s            | 2–5min       | 10s       | JVM/Go: dev speed     |
| **Image size**    | 200–500MB     | 50–100MB     | 10–20MB   | Native/Go: registry   |
| **Observability** | Full          | Limited      | Limited   | JVM: production ops   |

**How to choose:** Use Native Image for AWS Lambda, scale-to-zero Kubernetes,
CLI tools, and microservices with < 100ms cold start requirement. Use JVM for
stateful services, high-compute workloads, and when JVM tooling (profilers, dumps)
is needed in production.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                     |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Native Image is just a fat JAR                 | It contains no JVM, no bytecode — it's a native binary with embedded GC and runtime, fundamentally different                |
| Native Image runs faster than JVM in all cases | Steady-state throughput is often 5–15% lower than JIT-compiled JVM; Native Image wins on startup and memory, not throughput |
| All Java libraries work with Native Image      | Libraries using heavy reflection (some JPA providers, certain XML parsers) require configuration or are unsupported         |
| You can debug Native Image the same way as JVM | jstack, jmap, heap dumps are not available on Native Image; use GDB or GraalVM debugger tools instead                       |
| Native Image builds are fast                   | A typical Spring Boot Native Image build takes 2–5 minutes; complex apps take 10+ minutes                                   |

---

### 🚨 Failure Modes & Diagnosis

**ClassNotFoundException in Native Image**

Symptom:
Application works fine with JVM but crashes at runtime in native mode with
`ClassNotFoundException` or `InstantiationException`.

Root Cause:
Class is referenced dynamically (via reflection, `Class.forName`,
`ObjectInputStream`, etc.) but wasn't registered in reflection config.

Diagnostic Command / Tool:

```bash
# Generate reflection config using tracing agent:
java -agentlib:native-image-agent=\
  config-output-dir=src/main/resources/META-INF/native-image \
  -jar app.jar

# Then verify generated file contents:
cat src/main/resources/META-INF/native-image/reflect-config.json
```

Fix:
Add class to `reflect-config.json`, rebuild native image, retest.

Prevention:
Always run the tracing agent on a full integration test suite before
building production native images for the first time.

---

**Static Initializer Environment Contamination**

Symptom:
Native image reads incorrect environment-specific configuration (e.g., build
machine's hostname, build time's log level appears in binary).

Root Cause:
Static initializer reads system properties or environment at build time
and that value is snapshotted into the binary.

Diagnostic Command / Tool:

```bash
native-image -H:+PrintClassInitialization \
  --initialize-at-run-time=com.example.Config \
  -jar app.jar 2>&1 | grep "initialized at"
```

Fix:

```bash
# Force environment-sensitive class to init at runtime:
--initialize-at-run-time=com.example.Config
```

Prevention:
Avoid reading System.getenv(), System.getProperty() in static initializers.
Use instance-level lazy initialization for environment-dependent configuration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `GraalVM` — Native Image is a GraalVM technology; must understand GraalVM architecture
- `AOT (Ahead-of-Time Compilation)` — Native Image is the primary Java AOT implementation
- `JVM` — Native Image replaces JVM at runtime; must understand what JVM provides

**Builds On This (learn these next):**

- `Cloud — AWS` — Lambda use case is primary Native Image driver
- `Microservices` — Native Image economics enable new microservice deployment patterns

**Alternatives / Comparisons:**

- `AOT (Ahead-of-Time Compilation)` — broader concept; Native Image is the implementation
- `GraalVM` — parent technology that provides Native Image

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Java→native binary: no JVM at runtime     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ JVM startup cost makes Java non-viable    │
│ SOLVES       │ for serverless and scale-to-zero           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Heap snapshotting pre-initializes the      │
│              │ Spring context at build time — that's what │
│              │ makes 150ms Spring startup possible         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lambda, scale-to-zero, CLI tools, edge     │
│              │ deployments, memory-constrained containers  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-throughput compute requiring JIT peak, │
│              │ heavy reflection without AOT framework      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Build complexity + throughput -15% vs      │
│              │ startup 40× faster + memory 10× lower      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Ship the cake, not the bakery"            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GraalVM → AOT → Cloud — AWS (Lambda)       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot microservice uses `@Scheduled` tasks that scan for
`@EventListener` implementations dynamically using classpath scanning.
In JVM mode this works perfectly. In Native Image mode it fails. Trace the
exact mechanism causing this failure at the points-to analysis phase, and
design the minimum change to the application and build configuration that
would make it work with Native Image while preserving the dynamic discovery behavior.

**Q2.** Native Image's steady-state throughput is 5–15% lower than JIT-compiled
JVM code for the same application. However, in a scale-to-zero Kubernetes
deployment, the total system throughput (including cold starts) may be higher
for Native Image because pods start 40× faster. Derive the exact equations for
when Native Image's total throughput exceeds JIT's, given: cold start frequency F,
steady-state throughput ratio R (JIT/Native), warm-up time T_warm, and pod count N.
