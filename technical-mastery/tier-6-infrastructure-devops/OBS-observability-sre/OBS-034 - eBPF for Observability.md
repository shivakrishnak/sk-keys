---
id: OBS-034
title: eBPF for Observability
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★★★
depends_on: OBS-001, OBS-006, OBS-008, OBS-033
used_by: OBS-044, OBS-045, OBS-047
related: OBS-006, OBS-008, OBS-033, OBS-030, OBS-044
tags:
  - observability
  - linux
  - performance
  - kernel
  - advanced
  - production
  - deep-dive
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/obs/ebpf-for-observability/
---

⚡ TL;DR - eBPF (extended Berkeley Packet Filter) lets
you run small, verified programs inside the Linux
kernel without modifying kernel source or loading
kernel modules. For observability, this means capturing
any system event (network packets, system calls, function
calls) with near-zero overhead and no code changes
in applications.

| #034            | Category: Observability & SRE                                            | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Observability Fundamentals, Metrics Types, Tracing, Continuous Profiling |                 |
| **Used by:**    | Platform Observability, Distributed Tracing Architecture                 |                 |
| **Related:**    | Metrics Types, Distributed Tracing, Continuous Profiling, USE Method     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Observing a running production system requires a
choice between two bad options:

1. **Instrument the code:** add SDK calls to every
   application. Requires code changes, rebuilds,
   redeployments. Cannot observe legacy services,
   third-party binaries, or kernel-level behaviour.
   Adds latency (every trace span requires a function
   call). Misses: network-level events, kernel syscalls,
   and cross-service packet flows.

2. **Add a monitoring agent:** kernel modules or
   ptrace-based tools. Kernel modules require matching
   kernel version, can crash the kernel if buggy,
   require root and specialised expertise. ptrace
   is 10-1000x overhead (unsuitable for production).

Neither option can safely answer: "Which process is
causing this network traffic?" or "Which syscall is
called most frequently before this latency spike?"
without significant overhead or risk.

**THE INVENTION:**
eBPF, introduced in Linux 3.15 (2014) and matured
in 4.x+, allows loading small verified programs into
the kernel that execute at specific hook points (when
a packet arrives, when a syscall is called, when a
function is entered). These programs are verified
by the kernel's eBPF verifier before execution -
they cannot crash the kernel, cannot loop infinitely,
and cannot access arbitrary memory. Overhead: < 1%.
No application code changes. Works across all languages
and runtimes on Linux.

---

### 📘 Textbook Definition

**eBPF (extended Berkeley Packet Filter)** is a
Linux kernel technology that allows loading sandboxed
user-defined programs into the kernel. An eBPF program:

- Is written in restricted C (or using high-level
  wrappers: BCC Python API, libbpf, Go eBPF library)
- Is compiled to eBPF bytecode
- Is verified by the eBPF verifier before loading:
  - Must terminate (no unbounded loops)
  - Cannot dereference arbitrary pointers
  - Must access only authorised kernel data
- Executes at a hook point (kprobe, tracepoint,
  socket filter, perf event, cgroup, XDP)
- Communicates with userspace via eBPF maps (key-value
  stores shared between kernel and userspace)

**eBPF hook types for observability:**

- **kprobe/kretprobe**: attach to any kernel function
  entry or return. Captures arguments and return values.
- **tracepoint**: stable kernel-defined trace event.
  Less fragile than kprobes (survives kernel updates).
- **uprobe/uretprobe**: attach to userspace function
  entry or return without code changes. Works with
  compiled binaries.
- **perf_event**: sample CPU performance counters.
  Used for continuous profiling (Parca, BCC tools).
- **XDP (eXpress Data Path)**: intercept packets
  before they reach the network stack. Used for
  high-performance packet filtering and network observability.

**Key eBPF observability tools:**

- **Cilium + Tetragon**: Kubernetes networking and
  security observability via eBPF (replaces kube-proxy)
- **Parca / BPFtrace**: continuous CPU profiling
- **bpftrace**: one-liner eBPF scripting for ad-hoc
  kernel tracing
- **BCC tools (execsnoop, tcptracer, opensnoop)**:
  pre-built eBPF tracing scripts
- **Pixie**: auto-instrumentation of Kubernetes services
  via eBPF - captures HTTP/gRPC/DNS without code changes
- **Falco**: security monitoring via eBPF syscall audit
- **Hubble** (part of Cilium): network flow visibility

---

### ⏱️ Understand It in 30 Seconds

