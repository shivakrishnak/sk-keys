---
id: NET-032
title: "Reverse Proxy"
category: Networking
tier: tier-2-networking-security
folder: NET-networking
difficulty: ★★☆
depends_on: NET-003, NET-030
used_by: NET-046
related: NET-031, NET-046, NET-030
tags:
  - networking
  - reverse-proxy
  - nginx
  - caching
  - ssl-termination
status: complete
version: 4
layout: default
parent: "Networking"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/net/reverse-proxy/
---

**⚡ TL;DR** - A reverse proxy sits between clients and
backend servers, forwarding requests to backends on behalf
of clients. Unlike a forward proxy (which serves clients
accessing the internet), a reverse proxy serves external
clients accessing your internal services. Key capabilities:
SSL termination, caching, request routing, rate limiting,
and hiding backend topology. nginx, Caddy, HAProxy,
Cloudflare, and AWS ALB are all reverse proxies.

| #032 | Category: Networking | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Client-Server Model, HTTP and HTTPS Basics | |
| **Used by:** | Load Balancing Algorithms | |
| **Related:** | Load Balancer Basics, Load Balancing Algorithms, HTTP and HTTPS Basics | |

---

### 🔥 The Problem This Solves

A web application server (Django, Spring Boot, Node.js)
is designed to handle application logic, not to:
terminate TLS, cache static content, rate limit by IP,
serve multiple domains on one IP, or efficiently handle
slow clients while the application thread is blocked.
The reverse proxy handles all of this in front of the
application servers, letting each layer do what it's
best at.

---

### 📘 Textbook Definition

A **reverse proxy** is an intermediary server that accepts
requests from clients and forwards them to backend servers,
returning the backend's response to the client as if it
were its own. The client sees only the proxy's IP; the
backend's topology is hidden. Core functions: TLS
termination (offloads crypto from backends), load
balancing (distribute across backend pool), caching
(cache-Control response reuse), compression, rate limiting,
and request rewriting. Contrast: a **forward proxy** serves
clients accessing external services (enterprise internet
gateway), while a **reverse proxy** serves external clients
accessing internal services.

---

### ⏱️ Understand It in 30 Seconds

**Forward proxy vs Reverse proxy:**

```
Forward Proxy:
  Client → [Forward Proxy] → Internet
  Proxy knows WHO the client is (their real IP).
  Use: corporate internet gateway, Tor, caching proxy.
  Client configures proxy explicitly.

Reverse Proxy:
  Client → [Reverse Proxy] → Backend Server
  Client sees ONLY the proxy (doesn't know backends exist).
  Use: protect backends, SSL termination, load balancing.
  Client doesn't know it's talking to a proxy.

You are ALWAYS using a reverse proxy when you visit any
major website. Cloudflare, CDN, AWS ALB are all reverse
proxies.
```

---

### 🔩 First Principles Explanation

**What a reverse proxy does to a request:**

```
┌──────────────────────────────────────────────────────────┐
│  Request Transformation Through Reverse Proxy           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Client → Proxy Request:                               │
│    Client IP: 203.0.113.50                             │
│    Protocol: HTTPS (TLS encrypted)                     │
│    Destination: api.example.com:443                    │
│    HTTP: GET /api/users HTTP/2                         │
│                                                          │
│  Proxy → Backend Request (transformed):                │
│    Client IP: 10.0.1.5 (proxy internal IP)             │
│    Protocol: HTTP (TLS terminated at proxy)            │
│    Destination: backend:8080                           │
│    HTTP: GET /api/users HTTP/1.1                       │
│    Added headers:                                      │
│      X-Forwarded-For: 203.0.113.50  ← real client IP  │
│      X-Forwarded-Proto: https       ← original proto  │
│      X-Real-IP: 203.0.113.50                          │
│      X-Request-ID: abc-123-def-456  ← correlation ID  │
└──────────────────────────────────────────────────────────┘
```

**Core reverse proxy capabilities:**

