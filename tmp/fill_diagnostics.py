#!/usr/bin/env python3
"""Fill TODO sections for Java - Diagnostics and Security.md (3 keywords)."""
import re

FILE = "interview/java/Java - Diagnostics and Security.md"

KEYWORDS = [
    "JVM Profiling and Diagnostic Tools",
    "Java Security Vulnerabilities",
    "GC Algorithm Selection Framework",
]

LEVEL5 = {
    "JVM Profiling and Diagnostic Tools": (
        "JVM diagnostics tools form a layered observability stack "
        "that mirrors the universal monitoring pyramid: metrics "
        "(JMX/MBeans), logs (GC logs, thread dumps), traces "
        "(async-profiler, JFR), and deep inspection (heap dumps, "
        "core dumps). The same layered approach appears in "
        "Kubernetes observability (Prometheus metrics, log "
        "aggregation, distributed tracing), database monitoring "
        "(pg_stat_statements, slow query log, EXPLAIN ANALYZE), "
        "and OS diagnostics (vmstat, strace, perf). The expert "
        "insight: production profiling requires sampling, not "
        "instrumentation. `async-profiler` uses OS signals "
        "(SIGPROF/perf_events) to sample at near-zero overhead "
        "(<1%), while instrumenting profilers (VisualVM's CPU "
        "profiler) add 10-50% overhead and skew results via "
        "observer effect. At extreme scale, the critical tool "
        "chain is: JFR (always-on recording) -> async-profiler "
        "(targeted deep dive) -> heap dump (OOM diagnosis) -> "
        "core dump (JVM crash analysis). If redesigning today, "
        "you would integrate JFR events with OpenTelemetry spans "
        "so a single flame graph shows both JVM internals and "
        "distributed call context.\n\n"
        "**Expert thinking cues:**\n"
        "- \"What's the overhead budget?\" - JFR <1%, "
        "async-profiler <2%, heap dump = full GC pause\n"
        "- \"Sampling or tracing?\" - sampling for CPU profiling, "
        "tracing for allocation/lock contention\n"
        "- \"Is this reproducible?\" - if not, use JFR continuous "
        "recording to capture when it happens"
    ),
    "Java Security Vulnerabilities": (
        "Java security vulnerabilities follow the same OWASP "
        "taxonomy as any web application: injection, broken "
        "authentication, sensitive data exposure, XXE, and "
        "deserialization attacks. The cross-domain insight: "
        "security vulnerabilities are always about untrusted "
        "input crossing a trust boundary without validation. "
        "Every security bug is a failure to validate at the "
        "boundary. Java's specific attack surface includes: "
        "deserialization (ObjectInputStream can instantiate any "
        "class on the classpath), reflection (bypasses access "
        "controls), JNDI (Log4Shell exploited JNDI lookup with "
        "attacker-controlled strings), and classpath manipulation "
        "(dependency confusion). At extreme scale, supply chain "
        "attacks (malicious Maven dependencies) are more dangerous "
        "than code vulnerabilities because they affect thousands "
        "of applications simultaneously. If redesigning today, you "
        "would make deserialization opt-in (allowlist classes), "
        "disable JNDI remote lookups by default, and require "
        "cryptographic signing of all dependencies.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Where does untrusted input enter?\" - every entry "
        "point is a potential attack surface\n"
        "- \"Is this deserializing user input?\" - if yes, it's "
        "probably exploitable\n"
        "- \"Are dependencies audited?\" - `mvn dependency:tree` "
        "and `npm audit` reveal transitive vulnerabilities"
    ),
    "GC Algorithm Selection Framework": (
        "GC algorithm selection is the JVM equivalent of choosing "
        "a database index strategy: the right choice depends on "
        "workload characteristics (throughput vs latency vs "
        "memory), and the wrong choice causes cascading "
        "performance failures. The same trade-off pattern appears "
        "in Linux schedulers (CFS vs SCHED_DEADLINE), database "
        "isolation levels (serializable vs read-committed), and "
        "network protocols (TCP vs UDP). The expert framework: "
        "G1 is the default for balanced workloads, ZGC for "
        "sub-millisecond pause requirements, Parallel GC for "
        "maximum throughput (batch processing), and Shenandoah "
        "for ultra-low latency on OpenJDK. At extreme scale, GC "
        "tuning is about understanding the generational hypothesis "
        "(most objects die young) and sizing generations to match "
        "your allocation profile. If redesigning today, you would "
        "make ZGC the default (it handles all workloads with "
        "sub-ms pauses and competitive throughput on modern "
        "hardware) and deprecate Parallel GC.\n\n"
        "**Expert thinking cues:**\n"
        "- \"What's the p99 latency requirement?\" - <10ms = ZGC, "
        "<200ms = G1, throughput-only = Parallel\n"
        "- \"How much heap?\" - <4GB = any GC works. >32GB = "
        "ZGC or Shenandoah to avoid long G1 mixed collections\n"
        "- \"What's the allocation rate?\" - high allocation "
        "stresses young gen. Tune `-Xmn` or let G1 auto-size."
    ),
}

