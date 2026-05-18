---
id: OSY-035
title: "Inter-Process Communication (Pipes, Message Queues, Shared Memory)"
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★☆
depends_on: OSY-006, OSY-019, OSY-034
used_by: OSY-041, OSY-042
related: OSY-036, OSY-041, OSY-062
tags:
  - IPC
  - pipes
  - message-queues
  - shared-memory
  - inter-process-communication
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 35
permalink: /technical-mastery/osy/inter-process-communication/
---

## TL;DR

IPC mechanisms: Pipes (unidirectional byte stream, parent-
child), FIFO/Named Pipes (filesystem-named, unrelated
processes), Message Queues (structured messages with
priority), Shared Memory (fastest: shared virtual pages,
needs external sync), Sockets (network-capable, most
flexible). Choose shared memory for max throughput, sockets
for distributed systems.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-035 |
| **Difficulty** | ★★☆ Working |
| **Category** | Operating Systems |
| **Tags** | IPC, pipes, message queues, shared memory, sockets |
| **Prerequisites** | OSY-006, OSY-019, OSY-034 |

---

### IPC Mechanisms Overview

```
IPC Mechanism     Speed      Scope          Use Case
Pipe              Fast       Parent-child   Shell pipelines, subprocess
Named Pipe (FIFO) Fast       Same host      Unrelated processes, simple stream
Message Queue     Medium     Same host      Priority messages, structured data
Shared Memory     Fastest    Same host      High-throughput, low-latency data share
Signals           Instant    Same host      Notification only (no data payload)
Unix Domain Socket Fast      Same host      Service-to-service (Docker containers)
TCP/UDP Socket    Slower     Any host       Distributed systems, microservices
```

---

### Pipes (Anonymous Pipes)

```bash
# Pipe: unidirectional, exists only between related processes
# Shell: ls | grep .java | wc -l
#   Shell creates 2 pipes: (ls->grep), (grep->wc)
#   Each pipe is a kernel buffer (~64KB circular buffer)

# pipe() syscall: creates pipe FDs
# int pipefd[2];  pipe(pipefd);
# pipefd[0] = read end, pipefd[1] = write end

# Java: ProcessBuilder with pipe
ProcessBuilder pb = new ProcessBuilder("ls", "-la");
pb.redirectOutput(ProcessBuilder.Redirect.PIPE);
Process p = pb.start();
try (BufferedReader reader = new BufferedReader(
        new InputStreamReader(p.getInputStream()))) {
    reader.lines().forEach(System.out::println);
}

# Key properties:
# - Kernel-buffered: writer can write ahead of reader
# - Blocking: write blocks when buffer full (back-pressure)
# - EOF: read returns 0 when all write ends are closed
# - Lifetime: destroyed when both ends are closed
```

---

### Named Pipes (FIFOs)

```bash
# Create a named pipe in the filesystem
mkfifo /tmp/myfifo

# Producer (Terminal 1):
echo "hello world" > /tmp/myfifo  # blocks until consumer opens

# Consumer (Terminal 2):
cat /tmp/myfifo  # reads, unblocks producer

# Key difference from anonymous pipe:
# Named pipe persists in filesystem as a special file
# Unrelated processes can open it by path
# Still FIFO, still kernel-buffered, no random access

# Java usage:
Path fifo = Path.of("/tmp/myfifo");
// Write side:
try (var os = Files.newOutputStream(fifo)) {
    os.write("data".getBytes());
}
// Read side (separate process):
try (var is = Files.newInputStream(fifo)) {
    byte[] buf = is.readAllBytes();
}
```

---

### POSIX Message Queues

