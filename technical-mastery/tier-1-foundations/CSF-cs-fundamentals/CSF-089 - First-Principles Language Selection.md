---
id: CSF-089
title: First-Principles Language Selection
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-083, CSF-088, CSF-080
used_by:
related: CSF-083, CSF-088, CSF-080, CSF-082, CSF-086
tags: [first-principles, language-selection, requirements-analysis, reasoning, engineering-judgment]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 89
permalink: /technical-mastery/csf/first-principles-language-selection/
---

⚡ TL;DR - First-principles language selection: starting from REQUIREMENTS, not from preferences
or popularity. Step 1: what problem is being solved? Step 2: what does the problem require from
a programming language (deterministic latency? memory safety? domain-specific libraries? runtime
portability?)? Step 3: what languages satisfy ALL the requirements? Step 4: of those, which
minimizes total cost of ownership (team capability, ecosystem maturity, operational cost, longevity)?
Elon Musk's first-principles analogy: "don't start with what languages we know - start with what
language would we design for this problem, then find the closest existing match."

| #089 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-083 (Language Evaluation Framework), CSF-088 (Trade-off Framing), CSF-080 (Language Design Rationale) | |
| **Used by:** | (technology strategy, platform decisions, greenfield architecture, technical leadership) | |
| **Related:** | CSF-083 (Evaluation Framework), CSF-088 (Trade-off Framing), CSF-080 (Design Rationale), CSF-082 (Polyglot Architecture), CSF-086 (Paradigm-Agnostic Thinking) | |

---

### 🔥 The Problem This Solves

**THE ASSUMPTION-FIRST SELECTION FAILURE:**

Most language selection decisions in practice:
1. The team has experience with Java.
2. A new service is needed.
3. Decision: Java. (No analysis. Assumed.)

The ASSUMPTION: "Java is the right language because we know it" is not engineering reasoning.
It is HABIT. Sometimes habit is correct (familiarity has real value). But habits:

- Never discover that Go would have been 50% lower memory for this network-intensive service.
- Never discover that the service has a hard requirement (sub-1ms deterministic latency)
  that Java's GC cannot reliably meet without significant tuning.
- Never discover that Kotlin would have halved the boilerplate for this Android feature.
- Never surface the question: "What would the IDEAL language for this specific problem be?"

**THE CARGO-CULT SELECTION FAILURE:**

Opposite failure: a team reads about Rust at a conference. "Companies like Discord and Figma
use Rust for performance-critical services." Decision: rewrite the order management service
in Rust for performance.

Questions not asked:
- Is the order management service actually a performance bottleneck? (Probably not.)
- What SPECIFIC performance requirement does the service fail to meet? (None identified.)
- Does the team have Rust expertise? (No.)
- Does the Rust ecosystem have the required libraries (Spring Data equivalent, Hibernate)? (No.)

Result: the service is rewritten in Rust, takes 12 months instead of 3, nobody can debug the
production issues, and the "performance improvement" was never measurable because the original
Java service was not a bottleneck.

**FIRST-PRINCIPLES PREVENTS BOTH:**

Starting from requirements: (1) identifies the ACTUAL requirements before any language is named,
(2) eliminates languages that fail to meet hard requirements, (3) selects from the remaining
viable options based on total cost of ownership. No habit. No cargo cult.

---

### 📘 Textbook Definition

**First Principles Reasoning:** A problem-solving approach that decomposes a problem to its
most fundamental truths (the "first principles") and reasons from those truths, rather than
reasoning from analogy (what other people have done) or from existing solutions. Associated
with philosophers: Rene Descartes ("Cogito, ergo sum" as the one unquestionable truth). Modern
popularization: Elon Musk's application to engineering problems ("What are the physics? What
materials are needed? What would it cost if we started from scratch?").

**Hard Requirements vs Soft Requirements:**
- Hard requirement: a property that MUST be satisfied. Failure to satisfy it: the solution
  is rejected regardless of other properties. "The system must respond within 1ms p99." If a
  language cannot meet this: it is eliminated.
- Soft requirement: a property that is DESIRED but can be traded off. "Prefer Java because the
  team knows it." This is a soft requirement: it has cost (team familiarity) but can be weighed
  against other benefits.

