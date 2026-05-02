---
layout: default
title: "Model Parameters"
parent: "AI Foundations"
nav_order: 1596
permalink: /ai-foundations/model-parameters/
number: "1596"
category: AI Foundations
difficulty: ★★★
depends_on: Neural Network, Training, Deep Learning
used_by: Model Weights, Model Quantization, Fine-Tuning
related: Model Weights, Inference, Training
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - internals
---

# 1596 — Model Parameters

⚡ TL;DR — Model parameters are the billions of learned numerical values stored in a neural network's matrices — they encode everything the model "knows," shaped entirely by gradient descent during training.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine writing an AI system using hand-coded rules: "If the sentence contains 'happy', output positive sentiment. If it contains 'sad', output negative." You spend months encoding rules. Then users write "not bad" (positive but no 'happy'), "I'm not not satisfied" (double negative), or Portuguese text. The hand-coded system breaks on every edge case and requires constant manual maintenance.

**THE BREAKING POINT:**
Rule-based systems cannot scale to the complexity of natural language, images, or audio. The number of rules needed grows combinatorially. Engineers can never encode enough rules to handle real-world distribution.

**THE INVENTION MOMENT:**
This is exactly why Model Parameters were invented — as the mechanism by which neural networks store learned behaviour as numerical values, automatically discovered through training on data rather than manually written by engineers.

---

### 📘 Textbook Definition

**Model parameters** are the learnable numerical values within a neural network — primarily the weights and biases of each layer — that are updated during training via gradient descent to minimise the loss function. For transformer-based LLMs, parameters are stored as floating-point numbers in matrices representing attention heads, feed-forward layers, embedding tables, and layer normalisation scales. Parameter count (e.g., 7B, 70B, 405B) is the dominant measure of model size and roughly correlates with model capability, though scaling laws (Chinchilla) define optimal compute-to-parameter ratios.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Model parameters are the numbers the model learned — billions of weights that together encode its "knowledge" of language.

**One analogy:**
> Think of a piano. The keys, strings, and hammers are the architecture. The musician's years of practice — muscle memory, intuition, sense of timing — are the parameters. You cannot see the practice directly; it is encoded in the musician's body. Model parameters are the same: invisible learned values that encode skill, shaped by millions of examples during training.

**One insight:**
Parameters are the only persistent state of a trained neural network. Everything the model "knows" — grammar, facts, reasoning patterns, code syntax — is somehow encoded in these numerical values. This is both remarkable (emergent capability from numbers) and fragile (the knowledge is opaque, lossy, and cannot be directly edited).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A neural network is a composition of mathematical functions (layers).
2. Each layer has free variables (parameters) that determine its output for any given input.
3. Training finds parameter values that make the network's outputs match the desired outputs on the training data.

**DERIVED DESIGN:**
For a simple linear layer: `output = W × input + b`

`W` (weight matrix) and `b` (bias vector) are the parameters. During training:
1. Forward pass: compute output using current W, b.
2. Compute loss: how wrong is the output?
3. Backward pass: compute gradient of loss with respect to every parameter.
4. Update: `W = W - learning_rate × gradient_of_W`

Repeated over billions of examples, parameters converge to values that produce correct-ish outputs on seen inputs and generalise to unseen inputs.

For a 7B parameter model, this means ~7 billion such values, mostly in weight matrices of size (hidden_dim × hidden_dim) for each layer.

