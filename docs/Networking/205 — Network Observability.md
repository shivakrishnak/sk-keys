---
layout: default
title: "Network Observability"
parent: "Networking"
nav_order: 205
permalink: /networking/network-observability/
number: "0205"
category: Networking
difficulty: ★★★
depends_on: Observability & SRE, Networking, Distributed Systems
used_by: Observability & SRE, Kubernetes, Platform & Modern SWE, Microservices
related: East-West vs North-South Traffic, Service Discovery, mTLS, Packet Loss Latency & Jitter, BGP
tags:
  - networking
  - observability
  - network-monitoring
  - ebpf
  - flow-logs
  - cilium-hubble
  - packet-capture
---

# 205 — Network Observability

⚡ TL;DR — Network Observability = understanding what's happening in your network at any moment: which services talk to which, what's the latency, where are packets dropped, and which connections are failing. Tools: **flow logs** (VPC Flow Logs, Cilium Hubble — who talked to whom), **packet capture** (tcpdump/Wireshark — deep packet inspection), **network metrics** (latency, packet loss, throughput per path), **eBPF-based tracing** (kernel-level visibility without code changes). Essential for diagnosing cascading failures, security incidents, and performance bottlenecks in cloud and Kubernetes environments.

---

### 🔥 The Problem This Solves

Traditional APM (Application Performance Monitoring) tells you a service is slow but can't tell you WHY at the network level. Is it retransmissions? DNS resolution delay? Connection pool exhaustion? A misconfigured network policy silently dropping packets? Network Observability provides the network-layer view: you can see every TCP connection, every dropped packet, every DNS query, and every flow with sub-millisecond precision — often without changing any application code, using eBPF to hook directly into the kernel.

---

### 📘 Textbook Definition

**Network Observability:** The ability to understand the behaviour, health, and performance of a network system from the outside, based on the network signals it produces: flows (who talks to whom), metrics (latency, throughput, error rates), logs (connection events, DNS queries), and traces (distributed network path tracing). Distinguished from traditional monitoring by its focus on unknown unknowns — understanding novel failure modes without pre-defined metrics.

**Key signals:** Flow data (NetFlow/IPFIX/VPC Flow Logs), packet-level data (pcap/tcpdump), network metrics (SNMP, streaming telemetry), kernel-level eBPF traces, DNS query logs, connection state logs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Network Observability = know what's actually happening in your network. Which pods talk to which, where packets are dropped, what's causing latency — without relying on apps to instrument themselves.

**One analogy:**
> Network Observability is like having CCTV cameras AND traffic sensors on every road in a city, in real-time. You see every car (packet), every trip (flow), every traffic jam (congestion), and every accident (packet drop). The city was running before the cameras, but you had no way to know what was happening. Now you can route traffic around accidents and predict bottlenecks before they become incidents.

---

### 🔩 First Principles Explanation

**THE OBSERVABILITY LAYERS:**
```
Layer 7 (Application): APM, distributed tracing
  What: HTTP requests, DB queries, gRPC calls
  Who: Jaeger, Zipkin, DataDog APM
  What it misses: network-level issues (TCP retransmits, DNS failures)

Layer 4/5 (Transport): Connection-level metrics
  What: TCP connections, connection state, retransmit rate
  Who: ss, netstat, /proc/net/tcp, Prometheus node_exporter
  What it misses: why connections fail (routing? firewall? DNS?)

Layer 3 (Network): IP-level flows
  What: flows (src IP, dst IP, protocol, bytes, packets)
  Who: VPC Flow Logs, NetFlow, IPFIX, Cilium Hubble
  What it misses: application context (which service? which request?)

Layer 2 (Link): Frame-level
  What: ARP, ICMP, raw packets
  Who: tcpdump, Wireshark, packet capture
  What it misses: too low-level, too much data for production

eBPF (cross-layer magic):
  Observes: kernel-level network stack, socket operations
  Can: associate network events with pod/process identity
  Who: Cilium Hubble, Pixie, Parca, Falco
  What it provides: both network visibility AND application context
```

