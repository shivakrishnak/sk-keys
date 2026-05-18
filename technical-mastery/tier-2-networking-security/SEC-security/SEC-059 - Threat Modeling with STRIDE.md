---
id: SEC-059
title: "STRIDE Threat Modeling"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★★
depends_on: SEC-001, SEC-003, SEC-010, SEC-013, SEC-016, SEC-041, SEC-055
used_by: SEC-099, SEC-109, SEC-114, SEC-116, SEC-126
related: SEC-001, SEC-010, SEC-013, SEC-016, SEC-041, SEC-055, SEC-114
tags:
  - security
  - threat-modeling
  - stride
  - design-security
  - risk-assessment
  - secure-design
  - owasp-a04
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/sec/stride-threat-modeling/
---

⚡ TL;DR - STRIDE is a threat modeling framework for systematically
enumerating threats during the design phase. Each letter is a threat
category: Spoofing, Tampering, Repudiation, Information Disclosure,
Denial of Service, Elevation of Privilege. For each data flow in a
system diagram, ask: can an attacker do each of the six things?

**STRIDE quick reference:**

| Threat | Question | Mitigation |
|--------|----------|------------|
| **S**poofing | Can an attacker pretend to be someone/something else? | Authentication |
| **T**ampering | Can an attacker modify data in transit or at rest? | Integrity / HMAC / Signing |
| **R**epudiation | Can a user deny performing an action? | Audit logs / Non-repudiation |
| **I**nformation Disclosure | Can an attacker read data they shouldn't? | Encryption / ACLs |
| **D**enial of Service | Can an attacker make the system unavailable? | Rate limiting / Redundancy |
| **E**levation of Privilege | Can an attacker do more than they're allowed? | Authorization / Least privilege |

---

| #059 | Category: Security | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | OWASP Top 10, Security Fundamentals, Input Validation, Security Headers, Authentication, Security Code Review, OWASP Workshop | |
| **Used by:** | Threat Modeling Workshop, Platform Security Engineering, Zero Trust Introduction, Security Champions Program, SSDLC | |
| **Related:** | OWASP A04 Insecure Design, PASTA, DREAD, Security Architecture | |

---

### 🔥 The Problem This Solves

**WHY THREAT MODELING EXISTS:**

```
THE COST CURVE OF FIXING SECURITY PROBLEMS:

  DESIGN PHASE:
    Finding threat: 1 hour (whiteboard session)
    Fixing threat: 1 day (change the design before a line is written)
    Cost: LOW
  
  IMPLEMENTATION PHASE:
    Finding threat: code review or SAST scan
    Fixing threat: refactor code, write tests, re-review
    Cost: MEDIUM (5-10x design phase)
  
  PRODUCTION:
    Finding threat: security audit, pentest, or breach
    Fixing threat: emergency patch, deployment, incident response,
                   possible breach notification, regulatory fines
    Cost: 100x design phase
  
  Source: NIST SP 800-64 "Security Considerations in System Development"
  Empirical cost data from Microsoft SDL research (2004-2010)

THE PROBLEM WITH REACTIVE SECURITY:
  Team ships feature. After launch, security auditor finds:
    "The comment API doesn't check ownership - any user can edit
    anyone's comment." (A01 - Broken Access Control)
  
  Fix requires:
    - Code change (add ownership check)
    - Database query change (join with owner table)
    - New test cases
    - Re-deployment
    - Possible data migration (who owns existing comments without owner field?)
    - API version bump or backward compatibility handling
  
  If caught during design:
    "Our comment service needs to store comment.user_id and verify
    the requestor's user_id matches before allowing edit/delete."
    One line added to the design diagram. Zero code changed.
    Cost: 15 minutes in a whiteboard session.

WHAT THREAT MODELING PROVIDES:
  1. Systematic enumeration of what can go wrong (vs. ad-hoc intuition)
  2. Design-time discovery (before code is written)
  3. Shared vocabulary (STRIDE terms understood by engineers and security)
  4. Documentation of threat decisions (accepted, mitigated, transferred)
  5. Basis for security test cases (threat → test case is direct)
```

---

