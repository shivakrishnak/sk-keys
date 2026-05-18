---
id: DSA-079
title: Build a Mini Search System - Phase 2 (Ranking and Trie)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-049, DSA-056, DSA-028
used_by: DSA-100
related: DSA-049, DSA-056, DSA-086
tags:
  - project
  - search-system
  - inverted-index
  - trie
  - ranking
  - tf-idf
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 79
permalink: /technical-mastery/dsa/mini-search-phase-2/
---

## TL;DR

Phase 2 extends the Phase 1 inverted index with TF-IDF
ranking and a Trie for prefix autocomplete - transforming
a basic keyword lookup into a ranked, type-ahead search
experience.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-079 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | project, search-system, TF-IDF, Trie, ranking |
| **Prerequisites** | DSA-049, DSA-056, DSA-028 |

---

### The Problem This Solves

Phase 1 returned all documents containing a keyword but
gave no ranking. A search for "java" returning 500 documents
in random order is useless. Phase 2 adds TF-IDF scoring
(relevant documents rank first) and Trie-based autocomplete
(type "jav" and see suggestions before finishing).

---

### The Phase 2 Extensions

**TF-IDF Scoring:**

TF-IDF (Term Frequency - Inverse Document Frequency)
ranks documents by relevance:
- TF(term, doc) = count of term in doc / total words in doc
- IDF(term) = log(total docs / docs containing term)
- Score(term, doc) = TF * IDF

Words appearing in few documents have high IDF (rare =
informative). Words appearing in all documents have low
IDF ("the", "is"). A rare term appearing many times in
a document = high relevance.

**Phase 2 Implementation:**

```java
class SearchSystemV2 {
    // Phase 1: inverted index (term → List of docIds)
    private Map<String, List<Integer>> invertedIndex = new HashMap<>();

    // Phase 2 additions:
    // TF: docId → (term → frequency)
    private Map<Integer, Map<String, Integer>> termFreq = new HashMap<>();
    // Document lengths for TF normalization
    private Map<Integer, Integer> docLength = new HashMap<>();
    // Total document count for IDF
    private int totalDocs = 0;
    // Autocomplete Trie
    private Trie autocompleteTrie = new Trie();

    void index(int docId, String content) {
        String[] words = content.toLowerCase().split("\\W+");
        docLength.put(docId, words.length);
        Map<String, Integer> freq = new HashMap<>();
        for (String word : words) {
            freq.merge(word, 1, Integer::sum);
            invertedIndex.computeIfAbsent(word,
                k -> new ArrayList<>()).add(docId);
            autocompleteTrie.insert(word); // for autocomplete
        }
        termFreq.put(docId, freq);
        totalDocs++;
    }

    // Ranked search: O(k log k) where k = matching docs
    List<int[]> search(String term) {
        List<Integer> docs = invertedIndex.getOrDefault(
            term, Collections.emptyList());

        double idf = Math.log(
            (double) totalDocs / (docs.size() + 1)
        );

        // Score each document
        PriorityQueue<double[]> heap = new PriorityQueue<>(
            Comparator.comparingDouble(a -> -a[1]) // max-heap
        );
        for (int docId : docs) {
            int tf = termFreq.get(docId).getOrDefault(term, 0);
            int len = docLength.get(docId);
            double score = ((double) tf / len) * idf;
            heap.offer(new double[]{docId, score});
        }

        // Return top-10 ranked results
        List<int[]> results = new ArrayList<>();
        for (int i = 0; i < 10 && !heap.isEmpty(); i++) {
            double[] entry = heap.poll();
            results.add(new int[]{(int)entry[0]});
        }
        return results;
    }

    // Autocomplete: O(k) where k = prefix length
    List<String> autocomplete(String prefix) {
        return autocompleteTrie.autocomplete(prefix);
    }
}
```

---

### What Phase 2 Adds vs Phase 1

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Result ranking | None (arbitrary) | TF-IDF score |
| Autocomplete | None | Trie prefix search |
| Query time | O(1) lookup | O(k) autocomplete + O(k log k) rank |
| Space | O(n*k) inverted index | + O(n*k) Trie + TF freq maps |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "TF-IDF is how Google works" | Google uses TF-IDF as one signal among hundreds; PageRank, anchor text, query context, and user behavior data dominate |
| "Trie and inverted index serve the same purpose" | Trie serves prefix autocomplete (incomplete queries). Inverted index serves full-word lookup (complete queries). Both are needed |

---

### Failure Modes & Diagnosis

**Failure: Autocomplete returns too many results slowly**
- Cause: DFS from prefix node visits all descendants;
  for popular prefixes this is O(total_words)
- Fix: Store precomputed top-K suggestions at each Trie
  node, updated incrementally on new document indexing

---

### Quick Reference Card

| Phase | Key Addition | Data Structure |
|-------|-------------|---------------|
| Phase 1 | Full-word lookup | Inverted Index |
| Phase 2 | Ranked results | TF-IDF + min-heap |
| Phase 2 | Prefix autocomplete | Trie |
| Phase 3 (DSA-100) | Production scale | Distributed index |

---

### Mastery Checklist

- [ ] Can explain TF-IDF scoring intuitively
- [ ] Integrates Trie with inverted index for autocomplete
- [ ] Implements TF normalization correctly

---

### Interview Deep-Dive

**Q1 (Hard):** Design an autocomplete system for a search
engine. When a user types, return the top 3 most searched
completions for their prefix.

> Data structures: Trie for prefix traversal + HashMap
> for query frequency counts.
> Index: for each query string, store in Trie AND increment
> its frequency in a HashMap.
> Query: traverse Trie to prefix node in O(k). DFS from
> that node, collecting all completions. Use min-heap
> of size 3 to track top-3 by frequency. O(k + output).
> Optimization: cache top-3 at each Trie node. Update
> cache on every new query (propagate up the path).
> Query then becomes O(k) always.
> Scale: shard Trie by first letter; replicate for reads.
