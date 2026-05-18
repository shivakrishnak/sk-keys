---
id: NET-056
title: "Nagle's Algorithm and TCP_NODELAY"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★
depends_on: NET-020, NET-029
used_by: NET-057, NET-058
related: NET-020, NET-029, NET-057
tags:
  - networking
  - tcp
  - nagle
  - tcp-nodelay
  - latency
  - performance
  - optimization
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/net/nagles-algorithm-and-tcp-nodelay/
---

**⚡ TL;DR** - Nagle's algorithm buffers small TCP sends
until either: a full MSS packet is accumulated, or all
previous unacknowledged data has been ACKed. This reduces
"silly window syndrome" - wasteful transmission of many
tiny packets. But it adds up to 200ms latency for
interactive/streaming protocols: HTTP/2 streams, gRPC,
database queries, Redis, SSH keystrokes. TCP_NODELAY
disables Nagle's - almost always correct for low-latency
applications and is already set by most modern frameworks.

| #056 | Category: Networking | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | TCP Deep Dive (NET-020), Socket Programming (NET-029) | |
| **Used by:** | epoll and io_uring (NET-057), eBPF for Networking (NET-058) | |
| **Related:** | TCP Deep Dive, Socket Programming, epoll and io_uring | |

---

### 🔥 The Problem This Solves

A Redis client shows 200ms latency for simple GET/SET
operations. The same Redis server from a different client
returns in 0.1ms. The slow client uses a TCP library
that has Nagle's algorithm enabled. Redis sends the
response in one small packet (< MSS). Nagle buffers the
response, waiting for more data. The 40ms delayed ACK
timer triggers first. Together: 40ms+ latency added to
every Redis operation. Fix: `TCP_NODELAY` on the Redis
client socket.

---

### 🧠 Intuition: The Buffering Trade-Off

```
Without Nagle (TCP_NODELAY):
  App writes 1 byte → immediately sent as 1-byte TCP segment
  App writes 1 byte again → immediately sent
  Result: 40 × 1-byte packets for "hello world typed one key at a time"
  Each: 20 IP header + 20 TCP header + 1 data = 41 bytes overhead
  Efficiency: 1/41 = 2.4% → "silly window syndrome"

With Nagle (default):
  App writes 1 byte → wait
  More data? Buffer it
  Either: buffer reaches MSS (1460 bytes) → send full packet
  Or: no outstanding unACKed data → send what we have
  
  Efficiency: much better for bulk transfer
  Latency: worse for interactive (each write waits)

The conflict: Nagle + Delayed ACK = worst case
  Nagle: "wait for ACK before sending small data"
  Delayed ACK: "wait 40ms before sending ACK"
  Together: sender waits for ACK, receiver waits to ACK
  Result: 40ms forced latency per small exchange
```

---

### ⚙️ How Nagle's Algorithm Works

```
Nagle's rule (RFC 896):
  Send immediately IF:
    1. Packet size >= MSS (full segment), OR
    2. No unacknowledged data outstanding

  Otherwise: buffer until one of those conditions is met

  State machine:
  - App write → check condition
  - If condition met: send now
  - If not: add to buffer, wait for ACK
  - On ACK received: send buffered data (if any)

Example with Nagle enabled (HTTP/1.1 request):
  App writes "GET / HTTP/1.1\r\n" → 18 bytes
  Condition: no unACKed data → SEND immediately
  App writes "Host: example.com\r\n" → 20 bytes
  Condition: first packet unACKed → BUFFER (wait)
  ...
  ACK arrives → SEND buffered data
  
  Result: 2+ segments instead of 1 (due to buffering delay)
  
Example with TCP_NODELAY:
  App writes "GET / HTTP/1.1\r\n" → SEND immediately
  App writes "Host: example.com\r\n" → SEND immediately
  (But: app should cork or buffer in userspace for efficiency)
```

---

### ⚙️ Setting TCP_NODELAY in Code

```java
// Java: TCP_NODELAY on a socket
import java.net.Socket;
import java.net.SocketException;

Socket socket = new Socket("service-host", 8080);
socket.setTcpNoDelay(true);  // Disables Nagle's
// Must be set BEFORE data is sent (preferably after connect)

// Netty (Java NIO framework) - always set TCP_NODELAY:
ServerBootstrap bootstrap = new ServerBootstrap();
bootstrap.childOption(ChannelOption.TCP_NODELAY, true);
// Without this: every write in Netty goes through Nagle
// causing latency spikes on small messages

// Spring WebFlux / Reactor Netty - already sets TCP_NODELAY
// by default: confirmed in Netty's DefaultChannelConfig
```

```python
# Python socket:
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(("service-host", 8080))

# Python's http.client and requests:
# Do NOT set TCP_NODELAY by default!
# For low-latency HTTP: consider httpx with custom transport
# or use socket-level control

# aiohttp (async): TCP_NODELAY configurable via connector:
import aiohttp
connector = aiohttp.TCPConnector(
    # Note: aiohttp does NOT expose TCP_NODELAY directly
    # Use custom socket factory for this
)
```

```go
// Go: TCP_NODELAY is ENABLED by default for net.Dial()
// No action needed - Go's dialer sets it automatically

// Verify: net/internal/nettest or trace syscalls
// syscall.SetsockoptInt(fd, syscall.IPPROTO_TCP,
//                       syscall.TCP_NODELAY, 1)
```

---

### ⚙️ Wrong vs Right: Nagle + Delayed ACK Trap

