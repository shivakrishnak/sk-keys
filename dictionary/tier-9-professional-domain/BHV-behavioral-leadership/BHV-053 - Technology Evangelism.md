---
version: 2
layout: default
title: "Technology Evangelism"
parent: "Behavioral & Leadership"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /leadership/technology-evangelism/
id: BHV-018
category: Behavioral & Leadership
difficulty: ★★★
depends_on: Technology Roadmap, Communication, Stakeholder Management
used_by: Behavioral & Leadership
related: Stakeholder Management, Engineering Standards Enforcement, Technology Roadmap
tags:
  - advanced
  - bestpractice
  - mental-model
---

# BHV-018 - Technology Evangelism

⚡ **TL;DR -** The deliberate practice of building internal belief and adoption for a technology or engineering approach by combining demonstration, education, champion-building, and strategic narrative - not just technical argumentation.

| Field | Value |
|---|---|
| **Depends on** | Technology Roadmap, Communication, Stakeholder Management |
| **Used by** | Behavioral & Leadership |
| **Related** | Stakeholder Management, Engineering Standards Enforcement, Technology Roadmap |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A senior engineer discovers that migrating to a reactive, event-driven architecture would reduce system latency by 70% and halve infrastructure costs. She writes a detailed technical document, shares it in Slack, presents it at a team meeting. Six months later, nothing has changed. The monolith is still there. Nobody adopted the idea.

**THE BREAKING POINT:** Technical merit alone does not drive adoption in organisations. People resist change not because they are irrational but because they weigh switching costs, risk, learning effort, and political safety. A technically superior solution that lacks a social adoption strategy loses to a good-enough solution that has champions.

**THE INVENTION MOMENT:** Rogers' 1962 *Diffusion of Innovations* theory revealed that every technology spreads through a predictable social curve, not through logical persuasion. Geoffrey Moore's *Crossing the Chasm* applied this to technology products: crossing from early adopters to the early majority requires a fundamentally different strategy. Technology evangelism operationalises these insights inside an organisation.

---

### 📘 Textbook Definition

**Technology Evangelism** is the structured practice of building awareness, credibility, and adoption for a technology, platform, or engineering approach within an organisation through demonstrations, education, relationship-building, and the deliberate cultivation of internal champions who amplify the message organically.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Great technology dies without someone actively building belief in it - evangelism is the social infrastructure for adoption.

> A new road does not produce traffic just by existing. Someone must explain where it goes, demonstrate that it is safe, remove the first few barriers to entry, and get the first drivers to tell their friends about it.

**One insight:** The target audience for evangelism is not the sceptics - it is the "Early Adopters" who can become champions. Once 2–3 credible engineers are using and talking about a technology, it spreads to the Early Majority without further push. The evangelism goal is to create those first champions, not to convince the entire organisation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Technology adoption is a social process, not a logical one.
2. People adopt new technology when they trust the source, see a concrete benefit, and perceive the switching cost as manageable.
3. Demonstrated working examples beat theoretical arguments every time.
4. Early adopters are a lever: convince 2–3 credible internal engineers and they do the rest of the persuasion.

**DERIVED DESIGN:** Rogers' **S-curve of diffusion** defines five adopter segments (Innovators → Early Adopters → Early Majority → Late Majority → Laggards). Effective evangelism targets Early Adopters with high-quality demonstrations and removes the first practical barriers to adoption. The Early Majority adopts when they see peers succeeding, not when they see technical arguments.

**THE TRADE-OFFS:**

**Gain:** Technology adopted more quickly; fewer fragmented independent experiments; organisation benefits from the improvement at scale.

**Cost:** Evangelism takes significant time away from individual delivery; premature evangelism for unproven technology creates adoption of the wrong thing; evangelism without genuine technical substance creates hype cycles that damage credibility.

---

### 🧪 Thought Experiment

**SETUP:** Your team has evaluated three API gateway options. One option is clearly superior on performance, cost, and operational simplicity. You need 12 teams across the organisation to migrate to it.

