---
layout: default
title: "Model Pruning"
parent: "AI Foundations"
nav_order: 1611
permalink: /ai-foundations/model-pruning/
number: "1611"
category: AI Foundations
difficulty: ★★★
depends_on: Model Weights, Model Parameters, Training
used_by: Distillation, Model Quantization, Inference
related: Model Quantization, Distillation, Model Weights
tags:
  - ai
  - performance
  - advanced
  - optimization
  - compression
---

# 1611 — Model Pruning

⚡ TL;DR — Model pruning removes redundant or low-importance weights from a neural network, reducing model size and inference cost — ideally with minimal quality degradation.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A trained 7B-parameter model achieves excellent performance but costs $0.02 per inference. At 10 million daily requests, that's $200,000/day — unsustainable. Quantization has already been applied. The team needs further size reduction without retraining from scratch.

**THE BREAKING POINT:**
Neural networks are over-parameterised by design — trained with far more parameters than strictly necessary, because training with redundancy improves convergence. After training, many weights contribute negligibly to predictions. Without a way to remove these, the model carries dead weight at every inference.

**THE INVENTION MOMENT:**
Pruning removes the least important weights after training (or during), exploiting the observation that large trained networks contain sparse, smaller "lottery ticket" subnetworks that can perform nearly as well as the full network.

---

### 📘 Textbook Definition

**Model pruning** is a neural network compression technique that removes a subset of weights, neurons, attention heads, or layers from a trained network — based on an importance criterion — reducing model size and inference cost while preserving as much predictive quality as possible. Pruning is classified by granularity: **unstructured pruning** (zeroing individual weights — high sparsity possible but requires sparse hardware); **structured pruning** (removing entire neurons, heads, or layers — immediately accelerates on standard hardware); **magnitude pruning** (removing weights with smallest absolute values); **gradient-based pruning** (removing weights with smallest impact on loss). After pruning, fine-tuning (pruning-aware fine-tuning) recovers quality.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Pruning removes the least useful parts of a model — like cutting unused branches from a tree — making it smaller and faster without starting over.

**One analogy:**

> Imagine an orchestra with 120 musicians. A conductor notices that during most performances, 30 musicians in the back rows are barely audible — their notes are always covered by louder instruments. Pruning removes those 30 musicians. The orchestra now costs 25% less and sounds nearly identical. Structured pruning removes entire sections (all brass); unstructured pruning mutes individual musicians regardless of section.

**One insight:**
The lottery ticket hypothesis (Frankle & Carlin, 2019) shows that large networks contain small subnetworks (the "winning tickets") that can be identified after training and perform nearly as well. Pruning is the process of finding and keeping these winning tickets.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Neural networks trained with SGD are over-parameterised — redundancy is intentional for training stability.
2. After training, many weights are near-zero or have negligible influence on the output.
3. Removing these weights has little impact on predictions — but reduces memory and compute.

**PRUNING TYPES:**

```
UNSTRUCTURED PRUNING:
Zero individual weights wherever in the matrix
Result: sparse weight matrix (e.g., 80% zeros)
  W = [0.3, 0.0, 0.0, -0.2, 0.0, 0.7, 0.0, 0.1]
Hardware: needs sparse ops (e.g., NVIDIA 2:4 sparsity)

STRUCTURED PRUNING:
Remove entire neurons, attention heads, or layers
Result: smaller dense matrix (no sparsity needed)
  Before: 12 attention heads per layer
  After:  8 attention heads per layer
  → standard dense matmul, immediate speedup
Hardware: works on all hardware — dense ops

MAGNITUDE PRUNING:
|w| < threshold → set w = 0
Simple, effective, widely used

GRADIENT-BASED PRUNING:
importance(w) = |w × ∂L/∂w|
Removes weights with smallest gradient-weighted magnitude
More accurate — accounts for loss sensitivity
```

**THE TRADE-OFFS:**
**Gain:** Smaller model size; faster inference (structured pruning especially); reduced memory bandwidth.
**Cost:** Quality degradation if too aggressive; requires pruning-aware fine-tuning to recover; unstructured pruning requires specialised sparse hardware to realise speedups.

---

### 🧪 Thought Experiment