### 📘 Textbook Definition

**Threat Modeling:** A structured approach to identifying,
evaluating, and addressing security threats during the design
phase of a system. Output: a list of threats with corresponding
mitigations, and decisions about accepted vs. mitigated risks.

**STRIDE:** A threat categorization framework from Microsoft
(introduced in the book "Writing Secure Code", 2002). Each
letter identifies a threat category and the security property
it violates:

| STRIDE | Violates |
|--------|----------|
| Spoofing | Authentication |
| Tampering | Integrity |
| Repudiation | Non-repudiation |
| Information Disclosure | Confidentiality |
| Denial of Service | Availability |
| Elevation of Privilege | Authorization |

**STRIDE maps directly to CIA+AAA:**
- Confidentiality (Information Disclosure)
- Integrity (Tampering)
- Availability (Denial of Service)
- Authentication (Spoofing)
- Authorization (Elevation of Privilege)
- Auditing/Non-repudiation (Repudiation)

**Other threat modeling methodologies:**
- PASTA (Process for Attack Simulation and Threat Analysis): business-risk focused
- DREAD: scoring model (Damage, Reproducibility, Exploitability, Affected users, Discoverability) - used for risk prioritization after STRIDE enumeration
- LINDDUN: privacy-focused threat modeling
- MITRE ATT&CK: attacker tactic-based (more appropriate for detection engineering than design)
- OWASP Threat Dragon: free tool for diagram-based threat modeling

---

### ⏱️ Understand It in 30 Seconds

**One line:**
STRIDE = a 6-category checklist for threats at each component
and data flow in a system diagram. For every arrow (data flow)
and box (component), ask: can someone spoof, tamper, repudiate,
disclose, deny, or escalate? If yes: decide how to mitigate.

**One analogy:**
> STRIDE is like a home security checklist.
>
> S - Spoofing: Can someone pretend to be you? (Identity theft, key copying)
> T - Tampering: Can someone modify your belongings? (Breaking in, changing locks)
> R - Repudiation: Can someone deny they were here? (No cameras, no logs)
> I - Info Disclosure: Can someone read your private documents? (Windows, mail slot)
> D - Denial of Service: Can someone prevent you accessing your home? (Changed locks, blocked driveway)
> E - Elevation of Privilege: Can a guest access rooms they shouldn't? (Master key duplication)
>
> STRIDE: a systematic checklist to think about every type of
> threat, not just the obvious ones. The checklist ensures you
> don't forget Repudiation (audit logs) or Information Disclosure
> (TLS, encryption) while focused on preventing break-ins.

---

### 🔩 First Principles Explanation

**STRIDE applied per element type:**

```
DFD (DATA FLOW DIAGRAM) ELEMENTS AND THREATS:

  Elements in a DFD:
    External Entity (actor): user, external service
    Process: application logic (web server, microservice, function)
    Data Store: database, cache, file system, S3
    Data Flow: network call, API request, message queue message, file read/write
    Trust Boundary: dotted line separating trust zones (internet/DMZ, DMZ/internal)

THREATS BY ELEMENT TYPE:

External Entity (e.g., user, mobile app, third-party API):
  S - Spoofing: Is the entity who they claim to be?
    Threat: Attacker impersonates a legitimate user.
    Mitigation: Authentication (OAuth, OIDC, mTLS, API keys)
  R - Repudiation: Can the entity deny their actions?
    Threat: User denies making a fraudulent transaction.
    Mitigation: Audit logs with signed entries; digital signatures

Process (e.g., web server, API service):
  S - Can a process be impersonated? (e.g., DNS hijacking → fake server)
    Mitigation: HTTPS + cert validation; mutual TLS
  T - Can the process be manipulated to produce wrong output?
    Mitigation: Input validation; parameterized queries; least privilege
  E - Can the process run with escalated privileges?
    Threat: RCE vulnerability → process runs as root.
    Mitigation: Minimal container capabilities; non-root user; seccomp

Data Store (e.g., PostgreSQL, S3, Redis):
  I - Information Disclosure: Can unauthorized parties read the data?
    Threat: Database exposed to internet; SQL injection
    Mitigation: ACLs; encryption at rest; parameterized queries
  T - Tampering: Can data be modified without authorization?
    Threat: SQL injection INSERT/UPDATE/DELETE
    Mitigation: Parameterized queries; application-level write authorization
  D - Denial of Service: Can the store be made unavailable?
    Threat: Volume attack fills disk; lock contention; OOM
    Mitigation: Rate limiting; disk quotas; query timeouts; replicas

Data Flow (e.g., HTTP call, message queue message):
  T - Tampering: Can data be modified in transit?
    Threat: Man-in-the-middle modifies the request body.
    Mitigation: TLS (transport-level integrity); request signing (HMAC)
  I - Information Disclosure: Can the data be read by a third party?
    Threat: HTTP (not HTTPS) → eavesdropping.
    Mitigation: TLS; end-to-end encryption
  D - Denial of Service: Can the flow be interrupted?
    Threat: Network partition; DDoS on endpoint.
    Mitigation: Timeouts; circuit breakers; retry with backoff

Trust Boundary crossing (highest risk area):
  Every data flow crossing a trust boundary needs authentication + integrity.
  Trust boundaries: public internet → DMZ, DMZ → internal, user → service,
                    service A → service B (microservices), browser → server.
```

