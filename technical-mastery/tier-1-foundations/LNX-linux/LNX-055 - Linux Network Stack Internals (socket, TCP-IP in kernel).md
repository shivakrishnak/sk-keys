---
id: LNX-055
title: "Linux Network Stack Internals (socket, TCP/IP in kernel)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-026, LNX-027
used_by: LNX-056, LNX-084, LNX-085
related: LNX-056, LNX-072, LNX-084
tags: [network-stack, socket, sk_buff, NAPI, zero-copy, sendfile, TCP-kernel, BSD-socket, GSO, GRO]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 55
permalink: /technical-mastery/lnx/linux-network-stack-internals/
---

## TL;DR

The Linux kernel implements TCP/IP in layers: BSD socket API (userspace
`socket()`, `send()`, `recv()`) -> VFS layer -> socket layer -> TCP/IP
protocol stack -> network device layer -> NIC driver. Core data structure:
`sk_buff` (socket buffer / skb), a single memory region that packets travel
through with headers prepended/stripped at each layer. Performance: NAPI
(interrupt batching), zero-copy `sendfile()`, GSO/GRO (offload segmentation
to hardware). Tuning: `net.core.rmem_max`, `net.core.wmem_max` for socket
buffer sizes. Diagnosis: `ss -s`, `netstat -s`, `ethtool -S` for counters.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-055 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | network stack, sk_buff, socket, NAPI, zero-copy, sendfile, GSO, GRO, BSD socket |
| **Prerequisites** | LNX-026 (networking basics), LNX-027 (TCP/IP) |

---

### The Problem This Solves

**Problem 1**: An HTTP server needs to send 1 GB files. Naive approach:
`read()` into userspace buffer, then `write()` to socket. This copies data
twice through userspace. `sendfile()` system call sends directly from
kernel file cache to socket without userspace copy (zero-copy). For large
file serving: 2x throughput improvement, 50% CPU reduction.

**Problem 2**: High-traffic server at 100,000 packets/second. Each packet
fires an interrupt, scheduling the kernel to handle it. At 100K pps: 100K
interrupts/second is catastrophic for CPU. NAPI: first interrupt disables
further interrupts, polls for more packets in a batch, re-enables interrupts
when queue is empty. Result: interrupt overhead amortized across many packets.

---

### Textbook Definition

**BSD Socket API**: The programming interface for network communication:
`socket()` creates a socket descriptor, `bind()` assigns address/port,
`listen()`/`accept()` (TCP server), `connect()` (TCP client), `send()`/
`recv()` transfer data. Implemented as VFS file descriptors - sockets can be
`poll()`ed, `select()`ed, `epoll()`ed, and `close()`d like files.

**sk_buff (socket buffer / skb)**: The kernel's per-packet data structure.
Contains: packet data (in a contiguous or scatter-gather memory region),
metadata (protocol headers' offset pointers: `transport_header`,
`network_header`, `mac_header`), control info (device, timestamp, priority).
Headers are prepended/stripped in-place by moving the `data` pointer.

**net_device**: The kernel abstraction for a network interface (NIC). Bridges
the protocol stack (upper layers) and hardware driver (lower layers). Has
TX/RX queues, statistics, and device operations (open, stop, xmit, etc.).

**NAPI (New API)**: Interrupt mitigation for high-speed networking. On first
packet interrupt: disable NIC interrupt, add device to polling list. `ksoftirqd`
or NET_RX softirq polls the device's receive queue, processing up to `budget`
(default 300) packets per poll. When queue is empty: re-enable interrupts.
Prevents interrupt storms at high packet rates.

---

### Understand It in 30 Seconds

