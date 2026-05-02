---
layout: default
title: "Model Quantization"
parent: "AI Foundations"
nav_order: 1610
permalink: /ai-foundations/model-quantization/
number: "1610"
category: AI Foundations
difficulty: ★★★
depends_on: Model Weights, Model Parameters, Inference
used_by: Latency vs Throughput (AI), Model Pruning, Distillation
related: Model Weights, Model Pruning, Distillation
tags:
  - ai
  - performance
  - advanced
  - systems
  - optimization
---

# 1610 — Model Quantization

⚡ TL;DR — Model quantization reduces the numerical precision of model weights and activations (e.g., from 32-bit floats to 4-bit integers) to dramatically reduce memory footprint and inference latency, at a typically small cost to model quality.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 70B-parameter LLM in 32-bit floating point requires 280GB of GPU memory just to hold the weights. No single consumer GPU (24GB) can run it. Even professional hardware requires four A100 GPUs (80GB each). Running inference is expensive and slow. For deployment at scale, every inference request requires 280GB+ of memory bandwidth — making throughput low and cost per token high.

**THE BREAKING POINT:**
LLMs are getting larger — 70B, 405B, 1T+ parameters. GPU memory is a hard wall (80GB on an A100). Without techniques to compress models into less memory, the cost of serving state-of-the-art AI is prohibitive for most organisations, and deployment on edge devices is impossible.

**THE INVENTION MOMENT:**
Quantization borrows from signal processing and hardware engineering: instead of storing each weight as a high-precision 32-bit float (fp32) or 16-bit float (fp16), reduce it to 8-bit, 4-bit, or even 2-bit integers. The information loss from reduced precision is often negligible — most model behaviour is captured at 4-bit precision, with only marginal quality loss.

---

### 📘 Textbook Definition

**Model quantization** is the process of reducing the numerical precision of a neural network's weights and/or activations from floating-point representations (fp32, fp16, bf16) to lower-bit integer representations (int8, int4, int2). This reduces memory footprint proportionally to the precision reduction (fp16→int4 = 4× smaller model), reduces memory bandwidth requirements at inference (faster decode), and can reduce compute cost on hardware with native int operations. Quantization is classified by timing: **post-training quantization (PTQ)** applies quantization to a pretrained model without retraining; **quantization-aware training (QAT)** incorporates quantization effects during training, typically achieving higher quality at lower bit depths.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Quantization shrinks model weights from 16-bit floats to 4-bit integers — making models 4× smaller and faster, with minimal quality loss.

**One analogy:**

> Imagine storing a detailed photograph. The original TIFF file (uncompressed, full precision) is 50MB. Saving it as a high-quality JPEG is 5MB — 10× smaller, visually nearly identical. Saving as low-quality JPEG is 500KB — some artefacts visible. Quantization is the JPEG compression of neural networks: the weights are stored at lower precision, the model "looks" nearly the same at 4-bit but starts to show artefacts at 1-bit.

**One insight:**
Quantization works because neural networks are remarkably tolerant of small numerical errors in individual weights. The model's emergent behaviour is an aggregate over billions of weights — small rounding errors in each weight largely cancel out at the prediction level. This makes 4-bit quantization viable with < 1% quality degradation in most tasks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. fp32 stores each weight in 32 bits (4 bytes); int4 stores each weight in 4 bits (0.5 bytes) — 8× memory reduction.
2. The quantization error for a single weight = rounding error; the aggregate effect across billions of weights is stochastic and partially cancels.
3. Lower bit depth = higher rounding error per weight; at some threshold (typically 2-3 bits), error accumulation degrades model quality significantly.

**DERIVED DESIGN:**

```
PRECISION OPTIONS:

fp32: 32-bit float  → 4 bytes/weight
fp16: 16-bit float  → 2 bytes/weight  (baseline)
bf16: 16-bit bfloat → 2 bytes/weight  (better range)
int8: 8-bit integer → 1 byte/weight   → 2× smaller
int4: 4-bit integer → 0.5 bytes/weight → 4× smaller
int2: 2-bit integer → 0.25 bytes/weight → 8× smaller*
  *significant quality degradation

70B MODEL SIZES:
fp16:  140 GB → needs 2× A100 (80GB)
int8:   70 GB → fits on 1× A100 (80GB)
int4:   35 GB → fits on 2× consumer RTX 3090 (24GB)
int4:   35 GB → fits on 1× A100 with room for KV-cache

QUANTIZATION TYPES:
Weight-only (W4A16): weights in int4, activations in fp16
  → 4× memory reduction; good quality
Activation quantization (W8A8): weights AND activations in int8
  → hardware accelerated matrix multiply (Tensor Cores)
  → fastest throughput on supported hardware (NVIDIA H100)
```