**One line:**
eBPF lets you attach a tiny surveillance program to
any kernel event - network packets, function calls,
system calls - with near-zero overhead and without
changing any application code.

> eBPF is like installing invisible security cameras
> throughout an office building. Traditional monitoring
> requires each office to install its own camera
> system (SDK instrumentation in each service).
> eBPF installs cameras at the building's infrastructure
> layer - hallways, elevators, entrances - that see
> every person (process, packet) passing through,
> without requiring each office to do anything.
> The cameras are verified (cannot record where they
> should not), run on minimal power (< 1% CPU), and
> are managed centrally by the building security
> team (platform SRE).

---

### 🔩 First Principles Explanation

**THE EBPF EXECUTION MODEL:**

```
Traditional code path (without eBPF):
  User application → syscall → kernel → hardware

eBPF code path:
  User application → syscall
    ↓
  [eBPF probe attached to this syscall]
    eBPF program executes:
      record: {pid, syscall_nr, timestamp, args}
      update eBPF map (shared with userspace)
    ↓
  kernel → hardware (normal execution continues)
    ↓
  [Userspace daemon reads eBPF map]
    Aggregates data → exports to Prometheus/OTLP

Overhead:
  eBPF program execution: 50-500 nanoseconds
  Normal syscall: 200-2000 nanoseconds
  Overhead: ~10-50% of syscall time
  But: syscalls are rare in typical services
  Effective overhead: < 1% for most workloads
```

**THE EBPF VERIFIER (why it is safe):**

```
When you load an eBPF program, the kernel verifier:

1. Checks: no unbounded loops
   (all loops must have a maximum iteration count)

2. Checks: all pointer dereferences are valid
   (cannot read arbitrary kernel memory)

3. Checks: program terminates in < 1M instructions
   (prevents infinite loops from blocking kernel)

4. Checks: stack size ≤ 512 bytes
   (prevents stack overflow in kernel context)

5. Type-checks all map accesses
   (correct key/value types for each map)

If verification fails: program rejected before loading.
If verification passes: program is safe to execute
in kernel context at near-native speed (JIT compiled
on x86, arm64, s390).

This is why eBPF programs cannot crash the kernel.
Kernel modules (traditional approach) have no such
safety guarantees.
```

**THE EBPF MAP (kernel-userspace communication):**

```c
// eBPF program (kernel side)
// Attached to: sys_enter_openat (file open syscall)

// Define a map: key=process ID, value=open count
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, u32);         // PID
    __type(value, u64);       // open() call count
} file_opens SEC(".maps");

// eBPF program: executed on every open() syscall
SEC("tracepoint/syscalls/sys_enter_openat")
int trace_open(struct trace_event_raw_sys_enter *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 *count = bpf_map_lookup_elem(&file_opens, &pid);
    if (count) {
        (*count)++;
    } else {
        u64 initial = 1;
        bpf_map_update_elem(&file_opens, &pid, &initial,
          BPF_ANY);
    }
    return 0;
}

// Userspace daemon (Go/Python/C)
// Reads the map every second and exports to Prometheus
for pid, count := range bpfMap.Iterate() {
    gauge.With(prometheus.Labels{
      "pid": strconv.Itoa(pid),
    }).Set(float64(count))
}
```

---

### 🧪 Thought Experiment

**THE MYSTERY LATENCY:**

A microservice has 50ms P99 latency. An engineer
suspects a specific kernel function is being called
inefficiently. Without eBPF:

- Cannot attach a profiler without code changes
- Cannot observe kernel-level function calls
- Guesswork: maybe DNS? Maybe TCP? Maybe I/O?

With bpftrace (one-liner eBPF):

```bash
# Trace all DNS lookups by process name, with latency
sudo bpftrace -e '
kprobe:getaddrinfo
/comm == "checkout-service"/
{
  @start[tid] = nsecs;
}
kretprobe:getaddrinfo
/comm == "checkout-service" && @start[tid]/
{
  @dns_latency = hist(nsecs - @start[tid]);
  delete(@start[tid]);
}
'
# Output after 30 seconds:
# @dns_latency:
#   [1K, 2K)             12 |@@@                           |
#   [2K, 4K)             89 |@@@@@@@@@@@@@@@@@@@@@@        |
#   [4K, 8K)            234 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
#   [8K, 16K)           45 |@@@@@@@@@@                    |
#   [16K, 32K)            8 |@@                            |
#   [32K, 64K)            1 |                              |
#   [64K, 128K)           0 |                              |
#   [128K, 256K)          0 |                              |
# [256K, 512K)          1 |                              |  ← outlier!
```

