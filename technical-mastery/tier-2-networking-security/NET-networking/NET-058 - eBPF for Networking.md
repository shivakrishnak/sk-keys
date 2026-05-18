---
id: NET-058
title: "eBPF for Networking"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-057
used_by: NET-063
related: NET-057, NET-063, NET-052
tags:
  - networking
  - ebpf
  - bpf
  - linux-kernel
  - performance
  - observability
  - xdp
  - cilium
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 58
permalink: /technical-mastery/net/ebpf-for-networking/
---

**⚡ TL;DR** - eBPF (extended Berkeley Packet Filter)
runs sandboxed programs in the Linux kernel without
modifying kernel source or loading kernel modules.
For networking: intercept and modify packets at the
earliest possible point (XDP - before sk_buff allocation),
implement load balancing in the kernel (Cilium uses this),
collect per-flow metrics without userspace overhead, and
enforce network policies at line rate. Used by Meta,
Cloudflare, Netflix, and every major Kubernetes CNI.
Tools: bpftrace (tracing), bpftool (inspection), Cilium
(K8s CNI), Katran (Facebook LB).

| #058 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | epoll and io_uring (NET-057) | |
| **Used by:** | Network Observability with Prometheus (NET-063) | |
| **Related:** | epoll and io_uring, Network Observability, Network Segmentation | |

---

### 🔥 The Problem This Solves

Cloudflare needs to drop 320 Gbps DDoS traffic.
Traditional kernel path: network stack (sk_buff alloc,
protocol parsing, iptables rules, socket delivery) takes
~5 microseconds per packet. At 320 Gbps × 1500 bytes:
26M packets/second. 26M × 5μs = 130 CPU seconds/second.
Impossible on any hardware. XDP (eBPF at NIC driver level):
drop decision at ~150ns per packet. 26M × 0.15μs = 3.9
CPU seconds/second. Feasible on a 4-core machine. eBPF
makes this possible without kernel modifications.

---

### 🧠 Intuition: Code That Runs in the Kernel

```
Traditional packet path (slow, high overhead):
  NIC → sk_buff allocation → IP layer → TCP layer
  → socket → userspace application

eBPF/XDP packet path (fast, minimal overhead):
  NIC → eBPF program (at NIC driver, or tc, or socket level)
      → DROP / PASS / REDIRECT / TX_BACK

eBPF safety guarantees (why kernel accepts it):
  1. Verifier: proves program terminates (no infinite loops)
  2. Verifier: proves all memory accesses are safe
  3. JIT compiled to native machine code (fast)
  4. Cannot crash kernel (verifier prevents it)
  5. Cannot call arbitrary kernel functions
     (only bpf_helpers API)

Think of eBPF as:
  SQL: you describe WHAT you want (not HOW)
  eBPF: you describe WHAT to do with each packet
  Kernel: executes it safely and efficiently
```

---

### ⚙️ eBPF Hook Points for Networking

```
Packet processing attachment points (in order):

1. XDP (eXpress Data Path):
   Location: NIC driver, before sk_buff allocation
   Latency: ~150ns per packet
   Use: DDoS mitigation, load balancing, packet filtering
   Return: XDP_PASS, XDP_DROP, XDP_TX, XDP_REDIRECT

2. tc (Traffic Control):
   Location: After sk_buff, before/after IP routing
   Latency: ~1-5μs
   Use: Packet modification, bandwidth shaping
   Both ingress (tc_bpf CLSACT ingress) and egress

3. socket_filter (original BPF):
   Location: On socket receive path
   Use: tcpdump's filter, packet capture
   Return: packet length to keep, 0 to drop

4. kprobes/tracepoints:
   Location: Any kernel function
   Use: Observability (bpftrace, Cilium Hubble)
   No packet modification, trace only
   
5. cgroup eBPF:
   Location: Per-cgroup (container) network rules
   Use: Kubernetes NetworkPolicy in Cilium
   Controls: socket-level accept/connect

Insertion points diagram:

  NIC → [XDP] → sk_buff → [tc ingress] → IP → TCP
     → [tc egress] → NIC (outbound)
     → socket → [socket_filter] → userspace app
```

