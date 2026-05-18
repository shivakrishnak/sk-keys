---
id: DSA-096
title: When HashMap Resizes and Latency Spikes - Quick Check
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-092, DSA-076
used_by: DSA-095
related: DSA-093, DSA-097
tags:
  - java
  - hashmap
  - diagnostic
  - quick-check
  - latency
  - operations
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 96
permalink: /technical-mastery/dsa/hashmap-latency-check/
---

## TL;DR

A five-step quick check for diagnosing HashMap-resize-
induced latency spikes: GC log pattern, JFR allocation
profile, pre-size calculation, verification, and
monitoring setup to prevent recurrence.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-096 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | java, HashMap, diagnostic, latency |
| **Prerequisites** | DSA-092, DSA-076 |

---

### TL;DR - The 5-Step Check

1. **GC log**: does latency spike match GC pause timing?
2. **JFR**: is HashMap.resize() at top of allocation profile?
3. **Code**: find all `new HashMap<>()` without initial capacity
4. **Fix**: apply pre-size formula `(n/0.75)+1`
5. **Monitor**: add Gauge metric on map size to catch unbounded growth

---

### Step 1 - GC Log Pattern Check

```bash
# Enable GC logging if not already enabled
# Add to JVM flags: -Xlog:gc*:file=gc.log:time,uptime

# Check: do latency spikes coincide with GC pauses?
# Look for Pause Young events during the spike window
grep "Pause Young" gc.log | awk '{print $1, $NF}'

# HashMap resize signature:
# Rapid succession of small pauses during startup/warm-up
# Pattern: pauses at roughly 2x intervals (resize doubling)
# Example output:
# [0.123s] Pause Young 12M->8M(32M) 8ms
# [0.187s] Pause Young 24M->16M(64M) 15ms
# [0.312s] Pause Young 48M->32M(128M) 28ms
# ^ Characteristic: pause sizes double, interval halves
```

---

### Step 2 - JFR Allocation Profile

```bash
# Start JFR allocation recording
jcmd <pid> JFR.start duration=60s \
  events=jdk.ObjectAllocationInNewTLAB,jdk.ObjectAllocationOutsideTLAB \
  filename=alloc.jfr

# Then trigger the suspected operation (cache warm-up, etc.)

# Dump the recording
jcmd <pid> JFR.dump filename=alloc.jfr

# Open in JDK Mission Control (JMC)
# Navigate: Events > Allocations > By Class
# Sort by: "Total Allocation" descending
# HashMap resize signature: "HashMap$Node[]" near top
# Stack trace shows: HashMap.resize() -> HashMap.put()
#                  -> YourCode.buildCache()
```

---

### Step 3 - Code Audit for Unspecified Capacity

```bash
# Find all HashMap/HashSet constructions without capacity
grep -rn "new HashMap<>()" src/ --include="*.java"
grep -rn "new HashSet<>()" src/ --include="*.java"
grep -rn "new LinkedHashMap<>()" src/ --include="*.java"

# Also check for putAll without pre-sizing
grep -rn "new HashMap<>(); .*putAll" src/ --include="*.java"

# Focus on: startup code, cache initialization,
#   batch processing methods, @PostConstruct methods
# Skip: trivial maps holding < 50 entries total
```

---

### Step 4 - Apply Pre-Sizing Fix

```java
// Formula: initialCapacity = (int)(expectedSize / 0.75) + 1

// Before (triggers multiple resizes for large maps):
Map<String, Product> catalog = new HashMap<>();
products.forEach(p -> catalog.put(p.getId(), p));

// After (zero resizes):
int size = products.size(); // know the size upfront
Map<String, Product> catalog =
    new HashMap<>((int)(size / 0.75) + 1);
products.forEach(p -> catalog.put(p.getId(), p));

// If size is only approximately known (e.g., DB query):
// Use upper bound * 1.1 for safety margin
int approxSize = estimatedCount * 11 / 10; // +10% buffer
Map<String, Product> catalog =
    new HashMap<>((int)(approxSize / 0.75) + 1);

// Verify: after building, log actual map size
log.debug("Catalog built: {} entries, capacity formula: {}",
    catalog.size(), (int)(catalog.size() / 0.75) + 1);
```

---

### Step 5 - Monitoring Setup to Prevent Recurrence

```java
// Add Micrometer gauge for large collections
// This catches unbounded growth AND resize issues
@PostConstruct
void registerMetrics() {
    Gauge.builder("product.catalog.size",
            productCatalog, Map::size)
        .description("Number of entries in product catalog")
        .register(meterRegistry);

    // Alert rule (Prometheus):
    // ALERT CatalogSizeUnexpected
    //   IF product_catalog_size > 1100000
    //   OR product_catalog_size < 900000
    //   FOR 5m
    //   LABELS { severity: "warning" }
    //   ANNOTATIONS { summary: "Catalog size outside bounds" }
}

// For collections that should be stable after init:
// verify size at startup and log a warning if unexpected
@PostConstruct
void verifyCatalogSize() {
    int size = catalog.size();
    if (size < EXPECTED_MIN || size > EXPECTED_MAX) {
        log.warn("Catalog size {} outside expected range [{},{}]",
            size, EXPECTED_MIN, EXPECTED_MAX);
    }
    log.info("Catalog initialized: {} entries", size);
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Pre-sizing is only for large maps" | Any map that will hold more than 12 entries (default threshold) benefits. For maps built in tight loops, even small saves add up |
| "One resize is acceptable" | Each resize allocates a new array (GC object) + copies all entries. Even one resize on a 500K-entry map is ~4MB allocation and ~500K iterations |

---

### Mastery Checklist

- [ ] Runs this 5-step check when diagnosing startup latency
- [ ] Has the pre-size formula memorized: (n/0.75)+1
- [ ] Adds collection size metrics to all production maps

---

### Interview Deep-Dive

**Q1 (Medium):** A service has 50ms latency at startup
for the first few requests. After warmup it's 5ms.
What could cause this and how do you investigate?

> Multiple candidates: JIT compilation (code isn't
> optimized yet), class loading, connection pool warmup,
> cache loading, or HashMap resize during initialization.
> 
> Narrow down:
> - JIT: latency improves gradually over first 100-1000
>   requests (typical JIT warmup curve)
> - Cache/HashMap: latency spike only during startup,
>   then immediately normal (not gradual)
> - Connection pool: initial requests take connection
>   acquisition time, then pool is warm
> 
> For HashMap specifically:
> - GC log: look for consecutive pauses at startup
> - JFR: allocation profile during the first 5 seconds
> - Code: @PostConstruct or ApplicationStartedEvent
>   building large collections
> 
> Fix: pre-size + move initialization to background
> (async cache warm-up) so first requests aren't blocked.
