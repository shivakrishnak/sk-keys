---
layout: default
title: "Sliding Window"
parent: "Networking"
nav_order: 175
permalink: /networking/sliding-window/
number: "0175"
category: Networking
difficulty: ★★★
depends_on: TCP, Flow Control
used_by: Distributed Systems, Network Latency Optimization
related: TCP, Flow Control, Congestion Control, Bandwidth vs Throughput
tags:
  - networking
  - tcp
  - sliding-window
  - flow-control
  - performance
---

# 175 — Sliding Window

⚡ TL;DR — The sliding window protocol allows a TCP sender to transmit multiple segments before waiting for an acknowledgement, bounded by the window size (min of rwnd and CWND) — maximising link utilisation by keeping the "pipe full" of in-flight data equal to the bandwidth-delay product, rather than waiting for each segment to be ACKed before sending the next.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
"Stop-and-Wait" protocol: sender sends one segment, waits for ACK, sends next. On a 100ms RTT link with 1Gbps bandwidth and 1460-byte segments: utilisation = segment_time / (segment_time + RTT) = 0.0117ms / 100.0117ms ≈ 0.012%. A 1 Gbps link running at 0.012% efficiency — achieving 1.17 Mbps instead of 1000 Mbps. The round trip time dominates because we're idle for 100ms waiting after each tiny segment.

**THE BREAKING POINT:**
The fundamental issue: the speed of light across the Atlantic is fixed. London to New York = ~72ms one way. Any protocol that waits for each acknowledgement before sending the next unit of data wastes all of that 72ms. The pipe (the network path) has a capacity measured in "bytes in flight" = bandwidth × RTT. If we only ever have 1460 bytes in flight, we're using 0.001% of a 1Gbps × 72ms = 9MB pipe.

**THE INVENTION MOMENT:**
The sliding window protocol solves this by allowing the sender to have multiple segments outstanding simultaneously — up to window_size bytes. The window "slides" forward as ACKs arrive: when segment 1 is ACKed, the window slides to allow segment N+1. This keeps the pipe full. The window size needed to fully utilise a link is exactly the bandwidth-delay product: window ≥ bandwidth × RTT. The sliding window was first described by Carr, Crocker, and Cerf in 1970 and is the foundational mechanism underlying TCP's throughput.

---

### 📘 Textbook Definition

The **sliding window protocol** is a flow-control and error-control mechanism that allows a sender to transmit multiple data units before receiving acknowledgements, bounded by a **window size** W. The sender maintains: (1) the sequence number of the earliest unacknowledged segment (left edge), and (2) the next sequence number to send (right edge ≤ left + W). The window "slides right" as ACKs arrive. The receiver maintains a similar window. In TCP: the effective window = `min(rwnd, CWND)`. Full link utilisation requires window ≥ **Bandwidth-Delay Product** (BDP = bandwidth × RTT). TCP uses cumulative ACKs (ACK=N means all bytes before N received) plus SACK (Selective ACK) for efficient out-of-order recovery.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The sliding window allows a sender to keep many segments in flight simultaneously — filling the network "pipe" to its bandwidth-delay product capacity — instead of the inefficient one-at-a-time stop-and-wait approach.

**One analogy:**
> Stop-and-wait is mailing letters one at a time: send a letter, wait for a reply, send next letter. If the post takes a week each way, you send one letter per two weeks. Sliding window is mailing 14 letters on day 1, then as each reply arrives (day 14 onwards), immediately sending another letter. The pipeline is full — 14 letters always in transit. The window (14) is the bandwidth-delay product: 1 letter/day × 14 days RTT.

**One insight:**
The **bandwidth-delay product (BDP)** is the single most important number for understanding network performance: BDP = bandwidth × RTT. To fully utilise a link, you must have at least BDP bytes in flight. If your TCP window is smaller than BDP, you are leaving bandwidth on the table. This is why tuning TCP socket buffer sizes is critical for long-distance or high-bandwidth transfers.

---

### 🔩 First Principles Explanation

**THE SENDER'S WINDOW:**
```
Sequence numbers (bytes):
     ↓ sent & ACKed   ↓ sent, unACKed  ↓ can send  ↓ cannot send yet
─────┼────────────────┼─────────────────┼────────────┼──────────────────
  0  │ 0...9999       │ 10000...19999   │20000...29999│ 30000+
─────┼────────────────┼─────────────────┼────────────┼──────────────────
     └──── discarded ─┘ ← WINDOW (20KB) →
     
Left edge (SND.UNA): 10000  — oldest unACKed byte
Right edge (SND.NXT): 20000 — next byte to send
Window limit: SND.UNA + Window = 10000 + 20000 = 30000

When ACK=15000 arrives:
  Left edge advances to 15000
  Right edge can advance to 35000
  → Window "slides right" by 5000 bytes
  → 5000 new bytes become available to send
```

