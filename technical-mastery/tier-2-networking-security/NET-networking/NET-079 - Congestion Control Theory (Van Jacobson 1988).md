---
id: NET-079
title: "Congestion Control Theory (Van Jacobson 1988)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-029, NET-077, NET-078
used_by: NET-083
related: NET-029, NET-077, NET-078, NET-083
tags:
  - networking
  - congestion-control
  - tcp
  - algorithms
  - van-jacobson
  - bbr
  - cubic
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/net/congestion-control-theory/
---

**⚡ TL;DR** - Congestion collapse (1986): the early internet
carried 32 Kbps of useful traffic on a 32 Kbps link
(100% collapse). Van Jacobson's 1988 paper introduced
slow start, congestion avoidance, and fast retransmit/
recovery - algorithms still in Linux today. Modern
algorithms: CUBIC (Linux default), BBR (Google, 2016)
use different signals: CUBIC uses packet loss, BBR uses
RTT and bandwidth model. The difference matters at scale:
BBR gets 10x throughput on high-RTT links (satellite,
transatlantic) where CUBIC is too conservative.

| #079 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Flow Control (NET-029), TCP RFC 793 (NET-077), QUIC Protocol Design (NET-078) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | TCP Flow Control, TCP RFC 793, QUIC Protocol Design, Networking Career Paths | |

---

### 🔥 The Congestion Collapse of 1986

```
Context: ARPANET in 1986
  Link between UC Berkeley and LBL: 32 Kbps
  Traffic observed: 32 Kbps sent, 40 bytes/second useful traffic
  
  "Congestion collapse": 100% of bandwidth consumed by retransmits
  
What happened:
  Network gets congested: packet loss occurs
  Sender: timeout → retransmits
  Retransmits: add MORE traffic to already-congested network
  More congestion → more loss → more retransmits → collapse
  
  Each sender assumes: "the network is fine, my packet got lost"
  Collective behavior: every sender adds traffic → positive feedback loop
  
Van Jacobson's insight:
  Senders need to cooperate, not just individually optimize
  Add to TCP: explicit congestion detection and response
  Design: reduce window when congestion detected
          grow window slowly when things are going well
```

---

### ⚙️ Algorithm 1 - Slow Start

```
Problem: new connection opens at full window → bursts → congestion
Solution: start small, grow exponentially until congestion

Slow start algorithm:
  Initial window: cwnd = 1 MSS (Maximum Segment Size)
  After each ACK: cwnd += 1 MSS (doubles per RTT)
  
  RTT 1: send 1, receive 1 ACK → cwnd = 2
  RTT 2: send 2, receive 2 ACK → cwnd = 4
  RTT 3: send 4, receive 4 ACK → cwnd = 8
  RTT 4: send 8, receive 8 ACK → cwnd = 16
  
  Exponential growth until ssthresh (slow start threshold)
  ssthresh: initially = max window (64K or full receiver window)
  When cwnd >= ssthresh: switch to congestion avoidance
  
Why "slow" start?
  Original TCP: opened at full window → 1 packet per byte
  Slow start: still exponential, but controlled
  "Slow" relative to previous: previous was uncontrolled
  
Initial congestion window (IW) evolution:
  RFC 793 (1981): IW = 1 MSS
  RFC 3390 (2002): IW = min(4×MSS, max(2×MSS, 4380 bytes)) ≈ 3 MSS
  RFC 6928 (2013): IW = 10 MSS (current recommendation)
  
  Impact of IW = 10:
    1 RTT: 10 × 1460 bytes = 14.6 KB sent
    For page loads: many assets < 14.6 KB → loaded in 1 RTT
    Without IW=10: 3-4 RTTs needed (slow start from 1 MSS)
```

---

### ⚙️ Algorithm 2 - Congestion Avoidance (AIMD)

