---
layout: default
title: "Pre-training"
parent: "AI Foundations"
nav_order: 1602
permalink: /ai-foundations/pre-training/
number: "1602"
category: AI Foundations
difficulty: ★★★
depends_on: Training, Model Parameters, Neural Network
used_by: Fine-Tuning, RLHF, Transfer Learning
related: Fine-Tuning, Transfer Learning, Foundation Models
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - internals
---

# 1602 — Pre-training

⚡ TL;DR — Pre-training is the expensive, large-scale training phase where a model learns general representations from vast unlabelled data — the foundation that makes all subsequent fine-tuning possible.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every NLP task team in 2017 trained their own model from scratch: one team trains a sentiment classifier, another trains a named-entity recogniser, another trains a question answerer — each on their own small labelled dataset. Each model learns to read English from scratch. They cannot share what they learn about language across tasks. Performance is bounded by the small labelled datasets available per task, which are expensive to create.

**THE BREAKING POINT:**
Most of a language model's learning is about language itself — grammar, semantics, reasoning — not about the specific task. Re-learning language from scratch for every task is massively wasteful. But there is no way to share the "language understanding" learned for one task with another task if all training is task-specific.

**THE INVENTION MOMENT:**
This is exactly why Pre-training was developed — as the phase where a model learns general language representations from enormous unlabelled text corpora, which can then be fine-tuned for any downstream task with minimal task-specific labelled data.

---

### 📘 Textbook Definition

**Pre-training** is the initial large-scale training phase of a neural network on a broad, general objective using vast unlabelled data — for LLMs, this is next-token prediction (causal language modelling) on trillions of tokens from web text, books, code, and other sources. Pre-training produces a **foundation model** with general-purpose representations that capture language structure, factual knowledge, and reasoning patterns. This model is then adapted via fine-tuning to specific tasks without needing to retrain the full model from scratch.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pre-training is the model reading everything ever written so it understands language before learning any specific task.

**One analogy:**

> Think of pre-training as a child learning to read and write fluently before entering school. Years of exposure to books, conversations, and stories (the pre-training corpus) builds foundational language understanding. Once literate (pre-trained), learning specific subjects (fine-tuning tasks) is vastly faster — because the child doesn't need to re-learn the alphabet for every class.

**One insight:**
Pre-training is why the modern LLM paradigm works. A single pre-training run ($10M–$100M of compute) produces a foundation that hundreds of teams can fine-tune for their specific tasks at a fraction of the cost. The pre-trained model is a shared public good; fine-tuning is the private specialisation layer.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. General language understanding is transferable across tasks — grammar learned on news text applies to medical text.
2. Unlabelled text is orders of magnitude more abundant than labelled datasets.
3. Next-token prediction is a self-supervised objective that requires no labels — every sentence is its own training signal.

**DERIVED DESIGN:**
The self-supervised pre-training objective for autoregressive LLMs:

`Objective: maximise P(token_t | token_1, ..., token_{t-1})`

No labels needed: for each sequence of tokens, the model predicts each token given all preceding tokens. The ground truth is the text itself.

This forces the model to learn:

- Syntax: to predict "John runs" correctly, the model must learn subject-verb agreement.
- Semantics: to predict "The hospital admitted the patient" vs "The prison admitted the prisoner," the model must learn contextual meaning.
- Factual knowledge: to predict "The capital of France is Paris," the model must encode this fact.
- Reasoning: to predict the continuation of a math problem, the model must learn arithmetic patterns.

**THE TRADE-OFFS:**
**Gain:** One pre-training run produces a general model usable for thousands of downstream tasks; unlabelled data is essentially unlimited.
**Cost:** Enormous compute and cost (GPT-4 pre-training estimated at $100M+); cannot target specific behaviours; model learns everything in training data including biases and misinformation.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams building a biomedical question-answering system. Team A: train a transformer from scratch on 50,000 labelled medical QA pairs. Team B: fine-tune a pre-trained LLM (Llama-3) on the same 50,000 pairs.

**WHAT HAPPENS WITH TEAM A (no pre-training):**
The model must learn basic English from 50,000 examples — far too few to generalise reliably. It learns to pattern-match medical QA surface forms but fails on paraphrased questions, complex multi-hop reasoning, or novel medical concepts not in its training set. Performance: 52% accuracy on held-out test set.

