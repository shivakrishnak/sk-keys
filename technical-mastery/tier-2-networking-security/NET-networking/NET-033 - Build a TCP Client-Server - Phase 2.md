---
id: NET-033
title: "Build a TCP Client-Server - Phase 2"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-019, NET-029
used_by: NET-075
related: NET-019, NET-029, NET-049
tags:
  - networking
  - hands-on
  - lab
  - tcp
  - sockets
  - python
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/net/build-tcp-client-server-phase-2/
---

**⚡ TL;DR** - A hands-on lab building a TCP echo server
and client from scratch, then capturing the connection
with tcpdump to observe the 3-way handshake, data
transfer, and FIN teardown at the packet level. Builds
muscle memory for socket programming patterns and directly
connects code to the TCP concepts you've read about.

| #033 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Your First Network Lab (Phase 1), Socket Programming Basics | |
| **Used by:** | Build a Secure Network Platform (Phase 3) | |
| **Related:** | Your First Network Lab (Phase 1), Socket Programming Basics, Wireshark and tcpdump | |

---

### 🔥 The Problem This Solves

Reading about TCP, sockets, and the 3-way handshake
creates theoretical knowledge. Building a working TCP
server and capturing its packets creates intuition. After
this lab you will have seen a SYN, SYN-ACK, and ACK in
your own tcpdump output - triggered by your own code.
The abstract becomes concrete.

---

### 📘 Lab Overview

This lab has 8 progressive exercises:

1. Basic echo server (one connection at a time)
2. Multi-client echo server (threading)
3. Length-prefix message framing
4. Capture the 3-way handshake with tcpdump
5. Observe FIN/ACK teardown
6. Simulate connection refused and timeout
7. Add connection keepalive detection
8. Load test with multiple concurrent clients

**Prerequisites:**
- Python 3.6+ (or Java/Go equivalents)
- `sudo` access for tcpdump
- Phase 1 lab tools (`ss`, `ip`, `nc`) available
- Optional: Wireshark (GUI version of tcpdump)

---

### ⚙️ Exercise 1: The Minimal Echo Server

```python
# echo_server.py - handles ONE client at a time
import socket

def main():
    server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9000))
    server.listen(5)
    print("Echo server listening on :9000")

    while True:
        conn, addr = server.accept()
        print(f"Connected: {addr}")
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    print(f"Client {addr} disconnected")
                    break
                print(f"Received: {data!r}")
                conn.sendall(data)  # echo back
        finally:
            conn.close()

if __name__ == '__main__':
    main()
```

**Test it:**
```bash
# Terminal 1: start server
python echo_server.py

# Terminal 2: connect with nc (netcat)
nc localhost 9000
# Type anything and press Enter → it echoes back

# Or with Python:
echo "Hello TCP!" | nc localhost 9000
```

**What you observe:**
- Server prints "Connected: ('127.0.0.1', PORT)"
- Server prints what you sent
- Ctrl+D (EOF) → server prints "disconnected"
- `ss -lntp | grep 9000` shows server listening

---

### ⚙️ Exercise 2: Multi-Client Server with Threads

```python
# echo_server_threaded.py
import socket
import threading

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            conn.sendall(data)
    except ConnectionResetError:
        pass
    finally:
        conn.close()
        print(f"[-] Disconnected: {addr}")

def main():
    server = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9000))
    server.listen(128)
    print("Multi-client echo server on :9000")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )
        thread.start()
        active = threading.active_count() - 1
        print(f"Active connections: {active}")

if __name__ == '__main__':
    main()
```

**Test with multiple clients:**
```bash
# Open 3 terminals, each running:
nc localhost 9000

# All can type simultaneously - all get echoed back
# Check active connections:
ss -tnp | grep 9000
```

---

### ⚙️ Exercise 3: Message Framing (Length-Prefix)

**Why this matters:** TCP is a byte stream. Without framing,
you cannot tell where one message ends and the next begins.

```python
# framed_protocol.py
import struct

def recv_exact(sock, n):
    """Read exactly n bytes from socket."""
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed")
        buf += chunk
    return buf

def send_message(sock, message: bytes):
    """Send message with 4-byte big-endian length prefix."""
    length = struct.pack('>I', len(message))
    sock.sendall(length + message)

def recv_message(sock):
    """Receive a length-prefixed message."""
    raw_len = recv_exact(sock, 4)
    msg_len = struct.unpack('>I', raw_len)[0]
    return recv_exact(sock, msg_len)
```

```python
# framed_client.py
import socket
from framed_protocol import send_message, recv_message

def main():
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 9001))

    for msg in [b"Hello", b"World", b"A" * 1000]:
        send_message(sock, msg)
        response = recv_message(sock)
        assert response == msg, "Echo mismatch!"
        print(f"OK: {len(msg)} bytes round-trip")

    sock.close()
```

**Run:**
```bash
python framed_server.py &
python framed_client.py
# OK: 5 bytes round-trip
# OK: 5 bytes round-trip
# OK: 1000 bytes round-trip
```

---

### ⚙️ Exercise 4: Capture the 3-Way Handshake

```bash
# Terminal 1: capture BEFORE connecting
sudo tcpdump -i lo -n -tt "port 9000 and tcp" -v

# Terminal 2: server running
python echo_server.py

# Terminal 3: connect and disconnect
python -c "
import socket, time
s = socket.socket()
s.connect(('127.0.0.1', 9000))
time.sleep(0.1)
s.sendall(b'Hello')
time.sleep(0.1)
data = s.recv(100)
print('Got:', data)
s.close()
"

# In tcpdump look for:
# Flags [S]    ← SYN  (client → server)
# Flags [S.]   ← SYN-ACK (server → client)
# Flags [.]    ← ACK  (client → server)
# Flags [P.]   ← PSH+ACK with data
# Flags [F.]   ← FIN  (teardown begins)
```

