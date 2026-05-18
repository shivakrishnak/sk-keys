---
id: LNX-091
title: "tc (Traffic Control) and qdisc (Linux networking)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-037, LNX-084
used_by: LNX-085, LNX-092
related: LNX-037, LNX-084, LNX-085, LNX-092
tags: [tc, traffic-control, qdisc, netem, tbf, htb, fq-codel, police, filter, classful-qdisc, classless-qdisc, bandwidth-shaping, rate-limiting, latency-emulation, packet-loss-simulation, tc-actions, tc-filter, ip-tc, network-emulation, shaping]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 91
permalink: /technical-mastery/lnx/tc-traffic-control-qdisc/
---

## TL;DR

`tc` (traffic control) is the Linux command for managing network queueing
disciplines (qdiscs). Use cases: (1) **Testing**: simulate network conditions
with `netem` (add latency, packet loss, duplication, reordering):
`tc qdisc add dev eth0 root netem delay 100ms loss 5%`; (2) **Rate limiting**:
`tbf` (Token Bucket Filter) or `htb` (Hierarchical Token Bucket) to limit
bandwidth per flow/host; (3) **Fair queuing**: `fq_codel` (default in many
distros) reduces bufferbloat via active queue management. Key commands:
`tc qdisc show dev eth0` (view), `tc qdisc del dev eth0 root` (remove),
`tc -s qdisc show` (with stats/drops). `netem` for CI/CD network chaos testing.
`htb` for per-customer rate limiting (ISP/cloud use). `fq` for BBR pacing.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-091 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | tc, qdisc, netem, HTB, TBF, fq_codel, rate limiting, bandwidth shaping, network emulation, packet loss simulation |
| **Prerequisites** | LNX-037 (Networking), LNX-084 (Network performance) |

---

### The Problem This Solves

**Problem 1**: Developers write code that works perfectly in a LAN environment
(< 1ms RTT) but breaks mysteriously when users on mobile connections (100ms
RTT, 2% packet loss) use it. Without tools: deploy to staging, wait for
real-world users to report issues. With `netem`: `tc qdisc add dev eth0
root netem delay 100ms 20ms loss 2%` - simulate mobile network conditions
on the developer's machine instantly. Protocol timeouts, retry logic, and
connection handling are now testable in development.

**Problem 2**: A cloud provider needs to enforce 10 Mbps bandwidth limit
per customer, even if the customer's VM tries to use more. Without tc: all
VMs compete for full NIC bandwidth (noisy neighbor problem). With HTB qdisc:
per-VM class hierarchy, each customer class capped at their purchased rate.
Customers cannot burst above their paid tier.

---

### Textbook Definition

**Traffic Control (tc)**: The Linux subsystem for managing how packets are
queued, scheduled, and sent on network interfaces. Controlled via the `tc`
command (part of iproute2).

**Queueing discipline (qdisc)**: An algorithm that determines how packets
are enqueued and dequeued from a network interface's output queue. Two types:

**Classless qdiscs** (simple, single queue):
| qdisc | Purpose |
|-------|---------|
| `pfifo_fast` | Priority FIFO (old default) |
| `fq_codel` | Fair Queuing + CoDel AQM (new default) |
| `fq` | Fair Queuing (used with BBR) |
| `tbf` | Token Bucket Filter (simple rate limit) |
| `netem` | Network Emulator (testing) |
| `prio` | Priority bands |

**Classful qdiscs** (hierarchical, multiple queues):
| qdisc | Purpose |
|-------|---------|
| `htb` | Hierarchical Token Bucket (complex rate limiting with classes) |
| `hfsc` | Hierarchical Fair Service Curve (precise latency guarantees) |
| `cbq` | Class-Based Queueing (older, complex) |

**Filter**: Classifies packets to classes (for classful qdiscs).
**Police**: Drops or marks excess packets.

---

### Understand It in 30 Seconds

