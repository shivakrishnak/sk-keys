---
layout: default
title: "Proof of Concept (POC) in Architecture"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /microservices/proof-of-concept-poc-in-architecture/
id: MSV-010
category: Microservices
difficulty: ★★★
depends_on: Technology Migration Strategy, Architecture Decision Record (ADR), Re-platforming vs Re-architecting
used_by: Technology Migration Strategy, Architecture Review, Engineering Strategy
related: Architecture Decision Record (ADR), Technology Migration Strategy, Spike, Prototype, Architecture Review
tags:
  - architecture
  - advanced
  - pattern
  - bestpractice
  - microservices
  - mental-model
---

# MSV-010 — Proof of Concept (POC) in Architecture

⚡ TL;DR — An architectural POC is a time-boxed technical experiment that validates a specific uncertain assumption before committing to full implementation.

| #2284 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Technology Migration Strategy, Architecture Decision Record (ADR), Re-platforming vs Re-architecting | |
| **Used by:** | Technology Migration Strategy, Architecture Review, Engineering Strategy | |
| **Related:** | Architecture Decision Record (ADR), Technology Migration Strategy, Spike, Prototype, Architecture Review | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team commits to re-architecting their monolith to event-driven microservices. Six months in: the Kafka cluster configuration for exactly-once semantics is far more complex than anticipated. Consumer group lag patterns cause unexpected data consistency issues. The team discovers that the event-driven model requires a complete redesign of their error handling strategy — none of which was anticipated. The entire architecture is now at risk. The team cannot ship features; they are firefighting architectural decisions made without validation.

**THE BREAKING POINT:**
Architecture decisions are expensive to reverse. Committing to a technology choice (message broker, database engine, communication pattern) without validating critical assumptions means discovering fundamental problems after months of investment. The cost of discovering a wrong assumption at week 48 is 10× the cost of discovering it at week 2.

**THE INVENTION MOMENT:**
The Proof of Concept (POC) emerged as the discipline of validating the highest-risk assumptions about an architecture before committing to its full implementation. A POC is not a prototype — it is a focused experiment that answers one specific question: "Does this technology/pattern work for our specific requirement?"

---

### 📘 Textbook Definition

A **Proof of Concept (POC) in Architecture** is a time-boxed, scope-limited technical investigation that validates a specific uncertain architectural assumption or technology choice. A POC is not production code — it is intentionally throwaway code that exists to answer a binary question: "Is this approach viable?" A well-designed POC identifies the riskiest assumptions in a proposed architecture, creates a minimal experiment to test each assumption, runs it within a fixed time box (1–2 sprints), and produces a documented recommendation (proceed / pivot / reject) backed by empirical evidence.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A time-boxed experiment that answers "will this work?" before months of investment commit you to the answer.

**One analogy:**
> Before building a bridge across a river, engineers take soil core samples to test whether the riverbed can support the foundations. They don't sink all the foundations and discover the soil is too soft halfway through. The core sample is the POC — targeted, cheap, disposable, answers the critical question before the commitment is made.

**One insight:**
A POC's value is proportional to the specificity of its question. "Does Kafka work?" is a bad POC question. "Can Kafka deliver exactly-once guarantees for our order-processing domain at 5,000 events/second with a consumer group size of 12?" is a good POC question.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A POC tests exactly one high-risk assumption — not the entire architecture.
2. A POC is time-boxed — scope is fixed and the deadline is non-negotiable.
3. A POC produces throwaway code — production quality is not the goal; answering the question is.
4. A POC produces a documented recommendation — conclusions must be recorded, not just experienced.
5. A failed POC is a success — discovering an assumption is wrong before committing to it saves enormous cost.

**DERIVED DESIGN:**
From invariant 1: a POC begins with a **risk register** of architectural assumptions. Rank assumptions by: (a) confidence level that the assumption is correct, and (b) cost if the assumption is wrong. POC highest-risk (lowest confidence × highest cost) assumptions first.

