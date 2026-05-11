#!/usr/bin/env python3
"""Fill TODO sections for Java - JVM Internals.md (5 keywords)."""
import re

FILE = "interview/java/Java - JVM Internals.md"

KEYWORDS = [
    "JVM Architecture",
    "Class Loading",
    "Memory Model",
    "JIT Compilation",
    "Bytecode",
]

# ── Level 5 ──────────────────────────────────────────────

LEVEL5 = {
    "JVM Architecture": (
        "The JVM is a stack-based virtual machine that provides "
        "platform independence through an intermediate bytecode "
        "layer - the same architectural pattern used by .NET CLR, "
        "Python's CPython, and WebAssembly. The cross-domain "
        "insight: every successful VM architecture converges on "
        "the same design: bytecode for portability, JIT for "
        "performance, GC for safety, and a security sandbox. "
        "The JVM's distinguishing feature is its adaptive "
        "optimization: the JIT compiler profiles running code "
        "and optimizes hot paths, making Java faster than "
        "ahead-of-time compiled languages in certain long-running "
        "scenarios. At extreme scale, JVM architecture decisions "
        "cascade: class loading affects startup, memory layout "
        "affects GC, GC affects latency, JIT affects throughput. "
        "If redesigning today, you would build value types "
        "(Project Valhalla) and lightweight threads (virtual "
        "threads) into the specification from day one, and use "
        "CRaC (Coordinated Restore at Checkpoint) for instant "
        "startup.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Which JVM subsystem is the bottleneck?\" - startup "
        "= classloading, throughput = JIT, latency = GC\n"
        "- \"Is this workload long-running or short-lived?\" - "
        "JIT amortizes over time; short tasks pay warmup cost\n"
        "- \"What's the memory budget?\" - JVM has fixed overhead "
        "(Metaspace, thread stacks, JIT code cache) beyond heap"
    ),
    "Class Loading": (
        "Class loading implements the universal lazy initialization "
        "pattern at the type level: classes are loaded, linked, and "
        "initialized only when first referenced. This same pattern "
        "appears in dynamic linking (shared libraries loaded on "
        "first call), module systems (ES modules, webpack code "
        "splitting), and database lazy loading (Hibernate proxies). "
        "The expert insight: the parent-delegation model is a "
        "trust hierarchy - bootstrap loader (JDK classes) is "
        "trusted, application loader is not. This prevents "
        "malicious code from replacing core classes (e.g., a "
        "fake `java.lang.String`). At extreme scale, class "
        "loading is the #1 startup bottleneck and the #1 source "
        "of memory leaks in application servers (classloader "
        "leaks). If redesigning today, you would build the module "
        "system (JPMS) into the classloader from the start and "
        "use ahead-of-time class loading (AppCDS) by default.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Which classloader loaded this class?\" - determines "
        "visibility, security, and unloading behavior\n"
        "- \"Is this a classloader leak?\" - if classes from "
        "undeployed apps survive, their loader is retained\n"
        "- \"Can I pre-load this?\" - AppCDS archives shared "
        "classes for faster startup"
    ),
    "Memory Model": (
        "The Java Memory Model (JMM) is a formal specification "
        "of how threads interact through memory, defining the "
        "happens-before relationship that guarantees visibility. "
        "The same memory ordering concepts appear in CPU memory "
        "models (x86-TSO, ARM relaxed), C++ memory model "
        "(std::memory_order), database isolation levels "
        "(read-committed = relaxed, serializable = sequential "
        "consistency), and distributed systems (causal "
        "consistency). The expert insight: the JMM is a contract "
        "between the programmer and the JVM/hardware. Without "
        "synchronization, the JVM and CPU are free to reorder, "
        "cache, and speculate on memory operations. "
        "`volatile` and `synchronized` establish happens-before "
        "edges that constrain this freedom. At extreme scale, "
        "understanding the JMM is the difference between code "
        "that works on one CPU architecture (x86, which is "
        "strongly ordered) and code that breaks on another "
        "(ARM, which is weakly ordered). If redesigning today, "
        "you would make `volatile` semantics the default and "
        "require explicit `relaxed` for optimization.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is there a happens-before edge?\" - if not, "
        "visibility is not guaranteed\n"
        "- \"Would this break on ARM?\" - x86 hides many "
        "memory ordering bugs\n"
        "- \"Is this a data race?\" - two threads accessing "
        "the same field, at least one writing, no synchronization"
    ),
    "JIT Compilation": (
        "JIT compilation is the JVM's adaptive optimization "
        "engine that transforms bytecode to native machine "
        "code at runtime, using profiling data to make better "
        "optimization decisions than any ahead-of-time compiler "
        "could. This same profile-guided optimization (PGO) "
        "concept appears in V8 (JavaScript), .NET RyuJIT, "
        "database query optimizers (adaptive query plans), "
        "and branch prediction in CPUs. The expert insight: "
        "the JIT has a speculative optimization model - it "
        "makes optimistic assumptions (this virtual call always "
        "dispatches to SubClass.method()) and deoptimizes if "
        "the assumption is violated. This speculation enables "
        "method inlining, escape analysis, and devirtualization "
        "that are impossible for static compilers. At extreme "
        "scale, JIT warmup time (2-5 minutes for complex apps) "
        "is a real problem for serverless and container "
        "deployments. If redesigning today, you would combine "
        "AOT compilation (GraalVM native image) for startup "
        "with JIT for steady-state optimization.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is the app warmed up?\" - benchmark results before "
        "JIT stabilization are meaningless\n"
        "- \"Is this method inlined?\" - inlining is the most "
        "impactful JIT optimization\n"
        "- \"Are there deoptimization events?\" - frequent "
        "deopts indicate polymorphic dispatch or uncommon traps"
    ),
    "Bytecode": (
        "Bytecode is the JVM's instruction set - a platform-"
        "independent intermediate representation that serves "
        "as the contract between language compilers (javac, "
        "kotlinc, scalac) and the JVM runtime. This same IR "
        "concept appears in LLVM IR (used by Clang, Rust, "
        "Swift), WebAssembly (browser-portable code), .NET IL, "
        "and database query plans. The expert insight: bytecode "
        "is NOT interpreted in modern JVMs - it's a convenient "
        "portable format that the JIT compiler translates to "
        "native code. The bytecode's stack-based design was "
        "chosen for compactness and verification simplicity, "
        "not for execution efficiency. Understanding bytecode "
        "is essential for: debugging unusual behavior, "
        "understanding framework magic (Spring proxies, "
        "Hibernate instrumentation), and verifying compiler "
        "output. If redesigning today, you would use a "
        "register-based IR (like Dalvik/ART) for better "
        "JIT compilation efficiency.\n\n"
        "**Expert thinking cues:**\n"
        "- \"What bytecode does this generate?\" - `javap -c` "
        "reveals what the compiler actually does\n"
        "- \"Is this framework manipulating bytecode?\" - "
        "Spring, Hibernate, Mockito all use bytecode engineering\n"
        "- \"Is the bytecode verifier passing this?\" - illegal "
        "bytecode = VerifyError at class loading"
    ),
}

