#!/usr/bin/env python3
"""Write RAG-008 through RAG-010 full v3.0 content."""
import pathlib

BASE = pathlib.Path(
    r"c:\ASK\MyWorkspace\sk-keys\dictionary"
    r"\tier-8-artificial-intelligence\RAG-rag-agents-llmops"
)

def w(filename, content):
    fp = BASE / filename
    fp.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"OK: {filename}")

# ── RAG-008 ───────────────────────────────────────────────────────────────
w("RAG-008 - Chunking Strategies for RAG.md", """
---
id: RAG-008
title: Chunking Strategies for RAG
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★☆☆
depends_on: RAG-007
used_by: RAG-010, RAG-019
related: RAG-006, RAG-009
tags:
  - rag
  - foundational
  - first-principles
  - production
status: complete
version: 1
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /rag/chunking-strategies-for-rag/
---

# RAG-008 - Chunking Strategies for RAG

⚡ **TL;DR —** Chunking splits documents into embeddable units — chunk size and strategy are the highest-leverage quality dial in any RAG system, and most teams get it wrong.

| Field | Value |
|-------|-------|
| **Depends on** | RAG-007 |
| **Used by** | RAG-010, RAG-019 |
| **Related** | RAG-006, RAG-009 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer builds a RAG system and embeds entire documents (50-page PDFs) as single vectors. The query "What is the refund policy?" retrieves the entire "Customer Service Handbook" because it contains a refund section — but the LLM receives 50 pages of context, the refund section is on page 43, and the LLM either misses it (lost in the middle) or truncates the input entirely.

**THE BREAKING POINT:**
Two failure modes pull in opposite directions. Too large a chunk: the embedding averages over too much text, diluting the signal. One relevant paragraph in a 10-page chunk makes the chunk embedding similar to many queries, not specifically relevant to the right one. Too small a chunk: the relevant sentence is split from its context. "The refund period is" in chunk A and "30 days for international orders" in chunk B — neither chunk alone answers the question.

**THE INVENTION MOMENT:**
The insight: chunking is a trade-off between embedding specificity (smaller = more focused) and context completeness (larger = more context for the LLM to reason from). The right chunking strategy depends on document structure, query characteristics, and the embedding model's optimal input size.

**EVOLUTION:**
Early RAG systems (2022) used fixed-size character chunks (500 chars). The community quickly discovered sentence-level chunking improved retrieval for well-structured text. Semantic chunking (2023) used embedding similarity between adjacent sentences to find natural topic breaks. Recursive chunking (LangChain's `RecursiveCharacterTextSplitter`) applied hierarchical splitting rules. Research into "parent-child" or "small-to-big" retrieval (2023-2024) emerged: retrieve small chunks for precise matching, return surrounding larger context to the LLM.

---

### 📘 Textbook Definition

**Chunking** in RAG is the process of splitting source documents into discrete text segments (chunks) before embedding and indexing. The chunking strategy determines the granularity of retrieval: each chunk becomes a retrievable unit. Key parameters include chunk size (in tokens or characters), chunk overlap (shared tokens between adjacent chunks to preserve cross-boundary context), and splitting strategy (fixed-size, sentence-boundary, semantic, or recursive).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Chunking decides what a "retrieval unit" is — get it wrong and even a perfect vector database cannot find the right answer.

> *Chunking is like deciding how to index a textbook: one entry per chapter (too coarse — retrieves too much), one entry per sentence (too fine — retrieves too little context), or one entry per section (just right — specific enough to match, complete enough to answer).*

**One insight:** The chunk that gets retrieved must be both specific enough to rank high in similarity search AND complete enough that the LLM can derive the answer from it alone.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. An embedding model produces ONE vector per chunk. All information in the chunk is compressed into that single vector.
2. A chunk that is too large produces an embedding that averages over many topics, becoming vague — it matches many queries poorly instead of one query well.
3. A chunk that is too small produces a precise embedding that may be retrieved correctly, but the LLM lacks sufficient context to derive the answer from it.
4. Chunk overlap (repeating N tokens at the start of the next chunk) reduces the probability that a key fact falls at a chunk boundary and gets split from its context.

**DERIVED DESIGN:**
The optimal chunk strategy: chunks should correspond to a natural unit of information that can be both specifically described by a user query AND completely answered within the chunk. For prose: a paragraph or topic section. For structured data: a Q&A pair. For code: a function or class. There is no universal optimal chunk size — it depends on document structure and query type.

**THE TRADE-OFFS:**
- **Smaller chunks:** Higher embedding precision, lower context completeness, more chunks in the index (higher storage + search cost).
- **Larger chunks:** Lower embedding precision, higher context completeness, fewer chunks (lower storage + search cost).
- **Overlap:** Reduces boundary failures, increases index size and token cost (same content stored twice near boundaries).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
- **Essential:** The fundamental tension between precision (small) and completeness (large) is irreducible. There is no strategy that maximises both simultaneously.
- **Accidental:** Over-engineering chunking with LLM-based semantic splitters before establishing a fixed-size baseline. Always baseline first.

---

### 🧪 Thought Experiment

**SETUP:** A document contains this text: "The standard refund period is 30 days. For international orders, the refund period is 90 days. Processing time is 5-7 business days."

**CHUNK AT 30 TOKENS (too small):**
Chunk A: "The standard refund period is 30 days."
Chunk B: "For international orders, the refund period is 90 days."
Chunk C: "Processing time is 5-7 business days."

Query: "How long does an international refund take?"
Retrieves Chunk B (correct). LLM has only "90 days" — misses the processing time.
Retrieved Chunk B + Chunk C would answer completely, but they may not both be in top-k.

**CHUNK AT 150 TOKENS (appropriate):**
Chunk: "The standard refund period is 30 days. For international orders, the refund period is 90 days. Processing time is 5-7 business days."

Query: "How long does an international refund take?"
Retrieves this chunk. LLM has both pieces of information. Answers: "90 days, with 5-7 days processing time."

**THE INSIGHT:**
Chunking at the natural information unit (a complete policy clause) outperforms arbitrary character splits because it preserves the conceptual completeness that the LLM needs.

---

### 🧠 Mental Model / Analogy

> *Chunking is like cutting a pizza. Too many slices (small chunks): each slice has one topping but you need 5 slices to get a full flavour combination. Too few slices (large chunks): each slice has everything but is awkward to eat (the LLM gets too much context). The right cut size depends on how the pizza will be eaten.*

- Pizza = source document
- Slice = chunk
- Topping combination = complete semantic unit (a complete answer to a likely query)
- Eating = LLM reasoning over retrieved context

Where this analogy breaks down: a pizza has uniform toppings and slicing is straightforward; a document has varying information density — some sections need finer slicing (dense technical content) and some need coarser slicing (narrative prose).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before storing your documents in a RAG system, you cut them into pieces. The way you cut determines what the AI can find. Too small = pieces lack context. Too large = pieces contain too much noise. Good chunking finds the natural breaks in the document (paragraphs, sections).

**Level 2 - How to use it (junior developer):**
Start with `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)` from LangChain. Measure retrieval quality on a test set. If answers are incomplete: increase chunk size or overlap. If wrong documents retrieved: decrease chunk size. Only invest in more complex strategies after measuring the baseline.

**Level 3 - How it works (mid-level engineer):**
Four main strategies: (1) Fixed-size: split at N characters/tokens with overlap. Simple, fast, ignores structure. (2) Sentence-boundary: split at sentence ends. Preserves semantic units but varies chunk size. (3) Recursive: try paragraph, then sentence, then character splits — respects document hierarchy. (4) Semantic: embed adjacent sentences, split where embedding similarity drops (topic change). Most sophisticated, computationally expensive. Parent-child: index small child chunks for retrieval precision, return larger parent chunk to LLM for completeness.

**Level 4 - Why it was designed this way (senior/staff):**
Chunking is an approximation of the "ideal retrieval unit" problem, which has no closed-form solution. The ideal unit is "the smallest text segment that is both uniquely retrievable for a given query class AND sufficient for the LLM to derive the answer." This definition depends on the query distribution (unknown until production) and the LLM's context utilisation pattern (varies by model). Production RAG teams iterate on chunking strategies as a core quality improvement loop, not a one-time setup decision. The right strategy is data-dependent and query-dependent — treat it as a hyperparameter.

**Expert Thinking Cues:**
- "Always compute a baseline with fixed-size 512-token chunks before investing in semantic chunking. The improvement may not be worth the complexity."
- "Parent-child retrieval (LlamaIndex's SentenceWindowNodeParser) is worth evaluating for documents with clear hierarchical structure."
- "Overlap of 10-15% of chunk size is a good starting point. More overlap = more duplicate content in the index."

---

### ⚙️ How It Works (Mechanism)

**FIXED-SIZE CHUNKING:**
Split text every N tokens. Add M token overlap.
```
[......512 tokens......]
              [......512 tokens......]
         ^64 overlap^
```

**SENTENCE-BOUNDARY CHUNKING:**
Split at sentence boundaries (.!?). Group sentences until target size reached.

**RECURSIVE CHUNKING (most common):**
Try to split at `\n\n` (paragraphs). If chunk still too large, split at `\n` (lines). If still too large, split at `. ` (sentences). If still too large, split at ` ` (words).

**SEMANTIC CHUNKING:**
1. Split into individual sentences.
2. Embed each sentence.
3. Calculate cosine similarity between adjacent sentence embeddings.
4. Insert split at positions where similarity drops significantly (topic change).

**PARENT-CHILD RETRIEVAL:**
Index: small chunks (128 tokens) with precise embeddings.
Return to LLM: parent chunk (512 tokens) that contains the matched small chunk.
Result: precision of small chunks for retrieval + completeness of large chunks for generation.

---

### 🔄 The Complete Picture - End-to-End Flow

**CHUNKING IN THE RAG PIPELINE:**
```
Raw Document
  |
  v
Text Extraction (PDF, DOCX, HTML)
  |
  v
[CHUNKING] <- YOU ARE HERE
  Choose strategy:
  - RecursiveCharacterTextSplitter
  - SemanticChunker
  - SentenceWindowSplitter
  |
  v
Chunk List
  [chunk_text, chunk_id, source_metadata]
  |
  v
Embedding Model
  |
  v
Vector DB (indexed)
```

**FAILURE PATH:**
Chunks that straddle a document section boundary (table header in one chunk, table body in another). Chunks that split mid-sentence due to exact character count. Very short chunks (< 50 tokens) with low semantic content.

**WHAT CHANGES AT SCALE:**
At document update scale: incremental chunking (re-chunk only changed documents, not the entire corpus). At domain scale: different chunking strategies per document type (tabular data needs row-level chunking; code needs function-level chunking). At multi-format scale: specialised parsers per format before chunking.

---

### 💻 Code Example

**BAD — Single large chunk per document:**
```python
from langchain.docstore.document import Document

# Anti-pattern: full document as one chunk
chunks = [Document(page_content=full_doc_text)]
# Embedding averages 50 pages into one vector
# LLM receives 50 pages of context
# Both embedding and generation quality suffer
```

**GOOD — Recursive chunking with overlap:**
```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)
import tiktoken

enc = tiktoken.encoding_for_model("text-embedding-3-small")

def token_len(text: str) -> int:
    return len(enc.encode(text))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,       # tokens
    chunk_overlap=64,     # tokens
    length_function=token_len,  # token-based, not chars
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.create_documents(
    texts=[doc_text],
    metadatas=[{"source": doc_filename, "page": page_num}]
)

# Validate chunk quality
for chunk in chunks:
    token_count = token_len(chunk.page_content)
    assert 50 <= token_count <= 600, (
        f"Suspect chunk size: {token_count} tokens"
    )
```

**How to test / verify correctness:**
```python
# Measure retrieval recall on a labeled test set
def measure_recall_at_k(retriever, test_cases, k=5):
    hits = 0
    for query, expected_doc_id in test_cases:
        results = retriever.retrieve(query, k=k)
        retrieved_ids = [r.metadata["source"] for r in results]
        if expected_doc_id in retrieved_ids:
            hits += 1
    recall = hits / len(test_cases)
    print(f"Recall@{k}: {recall:.2%}")
    return recall

# Compare chunking strategies
for strategy_name, retriever in strategies.items():
    print(f"\n{strategy_name}:")
    measure_recall_at_k(retriever, test_cases)
```

---

### ⚖️ Comparison Table

| Strategy | Precision | Completeness | Complexity | Best For |
|---|---|---|---|---|
| **Fixed-size** | Medium | Medium | Low | Baseline, fast iteration |
| **Sentence-boundary** | High | Medium | Low | Well-structured prose |
| **Recursive** | High | High | Low | General purpose (recommended default) |
| **Semantic** | Very High | High | High | Dense technical docs |
| **Parent-child** | Very High | Very High | High | Mixed granularity needs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Smaller chunks always improve retrieval" | Below ~100 tokens, chunks lose context needed for the LLM to derive answers. Precision improves but completeness collapses. |
| "Larger overlap is always better" | Overlap > 20% of chunk size increases index size and cost without proportional recall improvement. |
| "Semantic chunking is always better than fixed-size" | Semantic chunking is slower, more expensive, and not consistently better. Always baseline first. |
| "Chunk size is set once" | Optimal chunk size changes with query distribution, document type, and embedding model. Treat it as a tunable parameter. |

---

### 🚨 Failure Modes & Diagnosis

**1. Answer split across chunk boundary**

**Symptom:** RAG says "I don't know" but the correct answer is in the knowledge base. Manual inspection shows the answer straddles two consecutive chunks.

**Root Cause:** Fixed-size chunking with no overlap split a key fact across chunk boundaries.

**Diagnostic:**
```python
# Find boundary splits
for i in range(len(chunks) - 1):
    if "international" in chunks[i].page_content[-100:]:
        if "90 days" in chunks[i+1].page_content[:100]:
            print(f"BOUNDARY SPLIT at chunk {i}/{i+1}")
            print("Last of chunk:", chunks[i].page_content[-200:])
            print("Start of next:", chunks[i+1].page_content[:200])
```

**Fix:**
BAD: No overlap.
GOOD: Add overlap of 10-15% of chunk size. For 512-token chunks: 64-token overlap. This ensures boundary content appears in both adjacent chunks.

**Prevention:** Run boundary analysis on the document corpus before production deployment.

---

**2. Over-large chunks (embedding dilution)**

**Symptom:** Vector search returns topically relevant documents, but the retrieved chunks are too broad. The LLM cannot identify the specific relevant section.

**Root Cause:** Chunk size too large. A 2048-token chunk about general financial policy includes one sentence about refunds — the embedding is "finance/policy" not "refunds."

**Diagnostic:**
```python
# Check average chunk size
sizes = [token_len(c.page_content) for c in chunks]
import statistics
print(f"Mean: {statistics.mean(sizes):.0f} tokens")
print(f"Max: {max(sizes)} tokens")
print(f"Chunks > 1000 tokens: "
      f"{sum(1 for s in sizes if s > 1000)}")
```

**Fix:**
BAD: 2048-token chunks for varied-topic documents.
GOOD: Reduce to 512 tokens with recursive splitter. Measure retrieval recall before and after.

**Prevention:** Set a maximum chunk size and enforce it at ingestion. Alert on chunks above threshold.

---

**3. Table / structured content destroyed by text splitting**

**Symptom:** Markdown tables, CSV data, or code blocks are split mid-structure. Retrieved "chunks" are partial tables or broken code.

**Root Cause:** Text splitters designed for prose split tables at row boundaries, destroying the structure needed for the LLM to interpret the content.

**Diagnostic:**
```python
# Detect split tables
for chunk in chunks:
    lines = chunk.page_content.split("\n")
    pipe_lines = sum(1 for l in lines if l.strip().startswith("|"))
    if 0 < pipe_lines < 3:
        print(f"Possible split table in chunk: "
              f"{chunk.page_content[:200]}")
```

**Fix:**
BAD: Applying text splitter to raw markdown with tables.
GOOD: Pre-process: extract tables as separate chunks (one table = one chunk, regardless of size). Apply text splitter only to prose sections.

**Prevention:** Use document-structure-aware parsers (Unstructured, LlamaParse) that identify tables, code blocks, and lists before chunking.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `RAG-007 - Embeddings` — what each chunk becomes after chunking

**Builds On This (learn these next):**
- `RAG-010 - RAG Pipeline Basics` — chunking in the full pipeline
- `RAG-019 - Document Parsing and Extraction` — what happens before chunking

**Alternatives / Comparisons:**
- `RAG-014 - Hybrid Search` — chunking quality interacts with BM25 retrieval

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Splitting documents into         |
|               | embeddable retrieval units       |
+--------------------------------------------------+
| PROBLEM       | Too large = vague embeddings;    |
|               | too small = incomplete context   |
+--------------------------------------------------+
| KEY INSIGHT   | Each chunk must be both          |
|               | findable AND self-sufficient     |
+--------------------------------------------------+
| USE WHEN      | Every RAG system (unavoidable)   |
+--------------------------------------------------+
| DEFAULT       | RecursiveCharacterTextSplitter   |
|               | 512 tokens, 64 token overlap     |
+--------------------------------------------------+
| TRADE-OFF     | Precision (small) vs             |
|               | completeness (large)             |
+--------------------------------------------------+
| ONE-LINER     | "Retrieval unit sizing"          |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-010, RAG-014, RAG-019        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Start with 512-token recursive chunks and 64-token overlap as the baseline before trying anything more complex.
2. The chunk must be both specific enough to retrieve correctly AND complete enough for the LLM to answer from it.
3. Tables, code, and structured content need special handling — text splitters destroy structure.

**Interview one-liner:** "Chunking splits documents into retrieval units where each chunk is embedded as one vector — the key trade-off is precision (smaller chunks retrieve more specifically) vs completeness (larger chunks provide more context for generation), balanced at around 256-512 tokens with 10-15% overlap."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The granularity of your retrieval unit determines the precision-completeness trade-off. This principle applies to any retrieval system: database query granularity (row vs aggregated), search index granularity (document vs paragraph vs sentence), and log analysis granularity (raw event vs aggregated metric). Getting granularity right is always a domain-specific calibration problem, not a formula.

**Where else this pattern appears:**
- **Database indexing:** A composite index on (customer_id, order_date) is the "chunk" of a query workload — precise enough to match specific queries, complete enough to serve the full result. Too granular (every column indexed) = index bloat. Too coarse (no index) = full table scan.
- **Search engine inverted indexes:** Documents are segmented into terms (token-level), and relevance scoring (BM25) is computed per term. Phrase queries need adjacent terms — analogous to chunk overlap preserving cross-boundary phrases.
- **Event-driven architecture (Kafka):** Message size is the "chunk" trade-off. Small messages: high precision routing, high overhead per event. Large messages: lower overhead, harder to route precisely. Most systems target 10KB-1MB per message as the practical middle ground.

---

### 💡 The Surprising Truth

The optimal chunk size for RAG is not determined by the embedding model's input capacity — it is determined by the average length of a complete answer in the source documents. If your source documents contain self-contained Q&A pairs, chunking at the Q&A boundary will outperform any fixed-size strategy, regardless of whether that chunk is 50 tokens or 500 tokens. Teams that measure this find that the "right" chunk size for their use case often differs by 5-10x from the common advice of "512 tokens." The universal recommendation of 512 tokens is a reasonable default, not an optimum — and it was reverse-engineered from OpenAI's original ada-002 training context window, not from RAG retrieval experiments.

---

### 🧠 Think About This Before We Continue

**Q1 (Design Trade-off):** You are building a RAG system for a legal contract repository. Contracts have highly hierarchical structure: Part > Section > Clause > Sub-clause. A query might ask about a specific sub-clause, or about how multiple sections interact. Design a chunking strategy that handles both query types.

*Hint:* Think about the parent-child retrieval pattern: you need fine-grained chunks (sub-clause level) for precise retrieval on specific questions, AND coarse-grained chunks (section level) for questions requiring cross-clause context. Consider indexing at sub-clause granularity and returning the parent section to the LLM, OR indexing at both levels and letting the query determine which granularity to use. What metadata do you need to navigate the hierarchy?

**Q2 (Scale):** You have a 10TB document corpus that takes 8 hours to chunk and embed. A user uploads a new document every 30 seconds. Design the incremental update strategy.

*Hint:* Think about the difference between batch re-processing the entire corpus (unacceptable for real-time uploads) and incremental processing (chunk + embed only the new document). Consider the infrastructure required for real-time ingestion: an event-driven pipeline (file upload -> trigger -> chunk -> embed -> insert to vector DB). What is the maximum acceptable delay between upload and searchability? Design for that SLO, not for zero latency.

**Q3 (Root Cause):** After switching from 512-token to 256-token chunks, Recall@5 improved from 0.78 to 0.85, but end-to-end answer quality (measured by human raters) dropped from 0.82 to 0.71. Explain this apparently contradictory result.

*Hint:* Think about what improved (retrieval precision) and what degraded (answer completeness). Smaller chunks retrieve more precisely, so more "correct" chunks appear in top-5. But each chunk now contains less context — the LLM is receiving 5 pieces of a puzzle but each piece is smaller. The LLM may retrieve the right chunk but cannot synthesize a complete answer from it alone. Consider whether the answer quality would recover if top-k is increased from 5 to 10 (to compensate for smaller chunks), and what the latency/cost implications of that trade-off are.
""")

