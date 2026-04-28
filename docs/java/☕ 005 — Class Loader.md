---
layout: default
title: "Class Loader"
parent: "Java Fundamentals"
nav_order: 5
permalink: /java/class-loader/
---
ðŸ·ï¸ Tags â€” #java #jvm #internals #classloading #intermediate 

âš¡ TL;DR â€” The JVM component that finds, loads, and links `.class` files into memory before execution begins.


```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ #005  â”‚ Category: JVM Internals  â”‚ Difficulty: â˜…â˜…â˜†   â”‚
â”‚ Depends on: JVM, Bytecode         â”‚ Used by: JIT,    â”‚
â”‚ Spring, Hibernate, OSGi, Tomcat   â”‚                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### ðŸ“˜ Textbook Definition

A Class Loader is a component of the JVM responsible for **loading compiled `.class` files into memory**, verifying their bytecode, preparing static fields, and resolving symbolic references â€” following a strict **parent-delegation model** to ensure class uniqueness and security.

---

#### ðŸŸ¢ Simple Definition (Easy)

The Class Loader is the JVM's **file finder and loader** â€” when your code references a class, the Class Loader finds the `.class` file and brings it into memory so the JVM can use it.

---

#### ðŸ”µ Simple Definition (Elaborated)

When your program says `new ArrayList()`, the JVM doesn't magically know what `ArrayList` is â€” the Class Loader has to find `ArrayList.class`, load its bytecode into memory, verify it's safe, and set it up before any instance can be created. This happens **lazily** â€” classes are loaded on first use, not all at startup. And it follows a strict hierarchy to prevent malicious code from overriding core Java classes.

---

#### ðŸ”© First Principles Explanation

**The problem:**

The JVM starts with nothing loaded except itself. Your program references hundreds of classes â€” `String`, `ArrayList`, your own classes, third-party libraries. Someone needs to:

1. Find the `.class` file for each referenced class
2. Load the raw bytes into memory
3. Verify the bytecode isn't malicious/corrupt
4. Set up static memory (fields, constants)
5. Resolve references between classes

**The deeper problem â€” security:**

What stops someone from shipping a fake `java.lang.String` class that steals data? The Class Loader hierarchy.

**The solution â€” Parent Delegation:**

> "Before loading a class yourself, always ask your parent first. Only load it yourself if the parent can't find it."

This guarantees core Java classes always come from trusted sources â€” never from application code.

```
Request: "Load java.lang.String"
        â†“
Application ClassLoader â†’ asks parent first
        â†“
Platform ClassLoader â†’ asks parent first
        â†“
Bootstrap ClassLoader â†’ "I have it" âœ…
        â†‘