**Record:**
- Client source port
- Initial sequence numbers (ISN) for each direction
- RTT from SYN to SYN-ACK (timestamp difference)
- TCP options in SYN packet (MSS, SACK_OK, window scale)

---

### ⚙️ Exercise 5: Observe FIN Teardown and TIME_WAIT

```bash
# After the connection from Exercise 4 closes:

# Check for TIME_WAIT
ss -tn state time-wait | grep 9000

# Watch TIME_WAIT count over 60 seconds
watch -n 5 "ss -tn state time-wait | grep 9000 | wc -l"
# Count decreases as 60-second TIME_WAIT expires

# tcpdump shows 4-way FIN close:
# [F.] → [.] → [F.] → [.]
# Then client enters TIME_WAIT (no more packets)
```

---

### ⚙️ Exercise 6: Simulate Failure Scenarios

**Connection Refused (server not running):**
```bash
pkill -f echo_server.py   # stop server
time nc localhost 9000
# "Connection refused" instantly
# real 0m0.002s   ← immediate RST from OS
```

**Connection Timeout (no response from firewall DROP):**
```bash
# Capture retransmits during timeout
sudo tcpdump -i lo -n "port 9999" -tt &

time nc -w 5 127.0.0.1 9999
# real 0m5.000s  ← waited for specified timeout

# Without -w: TCP retransmits at 1s, 2s, 4s, 8s, 16s...
# ~75 seconds total before ETIMEDOUT
```

---

### ⚙️ Exercise 7: Dead Connection Detection (Keepalive)

```python
# server_with_keepalive.py
import socket

def handle_client_with_keepalive(conn, addr):
    # Enable TCP keepalive probes
    conn.setsockopt(
        socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    # First probe after 10 seconds idle
    conn.setsockopt(
        socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
    # Probe every 5 seconds
    conn.setsockopt(
        socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
    # Declare dead after 3 failed probes
    conn.setsockopt(
        socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
    # 10 + 3×5 = 25 seconds to detect dead client

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                print(f"{addr}: clean disconnect (FIN)")
                break
            conn.sendall(data)
    except ConnectionResetError:
        print(f"{addr}: dead connection detected")
    finally:
        conn.close()
```

**Test dead connection:**
```bash
# Connect a client, then kill it hard (SIGKILL, no FIN)
nc localhost 9000 &
NC_PID=$!
kill -9 $NC_PID   # hard kill, no FIN sent

# Wait ~25 seconds. Server should detect the dead connection.
```

---

### ⚙️ Exercise 8: Load Test

```python
# load_test.py
import socket, threading, time

def client_worker(client_id, messages=50):
    try:
        s = socket.socket()
        s.settimeout(5.0)
        s.connect(('127.0.0.1', 9000))
        for i in range(messages):
            msg = f"c{client_id}m{i}".encode()
            s.sendall(msg)
            resp = s.recv(4096)
            assert resp == msg
        s.close()
        return True
    except Exception as e:
        print(f"Client {client_id}: {e}")
        return False

def main(n=50):
    start = time.time()
    threads = [
        threading.Thread(target=client_worker, args=(i,))
        for i in range(n)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start
    total_msgs = n * 50
    print(f"{n} clients, {total_msgs} messages "
          f"in {elapsed:.2f}s = "
          f"{total_msgs/elapsed:.0f} msg/s")

if __name__ == '__main__':
    main(n=50)
```

```bash
# Monitor while running:
python load_test.py &
watch -n 0.2 \
  "ss -tn | grep 9000 | awk '{print \$1}' | sort | uniq -c"
```

---

### ⚙️ Lab Summary

```
┌──────────────────────────────────────────────────────────┐
│  Phase 2 Lab - Competencies Acquired                     │
├───────────────────────┬──────────────────────────────────┤
│  Exercise             │  Skill                           │
├───────────────────────┼──────────────────────────────────┤
│  1. Echo server       │  Socket API lifecycle            │
│  2. Multi-client      │  Thread-per-connection pattern   │
│  3. Message framing   │  Length-prefix protocol design   │
│  4. Capture handshake │  SYN/SYN-ACK/ACK in real packets │
│  5. FIN teardown      │  4-way close + TIME_WAIT         │
│  6. Failure modes     │  RST vs timeout diagnosis        │
│  7. Keepalive         │  Dead connection detection       │
│  8. Load test         │  Thread-per-conn scaling limits  │
└───────────────────────┴──────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The threaded server creates 1 thread per connection.
With 1000 clients, that's 1000 threads × ~1MB stack = 1GB
RAM for stacks alone. What would happen at 10,000 concurrent
connections? How does nginx handle 10,000+ connections with
just 4 worker threads? What system call is the core of
this approach?

*Hint: epoll (Linux). Non-blocking sockets + event loop.
NET-057 (epoll and io_uring) covers this in depth.*

**Q2.** In Exercise 4 you captured TCP options in the SYN.
If window scaling was NOT negotiated, what is the maximum
TCP window size? On a 100ms RTT link with unlimited
bandwidth, what is the maximum achievable throughput?

*Hint: Max window without scaling = 64KB. Max throughput
= 64KB / 0.1s = 640 Kbps - worse than a 2003 DSL line,
regardless of actual link bandwidth.*

**Q3.** [Challenge] Add a "stats" command to the framed
server: `{"op": "stats"}` returns
`{"clients_served": N, "messages_processed": N}`.
Make the counters thread-safe. This is the foundation
of how Redis INFO, PostgreSQL pg_stat_activity, and
Kafka JMX metrics work - a built-in stats endpoint
directly in the protocol.