#!/usr/bin/env python3
"""Fill TODO sections for Java - Exceptions and IO.md (5 keywords)."""
import re

FILE = "interview/java/Java - Exceptions and IO.md"

KEYWORDS = [
    "Exception Hierarchy",
    "Checked vs Unchecked Exceptions",
    "Try-with-Resources",
    "IO Streams",
    "NIO and NIO.2",
]

LEVEL5 = {
    "Exception Hierarchy": (
        "Java's exception hierarchy embodies a universal error "
        "classification pattern found in every robust system: "
        "recoverable errors (checked exceptions, like HTTP 4xx), "
        "programming bugs (RuntimeException, like assertion "
        "failures), and system failures (Error, like hardware "
        "faults). The same taxonomy appears in Go (error vs panic), "
        "Rust (Result vs panic!), and operating systems (signals "
        "vs traps). The expert insight: `Throwable` was designed "
        "as a class hierarchy so that catch blocks could match "
        "at any granularity - catch `IOException` for file errors, "
        "`Exception` for all recoverable errors, or `Throwable` "
        "for everything including `OutOfMemoryError`. At extreme "
        "scale, exception cost matters: creating an exception "
        "captures the entire stack trace (expensive), so "
        "high-throughput systems override "
        "`fillInStackTrace()` to return `this` without walking "
        "the stack, or use pre-allocated singleton exceptions. "
        "If redesigning today, you would use sealed types (like "
        "Kotlin's sealed classes or Rust's Result enum) to make "
        "exception handling exhaustive and verifiable at compile "
        "time.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is this recoverable or a bug?\" - recoverable = "
        "checked, bug = RuntimeException, system = Error\n"
        "- \"How deep is this stack?\" - deep stacks make exception "
        "creation expensive (100+ frames = microseconds)\n"
        "- \"Should I catch or propagate?\" - catch only if you "
        "can add value; otherwise let it bubble"
    ),
    "Checked vs Unchecked Exceptions": (
        "The checked vs unchecked debate is Java's version of "
        "the fundamental error handling design choice that every "
        "language makes: forced handling (checked) vs optional "
        "handling (unchecked). Rust chose forced (Result<T,E>), "
        "Go chose forced (multiple return values), Python/JS chose "
        "optional (all exceptions are unchecked), and Kotlin "
        "chose optional (no checked exceptions). The expert "
        "insight: checked exceptions compose poorly - they leak "
        "implementation details up the call stack, make lambda/"
        "stream code verbose, and create artificial coupling. "
        "Modern Java practice: use checked exceptions only at "
        "system boundaries (IO, network, DB) where recovery is "
        "plausible, and unchecked for everything else. Spring, "
        "Hibernate, and JDBC-template all wrap checked exceptions "
        "in unchecked for this reason. If redesigning today, "
        "you would use a Result type (like Kotlin's Result or "
        "Vavr's Either) that works with generics and lambdas "
        "without the compositional problems.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Can the caller realistically recover?\" - if yes, "
        "checked; if no, unchecked\n"
        "- \"Does this exception cross a module boundary?\" - "
        "wrap implementation-specific exceptions at boundaries\n"
        "- \"Is this breaking lambda/stream composition?\" - "
        "wrap in unchecked or use ThrowingFunction utilities"
    ),
    "Try-with-Resources": (
        "Try-with-resources is Java's implementation of the "
        "RAII (Resource Acquisition Is Initialization) pattern "
        "from C++ - the same concept as Python's `with`, C#'s "
        "`using`, Go's `defer`, and Rust's `Drop` trait. The "
        "universal principle: tie resource lifetime to a lexical "
        "scope so cleanup happens deterministically. The expert "
        "insight: try-with-resources handles the subtle "
        "suppressed exception problem - if both the try block "
        "and close() throw, the original exception is primary "
        "and the close exception is added as suppressed "
        "(`Throwable.getSuppressed()`). Before Java 7, this "
        "required 25+ lines of nested try-finally with manual "
        "null checks. At extreme scale, resource leaks are the "
        "#1 production issue: leaked connections exhaust pools, "
        "leaked file handles hit OS limits (ulimit), leaked "
        "memory causes GC pressure. If redesigning today, you "
        "would make `AutoCloseable` the default for any type "
        "holding native resources, with compiler warnings for "
        "non-try-with-resources usage.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Does this object hold a native resource?\" - if "
        "yes, it must be in try-with-resources\n"
        "- \"What happens if close() fails?\" - check for "
        "suppressed exceptions in logs\n"
        "- \"Is the resource scope correct?\" - resource should "
        "live exactly as long as needed, no longer"
    ),
    "IO Streams": (
        "Java's IO Streams implement the decorator pattern over "
        "byte/character sequences - the same concept as Unix "
        "pipes, Node.js readable/writable streams, and .NET "
        "System.IO.Stream. The expert insight: the stream "
        "decorator stack (e.g., FileInputStream -> "
        "BufferedInputStream -> DataInputStream) is both powerful "
        "and problematic. Powerful because you compose behaviors "
        "without modifying classes. Problematic because each "
        "layer adds a `read()` method call, and modern CPUs pay "
        "more for method dispatch overhead than for the actual "
        "IO (when using SSDs). At extreme scale, "
        "`BufferedReader.readLine()` allocates a new String per "
        "line (GC pressure for GB files), while NIO's "
        "`FileChannel` with `MappedByteBuffer` enables zero-copy "
        "reads. If redesigning today, you would unify "
        "InputStream/Reader into a single type parameterized by "
        "element type (byte vs char), eliminate the synchronization "
        "in FilterInputStream, and default to buffered IO.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Bytes or characters?\" - InputStream for bytes, "
        "Reader for characters. Always specify charset.\n"
        "- \"Am I buffering?\" - unbuffered IO to disk is 10-100x "
        "slower. Always wrap in Buffered*.\n"
        "- \"Can I use Files.readAllLines()?\" - for small files "
        "yes; for large files use streaming to avoid OOM"
    ),
    "NIO and NIO.2": (
        "NIO represents the evolution from blocking-thread-per-"
        "connection IO to non-blocking event-driven IO - the same "
        "paradigm shift as Node.js (libuv event loop), Nginx "
        "(epoll/kqueue), Go (goroutines on netpoller), and "
        "Rust (tokio/async-std). The expert insight: NIO's "
        "Selector is Java's abstraction over OS-level IO "
        "multiplexing (epoll on Linux, kqueue on macOS, IOCP on "
        "Windows). One thread can monitor thousands of channels "
        "because the OS kernel does the waiting. NIO.2 added "
        "the Path/Files API and `AsynchronousFileChannel` "
        "(true async file IO via OS completion ports). At extreme "
        "scale, raw NIO Selectors are complex and error-prone - "
        "this is why Netty, Vert.x, and Project Reactor exist "
        "as higher-level abstractions. If redesigning today, "
        "you would build virtual threads (Project Loom) from the "
        "start, making blocking IO efficient without NIO's "
        "complexity - which is exactly what Java 21 delivers.\n\n"
        "**Expert thinking cues:**\n"
        "- \"How many concurrent connections?\" - <1000: blocking "
        "IO with virtual threads. >10K: NIO with Netty\n"
        "- \"File or network IO?\" - Files: use NIO.2 Path/Files "
        "API. Network: use Netty or virtual threads\n"
        "- \"Is NIO complexity justified?\" - with virtual threads "
        "(Java 21+), blocking IO scales equally well with simpler "
        "code"
    ),
}

