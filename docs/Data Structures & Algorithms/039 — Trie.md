---
layout: default
title: "Trie"
parent: "Data Structures & Algorithms"
nav_order: 39
permalink: /dsa/trie/
number: "039"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: Array, HashMap, Tree Data Structures
used_by: Autocomplete, Spell Checker, IP Routing (LPM), Word Search, String Matching
tags:
  - datastructure
  - algorithm
  - intermediate
  - string
---

# 039 — Trie

`#datastructure` `#algorithm` `#intermediate` `#string`

⚡ TL;DR — A tree where each node represents a character prefix, enabling O(L) insert/search/prefix-check for strings where L is the string length — independent of the number of strings stored.

| #039 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Array, HashMap, Tree Data Structures | |
| **Used by:** | Autocomplete, Spell Checker, IP Routing (LPM), Word Search, String Matching | |

---

### 📘 Textbook Definition

A **trie** (also called a prefix tree or re-trie-val tree) is a rooted tree data structure where each node represents a shared prefix of one or more strings, and edges represent individual characters. Each path from root to a marked terminal node spells out one of the stored strings. For an alphabet of size Σ, each node has up to Σ children (typically stored as an array of size 26 for lowercase letters, or a `HashMap` for variable alphabets). All strings sharing a common prefix share the same initial path. Operations — `insert`, `search`, and `startsWith` — run in O(L) time where L is the string length, independent of the number of strings n in the trie.

### 🟢 Simple Definition (Easy)

A trie is a tree where you spell out a word letter by letter as you walk down the tree — "apple" and "app" share the "a-p-p" path, saving space and enabling fast prefix search.

### 🔵 Simple Definition (Elaborated)

Storing 1,000 strings in a HashMap and searching requires hashing the query string — O(L) for hashing. A trie does better for prefix operations: "does any stored word start with 'pre'?" takes exactly 3 steps in a trie (follow p→r→e) regardless of how many words are stored. The key insight: words sharing a prefix share a path in the tree. "cat," "car," and "card" all start with "ca" — stored as a single shared "ca" node in the trie. This shared-prefix compression makes tries the canonical structure for autocomplete, dictionary lookup, IP longest-prefix matching, and predictive text.

### 🔩 First Principles Explanation

**Structure:**

```
Trie containing: ["app", "apple", "apply", "ape", "bat"]

         root
       /      \
      a*        b*
     /           \
    p*             a*
   / \              \
  p*  e*             t*[end]
  |
  l*
 / \
e* y*
[end][end]

* = node, [end] = end-of-word marker
```

**Node design — two approaches:**

```java
// Approach 1: Fixed-size array (fast, memory-heavy)
class TrieNode {
    TrieNode[] children = new TrieNode[26]; // a-z
    boolean isEnd;
}
// Memory: 26 * 8 bytes per node = 208 bytes even if most children null

// Approach 2: HashMap (memory-efficient, slightly slower)
class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isEnd;
}
// Memory: proportional to actual children count
```

**Insert "apple":**

```
root -> a -> p -> p -> l -> e (mark isEnd=true)
Each level: if child for character doesn't exist, create it; else follow it
Time: O(len("apple")) = O(5)
```

**Search "app" (exact):** Follow a→p→p. Is last node's `isEnd = true`? No (only "apple"/"apply"/"apply" end beyond here) → "app" is NOT a stored word but IS a prefix.

**startsWith("app"):** Follow a→p→p. Reached without null pointer → "app" IS a prefix. O(3).

**Complexity:**

| Operation | Time | Space |
|---|---|---|
| insert | O(L) | O(L × Σ) per word worst case |
| search (exact) | O(L) | — |
| startsWith (prefix) | O(L) | — |
| delete | O(L) | — |
| Total space | — | O(n × L) worst case, better with shared prefixes |

### ❓ Why Does This Exist (Why Before What)

WITHOUT Trie (using HashSet/HashMap for string storage):

- `startsWith("pre")`: must scan ALL stored strings — O(n × L) total.
- Autocomplete: must scan all words to find those starting with prefix — O(n × L).
- IP longest prefix matching with 500k routes: O(n) scan per packet → too slow.

What breaks without it:
1. DNS resolver/ router with 500k routes: O(500k) lookup per packet = unusable.
2. Autocomplete with 1M words: O(1M × avg_length) per keystroke = unacceptable.

