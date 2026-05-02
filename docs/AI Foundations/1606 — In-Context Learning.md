---
layout: default
title: "In-Context Learning"
parent: "AI Foundations"
nav_order: 1606
permalink: /ai-foundations/in-context-learning/
number: "1606"
category: AI Foundations
difficulty: ★★★
depends_on: Context Window, Few-Shot Learning, Transformer Architecture
used_by: Few-Shot Learning, Zero-Shot Learning, Retrieval-Augmented Generation
related: Few-Shot Learning, Fine-Tuning, Grounding
tags:
  - ai
  - llm
  - advanced
  - mental-model
  - mechanism
---

# 1606 — In-Context Learning

⚡ TL;DR — In-context learning (ICL) is the ability of LLMs to adapt to new tasks by reading examples or instructions directly from the input prompt — without any weight updates — purely through the attention mechanism over the context window.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every new task or dataset requires a new gradient descent run. A model trained to classify news articles cannot suddenly perform sentiment analysis without retraining. In production, the cost of retraining a large model is measured in GPU-hours and thousands of dollars. Teams wait weeks between deploying new capabilities.

**THE BREAKING POINT:**
Neural networks before LLMs were task-specific. Adapting to a new task required a new training loop. The overhead of collecting data, training, validating, and deploying made rapid iteration impossible for the vast majority of use cases.

**THE INVENTION MOMENT:**
In-context learning, first described as a clear capability of GPT-3 (Brown et al., 2020), showed that sufficiently large models could "learn" to perform new tasks just from examples placed in the prompt — with no weight updates at all. The context window became a functional substitute for the gradient tape.

---

### 📘 Textbook Definition

**In-context learning (ICL)** is a paradigm in which a language model adapts its output to a task described (or demonstrated) within the input context, without modifying any model parameters. ICL encompasses zero-shot (task description only), few-shot (demonstrations provided), and chain-of-thought variants. Unlike traditional fine-tuning, ICL operates entirely at inference time: the model's forward pass over the prompt implicitly computes an "adaptation" through the attention mechanism applied to the context. ICL was first described as an emergent capability at scale in GPT-3, absent in smaller models, dramatically present in models above ~100B parameters.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
ICL means the model reads your examples in the prompt and immediately "knows" how to do your task — without you changing anything in the model.

**One analogy:**

> Imagine a contractor so experienced and adaptable that you hand them a one-page brief in the morning and they're delivering quality work that afternoon — without any formal onboarding or training. They read the brief, infer the conventions, and produce work that fits your standards. In-context learning is the same: the model reads the prompt and its "prior experience" (pre-training) allows it to immediately produce conforming outputs.

**One insight:**
ICL does not update the model. The same model that classified news articles this morning can do sentiment analysis this afternoon — same weights, different prompt. The "learning" is entirely transient: it exists only for the duration of that forward pass and is completely gone after the response is generated.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Transformer attention computes learned relationships between all tokens in the context window simultaneously.
2. In-context examples set up key-value pairs in the attention heads that the model uses to pattern-match the new query.
3. This mechanism functionally resembles a gradient descent step — but executed through attention over the prompt rather than backpropagation through the network.

**DERIVED DESIGN:**
Why does ICL work mechanistically?

Research (Akyürek et al., 2022; Garg et al., 2022) suggests that ICL implements a form of "implicit meta-learning." During pre-training, the model is trained to predict the next token across millions of diverse documents. Some of those documents are themselves "few-shot tasks" (instruction manuals, worked examples, test-answer pairs). The model learns: "given a sequence of input→output pairs, what is the most likely next output?"

At inference time, a few-shot prompt is exactly this structure. The model pattern-matches to its meta-learned understanding of what comes next in a sequence of demonstrations.

**THE TRADE-OFFS:**
**Gain:** Zero training cost; instantly adaptable; no labelling pipeline needed.
**Cost:** No persistent learning — ICL does not update weights; limited by context window length; sensitive to example order, quality, and format; degrading performance with very long contexts.

