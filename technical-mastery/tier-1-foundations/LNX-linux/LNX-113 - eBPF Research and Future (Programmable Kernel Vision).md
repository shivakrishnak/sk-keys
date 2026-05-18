---
id: LNX-113
title: "eBPF Research and Future (Programmable Kernel Vision)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-035, LNX-101
used_by: LNX-114
related: LNX-035, LNX-101, LNX-114, LNX-117
tags: [ebpf, bpf, xdp, co-re, btf, bpf-type-format, libbpf, bpftool, cilium, pixie, bcc, bpf-lsm, bpf-prog, bpf-maps, ring-buffer, tc-bpf, kprobe, uprobe, tracepoint, sock-ops, sk-lookup, bpf-verifier, kernel-programmability, ebpf-in-production, bpfd, bpf-security, kernel-bypass, dpdk-comparison, ebpf-networking, ebpf-observability, ebpf-security]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 113
permalink: /technical-mastery/lnx/ebpf-research-future-programmable-kernel/
---

## TL;DR

eBPF (extended Berkeley Packet Filter) is a technology allowing **safe, verified
programs to run in the Linux kernel** without writing kernel modules or recompiling
the kernel. Programs written in restricted C -> compiled to BPF bytecode -> verified
by the kernel's BPF verifier (no loops that might not terminate, no out-of-bounds
memory access, no null pointer dereference) -> JIT compiled to native machine code
-> attached to kernel hook points (network packet arrival, system calls, scheduler
events, function entry/exit). **CO-RE (Compile Once - Run Everywhere)**: uses BTF
(BPF Type Format) = debug info embedded in kernel, allows a BPF program compiled
on Ubuntu 22.04 to run on CentOS 7 kernel 3.10+. **In production today**: Cilium
(Kubernetes networking/security via eBPF, replaces iptables with XDP-based
forwarding - 100x faster), Pixie (no-code observability via uprobes), Cloudflare
(DDoS mitigation at 1Tbps+), Meta (Katran L4 load balancer). **Future vision**:
"programmable OS" - eBPF as universal extension layer: BPF LSM for security policies,
bpfd as system service managing BPF lifecycle, eBPF storage I/O path, eBPF scheduling.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-113 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | eBPF, BPF, XDP, CO-RE, BTF, libbpf, Cilium, observability, security, kernel programmability |
| **Prerequisites** | LNX-035 (eBPF for observability), LNX-101 (eBPF for platform engineering) |

---

### The Problem This Solves

**Problem 1 - The kernel modification bottleneck**: Adding new kernel features
requires: writing C code, understanding kernel internals, submitting to LKML,
waiting 9-10 weeks per release cycle, distribution adoption (1+ years). Security
policies, network optimizations, performance tooling - all slow to deploy because
they require kernel changes. eBPF bypasses this: you write BPF code, load it into
the running kernel TODAY, no kernel patch required.

**Problem 2 - The kernel module safety problem**: Kernel modules run in Ring 0
with no isolation. A bug in a kernel module crashes the entire system. eBPF's
verifier provides: mathematical proof of program safety before execution. eBPF
programs are provably safe - the verifier ensures they cannot crash the kernel.

**Problem 3 - The observability overhead**: Adding tracing to production systems
historically required: inserting printk() (change kernel, recompile), using
SystemTap (complex scripting), or performance overhead from non-selective tracing.
eBPF probes: add/remove tracing to running production systems with negligible
overhead (verified to be safe, JIT compiled for performance).

---

### Textbook Definition

**eBPF (extended Berkeley Packet Filter)**: A virtual machine and instruction
set in the Linux kernel (since 3.18, with major extensions through 4.x and 5.x)
that allows sandboxed programs to run in kernel context. Programs are verified
for safety before execution, JIT compiled to native code, and attached to kernel
hook points. Supports: networking, tracing, security, and scheduling.

**BPF verifier**: The kernel component that analyzes BPF bytecode before
execution to prove: no unbounded loops, no out-of-bounds memory access, no
use-after-free, no null pointer dereference, no resource leaks. If verification
fails: the program is rejected (kernel returns EPERM).

**CO-RE (Compile Once - Run Everywhere)**: Mechanism for writing portable BPF
programs. Uses BTF (BPF Type Format) - kernel debug information - to allow a
BPF program to adapt to different kernel versions' struct layouts at load time,
eliminating the need to compile BPF programs on the target host.

**XDP (eXpress Data Path)**: BPF attachment point in the network driver, before
packet data reaches the kernel network stack. Enables: highest-performance packet
processing (1-10 microseconds per packet), DDoS mitigation, load balancing, DPDK
alternative using standard NIC hardware.

---

### Understand It in 30 Seconds

