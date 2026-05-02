---
layout: default
title: "Inference"
parent: "AI Foundations"
nav_order: 1598
permalink: /ai-foundations/inference/
number: "1598"
category: AI Foundations
difficulty: ★★☆
depends_on: Model Weights, Model Parameters, Neural Network
used_by: Context Window, Temperature, Latency vs Throughput (AI)
related: Training, Model Quantization, Latency vs Throughput (AI)
tags:
  - ai
  - llm
  - intermediate
  - production
  - performance
---

# 1598 — Inference

⚡ TL;DR — Inference is running a trained model to generate predictions — the production phase where a model's frozen weights are used to process new inputs, as opposed to training where weights are learned.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (as a concept):**
A data scientist finishes training a fraud detection model. The model achieves 99% accuracy on the test set. Now what? The model exists as a trained artifact — a set of learned parameters in GPU memory. Without the concept of "inference" as a distinct, deployable phase, there is no framework for: running the model on production requests, serving it at scale, optimising it for latency vs. training throughput, or reasoning about the cost trade-offs between training compute and serving compute.

**THE BREAKING POINT:**
Training and inference have fundamentally different requirements: training needs high GPU utilisation with large batches and gradient storage; inference needs low latency with small batches and no gradient tracking. Without distinguishing these phases, engineers cannot optimise for either.

**THE INVENTION MOMENT:**
This is exactly why Inference was defined as a distinct phase — to separate the model application phase (use the weights) from the model learning phase (update the weights), enabling specialised infrastructure, optimisation, and cost modelling for each.

---

### 📘 Textbook Definition

**Inference** (also called **prediction** or **forward pass**) is the process of running a trained neural network on new, unseen inputs to generate outputs — without updating the model's parameters. During inference, all weights are frozen; no gradients are computed; memory requirements are lower than training. For autoregressive LLMs, inference is iterative: the model generates one token at a time, appending each to the context and running a new forward pass, until a stop condition is reached.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Inference is using the finished model to answer questions — like sitting the exam after all the studying is done.

**One analogy:**

> Training is like a student spending months studying for a medical exam, memorising thousands of cases, running thousands of practice tests, and correcting mistakes. Inference is the exam itself: the student applies everything they learned to new questions, but nothing they do during the exam changes their underlying knowledge. The knowledge is frozen; only the application is new.

**One insight:**
Inference and training have different resource profiles. Training requires storing gradients for every parameter (10–20× more memory than inference). Inference only requires the forward pass — much cheaper per sample but must run at low latency for real-time applications. In production, 90%+ of compute spend is inference, not training.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. During inference, weights are read but never written.
2. No gradient computation is required (no backward pass).
3. For autoregressive models, each generated token requires a new forward pass (sequential, not parallelisable).

**DERIVED DESIGN:**
Given invariant 2: `torch.no_grad()` context disables gradient tracking, reducing memory by ~2× and compute by removing gradient operations.

Given invariant 3: LLM inference has a unique structure — a "prefill" phase (process all input tokens in parallel) and a "decode" phase (generate tokens one at a time):

```
Prefill: [all input tokens] → processed in parallel → KV cache
Decode:  [one new token]    → one forward pass       → one output
         [two tokens]       → one forward pass       → one output
         ... repeat until stop token
```

The KV cache (key-value cache) stores attention key and value matrices for all previously processed tokens, so the decode phase doesn't recompute attention over the full history — it only computes attention for the new token against the cached keys/values.

**THE TRADE-OFFS:**
**Gain:** Lower memory than training; no gradient storage; can be run on CPUs or consumer hardware with quantization.
**Cost:** Autoregressive decode is sequential — cannot be parallelised; latency grows with output length; KV cache grows with context length, consuming GPU memory.

---

### 🧪 Thought Experiment

**SETUP:**
Two LLM deployments: System A uses batch inference (process 64 requests simultaneously). System B uses streaming inference (process 1 request at a time, return tokens immediately).

