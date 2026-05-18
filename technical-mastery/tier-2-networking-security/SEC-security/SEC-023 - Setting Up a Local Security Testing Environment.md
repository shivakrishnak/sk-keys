---
id: SEC-023
title: "Setting Up a Local Security Testing Environment"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-022, SEC-024
used_by: SEC-039, SEC-077
related: SEC-001, SEC-022, SEC-024, SEC-039, SEC-073, SEC-077
tags:
  - security
  - security-testing
  - dvwa
  - webgoat
  - juice-shop
  - lab-setup
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/sec/setting-up-a-local-security-testing-environment/
---

⚡ TL;DR - Practicing web security attacks requires
deliberately vulnerable applications - not real applications
you could damage. The standard intentionally vulnerable
targets for security practice:

- **OWASP Juice Shop:** Modern Node.js SPA with 100+ challenges
  spanning OWASP Top 10. Best all-around target for web security
  learning.
- **DVWA (Damn Vulnerable Web App):** Classic PHP app, older
  but covers fundamentals (SQLi, XSS, CSRF, file inclusion).
- **WebGoat:** OWASP's Java-based lessons with guided
  explanations. Best for structured learning.

All run locally via Docker in minutes. Never practice on
real websites - it's illegal. The legal, ethical way to
develop security skills: vulnerable apps on your local
machine + platforms like HackTheBox, TryHackMe, PentesterLab.

---

| #023 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, OWASP ZAP, Burp Suite | |
| **Used by:** | Security Testing ZAP Hands-On, Security Testing in CI/CD | |
| **Related:** | OWASP ZAP, Burp Suite, Penetration Testing, Security Testing in CI/CD | |

---

### 🔥 The Problem This Solves

**THE SECURITY PRACTICE DILEMMA:**
Security skills require practice: actually exploiting SQL
injection, XSS, CSRF, path traversal in a running application.
Reading about them is insufficient. But practicing on real
websites is:
- Illegal (unauthorized computer access laws globally)
- Destructive (real data, real users affected)
- Professionally damaging (criminal charges, termination)

**THE SOLUTION:**
Intentionally vulnerable applications are real web apps,
running real technology stacks, with intentional vulnerabilities
built in. You can exploit them freely because:
- They're designed for exploitation
- They're on your local machine or a dedicated lab environment
- No real data is at risk
- No laws are violated

Learning path: run Juice Shop locally → use ZAP/Burp to find
vulnerabilities → understand why they exist → fix them in
real projects.

---

### 📘 Textbook Definition

**Security Testing Environment:** A controlled, isolated
environment where security techniques can be practiced
without risk of violating laws, damaging real systems,
or exposing real data.

**Components:**

**Intentionally Vulnerable Applications:**

**OWASP Juice Shop (recommended starting point):**
- Technology: Node.js/Angular SPA, modern stack
- Vulnerabilities: 100+ challenges across all OWASP Top 10 categories
- Features: built-in scoreboard, hint system, JWT-based auth,
  REST API, GraphQL endpoint
- Best for: learning modern web vulnerabilities in a realistic
  tech stack

**DVWA (Damn Vulnerable Web App):**
- Technology: PHP/MySQL, traditional stack
- Vulnerabilities: SQLi, XSS, CSRF, file upload, command injection,
  IDOR, SSRF, XXE (in newer versions)
- Features: adjustable difficulty (low/medium/high/impossible)
- Best for: learning fundamentals, comparing vulnerable vs secure code

**WebGoat:**
- Technology: Java Spring Boot
- Vulnerabilities: structured lessons with explanations
- Features: guided learning with hints and solutions
- Best for: structured learning with explanations, not just hacking

**Security Testing Tools (to use against vulnerable apps):**
- **OWASP ZAP:** automated DAST scanner (see SEC-022)
- **Burp Suite Community:** manual security testing proxy (see SEC-024)
- **sqlmap:** automated SQL injection testing
- **Browser DevTools:** inspect requests, modify parameters

