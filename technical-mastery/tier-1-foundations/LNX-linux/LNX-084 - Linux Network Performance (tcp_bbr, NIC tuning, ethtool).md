---
id: LNX-084
title: "Linux Network Performance (tcp_bbr, NIC tuning, ethtool)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-037, LNX-039
used_by: LNX-085, LNX-093
related: LNX-085, LNX-037, LNX-039, LNX-093
tags: [tcp-bbr, ethtool, ring-buffer, interrupt-coalescing, rss, rps, xps, gro, gso, tso, tcp-tuning, network-performance, socket-buffer, qdisc, offloading, nic-tuning, napi]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 84
permalink: /technical-mastery/lnx/linux-network-performance/
---

## TL;DR

Linux network performance tuning covers multiple layers: **NIC hardware**
(ring buffer size, interrupt coalescing via `ethtool`), **offloading** (TSO/GSO/
GRO/LRO - NIC handles segmentation/reassembly), **RSS/RPS/RFS** (distribute
packet processing across CPUs), **socket buffers** (`net.core.rmem_max`,
`net.core.wmem_max`, TCP buffer autotune), and **TCP congestion control**
(`tcp_bbr` - Google's BBR algorithm for high-bandwidth/high-latency links,
vs CUBIC default). Key tools: `ethtool -g/-C/-k` (ring, coalescing, offloads),
`ss -s` (socket stats), `netstat -s` (protocol stats), `iperf3` (bandwidth test).
BBR: set `sysctl net.ipv4.tcp_congestion_control=bbr`. Check NIC stats:
`ethtool -S eth0 | grep -i drop`.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-084 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | TCP BBR, ethtool, ring buffer, interrupt coalescing, TSO/GRO, RSS, socket buffer, network performance, qdisc |
| **Prerequisites** | LNX-037 (Networking fundamentals), LNX-039 (TCP/IP) |

---

### The Problem This Solves

**Problem 1**: A 10Gbps link is only achieving 2Gbps throughput. The application
is using default socket buffers (212KB). A 100ms RTT connection with a 2Gbps
link needs at minimum 25MB of buffer (bandwidth-delay product = 10Gbps * 0.1s /
8 = 125MB socket buffer). With only 212KB buffer: the sender fills the buffer,
stops sending (flow control), waits for ACK, repeats. Link is mostly idle.
Increasing `net.ipv4.tcp_rmem` and `net.ipv4.tcp_wmem` allows TCP to fill the
pipe.

**Problem 2**: A 40Gbps NIC is causing 100% CPU usage on CPU 0 alone. All
packet interrupts are going to CPU 0. With RSS (Receive Side Scaling): the
NIC's hardware can distribute interrupts across all CPUs using a hash of
IP/port tuples. CPU usage distributes across 8 CPUs = 12.5% each instead
of 100% on one.

---

### Textbook Definition

**Network performance stack (bottom-up):**
| Layer | Components | Tools |
|-------|-----------|-------|
| NIC Hardware | Ring buffers, RSS queues, interrupt coalescing | `ethtool` |
| Kernel Driver | NAPI polling, IRQ affinity | `irqbalance`, `/proc/irq/` |
| Offloading | TSO, GSO, GRO, LRO, checksum | `ethtool -k` |
| Packet dispatch | RSS, RPS, RFS, XPS | `sysctl`, `/sys/class/net/` |
| Socket buffers | `rmem`, `wmem`, `backlog` | `sysctl net.*` |
| TCP/IP | Congestion control, window scaling | `sysctl net.ipv4.*` |
| Application | Socket API, zero-copy, io_uring | `iperf3`, `netperf` |

**Key terms:**
- **TSO** (TCP Segmentation Offload): NIC segments large TCP frames into MTU-sized packets (no CPU needed)
- **GRO** (Generic Receive Offload): kernel coalesces small packets into large ones before protocol processing
- **RSS** (Receive Side Scaling): NIC hardware distributes incoming packets to multiple RX queues via IP/port hash
- **RPS** (Receive Packet Steering): software RSS for NICs without hardware RSS
- **BBR** (Bottleneck Bandwidth and RTT): Google's TCP congestion control algorithm (2016). Probes for bandwidth and RTT instead of packet loss. Better than CUBIC on lossy/high-latency links.

---

### Understand It in 30 Seconds

