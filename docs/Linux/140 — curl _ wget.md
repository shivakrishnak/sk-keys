---
layout: default
title: "curl / wget"
parent: "Linux"
nav_order: 140
permalink: /linux/curl-wget/
number: "0140"
category: Linux
difficulty: ★☆☆
depends_on: HTTP & APIs, Networking, Shell (bash, zsh)
used_by: CI/CD, Shell Scripting, Package Managers (apt, yum, dnf), Docker
related: SCP / rsync, SSH, HTTP & APIs
tags:
  - linux
  - networking
  - api
  - foundational
---

# 140 — curl / wget

⚡ TL;DR — `curl` transfers data to/from any URL using any protocol; `wget` downloads files recursively from the web — both are command-line HTTP workhorses for scripting and debugging.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to test a REST API from the command line, download a file to a remote server, or check if an endpoint returns the correct headers — all without a browser or GUI. Without `curl` or `wget` you would need to write a small program in Python or Java just to make an HTTP request, set headers, inspect the response, and handle authentication.

**THE BREAKING POINT:**
A CI/CD script needs to: download a binary release from GitHub, send a POST request to a webhook with build metadata, check that a health endpoint returns HTTP 200 before proceeding, and download a configuration file over HTTPS with authentication. Each of these requires a different ad-hoc script unless you have a universal HTTP tool.

**THE INVENTION MOMENT:**
This is exactly why `curl` and `wget` were created. They encapsulate the full complexity of HTTP (and dozens of other protocols) in a single command-line tool, making network operations as simple as file operations in shell scripts.

---

### 📘 Textbook Definition

`curl` (Client URL) is a command-line tool and library (`libcurl`) for transferring data with URLs. It supports HTTP, HTTPS, FTP, SFTP, SMTP, and over 25 other protocols. It provides full control over request method, headers, body, authentication, and TLS settings. `wget` is a non-interactive network downloader specialised for HTTP and FTP, with built-in support for recursive website mirroring, rate limiting, and resumable downloads. Both tools are available on virtually all Unix-like systems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`curl` makes any HTTP request from the command line; `wget` downloads files, even entire websites, recursively.

**One analogy:**

> `curl` is like a Swiss Army knife for HTTP — you can talk to any server using any verb (GET, POST, PUT, DELETE), set any header, and inspect every byte of the response. `wget` is like a download manager — point it at a URL and it fetches everything, follows redirects, and can continue an interrupted download where it left off.

**One insight:**
`curl` is the de facto standard for API debugging and scripting because it mirrors exactly what an HTTP client sends — making it the most reliable tool to verify "is this an API problem or an application problem?" independently of any application code.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. HTTP is text-based (headers + optional body) over TCP — any text-capable tool can implement it.
2. A command-line HTTP client must give full control over every request component.
3. For file download: resumability and redirect-following are non-negotiable for reliability.

**DERIVED DESIGN:**
`curl` exposes the full HTTP request model: method (`-X`), headers (`-H`), body (`-d`), authentication (`-u`), TLS settings (`--cacert`, `-k`), and cookies (`-b`/`-c`). Its output defaults to stdout, making it composable in pipes. The `libcurl` library underneath `curl` powers millions of applications (git, wget internally, PHP, Python requests).

`wget` optimises for recursive download: it parses HTML to find links, downloads them to a directory tree mirroring the remote structure, and handles rate limiting and retries automatically. Its `--continue` flag uses the HTTP `Range` header to resume interrupted downloads.

**THE TRADE-OFFS:**
**curl gain:** Protocol versatility, full request control, perfect for API work and scripting.
**curl cost:** Verbose flags for simple file downloads; no built-in recursion.
**wget gain:** Simple file download with built-in resume and recursion.
**wget cost:** Primarily HTTP/FTP only; less control over request details; not available on macOS by default.

---

### 🧪 Thought Experiment

**SETUP:**
You write a shell script that deploys a new service version. The script needs to: (1) download the release binary, (2) call a deployment API to register the new version, (3) wait for a health check endpoint to return 200.

**WHAT HAPPENS WITHOUT curl/wget:**
You write three separate Python scripts. Each requires Python to be installed, a virtual environment, the `requests` library. The script now has 30 lines of boilerplate instead of 3 lines. The script cannot be easily tested in isolation, fails if Python isn't installed in the minimal deploy environment, and takes 5 seconds to start because of Python import overhead.

**WHAT HAPPENS WITH curl/wget:**

```bash
wget -q https://releases.example.com/app-v2.tar.gz
curl -s -X POST https://api.example.com/deploy \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"version": "2.0"}'
curl -sf https://app.example.com/health
```