**SETUP:**
A BERT-base model has 12 attention heads per layer. Research (Michel et al., 2019) found that after training, only 2–4 heads per layer are critical for most tasks. You prune 8 of 12 attention heads (67% structured pruning of attention) and compare to the original.

**RESULTS:**
Before pruning: 110M parameters, 100ms inference, 92.3% F1 on NER.
After pruning (no fine-tuning): 60M parameters, 60ms inference, 86.1% F1 — 6.2pp quality loss.
After pruning + 3 epochs fine-tuning: 60M parameters, 60ms inference, 91.7% F1 — only 0.6pp quality loss.

**THE INSIGHT:**
Pruning without fine-tuning causes significant quality loss — the model was optimised for the full set of heads. Fine-tuning after pruning allows the remaining heads to compensate, recovering almost all quality. The combination of pruning + fine-tuning achieves 45% fewer parameters and 40% faster inference at 0.6pp quality cost. This is the standard "prune then fine-tune" pipeline.

---

### 🧠 Mental Model / Analogy

> Pruning a model is like editing a first draft down to a polished article. The first draft (trained model) contains everything — many sentences that say the same thing, tangents, redundant examples. Editing (pruning) removes the weakest material. A quick re-read and minor rewriting (fine-tuning) makes the shorter piece flow naturally. The final article is shorter, cleaner, and nearly as informative — but took far less editing than writing from scratch.

Mapping:

- "First draft" → fully trained model (over-parameterised)
- "Redundant sentences" → near-zero or low-importance weights
- "Editing" → magnitude or gradient-based pruning
- "Re-read and minor rewriting" → post-pruning fine-tuning
- "Shorter, cleaner article" → pruned model (smaller, faster)

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Pruning removes parts of an AI model that aren't doing much work — like deleting unused code from a program — making it smaller and faster without losing much quality.

**Level 2 — How to use it (junior developer):**
For LLMs, structured pruning of attention heads and FFN layers using libraries like LLM-Pruner or SparseGPT is the practical approach. The general workflow: (1) Train or download full model. (2) Compute importance scores for each head/neuron. (3) Set a pruning ratio (10–30% for minimal quality loss; > 50% requires significant fine-tuning). (4) Prune and save the new smaller architecture. (5) Fine-tune for 1–3 epochs on domain data. (6) Validate on benchmark before deploying.

**Level 3 — How it works (mid-level engineer):**
**SparseGPT** (Frantar & Alistarh, 2023) enables one-shot unstructured pruning at 50–60% sparsity with minimal quality loss — no retraining needed. It uses the Hessian of the loss (like GPTQ) to compute which weights can be pruned and compensates by adjusting remaining weights. **2:4 structured sparsity** (NVIDIA Ampere and later): exactly 2 of every 4 consecutive weights are zeroed — a hardware-accelerated sparse format that delivers ~2× speedup on A100/H100 at 50% sparsity. This is the practical "structured sparsity" that requires no special hardware adaptation — just the right weight pattern.

**Level 4 — Why it was designed this way (senior/staff):**
The lottery ticket hypothesis predicts that dense networks contain sparse subnetworks that can be identified and isolated. Empirically, LLMs are more prunable than expected: LLaMA-2-7B can be pruned to 50% sparsity with < 2% quality loss using SparseGPT. The open research question is: can pruning recover a model as small as a model of the same size trained from scratch? Typically, no — a 7B model pruned to 3.5B parameters is slightly worse than a dedicated 3.5B model trained from scratch (Hu et al., 2023). This suggests pruning is most useful when you have a high-quality large model and want a smaller version without the training cost, not as a replacement for architecture design. The exception is iterative pruning with full retraining (expensive) — this can match dedicated small model quality.

---

### ⚙️ How It Works (Mechanism)

