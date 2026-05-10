---
id: RAG-010
title: RAG Pipeline Basics (Index, Retrieve, Generate)
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★☆☆
depends_on: RAG-001, RAG-007, RAG-008
used_by: RAG-025, RAG-035
related: RAG-002, RAG-006, RAG-009
tags:
  - rag
  - foundational
  - first-principles
  - production
status: complete
version: 2
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /rag/rag-pipeline-basics-index-retrieve-generate/
---

# RAG-010 - RAG Pipeline Basics (Index, Retrieve, Generate)

⚡ **TL;DR —** Every RAG system has two pipelines: an offline Index pipeline (chunk, embed, store) and an online Query pipeline (embed, search, generate) — understanding both is the starting point for all RAG work.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | RAG-001, RAG-007, RAG-008 |
| **Used by**    | RAG-025, RAG-035          |
| **Related**    | RAG-002, RAG-006, RAG-009 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Developers read "use RAG" in a tutorial, install LangChain, call three functions, and have something that works on 5 test documents. In production with 50,000 documents it breaks. They don't understand where the two pipelines are, what each step does, or which step is failing. Every production incident is a debugging mystery.

**THE BREAKING POINT:**
Without understanding that RAG is TWO distinct pipelines (offline indexing and online querying), teams conflate failures. A latency spike in production could be the embedding step, the ANN search, the LLM call, or the chunking that happened weeks ago. Without a named pipeline model, there is no systematic diagnosis.

**THE INVENTION MOMENT:**
Naming the two pipelines makes every RAG problem diagnosable. The Index pipeline runs when data changes. The Query pipeline runs per user request. Problems in the Index pipeline manifest as poor retrieval. Problems in the Query pipeline manifest as latency or generation failures. The separation is the diagnostic tool.

**EVOLUTION:**
Early RAG tutorials (2022) showed a single end-to-end notebook. As teams moved to production, they discovered the two pipelines needed different infrastructure: Index uses batch processing (Spark, Airflow, or Lambda on S3 events); Query uses low-latency serving (FastAPI, Lambda). By 2023, all production RAG frameworks (LangChain, LlamaIndex) explicitly separate the two pipelines.

---

### 📘 Textbook Definition

A **RAG pipeline** consists of two sub-pipelines: (1) the **Index pipeline** (offline) — parses documents, chunks text, generates embeddings, and stores (vector, text, metadata) in a vector database; (2) the **Query pipeline** (online) — embeds the user query with the same model, performs ANN search for top-k relevant chunks, assembles an augmented prompt, and calls the LLM to generate an answer with citations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Index pipeline fills the library; Query pipeline reads the right pages and asks the LLM to explain them.

> _The Index pipeline is a one-time (or incremental) process that organises your documents into a searchable form. The Query pipeline is the per-request process that finds relevant documents and uses an LLM to synthesize an answer._

**One insight:** The Index pipeline runs offline and asynchronously; the Query pipeline is on the critical path of user requests. They must be designed with different performance requirements.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Documents are too large to embed whole. They must be chunked into retrieval units first.
2. The embedding model used for indexing and querying MUST be identical. Different models produce incompatible vector spaces.
3. The Index pipeline is a pre-computation step that trades storage and compute upfront for fast online retrieval.
4. Query pipeline latency = embed_time + search_time + llm_time. Each is independently optimisable.

**DERIVED DESIGN:**
Separate the pipeline that changes when data changes (Index) from the pipeline that runs per user request (Query). This separation enables independent scaling: Index pipeline runs once per document update; Query pipeline runs thousands of times per second.

**THE TRADE-OFFS:**

- **Gain:** Fast online retrieval (pre-computed indexes), separation of concerns, independent scaling.
- **Cost:** Index staleness (new documents not searchable until Index pipeline runs), storage cost for vectors, embedding compute cost proportional to corpus size.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** The two-pipeline structure is required by the physics of the problem (cannot embed at query time for millions of docs).
- **Accidental:** Over-engineering the Index pipeline before measuring whether a simpler approach meets freshness SLOs.

---

### 🧪 Thought Experiment

**SETUP:** You have 100,000 PDF documents. A user asks a question every 100ms (10 requests/second).

**WITHOUT PRE-INDEXING (embed at query time):**
Each query: embed 100,000 × 500-token chunks = 50M tokens of embedding calls, then brute-force search. Latency per query: minutes. Cost per query: $100+. Completely infeasible.