Three lines, no dependencies beyond curl/wget (present in every Linux environment), sub-100ms startup.

**THE INSIGHT:**
The shell + curl combination is often more reliable and portable than language-specific HTTP clients because the tools are universally available, have stable interfaces, and compose naturally with shell pipes.

---

### 🧠 Mental Model / Analogy

> `curl` is a telephone that speaks every protocol. You dial any URL (number), choose what to say (method + headers + body), and hear back exactly what the server says (raw response). Nothing is hidden — no cookies stored automatically, no redirects followed unless you ask. `wget` is a FAX machine connected to the internet — you give it an address and it fetches the document, saves it to disk, and can even call every number in the directory automatically.

- "Dialing a number" → specifying a URL
- "Choosing what to say" → setting method, headers, body
- "Hearing exactly what server says" → raw response including headers
- "FAX that fetches everything" → wget recursive download

Where this analogy breaks down: curl does follow redirects with `-L` and can store/send cookies with `-b`/`-c` — it's not always "nothing hidden", but these must be explicitly enabled.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`curl` and `wget` are commands that download files and talk to websites from the terminal. Instead of opening a browser, you type a command and get the result in your terminal or save it to a file.

**Level 2 — How to use it (junior developer):**
`curl https://api.example.com/users` makes a GET request and prints the response. `curl -X POST -H "Content-Type: application/json" -d '{"name":"Alice"}' https://api.example.com/users` sends a POST with a JSON body. `wget https://example.com/file.tar.gz` downloads a file to the current directory. `wget -c URL` resumes an interrupted download.

**Level 3 — How it works (mid-level engineer):**
curl opens a TCP connection (with TLS handshake for HTTPS), serialises the HTTP request (method + headers + body), sends it, reads the response, and outputs the body to stdout or a file. The `-v` flag shows the full request/response including TLS negotiation, useful for debugging. curl respects HTTP redirects only with `-L`. The `-w` flag formats response metadata (status code, timing) for scripting. `--connect-timeout` and `--max-time` prevent scripts from hanging indefinitely.

**Level 4 — Why it was designed this way (senior/staff):**
curl's Unix philosophy (single tool, composable with pipes, no hidden state) is why it became the universal HTTP debug tool. The decision to default to stdout rather than saving to files makes it trivially composable: `curl ... | jq .field | xargs command`. The `libcurl` C library extracts curl's functionality for embedding — today it powers git's HTTP transport, PHP's file_get_contents, and countless SDKs. wget's recursive mode predates JavaScript-heavy SPAs and works best on server-rendered HTML — modern web scraping requires headless browsers instead.

---

### ⚙️ How It Works (Mechanism)

**curl request flow:**

```
┌─────────────────────────────────────────────┐
│  curl -X POST https://api.example.com/data  │
└─────────────────────────────────────────────┘

1. DNS resolve: api.example.com → 93.184.216.34
2. TCP connect: SYN → SYN-ACK → ACK (:443)
3. TLS handshake: ClientHello → ServerHello
   → Certificate → Finished (session key)
4. HTTP/2 (or 1.1) request sent:
   POST /data HTTP/1.1
   Host: api.example.com
   Content-Type: application/json
   Authorization: Bearer TOKEN

   {"key": "value"}
5. Server responds: headers + body
6. curl outputs body to stdout (or -o file)
7. Exit code 0 = success, non-zero = error
```

**Essential curl commands:**

```bash
# Basic GET
curl https://api.example.com/users

# GET with response headers
curl -i https://api.example.com/users

# Only headers, no body
curl -I https://api.example.com/  # HEAD request

# POST with JSON body
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"username":"alice","role":"admin"}' \
  https://api.example.com/users

# POST multipart form data (file upload)
curl -X POST \
  -F "file=@/path/to/file.pdf" \
  -F "name=report" \
  https://api.example.com/upload

# Follow redirects
curl -L https://short.url/abc

# Save to file (with remote name)
curl -O https://example.com/file.tar.gz

# Save to specific file
curl -o myfile.tar.gz https://example.com/file.tar.gz

# Silent (no progress), fail on HTTP errors
curl -sf https://api.example.com/health

# Verbose debug output
curl -v https://api.example.com/health

# Check HTTP status code only
curl -o /dev/null -w "%{http_code}" \
  https://api.example.com/health

# Basic auth
curl -u username:password https://api.example.com/

# Set timeout (fail if > 10 seconds)
curl --connect-timeout 5 --max-time 10 URL
```

**Essential wget commands:**

