---
layout: default
title: "Latency vs Throughput (AI)"
parent: "AI Foundations"
nav_order: 1609
permalink: /ai-foundations/latency-vs-throughput-ai/
number: "1609"
category: AI Foundations
difficulty: ★★★
depends_on: Inference, Model Parameters, Model Quantization
used_by: Model Quantization, Inference, Foundation Models
related: Inference, Model Quantization, Context Window
tags:
  - ai
  - performance
  - advanced
  - systems
  - trade-off
---

# 1609 — Latency vs Throughput (AI)

⚡ TL;DR — In AI inference, latency is the time to generate one response; throughput is the number of requests processed per second. They are in fundamental tension — optimising one often degrades the other — and the right trade-off depends entirely on your use case.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team deploys an LLM API with a GPU cluster. They receive a complaint from the interactive chatbot team: responses take 8 seconds — users abandon conversations. They also receive a complaint from the batch processing team: they can only process 12 documents per minute, making overnight batch jobs take 14 hours. Both teams want better performance. Without a framework distinguishing latency from throughput — and understanding their trade-offs — the team makes optimisations that help one team and hurt the other.

**THE BREAKING POINT:**
A single AI inference serving stack must often serve both interactive (latency-sensitive) and batch (throughput-sensitive) workloads. Without understanding the latency-throughput trade-off, teams either serve every request with minimum batch size (wasting GPU efficiency) or maximise batching (making interactive responses unacceptably slow).

**THE INVENTION MOMENT:**
The latency vs. throughput framework from distributed systems applies directly to AI inference: latency = time per individual request; throughput = total requests per unit time. In LLM serving, these are connected but opposing forces — and understanding the mechanism enables intelligent serving decisions.

---

### 📘 Textbook Definition

**Latency** in AI inference is the wall-clock time elapsed from input submission to complete output generation — comprising prompt processing (prefill) time plus token generation (decode) time. **Throughput** is the number of tokens (or requests) generated per unit time across all concurrent requests. For LLM serving, the primary mechanisms governing this trade-off are: **batching** (serving multiple requests simultaneously on a GPU to improve throughput at the cost of individual request latency), **continuous batching** (dynamic batching that minimises latency overhead), and **memory bandwidth vs. compute utilisation** (the fundamental hardware constraint driving the trade-off at the matrix multiplication level).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Latency = how fast one request is answered; throughput = how many requests are answered per second. More batching = better throughput, worse latency.

**One analogy:**
> **Latency:** A restaurant that serves one table at a time cooks each dish immediately upon order — maximum freshness, minimum wait for that one diner.
>
> **Throughput:** A cafeteria batches orders — waits until 20 people are in line before cooking. Each individual waits longer, but the kitchen serves far more people per hour.
>
> **The trade-off:** A sushi conveyor belt is the continuous batching solution — near-real-time service at near-batch efficiency.

**One insight:**
GPU utilisation is the core tension. Modern GPUs are compute-bound at batch size ≥ 16 but memory-bandwidth-bound at batch size 1. A single request at batch size 1 uses perhaps 20% of GPU compute. Batching 16 requests together uses 100% of GPU compute — but each request waits ~3× longer for its response.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. LLM inference has two phases: **prefill** (process all input tokens in parallel — compute-bound) and **decode** (generate output tokens one at a time — memory-bandwidth-bound).
2. GPU batch matmul is the fundamental operation. At batch size 1, most GPU compute units are idle (memory bandwidth saturated before compute). At larger batch sizes, compute utilisation improves dramatically.
3. Batching multiplies GPU efficiency — at the cost of making each request wait for the batch to be assembled.

**DERIVED DESIGN:**

```
LLM INFERENCE COMPONENTS:

PREFILL (input processing):
  All input tokens processed in PARALLEL
  O(seq_len) GPU operations
  Compute-bound (benefits from batching less)

DECODE (output generation):
  One token generated per forward pass
  Memory-bound: must load all model weights
  for each token → bandwidth bottleneck
  Benefits enormously from batching:
    Batch 1: loads weights once, generates 1 token
    Batch 8: loads weights once, generates 8 tokens
    → 8× throughput improvement at same bandwidth cost!

LATENCY = Prefill_time + (n_output_tokens × decode_time_per_token)

THROUGHPUT = Total_tokens_generated / second
           = (batch_size × decode_tokens) / decode_time
```