QUICKREF = {
    "JVM Profiling and Diagnostic Tools": (
        "**WHAT IT IS:** Suite of tools for profiling, monitoring, "
        "and diagnosing JVM applications (JFR, async-profiler, "
        "jmap, jstack)\n"
        "**PROBLEM IT SOLVES:** Identifies CPU bottlenecks, memory "
        "leaks, thread deadlocks, and GC issues in production\n"
        "**KEY INSIGHT:** Use sampling profilers (async-profiler, "
        "JFR) in production - <2% overhead vs 10-50% for "
        "instrumentation\n"
        "**USE WHEN:** Performance degradation, OOM errors, "
        "thread hangs, latency spikes, capacity planning\n"
        "**AVOID WHEN:** Using instrumentation profilers in "
        "production - they skew results and impact performance\n"
        "**ANTI-PATTERN:** Profiling only in dev environment "
        "with synthetic data - production workloads are different\n"
        "**TRADE-OFF:** Diagnostic depth vs overhead and data "
        "volume. JFR is always-on; heap dump freezes the JVM\n"
        "**ONE-LINER:** \"async-profiler for CPU, JFR for "
        "everything, jmap for OOM, jstack for deadlocks\""
    ),
    "Java Security Vulnerabilities": (
        "**WHAT IT IS:** Common attack patterns against Java "
        "applications: injection, deserialization, XXE, SSRF, "
        "dependency exploits\n"
        "**PROBLEM IT SOLVES:** Understanding and preventing "
        "security breaches in Java backend systems\n"
        "**KEY INSIGHT:** Every vulnerability is untrusted input "
        "crossing a trust boundary without validation\n"
        "**USE WHEN:** Code review, security audits, incident "
        "response, dependency upgrades, threat modeling\n"
        "**AVOID WHEN:** Assuming frameworks handle all security - "
        "misconfiguration is the #1 vulnerability\n"
        "**ANTI-PATTERN:** Using `ObjectInputStream` on untrusted "
        "data - arbitrary code execution via gadget chains\n"
        "**TRADE-OFF:** Security controls vs development speed "
        "and user experience friction\n"
        "**ONE-LINER:** \"Never trust input, never deserialize "
        "untrusted data, always update dependencies\""
    ),
    "GC Algorithm Selection Framework": (
        "**WHAT IT IS:** Decision framework for choosing the right "
        "JVM garbage collector based on workload characteristics\n"
        "**PROBLEM IT SOLVES:** Matching GC behavior (pause time, "
        "throughput, memory) to application requirements\n"
        "**KEY INSIGHT:** G1 for balanced, ZGC for low latency, "
        "Parallel for max throughput, Shenandoah for OpenJDK "
        "ultra-low pause\n"
        "**USE WHEN:** Performance tuning, capacity planning, "
        "SLA compliance, choosing GC for new services\n"
        "**AVOID WHEN:** Over-tuning before measuring - default "
        "G1 is correct for most workloads\n"
        "**ANTI-PATTERN:** Tuning 50+ GC flags without "
        "understanding the workload - makes GC behavior fragile "
        "and non-portable\n"
        "**TRADE-OFF:** Low pause times (ZGC) vs maximum "
        "throughput (Parallel) vs balanced (G1)\n"
        "**ONE-LINER:** \"Start with G1 defaults, measure, switch "
        "to ZGC for latency or Parallel for batch\""
    ),
}

