---
layout: default
title: "Serialization / Deserialization"
parent: "Java Language"
nav_order: 321
permalink: /java-language/serialization-deserialization/
number: "0321"
category: Java Language
difficulty: ★★☆
depends_on: JVM, Reflection, Type Erasure, Generics
used_by: Spring Core, Stream API, Records (Java 16+)
related: Reflection, Annotation Processing (APT), Records (Java 16+)
tags:
  - java
  - serialization
  - internals
  - security
  - intermediate
---

# 0321 — Serialization / Deserialization

⚡ TL;DR — Java serialization converts objects to bytes for storage or network transfer; deserialization restores them — but Java's built-in mechanism has critical security vulnerabilities, making JSON/binary format libraries the modern standard.

| #0321 | Category: Java Language | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, Reflection, Type Erasure, Generics | |
| **Used by:** | Spring Core, Stream API, Records (Java 16+) | |
| **Related:** | Reflection, Annotation Processing (APT), Records (Java 16+) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An object lives in memory as a graph of references — `Customer` holds an `Address` holds `String` field values. When a process ends, everything in memory is lost. When you want to send an object over the network to another JVM, you cannot send memory addresses — the other JVM has a completely different memory layout. You need to convert the object to a portable representation (bytes or text) that can be recreated identically elsewhere.

**THE BREAKING POINT:**
A distributed cache wants to store `UserSession` objects. Without serialization, you must manually write: extract each field, format as bytes, handle nested objects, handle null, handle collections. Then write the reverse. For a class with 20 fields, including nested objects and collections: hundreds of lines of error-prone conversion code per class.

**THE INVENTION MOMENT:**
This is exactly why **Serialization** was created — to let the JVM automatically convert any `Serializable` object to bytes and back, handling the entire object graph without per-class conversion code.

---

### 📘 Textbook Definition

**Serialization** is the process of converting an object graph into a flat sequence of bytes that encodes its state. **Deserialization** is the reverse: reconstructing the full object graph from those bytes, potentially on a different JVM. Java's built-in mechanism uses `ObjectOutputStream`/`ObjectInputStream`, requiring classes to implement `java.io.Serializable` (a marker interface). The JVM uses reflection to read all non-`transient` fields and writes them with type meta-information. A `serialVersionUID` field provides version compatibility checking. Modern Java applications typically use JSON (Jackson, Gson), XML (JAXB), or binary (Protobuf, Avro, Kryo) formats instead of Java's built-in serialization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Serialization packs an object into bytes; deserialization unpacks those bytes back into the same object.

**One analogy:**
> Packing a piece of furniture for moving: you disassemble it, label every part, and pack it all in a box. The movers deliver the box, and you reassemble the exact same piece on the other end. Serialization is the disassembly and packing; deserialization is the reassembly.

**One insight:**
Java's built-in serialization is powerful but dangerous — `ObjectInputStream.readObject()` executes arbitrary code during deserialization via `readResolve()` and similar hooks. This made it a vector for remote code execution exploits that compromised major Java applications (Struts, WebLogic) for years. Modern best practice: use Jackson/Gson for JSON, never expose `ObjectInputStream` to untrusted data.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Serialized form must encode both data and enough type information to reconstruct the object.
2. The object graph may contain references — serialization must handle cycles and shared references.
3. Deserialization must be deterministic: the same bytes always produce the same object state.

**DERIVED DESIGN:**
Given invariant 1, Java's `ObjectOutputStream` writes class name, `serialVersionUID`, and field values for each object. Given invariant 2, `ObjectOutputStream` maintains a reference table: on seeing an already-serialized object, it writes a reference handle rather than serializing again. This handles cycles without infinite recursion.

Given invariant 3, changes to a class (adding fields, renaming) can break deserialization if `serialVersionUID` doesn't match. This is why `serialVersionUID` should be explicitly declared — the default (auto-generated) changes when the class changes, causing `InvalidClassException` on reading old data.