**WHAT HAPPENS WITH TEAM B (pre-trained foundation):**
Llama-3 already understands language structure and encodes billions of medical facts from pre-training on web and scientific text. Fine-tuning on 50,000 pairs specialises the answer format, not the language understanding. Performance: 84% accuracy on the same test set — 32 percentage points better with identical task-specific data.

**THE INSIGHT:**
Pre-training provides "free" language understanding that would otherwise require orders of magnitude more labelled data to learn from scratch. The 50,000 labelled examples only need to teach the task; the language understanding is already there.

---

### 🧠 Mental Model / Analogy

> Think of pre-training as building the infrastructure of a city before constructing any buildings. Roads, utilities, communications networks — these take enormous resources but enable everything that comes afterward. Fine-tuning is constructing a specific building (bank, hospital, school) on top of this infrastructure. Without the infrastructure, every building would need its own roads and utilities — impossibly expensive. With it, each building needs only walls and doors.

Mapping:

- "City infrastructure" → pre-trained model weights (general language representations)
- "Roads and utilities" → grammar, semantics, reasoning embedded in weights
- "Construction cost" → pre-training compute ($10M–$100M)
- "Building a specific structure" → fine-tuning for a specific task
- "Building needs only walls and doors" → fine-tuning needs only task-specific data

Where this analogy breaks down: city infrastructure is fixed; pre-trained model weights can be further updated (fine-tuned), though this changes the "infrastructure" in small ways.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Pre-training is the AI reading billions of web pages, books, and code to learn language. It happens once, costs a lot of money, and creates a foundation that everyone can build on.

**Level 2 — How to use it (junior developer):**
You almost never run pre-training yourself — it is done by organisations with large GPU clusters. You download the resulting pre-trained weights from Hugging Face and fine-tune them. Choosing a pre-trained base model: consider the training data mix (code-heavy for code tasks, multilingual for multilingual tasks), licence, and context length. Key providers: Meta (Llama), Mistral, Google (Gemma), Alibaba (Qwen).

**Level 3 — How it works (mid-level engineer):**
Pre-training data pipeline: web crawl (Common Crawl) → deduplication (MinHash LSH) → quality filtering (FastText classifiers) → tokenisation → shuffled sequence packing. Training: causal language modelling loss, AdamW optimiser, cosine learning rate schedule with warmup, gradient checkpointing for memory efficiency. Distributed training: 3D parallelism (data parallel × tensor parallel × pipeline parallel) across thousands of GPUs. Evaluation: perplexity on held-out corpora, plus downstream task benchmarks every N steps.

**Level 4 — Why it was designed this way (senior/staff):**
The choice of causal (autoregressive) LM objective over masked LM (BERT) reflects a design trade-off: causal LM enables generation (predict next token → generate text); masked LM gives better bidirectional representations for classification tasks. GPT chose causal LM and the subsequent success of GPT-3/4 demonstrated that generation-focused pre-training scales better to emergent capabilities. The Chinchilla scaling law determined that pre-training compute should be split ~50/50 between model parameters and training tokens — overturning the previous paradigm (GPT-3: 175B params but only ~300B tokens, undertrained by Chinchilla standards).

---

### ⚙️ How It Works (Mechanism)

**Pre-training pipeline:**

```
┌─────────────────────────────────────────────┐
│ DATA PIPELINE                               │
│ Web crawl: 60 TB raw HTML                  │
│ → text extraction                           │
│ → language detection (keep English/other)  │
│ → deduplication (MinHash)                  │
│ → quality filtering (perplexity, rules)    │
│ → tokenisation (BPE/SentencePiece)         │
│ Result: ~15T tokens of high-quality text   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ TRAINING (distributed across 1000s of GPUs)│
│ Data: packed sequences of 4096 tokens each  │
│ Objective: predict next token (CE loss)    │
│ Optimiser: AdamW + cosine LR schedule      │
│ Duration: weeks to months                  │
│ Checkpoints: saved every N steps           │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ EVALUATION                                  │
│ Perplexity on held-out text                │
│ Benchmark performance (MMLU, HumanEval)    │
│ Track emergent capabilities at scale       │
└──────────────┬──────────────────────────────┘
               ↓
        Pre-trained base model released
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Raw data collection (web, books, code)
    ↓
Data cleaning and deduplication
    ↓
Tokenisation
    ↓
[PRE-TRAINING ← YOU ARE HERE]
  Self-supervised next-token prediction
  on trillions of tokens
  across thousands of GPUs
    ↓
Pre-trained base model (weights)
    ↓
Optional: continued pre-training (domain)
    ↓
Fine-tuning / RLHF for specific tasks
    ↓
Deployed model (ChatGPT, Claude, etc.)
```

