---
layout: default
title: "Linux Networking (ip, ss, netstat)"
parent: "Linux"
nav_order: 147
permalink: /linux/linux-networking/
number: "0147"
category: Linux
difficulty: ★★☆
depends_on: Networking, Linux File System Hierarchy, /proc File System
used_by: Observability & SRE, iptables / nftables, Linux Security Hardening
related: iptables / nftables, tcpdump / Wireshark, SSH
tags:
  - linux
  - networking
  - os
  - intermediate
---

# 147 — Linux Networking (ip, ss, netstat)

⚡ TL;DR — `ip` configures network interfaces, routes, and policies; `ss` shows socket state; `netstat` (legacy) shows connections — together they are the command-line toolkit for diagnosing Linux network issues.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A service is unreachable. Is the interface down? Is the route missing? Is the port not listening? Is the connection being dropped? Without network diagnostic tools you'd be guessing — restarting services blindly and waiting for the problem to reappear. Each network layer requires a different inspection tool; without a unified toolkit, diagnosing multi-layer issues takes hours.

**THE BREAKING POINT:**
Production: a microservice suddenly can't reach its database. The database is running. The application is running. No errors in application logs. Without tools to inspect routing tables, socket states, and interface statistics, the root cause — a misconfigured route added by a colleague — is invisible.

**THE INVENTION MOMENT:**
This is exactly why Linux networking tools were created. `ip route show` reveals the missing route in 2 seconds. `ss -tnp` shows whether the application has established TCP connections to the DB. `ip link show` reveals a flapping interface. The tools make invisible network state visible.

---

### 📘 Textbook Definition

`ip` (from the `iproute2` package) is the modern Linux tool for configuring and inspecting network interfaces, routing tables, ARP/NDP caches, and network policies. It replaces the deprecated `ifconfig`, `route`, and `arp` commands. `ss` (socket statistics) queries the kernel's socket table via netlink and displays socket state, addresses, ports, and owning processes — faster and more capable than `netstat`. `netstat` (from `net-tools`) is the legacy tool for connection and interface statistics, still widely found on older systems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`ip` configures network settings; `ss` shows what's connected; together they give complete visibility into Linux network state.

**One analogy:**

> `ip` is the city's traffic department — it sets road signs (routes), opens and closes lanes (interfaces), and manages traffic rules (policies). `ss` is a traffic camera operator who can show you every car currently on every road, which road it came from, and where it's going. `netstat` is an older traffic log book — shows similar info but requires more manual page flipping.

**One insight:**
`netstat` reads `/proc/net/tcp` and `/proc/net/udp` — text files it must parse for every invocation. `ss` uses the netlink socket API to query kernel data structures directly, making it 10-100× faster on systems with thousands of connections. On high-traffic servers, `netstat -an` can take 30 seconds; `ss -an` takes under a second.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Network state (interfaces, routes, sockets) is maintained entirely in the kernel.
2. User-space tools are simply translators between kernel data structures and human-readable output.
3. All configuration (adding routes, IPs) is temporary by default — it lives in kernel memory and is lost on reboot.

**DERIVED DESIGN:**
Linux networking is implemented in the kernel's net/ subsystem. Network interfaces are `net_device` structs; routing tables are `rtable` radix trees; sockets are `sock` structs. `iproute2`'s `ip` command communicates with the kernel via netlink sockets (AF_NETLINK) — a message-passing interface that replaces the older ioctl-based approach. This allows structured, extensible queries and configuration without parsing text files.

`ss` uses `NETLINK_SOCK_DIAG` messages to dump socket tables directly from kernel data structures — bypassing the text serialisation that makes `/proc/net/tcp` parsing slow.

**THE TRADE-OFFS:**
**Gain:** Complete visibility into all network state; configuration without editing files; instant feedback.
**Cost:** All `ip` changes are lost on reboot unless persisted to `/etc/network/interfaces`, NetworkManager, or systemd-networkd; complex routing policies require careful rule ordering.

---

### 🧪 Thought Experiment

**SETUP:**
Your server has two NICs: `eth0` (public, 10.0.0.1) and `eth1` (private, 192.168.1.1). Traffic arriving on `eth1` needs to be routed back via `eth1`, not `eth0` (asymmetric routing issue).

**WHAT HAPPENS WITHOUT policy routing:**
A packet arrives on `eth1` from `192.168.1.100`. The kernel looks up its routing table: the default route is via `eth0`. The reply goes out `eth0` from a different IP. The remote host rejects the reply (wrong source address). Connection fails silently.

**WHAT HAPPENS WITH `ip rule` + `ip route`:**

```bash
# Create a separate routing table for eth1 traffic
ip route add default via 192.168.1.254 table 100
# Rule: packets from eth1's network use table 100
ip rule add from 192.168.1.0/24 lookup 100
```