**THE TRADE-OFFS:**
**Gain:** 2–8× memory reduction; proportional bandwidth reduction (faster decode); hardware integer compute (further speedup on H100).
**Cost:** Quantization error (typically < 1% quality degradation at int4; 5–15% at int2); calibration overhead; some tasks (long context, reasoning) are more sensitive to quantization than others.

---

### 🧪 Thought Experiment

**SETUP:**
You have a 7B-parameter LLM. It achieves a benchmark score of 76.3% on MMLU in fp16. You apply four quantization levels and measure quality degradation.

**RESULTS:**

```
fp16 (baseline):  76.3% MMLU, 14GB VRAM
int8 (GPTQ):      76.1% MMLU, 7GB VRAM  → -0.2% quality, 2× smaller
int4 (GPTQ):      75.6% MMLU, 3.5GB VRAM → -0.7% quality, 4× smaller
int3 (GGUF):      73.1% MMLU, 2.6GB VRAM → -3.2% quality, 5.4× smaller
int2 (GPTQ):      68.0% MMLU, 1.75GB VRAM → -8.3% quality, 8× smaller
```

**THE INSIGHT:**
The quality degradation is NOT linear with bit depth reduction. int8 is nearly indistinguishable from fp16 — the rounding error per weight is tiny. int4 is still excellent — most LLM deployments use int4. int2 starts showing meaningful degradation. The "sweet spot" for most production use cases is int4: 4× memory reduction with < 1% quality cost. This is why llama.cpp, ollama, and most consumer LLM tools default to 4-bit quantization.

---

### 🧠 Mental Model / Analogy

> Quantization is like converting your bookshelf from hardcover books to pocket paperbacks. The words are identical — the story doesn't change. The shelf is 3× less full. Individual page quality is slightly lower (smaller font, thinner paper). For most reading purposes (skimming, referencing key passages), the pocket edition is fine. For extremely detailed technical diagrams or fine print, you might occasionally wish for the hardcover. But for 95% of uses, the pocket edition works perfectly and you can carry 3× as many books.

Mapping:

- "Hardcover books" → fp16/fp32 weights
- "Pocket paperbacks" → int4/int8 weights
- "Words are identical" → model predictions nearly identical
- "Shelf 3× less full" → 3–4× memory reduction
- "Fine print sometimes clearer in hardcover" → edge cases where quantization degrades nuanced reasoning

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Quantization makes AI models smaller by storing their numbers less precisely — like saving a photo as JPEG instead of RAW. The result looks nearly the same but takes 4× less space.

**Level 2 — How to use it (junior developer):**
In practice, use existing libraries. For llama.cpp/GGUF models, download the Q4_K_M or Q5_K_M quantized version — the most popular formats for consumer hardware. For Hugging Face models, use BitsAndBytes for 4-bit loading: `BitsAndBytesConfig(load_in_4bit=True)`. For GPTQ quantized models, use AutoGPTQ. Rule of thumb: Q4_K_M is the best quality-size trade-off for most use cases.

**Level 3 — How it works (mid-level engineer):**
**Post-training quantization (PTQ) — the GPTQ algorithm:** (1) For each weight matrix, find the quantization scale that minimises the output error — not just the weight error. (2) Use a calibration dataset (128–512 samples) to measure which quantization errors have the largest impact on output. (3) Sequentially quantize weights, compensating for accumulated error using the Hessian of the loss. This "layerwise" quantization with error compensation is why GPTQ outperforms naïve round-to-nearest. **GGUF (llama.cpp) k-quants:** Divide weights into blocks of 32 values. Store the block's scale factor and zero point in fp16; store individual weights in 4-bit. This "grouped quantization" amortises precision over blocks, reducing the impact of outlier weights.