```bash
# === netem: network emulation for testing ===

# Add 100ms latency with 20ms jitter to eth0:
tc qdisc add dev eth0 root netem delay 100ms 20ms
# (100ms +/- 20ms, normally distributed)

# Add 5% random packet loss:
tc qdisc add dev eth0 root netem loss 5%

# Combined: 100ms delay + 20ms jitter + 2% loss:
tc qdisc add dev eth0 root netem \
    delay 100ms 20ms distribution normal \
    loss 2% \
    duplicate 0.1% \
    corrupt 0.05%
# Tests: retry logic, timeout handling, packet ordering

# Add reordering (25% of packets arrive out of order):
tc qdisc add dev eth0 root netem delay 100ms reorder 25% 50%

# Remove netem (restore normal operation):
tc qdisc del dev eth0 root

# === View current qdiscs ===

# Show all qdiscs:
tc qdisc show
# qdisc noqueue 0: dev lo root refcnt 2
# qdisc fq_codel 0: dev eth0 root refcnt 2 limit 10240p flows 1024
#   quantum 1514 target 5ms interval 100ms memory_limit 32Mb ecn
#   drop_batch 64

# Show with statistics (drops, packets):
tc -s qdisc show dev eth0
# qdisc fq_codel 0: dev eth0 root refcnt 2 limit 10240p flows 1024
#  Sent 1234567 bytes 9876 pkt (dropped 0, overlimits 0 requeues 0)
#  backlog 0b 0p requeues 0
#  maxpacket 1514 drop_overlimit 0 new_flow_count 1234 keep_count 5678

# === tbf: simple rate limiting ===
# Limit eth0 to 10 Mbps with 100KB burst:
tc qdisc add dev eth0 root tbf \
    rate 10mbit \       # 10 Mbps sustained rate
    burst 100kb \       # burst size (must be >= rate/HZ)
    latency 400ms       # max latency before drop (queue size)

# View tbf statistics:
tc -s qdisc show dev eth0
# qdisc tbf ...: Sent X bytes Y pkt (dropped Z, ...) rate 10Mbit

# Replace (modify) existing qdisc:
tc qdisc change dev eth0 root tbf rate 20mbit burst 200kb latency 400ms

# === htb: hierarchical rate limiting ===

# Setup: 100Mbps total, 2 classes: class 1 gets 60Mbps, class 2 gets 40Mbps
# Step 1: Root HTB qdisc:
tc qdisc add dev eth0 root handle 1: htb default 30

# Step 2: Root class (100Mbps total):
tc class add dev eth0 parent 1: classid 1:1 htb rate 100mbit

# Step 3: Child classes:
tc class add dev eth0 parent 1:1 classid 1:10 htb \
    rate 60mbit ceil 100mbit   # class 1: min 60Mbps, can burst to 100Mbps

tc class add dev eth0 parent 1:1 classid 1:20 htb \
    rate 40mbit ceil 100mbit   # class 2: min 40Mbps, can burst to 100Mbps

tc class add dev eth0 parent 1:1 classid 1:30 htb \
    rate 1mbit ceil 100mbit    # default: 1Mbps min (for unclassified)

# Step 4: Filters to assign traffic to classes:
# Class 1 for traffic from 192.168.1.0/24:
tc filter add dev eth0 parent 1: protocol ip u32 \
    match ip src 192.168.1.0/24 flowid 1:10

# Class 2 for everything else (goes to default 1:30):

# View class hierarchy:
tc class show dev eth0
tc -s class show dev eth0  # with statistics

# Clean up all qdisc:
tc qdisc del dev eth0 root

# === fq_codel: active queue management ===
# fq_codel is default on many modern Linux distros
# It reduces bufferbloat by combining:
# - Fair Queuing (FQ): separate queue per flow, round-robin
# - CoDel (Controlled Delay): active queue management, drops if delay > target

# View fq_codel parameters:
tc qdisc show dev eth0
# fq_codel ... target 5ms interval 100ms
# target 5ms: acceptable max queuing delay
# interval 100ms: window for measuring delay

# Configure fq_codel explicitly:
tc qdisc replace dev eth0 root fq_codel \
    limit 10240 \     # max packets in queue
    flows 1024 \      # number of hash buckets (flows)
    target 5ms \      # target queuing delay
    interval 100ms    # interval for CoDel algorithm
```

---

### First Principles

