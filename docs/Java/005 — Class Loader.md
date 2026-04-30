---
layout: default
title: "Class Loader"
parent: "Java Fundamentals"
nav_order: 5
permalink: /java/class-loader/
---
🏷️ Tags — #java #jvm #internals #classloading #intermediate 

⚡ TL;DR — The JVM component that finds, loads, and links `.class` files into memory before execution begins.


| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |

---

#### 📘 Textbook Definition

A Class Loader is a component of the JVM responsible for **loading compiled `.class` files into memory**, verifying their bytecode, preparing static fields, and resolving symbolic references — following a strict **parent-delegation model** to ensure class uniqueness and security.

---

#### 🟢 Simple Definition (Easy)

The Class Loader is the JVM's **file finder and loader** — when your code references a class, the Class Loader finds the `.class` file and brings it into memory so the JVM can use it.

---

#### 🔵 Simple Definition (Elaborated)

When your program says `new ArrayList()`, the JVM doesn't magically know what `ArrayList` is — the Class Loader has to find `ArrayList.class`, load its bytecode into memory, verify it's safe, and set it up before any instance can be created. This happens **lazily** — classes are loaded on first use, not all at startup. And it follows a strict hierarchy to prevent malicious code from overriding core Java classes.

---

#### 🔩 First Principles Explanation

**The problem:**

The JVM starts with nothing loaded except itself. Your program references hundreds of classes — `String`, `ArrayList`, your own classes, third-party libraries. Someone needs to:

1. Find the `.class` file for each referenced class
2. Load the raw bytes into memory
3. Verify the bytecode isn't malicious/corrupt
4. Set up static memory (fields, constants)
5. Resolve references between classes

**The deeper problem — security:**

What stops someone from shipping a fake `java.lang.String` class that steals data? The Class Loader hierarchy.

**The solution — Parent Delegation:**

> "Before loading a class yourself, always ask your parent first. Only load it yourself if the parent can't find it."

This guarantees core Java classes always come from trusted sources — never from application code.

```
Request: "Load java.lang.String"
        ↓
Application ClassLoader → asks parent first
        ↓
Platform ClassLoader → asks parent first
        ↓
Bootstrap ClassLoader → "I have it" ✅
        ↑
Result bubbles back up — String loaded from JDK, not your code
```

---

#### 🧠 Mental Model / Analogy

> Think of Class Loaders as a **chain of librarians**, each responsible for a specific section.
> 
> When you request a book (class), the junior librarian (Application) doesn't search their shelf first — they ask the senior librarian (Platform), who asks the head librarian (Bootstrap).
> 
> Only if the head librarian says "I don't have it" does it come back down the chain for the junior to handle.
> 
> This ensures the **official, trusted edition** of every core book is always served — nobody can slip a fake copy of `java.lang.Object` onto the shelf.

---

#### ⚙️ How It Works — The Three Built-in Class Loaders

| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |
│                       │ parent of                       │
│| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |
│                       │ parent of                       │
│| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |
│                       │ parent of                       │
│| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |
└─────────────────────────────────────────────────────────┘
```

---

#### ⚙️ The Three Phases of Class Loading

```
LOADING → LINKING → INITIALIZATION
```

**Phase 1 — Loading**

```
- Find the .class file (classpath, jar, network, DB — anywhere)
- Read raw bytes into memory
- Create a java.lang.Class object representing it
```

**Phase 2 — Linking (3 sub-phases)**

| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |

**Phase 3 — Initialization**

```
- Execute static initializers (static {} blocks)
- Assign actual initial values to static fields
- This is where YOUR code first runs
```

---

#### 🔄 How It Connects

```
.class file on disk
      ↓
[Class Loader] ← you are here
      ↓
Bytecode in JVM memory (Method Area / Metaspace)
      ↓
Bytecode Verifier (part of Linking)
      ↓
JIT Compiler / Interpreter
      ↓
Execution
```

---

#### 💻 Code Example

**Inspecting Class Loaders at runtime:**

java

```java
public class ClassLoaderInspect {
    public static void main(String[] args) {

        // Your class — loaded by Application ClassLoader
        ClassLoader appCL = ClassLoaderInspect.class.getClassLoader();
        System.out.println("App CL: " + appCL);
        // Output: jdk.internal.loader.ClassLoaders$AppClassLoader@...

        // Standard library class — loaded by Bootstrap
        ClassLoader stringCL = String.class.getClassLoader();
        System.out.println("String CL: " + stringCL);
        // Output: null  ← Bootstrap returns null (it's native/C++)

        // Walk the parent chain
        ClassLoader cl = appCL;
        while (cl != null) {
            System.out.println(cl);
            cl = cl.getParent();
        }
        // Output:
        // AppClassLoader
        // PlatformClassLoader
        // (null = Bootstrap)
    }
}
```

**Building a Custom Class Loader:**

java

```java
// Real use case: load classes from an encrypted jar,
// a database, or a remote URL

public class CustomClassLoader extends ClassLoader {

    private final Path classDirectory;

