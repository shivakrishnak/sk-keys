---
id: DSA-049
title: "Build a Mini Search System - Phase 1 (Index and Query)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★☆
depends_on: DSA-014, DSA-019, DSA-020, DSA-027, DSA-043
used_by: DSA-077, DSA-100
related: DSA-014, DSA-027, DSA-043, DSA-056, DSA-077
tags:
  - project
  - search
  - inverted-index
  - implementation
  - tfidf
  - applied
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/dsa/build-mini-search-system-phase-1/
---

## TL;DR

Build a basic text search system using an inverted index
(HashMap of word → document IDs) - Phase 1: index
documents and query by keyword in O(1) per lookup.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-049 |
| **Difficulty** | ★★☆ Working Level |
| **Category** | Data Structures & Algorithms |
| **Tags** | project, search, inverted-index, applied |
| **Prerequisites** | DSA-014, DSA-019, DSA-020, DSA-027, DSA-043 |

---

### The Problem This Solves

Given 10,000 documents, find all documents containing
a keyword. Linear scan = O(n * doc length). An inverted
index pre-computes which documents contain each word,
reducing search to O(1) hash lookup. This is the core
of every search engine.

---

### What Is an Inverted Index?

**Forward index:** document → list of words it contains.

**Inverted index:** word → list of documents containing it.

The "inversion" makes search efficient:

```
Documents:
  doc1: "java heap memory management"
  doc2: "java garbage collection heap"
  doc3: "python memory management"

Inverted Index:
  "java"       → [doc1, doc2]
  "heap"       → [doc1, doc2]
  "memory"     → [doc1, doc3]
  "management" → [doc1, doc3]
  "garbage"    → [doc2]
  "collection" → [doc2]
  "python"     → [doc3]
```

---

### How It Works

**Phase 1 implementation:**

```java
class MiniSearchEngine {
    // word → set of document IDs
    private Map<String, Set<String>> index = new HashMap<>();

    // INDEX: add a document
    void index(String docId, String content) {
        String[] words = content.toLowerCase()
                                .split("[^a-z0-9]+");
        for (String word : words) {
            if (word.isEmpty()) continue;
            index.computeIfAbsent(word, k -> new HashSet<>())
                 .add(docId);
        }
    }

    // QUERY: single keyword search - O(1)
    Set<String> search(String keyword) {
        return index.getOrDefault(
            keyword.toLowerCase(), Collections.emptySet()
        );
    }

    // QUERY: AND of multiple keywords
    Set<String> searchAll(String... keywords) {
        if (keywords.length == 0) return Collections.emptySet();
        Set<String> result = new HashSet<>(
            search(keywords[0])
        );
        for (int i = 1; i < keywords.length; i++) {
            result.retainAll(search(keywords[i])); // intersection
        }
        return result;
    }

    // QUERY: OR of multiple keywords
    Set<String> searchAny(String... keywords) {
        Set<String> result = new HashSet<>();
        for (String kw : keywords) result.addAll(search(kw));
        return result;
    }
}
```

**Usage:**

```java
MiniSearchEngine engine = new MiniSearchEngine();
engine.index("doc1", "java heap memory management");
engine.index("doc2", "java garbage collection heap");
engine.index("doc3", "python memory management");

engine.search("java");          // {doc1, doc2}
engine.searchAll("java","heap");// {doc1, doc2} AND
engine.searchAny("java","python");// {doc1, doc2, doc3} OR
```

**Time complexity:**
- Index document: O(words in document)
- Single keyword search: O(1) hash lookup
- AND query: O(k * min(result sizes)) where k = keyword count
- Total index space: O(total words across all documents)

---

### What Phase 2 and 3 Will Add

| Phase | Feature | Data Structure |
|-------|---------|----------------|
| Phase 1 | Index + keyword query | HashMap + HashSet |
| Phase 2 | Ranked results (TF-IDF) | Trie + scoring |
| Phase 3 | Distributed, scalable | Sharded index + merge |

---

### Mastery Checklist

- [ ] Can implement an inverted index from scratch
- [ ] Understands AND (intersection) vs OR (union) of
      document sets
- [ ] Can describe the time complexity of index and query

---

### Interview Deep-Dive

**Q1 (Medium):** Design a search engine for 1 million
documents. How does the inverted index scale?

> Build an inverted index: Map<String, List<DocPosting>>
> where DocPosting contains document ID and term frequency.
> Storage: 1M docs * avg 500 unique words = 500M entries.
> At 20 bytes each = 10GB. Fits in memory for a single
> machine, or shard by first letter of word for distributed.
> Query: hash lookup gives posting list in O(1). For AND:
> intersect two sorted posting lists in O(m+n). For ranking:
> score by TF-IDF or BM25. This is how Elasticsearch and
> Solr work at their core - the inverted index is the
> fundamental data structure behind all text search.