WITH Trie:
→ Prefix check in O(L) — no scan of other strings.
→ Autocomplete: follow prefix path in O(L), then collect all words below: O(results).
→ IP routing: longest prefix match in O(32) for IPv4 (32-bit addresses).

### 🧠 Mental Model / Analogy

> A trie is like a printed dictionary organised by letters. "Apple," "application," and "apply" all share the "appl" section. If you want all words starting with "appl," you flip to the "appl" page and list everything on that page and beyond — you don't scan from page 1. The shared prefix path is the page number; the depth is the specificity of the prefix.

"Dictionary section" = trie subtree, "flipping to the right page" = following prefix path, "listing everything on that page" = DFS from the prefix node.

### ⚙️ How It Works (Mechanism)

**Autocomplete implementation:**

```
Trie with: ["apple", "app", "apply", "banana"]

Query: startsWith("app") → returns ["app", "apple", "apply"]

1. Navigate to node for "app": root→a→p→p
2. DFS from this node, collect all isEnd=true paths:
   - "app" node: isEnd=true → collect "app"
   - →l→e: isEnd=true → collect "apple"
   - →l→y: isEnd=true → collect "apply"
Time: O(L + results) = very fast for prefix queries
```

**Compressed trie (PATRICIA trie / radix tree):**

For memory efficiency, compress chains of single-child nodes into single edges labeled with the full substring. The compressed trie for {apple, application} stores "appl" as a single edge, branching at 'e' vs 'ic'.

### 🔄 How It Connects (Mini-Map)

```
HashMap (string storage, O(L) exact match only)
        ↓ prefix operations needed
Trie ← you are here
  (O(L) insert/search/prefix; shared prefix compression)
        ↓ compressed variant
Radix Tree / PATRICIA Trie (IP routing, fewer nodes)
        ↓ used in
Autocomplete | Spell Check | IP Routing (LPM)
Word Search | String Matching | T9 Predictive Text
```

### 💻 Code Example

Example 1 — Standard trie implementation:

```java
class Trie {
    private static class Node {
        Node[] children = new Node[26];
        boolean isEnd;
    }

    private final Node root = new Node();

    public void insert(String word) {
        Node node = root;
        for (char c : word.toCharArray()) {
            int idx = c - 'a';
            if (node.children[idx] == null)
                node.children[idx] = new Node();
            node = node.children[idx];
        }
        node.isEnd = true;
    }

    public boolean search(String word) {
        Node node = findNode(word);
        return node != null && node.isEnd;
    }

    public boolean startsWith(String prefix) {
        return findNode(prefix) != null;
    }

    private Node findNode(String s) {
        Node node = root;
        for (char c : s.toCharArray()) {
            int idx = c - 'a';
            if (node.children[idx] == null) return null;
            node = node.children[idx];
        }
        return node;
    }
}
```

Example 2 — Autocomplete (all words with prefix):

```java
public List<String> autocomplete(String prefix) {
    Node node = findNode(prefix);
    if (node == null) return Collections.emptyList();

    List<String> results = new ArrayList<>();
    dfs(node, new StringBuilder(prefix), results);
    return results;
}

private void dfs(Node node, StringBuilder path,
                  List<String> results) {
    if (node.isEnd) results.add(path.toString());
    for (int i = 0; i < 26; i++) {
        if (node.children[i] != null) {
            path.append((char)('a' + i));
            dfs(node.children[i], path, results);
            path.deleteCharAt(path.length() - 1);
        }
    }
}
```

Example 3 — Word Search II (LeetCode 212) using Trie for pruning:

```java
// Search grid for multiple words from a dictionary
// Trie enables pruning: if no word starts with current path, stop
void solve(char[][] board, Trie trie, int i, int j,
           TrieNode node, StringBuilder path,
           List<String> result) {
    char c = board[i][j];
    TrieNode next = node.children[c - 'a'];
    if (next == null) return; // no word starts with this prefix → prune!

    path.append(c);
    board[i][j] = '#'; // mark visited

    if (next.isEnd) result.add(path.toString());

    // Explore 4 directions
    int[] dr = {0,0,1,-1}, dc = {1,-1,0,0};
    for (int d = 0; d < 4; d++) {
        int ni = i + dr[d], nj = j + dc[d];
        if (ni>=0 && ni<board.length &&
            nj>=0 && nj<board[0].length &&
            board[ni][nj] != '#') {
            solve(board, trie, ni, nj, next, path, result);
        }
    }

    board[i][j] = c; // restore
    path.deleteCharAt(path.length() - 1);
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Trie always uses less memory than HashMap/HashSet | For sparse dictionaries with heterogeneous prefixes, the 26-pointer array per node wastes far more memory than a HashMap storing only existing strings. Use HashMap children for sparse alphabets. |
| Trie is faster than HashMap for exact string lookup | For exact lookup, HashMap O(L) with good hash is comparable to Trie O(L). Trie's advantage is O(L) prefix operations — exact lookup is not uniquely better. |
| Trie nodes store characters | Edges represent characters; nodes represent the state after consuming a prefix of characters. The root represents the empty string. |
| Tries only work for alphabetic strings | Tries work for any discrete alphabet: binary (IP routing), Unicode, DNA sequences, file system paths. |
| A trie with n words has exactly n × L nodes | Shared prefixes reduce total nodes significantly. In the worst case (no shared prefixes) it's n × L; in the best case (all words share a root prefix), it approaches L_max + diverging suffixes. |

### 🔥 Pitfalls in Production

**1. Using Array-Based Trie for Non-English Characters**

```java
// BAD: Fixed 26-slot array for Unicode input
class TrieNode { TrieNode[] children = new TrieNode[26]; }
// index = c - 'a' → fails for 'À', '中', emoji!

// GOOD: HashMap children for non-ASCII or variable alphabet
class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
}
// Or for IP routing: int[2] children for binary trie
```

**2. Memory Explosion with Sparse Word Sets**

```java
// BAD: 26-pointer array for storing 100 long unique words
// 100 words × 10 chars = 1000 nodes × 26 × 8 bytes = 208 KB
// for just 100 words! (normal would be ~100 × 10 = 1 KB)

// GOOD: HashMap-based children or use compressed trie
// Or: for large datasets, consider compressed radix tries
```

**3. Thread Safety — Shared Trie Without Synchronisation**

```java
// BAD: Shared mutable Trie in concurrent context
Trie globalTrie = new Trie(); // shared across threads
threads.forEach(t -> t.setTrie(globalTrie));
// Concurrent inserts → race condition on node creation

// GOOD: Build trie once (immutable after build), read concurrently
// Or: use read-write lock for concurrent insert + search
ReadWriteLock lock = new ReentrantReadWriteLock();
// insert: lock.writeLock(); search: lock.readLock()
```

### 🔗 Related Keywords

- `HashMap` — alternative for exact-match string storage; no prefix support.
- `Array` — the backing storage for each trie node's fixed-alphabet children.
- `DFS` — the traversal algorithm used to enumerate all words with a given prefix.
- `IP Routing (LPM)` — longest-prefix matching uses a binary trie (0/1) for IPv4/IPv6.
- `String Matching` — Aho-Corasick algorithm extends trie with failure links for multi-pattern search.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Prefix-sharing tree: O(L) insert/search/ │
│              │ prefix-check; shared prefixes = space win.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Autocomplete, spell check, IP routing,   │
│              │ word search, prefix counting.             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ No prefix queries needed → HashMap;       │
│              │ non-English chars → use HashMap children; │
│              │ very sparse word set → memory overhead.   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Trie: words sharing a beginning share    │
│              │ a path — prefix queries for free."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Graph → BFS → DFS → Aho-Corasick          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An IP router implementing longest-prefix matching (LPM) uses a binary trie where each bit of the IP address determines left (0) or right (1) at each level. For IPv4 (32 bits), the trie has depth 32. If a routing table has 500,000 routes, compare the memory usage of storing these routes in a sorted array vs. a binary trie, assuming routes are /16 to /32 prefixes with significant prefix sharing (typical for regional allocations). Which structure has better memory efficiency in practice, and what algorithmic benefit does the trie provide that the sorted array cannot?

**Q2.** The Aho-Corasick algorithm extends a trie with "failure links" — pointers from each node to the longest proper suffix of that node's path that is also a prefix in the trie. Describe at a high level how failure links enable O(n + m + z) multi-pattern string matching (n = text length, m = total pattern length, z = matches found), contrasting with naive multi-pattern matching and explaining why simple per-pattern KMP falls short for many simultaneous patterns.