QUICKREF = {
    "Exception Hierarchy": (
        "**WHAT IT IS:** Class tree rooted at Throwable with "
        "Error (system) and Exception (application) branches\n"
        "**PROBLEM IT SOLVES:** Classifies failures into "
        "recoverable errors, bugs, and system failures\n"
        "**KEY INSIGHT:** Catch blocks match by type hierarchy - "
        "catch specific exceptions, not `Exception` or `Throwable`\n"
        "**USE WHEN:** Designing error handling strategy, "
        "creating custom exceptions, deciding catch granularity\n"
        "**AVOID WHEN:** Catching Error subclasses (OOM, "
        "StackOverflow) - these are unrecoverable\n"
        "**ANTI-PATTERN:** `catch (Exception e) { /* ignore */ }` "
        "- swallowing exceptions hides bugs permanently\n"
        "**TRADE-OFF:** Type-safe error handling vs class "
        "proliferation and hierarchy complexity\n"
        "**ONE-LINER:** \"Error = JVM dying, RuntimeException = "
        "your bug, checked Exception = expected failure\""
    ),
    "Checked vs Unchecked Exceptions": (
        "**WHAT IT IS:** Checked: compiler-enforced handling. "
        "Unchecked: optional handling (RuntimeException subtypes)\n"
        "**PROBLEM IT SOLVES:** Forces callers to acknowledge "
        "recoverable failure scenarios at compile time\n"
        "**KEY INSIGHT:** Modern practice uses checked only at "
        "system boundaries; Spring/Hibernate wrap everything "
        "in unchecked\n"
        "**USE WHEN:** Checked: IO/network where recovery is "
        "possible. Unchecked: programming errors, validation\n"
        "**AVOID WHEN:** Checked exceptions in lambda/stream code "
        "- they break functional composition\n"
        "**ANTI-PATTERN:** Catching checked exceptions and "
        "rethrowing as RuntimeException without cause chaining\n"
        "**TRADE-OFF:** Compile-time safety vs leaking "
        "implementation details and lambda incompatibility\n"
        "**ONE-LINER:** \"Checked = must handle or declare. "
        "Unchecked = handle if you can. Modern: unchecked by "
        "default.\""
    ),
    "Try-with-Resources": (
        "**WHAT IT IS:** Language construct that auto-closes "
        "AutoCloseable resources when scope exits\n"
        "**PROBLEM IT SOLVES:** Eliminates resource leaks from "
        "forgotten close() calls in finally blocks\n"
        "**KEY INSIGHT:** Handles suppressed exceptions - if both "
        "try and close() throw, neither is lost\n"
        "**USE WHEN:** Any resource that implements AutoCloseable: "
        "streams, connections, locks, channels\n"
        "**AVOID WHEN:** Resource lifetime extends beyond a single "
        "method scope (use explicit lifecycle management)\n"
        "**ANTI-PATTERN:** Using try-finally instead of "
        "try-with-resources - verbose and error-prone\n"
        "**TRADE-OFF:** Automatic cleanup vs resource must "
        "implement AutoCloseable and scope must be lexical\n"
        "**ONE-LINER:** \"Declare resources in try() - guaranteed "
        "close in reverse order, even on exception\""
    ),
    "IO Streams": (
        "**WHAT IT IS:** Byte (InputStream/OutputStream) and "
        "character (Reader/Writer) stream abstractions for IO\n"
        "**PROBLEM IT SOLVES:** Uniform API for reading/writing "
        "files, network, memory, and other byte/char sources\n"
        "**KEY INSIGHT:** Decorator pattern - wrap streams to add "
        "buffering, filtering, data types, compression\n"
        "**USE WHEN:** File IO, network communication, "
        "serialization, any byte/character processing\n"
        "**AVOID WHEN:** Large files where memory-mapping (NIO) "
        "or streaming (Files.lines()) is more efficient\n"
        "**ANTI-PATTERN:** Forgetting BufferedInputStream - "
        "unbuffered file IO is 10-100x slower\n"
        "**TRADE-OFF:** Flexible composition via decoration vs "
        "wrapper overhead and synchronization cost\n"
        "**ONE-LINER:** \"Wrap to compose: FileIn -> BufferedIn "
        "-> DataIn. Always buffer, always close.\""
    ),
    "NIO and NIO.2": (
        "**WHAT IT IS:** Non-blocking IO with Channels, Buffers, "
        "Selectors (NIO) plus Path/Files API (NIO.2)\n"
        "**PROBLEM IT SOLVES:** Handles thousands of concurrent "
        "connections with few threads via IO multiplexing\n"
        "**KEY INSIGHT:** One Selector thread monitors thousands "
        "of channels - OS does the waiting, not Java threads\n"
        "**USE WHEN:** High-connection-count servers (>1K), "
        "memory-mapped files, async file operations\n"
        "**AVOID WHEN:** Simple file IO (use Files API) or with "
        "Java 21+ virtual threads (simpler blocking code scales)\n"
        "**ANTI-PATTERN:** Using raw NIO Selectors when Netty or "
        "virtual threads provide simpler, safer alternatives\n"
        "**TRADE-OFF:** Scalability to 10K+ connections vs "
        "complex state machines and buffer management\n"
        "**ONE-LINER:** \"Channel + Buffer + Selector = scalable "
        "IO. But prefer virtual threads (Java 21+) for simplicity\""
    ),
}