```
┌─────────────────────────────────────────────┐
│ Transformer layer (~7B params spread across)│
│                                             │
│ Embedding table:   50K × 4096 = 200M        │
│ Attention (×32):   32 × 4 × 4096²/H = 2B  │
│ FFN (×32):         32 × 2 × 4096 × 16384   │
│                  = ~4.3B                    │
│ Other (norms):     ~50M                     │
└─────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain (more parameters):** Greater model capacity → better performance on complex tasks.
**Cost (more parameters):** More GPU memory required (7B float16 = ~14 GB), slower inference, higher serving cost.

Could we do this differently? Symbolic AI stores knowledge as explicit rules (inspectable, editable, but brittle). Neural parameters store knowledge implicitly (not inspectable, not directly editable, but enormously powerful).

---

### 🧪 Thought Experiment

**SETUP:**
Two identical transformer architectures, same training data. Model A: 1B parameters. Model B: 7B parameters.

**WHAT HAPPENS WITH MODEL A (1B):**
The 1B parameter capacity is enough to learn basic grammar, common vocabulary, and frequent factual associations. But for rare or complex reasoning tasks, the model runs out of representational capacity — it cannot store enough information about low-frequency patterns. Performance plateaus after ~3B training tokens.

**WHAT HAPPENS WITH MODEL B (7B):**
The 7B parameter space allows the model to store more fine-grained associations, longer-range syntactic patterns, and more factual knowledge. Perplexity continues decreasing longer. The model handles rare constructions and multi-step reasoning that 1B cannot.

**THE INSIGHT:**
Parameters are the "memory budget" of the neural network. More parameters = more things can be stored. But parameters are not free — they cost memory, compute, and money at inference time. The Chinchilla scaling law (Hoffmann et al., 2022) showed that the optimal number of training tokens is approximately 20× the parameter count: 7B parameters benefit from ~140B training tokens.

---

### 🧠 Mental Model / Analogy

> Think of parameters as the synaptic strengths in a brain. Each connection between neurons has a strength (the weight). Learning = adjusting these strengths based on experience. A "stronger" synapse means "this pattern matters more." The brain doesn't store facts in single neurons; it stores them as distributed patterns across billions of connections. Neural network parameters work identically.

Mapping:
- "Neurons" → activations (computed, not stored)
- "Synaptic strengths" → weight matrix values (stored, learned)
- "Learning from experience" → gradient descent on training data
- "Remembering a fact" → a distributed pattern across many weights
- "Brain damage" → pruning or quantizing parameters

Where this analogy breaks down: a biological brain's learning is local (Hebbian, synaptic plasticity) and continuous; neural network training uses global backpropagation with discrete gradient steps.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When people say a model has "7 billion parameters," they mean it has 7 billion numbers it learned during training. These numbers are the model's "knowledge" — everything it knows is somehow encoded in them.

**Level 2 — How to use it (junior developer):**
Parameter count tells you about memory requirements and capability tier. Loading a 7B float16 model requires ~14 GB GPU VRAM. A 70B model requires ~140 GB — need multiple GPUs or quantization. Larger models generally perform better but cost more to serve. Choose the smallest model that meets your task's quality bar.

**Level 3 — How it works (mid-level engineer):**
Parameters are stored as NumPy arrays / PyTorch tensors. Common data types: float32 (4 bytes/param), float16 (2 bytes/param), bfloat16 (2 bytes/param), int8 (1 byte/param, quantized). Total memory footprint = N_params × bytes_per_param + activations (runtime) + KV cache (inference). KV cache grows with context length and batch size. For serving: parameter memory is static; KV cache is the dynamic component.

**Level 4 — Why it was designed this way (senior/staff):**
The distributed representation of knowledge in parameters is a deliberate design choice with deep consequences: it enables generalisation (knowledge is stored as statistical patterns, not facts), but it also enables hallucination (patterns fire on inputs they were never exactly trained on). The parameter count vs. quality relationship follows power laws described by scaling laws. Modern architectures like mixture-of-experts (MoE) separate total parameter count from active parameter count — a 141B MoE model (Mixtral) may only activate ~45B parameters per forward pass, dramatically reducing inference cost while preserving capacity.

---

### ⚙️ How It Works (Mechanism)

**Parameter storage and loading:**

```
┌─────────────────────────────────────────────┐
│ Model file on disk (safetensors / .bin):    │
│ Layer 0 attn.q_proj: float16 tensor        │
│   shape: [4096, 4096] = 16.7M values       │
│ Layer 0 attn.k_proj: float16 tensor        │
│   shape: [4096, 4096] = 16.7M values       │
│ ... (32 layers × ~10 weight matrices)      │
│ Total file: ~14 GB for 7B float16          │
└──────────────┬──────────────────────────────┘
               ↓ Load to GPU VRAM