Finding: 1 DNS lookup out of 390 took > 256ms. The
rest are under 32ms. One slow DNS response is
the source of the tail latency. No code changes.
No application rebuild. Kernel-level trace.

---

### 🧠 Mental Model / Analogy

> eBPF is like a building's smart electrical system
> that can report the power draw of any circuit in
> real time without adding a power meter to each
> device. Traditional observability = asking each
> device to report its own power draw (SDK instrumentation).
> eBPF observability = measuring power at the wiring
> level (kernel), where every device's consumption
> is automatically visible.
>
> The building's electrical system "knows" about
> every device because all power flows through the
> same infrastructure. The Linux kernel "knows" about
> every process because all system calls, all network
> packets, and all I/O flows through the kernel.
> eBPF hooks into that shared infrastructure layer.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
eBPF is a Linux technology that lets you observe
what a system is doing at the most detailed level
(which processes are making network calls, which
files are being opened, which functions are slow)
without changing any application code.

**Level 2 - Tool-level usage (junior):**
Use pre-built eBPF tools: `execsnoop` (trace all
process executions), `tcptracer` (trace all TCP
connections), `opensnoop` (trace all file opens),
`funclatency` (measure latency of any kernel function).
These tools are part of the BCC toolset and require
no eBPF programming knowledge. Install: `apt install
bpfcc-tools`. Run: `sudo execsnoop-bpfcc` to see
all process executions system-wide.

**Level 3 - Platform observability (mid-level):**
Deploy Pixie on Kubernetes: auto-captures HTTP/gRPC/
DNS traffic between all pods without any instrumentation.
Deploy Parca (or Pyroscope with eBPF backend) for
system-wide CPU profiling. Deploy Cilium for Kubernetes
networking with Hubble for network flow visibility.
These tools give "zero-instrumentation observability"
for an entire Kubernetes cluster.

**Level 4 - Custom tooling (senior):**
Write custom eBPF programs with bpftrace for ad-hoc
investigation: trace specific kernel functions,
measure custom syscall latency, track memory allocation
patterns. Use libbpf (C) or the Go eBPF library
for production-grade tools. Understand the eBPF verifier
constraints to write programs that pass verification.
Understand map types (hash, array, ring buffer, perf
event array) for different data patterns.

**Level 5 - Infrastructure design (staff):**
Design an eBPF observability platform: DaemonSet-based
eBPF agents deployed to every Kubernetes node,
collecting system-wide metrics (syscall latency,
network flow topology, CPU profile) and exporting
to Prometheus/OTLP. eBPF as the observation layer
for zero-trust security monitoring (Tetragon/Falco:
alert when a container makes an unexpected syscall
or network connection). Evaluate eBPF vs sidecar
proxy (Istio/Envoy) for service mesh observability:
eBPF has lower overhead but less configurability;
sidecar has more features but adds latency. CO-RE
(Compile Once - Run Everywhere): BPF programs that
compile once and run on any kernel version without
recompilation.

---

### ⚙️ How It Works (Mechanism)

**PIXIE - ZERO-INSTRUMENTATION KUBERNETES OBSERVABILITY:**

```bash
# Deploy Pixie to Kubernetes (no app code changes needed)
# Pixie uses eBPF uprobes + kprobes to auto-capture:
#   HTTP1.1, HTTP2, gRPC, MySQL, PostgreSQL, Redis,
#   Kafka, DNS, SSL/TLS traffic

# Install
px deploy

# Query: HTTP latency for all services in last 5 minutes
# (Pixie PXL query language)
import px

df = px.DataFrame(table='http_events',
  start_time='-5m')
df = df[df.ctx['namespace'] == 'production']
df.latency_p99 = df.groupby(
  ['ctx.service', 'req_path']
).agg(
  latency_p99=('resp_latency_ns', px.percentile, 99)
)
px.display(df, 'HTTP P99 Latency by Service and Path')
# Output: real HTTP traces from ALL services
# No instrumentation added to any service
```

**TETRAGON - SECURITY OBSERVABILITY:**

```yaml
# Tetragon TracingPolicy: alert on unexpected outbound
# network connections from production pods
# Uses eBPF kprobes on tcp_connect kernel function

apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: block-unexpected-outbound
spec:
  kprobes:
    - call: "tcp_connect"
      return: false
      syscall: false
      args:
        - index: 0
          type: "sock"
      selectors:
        - matchNamespaces:
            - namespace: Production
              values: ["production"]
          matchActions:
            - action: Sigkill
            # Kill process making unexpected connection
              # or: action: Post  (alert only)
```

