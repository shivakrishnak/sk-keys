---
id: DSA-075
title: Testing DSA Correctness (Property-Based and Edge Cases)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-023, DSA-042
used_by: DSA-077
related: DSA-042, DSA-076
tags:
  - testing
  - property-based-testing
  - edge-cases
  - correctness
  - junit
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 75
permalink: /technical-mastery/dsa/testing-dsa-correctness/
---

## TL;DR

DSA implementations need property-based testing (invariant
holds for all inputs) and systematic edge cases - not just
happy-path examples; off-by-one bugs hide in empty
collections, single elements, and duplicates.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-075 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | testing, DSA-correctness, property-based |
| **Prerequisites** | DSA-023, DSA-042 |

---

### The Problem This Solves

A custom sorting implementation passes 20 hand-crafted
unit tests but silently produces wrong output for arrays
with duplicate elements, negative numbers, or exactly 2
elements. Property-based testing generates thousands of
random inputs and checks invariants (sorted order,
same elements) - catches corner cases that example-based
tests miss.

---

### Textbook Definition

Property-based testing verifies that implementations
satisfy invariant properties across many generated inputs,
not just specific examples. For DSA:
- Structural invariants: BST property holds after every
  insert/delete; heap order property maintained
- Functional properties: sort produces ordered output
  with same elements; search returns correct result
- Idempotency: sort(sort(arr)) == sort(arr)
- Roundtrip: insert then remove = original state

---

### How It Works

**Systematic edge cases for any DSA operation:**

```java
// MANDATORY edge cases to test for any collection:
// 1. Empty collection
// 2. Single element
// 3. Two elements (boundary)
// 4. Maximum size (stress test)
// 5. Duplicates
// 6. Already sorted / reverse sorted (for sort algos)
// 7. All same elements
// 8. Negative numbers / null values (if applicable)

@Test
void testBinarySearch_allEdgeCases() {
    int[] arr = {};
    assertEquals(-1, binarySearch(arr, 5));   // empty

    arr = new int[]{5};
    assertEquals(0, binarySearch(arr, 5));     // found, size 1
    assertEquals(-1, binarySearch(arr, 3));    // not found, size 1

    arr = new int[]{1, 2};
    assertEquals(0, binarySearch(arr, 1));     // left of 2
    assertEquals(1, binarySearch(arr, 2));     // right
    assertEquals(-1, binarySearch(arr, 3));    // not found, size 2

    arr = new int[]{1, 1, 1, 1};
    // any valid index for duplicates
    assertTrue(binarySearch(arr, 1) >= 0);     // duplicates

    arr = new int[]{1};
    assertEquals(-1, binarySearch(arr, 0));    // below range
    assertEquals(-1, binarySearch(arr, 2));    // above range
}
```

**Property-based testing with jqwik (Java):**

```java
import net.jqwik.api.*;

class SortPropertyTest {

    @Property
    void sortedOutputIsOrdered(@ForAll List<Integer> list) {
        int[] arr = list.stream().mapToInt(i->i).toArray();
        mySort(arr);
        // Property: every adjacent pair must be ordered
        for (int i = 0; i < arr.length - 1; i++) {
            assertTrue(arr[i] <= arr[i+1],
                "Not sorted at index " + i);
        }
    }

    @Property
    void sortPreservesSameElements(@ForAll List<Integer> list) {
        int[] arr = list.stream().mapToInt(i->i).toArray();
        int[] copy = arr.clone();
        mySort(arr);
        // Property: sorted array has same elements
        Arrays.sort(copy); // reference sort
        assertArrayEquals(copy, arr);
    }

    @Property
    void sortIsIdempotent(@ForAll List<Integer> list) {
        int[] arr = list.stream().mapToInt(i->i).toArray();
        mySort(arr);
        int[] firstSort = arr.clone();
        mySort(arr);
        assertArrayEquals(firstSort, arr); // sort(sort(x)) == sort(x)
    }
}
```

**BST invariant testing:**

```java
// Property: every BST node satisfies BST property
boolean isBST(TreeNode node, long min, long max) {
    if (node == null) return true;
    if (node.val <= min || node.val >= max) return false;
    return isBST(node.left, min, node.val) &&
           isBST(node.right, node.val, max);
}

@After // run after every insert/delete test
void verifyBSTInvariant() {
    assertTrue(isBST(root, Long.MIN_VALUE, Long.MAX_VALUE));
}
```

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "If 5 example tests pass, the implementation is correct" | Off-by-one bugs, integer overflow, and edge cases appear at boundaries; property-based tests generate 1000+ cases automatically |
| "Property tests replace unit tests" | Complementary: unit tests document expected behavior with specific examples; property tests verify invariants across the input space |

---

### Failure Modes & Diagnosis

**Failure: Sort breaks on arrays with Integer.MIN_VALUE**
- Cause: Comparator `(a,b) -> a-b` overflows for
  Integer.MIN_VALUE - Integer.MAX_VALUE
- Fix: Use `Integer.compare(a, b)` never subtraction

---

### Quick Reference Card

| DSA Operation | Key Properties to Test |
|--------------|----------------------|
| Sort | Ordered output, same elements, idempotent |
| Search | Correct index, -1 for missing, all positions |
| HashMap | get(put(k,v))==v, size after remove |
| BST | BST invariant after every operation |
| Graph algo | Correct on empty graph, single node, cycle |

---

### Mastery Checklist

- [ ] Tests all 8 edge cases for any new implementation
- [ ] Can write a property-based test with jqwik or QuickCheck
- [ ] Uses `Integer.compare()` not subtraction in comparators

---

### Interview Deep-Dive

**Q1 (Medium):** How would you test a custom hash map
implementation beyond basic put/get?

> Structural: verify size() after put/remove; verify
> size stays correct after duplicate key put.
> Functional: get returns null for absent key; get after
> remove returns null; put returns previous value.
> Property-based: for random key-value pairs, verify
> get(k) == last put(k, v) for all k.
> Edge cases: null key (if supported), null value, capacity
> boundary (stress to trigger resizing), same hashcode
> keys (collision test).
> Performance property: 1000 sequential puts, all gets
> succeed (verify no silent data loss during resize).