COMPARISON = {
    "Exception Hierarchy": (
        "| Aspect | Checked Exception | RuntimeException | "
        "Error |\n"
        "|--------|------------------|-----------------|"
        "------|\n"
        "| Extends | Exception | RuntimeException | Error |\n"
        "| Compiler enforced | Yes (must catch/declare) | No | "
        "No |\n"
        "| Recoverable | Usually yes | Usually no (bug) | "
        "No (JVM) |\n"
        "| Example | IOException, SQLException | "
        "NullPointerException | OutOfMemoryError |\n"
        "| When to use | External failures (IO, network) | "
        "Programming errors | Never throw manually |"
    ),
    "Checked vs Unchecked Exceptions": (
        "| Aspect | Checked | Unchecked |\n"
        "|--------|---------|----------|\n"
        "| Compiler enforcement | Must catch or declare | "
        "Optional |\n"
        "| Lambda compatible | No (breaks streams) | Yes |\n"
        "| API coupling | Tight (leaks impl details) | "
        "Loose |\n"
        "| Recovery expectation | Caller should handle | "
        "Fix the bug |\n"
        "| Modern frameworks | Avoided (Spring wraps) | "
        "Preferred |\n"
        "| Examples | IOException, SQLException | "
        "IllegalArgumentException, NPE |"
    ),
    "Try-with-Resources": (
        "| Aspect | Try-with-Resources | Try-Finally | "
        "Manual close() |\n"
        "|--------|-------------------|------------|"
        "---------------|\n"
        "| Resource leak risk | None | Low (if correct) | "
        "High |\n"
        "| Suppressed exceptions | Handled automatically | "
        "Must code manually | Lost |\n"
        "| Lines of code | ~5 | ~15-25 | ~3 (unsafe) |\n"
        "| Multiple resources | Declare in same try() | "
        "Nested try-finally | Error-prone |\n"
        "| Null safety | Built-in | Must check | Must check |"
    ),
    "IO Streams": (
        "| Aspect | InputStream/OutputStream | Reader/Writer | "
        "NIO Channel |\n"
        "|--------|------------------------|-------------|"
        "------------|\n"
        "| Unit | Bytes | Characters | Bytes (Buffer) |\n"
        "| Encoding | None (raw bytes) | Charset-aware | "
        "Manual |\n"
        "| Blocking | Yes | Yes | "
        "Configurable |\n"
        "| Buffering | Wrap in Buffered* | Wrap in Buffered* | "
        "ByteBuffer |\n"
        "| Use case | Binary data | Text data | "
        "High-performance |"
    ),
    "NIO and NIO.2": (
        "| Aspect | Old IO (java.io) | NIO (java.nio) | "
        "NIO.2 (java.nio.file) |\n"
        "|--------|-----------------|----------------|"
        "---------------------|\n"
        "| Blocking | Always | Configurable | Both |\n"
        "| Unit | Stream (byte/char) | Buffer | Buffer/Path |\n"
        "| File API | File | FileChannel | Path/Files |\n"
        "| Multiplexing | No | Selector | "
        "AsynchronousChannel |\n"
        "| Memory mapping | No | MappedByteBuffer | "
        "MappedByteBuffer |\n"
        "| Use case | Simple IO | Network servers | "
        "File operations |"
    ),
}

