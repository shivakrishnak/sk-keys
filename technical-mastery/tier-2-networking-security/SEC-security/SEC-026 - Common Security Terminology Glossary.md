---
id: SEC-026
title: "Common Security Terminology Glossary"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★☆☆
depends_on: SEC-001, SEC-003
used_by: SEC-027, SEC-087, SEC-094, SEC-095, SEC-096
related: SEC-001, SEC-003, SEC-025, SEC-027, SEC-087, SEC-094, SEC-095, SEC-096
tags:
  - security
  - terminology
  - cve
  - cvss
  - vocabulary
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/sec/common-security-terminology-glossary/
---

⚡ TL;DR - Security conversations use precise terminology.
Using terms incorrectly in a security context signals
shallow knowledge. Key distinctions:

- **Vulnerability vs Exploit vs Attack:** vulnerability = flaw
  in code/design. Exploit = code/technique using the flaw.
  Attack = someone actually executing the exploit.
- **CVE vs CWE:** CVE = specific vulnerability instance
  (CVE-2021-44228 = Log4Shell). CWE = vulnerability class
  (CWE-502 = Deserialization of Untrusted Data).
- **CVSS:** Severity score 0.0-10.0. Critical = 9.0+, High = 7.0-8.9.
- **Threat vs Risk:** threat = what could happen, risk = likelihood
  × impact. "We have a threat from DDoS" vs "Our DDoS risk
  is medium because we have mitigation controls."
- **Pentest vs Bug Bounty:** pentest = contracted, scope-limited,
  time-boxed professional security assessment. Bug bounty =
  ongoing program where independent researchers report
  vulnerabilities for rewards.

---

| #026 | Category: Security | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Security Problem, What Attackers Actually Do | |
| **Used by:** | Vuln vs Exploit, Responsible Disclosure, CVSS, CVE+NVD | |
| **Related:** | Attacker Mindset, CVSS Scoring, CVE+NVD, Responsible Disclosure | |

---

### 🔥 The Problem This Solves

**THE VOCABULARY GAP:**
Security reports, CVE databases, CVSS scores, CVE numbers,
CWE classifications, pentest reports, and security discussions
use a precise vocabulary. Misusing terms creates confusion:
"We have a vulnerability" (maybe you mean a risk, or an
exploit, or an attack surface). "The CVSS score is high"
(meaning what - base, temporal, or environmental?).
"This is a critical vulnerability" (by what standard?).

**WHY PRECISION MATTERS:**
Security prioritization depends on precise terminology.
A CVSS 9.8 (Critical) vulnerability with no available
exploit in the wild has a very different risk profile
from a CVSS 7.5 (High) vulnerability with an active exploit
kit. Understanding the difference between a vulnerability
(flaw exists) and an exploit (weaponized code exists) is
the difference between "patch next quarter" and "patch now."

---

### 📘 Textbook Definition

**Core Security Terminology (alphabetical by concept):**

**ATTACK SURFACE:**
The sum of all points where an attacker can attempt to
enter data or extract data from an environment. A web
application's attack surface: every URL, every parameter,
every file upload endpoint, every API, every authentication
form. Reducing attack surface = disabling or removing
unneeded components.

**ATTACK VECTOR:**
The path by which an attacker exploits a vulnerability.
CVSS uses: Network (exploitable remotely), Adjacent (requires
same network), Local (requires local access), Physical.
Network attack vector = remotely exploitable = highest severity.

**CVE (Common Vulnerabilities and Exposures):**
A standardized identifier for a specific, publicly known
vulnerability. Format: CVE-[year]-[number]. Maintained by
MITRE, published in NVD (National Vulnerability Database).
Examples: CVE-2021-44228 (Log4Shell), CVE-2014-0160 (Heartbleed),
CVE-2017-5638 (Equifax/Apache Struts RCE).
CVE = the unique ID, NVD = the database with full details.

**CWE (Common Weakness Enumeration):**
A taxonomy of vulnerability classes/patterns. Where CVE
identifies specific vulnerabilities, CWE categorizes the
type of weakness. CWE-89 = SQL Injection, CWE-79 = XSS,
CWE-502 = Deserialization of Untrusted Data. A CVE entry
will list the CWE category of the vulnerability.

