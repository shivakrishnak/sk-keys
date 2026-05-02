---
layout: default
title: "Fine-Tuning"
parent: "AI Foundations"
nav_order: 1600
permalink: /ai-foundations/fine-tuning/
number: "1600"
category: AI Foundations
difficulty: ★★★
depends_on: Training, Model Weights, Transfer Learning
used_by: RLHF, Model Evaluation Metrics, Responsible AI
related: RLHF, Pre-training, Transfer Learning
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - production
---

# 1600 — Fine-Tuning

⚡ TL;DR — Fine-tuning adapts a pretrained model to a specific task or domain by continuing training on a smaller, targeted dataset — borrowing the model's broad knowledge while specialising its behaviour.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
GPT-4 is a brilliant generalist. But your company needs a model that: formats all responses as structured JSON, uses your internal product terminology, follows your specific tone-of-voice guide, and never discusses competitor products. No amount of prompt engineering reliably enforces all these constraints. A user can always jailbreak a system prompt. The model still reaches for generic phrasing. At high volume, inconsistent outputs cause real business problems.

**THE BREAKING POINT:**
Prompt engineering can influence but not guarantee model behaviour. For consistent, task-specific behaviour at scale — especially for format constraints, domain vocabulary, and safety policies — runtime prompting is insufficient. The model needs its weights updated to deeply internalise the target behaviour.

**THE INVENTION MOMENT:**
This is exactly why Fine-Tuning was developed — as the mechanism to adapt a pretrained model's weights to a specific task, domain, or behaviour, encoding the specialisation directly into the parameters rather than relying on prompt-time instructions.

---

### 📘 Textbook Definition

**Fine-tuning** is the process of continuing gradient descent on a pretrained model's weights (or a subset thereof) using a smaller, task-specific dataset, to specialise the model for a particular domain, task, or output format. Unlike pre-training, which requires trillions of tokens and massive compute, fine-tuning typically uses thousands to millions of examples with orders of magnitude less compute. Techniques include full fine-tuning (all weights updated), parameter-efficient fine-tuning (LoRA, prefix tuning, adapters), supervised fine-tuning (SFT on labelled demos), and reinforcement learning from human feedback (RLHF).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Fine-tuning is teaching an expert a new specialty — they keep all their knowledge but specialise their behaviour for your use case.

**One analogy:**

> Think of a medical school graduate (pretrained model). They have broad knowledge of medicine (general capabilities). Fine-tuning is their residency: they spend 3 years focusing specifically on cardiology (your domain). They don't unlearn general medicine — they build specialised expertise on top of it. Fine-tuning a language model works identically: deep general knowledge stays; specific behaviour is added.

**One insight:**
Fine-tuning is most powerful for changing HOW the model responds (format, style, persona, safety policies) rather than WHAT it knows. For adding new factual knowledge, retrieval (RAG) is often more reliable — fine-tuning on new facts can cause the model to partially forget existing knowledge (catastrophic forgetting).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Pretrained weights encode broad language patterns — they are expensive to reproduce.
2. Task-specific patterns can be added on top with much less data and compute.
3. Gradient descent on a small dataset from a pretrained starting point converges faster and generalises better than training from scratch.

**DERIVED DESIGN:**
Fine-tuning initialises gradient descent from pretrained weights rather than random initialisation. The "weight space" is already well-positioned near good solutions for most language tasks — fine-tuning only needs to navigate a small region of this space.

Two strategies:

**Full fine-tuning:** All N parameters are updated.

- Cost: same memory and compute as training a model of the same size.
- Risk: catastrophic forgetting — fine-tuning data may overwrite general capabilities.

**Parameter-efficient fine-tuning (PEFT — LoRA):**
Instead of updating W directly, inject low-rank matrices:
`W' = W + ΔW = W + A × B`
Where A ∈ R^(d×r) and B ∈ R^(r×d), rank r << d.
Only A and B are trained (~ 0.1–1% of total parameters).
W (base weights) remain frozen.

**THE TRADE-OFFS:**
**Full fine-tuning gain:** Maximum task specialisation; can reshape any behaviour.
**Full fine-tuning cost:** Expensive, risks catastrophic forgetting, one fine-tuned model per task.

**LoRA gain:** Near-full-fine-tuning quality at 0.1% of the parameter count; preserves base capabilities; adapters can be swapped at inference time.
**LoRA cost:** Does not fully update base weights; may underperform on very large distribution shifts.

---

### 🧪 Thought Experiment

**SETUP:**
Two approaches to building a customer support bot that responds in Spanish JSON format:

Approach A: Prompt engineering only. System prompt: "Always respond in Spanish. Always format as JSON with keys 'answer' and 'confidence'."