MISCONCEPTIONS = {
    "Exception Hierarchy": [
        ("Errors should be caught and handled",
         "Errors (OutOfMemoryError, StackOverflowError) indicate "
         "JVM-level failures. Catching them is almost never "
         "correct - the JVM may be in an inconsistent state."),
        ("RuntimeException means 'runtime only'",
         "All exceptions occur at runtime. 'Runtime' means "
         "'unchecked by the compiler.' The name is about compiler "
         "behavior, not when the exception happens."),
        ("Custom exceptions should always extend Exception",
         "Extend RuntimeException for programming errors and "
         "validation failures. Extend Exception (checked) only "
         "for recoverable failures at system boundaries."),
        ("More exception types means better error handling",
         "Excessive exception hierarchy creates catch-block "
         "proliferation. One custom exception per module "
         "boundary with error codes is often cleaner."),
    ],
    "Checked vs Unchecked Exceptions": [
        ("Checked exceptions guarantee error handling",
         "Developers often write `catch (Exception e) {}` to "
         "satisfy the compiler, which is worse than no checking "
         "at all - the error is silently swallowed."),
        ("Unchecked exceptions mean 'don't handle'",
         "Unchecked just means the compiler doesn't force handling. "
         "You should still catch where recovery is possible "
         "(e.g., validation errors at API boundaries)."),
        ("Converting checked to unchecked is always wrong",
         "Frameworks like Spring, Hibernate, and Java NIO.2 "
         "intentionally wrap checked in unchecked to improve API "
         "ergonomics. This is a design choice, not an anti-pattern."),
        ("throws clause documents all possible exceptions",
         "`throws` only declares checked exceptions. A method can "
         "throw any unchecked exception without declaring it. "
         "Use Javadoc `@throws` for significant unchecked cases."),
    ],
    "Try-with-Resources": [
        ("try-with-resources can only have one resource",
         "Multiple resources can be declared separated by "
         "semicolons: `try (var a = ...; var b = ...)`. They "
         "close in reverse declaration order."),
        ("The resource variable must be declared in the try()",
         "Since Java 9, effectively final variables declared "
         "outside can be used: `var r = new Resource(); try (r)`. "
         "No need to re-declare."),
        ("close() exceptions replace the original exception",
         "Try-with-resources adds close() exceptions as "
         "'suppressed' on the original. Both are preserved and "
         "accessible via `getSuppressed()`."),
        ("try-with-resources eliminates all resource leaks",
         "Only if the resource is actually declared in the try(). "
         "A resource created and passed to another method without "
         "try-with-resources can still leak."),
    ],
    "IO Streams": [
        ("BufferedReader is always better than unbuffered",
         "For random-access patterns (seek then read small chunk), "
         "buffering wastes memory pre-reading data you won't use. "
         "For sequential reading, always buffer."),
        ("InputStream and Reader are interchangeable",
         "InputStream handles raw bytes. Reader handles characters "
         "with charset decoding. Mixing them without "
         "`InputStreamReader` corrupts multi-byte characters."),
        ("Files.readAllBytes() is fine for any file size",
         "It loads the entire file into memory. For a 2GB file, "
         "it needs 2GB of heap. Use streaming APIs (Files.lines() "
         "or BufferedReader) for large files."),
        ("Closing the outermost wrapper closes all inner streams",
         "This is usually true for decorator chains, but not "
         "guaranteed by the API contract. Always use "
         "try-with-resources on the outermost wrapper."),
    ],
    "NIO and NIO.2": [
        ("NIO is always faster than old IO",
         "For simple sequential file reads, old IO with buffering "
         "is comparable or faster. NIO's advantage is "
         "multiplexing (many connections, few threads)."),
        ("ByteBuffer is like a byte array",
         "ByteBuffer has position, limit, and capacity state. "
         "Forgetting `flip()` after writing is the #1 NIO bug - "
         "you read garbage instead of your data."),
        ("NIO replaces java.io completely",
         "NIO.2's Path/Files API replaces java.io.File, but "
         "InputStream/Reader are still used for streaming. NIO "
         "Channels and Selectors serve different use cases."),
        ("Memory-mapped files are always better for large files",
         "Mapped files consume virtual address space and can "
         "cause unpredictable page faults. For sequential reads, "
         "buffered streaming is simpler and equally fast."),
    ],
}

