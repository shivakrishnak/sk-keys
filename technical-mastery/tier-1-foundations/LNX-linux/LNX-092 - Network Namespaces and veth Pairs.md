---
id: LNX-092
title: "Network Namespaces and veth Pairs"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★★
depends_on: LNX-037, LNX-051
used_by: LNX-091, LNX-093
related: LNX-051, LNX-037, LNX-091, LNX-055
tags: [network-namespace, netns, veth, virtual-ethernet, ip-netns, bridge, docker-networking, container-networking, kubernetes-networking, pod-networking, nat, iptables, nsenter, unshare, network-isolation, cni, overlay-network, bridge-networking]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 92
permalink: /technical-mastery/lnx/network-namespaces-veth-pairs/
---

## TL;DR

Linux network namespaces provide isolated network stacks (interfaces, routing
tables, iptables rules, sockets). Each Docker container and Kubernetes pod runs
in its own network namespace - this is how containers get their own IP addresses
and isolated networking. A `veth` (virtual ethernet) pair is two connected
virtual interfaces: packet sent into one end comes out the other. Used to
connect a container's network namespace to the host bridge (docker0, cni0).
Commands: `ip netns add myns`, `ip netns exec myns ip link list`,
`ip link add veth0 type veth peer name veth1`,
`ip link set veth1 netns myns`. Understanding this explains: why `ping`
works differently from inside vs outside a container, how container networking
is implemented without hardware, and how Kubernetes pod networking works.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-092 |
| **Difficulty** | ★★★ Advanced |
| **Category** | Linux |
| **Tags** | network namespace, veth pair, container networking, Docker, Kubernetes, bridge, ip netns |
| **Prerequisites** | LNX-037 (Networking), LNX-051 (Namespaces) |

---

### The Problem This Solves

**Problem 1**: Running multiple services on the same host that both need port
80 (nginx on port 80, Apache on port 80). On a plain OS: second service
gets "Address already in use". With network namespaces: each namespace has
its own network stack. Service A in namespace `ns1` can listen on port 80
independently from Service B in namespace `ns2` - they have separate IP
addresses and separate socket tables. This is exactly how Docker runs two
nginx containers on the same host simultaneously.

**Problem 2**: A developer needs to test distributed system behavior without
multiple physical machines or cloud VMs. With network namespaces + veth pairs:
create 5 namespaces (simulating 5 servers), connect them with veth pairs
and a software bridge (simulating a LAN switch), run your distributed service
in each namespace. Test network partitions by deleting veth links (`ip link
del veth0`). Complete network simulation on a single laptop at near-zero cost.

---

### Textbook Definition

**Network namespace**: A kernel feature that provides a process (or group
of processes) with an isolated view of the network subsystem. Each network
namespace has its own: network interfaces, IP routing tables, iptables rules,
netfilter hooks, sockets, `/proc/net/` entries.

**veth (virtual ethernet) pair**: Two virtual network interfaces created
as a connected pair. A packet injected into one end emerges from the other
end, as if connected by a cable. Typically used to connect two network
namespaces.

**Key components of the container network model:**
```
Host network namespace:
  docker0 bridge (172.17.0.1/16)
  veth0abc1 --- connected to container's eth0

Container network namespace:
  eth0 (172.17.0.2/24)
  lo (127.0.0.1)
  route: default via 172.17.0.1

Packet flow (container -> internet):
  container eth0 -> veth0abc1 on host -> docker0 bridge
  -> iptables MASQUERADE (SNAT: 172.17.0.2 -> host IP)
  -> host eth0 -> internet
```

---

### Understand It in 30 Seconds