**Online Practice Platforms (extend beyond local):**
- HackTheBox: machines + web challenges
- TryHackMe: guided rooms with walkthrough
- PentesterLab: web security specific
- PortSwigger Web Security Academy: best free web security course + labs

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Run intentionally vulnerable apps locally (Juice Shop,
DVWA, WebGoat) as safe targets to practice exploiting
real vulnerabilities. Never practice on actual websites.

**One analogy:**
> Vulnerable web apps are like combat training simulators.
> Military pilots train in flight simulators before flying
> real jets in combat. The simulator is realistic enough
> to build real skills but controlled enough that mistakes
> don't crash real planes. DVWA, Juice Shop, WebGoat are
> security simulators. The vulnerabilities are real. The
> exploitation techniques are real. The targets are designed
> to be exploited safely.

---

### 🔩 First Principles Explanation

**Why isolated environments matter:**

```
LEGAL AND ETHICAL FRAMEWORK:

The Computer Fraud and Abuse Act (US) / Computer Misuse Act (UK)
and equivalent laws globally criminalize:
  "Intentionally accessing a computer without authorization
   or exceeding authorized access."

This applies to:
  - Public websites you're not authorized to test
  - Your company's production systems (even if you work there)
  - Cloud services (your provider's ToS defines authorization)
  - Any system where you don't have explicit written authorization

SAFE TESTING CONTEXTS:
  1. Your own infrastructure (you own the server)
  2. Systems with explicit written authorization
     (bug bounty programs, pentest contracts, your staging env)
  3. Intentionally vulnerable apps (designed for exploitation,
     running locally, no real data)
  4. CTF (Capture The Flag) competitions (authorized scope)
  5. Dedicated practice platforms (HackTheBox, TryHackMe)

THE SCOPE OF "YOUR OWN LOCALHOST":
  Running DVWA on localhost:8080 on your machine:
  → Completely legal, no authorization needed
  → No real data at risk
  → Isolated from any production system
  
  Using ZAP to actively scan https://your-staging-app.example.com:
  → Legal IF you own that server or have authorization
  → Still: notify team, don't use during high traffic
  
  Running automated scanner against https://any-real-site.com:
  → Illegal (even if you "don't mean harm")
  → Even port scanning can violate computer misuse laws
```

---

### 🧪 Thought Experiment

**SCENARIO: What you can learn from Juice Shop in an afternoon**

```
SETUP: docker run -p 3000:3000 bkimminich/juice-shop
       Browser: localhost:3000

CHALLENGE 1: Find the scoreboard (hidden page)
  Method: inspect page source, look for hidden links or
    interesting URL patterns. XSS challenges might reveal paths.
  Skill developed: information gathering, source code review

CHALLENGE 2: SQL injection login bypass
  Target: login form at /#/login
  Attempt: email = "' OR '1'='1"--", password = anything
  Success: logged in as first user (usually admin)
  Skill developed: SQL injection mechanics, how parameterized
    queries prevent this

CHALLENGE 3: Access another user's basket
  URL: /api/BasketItems/1 (your basket ID)
  Try: /api/BasketItems/2, /api/BasketItems/3
  Success: seeing other users' basket data
  Skill developed: IDOR (Insecure Direct Object Reference),
    authorization vs authentication distinction

CHALLENGE 4: Reflected XSS
  Search: <iframe src="javascript:alert(`xss`)">
  If alert fires: reflected XSS found
  Skill developed: XSS mechanics, DOM execution context

WHAT THESE 4 CHALLENGES TEACH:
  - Real vulns in a modern JS framework (not "toy" examples)
  - How to use browser DevTools to inspect requests
  - How the attacker's perspective differs from the developer's
  - Muscle memory for what vulnerability patterns look like

TRANSITION TO REAL WORK:
  When you see login form in real app: remember Juice Shop lesson
  When you write API returning resource by ID: remember IDOR
  When you see {{ variable }} in template: check if encoded
  The practice in safe environment → recognition in production code
```

---

### 🧠 Mental Model / Analogy