```
┌──────────────────────────────────────────────────────────┐
│  Reverse Proxy Capabilities                              │
├──────────────┬───────────────────────────────────────────┤
│  SSL         │  Terminate TLS at proxy. Backends use     │
│  Termination │  plain HTTP internally. Centralize cert  │
│              │  management (Let's Encrypt automation).  │
├──────────────┼───────────────────────────────────────────┤
│  Caching     │  Cache GET responses per Cache-Control.  │
│              │  Serve cached response without hitting  │
│              │  backend. Nginx/Varnish: 100x throughput │
├──────────────┼───────────────────────────────────────────┤
│  Compression │  gzip/brotli compress responses.         │
│              │  Reduces bandwidth by 60-80% for HTML/   │
│              │  JSON/CSS. Offloads CPU from backends.   │
├──────────────┼───────────────────────────────────────────┤
│  Rate        │  Limit requests per IP per second.       │
│  Limiting    │  Block brute force. Protect backends     │
│              │  from request floods.                    │
├──────────────┼───────────────────────────────────────────┤
│  URL         │  Rewrite request paths before forwarding.│
│  Rewriting   │  /v1/users → /api/v1/users (versioning)  │
├──────────────┼───────────────────────────────────────────┤
│  Auth        │  Validate tokens before forwarding.      │
│  Sidecar     │  Reject unauthenticated requests at edge.│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**SETUP: Slow client DoS without reverse proxy**

Your Python/Java/Node app server accepts HTTP requests
directly. A client on a 56k modem connects and slowly
downloads a 100MB response over 3 hours. The app thread
(or connection) is occupied the entire time.

With only 100 worker threads, 100 such slow clients
saturate all workers. New requests queue up. Timeout.
503 for legitimate fast clients.

**With reverse proxy (nginx) in front:**
- App server generates the 100MB response immediately
  (takes 0.1 seconds)
- Proxy buffers the response and dribbles it out to
  the slow client over 3 hours
- App server connection is FREE immediately after generating
  the response
- App thread handles next request in 0.1 seconds

**THE INSIGHT:**
Application servers are optimized for fast in-memory
processing, not slow network I/O. The reverse proxy acts
as a "slow client buffer," absorbing variable network
speeds. This is why nginx (event-driven, non-blocking)
sitting in front of Python/Ruby/PHP (blocking, thread-per-
request) became standard - nginx handles 10K concurrent
slow clients; the app server sees only fast in-memory
connections to nginx.

---

### 🧠 Mental Model / Analogy

> A reverse proxy is a hotel concierge:
>
> Guests (clients) interact only with the concierge.
> They don't know which staff member or department
> handles their request.
>
> The concierge: decrypts their whispered secrets
> (TLS termination), translates their language if needed
> (protocol translation), checks their reservation (auth),
> routes to the right department (load balancing),
> and handles common requests from memory (caching).
>
> Hotel staff (backends) only deal with the concierge,
> never directly with guests - they work in an efficient,
> protected environment.

---

### ⚙️ How It Works (Mechanism)

**Production nginx reverse proxy configuration:**

```nginx
# Upstream definition (backend pool)
upstream app {
    least_conn;
    server app-1:8080;
    server app-2:8080;
    keepalive 32;  # keep 32 connections open to backends
}