```bash
# === Create and use a network namespace ===

# Create namespace:
ip netns add myns

# List namespaces:
ip netns list
# myns

# Execute command inside namespace:
ip netns exec myns ip link list
# 1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN mode DEFAULT
# ^ Only loopback exists (no eth0, no internet)

ip netns exec myns ip route
# (empty - no routes)

ip netns exec myns ping 8.8.8.8
# connect: Network is unreachable
# ^ Isolated! No external connectivity

# === Create veth pair and connect namespace to host ===

# Create veth pair:
ip link add veth0 type veth peer name veth1
# veth0 stays in host namespace
# veth1 will go to myns

# Move veth1 to namespace:
ip link set veth1 netns myns

# Configure IPs:
ip addr add 192.168.100.1/24 dev veth0   # host side
ip netns exec myns ip addr add 192.168.100.2/24 dev veth1

# Bring interfaces up:
ip link set veth0 up
ip netns exec myns ip link set veth1 up
ip netns exec myns ip link set lo up

# Test connectivity:
ping 192.168.100.2
# PING 192.168.100.2: 64 bytes from 192.168.100.2: icmp_seq=1 ...
# ^ Host can ping inside namespace

ip netns exec myns ping 192.168.100.1
# PING 192.168.100.1: 64 bytes from 192.168.100.1: icmp_seq=1 ...
# ^ Namespace can ping host

# === Add internet access to namespace ===
# Enable IP forwarding on host:
echo 1 > /proc/sys/net/ipv4/ip_forward

# Add default route inside namespace:
ip netns exec myns ip route add default via 192.168.100.1

# Add NAT (MASQUERADE) for namespace traffic:
iptables -t nat -A POSTROUTING -s 192.168.100.0/24 -j MASQUERADE

# Test internet from namespace:
ip netns exec myns ping 8.8.8.8
# PING 8.8.8.8: 64 bytes from 8.8.8.8: icmp_seq=1 ...

# === Inspect Docker container networking ===
# Container ID:
CID=$(docker run -d nginx)
PID=$(docker inspect -f '{{.State.Pid}}' $CID)

# Enter container's network namespace:
nsenter -t $PID -n ip link list
# 1: lo: <LOOPBACK,UP,LOWER_UP>
# 5: eth0@if6: <BROADCAST,MULTICAST,UP,LOWER_UP>
# ^ eth0 is one end of a veth pair (if6 = index 6 on host)

# Find the host-side veth:
ip link | grep -A1 "6:"
# 6: veth3a2b4c@if5: <BROADCAST,MULTICAST,UP,LOWER_UP>
# ^ This is the host-side veth connected to container's eth0

# Show bridge connections:
bridge link show
# 6: veth3a2b4c master docker0 state forwarding ...

# Cleanup:
docker stop $CID && docker rm $CID
ip netns delete myns
ip link del veth0   # also deletes veth1
```

---

### First Principles

**How network namespaces work in the kernel:**
```
Linux kernel maintains a list of network namespaces.
Every process has a pointer to a 'struct net' (network namespace object).
init_net = the default (host) network namespace.

Process creation (clone/unshare):
  CLONE_NEWNET flag: new network namespace created
  Process gets empty namespace: only 'lo' interface
  Parent's namespace: unchanged

/proc/net/ virtualization:
  /proc/net/dev -> shows interfaces in current process's netns
  /proc/net/route -> shows routing table in current process's netns
  /proc/PID/net/ -> network namespace of specific process

Namespace persistence (without processes):
  /var/run/netns/NAME: bind mount of /proc/PID/ns/net
  This is what ip netns creates: a persistent named namespace
  Even if all processes leave, namespace stays (bind mount holds it)
  
  cat /proc/PID/ns/net -> /proc/net/ns/net:[4026531992]
  The number (inode) identifies the network namespace
  Processes with same inode = same namespace

veth pair internals:
  Two 'struct net_device' objects created as a pair
  xmit function of veth0: enqueues to veth1's receive queue
  xmit function of veth1: enqueues to veth0's receive queue
  No kernel copies: skb pointer moved directly
  Performance: near-line-speed (limited by memory bandwidth,
               not protocol processing)
  
  One interface can be in any namespace, the other in another
  The pair is linked regardless of which namespace each end is in

Bridge (software switch):
  struct net_device with BRIDGE flag
  Bridge forwarding database (FDB): MAC -> port mapping
  When packet arrives on bridge port:
    1. Learn source MAC -> port
    2. Lookup destination MAC in FDB
    3. Forward to specific port (unicast) or all ports (unknown/broadcast)
  
  veth0 connected to bridge (docker0):
    veth0's 'master' set to docker0
    Packets from veth0 -> bridge forwarding logic -> other ports
    
  iptables FORWARD chain:
    By default: iptables FORWARD chain DROP
    Docker adds FORWARD ACCEPT for docker0 traffic
    This is why you need iptables -P FORWARD ACCEPT
    or DOCKER-USER chain entries for container forwarding

Kubernetes pod networking:
  Per-pod network namespace:
    ip link add veth-pod123 type veth peer name eth0
    ip link set eth0 netns /proc/PID/ns/net   # pod's init process
    ip link set veth-pod123 master cni0        # bridge or CNI bridge
  
  CNI (Container Network Interface):
    Standard interface: CNI plugin called on container start
    Plugin receives: container PID, network config, interface name
    Plugin creates veth pair, configures IP, routes, etc.
    
  Calico CNI:
    No bridge! Uses policy routing:
    veth-pod123 in host namespace
    Host routing: 10.244.0.5/32 via veth-pod123
    ARP proxy on veth interface (host answers ARP for pod IPs)
    BGP routing between nodes for cross-node pod communication
  
  Flannel CNI (VXLAN mode):
    veth pair to bridge (cni0)
    VXLAN encapsulation for cross-node traffic (UDP port 8472)
    flannel.1 VTEP interface: encap/decap VXLAN
```

