---
id: SYD-078
title: System Design Interview Framework
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-001
used_by: ""
related: SYD-001, SYD-002, SYD-079, SYD-004, SYD-008
tags:
  - interview
  - framework
  - process
  - communication
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 78
permalink: /technical-mastery/syd/system-design-interview-framework/
---

⚡ TL;DR - System design interviews are structured
45-60 minute conversations. Interviewers assess:
(1) communication - can you articulate trade-offs?
(2) technical depth - do you understand why designs
work? (3) breadth - do you know the tools? (4) judgment -
can you make reasonable decisions with ambiguity?
Framework: Requirements (5 min) → Capacity estimates
(5 min) → High-level design (10-15 min) → Deep dive
(20-25 min) → Summary/trade-offs (5 min). The biggest
mistake: jumping to design without clarifying scope.
The second mistake: not making decisions (saying
"it depends" without follow-up).

| #078 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | System Design Process | |
| **Related:** | System Design Process, Scalability Fundamentals, System Design Interview Preparation Guide, High Availability Design, Load Balancing | |

---

### 🔥 The Problem This Solves

"Design Twitter." You have 45 minutes. Where do you start?
Without a framework: you either talk forever about the
database (and never get to CDN or feed generation), or
you try to cover everything superficially (and nothing
impresses). With a framework: you control the structure,
demonstrate engineering judgment, and guide the
interviewer through the areas where you're strongest.
The framework is not a rigid script - it is a mental
checklist that prevents you from forgetting to scope
the problem, estimate scale, or discuss trade-offs.

---

### 📘 Textbook Definition

