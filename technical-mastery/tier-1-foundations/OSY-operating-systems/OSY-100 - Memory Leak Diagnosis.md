---
id: OSY-100
title: Memory Leak Diagnosis
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-012, OSY-054, OSY-070, OSY-085, OSY-091
used_by: []
related: OSY-099, OSY-101, OSY-109
tags:
  - memory-leak
  - diagnosis
  - JVM
  - heap-dump
  - native-memory
  - production
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 100
permalink: /technical-mastery/osy/memory-leak-diagnosis/
---

## TL;DR

Memory leaks occur when allocated memory is never freed.
JVM leaks: objects retained in heap but never reachable (GC
cannot collect). Native leaks: off-heap, JNI, or Metaspace
growth. Diagnosis path: confirm leak (RSS growth), locate
source (heap dump, MAT, native profiler). Fix: remove retention,
tune Metaspace, fix native allocations.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-100 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | memory leak, heap dump, MAT, native memory, Metaspace, diagnosis |
| **Prerequisites** | OSY-012, OSY-054, OSY-070, OSY-085, OSY-091 |

---

### Confirming a Memory Leak

```
Step 1: Distinguish leak from normal memory growth
  
  Normal patterns:
    JVM RSS grows at startup (demand paging, AlwaysPreTouch effect)
    JVM RSS grows with load (more objects = more GC regions used)
    JVM RSS stable or slowly decreasing when idle (GC returning)
    
  Leak pattern:
    RSS grows continuously over hours/days without stabilizing
    Even after periods of low load: RSS doesn't decrease
    GC runs but RSS keeps growing (after-GC heap size trending up)
    
  Measurement:
    # Watch RSS trend over time
    watch -n 30 'ps -p $PID -o pid,rss,vsz --no-headers'
    # rss: Resident Set Size in KB
    # Increasing over time without load increase = leak candidate
    
    # Better: graph it
    while true; do
      echo "$(date +%s) $(ps -p $PID -o rss= 2>/dev/null)"
      sleep 60
    done >> /tmp/memory_trend.txt
    # Plot the file: should plateau, not grow linearly
    
Step 2: Distinguish Java heap leak vs native memory leak
  
  Check JVM heap size vs RSS:
    jcmd $PID GC.heap_info
    # Shows: heap used / heap capacity
    
    ps -p $PID -o rss
    # RSS includes: heap + native + code cache + metaspace + threads
    
  If heap is growing:
    Java heap leak (objects not GC'd)
    GC stats: after-GC used heap trends upward
    
  If heap is stable but RSS grows:
    Native memory leak: Metaspace, code cache, JNI, direct buffers
    Native Memory Tracking (NMT) to diagnose
```

---

### Diagnosing Java Heap Leaks

```bash
# Method 1: GC logs trending
# Enable GC logs:
java -Xlog:gc*:file=/tmp/gc.log:time,uptime:filecount=5,filesize=10m \
     -jar application.jar

# After-GC heap size should be roughly stable across GCs
# If growing: heap leak
# grep "Heap after GC" /tmp/gc.log | tail -50

# Method 2: Heap dump analysis (definitive)
# Trigger heap dump (while app is running):
jcmd $PID GC.heap_dump /tmp/heap.hprof

# Or via JVM flag (on OutOfMemoryError):
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/ \
     -jar application.jar

# Analyze with Eclipse MAT (Memory Analyzer Tool):
# 1. Open heap.hprof in MAT
# 2. Run: "Leak Suspects Report" (automatic analysis)
# 3. Look for: "One instance of X occupies Y% of heap"
# 4. Dominator tree: shows what's holding most memory
# 5. Retained heap: transitive closure of what each object holds

# Method 3: Live heap histogram (no dump required)
jcmd $PID GC.class_histogram | head -30
# Shows: count and bytes per class
# Compare at two time points:
jcmd $PID GC.class_histogram > /tmp/hist_before.txt
# ... wait 10 minutes ...
jcmd $PID GC.class_histogram > /tmp/hist_after.txt
diff /tmp/hist_before.txt /tmp/hist_after.txt
# Growing class counts = leak candidates
```

---

### Common Java Leak Patterns