**WITH PRE-INDEXING (Index pipeline):**
Offline: embed 100,000 chunks once (cost: $2, time: 10 minutes). Online: embed query (1 call, 50ms), ANN search (5ms), LLM call (500ms). Total query latency: ~600ms. Feasible at any scale.

**THE INSIGHT:**
The Index pipeline is the entire reason RAG is economically and technically viable. It amortises the embedding cost over all future queries. Without it, every query pays the full embedding cost.

---

### 🧠 Mental Model / Analogy

> _The Index pipeline is a librarian cataloguing every book before the library opens. The Query pipeline is a patron asking the librarian a question — the librarian finds the relevant books (fast, because of the catalogue) and reads the key passages aloud._

- Cataloguing books (Index) = chunking, embedding, storing in vector DB
- Library catalogue = vector database with ANN index
- Patron's question = user query embedding
- Finding relevant books = ANN search
- Reading passages = assembling context and calling the LLM

Where this analogy breaks down: a librarian can understand intent and ask clarifying questions; the ANN search finds mathematically similar vectors — it cannot understand ambiguous intent without query transformation steps.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Building a RAG system is two jobs done separately. Job 1 (done once): break your documents into pieces, turn each piece into numbers, store the numbers. Job 2 (done per question): turn the question into numbers, find the most similar stored numbers, give the matching text to the AI to answer from.

**Level 2 - How to use it (junior developer):**
Index: `splitter.split_documents(docs)` → `OpenAIEmbeddings().embed_documents(chunks)` → `Chroma.from_documents(chunks, embeddings)`. Query: `vectorstore.as_retriever()` → `RetrievalQA.from_chain_type(llm, retriever)` → `qa.invoke({"query": question})`. The framework handles both pipelines; your job is configuration.

**Level 3 - How it works (mid-level engineer):**
Index pipeline steps: parse (PDFLoader, HTMLLoader) → split (RecursiveCharacterTextSplitter, 512 tokens, 64 overlap) → embed (batch API call) → upsert to vector DB (Chroma/Qdrant/Pinecone with metadata: source, page, date). Query pipeline steps: embed user query (single API call) → vector DB ANN search (top-k=4-6) → build prompt ([system] + [context chunks] + [query]) → LLM call → parse response + extract citations.

**Level 4 - Why it was designed this way (senior/staff):**
The two-pipeline separation reflects a fundamental engineering principle: separate the write path (Index) from the read path (Query). Index is throughput-optimised (batch embedding, bulk upsert); Query is latency-optimised (single embedding, ANN search, streamed LLM response). Treating them as one pipeline creates architectural pressure: optimizing for batch throughput degrades online latency and vice versa. Most production RAG failures come from not respecting this boundary — embedding at query time, or running the full Index pipeline on the hot path.

**Expert Thinking Cues:**

- "The Index pipeline is your data ingestion system. It needs the same reliability as ETL: dead-letter queues, failure retries, and freshness SLOs."
- "Add `embedding_model` and `chunk_strategy_version` to every stored chunk's metadata. When you change either, you need to re-index."
- "Query latency budget: embed (~50ms), search (~10ms), LLM (~500ms). The LLM is always the bottleneck. Optimise retrieval first."

---

### ⚙️ How It Works (Mechanism)

**INDEX PIPELINE (offline):**

```
Documents (PDF, HTML, DOCX)
  -> Document Loader (extract text)
  -> Text Splitter (512 tokens, 64 overlap)
  -> Embedding Model (batch API call)
  -> Vector DB upsert (id, vector, text, metadata)
```

**QUERY PIPELINE (per request):**

```
User Query
  -> Embedding Model (single call)
  -> Vector DB ANN search (top-k)
  -> Prompt builder ([system] + [chunks] + [query])
  -> LLM call
  -> Response + sources
```

**Key constraint:** Both pipelines must use the same embedding model and version. This is enforced by storing the model name as metadata and asserting it at query time.

---

### 🔄 The Complete Picture - End-to-End Flow

**FULL PIPELINE:**