**VPC FLOW LOGS (AWS):**
```
AWS VPC Flow Log entry (default format):
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status

Example:
2 123456789012 eni-xxx 10.0.1.5 10.0.2.10 54321 8080 6 5 320 1620000000 1620000060 ACCEPT OK

Fields:
  srcaddr/dstaddr: source/destination IP
  srcport/dstport: port numbers
  protocol: 6=TCP, 17=UDP, 1=ICMP
  packets/bytes: traffic volume
  action: ACCEPT or REJECT
  log-status: OK, NODATA, SKIPDATA

Key use cases:
  1. Security: find unexpected flows (port scanning, data exfiltration)
     Query: action=REJECT AND dstport=22 → SSH brute force attempts
  2. Compliance: audit access to sensitive resources (RDS, S3)
  3. Cost: find high-bandwidth flows → optimise placement
  4. Troubleshooting: why can't service A reach service B?
     Query: srcaddr=A AND dstaddr=B AND action=REJECT

Storage: CloudWatch Logs, S3 (query with Athena), Splunk
Cost: ~$0.05/GB for VPC Flow Log data
```

**CILIUM HUBBLE (eBPF-BASED KUBERNETES NETWORK OBSERVABILITY):**
```
Architecture:
  Hubble agent: runs on each node, observes network via eBPF programs
  Hubble relay: aggregates from all nodes
  Hubble UI: visual service map + flow explorer
  Hubble CLI: command-line query interface

What Hubble provides:
  1. L3/L4 flows: every connection between pods (src, dst, verdict)
  2. L7 visibility: HTTP method, URL, status code (with Cilium)
  3. DNS visibility: which pod queries what DNS name
  4. Policy verdicts: which flows were allowed/denied by NetworkPolicy
  5. Service map: auto-generated dependency graph from observed traffic

Example Hubble CLI queries:
  # See all flows from order-service
  hubble observe --pod production/order-service-xxx --follow
  
  # See all dropped flows (NetworkPolicy violations)
  hubble observe --verdict DROPPED --follow
  
  # DNS query tracing
  hubble observe --type dns --follow
  
  # HTTP flows to payment service
  hubble observe --http-method POST --pod production/payment-service
```

**eBPF NETWORK TRACING:**
```
eBPF = Extended Berkeley Packet Filter
  Programs run in kernel space (safe sandbox)
  Triggered by kernel events: system calls, network packets, kprobes
  NO application code changes needed
  NO performance overhead of traditional packet capture

Key eBPF networking tools:
  bpftrace: write eBPF probes on the fly
    bpftrace -e 'kprobe:tcp_sendmsg { printf("%s\n", comm); }'
    → shows which process sent TCP data
  
  tcptracer-bpf (Weave Scope): traces TCP connect/accept/close
  bcc tools: tcplife, tcpretrans, tcpconnect, tcpaccept
  
  Cilium/Hubble: production-grade eBPF network observability
    Tracks every L3/L4/L7 flow with pod identity
    No tcpdump (too expensive in production), no iptables -j LOG

tcpretrans example:
  ./tcpretrans  # shows TCP retransmits
  TIME     PID    IP  LADDR:LPORT       RADDR:RPORT       STATE
  10:23:01 1234   4   10.0.1.5:54321    10.0.2.10:8080   ESTABLISHED
  → TCP retransmit: connection is experiencing packet loss
```

**NETWORK METRICS STACK:**
```
Golden signals for network (RED + network-specific):
  Rate:     requests/sec per service pair (from flow data or APM)
  Errors:   connection errors, TCP RSTs, DNS NXDOMAIN rate
  Duration: connection establishment time, DNS resolution time

Network-specific metrics:
  Throughput: bytes/sec per interface/connection
  Packet loss: retransmit rate (from /proc/net/snmp, node_exporter)
  TCP RTT: round-trip time per connection (ss -i, or eBPF)
  DNS latency: time from query to response (dig, dnsmasq logs)
  Connection churn: new connections/sec (TCP_SYN rate)
  Bandwidth utilisation: bytes_sent/link_capacity

Prometheus metrics (from node_exporter):
  node_network_receive_bytes_total{device="eth0"}
  node_network_transmit_bytes_total{device="eth0"}
  node_netstat_TcpExt_TCPRetransFail  # retransmit failures
  node_netstat_Tcp_RetransSegs        # retransmit segments
  node_netstat_Tcp_CurrEstab          # current established connections
  
  Alert: retransmit rate > 1% → packet loss issue
  Alert: DNS query latency p99 > 10ms → DNS resolver issue
```

---

### 🧪 Thought Experiment

**LATENCY SPIKE WITH NO APP CHANGE:**
Users report checkout latency spikes from 200ms to 3s every few hours. APM shows no spike at the service level. Flow logs show normal-looking connections. But eBPF tcpretrans shows TCP retransmits from order-service → payment-service every ~4 hours. Further analysis: the retransmits coincide with the payment-service pod being evicted and rescheduled (resource pressure). During pod restart, kube-proxy updates iptables — for ~2-3 seconds, traffic routes to the old pod IP (which is gone) until iptables is updated. TCP retransmits during this window = latency spike. Network Observability revealed what APM couldn't: the network-level manifestation of a Kubernetes eviction cycle.

