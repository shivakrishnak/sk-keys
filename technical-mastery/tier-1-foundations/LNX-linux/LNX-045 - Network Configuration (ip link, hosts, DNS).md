---
id: LNX-045
title: "Network Configuration (ip link, /etc/hosts, DNS)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-023, LNX-044, NET-001
used_by: LNX-055, LNX-092
related: LNX-055, NET-001, LNX-023
tags: [ip-link, ip-addr, route, dns, resolv.conf, hostname, nmcli, netplan, ifconfig]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/lnx/network-configuration/
---

## TL;DR

Modern Linux network configuration uses `ip` command (replacing deprecated
`ifconfig`, `route`). `ip addr show` (or `ip a`) lists interfaces and IPs.
`ip link set eth0 up/down` enables/disables interfaces. `ip route show`
shows routing table. DNS configured via `/etc/resolv.conf` (nameserver
lines) but managed by `systemd-resolved` or `NetworkManager` on modern
systems. Static IP: edit `/etc/netplan/*.yaml` (Ubuntu) or
`/etc/sysconfig/network-scripts/` (RHEL). `nmcli` for NetworkManager.
`dig`, `host`, `nslookup` for DNS queries.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-045 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | ip addr, ip link, ip route, DNS, resolv.conf, netplan, nmcli, ifconfig |
| **Prerequisites** | LNX-023, LNX-044, NET-001 |

---

### The Problem This Solves

After creating a new VM or container: it has no IP configuration yet. Or:
a VM has the wrong IP/DNS. Without knowing how to configure networking,
you can't connect to other services. Network configuration is foundational:
every SSH connection, API call, and database query depends on correct network
settings.

---

### Textbook Definition

**Network interface**: A software representation of a network adapter
(physical or virtual). Named: `eth0`, `ens3`, `enp2s0` (Ethernet), `lo`
(loopback), `wlan0` (WiFi), `docker0` (Docker bridge), `veth*` (virtual
Ethernet pairs in containers).

**IP address**: Numeric identifier for a network interface. IPv4: 32-bit
(e.g., 192.168.1.100). IPv6: 128-bit (e.g., fe80::1). CIDR notation:
`192.168.1.100/24` (IP + subnet mask).

**Routing table**: The kernel's table mapping destination networks to
next-hop gateways and interfaces. `ip route show` displays it.

**DNS (Domain Name System)**: Translates hostnames to IP addresses.
`/etc/resolv.conf` lists DNS servers. Lookup order controlled by
`/etc/nsswitch.conf`.

**Persistent vs runtime configuration**: `ip` command changes are
runtime-only (lost on reboot). Persistent config uses distro-specific
tools (netplan, NetworkManager, ifupdown).

---

### Understand It in 30 Seconds

```bash
# === ip command (modern, replaces ifconfig/route) ===
ip addr show                 # list all interfaces and IPs (alias: ip a)
ip addr show eth0            # specific interface
ip link show                 # interface link state (up/down)

# Enable/disable interface:
ip link set eth0 up
ip link set eth0 down

# Add/remove IP address (runtime, not persistent):
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0

# Routing:
ip route show                # routing table (alias: ip r)
ip route add 10.0.0.0/8 via 192.168.1.1      # add static route
ip route del 10.0.0.0/8                       # remove route
ip route add default via 192.168.1.1          # set default gateway

# === DNS queries ===
dig example.com              # DNS lookup (full details)
dig example.com +short       # just the IP
dig MX example.com           # MX records
dig @8.8.8.8 example.com    # query specific DNS server
host example.com             # simpler DNS lookup
nslookup example.com         # interactive or one-shot DNS query

# Verify DNS resolution:
getent hosts database.internal  # uses nsswitch (checks /etc/hosts first)
dig database.internal           # queries DNS directly (bypasses /etc/hosts)

# === Checking current DNS config ===
cat /etc/resolv.conf              # DNS servers in use
resolvectl status                 # systemd-resolved status and DNS info
nmcli device show eth0 | grep DNS # DNS via NetworkManager

# === Hostname ===
hostname                     # show current hostname
hostname -I                  # show all IP addresses
hostnamectl                  # systemd hostname info
hostnamectl set-hostname myserver  # set persistent hostname

# === Old commands (deprecated but still found on many systems) ===
ifconfig                     # replaced by: ip addr
ifconfig eth0 up/down        # replaced by: ip link set eth0 up/down
route                        # replaced by: ip route
netstat -tlnp                # replaced by: ss -tlnp
```