---

### 🧪 Thought Experiment

**STRIDE WORKSHOP: Apply to a login system**

```
SYSTEM: Username/password login API

COMPONENTS:
  Browser (External Entity) → POST /login → Auth API (Process) → Users DB (Data Store)
  Auth API → POST /session → Redis Cache (Data Store)
  Auth API → Email API (External Service) - sends password reset emails

DATA FLOWS AND THREATS:

FLOW 1: Browser → Auth API (POST /login)
  S: Is the browser who they claim? Attacker spoofs user_id in request.
     Mitigation: Auth based on credentials (password), not on self-asserted user_id.
  T: Can the login request be modified in transit?
     Mitigation: HTTPS (TLS). Without TLS: MITM can change password in transit.
  I: Can credentials be read in transit?
     Mitigation: HTTPS. Without TLS: password visible in cleartext on network.
  D: Can the Auth API be flooded? (DDoS, brute force)
     Mitigation: Rate limiting per IP + per account; CAPTCHA after threshold.

FLOW 2: Auth API → Users DB (SQL query)
  T: Can the SQL query be tampered by injection?
     Mitigation: Parameterized queries.
  I: Can the database expose data beyond intended (SQL injection read)?
     Mitigation: Parameterized queries; ORM; min privilege for DB user.
  D: Can DB become unavailable? (connection pool exhaustion)
     Mitigation: Connection pooling; query timeouts; circuit breaker.

DATA STORE: Users DB (passwords)
  I: Can password hashes be read (SQL injection or DB breach)?
     Mitigation: bcrypt (strong hash, work factor). Even if read: not crackable.
  T: Can an attacker set is_admin=true via SQL injection?
     Mitigation: Parameterized queries; input validation; DB user with min privilege.

PROCESS: Auth API
  E: Can a regular user perform admin actions?
     Mitigation: Role-based access control; check role before admin actions.
  R: Can users deny making authentication attempts? (brute force, fraud)
     Mitigation: Audit log every auth attempt: user_id, timestamp, IP, success/failure.

FLOW 3: Auth API → Email API (password reset emails)
  S: Can an attacker send password reset emails for arbitrary users?
     Mitigation: Rate limit password reset requests; log all reset requests.
  T: Can the email content be modified?
     Mitigation: Email API internal only (not exposed to internet).

RISK PRIORITIZATION (DREAD):
  Threat: SQL injection in login query
    Damage: 10 (all user data exposed)
    Reproducibility: 10 (deterministic)
    Exploitability: 7 (requires SQL injection skill)
    Affected users: 10 (all users)
    Discoverability: 8 (common vulnerability, scannable)
    DREAD score: 9/10 → CRITICAL PRIORITY

  Threat: Email API spoofing (attacker sends reset emails)
    Damage: 6 (account takeover for target user)
    Reproducibility: 8
    Exploitability: 4 (Email API on internal network)
    Affected users: 3 (targeted attack)
    Discoverability: 5
    DREAD score: 5.2/10 → MEDIUM

MITIGATIONS TABLE OUTPUT (document this):
  Threat ID | Element | STRIDE | Threat | Mitigation | Status
  T-001 | Browser→API | T,I | No TLS | Enforce HTTPS | Done
  T-002 | API→DB | T,I | SQL injection | Parameterized queries | Done
  T-003 | Users DB | I | Password hash exposure | bcrypt w/factor=12 | Done
  T-004 | Auth API | D | Brute force | Rate limit per account | TODO
  T-005 | Auth API | E | Admin escalation | RBAC check | Done
  T-006 | Auth API | R | No audit trail | Log all auth events | TODO
```

