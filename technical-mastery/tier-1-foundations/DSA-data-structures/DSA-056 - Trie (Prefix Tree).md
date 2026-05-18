---
id: DSA-056
title: Trie (Prefix Tree)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-016
used_by: DSA-077, DSA-100
related: DSA-016, DSA-049, DSA-077
tags:
  - data-structures
  - trie
  - prefix-tree
  - autocomplete
  - string
  - o-k
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 56
permalink: /technical-mastery/dsa/trie/
---

## TL;DR

A Trie stores strings by sharing prefixes as tree paths -
O(k) insert, search, and prefix-check where k = key length,
regardless of how many strings are stored. The data
structure behind autocomplete and spell-check.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-056 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, trie, autocomplete, O(k) |
| **Prerequisites** | DSA-016 |

---

### The Problem This Solves

HashMap gives O(1) exact match lookup. But "does any stored
string start with 'pre'?" requires scanning all strings
with HashMap. A Trie answers prefix queries in O(k)
regardless of how many strings are stored.

---

### Textbook Definition

A Trie (retrieval tree, pronounced "try") is a tree where
each path from root to a marked node represents a stored
string. Each node stores one character and a map of children.
The root is empty. All descendants of a node share the same
prefix.

Time: O(k) for insert, search, starts-with, where k = key
length. Space: O(sum of all key lengths) in worst case;
prefix sharing reduces space when keys share prefixes.

---

### Understand It in 30 Seconds

Insert "apple", "app", "apply", "apt":

```
           root
            |
           [a]
            |
           [p]
          /   \
        [p]   [t] ← "apt"
       /   \
     [l]   (end) ← "app"
    /    \
  [e]   [y]   ← "apply"
   |
  (end) ← "apple"
```

Search "app": root→a→p→p → found (marked).
Starts with "ap": root→a→p → exists (any child).

---

### How It Works

**Trie implementation:**

```java
class Trie {
    private final Map<Character, Trie> children =
        new HashMap<>();
    private boolean isEnd = false;

    // Insert word: O(k) where k = word length
    void insert(String word) {
        Trie node = this;
        for (char c : word.toCharArray()) {
            node.children.putIfAbsent(c, new Trie());
            node = node.children.get(c);
        }
        node.isEnd = true;
    }

    // Exact search: O(k)
    boolean search(String word) {
        Trie node = this;
        for (char c : word.toCharArray()) {
            if (!node.children.containsKey(c)) return false;
            node = node.children.get(c);
        }
        return node.isEnd;
    }

    // Prefix search: O(k)
    boolean startsWith(String prefix) {
        Trie node = this;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c)) return false;
            node = node.children.get(c);
        }
        return true;  // any string under this node exists
    }

    // Get all words with prefix (autocomplete): O(k + output)
    List<String> autocomplete(String prefix) {
        List<String> results = new ArrayList<>();
        Trie node = this;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c))
                return results; // no match
            node = node.children.get(c);
        }
        collectAll(node, new StringBuilder(prefix), results);
        return results;
    }

    private void collectAll(Trie node, StringBuilder current,
                            List<String> results) {
        if (node.isEnd) results.add(current.toString());
        for (Map.Entry<Character, Trie> entry :
                node.children.entrySet()) {
            current.append(entry.getKey());
            collectAll(entry.getValue(), current, results);
            current.deleteCharAt(current.length() - 1);
        }
    }
}
```

---

### Comparison Table

| Operation | HashMap | Trie | Sorted Map |
|-----------|---------|------|-----------|
| Exact search | O(k) avg | O(k) | O(k log n) |
| Prefix search | O(n*k) | O(k) | O(log n) |
| All with prefix | O(n*k) | O(k+output) | O(log n+output) |
| Space | O(n*k) | O(n*k) but shared | O(n*k) |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Trie is always more space-efficient than HashMap" | For keys with few shared prefixes, Trie uses more space (overhead per node) |
| "Trie search is O(1) like HashMap" | O(k) - proportional to key length. But k is typically small and bounded, so it behaves like O(1) in practice |

---

### Failure Modes & Diagnosis

**Failure: Memory explosion with long, unique keys**
- Cause: Trie with many long keys sharing no prefixes
  creates a node per character - more memory than HashMap
- Fix: Compressed trie (Patricia tree) merges single-child
  chains into one node; Apache's Ternary Search Tree is
  another option

---

### Quick Reference Card

| Operation | Time |
|-----------|------|
| Insert | O(k) |
| Search (exact) | O(k) |
| Search (prefix) | O(k) |
| Autocomplete | O(k + results) |
| Space | O(n*k) worst, prefix-sharing reduces it |

**k = key length. Independent of number of stored keys.**

---

### The Surprising Truth

Google's search autocomplete was built on tries. When you
type "jav", the prefix lookup returns all stored queries
starting with "jav" in O(k) regardless of the 100 billion
queries indexed. The challenge Google solved was storing a
Trie of 100 billion unique queries - they use compressed
tries (DAWG - Directed Acyclic Word Graph) to merge common
suffixes in addition to common prefixes, reducing memory
by orders of magnitude.

---

### Mastery Checklist

- [ ] Can implement Trie with insert, search, startsWith
      from memory
- [ ] Understands the prefix sharing memory advantage
- [ ] Can implement autocomplete (DFS from prefix node)
- [ ] Knows when to prefer Trie over HashMap

---

### Interview Deep-Dive

**Q1 (Medium):** Design an autocomplete system. When a
user types a prefix, return the top 3 most frequently
searched completions.

> Data structure: Trie where each end node stores the
> frequency count. Insert: O(k), increment frequency.
> Query: traverse to prefix node in O(k), then DFS to
> find all words under it. Use a min-heap of size 3 to
> track top-3 by frequency as you DFS. Return heap.
> Time: O(k + n) where n = words under prefix node.
> Enhancement for production: cache top-3 at each node
> (update cache on every insert); reduces query to O(k).
> This is the design behind search engine autocomplete.
