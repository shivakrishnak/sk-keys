---
layout: default
title: "TCP Teardown"
parent: "Networking"
nav_order: 172
permalink: /networking/tcp-teardown/
number: "0172"
category: Networking
difficulty: ★★☆
depends_on: TCP, TCP Handshake
used_by: HTTP & APIs, Load Balancers, Microservices
related: TCP, TCP Handshake, Flow Control, Congestion Control
tags:
  - networking
  - tcp
  - teardown
  - connection
  - fin
  - time-wait
---

# 172 — TCP Teardown

⚡ TL;DR — TCP teardown is the 4-way FIN exchange that gracefully closes a connection: FIN → ACK → FIN → ACK. The closing side enters TIME_WAIT for 2×MSL (~60-120 seconds) to handle delayed packets, which can exhaust ports on high-throughput servers if connections aren't reused — and understanding TIME_WAIT is key to diagnosing connection refused errors and port exhaustion.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If a TCP connection could be torn down by simply closing the socket, two problems emerge: (1) data in flight is lost — the sender may have sent data that's still traversing the network when the receiver closes; (2) old packets can corrupt new connections — a delayed duplicate packet from a previous connection that shared the same 4-tuple could arrive and be interpreted as data in a new connection.

**THE BREAKING POINT:**
A file server sends a large file. The client receives it and closes its socket immediately. The server is still sending the last few kilobytes — they arrive at the closed socket and are discarded. The file is incomplete. Without graceful teardown, the application layer can never know whether all data was received. You need a mechanism to say "I'm done sending" AND verify the other side has received everything.

**THE INVENTION MOMENT:**
TCP's FIN (finish) mechanism solves this: a FIN is a one-directional close. Sending a FIN means "I have no more data to send" — but you can still receive. The other side ACKs the FIN (data received), finishes any remaining sends, then sends its own FIN. You ACK that FIN. Four steps total. This graceful teardown ensures both sides agree the connection is over and no in-flight data is lost. TIME_WAIT adds an additional safeguard: by waiting 2×MSL (Maximum Segment Lifetime, ~60s) after the last FIN-ACK, the closing side ensures all delayed packets from this connection have expired before the same 4-tuple can be reused.

---

### 📘 Textbook Definition

**TCP teardown** (graceful close) is the process of terminating a TCP connection using FIN (finish) segments. In the standard 4-way exchange: (1) Active closer sends FIN. (2) Passive closer ACKs the FIN (passive closer may continue sending data — half-close). (3) Passive closer sends FIN when ready. (4) Active closer sends final ACK and enters TIME_WAIT. TIME_WAIT lasts 2×MSL (Maximum Segment Lifetime, typically 60 seconds on Linux = 2×30s or 2×60s depending on kernel). An alternative is simultaneous close (both send FIN at the same time) and RST (abortive close — immediate, no guarantee). After TIME_WAIT expires, the 4-tuple (src-IP, src-port, dst-IP, dst-port) can be safely reused.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
TCP teardown is a 4-step exchange (FIN/ACK/FIN/ACK) that gracefully closes a connection, followed by TIME_WAIT — a quarantine period ensuring old packets from this connection can't corrupt future connections.

**One analogy:**
> Ending a phone call: "I'm done talking." (FIN) → "OK, I heard you're done." (ACK) → The other person finishes their sentence, then: "I'm done too." (FIN) → "Got it, bye!" (ACK) → You wait a minute before handing the phone to someone else (TIME_WAIT), just in case their last words are still echoing in the line. Compare to hanging up mid-sentence (RST — abortive close): fast but the other person doesn't know the call ended, and their last words were cut off.

**One insight:**
TIME_WAIT is often misunderstood as a bug or performance problem. It is intentional, correct behaviour. The issue arises when you have many short-lived connections (microservices, API calls) that create many TIME_WAIT sockets — potentially exhausting the ~28,000 available ephemeral ports. The solution is connection reuse, not eliminating TIME_WAIT.

---

### 🔩 First Principles Explanation

**THE FOUR STEPS:**