---

### Thought Experiment

Replicating Docker's networking model from scratch:

```bash
# Replicate: docker run --network bridge nginx
# This is (simplified) what Docker does:

# 1. Create a bridge (docker0 equivalent):
ip link add br0 type bridge
ip addr add 172.20.0.1/24 dev br0
ip link set br0 up

# 2. Create network namespace (container):
ip netns add container1

# 3. Create veth pair:
ip link add veth-host type veth peer name eth0

# 4. Move container-side veth to namespace:
ip link set eth0 netns container1

# 5. Connect host-side veth to bridge:
ip link set veth-host master br0
ip link set veth-host up

# 6. Configure container's networking:
ip netns exec container1 ip addr add 172.20.0.2/24 dev eth0
ip netns exec container1 ip link set eth0 up
ip netns exec container1 ip link set lo up
ip netns exec container1 ip route add default via 172.20.0.1

# 7. Enable NAT for container internet access:
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -s 172.20.0.0/24 ! -o br0 \
    -j MASQUERADE
# ^ MASQUERADE: SNAT container IP to host IP when leaving non-br0 interface

# 8. Run a service inside the "container":
ip netns exec container1 python3 -m http.server 80 &
# Service listening on 172.20.0.2:80

# 9. Port publishing (docker -p 8080:80 equivalent):
iptables -t nat -A PREROUTING -p tcp --dport 8080 \
    -j DNAT --to-destination 172.20.0.2:80
iptables -A FORWARD -p tcp -d 172.20.0.2 --dport 80 -j ACCEPT

# Test: curl localhost:8080 -> hits container's port 80!

# 10. Second "container" (same port 80, different namespace):
ip netns add container2
ip link add veth-host2 type veth peer name eth0
ip link set eth0 netns container2
ip link set veth-host2 master br0
ip link set veth-host2 up
ip netns exec container2 ip addr add 172.20.0.3/24 dev eth0
ip netns exec container2 ip link set eth0 up
ip netns exec container2 ip route add default via 172.20.0.1
ip netns exec container2 python3 -m http.server 80 &
# Both containers run port 80 simultaneously! Different IPs, same port.

# Verify isolation:
ip netns exec container1 ip link list
# Only: lo, eth0 (no br0, no host eth0 visible)

ip netns exec container1 ss -tlnp
# Only shows the python server - no other host processes!

# Cleanup:
kill %1 %2
ip netns delete container1
ip netns delete container2
ip link delete br0       # removes bridge and connected ports
iptables -t nat -F POSTROUTING
iptables -t nat -F PREROUTING
iptables -F FORWARD
```

---

### Mental Model / Analogy