> A local security lab is like a chemistry lab with safety
> equipment. You can work with real reagents (real vulnerability
> classes) and real reactions (actual exploitation) safely
> because: the environment is contained (localhost, isolated),
> the materials are designed for educational use (Juice Shop's
> intentional vulns), and you're working in a controlled space
> (not the open air / real internet). Without the lab: you
> either never practice (theory only, no skills) or you
> practice unsafely (real sites, legal risk). The lab enables
> safe, practical skill development.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Security labs are practice environments for learning to find
and fix security vulnerabilities safely. Instead of hacking
real websites (illegal and destructive), you use special
"broken on purpose" web apps on your own computer. These
apps are designed to be hacked - that's their purpose.

**Level 2 - How to use it (junior developer):**
Start with OWASP Juice Shop. Run with one Docker command.
Enable ZAP in proxy mode. Work through challenges starting
with 1-star (easiest). Check the scoreboard for hints.
For each vulnerability you find: understand HOW it works,
then look at how the code should have been written to prevent it.
PortSwigger Web Security Academy provides the best structured
curriculum with in-browser labs (no setup required).

**Level 3 - How it works (mid-level engineer):**
Intentionally vulnerable apps are production-quality codebases
with security controls deliberately removed or misconfigured.
Juice Shop's source code is open: you can see exactly which
vulnerability was introduced and how. This is pedagogically
valuable: compare the vulnerable code with how it should look.
Run ZAP against Juice Shop: practice interpreting ZAP alerts,
verify findings manually, understand false positives. This
builds the skill needed to use ZAP on real applications.

**Level 4 - Why it was designed this way (senior/staff):**
The challenge with security education: bridging theory to
practice requires actual exploitation experience. Course
content that teaches SQL injection without having the student
actually exploit a SQL injection doesn't build the intuition
for recognizing it in real code. Intentionally vulnerable apps
solve this by providing a legal, safe exploitation environment.
The learning model mirrors medicine: medical schools have
cadavers for surgical training before operating on living
patients. Security labs are the cadavers of cybersecurity
education. The key pedagogical design of Juice Shop: "hints
but not solutions" in the scoreboard - you work to find the
vulnerability, which builds recognition skills better than
following a tutorial.

**Level 5 - Mastery (distinguished engineer):**
Building a comprehensive security lab for team training:
Docker Compose with multiple targets (Juice Shop, WebGoat,
DVWA, a custom app with business logic vulns), ZAP configured
for each target, a vulnerability tracking spreadsheet for
exercises. Internal security training using the team's
own architecture: create a miniature version of your
production stack with deliberately introduced vulnerabilities
relevant to your specific technology choices. Teams
that have practiced on their own stack recognize their
own patterns faster. The most advanced lab work: deliberately
introduce a vulnerability in a feature branch, run through
the full SDLC to see if your security controls catch it.
Measure: which stage catches it? How long does it take?
Use this to calibrate your security control effectiveness.

---

### ⚙️ How It Works (Mechanism)

**Local lab architecture:**

```
LOCAL SECURITY TESTING ENVIRONMENT:

Docker Compose (docker-compose.yml):

  ┌─────────────────┐    ┌─────────────────┐
  │  Juice Shop     │    │  DVWA           │
  │  :3000          │    │  :8080          │
  │  Modern SPA     │    │  PHP/MySQL      │
  │  100+ challenges│    │  Classic vulns  │
  └─────────────────┘    └─────────────────┘
           ↑                      ↑
           │                      │
  ┌────────────────────────────────────────┐
  │  OWASP ZAP Proxy      │  Burp Suite   │
  │  localhost:8090       │  localhost:8080│
  │  Automated scanning   │  Manual testing│
  └────────────────────────────────────────┘
           ↑                      ↑
           │                      │
  ┌────────────────────────────────────────┐
  │              Browser                   │
  │  (proxy configured to ZAP or Burp)    │
  └────────────────────────────────────────┘

ISOLATION: All containers on a local Docker network.
  No internet access from containers.
  No exposure to the real internet.
  Browser testing is localhost only.
```

---

### 💻 Code Example

**Docker Compose setup for local security lab:**