---

### First Principles

**The `ip addr show` output decoded:**
```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
  ^   ^                                        ^                         ^
  |   Interface name                            MTU (max frame size)     Link state
  Interface index

    link/ether 52:54:00:ab:cd:ef brd ff:ff:ff:ff:ff:ff
                ^                    ^
                MAC address          Broadcast MAC

    inet 192.168.1.100/24 brd 192.168.1.255 scope global dynamic eth0
         ^               ^                         ^
         IP/CIDR         Broadcast IP              Lifetime (dynamic = DHCP)

    inet6 fe80::5054:ff:feab:cdef/64 scope link
          ^                           ^
          Link-local IPv6              Scope: link-local (not routable)

Flags: UP=enabled, LOWER_UP=physical link present
       BROADCAST=can broadcast, MULTICAST=supports multicast
```

**Routing table reading:**
```bash
ip route show:
  default via 192.168.1.1 dev eth0 proto dhcp src 192.168.1.100
  ^       ^                                       ^
  Match   Next hop for all traffic                Our source IP
  (any)   (gateway)

  192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100
  ^                                         ^
  Direct route (same subnet, no gateway)    Kernel added this
                                            (when IP was assigned)

How to use: destination IP matched longest prefix
  packet to 8.8.8.8: no specific route -> use "default" -> send to 192.168.1.1
  packet to 192.168.1.5: matches 192.168.1.0/24 -> send directly on eth0
```

---

### Thought Experiment

Configuring a static IP on a server to replace DHCP:

```bash
# Current state: eth0 has DHCP IP 192.168.1.50
# Goal: static IP 192.168.1.10, gateway 192.168.1.1, DNS 8.8.8.8

# === Ubuntu 18+ (Netplan) ===
cat /etc/netplan/01-netcfg.yaml   # view current
cat > /etc/netplan/01-netcfg.yaml << 'EOF'
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.10/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
        search: [example.com]
EOF
netplan apply    # apply (will briefly drop and restore connection)

# === RHEL/CentOS 7 (ifcfg files) ===
cat > /etc/sysconfig/network-scripts/ifcfg-eth0 << 'EOF'
TYPE=Ethernet
BOOTPROTO=none
NAME=eth0
DEVICE=eth0
ONBOOT=yes
IPADDR=192.168.1.10
PREFIX=24
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
EOF
systemctl restart NetworkManager
nmcli connection up eth0

# === RHEL/CentOS 8+ (NetworkManager via nmcli) ===
nmcli con mod "Wired connection 1" \
    ipv4.method manual \
    ipv4.addresses "192.168.1.10/24" \
    ipv4.gateway "192.168.1.1" \
    ipv4.dns "8.8.8.8,8.8.4.4"
nmcli con up "Wired connection 1"

# Verify:
ip addr show eth0
ip route show
dig google.com
```

---

### Mental Model / Analogy

```
Network interface = your house's mailbox
IP address = your house's street address (what to write on envelopes)
Subnet (/24) = your neighborhood (192.168.1.0-255 = 254 houses)

Routing table = your personal delivery plan:
  "For mail to 192.168.1.* : deliver locally (direct)"
  "For everything else: give to 192.168.1.1 (the post office/gateway)"

DNS = the phone book:
  You know "google.com" but the network needs the IP address
  /etc/resolv.conf = "which phone book company to call"
  /etc/hosts = "my personal list of shortcuts I maintain myself"
  dig/host/nslookup = "looking someone up in the phone book"

ip addr = your current address label
ip link = whether your mailbox is open (up) or sealed (down)
ip route = your delivery instructions

systemd-resolved/NetworkManager = the postal service company
  (manages DNS, maintains /etc/resolv.conf for you)
  (direct editing might conflict with their management)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`ip addr show` (see IPs), `ip route show` (see default gateway),
`cat /etc/resolv.conf` (see DNS servers), `ping -c4 8.8.8.8` (test
IP connectivity), `dig google.com` (test DNS). Five commands cover
90% of network diagnosis.

**Level 2:**
`ip link set eth0 up/down`. Runtime IP assignment vs persistent config.
Netplan (Ubuntu) vs NetworkManager (most distros). `nmcli device show`
for interface details. `ss -tlnp` (ports). `curl -v https://example.com`
(full HTTP stack test). `traceroute` for path tracing.