---

### 🧠 Mental Model / Analogy

> Network Observability is like an X-ray combined with a real-time GPS tracker for your network. Traditional monitoring is like taking someone's temperature (know they're sick) but network observability is like seeing which organ is causing the fever and watching the blood flow in real-time. eBPF is the X-ray machine built into the kernel itself — it shows you what's happening inside without surgery (code changes). Flow logs are the GPS: they tell you every car's journey, but not what they were thinking. The combination — flows + eBPF traces + metrics + logs — is a complete picture.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Network Observability = seeing what's happening in your network. Key tools: VPC Flow Logs (who talked to whom, allowed/denied), tcpdump (packet-level inspection), Prometheus metrics (bytes/sec, connection counts). In Kubernetes: Cilium Hubble gives a live map of all pod-to-pod communication.

**Level 2:** Layer-aware debugging: DNS issues (dig, CoreDNS logs), connection-level (ss, netstat), flow-level (VPC Flow Logs, Hubble). Alert on retransmit rate (> 1% = packet loss), DNS latency (p99 > 10ms), connection establishment time (p99 > 50ms). eBPF tools (tcpretrans, tcpconnect) give kernel-level visibility without code changes.

**Level 3:** AWS network observability stack: VPC Flow Logs → S3 → Athena (ad-hoc queries), or → CloudWatch Insights (live queries). AWS Network Firewall: detailed connection logs. AWS Reachability Analyser: verify connectivity without sending traffic. CloudWatch Network Monitor: synthetic monitoring for cross-VPC/Transit Gateway paths. Kubernetes: Cilium Hubble (L3/L4/L7 flows) + Prometheus node_exporter (interface metrics) + CoreDNS metrics + Istio/Envoy metrics (per-service latency).

**Level 4:** Streaming network telemetry for large-scale observability: BGP-based routing observability (BGPmon, looking glasses for global route monitoring), SNMP polling vs gNMI streaming telemetry (push-based, sub-second granularity). eBPF XDP (Express Data Path) for high-speed packet classification: runs at NIC driver level, before kernel network stack, enabling line-rate packet processing for observability (capturing flow statistics at 10Gbps without CPU overhead). Clickhouse or Apache Druid for storing and querying billions of flow records: columnar storage enables fast analytical queries over raw flow data (e.g., "top-talker IPs in the last 5 minutes" at trillion-record scale).

---

### ⚙️ How It Works (Mechanism)

```bash
# 1. tcpdump: raw packet capture (development/debugging)
# Capture traffic between two pods (by IP)
tcpdump -i eth0 -n \
  "host 10.244.1.5 and host 10.244.2.10" \
  -w /tmp/capture.pcap

# Filter by port (HTTP/HTTPS)
tcpdump -i eth0 -n "port 8080 or port 443" -v

# Decode HTTP traffic (plaintext only)
tcpdump -i eth0 -A "port 8080" | grep -E "GET|POST|HTTP|Host:"

# 2. ss: connection state inspection
ss -tunaop  # all connections with process info
# Check established connections to specific port
ss -tnp state established '( dport = :8080 )'

# TCP retransmit rate
cat /proc/net/snmp | grep Tcp
# RetransSegs / OutSegs = retransmit rate (should be < 1%)

# 3. eBPF tools (bcc-tools package)
# TCP connections in real-time
/usr/share/bcc/tools/tcpconnect

# TCP retransmits with reason
/usr/share/bcc/tools/tcpretrans -l  # include header lines

# DNS latency per query
/usr/share/bcc/tools/gethostlatency

# 4. Cilium Hubble (Kubernetes)
# Install Hubble CLI
# hubble observe: live flows
hubble observe --namespace production --follow

# Flows dropped by network policy
hubble observe --verdict DROPPED --namespace production

# HTTP request visibility
hubble observe --namespace production --protocol http

# 5. AWS VPC Flow Logs analysis (Athena)
# Query: find all rejected traffic from specific source
cat << 'SQL'
SELECT srcaddr, dstaddr, dstport, COUNT(*) AS count
FROM vpc_flow_logs
WHERE action = 'REJECT'
  AND start > to_unixtime(now() - interval '1' hour)
GROUP BY srcaddr, dstaddr, dstport
ORDER BY count DESC
LIMIT 20;
SQL
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Diagnosing a Kubernetes network issue using layered observability:

SYMPTOM: checkout-service → payment-service calls failing 5% of the time

1. APM (Jaeger): shows payment-service calls with "connection refused" errors
   → Network issue, not application issue

2. Hubble flows:
   hubble observe --verdict DROPPED --pod production/checkout-service
   → Output: DROP from checkout (10.244.1.5) to payment-service (10.244.2.10)
     Reason: "POLICY_DENIED"
   → A NetworkPolicy is blocking some connections

3. kubectl get networkpolicies -n production
   → Found: "allow-checkout-to-payment" policy exists
   → But policy only allows port 8080; payment-service recently added port 8443
   
4. Verify with Hubble:
   hubble observe --pod production/payment-service -t policy-verdict
   → Ingress from checkout allowed on 8080, DENIED on 8443

5. Fix: update NetworkPolicy to allow port 8443
6. Verify: Hubble shows ALLOWED verdict for both ports

WITHOUT Hubble: would need to check NetworkPolicies manually,
try curl from inside pods, add tcpdump to check packets — much slower
```

