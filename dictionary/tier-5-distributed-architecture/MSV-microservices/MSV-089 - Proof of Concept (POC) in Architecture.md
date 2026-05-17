---
id: MSV-089
title: Proof of Concept (POC) in Architecture
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-001, MSV-087, MSV-088, MSV-085
used_by: MSV-087, MSV-088
related: MSV-087, MSV-088, MSV-085, MSV-086, MSV-001, MSV-090
tags:
  - microservices
  - architecture
  - deep-dive
  - design
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 89
permalink: /microservices/proof-of-concept-poc-in-architecture/
---

# MSV-089 - Proof of Concept (POC) in Architecture

⚡ TL;DR - Proof of Concept (POC) in
Architecture: a time-boxed, scope-limited
experiment to validate technical feasibility
and key architectural assumptions BEFORE
full commitment. POC purpose: answer specific
questions ("Can we achieve < 50ms p99 latency
with Kafka Streams for real-time fraud detection?")
with minimal investment (1-2 engineers, 2-4
weeks). NOT a prototype (user-facing feature
preview). NOT an MVP (minimum viable product
for production). POC: code is THROWAWAY.
Key failure mode: POC that "proves" the
concept but becomes production code without
proper engineering. Result: technical debt
from day one. Clear POC contract: "this code
will not go to production; we will rebuild."

| #089 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What are Microservices, Technology Migration Strategy, Re-platforming vs Re-architecting, Monolith to Microservices Migration | |
| **Used by:** | Technology Migration Strategy, Re-platforming vs Re-architecting | |
| **Related:** | Technology Migration Strategy, Re-platforming vs Re-architecting, Monolith to Microservices Migration, On-Premises to Cloud Migration, What are Microservices, Anti-Patterns in Microservices | |

---

### 🔥 The Problem This Solves

**EXPENSIVE COMMITMENT TO UNVALIDATED TECHNOLOGY:**
Architect proposes: migrate from PostgreSQL
to Apache Cassandra for user profile storage
(reason: "Cassandra scales better"). Team:
spends 4 months migrating the user service
to Cassandra. 4 months in: discover that
Cassandra's limited secondary index support
makes the user search queries 100x slower
than PostgreSQL. Rollback: painful (4 months
of work lost). A 2-week POC: would have
discovered this before any commitment. POC
question: "Can Cassandra handle our user
search query patterns at target latency?"
Answer: no. Decision: stay with PostgreSQL.
Cost saved: 3.5 months of engineering.

---

### 📘 Textbook Definition

**Proof of Concept (POC)** in software architecture
is a time-boxed, focused experiment designed
to validate technical feasibility, performance
characteristics, or integration complexity
of a proposed architectural decision before
full implementation.

**POC vs Related Concepts:**

| Term | Purpose | Audience | Code fate |
|---|---|---|---|
| **POC** | Validate technical feasibility | Engineering team | Throwaway |
| **Prototype** | Validate user experience/design | Stakeholders/Users | Usually throwaway |
| **Spike** (Agile) | Reduce estimation uncertainty | Engineering team | Throwaway |
| **MVP** | Validate market fit | Real users | Becomes production |
| **Pilot** | Limited production rollout | Real users | Becomes production |

**Well-structured POC elements:**
1. **Specific questions**: "Can X achieve Y
   under Z conditions?" (not: "Let's explore X")
2. **Success criteria**: defined BEFORE building
   (what answer would make us proceed? what
   answer would make us choose alternative?)
3. **Time box**: 1-4 weeks. If not answered
   in time box: scope was too large (break down)
4. **Minimal team**: 1-2 engineers
5. **Throwaway contract**: explicit agreement
   that POC code will NOT go to production
6. **Decision record**: what was learned;
   architectural decision made; why

**Questions POC should answer:**
- Performance: "Does X meet our latency/throughput
  requirements?"
- Feasibility: "Can X integrate with our existing
  system Y?"
- Complexity: "Is the operational complexity
  of X acceptable to our team?"
- Cost: "What is the cloud cost of X at our
  expected load?"
- Learning: "Does our team have the skills
  to implement X? What gaps?"

---

### ⏱️ Understand It in 30 Seconds

**One line:**
POC: 2-4 week experiment to answer one specific
technical question before committing to an
architectural direction. Code is throwaway.

**One analogy:**
> POC is like a test drive before buying a
> car. You don't buy the car (full implementation),
> then discover it doesn't fit in your garage
> (doesn't meet requirements). You test drive
> first: does the performance feel right? Does
> it fit your family? Can you afford the
> insurance? If test drive answers yes:
> buy (proceed). If no: try different model
> (different technology). Test drive car:
> not your car (throwaway). The same car
> you buy after test drive: is built for you
> (production implementation, not POC code).

**One insight:**
The most important POC discipline is the
"throwaway contract." Without it: POC code
becomes production. Why: POC code is written
under time pressure with shortcuts (no error
handling, hardcoded credentials, no tests,
no logging). If it goes to production:
(1) no tests: unsafe to refactor; (2) no
logging: impossible to debug; (3) hardcoded
credentials: security breach waiting to happen;
(4) no error handling: fails silently. The
POC code that "works" in a 2-week demo:
creates 6-12 months of technical debt if
used in production. The throwaway contract:
more important than any technical decision
made during the POC.

---

### 🔩 First Principles Explanation

**POC STRUCTURE: GOOD VS BAD QUESTIONS**

```
BAD POC QUESTIONS (too vague, no clear answer):
  - "Let's explore Kafka"
  - "Can we use GraphQL?"
  - "How does Kubernetes work?"
  - "Should we use microservices?"
  These: produce interesting learning but
  no clear decision trigger

GOOD POC QUESTIONS (specific, measurable):
  - "Can Kafka Streams achieve < 50ms
    p99 latency for 10,000 transactions/sec
    real-time fraud detection scoring?"
  - "Can we integrate GraphQL with our
    existing Spring Boot + JPA setup with
    < 2 weeks of implementation per service?"
  - "Can a Kubernetes pod autoscale
    from 1 to 50 replicas in < 60 seconds
    to handle our Black Friday traffic spike?"
  - "Does PostgreSQL JSONB column perform
    within 10ms p99 for our user profile
    query patterns? (Alternative to MongoDB)"
    
SUCCESS CRITERIA (defined BEFORE building):
  "IF Kafka Streams achieves < 50ms p99 at
   10K TPS: proceed with Kafka Streams for
   fraud detection."
  "IF NOT: evaluate Apache Flink as alternative;
   OR accept higher latency with batch detection."
  Clear: yes/no answer from the POC.
  No ambiguity after the time box.
```

**POC FOR ARCHITECTURE DECISIONS:**

```
SCENARIO: Evaluating service mesh (Istio)
for the microservices platform

POC questions:
  Q1: What is the performance overhead of
    Istio sidecar proxy? (target: < 5ms
    added latency per service hop)
  Q2: Can Istio integrate with our existing
    Spring Boot services without code change?
  Q3: What is the Kubernetes resource
    overhead of Istio? (acceptable: < 10%
    CPU increase on 20-service deployment)

POC scope (2 weeks, 2 engineers):
  - Deploy Istio in staging K8s cluster
  - Deploy 3 representative services
  - Run load test: 1000 req/s, 10 service hops
  - Measure: latency (with vs without Istio)
  - Measure: CPU/memory overhead
  - Verify: mTLS auto-configured (no code change)

POC result:
  Q1: 2ms added per hop (< 5ms target: PASS)
  Q2: Zero code change to Spring Boot (PASS)
  Q3: 8% CPU overhead (< 10% target: PASS)
  Decision: proceed with Istio
  Confidence: HIGH (all questions answered)
  ADR: written with POC results as evidence
```

---

### 🧪 Thought Experiment

**AMAZON'S DYNAMO POC: 2004**

```
Amazon (2004):
  Problem: relational DB can't keep up
  with shopping cart read/write scale
  Specific question: "Can we build a key-value
  store that handles Amazon's read/write
  volume with 99.9% availability at < 10ms
  latency?"
  
POC approach:
  Small team: 2-3 engineers
  Time box: several months (large-scale POC)
  Questions: very specific
    - Consistent hashing: can it distribute
      data evenly?
    - Gossip protocol: can it handle
      membership in 1000-node cluster?
    - Eventual consistency: is it acceptable
      for shopping cart use case?
    
POC result:
  All questions: answered YES
  Key insight from POC: eventual consistency
  is acceptable for cart (customers rarely
  add items simultaneously on two sessions)
  
Production: DynamoDB (2007, as AWS service)
POC code: thrown away; rebuilt properly
  
Lesson:
  Even at Amazon's scale: specific POC questions
  first. Don't assume you know the answers.
  DynamoDB's eventual consistency design
  came FROM the POC question; not a prior
  decision imposed on the POC.
```

---

### 🧠 Mental Model / Analogy

> POC in architecture is like an expedition's
> scouting party. The main army (full engineering
> team) can't move until the terrain is known.
> The scouting party (2 engineers): small, fast,
> exploratory. Goes ahead, maps the terrain
> (validates technical feasibility), reports
> back (POC results), then the army moves with
> confidence (or chooses a different route).
> The scouting party doesn't build permanent
> structures (throwaway code). They establish:
> is this route viable? Under what conditions?
> What are the obstacles? Their report:
> is the architectural decision record (ADR).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
POC: small experiment (2-4 weeks) to check
if a technology works for your specific need
before spending months building it properly.
Answer your biggest uncertainty first.

**Level 2 - Time boxing (junior developer):**
POC time box: non-negotiable. If the question
isn't answered in 2-4 weeks: the question
was too broad (narrow it). Or: the technology
is too complex for your team (a signal itself).
Time box ends: write the ADR regardless of
result ("we proved it works" or "we proved
it doesn't work"). Both are valuable outcomes.

**Level 3 - Metrics-driven POC (mid-level):**
POC for performance decisions: always include
a load test. Technology that performs well
under low load (1 request/second): may fail
under production load (1,000 requests/second).
POC load test: use Apache JMeter, k6, or
Gatling. Target: 2x expected production
load (proves headroom). Always test under
concurrent load (not sequential): distributed
systems behave differently under concurrency.

**Level 4 - POC to ADR pipeline (senior):**
Every POC: should produce an ADR (Architecture
Decision Record). ADR: captures (1) context
(what problem, what alternatives), (2) decision
(what was chosen), (3) rationale (POC results
that support the decision), (4) consequences
(what tradeoffs are accepted). Without ADR:
in 12 months: no one remembers WHY Kafka was
chosen over SQS. New engineers: question
the decision; re-evaluate; waste time. ADR:
the institutional memory of architectural
decisions. POC without ADR: lost knowledge.

**Level 5 - POC at organizational scale (principal):**
POC at organizational scale: multiple teams
evaluating competing technologies simultaneously.
Bake-off: two teams, same requirements, different
technologies, same time box. Compare results
objectively. Example: Team A evaluates
Apache Flink; Team B evaluates Kafka Streams
(both for real-time processing). Bake-off
result: choose the winner based on evidence.
Risk: both teams: may recommend their technology
(survivorship bias - each team invested in
their choice). Mitigation: independent evaluation
criteria set by a third-party architect before
bake-off. No criteria change after results.

---

### ⚙️ How It Works (Mechanism)

```
POC CHECKLIST:

BEFORE (1 day):
  [ ] Specific question (1-3 questions MAX)
  [ ] Success criteria (quantified thresholds)
  [ ] Time box (1-4 weeks; start + end date)
  [ ] Team (1-2 engineers; named)
  [ ] Throwaway contract (signed off by all)
  [ ] Alternative (if POC fails, what's plan B?)

DURING:
  [ ] Build minimal implementation to test
      the specific question only
  [ ] Measure the specific metrics
  [ ] Document observations (daily notes)
  [ ] If time box threatens: narrow scope;
      don't extend the time box

AFTER (1 day):
  [ ] Write POC results report
      (quantified: latency numbers, code complexity)
  [ ] Make clear decision (proceed / don't proceed)
  [ ] Write ADR with POC results as evidence
  [ ] DELETE POC code (or archive clearly as
      "not production-ready POC")
  [ ] Share results with team
  [ ] Plan production implementation (separate project)
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
POC LIFECYCLE: Kafka Streams for fraud detection

  DAY 0: Problem statement
    Current: batch fraud detection (15 min latency)
    Goal: real-time (< 100ms)
    Candidate: Kafka Streams
    Alternative if fails: Apache Flink

  DAY 1: POC definition
    Question: Can Kafka Streams achieve < 100ms
    end-to-end fraud detection for 5,000 TPS?
    Success: p99 < 100ms at 5,000 TPS sustained
    Failure: p99 > 100ms -> evaluate Flink instead
    Time box: 3 weeks
    Team: 2 engineers (Alice + Bob)
    Throwaway: confirmed (no production usage)

  WEEK 1-2: Build minimal POC
    - Kafka Streams topology: simple rules
    - NOT: full fraud model (just enough to test)
    - NOT: production error handling
    - NOT: production security
    - YES: realistic data volume (5,000 TPS)
    - YES: latency measurement (Micrometer)

  WEEK 3: Load test + measurement
    Run: 5,000 TPS load test (k6)
    Measure: end-to-end latency (p50, p95, p99)
    Measure: Kafka lag (consumer keeping up?)
    Measure: CPU/memory of Kafka Streams app

  DAY 21: Results
    p99 latency: 45ms (< 100ms: PASS)
    Kafka consumer lag: < 100ms at 5K TPS (PASS)
    CPU: 2 vCPU at 5K TPS (acceptable: PASS)
    Decision: proceed with Kafka Streams
    ADR: written, shared, merged
    POC code: archived (labeled: NOT FOR PRODUCTION)

  WEEK 4+: Production implementation
    New project, new branch
    Proper error handling, tests, security
    Uses POC learning but not POC code
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Vague POC vs Specific POC**

```java
// BAD: POC without specific question or success criteria

// "Let's explore GraphQL" POC:
// Week 1: read GraphQL docs
// Week 2: build a GraphQL endpoint that returns users
// Week 3: add filtering to GraphQL query
// Week 4: present: "GraphQL is cool, we can use it"
// 
// Problems:
// - No specific question answered
// - No performance measurement
// - No integration complexity assessment
// - No comparison to REST baseline
// - Decision: based on enthusiasm, not evidence
// - POC code: becomes the production implementation
//   ("it already works, why rewrite?")
// Cost: 4 weeks + production debt
```

```java
// GOOD: Specific POC with measurable success criteria

// POC Question: "Can we replace our REST user API
// with GraphQL while:
// (1) maintaining p99 < 50ms for common queries
// (2) N+1 query problem solved by DataLoader
// (3) integration with Spring Security
// (4) < 1 week per service to add GraphQL layer"
//
// POC: 2 weeks, 1 engineer
// Result measured and documented:

// Performance test result (k6):
// REST GET /users?id=1: p99 = 8ms
// GraphQL query { user(id: 1) { name, email } }: p99 = 12ms
// GraphQL with DataLoader (N+1 fix): p99 = 11ms
// Verdict: PASS (< 50ms target met)

// N+1 solution: DataLoader batching confirmed working
// Spring Security integration: @AuthenticationPrincipal
// works in GraphQL resolver (PASS)
// Time per service: 3 days (< 1 week target: PASS)

// Decision: proceed with GraphQL
// ADR: written with above numbers
// POC code: DELETED (archived in branch)
//   "poc/graphql-evaluation-2024-01"
// Production implementation: new branch, clean code

// What the production implementation has
// (POC did NOT):
// - Unit tests (0 in POC)
// - Integration tests
// - Error handling (POC: returned raw exceptions)
// - Logging + tracing
// - Input validation
// - Production security (POC: Spring Security
//   manually configured, not production-hardened)
```

---

### ⚖️ Comparison Table

| Approach | POC | Prototype | Spike | MVP |
|---|---|---|---|---|
| **Purpose** | Validate technical feasibility | Validate UX/design | Reduce estimation uncertainty | Validate market fit |
| **Audience** | Engineering | Stakeholders/users | Engineering | Real users |
| **Duration** | 1-4 weeks | 1-3 weeks | 1-3 days | 4-12 weeks |
| **Code fate** | Throwaway (always) | Usually throwaway | Throwaway | Becomes production |
| **Output** | Decision + ADR | Clickable mockup | Estimate | Working product |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "The POC works, so we can ship it" | POC code is not production-ready by design. POC success criteria: "does the technical approach work?" Production criteria: "is the code correct, tested, secure, observable, and maintainable?" POC code has: no tests, no error handling, often hardcoded values, no security review. Shipping POC code: starts a project with 6-12 months of technical debt. Rule: POC code is thrown away even when the POC succeeds. The production implementation starts fresh, informed by POC learnings. |
| A POC that fails is wasted work | A POC that proves an approach DOESN'T work is equally valuable as one that proves it does. Discovering that Cassandra doesn't support your query patterns (in 2 weeks of POC) vs discovering it in month 4 of a full migration: saves 3.5 months of work. The purpose of the POC is to answer the question, not to confirm the answer you hoped for. Failed POC: the most valuable outcome is when it catches a wrong direction early. |
| POC and MVP are the same thing | POC and MVP serve opposite masters. POC: answers "can we build this?" (engineering question). MVP: answers "should we build this?" (product/market question). POC code: throwaway. MVP code: production. POC team: 1-2 engineers. MVP team: full product team. POC timeline: weeks. MVP timeline: months. Confusing them: leads to either throwaway code in production (POC code shipped as MVP) or MVP-quality effort spent on a feasibility question (expensive POC). |

---

### 🚨 Failure Modes & Diagnosis

**POC code shipped to production: the most common POC failure**

**Symptom:**
New microservice for real-time fraud detection:
Kafka Streams. Launched 3 months ago. Engineers:
always say "we need to refactor this, but
no time." Code review: reveals hardcoded
API keys, no unit tests, error handling that
consists of `catch (Exception e) { log.error(e); }`
(silently swallows errors). Customer fraud
detection: occasionally stops working with
no alert (exception caught and logged to
a log no one monitors). Security team:
finds API keys in the codebase (SOC2 audit
failure).

**Root Cause:**
The "fraud detection service" was the POC.
POC ran 3 weeks. Results were good. Product
Manager: "great, just deploy it!" Engineers:
protested, then complied (business pressure).
POC code: became production. All POC shortcuts:
now in production.

**Diagnosis:**
```
Code quality scan:
  Unit test coverage: 0%
  Integration test coverage: 0%
  Hardcoded credentials: 3 found (CRITICAL)
  Exception handling: catch-all with no alerting
  Logging: println statements (not structured)
  Health check: not implemented
  Metrics: none
  
Operational impact:
  Fraud detection: silent failures (undetected)
  Security: API keys in codebase (breach risk)
  Maintenance: no tests = can't safely change
```

**Fix:**
```
SHORT TERM (1 week):
  Rotate all hardcoded credentials immediately
  Add circuit breaker + dead letter queue
    (silent failures: now detected + alerted)

MEDIUM TERM (1 month):
  Rewrite service properly:
  - Full test suite (unit + integration)
  - Structured logging + distributed tracing
  - Health checks + readiness probes
  - Proper error handling + alerting
  - Code review from security team
  - This is the "rebuild after POC" that
    should have happened from day 1

ORGANIZATIONAL:
  Establish POC policy:
    "POC code cannot be shipped to production.
     POC -> ADR -> rebuild. Always."
    Engineering VP sign-off on exceptions
    (which should be: never)
```

---

### 🔗 Related Keywords

**Architecture process:**
- `Technology Migration Strategy` - POC is
  the validation step before migration commitment
- `Re-platforming vs Re-architecting` - POC
  validates which approach is technically feasible

**Organizational context:**
- `Anti-Patterns in Microservices` - POC code
  in production is a classic anti-pattern

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| POC STRUCTURE | 1-3 specific questions        |
|               | Quantified success criteria   |
|               | 1-4 week time box             |
|               | 1-2 engineers                 |
|               | Throwaway contract            |
+--------------+----------------------------------+
| OUTPUTS      | Decision (yes/no) + ADR        |
| NEVER OUTPUT | Production-ready code          |
+--------------+----------------------------------+
| ONE-LINER    | "Answer your biggest technical |
|              |  uncertainty first, cheaply.   |
|              |  Then rebuild properly."       |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Specific question + success criteria BEFORE
   building. "Can X achieve Y under Z?" If you
   don't know the success criteria: you can't
   evaluate the POC result.
2. Time box: 1-4 weeks. Non-negotiable. Extends:
   narrow the scope, don't extend the time.
3. Throwaway contract: POC code NEVER goes to
   production. If the POC succeeds: rebuild
   properly. This rule must be enforced by
   engineering leadership.

**Interview one-liner:**
"POC (Proof of Concept) in architecture: a 1-4 week
time-boxed experiment with 1-2 engineers to answer
specific technical questions before full implementation
commitment. Structure: specific questions (not 'explore
Kafka' but 'can Kafka achieve < 100ms p99 at 5K TPS?'),
quantified success criteria defined BEFORE building,
time box (non-negotiable), and throwaway contract
(POC code never goes to production). Output: ADR
(Architecture Decision Record) with evidence. Key
failure mode: POC code shipped to production
(no tests, no error handling, hardcoded credentials -
technical debt from day 1)."

---

### 💡 The Surprising Truth

The most valuable moment in any POC is NOT
the moment you see the technology work - it's
the moment you UNDERSTAND WHY it works (or
doesn't). When Kafka Streams achieves < 50ms
latency in your POC: the important question
is not "great, it works" but "WHY? What design
decisions made this possible? What would break
this in production that didn't appear in the
POC?" The POC engineer who answers these
questions: writes an ADR that's valuable for
years. The POC engineer who just confirms
"it works": writes an ADR that's useless
in 6 months when a new engineer asks why.
The depth of understanding from a POC: should
approach "I know this technology well enough
to teach it" before signing off on the ADR.
This is what separates a POC that de-risks
a decision from a POC that just creates false
confidence.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **POC DESIGN** For a proposed migration
   from REST to gRPC: write the POC plan.
   What are the 3 specific questions? What
   are the quantified success criteria for
   each? What is the time box? What does
   the load test scenario look like?
2. **ADR WRITING** After a POC, write a
   complete ADR: context, decision, alternatives
   considered, consequences (good and bad),
   POC quantitative results. What makes an
   ADR useful in 2 years vs one that becomes
   meaningless?
3. **POC SCOPE CONTROL** A POC is in week 3
   of a 2-week time box. The original question
   is only 70% answered. What do you do:
   extend the time box, narrow the scope,
   or declare it inconclusive and move to
   plan B? Justify your answer.
4. **THROWAWAY ENFORCEMENT** Your PM says:
   "The POC is working great; let's just ship
   it." Write the technical rebuttal: what
   specific risks does POC code have that
   production code must not? What is the
   time estimate for proper rebuild? How
   do you frame this as business risk?
5. **BAKE-OFF** Design a technology bake-off
   between Apache Flink and Kafka Streams for
   real-time analytics. What are the evaluation
   criteria? How do you prevent team bias
   (each team rooting for their technology)?
   How do you make the final decision when
   results are mixed (Flink wins on latency;
   Kafka Streams wins on operational simplicity)?

---

### 🧠 Think About This Before We Continue

**Q1.** Your team is evaluating whether to
build a feature using WebSockets (real-time
bi-directional) or Server-Sent Events (one-
way server push). Design the POC: what are
the 3 questions, the success criteria for
each, the time box, and what load test
scenario would differentiate the two
technologies at your expected production
scale (50,000 concurrent connections)?

**Q2.** A POC concludes that technology X
works but only under very specific conditions
(works at < 1,000 TPS; degrades at 5,000 TPS).
Your current load: 500 TPS. Expected load
in 18 months: 3,000 TPS. Do you proceed with
technology X? What additional POC work would
you do before committing? How do you write
the ADR when the answer is "yes, but with
caveats"?

**Q3.** Your organization has a culture where
POC code always ends up in production ("it
works, just ship it"). You've been asked to
create the engineering policy to prevent this.
What are the specific policy rules (not just
"don't do it")? What is the enforcement
mechanism (code review process, CI/CD gate,
architecture review board)? How do you handle
legitimate exceptions (POC code that is
actually production quality)?