---
id: NET-077
title: "TCP Specification (RFC 793) - Core Design Decisions"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-020, NET-029
used_by: NET-083
related: NET-020, NET-029, NET-078, NET-079, NET-083
tags:
  - networking
  - tcp
  - rfc
  - protocols
  - specification
  - design-decisions
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 77
permalink: /technical-mastery/net/tcp-specification-rfc-793/
---

**⚡ TL;DR** - RFC 793 (TCP, 1981) made specific design
choices that determined how the internet works for the
next 50 years. Why 3-way handshake? Why sequence numbers?
Why sliding window? Why TIME_WAIT exists? Each choice
solved a specific problem in unreliable network delivery.
Understanding WHY these decisions were made lets you
diagnose TCP behavior in production (SYN floods, port
exhaustion, HOL blocking) by reasoning from first
principles rather than memorizing symptoms.

| #077 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | TCP - Three-Way Handshake (NET-020), TCP Flow Control (NET-029) | |
| **Used by:** | Networking Career Paths (NET-083) | |
| **Related:** | TCP Handshake, TCP Flow Control, QUIC Protocol Design (NET-078), Congestion Control Theory (NET-079), Networking Career Paths | |

---

### 🧠 The Core Design Problem (1977-1981)

```
Context: ARPANET had multiple heterogeneous networks
Goal: a single protocol for reliable data delivery
      over any unreliable underlying network
      
Problems to solve:
  1. Packets can be lost (network drops them)
  2. Packets can arrive out of order (different routes)
  3. Packets can arrive as duplicates (retransmit on false loss)
  4. Network can be congested (too much traffic)
  5. Hosts can crash mid-connection
  
Constraints:
  Routers are simple (no state per connection)
  TCP must handle reliability in endpoints (end-to-end principle)
  Must work with any link type (Ethernet, radio, satellite)
```

---

### ⚙️ Decision 1 - Three-Way Handshake

**Why not 1-way or 2-way?**

```
1-way handshake (just send data):
  Problem: receiver doesn't know sender's ISN
  Problem: duplicate SYNs from network would start fake connections
  Abandoned: cannot establish synchronized state
  
2-way handshake (SYN, SYN-ACK):
  Client: "I want to connect, my seq starts at 100"
  Server: "OK, my seq starts at 200, I acknowledge 101"
  Problem: server doesn't know if client received SYN-ACK
  Problem: delayed SYN from a previous crashed connection
             arrives → server creates half-open connection
             with no client to complete it
             
3-way handshake (SYN, SYN-ACK, ACK):
  Client → Server: SYN (seq=100)
  Server → Client: SYN-ACK (seq=200, ack=101)
  Client → Server: ACK (seq=101, ack=201)
  
  Why this works:
  Client proves reachability: ACK arrives at server
  Both sides: know the other's initial sequence number
  Duplicate old SYN: server sends SYN-ACK, no ACK arrives → RST
  
  The 3-way handshake is the minimum to:
  1. Synchronize sequence numbers in both directions
  2. Prove both sides can receive (not just send)
```

---

### ⚙️ Decision 2 - Random Initial Sequence Number (ISN)

```
Why not start at sequence 0 every time?

Problem with ISN=0:
  Connection A: src 10.0.0.1:54321, dst 10.0.0.2:80, seq 0-1000
  Connection closes.
  
  New connection B: same src/dst ports (TIME_WAIT expired)
  Also starts at seq 0
  
  If a delayed packet from connection A (seq=500) arrives:
  It matches connection B's sequence space!
  Connection B: accepts old data as if it were new
  Result: data corruption (silent, difficult to debug)
  
Why random ISN prevents this:
  Connection A: ISN = 4,293,000,000
  Delayed packet from A: seq near 4,293,000,000
  Connection B: ISN = 1,234,567 (random)
  Delayed packet from A: far outside B's window → discarded
  
  ISN randomness: the sequence number space (2^32 = 4 billion)
  is large enough that collision is practically impossible
  within the network MSL (Maximum Segment Lifetime = 120s)
  
Security implication:
  ISN must be unpredictable (not just random-looking)
  Predictable ISN: attacker can inject packets mid-connection
  TCP sequence prediction attacks: possible with weak ISNs
  Modern: cryptographically random ISN per connection
```

---

### ⚙️ Decision 3 - Sliding Window (Not Stop-and-Wait)

```
Stop-and-wait: send one segment, wait for ACK, send next
  RTT = 100ms, segment = 1500 bytes:
  Throughput = 1500 bytes / 0.1s = 12 KB/s
  Even on 1 Gbps link: wasted 99.99% of capacity
  
Sliding window: send W segments without waiting for each ACK
  Window size W = 65535 bytes (original TCP)
  RTT = 100ms:
  Throughput = 65535 bytes / 0.1s = 655 KB/s
  Better, but still limited by 16-bit window field
  
Window scale option (RFC 7323):
  Multiplier: window_size = value × 2^scale_factor
  Scale factor 8: 65535 × 256 = 16.7 MB window
  RTT = 100ms: 16.7 MB / 0.1s = 167 MB/s
  
Bandwidth-delay product:
  BDP = bandwidth × RTT
  1 Gbps link, 100ms RTT: BDP = 12.5 MB
  To saturate a 1 Gbps link with 100ms RTT:
  Must have 12.5 MB of data in-flight simultaneously
  Window must be ≥ BDP to saturate a link
  
Why this matters in production:
  Long-fat network (high bandwidth + high latency):
    AWS to EU: 100ms RTT, 10 Gbps link
    BDP: 125 MB
    Default window (no scaling): 65 KB → 0.05% utilization
    With window scaling: 125 MB → full utilization
  
  Check: ss -i "dst 10.0.0.1"
  rcv_space: current receiver window
  If rcv_space is small: throughput is window-limited
```