```bash
# === NIC information and tuning with ethtool ===

# View NIC ring buffer sizes:
ethtool -g eth0
# Ring parameters for eth0:
# Pre-set maximums:
# RX:     4096    <- max hardware RX ring
# TX:     4096    <- max hardware TX ring
# Current hardware settings:
# RX:     256     <- currently set (too small for high traffic!)
# TX:     256

# Increase ring buffers (reduce drops under burst):
ethtool -G eth0 rx 4096 tx 4096

# View interrupt coalescing settings:
ethtool -c eth0
# Adaptive RX: on    <- auto-adjust coalescing
# rx-usecs: 50       <- coalesce interrupts for 50 microseconds
# rx-frames: 0

# Set coalescing (trade off latency vs throughput):
# For throughput (batch more packets per interrupt):
ethtool -C eth0 rx-usecs 100 tx-usecs 100
# For low latency (interrupt per packet):
ethtool -C eth0 rx-usecs 0 tx-usecs 0 adaptive-rx off

# View offloading features:
ethtool -k eth0
# tcp-segmentation-offload: on   <- TSO enabled
# generic-segmentation-offload: on <- GSO enabled
# generic-receive-offload: on    <- GRO enabled
# large-receive-offload: off     <- LRO (can cause issues, usually off)
# rx-checksumming: on
# tx-checksumming: on

# Disable LRO if causing issues:
ethtool -K eth0 lro off

# View NIC stats (drops, errors):
ethtool -S eth0 | grep -i "drop\|miss\|error\|overflow"
# rx_dropped: 12345   <- drops at NIC level (ring buffer full?)
# rx_missed_errors: 0

# === TCP congestion control ===
# Check current congestion control:
sysctl net.ipv4.tcp_congestion_control
# net.ipv4.tcp_congestion_control = cubic  <- default

# Available algorithms:
sysctl net.ipv4.tcp_available_congestion_control
# reno cubic bbr

# Load BBR module:
modprobe tcp_bbr
echo "tcp_bbr" >> /etc/modules-load.d/bbr.conf

# Enable BBR:
sysctl -w net.ipv4.tcp_congestion_control=bbr
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.d/99-bbr.conf

# Verify BBR is active:
sysctl net.ipv4.tcp_congestion_control
# net.ipv4.tcp_congestion_control = bbr

# === Socket buffer tuning ===
# View current limits:
sysctl net.core.rmem_max     # max receive buffer
sysctl net.core.wmem_max     # max send buffer
sysctl net.ipv4.tcp_rmem     # TCP: min default max
sysctl net.ipv4.tcp_wmem

# Example output:
# net.core.rmem_max = 212992      <- ~208KB (very small for 10Gbps!)
# net.ipv4.tcp_rmem = 4096 87380 6291456  <- min 4KB default 85KB max 6MB

# For high-bandwidth connections (10Gbps+):
cat >> /etc/sysctl.d/99-network.conf << 'EOF'
net.core.rmem_max = 134217728       # 128MB max socket receive buffer
net.core.wmem_max = 134217728       # 128MB max socket send buffer
net.ipv4.tcp_rmem = 4096 87380 134217728  # TCP: 128MB max
net.ipv4.tcp_wmem = 4096 65536 134217728  # TCP: 128MB max
net.core.netdev_max_backlog = 5000  # increase packet backlog
EOF
sysctl -p /etc/sysctl.d/99-network.conf

# === RSS: distribute packets across CPUs ===
# Check number of RSS queues:
ethtool -l eth0
# Channel parameters for eth0:
# Pre-set maximums:
# Combined: 8     <- 8 hardware queues available
# Current hardware settings:
# Combined: 1     <- only 1 queue being used!

# Enable all hardware queues:
ethtool -L eth0 combined 8

# Check IRQ affinity (which CPUs handle which queue):
for i in $(seq 0 7); do
    echo -n "Queue $i -> CPU: "
    cat /proc/irq/$(ls /proc/irq/ | xargs grep -l "eth0-TxRx-$i" 2>/dev/null | head -1)/smp_affinity_list 2>/dev/null || echo "?"
done

# Enable RPS (software RSS) for NICs without hardware RSS:
for f in /sys/class/net/eth0/queues/rx-*/rps_cpus; do
    echo ff > $f  # all CPUs (bitmask ff = 8 CPUs)
done

# === Test network performance ===
# Bandwidth test with iperf3:
# Server:
iperf3 -s

# Client (test TCP throughput):
iperf3 -c server_ip -t 30 -P 4  # 4 parallel streams, 30 seconds
# [SUM] 0.00-30.00 sec  35.7 GBytes  9.96 Gbits/sec  <- ~10Gbps

# Test with large receive window:
iperf3 -c server_ip -t 30 -P 4 -w 128M  # 128MB window

# TCP retransmission statistics:
netstat -s | grep -i retransmit
# 1234 segments retransmitted
ss -s
# Total: 234 (kernel 0) sockets
# TCP:   123 (estab 45, closed 67, orphaned 2, timewait 9)
```

---

### First Principles

