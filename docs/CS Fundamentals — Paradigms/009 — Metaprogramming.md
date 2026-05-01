---
layout: default
title: "Metaprogramming"
parent: "CS Fundamentals — Paradigms"
nav_order: 9
permalink: /cs-fundamentals/metaprogramming/
number: "9"
category: CS Fundamentals — Paradigms
difficulty: ★★★
depends_on: Object-Oriented Programming (OOP), Type Systems (Static vs Dynamic), Compiled vs Interpreted Languages
used_by: Aspect-Oriented Programming, Spring Core, Reflection, Code Generation
tags: #deep-dive, #advanced, #internals, #pattern, #java
---

# 9 — Metaprogramming

`#deep-dive` `#advanced` `#internals` `#pattern` `#java`

⚡ TL;DR — Writing code that reads, generates, or modifies other code at compile time or runtime, treating programs as data.

| #9              | Category: CS Fundamentals — Paradigms                                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming (OOP), Type Systems (Static vs Dynamic), Compiled vs Interpreted Languages |                 |
| **Used by:**    | Aspect-Oriented Programming, Spring Core, Reflection, Code Generation                                  |                 |

---

### 📘 Textbook Definition

**Metaprogramming** is a programming technique in which a program has the ability to treat programs as data — reading, generating, transforming, or modifying code at compile time or runtime. A metaprogram operates on the structure of code (its syntax tree, bytecode, or type information) rather than on domain data. Forms include compile-time metaprogramming (macros, annotation processors, code generators), runtime metaprogramming (reflection, dynamic proxies), and self-modifying code. Metaprogramming is the foundation of frameworks, ORMs, DI containers, serialisation libraries, and AOP implementations.

---

### 🟢 Simple Definition (Easy)

Metaprogramming means writing code that writes or reads other code — a program that can inspect itself, generate new classes at runtime, or transform source code before it compiles.

---

### 🔵 Simple Definition (Elaborated)

Normally, you write code that operates on data — strings, numbers, objects. In metaprogramming, the code itself is the data you operate on. A Java annotation processor reads your annotations at compile time and generates new `.java` files. Spring's dependency injection container reads class metadata at startup to wire beans together. Jackson reads field names via reflection to serialise an object to JSON without you writing any serialisation code. All of these are metaprogramming: programs that understand and manipulate the structure of other programs. This is what enables the "magic" in most modern frameworks — and understanding it demystifies that magic completely.

---

### 🔩 First Principles Explanation

**The problem: repetitive structural patterns that cannot be abstracted by functions.**

Consider serialising an arbitrary Java object to JSON without metaprogramming:

```java
// Manual — must be written for every single class
String toJson(User user) {
    return "{\"id\":" + user.getId()
        + ",\"name\":\"" + user.getName() + "\"}";
}
```

You need a different function for every class. You cannot abstract this further with OOP because you would need to know the field names and types at compile time.

**The constraint:** Static languages like Java compile code to bytecode. Once compiled, a class is a fixed structure. To write generic behaviour that works across _any_ class, you need a way to inspect that structure at runtime.

**The insight:** the class structure (field names, types, method signatures) is itself data — stored in the `.class` file as metadata. If code can read that metadata, it can act on any class generically.

**The solution — reflection:**

```java
// Works for ANY object — metaprogramming via reflection
String toJson(Object obj) throws Exception {
    StringBuilder sb = new StringBuilder("{");
    for (Field field : obj.getClass().getDeclaredFields()) {
        field.setAccessible(true);
        sb.append("\"").append(field.getName()).append("\":")
          .append("\"").append(field.get(obj)).append("\",");
    }
    sb.append("}");
    return sb.toString();
}
```

Jackson, Gson, and every serialisation library use this pattern. Spring uses the same approach to find `@Autowired` fields, scan `@Component` classes, and create proxies.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Metaprogramming:

```java
// Every repository needs hand-written CRUD — hundreds of methods
class UserRepository {
    User findById(Long id) { /* SQL boilerplate */ }
    void save(User u)      { /* SQL boilerplate */ }
    void delete(Long id)   { /* SQL boilerplate */ }
}
class OrderRepository {
    Order findById(Long id) { /* same SQL boilerplate */ }
    void save(Order o)      { /* same SQL boilerplate */ }
    void delete(Long id)    { /* same SQL boilerplate */ }
}
// Repeated for every entity — thousands of lines of identical structure
```

What breaks without it:

1. Structural boilerplate is copy-pasted for every class — impossible to maintain at scale.
2. Framework magic (DI, ORM, AOP) would require explicit wiring by the developer in every case.
3. Generic serialisation/deserialisation is impossible without knowing all class structures upfront.
4. Code generation tools (Lombok, MapStruct) cannot exist — every DTO getter/setter must be hand-written.

WITH Metaprogramming:
→ JPA generates SQL from entity class metadata — one `@Entity` annotation replaces hundreds of lines.
→ Spring scans classpath for `@Component` — no XML bean configuration required.
→ Jackson serialises any object to JSON by reading its fields — no per-class serialisers needed.
→ Lombok generates `equals`, `hashCode`, `toString`, constructors at compile time from annotations.

