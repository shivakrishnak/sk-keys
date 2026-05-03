---
layout: default
title: "Packet Loss, Latency & Jitter"
parent: "Networking"
nav_order: 188
permalink: /networking/packet-loss-latency-jitter/
number: "0188"
category: Networking
difficulty: ★★☆
depends_on: TCP, UDP, Networking, Congestion Control
used_by: Observability & SRE, Distributed Systems, System Design
related: TCP, Congestion Control, Bandwidth vs Throughput, Network Latency Optimization, QUIC
tags:
  - networking
  - latency
  - packet-loss
  - jitter
  - performance
  - sre
---

# 188 — Packet Loss, Latency & Jitter

⚡ TL;DR — **Latency** is the time for a packet to travel from source to destination (RTT = round-trip). **Packet loss** is the percentage of packets that never arrive. **Jitter** is the variation in latency between packets. For TCP: packet loss triggers retransmission and congestion window reduction — catastrophic for throughput. For real-time apps (VoIP, video): jitter causes audio artifacts even without loss. Understanding all three is essential for diagnosing network-related performance issues.

---

### 🔥 The Problem This Solves

Network performance isn't just about bandwidth (capacity). A 10 Gbps link with 1% packet loss and 200ms latency is far worse for most applications than a 1 Mbps link with 0% loss and 10ms latency. TCP throughput degrades quadratically with packet loss (Mathis formula). VoIP becomes unintelligible with 5% loss and 50ms jitter. Understanding the three dimensions of network quality enables accurate diagnosis and targeted fixes.

---

### 📘 Textbook Definition

**Latency:** The time for a packet to travel from source to destination. Measured as RTT (Round-Trip Time) — the time for a packet + acknowledgement to return. Components: propagation delay (speed of light in fibre ≈ 200,000 km/s), transmission delay (packet size / link bandwidth), processing delay (queuing in routers).

**Packet Loss:** The percentage of transmitted packets that fail to reach the destination. Causes: congestion (queue overflow), bit errors (wireless), faulty hardware, MTU mismatches (MTU black hole). TCP detects via timeout or 3 duplicate ACKs; triggers retransmission.

**Jitter:** The variation in packet arrival times (standard deviation of inter-packet delay). Formula: jitter = |latency(n) - latency(n-1)|. Cause: packets taking different routes or experiencing varying queuing delays. Impact: real-time applications (VoIP, gaming, video conferencing) require consistent arrival timing; jitter buffers smooth out variation at the cost of added latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Latency = how long a packet takes; packet loss = how many packets disappear; jitter = how inconsistent the latency is. TCP hates loss. Real-time apps hate jitter. Everything hates high latency.

**One analogy:**

> Imagine a courier service (network). Latency: how long it takes a parcel to arrive. Packet loss: some parcels go missing entirely. Jitter: sometimes parcels arrive 2 hours after dispatch, sometimes 8 hours — you can't plan around it. A business (TCP app) can cope with slow deliveries if they're reliable. A restaurant (VoIP) needs predictable delivery: ingredients (packets) that arrive randomly throughout the day make service impossible.

---

### 🔩 First Principles Explanation

**LATENCY COMPONENTS:**

```
RTT = propagation + transmission + queuing + processing

Propagation delay (irreducible):
  Speed of light in fibre: ~200,000 km/s
  New York → London: ~5,500 km = ~27.5ms one-way
  (actual: ~70ms due to routing, equipment)

  Rule: ~1ms per 100km of fibre

Transmission delay:
  = packet_size / link_bandwidth
  1500 byte (MTU) on 1 Gbps link = 0.012ms (negligible)
  1500 byte on 1 Mbps link = 12ms (significant for large packets)

Queuing delay (variable, root of jitter):
  Router buffer fills during congestion
  Added delay: depends on queue depth and draining rate
  Modern routers: FQ-CoDel, CAKE → active queue management
  Old routers: tail-drop → buffers grow → bufferbloat (high jitter)

Processing delay: < 0.1ms in modern hardware (usually negligible)
```

**PACKET LOSS IMPACT ON TCP:**