**How qdiscs work in the Linux network stack:**
```
Transmit path:
  Application -> socket buffer
  IP layer -> routing -> packet to interface
  NIC driver: dequeue from qdisc -> put in NIC ring -> DMA to NIC

Queue without qdisc (pfifo):
  Packets arrive -> FIFO queue (first in, first out)
  When queue full: drop (tail drop)
  Problem: large queue + tail drop = bufferbloat
    Short queue: reduce bufferbloat but increase loss under burst
    
  Bufferbloat: queue fills with large latency, old TCP thinks
    queue is infinite - fills it. Then sudden loss at 100% full.
    CoDel (Controlled Delay) fixes this: drop packets when
    queuing delay exceeds target (not when queue is full)

netem (Network Emulator) internals:
  Packet arrives at qdisc:
    1. Apply delay: store packet, schedule release after delay
       Delay distribution: normal, pareto, paretonormal, uniform
    2. Apply loss: random number < loss_rate -> drop
    3. Apply duplication: random number < dup_rate -> enqueue twice
    4. Apply corruption: flip random bit in packet
    5. Apply reordering: swap packet with previous or next
  
  Implementation: per-packet timer (uses high-resolution timers)
  All netem operations are per-packet decisions (independent)

tbf (Token Bucket Filter) internals:
  Bucket: fills at 'rate' (tokens added per second)
  Maximum tokens: 'burst' (burst size)
  Packet arrives:
    If enough tokens: consume tokens, send packet immediately
    If insufficient tokens: wait for tokens to accumulate
    If wait > 'latency': drop packet
  
  Effect: sustained throughput = rate
          short bursts up to 'burst' size allowed
          excess queued up to 'latency' worth
  
  Perfect for: simple egress rate limiting

htb (Hierarchical Token Bucket) internals:
  Class hierarchy:
    Root class: total bandwidth limit
    Child classes: guaranteed (rate) + maximum (ceil)
  
  Bandwidth sharing:
    Each class gets its 'rate' guarantee
    If a class has spare bandwidth: lends to other classes
    No class exceeds its 'ceil'
  
  Example: class A: rate=60Mbps ceil=100Mbps
              class B: rate=40Mbps ceil=100Mbps
    If only A has traffic: A gets 100Mbps (burst to ceil)
    If both have traffic: A gets 60Mbps, B gets 40Mbps (guarantees)
    If A is sending less: B can borrow A's unused bandwidth (up to ceil)

fq_codel internals:
  Fair Queuing (FQ):
    Hash all flows (5-tuple: src/dst IP/port, protocol)
    Each flow has its own queue
    Round-robin across active flow queues
    Prevents one elephant flow from starving mice flows
    
  CoDel (Controlled Delay):
    For each packet in queue: measure sojourn time (time in queue)
    If sojourn > target (5ms) for > interval (100ms): start dropping
    Drop algorithm: interval/sqrt(drop_count) - increasing drop rate
    Effect: queuing delay stays near target, prevents bufferbloat

tc filter types:
  u32 (universal 32-bit): match on arbitrary packet fields (IP, port)
    tc filter add dev eth0 parent 1: protocol ip u32 \
        match ip src 192.168.1.0/24 flowid 1:10
  
  flower: match on L2-L4 fields (supports hardware offload):
    tc filter add dev eth0 root flower \
        ip_proto tcp dst_port 443 action mirred egress redirect dev eth1
  
  bpf: attach eBPF program as classifier:
    tc filter add dev eth0 root bpf obj classifier.bpf.o sec classifier
    (TC BPF: runs before qdisc, can classify and modify packets)
```

---

### Thought Experiment

Building a network test environment with netem:

```bash
# CI/CD: test application behavior under different network conditions
# Requires: two network namespaces connected by veth pair

# Create namespaces:
ip netns add server
ip netns add client

# Create veth pair:
ip link add veth0 type veth peer name veth1

# Assign to namespaces:
ip link set veth0 netns server
ip link set veth1 netns client

# Configure IPs:
ip netns exec server ip addr add 10.0.0.1/24 dev veth0
ip netns exec client ip addr add 10.0.0.2/24 dev veth1
ip netns exec server ip link set veth0 up
ip netns exec client ip link set veth1 up

# Test 1: baseline (no emulation):
ip netns exec client ping -c 5 10.0.0.1
# Round-trip avg: 0.05ms (fast local kernel networking)

# Test 2: simulate 100ms WAN latency:
ip netns exec client tc qdisc add dev veth1 root netem delay 100ms
ip netns exec client ping -c 5 10.0.0.1
# Round-trip avg: 200ms (100ms each way from client)

# Test 3: simulate lossy mobile network:
ip netns exec client tc qdisc replace dev veth1 root netem \
    delay 80ms 30ms loss 3% duplicate 0.1%
# iperf3: test throughput under these conditions

# Test 4: simulate rate-limited broadband (10 Mbps):
ip netns exec client tc qdisc replace dev veth1 root tbf \
    rate 10mbit burst 100kb latency 400ms

# Run your service in server namespace, client in client namespace
# Test: timeouts, retries, streaming performance
ip netns exec server my-service &
ip netns exec client my-client --server 10.0.0.1

# Cleanup:
ip netns exec client tc qdisc del dev veth1 root
ip netns delete server
ip netns delete client
```

