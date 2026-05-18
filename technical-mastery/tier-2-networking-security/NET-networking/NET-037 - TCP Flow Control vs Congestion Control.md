---
id: NET-037
title: "TCP Flow Control vs Congestion Control"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-035, NET-036
used_by: NET-058
related: NET-020, NET-035, NET-036
tags:
  - networking
  - tcp
  - flow-control
  - congestion-control
  - performance
  - rwnd
  - cwnd
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/net/tcp-flow-vs-congestion-control/
---

**⚡ TL;DR** - Flow control and congestion control both
limit TCP throughput but protect different resources. Flow
control (rwnd) protects the *receiver's buffer* - the
receiver tells the sender how much space it has.
Congestion control (cwnd) protects the *network* -
the sender probes how much the network can handle. The
actual send rate is `min(cwnd, rwnd)`. Both being
non-zero simultaneously is normal; zero from either
causes a zero-window stall.

| #037 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Connection Lifecycle (NET-035), TCP Congestion Control (NET-036) | |
| **Used by:** | TCP Retransmit and Packet Loss | |
| **Related:** | TCP (NET-020), TCP Connection Lifecycle, TCP Congestion Control | |

---

### 🔥 The Problem This Solves

A Java service is producing data faster than a Python
consumer can process it. The consumer's read buffer fills
up. Without flow control, the producer keeps sending,
packets are dropped, and the producer retransmits in a
tight loop - wasting bandwidth. With flow control, the
consumer says "I have 0 bytes available, please stop."
The producer pauses. When the consumer processes some
data, it says "I have 16KB available now" - the producer
resumes. The network is not burdened with retransmits.

---

### 🧠 The Key Distinction

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Flow control: "how fast CAN you send?"                 │
│               ↑ determined by RECEIVER                  │
│               ↑ protects RECEIVER BUFFER                │
│               ↑ mechanism: rwnd in every ACK            │
│                                                          │
│  Congestion control: "how fast SHOULD I send?"          │
│               ↑ determined by SENDER (self-regulation)  │
│               ↑ protects NETWORK (shared resource)      │
│               ↑ mechanism: cwnd maintained by sender    │
│                                                          │
│  Effective send rate = min(cwnd, rwnd) / RTT            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### ⚙️ Flow Control: Receive Window (rwnd)

**How it works:**

```
Receiver side:
  recv_buffer = OS-allocated buffer for incoming data
  rwnd = free space in recv_buffer
  rwnd is advertised in every ACK header (16-bit field)

Sender side:
  bytes_in_flight <= rwnd
  (never have more unACKed bytes than receiver can buffer)

Application reads from recv_buffer:
  → frees space
  → rwnd increases
  → receiver sends ACK with updated rwnd
  → sender can send more
```

**Zero window:**

```
Application stops reading (busy processing, deadlock,
slow consumer), recv_buffer fills, rwnd → 0.

Sender receives ACK with rwnd = 0:
  → sender enters "zero window" state
  → stops sending (except 1-byte probe packets)
  → probe interval doubles (1s, 2s, 4s, 8s...)
  → when rwnd > 0 ACK arrives: sender resumes

Symptom: "TCP ZeroWindow" in Wireshark
         "rcvd 0 window" in kernel counters
Cause: application not reading fast enough
```

**Window scaling (RFC 1323):**

```
Original TCP: 16-bit window field = max 65,535 bytes
Problem: on 1Gbps × 100ms RTT link, BDP = 12.5 MB
  Max throughput = 64KB / 0.1s = 5.2 Mbps (link underused)

Window scale option (negotiated in SYN):
  Actual window = advertised_window × (2^scale_factor)
  Scale factor up to 14 → max window = 64KB × 16384 = 1 GB

Check negotiated window scale:
  tcpdump -v "port 80 and tcp[13] == 2"  ← SYN packets
  Look for "wscale" in SYN and SYN-ACK
```

---

### ⚙️ Congestion Control: Congestion Window (cwnd)

**How it works:**