**WHAT HAPPENS WITH BATCH INFERENCE (System A):**
64 requests wait in a queue. When the batch is full, all 64 are processed together — GPU utilisation is high (~80%), throughput is maximised (tokens/second/GPU). BUT: each user waits for the full batch to fill before getting their first token. Latency = queue wait + batch inference time.

**WHAT HAPPENS WITH STREAMING INFERENCE (System B):**
Each request starts immediately. The first token arrives in < 500ms. GPU utilisation is low (~15%) because small batches under-utilise the GPU. Throughput is 5× lower than System A.

**THE INSIGHT:**
Inference involves a fundamental trade-off between latency (time to first token, important for UX) and throughput (tokens/second/GPU, important for cost). Continuous batching (used by vLLM) attempts to solve this by dynamically adding new requests to in-progress batches, achieving near-batch throughput with near-streaming latency.

---

### 🧠 Mental Model / Analogy

> Think of inference as a chef executing a recipe. Training was learning the recipe (years of practice, many mistakes, gradual improvement). Inference is service — cooking dish after dish using the perfected recipe without changing it. The recipe (weights) stays the same. The inputs (customer orders) change. The chef's job is to execute the recipe as fast and consistently as possible.

Mapping:

- "Recipe" → trained model weights
- "Cooking a dish" → one forward pass
- "Customer order" → input prompt
- "Dish served" → model output (generated tokens)
- "Chef's speed" → inference latency
- "Dishes per hour" → inference throughput

Where this analogy breaks down: a chef can cook in parallel (multiple stations); autoregressive LLM decode is inherently sequential — each token depends on all previous tokens.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Inference is using the AI to answer questions. Training taught it; inference applies that teaching to new questions you ask it now.

**Level 2 — How to use it (junior developer):**
Always wrap inference in `torch.no_grad()` to disable gradient computation. Use `model.eval()` to disable dropout layers. Batch inputs for throughput; stream tokens for latency. Monitor inference latency (time to first token), throughput (tokens/sec), and memory usage (KV cache growth).

**Level 3 — How it works (mid-level engineer):**
LLM inference has two distinct phases: (1) **Prefill**: the entire prompt is processed in a single batched forward pass — highly parallelisable on GPU. (2) **Decode**: tokens are generated sequentially, one forward pass per token — inherently sequential. The KV cache (storing attention K and V matrices) avoids recomputing attention over prior tokens in each decode step. KV cache memory grows as: `2 × n_layers × n_heads × head_dim × seq_len × batch_size × dtype_bytes`. At long context (128K tokens) with large batches, KV cache memory can exceed model weight memory.

**Level 4 — Why it was designed this way (senior/staff):**
The prefill/decode split maps directly to GPU hardware characteristics. Prefill is memory-bandwidth-intensive (large matrix multiplications) — well-suited to GPU tensor cores. Decode is compute-light but sequential — often memory-bandwidth-bound, not compute-bound. This is why inference optimisers like vLLM use PagedAttention (managing KV cache like virtual memory with paging) and continuous batching (filling GPU with mixed prefill/decode work). At extreme scale (millions of requests/day), inference infrastructure cost dominates over training cost by 10–50×, making every inference optimisation (quantization, speculative decoding, caching) directly translate to operating cost reduction.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ PREFILL PHASE                               │
│ Input: "Translate to French: Hello World"  │
│ All tokens processed in parallel            │
│ KV cache populated for each token           │
│ Compute: high (GPU utilisation ~90%)        │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ DECODE PHASE — Token 1                      │
│ Input: [KV cache + new query position]     │
│ Forward pass → logits → sample "Bonjour"    │
│ Append "Bonjour" to context                 │
│ Compute: low per step (sequential)          │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ DECODE PHASE — Token 2                      │
│ Input: [KV cache + "Bonjour" position]     │
│ Forward pass → logits → sample "Monde"      │
│ Append "Monde" to context                   │
└──────────────┬──────────────────────────────┘
               ↓
        Continue until stop token or max_tokens
