---
id: RAG-015
title: Re-ranking in RAG (Cross-Encoder, Cohere Rerank)
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★★☆
depends_on: RAG-009, RAG-014
used_by:
related: RAG-018, RAG-023
tags:
  - rag
  - intermediate
  - algorithm
  - production
status: complete
version: 1
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /rag/re-ranking-in-rag-cross-encoder-cohere-rerank/
---

# RAG-015 - Re-ranking in RAG (Cross-Encoder, Cohere Rerank)

⚡ **TL;DR —** Re-ranking is a two-stage pipeline: fast ANN retrieval gets top-50 candidates, then a cross-encoder re-scores each candidate with full query-document attention, promoting the genuinely most relevant results to the top-5.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | RAG-009, RAG-014 |
| **Used by**    | —                |
| **Related**    | RAG-018, RAG-023 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Vector similarity search (ANN) retrieves top-K documents based on embedding cosine similarity. But embeddings are computed independently — the query and document are encoded separately with no knowledge of each other. This bi-encoder approach is fast but loses the fine-grained relevance signal that comes from joint query-document attention.

**THE BREAKING POINT:**
In practice, the 5th most relevant document in a retrieved set of 50 is often more relevant than the 1st. A query like "how do I cancel my subscription without losing data?" may retrieve documents about cancellation (semantically close) at rank 1, while the actual answer ("cancel via Settings > Account > Delete Account, data exported automatically") sits at rank 15 because the embedding doesn't capture the "without losing data" nuance.

**THE INVENTION MOMENT:**
Cross-encoders (Nogueira & Cho, 2019) process the query and document together in a single forward pass through a transformer: `[CLS] query [SEP] document [SEP]`. The attention mechanism can attend across the full query-document pair, producing a relevance score that is far more accurate than bi-encoder similarity. The cost: one forward pass per (query, document) pair.

**EVOLUTION:**
Two-stage retrieval (bi-encoder + cross-encoder) became the standard RAG pattern. Cohere (2023) released a managed Rerank API that abstracts cross-encoder inference. `sentence-transformers` provides open-source cross-encoder models (`ms-marco-MiniLM-L-12-v2`). Flash Rank (2024) offers sub-millisecond re-ranking with tiny distilled models.

---

### 📘 Textbook Definition

**Re-ranking** is a post-retrieval step that scores the retrieved candidate set using a cross-encoder model, which processes the full query-document pair together through a transformer. Unlike the bi-encoder (embedding model) used in retrieval, the cross-encoder uses bidirectional attention across the full query-document pair, producing a more accurate relevance score at the cost of higher per-document latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Retrieval is about recall; re-ranking is about precision — first cast a wide net, then carefully pick the best.

> _Hiring analogy: a recruiter (bi-encoder) screens 500 CVs and shortlists 50 promising candidates quickly. A panel interview (cross-encoder) evaluates the 50 in depth and identifies the best 5. The recruiter is fast but imprecise; the panel is slow but accurate. You use both._

**One insight:** Cross-encoders are typically 5-10x more accurate than bi-encoders for relevance ranking — but 100x slower per document. The two-stage design gets both: bi-encoder speed for recall, cross-encoder accuracy for precision.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Bi-encoder: `score = cosine(embed(query), embed(doc))`. Query and doc are embedded independently. Fast (O(1) at query time after indexing), but loses cross-term attention.
2. Cross-encoder: `score = model([CLS] query [SEP] doc [SEP])`. Processes both together. Accurate (full attention), but must run one forward pass per doc at query time (O(n) per query).
3. Two-stage design: use bi-encoder for top-50 recall, cross-encoder for top-5 precision. Total latency = ANN search time + (50 x cross-encoder inference time).

**THE TRADE-OFFS:**
Gain: significantly higher precision (top-5 quality). At 50 candidates x 10ms per cross-encoder pass: 500ms extra latency. Cost is latency + inference compute (can use GPU or Cohere API to manage this).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** The computation needed for joint query-document attention is irreducibly more expensive than independent encoding.
- **Accidental:** Running your own cross-encoder inference server — Cohere Rerank API and FlashRank eliminate this for most teams.

---

### 🧪 Thought Experiment

You search for "Python async exception handling best practices." ANN retrieves 20 documents:

- Rank 1: "Python async programming guide" (embedding is close to query)
- Rank 7: "Handling exceptions in asyncio tasks" (exact answer)
- Rank 11: "Best practices for Python error handling" (relevant but not async-specific)

The bi-encoder ranks "async programming guide" first because it's semantically similar. The cross-encoder reads the actual query "async exception handling" and compares it word-by-word with each document — it correctly scores rank 7 ("exceptions in asyncio tasks") highest because it contains the exact required concepts together.

