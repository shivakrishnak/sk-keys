---
layout: default
title: "Magic Numbers Anti-Pattern"
parent: "Design Patterns"
nav_order: 803
permalink: /design-patterns/magic-numbers-anti-pattern/
number: "803"
category: Design Patterns
difficulty: ★☆☆
depends_on: "Anti-Patterns Overview, Code Quality, Refactoring"
used_by: "Code review, static analysis, developer onboarding"
tags: #beginner, #anti-patterns, #design-patterns, #code-quality, #readability, #maintainability
---

# 803 — Magic Numbers Anti-Pattern

`#beginner` `#anti-patterns` `#design-patterns` `#code-quality` `#readability` `#maintainability`

⚡ TL;DR — **Magic Numbers** are hard-coded numeric (or string) literals scattered throughout code with no explanation — their meaning only known to the original author — making the code fragile, unmaintainable, and incomprehensible.

| #803            | Category: Design Patterns                          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------- | :-------------- |
| **Depends on:** | Anti-Patterns Overview, Code Quality, Refactoring  |                 |
| **Used by:**    | Code review, static analysis, developer onboarding |                 |

---

### 📘 Textbook Definition

**Magic Numbers Anti-Pattern** (identified in early structured programming literature; formalized in McConnell "Code Complete" and Martin "Clean Code"): the practice of embedding unexplained numeric or string literals directly in source code. The term "magic" denotes that the number appears to have magical significance — it works but nobody can explain why. Examples: `if (status == 503)` (what does 503 mean? Service Unavailable — non-obvious to readers); `Thread.sleep(5000)` (why 5 seconds?); `if (retries < 3)` (why 3?); `maxSize = 1024` (1024 what? bytes? items?). Impact: the meaning is not self-documenting; changing the value requires finding every occurrence; same value with different meanings creates dangerous confusion.

---

### 🟢 Simple Definition (Easy)

`if (code == 404) { return "Not Found"; }` — what is 404? You either know HTTP status codes or you don't. Now imagine 50 of these throughout the code. `if (x == 8 && y == 3)` — what are 8 and 3? Nobody knows. Magic Numbers: numbers in code that require external knowledge or the original author to understand their meaning.

---

### 🔵 Simple Definition (Elaborated)

A payment service: `if (transactionType == 7)` and later `if (transactionType == 7 || transactionType == 12)` and then `if (transactionType != 7 && transactionType != 12 && transactionType != 15)`. What are 7, 12, and 15? The developer who wrote this left 2 years ago. The code works. Nobody can change the logic because nobody knows which transaction types are which. Magic Numbers create knowledge silos: the code only makes sense if you already know its secrets.

---

### 🔩 First Principles Explanation

**Magic Numbers in all their forms and systematic remediation:**

