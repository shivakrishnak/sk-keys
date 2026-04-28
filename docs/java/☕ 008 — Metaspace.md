---
layout: default
title: "Metaspace"
parent: "Java Fundamentals"
nav_order: 8
permalink: /java/metaspace/
---
ðŸ·ï¸ Tags â€” #java #jvm #memory #internals #classloading #intermediate

âš¡ TL;DR â€” Off-heap native memory region that stores class metadata, replacing PermGen in Java 8 â€” grows dynamically and lives outside GC-managed heap. 

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #008  â”‚ Category: JVM Memory     â”‚ Difficulty: â˜…â˜…â˜†   â”‚
â”‚ Depends on: JVM, Class Loader,   â”‚ Used by: Every    â”‚
â”‚ Heap Memory                      â”‚ loaded class,     â”‚
â”‚                                  â”‚ Spring, Hibernate â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

Metaspace is a **native memory region** (off-heap) introduced in Java 8 to replace PermGen. It stores **class metadata** â€” the structural descriptions of loaded classes including method bytecode, field definitions, constant pools, and annotations. Unlike PermGen, Metaspace is not bounded by heap limits and grows dynamically into native OS memory â€” but must be explicitly capped to prevent unbounded growth.

---

#### ðŸŸ¢ Simple Definition (Easy)

