---
id: NET-029
title: "Socket Programming Basics"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-010, NET-020
used_by: NET-033, NET-047
related: NET-020, NET-021, NET-033
tags:
  - networking
  - sockets
  - tcp
  - programming
  - api
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/net/socket-programming-basics/
---

**⚡ TL;DR** - A socket is a file descriptor that represents
one endpoint of a network connection. The POSIX socket API
(socket/bind/listen/accept/connect/send/recv/close) is the
universal interface between applications and the OS
networking stack. Every network library, framework, and
protocol (HTTP, database drivers, messaging systems) sits
on top of this API. Understanding sockets makes all
networking code transparent.

| #029 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Port Number, TCP | |
| **Used by:** | Build a TCP Client-Server (Phase 2), Connection Pooling | |
| **Related:** | TCP, UDP, Build a TCP Client-Server (Phase 2) | |

---

### 🔥 The Problem This Solves

HTTP clients, database drivers, message queue clients,
and gRPC stubs all look like magic: call a function, data
goes to a remote server. In reality, they all use the
same 6 operating system calls: socket, bind/connect,
send, recv, close. Understanding the socket API removes
the abstraction layers from any networking library and
enables direct diagnosis of connection issues, performance
tuning, and protocol implementation.

---

### 📘 Textbook Definition

A **socket** is an endpoint for network communication,
represented by a file descriptor in POSIX operating
systems. The **Berkeley sockets API** (BSD sockets, POSIX
sockets) defines the standard interface: `socket()`
creates an endpoint, `bind()` assigns an address, `listen()`
marks it as server, `accept()` accepts connections,
`connect()` establishes outbound connections, `send()/recv()`
transfer data, `close()` terminates. The socket API
abstracts the difference between TCP (stream, connected),
UDP (datagram, connectionless), and Unix domain sockets
(local IPC).

---

### ⏱️ Understand It in 30 Seconds

**The 3 socket types you need to know:**

```
AF_INET, SOCK_STREAM   = TCP socket
  - Connection-oriented (connect/accept)
  - Reliable, ordered byte stream
  - Used by: HTTP, SSH, database drivers

AF_INET, SOCK_DGRAM    = UDP socket
  - Connectionless (sendto/recvfrom)
  - Unreliable datagrams
  - Used by: DNS, NTP, QUIC base

AF_UNIX, SOCK_STREAM   = Unix domain socket
  - Local IPC (same machine only)
  - No network overhead
  - Used by: PostgreSQL local, Docker daemon, systemd
```

**The complete server lifecycle in 7 calls:**

```python
socket() → bind() → listen() → accept() → recv() → send() → close()
```

**The complete client lifecycle in 5 calls:**

```python
socket() → connect() → send() → recv() → close()
```

---

### 🔩 First Principles Explanation

**What happens when you call `connect()`:**

```
┌──────────────────────────────────────────────────────────┐
│  connect() Internal Flow (TCP)                           │
├──────────────────────────────────────────────────────────┤
│  Application calls connect(sock, server_addr, port)     │
│                                                          │
│  1. OS selects ephemeral source port (49152-65535)      │
│     (unless bind() was called first)                    │
│                                                          │
│  2. OS sends TCP SYN to server IP:port                  │
│                                                          │
│  3. connect() BLOCKS until:                             │
│     a. SYN-ACK received → sends ACK → returns 0 (OK)   │
│     b. RST received → returns ECONNREFUSED              │
│     c. Timeout (SYN retransmits for ~75s) → ETIMEDOUT  │
│     d. ICMP unreachable → ENETUNREACH                   │
│                                                          │
│  4. After connect() returns 0:                          │
│     TCP state is ESTABLISHED                            │
│     4-tuple locked in: local IP:port ↔ remote IP:port  │
└──────────────────────────────────────────────────────────┘
```

**What happens in the server's `accept()` loop:**

```
┌──────────────────────────────────────────────────────────┐
│  TCP Server Accept Queue                                 │
├──────────────────────────────────────────────────────────┤
│  listen(sock, backlog=128):                             │
│    Creates two queues:                                  │
│    - SYN queue: partially-established connections        │
│      (SYN received, SYN-ACK sent, waiting for ACK)     │
│    - Accept queue: fully-established connections         │
│      (3-way handshake complete, waiting for accept())   │
│                                                          │
│  accept() blocks until accept queue has an entry:       │
│    Returns NEW socket fd for that specific connection   │
│    Original listening socket unchanged (keeps listening)│
│                                                          │
│  If accept queue overflows (backlog exceeded):          │
│    New SYNs are dropped (client retransmits SYN)        │
│    Not a hard error for client, but causes latency      │
│    Seen when: app too slow to call accept(), DDoS       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP: Why does accept() return a NEW socket?**

You call `accept()` on a server socket bound to port 8080.
A client connects from `192.168.1.50:52000`.
`accept()` returns a new socket (file descriptor 4).

**The new socket's 4-tuple:**
```
local:  0.0.0.0:8080  (the listening socket)
becomes:
fd 4:   server_ip:8080 ↔ 192.168.1.50:52000
```

**Why two sockets?**
The original listening socket on port 8080 must remain
available for the next client connection. If you used
the same socket, accepting one client would block all
others. The returned `accept()` socket is a NEW socket
that represents only this one specific connection.

**This explains:**
- Why you can have 10,000 connections to port 8080 on
  one server: one listening socket + 10K connected sockets
- Why the 4-tuple (src IP, src port, dst IP, dst port)
  must be unique: each connection is its own socket
- Why `ss -lntp | grep :8080` shows 1 LISTEN socket even
  when you have 10K established connections

---

### 🧠 Mental Model / Analogy

> A server socket is a telephone company's main number.
> One number (port 8080) that many people can call.
> But the receptionist (accept()) hands each caller
> to a dedicated agent (new socket fd) who handles that
> conversation exclusively.
>
> The main number is never "busy" - it always accepts
> new calls (up to the backlog queue limit). Each caller
> gets their own agent.
>
> `send()` and `recv()` on the connected socket are like
> the agent talking and listening on their specific line.

---

### ⚙️ How It Works (Mechanism)

**Complete TCP server and client in Python:**

```python
# TCP Server
import socket
import threading

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break   # client closed connection
            conn.sendall(data)  # echo back