---

### 🧠 Mental Model / Analogy

> Think of a skilled bureaucrat who can read any government form and automatically understand its structure: "this form has a Name field, a Date field, and a Signature section." Without asking the form's creator, the bureaucrat can process, copy, and file any form they have never seen before. They are not reading the _content_ of the form (the data) — they are reading the _structure_ of the form (the metadata) to know how to handle it.

"Bureaucrat reading form structure" = runtime reflection
"Form fields and their types" = class fields and their types (metadata)
"Processing any unseen form generically" = generic serialisation / DI / ORM
"Form content (the actual values)" = object field values
"Reading the blank form template" = reading the `Class<?>` object

The bureaucrat's superpower (working with any unseen form) is exactly what metaprogramming gives a framework.

---

### ⚙️ How It Works (Mechanism)

**Forms of Metaprogramming:**

**1. Runtime Reflection (most common in Java)**

```java
Class<?> clazz = obj.getClass();

// Inspect structure
Field[] fields   = clazz.getDeclaredFields();
Method[] methods = clazz.getMethods();
Annotation[] ann = clazz.getAnnotations();

// Read/write values
Field f = clazz.getDeclaredField("name");
f.setAccessible(true);          // bypass private access
String name = (String) f.get(obj);  // read
f.set(obj, "newName");          // write
```

**2. Dynamic Proxies (runtime code generation)**

```java
// JDK dynamic proxy: intercept all interface method calls
Object proxy = Proxy.newProxyInstance(
    target.getClass().getClassLoader(),
    new Class[]{MyInterface.class},
    (proxyObj, method, args) -> {
        log.info("Calling: " + method.getName()); // intercept
        return method.invoke(target, args);        // delegate
    }
);
```

Spring AOP uses this to implement `@Transactional` and `@Cacheable`.

**3. Compile-Time Annotation Processing**

```
┌──────────────────────────────────────────────┐
│    Java Compile-Time Annotation Processing   │
│                                              │
│  Source.java  ──►  javac                     │
│                      │                       │
│                      ▼                       │
│             Annotation Processor             │
│             reads @Annotations               │
│             generates new .java files        │
│                      │                       │
│                      ▼                       │
│         Generated source + original          │
│               compiled together              │
└──────────────────────────────────────────────┘
```

Lombok (`@Data`), MapStruct (`@Mapper`), and Micronaut's DI use annotation processing.

**4. Bytecode Manipulation**

Frameworks like Hibernate, ByteBuddy, and ASM generate or transform `.class` files at load time:

```
Entity.class  ──►  ByteBuddy / ASM  ──►  EnhancedEntity.class
                   (adds lazy loading
                    proxy methods)
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming
        │
        ▼
Metaprogramming  ◄── Type Systems  ◄── Compiled/Interpreted
(you are here)
        │
        ├──────────────────────────┬───────────────────────┐
        ▼                          ▼                       ▼
Aspect-Oriented Programming   Spring DI Container    Reflection API
        │                          │                       │
        ▼                          ▼                       ▼
Dynamic Proxies           @Component Scanning        Jackson / Gson
                          (classpath reflection)    (serialisation)
```

---

### 💻 Code Example

**Example 1 — Reflection to inspect and invoke methods:**

```java
import java.lang.reflect.*;

public class Inspector {
    public static void main(String[] args) throws Exception {
        Object obj = new StringBuilder("hello");
        Class<?> clazz = obj.getClass();

        // List all public methods
        for (Method m : clazz.getMethods()) {
            System.out.println(m.getName());
        }

        // Invoke 'append' method reflectively
        Method append = clazz.getMethod("append", String.class);
        append.invoke(obj, " world"); // equivalent to obj.append(" world")
        System.out.println(obj); // → hello world
    }
}
```

**Example 2 — JDK dynamic proxy (intercept method calls):**

```java
interface PaymentService {
    void charge(String userId, BigDecimal amount);
}

// Wrap any PaymentService implementation with logging
PaymentService loggingProxy = (PaymentService) Proxy.newProxyInstance(
    PaymentService.class.getClassLoader(),
    new Class[]{PaymentService.class},
    (proxy, method, args) -> {
        log.info("→ {} called with {}", method.getName(), args);
        Object result = method.invoke(realService, args);
        log.info("← {} returned {}", method.getName(), result);
        return result;
    }
);
loggingProxy.charge("user1", new BigDecimal("9.99"));
```

**Example 3 — Annotation processing (Lombok @Data equivalent concept):**

