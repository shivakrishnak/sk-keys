---
layout: default
title: "Reflection"
parent: "Java Language"
nav_order: 319
permalink: /java-language/reflection/
number: "0319"
category: Java Language
difficulty: ★★★
depends_on: JVM, Class Loader, Generics, Type Erasure, Bytecode
used_by: Annotation Processing (APT), Spring Core, Serialization / Deserialization
related: Annotation Processing (APT), invokedynamic, Metaprogramming
tags:
  - java
  - jvm
  - reflection
  - internals
  - deep-dive
---

# 0319 — Reflection

⚡ TL;DR — Reflection lets Java code inspect and modify its own classes, fields, and methods at runtime — enabling frameworks like Spring and Jackson to wire and serialise objects without knowing their types at compile time.

| #0319 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Class Loader, Generics, Type Erasure, Bytecode | |
| **Used by:** | Annotation Processing (APT), Spring Core, Serialization / Deserialization | |
| **Related:** | Annotation Processing (APT), invokedynamic, Metaprogramming | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Frameworks like Spring DI, JUnit, Jackson, Hibernate, and Java serialization all need to do the same thing: take an arbitrary class they've never seen at compile time and inspect it — read its fields, invoke its methods, call its constructors. Without reflection, a dependency injection container would require every developer to manually register each bean. Jackson would require a custom serializer per class. JUnit would need every test method explicitly listed.

**THE BREAKING POINT:**
A developer writes a new `@Service` class. Without reflection, to have Spring auto-wire it: add a factory method, register it in a configuration file, write a constructor adapter. This is what IoC looked like in Spring XML configuration 1.0 — hundreds of lines of boilerplate per class. At enterprise scale, a team managing 2,000 Spring beans would spend more time wiring than coding.

**THE INVENTION MOMENT:**
This is exactly why **Reflection** was built into the JVM — to let frameworks discover class structure at runtime and automate the boilerplate of object wiring, serialization, and test discovery that would otherwise require enormous amounts of manual registration code.

---

### 📘 Textbook Definition

**Reflection** is the Java platform's ability to inspect and dynamically invoke the structure of classes, interfaces, fields, and methods at runtime, using the `java.lang.reflect` package. Through reflection, code can: obtain a `Class<?>` object for any loaded class; list its fields, methods, and constructors; read or write field values (including private ones via `setAccessible(true)`); invoke methods and instantiate objects without knowing the type at compile time. Reflection operates on class metadata embedded in `.class` files and exposed by the JVM's class loader subsystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Reflection lets your program look at itself in a mirror and even reshape what it sees.

**One analogy:**
> A library catalogue knows everything about every book without reading them: author, number of pages, publication year. You can search, find any book by criteria, and even modify the catalogue entry. Reflection is the JVM's catalogue of classes — every class's fields, methods, and constructors, all available for inspection and invocation.

**One insight:**
Reflection operates outside the normal type-safety guarantees of Java. Calling `field.setAccessible(true)` bypasses `private` — the compiled bytecode still executes, but the access control enforced by the compiler is overridden at runtime. This power is what makes frameworks possible, but it also bypasses encapsulation and incurs runtime overhead that static dispatch avoids.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every loaded Java class has exactly one `Class<?>` object in the JVM representing it.
2. The `Class<?>` object contains metadata about all fields, methods, and constructors — including private ones.
3. Reflection bypasses compile-time type checking but NOT bytecode execution safety (the JVM still verifies operand types at runtime).

**DERIVED DESIGN:**
Given invariant 1, `MyClass.class`, `myObj.getClass()`, and `Class.forName("com.example.MyClass")` all return the same `Class<?>` object. All metadata access flows through this singleton.

Given invariant 2, frameworks can discover `@Autowired` fields by iterating `clazz.getDeclaredFields()` and checking annotations — without knowing the class at compile time. Spring's `AutowiredAnnotationBeanPostProcessor` does exactly this.

Given invariant 3, `method.invoke(obj, args)` ultimately dispatches to the regular bytecode of `method`. The JVM verifies argument types (throwing `IllegalArgumentException` if wrong) and catches access violations. Reflection adds a layer of dynamic dispatch overhead but does not skip bytecode validation.