FAILURES = {
    "Exception Hierarchy": """**Failure Mode 1: Catching Exception swallows everything**
**Symptom:** Bugs silently disappear. Application produces wrong results with no errors logged.
**Root Cause:** `catch (Exception e) {}` or `catch (Exception e) { log.error(...) }` catches both business exceptions and programming bugs (NPE, ClassCast).
**Diagnostic:**

```
grep -rn 'catch.*Exception' src/ | grep -v 'IOException\\|SQLException'
# Find overly broad catch blocks
```

**Fix:**
```java
// BAD: catches everything
try { process(data); }
catch (Exception e) { log.error("Failed", e); }

// GOOD: catch specific exceptions
try { process(data); }
catch (IOException e) { return fallback(); }
// Let NPE, ClassCastException propagate
```
**Prevention:** Catch the most specific exception type. Never catch Exception in business logic.

**Failure Mode 2: Lost exception cause chain**
**Symptom:** Log shows "Processing failed" but no root cause or stack trace of the original error.
**Root Cause:** Rethrowing a new exception without setting the original as the cause.
**Diagnostic:**

```
grep -rn 'throw new.*Exception(' src/ | grep -v 'cause\\|, e)'
# Find throw-new without cause parameter
```

**Fix:**
```java
// BAD: loses original cause
catch (SQLException e) {
    throw new ServiceException("DB failed");
}

// GOOD: chain the cause
catch (SQLException e) {
    throw new ServiceException("DB failed", e);
}
```
**Prevention:** Always pass the original exception as the cause parameter when wrapping.

**Failure Mode 3: Stack trace cost in hot path**
**Symptom:** Exception-heavy code path shows `Throwable.fillInStackTrace()` dominating CPU profiler.
**Root Cause:** Every `new Exception()` walks the entire call stack to capture the trace. In hot paths with deep stacks, this costs microseconds per exception.
**Diagnostic:**

```
asprof -e cpu -d 30 -f cpu.html <pid>
# Look for fillInStackTrace in hot methods
```

**Fix:**
```java
// BAD: exception for control flow
if (!valid) throw new ValidationException(msg);

// GOOD: use return values for expected cases
ValidationResult result = validate(input);
if (!result.isValid()) return error(result);

// Or: pre-allocated exception (rare cases only)
static final MyException INSTANCE = new MyException();
@Override
public Throwable fillInStackTrace() { return this; }
```
**Prevention:** Never use exceptions for control flow. Reserve exceptions for truly exceptional conditions.""",

    "Checked vs Unchecked Exceptions": """**Failure Mode 1: Checked exception leaking implementation details**
**Symptom:** Service interface declares `throws SQLException` - changing the DB implementation requires changing the interface.
**Root Cause:** Checked exceptions in the interface signature couple callers to a specific implementation technology.
**Diagnostic:**

```
grep -rn 'throws.*SQL\\|throws.*Hibernate' src/
# Find implementation-specific exceptions in interfaces
```

**Fix:**
```java
// BAD: leaks implementation
interface UserRepo {
    User find(int id) throws SQLException;
}

// GOOD: wrap at boundary
interface UserRepo {
    User find(int id); // throws unchecked
}
class JdbcUserRepo implements UserRepo {
    public User find(int id) {
        try { /* JDBC */ }
        catch (SQLException e) {
            throw new DataAccessException(e);
        }
    }
}
```
**Prevention:** Wrap checked exceptions at module boundaries into module-specific unchecked exceptions.

**Failure Mode 2: Empty catch block hiding failures**
**Symptom:** Application silently produces wrong output. No errors in logs. Works "most of the time."
**Root Cause:** Developer added empty catch to satisfy compiler, intending to fix later.
**Diagnostic:**

```
grep -A1 'catch.*Exception' src/**/*.java | grep -B1 '^\s*}'
# Find catch blocks with empty or near-empty bodies
```

**Fix:**
```java
// BAD: silent swallowing
try { sendEmail(user); }
catch (MessagingException e) { }

// GOOD: at minimum, log. Preferably handle.
try { sendEmail(user); }
catch (MessagingException e) {
    log.warn("Email failed for user={}", user.id(), e);
    metrics.increment("email.failure");
}
```
**Prevention:** Static analysis rules (SonarQube, Error Prone) that flag empty catch blocks.

**Failure Mode 3: Wrapping without cause in lambda**
**Symptom:** Stack trace shows `UncheckedIOException` or `RuntimeException` but root cause is missing.
**Root Cause:** Lambda wraps checked exception in unchecked but forgets the cause parameter.
**Diagnostic:**

```
grep -rn 'RuntimeException(' src/ | grep -v ', e)\\|, ex)'
# Find RuntimeException without cause
```

**Fix:**
```java
// BAD: loses cause
.map(path -> {
    try { return Files.readString(path); }
    catch (IOException e) {
        throw new RuntimeException("failed"); // no cause!
    }
})

// GOOD: preserve cause
.map(path -> {
    try { return Files.readString(path); }
    catch (IOException e) {
        throw new UncheckedIOException(e); // cause preserved
    }
})
```
**Prevention:** Always pass the original exception to the wrapping constructor.""",

    "Try-with-Resources": """**Failure Mode 1: Resource created outside try-with-resources**
**Symptom:** Resource leak under exception conditions. Connection pool exhaustion after hours.
**Root Cause:** Resource created before the try block - if an exception occurs between creation and try, close() never runs.
**Diagnostic:**

```
grep -B2 'try (' src/**/*.java | grep 'new.*Stream\\|new.*Connection'
# Find resources created before try()
```

**Fix:**
```java
// BAD: leak if getConnection() succeeds
// but prepareStatement() fails
Connection conn = ds.getConnection();
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    // conn is NOT managed by try-with-resources!
}

// GOOD: manage all resources
try (Connection conn = ds.getConnection();
     PreparedStatement ps = conn.prepareStatement(sql)) {
    // both managed
}
```
**Prevention:** Declare ALL resources in the try() parentheses.

**Failure Mode 2: Suppressed exception lost in logging**
**Symptom:** close() throws but the suppressed exception is never logged; only the primary exception appears.
**Root Cause:** Logging framework prints the primary exception's stack trace but not its suppressed exceptions.
**Diagnostic:**

```
jshell> try { throw new IOException("primary"); }
...> catch (Exception e) {
...>     for (var s : e.getSuppressed())
...>         System.out.println("Suppressed: " + s);
...> }
```

**Fix:**
```java
// BAD: only logs primary
catch (Exception e) {
    log.error("Failed", e); // suppressed not shown
}

// GOOD: log suppressed too
catch (Exception e) {
    log.error("Failed", e);
    for (Throwable s : e.getSuppressed()) {
        log.warn("Suppressed during close", s);
    }
}
```
**Prevention:** Configure logging to include suppressed exceptions. Use structured logging.

**Failure Mode 3: AutoCloseable not implemented correctly**
**Symptom:** Custom resource is used in try-with-resources but cleanup doesn't happen or throws unexpectedly.
**Root Cause:** `close()` is not idempotent - calling it twice throws, or it doesn't actually release the resource.
**Diagnostic:**

```
# Test idempotency
jshell> var r = new MyResource();
jshell> r.close(); r.close(); // should not throw
```

**Fix:**
```java
// BAD: not idempotent
public void close() {
    handle.release(); // throws if already released!
}

// GOOD: idempotent close
private boolean closed = false;
public void close() {
    if (!closed) {
        handle.release();
        closed = true;
    }
}
```
**Prevention:** Make close() idempotent. Track closed state. Test double-close scenarios.""",

    "IO Streams": """**Failure Mode 1: Charset corruption from default encoding**
**Symptom:** Characters appear as `?`, `???`, or garbled text. Works on developer's machine but fails on server.
**Root Cause:** Using `new FileReader(file)` or `new InputStreamReader(fis)` without specifying charset. Default charset varies by OS/locale.
**Diagnostic:**

```
grep -rn 'new FileReader\\|new InputStreamReader(' src/
# Check for missing charset parameter
```

**Fix:**
```java
// BAD: platform-dependent encoding
Reader r = new FileReader("data.csv");

// GOOD: explicit charset
Reader r = new FileReader("data.csv",
    StandardCharsets.UTF_8);
// Or better:
BufferedReader br = Files.newBufferedReader(
    Path.of("data.csv"), StandardCharsets.UTF_8);
```
**Prevention:** Always specify `StandardCharsets.UTF_8` explicitly. Never rely on default charset.

**Failure Mode 2: OutOfMemoryError from reading entire file**
**Symptom:** OOM when processing a large file. Heap dump shows giant `byte[]` or `char[]`.
**Root Cause:** Using `Files.readAllBytes()` or `readAllLines()` on a multi-GB file.
**Diagnostic:**

```
grep -rn 'readAllBytes\\|readAllLines\\|readString' src/
# Check file sizes these methods are called on
```

**Fix:**
```java
// BAD: loads entire file into memory
byte[] data = Files.readAllBytes(hugePath);

// GOOD: stream line by line
try (Stream<String> lines = Files.lines(hugePath,
        StandardCharsets.UTF_8)) {
    lines.filter(l -> l.contains("ERROR"))
         .forEach(this::process);
}
```
**Prevention:** Use streaming APIs for files that could be large. Set size limits at input boundaries.

**Failure Mode 3: Resource leak from unclosed streams**
**Symptom:** "Too many open files" error after running for hours. `lsof` shows thousands of open file handles.
**Root Cause:** InputStream/OutputStream opened but never closed, especially in error paths.
**Diagnostic:**

```
lsof -p <pid> | wc -l
# Compare with ulimit -n to check proximity
```

**Fix:**
```java
// BAD: leak on exception
InputStream is = new FileInputStream(file);
byte[] data = is.readAllBytes();
is.close(); // never reached if readAllBytes throws

// GOOD: try-with-resources
try (InputStream is = new FileInputStream(file)) {
    byte[] data = is.readAllBytes();
}
```
**Prevention:** Always use try-with-resources for IO streams. Run leak detection tools (Eclipse MAT, VisualVM).""",

    "NIO and NIO.2": """**Failure Mode 1: ByteBuffer flip() forgotten**
**Symptom:** Channel.write() writes zero bytes or garbage. Buffer appears empty after filling it.
**Root Cause:** After writing to a buffer (put), `flip()` must be called to set position=0 and limit=position before reading. Without flip, position is at the end and limit is at capacity.
**Diagnostic:**

```
# Debug buffer state
System.out.println("pos=" + buf.position()
    + " lim=" + buf.limit()
    + " cap=" + buf.capacity());
# If pos == lim after put, flip was forgotten
```

**Fix:**
```java
// BAD: forgot flip
ByteBuffer buf = ByteBuffer.allocate(1024);
channel.read(buf);
// position is at end of data, limit at capacity
outChannel.write(buf); // writes 0 bytes!

// GOOD: flip before switching direction
ByteBuffer buf = ByteBuffer.allocate(1024);
channel.read(buf);
buf.flip(); // position=0, limit=bytes read
outChannel.write(buf);
buf.clear(); // reset for next read
```
**Prevention:** Rule: flip() after every direction change (read->write or write->read). Use `compact()` for partial reads.

**Failure Mode 2: Selector spin loop (100% CPU)**
**Symptom:** One CPU core at 100%. Thread dump shows thread spinning in `Selector.select()` returning 0.
**Root Cause:** Known JDK bug on Linux (epoll): cancelled key causes `select()` to return immediately with empty set indefinitely.
**Diagnostic:**

```
jstack <pid> | grep -A5 "Selector"
# Thread spinning in select() with no selected keys
```

**Fix:**
```java
// Detect and rebuild selector
int spins = 0;
while (true) {
    int n = selector.select(1000);
    if (n == 0 && ++spins > 512) {
        selector = rebuildSelector(selector);
        spins = 0;
    }
    // process selected keys...
}
// Netty handles this automatically
```
**Prevention:** Use Netty or another framework that handles the epoll spin bug. Avoid raw Selector usage.

**Failure Mode 3: MappedByteBuffer not released**
**Symptom:** File cannot be deleted or moved on Windows. "File is in use" error. Memory grows without bound.
**Root Cause:** `MappedByteBuffer` is not unmapped when the channel/file is closed. It relies on GC finalization, which is non-deterministic.
**Diagnostic:**

```
# Check for mapped regions
pmap <pid> | grep "mapped"
# On Windows: ProcessExplorer shows file handles
```

**Fix:**
```java
// BAD: buffer lives until GC
MappedByteBuffer buf = channel.map(
    READ_ONLY, 0, channel.size());
channel.close();
// buf still mapped! File locked on Windows.

// GOOD: use Cleaner (Java 9+) or avoid mapping
// For Java 9+:
((sun.misc.Unsafe) ...).invokeCleaner(buf);
// Better: use Files.readAllBytes for small files
// or BufferedReader for large files
```
**Prevention:** Avoid MappedByteBuffer on Windows. For cross-platform code, prefer streaming IO or `FileChannel.transferTo()`.""",
}