Metaspace is where the JVM stores **the blueprints of your classes** â€” not your objects (that's heap), but the class definitions themselves. It lives outside the heap in native memory.

---

#### ðŸ”µ Simple Definition (Elaborated)

Every class the JVM loads needs to store its structure somewhere â€” method signatures, bytecode, field types, constant pools. That storage is Metaspace. It's separate from the heap because class metadata has a completely different lifecycle from objects â€” it lives as long as its ClassLoader is alive. By moving it off-heap into native memory, Java 8 removed the infamous `OutOfMemoryError: PermGen space` and let Metaspace grow as needed â€” which sounds great until it grows without bound and exhausts native memory instead.

---

#### ðŸ”© First Principles Explanation

**The PermGen problem (pre Java 8):**

Before Java 8, class metadata lived in **PermGen** â€” a fixed-size heap region:

bash

```bash
java -XX:MaxPermSize=256m MyApp  # had to guess the right size
```

Two failure modes:

```
Too small â†’ OutOfMemoryError: PermGen space
            (common in apps with lots of classes or hot redeploy)

Too large â†’ wasted heap space reserved but unused
```

PermGen was also collected by Full GC â€” meaning class metadata cleanup was tied to the most expensive GC operation.

**The deeper problem:**

Class metadata lifetime â‰  object lifetime.

```
Object lifetime:   created â†’ used â†’ unreachable â†’ GC collects
Class lifetime:    loaded â†’ used until ClassLoader dies â†’ then collected
```

Mixing them in the same memory region (heap) was conceptually wrong.

**The Java 8 solution â€” Metaspace:**

> "Move class metadata to native memory. Let it grow dynamically. Collect it when its ClassLoader is GC'd â€” not on every Full GC."

```
Before Java 8:                After Java 8:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚     Heap     â”‚              â”‚     Heap     â”‚  â”‚  Metaspace  â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚              â”‚              â”‚  â”‚  (native)   â”‚
â”‚  â”‚PermGen â”‚  â”‚              â”‚  Objects     â”‚  â”‚  Classes    â”‚
â”‚  â”‚Classes â”‚  â”‚              â”‚  Arrays      â”‚  â”‚  Methods    â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚              â”‚              â”‚  â”‚  Constants  â”‚
â”‚  Objects     â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â”‚  Arrays      â”‚              bounded by -Xmx   grows into OS
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                                memory
bounded by -Xmx
+ MaxPermSize
```

---

#### ðŸ§  Mental Model / Analogy

> Think of a city (JVM) with two kinds of storage:
> 
> **Heap** = apartment buildings where residents (objects) live. Buildings have a fixed total capacity (`-Xmx`).
> 
> **Metaspace** = the city's **architectural office** â€” stores blueprints (class definitions) for every building type. The office is outside the residential zone (off-heap), in its own district (native memory). It expands by renting more office space from the OS as needed.
> 
> When a building type is no longer used (ClassLoader unloaded) â€” the blueprints are archived and the office space reclaimed.

---

#### âš™ï¸ What Lives in Metaspace

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                     METASPACE                           â”‚
â”‚                                                         â”‚
â”‚  Per-class metadata:                                    â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
â”‚  â”‚  Class structure (klass)                        â”‚    â”‚
â”‚  â”‚  â€¢ Field names, types, offsets                  â”‚    â”‚
â”‚  â”‚  â€¢ Method signatures                            â”‚    â”‚
â”‚  â”‚  â€¢ Method bytecode                              â”‚    â”‚
â”‚  â”‚  â€¢ Constant pool (string literals, refs)        â”‚    â”‚
â”‚  â”‚  â€¢ Access flags (public/private/final)          â”‚    â”‚
â”‚  â”‚  â€¢ Annotations                                  â”‚    â”‚
â”‚  â”‚  â€¢ Interface list                               â”‚    â”‚
â”‚  â”‚  â€¢ vtable (virtual method dispatch table)       â”‚    â”‚
â”‚  â”‚  â€¢ itable (interface method dispatch table)     â”‚    â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
â”‚                                                         â”‚
â”‚  Runtime data:                                          â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
â”‚  â”‚  â€¢ JIT compiled code cache (Code Cache)         â”‚    â”‚
â”‚  â”‚    (technically separate but also off-heap)     â”‚    â”‚
â”‚  â”‚  â€¢ Interned strings (String Pool)               â”‚    â”‚
â”‚  â”‚    (moved to heap in Java 7+)                   â”‚    â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
â”‚                                                         â”‚
â”‚  NOT in Metaspace:                                      â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”‚
â”‚  â”‚  âœ— Object instances â†’ Heap                      â”‚    â”‚
â”‚  â”‚  âœ— Static variable values â†’ Heap (Java 8+)      â”‚    â”‚
â”‚  â”‚  âœ— String literal values â†’ Heap String Pool     â”‚    â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

> **Critical nuance:** Static variable **references** are stored in the class metadata in Metaspace, but the **objects they point to** live on the heap. This is a common exam and interview confusion point.

---

#### âš™ï¸ Metaspace Lifecycle â€” Tied to ClassLoader

```
ClassLoader created
      â†“
Classes loaded â†’ metadata allocated in Metaspace
      â†“
Classes used (methods called, objects created)
      â†“
ClassLoader becomes unreachable
(no more references to it or its classes)
      â†“
Next GC cycle detects unreachable ClassLoader
      â†“
ALL metadata for ALL classes loaded by that
ClassLoader freed from Metaspace
      â†“
Metaspace space reclaimed
```

**This is why hot redeploy leaks Metaspace:**

```
Deploy v1 â†’ ClassLoader1 loads 500 classes â†’ 50MB Metaspace
Redeploy â†’ ClassLoader2 loads 500 classes â†’ +50MB Metaspace
           ClassLoader1 should be freed...
           BUT if any reference to ClassLoader1's classes
           survives (static field, thread local, cache) â†’
           ClassLoader1 NOT GC'd â†’ 50MB STUCK in Metaspace

Redeploy again and again â†’ Metaspace grows â†’ OOM: Metaspace
```

---

#### ðŸ”„ How It Connects

```
javac â†’ Bytecode (.class)
             â†“
        Class Loader reads bytecode
             â†“
   [Metaspace] â† class structure stored here
             â†“
        JVM creates Class object â†’ [Heap]
             â†“
   new MyObject() â†’ instance â†’ [Heap]
        uses class structure from [Metaspace]
             â†“
   ClassLoader unreachable â†’ Metaspace entry freed
```

---

#### ðŸ’» Code Example

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
// â† "unlimited" is dangerous in production
```

**Simulating Metaspace exhaustion â€” class generation:**

java

```java
import net.bytebuddy.ByteBuddy; // or use ASM directly

public class MetaspaceExhaust {
    public static void main(String[] args) throws Exception {
        // Generate and load unique classes in a loop
        // Each class adds metadata to Metaspace
        // ClassLoader kept alive â†’ no Metaspace reclaim

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
                classes.add(c); // hold ref â†’ ClassLoader stays alive
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

# Class histogram â€” what's taking space
jcmd <pid> GC.class_histogram | head -30

# Class loader stats
jmap -clstats <pid>
# Shows each ClassLoader, how many classes it loaded,
# and memory consumed â†’ identify leaking loaders
```

**Setting Metaspace limits â€” production config:**

bash

```bash
# No cap (dangerous â€” can exhaust native memory):
java -jar myapp.jar

# Capped (recommended):
java -XX:MaxMetaspaceSize=256m -jar myapp.jar

# Also tune initial size to avoid early resizing:
java -XX:MetaspaceSize=128m \
     -XX:MaxMetaspaceSize=256m \
     -jar myapp.jar

# MetaspaceSize = initial committed size (not max)
# When Metaspace hits MetaspaceSize â†’ GC triggered
# Set high enough to avoid early GC thrashing
```

---

#### âš™ï¸ PermGen vs Metaspace â€” Side by Side

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Aspect             â”‚ PermGen (â‰¤Java 7)  â”‚ Metaspace (Java 8+)â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Location           â”‚ On heap            â”‚ Native memory      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Size               â”‚ Fixed              â”‚ Dynamic            â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Default max        â”‚ 64MB-82MB          â”‚ Unlimited          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ GC trigger         â”‚ Full GC            â”‚ When threshold hit â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ OOM message        â”‚ PermGen space      â”‚ Metaspace          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Tuning flag        â”‚ -XX:MaxPermSize    â”‚ -XX:MaxMetaspace   â”‚
â”‚                    â”‚                   â”‚       Size         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ String pool        â”‚ Stored here        â”‚ Moved to heap      â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Static variables   â”‚ Stored here        â”‚ Values on heap     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"Metaspace is part of heap"|It's **native memory** â€” outside heap, not bounded by `-Xmx`|
|"Metaspace stores objects"|It stores **class structures** â€” objects always live on heap|
|"Metaspace replaced PermGen entirely"|PermGen stored static vars + String pool too â€” those moved to **heap**|
|"Metaspace grows freely = no problem"|Unbounded growth **exhausts native memory** â†’ OOM or OS instability|
|"Static variables live in Metaspace"|Static variable **references** in Metaspace; **values/objects** on heap|
|"Metaspace GC'd with heap GC"|Triggered separately when Metaspace threshold hit|

---

#### ðŸ”¥ Pitfalls in Production

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
# Total native â‰ˆ 512 + 128 + 128 + ~100 overhead â‰ˆ ~870MB
# Set container limit to ~1GB
```

**2. Hibernate + dynamic proxy Metaspace leak**

```
Hibernate generates proxy classes for lazy-loaded entities
Spring generates CGLIB proxies for @Transactional beans

Each proxy = new class = Metaspace entry

In correctly written apps: proxies generated once at startup â†’ fine
In leaking apps:
  â€¢ Creating new SessionFactory per request â†’ new proxies each time
  â€¢ Dynamic class generation in loops
  â†’ Metaspace grows unbounded

Diagnostic:
jmap -clstats <pid> | grep -i "hibernate\|cglib\|proxy"
â†’ if count grows over time â†’ leak confirmed
```

**3. Kubernetes OOMKilled with "healthy" heap**

```
# Common prod scenario:
# App reports heap usage: 400MB / 512MB max â†’ looks fine
# Kubernetes kills pod: OOMKilled
# Engineers confused: "heap is fine!"

# Reality: container sees ALL memory
# Heap:       400MB
# Metaspace:  200MB (uncapped, grew with class loading)
# CodeCache:  100MB
# Threads:    50MB  (500 threads Ã— ~100KB stack)
# Other:      50MB
# Total:      800MB â†’ exceeds 768MB container limit â†’ killed

# Fix: set explicit limits on ALL regions
java -Xmx400m \
     -XX:MaxMetaspaceSize=100m \
     -XX:ReservedCodeCacheSize=64m \
     -Xss256k \               # smaller stack per thread
     -jar myapp.jar
```

---

#### ðŸ”— Related Keywords

- `PermGen` â€” predecessor to Metaspace (Java â‰¤ 7)
- `Class Loader` â€” its lifecycle directly controls Metaspace reclamation
- `Heap Memory` â€” where objects live (contrast to Metaspace)
- `OutOfMemoryError: Metaspace` â€” Metaspace exhausted
- `CGLIB` â€” generates classes at runtime â†’ adds to Metaspace
- `Hibernate Proxy` â€” dynamic class generation â†’ Metaspace consumer
- `jcmd VM.metaspace` â€” live Metaspace inspection tool
- `Code Cache` â€” also off-heap; stores JIT-compiled native code
- `Full GC` â€” can trigger Metaspace collection
- `Hot Redeploy` â€” primary cause of Metaspace leaks in app servers

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Off-heap native memory for class          â”‚
â”‚              â”‚ metadata â€” lives and dies with its        â”‚
â”‚              â”‚ ClassLoader                               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Always present â€” every loaded class uses  â”‚
â”‚              â”‚ it; tune it for dynamic class-heavy apps  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Never leave MaxMetaspaceSize uncapped     â”‚
â”‚              â”‚ in production â€” native memory exhaustion  â”‚
â”‚              â”‚ is worse than heap OOM                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Metaspace = class blueprint storage,     â”‚
â”‚              â”‚  off-heap, grows until you stop it"       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ PermGen â†’ Code Cache â†’ Class Loader GC â†’  â”‚
â”‚              â”‚ CGLIB â†’ Hibernate Proxy â†’ jcmd            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

**Entry 008 complete.**

#### ðŸ§  Think About This Before We Continue

**Q1.** A Spring Boot app running in Kubernetes gets OOMKilled every 48 hours. Heap metrics look normal. Metaspace is uncapped. Walk me through your diagnosis and the exact JVM flags you'd set to stabilize it.

**Q2.** Spring generates CGLIB proxies for every `@Transactional` and `@Cacheable` bean at startup. These are new classes loaded into Metaspace. Why don't they cause a Metaspace leak â€” but creating a new `AnnotationConfigApplicationContext` in a loop does?