```
┌────────────────────────────────────────────────┐
│       Reflection Object Hierarchy              │
│                                                │
│  Class<?>                                      │
│    ├─ getDeclaredFields()  → Field[]           │
│    ├─ getDeclaredMethods() → Method[]          │
│    ├─ getDeclaredConstructors() → Ctor[]       │
│    ├─ getAnnotations()     → Annotation[]      │
│    └─ getSuperclass()      → Class<?>          │
│                                                │
│  Field: getName(), getType(), get(obj),        │
│         set(obj, val), setAccessible(true)     │
│  Method: getName(), invoke(obj, args...)       │
│  Constructor: newInstance(args...)             │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Runtime class introspection; dynamic object creation and method invocation; enables entire categories of frameworks (DI, ORM, serialization, testing).
**Cost:** 10–100× slower than direct method calls (before JVM optimisation); bypasses compile-time type safety; breaks encapsulation (private members accessible); impedes JIT inlining; fails silently when code is obfuscated or modules deny reflective access.

---

### 🧪 Thought Experiment

**SETUP:**
A simple JSON serializer that must serialise any Java object to `{"field": "value", ...}` without knowing the class at compile time.

**WHAT HAPPENS WITHOUT REFLECTION:**
```java
// Must write one serializer per class:
String toJson(User u) {
    return "{\"name\":\"" + u.getName() + "\"}";
}
// 1000 classes → 1000 serializers. Every class change
// requires updating its serializer.
```

**WHAT HAPPENS WITH REFLECTION:**
```java
String toJson(Object obj) throws Exception {
    Class<?> cls = obj.getClass();
    StringBuilder sb = new StringBuilder("{");
    for (Field f : cls.getDeclaredFields()) {
        f.setAccessible(true);
        sb.append('"').append(f.getName()).append("\":")
          .append('"').append(f.get(obj)).append("\",");
    }
    return sb.append("}").toString();
}
// Works for ANY class. Zero per-class code needed.
```

**THE INSIGHT:**
The difference is the shift from compile-time knowledge to runtime discovery. Reflection enables "write once, work for any class" tools — the foundation of every Java framework. The cost is runtime overhead and loss of compile-time type safety at the framework layer.

---

### 🧠 Mental Model / Analogy

> Reflection is like the security system access log at a company. Normally, employees use keycards — fast, pre-authorised, no manual check. But a security auditor with a master key can open any door, inspect any room, and even change access levels on the fly. Frameworks are the auditors; regular method calls are the keycards.

- "Regular method call" → compiled dispatch — fast, type-checked at compile time.
- "Master key (setAccessible)" → bypasses private/protected — slower, runtime-checked.
- "Security auditor inspecting rooms" → framework reading fields and annotations.
- "Changing access levels" → modifying field values or wiring dependencies at startup.

Where this analogy breaks down: In Java 9+, the module system (`--add-opens`) is the physical lock that can't be bypassed even with `setAccessible` — the module system restores encapsulation that the master key previously bypassed.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Normally Java must know all types at compile time. Reflection lets code examine and use classes it never knew about until the program was running — like a mechanic who can look at any unknown car model, find out what parts it has, and fix it without a manual.

**Level 2 — How to use it (junior developer):**
Get a `Class` object with `MyClass.class` or `obj.getClass()`. Use `getDeclaredFields()` and `getDeclaredMethods()` to list members (includes private). Call `setAccessible(true)` on private members before accessing them. Use `Field.get(obj)` to read and `Field.set(obj, val)` to write from fields. Use `Method.invoke(obj, args)` to call methods. Always catch `ReflectiveOperationException`.

**Level 3 — How it works (mid-level engineer):**
The `Class<?>` object is populated by the class loader from the `.class` file's metadata tables: constant pool, field/method descriptors, attributes (including `Signature` for generics, `RuntimeVisibleAnnotations` for annotations). `getDeclaredFields()` reads the field table, returning field names, types, and modifiers. `Method.invoke()` calls through a chain of access checks, argument adapters, and ultimately an `MethodAccessor` (native or generated bytecode). JVM 21 reflective access is mediated by `VarHandle`s and method handles increasingly replacing legacy `Field`/`Method` invoke paths.

**Level 4 — Why it was designed this way (senior/staff):**
Reflection was designed as a "last resort" escape hatch when static typing cannot express a requirement. The JDK itself uses reflection internally for serialization (`ObjectInputStream`), JDBC, RMI, and JMX. The design preserved encapsulation deliberately at first — `setAccessible(false)` was the default. Java 9 modules restored stricter encapsulation by making `setAccessible` conditional on module access permissions, breaking many older frameworks and forcing migration to `MethodHandles.privateLookupIn()` — a more controlled, permission-based reflection API. This signals the long-term direction: reflection's unrestricted power is being narrowed in favour of safer, faster handles.

---

### ⚙️ How It Works (Mechanism)

**Getting a Class object:**
```java
// Three ways — all return same object:
Class<String> c1 = String.class;           // literal
Class<?> c2 = "hello".getClass();          // instance
Class<?> c3 = Class.forName("java.lang.String"); // name
System.out.println(c1 == c2); // true
```

**Inspecting fields:**
```java
class Employee {
    private String name;
    protected int id;
    public String department;
}