server {
    listen 80;
    server_name api.example.com;
    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # TLS configuration
    ssl_certificate     /etc/letsencrypt/live/.../fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/.../privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Compression
    gzip on;
    gzip_types application/json text/html text/css;
    gzip_min_length 1024;

    # Rate limiting (requires limit_req_zone in http block)
    limit_req zone=api burst=20 nodelay;

    location /api/ {
        proxy_pass http://app;

        # Forward real client IP to backend
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;

        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer slow clients
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Cache static assets
    location /static/ {
        proxy_pass http://app;
        proxy_cache_valid 200 1d;
        add_header Cache-Control "public, max-age=86400";
    }
}
```

**Wrong vs Right - missing X-Forwarded-Proto:**

```python
# BAD: app doesn't know request was HTTPS at proxy
# Generates HTTP redirect URLs or insecure cookies
@app.route('/login', methods=['POST'])
def login():
    # ...authenticate...
    resp = redirect('/dashboard')
    # Sets cookie without Secure flag because app thinks HTTP
    resp.set_cookie('session', token,
                    secure=False)  # BAD: insecure!
    return resp

# GOOD: trust X-Forwarded-Proto from proxy
from flask import request as req

@app.route('/login', methods=['POST'])
def login():
    # ...authenticate...
    is_https = req.headers.get('X-Forwarded-Proto') == 'https'
    resp = redirect('/dashboard')
    resp.set_cookie('session', token,
                    secure=is_https,  # GOOD
                    httponly=True,
                    samesite='Strict')
    return resp

# Or use a framework that handles this automatically:
# Flask: app.config['PREFERRED_URL_SCHEME'] = 'https'
# Django: SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

### 🔄 The Complete Picture - End-to-End Flow

**How Cloudflare works as a global reverse proxy:**

```
┌──────────────────────────────────────────────────────────┐
│  Cloudflare as Reverse Proxy                             │
├──────────────────────────────────────────────────────────┤
│  1. Your DNS: api.example.com → Cloudflare IP (anycast) │
│  2. Client connects to nearest Cloudflare PoP           │
│  3. Cloudflare terminates TLS                           │
│  4. Checks: DDoS? Block. Bot? Challenge. Cached? Return.│
│  5. If not cached: forward to your origin server        │
│     - From Cloudflare's IP (your server sees CF IP)    │
│     - With CF-Connecting-IP header (real client IP)    │
│  6. Cache response per Cache-Control header             │
│  7. Return to client from nearest PoP                   │
│                                                          │
│  Benefits:                                              │
│  - DDoS protection at edge (not reaching your server)  │
│  - Global CDN (cached responses from nearest PoP)      │
│  - SSL offloaded (your server can use HTTP internally)  │
│  - Your server's IP is hidden (CF absorbs attacks)     │
└──────────────────────────────────────────────────────────┘
```

---

### ⚖️ Comparison Table

| | Reverse Proxy | Load Balancer | API Gateway |
|---|---|---|---|
| **Traffic routing** | Yes | Yes (primary) | Yes (advanced) |
| **SSL termination** | Yes | Yes (L7) | Yes |
| **Caching** | Yes (nginx, Varnish) | Rarely | Rarely |
| **Auth/AuthZ** | Basic | No | Yes (JWT, OAuth) |
| **Rate limiting** | Yes | Basic | Yes (per key) |
| **Protocol transform** | Yes | No | Yes (REST→gRPC) |
| **Examples** | nginx, Caddy, HAProxy | AWS ALB/NLB | AWS API GW, Kong |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Reverse proxy = load balancer | Load balancing is one feature of a reverse proxy. A reverse proxy can serve a single backend (for caching, SSL termination, rate limiting) with no load balancing at all. A load balancer may lack caching, compression, and content inspection. |
| Caching at proxy invalidates data | Proxy caches respect Cache-Control headers from the backend. Set `Cache-Control: no-cache` for dynamic data. Set `Cache-Control: max-age=86400` for static content. The problem is developers not setting headers, not the cache being aggressive. |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Intermediary: client connects to proxy,   │
│              │ proxy forwards to backend. Backend hidden. │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFITS │ SSL termination, slow client buffering,   │
│              │ caching, compression, rate limiting, auth │
├──────────────┼───────────────────────────────────────────┤
│ MUST DO      │ Set X-Forwarded-For, X-Forwarded-Proto    │
│              │ Backend must read these for IP and HTTPS  │
├──────────────┼───────────────────────────────────────────┤
│ CACHING      │ Respect Cache-Control from backend.       │
│              │ Dynamic APIs: Cache-Control: no-cache     │
│              │ Static assets: max-age=86400+             │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Backend trusts X-Forwarded-For without    │
│              │ validating it's from proxy (spoofable)    │
│              │ Not setting proxy_buffering (slow clients │
│              │ block backend threads)                    │
└──────────────────────────────────────────────────────────┘
```

**Interview one-liner:**
"A reverse proxy sits between external clients and backend
servers - clients see only the proxy's IP, backend topology
is hidden. Core value: SSL termination (backends use plain
HTTP), slow client buffering (backends see only fast in-
memory connections to proxy), caching (GET responses
reused per Cache-Control), compression, and rate limiting.
Critical header: X-Forwarded-For carries the real client
IP (otherwise backends see the proxy's IP). Django/Flask
need `SECURE_PROXY_SSL_HEADER` to trust X-Forwarded-Proto
so they know the original request was HTTPS, enabling
Secure cookie flags and HTTPS redirect URLs."