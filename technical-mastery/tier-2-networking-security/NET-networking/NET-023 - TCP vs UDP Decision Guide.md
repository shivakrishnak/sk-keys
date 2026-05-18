---
id: NET-023
title: "TCP vs UDP Decision Guide"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-020, NET-021
used_by: NET-039, NET-041
related: NET-020, NET-021, NET-039
tags:
  - networking
  - tcp
  - udp
  - decision
  - tradeoffs
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/net/tcp-vs-udp-decision-guide/
---

**⚡ TL;DR** - The TCP vs UDP decision reduces to one
question: "Is retransmitting stale data better or worse
than the delay it causes?" If retransmitting is better
(HTTP, SSH, database queries) → TCP. If retransmitting
is worse or unnecessary (real-time audio/video, gaming,
DNS, QUIC's base) → UDP. When uncertain, start with TCP.

| #023 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | TCP, UDP | |
| **Used by:** | HTTP/3 and QUIC Protocol, gRPC and Protocol Buffers | |
| **Related:** | TCP, UDP, HTTP/3 and QUIC Protocol | |

---

### 🔥 The Problem This Solves

Developers default to TCP for everything, then discover
real-time applications fail because TCP's retransmit
mechanism freezes the stream for hundreds of milliseconds.
Conversely, developers who choose UDP for everything often
re-implement TCP badly (no congestion control, no proper
reliability). This guide provides a systematic decision
framework with specific criteria.

---

### 📘 Textbook Definition

**TCP vs UDP selection** is a protocol design decision
based on trade-off analysis across five dimensions:
(1) reliability requirements, (2) latency tolerance,
(3) ordering requirements, (4) connection model fit,
and (5) application control requirements. Neither is
universally superior; each is optimal for specific use
cases. A third option - QUIC - provides UDP's flexibility
with TCP-level reliability in user space.

---

### ⏱️ Understand It in 30 Seconds

**The 3-question decision:**

```
┌──────────────────────────────────────────────────────────┐
│  TCP vs UDP Decision Tree                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Q1: Is retransmitting late/lost data WORSE than         │
│      the delay it causes?                               │
│      YES → Use UDP (video, audio, gaming)               │
│      NO  → Continue                                     │
│                                                          │
│  Q2: Does every byte need to arrive in order?            │
│      YES → Use TCP (HTTP, SSH, DB queries)              │
│      NO  → Continue                                     │
│                                                          │
│  Q3: Do you need broadcast or multicast?                 │
│      YES → Use UDP (DNS mDNS, DHCP, IPTV)              │
│      NO  → Default to TCP                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🔩 First Principles Explanation

**The fundamental TCP trade-off:**

```
┌──────────────────────────────────────────────────────────┐
│  What TCP gives you         │  What TCP costs you        │
├─────────────────────────────┼────────────────────────────┤
│  Reliable delivery          │  1 RTT handshake           │
│  In-order bytes             │  Head-of-line blocking     │
│  Flow control               │  Per-connection kernel state│
│  Congestion control         │  Retransmit delays (0-3s)  │
│  Error detection            │  20+ byte header overhead  │
└──────────────────────────────────────────────────────────┘
```

**The fundamental UDP trade-off:**

```
┌──────────────────────────────────────────────────────────┐
│  What UDP gives you         │  What UDP costs you        │
├─────────────────────────────┼────────────────────────────┤
│  Zero connection overhead   │  No delivery guarantee     │
│  No HOL blocking            │  Must implement reliability │
│  App controls everything    │  Must implement ordering    │
│  8-byte header              │  Must implement congestion  │
│  Multicast/broadcast        │  control if high BW        │
│  Datagram boundaries        │  No flow control           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**Video conferencing call at 50ms RTT:**

**With TCP:**
- At t=0ms: 30 video frames/sec (one frame every 33ms)
- At t=100ms: Frame 3 is lost in transit
- At t=150ms: TCP detects loss (3 duplicate ACKs)
- At t=350ms: Frame 3 retransmitted and received
- At t=350ms: Frames 4-9 (already received) finally
  delivered to application (HOL blocking released)
- **Result:** 200ms freeze in the video. Then 6 frames
  play simultaneously (jitter burst). Terrible UX.

**With UDP + application-level loss handling:**
- At t=100ms: Frame 3 is lost
- At t=133ms: Frame 4 arrives. App notices Frame 3
  is missing (sequence number gap).
- App decision: freeze? interpolate? show last frame?
  Typically: show last known good frame (1 frame blink)
- **Result:** One frame flicker (33ms) instead of 200ms
  freeze. Significantly better for real-time video.

**THE INSIGHT:**
TCP's retransmit is the right answer when ALL subsequent
data depends on the missing data. It's the wrong answer
when subsequent data is independent and fresher than the
missing data.

---

### 🧠 Mental Model / Analogy

> **TCP is a book delivery service:** every page must
> arrive, in order. If page 50 is lost, you wait while
> they resend it before getting pages 51-200.
>
> **UDP is a live TV broadcast:** if you miss 3 seconds
> of a live game, the broadcast doesn't pause to replay
> it. You just missed 3 seconds, and the game continues.
>
> **The decision:** Are you delivering a book (TCP) or
> broadcasting live (UDP)?

---

### ⚙️ How It Works (Mechanism)

**Complete decision matrix:**

```
┌──────────────────────────────────────────────────────────┐
│  Protocol Selection Matrix                               │
├────────────────────┬─────────┬───────┬───────────────────┤
│  Use Case          │  TCP    │  UDP  │  Why              │
├────────────────────┼─────────┼───────┼───────────────────┤
│  HTTP/HTTPS        │  ✅     │  ✗    │  Every byte needed │
│  HTTP/3 (QUIC)     │  ✗      │  ✅   │  UDP+reliability   │
│  SSH               │  ✅     │  ✗    │  Interactive shell  │
│  SMTP/IMAP         │  ✅     │  ✗    │  Every email needed │
│  SQL DB query      │  ✅     │  ✗    │  Every row needed  │
│  File transfer     │  ✅     │  ✗    │  Every byte needed │
│  DNS lookup        │  ✗      │  ✅   │  1-packet req/resp  │
│  NTP               │  ✗      │  ✅   │  1-packet, latency  │
│  DHCP              │  ✗      │  ✅   │  Broadcast needed  │
│  VoIP audio        │  ✗      │  ✅   │  Stale audio worse │
│  Video streaming   │  ✗      │  ✅   │  Stale frames worse │
│  Multiplayer game  │  ✗      │  ✅   │  Old positions bad  │
│  IPTV/multicast    │  ✗      │  ✅   │  Multicast needed  │
│  Logging (UDP)     │  ✗      │  ✅   │  Lose logs, don't  │
│                    │         │       │  stall application  │
└────────────────────┴─────────┴───────┴───────────────────┘
```

**Wrong vs Right - choosing TCP for game state:**

```python
# BAD: TCP for game position updates (100 updates/sec)
# One lost position update causes 100-300ms freeze
# while TCP waits for retransmit. Players see lag spikes.
def send_player_position_BAD(tcp_sock, pos):
    data = json.dumps({'x': pos.x, 'y': pos.y}).encode()
    tcp_sock.sendall(data)  # HOL blocking on loss!

# GOOD: UDP for game state, TCP for critical events
import socket
import struct

udp_sock = socket.socket(AF_INET, SOCK_DGRAM)
tcp_sock = socket.socket(AF_INET, SOCK_STREAM)

def send_player_position_GOOD(udp_sock, seq, pos):
    # seq number so receiver can discard old positions
    data = struct.pack('>Iff', seq, pos.x, pos.y)
    udp_sock.sendto(data, server_addr)
    # Lost? The next position update (10ms later) is fine.

def send_critical_event_GOOD(tcp_sock, event):
    # Level complete, score change: use TCP - must arrive
    data = json.dumps(event).encode()
    length = struct.pack('>I', len(data))
    tcp_sock.sendall(length + data)
```

**When to implement custom reliability over UDP:**

```
┌──────────────────────────────────────────────────────────┐
│  UDP + Custom Reliability Patterns                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. STOP AND WAIT (simple):                             │
│     Send → wait for ACK → send next                    │
│     Use for: DNS (already does this)                    │
│                                                          │
│  2. SELECTIVE NACK (efficient):                         │
│     Receiver sends NACK for missing packets only        │
│     Use for: video conferencing (request only critical  │
│     I-frames, not P-frames)                             │
│                                                          │
│  3. FORWARD ERROR CORRECTION (low latency):             │
│     Send redundant data (e.g., parity packets)          │
│     Receiver can reconstruct N lost packets from        │
│     N parity packets without retransmit RTT             │
│     Use for: live video broadcast (no retransmit time)  │
│                                                          │
│  4. NONE (acceptable loss):                             │
│     NTP, DHCP, game position updates: just move on     │
│                                                          │
│  5. FULL RELIABILITY IN USER SPACE (complex):           │
│     QUIC: implements TCP-level reliability over UDP     │
│     Use for: HTTP/3, when TLS integration needed,      │
│     or when connection migration needed                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Five-dimension decision framework:**

```
┌──────────────────────────────────────────────────────────┐
│  Dimension 1: RELIABILITY                                │
│  TCP: retransmit until delivered or connection fails    │
│  UDP: none, implement yourself                          │
│  → Required fully? TCP. Optional/selective? UDP.        │
├──────────────────────────────────────────────────────────┤
│  Dimension 2: LATENCY TOLERANCE                         │
│  TCP: retransmit adds minimum 200ms (1 RTT reorder)    │
│  UDP: no forced delay                                   │
│  → Hard real-time (<50ms)? UDP. Soft real-time? Depends │
├──────────────────────────────────────────────────────────┤
│  Dimension 3: DATA FRESHNESS                            │
│  TCP: delivers all data in order (even stale)          │
│  UDP: app decides whether to use old data              │
│  → Old data worthless? UDP. Every byte needed? TCP.    │
├──────────────────────────────────────────────────────────┤
│  Dimension 4: SCALE (connections × state)               │
│  TCP: kernel tracks per-connection state (memory)      │
│  UDP: stateless (only application state)               │
│  → >100K connections? UDP might have memory advantage. │
├──────────────────────────────────────────────────────────┤
│  Dimension 5: MULTICAST/BROADCAST                       │
│  TCP: point-to-point only                              │
│  UDP: broadcast and multicast supported                 │
│  → One-to-many delivery? UDP required.                  │
└──────────────────────────────────────────────────────────┘
```

---

### ⚖️ Comparison Table

| | TCP | UDP | QUIC |
|---|---|---|---|
| **Connection setup** | 1 RTT | 0 RTT | 1 RTT (0 on resume) |
| **Reliability** | Full | None | Full (user space) |
| **HOL blocking** | Yes | No | No (per-stream) |
| **Congestion control** | Kernel | None | User space |
| **TLS integration** | Separate | Separate | Built-in |
| **Header overhead** | 20+ bytes | 8 bytes | ~20 bytes |
| **OS support required** | Standard | Standard | Library only |
| **Good for** | HTTP,SSH,DB | DNS,video,games | HTTP/3 |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| UDP is faster than TCP | For the first message: yes (0 RTT vs 1 RTT). For bulk reliable transfer: TCP is often faster because its congestion control and SACK are highly optimized and implemented in kernel with hardware offloading. Naive UDP retransmit is slower than TCP. |
| Use TCP to be safe | TCP's head-of-line blocking can make latency-sensitive apps worse than UDP. "Safe" depends on your requirements. |
| UDP is unreliable therefore bad | UDP is unreliable at the transport layer. Applications implement exactly the reliability they need. DNS is "reliable enough" with retry. QUIC over UDP is fully reliable. |
| QUIC replaces TCP | QUIC runs over UDP and provides similar guarantees to TCP, but implemented in user space. It doesn't replace TCP for existing protocols (SSH, database) but provides an alternative for protocols that can recompile to use QUIC. |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ USE TCP      │ HTTP, SSH, database, file transfer, email │
│              │ Any protocol where every byte must arrive │
├──────────────┼───────────────────────────────────────────┤
│ USE UDP      │ DNS, NTP, VoIP, video, gaming, multicast, │
│              │ logging where loss is acceptable          │
├──────────────┼───────────────────────────────────────────┤
│ USE QUIC     │ HTTP/3, when TCP HOL blocking is a proven │
│              │ problem, when 0-RTT resume is needed      │
├──────────────┼───────────────────────────────────────────┤
│ KEY QUESTION │ "Is retransmitting stale data better or   │
│              │  worse than the delay it causes?"         │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ TCP for real-time position updates:       │
│              │ HOL blocking creates game lag spikes      │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ UDP for file transfer with no reliability: │
│              │ re-implementing TCP badly                 │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"Choose TCP when every byte must arrive in order (HTTP,
SSH, databases). Choose UDP when retransmitting old data
is worse than dropping it (real-time audio/video, gaming)
or when the protocol fits a single packet (DNS, NTP).
The deciding question: 'Is retransmitting stale data
better or worse than the delay it causes?' QUIC is a
third option - UDP base with TCP-level reliability in
user space, eliminating TCP's head-of-line blocking
while keeping full reliability for HTTP/3."