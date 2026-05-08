---
layout: default
title: "Java File IO and Serialization"
parent: "Java & JVM Internals"
nav_order: 12
permalink: /java/java-file-io-serialization/
id: JLG-012
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Language, Operating Systems, File Descriptor
used_by: Spring Batch, Java Language, Testing
related: Serialization / Deserialization, NIO, Blocking I/O
tags:
  - java
  - jvm
  - intermediate
  - os
---

# JLG-012 — Java File IO and Serialization

⚡ TL;DR — Java I/O provides layered stream abstractions for reading and writing files; serialisation converts object graphs to byte streams for persistence or transfer.

| Attribute | Value |
|---|---|
| **Depends on** | Java Language, Operating Systems, File Descriptor |
| **Used by** | Spring Batch, Java Language, Testing |
| **Related** | Serialization / Deserialization, NIO, Blocking I/O |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Without a standard I/O abstraction, every Java program would call OS system calls directly — `open()`, `read()`, `write()`, `close()` — with no buffering, no character encoding handling, and no portable path semantics. Data structures in memory could not be persisted without manually converting every field to bytes.

**THE BREAKING POINT:** Real applications need to read config files, write logs, receive network payloads, and checkpoint processing state. Doing this at the raw byte level is verbose, error-prone, and tightly coupled to the OS. Character encoding differences (UTF-8 vs ISO-8859-1) cause silent data corruption when ignored.

**THE INVENTION MOMENT:** Java's I/O package was designed around two orthogonal hierarchies: byte streams (`InputStream`/`OutputStream`) for raw binary data, and character streams (`Reader`/`Writer`) for text with explicit encoding. The Decorator pattern stacks stream wrappers for buffering, compression, and data conversion. Java 1.1 added `Serializable` for automatic object persistence. Java NIO (1.4) and NIO.2 (7) added non-blocking channels, memory-mapped files, and the modern `Path`/`Files` API.

---

### 📘 Textbook Definition

**Java File I/O** is the set of classes in `java.io` and `java.nio` for reading and writing data to files, streams, and channels. The `java.io` package provides blocking byte-oriented streams (`InputStream`/`OutputStream`) and character-oriented streams (`Reader`/`Writer`). The `java.nio` package provides `Path`, `Files`, `Channel`, and `ByteBuffer` for higher-performance, non-blocking, and memory-mapped I/O. **Java Serialisation** is the mechanism by which an object implementing `java.io.Serializable` is converted to a byte stream (marshalling) and reconstructed (unmarshalling) via `ObjectOutputStream`/`ObjectInputStream`.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Java I/O wraps OS file descriptors in layered stream objects; serialisation automates the conversion of objects to bytes and back.

> A postal system: `InputStream` is the incoming mail slot (bytes arrive one at a time), `BufferedInputStream` is the sorting room (batched for efficiency), `ObjectInputStream` is the parcel scanner (reassembles full objects from bytes), and `Serializable` is the legal declaration that the parcel may be transported.

**One insight:** Always buffer I/O — a bare `FileInputStream` makes one system call per byte. A `BufferedInputStream` batches reads into 8 KB chunks, reducing system calls by 8,000x.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. All I/O in Java ultimately maps to OS file descriptors — files, sockets, and pipes share the same abstraction
2. Byte streams move raw bytes; character streams decode bytes using a `Charset` — mixing them requires an `InputStreamReader`/`OutputStreamWriter` bridge
3. Streams must be closed to release the OS file descriptor — failure leaks the descriptor
4. Serialisation converts the entire reachable object graph to bytes; `transient` fields are excluded
5. `serialVersionUID` is the compatibility key — changing a class without updating it will break deserialisation

**DERIVED DESIGN:** The Decorator pattern chains stream wrappers: `new BufferedReader(new InputStreamReader(new FileInputStream(path), UTF_8))`. Each layer adds a capability without modifying the inner stream. Java 7's try-with-resources guarantees `close()` even on exception. The NIO `Files` API consolidates common patterns into single-method calls.

