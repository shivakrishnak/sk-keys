---
layout: default
title: "Reflection"
parent: "Java Language"
nav_order: 319
permalink: /java-language/reflection/
number: "319"
category: Java Language
difficulty: ★★★
depends_on: "Class Loader, Type Erasure, Annotations, JVM Bytecode"
used_by: "Spring DI, Hibernate ORM, JUnit 5, Jackson, Mockito, Java modules"
tags: #java, #reflection, #runtime, #introspection, #spring, #performance
---

# 319 — Reflection

`#java` `#reflection` `#runtime` `#introspection` `#spring` `#performance`

⚡ TL;DR — **Reflection** is Java's runtime introspection API: inspect and invoke any class, field, method, or constructor — even private ones — bypassing compile-time type checking. Powers Spring, Hibernate, and JUnit.

| #319            | Category: Java Language                                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Class Loader, Type Erasure, Annotations, JVM Bytecode             |                 |
| **Used by:**    | Spring DI, Hibernate ORM, JUnit 5, Jackson, Mockito, Java modules |                 |

---

### 📘 Textbook Definition

**Java Reflection** (`java.lang.reflect` package): a runtime API that allows a program to examine or modify its own structure. Core capabilities: (1) load a class by name at runtime (`Class.forName()`); (2) inspect class metadata (fields, methods, constructors, annotations, modifiers); (3) invoke methods, access fields, and create instances without compile-time type knowledge; (4) bypass access control (`setAccessible(true)` — constrained by Java 9 module system). Key classes: `Class<T>`, `Field`, `Method`, `Constructor`, `Modifier`. Performance: reflective calls are slower than direct calls (JIT cannot optimize; boundary checks; security validation). Java 9+: module encapsulation restricts deep reflection across module boundaries.

---

### 🟢 Simple Definition (Easy)

Normal Java: `User user = new User(); user.setName("Alice");` — you know the type at compile time. Reflection: `Class<?> clazz = Class.forName("com.example.User"); Object user = clazz.getDeclaredConstructor().newInstance(); clazz.getDeclaredMethod("setName", String.class).invoke(user, "Alice");` — you work with the class using its name as a string, without importing it or knowing its type at compile time. Spring uses this to wire beans by type/name from configuration. Hibernate maps Java fields to database columns. JUnit discovers and runs `@Test` methods. All powered by reflection.

---

### 🔵 Simple Definition (Elaborated)

Reflection is the foundation of most Java frameworks. Spring's dependency injection: scans your classpath for classes annotated with `@Component`, instantiates them via `getDeclaredConstructor().newInstance()`, reads `@Autowired` fields via `getDeclaredFields()`, and injects dependencies. None of this is possible with normal Java code — Spring doesn't know your classes at compile time. Hibernate maps `@Column` annotations to database columns by reading field metadata at runtime. JUnit runs `@Test` methods by scanning your test class and invoking annotated methods. The power of reflection is framework-level metaprogramming. The cost: slower execution and harder-to-understand code flow.

---

### 🔩 First Principles Explanation

**Complete Reflection API — inspection, invocation, and module system impact:**