```
MAGIC NUMBER CATEGORIES:

  1. HTTP STATUS CODES:

  // BAD:
  if (response.getStatus() == 503) {
      retryRequest();
  }
  if (response.getStatus() == 200 || response.getStatus() == 201) {
      processSuccess(response);
  }

  // GOOD — named constants (Spring's HttpStatus):
  if (response.getStatus() == HttpStatus.SERVICE_UNAVAILABLE.value()) {
      retryRequest();
  }
  if (response.getStatusCode().is2xxSuccessful()) {
      processSuccess(response);
  }

  2. TIMING VALUES:

  // BAD:
  Thread.sleep(5000);              // 5 seconds? 5 milliseconds? Why 5?
  scheduler.scheduleAtFixedRate(task, 0, 300, TimeUnit.SECONDS);  // Why 300?

  // GOOD — named constants with units in name:
  private static final long RETRY_DELAY_MS = 5_000;
  private static final long SYNC_INTERVAL_SECONDS = 300;

  Thread.sleep(RETRY_DELAY_MS);
  scheduler.scheduleAtFixedRate(task, 0, SYNC_INTERVAL_SECONDS, TimeUnit.SECONDS);

  3. BUSINESS CONSTANTS:

  // BAD:
  if (order.getTotal().compareTo(new BigDecimal("10000")) > 0) {
      requireManagerApproval(order);
  }

  // What is 10000? Dollars? Cents? Percentage? Why that threshold?

  // GOOD — named constant with business context:
  private static final BigDecimal MANAGER_APPROVAL_THRESHOLD_USD = new BigDecimal("10000");

  if (order.getTotal().compareTo(MANAGER_APPROVAL_THRESHOLD_USD) > 0) {
      requireManagerApproval(order);
  }

  4. COLLECTION/BUFFER SIZES:

  // BAD:
  byte[] buffer = new byte[8192];
  List<Order> page = getOrders(0, 100);

  // GOOD:
  private static final int FILE_BUFFER_SIZE_BYTES = 8_192;  // 8 KB
  private static final int DEFAULT_PAGE_SIZE = 100;

  byte[] buffer = new byte[FILE_BUFFER_SIZE_BYTES];
  List<Order> page = getOrders(0, DEFAULT_PAGE_SIZE);

  5. ENUMS (the best form — named AND typed):

  // BAD:
  if (transactionType == 7) { /* refund */ }
  if (transactionType == 12) { /* chargeback */ }
  if (transactionType == 15) { /* partial refund */ }

  // GOOD — enum: named, typed, exhaustive:
  enum TransactionType {
      PURCHASE(1),
      REFUND(7),
      CHARGEBACK(12),
      PARTIAL_REFUND(15),
      VOID(20);

      private final int code;
      TransactionType(int code) { this.code = code; }

      public static TransactionType fromCode(int code) {
          return Arrays.stream(values())
              .filter(t -> t.code == code)
              .findFirst()
              .orElseThrow(() -> new IllegalArgumentException("Unknown transaction type: " + code));
      }
  }

  if (transaction.getType() == TransactionType.REFUND) { /* refund */ }
  // switch pattern (Java 14+):
  String label = switch (transaction.getType()) {
      case PURCHASE      -> "Purchase";
      case REFUND        -> "Refund";
      case CHARGEBACK    -> "Chargeback";
      case PARTIAL_REFUND -> "Partial Refund";
      case VOID          -> "Void";
  };
  // Compiler enforces exhaustiveness — new enum values = compile error if switch is incomplete.

  6. WHERE LITERALS ARE ACCEPTABLE:

  0, 1, -1 in obvious mathematical contexts:
    for (int i = 0; i < list.size(); i++) { }   // 0 as start: clear
    return Collections.emptyList();               // OK
    result += 1;                                  // incrementing: clear

  HTTP 200 in a test assertion:
    assertThat(response.getStatusCode()).isEqualTo(200);   // context: test
    // vs. production code: assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK.value())
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT named constants:

- Faster to type initially — no declaration overhead
- Numbers feel "concrete" and "obvious" to the author

WITH named constants:
→ Self-documenting. Single source of truth. One change propagates everywhere. Reader understands intent. Compiler/IDE can find all usages for a change.

---

### 🧠 Mental Model / Analogy

> A recipe that says "add 3 of the white powder, cook for 27 until it reads 165, rest for 8 minutes." 3 cups? 3 tablespoons? What is "27"? 27 minutes? 27 degrees? 165°F (internal temp for poultry)? 8 minutes on which setting? A professional recipe: "add 3 cups flour; bake at 350°F for 27 minutes until internal temperature reads 165°F; rest for 8 minutes." Magic Numbers = unlabeled recipe measurements. Named constants = professional recipe with labeled units and context.

"3 of the white powder" = `maxRetries = 3` (3 what? why 3?)
"cook for 27 until it reads 165" = `Thread.sleep(27000)` ... `if (temp >= 165)` (27 seconds? ms? 165 what?)
"rest for 8 minutes" = `cache.setExpiry(8)` (8 minutes? hours? why 8?)
"3 cups flour; 350°F; 165°F internal temperature" = `MAX_RETRIES = 3; BAKE_TEMP_F = 350; SAFE_TEMP_F = 165`
"labeled, contextual measurements" = named constants with units in their name

---

### ⚙️ How It Works (Mechanism)

```
STATIC ANALYSIS TOOLS FOR MAGIC NUMBERS:

  PMD rule: MagicNumber
    <!-- in pmd-ruleset.xml: -->
    <rule ref="category/java/errorprone.xml/MagicNumber"/>

  Checkstyle rule: MagicNumber
    <module name="MagicNumber">
        <property name="ignoreNumbers" value="-1, 0, 1, 2"/>
    </module>

  SonarQube: rule squid:S109 (Magic numbers should not be used)

  IntelliJ IDEA: Inspection "Constant value can be extracted"

  REFACTORING WORKFLOW:
  1. Static analysis scan → list of magic numbers
  2. For each: determine business context (what does this number MEAN?)
  3. Name it with context: RETRY_MAX, TIMEOUT_MS, APPROVAL_THRESHOLD_USD
  4. Extract to constant (Java: private static final)
  5. Or extract to enum if multiple values represent a type
  6. Or extract to configuration (application.properties) if value may change per environment