**THE TRADE-OFFS:**
Batch size 1: minimum latency, poor GPU utilisation (~20%), low throughput.
Batch size 32: 2–5× higher latency per request, near-optimal GPU utilisation, very high throughput.
Continuous batching: dynamically adds/removes requests; targets the best of both.

---

### 🧪 Thought Experiment

**SETUP:**
You have a 70B-parameter LLM, an A100 GPU (80GB), and two workloads:
- Workload A: 1,000 interactive chat users (must respond in < 2 seconds for a 200-token response)
- Workload B: Batch processing 10,000 documents overnight (throughput matters, latency doesn't)

**WHAT HAPPENS WITH SAME CONFIG:**
Serving Workload A with batch_size=32 (tuned for throughput): latency spikes to 6 seconds per response — users leave.

Serving Workload B with batch_size=1 (tuned for latency): processes 10,000 documents in 28 hours — misses the overnight window.

**THE OPTIMAL SOLUTION:**
Different serving configurations for different workloads:

Interactive chat: continuous batching with max_batch=4, priority queue for low-latency requests. Achieves 1.8s latency.

Batch processing: batch_size=32, no latency target. Achieves 10,000 docs in 3.5 hours.

**THE INSIGHT:**
"Optimal AI serving" has no universal answer — it's always relative to the latency SLA and throughput requirement of the workload. The fundamental question is: what are users actually waiting for, and what is the cost of making them wait?

---

### 🧠 Mental Model / Analogy

> Think of GPU inference like a freight vs. passenger train trade-off. A passenger train departs immediately, carrying few passengers, getting each person to the destination quickly. A freight train waits to fill all cars before departing — much slower per unit, but dramatically more goods moved per journey. The GPU is the locomotive — it carries far more weight if you fill it before departure. The question is whether your users are passengers (care about their personal arrival time) or cargo (care about total delivery volume).

Mapping:
- "Locomotive" → GPU compute
- "Passenger train" → batch size 1 (low latency serving)
- "Freight train" → large batch serving (high throughput)
- "Waiting to fill the train" → batching wait time (added latency)
- "Total goods moved per journey" → throughput (tokens/second)

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Latency = how fast you get your answer. Throughput = how many answers the system produces per second. Making the system answer everyone faster usually means it answers each person a bit slower.

**Level 2 — How to use it (junior developer):**
Key serving parameters to tune: `max_batch_size` (higher = more throughput, higher latency), `max_tokens_per_request` (limits tail latency), `timeout` (how long to wait before sending a partial batch — critical for interactive use). Use streaming responses (stream=True in OpenAI API) to reduce PERCEIVED latency — the user sees tokens as they're generated rather than waiting for the complete response. For batch workloads, disable streaming and maximise batch size.

**Level 3 — How it works (mid-level engineer):**
**Continuous batching** (Orca, vLLM) solves the static batching problem. Traditional batching: wait for N requests, process together, return all. Problem: one long request blocks all others. Continuous batching: on each decode step, add new requests to the in-flight batch and remove completed ones. Results: GPU utilisation improves from ~40% (static batching) to ~60–85% (continuous batching) with dramatically better P50 latency at the same P99. **PagedAttention** (vLLM) extends this by managing KV-cache memory in pages — allowing memory to be allocated dynamically and shared between requests with the same prefix (prefix caching).

**Level 4 — Why it was designed this way (senior/staff):**
The fundamental reason latency and throughput trade off is the memory bandwidth wall. The A100 GPU has 2TB/s memory bandwidth. A 70B-parameter model in fp16 = 140GB. Loading the full model weights for a single forward pass takes 140GB / 2TB/s = 70ms at minimum — this is the irreducible memory-bandwidth bound on decode latency. At batch_size=1, those 70ms of bandwidth access generate 1 output token. At batch_size=32, the same 70ms generates 32 tokens — throughput 32×, latency unchanged. This is why batching improves throughput so dramatically for memory-bound decode: the bandwidth cost is amortised across the batch. Above the compute-bound threshold (~batch_size 128 for attention), adding more requests doesn't improve throughput further — you've maxed out both compute and bandwidth.

---

### ⚙️ How It Works (Mechanism)

```
GPU UTILISATION VS BATCH SIZE:

Batch Size │ GPU Utilisation │ Throughput (tok/s) │ Latency
───────────┼─────────────────┼────────────────────┼──────────
    1      │     ~20%        │      150           │  100ms/tok
    4      │     ~50%        │      450           │  120ms/tok
    16     │     ~85%        │    1,200           │  170ms/tok
    32     │     ~95%        │    2,000           │  240ms/tok
    64     │     ~95%        │    2,100           │  440ms/tok
   128     │     ~95%        │    2,150           │  850ms/tok

At ~batch_size 32: memory bandwidth bottleneck exhausted
Above ~batch_size 64: compute bottleneck — adding requests
                      no longer helps throughput

STREAMING EFFECT ON PERCEIVED LATENCY:
Without streaming: user waits 10 seconds for 200 tokens
With streaming: user sees first token in 200ms,
                full response over 10 seconds
                → dramatically better user experience
                  same server-side latency
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (setting up a serving system):**
```
Define workload:
  Interactive? → P50 latency target
  Batch? → throughput target, latency budget
    ↓
Profile model:
  Measure decode latency at batch_sizes 1,4,8,16,32
  Find the batch size where latency SLA breaks
    ↓
Configure serving system:
  max_batch_size = max size where latency ≤ SLA
  continuous batching ON for interactive
  streaming ON for interactive
    ↓
[SERVING ← YOU ARE HERE]
    ↓
Monitor:
  P50, P95, P99 latency per request type
  GPU utilisation
  Tokens/second served
  Queue depth (if rising → add capacity)
    ↓
Tune based on observed trade-offs
```

---

### 💻 Code Example

**Example 1 — Streaming for perceived latency:**
```python
import openai

def stream_response(prompt: str, client) -> str:
    """Stream tokens for better perceived latency."""
    full_text = []
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            token = chunk.choices[0].delta.content
            print(token, end="", flush=True)  # real-time
            full_text.append(token)
    return "".join(full_text)
```

**Example 2 — vLLM offline batch inference:**
```python
from vllm import LLM, SamplingParams

# High-throughput batch mode
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,  # multi-GPU
    max_num_seqs=256,         # max concurrent sequences
    gpu_memory_utilization=0.9
)

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=512
)