```
TCP throughput (Mathis formula):
  BDP = Bandwidth × RTT
  Throughput ≤ (MSS / RTT) × (1 / √loss)

  Example: 100 Mbps link, 100ms RTT, 1% loss:
  Throughput ≤ (1460 bytes / 0.1s) × (1 / √0.01)
             = 14,600 bytes/s × 10
             = 146,000 bytes/s = ~1.2 Mbps  ← only 1.2% of capacity!

  1% packet loss on a 100 Mbps link → effective throughput ~1.2 Mbps
  Why: each loss triggers:
    - Congestion window halving (AIMD)
    - Retransmission timeout (adds RTT)
    - Slow start from reduced window

0.01% loss: throughput ~12 Mbps (12% of 100 Mbps)
0.1% loss: throughput ~3.8 Mbps
1% loss: throughput ~1.2 Mbps
```

**JITTER AND REAL-TIME APPS:**

```
VoIP packet arrival:
  Without jitter:  t=20ms, t=40ms, t=60ms, t=80ms (perfect 20ms interval)
  With jitter:     t=20ms, t=45ms, t=55ms, t=95ms (variable delays)

  Jitter buffer: holds packets, plays them at scheduled time
    - Small buffer (20ms): low added latency, occasional dropout
    - Large buffer (200ms): smooth playback, high added latency

  G.711 codec: 20ms packet interval, tolerates ~150ms one-way latency
  ITU-T G.114: max 150ms one-way for acceptable voice quality

  With 200ms jitter buffer + 80ms RTT:
    Total one-way: 100ms (jitter buffer) + 40ms (propagation) = 140ms (OK)

  With 200ms jitter buffer + 300ms RTT:
    Total one-way: 100ms + 150ms = 250ms → perceptible delay, call quality poor

MEASUREMENT:
  Latency: ping -c 100 HOST (average RTT)
  Jitter:  ping -c 100 HOST (mdev = mean deviation ≈ jitter)
  Loss:    ping -c 1000 HOST; count "packet loss" %
  Detailed: mtr --report HOST (per-hop latency + loss)
```

---

### 🧪 Thought Experiment

**BUFFERBLOAT:**
Many home routers have large buffers (10-50MB). This seems helpful — never drop packets. In reality: packets queue for hundreds of milliseconds in the buffer before being dropped. The result: no packet loss, but massive jitter (latency varies from 10ms to 500ms). A file download fills the buffer; your VoIP call then experiences 400ms jitter — far worse than small packet loss would be. Solution: AQM (Active Queue Management) — CoDel, FQ-CoDel, CAKE — drop or delay packets intelligently to keep queue short, reducing jitter while accepting slightly higher loss rate.

---

### 🧠 Mental Model / Analogy

> A highway (network link): latency = how long the drive takes, packet loss = cars that fall off a cliff, jitter = the unpredictability of arrival time due to traffic lights and accidents. A high-capacity highway (bandwidth) doesn't help if every car might fall off a cliff (packet loss) or arrive at wildly different times (jitter). For a package delivery company (TCP), lost packages are a disaster — they have to be re-sent. For a radio station (VoIP), a car arriving 5 minutes early or late means the song either plays too early (overlap) or there's dead air.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Latency is how slow packets travel. Packet loss means some packets disappear and must be resent (slowing TCP). Jitter is inconsistent delay — bad for voice/video calls.

**Level 2:** Diagnose with: `ping HOST` (latency and loss), `mtr HOST` (per-hop breakdown), `iperf3` (bandwidth and loss under load). Fix packet loss: check for errors with `ethtool -S eth0` (hardware errors), check for drops with `netstat -s | grep dropped`. Fix jitter: upgrade router firmware (AQM support), reduce buffer size, prioritise real-time traffic with QoS.

**Level 3:** TCP CUBIC/BBR congestion algorithms respond very differently to loss. CUBIC (default Linux) halves the congestion window on loss — correct for random loss, catastrophic for measured/managed loss (like WiFi retransmission, which masks loss from TCP). BBR (Bottleneck Bandwidth and RTT) models the network bottleneck directly, doesn't rely on loss as a congestion signal — much better for lossy links (WiFi, satellite). QUIC (UDP + QUIC protocol) also improves loss handling because head-of-line blocking doesn't exist — one stream's loss doesn't block other streams.

