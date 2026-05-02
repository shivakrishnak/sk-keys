---
layout: default
title: "Trie"
parent: "Data Structures & Algorithms"
nav_order: 39
permalink: /dsa/trie/
number: "0039"
category: Data Structures & Algorithms
difficulty: ★★☆
depends_on: HashMap, Array
used_by: String Matching (KMP, Rabin-Karp), Prefix Search
related: HashMap, Radix Tree, Aho-Corasick
tags:
  - datastructure
  - intermediate
  - algorithm
  - performance
---

# 039 — Trie

⚡ TL;DR — A Trie stores strings by their shared prefixes, enabling O(L) lookup and prefix search impossible to do this efficiently with a HashMap.

| #039 | Category: Data Structures & Algorithms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HashMap, Array | |
| **Used by:** | String Matching (KMP, Rabin-Karp), Prefix Search | |
| **Related:** | HashMap, Radix Tree, Aho-Corasick | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You are building an autocomplete feature for a search engine. A user types "prog" and you must instantly return all words starting with "prog": "program", "programming", "progress", "programmer". You have 1 million words in a HashMap. Prefix search requires scanning all 1 million entries and checking if each starts with "prog" — O(N) per keystroke, and users type fast.

**THE BREAKING POINT:**
A HashMap finds an exact key in O(1) — but it has no concept of "starts with" because keys with the same prefix are scattered across buckets. Prefix search requires either O(N) full scan or sorting (O(N log N) rebuild, O(log N + K) query with TreeMap). Neither is fast enough for real-time autocomplete at scale.

**THE INVENTION MOMENT:**
If you store words letter-by-letter in a tree where each level represents one character position, then all words sharing a prefix share a tree path. "prog" navigates to a single node from which all descendants are words with that prefix. This is exactly why the Trie was created.

---

### 📘 Textbook Definition

A **Trie** (also called a prefix tree or digital tree) is a multiway tree data structure for storing strings where each node represents one character of a key. The path from root to any node spells a prefix; a "terminal" flag at a node indicates a complete word. Insert, search, and prefix-search operations complete in O(L) where L is the length of the key or prefix — independent of the number of stored strings. Nodes typically store child references as an array of 26 (for lowercase alphabet) or a HashMap for sparse alphabets.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A tree where each path from root to a node spells a word's prefix, sharing storage among words with common beginnings.

**One analogy:**
> Think of a paper dictionary. Letters on spine tabs lead you level by level: 'A' on the first tab, 'AP' on the second, 'APP' on the third — all "APP" words share that path. Prefix search means "find the 'PROG' tab and read all words below it."

**One insight:**
Unlike a HashMap, a Trie is not just about retrieving a single key — it is about navigating a *shared prefix tree* where structure encodes relationships between strings. All words with the same prefix physically share the same tree path, making prefix queries a single traversal rather than N individual lookups.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each node represents one character position; the root represents the empty prefix.
2. A node at depth d has exactly the characters at position d for all words with its ancestor path as prefix.
3. A word is "present" when a path from root to a terminal node spells it exactly.

**DERIVED DESIGN:**
Each node has `children[26]` (or a HashMap) for next-character branching. Complexity depends on the branching factor and string length:
- **Insert** "apple": traverse/create nodes for 'a'→'p'→'p'→'l'→'e', mark last as terminal. O(L).
- **Search** "apple": traverse 5 nodes, check terminal flag. O(L).
- **Prefix** "app": traverse 3 nodes, return all descendants via DFS. O(L + K) for K results.
- **Delete**: clear terminal flag (or prune leaf nodes if no children). O(L).

Array children (`children[26]`) vs HashMap children:
- Array: O(1) child lookup per character, but 26 pointers per node even if few children are non-null — wasteful for sparse alphabets.
- HashMap: amortised O(1) lookup, no wasted pointers for empty children, more memory-efficient for large alphabets (e.g., Unicode).

**THE TRADE-OFFS:**
**Gain:** O(L) all operations, O(L + K) prefix enumeration, shared prefix storage.
**Cost:** High memory for dense alphabets with many nodes; slower than HashMap for exact-key lookups due to L comparisons vs 1 hash.

---