┌─────────────────────────────────────────────┐
│ GPU VRAM allocation:                        │
│ Parameters:  ~14 GB                        │
│ Activations: ~2–4 GB (batch-dependent)     │
│ KV cache:    grows with context × batch    │
└──────────────┬──────────────────────────────┘
               ↓ Forward pass
┌─────────────────────────────────────────────┐
│ Input tokens → embeddings (lookup table)   │
│ → multiply by weight matrices (params)     │
│ → activations flow through layers          │
│ → output logits from final layer           │
└─────────────────────────────────────────────┘
```

**Happy path:** Model fits in VRAM → full forward pass → inference.

**Error path:** Model too large for VRAM → OOM error → need quantization, model sharding, or smaller model.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (training):**
```
Random initialisation of parameters
    ↓
Training batch → forward pass
    ↓
Loss computed (cross-entropy)
    ↓
Backward pass: gradients for all parameters
    ↓
[PARAMETER UPDATE ← YOU ARE HERE]
  W = W - lr × gradient
    ↓
Repeat for billions of training steps
    ↓
Parameters converge to learned values
    ↓
Model saved to disk
```

**NORMAL FLOW (inference):**
```
Model parameters loaded to GPU memory
    ↓
Input tokens processed
    ↓
[PARAMETERS USED ← YOU ARE HERE]
  Matrix multiplications with weight matrices
    ↓
Output logits → sampled token
```

**WHAT CHANGES AT SCALE:**
At very large parameter counts (70B+), single-node inference becomes impossible — model must be sharded across multiple GPUs (tensor parallelism). Each GPU holds a fraction of each weight matrix; matrix multiplications happen in parallel with all-reduce operations across GPUs. Communication overhead between GPUs becomes a significant fraction of total inference time.

---

### 💻 Code Example

**Example 1 — Inspecting model parameters:**
```python
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
)

# Count total parameters
total = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total/1e9:.2f}B")
# → "Total parameters: 6.74B"

# Inspect a specific weight matrix
q_proj = model.model.layers[0].self_attn.q_proj.weight
print(f"Shape: {q_proj.shape}")  # → [4096, 4096]
print(f"dtype: {q_proj.dtype}")  # → torch.float16
print(f"Memory: {q_proj.nbytes/1e6:.1f} MB")
# → "Memory: 33.6 MB"
```

**Example 2 — Memory calculation before loading:**
```python
def estimate_model_memory(n_params: int,
                          dtype_bytes: int = 2,
                          overhead_factor: float = 1.2
                          ) -> float:
    """
    Estimate GPU VRAM needed for inference.
    dtype_bytes: 2 for float16, 4 for float32
    Returns: GB
    """
    base_gb = (n_params * dtype_bytes) / 1e9
    # Add activation and overhead
    return base_gb * overhead_factor

print(estimate_model_memory(7e9))    # → ~16.8 GB
print(estimate_model_memory(70e9))   # → ~168 GB
print(estimate_model_memory(7e9, 1)) # int8 → ~8.4 GB
```

**Example 3 — Freezing parameters for fine-tuning:**
```python
# Fine-tuning: freeze base params, only train adapter
for name, param in model.named_parameters():
    if "lora" in name:
        param.requires_grad = True  # only train LoRA
    else:
        param.requires_grad = False  # freeze base model