```
Sender maintains cwnd (not sent to receiver, sender-local)
Initial cwnd = 10 segments (Linux default, RFC 6928)

At any time: bytes_in_flight <= min(cwnd, rwnd)

cwnd increases (no loss):
  Slow start: cwnd += 1 per ACK (doubles per RTT)
  Cong. avoid: cwnd += 1/cwnd per ACK (~1 per RTT)

cwnd decreases (loss detected):
  3 dup ACKs: cwnd = cwnd/2, ssthresh = cwnd/2
  Timeout: cwnd = 1, ssthresh = old cwnd/2
```

**The sender sees only ACKs (or lack of them):**

```python
# Conceptual sender state machine
cwnd = 10  # initial (segments)
ssthresh = 65535
in_flight = 0

def on_ack_received(acked_bytes):
    global cwnd, ssthresh, in_flight
    in_flight -= acked_bytes

    if cwnd < ssthresh:
        cwnd += 1  # slow start: exponential
    else:
        cwnd += 1/cwnd  # congestion avoidance: linear

def on_3_dup_acks():
    global cwnd, ssthresh
    ssthresh = cwnd / 2
    cwnd = ssthresh  # fast recovery

def on_timeout():
    global cwnd, ssthresh
    ssthresh = cwnd / 2
    cwnd = 1  # restart slow start
```

---

### ⚙️ Wrong vs Right: The Zero-Window Deadlock

```python
# BAD: sender and receiver are in the same process
# Producer writes fast, consumer is blocked on computation
# → recv buffer fills → rwnd = 0 → producer blocks on send()
# → consumer thread is blocked waiting for producer result
# → DEADLOCK

import socket, threading

def producer_consumer_deadlock():
    client, server = socket.socketpair()

    def producer():
        # Writes 10MB without checking if consumer is reading
        client.sendall(b'X' * 10 * 1024 * 1024)
        print("producer done")

    def consumer():
        # Expensive compute before reading
        result = expensive_computation()  # blocks for 10s
        data = server.recv(1024 * 1024)   # too late - buffer full
        server.close()

    threading.Thread(target=producer).start()
    threading.Thread(target=consumer).start()
    # producer blocks on sendall() because recv buffer is full
    # consumer is blocked on expensive_computation()
    # → DEADLOCK

# GOOD: keep producer and consumer on separate OS processes
# or use non-blocking sockets with epoll/select
# or use a queue between producer and consumer threads
```

---

### ⚙️ Diagnosing Which Limit is Active

```bash
# ss -tni shows both cwnd and rcv_space
ss -tni 'dst TARGET_IP' | head -6
# Example output:
# ESTAB  0    0    192.168.1.10:54321  10.0.0.5:8080
#  cubic wscale:9,9 rto:208 rtt:4.5/2.2 ato:40
#  mss:1448 pmtu:1500 rcvmss:1448
#  rcvbuf:131072 sndbuf:87040
#  rcv_space:43690 rcv_ssthresh:87380
#  cwnd:32 ssthresh:48 send 83.2Mbps
#
# Interpretation:
# cwnd:32 = 32 × 1448 = 46,336 bytes in-flight allowed (cwnd)
# rcv_space:43690 = ~43KB recv buffer free (rwnd)
# min(46KB, 43KB) = 43KB in-flight
# → flow control (rwnd) is the current limiting factor
# → throughput: 43KB / 4.5ms RTT = ~9.6 Mbps
# → fix: application reading faster, or tune SO_RCVBUF

# Check if zero window events are occurring:
netstat -s | grep -i "zero window"
# "0 window probes sent" = no zero window stalls

# Check receiver-side buffer sizes:
cat /proc/sys/net/ipv4/tcp_rmem
# 4096   87380   6291456
# min:default:max (bytes)

# Check sender-side buffer sizes:
cat /proc/sys/net/ipv4/tcp_wmem
# 4096   16384   4194304
```

---

### ⚙️ Failure Example: Misconfigured SO_SNDBUF Kills Throughput

**Symptoms:** A file transfer between two hosts achieves
only 1 Mbps on a 100 Mbps link with 20ms RTT. The hosts
are not congested. Retransmits are near zero.

