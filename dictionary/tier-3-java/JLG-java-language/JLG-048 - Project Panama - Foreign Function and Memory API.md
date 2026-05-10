---
id: JLG-048
title: "Project Panama: Foreign Function and Memory API"
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-001, JLG-046
used_by:
related: JLG-045, JLG-047, JLG-049
tags:
  - java
  - advanced
  - internals
  - deep-dive
status: complete
version: 2
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /jlg/project-panama-foreign-function-and-memory-api/
---

# JLG-048 - Project Panama: Foreign Function and Memory API

⚡ TL;DR - The Foreign Function and Memory (FFM) API (Java 22, JEP 454) replaces JNI with type-safe, memory-managed Java calls to native C libraries using `Linker`, `MemorySegment`, and `Arena` without writing C code.

| Field | Value |
|---|---|
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-046 - Java Language Specification Deep Dive]] |
| **Used by** | (none yet) |
| **Related** | [[JLG-045 - Java in Polyglot Architecture]], [[JLG-047 - Project Valhalla - Value Types and Primitives]], [[JLG-049 - Java Language Design History and Rationale]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

JNI (Java Native Interface, 1997) was the only way to call native C/C++ libraries from Java. JNI requires: (1) writing a C header file, (2) implementing C wrapper functions with JNI signatures (`JNIEXPORT void JNICALL Java_com_example_MyClass_myMethod`), (3) managing raw C pointers manually. JNI is verbose, error-prone, memory-unsafe (no GC for native memory), and difficult to debug. A single mistake causes JVM crashes, not exceptions.

**THE BREAKING POINT:**

Modern Java applications need native access for: operating system calls not in the JDK, high-performance libraries (OpenSSL, LZ4, LevelDB), GPU computation APIs (CUDA, OpenCL), and hardware device drivers. JNI's 27-year-old design made every native integration a specialist project taking weeks. Incorrect JNI code causes silent memory corruption.

**THE INVENTION MOMENT:**

**Project Panama** (Java 14-22) incrementally delivered the Foreign Function and Memory API (JEP 454, finalised Java 22). FFM provides:
- `MemorySegment`: a bounded, lifecycle-managed chunk of native or heap memory
- `Arena`: manages `MemorySegment` lifetime; auto-closes segments when arena closes
- `Linker`: looks up and calls native function symbols by name
- `FunctionDescriptor`: describes C function signature (return type + parameter types)
- `jextract`: tool that generates Java bindings from C header files automatically

**EVOLUTION:**

- **1997:** JNI - Java Native Interface; the original C interop mechanism
- **2020:** Java 14 - `jdk.incubator.foreign` (JEP 370); first incubation
- **2021:** Java 16/17 - API iterates; `MemoryAddress`, `MemorySegment` take shape
- **2022:** Java 19 - `java.lang.foreign` package; third incubation
- **2023:** Java 21 - second preview (JEP 442)
- **2024:** Java 22 - **Finalised** (JEP 454); stable API; JNI deprecation signals

---

### 📘 Textbook Definition

The **Foreign Function and Memory (FFM) API** (`java.lang.foreign`, finalised Java 22) enables Java programs to:

- **Allocate native memory** (`MemorySegment.allocateNative()`): off-heap memory outside GC management
- **Manage memory lifetime** (`Arena`): `Arena.ofConfined()`, `Arena.ofShared()`, `Arena.global()` control when native memory is freed
- **Call native functions** (`Linker`): look up C function by symbol name; create `MethodHandle` that calls it directly
- **Describe C types** (`MemoryLayout`): C structs, arrays, and primitive types described as Java objects; enables struct field access by name

---

### ⏱️ Understand It in 30 Seconds

**One line:** FFM API lets Java call C functions and manage native memory safely with `Linker`, `MemorySegment`, and `Arena` - no C boilerplate required.

> The FFM API is like a well-staffed customs office at the Java-C border. JNI was a 1990s border crossing: bring your own passport (C header file), fill out forms in C (wrapper functions), and manage your own baggage (raw pointers). FFM is the modern e-gate: describe what you need (`FunctionDescriptor`), present it at the customs scanner (`Linker`), get a typed pass (`MethodHandle`), and the customs office (`Arena`) manages your baggage lifetime automatically.

**One insight:** `jextract` - the companion tool to FFM - reads a C header file (`.h`) and generates all the Java `MemoryLayout` and `MethodHandle` bindings automatically. Calling a C library becomes: run `jextract`, import the generated class, call the method.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Native memory is not managed by the JVM GC; it must be explicitly freed to avoid native memory leaks
2. A `MemorySegment` has a fixed bound; accessing beyond bounds throws `IndexOutOfBoundsException` (safety guarantee absent in JNI)
3. A `MemorySegment` from a closed `Arena` throws `IllegalStateException`; use-after-free is caught at access time, not at crash time
4. C function calling convention (ABI) must match exactly; wrong `FunctionDescriptor` causes JVM crash or silent data corruption
5. `MethodHandle` invocation through `Linker.downcallHandle()` is zero-overhead after JIT compilation; no reflection cost

**DERIVED DESIGN:**

From invariant 1 → `Arena` wraps `MemorySegment` lifecycle; `try-with-resources` ensures cleanup.
From invariant 2 → `MemorySegment` is safer than JNI raw `long` addresses; bounds checks are automatic.
From invariant 5 → FFM performance equals JNI for hot-path C calls; no overhead penalty for using the safe API.

**THE TRADE-OFFS:**

**Gain:** Type-safe native interop with bounds checking; automatic memory management via `Arena`; no C boilerplate; `jextract` generates bindings from headers.

**Cost:** `FunctionDescriptor` must match C ABI exactly (wrong types cause crashes); still requires understanding of C memory layouts for struct access; debugging native crashes still requires C-level tools.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** C function signatures and memory layouts must be described correctly; this is inherent to native interop.

**Accidental:** JNI's C wrapper files, header generation, and `javah` tool were accidental complexity. FFM eliminates them; `jextract` handles the mechanical translation.

---

### 🧪 Thought Experiment

**SETUP:** A Java application needs to call `libz` (zlib) for compression. Today's choice: use JNI (write C wrapper code) or use a Java zlib wrapper library (adds a dependency, may be outdated).

**WHAT HAPPENS WITH JNI:**

1. Write `compress_native.h` and `compress_native.c` with JNI signatures
2. Compile to `.so` shared library
3. Load via `System.loadLibrary()`
4. Handle JNI environment management in C
5. Every parameter passing requires JNI type conversion (`jint`, `jarray`, etc.)
6. Memory errors cause JVM crash with no Java stack trace

**WHAT HAPPENS WITH FFM API:**

```java
// 1. Run: jextract --output src zlib.h
// 2. Import generated bindings
// 3. Call directly:
try (Arena arena = Arena.ofConfined()) {
    MemorySegment dest =
        arena.allocate(1024);
    MemorySegment src =
        arena.allocateFrom(inputData);
    long result = zlib.compress(
        dest, destLen, src, src.byteSize());
}
```

**THE INSIGHT:**

FFM makes native library integration a half-day task instead of a multi-day specialist task. The C wrapper code is generated, not hand-written.

---

### 🧠 Mental Model / Analogy

> FFM's `Arena` + `MemorySegment` is like a rental car company for native memory. `Arena.ofConfined()` is renting a car for a day: you get it, use it, and when your rental expires (arena closes), it goes back to the fleet (native memory freed). `Arena.global()` is buying a car: it exists for the program's lifetime. A `MemorySegment` is the car: you can drive it (access memory) but only while the rental is active (arena open). Trying to drive after the rental expires (accessing segment after arena close) throws an exception instead of crashing.

**Element mapping:**
- Rental company → `Arena` managing native memory
- Car rental duration → arena lifecycle
- Car → `MemorySegment`
- Driving the car → reading/writing segment bytes
- Returning the car → arena close (free native memory)
- Driving after return → `IllegalStateException` (caught)
- JNI raw pointer → buying a car with no records (unmanaged)

Where this analogy breaks down: unlike rental cars, a `MemorySegment` from a `shared` arena can be used across threads; a `confined` arena's segments are single-threaded.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java can now call native C/C++ libraries directly without writing C code. The FFM API provides Java classes for allocating native memory, describing C function signatures, and calling C functions safely. If a native memory access is out of bounds, Java throws an exception instead of crashing.

**Level 2 - How to use it (junior developer):**
```java
import java.lang.foreign.*;
import java.lang.invoke.*;

// Call C strlen() without JNI:
Linker linker = Linker.nativeLinker();
SymbolLookup stdlib =
    linker.defaultLookup();

MethodHandle strlenHandle =
    linker.downcallHandle(
        stdlib.find("strlen").orElseThrow(),
        FunctionDescriptor.of(
            ValueLayout.JAVA_LONG,  // return
            ValueLayout.ADDRESS     // char*
        )
    );

try (Arena arena = Arena.ofConfined()) {
    MemorySegment str =
        arena.allocateFrom("Hello World");
    long len = (long) strlenHandle.invoke(str);
    // len == 11
}
```

**Level 3 - How it works (mid-level engineer):**
`Linker.downcallHandle()` returns a `MethodHandle` that, when invoked, marshals Java types to C ABI types, transfers control to the native function via a dynamically generated stub, and marshals the return value back. The stub is generated by the Linker implementation at first call and cached. On x86-64 Linux (System V ABI), integer arguments go in `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` registers; floating-point in `xmm0`-`xmm7`. The Linker generates machine code that moves Java values into these registers before the `CALL` instruction.

**Level 4 - Why it was designed this way (senior/staff):**
The `Arena` lifecycle model (confined, shared, global) was designed to match the common patterns of native memory usage while providing safety. Confined arenas are single-threaded: segment access from other threads throws `WrongThreadException` at the API level, not a JVM crash. Shared arenas use reference counting to delay deallocation until all segments are closed. Global arenas use `malloc`-style explicit management. The three modes cover: scoped method-local allocation (confined), cross-thread shared buffers (shared), and long-lived program-global structures (global). This is more ergonomic than raw `malloc`/`free` while providing provable memory safety from the Java side.

**Expert Thinking Cues:**
- `StructLayout` and `UnionLayout` describe C struct/union layouts including padding; field access uses `VarHandle` obtained from layout (type-safe, no manual offset calculation)
- Upcall stubs (`Linker.upcallStub()`) enable C code to call back into Java; used for callback-based APIs (libuv event loops, libssh2 callbacks)
- `MemorySegment.reinterpret()` relaxes bounds; used when C returns an address that is not a Java-allocated segment; marks the segment with new bounds

---

### ⚙️ How It Works (Mechanism)

```
FFM Architecture:

[Java code]
  MethodHandle mh =
    linker.downcallHandle(addr, descriptor)
     |
     v
[Linker generates native stub]
  Stub maps Java types to C ABI types
  Moves args to registers (System V ABI)
  Issues CALL instruction to native addr
     |
     v
[Native C function executes]
  Reads args from registers/stack
  Returns via rax register
     |
     v
[Linker stub marshals return value]
  Maps C return to Java type
     |
     v
[Java receives typed result]

Memory Safety Layer:
  MemorySegment = address + size + scope
  Access beyond size -> IOOBE
  Access after scope close -> ISE
  JNI: address only -> crash on violation
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Need to call native library]
     |
     ├─ Option A: Use jextract (recommended)
     |    jextract --output src mylib.h
     |    Import generated bindings
     |    Call type-safe generated methods
     |         ← YOU ARE HERE
     |
     ├─ Option B: Manual FFM API
     |    Linker.nativeLinker()
     |    .defaultLookup().find("myFunc")
     |    linker.downcallHandle(addr, desc)
     |
[Allocate memory with Arena]
     |
     ├─ Arena.ofConfined() for local scope
     ├─ Arena.ofShared() for multi-thread
     └─ Arena.global() for program lifetime

[Call via MethodHandle.invoke()]
     |
     └─ Native executes; result returned
          Arena.close() frees all segments
```

**FAILURE PATH:**

Wrong `FunctionDescriptor`: Java passes `int` where C expects `long`. On x86-64, int is 32-bit, long is 64-bit. The high 32 bits of the register are garbage. Function returns corrupt result or crashes.

**WHAT CHANGES AT SCALE:**

At scale, `MethodHandle` invocations are JIT-compiled to direct CALL instructions; no overhead after warmup. `Arena.ofShared()` uses atomic reference counting; high-frequency creation/close of shared arenas causes contention. For hot paths: use thread-confined arenas and segment reuse.

---

### 💻 Code Example

**Calling libssl's MD5 via FFM (example):**

```java
// BAD: JNI approach (requires C wrapper)
// C wrapper file needed:
// JNIEXPORT jbyteArray JNICALL
// Java_com_example_Crypto_md5(
//   JNIEnv* env, jclass cls,
//   jbyteArray input) { ... }

// GOOD: FFM API (pure Java)
import java.lang.foreign.*;
import java.lang.invoke.*;
import static java.lang.foreign.ValueLayout.*;

public class Md5FFM {
    private static final Linker LINKER =
        Linker.nativeLinker();

    // Call C strlen via FFM:
    private static final MethodHandle STRLEN =
        LINKER.downcallHandle(
            LINKER.defaultLookup()
                .find("strlen").orElseThrow(),
            FunctionDescriptor.of(
                JAVA_LONG,  // size_t return
                ADDRESS     // const char*
            )
        );

    public static long strlen(String s)
        throws Throwable {
        try (Arena arena = Arena.ofConfined()) {
            MemorySegment cStr =
                arena.allocateFrom(s);
            return (long) STRLEN.invoke(cStr);
        }
        // arena.close() frees cStr
    }
}
```

**Struct layout access:**

```java
// C struct: struct Point { int x; int y; }
StructLayout POINT_LAYOUT = MemoryLayout
    .structLayout(
        JAVA_INT.withName("x"),
        JAVA_INT.withName("y")
    );

VarHandle X = POINT_LAYOUT
    .varHandle(
        MemoryLayout.PathElement.groupElement("x")
    );

try (Arena arena = Arena.ofConfined()) {
    MemorySegment point =
        arena.allocate(POINT_LAYOUT);
    X.set(point, 0L, 42); // set x=42
    int x = (int) X.get(point, 0L); // x==42
}
```

**How to test / verify correctness:**

```bash
# Generate bindings from header:
jextract --output src \
  --target-package com.example.bindings \
  /usr/include/string.h

# Verify native library loads:
System.loadLibrary("mylib");
# If UnsatisfiedLinkError: check LD_LIBRARY_PATH

# Check segment bounds:
# Enable bounds checking (default on):
java -Djava.foreign.check.bounds=true MyApp
```

---

### ⚖️ Comparison Table

| Feature | JNI (Java 1.1) | FFM API (Java 22) | JNA (third-party) |
|---|---|---|---|
| C boilerplate | Yes (C wrapper) | No | No |
| Type safety | Low (raw types) | High (layouts) | Medium (auto-mapping) |
| Memory safety | None (raw pointers) | Bounds + scope | None (raw pointers) |
| Performance | High (direct) | High (after JIT) | Lower (reflection) |
| Upcalls (C calls Java) | Yes | Yes | Yes |
| jextract support | N/A | Yes | No |
| Status | Deprecated signals | Stable (Java 22+) | Third-party |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "FFM API is slower than JNI" | After JIT compilation, FFM `MethodHandle` invocation is equivalent to JNI. Initial calls are slower due to stub generation; this warms up within milliseconds. |
| "Arena.close() is optional" | Not closing an arena leaks native memory. JVM GC does not manage native memory. Use try-with-resources for confined/shared arenas. |
| "FFM replaces all JNI use cases" | FFM replaces C-library interop. For passing Java arrays to C without copy, JNI `GetPrimitiveArrayCritical` has no FFM equivalent. |
| "jextract generates complete safe bindings" | jextract generates mechanical bindings from headers. Caller must still understand C semantics (pointer ownership, error codes, thread safety). |
| "MemorySegment.reinterpret() is safe" | `reinterpret()` removes bounds checks. It is a safety escape hatch for C APIs that return addresses; use only when bounds are known from C docs. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Wrong FunctionDescriptor causes silent data corruption**

**Symptom:** Native function returns wrong values. No exception thrown. JVM does not crash.

**Root Cause:** `FunctionDescriptor` declares `JAVA_INT` return type but C function returns `long`. 32-bit read truncates the 64-bit return value. Upper bits lost silently.

**Diagnostic:**
```bash
# Enable JVM crash on native access anomaly:
java -XX:+CheckJNICalls MyApp
# Also verify FunctionDescriptor against
# the actual C header file:
nm -D libmylib.so | grep myFunction
# Check symbol signature matches
```

**Fix:** Match `FunctionDescriptor` exactly to C function signature. Use `jextract` to generate bindings automatically from the header file.

**Prevention:** Always use `jextract` when the C header is available. For manual bindings, have a C expert verify the `FunctionDescriptor` against the header.

---

**Mode 2: Native memory leak from unclosed Arena**

**Symptom:** JVM heap stable but native memory (RSS in OS) grows unboundedly. OOM from OS, not JVM.

**Root Cause:** `Arena.ofConfined()` created but not closed. Native memory freed only when `close()` called.

**Diagnostic:**
```bash
# Monitor native memory:
jcmd <pid> VM.native_memory
# Shows: Other (native) memory usage

# Or with /proc:
cat /proc/<pid>/status | grep VmRSS
# Growing VmRSS with stable JVM heap
# = native memory leak
```

**Fix:** Always use `try-with-resources` for arenas:
```java
try (Arena arena = Arena.ofConfined()) {
    // arena.close() guaranteed at end
}
```

**Prevention:** Code review rule: every `Arena.ofConfined()` or `Arena.ofShared()` call must be in a try-with-resources block.

---

**Mode 3: MemorySegment access from wrong thread (Security/Safety)**

**Symptom:** `WrongThreadException: Attempting to call close on scope owned by thread X from thread Y` in multi-threaded code.

**Root Cause:** `Arena.ofConfined()` segments are single-threaded. Another thread attempts to access or close the arena.

**Diagnostic:**
```java
// Check thread ownership at runtime:
// WrongThreadException message includes
// owning thread name - use for diagnosis

// Add defensive check:
Thread owner = Thread.currentThread();
assert owner == arenaOwner :
    "Arena used from wrong thread";
```

**Fix:** Use `Arena.ofShared()` for segments accessed from multiple threads. Or pass segments to worker threads using the owned-thread pattern (create in thread, pass only the data).

**Prevention:** Design rule: confined arenas are method-scoped; shared arenas are field-scoped with explicit ownership transfer.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-001 - What Is Java - History and Philosophy]] - JVM memory model; JNI history
- [[JLG-046 - Java Language Specification Deep Dive]] - memory ordering at native boundary

