---
id: OSY-029
title: Race Condition and Critical Section
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-007, OSY-017
used_by: OSY-038, OSY-042
related: OSY-027, OSY-030, OSY-038
tags:
  - race-condition
  - critical-section
  - concurrency
  - atomicity
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/osy/race-condition-critical-section/
---

## TL;DR

A race condition occurs when program correctness depends
on thread execution timing. The critical section is the
code region accessing shared data that must execute
atomically. Protection: mutexes, atomic variables, or
lock-free algorithms. Detection: ThreadSanitizer.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-029 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | race condition, critical section, atomicity |
| **Prerequisites** | OSY-007, OSY-017 |

---

### The Problem This Solves

Multiple threads operating on shared data produce
incorrect results when accesses interleave without
synchronization. A "read-modify-write" operation that
appears atomic in source code is typically 3+ CPU
instructions, all of which can be interleaved with
other threads.

---

### Why Races Happen (Hardware Level)

```
// Java code: balance -= withdrawal;
// Compiles to 3 CPU instructions:

LOAD  R1, [balance_addr]    ; load current balance
SUB   R1, R1, withdrawal    ; compute new balance
STORE [balance_addr], R1    ; write back

// Thread interleave scenario:
Time  Thread 1                  Thread 2
 1    LOAD R1 = 1000            
 2                              LOAD R2 = 1000
 3    SUB R1 = 1000 - 200 = 800
 4                              SUB R2 = 1000 - 300 = 700
 5    STORE balance = 800       
 6                              STORE balance = 700

// Expected: 1000 - 200 - 300 = 500
// Actual:   700 (Thread 1's update lost!)
// This is called a "lost update" race condition
```

---

### Critical Section Definition and Properties

```
Critical Section: code region that accesses shared 
mutable data and must not be concurrently executed
by multiple threads.

Three required properties (Dijkstra 1965):
  1. Mutual Exclusion: only ONE thread in CS at a time
  2. Progress: if no thread is in CS and some want to
     enter, one must eventually be allowed in
  3. Bounded Waiting: a thread waiting to enter must
     eventually get in (no starvation)

CS structure:
  entry section   -> acquire lock
  critical section -> access/modify shared data
  exit section    -> release lock
  remainder section -> everything else
```

---

### Race Condition Examples and Fixes

```java
// BAD: race condition on counter
public class RacyCounter {
    private int count = 0;  // shared mutable state
    
    // NOT thread-safe: 3 instructions (load, add, store)
    public void increment() {
        count++;  // race condition!
    }
    
    public int getCount() {
        return count;  // may read stale value!
    }
}
// Two threads calling increment() 500,000 times each
// Expected: 1,000,000; Actual: 700,000 to 1,000,000 (random)

// GOOD OPTION 1: synchronized (mutex-based critical section)
public class SynchronizedCounter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;  // only one thread at a time
    }
    
    public synchronized int getCount() {
        return count;  // reads consistent value
    }
}

// GOOD OPTION 2: AtomicInteger (lock-free, CAS-based)
public class AtomicCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();  // single atomic CAS instruction
    }
    
    public int getCount() {
        return count.get();  // always reads current value
    }
}
// AtomicInteger: 2-5x faster than synchronized for single variable
// synchronized: better when protecting multiple fields together
```

---

### Java Memory Model and Visibility Races

```java
// Visibility race: not just atomicity!
// Problem: thread 2 may cache 'running' in register
// and never see thread 1's write to memory

// BAD: missing volatile
public class VisibilityRace {
    private boolean running = true;  // no visibility guarantee
    
    public void stop() {
        running = false;  // thread 1 writes
    }
    
    public void run() {
        while (running) {  // thread 2 may loop forever!
            // Java compiler/JIT can hoist this check
            // out of loop if no volatile/sync
            doWork();
        }
    }
}

// GOOD: volatile ensures visibility
public class VisibilitySafe {
    private volatile boolean running = true;
    // volatile: writes immediately visible to all threads
    // No caching of volatile variables in registers
    
    public void stop() {
        running = false;  // all threads see this immediately
    }
    
    public void run() {
        while (running) {  // always reads from memory
            doWork();
        }
    }
}
// volatile: visibility only (not atomicity)
// Use for: flags, shutdown signals, one-write/many-read patterns
// NOT sufficient for: count++ (read-modify-write sequences)
```

---

### Check-Then-Act Race Pattern