```
REFLECTION CORE API:

  1. OBTAINING Class OBJECT:

  // From class literal (compile-time known):
  Class<User> clazz = User.class;

  // From instance:
  User user = new User("Alice");
  Class<?> clazz = user.getClass();

  // From name (runtime; class must be on classpath):
  Class<?> clazz = Class.forName("com.example.User");  // throws ClassNotFoundException

  2. INSPECTING STRUCTURE:

  Class<?> clazz = User.class;

  // Fields:
  Field[] publicFields  = clazz.getFields();           // public fields (including inherited)
  Field[] allFields     = clazz.getDeclaredFields();   // all fields (incl private, excl inherited)

  Field nameField = clazz.getDeclaredField("name");
  nameField.setAccessible(true);   // bypass private access control
  Object value = nameField.get(user);  // get field value
  nameField.set(user, "Bob");          // set field value

  // Methods:
  Method[] methods = clazz.getDeclaredMethods();
  Method setName = clazz.getDeclaredMethod("setName", String.class);
  setName.setAccessible(true);
  setName.invoke(user, "Charlie");  // invoke method on instance

  // Static method (no instance needed):
  Method staticMethod = clazz.getDeclaredMethod("createDefault");
  staticMethod.invoke(null);  // null = no instance

  // Constructors:
  Constructor<?> constructor = clazz.getDeclaredConstructor(String.class, int.class);
  Object newUser = constructor.newInstance("Dave", 30);

  // Annotations:
  if (clazz.isAnnotationPresent(Entity.class)) {
      Entity entity = clazz.getAnnotation(Entity.class);
      String tableName = entity.name();
  }

  Field ageField = clazz.getDeclaredField("age");
  Column column = ageField.getAnnotation(Column.class);

  3. MODIFIERS:

  int mods = clazz.getModifiers();
  Modifier.isPublic(mods)    → true/false
  Modifier.isAbstract(mods)  → true/false
  Modifier.isFinal(mods)     → true/false

JAVA 9 MODULE SYSTEM IMPACT:

  Pre-Java 9: setAccessible(true) works on any field in any package
  Java 9+: modules control access:

  // Accessing a private field in an unexported package:
  field.setAccessible(true);
  // → InaccessibleObjectException: "Unable to make private accessible:
  //    module com.example does not 'opens com.example' to unnamed module"

  FIX (module-info.java):
  module com.example {
      opens com.example to my.framework;  // allow deep reflection from my.framework
  }

  OR JVM flag (for legacy tools):
  --add-opens java.base/java.lang=ALL-UNNAMED

  IMPLICATION: Spring Boot, Hibernate, Mockito required --add-opens for Java 17+
  Spring 6 + Hibernate 6: moved to compile-time generation (annotation processing)
  to reduce reflection dependency

PERFORMANCE COMPARISON:

  // Benchmark: 10 million invocations
  Direct call:         ~15ms
  Reflective invoke:   ~180ms  (12x slower)
  With MethodHandle:   ~20ms   (near direct; JIT-optimizable)

  // Spring 6: AOT compilation pre-generates bean factory code
  // Avoids reflection for most bean operations at runtime → near-direct performance

METHOD HANDLES (Java 7 — modern alternative):

  // MethodHandle: typed, JIT-optimizable reflection
  MethodHandles.Lookup lookup = MethodHandles.lookup();
  MethodHandle setter = lookup.findVirtual(User.class, "setName",
      MethodType.methodType(void.class, String.class));
  setter.invokeExact(user, "Eve");  // JIT-friendly; faster than Method.invoke

  // Java 9 VarHandle: field access via MethodHandle mechanism
  VarHandle nameHandle = MethodHandles.lookup().findVarHandle(User.class, "name", String.class);
  nameHandle.set(user, "Frank");
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Reflection:

- Frameworks cannot instantiate user classes without importing them (circular dependency)
- DI containers cannot discover and wire beans at runtime
- ORMs cannot map unknown Java classes to database schemas
- Test frameworks cannot discover and run annotated test methods

WITH Reflection:
→ Frameworks operate on user classes without compile-time dependency. Loose coupling between framework and application code. Configuration-driven instantiation, injection, and mapping.

---

### 🧠 Mental Model / Analogy

> A locksmith with a master key and an x-ray scanner. Normal Java code: you enter a building with your own key — you can only access rooms you have a key for. Reflection: the locksmith uses x-ray to see the floor plan (class metadata), picks any lock (setAccessible), and opens any door (accesses private members). The locksmith can also read signs on doors (annotations) to understand the purpose of each room. Spring is the locksmith hired by building management to install all the furniture (beans) per the blueprint (configuration).

"X-ray scanner sees floor plan" = reflection reads class metadata (fields, methods, annotations)
"Master key opens any door" = `setAccessible(true)` bypasses private access control
"Reads signs on doors" = `getAnnotation()` reads annotation metadata
"Locksmith hired by management" = Spring DI framework using reflection to wire beans
"Java 9 module system" = security doors that even the locksmith can't bypass without a permit

---

### ⚙️ How It Works (Mechanism)

```
REFLECTION INVOCATION PIPELINE:

  Method.invoke(obj, args):
  1. Security check: is the caller allowed? (setAccessible state, module access)
  2. Argument boxing: primitive args auto-boxed to Object
  3. Method resolution: find method descriptor in class metadata
  4. Dispatch: either via JNI or inflated to a MethodAccessor (JVM-specific)
     First 15 calls: native (NativeMethodAccessor)
     After 15 calls: JVM inflates to a faster bytecode accessor (ReflectionFactory)
  5. Invoke: actual method execution
  6. Return boxing/unboxing

  Why slower than direct call:
  - No JIT inlining across reflection boundary
  - Argument boxing for primitive types
  - Security checks per call (unless accessible cached)
  - Dynamic dispatch cannot be devirtualized
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to work with unknown classes at runtime
        │
        ▼
Reflection ◄──── (you are here)
(Class/Field/Method/Constructor API; setAccessible; Java 9 module restrictions)
        │
        ├── Annotation Processing (APT): compile-time alternative to runtime reflection
        ├── MethodHandle: modern, JIT-friendly alternative for performance-sensitive code
        ├── Spring IoC: uses reflection for bean instantiation, field injection, proxies
        └── Type Erasure: reflection recovers generic type info from class metadata
```

---

### 💻 Code Example

```java
// SPRING-STYLE: discover and instantiate @Service classes:
public Object createBean(String className) throws Exception {
    Class<?> clazz = Class.forName(className);
    if (!clazz.isAnnotationPresent(Service.class)) {
        throw new IllegalArgumentException("Not a service: " + className);
    }
    return clazz.getDeclaredConstructor().newInstance();
}

// HIBERNATE-STYLE: map @Column annotations to DB columns:
public Map<String, String> getColumnMappings(Class<?> entityClass) {
    Map<String, String> mappings = new HashMap<>();
    for (Field field : entityClass.getDeclaredFields()) {
        Column col = field.getAnnotation(Column.class);
        if (col != null) {
            mappings.put(field.getName(), col.name().isEmpty() ? field.getName() : col.name());
        }
    }
    return mappings;
}