# ── Quick Reference Card ─────────────────────────────────

QUICKREF = {
    "JVM Architecture": (
        "**WHAT IT IS:** The Java Virtual Machine - a stack-based "
        "VM that executes bytecode with JIT compilation, GC, and "
        "platform independence\n"
        "**PROBLEM IT SOLVES:** Write once, run anywhere - "
        "isolates application code from OS and hardware "
        "differences\n"
        "**KEY INSIGHT:** The JVM is three systems in one: "
        "class loader (loading), execution engine (JIT + "
        "interpreter), and memory manager (GC)\n"
        "**USE WHEN:** Understanding performance, diagnosing "
        "issues, tuning applications, or explaining Java's "
        "runtime behavior\n"
        "**AVOID WHEN:** Treating the JVM as a black box - "
        "understanding architecture is essential for production "
        "engineering\n"
        "**ANTI-PATTERN:** Ignoring JVM subsystem interactions - "
        "GC tuning without understanding memory layout, or JIT "
        "without profiling\n"
        "**TRADE-OFF:** Platform independence and safety (GC, "
        "verification) vs startup time and memory overhead\n"
        "**ONE-LINER:** \"The JVM trades startup cost for "
        "runtime optimization, portability, and memory safety\""
    ),
    "Class Loading": (
        "**WHAT IT IS:** The JVM subsystem that loads, links, "
        "and initializes classes on demand using parent-"
        "delegation hierarchy\n"
        "**PROBLEM IT SOLVES:** Lazy type resolution, namespace "
        "isolation, security boundaries, and modular class "
        "visibility\n"
        "**KEY INSIGHT:** Parent-delegation prevents untrusted "
        "code from replacing core classes. Bootstrap -> "
        "Platform -> Application loader chain\n"
        "**USE WHEN:** Debugging ClassNotFoundException, "
        "NoClassDefFoundError, classloader leaks, or "
        "understanding framework startup\n"
        "**AVOID WHEN:** Creating custom classloaders unless "
        "you truly need isolation (plugin systems, app servers)\n"
        "**ANTI-PATTERN:** Creating classloader hierarchies "
        "without understanding unloading - causes Metaspace "
        "leaks in app servers\n"
        "**TRADE-OFF:** Lazy loading (fast startup) vs eager "
        "loading (fail-fast on missing classes)\n"
        "**ONE-LINER:** \"Class loading is lazy, hierarchical, "
        "and the #1 source of both startup bottlenecks and "
        "memory leaks\""
    ),
    "Memory Model": (
        "**WHAT IT IS:** The formal specification (JMM/JSR-133) "
        "defining how threads interact through shared memory "
        "and the happens-before guarantee\n"
        "**PROBLEM IT SOLVES:** Defines when writes by one "
        "thread become visible to reads by another - without "
        "this, concurrent code is unpredictable\n"
        "**KEY INSIGHT:** Without synchronization, the JVM and "
        "CPU may reorder, cache, or optimize away memory "
        "operations. Happens-before constrains this\n"
        "**USE WHEN:** Writing concurrent code, debugging "
        "visibility bugs, understanding volatile/synchronized/"
        "final semantics\n"
        "**AVOID WHEN:** Single-threaded code - the JMM only "
        "matters when multiple threads share mutable state\n"
        "**ANTI-PATTERN:** Relying on x86 memory ordering "
        "strength - code that 'works' on x86 can break on ARM\n"
        "**TRADE-OFF:** Synchronization correctness vs "
        "performance overhead of memory barriers and cache "
        "flushes\n"
        "**ONE-LINER:** \"The JMM guarantees visibility through "
        "happens-before edges; without them, anything goes\""
    ),
    "JIT Compilation": (
        "**WHAT IT IS:** The JVM's runtime optimizer that "
        "compiles hot bytecode to native machine code using "
        "profiling data (C1/C2 tiered compilation)\n"
        "**PROBLEM IT SOLVES:** Bytecode interpretation is slow. "
        "JIT provides native performance while retaining "
        "portability and dynamic optimization\n"
        "**KEY INSIGHT:** JIT uses runtime profiling to make "
        "optimizations impossible for static compilers: "
        "speculative inlining, devirtualization, escape "
        "analysis\n"
        "**USE WHEN:** Analyzing performance, understanding "
        "warmup, diagnosing deoptimization, benchmarking "
        "correctly\n"
        "**AVOID WHEN:** Micro-benchmarks without warmup - "
        "JIT hasn't optimized yet, results are meaningless\n"
        "**ANTI-PATTERN:** Benchmarking cold code and drawing "
        "conclusions - always use JMH with proper warmup "
        "iterations\n"
        "**TRADE-OFF:** Warmup time and memory for compiled "
        "code vs peak throughput (JIT code > static in many "
        "scenarios)\n"
        "**ONE-LINER:** \"JIT turns Java from interpreted to "
        "faster-than-C for long-running hot paths\""
    ),
    "Bytecode": (
        "**WHAT IT IS:** The JVM's instruction set - portable "
        "stack-based opcodes (200+) that javac compiles source "
        "code to, stored in .class files\n"
        "**PROBLEM IT SOLVES:** Platform independence - bytecode "
        "runs on any JVM regardless of OS or CPU architecture\n"
        "**KEY INSIGHT:** Bytecode is a portable IR, not an "
        "execution format. Modern JVMs JIT-compile it to native "
        "code. Understanding it reveals compiler and framework "
        "behavior\n"
        "**USE WHEN:** Debugging framework magic (proxies, "
        "instrumentation), verifying compiler output, "
        "understanding performance characteristics\n"
        "**AVOID WHEN:** Day-to-day development - bytecode "
        "knowledge is for deep debugging and understanding, "
        "not routine coding\n"
        "**ANTI-PATTERN:** Writing bytecode by hand when javac "
        "or a library (ASM, ByteBuddy) handles it correctly\n"
        "**TRADE-OFF:** Stack-based design (compact, easy to "
        "verify) vs register-based (faster interpretation, "
        "better for JIT)\n"
        "**ONE-LINER:** \"Bytecode is the lingua franca of the "
        "JVM - every language compiles to it, the JIT optimizes "
        "it, frameworks manipulate it\""
    ),
}