**Diagnosis:**

```bash
# Check actual socket buffer on sending side
ss -tni 'dst TARGET_IP' | grep sndbuf
# sndbuf:8192   ← kernel set it to 8 KB

# Expected throughput with 8KB sndbuf:
# BDP = 100Mbps × 20ms = 250 KB
# 8KB << 250KB → buffer exhausted, sender stalls every RTT
# Max throughput = 8KB / 20ms = 3.2 Mbps (matches observation)

# Fix: set larger send buffer before connect
import socket

sock = socket.socket()
# Set 256KB send buffer
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 256*1024)
sock.connect(TARGET)
# Verify actual size (kernel may double it)
actual = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
print(f"Send buffer: {actual}")  # kernel may set to 512KB

# System-wide fix (for all sockets):
# /etc/sysctl.conf: net.ipv4.tcp_wmem = 4096 87380 16777216
# net.core.wmem_max = 16777216
```

---

### ⚙️ The Combined Equation

```
TCP effective throughput:

  throughput = min(cwnd, rwnd) / RTT

Where:
  cwnd = current congestion window (set by sender)
  rwnd = current receive window (advertised by receiver)
  RTT  = round-trip time

Bottleneck analysis:
  If cwnd << rwnd:  network is congested, or slow start
                    → wait for cwnd to grow
                    → or check for packet loss
  If rwnd << cwnd:  receiver buffer full
                    → application reading too slowly
                    → or SO_RCVBUF too small
  If cwnd ≈ rwnd ≈ BDP: fully utilizing the path
                    → limited by actual link bandwidth

Example:
  BDP = 1Gbps × 50ms = 6.25MB (4,280 segments × 1460B)
  cwnd = 200 (limited by slow start / recent loss)
  rwnd = 4096 (small recv buffer on receiver)
  
  Actual in-flight = min(200×1460, 4096) = min(292KB, 4KB)
  = 4KB (rwnd bottleneck!)
  Throughput = 4KB / 50ms = 640 Kbps  ← pathetic
  
  Fix: increase SO_RCVBUF on receiver to ≥ 6.25MB
```

---

### 📐 Scale Considerations

```
Single connection throughput math:
  throughput = min(cwnd, rwnd) / RTT

100 concurrent connections to same server:
  Server has 100 pairs of (cwnd_i, rwnd_i)
  Each managed independently
  Total network load = sum of all min(cwnd_i, rwnd_i)

Application design impact:
  A slow consumer sets rwnd → 0 on every connection
  → all produces stall waiting for consumer to read
  → use bounded queues + async processing to prevent this
  → connection pools help: fewer long-lived, well-tuned
    connections instead of many new short ones

Kernel tuning at scale (10Gbps servers):
  net.ipv4.tcp_rmem = 4096 87380 134217728  (128MB max)
  net.ipv4.tcp_wmem = 4096 65536 134217728  (128MB max)
  net.core.rmem_max = 134217728
  net.core.wmem_max = 134217728
  net.ipv4.tcp_moderate_rcvbuf = 1  ← auto-tune (default on)
```

---

### 🧭 Decision Guide

```
When I see poor throughput, which window is the limit?
  1. Run: ss -tni 'dst TARGET' | grep "cwnd\|rcv_space"
  2. If cwnd is small:  congestion control bottleneck
     → Check: packet loss, RTT increase, ssthresh
     → Wait for cwnd to grow, or investigate loss source
  3. If rcv_space is small: flow control bottleneck
     → Check: is application reading the socket promptly?
     → Increase SO_RCVBUF, or fix slow consumer

"Does flow control affect the server's throughput?
  RECEIVER's rwnd limits the SENDER's throughput.
  So if your server is the sender: fix the RECEIVER's buffer.
  If your server is the receiver: fix your own recv buffer
  (affects what clients can send to you).

Interview one-liner:
  'Flow control protects the receiver from buffer overflow
   (rwnd set by receiver). Congestion control protects the
   network from overload (cwnd set by sender). Throughput
   is min(cwnd, rwnd) / RTT.'
```