```
OFFLINE (Index Pipeline)
  Raw Docs
    |-> Parse -> Chunk -> Embed -> Store
                                    |
                              Vector DB
                                    |
ONLINE (Query Pipeline)          (ANN index)
  User Query                       |
    |-> Embed -> Search ---------->+
                    |
                 Top-k chunks <- YOU ARE HERE
                    |
                 Build Prompt
                 [sys][ctx][query]
                    |
                 LLM Call
                    |
                 Response + Citations
```

**FAILURE PATH:**
Index pipeline fails silently (new docs not indexed) → Query returns stale results → LLM "doesn't know" about recent documents. Fix: monitor Index pipeline success and document count in vector DB.

**WHAT CHANGES AT SCALE:**
Index pipeline: distributed chunking (Spark), parallel embedding (batch API), streaming upsert. Query pipeline: horizontal scaling behind a load balancer, semantic caching for repeated queries, streaming LLM responses for lower perceived latency.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Index pipeline writes; Query pipeline reads. Vector DBs use MVCC or segment-based approaches to allow concurrent reads during index updates (no locks needed for queries). A 30-second delay between document upload and searchability is acceptable in most enterprise use cases.

---

### 💻 Code Example

**BAD — Single notebook function, no pipeline separation:**

```python
def answer_question(docs, query):
    # Anti-pattern: re-embeds ALL docs every query
    vectors = embed(docs)   # expensive! O(N) per query
    idx = build_faiss(vectors)
    chunks = search(idx, query)
    return llm(query, chunks)
```

**GOOD — Separated Index and Query pipelines:**

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)

EMBED_MODEL = "text-embedding-3-small"
embeddings = OpenAIEmbeddings(model=EMBED_MODEL)

# ── INDEX PIPELINE (run offline, on doc changes) ──
def index_documents(docs: list, persist_dir: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=64
    )
    chunks = splitter.split_documents(docs)
    # Add model version to metadata for change detection
    for c in chunks:
        c.metadata["embed_model"] = EMBED_MODEL
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return vectordb

# ── QUERY PIPELINE (run per user request) ──
def build_query_chain(persist_dir: str):
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(
            search_kwargs={"k": 5}
        ),
        return_source_documents=True
    )

# Usage:
# index_documents(my_docs, "./db")   # once
# chain = build_query_chain("./db")  # per deployment
# result = chain.invoke({"query": q}) # per request
```

**How to test / verify correctness:**

```python
# Test Index: verify chunk count and metadata
chunks = vectordb.get(limit=5)
assert chunks["metadatas"][0]["embed_model"] == EMBED_MODEL

