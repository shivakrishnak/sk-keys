---
id: LNX-034
title: "Network Tools (curl, wget, netstat, ss)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-023, LNX-006
used_by: LNX-045, LNX-055
related: LNX-023, LNX-045, NET-001
tags: [curl, wget, netstat, ss, network, http, download, port, connection, debugging]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 34
permalink: /technical-mastery/lnx/network-tools/
---

## TL;DR

`curl` makes HTTP requests and shows responses (the Swiss Army knife for
HTTP debugging). `wget` downloads files. `ss -tlnp` shows listening
ports and which process owns them. `netstat -tlnp` is the older
equivalent (requires `net-tools`). Key production skills: `curl -v URL`
for full HTTP debug, `ss -tlnp | grep :8080` to verify an app is
listening, `curl -I URL` for response headers only. Master `curl` first -
it's everywhere.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-034 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | curl, wget, ss, netstat, HTTP, download, connection, port listening |
| **Prerequisites** | LNX-023, LNX-006 |

---

### The Problem This Solves

API endpoint returning 500 errors. Is it a DNS issue, a TLS issue, a
load balancer issue, or the application itself? `curl -v https://api.example.com/health`
shows exactly: DNS resolution, TCP connection, TLS handshake, HTTP request,
response headers, and response body - in one command. Without curl, you'd
need to guess which layer is failing. `ss -tlnp` confirms whether your
application is actually listening on the expected port.

---

### Textbook Definition

**curl** (Client URL): Command-line tool for transferring data using
URLs. Supports HTTP, HTTPS, FTP, SFTP, and more. Indispensable for
API testing, HTTP debugging, downloading files, and testing network
connectivity to specific ports.

**wget**: Command-line file downloader. Simpler than curl for downloading.
Supports recursive download, resuming interrupted downloads. HTTP/FTP.

**ss** (socket statistics): Modern replacement for `netstat`. Shows socket
information: listening ports, established connections, process names. Part of
the `iproute2` package (always available on modern Linux).

**netstat**: Older network statistics tool (from `net-tools` package, may
not be installed). Same capabilities as ss but slower. On modern systems,
prefer ss.

---

### Understand It in 30 Seconds

```bash
# CURL - HTTP requests and debugging:
curl http://example.com               # GET request
curl -v https://api.example.com       # verbose: show headers and TLS
curl -I https://example.com           # HEAD request: headers only
curl -X POST https://api.example.com/users \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer TOKEN" \
    -d '{"name":"Alice","email":"a@example.com"}'

curl -s https://example.com > output.html   # save to file (-s=silent)
curl -o file.tar.gz https://example.com/file.tar.gz  # download to file

# Follow redirects:
curl -L https://example.com           # -L = follow redirects

# Test TCP port without HTTP:
curl -v telnet://host:port            # test raw TCP
curl -v smtp://mailserver:25          # test SMTP

# WGET - downloading files:
wget https://example.com/file.tar.gz  # download
wget -c https://example.com/big.file  # resume interrupted download
wget -r -np https://docs.example.com/ # recursive download
wget -O - https://example.com/script.sh | bash  # run downloaded script

# SS - port and connection status:
ss -tlnp                  # TCP Listening ports + process Names
ss -ulnp                  # UDP listening
ss -an                    # all connections (all states)
ss -tnp                   # established TCP connections
ss -tnp | grep :8080      # connections to port 8080
ss -s                     # summary statistics

# NETSTAT (older alternative):
netstat -tlnp             # TCP listening ports
netstat -an               # all connections
netstat -s                # protocol statistics
```

---

### First Principles

**curl's layered output (-v):**
`curl -v` reveals each protocol layer in sequence:
```
* Trying 93.184.216.34:443...     <- DNS resolved, TCP connecting
* Connected to example.com        <- TCP connection established
* ALPN: offers h2,http/1.1       <- TLS negotiation starting
* TLSv1.3 (OUT), TLS handshake   <- TLS handshake
* Server certificate:             <- cert info
* SSL connection using TLSv1.3   <- TLS established
> GET / HTTP/1.1                  <- HTTP request sent
> Host: example.com               <- request headers (> = sent)
>
< HTTP/1.1 200 OK                 <- response status (< = received)
< Content-Type: text/html         <- response headers
<
[response body]
```

