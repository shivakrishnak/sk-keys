---
layout: default
title: "Congestion Control"
parent: "Networking"
nav_order: 173
permalink: /networking/congestion-control/
number: "0173"
category: Networking
difficulty: ★★★
depends_on: TCP, TCP/IP Stack
used_by: Distributed Systems, Network Latency Optimization, Observability & SRE
related: TCP, Flow Control, Sliding Window, QUIC, Bandwidth vs Throughput
tags:
  - networking
  - tcp
  - congestion
  - performance
  - algorithms
---

# 173 — Congestion Control

⚡ TL;DR — TCP congestion control is the algorithm that prevents senders from overwhelming the network: it starts slow (Slow Start), grows CWND exponentially until a threshold (ssthresh), then linearly (Congestion Avoidance), cuts CWND on packet loss, and modern variants (BBR) model bandwidth-delay product directly instead of using loss as a signal — enabling high-throughput on long-distance or lossy links.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In 1986, the internet suffered its first "congestion collapse." Multiple TCP implementations were sending at line rate with no rate adaptation. As routers filled their queues and dropped packets, senders interpreted drops as retransmit triggers and immediately resent at full rate — saturating the network further. Throughput on some links dropped from 32 Kbps to 40 bps — a 99.9% degradation. The internet was unusable.

**THE BREAKING POINT:**
Without congestion control, TCP operates as a tragedy of the commons: each sender maximises its own throughput, collectively destroying the shared network. The more data in flight, the more drops, the more retransmits, the more congestion — a positive feedback loop to zero throughput. This is the definition of congestion collapse.

**THE INVENTION MOMENT:**
Van Jacobson's 1988 paper introduced the congestion control algorithms still used today: Slow Start, Congestion Avoidance, and Fast Retransmit/Fast Recovery. The key insight: packet loss is a signal from the network that the path is congested. TCP must reduce its sending rate when it detects loss, and probe for available bandwidth cautiously. Jacobson's AIMD (Additive Increase/Multiplicative Decrease) algorithm: increase CWND by 1 MSS per RTT (additive), halve CWND on loss (multiplicative decrease). This creates a sawtooth pattern that's provably fair and stable under multi-sender competition. Modern variants (BBR, CUBIC) improve on this but retain the core principle.

---

### 📘 Textbook Definition

**TCP congestion control** is the mechanism by which a TCP sender limits its transmission rate to avoid overwhelming the network. The sender maintains a **Congestion Window** (CWND) — the maximum number of unacknowledged bytes the sender may have in flight. The effective send rate is limited by `min(CWND, receiver_window)`. Key algorithms: **Slow Start** (CWND doubles per RTT from 1 MSS until ssthresh or loss), **Congestion Avoidance** (CWND increases by 1 MSS per RTT), **Fast Retransmit** (retransmit on 3 duplicate ACKs without waiting for RTO), **Fast Recovery** (CWND halved, not reset, on triple-dup-ACK). Modern variants include TCP CUBIC (Linux default) and TCP BBR (available since Linux 4.9).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Congestion control is TCP's throttle: it starts slow, increases the sending rate cautiously, and backs off sharply when it detects the network is full — preventing any single sender from crashing the network.

**One analogy:**

> Merging onto a motorway in rush hour. You can't just floor it — you'll cause a crash (congestion collapse). Instead: accelerate carefully (Slow Start), match motorway speed (Congestion Avoidance), and if someone brakes hard (packet loss), you brake sharply and then re-accelerate cautiously. TCP does exactly this, mathematically, for every connection on the internet — ensuring all senders share the road fairly.

**One insight:**
"Slow Start" is a terrible name: it starts slow but grows exponentially (doubling CWND every RTT). It's only "slow" compared to "send everything at once." The slowness of Slow Start is what saves the internet from the 1986 congestion collapse at every new connection.

---

### 🔩 First Principles Explanation

**CWND (Congestion Window):**
The key variable. CWND is measured in bytes (or MSS units). Sender's effective send limit: `effective_window = min(CWND, rwnd)` where rwnd is the receiver's advertised window (flow control). Bytes in flight ≤ effective_window at all times.

**PHASE 1: Slow Start**

```
Initial: CWND = 1 MSS (typically 10 MSS in modern Linux: net.ipv4.tcp_init_cwnd)
Each ACK received: CWND += 1 MSS
Net effect: CWND doubles each RTT (exponential growth)
Duration: until CWND >= ssthresh, or packet loss
```