# Test Query: verify answer comes from retrieved context
result = chain.invoke({"query": "What is the refund policy?"})
assert len(result["source_documents"]) > 0
assert result["result"]  # non-empty answer
```

---

### ⚖️ Comparison Table

| Approach         | Index Pipeline                   | Query Pipeline                     | Best For                     |
| ---------------- | -------------------------------- | ---------------------------------- | ---------------------------- |
| **Naive RAG**    | Fixed chunking, single embedding | Top-k retrieval, direct generation | Baselines, simple use cases  |
| **Advanced RAG** | Semantic chunking, parent-child  | Re-ranking, query rewriting        | Production, high-precision   |
| **Modular RAG**  | Pluggable components per step    | Custom routing, step selection     | Complex multi-document types |
| **Agentic RAG**  | Standard                         | Agent-controlled retrieval loop    | Multi-hop reasoning          |

---

### 🔁 Flow / Lifecycle

**INDEX PIPELINE PHASES:**

1. **Ingest** — Document loader extracts raw text from source format (PDF, HTML, DB).
2. **Chunk** — Text splitter divides text into overlapping retrieval units (512 tokens, 64 overlap).
3. **Embed** — Embedding model converts each chunk to a dense vector (batch API call).
4. **Store** — Vector DB upserts (id, vector, text, metadata). ANN index is built/updated.
5. **Validate** — Assert chunk count matches source doc count. Verify embedding model version in metadata.

**QUERY PIPELINE PHASES:**

1. **Embed query** — Same embedding model converts user question to a query vector (single call).
2. **Retrieve** — ANN search returns top-k (score, chunk_text, metadata) tuples.
3. **Augment** — Prompt builder assembles [system instruction] + [context chunks] + [user query].
4. **Generate** — LLM call produces answer grounded in retrieved context.
5. **Cite** — Response includes source references (filename, page, chunk_id) from metadata.

---

### ⚠️ Common Misconceptions

| Misconception                                                      | Reality                                                                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| "RAG is a single pipeline"                                         | RAG is always two pipelines: offline Index and online Query. Treating them as one causes architectural failures.                     |
| "You embed documents at query time"                                | Embedding all documents per query is O(N) per request — infeasible at any scale. Index pipeline pre-computes embeddings.             |
| "Any embedding model works for querying if it worked for indexing" | Only the EXACT SAME model produces compatible vectors. A model version update requires full re-indexing.                             |
| "The vector DB is the whole RAG system"                            | The vector DB is one component of the Index pipeline. RAG requires chunking, embedding, prompt assembly, and LLM generation as well. |
| "RAG guarantees fresh results"                                     | RAG is only as fresh as the last Index pipeline run. Without continuous ingestion, answers can be stale.                             |

---

### 🚨 Failure Modes & Diagnosis

**1. Index pipeline staleness**

**Symptom:** Users report that RAG doesn't know about a document that was uploaded days ago.

**Root Cause:** Index pipeline is not triggered on document upload, or failed silently.

**Diagnostic:**

```python
# Compare source document count vs indexed chunk count
source_count = len(list(docs_folder.glob("*.pdf")))
indexed_count = vectordb.collection.count()
print(f"Source: {source_count} | Indexed: {indexed_count}")
# Gap = missing documents in index
```

**Fix:**
BAD: Manually running the Index pipeline on complaint.
GOOD: Trigger Index pipeline on document upload (S3 event → Lambda → chunk/embed → upsert). Monitor `indexed_doc_count` metric; alert if it falls behind `source_doc_count`.

**Prevention:** Implement an Index freshness SLO (e.g., new docs searchable within 5 minutes). Alert on violations.

---

**2. Embedding model version drift**

**Symptom:** After a dependency update, retrieval quality degrades. Old documents return irrelevant results.

**Root Cause:** Embedding model version changed (package update changed model weights or API updated the model). New query vectors are incompatible with old indexed vectors.

**Diagnostic:**

```python
# Check stored embedding model vs current model
stored = vectordb.get(limit=1)["metadatas"][0]
print(f"Stored model: {stored.get('embed_model')}")
print(f"Current model: {EMBED_MODEL}")
# Mismatch = incompatible vector spaces
```

**Fix:**
BAD: Querying with new model against old embeddings.
GOOD: Pin the embedding model version. When changing, re-run the full Index pipeline with the new model before switching queries.

**Prevention:** Store `embed_model` in every chunk's metadata. Assert at query time that query model matches stored model.

---

**3. Prompt context overflow**

**Symptom:** LLM responses are truncated, generic, or refuse to answer. Errors: "context length exceeded."

**Root Cause:** top-k is too large, or chunks are too large. The assembled prompt exceeds the LLM's context window limit.

**Diagnostic:**

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
prompt_tokens = len(enc.encode(assembled_prompt))
print(f"Prompt tokens: {prompt_tokens}")
# gpt-4o limit: 128K tokens
# Warn if > 100K (leave room for output)
```

**Fix:**
BAD: top-k=20 with 2048-token chunks.
GOOD: top-k=4 to 6, chunk_size=512. Compute prompt token count before LLM call and assert < 80% of context limit.

**Prevention:** Set a hard prompt token budget. Truncate context if needed, prioritising highest-scored chunks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `RAG-001 - What Is RAG` — why RAG exists
- `RAG-007 - Embeddings` — the core transformation in the Index pipeline
- `RAG-008 - Chunking Strategies` — the first step of the Index pipeline

**Builds On This (learn these next):**

- `RAG-019 - RAG Evaluation` — measuring pipeline quality
- `RAG-025 - Advanced RAG Patterns` — extending both pipelines
- `RAG-035 - Agentic RAG` — dynamic query pipeline control

**Alternatives / Comparisons:**

