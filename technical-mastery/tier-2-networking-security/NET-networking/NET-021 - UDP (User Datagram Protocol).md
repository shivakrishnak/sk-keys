---
id: NET-021
title: "UDP (User Datagram Protocol)"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-010, NET-014, NET-020
used_by: NET-023, NET-039
related: NET-020, NET-023, NET-039
tags:
  - networking
  - transport-layer
  - udp
  - datagram
  - connectionless
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 21
permalink: /technical-mastery/net/udp/
---

**⚡ TL;DR** - UDP sends datagrams with no connection, no
delivery guarantee, no ordering, and no congestion control.
What it lacks in guarantees it compensates with speed (no
handshake, no ACK overhead), simplicity (8-byte header),
and flexibility (application controls what gets retransmitted,
if anything). DNS, video streaming, online games, and
QUIC all use UDP.

| #021 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Port Number, Packet Structure, TCP | |
| **Used by:** | TCP vs UDP Decision Guide, HTTP/3 and QUIC Protocol | |
| **Related:** | TCP, TCP vs UDP Decision Guide, HTTP/3 and QUIC Protocol | |

---

### 🔥 The Problem This Solves

TCP's reliability guarantees come with costs: 1 RTT
connection setup, per-segment ACK overhead, head-of-line
blocking (one lost packet stalls all subsequent data),
and kernel-managed congestion control that cannot be
modified without kernel changes. For applications where
these costs exceed the benefits - DNS (single-packet
query/response), video streaming (retransmitting an old
video frame is worse than skipping it), multiplayer games
(100ms retransmit stall destroys gameplay) - UDP provides
a lower-level primitive where the application decides
exactly what reliability to add, if any.

---

### 📘 Textbook Definition