**WHAT HAPPENS WITHOUT EVANGELISM:** You send an email with benchmarks and a recommendation. Eight teams ignore it. Two teams read it and say "interesting, we'll look at it when we have time." Two teams adopt it but have questions that nobody answers. The remaining ten teams build bespoke solutions over the next year. Your organisation now maintains eleven different API gateway patterns.

**WHAT HAPPENS WITH EVANGELISM:** You pick two teams with sympathetic tech leads (Early Adopters), help them migrate, resolve their practical issues, and document every lesson. You run an internal tech talk showing a real before/after comparison with real numbers from the two teams. The two adopting teams become your champions. Within 6 months, 8 of 12 teams have migrated - not because of your emails but because their peers recommended it.

**THE INSIGHT:** The unit of evangelism is not the technology. It is the success story. Every working example is worth more than a hundred slides of benchmarks.

---

### 🧠 Mental Model / Analogy

> A spark can light a fire - but only if you lay the kindling correctly. The spark is the technology. The kindling is the early adopters, the demos, the documentation, the removed barriers, and the word-of-mouth from the first successful users. Without kindling, the spark dies. With it, the fire spreads on its own.

- Spark → The technology or approach being evangelised
- Kindling → Early adopters, working examples, documentation
- Oxygen → Organisational context: psychological safety, time to learn
- Fire spreading → Organic peer-to-peer adoption by Early Majority
- Blowing directly on a wet log → Sending benchmarks to sceptics

Where this analogy breaks down: unlike fire, technology adoption can reverse - if early adopters have a bad experience, negative word-of-mouth spreads equally fast. Evangelism must include support infrastructure, not just promotion.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):** Technology evangelism is convincing your colleagues to try and adopt a new tool or approach - through showing, not just telling.

**Level 2 - How to use it (junior developer):** Build something real with the technology. Document the experience honestly. Run a 20-minute demo showing the before-and-after. Answer questions. Offer to pair with the first person who wants to try it. Repeat.

**Level 3 - How it works (mid-level engineer):** Map the organisation using Rogers' adoption curve. Identify the 2–3 Early Adopters: engineers who are respected, curious, and willing to try new things. Give them a working example, personal support, and a forum to share results. Host an internal tech talk not to persuade but to show a success story. Remove the first three practical barriers to adoption (documentation gaps, environment setup friction, integration examples). Create a channel (#tech-name) for ongoing questions. Measure adoption at 30/60/90 days.

**Level 4 - Why it was designed this way (senior/staff):** Technology evangelism at the senior/staff level is fundamentally narrative management. Organisations adopt technology that fits the story they tell about themselves. The senior engineer's job is to connect the technology to the organisation's existing identity and strategic direction: "This is how we become the kind of team that ships features in hours, not weeks." The other dimension is **coalition building**: identify which managers have organisational incentives to support the adoption (reduced toil, cost savings, team morale) and give them the language to advocate internally. Every champion in management is worth ten champions at the engineer level in terms of organisational velocity.

---

### ⚙️ How It Works (Mechanism)

**ROGERS' INNOVATION DIFFUSION CURVE:**

```
+-------------------------------------------------------+
|                        ╭─────╮                        |
|                    ╭───╯     ╰───╮                    |
|                ╭───╯             ╰───╮                |
|  Innovators Early    Early     Late    Laggards        |
|   (2.5%)   Adopters  Majority Majority  (16%)          |
|            (13.5%)   (34%)    (34%)                   |
|                                                        |
|  ←── evangelism focus ──►  ← peer diffusion ──►       |
+-------------------------------------------------------+
```

**EVANGELISM TACTICS BY STAGE:**