**System design interview:** A technical interview format
where the candidate is asked to design a large-scale
system (e.g., "Design YouTube," "Design a URL Shortener").
The interviewer is not looking for a single correct answer
(there isn't one). They are evaluating the candidate's
design process, communication, and judgment.

**Functional requirements:** What the system DOES.
Features the user cares about. "Users can post tweets."
"Users can follow other users."

**Non-functional requirements:** How the system BEHAVES
under constraints. "The system should handle 100M daily
active users." "Latency: < 200ms for feed reads."
"Availability: 99.99%."

**Capacity estimation:** A rough calculation of the
scale the system must handle. Not precise - order of
magnitude is sufficient. Used to justify architectural
decisions (need a CDN? need sharding?).

**Deep dive:** The portion of the interview where the
candidate examines one or two components in detail.
This is where technical depth is assessed. Choose
components where you have the most to say.

**Trade-off discussion:** Explicitly calling out what
a design choice gives you and what it costs you.
"We chose eventual consistency: we gain availability
and write throughput, but reads may return stale data
for up to a few seconds."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Clarify scope → estimate scale → design high-level →
deep dive on hard parts → articulate trade-offs.

**One analogy:**
> System design is like designing a building for a client:
>
> Step 1: Clarify requirements. "Is this a house or
> an office building? How many occupants? Budget?"
> Step 2: Estimate capacity. "100 occupants = need 20
> floors, 4 elevators, fire exits every 20m."
> Step 3: High-level layout. "Ground floor: lobby, cafe.
> Floors 2-15: office space. Floors 16-20: executive."
> Step 4: Deep dive. "Elevator system: 4 lifts, 2
> express (lobby to 16-20), 2 local (1-15). Capacity:
> each lift 15 people, 30-second cycle."
> Step 5: Trade-offs. "Express elevators reduce wait
> time for executives but mean locals are busier. We
> could add a 5th lift if occupancy exceeds 120."
>
> A good architect doesn't start drawing elevator
> shafts without knowing how many floors there are.
> A good system designer doesn't start designing
> schemas without knowing the scale.

**One insight:**
The single most important signal in a system design
interview is "does this person communicate their
reasoning?" An interviewer can follow a design they
disagree with as long as the candidate explains why
they made each choice. An unexplained choice - even
the right choice - leaves the interviewer unsure
whether you knew what you were doing. Always say why.

---

### 🔩 First Principles Explanation

**STEP 1: CLARIFY REQUIREMENTS (5 MINUTES)**

```
MANDATORY before designing anything:

Functional requirements (WHAT does it do?):
  - Which features are in scope for this interview?
  - "Should I focus on write path or read path?"
  - "Should I design the recommendation algorithm
     or just the feed serving?"

Non-functional requirements (HOW does it behave?):
  - Scale: DAU, QPS, data volume.
  - Latency: "What is acceptable latency for reads?"
  - Availability: "Is this 24/7 global or internal?"
  - Consistency: "Is eventual consistency acceptable?"

Clarifying questions (examples for "Design Twitter"):
  1. "How many daily active users are we targeting?"
     → "100M DAU."
  2. "Should I focus on the feed? The tweet write path?
     Or the full system?"
     → "Focus on feed generation and delivery."
  3. "Do we support video or just text?"
     → "Text and images only for this discussion."
  4. "What is the read:write ratio?"
     → "Mostly reads (feeds) vs. writes (new tweets)."

Why this matters:
  "Design Twitter" without clarification = infinite scope.
  You can't design everything in 45 minutes.
  Narrowing to "feed generation for 100M DAU, text only"
  gives you a manageable problem with a definite answer.
  Interviewers expect and appreciate scoping.
```

**STEP 2: CAPACITY ESTIMATION (5 MINUTES)**

```
Back-of-envelope math to justify design decisions.
Order of magnitude only. Not precise.

Example: Twitter-like system, 100M DAU.
  DAU: 100M
  Avg tweets read per user per day: 100
  Avg tweets written per user per day: 0.1 (1 per 10 days)
  
  Read QPS: (100M × 100) / 86,400 ≈ 115,000 QPS
  Write QPS: (100M × 0.1) / 86,400 ≈ 115 QPS
  → Read:Write ratio ≈ 1000:1. Optimize for reads.
  
  Storage (tweets):
  Avg tweet size: 300 bytes (text + metadata)
  10M writes/day × 300 bytes = 3 GB/day
  1 year = ~1 TB. 5 years = ~5 TB. Single node viable
  for storage, but not for QPS.
  
  Media:
  20% of tweets have images. 500KB average.
  2M image tweets/day × 500KB = 1 TB/day.
  5 years = ~1.8 PB. Definitely needs object storage + CDN.

Why estimate?
  "Read QPS of 115,000" → need a CDN and caching.
  "1 TB/day of images" → need object storage (not DB).
  "Text only 5 TB over 5 years" → one DB shard is fine
  for storage, but 115,000 QPS requires read replicas.
  
  Estimates unlock architectural decisions. Without
  them, you're guessing. With them, you're reasoning.
```

**STEP 3: HIGH-LEVEL DESIGN (10-15 MINUTES)**

```
Draw the major components and data flows.
Do NOT go deep on any one component yet.
Cover the full flow end-to-end.

Example: Twitter feed (simplified)

  Client → CDN → Load Balancer
    → API Gateway
      → Feed Service ← Fanout service
                     ← Post DB (Cassandra)
      → Media Service ← Object Storage (S3)
                      ← CDN
    → Auth Service

Data flow: write path
  1. User posts tweet.
  2. API Gateway → Write Service.
  3. Write Service: save tweet to Post DB.
  4. Write Service: push tweet_id to Fanout service.
  5. Fanout service: get user's followers (100K?).
  6. Fanout service: write tweet_id to each follower's
     feed cache (Redis list).

Data flow: read path
  1. User opens app.
  2. API Gateway → Feed Service.
  3. Feed Service: get tweet_ids from Redis (user's feed).
  4. Feed Service: fetch tweet content from Post DB.
  5. Return feed to client.

At this point: interviewer may interrupt with questions.
Good sign: they're engaged. Answer clearly, then continue.
```

**STEP 4: DEEP DIVE (20-25 MINUTES)**

```
Interviewer often guides: "Let's talk more about
how fanout works." OR candidate proposes: "I'd like
to dive into the feed generation, since that's
the most interesting part of this system."

Good deep dive topics (choose based on your knowledge):
  - The hardest scaling problem (fanout for celebrities)
  - The most novel component (CRDT for collaboration)
  - The area with most trade-offs (cache invalidation)
  - A specific failure mode (what if fanout queue backs
    up?)

Depth signals to demonstrate:
  - Know the specific technology: "Redis Sorted Set for
    feed storage - keys are user IDs, values are tweet IDs,
    scores are timestamps."
  - Failure mode: "What if the fanout service lags? The
    fan-out queue builds up. We need a DLQ and an SLA
    alert for queue depth > 1M."
  - Scale behavior: "For users with 10M followers, fan-out
    to 10M Redis keys is too slow (seconds). We use a
    hybrid: pre-compute feeds only for users with <1M
    followers. Celebrity tweets: pull at read time, merge
    with cached feed."

Avoid:
  - Surface-level answers: "We use Kafka for this."
  - No trade-off discussion.
  - No failure consideration.
```

**STEP 5: SUMMARY AND TRADE-OFFS (5 MINUTES)**

```
Wrap up with a brief summary:
  1. What you designed (1-2 sentences).
  2. The key trade-offs made.
  3. What you'd do differently at larger scale.

Example:
  "We designed a Twitter-like feed system for 100M DAU.
  
  Key decisions:
  - Pre-computed fanout (push model): faster reads,
    more complex writes. Trade-off: storage cost and
    fanout latency for celebrity accounts (solved with
    hybrid pull model for high-follower users).
  - Eventual consistency for feeds: a user may see a
    tweet a few seconds late. Acceptable for social feed.
    Would be wrong for payment notifications.
  - Cassandra for Post DB: high write throughput,
    tunable consistency, horizontal scale. Trade-off:
    no complex queries (no JOIN, no ad-hoc filters).
  
  At 10x scale (1B DAU):
  - Multi-region deployment with regional fanout.
  - Cassandra sharded by user geography.
  - Separate CDN per region for media."
```

---

### 🧪 Thought Experiment

**What Interviewers Are Scoring**

Scale up/down signal:
  Junior: can describe a system that works at small scale.
  Mid: understands why designs break at scale and what to add.
  Senior: independently identifies the scale break-points.
  Staff: drives the conversation, proposes alternatives
         and explains why one is better for this specific
         use case.

Red flags:
  - Jumping to implementation ("I'd use a PostgreSQL
    table with these columns...") without discussing scale.
  - No requirements clarification.
  - "It depends" without completing the thought.
  - Being unable to make a decision when asked to.
  - Designing for 1 billion users when the problem said
    100K (over-engineering for the stated scale).

Green flags:
  - "Let me clarify scope before designing."
  - Explicitly stating assumptions: "I'm assuming strong
    consistency is not required here."
  - Knowing the specific trade-offs: "Cassandra vs MySQL:
    Cassandra writes at O(1), MySQL writes at O(log N)
    with B-tree index maintenance. At 100K writes/sec,
    the difference is significant."
  - Guiding the depth: "I can go deeper on the fanout
    algorithm or the caching strategy - which is more
    interesting for this interview?"

---

### 🧠 Mental Model / Analogy

> System design interview = presenting a city's master
> development plan to city council:
>
> The council (interviewer) knows the city (domain)
> well. They're testing whether you can lead the
> planning process.
>
> Good planner: starts by understanding the city's
> goals and constraints. Presents the big picture first.
> Explains trade-offs: "A highway reduces commute time
> but divides the residential area." Invites questions.
> Adjusts based on feedback.
>
> Bad planner: starts designing road widths before
> knowing how many cars the city has. Cannot explain
> why they chose a roundabout vs. traffic lights.
> Says "it depends" when asked to choose.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A system design interview is a 45-60 minute conversation
where you design a large-scale system like Google Maps
or Netflix. The interviewer is not looking for the
one correct answer. They want to see how you think,
communicate, and handle trade-offs with limited information.

**Level 2 - How to use it (junior developer):**
Five steps: (1) Clarify scope and requirements (5 min).
(2) Estimate scale (5 min). (3) Draw high-level design
end-to-end (10-15 min). (4) Deep dive on one hard
component (20-25 min). (5) Summarize trade-offs (5 min).
Always say why you made each choice. Always state
trade-offs explicitly.

**Level 3 - How it works (mid-level engineer):**
Requirements drive architecture. Capacity estimates
justify technology choices: "115K read QPS → need
CDN and read replicas; 115 write QPS → single writer."
High-level design covers all components without depth.
Deep dive shows you know the hard parts: what fails at
scale, how to fix it, what trade-offs result. Trade-off
discussion is the final gate: an engineer who knows why
a design works is more valuable than one who knows what
design to draw.

**Level 4 - Why it was designed this way (senior/staff):**
System design interviews emerged as a proxy for
on-the-job performance for senior engineers because
they test the skills that matter most at senior level:
navigating ambiguity, making decisions with incomplete
information, communicating technical ideas clearly,
understanding trade-offs across components. A senior
engineer's primary daily activity is not writing code
- it's making architectural decisions and communicating
them to stakeholders. The interview simulates exactly
this. Staff-level engineers are additionally evaluated
on whether they can guide a conversation, challenge
assumptions, and propose better alternatives than
what was originally asked.

**Level 5 - Mastery (distinguished engineer):**
The meta-skill in system design interviews: the ability
to recognize which dimension of the problem is the
"hard part" and allocate time accordingly. In most
system design problems, there is one or two components
where the interesting engineering challenges live.
The rest of the system is standard (load balancer,
API gateway, database, cache). Distinguished engineers
identify the hard part immediately ("the interesting
question here is: how do you fan out to 10M followers
without making the write path slow?") and spend 80%
of the interview there. This signals production system
experience: you've seen where these designs fail before,
and you know where to focus.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ INTERVIEW TIME BUDGET (60 minutes)                  │
│                                                      │
│ 0:00-5:00   Requirements Clarification (5 min)    │
│  - Functional: what features?                     │
│  - Non-functional: scale, latency, availability   │
│  - "Which aspect should I focus on?"             │
│                                                      │
│ 5:00-10:00  Capacity Estimation (5 min)           │
│  - DAU, QPS (read and write), storage             │
│  - Justify architectural decisions                │
│                                                      │
│ 10:00-25:00 High-Level Design (15 min)            │
│  - All major components                           │
│  - End-to-end flow (write + read path)           │
│  - No deep dives yet                             │
│                                                      │
│ 25:00-50:00 Deep Dive (25 min)                    │
│  - 1-2 components in detail                      │
│  - Hard scaling problem                          │
│  - Failure modes and fixes                       │
│  - Specific technology choices with reasoning    │
│                                                      │
│ 50:00-55:00 Trade-offs and Summary (5 min)        │
│  - What you'd change at 10x scale                │
│  - Open questions                                │
│                                                      │
│ 55:00-60:00 Buffer / Q&A                          │
│  - Interviewer questions                         │
│  - Anything missed                               │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Requirements gathering template**
```
# SYSTEM DESIGN REQUIREMENTS TEMPLATE
# Use this mental checklist at the start of every
  interview.

## Functional Requirements (WHAT)
1. Core feature: ___________________________________
   ("Users can post tweets of up to 280 characters.")
2. Secondary features (if time allows): ____________
   ("Follow users, likes, retweets - out of scope today.")
3. Feature NOT in scope (explicitly): _______________
   ("Trending topics, search, ads - not in scope.")

## Non-Functional Requirements (HOW)
4. Scale:
   - DAU: ___ M users
   - Read QPS: ___ K/s    (estimate from DAU)
   - Write QPS: ___ K/s   (estimate from DAU)
   - Data volume: ___ GB/day → ___ TB/year

5. Latency:
   - Read: < ___ms (p99)
   - Write: < ___ms (p99)
   - Accept: batch processing / async where?

6. Availability:
   - Target: 99.9% (8h/year downtime) or 99.99%?
   - Consistency vs. availability trade-off?
   - Multi-region?

7. Assumptions to state explicitly:
   - "I'm assuming eventual consistency is acceptable."
   - "I'm assuming a single geographic region."
   - "I'm assuming ~10% of users are active at peak."

## Back-of-Envelope Estimates
   DAU:         100M
   Read:        100M × 100 views/day / 86400 = 115K QPS
   Write:       100M × 0.1 posts/day / 86400 = 115 QPS
   Read/Write:  ~1000:1 (read-heavy, optimize for reads)
   Storage:     115 writes/s × 300B = 34KB/s = 3GB/day
                5 years = ~5.4 TB (text only)
```

**Example 2 - Deep dive question responses**
```
# Interviewer: "How does fanout work for users with
#              10 million followers?"

# BAD RESPONSE (no depth):
"We use Kafka to fan out to followers."

# GOOD RESPONSE (shows depth + trade-off + solution):
"""
For most users (< 1M followers), we use a push-based
fanout: when a tweet is written, the fanout service
reads the follower list and writes the tweet_id to
each follower's Redis feed list.

For users with 10M followers, push fanout is too slow:
10M Redis writes takes ~10 seconds at 1M writes/second.
The write latency is unacceptable and creates backpressure
on the Kafka consumer.

Solution: hybrid push-pull model.
- Users with < 1M followers: push fanout (pre-computed
  feed stored in Redis).
- Users (celebrities) with >= 1M followers: pull at
  read time. When a non-celebrity opens their feed, 
  we return their pre-computed feed from Redis AND
  fetch the latest N tweets from each celebrity they
  follow. Merge the two lists by timestamp.

Trade-off:
  Push-only: O(followers) work per write. Slower writes
  for celebrities. Fast reads.
  Pull-only: O(following) work per read. Slower reads.
  Simpler writes.
  Hybrid: fast reads for all users (most of feed is
  pre-computed). Reduced write amplification for
  celebrities. Added complexity: two code paths.

Implementation:
  At write time: check follower count.
  If > 1M: skip fanout (just store tweet in DB).
  At read time: fetch celebrity tweets from Post DB
  with a Redis cache (short TTL = 30s).
  Merge with pre-computed feed. Return merged + ranked.
"""
```

---

### ⚖️ Comparison Table

| Step | Time | Purpose | Common Mistake |
|---|---|---|---|
| **Requirements** | 5 min | Scope the problem | Skipping, assuming too much |
| **Estimation** | 5 min | Justify architectural choices | Making up precise numbers |
| **High-level** | 15 min | Cover full system end-to-end | Going too deep too early |
| **Deep dive** | 25 min | Show technical depth | Staying too shallow |
| **Trade-offs** | 5 min | Demonstrate judgment | "It works fine" - no trade-offs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| There is a correct answer to system design questions | System design interviews are open-ended. The same system can be designed multiple ways, each with valid trade-offs. The interviewer is evaluating your process and judgment, not whether you chose Kafka over RabbitMQ. Two candidates with completely different high-level designs can both get the job if both can articulate their choices clearly and handle follow-up questions well. |
| Estimation must be accurate | Estimations are order-of-magnitude approximations. Getting within a factor of 10 is fine. Getting within 2x is excellent. The purpose is to reason about scale: "do we need a CDN? do we need sharding?" If your estimate says 100 QPS, you probably don't need Kubernetes. If it says 1M QPS, you definitely do. The math matters less than the conclusion it leads to. |
| More components = better design | Adding unnecessary complexity signals poor judgment. If the problem is a URL shortener for 1,000 QPS, you don't need Kafka, Kubernetes, multi-region failover, or a dedicated service mesh. Proposing a design that would handle 1B QPS for a 1K QPS problem shows you cannot calibrate your solution to the stated requirements. Design for the scale given. Say "if this scaled to X, I would add Y." |

---

### 🚨 Failure Modes & Diagnosis

**Failure: Running Out of Time Before Deep Dive**

**Symptom:**
45 minutes elapsed. The candidate has been discussing
requirements and high-level design the entire time.
The interviewer hasn't seen any technical depth.
"Can you tell me more about the database design?"
"Uh, we'd use a relational database."

**Root Cause:**
Requirements and scope discussion ran too long (>10 min).
High-level design was too detailed too early
(discussed implementation before structure).
No timekeeping awareness.

**Diagnosis and Fix:**
```
Before the interview:
  Practice timekeeping: set a 5-min timer for requirements,
  5-min for estimates, 15-min for high-level.

During the interview:
  After 5 minutes of requirements: explicitly say
  "I think I have enough to start. Let me proceed
  with the design and flag when I make assumptions."
  
  In high-level design: stay at the component level.
  "API → Feed Service → Post DB" is enough for now.
  Do NOT start discussing connection pool sizes
  or caching strategies in the high-level design.
  Save that for deep dive.
  
  Transition: "I've covered the full system at a high
  level. I'd like to go deeper on the feed generation
  algorithm - the part with the most interesting
  engineering challenges here. Is that OK?"
  
  If the interviewer steers: follow their lead.
  They know where they want to probe.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `System Design Process` - core methodology and
  design thinking principles applied in interviews

**Builds On This (learn these next):**
- `Scalability Fundamentals` - the concepts discussed
  in requirements and deep dives (scale, CAP, etc.)
- `System Design Interview Preparation Guide` - how to
  study and practice system design interviews
- `High Availability Design` - common deep-dive area:
  "how do you make this highly available?"
- `Load Balancing` - common component in all high-level
  designs; know the depth here

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1      │ Requirements. Functional + non-functional.│
│ (5 min)     │ Scale, latency, availability, consistency.│
├─────────────┼──────────────────────────────────────────┤
  │
│ STEP 2      │ Capacity. DAU → QPS (read/write). Storage.│
│ (5 min)     │ Order of magnitude. Justify arch choices. │
├─────────────┼──────────────────────────────────────────┤
  │
│ STEP 3      │ High-level. All components, end-to-end.   │
│ (15 min)    │ Write path + read path. No deep dives yet.│
├─────────────┼──────────────────────────────────────────┤
  │
│ STEP 4      │ Deep dive. 1-2 hard components. Failure  │
│ (25 min)    │ modes. Scale behavior. Tech specifics.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ STEP 5      │ Trade-offs. What you'd change at 10x.    │
│ (5 min)     │ Open questions. Summary.                 │
├─────────────┼──────────────────────────────────────────┤
  │
│ GREEN FLAG  │ "Let me clarify scope first."           │
│             │ "Trade-off: X gives us A but costs B."  │
│             │ "At 10x this breaks because..."         │
├─────────────┼──────────────────────────────────────────┤
  │
│ RED FLAG    │ Jump to implementation without scope.   │
│             │ "It depends" without completing thought. │
│             │ No trade-offs mentioned at all.         │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Requirements → Estimate → Design →    │
│             │  Dive → Trade-offs. Always say why."   │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ System Design Interview Preparation Guide│
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Clarify requirements before drawing anything. Ask about
   scale (DAU), latency requirements, and which features
   are in scope. "Design Twitter" is too vague; "Design
   Twitter's feed for 100M DAU, text only, focusing on
   the read path" is actionable.
2. Always say why. Every architectural choice must be
   accompanied by a reason. "Cassandra because it gives
   us high write throughput and horizontal scale" is
   better than "Cassandra." The reason matters more
   than the choice.
3. Budget your time. Requirements: 5 min. Estimates: 5 min.
   High-level: 15 min. Deep dive: 25 min. Trade-offs: 5 min.
   The deep dive is where you're evaluated most heavily.
   Protect that 25 minutes.

**Interview one-liner:**
"Framework: 5 min requirements (functional + non-functional, scale/latency/consistency);
5 min capacity estimation (DAU → read/write QPS, storage); 15 min high-level (all
components, end-to-end write + read path, no depth); 25 min deep dive (hardest
component, failure modes, scale behavior, specific tech choices with reasons);
5 min trade-offs (what you'd change at 10x). Always say why. Green flag: 'let me
clarify scope first.' Red flag: jumping to implementation without scope or saying
'it depends' without completing the thought."