**The network receive path (RX) performance:**
```
NIC receives packet:
  1. NIC: DMA packet to ring buffer (RAM, pre-allocated)
         Ring buffer = circular array of packet descriptors
         Ring buffer too small -> drops when burst fills it
         ethtool -G eth0 rx 4096: increase ring size
  
  2. NIC: raises hardware interrupt (IRQ)
         interrupt coalescing (ethtool -C rx-usecs 50):
           wait 50us, batch multiple packets before interrupting
           Trade-off: latency (50us added) vs throughput (fewer interrupts)
  
  3. CPU: interrupt handler runs
         Disables further interrupts (NAPI: poll mode instead)
         Schedules softirq NET_RX_SOFTIRQ
  
  4. Softirq (NAPI poll) runs on interrupted CPU:
         Polls ring buffer: reads packets in batch
         For each packet: sk_buff allocation + copy
         Runs protocol stack: Ethernet -> IP -> TCP
         Places data in socket receive buffer
  
  5. Application: recv() reads from socket receive buffer

Bottlenecks at each step:
  Step 1: Ring buffer drops -> increase with ethtool -G
  Step 2: Too many interrupts -> use adaptive coalescing
  Step 3: All interrupts on CPU 0 -> use RSS/RPS to spread
  Step 4: Single CPU for softirq -> RSS (multi-queue NIC)
  Step 5: Small socket buffer -> increase rmem_max

GRO (Generic Receive Offload) optimization:
  Without GRO: 10 small TCP segments -> 10 sk_buff allocations
               -> 10 IP header parses -> 10 TCP header parses
               -> 10 calls up the stack
  
  With GRO: kernel coalesces 10 segments into 1 large segment
            -> 1 allocation -> 1 parse -> 1 stack call
            -> Better CPU efficiency for bulk data
  
  GRO limitation: cannot coalesce if headers differ
  Always enabled for TCP bulk transfers
  Slight latency increase for individual small packets

TSO (TX Segmentation Offload):
  Without TSO: CPU segments 64KB buffer into 1460-byte segments
               10+ sk_buff allocations + IP/TCP headers per segment
               CPU overhead: ~50ns per segment
               64KB / 1460B = 45 segments = 2.25us CPU overhead
               At 10Gbps: 10^9 / 1460 = 685,000 segments/sec
               685,000 * 2.25us = 1.54 SECONDS of CPU per second (!)
  
  With TSO: CPU creates one large sk_buff (up to 64KB)
            NIC hardware segments to MTU-sized packets
            CPU overhead: ~50ns for one large sk_buff
            At 10Gbps: still ~685,000 segments but NIC does the work
            CPU freed for other tasks
```

**TCP BBR vs CUBIC:**
```
CUBIC (default Linux TCP):
  Congestion detection: PACKET LOSS
  Behavior: increase window until packet loss -> halve window
  Problem 1: On lossy WiFi/cellular: 1% random loss = halve window
             even though bandwidth is available!
  Problem 2: Bandwidth-delay product (BDP) unfilled:
             RTT=100ms, 10Gbps link, BDP = 125MB
             CUBIC probes slowly: may take minutes to fill pipe
  Problem 3: Shallow buffers: packet queued in router buffer
             CUBIC doesn't know buffer is full until loss occurs
             -> large queuing latency ("bufferbloat")

BBR (Bottleneck Bandwidth and RTT):
  Model: estimates bandwidth AND RTT separately
  Algorithm:
    1. Probe bandwidth: slowly increase rate, measure delivery rate
    2. Probe RTT: periodically reduce rate to measure minimum RTT
    3. Operate at estimated bandwidth, pace to avoid bursts
  
  Advantage 1: doesn't rely on loss for congestion detection
    Handles 1-2% random loss (WiFi, LTE) without rate reduction
  Advantage 2: startup - fills pipe faster (exponential probing)
  Advantage 3: pacing - sends at even rate, less burst buffering
  Advantage 4: high-BDP links - exploits full bandwidth
  
  Disadvantage: can be unfair to CUBIC flows in mixed networks
    BBR may "crowd out" CUBIC connections on shared bottleneck
    BBR v2 (2022) improves this fairness
  
  When to use BBR:
    Inter-datacenter links (high bandwidth, non-zero loss)
    Content delivery (video streaming to varied client networks)
    Connections over lossy networks (cellular, satellite)
  
  When CUBIC may be fine:
    LAN connections (zero loss, very low RTT)
    Short-lived connections (never reaches steady state)
```

---

### Thought Experiment

Diagnosing a 10Gbps link only achieving 2Gbps:

```bash
# Step 1: Basic bandwidth test:
iperf3 -c server_ip -t 30 -P 4
# [SUM] 0.00-30.00 sec  7.5 GBytes  2.09 Gbits/sec  <- only 2Gbps!

# Step 2: Check socket buffer sizes:
sysctl net.ipv4.tcp_rmem net.ipv4.tcp_wmem
# net.ipv4.tcp_rmem = 4096 87380 6291456
# net.ipv4.tcp_wmem = 4096 65536 6291456
# Max 6MB buffers on a 100ms RTT link:
# BDP = 10Gbps * 0.1s / 8 = 125MB needed!
# 6MB << 125MB -> buffer too small

# Fix: increase buffers:
sysctl -w net.core.rmem_max=134217728    # 128MB
sysctl -w net.ipv4.tcp_rmem="4096 87380 134217728"
sysctl -w net.ipv4.tcp_wmem="4096 65536 134217728"

# Re-test:
iperf3 -c server_ip -t 30 -P 4 -w 64M
# [SUM] 0.00-30.00 sec  35.7 GBytes  9.96 Gbits/sec  <- 10Gbps!

# Step 3: If still slow - check NIC ring buffer:
ethtool -S eth0 | grep -i drop
# rx_dropped: 5678234   <- massive drops!
ethtool -g eth0
# Current RX: 256  <- too small!
ethtool -G eth0 rx 4096   # increase ring

# Step 4: Check IRQ distribution:
mpstat -P ALL 1 3 | grep -v "^$"
# CPU 0: %softirq 89.2  <- almost all interrupts on CPU 0
# CPU 1-7: %softirq < 1%
# RSS not configured!

# Enable RSS (multi-queue):
ethtool -l eth0 | grep Combined
# Current: 1 <- only 1 queue
ethtool -L eth0 combined $(nproc)   # set to CPU count
# Now interrupts distribute across all CPUs
```

---

### Mental Model / Analogy