```
+-------------------------------------------------------+
| Stage             | Tactic                            |
|-------------------|-----------------------------------|
| Awareness         | Tech talks, blog posts, demos     |
| Interest          | Working examples, sandbox envs    |
| Evaluation        | Pair programming, office hours    |
| Trial             | Migration support, docs, FAQ      |
| Adoption          | Success story sharing, metrics    |
| Champion          | Speaker slots, co-authorship      |
+-------------------------------------------------------+
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Technology Identified / Evaluated
      │
      ▼
Internal Proof of Concept Built      ← YOU ARE HERE
      │
      ▼
Identify 2–3 Early Adopter Teams
      │
      ▼
Hands-on Adoption Support (pairing, office hours)
      │
      ▼
Document Lessons Learned + Success Metrics
      │
      ▼
Internal Tech Talk (success story, not sales pitch)
      │
      ▼
Remove Top 3 Barriers to Adoption
      │
      ▼
Early Majority Adopts via Peer Recommendation
      │
      ▼
Official Standard / Recommended Approach Status
```

**FAILURE PATH:** Engineer sends benchmark email to all 12 teams → sceptics respond with objections → debate degrades into opinion thread → no action → original engineer gives up → technology not adopted.

**WHAT CHANGES AT SCALE:** At enterprise scale, evangelism becomes a formal **Developer Relations** or **Platform Engineering** function. Internal tech talks become conference-style "Engineering Open Days." Champions form a **Technology Advisory Group** that formally shapes the technology roadmap.

---

### 💻 Internal Tech Talk Outline (BAD → GOOD)

**BAD - Vendor-style pitch deck:**

```
Slide 1: Title - "Why we should use Technology X"
Slide 2: Vendor logo + feature list
Slide 3: Benchmark graph from vendor website
Slide 4: "Questions?"
```

**GOOD - Story-driven demo-first talk:**

```markdown
# Migrating Team Falcon's API Gateway - What We Learned

## The Problem We Had (2 min)
- Our API gateway was timing out under peak load
- On-call engineers spent 4h/week on gateway incidents
- Configuration required understanding of 3 legacy systems

## What We Tried (3 min)
- We evaluated 3 options (show criteria table)
- We picked Option X - here is why (show decision matrix)

## Live Demo - Before vs After (10 min)
- BEFORE: deploy a config change (show: 25 min, 3 PRs)
- AFTER:  deploy a config change (show: 3 min, 1 PR)
- BEFORE: p99 latency under load (show: 2,400ms)
- AFTER:  p99 latency under load (show: 180ms)

## What Was Hard (3 min)
- Migration of legacy routes took 2 sprints
- Documentation gap for header transformation rules
- We wrote a migration guide: [link]

## How to Try It (2 min)
- Sandbox environment: [link]
- Migration guide: [link]
- Office hours: Thursdays 15:00 on #gateway-migration

## Questions + Honest Tradeoffs Discussion (5 min)
```

---

### ⚖️ Comparison Table

| Approach | Effect | Best For | Risk |
|---|---|---|---|
| **Demo-Driven Evangelism** | Show working solution | Engineers; hands-on learners | Time-intensive to prepare |
| **Written Case Study** | Documented evidence | Async readers; decision makers | Ignored if not promoted |
| **Office Hours** | Removes adoption barriers | Onboarding first adopters | Scales poorly beyond 5 teams |
| **Internal Tech Talk** | Amplifies success stories | Cross-team awareness | Preaches to the converted if not promoted |
| **Champion Network** | Organic peer adoption | Late Majority conversion | Requires careful cultivation |
| **Mandate/Standard** | Forced adoption | Compliance-driven orgs | Resistance; shadow workarounds |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Technical merit wins arguments" | Adoption is social; a good-enough solution with champions beats a superior solution without them |
| "Send the benchmarks and people will decide rationally" | Benchmarks remove technical objections; they do not create adoption motivation |
| "Target the sceptics first" | Target Early Adopters; let their success convert the Early Majority |
| "Evangelism is marketing / hype" | Genuine evangelism requires honest reporting of tradeoffs and failure modes |
| "Once someone adopts it, your job is done" | Post-adoption support during the first 90 days determines whether adoption sticks |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Premature Evangelism**

**Symptom:** Technology is evangelised before it is stable. Early adopters hit critical bugs. Word-of-mouth turns negative. Adoption reverses. Technology is now harder to re-introduce than if it had never been promoted.

**Root Cause:** Evangelism began before a working internal proof of concept validated the technology for the organisation's specific context.