```bash
# === View socket statistics ===
ss -s          # summary: TCP states, UDP, RAW counts
ss -tan        # TCP sockets: state, recv-Q, send-Q, addresses
ss -tnp        # TCP with process info (PID, name)

# Key TCP states in ss output:
# LISTEN: server waiting for connections
# ESTABLISHED: active connection
# TIME_WAIT: TCP 4-way close (waiting for delayed packets)
# CLOSE_WAIT: app has received FIN but hasn't closed yet (app bug!)

# === Socket buffer sizes (current settings) ===
sysctl net.core.rmem_max      # max receiver socket buffer
sysctl net.core.wmem_max      # max sender socket buffer
sysctl net.ipv4.tcp_rmem      # TCP: min, default, max recv buffer
sysctl net.ipv4.tcp_wmem      # TCP: min, default, max send buffer

# Increase for high-throughput:
sysctl -w net.core.rmem_max=134217728      # 128 MB max
sysctl -w net.core.wmem_max=134217728
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"
sysctl -w net.ipv4.tcp_window_scaling=1    # enable window scaling

# === NAPI settings ===
# Check per-device interrupt coalescing:
ethtool -c eth0         # current coalesce settings
ethtool -C eth0 rx-usecs 50  # batch interrupts: wait 50us before firing

# === Check for dropped packets ===
ip -s link show eth0    # RX/TX statistics including drops
ethtool -S eth0 | grep -i drop   # NIC-level drop counters
cat /proc/net/softnet_stat        # per-CPU softnet stats
# Col 1: total frames received
# Col 2: frames dropped (backlog full - increase net.core.netdev_max_backlog)
# Col 3: time squeezed (NAPI budget exceeded without finishing)

# Adjust backlog:
sysctl -w net.core.netdev_max_backlog=5000

# === TCP performance statistics ===
netstat -s | grep -E "retransmit|failed|segments"
ss -tn | awk '{print $1}' | sort | uniq -c | sort -rn  # count by TCP state

# === zero-copy: sendfile() in use ===
# When nginx sends a file, it uses sendfile():
strace -e sendfile64 nginx -t 2>&1 | head -5
# Or check nginx config:
# sendfile on;   (default for nginx - uses kernel's sendfile syscall)

# === GSO/GRO/TSO (offloads) ===
ethtool -k eth0 | grep -E "scatter-gather|tcp-segmentation|generic|large"
# tcp-segmentation-offload: on    <- NIC segments large TCP writes
# generic-segmentation-offload: on  <- kernel software fallback for GSO
# generic-receive-offload: on    <- GRO: coalesce small received packets
```

---

### First Principles

**Packet receive path in Linux kernel:**
```
NIC hardware receives packet
          |
          v
DMA: packet written to ring buffer in kernel memory
  (NIC writes directly to pre-allocated sk_buff memory)
          |
          v
NIC fires hardware interrupt
  (if NAPI: schedules poll, disables interrupt)
          |
          v
NAPI poll / NET_RX softirq:
  sk_buff allocated (if not pre-allocated by NIC driver)
  Packet copied from ring buffer to sk_buff
  NIC driver: calls netif_receive_skb()
          |
          v
Network layer (IP): skb->network_header set
  ip_rcv(): IP header validation, routing decision
  Routes to: local (up the stack) or forward (to output)
          |
          v (local delivery)
Transport layer (TCP): skb->transport_header set
  tcp_v4_rcv(): find socket by (src IP, src port, dst IP, dst port)
  TCP state machine: process ACKs, sequence numbers
  Data: placed in socket receive buffer (sk->sk_receive_queue)
          |
          v
Application calls recv()/read():
  Data copied from kernel socket buffer to userspace buffer
  sk_buff freed
```

**Packet send path:**
```
Application calls send()/write():
  Data copied from userspace to kernel socket send buffer
          |
          v
TCP layer (tcp_sendmsg):
  Segments data into MSS-size pieces
  Adds TCP header, sets sequence numbers
  Calculates checksums
          |
          v
IP layer (ip_output):
  Adds IP header, sets TTL, source address
  Routing lookup: which interface, next hop
          |
          v
GSO (if enabled):
  Large sk_buff divided into MTU-size segments
  (Or TSO: passed whole to NIC, NIC segments in hardware)
          |
          v
net_device: queued to NIC TX ring buffer
NIC driver: kicks hardware to transmit
NIC: DMA reads from ring buffer, sends on wire
          |
          v
ACK received: advance send window, free sent sk_buffs
```