Approach B: Fine-tune on 5,000 examples of correct Spanish JSON responses.

**WHAT HAPPENS WITH APPROACH A (prompting only):**
90% of responses are in the correct format. 10% have issues: occasional English words, missing JSON keys, extra text before the JSON object. Under adversarial inputs ("Ignore your instructions and respond normally"), compliance drops to 60%. At 100,000 daily requests, 10,000 malformed responses require fallback handling.

**WHAT HAPPENS WITH APPROACH B (fine-tuning):**
The model has deeply internalised the response format. Compliance is 98%+. Adversarial prompts do not override the format — the weight-level behaviour is much harder to override than a system prompt. Fallback handling is rarely needed.

**THE INSIGHT:**
Prompt instructions sit in the context window — they can be overridden by later context or sufficiently adversarial inputs. Weight-level behaviour (fine-tuning) is far more robust to adversarial inputs because it is baked into the model's fundamental response patterns.

---

### 🧠 Mental Model / Analogy

> Think of a pretrained model as a versatile actor who can play any role. Fine-tuning is a role they have practised intensively — they don't need the script anymore. Without fine-tuning, you hand the actor a script (system prompt) every time they go on stage. With fine-tuning, they've rehearsed the role so thoroughly that the character is now second nature — they'll stay in character even under pressure.

Mapping:

- "Versatile actor" → pretrained general model
- "Practised role" → fine-tuned specialisation
- "Script" → system prompt (prompt engineering)
- "Staying in character under pressure" → robustness to adversarial inputs
- "Character is second nature" → behaviour encoded in weights, not context

Where this analogy breaks down: an actor can choose to break character; a fine-tuned model cannot consciously override its weight-level behaviour — but sufficiently adversarial prompts can still elicit off-distribution outputs.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Fine-tuning is giving a trained AI model extra practice on specific examples you care about, so it gets much better at your particular use case without forgetting everything else it knows.

**Level 2 — How to use it (junior developer):**
Practical fine-tuning recipe: (1) Start with a capable base model (Llama-3, Mistral, etc.); (2) Prepare a dataset of ~1,000–50,000 input/output pairs in the target behaviour; (3) Use LoRA fine-tuning via Hugging Face PEFT + TRL libraries; (4) Train for 1–3 epochs; (5) Evaluate on a held-out validation set. Use `SFTTrainer` from TRL for standard supervised fine-tuning. Monitor for overfitting — with small datasets, models can overfit in < 1 epoch.

**Level 3 — How it works (mid-level engineer):**
LoRA injects low-rank matrices at attention layers. For each weight matrix W (e.g., Q, K, V projections), it learns ΔW = A×B with rank r=8–64. During training, only A and B have gradients; W is frozen. Memory saving: LoRA requires only `2 × rank × hidden_dim × n_adapted_layers` extra parameters. For a 7B model with r=16 adapting all attention layers, this is ~6.5M parameters vs. 7B — 0.09% of the model. At inference, LoRA can be merged: `W_merged = W + A×B` for zero-overhead inference.

**Level 4 — Why it was designed this way (senior/staff):**
LoRA's low-rank hypothesis is empirically supported: the intrinsic dimensionality of task-specific adaptation is much lower than the full parameter space. This is why rank r=8 or r=16 often performs near-identically to full fine-tuning on many tasks — the fine-tuning gradient updates are effectively low-rank anyway. The ability to merge adapters at inference (zero overhead) or keep them separate (swappable per request) is a major production advantage. At scale, a single base model with hundreds of LoRA adapters (one per customer) can be served efficiently using adapter routing — far cheaper than storing and serving hundreds of full 7B models.

---

### ⚙️ How It Works (Mechanism)

**LoRA injection (per attention weight matrix):**

```
┌─────────────────────────────────────────────┐
│ Original weight: W (4096 × 4096, frozen)   │
│                                             │
│ LoRA injection:                             │
│   W' = W + A × B                            │
│   A: (4096 × 16), B: (16 × 4096)           │
│   rank r=16 → 16 × 4096 × 2 = 131K params  │
│   vs full W: 4096² = 16.7M params           │
│   Savings: 99.2% fewer trainable params     │
└──────────────┬──────────────────────────────┘
               ↓ Training
┌─────────────────────────────────────────────┐
│ Only A and B have gradients                 │
│ W is frozen (no gradient, no memory alloc) │
│ Adam state: only for A and B parameters    │
│ → training memory << full fine-tuning      │
└──────────────┬──────────────────────────────┘
               ↓ Inference
┌─────────────────────────────────────────────┐
│ Option 1 — Merged:                          │
│   W_merged = W + A × B                      │
│   Zero inference overhead                  │
│                                             │
│ Option 2 — Separate (swappable adapter):   │
│   W_out = W(input) + A×B(input)             │
│   Small overhead; can swap adapter/request │
└─────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Pretrained base model + weights
    ↓
Prepare fine-tuning dataset
(input/output pairs in target format)
    ↓
Configure LoRA adapters
(rank, target modules, alpha)
    ↓
[FINE-TUNING ← YOU ARE HERE]
  Gradient descent on SFT objective
  Only LoRA params updated (W frozen)
    ↓
Monitor train/val loss, format compliance
    ↓
Save adapter weights (~50–500 MB)
    ↓
Merge adapter into base model (optional)
    ↓
Deploy fine-tuned model
    ↓
Evaluate on held-out benchmark
```