**Diagnostic:**
```
Before starting evangelism, verify:
- Does a working internal PoC exist?
- Have you run it under realistic load?
- Are the top 3 failure modes documented?
If any answer is No → not ready to evangelise.
```

**Fix:** Build an internal PoC for your specific environment. Find one real problem it solves better than the current approach. Document what went wrong during the PoC. Publish this honestly.

**Prevention:** Define "evangelism readiness" criteria: working PoC, documented failure modes, migration guide, known limitations.

---

**Failure Mode 2: Evangelising to the Wrong Audience**

**Symptom:** Evangelism sessions are attended only by already-converted engineers. Sceptics don't attend. Late Majority never hears about it through credible peers.

**Root Cause:** Evangelism was directed at open all-hands or opt-in tech talks, which self-select for Innovators and Early Adopters who are already curious.

**Diagnostic:**
```
Map attendees of tech talks to Rogers' curve:
- Mostly Innovators? → You're preaching to the choir.
- No Late Majority representation? → Peer channels
  are not activated.
```

**Fix:** Identify which managers have reports in the Early and Late Majority. Brief the managers directly. Ask Early Adopter champions to personally invite their peers rather than relying on open invitations.

**Prevention:** Design evangelism activities by adoption segment. Separate "awareness" activities (for all) from "adoption support" activities (for committed trialists).

---

**Failure Mode 3: No Support Infrastructure**

**Symptom:** Teams attempt adoption after a successful demo. They hit configuration questions, migration edge cases, and integration issues. Nobody answers in the #tech-name Slack channel. Teams abandon the migration half-complete, creating a worse state than before.

**Root Cause:** Evangelism created demand without creating supply: no documentation, no migration guide, no owned support channel, no office hours.

**Diagnostic:**
```
For each evangelised technology:
- Is there a migration guide? (yes/no)
- Is there an owned support channel? (yes/no)
- Is there a named owner for adoption questions? (yes/no)
If any No → support infrastructure gap.
```

**Fix:** Before evangelising, create: a one-page quick-start guide, a migration guide for the most common existing setup, a named owner for the support channel, and a weekly office hours slot for the first 90 days.

**Prevention:** Define "support readiness" as a prerequisite for any internal technology promotion activity.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):** Stakeholder Management, Technology Roadmap, Communication

**Builds On This (learn these next):** Engineering Standards Enforcement, Platform Engineering, Inner-Source

**Alternatives / Comparisons:** Engineering Mandate (forced adoption), Proof of Concept Strategy (evaluation before evangelism), Developer Relations (external variant)

---

### 📌 Quick Reference Card

```
+-------------------------------------------------------+
| WHAT IT IS    | Structured practice of building       |
|               | internal adoption for technology      |
| PROBLEM       | Technically superior solutions die    |
|               | without social adoption strategy      |
| KEY INSIGHT   | Target Early Adopters; let their      |
|               | success convert the Early Majority    |
| USE WHEN      | Introducing new platform, tool, or    |
|               | architectural approach across teams   |
| AVOID WHEN    | Technology is not yet proven in your  |
|               | specific internal context             |
| TRADE-OFF     | Adoption speed vs mandate resentment  |
| ONE-LINER     | Build champions, not arguments        |
| NEXT EXPLORE  | Engineering Standards Enforcement     |
+-------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

1. **(System Interaction)** You are evangelising a new observability platform. The current platform vendor has a multi-year contract managed by a VP who championed the original selection. How do you build adoption for the new platform while managing the political sensitivity of implicitly criticising the existing investment?

2. **(Scale)** Your technology has successfully crossed the chasm: Early Adopters and Early Majority are using it. But Late Majority teams are now mandated to adopt it as a standard. How does the evangelism strategy change when you transition from voluntary early adoption to organisation-wide enforcement?

3. **(Design Trade-off)** Evangelism that honestly reports a technology's weaknesses and failure modes is more credible but may reduce adoption speed. Evangelism that emphasises only strengths accelerates initial adoption but creates backlash when teams hit the hidden problems. How do you calibrate the level of critical honesty in evangelism materials?