Field[] declared = Employee.class.getDeclaredFields();
// Returns: name, id, department (all declared — any visibility)

Field[] publicOnly = Employee.class.getFields();
// Returns: department only (public, including inherited)

Field nameField = Employee.class.getDeclaredField("name");
nameField.setAccessible(true); // bypass private
Employee emp = new Employee();
nameField.set(emp, "Alice");
System.out.println(nameField.get(emp)); // "Alice"
```

**Invoking methods:**
```java
Method m = String.class.getDeclaredMethod(
    "toUpperCase"
);
String result = (String) m.invoke("hello");
// returns "HELLO"

// Parameterised method:
Method replace = String.class.getMethod(
    "replace", char.class, char.class
);
String r2 = (String) replace.invoke("hello", 'l', 'r');
// returns "herro"
```

**Creating instances:**
```java
// Using Constructor:
Constructor<ArrayList> ctor =
    ArrayList.class.getConstructor(int.class);
ArrayList<?> list = ctor.newInstance(16);
// equivalent to new ArrayList<>(16)
```

**Modern alternative — MethodHandles (Java 9+):**
```java
// Preferred for performance-sensitive reflection:
MethodHandles.Lookup lookup =
    MethodHandles.privateLookupIn(
        Employee.class,
        MethodHandles.lookup()
    );
MethodHandle getter = lookup.findVarHandle(
    Employee.class, "name", String.class
).toMethodHandle(VarHandle.AccessMode.GET);
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (Spring DI example):
```
[Application starts]
    → [Spring scans classpath for @Component classes]
    → [For each class: Class.forName() + getAnnotations()]
    → [getDeclaredFields() seeking @Autowired]  ← YOU ARE HERE
    → [field.setAccessible(true)]
    → [field.set(bean, dependency)]
    → [Bean ready with all dependencies wired]
    → [Application serves requests]
```

**FAILURE PATH:**
```
[Module system denies reflective access]
    → [setAccessible(true) throws InaccessibleObjectException]
    → [Spring startup fails: "Cannot access field..."]
    → [Fix: --add-opens module/package=ALL-UNNAMED flag]
    → [Or: migrate to constructor injection (no reflection needed)]
```

**WHAT CHANGES AT SCALE:**
Reflection at startup (framework wiring, annotation scanning) is a one-time cost and acceptable. Reflection inside hot request-handling loops is catastrophic — method invocation via reflection is 10–100× slower than direct calls and blocks JIT inlining. Large frameworks (Spring, Quarkus) moved reflection to startup-time with AOT compilation to eliminate runtime reflection overhead in production. Quarkus' `@RegisterForReflection` annotation explicitly marks classes for GraalVM native image compilation, which cannot discover reflection usage dynamically.

---

### 💻 Code Example

Example 1 — Deep field access (framework style):
```java
// Reads all fields from any object (including private)
Map<String, Object> toMap(Object obj) throws Exception {
    Map<String, Object> map = new LinkedHashMap<>();
    Class<?> cls = obj.getClass();
    while (cls != null && cls != Object.class) {
        for (Field f : cls.getDeclaredFields()) {
            if (Modifier.isStatic(f.getModifiers())) continue;
            f.setAccessible(true);
            map.put(f.getName(), f.get(obj));
        }
        cls = cls.getSuperclass(); // walk hierarchy
    }
    return map;
}
```

Example 2 — Dynamic method invocation:
```java
// Call any no-arg method by name at runtime
Object callMethod(Object target, String methodName)
    throws ReflectiveOperationException {
    Method m = target.getClass()
        .getDeclaredMethod(methodName);
    m.setAccessible(true);
    return m.invoke(target);
}
```

Example 3 — Annotation discovery (JUnit-like):
```java
// Find all methods annotated with @Test
List<Method> findTestMethods(Class<?> testClass) {
    return Arrays.stream(testClass.getDeclaredMethods())
        .filter(m -> m.isAnnotationPresent(Test.class))
        .collect(Collectors.toList());
}
// JUnit 5's test discovery works like this internally
```