---

### 💻 Code Example

```python
# Query AWS VPC Flow Logs via Athena for network analysis
import boto3
import time

def query_vpc_flow_logs(
    database: str,
    table: str,
    source_ip: str = None,
    dest_ip: str = None,
    action: str = None,
    hours_back: int = 1
) -> list[dict]:
    """Query VPC Flow Logs stored in S3 via Athena."""
    athena = boto3.client('athena', region_name='us-east-1')
    
    # Build query
    conditions = [f"start > (to_unixtime(now()) - {hours_back * 3600})"]
    if source_ip:
        conditions.append(f"srcaddr = '{source_ip}'")
    if dest_ip:
        conditions.append(f"dstaddr = '{dest_ip}'")
    if action:
        conditions.append(f"action = '{action}'")
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
    SELECT srcaddr, dstaddr, srcport, dstport, protocol,
           action, packets, bytes,
           from_unixtime(start) AS start_time
    FROM {database}.{table}
    WHERE {where_clause}
    ORDER BY packets DESC
    LIMIT 100
    """
    
    # Start query execution
    response = athena.start_query_execution(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': 's3://my-bucket/athena-results/'
        }
    )
    query_id = response['QueryExecutionId']
    
    # Wait for completion
    for _ in range(30):
        status = athena.get_query_execution(QueryExecutionId=query_id)
        state = status['QueryExecution']['Status']['State']
        if state in ('SUCCEEDED', 'FAILED', 'CANCELLED'):
            break
        time.sleep(2)
    
    if state != 'SUCCEEDED':
        raise RuntimeError(f"Query failed: {state}")
    
    # Fetch results
    result = athena.get_query_results(QueryExecutionId=query_id)
    headers = [col['Label'] for col in result['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [
        dict(zip(headers, [field.get('VarCharValue', '') for field in row['Data']]))
        for row in result['ResultSet']['Rows'][1:]  # skip header row
    ]
    return rows

# Find rejected traffic from a suspicious IP
# flows = query_vpc_flow_logs("mydb", "vpc_flow_logs", 
#                             source_ip="203.0.113.1", action="REJECT")
```

---

### ⚖️ Comparison Table

| Tool | Scope | Data Type | Overhead | Best For |
|---|---|---|---|---|
| VPC Flow Logs | AWS VPC | IP flows (L3/L4) | Low (async) | Cloud network audit, security |
| Cilium Hubble | Kubernetes | L3/L4/L7 flows + DNS | Low (eBPF) | K8s pod connectivity debug |
| tcpdump | Single host | Raw packets (L2-L7) | Medium-High | Deep protocol debugging |
| Prometheus node_exporter | All hosts | Aggregated metrics | Low | Alerting on interface stats |
| eBPF (bcc/bpftrace) | Single host | Kernel-level events | Low | Root cause analysis |
| AWS Reachability Analyser | AWS | Path simulation | None | Verify connectivity design |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| tcpdump is safe for production | tcpdump in promiscuous mode captures ALL traffic on the interface, including unrelated services. CPU and memory impact at high packet rates can be significant. In production: use eBPF-based tools (tcpretrans, Hubble) for production-safe continuous observation; use tcpdump only for short, targeted captures |
| VPC Flow Logs show all traffic | VPC Flow Logs capture flows at the ENI level, with a 1-15 minute aggregation window. They do NOT show: blocked traffic before it reaches the ENI (e.g., Security Group blocks at the EC2 hypervisor level — actually they DO show these as REJECT). They do NOT show inter-pod traffic within a node (all on the same ENI) |
| Network observability is only for network teams | In microservices architectures, network issues manifest as application errors. Service and platform engineers need network visibility to diagnose: DNS failures, connection pool exhaustion, NetworkPolicy misconfigurations, and cross-AZ latency — all of which look like "slow service" in APM |