**PHASE 2: Congestion Avoidance (AIMD)**

```
Triggered when: CWND >= ssthresh
Each ACK received: CWND += MSS² / CWND  (additive: ~1 MSS per RTT)
Net effect: CWND grows linearly
Duration: until packet loss
```

**LOSS DETECTION AND RESPONSE:**

_Triple duplicate ACKs (fast retransmit):_

```
Event: 3 duplicate ACKs for same sequence number
→ A packet was lost but later packets arrived (mild congestion)
TCP Reno response:
  ssthresh = CWND / 2
  CWND = ssthresh + 3 MSS (Fast Recovery)
  Retransmit the lost packet
  After recovery: CWND = ssthresh (Congestion Avoidance)
TCP CUBIC response: CWND reduced by ~30% (not halved)
```

_Retransmit Timeout (RTO):_

```
Event: RTO timer fires (no ACK for too long)
→ Severe congestion — multiple packets lost
Response:
  ssthresh = max(CWND / 2, 2 × MSS)
  CWND = 1 MSS (reset to Slow Start!)
  Enter Slow Start from CWND=1
```

**THE SAWTOOTH:**
The classic AIMD sawtooth: CWND grows linearly, drops to half on loss, grows again. The average CWND is roughly `ssthresh × 0.75`. On a stable path, ssthresh converges to approximately half the bottleneck bandwidth × RTT (the bandwidth-delay product).

**TCP CUBIC (Linux default since 2.6.19):**
CUBIC uses a cubic function of time since last congestion event to set CWND, rather than ACK-counting. Grows faster on large BDP paths, more conservatively near the saturation point. Fair when competing with CUBIC connections. More aggressive than Reno in high-BDP environments.

**TCP BBR (Bottleneck Bandwidth and RTT, Google 2016):**
BBR fundamentally changes the approach: instead of using packet loss as a congestion signal, BBR estimates the bottleneck bandwidth (BtlBw) and minimum RTT (RTprop) and sets CWND = BtlBw × RTprop (the bandwidth-delay product). Continuously probes for more bandwidth by sending 25% above estimated BtlBw in brief bursts. Result: higher utilisation on high-BDP paths, faster recovery, better performance in shallow-buffered networks. Used by Google, YouTube, many CDNs. Enable: `sysctl -w net.ipv4.tcp_congestion_control=bbr`.

---

### 🧪 Thought Experiment

**SETUP:**
Two connections share a 10 Mbps bottleneck link. Both use TCP CUBIC. RTT = 50ms. How do they share the bandwidth?

**ANALYSIS:**

- Each connection's CWND grows independently
- When the bottleneck link fills (router queue builds up), packets are dropped
- Both connections detect triple-dup-ACKs
- Both reduce CWND by ~30% (CUBIC)
- Both restart Congestion Avoidance from reduced CWND
- Net result: each connection converges to ~5 Mbps (50% each)

**CUBIC FAIRNESS:**
CUBIC is provably fair when all connections have the same RTT. Connections with lower RTT can probe more aggressively (more ACKs per second → CWND grows faster). This means: in a datacenter (1ms RTT), a local connection will "crowd out" a remote connection (100ms RTT) on a shared link. This RTT-unfairness is a known CUBIC limitation. BBR is more RTT-fair.

**BBR vs CUBIC on a lossy link:**
CUBIC on 1% loss: CWND halved every ~7 RTTs on average → severely reduced throughput. BBR on 1% loss: BBR sees RTT increasing (queue building) before loss and reduces rate before drops occur → maintains ~90% of bottleneck bandwidth even at 5% loss. Result: on 4G mobile (lossy), BBR can be 5x faster than CUBIC.

---

### 🧠 Mental Model / Analogy

> TCP congestion control is like the traffic control system on a road without traffic lights. Cars (data segments) join the road. Initially, only one car per minute (Slow Start CWND=1). If the road is clear, double cars per minute every check (exponential growth). Once approaching capacity, add only one car per check (Congestion Avoidance). If a car crashes (packet loss): pull half the cars off the road immediately (CWND halved). The key: no driver can see how many total cars are on the road — they only see crashes (loss) as their signal. BBR is like a driver who checks GPS traffic data (bandwidth estimate) instead of waiting for crashes — faster but requires accurate measurement.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
TCP congestion control is how the internet prevents gridlock. Without it, everyone would send data at maximum speed, routers would overflow, and the internet would grind to a halt (which actually happened in 1986). Congestion control makes each TCP connection start slowly, increase speed cautiously, and slow down when it detects the network is getting full. This ensures the internet's shared bandwidth is fairly distributed.

