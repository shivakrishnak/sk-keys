---
id: SEC-024
title: "Burp Suite Community - Introduction"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-001, SEC-011, SEC-012, SEC-022
used_by: SEC-039, SEC-064, SEC-075, SEC-077
related: SEC-001, SEC-011, SEC-012, SEC-022, SEC-039, SEC-064, SEC-075, SEC-077
tags:
  - security
  - burp-suite
  - penetration-testing
  - security-testing
  - dast
  - proxy
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/sec/burp-suite-community-introduction/
---

⚡ TL;DR - Burp Suite is the industry-standard tool for
manual web application security testing. Community (free)
edition is sufficient for learning and most developer
security testing. Professional edition ($449/year) adds
automation, scanning, and CI/CD integration.

Burp Suite's core: an intercepting HTTP proxy (default port
8080). Browser sends all traffic through Burp, which
displays every request and response, allowing you to: pause
and modify requests before they reach the server (intercept),
replay modified requests (Repeater), test many values
automatically (Intruder - rate-limited in Community),
search for vulnerabilities across all observed traffic (Scanner
- Pro only, but Community has passive indicators).

Learning path: PortSwigger Web Security Academy provides
guided Burp Suite tutorials free. Key skill: using Repeater
to manually test vulnerability hypotheses (if I change this
parameter, does the server return different data?).

---

| #024 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, SQL Injection, XSS, OWASP ZAP | |
| **Used by:** | Security Testing ZAP Hands-On, DAST, Advanced XSS, Pentest Methodology | |
| **Related:** | OWASP ZAP, DAST, SQL Injection, XSS, Pentest Methodology | |

---

### 🔥 The Problem This Solves

**WHAT BROWSER DEVTOOLS CAN'T DO:**
Browser DevTools shows you requests your browser makes.
You cannot easily: intercept and modify a request before
it's sent, replay a modified request, send 1000 variations
of a parameter to test for vulnerabilities, or capture
and analyze all traffic from all tabs simultaneously.