```
┌────────────────────────────────────────────────┐
│    Java Serialization Wire Format (simplified) │
│                                                │
│  Header:  0xACED 0x0005 (magic + version)      │
│  Object:  TC_OBJECT (0x73)                     │
│  Class:   fully-qualified name + serialVersionUID│
│  Fields:  name, type, value (recursively)      │
│  Cycles:  TC_REFERENCE (0x71) + handle         │
│  End:     TC_ENDBLOCKDATA (0x78)               │
└────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Automatic, zero-code-per-class serialization of any `Serializable` object graph including cycles.
**Cost:** Security vulnerabilities (RCE via gadget chains); tight coupling to binary format; brittle across class version changes; ~10× slower than Kryo or Protobuf; not human-readable; not language-interoperable.

---

### 🧪 Thought Experiment

**SETUP:**
A distributed system caches user sessions. `UserSession` implements `Serializable` and is stored in Redis.

WHAT GOES WRONG WITH JAVA SERIALIZATION:
Sprint 1: `UserSession` has `userId`, `token`, `expiresAt`.
Sprint 2: Add `List<Permission> permissions`. Deploy new code.
Existing cached sessions: serialized with old class, no `permissions` field.
Read with new code: `InvalidClassException` if `serialVersionUID` mismatch, or `permissions = null` if `serialVersionUID` matches.
5% of live sessions fail silently. Support tickets flood in.

WHAT WORKS WITH JSON SERIALIZATION:
Sprint 2: Jackson reads `{"userId":..., "token":...}` — `permissions` simply absent → defaults to empty list. No exception. Backward compatible automatically. Readable in Redis CLI. Debuggable.

**THE INSIGHT:**
Java's built-in serialization couples the wire format to internal Java class structure. JSON decouples them. The more valuable property is not "zero code" but "human-readable, language-neutral, and tolerant of schema evolution."

---

### 🧠 Mental Model / Analogy

> Java serialization is like photocopying a document at a specific copier. The copy includes internal printer settings and formatting codes from that specific copier. If you try to read the photocopy on a different copier that uses different settings, it might not print correctly — and the photocopy itself reveals details about the copier's internal settings. JSON serialization is like transcribing the document's text — any copier can print it, and the transcription reveals only the content, not the machine internals.

- "Photocopy with printer codes" → Java binary serialization (format tied to JVM internals).
- "Transcribed text" → JSON representation (format independent of JVM).
- "Different copier misreading" → `InvalidClassException` across class versions.

Where this analogy breaks down: Unlike a photocopy, Java serialization CAN handle cycles and complex graphs; JSON cannot handle object cycles natively without extensions.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Saving an object to a file or sending it over the network requires converting it to bytes. Serialization is the conversion to bytes; deserialization is loading it back. It's like saving a video game state and loading it later.

**Level 2 — How to use it (junior developer):**
Implement `java.io.Serializable` (no methods needed — it's a marker). Declare `private static final long serialVersionUID = 1L` explicitly. Mark sensitive or non-serializable fields as `transient`. For JSON: use Jackson with `@JsonProperty` and `@JsonIgnore`. Never accept serialized Java objects from untrusted sources (network, user input).

**Level 3 — How it works (mid-level engineer):**
`ObjectOutputStream` uses reflection to traverse all non-transient, non-static fields, writing their class names and values. Nested `Serializable` objects are serialized recursively; a reference table prevents infinite loops on cycles. Deserialization via `ObjectInputStream.readObject()` allocates a new instance WITHOUT calling the constructor (using `Unsafe.allocateInstance`), then uses reflection to set all fields. This bypasses any validation in the constructor — a significant security concern.

**Level 4 — Why it was designed this way (senior/staff):**
Java serialization was designed in 1996 for RMI (Remote Method Invocation) and Java Beans persistence. The automatic "serialize anything without code" design traded safety for convenience. The decision to bypass constructors was pragmatic — constructors might have side effects incompatible with reconstruction. By 2015, security researchers had catalogued dozens of "gadget chains" — sequences of deserialization callbacks that, when chained, execute arbitrary OS commands. This led to CVE-2015-7450 (WebSphere), CVE-2015-4852 (WebLogic), and others. The Java team's response: JEP 290 (2017) — deserialization filters that restrict which classes can be deserialized. Josh Bloch in Effective Java 3rd Edition (2018) recommends never serializing anything using Java's native mechanism.

---

### ⚙️ How It Works (Mechanism)

**Basic Java serialization:**
```java
// Serialise to bytes
ByteArrayOutputStream baos = new ByteArrayOutputStream();
try (ObjectOutputStream oos = new ObjectOutputStream(baos)) {
    oos.writeObject(myObject);
}
byte[] bytes = baos.toByteArray();

// Deserialise from bytes
// WARNING: NEVER deserialise untrusted bytes
try (ObjectInputStream ois = new ObjectInputStream(
     new ByteArrayInputStream(bytes))) {
    MyClass restored = (MyClass) ois.readObject();
}
```

**Custom serialization hooks:**
```java
public class Account implements Serializable {
    private String username;
    private transient String password; // NOT serialized