**Level 2 — How to use it (junior developer):**
As a developer, congestion control is mostly invisible — TCP handles it automatically. But it affects your application: when you make many parallel requests over new TCP connections, each starts in Slow Start and takes several RTTs to reach full speed. Implications: prefer fewer, long-lived connections over many short-lived ones. For file uploads/downloads, a single TCP connection eventually reaches full bandwidth, but multiple connections reach it faster (each in Slow Start simultaneously). For latency-critical applications (interactive), TCP's slow ramp-up can be felt — consider QUIC or WebSockets over a persistent connection. Check the congestion algorithm in use: `sysctl net.ipv4.tcp_congestion_control`.

**Level 3 — How it works (mid-level engineer):**
The bandwidth-delay product (BDP) is the most important concept for understanding congestion control performance: BDP = bandwidth × RTT. On a 1 Gbps link with 100ms RTT, BDP = 1,000,000,000 × 0.1 = 100MB. To fully utilise this link, the sender must have 100MB of data in flight simultaneously. Default Linux socket buffers (87KB) are far too small. Tune: `net.ipv4.tcp_rmem` and `net.ipv4.tcp_wmem` max to 16MB or more. CUBIC CWND grows as `W_cubic(t) = C × (t - K)³ + W_max` where K is calculated such that the function approaches W_max (pre-congestion window) gradually. The cubic shape means fast growth far from saturation, slow growth near saturation — efficient for high-BDP links.

**Level 4 — Why it was designed this way (senior/staff):**
The AIMD (Additive Increase/Multiplicative Decrease) design is not arbitrary — it's mathematically proven to converge to fair sharing. Any other combination (additive decrease or multiplicative increase) either fails to converge (oscillates) or converges unfairly. The multiplicative decrease ensures fast response to congestion; the additive increase ensures cautious probing. The fundamental tension in congestion control: using loss as a signal means you must cause loss (fill buffers to overflow) before backing off — this adds latency (bufferbloat). BBR attacks this by measuring RTT increase (buffer filling) before loss, enabling proactive rate reduction. CoDel (Controlled Delay) and FQ-CoDel tackle bufferbloat from the router/switch side by intentionally dropping packets from connections that have been queued too long. Modern congestion control is a rich research area with implications for cloud networking, satellite internet, and 5G.

---

### ⚙️ How It Works (Mechanism)

```bash
# Check current congestion control algorithm
sysctl net.ipv4.tcp_congestion_control
# default: cubic

# List available algorithms
sysctl net.ipv4.tcp_available_congestion_control

# Switch to BBR (Google's bandwidth-based CC)
# (requires kernel 4.9+ and tcp_bbr module)
modprobe tcp_bbr
sysctl -w net.ipv4.tcp_congestion_control=bbr
sysctl net.ipv4.tcp_congestion_control  # verify

# Check initial CWND (Linux default = 10 MSS)
sysctl net.ipv4.tcp_init_cwnd  # not always visible directly
# Or check with ss on an active connection:
ss -tn -o -i dst <server-ip>
# cwnd:10 means CWND = 10 segments
# Look for: cwnd, ssthresh, send, rto, ato, mss, pmtu

# Monitor CWND in real time on a transfer
# (while running a large download)
ss -tn -o -i | grep cwnd

# Simulate congestion control with tc netem
tc qdisc add dev eth0 root netem \
   loss 1% delay 50ms 5ms
# Now run iperf3 and observe throughput reduction vs clean

# Tune buffers for high-BDP links
# BDP = 1Gbps × 100ms = 12.5MB; need buffers > BDP
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_window_scaling=1  # must be enabled
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  CWND Evolution: Slow Start → Congestion Avoid │
└────────────────────────────────────────────────┘

 CWND
 (MSS)
  64 │                         *
  48 │                    *   / \
  32 │               *   /   /   *
  20 │          *   /   /   /     \  *
  16 │     *   /   /   /           \/  *
   8 │    /   /   /
   4 │   /   /
   2 │  /
   1 │ *
     └────────────────────────────────── Time (RTTs)
     SS│  Cong Avoid  │loss│ SS │ CA  │loss

 SS = Slow Start (exponential)
 CA = Congestion Avoidance (linear)
 loss = packet loss event (CWND halved or reset)

 ════════════════════════════════════

 BBR (vs CUBIC):

 CWND     ┌────────────────────────────────┐
 (ideal)  │   BBR: stable near BDP         │
          │   ████████████████████████████ │
          │   CUBIC: sawtooth              │
          │   /\/\/\/\/\/\/\/\/\/\/\/\/\/\ │
          └────────────────────────────────┘
          Time
```