**THE TRADE-OFFS:**
- **Gain:** Portable path semantics, explicit encoding control, automatic buffering, object graph persistence
- **Cost:** Java serialisation is slow, produces large byte streams, is not language-interoperable, and has well-documented security vulnerabilities (gadget chains leading to RCE)

---

### 🧪 Thought Experiment

**SETUP:** You need to save and restore a `Map<String, User>` containing 50,000 entries between application restarts.

**WHAT HAPPENS WITHOUT SERIALISATION:** You write a custom encoder that iterates every entry, converts it to CSV or JSON, and writes it field by field. On reload you write a parser. Any added field requires updating both encoder and parser. Supporting nested objects doubles the complexity.

**WHAT HAPPENS WITH SERIALISATION:** You declare `User implements Serializable`, wrap the map in `ObjectOutputStream`, and call `writeObject(map)`. The JVM serialises the full object graph — all `User` fields, nested objects, and the `HashMap` internal structure. Deserialisation reconstructs the exact same object graph in one call.

**THE INSIGHT:** Serialisation trades performance and portability for simplicity. It is appropriate for short-lived local persistence (session state, caching) but should never be used as a data interchange format — use JSON or Protobuf there.

---

### 🧠 Mental Model / Analogy

> Think of Java I/O as a factory assembly line. Raw materials (bytes) come in on a conveyor belt (`InputStream`). Workers at stations add value in sequence: the sorting worker buffers them (`BufferedInputStream`), the translation worker converts language (`InputStreamReader`), and the packaging worker assembles the final product (`ObjectInputStream` → Java object). The same line in reverse is the output path.

- `FileInputStream` → raw conveyor: bytes from disk one at a time
- `BufferedInputStream` → batch sorter: 8 KB chunks reduce trips
- `InputStreamReader` → translator: bytes → characters via charset
- `ObjectInputStream` → final assembler: bytes → complete Java object
- `close()` → end-of-shift: conveyors must be stopped to free resources

Where this analogy breaks down: the assembly line is strictly sequential (blocking); NIO channels allow multiple conveyors to run in parallel on a single thread via `Selector`.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java I/O is how your program reads from and writes to files, networks, and other data sources. Serialisation is the way Java turns an in-memory object into bytes that can be saved to a file or sent across a network.

**Level 2 — How to use it (junior developer):**
Use `Files.readAllBytes(path)` or `Files.readString(path)` for simple file reads. Use `Files.writeString(path, content)` for writes. Wrap `FileInputStream` in `BufferedInputStream` when reading large files. Implement `Serializable` for objects you need to persist. Always close streams with try-with-resources. Set `serialVersionUID` explicitly on every `Serializable` class.

**Level 3 — How it works (mid-level engineer):**
`FileInputStream.read()` delegates to a native method that calls the OS `read()` system call, which copies bytes from the kernel page cache into the JVM heap. `BufferedInputStream` pre-fetches 8 KB per system call, trading memory for syscall count. `ObjectOutputStream.writeObject()` uses reflection to enumerate all non-transient, non-static fields, writing a binary header (class name, `serialVersionUID`), then each field recursively. Java NIO `FileChannel.transferTo()` can avoid copying data through the JVM heap entirely by using the OS `sendfile()` system call.

**Level 4 — Why it was designed this way (senior/staff):**
The Decorator pattern used in `java.io` was a conscious design choice to maximise composability without combinatorial class explosion. The downside is multi-layer wrapping verbosity — addressed by `java.nio.file.Files` convenience methods. Java serialisation was designed for simplicity but neglects security: a crafted byte stream can instantiate arbitrary classes during deserialisation, enabling Remote Code Execution via gadget chains (the basis of many historical Java CVEs). Modern Java applications use `ObjectInputFilter` (Java 9+) or replace serialisation entirely with Jackson, Protobuf, or Kryo.

---

### ⚙️ How It Works (Mechanism)