```bash
# === eBPF in 3 commands ===

# 1. Install BCC (BPF Compiler Collection):
apt install bpfcc-tools linux-headers-$(uname -r)
# or: pip3 install bcc

# 2. Trace all opens (file open system calls) in real-time:
opensnoop-bpfcc
# PID     COMM      FD ERR PATH
# 12345   vim        3   0 /home/user/.vimrc
# 23456   sshd       5   0 /proc/12345/status
# 34567   chrome    12   0 /proc/self/maps
# (works on LIVE production system, negligible overhead!)

# 3. Show CPU flame graph style function tracing:
profile-bpfcc -F 99 30  # sample at 99Hz for 30 seconds
# (outputs call stacks showing where CPU time is spent)

# === eBPF program types and attachment points ===

# Check what BPF programs are currently loaded:
bpftool prog list
# 1: socket_filter  name xxx  tag abc123  gpl
# 2: kprobe  name trace_write  tag def456  gpl
# 10: xdp  name xdp_fw  tag ghi789  gpl  loaded_at 2024-01-01T00:00:00
# 42: cgroup_skb  name restrict_net  tag jkl012  gpl

# Show details of a specific program:
bpftool prog show id 10
# 10: xdp  name xdp_fw  tag ghi789
#     loaded_at 2024-01-01T00:00:00  uid 0
#     xlated 456B  jited 312B  memlock 4096B
#     map_ids 3,4
#     btf_id 5

# Disassemble to see JIT-compiled native instructions:
bpftool prog dump jited id 10
# 0xffffffffc01234xx:
#   endbr64
#   push   rbp
#   mov    rbp,rsp
#   ...

# === CO-RE: compile once, run everywhere ===

# Traditional BPF: compile WITH kernel headers on target system
# (required exact kernel version headers)

# CO-RE: compile ONCE on any machine, run on any kernel
# Requires: kernel built with CONFIG_DEBUG_INFO_BTF=y (most modern kernels)

# Check if your kernel has BTF:
ls /sys/kernel/btf/vmlinux
# /sys/kernel/btf/vmlinux  -> exists! BTF is available

# Check BTF kernel version info:
bpftool btf dump file /sys/kernel/btf/vmlinux | grep "struct task_struct"
# [1234] STRUCT 'task_struct' size=9600 vlen=237
# kernel's exact task_struct layout is now available!

# CO-RE magic: BPF program declares what fields it needs
# At load time: kernel reads BTF, finds actual field offsets
# Works on: kernel 5.2+ with BTF support

# === Cilium: eBPF-based Kubernetes networking ===

# Traditional Kubernetes (with iptables):
# Pod A -> iptables PREROUTING -> iptables FORWARD -> iptables POSTROUTING -> Pod B
# iptables: O(N) rules scan for each packet (N = number of services)
# 10,000 services = 10,000 rules to scan per packet = slow!

# Cilium (with eBPF):
# Pod A -> BPF XDP/TC hook -> O(1) BPF map lookup -> Pod B
# BPF maps: hash tables with O(1) lookup
# 10,000 services = same O(1) lookup as 10 services!

# Check Cilium status:
kubectl -n kube-system exec -it cilium-xxx -- cilium status
# KVStore:      Ok       etcd: ...
# Kubernetes:   Ok       1.28+
# Kubernetes has 50 node, 500 services
# eBPF maps replacing 50,000 iptables rules with O(1) lookups

# === XDP for DDoS mitigation (Cloudflare approach) ===

# XDP hook: first point in network stack after NIC DMA
# Can DROP packet with XDP_DROP before it enters kernel stack
# At 10GbE: ~14.88 million packets/second
# XDP can process all of them with single-digit microsecond latency

# Sample XDP program (conceptual):
# int xdp_drop_icmp(struct xdp_md *ctx) {
#     struct ethhdr *eth = (void *)(long)ctx->data;
#     struct iphdr *ip = (void *)(eth + 1);
#     // Drop ICMP flood packets:
#     if (ip->protocol == IPPROTO_ICMP)
#         return XDP_DROP;  // dropped before reaching kernel!
#     return XDP_PASS;      // pass to normal kernel processing
# }
```

---

### First Principles