// JUNIT-STYLE: find and invoke @Test methods:
public void runTests(Object testInstance) throws Exception {
    for (Method method : testInstance.getClass().getDeclaredMethods()) {
        if (method.isAnnotationPresent(Test.class)) {
            method.invoke(testInstance);  // run each @Test method
        }
    }
}

// INJECT PRIVATE FIELD (for testing):
public static <T> void injectField(Object target, String fieldName, T value) throws Exception {
    Field field = target.getClass().getDeclaredField(fieldName);
    field.setAccessible(true);
    field.set(target, value);
}
// Usage in test:
injectField(orderService, "paymentGateway", mockGateway);
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `setAccessible(true)` is always sufficient for field access | Since Java 9, modules control deep reflection. If the target field's module doesn't `opens` the package, `setAccessible(true)` throws `InaccessibleObjectException`. Spring 6+, Hibernate 6+, and other frameworks require either module `opens` declarations or migrate to compile-time generation.                                                                  |
| Reflection is too slow for production use                   | Reflection is slower than direct calls (~12×), but in context: if you call a reflective method once per HTTP request (e.g., Spring's bean wiring), the overhead is microseconds — irrelevant. The cost is in hot paths: reflective calls in tight loops, per-element processing. Spring caches Method objects and uses MethodHandles internally to minimize overhead. |
| `Class.forName("com.example.Foo")` always finds the class   | `forName` uses the current thread's context class loader. In multi-classloader environments (OSGi, app servers), the class may not be visible. Explicitly pass the classloader: `Class.forName("com.example.Foo", true, targetClassLoader)`.                                                                                                                          |

---

### 🔥 Pitfalls in Production

**Reflection performance in hot path causing latency regression:**

```java
// ANTI-PATTERN — new reflective Method lookup on every call:
public Object invokeMethod(Object target, String methodName, Object... args) throws Exception {
    Method method = target.getClass().getDeclaredMethod(methodName,
        Arrays.stream(args).map(Object::getClass).toArray(Class[]::new));
    method.setAccessible(true);
    return method.invoke(target, args);  // method lookup on EVERY call!
}
// At 10,000 calls/sec: getDeclaredMethod() is slow (string hash lookup, security check)

// FIX — cache Method objects:
private final ConcurrentHashMap<String, Method> methodCache = new ConcurrentHashMap<>();

public Object invokeMethod(Object target, String methodName, Object... args) throws Exception {
    String key = target.getClass().getName() + "#" + methodName;
    Method method = methodCache.computeIfAbsent(key, k -> {
        try {
            Method m = target.getClass().getDeclaredMethod(methodName,
                Arrays.stream(args).map(Object::getClass).toArray(Class[]::new));
            m.setAccessible(true);
            return m;
        } catch (NoSuchMethodException e) { throw new RuntimeException(e); }
    });
    return method.invoke(target, args);  // cached Method: much faster
}
// OR: use MethodHandle (JIT-friendly, even faster after caching)
```

---

### 🔗 Related Keywords

- `Annotation Processing (APT)` — compile-time alternative to runtime reflection for code generation
- `MethodHandle` — modern, JIT-optimizable alternative to `Method.invoke()` (Java 7+)
- `Spring IoC` — uses reflection for DI, proxies, `@Autowired` injection
- `Java Modules` — module system restricts `setAccessible` across module boundaries (Java 9+)
- `Type Erasure` — reflection's `getGenericType()` recovers generic info that erasure preserved

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runtime class introspection + invocation.│
│              │ Powers frameworks: Spring, Hibernate,    │
│              │ JUnit, Jackson, Mockito.                 │
├──────────────┼───────────────────────────────────────────┤
│ API          │ Class.forName(); getDeclaredFields/       │
│              │ Methods/Constructors(); setAccessible();  │
│              │ Method.invoke(); field.get()/set()        │
├──────────────┼───────────────────────────────────────────┤
│ JAVA 9       │ Module system restricts setAccessible.   │
│              │ Requires opens in module-info.java        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Locksmith with master key: reads the    │
│              │  floor plan, opens any door, checks      │
│              │  the signs (annotations) on each."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Annotation Processing → MethodHandle →    │
│              │ Spring IoC → Java Modules → VarHandle    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Framework historically used reflection for nearly all DI operations. Spring 6 (with Spring Boot 3) introduced AOT (Ahead-of-Time compilation) that pre-generates bean factory code at build time, converting reflective calls to direct Java code. What are the benefits of AOT for startup time, runtime performance, and GraalVM native image compilation? And what are the limitations — what use cases still require runtime reflection?

**Q2.** `Method.invoke()` throws `InvocationTargetException` when the invoked method throws any exception. The actual exception is wrapped inside. This is a common source of confusing stack traces in framework code. How do you properly unwrap `InvocationTargetException` to re-throw the original exception? And when should you rethrow the wrapped exception as-is vs. unwrap it?