**Builds On This (learn these next):**
- [[JLG-045 - Java in Polyglot Architecture]] - FFM as one polyglot integration mechanism

**Alternatives / Comparisons:**
- JNA (Java Native Access) - third-party library for JNI-free native calls; uses reflection; lower performance than FFM
- JNI - legacy mechanism; still works; being soft-deprecated as FFM matures

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | FFM API: type-safe native C interop via |
|               | Linker, MemorySegment, Arena (Java 22+) |
| PROBLEM       | JNI requires C wrapper code; unsafe raw |
|               | pointers; crashes instead of exceptions |
| KEY INSIGHT   | Arena manages native memory lifetime;   |
|               | closed segments throw ISE not crash     |
| USE WHEN      | Calling native C/C++ libraries; off-heap|
|               | memory management; system call wrapping |
| AVOID WHEN    | Pure Java solutions exist; JNI code     |
|               | already working and stable              |
| TRADE-OFF     | Type-safe + managed vs must match C ABI |
|               | exactly; wrong FunctionDescriptor = crash|
| ONE-LINER     | Linker.downcallHandle(symbol, desc) =   |
|               | direct C function call from pure Java   |
| NEXT EXPLORE  | JLG-045 (Polyglot architecture),        |
|               | JLG-047 (Valhalla value types)          |
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. `Arena` manages native memory lifetime; always use try-with-resources; unclosed arena = native memory leak
2. `FunctionDescriptor` must exactly match the C function signature; wrong types = JVM crash or silent corruption
3. `jextract` generates Java bindings from C header files automatically; use it instead of manual `FunctionDescriptor` definitions