**WHAT ZAP AUTOMATES VERSUS WHAT BURP ENABLES:**
ZAP automates scanning: it sends known attack payloads
and looks for vulnerability signatures. Burp Suite (especially
via Repeater) enables manual testing: you observe a request,
form a hypothesis ("if I change user_id from 1 to 2, will
I see another user's data?"), modify the request, send it,
analyze the response, refine the hypothesis. This manual
test-and-observe loop is how most real security vulnerabilities
are found by professionals. Automated scanners miss IDOR,
broken business logic, and complex authorization failures.
Burp Suite makes manual testing efficient.

---

### 📘 Textbook Definition

**Burp Suite:** A comprehensive platform for web application
security testing. Developed by PortSwigger. Available in
Community (free) and Professional ($449/year) editions.

**Core Tools (Community Edition):**

**Proxy:** Intercepts HTTP/HTTPS traffic between browser
and server. All requests/responses are captured in the
HTTP history. Can intercept (pause) requests for manual
modification before forwarding.

**Target Site Map:** Builds a map of all discovered content
(URLs, parameters, forms) from observed traffic.

**Repeater:** Manual request testing tool. Send a saved
request to Repeater, modify any parameter, send it, compare
responses. Fastest tool for manually testing a vulnerability
hypothesis. Core manual testing workflow.

**Intruder (rate-limited in Community):** Automated parameter
fuzzing. Set a payload position (e.g., the user_id parameter),
define a payload list, send all combinations. Community
is deliberately rate-limited (1 request per 2 seconds) -
Pro is unlimited. Still useful for small lists.

**Decoder:** Encode/decode data in common formats:
URL, HTML, Base64, Hex, Gzip. Useful for analyzing
obfuscated parameters.

**Comparer:** Diff tool for HTTP responses. Compare two
responses side-by-side to identify what changed between
a successful request and a failed one.

**DOM Invader (browser extension):** Automated DOM-based XSS
and prototype pollution scanner that works inside the browser.

**Professional Edition Additions:**
- Burp Scanner: full automated vulnerability scanner
- Intruder: unlimited speed
- Collaborator: out-of-band interaction server (SSRF, blind SQLi detection)
- Audit extension API

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Burp Suite = browser traffic interceptor + manual request
editor. All HTTP/HTTPS goes through Burp. You can pause,
modify, replay any request. Repeater is the essential tool:
test security hypotheses by manually sending modified requests.

**One analogy:**
> Burp Suite is like a postal inspector's workstation for
> web traffic. All letters (HTTP requests) pass through
> the workstation. The inspector can: read every letter
> (HTTP history), open a letter before delivery and change
> the contents (intercept mode), make a perfect copy and
> send it multiple times with modifications (Repeater),
> try variations of a specific word in 1000 letters
> (Intruder). Security testing = acting as your own
> postal inspector to find what happens when unusual
> messages are sent to your application.

---

### 🔩 First Principles Explanation

**Burp Repeater - the core manual testing loop:**

```
SCENARIO: Testing for IDOR (Insecure Direct Object Reference)
  Application: /api/users/1/profile returns your own profile
  Question: does /api/users/2/profile return another user's profile?

WITHOUT BURP:
  Option 1: manually type URL in browser → works for GETs
  Option 2: can't easily modify POST body, custom headers,
    maintain session cookies across requests

WITH BURP REPEATER:
  Step 1: Browse application normally (logged in as User 1)
    Burp captures: GET /api/users/1/profile
    Cookie: session=user1_token (automatically captured)
  
  Step 2: Right-click request → "Send to Repeater"
  
  Step 3: In Repeater:
    Request shows:
      GET /api/users/1/profile HTTP/1.1
      Host: api.example.com
      Cookie: session=user1_token
    
    Modify: change 1 → 2:
      GET /api/users/2/profile HTTP/1.1
      (all other headers unchanged, including session cookie)
  
  Step 4: Send. View response.
    If 200 OK + user 2's data: IDOR confirmed.
    If 403 Forbidden: properly protected.
    If 404 Not Found: resource doesn't exist.
  
  Step 5: Hypothesis refinement
    Try: /api/users/999, /api/users/0, /api/users/-1
    Try: UUID format if numeric doesn't work
    Try: /api/admin/users/1 (elevation, not just IDOR)
  
  EFFICIENCY: Repeater + session cookie = fast iteration
    without re-logging-in, re-navigating to the endpoint
    each time. Test 20 variants in 5 minutes.

WHY THIS FINDS THINGS SCANNERS MISS:
  ZAP doesn't know that /api/users/1 is "my" resource
    and /api/users/2 is "someone else's."
  ZAP would scan both with the same auth context.
  Only a human tester knows: "1 is mine, 2 is not,
    if 2 returns data, that's a vulnerability."
  Business context drives manual testing.
  Automated scanning tests by pattern, not by business logic.
```

---

### 🧪 Thought Experiment

**SCENARIO: Finding a JWT manipulation vulnerability**

```
SCENARIO: Application uses JWTs for authentication.
  JWT payload: {"user_id": 123, "role": "user"}

STEP 1: Capture JWT from normal login
  Burp HTTP History: POST /login → response contains:
  Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJ1c2VyIn0.XXXX

STEP 2: Decode JWT in Burp Decoder
  Select base64 payload part: eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJ1c2VyIn0
  Decode as Base64: {"user_id":123,"role":"user"}
  
STEP 3: Hypothesis - can I change "role" to "admin"?
  Modify payload: {"user_id":123,"role":"admin"}
  Encode as Base64: eyJ1c2VyX2lkIjoxMjMsInJvbGUiOiJhZG1pbiJ9
  
STEP 4: Test with none algorithm (common JWT vulnerability)
  Many JWT libraries had a bug: accepting alg="none" (no signature)
  Craft: header={"alg":"none","typ":"JWT"}
          payload={"user_id":123,"role":"admin"}
          signature=(empty)
  Full token: <encoded_header>.<encoded_payload>.
  (note trailing dot with no signature)

STEP 5: Send to Repeater
  Request: GET /api/admin/dashboard
  Authorization: Bearer <manipulated_token>
  
  If 200 OK: JWT algorithm none vulnerability confirmed.
  If 401/403: proper algorithm validation (good).

STEP 6: Report finding
  Severity: CRITICAL (authentication bypass)
  Evidence: request/response screenshots from Repeater
  Proof of concept: the manipulated JWT + response
  Remediation: explicitly specify HS256 in jwt.decode()
    and reject "none" algorithm

LESSON: This specific test pattern (alg:none) is documented
  in OWASP. Without Burp Repeater: manually constructing
  and testing this token would be tedious. With Repeater:
  5-minute test.
```

---

### 🧠 Mental Model / Analogy

> Burp Suite Repeater is a scientist's hypothesis testing
> tool. A scientist forms a hypothesis ("this compound will
> react with this catalyst"), sets up the experiment (crafts
> the HTTP request), runs it (sends the request), observes
> the result (reads the response), and updates the hypothesis.
> Burp makes each iteration fast and reproducible: same
> request, different variables, systematic comparison.
> Without Burp: manual HTTP testing is like running
> chemistry experiments by hand, writing letters to the
> chemistry lab and waiting for responses. Burp is the
> lab equipment that makes the scientific method efficient.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Burp Suite lets you see and change every message your
browser sends to a website. It's like being able to open
every envelope before it's delivered and change the letter
inside. Security testers use this to send unusual messages
to websites and see if the site handles them correctly.

**Level 2 - How to use it (junior developer):**
Install Burp Community (free from portswigger.net). Set
browser to use Burp proxy (localhost:8080). Install Burp's
CA certificate in browser (for HTTPS). Browse your application
- all requests appear in HTTP history. Right-click an
interesting request → Send to Repeater → Modify and test.
PortSwigger Web Security Academy: free labs that guide you
through Burp usage for each vulnerability category.

**Level 3 - How it works (mid-level engineer):**
Burp operates as an HTTP proxy using a locally generated
certificate authority. Burp generates per-host TLS
certificates signed by the Burp CA (which you install
in the browser). This allows Burp to terminate and re-establish
TLS on both sides (MITM), giving full visibility into
HTTPS traffic. The proxy logs all traffic to its HTTP
history database. Tools like Repeater, Intruder, and
Scanner all operate on requests from this history or
manually constructed requests.

**Level 4 - Why it was designed this way (senior/staff):**
Burp's design center is "manual testing efficiency for
security researchers." This differs from ZAP, which is
"automated DAST for developers." Burp's Repeater is the
fastest single-hypothesis test tool available. Professional
pentesters use it as their primary analysis interface.
The tooling reflects the work: security researchers need
to quickly explore application behavior through many
manual hypotheses. Burp reduces friction in that loop.
The tradeoff: Burp Community lacks automation. For CI/CD:
ZAP. For manual security review: Burp. The tools are
complementary, not alternatives.

**Level 5 - Mastery (distinguished engineer):**
Burp Collaborator (Pro) is one of the most powerful features:
a server that receives out-of-band HTTP, DNS, and SMTP
interactions. When testing for SSRF: inject the Collaborator
URL into every URL parameter. If the server fetches the
URL: Collaborator receives the request, confirming SSRF
even when the application's response gives no indication
(blind SSRF). Same for blind XSS (inject Collaborator URL
as a script source in a stored location - when an admin
views it, Collaborator receives the request), blind SQLi
(DNS exfiltration). Collaborator extends Burp from "test
what you can see" to "test what the server does that you
can't see." This is critical for finding vulnerabilities
in asynchronous processing, admin interfaces, and internal
services accessed by the target.

---

### ⚙️ How It Works (Mechanism)

**Burp proxy architecture and traffic flow:**

```
BURP SUITE PROXY ARCHITECTURE:

Browser settings: HTTP Proxy = localhost:8080
                  HTTPS Proxy = localhost:8080

Browser ──HTTP request──→ Burp (localhost:8080)
           ↓
    Burp intercepts (if intercept is ON):
    Request shown in Proxy tab → you can modify
    [Forward] → sends (modified) request to server
    [Drop] → cancels request
    
    Intercept OFF (passive):
    All requests pass through automatically
    Logged to HTTP History
    Passive checks applied
           ↓
Burp (as client) ──HTTPS request──→ Target Server
  Burp terminates TLS on both sides using Burp CA cert.
  Browser trusts Burp CA (you installed it).
  Target server: regular TLS connection from Burp.
  Burp: full visibility into plaintext HTTPS traffic.

HTTP HISTORY:
  Every request/response logged.
  Searchable: find all requests to /api/
  Filter: by status code, content type, source
  
REPEATER WORKFLOW:
  Any request from History → Right-click → Send to Repeater
  Repeater: modify any part of request → Send → View response
  Multiple tabs: test same endpoint with different payloads
  History in Repeater: track what you sent/received

SCOPE DEFINITION:
  Target → Scope → Add domain
  Focuses history and scanning to in-scope targets
  Prevents accidentally testing out-of-scope domains
  (Important: stay in scope legally and professionally)
```

---

### 💻 Code Example

**Using Burp with Python requests for scripted testing:**

```python
# Use Burp as proxy for Python security testing scripts
# This sends Python requests through Burp for inspection

import requests
import urllib3

# Configure requests to use Burp proxy
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'  # HTTPS through HTTP proxy
}

# Disable SSL verification (Burp uses its own cert)
# WARNING: Only for local testing environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_idor(base_url, session_token, target_user_ids):
    """
    Test for IDOR vulnerability by accessing other users' profiles.
    This script runs through Burp proxy - all requests visible in history.
    """
    session = requests.Session()
    session.proxies = proxies
    session.verify = False  # Trust Burp's certificate
    session.headers.update({
        'Authorization': f'Bearer {session_token}'
    })
    
    findings = []
    
    # Assume we know our own user ID is 100
    my_user_id = 100
    
    for user_id in target_user_ids:
        if user_id == my_user_id:
            continue
            
        resp = session.get(f'{base_url}/api/users/{user_id}/profile')
        
        if resp.status_code == 200:
            findings.append({
                'user_id': user_id,
                'status': 'VULNERABLE: IDOR confirmed',
                'response': resp.json()
            })
        elif resp.status_code == 403:
            pass  # Expected: access denied
        elif resp.status_code == 404:
            pass  # User doesn't exist
        else:
            findings.append({
                'user_id': user_id,
                'status': f'Unexpected: {resp.status_code}'
            })
    
    return findings

# All requests visible in Burp HTTP History for manual analysis
results = test_idor(
    'https://staging.example.com',
    session_token='your-test-user-token',
    target_user_ids=range(1, 20)
)
print(results)
```

---

### ⚖️ Comparison Table

| Feature | Burp Community | Burp Professional | OWASP ZAP |
|:---|:---|:---|:---|
| **Cost** | Free | $449/year | Free |
| **Proxy/Intercept** | Yes | Yes | Yes |
| **Repeater** | Yes | Yes | Yes (Manual Request Editor) |
| **Automated Scanner** | No | Yes (full) | Yes (open source) |
| **Intruder speed** | Throttled | Unlimited | Yes (no throttle) |
| **Collaborator** | No | Yes (OOB server) | No |
| **CI/CD integration** | Poor | Good (Burp REST API) | Excellent (Docker) |
| **Best use** | Manual testing, learning | Professional pentest | Automated DAST |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Burp Community is too limited for real security work | Burp Community is what most security-conscious developers and many junior pentesters use exclusively. The Proxy, HTTP History, Repeater, Decoder, and Comparer are fully functional with no limitations. Intruder rate-limiting is annoying but workable for small-scale testing. The Scanner (automated vulnerability detection) is the main thing you miss in Community. For manual, hypothesis-driven testing: Community is excellent. |
| Burp Scanner finds all vulnerabilities | Burp Scanner (Pro) is powerful but still misses application-specific business logic issues: IDOR (requires understanding what YOU own vs. others), access control (requires understanding what different roles should see), and vulnerabilities in complex, multi-step business processes. No scanner knows your application's intended behavior. Manual testing with Repeater remains essential for access control and business logic testing. |

---

### 🚨 Failure Modes & Diagnosis

**Common Burp setup problems:**

```bash
# ISSUE: "The certificate isn't from a trusted source"
# After setting browser proxy to :8080
# CAUSE: Burp's dynamic certificate hasn't been installed
# FIX:
# 1. Browse to http://burp (while proxy is set to :8080)
#    - Shows Burp's CA certificate download
# 2. Export from Burp: Proxy → Options → Import/Export CA certificate
#    → Certificate in DER format
# 3. Install in browser:
#    Firefox: Settings → Privacy → View Certificates → Import
#    Chrome: Settings → Security → Manage certificates → Import
# After installation: HTTPS sites intercept without errors.

# ISSUE: Burp not seeing mobile app traffic
# Mobile apps use certificate pinning (won't trust Burp CA)
# Advanced: use Frida to bypass certificate pinning on Android
# Or: use an Android emulator with user CA store writeable

# ISSUE: WebSocket traffic not appearing
# Burp Community: limited WebSocket support
# Pro: full WebSocket interception + testing
# For WebSocket: use Burp Pro or browser DevTools (Network tab)

# ISSUE: Need to test behind authentication without
# manually logging in each time
# Solution: Set sticky session in Burp (macros)
# Or: set session header in Project Options → Sessions → Token handling
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `SQL Injection, XSS` - what Burp helps you test
- `OWASP ZAP` - complementary automated DAST tool

**Builds on this:**
- `Advanced XSS` - DOM Invader in Burp
- `DAST` - how DAST tools work
- `Penetration Testing Methodology` - Burp in professional pentesting
- `Security Testing in CI/CD` - ZAP preferred, Burp Pro for CI

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PROXY        │ localhost:8080, install Burp CA cert      │
│              │ All browser traffic captured in History   │
├──────────────┼───────────────────────────────────────────┤
│ REPEATER     │ Core manual testing tool                  │
│              │ Right-click → Send to Repeater            │
│              │ Modify → Send → Analyze response          │
├──────────────┼───────────────────────────────────────────┤
│ INTRUDER     │ Automated fuzzing (throttled in Community)│
│              │ Good for small payload lists              │
├──────────────┼───────────────────────────────────────────┤
│ DECODER      │ URL, Base64, HTML decode/encode           │
│              │ Useful for JWT analysis                   │
├──────────────┼───────────────────────────────────────────┤
│ VS ZAP       │ Burp: manual, hypothesis-driven           │
│              │ ZAP: automated, CI/CD, scan-based         │
│              │ Use both: ZAP in pipeline, Burp for       │
│              │ manual review                             │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"The best tool is the one that reduces friction in your
actual workflow." Burp Suite is dominant in security testing
not because it has the most features (many tools have
equivalent features) but because its workflow - intercept,
inspect, replay - matches exactly how security researchers
think about testing: "what happens if I send THIS?" The
Repeater tab is the clearest expression of this: minimum
friction between hypothesis and test result. Design tools
around the natural workflow of the task, not around exhaustive
feature lists.

---

### 💡 The Surprising Truth

The most used Burp feature by working security professionals
is not the scanner (which doesn't exist in Community) or
the fancy automated features. It's the plain HTTP History
tab and Repeater. Having all traffic in one place (HTTP
History) means you can scroll back 20 requests, find
the interesting one, and test variations in Repeater.
The "active testing" in professional pentests is almost
entirely this loop: "I saw something interesting in the
traffic, let me test it in Repeater." The sophistication
is not in the tooling - it's in knowing WHAT to test
(which comes from security knowledge) and having Repeater
reduce the friction of TESTING IT. The lesson: complex
tooling built on a simple, efficient core workflow > complex
tooling with complex workflow.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** Burp as a browser proxy, install the CA
   certificate, and confirm HTTPS traffic appears in History.
2. **USE** Repeater to test a specific hypothesis: capture
   a request, modify a parameter, send, interpret the response.
3. **TEST** for IDOR manually using Repeater: change a
   resource ID and determine if the server returns unauthorized data.
4. **EXPLAIN** when to use Burp vs ZAP: manual hypothesis
   testing vs automated DAST scanning.

---

### 🎯 Interview Deep-Dive

**Q: Walk me through how you would manually test for
authorization vulnerabilities in a web API.**

*Why they ask:* Tests practical security testing skill.
Can the candidate actually DO security testing, not just
describe it?

*Strong answer includes:*
- Set up Burp Suite as proxy for browser/test client.
- Log in as multiple test users with different roles (user A,
  user B, admin). Capture API traffic.
- Identify resource endpoints: /api/users/{id}, /api/orders/{id},
  /api/admin/... 
- Test IDOR: as user A, access resources belonging to user B.
  Use Repeater: change the ID, observe response.
  200 with data = IDOR. 403 = properly protected.
- Test privilege escalation: as regular user, send requests
  to admin endpoints. Expect 403. If 200: access control failure.
- Test horizontal escalation: user can modify account settings.
  Can they modify OTHER users' settings?
- Test missing auth: remove Authorization header.
  Expect 401. If 200: endpoint doesn't require authentication.
- Document everything: request/response screenshots from Repeater.
  Severity based on data exposed, actions possible.
- Systematic coverage: work through entire API surface, not just
  obvious endpoints. Include pagination parameters, search parameters,
  filter parameters - all are potential injection/IDOR vectors.