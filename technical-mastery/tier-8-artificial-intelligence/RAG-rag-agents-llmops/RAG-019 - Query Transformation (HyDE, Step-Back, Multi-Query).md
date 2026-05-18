---
id: RAG-021
title: Query Transformation (HyDE, Step-Back, Multi-Query)
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★★☆
depends_on: RAG-007, RAG-010
used_by:
related: RAG-017, RAG-025
tags:
  - rag
  - intermediate
  - pattern
  - advanced
status: complete
version: 2
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Mastery"
nav_order: 19
permalink: /technical-mastery/rag/query-transformation-hyde-step-back-multi-query/
---

⚡ **TL;DR  - ** Query transformation improves RAG recall by rewriting the user query before embedding  -  HyDE generates a hypothetical answer, multi-query creates N variants, step-back broadens to a general principle  -  each targeting a different retrieval failure mode.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | RAG-007, RAG-010 |
| **Used by**    |  -                 |
| **Related**    | RAG-017, RAG-025 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
User queries are short (5-10 words), ambiguous, and often phrased differently from the target documents. A query like "why is my app slow?" embeds differently from a document section titled "Performance Optimisation: Database Query Bottlenecks" even if that section directly answers the question. The embedding distance is large because the vocabularies don't match.

**THE BREAKING POINT:**
Technical queries often suffer vocabulary mismatch: users ask in plain English; documents use domain terminology. Conversational queries embed close to other conversational text, not to technical documentation. Ambiguous queries ("Python error") match too many documents. The raw query is a poor retrieval signal.

**THE INVENTION MOMENT:**
HyDE (Hypothetical Document Embeddings, Gao et al., 2022) showed that embedding a hypothetical answer document  -  instead of the query  -  dramatically improves retrieval. The intuition: a generated answer uses the same vocabulary as real answer documents. Multi-query (Langchain, 2023) generates N query variants to cover different phrasings of the same question. Step-back prompting (Google, 2023) generalises specific questions to broader principles.

**EVOLUTION:**
Query transformation became a standard RAG component. Fusion retrieval (RAG-Fusion) combines multi-query + RRF. Hypothetical Document Embeddings extended to images and code. Query routing (route different query types to different retrievers) emerged as a related pattern. LangChain and LlamaIndex provide built-in implementations.

---

### 📘 Textbook Definition

**Query transformation** modifies the user query before embedding and retrieval to improve recall. The three primary techniques are: **HyDE** (generate a hypothetical document that would answer the query, then embed that instead of the query); **multi-query** (generate N rephrasings of the query, retrieve for each, and union the results); and **step-back** (rephrase the specific query as a more general question, retrieve background knowledge, then combine with the original query).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Users ask questions; documents have answers. Query transformation makes queries look more like answers before retrieval.

> _You're searching a library for books about a topic, but you only know the question, not the technical title. A librarian (query transformer) rewrites your question as "This would be in a book about X and Y" and searches using that  -  finding better matches than your original question._

**One insight:** Embedding models learn the distribution of text in their training corpus. Queries and answers live in different parts of that distribution. Query transformation bridges the gap by moving the query embedding closer to where answers live.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The embedding space is shaped by the text distribution seen during training. Short, conversational queries embed differently from long, technical document passages, even when they share the same meaning.
2. HyDE exploits asymmetry: the model knows more about the answer domain than the question domain. Generating a hypothetical answer produces text that embeds in the same region as real answers.
3. Multi-query and step-back increase recall by diversity  -  the union of multiple retrieval sets covers more of the relevant document space than any single retrieval.

**THE TRADE-OFFS:**
Gain: higher recall on short/ambiguous/vocabulary-mismatched queries (10-25% improvement measured in RAG-Fusion). Cost: additional LLM call before retrieval (+100-500ms, +cost). HyDE can generate hallucinated content that embeds worse than the original query if the domain is too specialised.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** Bridging the vocabulary gap between user queries and document text is a genuine challenge in RAG.
- **Accidental:** The LLM call overhead  -  mitigated by using a smaller model (GPT-3.5, Llama-3) for transformation while using a larger model for generation.

---

### 🧪 Thought Experiment

Query: "why does my Java app leak memory after 2 hours?"

Direct embedding: the vector is close to other "Java memory" questions and generic Java tutorials.

HyDE: the LLM generates: "Java memory leaks after extended runtime are often caused by: (1) unclosed resources in long-running loops, (2) static collection accumulation, (3) listener registration without deregistration, (4) ThreadLocal variables not cleaned up..."

This generated text embeds close to technical Java performance documentation  -  exactly where the relevant answer document lives. The embedding is a much better retrieval signal.

