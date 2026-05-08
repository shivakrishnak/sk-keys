---
layout: default
title: "Technology Roadmap"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /software-architecture/technology-roadmap/
id: SAP-007
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Architecture Decision Record (ADR), Engineering Strategy, Architecture Review, Technical Debt Management
used_by: Engineering Strategy, Architecture Review, Technology Migration Strategy
related: Architecture Decision Record (ADR), Architecture Review, Engineering Strategy, Technical Debt Management
tags:
  - architecture
  - advanced
  - pattern
  - bestpractice
  - mental-model
---

# SAP-007 - Technology Roadmap

⚡ TL;DR - A technology roadmap is a time-phased view of planned technology changes, investments, and retirements - linking engineering decisions to business strategy.

| #2301 | Category: Software Architecture Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Architecture Decision Record (ADR), Engineering Strategy, Architecture Review, Technical Debt Management | |
| **Used by:** | Engineering Strategy, Architecture Review, Technology Migration Strategy | |
| **Related:** | Architecture Decision Record (ADR), Architecture Review, Engineering Strategy, Technical Debt Management | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineering teams make technology choices in an uncoordinated fashion. Team A migrates to Kubernetes, Team B keeps on Docker Swarm, Team C adopts a third container orchestration tool. Database choices diverge across 12 teams. Security upgrade timelines are team-dependent. When a critical vulnerability appears in a library version used by 9 teams, the security team cannot coordinate patching because there is no inventory of technology versions, no planned upgrade timeline, and no cross-team visibility into the current state.

**THE BREAKING POINT:**
Technology fragmentation at scale creates: increased operational overhead (supporting 5 different database engines), security exposure (unknown technology versions), onboarding friction (each team runs a unique stack), and lost economies of scale (no shared investment in common components). The invisible compound interest of uncoordinated technology choices becomes the dominant engineering productivity constraint.

**THE INVENTION MOMENT:**
A technology roadmap provides the shared, time-phased view of where the technology portfolio is heading - which technologies are being adopted, which are stable, which are being phased out, and on what timeline. It replaces uncoordinated local decisions with coordinated direction.

---

### 📘 Textbook Definition

A **Technology Roadmap** is a strategic planning document that defines the organisation's technology portfolio evolution over a planning horizon (typically 1–3 years), specifying: which technologies are in active adoption (invest), which are stable and supported (hold), which are being phased out (retire), and which are deprecated (remove). Technology Roadmaps are commonly visualised as a **technology radar** (ThoughtWorks format: Adopt / Trial / Assess / Hold) or as a timeline lanes diagram. Roadmaps are updated quarterly, reviewed annually, and link technology decisions to business strategic themes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A quarterly-updated view of which technologies the organisation is adopting, holding, trialling, or retiring - and why.

**One analogy:**
> A city's urban planning zoning map. It shows which areas are designated for development (Adopt), which are established residential (Hold), which are earmarked for demolition and redevelopment (Retire), and which are experimental mixed-use zones (Trial). Developers (engineering teams) consult the map before building so individual choices align with the planned city layout. The map evolves as strategic priorities change.

**One insight:**
A technology roadmap's primary function is enabling independent teams to make locally consistent decisions. When teams know the roadmap, they choose from the Adopt list without needing centralised approval for each choice.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The roadmap covers all technology layers: infrastructure, platforms, frameworks, languages, tools.
2. Each technology has an explicit status: Adopt / Trial / Hold / Retire.
3. The roadmap is time-phased - not a static inventory but a direction over time.
4. The business strategy drives technology choices, not the reverse.
5. The roadmap is publicly accessible to all engineers and reviewed collaboratively.

**DERIVED DESIGN:**
From invariant 2: the four statuses create a clear decision guide. **Adopt** = use this for new work; **Trial** = try on low-risk projects; **Hold** = continue using where it exists, but don't start new projects with it; **Retire** = migrate away from, no new usage permitted.

From invariant 4: each roadmap decision traces to a business strategic theme. "Adopt Kubernetes" traces to "reduce operational overhead and increase deployment frequency." Without this linkage, roadmaps become technology wish-lists disconnected from business value.

**THE TRADE-OFFS:**
**Gain:** Cross-team technology alignment; clear onboarding defaults; security posture visibility; economies of scale in shared tooling.
**Cost:** Requires governance discipline to maintain currency; stale roadmaps mislead; Too-prescriptive roadmaps inhibit team autonomy; roadmaps require significant upfront stakeholder alignment.