```
After slow start reaches ssthresh:
  Switch to: Additive Increase, Multiplicative Decrease (AIMD)
  
Additive Increase:
  Each RTT (all ACKs received): cwnd += 1 MSS
  Growth: linear (not exponential)
  
  RTT 1: cwnd = 16, send 16 → receive 16 ACKs → cwnd = 17
  RTT 2: cwnd = 17 → cwnd = 18
  ...
  Probing: slowly increasing load until congestion detected
  
Multiplicative Decrease:
  When: packet loss detected (timeout or 3 duplicate ACKs)
  ssthresh = cwnd / 2 (cut in half)
  cwnd = ssthresh (or 1 MSS for timeout)
  Restart: slow start or congestion avoidance from ssthresh
  
AIMD produces the "sawtooth" pattern:
  Window: grows linearly → drops at loss → grows → drops → ...
  
  ^
  |     /\    /\    /\
  |    /  \  /  \  /  \
  |   /    \/    \/    \
  |  /
  +---------------------------> time
  
Why multiplicative decrease:
  Additive decrease: would take N RTTs to reduce to safe level
  Multiplicative: reduces to 50% in one event
  Network: quickly returns to usable state
  
Why additive increase:
  Exponential increase: would overshoot again
  Linear: slowly probes available capacity
  Network: fair sharing among competing flows
```

---

### ⚙️ Algorithm 3 - Fast Retransmit and Fast Recovery

```
Problem: RTO timeout is slow (500ms-1s default)
  After packet loss: wait for timeout before retransmit
  High-RTT paths: 1-2 seconds of wasted time
  
Van Jacobson's fix: 3 duplicate ACKs = loss signal
  Receiver: gets out-of-order packet, sends ACK for last in-order byte
  3 duplicate ACKs: strong signal that ONE specific packet is lost
  (not general congestion - just one packet)
  
Fast retransmit:
  3 dup ACKs received → retransmit the missing packet immediately
  No waiting for timeout
  
Fast recovery:
  After fast retransmit: ssthresh = cwnd / 2
  BUT: don't reset cwnd to 1 (as timeout does)
  Instead: cwnd = ssthresh (stay in congestion avoidance)
  
  Rationale: 3 dup ACKs means data IS flowing through network
  (receiver is getting packets, just one is missing)
  Not a catastrophic event → less aggressive reduction
  
  vs Timeout: means NO data flowing (no ACKs at all)
  More severe: reset to cwnd = 1, restart slow start

Combined effect of Van Jacobson's algorithms:
  Before (1986): 40 bytes/second on 32 Kbps link
  After: stable utilization at 90%+ of link capacity
  Without congestion collapse
```

---

### ⚙️ Modern Algorithm - CUBIC (Linux Default)

```
Problem with Reno (Van Jacobson): conservative on high-bandwidth links
  10 Gbps link, 100ms RTT: BDP = 125 MB
  After congestion event: cwnd = 62.5 MB
  Additive increase: +1.46 KB per RTT
  Time to reach 125 MB again: 62.5 MB / 1.46 KB = 42,808 RTTs
  Time: 42,808 × 0.1s = 4,280 seconds = 71 MINUTES
  
CUBIC (Linux 2.6.19+, 2006):
  Window grows as a cubic function of time since last event
  Much faster recovery on high-bandwidth links
  
  W(t) = C × (t - K)^3 + W_max
  Where K = time to reach pre-congestion window W_max
  
  After congestion: grows slowly (near W_max, careful)
  Far from W_max: grows faster (cubic acceleration)
  
  Recovery time: seconds, not minutes
  On high-RTT links: 10x better throughput than Reno
  
  Linux: cubic is default (sysctl net.ipv4.tcp_congestion_control)
  Check: sysctl net.ipv4.tcp_congestion_control → returns "cubic"
```

---

### ⚙️ Modern Algorithm - BBR (Google, 2016)

```
CUBIC limitation: uses packet loss as congestion signal
  Problem: by the time loss occurs, buffers are FULL
  Full buffers: adds 100s of ms of delay (bufferbloat)
  
  Modern switches: large buffers (512 MB on some Cisco)
  CUBIC: fills buffers completely before detecting congestion
  Result: high throughput BUT very high latency (buffer filling)
  
BBR (Bottleneck Bandwidth and Round-trip time):
  Different signal: measures RTT + bandwidth to model network state
  
  Two-variable model:
    BtlBw: estimated bottleneck bandwidth (delivery rate)
    RTprop: minimum observed RTT (propagation delay)
  
  Target: fully utilize BtlBw while NOT adding to queue
  (send just fast enough to fill pipe, not overflow buffers)
  
  Algorithm:
    Probe bandwidth: periodically send faster to measure max throughput
    Drain: send slower to drain any built-up queue
    Cruise: operate at measured BtlBw × RTprop
    
BBR vs CUBIC:
  Long-fat network (satellite 600ms RTT, 100 Mbps):
    CUBIC: fills buffers, 600ms latency + queuing
    BBR: utilizes full bandwidth at 600ms (not 800ms+)
    
  Shared congested link:
    CUBIC vs CUBIC: fair sharing (both use loss signal)
    BBR vs CUBIC: BBR can win unfairly (detects congestion earlier)
    Mixed: controversial, ongoing research
    
  Where BBR wins:
    Google's experience: 2-25% improvement worldwide
    High-RTT paths: satellite, transatlantic
    Lossy networks: mobile (BBR distinguishes congestion vs loss)
```