**Step 1: FIN (Active closer → Passive closer)**
```
TCP Header: Flags=FIN+ACK, seq=X
```
Active closer: `ESTABLISHED → FIN_WAIT_1`
Meaning: "I have no more data to send."

**Step 2: ACK (Passive closer → Active closer)**
```
TCP Header: Flags=ACK, ack=X+1
```
Passive closer: `ESTABLISHED → CLOSE_WAIT`
Active closer: `FIN_WAIT_1 → FIN_WAIT_2`
Meaning: "I received your FIN. I may still have data to send."

**Step 3: FIN (Passive closer → Active closer)**
```
TCP Header: Flags=FIN+ACK, seq=Y
```
Passive closer: `CLOSE_WAIT → LAST_ACK`
Meaning: "I'm also done sending. Connection can be closed."

**Step 4: ACK (Active closer → Passive closer)**
```
TCP Header: Flags=ACK, ack=Y+1
```
Active closer: `FIN_WAIT_2 → TIME_WAIT → (after 2MSL) CLOSED`
Passive closer: `LAST_ACK → CLOSED`

**TIME_WAIT PURPOSE:**
Two reasons for TIME_WAIT lasting 2×MSL:
1. **Reliability**: If the final ACK (step 4) is lost, the passive closer retransmits its FIN. The active closer must still be in TIME_WAIT to re-send the ACK. Without TIME_WAIT, the ACK is lost and the passive closer hangs in LAST_ACK forever.
2. **Duplicate packet prevention**: Packets from this connection could be delayed in the network for up to MSL (60 seconds). After TIME_WAIT (2×MSL), all such packets have expired. A new connection reusing the same 4-tuple won't receive stale packets from the old connection.

**RST (Abortive close):**
`RST` immediately terminates a connection. No FIN exchange, no TIME_WAIT. The receiving side gets an error: "Connection reset by peer". Used when: the application wants to discard unread data and close immediately; the port is not listening (server sends RST in response to SYN to a closed port); keepalive fails.

---

### 🧪 Thought Experiment

**SETUP:**
A microservice makes 1,000 HTTP requests/second to a backend. Each request opens a new TCP connection and closes it after the response. RTT = 2ms.

**ANALYSIS:**
- 1,000 connections/second × each produces 1 TIME_WAIT socket
- TIME_WAIT duration: 60 seconds (Linux default)
- TIME_WAIT sockets accumulating: 1,000 × 60 = 60,000 TIME_WAIT sockets
- Ephemeral ports available: ~28,000 (ports 32768-60999)
- Result: port exhaustion after ~28 seconds → new connections fail with "Address already in use" or "Cannot assign requested address"

**SYMPTOMS:**
`ss -tan | grep TIME_WAIT | wc -l` → 60,000+
New connection attempts fail: `EADDRINUSE` or `EADDRNOTAVAIL`

**SOLUTIONS (in order of preference):**
1. **Connection pooling**: reuse connections, avoid creating 1,000/second. Most impactful.
2. **HTTP keep-alive**: reuse existing TCP connections across multiple HTTP requests.
3. **SO_REUSEADDR + SO_REUSEPORT**: allow reusing TIME_WAIT ports sooner.
4. **tcp_tw_reuse = 1**: allow kernel to reuse TIME_WAIT ports for new outbound connections (safe for clients).
5. **Reduce TIME_WAIT duration**: `net.ipv4.tcp_fin_timeout` (default 60s, can reduce to 30s).
6. **Expand ephemeral port range**: `net.ipv4.ip_local_port_range = 1024 65535` (broader range).
7. **DO NOT use tcp_tw_recycle**: deprecated and broken with NAT (removed in Linux 4.12).

---

### 🧠 Mental Model / Analogy

> A half-close is like two people writing letters. Alice sends her last letter and writes "No more letters from me." (FIN) Bob acknowledges: "Got your last letter." (ACK) Bob writes two more letters (data still flowing in one direction — CLOSE_WAIT). Then Bob writes "I'm also done." (FIN). Alice acknowledges: "Got it." (ACK). Alice then sits by the letterbox for 2 minutes (TIME_WAIT) in case her last acknowledgement got lost in the mail and Bob needs to re-send his final letter. After 2 minutes, Alice knows any lingering mail from this correspondence has been delivered or lost, and she can safely use this correspondence address for a new pen pal.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
TCP teardown is how two computers politely hang up a connection. Each side says "I'm done sending" and the other confirms. There's a waiting period afterwards (TIME_WAIT) to make sure any stray data packets have expired before the same port numbers can be reused. Understanding this helps explain why many short-lived network connections can cause port exhaustion.