```
Network stack performance = highway system for data

NIC ring buffer = on-ramp holding area:
  Too small: during traffic burst, cars pile up, overflow
  Some cars (packets) turned away (dropped)
  ethtool -G eth0 rx 4096: build a bigger on-ramp

Interrupt coalescing = traffic light timing:
  Without coalescing: traffic light changes every car (1 car per interrupt)
  High overhead: light-change time >> car-passing time
  
  With coalescing: light stays green until N cars pass or T time
  Less overhead, more cars per light change
  Trade-off: first car waits until light changes (latency)
  ethtool -C rx-usecs 50: change light every 50 microseconds

RSS (multi-queue) = multiple highway lanes:
  Single queue: all cars exit at same tollbooth -> bottleneck
  RSS/4 queues: 4 parallel toll booths, cars distributed by hash
  4x throughput, CPU load distributed

Socket buffers = destination parking lots:
  TCP receiver has a "parking lot" (socket buffer)
  Too small: sender fills it, must stop and wait (TCP flow control)
  Buffer limit: BDP = bandwidth * RTT
  For 10Gbps + 100ms: need 125MB parking lot minimum
  Default 6MB: sender is idle 95% of the time!

TSO = shipping by pallet vs individual boxes:
  Without TSO: CPU wraps every 1460-byte box individually (CPU intensive)
  With TSO: CPU wraps one 64KB pallet, NIC splits into boxes
  NIC is specialized hardware: box-splitting is its job (not CPU's)

GRO = mail room consolidation:
  Incoming mail: 100 letters per second from same sender
  Without GRO: deliver each letter individually (100 trips)
  With GRO: consolidate letters, deliver batch of 10 (10 trips)
  10x fewer trips up the protocol stack

BBR = smart delivery truck route planning:
  CUBIC (old): drive until you hit a traffic jam (packet loss)
  Then slow down dramatically
  Problem: light rain (1% packet loss) = always hit "jams"
  
  BBR: continuously probe optimal speed
    "What's the fastest I can go without causing jams?"
    Measures actual bandwidth + RTT (not loss)
    Adjusts smoothly to network conditions
    Better for cross-country deliveries (high RTT)
    Better for bumpy roads (lossy WiFi/cellular)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Network performance basics: bandwidth, latency, throughput. `iperf3` for
testing. Default socket buffer sizes. Basic `ethtool` for NIC info.
TCP congestion control concept.

**Level 2:**
Socket buffer tuning (`rmem_max`, `wmem_max`). `ethtool -g` ring buffers.
TSO/GRO offloading. `ethtool -k` to view/set offloads. RSS for multi-queue
NICs. TCP BBR vs CUBIC. `ss -s` and `netstat -s` for statistics.

**Level 3:**
NAPI polling mechanism. IRQ affinity (`/proc/irq/*/smp_affinity`). RPS/RPS/
XPS software steering. Interrupt coalescing trade-offs. Bandwidth-delay
product calculation. Qdisc (queuing disciplines): `tc qdisc show`. `fq`
(Fair Queuing) qdisc for pacing. `ethtool -S` for NIC statistics and drop
analysis.

**Level 4:**
DPDK (Data Plane Development Kit): kernel bypass for maximum NIC performance.
XDP (eXpress Data Path): eBPF at NIC driver level. `SO_BUSY_POLL` socket
option: busy-polling instead of interrupts for low-latency. Receive flow
steering (RFS): direct packets to the CPU where the application thread
runs. `sk_buff` structure internals. Zero-copy receive: `SO_ZEROCOPY` send,
`MSG_ZEROCOPY`. PCIe bandwidth limits for very high-speed NICs.

**Level 5:**
NIC driver architecture: `struct net_device_ops`. `netif_receive_skb` path.
RSS hash function configuration (Toeplitz hash, symmetric hash). Kernel
network flow offloading (TC flower for hardware offload). Smart NIC
(DPU - Data Processing Unit): running networking workloads on NIC CPU
(Nvidia BlueField, Marvell LiquidIO). BBR v2 algorithm internals: pacing
rate, cwnd, BW probing state machine. RDMA (Remote Direct Memory Access)
over Ethernet (RoCEv2): bypass kernel for lowest latency.

---

### Code Example

**BAD - ignoring network performance settings:**
```bash
# BAD 1: Large file transfer over WAN with default buffers:
# scp large_file.tar.gz user@remote:/destination/
# Speed: 25 MB/s on a 1Gbps link (could be 125 MB/s)
# 
# Root cause: default TCP socket buffer (87KB) on 50ms RTT link
# BDP = 1Gbps * 0.05s / 8 = 6.25MB needed
# 87KB << 6.25MB -> sender fills buffer, stalls
# Utilization: 87KB / 6.25MB = 1.4% of link bandwidth!

# GOOD: Set buffers before scp, or use tool with window control:
sysctl -w net.core.rmem_max=67108864       # 64MB
sysctl -w net.core.wmem_max=67108864       # 64MB
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"
# Retry scp: now achieves 120+ MB/s

# Or use rsync with explicit window:
rsync -avz --sockopts=SO_RCVBUF=67108864 large_file.tar.gz user@remote:/

# BAD 2: All NIC interrupts on CPU 0 (single-queue):
# top shows: CPU 0 at 100% (mostly softirq si%)
# CPU 1-7 at < 5%

# GOOD: Enable multi-queue and distribute interrupts:
# Check queue count:
ethtool -l eth0 | grep Combined
# Current hardware settings: Combined: 1  <- only 1 queue!

# Enable all queues:
ethtool -L eth0 combined $(nproc)

# Set IRQ affinity manually (if needed):
# Spread IRQs across CPUs:
IRQ_LIST=$(grep eth0 /proc/interrupts | awk '{print $1}' | tr -d ':')
CPU=0
for irq in $IRQ_LIST; do
    echo $(printf "%x" $((1 << CPU))) > /proc/irq/$irq/smp_affinity
    CPU=$(( (CPU + 1) % $(nproc) ))
done

# Verify distribution:
cat /proc/net/softnet_stat | awk '{print NR-1": total="$1" dropped="$2}'
# CPU 0: total=1234567 dropped=0
# CPU 1: total=1234000 dropped=0  <- balanced!
# CPU 2: total=1235000 dropped=0
```

**GOOD - BBR and performance validation:**
```bash
# Enable and validate BBR:
# 1. Load BBR module:
modprobe tcp_bbr
lsmod | grep bbr   # confirm loaded

# 2. Set BBR as default:
sysctl -w net.ipv4.tcp_congestion_control=bbr

# 3. Verify per-connection: (requires ss version supporting bbrinfo)
ss -tin dst server_ip
# ... cwnd:10 send 1.2Mbps ... bbr ...
# bbr field present = BBR active for this connection

# 4. Benchmark CUBIC vs BBR on a lossy link (simulated):
# Add 1% packet loss on loopback for testing:
tc qdisc add dev lo root netem loss 1%

# Test CUBIC:
sysctl -w net.ipv4.tcp_congestion_control=cubic
iperf3 -c localhost -t 30 -b 1G 2>&1 | tail -3
# [SUM] 0.00-30.00 sec  2.80 GBytes   804 Mbits/sec  <- 20% of bandwidth!

# Test BBR:
sysctl -w net.ipv4.tcp_congestion_control=bbr
iperf3 -c localhost -t 30 -b 1G 2>&1 | tail -3
# [SUM] 0.00-30.00 sec  3.35 GBytes   963 Mbits/sec  <- 96% of bandwidth!

# Cleanup:
tc qdisc del dev lo root

# Persistent BBR configuration:
cat > /etc/sysctl.d/99-network-perf.conf << 'EOF'
# TCP BBR congestion control
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq       # BBR works best with Fair Queue qdisc

# Socket buffers for high-bandwidth links
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Reduce TCP TIME_WAIT for busy servers
net.ipv4.tcp_tw_reuse = 1

# Increase connection backlog
net.core.somaxconn = 32768
net.core.netdev_max_backlog = 5000
EOF
sysctl -p /etc/sysctl.d/99-network-perf.conf
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "BBR is always better than CUBIC" | BBR is better for: lossy networks, high-bandwidth-delay-product links, and streaming. BBR can be WORSE in: (1) LAN connections with zero loss and very low RTT (CUBIC performs equally well in ideal conditions). (2) Mixed networks where BBR and CUBIC flows compete (BBR can be unfair, crowding out CUBIC flows). (3) Connections that need predictable steady-state throughput (BBR periodically reduces rate to probe RTT). BBR v2 (kernel 5.13+) improves fairness. The rule: try BBR on inter-datacenter/WAN links and measure. Don't blindly apply to all connections. |
| "Increasing socket buffers always improves performance" | Large socket buffers improve performance on high-bandwidth-delay-product links but can HURT in other cases: (1) Bufferbloat: large send buffers mean more data in-flight that can fill router queues, increasing latency for other connections. (2) Memory: each TCP connection with a 128MB buffer doesn't use 128MB by default (TCP autotune starts small and grows), but 10,000 connections at 128MB max = 1.28TB of potential allocation. Set `net.core.rmem_max` and `net.core.wmem_max` as the MAXIMUM (kernel autotunes within). The tcp_rmem and tcp_wmem third field (max) is what autotune can grow to. |
| "ethtool offloads are always beneficial" | Most offloads (TSO, GSO, GRO, checksum) are beneficial in normal operation. LRO (Large Receive Offload) is frequently problematic: hardware coalesces packets before the kernel can inspect them, which can cause issues with packet capture tools (tcpdump sees wrong sizes), virtualization (forwarded packets become too large), and some tunnel protocols. GRO is generally preferred over LRO (software, more flexible, can be disabled per-interface). TSO/GSO can interfere with TC qdisc shapers because the kernel sees 64KB frames instead of 1500-byte packets, making rate limiting inaccurate. Disable TSO/GSO when using traffic control: `ethtool -K eth0 gso off gro off tso off`. |
| "NIC ring buffer drops mean packet loss" | NIC ring buffer drops (seen in `ethtool -S eth0 | grep drop`) indicate packets dropped at the NIC level BEFORE the kernel. However: (1) This does not immediately mean application data loss - TCP retransmits dropped packets. (2) Ring buffer drops indicate CPU is not processing packets fast enough (interrupt handling too slow, or burst exceeding ring). (3) Some NIC counter names are misleading - `rx_dropped` in some drivers counts packets filtered by hardware (e.g., not addressed to this MAC), not truly lost packets. Always correlate with `netstat -s` (TCP retransmits) and application-level metrics to understand actual impact. |

---

### Failure Modes & Diagnosis

**Network performance diagnosis:**
```bash
# Symptom: network throughput far below link speed
# Complete diagnosis:

# Step 1: Baseline test:
iperf3 -c server_ip -t 30 -P 4
# Record: actual_bps vs link_speed

# Step 2: Check NIC drops:
ethtool -S eth0 | grep -i "drop\|error\|miss"
# If rx_dropped > 0: ring buffer too small or CPU can't keep up
# Fix: ethtool -G eth0 rx 4096; check CPU load

# Step 3: Check socket buffer limits:
sysctl net.ipv4.tcp_rmem net.ipv4.tcp_wmem
# Compare max (3rd value) vs BDP (bandwidth * RTT / 8)
# If max << BDP: increase

# Step 4: Check CPU distribution:
mpstat -P ALL 1 3
# If one CPU at 100% (softirq): RSS not configured
# Fix: ethtool -L eth0 combined $(nproc)

# Step 5: Check TCP retransmits:
netstat -s | grep -i retransmit
# retransmitted: 12345 <- high = packet loss somewhere
# Fix: investigate network path, consider BBR

# Step 6: Check qdisc drops:
tc -s qdisc show dev eth0
# qdisc mq 0: root
#   Sent X bytes Y pkts (dropped Z, ...)
# Drops in qdisc = TX queue full (outgoing packet loss)
# Fix: increase txqueuelen: ip link set eth0 txqueuelen 10000

# Symptom: low-latency service has high jitter
# Check interrupt coalescing:
ethtool -c eth0
# rx-usecs: 100  <- 100us interrupt delay adds to latency!
# For latency-sensitive (trading, VoIP):
ethtool -C eth0 adaptive-rx off rx-usecs 0 tx-usecs 0

# Check CPU C-states (power management adds latency):
cat /sys/devices/system/cpu/cpu0/cpuidle/state*/name
# C0, C1, C2, C6  <- deep C-states add wakeup latency
# Disable deep C-states for latency-critical:
# kernel cmdline: intel_idle.max_cstate=1
```

---

### Related Keywords

**Foundational:**
LNX-037 (Networking fundamentals), LNX-039 (TCP/IP protocol)

**Builds on this:**
LNX-085 (XDP, kernel bypass), LNX-093 (Performance troubleshooting)

**Related:**
LNX-091 (Traffic control), LNX-092 (Network namespaces)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ethtool -g eth0` | View NIC ring buffer sizes |
| `ethtool -G eth0 rx 4096` | Set ring buffer size |
| `ethtool -k eth0` | View NIC offloading features |
| `ethtool -S eth0 \| grep drop` | NIC-level drop statistics |
| `ethtool -l eth0` | View/set number of NIC queues |
| `sysctl net.ipv4.tcp_congestion_control` | Current CC algorithm |
| `sysctl -w ... = bbr` | Enable BBR |
| `iperf3 -c server -P 4 -t 30` | Bandwidth test |
| `ss -s` | Socket statistics summary |