```java
// BAD: check-then-act race (common in production bugs)
public class LazyCacheRace {
    private ExpensiveObject cache = null;
    
    // Race: two threads both see null, both create object
    public ExpensiveObject get() {
        if (cache == null) {         // check
            cache = new ExpensiveObject();  // act
        }
        return cache;
    }
}

// GOOD: double-checked locking with volatile
public class LazyCacheSafe {
    private volatile ExpensiveObject cache = null;
    
    public ExpensiveObject get() {
        if (cache == null) {  // outer check (no lock)
            synchronized (this) {
                if (cache == null) {  // inner check (with lock)
                    cache = new ExpensiveObject();
                }
            }
        }
        return cache;
    }
}
// volatile: ensures cache's fields are visible after creation
// synchronized: mutual exclusion for the initialization
```

---

### Detecting Race Conditions

```bash
# Method 1: ThreadSanitizer (native code, C/C++/Go)
g++ -fsanitize=thread -g my_program.cpp
./a.out
# Outputs: race condition with stack traces

# Method 2: Java - helgrind via Valgrind
valgrind --tool=helgrind java -cp . MyClass

# Method 3: Java - stress testing
# Run concurrent operations many times and check invariants
# Use: java -XX:+UseCompressedOops under load

# Method 4: Code review pattern
# Look for: field without volatile/synchronized,
#           count++ or similar RMW operations,
#           if (x == null) { x = new X(); } patterns
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "volatile makes operations atomic" | volatile only guarantees visibility (writes are immediately visible to other threads). It does NOT make compound operations (count++, check-then-act) atomic. Use AtomicInteger for atomic compound operations |
| "synchronized is always the right fix for races" | synchronized works but can create contention. For simple counters: AtomicInteger (lock-free CAS) is 2-5x faster. For complex multi-step operations: synchronized is appropriate |
| "Race conditions always produce wrong answers" | Race conditions can also cause: infinite loops (visibility race in while(flag) loop), NullPointerException (partially-constructed objects), stale reads (reads from CPU cache instead of memory) |

---

### Failure Modes and Diagnosis

```
Symptom 1: Lost updates (counter lower than expected)
  Diagnosis: multiple writers to same field without sync
  Fix: AtomicLong or synchronized method

Symptom 2: Application hangs in while loop forever
  Diagnosis: visibility race on boolean flag (missing volatile)
  Fix: add volatile to flag variable

Symptom 3: NullPointerException on object that "should be set"
  Diagnosis: partially constructed object published unsafely
  (object reference set before constructor completes)
  Fix: declare field volatile or use synchronized publication
  
Symptom 4: Inconsistent reads in financial calculations
  Diagnosis: check-then-act pattern without atomicity
  Fix: synchronize the entire check-and-act block

Security consideration:
  Race conditions in file operations = TOCTOU
  (Time Of Check To Time Of Use) vulnerability
  Check: File.exists() then File.delete()
  Attack: replace file between check and use
  Fix: use atomic file operations (Files.move with
       StandardCopyOption.ATOMIC_MOVE)
```

---

### Related Keywords

**Builds on:** OSY-007 (Thread vs Process), OSY-017 (Mutex)

**Related:** OSY-027 (Deadlock), OSY-030 (Mutex vs
Semaphore vs Monitor), OSY-038 (Thread-Safe Programming)

---

### Quick Reference Card

| Concept | Java Solution | Use When |
|---------|--------------|---------|
| Atomicity race | AtomicInteger/Long | Single variable RMW |
| Multi-field atomicity | synchronized block | Multiple fields together |
| Visibility race | volatile | Flag variables, one writer |
| Check-then-act | synchronized method | Any compound condition |
| Lock-free complex | java.util.concurrent | High-concurrency collections |

---

### Interview Deep-Dive

**Q1 (Easy): What is the difference between a race
condition and a data race?**
Data race: two threads access the same memory location
without synchronization (at least one write). Race
condition: program outcome depends on timing/ordering
of operations. All data races are race conditions but
not all race conditions involve data races (e.g.,
check-then-act is a race condition but protected memory
accesses can still have check-then-act logic faults).

**Q2 (Medium): Why is count++ not thread-safe in Java
even though it looks like one operation?**
Java source `count++` compiles to 3 bytecode operations:
GETFIELD (load), IADD (increment), PUTFIELD (store).
The JVM can context-switch between any two of these.
Two threads: both read the same value, both increment
to the same result, one write overwrites the other.
Lost update. Fix: AtomicInteger.incrementAndGet() uses
CAS (compare-and-swap), which is a single atomic
hardware instruction.

**Q3 (Hard): You're debugging a NullPointerException
that only occurs under high load. The field appears
non-null in all code paths. What could cause this?**
Unsafe object publication race: Thread 1 creates an
object and stores its reference; Thread 2 reads the
reference but may see a partially-constructed object
because the constructor writes may not be visible
(JIT reordering + no memory barrier). Fix: declare
the field final (final fields are guaranteed visible
after constructor) or volatile (writes establish
happens-before). Also possible: lazy initialization
race (double-checked locking without volatile).