# All prompts processed together — maximum GPU utilisation
prompts = [f"Summarise: {doc}" for doc in documents]
outputs = llm.generate(prompts, sampling_params)
```

**Example 3 — Latency profiling:**
```python
import time
import statistics

def profile_batch_latency(
    prompts: list[str],
    batch_sizes: list[int],
    llm
) -> dict:
    """Profile P50/P95 latency for each batch size."""
    results = {}
    for bs in batch_sizes:
        batch = prompts[:bs]
        latencies = []
        for _ in range(10):  # 10 iterations
            start = time.perf_counter()
            llm.generate(batch)
            latencies.append(time.perf_counter() - start)
        results[bs] = {
            "p50": statistics.median(latencies),
            "p95": sorted(latencies)[int(len(latencies)*0.95)]
        }
    return results
```

---

### ⚖️ Comparison Table

| Serving Mode | Latency | Throughput | GPU Util | Best For |
|---|---|---|---|---|
| Batch_size=1, no streaming | Lowest | Lowest | ~20% | Single-user dev testing |
| Batch_size=1, streaming | Same (perceived lower) | Lowest | ~20% | Interactive single-user |
| Static batching (bs=32) | High | High | ~90% | Batch processing |
| **Continuous batching** | Low-medium | High | ~70–85% | Mixed workloads |
| Speculative decoding | Lower (same GPU) | Same | ~90% | Latency-critical |
| Multi-GPU tensor parallel | Lower (multi-GPU) | Same per GPU | ~90% | Large models |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A faster GPU always means lower latency" | A faster GPU mainly helps throughput; memory-bandwidth-bound decode latency improves only with higher-bandwidth HBM, not raw compute |
| "Larger batch size always helps" | Above the memory-bandwidth saturation point (~bs=32 for 70B model on A100), adding requests improves latency for newly added requests but hurts existing requests |
| "Streaming reduces latency" | Streaming reduces PERCEIVED latency (time to first token); total generation time is identical |
| "High GPU utilisation means low latency" | GPU utilisation measures efficiency, not latency; a heavily batched system has high GPU utilisation AND high per-request latency |
| "Throughput and latency are both in the SLA" | Interactive SLAs care about P95 latency; batch SLAs care about total completion time; these require different serving optimisations |

---

### 🚨 Failure Modes & Diagnosis

**Memory OOM (Out-of-Memory) Under Load**

**Symptom:** Serving system works fine at low load. Under peak load, OOM errors appear and serving crashes or degrades.

**Root Cause:** KV-cache for all in-flight requests exceeds GPU memory. At large batch sizes, each request's KV-cache uses substantial memory. At batch_size=32 with 2,048 context tokens per request, KV-cache can consume 10–30GB on a 70B model.

**Diagnostic Command / Tool:**
```python
# Monitor GPU memory during serving
import subprocess