From invariant 3: the discipline is deliberately reducing production-quality temptation. Engineers naturally want to polish code. In a POC context, time spent on error handling, logging, or test coverage is time not spent answering the question.

**THE TRADE-OFFS:**
**Gain:** De-risk architecture decisions before full commitment; empirical evidence replaces speculation; course-correct cheaply; builds team confidence or surfaces blockers early.
**Cost:** POC time does not directly deliver product features; throwaway code creates sunk-cost psychology if not disciplined; POC findings can be dismissed if not documented rigorously; under-scoped POCs miss the critical assumption they were designed to test.

---

### 🧪 Thought Experiment

**SETUP:**
A team is deciding between two database technologies for a high-volume time-series metrics store: A) TimescaleDB (PostgreSQL extension), B) InfluxDB. The POC question: "Which can ingest 500,000 metrics/second with P99 read latency < 50ms for a 90-day window query?"

**WHAT HAPPENS WITHOUT POC:**
Team commits to TimescaleDB based on "PostgreSQL familiarity." 3 months of development later: production load testing reveals TimescaleDB's compression and query performance for their specific access pattern is insufficient at the required scale. InfluxDB would have been the correct choice. Cost of wrong decision: 3 months + migration.

**WHAT HAPPENS WITH POC:**
Week 1: synthetic data generator. Week 2: ingest test at 500k/second for both databases. Week 2: P99 read query measured for 90-day window. Result: InfluxDB meets requirements. TimescaleDB exceeds P99 threshold. Architecture decision made with data. Total POC cost: 2 weeks. Correct technology chosen before any production code written.

**THE INSIGHT:**
The POC answered the specific question that mattered — "which meets our exact performance requirement?" — in 10% of the time a wrong commitment would have cost to discover and fix.

---

### 🧠 Mental Model / Analogy

> An architectural POC is like a recipe tasting session before cooking for 200 guests. Before committing to a menu for a large event, a chef cooks a small-scale version of each dish for a panel of tasters. The panel validates: taste ✓, dietary requirements ✓, preparation time realistic ✓. If a dish fails the tasting, it is replaced before 200 portions are prepared. The tasting session is time-limited, uses a fraction of the ingredients, and the food is consumed (throwaway) — not served to guests.

- "Tasting session" → POC
- "Full event cooking" → full implementation
- "Tasting panel" → technical reviewers evaluating POC results
- "Recipe failing the tasting" → assumption invalidated by POC
- "Replacing the dish" → architectural pivot before full commitment
- "Throwaway food" → throwaway POC code

Where this analogy breaks down: a tasting panel's judgement is subjective. A POC's results must be objective and measurable — not "this feels right" but "P99 latency = 32ms, which meets the ≤50ms requirement."

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A POC is a small experiment you run before deciding to build something big. You're testing whether your plan will work before spending months on it. If the experiment fails, you change your plan. If it succeeds, you proceed with confidence.

**Level 2 — How to use it (junior developer):**
Identify the riskiest assumption in your architecture. Write the minimum code to test that specific assumption. Time-box the work (1–2 sprints). Document the result (what you tested, what you found, your recommendation). Discard the code or clearly label it "POC — NOT FOR PRODUCTION." Use the documented result to make the architecture decision.

**Level 3 — How it works (mid-level engineer):**
Structure a POC in five steps: (1) **Question** — one specific assumption to test. (2) **Success criteria** — what outcome proves the assumption valid? (3) **Scope** — minimum code to test the assumption, nothing more. (4) **Time-box** — fixed sprint(s), scope cut before deadline passes. (5) **Deliverable** — written recommendation with empirical evidence. Common POC subjects: performance at target load, technology integration complexity, library API suitability, cloud service SLA validation, team capability assessment. Typical time-box: 1 sprint for focused technical question, 2 sprints for cross-team integration question.