**CVSS (Common Vulnerability Scoring System):**
A numerical score from 0.0 to 10.0 quantifying vulnerability
severity. Base score components: Attack Vector, Attack
Complexity, Privileges Required, User Interaction,
Scope, Confidentiality/Integrity/Availability Impact.
Severity ratings: Critical 9.0-10.0, High 7.0-8.9,
Medium 4.0-6.9, Low 0.1-3.9. Note: CVSS base score
does not account for threat intelligence or environmental
context - environmental score does.

**EXPLOIT:**
A program, code, or technique that takes advantage of a
vulnerability. Proof of Concept (PoC) exploit = demonstrates
the vulnerability without malicious payload. Weaponized
exploit = delivers a malicious payload (shell, ransomware).
The EXISTENCE of a public exploit dramatically changes
risk: a theoretical vulnerability with no known exploit
is very different from one with Metasploit module available.

**INDICATOR OF COMPROMISE (IoC):**
Evidence that a system has been compromised: unusual outbound
connections, unexpected processes, modified system files,
unusual account activity. Used in incident response to
determine scope of a breach.

**PAYLOAD:**
The component of an attack that causes the actual harmful
effect. In an SQL injection attack: the malicious SQL string
IS the payload. In malware: the ransomware executable is
the payload. In XSS: the JavaScript code that steals cookies
is the payload.

**PENTEST (Penetration Test):**
A contractual, scoped security assessment where professional
security testers attempt to compromise a system with
explicit authorization. Scope: specific systems, IP ranges,
time window. Types: black box (no prior knowledge),
grey box (partial knowledge), white box (full knowledge/source).
Output: a report of findings, severity, exploitation evidence.

**BUG BOUNTY:**
A program where organizations invite independent security
researchers to find and report vulnerabilities in exchange
for rewards (cash, credit, recognition). Ongoing (vs
point-in-time pentest), broader scope, crowdsourced.
Major platforms: HackerOne, Bugcrowd. Responsible disclosure
= the process of reporting to the vendor before public
disclosure.

**RCE (Remote Code Execution):**
A vulnerability class that allows an attacker to execute
arbitrary code on a target system over a network without
physical access. Generally Critical severity. Log4Shell
(CVE-2021-44228) is an RCE vulnerability.

**SSRF (Server-Side Request Forgery):**
The server makes requests on behalf of the attacker to
internal or external resources. Can reach internal services
behind firewalls, cloud metadata APIs (AWS IMDSv1 = credential
theft), or probe internal network topology.

**LFI / RFI (Local/Remote File Inclusion):**
Vulnerability where user input controls which file is
included/executed by the server. LFI reads local files
(e.g., /etc/passwd). RFI loads and executes a remote file.
Common in legacy PHP applications.

**THREAT:**
A potential cause of an incident that may result in harm.
Threats are categorized by source (external attacker,
insider, state actor) and type (STRIDE categories).
A threat is not a risk - risk = threat likelihood × impact.

**RISK:**
The probability that a threat will exploit a vulnerability
combined with the impact if it does. Risk = Likelihood
× Impact. Risk management = accepting, transferring,
mitigating, or avoiding risk.

**ZERO-DAY (0-Day):**
A vulnerability that is not publicly known and for which
no patch exists. "Zero days" of time for defenders to
prepare before attackers may use it. Zero-day exploits
are extremely valuable and closely held by nation-states
and sophisticated threat actors. Once public: n-day (some
number of days since disclosure).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Security vocabulary: vulnerability (flaw), exploit (weaponized
flaw), attack (using the exploit), CVE (specific vuln ID),
CWE (vuln class), CVSS (severity score), pentest (authorized
assessment), bug bounty (ongoing reward program), RCE
(remote code execution = worst case), zero-day (unknown
to vendor).

**One analogy:**
> A criminal law analogy: vulnerability = a broken lock,
> exploit = a technique for bypassing that specific broken
> lock, attack = someone actually breaking in. CVE = the
> specific lock model with the defect. CWE = the CLASS of
> defect (pin tumbler vulnerabilities). CVSS = severity
> rating the lock defect (does it affect all locks or just
> commercial grade?). Pentest = a locksmith hired to test
> all your locks. Bug bounty = offering a reward if anyone
> finds a broken lock before a burglar does.

---

### 🔩 First Principles Explanation

**Vocabulary precision enables risk-based decision making:**