### 🧪 Thought Experiment

**SETUP:**
Autocomplete for a dataset of 1,000 words. User has typed "pre" and wants all completions. Alphabet size = 26.

**WHAT HAPPENS WITH HASHMAP:**
For each of 1,000 words: call `word.startsWith("pre")` — O(L) per check, O(N × L) total. At 3 characters typed and 1,000 words of average length 7: ~7,000 comparisons. For 1,000,000 words: 7,000,000 comparisons per keystroke.

**WHAT HAPPENS WITH TRIE:**
Traverse 3 nodes ('p'→'r'→'e'). Collect all words in subtree rooted at 'e' node. If only 20 words start with "pre", only 20 words are visited. Time: O(3 + 20) = O(23) — constant regardless of total dictionary size.

**THE INSIGHT:**
The Trie's structure makes prefix queries output-sensitive: time is proportional to the result size (K), not the total data size (N). This is impossible with a HashMap because it has no structural notion of prefix.

---

### 🧠 Mental Model / Analogy

> A Trie is like a city's street directory organised by address. To find all buildings on "Progress Street", you go to the 'P-R-O-G-R-E-S-S' path in the directory. Every building on that street is a child of the last node — you find them all without scanning the entire city.

- "City directory structure" → trie tree
- "Street path (P→R→O...)" → character-by-character traversal
- "Buildings on the street" → terminal nodes (complete words)
- "Shared address prefix" → shared trie path

Where this analogy breaks down: A city directory is static; a trie can be modified (insert/delete) dynamically while maintaining its structure.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A tree where you spell words letter by letter, and all words sharing a start share the same tree path. Finding all words starting with "pr" means going to the 'p' then 'r' node and collecting everything below.

**Level 2 — How to use it (junior developer):**
Java has no built-in Trie. Implement with a `TrieNode` class: `boolean isEndOfWord; TrieNode[] children = new TrieNode[26]`. `insert(word)`: for each char `c - 'a'`, create child if null, advance. `search(word)`: traverse; return `isEndOfWord` at last char. `startsWith(prefix)`: traverse; return true if path exists.

**Level 3 — How it works (mid-level engineer):**
Children stored as `TrieNode[26]` — index is `ch - 'a'`. Memory per node: 26 references × 8 bytes = 208 bytes per node for empty children array. For Unicode or large alphabets, replace array with `HashMap<Character, TrieNode>`. A compressed trie (Patricia tree/radix tree) collapses single-child chains into edge labels — reduces node count dramatically for sparse dictionaries.

**Level 4 — Why it was designed this way (senior/staff):**
The standard 26-array implementation is a time-space trade-off: array indexing is branchless and cache-friendly (O(1) child access) but wastes ~200 bytes per node for rarely-filled children. Real-world autocomplete systems use **compressed tries** (radix trees) or DAWG (Directed Acyclic Word Graph) which further deduplicate shared suffixes. Linux routing tables use radix-2 tries (binary tries) for IP prefix matching — O(32) lookup for IPv4 regardless of routing table size.

---

### ⚙️ How It Works (Mechanism)

**TrieNode structure:**
```java
class TrieNode {
    TrieNode[] children = new TrieNode[26];
    boolean isEndOfWord;
}
```

**Insert "apple" into empty trie:**
```
root → [a] create, → [p] create, → [p] existing,
      → [l] create, → [e] create, mark isEndOfWord=true
```

**Prefix search "app" — all words starting with "app":**
```
root → a (index 0) → p (index 15) → p (index 15)
Found "app" node → DFS all descendants with isEndOfWord=true
→ returns ["apple", "apply", "approach", ...]
```

┌───────────────────────────────────────────────────────┐
│  Trie storing: "app", "apple", "apply", "apt"         │
│                                                       │
│  root                                                 │
│    └── [a]                                            │
│         └── [p]                                       │
│              ├── [p]★ (app)                           │
│              │    ├── [l]                             │
│              │    │    ├── [e]★ (apple)               │
│              │    │    └── [y]★ (apply)               │
│              └── [t]★ (apt)                           │
│                                                       │
│  ★ = isEndOfWord = true                               │
└───────────────────────────────────────────────────────┘