```
HOW eBPF WORKS: end-to-end flow

Step 1: WRITE (user space)
  Language: restricted C (or high-level: Rust/Go eBPF libraries)
  Constraints: no global variables, no loops without bounded iterations,
               no calling arbitrary kernel functions (only approved helpers),
               no pointer arithmetic beyond verified bounds
  
  Example program (count system calls per process):
  BPF_HASH(syscall_count, u32, u64);  // map: pid -> count
  int syscall_enter(struct pt_regs *ctx) {
      u32 pid = bpf_get_current_pid_tgid() >> 32;
      u64 *count = syscall_count.lookup(&pid);
      if (count) {
          (*count)++;
      } else {
          u64 init = 1;
          syscall_count.update(&pid, &init);
      }
      return 0;
  }

Step 2: COMPILE (user space)
  clang -O2 -target bpf -c program.c -o program.o
  -> ELF file containing BPF bytecode (64-bit RISC instruction set)
  -> 11 64-bit registers (R0-R10 + R11 for stack pointer)
  -> 512-byte stack limit (strict!)
  -> Max 1,000,000 instructions (before kernel 5.3: 4,096!)

Step 3: VERIFY (kernel)
  bpf(BPF_PROG_LOAD, ...) syscall invokes BPF verifier:
  
  Pass 1: DAG (Directed Acyclic Graph) check
    - No unreachable instructions
    - No out-of-bounds jumps
    - All exits must set R0 (return value)
  
  Pass 2: State exploration
    - Tracks type of every register at every instruction
    - Tracks whether pointers are NULL-checked before use
    - Tracks memory bounds for each pointer
    - Explores all possible code paths
    - If any path can: crash kernel, corrupt memory, loop forever
      -> REJECT (bpf() returns -EPERM)
    
  Key verifier rules:
    - Packet pointer (PTR_TO_PACKET): must be bounds-checked before dereference
    - Map value pointer: bounds-checked against map value size
    - Context pointer (PTR_TO_CTX): can only access fields defined in program type
    - Scalar values from user/network: treated as untrusted until range-checked

Step 4: JIT COMPILE (kernel)
  After verification: BPF bytecode -> native x86_64/ARM64/s390 instructions
  JIT compiler: kernel/bpf/x86_64.c (for x86_64)
  Performance: JIT BPF ~ C code compiled with -O2
               interpretive BPF (no JIT): ~10x slower (legacy systems only)
  Result: native machine code, stored in kernel memory, protected from modification

Step 5: ATTACH (user space -> kernel hook)
  Different program types attach to different hooks:
  
  kprobe/kretprobe:  any kernel function entry/exit
  uprobe/uretprobe:  any user-space function entry/exit
  tracepoint:        kernel static trace points (stable ABI)
  raw_tracepoint:    same, but with raw args (faster)
  XDP:               NIC receive path (before sk_buff allocation)
  TC (traffic control): after sk_buff, in qdisc layer
  socket_filter:     per-socket packet filter
  cgroup/skb:        per-cgroup network policy
  sched_cls/act:     TC classifier/action
  LSM:               Linux Security Module hooks (BPF LSM, kernel 5.7+)
  struct_ops:        replace kernel struct function pointers (e.g., scheduler)
  sk_msg:            socket message redirects

Step 6: RUN (kernel hook fires)
  When the hook fires (e.g., network packet arrives):
  1. Kernel calls JIT-compiled BPF code
  2. BPF code accesses context (packet data, syscall args, etc.)
  3. BPF code reads/writes BPF maps (persistent state)
  4. BPF code can call BPF helper functions:
     bpf_map_lookup_elem, bpf_ktime_get_ns, bpf_perf_event_output,
     bpf_skb_store_bytes, bpf_redirect, bpf_get_current_task, etc.
  5. BPF code returns action: XDP_PASS/XDP_DROP/XDP_TX for XDP,
     TC_ACT_OK/TC_ACT_DROP for TC, or returns an integer for probes

Step 7: DATA ACCESS (user space)
  BPF maps: shared memory between BPF program (kernel) and user space
  Types: BPF_MAP_TYPE_HASH, BPF_MAP_TYPE_ARRAY, BPF_MAP_TYPE_PERF_EVENT_ARRAY,
         BPF_MAP_TYPE_RINGBUF (kernel 5.8: preferred for event streaming)
  
  User space reads maps via bpf() syscall:
  bpf(BPF_MAP_LOOKUP_ELEM, ...) -> get value for a key
  bpf(BPF_MAP_GET_NEXT_KEY, ...) -> iterate over all keys

THE BPF VISION: "PROGRAMMABLE OS KERNEL"

eBPF has expanded from network filter to:
  1. Networking: XDP, TC, socket, cgroup network policy
  2. Observability: kprobe, uprobe, tracepoint, perf (all kernel events)
  3. Security: BPF LSM (Linux Security Module via BPF, kernel 5.7)
  4. Scheduling: BPF sched (still experimental, struct_ops + sched hooks)
  5. File system: (early research: BPF I/O schedulers)
  
The pattern: each kernel subsystem opening itself to BPF programmability
  
Alexei Starovoitov (eBPF co-creator) vision:
  "eBPF will do for the kernel what JavaScript did for the browser"
  JavaScript: browser was fixed HTML renderer -> JS made it programmable
  eBPF: kernel was fixed set of behaviors -> eBPF makes it programmable
  
  Both: sandboxed (JS: browser sandbox, BPF: verifier sandbox)
  Both: JIT compiled for performance
  Both: event-driven (JS: DOM events, BPF: kernel hooks)
  Both: have a standard "library" (JS: DOM API, BPF: helper functions)
  
CO-RE and the portability revolution:
  Pre-CO-RE (BCC era, 2015-2019):
    Write BPF in embedded strings (Python + C strings)
    Compile on target machine (required kernel headers on prod server!)
    Different kernel versions: different struct layouts -> broken programs
    Production deployment: nightmare
  
  Post-CO-RE (libbpf + BTF era, 2019-present):
    Compile once: clang -target bpf
    BTF (BPF Type Format): kernel embeds type info at build time
    At load time: libbpf reads BTF from /sys/kernel/btf/vmlinux
    Relocation: adjusts struct field offsets to match current kernel
    Deploy: ship binary, runs on Ubuntu 20.04 5.4 or Fedora 6.7
    Production ready!
```

---

### Thought Experiment

Designing a zero-overhead production security audit tool:

```bash
# === Building a read-only file monitor with eBPF ===
# Goal: detect any process reading /etc/shadow (password file)
# Requirements: production system, zero impact, no polling

# Traditional approach (BAD):
# - inotify: generates event for every access, kernel overhead
# - audit daemon: high overhead, complex, generates many events
# - file integrity monitor (tripwire): only catches CHANGES, not reads
# - LD_PRELOAD hook: only works for dynamically linked programs

# eBPF approach (GOOD):
# Attach kprobe on vfs_read OR use LSM hook for file access

# Write the BPF program (shadow_audit.bpf.c):
# (simplified pseudo-code showing the concept)
#
# struct event {
#     u32 pid;
#     char comm[16];
#     char filename[64];
#     u64 timestamp;
# };
#
# struct {
#     __uint(type, BPF_MAP_TYPE_RINGBUF);
#     __uint(max_entries, 256 * 1024);
# } events SEC(".maps");
#
# // LSM hook: fires BEFORE file open is allowed
# // kernel 5.7+ with CONFIG_BPF_LSM
# SEC("lsm/file_open")
# int BPF_PROG(restrict_file_open, struct file *file) {
#     char target[] = "/etc/shadow";
#     char fname[64];
#     bpf_d_path(&file->f_path, fname, sizeof(fname));
#     if (bpf_strncmp(fname, sizeof(target), target) == 0) {
#         // Emit event to ring buffer (user space reads this)
#         struct event *e = bpf_ringbuf_reserve(&events, sizeof(*e), 0);
#         if (e) {
#             e->pid = bpf_get_current_pid_tgid() >> 32;
#             bpf_get_current_comm(e->comm, sizeof(e->comm));
#             bpf_probe_read_str(e->fname, sizeof(e->fname), fname);
#             e->timestamp = bpf_ktime_get_ns();
#             bpf_ringbuf_submit(e, 0);
#         }
#         // Return 0 to ALLOW the access (just audit, don't block)
#         // Return -EACCES to DENY the access (BPF LSM can enforce!)
#     }
#     return 0;
# }

# Load and run:
# ./shadow_audit  # loads BPF, starts printing events

# Output when someone reads /etc/shadow:
# TIME           PID     COMM         FILE
# 14:30:45.123   99999   sudo         /etc/shadow
# 14:30:45.124   12345   python3      /etc/shadow  <- suspicious!
# 14:30:50.999   44444   passwd       /etc/shadow  <- expected

# Performance characteristics:
# Overhead: only fires when /etc/shadow is accessed
# If /etc/shadow is never read: ZERO overhead (hook fires = ~100ns)
# vs. audit daemon: continuously running, sampling all syscalls
# vs. inotify: kernel generates event for every read syscall

# === bpftool: introspecting the eBPF universe ===

# See all BPF programs loaded on system:
sudo bpftool prog list
# Typical production system with Cilium:
# 1: cgroup_skb  name...   <- Cilium network policy
# 2: cgroup_skb  name...   <- more Cilium programs
# ...
# 48: xdp  name cilium_entrypoint  <- main XDP entry
# 78: tc  name to_host  <- TC hook
# Total: 50-200 BPF programs on a Cilium-managed node!

# See all BPF maps:
sudo bpftool map list
# 1: hash  name cilium_lb4_services  key 12B  value 8B  max_entries 65536
# <- BPF hash map: 65536 load balancer entries, O(1) lookup

# Check BPF map contents (inspect running state!):
sudo bpftool map dump id 1 | head -20
# key: 0a 00 00 01 0f a0 00 00  value: 01 00 00 00 00 00 00 00
# key = IP+port of backend; value = backend ID

# Profile BPF program (how long does it take?):
sudo bpftool prog profile id 48 duration 5 cycles instructions
# XDP program cilium_entrypoint:
# 5s, CPU 0: 1,234,567 runs, 123 ns/run, 456 cycles/run
# 5s, CPU 1: 2,345,678 runs, 98 ns/run, 389 cycles/run
# average: ~100ns per packet processing = 10M packets/second per CPU!
```