**Level 2 — How to use it (junior developer):**
In code, `socket.close()` triggers the FIN sequence. `socket.shutdown(SHUT_WR)` sends a FIN without closing the socket for reading (half-close). For servers: always use connection pooling or keep-alive to avoid creating thousands of short-lived connections. Monitor: `ss -s` shows counts per state — watch CLOSE_WAIT (server-side bug) and TIME_WAIT (client-side port exhaustion). Common bug: application not calling `close()` causes CLOSE_WAIT to accumulate → server leaks file descriptors.

**Level 3 — How it works (mid-level engineer):**
CLOSE_WAIT accumulation is a server-side bug: the remote side has sent FIN (entering FIN_WAIT_2), server has ACKed (entering CLOSE_WAIT), but the server application has not called `close()`. If `ss -tan | grep CLOSE_WAIT` shows thousands of entries on a server, the application has a resource leak. FIN_WAIT_2 can linger: if the active closer (client) sends FIN but the server ACKs and then never sends its FIN (server bug), the client stays in FIN_WAIT_2. `net.ipv4.tcp_fin_timeout` limits how long to stay in FIN_WAIT_2 before forceful close (default 60s). Simultaneous close: if both sides send FIN at the same time, both enter FIN_WAIT_1, both receive each other's FIN, both send ACK, both enter CLOSING, then TIME_WAIT. This is rare but handled correctly by the TCP state machine.

**Level 4 — Why it was designed this way (senior/staff):**
The TIME_WAIT 2×MSL design reflects that TCP operates over an unreliable network. MSL (Maximum Segment Lifetime, typically 60s in RFC 793) is the maximum time a TCP segment can remain in the network before being discarded. The 2×MSL wait ensures that both directions of old packets have expired. The fundamental tension: TIME_WAIT is correct but expensive at high connection rates. Solutions like `tcp_tw_reuse` and `SO_REUSEADDR` trade theoretical correctness for practical performance — safe in modern environments where RTTs are measured in milliseconds, not minutes, and actual MSL is effectively much shorter. The real solution (used in modern architectures) is connection persistence: HTTP/2, database connection pools, gRPC long-lived streams — all designed to amortise connection overhead across many requests.

---

### ⚙️ How It Works (Mechanism)

```bash
# Capture TCP teardown
tcpdump -nn -i any 'tcp[tcpflags] & (tcp-fin|tcp-rst) != 0'
# Expected output for graceful close:
# Client→Server: Flags [F.], seq X, ack Y
# Server→Client: Flags [.], ack X+1
# Server→Client: Flags [F.], seq Y, ack X+1
# Client→Server: Flags [.], ack Y+1

# Check connection states
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
# ESTABLISHED: active connections
# TIME_WAIT: recently closed (normal on busy client)
# CLOSE_WAIT: remote closed; app hasn't called close() — BUG if many

# Diagnose CLOSE_WAIT leak (find the process)
ss -tnp state close-wait
# Shows process name/PID — fix the application to call close()

# TIME_WAIT tuning for high-connection-rate clients
sysctl net.ipv4.tcp_tw_reuse          # 0=off, 1=safe reuse
sysctl net.ipv4.tcp_fin_timeout       # default 60s
sysctl net.ipv4.ip_local_port_range   # ephemeral port range

# Expand port range (default ~28000 ports → ~62000 ports)
sysctl -w net.ipv4.ip_local_port_range="1024 65535"

# Allow TIME_WAIT port reuse for new outbound connections
sysctl -w net.ipv4.tcp_tw_reuse=1

# Check TIME_WAIT count
ss -tan state time-wait | wc -l
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│  TCP 4-Way Teardown State Machine               │
└────────────────────────────────────────────────┘

 Client (active close)           Server (passive close)
 
 ESTABLISHED                     ESTABLISHED
    │                                │
    │ close() called                 │
    ▼                                │
 FIN_WAIT_1 ──── FIN ──────────────►│
                                     ▼
                              CLOSE_WAIT
    │                                │
    │◄──────────── ACK ──────────────│
    ▼                                │
 FIN_WAIT_2                         │
                              [Server sends remaining data]
    │                                │
    │         close() called         │
    │                                ▼
    │◄──────────── FIN ──────────── LAST_ACK
    │                                │
    │ ─────────── ACK ──────────────►│
    ▼                                ▼
 TIME_WAIT                        CLOSED
    │
    │ (waits 2×MSL ≈ 60-120 seconds)
    ▼
 CLOSED
 (4-tuple safe to reuse)
```