---

### ⚙️ Selecting Congestion Control in Production

```bash
# Check current congestion control algorithm:
sysctl net.ipv4.tcp_congestion_control
# cubic (default Linux)

# List available algorithms:
sysctl net.ipv4.tcp_available_congestion_control
# cubic reno bbr

# Enable BBR globally (persistent):
cat >> /etc/sysctl.conf << 'EOF'
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq    # fair queue scheduler (required for BBR)
EOF
sysctl -p

# Enable BBR for specific socket (application code):
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, b'bbr')
# Note: TCP_CONGESTION option - sets per-socket algorithm

# Check what algorithm a connection is using:
ss -ti "dst 10.0.0.1"
# Look for: cubic or bbr in output
# Also: retransmissions, rtt, cwnd

# Measure impact:
# Before changing: record baseline throughput and latency
iperf3 -c remote_host -P 4 -t 30  # parallel streams, 30 seconds

# After changing to BBR:
sysctl -w net.ipv4.tcp_congestion_control=bbr
sysctl -w net.core.default_qdisc=fq
iperf3 -c remote_host -P 4 -t 30  # compare

# Typical result on high-RTT link: 20-50% throughput improvement
# Typical result on LAN: similar (BDP is small, both saturate quickly)
```

---

### 📐 QUIC Congestion Control

```
QUIC implements congestion control in userspace:
  Not tied to OS kernel algorithm
  Can update algorithm per-application without kernel update
  
Default: QUIC uses CUBIC or BBR (implementation choice)
  Google QUIC: uses BBR (of course)
  Most QUIC libraries: configurable at compile or runtime
  
Advantages of userspace congestion control:
  1. Per-application tuning: video streaming vs bulk transfer
  2. Faster iteration: no kernel release cycle
  3. A/B test algorithms: route 50% traffic to BBR variant
  4. Platform-specific: mobile vs server vs embedded
  
QUIC ACK handling:
  QUIC ACKs are more precise than TCP
  Packet numbers are monotonically increasing (never wrap)
  ACK ranges: more accurate loss detection
  ECN (Explicit Congestion Notification): first-class in QUIC
  
ECN (Explicit Congestion Notification):
  Router: detects congestion BEFORE dropping
  Marks packet: ECN-CE (Congestion Experienced) bit
  Receiver: reports CE to sender via ACK
  Sender: reduce window BEFORE packet drop
  
  Result: no packet loss needed for congestion signal
  Much more precise than waiting for timeout/dup-ACK
  BBR + ECN: the future of high-performance congestion control
```

---

### 🧭 Decision Guide

```
When to change congestion control algorithm:

Use CUBIC (default):
  Most cases (data center, stable links, LANs)
  Proven, stable, fair to other CUBIC flows
  Don't change unless you have a measured problem
  
Switch to BBR when:
  High-RTT links (> 50ms): transatlantic, satellite
  Mobile users: lossy networks
  You have evidence CUBIC is leaving bandwidth unused
  (measure: iperf3 throughput far below link speed)
  
Test protocol:
  1. Baseline: iperf3 throughput with CUBIC (5 trials)
  2. Enable BBR
  3. Measure: iperf3 throughput with BBR (5 trials)
  4. Statistical significance: is improvement consistent?
  5. Monitor: do other flows suffer? (fairness check)
  
Watch for BBR deployment issues:
  BBR v1 unfairness: BBR flows dominate CUBIC flows on shared link
  Mitigation: ensure all senders use BBR (uniform deployment)
  BBR v2: improved fairness (experimental as of 2023)
  
Diagnosing throughput problems:
  Low throughput on good link → cwnd limited?
  ss -ti | grep cwnd → is window suspiciously small?
  Retransmits? → ss -s | grep retransmits
  If retransmits high + cwnd low → congestion signal firing too often
    → Check: is there actual congestion or spurious loss?
    → If spurious: consider tcp_min_rtt_wlen tuning
```
permalink: /technical-mastery/net/congestion-control-theory-van-jacobson-1988/
---