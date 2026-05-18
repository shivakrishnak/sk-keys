---
id: DSA-074
title: ReDoS and Algorithmic Complexity Attacks
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-023
used_by: DSA-077
related: DSA-023, DSA-050
tags:
  - security
  - redos
  - algorithmic-attacks
  - regex
  - dos
  - catastrophic-backtracking
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 74
permalink: /technical-mastery/dsa/redos-complexity-attacks/
---

## TL;DR

ReDoS exploits catastrophic backtracking in regex engines
to cause O(2^n) processing on crafted inputs - a pure
algorithmic DOS attack with no exploits needed, just a
malicious string against a vulnerable regex pattern.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-074 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | security, ReDoS, regex, catastrophic-backtracking |
| **Prerequisites** | DSA-023 |

---

### The Problem This Solves

An attacker submits a specially crafted 50-character string
to your email validation endpoint. Your regex takes 30
seconds to process it, blocking the thread. Submit 10
requests concurrently: your API is unresponsive. No
exploits, no SQL injection - pure algorithmic amplification.
Understanding algorithmic complexity attacks is an OWASP
Top 10 defense requirement.

---

### Textbook Definition

ReDoS (Regular Expression Denial of Service) exploits
catastrophic backtracking in NFA-based regex engines.
When a regex with nested quantifiers fails to match, the
engine may explore exponentially many paths O(2^n).
More broadly, algorithmic complexity attacks identify
operations that perform poorly on adversarially crafted
inputs: hash collision attacks (O(n^2) on hash table),
sort attacks (O(n^2) on quicksort with sorted input).

---

### How It Works

**Catastrophic backtracking explained:**

```
Vulnerable regex: ^(a+)+$
Test string:      "aaaaab" (notice trailing 'b')

The regex engine tries to match "aaaaab" against ^(a+)+$:
  (a)(a)(a)(a)(a) + b fails
  (a)(a)(a)(aa)   + b fails
  (a)(a)(aa)(a)   + b fails
  (a)(a)(aaa)     + b fails
  (a)(aa)(a)(a)   + b fails
  ... exponential combinations!

For "aaaaaaaaaaaaaab" (15 a's + b):
  2^15 = 32,768 attempts → fast
For "aaaaaaaaaaaaaaaaaaaaaab" (22 a's + b):
  2^22 = 4 million attempts → noticeable lag
For "a" * 30 + "b":
  2^30 = 1 billion attempts → ~1 second
```

**Identifying vulnerable regex patterns:**

```
HIGH RISK (catastrophic backtracking possible):
  (a+)+           nested quantifier
  (a|aa)+         alternation inside quantifier
  (a|a?)+         optional alternation
  ([a-zA-Z0-9]+)* grouping with quantifier

SAFE alternatives for email validation:
  BAD:  ^([a-zA-Z0-9]([a-zA-Z0-9_\-\.]*[a-zA-Z0-9])?@...)+$
  GOOD: ^[a-zA-Z0-9][a-zA-Z0-9_\-.]*@[a-zA-Z0-9.-]+\.[a-z]{2,}$
```

**Hash collision attack:**

```java
// HashMap with String keys: hashCode() computes polynomial hash
// Attacker crafts strings with same hashCode():
// "Ba" and "CB" have same hashCode in Java
// All inserted to same bucket → O(n^2) get/put

// ATTACK: Submit 10,000 form fields with
// collision-engineered key names
// → HashMap degrades to O(n^2) per request

// DEFENSE: Java 8+ HashMap uses TreeMap for long chains
// But: explicit randomization of hash seed per JVM
// For production: use LinkedHashMap or explicit size limit
```

**Defend against ReDoS:**

```java
// DEFENSE 1: Timeout on regex operations
ExecutorService exec = Executors.newSingleThreadExecutor();
Future<Boolean> future = exec.submit(() ->
    input.matches(suspiciousRegex)
);
try {
    return future.get(100, TimeUnit.MILLISECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
    throw new ValidationException("Input too complex");
}

// DEFENSE 2: Limit input length BEFORE regex evaluation
if (email.length() > 320) throw new ValidationException("Too long");
// Maximum valid email = 320 chars per RFC 5321

// DEFENSE 3: Use linear-time regex engine
// Java's java.util.regex is NFA-based (vulnerable)
// Alternatives: Google RE2J (always linear time)
// com.google.re2j.Pattern - drop-in replacement
Pattern safePattern = com.google.re2j.Pattern.compile(regex);
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "ReDoS requires a server bug to exploit" | No. Any backtracking regex engine + nested quantifiers + non-matching input = potential ReDoS. It's a design flaw, not a bug |
| "Limiting concurrent requests prevents ReDoS" | ReDoS consumes CPU, not connections; a single request can block one thread for seconds |

---

### Failure Modes & Diagnosis

**Failure: API endpoint periodically slow with no load**
- Cause: Attacker found a regex with catastrophic
  backtracking and is sending crafted inputs
- Diagnosis: Thread dump shows threads stuck in
  `java.util.regex.Pattern.match()` for seconds;
  input strings contain repeating patterns
- Fix: Replace regex with RE2J; add input length limit;
  add regex timeout

---

### Quick Reference Card

| Attack | Mechanism | Defense |
|--------|-----------|---------|
| ReDoS | Catastrophic backtracking | RE2J, input limits, timeout |
| Hash collision | All keys same bucket | Java 8 tree bins, randomize seed |
| Sorted input quicksort | O(n^2) worst case | Randomized pivot, introsort |
| XML bomb | Exponential entity expansion | Disable entity expansion |

---

### The Surprising Truth

Cloudflare suffered a global outage in July 2019 caused
by a ReDoS in a WAF (Web Application Firewall) rule.
A new regex rule was deployed: `(?:(?:\"|'|\]|\}|\\|\d|(?:nan|infinity|true|false|null|undefined|symbol|math)|\`|\-|\+)+[)]*;?((?:\s|-|~|!|\{\}|\|\||\+)*.*(?:.*=.*)))`
Against certain inputs this caused ~100% CPU usage across
all edge nodes worldwide, taking Cloudflare's entire
network offline for 27 minutes. An algorithmic complexity
bug disrupted services for millions of sites globally.

---

### Mastery Checklist

- [ ] Can identify vulnerable regex patterns (nested
      quantifiers, backtracking alternation)
- [ ] Knows Google RE2J as the safe alternative
- [ ] Implements input length limits before regex
- [ ] Can explain hash collision DoS attacks

---

### Interview Deep-Dive

**Q1 (Hard):** Your email validation is causing intermittent
API slowdowns of 10-30 seconds. How do you diagnose and fix?

> Diagnosis: Take thread dump during slowdown. If threads
> are in java.util.regex.Pattern.match() for >100ms,
> this is ReDoS. Record the input that triggers it:
> typically repeating characters followed by an invalid
> character (e.g., "aaa...a@").
> 
> Root cause: The email validation regex likely has nested
> quantifiers like `([a-zA-Z0-9_-]+)+` which causes
> catastrophic backtracking.
> 
> Fix (in order of implementation):
> 1. IMMEDIATE: Add `if (email.length() > 320) reject`
>    before any regex - caps worst case
> 2. SHORT-TERM: Add regex timeout via ExecutorService
> 3. LONG-TERM: Replace java.util.regex with RE2J
>    (linear time, no backtracking)
> 4. VALIDATE: Use Apache Commons Validator for email
>    (tested, RFC-compliant, safe implementation)