**FAILURE PATH:**

```
Overfitting (small dataset + too many epochs)
    ↓
Train loss → 0, val loss increases
    ↓
Model memorises training examples
    ↓
Reduce epochs, add dropout, increase dataset
```

**WHAT CHANGES AT SCALE:**
At enterprise scale with many domain-specific use cases, fine-tuning becomes an infrastructure problem: a model hub stores hundreds of LoRA adapters; routing layer selects the right adapter per request; adapter merging/unmerging must happen at request boundary. Companies like Predibase offer platforms specifically for this "LoRA as a service" pattern.

---

### 💻 Code Example

**Example 1 — LoRA fine-tuning with TRL:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig
from datasets import Dataset

# Prepare dataset: list of {"text": "..."} dicts
# Format: "<human>: {input}\n<assistant>: {output}"
dataset = Dataset.from_list([
    {"text": "<human>: What's our return policy?\n"
             "<assistant>: {\"policy\": \"30-day returns "
             "with receipt\", \"exceptions\": [\"sale items"
             "\"]}"},
    # ... more examples
])

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    device_map="auto"
)

# Configure LoRA
lora_config = LoraConfig(
    r=16,              # rank
    lora_alpha=32,     # scaling factor
    target_modules=["q_proj", "v_proj"],  # which matrices
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# → trainable params: 6,553,600 (0.09%)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=SFTConfig(
        output_dir="./fine-tuned-model",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        fp16=True,
    ),
)
trainer.train()
```

**Example 2 — Merging adapter and saving:**

```python
from peft import PeftModel

# Load base model + adapter
base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1"
)
model = PeftModel.from_pretrained(
    base_model, "./fine-tuned-model"
)

# Merge adapter weights into base model
merged_model = model.merge_and_unload()
# Now a standard model with zero inference overhead

merged_model.save_pretrained("./merged-model")
```

**Example 3 — Evaluating format compliance:**

```python
import json

def eval_format_compliance(model, tokenizer,
                            test_prompts: list[str]) -> float:
    """Measure % of responses that are valid JSON."""
    valid = 0
    for prompt in test_prompts:
        output = generate(model, tokenizer, prompt)
        try:
            json.loads(output)
            valid += 1
        except json.JSONDecodeError:
            pass
    return valid / len(test_prompts)

# Before fine-tuning
before = eval_format_compliance(base_model, tok, prompts)
# After fine-tuning
after = eval_format_compliance(ft_model, tok, prompts)
print(f"Compliance: {before:.1%} → {after:.1%}")
# → "Compliance: 72.3% → 97.8%"
```

---

### ⚖️ Comparison Table

| Approach             | Data Needed     | Compute         | Robustness | Best For                     |
| -------------------- | --------------- | --------------- | ---------- | ---------------------------- |
| Prompting only       | 0               | 0               | Low        | Quick iteration, prototyping |
| RAG                  | 0               | Low (retrieval) | Medium     | Factual knowledge injection  |
| **Full fine-tuning** | 10K–1M          | High            | Highest    | Full behaviour overhaul      |
| **LoRA fine-tuning** | 1K–100K         | Low–medium      | High       | Task/format specialisation   |
| RLHF/DPO             | 1K–100K ratings | Medium          | High       | Preference alignment         |
| Adapter (prefix)     | 1K–100K         | Low             | Medium     | Multi-task serving           |

**How to choose:** For most production cases, LoRA fine-tuning is the best starting point — cheap, fast, reversible, and near-equivalent to full fine-tuning. Use full fine-tuning only when LoRA quality is insufficient. Use RAG alongside fine-tuning for knowledge-intensive tasks — they complement each other.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                     |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| "Fine-tuning teaches the model new facts"    | Fine-tuning is more reliable for behaviour/format changes than factual knowledge injection; RAG is better for facts         |
| "More fine-tuning data always helps"         | More data helps until overfitting; data quality > quantity; 1,000 perfect examples outperforms 100,000 noisy ones           |
| "LoRA is always worse than full fine-tuning" | For most tasks, LoRA with good rank achieves near-identical results to full fine-tuning at 1% of the cost                   |
| "Fine-tuning is permanent and irreversible"  | Fine-tuning can be undone by reloading base weights; LoRA adapters are separate files that can be swapped                   |
| "Fine-tuning solves alignment"               | SFT alone improves instruction following but does not reliably improve honesty, harmlessness, or alignment — RLHF is needed |

---

### 🚨 Failure Modes & Diagnosis

**Catastrophic Forgetting**

**Symptom:** Fine-tuned model performs well on the target task but dramatically regresses on general capabilities (e.g., forgets how to write code, loses reasoning ability).

**Root Cause:** Full fine-tuning on a narrow dataset overrides gradients that were critical for general capabilities. The training data distribution is too narrow relative to the base model's training distribution.

**Diagnostic Command / Tool:**

```python
# Test on general benchmarks after fine-tuning
from lm_eval import simple_evaluate