---

### 🧪 Thought Experiment

**SETUP:**
100 engineers across 20 teams. No technology roadmap. A security vulnerability is found in Log4j (real: Log4Shell, 2021). Security team must patch within 72 hours.

**WHAT HAPPENS WITHOUT Roadmap:**
Security team must first inventory which teams use Log4j, which versions, and in which systems. This takes 48 hours. Contact each team individually. Some teams don't respond. 4 days later: still uncertain which systems are patched. Executive escalation required.

**WHAT HAPPENS WITH Roadmap:**
Roadmap contains technology inventory - Log4j listed as "Hold" (migration to Logback in progress). Technology register shows 14 services using Log4j 2.14.x. Security team contacts 14 teams directly in hour 1. Automated SBOM (Software Bill of Materials) verified against roadmap database. Patch completed across all affected services in 36 hours.

**THE INSIGHT:**
The roadmap's secondary benefit - technology inventory - is often more immediately valuable than the strategic planning function. Knowing what you run enables you to respond to security and operational events with speed.

---

### 🧠 Mental Model / Analogy

> A technology roadmap is like a supermarket's product range review. The buying team periodically reviews: which products are growing sales (Adopt: expand shelf space), which are stable sellers (Hold: maintain), which are declining (Retire: reduce range), and which are new pilots on limited shelves (Trial). The review prevents the supermarket filling up with obsolete products and ensures shelf space is allocated to what customers (engineers) actually want and need.

- "Growing products" → Adopt (invest resources)
- "Stable sellers" → Hold (maintain, no new investment)
- "Declining products" → Retire (wind down, replace)
- "Pilot shelves" → Trial (limited use, evaluate)
- "Supermarket buying team" → architecture / platform team
- "Shelf space" → engineering attention and investment

Where this analogy breaks down: supermarket products are independent; technology choices are often interdependent (choosing Kubernetes implies choosing container images, which implies choosing a container registry strategy). Roadmap decisions cascade in ways product decisions do not.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A technology roadmap is a list of all the tools and technologies your organisation uses, each with a simple status: "use this for new projects," "keep using it but don't start new things with it," "move away from this," or "try this on a testing project." It helps all teams make consistent technology choices without asking for permission every time.

**Level 2 - How to use it (junior developer):**
When starting a new project or making a technology decision, consult the technology radar. If a technology is in "Adopt" → use it. If "Hold" → prefer alternatives from the Adopt list. If "Retire" → schedule migration away. If "Trial" → discuss with your tech lead before adopting. For decisions that don't appear on the radar, propose an addition via the roadmap update process (typically quarterly).

**Level 3 - How it works (mid-level engineer):**
A technology radar is built from inputs: engineering team surveys (what are you using / what would you recommend?), security assessments (any technologies with unacceptable risk profiles?), architecture review board observations (patterns being repeated, patterns being avoided), and business strategic themes (cloud-first implies cloud technologies move to Adopt). The radar is updated quarterly. Technology additions require: a proposer, a business justification, and a reviewer (typically architecture team or principal engineers). The radar is published internally with notes explaining each placement - not just the ring, but the reasoning.

**Level 4 - Why it was designed this way (senior/staff):**
A technology roadmap is a solution to **Conway's Law** applied to tooling: the technology choices organisations make reflect the communication structures of their teams. Without a roadmap, each team's tool choices reflect their local context - not the organisation's shared needs. The roadmap acts as a shared "organisational technical memory" that enables decentralised decision-making within a coherent strategy. The ThoughtWorks Technology Radar popularised this format by making it public - establishing an external benchmark against which organisations can orient their own roadmaps. At senior/staff level, roadmap maintenance is a key deliverable: quarterly radar updates are architecture artefacts, not administrative tasks.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│  TECHNOLOGY RADAR - FOUR QUADRANTS & RINGS             │
│                                                        │
│  Quadrants: Techniques, Platforms, Tools, Languages    │
│                                                        │
│        ADOPT         │         TRIAL                  │
│  (use for new work)  │  (evaluate on small projects)  │
│  ─────────────────── │ ──────────────────────────────  │
│        HOLD          │         RETIRE                  │
│  (stable, no new     │  (migrate away, no new         │
│   adoption)          │   projects)                    │
│                                                        │
│  Update cadence: quarterly                             │
│  Ownership: Architecture team + Principal Engineers    │
│  Access: all engineers (public internal document)      │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Q1 Roadmap update:
  → Architecture team collects inputs:
    [← YOU ARE HERE: quarterly review process]
  → Team survey: "What are you using well? Struggling with?"
  → Security: "Any tech with CVEs or unacceptable risk?"
  → Business strategy: "Cloud-first in H2 2026"
  → Changes drafted: Kubernetes → Adopt (from Trial)
                     Docker Swarm → Retire
                     Kafka → Adopt (from Hold)
  → Changes reviewed by principal engineers
  → Roadmap published + change-log communicated
  → Teams self-service based on updated guidance
