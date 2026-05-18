---
id: OSY-061
title: Lock-Free Data Structures
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-023, OSY-024, OSY-059
used_by: OSY-062
related: OSY-062, OSY-063, OSY-094
tags:
  - lock-free
  - CAS
  - compare-and-swap
  - wait-free
  - ABA-problem
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/osy/lock-free-data-structures/
---

## TL;DR

Lock-free data structures use CAS (Compare-And-Swap)
hardware instructions instead of mutexes. No thread ever
blocks: if CAS fails, it retries. This eliminates mutex
overhead, priority inversion, and deadlock - but adds
complexity and the ABA problem. Java provides
`AtomicReference`, `ConcurrentLinkedQueue`, and `LongAdder`
as lock-free building blocks.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-061 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | CAS, lock-free, wait-free, ABA problem, AtomicReference |
| **Prerequisites** | OSY-023, OSY-024, OSY-059 |

---

### Lock-Free vs Wait-Free vs Obstruction-Free

```
Progress guarantees (from strongest to weakest):
  
  Wait-free:
    Every thread completes in bounded steps regardless of others
    No starvation EVER
    Hardest to implement
    Example: LMAX Disruptor's ring buffer reads
    
  Lock-free:
    System-wide progress guaranteed: at least ONE thread completes
    Individual threads CAN starve (but unlikely in practice)
    Most practical concurrent data structures aim here
    Examples: ConcurrentLinkedQueue, AtomicReference.compareAndSet()
    
  Obstruction-free:
    A thread makes progress if it runs alone
    Weakest useful guarantee
    
  Blocking (with mutex):
    No progress guarantee: holding thread can sleep/die
    Priority inversion, deadlock possible
    OS must be involved (context switch on contention)
    
Progress hierarchy:
  Wait-free -> Lock-free -> Obstruction-free -> Blocking
  (stronger guarantee requires more implementation complexity)
```

---

### CAS: The Hardware Primitive

```java
// Compare-And-Swap (CAS): atomic hardware instruction
// CMPXCHG on x86: single uninterruptible operation
//
// Pseudocode:
//   boolean CAS(address, expectedValue, newValue) {
//     lock the memory bus;  // or use cache coherence
//     if (memory[address] == expectedValue) {
//       memory[address] = newValue;
//       return true;  // success
//     } else {
//       return false; // someone else changed it
//     }
//     unlock;
//   }

// Java AtomicLong implements lock-free counter:
import java.util.concurrent.atomic.AtomicLong;

public class LockFreeCounter {
    private final AtomicLong count = new AtomicLong(0);
    
    public void increment() {
        // BAD way (but correct): retry loop
        long current, next;
        do {
            current = count.get();
            next = current + 1;
        } while (!count.compareAndSet(current, next));
        // CAS fails if another thread modified count between get() and CAS
        // Retry: re-read current value and try again
    }
    
    // GOOD: use built-in atomic operation (same semantics, cleaner)
    public void incrementBetter() {
        count.incrementAndGet();  // internally uses CAS loop
    }
    
    // For high-contention counters: LongAdder is better
    // LongAdder: maintains per-thread cells, sums on read
    // Lock-free AND no false sharing (cells are @Contended)
}
```

---

### Lock-Free Stack (Treiber Stack)

```java
// Classic lock-free stack using CAS
public class LockFreeStack<T> {
    private static class Node<T> {
        final T value;
        Node<T> next;
        Node(T value) { this.value = value; }
    }
    
    // AtomicReference<Node<T>>: allows CAS on head pointer
    private final AtomicReference<Node<T>> head =
        new AtomicReference<>(null);
    
    public void push(T value) {
        Node<T> newHead = new Node<>(value);
        Node<T> oldHead;
        do {
            oldHead = head.get();
            newHead.next = oldHead;
            // CAS: atomically set head to newHead only if still oldHead
        } while (!head.compareAndSet(oldHead, newHead));
        // If another thread pushed between get() and CAS:
        // CAS fails, retry with new oldHead
    }
    
    public T pop() {
        Node<T> oldHead, newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;  // empty stack
            newHead = oldHead.next;
        } while (!head.compareAndSet(oldHead, newHead));
        // CAS succeeds: we atomically moved head from oldHead to newHead
        return oldHead.value;
    }
}
// Problem with this implementation: ABA problem (see below)
```

