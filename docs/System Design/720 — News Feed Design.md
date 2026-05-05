---
layout: default
title: "News Feed Design"
parent: "System Design"
nav_order: 720
permalink: /system-design/news-feed-design/
number: "0720"
category: System Design
difficulty: ★★★
depends_on: Fan-Out on Write vs Read, Caching, Ranking Systems
used_by: Social Networks, Content Platforms, Activity Streams
related: Fan-Out on Write vs Read, Read-Heavy vs Write-Heavy Design, Notification System Design
tags:
  - system-design
  - feed
  - social
  - advanced
  - caching
---

# 720 — News Feed Design

⚡ TL;DR — A news feed system collects content from many producers, ranks it for each user, and serves it with low latency at massive read volume. The hard parts are fan-out strategy, ranking freshness, storage growth, and celebrity skew.

| #720            | Category: System Design                               | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Fan-Out on Write vs Read, Caching, Ranking Systems   |                 |
| **Used by:**    | Social Networks, Content Platforms, Activity Streams |                 |
| **Related:**    | Fan-Out on Write vs Read, Read-Heavy vs Write-Heavy Design, Notification System Design | |

---

### 🔥 The Problem This Solves

**ISSUE:**
Each user follows many accounts, but expects a fresh personalized feed in milliseconds.

**SOLUTION:**
Precompute some work, cache heavily, and rank intelligently.

---

### 📘 Textbook Definition

**News Feed Design:** System design problem focused on aggregating, ranking, storing, and serving personalized streams of content updates for users at very large scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Take posts from people I follow, decide which matter most, and return them fast.

**One analogy:**

> A personalized newspaper assembled from thousands of reporters, but printed differently for every reader.

**One insight:**
The serving path is read-heavy, but the write path becomes explosive when one producer has millions of followers.

---

### 🧠 Mental Model

```
producers -> post store -> fanout/ranking pipeline -> feed cache -> user read
```

---

### 📶 Gradual Depth

**Level 1:** Gather posts from followed accounts.

**Level 2:** Choose fan-out on write, read, or hybrid based on follower count.

**Level 3:** Separate candidate generation from ranking and cache top feed pages aggressively.

**Level 4:** News feed design is mostly about controlling write amplification and ranking cost while protecting the hot read path.

---

### ⚙️ How It Works

```
1. User creates post
2. System stores canonical content
3. Fanout layer updates follower feed candidates
4. Ranking service scores candidates
5. Cache top N items per user
6. Client requests next page with cursor

Hybrid rule of thumb:
- normal user: fan-out on write
- celebrity: fan-out on read
```

---

### 💻 Code Example

```python
import heapq


def top_feed_items(candidates, limit=20):
    return heapq.nlargest(limit, candidates, key=lambda item: item["score"])


items = [
    {"id": 1, "score": 0.8},
    {"id": 2, "score": 0.4},
    {"id": 3, "score": 0.95},
]
print(top_feed_items(items, limit=2))
```

---

### ⚖️ Comparison Table

| Concern | Common answer |
| --- | --- |
| Write amplification | hybrid fan-out |
| Read latency | feed cache |
| Personalization | ranking stage |
| Pagination | cursor-based |
| Viral publishers | fan-out on read |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| --- | --- |
| "A feed is just SQL ORDER BY timestamp" | Real feeds require ranking, filtering, and large-scale caching. |
| "One fan-out strategy fits all users" | Celebrity and normal-user workloads differ drastically. |

---

### 🚨 Failure Modes

**Failure Mode 1: Celebrity fan-out storm**

**Symptom:**
One post triggers millions of feed updates and overwhelms caches or queues.

**Prevention:**
Hybrid fan-out strategy and asynchronous propagation.

---

**Failure Mode 2: Stale personalized ranking**

**Symptom:**
Feed cache is fast but relevance is poor because scores are not refreshed.

**Prevention:**
Short-lived cache windows, background reranking, candidate refresh.

---

### 📌 Quick Reference

```
News feed design:
  canonical post store
  candidate generation
  ranking stage
  feed cache
  hybrid fan-out for skewed follower graphs
```

---

### 🧠 Questions

**Q1.** Which should be fresher in your product: ranking quality or latency?

**Q2.** How would you keep a celebrity post from triggering a cache write storm?