    public CustomClassLoader(Path classDirectory) {
        // Crucial: pass parent explicitly — preserves delegation
        super(ClassLoader.getSystemClassLoader());
        this.classDirectory = classDirectory;
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // Only called if parent delegation FAILED to find the class
        // Convert class name to file path
        String fileName = name.replace('.', '/') + ".class";
        Path classFile = classDirectory.resolve(fileName);

        try {
            byte[] bytes = Files.readAllBytes(classFile);
            // Hand raw bytes to JVM → triggers Linking + Initialization
            return defineClass(name, bytes, 0, bytes.length);
        } catch (IOException e) {
            throw new ClassNotFoundException(name, e);
        }
    }
}

// Usage
var loader = new CustomClassLoader(Path.of("/secure/classes"));
Class<?> clazz = loader.loadClass("com.example.Plugin");
Object instance = clazz.getDeclaredConstructor().newInstance();
```

**The isolation trick — same class, two loaders = two different types:**

java

```java
ClassLoader loader1 = new CustomClassLoader(path);
ClassLoader loader2 = new CustomClassLoader(path);

Class<?> class1 = loader1.loadClass("com.example.Service");
Class<?> class2 = loader2.loadClass("com.example.Service");

System.out.println(class1 == class2);           // false ← different Class objects
System.out.println(class1.equals(class2));      // false
System.out.println(class1.isInstance(          
    class2.newInstance()));                      // false ← ClassCastException territory!
```

> This is how **Tomcat isolates webapps** — each webapp gets its own ClassLoader, so `com.example.Service` in App1 is a completely different type from `com.example.Service` in App2 — even if the bytecode is identical.

---

#### 🔁 How Spring Uses Class Loaders

| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |

---

#### ⚠️ Common Misconceptions

|Misconception|Reality|
|---|---|
|"All classes load at startup"|Classes load **lazily** — on first reference|
|"Bootstrap CL is a Java class"|It's written in C/C++ — returns `null` for `.getClassLoader()`|
|"Same bytecode = same class"|Same bytecode loaded by **different loaders** = different types|
|"Class Loader just reads files"|It also **verifies, prepares, resolves, and initializes**|
|"Custom CLs are rare/advanced"|Tomcat, Spring, OSGi, JPA all use them heavily|

---

#### 🔥 Pitfalls in Production

**1. ClassNotFoundException vs NoClassDefFoundError**

```
ClassNotFoundException  → Class not found at LOAD time
                          (wrong classpath, missing jar)

NoClassDefFoundError    → Class WAS found at compile time
                          but MISSING at runtime
                          (jar in compile scope but not runtime scope)

// NoClassDefFoundError is trickier — your code compiled fine
// but the runtime classpath is incomplete
```

**2. ClassCastException from class loader isolation**

java

```java
// Symptom: you KNOW the types match but get ClassCastException
// Root cause: same class loaded by two different ClassLoaders

// Common in: Tomcat hot reload, OSGi, plugin systems
// Fix: ensure both sides use the SAME ClassLoader for shared types

// Diagnostic:
System.out.println(obj.getClass().getClassLoader());
System.out.println(TargetType.class.getClassLoader());
// If different → ClassCastException regardless of type name match
```

**3. Memory leak via ClassLoader**

```
Custom ClassLoader holds reference to Class objects
Class objects hold reference to ClassLoader
ClassLoader holds references to all loaded classes

If ClassLoader is not GC'd → ALL its classes stay in Metaspace
→ Metaspace grows → eventually OutOfMemoryError: Metaspace

Common cause: Hot redeploy in Tomcat without proper cleanup
Diagnostic: jmap -clstats <pid> | grep ClassLoader
```

**4. Thread Context Class Loader (TCCL) confusion**

java

```java
// The thread's ClassLoader ≠ the class's ClassLoader
// JDBC, JNDI, logging frameworks use TCCL to find implementations

// If you spawn threads manually, TCCL may be wrong:
Thread t = new Thread(() -> {
    // TCCL might be Bootstrap here — can't find your classes
    Class.forName("com.example.MyDriver"); // ← fails
});

// Fix: explicitly set TCCL
t.setContextClassLoader(Thread.currentThread().getContextClassLoader());
```

---

#### 🔗 Related Keywords

- `JVM` — Class Loader is a core JVM subsystem
- `Bytecode` — what Class Loader loads into memory
- `Metaspace` — where loaded class metadata lives
- `ClassNotFoundException` — Class Loader failure at load time
- `NoClassDefFoundError` — Class Loader failure at runtime
- `CGLIB` — generates and loads new bytecode at runtime
- `Spring Boot Loader` — custom CL for nested jars
- `OSGi` — extreme ClassLoader isolation per bundle
- `Hot Reload` — new ClassLoader instance per redeploy
- `Reflection` — operates on Class objects that CL produced

---

#### 📌 Quick Reference Card

| #??? | Category: ??? | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | — | |
| **Used by:** | — | |

---
#### 🧠 Think About This Before We Continue

**Q1.** Tomcat runs multiple webapps in one JVM. Each webapp has its own `ClassLoader`. What happens when two webapps both use `log4j` but different versions — and how does ClassLoader isolation solve this?

**Q2.** Spring's `@Transactional` works via a CGLIB proxy — a subclass generated and loaded at runtime by a custom ClassLoader. What does that mean for `final` classes and `final` methods — and why does `@Transactional` silently fail on them?
