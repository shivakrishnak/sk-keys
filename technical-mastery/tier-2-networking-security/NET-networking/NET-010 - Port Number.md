---
id: NET-010
title: "Port Number"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★☆☆
depends_on: NET-009, NET-008
used_by: NET-020, NET-022, NET-029, NET-035
related: NET-009, NET-014, NET-020
tags:
  - networking
  - foundational
  - transport-layer
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 10
permalink: /technical-mastery/net/port-number/
---

**⚡ TL;DR** - A port number is a 16-bit integer (0-65535)
that identifies a specific process or service on a host.
IP routes packets to the right machine; port numbers route
packets to the right application on that machine.

| #010 | Category: Networking | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | IP Address, TCP/IP Model (Four Layers) | |
| **Used by:** | TCP, TCP Three-Way Handshake, Socket Programming Basics, TCP Connection Lifecycle | |
| **Related:** | IP Address, Packet Structure, TCP | |

---

### 🔥 The Problem This Solves

Without port numbers, a computer could only run one network
service at a time. If two processes need to receive network
data simultaneously - a web server and an SSH daemon - there
would be no way for the OS to know which process to deliver
each incoming packet to. Port numbers solve the delivery
problem: they are the apartment numbers on a building (the
IP address) that ensure the mail (packets) reaches the right
resident (process).

---

### 📘 Textbook Definition

A **port number** is a 16-bit unsigned integer (range 0-65535)
in the TCP and UDP headers that identifies the sending and
receiving application. The combination of IP address and
port number is called a **socket**. A TCP connection is
uniquely identified by the 4-tuple: `(src_ip, src_port,
dst_ip, dst_port)`. The OS uses this 4-tuple to demultiplex
incoming packets to the correct socket and process.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Port numbers extend IP addressing to the process level:
IP reaches the machine, port number reaches the application.

**One analogy:**

> A port number is like an apartment number in a large
> apartment building. The IP address is the building's
> street address (gets the letter to the right building).
> The port number is the apartment number (gets the letter
> to the right resident). Without apartment numbers, the
> building could only have one resident.

**One insight:**
Every TCP connection requires 4 numbers to be unique:
source IP, source port, destination IP, destination port.
This is why a server can handle thousands of simultaneous
connections to the same port 443 (HTTPS): each connection
has a different source IP:port pair. The 4-tuple uniqueness
constraint is the fundamental math behind connection scaling.

---

### 🔩 First Principles Explanation

**Port number ranges:**

```
┌──────────────────────────────────────────────────────────┐
│  Port Number Ranges                                      │
├────────────────────┬─────────────────────────────────────┤
│  Range             │  Name and Usage                     │
├────────────────────┼─────────────────────────────────────┤
│  0 - 1023          │  Well-Known Ports (IANA-assigned)   │
│                    │  Require root/admin to bind          │
│                    │  HTTP:80, HTTPS:443, SSH:22,         │
│                    │  DNS:53, SMTP:25, FTP:21,            │
│                    │  MySQL:3306 is NOT in this range     │
├────────────────────┼─────────────────────────────────────┤
│  1024 - 49151      │  Registered Ports (IANA-registered) │
│                    │  Applications register with IANA    │
│                    │  MySQL:3306, PostgreSQL:5432,        │
│                    │  Redis:6379, Kafka:9092,             │
│                    │  Elasticsearch:9200, MongoDB:27017   │
├────────────────────┼─────────────────────────────────────┤
│  49152 - 65535     │  Ephemeral (Dynamic) Ports          │
│                    │  OS assigns for outbound connections │
│                    │  Client source port for TCP/UDP      │
│                    │  Short-lived, reused after close     │
└────────────────────┴─────────────────────────────────────┘
```

**Well-known ports every SE should know:**

