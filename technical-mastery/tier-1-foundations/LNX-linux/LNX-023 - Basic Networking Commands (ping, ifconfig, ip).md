---
id: LNX-023
title: "Basic Networking Commands (ping, ifconfig, ip)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★☆☆
depends_on: LNX-006
used_by: LNX-034, LNX-045
related: LNX-034, LNX-045, NET-001
tags: [ping, ifconfig, ip, networking, diagnostics, IP-address, network-troubleshooting]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/lnx/basic-networking-commands/
---

## TL;DR

Three commands cover basic network diagnostics: `ping` (is the
host reachable?), `ip addr` (what IP addresses do I have?),
`ip route` (how do I reach other networks?). `ifconfig` is the
older alternative to `ip addr`. `traceroute` shows the network
path. In production troubleshooting: ping to test connectivity,
`ip addr` to verify interface configuration, `ss -tlnp` to see
what's listening on which port.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-023 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Linux |
| **Tags** | ping, ifconfig, ip addr, ip route, traceroute, network diagnosis |
| **Prerequisites** | LNX-006 |

---

### The Problem This Solves

Server not responding to requests. Is the network down? Is my server's
IP configured correctly? Can I reach the database server? Is my
application even listening on the expected port? These questions need
answers at 3am with a production outage. Basic networking commands
provide the initial triage: yes/no connectivity, IP configuration,
port status. Without them, you're debugging blind.

---

### Textbook Definition

**ping**: Sends ICMP Echo Request packets to a target host and measures
response time. Tests basic IP-layer reachability. Does NOT test if a
specific port/service is available (firewalls can block ping but allow
TCP 80).

**ip addr** (iproute2): Shows and manages network interface addresses.
Modern replacement for `ifconfig`. Part of the `ip` command suite
(also: `ip route`, `ip link`, `ip neigh`).

**ifconfig**: Old-style network configuration tool (net-tools package).
Deprecated on modern Linux but still widely used. On many minimal
installations, only `ip` is available.

**traceroute**: Shows the path packets take through the network (each
router hop). Useful for finding where connectivity breaks.

---

### Understand It in 30 Seconds

```bash
# Test connectivity:
ping 8.8.8.8               # ping Google's DNS (Ctrl+C to stop)
ping -c 4 server.example.com  # send exactly 4 packets
ping -W 2 host             # 2 second timeout per packet

# Show IP addresses (modern):
ip addr                    # all interfaces and their IPs
ip addr show eth0          # specific interface
ip a                       # shorthand

# Show routes:
ip route                   # routing table
ip route show default      # just the default route (gateway)

# Old style (ifconfig):
ifconfig                   # show active interfaces
ifconfig -a                # show all interfaces including down ones
ifconfig eth0              # specific interface

# What's listening on which port:
ss -tlnp                   # TCP + listening + numeric + process info
ss -ulnp                   # UDP listening
netstat -tlnp              # older alternative (may need net-tools)

# Trace network path:
traceroute google.com
tracepath google.com       # similar, no root required
mtr google.com             # real-time traceroute (modern, interactive)
```

---

### First Principles

**Why ping doesn't prove everything:**
ping uses ICMP (Internet Control Message Protocol). Many firewalls
block ICMP while allowing TCP traffic. A host can be unreachable via
ping but completely functional for HTTP/HTTPS. Conversely, ping can
succeed while port 8080 (your app) is blocked by a firewall.
ping confirms: "IP-level packet delivery works between these two points."
It does NOT confirm: "The service I want to use is accessible."

**Network interface types:**
- `lo` (loopback): 127.0.0.1 - virtual interface, communicates with yourself
- `eth0`, `ens3`, `enp3s0`: physical Ethernet or virtual NIC
- `wlan0`: WiFi
- `docker0`: Docker bridge network (created by Docker daemon)
- `veth*`: virtual Ethernet pairs (one end in container, one in host)
- `virbr0`: libvirt virtual bridge (for VMs)

---

### Thought Experiment

Your Java application cannot connect to the database. Triage flow:

```
Step 1: Can I reach the database server's IP at all?
  ping 10.0.1.50    -> if NO: network layer problem (routing, firewall)
                    -> if YES: IP connectivity works

Step 2: Can I reach the database port?
  nc -zv 10.0.1.50 5432    -> tests TCP connectivity to port 5432
  # or: telnet 10.0.1.50 5432

Step 3: Is the database actually listening?
  ssh 10.0.1.50 "ss -tlnp | grep 5432"   # check on the DB server

Step 4: Is my server's IP correct?
  ip addr    -> verify my server has the expected IP

Step 5: Can I route to the DB subnet?
  ip route   -> verify route to 10.0.1.0/24 exists

This systematic approach finds the problem layer by layer.
```

---

### Mental Model / Analogy

Network commands are like **progressively detailed postal service checks:**

