---
layout: default
title: "Array"
parent: "Data Structures & Algorithms"
nav_order: 31
permalink: /dsa/array/
number: "031"
category: Data Structures & Algorithms
difficulty: ★☆☆
depends_on: Memory Management Models
used_by: ArrayList, Stack, Queue / Deque, HashMap, Heap (Min/Max), Dynamic Programming
tags:
  - datastructure
  - algorithm
  - foundational
---

# 031 — Array

`#datastructure` `#algorithm` `#foundational`

⚡ TL;DR — A contiguous block of memory storing elements of the same type at fixed-size intervals, providing O(1) random access by index but O(n) insertion and deletion.

| #031 | Category: Data Structures & Algorithms | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Memory Management Models | |
| **Used by:** | ArrayList, Stack, Queue / Deque, HashMap, Heap (Min/Max), Dynamic Programming | |

---

### 📘 Textbook Definition

An **array** is a data structure consisting of a contiguous region of memory storing a fixed number of elements of a uniform type, each accessible via an integer index in O(1) time using pointer arithmetic (`base_address + index × element_size`). Arrays have a fixed capacity determined at allocation; resizing requires allocating a new block and copying elements. In Java, arrays are objects with a fixed `length` field; the `int[]`, `Object[]` notation is the primitive form, while `ArrayList<E>` provides a dynamic-capacity wrapper.

### 🟢 Simple Definition (Easy)

An array is a numbered list of boxes in a row — each box holds one item, and you can reach any specific box instantly by its number.

### 🔵 Simple Definition (Elaborated)

Arrays are the most fundamental data structure in computing. All elements sit side by side in memory, which means finding the element at position 5 takes the same time as finding element 5,000 — just multiply the size of one element by the index and jump directly to that memory address. This O(1) access makes arrays extremely fast for reading. The trade-off: inserting an element in the middle requires shifting everything after it one position forward, which is O(n). Arrays also have a fixed size — to add more elements than allocated, you must copy the entire array to a larger space (which is exactly what `ArrayList` does internally).

### 🔩 First Principles Explanation

**Memory layout:** When you declare `int[] arr = new int[5]`, the JVM allocates 5 × 4 bytes (20 bytes) contiguously. The address of element `i` is `base + i × 4`. This is identical to how hardware cache works — sequential memory access patterns are cache-friendly (spatial locality).

**Access:** `arr[i]` → `*(base + i × sizeof(int))` — a single memory read regardless of `i`.

**Insert at position k:**
1. Shift all elements from `k` to `n-1` one position right: O(n-k) shifts.
2. Write new element at position `k`.
3. Worst case (insert at 0): shift all n elements = O(n).

**Delete at position k:**
1. Shift all elements from `k+1` to `n-1` one position left: O(n-k) shifts.
2. Nullify/overwrite last element.
3. Worst case (delete at 0): shift all n elements = O(n).

**Dynamic resizing (ArrayList pattern):**
When the array is full:
1. Allocate new array of capacity `2 × old_capacity`.
2. Copy all `n` elements.
3. Free old array.
4. Amortised O(1) append — resize happens O(log n) times for n operations.