```
WHY CVE PRECISION MATTERS:

Development team receives: "We have a Log4j vulnerability"
  (imprecise: which CVE? what CVSS? what component version?)

vs.

"CVE-2021-44228 (Log4Shell) in log4j-core 2.14.1
 CVSS 10.0 (Critical). Attack vector: Network.
 User interaction: None. Privileges required: None.
 Exploitability: active Metasploit module available.
 
 Your service authenticates incoming messages using Log4j.
 This specific code path receives user-controlled strings.
 Attacker can achieve RCE via JNDI lookup string in request."

DECISION IMPACT:
  Imprecise: "investigate when we have time"
  Precise: "ALL HANDS - patch and redeploy by end of day"

CVSS COMPONENTS THAT CHANGE DECISIONS:
  CVSS Base 9.8 + AV:Network + AI:None + PR:None
  = unauthenticated, network-reachable = patch TODAY

  CVSS Base 7.2 + AV:Local + PR:High + UI:Required
  = attacker needs local admin AND user interaction
  = patch in next sprint, not emergency

CVE + CVSS + Exploitability intelligence combined
= actual risk, not just theoretical severity.
```

---

### 🧪 Thought Experiment

**SCENARIO: Reading a CVE database entry**

```
CVE-2021-44228 (Log4Shell) - REAL ENTRY BREAKDOWN:

CVE ID: CVE-2021-44228
Published: 2021-12-10

CVSS v3.1 Base Score: 10.0 CRITICAL
  Attack Vector: Network        ← No local access needed
  Attack Complexity: Low        ← Easy to exploit
  Privileges Required: None     ← No auth needed
  User Interaction: None        ← Fully automated attack
  Scope: Changed                ← Affects components beyond vuln scope
  Confidentiality: High         ← Full data exposure
  Integrity: High               ← System can be fully modified
  Availability: High            ← Service can be destroyed

CWE: CWE-502 Deserialization of Untrusted Data
     CWE-917 Improper Neutralization of Special Elements

Description: Apache Log4j2 2.0-beta9 through 2.15.0 JNDI features
  used in configuration, log messages, and parameters do not protect
  against attacker controlled LDAP and other JNDI related endpoints.
  An attacker who can control log messages or log message parameters
  can execute arbitrary code loaded from LDAP servers when message
  lookup substitution is enabled.

WHAT THIS TELLS A DEVELOPER:
  - Score 10.0: highest possible. Emergency patch.
  - CWE-502: deserialization is the class of vulnerability.
  - "Control log messages": does user input ever reach log calls?
    Nearly every application logs user input somewhere.
  - Fix: upgrade to 2.17.1+ or set log4j2.formatMsgNoLookups=true

WHAT THIS TELLS A SECURITY ENGINEER:
  - Check every service for log4j-core version in dependency tree
  - Check if log messages include user-controlled data
    (strings from HTTP requests, headers, user inputs)
  - Temporary mitigation: WAF rule blocking ${jndi: in requests
  - Permanent: upgrade. No workaround is reliable.
```

---

### 🧠 Mental Model / Analogy

> CVE/CWE/CVSS are like an aircraft accident database.
> Accident report number (like a CVE): uniquely identifies
> the specific crash. Cause category (like CWE): landing gear
> failure, pilot error, weather, etc. NTSB severity
> rating (like CVSS): fatal, serious, minor incident.
> Understanding all three tells you what happened (CVE),
> what class of failure it was (CWE), and how bad it was
> (CVSS). Just having the accident number doesn't tell you
> how to prevent future crashes. Just having the cause
> category doesn't tell you which aircraft are affected.
> All three together: actionable intelligence.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Security has its own dictionary. A vulnerability is a flaw.
An exploit is a weapon built for that flaw. An attack is
someone using that weapon. CVE numbers are like part numbers
for flaws - they uniquely identify a specific flaw. CVSS
is the severity score. Knowing these terms lets you read
security reports, CVE databases, and vulnerability advisories
without confusion.

**Level 2 - How to use it (junior developer):**
When you see a CVE number in a dependency scanner alert:
look it up in NVD (nvd.nist.gov). Read: the CVSS score,
the affected version range, the description, and (critically)
are there known exploits in the wild? High CVSS + known
exploit = emergency patch. High CVSS + no known exploit
= patch this sprint. Medium CVSS + no known exploit = patch
in next release. CWE tells you the class of vulnerability
affecting your specific dependency.

**Level 3 - How it works (mid-level engineer):**
CVSS base score is theoretical maximum severity on a generic
system. Environmental score modifies based on your context:
if a Critical AV:Network vulnerability affects a service
that isn't internet-exposed (behind your VPN), the actual
risk is lower than CVSS base suggests. Similarly: a Medium
CVSS vulnerability in your authentication service carries
more actual risk than a Critical in an internal reporting
tool. Risk prioritization = CVSS base × exploitability
× business context, not CVSS base alone.