Example 4 — MethodHandle (performant reflection):
```java
// BAD for hot paths: Method.invoke()
Method toUpper = String.class.getMethod("toUpperCase");
String result = (String) toUpper.invoke("hello"); // slow

// GOOD for hot paths: MethodHandle (JIT-inlinable)
MethodHandle toUpperHandle = MethodHandles.lookup()
    .findVirtual(
        String.class, "toUpperCase",
        MethodType.methodType(String.class)
    );
String result2 = (String) toUpperHandle.invoke("hello");
// MethodHandle can be inlined by JIT after warmup
```

---

### ⚖️ Comparison Table

| Mechanism | Speed | Type Safety | Compile-Time | Module-Safe | Best For |
|---|---|---|---|---|---|
| Direct method call | Fastest | Full | Yes | Yes | All normal code |
| **Reflection (Field/Method)** | 10–100× slower | None | No | Requires open | Frameworks, tooling |
| MethodHandle | Near-direct (JIT) | Partial | No | Yes (privateLookup) | Performance-sensitive dynamics |
| invokedynamic / LambdaMetafactory | Near-direct | Partial | No | Partial | Lambda, method refs internals |

How to choose: Use direct calls always. Use reflection only for framework code run at startup or outside hot paths. Use `MethodHandle` for dynamic dispatch in performance-sensitive library code. Avoid `Field.set`/`Method.invoke` in request-handling loops.

---

### 🔁 Flow / Lifecycle

```
┌────────────────────────────────────────────────┐
│       Reflection Access Control Flow          │
│                                                │
│  [Get Class<?>]                               │
│      ↓                                         │
│  [Get Field/Method/Constructor]               │
│      ↓                                         │
│  [isAccessible?]                              │
│      ├─YES→ [Access granted — proceed]        │
│      └─NO→  [setAccessible(true)]             │
│               ↓                               │
│  [SecurityManager check (Java <17)]           │
│  [Module system check (Java 9+)]              │
│      ├─DENY→ [InaccessibleObjectException]    │
│      └─ALLOW→[AccessibleObject.override=true] │
│               ↓                               │
│  [Field.get(obj) / Method.invoke(obj, args)]  │
│      ↓                                         │
│  [JVM arg type check]                         │
│      ├─FAIL→ [IllegalArgumentException]       │
│      └─PASS→ [bytecode executes normally]     │
└────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `setAccessible(true)` disables security entirely | It only disables Java's access control (public/private/protected). The JVM still validates bytecode, checks argument types, and honours module system restrictions in Java 9+ |
| Reflection skips bytecode execution | No — `Method.invoke()` ultimately runs the same bytecode as a direct call. The overhead comes from dynamic dispatch, argument boxing/unboxing, and access checks — not from skipping execution |
| Reflection is always slow | Reflection is slow for single calls. After JVM warmup and optimization, `MethodHandle`-based reflection approaches direct call speed. Legacy `Method.invoke()` also warms up but remains slower than handles due to boxing |
| getFields() returns all fields | `getFields()` returns only public fields (including inherited). `getDeclaredFields()` returns all fields declared in the class (any visibility) but NOT inherited ones. You must walk the superclass chain for full field enumeration |
| Reflection works the same in Java 9+ modules | Java 9+ modules require `--add-opens` or `module-info.java` `opens` declarations for reflective access to non-public members. Frameworks that relied on unrestricted reflection broke on Java 9 until they added `--add-opens` flags |

---

### 🚨 Failure Modes & Diagnosis

**InaccessibleObjectException (Java 9+ Modules)**

**Symptom:**
`java.lang.reflect.InaccessibleObjectException: Unable to make field private ... accessible: module java.base does not 'opens java.lang' to unnamed module`

**Root Cause:**
Java module system blocks unrestricted reflective access. Class is in a module that doesn't declare `opens` for the package.

**Diagnostic:**
```bash
# Run with --add-opens to diagnose:
java --add-opens java.base/java.lang=ALL-UNNAMED \
     -jar myapp.jar
# If it works → module access was the problem
```

**Fix:**
```bash
# Short-term: JVM flags
--add-opens java.base/java.lang=ALL-UNNAMED

# Long-term: switch to MethodHandles.privateLookupIn()
# or use constructor injection (avoids field reflection)
```

**Prevention:** Migrate frameworks to constructor injection. Use `MethodHandles.lookup()` APIs for performant, module-safe reflection.

---

**Performance Degradation from Reflection in Hot Paths**

**Symptom:**
Profiler shows `Method.invoke()` or `Field.get()` in the top 5 hot methods during request handling. p99 latency spikes. GC pressure from reflection argument boxing.

**Root Cause:**
Reflection inside request-handling code path — e.g., a custom serializer calling `field.get(obj)` per field per request.

**Diagnostic:**
```bash
# Async profiler to identify hot reflection sites:
./asprof -d 30 -f flamegraph.html <pid>
# Look for: sun.reflect.*, java.lang.reflect.Method.invoke