```

**FAILURE PATH:**
```
Stale roadmap (not updated for 18 months):
  → Teams consult roadmap → "AWS Lambda in Trial"
  → Lambda now "Adopt" de-facto (20 services use it)
  → New team avoids Lambda (roadmap says Trial)
  → Builds unnecessary custom solution instead
  → Technical debt + rework when roadmap later updated
[Fix: treat roadmap staleness as a governance incident]
```

**WHAT CHANGES AT SCALE:**
5 teams: informal radar maintained in a wiki page. 20 teams: formal quarterly review process, published radar website (ThoughtWorks Radar format). 100 teams: tooling integration (Backstage plugin showing radar status on each service's tech stack page).

---

### 💻 Code Example

**Example 1 - Technology radar entry (YAML):**

```yaml
# technology-radar.yaml
quadrant: platforms
entries:
  - name: Kubernetes
    ring: adopt
    description: |
      Standard container orchestration. All new services
      must be deployed on Kubernetes. Migration from
      Docker Swarm must complete by Q4 2026.
    business_driver: "cloud-native-first strategy"
    date_added: "2025-01-15"
    date_updated: "2026-04-01"

  - name: Docker Swarm
    ring: retire
    description: |
      Replaced by Kubernetes. No new services on Swarm.
      Existing services: migrate to Kubernetes per
      docs/migration/swarm-to-k8s.md by Q4 2026.
    superseded_by: Kubernetes
    date_added: "2022-06-01"
    date_updated: "2025-01-15"

  - name: Apache Kafka
    ring: adopt
    description: |
      Standard event streaming platform. Use for
      event-driven architectures and data pipelines.
    date_added: "2025-04-01"
```

---

### ⚖️ Comparison Table

| Format | Visualisation | Update Cadence | Best For |
|---|---|---|---|
| **ThoughtWorks Radar** | Concentric rings | Quarterly | Engineering teams, public sharing |
| **Timeline Roadmap** | Gantt-style lanes | Monthly | Executive communication |
| **Technology Register** | Spreadsheet | Continuous | Security inventory, governance |
| **ADR-based Roadmap** | Linked ADR index | Per-decision | Small teams, code-centric |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The roadmap dictates every technology choice | The roadmap provides guidance, not mandates (except for Retire). Teams retain autonomy for choices not covered. The roadmap's power is simplifying the decision space, not eliminating judgment |
| Roadmaps are a platform team responsibility | Roadmaps require input from all engineering teams. They fail when maintained exclusively by a central team without practitioner input |
| Roadmaps only cover new technologies | Technology retirement and stabilisation decisions are equally important. A roadmap that only lists "exciting new tech" neglects the majority of an organisation's existing stack |
| Quarterly updates are too frequent | Quarterly updates reflect the pace of technology change. Annual updates lead to roadmaps that are always 6–12 months stale and lose credibility |

---

### 🚨 Failure Modes & Diagnosis

**1. Roadmap Not Consulted**

**Symptom:** Teams make technology choices that conflict with roadmap guidance. New service starts on a Retired technology.

**Root Cause:** Roadmap not visible or not integrated into the decision-making workflow.

**Diagnostic:**
```bash
# Survey: "Did you consult the technology roadmap
# before making your last major technology choice?"
# If <50%: visibility problem
# Check: is roadmap linked from new project templates?
grep -r "technology-radar\|roadmap" \
  docs/templates/ | wc -l