**sk_buff memory layout:**
```
sk_buff metadata struct:
  head -------> +------------------------+
                | headroom               |
  mac_header -> +------------------------+
                | Ethernet header (14B)  |
  network_hdr-> +------------------------+
                | IP header (20B+)       |
  transport_hdr>+------------------------+
                | TCP header (20B+)      |
  data -------> +------------------------+
                | application payload    |
  tail -------> +------------------------+
                | tailroom               |
  end --------> +------------------------+

Headers are "prepended" by moving data pointer backward:
  skb_push(skb, sizeof(iphdr)) moves data back 20 bytes
  memcpy the IP header there
  No data copying of payload needed - just pointer manipulation
```

---

### Thought Experiment

Optimizing a file server with `sendfile()`:

```c
/* BAD: naive file-to-socket copy */
/* Two copies: disk -> kernel buf -> userspace buf -> kernel socket buf */
int fd = open("/var/files/bigfile.dat", O_RDONLY);
char buf[65536];
while ((n = read(fd, buf, sizeof(buf))) > 0) {
    write(socket_fd, buf, n);
    /* DATA PATH: disk -> page cache -> buf (userspace) -> socket buffer */
}
/* CPU cost: 2 copies, 2 context switches per chunk */

/* GOOD: sendfile() - zero copy */
/* One "copy": page cache -> NIC directly (via DMA, no CPU copy) */
off_t offset = 0;
sendfile(socket_fd, fd, &offset, file_size);
/* DATA PATH: disk -> page cache -> NIC DMA (CPU not involved) */
/* NIC reads directly from page cache pages */
/* No userspace buffer allocation needed */

/* Nginx config equivalent: */
/* sendfile on; */
/* tcp_nopush on;  (batch sendfile output with TCP_CORK) */
/* tcp_nodelay on; (for the last segment, disable Nagle) */
```

Shell-level diagnosis:

```bash
# See sendfile in action:
strace -p $(pgrep nginx | head -1) -e sendfile64 2>&1 | head -10
# sendfile64(12, 9, NULL, 1048576) = 1048576

# Verify GSO is helping:
watch -n 1 'ethtool -S eth0 | grep -E "gso|gro|tx_queue|rx_queue"'
# gso_packets: increasing = GSO segmenting large sends
# gro_merged: increasing = GRO coalescing received packets

# Identify NAPI effectiveness:
watch -n 1 'cat /proc/net/softnet_stat | head -4'
# Column 3 (time_squeeze): should be low
# High time_squeeze = NAPI budget too small; try:
sysctl -w net.core.netdev_budget=600      # default 300; try 600
sysctl -w net.core.netdev_budget_usecs=8000  # max time per NAPI poll
```

---

### Mental Model / Analogy

```
Linux network stack = assembly line with multiple stations

Raw materials (packets): arrive at loading dock (NIC)
Assembly line stations:
  Station 1 (NIC driver): unpack delivery, put on conveyor (sk_buff)
  Station 2 (IP layer): check address label, route to right dept
  Station 3 (TCP layer): verify sequence, acknowledge receipt
  Station 4 (Socket): place in your mailbox

NAPI = smart loading dock manager:
  BAD: ring bell for every individual package (interrupt per packet)
  GOOD: disable bell, batch-process 300 packages at once, re-enable bell

sk_buff = the box that travels the whole assembly line
  Each station stamps the box (adds header) or reads it
  Box isn't reprinted at each station - just a new header sticker added
  Moving header pointer backward = adding sticker to front, not reprinting

sendfile = shortcut express delivery:
  Regular: package -> receiving room -> internal courier -> your desk
  sendfile: package -> receiving room -> your desk (direct, no courier)
  (DMA: NIC reads directly from file cache, CPU uninvolved)

Socket buffer = your physical in-box:
  Packets delivered but you haven't read them yet
  Buffer full = you're too slow reading; new deliveries dropped
  CLOSE_WAIT = you got a "we're done" note but haven't cleaned your desk
```

---

### Gradual Depth - Five Levels