COMPARISON = {
    "JVM Profiling and Diagnostic Tools": (
        "| Tool | Purpose | Overhead | "
        "Production Safe |\n"
        "|------|---------|----------|"
        "----------------|\n"
        "| JFR | Always-on event recording | <1% | Yes |\n"
        "| async-profiler | CPU/alloc/lock sampling | <2% | "
        "Yes |\n"
        "| jstack | Thread dump snapshot | Pause | "
        "Yes (brief) |\n"
        "| jmap -histo | Object histogram | Brief pause | "
        "Caution |\n"
        "| jmap -dump | Full heap dump | Full GC pause | "
        "Emergency only |\n"
        "| VisualVM | GUI profiler | 10-50% | No (dev only) |"
    ),
    "Java Security Vulnerabilities": (
        "| Vulnerability | Attack Vector | "
        "Java Impact | Prevention |\n"
        "|--------------|--------------|"
        "------------|------------|\n"
        "| SQL Injection | User input in SQL | "
        "JDBC statements | Parameterized queries |\n"
        "| Deserialization | Untrusted ObjectInputStream | "
        "RCE via gadgets | Use JSON, allowlist |\n"
        "| XXE | XML parser with DTD | "
        "File read, SSRF | Disable DTD processing |\n"
        "| Log4Shell | JNDI lookup in log message | "
        "RCE | Update Log4j, disable JNDI |\n"
        "| Dependency exploit | Transitive vulnerable lib | "
        "Varies | Scan with OWASP, Snyk |"
    ),
    "GC Algorithm Selection Framework": (
        "| Aspect | G1 GC | ZGC | "
        "Parallel GC | Shenandoah |\n"
        "|--------|-------|-----|"
        "------------|------------|\n"
        "| Max pause | 200ms (target) | <1ms | "
        "Seconds | <10ms |\n"
        "| Throughput | Good | Good (JDK 21+) | "
        "Best | Good |\n"
        "| Min heap | ~4GB | ~256MB | Any | ~4GB |\n"
        "| CPU overhead | Medium | Higher | Lowest | Higher |\n"
        "| Default since | JDK 9 | No | JDK 1-8 | No |\n"
        "| Best for | General purpose | Latency-critical | "
        "Batch | OpenJDK latency |"
    ),
}