```
ping = "Did my letter arrive at the right country?" (IP reachability)
  Yes/No: can packets reach the IP address
  
ip addr = "What address is on my building?" (local IP config)
  Shows: your IP addresses, masks, interfaces
  
ip route = "Which roads lead from here to other places?" (routing)
  Shows: how to reach other networks (via which gateway/interface)
  
traceroute = "Show me every post office my letter passed through"
  Shows: each router hop between you and the destination
  
ss -tlnp = "Is the post office actually open and accepting mail?"
  Shows: which ports are open and what programs are listening
  
nc -zv host port = "Can I physically hand a letter to that address?"
  Tests TCP connection to a specific port
```

---

### Gradual Depth - Five Levels

**Level 1:**
ping = connectivity test. ip addr = my IP addresses. ip route = routing.
ss -tlnp = what's listening. These 4 commands handle 80% of basic
network troubleshooting.

**Level 2:**
`ip route get 8.8.8.8` = which interface/gateway would be used to reach
that IP. `ip neigh` = ARP table (who's at which MAC address on local
network). `nmap -p 80,443 host` = port scan (check if ports are open
from outside). `curl -v http://host` = full HTTP transaction debug.

**Level 3:**
`ss -tlnp` output interpretation: Local Address:Port shows what IP
and port the service is listening on. `0.0.0.0:8080` = listening on
ALL interfaces. `127.0.0.1:8080` = listening only on loopback (not
accessible from outside). `:::8080` = IPv6 any-address. Service bound
to 0.0.0.0 is externally accessible; 127.0.0.1 is local-only.

**Level 4:**
`ip link` = Layer 2 info (MAC address, MTU, interface state UP/DOWN).
`ethtool eth0` = physical link speed, duplex, auto-negotiation. `arp -n`
= ARP cache. `tcpdump -i eth0 port 80` = capture and display packets.
`wireshark` (GUI) = packet capture with analysis. These are for deep
networking issues beyond basic connectivity.

**Level 5:**
Container networking: Docker creates `docker0` bridge and veth pairs.
`ip link show` shows all veth interfaces. `nsenter -t PID -n ip addr`
shows IP from inside a container's network namespace. Kubernetes:
each pod has its own network namespace with a unique IP. CNI plugins
(Calico, Flannel, Cilium) implement pod networking. For troubleshooting
k8s networking: kubectl exec into a debug container with network tools.

---

### Code Example

**BAD - incomplete network diagnosis:**
```bash
# BAD 1: only pinging to diagnose "connection refused"
ping myapp.example.com
# PING succeeds (IP reachable), but the issue is:
# - Application not listening on port 8080
# - Firewall blocking port 8080
# Ping success doesn't mean application is accessible!

# BAD 2: using ifconfig on modern systems (not available or deprecated)
ifconfig    # may not be installed; output format is harder to parse
# Use: ip addr

# BAD 3: not checking what IP the service is bound to
ss -tlnp    # shows service listening on 127.0.0.1:8080
# External clients try to reach public-IP:8080
# Connection refused! Because bound to localhost only
# Fix: bind to 0.0.0.0:8080 (or the specific public IP)
```

**GOOD - systematic network troubleshooting:**
```bash
# GOOD 1: complete connectivity triage
# Is the host reachable?
ping -c 4 10.0.1.50
# Can I reach the specific port?
nc -zv 10.0.1.50 8080    # -z=don't send data, -v=verbose
# Or using bash (no nc needed):
timeout 3 bash -c "echo >/dev/tcp/10.0.1.50/8080" && echo "Port open" || echo "Port closed"

# GOOD 2: verify interface configuration
ip addr show   # check IP, prefix length, state
# Look for: inet 10.0.1.100/24 (IP + subnet mask in CIDR notation)
# State should be: state UP

# GOOD 3: verify routing
ip route
# Should see: default via 10.0.1.1 dev eth0 (default gateway)
# And: 10.0.1.0/24 dev eth0 (local subnet route)

# GOOD 4: check what's actually listening
ss -tlnp    # check: is app listening on expected port?
# Example output:
# LISTEN  0  128  0.0.0.0:8080  0.0.0.0:*  users:(("java",pid=1234,fd=12))
# This means: java (PID 1234) is listening on ALL interfaces, port 8080

# GOOD 5: check from external perspective
# On your local machine (not the server):
curl -v http://server-ip:8080/health    # full HTTP debug
# -v = verbose (shows TCP connection, headers, response)

# GOOD 6: temporary IP assignment for testing
sudo ip addr add 10.0.1.200/24 dev eth0  # add temporary IP
# After test:
sudo ip addr del 10.0.1.200/24 dev eth0  # remove it
```

---

### Reading ip addr Output