# ── Comparison Table ─────────────────────────────────────

COMPARISON = {
    "JVM Architecture": (
        "| Component | JVM (HotSpot) | .NET CLR | "
        "V8 (JavaScript) |\n"
        "|-----------|--------------|---------|"
        "----------------|\n"
        "| IR format | Bytecode (stack) | IL (stack) | "
        "Bytecode (register) |\n"
        "| GC | Generational (G1/ZGC) | Generational | "
        "Generational (Orinoco) |\n"
        "| JIT | C1+C2 tiered | RyuJIT | TurboFan |\n"
        "| Startup | Slow (class loading) | Fast (AOT option) | "
        "Fast (interpreted) |\n"
        "| Type system | Erased generics | Reified generics | "
        "Dynamic |\n"
        "| Memory model | JMM (JSR-133) | .NET MM | "
        "Single-threaded* |"
    ),
    "Class Loading": (
        "| Aspect | Bootstrap Loader | Platform Loader | "
        "Application Loader |\n"
        "|--------|-----------------|----------------|"
        "-------------------|\n"
        "| Loads | java.lang, java.util | JDBC, XML, crypto | "
        "Application classes |\n"
        "| Implementation | Native (C++) | Java | Java |\n"
        "| Parent | None (root) | Bootstrap | Platform |\n"
        "| Trust level | Highest | High | Normal |\n"
        "| Customizable | No | No | Yes (extends) |"
    ),
    "Memory Model": (
        "| Mechanism | Visibility | Atomicity | "
        "Ordering |\n"
        "|-----------|-----------|----------|"
        "---------|\n"
        "| volatile | Yes | Yes (read/write) | "
        "Happens-before |\n"
        "| synchronized | Yes | Yes (block) | "
        "Happens-before |\n"
        "| final field | Yes (after construction) | "
        "N/A | Initialization safety |\n"
        "| Atomic classes | Yes | Yes (CAS) | "
        "Happens-before |\n"
        "| No sync | No guarantee | No | "
        "No guarantee |"
    ),
    "JIT Compilation": (
        "| Aspect | C1 (Client) | C2 (Server) | "
        "Interpreter |\n"
        "|--------|------------|------------|"
        "------------|\n"
        "| Speed | Fast compile | Slow compile | "
        "No compile |\n"
        "| Optimization | Basic | Aggressive | None |\n"
        "| Code quality | Good | Best | N/A |\n"
        "| Startup impact | Low | High | None |\n"
        "| Profiling | Basic | Full | Collects data |\n"
        "| Use case | Warmup tier | Steady-state | "
        "Cold code |"
    ),
    "Bytecode": (
        "| Feature | JVM Bytecode | .NET IL | "
        "WebAssembly |\n"
        "|---------|-------------|---------|"
        "------------|\n"
        "| Design | Stack-based | Stack-based | "
        "Stack-based |\n"
        "| Type safety | Verified | Verified | "
        "Type-checked |\n"
        "| Opcodes | ~200 | ~220 | ~400 |\n"
        "| Generics | Erased | Reified | N/A |\n"
        "| Inspection | javap -c | ildasm | "
        "wasm-objdump |\n"
        "| Manipulation | ASM, ByteBuddy | Mono.Cecil | "
        "binaryen |"
    ),
}