Each layer can fail independently. This is why `-v` is the first debugging
tool for HTTP issues.

**ss output columns:**
```
State  Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN 0       128     0.0.0.0:8080        0.0.0.0:*          users:(("java",pid=1234))

State: LISTEN (waiting), ESTABLISHED (connected), TIME_WAIT (closing)
Recv-Q: received but not read by application (backpressure indicator)
Send-Q: sent but not acknowledged (TCP buffer)
Local: service's IP:port
Peer: client's IP:port (* = any, for LISTEN state)
Process: which program and PID owns this socket
```

---

### Thought Experiment

Deployment failed. Application is supposed to be running on port 8080
but clients get "connection refused."

```bash
# Step 1: is the process running?
ps aux | grep java         # or: pgrep -a java

# Step 2: is it listening on port 8080?
ss -tlnp | grep 8080
# Case A: no output -> process is running but not listening yet
#   (still starting up?) or bound to wrong port
# Case B: 127.0.0.1:8080 -> listening on loopback only
#   (clients from outside can't connect)
# Case C: 0.0.0.0:8080 -> correct, listening on all interfaces

# Step 3: can I connect from localhost?
curl -v http://localhost:8080/health

# Step 4: if local works, is it a firewall issue?
# Test from the client machine:
curl -v http://SERVER_IP:8080/health

# Step 5: check firewall rules
iptables -L INPUT -n | grep 8080

# Root cause: Spring Boot application.properties had:
# server.address=127.0.0.1 (should be 0.0.0.0 or not set)
```

---

### Mental Model / Analogy

`curl -v` is like **calling a business and asking for a detailed transcript
of the entire call:**

```
curl -v https://api.example.com/health

Dialing (TCP):   "Trying 203.0.113.50:443... Connected!"
ID check (TLS):  "Verifying certificate... Valid!"
Request (HTTP):  "GET /health HTTP/1.1" + your request headers
Response:        "HTTP/1.1 200 OK" + their response headers + body

If ANY step fails, curl shows exactly WHICH step failed:
- DNS failure: "Could not resolve host"
- TCP failure: "Connection refused" or "Connection timed out"  
- TLS failure: "SSL certificate problem"
- HTTP failure: 4xx or 5xx status codes

ss -tlnp = checking if the business has their phone plugged in
(is there someone listening on that port?)
```

---

### Gradual Depth - Five Levels

**Level 1:**
`curl URL` (GET request), `curl -v URL` (verbose debug), `curl -I URL`
(headers only), `ss -tlnp` (listening ports). These 4 cover most
HTTP/network debugging needs.

**Level 2:**
POST with JSON: `curl -X POST -H "Content-Type: application/json"
-d '{"key":"value"}' URL`. Headers: `-H "Key: Value"`. Auth:
`-H "Authorization: Bearer TOKEN"` or `-u user:password`.
Save output: `-o file`. Follow redirects: `-L`. Timing: `--write-out`
for response time. Timeout: `--connect-timeout 5 --max-time 30`.

**Level 3:**
`curl -w "%{time_total}\n" -o /dev/null -s URL` for timing only.
`curl --resolve hostname:443:IP URL` to bypass DNS and test specific
server. Client certificates: `--cert cert.pem --key key.pem`.
`curl --cacert ca.pem` for custom CA. Cookie jar: `--cookie-jar cookies.txt`.
Form upload: `-F "file=@/path/to/file"`.

**Level 4:**
Scripting with curl: `RESPONSE=$(curl -sf URL)` (-s = silent, -f =
fail on HTTP errors). `HTTP_CODE=$(curl -w "%{http_code}" -o /dev/null -s URL)`.
curl for REST API testing in shell scripts. `ss -o` for timer info
(detect stuck connections). `ss state established '( dport = :8080 )'`
(filter by state and port). Connection tracking: number of connections to
a port: `ss -tnp | grep :8080 | wc -l`.

**Level 5:**
`curl --http2` to force HTTP/2. `curl --http3` for HTTP/3/QUIC.
`--compressed` for automatic decompression. `--parallel` for concurrent requests.
`curl` for service mesh debugging (Istio/Envoy sidecar injection affects
curl from within pods). `mkcert` + curl for local HTTPS development.
For production API testing at scale: `k6` or `hey` or `wrk` (purpose-built
load testing tools that use curl-like semantics but with concurrency and
reporting).

