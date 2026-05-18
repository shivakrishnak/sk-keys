---
id: RAG-020
title: RAG Evaluation (RAGAs, Faithfulness, Relevance)
category: RAG & Agents & LLMOps
tier: tier-8-artificial-intelligence
folder: RAG-rag-agents-llmops
difficulty: ★★☆
depends_on: RAG-002, RAG-010
used_by: RAG-031
related: RAG-005, RAG-031
tags:
  - rag
  - intermediate
  - production
  - bestpractice
status: complete
version: 2
layout: default
parent: "RAG & Agents & LLMOps"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/rag/rag-evaluation-ragas-faithfulness-relevance/
---

⚡ **TL;DR  - ** RAGAs provides four metrics  -  faithfulness, answer relevancy, context precision, context recall  -  that together measure whether a RAG system retrieves the right context AND generates answers that faithfully use it.

| Field          | Value            |
| -------------- | ---------------- |
| **Depends on** | RAG-002, RAG-010 |
| **Used by**    | RAG-031          |
| **Related**    | RAG-005, RAG-031 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A RAG system is deployed and described as "working." A month later, users complain about wrong answers. There are no metrics to determine whether the problem is retrieval (wrong context retrieved), generation (model ignored context), or the prompt. Without measurements, you cannot distinguish between these failure modes.

**THE BREAKING POINT:**
Traditional NLP metrics are wrong for RAG. ROUGE measures n-gram overlap with a reference answer  -  useless when the answer is generated from retrieved context that may use different phrasing. BLEU penalises paraphrase. Accuracy requires labelled test data that doesn't exist. The field lacked purpose-built metrics.

**THE INVENTION MOMENT:**
RAGAs (Evaluation As A Service, Shahul Es et al., 2023) defined four metrics specifically for RAG: Faithfulness (does the answer follow from context?), Answer Relevancy (does the answer address the question?), Context Precision (are retrieved chunks relevant?), Context Recall (does context contain the answer?). The insight: LLMs themselves can evaluate LLM outputs  -  "LLM-as-judge."

**EVOLUTION:**
RAGAs evolved from offline evaluation (test sets, LLM-as-judge scoring) to production monitoring (LangSmith, Arize Phoenix). RAGAS v0.2 (2024) added multi-turn conversation evaluation and component-level testing. Alternative frameworks: ARES (Stanford), TruLens, DeepEval. The LLM-as-judge approach extended beyond RAG to general LLM output evaluation.

---

### 📘 Textbook Definition

**RAGAs** (Retrieval-Augmented Generation Assessment) is an evaluation framework for RAG systems defining four core metrics: (1) **Faithfulness**  -  fraction of answer claims supported by retrieved context; (2) **Answer Relevancy**  -  how well the answer addresses the question; (3) **Context Precision**  -  fraction of retrieved chunks that are relevant; (4) **Context Recall**  -  fraction of ground truth information present in retrieved context. All four use an LLM-as-judge to score each sample.

---

### ⏱️ Understand It in 30 Seconds

**One line:** RAGAs tells you if your RAG retrieves the right context (precision, recall) and generates a faithful answer from it (faithfulness, relevancy).

> _RAGAs is a report card for RAG systems. Four grades: Did you retrieve relevant material? Did you retrieve enough material? Did you stay on topic? Did you make up anything? A perfect RAG scores 1.0 on all four._

**One insight:** The four metrics decompose RAG failures: low context precision = retrieval problem. Low faithfulness = generation problem. Low answer relevancy = prompt or LLM problem. Low context recall = chunking or retrieval coverage problem.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. RAG fails in two independent ways: retrieval failure (wrong context retrieved) and generation failure (model does not use context correctly). These require different fixes  -  retrieval metrics vs generation metrics must be separated.
2. LLM-as-judge works because the LLM evaluator can apply semantic understanding to check consistency, relevance, and factual support  -  which token-matching metrics (ROUGE/BLEU) cannot.
3. All four RAGAs metrics are bounded [0, 1]. Higher is always better. This makes them comparable across systems and suitable for automated regression testing.

**THE TRADE-OFFS:**
Gain: automatic evaluation without hand-labelled answers for faithfulness and relevancy metrics. Cost: LLM-as-judge costs money (API calls) and has its own bias  -  larger models may score their own outputs higher. Context recall requires ground truth, which requires labelling effort.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

- **Essential:** Measuring retrieval and generation quality separately is genuinely complex  -  the RAG pipeline has two failure modes that standard metrics cannot distinguish.
- **Accidental:** The LLM-as-judge API cost and latency  -  can be mitigated with sampling (evaluate 10% of production traffic) and cheaper judge models.

---

### 🧪 Thought Experiment

Your RAG answer quality drops from 85% to 65% user satisfaction after adding 10,000 new documents. Without metrics, you don't know why. With RAGAs:

- Context precision drops: 0.82 -> 0.61 (the new documents are noisy  -  retrieval is pulling irrelevant chunks)
- Faithfulness stays stable: 0.91 -> 0.89 (when given good context, the LLM still answers faithfully)
- Context recall stays stable: 0.78 -> 0.80

Diagnosis: the problem is in retrieval quality of the new documents, not the LLM. Fix: improve chunking of new documents, add metadata filtering to separate high-quality from low-quality sources. Without RAGAs, you would have tried prompt engineering or switching LLMs  -  both wrong fixes.

---

### 🧠 Mental Model / Analogy

> _RAGAs is a quality audit for a research assistant. Four checks: Did they pull the right sources? Did they pull enough sources? Did they cover the question? Did they fabricate anything? Each check is scored independently, pinpointing where the assistant needs improvement._

- Pull the right sources = Context Precision
- Pull enough sources = Context Recall
- Cover the question = Answer Relevancy
- No fabrication = Faithfulness

Where this analogy breaks down: a human research assistant can be asked to explain their reasoning; an LLM judge scoring RAGAs can only assess the visible output  -  it cannot inspect the model's internal reasoning or detect confident hallucination.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
RAGAs gives your RAG system a score card: how often does it retrieve relevant information, and how often does it answer correctly based on what it found?

**Level 2 - How to use it (junior developer):**

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset
result = evaluate(
    Dataset.from_list(samples),
    metrics=[faithfulness, answer_relevancy]
)
print(result["faithfulness"])  # 0.0-1.0
```

**Level 3 - How it works (mid-level engineer):**
**Faithfulness**: RAGAs extracts all factual claims from the answer using an LLM, then asks the judge LLM: "Is this claim supported by the context?" Score = supported_claims / total_claims. **Answer Relevancy**: generates N question paraphrases from the answer, embeds them, and measures cosine similarity to the original question. High similarity = answer is on-topic. **Context Precision**: for each retrieved chunk, asks LLM: "Is this useful for answering the question?" Score = useful_chunks / total_chunks. **Context Recall**: given ground truth answer, asks LLM: "What part of this ground truth is covered by the retrieved context?"

**Level 4 - Why it was designed this way (senior/staff):**
RAGAs uses LLM-as-judge because traditional metrics fail on the specific structure of RAG evaluation: the answer is generated (not retrieved), so ROUGE/BLEU comparisons against reference answers are unreliable. The faithfulness metric specifically addresses hallucination  -  an answer can be high ROUGE if it reuses words from context, even if it makes false claims. Splitting into four metrics reflects the two-component RAG pipeline: retrieval quality (precision/recall) and generation quality (faithfulness/relevancy). This decomposition enables targeted debugging.

**Expert Thinking Cues:**

- "Context recall requires ground truth (expected answer)  -  it's the most expensive metric to compute but the most valuable for debugging retrieval gaps."
- "Run faithfulness + answer_relevancy on every production sample (sampled at 10%). Run context_precision + context_recall on your offline eval set."

---

### ⚙️ How It Works (Mechanism)

```
Faithfulness:
  answer -> LLM extract claims: [c1, c2, c3]
  for each ci: ask judge LLM "is ci supported by context?"
  score = supported_count / total_claims

Answer Relevancy:
  answer -> LLM generate N question variants
  embed each variant
  score = avg cosine_sim(variant_embed, original_q_embed)

Context Precision:
  for each chunk in context:
    ask judge LLM "is this chunk useful for answering q?"
  score = useful_chunks / total_chunks

Context Recall (requires ground truth):
  ground_truth -> LLM extract key statements
  for each statement:
    ask "is this statement supported by retrieved context?"
  score = supported_statements / total_statements
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Test sample: {question, context, answer, [ground_truth]}
                                  |
                          RAGAs evaluate()  <- YOU ARE HERE
                                  |
            +--------------------+--------------------+
            |                    |                    |
    Faithfulness          Context Precision     Answer
      Relevancy
    (LLM checks            (LLM checks           (LLM
      generates
    claim support)         chunk utility)         question
      back)
            |
            v
    Scores per sample -> Aggregate -> Dashboard
    (faithfulness: 0.87, answer_relevancy: 0.79, ...)
```

**FAILURE PATH:** LLM-as-judge picks different judge model than production LLM  -  scores may not correlate with actual quality. Always use the same judge model consistently for comparability.

**WHAT CHANGES AT SCALE:** Evaluate 100% of offline test set, sample 5-10% of production traffic. Use async evaluation to avoid blocking the production path.

---

### 💻 Code Example

**BAD  -  Eyeballing answers as evaluation:**

```python
answers = [chain.invoke(q) for q in test_questions]
for a in answers:
    print(a)  # manually checking 20 answers