```

---

### 🔄 How It Connects (Mini-Map)

```
Unexplained literals scattered through code → fragile, unreadable, unmaintainable
        │
        ▼
Magic Numbers Anti-Pattern ◄──── (you are here)
(hard-coded literals; no self-documentation; single-point-of-truth violation)
        │
        ├── Refactoring: Extract Constant, Extract Enum are the direct fixes
        ├── Code Quality: Magic Numbers are a leading code smell indicator
        ├── Anti-Patterns Overview: Magic Numbers in the catalog
        └── Cargo Cult Programming: Magic Numbers often come from copied code
```

---

### 💻 Code Example

```java
// BEFORE — magic numbers throughout a payment processor:
public ProcessingResult process(Order order, int paymentMethod) {
    if (order.getTotal().doubleValue() > 50000.0) {
        return ProcessingResult.DECLINED;
    }

    if (paymentMethod == 1 || paymentMethod == 2) {
        if (order.getTotal().doubleValue() < 0.50) {
            return ProcessingResult.DECLINED;   // what is 0.50?
        }
    }

    if (paymentMethod == 3) {
        if (order.getTotal().doubleValue() > 2000.0) {
            return ProcessingResult.DECLINED;   // what is 2000 for method 3?
        }
    }

    int attempts = 0;
    while (attempts < 3) {                     // why 3?
        try {
            gateway.charge(order, paymentMethod);
            return ProcessingResult.SUCCESS;
        } catch (TransientException e) {
            attempts++;
            Thread.sleep(1000);                // why 1000?
        }
    }
    return ProcessingResult.FAILED;
}

// AFTER — all magic numbers replaced with named constants and enums:
// Constants (or load from config):
private static final BigDecimal MAX_SINGLE_TRANSACTION_USD = new BigDecimal("50000.00");
private static final BigDecimal CARD_MIN_TRANSACTION_USD   = new BigDecimal("0.50");
private static final BigDecimal DIGITAL_WALLET_MAX_USD     = new BigDecimal("2000.00");
private static final int        MAX_RETRY_ATTEMPTS         = 3;
private static final long       RETRY_BACKOFF_MS           = 1_000;

enum PaymentMethod {
    VISA(1), MASTERCARD(2), DIGITAL_WALLET(3);
    final int code;
    PaymentMethod(int code) { this.code = code; }
}