- `RAG-002 - The RAG Mental Model` — Retrieve/Augment/Generate framing of the same system
- `RAG-037 - RAG at Scale` — distributed Index and Query pipelines

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Two pipelines: offline Index     |
|               | + online Query                   |
+--------------------------------------------------+
| INDEX         | Parse -> Chunk -> Embed -> Store |
+--------------------------------------------------+
| QUERY         | Embed -> Search -> Augment ->    |
|               | Generate                         |
+--------------------------------------------------+
| KEY INSIGHT   | Index amortises embedding cost;  |
|               | Query is on the latency SLA      |
+--------------------------------------------------+
| SAME MODEL    | ALWAYS use same embedding model  |
|               | for indexing and querying        |
+--------------------------------------------------+
| TRADE-OFF     | Index freshness vs re-index cost;|
|               | chunk size vs retrieval precision|
+--------------------------------------------------+
| ONE-LINER     | "Pre-compute to serve fast"      |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-019, RAG-025, RAG-035        |
+--------------------------------------------------+
```

**If you remember only 3 things:**

1. RAG has two separate pipelines: offline Index (chunk/embed/store) and online Query (search/augment/generate).
2. The same embedding model must be used for both pipelines — a version mismatch breaks everything silently.
3. The Index pipeline must be triggered on document changes; stale indexes produce stale answers.

**Interview one-liner:** "A RAG pipeline splits into offline Index (chunk documents, embed, store in vector DB) and online Query (embed query, ANN search for top-k, assemble prompt, call LLM) — the separation enables pre-computation of expensive embeddings, making per-query latency feasible."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate write-time pre-computation from read-time serving. Any system where expensive computation can be done ahead of time should do so. This is the principle behind database indexes, search engine inverted indexes, CDN edge caching, and materialized views — all pre-compute so that reads are fast.

**Where else this pattern appears:**

- **Search engine inverted indexes:** The index is built once (offline) from all crawled pages; queries hit the pre-built index (online). Same two-pipeline structure as RAG.
- **Database query plans:** EXPLAIN ANALYZE shows the query plan is pre-computed (offline) and cached; execution hits the cached plan path (online).
- **Recommendation systems (precomputed embeddings):** User and item embeddings are computed offline and stored; online serving just does ANN search for the user's vector.

---

### 💡 The Surprising Truth

The most common production RAG failure is not in the Query pipeline — it is in the Index pipeline running too infrequently. Teams spend weeks optimising embedding models, chunk sizes, and LLM prompts, achieving 90% accuracy on their test set, then ship to production where the Index pipeline runs once a week. Users ask about documents added yesterday and get wrong answers. A 95%-accurate RAG system with daily indexing outperforms a 99%-accurate system with weekly indexing for any real-world enterprise knowledge base that changes regularly. Freshness is a first-order quality metric, not an operational afterthought.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Your Index pipeline fails halfway through re-indexing 100,000 documents (power cut at document 60,000). You now have a mixed index: 60,000 documents re-indexed with the new chunking strategy, 40,000 still indexed with the old strategy. How do you detect and recover from this partial state?

_Hint:_ Think about idempotency in the Index pipeline: if you can re-run it on any document without side effects (upsert by document ID is idempotent), you can simply re-run from the beginning. Consider how you track which documents have been indexed with which strategy version — storing `chunk_strategy_version` as metadata enables filtering out stale documents. Explore whether a blue-green index approach (build new index completely before cutting over queries) eliminates this partial-state problem entirely.

**Q2 (Scale):** Your Query pipeline serves 1,000 requests per second. The embedding step takes 50ms per request. How does this translate to embedding API concurrency requirements, and what caching strategy would reduce this cost?

_Hint:_ Think about the math: 1,000 req/s × 50ms embedding = 50 concurrent embedding calls at any moment. Most embedding APIs have rate limits; at 1k req/s you may exceed per-minute token limits. Semantic caching (store (query_hash, result) in Redis) can serve repeated or near-identical queries without hitting the embedding API. Estimate what % of queries are likely to be semantically identical in your use case (high for FAQ systems, low for open-ended questions).

**Q3 (Design Trade-off):** Design an Index pipeline that supports three freshness tiers: "real-time" documents (searchable within 30 seconds), "daily" documents (re-indexed nightly), and "archive" documents (indexed once, never updated). How does this affect the vector DB architecture?

_Hint:_ Think about three separate indexes or collections: a "hot" index (small, frequently updated via streaming upsert, possibly using a simpler IVF or flat index), a "warm" index (nightly batch re-index, HNSW for performance), and a "cold" archive (large HNSW, read-only). At query time, fan out to all three and merge results by score. Consider how metadata filtering can restrict certain queries to specific tiers (e.g., "search only recent documents for this query type").