**BPFTRACE - AD-HOC KERNEL TRACING:**

```bash
# One-liner: trace all slow file reads (> 1ms)
sudo bpftrace -e '
kprobe:vfs_read
{
  @start[tid] = nsecs;
  @file[tid] = arg0;   # struct file*
}
kretprobe:vfs_read
/@start[tid]/
{
  $duration = nsecs - @start[tid];
  if ($duration > 1000000) {  // 1ms in nanoseconds
    printf("PID %d: slow read %ldms on fd %d\n",
      pid, $duration / 1000000,
      ((struct file*)@file[tid])->f_pos);
  }
  delete(@start[tid]);
  delete(@file[tid]);
}'

# One-liner: HTTP request latency via SSL write/read
# (works for TLS traffic - no SSL inspection needed)
sudo bpftrace -e '
uprobe:/usr/lib/libssl.so:SSL_write
/comm == "checkout"/
{
  @start[tid] = nsecs;
}
uretprobe:/usr/lib/libssl.so:SSL_write
/comm == "checkout" && @start[tid]/
{
  @send_latency = hist(nsecs - @start[tid]);
  delete(@start[tid]);
}'
```

---

### 🔄 The Complete Picture - End-to-End Flow

**EBPF OBSERVABILITY STACK (Kubernetes):**

```
[All Kubernetes Nodes]
  ↓
[eBPF DaemonSet (Pixie / Parca / Cilium Hubble)]
  Deployed to every node.
  Loads eBPF programs on node startup.
  Hooks: kprobes, tracepoints, uprobes, XDP
  Captures:
    - All HTTP/gRPC/DNS traffic (Pixie)
    - All TCP connections and network flows (Hubble)
    - CPU profiles for all processes (Parca)
    - Syscall anomalies (Tetragon)
  ↓
[eBPF Map → Userspace Agent]
  Ring buffer or perf event array carries events
  from kernel to userspace agent (low latency)
  Userspace agent aggregates + enriches with
  Kubernetes metadata (pod name, namespace, service)
  ↓
[Export]
  Prometheus metrics → Prometheus server
  OTLP traces → Jaeger / Grafana Tempo
  Hubble network flows → Hubble UI
  Parca profiles → Parca server / Pyroscope
  ↓
[Grafana Dashboards + Alerts]
  HTTP latency by service (no SDK instrumentation)
  Network topology (which service calls which)
  CPU profiles (no application code changes)
  Security events (unexpected syscalls)
```

---

### 💻 Code Example

**Example 1 - BAD: Traditional observability for kernel events:**

```python
# BAD: trying to observe kernel-level I/O via
# application-level instrumentation
# Cannot see: kernel TCP retransmits, DNS latency,
# kernel scheduler delays, filesystem cache misses

# Application logs disk read duration:
start = time.time()
data = open(file_path).read()
duration = time.time() - start
metrics.record("file_read_duration", duration)

# Problem: this measures user-space perception of I/O.
# It cannot distinguish:
# - Actual disk read (physical I/O)
# - Page cache hit (memory operation, very fast)
# - Kernel buffer waiting (I/O scheduler delay)
# Only eBPF can see which of these is happening.
```

**Example 2 - GOOD: eBPF for precise kernel-level measurement:**

```bash
# Using BCC biolatency: measure actual block I/O latency
# (not application-level perception)
# Shows the distribution of disk operation latency

sudo /usr/share/bcc/tools/biolatency -D
# -D: show disk names
# Output (30 seconds):
# Tracing block device I/O... Hit Ctrl-C to end.
#
# nvme0n1
# usecs               : count     distribution
#     0 -> 1          : 0        |                        |
#     2 -> 3          : 0        |                        |
#     4 -> 7          : 623      |@@@@@@@@@@@@@@@@@@@@@@@ |
#     8 -> 15         : 1240     |@@@@@@@@@@@@@@@@@@@@@@@@|
#    16 -> 31         : 89       |@@@                     |
#    32 -> 63         : 12       |                        |
# 64 -> 127        : 2        |                        |  ← outliers
#    128 -> 255       : 1        |                        |

# Real kernel block I/O latency distribution.
# No application code changed. No rebuild. No restart.
```

**Example 3 - Pixie HTTP observability (no SDK needed):**