**Level 4 — Why it was designed this way (senior/staff):**
The key insight driving quantization research is that neural network weight distributions are not uniform — they are approximately Gaussian with significant outliers. Naive uniform int8 quantization (map the min-max range to 0–255) wastes most precision on outliers, leaving most weights poorly quantized. SmoothQuant (Xiao et al., 2022) addresses activation quantization difficulty by migrating quantization difficulty from activations (which have large outliers) to weights (which don't) via a mathematically equivalent rescaling. SpQR (Dettmers et al., 2023) handles weight outliers by storing them in higher precision (fp16) while quantizing the remaining 99% of weights to 4-bit — targeting the Pareto optimal frontier of quality vs. compression. These techniques demonstrate that quantization quality is primarily determined by how well the method handles outliers in the weight and activation distributions.

---

### ⚙️ How It Works (Mechanism)

```
QUANTIZATION MATH (simplified):

fp16 weight w ∈ [-7.23, 8.41] for a weight matrix

Step 1: Find scale and zero point
  scale = (max - min) / (2^bits - 1)
        = (8.41 - (-7.23)) / 15  [for int4]
        = 1.0427

  zero_point = round(-min / scale)
             = round(7.23 / 1.0427)
             = 7

Step 2: Quantize weights
  w_quantized = round(w / scale) + zero_point
  [integer in range 0–15 for int4]

Step 3: Dequantize at inference
  w_reconstructed = (w_quantized - zero_point) × scale

QUANTIZATION ERROR:
  Original w = 3.14
  w_q = round(3.14 / 1.0427) + 7 = round(3.01) + 7 = 10
  w_reconstructed = (10 - 7) × 1.0427 = 3.13
  Error = 0.01 (< 1%)
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Start with fp16 pretrained model
    ↓
Choose quantization target:
  int4 (recommended for most use cases)
  int8 (if quality critical)
    ↓
Choose method:
  PTQ (no GPU for training, fast)
  QAT (better quality, requires training)
    ↓
[QUANTIZE ← YOU ARE HERE]
Apply GPTQ / GGUF / BitsAndBytes
  with calibration dataset
    ↓
Validate: measure quality on benchmark
  vs. fp16 baseline
    ↓
If quality acceptable → deploy
If quality degraded → try higher bit depth
                   or QAT
    ↓
Serve quantized model
  (4× less memory, ~2× higher throughput)
```

---

### 💻 Code Example

**Example 1 — 4-bit loading with BitsAndBytes:**

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Load 70B model in 4-bit — fits on ~40GB GPU instead of 140GB
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,  # nested quantization
    bnb_4bit_quant_type="nf4"        # NF4 = best quality 4-bit
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)
```

**Example 2 — GPTQ quantization:**

```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-2-7b-hf"
)
# Calibration dataset — 128 samples from target domain
examples = [
    tokenizer(text, return_tensors="pt")
    for text in calibration_texts[:128]
]

quantize_config = BaseQuantizeConfig(
    bits=4,            # 4-bit quantization
    group_size=128,    # grouped quantization block size
    desc_act=False     # activations in fp16
)

model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantize_config=quantize_config
)
model.quantize(examples)
model.save_quantized("llama-2-7b-gptq-4bit")
```

**Example 3 — Measure quantization quality degradation:**

```python
def compare_quantization_quality(
    fp16_model,
    quantized_model,
    eval_texts: list[str],
    tokenizer
) -> dict:
    """Compare perplexity: lower = better quality."""
    import torch
    import math

    def compute_perplexity(model, texts):
        losses = []
        for text in texts:
            inputs = tokenizer(
                text, return_tensors="pt"
            ).to(model.device)
            with torch.no_grad():
                output = model(**inputs, labels=inputs["input_ids"])
            losses.append(output.loss.item())
        return math.exp(sum(losses) / len(losses))

    fp16_ppl = compute_perplexity(fp16_model, eval_texts)
    quant_ppl = compute_perplexity(quantized_model, eval_texts)
    degradation = (quant_ppl - fp16_ppl) / fp16_ppl * 100

    print(f"fp16 perplexity: {fp16_ppl:.2f}")
    print(f"Quantized perplexity: {quant_ppl:.2f}")
    print(f"Degradation: {degradation:+.1f}%")
    return {"fp16": fp16_ppl, "quantized": quant_ppl,
            "degradation_pct": degradation}