MISCONCEPTIONS = {
    "JVM Profiling and Diagnostic Tools": [
        ("Thread dumps are only for deadlocks",
         "Thread dumps reveal: deadlocks, lock contention, "
         "thread pool saturation, blocked IO, and CPU hotspots. "
         "Take 3-5 dumps 5 seconds apart to see patterns."),
        ("Heap dumps crash the application",
         "Heap dumps cause a full GC pause (seconds to minutes "
         "for large heaps) but don't crash the JVM. Schedule "
         "during maintenance windows for production."),
        ("JFR has significant overhead",
         "JFR was designed for always-on production use with "
         "<1% overhead. It's integrated into the JVM and uses "
         "thread-local buffers to minimize contention."),
        ("Profiling in dev is sufficient",
         "Dev environments have different data sizes, connection "
         "pools, thread counts, and GC behavior. Production "
         "profiling with JFR/async-profiler is essential."),
    ],
    "Java Security Vulnerabilities": [
        ("Using a framework prevents all vulnerabilities",
         "Frameworks prevent common attacks when configured "
         "correctly, but misconfiguration (disabled CSRF, open "
         "CORS) is the #1 cause of framework-based vulnerabilities."),
        ("SQL injection is a solved problem",
         "Parameterized queries prevent injection, but dynamic "
         "table/column names, native queries, and string-built "
         "criteria are still vulnerable."),
        ("HTTPS encrypts everything",
         "HTTPS encrypts transport but not the data at rest, "
         "in logs, or in error messages. Sensitive data can "
         "leak through logs, stack traces, and debug endpoints."),
        ("Updating dependencies is optional",
         "Log4Shell (CVE-2021-44228) affected millions of "
         "applications through a transitive dependency. Regular "
         "dependency scanning is a critical security practice."),
    ],
    "GC Algorithm Selection Framework": [
        ("G1 is always the best choice",
         "G1 struggles with very large heaps (>64GB) where mixed "
         "collections can exceed pause targets. ZGC handles "
         "multi-terabyte heaps with sub-ms pauses."),
        ("ZGC has lower throughput than G1",
         "Since JDK 21, ZGC (generational mode) achieves "
         "throughput within 5% of G1 for most workloads while "
         "maintaining sub-ms pauses."),
        ("More GC tuning flags means better performance",
         "Over-tuning creates fragile configurations that break "
         "when workload changes. Start with defaults, measure, "
         "and tune only the 2-3 most impactful parameters."),
        ("GC pause time = total application impact",
         "GC impact includes: pause time + CPU stolen for "
         "concurrent work + allocation stalls + reference "
         "processing. Total GC overhead is more than pause time."),
    ],
}

FAILURES = {
    "JVM Profiling and Diagnostic Tools": r"""**Failure Mode 1: SafePoint bias in profiling**
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
**Prevention:** Set timeouts on ALL external calls. Monitor connection pool usage. Take 3-5 thread dumps 5 seconds apart to see patterns.""",

    "Java Security Vulnerabilities": r"""**Failure Mode 1: SQL Injection via string concatenation**
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
**Prevention:** Disable DTD processing in all XML parsers. Use JAXB or JSON where possible.""",

    "GC Algorithm Selection Framework": r"""**Failure Mode 1: Wrong GC for latency-sensitive service**
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
**Prevention:** Profile allocation rate with async-profiler. Set allocation rate alerts. Size young gen to survive between GC cycles.""",
}

RELATED = {
    "JVM Profiling and Diagnostic Tools": r"""**Prerequisites (understand these first):**

- JVM memory model - understanding heap, stack, and metaspace layout
- Threading basics - thread states (RUNNABLE, WAITING, BLOCKED)

**Builds on this (learn these next):**

- GC Algorithm Selection - use profiling data to choose and tune GC
- Observability and SRE - integrating JVM metrics into monitoring systems

**Alternatives / Comparisons:**

- OpenTelemetry - distributed tracing across services (complements JVM tools)
- Datadog/New Relic APM - commercial tools with JVM agent instrumentation""",

    "Java Security Vulnerabilities": r"""**Prerequisites (understand these first):**

- HTTP and APIs - understanding request/response and input handling
- Exception handling - proper error responses without information leakage

**Builds on this (learn these next):**

- Spring Security - framework-level security controls
- OAuth2/OIDC - authentication and authorization protocols

**Alternatives / Comparisons:**

- OWASP ZAP/Burp Suite - dynamic security testing tools
- SonarQube/Snyk - static analysis and dependency vulnerability scanning""",

    "GC Algorithm Selection Framework": r"""**Prerequisites (understand these first):**

- JVM Memory Model - understanding heap generations and object lifecycle
- JVM Profiling Tools - how to measure GC behavior and impact

**Builds on this (learn these next):**

- GC Tuning - advanced flag tuning for specific workloads
- JFR GC analysis - using Flight Recorder to diagnose GC issues

**Alternatives / Comparisons:**

- Manual memory management (Rust, C++) - no GC overhead but developer burden
- Off-heap storage (Chronicle, Memcached) - bypass GC for large data sets""",
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