```python
# Pixie PXL script: auto-captured HTTP traces
# No instrumentation in any application

import px

# HTTP services overview - captured via eBPF uprobes
# on the HTTP/1.1 and HTTP/2 protocol parsers
df = px.DataFrame(
  table='http_events',
  start_time='-10m'
)

# Enrich with Kubernetes metadata
df.service = df.ctx['service']
df.namespace = df.ctx['namespace']

# Aggregate by service and endpoint
df = df.groupby(['service', 'req_path']).agg(
  latency_p50=('resp_latency_ns', px.percentile, 50),
  latency_p99=('resp_latency_ns', px.percentile, 99),
  req_count=('resp_latency_ns', px.count),
  error_rate=('resp_status', lambda x: (x >= 500).mean())
)

px.display(df, 'HTTP Overview')
# Displays RED metrics for ALL services in the cluster
# with ZERO application code changes
```

---

### ⚖️ Comparison Table

| Approach              | Code change?          | Overhead  | Languages         | Kernel visibility | Production safe?  |
| --------------------- | --------------------- | --------- | ----------------- | ----------------- | ----------------- |
| SDK instrumentation   | Yes                   | 1-5%      | Language-specific | None              | Yes               |
| eBPF (Pixie, Parca)   | No                    | < 1%      | Any               | Full              | Yes (verified)    |
| Kernel module         | No                    | Low-high  | Any               | Full              | Risky (can crash) |
| ptrace                | No                    | 10-1000x  | Any               | Full              | No (too slow)     |
| sidecar proxy (Istio) | No (but infra change) | 5-15%     | Any               | Network only      | Yes               |
| strace                | No                    | Very high | Any               | Syscalls only     | No                |

**eBPF tool landscape:**

| Tool           | Purpose                    | Kubernetes?     | Code change? |
| -------------- | -------------------------- | --------------- | ------------ |
| Pixie          | HTTP/gRPC/DNS auto-tracing | Yes             | No           |
| Parca          | Continuous CPU profiling   | Yes (DaemonSet) | No           |
| Cilium Hubble  | Network flow visibility    | Yes             | No           |
| Tetragon/Falco | Security audit             | Yes             | No           |
| bpftrace       | Ad-hoc kernel tracing      | Any Linux       | No           |
| BCC tools      | Pre-built trace scripts    | Any Linux       | No           |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                                                               |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "eBPF requires modifying the kernel"    | No. eBPF programs are loaded into the kernel via the `bpf()` syscall. They run in a sandboxed JIT-compiled environment without modifying kernel source. The kernel must be ≥ 4.4 for basic eBPF, ≥ 4.18 for full observability features.              |
| "eBPF programs can crash the kernel"    | No. The eBPF verifier ensures safety before loading: no infinite loops, no invalid pointer dereferences, bounded stack usage. A buggy eBPF program is rejected by the verifier, not executed. This is the fundamental difference from kernel modules. |
| "eBPF replaces SDK instrumentation"     | No. eBPF excels at: network flows, syscall tracing, CPU profiling (no code changes). SDK instrumentation excels at: business-level tracing (trace IDs, custom spans, business events), request correlation, custom metrics. Use both.                 |
| "eBPF is Linux-only"                    | True for the original eBPF. Microsoft has eBPF for Windows (preview). macOS uses dtrace (different technology). For cloud-native (Linux-based) deployments: eBPF is the standard.                                                                     |
| "eBPF is only for networking (packets)" | eBPF started as a packet filter (BPF in 1992). Extended eBPF (2014+) hooks into any kernel function: file I/O, process events, scheduler, memory, security, CPU performance. Networking is one of many use cases.                                     |

---

### 🚨 Failure Modes & Diagnosis

**eBPF verifier rejection: program too complex**

**Symptom:**
Deploying a custom eBPF program fails with:
`Error: failed to load BPF object: verifier log: ...
processed 1000001 insns (limit is 1000000)`.
The program was tested on the development kernel
but fails on the production kernel (older version).

**Root Cause:**
The eBPF verifier instruction limit varies by kernel
version. Older kernels have lower limits (32,768
instructions in 4.x, 1,000,000 in 5.3+). A complex
program that passes verification on kernel 5.15
may fail on 4.19 (common in enterprise Linux).

**Fix:**