**Level 3:**
IPv6 configuration and dual-stack. MTU tuning: `ip link set eth0 mtu 9000`
(jumbo frames for high-throughput). VLAN tagging: `ip link add link eth0
name eth0.100 type vlan id 100`. Bonding/teaming interfaces (LACP):
`nmcli con add type bond`. Network namespaces: `ip netns add mynamespace`
(used by containers). `tcpdump` for packet capture: `tcpdump -i eth0 port 80`.

**Level 4:**
Policy-based routing: multiple routing tables selected based on source IP
or firewall marks (`ip rule`, `ip route table N`). BGP with BIRD or FRRouting
for dynamic routing. `iproute2` tc (traffic control): rate limiting, QoS,
queuing disciplines. Interface statistics: `ip -s link show eth0` (errors,
drops). Kernel network tuning via sysctl: `net.core.somaxconn`,
`net.ipv4.tcp_rmem/wmem`, `net.ipv4.ip_forward`.

**Level 5:**
DPDK (Data Plane Development Kit): bypasses kernel network stack for
line-rate packet processing (used in Cisco VPP, OVS-DPDK). SR-IOV:
PCIe-level interface virtualization, hardware-level isolation for VMs.
XDP (eXpress Data Path): eBPF programs attached before the Linux network
stack for line-rate packet processing. eBPF-based networking (Cilium):
replaces iptables/conntrack with eBPF hash tables for O(1) routing.
These are the approaches for 100 Gbps+ networking where kernel networking
is the bottleneck.

---

### Code Example

**BAD - network configuration mistakes:**
```bash
# BAD 1: Making runtime changes and thinking they're persistent:
ip addr add 10.0.0.100/24 dev eth0    # runtime only!
# Works until: reboot, network restart, or NetworkManager reconnects
# After reboot: 10.0.0.100 is gone

# GOOD: use netplan (Ubuntu) or nmcli for persistent config:
# Then verify: ip addr show eth0  (after applying persistent config)

# BAD 2: Editing /etc/resolv.conf directly on systemd-resolved systems:
echo "nameserver 8.8.8.8" > /etc/resolv.conf
# NetworkManager or systemd-resolved will overwrite this!

# Check first:
ls -la /etc/resolv.conf
# If symlink to /run/systemd/resolve/... -> managed by systemd-resolved
# Edit via: resolvectl dns eth0 8.8.8.8
# Or configure in /etc/systemd/resolved.conf

# BAD 3: Testing DNS with ping when DNS might be broken:
ping google.com    # FAILS: could be DNS OR network OR firewall
# You don't know WHICH layer failed

# GOOD: test each layer:
ping -c2 8.8.8.8                     # test IP connectivity (no DNS)
dig @8.8.8.8 google.com +short       # test DNS against specific server
dig google.com +short                 # test DNS via configured resolver
curl -v --resolve google.com:443:142.250.80.46 https://google.com  # bypass DNS
```