**UDP (User Datagram Protocol)** is a connectionless,
unreliable, unordered transport protocol defined in RFC 768
(1980). It provides: (1) **multiplexing** via source and
destination port numbers, (2) **error detection** via
optional 16-bit checksum (required for IPv6), (3) **no
connection state** - each datagram is independent. UDP
does NOT provide: reliable delivery, ordering, flow control,
or congestion control. A UDP datagram is sent once; if
lost, it is gone unless the application retransmits it.
The entire UDP header is 8 bytes (vs TCP's minimum 20).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
UDP is "fire and forget" - send a datagram, don't wait
for a reply, don't track if it arrived. The application
decides what, if anything, to do about losses.

**One analogy:**

> UDP is a postcard. You write it, drop it in a mailbox,
> and walk away. You don't know if it arrived. You don't
> get a receipt. If the recipient needs a response, they
> write you back (but that's your application protocol,
> not UDP itself). TCP is a certified letter with return
> receipt, insurance, and delivery confirmation.

**One insight:**
UDP isn't "broken TCP" - it's intentionally minimal.
Video conferencing is better over UDP because a 1% packet
loss is less damaging than the 100-300ms stall TCP causes
when retransmitting a late packet. The jitter from missing
one video frame is imperceptible; the freeze from waiting
for TCP retransmit is very noticeable. The right choice
between TCP and UDP depends entirely on which cost is
higher for your application.

---

### 🔩 First Principles Explanation

**UDP Header - The Minimal Transport:**

```
┌──────────────────────────────────────────────────────────┐
│  UDP Header (8 bytes - total)                            │
├──────────────────────────────────────────────────────────┤
│  Source Port     (16 bits) | Dest Port    (16 bits)      │
│  Length          (16 bits) | Checksum     (16 bits)      │
│                                                          │
│  Total: 8 bytes (vs TCP: 20 bytes minimum)               │
│                                                          │
│  Source Port: often ephemeral (OS-assigned 49152-65535) │
│  Dest Port: well-known (53 for DNS, 443 for QUIC)       │
│  Length: header + data in bytes (min 8, max 65535)      │
│  Checksum: optional IPv4, mandatory IPv6, 16-bit CRC    │
└──────────────────────────────────────────────────────────┘
```

**What UDP provides vs what TCP provides:**

```
┌──────────────────────────────────────────────────────────┐
│  Feature              │  TCP    │  UDP                   │
├───────────────────────┼─────────┼────────────────────────┤
│  Connection required  │  Yes    │  No                    │
│  Reliable delivery    │  Yes    │  No                    │
│  Ordered delivery     │  Yes    │  No                    │
│  Error detection      │  Yes    │  Yes (optional IPv4)   │
│  Flow control         │  Yes    │  No                    │
│  Congestion control   │  Yes    │  No                    │
│  Header overhead      │  20+B   │  8 bytes               │
│  Connection setup     │  1 RTT  │  0 RTT                 │
│  HOL blocking         │  Yes    │  No                    │
│  Broadcast/multicast  │  No     │  Yes                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
You're sending 10 UDP datagrams numbered 1-10.

- Datagram 5 is lost in the network
- Datagrams 6-10 arrive before 4 (reordered)

**What happens?**
With raw UDP:
- Your `recvfrom()` calls return: 1, 2, 3, 6, 7, 8, 9, 10, 4
  (in arrival order, or whatever the OS gives you)
- Datagram 5 is simply absent - no notification, no error
- You won't know 5 is missing unless you track sequence
  numbers yourself

**What DNS does:**
- Uses UDP for queries (single datagram each way)
- If no response within ~2 seconds, retransmits the query
- After 3 retries, falls back to TCP
- This is reliable-enough DNS for mostly-reliable LANs

**What video streaming does:**
- Each video frame is sent, never retransmitted
- Loss concealment: repeat last frame, interpolate, or
  show artifacts - all better than freeze waiting for TCP
- Sequence numbers in RTP header detect loss for statistics
  but lost frames are NOT retransmitted

**THE INSIGHT:**
UDP doesn't prevent reliability - it just removes the
forced reliability of TCP. DNS implements its own retry
logic. Video chooses to not retry. QUIC implements full
TCP-level reliability over UDP but in user space. The
application controls the trade-off.

---

### 🧠 Mental Model / Analogy

> UDP is the transport equivalent of a UDP socket being
> a mailbox slot: anyone can shove datagrams in (no
> connection required) and the OS delivers them to your
> process. You read them with `recvfrom()` which also
> tells you who sent it. There is no concept of a
> "connection" - each datagram is independent. If you
> want to associate responses with requests, you track
> that in your application.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is:**
UDP sends individual packets with no connection, no
retransmit, no ordering. Fast and simple. Used for DNS,
video calls, gaming, and the base layer of HTTP/3.

**Level 2 - When to use it:**
Use UDP when: (a) you need low latency more than you need
reliability (games, VoIP), (b) the protocol is
request/response in a single packet (DNS), (c) you want
to implement your own reliability (QUIC), or (d) you need
broadcast/multicast (UDP supports it, TCP doesn't). Use
TCP when data loss is unacceptable (HTTP, database
queries, file transfer, SSH).

**Level 3 - What to implement on top:**
Applications on UDP often add: (a) sequence numbers to
detect out-of-order delivery, (b) timestamps for RTT
measurement, (c) selective retransmit for critical data
only, (d) NACK-based error reporting (receiver tells
sender what's missing) vs ACK-based (receiver confirms
what arrived), (e) application-level connection ID for
connection migration (moving a connection between IPs).

**Level 4 - Production nuances:**
UDP has no built-in congestion control. A UDP sender that
floods at maximum rate CAN congest the network and
indirectly slow TCP flows (TCP backs off, UDP doesn't).
This is why QUIC implements congestion control: using UDP
without congestion control in long-haul networks is
unethical (technically, but practically: aggressive UDP
floods get rate-limited or dropped by carriers). Any
high-bandwidth UDP protocol MUST implement congestion
control. This is an explicit requirement in IETF guidelines.

---

### ⚙️ How It Works (Mechanism)

**UDP server/client pattern:**

```python
# UDP server (Python) - receives datagrams
import socket

sock = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 9000))