---

### Mental Model / Analogy

```
eBPF = JavaScript for the Linux kernel

Browser analogy:
  
  Web Browser (pre-JS era):
    Fixed behavior: request HTML, render, click links
    Want new feature (dynamic form validation)?
    -> Change browser source code, rebuild, release, wait for user upgrade
    -> Slow! Impractical for web developers!
  
  Web Browser (post-JS era):
    JavaScript VM: sandboxed execution of untrusted code in the browser
    JIT compiler: fast JS execution
    DOM API: JS programs can interact with page elements
    Events: JS code runs in response to user actions
    Result: web developer can change browser behavior WITHOUT browser update
    Safety: sandbox prevents JS from accessing user's files (mostly...)
  
  Linux Kernel (pre-eBPF era):
    Fixed behavior: network stack, scheduler, security, tracing
    Want new feature (DDoS mitigation)?
    -> Write kernel module, submit to LKML, wait 9-10 weeks, distro adoption...
    -> Or: ship binary kernel module (unsafe, taints kernel)
  
  Linux Kernel (post-eBPF era):
    eBPF VM: sandboxed execution of verified programs in the kernel
    JIT compiler: fast BPF execution (comparable to native C)
    BPF helper API: BPF programs interact with kernel data
    Hooks: BPF code runs in response to kernel events
    Result: user can change kernel behavior WITHOUT kernel update
    Safety: BPF verifier prevents BPF from crashing kernel

The analogy holds deeply:
  JS sandbox = BPF verifier (safety enforcement)
  JS V8 JIT = BPF JIT (performance)
  DOM/Browser API = BPF helper functions (approved kernel interaction)
  DOM events = BPF hooks (kernel events)
  node_modules/npm = BCC/libbpf ecosystem (libraries)
  TypeScript = eBPF with CO-RE (strongly typed, portable)
  Chrome Extensions = Cilium/Falco (eBPF-based products)

Verifier analogies:
  BPF verifier = TypeScript compiler (proves type safety before run)
  BPF verifier = Rust borrow checker (proves memory safety before run)
  BPF verifier = Java bytecode verifier (proves JVM safety before run)
  All: "prove safe before executing" rather than "fail at runtime"

XDP position in stack:
  OSI Layer 1 (PHY): NIC hardware
  Ethernet/NIC driver: DMA transfer from NIC to RAM
  XDP hook: HERE <- before sk_buff allocation, before any kernel processing
  sk_buff allocation: memory allocation for packet structure
  Netfilter (iptables): packet filtering
  Socket: recv() in user space
  
  "Too late" optimization = adding filter at application layer
  "Early" optimization = XDP (filter before kernel even allocates memory)
  Analogy: XDP vs application filter = bouncer at door vs security inside club
```

---

### Gradual Depth - Five Levels

**Level 1:**
What eBPF is (run programs in kernel safely). What problems it solves (tracing,
networking, security). Tools: bpftool, bcc-tools (opensnoop, execsnoop, etc.),
bpftrace. That Cilium uses eBPF for Kubernetes networking. That it requires
modern kernel (5.x+).

**Level 2:**
BPF verifier: what it checks and why. BPF program types: XDP vs kprobe vs
tracepoint vs LSM. BPF maps: key-value stores for communication between BPF
and user space. CO-RE and BTF: portability mechanism. JIT compilation and
performance implications. bpftool prog list and map list commands.

**Level 3:**
Write a basic BPF program with libbpf: skeleton API, CO-RE structs, ring buffer.
XDP program types and actions (XDP_PASS, XDP_DROP, XDP_TX, XDP_REDIRECT). TC
BPF vs XDP trade-offs. BPF map types (hash, array, lru_hash, ringbuf, perf_event_array).
BPF helper function categories. BPF LSM (kernel 5.7): writing security policies
as BPF programs. bpftrace one-liners for production investigation.