```python
# BAD: sending headers then body separately (HTTP-like pattern)
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("server", 8080))
# NO TCP_NODELAY set - Nagle enabled

# Send HTTP request in two writes (common mistake):
sock.send(b"GET / HTTP/1.1\r\n")     # Write 1: sent immediately
sock.send(b"Host: example.com\r\n\r\n")  # Write 2: BUFFERED by Nagle
# Nagle: "first packet not ACKed yet, buffer the second"
# Server's delayed ACK: "wait 40ms before ACKing"
# → 40ms delay before second write is sent

# Actual measured: ~40ms for simple HTTP headers to be sent
# vs expected < 1ms

# GOOD option 1: TCP_NODELAY
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.send(b"GET / HTTP/1.1\r\n")          # sent immediately
sock.send(b"Host: example.com\r\n\r\n")   # sent immediately

# GOOD option 2: TCP_CORK (Linux) - buffer in userspace, send as one
import socket, struct
TCP_CORK = 3  # Linux only
sock.setsockopt(socket.IPPROTO_TCP, TCP_CORK, 1)  # cork
sock.send(b"GET / HTTP/1.1\r\n")
sock.send(b"Host: example.com\r\n\r\n")
sock.setsockopt(socket.IPPROTO_TCP, TCP_CORK, 0)  # flush
# All data sent as one segment (similar to writev/sendmsg)

# GOOD option 3: combine into single write
request = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
sock.send(request)  # one write → one packet → no Nagle delay
```

---

### ⚙️ Debugging Nagle's Algorithm Symptoms

```bash
# SYMPTOM: intermittent ~40ms latency spikes
# SUSPECTED: Nagle + Delayed ACK interaction

# 1. Measure actual latency with strace timing:
strace -e trace=network -T -p $(pgrep myapp) 2>&1 | \
  grep -E "send|recv"
# Look for 40ms gaps between send() and recv() completing

# 2. tcpdump: observe packet timing
sudo tcpdump -i lo -n -tt "port 8080" 2>&1 | head -40
# Look for: write 1 sent, then 40ms gap, then write 2 sent
# 14:23:01.000000 → write 1
# 14:23:01.040000 → write 2  ← 40ms = delayed ACK timeout

# 3. Check if TCP_NODELAY is set on production sockets
# Linux /proc (approximate - not reliable for all processes):
ss -tni dst :8080 | grep -i nodelay
# No direct /proc inspection; use strace at socket creation:
strace -e setsockopt -f -p $(pgrep myapp) 2>&1 | \
  grep TCP_NODELAY

# 4. Verify with ss -o (shows keepalive timer, not NODELAY):
ss -tni "dst :6379"  # Redis connections
# Look at Retransmits and RTT fields

# 5. If using Redis/Memcached: they already expect TCP_NODELAY
# redis-cli sets it: check client library source
```

---

### 📐 Scale Considerations

```
When Nagle's matters at scale:

Low-latency services (Redis, Memcached, gRPC):
  TCP_NODELAY is standard - nearly all clients set it
  Without it: 40ms latency per operation × M operations = death

Bulk data transfer (file uploads, streaming):
  Nagle HELPS: fewer packets, better throughput
  TCP_CORK is better than TCP_NODELAY for writes
  Kernel's sendfile() bypasses this entirely (zero-copy)

HTTP/2 and HTTP/3:
  HTTP/2: Nagle can affect stream multiplexing
  HEADERS + DATA frames sent separately: Nagle buffers DATA
  Fix: libraries send combined (or use TCP_CORK internally)
  HTTP/3 (QUIC over UDP): no Nagle at all; UDP is a raw channel

Database connections:
  PostgreSQL libpq: sets TCP_NODELAY by default
  MySQL Connector/J: TCP_NODELAY off by default (!)
    → Add: tcpNoDelay=true to JDBC URL for MySQL

Service mesh (Istio/Envoy):
  Envoy proxy: TCP_NODELAY set on all proxied connections
  Envoy also manages cork/flush for efficiency

Kubernetes:
  No special consideration - each container has standard
  TCP stack; TCP_NODELAY must be set at application level
```

---

### 🧭 Decision Guide

```
Should I set TCP_NODELAY?

YES (always):
  Redis, Memcached clients (small request/response)
  gRPC connections (streaming, many small messages)
  Database connections (query + result)
  SSH tunnels (keystrokes are small)
  Any real-time protocol (chat, gaming)
  HTTP clients making rapid sequential requests

NO (Nagle can help):
  Bulk data upload (large file transfer via TCP)
  Log streaming to Elasticsearch (large batches)
  Any write-only stream with large payloads

Use TCP_CORK instead of TCP_NODELAY when:
  Building a protocol with multiple writes per logical message
  Want efficiency (one packet per message) without Nagle
  Linux-only applications

Default in popular libraries:
  Netty: TCP_NODELAY NOT set by default → CONFIGURE IT
  Go net: TCP_NODELAY = true (always on)
  Python requests: TCP_NODELAY not set → may have issues
  Redis clients (jedis, lettuce): TCP_NODELAY = true
  JDBC (PostgreSQL): TCP_NODELAY = true
  JDBC (MySQL): TCP_NODELAY = false → add tcpNoDelay=true

Quick diagnostic:
  Latency 40ms on small payloads → Nagle + Delayed ACK
  Latency 200ms on small payloads → possibly TLS + Nagle
  Set TCP_NODELAY → re-test → latency drops to <1ms → confirmed
```