while True:
    data, addr = sock.recvfrom(4096)
    # addr = (sender_ip, sender_port)
    print(f"From {addr}: {data}")
    # Echo back to sender
    sock.sendto(b"ACK: " + data, addr)
```

```python
# UDP client - sends datagrams
import socket

sock = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM)

# No connect() needed - just sendto()
sock.sendto(b"Hello", ('192.168.1.100', 9000))

# Set timeout for response (application retry logic)
sock.settimeout(2.0)
try:
    response, addr = sock.recvfrom(4096)
except socket.timeout:
    print("No response - retransmit or give up")
```

**Wrong vs Right - UDP application timeout:**

```python
# BAD: no timeout - hangs forever if server drops packet
sock = socket.socket(AF_INET, SOCK_DGRAM)
sock.sendto(request, server_addr)
response, _ = sock.recvfrom(4096)  # blocks forever

# GOOD: application retry with backoff
import time

def send_with_retry(sock, data, addr, max_retries=3):
    timeout = 0.5  # start with 500ms
    for attempt in range(max_retries):
        sock.settimeout(timeout)
        try:
            sock.sendto(data, addr)
            return sock.recvfrom(4096)
        except socket.timeout:
            timeout *= 2  # exponential backoff
            print(f"Retry {attempt+1}/{max_retries}")
    raise TimeoutError("Server unreachable")
```

**Capture UDP traffic:**

```bash
# Capture DNS (UDP port 53)
sudo tcpdump -i eth0 -n "udp port 53" -v

# Capture all UDP
sudo tcpdump -i eth0 -n "udp"

# Show UDP socket statistics
ss -unp   # -u = UDP

# UDP receive buffer overflow (dropped datagrams)
netstat -s -u | grep "receive buffer errors"
# or
cat /proc/net/udp | head -5
# Note: no state column - UDP has no connection state
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DNS over UDP (the canonical UDP use case):**

```
┌──────────────────────────────────────────────────────────┐
│  DNS Query/Response (UDP port 53)                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Client                          DNS Server             │
│    │                                  │                  │
│    ├──── UDP datagram ─────────────>  │                  │
│    │  SrcPort: 54123 (ephemeral)      │                  │
│    │  DstPort: 53                     │                  │
│    │  Payload: "A record for          │                  │
│    │           google.com?"           │                  │
│    │                                  │                  │
│    │  [timeout 2s] ←── response ──── │                  │
│    │  "google.com IN A 142.250.80.78" │                  │
│    │                                  │                  │
│    If no response within 2s:          │                  │
│    [retransmit] ─────────────────>   │                  │
│    After 3 retries with no response:  │                  │
│    Fall back to TCP port 53           │                  │
└──────────────────────────────────────────────────────────┘
```

**Why DNS fallback to TCP matters:**
DNS responses over 512 bytes (or 4096 bytes with EDNS0)
fall back to TCP. DNSSEC responses are often > 512 bytes
due to signature data. Zone transfers always use TCP
(large data, reliability required). This is why firewalls
must allow BOTH UDP and TCP on port 53.

---

### ⚖️ Comparison Table

| Scenario | TCP | UDP | Reason |
|---|---|---|---|
| HTTP API requests | ✅ | ✗ | Reliability required |
| SQL database queries | ✅ | ✗ | Every byte must arrive |
| DNS lookups | ✗ | ✅ | Single packet, low latency |
| Video conferencing | ✗ | ✅ | Stale frames worthless |
| Multiplayer game state | ✗ | ✅ | Old positions worthless |
| File transfer | ✅ | ✗ | Every byte required |
| Network discovery (mDNS) | ✗ | ✅ | Broadcast required |
| VoIP audio | ✗ | ✅ | Retransmit causes gaps |
| QUIC/HTTP3 | ✗ | ✅ | UDP with app reliability |
| NTP time sync | ✗ | ✅ | Single small packet |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| UDP is faster than TCP for all cases | UDP eliminates connection overhead and retransmit delays. For initial connection, yes: UDP saves 1 RTT. But for bulk data over a lossy network, UDP with application retransmit may be SLOWER than TCP (which has highly optimized SACK). |
| UDP has no security | UDP has the SAME IP-layer security as TCP. Both can be spoofed (source IP spoofing). Both can be encrypted with DTLS. The difference: UDP's lack of connection makes amplification attacks easier (see DNS amplification DDoS). |
| UDP doesn't have connections | UDP has no kernel-tracked connections, but you can `connect()` a UDP socket to an address. This doesn't do a handshake - it just sets a default destination for `send()` and filters incoming datagrams by source address. It's a convenience, not a TCP-style connection. |
| UDP doesn't work through NAT | UDP works through NAT but requires active "hole punching" for peer-to-peer. NAT tracks UDP flows by 4-tuple with a timeout (typically 30s). Idle UDP flows are evicted from NAT tables. This is why VoIP keepalives send a packet every 20-30s. |