---

### ⚙️ XDP: Maximum Performance Packet Drop

```c
// Minimal XDP program: drop all UDP on port 53
// (DNS amplification DDoS mitigation)
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <bpf/bpf_helpers.h>

SEC("xdp")
int drop_dns_amplification(struct xdp_md *ctx) {
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;

    // Bounds check (required by verifier!)
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;  // malformed - pass to stack

    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;  // not IPv4

    struct iphdr *iph = (void *)(eth + 1);
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;

    if (iph->protocol != IPPROTO_UDP)
        return XDP_PASS;  // not UDP

    struct udphdr *udp = (void *)(iph + 1);
    if ((void *)(udp + 1) > data_end)
        return XDP_PASS;

    // Drop UDP source port 53 (DNS response = amplification attack)
    if (udp->source == __constant_htons(53))
        return XDP_DROP;  // drop the packet

    return XDP_PASS;
}

char _license[] SEC("license") = "GPL";

// Load and attach:
// ip link set dev eth0 xdp obj drop_dns.o sec xdp
// (or using xdp-loader tool)
```

---

### ⚙️ bpftrace: Kernel-Level Network Tracing

```bash
# bpftrace: high-level language for eBPF tracing programs

# Trace all TCP connections being established:
sudo bpftrace -e '
kprobe:tcp_connect {
    printf("CONNECT: PID %d (%s) → %s:%d\n",
        pid, comm,
        ntop(AF_INET, args->daddr),
        ntohs(args->dport)
    );
}'
# Output shows every outbound TCP connection attempt:
# CONNECT: PID 1234 (curl) → 142.250.80.14:443

# Count packets by port (live histogram):
sudo bpftrace -e '
tracepoint:net:netif_receive_skb {
    @packets[args->len > 1400 ? "large" : "small"]++;
}
interval:s:1 {
    print(@packets);
    clear(@packets);
}'

# Measure TCP receive latency (socket to application):
sudo bpftrace -e '
kprobe:tcp_recvmsg { @start[tid] = nsecs; }
kretprobe:tcp_recvmsg /@start[tid]/ {
    @latency_us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'

# Find which processes are making the most connections:
sudo bpftrace -e '
kprobe:tcp_connect {
    @conn[comm]++;
}
END { print(@conn); }'

# Profile packet drops (useful during DDoS):
sudo bpftrace -e '
tracepoint:skb:kfree_skb {
    @drops[args->reason]++;
}
interval:s:1 { print(@drops); clear(@drops); }'
```

---

### ⚙️ Cilium: eBPF-Powered Kubernetes Networking

```yaml
# Cilium replaces kube-proxy and iptables with eBPF programs
# Result: faster, more observable, more powerful networking

# Install Cilium as Kubernetes CNI:
# helm install cilium cilium/cilium \
#   --set kubeProxyReplacement=strict \
#   --set bpf.masquerade=true

# Cilium NetworkPolicy (more powerful than K8s NetworkPolicy)
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-frontend-get-only
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: backend
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"      # L7 HTTP method policy!
          path: "/api/v1/.*" # only GET on /api/v1/*
          # DELETE /api/v1/users → blocked at kernel level
          # GET /api/v1/users → allowed
          # L7 enforcement via eBPF proxy in kernel

---
# Hubble: Cilium's observability component
# Provides real-time flow visibility via eBPF

# View flows in Kubernetes cluster:
# hubble observe --namespace production --follow
# Output:
# Feb  1 14:30:01 frontend (ID:1) → backend (ID:2) TCP Flags: SYN
# Feb  1 14:30:01 backend (ID:2) → frontend (ID:1) TCP Flags: SYN-ACK
# Feb  1 14:30:01 frontend (ID:1) → backend (ID:2) HTTP/1.1 GET /api/v1/users
# Feb  1 14:30:01 backend (ID:2) → frontend (ID:1) HTTP/1.1 200 OK
```

