---
number: "060"
category: Java Language
difficulty: ★★☆
depends_on: JVM, Object, Streams
used_by: RMI, JMS, Caching, Persistence, Network Protocols
tags: #java #intermediate #serialization #io #security
---

# 060 — Serialization / Deserialization

`#java` `#intermediate` `#serialization` `#io` `#security`

⚡ TL;DR — Convert a Java object graph to bytes (serialize) and restore it (deserialize); Java's built-in mechanism is legacy and insecure — prefer JSON/Protobuf/Avro in modern code.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #060         │ Category: Java Language              │ Difficulty: ★★☆           │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ JVM, Object, Streams                                              │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ RMI, JMS, Caching (legacy), Persistence, Network Protocols        │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

Java serialization is the process of converting an object's state to a byte sequence (`ObjectOutputStream`), and deserialization is the reverse — reconstructing the object from bytes (`ObjectInputStream`). A class must implement `java.io.Serializable` (a marker interface). Fields marked `transient` are excluded. The process is defined by `serialVersionUID` for version control.

---

## 🟢 Simple Definition (Easy)

Serialization is **saving an object to bytes**. Deserialization is **loading it back**. Think of it as freezing an object (serialize) and thawing it (deserialize) — to store to disk, send over a network, or put in a cache.

---

## 🔵 Simple Definition (Elaborated)

Java serialization is automatic — implement `Serializable`, use `ObjectOutputStream.writeObject()`, done. But this automatic nature is dangerous: deserializing untrusted bytes can execute **arbitrary code** (gadget chains). Modern systems use JSON (Jackson), binary formats (Protobuf, Avro), or explicit DTOs rather than Java native serialization.

---

## 🔩 First Principles Explanation

**What the JVM serializes:**
```
Object in memory:
  User { name="Alice", age=30, password="secret", conn=DbConn }
                                    ↑                  ↑
                               transient fields excluded from bytes
                               (mark sensitive/non-serializable fields)

Byte stream format:
  [magic bytes][class descriptor][serialVersionUID][field values...]
  Binary format — not human-readable, not cross-language
```

**deserialization executes code:**
```
readObject() can call custom readResolve(), readObject() methods
→ Attacker can craft bytes that trigger code execution via "gadget chains"
→ Java standard library gadget chains exist (Apache Commons Collections, etc.)
```

---

## ❓ Why Does This Exist (Why Before What)

Pre-1990s distributed systems needed to pass objects between JVMs — over RMI, JMS, CORBA. Java's built-in serialization was the solution: automatic, no schema needed, handles object graphs (circular references). It was convenient — and that convenience became a security liability.

---

## 🧠 Mental Model / Analogy

> Serialization is like **cryogenics**: you freeze a person (object) completely — all their memories, state, connections. The frozen state can be stored or transported. Thawing (deserializing) restores them exactly. But if an attacker tampers with the cryo-pod (the byte stream) before thawing, strange things happen when they wake up — that's the deserialization vulnerability.

---

## ⚙️ How It Works (Mechanism)

```
Serialize:
  ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("obj.ser"));
  oos.writeObject(myObject);   // writes class descriptor + field values
  oos.close();

Deserialize:
  ObjectInputStream ois = new ObjectInputStream(new FileInputStream("obj.ser"));
  MyClass obj = (MyClass) ois.readObject();  // reconstructs object
  ois.close();

Key mechanism points:
  - Marker interface: implements Serializable (no methods required)
  - transient = excluded from serialization
  - static fields = excluded (they belong to class, not instance)
  - serialVersionUID = version ID (see #061)
  - Custom hooks: readObject(), writeObject(), readResolve(), writeReplace()

Object graph handling:
  - Handles circular references (writes each object once, uses back-references)
  - All referenced objects must also be Serializable (or transient)
```

---

## 🔄 How It Connects (Mini-Map)

```
[Java Serialization] ─uses─► [Serializable marker interface]
       │                      [serialVersionUID #061]
       │                      [transient keyword]
       │
       ├─► Problems: security, performance, cross-language
       │
       └─► Modern alternatives:
               JSON: Jackson, Gson
               Binary: Protobuf, Avro, Thrift, MessagePack
               Structured: JAXB (XML), Kryo (fast binary)
```