```yaml
# docker-compose.yml - Local security lab
# Usage: docker compose up -d

version: '3'
services:
  
  # OWASP Juice Shop - Modern target (recommended start)
  juice-shop:
    image: bkimminich/juice-shop
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=unsafe  # Disables some default security headers
    restart: unless-stopped
    
  # DVWA - Classic PHP target
  dvwa:
    image: vulnerables/web-dvwa
    ports:
      - "8080:80"
    environment:
      - MYSQL_PASS=p@ssw0rd
    restart: unless-stopped
    
  # WebGoat - Java guided learning
  webgoat:
    image: webgoat/webgoat
    ports:
      - "8888:8888"  # WebGoat
      - "9090:9090"  # WebWolf (attacker server)
    restart: unless-stopped

  # ZAP as a daemon for API-based scanning
  zap:
    image: owasp/zap2docker-stable
    ports:
      - "8090:8090"
    command: >
      zap.sh -daemon -host 0.0.0.0 -port 8090
      -config api.addrs.addr.name=.*
      -config api.addrs.addr.regex=true
    restart: unless-stopped
```

```bash
# Start the lab
docker compose up -d

# Verify targets are running
curl -o /dev/null -s -w "%{http_code}" http://localhost:3000
# 200 = Juice Shop running

curl -o /dev/null -s -w "%{http_code}" http://localhost:8080
# 200 = DVWA running

# Run ZAP passive scan against Juice Shop
docker run -t owasp/zap2docker-stable \
  zap-baseline.py \
  -t http://host.docker.internal:3000 \
  -r juice-shop-scan.html

# Configure browser proxy:
# Firefox: Settings → Network → Manual proxy: localhost:8090
# Chrome: use FoxyProxy extension for easy switching

# Check DVWA - default creds: admin/password
# Set difficulty to 'Low' to start
# Navigate: http://localhost:8080/vulnerabilities/sqli/
```

---

### ⚖️ Comparison Table

| Target | Stack | Difficulty | Best For | # Vulns |
|:---|:---|:---|:---|:---|
| **Juice Shop** | Node/Angular | ★★☆ | Modern web security, comprehensive | 100+ challenges |
| **DVWA** | PHP/MySQL | ★☆☆ | Fundamentals, adjustable difficulty | ~10 categories |
| **WebGoat** | Java/Spring | ★☆☆ | Structured learning, guided | 50+ lessons |
| **PortSwigger Labs** | Browser-based | ★★★ | Specific vuln categories, professional | 200+ labs |
| **HackTheBox** | Various | ★★★ | CTF-style, full machines | 300+ machines |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Using a VPN makes it safe to scan real websites | A VPN changes your IP address but does not change the legal status of unauthorized access. Scanning a website without authorization is illegal regardless of whether your IP is visible. The crime is the unauthorized access, not being identified. VPN users have been successfully prosecuted for cybercrimes. No VPN provides legal cover for unauthorized testing. |
| Local vulnerable apps are risk-free to run | DVWA and some older vulnerable apps use weak default credentials and expose services. If run on a machine connected to a network with other users, or if the Docker container is exposed beyond localhost, the vulnerable app becomes a real risk. Always: bind to localhost only (`127.0.0.1:8080:80`), don't run on shared or production machines, use Docker's `--network host` only if you understand the exposure. |

---

### 🚨 Failure Modes & Diagnosis

**Common setup issues:**

```bash
# ISSUE: Docker ports conflict
# Error: "port is already allocated"
# Fix: change port mapping in docker-compose.yml
#      or stop conflicting service

# Find what's using port 8080:
# Windows: netstat -aon | findstr :8080
# Linux/Mac: lsof -i :8080

# ISSUE: DVWA database not initialized
# Navigate to: http://localhost:8080/setup.php
# Click "Create / Reset Database"
# Then login: admin / password

# ISSUE: Juice Shop accessible from network (security risk)
# Check: docker ps  → shows port binding
# If: 0.0.0.0:3000->3000/tcp (exposed to all interfaces)
# Fix in docker-compose.yml:
ports:
  - "127.0.0.1:3000:3000"  # Localhost only
# ↑ This binds only to localhost, not exposed to network

# ISSUE: ZAP proxy intercepting all browser traffic
# Problem: ZAP sees your real browsing (privacy issue)
# Solution: use Firefox with a proxy profile dedicated to
#           security testing, or use FoxyProxy to toggle
#           proxy on/off per site/session
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP ZAP` - tool to use against the vulnerable apps
- `Burp Suite Community Intro` - manual testing tool