```bash
# Download file
wget https://example.com/file.tar.gz

# Download to specific filename
wget -O myfile.tar.gz https://example.com/file.tar.gz

# Resume interrupted download
wget -c https://example.com/bigfile.tar.gz

# Download quietly (no progress bar)
wget -q https://example.com/file

# Mirror a website
wget -r -np -k https://example.com/docs/

# Download with authentication
wget --user=alice --password=secret \
  https://secure.example.com/file
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│  API HEALTH CHECK IN CI PIPELINE            │
└─────────────────────────────────────────────┘

 CI pipeline: deploy new version
       │
       ▼
 Start service
       │
       ▼
 curl -sf --retry 5 --retry-delay 2 \
      http://localhost:8080/health   ← YOU ARE HERE
       │
       ├─ HTTP 200 ──▶ proceed with tests
       │
       └─ HTTP non-200 or timeout
              │
              ▼
         curl exits non-zero
              │
              ▼
         CI step fails → pipeline aborted
```

**FAILURE PATH:**
Network unreachable or DNS failure → curl exits with non-zero code (e.g., exit code 6 for DNS failure, 28 for timeout) → shell `set -e` causes script to exit → CI pipeline reports failure.

**WHAT CHANGES AT SCALE:**
In Kubernetes readiness probes, `curl` replaces the Exec handler for HTTP endpoints. At scale, curl is used in init containers and sidecar readiness checks. For load testing, curl is replaced by `k6` or `ab` — curl is single-threaded and not designed for parallel request generation.

---

### 💻 Code Example

**Example 1 — BAD: ignoring errors, no timeout:**

```bash
# BAD — hangs forever on network failure;
#       proceeds even on HTTP 500
curl https://api.example.com/deploy \
  -d '{"version": "2.0"}'
echo "Deploy done"
```

**Example 1 — GOOD: error handling and timeout:**

```bash
# GOOD — -f fails on HTTP error; timeout set;
#         exit code checked
HTTP_STATUS=$(curl -sf \
  --connect-timeout 10 \
  --max-time 30 \
  -o /dev/null \
  -w "%{http_code}" \
  https://api.example.com/health)

if [ "$HTTP_STATUS" -ne 200 ]; then
  echo "Health check failed: HTTP $HTTP_STATUS" >&2
  exit 1
fi
echo "Service healthy"
```

**Example 2 — Polling until ready:**

```bash
#!/bin/bash
# Wait for service to become healthy (up to 60 seconds)
for i in $(seq 1 12); do
  if curl -sf \
       --connect-timeout 5 \
       http://localhost:8080/health \
       > /dev/null 2>&1; then
    echo "Service ready after ${i}x5 seconds"
    exit 0
  fi
  echo "Attempt $i/12 — waiting 5s..."
  sleep 5
done
echo "Service failed to start in 60 seconds" >&2
exit 1
```

**Example 3 — Downloading and verifying a release:**

```bash
# Download with checksum verification
VERSION="1.2.3"
BASE="https://releases.example.com"

wget -q "${BASE}/app-${VERSION}.tar.gz" \
  "${BASE}/app-${VERSION}.tar.gz.sha256"

# Verify integrity before using
sha256sum --check "app-${VERSION}.tar.gz.sha256"
echo "Checksum verified — safe to use"
```

---

### ⚖️ Comparison Table

| Tool            | Protocols              | Resumable        | Recursive | Best For                          |
| --------------- | ---------------------- | ---------------- | --------- | --------------------------------- |
| **curl**        | 25+ (HTTP, FTP, SMTP…) | Manual (-C -)    | No        | API testing, scripting, debugging |
| wget            | HTTP, HTTPS, FTP       | Yes (--continue) | Yes (-r)  | File downloads, website mirroring |
| httpie          | HTTP only              | No               | No        | Human-readable API debugging      |
| Postman         | HTTP only              | No               | No        | GUI API development and testing   |
| Python requests | HTTP only              | Manual           | No        | Application code, not shell       |

How to choose: use `curl` for scripting and API debugging (universal, full control); use `wget` for simple file downloads with resume support; use `httpie` for human-readable interactive API exploration in the terminal.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                    |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| curl follows redirects automatically         | curl does NOT follow redirects by default; use `-L` to follow them                                         |
| curl exits non-zero on HTTP error (4xx, 5xx) | curl exits 0 even on HTTP 500 unless you use the `-f` flag                                                 |
| wget and curl are interchangeable            | wget is better for file downloads with resume; curl is better for API calls and request control            |
| Adding -s silences all curl output           | -s silences progress/stats but not the response body; use `-o /dev/null` to discard the body               |
| curl -k is acceptable in production scripts  | `-k` disables TLS certificate verification, creating a security vulnerability; fix the certificate instead |