**Interview one-liner:** "The Foreign Function and Memory API (Java 22, JEP 454) replaces JNI with pure-Java native interop: `Linker.downcallHandle(symbol, FunctionDescriptor)` creates a `MethodHandle` that calls a C function directly; `Arena` manages native memory lifetime with automatic cleanup on close; `MemorySegment` adds bounds checking absent in JNI's raw pointers."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** *Lifecycle management must be explicit and enforceable at the language/API level to prevent resource leaks.* JNI's raw pointers have no enforced lifecycle - leaks are found through observation, not compilation. FFM's `Arena` makes the lifecycle explicit and enforceable through `AutoCloseable` + `try-with-resources`. The same principle applies to database connections (`Connection.close()`), file handles (`InputStream.close()`), and locks (`Lock.unlock()`). Every resource with an explicit lifecycle should implement `AutoCloseable`.

**Where else this pattern appears:**
- **Python context managers (`with` statement):** `with open(file) as f:` - file handle closed automatically; same pattern as `try (Arena arena = ...)` in FFM
- **Go `defer`:** `defer file.Close()` ensures cleanup runs when function returns; similar lifecycle guarantee to `try-with-resources`
- **Rust ownership and drop:** when an owner goes out of scope, `drop()` is called automatically; this is the most principled version of the same lifecycle management concept

