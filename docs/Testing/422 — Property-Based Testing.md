---
layout: default
title: "Property-Based Testing"
parent: "Testing"
nav_order: 422
permalink: /testing/property-based-testing/
number: "422"
category: Testing
difficulty: ★★★
depends_on: Unit Test, QuickCheck, jqwik
used_by: Unit Test, TDD, Fuzzing
tags: #testing #advanced #property-based #quality
---

# 422 — Property-Based Testing

`#testing` `#advanced` `#property-based` `#quality`

⚡ TL;DR — Instead of specifying specific examples, define properties that must hold for all inputs — and let the framework generate hundreds of random test cases automatically.

| #422 | Category: Testing | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Unit Test, QuickCheck, jqwik | |
| **Used by:** | Unit Test, TDD, Fuzzing | |

---

### 📘 Textbook Definition

Property-Based Testing (PBT) is a testing approach where instead of writing specific example inputs and expected outputs, you define invariant properties that must hold for ALL valid inputs. A PBT framework (jqwik, QuickCheck) generates hundreds or thousands of random inputs, runs the code against each, and reports any input that falsifies the property — the "shrunk" minimal failing example.

---

### 🟢 Simple Definition (Easy)

Instead of "test that sort([3,1,2]) returns [1,2,3]", you write: **"for any list, sorted output is always in ascending order"** — and the framework generates 1000 random lists to try to break that property.

---

### 🔵 Simple Definition (Elaborated)

Example-based tests (unit tests) verify specific cases — only the cases you thought to write. Properties describe universal truths about your code. PBT finds edge cases you never thought to write — empty lists, negative numbers, Unicode strings, extremely large inputs, boundary values — by generating them automatically. When it finds a failure, it "shrinks" the input to the minimal failing example for easy debugging.

---

### 🔩 First Principles Explanation

**The core problem:**
Unit tests only test what you think to test. The bug is always in the case you didn't think to test. "I tested positive numbers; the bug was in negative numbers." "I tested normal strings; the bug was in empty strings."

**The insight:**
> "Instead of specifying examples, specify invariants. Let the machine find the counterexamples you didn't think of."

```
Example-Based Test:
  @Test void sort_example() {
    assertThat(sort(List.of(3,1,2))).isEqualTo(List.of(1,2,3));
  }
  // Tests ONE specific case

Property-Based Test:
  @Property void sorted_output_is_ordered(@ForAll List<Integer> list) {
    List<Integer> sorted = sort(list);
    for (int i = 0; i < sorted.size() - 1; i++) {
      assertThat(sorted.get(i)).isLessThanOrEqualTo(sorted.get(i + 1));
    }
  }
  // Tests ANY list jqwik generates — 1000 random cases
```

---

### ❓ Why Does This Exist (Why Before What)

Example-based tests are limited by imagination. Properties eliminate this limitation — the framework is an adversary trying to break your property with creative inputs. This discovers bugs in edge cases humans naturally avoid when writing examples.

---

### 🧠 Mental Model / Analogy

> PBT is like hiring 1000 quality assurance testers at once, each choosing random but valid inputs to try to break your system. They don't follow a test script — they creatively try anything the specification allows. When one of them breaks it, they hand you the simplest possible reproduction case.

---

### ⚙️ How It Works (Mechanism)

```
PBT execution flow:

  1. Define a property (invariant that must always hold)
  2. Framework generates random valid inputs (100s by default)
  3. Run property for each input — check invariant holds
  4. If invariant fails: record the failing input
  5. Shrink: find the minimal input that still fails
  6. Report: "Property failed for input [0, -1] — minimal failing case"

Good properties to write:
  - Roundtrip: encode(decode(x)) == x
  - Idempotency: sort(sort(x)) == sort(x)
  - Commutativity: add(a,b) == add(b,a)
  - Invariant: size doesn't change: sort(x).size() == x.size()
  - Boundary: no element lost or added
  - Oracle: compare to known-correct (slow) implementation
```

---

### 💻 Code Example

```java
// jqwik — Java property-based testing framework
class SortingProperties {

    @Property
    void sorted_output_is_in_ascending_order(
            @ForAll List<@IntRange(min = -1000, max = 1000) Integer> list) {

        List<Integer> sorted = MergeSort.sort(list);

        for (int i = 0; i < sorted.size() - 1; i++) {
            assertThat(sorted.get(i))
                .isLessThanOrEqualTo(sorted.get(i + 1));
        }
    }

    @Property
    void sorting_is_idempotent(@ForAll List<Integer> list) {
        // sort(sort(x)) == sort(x)
        List<Integer> sortedOnce = MergeSort.sort(list);
        List<Integer> sortedTwice = MergeSort.sort(sortedOnce);
        assertThat(sortedTwice).isEqualTo(sortedOnce);
    }

    @Property
    void sorting_preserves_all_elements(@ForAll List<Integer> list) {
        List<Integer> sorted = MergeSort.sort(list);
        // No elements lost or added
        assertThat(sorted).containsExactlyInAnyOrderElementsOf(list);
    }

    // Roundtrip property for serialization
    @Property
    void json_roundtrip_preserves_user(
            @ForAll @NotNull String name,
            @ForAll @IntRange(min = 0, max = 150) int age) {

        User user = new User(name, age);
        String json = jackson.writeValueAsString(user);
        User deserialized = jackson.readValue(json, User.class);

        assertThat(deserialized.getName()).isEqualTo(user.getName());
        assertThat(deserialized.getAge()).isEqualTo(user.getAge());
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| PBT replaces example-based tests | They complement — examples for documentation; properties for edge coverage |
| PBT is only for pure functions | PBT works for stateful systems too (stateful testing, model-based) |
| Failures are hard to debug | Shrinking reduces the failing input to the minimal case automatically |
| PBT finds all bugs | PBT is probabilistic — it increases confidence but can't prove correctness |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Weak Properties**
`@Property void always_returns_non_null(@ForAll String s) { assertThat(service.process(s)).isNotNull(); }`
This property is too weak — it verifies almost nothing.
Fix: write properties that encode real invariants about your domain.

**Pitfall 2: Non-Deterministic Tests**
PBT generates random inputs — the same test can fail differently each run if not seeded.
Fix: jqwik records the seed for failing cases; always reproduce with the same seed before fixing.

**Pitfall 3: Too Slow for CI**
Running 1000 cases per property × 50 properties = 50,000 iterations in CI.
Fix: configure fewer iterations in CI (`tries = 100`); run full suite nightly or pre-merge.

---

### 🔗 Related Keywords

- **Unit Test** — example-based testing; PBT complements it
- **jqwik** — the leading Java PBT framework (JUnit 5 compatible)
- **QuickCheck** — the original Haskell PBT framework; inspired all others
- **Shrinking** — the process of reducing a failing input to its minimal form
- **Fuzzing** — related technique; generates malformed/random security-focused inputs

---

### 📌 Quick Reference Card

| #422 | Category: Testing | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Unit Test, QuickCheck, jqwik | |
| **Used by:** | Unit Test, TDD, Fuzzing | |

---

### 🧠 Think About This Before We Continue

**Q1.** What is "shrinking" in property-based testing and why is it essential for usability?  
**Q2.** Give three examples of properties you could write for a stack data structure.  
**Q3.** How does property-based testing complement rather than replace example-based unit tests?