**Builds on this:**
- `Security Testing ZAP Hands-On` - practical exercises
- `Penetration Testing Methodology` - professional approach
- `DAST` - how automated scanning works

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TARGETS      │ Juice Shop (modern, 100+ challenges)      │
│              │ DVWA (classic, adjustable difficulty)     │
│              │ WebGoat (guided lessons, Java)            │
├──────────────┼───────────────────────────────────────────┤
│ QUICK START  │ docker run -p 3000:3000 \                 │
│              │   bkimminich/juice-shop                   │
├──────────────┼───────────────────────────────────────────┤
│ LEGAL        │ ONLY localhost / your own infra           │
│              │ Never real sites. VPN doesn't help.       │
├──────────────┼───────────────────────────────────────────┤
│ ONLINE ALT   │ PortSwigger Web Security Academy (free)   │
│              │ HackTheBox, TryHackMe                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Practice on apps designed to be hacked.  │
│              │  Juice Shop: docker run -p 3000:3000      │
│              │  bkimminich/juice-shop. Then exploit."    │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Safe failure modes require safe practice environments."
Test-driven development requires test environments. Performance
testing requires load testing environments. Security skill
development requires security testing environments. The pattern:
any skill involving "what happens when things go wrong"
requires a controlled environment where things can go wrong
safely. A security team that has never practiced exploitation
is like a fire department that has never practiced putting
out fires. The lab is where you make mistakes cheaply,
build muscle memory, and develop the intuition that makes
you effective when it counts.

---

### 💡 The Surprising Truth

PortSwigger Web Security Academy (portswigger.net/web-security)
is arguably the best free web security course available,
and it requires no local setup. It includes: detailed written
explanations of every OWASP Top 10 vulnerability category,
in-browser labs that run vulnerable applications (no Docker
required), progressive difficulty from beginner to expert,
and guided learning with hints. The labs use actual Burp
Suite Community (free) as the testing tool. The entire
curriculum from "what is SQL injection" to "advanced
deserialization attacks" is available, free, with live
labs. Most security professionals consider it better than
many paid courses. It was built by PortSwigger (makers of
Burp Suite) as a learning resource and is maintained by
professional security researchers. If you're starting web
security: PortSwigger Web Security Academy first,
local Docker lab second.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **SPIN UP** a local vulnerable application (Juice Shop
   or DVWA) using Docker and configure your browser to
   test through ZAP or Burp Suite proxy.
2. **FIND** at least one SQL injection and one XSS
   vulnerability in a vulnerable app manually.
3. **EXPLAIN** the legal boundaries: what you can and cannot
   test, and why a VPN doesn't change legal status.
4. **COMPARE** the learning paths: local lab vs. PortSwigger
   Academy vs. HackTheBox - and when to use each.

---

### 🎯 Interview Deep-Dive

**Q: How do you practice security skills and stay current
with new vulnerabilities?**

*Why they ask:* Security skills require continuous practice.
Demonstrates commitment and practical approach.

*Strong answer includes:*
- Local vulnerable apps: Juice Shop, DVWA, WebGoat.
  Specific exercises: found 10 challenges in Juice Shop,
  practiced SQLi in DVWA at each difficulty level.
- PortSwigger Web Security Academy for structured learning
  with explanations - covered SQLi, XSS, CSRF, SSRF modules.
- Reading resources: OWASP releases, HackerOne disclosure blog,
  Google Project Zero blog, PortSwigger Research blog for
  new technique writeups.
- Applying to real work: when learning SSRF, reviewed team's
  code for URL-fetching patterns. Found one issue, fixed it.
- CTF participation if applicable.
- Key differentiator: describing specific things learned,
  not just listing resources. "I practiced SQL injection
  and specifically understood how UNION-based extraction
  works versus blind SQLi" > "I read about SQL injection."