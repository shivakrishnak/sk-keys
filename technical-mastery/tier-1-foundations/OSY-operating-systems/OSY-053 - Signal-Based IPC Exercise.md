---
id: OSY-053
title: Signal-Based IPC Exercise
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-035, OSY-036, OSY-041
used_by: []
related: OSY-035, OSY-036, OSY-041
tags:
  - practice
  - lab
  - signals
  - IPC
  - hands-on
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/osy/signal-ipc-exercise/
---

## TL;DR

Hands-on exercise: build signal-based communication
between processes. Use SIGUSR1/SIGUSR2 for custom
notifications, SIGHUP for config reload, and SIGTERM
for graceful shutdown. Completion verifies you can
use signals for real IPC scenarios.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-053 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | lab, signals, IPC, SIGUSR1, SIGHUP, SIGTERM |
| **Prerequisites** | OSY-035, OSY-036, OSY-041 |

---

### Exercise 1: Config Reload via SIGHUP

```java
// ConfigReloadServer.java
// Demonstrates SIGHUP -> reload configuration (like Nginx reload)

import sun.misc.Signal;  // Java's signal handling (unofficial API)
// Note: Signal API is in sun.misc (not in standard API)
// For production: use runtime.addShutdownHook pattern instead

public class ConfigReloadServer {
    private volatile Map<String, String> config = new HashMap<>();
    private final String configPath = "/etc/app/config.properties";
    
    public void start() {
        // Load initial config
        loadConfig();
        
        // Register SIGHUP handler for config reload
        Signal.handle(new Signal("HUP"), signal -> {
            System.out.println("Received SIGHUP - reloading config...");
            loadConfig();
            System.out.println("Config reloaded: " + config.size() + " keys");
        });
        
        // Register SIGTERM for graceful shutdown
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("SIGTERM: shutting down gracefully...");
            // close connections, flush buffers...
        }));
        
        System.out.println("Server started. PID: " +
            ProcessHandle.current().pid());
        System.out.println("Send SIGHUP to reload config: kill -1 " +
            ProcessHandle.current().pid());
        
        // Main loop
        while (true) {
            try {
                Thread.sleep(5000);
                System.out.println("Running with config: " + config);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    private void loadConfig() {
        // In real code: read from file
        Map<String, String> newConfig = new HashMap<>();
        newConfig.put("reload.time", Instant.now().toString());
        newConfig.put("feature.enabled", "true");
        this.config = newConfig;  // atomic reference swap
    }
    
    public static void main(String[] args) {
        new ConfigReloadServer().start();
    }
}
```

```bash
# Test config reload:
java ConfigReloadServer &
PID=$!
sleep 2
echo "Sending SIGHUP (reload)..."
kill -1 $PID   # SIGHUP = reload
sleep 3
echo "Sending SIGHUP again..."
kill -1 $PID
sleep 2
kill -15 $PID  # SIGTERM = graceful stop
```

---

### Exercise 2: SIGUSR1 Statistics Request

```java
// StatsServer.java  
// SIGUSR1 -> dump current statistics (like Java's kill -3 for thread dump)

public class StatsServer {
    private final AtomicLong requestCount = new AtomicLong(0);
    private final AtomicLong errorCount = new AtomicLong(0);
    
    public void start() {
        // SIGUSR1: dump statistics on demand
        Signal.handle(new Signal("USR1"), signal -> {
            System.out.println("=== Statistics ===");
            System.out.println("Requests: " + requestCount.get());
            System.out.println("Errors: " + errorCount.get());
            System.out.println("Error rate: " +
                (100.0 * errorCount.get() / 
                 Math.max(1, requestCount.get())) + "%");
            System.out.println("Free memory: " +
                Runtime.getRuntime().freeMemory() / 1024 / 1024 + "MB");
            System.out.println("Thread count: " +
                Thread.activeCount());
            System.out.println("==================");
        });
        
        System.out.println("Server started. PID: " +
            ProcessHandle.current().pid());
        System.out.println("Send SIGUSR1 for stats: kill -10 " +
            ProcessHandle.current().pid());
        
        // Simulate request handling
        Random rng = new Random();
        while (true) {
            try {
                Thread.sleep(100);
                requestCount.incrementAndGet();
                if (rng.nextInt(20) == 0) {
                    errorCount.incrementAndGet();
                }
            } catch (InterruptedException e) {
                break;
            }
        }
    }
    
    public static void main(String[] args) {
        new StatsServer().start();
    }
}
```

```bash
# Test on-demand stats:
java StatsServer &
PID=$!
sleep 5
echo "Requesting stats..."
kill -10 $PID  # SIGUSR1
sleep 5
kill -10 $PID  # request again
kill $PID      # terminate
```

---

### Exercise 3: Process Supervisor Pattern

```bash
#!/usr/bin/env bash
# supervisor.sh - restart child on crash, stop on SIGTERM

CHILD_PID=""
RUNNING=true

cleanup() {
    echo "Supervisor: SIGTERM received, stopping child..."
    if [ -n "$CHILD_PID" ]; then
        kill -SIGTERM "$CHILD_PID"
        wait "$CHILD_PID"
    fi
    RUNNING=false
}

trap cleanup SIGTERM SIGINT

while $RUNNING; do
    echo "Supervisor: starting java app..."
    java -jar app.jar &
    CHILD_PID=$!
    
    wait $CHILD_PID
    EXIT_CODE=$?
    
    if ! $RUNNING; then
        echo "Supervisor: intentional stop, exiting"
        break
    fi
    
    echo "Supervisor: child exited with $EXIT_CODE, restarting in 3s..."
    sleep 3
done

echo "Supervisor: exiting"
```

---

### Completion Criteria

- [ ] Implemented SIGHUP config reload and tested with kill -1
- [ ] Implemented SIGUSR1 stats dump and verified output
- [ ] Understands why SIGKILL cannot be caught
- [ ] Can explain the supervisor pattern and why PID 1 matters in containers

---

### Key Insight: Signals vs Polling

```
Signal-based notification vs polling:

POLLING:
  while (true) {
      if (configFile.lastModified() != lastCheck) {
          reload();
      }
      Thread.sleep(5000);  // check every 5 seconds
  }
  Latency: up to 5 seconds between change and reload
  CPU: minimal but wasted on negative checks

SIGNAL-BASED:
  Signal.handle("HUP", -> reload());
  // Zero latency: reload triggered instantly
  // Zero CPU: no polling loop
  
INOTIFY (Linux file watch, even better):
  Better than signal for file change notification
  Uses inotify_add_watch() syscall
  Java: WatchService API (wraps inotify on Linux)
  WatchService: event-driven, zero latency, zero CPU poll
```