```java
// @Data generates: constructor, getters, setters, equals, hashCode, toString
// WITHOUT Lombok — written manually (50+ lines)
public class User {
    private String name;
    private int age;
    public User(String name, int age) { ... }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    // equals, hashCode, toString...
}

// WITH Lombok @Data — 3 lines
@Data
public class User {
    private String name;
    private int age;
}
// Annotation processor generates all boilerplate at compile time
```

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reflection is slow and should never be used     | Reflection has overhead (~5-10x a direct call), but frameworks cache `Method` and `Field` references; the amortised cost is negligible for framework startup and infrequent operations |
| Metaprogramming only works in dynamic languages | Java has reflection and annotation processors; compile-time metaprogramming via annotation processing is faster than runtime reflection and used heavily in Lombok and Micronaut       |
| Spring's DI magic is inherently insecure        | Spring scans only the application classpath; the attack surface is your code, not the reflection API itself — injection comes from untrusted input, not from class inspection          |
| Dynamic proxies work on concrete classes        | JDK dynamic proxies require an interface; CGLIB subclass proxies work on concrete classes but cannot proxy `final` methods — this is a critical Spring AOP limitation                  |
| Annotation processors run at runtime            | Annotation processors (APT) run at _compile time_ — they generate source files before the compiler finishes; runtime annotations are different and require reflection to read          |

---

### 🔥 Pitfalls in Production

**Bypassing encapsulation with `setAccessible(true)`**

```java
// BAD: forces access to private field — couples to internal impl
Field secret = PaymentProcessor.class.getDeclaredField("apiKey");
secret.setAccessible(true); // bypasses private modifier
String key = (String) secret.get(processor); // reads private field

// GOOD: use the public API — or if testing, use constructor injection
// In tests: inject via constructor, not reflection access
```

Reflective private field access breaks when the class is refactored, compiled with a security manager, or run in a Java module that denies deep reflection.

---

**Caching Class / Method objects — never lookup inside hot loops**

```java
// BAD: reflective lookup on every request — 10,000 lookups/sec
void processRequest(Object payload) {
    Method m = payload.getClass().getMethod("process"); // slow lookup!
    m.invoke(payload);
}

// GOOD: cache the Method reference once at startup
private static final Map<Class<?>, Method> METHOD_CACHE =
    new ConcurrentHashMap<>();

void processRequest(Object payload) throws Exception {
    Method m = METHOD_CACHE.computeIfAbsent(
        payload.getClass(),
        c -> c.getMethod("process") // looked up once, cached forever
    );
    m.invoke(payload);
}
```

---

**Module system blocking deep reflection in Java 9+**

```java
// BAD: works in Java 8, throws InaccessibleObjectException in Java 9+
Field f = SomeClass.class.getDeclaredField("privateField");
f.setAccessible(true); // blocked if module does not open the package

// Fix: add JVM flag (only viable during migration)
// --add-opens com.example/com.example.model=ALL-UNNAMED
// Proper fix: expose the API or use public constructors for DI
```

---

### 🔗 Related Keywords

- `Object-Oriented Programming (OOP)` — metaprogramming typically operates on OOP class/object structure
- `Reflection` — the most common form of runtime metaprogramming in Java
- `Aspect-Oriented Programming` — implemented via dynamic proxies and bytecode weaving — metaprogramming applied to cross-cutting concerns
- `Spring Core` — Spring's DI container is a metaprogramming engine: classpath scanning, proxy creation, annotation processing
- `Annotation Processors` — compile-time metaprogramming tools (Lombok, MapStruct, Micronaut DI)
- `Compiled vs Interpreted Languages` — compiled languages (Java) do metaprogramming at compile time or via reflection; interpreted languages (Python, Ruby) have richer runtime metaprogramming
- `Dynamic Proxies` — the runtime mechanism for generating proxy classes that intercept method calls
- `Type Systems (Static vs Dynamic)` — dynamic type systems (Python, Ruby) enable more powerful runtime metaprogramming at the cost of compile-time safety

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Code that reads or generates other code;  │
│              │ programs treating their own structure as  │
│              │ data to enable generic, zero-boilerplate  │
│              │ behaviour                                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Framework internals, DI containers,       │
│              │ serialisation, ORM, AOP, code generation  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Business logic; prefer explicit code for  │
│              │ clarity, debuggability, and compile safety│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Metaprogramming is the art of writing    │
│              │ code that writes the code you're tired    │
│              │ of writing yourself."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Reflection → Dynamic Proxies →            │
│              │ Annotation Processors → Spring AOP →      │
│              │ Bytecode Manipulation (ByteBuddy/ASM)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Micronaut advertises "no reflection" DI, claiming faster startup and lower memory usage than Spring. If Spring uses reflection to scan and wire beans at runtime, and Micronaut does the same at compile time via annotation processors, trace exactly what work happens at startup in each model, and explain why Micronaut's approach is incompatible with creating beans from class names stored in a database at runtime.

**Q2.** A Java 17 application running in a Docker container uses a library that calls `setAccessible(true)` on a JDK internal class. The application crashes with `InaccessibleObjectException` only in production, not locally. Explain the Java module system rule that causes this, the exact JVM flag that silences the error, and why that flag is a technical debt that should be resolved rather than permanently applied.