# ── RAG-009 ───────────────────────────────────────────────────────────────
w("RAG-009 - Similarity Search (Cosine, Dot Product, Euclidean).md", """
---
id: RAG-009
title: Similarity Search (Cosine, Dot Product, Euclidean)
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★☆☆
depends_on: RAG-007
used_by: RAG-006, RAG-010
related: RAG-046, DSA-001
tags:
  - rag
  - foundational
  - first-principles
  - algorithm
status: complete
version: 1
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Dictionary"
nav_order: 9
permalink: /rag/similarity-search-cosine-dot-product-euclidean/
---

# RAG-009 - Similarity Search (Cosine, Dot Product, Euclidean)

⚡ **TL;DR —** Three distance metrics for comparing vectors: cosine (angle), dot product (projection), and Euclidean (straight-line distance) — cosine is the default for RAG because it is scale-invariant.

| Field | Value |
|-------|-------|
| **Depends on** | RAG-007 |
| **Used by** | RAG-006, RAG-010 |
| **Related** | RAG-046, DSA-001 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have two vectors representing text and need to measure how similar they are. Without a clear definition of "similar," you pick a metric arbitrarily (Euclidean, because it sounds familiar from geometry). Your RAG system retrieves irrelevant results. Investigation reveals that after L2 normalisation, Euclidean distance and cosine similarity are equivalent — but you had un-normalized vectors, so Euclidean was penalising long documents regardless of semantic content.

**THE BREAKING POINT:**
Using the wrong distance metric causes silent, systematic retrieval failure. A long document about "refund policies" will be retrieved less often than a short document about "refunds" because Euclidean distance penalises the magnitude difference — even if the long document is semantically more relevant.

**THE INVENTION MOMENT:**
Cosine similarity emerged as the standard for text similarity because it measures the angle between vectors, not their magnitude. A long document and a short document about the same topic have different magnitudes (more tokens = larger vector magnitude in some representations) but the same direction. Cosine captures direction. Euclidean captures both direction and magnitude.

**EVOLUTION:**
Early information retrieval (TF-IDF vectors) used cosine similarity. Neural embedding models output dense vectors optimised for cosine similarity (training objective pushes similar pairs to small cosine distance). OpenAI's embedding models explicitly recommend cosine similarity. Dot product emerged as a fast alternative when vectors are L2-normalised (dot product = cosine on unit vectors). FAISS and HNSW support all three; most vector DBs default to cosine.

---

### 📘 Textbook Definition

**Similarity search** is the task of finding vectors in a database most similar to a query vector, measured by a distance or similarity metric. The three standard metrics are: (1) **Cosine similarity** — measures the cosine of the angle between vectors (1 = identical direction, 0 = orthogonal, -1 = opposite); (2) **Dot product** — the sum of element-wise products (equivalent to cosine when vectors are L2-normalised); (3) **Euclidean distance (L2)** — the straight-line distance between vector endpoints in N-dimensional space (lower = more similar).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Cosine measures direction (topic similarity), Euclidean measures distance (must normalize first), dot product is cosine when vectors are unit length.

> *Think of vectors as arrows. Cosine similarity measures whether two arrows point in the same direction, ignoring how long they are. Euclidean distance measures how far apart the arrow tips are. For semantically similar text, direction matters more than length.*

**One insight:** For RAG, always use cosine similarity or dot product on L2-normalized embeddings. Euclidean distance is only valid when you know all vectors have the same magnitude.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Embedding vectors encode semantic direction. Two texts about the same topic produce vectors pointing in similar directions in the high-dimensional space.
2. Vector magnitude (length) reflects the "confidence" or "information density" of the representation, not semantic topic.
3. Cosine similarity captures semantic direction. It is magnitude-invariant.
4. After L2 normalisation (all vectors become unit vectors), cosine similarity and dot product are mathematically equivalent.
5. Euclidean distance conflates direction and magnitude. Only use it for magnitude-normalised vectors.

**DERIVED DESIGN:**
For RAG: use cosine similarity (or dot product on unit-norm vectors). Most embedding APIs return unit-norm vectors by default. Verify: `||embedding|| ≈ 1.0`.

**THE TRADE-OFFS:**
- **Cosine:** Magnitude-invariant (correct for semantic similarity), slightly more compute (normalisation step).
- **Dot product:** Fast (no normalisation in the similarity step), requires pre-normalised vectors.
- **Euclidean:** Intuitive geometry, wrong for unnormalized text embeddings, correct only for magnitude-normalised vectors.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
- **Essential:** The choice of metric matters when vectors are not normalised. The mathematical relationship between the three metrics is real and consequential.
- **Accidental:** Implementing your own similarity function. Every vector database and embedding library provides these — use the built-in implementations.

---

### 🧪 Thought Experiment

**SETUP:** Two documents. Document A: "Refund Policy" (3 sentences). Document B: "Customer Service Handbook - Including Refund Policy, Shipping Policy, and Returns" (30 pages). Both are about the same refund policy. A user queries: "How do I get a refund?"

**WITHOUT L2 NORMALISATION (Euclidean):**
Document B has a vector with larger magnitude (more text = more signal in some models). Euclidean distance between the query vector and Document B is larger than between the query and Document A — even if both are about the same topic. Document A ranks higher. But Document B may contain more relevant information.

**WITH COSINE SIMILARITY:**
Both documents, when their vectors are projected to unit length, point in the same semantic direction (both are about "refund policy"). Cosine similarity scores both equally high. Both are retrieved. The LLM gets the most relevant content.

**THE INSIGHT:**
Document length should not determine retrieval rank. Topic similarity should. Cosine similarity achieves this by normalising out magnitude. This is why it is the standard for text retrieval.

---

### 🧠 Mental Model / Analogy

> *The three metrics are like three ways to judge whether two people are headed to the same destination. Cosine similarity checks if they're walking in the same direction, regardless of how fast or how far they've walked. Euclidean distance checks how far apart they are on the map. Dot product is the combination of both direction and speed in a single number.*

- Walking direction = semantic topic (what the text is about)
- Walking speed / distance = text length / information density (how much content)
- "Same destination" = semantic similarity

Where this analogy breaks down: people walking in the same direction may have different destinations if they eventually diverge; in vector space, two vectors pointing in exactly the same direction are semantically identical (not just "headed the same way").

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When comparing text, we need a way to say "these two pieces of text are about the same thing." Cosine similarity gives a score from 0 (nothing in common) to 1 (same meaning). It looks at the direction of the vectors, not how long they are — so a short summary and a long report about the same topic both get high scores against the same query.

**Level 2 - How to use it (junior developer):**
Use the metric your vector database uses by default. For Chroma, Qdrant, and most others: cosine. For FAISS: choose `faiss.IndexFlatIP` for dot product (fast on unit-norm vectors) or `faiss.IndexFlatL2` for Euclidean. When in doubt: cosine. Verify your embedding vectors are unit-normalised: `assert abs(np.linalg.norm(vec) - 1.0) < 0.01`.

**Level 3 - How it works (mid-level engineer):**
For unit-norm vectors (most embedding models): dot product == cosine. Use dot product for speed (one fewer normalisation step). For unnormalized vectors: cosine requires explicit normalisation, Euclidean gives magnitude-biased results. The mathematical relationship: `cosine(A, B) = dot(A, B) / (||A|| * ||B||)`. After normalisation: `||A|| = ||B|| = 1`, so `cosine(A, B) = dot(A, B)`.

**Level 4 - Why it was designed this way (senior/staff):**
The choice to train embedding models with cosine objective (minimise angular distance between similar pairs) is deliberate. It forces the model to encode semantic similarity into vector direction, not magnitude. This creates a clean separation: magnitude encodes information about the text (confidence, specificity), direction encodes topic. By normalising out magnitude at query time, cosine similarity gives pure topic similarity. This design choice cascades through the entire RAG stack: from embedding training to vector DB configuration to ANN index selection (HNSW with cosine space vs L2 space).

**Expert Thinking Cues:**
- "When you see poor retrieval despite good embedding quality, check your vector DB's distance metric setting. A misconfigured Euclidean distance on unnormalized vectors will produce systematically wrong rankings."
- "For maximum speed in production: pre-normalise all vectors at indexing time, then use dot product at query time. You get cosine semantics at dot product speed."
- "Dot product is the standard metric in FAISS `IndexFlatIP` (IP = Inner Product). It assumes unit-norm vectors. Always normalise before inserting into IP indexes."

---

### ⚙️ How It Works (Mechanism)

**COSINE SIMILARITY:**
$$\text{cosine}(A, B) = \frac{A \cdot B}{\|A\| \|B\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum A_i^2} \cdot \sqrt{\sum B_i^2}}$$

Range: [-1, 1]. For RAG: 1 = identical direction (same topic), 0 = orthogonal (unrelated topics).

**DOT PRODUCT:**
$$A \cdot B = \sum_{i=1}^{n} A_i B_i$$

Range: unbounded. Equivalent to cosine when ||A|| = ||B|| = 1. Faster to compute (no normalisation).

**EUCLIDEAN DISTANCE (L2):**
$$d(A, B) = \sqrt{\sum_{i=1}^{n} (A_i - B_i)^2}$$

Range: [0, infinity). Lower = more similar. Sensitive to vector magnitude.

**RELATIONSHIP:**
For unit-norm vectors: `cosine_similarity(A, B) = dot(A, B)` and `euclidean(A, B)^2 = 2 * (1 - cosine(A, B))`. On unit-norm vectors, all three metrics give the same ranking.

---

### 🔄 The Complete Picture - End-to-End Flow

**SIMILARITY SEARCH IN RAG:**
```
User Query
  |
  v
Embed query -> q_vec (unit norm)
  |
  v
[SIMILARITY SEARCH] <- YOU ARE HERE
  For each stored vector v:
    score = dot(q_vec, v)  # fast, unit norm
  |
  v
Sort by score descending
  |
  v
Return top-k (score, chunk_id)
  |
  v
Fetch chunk text, build prompt
```

**FAILURE PATH:**
Metric mismatch: vectors stored as unit-norm, queried with Euclidean distance. Rankings are incorrect. Vectors stored without normalisation, queried with dot product. Long documents systematically over-ranked.

**WHAT CHANGES AT SCALE:**
At 100M+ vectors, computing exact similarity for all N vectors is O(N) per query. ANN indexes (HNSW, IVF) approximate this search in O(log N) by precomputing a navigable graph structure optimised for the chosen metric. Always configure the ANN index with the same metric you use for training and querying.

---

### 💻 Code Example

**BAD — Using Euclidean on unnormalized vectors:**
```python
import numpy as np

# Documents with different lengths -> different norms
doc_short = np.array([0.5, 0.3, 0.8])  # short doc
doc_long  = np.array([1.5, 0.9, 2.4])  # long doc (3x norm)
query     = np.array([0.4, 0.2, 0.7])

# Euclidean distance penalises the longer vector
d_short = np.linalg.norm(query - doc_short)  # 0.14
d_long  = np.linalg.norm(query - doc_long)   # 1.57
# doc_short ranks higher despite both being about
# the same topic (just different lengths)
print(f"Short: {d_short:.2f}, Long: {d_long:.2f}")
```

**GOOD — Cosine similarity, scale-invariant:**
```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

# L2-normalise for fast dot product (= cosine on unit vecs)
def l2_normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

doc_short = np.array([0.5, 0.3, 0.8])
doc_long  = np.array([1.5, 0.9, 2.4])  # same direction
query     = np.array([0.4, 0.2, 0.7])

# Cosine: doc_long has same direction as doc_short
sim_short = cosine_similarity(query, doc_short)  # 0.99
sim_long  = cosine_similarity(query, doc_long)   # 0.99
# Both rank equally -- correct behavior
print(f"Cosine short: {sim_short:.3f}")
print(f"Cosine long:  {sim_long:.3f}")
```

**How to test / verify correctness:**
```python
def test_metrics_on_known_pairs():
    similar_texts = [
        "The dog ran in the park",
        "A puppy played outside"
    ]
    dissimilar_text = "Quarterly earnings exceeded targets"

    vecs = embed_texts(similar_texts + [dissimilar_text])
    v1, v2, v3 = vecs

    sim_12 = cosine_similarity(np.array(v1), np.array(v2))
    sim_13 = cosine_similarity(np.array(v1), np.array(v3))

    assert sim_12 > 0.7, f"Similar texts: {sim_12:.3f}"
    assert sim_13 < 0.5, f"Different texts: {sim_13:.3f}"
    print(f"Similar pair cosine: {sim_12:.3f}")
    print(f"Different pair cosine: {sim_13:.3f}")
```

---

### ⚖️ Comparison Table

| Metric | Formula | Range | Scale-Invariant | Best For |
|---|---|---|---|---|
| **Cosine** | dot(A,B) / (||A|| ||B||) | [-1, 1] | Yes | Text similarity (default for RAG) |
| **Dot Product** | sum(A_i * B_i) | Unbounded | No (use on unit vecs) | Fast search on unit-norm vectors |
| **Euclidean (L2)** | sqrt(sum((A_i - B_i)^2)) | [0, inf) | No | Geometric space, image embeddings |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Dot product and cosine are different metrics" | On unit-norm vectors, they are mathematically identical. The difference only matters for unnormalized vectors. |
| "Euclidean distance works for text embeddings" | Only if vectors are L2-normalised. Most embedding APIs return unit-norm vectors, making Euclidean and cosine equivalent - but verify first. |
| "Higher cosine score always means more relevant" | Cosine measures semantic direction similarity, not factual correctness or answer quality. A highly similar but factually wrong chunk will score high. |
| "Negative cosine scores mean the vectors are wrong" | Negative cosine is valid for vectors pointing in opposite semantic directions (e.g., positive vs negative sentiment). It is not an error. |

---

### 🚨 Failure Modes & Diagnosis

**1. Wrong metric in vector DB configuration**

**Symptom:** Retrieval rankings are systematically wrong. Manual inspection shows obviously relevant documents ranked low.

**Root Cause:** Vector DB configured with Euclidean distance, but embedding model returns non-unit-norm vectors, causing magnitude to dominate rankings.

**Diagnostic:**
```python
# Check vector norms
import numpy as np
vecs = collection.get(limit=100)["embeddings"]
norms = [np.linalg.norm(v) for v in vecs]
print(f"Mean norm: {np.mean(norms):.4f}")
print(f"Std norm:  {np.std(norms):.4f}")
# If mean != ~1.0 and std > 0.01:
# vectors are not unit-norm
# Euclidean distance will be magnitude-biased
```

**Fix:**
BAD: Using `hnsw:space: l2` in Chroma with unnormalized vectors.
GOOD: Change to `hnsw:space: cosine` OR pre-normalize all vectors with L2 normalisation before insertion.

**Prevention:** Always verify vector norms after embedding. Assert `abs(norm - 1.0) < 0.05` before inserting.

---

**2. Metric mismatch at index build vs query time**

**Symptom:** Query scores are nonsensical (very high for irrelevant documents, very low for relevant ones).

**Root Cause:** FAISS index built with L2 distance, but queries use inner product (or vice versa). The ANN search returns approximately-nearest by the wrong metric.

**Diagnostic:**
```python
import faiss
# Check index type
index = faiss.read_index("my_index.faiss")
print(type(index))
# faiss.IndexFlatL2 -> L2 distance
# faiss.IndexFlatIP -> inner product (dot product)
# Mismatch with your query metric = wrong results
```

**Fix:**
BAD: Building index with `IndexFlatL2`, then interpreting scores as cosine similarity.
GOOD: Use `IndexFlatIP` for dot product (unit-norm vectors). Distances returned are dot product scores (0 to 1 for unit-norm, 1 = identical).

**Prevention:** Document the metric used for every vector index. Assert the metric at query time.

---

**3. Symmetric semantic similarity (false positives)**

**Symptom:** Query "What is the refund DEADLINE?" retrieves chunks about "What is the refund AMOUNT?" Cosine similarity is high because both are about refunds.

**Root Cause:** Cosine similarity is topic-level. It cannot distinguish between different aspects of the same topic.

**Diagnostic:**
```python
# Check score distribution for a known case
results = vector_db.query(query_vec, k=10)
for r in results:
    print(f"Score: {r.score:.3f} | {r.text[:100]}")
# If all top-10 results are about "refunds" but
# only 2 answer the specific question -> topic-level
# retrieval is working, subtopic is not
```

**Fix:**
BAD: Relying only on cosine similarity for high-precision retrieval.
GOOD: Add re-ranking (cross-encoder) as a second stage: cosine similarity finds the relevant topic region, cross-encoder re-ranks by answer relevance to the specific query.

**Prevention:** For high-precision use cases, always add a re-ranking step after cosine retrieval.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `RAG-007 - Embeddings` — the vectors being compared

**Builds On This (learn these next):**
- `RAG-006 - Vector Databases` — systems implementing ANN similarity search
- `RAG-046 - Vector Index Algorithm Research` — HNSW and IVF internals

**Alternatives / Comparisons:**
- `RAG-014 - Hybrid Search` — combining vector similarity with BM25 keyword similarity

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Three metrics for comparing      |
|               | vectors: cosine, dot, euclidean  |
+--------------------------------------------------+
| PROBLEM       | Wrong metric -> wrong rankings   |
|               | (magnitude vs direction bias)    |
+--------------------------------------------------+
| KEY INSIGHT   | Cosine is scale-invariant:       |
|               | measures direction, not length   |
+--------------------------------------------------+
| DEFAULT       | Cosine for RAG. Dot product      |
|               | on pre-normalised vectors = fast |
+--------------------------------------------------+
| AVOID         | Euclidean on unnormalized text   |
|               | embedding vectors                |
+--------------------------------------------------+
| TRADE-OFF     | Cosine (correct, slightly slower)|
|               | vs dot product (fast, needs norm)|
+--------------------------------------------------+
| ONE-LINER     | "Use cosine; it ignores length"  |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-006, RAG-014, RAG-046        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Use cosine similarity for text vector comparison — it is scale-invariant and measures semantic direction.
2. Dot product equals cosine similarity when vectors are L2-normalised (most embedding APIs return unit-norm vectors).
3. Verify your vector norms before choosing a metric — unnormalized vectors with Euclidean distance produce silently wrong rankings.

**Interview one-liner:** "Cosine similarity is the standard RAG metric because it measures the angle between embedding vectors (semantic direction), ignoring magnitude — making it length-invariant; dot product equals cosine on unit-norm vectors and is faster; Euclidean distance is only appropriate when vectors are normalised."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When comparing objects, choose a metric that captures the aspect of similarity that matters for your application. Length-invariant comparison (direction, proportion, relative structure) is often more semantically meaningful than absolute distance. This principle applies across domains.

**Where else this pattern appears:**
- **Financial ratio analysis:** Comparing companies by profit margin (percentage, direction-like) is more meaningful than comparing by absolute profit (magnitude-like). A startup with 40% margin is more similar to a large tech company with 40% margin than to another startup with $1M absolute profit.
- **Statistical correlation (Pearson's r):** Pearson correlation measures the direction of the linear relationship between variables, ignoring scale. A company's stock price and a market index may move in the same direction (high correlation) regardless of whether the stock is $5 or $500.
- **Cosine similarity in recommendation systems:** User preference vectors are compared by direction (similar preference patterns) not magnitude (one user rated 1,000 movies, another rated 10 — magnitude difference doesn't change the preference similarity).

---

### 💡 The Surprising Truth

Cosine similarity can be fooled by what is called the "hubness problem" in high-dimensional spaces. In very high dimensions (1536+), certain vectors tend to appear as nearest neighbors for a disproportionate fraction of queries, regardless of true semantic similarity — simply because the geometry of high-dimensional spaces makes some points "hubs" that are close to everything. Studies on text embeddings have found that 5-10% of embedding vectors in a large corpus account for 30-50% of all nearest-neighbor results. These "hubs" are semantically generic text (common phrases, transitional sentences) that end up near the center of the semantic space. The practical implication: maximum marginal relevance (MMR) re-ranking, which penalises redundancy, often improves RAG answer quality more than tuning the similarity metric itself.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** For unit-norm vectors, cosine similarity and dot product are identical. For non-unit-norm vectors, they differ. Design an experiment to determine empirically whether your embedding model returns unit-norm vectors, and describe what you would do if it does not.

*Hint:* Think about what "unit norm" means: `||v|| = 1.0`. Generate 100 embeddings for random text inputs. Compute the L2 norm of each. If all norms are within 0.01 of 1.0, the model returns unit-norm vectors. If not, choose cosine similarity (compute norms at query time) or pre-normalise all vectors during ingestion. Consider whether normalisation should happen in the embedding pipeline (before storage) or at query time (additional compute per query).

**Q2 (Scale):** At 1 billion vectors, computing cosine similarity for every vector takes seconds. ANN indexes (HNSW) approximate this in milliseconds. What does the approximation cost you in terms of similarity precision, and how do you determine if the approximation error is acceptable for your RAG use case?

*Hint:* Think about what ANN "approximation error" means in retrieval terms: the truly most similar vector might not appear in the top-k results (recall@k < 1.0). The question is whether the omitted vectors would have produced better LLM answers than the vectors that were returned. Design an evaluation: compute both exact (brute-force) top-k and ANN top-k for a test query set. Compare the LLM answer quality for both result sets. If they are statistically equivalent, the ANN approximation error is acceptable.

**Q3 (Design Trade-off):** You discover that cosine similarity returns many high-scoring but redundant results (5 chunks from the same document, all about the same sentence). This makes the context window repetitive, reducing answer quality. Design a retrieval strategy that maintains high recall while reducing redundancy in the final context.

*Hint:* Think about Maximum Marginal Relevance (MMR): a retrieval strategy that alternates between selecting the most relevant remaining result and the most diverse remaining result. MMR penalises a result if it is too similar to already-selected results. Consider the trade-off: MMR improves diversity but may sacrifice the highest-precision results. Research how LangChain implements `search_type="mmr"` in vector store retrievers and what the `lambda_mult` parameter controls.
""")

print("\nRAG-008 and RAG-009 written.")