```bash
# Check kernel version of production nodes:
kubectl get nodes -o wide | grep VERSION

# For older kernels (< 5.x):
# Simplify the eBPF program:
# 1. Move complex logic to userspace (simplify kernel side)
# 2. Use ring buffers instead of complex map patterns
# 3. Split into multiple smaller programs
# 4. Use BTF (BPF Type Format) for CO-RE compatibility

# CO-RE approach (Compile Once - Run Everywhere):
# Allows building against a BTF schema rather than
# kernel headers - works across kernel versions
# without recompilation
```

---

**eBPF memory pressure on busy systems**

**Symptom:**
After deploying Pixie, a high-traffic node (50,000
req/s) shows kernel memory allocation failures in
`dmesg`. The eBPF ring buffer is filling faster
than userspace can drain it. Some events are dropped.

**Root Cause:**
eBPF ring buffer size too small for the event rate.
Default ring buffer: 1 MB. At 50,000 HTTP events/s
x 200 bytes/event = 10 MB/s throughput requirement.
The ring buffer fills and events are dropped.

**Fix:**

```bash
# Increase ring buffer size in eBPF program definition:
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 16 * 1024 * 1024);  # 16 MB
    # was: 1 * 1024 * 1024 (1 MB)
} events SEC(".maps");

# In Pixie config (Helm values.yaml):
vizier-config:
  pem:
    ringBufferSizeMb: 64  # Increase from default 8 MB

# Also: check event drop rate metric:
# Pixie: vizier.ring_buffer.dropped_events
# Alert if > 0.1% of events are dropped
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability` - eBPF provides the kernel-
  layer observability that completes the stack
- `Distributed Tracing Fundamentals` - eBPF tools
  like Pixie produce trace-like data without SDK
  instrumentation
- `Continuous Profiling` - Parca uses eBPF for
  zero-instrumentation CPU profiling

**Builds On This (learn these next):**

- `Platform Observability Engineering` - eBPF is
  the core technology for zero-instrumentation
  platform observability
- `Distributed Tracing System Architecture` - eBPF-
  based tracing vs SDK-based tracing architecture
  decisions

**Alternatives / Comparisons:**

- `SDK instrumentation (OpenTelemetry)` - alternative
  for application-level tracing. Higher overhead but
  supports custom business-level spans and events
  that eBPF cannot capture.
- `Service mesh sidecar (Istio/Envoy)` - alternative
  for network observability. More configurable traffic
  policies but higher latency overhead (5-15% vs
  eBPF < 1%).

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Sandboxed kernel programs loaded via     │
│              │ bpf() syscall, verified for safety       │
│              │ No kernel modification required          │
├──────────────┼──────────────────────────────────────────┤
│ HOOK TYPES   │ kprobe: any kernel function              │
│              │ tracepoint: stable kernel events         │
│              │ uprobe: userspace function (no code chg) │
│              │ XDP: network packet at NIC level         │
│              │ perf_event: CPU performance counters     │
├──────────────┼──────────────────────────────────────────┤
│ SAFETY       │ Verifier: no infinite loops, no invalid  │
│              │ pointers, terminates in < 1M instructions│
│              │ Cannot crash the kernel (unlike modules) │
├──────────────┼──────────────────────────────────────────┤
│ OVERHEAD     │ < 1% CPU for typical observability use   │
│              │ Safe for continuous production use       │
├──────────────┼──────────────────────────────────────────┤
│ KEY TOOLS    │ Pixie: auto HTTP/gRPC traces (no SDK)    │
│              │ Parca: CPU profiling (no code changes)   │
│              │ Hubble: K8s network flow visibility      │
│              │ bpftrace: ad-hoc one-liner tracing       │
│              │ Tetragon/Falco: security audit           │
├──────────────┼──────────────────────────────────────────┤
│ BEST FOR     │ Network flows, syscall tracing, profiling│
│              │ Zero-instrumentation K8s observability   │
│              │ Security monitoring at kernel level      │
├──────────────┼──────────────────────────────────────────┤
│ NOT FOR      │ Business-level custom trace spans        │
│              │ Custom business metrics and events       │
│              │ (use SDK instrumentation for these)      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Platform Observability Engineering       │
│              │ Continuous Profiling (Pyroscope, Parca)  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Observe at the infrastructure layer when possible,
the application layer only when necessary. eBPF
demonstrates that observing at the kernel (infrastructure)
layer provides complete coverage with zero application
coupling and minimal overhead. This principle generalises:
in distributed systems, observing at the network layer
(service mesh) provides latency and throughput data
without application changes, but misses business-level
context. Observing at the database layer (slow query
log, query plan cache) provides query patterns without
application instrumentation but misses caller context.
The correct observability architecture layers these:
kernel-layer observation for system behaviour, network-
layer for service communication patterns, application-
layer for business context and custom events. Each
layer provides what the others cannot.