**First-Principles Language Selection:** The process of (1) starting with the requirements of the
problem (not the team's preferred language), (2) identifying the hard requirements that eliminate
language candidates, (3) identifying which remaining languages best satisfy the requirements,
(4) selecting based on TOTAL cost of ownership, not on a single dimension.

**Analogy-Based Reasoning (contrast with first principles):** Reasoning by comparison to
existing solutions. "Facebook uses Hack. We're building a social network. We should use Hack."
The analogy: may be correct, but it skips the question "WHY did Facebook choose Hack?" and
"Do we have the same constraints as Facebook?" First principles: derives the answer from the
requirements, not from analogies to others' solutions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Start with REQUIREMENTS, not preferences. What does the problem NEED from a language?
Eliminate languages that fail any hard requirement. Select the remainder that minimizes
total cost of ownership.

**One analogy:**

> Building a bridge: first principles engineering.
>
> ASSUMPTION-FIRST: "We've always built bridges with wood. Use wood."
>   -> Result: wooden bridge that fails under the required load.
>   -> The assumption (wood) was never tested against the requirement (load capacity).
>
> ANALOGY-FIRST: "The Golden Gate Bridge uses steel. Use steel."
>   -> Maybe correct for the same problem. Wrong if this is a pedestrian bridge.
>   -> The analogy (Golden Gate) was never tested against THIS bridge's requirements.
>
> FIRST PRINCIPLES: "What is this bridge required to carry?
>   Cars: 10T load. 50-year lifespan. Salt air corrosion resistance required.
>   Span: 200m. What materials meet ALL these requirements?
>   Steel + weathering coating. Wood: fails load. Aluminum: too expensive. Steel: viable."
>
> The first-principles bridge engineer: arrives at "steel" by DERIVING it from requirements,
> not by analogy or habit. Same process for language selection.

**One insight:**

The first-principles approach sounds slow. "Won't analyzing requirements from scratch take
longer than just using Java?" In practice: the requirements analysis takes 1-3 hours for
a typical service. The COST of skipping it: discovered over 1-3 years of maintaining the
wrong choice. Discord migrated from Go to Rust for their read-states service (2020) because
Go's GC caused latency spikes that violated their real-time performance requirements -
requirements they didn't fully analyze before choosing Go. The first-principles analysis
(including GC behavior as a hard requirement) would have identified this BEFORE the choice.
1-3 hours of analysis vs 6 months of migration work. First principles: pays for itself.

---

### 🔩 First Principles Explanation

**THE FIVE-QUESTION FRAMEWORK:**

```
┌──────────────────────────────────────────────────────┐
│ FIRST-PRINCIPLES LANGUAGE SELECTION:                 │
│ 5 QUESTIONS IN ORDER                                 │
│                                                      │
│ Q1: WHAT PROBLEM IS BEING SOLVED?                   │
│   Describe the problem in non-language terms:       │
│   "Process 100K financial transactions per second.  │
│    Each transaction: validate, apply business rules,│
│    persist, and notify downstream services."        │
│   NOT: "Build a microservice." (Too vague.)         │
│   NOT: "Build it in Java." (Language assumed.)      │
│                                                      │
│ Q2: WHAT ARE THE HARD REQUIREMENTS?                  │
│   (Non-negotiable. Failing any = eliminate language) │
│   "Latency: p99 < 10ms" -> eliminates languages     │
│     with GC pauses > 10ms (Java G1GC: sometimes    │
│     fails this without tuning. ZGC: likely meets). │
│   "Memory: < 128MB per instance" -> eliminates JVM  │
│     (baseline ~200-500MB). Go or Native: viable.   │
│   "Domain library X required" -> eliminates any    │
│     language without a mature X library.            │
│   "Team: deploy on WASM" -> eliminates non-WASM    │
│     compilation targets.                            │
│                                                      │
│ Q3: WHAT DOES THIS PROBLEM REQUIRE FROM A LANGUAGE? │
│   "Concurrent execution model?" -> Go goroutines,  │
│     JVM virtual threads, Kotlin coroutines?        │
│   "Type safety for financial correctness?" ->      │
│     static typing with sum types (Kotlin, Scala,  │
│     Rust, Java with records+sealed).               │
│   "Domain-specific library?" -> Python for ML,    │
│     Java for enterprise (Spring), Go for CLI tools.│
│   "Ecosystem for FIX protocol?" ->                 │
│     QuickFIX/J (Java), QuickFIX/Go.               │
│                                                      │
│ Q4: WHAT LANGUAGES SATISFY ALL HARD REQUIREMENTS?   │
│   After Q1-Q3: a SHORT LIST remains. All viable.   │
│   Typically 1-3 languages pass the hard requirement │
│   filter. Often: the team's existing language IS   │
│   in the viable list (familiarity has real value). │
│                                                      │
│ Q5: OF THE VIABLE LANGUAGES, WHICH HAS LOWEST TCO? │
│   Team capability: existing expertise?             │
│   Ecosystem: all required libraries?              │
│   Operational cost: monitoring, CI/CD, on-call?   │
│   Longevity: hiring pool, active ecosystem?        │
│   Choose the viable language with the lowest total │
│   cost of ownership.                               │
└──────────────────────────────────────────────────────┘
```

**THE "IDEAL LANGUAGE" THOUGHT EXERCISE:**

The most powerful first-principles question: "If I had to DESIGN a language for this
problem, what properties would it have?"

```
EXAMPLE: First-principles for an HFT (High-Frequency Trading) system.

"What properties would the IDEAL language for HFT have?"
  1. Deterministic latency: no GC pauses. NEVER stop-the-world.
     Ideal: manual memory management OR GC-less runtime.
  2. Direct hardware access: SIMD instructions, memory alignment control.
     Ideal: control over memory layout.
  3. Zero-overhead abstractions: abstractions that cost nothing at runtime.
     Ideal: compile-time zero-cost abstractions.
  4. Minimal runtime: no JVM, no interpreter. Maximum predictability.
     Ideal: AOT compiled to machine code with no runtime overhead.
  5. Type safety: financial calculations require precision.
     Ideal: strong static type system.
  6. Fast I/O: kernel bypass networking (DPDK/XDP) for < 1 microsecond latency.
     Ideal: language that allows raw kernel bypass networking.

"What existing language MOST CLOSELY matches this ideal?"
  C++: manual memory, SIMD, zero-overhead abstractions, AOT, strong types, DPDK support.
    Cost: manual memory management = memory safety risk.
  Rust: manual memory WITH safety guarantee (borrow checker), SIMD, zero-cost abstractions,
    AOT, strong types, DPDK support emerging.
    Cost: borrow checker complexity for some shared-state patterns.
  Java (with ZGC + pre-allocated off-heap): JVM startup + ZGC (< 1ms GC).
    Off-heap direct ByteBuffer: bypasses GC for hot path data.
    Not pure deterministic: ZGC pauses are < 1ms but not zero.
    Cost: still has GC; cannot match C++/Rust determinism for extreme cases.
  Go: GC (though very low pause), no DPDK direct support, simpler than Rust/C++.
    Cost: GC pauses (sub-1ms but present). Not DPDK-ready without C FFI.

"Decision: C++ or Rust for extreme HFT (sub-microsecond). Java ZGC acceptable
for latency > 1ms (most financial services, not extreme HFT)."

This reasoning: derived FROM REQUIREMENTS. Not "C++ is what we always used."
Not "Rust is what the cool kids use now."
```

---

### 🧪 Thought Experiment

**FIRST-PRINCIPLES FOR A MOBILE GAME SERVER**

Context: mobile game, 1 million concurrent users, real-time multiplayer state sync.

```
Q1: WHAT IS THE PROBLEM?
  "Maintain real-time game state for 1 million concurrent players.
   Each player: sends position updates 10 times per second.
   Server: broadcasts to nearby players (< 100m in game world).
   Maximum latency acceptable: 100ms (game-play critical).
   Peaks: 10x normal load during launch events."

Q2: HARD REQUIREMENTS:
  - 10M msg/s throughput (1M players * 10 updates/s)
  - p99 latency < 100ms
  - Horizontal scalability (stateless or state-sharded: 10x spikes)
  - Memory: efficient (< 1MB per connected player = < 1TB total: needs sharding)

Q3: WHAT DOES THIS REQUIRE FROM A LANGUAGE?
  - High concurrency model: 1M concurrent WebSocket connections.
    -> Requires: goroutines (Go), JVM virtual threads (Java 21), async I/O (Rust Tokio).
    -> NOT: thread-per-connection model (1M OS threads: infeasible, ~50GB stack memory).
  - Low GC pause: 100ms latency budget. GC pause must be < 20ms.
    -> Java: ZGC (< 1ms). Go: sub-1ms GC. Rust: no GC.
  - Fast binary serialization: 10M msg/s requires efficient (de)serialization.
    -> Protobuf or FlatBuffers in any language: fast enough.
  - Ecosystem: WebSocket server, game state management.
    -> Netty (Java), Go net/http, Rust actix-web/tokio-tungstenite.

Q4: VIABLE LANGUAGES:
  Go: goroutines (1M concurrent = lightweight goroutines: viable), sub-1ms GC, fast.
    Ecosystem: WebSocket libraries mature.
  Java (21+): virtual threads (1M = lightweight virtual threads: viable), ZGC: viable.
    Ecosystem: Netty (battle-tested for game servers: Riot Games uses Netty for LoL).
  Rust: async Tokio (1M concurrent: viable), no GC (zero latency from GC).
    Ecosystem: mature (actix-web for WebSocket).
  Node.js: single-threaded event loop (1M connections: viable with clustering).
    JavaScript: fast to develop. Runtime: V8 JIT.
  All four: technically viable. Team capability: determines the winner.

Q5: LOWEST TCO:
  For a 5-person team with Java expertise:
    Java (21+ virtual threads + ZGC + Netty): lowest TCO.
    - Immediate productivity. Existing expertise. Netty: battle-tested for game servers.
    - ZGC: meets 100ms latency requirement.
    - Virtual threads (Java 21): 1M concurrent connections without goroutines.
  For a 5-person team with Go expertise:
    Go: lowest TCO.
    - Goroutines: natural for 1M concurrent players.
    - Sub-1ms GC: meets latency. Simple deployment.
  For a team with no expertise in any language:
    Go or Java: both good. Go: faster ramp-up (simpler language).
```

---

### 🎯 Mental Model / Analogy

**THE REQUIREMENTS FILTER FUNNEL**

```
┌──────────────────────────────────────────────────────┐
│ LANGUAGE SELECTION FUNNEL:                          │
│                                                      │
│ START: All languages (~500 general-purpose langs)   │
│           |                                         │
│ FILTER 1: Mature enough for production use?         │
│   (100+ general-purpose languages: eliminate       │
│    esoteric, research, single-use languages)        │
│           |                                         │
│ FILTER 2: Required ecosystem libraries exist?       │
│   ML/AI service: Python, Julia, Java (DL4J)        │
│   Android app: Kotlin, Java                        │
│   iOS app: Swift, Objective-C                      │
│   Embedded IoT: C, C++, Rust, MicroPython         │
│   (Usually 3-8 languages survive this filter)     │
│           |                                         │
│ FILTER 3: Performance hard requirements met?        │
│   p99 < 1ms: Rust, C++, C. (Eliminates JVM, Go)  │
│   p99 < 10ms: Go, Java ZGC, Rust. (Eliminates Python│
│     for CPU-bound tasks)                           │
│   p99 < 100ms: Any language.                       │
│   (Typically: 1-4 languages survive)               │
│           |                                         │
│ FILTER 4: Memory hard requirements met?             │
│   < 64MB: Rust, C, C++, Go, Native Image.          │
│   < 256MB: Go, Native Image, Java (tuned).         │
│   < 512MB: Java, Python, Node.js.                  │
│   (Usually: 1-3 languages survive)                 │
│           |                                         │
│ REMAINING: Viable candidates. All satisfy hard reqs.│
│           |                                         │
│ TCO SELECTION: Team capability, ecosystem,          │
│   operational cost, longevity.                      │
│           |                                         │
│ DECISION: Best TCO among viable candidates.         │
└──────────────────────────────────────────────────────┘
```

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
When choosing which tool to use for a project: first ask "what do I need the tool to DO?"
Make a list of the MUST-HAVE requirements. Any tool that cannot do all the must-have things:
is removed from the list. Then from the remaining tools: choose the one that is easiest to
use and that you know best. Never choose a tool just because it's popular or new.

**Level 2 - Student:**
First-principles applied to a web backend choice:
```
Problem: "Build a REST API for a mobile app. 1000 RPS at peak. < 200ms p99."

Hard requirements:
  - REST HTTP server: all languages have this. Not a filter.
  - PostgreSQL client: Java, Python, Go, Node.js, Rust. All viable.
  - < 200ms p99: all languages with proper async. Not a filter (all pass at 1000 RPS).
  - JWT authentication: all languages. Not a filter.

Soft requirements:
  - Team knows Java (5 engineers with Java experience).
  - Spring Boot ecosystem (Spring Security, Spring Data).
  - Kubernetes deployment.

Hard requirement analysis: NO hard requirements eliminate any language for this problem.
TCO analysis:
  Java: immediate productivity (team knows it), Spring Boot handles JWT + PostgreSQL + REST.
  Go: 0 existing expertise. Would need 2-3 months training.
  Python: partial expertise (1 engineer). Limited throughput capacity vs Java at 1000 RPS.
  Node.js: 0 expertise. Training needed.

DECISION: Java. All hard requirements met. Lowest TCO due to team expertise.
NOTE: This is NOT "use Java because we always do."
It IS "Java is the correct first-principles choice because: hard requirements met,
and Java has the lowest TCO given the team's existing expertise."
```

**Level 3 - Professional:**
First-principles for a real-world architecture decision:
```
DISCORD'S READ STATES SERVICE - FIRST-PRINCIPLES ANALYSIS:

Context: Discord's read states service tracks which messages each user has read.
Requirements: millions of users, each updating read state frequently (every message read).
Discord's experience (2020):

ORIGINAL CHOICE: Go
  First-principles at time of Go adoption (2017):
  - High concurrency: 1M+ connections. Go goroutines: suitable. PASS.
  - Low latency: sub-50ms. Go: generally suitable. PASS.
  - Team capability: team had Go expertise. LOW TCO.
  - Ecosystem: mature HTTP/gRPC libraries. PASS.
  
  DISCOVERED HARD REQUIREMENT (missed at initial analysis):
  Go's GC: triggered latency SPIKES (not sustained high latency).
  GC pauses: typically < 1ms, but occasional pauses of 10-100ms during GC cycles.
  The read states service: latency SPIKES unacceptable (real-time user experience).
  
  FIRST-PRINCIPLES RE-ANALYSIS when spikes became a production problem:
  "What does the read states service REQUIRE from a language?"
  Key insight: "ZERO GC PAUSE, NOT JUST LOW GC PAUSE."
  The GC SPIKES (not average latency) were the hard requirement.
  
  LANGUAGE FILTER APPLIED TO "ZERO GC PAUSE":
  Go: sub-ms average BUT has occasional pauses. FAIL on "zero GC pause" hard requirement.
  Java ZGC: sub-1ms concurrent. BORDERLINE (technically still has pauses).
  C++: manual memory = no GC. PASS. But safety risk.
  Rust: no GC (Rust's ownership system handles memory without GC). PASS.
  
  DECISION: Migrate read states from Go to Rust.
  Result: eliminated GC-related latency spikes entirely. Memory usage: halved.
  
LESSON: The hard requirement (zero GC SPIKES) was only discovered in production.
First-principles analysis BEFORE the Go choice: would have asked
"Can we tolerate any GC pause, even if rare?" If the answer was "No":
Rust or C++ would have been identified as required.
Production data: revealed the hidden hard requirement.
The LESSON: even a thorough first-principles analysis may miss requirements
that only become visible under production load. Plan for RE-ANALYSIS when
production behavior deviates from requirements.
```

**Level 4 - Senior Engineer:**
First-principles applied to embedded/IoT language selection:
```
Problem: "Firmware for a medical device. Detects heart arrhythmia.
  Triggers alert within 200ms of arrhythmia detection.
  Memory: 128KB RAM. Flash: 1MB.
  Safety: IEC 62304 (medical device software lifecycle).
  No OS: bare-metal (no RTOS)."

Hard requirements:
1. Deterministic execution: no GC, no dynamic memory allocation
   (IEC 62304 Level C: memory allocation not allowed at runtime).
   -> Eliminates: Java, Python, Go, all GC languages.
   -> Viable: C, C++, Rust, Ada.

2. Memory: 128KB RAM. JVM: ~50MB minimum. Python: ~10MB.
   -> Eliminates: JVM, Python, Node.js.
   -> Viable: C, C++, Rust, Ada.

3. Real-time: <200ms deterministic. No GC pauses.
   -> Same filter: C, C++, Rust, Ada.

4. IEC 62304 compliance: must have qualified compiler (DO-178B or similar).
   -> C: qualified compilers (IAR, GCC for specific targets, LLVM-based).
   -> C++: same compilers, but subsets required (MISRA C++).
   -> Rust: NO qualified compiler yet for IEC 62304 Level C as of 2024.
      (Ferrocene project: working toward Rust for safety-critical. Not yet FDA-cleared.)
   -> Ada: GNAT Pro: qualified for DO-178B/IEC 62304. Traditional aerospace/medical.

5. Ecosystem: existing drivers for target MCU (STM32, Nordic nRF).
   -> C/C++: HAL libraries exist (STM32 HAL, Nordic nRF5 SDK).
   -> Rust: embassy-rs (async Rust for embedded): growing ecosystem, not all MCUs.
   -> Ada: Ravenscar (real-time subset), GNAT for ARM: limited MCU drivers.

VIABLE after all hard requirements: C or C++ (with MISRA compliance).
  Ada: viable if FAA-qualified toolchain is the priority.
  Rust: NOT viable today for IEC 62304 Level C (no qualified compiler).

TCO selection between C and C++:
  C: simpler, widely understood in embedded, strict MISRA-C subset.
  C++: more expressive, RAII useful for resource management, MISRA C++ stricter.
  
DECISION: C with MISRA-C subset (most common choice for medical device firmware).
  Note: this decision: derived FROM the requirements. Not from "C is what embedded uses."
  Rust would be the first-principles choice IF a qualified compiler existed for IEC 62304.
  When Ferrocene or similar gets FDA clearance: re-evaluate.
```

**Level 5 - Expert:**
First-principles and the language design spectrum:
```
Expert insight: The "ideal language" thought exercise reveals LANGUAGE DESIGN SPACE.

ANY language represents a point in a multi-dimensional design space:
  Dimension 1: Safety (memory safety, type safety, null safety)
  Dimension 2: Performance (throughput, latency, memory)
  Dimension 3: Expressiveness (lines of code per concept, DSL capability)
  Dimension 4: Simplicity (learning curve, toolchain complexity)
  Dimension 5: Ecosystem (libraries, frameworks, tooling)
  Dimension 6: Concurrency model (shared memory, actor, CSP, async/await)
  Dimension 7: Compilation model (AOT, JIT, interpreted)

LANGUAGE POSITIONS IN THE DESIGN SPACE:
  C:      Safety(low), Performance(max), Expressiveness(med), Simplicity(med)
  C++:    Safety(med), Performance(max), Expressiveness(high), Simplicity(low)
  Rust:   Safety(max), Performance(max), Expressiveness(high), Simplicity(low)
  Go:     Safety(high), Performance(high), Expressiveness(med), Simplicity(max)
  Java:   Safety(high), Performance(high), Expressiveness(high), Simplicity(med)
  Kotlin: Safety(max+null), Performance(high), Expressiveness(max), Simplicity(med)
  Python: Safety(low), Performance(med), Expressiveness(max), Simplicity(max)
  Haskell:Safety(max), Performance(high), Expressiveness(max), Simplicity(low-academic)
  Erlang: Safety(med), Performance(med), Expressiveness(med), Concurrency(max-actor)

FIRST-PRINCIPLES LANGUAGE SELECTION:
  Step 1: Identify which DIMENSIONS have hard requirements for this problem.
    (Performance > threshold? Safety must include memory safety? Concurrency model required?)
  Step 2: In the design space: which languages are positioned in the "valid region"
    (meeting all hard requirements)?
  Step 3: Of those in the valid region: which has lowest TCO (team capability, ecosystem,
    operational cost)?

EXAMPLE: Safety-critical, high-throughput, embedded:
  Safety: MUST include memory safety AND determinism (no GC).
  Performance: MUST have max throughput, < 1ms deterministic latency.
  Simplicity: not a hard requirement (team can learn complex language).
  
  Valid region: {Rust, Ada, C++ with MISRA}
  C: EXCLUDED (memory safety = low, not hard-req compliant for safety-critical).
  Python, Java, Go: EXCLUDED (GC not deterministic for embedded hard real-time).
  
  Rust: best position in the valid region IF no qualified compiler is required.
  Ada: best position IF DO-178B qualified compiler IS required.
  C++ MISRA: viable fallback if Rust is not mature enough for the target platform.
```

---

### ⚙️ How It Works

**THE FIRST-PRINCIPLES LANGUAGE SELECTION CHECKLIST:**

```
┌──────────────────────────────────────────────────────┐
│ PHASE 1: REQUIREMENTS EXTRACTION (1-2 days)          │
│   1. Describe the problem without naming a language. │
│   2. List ALL hard requirements. For each:           │
│      - Latency: p50, p99, p999 requirements.        │
│      - Throughput: msg/s, RPS, connections.         │
│      - Memory: per-instance budget.                 │
│      - Platform: OS, architecture, cloud, embedded. │
│      - Safety: memory-safe? Real-time determinism? │
│      - Ecosystem: what libraries are MANDATORY?     │
│      - Team: what languages does the team know?    │
│        (team capability is a soft requirement)      │
│   3. Mark each: HARD (eliminates if not met) or SOFT.│
│                                                      │
│ PHASE 2: CANDIDATE IDENTIFICATION (1 day)            │
│   1. Start with all viable languages for the domain.│
│   2. Apply HARD requirement filters ONE AT A TIME.  │
│   3. After each filter: list surviving languages.   │
│   4. Stop when 1-3 languages remain (or less).     │
│                                                      │
│ PHASE 3: TCO EVALUATION (2-3 days)                  │
│   For each surviving candidate:                     │
│   1. Team capability: existing expertise? Training? │
│   2. Ecosystem: ALL required libraries verified?   │
│   3. Operational cost: CI/CD, monitoring, on-call?  │
│   4. Longevity: adoption trend, hiring, backing?    │
│                                                      │
│ PHASE 4: PROTOTYPE (1-2 weeks)                      │
│   Build a MINIMAL prototype in the top 1-2 candidates│
│   that verifies the HARD requirements hold.         │
│   Test: does the language actually meet the latency │
│   requirement on YOUR workload? (Not benchmarks.)  │
│                                                      │
│ PHASE 5: DECISION + ADR (1 day)                     │
│   Document: requirements, candidates, filters,      │
│   prototype results, decision, trade-offs, review. │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Assumption-based vs First-Principles Selection**

```bash
# BAD: Assumption-based decision (no first-principles analysis)
# Scenario: "New data processing pipeline needed."
# Decision: "We use Java everywhere. Java."
# Tool: Spring Batch.
# 3 months later: pipeline takes 4 hours for 1GB file.
# Issue: single-threaded Java stream processing. No parallelism.
# 
# The team assumed Java was correct without analyzing:
# - Is CPU-bound or I/O-bound? (CPU-bound: Python with multiprocessing or Go may be better)
# - What is the throughput requirement? (Not specified before implementation)
# - Is Python with Pandas/Polars faster for this ETL? (Likely: specialized for tabular data)
#
# FIRST PRINCIPLES ANALYSIS (should have been done first):
#
# Q1: What is the problem?
#   "Process 1GB CSV files: validate, transform, aggregate, write to DB. Daily batch job."
#
# Q2: Hard requirements?
#   - Complete in < 1 hour (business requirement: run overnight, finish by 06:00).
#   - Memory: < 8GB (server has 16GB, shared with other services).
#   - Output: PostgreSQL DB write.
#
# Q3: What does this require from a language?
#   - Efficient tabular data processing.
#   - Parallel/vectorized column operations (not row-by-row).
#   - PostgreSQL client.
#
# Q4: Viable languages?
#   Python (Polars/DuckDB): columnar operations, vectorized, PARALLEL by default.
#     1GB CSV: Polars processes in ~10s (lazy evaluation, parallel column ops).
#   Java (Spring Batch): row-by-row processing by default. Parallelism manual.
#     1GB CSV row-by-row: 10-60 minutes depending on processing.
#   Go: no native vectorized data processing library (Pandas equivalent: none).
#   SQL (DuckDB): can process CSVs directly as SQL tables. Vectorized engine.
#     DuckDB SELECT from 1GB CSV: seconds.
#
# Q5: Lowest TCO?
#   Python (Polars) + psycopg2: meets hard requirement easily.
#     Team has Python experience. Polars has simple API.
#   DuckDB: fastest (native vectorized SQL). But team: no SQL pipeline experience.
#   Java: slowest. But team knows it. Needs significant optimization to meet 1-hour req.
#
# DECISION: Python with Polars.
#   Fastest to implement. Meets hard requirement (< 1 hour).
#   Existing team Python expertise.
#   NOTE: This is NOT "use Python instead of Java always."
#         It IS "Python (Polars) meets the hard requirement; Java requires significant
#         optimization work (custom parallelism, chunking) to meet the same requirement."
```

**Example 2 - First-Principles Analysis Documentation Template**

```markdown
# First-Principles Language Analysis: [Service Name]

## 1. Problem Description (no language assumptions)
[Describe the problem in pure requirements terms]
Example: "Process payment authorizations in real-time. 10K authorizations/second.
Each authorization: validate card details, apply fraud rules, call payment network,
persist result. SLA: p99 < 100ms."

## 2. Hard Requirements (any failure = language eliminated)

| Requirement | Threshold | Why Hard |
|---|---|---|
| Latency p99 | < 100ms | SLA contract with payment network |
| Throughput | > 10K auth/s | Current peak: 8K/s, 25% headroom required |
| Memory | < 512MB/instance | Kubernetes node constraint |
| PCI-DSS compliance | Required | Payment card data handled |
| PostgreSQL client | Required | Existing DB is PostgreSQL |

## 3. Language Filter

| Language | Latency | Throughput | Memory | PCI | PostgreSQL | RESULT |
|---|---|---|---|---|---|---|
| Java (ZGC) | PASS (ZGC < 1ms) | PASS | PASS (512MB tunable) | PASS | PASS | VIABLE |
| Go | PASS | PASS | PASS | PASS | PASS | VIABLE |
| Python | QUESTIONABLE (GIL) | FAIL (>10K RPS needs async) | PASS | PASS | PASS | ELIMINATED |
| Rust | PASS | PASS | PASS | PASS | PASS | VIABLE |
| Node.js | PASS | QUESTIONABLE | PASS | PASS | PASS | VIABLE |

## 4. TCO Evaluation (viable candidates only)

| Dimension | Java (ZGC) | Go | Rust |
|---|---|---|---|
| Team capability | HIGH (10 Java engineers) | LOW (0 Go) | LOW (0 Rust) |
| Ecosystem | HIGH (Spring Security, Spring Data) | MEDIUM | LOW |
| Ops cost | LOW (existing pipeline) | HIGH (new) | HIGH (new) |
| TCO | LOWEST | HIGH | HIGHEST |

## 5. Prototype Required?
Java meets hard requirements in theory. Prototype: verify ZGC meets p99 < 100ms
under 10K auth/s load with the actual fraud rule computation.
[Yes/No with justification]

## 6. Decision
Java with ZGC and Spring Boot.
Reasoning: meets all hard requirements. Lowest TCO (team expertise, existing ops).
Review in 12 months: if performance requirements tighten to p99 < 10ms: re-evaluate Go or Rust.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "First-principles always leads to a different answer than the team's default language" | First-principles analysis often CONFIRMS the team's default language, but for EXPLICIT reasons rather than habit. If the team uses Java and the first-principles analysis shows Java meets all hard requirements with the lowest TCO: Java is the first-principles answer. The value of the analysis: not finding a different answer, but VALIDATING the assumed answer or finding the cases where it is WRONG. Teams that never do first-principles analysis: never find the cases where their default language is wrong. The cases that matter: service with a hard latency requirement the default language cannot meet; service with a hard memory constraint the default JVM cannot satisfy; service with a mandatory library that only exists in Python. First-principles: catches these. Habit: misses them. |
| "First-principles analysis takes too long to be practical" | For most services: the hard requirement analysis takes 2-4 hours (structured conversation between the engineer, the tech lead, and the ops team lead). The HARD REQUIREMENTS are usually few: latency SLA, throughput target, memory budget, mandatory libraries. The filter process: eliminates candidates quickly. The prototype (if needed): 1-2 weeks. The total cost: 2-3 weeks for a thorough analysis and prototype. The cost of the WRONG language choice: measured in months (migration) or years (living with the wrong choice). The analysis is cheaper. The "it takes too long" objection: usually reflects that the team has never seen a structured first-principles analysis done efficiently. Done well: it is fast. |
| "The requirements always change, so first-principles analysis is wasted effort" | Requirements change. But HARD REQUIREMENTS change slowly. "The system must respond within 100ms" is a hard requirement that comes from a contractual SLA, a user experience standard, or a physics constraint. These change on a timescale of years, not months. The soft requirements (preferred language, team composition) change faster. First-principles analysis: documents the HARD REQUIREMENTS explicitly, making it clear WHEN they change and what the implications are. "Our SLA changed from 100ms to 10ms p99" -> trigger a re-analysis. Without the first-principles documentation: the implication of the SLA change (current Java service may no longer meet the requirement) is invisible until the service starts violating SLA in production. First-principles analysis: makes requirement changes visible as decision triggers. |
| "First-principles means you ignore what others have done (experience)" | First principles does NOT mean ignoring experience. It means: deriving the answer from requirements FIRST, and THEN checking if experience confirms or contradicts the derived answer. "Our first-principles analysis says Go is the right choice for this service. Let's check: do any major companies with similar requirements use Go?" If yes: experience confirms the analysis. If no: investigate why - either the analysis missed something, or those companies are using Go for different reasons. The analogy pattern (what does Google/Facebook/Netflix use?) is useful as a VALIDATION step, not as the PRIMARY REASONING. First-principles + experience cross-check: stronger than either alone. The mistake: using the analogy as the PRIMARY reasoning without checking whether the constraints match. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Missing Hard Requirement (Latency Spike Blind Spot)**

**Symptom:** Language was chosen after analysis. Works well in staging. In production under
peak load: unexpected latency spikes. Investigation reveals: a hard requirement was missed.

**Diagnosis:**
```bash
# PATTERN: Discord's Go -> Rust migration (real-world example)
# Missed hard requirement: "NO GC SPIKES, not just low average GC pause time."
#
# How to prevent this:
# 1. Load test EXPLICITLY for the hard requirement's worst case.
# Go service: run under peak load for 30 minutes.
# Measure: NOT average latency, but p999 (99.9th percentile) and MAX.
# If p999 >> p99: GC spikes likely.

# 2. Java GC spike detection:
jcmd <pid> VM.flags | grep -E "GC|Pause"
# Enable GC logging during load test:
java -Xlog:gc*:file=gc.log:time,uptime -jar service.jar
# After test: look for pause events > 5ms:
grep -E "Pause.*(([5-9][0-9]|[1-9][0-9]{2,})ms)" gc.log

# 3. Go GC spike detection:
# GODEBUG=gccheckmark=1 go run . & 
# Prometheus: go_gc_duration_seconds{quantile="0.999"}
# Grafana: P999 latency during GC trigger events.
# Alert: if p999 GC pause > (SLA_latency * 0.1). 
# Example: SLA = 100ms. Alert if GC pause p999 > 10ms.

# 4. Re-analysis trigger when spikes are detected:
# Q: "Is zero GC pause a hard requirement?"
# If yes: re-apply first-principles filter.
# Go, Java: FAIL (have GC pauses, even if small).
# Rust, C++: PASS (no GC). Must accept new language COST (learning curve).
# Java ZGC: borderline (sub-1ms but NOT zero). May meet the requirement.
# Test ZGC under same load: compare p999 with Go.
```

---

**Security Note:**

First-principles analysis must include security as a dimension:

1. **Memory safety as a hard requirement:**
   ```
   For security-critical applications (authentication, cryptography, parser for untrusted data):
   HARD REQUIREMENT: memory-safe language.
   Reason: OWASP Top 10, CVE history shows that 70% of Microsoft's CVEs (2006-2018)
   were memory safety issues (use-after-free, buffer overflow, integer overflow).
   NSA/CISA guidance (2022): "Use memory-safe languages for new development."
   
   First-principles filter: IF handling untrusted input in a performance-critical path
   -> memory safety is a HARD REQUIREMENT.
   Eliminates: C, C++ (without MISRA/ASAN/sanitizers).
   Viable: Rust, Go, Java, Kotlin, Python, JavaScript (all memory-safe by design).
   ```

2. **Compliance requirements as hard requirements:**
   ```
   PCI-DSS: payment card data handling standards.
     -> No hard requirement on the LANGUAGE, but on the IMPLEMENTATION.
     -> Any language: can meet PCI-DSS if implemented correctly.
   FIPS 140-2: federal encryption standards.
     -> Requires FIPS-validated cryptographic modules.
     -> Java: FIPS-validated JCE providers exist.
     -> Go: FIPS-compliant branch (golang/go/tree/dev.boringcrypto).
     -> Rust: FIPS-compliant AWS-LC-rs (Amazon's fork of BoringSSL bindings).
     -> Check: before choosing a language for government/financial systems.
   ```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Language Evaluation Framework` (CSF-083) - the framework that this first-principles approach feeds into
- `Trade-off Framing` (CSF-088) - the tool for articulating the first-principles analysis

**Builds On This (learn these next):**
- `Paradigm-Agnostic Thinking` (CSF-086) - paradigm selection follows the same first-principles approach
- `Polyglot Architecture Strategy` (CSF-082) - when first-principles selects different languages for different services

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ Q1: WHAT IS THE PROBLEM? (No language assumed.)       │
│     Describe in requirements. Not implementation.    │
├────────────┼─────────────────────────────────────────┤
│ Q2: HARD   │ Latency SLA (p99, p999)?                │
│ REQTS      │ Throughput (msg/s, RPS, connections)?   │
│            │ Memory budget (per instance)?           │
│            │ Mandatory libraries/ecosystem?          │
│            │ Safety (memory-safe? real-time?)?       │
│            │ Platform (OS, MCU, cloud, WASM)?        │
├────────────┼─────────────────────────────────────────┤
│ FILTER     │ Apply hard requirements ONE AT A TIME.  │
│            │ Eliminate any language failing ANY req. │
├────────────┼─────────────────────────────────────────┤
│ TCO        │ Team capability. Ecosystem. Ops cost.  │
│            │ Longevity. Pick lowest TCO viable.      │
├────────────┼─────────────────────────────────────────┤
│ PROTOTYPE  │ Verify hard requirements hold on        │
│            │ YOUR workload. Not benchmarks.          │
├────────────┼─────────────────────────────────────────┤
│ DOCUMENT   │ ADR: requirements, filter, decision.   │
│            │ Review date when SLA or team changes.  │
└────────────┴─────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Start from REQUIREMENTS, not from "what language do we use?" The first question: "What does
   this problem NEED from a language?" Hard requirements (latency SLA, memory budget, mandatory
   libraries) eliminate candidates BEFORE any preference or habit is applied. If the team's
   default language passes all hard requirements: great - use it with explicit reasoning. If it
   fails a hard requirement: find the language that meets it.
2. The "ideal language" thought exercise: "If I had to design a language for this problem, what
   properties would it have?" Identify which existing language most closely matches those properties.
   This avoids both habit (defaulting to the familiar) and cargo cult (copying what famous companies
   use). The answer is derived FROM your specific requirements.
3. Prototype to verify hard requirements on YOUR workload. No benchmark from a blog post replaces
   "does this language meet p99 < 100ms under 10K RPS on our specific business logic?" Discord's Go
   -> Rust migration: could have been prevented by a prototype that measured p999 latency (not p99)
   under peak load. The prototype reveals the hidden hard requirements that desk research misses.

**Interview one-liner:**
"First-principles language selection: 5 questions - (1) What is the problem (no language assumed)? (2) What are the HARD requirements (latency SLA, memory budget, mandatory libraries)? (3) What does the problem require from a language (concurrent model, type safety, ecosystem)? (4) Which languages survive the hard-requirement filter? (5) Of those, which has lowest TCO (team capability, ecosystem, ops cost, longevity)? Prototype to verify. Document as ADR. Prevents both 'use what we know' habit and 'cool new language' cargo cult."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
REQUIREMENTS BEFORE SOLUTIONS. The first-principles approach: is a specific application of
the general engineering principle that PROBLEM DEFINITION precedes SOLUTION SELECTION.

This principle: produces better outcomes across ALL engineering decisions:
- Database selection: "What does the problem REQUIRE from a database?" (ACID? Document model?
  Horizontal scale? Time-series? Graph traversal?) -> Then: filter databases by requirement.
- Architecture pattern: "What does the problem REQUIRE from an architecture?" (Independent
  deployment? Fault isolation? Strong consistency? Low latency?) -> Filter architectures.
- Framework selection: "What does the problem REQUIRE from a framework?" (Convention over
  configuration? Annotation-driven? Reactive? JPA integration?) -> Filter frameworks.
- Team structure: "What does this product REQUIRE from the team structure?" (Conway's Law:
  the system structure follows the team structure.) -> Design the team for the system.

In all cases: starting from REQUIREMENTS and DERIVING the solution produces a decision that
can be EXPLAINED (here is why we chose X: it meets requirements A, B, C that other options
failed) and REVISITED (when requirement A changes, re-evaluate options that previously failed A).

Starting from SOLUTIONS and RETROFITTING requirements: produces decisions that appear
justified but are not (the justification is constructed AFTER the decision to rationalize
a preference or habit). These decisions: cannot be revisited because the original requirements
were never explicit.

---

### 💡 The Surprising Truth

The first-principles approach to language selection was used by the designers of LANGUAGES
THEMSELVES - not just by engineers selecting languages. The designers of Rust asked: "What
is the IDEAL language for systems programming?" Their first principles: memory safety
(no use-after-free), zero runtime overhead (no GC, no runtime exceptions), performance
equivalent to C/C++ (no hidden allocations), fearless concurrency (data races: compile
error). The result: the borrow checker - the defining feature of Rust that makes it unusual.
The borrow checker EXISTS because the requirements DEMANDED it. If the first-principles
analysis had not included "memory safety without GC" as a non-negotiable requirement:
the borrow checker would never have been invented. Similarly: Go's designers asked "What
is the ideal language for large-scale software development at Google?" Their first principles:
fast compilation (Google had 50M+ lines of C++ that took 45 minutes to compile), readability
(multiple teams reading each other's code), simplicity (no feature creep), and good concurrency
(Google's workloads are inherently concurrent). Result: Go's simplicity, fast compiler, and
goroutines - all DERIVED from the first-principles requirements. Understanding WHY a language
has its distinctive features: means understanding the first-principles analysis that the
language designers performed. This is why "Language Design Rationale" (CSF-080) is a
prerequisite for first-principles language selection: you cannot apply first principles
if you do not understand which language was designed for which problem.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[PROBLEM STATEMENT]** Given the scenario "Build a new payment processing service":
   write a first-principles problem statement that includes no language assumptions, lists
   5 hard requirements, and 3 soft requirements. Distinguish clearly between hard and soft.

2. **[FILTER APPLICATION]** Apply the hard requirements filter to: Java (JVM), Go, Python,
   Node.js, and Rust for the following: "Service must respond within p99 < 5ms. Must handle
   50K concurrent WebSocket connections. Memory: < 256MB per instance." Show which are
   eliminated and why.

3. **[IDEAL LANGUAGE EXERCISE]** For an IoT sensor firmware (8KB RAM, no OS, deterministic
   execution, 10-year device lifecycle): perform the "ideal language" thought exercise.
   What properties does the ideal language have? Which existing languages most closely match?
   Which are eliminated by hard requirements?

4. **[DISCORD ANALYSIS]** Reconstruct the first-principles analysis that Discord should have
   done before choosing Go for the read-states service. What hard requirement did they miss?
   What prototype test would have revealed it? What would the first-principles analysis have
   recommended?

5. **[ADR CREATION]** Write a complete first-principles language selection ADR for this
   scenario: "Data analytics pipeline, 500GB data per day, p99 < 5 minutes for full run,
   team of 3 data engineers with Python expertise." Apply the five-question framework,
   filter candidates, document the decision with GAIN/COST/CONSTRAINT structure.

---

### 🧠 Think About This Before We Continue

**Q1.** The first-principles approach: starts from requirements. But requirements themselves
can be wrong or incomplete. What are three ways requirements are commonly wrong, and how
does first-principles analysis help surface those errors?

*Hint: HOW REQUIREMENTS CAN BE WRONG AND HOW FIRST PRINCIPLES HELPS:

ERROR TYPE 1: Requirements are copied from a previous project without validation.
  Example: "p99 < 100ms" was the SLA for the old service. The new service: serves
  different traffic (batch analytics, not real-time API). The < 100ms requirement:
  copied without asking "does this make sense for analytics?"
  
  FIRST-PRINCIPLES HELPS: forces the question "WHY is 100ms required?"
  If the answer is "because the old service had that SLA" -> wrong source.
  First principles: derive the SLA from the USER EXPERIENCE requirement.
  "The user waits for analytics results. What is acceptable wait time?"
  Answer: for a daily report, 2 minutes is acceptable. p99 < 100ms: irrelevant.
  DERIVED REQUIREMENT: "Run completes within 2 minutes per 1GB data."
  This is completely different from "< 100ms." The wrong requirement would have
  led to over-engineering (choosing high-performance runtime unnecessarily).

ERROR TYPE 2: Requirements conflate the PROBLEM with the SOLUTION.
  Example: "The system must use Redis for caching."
  This is a SOLUTION REQUIREMENT (specifying Redis), not a PROBLEM REQUIREMENT.
  The underlying problem requirement: "read latency < 10ms for user session data."
  
  FIRST-PRINCIPLES HELPS: forces the question "What problem is Redis solving?"
  If the problem is "read latency < 10ms": Redis is ONE solution.
  But: Caffeine in-process cache may also solve it (lower latency, lower ops cost).
  By exposing the PROBLEM requirement: first principles enables comparison of solutions.
  The solution requirement (Redis) would have pre-empted the comparison.

ERROR TYPE 3: Requirements omit the SCALE dimension.
  Example: "The service must handle the load." (No number.)
  First-principles: forces "what IS the load?" Before any language analysis.
  "Current: 100 RPS. Projected 12 months: 500 RPS."
  NOW: language analysis makes sense. 500 RPS: trivially met by any language.
  Without the number: engineers over-engineer for imagined million-RPS scale.
  "The service must handle THE LOAD" -> leads to Kafka, Redis, microservices...
  "The service must handle 500 RPS" -> leads to: a single Spring Boot service.
  
  LESSON: First-principles analysis reveals that requirements MUST be numeric
  (where applicable) before language selection is possible. The process:
  forces NUMBER ELICITATION from the requirements. This alone: prevents
  significant over-engineering.*

---

### 🎯 Interview Deep-Dive

**Q1: "Walk me through how you would select a programming language for a new greenfield service."**

*Why they ask:* Tests structured engineering reasoning and decision-making process. Expected for senior and staff engineers.

*Strong answer includes:*
- Framework: 5 questions - (1) describe the problem without language assumptions, (2) identify hard requirements (latency SLA, throughput, memory, ecosystem, safety), (3) what does the problem require from a language, (4) which languages survive the hard-requirement filter, (5) of those, lowest TCO (team capability, ecosystem, ops cost, longevity).
- Hard requirement vs soft requirement distinction: hard = eliminates candidates. Soft = TCO factor.
- Prototype: to verify hard requirements on actual workload, not benchmarks.
- ADR documentation: record the analysis so future team understands the reasoning.
- Example: walk through a real scenario with specific numbers (latency p99, throughput, memory).

**Q2: "Have you ever changed a technology decision after discovering it was wrong? What happened?"**

*Why they ask:* Tests intellectual honesty, learning orientation, and how engineers handle being wrong. Expected for all levels.

*Strong answer includes:*
- Concrete example of a technology decision made without full first-principles analysis.
- What assumption was wrong (the hard requirement that was missed).
- How it was discovered (production behavior, new requirement, profiling result).
- What the corrected decision was.
- What process improvement prevents the same mistake (first-principles analysis, prototype with p999 testing, explicit hard requirement documentation in ADR).
- Connecting to broader lesson: requirements must be explicit and measurable before selection. The missed requirement: typically a HARD requirement that was treated as a soft requirement ("we'll tune JVM to avoid GC pauses" treated as achievable, not tested under production load).