Now replies for `eth1` traffic use the `eth1` gateway. Symmetric routing is restored. This is impossible to configure without `ip`'s policy routing support.

**THE INSIGHT:**
Linux routing is not just a routing table — it is a set of rules (`ip rule`) that select which routing table to consult. Visualising this multi-layer system requires `ip route show` and `ip rule show` together.

---

### 🧠 Mental Model / Analogy

> Think of Linux networking as a post office. `ip link` manages the receiving windows (interfaces — open or closed). `ip addr` manages the addresses on each window (which postal codes each window serves). `ip route` manages the sorting charts (which postal code goes to which lorry bay). `ss` is the parcel tracker — it shows every parcel (connection) currently in the system, which window it came through, and where it's headed.

- "Receiving windows" → network interfaces
- "Postal codes per window" → IP addresses per interface
- "Sorting charts" → routing table
- "Parcel tracker" → ss socket state display

Where this analogy breaks down: a real post office is shared between all senders; Linux has per-namespace network stacks — each container can have a completely separate "post office" via network namespaces.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`ip` is the tool for configuring network settings on Linux — turning interfaces on/off, setting IP addresses, and telling the computer where to send traffic. `ss` shows all open network connections, like Task Manager for network connections.

**Level 2 — How to use it (junior developer):**
`ip addr show` lists all interfaces and their IPs. `ip route show` shows the routing table (where traffic goes). `ss -tnp` shows TCP connections with the process using each. `ss -tlnp` shows which ports are listening. Replace `netstat -an` with `ss -an` on modern systems. `ip link set eth0 up/down` enables/disables an interface.

**Level 3 — How it works (mid-level engineer):**
`ip` communicates with the kernel via RTM_GETADDR, RTM_GETROUTE, RTM_GETLINK netlink messages. Each `ip` subcommand maps to specific netlink message types. Routing lookup uses a radix trie (FIB — Forwarding Information Base) keyed on destination prefix. `ss` uses `sock_diag` netlink messages to dump socket tables — it can filter by state, address, port, and process without loading all sockets into user-space first. The `-o` flag in `ss` shows socket timer state (retransmit timers, keepalive timers) useful for diagnosing connection hangs.

**Level 4 — Why it was designed this way (senior/staff):**
`iproute2` replaced the ancient `net-tools` package because `net-tools` used ioctl() for everything — a binary, unversioned interface that couldn't be extended without breaking compatibility. Netlink provides a structured, versioned, extensible message-passing interface. The `ip` command's subcommand structure (`ip link`, `ip addr`, `ip route`, `ip rule`, `ip neigh`) directly maps to netlink subsystems. The `ss` tool's speed advantage comes from requesting only the data needed (filtered dump) rather than dumping all sockets and filtering in user-space like `netstat` does.

---

### ⚙️ How It Works (Mechanism)

**Key `ip` commands:**

```bash
# Interface management
ip link show              # list all interfaces
ip link show eth0         # show specific interface
ip link set eth0 up       # bring up
ip link set eth0 down     # bring down
ip link set eth0 mtu 9000 # set jumbo frames

# IP address management
ip addr show              # list all IPs
ip addr show eth0         # IPs on eth0
ip addr add 10.0.0.2/24 dev eth0  # add IP
ip addr del 10.0.0.2/24 dev eth0  # remove IP
ip addr flush dev eth0    # remove all IPs from interface

# Routing
ip route show             # show routing table
ip route show default     # show default gateway
ip route add default via 10.0.0.1  # add default gateway
ip route add 192.168.2.0/24 via 10.0.0.1  # add specific route
ip route del 192.168.2.0/24       # delete route
ip route get 8.8.8.8       # show route to specific destination

# ARP/neighbor cache
ip neigh show             # show ARP table
ip neigh flush dev eth0   # flush ARP cache

# Network namespaces
ip netns list             # list network namespaces
ip netns exec myns ip addr show  # run cmd in namespace
```

**Key `ss` commands:**

```bash
# Show all TCP connections (established)
ss -tn                    # no process info
ss -tnp                   # with process info (needs root)

# Show listening ports
ss -tlnp                  # TCP listening with process
ss -ulnp                  # UDP listening with process

# Filter by port
ss -tnp sport = :443      # connections on port 443
ss -tnp dport = :5432     # connections TO port 5432

# Show socket timer info (retransmit, keepalive)
ss -tnpo state established

# Count connections by state
ss -tan | awk 'NR>1 {count[$1]++}
  END {for (s in count) print s, count[s]}'

# Show unix domain sockets
ss -xnp

# All sockets summary
ss -s
```

**ss connection states:**