---

### 💡 The Surprising Truth

The most counterintuitive eBPF insight: eBPF programs
can observe TLS-encrypted HTTPS traffic without
intercepting the SSL handshake or having access to
private keys. How? eBPF attaches uprobes to the
`SSL_read` and `SSL_write` functions inside the
SSL library (OpenSSL, BoringSSL, NSS) - these
functions execute AFTER decryption, so the eBPF
program sees the plaintext data inside the SSL
library's memory space. This is how Pixie captures
HTTPS request/response bodies without SSL certificates
or proxy interception. The implication for security:
any process with sufficient Linux capabilities can
read SSL traffic from other processes via eBPF uprobes.
This is why eBPF requires `CAP_BPF` or `CAP_SYS_ADMIN`
privileges, and why container security policies should
restrict these capabilities to trusted observability
agents only.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe how the eBPF verifier
   ensures safety. List three specific safety properties
   it enforces and explain why each is necessary for
   kernel execution.
2. **[DISTINGUISH]** Explain the difference between
   kprobe, tracepoint, and uprobe hooks, and give
   a use case where each is the most appropriate.
3. **[USE]** Write a bpftrace one-liner that traces
   all TCP connections made by a specific process,
   showing the destination IP and port.
4. **[COMPARE]** Compare eBPF-based observability
   (Pixie) vs SDK-based observability (OpenTelemetry).
   Describe two scenarios where eBPF is clearly better,
   and two scenarios where SDK instrumentation is
   necessary.
5. **[DESIGN]** Design the eBPF observability stack
   for a Kubernetes platform: which tools to deploy,
   what each captures, how they integrate with Grafana,
   and what data they produce that SDK instrumentation
   cannot.

---

### 🧠 Think About This Before We Continue

**Q1.** A security engineer says "eBPF can read SSL
traffic without certificates, so we should block
all eBPF usage on our Kubernetes nodes." A platform
engineer says "eBPF is essential for our observability
and security monitoring." How do you resolve this
tension? What is the correct security policy?
_Hint: Both are correct in isolation. Resolution:
eBPF with `CAP_SYS_ADMIN` or `CAP_BPF` CAN read SSL
traffic from processes running on the same node.
The security policy: (1) restrict eBPF capabilities
to trusted DaemonSets only (observability, security
monitoring). (2) Use Pod Security Standards (restricted
profile) to prevent arbitrary pods from requesting
eBPF capabilities. (3) Trusted eBPF agents (Pixie,
Tetragon) run in a dedicated privileged namespace
with strict RBAC. (4) The security monitoring agent
(Tetragon/Falco) itself monitors for unexpected eBPF
program loads. This way: legitimate observability
and security tools use eBPF; arbitrary workloads
cannot. The correct answer is: restrict capability,
not the technology._

**Q2.** You are investigating high P99 latency (800ms)
in a Go service. Metrics show: CPU 35% (normal),
memory 60% (normal), network bandwidth 20% (normal).
The Go profiler shows no hot functions. What kernel-
level investigation would you perform with bpftrace
to identify the cause?
_Hint: Profile normal, CPU/memory/network normal, but
P99 high = something is blocking outside of CPU/memory.
Candidates: (1) network syscall latency (getaddrinfo
DNS, connect, recv delays), (2) file I/O latency
(slow disk reads), (3) futex contention (goroutine
lock waits at kernel level), (4) scheduler latency
(process not scheduled = kernel runqueue). Investigations:
bpftrace DNS: `kprobe:getaddrinfo { @start[tid]=nsecs }
kretprobe:getaddrinfo { @lat=hist(nsecs-@start[tid]) }`.
bpftrace network I/O: `kprobe:tcp_recvmsg` with latency.
bpftrace futex: `tracepoint:syscalls:sys_enter_futex` with
counts and latency. If runqueue: `runqlat` BCC tool to
measure kernel scheduler latency. Each of these can reveal
100ms+ delays invisible to Go runtime metrics._