```

**KV Cache growth:**

```
seq_len=1000, batch=8, 32 layers, 32 heads:
32 × 32 × 128 × 1000 × 8 × 2 bytes ≈ 2.1 GB
seq_len=128K → 268 GB — exceeds GPU capacity!
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
HTTP request arrives (user prompt)
    ↓
Tokenisation
    ↓
[PREFILL ← INFERENCE STARTS HERE]
  All input tokens → forward pass
  KV cache populated
    ↓
[DECODE LOOP ← YOU ARE HERE]
  One token per forward pass
  KV cache grows each step
    ↓
Stop token reached / max_tokens hit
    ↓
Tokens decoded to text
    ↓
HTTP response returned
```

**FAILURE PATH:**

```
KV cache fills GPU memory (long context + large batch)
    ↓
OOM error during decode
    ↓
Request fails mid-generation
    ↓
User receives truncated or error response
```

**WHAT CHANGES AT SCALE:**
At high concurrency, batching becomes critical — multiple decode steps from different requests are batched together to maximise GPU utilisation. Continuous batching (vLLM, TGI) allows new requests to join an in-progress batch between decode steps. KV cache management becomes a memory scheduling problem: PagedAttention allocates KV cache in pages (like OS virtual memory) to prevent fragmentation and support variable-length sequences efficiently.

---

### 💻 Code Example

**Example 1 — Basic inference with correct settings:**

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-2-7b-hf"
)

# BAD: gradients computed unnecessarily
# output = model.generate(input_ids)

# GOOD: disable gradient computation for inference
model.eval()  # disable dropout
with torch.no_grad():  # disable gradient tracking
    inputs = tokenizer("Hello, world!", return_tensors="pt"
                       ).to("cuda")
    output = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.7,
        do_sample=True
    )
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

**Example 2 — Streaming inference for real-time UX:**

```python
from transformers import TextStreamer

streamer = TextStreamer(tokenizer, skip_prompt=True)

with torch.no_grad():
    model.generate(
        **inputs,
        max_new_tokens=200,
        streamer=streamer,  # tokens printed as generated
        temperature=0.7,
        do_sample=True
    )
# Tokens appear one by one in terminal — low TTFT
```

**Example 3 — Measuring inference metrics:**

```python
import time

def measure_inference(model, tokenizer, prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt"
                       ).to("cuda")
    n_input_tokens = inputs["input_ids"].shape[1]

    start = time.time()
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=100,
        )
    elapsed = time.time() - start

    n_output_tokens = output.shape[1] - n_input_tokens
    throughput = n_output_tokens / elapsed

    print(f"Input tokens: {n_input_tokens}")
    print(f"Output tokens: {n_output_tokens}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Throughput: {throughput:.1f} tokens/sec")
```

---

### ⚖️ Comparison Table

| Mode                       | Latency  | Throughput | GPU Use | Best For               |
| -------------------------- | -------- | ---------- | ------- | ---------------------- |
| Single request             | Lowest   | Lowest     | ~15%    | Development, testing   |
| **Batched inference**      | Medium   | Highest    | ~90%    | High-throughput APIs   |
| Streaming (token-by-token) | Low TTFT | Medium     | ~40%    | Real-time chat UX      |
| Continuous batching        | Low TTFT | High       | ~80%    | Production serving     |
| Speculative decoding       | Very low | High       | ~80%    | Latency-critical tasks |

**How to choose:** For production chat APIs, continuous batching (vLLM) provides the best balance. For batch processing (document analysis, embeddings), maximise batch size for throughput. For interactive apps, streaming is essential for good UX regardless of throughput cost.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- |
| "Inference is just running the model"        | Inference has two distinct phases (prefill + decode) with very different compute profiles   |
| "More GPU memory only matters for training"  | KV cache during long-context inference can consume more memory than model weights           |
| "Inference is cheap compared to training"    | At scale, cumulative inference spend dominates training spend by 10–50×                     |
| "Batching always reduces latency"            | Batching improves throughput but increases individual request latency due to queuing        |
| "torch.no_grad() is just for training loops" | It must be used in every production inference call to prevent unnecessary memory allocation |

---

### 🚨 Failure Modes & Diagnosis

**OOM During Decode (KV Cache Overflow)**

**Symptom:** `CUDA out of memory` error after successful prefill; occurs more frequently with long outputs or large batches.

**Root Cause:** KV cache grows with each generated token. Long sequences with large batches exhaust GPU VRAM during decode.

**Diagnostic Command / Tool:**

```python
# Monitor KV cache size during generation
import torch