The insight: relevance is a joint property of the query AND document — you cannot compute it accurately without attending to both simultaneously.

---

### 🧠 Mental Model / Analogy

> _Re-ranking is spell-checking with context. A spell-checker (bi-encoder) quickly finds words that look similar. A human proofreader (cross-encoder) reads the sentence as a whole and corrects the word that is wrong in context — a different (and more accurate) operation._

- Spell-checker = bi-encoder (fast, context-free similarity)
- Proofreader = cross-encoder (slow, full context attention)
- Two-pass editing = two-stage retrieve + re-rank

Where this analogy breaks down: a proofreader improves text; a cross-encoder only scores — it does not modify retrieved documents. Re-ranking is scoring, not generation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
After the AI retrieves 50 candidate documents, re-ranking carefully re-reads each one alongside the question and scores it more accurately, then returns only the best 5.

**Level 2 - How to use it (junior developer):**
With Cohere: pass the query and list of retrieved docs to `co.rerank(model="rerank-english-v3.0", query=q, documents=docs, top_n=5)`. With sentence-transformers: `CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2").predict([(q, doc) for doc in docs])`.

**Level 3 - How it works (mid-level engineer):**
The cross-encoder tokenises `[CLS] query [SEP] document [SEP]` and runs it through a BERT-like transformer. The `[CLS]` token output is passed through a linear layer to produce a relevance score. For re-ranking 50 candidates: 50 forward passes, each ~10-50ms on CPU (faster on GPU). The scores are then sorted and the top-N returned. No new information is added to the document; only the ordering changes.

**Level 4 - Why it was designed this way (senior/staff):**
Cross-encoder accuracy comes from the interaction between query and document tokens during self-attention. In a bi-encoder, the query can only interact with document tokens indirectly through the shared vector space. In a cross-encoder, every query token can attend to every document token — this captures complex relevance signals like negation ("how to cancel WITHOUT losing data"), specificity ("asyncio" vs generic Python), and conditional relationships. The per-document cost is unavoidable given the architecture; the two-stage design is the practical compromise.

**Expert Thinking Cues:**

- "Re-rank over a larger candidate set (top-100 instead of top-10) for better recall at the retrieval stage, then compress to top-5 with the cross-encoder."
- "Use FlashRank for sub-millisecond re-ranking when cross-encoder latency is a bottleneck — it uses tiny distilled models acceptable for non-critical ranking."

---

### ⚙️ How It Works (Mechanism)

```
Query: "async exception handling Python"

Stage 1 - Bi-encoder ANN retrieval:
  embed(query) -> ANN search -> top-50 candidates
  Latency: ~20ms

Stage 2 - Cross-encoder re-ranking:
  For each (query, doc_i) in top-50:
    input = [CLS] query [SEP] doc_i [SEP]
    score_i = bert_encoder(input)[CLS] -> Linear
  Sort by score, return top-5
  Latency: 50 * 15ms = 750ms (CPU) or 50ms (GPU batched)

Final output: 5 best documents (precision-optimised)
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
User Query
  |
  v
Embed query
  |
  v
ANN Search (top-50)     <- Fast recall stage
  |
  v
50 candidate docs       <- YOU ARE HERE
  |
  v
Cross-encoder re-rank   <- Precision stage
(query x 50 docs, parallel)
  |
  v
Top-5 highest-scored docs
  |
  v
LLM context window
```

**FAILURE PATH:** Cross-encoder domain mismatch — model trained on MS MARCO (web search) performs poorly on technical/legal/medical documents. Fix: fine-tune on domain-specific pairs or use a general-purpose model like Cohere Rerank-v3.

**WHAT CHANGES AT SCALE:** GPU batching for cross-encoder inference is critical at scale. Batch 50 candidates in a single GPU forward pass instead of 50 sequential CPU passes. Reduces latency from 750ms to ~50ms.

---

### 💻 Code Example

**BAD — Pure bi-encoder top-5 (imprecise ranking):**

```python
# ANN search returns top-5 by cosine similarity
# Fine for recall, but top-1 may not be most relevant
results = vectorstore.similarity_search(query, k=5)
context = "\n\n".join(r.page_content for r in results)
```

**GOOD — Two-stage: retrieve 50, re-rank to 5:**