```
┌──────────────────────────────────────────────────────────┐
│  Essential Well-Known and Registered Ports               │
├─────────┬───────────────────────────────────────────────┤
│  Port   │  Service (Protocol)                           │
├─────────┼───────────────────────────────────────────────┤
│  20,21  │  FTP (data + control) - TCP                  │
│  22     │  SSH - TCP                                    │
│  23     │  Telnet - TCP (insecure - avoid)              │
│  25     │  SMTP - TCP (email sending)                   │
│  53     │  DNS - UDP (queries) + TCP (transfers)        │
│  80     │  HTTP - TCP                                   │
│  110    │  POP3 - TCP (email retrieval)                 │
│  143    │  IMAP - TCP (email retrieval)                 │
│  443    │  HTTPS (HTTP over TLS) - TCP                  │
│  465    │  SMTPS (SMTP over TLS) - TCP                  │
│  587    │  SMTP submission - TCP                        │
│  3306   │  MySQL - TCP                                  │
│  5432   │  PostgreSQL - TCP                             │
│  6379   │  Redis - TCP                                  │
│  8080   │  HTTP alternate (dev servers, proxies)        │
│  8443   │  HTTPS alternate                              │
│  9092   │  Apache Kafka - TCP                           │
│  27017  │  MongoDB - TCP                                │
└─────────┴───────────────────────────────────────────────┘
```

**The 4-tuple uniqueness constraint:**

```
┌──────────────────────────────────────────────────────────┐
│  TCP Connection Identification                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Connection 1: client1:50001 → server:443               │
│  Connection 2: client1:50002 → server:443               │
│  Connection 3: client2:50001 → server:443               │
│                                                          │
│  All three are distinct because the 4-tuple:            │
│  (src_ip, src_port, dst_ip, dst_port) differs           │
│                                                          │
│  Max theoretical connections to one server port:        │
│  ~4B (2^32 src IPs) × 65536 (2^16 src ports)           │
│  = ~280 trillion (practical: much less due to           │
│  file descriptor limits and memory)                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP:**
A server is running HTTPS on port 443 and has 1000 active
connections from different clients. What is unique about
each connection?

Each connection has: same destination IP (server), same
destination port (443). What differs: source IP, source
port (ephemeral, OS-assigned). So the 4-tuple is:
`(client_IP_N, ephemeral_port_N, server_IP, 443)`.

**FOLLOW-UP:**
What happens when a client machine has 65535+ connections
to the same server? Source port range is 49152-65535 (about
16,384 ports). If one client needs more than 16,384 simultaneous
connections to the same server, the OS will try to reassign
ports - but a port can only be reused if the old connection
using it is in `CLOSED` or `TIME_WAIT` state. Port exhaustion
(where all 16,384 ephemeral ports are in use) causes new
connection attempts to fail with "Cannot assign requested
address."

**THE INSIGHT:**
Port exhaustion is a real production problem in high-
throughput services. Solutions: increase `ip_local_port_range`,
use `SO_REUSEPORT` to allow multiple sockets on the same
source port with same destination, or use connection pooling
to reduce connection creation rate.

---

### 🧠 Mental Model / Analogy

> A port number is like a radio channel frequency. An IP
> address gets your signal to the right city (machine). A
> port number is the specific channel (frequency) that the
> right receiver is tuned to. If no receiver is tuned to
> that channel, the signal goes unheard (connection refused).
> Multiple different shows (processes) can broadcast on
> different channels simultaneously on the same transmitter
> (machine).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Port numbers let multiple applications on one computer all
use the network simultaneously. Each application listens on
a different port number.

**Level 2 - How to use it (junior developer):**
When you start a web server with `listen(8080)`, it "binds"
to port 8080 on all interfaces. Clients connect to
`host:8080`. If you forget to open port 8080 in the firewall,
clients see "Connection refused." Use `ss -lntp` or
`netstat -tlnp` to see what ports your server is listening on.

**Level 3 - How it works (mid-level engineer):**
When a client `connect()` call is made without binding a
source port, the OS kernel assigns an ephemeral port from
`/proc/sys/net/ipv4/ip_local_port_range` (typically
`32768-60999` on Linux). The kernel ensures this source port
is not already used in an active connection to the same
destination. After the connection closes, the source port
goes through `TIME_WAIT` (60 seconds default) before being
reused.

**Level 4 - Why it was designed this way (senior/staff):**
The port number is the TCP/UDP demultiplexing key. The
alternative - using process IDs - was rejected because PIDs
are local to a machine and restart between processes.
Well-known ports (< 1024) requiring root to bind is a
security design from UNIX: it ensures only privileged
processes can claim to be SSH (port 22) or HTTP (port 80).
On modern Linux, the `CAP_NET_BIND_SERVICE` capability
allows a non-root process to bind to low ports without
full root privileges.

**Level 5 - Mastery (distinguished engineer):**
`SO_REUSEPORT` (Linux 3.9+) allows multiple sockets
to bind to the same port simultaneously. The kernel
distributes incoming connections across all listening
sockets using a hash of the 4-tuple. This enables zero-
downtime restarts: start a new process binding to the same
port, then gracefully shut down the old process. The new
process starts receiving new connections while the old
finishes handling existing ones. Nginx and HAProxy use
this pattern. Without `SO_REUSEPORT`, you'd need a
coordinator process (master-worker) to handle socket
inheritance, which is the older pattern.

---

### ⚙️ How It Works (Mechanism)

**Port location in TCP header:**

```
┌──────────────────────────────────────────────────┐
│  TCP Header (first 8 bytes)                      │
├──────────────────────────────────────────────────┤
│  Bits 0-15:  Source Port      (16 bits)          │
│  Bits 16-31: Destination Port (16 bits)          │
│  Bits 32-63: Sequence Number  (32 bits)          │
│  Bits 64-95: Acknowledgment   (32 bits)          │
│  ...                                             │
└──────────────────────────────────────────────────┘
```

**Diagnosing port issues:**

```bash
# See all listening ports (TCP and UDP)
ss -lntp
# -l = listening, -n = numeric, -t = TCP, -p = process

