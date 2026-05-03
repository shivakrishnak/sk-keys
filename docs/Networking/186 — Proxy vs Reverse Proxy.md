---
layout: default
title: "Proxy vs Reverse Proxy"
parent: "Networking"
nav_order: 186
permalink: /networking/proxy-vs-reverse-proxy/
number: "0186"
category: Networking
difficulty: ★★☆
depends_on: HTTP & APIs, IP Addressing, TCP, DNS
used_by: Microservices, Load Balancer L4_L7, CDN, Networking
related: Load Balancer L4_L7, CDN, Firewall, NAT, TLS/SSL
tags:
  - networking
  - proxy
  - reverse-proxy
  - nginx
  - http
  - gateway
---

# 186 — Proxy vs Reverse Proxy

⚡ TL;DR — A **forward proxy** sits between clients and the internet (clients know about it; it hides client identity from servers). A **reverse proxy** sits in front of servers (clients don't know about it; it hides server identity from clients) — used for load balancing, TLS termination, caching, rate limiting, and request routing. Nginx, HAProxy, and Envoy are reverse proxies; Squid is a forward proxy.

---

### 🔥 The Problem This Solves

**FORWARD PROXY:**
A company wants to control and monitor employee internet access — block social media, log all requests, cache frequently-visited pages. Without a proxy, each employee's browser connects directly to the internet; the company has no visibility or control.

**REVERSE PROXY:**
A company has 5 web servers behind a single IP. When `api.example.com` receives a request, which server handles it? How does TLS terminate? How do you add rate limiting and caching without changing each server? A reverse proxy solves all of this as a single entry point in front of the servers.

---

### 📘 Textbook Definition

**Forward Proxy:** An intermediary server that clients explicitly configure their requests to pass through. The proxy fetches resources from the internet on behalf of clients, hiding client IPs from origin servers. Uses: corporate filtering, bypassing geo-restrictions (consumer VPN-like), caching.

**Reverse Proxy:** An intermediary server deployed in front of one or more backend servers. Clients send requests to the proxy, not knowing (or caring) about the backend servers. The proxy forwards requests to backends based on routing rules. Uses: load balancing, TLS termination, caching, compression, rate limiting, authentication offload, routing by URL path.

Key distinction: **Who benefits?** Forward proxy: the client (privacy, access control). Reverse proxy: the server (protection, scaling, features).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Forward proxy: you tell your browser to use it; it represents YOU to the internet. Reverse proxy: you don't know it exists; it represents the SERVER to you.

**One analogy:**

> Forward proxy: a personal assistant who goes to the store on your behalf — the store only sees the assistant, not you. Reverse proxy: the receptionist at a large company — you call the main number (the receptionist), and they route you to the right employee without you knowing which floor they're on or how many people work there.

---

### 🔩 First Principles Explanation

**FORWARD PROXY:**

```
Client → [Forward Proxy] → Internet (servers)

Client configures proxy: HTTP_PROXY=http://proxy.corp.com:3128
All HTTP requests go to proxy server first
Proxy checks policy: allow? block? log?
Proxy fetches from origin, returns to client
Origin server sees: proxy IP, not client IP

Uses:
  - Corporate web filtering (Squid, Blue Coat)
  - Anonymity / geo-bypassing (consumer VPNs use this model)
  - Caching (reduces bandwidth for repeated requests)
  - SSL inspection (proxy terminates HTTPS to inspect content)
```

**REVERSE PROXY:**

```
Internet (clients) → [Reverse Proxy] → Backend Servers

Client: GET api.example.com/users (thinks it's talking to the server)
Reverse proxy receives request
  - TLS termination (decrypt HTTPS)
  - Load balance to backend (round-robin, least-conn)
  - Cache response (if cacheable)
  - Rate limit (429 if exceeded)
  - Add headers (X-Request-ID, X-Real-IP)
  - Route by path: /api → api-servers, /static → S3
Backend server sees: reverse proxy IP (+ X-Forwarded-For header)

Uses:
  - Load balancing (Nginx, HAProxy, AWS ALB)
  - TLS termination (certificate managed at proxy, backends plain HTTP)
  - API gateway (path-based routing, auth, rate limiting)
  - Caching (Varnish, Nginx proxy_cache)
  - Web Application Firewall (Cloudflare, AWS WAF)
```

**NGINX AS REVERSE PROXY:**

```nginx
# nginx.conf — reverse proxy with load balancing
upstream api_servers {
    least_conn;  # routing algorithm
    server api-1.internal:8080;
    server api-2.internal:8080;
    server api-3.internal:8080;
    keepalive 32;  # persistent connections to backends
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    # Route /api to backend pool
    location /api/ {
        proxy_pass http://api_servers;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;

        # Caching
        proxy_cache api_cache;
        proxy_cache_valid 200 60s;
    }

    # Route /static to object storage
    location /static/ {
        proxy_pass https://my-bucket.s3.amazonaws.com/;
    }
}
```

---

### 🧪 Thought Experiment

**Why TLS should terminate at the reverse proxy:**

- Backend servers serve plain HTTP (port 80) internally
- Reverse proxy holds the TLS certificate and private key
- Backends don't need certificate management
- Internal network is trusted (or mTLS used for backend)
- Benefit: one cert renewal, not N server cert renewals
- Trade-off: traffic between proxy and backend is unencrypted
  (acceptable in private VPC; use mTLS in zero-trust environments)

---

### 🧠 Mental Model / Analogy

> Think of a city. A forward proxy is your personal travel agent — you tell them "book flights to Paris" and they book on your behalf; Air France only sees the travel agent. A reverse proxy is the city's tourism office — all tourists come to one address (the tourism office), which then routes them to specific hotels and restaurants they didn't need to know about in advance.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A forward proxy is an intermediary you use to access the internet (you configure it). A reverse proxy is an intermediary in front of a server that you don't configure — it's invisible to you as a client.

**Level 2:** Use Nginx as a reverse proxy by configuring `proxy_pass`. Set `X-Forwarded-For` headers so backends see real client IPs. Enable `proxy_cache` for caching. Configure upstream pool for load balancing.

**Level 3:** Reverse proxy concerns: connection pooling to backends (`keepalive`), health checks (remove unhealthy backends from rotation), sticky sessions (consistent hashing or cookie-based), timeouts (proxy_connect/read/send_timeout), header manipulation (strip/add headers), response buffering.

**Level 4:** Envoy proxy (used by Istio service mesh) extends the reverse proxy model with: xDS (discovery service protocol for dynamic configuration), circuit breaking, retry budgets, distributed tracing (injects trace headers), per-route outlier detection. This makes every service-to-service call pass through an Envoy sidecar — effectively turning all internal network calls into reverse-proxied connections with full observability and policy control.

---

### ⚙️ How It Works (Mechanism)

```bash
# Check if a site is behind a reverse proxy
curl -I https://api.example.com
# Server: nginx/1.24.0 ← reverse proxy
# X-Served-By: web-1.internal ← backend ID (if exposed)
# Via: 1.1 varnish ← caching reverse proxy

# View Nginx access log (reverse proxy)
tail -f /var/log/nginx/access.log
# $remote_addr = reverse proxy IP; check X-Forwarded-For for real client

# Test Nginx config
nginx -t

# Reload Nginx without dropping connections
nginx -s reload
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Forward Proxy:
  Client (10.0.0.5)
    → HTTP CONNECT proxy.corp.com:3128  (configure proxy)
    → GET https://example.com/page
  Proxy:
    → logs request, checks policy
    → fetches https://example.com/page
    → returns to client
  Server sees: proxy IP, not 10.0.0.5

Reverse Proxy:
  Client → GET api.example.com/users (HTTPS:443)
  Reverse Proxy:
    → TLS termination
    → route: /users → upstream api_servers
    → load balance: pick api-2 (least connections)
    → HTTP GET api-2.internal:8080/users
    → add X-Forwarded-For: client IP
  Backend: processes, responds
  Reverse Proxy: → adds cache headers, forwards response to client
```

---

### 💻 Code Example

```python
# Simple reverse proxy in Python (educational, not production)
import http.server
import urllib.request
import urllib.parse

BACKEND_URL = "http://localhost:8080"

class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        target = f"{BACKEND_URL}{self.path}"

        # Forward request to backend
        req = urllib.request.Request(
            target,
            headers={
                "X-Forwarded-For": self.client_address[0],
                "X-Forwarded-Proto": "http",
            }
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            self.send_response(resp.status)
            for header, value in resp.headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(resp.read())

    def log_message(self, fmt, *args):
        pass  # suppress default logging

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8000), ReverseProxyHandler)
    print("Reverse proxy on :8000 → backend :8080")
    server.serve_forever()
```

---

### ⚖️ Comparison Table

| Aspect            | Forward Proxy                 | Reverse Proxy                |
| ----------------- | ----------------------------- | ---------------------------- |
| Who configures it | Client                        | Server operator              |
| Hides identity of | Client                        | Server                       |
| Client awareness  | Explicit (configured)         | Transparent                  |
| Common tools      | Squid, Privoxy                | Nginx, HAProxy, Envoy, Caddy |
| TLS handling      | Can inspect/block TLS         | Terminates TLS               |
| Use cases         | Filtering, caching, anonymity | LB, TLS termination, routing |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| "Reverse proxy" is just load balancing  | Load balancing is one feature; reverse proxies also do TLS termination, caching, rate limiting, routing, header manipulation, WAF, compression |
| Getting the real client IP is automatic | Backend servers see the proxy IP, not the client IP. Must configure `X-Forwarded-For` / `X-Real-IP` headers and trust them only from the proxy |
| Forward proxy and VPN are the same      | A forward proxy only handles HTTP/HTTPS at Layer 7. A VPN tunnels ALL traffic at Layer 3/4 (TCP, UDP, DNS, any protocol)                       |

---

### 🚨 Failure Modes & Diagnosis

**Backend returns wrong IP — X-Forwarded-For not set**

```bash
# Check what IP the backend sees
# (backend log shows proxy IP, not real client)
grep "GET /api" /var/log/app/access.log | head -5
# 10.0.0.1 - GET /api/users  ← proxy IP, not client

# Fix: Nginx must set the header
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;

# App must read real IP from header (not socket)
# Flask: request.headers.get('X-Real-IP') or request.remote_addr
# Spring: use RemoteIpFilter or X-Forwarded headers support
```

---

### 🔗 Related Keywords

**Prerequisites:** `HTTP & APIs`, `IP Addressing`, `TCP`

**Related:** `Load Balancer L4/L7`, `CDN`, `Firewall`, `NAT`, `TLS/SSL`, `mTLS`, `API Gateway`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORWARD PROXY│ Client → Proxy → Internet; hides client   │
│ REVERSE PROXY│ Internet → Proxy → Servers; hides servers │
├──────────────┼───────────────────────────────────────────┤
│ REVERSE USE  │ Load balance, TLS term, cache, rate limit,│
│              │ routing, WAF, header manipulation         │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Nginx, HAProxy, Envoy, Caddy, Traefik     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Forward: your agent; Reverse: their      │
│              │ receptionist (you don't know it exists)"  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Envoy proxy is the foundation of Istio service mesh. Explain how deploying Envoy as a sidecar container next to every service pod creates a transparent reverse proxy for all service-to-service calls: (a) how iptables rules intercept all inbound/outbound traffic and redirect through Envoy (without app code changes), (b) what observability Envoy adds automatically (request logs, distributed traces, metrics for every call), (c) how Envoy implements circuit breaking (max connections, max pending requests, outlier detection), (d) how mTLS is enforced by the sidecar — what the cert lifecycle looks like (Istio CA issues short-lived certs, Envoy handles TLS handshake, app code sees plain HTTP), and (e) the performance overhead of the sidecar pattern (~1-5ms per hop, ~200MB memory per sidecar).