---

### ⚙️ Wrong vs Right: iptables vs eBPF for Service Mesh

```bash
# BAD: kube-proxy iptables for Kubernetes services
# (default Kubernetes, pre-Cilium)

# kube-proxy adds iptables rules for each service:
sudo iptables -L KUBE-SERVICES | wc -l
# 500 services × 10 pods each = thousands of rules
# Every packet: linear scan of ALL iptables rules
# 10,000 iptables rules: ~500μs per packet (at CPU)
# Service discovery: O(n) in number of services

# Scale problem: 10,000 pods, 1,000 services
# iptables NAT rules: ~100,000 entries
# Every connection: scans all 100,000 rules to find match
# This is why Kubernetes clusters slow down with many services

# GOOD: Cilium with eBPF (replaces kube-proxy)
# eBPF uses hash maps (BPF_MAP_TYPE_HASH)
# Lookup: O(1) regardless of number of services
# 10,000 pods, 1,000 services: same speed as 10 services

# Measured improvement (published by Cilium):
# 50% improvement in network latency at 1,000 services
# 300% improvement at 10,000 services
# Eliminates conntrack for direct routing

# Install check:
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl exec -n kube-system cilium-xyz -- cilium status
```

---

### 📐 Scale Considerations

```
eBPF map size limits:
  BPF_MAP_TYPE_HASH: max ~1M entries (configurable)
  BPF_MAP_TYPE_ARRAY: max ~4GB
  Per-CPU maps: each CPU has separate copy (no lock contention)

XDP performance numbers (published):
  Without XDP (kernel path): ~2M pps per core
  XDP (driver mode): ~14M pps per core
  XDP (offload to NIC): ~50M+ pps (SmartNIC)
  
  At 100 Gbps line rate:
  Packet size 64 bytes: ~148M pps
  Need: 148M / 14M = ~11 cores for XDP
  (vs 148M / 2M = ~74 cores without XDP)

Production eBPF users:
  Meta: KATRAN load balancer (XDP, replaces IPVS)
    - 40 Gbps per server, millions of pps
  Cloudflare: DDoS mitigation (XDP drop at 3.8 Tbps)
  Netflix: Atlas in-kernel tracing (bpftrace)
  Google: gVisor with eBPF sandboxing

Limits and cautions:
  eBPF program size: 1 million instructions max
  Stack size: 512 bytes per frame (helpers for larger data)
  Verifier: complex programs may fail verification
  Kernel version: most features require Linux 5.x+
```

---

### 🧭 Decision Guide

```
When eBPF is the right tool:

XDP (packet processing):
  DDoS mitigation at line rate
  Hardware load balancing
  Packet sampling (1-in-N)
  Fast ACL enforcement (firewall)
  Protocol translation (IPv4↔IPv6)

tc BPF (traffic control):
  Bandwidth shaping per flow
  Service mesh sidecar (Cilium without iptables)
  Traffic steering (A/B testing at network layer)

bpftrace/kprobes (observability):
  "Which process is opening TCP connections to X?"
  "What is the latency distribution of DNS queries?"
  "Which connections are being dropped and why?"
  → Always-on: unlike strace, low overhead

When NOT to use eBPF directly:
  Application-level routing: use service mesh
  HTTP routing: use API gateway or ingress controller
  Simple firewall rules: iptables is sufficient
  Need cross-kernel-version support: wait for stable API

Getting started:
  Install: bpftrace, bcc-tools (provides execsnoop, tcptracer)
  
  Quick tracing commands:
  sudo tcptracer -p 1234     # trace connections for PID
  sudo tcpconnect            # trace all new TCP connections
  sudo tcpaccept             # trace all accepted TCP connections
  sudo tcpretrans            # trace TCP retransmissions
  (all from bcc-tools package)

Maturity:
  bpftrace: stable, production-safe
  XDP: stable in Linux 5.x+
  Cilium: production-grade, used by large enterprises
  io_uring+eBPF: emerging, rapidly developing (2024+)
```