---

### 🧠 Mental Model / Analogy

> STRIDE is like a code reviewer who asks the same six questions
> about every function:
>
> S - Who calls this function? Can anyone pretend to be an authorized caller?
> T - Can the inputs be manipulated to change the function's behavior?
> R - If this function does something bad, can we prove it happened?
> I - Does this function expose data to callers who shouldn't see it?
> D - Can this function be called so many times it makes the system unavailable?
> E - Can calling this function with certain inputs give more access than intended?
>
> STRIDE is a checklist that forces you to think about each security
> dimension systematically. Without it, engineers naturally focus on
> the "obvious" threats (injection, authentication) and miss the
> less intuitive ones (Repudiation = audit logging, Denial of Service
> at the design level).
>
> The value is not that STRIDE finds all threats - it's that it
> structures your thinking to systematically cover all threat categories
> rather than relying on intuition that has known blind spots.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
STRIDE is a checklist of 6 types of security problems (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege). When designing a new system, you draw a diagram of the system and check each component and connection against each of the 6 categories. This finds security problems before any code is written.

**Level 2 - How to use it (junior developer):**
Draw a simple data flow diagram (boxes and arrows) for the feature you're building. For each arrow (data flow) and box (component), go through STRIDE: (S) how do we know who we're talking to? (T) is the data protected in transit and at rest? (R) do we log what happens? (I) can unauthorized parties read this data? (D) can this be made unavailable by flooding? (E) can users get more access than they should? If yes to any: add it to the threat list. Use OWASP Threat Dragon (free tool) to draw diagrams and track threats.

**Level 3 - How it works (mid-level engineer):**
STRIDE is most powerful when applied per element type (external entity, process, data store, data flow) because each element type has a characteristic threat profile. External entities: focus on Spoofing (authentication) and Repudiation (audit logging). Data flows: focus on Tampering and Information Disclosure (TLS, signing). Data stores: focus on Information Disclosure (encryption, ACLs) and Tampering (SQL injection, write access controls). Processes: focus on Elevation of Privilege (least privilege, input validation). Trust boundaries crossing is the highest-value focus area in a DFD.

**Level 4 - Why it was designed this way (senior/staff):**
STRIDE was formalized by Loren Kohnfelder and Praerit Garg at Microsoft in 1999, published in "The Threats to Our Products." Microsoft made STRIDE the foundation of its Security Development Lifecycle (SDL) after the Trustworthy Computing initiative (2002, post-Code Red and Nimda worms). SDL reduced Microsoft product vulnerabilities significantly (later quantified in reports). STRIDE is deliberately simple (6 categories, easy to remember) to enable engineers without deep security expertise to participate in threat modeling. More comprehensive models exist (PASTA, LINDDUN) but require more expertise and take more time. STRIDE's simplicity is its feature: it enables team-wide participation.

**Level 5 - Mastery (distinguished engineer):**
Advanced threat modeling: STRIDE-per-interaction (SPI) applies all 6 STRIDE categories to every element interaction, not just per-element. This catches inter-service threats that per-element analysis misses. The output feeds directly into: (a) security requirements (T-001 → "all API communications must use TLS"), (b) security test cases (T-004 → "rate limiting test: 10 requests in 1 minute must return 429"), (c) security controls in architecture documentation (architecture decision records with security rationale). At enterprise scale: threat models are maintained alongside system documentation and updated when the architecture changes. Automation: tools like pytm (Python Threat Modeling) allow threat model as code - the DFD is defined in Python, STRIDE analysis is automated, findings are output in structured format for integration with issue trackers. Microsoft Threat Modeling Tool is the free GUI-based option.

