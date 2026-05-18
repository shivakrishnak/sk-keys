---
id: OSY-038
title: Thread-Safe Programming Basics
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-007, OSY-029, OSY-030
used_by: OSY-042
related: OSY-029, OSY-030, OSY-056
tags:
  - thread-safe
  - concurrency
  - atomicity
  - immutability
  - confinement
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 38
permalink: /technical-mastery/osy/thread-safe-programming/
---

## TL;DR

Thread safety strategies in order of preference:
(1) Stateless - no shared mutable state, (2) Immutable -
shared but unchanging, (3) Thread confinement - one thread
owns each object, (4) Synchronized access - explicit locks.
Most bugs come from strategy 4 applied incorrectly.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-038 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | thread safety, immutability, confinement, synchronization |
| **Prerequisites** | OSY-007, OSY-029, OSY-030 |

---

### Thread Safety Strategies (Preference Order)

**Strategy 1: Stateless (Best)**

```java
// No shared state = no synchronization needed
// Pure functions: input -> output, no side effects

// GOOD: Stateless service (Spring @Service default)
@Service
public class PriceCalculator {
    // No instance fields (no state)
    public BigDecimal calculate(Item item, Discount discount) {
        // Uses only method-local variables
        // Safe for concurrent calls from thousands of threads
        return item.getPrice()
                   .multiply(BigDecimal.ONE.subtract(discount.getRate()));
    }
}
// Every Spring controller, service, and repository should be
// stateless by design. If you need state, make it local or external.
```

**Strategy 2: Immutability**

```java
// Immutable objects can be safely shared across threads
// No state = no race conditions possible

// GOOD: Immutable value object
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;
    
    public Money(BigDecimal amount, Currency currency) {
        this.amount = Objects.requireNonNull(amount);
        this.currency = Objects.requireNonNull(currency);
    }
    
    // Returning new instance instead of mutating
    public Money add(Money other) {
        if (!this.currency.equals(other.currency))
            throw new IllegalArgumentException("Currency mismatch");
        return new Money(this.amount.add(other.amount), this.currency);
    }
    
    // No setters, final fields, final class = immutable
    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }
}
// Thread safe: multiple threads can read simultaneously
// Safely passed through thread boundaries without sync
// Java's String, Integer, BigDecimal are all immutable - thread safe
```

**Strategy 3: Thread Confinement**

```java
// ThreadLocal: each thread has its own copy
// No sharing = no synchronization needed

// GOOD: ThreadLocal for request context
public class RequestContext {
    private static final ThreadLocal<String> currentUser =
        new ThreadLocal<>();
    
    public static void setUser(String user) {
        currentUser.set(user);   // sets for CURRENT thread only
    }
    
    public static String getUser() {
        return currentUser.get(); // gets CURRENT thread's value
    }
    
    public static void clear() {
        currentUser.remove();    // IMPORTANT: prevent memory leak!
    }
    // In thread pools: thread is reused, ThreadLocal persists
    // Call remove() in finally block when done with request
}

// Spring uses ThreadLocal for:
// - SecurityContextHolder (current user's security context)
// - TransactionSynchronizationManager (current transaction)
// - RequestContextHolder (current HTTP request)
```

**Strategy 4: Synchronized Access**

```java
// Use when state must be shared AND mutable
// Atomic for single variables, synchronized for compound ops

// GOOD: multiple fields requiring atomic update
public class BankAccount {
    private BigDecimal balance;
    private final List<Transaction> history = new ArrayList<>();
    
    // synchronized: both fields updated atomically
    public synchronized void deposit(BigDecimal amount) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0)
            throw new IllegalArgumentException("Amount must be positive");
        balance = balance.add(amount);
        history.add(new Transaction("DEPOSIT", amount));
        // Both updates happen atomically under the lock
    }
    
    public synchronized BigDecimal getBalance() {
        return balance;  // read also synchronized for consistency
    }
}
```

---

### Common Thread Safety Mistakes

```java
// MISTAKE 1: Returning reference to mutable internal state
public class Config {
    private final Map<String, String> settings = new HashMap<>();
    
    // BAD: caller gets mutable reference to internal map
    public Map<String, String> getSettings() {
        return settings;  // caller can do settings.clear()!
    }
    
    // GOOD: return unmodifiable view
    public Map<String, String> getSettings() {
        return Collections.unmodifiableMap(settings);
    }
}

// MISTAKE 2: "synchronized wrapper" doesn't make compound ops atomic
List<String> syncList = Collections.synchronizedList(new ArrayList<>());
// BAD: check-then-act is NOT atomic even with synchronized list!
if (!syncList.contains("item")) {
    syncList.add("item");  // RACE: another thread may add between check and add
}
// GOOD: synchronize the compound operation
synchronized (syncList) {
    if (!syncList.contains("item")) {
        syncList.add("item");
    }
}

// MISTAKE 3: Synchronized scope too narrow
public class Counter {
    private int count = 0;
    
    // BAD: compound operation not atomic
    public int getAndIncrement() {
        synchronized (this) { return count; }      // released here!
        // Another thread can increment between these operations
        synchronized (this) { count++; return count; }  // wrong
    }
    
    // GOOD: one atomic operation
    public synchronized int getAndIncrement() {
        return count++;  // both read AND increment under lock
    }
    // Or: AtomicInteger.getAndIncrement() (lock-free)
}
```

---

### Immutability Checklist

```java
// To make a class properly immutable:
public final class ImmutablePoint {  // 1. final class (no subclassing)
    private final double x;           // 2. final fields
    private final double y;           // 3. no setters
    
    public ImmutablePoint(double x, double y) {
        this.x = x;
        this.y = y;
        // 4. defensive copy of mutable constructor args
        // (not needed here; doubles are primitives)
    }
    
    // 5. defensive copy of mutable return values
    public double[] toArray() {
        return new double[]{x, y};  // new array, not internal reference
    }
    
    // 6. return new instance for "mutations"
    public ImmutablePoint translate(double dx, double dy) {
        return new ImmutablePoint(x + dx, y + dy);
    }
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "synchronized on all methods makes a class thread-safe" | Synchronized on individual methods makes each method atomic, but compound operations (calling multiple methods) are still not atomic. Synchronizing the caller's compound operation is needed |
| "volatile makes a variable thread-safe" | volatile ensures visibility (all threads see latest write) but NOT atomicity. count++ with volatile is still a race condition. Use AtomicInteger for atomic compound operations |
| "Immutable objects are always slower due to object creation" | Immutable objects enable lock-free sharing. The JVM can also eliminate redundant allocations (escape analysis). For long-lived shared objects, immutability removes synchronization overhead entirely |

---

### Quick Reference Card

| Strategy | When to Use | Java Mechanism |
|---------|------------|----------------|
| Stateless | Default for services | No instance fields |
| Immutable | Value objects, DTOs | final class, final fields |
| Thread confinement | Per-request state | ThreadLocal |
| Atomic variables | Single counters/flags | AtomicInteger, AtomicReference |
| Synchronized | Multiple fields together | synchronized, ReentrantLock |
| Concurrent collections | High-concurrency maps/lists | ConcurrentHashMap, CopyOnWriteArrayList |
