---
layout: default
title: "Property-Based Testing"
parent: "Testing"
nav_order: 1152
permalink: /testing/property-based-testing/
number: "1152"
category: Testing
difficulty: ★★★
depends_on: Unit Test, TDD
used_by: Developers, QA Engineers
related: Fuzzing, QuickCheck, jqwik, Hypothesis, Generative Testing
tags:
  - testing
  - property-based-testing
  - generative
  - randomized
---

# 1152 — Property-Based Testing

⚡ TL;DR — Property-Based Testing (PBT) automatically generates hundreds of random inputs and verifies that your code satisfies a general property (not just a single example) — finding edge cases you'd never think to write by hand.

| #1152           | Category: Testing                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Unit Test, TDD                                             |                 |
| **Used by:**    | Developers, QA Engineers                                   |                 |
| **Related:**    | Fuzzing, QuickCheck, jqwik, Hypothesis, Generative Testing |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You write tests for `sort(list)`:

- `sort([3, 1, 2])` → `[1, 2, 3]` ✓
- `sort([])` → `[]` ✓
- `sort([1])` → `[1]` ✓

You feel confident. But there's a bug: `sort` fails when the list has more than 1,000 elements (integer overflow in merge step). Or it fails for lists containing `Integer.MIN_VALUE`. Or it fails when the same element appears 3+ times. Your hand-picked examples never hit these cases. Property-based testing would generate thousands of random lists — including those edge cases you didn't think of — and find the bug automatically.

THE INSIGHT:
Example-based tests verify: "given THIS input, I get THIS output." Property-based tests verify: "for ANY valid input, THIS invariant holds." The invariants (properties) are higher-level: "sorted list is always sorted," "sorted list has same length as input," "sorted list is a permutation of input." These three properties together fully specify correct sort behavior.

---

### 📘 Textbook Definition

**Property-Based Testing (PBT)** is a testing technique where instead of writing specific input-output examples, you write **properties** — invariants that must hold for all (or a statistically representative sample of) valid inputs. A PBT framework generates random inputs, runs the test for each, and if a property fails, automatically **shrinks** the failing input to the minimal example that still causes failure (making debugging easier). Originated with Haskell's QuickCheck (1999); major implementations: Hypothesis (Python), jqwik (Java), fast-check (JavaScript), ScalaCheck.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
PBT = define invariants + let the framework generate 1,000 random tests to break them.

**One analogy:**

> PBT is like hiring a **tireless adversarial QA engineer** who tries every possible input combination, looking for any case that breaks your stated invariant. Unlike a human QA who picks a few representative cases, this QA never gets tired and can check thousands of variations — including the weird ones at the edges.

---

### 🔩 First Principles Explanation

IDENTIFYING PROPERTIES (the hard part):

```
Function: encode(String s) and decode(String encoded)
Property: round-trip property
  ∀ s: decode(encode(s)) == s

  This one property, if it holds for 10,000 random strings,
  gives extremely high confidence in both encode and decode.

Function: sort(List list)
Properties:
  1. Sorted:      sort(list)[i] ≤ sort(list)[i+1] for all i
  2. Same length: sort(list).size() == list.size()
  3. Permutation: every element in list appears in sort(list) same number of times

  (These three together constitute the complete specification of sort)
```

PROPERTY CATEGORIES:

```
1. Round-trip (inverse operations):
   parse(serialize(x)) == x
   decode(encode(s)) == s

2. Invariants (properties preserved under transformation):
   sort(list).size() == list.size()
   encrypt and decrypt restore original

3. Idempotence (applying twice = applying once):
   sort(sort(list)) == sort(list)
   toUpperCase(toUpperCase(s)) == toUpperCase(s)

4. Commutativity:
   add(a, b) == add(b, a)

5. Oracle (compare against simpler reference implementation):
   fastSort(list) == referenceSort(list)

6. Boundary invariants:
   result is never null
   result is always in valid range [0, 100]
```

SHRINKING — THE KILLER FEATURE:

```
PBT finds failing input: [8472, -1, 99999, 0, Integer.MIN_VALUE, 3]
               shrinks to: [0, Integer.MIN_VALUE]
               shrinks to: [Integer.MIN_VALUE]
Minimal failing example: a list containing only Integer.MIN_VALUE

Without shrinking: you'd debug a complex 6-element list
With shrinking:    you immediately see the minimal case
                   "sort fails when list contains Integer.MIN_VALUE"
```

---

### 🧪 Thought Experiment

THE SERIALIZATION BUG HUNT:

```java
@Property
void jsonSerializationRoundTrip(@ForAll Order order) {
    String json = objectMapper.writeValueAsString(order);
    Order deserialized = objectMapper.readValue(json, Order.class);
    assertThat(deserialized).isEqualTo(order);
}

// jqwik generates 1,000 random Order objects:
// - null fields in optional values? ✓
// - empty strings? ✓
// - strings with unicode characters (emoji, CJK)? ← FAIL!
// Minimal failing case (after shrinking): order.description = "€"
// Root cause: Jackson configured with ISO-8859-1, not UTF-8
// Found in 3 seconds; would have hit production with customer names
```

---

### 🧠 Mental Model / Analogy

> Property-based testing is the **mathematician's approach** to verification: instead of checking specific examples ("is 2+2=4?"), it proves general theorems ("for all integers a, b: add(a,b) == add(b,a)"). You can't check all integers, but checking 10,000 random ones gives statistical confidence. If it's true for 10,000 random pairs, the chances it's false are astronomically low — and if it IS false, the framework finds the simplest counterexample.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Instead of writing one test with one input, write a property (invariant) and let the framework generate 1,000 random inputs to test it. If any input breaks the property, you see the minimal failing case.

**Level 2:** In Java with jqwik: `@Property` annotation on a test method, `@ForAll` on parameters — jqwik generates values. Built-in generators: `@ForAll int`, `@ForAll String`, `@ForAll List<@ForAll Integer>`. Custom generators with `@Provide`. Number of tries: `@Property(tries = 1000)`. Reproducible: every failure includes a seed for reproduction.

**Level 3:** Stateful property-based testing: generating sequences of operations and verifying invariants hold after each. Example: generate random sequences of `add(item)`, `remove(item)`, `clear()` operations on a shopping cart; verify after each operation that `cart.size() >= 0` and `cart.total() == sum(cart.items())`. This finds race conditions and state machine bugs.

**Level 4:** PBT and TDD: use PBT where the property is easy to express (serialization, parsing, mathematical operations, state machines). Use example-based TDD where the behavior is specific and hard to express as a general property (business rules with specific edge cases). They complement: TDD for known edge cases, PBT for unknown edge cases. The "free theorem" insight: if your function satisfies the round-trip property for 10,000 random inputs, the chance of a latent bug is lower than most security CVEs. PBT is particularly powerful for: parsers/serializers, algorithms (sort, search, compression), cryptography, state machines.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              PROPERTY-BASED TESTING FLOW                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  @Property: ∀ input: serialize-deserialize roundtrip     │
│                                                          │
│  Generator → random Order #1 → serialize → deserialize  │
│              → equals? ✓                                │
│  Generator → random Order #2 → ... ✓                   │
│  Generator → random Order #573 → ... FAIL!              │
│                      │                                  │
│              SHRINKING: find minimal failing input       │
│              Order(desc=null, items=[], ...) → PASS       │
│              Order(desc="€", items=[]) → FAIL ✓ minimal  │
│                      │                                  │
│  Report: "Property failed for: Order(description='€')"  │
│          "Seed: 42 (reproduce with @Seed(42))"           │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Testing a URL parser with PBT:

Properties:
  1. parse(url).toUrl() == url  (round-trip)
  2. parse(url).host() is never null for valid URLs
  3. parse(url).port() is in range [1, 65535] or -1 (not specified)

PBT session (jqwik, 1,000 tries):
  Try #1-500: valid URLs → all pass
  Try #501: URL with port 0 → parse succeeds → port() = 0 → PROPERTY 3 FAILS
    Minimal failing input: "http://host:0"
    Bug: URL parser allows port 0 (invalid, reserved by OS)
    Fix: validate port range in parser

  Re-run after fix: 1,000 tries, all pass

  Additional property test: null safety
  @Property void parse_neverThrowsForAnyString(@ForAll String input) {
    assertThatCode(() -> urlParser.parse(input)).doesNotThrowAnyException();
    // Should handle garbage input gracefully (return empty Optional, not throw)
  }
  Try #73: input = null → NullPointerException → FAIL
  Minimal: null
  Fix: null check at entry
```

---

### 💻 Code Example

```java
// jqwik: Property-based testing for Java
class StringEncoderPropertyTest {

    @Property
    void roundTripEncoding(@ForAll String original) {
        String encoded = StringEncoder.encode(original);
        String decoded = StringEncoder.decode(encoded);
        assertThat(decoded).isEqualTo(original);
    }

    @Property
    void encodedStringIsAlwaysPrintable(@ForAll String input) {
        String encoded = StringEncoder.encode(input);
        encoded.chars().forEach(c ->
            assertThat(c).isBetween(32, 126));  // printable ASCII
    }