---

### ⚙️ How It Works (Mechanism)

**STRIDE threat modeling workshop process:**

```
THREAT MODELING WORKSHOP (2-hour session):

PARTICIPANTS:
  Developer (2-3 who know the system)
  Security champion or security engineer (1)
  Product/architect (optional, for context)

PHASE 1: Scope (15 min)
  What are we modeling?
    - The new feature / system component
    - The specific sprint's changes
    - A specific high-risk area identified in design review
  
  Define the scope clearly. Too broad = analysis paralysis.
  Good scope: "the user authentication service"
  Bad scope: "the entire application"

PHASE 2: Draw DFD (20 min)
  Draw on whiteboard or tool (Threat Dragon, draw.io, Miro)
  
  Elements to include:
    External entities (actors): web browser, mobile app, third-party APIs
    Processes: auth service, payment service, API gateway
    Data stores: PostgreSQL, Redis, S3, RabbitMQ
    Data flows: labeled arrows (what data, what protocol)
    Trust boundaries: dotted lines (internet/DMZ/internal)
  
  Keep it simple. 5-10 elements max per diagram.
  Can be decomposed into multiple diagrams (level 1, level 2).

PHASE 3: STRIDE per element (60 min)
  Go through each element and data flow.
  For each: ask STRIDE questions (use the table).
  Record threats: threat ID, element, category, description.
  
  DON'T SOLVE DURING THIS PHASE.
  Just enumerate threats without debate. 
  "Is this a threat? Yes → write it down. Move on."
  Debate slows enumeration. Solve in phase 4.

PHASE 4: Risk rating and mitigations (20 min)
  For each threat:
    Rate severity: Critical / High / Medium / Low
    (Use DREAD, CVSS, or intuition)
    Assign mitigation:
      Mitigate: add a security control
      Accept: risk is low enough to accept
      Transfer: use a third-party service to handle it
      Avoid: change the design to eliminate the risk
  
  Assign owners and deadlines for mitigated threats.

PHASE 5: Document (5 min)
  Export to: threat register (spreadsheet or issue tracker)
  Link threat model to: design doc, ADR, architecture diagram
  Update when: significant design changes
```

---

### 💻 Code Example

**pytm: Threat model as code (Python):**

```python
# pip install pytm
# Threat model for a simple login API - generates DFD + STRIDE analysis

from pytm import TM, Actor, Dataflow, Datastore, Process, Boundary

tm = TM("Login API Threat Model")
tm.description = "Auth service threat model for sprint 4"

# Trust boundaries
internet = Boundary("Internet")
app_zone = Boundary("Application Zone")
data_zone = Boundary("Data Zone")

# Elements
browser = Actor("Web Browser")
browser.inBoundary = internet

auth_api = Process("Auth API")
auth_api.inBoundary = app_zone
auth_api.codeType = "Python"

users_db = Datastore("Users PostgreSQL")
users_db.inBoundary = data_zone
users_db.isEncryptedAtRest = True  # Marks threat as mitigated

session_cache = Datastore("Redis Session Cache")
session_cache.inBoundary = app_zone

# Data flows
login_request = Dataflow(browser, auth_api, "Login Request")
login_request.protocol = "HTTPS"     # TLS mitigates Tampering/Info Disclosure
login_request.isEncrypted = True

db_query = Dataflow(auth_api, users_db, "User Lookup")
db_query.protocol = "PostgreSQL/TLS"
db_query.isEncrypted = True

session_write = Dataflow(auth_api, session_cache, "Session Store")
session_write.protocol = "Redis/TLS"

# Generate report and DFD:
# python3 threat_model.py --report report.html --dfd dfd.png
# Output: list of threats per STRIDE category with severity ratings
tm.process()
```

---

### ⚖️ Comparison Table