**Level 4 - Why it was designed this way (senior/staff):**
CVE was created in 1999 to solve a fragmentation problem:
different security tools referred to the same vulnerability
by different names. CVE provides a common language across
tools, vendors, and organizations. NVD enriches CVE with
CVSS scores, CWE classification, and CPE (affected products).
CVSS was designed to be vendor-neutral and reproducible.
The CVSS formula is public: anyone can compute the same
score from the same factors. The limitation: CVSS base
score doesn't incorporate threat intelligence, patch
availability, or environmental context - intentionally,
because those vary per organization. Environmental and
temporal CVSS scores exist but are rarely used in practice.

**Level 5 - Mastery (distinguished engineer):**
Advanced security risk programs use EPSS (Exploit Prediction
Scoring System) alongside CVSS. EPSS predicts the probability
that a CVE will be exploited in the wild within 30 days,
based on characteristics of the vulnerability and observed
exploitation patterns. A CVE with CVSS 9.8 but EPSS 0.5%
(low exploitation likelihood) may be lower actual priority
than CVSS 7.5 with EPSS 22% (actively exploited). CISA KEV
(Known Exploited Vulnerabilities catalog) is the authoritative
list of CVEs currently exploited by threat actors - if
a CVE is in KEV, it has confirmed real-world exploitation
and should be patched immediately regardless of CVSS score.
Security programs that only use CVSS base scores for
prioritization are leaving money on the table by patching
theoretical vulnerabilities over actively exploited ones.

---

### ⚙️ How It Works (Mechanism)

**CVE lifecycle and how information flows:**

```
CVE LIFECYCLE:

Discovery ──────────────────────────────────────────────→

  1. DISCOVERY:
     Researcher/organization finds vulnerability.
  
  2. RESPONSIBLE DISCLOSURE (ideally):
     Researcher contacts vendor privately.
     Vendor gets 90 days to patch (Google Project Zero standard).
  
  3. PATCH DEVELOPMENT:
     Vendor develops and tests fix.
  
  4. CVE ASSIGNMENT:
     CVE Numbering Authority (CNA) - vendor or MITRE - assigns CVE ID.
     This can happen before or at disclosure.
  
  5. PUBLIC DISCLOSURE:
     Patch released + CVE published in NVD.
     NVD adds CVSS score, CWE classification, CPE (affected versions).
  
  6. ECOSYSTEM RESPONSE:
     Dependency scanners (Dependabot, Snyk, OWASP Dependency-Check)
     update databases to flag affected libraries.
     Organizations receive automated alerts.
  
  7. PATCH DEPLOYMENT:
     Organizations update affected dependencies/software.

ZERO-DAY vs N-DAY:
  Zero-day: vulnerability unknown to vendor / not yet patched.
  N-day: vulnerability known for N days. Patch may exist.
  The distinction changes attacker economics:
    Zero-day: valuable, expensive, often used only by nation-states.
    N-day: cheap, widely available, used by lower-sophistication actors.
  After public disclosure: n-day exploits proliferate rapidly.
  Patch ASAP after public disclosure.
```

---

### 💻 Code Example

**Using security terminology in incident documentation:**

```markdown
# Security Incident Report

## Incident: SQL Injection in User Search Endpoint

### Identification
**CVE:** N/A (internal vulnerability, not publicly reported)
**CWE:** CWE-89 (SQL Injection)
**CVSS Base Score:** 8.8 (High)
  - Attack Vector: Network (AV:N)
  - Attack Complexity: Low (AC:L)
  - Privileges Required: Low (PR:L) - requires authentication
  - User Interaction: None (UI:N)
  - Scope: Unchanged (S:U)
  - Confidentiality: High (C:H)
  - Integrity: High (I:H)
  - Availability: Low (A:L)

### Vulnerability
**Type:** SQL Injection via unsanitized search parameter
**Component:** UserSearchService.searchByName()
**Affected versions:** 2.1.0 - 2.4.3

**Vulnerable code:**
    query = f"SELECT * FROM users WHERE name = '{search_term}'"

**Exploit condition:**
  Authenticated user sends search_term = "' OR '1'='1";DROP TABLE users;--"
  Exploitability: Proof of Concept confirmed in staging.
  No known public exploit. No current external exploitation.

### Risk Assessment
**Business impact:** All user records potentially extractable.
  User PII (name, email, phone). No payment card data exposed.
**Attack surface:** External (authenticated users, ~50,000 accounts).
**Exploitability in wild:** Low - no active exploitation observed.
**Risk rating:** High (CVSS 8.8 with confirmed PoC)

### Remediation
**Fix:** Parameterized queries using PreparedStatement.
**Patch version:** 2.4.4 (released 2024-01-15)
**Verification:** Security regression test added.
**Patch status:** Deployed to production 2024-01-16.
```

