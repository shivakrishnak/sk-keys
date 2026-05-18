---
id: DPT-048
title: Magic Numbers Anti-Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★☆☆
depends_on: DPT-042
used_by: DPT-063, DPT-064
related: DPT-042, DPT-044, DPT-046
tags:
  - anti-pattern
  - code-quality
  - beginner
  - readability
  - maintainability
  - constants
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 48
permalink: /technical-mastery/design-patterns/magic-numbers/
---

⚡ TL;DR - Magic Numbers are unexplained numeric or string
literals embedded directly in code - the reader cannot
tell what they represent, why they have that specific
value, or whether changing them will break something.

| #48 | Category: Design Patterns | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | DPT-042 | |
| **Used by:** | DPT-063, DPT-064 | |
| **Related:** | DPT-042, DPT-044, DPT-046 | |

---

### 🔥 The Problem This Documents

```java
// What does this code do?
if (user.getScore() > 42) {
    applyDiscount(user, 0.15);
    if (user.getOrderCount() >= 10) {
        user.setTier(3);
    }
}

// The questions that cannot be answered from the code:
// - Why 42? Is this a business threshold or an arbitrary limit?
// - Is 0.15 a 15% discount? In what currency?
// - What is tier 3? How many tiers are there?
// - If the business changes "loyalty threshold" from 42 to 50,
//   how many places need updating? (There might be 5 more.)
```

**The hidden cost:**
Six months later, a developer must change the loyalty
threshold from 42 to 50. They search for "42" in the codebase.
Found in 18 places. Which ones are the loyalty threshold?
Which are unrelated? Some are test data, some are timeouts,
some are the loyalty threshold. Change the wrong 42 and
break something unrelated. The fix: a few hours of archaeology
in code that should have taken 2 minutes.

---

### 📘 Definition

A **Magic Number** is a numeric or string literal that
appears in code without explanation or named context.
The value is "magic" because its meaning is not obvious
from the code itself - the reader must guess, search
documentation, or ask the author.

**Magic Numbers include:**
- Numeric thresholds: `if (count > 100)`
- Sizes: `new byte[1024]`, `new StringBuilder(512)`
- Time intervals: `Thread.sleep(5000)`, `.timeout(30)`
- Status codes: `if (status == 3)`, `response.setStatus(422)`
- Multipliers: `price * 1.23`, `amount * 0.1`
- Array offsets: `parts[2]`, `data[7]`
- Magic string values: `if (type.equals("P"))`, `prefix = "USR_"`

**Magic Numbers are a maintenance anti-pattern**, not
a performance problem. The code works. The cost is paid
by the developer who must modify it later.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Magic Numbers = literals in code that force the reader
to guess what they mean.

**One analogy:**
> Imagine receiving a contract with all names replaced
> by numbers: "Party 1 agrees to pay Party 2 a sum of 42
> to Party 3 within 7 days of 15."
> The contract might be legally valid but completely
> unreadable without a key. Magic Numbers are the same:
> the code works, but only the original author (who has
> the "key" in their head) can safely change it.

**One insight:**
A named constant does three things: (1) gives the value
a name (documentation), (2) provides a single point of
change (maintainability), and (3) allows search by name
not value (discoverability). `MAX_RETRY_ATTEMPTS = 3`
is findable, changeable, and self-documenting. `3` is none
of these things.

---

### 🔩 Root Causes

**HASTE:** "I'll name it later" - later never comes.

**CONTEXT**: The value was obvious to the author at
writing time. "Of course 42 is the loyalty threshold;
we decided that in the sprint meeting." Context is lost
within weeks.

**EVOLUTION:** Values start as one-time magic and get
copied (Copy-Paste Programming) throughout the codebase.
Now changing the value requires a risky find-replace
across 15 files.

**LACK OF DISCIPLINE:** No code review enforcement of
"no naked literals."

---

### 📶 Gradual Depth - Two Levels

**Level 1 - What to do:**
Every literal value that has a business or technical
meaning should be extracted to a named constant (or
enum). The name explains what the value represents.

```java
// Beginner fix: private static final constants
private static final int    LOYALTY_THRESHOLD = 42;
private static final double PREMIUM_DISCOUNT  = 0.15;
private static final int    PREMIUM_TIER      = 3;
private static final int    PREMIUM_MIN_ORDERS = 10;
```

**Level 2 - Production-quality approach:**
Constants that represent domain concepts should live
in domain classes or enums, not scattered as static
fields across service classes. Configuration values
that differ between environments (timeouts, limits,
feature thresholds) should be externalized to
`application.properties` / config server, not hardcoded
even as named constants.

---

### 💻 Code Example

**Example 1 - Magic Numbers (anti-pattern):**

```java
// BAD: Cryptic literals throughout business logic
public void processLoyalty(User user) {
    if (user.getScore() > 42) {
        applyDiscount(user, 0.15);
        if (user.getOrderCount() >= 10) {
            user.setTier(3);
        }
    }
}

public boolean isEligibleForCredit(User user) {
    return user.getScore() > 42     // same 42 again
        && user.getAge() >= 18      // is this the same threshold?
        && user.getCreditScore() > 650;
}

public void scheduleRetry(Task task) {
    scheduler.schedule(task, 30, TimeUnit.SECONDS); // why 30?
    if (task.getAttempts() > 3) {                   // why 3?
        notifyAdmin(task);
    }
}
// Three methods. Five magic numbers. Zero context.
```

