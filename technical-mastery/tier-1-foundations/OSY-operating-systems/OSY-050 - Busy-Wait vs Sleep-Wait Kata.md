---
id: OSY-050
title: Busy-Wait vs Sleep-Wait Kata
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-039, OSY-030
used_by: []
related: OSY-039, OSY-030, OSY-056
tags:
  - practice
  - kata
  - busy-wait
  - sleep-wait
  - hands-on
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/osy/busy-wait-sleep-kata/
---

## TL;DR

Hands-on kata: implement a producer-consumer system
first with busy-wait (observe 100% CPU), then rewrite
with sleep-wait primitives (observe ~0% CPU idle).
Completion proves you can identify and fix busy-wait
anti-pattern by measurement.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-050 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | kata, practice, busy-wait, producer-consumer |
| **Prerequisites** | OSY-039, OSY-030 |

---

### Part 1: Implement the Busy-Wait Version (DO THIS FIRST)

```java
// BusyWaitProducerConsumer.java
// Deliberately wrong: observe the CPU waste

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.Queue;

public class BusyWaitProducerConsumer {
    private final Queue<Integer> queue = new ConcurrentLinkedQueue<>();
    private volatile boolean done = false;
    
    // Producer: adds items to queue every 10ms
    class Producer implements Runnable {
        public void run() {
            for (int i = 0; i < 1000; i++) {
                queue.add(i);
                try { Thread.sleep(10); } // produce slowly
                catch (InterruptedException e) { return; }
            }
            done = true;
        }
    }
    
    // Consumer: BUSY-WAIT (wrong!)
    class Consumer implements Runnable {
        public void run() {
            int processed = 0;
            while (!done || !queue.isEmpty()) {
                Integer item = queue.poll();
                if (item != null) {
                    // process item
                    processed++;
                }
                // NO SLEEP: busy-wait! Loops at full CPU speed
            }
            System.out.println("Consumed: " + processed);
        }
    }
    
    public static void main(String[] args) throws Exception {
        BusyWaitProducerConsumer pc = new BusyWaitProducerConsumer();
        Thread producer = new Thread(pc.new Producer());
        Thread consumer = new Thread(pc.new Consumer());
        
        consumer.start();
        producer.start();
        producer.join();
        consumer.join();
    }
}
```

```bash
# Run and observe CPU usage:
java BusyWaitProducerConsumer &
PID=$!
top -H -p $PID -b -n 5 | grep java
# Expected: Consumer thread at ~100% CPU even though queue is usually empty!
# Producer thread at ~0% CPU (sleeping 10ms between items)
kill $PID
```

---

### Part 2: Measure the Problem

```bash
# Record exact CPU metrics before fix
java BusyWaitProducerConsumer &
PID=$!

# Measure for 10 seconds
for i in {1..10}; do
  ps -p $PID -o pid,pcpu,pmem,nlwp
  sleep 1
done
kill $PID

# Record: CPU% _____________ (should be ~100% on one core)
# Record: Thread count (nlwp) _____________
```

---

### Part 3: Rewrite with BlockingQueue

```java
// SleepWaitProducerConsumer.java
// Fixed version using blocking wait

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class SleepWaitProducerConsumer {
    // BlockingQueue: take() sleeps when empty, wakes on item add
    private final BlockingQueue<Integer> queue =
        new LinkedBlockingQueue<>(100); // bounded: back-pressure
    
    class Producer implements Runnable {
        public void run() {
            try {
                for (int i = 0; i < 1000; i++) {
                    queue.put(i);  // blocks if queue full (back-pressure)
                    Thread.sleep(10);
                }
                queue.put(-1); // sentinel: end of work
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    // Consumer: SLEEP-WAIT (correct!)
    class Consumer implements Runnable {
        public void run() {
            int processed = 0;
            try {
                while (true) {
                    // take() BLOCKS (parks thread) when queue is empty
                    // OS wakes thread only when producer adds item
                    Integer item = queue.take();
                    if (item == -1) break; // sentinel: done
                    // process item
                    processed++;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            System.out.println("Consumed: " + processed);
        }
    }
    
    public static void main(String[] args) throws Exception {
        SleepWaitProducerConsumer pc = new SleepWaitProducerConsumer();
        Thread producer = new Thread(pc.new Producer());
        Thread consumer = new Thread(pc.new Consumer());
        
        consumer.start();
        producer.start();
        producer.join();
        consumer.join();
    }
}
```

---

### Part 4: Measure the Improvement

```bash
# Run fixed version and measure CPU:
java SleepWaitProducerConsumer &
PID=$!

for i in {1..10}; do
  ps -p $PID -o pid,pcpu,pmem,nlwp
  sleep 1
done
kill $PID

# Record: CPU% _____________ (should be ~0-2% when queue mostly empty)
# Compare to busy-wait version above

# Expected difference:
# Busy-wait:   CPU ~100% (1 full core wasted)
# Sleep-wait:  CPU ~1% (thread sleeping 99% of the time)
```

---

### Part 5: Extend Challenge

Extend the sleep-wait version to add:
1. Multiple consumers (2 consumers, 1 producer)
2. Priority queue (higher priority items processed first)
3. Bounded queue with back-pressure (producer slows when queue full)
4. Graceful shutdown (SIGTERM -> finish current batch, exit)

```java
// Hint for multiple consumers with sentinel:
// Each consumer needs ONE sentinel; producer sends N sentinels
for (int i = 0; i < consumerCount; i++) {
    queue.put(-1); // one sentinel per consumer
}
```

---

### Completion Criteria

- [ ] Ran busy-wait version and observed ~100% CPU on consumer thread
- [ ] Ran sleep-wait version and observed ~0-2% CPU when queue empty
- [ ] Explained to a colleague WHY the CPU usage differs
- [ ] Completed at least 2 extension challenges

---

### Key Takeaway

The difference between busy-wait and sleep-wait is:
- Busy-wait: OS sees RUNNABLE thread, schedules it, wastes CPU cycles
- Sleep-wait: OS sees BLOCKED thread, doesn't schedule it, CPU free

In production with hundreds of threads and thousands of requests,
sleep-wait ensures CPU goes to actual work, not polling loops.
This is why Java's concurrent utilities (BlockingQueue, Condition,
CompletableFuture) all park threads rather than spin.