# Example output:
# State  Recv-Q  Send-Q  Local Address:Port
# LISTEN 0       128     0.0.0.0:22        ← SSH
# LISTEN 0       511     0.0.0.0:80        ← HTTP
# LISTEN 0       511     0.0.0.0:443       ← HTTPS
# LISTEN 0       128     127.0.0.1:5432    ← Postgres (local only)

# Test if a port is open
nc -zv target_host 443
# -z = scan mode, -v = verbose
# Connection to target_host 443 port [tcp/https]: OK

# Test with timeout
nc -zv -w 3 target_host 443
# -w 3 = 3 second timeout

# Check ephemeral port range
cat /proc/sys/net/ipv4/ip_local_port_range
# 32768   60999  (28,231 available ephemeral ports)

# Count established connections per destination port
ss -tn | awk '{print $5}' | cut -d: -f2 | \
  sort | uniq -c | sort -rn | head -10
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Connection setup with port numbers:**

1. Server: `bind(sock, 0.0.0.0:443)` - reserve port 443
2. Server: `listen(sock, 128)` - mark socket as passive
3. Client: `connect(server_ip, 443)` - OS assigns src port
   (e.g., 50234). SYN sent: `src=client:50234, dst=server:443`
4. Server: `accept()` - new socket for this connection
   identified by 4-tuple `(client_IP, 50234, server_IP, 443)`
5. Server: handles request on new socket while still
   `listen()`-ing on port 443 for more connections

**PORT REUSE AND TIME_WAIT:**
After a TCP connection closes, the 4-tuple cannot be reused
for 2*MSL (Maximum Segment Lifetime = 60 seconds default).
This prevents delayed packets from a previous connection
being delivered to a new connection with the same 4-tuple.
A busy server closing many connections creates many sockets
in `TIME_WAIT`. This is normal - but if source ports run out
waiting for `TIME_WAIT` to expire, new connections fail.

**WHAT CHANGES AT SCALE:**
At 100,000 connections/second, port exhaustion becomes real.
Solutions in production:
- Multiple source IPs (multiplies available port space)
- `tcp_tw_reuse` sysctl: reuse `TIME_WAIT` sockets for
  outbound connections with `SO_REUSEADDR`
- `tcp_fin_timeout` reduction: reduce `TIME_WAIT` duration
- Connection pooling: avoid per-request TCP connections

---

### ⚖️ Comparison Table