---

### 🚨 Failure Modes & Diagnosis

**UDP Receive Buffer Overflow - Dropped Datagrams**

**Symptom:** Application reports data loss or gaps. Wireshark
on the sender shows packets sent. Application on receiver
reports less data than sent. No TCP retransmit (nothing to
retransmit). Counter in `/proc/net/udp` shows drops.

**Root Cause:** The OS UDP receive buffer fills up faster
than the application calls `recvfrom()`. New datagrams are
silently dropped by the kernel. Default UDP receive buffer:
208KB on Linux. If your application receives 100Mbps of
UDP and processes in bursts, drops occur during processing.

**Diagnostic:**
```bash
# Check UDP receive buffer drops
netstat -s | grep "receive buffer errors"
# RcvbufErrors: 12345 ← dropped due to full buffer

# Watch in real time
watch -n 1 "netstat -su | grep 'receive buffer'"

# Check socket buffer size
ss -um
# r0 = receive buffer used, rb = max buffer

# Increase UDP receive buffer
sysctl -w net.core.rmem_max=26214400    # 25MB max
sysctl -w net.core.rmem_default=4194304 # 4MB default
```

**Fix:** Increase buffer OR process datagrams faster (separate
receive thread from processing thread). For streaming media,
accept that some loss is normal and add application-level
loss concealment.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Port Number` - how UDP multiplexes between services
- `Packet Structure` - UDP datagram within IP packet
- `TCP` - the reliable alternative for comparison

**Builds On This:**
- `TCP vs UDP Decision Guide` - decision framework
- `HTTP/3 and QUIC Protocol` - TCP reliability over UDP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Connectionless, unreliable datagram       │
│              │ protocol. 8-byte header. Fire-and-forget. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Low latency > reliability: DNS, VoIP,     │
│              │ gaming, streaming, QUIC base              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Every byte must arrive: HTTP, SSH, DB,    │
│              │ file transfer                             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ UDP is not "broken TCP." It's intentional │
│              │ minimalism. App decides what reliability  │
│              │ to add. QUIC proves this works.           │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ ss -unp (sockets), netstat -su (stats),  │
│              │ /proc/net/udp, "receive buffer errors"    │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ No timeout on recvfrom (hangs forever).   │
│              │ High-bandwidth UDP with no congestion ctl │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "UDP: 8-byte header, 0 RTT, no guarantees │
│              │  - perfect when old data is worthless."   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. UDP: 8-byte header, 0-RTT, no reliability, no ordering,
   no congestion control. Perfect when stale data is
   worthless (video, games, DNS).
2. UDP application pattern: send datagram → set timeout →
   retry on timeout. Never `recvfrom()` without a timeout.
3. High-bandwidth UDP MUST implement congestion control or
   it will saturate links and violate IETF fairness guidelines.

**Interview one-liner:**
"UDP provides connectionless, unreliable datagram delivery
with an 8-byte header and zero connection overhead. It's
chosen over TCP when retransmitting stale data is worse
than dropping it (video, gaming, VoIP) or when the request
fits in one packet (DNS). QUIC uses UDP as a base but
implements full TCP-like reliability + TLS in user space
to escape kernel TCP limitations. The critical anti-pattern
is high-bandwidth UDP without congestion control, which
can collapse network links."