**Level 4:** The relationship between latency, bandwidth, and throughput is captured by the Bandwidth-Delay Product (BDP). BDP = bandwidth × RTT = "bytes in flight" at full utilisation. TCP buffer sizes must be at least equal to BDP to saturate a link. A 1 Gbps link with 200ms RTT: BDP = 1 Gbps × 0.2s = 200 MB — default TCP socket buffers (4MB) are 50x too small, limiting throughput to 4MB/0.2s = 160 Mbps regardless of link speed. Tune: `net.core.rmem_max`, `net.ipv4.tcp_rmem`, `net.core.wmem_max`.

---

### ⚙️ How It Works (Mechanism)

```bash
# Measure latency and packet loss
ping -c 100 google.com
# rtt min/avg/max/mdev = 12.1/14.3/22.5/2.1 ms
# mdev (~jitter): 2.1ms = excellent
# packet loss: 0%

# Per-hop latency and loss (traceroute + ping combined)
mtr --report --report-cycles 100 google.com
# Shows each hop: latency, loss, jitter per hop

# Continuous latency monitoring
ping -i 0.2 -c 1000 target.host | awk -F'[= ]' '/rtt/{
  split($8,a,"/"); print a[1], a[2], a[3], a[4]}'

# Measure under load with iperf3
iperf3 -s  # server
iperf3 -c server-ip -t 30 -P 4  # client: 4 parallel streams, 30s
# Shows bandwidth, retransmissions (=loss indicator)

# Check interface errors
ip -s link show eth0
# RX errors, dropped, overrun → physical layer issues

# Check TCP retransmissions
netstat -s | grep -i retransmit
# TCP: 1234 segments retransmitted → packet loss indicator

# Check kernel socket buffer usage
ss -tmn state established
# skmem:(r bytes, rb recv buf, t bytes, tb send buf)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Packet journey (source → destination):

Source:      App sends 1460-byte segment
             Kernel adds TCP/IP headers (40 bytes)
             NIC DMA, 1500-byte frame transmitted

Path:
  Hop 1 (LAN):     0.1ms propagation + 0.001ms tx = 0.1ms
  Hop 2 (ISP):     2ms + queue time (0-50ms variable = jitter!)
  Hop 3 (internet): 50ms propagation (intercontinental)
  Hop 4 (CDN):     1ms

Destination: Packet arrives at 53ms
             ACK sent back: another 53ms
             Total RTT: ~106ms

Packet loss at Hop 2:
  Hop 2 buffer full → tail-drop
  TCP sender: no ACK after timeout (200ms)
  → TCP retransmits
  → Congestion window halved
  → Throughput drops dramatically
```

---

### 💻 Code Example

```python
import subprocess
import re
import statistics
from typing import NamedTuple

class NetworkQuality(NamedTuple):
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    jitter_ms: float  # mdev from ping
    packet_loss_pct: float

def measure_network_quality(
    host: str, count: int = 100
) -> NetworkQuality:
    """Measure latency, jitter, and packet loss to a host."""
    result = subprocess.run(
        ["ping", "-c", str(count), host],
        capture_output=True, text=True, timeout=120
    )

    output = result.stdout + result.stderr

    # Parse packet loss
    loss_match = re.search(r'(\d+(?:\.\d+)?)% packet loss', output)
    packet_loss = float(loss_match.group(1)) if loss_match else 100.0

    # Parse RTT stats: min/avg/max/mdev
    rtt_match = re.search(
        r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)',
        output
    )

    if rtt_match:
        min_rtt, avg_rtt, max_rtt, mdev = (
            float(x) for x in rtt_match.groups()
        )
    else:
        min_rtt = avg_rtt = max_rtt = mdev = float('inf')

    return NetworkQuality(
        avg_latency_ms=avg_rtt,
        min_latency_ms=min_rtt,
        max_latency_ms=max_rtt,
        jitter_ms=mdev,
        packet_loss_pct=packet_loss
    )

def assess_quality(nq: NetworkQuality) -> str:
    """Rate network quality for different use cases."""
    issues = []

    if nq.packet_loss_pct > 1.0:
        issues.append(f"HIGH LOSS {nq.packet_loss_pct}% (TCP throughput severely degraded)")
    elif nq.packet_loss_pct > 0.1:
        issues.append(f"ELEVATED LOSS {nq.packet_loss_pct}%")

    if nq.jitter_ms > 30:
        issues.append(f"HIGH JITTER {nq.jitter_ms}ms (VoIP/video problematic)")

    if nq.avg_latency_ms > 150:
        issues.append(f"HIGH LATENCY {nq.avg_latency_ms}ms (user-perceptible)")

    return "GOOD" if not issues else "; ".join(issues)

# Usage
nq = measure_network_quality("8.8.8.8", count=100)
print(f"Latency: {nq.avg_latency_ms}ms (jitter: {nq.jitter_ms}ms)")
print(f"Loss: {nq.packet_loss_pct}%")
print(f"Quality: {assess_quality(nq)}")
```