---

### 🧪 Thought Experiment

**SETUP:**
You have a 7B-parameter LLM and a 175B-parameter LLM. You give each the same few-shot prompt: 5 examples of arithmetic word problems → numeric answers. Then you give a new word problem.

**WHAT HAPPENS WITH 7B:**
The 7B model reads the examples, produces a response that sometimes follows the format but gets arithmetic wrong on complex problems. It recognises the pattern but lacks the reasoning capacity to execute the task reliably. ICL at small scale = format matching without reliable task execution.

**WHAT HAPPENS WITH 175B:**
The 175B model reads the examples, correctly identifies the pattern, and solves the arithmetic problem accurately. ICL at large scale = reliable task adaptation.

**THE INSIGHT:**
ICL is an emergent capability — it does not linearly scale from smaller models; it appears dramatically and suddenly at certain model sizes. This is why "just use GPT-2 and add examples" doesn't work — the capability requires sufficient scale. The threshold is approximately correlated with the model's ability to reliably perform reasoning, not merely pattern-matching.

---

### 🧠 Mental Model / Analogy

> ICL is like the model performing **scratch-pad learning**: when you show it 3 examples, it uses its context window as working memory, inferring the rule, and applying it to the new case — all within a single "thought." When that thought finishes, the working memory is cleared. No permanent learning occurred.

Mapping:

- "Scratch pad" → context window
- "Shows 3 examples" → few-shot prompt
- "Infers the rule" → attention over demonstrations
- "Applying it to the new case" → generating the output
- "Working memory cleared" → weights unchanged after inference

Where this analogy breaks down: real working memory persists briefly after the task; ICL is completely stateless. The next API call knows nothing of the previous inference.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
You show the AI examples of what you want in your message. It reads them, figures out the pattern, and does it — all in the same conversation, no training needed.

**Level 2 — How to use it (junior developer):**
Use ICL by structuring prompts with a system message (task description), optional few-shot examples in user/assistant turns or as inline text, and the new input. System prompts are a form of zero-shot ICL. Few-shot examples in the message are multi-shot ICL. Key tip: ICL quality degrades when the context window is filled with many long examples — prioritise concise, representative examples over comprehensive examples.

**Level 3 — How it works (mid-level engineer):**
Mechanistically, each attention head in the transformer computes queries, keys, and values over all tokens in the context. Few-shot examples establish attention patterns that align the output token distribution with the demonstrated output format. The "implicit fine-tuning" interpretation (Garg et al., 2022) shows that for linear regression tasks, ICL in transformers implements something close to gradient descent: each layer performs one approximate gradient step using the examples as training data. This explains why: (1) more examples help up to a point, (2) the model generalises the pattern rather than memorising examples, and (3) the model is sensitive to inconsistencies in examples (they produce contradictory "gradient steps").

**Level 4 — Why it was designed this way (senior/staff):**
The discovery that transformers implement an implicit optimization algorithm through their attention layers (von Oswald et al., 2023) explains why ICL works for a wide range of function classes — not just the text patterns in pre-training data. The dual form of the attention mechanism (attention = key-value lookup) can be seen as storing demonstrations as "virtual weights" that modify the effective output distribution during the forward pass. This is why Retrieval-Augmented Generation (RAG) is a powerful extension: by dynamically populating the context window with relevant retrieved documents, RAG effectively extends ICL from few demonstrations to richly grounded inference — using retrieval to overcome the knowledge gap that limits pure ICL.

---

### ⚙️ How It Works (Mechanism)