**3 things to remember:**
1. Bandwidth-delay product (BDP) = bandwidth x RTT: your socket buffer must be >= BDP to fill a pipe; default 6MB is too small for 10Gbps+100ms
2. BBR = better than CUBIC on lossy/high-latency links; enable with `sysctl net.ipv4.tcp_congestion_control=bbr` + `net.core.default_qdisc=fq`
3. Check NIC drops first: `ethtool -S eth0 | grep drop`; high values mean ring buffer too small or CPU can't keep up

---

### Transferable Wisdom

Bandwidth-delay product (BDP) is the key insight: for maximum throughput,
in-flight data must equal BDP. Same principle: (1) TCP window scaling,
(2) Kubernetes concurrent reconciliation workers, (3) database connection
pool sizing (enough connections to keep all CPUs busy), (4) thread pool
sizing (enough threads to keep all cores busy while waiting for I/O).
The interrupt coalescing trade-off (batch more = higher throughput but
higher latency) appears in: database write coalescing (write journal
batches for throughput vs fsync per-write for durability), Kafka producer
`linger.ms` (wait to batch messages vs send immediately), SQS long polling
(wait for messages vs poll immediately). NIC offloading (TSO/GRO: do less
work in kernel, let specialized hardware handle it) is the same principle
as: GPU compute offloading, AWS Nitro for I/O, SmartNIC DPU offloading.
BBR's model-based approach (estimate bandwidth + RTT, operate at that rate)
vs CUBIC's reactive approach (detect loss, react) maps to: proactive vs
reactive monitoring (predict failures vs respond to failures), SLO-based
alerting vs threshold alerting.

