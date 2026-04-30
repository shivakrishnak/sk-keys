---
layout: default
title: "Metaspace"
parent: "Java & JVM Internals"
nav_order: 8
permalink: /java/metaspace/
---
# 008 — Metaspace

`#java` `#jvm` `#memory` `#internals` `#classloading` `#intermediate`

⚡ TL;DR — Off-heap native memory region that stores class metadata, replacing PermGen in Java 8 — grows dynamically and lives outside GC-managed heap.

| #008 | Category: JVM Memory | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Class Loader, Heap Memory | |
| **Used by:** | Every loaded class, Spring, Hibernate | |

---

### 📘 Textbook Definition

Metaspace is a **native memory region** (off-heap) introduced in Java 8 to replace PermGen. It stores **class metadata** — the structural descriptions of loaded classes including method bytecode, field definitions, constant pools, and annotations. Unlike PermGen, Metaspace is not bounded by heap limits and grows dynamically into native OS memory — but must be explicitly capped to prevent unbounded growth.

---

### 🟢 Simple Definition (Easy)

Metaspace is where the JVM stores **the blueprints of your classes** — not your objects (that's heap), but the class definitions themselves. It lives outside the heap in native memory.

---

### 🔵 Simple Definition (Elaborated)

Every class the JVM loads needs to store its structure somewhere — method signatures, bytecode, field types, constant pools. That storage is Metaspace. It's separate from the heap because class metadata has a completely different lifecycle from objects — it lives as long as its ClassLoader is alive. By moving it off-heap into native memory, Java 8 removed the infamous `OutOfMemoryError: PermGen space` and let Metaspace grow as needed — which sounds great until it grows without bound and exhausts native memory instead.

---

### 🔩 First Principles Explanation

**The PermGen problem (pre Java 8):**

Before Java 8, class metadata lived in **PermGen** — a fixed-size heap region:

bash

```bash
java -XX:MaxPermSize=256m MyApp  # had to guess the right size
```

Two failure modes:

```
Too small → OutOfMemoryError: PermGen space
            (common in apps with lots of classes or hot redeploy)

Too large → wasted heap space reserved but unused
```

PermGen was also collected by Full GC — meaning class metadata cleanup was tied to the most expensive GC operation.

**The deeper problem:**

Class metadata lifetime ≠ object lifetime.

```
Object lifetime:   created → used → unreachable → GC collects
Class lifetime:    loaded → used until ClassLoader dies → then collected
```

Mixing them in the same memory region (heap) was conceptually wrong.

**The Java 8 solution — Metaspace:**

> "Move class metadata to native memory. Let it grow dynamically. Collect it when its ClassLoader is GC'd — not on every Full GC."

```
Before Java 8:                After Java 8:
┌──────────────┐              ┌──────────────┐  ┌─────────────┐
│     Heap     │              │     Heap     │  │  Metaspace  │
│  ┌────────┐  │              │              │  │  (native)   │
│  │PermGen │  │              │  Objects     │  │  Classes    │
│  │Classes │  │              │  Arrays      │  │  Methods    │
│  └────────┘  │              │              │  │  Constants  │
│  Objects     │              └──────────────┘  └─────────────┘
│  Arrays      │              bounded by -Xmx   grows into OS
└──────────────┘                                memory
bounded by -Xmx
+ MaxPermSize
```

---

### 🧠 Mental Model / Analogy

> Think of a city (JVM) with two kinds of storage:
> 
> **Heap** = apartment buildings where residents (objects) live. Buildings have a fixed total capacity (`-Xmx`).
> 
> **Metaspace** = the city's **architectural office** — stores blueprints (class definitions) for every building type. The office is outside the residential zone (off-heap), in its own district (native memory). It expands by renting more office space from the OS as needed.
> 
> When a building type is no longer used (ClassLoader unloaded) — the blueprints are archived and the office space reclaimed.

---

### ⚙️ What Lives in Metaspace

> **Critical nuance:** Static variable **references** are stored in the class metadata in Metaspace, but the **objects they point to** live on the heap. This is a common exam and interview confusion point.

---

### ⚙️ Metaspace Lifecycle — Tied to ClassLoader

```
ClassLoader created
      ↓
Classes loaded → metadata allocated in Metaspace
      ↓
Classes used (methods called, objects created)
      ↓
ClassLoader becomes unreachable
(no more references to it or its classes)
      ↓
Next GC cycle detects unreachable ClassLoader
      ↓
ALL metadata for ALL classes loaded by that
ClassLoader freed from Metaspace
      ↓
Metaspace space reclaimed
```

**This is why hot redeploy leaks Metaspace:**

```
Deploy v1 → ClassLoader1 loads 500 classes → 50MB Metaspace
Redeploy → ClassLoader2 loads 500 classes → +50MB Metaspace
           ClassLoader1 should be freed...
           BUT if any reference to ClassLoader1's classes
           survives (static field, thread local, cache) →
           ClassLoader1 NOT GC'd → 50MB STUCK in Metaspace

Redeploy again and again → Metaspace grows → OOM: Metaspace
```

---

### 🔄 How It Connects

```
javac → Bytecode (.class)
             ↓
        Class Loader reads bytecode
             ↓
   [Metaspace] ← class structure stored here
             ↓
        JVM creates Class object → [Heap]
             ↓
   new MyObject() → instance → [Heap]
        uses class structure from [Metaspace]
             ↓
   ClassLoader unreachable → Metaspace entry freed
```

---

### 💻 Code Example

**Monitoring Metaspace programmatically:**

java

```java
import java.lang.management.*;
import java.util.List;

public class MetaspaceMonitor {
    public static void main(String[] args) {
        List<MemoryPoolMXBean> pools =
            ManagementFactory.getMemoryPoolMXBeans();

        pools.stream()
             .filter(p -> p.getName().contains("Metaspace"))
             .forEach(p -> {
                 MemoryUsage usage = p.getUsage();
                 System.out.printf(
                     "%-30s used=%dMB  committed=%dMB  max=%s%n",
                     p.getName(),
                     usage.getUsed()      / 1024 / 1024,
                     usage.getCommitted() / 1024 / 1024,
                     usage.getMax() == -1
                         ? "unlimited"
                         : usage.getMax() / 1024 / 1024 + "MB"
                 );
             });
    }
}

// Output (no MaxMetaspaceSize set):
// Metaspace    used=45MB  committed=46MB  max=unlimited
// ← "unlimited" is dangerous in production
```

**Simulating Metaspace exhaustion — class generation:**

java

```java
import net.bytebuddy.ByteBuddy; // or use ASM directly

public class MetaspaceExhaust {
    public static void main(String[] args) throws Exception {
        // Generate and load unique classes in a loop
        // Each class adds metadata to Metaspace
        // ClassLoader kept alive → no Metaspace reclaim

        List<Class<?>> classes = new ArrayList<>();
        int count = 0;
        try {
            while (true) {
                // Generate a new unique class dynamically
                Class<?> c = new ByteBuddy()
                    .subclass(Object.class)
                    .make()
                    .load(MetaspaceExhaust.class.getClassLoader())
                    .getLoaded();
                classes.add(c); // hold ref → ClassLoader stays alive
                count++;
                if (count % 1000 == 0)
                    System.out.println("Loaded: " + count + " classes");
            }
        } catch (OutOfMemoryError e) {
            System.out.println("OOM after " + count + " classes");
            System.out.println(e.getMessage());
            // Output: OOM after ~XXXXX classes
            //         Metaspace
        }
    }
}
```

**Inspecting Metaspace from command line:**

bash

```bash
# Live Metaspace usage breakdown by ClassLoader
jcmd <pid> VM.metaspace

# Output:
# Total Usage - 1018 loaders, 10345 classes:
#   Non-class:  47.36 MB
#   Class    :   6.12 MB
#   Total    :  53.48 MB
# Virtual space:
#   Non-class space:  50.00 MB reserved, 47.75 MB committed
#   Class space   :  1.00 GB reserved,   6.25 MB committed

# Class histogram — what's taking space
jcmd <pid> GC.class_histogram | head -30

# Class loader stats
jmap -clstats <pid>
# Shows each ClassLoader, how many classes it loaded,
# and memory consumed → identify leaking loaders
```

**Setting Metaspace limits — production config:**

bash

```bash
# No cap (dangerous — can exhaust native memory):
java -jar myapp.jar

# Capped (recommended):
java -XX:MaxMetaspaceSize=256m -jar myapp.jar

# Also tune initial size to avoid early resizing:
java -XX:MetaspaceSize=128m \
     -XX:MaxMetaspaceSize=256m \
     -jar myapp.jar

# MetaspaceSize = initial committed size (not max)
# When Metaspace hits MetaspaceSize → GC triggered
# Set high enough to avoid early GC thrashing
```

---

### ⚙️ PermGen vs Metaspace — Side by Side

---

### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Metaspace is part of heap"|It's **native memory** — outside heap, not bounded by `-Xmx`|
|"Metaspace stores objects"|It stores **class structures** — objects always live on heap|
|"Metaspace replaced PermGen entirely"|PermGen stored static vars + String pool too — those moved to **heap**|
|"Metaspace grows freely = no problem"|Unbounded growth **exhausts native memory** → OOM or OS instability|
|"Static variables live in Metaspace"|Static variable **references** in Metaspace; **values/objects** on heap|
|"Metaspace GC'd with heap GC"|Triggered separately when Metaspace threshold hit|

---

### 🔥 Pitfalls in Production

**1. No MaxMetaspaceSize cap in production**

bash

```bash
# Symptom: container memory grows steadily
# OS kills process (OOMKilled in Kubernetes)
# but heap looks fine in JVM metrics

# Why: Metaspace is native memory
# Container memory limit = heap + Metaspace + threads + CodeCache + ...
# -Xmx only controls heap

# Fix: account for ALL JVM memory
# Container limit = Xmx + ~200-400MB (Metaspace + overhead)
java -Xmx512m \
     -XX:MaxMetaspaceSize=128m \
     -XX:ReservedCodeCacheSize=128m \
     -jar myapp.jar
# Total native ≈ 512 + 128 + 128 + ~100 overhead ≈ ~870MB
# Set container limit to ~1GB
```

**2. Hibernate + dynamic proxy Metaspace leak**

```
Hibernate generates proxy classes for lazy-loaded entities
Spring generates CGLIB proxies for @Transactional beans

Each proxy = new class = Metaspace entry

In correctly written apps: proxies generated once at startup → fine
In leaking apps:
  • Creating new SessionFactory per request → new proxies each time
  • Dynamic class generation in loops
  → Metaspace grows unbounded

Diagnostic:
jmap -clstats <pid> | grep -i "hibernate\|cglib\|proxy"
→ if count grows over time → leak confirmed
```

**3. Kubernetes OOMKilled with "healthy" heap**

```
# Common prod scenario:
# App reports heap usage: 400MB / 512MB max → looks fine
# Kubernetes kills pod: OOMKilled
# Engineers confused: "heap is fine!"

# Reality: container sees ALL memory
# Heap:       400MB
# Metaspace:  200MB (uncapped, grew with class loading)
# CodeCache:  100MB
# Threads:    50MB  (500 threads × ~100KB stack)
# Other:      50MB
# Total:      800MB → exceeds 768MB container limit → killed

# Fix: set explicit limits on ALL regions
java -Xmx400m \
     -XX:MaxMetaspaceSize=100m \
     -XX:ReservedCodeCacheSize=64m \
     -Xss256k \               # smaller stack per thread
     -jar myapp.jar
```

---

### 🔗 Related Keywords

- `PermGen` — predecessor to Metaspace (Java ≤ 7)
- `Class Loader` — its lifecycle directly controls Metaspace reclamation
- `Heap Memory` — where objects live (contrast to Metaspace)
- `OutOfMemoryError: Metaspace` — Metaspace exhausted
- `CGLIB` — generates classes at runtime → adds to Metaspace
- `Hibernate Proxy` — dynamic class generation → Metaspace consumer
- `jcmd VM.metaspace` — live Metaspace inspection tool
- `Code Cache` — also off-heap; stores JIT-compiled native code
- `Full GC` — can trigger Metaspace collection
- `Hot Redeploy` — primary cause of Metaspace leaks in app servers

---

### 📌 Quick Reference Card

---

**Entry 008 complete.**

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot app running in Kubernetes gets OOMKilled every 48 hours. Heap metrics look normal. Metaspace is uncapped. Walk me through your diagnosis and the exact JVM flags you'd set to stabilize it.

**Q2.** Spring generates CGLIB proxies for every `@Transactional` and `@Cacheable` bean at startup. These are new classes loaded into Metaspace. Why don't they cause a Metaspace leak — but creating a new `AnnotationConfigApplicationContext` in a loop does?