```

**Fix:** Add technology radar link to new project checklist, architecture decision template, and PR review checklist.

**Prevention:** Feature roadmap compliance in engineering onboarding. Include roadmap adherence in architecture review checklist.

---

**2. Roadmap Drift - Reality and Roadmap Diverged**

**Symptom:** Roadmap shows MongoDB as "Hold" but 6 of 8 new services adopted MongoDB in the last quarter. Roadmap lost credibility.

**Root Cause:** Teams found roadmap guidance impractical. No feedback mechanism to update roadmap based on actual adoption patterns.

**Diagnostic:**
```bash
# Compare service tech stacks vs. roadmap status:
# From service catalog or SBOM:
jq '.services[].database' service-catalog.json \
  | sort | uniq -c | sort -rn
# Map each to roadmap ring → identify drift
```

**Fix:** Run a "roadmap reality check" - where is actual adoption diverging from guidance? Update roadmap to reflect reality, or communicate why the original guidance stands more clearly.

**Prevention:** Quarterly roadmap review explicitly compares stated guidance vs. observed adoption trends.

---

**3. Roadmap as Mandate - Team Autonomy Lost**

**Symptom:** Teams feel they cannot use the right tool for their specific problem because it's not on the Adopt list. Innovation slows. Senior engineers frustrated.

**Root Cause:** Roadmap treated as a compliance requirement rather than guidance.

**Diagnostic:**
```bash
# Survey: "Has the technology roadmap blocked a decision
# you believed was correct for your context?"
# If >30% yes: roadmap is being applied as mandate
```

**Fix:** Clarify that roadmap is a "sensible default" framework. Teams can deviate with ADR justification. Add "Exception" process for context-specific deviations.

**Prevention:** Publish roadmap as "the default choice, not the only choice" with documented exception process.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Architecture Decision Record (ADR)` - individual technology decisions captured in ADRs aggregate into the technology roadmap; understanding ADRs provides the granular decision layer beneath the roadmap
- `Technical Debt Management` - the technology roadmap's Retire ring is driven by technical debt analysis; understanding technical debt helps prioritise roadmap retirement decisions

**Builds On This (learn these next):**
- `Architecture Review` - the governance process that validates implementation against roadmap guidance; the roadmap sets the targets, architecture review validates alignment
- `Engineering Strategy` - the roadmap is one output of the engineering strategy; understanding the relationship between strategy and roadmap clarifies how roadmap decisions are derived

**Alternatives / Comparisons:**
- `Engineering Strategy` - the broader strategy from which the roadmap derives its technical themes; strategy is the "why," roadmap is the "what"
- `Architecture Review Board` - the governance body that produces and enforces the technology roadmap

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Time-phased view of technology investment: │
│              │ Adopt / Trial / Hold / Retire             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Technology fragmentation across teams;    │
│ SOLVES       │ uncoordinated lifecycle management        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Roadmaps enable decentralised decisions   │
│              │ within a coherent direction - default    │
│              │ choices without mandates                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple teams, diverse technology choices│
│              │ and a need for cross-team alignment       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small single-team organisations where     │
│              │ overhead exceeds coordination benefit     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Technology alignment + security posture  │
│              │ vs. governance overhead, staleness risk, │
│              │ potential team autonomy reduction         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The map that lets 100 engineers navigate │
│              │  in the same direction independently."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ADR → Architecture Review → Engineering   │
│              │ Strategy → Technology Migration Strategy  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation's technology roadmap lists React as "Adopt" and Angular as "Hold." A team building a new front-end application has 4 senior Angular engineers and 0 React engineers. They propose using Angular for the new application. Evaluate the tension between roadmap guidance and team capability constraints. Design a decision framework that balances roadmap consistency with pragmatic team-capability considerations, including the conditions under which a deviation from the roadmap is justified.

**Q2.** A technology radar lists Log4j as "Hold" (in use, no new projects). A critical Log4Shell-type vulnerability is discovered. The security team needs to patch or replace all usages within 72 hours. However, the technology register shows Log4j is in 34 services owned by 12 different teams. Design the incident response process that leverages the technology roadmap's inventory to coordinate the 72-hour remediation, and explain what additional registry data would accelerate the response.

**Q3.** An organisation's technology roadmap is produced by a central architecture team and published quarterly. An engineer on a product team argues that the radar becomes stale within weeks because the central team is too slow to respond to new technology signals from practitioners. Design an alternative roadmap governance model that incorporates practitioner signals continuously while maintaining quality and consistency, specifying: who contributes, who decides, and how conflicts between central guidance and team signals are resolved.