**GOOD - network diagnostic runbook:**
```bash
#!/bin/bash
# network-diagnosis.sh: Systematic network troubleshooting

echo "=== Interface State ==="
ip link show

echo ""
echo "=== IP Addresses ==="
ip addr show

echo ""
echo "=== Routing Table ==="
ip route show

echo ""
echo "=== DNS Configuration ==="
cat /etc/resolv.conf

echo ""
echo "=== Layer Tests ==="

# Test 1: Loopback (OS networking):
if ping -c1 -W1 127.0.0.1 &>/dev/null; then
    echo "PASS: Loopback"
else
    echo "FAIL: Loopback - kernel networking issue"
fi

# Test 2: Default gateway (local network):
GW=$(ip route show default | awk '{print $3}')
if [[ -n "$GW" ]] && ping -c1 -W2 "$GW" &>/dev/null; then
    echo "PASS: Gateway ($GW)"
else
    echo "FAIL: Gateway ($GW) - local network issue"
fi

# Test 3: External IP (internet without DNS):
if ping -c1 -W3 8.8.8.8 &>/dev/null; then
    echo "PASS: Internet (8.8.8.8)"
else
    echo "FAIL: Internet - firewall or routing issue"
fi

# Test 4: DNS resolution:
if dig +short +timeout=3 google.com @"$(grep nameserver /etc/resolv.conf | head -1 | awk '{print $2}')" &>/dev/null; then
    echo "PASS: DNS resolution"
else
    echo "FAIL: DNS - resolver issue"
fi

# Test 5: HTTPS:
if curl -sf --max-time 5 https://example.com &>/dev/null; then
    echo "PASS: HTTPS"
else
    echo "FAIL: HTTPS - SSL or HTTP issue"
fi
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`ifconfig` is the command to use for network config" | `ifconfig` is deprecated and may not be installed on modern systems (requires `net-tools` package). The modern replacement is `ip addr` (ip-route2 package, installed by default). `ifconfig eth0 192.168.1.100 netmask 255.255.255.0` is replaced by `ip addr add 192.168.1.100/24 dev eth0`. |
| "`/etc/resolv.conf` is directly configurable on all systems" | On systems using `systemd-resolved` (Ubuntu 18+) or `NetworkManager`, `/etc/resolv.conf` is a symlink to a generated file. Direct edits are overwritten. Configure DNS through the owning service: `resolvectl dns`, `nmcli`, or `/etc/systemd/resolved.conf`. Check `ls -la /etc/resolv.conf` first. |
| "`ip addr add` makes a permanent IP assignment" | `ip` commands only modify kernel runtime state. They're lost on reboot or network restart. For persistent config: Ubuntu = netplan YAML, RHEL 7 = ifcfg files in /etc/sysconfig/network-scripts/, RHEL 8+ = nmcli or NetworkManager connection files. |
| "DNS failure means the server is unreachable" | DNS failure means you can't resolve the HOSTNAME. The server might be perfectly reachable by IP. Always test: `ping -c2 IP_ADDRESS` (bypass DNS). DNS failure could be: wrong nameserver in resolv.conf, DNS server down, firewall blocking UDP port 53. Network failure could be: no route to host, interface down, firewall blocking TCP/IP. Different problems, different fixes. |
| "The `ping` command is a reliable network test" | ICMP (used by ping) is often blocked by firewalls. A failed ping doesn't mean the host is unreachable - it might be that ICMP is filtered. `curl http://host:port` or `nc -zv host port` test the actual service port. Conversely: a successful ping doesn't mean the service is running (ICMP might work while port 8080 is down). |

---

### Failure Modes & Diagnosis

**No DNS resolution after network config change:**
```bash
# Symptom: ping -c2 8.8.8.8 works, but ping google.com fails
# "ping: google.com: Temporary failure in name resolution"

# Step 1: Check resolv.conf:
cat /etc/resolv.conf
# If empty or no nameserver lines: DNS not configured

# Step 2: Test DNS directly:
dig @8.8.8.8 google.com +short    # query Google DNS directly
# If this works: problem is in /etc/resolv.conf (wrong nameserver)
# Fix: add 'nameserver 8.8.8.8' to /etc/resolv.conf
# (or configure systemd-resolved/NetworkManager properly)

# Step 3: Check if systemd-resolved is responsible:
ls -la /etc/resolv.conf
resolvectl status    # shows active DNS and resolution stats

# Step 4: If managed by systemd-resolved:
resolvectl dns eth0 8.8.8.8   # configure DNS for interface
# Or: in /etc/systemd/resolved.conf:
# [Resolve]
# DNS=8.8.8.8 8.8.4.4

# Step 5: Check nsswitch:
grep ^hosts /etc/nsswitch.conf
# Should include 'dns': hosts: files dns
```

---

### Related Keywords

**Foundational:**
LNX-023 (Networking Commands), LNX-044 (/etc Directory), NET-001

**Builds on this:**
LNX-055 (Linux Network Stack Internals), LNX-092 (Network Namespaces)