    // Custom write: can add extra data
    private void writeObject(ObjectOutputStream oos)
        throws IOException {
        oos.defaultWriteObject();
        oos.writeUTF(encryptedToken()); // custom field
    }

    // Custom read: restore custom field
    private void readObject(ObjectInputStream ois)
        throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        this.rawToken = decryptToken(ois.readUTF());
    }
}
```

**Jackson JSON serialization (modern approach):**
```java
// Class — no interface needed
public class UserDto {
    @JsonProperty("user_id")
    private Long id;

    @JsonIgnore  // excluded from JSON
    private String internalCode;

    // Getters/setters or use @JsonAutoDetect
}

ObjectMapper mapper = new ObjectMapper();
String json = mapper.writeValueAsString(userDto);
UserDto restored = mapper.readValue(json, UserDto.class);
```

**Deserialization filter (JEP 290 — Java 9+):**
```java
// SAFE: only allow specific classes during deserialization
ObjectInputStream ois = new ObjectInputStream(input);
ois.setObjectInputFilter(filterInfo -> {
    Class<?> cl = filterInfo.serialClass();
    if (cl == null) return ObjectInputFilter.Status.UNDECIDED;
    if (cl == MyAllowedClass.class)
        return ObjectInputFilter.Status.ALLOWED;
    return ObjectInputFilter.Status.REJECTED;
});
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (Jackson JSON):
```
[Object: UserDto{id=1, name="Alice"}]
    → [mapper.writeValueAsString(dto)]
    → [Jackson reflection: reads fields/getters]  ← YOU ARE HERE
    → [Writes JSON: {"id":1,"name":"Alice"}]
    → [Transmitted over network / stored in Redis]
    → [mapper.readValue(json, UserDto.class)]
    → [Jackson reads JSON, creates UserDto via constructor]
    → [Restored: UserDto{id=1, name="Alice"}]
```

**FAILURE PATH:**
```
[New field added to UserDto: private List<Role> roles]
    → [Old JSON in cache: {"id":1,"name":"Alice"} — no roles]
    → [readValue with FAIL_ON_UNKNOWN_PROPERTIES=false]
    → [roles = null — default value, not error]
    → [Application must handle null roles defensively]
    → [OR use @JsonProperty with defaultValue]
```

**WHAT CHANGES AT SCALE:**
At 100K requests/second with JSON deserialization, Jackson's reflection-based deserialization becomes measurable. Each `readValue()` call traverses the type model. Solutions: `ObjectMapper` reuse (it's thread-safe and expensive to create), `ReaderFor`/`WriterFor` caching, and Jackson modules like `afterburner` or `blackbird` that replace reflection with generated bytecode — giving near-direct field access speed.

---

### 💻 Code Example

Example 1 — Java serialization (understand, then avoid):
```java
// Implements Serializable — everything serializable
public class Order implements Serializable {
    private static final long serialVersionUID = 1L;
    private Long id;
    private LocalDateTime createdAt;
    private transient String cacheKey; // excluded

    // Constructor, getters omitted
}

// Write:
try (var oos = new ObjectOutputStream(
     new FileOutputStream("order.ser"))) {
    oos.writeObject(order);
}

// Read (ONLY from trusted source!):
try (var ois = new ObjectInputStream(
     new FileInputStream("order.ser"))) {
    Order loaded = (Order) ois.readObject();
}
```

Example 2 — Jackson for HTTP APIs (recommended):
```java
// DTO with Jackson annotations
public record OrderDto(
    @JsonProperty("order_id") Long id,
    @JsonFormat(pattern = "yyyy-MM-dd")
    LocalDate orderDate,
    @JsonIgnore String internalCode
) {}

// Spring Boot: auto-configured Jackson
@RestController
public class OrderController {
    @GetMapping("/orders/{id}")
    public OrderDto getOrder(@PathVariable Long id) {
        return orderService.findById(id); // auto-serialized
    }
}
```

Example 3 — Jackson schema evolution (adding optional field):
```java
// v1 JSON: {"id":1,"name":"Alice"}
// v2 class adds optional field:
public class UserDto {
    private Long id;
    private String name;

    // Optional with default — absent in old JSON = empty list
    @JsonProperty(defaultValue = "[]")
    private List<String> roles = new ArrayList<>();
}

// Deserialization of v1 JSON into v2 class:
// roles = []  (empty list, not null — safe)
// Configure mapper:
mapper.configure(
    DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES,
    false
);
```