**Example 2 - Named constants (better):**

```java
// GOOD: Named constants with single definition points
public class LoyaltyConfig {
    public static final int    LOYALTY_SCORE_THRESHOLD = 42;
    public static final double PREMIUM_DISCOUNT_RATE   = 0.15;
    public static final int    PREMIUM_TIER_LEVEL      = 3;
    public static final int    PREMIUM_MIN_ORDER_COUNT = 10;
    public static final int    MIN_CREDIT_AGE          = 18;
    public static final int    MIN_CREDIT_SCORE        = 650;
}

public class RetryConfig {
    public static final int  MAX_RETRY_ATTEMPTS    = 3;
    public static final long RETRY_DELAY_SECONDS   = 30;
}

// Now the business logic reads like English:
public void processLoyalty(User user) {
    if (user.getScore() > LoyaltyConfig.LOYALTY_SCORE_THRESHOLD) {
        applyDiscount(user, LoyaltyConfig.PREMIUM_DISCOUNT_RATE);
        int minOrders = LoyaltyConfig.PREMIUM_MIN_ORDER_COUNT;
        if (user.getOrderCount() >= minOrders) {
            user.setTier(LoyaltyConfig.PREMIUM_TIER_LEVEL);
        }
    }
}
```

**Example 3 - Externalized configuration (production-quality):**

```java
// BEST: Environment-specific values in config, not code
// application.properties:
// loyalty.score.threshold=42
// loyalty.premium.discount-rate=0.15
// retry.max-attempts=3
// retry.delay-seconds=30

@ConfigurationProperties(prefix = "loyalty")
@Component
public class LoyaltyProperties {
    private int scoreThreshold;      // 42
    private double premiumDiscountRate; // 0.15

    // getters, setters...
}

@Service
public class LoyaltyService {
    @Autowired private LoyaltyProperties loyaltyProps;

    public void processLoyalty(User user) {
        if (user.getScore() > loyaltyProps.getScoreThreshold()) {
            applyDiscount(user,
                loyaltyProps.getPremiumDiscountRate());
        }
    }
}
// Config change (threshold 42 → 50): edit application.properties
// No redeployment needed (with Spring Cloud Config)
// No code change
// No magic anywhere
```

**Example 4 - Enum for status codes (clearer than integers):**

```java
// BAD: integer status codes
if (order.getStatus() == 3) { ... }  // what is 3?
if (order.getStatus() == 5) { ... }  // what is 5?

// GOOD: enum (not just named constants)
public enum OrderStatus {
    PENDING, CONFIRMED, FULFILLED, CANCELLED, REFUNDED
}
// Compile-time safety: cannot set status to 6 (invalid)
// Self-documenting: OrderStatus.FULFILLED is readable
// Exhaustive switch: compiler warns for unhandled cases
if (order.getStatus() == OrderStatus.FULFILLED) { ... }
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Only numeric literals are Magic Numbers | String literals are also Magic Numbers: `if (type.equals("P"))` is as unreadable as `if (type == 3)`. String constants or enums apply: `if (type == PaymentType.PAYPAL)` |
| Named constants are always better than literals | A constant like `private static final int ONE = 1` is worse than `1`. The constant name must ADD meaning. `MAX_CONNECTION_POOL_SIZE = 10` adds meaning; `TEN = 10` does not |
| Comments on literals are equivalent to named constants | `// 42 is the loyalty threshold` + `> 42` is better than naked `> 42`. But the comment is not a single point of change. If `42` appears in 5 places, each needs a comment update. `LOYALTY_THRESHOLD` appears once (in the constant definition) and is referenced from all 5 places |
| Magic Numbers are only a style issue | Magic Numbers create real maintenance risk. When a value changes: find-replace on a number risks changing unrelated literals. A named constant is changed in one place, and all usages update automatically |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Unexplained numeric/string literals in   │
│              │ code with no visible meaning             │
├──────────────┼──────────────────────────────────────────┤
│ COST         │ Unreadable code; risky find-replace when │
│              │ value must change; duplicated literals   │
├──────────────┼──────────────────────────────────────────┤
│ FIX 1        │ Named constants (static final):          │
│              │ LOYALTY_THRESHOLD = 42                   │
├──────────────┼──────────────────────────────────────────┤
│ FIX 2        │ Enums for status codes and types         │
│              │ (compile-time safety + self-documenting) │
├──────────────┼──────────────────────────────────────────┤
│ FIX 3        │ Externalize config values to properties  │
│              │ (change without code deployment)         │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-049: Lava Flow Anti-Pattern          │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Magic Numbers: literals with no name = no context,
   no single change point, no searchability. Named constants
   fix all three.
2. Three levels of fix: (1) named constant for code-owned
   values; (2) enum for categorical types/states; (3)
   externalized config for environment-variable values.
3. The test: could a new developer read your code and
   explain what every literal means without searching
   anywhere? If no: Magic Number. Give it a name.