Result bubbles back up â€” String loaded from JDK, not your code
```

---

#### ðŸ§  Mental Model / Analogy

> Think of Class Loaders as a **chain of librarians**, each responsible for a specific section.
> 
> When you request a book (class), the junior librarian (Application) doesn't search their shelf first â€” they ask the senior librarian (Platform), who asks the head librarian (Bootstrap).
> 
> Only if the head librarian says "I don't have it" does it come back down the chain for the junior to handle.
> 
> This ensures the **official, trusted edition** of every core book is always served â€” nobody can slip a fake copy of `java.lang.Object` onto the shelf.

---

#### âš™ï¸ How It Works â€” The Three Built-in Class Loaders

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              CLASS LOADER HIERARCHY                     â”‚
â”‚                                                         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚         Bootstrap ClassLoader                    â”‚   â”‚
â”‚  â”‚  â€¢ Built into JVM (written in C/C++)             â”‚   â”‚
â”‚  â”‚  â€¢ Loads: java.lang.*, java.util.*, etc.         â”‚   â”‚
â”‚  â”‚  â€¢ Source: $JAVA_HOME/lib/modules (Java 9+)      â”‚   â”‚
â”‚  â”‚  â€¢ Parent: none (root of hierarchy)              â”‚   â”‚
â”‚  â”‚  â€¢ Returns NULL when asked for parent            â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                       â”‚ parent of                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚         Platform ClassLoader                     â”‚   â”‚
â”‚  â”‚  â€¢ (was Extension ClassLoader pre Java 9)        â”‚   â”‚
â”‚  â”‚  â€¢ Loads: java.sql.*, java.xml.*, etc.           â”‚   â”‚
â”‚  â”‚  â€¢ Source: JDK platform modules                  â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                       â”‚ parent of                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚         Application ClassLoader                  â”‚   â”‚
â”‚  â”‚  â€¢ (aka System ClassLoader)                      â”‚   â”‚
â”‚  â”‚  â€¢ Loads: YOUR code + third-party jars           â”‚   â”‚
â”‚  â”‚  â€¢ Source: -classpath / -cp / CLASSPATH env var  â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                       â”‚ parent of                       â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚         Custom ClassLoaders                      â”‚   â”‚
â”‚  â”‚  â€¢ Tomcat, Spring, OSGi, JPA â€” all use these     â”‚   â”‚
â”‚  â”‚  â€¢ Load from DB, network, encrypted jars, etc.   â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš™ï¸ The Three Phases of Class Loading

```
LOADING â†’ LINKING â†’ INITIALIZATION
```

**Phase 1 â€” Loading**

```
- Find the .class file (classpath, jar, network, DB â€” anywhere)
- Read raw bytes into memory
- Create a java.lang.Class object representing it
```

**Phase 2 â€” Linking (3 sub-phases)**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  2a. VERIFICATION                               â”‚
â”‚  â€¢ Is bytecode structurally valid?              â”‚
â”‚  â€¢ No stack overflows? Valid opcodes?           â”‚
â”‚  â€¢ Type safety checks                           â”‚
â”‚  â€¢ Security: prevents malformed bytecode attack â”‚
â”‚                                                 â”‚
â”‚  2b. PREPARATION                                â”‚
â”‚  â€¢ Allocate memory for static fields            â”‚
â”‚  â€¢ Set default values (0, null, false)          â”‚
â”‚  â€¢ NOT your initial values yet                  â”‚
â”‚                                                 â”‚
â”‚  2c. RESOLUTION                                 â”‚
â”‚  â€¢ Replace symbolic references with direct refs â”‚
â”‚  â€¢ "java/util/ArrayList" â†’ actual memory pointerâ”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Phase 3 â€” Initialization**

```
- Execute static initializers (static {} blocks)
- Assign actual initial values to static fields
- This is where YOUR code first runs
```

---

#### ðŸ”„ How It Connects

```
.class file on disk
      â†“
[Class Loader] â† you are here
      â†“
Bytecode in JVM memory (Method Area / Metaspace)
      â†“
Bytecode Verifier (part of Linking)
      â†“
JIT Compiler / Interpreter
      â†“