def run_server(host='0.0.0.0', port=8080):
    # socket() - create socket endpoint
    # AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) as s:
        # SO_REUSEADDR: don't fail if port in TIME_WAIT
        s.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind() - assign local address and port
        s.bind((host, port))
        # listen() - mark as server, set backlog
        s.listen(128)
        print(f"Listening on {host}:{port}")
        while True:
            # accept() - blocks, returns new socket+addr
            conn, addr = s.accept()
            # Handle each connection in its own thread
            t = threading.Thread(
                target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
```

```python
# TCP Client
import socket

def run_client(host='127.0.0.1', port=8080):
    with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) as s:
        # connect() - blocks until ESTABLISHED or error
        s.connect((host, port))
        # send() - write to stream (may not send all)
        # sendall() - loops until all data sent
        s.sendall(b"Hello, server!")
        # recv() - blocks until data available
        data = s.recv(4096)
        print(f"Received: {data.decode()}")
```

**Wrong vs Right - common socket mistakes:**

```python
# BAD 1: not setting SO_REUSEADDR on server
# After server restart, bind() fails for 60 seconds:
# "OSError: [Errno 98] Address already in use"
# (port stuck in TIME_WAIT from previous connections)
s = socket.socket(AF_INET, SOCK_STREAM)
s.bind(('0.0.0.0', 8080))  # may fail after restart!

# GOOD: always set SO_REUSEADDR before bind()
s = socket.socket(AF_INET, SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 8080))  # works even after restart

# BAD 2: using recv() assuming full message arrives
data = sock.recv(4096)
message = json.loads(data)  # fails if partial message!
# TCP is a byte stream - recv() may return partial data