---

### 💻 Code Example

**Example — Observing Slow Start with iperf3:**

```bash
# Terminal 1: Start iperf3 server
iperf3 -s

# Terminal 2: Run transfer and observe CWND growth
iperf3 -c localhost -t 30 --json | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for interval in data['intervals']:
    stream = interval['streams'][0]
    print(f\"t={stream['start']:.1f}s  \
bits={stream['bits_per_second']/1e6:.1f}Mbps  \
retrans={stream['retransmits']}\")
"

# The first few seconds show Slow Start:
# t=0.0s bits=0.1Mbps retrans=0
# t=0.5s bits=0.8Mbps retrans=0
# t=1.0s bits=3.2Mbps retrans=0
# t=1.5s bits=12.1Mbps retrans=0
# t=2.0s bits=45.3Mbps retrans=0
# Then levels off at line rate (Congestion Avoidance)

# Monitor CWND with ss while iperf3 runs
watch -n 0.1 "ss -tn -o -i | grep cwnd"
```

**Python: measuring congestion via retransmit rate:**

```python
import subprocess
import re
import time

def get_tcp_retransmit_rate() -> dict:
    """Read TCP retransmit statistics from /proc/net/netstat."""
    with open('/proc/net/netstat', 'r') as f:
        lines = f.readlines()

    # Parse TcpExt: header + values
    headers = None
    for line in lines:
        if line.startswith('TcpExt:'):
            if headers is None:
                headers = line.split()[1:]
            else:
                values = [int(x) for x in line.split()[1:]]
                stats = dict(zip(headers, values))
                return {
                    'retransmits': stats.get('TCPRetransFail', 0),
                    'fast_retransmits': stats.get('TCPFastRetrans', 0),
                    'timeout_retransmits': stats.get('TCPTimeouts', 0),
                    'slow_start_retrans': stats.get('TCPSlowStartRetrans', 0),
                    'forward_retransmits': stats.get('TCPForwardRetrans', 0),
                }
    return {}

# Compare before and after
t1 = get_tcp_retransmit_rate()
time.sleep(10)
t2 = get_tcp_retransmit_rate()

delta = {k: t2[k] - t1[k] for k in t1}
print("TCP retransmit events (last 10s):")
for k, v in delta.items():
    if v > 0:
        print(f"  {k}: {v}")
```

---

### ⚖️ Comparison Table

| Algorithm        | Congestion Signal | CWND Growth    | Best For            | Weakness                 |
| ---------------- | ----------------- | -------------- | ------------------- | ------------------------ |
| TCP Reno         | Loss (3 dup ACK)  | Linear (CA)    | Low BDP             | Slow on high BDP         |
| TCP CUBIC        | Loss (3 dup ACK)  | Cubic function | High BDP            | Bufferbloat, RTT unfair  |
| TCP BBR          | RTT + bandwidth   | BDP-based      | High latency, lossy | Unfair vs CUBIC at start |
| QUIC (CUBIC/BBR) | Configurable      | Configurable   | Modern web          | Still evolving           |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Slow Start" means TCP starts slowly        | Slow Start grows CWND exponentially (doubles every RTT). It's "slow" only vs sending everything at once                                                                                |
| Higher CWND = always better                 | CWND is bounded by `min(CWND, rwnd)`. If rwnd (receiver window) is the bottleneck, increasing CWND has no effect; fix socket buffer sizes                                              |
| Packet loss always means network congestion | Packet loss can be caused by wireless interference, bad cables, or overloaded hosts — not just network congestion. BBR's model-based approach is less sensitive to non-congestion loss |
| BBR is strictly better than CUBIC           | BBR can be unfair to CUBIC connections on shared bottlenecks (BBR may grab too much bandwidth initially). Mixed environments with both BBR and CUBIC senders can have fairness issues  |
| More connections = more throughput          | Multiple TCP connections skip Slow Start faster in aggregate, but cause more load on routers and may be rate-limited by servers or CDNs                                                |

---

### 🚨 Failure Modes & Diagnosis

**Throughput Far Below Line Rate on Long-Distance Link**