**Level 4:**
BPF verifier internals: register state tracking, pointer type analysis. Global
BPF variables and struct_ops for replacing kernel function tables. bpf_timer for
delayed execution from BPF. BPF CO-RE relocations in ELF sections. bpfd daemon:
system service for managing BPF program lifecycle. Performance analysis: BPF
overhead measurement with bpftool prog profile. Combining multiple BPF programs
with tail calls and BPF-to-BPF function calls.

**Level 5:**
BPF scheduler (sched_ext, kernel 6.11): custom CPU scheduling policies in BPF.
Impact: Meta running "scx_rusty" BPF scheduler in production, claims 10-15%
throughput improvement for specific workloads. BPF for kernel bypass storage
(early research: eBPF io_uring integration). The BPF verifier's fundamental
limitation: it does path explosion for complex programs (exponential number of
states). Mitigations: bounded loops (verified loop count), function calls
(separate state machines). BTF-CO-RE portability limits (some fields added
in newer kernels: conditional field access required). eBPF in Windows: Microsoft
announced "eBPF for Windows" project (2021, still in development).

---

### Code Example

**BAD - legacy BCC-based BPF (not portable, requires kernel headers on target):**
```python
# BAD: BCC-style BPF (pre-CO-RE, not portable)
# Requires: python3-bcc package AND kernel headers on EVERY target machine
# Different kernel versions: breaks silently or crashes

from bcc import BPF

# BAD: embedded C string, compiled AT RUNTIME on target machine
# Requires /usr/src/linux-headers-$(uname -r) to be installed
bpf_text = """
int trace_open(struct pt_regs *ctx, int dfd, const char __user *filename) {
    bpf_trace_printk("open called\\n");
    return 0;
}
"""
b = BPF(text=bpf_text)  # fails if no kernel headers!
b.attach_kprobe(event="do_sys_open", fn_name="trace_open")
# prints via /sys/kernel/debug/tracing/trace_pipe (slow, lossy!)
```

```c
/* GOOD: libbpf + CO-RE (modern approach, portable) */
/* Compile once on any machine, run on any kernel 5.2+ with BTF */

/* file: minimal.bpf.c (kernel-side BPF program) */
#include <vmlinux.h>          /* generated from BTF: all kernel types */
#include <bpf/bpf_helpers.h>  /* BPF helper macros */
#include <bpf/bpf_tracing.h>

/* License must be GPL for full access to kernel helpers */
char LICENSE[] SEC("license") = "GPL";

/* BPF ring buffer map: efficient user-kernel data transfer */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024); /* 256KB ring buffer */
} rb SEC(".maps");

/* Event structure shared with user space */
struct event {
    __u32 pid;
    char comm[16];
    char filename[256];
};

/* Attach to sys_enter_openat tracepoint (stable API, not kprobe) */
/* Tracepoints: more stable than kprobes (less likely to break) */
SEC("tp/syscalls/sys_enter_openat")
int handle_openat(struct trace_event_raw_sys_enter *ctx) {
    struct event *e;
    
    /* Reserve space in ring buffer */
    e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e)
        return 0;  /* ring buffer full: drop event */
    
    /* Fill event data */
    e->pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(e->comm, sizeof(e->comm));
    
    /* CO-RE: bpf_core_read handles different kernel versions */
    /* ctx->args[1] = filename argument of openat */
    bpf_probe_read_user_str(e->filename, sizeof(e->filename),
                            (void *)ctx->args[1]);
    
    /* Submit event (zero-copy to user space) */
    bpf_ringbuf_submit(e, 0);
    return 0;
}

/* Build: clang -O2 -target bpf -D__TARGET_ARCH_x86 \
 *   -I/usr/include/bpf -c minimal.bpf.c -o minimal.bpf.o
 * Generate skeleton: bpftool gen skeleton minimal.bpf.o > minimal.skel.h
 */
```