# GOOD: length-prefix framing (see NET-020 TCP entry)
import struct
def recv_exact(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError("Connection closed")
        buf += chunk
    return buf

def recv_message(sock):
    # Read 4-byte length prefix
    length = struct.unpack('>I', recv_exact(sock, 4))[0]
    return recv_exact(sock, length)

# BAD 3: blocking socket with no timeout
sock.connect((host, port))  # blocks for up to 75s if host down

# GOOD: set timeout before connect
sock.settimeout(5.0)         # fail after 5s
try:
    sock.connect((host, port))
    sock.settimeout(None)    # reset to blocking after connect
except socket.timeout:
    print("Connection timed out")
```

**Key socket options:**

```python
# SO_REUSEADDR - allow bind to port in TIME_WAIT
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# TCP_NODELAY - disable Nagle's algorithm
# Essential for interactive/real-time apps (SSH, gaming)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# SO_KEEPALIVE - OS sends keepalive probes for idle connections
# Detects dead connections (network dropped between sends)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
# TCP_KEEPIDLE: seconds before first probe (default 7200s!)
import socket as sock
s.setsockopt(sock.IPPROTO_TCP, sock.TCP_KEEPIDLE, 60)
# TCP_KEEPINTVL: seconds between probes
s.setsockopt(sock.IPPROTO_TCP, sock.TCP_KEEPINTVL, 10)
# TCP_KEEPCNT: number of probes before declaring dead
s.setsockopt(sock.IPPROTO_TCP, sock.TCP_KEEPCNT, 3)
# After 60s + 3×10s = 90s idle → connection declared dead

# SO_RCVBUF / SO_SNDBUF - override buffer size
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Non-blocking sockets and event loops:**

```python
# Production servers use non-blocking sockets + selector
# This is how asyncio, nginx, Node.js work internally

import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock, mask):
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1024)
    if data:
        conn.sendall(data)  # echo
    else:
        sel.unregister(conn)
        conn.close()

# Server setup
server = socket.socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(('', 8080))
server.listen(100)
server.setblocking(False)
sel.register(server, selectors.EVENT_READ, accept)

# Event loop - handle ALL sockets without blocking
while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
# This handles 10K+ connections in a single thread
```

**WHAT CHANGES AT SCALE:**
At 10,000 concurrent sockets, the default approach of
one thread per connection (above TCP server example)
uses 10K OS threads × ~1MB stack = 10GB RAM just for
thread stacks. This is the "C10K problem" (1999). Modern
solutions: non-blocking sockets + event loop (epoll on
Linux, kqueue on macOS) = one thread handles 10K+ sockets
with `O(1)` wakeup per ready socket. This is what
Node.js, asyncio, Netty, Nginx, and NGINX unit use.
The `epoll` entry (NET-057) covers this in depth.

---

### ⚖️ Comparison Table

| Call | TCP | UDP |
|---|---|---|
| `socket()` | `SOCK_STREAM` | `SOCK_DGRAM` |
| `bind()` | Optional for client | Optional for client |
| `listen()` | Server only | Not used |
| `accept()` | Server only | Not used |
| `connect()` | Establishes TCP 3-way | Optional (sets default dest) |
| Send | `send()`/`sendall()` | `sendto(addr)` |
| Receive | `recv()` | `recvfrom()` (returns addr) |
| `close()` | 4-way FIN | Just closes socket |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `send()` sends all the data | `send()` returns the number of bytes actually sent, which may be less than requested (if the send buffer is full). Always use `sendall()` or implement a send loop. |
| `recv()` receives one message | `recv()` returns up to `bufsize` bytes - could be less. For TCP, there are NO message boundaries. Multiple sends may arrive in one recv(). Always implement message framing. |
| Closing a socket immediately frees the port | TCP sockets enter TIME_WAIT state (60 seconds) after close. The port cannot be reused during TIME_WAIT unless `SO_REUSEADDR` is set. Servers MUST set this option. |

---

### 🚨 Failure Modes & Diagnosis

**Accept Queue Full - SYNs Dropped**

**Symptom:** Server is running. Client SYN-ACKs stop
arriving. Client keeps retransmitting SYN (1s, 2s, 4s).
Server `ss -lntp` shows 1 LISTEN socket but `ss -s` shows
many syn connections. Application CPU is high.

**Root Cause:** The kernel's accept queue (completed
3-way handshakes waiting for `accept()` call) is full.
The `listen(sock, backlog)` backlog parameter sets the
maximum queue length. If the application is too slow to
call `accept()` (processing bottleneck), new connections
are silently dropped.

**Diagnosis:**
```bash
# Check accept queue length and backlog
ss -lnt
# Recv-Q: current queue depth
# Send-Q: backlog (max queue size)
# If Recv-Q == Send-Q: queue is FULL

# Check kernel overflow counter
netstat -s | grep "SYNs to LISTEN"
# "X SYNs to LISTEN sockets dropped" = accept queue overflow

# Check application latency (is accept() fast enough?)
# strace: see how long between accept() calls
sudo strace -p PID -e trace=accept4 -T 2>&1 | head -20
```

**Fix:**
1. Increase backlog: `listen(sock, 4096)` (increase to
   `net.core.somaxconn` limit)
2. `sysctl net.core.somaxconn=4096` (OS max backlog)
3. Faster `accept()` processing (separate accept thread
   from worker threads)
4. Scale horizontally (more server processes/pods)

---

### 🔗 Related Keywords

**Prerequisites:**
- `Port Number` - bind/listen/connect use port numbers
- `TCP` - socket programming abstracts TCP

**Builds On This:**
- `Build a TCP Client-Server (Phase 2)` - hands-on lab
- `Connection Pooling` - pool of pre-created sockets

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SOCKET       │ File descriptor = one endpoint of a conn  │
├──────────────┼───────────────────────────────────────────┤
│ SERVER       │ socket→bind→listen→accept→recv→send→close │
├──────────────┼───────────────────────────────────────────┤
│ CLIENT       │ socket→connect→send→recv→close            │
├──────────────┼───────────────────────────────────────────┤
│ MUST-SET     │ SO_REUSEADDR before bind (avoid EADDRINUSE│
│              │ TCP_NODELAY for real-time (disable Nagle) │
│              │ SO_KEEPALIVE for detecting dead connections│
├──────────────┼───────────────────────────────────────────┤
│ recv() TRAP  │ recv() returns partial data. TCP is byte  │
│              │ stream. ALWAYS implement message framing. │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ send() not checked for partial send.      │
│              │ recv() without message framing.           │
│              │ No timeout on connect() (hangs 75s).     │
├──────────────┼───────────────────────────────────────────┤
│ SCALE        │ One thread per connection → C10K problem  │
│              │ Solution: epoll + non-blocking sockets    │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"A socket is a file descriptor representing one endpoint
of a network connection. Server lifecycle: socket() →
bind() → listen() → accept() (returns NEW socket per
connection) → recv()/send() → close(). Client: socket() →
connect() → send()/recv() → close(). Critical socket
options: SO_REUSEADDR before bind (allows reuse of TIME_WAIT
ports), TCP_NODELAY for real-time apps, SO_KEEPALIVE to
detect dead connections. The most common socket programming
bug: assuming recv() returns a complete message - TCP is
a byte stream with no message boundaries. Always implement
length-prefix or delimiter framing."