---

### 💻 Code Example

**Example — Diagnosing TIME_WAIT and CLOSE_WAIT:**
```python
import socket
import subprocess
import re
from collections import Counter

def get_tcp_states():
    """Get count of TCP connections by state using ss."""
    result = subprocess.run(
        ['ss', '-tan'],
        capture_output=True, text=True
    )
    states = Counter()
    for line in result.stdout.splitlines()[1:]:  # Skip header
        parts = line.split()
        if parts:
            states[parts[0]] += 1
    return dict(states)

def diagnose_connection_states():
    states = get_tcp_states()
    print("TCP Connection State Counts:")
    for state, count in sorted(states.items(),
                                key=lambda x: -x[1]):
        status = ""
        if state == "CLOSE_WAIT" and count > 10:
            status = "⚠️  APPLICATION BUG: not calling close()"
        elif state == "TIME_WAIT" and count > 5000:
            status = "⚠️  PORT EXHAUSTION RISK: add connection pooling"
        elif state == "ESTABLISHED":
            status = "✓ Active connections"
        print(f"  {state:20s}: {count:6d}  {status}")

# Example: proper teardown with shutdown for half-close
def send_and_receive(host: str, port: int, request: bytes) -> bytes:
    """Send data, then half-close (FIN) to signal end of request.
    Wait for response, then full close.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Send request data
    sock.sendall(request)
    
    # Half-close: send FIN (no more data from us)
    # Server now knows we're done sending
    sock.shutdown(socket.SHUT_WR)
    
    # Receive response until server closes
    response = b''
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break  # Server sent FIN (empty recv = EOF)
        response += chunk
    
    # Full close: server's FIN already received; send our ACK via close()
    sock.close()
    
    return response
```

---

### ⚖️ Comparison Table

| Aspect | Graceful Close (FIN) | Abortive Close (RST) |
|---|---|---|
| Steps | 4-way FIN exchange | Immediate |
| Data in flight | Preserved | Discarded |
| TIME_WAIT | Yes (active closer) | No |
| Peer notification | Graceful EOF | `Connection reset by peer` error |
| Use case | Normal connection end | Error conditions, discard unread data |
| Half-close possible | Yes (one direction) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TIME_WAIT is a bug or performance problem | TIME_WAIT is correct behaviour preventing packet mix-up; the performance problem is creating too many short-lived connections, not TIME_WAIT itself |
| `tcp_tw_recycle` fixes TIME_WAIT exhaustion | `tcp_tw_recycle` was removed in Linux 4.12 for being broken with NAT (breaks connections from clients behind NAT); never use it |
| `SO_REUSEADDR` and `tcp_tw_reuse` are the same | `SO_REUSEADDR` allows binding a port in TIME_WAIT (for servers after restart). `tcp_tw_reuse` allows reusing TIME_WAIT connections for new outbound connections (for clients). Different use cases. |
| CLOSE_WAIT is normal | Many CLOSE_WAIT connections indicate an application bug — the remote side closed the connection but the local application hasn't called `close()`. File descriptor leak. |
| RST closes connections faster with no downsides | RST discards data in flight — appropriate for error cases but should not be used as a performance optimisation for normal connection closure |

---

### 🚨 Failure Modes & Diagnosis