```
PRUNING PIPELINE:

Full Model (100%)
  W = [[0.8, 0.1, -0.5, 0.9, -0.2, 0.7, ...]]
      ↓ Compute importance score
      importance(w) = |w| or |w × ∇L|
      ↓ Rank weights by importance
      ↓ Set bottom-k% to zero
  W_pruned = [[0.8, 0.0, -0.5, 0.9, 0.0, 0.7, ...]]
      ↓ Optional: fine-tune to recover quality
  W_fine-tuned = [[0.79, 0.0, -0.52, 0.91, 0.0, 0.71, ...]]

2:4 STRUCTURED SPARSITY PATTERN:
  Original:   [0.8, 0.1, -0.5, 0.9]
  2:4 pruned: [0.8, 0.0, -0.5, 0.0]  (2 of 4 non-zero)
              [0.0, 0.1, 0.0,  0.9]  ← alt: keep smaller
  NVIDIA A100: 2× matmul speedup with this pattern
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Trained dense model
    ↓
Define pruning target:
  What to prune: weights / neurons / heads / layers
  How much: pruning ratio (10–80%)
  Criterion: magnitude / gradient / random
    ↓
Compute importance scores
(require calibration data for gradient-based)
    ↓
[PRUNE ← YOU ARE HERE]
Remove low-importance weights/structures
    ↓
Validate quality on benchmark
    ↓
If degradation acceptable → deploy
    ↓
If degradation too high → fine-tune
    ↓
Post-pruning fine-tuning (1–5 epochs)
    ↓
Validate; deploy
```

---

### 💻 Code Example

**Example 1 — Magnitude-based unstructured pruning with PyTorch:**

```python
import torch
import torch.nn.utils.prune as prune

def prune_model_magnitude(
    model: torch.nn.Module,
    sparsity: float  # fraction of weights to zero
) -> torch.nn.Module:
    """Apply global magnitude pruning to all linear layers."""
    params_to_prune = [
        (module, "weight")
        for module in model.modules()
        if isinstance(module, torch.nn.Linear)
    ]
    # Global unstructured: prune globally across all layers
    prune.global_unstructured(
        params_to_prune,
        pruning_method=prune.L1Unstructured,
        amount=sparsity  # e.g., 0.5 = 50% sparsity
    )
    # Make pruning permanent (remove mask, zero weights)
    for module, name in params_to_prune:
        prune.remove(module, name)
    return model
```

**Example 2 — Structured attention head pruning:**

```python
def prune_attention_heads(
    model,
    heads_to_prune: dict[int, list[int]]
) -> None:
    """
    Prune specific attention heads per layer.
    heads_to_prune: {layer_idx: [head_idx, ...]}
    """
    model.prune_heads(heads_to_prune)

# Example: prune heads 3,5,7,9 from layer 0
#          heads 0,2,6,11 from layer 1
heads_to_prune = {
    0: [3, 5, 7, 9],
    1: [0, 2, 6, 11]
}
prune_attention_heads(model, heads_to_prune)
```

**Example 3 — Measure sparsity:**

```python
def measure_sparsity(model: torch.nn.Module) -> float:
    """Compute fraction of zero weights in linear layers."""
    total_weights = 0
    zero_weights = 0
    for module in model.modules():
        if isinstance(module, torch.nn.Linear):
            total_weights += module.weight.numel()
            zero_weights += (module.weight == 0).sum().item()
    sparsity = zero_weights / total_weights
    print(f"Sparsity: {sparsity:.1%} "
          f"({zero_weights:,} / {total_weights:,} zeros)")
    return sparsity
```

---

### ⚖️ Comparison Table

| Method                        | Hardware Need                | Speedup             | Quality                    | Best For                       |
| ----------------------------- | ---------------------------- | ------------------- | -------------------------- | ------------------------------ |
| **Magnitude unstructured**    | Sparse ops or dense (masked) | Low on standard GPU | Good                       | Research; sparse hardware      |
| **NVIDIA 2:4 structured**     | A100/H100                    | 2× on matmul        | Good                       | Production serving on NVIDIA   |
| **Head pruning (structured)** | Any                          | Moderate            | Good after FT              | LLM serving, BERT-class models |
| **Layer pruning**             | Any                          | High                | Moderate (more aggressive) | Extreme compression targets    |
| **SparseGPT**                 | Any                          | Low (dense)         | Excellent (one-shot)       | Quick PTQ-style pruning        |
| Quantization (comparison)     | Any                          | Moderate-high       | Excellent                  | Easiest compression option     |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                               |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| "Pruning always speeds up inference on GPUs"      | Unstructured sparsity does NOT speed up standard dense GPU operations; structured pruning or 2:4 sparsity is required for GPU speedup |
| "Pruning the smallest weights is always best"     | Magnitude pruning is a heuristic; gradient-weighted importance is more accurate but slower to compute                                 |
| "Pruning is better than quantization"             | For practical GPU speedup: quantization is usually more impactful and simpler; pruning and quantization are complementary             |
| "50% pruning → 50% faster inference"              | Speedup depends entirely on pruning structure and hardware; 50% unstructured sparsity → 0% GPU speedup without sparse hardware        |
| "Pruning replaces training the right-sized model" | A pruned large model is typically slightly worse than a dedicated small model of the same parameter count                             |