```
Network namespace = private office building

Host network = public street network (internet + host services)
  All buildings visible to each other

Container namespace = isolated private building:
  Has its own "address" (IP, e.g., 172.17.0.2)
  Internal phone system (localhost) stays internal
  Employees inside don't see the street directly

veth pair = dedicated private road between buildings:
  One end (veth1) inside the private building (container eth0)
  Other end (veth0) on the host side (connects to street/bridge)
  Traffic on this road: bidirectional, dedicated

Bridge (docker0) = shared lobby / reception in the host:
  Multiple private roads connect to the lobby
  Lobby knows which road leads to which building (MAC table)
  Routes traffic between buildings and to the street

NAT/MASQUERADE = building reception desk:
  When employees (container) send mail to the internet:
    Reception stamps their name over employee's (SNAT)
    Internet replies go to reception first
    Reception delivers to correct employee (DNAT)
  Employees don't need public addresses - share building's address

Port forwarding = "Call extension 80 -> forward to building 2":
  Incoming call from outside on host port 8080:
    DNAT: redirect to 172.17.0.2:80 (specific container)
  Outgoing calls still NAT'd through building address

Multiple buildings (containers) on the same plot (host):
  Each has a private road to the shared lobby
  Each has its own internal address space
  Each can use the same internal port numbers (no conflicts!)
  Isolation: Building A cannot see Building B's internal network
```

---

### Gradual Depth - Five Levels

**Level 1:**
What a network namespace is: isolated network stack. `ip netns add/list/exec`.
Why containers have their own IP addresses (each container = own namespace).
veth pair concept: virtual cable between namespaces.

**Level 2:**
Creating namespaces and veth pairs. Connecting namespace to host via bridge.
NAT/MASQUERADE for internet access. `nsenter -n -t PID` to inspect container
networking. `bridge link show` and `ip link show master docker0`.

**Level 3:**
How Docker uses namespaces + veth + bridge + iptables internally. CNI
(Container Network Interface) plugin API. Kubernetes pod networking: veth per
pod, CNI plugin. Port forwarding with DNAT. Namespace persistence via bind
mount at `/var/run/netns/`. `unshare --net bash` for transient namespace.

**Level 4:**
Differences between CNI plugins: Flannel (VXLAN overlay), Calico (BGP routing,
no bridge), Cilium (eBPF, no iptables). Calico's approach: host routes per
pod IP (`ip route show` shows individual /32 routes), ARP proxy on veth
(`ip link set veth-pod123 proxy_arp on`). Multi-host networking: VXLAN
encapsulation, VTEP (VXLAN Tunnel Endpoint) interfaces. Service mesh sidecar
injection: additional namespace configuration for Envoy/Istio transparent
proxying (iptables REDIRECT rules inside pod namespace).

**Level 5:**
Linux kernel `struct net` lifecycle: namespace creation, deletion, garbage
collection of sockets/routes/interfaces. veth kernel source: `drivers/net/veth.c`
- `veth_xmit()` directly enqueues to peer's receive queue. Kernel network
stack bypass for container networking: AF_XDP, DPDK in namespaces. Container
network namespace sharing: `--network container:NAME` in Docker (shares
namespace without creating new one). Service mesh data plane: Envoy runs in
same network namespace as application pod; iptables rules redirect all traffic
through Envoy. Kernel namespace audit: `lsns -t net` to list all network
namespaces with PIDs. Production debugging: `ip netns identify PID` to find
which named namespace a process is in.

---

### How It Works

```
Kernel namespace implementation:

struct net {
    atomic_t         count;        /* reference count */
    struct list_head list;         /* namespace list */
    struct net_device *loopback;   /* lo device */
    struct netns_ipv4 ipv4;        /* IPv4 config, routes, ARP */
    struct netns_ipv6 ipv6;        /* IPv6 config, routes */
    struct netns_nf   nf;          /* netfilter hooks, iptables */
    struct xt_table   *tables[...]; /* iptables tables */
    /* ... many more subsystems ... */
};

Task's namespace pointer:
  struct task_struct {
      struct nsproxy *nsproxy;
  };
  struct nsproxy {
      struct net *net_ns;     /* pointer to network namespace */
      /* also: uts, ipc, pid, mnt namespaces */
  };

When a process calls socket():
  kernel looks up process->nsproxy->net_ns
  socket is created in that namespace
  all operations (bind, connect, send) scoped to that namespace

ip netns exec <NAME> <CMD>:
  1. Open /var/run/netns/<NAME> (a bind-mounted namespace fd)
  2. setns(fd, CLONE_NEWNET): switch current process's net namespace
  3. exec() the command
  Command runs with the new namespace

Veth pair receive/transmit:
  struct veth_priv {
      struct net_device __rcu *peer;  /* pointer to peer veth */
  };
  
  veth_xmit(skb, dev):
      peer = rcu_dereference(priv->peer)
      netif_rx(skb, peer)   /* inject into peer's receive queue */
  
  No kernel networking stack in between (no IP routing, no iptables!)
  Just: enqueue skb into peer's rx queue
  Extremely fast: ~5-10 Gbps on modern hardware
```