**Stream layering (Decorator pattern):**
```
┌──────────────────────────────────────────┐
│  ObjectInputStream                       │
│    └─ BufferedInputStream (8KB buffer)   │
│         └─ FileInputStream               │
│              └─ OS file descriptor       │
│                   └─ kernel page cache   │
│                        └─ disk blocks    │
└──────────────────────────────────────────┘
```

**Serialisation wire format:**
```
┌────────────────────────────────────────────────┐
│ STREAM_MAGIC (0xACED)                          │
│ STREAM_VERSION (0x0005)                        │
│ TC_OBJECT → class descriptor                   │
│   className: "com.example.User"                │
│   serialVersionUID: 1234567890L                │
│   fields: [name:String, age:int, ...]          │
│ field values (recursive for nested objects)    │
└────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (write object to file, read back):**
```
Serialize:
  User user = new User("Alice", 30)
    ← YOU ARE HERE
  ObjectOutputStream oos =
    new ObjectOutputStream(
      new BufferedOutputStream(
        new FileOutputStream("user.ser")))
  oos.writeObject(user)
    → reflection: enumerate fields
    → write class descriptor + field bytes
    → flush buffer → OS write syscall
    → disk blocks written

Deserialize:
  ObjectInputStream ois = ...
  User restored = (User) ois.readObject()
    → read header, verify serialVersionUID
    → instantiate User (no-args constructor
         NOT called)
    → populate fields from bytes
```

**FAILURE PATH:**
- `InvalidClassException` — `serialVersionUID` mismatch between writer and reader versions
- `ClassNotFoundException` — deserialising class not in receiver's classpath
- Security gadget chain — untrusted byte stream triggers malicious `readObject()` override

**WHAT CHANGES AT SCALE:**
- Replace `ObjectOutputStream` with Jackson JSON or Protobuf for interoperability and performance
- Use `Files.newBufferedWriter()` with explicit `Charset` to avoid platform encoding bugs
- For large file processing, use `FileChannel` with `MappedByteBuffer` (memory-mapped I/O)

---

### 💻 Code Example

**BAD — resource leak, no buffering, unsafe deserialisation:**
```java
// BAD: no try-with-resources → file descriptor leak
FileInputStream fis =
    new FileInputStream("data.bin");
int b;
while ((b = fis.read()) != -1) { // 1 syscall/byte!
    process(b);
}
// fis never closed if exception thrown

// BAD: deserialising untrusted stream
ObjectInputStream ois =
    new ObjectInputStream(socket.getInputStream());
Object obj = ois.readObject(); // RCE risk!
```

**GOOD — buffered, try-with-resources, filtered deserialisation:**
```java
// GOOD: try-with-resources + buffering
Path path = Path.of("data.txt");

// Simple read (Java 11+)
String content = Files.readString(path, UTF_8);

// Large file: buffered line-by-line
try (BufferedReader reader =
        Files.newBufferedReader(path, UTF_8)) {
    reader.lines()
          .filter(line -> !line.isBlank())
          .forEach(this::process);
}

// GOOD: write atomically via temp file
Path tmp = Files.createTempFile("out", ".tmp");
Files.writeString(tmp, content, UTF_8);
Files.move(tmp, path,
    StandardCopyOption.ATOMIC_MOVE,
    StandardCopyOption.REPLACE_EXISTING);

// GOOD: Serializable with explicit UID
public class SessionData implements Serializable {
    private static final long serialVersionUID =
        2L; // increment when fields change
    private final String userId;
    private transient String sessionToken; // excluded
    // ...
}

// GOOD: filtered deserialisation (Java 9+)
ObjectInputStream ois =
    new ObjectInputStream(inputStream);