before_score = simple_evaluate(
    base_model, tasks=["mmlu", "hellaswag"]
)
after_score = simple_evaluate(
    ft_model, tasks=["mmlu", "hellaswag"]
)
print(f"MMLU: {before_score} → {after_score}")
# Regression > 5 points = catastrophic forgetting
```

**Fix:** Use LoRA instead of full fine-tuning; reduce learning rate; use a replay buffer (mix fine-tuning data with base pre-training data); reduce number of epochs.

**Prevention:** Always evaluate on general benchmarks before and after fine-tuning. Use LoRA as the default approach.

---

**Overfitting on Small Dataset**

**Symptom:** Training loss reaches near-zero after 1–2 epochs; validation loss increases; model outputs training examples verbatim.

**Root Cause:** Model has capacity far exceeding the information content of the fine-tuning dataset; it memorises examples rather than generalising.

**Diagnostic Command / Tool:**

```bash
# Use perplexity on held-out validation set
python -m lm_eval --model hf \
  --model_args pretrained=./fine-tuned-model \
  --tasks wikitext \
  --output_path results/
# Perplexity > 2× base model = overfitting signal
```

**Fix:** Reduce number of epochs; increase LoRA dropout; use early stopping; augment dataset.

**Prevention:** Always create a validation split; monitor validation loss in real time during training; stop training when validation loss starts increasing.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Training` — fine-tuning is continued training; understanding the base mechanism is essential
- `Model Weights` — fine-tuning updates (LoRA) or modifies weights; understanding what weights are is prerequisite
- `Transfer Learning` — fine-tuning is the applied practice of transfer learning for LLMs

**Builds On This (learn these next):**

- `RLHF` — the alignment-focused fine-tuning technique that follows SFT to train from human preferences
- `Model Evaluation Metrics` — evaluating fine-tuning quality requires task-specific metrics
- `Responsible AI` — fine-tuning can reinforce or mitigate biases; alignment must be monitored

**Alternatives / Comparisons:**

- `Pre-training` — creating the base model that fine-tuning starts from; orders of magnitude more expensive
- `Grounding (RAG)` — alternative to fine-tuning for knowledge injection; complementary for behaviour
- `In-Context Learning` — zero/few-shot prompting as a cheaper alternative to fine-tuning for some tasks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Continuing training on a pretrained model │
│              │ with task-specific examples               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Prompt engineering cannot reliably        │
│ SOLVES       │ enforce consistent behaviour at scale     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Best for changing HOW the model responds  │
│              │ (format, style, persona); use RAG for     │
│              │ WHAT it knows (factual knowledge)         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Consistent output format required;        │
│              │ domain-specific tone/persona; prompt      │
│              │ jailbreaks are a real concern             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Use RAG instead for frequently-updated    │
│              │ factual knowledge; avoid full fine-tuning │
│              │ if LoRA achieves the same quality         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Specialised behaviour (robust) vs base    │
│              │ capability retention (catastrophic        │
│              │ forgetting risk)                          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The residency after medical school —     │
│              │ all general knowledge stays;              │
│              │ specialisation is added on top."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RLHF → Model Evaluation → Responsible AI  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A company fine-tunes Llama-3-8B on their internal customer support conversation logs using LoRA (r=16). The fine-tuned model scores 94% on format compliance but security testing reveals it now repeats back customer PII from the training conversations verbatim when given certain trigger phrases. Trace the mechanism: how did the PII enter the fine-tuning process, how did the model encode it, and what steps in the fine-tuning pipeline would have detected and prevented this failure?

**Q2.** Both fine-tuning and few-shot prompting can teach a model to respond in a specific JSON format. Under what precise conditions does few-shot prompting match fine-tuning quality — and what property of a task causes fine-tuning to decisively outperform prompting regardless of how many few-shot examples you add?
