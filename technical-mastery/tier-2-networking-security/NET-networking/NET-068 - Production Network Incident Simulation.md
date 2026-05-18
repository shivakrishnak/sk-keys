---
id: NET-068
title: "Production Network Incident Simulation"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★★★
depends_on: NET-049, NET-063
used_on: NET-075, NET-083
used_by: NET-075, NET-083
related: NET-049, NET-063, NET-075
tags:
  - networking
  - incident-simulation
  - hands-on
  - debugging
  - production
  - troubleshooting
  - lab
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 68
permalink: /technical-mastery/net/production-network-incident-simulation/
---

**⚡ TL;DR** - This entry is a series of realistic
production network incident scenarios you can run in
your local environment. Each scenario: inject the
problem, simulate being paged, diagnose from metrics
and logs, fix it, and write the postmortem. Scenarios
cover: connection pool exhaustion, DNS failure, TCP
retransmit cascade, MTU mismatch causing silent packet
drop, and a firewall misconfiguration blocking traffic.
Run these before on-call. The muscle memory of
systematic diagnosis matters more than memorizing commands.

| #068 | Category: Networking | Difficulty: ★★★★ |
|:---|:---|:---|
| **Depends on:** | Wireshark and tcpdump (NET-049), Network Observability (NET-063) | |
| **Used by:** | Build a Secure Network Platform (NET-075), Networking Career Paths (NET-083) | |
| **Related:** | Wireshark and tcpdump, Network Observability, Build a Secure Network Platform | |

---

### 🔥 Why Practice Incidents?

Reading about debugging is different from doing it.
Production incidents arrive at 3 AM with incomplete
context, ambiguous metrics, and pressure. Systematic
diagnostic habits only come from practice. These
simulations create the cognitive pattern: "What do I
know? What would I check next? What does this metric
tell me?" Run each scenario without reading the solution
first. Time yourself. Write the postmortem.

---

### ⚙️ Setup: Local Environment

```bash
# Requirements: Docker and docker-compose
# All simulations run locally

# Install netshoot (diagnostic container with all network tools):
docker pull nicolaka/netshoot

# Start base infrastructure:
cat > docker-compose.yml << 'EOF'
version: "3"
services:
  app:
    image: python:3.11
    command: >
      python3 -c "
      import http.server, socketserver
      with socketserver.TCPServer(('', 8080), http.server.SimpleHTTPRequestHandler) as h:
        h.serve_forever()
      "
    ports:
      - "8080:8080"
    networks:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    networks:
      - backend

  client:
    image: nicolaka/netshoot
    command: sleep infinity
    networks:
      - backend

networks:
  backend:
    driver: bridge
EOF

docker-compose up -d
```

---

### ⚙️ Scenario 1 - Connection Pool Exhaustion

**Setup (inject the problem):**

```bash
# Simulate a service that creates new DB connection per request:
cat > leaky_app.py << 'EOF'
import psycopg2
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # BAD: new connection per request (never pooled)
        conn = psycopg2.connect(
            host="db", user="postgres",
            password="secret", dbname="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT pg_sleep(0.1), 'data'")
        result = cursor.fetchone()
        # NOT closing connection properly
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

HTTPServer(('', 9090), Handler).serve_forever()
EOF

docker-compose exec client python3 /app/leaky_app.py &

# Simulate load:
for i in $(seq 1 200); do
    curl -s http://app:9090/ &
done
wait
```