```c
/* file: minimal.c (user-space loader and reader) */
#include <stdio.h>
#include <signal.h>
#include "minimal.skel.h"  /* auto-generated by bpftool */

static struct minimal_bpf *skel;
static volatile bool running = true;

static int handle_event(void *ctx, void *data, size_t sz) {
    const struct event *e = data;
    printf("PID: %u COMM: %-16s FILE: %s\n",
           e->pid, e->comm, e->filename);
    return 0;
}

int main(void) {
    struct ring_buffer *rb = NULL;
    int err;
    
    /* Open, load, and verify BPF application */
    skel = minimal_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open/load BPF skeleton\n");
        return 1;
    }
    
    /* Attach BPF program to tracepoint */
    err = minimal_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF skeleton\n");
        goto cleanup;
    }
    
    /* Set up ring buffer polling */
    rb = ring_buffer__new(bpf_map__fd(skel->maps.rb),
                          handle_event, NULL, NULL);
    
    printf("Tracing file opens... Ctrl-C to stop.\n");
    while (running) {
        ring_buffer__poll(rb, 100 /* ms timeout */);
    }
    
cleanup:
    ring_buffer__free(rb);
    minimal_bpf__destroy(skel);
    return 0;
}

/* Build and run:
 * make
 * sudo ./minimal
 * Output: PID: 12345 COMM: vim             FILE: /home/user/code.c
 */
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "eBPF programs can crash the Linux kernel" | The entire design purpose of eBPF is to prevent this. The BPF verifier performs a mathematical proof of program safety before execution. It verifies: no unbounded loops (loops must be provably bounded), no out-of-bounds memory access (all pointer dereferences are bounds-checked), no null pointer dereference (all nullable pointers are null-checked before use), no type confusion (each register has a tracked type), no resource leaks (all reserved resources must be released or submitted on every code path). If ANY possible execution path violates these properties: the program is REJECTED and never runs. The safety guarantee is: a BPF program that passes verification CANNOT crash the kernel. (Note: bugs in the BPF verifier itself could theoretically allow unsafe programs, and several such bugs have been found and exploited - but those are bugs in the verifier, not in the design.) The practical effect: production companies (Meta, Google, Cloudflare, Netflix) run BPF code in production kernels with confidence that it won't cause kernel panics. |
| "eBPF is only useful for networking (it started as a packet filter)" | eBPF started as a packet filter (BPF, 1992, for tcpdump). Extended BPF (2014) added: maps, arbitrary JIT, program types beyond sockets. Today eBPF is used in five major domains: (1) NETWORKING: XDP for DDoS mitigation, TC for traffic shaping, cgroup for network policy (Cilium). (2) OBSERVABILITY: kprobes/uprobes/tracepoints for zero-overhead production profiling (Pixie, bpftrace, bcc-tools). (3) SECURITY: BPF LSM for security policies, seccomp-bpf for syscall filtering. (4) PERFORMANCE ANALYSIS: CPU profiling (bpftrace), latency histograms, I/O tracing. (5) SCHEDULING: sched_ext (kernel 6.11) for custom CPU schedulers in BPF. The networking origin is a historical artifact - eBPF is now a general-purpose kernel extension mechanism. The name "Berkeley Packet Filter" is a historical anachronism for the general-purpose tool it has become. |
| "CO-RE means any eBPF program runs on any kernel" | CO-RE (Compile Once - Run Everywhere) solves the STRUCT LAYOUT problem: a BPF program that accesses task_struct->mm->pgd no longer needs to know the exact byte offset of `pgd` in `mm_struct` (which changes between kernel versions). CO-RE + BTF handles this automatically. What CO-RE DOES NOT solve: (1) Feature availability: a BPF program using bpf_ringbuf (added in 5.8) won't load on kernel 5.4 (the map type doesn't exist). (2) Program type availability: BPF LSM requires CONFIG_BPF_LSM + kernel 5.7+. (3) Helper function availability: some BPF helpers are only available in newer kernels. (4) Missing BTF: CO-RE requires the kernel was built with CONFIG_DEBUG_INFO_BTF (most modern distros: yes; older IoT/embedded kernels: no). Portable BPF programs: need to guard feature usage with #ifdef or use runtime feature detection (libbpf's LINUX_VERSION_CODE checks), and handle "feature not available" gracefully. bcc-libbpf wrapper provides feature detection helpers for common cases. |
| "eBPF has replaced iptables/netfilter" | eBPF has COMPLEMENTED and in some cases REPLACED iptables in specific deployments, but not universally. Cilium replaces iptables with eBPF for Kubernetes pod networking: O(1) BPF map lookups vs O(N) iptables chain traversal - significant for large clusters (10,000+ services). But: (1) iptables is still default networking for most Kubernetes installations (kubeadm uses iptables/ipvs unless Cilium is specified). (2) Non-Kubernetes Linux systems still primarily use iptables or nftables (the official iptables successor). (3) nftables (the iptables replacement) is NOT eBPF-based but has similar O(log N) set lookups. (4) eBPF XDP requires either NIC driver support (native XDP) or generic XDP (slower). Not all NICs support native XDP. The claim "eBPF replaced iptables" is accurate for Cilium-managed Kubernetes clusters but misleading as a general statement about Linux networking. |

---

### Failure Modes & Diagnosis

```bash
# === BPF program rejected by verifier ===

# Load BPF program:
sudo bpftool prog load my_program.bpf.o /sys/fs/bpf/my_prog
# Error: libbpf: load bpf: invalid argument

# Check kernel log for verifier rejection:
dmesg | tail -50 | grep -A 20 "BPF program (interpreter)"
# Oops, wrong approach - check libbpf's verbose output:

# Enable verbose logging:
sudo bpftool prog load -d my_program.bpf.o /sys/fs/bpf/my_prog 2>&1 | head -50
# 0: (85) call bpf_map_lookup_elem#1
# 1: (bf) r3 = r0
# 2: (07) r3 += 8
# 3: (69) r4 = *(u16 *)(r3 +0)
#                              ^
# R3 pointer arithmetic on map value pointer outside range
# [3] = &map_value[8]: map value size=4, invalid access

# This means: accessed map[key] which has value size 4 bytes
# Then tried to read map[key]+8 -> out of bounds!
# Fix: check map value size matches the struct you're reading

# === CO-RE not working on target kernel ===

# Program loads on dev machine (kernel 6.1) but fails on target (kernel 5.4):
sudo ./my_bpf_tool
# libbpf: Error in bpf_object__relocate_data: ...
# libbpf: failed to open and load BPF object

# Diagnosis: check BTF availability:
ls /sys/kernel/btf/vmlinux
# ls: cannot access '/sys/kernel/btf/vmlinux': No such file or directory
# -> Kernel built WITHOUT CONFIG_DEBUG_INFO_BTF -> CO-RE fails!

# Check kernel config:
zcat /proc/config.gz | grep BTF
# CONFIG_DEBUG_INFO_BTF is not set
# -> No BTF available -> CO-RE cannot work

# Solutions:
# 1. Use BTF hub (btfhub.io) - precompiled BTF files for popular distros
#    Download /sys/kernel/btf/vmlinux for your exact kernel version
# 2. Rebuild kernel with CONFIG_DEBUG_INFO_BTF=y
# 3. Fall back to BCC (runtime compilation - requires kernel headers on target)

# === XDP program not processing packets ===

# Loaded XDP program on eth0 but packets are not being filtered:
ip link show eth0
# 2: eth0: <...> mtu 1500 ...
#     link/ether ...
#     ^ no "xdp" in output = XDP not attached!

# Attach XDP program to interface:
ip link set eth0 xdp obj my_xdp.bpf.o sec xdp
# or: using bpftool:
bpftool net attach xdp id 10 dev eth0