```java
// Leak Pattern 1: Static collections
public class MetricsRegistry {
    // Static: lives for JVM lifetime
    // If metrics are added but never removed: unbounded growth
    private static final Map<String, Metric> metrics =
        new HashMap<>();
    
    public static void register(String name, Metric m) {
        metrics.put(name, m);  // never removed!
    }
}

// Fix: use weak references or explicit deregistration
private static final Map<String, WeakReference<Metric>> metrics =
    new WeakHashMap<>();

// Leak Pattern 2: Listener/callback not unregistered
class EventBus {
    private final List<EventListener> listeners = new ArrayList<>();
    
    public void subscribe(EventListener listener) {
        listeners.add(listener);
    }
    // No unsubscribe: listeners held forever
    // Even if the component using this listener is "destroyed"
}

// Fix: provide and call unsubscribe(); use weak references
class EventBus {
    private final List<WeakReference<EventListener>> listeners =
        new CopyOnWriteArrayList<>();
}

// Leak Pattern 3: ThreadLocal not removed
class RequestContext {
    // ThreadLocal in thread pool: thread reused across requests
    // If not removed: context from request N visible in request N+1
    // AND: object stays in thread's map = leak
    private static final ThreadLocal<Context> ctx =
        new ThreadLocal<>();
    
    // BAD: set without remove
    public static void set(Context c) { ctx.set(c); }
    
    // GOOD: always remove in finally block
    public static void cleanup() { ctx.remove(); }
}
// Usage:
try {
    RequestContext.set(new Context(request));
    processRequest();
} finally {
    RequestContext.cleanup();  // CRITICAL: must remove
}
```

---

### Native Memory Leaks

```bash
# Native memory tracking (NMT)
# Start JVM with:
java -XX:NativeMemoryTracking=detail -jar application.jar

# Take baseline snapshot:
jcmd $PID VM.native_memory baseline

# ... wait some time ...

# Compare to baseline:
jcmd $PID VM.native_memory detail.diff

# Output sections:
# - Java Heap: JVM heap
# - Class: Metaspace
# - Thread: thread stacks
# - Code: JIT compiled code
# - GC: GC data structures
# - Compiler: JIT compilation buffers
# - Internal: JVM internals
# - Other: ?
# - Symbol: String pool, class names
# - Native Memory Tracking: NMT itself
# - Arena Chunk: malloc arenas
# - Unknown: untracked

# Common native leaks:
#   Metaspace: growing "Class" section = class loading leak
#   Code: growing "Code" section = JIT code cache filling up
#   Other: JNI native library allocation

# Metaspace leak (class loader leak):
jcmd $PID VM.classloaders  # show all classloaders
# Look for: many custom ClassLoader instances
# Each: holds its classes in Metaspace
# Fix: ensure classloaders are GC'd when not needed

# For C/C++ native library leaks:
# Use Valgrind (testing):
valgrind --leak-check=full --track-origins=yes java -jar app.jar

# Use Address Sanitizer (requires recompile of native lib):
# LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libasan.so.4 java ...
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Java doesn't have memory leaks because of GC" | Java has semantic leaks: objects that are REACHABLE by a reference chain but never used again. GC cannot collect reachable objects. Classic: static Map with entries never removed; listeners never unsubscribed; ThreadLocal never removed. These are Java's version of memory leaks. |
| "Java OutOfMemoryError always means a leak" | OOM can mean: (1) genuine leak, (2) heap too small for the workload, (3) GC overhead limit exceeded (too much time in GC vs little memory freed), (4) direct buffer exhaustion (not in -Xmx), (5) Metaspace full (different from heap). Diagnose with heap dump BEFORE concluding it's a leak. |
| "Heap dump analysis requires stopping the application" | `jcmd GC.heap_dump` pauses the JVM briefly (STW GC to get consistent snapshot) but doesn't require stopping the application. The pause is typically 1-10 seconds for a several-GB heap. In production, schedule this during low-traffic periods. |

---

### Failure Modes & Diagnosis

| Failure | Symptom | Diagnosis | Fix |
|---------|---------|-----------|-----|
| Java heap leak | RSS grows; OOM after hours/days | Heap dump -> MAT Leak Suspects | Remove retaining references |
| ThreadLocal leak | Thread pool threads accumulate state | Class histogram: Context objects count growing | Add ThreadLocal.remove() in finally |
| Classloader leak | Metaspace OOM after redeploys | NMT Class section growing; `jcmd VM.classloaders` | Fix ClassLoader lifecycle; use -XX:MaxMetaspaceSize |
| JNI native leak | RSS grows beyond heap+metaspace | NMT "Other" growing; Valgrind | Fix native code memory management |

---

### Quick Reference Card

| Task | Tool | Command |
|------|------|---------|
| Confirm leak (RSS trend) | ps | `watch 'ps -p PID -o rss'` |
| Live heap histogram | jcmd | `jcmd PID GC.class_histogram` |
| Heap dump | jcmd | `jcmd PID GC.heap_dump /tmp/heap.hprof` |
| Native memory tracking | jcmd + NMT | `jcmd PID VM.native_memory detail.diff` |
| Automatic leak report | MAT | Open hprof -> Leak Suspects |
| Classloader count | jcmd | `jcmd PID VM.classloaders` |
| OOM on crash | JVM flag | `-XX:+HeapDumpOnOutOfMemoryError` |