# JMH benchmark to quantify:
@Benchmark
public Object directCall() { return obj.getName(); }
@Benchmark
public Object reflective() throws Exception {
    return nameField.get(obj);
}
```

**Fix:**
```java
// BAD: reflection in hot path (per-request)
Object value = field.get(incomingObject);

// GOOD: generate code at startup (Spring AOT style)
// Use ByteBuddy, ASM, or MethodHandles to generate
// direct accessor at startup, call generated code at runtime
MethodHandle getter = generateGetter(field);
// At request time: getter.invoke(incomingObject) — fast
```

**Prevention:** Confine reflection to framework initialisation (startup). Generate direct accessor code using `MethodHandle`, `ByteBuddy`, or code generation at startup.

---

**ClassNotFoundException from Dynamic Class Loading**

**Symptom:**
`ClassNotFoundException: com.example.MyService` thrown at runtime inside `Class.forName()`.

**Root Cause:**
Class not on the classpath at runtime, or loaded by a different class loader than the one used in `Class.forName()`.

**Diagnostic:**
```bash
# Check classpath:
java -verbose:class -cp . MyApp 2>&1 | grep MyService
# If not shown → class not loaded

# Check which classloader is active:
System.out.println(
    Thread.currentThread().getContextClassLoader()
);
```

**Fix:**
```java
// BAD: uses bootstrap classloader (may miss app classes)
Class<?> cls = Class.forName("com.example.MyService");

// GOOD: use context classloader (finds app classes)
Class<?> cls = Class.forName(
    "com.example.MyService",
    true,  // initialise the class
    Thread.currentThread().getContextClassLoader()
);
```

**Prevention:** Always specify the class loader explicitly in framework code. Test with all deployment class loader configurations (flat, OSGi, Spring Boot fat jar).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — reflection operates on the JVM's class representation; understanding what the JVM loads and executes is foundational
- `Class Loader` — `Class.forName()` uses class loaders; understanding class loading explains `ClassNotFoundException` and class loader isolation
- `Type Erasure` — reflection exposes the `Signature` attribute that preserves generic type info; understanding erasure explains `getGenericType()` vs `getType()`

**Builds On This (learn these next):**
- `Annotation Processing (APT)` — annotations and reflection are complementary; APT processes annotations at compile time, reflection reads them at runtime
- `Spring Core` — Spring's DI, AOP, and bean management are built almost entirely on reflection (with increasingly AOT-generated optimizations)
- `Serialization / Deserialization` — Java serialization and Jackson use reflection to discover fields for ser/deser

**Alternatives / Comparisons:**
- `invokedynamic` — a JVM instruction that enables faster dynamic dispatch; `MethodHandle` is its API counterpart and is preferred over reflection for performance
- `Annotation Processing (APT)` — compile-time alternative to runtime reflection for many framework use cases; AOT compilation (GraalVM) pushes frameworks further in this direction

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime inspection and invocation of      │
│              │ classes, fields, methods, constructors   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Frameworks need to work with unknown      │
│ SOLVES       │ classes at compile time (DI, ORM, JSON)  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Bypasses compile-time type safety. 10–100x│
│              │ slower than direct calls. Only acceptable │
│              │ at startup or in tooling — never in loops │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Framework/library code that works with    │
│              │ unknown user classes at startup           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hot request-handling code; use            │
│              │ MethodHandle or generated code instead    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Dynamic power vs performance, type safety,│
│              │ and encapsulation                         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The framework's master key — powerful    │
│              │  but expensive and breaks locks"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Annotation Processing → invokedynamic →   │
│              │ Spring Core (how it uses reflection)      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot performs classpath scanning and dependency injection at startup using reflection. A new `@Component` bean has 500 fields, of which 20 are `@Autowired`. Trace the exact sequence of reflection operations Spring performs to wire this bean — from `ClassPathScanningCandidateComponentProvider` finding the class through `AutowiredAnnotationBeanPostProcessor` setting all 20 fields — and calculate the minimum number of JVM reflection API calls required, noting which calls are the most expensive.

**Q2.** GraalVM's native image compilation cannot discover reflection usage dynamically — every reflectively accessed class must be declared in a `reflect-config.json` file. Explain why this is a fundamental limitation of AOT compilation (not a GraalVM bug), what specifically about reflection makes static analysis of all possible reflective access impossible in the general case, and what approach frameworks like Quarkus and Micronaut take to solve this without requiring developers to manually write `reflect-config.json`.