---

### Complete Picture - End-to-End Flow

```
Complete packet flow: container process -> internet

Inside container (namespace: container-ns):
  Process: send() to 8.8.8.8:53
  Socket in container-ns
  IPv4 routing: route table in container-ns
    -> default via 172.17.0.1 dev eth0
  eth0 in container-ns (veth pair - container side)
    -> skb sent to eth0
    -> veth_xmit: enqueue to peer (vethABCD on host)
  [namespace boundary crossed via veth]

On host (default namespace):
  vethABCD receives packet
  vethABCD's master: docker0 bridge
  Bridge processing:
    Learn source MAC (container's eth0 MAC -> vethABCD port)
    Dest MAC: FF:FF:FF:FF:FF:FF (ARP for 172.17.0.1)
      -> Bridge: ARP reply from docker0 interface
      -> container: ARP cache: 172.17.0.1 -> docker0 MAC
    Unicast to docker0 MAC: forwarded to docker0 interface
  docker0 interface: 172.17.0.1 - LOCAL
  IP routing in host namespace:
    Dest: 8.8.8.8 -> default route -> eth0 (internet facing)
  iptables POSTROUTING (nat table):
    MASQUERADE: src 172.17.0.2 -> host IP (e.g., 10.0.0.5)
  eth0 -> NIC driver -> wire -> internet

Return path:
  Internet -> host eth0: src=8.8.8.8 dst=10.0.0.5
  iptables PREROUTING (nat table):
    Conntrack: knows 10.0.0.5:PORT was MASQUERADE'd from 172.17.0.2
    DNAT: dst=10.0.0.5 -> dst=172.17.0.2
  Routing: 172.17.0.2 via docker0 bridge
  Bridge: FDB lookup -> vethABCD port
  vethABCD -> veth_xmit -> container eth0 receive queue
  Container process: recv() gets data

Performance bottlenecks in this path:
  1. veth xmit: fast (just pointer swap), no copy
  2. Bridge FDB lookup: O(1) hash table
  3. iptables conntrack: O(1) per flow (after first packet)
  4. MASQUERADE NAT: per-packet port translation (minimal overhead)
  
  Total overhead vs non-containerized: typically < 5% throughput,
  < 0.05ms additional latency for small packets
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "Network namespaces provide security isolation between containers" | Network namespaces provide ISOLATION but not complete SECURITY. A container with CAP_NET_ADMIN can manipulate its own namespace (add routes, iptables rules, create raw sockets). A container that escapes its namespace (kernel exploit like CVE-2022-0185) can affect host networking. True security requires: (1) no CAP_NET_ADMIN capability (default in Docker for non-privileged containers), (2) seccomp profiles blocking dangerous syscalls (socket(AF_PACKET), socket(AF_NETLINK)), (3) AppArmor/SELinux profiles. `docker run --network none` removes all networking - strongest isolation but no connectivity. |
| "Each veth pair can only connect two namespaces" | A veth pair connects exactly two endpoints, yes. But you can create MANY veth pairs. One end of each can connect to a single bridge - this is how Docker connects many containers (each container gets its own veth pair, one end in container namespace, other end connected to docker0 bridge). So N containers = N veth pairs = 2N veth interfaces. The bridge (docker0) can have hundreds of veth interfaces connected to it. From a container's perspective: it only sees its eth0 (container side of its veth pair). |
| "ip netns exec is the only way to run commands in a namespace" | Multiple ways: (1) `ip netns exec NAME cmd`: uses named namespace at /var/run/netns/NAME. (2) `nsenter -t PID -n cmd`: enters PID's network namespace (works with any process, including container processes). (3) `nsenter --net=/proc/PID/ns/net cmd`: explicit namespace fd. (4) `unshare --net cmd`: creates NEW namespace and runs cmd in it. (5) Process can call `setns(fd, CLONE_NEWNET)` directly in C code. For Docker: `docker exec` uses nsenter-equivalent internally. For Kubernetes: `kubectl exec` uses nsenter on the node. You can also use `/proc/PID/ns/net` directly in scripts for automation. |
| "Deleting a network namespace kills all processes inside it" | Deleting a named namespace (`ip netns del NAME`) removes the bind mount at `/var/run/netns/NAME`. If processes are still running with that namespace (their net_ns pointer still points to that namespace struct), they continue running. The namespace itself lives as long as any process holds a reference to it. Deleting the named namespace just removes the ability to reference it by name. Processes remain in their original network namespace - they don't lose connectivity. The actual namespace (struct net) is garbage collected only when all references are released. To kill processes in a namespace: use `ip netns pids NAME` to list PIDs, then kill them. |

---

### Failure Modes & Diagnosis

**Network namespace troubleshooting:**
```bash
# === Failure: veth pair - no connectivity after setup ===

