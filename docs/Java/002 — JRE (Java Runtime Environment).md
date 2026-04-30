---
layout: default
title: "JRE (Java Runtime Environment)"
parent: "Java & JVM Internals"
nav_order: 2
permalink: /java/jre-java-runtime-environment/
---
# 002 — JRE (Java Runtime Environment)

`#java` `#jvm` `#internals` `#foundational`

⚡ TL;DR — JVM + standard library = everything needed to run a Java program.

| #002 | Category: Java & JVM Internals | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | JVM | |
| **Used by:** | JDK, Application Deployment | |

---

### 📘 Textbook Definition

The JRE is a software package that provides the minimum environment required to **run** a compiled Java application. It consists of the JVM, the Java Class Library (standard library), and supporting files — but does **not** include development tools like the compiler.

---

### 🟢 Simple Definition (Easy)

The JRE is **everything you need to run a Java program** — but not to write or compile one. It's the "player" without the "studio."

---

### 🔵 Simple Definition (Elaborated)

When someone just wants to **run** your `.jar` file — not develop Java — they need the JRE. It bundles the JVM (the engine) with the standard Java libraries (`java.lang`, `java.util`, `java.io`, etc.) that your program depends on at runtime. Without it, the JVM wouldn't know what `ArrayList` or `String` is.

---

### 🔩 First Principles Explanation

**The problem:**

Your compiled bytecode calls `java.util.ArrayList`. Where does that class come from? It's not in your `.jar`. It needs to be provided by the runtime environment.

**The solution:**

Package the JVM + all standard library classes together → that bundle is the JRE.

```
Your App (.jar)
     ↓ needs
┌─────────────────────────────┐
│           JRE               │
│  ┌───────┐  ┌────────────┐  │
│  │  JVM  │  │  Java Std  │  │
│  │       │  │  Library   │  │
│  │       │  │(rt.jar /   │  │
│  └───────┘  │ modules)   │  │
│             └────────────┘  │
└─────────────────────────────┘
     ↓ runs on
  OS + Hardware
```

The JRE is the **complete runtime contract** — JVM executes, standard library provides the building blocks.

---

### 🧠 Mental Model / Analogy

> Think of your Java app as a **movie file**. The JRE is the **media player + codec pack**. The player (JVM) runs the file, the codecs (standard library) decode the content. Without both, nothing plays.

You don't need a video editing suite (JDK) just to watch a movie.

---

### ⚙️ What's Inside the JRE

```
JRE/
├── bin/
│   └── java              ← the executable that launches JVM
│
├── lib/
│   ├── rt.jar            ← (pre Java 9) all standard classes
│   │                        (post Java 9: replaced by modules)
│   ├── jvm.cfg           ← JVM configuration
│   ├── security/         ← security policies, CA certs
│   └── ext/              ← extension classloader directory
│
└── jvm/ (or lib/server/)
    └── libjvm.so         ← the actual JVM shared library (OS-specific)
```

**Post Java 9 — Module System (JPMS):**

`rt.jar` was split into ~70 modules (`java.base`, `java.sql`, `java.xml`, etc.)

```
java.base      ← String, Object, Collections, IO
java.sql       ← JDBC
java.xml       ← XML parsing
java.logging   ← java.util.logging
...
```

This allows **custom minimal JREs** via `jlink` — ship only what you use.

---

### 🔁 Where JRE Fits in the Execution Flow

```
Developer Machine                 User / Server
─────────────────                 ──────────────
  .java source
      ↓ javac (JDK)
  .class bytecode
      ↓ packaged
  .jar / .war file   ──────────→  Needs only JRE to run
                                       ↓
                                  JRE = JVM + Std Lib
                                       ↓
                                  Program executes
```

---

### 💻 Code Example — What JRE Provides at Runtime

java

```java
// Every single import below is part of the JRE standard library
// Your code uses them — JRE provides them at runtime

import java.util.ArrayList;     // java.base module
import java.util.Collections;   // java.base module
import java.io.FileReader;      // java.base module
import java.sql.Connection;     // java.sql module
import java.net.HttpURLConnection; // java.net module

public class JREDemo {
    public static void main(String[] args) {
        // This works because JRE ships ArrayList's bytecode
        // alongside your app's bytecode
        var list = new ArrayList<String>();
        list.add("JRE provides this class");
        System.out.println(list);
    }
}
```

bash

```bash
# On a machine with ONLY JRE (no JDK):
java -jar myapp.jar     # ✅ works
javac MyApp.java        # ❌ javac not available — needs JDK
```

---

This is a **critical modern reality:**

> From Java 9 onward, Oracle stopped shipping a standalone JRE. You use the JDK directly, or build a custom runtime image with `jlink`.

bash

```bash
# Build a minimal custom JRE with only what your app needs
jlink \
  --module-path $JAVA_HOME/jmods \
  --add-modules java.base,java.sql,java.net.http \
  --output my-custom-jre \
  --compress 2

# Result: a minimal runtime image — often 30-50MB vs 200MB+ full JDK
```

This is how **Docker images** for Java apps are kept lean.

---

### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"JRE includes the compiler"|No — compiler (`javac`) is JDK only|
|"JRE and JVM are the same"|JVM is inside JRE; JRE = JVM + standard library|
|"You always need full JRE"|Java 9+ lets you build minimal runtimes via `jlink`|
|"JRE is still separately distributed"|Not since Java 9 — JDK is the distribution unit now|

---

### 🔥 Pitfalls in Production

**1. Shipping fat Docker images**

dockerfile

```dockerfile
# Bad: using full JDK in production image
FROM openjdk:21-jdk        # ~400MB — has compiler, debugger, etc.

# Good: use JRE-equivalent slim image
FROM openjdk:21-jre-slim   # ~200MB

# Best: use jlink to build minimal runtime
FROM eclipse-temurin:21-jdk AS builder
RUN jlink --add-modules java.base,java.sql \
          --output /custom-jre

FROM debian:slim
COPY --from=builder /custom-jre /opt/jre
ENTRYPOINT ["/opt/jre/bin/java", "-jar", "/app.jar"]
# Result: ~80-100MB image
```

**2. Version mismatch**

bash

```bash
# Compiled with JDK 21, but JRE 11 on server
# Error at runtime:
# UnsupportedClassVersionError: major version 65 (Java 21)
#   vs supported 55 (Java 11)

# Always match: compile target = runtime version
javac --release 11 MyApp.java   # compile for Java 11 compatibility
```

---

### 🔗 Related Keywords

- `JVM` — the execution engine inside JRE
- `JDK` — superset of JRE; adds compiler + dev tools
- `Class Loader` — the JRE component that loads class files
- `java.base` module — the core of the standard library
- `jlink` — tool to build custom minimal JREs
- `Bytecode` — what the JRE's JVM executes
- `Module System (JPMS)` — replaced `rt.jar` in Java 9+

---

### 📌 Quick Reference Card

---