    @Property
    void sortIsIdempotent(@ForAll List<@ForAll Integer> list) {
        List<Integer> once = new ArrayList<>(list);
        List<Integer> twice = new ArrayList<>(list);
        Collections.sort(once);
        Collections.sort(twice);
        Collections.sort(twice);  // sort twice
        assertThat(twice).isEqualTo(once);
    }

    // Custom generator: valid email addresses
    @Provide
    Arbitrary<String> validEmails() {
        return Arbitraries.strings().alpha().ofMinLength(1).ofMaxLength(20)
            .map(local -> local + "@" + "example.com");
    }

    @Property
    void emailParserAcceptsAllValidEmails(@ForAll("validEmails") String email) {
        assertThat(EmailValidator.isValid(email)).isTrue();
    }
}
```

---

### ⚖️ Comparison Table

|                     | Example-Based (Unit)             | Property-Based                           |
| ------------------- | -------------------------------- | ---------------------------------------- |
| Test data           | Hand-picked specific values      | Generated automatically (random)         |
| What it verifies    | Specific input → expected output | Invariant holds for all (sampled) inputs |
| Edge case discovery | What you think of                | What the generator finds                 |
| Failing output      | Failing example                  | Minimal shrunk failing case              |
| Maintenance         | Low                              | Medium (properties need thought)         |
| Best for            | Known business cases             | Algorithms, serialization, parsers       |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- |
| "PBT replaces unit tests"              | PBT complements unit tests; unit tests for specific cases, PBT for invariants                  |
| "PBT is just random testing"           | PBT is systematic: it uses shrinking to find minimal failures; random testing has no shrinking |
| "PBT is only for functional languages" | jqwik (Java), Hypothesis (Python), fast-check (JS) bring PBT to mainstream languages           |
| "Properties are hard to find"          | Start with round-trip properties (serialize/deserialize); these are easy and very effective    |

---

### 🚨 Failure Modes & Diagnosis

**1. Flaky PBT (Passes Sometimes, Fails Sometimes)**

Cause: PBT is randomized; with a low `tries` setting, the failing case may not be generated every run.
Fix: Increase `tries`. Once a failure is found, the seed is logged — add `@Seed(123)` to reproduce deterministically.

**2. Property Too Weak (Test Always Passes Even With Bugs)**

Cause: Property allows too many outcomes (e.g., "result is not null" — true even if result is completely wrong).
Fix: Strengthen the property: combine multiple invariants. Use the oracle pattern: compare with a simple reference implementation.

---

### 🔗 Related Keywords

- **Prerequisites:** Unit Test, TDD
- **Builds on:** jqwik, QuickCheck, Hypothesis, Fuzzing
- **Related:** Generative Testing, Randomized Testing, Specification-Based Testing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Generate random inputs, verify invariants│
├──────────────┼───────────────────────────────────────────┤
│ PROPERTY     │ Round-trip, idempotence, commutativity,  │
│ PATTERNS     │ invariant, oracle                        │
├──────────────┼───────────────────────────────────────────┤
│ JAVA TOOL    │ jqwik: @Property @ForAll                 │
├──────────────┼───────────────────────────────────────────┤
│ KILLER FEAT  │ Shrinking: fails with minimal example    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Write the law, not the example"         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Property-based testing found the "therac-25 class" of bugs — bugs that only appear under specific combinations of input values that are unlikely to be hand-picked. Describe a specific domain where PBT provides exceptional value: a payment amount calculator that accepts amounts in different currencies, rounding to 2 decimal places, with currency conversion rates. (1) What hand-picked unit tests would NOT catch a floating-point precision bug that occurs for amounts like 0.1 + 0.2? (2) What property would catch it? (3) How would shrinking help identify the minimal failing amount? (4) How does the "oracle pattern" (compare against BigDecimal reference implementation) eliminate the need to predict the exact expected output?

**Q2.** Stateful PBT: instead of testing pure functions, test a stateful system (like a shopping cart) by generating random sequences of operations. Describe: (1) how jqwik's `@StatefulProperty` / action-based PBT works (generate a list of actions, apply them in order, verify invariants after each action); (2) what invariants you'd define for a shopping cart (size ≥ 0, total = sum of item prices, remove(item) only if item exists); (3) what class of bug stateful PBT finds that pure PBT doesn't (sequence-dependent bugs, state machine violations); (4) the connection between stateful PBT and model-based testing (maintaining a simple model alongside the real implementation, comparing states).