---

### Mental Model / Analogy

```
qdisc = factory production line management system

Network interface = factory shipping dock
Packets = boxes waiting to be shipped

pfifo (plain FIFO, old default):
  One conveyor belt, first box loaded = first box shipped
  If conveyor full: new boxes pushed off the end (tail drop)
  Problem: loading dock is always full (bufferbloat)
  Trucks (packets) wait in queue, increasing delivery time

fq_codel (modern default):
  One conveyor belt PER customer (flow queues)
  Round-robin: serve one box from each customer alternately
  Intelligent control: if any box waits > 5ms -> push it off
  (CoDel: controlled delay = SLA enforcement)
  Result: no customer monopolizes the belt, latency controlled

tbf (Token Bucket Filter):
  Truck arrival rate limited by tokens
  Factory receives 10 tokens/second (rate=10Mbps)
  Each box costs tokens proportional to size
  Spare tokens saved (burst=100KB): short rush possible
  No tokens left: box waits (or discarded if waited too long)
  = simple ISP rate limiting: your 10Mbps broadband "plan"

htb (Hierarchical Token Bucket):
  Multiple customers, each with guaranteed minimum speed:
  Dock master (root): 100 boxes/sec total capacity
    Customer A (class 1:10): guaranteed 60 boxes/sec
    Customer B (class 1:20): guaranteed 40 boxes/sec
    
  When A is quiet: B can use A's unused capacity (borrow up to ceil)
  When both busy: enforced at their minimum guarantee
  
  ISP use: each subscriber's VM gets their own class
  Netflix business plan: 1000 boxes/sec min, 1000 boxes/sec ceil
  Home user: 10 boxes/sec min, 100 boxes/sec ceil (can burst!)

netem (Network Emulator):
  Quality control department deliberately introduces defects:
  "Before shipping: randomly lose 5% of boxes"
  "Delay all boxes by 100ms (simulate overseas delivery)"
  "Occasionally corrupt a box's label" (packet corruption)
  
  Used by: testing teams who need to simulate bad delivery conditions
  CI/CD: test application behavior before real customers experience it
  Development: "does our app handle dropped packets gracefully?"
```

---

### Gradual Depth - Five Levels

**Level 1:**
Concept of traffic shaping. `tc qdisc show` to view current qdiscs. `netem`
for adding latency/loss for testing. Basic `tc qdisc add/del` commands.
Default qdisc: `pfifo_fast` (old) or `fq_codel` (modern distros).

**Level 2:**
netem parameters: delay, loss, duplicate, corrupt, reorder. tbf for simple
rate limiting (rate, burst, latency). `tc -s qdisc show` for statistics
(dropped packets). Classful vs classless qdiscs. When to use tbf vs htb.
`fq_codel` and its role in preventing bufferbloat.

**Level 3:**
HTB class hierarchy: handle:classid notation, rate vs ceil. tc filters: u32
filters for IP matching. Actions: `mirred` (redirect/mirror), `police`
(rate limiting with drop). IFB (Intermediate Functional Block) for ingress
shaping (tc only natively supports egress). Per-IP rate limiting with hash
tables in tc. `fq` qdisc and its relationship with BBR congestion control.

**Level 4:**
TC BPF (tc-bpf): eBPF program as classifier or action (Cilium uses this
for Kubernetes networking). Hardware offload: flower qdisc with `offload`
flag (NIC handles classification in hardware). CAKE (Common Applications
Kept Enhanced): modern alternative to fq_codel for home routers. `ssock`
and `ethtool` integration with qdisc for hardware offload. DSCP (Differentiated
Services Code Point) and tc DSCP-based classification. Container-per-class
network QoS in Kubernetes.