---

### The Surprising Truth

TCP's default socket buffer size (87KB on Linux) was originally sized for
10Mbps Ethernet in the 1990s. The buffer was designed to hold one "pipe
full" of data at that speed and RTT (10Mbps * 1ms RTT = 1.25KB). As Ethernet
speeds grew 1000x (10Gbps), the buffer grew only 87x (from 1KB to 87KB),
creating a massive mismatch. On a 10Gbps link with a 100ms cross-continent
RTT: the bandwidth-delay product is 125MB. With an 87KB buffer: you're
using less than 0.07% of link capacity. This is why naive file transfers
between datacenters are so slow - not because of bandwidth, but because
default kernel settings are locked in the 1990s. The solution (increase
`net.core.rmem_max` and `net.ipv4.tcp_rmem`) was known since at least 2003,
but most Linux distributions still ship with 1990s-era defaults. Google,
cloud providers, and high-performance computing sites all tune these settings
as a first-day operation. The BBR paper (2016) showed that YouTube server
performance improved by 4% globally and 14% for connections from Japan
after switching from CUBIC to BBR - purely from a congestion control
algorithm change, no hardware upgrade required.

---

### Mastery Checklist

- [ ] Can use `ethtool` to inspect ring buffers, offloads, and NIC statistics
- [ ] Understands bandwidth-delay product and can calculate required socket buffer sizes
- [ ] Can enable TCP BBR and knows when it's beneficial vs CUBIC
- [ ] Can use `iperf3` to benchmark throughput and identify bottlenecks
- [ ] Knows how to enable RSS for multi-queue NICs to distribute interrupt load

