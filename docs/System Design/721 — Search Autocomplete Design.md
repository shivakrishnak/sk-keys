---
layout: default
title: "Search Autocomplete Design"
parent: "System Design"
nav_order: 721
permalink: /system-design/search-autocomplete-design/
number: "0721"
category: System Design
difficulty: ★★★
depends_on: Trie, Ranking, Caching
used_by: Search Products, E-Commerce, Typeahead UX
related: News Feed Design, Caching, Rate Limiter Design
tags:
  - system-design
  - search
  - autocomplete
  - advanced
  - trie
---

# 721 — Search Autocomplete Design

⚡ TL;DR — Search autocomplete returns likely query completions while the user is still typing. The hard parts are low latency, relevance ranking, typo tolerance, and updating suggestions from fast-changing query trends.

| #721            | Category: System Design                        | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Trie, Ranking, Caching                         |                 |
| **Used by:**    | Search Products, E-Commerce, Typeahead UX      |                 |
| **Related:**    | News Feed Design, Caching, Rate Limiter Design |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Users type slowly, make spelling mistakes, and expect instant suggestions.

**SOLUTION:**
Pre-index prefixes and rank likely completions under strict latency budgets.

---

### 📘 Textbook Definition

**Search Autocomplete Design:** System design problem focused on building a low-latency service that returns ranked suggestions for partially typed queries using prefix-oriented data structures and popularity signals.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
As the user types `mic`, return likely completions such as `microsoft`, `microwave`, or `microservices` in milliseconds.

**One analogy:**

> A librarian hearing the first few letters of a title and immediately offering the most likely matches from memory.

**One insight:**
Autocomplete is mostly a latency problem hiding inside a ranking problem.

---

### 🧠 Mental Model

```
typed prefix -> prefix index/trie -> candidate set -> ranking -> top N suggestions
```

---

### 📶 Gradual Depth

**Level 1:** Match query prefixes quickly.

**Level 2:** Use trie or prefix index for fast lookup.

**Level 3:** Rank by popularity, recency, locale, and personalization. Cache hot prefixes.

**Level 4:** Large systems often separate offline model building from online serving so suggestion retrieval stays fast.

---

### ⚙️ How It Works

```
1. Build prefix index from historical queries/doc titles
2. Track frequency and trend scores
3. User types prefix
4. Fetch candidate completions for prefix
5. Rank using popularity + freshness + personalization
6. Return top K results
```

---

### 💻 Code Example

```python
def autocomplete(prefix, entries, limit=5):
    matches = [entry for entry in entries if entry.startswith(prefix)]
    return matches[:limit]


queries = ["microservices", "microsoft", "microwave", "migration"]
print(autocomplete("mic", queries))
```

---

### ⚖️ Comparison Table

| Concern       | Typical answer                     |
| ------------- | ---------------------------------- |
| Prefix lookup | trie / prefix index                |
| Ranking       | frequency + recency                |
| Speed         | cache hot prefixes                 |
| Trend updates | streaming counters + batch rebuild |

---

### ⚠️ Common Misconceptions

| Misconception                       | Reality                                                       |
| ----------------------------------- | ------------------------------------------------------------- |
| "Trie alone solves autocomplete"    | Retrieval is only half; ranking quality matters just as much. |
| "Use full search engine query path" | Full-text ranking is often too heavy for every keystroke.     |

---

### 🚨 Failure Modes

**Failure Mode 1: High latency per keystroke**

**Symptom:**
Autocomplete lags behind typing.

**Prevention:**
Prefix caches, precomputed candidates, short payloads.

---

**Failure Mode 2: Irrelevant suggestions dominate**

**Symptom:**
Popular but low-intent queries bury what users actually want.

**Prevention:**
Blended ranking with recency, locale, and personalization.

---

### 📌 Quick Reference

```
Autocomplete design:
  prefix retrieval + ranking + caching
  optimize for per-keystroke latency
  keep candidate generation cheaper than full search
```

---

### 🧠 Questions

**Q1.** Should autocomplete rank by global popularity or user-specific history first?

**Q2.** How do you update trending suggestions without rebuilding the whole index every minute?