# Verify attachment:
ip link show eth0
# 2: eth0: <...> mtu 1500 xdpgeneric ...
#                          ^^ "xdpgeneric" = generic XDP mode
#                          (not native - slower!)
# For native XDP (fast):
# Requires: driver support (check: ethtool -i eth0 -> driver name)
# Supported drivers: ixgbe, mlx5, i40e, bnxt, ...
# Not supported: virtio-net in some configurations (use generic fallback)

# Compare XDP modes:
# xdp (native): driver-level, fastest, < 1 microsecond
# xdpgeneric:   after sk_buff alloc, slower but works on any NIC
# xdpoffload:   on NIC hardware (SmartNIC only, sub-100ns)
```

---

### Related Keywords

**Foundational:**
LNX-035 (eBPF basics), LNX-101 (eBPF platform engineering)

**Builds on this:**
LNX-114 (open problems)

**Related:**
LNX-035 (eBPF basics), LNX-101 (eBPF platform engineering), LNX-117 (namespace pattern)

---

### Quick Reference Card

| Tool | Purpose |
|------|---------|
| `bpftool prog list` | List all loaded BPF programs |
| `bpftool map list` | List all BPF maps |
| `bpftool prog show id N` | Details of program N |
| `bpftool prog profile id N` | Runtime performance of program |
| `bpftrace -l 'kprobe:vfs_*'` | List available tracepoints |
| `opensnoop-bpfcc` | Trace file opens (BCC) |
| `execsnoop-bpfcc` | Trace process executions |
| `cilium status` | Cilium eBPF networking status |

**3 things to remember:**
1. BPF verifier provides mathematical safety proof before execution: no crashes, no out-of-bounds, no infinite loops. This is what makes eBPF different from kernel modules (modules: no safety checks; BPF: fully verified). JIT compilation means verified BPF runs at native speed.
2. CO-RE (Compile Once - Run Everywhere) = BTF (kernel debug type info) + libbpf: allows compiling BPF once and running on any kernel 5.2+ with BTF. Check: `/sys/kernel/btf/vmlinux` must exist. Pre-CO-RE (BCC): compiled at runtime on target, required kernel headers on every production server.
3. Five eBPF domains: networking (XDP: fastest packet path, O(1) load balancing), observability (kprobe/tracepoint: zero-overhead production tracing), security (BPF LSM: programmable security policies), performance (profiling, flame graphs), scheduling (sched_ext: custom CPU schedulers). Cilium uses eBPF XDP to replace iptables at 100x better performance.

---

### Transferable Wisdom

The eBPF model of "safe sandboxed programs in the kernel" transfers to: WebAssembly
(WASM) in browsers and servers (safe sandboxed programs in user space - provably
safe via bytecode verification), AWS Firecracker (lightweight VM via KVM - fast,
safe isolation like eBPF but at VM level), eBPF for Windows (Microsoft's cross-
platform BPF implementation), LLVM IR as universal "kernel" for compilers
(programs compiled to IR, run safely in the LLVM VM). The BPF verifier technique
(type-directed program analysis, proving safety statically) transfers to: Rust's
borrow checker (proves memory safety without GC), Java's bytecode verifier (proves
type safety before JVM execution), Dafny/TLA+ formal verification (proves algorithm
correctness). The BPF map concept (shared state between kernel and user space via
fd) is used in: io_uring's submission/completion queues, shared memory IPC, DPDK
mempool (user-space NIC). CO-RE's "adapt at load time from type metadata" is the
same technique as: JVM class loading with reflection, LLVM bitcode linking with
LTO (link-time type information), protobuf evolution (type metadata allows reading
newer/older messages). The "programmable hook" architecture (attach code to defined
points in a fixed system) is used in: browser extensions (defined DOM APIs),
Kubernetes admission webhooks (defined admission control points), AWS Lambda
@Edge (defined CDN hook points), Jenkins pipeline hooks (defined CI stages).

---

### The Surprising Truth

The BPF verifier rejects programs it cannot prove safe, even if they ARE safe.
It is "sound but not complete" in the formal verification sense - it will never
accept an unsafe program (sound), but it WILL reject some safe programs (incomplete).
This means: a programmer can write a correct, safe BPF program that the verifier
refuses to load. The verifier's analysis is path-based: if a program has 2^100
possible paths (from nested conditionals), the verifier cannot analyze all paths.
It has limits: 1,000,000 instructions to analyze, 64 nested call levels.

The practical consequence: complex eBPF programs sometimes need to be restructured
NOT to be correct, but to be PROVABLY correct to the verifier's satisfaction.
Developers may need to add redundant NULL checks that are logically unnecessary
(the pointer can't be NULL in practice) because the verifier tracks that the
pointer is nullable at that point in the state machine. The verifier is a proof
assistant, not an oracle - you must help it understand your program's invariants.

This same trade-off appears in: dependent type systems (Coq, Lean: you prove
properties, type checker verifies the proof), Rust's borrow checker (sometimes
requires restructuring correct code to satisfy the checker), TLA+ model checking
(state space explosion for complex protocols).

---

### Mastery Checklist

- [ ] Can explain the eBPF execution model: write C -> compile to BPF bytecode -> verify -> JIT -> attach to hook
- [ ] Understands what the BPF verifier checks and why it's the safety foundation
- [ ] Knows CO-RE and BTF: how they solve the portability problem, and what prerequisites they require
- [ ] Can use bpftool to inspect running BPF programs and maps on a live system
- [ ] Understands XDP position in network stack and why it enables high-performance packet processing

---

### Think About This

1. The eBPF verifier is described as "Turing-incomplete by design" - you cannot
   write a BPF program that runs indefinitely. This is a fundamental tradeoff:
   safety requires bounded programs. But many useful algorithms are inherently
   iterative (packet reassembly, flow tracking). How does eBPF work around this
   limitation? Compare: helper functions (delegate unbounded work to the kernel),
   tail calls (chain BPF programs for longer logic), BPF maps (accumulate state
   across multiple invocations). Is "Turing-incomplete" always the right safety
   model, or could there be a more expressive but still safe eBPF? What would
   such a system look like?

2. Meta (Facebook) runs the "scx_rusty" BPF CPU scheduler in production on their
   data center fleet, claiming 10-15% throughput improvement for specific workloads.
   This requires: sched_ext (experimental in 5.x, merged in 6.11). Analyze the
   risk/reward: a bug in a BPF scheduler doesn't cause a kernel panic (the verifier
   ensures safety), but could cause task starvation (all tasks on one CPU) or live-
   lock (tasks continuously migrated). How should production use of sched_ext be
   validated? What monitoring would you add? When is "experimental kernel feature
   in production for performance" the right call?

3. eBPF programs can be used to implement kernel rootkits (malicious programs
   that hide files, network connections, or processes). The BPF LSM (security
   module) was designed to ADD security policies, but eBPF can also observe and
   potentially interfere with security mechanisms. CAP_BPF (or root) is required
   to load BPF programs. Analyze: is CAP_BPF privilege sufficient protection?
   What happens in a container that has cap_bpf? How should security-conscious
   teams restrict BPF program loading? Compare eBPF's security posture to:
   kernel modules (no restrictions by default), user-space tools (no kernel
   visibility), and hardware-level attestation (TPM-based boot measurement).

---

### Interview Deep-Dive

**Foundational:**
Q: What is eBPF and how does it differ from writing a traditional kernel module?
A: KERNEL MODULE vs eBPF - THE CORE DISTINCTION: KERNEL MODULE: compiled C code that runs in kernel space (Ring 0) with zero safety checks. Can: allocate kernel memory (kmalloc), access any kernel data structure, crash the entire system with a single bad pointer. Loaded via insmod/modprobe. A bug in a module crashes all running processes, corrupts filesystem state, panics the kernel. Requires: kernel headers matching exact kernel version, recompilation when kernel updates, often GPLv2 compatible code. eBPF PROGRAM: restricted bytecode that runs in kernel space but: must pass BPF verifier (mathematical safety proof) before executing. Cannot: access arbitrary memory (all pointer accesses bounds-checked by verifier), run unbounded loops (loop termination must be provable), call arbitrary kernel functions (only approved BPF helper functions). Can: read kernel data structures, modify packet data, access BPF maps, emit events to user space. WHAT THIS MEANS IN PRACTICE: Production safety: eBPF programs can be deployed to production systems without the risk of kernel crashes. If the verifier rejects a program: it's caught at load time, not at runtime. If a module had the same bug: kernel panic during execution. Deployment: eBPF programs are portable (CO-RE + BTF) and don't require kernel recompilation. Kernel module: need matching kernel headers, breaks between kernel versions. Speed: both JIT compiled to native code - similar performance for equivalent operations. eBPF limits (stack: 512 bytes, JIT code size: typically <1MB) can force restructuring complex logic. WHEN TO USE EACH: Use eBPF for: networking (XDP, TC), observability (kprobes, tracepoints), security policies (BPF LSM), CPU profiling. Use kernel module for: hardware driver (interrupt handler, DMA, register I/O), implementing a new filesystem, complex in-kernel data structures beyond eBPF's constraints. The trend: more functionality moving from "requires kernel module" to "possible with eBPF" as BPF capabilities expand.

**Expert:**
Q: How does Cilium use eBPF to improve Kubernetes networking performance compared to iptables?
A: THE FUNDAMENTAL PROBLEM WITH IPTABLES AT SCALE: Kubernetes uses Services (ClusterIP) to load balance traffic across pods. Default implementation (kube-proxy): generates iptables rules - one chain per service, one rule per backend pod endpoint. Scale: 10,000 services, 50,000 pod endpoints = 10,000 iptables chains, 50,000 rules. Problem: iptables is a LINKED LIST of rules. Each packet: traverse from rule 1 to rule N until match found. Average: N/2 rule checks per packet. At 50,000 rules: 25,000 rule checks per packet. At 100,000 packets/second: 2.5 BILLION rule checks/second. Even with conntrack caching (established connections skip rules): new connections at scale suffer. CILIUM'S APPROACH - eBPF MAPS: Replace iptables chains with BPF hash maps. BPF hash maps: O(1) lookup regardless of size (hash table, not linked list). 10,000 services: ONE BPF map lookup per packet (same as 10 services). Attachment points: TC hook (Layer 3/4) or XDP (Layer 2, before sk_buff). Load balancing: BPF program looks up service IP:port in BPF map -> gets array of backend IPs -> consistent hash selects backend -> rewrites packet dst IP:port. PERFORMANCE DIFFERENCE: kube-proxy (iptables): packet traverses N iptables rules. O(N) per packet, connection setup: ~microseconds * N. Cilium (eBPF): single BPF map lookup. O(1) per packet. Connection setup: ~1-2 microseconds regardless of service count. Benchmark (reported by Cilium team): 1000 services: Cilium 2x faster. 10,000 services: Cilium 10x faster. 100,000 services: theoretical 100x (iptables becomes unusable). ADDITIONAL CILIUM FEATURES ONLY POSSIBLE WITH eBPF: Per-pod network policy enforcement at XDP speed. Identity-based security (crypto identity in BPF map, not just IP-based). Direct server return (DSR) for load balancing: bypass return path, save 50% bandwidth. BPF-based L7 policy (can inspect HTTP headers). The architectural insight: iptables was designed for stateful firewall rules (O(N) acceptable for N <= 1000). Kubernetes services at scale (N >= 10,000) exceed iptables' design assumptions. eBPF maps match the data structure (service lookup) to the algorithm (hash table O(1)).