**Level 5:**
Linux kernel qdisc API: `struct Qdisc_ops`, `enqueue`, `dequeue` methods.
Writing a custom qdisc kernel module. TC subsystem interaction with `netfilter`
(iptables/nftables) and `nft` (`nft` can set packet marks for tc classification).
`nfmark` + tc filter: mark packets in iptables, classify by mark in tc.
Kubernetes network QoS: CNI plugin integration (Calico, Cilium both use tc
internally). Traffic shaping in Linux containers: `nsenter` into network
namespace, apply tc per-container. `tc-taprio` (Time-Aware Priority Shaper):
IEEE 802.1Qbv for deterministic Ethernet (industrial Ethernet, TSN).

---

### Code Example

**BAD - misusing netem in production:**
```bash
# BAD: Left netem on a production interface accidentally:
# Developer added netem for testing, forgot to remove
tc qdisc add dev eth0 root netem delay 100ms

# Impact: ALL traffic on eth0 now has 100ms added latency!
# Database queries: 200ms round-trip becomes 400ms+
# Health checks: timeout and trigger false alarms
# Symptom: mysterious latency increase after "routine config change"

# Diagnosis:
tc qdisc show dev eth0
# qdisc netem 8001: root refcnt 2 limit 1000 delay 100ms
# ^ netem present! Not normal!

# Fix: remove it immediately:
tc qdisc del dev eth0 root

# Verify:
tc qdisc show dev eth0
# qdisc fq_codel 0: dev eth0 root  <- back to normal

# GOOD: always use a separate network namespace for netem testing
# (isolates from production traffic)
# OR: document netem commands with removal commands:
# APPLY: tc qdisc add dev eth0 root netem delay 100ms loss 2%
# REMOVE: tc qdisc del dev eth0 root
# Set a reminder/alarm to remove after test!
```

**GOOD - per-container rate limiting with HTB:**
```bash
# Rate limit containers on a Docker bridge network
# Scenario: limit each container to 10 Mbps on docker0 bridge

# Get container veth interfaces:
for container in $(docker ps -q); do
    pid=$(docker inspect -f '{{.State.Pid}}' $container)
    veth=$(ip link | grep -A1 "veth" | grep "docker0" | \
           awk '{print $2}' | tr -d ':')
    echo "Container: $container -> veth: $veth"
done

# Rate limit a specific veth (container's NIC on host side):
VETH="vethABCD1234"   # from above
RATE="10mbit"

# Root HTB qdisc:
tc qdisc add dev $VETH root handle 1: htb default 10

# Default class (10 Mbps limit):
tc class add dev $VETH parent 1: classid 1:10 htb \
    rate ${RATE} ceil ${RATE}

# Verify:
tc -s qdisc show dev $VETH
tc class show dev $VETH

# Test from inside container:
# docker exec <container> iperf3 -c iperf-server
# Should see: 10 Mbps limit enforced
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "tc can shape ingress (incoming) traffic directly" | `tc` natively manages EGRESS (outgoing) traffic only. The qdisc sits between the IP routing layer and the NIC transmit queue. For ingress shaping: use the IFB (Intermediate Functional Block) device - redirect ingress traffic to an IFB device, then apply tc to the IFB's egress. Alternative: use `tc` ingress qdisc with a `police` action (drops excess incoming packets, not true shaping). True ingress shaping requires a proxy (squid, HAProxy) or network-level control (router QoS). In container networking: shaping is applied to the host-side veth interface's EGRESS, which is the container's ingress - this effectively limits incoming bandwidth for the container. |
| "netem adds latency in both directions" | `netem` applied to an interface adds latency only to OUTGOING traffic from that interface. For bidirectional latency simulation: apply netem on BOTH ends of the connection. In a veth pair (server <-> client namespace): apply netem on client's veth1 for client->server latency, and apply netem on server's veth0 for server->client latency. Common mistake: adding 100ms netem on client interface and observing 100ms ping RTT instead of the expected 200ms (each direction). RTT = client egress delay (100ms) + server egress delay (0ms) = 100ms total, not 200ms. For 200ms RTT: add 100ms on EACH side. |
| "fq_codel always reduces latency compared to pfifo" | `fq_codel` reduces QUEUING latency (bufferbloat) by actively managing queue depth. But it introduces some per-packet overhead (hash computation, queue selection, CoDel measurement). For very low latency workloads (HFT, network gaming at < 1ms): the overhead of fq_codel might be measurable. For high-throughput servers where fairness is needed: fq_codel improves overall fairness and prevents elephant flow monopolization. The default switch from `pfifo_fast` to `fq_codel` (done in many distributions) is correct for most use cases (web servers, general networking). For specialized ultra-low-latency: consider `none` (NVMe equivalent for networking) or `fq` (fair queuing without CoDel). |
| "tc qdisc delete removes all shaping instantly" | `tc qdisc del dev eth0 root` removes the root qdisc and all child classes/qdiscs/filters. Packets already IN the queue at the time of deletion: flushed immediately. In-flight packets (sent to NIC ring): unaffected. So yes, it takes effect nearly instantly for new packets. HOWEVER: if using HTB or TBF and the qdisc was holding packets (throttled), those queued packets are dropped immediately upon deletion. Applications may observe a burst of packet loss at the moment of removal. For graceful removal: first set the rate higher (tc qdisc change), wait for queue to drain, then remove. Also: kernel network namespace deletion (`ip netns del`) removes all qdiscs in that namespace instantly. |

---

### Failure Modes & Diagnosis

**tc/qdisc troubleshooting:**
```bash
# === Failure: tc qdisc add fails ===
tc qdisc add dev eth0 root netem delay 100ms
# Error: RTNETLINK answers: Operation not supported
# Cause 1: netem module not loaded
modprobe sch_netem
# Verify: lsmod | grep sch_netem
# Cause 2: non-root user without CAP_NET_ADMIN