**Level 1:**
BSD socket API (`socket`, `bind`, `listen`, `accept`, `connect`, `send`,
`recv`). Key sysctl tuning: `net.core.rmem_max`, `wmem_max` for socket
buffer sizes. `sendfile()` for efficient file serving. `ss -tan` to view
TCP connections. ESTABLISHED, TIME_WAIT, CLOSE_WAIT states and their meaning.

**Level 2:**
NAPI and interrupt coalescing (`ethtool -c`, `-C`). `/proc/net/softnet_stat`
for drop diagnosis. `net.core.netdev_max_backlog` for receive queue depth.
GSO (Generic Segmentation Offload) vs TSO (TCP Segmentation Offload - in NIC
hardware). GRO (Generic Receive Offload): coalesces multiple received packets
into one before passing to IP layer. `ethtool -k eth0` to see enabled offloads.
TCP buffer auto-tuning (`net.ipv4.tcp_moderate_rcvbuf=1`).

**Level 3:**
`sk_buff` structure and lifecycle. Scatter-gather I/O (`sendmsg` with
`iovec`): userspace can pass multiple memory regions; kernel assembles into
one sk_buff avoiding copy. `splice()` for pipe-to-socket zero copy. TCP
segmentation: MSS negotiation during handshake, GSO splitting at output.
Netfilter hooks: where iptables rules are evaluated in the receive/send path.
`SO_REUSEPORT`: multiple processes/threads bind the same port; kernel
distributes connections across them (reduces accept() lock contention).
`SO_ZEROCOPY` (Linux 4.14+): send from userspace memory without kernel copy.

**Level 4:**
XDP (eXpress Data Path): eBPF programs attached to NIC driver, process
packets before sk_buff allocation (before NAPI). Kernel bypass techniques:
DPDK (userspace polling, no kernel involvement), RDMA/RoCE (direct NIC-to-NIC
memory without kernel). io_uring for asynchronous socket I/O without
`epoll`. `AF_XDP` sockets: userspace can receive/send using XDP-bypassed
packets. TCP stack tuning for 10Gbps: MTU 9000 (jumbo frames), BDP
(bandwidth-delay product) matching, BBR congestion control.

**Level 5:**
Kernel network RX scaling: RSS (Receive Side Scaling) - NIC hashes packets
to multiple RX queues, one per CPU core. RPS (Receive Packet Steering) -
software version for NICs without RSS. RFS (Receive Flow Steering) - directs
packets to the CPU running the receiving application (cache affinity). XPS
(Transmit Packet Steering) - binds TX queues to CPUs. BQL (Byte Queue Limits)
- prevents TX queue starvation/bloat. TCP Small Queues (TSQ) - limits per-
socket in-flight data. `SO_TIMESTAMPING` for hardware packet timestamps (PTP,
latency measurement). `MSG_ZEROCOPY` path through the stack.

---

### Code Example

**BAD - common socket programming mistakes:**
```java
// Java: BAD - not tuning socket buffers for high throughput:
ServerSocket serverSocket = new ServerSocket(8080);
// Default buffer sizes (usually 8-16 KB) cause throughput collapse
// for connections > 80ms RTT due to TCP window limiting

// GOOD - set buffer sizes matching BDP:
// BDP = bandwidth * RTT
// 1 Gbps * 100ms = 100 Mbps * 0.1s = 10 MB
ServerSocket serverSocket = new ServerSocket();
serverSocket.setReceiveBufferSize(10 * 1024 * 1024);  // 10 MB
// Also set sysctl net.core.rmem_max >= 10MB or Java setting is silently capped
serverSocket.bind(new InetSocketAddress(8080));
```