**BANDWIDTH-DELAY PRODUCT CALCULATION:**
```
London → Sydney: 220ms RTT, 100 Mbps bandwidth
BDP = 100,000,000 bps × 0.220 s = 22,000,000 bits = 2.75 MB

Minimum window size needed to saturate the link: 2.75 MB
Default Linux socket buffer: 87 KB

Achievable throughput with 87KB window:
= 87,000 × 8 / 0.220 = 3.16 Mbps (not 100 Mbps!)

With 4MB window (tuned):
= 4,000,000 × 8 / 0.220 = 145 Mbps → saturates 100Mbps link ✓
```

**GO-BACK-N vs SELECTIVE REPEAT:**
Two sliding window error recovery strategies:
- **Go-Back-N**: on loss, retransmit the lost segment AND all subsequent segments. Simple but wasteful on lossy links.
- **Selective Repeat (SACK)**: retransmit only the lost segment; receiver buffers out-of-order segments. Efficient. TCP uses this with **SACK (Selective Acknowledgement)** option (RFC 2018).

**SACK (TCP Selective Acknowledgement):**
```
Sender transmits: 1-1460, 1461-2920, 2921-4380, 4381-5840
Packet 2921-4380 lost.
Receiver receives: 1-1460, 1461-2920, 4381-5840 (out of order)

Without SACK:
  ACK = 2921 (cumulative: received up to 2920)
  Sender doesn't know if 4381-5840 was received
  Sender may retransmit 2921-5840 (all three)

With SACK:
  ACK = 2921 (cumulative: received up to 2920)
  SACK block: [4381, 5840] (received out-of-order)
  Sender knows: retransmit ONLY 2921-4380
  → Much more efficient recovery
```

---

### 🧪 Thought Experiment

**SETUP:**
Compare stop-and-wait vs sliding window on a 10 Gbps fibre link with 100ms RTT, 1460-byte MSS.

**STOP-AND-WAIT:**
Cycle time = transmit_time + RTT = (1460×8 / 10×10⁹) + 0.1 = 0.0001168ms + 100ms ≈ 100ms
Throughput = 1460 bytes / 100ms = 14,600 bytes/s = 0.117 Mbps
Utilisation: 0.117 Mbps / 10,000 Mbps = 0.0012%

**SLIDING WINDOW (window = BDP):**
BDP = 10 Gbps × 0.1s = 1 Gb = 125 MB
With window = 125MB:
Pipe always full → throughput ≈ 10 Gbps → utilisation ≈ 100%

**REAL-WORLD CONSTRAINT:**
Default Linux max TCP receive buffer = 87KB (far below 125MB BDP). Achievable throughput = 87,000 bytes / 0.1s × 8 = 6.96 Mbps (0.07% of 10 Gbps!). Tuned to 256MB: ~20 Gbps theoretical → saturates 10 Gbps link.

**INSIGHT:**
On high-bandwidth, high-latency links, the bottleneck is almost never the network itself — it's the TCP window size (determined by socket buffer sizes). Tuning `net.ipv4.tcp_rmem` and `tcp_wmem` can increase throughput by 100x on long-distance links.

---

### 🧠 Mental Model / Analogy

> The sliding window is an assembly line. Each worker (network segment) starts their task as soon as materials are ready — they don't wait for the previous worker to finish. The "window" is how many tasks are in progress simultaneously. As one task completes (ACK arrives), the line advances (window slides) and a new task begins. The optimal window size is the number of tasks that keeps every worker busy simultaneously — which is exactly the bandwidth-delay product (how many segments fit in the "pipe"). A window smaller than BDP means some workers are idle (wasted bandwidth). A window larger than BDP floods the assembly line and drops items (congestion).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Instead of sending one packet and waiting for a reply before sending the next (slow), TCP sends many packets and keeps sending while waiting for replies. It keeps track of which packets have been acknowledged and always has a certain number "in flight." This is why downloads are fast — the network is always busy carrying data, not sitting idle waiting for confirmation of each individual piece.