**FAILURE PATH:**

```
Training data contaminated with test sets
    ↓
Model "memorises" benchmark answers
    ↓
Inflated benchmark scores
    ↓
Observed: mysterious high performance on
specific benchmarks vs. poor real-world use
```

**WHAT CHANGES AT SCALE:**
Pre-training at scale reveals emergent capabilities — abilities not present in smaller models that appear suddenly at certain scale thresholds (e.g., multi-step arithmetic, in-context learning). These emergent abilities are not programmed; they arise from the interaction of scale and the next-token prediction objective. This makes frontier model behaviour partially unpredictable before training completes.

---

### 💻 Code Example

**Example 1 — Running continued pre-training on domain data:**

```python
from transformers import (AutoModelForCausalLM,
                          AutoTokenizer, Trainer,
                          TrainingArguments,
                          DataCollatorForLanguageModeling)
from datasets import load_dataset

# Load pretrained base model for domain adaptation
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B"  # open base model
)
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3-8B"
)

# Domain-specific corpus (e.g., medical papers)
dataset = load_dataset("medical_papers_corpus")

def tokenize(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=2048,
    )

tokenized = dataset.map(tokenize, batched=True)

# Causal LM data collator (no labels needed)
collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)

trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="./medical-pretrained",
        num_train_epochs=1,        # continued pretraining
        per_device_train_batch_size=4,
        learning_rate=1e-5,        # much lower than SFT
        save_steps=500,
        fp16=True,
    ),
    train_dataset=tokenized["train"],
    data_collator=collator,
)
trainer.train()
```

**Example 2 — Evaluating perplexity of pre-trained model:**

```python
import torch
import math

def compute_perplexity(model, tokenizer,
                       text: str) -> float:
    """Lower perplexity = model better at predicting text."""
    inputs = tokenizer(text, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model(
            **inputs, labels=inputs["input_ids"]
        )
    return math.exp(outputs.loss.item())

# A model pre-trained on medical data should have
# lower perplexity on medical text
print(compute_perplexity(base_model, tokenizer, medical_text))
# → 12.4 (higher = less fluent on this domain)
print(compute_perplexity(medical_model, tokenizer, medical_text))
# → 7.2 (lower = more fluent after domain pre-training)
```

---

### ⚖️ Comparison Table

| Approach               | Cost      | Data                | Task Generality | Best For                |
| ---------------------- | --------- | ------------------- | --------------- | ----------------------- |
| **Full pre-training**  | $10M–$1B  | Trillions of tokens | Maximum         | Frontier model creation |
| Continued pre-training | $10K–$1M  | Billions of tokens  | High            | Domain specialisation   |
| Fine-tuning (SFT)      | $100–$10K | Thousands–millions  | Low-medium      | Task behaviour          |
| Few-shot prompting     | $0        | 0–100 examples      | Medium          | Quick adaptation        |

**How to choose:** For almost all organisations, start from an existing pre-trained base model. Continued pre-training on domain data is worthwhile only when the domain is substantially underrepresented in the base model's training corpus (e.g., proprietary codebases, specialised medical literature).

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                             |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Pre-training = training"                          | Pre-training is specifically large-scale self-supervised training on unlabelled data; fine-tuning, RLHF, and continued training are separate phases                                 |
| "Larger pre-training always dominates"             | A 7B model pre-trained on more high-quality tokens (Llama-3 7B on 15T tokens) can outperform a 13B model pre-trained on fewer tokens                                                |
| "Pre-training data is freely available"            | High-quality pre-training data (deduplicated, filtered web text + books + code) requires significant engineering; the data pipeline is often as important as the model architecture |
| "You can't change a pre-trained model's knowledge" | Continued pre-training and fine-tuning both update the model's weights and can inject new knowledge (with risk of catastrophic forgetting)                                          |
| "All pre-trained models learn the same things"     | Data mix composition (web vs. books vs. code vs. multilingual) fundamentally shapes what the model learns; same architecture, different data → substantially different model        |