---

### The ABA Problem

```
ABA problem: CAS can succeed even when the value changed and changed back
  
Timeline:
  Stack: A -> B -> C
  Thread 1: reads head = A (preparing to pop)
  Thread 1: suspended by OS (pre-empted)
  
  Thread 2: pops A (stack: B -> C)
  Thread 2: pops B (stack: C)
  Thread 2: pushes A back (stack: A -> C)
  
  Thread 1: resumes
  Thread 1: CAS(head, A, B) -> SUCCEEDS! (head is A again)
  Thread 1: head.next = B (but B was already freed/recycled!)
  -> Use-after-free / dangling pointer BUG
  
Fix: AtomicStampedReference (version counter)
  AtomicStampedReference<Node<T>> head
  Each CAS also increments stamp (version number)
  Even if value returns to A: stamp is different
  CAS(A, stamp1, B, stamp2) fails if stamp doesn't match

Java solution:
  AtomicStampedReference<V>: value + int stamp pair
  AtomicMarkableReference<V>: value + boolean mark pair
  
Real-world: Java's ConcurrentLinkedQueue avoids ABA
  by never reusing Node objects (allocation instead of recycling)
  -> Memory overhead but ABA-safe
```

---

### Java's Lock-Free Collections

```
java.util.concurrent lock-free structures:
  
  ConcurrentLinkedQueue<E>:
    Lock-free FIFO queue (Michael-Scott queue algorithm)
    CAS on head (dequeue) and tail (enqueue)
    Safe for multiple producers and consumers
    
  ConcurrentSkipListMap<K,V>:
    Lock-free sorted map (skip list implementation)
    O(log n) operations without locks
    Good for: sorted concurrent maps, leaderboards, range queries
    
  LongAdder / DoubleAdder:
    Lock-free + no false sharing (striped cells)
    Best for: write-heavy counters, metrics, statistics
    
  AtomicReferenceArray<E>:
    Lock-free atomic operations on array elements
    
  AtomicIntegerFieldUpdater (advanced):
    Retrofit atomic CAS to existing class fields
    Avoids object allocation overhead of AtomicInteger
    
When to prefer lock-free over synchronized:
  Use lock-free when:
    Contention is frequent
    Critical section is small (CAS fits)
    GC pause sensitivity matters (locks can cause GC delays)
    
  Use synchronized/Lock when:
    Multiple variables must update atomically
    CAS retry overhead too high (high contention)
    Logic requires conditional compound operations
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Lock-free always outperforms synchronized" | Lock-free wins under high contention and small critical sections. Under LOW contention, uncontested synchronized blocks are extremely fast (~20ns, just an atomic increment). Lock-free with complex retry logic can be SLOWER than synchronized when contention is low due to the overhead of CAS memory barriers |
| "If no thread can block, wait-free is achieved" | Lock-free guarantees SYSTEM progress (some thread advances). Individual threads can still spin in CAS retry loops indefinitely if consistently pre-empted by others. Wait-free is stronger: every individual thread makes progress within bounded steps - a much harder guarantee |

---

### Quick Reference Card

| Concept | Key Fact |
|---------|---------|
| CAS instruction | `CMPXCHG` on x86; single atomic read-modify-write |
| Lock-free guarantee | System-wide progress; individual thread may retry |
| ABA problem | Value changed from A->B->A; CAS sees A and succeeds incorrectly |
| ABA fix | `AtomicStampedReference` (version counter) |
| Best counter | `LongAdder` (lock-free + @Contended striped cells) |
| ConcurrentLinkedQueue | Michael-Scott lock-free queue algorithm |