```
CONTEXT WINDOW AT INFERENCE TIME:

[System prompt — zero-shot ICL]
"You are a sentiment classifier.
 Classify each review as positive or negative."

[Demonstration 1 — few-shot ICL]
User: "Great product, works perfectly!"
Assistant: "positive"

[Demonstration 2]
User: "Broke after 2 days. Complete waste."
Assistant: "negative"

[New query]
User: "Decent quality but overpriced."
Assistant: ???

ATTENTION MECHANISM:
    New query attends over ALL prior tokens
    Extracts: format (one-word response)
              label space (positive/negative)
              decision boundary (quality vs. price)
    Output token distribution:
        "positive" → 12%
        "negative" → 71%  ← selected
        "neutral"  → 8%
        "decent"   → 4%
        [other]    → 5%
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Identify new task
    ↓
Design prompt:
  [task description] + [demonstrations] + [query]
    ↓
[IN-CONTEXT INFERENCE ← YOU ARE HERE]
Prompt → LLM forward pass → output
Attention over full context determines output
    ↓
Evaluate output quality
    ↓
Iterate on prompt structure / examples
    ↓
Deploy (or upgrade to fine-tuning at scale)
```

**FAILURE PATH:**

```
Context window overflows
(too many examples, too long inputs)
    ↓
Attention dilution: early examples
receive less attention weight
    ↓
Later examples dominate output
(recency bias)
    ↓
Fix: reduce number of examples;
     use shorter examples;
     use retrieval to select relevant
     examples dynamically (RAG + ICL)
```

---

### 💻 Code Example

**Example 1 — ICL via system prompt (zero-shot):**

```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a sentiment classifier. "
                "For each user message, respond ONLY with "
                "'positive', 'negative', or 'neutral'. "
                "No other text."
            )
        },
        {
            "role": "user",
            "content": "Great product, works perfectly!"
        }
    ],
    temperature=0.0
)
```

**Example 2 — ICL via few-shot turns:**

```python
messages = [
    {"role": "system",
     "content": "Classify sentiment."},
    {"role": "user",
     "content": "Great product, works perfectly!"},
    {"role": "assistant", "content": "positive"},
    {"role": "user",
     "content": "Broke after 2 days. Complete waste."},
    {"role": "assistant", "content": "negative"},
    # New query
    {"role": "user",
     "content": "Decent quality but overpriced."}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    temperature=0.0
)
```

**Example 3 — Dynamic ICL: retrieve relevant examples:**

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def retrieve_examples(
    query: str,
    example_pool: list[dict],
    embedder,
    k: int = 3
) -> list[dict]:
    """Retrieve top-k most similar examples for ICL."""
    query_emb = embedder.encode(query)
    example_embs = embedder.encode(
        [e["input"] for e in example_pool]
    )
    scores = cosine_similarity(
        query_emb.reshape(1, -1), example_embs
    )[0]
    top_k_indices = np.argsort(scores)[-k:][::-1]
    return [example_pool[i] for i in top_k_indices]

# Usage: build messages from retrieved examples
def dynamic_icl_classify(
    query: str,
    example_pool: list[dict],
    embedder,
    client
) -> str:
    examples = retrieve_examples(query, example_pool,
                                 embedder, k=3)
    messages = [{"role": "system",
                 "content": "Classify sentiment."}]
    for ex in examples:
        messages.append({"role": "user",
                         "content": ex["input"]})
        messages.append({"role": "assistant",
                         "content": ex["label"]})
    messages.append({"role": "user", "content": query})
    return client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.0
    ).choices[0].message.content.strip()