---

### Think About This

1. You have two datacenters 100ms RTT apart, connected by a 10Gbps dedicated
   link. Your application does large file replication and achieves only 800Mbps
   consistently. Calculate the BDP, explain why the default Linux settings
   cause this limitation, write the exact `sysctl` commands to fix it, and
   estimate the expected throughput improvement.

2. A high-frequency trading application requires sub-100 microsecond network
   latency for market data reception. The server has an Intel X710 25GbE NIC.
   Walk through each layer of network performance optimization: what interrupt
   coalescing setting do you use and why, what about C-states, NUMA topology
   for IRQ affinity, and whether TSO/GRO should be enabled or disabled?

3. You're choosing between TCP CUBIC and BBR for a video streaming platform
   serving global users. 30% of users are on mobile networks (1-3% packet
   loss typical). 50% are on broadband (< 0.1% loss). 20% are on enterprise
   networks (very low loss, low RTT). Explain the expected performance of each
   algorithm for each user segment and make a recommendation.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the bandwidth-delay product and why do default Linux TCP settings limit performance on high-speed WAN links?
A: The bandwidth-delay product (BDP) is the amount of data that can be "in flight" on a network path to keep the pipe full: BDP = bandwidth (bits/second) * RTT (seconds) / 8 (bits per byte). EXAMPLE: 1Gbps link, 100ms RTT: BDP = 1e9 * 0.1 / 8 = 12.5MB. For the sender to transmit at 1Gbps continuously: 12.5MB must always be in-flight (waiting for ACKs). TCP flow control: the receiver advertises a receive window. The sender cannot have more than window bytes unacknowledged. If window < BDP: sender exhausts the window, stops sending, waits for ACK (idle time). DEFAULT LINUX LIMITS: `net.core.rmem_max = 212992` (~208KB). `net.ipv4.tcp_rmem max = 6291456` (6MB). TCP autotune can grow up to the max: 6MB. 6MB / 12.5MB = 48% utilization (sender is idle 52% of time!). FIX: `net.core.rmem_max = 134217728` (128MB). `net.ipv4.tcp_rmem = "4096 87380 134217728"` (128MB max). TCP autotune now grows window to fill the BDP. VERIFICATION: `iperf3 -c server -w 64M -t 30`. Before: 480Mbps. After: 980Mbps. HISTORY: Linux default was set for 10Mbps LAN in the 1990s. Never updated as speeds grew. Cloud providers and HPC systems always tune these. It's a first-day optimization for any high-bandwidth server.

**Expert:**
Q: How does TCP BBR work differently from CUBIC, and what are the scenarios where each performs better?
A: CUBIC and BBR are TCP congestion control algorithms with fundamentally different models of network capacity. CUBIC MECHANISM: Loss-based congestion control. Algorithm: start with small cwnd, increase cubically (hence the name). When packet loss (duplicate ACKs or RTO) is detected: halve cwnd (multiplicative decrease). Continue increasing until next loss event. MODEL: the bottleneck capacity is found by probing to packet loss. PROBLEM: in lossy networks (WiFi 1-2% loss, LTE 1-5% loss), CUBIC halves its window on random losses, achieving far below available bandwidth. On a link with 2% random loss: CUBIC's throughput is proportional to 1/sqrt(loss_rate) - at 2% loss: ~50% of available bandwidth. BBR MECHANISM: Model-based. Maintains two estimates: BtlBw (bottleneck bandwidth - measured delivery rate during bandwidth probing phases) and RTprop (minimum RTT - measured when rate is reduced). Pacing rate = BtlBw. cwnd = BtlBw * RTprop * 2 (to allow some in-flight data). State machine: STARTUP (exponential probing), DRAIN (reduce backlog), PROBE_BW (steady state with periodic bandwidth probing), PROBE_RTT (reduce rate to measure minimum RTT). KEY DIFFERENCE: BBR decouples bandwidth estimation from loss. A random lost packet doesn't reduce BBR's estimated bandwidth. WHEN BBR WINS: (1) Lossy networks: maintains bandwidth while CUBIC cuts. (2) High BDP: BBR's startup fills the pipe faster. (3) Inter-DC links: random loss in long optical paths. WHEN CUBIC WINS: (1) Zero-loss LAN: both algorithms fill the pipe; CUBIC is simpler. (2) Mixed environments: BBR can be unfair to CUBIC flows (BBR probes bandwidth aggressively, crowding out CUBIC). WHEN NEITHER IS OPTIMAL: Short flows (connection completes before either algorithm reaches steady state). BBR v2 (kernel 5.13+) improves fairness in mixed environments via loss-based cwnd reduction when loss is detected.