---

### Code Example

**BAD - curl antipatterns:**
```bash
# BAD 1: not handling curl exit code in scripts
curl http://api.example.com/endpoint
RESPONSE=$?
# curl returns 0 even on HTTP 404/500!
# curl exit code is about the TRANSFER, not the HTTP status code

# GOOD: use -f to fail on HTTP errors (4xx/5xx):
curl -f http://api.example.com/endpoint
# Now exit code 22 on HTTP 4xx/5xx

# BAD 2: piping untrusted content to bash (security risk)
curl https://untrusted-site.com/install.sh | bash
# The script could do ANYTHING with root privileges!
# If you must: download first, inspect, then execute
curl -o install.sh https://example.com/install.sh
cat install.sh   # READ IT FIRST
bash install.sh

# BAD 3: hardcoding credentials in curl command (visible in ps)
curl -H "Authorization: Bearer MY_SECRET_TOKEN" https://api.example.com
# Token visible in: ps aux, shell history, log files

# GOOD: read from environment variable
curl -H "Authorization: Bearer ${API_TOKEN}" https://api.example.com
# Or: use a config file
curl -K /etc/mycurl.conf https://api.example.com
# ~/.netrc for credentials (chmod 600)
```

**GOOD - production curl patterns:**
```bash
# Health check script with proper error handling:
check_health() {
    local url="$1"
    local timeout="${2:-10}"
    
    HTTP_CODE=$(curl \
        --silent \
        --output /dev/null \
        --write-out "%{http_code}" \
        --connect-timeout "$timeout" \
        --max-time "$((timeout * 2))" \
        "$url")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "HEALTHY: $url -> $HTTP_CODE"
        return 0
    else
        echo "UNHEALTHY: $url -> $HTTP_CODE" >&2
        return 1
    fi
}

# Time an API endpoint:
curl -w "
  time_dns:        %{time_namelookup}s
  time_connect:    %{time_connect}s
  time_ssl:        %{time_appconnect}s
  time_ttfb:       %{time_starttransfer}s
  time_total:      %{time_total}s
  http_code:       %{http_code}
" -o /dev/null -s https://api.example.com/endpoint

# Test all servers behind a load balancer:
for server in web1 web2 web3; do
    echo -n "$server: "
    curl --resolve "api.example.com:443:$(dig +short $server)" \
        -s -o /dev/null -w "%{http_code}" \
        https://api.example.com/health
    echo ""
done

# Monitor connection count to a service:
watch -n 1 "ss -tnp | grep :8080 | wc -l"
# Shows how many clients are connected to port 8080, updated every second

# Find which process is using port 8080:
ss -tlnp | grep :8080
# Or: fuser 8080/tcp   (shows PID)
# Or: lsof -i :8080    (more details)
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "curl exit code 0 means the request succeeded" | curl exit code 0 means the TRANSFER completed, not that the HTTP response was successful. `curl -f` (fail-on-error) makes curl return non-zero on HTTP 4xx/5xx. Without `-f`: `curl https://example.com/returns-500` = exit code 0. With `-f`: exit code 22. |
| "ss and netstat -tlnp show the same thing" | Mostly, but ss is much faster on systems with many connections (netstat must read /proc/net/tcp line-by-line; ss uses the kernel netlink API). ss also has more filtering options. On modern systems, ss is preferred; netstat may not even be installed. |
| "wget and curl are interchangeable" | wget is optimized for downloading: resumable (`-c`), recursive website download (`-r`), background (`-b`). curl is optimized for protocol flexibility: REST APIs, POST data, headers, auth, timing info, HTTP/2. For downloading: either works. For API testing or debugging: curl is the right tool. |
| "nc -zv is a substitute for curl" | `nc -zv host port` tests TCP connectivity only (can I connect to this port?). curl tests the full HTTP/HTTPS stack: DNS, TCP, TLS, HTTP protocol. Use nc for "can I reach the port?", use curl for "does the HTTP service work?" |
| "curl shows the full TLS certificate chain" | `curl -v` shows certificate subject and issuer. For the FULL chain: `openssl s_client -connect host:443 -showcerts`. For certificate expiry checking: `echo | openssl s_client -connect host:443 2>/dev/null | openssl x509 -noout -dates`. |