**Symptom:**
`iperf3` shows 10 Mbps on a 1 Gbps link between two datacentres 150ms RTT apart. Expected: hundreds of Mbps.

**Root Cause:**
Small CWND due to default socket buffers + Slow Start not having enough time to grow on individual connections. BDP = 1 Gbps × 150ms = 18.75 MB. With default 87KB socket buffer, max in-flight bytes = 87KB → max throughput = 87,000 bytes / 0.150s = 4.6 Mbps.

**Diagnostic Commands:**

```bash
# Test throughput
iperf3 -c <remote> -t 30

# Check current buffer config
sysctl net.ipv4.tcp_rmem
sysctl net.ipv4.tcp_wmem

# Calculate required buffer
# BDP = bandwidth_bps * rtt_seconds / 8
python3 -c "bw=1e9; rtt=0.150; print(f'BDP: {bw*rtt/8/1e6:.1f} MB')"

# Check if window scaling is enabled
sysctl net.ipv4.tcp_window_scaling  # must be 1

# Check CWND on active connection
ss -tn -o -i dst <remote-ip> | grep cwnd
```

**Fix:**
Increase TCP socket buffers to at least 2× BDP; enable window scaling; optionally switch to BBR on long-distance links for better high-BDP performance.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `TCP` — congestion control is a core TCP mechanism; TCP basics are prerequisite
- `TCP/IP Stack` — congestion operates at the transport layer

**Builds On This (learn these next):**

- `Flow Control` — complementary to congestion control; flow control is receiver-side rate limiting (rwnd), congestion control is network-side rate limiting (CWND)
- `Sliding Window` — the window mechanism that implements both flow control and congestion control
- `Bandwidth vs Throughput` — congestion control directly determines the relationship between available bandwidth and achieved throughput
- `Network Latency Optimization` — understanding congestion control is key to latency/throughput optimisation

**Alternatives / Comparisons:**

- `QUIC` — QUIC has its own congestion control (BBR or CUBIC) in user space, enabling faster iteration
- `Flow Control` — receiver-side complement to sender-side congestion control

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ TCP's throttle: prevents senders from     │
│              │ overloading the network                   │
├──────────────┼───────────────────────────────────────────┤
│ SLOW START   │ CWND doubles per RTT from 1 (or 10) MSS   │
│              │ until ssthresh or loss                    │
├──────────────┼───────────────────────────────────────────┤
│ CONG AVOID   │ CWND += 1 MSS per RTT (linear, AIMD)      │
├──────────────┼───────────────────────────────────────────┤
│ ON LOSS      │ 3 dup ACK: CWND halved (fast recovery)    │
│              │ RTO: CWND = 1 MSS (back to Slow Start)    │
├──────────────┼───────────────────────────────────────────┤
│ BBR          │ Uses BDP model (not loss); better on high  │
│              │ latency/lossy links; default at Google    │
├──────────────┼───────────────────────────────────────────┤
│ BDP TUNING   │ Buffers must be >= BW × RTT; default 87KB │
│              │ far too small for WAN connections         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Probe for bandwidth, back off on loss,   │
│              │ converge to fair share" (AIMD)            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Flow Control → Sliding Window → BBR paper  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A content delivery network deploys servers in London (10ms RTT from users) and Sydney (200ms RTT from Australian users). Both servers use TCP CUBIC. An Australian user downloads a 100MB video from the Sydney server. (a) Calculate the theoretical time to fill the CWND to the BDP of a 100 Mbps link with 200ms RTT. (b) How many Slow Start doublings are required to reach the ssthresh of 1MB? (c) If the path has 0.5% packet loss (realistic for transpacific), what is the average CWND under CUBIC's sawtooth? (d) How would switching the Sydney server to TCP BBR change the download time? (e) What is "bufferbloat" and why does a high-latency path with a deep-buffered router make it worse?

**Q2.** Describe the "congestion collapse" event of 1986 in precise technical terms: (a) what the trigger was (early TCP implementations without congestion control), (b) the positive feedback loop (loss → retransmit at full rate → more loss), (c) how Van Jacobson's Slow Start breaks the feedback loop (specifically: why resetting CWND to 1 MSS on RTO timeout is the critical step), (d) why AIMD (and not other combinations like additive decrease or multiplicative increase) is mathematically guaranteed to converge to fair sharing among competing connections, and (e) how CoDel (Controlled Delay) AQM (Active Queue Management) at routers complements end-host congestion control to combat bufferbloat.