# ── Misconceptions ───────────────────────────────────────

MISCONCEPTIONS = {
    "JVM Architecture": [
        ("Java is always slower than C/C++",
         "JIT compilation with runtime profiling enables "
         "optimizations impossible for static compilers "
         "(speculative inlining, devirtualization). Long-running "
         "Java can outperform C for some workloads."),
        ("The JVM only runs Java",
         "The JVM runs any language that compiles to bytecode: "
         "Kotlin, Scala, Groovy, Clojure, JRuby. It's a "
         "language-agnostic runtime platform."),
        ("JVM overhead is only the heap",
         "JVM memory includes: heap + Metaspace (classes) + "
         "thread stacks (1MB each) + JIT code cache + "
         "GC overhead + direct buffers. Total overhead can be "
         "2-3x the heap."),
        ("GraalVM replaces HotSpot",
         "GraalVM is a JIT compiler (Graal) and AOT compiler "
         "(native-image). HotSpot with C2 JIT remains the "
         "default and most battle-tested for server workloads."),
    ],
    "Class Loading": [
        ("Classes are loaded at startup",
         "Classes are loaded lazily on first active use "
         "(instantiation, static method call, static field "
         "access). This is why ClassNotFoundException occurs at "
         "runtime, not startup."),
        ("ClassNotFoundException = class not on classpath",
         "It can also mean: wrong classloader, class loaded by "
         "incompatible loader, or classloader isolation "
         "(e.g., web app can't see another web app's classes)."),
        ("Loaded classes can always be garbage collected",
         "A class can only be unloaded when its classloader is "
         "GC'd. System classloader classes (bootstrap/platform) "
         "are never unloaded."),
        ("The classpath order doesn't matter",
         "When the same class exists in multiple JARs, the "
         "first one found on the classpath wins. JAR ordering "
         "determines which version is loaded - a source of "
         "subtle bugs."),
    ],
    "Memory Model": [
        ("volatile makes all operations atomic",
         "volatile guarantees atomic reads/writes and visibility, "
         "but NOT compound operations. `volatile int count; "
         "count++` is NOT atomic (read-modify-write). Use "
         "AtomicInteger."),
        ("synchronized is always slow",
         "Modern JVMs use biased locking, thin locks, and lock "
         "elision. Uncontended synchronized blocks have near-zero "
         "overhead. Only contended locks are expensive."),
        ("Data races only cause stale reads",
         "Data races can cause: out-of-thin-air values, "
         "partially constructed objects, reordered operations, "
         "and JIT-optimized-away reads (hoisted out of loops)."),
        ("final fields don't need synchronization",
         "final fields have special JMM semantics: they're "
         "safely published after construction IF the reference "
         "doesn't escape during construction (no `this` leak)."),
    ],
    "JIT Compilation": [
        ("JIT always makes code faster",
         "JIT compilation has overhead: profiling, compilation "
         "time, code cache memory. For short-lived processes "
         "(CLI tools, serverless), JIT warmup may never pay off."),
        ("You should help the JIT with manual optimizations",
         "The JIT is better at micro-optimization than humans. "
         "Manual tricks (loop unrolling, object pooling) often "
         "prevent JIT optimizations like escape analysis."),
        ("C2 is always used for hot methods",
         "Tiered compilation uses C1 first, then C2 for very "
         "hot methods. Some methods stay at C1 level if they "
         "don't reach the C2 threshold."),
        ("Deoptimization means a bug",
         "Deoptimization is normal JIT behavior when speculative "
         "assumptions fail. It becomes a problem only if it "
         "happens repeatedly for the same method (unstable "
         "optimization)."),
    ],
    "Bytecode": [
        ("Bytecode is interpreted instruction by instruction",
         "Modern JVMs JIT-compile hot bytecode to native machine "
         "code. The interpreter is only used for cold code and "
         "during warmup."),
        ("You need to know bytecode for daily development",
         "Bytecode knowledge is for deep debugging, framework "
         "internals, and performance analysis. It's a specialized "
         "skill, not a daily requirement."),
        ("More bytecode instructions means slower execution",
         "The JIT optimizes bytecode holistically. What matters "
         "is the SEMANTIC complexity, not instruction count. "
         "A method with fewer bytecodes can be slower if it "
         "prevents inlining."),
        ("All bytecode operations map to single CPU instructions",
         "Many bytecodes (invokeinterface, monitorenter, "
         "checkcast) expand to complex CPU instruction sequences. "
         "Bytecode is an abstraction, not a 1:1 mapping."),
    ],
}

