---
layout: default
title: "Technical Dictionary"
nav_order: 1
has_children: true
permalink: /
---

# 📚 Technical Dictionary

A comprehensive software engineering dictionary — **1,770 keywords** across **43 categories**, organized in learning-dependency order from foundations to specialized domains.

---

## 🗂️ Categories

### 🔵 Tier 1 — CS & Programming Foundations

| # | Category | Keywords | Range |
|---|---|---|---|
| 1 | [CS Fundamentals](./CS%20Fundamentals/) | 30 | 001–030 |
| 2 | [DSA](./DSA/) | 60 | 031–090 |
| 3 | [Operating Systems](./OS%20&%20Systems/) | 35 | 091–125 |
| 4 | [Linux](./Linux/) | 40 | 126–165 |

### 🔵 Tier 2 — Networking & Protocols

| # | Category | Keywords | Range |
|---|---|---|---|
| 5 | [Networking](./Networking/) | 40 | 166–205 |
| 6 | [HTTP & APIs](./HTTP%20&%20APIs/) | 55 | 206–260 |

### 🔵 Tier 3 — Java & JVM

| # | Category | Keywords | Range |
|---|---|---|---|
| 7 | [Java & JVM Internals](./Java/) | 50 | 261–310 |
| 8 | [Java Language](./Java%20Language/) | 20 | 311–330 |
| 9 | [Java Concurrency](./Java%20Concurrency/) | 40 | 331–370 |

### 🔵 Tier 4 — Spring & Frameworks

| # | Category | Keywords | Range |
|---|---|---|---|
| 10 | [Spring](./Spring/) | 40 | 371–410 |

### 🔵 Tier 5 — Databases

| # | Category | Keywords | Range |
|---|---|---|---|
| 11 | [Databases](./Databases/) | 40 | 411–450 |
| 12 | [NoSQL](./NoSQL/) | 25 | 451–475 |
| 13 | [Caching](./Caching/) | 20 | 476–495 |

### 🔵 Tier 6 — Data Engineering & Big Data

| # | Category | Keywords | Range |
|---|---|---|---|
| 14 | [Data Engineering](./Data%20Engineering/) | 35 | 496–530 |
| 15 | [Big Data & Streaming](./Big%20Data%20&%20Streaming/) | 40 | 531–570 |

### 🔵 Tier 7 — Distributed Systems

| # | Category | Keywords | Range |
|---|---|---|---|
| 16 | [Distributed Systems](./Distributed%20Systems/) | 55 | 571–625 |

### 🔵 Tier 8 — Microservices

| # | Category | Keywords | Range |
|---|---|---|---|
| 17 | [Microservices](./Microservices/) | 55 | 626–680 |

### 🔵 Tier 9 — System & Software Architecture

| # | Category | Keywords | Range |
|---|---|---|---|
| 18 | [System Design](./System%20Design/) | 45 | 681–725 |
| 19 | [Software Architecture](./Software%20Architecture/) | 40 | 726–765 |

### 🔵 Tier 10 — Design Patterns

| # | Category | Keywords | Range |
|---|---|---|---|
| 20 | [Design Patterns](./Design%20Patterns/) | 55 | 766–820 |

### 🔵 Tier 11 — Infrastructure & DevOps

| # | Category | Keywords | Range |
|---|---|---|---|
| 21 | [Containers](./Containers/) | 35 | 821–855 |
| 22 | [Kubernetes](./Kubernetes/) | 60 | 856–915 |
| 23 | [Cloud - AWS](./Cloud%20-%20AWS/) | 40 | 916–955 |
| 24 | [Cloud - Azure](./Cloud%20-%20Azure/) | 35 | 956–990 |
| 25 | [CI-CD](./CI-CD/) | 40 | 991–1030 |
| 26 | [Git](./Git/) | 35 | 1031–1065 |
| 27 | [Maven & Build Tools](./Maven%20&%20Build%20Tools/) | 30 | 1066–1095 |

### 🔵 Tier 12 — Quality & Observability

| # | Category | Keywords | Range |
|---|---|---|---|
| 28 | [Code Quality](./Code%20Quality/) | 35 | 1096–1130 |
| 29 | [Testing](./Testing/) | 45 | 1131–1175 |
| 30 | [Observability](./Observability/) | 35 | 1176–1210 |

### 🔵 Tier 13 — Frontend

| # | Category | Keywords | Range |
|---|---|---|---|
| 31 | [HTML](./HTML/) | 30 | 1211–1240 |
| 32 | [CSS](./CSS/) | 50 | 1241–1290 |
| 33 | [JavaScript](./JavaScript/) | 80 | 1291–1370 |
| 34 | [TypeScript](./TypeScript/) | 50 | 1371–1420 |
| 35 | [React](./React/) | 60 | 1421–1480 |
| 36 | [Node.js](./Node.js/) | 30 | 1481–1510 |
| 37 | [npm](./npm/) | 20 | 1511–1530 |
| 38 | [Webpack & Build Tools](./Webpack%20&%20Build%20Tools/) | 50 | 1531–1580 |

### 🔵 Tier 14 — AI & LLMs

| # | Category | Keywords | Range |
|---|---|---|---|
| 39 | [AI Foundations](./AI%20Foundations/) | 40 | 1581–1620 |
| 40 | [LLMs](./LLMs/) | 40 | 1621–1660 |
| 41 | [RAG & Agents](./RAG%20&%20Agents/) | 40 | 1661–1700 |

### 🔵 Tier 15 — Professional Skills

| # | Category | Keywords | Range |
|---|---|---|---|
| 42 | [Platform Engineering](./Platform%20Engineering/) | 30 | 1701–1730 |
| 43 | [Leadership](./Leadership/) | 40 | 1731–1770 |

---

## 📌 Quick Reference

| Stat | Value |
|---|---|
| Total keywords | 1,770 |
| Total categories | 43 |
| Difficulty ★☆☆ | Foundational |
| Difficulty ★★☆ | Intermediate |
| Difficulty ★★★ | Deep-dive |

---

## ⚡ Add a New Entry

```
1. Create file:  docs/<Category>/NNN — Keyword Name.md
2. Run script:   .\Update-MarkdownFrontmatter.ps1
3. Push:         git add docs/ && git commit -m "Add NNN" && git push
```

See [`GENERATOR_PROMPT.md`](../GENERATOR_PROMPT.md) for the full entry format and [`TECHNICAL_DICTIONARY.md`](../TECHNICAL_DICTIONARY.md) for the master keyword list.