def kv_cache_size_gb(n_layers, n_heads, head_dim,
                     seq_len, batch_size,
                     dtype_bytes=2) -> float:
    # 2× for keys and values
    return (2 * n_layers * n_heads * head_dim *
            seq_len * batch_size * dtype_bytes) / 1e9

# For Llama-2-7B: 32 layers, 32 heads, head_dim=128
print(kv_cache_size_gb(32, 32, 128, 4096, 8))
# → ~8.6 GB
```

**Fix:** Reduce batch size; reduce `max_new_tokens`; use quantized KV cache (int8); use PagedAttention (vLLM).

**Prevention:** Set KV cache memory budgets per request; cap `max_new_tokens` based on available memory.

---

**Slow First-Token Latency (Prefill Bottleneck)**

**Symptom:** Model takes 2–5 seconds to produce the first token on long prompts, then generates subsequent tokens quickly.

**Root Cause:** Prefill phase processes all input tokens in a single forward pass — long prompts require more compute. Attention is O(n²) in sequence length.

**Diagnostic Command / Tool:**

```bash
# Use vLLM's built-in benchmarking
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-hf \
  --enable-prefix-caching  # cache shared prefixes
```

**Fix:** Enable prefix caching for shared prompt prefixes. Use Flash Attention 2 for faster attention computation on long sequences.

**Prevention:** Design prompts to be as concise as possible; avoid unnecessary context in system prompts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Model Weights` — inference loads and uses frozen weights; understanding weight loading is prerequisite
- `Model Parameters` — inference is the read-only use of trained parameters
- `Neural Network` — inference is running the forward pass of a neural network

**Builds On This (learn these next):**

- `Context Window` — the maximum sequence length that fits in one inference forward pass
- `Temperature` — sampling strategy applied at the output of each inference step
- `Latency vs Throughput (AI)` — the core trade-off in production inference system design

**Alternatives / Comparisons:**

- `Training` — the opposite phase: updates weights, requires gradients, 10–20× more memory
- `Model Quantization` — reduces weight precision to speed inference and reduce memory
- `Fine-Tuning` — a hybrid: uses inference-like forward passes but with training-like gradient updates on a small dataset

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Running a trained model on new inputs     │
│              │ with frozen weights — no learning         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Training and deployment are different     │
│ SOLVES       │ phases with different resource needs —    │
│              │ inference is the deployment phase         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Autoregressive inference is sequential    │
│              │ (one token at a time) — KV cache makes    │
│              │ this manageable but not parallelisable    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any production deployment of a model —   │
│              │ always use no_grad() and model.eval()     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never run inference without no_grad() —  │
│              │ it wastes memory and compute on gradients │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Latency (streaming, small batches) vs     │
│              │ throughput (batching, GPU utilisation)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The exam — all the learning is done;    │
│              │ now we apply it, one question at a time." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ KV Cache → Quantization → vLLM serving   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are running a 70B model on 4 A100s (80 GB each) using tensor parallelism. A user sends a prompt of 100K tokens. Trace what happens during the prefill phase across the 4 GPUs: how is the computation distributed, what communication occurs between GPUs, and where does the bottleneck appear as context length increases from 8K to 100K tokens?

**Q2.** A team builds a RAG system where the same system prompt (3,000 tokens of company policies) is prepended to every user request. With 10,000 daily active users, this means 3,000 tokens × 10,000 requests = 30M tokens processed for prefill daily on the system prompt alone. What caching mechanism eliminates this redundant compute, how does it work at the KV cache level, and what constraint determines whether it works correctly?