---

### 🚨 Failure Modes & Diagnosis

**Silent DNS Failures Causing Random Service Errors**

```bash
# Symptom: random 5xx errors, no obvious pattern in APM
# Cause: intermittent DNS resolution failures for internal services

# Step 1: check DNS query failure rate
# Kubernetes CoreDNS metrics
kubectl port-forward -n kube-system svc/kube-dns 9153:9153
curl -s localhost:9153/metrics | grep -E "coredns_dns_responses_total|coredns_forward_request_failures"
# If coredns_dns_responses_total{rcode="SERVFAIL"} increasing: DNS failures

# Step 2: capture DNS traffic with eBPF (no overhead)
/usr/share/bcc/tools/gethostlatency
# Shows: process name, hostname being resolved, latency
# High latency (>5ms for internal) or failures: CoreDNS problem

# Step 3: Hubble DNS visibility
hubble observe --type dns --namespace production --follow
# Shows: which pod queries which hostname, answer, latency
# Look for NXDOMAIN or timeout responses

# Step 4: manual DNS test from affected pod
kubectl exec -n production deploy/checkout-service -- \
  for i in $(seq 1 100); do 
    time nslookup payment-service.production.svc.cluster.local 2>&1 | tail -1
  done
# If some queries return in >100ms: DNS latency issue

# Step 5: check CoreDNS resources
kubectl top pod -n kube-system -l k8s-app=kube-dns
# If CPU throttled: CoreDNS is under-resourced
# Fix: increase CoreDNS replicas and resource limits
kubectl scale deployment -n kube-system coredns --replicas=3

# Step 6: ndots configuration (common issue)
kubectl exec -n production deploy/checkout-service -- cat /etc/resolv.conf
# ndots:5 means: 5+ dots required to treat as absolute
# "payment-service" → tries production.svc.cluster.local, svc.cluster.local,
#   cluster.local, BEFORE bare "payment-service" — 5 DNS queries per lookup!
# Fix: use FQDN (payment-service.production.svc.cluster.local.) or ndots:2
```

---

### 🔗 Related Keywords

**Prerequisites:** `Observability & SRE`, `Networking`, `Distributed Systems`

**Related:** `East-West vs North-South Traffic`, `Packet Loss, Latency & Jitter`, `BGP`, `mTLS`, `Service Discovery`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FLOW LOGS    │ Who talked to whom, allowed/rejected       │
│              │ AWS VPC Flow Logs, Cilium Hubble            │
├──────────────┼───────────────────────────────────────────┤
│ eBPF TOOLS   │ Kernel-level; no code changes; low overhead│
│              │ tcpretrans, tcpconnect, gethostlatency     │
├──────────────┼───────────────────────────────────────────┤
│ METRICS      │ Retransmit rate (<1%), DNS latency (<5ms)  │
│              │ Connection churn, interface bytes/sec      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "See every packet, flow, and connection in │
│              │ your network — without touching app code"  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a comprehensive network observability platform for a 500-service microservices system on Kubernetes, with security, performance, and compliance requirements. (a) Define the data collection strategy: Cilium Hubble for L3/L4/L7 pod flows, Prometheus for aggregated metrics, VPC Flow Logs for cloud-level audit, CoreDNS metrics for DNS health — what is the data volume per day (estimate: 500 services × 100 flows/sec = 50,000 flows/sec = 4.3B flows/day) and how do you store and query it cost-effectively (ClickHouse, Loki, CloudWatch). (b) Design security use cases: how do you detect lateral movement (a pod suddenly communicating with services it never contacted before)? Define the anomaly detection approach using flow baseline establishment + statistical deviation alerting. (c) SLO for network observability: if your Cilium Hubble relay goes down, you lose network visibility but services continue operating. Design an SLO for the observability platform itself (99.9% uptime = 8.7h downtime/year is acceptable for observability tooling vs 99.99% for the services themselves). (d) Cost management: VPC Flow Logs cost $0.05/GB and a large cluster generates 100GB/day = $150/month. Describe sampling strategies (sample 1% of flows, always capture security-relevant flows like rejected connections) that reduce cost by 90% while preserving security observability.
