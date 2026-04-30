---
layout: default
title: "Reflection"
parent: "Java Language"
nav_order: 58
permalink: /java-language/reflection/
number: "058"
category: Java Language
difficulty: ★★★
depends_on: Class Loader, JVM, Type Erasure
used_by: Spring Framework, Jackson, JUnit, Mockito, Lombok
tags: #java #advanced #reflection #jvm #internals
---

# 058 — Reflection

`#java` `#advanced` `#reflection` `#jvm` `#internals`

⚡ TL;DR — Inspect and manipulate classes, methods, fields, and constructors at runtime — the backbone of Spring DI, Jackson serialization, JUnit, and any framework that must work with unknown types.

| #058 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Class Loader, JVM, Type Erasure | |
| **Used by:** | Spring Framework, Jackson, JUnit, Mockito, Lombok | |

---

### 📘 Textbook Definition

Java Reflection is the ability of code to examine and modify its own structure and behavior at runtime. Through the `java.lang.reflect` package, you can inspect class metadata (fields, methods, constructors, annotations), instantiate objects without knowing their class at compile time, invoke methods by name, and access or modify private members — bypassing Java's normal access control.

---

### 🟢 Simple Definition (Easy)

Reflection lets you ask a class: "What fields do you have?" or "Do you have a method called 'save'?" at runtime — and then call that method even if you didn't know its name when you wrote the code. This is how Spring knows which fields to inject `@Autowired` into.

---

### 🔵 Simple Definition (Elaborated)

Normal Java code is static — you call `obj.save()` and the compiler verifies `save()` exists. Reflection bypasses this: you can call `method.invoke(obj)` where `method` was looked up by name at runtime. This enables frameworks to work with **any** class — Spring introspects your classes to find `@Autowired` fields, Jackson reads field names to populate JSON, JUnit finds methods annotated `@Test`.

---

### 🔩 First Principles Explanation

**The core: Class is a class**
```
Every loaded class has a java.lang.Class object in the JVM.
That Class object is itself queryable.

User.class  →  Class<User> object
User.class.getDeclaredFields()    → Field[]
User.class.getDeclaredMethods()   → Method[]
User.class.getDeclaredConstructors() → Constructor[]
```

**Three entry points:**
```
1. MyClass.class              // compile-time known class
2. obj.getClass()             // runtime instance's class
3. Class.forName("com.MyClass")// fully-qualified name as String
```

---

### ❓ Why Does This Exist (Why Before What)

Java frameworks need to work with classes they've never seen before — a user's `Order` class, a plugin loaded at runtime, a class read from a config file. Without reflection, a framework would need to know every class at compile time — impossible for general-purpose tools. Reflection is what makes IoC containers, ORMs, serializers, and testing frameworks possible.

---

### 🧠 Mental Model / Analogy

> Reflection is like having an **X-ray machine for objects**. Normal code looks at the surface: "I see a Door, I'll open it." Reflection looks inside: "What materials is this Door made of? Does it have a lock? How do I unlock it programmatically, even if it's marked private?" Powerful — but you need to know what you're doing, or you'll break things.

---

### ⚙️ How It Works (Mechanism)

```
Key classes in java.lang.reflect:
  Class<T>      → entry point; represents a loaded class
  Field         → a class field (instance or static)
  Method        → a method (instance or static)
  Constructor<T>→ a constructor
  Parameter     → a method/constructor parameter
  Annotation    → annotation on class/method/field

Key operations:
  // Inspect
  clazz.getDeclaredFields()          // all fields (including private)
  clazz.getFields()                  // only public fields (incl inherited)
  clazz.getDeclaredMethod("save", String.class)  // by name + param types

  // Access private members
  field.setAccessible(true)    // bypass access control
  method.setAccessible(true)

  // Instantiate
  Constructor<?> c = clazz.getDeclaredConstructor();
  c.setAccessible(true);
  Object obj = c.newInstance();

  // Invoke method
  method.invoke(targetObject, arg1, arg2)

  // Read/write field
  field.set(targetObject, newValue)
  Object val = field.get(targetObject)

  // Annotations
  method.getAnnotation(MyAnnotation.class)
  clazz.isAnnotationPresent(MyAnnotation.class)
```