The insight: the generated document doesn't need to be correct. It just needs to be in the right vocabulary neighbourhood to retrieve documents that ARE correct.

---

### 🧠 Mental Model / Analogy

> _Query transformation is asking a friend to help you search. You ask: "Where can I find the thing that makes my code run faster?" Your friend (query transformer) says: "You mean performance profiling and optimisation? Let me search for that." They translated your vague question into the vocabulary the library uses._

- Your vague question = original user query
- Friend's translation = transformed query
- Library vocabulary = document embedding space
- Better search results = higher retrieval recall

Where this analogy breaks down: your friend understands your intent; the LLM transformer generates a plausible-sounding transformation but may misinterpret ambiguous queries, transforming in the wrong direction.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before searching your documents, query transformation rewrites the search question to be more precise or more general, finding more relevant results.

**Level 2 - How to use it (junior developer):**
LangChain provides `MultiQueryRetriever.from_llm(retriever, llm)` which generates 3 query variants automatically. For HyDE: add a "Generate a document that would answer this question:" step before the retriever in your LCEL chain.

**Level 3 - How it works (mid-level engineer):**
HyDE chain: `question -> LLM("Write a passage that answers: {question}") -> hypothetical_doc -> embed(hypothetical_doc) -> ANN search`. The embedding of the generated passage is typically closer to relevant answer passages than the embedding of the original question. Multi-query: `question -> LLM("Generate 3 different phrasings of this question") -> [q1, q2, q3] -> retrieve for each -> union(results)`. Deduplication by document ID is essential. Step-back: `question -> LLM("What broader principle relates to this question?") -> general_question -> retrieve background -> LLM(original_q + background + retrieved_context) -> answer`.

**Level 4 - Why it was designed this way (senior/staff):**
Query transformation addresses the asymmetry between question and answer embedding spaces  -  a fundamental limitation of bi-encoder retrieval. Dense embeddings trained with contrastive learning push query-answer pairs together, but this training signal is weaker for short queries vs long document passages. HyDE exploits LLM generative capability to produce text that sits in the answer distribution, bypassing the bi-encoder's question-answer gap. The cost (one LLM call) is acceptable because the generation model used for transformation can be smaller and cheaper than the one used for final synthesis.

**Expert Thinking Cues:**

- "HyDE works best when the domain vocabulary is well-represented in the LLM's training data. For highly specialised domains (rare medical terms, proprietary systems), HyDE may generate off-domain hypotheticals."
- "Multi-query deduplication is critical. Without it, the same document appears multiple times in context, wasting context window tokens."

---

### ⚙️ How It Works (Mechanism)

```
HyDE:
Query: "How do I fix Python GIL contention?"
  -> LLM: "Write a paragraph answering this:"
  -> Hypothetical: "Python GIL contention occurs when
     multiple threads compete for the Global Interpreter
     Lock. Solutions include: using multiprocessing instead
     of threading, using asyncio for I/O-bound tasks..."
  -> embed(hypothetical) -> ANN search -> relevant docs

Multi-Query:
Query: "Python GIL contention"
  -> LLM generates: ["Python thread performance issues",
     "Global Interpreter Lock workarounds",
     "Python concurrency bottlenecks"]
  -> retrieve(q1) U retrieve(q2) U retrieve(q3)
  -> deduplicate by doc_id
  -> top-K unique docs

Step-Back:
Query: "Why is asyncio faster than threading in Python?"
  -> LLM: "What broader principle applies?"
  -> "Python concurrency models and GIL"
  -> retrieve background context
  -> answer with original_q + background
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
User Query
  |
  v
Query Transformer (LLM call)  <- YOU ARE HERE
  |                    |               |
HyDE doc          [q1, q2, q3]   broader q
  |                    |               |
Embed+Search   3x Retrieve+Union  Retrieve+Original
  |
 Merged/Deduplicated results
  |
 LLM generation (answer)
```

**FAILURE PATH:** HyDE generates hallucinated hypothetical in wrong domain -> embedding is worse than original query -> retrieval quality drops. Detection: measure recall@k before and after HyDE.

**WHAT CHANGES AT SCALE:** Transformation LLM call is a serial step before parallel retrieval. Use a fast small model (Llama-3-8B, GPT-3.5-turbo) for transformation; keep retrieval latency low by parallelising multi-query retrievals.

---

### 💻 Code Example

**BAD  -  Short query embedded directly (vocabulary mismatch):**

```python
# Short user query may embed far from technical documentation
results = vectorstore.similarity_search(
    "why is my app slow",  # too vague for good retrieval
    k=5
)
```

**GOOD  -  Multi-query retrieval with deduplication:**