```
Array memory layout (int[5]):
index: [0]   [1]   [2]   [3]   [4]
value: [ 1] [ 3] [ 7] [12] [20]
addr:  1000  1004  1008  1012  1016  (4-byte int)
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT arrays (storing items one by one at unrelated memory locations):

- Finding element N requires traversing from element 0: O(n).
- No spatial locality — CPU cache misses on every access.

What breaks without it:
1. Indexed access (arr[42]) requires O(n) search through a linked list.
2. CPU cache lines load 64 bytes at a time — sequential array traversal is massively faster than pointer-chasing.

WITH arrays:
→ O(1) random access via index arithmetic.
→ Cache-friendly sequential scan — exploits spatial locality.
→ Foundation for ArrayList, hash tables, heaps, and most other data structures.

### 🧠 Mental Model / Analogy

> An array is like a row of numbered post office boxes. Each box is the same size and the boxes are in order. To get box #47, you count 47 boxes from the first one and open it directly — no searching. But to insert a new box in the middle of the row, you must physically shift every box after it one position. The boxes can't jump — their positions are fixed by their numbers.

"Post office boxes" = array slots, "box number" = index, "direct access by counting" = O(1) access, "shifting boxes" = O(n) insert/delete.

### ⚙️ How It Works (Mechanism)

**Complexity table:**

```
Operation          Best   Average  Worst
──────────────────────────────────────────
Random access [i]  O(1)   O(1)     O(1)
Search (unsorted)  O(1)   O(n)     O(n)
Search (sorted)    O(1)   O(log n) O(log n)  ← binary search
Insert at end      O(1)   O(1)*    O(n)*     ← *amortised (ArrayList)
Insert at index k  O(1)   O(n)     O(n)      ← shift required
Delete at end      O(1)   O(1)     O(1)
Delete at index k  O(1)   O(n)     O(n)      ← shift required
```

**Two-dimensional arrays:**

```
int[][] matrix = new int[3][4]; // 3 rows, 4 columns
matrix[i][j] = value;

Row-major storage (Java/C):
Row 0: [r0c0][r0c1][r0c2][r0c3]
Row 1: [r1c0][r1c1][r1c2][r1c3]
Row 2: [r2c0][r2c1][r2c2][r2c3]
→ Iterating row-by-row is cache-friendly
→ Iterating column-by-column causes cache misses (columns are non-contiguous)
```

### 🔄 How It Connects (Mini-Map)

```
Array (contiguous memory, fixed size) ← you are here
        ↓ dynamic wrapper
ArrayList (Java) — auto-resizing array
        ↓ used as backing data structure for
Stack | Queue | Heap | HashMap (bucket array)
        ↓ foundation for
Dynamic Programming (memoisation table)
Binary Search (requires random access)
Sorting algorithms (QuickSort, MergeSort, HeapSort)
```

### 💻 Code Example

Example 1 — Basic array operations in Java:

```java
// Fixed-size array
int[] arr = {5, 3, 8, 1, 9, 2};

// O(1) access
int val = arr[3]; // val = 1

// Linear search: O(n)
int target = 8;
int idx = -1;
for (int i = 0; i < arr.length; i++) {
    if (arr[i] == target) { idx = i; break; }
}

// Binary search on sorted array: O(log n)
int[] sorted = {1, 2, 3, 5, 8, 9};
int pos = Arrays.binarySearch(sorted, 5); // pos = 3

// Manual insert-at-index (shift right)
int insertAt = 2;
int[] copy = new int[arr.length + 1];
System.arraycopy(arr, 0, copy, 0, insertAt);
copy[insertAt] = 42; // new element
System.arraycopy(arr, insertAt, copy, insertAt + 1,
    arr.length - insertAt);
```

Example 2 — ArrayList (dynamic array):

```java
// ArrayList: auto-resizing array under the hood
List<Integer> list = new ArrayList<>(16); // initial capacity 16

list.add(5);      // O(1) amortised append
list.add(3);      // O(1)
list.add(1, 99);  // O(n) insert at index 1 — shifts elements

System.out.println(list.get(0)); // O(1) random access

// Iterator is cache-friendly — sequential memory traversal
for (int x : list) { /* O(n) total, optimal for cache */ }
```

Example 3 — 2D matrix traversal and cache effects:

```java
int n = 1000;
int[][] matrix = new int[n][n];

// Cache-friendly: row-major (sequential memory access)
long sum = 0;
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n; j++) {
        sum += matrix[i][j]; // sequential; cache-hot
    }
}