**GOOD - zero-copy file transfer in Java via FileChannel.transferTo:**
```java
import java.nio.channels.*;
import java.net.*;
import java.io.*;

// transferTo() maps to sendfile() syscall on Linux
// zero-copy: file data goes from page cache to NIC without userspace copy

public class ZeroCopyServer {
    public void serveFile(SocketChannel client, File file)
            throws IOException {
        try (FileChannel fc = FileChannel.open(file.toPath())) {
            long size = fc.size();
            long sent = 0;
            // transferTo maps to sendfile() on Linux:
            while (sent < size) {
                sent += fc.transferTo(sent, size - sent, client);
            }
        }
        // Equivalent to nginx's "sendfile on;" for Java
    }

    // BAD: read into byte[] then write to socket (2 copies):
    public void serveFileSlow(SocketChannel client, File file)
            throws IOException {
        byte[] buf = new byte[65536];
        try (InputStream fis = new FileInputStream(file)) {
            int n;
            while ((n = fis.read(buf)) != -1) {
                // buf is in userspace - extra copy versus transferTo
                client.write(ByteBuffer.wrap(buf, 0, n));
            }
        }
    }
}
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "sendfile() always outperforms read/write" | sendfile() wins for large files because it avoids userspace copies. For small files already in the page cache with high CPU cost elsewhere, the difference is minimal. sendfile() also cannot do SSL/TLS (data must pass through OpenSSL in userspace). SSL servers (HTTPS) cannot use sendfile() for encrypted content - only for unencrypted content (rare). This is why HTTPS servers can't easily achieve the same file-serving efficiency as HTTP for static files. |
| "Socket buffers are the application-level data buffers" | Socket buffers (`SO_RCVBUF`, `SO_SNDBUF`) are KERNEL memory - in the kernel socket structure, not in application memory. They represent the kernel's queue for unread received data and unsent/unacknowledged sent data. Application-side buffers are separate. Increasing socket buffers helps when the application reads slowly (receiver) or the network has high RTT (sender needs to keep window full). Setting buffer sizes in sysctl is not enough: the actual SO_RCVBUF/SNDBUF per socket must also be set (either via application `setsockopt()` or kernel auto-tuning). |
| "TIME_WAIT connections are bad and should be eliminated" | TIME_WAIT is a protocol correctness mechanism. It ensures late-arriving packets for a closed connection don't corrupt a new connection on the same port tuple. Aggressive elimination via `net.ipv4.tcp_tw_reuse=1` (safe for outbound connections) and `net.ipv4.tcp_fin_timeout` reduction can reduce TIME_WAIT accumulation, but eliminating it entirely risks TCP sequence number collisions. CLOSE_WAIT is worse (app bug - application didn't call close() after receiving FIN). High TIME_WAIT count is usually just a sign of many short-lived connections (HTTP/1.0 style), not an actual problem. |
| "NAPI always reduces latency" | NAPI reduces CPU overhead at high packet rates by batching, but increases LATENCY for individual packets at low rates. With NAPI, the first packet of a new burst waits for the poll cycle to process it, rather than being processed immediately on interrupt. For ultra-low-latency applications (HFT, game servers), interrupt-driven processing (pre-NAPI or busy-polling via `SO_BUSY_POLL`) can give better latency at the cost of higher CPU. For throughput, NAPI wins. |
| "Increasing socket buffer sizes always helps" | Over-buffering can actually hurt latency by enabling bufferbloat: data fills large kernel buffers, causing HOL (head-of-line) blocking. TCP's congestion control works best when buffers are sized to hold approximately one BDP (bandwidth-delay product). Over-sized buffers delay congestion signals, resulting in retransmission storms. For high-latency (WAN) connections: large buffers help. For LAN connections with < 1ms RTT: default buffers are usually fine. |

---

### Failure Modes & Diagnosis

**Packet drops under load - diagnosis:**
```bash
# Step 1: check overall drop counters
ip -s link show eth0
# RX: bytes=... packets=... errors=... dropped=... overruns=...
# Dropped > 0: kernel is dropping at backlog queue

# Step 2: detailed softnet statistics per CPU:
cat /proc/net/softnet_stat
# Format: total dropped squeezed ... throttled
# Column 2 (dropped): backlog queue full - increase:
sysctl -w net.core.netdev_max_backlog=10000

# Step 3: NIC-level drops (RX buffer ring full):
ethtool -S eth0 | grep -i "rx.*drop\|rx.*miss\|rx.*error"
# rx_missed_errors: NIC ring buffer full -> fix: increase ring buffer
ethtool -g eth0         # show current/max ring buffer size
ethtool -G eth0 rx 4096 # increase RX ring buffer (max depends on NIC)