**Level 4 — Why it was designed this way (senior/staff):**
At the senior/staff level, POCs are a risk management tool embedded in the architecture governance process. The key discipline: linking POCs to Architecture Decision Records (ADRs). Every ADR that involves a technology or pattern choice with significant uncertainty should reference a POC result. This creates an evidence-based architecture decision record rather than an opinion-based one. The organisational pattern for POC governance: a "spike" in agile terminology is a POC for a story-level uncertainty. An architectural POC is a spike at the system design level. Both share the same time-box discipline and throwaway-code principle. The failure mode to avoid: "productionising the POC" — converting POC throwaway code into production code because it's already written. This bypasses all production quality concerns and creates technical debt artifacts with no tests, no error handling, and no operational tooling.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  POC LIFECYCLE                                         │
│                                                        │
│  1. IDENTIFY RISK                                      │
│     Architecture assumption with highest               │
│     uncertainty × impact product                       │
│                                                        │
│  2. DEFINE QUESTION                                    │
│     Specific, binary, measurable:                      │
│     "Can X do Y at Z scale?"                           │
│                                                        │
│  3. DEFINE SUCCESS CRITERIA                            │
│     Numeric threshold: "P99 < 50ms at 5k RPS"         │
│                                                        │
│  4. EXECUTE (time-boxed)                               │
│     Minimal code to answer the question only           │
│     Sprint 1 → Sprint 2 (maximum)                      │
│                                                        │
│  5. DOCUMENT & DECIDE                                  │
│     Written: question, method, result, recommendation  │
│     Decision: proceed / pivot / reject                 │
│     Code: discard or clearly label                     │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Architecture review: event-driven design proposed
  → Risk register: "Kafka exactly-once at our scale?"
    [← YOU ARE HERE: assumption identified]
  → POC defined: measure EOS throughput at 5k events/s
  → Sprint 1: Kafka cluster + producer + consumer
  → Sprint 1: synthetic event generator
  → Sprint 2: load test at 5k/s for 1 hour
  → Result: EOS confirmed at 5k/s, P99 commit = 8ms
  → ADR created: "Kafka chosen (POC: doc/poc-001.md)"
  → Implementation begins with architectural confidence
```

**FAILURE PATH:**
```
POC reveals assumption is wrong:
  → Kafka EOS at 5k/s requires 32 partitions minimum
  → Current infrastructure: max 12 partitions Kafka
  → POC recommendation: REJECT — infrastructure constraint
  → Architecture pivot: consider Pulsar or SQS FIFO
  → New POC for alternative technology
  → Correct decision before production commitment
```

**WHAT CHANGES AT SCALE:**
Single team: informal POC documented in a wiki page. Multiple teams: POC results shared as ADRs consumed by all teams. Organisation-wide: POC library — a catalogue of validated architectural assumptions that prevents teams rediscovering the same answers independently.

---

### 💻 Code Example

**Example 1 — POC: Kafka exactly-once throughput test:**

```java
// POC code — NOT FOR PRODUCTION
// Question: Can Kafka deliver EOS at 5,000 events/sec?
// Success: P99 consumer commit latency < 20ms at 5k/s

public class KafkaEosPocTest {
    // POC: minimal producer + consumer, no error handling
    // (production code requires retry, DLQ, metrics)
    static void runLoadTest() throws Exception {
        KafkaProducer<String, String> producer =
            createTransactionalProducer();

        producer.initTransactions();
        long startMs = System.currentTimeMillis();
        int eventCount = 0;

        // Send 5,000 events and measure commit latency
        for (int i = 0; i < 5000; i++) {
            producer.beginTransaction();
            producer.send(new ProducerRecord<>(
                "poc-topic",
                "key-" + i, "value-" + i
            ));
            // POC measures this time only:
            long commitStart = System.currentTimeMillis();
            producer.commitTransaction();
            long commitMs = System.currentTimeMillis()
                - commitStart;
            latencies.add(commitMs); // record for P99
        }
        // POC deliverable: latencies histogram → P99 value
        System.out.println("P99 commit: "
            + percentile(latencies, 99) + "ms");
    }
}
```

**Example 2 — POC documentation template:**

```markdown
# POC-001: Kafka Exactly-Once Semantics Performance