```
$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo        <- loopback IP
    inet6 ::1/128 scope host              <- IPv6 loopback

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
    ^   ^              ^   ^               ^            ^
    |   IP address     |   Broadcast       |            Interface
    |                  |                   scope=global = routable
    |                  prefix length /16 = 255.255.0.0 subnet mask
    inet6 2001:db8::2/64 scope global     <- IPv6 address

Key: state UP = interface is up and running
     LOWER_UP = physical link is detected (cable connected)
     mtu 1500 = max transmission unit (standard Ethernet)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "ping works = service is accessible" | ping tests ICMP reachability (layer 3). Firewalls commonly block ICMP while allowing TCP. A successful ping means IP routing works, not that port 8080 or port 443 is accessible. Use `nc -zv host port` to test specific port connectivity. |
| "ifconfig and ip addr show the same info" | ip addr (iproute2) is the modern replacement for ifconfig (net-tools). ifconfig is deprecated. On minimal systems, only ip is available. ip addr shows more info and is more scriptable. |
| "127.0.0.1 and localhost are always the same" | Typically yes, but `/etc/hosts` maps localhost to 127.0.0.1. This can be overridden. Also: if an app binds to `localhost`, it depends on the hosts file. If you need to guarantee loopback: use `127.0.0.1` directly. |
| "An IP address identifies a computer" | An IP address identifies a NETWORK INTERFACE on a computer. One computer can have multiple interfaces, each with its own IP (or multiple IPs per interface). Servers often have multiple IPs (one per virtual host, one for admin, etc.). |
| "traceroute shows the actual packet path" | traceroute shows a best-effort view. ECMP (equal-cost multipath) routing may send different packets through different paths. Later probes in traceroute may follow a different path than earlier ones. The path can also vary by protocol (ICMP-based traceroute may be blocked while TCP flows go through). |

---

### Failure Modes & Diagnosis

**Application "connection refused" on the server:**
```bash
# Step 1: is the application running?
ps aux | grep java    # check if JVM is running

# Step 2: is it listening on the right port?
ss -tlnp | grep 8080

# Case A: no output (not listening)
# -> Application not started or crashed
# -> Check logs: journalctl -u myapp -n 50

# Case B: 127.0.0.1:8080 (listening on loopback only)
# -> Client trying to reach from outside gets "connection refused"
# -> Fix: configure app to listen on 0.0.0.0:8080 or the public IP
# In Spring Boot: server.address=0.0.0.0 in application.properties

# Case C: 0.0.0.0:8080 (correct) but firewall blocking
# -> Check iptables:
iptables -L INPUT -n | grep 8080
# Or: from outside the server:
nc -zv server-ip 8080   # should succeed
```

**IP address not assigned after reboot:**
```bash
# Problem: server comes up without IP (DHCP failed or static config wrong)
ip addr show eth0
# Shows: no inet line

# Check network config:
# Debian/Ubuntu: /etc/netplan/*.yaml or /etc/network/interfaces
# RHEL: /etc/sysconfig/network-scripts/ifcfg-eth0

# Restart networking:
systemctl restart networking   # Debian
systemctl restart NetworkManager  # RHEL/modern

# Temporary fix (test connectivity):
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip route add default via 192.168.1.1
```

---

### Related Keywords

**Foundational:**
LNX-006 (Terminal)

**Builds on this:**
LNX-034 (Network Tools - curl, wget, netstat, ss),
LNX-045 (Network Configuration)

**Related:**
NET-001 (Networking), NET-002 (TCP/IP)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ping -c 4 host` | Test IP reachability (4 packets) |
| `ip addr` | Show all interface IP addresses |
| `ip addr show eth0` | Show specific interface |
| `ip route` | Show routing table |
| `ip route get 8.8.8.8` | Which route/interface used for IP |
| `ss -tlnp` | TCP listening ports + process names |
| `ss -ulnp` | UDP listening ports |
| `nc -zv host port` | Test TCP port connectivity |
| `traceroute host` | Show network hops to destination |
| `mtr host` | Real-time traceroute |
| `ip link` | Show interface Layer 2 state |

**3 things to remember:**
1. ping success != service accessible (ICMP vs TCP; firewalls treat them differently)
2. `ss -tlnp`: service on 127.0.0.1 = localhost only; 0.0.0.0 = all interfaces
3. Replace `ifconfig` with `ip addr` - ifconfig is deprecated on modern Linux

---

### Transferable Wisdom

The network triage sequence (ping -> port test -> service listen check)
is the same systematic approach used at every scale: from single-server
debugging to cloud infrastructure diagnosis. AWS VPC troubleshooting:
security groups (instance-level firewall) vs NACL (subnet-level) vs
routing tables vs internet gateway - same layered approach, different
tools. Kubernetes service debugging: `kubectl port-forward`, DNS
resolution in cluster, service selector matching pods. The mental
model transfers: test connectivity at each layer until you find where
it breaks.