---

### Failure Modes & Diagnosis

**"curl: (60) SSL certificate problem":**
```bash
# Problem: certificate not trusted
curl https://api.example.com
# curl: (60) SSL certificate problem: certificate has expired

# Diagnose: view cert details
openssl s_client -connect api.example.com:443 < /dev/null 2>/dev/null | \
    openssl x509 -noout -dates -subject

# Options:
# 1. Fix: renew the certificate (the correct fix)
# 2. Bypass for testing ONLY (NEVER in production):
curl -k https://api.example.com    # insecure: skip cert verification
# Security warning: -k makes you vulnerable to MITM attacks

# 3. Custom CA (for internal CA):
curl --cacert /path/to/internal-ca.pem https://api.internal.com
```

**ss shows service not listening:**
```bash
# Application should be on port 8080 but nothing shows
ss -tlnp | grep 8080   # no output

# Check if the process is running:
pgrep -a java

# Check what port it's actually on:
ss -tlnp | grep java   # search by process name

# Check application logs for startup errors:
journalctl -u myapp -n 50

# Common causes:
# 1. Application using a different port (check config)
# 2. Application failed to start (bind error, config error)
# 3. Application is still starting (give it time)
# 4. Application bound to IPv6 (:::8080) not IPv4 (0.0.0.0:8080)
```

---

### Related Keywords

**Foundational:**
LNX-023 (Basic Networking Commands), LNX-006 (Terminal)

**Builds on this:**
LNX-045 (Network Configuration), LNX-055 (Linux Network Stack Internals)

**Related:**
NET-001 (Networking), API-001 (HTTP)

---

### Quick Reference Card

| Command | Purpose |
|---------|---------|
| `curl URL` | GET request |
| `curl -v URL` | Verbose: show all layers |
| `curl -I URL` | HEAD: headers only |
| `curl -f URL` | Fail on HTTP errors (4xx/5xx) |
| `curl -L URL` | Follow redirects |
| `curl -o file URL` | Download to file |
| `curl -X POST -H "..." -d '...'` | POST with JSON |
| `curl -w "%{http_code}" -s -o /dev/null URL` | Get HTTP code only |
| `wget URL` | Download file |
| `ss -tlnp` | TCP listening ports |
| `ss -tnp` | Established TCP connections |
| `ss -tlnp \| grep :8080` | Who's on port 8080 |

**3 things to remember:**
1. `curl -v URL` shows every layer: DNS -> TCP -> TLS -> HTTP (pinpoints failure layer)
2. `ss -tlnp` service on `127.0.0.1:port` = localhost only; `0.0.0.0:port` = all interfaces
3. curl exit code 0 != HTTP 200 - use `-f` flag to fail on HTTP errors in scripts

---

### Transferable Wisdom

`curl -v` is the manual version of what every HTTP framework does automatically.
Understanding the layers (DNS, TCP, TLS, HTTP) in curl output prepares you
for: Kubernetes service debugging (DNS resolution in-cluster vs external),
API gateway tracing (TLS termination at gateway, HTTP internally), service mesh
observability (Istio Envoy sidecar intercepts TCP connections). The mental model:
HTTP over a network is multiple protocols stacked - each can fail independently.

`ss -tlnp` verifying "is something listening on this port?" is the foundational
check for: Docker port mapping verification, Kubernetes NodePort/Service
troubleshooting, cloud security group testing. The `0.0.0.0` vs `127.0.0.1`
binding distinction is universal: database servers should bind to `0.0.0.0` only
if external access is needed (and protected by firewall), not by default.

---

### The Surprising Truth

`curl` was created in 1997 by Daniel Stenberg, who has maintained it for
over 27 years as the primary author. As of 2024, curl is installed on an
estimated 15 billion devices (embedded systems, IoT, servers, laptops,
smartphones via platform libraries). The same `curl` command you run in a
terminal is also the library (libcurl) embedded in: macOS, iOS, Android,
many game consoles, automotive systems, and spacecraft (curl was used in the
James Webb Space Telescope). Daniel Stenberg responds personally to most
bug reports. curl has had security vulnerabilities (it handles untrusted
network input), and Stenberg takes security seriously - but the breadth of
platforms means a curl CVE affects essentially everything connected to the
internet. Your `curl -v` debugging session shares its codebase with firmware
in orbiting telescopes.