# ── Failure Modes ────────────────────────────────────────

FAILURES = {
    "JVM Architecture": r"""**Failure Mode 1: Metaspace exhaustion causing OutOfMemoryError**
**Symptom:** `OutOfMemoryError: Metaspace`. Application fails to load new classes. Full GC doesn't help.
**Root Cause:** Too many classes loaded (heavy reflection, dynamic proxies, bytecode generation) without proper Metaspace sizing.
**Diagnostic:**

```
jstat -gcmetacapacity <pid>
# Check MCMX (max) vs MC (committed) vs MU (used)
jcmd <pid> VM.classloader_stats
# Count loaded classes per classloader
```

**Fix:**
```java
// BAD: default MetaspaceSize too small
// for apps with many generated classes

// GOOD: size Metaspace explicitly
// -XX:MetaspaceSize=256m
// -XX:MaxMetaspaceSize=512m

// Root cause: reduce class generation
// - Cache generated proxies
// - Limit reflection-based instantiation
```
**Prevention:** Monitor Metaspace usage. Set `-XX:MaxMetaspaceSize` explicitly. Profile classloader count for leaks.

**Failure Mode 2: JIT code cache exhaustion**
**Symptom:** Performance degrades after initial warmup. JIT log shows "code cache full, compiler disabled". Methods revert to interpreted.
**Root Cause:** Code cache (where JIT stores compiled native code) is full. Default is 240MB (JDK 9+). Large applications with many methods can exhaust it.
**Diagnostic:**

```
jcmd <pid> Compiler.codecache
# Shows total size, used, and free
# Or: -XX:+PrintCodeCache at JVM exit
```

**Fix:**
```java
// BAD: default code cache for large application
// 240MB may not be enough for 100k+ methods

// GOOD: increase code cache
// -XX:ReservedCodeCacheSize=512m
// Monitor: JMX java.lang:type=MemoryPool,
//   name=CodeCache (or CodeHeap)
```
**Prevention:** Monitor code cache usage in production. Alert at 80% capacity. Increase for large applications or those using many frameworks.

**Failure Mode 3: Native memory leak (RSS growing beyond heap)**
**Symptom:** Container OOM killed despite heap being within -Xmx. RSS (resident memory) grows continuously beyond heap size.
**Root Cause:** Native memory allocation outside the heap: thread stacks, JNI, direct ByteBuffers, Metaspace, or native library leaks.
**Diagnostic:**

```
# Enable native memory tracking
# -XX:NativeMemoryTracking=summary
jcmd <pid> VM.native_memory summary
# Compare total reserved vs committed vs -Xmx
```

**Fix:**
```java
// BAD: container limit = -Xmx (ignoring native)
// docker run -m 4g ... java -Xmx4g
// RSS = heap + native > 4g -> OOM killed

// GOOD: budget for native memory
// docker run -m 6g ... java -Xmx4g
// Rule: container limit = Xmx * 1.5 + 500MB
```
**Prevention:** Use Native Memory Tracking. Set container limits to Xmx + 50-75% overhead. Monitor RSS vs heap usage.""",

    "Class Loading": r"""**Failure Mode 1: ClassNotFoundException at runtime**
**Symptom:** `ClassNotFoundException` or `NoClassDefFoundError` when the application tries to use a class that exists in the project.
**Root Cause:** Class not on the classpath at runtime, or loaded by a different classloader that can't see the target class.
**Diagnostic:**

```
# Check if class is in any JAR on classpath
jar -tf app.jar | grep "TargetClass"
# Check which classloader loaded a related class
System.out.println(MyClass.class.getClassLoader());
```

**Fix:**
```java
// BAD: dependency not included at runtime
// <scope>provided</scope> in Maven
// Class exists at compile time but not runtime

// GOOD: ensure dependency is in runtime classpath
// Remove 'provided' scope if not in container
// Or: add to runtime classpath explicitly
// java -cp "app.jar:lib/*" com.app.Main
```
**Prevention:** Test runtime classpath in CI. Use `jdeps` to verify dependencies. Understand Maven scopes (compile, runtime, provided).

**Failure Mode 2: ClassLoader leak in application servers**
**Symptom:** Metaspace grows after each redeploy. Eventually `OutOfMemoryError: Metaspace`. Memory never reclaimed.
**Root Cause:** A reference from a long-lived object (static field, ThreadLocal, JMX MBean, JDBC driver) to a class in the web app's classloader prevents the classloader from being garbage collected.
**Diagnostic:**

```
# Heap dump analysis
jmap -dump:live,format=b,file=heap.hprof <pid>
# In Eclipse MAT: find WebAppClassLoader
# Path to GC Roots -> see what retains it
jcmd <pid> VM.classloader_stats
```

**Fix:**
```java
// BAD: static reference retains classloader
class LeakyServlet extends HttpServlet {
    static final Cache cache = new Cache();
    // Cache holds class-level references
    // -> retains classloader after undeploy
}

// GOOD: clean up on undeploy
@Override
public void destroy() {
    cache.clear();
    // Deregister JDBC drivers
    DriverManager.getDrivers().asIterator()
        .forEachRemaining(d -> {
            try { DriverManager.deregisterDriver(d); }
            catch (Exception e) { /* log */ }
        });
}
```
**Prevention:** Clean up static state, ThreadLocals, JDBC drivers, and JMX beans on undeploy. Use leak detection tools (Tomcat's MemoryLeakDetection).

**Failure Mode 3: JAR hell - wrong class version loaded**
**Symptom:** `NoSuchMethodError`, `AbstractMethodError`, or `IncompatibleClassChangeError` at runtime. The method exists in source but not in the loaded class.
**Root Cause:** Multiple versions of the same library on the classpath. The classloader picks the first JAR found, which may be the wrong version.
**Diagnostic:**

```
# Find duplicate classes
mvn dependency:tree | grep -i "conflict"
# Check which JAR a class was loaded from
URL url = MyClass.class.getProtectionDomain()
    .getCodeSource().getLocation();
```

**Fix:**
```java
// BAD: two versions of same library
// lib/guava-31.jar AND lib/guava-28.jar
// ClassLoader loads from guava-28 first

// GOOD: use Maven dependency management
// <dependencyManagement> to enforce versions
// mvn dependency:tree -Dverbose
// mvn enforcer:enforce (ban duplicate classes)
```
**Prevention:** Use Maven Enforcer plugin to ban duplicate classes. Use `mvn dependency:tree -Dverbose` to find conflicts. Pin versions in dependencyManagement.""",

    "Memory Model": r"""**Failure Mode 1: Visibility bug - stale read in loop**
**Symptom:** Thread never sees updated value. Loop spins forever or uses stale data. Works on some CPUs (x86) but fails on others (ARM).
**Root Cause:** No happens-before edge between write and read. JIT hoists the field read out of the loop (reads once, caches in register).
**Diagnostic:**

```
# Check if field is volatile or accessed under lock
grep -rn "boolean.*running\|boolean.*stop" src/
# If not volatile and accessed from another thread
# -> visibility bug
```

**Fix:**
```java
// BAD: non-volatile shared flag
boolean running = true;
// Thread 1: while (running) { work(); }
// Thread 2: running = false;
// Thread 1 may NEVER see false (JIT hoists read)

// GOOD: volatile ensures visibility
volatile boolean running = true;
// Or: use AtomicBoolean
```
**Prevention:** Every field shared between threads needs: volatile, synchronized, or atomic. No exceptions. Test on ARM hardware or use -XX:+StressGCM to stress test ordering.

**Failure Mode 2: Double-checked locking without volatile**
**Symptom:** Partially constructed object visible to other threads. Crashes or incorrect behavior in singleton initialization.
**Root Cause:** Without volatile, the JVM may reorder the assignment and constructor. Other threads see the reference before the constructor completes.
**Diagnostic:**

```
grep -rn "if.*null.*synchronized\|double.check" src/
# Classic pattern: check-lock-check without volatile
```

**Fix:**
```java
// BAD: broken double-checked locking
private static Singleton instance;
static Singleton get() {
    if (instance == null) {
        synchronized (Singleton.class) {
            if (instance == null)
                instance = new Singleton();
                // Other thread may see non-null
                // reference to uninitialized object!
        }
    }
    return instance;
}

// GOOD: volatile prevents reordering
private static volatile Singleton instance;
// Or better: use enum singleton or holder pattern
```
**Prevention:** Use volatile for double-checked locking. Prefer the holder pattern or enum singleton which are simpler and safe.

**Failure Mode 3: Data race in compound operation on volatile**
**Symptom:** Lost updates. Counter is lower than expected despite volatile declaration.
**Root Cause:** volatile guarantees visibility but NOT atomicity of compound operations (read-modify-write). `count++` on volatile is still a race.
**Diagnostic:**

```
grep -rn "volatile.*int\|volatile.*long" src/
# Check if any volatile field has ++, --, +=
# These are NOT atomic despite volatile
```

**Fix:**
```java
// BAD: volatile doesn't make ++ atomic
private volatile int count = 0;
count++; // read + increment + write (3 steps)
// Two threads: both read 5, both write 6 (lost!)

// GOOD: use AtomicInteger
private final AtomicInteger count =
    new AtomicInteger(0);
count.incrementAndGet(); // Atomic CAS operation
```
**Prevention:** Use `AtomicInteger`/`AtomicLong` for counters. Use `synchronized` for multi-step compound operations. Volatile is only for simple read/write visibility.""",

    "JIT Compilation": r"""**Failure Mode 1: Benchmark without warmup produces wrong results**
**Symptom:** Method appears 10-100x slower than expected. Performance varies wildly between runs.
**Root Cause:** Measuring code before JIT compilation. Interpreter executes bytecode ~10-100x slower than JIT-compiled native code.
**Diagnostic:**

```
# Check if method is compiled
# -XX:+PrintCompilation
# Look for method name in output
# Compiled = fast, not present = interpreted
jcmd <pid> Compiler.queue
```

**Fix:**
```java
// BAD: naive benchmark
long start = System.nanoTime();
result = myMethod(data); // May still be interpreted
long time = System.nanoTime() - start;

// GOOD: use JMH with proper warmup
@Benchmark
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 5, time = 1)
public void testMethod(Blackhole bh) {
    bh.consume(myMethod(data));
}
```
**Prevention:** Always use JMH for Java benchmarks. JMH handles warmup, dead code elimination, and JIT compilation barriers.

**Failure Mode 2: Frequent deoptimization causing latency spikes**
**Symptom:** Periodic latency spikes correlated with "made not entrant" events in compilation log. Throughput oscillates.
**Root Cause:** JIT made speculative optimizations (e.g., assumed monomorphic call site) that are invalidated at runtime. Method is deoptimized and recompiled.
**Diagnostic:**

```
# -XX:+PrintCompilation
# Look for "made not entrant" and "made zombie"
grep "not entrant\|zombie" compilation.log
# Frequent entries = unstable optimization
```

**Fix:**
```java
// BAD: polymorphic dispatch defeats inlining
// Method called with different types over time
void process(Shape s) { s.draw(); }
// JIT inlines for Circle, deoptimizes when
// Triangle appears later

// GOOD: stable type profiles
// Design for monomorphic call sites where possible
// Or: accept megamorphic dispatch cost
```
**Prevention:** Design for stable type profiles. Monitor deoptimization events with JFR. Accept megamorphic overhead for genuinely polymorphic code.

**Failure Mode 3: Method too large for inlining**
**Symptom:** Hot method not inlined. Performance lower than expected. `-XX:+PrintInlining` shows "too big".
**Root Cause:** JIT won't inline methods larger than `MaxInlineSize` (35 bytes bytecode default) or `FreqInlineSize` (325 bytes for hot methods). Large methods miss the most impactful optimization.
**Diagnostic:**

```
# Check inlining decisions
# -XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining
# Look for "too big" or "callee is too large"
javap -c MyClass | grep "Code:" -A 1
# Check method bytecode size
```

**Fix:**
```java
// BAD: huge method prevents inlining
void processOrder(Order o) {
    // 500 lines of code
    // JIT: "too big to inline"
}

// GOOD: extract hot path into small methods
void processOrder(Order o) {
    validate(o);     // Small, inlinable
    calculateTotal(o); // Small, inlinable
    persist(o);      // Small, inlinable
}
```
**Prevention:** Keep hot methods small (<35 bytes bytecode for automatic inlining). Use `-XX:+PrintInlining` to verify. Don't manually force with `-XX:MaxInlineSize` (side effects).""",

    "Bytecode": r"""**Failure Mode 1: VerifyError at class loading**
**Symptom:** `java.lang.VerifyError` when class is loaded. Application fails to start or fails at runtime when the class is first used.
**Root Cause:** Bytecode manipulation (ASM, ByteBuddy, agent) produced invalid bytecode that fails the JVM verifier. Common: wrong stack depth, type mismatch, invalid branch target.
**Diagnostic:**

```
# Get detailed verify error
java -Xverify:all -verbose:class -cp app.jar Main
# The error message shows the exact opcode position
# and expected vs actual stack/type state
```

**Fix:**
```java
// BAD: bytecode manipulation without verification
ClassWriter cw = new ClassWriter(0);
// Generating bytecode with wrong stack calculation

// GOOD: use COMPUTE_FRAMES for automatic verification
ClassWriter cw = new ClassWriter(
    ClassWriter.COMPUTE_FRAMES);
// ASM will compute stack maps and verify frames
// Or: use ByteBuddy which handles this automatically
```
**Prevention:** Use `ClassWriter.COMPUTE_FRAMES` with ASM. Use higher-level APIs (ByteBuddy) that handle verification. Test with `-Xverify:all`.

**Failure Mode 2: IncompatibleClassChangeError from stale bytecode**
**Symptom:** `IncompatibleClassChangeError`, `NoSuchMethodError`, or `AbstractMethodError` at runtime despite correct source code.
**Root Cause:** Compiled bytecode references a method/field signature that changed in a dependency. Binary was compiled against an old version.
**Diagnostic:**

```
# Check the bytecode reference
javap -c -p MyClass.class | grep "invoke"
# Compare with actual method signature in dependency
javap -p DependencyClass.class | grep "methodName"
```

**Fix:**
```java
// BAD: compiled against old API
// MyClass.class has: invokevirtual Lib.old(I)V
// New Lib.class has: Lib.old(J)V (int->long)

// GOOD: recompile against current dependencies
// mvn clean compile
// Ensure compile-time and runtime versions match
```
**Prevention:** Recompile when dependencies change. Use Maven Enforcer for version consistency. CI should build from scratch, not incrementally.

**Failure Mode 3: Performance regression from bytecode bloat**
**Symptom:** Method performance degrades. JIT won't inline. Generated bytecode is much larger than equivalent hand-written code.
**Root Cause:** Frameworks (Spring AOP, Hibernate) generate proxy classes with large bytecode. Excessive indirection prevents JIT inlining.
**Diagnostic:**

```
# Check bytecode size of generated class
javap -c -p GeneratedProxy.class | wc -l
# Compare with original class
# Check inlining: -XX:+PrintInlining
```

**Fix:**
```java
// BAD: every method call goes through proxy
// -> 3 layers of bytecode indirection
// Original -> CGLIB proxy -> interceptor chain

// GOOD: minimize proxy layers
// Use interface-based proxies (smaller bytecode)
// Use compile-time weaving (AspectJ) instead of
// runtime bytecode generation
```
**Prevention:** Profile proxy overhead. Use compile-time weaving for critical paths. Monitor method bytecode size. Keep hot methods small and inlinable.""",
}

