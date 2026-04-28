---
layout: default
title: "JDK (Java Development Kit)"
parent: "Java Fundamentals"
nav_order: 3
permalink: /docs/java/jdk/
---
# â˜• JDK (Java Development Kit)

ðŸ·ï¸ Tags â€” #java #jvm #internals #foundational

âš¡ TL;DR â€” The complete Java toolkit: compile, run, debug, and diagnose.

---
#### ðŸ“˜ Textbook Definition

The JDK is a full-featured software development kit for building Java applications. It is a superset of the JRE â€” containing the JVM, standard library, and additionally: the Java compiler (`javac`), debugger (`jdb`), profiler, documentation generator (`javadoc`), and other development tools.

---

#### ðŸŸ¢ Simple Definition (Easy)

The JDK is **everything you need to write, compile, debug, and run Java programs**. It's the complete developer toolkit.

---

#### ðŸ”µ Simple Definition (Elaborated)

The JDK is what you install on your development machine. It contains the JRE (to run programs) plus the tools to build them â€” most importantly `javac` to compile `.java` â†’ `.class`. Without the JDK, you can run Java programs but you can't create them.

---

#### ðŸ”© First Principles Explanation

**The problem:**

Running Java needs JRE. But building Java needs more:

- A compiler to turn source â†’ bytecode
- A debugger to inspect running programs
- A profiler to find performance bottlenecks
- A doc generator for API documentation
- Tools to inspect `.class` files, manage keystores, etc.

**The solution:**

Bundle all of that together â†’ JDK.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  JDK                    â”‚
â”‚                                         â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚   â”‚             JRE                 â”‚   â”‚
â”‚   â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚   â”‚
â”‚   â”‚   â”‚          JVM            â”‚   â”‚   â”‚
â”‚   â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚   â”‚
â”‚   â”‚   + Standard Library            â”‚   â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                                         â”‚
â”‚   + javac    (compiler)                 â”‚
â”‚   + jdb      (debugger)                 â”‚
â”‚   + javadoc  (doc generator)            â”‚
â”‚   + jar      (archive tool)             â”‚
â”‚   + jshell   (REPL)                     â”‚
â”‚   + jmap     (heap dump)                â”‚
â”‚   + jstack   (thread dump)              â”‚
â”‚   + jconsole (visual monitor)           â”‚
â”‚   + jlink    (custom runtime builder)   â”‚
â”‚   + jpackage (native installer)         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ§  Mental Model / Analogy

> JVM = engine. JRE = engine + car body (can drive). JDK = engine + car body + full mechanic's workshop (can drive AND build/fix cars).

---

#### âš™ï¸ Key JDK Tools â€” What They Actually Do

|Tool|Purpose|When You Use It|
|---|---|---|
|`javac`|Compiles `.java` â†’ `.class`|Every build|
|`java`|Launches JVM, runs bytecode|Every run|
|`jar`|Packages `.class` files into `.jar`|Packaging|
|`jshell`|REPL â€” run Java snippets interactively|Quick experiments|
|`jdb`|Command-line debugger|Low-level debugging|
|`javadoc`|Generates HTML API docs from comments|Documentation|
|`jmap`|Dumps heap snapshot|Memory leak analysis|
|`jstack`|Dumps all thread states|Deadlock/hang diagnosis|
|`jstat`|Live GC and class loading stats|GC monitoring|
|`jcmd`|Swiss-army knife â€” many diagnostics in one|Production diagnosis|
|`jlink`|Builds custom minimal runtime|Lean Docker images|
|`jpackage`|Creates native installers (.exe, .dmg)|Desktop distribution|
|`javap`|Disassembles `.class` â†’ bytecode|Understanding internals|

---

#### ðŸ’» Code Example â€” JDK Tools in Action

**Compile and run:**

bash

```bash
# JDK only step â€” needs javac
javac HelloWorld.java        # produces HelloWorld.class

# JRE step â€” just java
java HelloWorld              # runs the bytecode
```

**Inspect bytecode with `javap`:**

java

```java
// Source
public class Add {
    public int add(int a, int b) {
        return a + b;
    }
}
```

bash

```bash
javap -c Add.class
```

```
# Output â€” actual JVM bytecode instructions:
public int add(int, int);
  Code:
     0: iload_1        # push local var 1 (a) onto operand stack
     1: iload_2        # push local var 2 (b) onto operand stack
     2: iadd           # pop two ints, add, push result
     3: ireturn        # return int from top of stack
```

> This is what the JVM actually executes. `javap` makes it visible.

**Thread dump with `jstack` (production gold):**

bash

```bash
# Find Java process ID
jps -l

# Dump all threads â€” reveals deadlocks, blocked threads
jstack <pid> > thread-dump.txt

# Output shows:
# "http-nio-8080-exec-1" - BLOCKED on lock <0x...>
#   waiting for "http-nio-8080-exec-3" which holds it
# â† deadlock detected
```

**Heap dump with `jmap`:**

bash

```bash
jmap -dump:format=b,file=heap.hprof <pid>
# Open in Eclipse MAT or VisualVM to find memory leaks
```

**JShell â€” REPL for quick experiments:**

bash

```bash
$ jshell
|  Welcome to JShell

jshell> var list = List.of(1, 2, 3)
list ==> [1, 2, 3]

jshell> list.stream().mapToInt(x -> x).sum()
$2 ==> 6
```

---