# Check interface states (BOTH ends must be UP):
ip link show veth0
# veth0: <BROADCAST,MULTICAST> mtu 1500  <- state DOWN! forgot to up

ip netns exec myns ip link show veth1
# Same: check DOWN state

# Fix: bring both up:
ip link set veth0 up
ip netns exec myns ip link set veth1 up

# Check ARP / routes:
ip netns exec myns ip route show
# (empty? missing default route or /24 route)

ip netns exec myns ip neigh show
# (empty? ARP not resolved)

# Test: ping the gateway (host side of veth):
ip netns exec myns ping -c 1 192.168.100.1
# If fails: check iptables on host for FORWARD chain

# === Failure: container has IP but no internet ===
# Inside container: can ping 172.17.0.1 (gateway) but not 8.8.8.8

# Check 1: IP forwarding on host:
cat /proc/sys/net/ipv4/ip_forward
# 0 <- disabled! Enable:
echo 1 > /proc/sys/net/ipv4/ip_forward

# Check 2: iptables FORWARD chain:
iptables -L FORWARD -n -v
# If default policy DROP and no ACCEPT rules for container subnet:
iptables -A FORWARD -s 172.17.0.0/16 -j ACCEPT
iptables -A FORWARD -d 172.17.0.0/16 -j ACCEPT

# Check 3: NAT / MASQUERADE:
iptables -t nat -L POSTROUTING -n -v
# Should see: MASQUERADE for 172.17.0.0/16 or similar
# If missing:
iptables -t nat -A POSTROUTING -s 172.17.0.0/16 ! -o docker0 \
    -j MASQUERADE

# === Diagnosis: find container's network namespace ===
# From container ID:
PID=$(docker inspect -f '{{.State.Pid}}' CONTAINER_ID)

# List namespaces with lsns:
lsns -t net
# NS TYPE NPROCS   PID USER NETNSID NSFS COMMAND
# 4026531992 net 567 1 root unassigned /proc/1/ns/net init
# 4026532345 net   2 7890 root unassigned              nginx

# Inspect container's namespace directly:
nsenter -t $PID -n ip link list
nsenter -t $PID -n ip route show
nsenter -t $PID -n ss -tlnp

# Find which veth is connected to which container:
for f in /sys/class/net/veth*/; do
    ifindex=$(cat $f/iflink)
    ns_path="/proc/$PID/ns/net"
    echo "veth: $(basename $f) -> peer ifindex: $ifindex"
done

# === Debug: packet capture across veth pair ===
# Capture on host-side veth:
tcpdump -i veth3a2b4c -n

# Capture inside container:
nsenter -t $PID -n tcpdump -i eth0 -n