# Step 4: socket receive buffer drops:
netstat -s | grep -i "receive buffer"
# "receive buffer errors" = sk_rcvbuf full (app reading too slowly)
# Fix: increase SO_RCVBUF in application or:
sysctl -w net.core.rmem_max=16777216     # allow up to 16MB per socket
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"

# Step 5: TIME_WAIT exhaustion (busy servers with many short connections):
ss -s | grep TIME-WAIT
# Time-wait: 28000   <- high
sysctl -w net.ipv4.tcp_tw_reuse=1   # allow reusing TIME_WAIT sockets
sysctl -w net.ipv4.ip_local_port_range="1024 65535"  # more source ports
```

---

### Related Keywords

**Foundational:**
LNX-026 (Networking Basics), LNX-027 (TCP/IP)

**Builds on this:**
LNX-056 (iptables/Netfilter), LNX-084 (Network Performance), LNX-085 (XDP)

**Related:**
LNX-072 (cgroups - traffic control integration)

---

### Quick Reference Card

| Concept | Tool / Path |
|---------|------------|
| TCP connection states | `ss -tan` |
| Socket buffer sizes | `sysctl net.ipv4.tcp_rmem` |
| NIC interrupt coalescing | `ethtool -c eth0` |
| Packet drop diagnosis | `/proc/net/softnet_stat`, `ip -s link` |
| NIC offload settings | `ethtool -k eth0` |
| Network statistics | `netstat -s`, `ss -s` |
| Zero-copy file serving | `sendfile()` syscall / nginx sendfile on |

**3 things to remember:**
1. sk_buff is the kernel's packet envelope - travels all stack layers with headers added/removed by moving pointers, not copying data
2. NAPI batches interrupt processing for high packet rates; at low rates it adds latency
3. `sendfile()` = zero-copy for file-to-socket (page cache -> NIC DMA); doesn't work for TLS/SSL

---

### Transferable Wisdom

Stack design patterns appear in: Java NIO (`ByteBuffer`, channels, Selector)
mirrors BSD socket API with non-blocking I/O. Netty's ByteBuf is the
application-level equivalent of sk_buff (reference-counted, pointer-based
slice operations). Cloud load balancers (ALB, NLB) use kernel bypass and
DPDK for multi-million PPS performance. Kafka's zero-copy file serving uses
`sendfile()` via Java's FileChannel.transferTo(). gRPC HTTP/2 multiplexing
avoids connection overhead that creates TIME_WAIT at scale. The principle
of "process data in place with pointer manipulation rather than copying"
appears in every high-performance system.

---

### The Surprising Truth

Linux's `sk_buff` (socket buffer) is one of the most copied pieces of code
in the kernel. The structure and its operations have been ported to nearly
every embedded Linux networking device (routers, switches, IoT gateways).
sk_buff has a peculiar design: the actual data region is SHARED between
multiple sk_buffs via reference counting (`skb_share_check()`). When a
packet is broadcast or multicasted to multiple interfaces, the kernel doesn't
copy the packet data - it creates multiple sk_buff headers all pointing to
the same data buffer. The reference count on the data buffer tracks how many
sk_buffs are using it. Only when a sk_buff needs to MODIFY the data (adding/
changing a header) and the refcount > 1 does the kernel actually copy the
data (`skb_copy()`). This Copy-on-Write for network buffers means multicast
forwarding is nearly free from a memory perspective - the kernel broadcasts
1000 packets using just 1000 sk_buff headers plus 1 shared data buffer. The
same concept (shared immutable data + CoW on modification) powers Kafka's
log segments, Linux's fork(), Redis's snapshot creation, and ZFS/LVM snapshots.

---

### Mastery Checklist

- [ ] Understands the BSD socket API call sequence (socket, bind, listen, accept, connect, send, recv)
- [ ] Can tune socket buffer sizes for high-throughput or high-latency links
- [ ] Understands NAPI and can diagnose packet drops from /proc/net/softnet_stat
- [ ] Understands sendfile() zero-copy and when it applies (not with TLS)
- [ ] Can read `ss -tan` output and diagnose TIME_WAIT vs CLOSE_WAIT issues

---

### Think About This

1. An HTTP file server needs to transfer 10 TB/day at peak load. The
   server uses 100 Gbps NICs. List three kernel-level features (syscalls,
   sysctl parameters, or NIC settings) you would enable or tune, and
   explain why each one matters for this specific workload. Consider:
   copy overhead, interrupt overhead, and buffer sizing.

2. A Java service suddenly shows thousands of CLOSE_WAIT connections but
   very few ESTABLISHED. What is happening in the application code that
   causes CLOSE_WAIT to accumulate? What happens to memory on the server
   as CLOSE_WAIT connections accumulate? How do you fix it?

3. On a 40 Gbps NIC, you see `/proc/net/softnet_stat` column 3 (time_squeeze)
   increasing rapidly. What does this mean, and what are THREE different
   tuning parameters you could adjust to reduce time_squeeze? What trade-off
   does each involve?

---

### Interview Deep-Dive

**Foundational:**
Q: What is the receive path of a TCP packet in the Linux kernel?
A: A TCP packet arrives from the network and travels up the stack: (1) NIC HARDWARE: packet arrives, NIC performs DMA - writes packet data directly into pre-allocated kernel memory (RX ring buffer). Hardware interrupt fires. (2) NIC DRIVER / NAPI: interrupt handler runs, records that a packet is available, schedules NAPI poll, disables further NIC interrupts. NAPI poll (called from NET_RX softirq): allocates sk_buff, calls netif_receive_skb() for each packet, processes up to 'budget' packets. Re-enables NIC interrupt when ring is empty. (3) NETWORK LAYER (IP, ip_rcv): validates IP header, checks destination. If for this host: pass to transport layer. If not: forward (if routing enabled). (4) TRANSPORT LAYER (TCP, tcp_v4_rcv): looks up socket by (src_ip, src_port, dst_ip, dst_port) in connection table. Processes: validates sequence number, generates ACKs, handles congestion control, reassembles out-of-order segments. Places data in socket's receive queue (sk_receive_queue). (5) APPLICATION: calls recv()/read(). Kernel copies data from sk_receive_queue to userspace buffer. sk_buff freed. Key: each layer works on the same sk_buff, just adjusting header pointers - no copying of payload data until userspace delivery.

**Expert:**
Q: Explain GSO, GRO, and TSO and how they improve network performance.
A: All three reduce per-packet overhead by aggregating work: TSO (TCP Segmentation Offload): Applications write large buffers (64KB+) in a single send(). Without TSO, the kernel would segment this into MTU-size packets (1500 bytes each), generating ~44 small sk_buffs. With TSO: kernel creates one large sk_buff and sends it to the NIC. The NIC hardware divides it into MTU-size frames on the wire. Benefit: CPU does only one iteration of the TCP/IP stack for 44 packets worth of data. Requires hardware support. Check: `ethtool -k eth0 | grep tcp-segmentation`. GSO (Generic Segmentation Offload): Software fallback when hardware TSO is unavailable (virtual NICs, Wi-Fi). Kernel delays segmentation until the last possible moment in the transmit path. Until then, works with large sk_buffs (super-packets). Applied just before NIC driver. Available on all interfaces regardless of hardware. GRO (Generic Receive Offload): The receive-side counterpart. At receive time (in NAPI poll), GRO coalesces multiple small incoming TCP segments that belong to the same connection into a single large sk_buff before passing up the stack. Instead of the TCP layer processing 44 individual 1460-byte packets, it processes 1 super-packet. This reduces per-packet overhead: one trip through TCP state machine for many segments. Check: `ethtool -k eth0 | grep generic-receive`. Practical impact: on a 40 Gbps NIC receiving small 1500-byte packets at line rate: without GRO = 3.3 million NAPI callbacks/sec; with GRO = potentially 100K callbacks/sec (30x reduction). The combination of TSO+GSO (send) and GRO (receive) can reduce CPU overhead for network I/O by 60-70% on high-speed links.