---

### 🚨 Failure Modes & Diagnosis

**Script Proceeds on HTTP Error Response**

**Symptom:**
Script reports success after a deployment even though the API returned HTTP 500. The deployment is broken but the CI pipeline shows green.

**Root Cause:**
curl exits 0 even on HTTP 4xx/5xx responses unless `-f` (fail silently) or `-F` (fail with body) is used.

**Diagnostic Command:**

```bash
# Check exit code explicitly
curl -o /dev/null -w "%{http_code}\n" https://api/endpoint
echo "Exit code: $?"
```

**Fix:**

```bash
# BAD — always exits 0
curl https://api.example.com/deploy

# GOOD — exits non-zero on HTTP error
curl -sf https://api.example.com/deploy
```

**Prevention:**
Always use `-sf` in CI scripts; capture and check the HTTP status code explicitly for diagnostic messages.

---

**Script Hangs on Network Timeout**

**Symptom:**
CI job hangs for 30+ minutes with no output when a service is down or unreachable.

**Root Cause:**
curl has no default timeout; it waits indefinitely for a connection or response.

**Diagnostic Command:**

```bash
# Test with intentional timeout
curl --connect-timeout 5 --max-time 10 \
  http://unreachable-host/
echo "Exit code: $?" # 28 = timeout
```

**Fix:**

```bash
# GOOD — always set timeouts in scripts
curl --connect-timeout 5 \
     --max-time 30 \
     -sf https://api.example.com/health
```

**Prevention:**
Establish a team standard: all curl commands in CI scripts must include `--connect-timeout` and `--max-time`.

---

**TLS Certificate Verification Failure**

**Symptom:**
`curl: (60) SSL certificate problem: certificate has expired`

**Root Cause:**
The server's TLS certificate is expired, self-signed, or the CA is not trusted.

**Diagnostic Command:**

```bash
# Show full TLS certificate details
curl -v --head https://server.example.com 2>&1 | \
  grep -A20 "Server certificate"
# Or use openssl directly
echo | openssl s_client -connect server.example.com:443 \
  2>/dev/null | openssl x509 -noout -dates
```

**Fix:**
Fix the certificate (renew or install the CA cert), not the curl flags:

```bash
# WRONG — disables all security
curl -k https://server.example.com

# RIGHT — provide the correct CA bundle
curl --cacert /path/to/ca-bundle.crt \
  https://internal-server.example.com
```

**Prevention:**
Monitor certificate expiry with alerting (30 days before expiry); never use `-k` in scripts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP & APIs` — curl operates at the HTTP protocol level; understanding HTTP methods, headers, and status codes is required
- `Networking` — DNS, TCP, TLS are the layers curl uses to establish connections
- `Shell (bash, zsh)` — curl is primarily used in shell scripts and interactive terminals

**Builds On This (learn these next):**

- `CI/CD` — curl is the standard tool for health checks, API calls, and artifact downloads in pipelines
- `Shell Scripting` — curl combined with `jq` and conditionals enables powerful API automation
- `Docker` — Dockerfiles use wget/curl to download dependencies and tools at build time

**Alternatives / Comparisons:**

- `SCP / rsync` — for host-to-host file sync over SSH, not HTTP
- `httpie` — more human-readable HTTP client for interactive use, not standard in minimal environments
- `Postman` — GUI tool for API development; not usable in shell scripts or CI

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ curl: universal URL transfer tool;        │
│              │ wget: recursive web downloader            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HTTP requests in scripts required custom  │
│ SOLVES       │ code; no universal CLI HTTP client        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ curl exits 0 even on HTTP 500 — always    │
│              │ use -f flag in scripts                    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Testing APIs, health checks in CI,        │
│              │ downloading files in shell scripts        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Load testing (use k6/ab); full website    │
│              │ scraping JS SPAs (use headless browser)   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full request control vs verbose flags for │
│              │ simple use cases                          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A Swiss Army knife for HTTP:             │
│              │  say anything to any server"              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ jq → httpie → API Gateway                │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Kubernetes liveness probe uses `curl -sf http://localhost:8080/health`. The application is healthy (returning 200) but the liveness probe keeps failing and the pod keeps restarting. What are three different root causes that could cause curl to fail even though the application is responding correctly, and how would you diagnose each?

**Q2.** You run `curl -sf https://internal-api/data | jq '.results[]' | process-each`. The `curl` command succeeds but `jq` fails because the response was actually an error JSON object `{"error": "unauthorized"}`. The shell pipeline appears to succeed (exit code 0) and silently processes invalid data. Explain why this happens and redesign the pipeline to correctly handle this failure.
