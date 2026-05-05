---
layout: default
title: "URL Shortener Design"
parent: "System Design"
nav_order: 718
permalink: /system-design/url-shortener-design/
number: "0718"
category: System Design
difficulty: ★★☆
depends_on: Hashing, Database Design, Caching
used_by: Interview Design Problems, Redirect Services, Analytics
related: Rate Limiter Design, Caching, Capacity Planning
tags:
  - system-design
  - design-problem
  - urls
  - caching
  - scalability
---

# 718 — URL Shortener Design

⚡ TL;DR — A URL shortener maps a long URL to a compact unique code and redirects requests quickly. The core design questions are code generation, collision avoidance, redirect latency, abuse prevention, and click analytics.

| #718            | Category: System Design                                 | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Hashing, Database Design, Caching                       |                 |
| **Used by:**    | Interview Design Problems, Redirect Services, Analytics |                 |
| **Related:**    | Rate Limiter Design, Caching, Capacity Planning         |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Long URLs are ugly, hard to share, and hard to track.

**SOLUTION:**
Generate short codes and redirect reliably at high read volume.

---

### 📘 Textbook Definition

**URL Shortener Design:** System design problem involving creation of a service that stores mappings from short identifiers to long URLs and serves low-latency redirects at large scale.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store `abc123 -> https://very.long.url/...` and redirect fast.

**One analogy:**

> A coat-check desk gives you a short ticket number instead of asking you to remember the whole coat description.

**One insight:**
Reads dominate writes heavily, so caching and hot-path simplicity matter more than fancy write logic.

---

### 🧠 Mental Model

```
create:
  long_url -> short_code -> store mapping

redirect:
  short_code -> lookup -> 301/302 redirect
```

---

### 📶 Gradual Depth

**Level 1:** Make a short code that points to a long URL.

**Level 2:** Use Base62 IDs, hash-derived codes, or random tokens plus collision checks.

**Level 3:** Cache hot codes, isolate analytics writes from redirect path, and rate-limit abusive creation traffic.

**Level 4:** Real systems separate redirect service from analytics ingestion because redirect latency must stay minimal.

---

### ⚙️ How It Works

```
Create flow:
1. Validate long URL
2. Generate unique code
3. Persist mapping
4. Return short URL

Redirect flow:
1. Resolve short code from cache or DB
2. Increment click event asynchronously
3. Return redirect response
```

---

### 💻 Code Example

```python
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode(number):
    if number == 0:
        return ALPHABET[0]
    chars = []
    while number:
        number, remainder = divmod(number, 62)
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


print(base62_encode(125))
```

---

### ⚖️ Comparison Table

| Decision        | Option           | Trade-off                             |
| --------------- | ---------------- | ------------------------------------- |
| Code generation | counter + Base62 | simple, predictable                   |
| Code generation | random token     | avoids guessability, collision checks |
| Redirect type   | 301              | cacheable permanent redirect          |
| Redirect type   | 302              | flexible, non-permanent               |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| "This is just a hash map"             | The real design includes abuse control, analytics, hot caching, and code lifecycle. |
| "Analytics must happen synchronously" | They should usually be async off the redirect path.                                 |

---

### 🚨 Failure Modes

**Failure Mode 1: Hot key overload**

**Symptom:**
One viral link dominates cache and backend traffic.

**Prevention:**
Cache, CDN, and lightweight redirect service.

---

**Failure Mode 2: Code collision**

**Symptom:**
Generated short code already exists.

**Prevention:**
Uniqueness constraint and regenerate on collision.

---

### 📌 Quick Reference

```
URL shortener:
  write path: low volume, generate unique code
  read path: high volume, cache heavily
  analytics: async
  abuse: rate limit and domain validation
```

---

### 🧠 Questions

**Q1.** Would you choose sequential Base62 IDs if you do not want users guessing nearby links?

**Q2.** Where should click analytics live so redirects stay fast?