```python
from langchain.retrievers import MultiQueryRetriever
from langchain_openai import ChatOpenAI

base_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}
)

# Generates 3 query variants automatically
multi_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # Use cheaper/faster model for transformation
)

docs = multi_retriever.invoke(
    "why is my Java app using too much memory?"
)
# Deduplication handled automatically by MultiQueryRetriever
print(f"Retrieved {len(docs)} unique documents")
```

**HyDE implementation:**

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

hyde_prompt = ChatPromptTemplate.from_template(
    "Write a short technical document that answers this "
    "question. Be specific and technical.\n\nQuestion: "
    "{question}\n\nDocument:"
)

hyde_chain = (
    {"question": lambda x: x}
    | hyde_prompt
    | ChatOpenAI(model="gpt-3.5-turbo")
    | StrOutputParser()
)

hypothetical_doc = hyde_chain.invoke(
    "why is my Java app using too much memory?"
)
# Embed the hypothetical document, not the original query
docs = vectorstore.similarity_search(hypothetical_doc, k=5)
```

---

### ⚖️ Comparison Table

| Technique       | Mechanism              | Best For                           | Weakness                          |
| --------------- | ---------------------- | ---------------------------------- | --------------------------------- |
| **HyDE**        | Embed generated answer | Technical vocabulary gaps          | Fails on specialised/rare domains |
| **Multi-query** | Union N query variants | Ambiguous, multi-faceted questions | More LLM calls, dedup required    |
| **Step-back**   | Broaden to principles  | "Why" questions needing background | May over-generalise               |
| **None**        | Direct query embedding | Precise technical queries          | Misses paraphrases                |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                               |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "HyDE always improves retrieval"              | HyDE degrades retrieval on highly specialised domains where the LLM lacks domain knowledge. The generated hypothetical embeds in the wrong neighbourhood. Always A/B test against baseline.           |
| "Multi-query just adds noise"                 | Multiple query variants systematically cover different semantic neighborhoods of the query intent. Studies show 10-25% recall improvement over single-query baselines on diverse query distributions. |
| "Step-back is only for "why" questions"       | Step-back improves any query requiring background knowledge not in the user's phrasing. "How to fix X" benefits from stepping back to "what causes X"  -  background context improves final synthesis.  |
| "Query transformation replaces hybrid search" | Orthogonal techniques. Multi-query improves semantic recall. Hybrid search improves keyword recall. Use both for maximum recall.                                                                      |

---

### 🚨 Failure Modes & Diagnosis

**1. HyDE degrades retrieval on specialised domain**

**Symptom:** After adding HyDE, retrieval recall drops. Evaluation (RAGAs context_recall) is lower with HyDE than without.

**Diagnostic:**

```python
# Compare recall@5 with and without HyDE
baseline_recall = measure_recall(base_retriever, eval_set)
hyde_recall = measure_recall(hyde_retriever, eval_set)
print(f"Baseline: {baseline_recall:.2f}")
print(f"HyDE:     {hyde_recall:.2f}")
# If HyDE recall < baseline: HyDE is hurting
# Inspect: print the hypothetical docs for failing queries
```

**Fix:** Restrict HyDE to queries where the LLM has domain knowledge. For highly specialised domains (proprietary systems, rare medical conditions), fall back to direct query embedding or use a domain-fine-tuned model for transformation.

---

**2. Multi-query returns duplicate documents in context**

**Symptom:** LLM context window filled with the same document 3 times. Answer quality does not improve despite higher retrieval volume.

**Diagnostic:**

```python
results = multi_retriever.invoke(query)
ids = [d.metadata.get("source") for d in results]
print(f"Total: {len(ids)}, Unique: {len(set(ids))}")
# Many duplicates = deduplication not working
```

**Fix:** Ensure documents have unique IDs in metadata (`source`, `doc_id`). Use `list({d.metadata["source"]: d for d in results}.values())` for manual deduplication. `MultiQueryRetriever` handles this automatically only if document IDs are unique.

---

**3. Step-back over-generalises**

**Symptom:** Step-back retrieves very general background information but misses the specific technical detail needed to answer the question. Final answer is vague.

**Diagnostic:**

```python
# Print the step-back question generated for failing queries
step_back_q = generate_step_back(query)
print(f"Original: {query}")
print(f"Step-back: {step_back_q}")
# If step-back is too broad (e.g., "general programming concepts")
# the retrieval covers too wide a space
```

**Fix:** Add the original query alongside the step-back query in retrieval (dual retrieval). Use step-back context as background + original query for specific details. Tune the step-back prompt to generalise one level up, not all the way to first principles.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `RAG-007 - Embeddings`  -  why query-document vocabulary gap exists in embedding space
- `RAG-010 - RAG Pipeline Basics`  -  where query transformation fits in the pipeline

**Builds On This (learn these next):**

- `RAG-017 - Re-ranking`  -  post-retrieval precision improvement (complementary technique)
- `RAG-025 - Advanced Retrieval Techniques`  -  contextual compression and parent-child retrieval

**Alternatives / Comparisons:**

- `RAG-018 - Metadata Filtering`  -  precision improvement via structure vs vocabulary transformation

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Pre-retrieval query rewriting to  |
|               | improve embedding-space recall   |
+--------------------------------------------------+
| PROBLEM       | User query vocabulary mismatches |
|               | document vocabulary              |
+--------------------------------------------------+
| 3 TECHNIQUES  | HyDE: embed hypothetical answer  |
|               | Multi-query: N variants + union  |
|               | Step-back: broaden to principle  |
+--------------------------------------------------+
| USE WHEN      | Short/vague user queries; high   |
|               | query-document vocab mismatch    |
+--------------------------------------------------+
| AVOID HyDE    | Specialised proprietary domain   |
|               | where LLM lacks knowledge        |
+--------------------------------------------------+
| TRADE-OFF     | +1 LLM call (+100-500ms) for     |
|               | 10-25% recall improvement        |
+--------------------------------------------------+
| ONE-LINER     | "Make queries look like answers" |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-017, RAG-025                 |
+--------------------------------------------------+
```