---

### 🚨 Failure Modes & Diagnosis

**Benchmark Contamination**

**Symptom:** Model scores dramatically higher on popular benchmarks (MMLU, HumanEval) than expected from its parameter count and training compute.

**Root Cause:** Benchmark test sets were included (accidentally or intentionally) in pre-training data. Model memorised answers rather than developing the reasoning they test.

**Diagnostic Command / Tool:**

```python
# Check for benchmark contamination with n-gram overlap
from collections import Counter

def check_contamination(train_corpus: list[str],
                        benchmark_q: str,
                        ngram_size: int = 10) -> float:
    """Returns fraction of benchmark n-grams in corpus."""
    q_ngrams = set(zip(*[iter(benchmark_q.split())] *
                   ngram_size))
    hits = sum(
        1 for doc in train_corpus
        for ngram in q_ngrams
        if " ".join(ngram) in doc
    )
    return hits / max(len(q_ngrams), 1)
```

**Fix:** Remove benchmarks from pre-training corpus; use held-out benchmarks not in public datasets; monitor for sudden performance jumps on specific benchmarks.

**Prevention:** Use private, unpublished benchmark sets for evaluation; apply n-gram contamination detection before pre-training.

---

**Distributional Imbalance (Domain Mismatch)**

**Symptom:** Pre-trained model performs well on common web text tasks but poorly on domain-specific tasks (legal, medical, code in rare languages).

**Root Cause:** Pre-training corpus is dominated by common English web text; rare domains are underrepresented and the model has weak priors for them.

**Diagnostic Command / Tool:**

```bash
# Measure domain representation in pre-training data
python analyze_corpus.py --domain medical \
  --corpus-path /data/pretraining/ \
  --output domain_stats.json
# Check: what % of tokens are from medical sources?
```

**Fix:** Continued pre-training with domain-specific data; domain upsampling in the pre-training mix.

**Prevention:** Analyse domain representation in training data before pre-training; over-sample rare but important domains.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Training` — pre-training is a specific type of training; understanding the gradient descent loop is required
- `Model Parameters` — pre-training produces the parameter values in the resulting model
- `Neural Network` — pre-training is applied to transformer-based neural networks

**Builds On This (learn these next):**

- `Fine-Tuning` — the next phase after pre-training; adapts pre-trained weights to specific tasks
- `RLHF` — aligns the pre-trained model with human preferences
- `Transfer Learning` — the general principle that pre-training enables; fine-tuning is transfer learning applied

**Alternatives / Comparisons:**

- `Transfer Learning` — the general concept; pre-training is the LLM-specific application
- `Foundation Models` — the outputs of pre-training; large models trained on broad data
- `Fine-Tuning` — what comes after pre-training; the specialisation phase

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Large-scale self-supervised training on   │
│              │ trillions of tokens to create a general   │
│              │ language foundation model                 │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Task-specific training from scratch       │
│ SOLVES       │ re-learns language for every task —       │
│              │ pre-training amortises this cost once     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Self-supervised next-token prediction     │
│              │ forces the model to learn everything:     │
│              │ grammar, facts, reasoning, code — from   │
│              │ unlabelled text alone                     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building a foundation model — requires    │
│              │ GPU cluster + $10M+ budget                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never pre-train from scratch when a       │
│              │ suitable open model exists — use          │
│              │ continued pre-training or fine-tuning     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Massive compute cost (once) vs enabling   │
│              │ all downstream tasks cheaply              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Teaching the AI to read everything       │
│              │ before learning anything specific —       │
│              │ pay once, reuse forever."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fine-Tuning → RLHF → Foundation Models    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Llama-3-8B was pre-trained on 15 trillion tokens vs. Llama-2-7B on 2 trillion tokens. Both are similar in parameter count. According to Chinchilla scaling laws, which model is better trained, and what does the 7.5× increase in training tokens do to the model's capabilities beyond simply "more data = better" — specifically, which types of capabilities emerge with more training tokens that cannot be achieved by scaling parameters alone?

**Q2.** A research team discovers that their pre-training corpus contains 0.01% of text in Swahili. At inference time, the model performs surprisingly well on Swahili tasks — far better than the 0.01% representation would suggest. Propose two mechanisms from transformer architecture that could explain this emergent multilingual capability, and describe an experiment that would distinguish between them.