Example 4 — Protobuf (binary, language-neutral):
```protobuf
// order.proto
syntax = "proto3";
message Order {
  int64 id = 1;
  string status = 2;
  repeated OrderItem items = 3;
}
```
```java
// Generated Java code (compile-time, via protoc):
Order order = Order.newBuilder()
    .setId(123)
    .setStatus("PENDING")
    .addItems(item)
    .build();
byte[] bytes = order.toByteArray();
Order restored = Order.parseFrom(bytes);
```

---

### ⚖️ Comparison Table

| Format | Speed | Human-Readable | Language-Neutral | Security | Version Tolerance | Best For |
|---|---|---|---|---|---|---|
| Java native serialization | Medium | No | Java only | Dangerous | Poor | Legacy JVM-to-JVM only |
| **Jackson JSON** | Medium | Yes | Yes | Safe | Good | HTTP APIs, configs |
| Protobuf / gRPC | Fast | No | Yes | Safe | Excellent | Inter-service, high throughput |
| Avro | Fast | Schema-based | Yes | Safe | Excellent | Big data, Kafka |
| Kryo | Very fast | No | Java only | Medium | Manual | High-speed Java caching |

How to choose: Use Jackson JSON for all HTTP APIs and external communication. Use Protobuf/Avro for high-throughput event streaming (Kafka). Never use Java native serialization for anything new. Use Kryo only for internal Java-to-Java caching where human-readability is not needed.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java serialization is the standard for Java applications | Java native serialization is largely deprecated for new code. Jackson JSON is the practical standard. Official Java guidance recommends against native serialization |
| Adding `transient` to sensitive fields is sufficient security | `transient` only prevents that field from being in the serialized bytes. If the class is deserialized at all from untrusted input, gadget chains can still execute arbitrary code regardless of which fields are transient |
| `serialVersionUID` ensures backward compatibility | `serialVersionUID` only prevents `InvalidClassException` on version mismatch. Fields added in new versions are null/default on old objects; removed fields are silently ignored. Data loss is possible without custom `readObject` logic |
| ObjectMapper is stateless and should be created per request | `ObjectMapper` is thread-safe and expensive to create (module loading, type factory setup). Always create one instance per application and reuse it. Creating per-request is a significant performance antipattern |
| JSON deserialization is always safe | JSON deserialization of polymorphic types (Jackson's `@JsonTypeInfo`) can be exploited via deserialization attacks similar to Java native serialization. Disable `activateDefaultTyping` unless specifically needed |

---

### 🚨 Failure Modes & Diagnosis

**InvalidClassException on Deserializing Old Data**

**Symptom:**
`java.io.InvalidClassException: com.example.Order; local class incompatible: stream classdesc serialVersionUID = -123, local class serialVersionUID = 456`

**Root Cause:**
Class changed since data was serialized: field added/removed/type changed. Default `serialVersionUID` auto-generated from class structure and changed.

**Diagnostic:**
```bash
# Find serialVersionUID in serialized bytes:
hexdump -C order.ser | head -20
# First 10 bytes: AC ED 00 05 73 = magic + object

# Compute expected serialVersionUID for class:
serialver -classpath target/classes com.example.Order
```

**Fix:**
```java
// Declare explicit serialVersionUID = never auto-changes
public class Order implements Serializable {
    private static final long serialVersionUID = 1L;
    // Handle new fields with defaults in readObject()
    private void readObject(ObjectInputStream ois)
        throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        if (this.newField == null) {
            this.newField = "default";
        }
    }
}
```

**Prevention:** Always declare `serialVersionUID = 1L` explicitly. Use Jackson or Protobuf for any externally stored or transmitted data.

---

**Remote Code Execution via Gadget Chain (CVE-class)**

**Symptom:**
Server executes unexpected OS commands or connects to attacker-controlled hosts. Occurs when accepting serialized Java objects from network input.

**Root Cause:**
`ObjectInputStream.readObject()` processes untrusted bytes containing a serialised gadget chain (e.g., Apache Commons Collections `InvokerTransformer`). Deserialization invokes arbitrary `readObject` callbacks including ones that execute system commands.

**Diagnostic:**
```bash
# Check if any endpoint accepts application/x-java-serialized-object:
grep -rn "ObjectInputStream\|readObject" --include="*.java" .
# Any usage that processes externally-sourced bytes is high-risk

# ysoserial tool generates gadget chain payloads for testing:
# java -jar ysoserial.jar CommonsCollections1 "id" > payload.ser
```

**Fix:**
```java
// NEVER: accept serialized Java from untrusted sources
// BAD: raw ObjectInputStream on network input
Object obj = new ObjectInputStream(
    request.getInputStream()
).readObject();

// GOOD: use JSON/Protobuf. If must use Java serialization:
ois.setObjectInputFilter(filterInfo -> {
    Class<?> cl = filterInfo.serialClass();
    if (cl == null) return UNDECIDED;
    // Allow ONLY your specific classes
    if (allowlist.contains(cl.getName())) return ALLOWED;
    return REJECTED;
});
```

**Prevention:** Never expose `ObjectInputStream` to untrusted data. Use JSON or Protobuf for all external communication. Apply JEP 290 deserialization filters on any legacy ObjectInputStream usage.

---

**Jackson NullPointerException from Missing Required Fields**

**Symptom:**
`NullPointerException` or application logic failure when deserializing JSON missing expected fields.

**Root Cause:**
JSON field absent, type mismatch, or `null` in JSON. Fields in the target class are not null-safe.

**Diagnostic:**
```bash
# Add Jackson strict validation:
mapper.enable(
    DeserializationFeature.FAIL_ON_NULL_FOR_PRIMITIVES
);
# Enable strict mode to catch silenced errors:
mapper.enable(
    DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES
);
# During dev: log at DEBUG level with full JSON
```

**Fix:**
```java
// BAD: no null handling
public class OrderDto {
    private Long id;           // might be null from JSON
    private String status;
    // total = null if missing from JSON
    private BigDecimal total;
}

// GOOD: defensive defaults + Jackson annotations
public class OrderDto {
    @JsonProperty(required = true) // error if missing
    private Long id;

    @JsonProperty(defaultValue = "PENDING")
    private String status = "PENDING";

    @JsonDeserialize(using = BigDecimalDeserializer.class)
    private BigDecimal total = BigDecimal.ZERO;
}
```

**Prevention:** Design DTOs defensively with non-null defaults. Use `@JsonProperty(required = true)` for mandatory fields. Validate with Bean Validation (`@NotNull`) after deserialization.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — Java serialization uses JVM-level object representation and `Unsafe.allocateInstance`; understanding the JVM clarifies why constructors are bypassed
- `Reflection` — Java serialization uses reflection to traverse fields; understanding reflection explains the performance characteristics and security surface

**Builds On This (learn these next):**
- `Records (Java 16+)` — Java records have different serialization semantics; serialization of records uses the canonical constructor, resolving the constructor-bypass issue
- `Spring Core` — Spring's `@RestController` auto-serializes responses via Jackson; understanding serialization explains how Spring HTTP responses are generated

**Alternatives / Comparisons:**
- `Annotation Processing (APT)` — Jackson can use APT-generated serializers (via Jackson Modules) for improved performance over reflection-based serialization
- `Records (Java 16+)` — represents modern Java approach to value objects that are safer to serialize

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Converting object graphs to bytes and     │
│              │ back for storage or network transfer      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Objects live in memory — cannot be sent   │
│ SOLVES       │ over network or persisted without conversion│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Java's built-in serialization has RCE     │
│              │ vulnerabilities. Use Jackson/Protobuf.    │
│              │ Never deserialise untrusted Java bytes.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Jackson for HTTP APIs. Protobuf/Avro for  │
│              │ event streaming. Java serialization: never│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid Java native (ObjectInputStream) for │
│              │ any externally-sourced or untrusted data  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Data portability vs format coupling;      │
│              │ automatic vs explicit schema control      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pack to bytes for travel; unpack to live"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Records → Spring Core (Jackson auto-config)│
│              │ → Stream API (serialization in pipelines) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A payment service stores `PaymentTransaction` objects in Redis using Java native serialization. Six months later, the team adds a `fraudScore` field (a `double`) to the class. Trace exactly what happens when the service restarts and tries to deserialise the existing Redis data — identify every step that succeeds or fails (with exact exception names), how `serialVersionUID` affects the outcome, what data is lost or incorrect, and what the minimum code change is to make the system forward-compatible without losing existing data.

**Q2.** Jackson's `@JsonTypeInfo(use = JsonTypeInfo.Id.CLASS)` annotation allows polymorphic deserialization by embedding the full class name in the JSON. A security researcher reports CVE-XXXX: an attacker can send crafted JSON with a class name pointing to a gadget class (e.g., `com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`) that executes arbitrary code during deserialization. Explain the exact chain: how `@JsonTypeInfo(use=CLASS)` enables the attack, what Jackson does internally to deserialize the injected class name, why disabling `@JsonTypeInfo(use=CLASS)` in favour of `@JsonTypeInfo(use=NAME)` with an explicit name-to-class registry prevents the attack, and what residual risk remains even after this change.