---

### 🚨 Failure Modes & Diagnosis

**Catastrophic Quality Collapse After Aggressive Pruning**

**Symptom:** Pruning 70% of weights causes a near-random model output — accuracy drops from 91% to 52%.

**Root Cause:** Over-aggressive pruning without importance calibration. Too many critical weights removed. Network cannot recover even with fine-tuning.

**Diagnostic Command / Tool:**

```python
def iterative_pruning_schedule(
    model,
    target_sparsity: float,
    n_steps: int,
    eval_fn,
    min_quality: float
) -> float:
    """
    Gradually increase pruning ratio,
    checking quality at each step.
    """
    step_size = target_sparsity / n_steps
    current_sparsity = 0.0

    for step in range(n_steps):
        current_sparsity += step_size
        prune_model_magnitude(model, step_size)
        quality = eval_fn(model)
        print(f"Step {step+1}: sparsity={current_sparsity:.0%}"
              f" quality={quality:.1%}")
        if quality < min_quality:
            print(f"Quality below threshold at "
                  f"{current_sparsity:.0%} sparsity — stopping")
            return current_sparsity - step_size  # last good point
    return current_sparsity
```

**Fix:** Use iterative pruning (gradually increase sparsity, fine-tune between steps) rather than one-shot pruning. Cap pruning ratio below the quality cliff.

**Prevention:** Never prune > 30% in a single step without calibration; always measure quality after each pruning increment.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Model Weights` — pruning directly operates on model weights
- `Model Parameters` — parameter count is what pruning reduces
- `Training` — pruning-aware fine-tuning requires a training loop to recover quality

**Builds On This (learn these next):**

- `Distillation` — alternative compression: train a small model to mimic a large one
- `Model Quantization` — complementary compression: reduce numerical precision
- `Inference` — the serving context where pruning benefits are realised

**Alternatives / Comparisons:**

- `Model Quantization` — reduces precision, not parameter count; easier to apply
- `Distillation` — trains a dedicated small model; better quality than pruning at same size
- `Model Weights` — the data structure that pruning manipulates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Removing low-importance weights/neurons   │
│              │ from a trained model to reduce size       │
├──────────────┼───────────────────────────────────────────┤
│ KEY TYPES    │ Unstructured: zero individual weights     │
│              │ Structured: remove heads/layers/neurons   │
│              │ 2:4 sparsity: NVIDIA hardware-accelerated │
├──────────────┼───────────────────────────────────────────┤
│ PIPELINE     │ Train → Compute importance → Prune →      │
│              │ Fine-tune → Validate → Deploy             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Need smaller model; quantization applied; │
│              │ want further compression; NVIDIA H100     │
│              │ hardware for 2:4 structured sparsity      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ > 50% pruning without fine-tuning;        │
│              │ unstructured pruning on standard GPU      │
│              │ (no speedup without sparse hardware)      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Remove the deadwood — most weights       │
│              │ contribute little; find them and cut."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Distillation → Model Quantization →       │
│              │ Lottery Ticket Hypothesis                 │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The lottery ticket hypothesis predicts that a randomly-initialised dense network contains sparse subnetworks that — when trained from the same initialisation — match the full network's performance. However, for LLMs, finding these winning tickets at initialisation (before training) has proven difficult. Explain why LLM-scale lottery ticket identification is harder than for small networks, and what this implies about the practical utility of pruning vs. training smaller models from scratch for LLM deployment.

**Q2.** You have two models: Model A = 7B parameters trained at high quality, Model B = 3.5B parameters trained from scratch. You want the best possible 3.5B-quality model. You can: (a) prune Model A to 3.5B, (b) train Model B from scratch, or (c) prune Model A to 3.5B then distil into Model B architecture. Under what conditions does each approach win, and what is the resource trade-off in terms of GPU-hours for each?
