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
version: 3
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
Try to split at `

` (paragraphs). If chunk still too large, split at `
` (lines). If still too large, split at `. ` (sentences). If still too large, split at ` ` (words).

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
    separators=["

", "
", ". ", " ", ""]
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
    print(f"
{strategy_name}:")
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
    lines = chunk.page_content.split("
")
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
