---
id: OSY-041
title: Build a Multi-Process Server (Phase 2 - IPC and Signals)
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-023, OSY-035, OSY-036
used_by: []
related: OSY-035, OSY-036, OSY-053
tags:
  - practice
  - lab
  - IPC
  - signals
  - hands-on
  - phase-2
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/osy/os-lab-phase-2/
---

## TL;DR

Phase 2 lab: build a multi-process server using fork/exec,
implement IPC via pipes, and handle signals for graceful
shutdown. Completion proves you can use OS primitives for
real inter-process coordination.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-041 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | lab, phase-2, multi-process, IPC, signals |
| **Prerequisites** | OSY-023, OSY-035, OSY-036 |

---

### Lab Goal

Build a Java "worker pool" using OS processes (not threads):
- A master process spawns N worker processes
- Master sends work via pipes (IPC)
- Workers report results via pipes back
- Master handles SIGTERM -> sends SIGTERM to all workers
- Workers handle SIGTERM -> finish current task, exit

---

### Exercise 1: Master-Worker with Pipes

```java
// MasterProcess.java
public class MasterProcess {
    private static final int WORKER_COUNT = 3;
    private final List<Process> workers = new ArrayList<>();
    private final List<BufferedWriter> workerInputs = new ArrayList<>();
    private final List<BufferedReader> workerOutputs = new ArrayList<>();
    
    public void start() throws IOException, InterruptedException {
        // Spawn N worker processes
        for (int i = 0; i < WORKER_COUNT; i++) {
            ProcessBuilder pb = new ProcessBuilder(
                "java", "-cp", System.getProperty("java.class.path"),
                "WorkerProcess", String.valueOf(i));
            pb.redirectError(ProcessBuilder.Redirect.INHERIT);
            Process worker = pb.start();
            workers.add(worker);
            
            // Pipes to worker (stdin/stdout via ProcessBuilder)
            workerInputs.add(new BufferedWriter(
                new OutputStreamWriter(worker.getOutputStream())));
            workerOutputs.add(new BufferedReader(
                new InputStreamReader(worker.getInputStream())));
        }
        System.out.println("Master: started " + WORKER_COUNT
            + " workers with PIDs: " +
            workers.stream().map(p -> String.valueOf(p.pid()))
                   .collect(Collectors.joining(", ")));
    }
    
    public void dispatch(int workerId, String task) throws IOException {
        // Send task to specific worker via pipe
        workerInputs.get(workerId).write(task + "\n");
        workerInputs.get(workerId).flush();
        // Read result
        String result = workerOutputs.get(workerId).readLine();
        System.out.println("Master: worker " + workerId
            + " completed: " + result);
    }
    
    public void shutdown() {
        System.out.println("Master: sending SIGTERM to workers...");
        workers.forEach(Process::destroy);  // sends SIGTERM
        workers.forEach(p -> {
            try { p.waitFor(5, TimeUnit.SECONDS); }
            catch (InterruptedException e) { p.destroyForcibly(); }
        });
        System.out.println("Master: all workers stopped");
    }
    
    public static void main(String[] args) throws Exception {
        MasterProcess master = new MasterProcess();
        master.start();
        
        // Register shutdown hook for own SIGTERM
        Runtime.getRuntime().addShutdownHook(new Thread(
            master::shutdown));
        
        // Dispatch some work
        for (int i = 0; i < 9; i++) {
            master.dispatch(i % WORKER_COUNT, "task-" + i);
        }
    }
}
```

```java
// WorkerProcess.java
public class WorkerProcess {
    public static void main(String[] args) throws Exception {
        int workerId = Integer.parseInt(args[0]);
        System.err.println("Worker " + workerId + " started, PID: " +
            ProcessHandle.current().pid());
        
        // Handle SIGTERM - complete current task, exit gracefully
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.err.println("Worker " + workerId +
                ": SIGTERM received, shutting down");
        }));
        
        // Read tasks from stdin (pipe from master)
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(System.in))) {
            String task;
            while ((task = reader.readLine()) != null) {
                System.err.println("Worker " + workerId
                    + ": processing " + task);
                Thread.sleep(100);  // simulate work
                // Send result back to master via stdout
                System.out.println("result-of-" + task);
                System.out.flush();  // IMPORTANT: flush to unblock master
            }
        }
        System.err.println("Worker " + workerId + ": exiting normally");
    }
}
```

---

### Exercise 2: Zombie Process Prevention

```java
// Without proper wait(), worker processes become zombies
// A zombie holds its PID and exit status but is dead

// BAD: spawns workers but never waits for them
public class ZombieCreator {
    public static void main(String[] args) throws Exception {
        ProcessBuilder pb = new ProcessBuilder("sleep", "1");
        Process p = pb.start();
        // p.waitFor() NOT called
        // After "sleep 1" exits, becomes zombie
        // Observable: ps aux shows Z (zombie) state
    }
}

// GOOD: always reap child processes
public class ProperParent {
    public static void main(String[] args) throws Exception {
        ProcessBuilder pb = new ProcessBuilder("sleep", "1");
        Process p = pb.start();
        int exitCode = p.waitFor();  // reap the child
        System.out.println("Child exited with: " + exitCode);
        // Process removed from process table
    }
}

// For background children: wait in shutdown hook or separate thread
Thread reaper = new Thread(() -> {
    try {
        int exit = worker.waitFor();
        System.out.println("Worker exited: " + exit);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
});
reaper.setDaemon(true);
reaper.start();
```

---

### Exercise 3: Named Pipe Communication

```bash
# In shell: demonstrate named pipe IPC between two JVMs

# Create named pipe
mkfifo /tmp/java_pipe

# Terminal 1: Java producer
java -e '
import java.io.*; import java.nio.file.*;
var out = new PrintStream(new FileOutputStream("/tmp/java_pipe"));
for (int i = 0; i < 10; i++) {
    out.println("message-" + i);
    Thread.sleep(500);
}
out.close();'

# Terminal 2: Java consumer (runs simultaneously)
java -e '
import java.io.*; import java.nio.file.*;
var in = new BufferedReader(
    new InputStreamReader(new FileInputStream("/tmp/java_pipe")));
String line;
while ((line = in.readLine()) != null) {
    System.out.println("Received: " + line);
}'
```

---

### Completion Criteria

You've completed Phase 2 when you can:
- [ ] Spawn child processes from Java using ProcessBuilder
- [ ] Communicate via pipes (master writes, worker reads, worker writes, master reads)
- [ ] Handle SIGTERM in both master and worker processes
- [ ] Prevent zombie processes by calling waitFor()
- [ ] Verify IPC with strace showing pipe read/write syscalls

---

### Key Insight

The multi-process server pattern is used in:
- Nginx: master process + worker processes (no shared state)
- PostgreSQL: postmaster + backend processes (one per connection)
- Apache httpd: mpm_prefork (one process per request)
- Redis: background AOF/RDB child processes

Java favors threads over processes for intra-JVM work, but
understanding OS process IPC is essential for:
- Container sidecar patterns
- External tool integration
- Understanding how your process appears to the OS