trainable = sum(p.numel() for p in model.parameters()
                if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Trainable: {trainable/total*100:.2f}%")
# → "Trainable: 0.08%" for LoRA on a 7B model
```

---

### ⚖️ Comparison Table

| Parameter Count | Memory (fp16) | Capability | Best For |
|---|---|---|---|
| ~1B | ~2 GB | Basic tasks | Edge/embedded devices |
| **~7B** | ~14 GB | Strong general | Single GPU (A100) |
| ~13B | ~26 GB | Better reasoning | 2× GPU or high VRAM |
| ~70B | ~140 GB | Near frontier | Multi-GPU cluster |
| ~405B | ~810 GB | Frontier | Large cluster |
| MoE (e.g., 141B total) | ~45B active | Frontier efficient | Mixture-of-experts serving |

**How to choose:** Start with the smallest model that meets your quality threshold — it's dramatically cheaper to serve. Use quantization (int8/int4) to fit larger models in less memory if quality is paramount.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More parameters = smarter model" | Parameter efficiency matters; a well-trained 7B model can outperform a poorly-trained 70B model on specific tasks |
| "Parameters directly store facts" | Facts are distributed across many parameters in superposition; no single parameter stores a single fact |
| "You can edit parameters to update knowledge" | Direct parameter editing is an active research area (model editing); it doesn't reliably work yet at scale |
| "Parameter count = training compute" | Training compute = parameters × training tokens × 6; the same parameter count can be undertrained or overtrained |
| "Inference cost = parameter count" | Inference cost also depends on context length, batch size, and KV cache — a 7B model with 128K context can use more memory than a 70B with 4K context |

---

### 🚨 Failure Modes & Diagnosis

**Out-of-Memory (OOM) at Load Time**

**Symptom:** `CUDA out of memory. Tried to allocate X GiB` when loading a model.

**Root Cause:** Model parameters exceed available GPU VRAM. float16 7B = ~14 GB; many consumer GPUs have 8–12 GB.

**Diagnostic Command / Tool:**
```bash
# Check GPU VRAM before loading
nvidia-smi --query-gpu=memory.free,memory.total \
  --format=csv,noheader
```

**Fix:**
```python
# Use quantization to fit in smaller VRAM
from transformers import BitsAndBytesConfig
bnb_config = BitsAndBytesConfig(load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)
# 7B float16 (14 GB) → ~4 GB with int4
```

**Prevention:** Always estimate memory requirements before loading (see Code Example 2).

---

**Gradient Explosion During Training**

**Symptom:** Training loss becomes NaN or jumps to infinity after a few steps.

**Root Cause:** Gradients flowing backward through layers become very large (explode), pushing parameters to extreme values that cause numerical overflow.

**Diagnostic Command / Tool:**
```python
# Monitor gradient norms during training
for name, param in model.named_parameters():
    if param.grad is not None:
        norm = param.grad.norm()
        if norm > 10.0:
            print(f"Large gradient: {name}: {norm:.2f}")
```

**Fix:** Gradient clipping: `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`

**Prevention:** Use gradient clipping in training loop; use mixed-precision training with loss scaling.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Neural Network` — parameters are the weights in neural network layers
- `Training` — gradient descent is the mechanism by which parameters acquire their values
- `Deep Learning` — deep networks have billions of parameters requiring GPU-scale compute

**Builds On This (learn these next):**
- `Model Weights` — the specific representation format of parameters at rest (on disk)
- `Model Quantization` — reducing parameter precision to save memory and speed inference
- `Fine-Tuning` — updating a subset of parameters on new data to specialise the model

**Alternatives / Comparisons:**
- `Model Weights` — often used interchangeably; technically weights are a subset of parameters (excluding biases)
- `Inference` — inference uses parameters without updating them; training updates them
- `Training` — the process that discovers optimal parameter values

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Billions of learned floating-point        │
│              │ numbers that encode the model's knowledge │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Hand-coded rules cannot scale to          │
│ SOLVES       │ language complexity — learned parameters  │
│              │ do                                        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Knowledge is NOT stored in individual     │
│              │ parameters — it's distributed across      │
│              │ billions of them simultaneously           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — parameters are the model;        │
│              │ you choose size based on task + budget    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't load more parameters than needed    │
│              │ — match model size to task complexity     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ More parameters = better capability vs    │
│              │ higher memory, latency, and serving cost  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "7 billion synapses — everything the AI  │
│              │ knows lives somewhere in those numbers."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Model Weights → Quantization → Fine-Tuning│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** GPT-4 has an estimated 1.8 trillion parameters (rumoured MoE). At inference, only ~220B parameters are active per forward pass. Given that serving cost is proportional to active compute (not total parameters), what does this tell you about why MoE architectures are economically attractive for frontier model serving — and what new failure modes does activating only a subset of experts introduce compared to a dense model?

**Q2.** A team discovers their 7B fine-tuned model hallucinates on a specific class of facts that were well-represented in the base training data. They propose "injecting the correct facts directly into the model parameters via targeted weight editing." What are the three fundamental obstacles that make this harder than it sounds, and which retrieval-based alternative would sidestep all three obstacles simultaneously?