| Methodology | Focus | Effort | Best For |
|:---|:---|:---|:---|
| **STRIDE** | Threat category per element | Low-Medium | Design reviews, any team |
| **PASTA** | Business risk + attack simulation | High | Risk-aligned security programs |
| **LINDDUN** | Privacy threats | Medium | GDPR compliance, privacy-by-design |
| **DREAD** | Threat scoring/prioritization | Low | Ranking STRIDE-found threats |
| **MITRE ATT&CK** | Attacker tactics | High | Detection engineering, red team |
| **OWASP Threat Dragon** | STRIDE tool with GUI | Low | Teams new to threat modeling |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Threat modeling is a security team activity, not a developer activity. | The most effective threat modeling involves developers who understand the system's implementation details. Security teams provide the framework (STRIDE) and facilitation, but developers identify the trust boundaries, data flows, and system-specific threats. A threat model done only by the security team without developer input misses implementation-specific threats. The goal is to enable the entire engineering team to think about security during design - not to create a separate security review gate. OWASP A04 (Insecure Design) explicitly calls out the need for threat modeling as a development practice. |
| Threat modeling needs to be exhaustive to be valuable. | A 2-hour STRIDE workshop that finds 5 critical threats and results in 5 specific mitigations is vastly more valuable than a 2-week exhaustive analysis that results in a 50-page document that nobody reads. Threat modeling should be proportionate to the risk of the feature being designed. A new payment flow warrants a thorough threat model. A new display preference setting does not. The goal is actionable security improvements at design time, not completeness for its own sake. Start with high-risk features (auth, payment, data export) and iterate. |

---

### 🚨 Failure Modes & Diagnosis

**Signs your threat modeling isn't working:**