**Question:** Can Kafka deliver EOS at 5,000 events/second
with P99 producer commit latency < 20ms?

**Date:** 2026-05-06
**Duration:** Sprint 23 (2 weeks)
**Engineers:** [Names]

**Method:**
- Kafka 3.4, 6-broker cluster, 32 partitions
- Transactional producer, isolated consumer group
- Synthetic load: 5,000 ProducerRecord/s for 60 minutes
- Measured: producer.commitTransaction() latency

**Results:**
- P50: 4ms | P95: 12ms | P99: 17ms | Max: 34ms
- Throughput sustained: 5,000 events/s ✓
- No transaction aborts during 1-hour run ✓

**Recommendation:** PROCEED with Kafka EOS
**Architecture Decision:** See ADR-042

**Code location:** /poc/kafka-eos-poc (DISCARD after ADR)
```

---

### ⚖️ Comparison Table

| Activity | Purpose | Code Quality | Output | Duration |
|---|---|---|---|---|
| **POC** | Validate uncertain assumption | Throwaway | Recommendation + evidence | 1–2 sprints |
| **Prototype** | Demonstrate concept/UX | Low | Demo or mock | 1–4 weeks |
| **Spike** | Resolve story-level uncertainty | Throwaway | Time estimate / approach | 1–3 days |
| **MVP** | Validate business value | Production-quality | Shippable product | Weeks–months |
| **Pilot** | Validate in production with real users | Production-quality | Go/no-go decision | Weeks–months |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| POC code can become production code | POC code is deliberately scope-limited: no error handling, no tests, no observability. Using it in production creates immediate technical debt with unknown failure modes |
| A failed POC means failure | A POC that invalidates an assumption is a success — it prevented months of work in the wrong direction at a fraction of the cost |
| POCs are only for new technology | POCs are equally valuable for validating integration complexity, performance assumptions, team capability gaps, and organisational process changes — not just new technology choices |
| One POC validates the entire architecture | A complex architecture may require 3–5 sequential POCs, each validating a different assumption. Running all assumptions through a single POC produces noise, not signal |

---

### 🚨 Failure Modes & Diagnosis

**1. POC Scope Creep — "While We're At It"**

**Symptom:** POC started as a 2-week Kafka performance test. Week 3: team is also building monitoring dashboards, error handling, and a consumer retry framework. POC has become a mini-implementation.

**Root Cause:** Engineers naturally extend scope toward production quality. No explicit scope boundary defined.

**Diagnostic:**
```bash
# Count LOC in POC vs. planned scope:
find poc/ -name "*.java" | xargs wc -l | tail -1
# If > 1,000 LOC for a 2-week POC: scope has expanded
# Check: does any code exceed the POC's stated question?
```

**Fix:** Restate the POC question. Delete any code that doesn't directly answer it. Reset time-box from the question, not the code state.

**Prevention:** Define POC scope as: "minimum code to answer: [specific question]." Any code addition requires justification against the question.

---

**2. POC Results Ignored — Architecture Proceeds Anyway**

**Symptom:** POC showed technology X cannot meet performance requirements. Architecture decision proceeds with X anyway because the team is already committed and has existing expertise.

**Root Cause:** Sunk-cost psychology and political factors override empirical evidence.

**Diagnostic:**
```bash
# Check ADR for POC reference:
grep -l "poc\|proof-of-concept" docs/adrs/
# ADR-042 should reference POC-001
# If ADR makes X decision but POC showed X fails: red flag
```

**Fix:** Treat POC results as mandatory input to ADR. ADR that contradicts POC findings must explicitly acknowledge and justify the contradiction.

**Prevention:** Governance rule: no architecture decision for a high-risk component without a referenced POC result in the ADR.

---

**3. Under-Scoped POC — Wrong Question Answered**

**Symptom:** POC "validated" Elasticsearch for full-text search. But production requires faceted search across 50 fields with real-time index updates. POC tested only basic keyword search against a 1,000-document index. Production: 50M documents, complex queries.

**Root Cause:** POC tested a simplified version of the requirement, not the actual requirement under realistic conditions.

**Diagnostic:**
```bash
# Compare POC data volume vs. production estimate:
cat poc/README.md | grep "dataset size"
# POC: 1,000 docs. Production: 50M docs
# Delta > 100x: POC conditions unrealistic
```

**Fix:** Rerun POC at realistic scale with realistic query complexity. Use data volume and query pattern projections from production usage estimates.

**Prevention:** POC success criteria must reference production-scale requirements, not simplified approximations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Architecture Decision Record (ADR)` — the documentation mechanism that captures POC results as evidence; every significant POC should produce an ADR
- `Technology Migration Strategy` — the broader programme within which POCs validate the riskiest technology assumptions before migration commitment