```c
// Message queues: structured, typed messages with priority
// mq_open(), mq_send(), mq_receive(), mq_close()

// Sender:
mqd_t mq = mq_open("/myqueue", O_CREAT | O_WRONLY, 0644, &attr);
char msg[] = "task_id=42";
mq_send(mq, msg, strlen(msg), priority=5);

// Receiver:
mqd_t mq = mq_open("/myqueue", O_RDONLY);
char buf[256];
unsigned int priority;
mq_receive(mq, buf, sizeof(buf), &priority);  // highest priority first

// Key properties:
// - Messages have priority (higher priority received first)
// - Messages have typed size (not byte stream)
// - Kernel-managed: persists until mq_unlink() or reboot
// - Blocking: mq_receive() blocks when queue empty
```

---

### Shared Memory (Fastest IPC)

```c
// shm_open + mmap: two processes map same physical pages

// Process 1 (creator):
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0666);
ftruncate(fd, sizeof(SharedData));  // set size
SharedData *data = mmap(NULL, sizeof(SharedData),
    PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
data->counter = 0;

// Process 2 (consumer):
int fd = shm_open("/myshm", O_RDWR, 0666);
SharedData *data = mmap(NULL, sizeof(SharedData),
    PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
// data->counter is same physical memory as Process 1!

// Speed: memory access speed (no syscall for read/write)
// Risk: both processes can corrupt each other's data
// Requires: semaphore or mutex for synchronization

// Java shared memory:
// MappedByteBuffer via FileChannel.map()
// Useful for: JVM <-> native process data sharing
FileChannel ch = FileChannel.open(Path.of("/dev/shm/data"),
    StandardOpenOption.READ, StandardOpenOption.WRITE,
    StandardOpenOption.CREATE);
MappedByteBuffer buf = ch.map(MapMode.READ_WRITE, 0, 1024);
buf.putInt(0, 42);  // Write
int val = buf.getInt(0);  // Read (another process sees same value)
```

---

### IPC Selection Guide

```
Choose based on:
  1. Pipe: parent-child process, byte stream, simple
  2. FIFO: unrelated processes, same host, byte stream
  3. Message Queue: structured messages, priority needed
  4. Shared Memory: maximum throughput, same host,
     willing to add synchronization
  5. Unix Domain Socket: flexible, stream or datagram,
     authentication via credentials, Docker IPC
  6. TCP Socket: different hosts, language-agnostic,
     standard protocol
     
For Java microservices:
  Service to subprocess: ProcessBuilder + pipes
  Service to local service: Unix domain socket (Java 16+)
  Service to remote service: TCP socket (HTTP, gRPC, etc.)
  Java 16+ Unix sockets: UnixDomainSocketAddress
```

---

### Comparison Table

| Mechanism | Throughput | Latency | Complexity | Data type |
|-----------|-----------|---------|-----------|-----------|
| Pipe | High | Low | Simple | Byte stream |
| Named Pipe | High | Low | Simple | Byte stream |
| Message Queue | Medium | Low | Medium | Discrete messages |
| Shared Memory | Very High | Lowest | High (needs sync) | Raw bytes |
| Unix Socket | High | Low | Medium | Stream or datagram |
| TCP Socket | Medium | Network | High | Stream or datagram |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Shared memory is the best IPC for all cases" | Shared memory is fastest but requires explicit synchronization (race conditions without it). For most use cases, Unix domain sockets provide excellent performance with simpler semantics |
| "Pipes can be used between unrelated processes" | Anonymous pipes require a common ancestor (e.g., parent/child). Unrelated processes need named pipes (FIFOs), Unix sockets, or message queues |

---

### Quick Reference Card

| Mechanism | Java API | Best For |
|-----------|---------|---------|
| Anonymous pipe | ProcessBuilder.Redirect.PIPE | Parent-child subprocess |
| Named pipe | FileInputStream on FIFO path | Unrelated local processes |
| Shared memory | FileChannel.map() (MappedByteBuffer) | High-throughput local data |
| Unix socket | UnixDomainSocketAddress (Java 16+) | Local service IPC |
| TCP socket | Socket, ServerSocket | Cross-host communication |