**Level 2 — How to use it (junior developer):**
As a developer, sliding windows are automatic in TCP. What you control: socket buffer sizes. Use `SO_SNDBUF` and `SO_RCVBUF` for large transfers on high-latency links. Enable window scaling (`net.ipv4.tcp_window_scaling = 1`). For file transfers: use a single long-lived TCP connection with large buffers — `rsync`, `scp`, or `http_range` requests over persistent connections all benefit from filled windows. For benchmarking: `iperf3 -c <host> -w 8M` explicitly sets the window size to 8MB.

**Level 3 — How it works (mid-level engineer):**
TCP's window is tracked by four sequence number variables: SND.UNA (oldest unACKed), SND.NXT (next to send), RCV.NXT (next expected at receiver), RCV.WND (advertised window). The window advances atomically when cumulative ACKs arrive. SACK blocks are stored separately and allow retransmitting specific ranges without retransmitting the entire window. Linux TCP "scoreboard" tracks which sequences have been SACKed vs. lost. `tcp_sack = 1` enables SACK (default on). Delayed ACKs: receiver may delay ACK up to 200ms to batch or piggyback on data — reduces ACK traffic but can reduce window advancement rate; `TCP_QUICKACK` disables delayed ACKs for latency-sensitive protocols.

**Level 4 — Why it was designed this way (senior/staff):**
The sliding window is the solution to the fundamental trade-off between reliability and throughput in a lossy, variable-latency network. The window size needs to adapt to two independent constraints: receiver buffer capacity (flow control, rwnd) and network capacity (congestion control, CWND). Using min(rwnd, CWND) elegantly combines both constraints. The SACK evolution (Go-Back-N → Selective Repeat → TCP SACK → QUIC's stream-level ACKing) represents progressive improvements in recovery efficiency. QUIC removes HoL blocking at the protocol level by having separate sequence number spaces per stream — the logical endpoint of the sliding window evolution. The bandwidth-delay product concept is one of the most useful mental models in networking, applicable to: TCP tuning, link budget analysis, satellite communication design, cloud storage transfer optimisation, and HPC networking (RDMA, InfiniBand).

---

### ⚙️ How It Works (Mechanism)

```bash
# Benchmark TCP throughput (tests window utilisation)
# Server:
iperf3 -s

# Client: test with different window sizes
iperf3 -c <server> -w 87k -t 10   # default window
iperf3 -c <server> -w 4M  -t 10   # larger window
iperf3 -c <server> -w 16M -t 10   # large window (high BDP)

# Calculate BDP for your path
RTT_MS=$(ping -c 5 <server> | tail -1 | awk -F'/' '{print $5}')
BW_MBPS=1000  # your link speed in Mbps
python3 -c "
rtt_s = $RTT_MS / 1000
bw_bps = $BW_MBPS * 1e6
bdp_bytes = bw_bps * rtt_s / 8
print(f'RTT: {rtt_s*1000:.1f}ms')
print(f'BDP: {bdp_bytes/1024/1024:.2f} MB')
print(f'Need window >= {bdp_bytes/1024/1024:.2f} MB')
"

# Check SACK is enabled
sysctl net.ipv4.tcp_sack  # should be 1

# Monitor window size on active connection
ss -tn -o -i dst <server-ip>
# Key fields:
# cwnd:N    — congestion window in segments
# rwnd:N    — receive window in bytes
# send Xbps — effective send rate
# rcv_space — receive buffer available

# Check for window scaling in a connection
tcpdump -nn -r <pcap> | grep "wscale"
# SYN/SYN-ACK packets show "wscale N" option
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  Sliding Window: Window = 4 segments (4 × MSS) │
└────────────────────────────────────────────────┘

 Time  Sender                    Receiver
 
 t=0   [1][2][3][4]→ (send all 4)
 
 t=50ms                          [1][2][3][4] received
                                 ← ACK=2 (received 1)
 
 t=50ms [5]→ (window slides: ACK 1 received, send 5)
 
 t=60ms                          ← ACK=3
 t=60ms [6]→
 t=70ms                          ← ACK=4
 t=70ms [7]→
 t=80ms                          ← ACK=5
 t=80ms [8]→
 
 → Pipe always has 4 segments in flight
 → Throughput ≈ 4 × MSS / RTT (not 1 × MSS / RTT)
 
 ════════════════════════════════════
 
 SACK recovery when segment 3 is lost:
 
 Sender: [1][2][3][4][5] sent
 Receiver: 1,2 received; 3 LOST; 4,5 received
 
 ← ACK=3 SACK=[4,5] (cumulative=3, SACK says 4-5 OK)
 ← ACK=3 SACK=[4,5] (duplicate)
 ← ACK=3 SACK=[4,5] (triple dup ACK → fast retransmit!)
 
 Sender: retransmit ONLY segment 3
 
 ← ACK=6 (all received: 1,2,3(retransmit),4,5)
```

---

### 💻 Code Example

**Example — BDP-optimal socket buffer configuration:**
```python
import socket
import os

def create_optimized_socket(
    host: str,
    port: int,
    bandwidth_mbps: int = 1000,
    rtt_ms: float = 100.0
) -> socket.socket:
    """Create a TCP socket with BDP-optimal buffer sizes.
    
    Args:
        bandwidth_mbps: Expected link bandwidth in Mbps
        rtt_ms: Expected round-trip time in milliseconds
    """
    # Calculate bandwidth-delay product
    rtt_s = rtt_ms / 1000
    bdp_bytes = int((bandwidth_mbps * 1_000_000 / 8) * rtt_s)
    # Use 2× BDP to handle CWND growth above BDP
    buffer_size = max(bdp_bytes * 2, 256 * 1024)
    
    print(f"RTT: {rtt_ms}ms, BW: {bandwidth_mbps}Mbps")
    print(f"BDP: {bdp_bytes / (1024*1024):.2f} MB")
    print(f"Socket buffer: {buffer_size / (1024*1024):.2f} MB")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set buffers before connect() to affect the initial window
    # Note: setting SO_RCVBUF disables kernel autotuning for this socket
    # Only set if you specifically need to override autotuning
    if buffer_size > 87 * 1024:  # Only set if > default
        try:
            sock.setsockopt(socket.SOL_SOCKET,
                           socket.SO_RCVBUF, buffer_size)
            sock.setsockopt(socket.SOL_SOCKET,
                           socket.SO_SNDBUF, buffer_size)
        except OSError as e:
            # Kernel may cap at net.core.rmem_max
            print(f"Buffer set failed (check sysctl rmem_max): {e}")
    
    sock.connect((host, port))
    
    # Read actual buffer sizes (kernel may cap them)
    actual_rcv = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    actual_snd = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print(f"Actual rcvbuf: {actual_rcv/(1024*1024):.2f} MB")
    print(f"Actual sndbuf: {actual_snd/(1024*1024):.2f} MB")
    
    return sock

def throughput_test(host: str, port: int, data_size_mb: int = 100):
    """Simple throughput test demonstrating window effects."""
    import time
    
    sock = create_optimized_socket(
        host, port,
        bandwidth_mbps=1000,
        rtt_ms=100.0
    )
    
    data = os.urandom(data_size_mb * 1024 * 1024)
    
    start = time.perf_counter()
    sock.sendall(data)
    elapsed = time.perf_counter() - start
    
    throughput_mbps = (data_size_mb * 8) / elapsed
    print(f"Sent {data_size_mb}MB in {elapsed:.2f}s: "
          f"{throughput_mbps:.1f} Mbps")
    
    sock.close()
```

---

### ⚖️ Comparison Table

| Protocol | Window Mechanism | HoL Blocking | Error Recovery |
|---|---|---|---|
| Stop-and-Wait | Window = 1 segment | Extreme (every packet) | Retransmit entire packet |
| Go-Back-N | Window = N | Yes (retransmit from loss) | Retransmit loss + all after |
| Selective Repeat | Window = N (SACK) | Within connection | Retransmit only lost |
| TCP (with SACK) | min(rwnd, CWND) | Yes (stream-level) | SACK: retransmit only lost |
| QUIC | Per-stream windows | No (stream-isolated) | SACK per stream |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| A larger window always means more throughput | Window > BDP means segments must queue at the bottleneck (bufferbloat). Optimal window = BDP. Larger window = higher latency without more throughput |
| Setting SO_SNDBUF is sufficient for high throughput | Both SO_SNDBUF (sender) and SO_RCVBUF (receiver) must be large enough; the effective window is limited by min(sndbuf, rcvbuf, CWND). Also check the system-wide `net.core.rmem_max` |
| TCP SACK is optional | SACK is negotiated in the handshake and is default-enabled on all modern OS. Without SACK, every loss causes retransmission of everything from the loss point — extremely inefficient on lossy links |
| The window is fixed | The window is dynamic: rwnd changes every RTT based on receiver buffer, CWND changes based on congestion. The window can grow or shrink every round trip |
| Stop-and-Wait is only a teaching concept | Many application-level protocols inadvertently implement stop-and-wait: sequential request/response without pipelining. HTTP/1.1 without pipelining, synchronous RPC calls, database queries without batching |

---

### 🚨 Failure Modes & Diagnosis

**Low Throughput Despite Fast Network: Buffer Too Small**

**Symptom:**
`iperf3` between two hosts achieves 5 Mbps on a 1 Gbps link with 100ms RTT. Expected: 1 Gbps.

**Root Cause:**
Socket buffer smaller than BDP → window smaller than BDP → pipe underutilised.

**Diagnostic Commands:**
```bash
# Calculate expected throughput
# BDP = 1Gbps * 0.1s = 12.5MB
# Default buffer = 87KB -> max throughput = 87KB / 0.1s * 8 = 6.96 Mbps
# Measured 5 Mbps ≈ matches calculation

# Check buffer sizes on connection
ss -tn -o -i dst <remote> | grep -E "cwnd|rcv_space|send"

# Test with explicit large window
iperf3 -c <remote> -w 16M -t 30
# Should approach 1 Gbps

# Tune system-wide
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"  # up to 128MB
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_window_scaling=1

# Retest
iperf3 -c <remote> -t 30
```

**Fix:**
Increase `net.ipv4.tcp_rmem` and `tcp_wmem` max values to at least 2× BDP; ensure window scaling is enabled; verify path MTU and TSO are not fragmenting unnecessarily.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `TCP` — the sliding window is a core TCP mechanism
- `Flow Control` — the sliding window implements flow control (rwnd); understanding flow control is prerequisite

**Builds On This (learn these next):**
- `Congestion Control` — CWND is the congestion side of the window equation; min(rwnd, CWND) is the full picture
- `Bandwidth vs Throughput` — BDP and window size directly determine achievable throughput
- `Network Latency Optimization` — BDP-aware buffer tuning is one of the highest-impact optimisations for WAN transfers

**Alternatives / Comparisons:**
- `QUIC` — QUIC implements sliding windows per stream, eliminating HoL blocking; the logical next step after mastering TCP sliding windows

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Send multiple segments before waiting for │
│              │ ACK; window slides as ACKs arrive         │
├──────────────┼───────────────────────────────────────────┤
│ BDP FORMULA  │ Bandwidth × RTT = bytes needed in flight  │
│              │ e.g. 1Gbps × 100ms = 12.5 MB window      │
├──────────────┼───────────────────────────────────────────┤
│ EFFECTIVE    │ min(rwnd, CWND)                           │
│ WINDOW       │ Both flow control and congestion control  │
├──────────────┼───────────────────────────────────────────┤
│ SACK         │ Only retransmit lost segments (efficient)  │
│              │ sysctl net.ipv4.tcp_sack = 1 (default)    │
├──────────────┼───────────────────────────────────────────┤
│ TUNING       │ Buffer ≥ BDP; window scaling on;          │
│              │ iperf3 -w to test different window sizes  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Keep the pipe full: window = BDP bytes   │
│              │ always in flight, sliding as ACKs arrive" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Congestion Control → BBR → QUIC streams   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A cloud provider offers an S3-compatible object storage service. A data engineer wants to transfer 100GB of data from Sydney to London (200ms RTT) over a 10 Gbps dedicated link. The naive Python script using `boto3.upload_file()` achieves only 50 Mbps. Diagnose this systematically: (a) calculate the BDP for this path, (b) estimate the default socket buffer vs BDP and the resulting throughput ceiling, (c) identify whether single-connection TCP or multi-connection transfer (S3 multipart) is the right approach and why, (d) explain how S3 multipart upload's parallel connections each running Slow Start achieves higher aggregate throughput than one connection, and (e) calculate the optimal part size and connection count to saturate the 10 Gbps link given the BDP constraint.

**Q2.** Explain SACK (Selective Acknowledgement) in detail for the following scenario: a TCP sender has transmitted segments 1-20 (20 × 1460 bytes). Segments 5, 11, and 17 are lost. Show: (a) the SACK blocks the receiver sends in each ACK after the losses are detected, (b) exactly which segments the sender retransmits (and in what order), (c) how the sender's scoreboard tracks the state of each segment (SACKed vs. lost vs. sent), (d) the difference between this SACK recovery and what Go-Back-N would do (retransmit 5-20, then 11-20, then 17-20), and (e) the minimum number of RTTs required to recover all three losses with SACK vs Go-Back-N.