**Builds On This (learn these next):**
- `Architecture Review` — the governance process that reviews POC results and approves architecture decisions; POC outputs are primary inputs to architecture reviews
- `Engineering Strategy` — the long-term technology direction that POCs help de-risk; a portfolio of POCs validates the feasibility of the engineering strategy before full investment

**Alternatives / Comparisons:**
- `Spike` — an agile story-level time-boxed investigation; the story-level equivalent of an architectural POC
- `Prototype` — a richer demonstration artefact emphasising user experience or concept validation, not assumption testing; often higher quality than a POC and not always throwaway

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Time-boxed experiment that validates one  │
│              │ specific uncertain architectural assumption│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Discovering wrong architecture assumptions │
│ SOLVES       │ after months of implementation commitment  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ A failed POC is a success — discovering   │
│              │ "this won't work" at week 2 beats week 48 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Architecture decision involves uncertain  │
│              │ technology, scale assumption, or new      │
│              │ integration pattern                       │
├──────────────┼───────────────────────="──────────────────┤
│ AVOID WHEN   │ The assumption is already well-validated  │
│              │ by existing evidence or team experience   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ 2-week investment de-risks a 6-month      │
│              │ commitment vs. sprint capacity spent on   │
│              │ throwaway code that doesn't ship features │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build the cheapest possible experiment   │
│              │  that answers the most expensive question."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ADR → Architecture Review →               │
│              │ Technology Migration Strategy → Spike     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has just completed a POC validating that Apache Kafka can handle 10,000 events/second with P99 latency of 8ms using exactly-once semantics. The POC was conducted with a 6-broker cluster, 48 partitions, and a single consumer group. Production will have: 3 consumer groups (notifications, analytics, audit), peak load of 50,000 events/second, and a requirement to not exceed P99 = 20ms. Evaluate whether the POC sufficiently validates the production architecture, identify what the POC does NOT validate, and design additional validation steps.

**Q2.** An architecture team runs a POC to validate a new API gateway technology. The POC takes 3 weeks and concludes the technology is not suitable for the requirement. A senior engineer who championed the technology argues the POC was "too narrow" and the real capability wasn't tested. How do you adjudicate this disagreement? What governance process ensures POC questions and success criteria are agreed before execution, preventing post-hoc invalidation of results?

**Q3.** A company conducts 8 POCs over 6 months during an architecture transformation programme. Each POC generates data but the results are scattered across wikis, code repos, and personal notes. One year later, a new team makes the same technology choice that a POC already invalidated — repeating 3 weeks of investigation. Design a POC knowledge management system that ensures POC results are discoverable, searchable, and integrated into future architecture decisions without creating bureaucratic overhead.