**Q3 (TYPE G):** Design a zero-instrumentation
observability platform for a Kubernetes cluster with
200 services. Zero instrumentation means: no changes
to any application code, no sidecar proxies, no
SDK libraries. Using only eBPF-based tooling, achieve:
(a) HTTP/gRPC latency metrics for all services,
(b) distributed tracing across services, (c) CPU
and memory profiling for all pods, (d) network flow
topology (which service calls which), (e) security
audit of all syscalls. Specify the tools, deployment
architecture, data flows, and limitations.
_Hint: (a) HTTP latency: Pixie DaemonSet on all nodes.
Auto-captures HTTP/1.1 and HTTP2 (gRPC) via uprobes
on kernel network stack. Exports RED metrics per service.
(b) Distributed tracing: challenging with zero SDK.
Pixie captures individual service HTTP calls but cannot
stitch them into end-to-end traces without trace ID
propagation (which requires SDK or header injection
at the proxy level). Limitation: full distributed traces
require either a sidecar (Envoy) or SDK to propagate
trace context. eBPF gives per-service latency but not
end-to-end traces. (c) CPU/memory profiling: Parca
DaemonSet on all nodes. eBPF-based statistical CPU
sampling for all processes. No code changes. Memory
profiling via eBPF memory allocation tracking (kmalloc
tracepoints). (d) Network topology: Hubble (Cilium)
on all nodes. Captures all TCP connections with
Kubernetes-enriched metadata (pod/service/namespace).
Network graph in Hubble UI. (e) Security: Tetragon
DaemonSet. TracingPolicies for syscall audit.
Limitations: (1) No business-level spans or custom
attributes without SDK. (2) No trace context propagation
without SDK or sidecar. (3) Some HTTP implementations
(custom or binary protocols) may not be captured by
Pixie. (4) Requires privileged DaemonSets: security
review required._

---

### 🎯 Interview Deep-Dive

**Q1: "What is eBPF and how does it enable observability
without code changes?"**
_Why they ask:_ Tests understanding of the technology
architecture, not just "Pixie is a tool that does X."
_Strong answer includes:_

- eBPF = sandboxed programs loaded into the kernel
  via `bpf()` syscall. Verified for safety before
  execution (no crashes, no infinite loops).
- Hooks into kernel events: kprobes (kernel functions),
  uprobes (userspace functions), tracepoints (stable
  kernel events), XDP (network).
- For observability: attach to kernel network functions
  → see all network traffic without code changes.
  Attach to SSL_read/SSL_write uprobes → see HTTPS
  payload without certificates.
- Overhead: < 1% CPU (JIT compiled, executes in
  kernel context without context switch).
- No code changes because: the kernel already processes
  all system calls, network packets, and function
  calls. eBPF hooks into this existing processing.

**Q2: "What is the difference between a kprobe and
a tracepoint in eBPF?"**
_Why they ask:_ Tests depth of eBPF technical knowledge.
_Strong answer includes:_

- kprobe: dynamic probe on any kernel function.
  Can attach to any function in the kernel (> 50,000
  possible probe points). Fragile: function names
  and signatures can change between kernel versions.
  Use when tracepoints do not cover what you need.
- tracepoint: static kernel-defined trace event.
  Stable API: kernel developers commit to not changing
  the tracepoint's name or arguments. Survives kernel
  updates. Available for: syscalls, scheduler events,
  network, block I/O, memory. Use when available.
  Example: `tracepoint/syscalls/sys_enter_openat`
  is stable across kernel versions.
- uprobe: userspace equivalent of kprobe. Attaches
  to a userspace function in a binary (e.g., `SSL_write`
  in libssl). Enables observing any language's functions
  without code changes.

**Q3: "When would you choose eBPF observability over
OpenTelemetry SDK instrumentation?"**
_Why they ask:_ Tests ability to make architectural
decisions, not just enumerate tools.
_Strong answer includes:_

- Choose eBPF for: (1) services you cannot instrument
  (third-party binaries, legacy code, scripts). (2)
  Network-level observability (TCP flows, DNS latency,
  network topology). (3) Kernel-level behaviour (disk
  I/O, scheduler latency, syscall audit). (4) Security
  monitoring (unexpected process executions, network
  connections, syscall patterns). (5) Zero-overhead
  requirement (eBPF < 1% vs SDK 1-5%).
- Choose SDK (OpenTelemetry) for: (1) Custom business
  spans (trace "checkout" with order_id, user_id as
  span attributes). (2) End-to-end distributed traces
  with trace context propagation. (3) Custom metrics
  (business-level counters, histograms). (4) Services
  where you can control the code.
- Best answer: use both. eBPF provides the infrastructure
  layer (network, system, security). SDK provides the
  business layer (custom traces, business metrics).
  They are complementary, not competing.

## OBS-029 - eBPF for Observability

> Entry stub. Generate full content using Master Prompt v3.0.