RELATED = {
    "Exception Hierarchy": """**Prerequisites (understand these first):**

- Object-oriented inheritance - exception types form a class hierarchy
- Stack traces - understanding how the JVM captures exception context

**Builds on this (learn these next):**

- Checked vs Unchecked Exceptions - the critical design decision in the hierarchy
- Try-with-Resources - modern exception-safe resource management

**Alternatives / Comparisons:**

- Rust Result<T,E> - algebraic error types instead of exception hierarchy
- Go error interface - simple error values without hierarchy""",

    "Checked vs Unchecked Exceptions": """**Prerequisites (understand these first):**

- Exception Hierarchy - understanding the Throwable class tree
- Method signatures and interfaces - how throws clauses affect contracts

**Builds on this (learn these next):**

- Spring exception translation - automatic checked-to-unchecked wrapping
- Lambda/Stream exception handling - working around checked exception limitations

**Alternatives / Comparisons:**

- Kotlin (no checked exceptions) - relies on documentation and nullability instead
- Result/Either types (Vavr) - type-safe error handling without exceptions""",

    "Try-with-Resources": """**Prerequisites (understand these first):**

- AutoCloseable interface - the contract for resources
- Exception handling basics - try/catch/finally mechanics

**Builds on this (learn these next):**

- Custom AutoCloseable implementations - writing your own managed resources
- Connection pooling - resources that return to pool instead of closing

**Alternatives / Comparisons:**

- Python `with` statement (context managers) - same RAII pattern
- Kotlin `use {}` - extension function equivalent of try-with-resources""",

    "IO Streams": """**Prerequisites (understand these first):**

- Byte and character encoding (UTF-8, ASCII) - foundation of IO correctness
- Decorator pattern - InputStream wrapping is the classic decorator example

**Builds on this (learn these next):**

- NIO and NIO.2 - non-blocking and memory-mapped alternatives
- Serialization - ObjectInputStream/ObjectOutputStream for Java objects

**Alternatives / Comparisons:**

- NIO Channels and Buffers - better for high-throughput or concurrent IO
- Files utility class (NIO.2) - simpler API for common file operations""",

    "NIO and NIO.2": """**Prerequisites (understand these first):**

- IO Streams - the blocking IO model that NIO improves upon
- Threading and concurrency - understanding why thread-per-connection doesn't scale

**Builds on this (learn these next):**

- Netty framework - production-grade NIO abstraction
- Virtual Threads (Java 21) - blocking IO that scales like NIO

**Alternatives / Comparisons:**

- Virtual Threads (Project Loom) - simpler blocking code with NIO-level scalability
- Netty/Vert.x - higher-level reactive frameworks built on NIO""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