// Cache-unfriendly: column-major (strided access)
sum = 0;
for (int j = 0; j < n; j++) {
    for (int i = 0; i < n; i++) {
        sum += matrix[i][j]; // strided; many cache misses
    }
}
// The row-major version can be 2-4× faster for large matrices
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Arrays and ArrayLists are the same | Arrays are fixed-size, primitives allowed. ArrayList wraps an array with dynamic resizing and only supports objects. |
| Inserting at the end of an array is O(n) | Inserting at the end (if capacity available) is O(1). Only inserting in the middle or beginning is O(n) due to shifting. |
| ArrayList.add() is always O(1) | ArrayList.add() is O(1) amortised — usually O(1) but occasionally O(n) when resize triggers a full copy. |
| Arrays are slower than LinkedLists for iteration | Arrays are faster for iteration due to spatial locality and cache friendliness. LinkedList has poor cache performance because nodes are scattered in memory. |
| Java arrays can store any type | Java arrays are typed: `int[]` cannot hold `String`. An `Object[]` can hold any reference type but requires casts. |

### 🔥 Pitfalls in Production

**1. ArrayIndexOutOfBoundsException (Off-by-One)**

```java
// BAD: Classic off-by-one error
int[] arr = new int[5]; // indices 0..4
arr[5] = 99; // ArrayIndexOutOfBoundsException!

// Loops that go too far:
for (int i = 0; i <= arr.length; i++) { // <= should be <
    arr[i] = i; // fails at i=5
}

// GOOD: Always use i < arr.length (not <=)
for (int i = 0; i < arr.length; i++) {
    arr[i] = i;
}
```

**2. Sharing Array References — Unexpected Mutations**

```java
// BAD: Array assignment copies the reference, not the data
int[] original = {1, 2, 3};
int[] copy = original;  // SAME array reference!
copy[0] = 99;           // also changes original[0]!

// GOOD: Deep copy for independent arrays
int[] trueCopy = Arrays.copyOf(original, original.length);
// or: int[] trueCopy = original.clone();
```

**3. Column-Major Matrix Access (Cache Thrashing)**

```java
// BAD for large matrices: column iteration causes cache misses
for (int j = 0; j < n; j++)
    for (int i = 0; i < n; i++)
        process(matrix[i][j]); // 4-10× slower than row-major

// GOOD: Always iterate outer=rows, inner=columns (row-major)
for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
        process(matrix[i][j]); // cache-hot access pattern
```

### 🔗 Related Keywords

- `LinkedList` — alternative data structure: O(1) insert/delete, O(n) access; contrast with array.
- `ArrayList` — Java's dynamic-capacity array wrapper.
- `HashMap` — uses an array of buckets internally for O(1) average key lookup.
- `Heap (Min/Max)` — implemented as an array with specific parent-child index relationships.
- `Binary Search` — requires O(1) random access; only efficient on arrays.
- `Dynamic Programming` — uses arrays (1D or 2D) as memoisation tables.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Contiguous memory: O(1) random access,   │
│              │ O(n) insert/delete in middle.             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Random index access needed; iteration;   │
│              │ known/fixed size; cache-sensitive code.   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Frequent middle insertion/deletion →      │
│              │ use LinkedList or deque instead.          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Array: instant address, painful middle  │
│              │ surgery."                                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ LinkedList → Stack → Queue → HashMap      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** ArrayList doubles its capacity when it runs out of space. Some implementations use a 1.5× growth factor instead. Mathematically derive the amortised cost per append for both factors, and explain why choosing a growth factor < 2 trades individual resize cost vs. total memory waste — specifically, for an ArrayList that grows to n elements with growth factor g, what is the maximum memory wasted as a fraction of actual content?

**Q2.** A 2D matrix operation that iterates column-major instead of row-major is 4× slower on modern hardware despite identical O(n²) algorithmic complexity. Explain the exact CPU hardware mechanism (L1/L2 cache size, cache line size, spatial locality) that causes this performance difference, and identify a real-world algorithm where column-major access is unavoidable — and how matrix transposition remedies it.