---

### ⚖️ Comparison Table

| Term | Meaning | Example |
|:---|:---|:---|
| **Vulnerability** | Flaw in system | Unparameterized SQL query |
| **Exploit** | Code/technique using flaw | SQLMap payload for that query |
| **Attack** | Actual exploitation | Attacker runs SQLMap against endpoint |
| **CVE** | Specific vuln ID | CVE-2021-44228 (Log4Shell) |
| **CWE** | Vulnerability class | CWE-89 (SQL Injection class) |
| **CVSS** | Severity score 0-10 | 10.0 (Critical) |
| **Zero-day** | Unknown, unpatched | State actor exploit, no CVE yet |
| **N-day** | Known, patch may exist | CVE exists, patch available |
| **Pentest** | Authorized assessment | Contracted annual pentest |
| **Bug bounty** | Ongoing reward program | HackerOne program |
| **RCE** | Remote code execution | Critical, highest impact class |
| **SSRF** | Server fetches attacker-controlled URL | Internal metadata API access |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| CVSS 10.0 = drop everything and patch right now | CVSS base score is theoretical severity on an uncontrolled target system. A CVSS 10.0 on a library that's: not in your dependency tree, in an internal-only component not reachable from internet, or mitigated by compensating controls (WAF rule, network segmentation) may be a lower actual priority than a CVSS 7.0 with an active public exploit affecting your internet-facing authentication endpoint. CVSS + exploitability + business context = actual risk. |
| A CVE being "fixed" in a library means you're protected after upgrading | The patch in the library only protects you after you upgrade. Organizations using old library versions remain vulnerable to old CVEs for months or years. Most successful attacks use n-day exploits against unpatched systems, not zero-days. The Equifax breach (CVE-2017-5638) occurred 2 months after a patch was available. The vulnerability being publicly known with a patch available does not mean it's exploited less - it means exploit code is more widely available. |

---

### 🚨 Failure Modes & Diagnosis

**Common terminology errors in security practice:**

```
ERROR 1: Conflating severity with risk
  "CVE-2021-XXX is Critical, so it's our top priority."
  FIX: "CVE-2021-XXX is Critical (base score). Our service
    uses the affected library, the attack vector is Network,
    we have no WAF rule. Actual risk: Critical. Top priority."
  
  vs.
  
  "CVE-2022-YYY is Critical but the library is used only
    in our internal batch processor, not internet-exposed.
    Actual risk: Medium-High. Patch in next sprint."

ERROR 2: Treating PoC and weaponized exploit the same
  "There's an exploit for this, patch immediately."
  FIX: "Is this a PoC (shows it's exploitable, requires
    technical skill) or a weaponized exploit (Metasploit
    module, point-and-click tool)?"
  A weaponized exploit means even low-skill attackers
  can exploit it. Dramatically changes urgency.

ERROR 3: Ignoring EPSS and KEV for prioritization
  Most orgs prioritize by CVSS alone.
  Better: CVEs in CISA KEV = actively exploited = patch immediately.
  EPSS > 10% = patch this week even if CVSS is "only" 7.5.

DIAGNOSTIC QUESTIONS WHEN REVIEWING A CVE:
  1. Is this in CISA KEV? (yes = immediate)
  2. Is there a weaponized exploit? (Metasploit, etc.)
  3. What is the attack vector? (Network = worse)
  4. Is the vulnerable component in our dependency tree?
  5. Is that component in an internet-facing service?
  6. Do we have any compensating controls?
  Only after answering all six: make a priority decision.
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Problem in Software Engineering` - context for the vocabulary
- `What Attackers Actually Do` - who uses these terms