| Aspect | TCP | UDP |
|---|---|---|
| **Port usage** | Source + destination port in header | Source + destination port in header |
| **Port binding** | `bind()` required before `listen()` | `bind()` required; no `listen()` |
| **Ephemeral ports** | OS assigns for outbound | OS assigns for outbound |
| **Port conflicts** | Two processes cannot bind same port (without SO_REUSEPORT) | Same |
| **Port 0 special** | Bind to port 0 = OS picks any available | Same |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Port numbers are limited to 65535 total concurrent | A single server can have millions of concurrent connections on port 443. The 65535 limit is per 4-tuple, not per machine. A machine can have 65535 concurrent connections TO a specific server, but can accept 65535 × (number of client IPs) connections FROM clients. |
| Firewall "opening a port" allows any traffic | A firewall rule for port 80 TCP allows TCP port 80. It says nothing about UDP port 80. You must specify protocol (TCP/UDP/ICMP) separately. |
| A process must restart to change its port | `SO_REUSEPORT` allows multiple processes to bind the same port. Old process closes; new process starts. Both overlap for zero-downtime. |
| Ports above 1024 are "safe" to use for anything | Registered ports (1024-49151) are IANA-registered. Binding to 3306 (MySQL) without running MySQL is asking for confusion. Always check IANA registry before picking a port. |

---

### 🚨 Failure Modes & Diagnosis

**Port Already in Use - "Address already in use"**

**Symptom:**
```
Error: listen EADDRINUSE: address already in use :::8080
```
or
```
bind: Address already in use
```

**Root Cause:** Another process is already bound to port
8080. OR a previous process just crashed and its socket
is in `TIME_WAIT`. OR `SO_REUSEADDR` is not set.

**Diagnostic Command / Tool:**
```bash
# Find what's using port 8080
ss -lntp | grep :8080
# or
lsof -i :8080
# or
fuser -n tcp 8080

# See if it's TIME_WAIT (already closing)
ss -tn | grep :8080
# If all are TIME_WAIT, wait 60s or:
# Add SO_REUSEADDR to your server socket code
```

**Fix:**
```python
# BAD: no SO_REUSEADDR (crashes on restart)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8080))

# GOOD: always set SO_REUSEADDR before bind
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(
    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
)
sock.bind(('0.0.0.0', 8080))
```

**Prevention:** Always set `SO_REUSEADDR` before `bind()`.
It allows binding to a port that has sockets in `TIME_WAIT`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `IP Address` - the other half of the socket address
- `TCP/IP Model (Four Layers)` - the layer where ports live

**Builds On This (learn these next):**
- `TCP (Transmission Control Protocol)` - how TCP uses ports
  for connection multiplexing
- `Socket Programming Basics` - how applications bind to and
  connect to ports
- `TCP Connection Lifecycle and States` - TIME_WAIT and how
  it relates to port reuse

**Alternatives / Comparisons:**
- `TCP Three-Way Handshake` - the port negotiation process
  during connection establishment

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 16-bit int (0-65535) identifying a        │
│              │ process; extends IP to the application    │
├──────────────┼───────────────────────────────────────────┤
│ KEY RANGES   │ 0-1023: Well-known (root to bind)         │
│              │ 1024-49151: Registered (apps)             │
│              │ 49152-65535: Ephemeral (client src)       │
├──────────────┼───────────────────────────────────────────┤
│ KEY PORTS    │ 22=SSH, 53=DNS, 80=HTTP, 443=HTTPS,       │
│              │ 3306=MySQL, 5432=PG, 6379=Redis           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ TCP connection = 4-tuple unique.          │
│              │ Server can have millions of connections   │
│              │ all to port 443 with different src ports. │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSTIC   │ ss -lntp (listening), nc -zv host port    │
│              │ (test), lsof -i :PORT (who uses it)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ SO_REUSEPORT: enables multi-process bind  │
│              │ on same port (zero-downtime restarts)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "IP delivers to the machine;              │
│              │  port delivers to the application."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ TCP → TCP Three-Way Handshake →           │
│              │ Socket Programming                        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Well-known ports (0-1023) require root. Common: SSH=22,
   DNS=53, HTTP=80, HTTPS=443. Client source ports are
   ephemeral (49152-65535 range).
2. A TCP connection is identified by 4 values: src_IP,
   src_port, dst_IP, dst_port. All four must be unique for
   each simultaneous connection.
