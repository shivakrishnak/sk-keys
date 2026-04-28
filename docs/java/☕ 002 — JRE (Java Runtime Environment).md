---
layout: default
title: "JRE (Java Runtime Environment)"
parent: "Java Fundamentals"
nav_order: 2
permalink: /java/jre-java-runtime-environment/
---
ðŸ·ï¸ Tags â€” #java #jvm #internals #foundational 

âš¡ TL;DR â€” JVM + standard library = everything needed to run a Java program.

---
#### ðŸ“˜ Textbook Definition

The JRE is a software package that provides the minimum environment required to **run** a compiled Java application. It consists of the JVM, the Java Class Library (standard library), and supporting files â€” but does **not** include development tools like the compiler.

---

#### ðŸŸ¢ Simple Definition (Easy)

The JRE is **everything you need to run a Java program** â€” but not to write or compile one. It's the "player" without the "studio."

---

#### ðŸ”µ Simple Definition (Elaborated)

When someone just wants to **run** your `.jar` file â€” not develop Java â€” they need the JRE. It bundles the JVM (the engine) with the standard Java libraries (`java.lang`, `java.util`, `java.io`, etc.) that your program depends on at runtime. Without it, the JVM wouldn't know what `ArrayList` or `String` is.

---

#### ðŸ”© First Principles Explanation

**The problem:**

Your compiled bytecode calls `java.util.ArrayList`. Where does that class come from? It's not in your `.jar`. It needs to be provided by the runtime environment.

**The solution:**

Package the JVM + all standard library classes together â†’ that bundle is the JRE.

```
Your App (.jar)
     â†“ needs
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚           JRE               â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  JVM  â”‚  â”‚  Java Std  â”‚  â”‚
â”‚  â”‚       â”‚  â”‚  Library   â”‚  â”‚
â”‚  â”‚       â”‚  â”‚(rt.jar /   â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚ modules)   â”‚  â”‚
â”‚             â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
     â†“ runs on
  OS + Hardware
```

The JRE is the **complete runtime contract** â€” JVM executes, standard library provides the building blocks.

---

#### ðŸ§  Mental Model / Analogy

> Think of your Java app as a **movie file**. The JRE is the **media player + codec pack**. The player (JVM) runs the file, the codecs (standard library) decode the content. Without both, nothing plays.

You don't need a video editing suite (JDK) just to watch a movie.

---

#### âš™ï¸ What's Inside the JRE

```
JRE/
â”œâ”€â”€ bin/
â”‚   â””â”€â”€ java              â† the executable that launches JVM
â”‚
â”œâ”€â”€ lib/
â”‚   â”œâ”€â”€ rt.jar            â† (pre Java 9) all standard classes
â”‚   â”‚                        (post Java 9: replaced by modules)
â”‚   â”œâ”€â”€ jvm.cfg           â† JVM configuration
â”‚   â”œâ”€â”€ security/         â† security policies, CA certs
â”‚   â””â”€â”€ ext/              â† extension classloader directory
â”‚
â””â”€â”€ jvm/ (or lib/server/)
    â””â”€â”€ libjvm.so         â† the actual JVM shared library (OS-specific)
```

**Post Java 9 â€” Module System (JPMS):**

`rt.jar` was split into ~70 modules (`java.base`, `java.sql`, `java.xml`, etc.)

```
java.base      â† String, Object, Collections, IO
java.sql       â† JDBC
java.xml       â† XML parsing
java.logging   â† java.util.logging
...
```

This allows **custom minimal JREs** via `jlink` â€” ship only what you use.

---

#### ðŸ” Where JRE Fits in the Execution Flow

```
Developer Machine                 User / Server
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€                 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  .java source
      â†“ javac (JDK)
  .class bytecode
      â†“ packaged
  .jar / .war file   â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’  Needs only JRE to run
                                       â†“
                                  JRE = JVM + Std Lib
                                       â†“
                                  Program executes
```

---

#### ðŸ’» Code Example â€” What JRE Provides at Runtime

java

```java
// Every single import below is part of the JRE standard library
// Your code uses them â€” JRE provides them at runtime

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
java -jar myapp.jar     # âœ… works
javac MyApp.java        # âŒ javac not available â€” needs JDK
```

---

#### ðŸ’¡ Java 9+ : JRE Is No Longer Distributed Separately

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

# Result: a minimal runtime image â€” often 30-50MB vs 200MB+ full JDK
```

This is how **Docker images** for Java apps are kept lean.

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"JRE includes the compiler"|No â€” compiler (`javac`) is JDK only|
|"JRE and JVM are the same"|JVM is inside JRE; JRE = JVM + standard library|
|"You always need full JRE"|Java 9+ lets you build minimal runtimes via `jlink`|
|"JRE is still separately distributed"|Not since Java 9 â€” JDK is the distribution unit now|

---

#### ðŸ”¥ Pitfalls in Production

**1. Shipping fat Docker images**

dockerfile

```dockerfile
# Bad: using full JDK in production image
FROM openjdk:21-jdk        # ~400MB â€” has compiler, debugger, etc.

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

#### ðŸ”— Related Keywords

- `JVM` â€” the execution engine inside JRE
- `JDK` â€” superset of JRE; adds compiler + dev tools
- `Class Loader` â€” the JRE component that loads class files
- `java.base` module â€” the core of the standard library
- `jlink` â€” tool to build custom minimal JREs
- `Bytecode` â€” what the JRE's JVM executes
- `Module System (JPMS)` â€” replaced `rt.jar` in Java 9+

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ JVM + Standard Library = everything       â”‚
â”‚              â”‚ needed to RUN (not develop) Java apps     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Deploying Java apps to servers/containers â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ You need to compile â€” use JDK instead     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "JRE = the player; JDK = player + studio" â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ JDK â†’ jlink â†’ Module System â†’ Class Loaderâ”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