**Builds on this:**
- `Vulnerability vs Exploit vs Attack` - deeper treatment of that trio
- `CVSS Scoring` - computing the score yourself
- `CVE and NVD` - using the database
- `Responsible Disclosure` - the process of reporting vulnerabilities

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CVE     │ Unique ID for specific vulnerability           │
│ CWE     │ Class of vulnerability (SQL Inj, XSS, etc.)   │
│ CVSS    │ Severity 0-10. Critical=9+, High=7-8.9        │
├─────────┼─────────────────────────────────────────────────┤
│ Vuln    │ The flaw in the code/design                    │
│ Exploit │ Code/technique weaponizing the flaw            │
│ Attack  │ Actual use of the exploit against a target     │
├─────────┼─────────────────────────────────────────────────┤
│ 0-Day   │ Unknown to vendor, no patch exists             │
│ N-Day   │ Public, patch may exist, exploits proliferate  │
├─────────┼─────────────────────────────────────────────────┤
│ Pentest │ Contracted, scoped, time-boxed assessment      │
│ Bounty  │ Ongoing, crowdsourced vulnerability reporting  │
├─────────┼─────────────────────────────────────────────────┤
│ RCE     │ Remote code execution - Critical class         │
│ SSRF    │ Server-side request forgery                    │
│ IoC     │ Indicator of compromise (breach evidence)      │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Precise vocabulary enables precise decisions." In any
technical domain, imprecise language leads to imprecise
action. "This system is slow" doesn't enable diagnosis.
"p99 latency is 4.2 seconds on the /api/search endpoint
with query complexity > 3 joins" enables action. Security
is no different: "we have a vulnerability" doesn't drive
decisions. "CVE-2021-44228, CVSS 10.0, EPSS 89%, in
CISA KEV, in our internet-facing auth service running
log4j-core 2.14.1" drives an all-hands emergency. The
investment in vocabulary is an investment in the precision
needed for effective decisions.

---

### 💡 The Surprising Truth

Most successful cyberattacks use publicly known vulnerabilities
(n-days), not zero-days. The Ponemon Institute and Verizon
DBIR data consistently show: organizations are breached
by vulnerabilities that had patches available for months
or years. The Equifax breach exploited a vulnerability
with a patch available 78 days earlier. The romanticized
image of attacker sophistication (secret zero-days, NSA-grade
tools) obscures the mundane reality: attackers take the path
of least resistance, and unpatched n-days are the widest
open door. Zero-days are expensive, precious, and reserved
for high-value targets by sophisticated actors. Mass
exploitation uses automation and widely-available exploit
kits against the long tail of unpatched systems. Implication:
systematic patch management eliminates the attack vector
used in most breaches. Patch management is not glamorous
security work, but it's where the biggest risk reduction
per dollar invested lies.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DISTINGUISH** vulnerability, exploit, and attack in
   a security incident description. "An exploit for this
   vulnerability was used to conduct an attack."
2. **READ** a CVE entry and extract: what's vulnerable, what
   version, what CVSS severity, what CWE class, if exploits exist.
3. **EXPLAIN** why CVSS base score doesn't equal business risk,
   and what factors modify the priority decision.
4. **DIFFERENTIATE** pentest and bug bounty: timing, scope,
   who does the testing, output.

---

### 🎯 Interview Deep-Dive

**Q: How do you prioritize which security vulnerabilities
to fix first?**

*Why they ask:* In any real codebase, there will always
be more vulnerabilities than capacity to fix them.
Prioritization skill is critical.

*Strong answer includes:*
- Framework: not CVSS alone. CVSS base × exploitability ×
  business context = actual priority.
- First filter: Is the CVE in CISA KEV (Known Exploited
  Vulnerabilities)? If yes: immediate. The US government
  tracks actively exploited CVEs - these are confirmed real-world
  attacks.
- Second: Is there a weaponized exploit available (Metasploit
  module, public exploit code)? Weaponized = any attacker
  can exploit without deep technical skill. Dramatically
  raises urgency.
- Third: Attack vector. AV:Network + PR:None = anyone on
  internet can try. AV:Local = much harder to exploit.
- Fourth: Is this in an internet-facing component or
  internal-only? Same CVE, vastly different exposure.
- Fifth: Do we have compensating controls? WAF rule,
  network segmentation, or additional authentication
  layer reduces effective risk.
- Output: tier 1 = patch this week (KEV or weaponized + internet-facing),
  tier 2 = patch this sprint (high CVSS + internet-facing),
  tier 3 = patch in next release (medium/internal).
  Accept risk for tier 3 items that are internal and have no known exploit.