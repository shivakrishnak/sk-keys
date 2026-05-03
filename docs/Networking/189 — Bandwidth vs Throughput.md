---
layout: default
title: "Bandwidth vs Throughput"
parent: "Networking"
nav_order: 189
permalink: /networking/bandwidth-vs-throughput/
number: "0189"
category: Networking
difficulty: ★★☆
depends_on: TCP, Packet Loss Latency & Jitter, Congestion Control
used_by: System Design, Observability & SRE, Distributed Systems
related: Packet Loss Latency & Jitter, Network Latency Optimization, TCP, Congestion Control, Sliding Window
tags:
  - networking
  - bandwidth
  - throughput
  - goodput
  - performance
  - bdp
---

# 189 — Bandwidth vs Throughput

⚡ TL;DR — **Bandwidth** is the maximum capacity of a link (the pipe's diameter). **Throughput** is the actual data transferred per second (what flows through the pipe). **Goodput** is the application-level throughput (useful data, excluding retransmissions and overhead). Throughput ≤ Bandwidth, and is limited by: packet loss (TCP halves window), TCP buffer sizes vs BDP (Bandwidth-Delay Product), congestion, and protocol overhead.

---

### 🔥 The Problem This Solves

Marketing says "10 Gbps network." Engineers observe 100 Mbps actual transfer speeds. Why? The gap between bandwidth (capacity) and throughput (actual) is one of the most common and misunderstood performance problems. Understanding the gap — and the Bandwidth-Delay Product — is essential for diagnosing slow network transfers and tuning systems to use available capacity.

---

### 📘 Textbook Definition

**Bandwidth:** The maximum data transfer rate of a network link, expressed in bits per second (Mbps, Gbps). Determined by physical media (fibre, copper, wireless). A 1 Gbps Ethernet link can transmit up to 1 billion bits per second.

**Throughput:** The actual rate of successful data transfer in a given time period. Always ≤ bandwidth. Reduced by: packet loss (retransmissions), protocol overhead (TCP/IP headers, TLS), flow control (receive window size), congestion control (sender window size).

**Goodput:** Application-level useful data transferred per second. Excludes: retransmitted data, TCP/IP/TLS headers, TCP ACKs, ICMP, padding. Goodput ≤ Throughput ≤ Bandwidth.

**Bandwidth-Delay Product (BDP):** The amount of data "in flight" on a network path at full utilisation. BDP = bandwidth × RTT. To saturate a link, TCP's buffer size must be ≥ BDP.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bandwidth is the pipe's size; throughput is how much actually flows through it — limited by TCP window size, packet loss, and protocol overhead. BDP tells you how big the TCP buffer needs to be to saturate the link.

**One analogy:**

> Bandwidth = width of a highway (8 lanes vs 2 lanes). Throughput = actual cars per hour on that highway (affected by accidents, traffic lights, speed limits). Goodput = cars carrying passengers (excludes empty service vehicles). A wide highway (high bandwidth) has low throughput if there's a traffic jam 10 miles ahead (bottleneck) or if cars keep crashing and turn around (retransmissions).

---

### 🔩 First Principles Explanation

**BANDWIDTH vs THROUGHPUT — THE GAP:**

```
Link bandwidth:  1 Gbps (hardware capacity)
TCP overhead:    ~3% (headers, ACKs)
Theoretical max: ~970 Mbps

Actual throughput scenarios:

1. Local LAN (1ms RTT, 0% loss):
   BDP = 1 Gbps × 0.001s = 125 KB
   Default TCP buffer: 4 MB >> BDP → saturates link
   Throughput: ~940 Mbps ✓

2. Cross-country (100ms RTT, 0% loss):
   BDP = 1 Gbps × 0.1s = 12.5 MB
   Default TCP buffer: 4 MB << BDP → bottleneck!
   Throughput: 4 MB / 0.1s = 320 Mbps (only 32% utilisation)
   Fix: set tcp_rmem/wmem max to 16+ MB

3. Cross-country (100ms RTT, 1% loss):
   Mathis formula: MSS/RTT × 1/√loss
   = 1460 / 0.1 × 1/√0.01 = 1.4 Mbps (!!)
   Link is 1 Gbps; TCP gets 1.4 Mbps due to loss
   → fix the packet loss first (1% is catastrophic for TCP)

4. WAN with default MTU (1500B) vs Jumbo Frames (9000B):
   Each MTU = one unit of work (header + payload)
   Larger MTU: fewer headers → higher goodput ratio
   Jumbo frames: 9000B payload vs 9000B + 40B header = 99.6% efficiency
   vs 1500B: 1460B payload + 40B header = 97.3% efficiency
   (significant at 10 Gbps+)
```

**BDP CALCULATION AND TCP TUNING:**

```bash
# BDP = Bandwidth × RTT

# Example: 10 Gbps link, 50ms RTT (cross-datacenter)
# BDP = 10 × 10^9 bps × 0.05s = 500 × 10^6 bits = 62.5 MB

# Check current TCP buffer settings
cat /proc/sys/net/ipv4/tcp_rmem
# 4096   87380   6291456  (min, default, max = 6 MB)
# Max buffer 6 MB < BDP 62.5 MB → throughput limited!

# Tune for high-bandwidth, high-latency links
sysctl -w net.core.rmem_max=134217728      # 128 MB
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"

# Enable TCP window scaling (required for windows > 65535)
sysctl -w net.ipv4.tcp_window_scaling=1

# After tuning: measure throughput
iperf3 -c remote-host -t 30 -P 4
# Before: 320 Mbps; After: 9.4 Gbps (if bottleneck was buffer size)
```

**MEASURING THE GAP:**

```bash
# Measure bandwidth (theoretical max)
iperf3 -c target -t 10 -P 16    # 16 parallel streams, saturate link
# Reports: sender bandwidth (link capacity)

# Measure throughput (actual TCP performance)
iperf3 -c target -t 30           # single stream
# Reports: actual throughput, retransmissions

# Retransmissions = packet loss indicator
# High retransmits → fix loss before tuning buffers

# Measure per-second throughput
iperf3 -c target -t 30 -i 1     # report every 1 second
# Watch for throughput variation = congestion events

# Web: measure with curl (time to transfer a large file)
curl -o /dev/null -w "%{speed_download}\n" https://target/bigfile
```

---

### 🧪 Thought Experiment

**THE BUFFER BLOAT vs BDP TRADE-OFF:**
Increasing TCP buffer size improves throughput on high-BDP paths. BUT: over-large buffers + congestion = bufferbloat (packets queue for 500ms). The right buffer size is: ≥ BDP to saturate the link, but no larger (to keep queuing delay low). BBR congestion control (Google) solves this differently: it models the network's bottleneck bandwidth and RTT directly, maintains a near-optimal inflight byte count without large buffers. BBR improves throughput on high-BDP paths AND reduces latency compared to CUBIC+large-buffers.

---

### 🧠 Mental Model / Analogy

> A river (link) has a maximum flow capacity (bandwidth). The actual water flowing through (throughput) depends on: upstream dams (sender window / congestion control), channel blockages (packet loss causing retransmission), and the river's cross-section × length (BDP — how much water is "in the river" at once). To transport maximum water, you need both a wide channel AND enough water in it. A tiny trickle (small TCP window) on a wide channel (high bandwidth, high latency) wastes capacity — the water doesn't fill the river.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Bandwidth is capacity. Throughput is what you actually get. A 1 Gbps connection can give you less than 10 Mbps if there's packet loss or the TCP window is too small.

**Level 2:** Diagnose throughput gaps: run `iperf3` to measure; check retransmissions in iperf3 output (= loss); compare single-stream vs multi-stream throughput (single stream limited by RTT × window, multi-stream compensates); check socket buffer size vs BDP.

**Level 3:** TCP throughput formula: `Throughput = Window_Size / RTT`. With default 4MB window, 100ms RTT: max throughput = 4MB / 0.1s = 40 MB/s = 320 Mbps — regardless of link speed. Increasing max socket buffers (tcp_rmem/wmem) allows the OS to auto-tune window size up to the BDP. Enable `tcp_moderate_rcvbuf` (on by default in Linux 4+) for automatic buffer tuning.

**Level 4:** BBR (Bottleneck Bandwidth and RTT) vs CUBIC: CUBIC uses loss as a congestion signal and slows down aggressively on loss. On wireless links with high natural loss rate (not congestion-loss), CUBIC dramatically underutilises bandwidth. BBR maintains the "bandwidth-delay product" as its operating point — it probes the bottleneck bandwidth with BtlBw × RTprop = inflight_optimal. BBR fills the pipe without overfilling buffers, yielding higher throughput and lower latency simultaneously. At Google, BBR on YouTube increased global throughput by 4% and reduced buffering by 14%.

---

### ⚙️ How It Works (Mechanism)

```bash
# Full throughput diagnosis workflow

# 1. Measure bandwidth ceiling (many parallel streams)
iperf3 -c target -P 16 -t 10

# 2. Measure single-stream TCP throughput
iperf3 -c target -t 30

# 3. Compare: if (1) >> (2): likely RTT × window bottleneck

# 4. Calculate BDP
ping -c 100 target | tail -1
# rtt avg = 80ms → BDP = link_bandwidth × 0.08
# For 10 Gbps: BDP = 10 × 10^9 × 0.08 / 8 = 100 MB

# 5. Check TCP buffer
cat /proc/sys/net/ipv4/tcp_rmem
# If max < BDP: increase buffer

# 6. Check for packet loss
iperf3 -c target -t 30 | grep -i retransmit
# Retransmits > 0: fix loss before tuning buffers

# 7. Enable BBR for better throughput (Linux 4.9+)
sysctl -w net.ipv4.tcp_congestion_control=bbr
sysctl -w net.core.default_qdisc=fq
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Bandwidth vs Throughput stack:

Physical link:  10 Gbps (1.25 GB/s)
                ↓ minus link overhead (framing, IFG)
L2 throughput:  ~9.8 Gbps
                ↓ minus IP/TCP/TLS headers (~3%)
Throughput:     ~9.5 Gbps max (no loss, optimal buffers)
                ↓ minus packet loss (1% → lose 87%)
                ↓ minus buffer size < BDP (loses up to 90%)
                ↓ minus congestion (AIMD window reduction)
Actual:         could be 100 Mbps on a 10 Gbps link
                ↓ minus retransmissions, ACKs
Goodput:        useful application data
```

---

### 💻 Code Example

```python
def calculate_tcp_throughput(
    bandwidth_gbps: float,
    rtt_ms: float,
    packet_loss_pct: float,
    tcp_buffer_mb: float = 4.0
) -> dict:
    """Estimate theoretical TCP throughput given network conditions."""
    bandwidth_bytes = bandwidth_gbps * 1e9 / 8
    rtt_s = rtt_ms / 1000
    buffer_bytes = tcp_buffer_mb * 1024 * 1024

    # BDP = bandwidth × RTT (bytes in flight to saturate link)
    bdp_bytes = bandwidth_bytes * rtt_s

    # Buffer-limited throughput
    buffer_limited = buffer_bytes / rtt_s

    # Loss-limited throughput (Mathis formula)
    mss_bytes = 1460  # typical MSS
    loss_fraction = packet_loss_pct / 100
    if loss_fraction > 0:
        loss_limited = (mss_bytes / rtt_s) * (1 / (loss_fraction ** 0.5))
    else:
        loss_limited = float('inf')

    # Actual throughput = min of all limits
    actual = min(bandwidth_bytes, buffer_limited, loss_limited)
    efficiency = (actual / bandwidth_bytes) * 100

    return {
        "bandwidth_mbps": bandwidth_gbps * 1000,
        "bdp_mb": bdp_bytes / (1024 * 1024),
        "buffer_mb": tcp_buffer_mb,
        "buffer_limited_mbps": buffer_limited / 1e6,
        "loss_limited_mbps": loss_limited / 1e6 if loss_fraction > 0 else None,
        "actual_throughput_mbps": actual / 1e6,
        "efficiency_pct": efficiency,
        "bottleneck": (
            "packet_loss" if loss_limited < buffer_limited
            else "tcp_buffer" if buffer_limited < bandwidth_bytes
            else "none"
        )
    }

# Examples
examples = [
    (1.0, 1.0, 0.0, 4.0),    # LAN
    (1.0, 100.0, 0.0, 4.0),  # WAN, small buffer
    (1.0, 100.0, 0.0, 16.0), # WAN, larger buffer
    (1.0, 100.0, 1.0, 16.0), # WAN, 1% loss
]
for bw, rtt, loss, buf in examples:
    r = calculate_tcp_throughput(bw, rtt, loss, buf)
    print(f"BW={bw}Gbps RTT={rtt}ms loss={loss}% buf={buf}MB → "
          f"{r['actual_throughput_mbps']:.1f}Mbps "
          f"({r['efficiency_pct']:.1f}%) bottleneck={r['bottleneck']}")
```

---

### ⚖️ Comparison Table

| Scenario                            | Bandwidth | Throughput         | Bottleneck        |
| ----------------------------------- | --------- | ------------------ | ----------------- |
| LAN (1ms RTT, no loss)              | 1 Gbps    | ~940 Mbps          | Protocol overhead |
| WAN (100ms RTT, no loss, 4MB buf)   | 1 Gbps    | ~320 Mbps          | TCP buffer < BDP  |
| WAN (100ms RTT, no loss, 128MB buf) | 1 Gbps    | ~940 Mbps          | None              |
| WAN (100ms RTT, 1% loss)            | 1 Gbps    | ~11 Mbps           | Packet loss       |
| Satellite (600ms RTT, no loss)      | 100 Mbps  | ~53 Mbps (4MB buf) | TCP buffer < BDP  |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                            |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Bandwidth upgrade fixes slow transfers | If the bottleneck is TCP buffer size vs BDP, or packet loss, more bandwidth doesn't help. Diagnose first with iperf3.              |
| Single iperf3 stream = bandwidth       | Single iperf3 stream shows RTT-limited throughput. Use `-P 16` for parallel streams to approach link bandwidth.                    |
| Retransmissions are rare/harmless      | In high-loss environments, retransmissions account for 5-50% of bandwidth. Goodput can be far below throughput in these scenarios. |

---

### 🚨 Failure Modes & Diagnosis

**TCP Throughput Far Below Link Speed on WAN**

```bash
# Reproduce: single-stream iperf3
iperf3 -c remote-host -t 30
# Result: 300 Mbps on a 10 Gbps link

# Step 1: check with parallel streams
iperf3 -c remote-host -P 16 -t 10
# If parallel >> single: buffer/RTT bottleneck (not loss, not bandwidth)

# Step 2: calculate BDP
ping remote-host -c 100 | grep rtt
# rtt avg = 50ms; 10 Gbps × 0.05s = 62.5 MB BDP
cat /proc/sys/net/ipv4/tcp_rmem
# max = 6 MB << 62.5 MB → buffer is the bottleneck

# Fix:
sysctl -w net.core.rmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"

# Re-test: should approach link speed
iperf3 -c remote-host -t 30
# Result: 9.2 Gbps ✓
```

---

### 🔗 Related Keywords

**Prerequisites:** `TCP`, `Congestion Control`, `Packet Loss, Latency & Jitter`

**Related:** `Network Latency Optimization`, `Sliding Window`, `QUIC`, `Congestion Control`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ BANDWIDTH    │ Link capacity (Gbps) — theoretical max    │
│ THROUGHPUT   │ Actual bits/s transferred (always ≤ BW)  │
│ GOODPUT      │ Useful data/s (excl. retransmits, headers)│
├──────────────┼───────────────────────────────────────────┤
│ BDP          │ BW × RTT = bytes in flight to saturate    │
│              │ TCP buffer must be ≥ BDP                  │
├──────────────┼───────────────────────────────────────────┤
│ TUNE         │ tcp_rmem/wmem max ≥ BDP; enable BBR;      │
│              │ fix packet loss before tuning buffers     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bandwidth = pipe size; throughput = what │
│              │ actually flows; BDP = fill the pipe"      │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A machine learning training cluster transfers 100 GB model checkpoints between nodes over a 100 Gbps InfiniBand network with 5μs RTT. (a) Calculate the BDP: what buffer size is needed to saturate this link? (b) Why is InfiniBand preferred over Ethernet for HPC (RDMA — Remote Direct Memory Access, bypasses kernel networking stack, latency < 2μs vs 50μs for Ethernet). (c) Explain RDMA: how the NIC directly reads/writes application memory without CPU involvement, eliminating copy overhead. (d) For 100 Gbps Ethernet (ROCE — RDMA over Converged Ethernet): what networking requirements exist (lossless fabric with PFC — Priority Flow Control, to prevent RDMA from breaking under packet loss). (e) Calculate: at 100 Gbps, how long does it take to transfer 100 GB? What would it take at TCP throughput limited by typical 4MB buffer and 5μs RTT? (Answer: BDP = 100 Gbps × 5μs = 62.5 KB → 4MB buffer >> BDP → saturates link easily.)