# ── Related Keywords ─────────────────────────────────────

RELATED = {
    "JVM Architecture": r"""**Prerequisites (understand these first):**

- Operating system concepts - processes, threads, virtual memory, context switching
- Compilation fundamentals - source code, compilation, linking, execution

**Builds on this (learn these next):**

- Class Loading - how the JVM finds, loads, and initializes types
- GC Algorithms - how the JVM manages heap memory automatically

**Alternatives / Comparisons:**

- .NET CLR - similar managed runtime with reified generics and AOT compilation
- GraalVM Native Image - AOT compilation for JVM languages, fast startup, no JIT""",

    "Class Loading": r"""**Prerequisites (understand these first):**

- JVM Architecture - understanding the overall JVM subsystem structure
- Java classpath and modules - how classes are organized and located

**Builds on this (learn these next):**

- Bytecode - the format that class loading reads and the verifier checks
- JPMS (Java modules) - the module system that extends classloader isolation

**Alternatives / Comparisons:**

- OSGi - dynamic module system with fine-grained classloader isolation
- Java modules (JPMS) - built-in module system replacing classpath for modular apps""",

    "Memory Model": r"""**Prerequisites (understand these first):**

- Java threading basics - Thread, Runnable, synchronized, wait/notify
- CPU architecture concepts - caches, store buffers, memory ordering

**Builds on this (learn these next):**

- Java Concurrency utilities - Lock, Semaphore, ConcurrentHashMap built on JMM guarantees
- Atomic classes - lock-free programming using CAS operations and JMM semantics

**Alternatives / Comparisons:**

- C++ memory model (std::memory_order) - more explicit control over ordering constraints
- Go memory model - simpler, based on channel communication (CSP)""",

    "JIT Compilation": r"""**Prerequisites (understand these first):**

- JVM Architecture - the overall execution engine that houses the JIT
- Bytecode - the input format that JIT compiles to native code

**Builds on this (learn these next):**

- Performance profiling (JFR, async-profiler) - measuring JIT effectiveness
- GraalVM compiler - alternative JIT with ahead-of-time compilation option

**Alternatives / Comparisons:**

- AOT compilation (GraalVM native-image) - compile-time optimization, instant startup, no warmup
- Interpreted execution - no compilation overhead but 10-100x slower""",

    "Bytecode": r"""**Prerequisites (understand these first):**

- JVM Architecture - the virtual machine that executes bytecode
- Java compilation (javac) - the compiler that produces bytecode from source

**Builds on this (learn these next):**

- JIT Compilation - how bytecode is optimized to native machine code at runtime
- Bytecode manipulation (ASM, ByteBuddy) - frameworks for programmatic bytecode generation

**Alternatives / Comparisons:**

- .NET IL (Intermediate Language) - similar portable IR for the CLR ecosystem
- WebAssembly - portable bytecode format for web browsers and edge computing""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