---

### Mastery Checklist

- [ ] Can use curl to make GET and POST HTTP requests with headers
- [ ] Can use curl -v to diagnose HTTP/TLS issues layer by layer
- [ ] Can verify a service is listening on the correct port with ss -tlnp
- [ ] Can identify which process owns a listening port
- [ ] Can write a curl-based health check script with proper exit codes

---

### Think About This

1. `curl -v https://api.example.com` shows:
   `* Connected to api.example.com (203.0.113.50) port 443 (#0)`
   `* SSL: No error`
   `< HTTP/1.1 200 OK`
   But the application logs show no incoming request. Where might the
   request have been handled, and how would you confirm?

2. `ss -tlnp` shows `LISTEN 0 128 0.0.0.0:8080`. The `128` in the
   Recv-Q (or actually Send-Q/Backlog) column means something specific.
   What does it indicate, and what happens when this number is exceeded?

3. You're debugging an API that randomly returns 200 or 503 (two servers
   behind a load balancer, one is broken). How would you use curl to
   test EACH server directly, bypassing the load balancer's DNS
   round-robin, to identify which server is broken?

---

### Interview Deep-Dive

**Foundational:**
Q: How do you make a POST request with JSON body using curl on the command line?
A: `curl -X POST https://api.example.com/endpoint -H "Content-Type: application/json" -d '{"key":"value","other":42}'`. Breakdown: `-X POST` = use POST method (default is GET), `-H "Content-Type: application/json"` = set header telling server the body format, `-d` = data (request body). For formatted JSON: `curl ... -d '{"key":"value"}' | python3 -m json.tool`. With auth: add `-H "Authorization: Bearer TOKEN"`. To see response headers: add `-i` (include response headers in output) or use `-I` for HEAD-only. To save response to file: `-o output.json`. For debugging: add `-v` to see the full request/response cycle.

**Intermediate:**
Q: How do you use curl to measure the response time of an API endpoint?
A: Use curl's `--write-out` option to output timing information:
```bash
curl -w "
  dns_lookup:    %{time_namelookup}s
  tcp_connect:   %{time_connect}s
  tls_handshake: %{time_appconnect}s
  time_to_first_byte: %{time_starttransfer}s
  total:         %{time_total}s
  http_code:     %{http_code}
" -o /dev/null -s https://api.example.com/endpoint
```

`-o /dev/null` discards the body (we only want timing), `-s` = silent (no progress bar). Key metrics: `time_namelookup` = DNS, `time_connect` = TCP, `time_appconnect` = TLS, `time_starttransfer` = TTFB (time to first byte = server processing time), `time_total` = full response. To run multiple times for statistics: `for i in {1..10}; do curl -w "%{time_total}\n" -o /dev/null -s https://api.example.com; done | awk '{sum+=$1} END{print "avg:", sum/NR}'`.

**Expert:**
Q: You're debugging a microservice where curl from inside the pod works but curl from another pod to this service fails. How do you systematically diagnose this?
A: Systematic layer-by-layer debug inside Kubernetes: (1) DNS resolution: `kubectl exec -it debug-pod -- nslookup servicename.namespace.svc.cluster.local`. If DNS fails: check CoreDNS pods (`kubectl get pods -n kube-system -l k8s-app=kube-dns`). (2) Service exists and has endpoints: `kubectl get service servicename` + `kubectl get endpoints servicename`. If no endpoints: pod selector labels don't match service selector. (3) Direct pod IP: `kubectl exec -it debug-pod -- curl -v http://POD_IP:8080/health`. If this works but service DNS doesn't: service selector issue. (4) Service IP: `kubectl exec -it debug-pod -- curl -v http://CLUSTER_IP:PORT/health`. If this fails but direct IP works: iptables/kube-proxy issue. (5) Network policy: `kubectl get networkpolicies -n namespace`. If a NetworkPolicy exists, it might block pod-to-pod traffic. Check if the policy allows traffic from the calling namespace. (6) Sidecar: if using Istio, the Envoy sidecar intercepts all traffic. Check Envoy logs: `kubectl logs pod-name -c istio-proxy`. (7) Port: `ss -tlnp` inside the target pod (via exec) confirms the service is actually listening on the declared container port.