```

---

### ⚖️ Comparison Table

| Method               | Bit Depth | Memory       | Quality         | Requires Training | Best For                   |
| -------------------- | --------- | ------------ | --------------- | ----------------- | -------------------------- |
| fp16 baseline        | 16-bit    | 2 bytes/w    | Best            | No                | Quality-critical inference |
| **GPTQ int4**        | 4-bit     | 0.5 bytes/w  | Excellent       | No (PTQ)          | Production default         |
| **BitsAndBytes NF4** | 4-bit     | 0.5 bytes/w  | Excellent       | No (PTQ)          | Fast dev, fine-tuning      |
| **GGUF Q4_K_M**      | ~4.5-bit  | ~0.6 bytes/w | Very good       | No (PTQ)          | CPU inference, ollama      |
| int8 (SmoothQuant)   | 8-bit     | 1 byte/w     | Near-lossless   | No (PTQ)          | Quality-first serving      |
| QAT (4-bit)          | 4-bit     | 0.5 bytes/w  | Better than PTQ | Yes               | High-value small models    |
| int2 (GPTQ)          | 2-bit     | 0.25 bytes/w | Noticeable loss | No                | Extreme edge deployment    |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                     |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Quantization always degrades quality significantly"    | int4 typically causes < 1% quality degradation on standard benchmarks; int8 is nearly lossless                                                              |
| "Quantization speeds up compute"                        | Quantization mainly reduces MEMORY bandwidth (faster decode); compute speedup depends on hardware support for int operations (H100 has better int8 support) |
| "All quantization methods are equivalent"               | GPTQ significantly outperforms round-to-nearest at the same bit depth by using calibration data; method choice matters                                      |
| "You should quantize to the lowest bit depth available" | Use the highest bit depth your VRAM budget allows; int4 is the practical minimum for production quality; don't use int2 unless there's no alternative       |
| "Quantization replaces fine-tuning"                     | Quantization and fine-tuning are orthogonal: you can fine-tune a quantized model (QLoRA) or quantize after fine-tuning                                      |

---

### 🚨 Failure Modes & Diagnosis

**Quality Degradation on Domain-Specific Tasks**

**Symptom:** Quantized model performs well on standard benchmarks (MMLU, HellaSwag) but produces poor results on your specific use case (e.g., code generation, medical terminology, long-form reasoning).

**Root Cause:** PTQ calibration data was general (Wikipedia, C4) and doesn't represent your domain. Quantization minimises error on the calibration distribution — domain-specific knowledge encoded in weights that don't activate during general calibration is poorly quantized.

**Diagnostic Command / Tool:**

```python
def diagnose_quantization_gap(
    fp16_model,
    quantized_model,
    domain_texts: list[str],
    general_texts: list[str],
    tokenizer
) -> None:
    """Compare domain-specific vs general degradation."""
    domain_gap = measure_perplexity_gap(
        fp16_model, quantized_model, domain_texts, tokenizer
    )
    general_gap = measure_perplexity_gap(
        fp16_model, quantized_model, general_texts, tokenizer
    )

    print(f"General perplexity gap: {general_gap:+.2f}")
    print(f"Domain perplexity gap:  {domain_gap:+.2f}")

    if domain_gap > 2 * general_gap:
        print("DOMAIN-SPECIFIC DEGRADATION DETECTED")
        print("Fix: Re-quantize with domain-specific "
              "calibration data")
```

**Fix:** Re-quantize using domain-specific calibration data from your actual use case. Use QAT if PTQ quality is insufficient.

**Prevention:** Always validate quantized models on your specific workload — not just general benchmarks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Model Weights` — quantization directly modifies how model weights are stored and computed
- `Model Parameters` — parameter count determines how much benefit quantization provides
- `Inference` — quantization is an inference optimisation technique; applied at serving time

**Builds On This (learn these next):**

- `Latency vs Throughput (AI)` — quantization directly improves both by reducing memory bandwidth requirements
- `Model Pruning` — complementary compression technique: removes weights entirely rather than reducing precision
- `Distillation` — alternative compression: trains a smaller model to mimic a larger one

**Alternatives / Comparisons:**

- `Model Pruning` — reduces parameter count; quantization reduces precision; can be combined
- `Distillation` — trains a smaller model; typically better quality than quantization at same size, but requires training
- `Model Weights` — the underlying data that quantization compresses

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reducing weight precision from fp16 to    │
│              │ int4/int8 — 2–8× memory reduction with   │
│              │ minimal quality loss                      │
├──────────────┼───────────────────────────────────────────┤
│ KEY NUMBERS  │ fp16 → int4: 4× smaller, <1% quality loss│
│              │ fp16 → int8: 2× smaller, ~0% quality loss│
│              │ fp16 → int2: 8× smaller, 5–15% loss      │
├──────────────┼───────────────────────────────────────────┤
│ DEFAULT REC  │ Use int4 (NF4/GPTQ Q4_K_M) for           │
│              │ production — best quality/size trade-off  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Model doesn't fit in VRAM; serving cost   │
│              │ too high; edge/mobile deployment          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Maximum quality required; very short      │
│              │ generation tasks (where latency gain      │
│              │ is negligible vs quality cost)            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Store numbers less precisely —           │
│              │ models tolerate it far better than        │
│              │ you'd expect."                            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Model Pruning → Distillation →            │
│              │ QLoRA (quantized fine-tuning)             │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team applies int4 PTQ (post-training quantization) to a 70B model and finds that performance on their coding benchmark degrades from 81% to 73% — a 8-point gap much larger than the 1% reported in academic benchmarks. Their calibration set consisted of 128 randomly sampled Wikipedia passages. Describe in detail why their calibration data choice caused disproportionate degradation on code generation, and redesign their quantization pipeline to achieve < 2% quality degradation on code tasks.

**Q2.** You are designing a serving system that needs to run a 405B-parameter model. Your hardware budget allows for 8× H100 80GB GPUs (640GB total). The model in fp16 requires 810GB. You can use int4 quantization (reducing to ~200GB) or distribute across all 8 GPUs without quantization using tensor parallelism. Compare the trade-offs of: (A) int4 quantization on 4 GPUs, (B) fp16 on 8 GPUs with tensor parallelism, and (C) a hybrid approach. Which would you choose, under what serving conditions, and what monitoring would you implement to validate the choice?