Execution
```

---

#### ðŸ’» Code Example

**Inspecting Class Loaders at runtime:**

java

```java
public class ClassLoaderInspect {
    public static void main(String[] args) {

        // Your class â€” loaded by Application ClassLoader
        ClassLoader appCL = ClassLoaderInspect.class.getClassLoader();
        System.out.println("App CL: " + appCL);
        // Output: jdk.internal.loader.ClassLoaders$AppClassLoader@...

        // Standard library class â€” loaded by Bootstrap
        ClassLoader stringCL = String.class.getClassLoader();
        System.out.println("String CL: " + stringCL);
        // Output: null  â† Bootstrap returns null (it's native/C++)

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
        // Crucial: pass parent explicitly â€” preserves delegation
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
            // Hand raw bytes to JVM â†’ triggers Linking + Initialization
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

**The isolation trick â€” same class, two loaders = two different types:**

java

```java
ClassLoader loader1 = new CustomClassLoader(path);
ClassLoader loader2 = new CustomClassLoader(path);

Class<?> class1 = loader1.loadClass("com.example.Service");
Class<?> class2 = loader2.loadClass("com.example.Service");

System.out.println(class1 == class2);           // false â† different Class objects
System.out.println(class1.equals(class2));      // false
System.out.println(class1.isInstance(          
    class2.newInstance()));                      // false â† ClassCastException territory!
```

> This is how **Tomcat isolates webapps** â€” each webapp gets its own ClassLoader, so `com.example.Service` in App1 is a completely different type from `com.example.Service` in App2 â€” even if the bytecode is identical.

---

#### ðŸ” How Spring Uses Class Loaders

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              SPRING BOOT CLASS LOADING                   â”‚
â”‚                                                          â”‚
â”‚  Spring Boot Fat JAR:                                    â”‚
â”‚  myapp.jar/                                              â”‚
â”‚    BOOT-INF/classes/     â† your code                     â”‚
â”‚    BOOT-INF/lib/*.jar    â† dependencies                  â”‚
â”‚    org/springframework/  â† Spring loader                 â”‚
â”‚                                                          â”‚
â”‚  LaunchedURLClassLoader (Spring's custom CL)             â”‚
â”‚    â€¢ Knows how to read nested jars                       â”‚
â”‚    â€¢ Standard AppClassLoader can't do this               â”‚
â”‚    â€¢ Spring Boot Loader bridges the gap                  â”‚
â”‚                                                          â”‚
â”‚  Flow:                                                   â”‚
â”‚  java -jar myapp.jar                                     â”‚
â”‚    â†’ JarLauncher.main()                                  â”‚
â”‚    â†’ Creates LaunchedURLClassLoader                      â”‚
â”‚    â†’ Loads your Application class through it             â”‚
â”‚    â†’ Spring context boots                                â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

#### âš ï¸ Common Misconceptions

|Misconception|Reality|
|---|---|
|"All classes load at startup"|Classes load **lazily** â€” on first reference|
|"Bootstrap CL is a Java class"|It's written in C/C++ â€” returns `null` for `.getClassLoader()`|
|"Same bytecode = same class"|Same bytecode loaded by **different loaders** = different types|
|"Class Loader just reads files"|It also **verifies, prepares, resolves, and initializes**|
|"Custom CLs are rare/advanced"|Tomcat, Spring, OSGi, JPA all use them heavily|

---

#### ðŸ”¥ Pitfalls in Production

**1. ClassNotFoundException vs NoClassDefFoundError**

```
ClassNotFoundException  â†’ Class not found at LOAD time
                          (wrong classpath, missing jar)

NoClassDefFoundError    â†’ Class WAS found at compile time
                          but MISSING at runtime
                          (jar in compile scope but not runtime scope)

// NoClassDefFoundError is trickier â€” your code compiled fine
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
// If different â†’ ClassCastException regardless of type name match
```

**3. Memory leak via ClassLoader**

```
Custom ClassLoader holds reference to Class objects
Class objects hold reference to ClassLoader
ClassLoader holds references to all loaded classes

If ClassLoader is not GC'd â†’ ALL its classes stay in Metaspace
â†’ Metaspace grows â†’ eventually OutOfMemoryError: Metaspace

Common cause: Hot redeploy in Tomcat without proper cleanup
Diagnostic: jmap -clstats <pid> | grep ClassLoader
```

**4. Thread Context Class Loader (TCCL) confusion**

java

```java
// The thread's ClassLoader â‰  the class's ClassLoader
// JDBC, JNDI, logging frameworks use TCCL to find implementations

// If you spawn threads manually, TCCL may be wrong:
Thread t = new Thread(() -> {
    // TCCL might be Bootstrap here â€” can't find your classes
    Class.forName("com.example.MyDriver"); // â† fails
});

// Fix: explicitly set TCCL
t.setContextClassLoader(Thread.currentThread().getContextClassLoader());
```

---

#### ðŸ”— Related Keywords

- `JVM` â€” Class Loader is a core JVM subsystem
- `Bytecode` â€” what Class Loader loads into memory
- `Metaspace` â€” where loaded class metadata lives
- `ClassNotFoundException` â€” Class Loader failure at load time
- `NoClassDefFoundError` â€” Class Loader failure at runtime
- `CGLIB` â€” generates and loads new bytecode at runtime
- `Spring Boot Loader` â€” custom CL for nested jars
- `OSGi` â€” extreme ClassLoader isolation per bundle
- `Hot Reload` â€” new ClassLoader instance per redeploy
- `Reflection` â€” operates on Class objects that CL produced

---

#### ðŸ“Œ Quick Reference Card

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ KEY IDEA     â”‚ Finds, loads, verifies, and links .class  â”‚
â”‚              â”‚ files into JVM memory via parent          â”‚
â”‚              â”‚ delegation for safety and isolation       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ USE WHEN     â”‚ Plugin systems, hot reload, multi-tenant  â”‚
â”‚              â”‚ apps, custom class sources (DB, network)  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ AVOID WHEN   â”‚ Don't bypass parent delegation unless     â”‚
â”‚              â”‚ you fully understand isolation effects    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ ONE-LINER    â”‚ "Class Loader is the JVM's gatekeeper â€”  â”‚
â”‚              â”‚  nothing runs until it says so"           â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ NEXT EXPLORE â”‚ Metaspace â†’ JIT Compiler â†’ Reflection â†’  â”‚
â”‚              â”‚ Spring Proxy â†’ CGLIB â†’ Hot Reload         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---
#### ðŸ§  Think About This Before We Continue

**Q1.** Tomcat runs multiple webapps in one JVM. Each webapp has its own `ClassLoader`. What happens when two webapps both use `log4j` but different versions â€” and how does ClassLoader isolation solve this?

**Q2.** Spring's `@Transactional` works via a CGLIB proxy â€” a subclass generated and loaded at runtime by a custom ClassLoader. What does that mean for `final` classes and `final` methods â€” and why does `@Transactional` silently fail on them?