# Not reproducible, doesn't scale, misses subtle failures
```

**GOOD  -  RAGAs automated evaluation pipeline:**

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

# Build test set: question + run RAG to get context + answer
samples = []
for q, ground_truth in test_pairs:
    docs = retriever.invoke(q)
    answer = rag_chain.invoke(q)
    samples.append({
        "question": q,
        "answer": answer,
        "contexts": [d.page_content for d in docs],
        "ground_truth": ground_truth,  # needed for recall
    })

dataset = Dataset.from_list(samples)

# Evaluate with LLM-as-judge (GPT-4o by default)
results = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]
)

print(results.to_pandas()[[
    "faithfulness", "answer_relevancy",
    "context_precision", "context_recall"
]].describe())
# Mean per metric: target > 0.80 for production
```

---

### ⚖️ Comparison Table

| Metric                | What it measures         | Requires ground truth  | Diagnoses                |
| --------------------- | ------------------------ | ---------------------- | ------------------------ |
| **Faithfulness**      | Answer claims vs context | No                     | Generation hallucination |
| **Answer Relevancy**  | Answer on-topic          | No                     | Off-topic generation     |
| **Context Precision** | Chunk usefulness         | No                     | Retrieval noise          |
| **Context Recall**    | Coverage of ground truth | Yes                    | Retrieval gaps           |
| **ROUGE-L**           | N-gram overlap           | Yes (reference answer) | Surface-level phrasing   |
| **BERTScore**         | Semantic similarity      | Yes                    | Paraphrase quality       |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                              |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "High faithfulness = correct answer"        | Faithfulness measures whether the answer is grounded in context  -  not whether the context is correct. If retrieved context is wrong, a faithful answer is also wrong.                |
| "ROUGE/BLEU works for RAG evaluation"       | ROUGE measures n-gram overlap with a reference answer. RAG answers are generated, paraphrased, and longer than references. ROUGE penalises valid paraphrases.                        |
| "Evaluation only matters before deployment" | Production drift is real: new documents, updated LLM APIs, and changing query distributions all degrade RAG quality over time. Sample 5-10% of production for continuous evaluation. |
| "One metric is enough"                      | The four metrics address different failure modes. High faithfulness + low context precision = the LLM faithfully uses bad context. You need all four to diagnose.                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Faithfulness drops after LLM upgrade**

**Symptom:** Faithfulness score drops from 0.91 to 0.72 after upgrading LLM version. The new model is more confident and generates claims beyond the provided context.

**Diagnostic:**

```python
# Sample from production after upgrade
low_faith = results.filter(lambda x: x["faithfulness"] < 0.7)
for sample in low_faith.select(range(10)):
    print("Q:", sample["question"])
    print("A:", sample["answer"])
    print("Context:", sample["contexts"][0][:200])
    print("---")
# Identify: is the LLM adding information not in context?
```

**Fix:** Strengthen the system prompt: `"Answer ONLY from the provided context. Do not use any external knowledge. If the context does not contain the answer, say: I don't have enough information."` Re-evaluate after prompt change.

---

**2. Context recall low despite relevant documents in corpus**

**Symptom:** Context recall is 0.45  -  the retriever is not finding the documents that contain the ground truth answer.

**Diagnostic:**

```python
# Find low-recall samples and inspect retrieved context
low_recall = results.filter(lambda x: x["context_recall"] < 0.5)
for s in low_recall.select(range(5)):
    print("Expected in context:", s["ground_truth"][:200])
    print("Retrieved context:", s["contexts"][0][:200])
    # Key question: is the ground truth in the corpus at all?
    # If yes: retrieval is failing. If no: ingestion is incomplete.
```

**Fix:** Verify the answer-containing document is in the vector store. If yes: improve retrieval (hybrid search, query transformation). If no: fix ingestion pipeline.

---

**3. LLM-as-judge evaluation is inconsistent**

**Symptom:** Running RAGAs twice on the same dataset gives different scores (e.g., 0.82 vs 0.79 faithfulness).

**Diagnostic:**

```python
# Check judge model temperature
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

judge_llm = LangchainLLMWrapper(
    ChatOpenAI(model="gpt-4o", temperature=0.0)  # MUST be 0
)
# Default RAGAs uses temperature > 0 which causes variance
```

**Fix:** Set judge LLM temperature to 0 for reproducible evaluation. Use `gpt-4o` or `gpt-4-turbo` as judge  -  smaller models have more variability in evaluation decisions. Run eval 3x and report median if consistency is critical.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `RAG-002 - The RAG Mental Model`  -  the pipeline that RAGAs evaluates
- `RAG-010 - RAG Pipeline Basics`  -  the two stages (retrieval + generation) each metric targets

**Builds On This (learn these next):**