---

### 💡 The Surprising Truth

JNI has a safety feature so dangerous that the JDK team quietly deprecated it: `GetPrimitiveArrayCritical`. This JNI function returns a direct pointer to a Java array's memory, bypassing the GC. While holding this pointer, the JVM pauses GC collection for the entire heap to prevent the array from being moved. If two threads call `GetPrimitiveArrayCritical` simultaneously, the entire JVM is paused until both release their pointers. In theory this is "milliseconds"; in practice, buggy native code has caused production outages where the JVM appeared completely frozen. The FFM API has no equivalent - all native memory is explicitly allocated outside the GC heap. The removal of `GetPrimitiveArrayCritical`-style access from the modern Java interop story reflects a design insight: mixing GC-managed and unmanaged memory in the same address range is fundamentally dangerous.

---

### 🧠 Think About This Before We Continue

**Question 1 (E - First Principles):** `Arena.ofConfined()` creates a single-threaded arena where segments can only be accessed from the creating thread. `Arena.ofShared()` uses reference counting to allow access from multiple threads. If an application creates 10,000 short-lived arenas per second (one per request), which arena type should be used, and what is the performance implication of the choice?

*Hint:* Reference counting uses atomic operations (compare-and-swap). Under high concurrency, atomic CAS operations cause cache-line contention. Research the cost of `AtomicInteger.decrementAndGet()` under high thread contention versus the cost of a single-threaded counter decrement. Consider whether per-request native memory allocation is the correct design.