def monitor_gpu_memory() -> dict:
    """Check GPU memory usage."""
    result = subprocess.run(
        ["nvidia-smi",
         "--query-gpu=memory.used,memory.total",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True
    )
    used, total = result.stdout.strip().split(", ")
    utilisation = int(used) / int(total)
    print(f"GPU Memory: {used}MiB / {total}MiB "
          f"({utilisation:.1%})")
    if utilisation > 0.90:
        print("WARNING: High memory — OOM risk under load")
    return {"used": int(used), "total": int(total)}
```

**Fix:** Reduce `max_num_seqs`; enable PagedAttention (vLLM); set `max_tokens` limits; use quantisation to reduce model footprint.

**Prevention:** Load-test at expected peak concurrency; set `gpu_memory_utilization=0.85` (leave buffer for KV-cache growth).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inference` — latency and throughput are properties of the inference serving system
- `Model Parameters` — model size is the primary determinant of memory bandwidth requirements
- `Model Quantization` — reduces model size, directly improving throughput and latency

**Builds On This (learn these next):**
- `Model Quantization` — the primary technique for improving the latency-throughput trade-off
- `Inference` — understanding the full inference pipeline is needed to optimise it
- `Foundation Models` — large foundation models face the most acute latency-throughput challenges

**Alternatives / Comparisons:**
- `Context Window` — longer context increases prefill time and KV-cache size, affecting both latency and throughput
- `Model Quantization` — trading accuracy for improved latency/throughput
- `Inference` — the parent concept; this entry focuses on its serving-level trade-offs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Latency = time per request;               │
│              │ Throughput = requests served per second   │
│              │ They trade off via batch size             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Decode is MEMORY-BANDWIDTH-BOUND:         │
│              │ batching amortises bandwidth cost →       │
│              │ huge throughput gain at small latency cost│
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSIS    │ P50 latency too high → reduce batch size  │
│              │ Throughput too low → increase batch size  │
│              │ GPU utilisation low → increase batching   │
├──────────────┼───────────────────────────────────────────┤
│ TOOLBOX      │ Continuous batching (vLLM/Orca),          │
│              │ PagedAttention, streaming, quantisation   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Every unit of throughput gained costs     │
│              │ latency for existing in-flight requests   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fill the GPU like a freight train —      │
│              │ but not if users are waiting at the       │
│              │ station."                                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Model Quantization → Inference →          │
│              │ vLLM / Triton Inference Server            │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are building an LLM serving system that must handle two types of workloads on the same GPU cluster: (1) real-time chatbot with a P95 latency SLA of 500ms for the first token, and (2) background document summarisation with no latency requirement but a throughput target of 5,000 documents per hour. Design the scheduling and serving architecture — including how you would priority-queue requests, what batch sizes to target for each workload, and how continuous batching interacts with your priority queuing when both workloads have concurrent demand.

**Q2.** A team observes that their P50 latency is acceptable (1.2s) but P99 latency is catastrophic (45s). Investigation reveals the P99 latency spikes correlate with long input sequences (> 3,000 tokens). Explain the two distinct mechanisms by which long context lengths increase inference latency, and design a serving-level mitigation for each that doesn't require retraining the model.