```python
import cohere

co = cohere.Client("YOUR_API_KEY")

# Stage 1: broad retrieval (high recall)
candidates = vectorstore.similarity_search(query, k=50)
doc_texts = [c.page_content for c in candidates]

# Stage 2: cross-encoder re-ranking (high precision)
response = co.rerank(
    model="rerank-english-v3.0",
    query=query,
    documents=doc_texts,
    top_n=5,
)

# Map scores back to original documents
reranked = [
    candidates[r.index]
    for r in response.results
]
context = "\n\n".join(r.page_content for r in reranked)
```

**Open-source alternative (sentence-transformers):**

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-12-v2"
)
pairs = [(query, doc.page_content) for doc in candidates]
scores = reranker.predict(pairs)
# Sort by score descending, take top 5
ranked = sorted(
    zip(scores, candidates), reverse=True
)
top5 = [doc for _, doc in ranked[:5]]
```

---

### ⚖️ Comparison Table

|                   | Bi-encoder           | Cross-encoder          | Cohere Rerank        |
| ----------------- | -------------------- | ---------------------- | -------------------- |
| **Latency**       | ~20ms                | ~500ms CPU             | ~200ms API           |
| **Accuracy**      | Good                 | Excellent              | Excellent            |
| **Domain tuning** | Fine-tune embeddings | Fine-tune model        | Managed by Cohere    |
| **Ops overhead**  | Index needed         | GPU recommended        | None (API)           |
| **Cost**          | Embedding API        | Inference cost         | Per-request          |
| **Use for**       | Retrieval (recall)   | Re-ranking (precision) | Re-ranking (managed) |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                    |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Re-ranking replaces retrieval"                | Re-ranking requires a candidate set from retrieval. It is always a second stage. You cannot run a cross-encoder over millions of documents at query time.  |
| "More candidates = better re-ranking"          | Diminishing returns beyond top-100. Cross-encoder time grows linearly with candidates. Top-50 is a good default; top-100 for recall-critical applications. |
| "Cross-encoder models work across all domains" | Models trained on MS MARCO (web search) underperform on medical, legal, or code retrieval. Use domain-specific models or Cohere's multilingual v3.         |
| "Re-ranking adds too much latency"             | GPU batching 50 candidates takes ~50ms. For latency-critical apps, FlashRank provides sub-millisecond re-ranking with small distilled models.              |

---

### 🚨 Failure Modes & Diagnosis

**1. Re-ranker trained on wrong domain**

**Symptom:** After re-ranking, top-1 result is less relevant than before re-ranking. NDCG decreases.

**Diagnostic:**

```python
# Compare pre/post re-ranking quality
for query, expected_doc_id in eval_set:
    raw = retriever.invoke(query)[:5]
    reranked = rerank(query, retriever.invoke(query)[:50])
    pre_score = expected_doc_id in [r.metadata["id"] for r in raw]
    post_score = expected_doc_id in [r.metadata["id"] for r in reranked]
    if pre_score and not post_score:
        print(f"Re-ranking HURTS: {query}")
```

**Fix:** Switch to a domain-specific cross-encoder. Cohere Rerank v3 is generally robust across domains.

---

**2. Re-ranking adds unacceptable latency**

**Symptom:** P99 latency exceeds SLA after adding re-ranking step.

**Diagnostic:**

```python
import time
start = time.perf_counter()
scores = reranker.predict([(q, doc) for doc in candidates])
print(f"Re-rank latency: {time.perf_counter()-start:.3f}s")
# High? -> check batch size, CPU vs GPU, model size
```

**Fix:** Reduce candidate count (top-20 instead of top-50), use GPU batching, or switch to FlashRank's distilled models for latency-sensitive paths.

---

**3. Re-ranker scores all candidates equally low**

**Symptom:** All candidates get scores near 0. Top-5 is effectively random from the candidate set.

**Diagnostic:**

```python
pairs = [(query, doc.page_content) for doc in candidates]
scores = reranker.predict(pairs)
print(f"Score range: {min(scores):.3f} to {max(scores):.3f}")
# Very small range (e.g. 0.001 to 0.003) = model mismatch
```

**Fix:** The cross-encoder model and the document language/domain are mismatched. Try `cross-encoder/ms-marco-electra-base` or Cohere multilingual rerank.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `RAG-009 - Similarity Search` — the bi-encoder ANN step that precedes re-ranking
- `RAG-014 - Hybrid Search` — hybrid retrieval often combined with re-ranking

**Builds On This (learn these next):**

- `RAG-018 - Query Transformation` — complementary recall improvement approach
- `RAG-023 - Advanced Retrieval Techniques` — contextual compression, parent-child retrieval

**Alternatives / Comparisons:**

- `RAG-016 - Metadata Filtering` — precision improvement via structural constraints vs relevance scoring

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Two-stage retrieval: fast ANN    |
|               | + precise cross-encoder scoring  |
+--------------------------------------------------+
| PROBLEM       | Bi-encoder ranks by embedding   |
|               | similarity, not true relevance  |
+--------------------------------------------------+
| KEY INSIGHT   | Cross-encoder attends to full   |
|               | query+doc pair simultaneously   |
+--------------------------------------------------+
| USE WHEN      | Precision matters: top-1 must   |
|               | be the actual best answer       |
+--------------------------------------------------+
| AVOID WHEN    | Latency budget < 50ms and no    |
|               | GPU for cross-encoder batching  |
+--------------------------------------------------+
| TRADE-OFF     | +50-500ms latency for 5-10x     |
|               | better precision                |
+--------------------------------------------------+
| TWO STAGES    | Retrieve top-50, re-rank top-5  |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-018, RAG-023                |
+--------------------------------------------------+
```