# Note: you'll see the SAME packets on both ends (veth is transparent)
# Useful: compare to confirm packet makes it across the veth
```

---

### Related Keywords

**Foundational:**
LNX-037 (Networking), LNX-051 (Linux namespaces)

**Builds on this:**
LNX-091 (tc and qdisc), LNX-093 (performance troubleshooting)

**Related:**
LNX-055 (cgroups), LNX-052 (process isolation)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `ip netns add NAME` | Create named network namespace |
| `ip netns list` | List all named network namespaces |
| `ip netns exec NAME CMD` | Run command in namespace |
| `ip link add veth0 type veth peer name veth1` | Create veth pair |
| `ip link set veth1 netns NAME` | Move interface to namespace |
| `nsenter -t PID -n CMD` | Enter PID's network namespace |
| `lsns -t net` | List all network namespaces with PIDs |
| `bridge link show` | Show bridge member interfaces |

**3 things to remember:**
1. Network namespaces give complete isolation: own interfaces, routes, iptables, socket table. Docker/Kubernetes containers have their own network namespace.
2. veth pairs are bidirectional virtual cables. One end in container namespace, other on host bridge. Packet in one end comes out the other.
3. Container networking = namespace + veth pair + bridge + iptables MASQUERADE. `nsenter -t PID -n` is your diagnostic tool.

---

### Transferable Wisdom

The network namespace + veth pair pattern is the foundation for: Docker
networking, Kubernetes pod networking, CNI plugins, network function
virtualization (NFV), software-defined networking (SDN) testing environments,
and CI/CD network simulation. The concept of "namespace provides isolation
via separate kernel data structures" transfers to: PID namespaces (separate
PID number space), mount namespaces (separate filesystem view), user namespaces
(separate UID/GID mapping). The software bridge (docker0) is conceptually
the same as a managed network switch's VLAN: create logical separation on
shared physical hardware. The MASQUERADE/SNAT pattern (containers share host
IP) is the same as home router NAT: all devices share one public IP. Port
forwarding (DNAT: host:8080 -> container:80) is the same as home router port
forwarding. These Linux kernel primitives (namespaces, veth, bridge, iptables
NAT) are what all container platforms, cloud providers (AWS VPC, GCP VPC),
and service meshes are built on top of.

---

### The Surprising Truth

When you run `docker network inspect bridge` and see the `docker0` bridge
with all containers' MAC addresses, you're looking at a pure software
implementation of an Ethernet switch running entirely in the Linux kernel.
The bridge code in the kernel (`net/bridge/`) implements the IEEE 802.1D
MAC Bridge standard. No specialized hardware or hypervisor required - just
the mainline Linux kernel.

The Docker networking model (which billions of containers worldwide use) is
entirely built from Linux primitives that predate Docker by decades: network
namespaces (added in Linux 2.6.24, January 2008), veth devices (added in
Linux 2.6.24), and Linux bridges (added in Linux 2.2, 1999). Docker was first
released in 2013, so the infrastructure it relies on was already 5-14 years
old. Kubernetes (2014) and all CNI plugins are similarly built on these same
ancient Linux primitives. The containers revolution was not about new kernel
features - it was about orchestrating existing features in a standardized way.

---

### Mastery Checklist

- [ ] Can create a network namespace, connect it with a veth pair, and verify connectivity with ping
- [ ] Understands the role of each component: namespace, veth pair, bridge, NAT/MASQUERADE
- [ ] Can use nsenter and ip netns exec to diagnose container networking issues
- [ ] Knows how to trace which veth interface on the host corresponds to a specific container
- [ ] Can explain the packet flow from a container process to the internet and back

---

### Think About This

1. Design a multi-container networking test environment on a single Linux host
   using only `ip` commands and network namespaces. Create 4 "server" namespaces
   connected to a central bridge namespace. No Docker or Kubernetes. The servers
   should be able to communicate with each other but have no direct internet
   access. How would you add internet access for only one specific namespace?
   What iptables rules are needed and why?

2. A Kubernetes engineer runs `kubectl exec -it pod-name -- curl 8.8.8.8`
   and gets "Network is unreachable". Using your knowledge of pod network
   namespaces, CNI plugins, and the Linux networking stack: write a systematic
   diagnosis procedure. What commands would you run on the node? What would
   you check inside the pod's namespace? How does the answer differ depending
   on whether the CNI plugin is Flannel vs Calico?

3. Service mesh sidecars (Envoy in Istio) use iptables rules inside the pod
   network namespace to transparently redirect all TCP traffic through the
   sidecar proxy (without application code changes). Explain exactly how this
   works: what iptables rules are added to the pod's namespace? How does Envoy
   avoid being caught in an infinite redirect loop? What happens to traffic
   that is already addressed to Envoy's listen port?

---

### Interview Deep-Dive

**Foundational:**
Q: How does Docker give each container its own IP address even though they all run on the same physical machine?
A: Docker uses LINUX NETWORK NAMESPACES and VETH PAIRS. Here is the exact mechanism: (1) NETWORK NAMESPACE: When a container starts, Docker creates a new network namespace for it. A network namespace provides a completely isolated network stack: separate interfaces, separate routing table, separate iptables rules, separate socket table. The container's processes only see their own network namespace - they have no visibility into the host's network or other containers' networks. (2) VETH PAIR: Docker creates a virtual ethernet (veth) pair - two virtual interfaces linked together. A packet sent into one end comes out the other. One end is placed inside the container's namespace (named eth0 from the container's perspective). The other end remains in the host namespace. (3) BRIDGE: The host-side veth interface is connected to a software bridge (docker0, at 172.17.0.1/16 by default). The bridge acts like a virtual Ethernet switch - it can have many veth interfaces connected to it, one per container. (4) IP ASSIGNMENT: Docker assigns the container an IP (e.g., 172.17.0.2) and configures the container's routing table to have docker0 as the default gateway. (5) NAT: For internet access, Docker configures iptables MASQUERADE on the host: when a container sends a packet to the internet, the source IP is rewritten from 172.17.0.2 to the host's public IP. Return packets are un-NATted back to the container. Result: container has its own private IP (172.17.0.2), invisible from outside, with internet access via NAT. Multiple containers can use the same PORT numbers without conflict (different IPs, different network stacks).

**Expert:**
Q: Compare the network datapath of Flannel (VXLAN mode) vs Calico (BGP mode) for pod-to-pod communication in Kubernetes. Which has lower latency and why?
A: FLANNEL (VXLAN): Cross-node packet flow: Pod A (10.244.1.5) sends to Pod B (10.244.2.5, on different node): (1) Pod A -> veth pair -> cni0 bridge on Node A; (2) Linux routing on Node A: 10.244.2.0/24 via flannel.1 (VTEP); (3) flannel.1 VTEP: VXLAN encapsulation - original packet wrapped in UDP (port 8472), outer src=Node A IP, outer dst=Node B IP; (4) Physical NIC on Node A sends encapsulated packet to Node B; (5) Node B NIC receives, kernel decapsulates at flannel.1 VTEP; (6) Inner packet: 10.244.2.5 - routed to cni0 bridge -> veth -> Pod B. OVERHEAD: (a) VXLAN header (50 bytes overhead per packet), (b) CPU for encap/decap (significant at high packet rates), (c) MTU reduction (physical MTU 1500 - VXLAN 50 = effective MTU 1450 for pods), (d) Extra memory copies in software. CALICO (BGP): Cross-node packet flow: Pod A (10.244.1.5) sends to Pod B (10.244.2.5): (1) Pod A -> veth pair (e.g., vethABC) directly connected to Linux routing (NO bridge); (2) Node A routing table: 10.244.2.5/32 via Node B's IP (learned via BGP from Node B's bird daemon); (3) Physical NIC: sends packet directly (no encapsulation!) to Node B; (4) Node B routing: 10.244.2.5/32 via local veth of Pod B; (5) Packet arrives directly in Pod B. LATENCY COMPARISON: Calico is typically 5-15% lower latency for small packets because: (1) No VXLAN encap/decap overhead (2+ microseconds per packet on software VTEP), (2) No extra memory copies, (3) Full MTU available (no overhead bytes), (4) Fewer software layers in the path. Flannel ADVANTAGE: simpler to set up, no BGP infrastructure needed, works on any network that forwards UDP (cloud environments with no BGP). Calico ADVANTAGE: direct routing, lower latency, native kernel path, IPsec without double-encapsulation. BOTTLENECK: at very high packet rates (>1M pps), Calico's host routing table size can become a factor (one /32 per pod), while Flannel only needs per-node CIDR routes. Calico address: use IPIP or VXLAN only when BGP is not feasible; otherwise pure BGP routing is optimal.