#### ðŸ” JDK in the Full Development Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                DEVELOPMENT LIFECYCLE                 â”‚
â”‚                                                      â”‚
â”‚  Write Code (.java)                                  â”‚
â”‚       â†“                                              â”‚
â”‚  javac â†’ .class files        [JDK: compiler]         â”‚
â”‚       â†“                                              â”‚
â”‚  jar â†’ .jar / .war           [JDK: packager]         â”‚
â”‚       â†“                                              â”‚
â”‚  Unit Tests (JUnit)          [JDK: runs tests]       â”‚
â”‚       â†“                                              â”‚
â”‚  javadoc â†’ HTML docs         [JDK: doc gen]          â”‚
â”‚       â†“                                              â”‚
â”‚  Deploy to server            [JRE sufficient]        â”‚
â”‚       â†“                                              â”‚
â”‚  Production issue?                                   â”‚
â”‚    jstack / jmap / jcmd      [JDK tools diagnose]    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš™ï¸ JDK Distributions â€” This Matters in Production

The JDK is a **specification** (OpenJDK). Multiple vendors ship it:

|Distribution|Vendor|Notes|
|---|---|---|
|Oracle JDK|Oracle|Commercial license for prod (Java 17+: free again)|
|OpenJDK|Oracle/Community|Open source reference impl|
|Eclipse Temurin|Adoptium|Most popular free production choice|
|Amazon Corretto|AWS|Free, AWS-optimized, LTS support|
|GraalVM|Oracle|JIT + AOT + polyglot (Python, JS in JVM)|
|Microsoft OpenJDK|Microsoft|Azure-optimized|
|Azul Zulu|Azul|Commercial support options|

> **Production recommendation:** Eclipse Temurin (Adoptium) or Amazon Corretto for most teams. GraalVM if you need native image compilation.

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"JDK and JRE are different products"|JDK contains JRE â€” it's a superset|
|"Only Oracle makes the JDK"|OpenJDK spec â†’ many vendors distribute it|
|"JDK version = Java version"|Yes â€” JDK 21 = Java 21|
|"I only need JDK on dev machines"|Production diagnostics (jstack, jmap) need JDK tools too|
|"All JDK distributions are identical"|Same spec, but GC tuning, performance, support differ|

---

#### ðŸ”¥ Pitfalls in Production

**1. Using JRE-only image and losing diagnostic tools**

bash

```bash
# You hit OutOfMemoryError in prod
# Try to run jmap â†’ command not found (JRE-only image)

# Fix: use JDK image in prod too, or ship jcmd/jmap explicitly
# OR: use jcmd which is often included in slim JDK images
jcmd <pid> VM.native_memory   # memory breakdown
jcmd <pid> GC.heap_info       # heap state
jcmd <pid> Thread.print       # thread dump (like jstack)
```

**2. LTS version confusion**

```
Java 8  â†’ LTS (still widely used, EOL approaching)
Java 11 â†’ LTS
Java 17 â†’ LTS â† current safe minimum for new projects
Java 21 â†’ LTS â† recommended (Virtual Threads, Pattern Matching)
Java 25 â†’ LTS (upcoming)

Non-LTS versions (9, 10, 12-16, 18-20) â†’ 6-month support only
Never use non-LTS in production
```

**3. Licensing trap**

```
Oracle JDK 8/11 in production without license = legal risk
Fix: switch to Eclipse Temurin or Amazon Corretto (free, production-grade)
```

---

#### ðŸ”— Related Keywords

- `JRE` â€” subset of JDK; runtime only
- `JVM` â€” the execution engine inside both
- `javac` â€” the compiler tool in JDK
- `javap` â€” bytecode disassembler (understand JVM internals)
- `jstack / jmap / jcmd` â€” production diagnostic tools
- `GraalVM` â€” advanced JDK with AOT compilation
- `jlink` â€” JDK tool to build minimal runtimes
- `OpenJDK` â€” the open-source specification JDK is built from

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Complete Java toolchain: compile, run,    â”‚
â”‚              â”‚ debug, profile, package                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Developing Java; diagnosing production    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Pure runtime containers (use slim JRE or  â”‚
â”‚              â”‚ jlink-built custom runtime)               â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "JDK = JRE + the tools to build and       â”‚
â”‚              â”‚  diagnose Java systems"                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Bytecode â†’ javap â†’ Class Loader â†’         â”‚
â”‚              â”‚ JIT Compiler â†’ GraalVM Native Image       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

### ðŸ§© JVM / JRE / JDK â€” The Complete Picture Together

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                      JDK                           â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚                   JRE                        â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚  â”‚
â”‚  â”‚  â”‚                JVM                      â”‚ â”‚  â”‚
â”‚  â”‚  â”‚  ClassLoader + Runtime Areas +          â”‚ â”‚  â”‚
â”‚  â”‚  â”‚  Execution Engine + GC                  â”‚ â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚  â”‚
â”‚  â”‚  + Java Standard Library (java.base, etc.)   â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚  + javac, jar, jshell, jdb, javadoc                â”‚
â”‚  + jstack, jmap, jstat, jcmd, jconsole             â”‚
â”‚  + jlink, jpackage, javap                          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

WHO NEEDS WHAT:
  End user running your app  â†’  JRE (or custom jlink runtime)
  Developer building Java    â†’  JDK
  Production server          â†’  JDK recommended (for diagnostics)
  Docker container           â†’  jlink minimal runtime (leanest)
```

---