**If you remember only 3 things:**

1. Stage 1 (bi-encoder ANN) provides recall. Stage 2 (cross-encoder) provides precision.
2. Cross-encoder processes `[query SEP document]` together — full attention enables accurate scoring.
3. Retrieve top-50, re-rank to top-5. Candidate count and domain match are the key tuning knobs.

**Interview one-liner:** "Re-ranking is a two-stage pipeline: bi-encoder ANN retrieval gets top-50 by embedding similarity, then a cross-encoder re-ranks with full query-document joint attention to identify the genuinely most relevant top-5."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Two-stage filtering is a general optimisation pattern: coarse fast filter to reduce the search space, then fine slow filter on the reduced set. The coarse filter optimises for recall (don't miss valid candidates); the fine filter optimises for precision (rank truly best candidates first).

**Where else this pattern appears:**

- **Database query optimisation:** Index scan (fast, finds candidate rows) + table scan (slower, evaluates full row against complex predicates). Two stages: index for speed, full scan for accuracy.
- **Recommendation systems:** Candidate generation (collaborative filtering, retrieves 1000 candidates) + ranking model (deep neural network scores 1000 → returns 10). Netflix, Spotify, YouTube all use this pattern.
- **Compiler optimisation:** Dead code elimination (fast, removes obvious dead code) + global value numbering (slower, finds redundant expressions in the reduced code). Coarse pass then fine pass.

---

### 💡 The Surprising Truth

Cross-encoders are not new. They were the standard approach to passage re-ranking in TREC evaluations throughout the 2000s. What changed in 2019 (Nogueira & Cho) was fine-tuning BERT as a cross-encoder — which produced a 10x improvement over previous cross-encoders on MS MARCO. The "discovery" of cross-encoders for RAG is really the rediscovery of a 20-year-old retrieval pattern, applied to neural dense retrieval pipelines. This means the academic literature on two-stage ranking (pre-2018) contains many insights about candidate set size, evaluation metrics, and failure modes that the RAG community is currently re-learning.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Your re-ranking pipeline processes 50 candidates per query. Each cross-encoder pass takes 15ms on CPU. At 100 queries/second, you need 5,000 cross-encoder inferences/second. Calculate the GPU count needed and compare against the Cohere Rerank API cost per month.

_Hint:_ GPU batching can process 50 candidates in ~50ms total (not 50x15ms sequentially). Calculate: 100 q/s x 50 candidates = 5000 pairs/s. A single A100 GPU batches ~2000 pairs/s at 15ms/inference. Compare this against Cohere Rerank pricing (per 1k API calls) at 100 q/s x 3600 x 24 = 8.6M calls/day.

**Q2 (Scale):** Your re-ranker achieves 0.85 NDCG@5. Adding hybrid search (RAG-014) improves your candidate recall from 60% to 80%. Does re-ranking benefit more from (a) a better cross-encoder model or (b) better candidate recall? Why?

_Hint:_ Re-ranking can only promote documents that were retrieved. If the correct answer is not in the top-50 candidates, the cross-encoder cannot surface it. Research the concept of "oracle recall" — maximum achievable precision given your retrieval recall. If your candidate recall is 60%, your maximum NDCG@5 is bounded regardless of re-ranker quality.

**Q3 (Design Trade-off):** Should re-ranking happen before or after metadata filtering? Design two architectures: (A) filter then re-rank, (B) re-rank then filter.

_Hint:_ Architecture A reduces cross-encoder candidate count (cheaper) but may miss documents near filter boundaries. Architecture B applies cross-encoder to all candidates (more expensive) then filters by metadata. Consider: if filtering removes 80% of candidates, how does the candidate count change in each architecture, and how does that affect cross-encoder cost and result quality?