```
ESTABLISHED  — Active connection
SYN_SENT     — Client initiated, waiting for SYN-ACK
SYN_RECV     — Server received SYN, sent SYN-ACK
FIN_WAIT1    — Sent FIN, waiting
FIN_WAIT2    — Received ACK of FIN, waiting for remote FIN
TIME_WAIT    — Waiting for all packets to expire (2×MSL)
CLOSE_WAIT   — Remote closed, local has not yet
LAST_ACK     — Waiting for final ACK
LISTEN       — Accepting new connections
CLOSED       — No connection
```

**Legacy `netstat` equivalents:**

```bash
netstat -an     → ss -an
netstat -tnp    → ss -tnp
netstat -rn     → ip route show
netstat -i      → ip -s link show
netstat -s      → ss -s (or cat /proc/net/snmp)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  DIAGNOSING: "can't reach DB on port 5432"  │
└─────────────────────────────────────────────┘

 Problem reported
       │
       ▼
 ip link show         ← interface up? ← YOU ARE HERE
       │  ✓ eth0: state UP
       ▼
 ip addr show eth0
       │  ✓ 10.0.1.5/24 assigned
       ▼
 ip route get 10.0.2.100
       │  ✓ via 10.0.0.1 dev eth0
       ▼
 ss -tnp dport = :5432
       │  No output → nothing connected to DB
       ▼
 ss -tlnp | grep 5432 (on DB server)
       │  ✓ DB IS listening
       ▼
 tcpdump -i eth0 host 10.0.2.100 port 5432
       │  SYN sent but no SYN-ACK
       ▼
 → iptables / firewall blocking traffic
       │
       ▼
 iptables -L -n | grep 5432
       → REJECT rule found → root cause!
```

**FAILURE PATH:**
`ip route get <destination>` returns "unreachable" → no route to host → check default gateway or add specific route.

**WHAT CHANGES AT SCALE:**
In Kubernetes, each pod has its own network namespace — `ip` commands run inside a pod see only that pod's interfaces and routes. Cluster-level routing is handled by kube-proxy or a CNI plugin (Calico, Cilium). Network debugging shifts from host-level `ss`/`ip` to kubectl-level tools (`kubectl exec`, `kubectl port-forward`) and network plugin diagnostics.

---

### 💻 Code Example

**Example 1 — Network diagnostic script:**

```bash
#!/bin/bash
# Quick network health check for a target host/port
TARGET_HOST=${1:-8.8.8.8}
TARGET_PORT=${2:-443}

echo "=== Interface Status ==="
ip -br link show    # brief one-line per interface

echo ""
echo "=== IP Addresses ==="
ip -br addr show    # brief IP addresses

echo ""
echo "=== Default Routes ==="
ip route show default

echo ""
echo "=== Route to $TARGET_HOST ==="
ip route get "$TARGET_HOST"

echo ""
echo "=== Listening Ports ==="
ss -tlnp | grep -v "State"

echo ""
echo "=== Connection Count by State ==="
ss -tan | awk 'NR>1 {count[$1]++}
  END {for (s in count) print s, count[s]}' | sort
```

**Example 2 — Detect TIME_WAIT accumulation:**

```bash
# Check for TIME_WAIT socket exhaustion
# (common cause of "connection refused" on high-traffic servers)
TW_COUNT=$(ss -tan state time-wait | wc -l)
echo "TIME_WAIT sockets: $TW_COUNT"

# Check local port range (max ephemeral ports)
cat /proc/sys/net/ipv4/ip_local_port_range

# If TIME_WAIT is high relative to port range, tune:
# Enable port reuse for TIME_WAIT sockets
echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
```

**Example 3 — Monitor interface errors:**

```bash
#!/bin/bash
# Alert on interface error spikes
NIC=eth0
THRESHOLD=100

while true; do
  errors=$(ip -s link show $NIC | \
    awk '/RX:/{getline; print $3}')
  if [ "$errors" -gt "$THRESHOLD" ]; then
    echo "ALERT: $NIC has $errors RX errors!" >&2
  fi
  sleep 60
done
```

---

### ⚖️ Comparison Table

| Tool     | Backend          | Speed (10k conns) | Process Names | Best For               |
| -------- | ---------------- | ----------------- | ------------- | ---------------------- |
| **ss**   | netlink (kernel) | < 1 second        | Yes (-p flag) | Modern Linux debugging |
| netstat  | /proc/net/ parse | 30+ seconds       | Yes (-p flag) | Legacy systems         |
| **ip**   | netlink          | Instant           | N/A           | Interface/route config |
| ifconfig | ioctl            | Fast              | No            | Legacy interface info  |
| route    | /proc/net/route  | Fast              | No            | Legacy routing display |
| lsof -i  | /proc scanning   | Slow              | Yes           | Cross-platform         |