**Question 2 (C - Design Trade-off):** A Java image processing service uses FFM to call `libpng` for PNG encoding. The `libpng` API is callback-based: it calls a user-supplied write function for each data chunk. FFM's `Linker.upcallStub()` creates a native function pointer that calls back into Java. Describe the implications of using upcall stubs in a high-throughput service: (a) performance overhead per upcall, (b) thread model constraints, and (c) alternative design that avoids upcalls entirely.

*Hint:* Each `upcallStub` involves a transition from native execution back to the JVM. Research the cost of JNI/FFM transitions (estimated at 100-500 cycles). Consider whether `libpng`'s in-memory buffer mode (`png_init_io` with a memory stream) avoids the need for callbacks entirely.

**Question 3 (B - Scale):** A microservice processes 100,000 requests per second, each requiring LZ4 compression of a 10KB payload via FFM calling `liblz4`. Each request allocates a `Arena.ofConfined()` with a 10KB `MemorySegment` for input and 12KB for output. Calculate the native memory allocation rate and describe the pooling strategy needed to prevent native allocator overhead from becoming a bottleneck.

*Hint:* 100,000 requests/s × (10KB + 12KB) = 2.2GB/s native allocation rate. Native `malloc`/`free` is not designed for this rate. Research `jemalloc` thread-local caches and whether `MemorySegment` reuse (retain the segment, reset contents) is possible within the FFM API. Consider `SegmentAllocator.slicingAllocator()` as a bump-pointer allocator for request-scoped segments.