**Port Exhaustion from TIME_WAIT**

**Symptom:**
`Cannot assign requested address (EADDRNOTAVAIL)` or `Address already in use (EADDRINUSE)` when making outbound connections. New connections to the backend start failing.

**Root Cause:**
High connection rate + short connection lifetime → thousands of TIME_WAIT sockets exhausting ephemeral port range.

**Diagnostic Commands:**
```bash
# Count TIME_WAIT sockets
ss -tan state time-wait | wc -l

# Check ephemeral port range
cat /proc/sys/net/ipv4/ip_local_port_range
# default: 32768 60999 = 28231 ports

# Watch connection state churn in real time
watch -n 1 "ss -tan | awk '{print \$1}' | sort | uniq -c"

# Confirm error in application logs
# Java: java.net.BindException: Address already in use
# Python: OSError: [Errno 98] Address already in use
```

**Fix (in order of priority):**
1. Add HTTP connection pooling (requests.Session, Apache HttpClient pool)
2. Enable TCP keep-alive and keep connections alive
3. `sysctl -w net.ipv4.tcp_tw_reuse=1` (safe for outbound)
4. `sysctl -w net.ipv4.ip_local_port_range="1024 65535"` (more ports)
5. `sysctl -w net.ipv4.tcp_fin_timeout=30` (reduce TIME_WAIT duration)

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `TCP` — teardown is part of TCP's connection lifecycle
- `TCP Handshake` — complementary to teardown; both are part of TCP's connection state machine

**Builds On This (learn these next):**
- `Flow Control` — teardown occurs after all data is transferred; flow control manages the data transfer phase
- `Congestion Control` — TCP's congestion window state is discarded at teardown; a new connection starts fresh

**Alternatives / Comparisons:**
- `QUIC` — QUIC connection teardown uses a `CONNECTION_CLOSE` frame with no TIME_WAIT equivalent (UDP has no state, so old packets naturally expire)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STEPS        │ FIN → ACK → FIN → ACK (4-way exchange)   │
│              │ Then: TIME_WAIT for 2×MSL (60-120s)       │
├──────────────┼───────────────────────────────────────────┤
│ TIME_WAIT    │ Active closer waits 2×MSL before reuse.   │
│              │ Prevents stale packets corrupting new conn│
├──────────────┼───────────────────────────────────────────┤
│ CLOSE_WAIT   │ Remote closed; you haven't. If many:      │
│              │ application bug — not calling close()     │
├──────────────┼───────────────────────────────────────────┤
│ PORT EXHAUST │ Many TIME_WAIT → too few ephemeral ports  │
│              │ Fix: connection pooling (not tcp_tw_recycle│
├──────────────┼───────────────────────────────────────────┤
│ RST          │ Abortive close — data discarded, no wait  │
│              │ Peer sees "Connection reset by peer"      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Polite hang-up: each side says done;     │
│              │ wait to ensure no stale packets remain"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Flow Control → Congestion Control → QUIC  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A production API gateway handles 5,000 requests per second to a backend pool of 10 servers. Each request creates a new TCP connection from the gateway to a backend (no connection pooling). Calculate: (a) how many TIME_WAIT sockets accumulate on the gateway after 60 seconds, (b) whether the default ephemeral port range (32768-60999) is sufficient, (c) what error the gateway logs when port exhaustion occurs, (d) the minimum connection pool size required to serve 5,000 req/s with 10ms backend response time, and (e) if you also add an 80ms timeout for idle connections in the pool, how does this affect TIME_WAIT accumulation?

**Q2.** Explain the CLOSE_WAIT bug in a Java application. A Java server uses a thread pool to handle connections. The bug: a `SocketInputStream.read()` call returns -1 (EOF — client sent FIN), but the thread logs an error and returns to the pool without calling `socket.close()`. (a) What state does the server-side socket enter? (b) What state is the client in waiting for the server's FIN? (c) After 1 hour with 100 req/s, how many stuck sockets accumulate? (d) What system-level symptom appears first (file descriptor limit or port exhaustion)? (e) Write the corrected Java code using try-with-resources to ensure `socket.close()` is always called.