**Search vs startsWith:**
```java
// search("app") → found node at 'p', isEndOfWord=true → true
// search("ap")  → found node at 'p', isEndOfWord=false → false
// startsWith("ap") → found node at 'p', exists → true
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
User types prefix "prog"
→ Traverse trie: p→r→o→g (O(4) steps)
→ [TRIE ← YOU ARE HERE]
→ DFS from "prog" node to collect all descendants
→ Return completions in O(K) where K = result count
```

**FAILURE PATH:**
```
Too many words share a common prefix
→ DFS returns thousands of completions
→ Response time grows with result set K
→ Fix: limit DFS to first N results; use BFS with bound
```

**WHAT CHANGES AT SCALE:**
A 5-million-word English trie with 26-array nodes uses ~5M × 208 bytes ≈ 1 GB of memory — impractical. Production autocomplete systems use compressed tries (radix trees), DAWG, or suffix arrays with burrows-wheeler transform. Redis's autocomplete feature uses a sorted set of prefix-expanded keys. Elasticsearch uses FST (Finite State Transducers) — a form of minimal DAWG — for 10× memory compression.

---

### 💻 Code Example

**Example 1 — Basic Trie implementation:**
```java
class Trie {
    private TrieNode root = new TrieNode();

    public void insert(String word) {
        TrieNode cur = root;
        for (char c : word.toCharArray()) {
            int i = c - 'a';
            if (cur.children[i] == null)
                cur.children[i] = new TrieNode();
            cur = cur.children[i];
        }
        cur.isEndOfWord = true;
    }

    public boolean search(String word) {
        TrieNode node = findNode(word);
        return node != null && node.isEndOfWord;
    }

    public boolean startsWith(String prefix) {
        return findNode(prefix) != null;
    }

    private TrieNode findNode(String s) {
        TrieNode cur = root;
        for (char c : s.toCharArray()) {
            int i = c - 'a';
            if (cur.children[i] == null) return null;
            cur = cur.children[i];
        }
        return cur;
    }
}
```

**Example 2 — Autocomplete (return all words with prefix):**
```java
List<String> autocomplete(String prefix) {
    TrieNode node = findNode(prefix);
    if (node == null) return List.of();
    List<String> results = new ArrayList<>();
    // DFS from prefix node, collecting endOfWord paths
    dfs(node, new StringBuilder(prefix), results);
    return results;
}

private void dfs(TrieNode node,
                 StringBuilder prefix,
                 List<String> results) {
    if (node.isEndOfWord)
        results.add(prefix.toString());
    for (int i = 0; i < 26; i++) {
        if (node.children[i] != null) {
            prefix.append((char)('a' + i));
            dfs(node.children[i], prefix, results);
            prefix.deleteCharAt(prefix.length() - 1);
        }
    }
}
```

---

### ⚖️ Comparison Table

| Structure | Exact lookup | Prefix search | Memory | Best For |
|---|---|---|---|---|
| **Trie** | O(L) | O(L + K) | High (sparse) | Prefix queries, autocomplete |
| HashMap | O(1) avg | O(N) scan | Medium | Exact key lookup |
| TreeMap | O(log N) | O(log N + K) | Medium | Sorted prefix scan |
| Sorted Array | O(log N) | O(log N + K) | Low | Static dictionary |
| Radix Tree | O(L) | O(L + K) | Low | Memory-efficient trie |

How to choose: Use a Trie when prefix queries are the primary operation. Use a HashMap when only exact lookups are needed. Use a radix tree (PATRICIA trie) when memory is a constraint for large dictionaries.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Trie is always faster than HashMap | For exact single-key lookup, HashMap O(1) often outperforms Trie O(L); Trie wins on prefix operations |
| Tries are only for lowercase letters | Tries work with any alphabet; use HashMap<Character, TrieNode> for Unicode, numbers, or mixed alphabets |
| A Trie automatically uses less memory than storing all strings | Each node uses ~200 bytes for a 26-branch array; a trie can use MORE memory than a HashMap for sparse word sets |
| search() and startsWith() return the same result for exact words | `search("app")` requires `isEndOfWord=true`; `startsWith("app")` only requires the path to exist |

---

