---
id: OSY-046
title: Testing Concurrent Programs (Basics)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-029, OSY-038
used_by: []
related: OSY-029, OSY-038, OSY-056
tags:
  - testing
  - concurrency
  - thread-safety
  - race-condition
  - junit
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/osy/testing-concurrent-programs/
---

## TL;DR

Concurrent bugs don't always appear under normal testing.
Effective strategies: stress tests with many threads,
CyclicBarrier to maximize contention, deterministic
replay with ThreadWeaver, and static analysis with
SpotBugs (FindBugs). Concurrent bugs require repeated
high-concurrency runs to surface reliably.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-046 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | concurrent testing, race conditions, stress testing |
| **Prerequisites** | OSY-029, OSY-038 |

---

### Why Concurrent Testing is Hard

```
Concurrent bugs depend on:
  - Thread scheduling order (non-deterministic)
  - CPU cache state (varies per run)
  - JIT compilation state (changes over time)
  - System load (other processes affecting scheduling)
  
A race condition test may:
  PASS  on developer's machine (low load, specific CPU)
  PASS  in CI (different scheduling)
  FAIL  on production (high load, many cores, different timing)
  FAIL  randomly (1 in 1000 runs)
  
Testing strategy:
  1. Maximize contention (many threads hitting same code)
  2. Repeat many times
  3. Use barriers to synchronize thread starts (maximize overlap)
  4. Verify invariants after concurrent execution
```

---

### Basic Concurrent Test Pattern

```java
// Pattern: CyclicBarrier + CountDownLatch stress test
@Test
public void testCounterThreadSafety() throws Exception {
    int threadCount = 100;
    int incrementsPerThread = 10_000;
    AtomicInteger counter = new AtomicInteger(0); // subject under test
    
    CountDownLatch startGate = new CountDownLatch(1);
    CountDownLatch endGate = new CountDownLatch(threadCount);
    
    for (int i = 0; i < threadCount; i++) {
        Thread t = new Thread(() -> {
            try {
                startGate.await(); // ALL threads wait here
                for (int j = 0; j < incrementsPerThread; j++) {
                    counter.incrementAndGet(); // operation under test
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                endGate.countDown();
            }
        });
        t.start();
    }
    
    startGate.countDown();          // release all threads at once
    endGate.await(30, TimeUnit.SECONDS); // wait for all to finish
    
    int expected = threadCount * incrementsPerThread;
    assertEquals("Counter must be exact under concurrency",
        expected, counter.get());
}
// If AtomicInteger -> passes
// If plain int counter++ -> fails (race condition detected)
```

---

### Testing with Known Race Condition

```java
// Test that DETECTS race condition (proving a bug exists)
@Test
public void detectRaceConditionInNonAtomicCounter() throws Exception {
    int[] failureCount = {0};
    int runsToFindRace = 100;
    
    for (int run = 0; run < runsToFindRace; run++) {
        // The buggy class under test:
        RacyCounter counter = new RacyCounter(); // int count++ 
        int threadCount = 10;
        CountDownLatch done = new CountDownLatch(threadCount);
        
        for (int i = 0; i < threadCount; i++) {
            new Thread(() -> {
                for (int j = 0; j < 1000; j++) counter.increment();
                done.countDown();
            }).start();
        }
        
        done.await();
        if (counter.getCount() != 10_000) {
            failureCount[0]++;
        }
    }
    
    // Should fail at least some runs if race condition exists
    assertTrue("Race condition never detected in " + runsToFindRace
        + " runs - is the test effective?",
        failureCount[0] > 0);
    System.out.println("Race detected in "
        + failureCount[0] + " of " + runsToFindRace + " runs");
}
```

---

### Invariant Checking Pattern

```java
// Test shared data structure invariants under concurrency
@Test
public void testBankTransferInvariant() throws Exception {
    int accountCount = 10;
    int initialBalance = 1000;
    int[] accounts = new int[accountCount];
    Arrays.fill(accounts, initialBalance);
    int totalInitial = accountCount * initialBalance;
    
    int threadCount = 50;
    CountDownLatch done = new CountDownLatch(threadCount);
    Random rng = new ThreadLocalRandom.current().getClass().newInstance();
    
    for (int t = 0; t < threadCount; t++) {
        new Thread(() -> {
            for (int op = 0; op < 100; op++) {
                int from = ThreadLocalRandom.current().nextInt(accountCount);
                int to = ThreadLocalRandom.current().nextInt(accountCount);
                int amount = ThreadLocalRandom.current().nextInt(100);
                // transfer() under test - should be thread-safe
                transfer(accounts, from, to, amount);
            }
            done.countDown();
        }).start();
    }
    
    done.await(30, TimeUnit.SECONDS);
    
    // INVARIANT: total money must be conserved
    int total = Arrays.stream(accounts).sum();
    assertEquals("Total money must be conserved (no money created/lost)",
        totalInitial, total);
}
```

---

### Tools for Concurrent Testing

```bash
# ThreadSanitizer (TSan) - for native code
g++ -fsanitize=thread -g my_program.cpp
./a.out  # Run test; TSan reports race conditions with stack traces

# Java: SpotBugs with concurrent bug detectors
# Add to pom.xml:
# <plugin>
#   <groupId>com.github.spotbugs</groupId>
#   <artifactId>spotbugs-maven-plugin</artifactId>
# </plugin>
# mvn spotbugs:check
# Detects: inconsistent synchronization, read/write without lock,
#          double-checked locking bugs, notify() on wrong object

# Java: jcstress (OpenJDK concurrency stress tests)
# Developed by OpenJDK team specifically for concurrency testing
# mvn dependency:get -Dartifact=org.openjdk.jcstress:jcstress-core:0.16
@JCStressTest
@Outcome(id = "1, 1", expect = Expect.ACCEPTABLE, desc = "OK")
@Outcome(id = "0, 1", expect = Expect.FORBIDDEN, desc = "Race!")
@State
public class VisibilityTest {
    int x;
    @Actor public void actor1() { x = 1; }
    @Actor public void actor2(II_Result r) { r.r1 = x; r.r2 = x; }
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "If tests pass in CI, there's no concurrency bug" | CI typically runs on a specific OS/hardware with specific thread scheduling. Concurrency bugs manifest based on timing which varies across environments. A race condition that appears 1 in 10,000 runs will never show in a CI run of 1 test |
| "Synchronized collection (Collections.synchronizedList) makes tests pass for concurrent use" | Synchronized collections make individual operations atomic, but compound operations (check-then-add) are still not atomic. Tests must verify compound-operation safety explicitly |

---

### Mastery Checklist

- [ ] Can write a concurrent stress test using CyclicBarrier/CountDownLatch
- [ ] Knows why repeating tests many times matters for concurrency bugs
- [ ] Can write an invariant check for a concurrent data structure
- [ ] Knows at least two tools for concurrent bug detection (TSan, SpotBugs)