```
ANTI-PATTERNS IN THREAT MODELING:

Anti-pattern 1: Checkbox compliance (not security improvement)
  Team runs threat model to satisfy a compliance requirement.
  The output lists threats but no one acts on them.
  No mitigations are implemented.
  
  Fix: Each threat must have an owner, a mitigation, and a deadline.
  Track mitigations as regular engineering tasks.
  Block release on CRITICAL and HIGH threats without accepted risk decision.

Anti-pattern 2: Too detailed too early
  Team tries to enumerate every possible attack scenario.
  3-day workshop produces 200 threats.
  Nobody can prioritize. Nothing gets done.
  
  Fix: Focus on trust boundaries and high-value data flows.
  Use DREAD scoring to prioritize top 10 threats.
  Aim for actionable output, not exhaustive analysis.

Anti-pattern 3: Only the security team participates
  Security team produces threat model without developers.
  Developers don't know about it. Don't implement mitigations.
  
  Fix: Developers must participate. Security champions in each team.
  Threat model is owned by the engineering team, reviewed by security.

Anti-pattern 4: Threat model done once, never updated
  System evolves: new features, new integrations, new data flows.
  The threat model becomes stale. New threats are never enumerated.
  
  Fix: Update threat model when: significant architecture changes,
  new external integrations added, new sensitive data types handled,
  before major feature launches.

HOW TO DIAGNOSE GOOD THREAT MODELING:
  - Can developers name the top 3 threats to their component?
  - Are there open tickets for threat mitigations in the sprint?
  - Is the threat model linked from the architecture doc?
  - When was it last updated? (>6 months = stale for active products)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `OWASP Top 10` - threat categories context
- `Security Fundamentals` - CIA triad, threat landscape
- `Security Code Review Checklist` - code-level threats
- `OWASP Top 10 Workshop` - connect threats to OWASP

**Builds on this:**
- `Threat Modeling Workshop` - facilitation for teams
- `Platform Security Engineering` - threat modeling at org scale
- `Zero Trust Introduction` - trust boundary design
- `SSDLC` - threat modeling in the development lifecycle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ S - Spoofing        → Authentication                     │
│ T - Tampering       → TLS, HMAC, Input Validation        │
│ R - Repudiation     → Audit Logs, Non-repudiation        │
│ I - Info Disclosure → Encryption, ACLs                   │
│ D - Denial of Svc   → Rate limiting, Redundancy          │
│ E - Elevation       → Authorization, Least Privilege     │
├──────────────────────────────────────────────────────────┤
│ PROCESS: Scope → DFD → STRIDE per element → Risk rate    │
│          → Mitigate → Document → Track                   │
├──────────────────────────────────────────────────────────┤
│ HIGH FOCUS │ Trust boundaries: internet/DMZ/internal      │
│ AREA       │ External entity → process data flows        │
├──────────────────────────────────────────────────────────┤
│ OUTPUT     │ Threat register + linked mitigation tickets  │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Explicit threat enumeration is better than assumed security."
STRIDE forces you to name specific threats rather than assuming
"the auth will handle it" or "we use HTTPS so it's secure."
Named threats can be mitigated, tested, and tracked.
Unnamed threats cannot.
This principle applies beyond security:
- Failure mode analysis in distributed systems (what are the
  specific ways this can fail? → not "it's reliable")
- Error budget in SRE (what are the specific reliability risks?
  → not "we care about reliability")
- Dependency risk analysis (what specific dependencies can fail?
  → not "we have good dependencies")
In each case: enumeration converts vague concerns into
specific, actionable items that engineers can address.
Vague: "security is important."
Specific: "T-004: the login endpoint can be brute-forced.
Mitigation: rate limit to 5 attempts/account/minute by sprint end."
The second is actionable. The first is not.

---

### 💡 The Surprising Truth

The Capital One 2019 breach (100 million customer records,
$80 million fine) was primarily an SSRF vulnerability followed
by AWS IAM privilege escalation. A STRIDE threat model of the
WAF-to-EC2 data flow would have identified:
- S: Can the WAF be spoofed to think a malicious request is legitimate?
  (Web shell bypass)
- E: If the EC2 running the WAF is compromised, can it access
  other AWS resources? (No IAM role least-privilege constraint)
The "E" threat (Elevation of Privilege via IAM) was the amplifier:
the initial SSRF gave RCE on the EC2 instance, but the EC2's
IAM role had S3:ListBuckets and S3:GetObject on all S3 buckets
(not least-privilege). The attacker used the overly-broad IAM
role to read 30 terabytes of customer data from S3.
A 15-minute STRIDE analysis of the IAM trust boundary would have
flagged: "Can the WAF EC2, if compromised, access S3?"
Answer: "Yes, currently - needs least-privilege IAM policy."
Cost to fix during design: 1 day.
Cost after breach: $80 million fine + $190 million settlement
+ reputational damage + CIO resignation.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **RECITE** STRIDE from memory with the security property each category violates.
2. **FACILITATE** a 1-hour STRIDE workshop for a feature you're building: draw DFD,
   enumerate threats per element, produce a threat register.
3. **CONNECT** each STRIDE threat to its corresponding OWASP Top 10 category.
4. **PRIORITIZE** a threat list using DREAD scores and differentiate between
   threats to mitigate vs. accept.

---

### 🎯 Interview Deep-Dive

**Q: What is STRIDE? Walk me through applying it to a login API.**

*Why they ask:* Tests whether candidate understands security design,
not just security implementation. Senior roles require design-level thinking.

*Strong answer covers:*
- STRIDE = 6 threat categories: Spoofing, Tampering, Repudiation,
  Information Disclosure, Denial of Service, Elevation of Privilege.
  Each maps to a security property violation.
- Draw a simple DFD: Browser → Auth API → Users DB.
  Mark trust boundary: Internet/App Zone crossing.
- Apply per data flow:
  Browser → Auth API: T/I = need TLS; S = need credential auth; D = rate limiting.
  Auth API → Users DB: T = parameterized queries (SQL injection); I = encryption at rest.
- Apply per process:
  Auth API: E = RBAC for admin; R = audit logging of all auth events.
- Output: threat register with owner + mitigation + status.
- Why at design time: cost to fix in design = hours; cost in production = orders
  of magnitude higher (Equifax, Capital One examples).
- OWASP A04 (Insecure Design): formally recognizes that design-level threats
  cannot be patched in code - the design must change.
- Tools: OWASP Threat Dragon (free), Microsoft Threat Modeling Tool, pytm (code).