# === Failure: rate limiting not working ===
tc qdisc add dev eth0 root tbf rate 10mbit burst 100kb latency 400ms
# iperf3 still shows 100 Mbps!
# Diagnosis: tc controls EGRESS. If iperf3 client is on THIS machine:
# iperf3 -c server (egress from this machine -> SHAPING APPLIED)
# iperf3 -s (ingress to this machine -> NO SHAPING BY DEFAULT)

# Check: tc -s qdisc show dev eth0
# Sent: X bytes Y pkt (dropped 0, overlimits 0 requeues 0)
# If overlimits=0 when you expect rate limiting: wrong direction

# === Failure: all traffic dropped after tc filter setup ===
# Added HTB with filter, now no traffic
tc qdisc show dev eth0
tc class show dev eth0
tc filter show dev eth0

# Check: default class in HTB (packets not matched by any filter):
# tc qdisc add dev eth0 root handle 1: htb default 30
# If 1:30 class doesn't exist: unmatched packets dropped!
# Fix: add default class:
tc class add dev eth0 parent 1:1 classid 1:30 htb rate 1mbit ceil 100mbit

# === Diagnosis: checking qdisc statistics ===
tc -s qdisc show dev eth0
# qdisc htb 1: root refcnt 2 r2q 10 default 0x30 ...
#  Sent 12345678 bytes 9876 pkt (dropped 123, overlimits 456 requeues 0)
# 
# dropped: packets dropped by qdisc (queue full, police action)
# overlimits: packets that exceeded rate (queued or dropped)
# requeues: packets requeued for retry

# Per-class statistics:
tc -s class show dev eth0
# class htb 1:10 parent 1:1 leaf 10:
#  rate 60Mbit ceil 100Mbit burst 1599b cburst 1536b
#  Sent 56789012 bytes 5678 pkt (dropped 0, overlimits 1234 requeues 0)

# === Latency measurement with netem ===
# Verify netem delay is applied correctly:
tc qdisc add dev eth0 root netem delay 50ms
ping -c 10 8.8.8.8
# rtt min/avg/max = 50.1/50.5/51.2 ms
# Expected: 50ms added on top of base RTT