**If you remember only 3 things:**

1. HyDE embeds a generated answer (not the query)  -  vocabulary matches document space.
2. Multi-query unions N variants  -  always deduplicate by document ID.
3. All techniques add one LLM call  -  use a small fast model for transformation.

**Interview one-liner:** "Query transformation rewrites the user query before retrieval: HyDE embeds a generated hypothetical answer, multi-query retrieves for N rephrasings and unions results, step-back generalises to broader context  -  each addressing a different vocabulary mismatch failure."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When two systems communicate using different vocabularies (user queries vs document terminology), translation at the boundary improves communication. This is the principle behind API translation layers, data transformation ETL pipelines, and protocol adapters  -  each bridges a vocabulary or schema mismatch at a system boundary.

**Where else this pattern appears:**

- **SQL query optimisation:** Query rewriting transforms a complex user query into an optimised execution plan. The user writes intent; the optimiser transforms it into an efficient form for the storage engine.
- **Search query expansion:** Classic IR technique: expand "car" to `OR automobile OR vehicle OR motorcar`. The same vocabulary bridging principle, pre-neural.
- **Compiler intermediate representations:** Source code is translated to an intermediate representation (LLVM IR) before being translated to machine code. Each stage operates in a vocabulary better suited to its task.

---

### 💡 The Surprising Truth

HyDE (Hypothetical Document Embeddings) generates documents that are deliberately hallucinated  -  and this is not a bug, it is the core mechanism. The model invents a plausible-but-possibly-incorrect answer to the query, and it is the embedding of this invented text that is used for retrieval, not the text itself. The actual content of the hypothetical document is thrown away after embedding. This means a RAG system using HyDE performs best when the LLM is fluent in the domain vocabulary  -  it generates better-positioned embeddings  -  but may degrade when the LLM is outside its training distribution. Controlled hallucination as a retrieval signal is one of the more counterintuitive engineering ideas in modern AI systems.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** HyDE generates a hypothetical document before embedding. This adds ~200ms to query latency. Design an architecture where HyDE transformation is applied only to queries likely to benefit from it, and direct embedding is used for queries that don't need it.

_Hint:_ Think about query classifiers: short queries (<5 tokens) benefit more from HyDE than long specific queries. Ambiguous queries (detected by low confidence score from an intent classifier) are better HyDE candidates. How would you train and maintain such a classifier, and what is the cost vs. benefit of this complexity?

**Q2 (Scale):** Multi-query generates 3 query variants, each triggering a retrieval call. At 1,000 queries/second, multi-query requires 3,000 retrieval calls/second instead of 1,000. What changes in your vector DB and infrastructure to support this?

_Hint:_ Retrieval calls are independent  -  they can run in parallel with `asyncio.gather()`. The bottleneck shifts from sequential retrieval to vector DB throughput and connection pool limits. Research Qdrant's concurrent search capabilities. Also consider: caching embeddings for repeated query variants.

**Q3 (Design Trade-off):** You have a RAG system with low recall (0.62 context_recall). You must choose one improvement: (A) add multi-query transformation or (B) add re-ranking (RAG-017). Based on what each technique optimises for, which is the correct fix for low recall?

_Hint:_ Recall measures whether the relevant document was retrieved at all. Re-ranking improves precision (the ordering of already-retrieved candidates). If the relevant document is not in top-50, re-ranking cannot help. Multi-query increases the probability the relevant document is in the retrieved set. Which addresses the root cause?