---

### The Surprising Truth

`ping` was invented in 1983 by Mike Muuss in just a few hours,
inspired by sonar's echo-location concept. He named it after the sound
sonar makes. The `ping` command name is not an acronym - it's purely
onomatopoeia. Muuss stated: "I named it after the sound that a sonar
makes, inspired by the whole principle of echo-location." The ICMP
echo protocol it uses was already defined; Muuss simply wrote the
user-facing tool. Today, ping is the most universally understood
network diagnostic tool across all operating systems, built on a
protocol designed in 1981 (RFC 792) and unchanged in its core
mechanism. Yet many enterprise firewalls block it by default, making
the most basic connectivity test unreliable in real-world environments.

---

### Mastery Checklist

- [ ] Can test basic IP connectivity with ping and interpret the output
- [ ] Can view and interpret IP address configuration with ip addr
- [ ] Can check routing table and explain the default route
- [ ] Can identify what's listening on which port with ss -tlnp
- [ ] Can trace network path with traceroute and identify failure points

---

### Think About This

1. You run `ping myapp.example.com` and it succeeds. But when you try
   `curl http://myapp.example.com:8080`, you get "Connection refused."
   Explain step by step what you would check next and why ping success
   doesn't rule out the problem.

2. `ss -tlnp` shows your application listening on `[::]:8080`. Is this
   IPv6 only, or does it also accept IPv4 connections? How does this
   differ from `0.0.0.0:8080`? What flag controls this behavior in
   most server applications?

3. You're in a Kubernetes pod and want to troubleshoot why your pod
   can't reach a database service. The pod is minimal (Alpine Linux)
   and doesn't have most network tools. What tools ARE likely available
   in a minimal container, and how would you use them to diagnose
   network connectivity?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you check if a remote service is reachable on a specific port from a Linux server?
A: Several approaches: (1) `nc -zv hostname port` - netcat with zero I/O mode and verbose output. Returns immediately with "succeeded" or "failed." (2) `telnet hostname port` - older but widely available. Connection either succeeds or fails. Ctrl+] then quit to exit. (3) Pure bash: `timeout 3 bash -c "echo >/dev/tcp/hostname/port" && echo "open" || echo "closed"` - no external tools needed. (4) `curl -v http://hostname:port` - for HTTP services, shows full transaction. Important: `ping hostname` only tests ICMP (layer 3) connectivity. A successful ping does NOT mean the TCP port is accessible. Firewalls often allow ICMP but block specific ports. Always test the specific port you care about, not just ping.

**Intermediate:**
Q: Your application is running but users can't connect. `ss -tlnp` shows it listening on `127.0.0.1:8080`. What does this mean and how do you fix it?
A: `127.0.0.1` is the loopback address - only accessible from the local machine, not from external clients. The application is bound to loopback-only, which means: connections from the same machine work, but connections from any external host are refused ("connection refused"). To fix: configure the application to bind to `0.0.0.0:8080` (all interfaces) or the specific public IP. For Spring Boot: `server.address=0.0.0.0` in application.properties. For nginx: `listen 0.0.0.0:80` or just `listen 80`. For Java directly: when creating `ServerSocket`, pass the InetAddress: `new ServerSocket(8080, 50, InetAddress.getByName("0.0.0.0"))`. Note: binding to 0.0.0.0 exposes the service on ALL interfaces - verify firewall rules are in place to restrict access to authorized clients only.

**Expert:**
Q: Explain what happens at the network level when a client connects to a server, including the roles of ip route, the ARP protocol, and TCP three-way handshake.
A: (1) DNS resolution: client resolves hostname to IP (not covered by ip command, but by /etc/resolv.conf and DNS queries). (2) Route lookup: client kernel looks up the destination IP in the routing table (`ip route`) to determine: which network interface to use and whether the destination is local (same subnet) or needs to go via a gateway. (3) ARP (if same subnet): client broadcasts "who has IP 10.0.1.50?" - server replies with its MAC address. Client caches this in ARP table (`ip neigh`). (4) If via gateway: client sends packet to gateway's MAC address (from ARP), with destination IP of the server. Gateway routes the packet. (5) TCP three-way handshake: client sends SYN -> server replies SYN-ACK (kernel handles this, before the application sees the connection) -> client sends ACK. Now the TCP connection is established. (6) Application level: server's listen socket (shown in `ss -tlnp`) accept()s the new connection. The server application now has a file descriptor for this specific client connection. (7) Data transfer, then FIN/FIN-ACK/ACK for graceful close. Understanding this flow explains: why `ss -tlnp` shows listening state before connection (server waiting at step 6), why connections in TIME_WAIT appear after close (kernel waits to handle late packets), and why a server at step 2 routing failure causes "no route to host" vs step 6 application failure causing "connection refused."