How to choose: always use `ss` instead of `netstat` on modern systems; always use `ip` instead of `ifconfig`/`route`; use `lsof -i` only when you need cross-platform compatibility.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ip route show` displays all routing rules     | `ip route show` shows one routing table; full policy routing requires `ip rule show` to see which table is consulted for which traffic                 |
| TIME_WAIT sockets mean the server is broken    | TIME_WAIT is normal and healthy — it prevents old packets from corrupting new connections; excessive TIME_WAIT may indicate connection pool exhaustion |
| `ip addr add` changes are permanent            | All `ip` commands modify kernel state in memory; changes are lost on reboot unless configured in network manager or `/etc/network/interfaces`          |
| `ss -tnp` shows all processes for a connection | `-p` shows the process owning the socket; for connections shared across fork'd processes, only one PID is shown                                        |
| netstat is deprecated everywhere               | netstat is deprecated on Linux (replaced by ss) but still the standard tool on macOS, BSD, and Windows                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Route Missing After Reboot**

**Symptom:**
A static route added with `ip route add` works until the next reboot, then disappears.

**Root Cause:**
`ip route add` modifies only the running kernel state; it is not persisted anywhere automatically.

**Diagnostic Command:**

```bash
ip route show  # verify current routes
# Check if route is in persistent config
grep -r "route" /etc/network/ /etc/sysconfig/network-scripts/ \
  /etc/netplan/ 2>/dev/null
```

**Fix:**
Add to the appropriate network configuration file for your distro:

```yaml
# Ubuntu/Debian: /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:
      routes:
        - to: 192.168.2.0/24
          via: 10.0.0.1
```

**Prevention:**
Never add production routes with bare `ip route add`; always add to network config and test with `netplan apply` or `systemctl restart networking`.

---

**Port Shows LISTEN but Connection Refused**

**Symptom:**
`ss -tlnp | grep 8080` shows the port is listening, but `curl http://localhost:8080` returns "connection refused".

**Root Cause:**
The service is listening on `127.0.0.1:8080` (loopback only) but the connection is attempted from a different interface, or a firewall rule is rejecting the connection before it reaches the socket.

**Diagnostic Command:**

```bash
# Check what address the port is bound to
ss -tlnp | grep 8080
# "127.0.0.1:8080" = loopback only
# "0.0.0.0:8080" = all interfaces
# ":::8080" = all IPv6 interfaces

# Check firewall
iptables -L INPUT -n | grep 8080
```

**Fix:**
Configure the service to bind to `0.0.0.0` (all interfaces) or the specific external interface address.

**Prevention:**
Always verify the bind address with `ss -tlnp` after starting a service; test from both loopback and external addresses.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Networking` — TCP/IP, OSI model, and routing concepts are required to understand what these tools display
- `Linux File System Hierarchy` — `/proc/net/` is the data source for legacy tools; `/sys/class/net/` exposes interface stats
- `/proc File System` — understanding that `netstat` reads `/proc/net/tcp` explains its performance characteristics

**Builds On This (learn these next):**

- `iptables / nftables` — packet filtering rules that affect what `ss` shows (connections being blocked)
- `tcpdump / Wireshark` — captures packets for deeper analysis when `ip`/`ss` shows a problem but not the root cause
- `Linux Security Hardening` — uses `ss` to audit open ports and `ip` to configure network access controls

**Alternatives / Comparisons:**

- `tcpdump` — packet capture for deep inspection vs `ss`/`ip` which show state without packet content
- `nmap` — external network scanning vs `ss`/`ip` which are local host inspection tools
- `Wireshark` — GUI packet analyser for complex protocol debugging

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ ip: network config tool; ss: socket       │
│              │ state viewer — both use netlink kernel API│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Network issues had no unified inspection  │
│ SOLVES       │ tool; each layer required separate legacy │
│              │ command with different syntax             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ss is 100× faster than netstat because    │
│              │ it uses netlink, not /proc text parsing   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing connectivity issues, auditing  │
│              │ open ports, configuring routing           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Making permanent network changes — always │
│              │ persist to network config files           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ ip changes are instant but ephemeral;     │
│              │ config file changes survive reboot        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "ip is the traffic department;            │
│              │  ss is the live traffic camera"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ iptables → tcpdump → network namespaces  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A server running 50,000 concurrent TCP connections shows high CPU usage from a monitoring agent running `netstat -an` every 5 seconds. Trace the exact system calls and kernel operations `netstat` performs to produce its output versus what `ss` performs, and calculate the approximate performance difference. At what connection count does this difference become a real operational problem?

**Q2.** In a Kubernetes cluster, a pod cannot reach a service by its ClusterIP. `ip route show` inside the pod shows the route exists. `ss -tnp` shows no connections established. `tcpdump` shows SYN packets leaving the pod but no response. The service has 3 healthy endpoints according to `kubectl get endpoints`. Trace the complete data path from pod IP to service IP, identify the two most likely failure points in kube-proxy/iptables/CNI, and describe the exact commands that would distinguish between them.