- `RAG-031 - RAG Testing and Quality Gates`  -  integrating RAGAs into CI/CD
- `RAG-005 - LLMOps`  -  production monitoring and drift detection

**Alternatives / Comparisons:**

- `RAG-031 - Advanced RAG Evaluation`  -  ARES, TruLens, component testing

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | 4-metric framework for RAG eval  |
|               | using LLM-as-judge               |
+--------------------------------------------------+
| PROBLEM       | "Does RAG work?" is unmeasurable |
|               | without purpose-built metrics    |
+--------------------------------------------------+
| 4 METRICS     | Faithfulness / AnswerRelevancy   |
|               | ContextPrecision / ContextRecall |
+--------------------------------------------------+
| DIAGNOSE WITH | Low faithfulness = LLM issue     |
|               | Low precision = retrieval noise  |
|               | Low recall = retrieval gaps      |
+--------------------------------------------------+
| USE WHEN      | Evaluating any RAG change:       |
|               | new model, new chunking, new DB  |
+--------------------------------------------------+
| GOTCHA        | Context recall needs ground truth|
|               | Other 3 are reference-free       |
+--------------------------------------------------+
| ONE-LINER     | "Report card for RAG pipelines" |
+--------------------------------------------------+
| NEXT EXPLORE  | RAG-005, RAG-031                 |
+--------------------------------------------------+
```

**If you remember only 3 things:**

1. Four metrics: Faithfulness (no hallucination), Answer Relevancy (on-topic), Context Precision (good chunks), Context Recall (complete retrieval).
2. Low faithfulness = generation problem. Low precision/recall = retrieval problem. Different fix for each.
3. Only context recall requires ground truth labels. The other three are reference-free.

**Interview one-liner:** "RAGAs evaluates RAG systems with four LLM-as-judge metrics: faithfulness (answer grounded in context), answer relevancy (answer addresses question), context precision (retrieved chunks relevant), and context recall (context covers ground truth)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When a system has two sequential processing stages, instrument each stage independently. A single end-to-end quality metric cannot distinguish failures in stage 1 (retrieval) from failures in stage 2 (generation). Decomposed metrics enable targeted debugging and prevent chasing the wrong root cause.

**Where else this pattern appears:**

- **E-commerce funnel metrics:** Impression rate (did the product show?) vs Click-through rate (did the user engage?) vs Conversion rate (did they buy?). Each measures a different stage failure.
- **ML pipeline evaluation:** Data quality score + model accuracy + inference latency. A low-accuracy model could be caused by bad data (stage 1) or wrong architecture (stage 2)  -  separate metrics distinguish these.
- **CI/CD quality gates:** Unit test pass rate (code correctness) + integration test pass rate (component interaction) + performance benchmark (runtime). Each stage has its own gate.

---

### 💡 The Surprising Truth

RAGAs' most important metric  -  faithfulness  -  does not measure whether the answer is correct. A RAG system can score 1.0 faithfulness (every claim is supported by context) and still be completely wrong, because the retrieved context itself contains incorrect information. This means a high-faithfulness RAG system can confidently provide wrong answers from a poorly curated knowledge base. Faithfulness measures hallucination (making things up), not accuracy (being right). Many teams deploy "high faithfulness" RAG systems without validating the accuracy of their source documents, creating systems that are confidently wrong at scale.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Your RAGAs evaluation shows context_precision = 0.62 and faithfulness = 0.94. Explain the state of your RAG system and propose two specific improvements to context_precision.

_Hint:_ High faithfulness means the LLM uses what it gets faithfully. Low precision means 38% of retrieved chunks are irrelevant. The LLM is faithfully using a mix of good and irrelevant context. Improving precision means improving retrieval selectivity  -  explore metadata filtering, re-ranking, or query transformation as potential fixes.

**Q2 (Scale):** You want to run RAGAs on 100% of production traffic (10,000 queries/day). Each RAGAs evaluation calls the LLM judge 4-8 times per sample. Estimate the monthly cost and propose a sampling strategy.

_Hint:_ 10,000 queries x 6 LLM calls/query x $0.01/call = $600/day = $18,000/month. Research sampling strategies: evaluate 5% of samples (reduce to ~$900/month). Ensure the sample is representative (not just easy queries). Consider trigger-based evaluation: always evaluate when user gives negative feedback.

**Q3 (Design Trade-off):** A colleague argues that human evaluation is more reliable than LLM-as-judge for RAGAs. Design an experiment to determine when human evaluation adds value over LLM-as-judge for your specific RAG use case.

_Hint:_ Compare human ratings and LLM-as-judge scores on the same 200 samples. Measure agreement (Cohen's kappa). Identify the categories of samples where they disagree most. Research the finding that LLM-as-judge shows "position bias" (favours longer, first-listed answers). Determine if your query distribution is affected by these known biases.