ois.setObjectInputFilter(
    ObjectInputFilter.Config.createFilter(
        "com.example.*;maxdepth=5;maxbytes=65536"
    )
);
SessionData data = (SessionData) ois.readObject();
```

---

### ⚖️ Comparison Table

| API | Package | Encoding | Blocking | Use Case |
|---|---|---|---|---|
| `FileInputStream`/`OutputStream` | `java.io` | Binary (bytes) | Yes | Raw byte file I/O |
| `FileReader`/`FileWriter` | `java.io` | Platform default | Yes | Text files (avoid — charset unclear) |
| `BufferedReader`/`Writer` | `java.io` | Specified charset | Yes | Buffered text I/O |
| `Files.readString()` | `java.nio.file` | Specified charset | Yes | Simple read-all-text |
| `Files.newBufferedReader()` | `java.nio.file` | Specified charset | Yes | Streaming text reads |
| `FileChannel` + `ByteBuffer` | `java.nio` | Binary | Configurable | High-performance binary I/O |
| `MappedByteBuffer` | `java.nio` | Binary | No (memory-mapped) | Large file random access |
| `ObjectOutputStream` | `java.io` | JVM binary format | Yes | Java-only object persistence |
| Jackson `ObjectMapper` | External | JSON/CBOR/etc. | Yes | Cross-language serialisation |
| Protobuf | External | Binary | Yes | Schema-based cross-language |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `FileReader` handles encoding correctly | `FileReader` uses the platform default charset — it will corrupt files on systems with different encodings; always use `InputStreamReader` with an explicit `Charset` |
| Serialisation preserves constructors | `ObjectInputStream.readObject()` reconstructs objects WITHOUT calling any constructor — field initialisation in constructors is bypassed |
| `serialVersionUID` is optional | Without it the JVM computes a hash based on class structure; any change (adding a field, changing a method signature) alters the hash, breaking existing serialised data |
| `close()` flushes the stream | `close()` does flush for `BufferedOutputStream`, but `FileOutputStream.close()` only guarantees the JVM buffer is flushed — OS page cache may still hold data; call `fsync` via `FileChannel.force(true)` for durability |
| Java serialisation is safe from untrusted input | Java serialisation is one of the most exploited attack vectors in Java history (Log4Shell used a related mechanism); never deserialise untrusted bytes without `ObjectInputFilter` |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: File descriptor leak**

**Symptom:** Application crashes with `java.io.IOException: Too many open files` after running for hours. Restarts fix it temporarily.

**Root Cause:** Streams opened without try-with-resources. An exception on the `read()` path skips the `close()` call, leaking the OS file descriptor.

**Diagnostic:**
```bash
# Check open file descriptors for the Java process
lsof -p <pid> | grep -c "REG"
# Expected < 1000; values in thousands indicate leak
# On Linux:
ls -l /proc/<pid>/fd | wc -l
```

**Fix:**
```java
// BAD: close skipped on exception
FileInputStream fis =
    new FileInputStream("f.txt");
process(fis);
fis.close(); // skipped if process() throws!

// GOOD: try-with-resources guarantees close
try (FileInputStream fis =
        new FileInputStream("f.txt")) {
    process(fis);
} // close() always called
```

**Prevention:** Enable IDE inspection "Resource opened but not closed". Use `Files` API convenience methods that manage descriptors internally.

---

**Mode 2: `InvalidClassException` on deserialisation**

**Symptom:** `java.io.InvalidClassException: com.example.User; local class incompatible: stream classdesc serialVersionUID = 1, local class serialVersionUID = 2`

**Root Cause:** A field was added or removed from the class after objects were serialised, and `serialVersionUID` was either omitted (JVM recomputed hash) or manually incremented without backward-compat handling.

**Diagnostic:**
```bash
# Check serialVersionUID of compiled class
serialver com.example.User
# Compare with value embedded in .ser file:
# hexdump -C user.ser | grep -A2 "User"
```

**Fix:**
```java
// GOOD: explicit UID + additive-only changes
public class User implements Serializable {
    private static final long serialVersionUID
        = 1L; // never change unless intentionally
    private String name;
    // Adding a field with default is backward-compat
    private String email = ""; // new in v2
}
```

**Prevention:** Always declare `serialVersionUID` explicitly. Treat serialised binary format as a public API — breaking it requires a migration strategy.

---

**Mode 3: Deserialisation RCE via gadget chain**

**Symptom:** Unexpected class instantiation, network connections to unknown hosts, or arbitrary file writes — triggered by deserialising a crafted byte stream from an external source.

**Root Cause:** `ObjectInputStream.readObject()` instantiates whatever class is named in the byte stream. If that class has a `readObject()` method with dangerous side effects (commons-collections, Spring, etc.), the attacker controls execution.

**Diagnostic:**
```bash
# Use ysoserial to generate test payloads:
# java -jar ysoserial.jar CommonsCollections1 \
#   "touch /tmp/pwned" > payload.ser
# Check if your app deserialises without filtering
grep -rn "readObject\|ObjectInputStream" src/
```

**Fix:**
```java
// BAD: no filter on external stream
Object o = new ObjectInputStream(
    externalStream).readObject();