---

### 🔄 How It Connects (Mini-Map)

```
[Reflection] ──powers──► [Spring @Autowired injection]
     │                   [Jackson JSON serialization]
     │                   [JUnit @Test discovery]
     │                   [Mockito proxy creation]
     │
     ├── uses ──────────► [Class Loader #005]
     ├── bypasses ───────► [Access Modifiers]
     └── limited by ─────► [Type Erasure #054] (generics erased)
                           [Java Module System] (strong encapsulation)
```

---

### 💻 Code Example

```java
// 1. Basic class inspection
Class<User> clazz = User.class;
System.out.println(clazz.getName());       // com.example.User
System.out.println(clazz.getSimpleName()); // User

for (Field f : clazz.getDeclaredFields()) {
    System.out.println(f.getName() + " : " + f.getType().getSimpleName());
}

// 2. Invoke method by name (like Spring MVC dispatcher)
Method saveMethod = clazz.getDeclaredMethod("save", String.class);
saveMethod.setAccessible(true);
User user = new User();
saveMethod.invoke(user, "data");   // equivalent to user.save("data")

// 3. Read/write private field (like Jackson or Hibernate)
Field nameField = clazz.getDeclaredField("name");
nameField.setAccessible(true);
User u = new User();
nameField.set(u, "Alice");              // set private field
String name = (String) nameField.get(u); // read private field

// 4. Find annotated methods (like JUnit discovering @Test)
for (Method m : clazz.getDeclaredMethods()) {
    if (m.isAnnotationPresent(MyTest.class)) {
        m.invoke(clazz.getDeclaredConstructor().newInstance());
    }
}

// 5. Instantiate without knowing the class (like IoC container)
String className = "com.example.UserService";
Class<?> serviceClass = Class.forName(className);
Object service = serviceClass.getDeclaredConstructor().newInstance();

// 6. Module system warning (Java 9+)
// setAccessible(true) may throw InaccessibleObjectException
// unless --add-opens is configured in module-info or JVM args
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Reflection only works on public members | `setAccessible(true)` accesses private members |
| Reflection is always slow | Slow first call; faster with caching; JVM can JIT Method.invoke |
| Reflection breaks encapsulation intentionally | Yes — by design, for framework use only; never in business logic |
| Java 9+ modules break all reflection | Only if module doesn't `opens` the package; frameworks work around it |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Performance without caching**
```java
// BAD: looks up Field every call — expensive
void setValue(Object obj, Object val) throws Exception {
    obj.getClass().getDeclaredField("name").set(obj, val);  // repeated lookup
}
// GOOD: cache Method/Field in a static final
private static final Field NAME_FIELD;
static {
    NAME_FIELD = User.class.getDeclaredField("name");
    NAME_FIELD.setAccessible(true);
}
```

**Pitfall 2: Breaking with Java modules (Java 9+)**
```text
InaccessibleObjectException: Unable to make field private ... accessible
Fix in module-info.java:
  opens com.example to spring.core;
Or JVM arg (avoid in prod):
  --add-opens com.example/com.example=ALL-UNNAMED
```

**Pitfall 3: Security manager restrictions**
Reflection calls are checked against the security manager in constrained environments (applets, certain app servers). Use `AccessController.doPrivileged` if needed.

---

### 🔗 Related Keywords

- **Class Loader (#005)** — loads classes whose `Class` objects reflection introspects
- **Annotation Processing (#059)** — compile-time alternative; often faster than runtime reflection
- **Type Erasure (#054)** — limits what reflection can see in generics
- **Spring IoC** — uses reflection to scan and wire `@Autowired` dependencies
- **Jackson** — uses reflection to map JSON fields to Java object fields

---

### 📌 Quick Reference Card

| #058 | Category: Java Language | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Class Loader, JVM, Type Erasure | |
| **Used by:** | Spring Framework, Jackson, JUnit, Mockito, Lombok | |

---

### 🧠 Think About This Before We Continue

**Q1.** How does Spring use reflection to implement `@Autowired` without knowing your class at compile time?
**Q2.** Why does Java 9's module system restrict `setAccessible(true)` — what security concern does it address?
**Q3.** What is the performance difference between reflection with and without caching `Method`/`Field` objects?