**Related:**
LNX-040 (Firewall Basics), NET-001 (Networking)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ip addr show` | List interfaces and IPs |
| `ip link set eth0 up` | Enable interface |
| `ip route show` | Routing table |
| `ip route add default via X.X.X.X` | Set default gateway |
| `dig example.com +short` | DNS lookup |
| `dig @8.8.8.8 example.com` | Query specific DNS |
| `resolvectl status` | systemd-resolved DNS status |
| `nmcli device show` | Interface details via NM |
| `netplan apply` | Apply netplan config |
| `hostnamectl set-hostname name` | Set hostname |

**3 things to remember:**
1. `ip addr/link/route` replaces deprecated `ifconfig`/`route` (use `ip` on modern systems)
2. Runtime IP changes (via `ip addr add`) are LOST on reboot - use netplan/nmcli for persistent config
3. DNS failure != network failure: test `ping 8.8.8.8` (IP) and `dig google.com` (DNS) separately

---

### Transferable Wisdom

`ip` command concepts transfer directly to: `kubectl` networking debugging
(pods have IP addresses, cluster has a routing table, CoreDNS is the DNS
server), Docker networking (`docker network inspect`, container IPs, bridge
interfaces appear in `ip addr show`), AWS VPC (subnets, route tables, DNS -
same concepts, AWS console interface), Kubernetes network debugging (`ip addr`
inside a pod, `ip route` to see pod routing). The mental model: network
interface + IP + routing table + DNS is universal. The tools change but
the concepts don't.

`dig` for DNS debugging transfers everywhere: checking if your service's
DNS record has propagated, verifying CNAMEs for cloud load balancers,
troubleshooting split-horizon DNS in Kubernetes (CoreDNS returns ClusterIP
for services, external DNS returns public IP - same hostname, different
answers depending on which resolver you query).

---

### The Surprising Truth

The `ifconfig` command has been deprecated since Linux kernel 3.5 (2012)
and net-tools has been unmaintained since around 2001. However, many
tutorials, documentation pages, and even enterprise runbooks still use it.
On minimal Ubuntu 22.04 and RHEL 9 installations, `ifconfig` is not installed
by default. The iproute2 package (providing the `ip` command) is the kernel
team's supported interface. The reason `ifconfig` persisted: it was installed
by default for decades, scripts and tutorials referenced it, and it mostly
worked. The modern `ip` command was introduced by Alexey Kuznetsov in 1999
as part of the iproute2 suite to support more advanced networking features
that ifconfig was never designed to handle. If you see an interview question
asking "how do you check the IP address?" and you answer `ifconfig`, you're
technically correct but revealing you haven't kept up with 12 years of
Linux networking evolution. `ip addr show` is the current answer.

---

### Mastery Checklist

- [ ] Can display and interpret network interface status and IP addresses
- [ ] Can add a static IP and default gateway (runtime and persistent)
- [ ] Can configure and verify DNS resolution
- [ ] Can diagnose network vs DNS failures systematically
- [ ] Understands the difference between runtime and persistent network config

---

### Think About This

1. Your server has `ip addr show eth0` showing IP `10.0.0.100/24`.
   The routing table shows `default via 10.0.0.1 dev eth0`. DNS is
   configured as `nameserver 8.8.8.8`. A `curl https://api.example.com`
   hangs indefinitely. Trace through each network layer (link, IP, routing,
   DNS, TCP, TLS, HTTP) and describe what test you'd do at each layer to
   isolate the failure.

2. Inside a Kubernetes pod, you run `ip addr show` and see `eth0@if7` with
   IP `10.244.0.15/24`. You run `ip route show` and see routes through
   a veth interface. But `ping 10.244.0.16` (another pod) fails. You can
   reach the Kubernetes service ClusterIP. What network component sits
   between pods on the same node, and what might be misconfigured?

3. You configure a server with static IP `192.168.1.100/24` and gateway
   `192.168.1.1`. But you need to reach servers on `10.0.0.0/8` via
   a VPN gateway at `192.168.1.200`. You don't want to change the default
   gateway (that breaks internet access). How would you add a specific
   route for the 10.0.0.0/8 subnet? Write the exact `ip route` command.

---

### Interview Deep-Dive