### 🚨 Failure Modes & Diagnosis

**1. Memory explosion on large alphabets**

**Symptom:** `OutOfMemoryError` when building a trie for URLs, email addresses, or Unicode strings.

**Root Cause:** Each node allocates `TrieNode[26]` (or [128] for ASCII) even if most children are null. Unicode alphabets (65,536 characters) make this fatal.

**Diagnostic:**
```bash
jmap -histo:live <pid> | grep TrieNode
# Number of TrieNode objects × 208 bytes = approximate trie memory
```

**Fix:** Replace `TrieNode[]` array children with `HashMap<Character, TrieNode>` children for sparse or large alphabets.

**Prevention:** Always profile memory before choosing array vs HashMap children.

---

**2. Case-sensitivity bugs**

**Symptom:** `search("Apple")` returns false after `insert("apple")` — case mismatch.

**Root Cause:** Characters inserted as-is; 'A' → index 65, 'a' → index 97 — different nodes.

**Diagnostic:**
```java
// Quick test: insert lowercase, search mixed case
trie.insert("apple");
System.out.println(trie.search("Apple")); // false if case-sensitive
```

**Fix:**
```java
// Normalize at insert and search:
word = word.toLowerCase();
```

**Prevention:** Normalise all strings to lowercase (or chosen case) at both insert and search boundaries.

---

**3. Missing limit on autocomplete results**

**Symptom:** Autocomplete for a single-character prefix returns millions of results, causing response timeout.

**Root Cause:** DFS over trie from root-level node returns all words starting with that character — potentially millions.

**Diagnostic:**
```bash
# Measure DFS duration for short prefixes:
long start = System.nanoTime();
autocomplete("a");
System.out.println(System.nanoTime() - start + "ns");
```

**Fix:**
```java
// Add an early-exit limit to DFS
private void dfs(TrieNode node, StringBuilder prefix,
                 List<String> results, int limit) {
    if (results.size() >= limit) return;
    // ...rest of DFS
}
```

**Prevention:** Always add a results limit to autocomplete DFS; common default is 10–20 suggestions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `HashMap` — alternative to the children array in trie nodes; essential for sparse or large alphabets.
- `Array` — the standard backing store for children in a fixed-alphabet trie.

**Builds On This (learn these next):**
- `String Matching (KMP, Rabin-Karp)` — Aho-Corasick (multi-pattern matching) is built on a trie with failure links.
- `Radix Tree / Compressed Trie` — a memory-optimised variant of the trie.

**Alternatives / Comparisons:**
- `HashMap` — O(1) exact lookup but O(N) prefix search; use when prefix queries are not needed.
- `TreeMap` — O(log N) prefix scan via `subMap`; simpler but slower than a trie for large dictionaries.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Prefix tree: each node = one character;   │
│              │ shared prefixes share tree paths          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HashMap cannot answer "all keys starting  │
│ SOLVES       │ with X" faster than O(N) scan             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Prefix queries are O(L+K) — output-       │
│              │ sensitive, not input-size sensitive        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Autocomplete, spell check, IP routing,    │
│              │ word games, dictionary prefix search      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Only exact lookups needed (use HashMap);  │
│              │ memory is tight with large alphabet       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(L+K) prefix power vs high memory usage  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A tree where every branch is a letter    │
│              │  and every path is a word"                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HashMap → String Matching → Bloom Filter  │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A spell checker must find all dictionary words within edit distance 1 of a user's input (one character added, deleted, or changed). A HashMap checks exact matches in O(1) but cannot find "near misses." A trie allows prefix traversal. Design an algorithm using a trie to find all words within edit distance 1 in O(26L) rather than O(N×L) where N is the dictionary size. What trie traversal technique enables this, and how does the branching factor of 26 replace N in the complexity?

**Q2.** A network router stores 500,000 IP address prefixes (/8 to /32) in a binary trie for longest-prefix matching. Each routing lookup must find the most-specific matching prefix for an incoming packet's destination address. Why is a binary trie (one bit per level, 32 levels for IPv4) preferred over a traditional 256-array trie for IP routing? What is the memory trade-off, and how does the CIDR prefix length distribution in real routing tables affect the practical depth of lookups?