# WARNING: netem affects all traffic on the interface
# Including: SSH sessions, monitoring agents, health checks!
# Best practice: use network namespaces for isolated netem testing
```

---

### Related Keywords

**Foundational:**
LNX-037 (Networking), LNX-084 (Network performance)

**Builds on this:**
LNX-085 (XDP), LNX-092 (Network namespaces)

**Related:**
LNX-092 (Network namespaces and veth pairs)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `tc qdisc show [dev eth0]` | View qdiscs |
| `tc -s qdisc show dev eth0` | View with statistics |
| `tc qdisc add dev eth0 root netem delay 100ms` | Add 100ms latency |
| `tc qdisc add dev eth0 root netem loss 5%` | Add 5% packet loss |
| `tc qdisc del dev eth0 root` | Remove all shaping |
| `tc qdisc add dev eth0 root tbf rate 10mbit burst 100kb latency 400ms` | Rate limit to 10Mbps |
| `modprobe sch_netem` | Load netem module |

**3 things to remember:**
1. `tc` shapes EGRESS only by default - to shape ingress you need IFB device or shape the other end
2. `netem` is for testing only; remember to remove it (`tc qdisc del dev eth0 root`) after testing, or it affects all production traffic
3. HTB `default` class is mandatory - packets not matched by any filter go to the default classid; missing default = unmatched traffic dropped

---

### Transferable Wisdom

The qdisc concepts (fair queuing, rate limiting, prioritization) are the
OS-level equivalent of: Kubernetes QoS (Guaranteed, Burstable, BestEffort),
AWS SQS FIFO queues vs standard queues, JVM thread pool executors (fixed,
cached, scheduled), database connection pools with max connections and queue.
The Token Bucket Filter (tokens accumulate at rate, burst uses tokens) is the
same as: API rate limiting (replenish N tokens per second, each request costs
1 token), Redis rate limiter with SETNX, AWS API Gateway throttling. fq_codel's
"drop based on queue delay, not queue size" is the same insight as: circuit
breaker (trip on response time, not on queue depth), Kafka producer
`delivery.timeout.ms` (timeout on delay, not on queue count), TCP keepalive
(drop connection if not responsive in time, not when buffer full). The HTB
class hierarchy (parent/child bandwidth sharing) maps to: Kubernetes namespace
resource quotas (cluster -> namespace -> pod), AWS org-level vs account-level
service quotas, tiered pricing in cloud services. netem's use for testing
distributed system resilience is the same principle as: Netflix Chaos Monkey
(inject failures in production), AWS Fault Injection Simulator, Chaos Mesh in
Kubernetes.

---

### The Surprising Truth

`tc` (traffic control) was implemented in Linux in 1998 and has barely changed
its command-line interface since. The same `tc qdisc add dev eth0 root htb`
syntax from 1998 Linux works on a 2024 kernel. Despite its age: it's used
in nearly every major cloud provider's networking stack. AWS's bandwidth
throttling on EC2 instances uses similar Linux TC mechanisms under the hood
(enforced at the hypervisor level via similar qdisc/token bucket logic on
the Nitro hypervisor). Kubernetes CNI plugins (Calico, Cilium) use TC BPF
(eBPF programs attached to the TC hook) for efficient pod-to-pod routing
and network policy. The bufferbloat problem (discovered and documented around
2011 by Jim Gettys and others) affected millions of routers and cable modems
worldwide - home internet users experienced high latency during file downloads
because router buffers were too large and filled completely. The fix (CoDel,
then fq_codel) was implemented in Linux in 2012. Linux 3.5+ ships with fq_codel
available. Many home routers still run older firmware with pfifo bufferbloat
issues, but any Linux-based router running modern software has the fix available.
The quality of your gaming or video call experience during a file download
depends directly on whether your router's qdisc is using fq_codel or an older
algorithm.

---

### Mastery Checklist

- [ ] Can use netem to simulate network conditions (delay, loss, jitter) for testing
- [ ] Understands the difference between classless (tbf, netem) and classful (htb) qdiscs
- [ ] Can diagnose qdisc issues using `tc -s qdisc show` statistics
- [ ] Knows that tc shapes egress only and can explain how to shape ingress
- [ ] Can set up basic HTB class hierarchy for per-user bandwidth limiting

---

### Think About This

1. Design a CI/CD test harness that automatically runs your microservice test
   suite under five different network conditions: (a) LAN (< 1ms, 0% loss),
   (b) corporate WAN (50ms, 0.1% loss), (c) mobile 4G (80ms, 2% loss, 10Mbps),
   (d) congested network (200ms, 5% loss, 1Mbps), (e) satellite (600ms, 1%
   loss). Use network namespaces and netem. Explain which tests would catch
   timeout bugs, retry logic failures, and streaming performance degradation.
   What specific code behavior are you testing with each scenario?

2. A multi-tenant cloud service needs to enforce per-tenant bandwidth limits:
   50 tenants, each with a 100 Mbps NIC. Tenant A paid for 10 Mbps, Tenant B
   for 30 Mbps, remaining tenants share 60 Mbps. Design the HTB class hierarchy
   (handle:classid notation, rate, ceil values), the filter rules to classify
   traffic per tenant, and explain what happens when Tenant A is idle and Tenant
   B has a burst of traffic.

3. Explain why `fq_codel` (with its 5ms target queuing delay) improves
   interactive application latency (gaming, video calls) even during bulk file
   transfer, while `pfifo_fast` causes degraded interactive latency during
   bulk transfer. Use the concept of sojourn time and the CoDel algorithm's
   dropping decision to explain the mechanism. Why is the dropping approach
   better than simply using a smaller queue size?

---

### Interview Deep-Dive

**Foundational:**
Q: What is a qdisc in Linux and how would you use netem to test your application's behavior on a poor network connection?
A: A qdisc (queueing discipline) is an algorithm that controls how packets are enqueued and dequeued from a network interface's transmit queue. The default qdisc on modern Linux is `fq_codel` (Fair Queuing with Controlled Delay), which provides per-flow fairness and active queue management to prevent bufferbloat. Different qdiscs provide different behaviors: simple FIFO (pfifo), rate limiting (tbf), hierarchical rate limiting (htb), and network emulation for testing (netem). NETEM FOR TESTING: `tc qdisc add dev eth0 root netem delay 100ms 20ms loss 2%` - this adds: (1) 100ms base delay with 20ms jitter (simulating a cross-country WAN connection), (2) 2% random packet loss (simulating congested mobile network). After adding this: all traffic from eth0 experiences these conditions. Test your application: does it timeout correctly? Does retry logic work? Does streaming degrade gracefully? PRACTICAL USAGE: In CI/CD: create a network namespace, connect it with a veth pair with netem, run the server in one namespace and the client in another. Test different scenarios: high latency (satellite), high loss (mobile), rate limited (slow broadband). IMPORTANT: always remember to remove netem after testing: `tc qdisc del dev eth0 root`. Leaving netem on a production interface adds artificial latency to all traffic. For isolation: use network namespaces (`ip netns add test; ip link add veth0 type veth peer name veth1; ip link set veth1 netns test`).

**Expert:**
Q: Explain the bufferbloat problem and how fq_codel solves it differently from simply using a smaller queue.
A: BUFFERBLOAT PROBLEM: TCP is a window-based protocol that fills available buffer space to probe bandwidth. Router/NIC buffers are often configured to be very large (to avoid packet loss). When a bulk transfer fills a large buffer: queue builds up, each packet sits in queue for seconds. Simultaneously: interactive traffic (DNS, ACK, small HTTP request) gets stuck behind the bulk data in the queue. User experience: video game ping spikes from 20ms to 2000ms during a file download. Why small queues don't fully solve it: reducing queue size reduces bufferbloat latency but INCREASES packet loss (TCP then throttles, reducing throughput). The challenge: need LOW latency for interactive flows AND HIGH throughput for bulk flows simultaneously. CoDel APPROACH: Instead of measuring queue SIZE: measure queuing DELAY (sojourn time). CoDel drops packets when sojourn time exceeds target (5ms) for longer than interval (100ms). The key insight: if packets are being processed fast enough, the queue is short and sojourn is low. If sojourn exceeds target: the bottleneck is congested, drop aggressively to signal TCP to back off. CoDel's drop rate increases with sqrt(drop_count): each subsequent drop is at 1/sqrt(N) * interval. This provides TCP with paced loss signals rather than a burst of drops at queue overflow. FQ (FAIR QUEUING) ADDITION in fq_codel: separate queue per flow (5-tuple hash) with round-robin service. Prevents one bulk TCP flow from monopolizing the queue. A single HTTP/2 download can no longer block a DNS query or VoIP packet. RESULT: fq_codel achieves: interactive flow latency near target (5ms additional), bulk throughput maintained, multiple flows share bandwidth fairly. This is far superior to simply reducing queue size (which hurts throughput) or ignoring the problem (which hurts interactive latency).