---

## 💻 Code Example

```java
// 1. Basic serialization
import java.io.*;

class User implements Serializable {
    private static final long serialVersionUID = 1L;  // explicit version
    String name;
    int    age;
    transient String password;  // excluded — sensitive!
    transient Connection dbConn; // excluded — not serializable
}

// Serialize
User user = new User();
user.name = "Alice"; user.age = 30; user.password = "secret123";
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("user.ser"))) {
    oos.writeObject(user);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("user.ser"))) {
    User restored = (User) ois.readObject();
    System.out.println(restored.name);     // "Alice"
    System.out.println(restored.password); // null — transient field
}

// 2. Custom serialization (validate on deserialize)
class SecureUser implements Serializable {
    private static final long serialVersionUID = 2L;
    private String name;

    private void readObject(ObjectInputStream ois)
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        if (name == null || name.isEmpty())
            throw new InvalidObjectException("name must not be null");
    }
}

// 3. Modern alternative — Jackson JSON (preferred)
ObjectMapper mapper = new ObjectMapper();
String json  = mapper.writeValueAsString(user);       // serialize to JSON
User restored = mapper.readValue(json, User.class);   // deserialize from JSON

// 4. Filter stream to defend against deserialization attacks (Java 9+)
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "com.example.*;maxdepth=5;maxarray=1000;!*");
ois.setObjectInputFilter(filter);
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Serialization is safe for untrusted input | Deserializing untrusted bytes can execute arbitrary code |
| `transient` means encrypted | `transient` means excluded — field is null/0 after deserialization |
| java.io.Serializable is still the right approach | Use Jackson/Protobuf; Java serialization is deprecated in new designs |
| static fields are serialized | Static fields belong to the class, not the instance — never serialized |

---

## 🔥 Pitfalls in Production

**Critical: Never deserialize untrusted bytes**
CVE-2015-4852 (WebLogic), CVE-2015-7501 (Apache Commons Collections) — real RCE exploits via Java deserialization gadget chains. Affected JBoss, WebSphere, WebLogic.
Fix: use `ObjectInputFilter` whitelist; prefer JSON/Protobuf; use `jdk.serialFilter` JVM flag.

**Pitfall 1: Missing serialVersionUID**
```java
class User implements Serializable {
    String name;
    // No serialVersionUID → JVM auto-computes based on class structure
    // Add any field → serialVersionUID changes → deserializing old data FAILS
}
// Fix: always declare: private static final long serialVersionUID = 1L;
```

**Pitfall 2: Non-serializable field**
```java
class Service implements Serializable {
    private DataSource ds;  // DataSource is not Serializable → exception!
}
// Fix: mark transient: transient private DataSource ds;
```

---

## 🔗 Related Keywords

- **SerialVersionUID (#061)** — version control for serialization compatibility
- **Reflection (#058)** — serialization uses reflection internally
- **transient keyword** — excludes fields from serialization
- **Jackson / Gson** — modern JSON serialization alternatives
- **Protobuf / Avro** — efficient binary serialization for cross-language use
- **Externalizable** — interface for fully custom serialization control

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Implements Serializable → auto byte             │
│              │ conversion; transient = skip; UID = version    │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ Legacy JMS/RMI; caching (Hazelcast/Redis)       │
│              │ ONLY with trusted sources + filters           │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ Any new design — use Jackson/Protobuf instead  │
│              │ Never deserialize untrusted bytes              │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "Object-to-bytes and back; powerful but        │
│              │  dangerous with untrusted input — avoid in new │
│              │  designs, use JSON/Protobuf"                   │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ SerialVersionUID → Jackson → Protobuf          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

**Q1.** Why can deserializing untrusted bytes lead to Remote Code Execution — what mechanism makes this possible?
**Q2.** What happens if you accidentally add a field to a `Serializable` class and there is no explicit `serialVersionUID`?
**Q3.** Why does marking a field `transient` lose its value on deserialization — how would you restore its value correctly?