// GOOD: allowlist with ObjectInputFilter
ObjectInputStream ois =
    new ObjectInputStream(externalStream);
ois.setObjectInputFilter(
    info -> {
        Class<?> c = info.serialClass();
        if (c == null) return ALLOWED;
        if (c == SessionData.class) return ALLOWED;
        return REJECTED;
    }
);
SessionData d = (SessionData) ois.readObject();
```

**Prevention:** Never deserialise untrusted bytes with Java serialisation. For external data, use JSON (Jackson with `@JsonTypeInfo` disabled), Protobuf, or other schema-validated formats.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language — streams, generics, try-with-resources
- Operating Systems — file descriptors, system calls, kernel page cache
- File Descriptor — OS-level handle that Java I/O streams wrap

**Builds On This (learn these next):**
- NIO — non-blocking channels, `Selector`, `FileChannel`, memory-mapped files
- Spring Batch — uses Java I/O for flat-file item readers and writers
- Serialization / Deserialization — JSON/Protobuf alternatives, security considerations

**Alternatives / Comparisons:**
- Jackson ObjectMapper — JSON serialisation: cross-language, human-readable, safer
- Protobuf — schema-based binary serialisation: compact, fast, cross-language
- Blocking I/O vs NIO — choose NIO/NIO.2 for high-concurrency servers handling many simultaneous connections

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ WHAT IT IS   │ Layered streams + object→bytes API  ║
║ PROBLEM      │ Raw OS syscalls; no portable I/O    ║
║ KEY INSIGHT  │ Always buffer; always close;        ║
║              │ never trust serialised input        ║
║ USE WHEN     │ Local file persistence, checkpoints ║
║ AVOID WHEN   │ Cross-language data exchange        ║
║ TRADE-OFF    │ Simplicity vs security/performance  ║
║ ONE-LINER    │ Files.readString(path, UTF_8)        ║
║ NEXT EXPLORE │ NIO FileChannel, Jackson, Protobuf  ║
╚════════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(A — System Interaction)** A Spring Batch job reads a 10 GB CSV file using `BufferedReader` and processes records in chunks of 1,000. The OS has 16 GB of RAM and 8 CPUs. How does the Linux kernel's page cache interact with your reads, and under what conditions would switching to memory-mapped I/O (`MappedByteBuffer`) improve — or worsen — throughput?

2. **(C — Design Trade-off)** Java serialisation does not call constructors during deserialisation. This allows reconstructing objects that lack a no-args constructor, but it also means invariants enforced in constructors can be violated by a crafted byte stream. How would you design a class hierarchy where security invariants must hold even after deserialisation?

3. **(B — Scale)** Your microservice writes an audit log to a local file at 50,000 events per second. A buffered `PrintWriter` with auto-flush enabled is dropping to 2,000 events per second under load. What is the likely bottleneck (system call frequency, kernel lock contention, disk IOPS), and what architectural changes — async I/O, log aggregation agent, structured logging framework — would you evaluate first?