---

### ⚙️ Decision 4 - Cumulative ACKs

```
TCP uses cumulative acknowledgment:
  ACK number = "I've received everything up to this byte"
  Not: "I received byte 1000, 1001, 1002" (selective)
  
  Sender: seq 1000, 1001, 1002 sent
  Packet 1001 lost
  Receiver: ACK 1001 (received 1000, but NOT 1001 yet)
  Sender: retransmit from 1001 onwards (Go-Back-N)
  
Head-of-line blocking (consequence of cumulative ACKs):
  Stream of packets: all must be delivered in order
  One lost packet: all subsequent packets wait
  HTTP/1.1: each request is one TCP stream → blocked
  HTTP/2: multiple streams in one TCP connection
         → all streams blocked if one packet lost
  HTTP/3 (QUIC): per-stream loss recovery solves this
  
SACK (Selective Acknowledgment, RFC 2018):
  Extension: receiver reports which segments it has
  ACK 1001 + SACK 1002-1003: lost 1001, have 1002-1003
  Sender: retransmit only 1001 (not 1002-1003)
  Benefit: fewer retransmissions on burst packet loss
  Enabled: in most TCP implementations today
  Check: ss -ti | grep sack (shows SACK enabled)
```

---

### ⚙️ Decision 5 - TIME_WAIT (Why the Delay?)

```
After connection closes: sender enters TIME_WAIT for 2×MSL
MSL = Maximum Segment Lifetime = 60 seconds (typically)
TIME_WAIT = 120 seconds of waiting before port reuse

Why this seems wasteful:
  Close connection → wait 2 minutes before reusing port
  High-throughput services: thousands of connections/minute
  Each waiting 2 minutes → tens of thousands of TIME_WAIT sockets

Why it's necessary:
  Purpose 1: Last ACK delivery guarantee
    If client's last ACK to server's FIN is lost:
    Server: retransmits FIN
    Client must still be alive (in TIME_WAIT) to re-send ACK
    If client immediately disappeared: server gets RST instead
    This can cause data loss if server had pending data in kernel
    
  Purpose 2: Prevent delayed segment confusion
    If port is reused immediately after close:
    A delayed packet from old connection could arrive
    New connection: same port numbers
    Old packet: might be in sequence space of new connection
    TIME_WAIT: ensures all network packets from old connection expire
    (MSL is the maximum time a packet can live in the network)
    
Production implication:
  ss -s | grep TIME-WAIT: how many TIME_WAIT sockets?
  If > 10,000: likely port exhaustion risk
  Fix: increase port range, enable tcp_tw_reuse, use connection pooling
```

---

### 📐 RFC 793 Limitations That Led to Newer Protocols

```
RFC 793 limitation → modern solution:

1. 2-RTT handshake overhead → QUIC: 1-RTT (0-RTT for resumption)
   Every new TCP connection: 3-way handshake + TLS handshake
   = 2-3 RTTs before first data byte
   QUIC: combines transport + crypto handshake = 1 RTT
   
2. Head-of-line blocking → QUIC: per-stream loss recovery
   Packet loss on stream 1 → all streams wait (TCP)
   QUIC: each stream independent → only stream 1 waits
   
3. IP address bound to connection → QUIC: connection IDs
   TCP: src IP:port + dst IP:port = connection identifier
   Mobile: IP changes when WiFi→4G → TCP connection drops
   QUIC: connection ID (not IP-based) → survives IP change
   
4. Handshake in plaintext → TLS 1.3: encrypted handshake
   TCP handshake: SYN/SYN-ACK/ACK visible to MITM
   Certificate: visible before encryption established
   QUIC: encrypted from first packet
   
5. No multiplexing → SPDY/HTTP/2 → HTTP/3 over QUIC
   TCP: one byte stream → HOL blocking for multiplexed requests
   HTTP/2: virtual streams in one TCP → still 1 HOL per connection
   QUIC: N streams, each with independent delivery → no HOL
   
RFC 793 is 40+ years old and powers the internet.
Its design decisions were remarkably good given the constraints.
The limitations only became painful at the scale of modern internet.
```

---

### 🧭 Decision Guide - When RFC 793 Knowledge Matters

```
RFC 793 design knowledge helps diagnose:

SYN flood attack:
  RFC 793: 3-way handshake allocates state at server
  Attack: half-open connections exhaust server state
  Solution: SYN cookies (encodes state in ISN, no server alloc)
  
Port exhaustion:
  RFC 793: connection identified by src:port + dst:port
  Problem: finite ports (64K) × TIME_WAIT (120s) = exhaustion
  Solution: tcp_tw_reuse, port range expansion, connection reuse
  
Retransmit storms:
  RFC 793: loss detected by timeout or 3 duplicate ACKs
  Duplicate ACKs arrive fast → fast retransmit (no timeout wait)
  3 duplicate ACKs rule: minimum 4 packets needed for detection
  
Throughput on long-fat paths:
  RFC 793: window limits in-flight bytes
  BDP = bandwidth × RTT
  Window must >= BDP to saturate link
  Check: ss -i shows current window, rcv_space
  
HOL blocking:
  RFC 793: sequential byte stream = one dropped packet stalls all
  Symptom: HTTP/2 multiplexing loses benefit on lossy network
  Solution: HTTP/3 (QUIC) for lossy/high-RTT paths
```
permalink: /technical-mastery/net/tcp-specification-rfc-793-core-design-decisions/
---