public ProcessingResult process(Order order, PaymentMethod method) {
    if (order.getTotal().compareTo(MAX_SINGLE_TRANSACTION_USD) > 0) {
        return ProcessingResult.DECLINED;
    }

    if (method == PaymentMethod.VISA || method == PaymentMethod.MASTERCARD) {
        if (order.getTotal().compareTo(CARD_MIN_TRANSACTION_USD) < 0) {
            return ProcessingResult.DECLINED;
        }
    }

    if (method == PaymentMethod.DIGITAL_WALLET) {
        if (order.getTotal().compareTo(DIGITAL_WALLET_MAX_USD) > 0) {
            return ProcessingResult.DECLINED;
        }
    }

    int attempts = 0;
    while (attempts < MAX_RETRY_ATTEMPTS) {
        try {
            gateway.charge(order, method.code);
            return ProcessingResult.SUCCESS;
        } catch (TransientException e) {
            attempts++;
            Thread.sleep(RETRY_BACKOFF_MS);
        }
    }
    return ProcessingResult.FAILED;
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0, 1, and 2 are always magic numbers                 | Common values like 0 (initial index, empty), 1 (increment), and -1 (not found) in obvious mathematical contexts are not magic numbers — their meaning is universally understood by context. `for (int i = 0; ...)` is not a magic number. `return -1; // not found` in a linear search is not a magic number. PMD's MagicNumber rule has an `ignoreNumbers` property defaulting to `−1, 0, 1, 2` for this reason. |
| Named constants solve the problem entirely           | Named constants solve readability and single-source-of-truth. But if the value can vary per environment (production vs. staging limits, configurable timeouts), it should be in configuration (`application.properties` / environment variables), not a hard-coded constant. Constants are for values that are truly invariant; environment-specific values belong in configuration.                              |
| Magic strings (non-numeric) are not the same pattern | "Magic strings" (hard-coded string literals like `"admin"`, `"ROLE_MANAGER"`, `"USD"`) are exactly the same anti-pattern with the same remediation. Spelled-out literals like `"application/json"` repeated across 20 files have the same fragility: change one and you must find and update all. `MediaType.APPLICATION_JSON_VALUE` is the named constant equivalent.                                            |

---

### 🔥 Pitfalls in Production

**Same magic number with different meanings in different contexts causing a silent bug:**

```java
// ANTI-PATTERN — two uses of "1" with different meanings:
class OrderService {
    public boolean isPriority(Order order) {
        return order.getCustomerTier() == 1;   // "1" means GOLD tier
    }

    public boolean isFreeShipping(Order order) {
        return order.getShippingMethod() == 1;  // "1" means STANDARD shipping
    }
}

class NotificationService {
    public void notify(Order order) {
        if (order.getStatus() == 1) {           // "1" means CONFIRMED status
            sendConfirmationEmail(order);
        }
    }
}

// Developer wants "priority" orders to get free shipping.
// Reads: isPriority checks == 1, isFreeShipping checks == 1
// Incorrect assumption: "both 1 means the same concept"
// "Bug": adds: if (isPriority(order) && isFreeShipping(order))
//         → but isPriority(1) checks customerTier, isFreeShipping(1) checks STANDARD shipping
//         → GOLD customers with STANDARD shipping get a flag that means nothing
// The developer had no way to know: all three "1"s mean different things.

// FIX — named constants / enums per domain concept:
enum CustomerTier    { STANDARD(0), GOLD(1), PLATINUM(2); }
enum ShippingMethod  { STANDARD(1), EXPRESS(2), OVERNIGHT(3); }
enum OrderStatus     { PENDING(0), CONFIRMED(1), SHIPPED(2), DELIVERED(3); }

// Now the intent is clear and the types prevent cross-domain comparison bugs.
```

---

### 🔗 Related Keywords

- `Refactoring` — Extract Constant, Extract Enum are the direct refactoring moves
- `Code Quality` — Magic Numbers are a primary code smell in static analysis
- `Enums` — the strongest form of magic number elimination: typed and exhaustive
- `Configuration Management` — environment-specific "magic numbers" belong in config, not constants
- `Anti-Patterns Overview` — parent: Magic Numbers in the complete anti-pattern catalog

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Unexplained numeric/string literals in    │
│              │ code. Meaning known only to original author│
│              │ or requires external knowledge.           │
├──────────────┼───────────────────────────────────────────┤
│ DETECT WITH  │ PMD:MagicNumber, Checkstyle, SonarQube;  │
│              │ code review: "what does this number mean?"│
├──────────────┼───────────────────────────────────────────┤
│ FIX WITH     │ Named constants (private static final);  │
│              │ Enums for typed sets; Config for          │
│              │ environment-specific values               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Recipe: add 3 of the white powder, cook │
│              │  for 27 until 165. Named: 3 cups flour,  │
│              │  27 min, 165°F internal temp."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Enums → Refactoring → Code Quality →     │
│              │ Configuration Management → PMD/Checkstyle │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Java enums are a powerful form of named constant replacement — they are typed, exhaustive, and can carry behavior. But Java enums predate sealed classes (Java 17). With Java's `sealed interface` + `record` pattern: `sealed interface PaymentMethod permits Visa, MasterCard, DigitalWallet {}`, you get algebraic data types. How do sealed interfaces + records differ from enums for representing a fixed set of types? In what scenario is a sealed interface + record more appropriate than an enum?

**Q2.** Configuration management is the domain for magic numbers that need to vary by environment (production timeout = 30s; dev timeout = 5s). Spring Boot's `@ConfigurationProperties`, `@Value`, and externalized configuration (application.yml + environment variables) enable this. But a constant that "just needs to be different in staging" might indicate a deeper design issue. Describe the decision framework: when should a value be: (a) a `private static final` constant; (b) an `@ConfigurationProperties` bean; (c) a database configuration record; (d) a feature flag?