---

### ⚖️ Comparison Table

| Metric        | Good   | Acceptable | Poor   | Impact                  |
| ------------- | ------ | ---------- | ------ | ----------------------- |
| Latency (RTT) | <20ms  | 20-150ms   | >150ms | UX, TCP throughput      |
| Packet loss   | <0.01% | 0.01-0.1%  | >0.1%  | TCP throughput collapse |
| Jitter        | <5ms   | 5-30ms     | >30ms  | VoIP, video quality     |

---

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                                                                                                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High bandwidth = good performance | 1 Gbps with 1% loss is far worse than 10 Mbps with 0% loss for TCP transfers. Bandwidth, latency, and loss are all independent dimensions                                                         |
| Packet loss is always a problem   | QUIC and some UDP applications handle loss gracefully — a single lost video frame is concealed; there's no retransmission storm. TCP is uniquely vulnerable to loss                               |
| Jitter only affects VoIP          | Jitter also affects web page load times (TCP slow start resumes from small window after a jitter-induced timeout), video streaming (rebuffering), and database query latency (tail latency spike) |

---

### 🚨 Failure Modes & Diagnosis

**Bufferbloat: High Jitter Under Load**

```bash
# Test for bufferbloat: run ping during heavy download
# Terminal 1: start download
curl -o /dev/null http://speedtest.tele2.net/10MB.zip &

# Terminal 2: measure latency during download
ping -i 0.2 -c 50 8.8.8.8

# Bufferbloat: ping shows 5ms normally, 500ms during download
# = buffer in router filling, adding massive queue delay

# Fix: enable FQ-CoDel / CAKE in router firmware (OpenWRT)
# Or: use ISP with modern AQM

# Verify fix: latency should stay <20ms even under full load

# Linux server: set AQM on interface
tc qdisc replace dev eth0 root cake bandwidth 100mbit
```

---

### 🔗 Related Keywords

**Prerequisites:** `TCP`, `UDP`, `Congestion Control`

**Related:** `Bandwidth vs Throughput`, `Network Latency Optimization`, `QUIC`, `Congestion Control`, `Observability & SRE`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LATENCY      │ Propagation + queue + tx delay; RTT = 2×  │
│ PACKET LOSS  │ TCP throughput ∝ 1/√loss; 1%→ ~1% of cap  │
│ JITTER       │ Latency variation; VoIP needs <30ms       │
├──────────────┼───────────────────────────────────────────┤
│ MEASURE      │ ping (loss, latency, jitter=mdev)         │
│              │ mtr (per-hop), iperf3 (throughput + loss) │
├──────────────┼───────────────────────────────────────────┤
│ BUFFERBLOAT  │ Large router buffers → no loss but 500ms  │
│              │ jitter; fix with CoDel/CAKE AQM           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "TCP hates loss. VoIP hates jitter.       │
│              │ Everything hates high latency."           │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A FAANG-scale distributed database cluster experiences "tail latency" — the p99 query latency is 500ms while the p50 is 5ms. Analyse: (a) how TCP's retransmission timeout (RTO) contributes to tail latency (a single lost packet causes 200ms timeout before retransmit, inflating p99), (b) how QUIC or UDP-based protocols reduce tail latency for database RPCs (no head-of-line blocking), (c) the role of jitter in tail latency (a burst of jitter → multiple simultaneous timeouts → timeout storm), (d) how TCP BBR congestion control reduces p99 latency compared to CUBIC in a high-bandwidth, moderate-latency environment, and (e) how Google's SPDY/HTTP/2 server push and prioritisation reduce page load p99 by ensuring critical resources aren't blocked by large non-critical transfers.