**Symptoms (what you'd see when paged):**

```
Alert: HTTP 500 error rate > 10% (from monitoring)
Error in app logs: "too many connections for role postgres"
Service: timing out or returning 500 errors under load
```

**Diagnostic commands:**

```bash
# Check: how many connections to PostgreSQL?
docker-compose exec db psql -U postgres -c \
  "SELECT count(*), state FROM pg_stat_activity GROUP BY state"
# Expected healthy: ~5 active, ~0 idle
# Broken: 100+ connections, hitting max_connections limit

# Check: what are all those connections doing?
docker-compose exec db psql -U postgres -c \
  "SELECT pid, state, wait_event_type, query_start, query
   FROM pg_stat_activity WHERE datname = 'postgres'
   ORDER BY query_start LIMIT 20"

# Check connection rate from app:
docker-compose exec client \
  ss -nt "dst 5432" | wc -l
# High number = connection leak

# Check: does the connection count grow with each request?
watch -n1 "docker-compose exec db psql -U postgres -c \
  \"SELECT count(*) FROM pg_stat_activity\""
```

**Fix:**

```python
# Add connection pooling with psycopg2.pool:
from psycopg2 import pool

db_pool = pool.ThreadedConnectionPool(
    minconn=2, maxconn=10,
    host="db", user="postgres",
    password="secret", dbname="postgres"
)

def get_data():
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 'data'")
        return cursor.fetchone()
    finally:
        db_pool.putconn(conn)  # Always return to pool
```

**Postmortem (write this after fixing):**

```
Incident: DB connection exhaustion causing 500 errors
Timeline: 14:30 alert → 14:32 root cause → 14:40 fix deployed
Root cause: per-request connection creation in handler
Contributing factor: no connection limit enforced at app level
Fix: thread-safe connection pool, maxconn=10
Prevention: code review checklist for DB connection patterns
Monitoring added: hikaricp_pending_threads or pg_stat_activity count alert
```

---

### ⚙️ Scenario 2 - DNS Failure Cascade

**Setup (inject the problem):**

```bash
# Simulate DNS failure by adding bad resolv.conf
docker-compose exec client bash -c \
  "echo 'nameserver 10.255.255.255' > /etc/resolv.conf"
# Now DNS queries time out (10.255.255.255 is unreachable)
```

**Symptoms:**

```
Alert: service-to-service calls failing (connection timeout, not refused)
Timeout: typically 30-60 seconds (DNS timeout)
Logs: "dial tcp: lookup service-name: no such host"
      or "could not translate host name to address"
Different from: ECONNREFUSED (which fails instantly)
```

**Diagnostic commands:**

```bash
# Test DNS resolution directly:
docker-compose exec client nslookup db
# Timeout = DNS not working

# Check which nameserver is configured:
cat /etc/resolv.conf
# Shows: nameserver 10.255.255.255 (broken!)
# Should be: nameserver 127.0.0.11 (Docker internal DNS)

# Verify DNS resolution timing:
time nslookup db 127.0.0.11   # with correct nameserver
time nslookup db              # with broken nameserver

# Check DNS query timeout behavior:
dig +time=2 +tries=1 db
# If timeout: DNS is unreachable

# Check if it's all DNS or specific:
docker-compose exec client nslookup google.com
docker-compose exec client nslookup db
# If both fail: entire DNS resolution broken
# If only internal: Kubernetes DNS or Docker DNS issue

# K8s equivalent diagnostic:
kubectl exec -it test-pod -- nslookup kubernetes.default
kubectl exec -it test-pod -- cat /etc/resolv.conf
kubectl get pods -n kube-system | grep dns
```

**Fix:**

```bash
# Restore correct DNS:
docker-compose exec client bash -c \
  "echo 'nameserver 127.0.0.11' > /etc/resolv.conf"

# In production: fix the DNS server, not /etc/resolv.conf
# For K8s: restart coredns pods if stuck
kubectl rollout restart deployment coredns -n kube-system
```

---

### ⚙️ Scenario 3 - Firewall Rule Blocking Traffic

**Setup (inject the problem):**

```bash
# Block traffic to the app on port 8080 using iptables
docker-compose exec app iptables -A INPUT -p tcp \
  --dport 8080 -j DROP
# Now all connections to 8080 will be silently dropped
```

**Symptoms:**

```
Alert: HTTP probe failing (blackbox_probe_success == 0)
Client: connection timeout (not connection refused)
Timeout: 30s+ (TCP SYN sent, no response, retry)
Service logs: no requests arriving (dropped before reaching app)
Different from: ECONNREFUSED (service not running = RST immediately)
```

**Diagnostic commands:**

```bash
# Test from client (takes 30s to timeout = DROP, not REJECT):
time curl -v http://app:8080/

# Compare with a known-blocked (REJECT gives instant ECONNREFUSED):
# DROP = silent discard = timeout
# REJECT = RST sent = immediate ECONNREFUSED

# Check if packets reach the server with tcpdump:
docker-compose exec app tcpdump -i eth0 -n "port 8080" &
docker-compose exec client curl http://app:8080/
# If SYN visible in tcpdump but no SYN-ACK: firewall dropping
# If no SYN visible: dropped before reaching host

# Check iptables rules on the server:
docker-compose exec app iptables -L INPUT -n -v
# Look for DROP rule on port 8080

# In cloud (AWS): check security group inbound rules
# In K8s: check NetworkPolicy
kubectl get networkpolicy -n default
```

**Fix:**

```bash
# Remove the DROP rule:
docker-compose exec app iptables -D INPUT -p tcp \
  --dport 8080 -j DROP

# Verify:
docker-compose exec client curl http://app:8080/
```

---

### ⚙️ Scenario 4 - MTU Mismatch (Silent Packet Drop on Large Transfers)

**Setup (inject the problem):**

```bash
# Reduce MTU on client interface to simulate tunnel overhead:
docker-compose exec client ip link set eth0 mtu 576
# Now large packets (> 576 bytes) are dropped
```

**Symptoms:**

```
Service: small HTTP requests succeed (headers fit in 576B)
Service: large responses fail (body > 576B gets dropped)
Curl: hangs after headers (body never arrives)
tcpdump: TCP SYN/SYNACK/data... then retransmits endlessly
```

**Diagnostic commands:**

```bash
# Small request works:
docker-compose exec client curl -s http://app:8080/ | head -c 100

# Large request hangs:
docker-compose exec client curl -v http://app:8080/largefile &

# Check interface MTU:
docker-compose exec client ip link show eth0
# mtu 576 << should be 1500

# Test with explicit packet sizes:
docker-compose exec client ping -M do -s 548 app   # 548+28=576: ok
docker-compose exec client ping -M do -s 549 app   # 549+28=577: fail

# Tracepath to find bottleneck:
docker-compose exec client tracepath app
# Shows pmtu at each hop

# TCP capture to see retransmits:
docker-compose exec app tcpdump -i eth0 -n "port 8080"
# See: data packets, then retransmits after timeout
# Retransmit pattern: 200ms, 400ms, 800ms (exponential backoff)
```

**Fix:**

```bash
# Restore correct MTU:
docker-compose exec client ip link set eth0 mtu 1500
# Or: set MSS clamping on the server
docker-compose exec app iptables -t mangle -A INPUT \
  -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --clamp-mss-to-pmtu
```

---

### ⚙️ Systematic Incident Response Framework

```
WHEN PAGED: use this sequence

1. ASSESS (2 minutes):
   What is the user-visible impact?
   What changed recently? (deploys, config, traffic increase)
   What metrics are elevated? (error rate, latency, CPU, network)

2. ISOLATE (5 minutes):
   Is it all traffic or specific users/regions?
   Is it all requests or specific endpoints?
   Is it the network (timeout) or application (500)?
   Network timeout → DNS, firewall, routing, overload
   Application error → code, DB, downstream service

3. DIAGNOSE (10 minutes):
   Use the appropriate tool:
   Connection refused → service not running, wrong port
   Connection timeout → firewall DROP, overloaded, DNS fail
   High latency → network path, slow query, GC pause
   Packet loss → retransmits, queue drops, MTU issue

4. MITIGATE (5 minutes):
   Stop the bleeding: rollback, scale out, enable circuit breaker
   Don't wait for root cause to mitigate

5. VERIFY (2 minutes):
   Metrics returning to baseline?
   Test request succeeds?
   No new alerts?

6. POSTMORTEM (after incident):
   Timeline with timestamps
   Root cause (specific line in config, specific deploy)
   Contributing factors (why wasn't it caught earlier?)
   Action items: monitoring, testing, process changes
```

---

### 📐 Scale Considerations

```
Local simulation vs production scale:
  Local: single container, single failure
  Production: distributed, multiple simultaneous failures
  
  Complexity increase:
  Local: iptables rule on one container
  Production: security group change across 100 instances
  Local: one DNS resolver broken
  Production: CoreDNS overloaded under high service count

  Practice both single-node and distributed scenarios
  Distributed: use chaos engineering tools

Chaos engineering tools for production:
  Chaos Mesh (Kubernetes): inject pod failures, network delays
  AWS Fault Injection Simulator: production-scale experiments
  Gremlin: paid, feature-rich, network impairment
  Litmus Chaos: open source K8s chaos

Network chaos injection examples:
  Add 100ms latency to specific service calls
  Drop 5% of packets to one downstream service
  Saturate egress bandwidth of one node
  Inject DNS failures for specific domains
  
  Purpose: build confidence that circuit breakers, retries,
  and timeouts work before a real outage
```

---

### 🧭 Decision Guide

```
Scenario selection by learning goal:

"I want to understand connection exhaustion":
  Run Scenario 1 multiple times
  Vary: max_connections, request rate, connection hold time

"I want to understand DNS failure modes":
  Run Scenario 2
  Also try: SERVFAIL vs NXDOMAIN vs timeout
  kubectl delete pods -n kube-system -l k8s-app=kube-dns (K8s DNS)

"I want to understand firewall debugging":
  Run Scenario 3
  Also: try with REJECT instead of DROP (instant vs timeout)
  Try: iptables LOG rule to see what's being dropped

"I want to understand MTU issues":
  Run Scenario 4
  Test: different MTU values, different payload sizes
  Add: VPN overhead simulation (reduce MTU further)

"I want full incident practice":
  Run all 4 scenarios in a random order
  Don't look at the diagnosis section first
  Time yourself from "alert fires" to "mitigation complete"
  
On-call preparation:
  Run each scenario quarterly
  Bring new team members through the simulations
  Write and test your runbooks against these scenarios
  The runbook should work without the person who wrote it
```