**Foundational:**
Q: How do you configure a static IP address on a Linux server, and how is this different from using DHCP?
A: DHCP: the server requests an IP from a DHCP server at boot. IP may change between reboots (or may be a lease that stays stable). Configured by: `dhcp4: yes` in netplan, or `BOOTPROTO=dhcp` in ifcfg, or `dhcp` in NetworkManager. Static IP: you manually assign a fixed IP, subnet mask, gateway, and DNS. Never changes unless you change it. Required for: servers that need predictable IPs, DNS A records, firewall rules, load balancer backends. Configuration on Ubuntu 18+ (netplan): create/edit `/etc/netplan/01-config.yaml`: `network: version: 2 / ethernets: eth0: dhcp4: no / addresses: [192.168.1.100/24] / gateway4: 192.168.1.1 / nameservers: addresses: [8.8.8.8]`. Apply with `netplan apply`. Verify: `ip addr show eth0` (see static IP), `ip route show` (see gateway), `dig google.com` (DNS works). Key consideration: after `netplan apply`, the old DHCP lease is released and the new static IP takes effect immediately - your SSH session may drop if you're connecting from outside (reconnect to the new IP).

**Intermediate:**
Q: What is the difference between `dig`, `nslookup`, and `getent hosts` when troubleshooting DNS?
A: Three different DNS testing tools with different scopes: `dig example.com`: queries DNS directly using the configured nameservers (from /etc/resolv.conf or specified with `@server`). Bypasses `/etc/hosts`. Returns full DNS response with record types, TTL, answer/authority/additional sections. Best for: understanding DNS record details, checking TTL, testing specific DNS servers with `@`. `nslookup example.com`: similar to dig but older, more interactive. Less detailed output. Deprecated in favor of dig. Still useful: `nslookup` then `server 8.8.8.8` then `example.com` for interactive testing. `getent hosts example.com`: uses the system resolver, which respects `/etc/nsswitch.conf`. Checks `/etc/hosts` first (if configured as "files" in nsswitch), then DNS. This is what applications actually use. Best for: "what will my application actually resolve this to?" Diagnostic approach: if `dig` works but `getent hosts` doesn't: problem is in nsswitch, /etc/hosts, or NSS configuration. If `dig @8.8.8.8` works but `dig` (using configured nameserver) fails: problem is with the configured DNS server. If `getent` works but the app can't resolve: might be a DNS caching issue inside the app (some apps cache DNS), or the app uses a different resolver (Java has its own DNS cache).

**Expert:**
Q: In a Kubernetes cluster, a pod can't resolve the hostname of a Kubernetes Service. Walk through how you would diagnose this, from the pod's networking to CoreDNS.
A: Systematic DNS debugging in Kubernetes: (1) Verify the problem: `kubectl exec -it mypod -- nslookup service-name`. If fails: DNS issue. (2) Check if CoreDNS is running: `kubectl get pods -n kube-system -l k8s-app=kube-dns`. All should be Running. (3) Check CoreDNS logs: `kubectl logs -n kube-system -l k8s-app=kube-dns`. Errors like "unable to establish UDP connection" or plugin errors visible here. (4) Verify the pod's DNS config: `kubectl exec -it mypod -- cat /etc/resolv.conf`. Should show: `nameserver 10.96.0.10` (CoreDNS ClusterIP), `search default.svc.cluster.local svc.cluster.local cluster.local`. (5) Test CoreDNS directly from pod: `kubectl exec -it mypod -- dig @10.96.0.10 service-name.default.svc.cluster.local`. If this works: problem is in the pod's /etc/resolv.conf or nsswitch. If fails: CoreDNS can't resolve it. (6) Check if the Service exists and has correct selector: `kubectl get svc service-name`, `kubectl get endpoints service-name`. No endpoints = selector doesn't match any pods. (7) Check Network Policy: `kubectl get networkpolicies`. A policy might block pod-to-CoreDNS traffic (UDP/TCP port 53 to kube-system namespace). (8) Check node-level DNS: is the node's resolv.conf correct? CoreDNS pods forward unknown domains to node's DNS. (9) CoreDNS ConfigMap: `kubectl get configmap -n kube-system coredns -o yaml`. Check the Corefile for misconfigurations. Common issues: wrong `forward` server, disabled `kubernetes` plugin, wrong `pods` mode.