3. `SO_REUSEADDR` before `bind()` prevents "Address already
   in use" on server restart. Always set it in server code.

**Interview one-liner:**
"Port numbers are 16-bit integers (0-65535) in the TCP/UDP
header that identify the receiving application on a host.
IP addresses get packets to the right machine; ports get
packets to the right process. A TCP connection is uniquely
identified by 4 values: source IP, source port, destination
IP, destination port - allowing a server to handle millions
of simultaneous connections all to port 443. Ports 0-1023
are well-known and require root to bind. The OS assigns
ephemeral ports (49152-65535) for client outbound connections."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Multiplexing multiple logical streams over a single
physical channel requires a demultiplexing key. Port
numbers ARE that key for TCP/UDP. The same pattern appears
in: HTTP/2 stream IDs (multiplex multiple requests over
one TCP connection), QUIC connection IDs (multiplex
streams over UDP), gRPC stream IDs, SSH channel IDs.
Every time you see multiple logical flows on one connection,
there is an ID field acting as the demultiplexing key.

**Where else this pattern appears:**
- **Hardware interrupts** - interrupt numbers are "ports"
  for hardware devices: NIC interrupt vs keyboard interrupt
  vs disk interrupt.
- **UNIX file descriptors** - each process gets an integer
  fd table; `fd=3` identifies a specific file just as
  port 443 identifies HTTPS.

---

### 💡 The Surprising Truth

Port numbers below 1024 requiring root is a security
model that dates from 1981 UNIX - long before containers,
namespaces, or Linux capabilities existed. Today, in
a Docker container running as a non-root user, your app
cannot bind to port 80 without either adding
`CAP_NET_BIND_SERVICE` capability or using a non-privileged
port (8080) and having a reverse proxy on port 80. This
is why every production containerized app runs on port
8080 (or 3000, 5000) internally and has an Nginx/HAProxy
on port 80/443 in front of it. The 40-year-old UNIX
security model shapes every containerized application's
network architecture today.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN** the three port ranges (well-known, registered,
   ephemeral) and why each has different access requirements.
2. **DEBUG** "Address already in use" errors using `ss`,
   `lsof`, or `fuser` to identify the process occupying a port.
3. **DECIDE** whether `SO_REUSEADDR` or `SO_REUSEPORT` is
   needed for your use case (server restart vs multi-process
   load distribution).
4. **BUILD** a mental model of the 4-tuple uniqueness
   constraint and calculate maximum theoretical concurrent
   connections from one client to one server.
5. **EXTEND** the port number concept to explain HTTP/2
   stream IDs and why they serve the same demultiplexing
   purpose within one TCP connection.

---

### 🧠 Think About This Before We Continue

**Q1.** A load balancer receives a connection from client
`203.0.113.5:52341` destined for `10.0.0.1:443`. It
forwards to backend `10.0.1.5:8080`. The backend sees
source IP `10.0.0.1:54200` (the load balancer's IP).
How many 4-tuples are involved? Draw the full picture.
What happens to the original client source port?

*Hint: Layer 4 (TCP) load balancers create a new TCP
connection to the backend. The original 4-tuple terminates
at the LB. A new 4-tuple begins from LB to backend.*

**Q2.** You are writing a TCP server that must handle
100,000 simultaneous connections. Linux's default listen
backlog is 128. What does this mean and why is it not the
limiting factor for 100K connections? What ARE the actual
limits? (Hint: file descriptors, memory, ephemeral ports)

*Hint: Listen backlog = max unaccepted connections queued.
After `accept()`, connections live in the fd table. Default
fd limit per process is 1024 (ulimit -n). 100K connections
need `ulimit -n 100001`.*

**Q3.** [Hands-On] On a Linux machine, run
`ss -tn | awk '{print $5}' | grep -oP ':\K\d+' | sort -n |
uniq -c | sort -rn | head -5`. This shows the top 5 most-
connected destination ports on your machine. Which ports
appear? Can you identify what service each one is? Bonus:
compare `ss -tn state established | wc -l` with
`ss -tn state time-wait | wc -l`. Are more connections
established or in TIME_WAIT?