```

---

### ⚖️ Comparison Table

| Paradigm              | Weight Updates | Persists    | Latency         | Cost      | Accuracy    |
| --------------------- | -------------- | ----------- | --------------- | --------- | ----------- |
| **Zero-shot ICL**     | None           | No          | Lowest          | Lowest    | Variable    |
| **Few-shot ICL**      | None           | No          | Low             | Low       | Medium-high |
| **Dynamic ICL (RAG)** | None           | No          | Medium          | Medium    | High        |
| Fine-tuning           | Yes            | Permanently | Post-train only | High once | Highest     |
| RLHF                  | Yes            | Permanently | Post-train only | Very high | Very high   |

**How to choose:** Use ICL first — it's free and fast. When ICL accuracy is insufficient at scale, fine-tune. Combine with RAG for knowledge-grounded ICL.

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                               |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| "ICL trains the model"                    | ICL never updates weights — it operates entirely at inference time; nothing is learned persistently                   |
| "More examples always helps"              | After ~10 examples, performance plateaus or degrades due to attention dilution and context pressure                   |
| "ICL and fine-tuning are interchangeable" | ICL is transient; fine-tuning persists; fine-tuning is cheaper per inference at scale (shorter prompts)               |
| "ICL can teach the model new knowledge"   | ICL cannot introduce knowledge absent from pre-training — it only activates and directs existing knowledge            |
| "ICL is only about few-shot examples"     | Zero-shot task descriptions, system prompts, chain-of-thought prompts, and RAG-retrieved context are all forms of ICL |

---

### 🚨 Failure Modes & Diagnosis

**Recency Bias (Lost in the Middle)**

**Symptom:** Model ignores early examples in a long few-shot prompt; performance improves dramatically when the same examples are reordered to put the most important one last.

**Root Cause:** Attention weights in transformers have a "recency bias" — more recent tokens receive higher attention weights for the final token prediction. Early examples in long prompts lose influence.

**Diagnostic Command / Tool:**

```python
def test_position_sensitivity(
    examples: list[dict],
    query: str,
    client
) -> dict:
    """Test if example position affects output."""
    results = {}
    # Try examples in forward order
    results["forward"] = run_icl(examples, query, client)
    # Try examples in reverse order
    results["reverse"] = run_icl(
        list(reversed(examples)), query, client
    )
    if results["forward"] != results["reverse"]:
        print("WARNING: Position-sensitive — "
              "consider reordering or using fewer examples")
    return results
```

**Fix:** Put the most representative example closest to the query. Use dynamic example retrieval (most similar = last). Use no more than 5–7 examples.

**Prevention:** Test with multiple orderings before deploying few-shot ICL prompts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Context Window` — ICL operates entirely within the context window; window size limits ICL capacity
- `Few-Shot Learning` — few-shot is the canonical demonstration of ICL in LLMs
- `Transformer Architecture` — attention mechanism is the implementation substrate of ICL

**Builds On This (learn these next):**

- `Few-Shot Learning` — the practical form of ICL with demonstrations
- `Zero-Shot Learning` — ICL without demonstrations
- `Retrieval-Augmented Generation` — extends ICL with dynamically retrieved context

**Alternatives / Comparisons:**

- `Fine-Tuning` — persistent learning; ICL is the zero-cost alternative
- `Grounding` — ICL with retrieved factual context is a form of grounding
- `Transfer Learning` — ICL is transfer at inference time; fine-tuning is transfer through gradient descent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Adapting model behaviour by reading       │
│              │ examples/instructions in the prompt —     │
│              │ no weight updates, no training            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Every task previously required           │
│ SOLVES       │ retraining; ICL enables instant          │
│              │ adaptation at zero training cost          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ ICL is NOT learning — weights never       │
│              │ change; it's attention-based pattern      │
│              │ matching over demonstrations in context   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ New tasks; rapid prototyping; low volume; │
│              │ no labelled training data                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High volume (long prompts = high cost);   │
│              │ strict consistency required;              │
│              │ task needs knowledge absent from model    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero training cost, instant deployment    │
│              │ vs no persistent learning, context limits │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The context window is the training set; │
│              │ the forward pass is the training run."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RAG → Chain-of-Thought → Fine-Tuning      │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In-context learning is described as not updating model weights. Yet research shows that ICL implements "implicit gradient descent" through the attention mechanism. Explain the exact sense in which these two statements are BOTH true — and then explain what this reveals about the equivalence and non-equivalence of ICL and gradient-based fine-tuning for practical engineering decisions.

**Q2.** You are building a production classification system that must handle 1,000 different task types dynamically, each with its own few-shot examples. Using ICL naively means constructing and sending a different prompt for each of the 1,000 task types. Design a system architecture that minimises per-request token cost while preserving few-shot ICL quality — including how you would handle dynamic task switching at inference time and what monitoring you would put in place to detect ICL quality degradation.
