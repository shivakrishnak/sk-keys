---
layout: default
title: "Distillation"
parent: "AI Foundations"
nav_order: 1612
permalink: /ai-foundations/distillation/
number: "1612"
category: AI Foundations
difficulty: ★★★
depends_on: Training, Model Weights, Fine-Tuning
used_by: Model Pruning, Inference, Foundation Models
related: Model Pruning, Model Quantization, Transfer Learning
tags:
  - ai
  - compression
  - advanced
  - training
  - optimization
---

# 1612 — Distillation

⚡ TL;DR — Knowledge distillation trains a small "student" model to mimic a large "teacher" model's outputs — transferring the teacher's learned knowledge into a model that is faster, cheaper, and deployable on resource-constrained hardware.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
GPT-4 achieves state-of-the-art quality but costs $0.03 per 1K tokens. A startup needs 100 million inferences per month. Monthly cost: $3,000,000. Infeasible. They cannot fine-tune GPT-4 (no access to weights). They can train a small model from scratch — but training from scratch with limited data yields poor quality. They are stuck.

**THE BREAKING POINT:**
Large models are too expensive to serve at scale; small models trained from scratch lack quality. The gap between "deployable" and "good enough" seems unbridgeable without either massive compute or massive data.

**THE INVENTION MOMENT:**
Knowledge distillation (Hinton et al., 2015) showed that a small student model can achieve much better performance than training from scratch by learning to predict the large teacher model's output distribution — not just the hard labels. The teacher's "soft labels" (probability distributions over all classes) carry far more information than binary correct/incorrect labels.

---

### 📘 Textbook Definition

**Knowledge distillation** is a model compression technique in which a smaller "student" model is trained to replicate the output distribution of a larger "teacher" model. The student learns from the teacher's "soft targets" — probability distributions over all output classes or tokens — which encode richer information than hard one-hot labels. In LLMs, distillation often takes the form of: training the student to match the teacher's token probability distribution (output distillation), or intermediate hidden state distributions (feature distillation), or both. "Speculative decoding" uses a small draft model paired with a large verifier — a form of distillation-inspired efficient inference.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distillation trains a small cheap model to "learn from" the large expensive model's outputs — getting big-model quality at small-model cost.

**One analogy:**

> A master chef (the teacher model) trains an apprentice (the student model). The apprentice doesn't just learn "dish A is correct, dish B is wrong" (hard labels). They watch the master prepare dozens of dishes — seeing HOW the master thinks, their hesitations, their preferences, their subtleties (soft labels). The apprentice, mentored by the master, becomes far better than they would from a cookbook alone. Distillation is exactly this: "learning from the master" rather than from a textbook.

**One insight:**
Soft labels are the key insight. When a large model outputs "cat: 70%, dog: 25%, fox: 5%," the student learns that cats and dogs are similar — information not present in the hard label "cat." The cross-entropy between teacher and student distributions forces the student to capture these similarities.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A teacher model's output probability distribution encodes learned similarities between classes — information absent from hard labels.
2. Training on soft targets is equivalent to training on a much larger dataset (each soft label provides as much information as multiple hard labels).
3. A student trained on teacher soft labels converges to better optima than one trained on hard labels with the same data.

**DISTILLATION LOSS:**

```
STANDARD CROSS-ENTROPY (hard labels):
L_CE = -∑ y_i × log(p_student_i)
  y_i = 1 for correct class, 0 elsewhere
  Only the correct class contributes gradient

DISTILLATION LOSS (soft targets):
L_KD = α × L_CE(y, p_student)        # standard loss
      + (1-α) × T² × KL(p_teacher/T, p_student/T)
                                       # distillation loss

Where T = temperature (higher T → softer distribution)
      α = balance between hard and soft targets

TEMPERATURE:
T=1: p_teacher = [0.95, 0.04, 0.01]  (sharp)
T=4: p_teacher = [0.55, 0.31, 0.14]  (soft, more informative)
Higher T: teacher reveals more about learned similarities
```

**THE TRADE-OFFS:**
**Gain:** Small student model approaches (not matches) teacher quality; faster inference; deployable on edge; cheaper to serve.
**Cost:** Requires access to teacher model or its outputs; student is always slightly worse than teacher; distillation requires a training run (compute cost).

---

### 🧪 Thought Experiment

**SETUP:**
Train three 6B-parameter models for sentiment analysis:

- Model A: train from scratch on 1M labelled examples
- Model B: distil from a 70B teacher using teacher soft labels on same 1M examples
- Model C: distil from a 70B teacher with only 10K examples (data-efficient scenario)

**RESULTS:**

```
Model A (from scratch, 1M hard labels):
  Accuracy: 87.3%   F1: 86.8%

Model B (distilled, 1M soft labels from 70B):
  Accuracy: 91.2%   F1: 90.7%
  (+3.9pp accuracy vs. hard label training)

Model C (distilled, 10K soft labels):
  Accuracy: 89.4%   F1: 88.9%
  (+2.1pp vs. from scratch on 1M labels!)
```

**THE INSIGHT:**
The distilled student on 10,000 examples (Model C) outperforms the from-scratch student on 1,000,000 examples (Model A). The teacher's soft labels are 100× more information-efficient than hard labels. This is the core value proposition of distillation: when you have a powerful teacher, you need far less labelled data to train a high-quality student.

---

### 🧠 Mental Model / Analogy

> Distillation is like learning physics from a Nobel laureate versus from a textbook. The textbook tells you the correct answer (hard label). The Nobel laureate doesn't just give you the answer — they explain their reasoning, show you related problems, describe what near-misses looked like, and convey their intuition about which approaches are likely to work (soft label). The student mentored by the laureate understands physics far more deeply than one who memorised textbook answers — even if both end up with the same formal degree.

Mapping:

- "Nobel laureate" → large teacher model
- "Textbook" → hard labels from a dataset
- "Their reasoning and intuitions" → soft output distribution (probabilities across all classes)
- "Far deeper understanding" → better generalisation by student
- "Same formal degree" → same architecture size

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A big AI teaches a small AI by showing it not just the right answer, but HOW likely every possible answer is — which lets the small AI learn much more from fewer examples.

**Level 2 — How to use it (junior developer):**
In practice for LLMs: (1) Generate a dataset from the teacher (teacher completions on your tasks). (2) Train a smaller student model on these completions using standard language modelling loss. This is "output distillation" — the simplest approach, used by Alpaca (distilling GPT-4 outputs into LLaMA), WizardLM, and others. This approach requires no access to teacher weights — only outputs. For better quality, use "logit distillation" — requires access to teacher's token probability distributions, not just the sampled outputs.

**Level 3 — How it works (mid-level engineer):**
**Output distillation (black-box):** Query the teacher API; collect input-output pairs; fine-tune the student using standard SFT on these pairs. Simple but loses the "soft label" information — you only get the sampled output, not the full distribution. **Logit distillation (white-box):** Requires teacher model weights. On each training example, compute teacher's token probability distribution for each position; train student to minimise KL divergence between its distribution and the teacher's. This is more powerful because the student learns from the teacher's uncertainty, not just its decisions. **Feature distillation:** Student learns to match intermediate representations (hidden states) at each layer of the teacher — requires that student and teacher have compatible architectures.

**Level 4 — Why it was designed this way (senior/staff):**
The original motivation (Hinton, 2015) was that soft labels encode "dark knowledge" — information about the relative similarities between classes that is invisible in hard labels. In LLMs, the equivalent is "token distribution knowledge": when the teacher assigns 30% probability to "happy" and 25% to "joyful," the student learns these are semantically similar — directly encoding the teacher's world model into the student. The theoretical justification: training on soft labels from a large teacher is equivalent, in information-theoretic terms, to training on a much larger hard-labelled dataset. The practical manifestation: Alpaca (fine-tuning 7B LLaMA on 52K GPT-4 outputs) produced a model dramatically better than 7B LLaMA trained from scratch on the same scale of natural language data — the teacher's knowledge was distilled efficiently through its outputs.

---

### ⚙️ How It Works (Mechanism)

```
DISTILLATION PIPELINE:

TEACHER (large, expensive):
  70B parameters
  Inputs → [token probabilities over vocab]
  e.g., "The cat sat on the ___"
  → "mat": 0.42, "floor": 0.31, "chair": 0.18 ...

STUDENT (small, cheap):
  7B parameters
  Learns to match teacher's token distribution
  Loss = KL(teacher_probs || student_probs)

TRAINING:
  For each training example:
    1. Forward pass through teacher → p_teacher
    2. Forward pass through student → p_student
    3. Loss = KL(p_teacher / T || p_student / T)
    4. Backpropagate through STUDENT ONLY
       (teacher weights frozen)

RESULT:
  Student learns: which tokens are likely
                  which are related but less likely
                  which are implausible
  → Richer learning signal than hard labels
```

---

### 🔄 The Complete Picture — End-to-End Flow

**OUTPUT DISTILLATION FLOW (black-box):**

```
Define tasks (prompts)
    ↓
Query teacher API for responses
    ↓
Collect (prompt, teacher_response) dataset
    ↓
Fine-tune student model on collected dataset
    ↓
[DISTILLATION ← YOU ARE HERE]
Student learns to mimic teacher's outputs
    ↓
Evaluate student vs. teacher on benchmark
    ↓
If quality sufficient → deploy student
  (faster, cheaper, deployable on smaller hardware)
```

---

### 💻 Code Example

**Example 1 — Generate distillation dataset from teacher API:**

```python
import openai

def generate_distillation_dataset(
    prompts: list[str],
    teacher_model: str,
    client,
    n_samples: int = 1
) -> list[dict]:
    """Generate teacher outputs for student training."""
    dataset = []
    for prompt in prompts:
        response = client.chat.completions.create(
            model=teacher_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,  # diversity in outputs
            n=n_samples
        )
        for choice in response.choices:
            dataset.append({
                "prompt": prompt,
                "response": choice.message.content
            })
    return dataset
```

**Example 2 — Logit distillation loss:**

```python
import torch
import torch.nn.functional as F

def distillation_loss(
    student_logits: torch.Tensor,  # [batch, seq, vocab]
    teacher_logits: torch.Tensor,  # [batch, seq, vocab]
    labels: torch.Tensor,          # [batch, seq]
    temperature: float = 2.0,
    alpha: float = 0.7
) -> torch.Tensor:
    """Combined hard-label and soft-label distillation loss."""
    # Hard label loss (standard cross-entropy)
    hard_loss = F.cross_entropy(
        student_logits.view(-1, student_logits.size(-1)),
        labels.view(-1),
        ignore_index=-100
    )

    # Soft label loss (KL divergence from teacher)
    soft_student = F.log_softmax(
        student_logits / temperature, dim=-1
    )
    soft_teacher = F.softmax(
        teacher_logits / temperature, dim=-1
    )
    soft_loss = F.kl_div(
        soft_student,
        soft_teacher,
        reduction="batchmean"
    ) * (temperature ** 2)  # scale for temperature

    return alpha * hard_loss + (1 - alpha) * soft_loss
```

---

### ⚖️ Comparison Table

| Compression Method                  | Training Cost | Quality vs. Same Size | Access Needed                     | Best For                           |
| ----------------------------------- | ------------- | --------------------- | --------------------------------- | ---------------------------------- |
| **Output distillation (black-box)** | Low           | Excellent             | Teacher API                       | LLM fine-tuning with GPT-4 outputs |
| **Logit distillation (white-box)**  | Medium        | Best                  | Teacher weights                   | Highest quality student            |
| **Feature distillation**            | High          | Excellent             | Teacher weights + compatible arch | Research                           |
| Model Quantization                  | None          | Very good (< 1% loss) | Full model                        | Quick size reduction               |
| Model Pruning                       | Medium        | Good                  | Full model                        | Structured sparsity                |
| Train from scratch                  | Highest       | Good                  | N/A                               | Novel architectures                |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Distillation always needs white-box access to the teacher" | Output distillation (API distillation) only needs teacher outputs — widely used (Alpaca, WizardLM used GPT-4 API)                                 |
| "Distillation makes the student equal to the teacher"       | Student always has lower quality ceiling than teacher (smaller capacity); distillation closes the gap but doesn't eliminate it                    |
| "Distillation and fine-tuning are the same"                 | Fine-tuning adapts a model to a specific task; distillation transfers knowledge from teacher to student — can be used together                    |
| "Higher temperature is always better"                       | Temperature controls softness of the teacher distribution; too high (> 5) makes all tokens equally likely, removing signal; T=2–4 is typical      |
| "Distillation only works for classification"                | Distillation generalises to any autoregressive generation: distil GPT-4's writing style, reasoning patterns, code generation into a smaller model |

---

### 🚨 Failure Modes & Diagnosis

**Student Quality Ceiling (Capacity Mismatch)**

**Symptom:** Despite excellent distillation training, the student model's performance plateaus far below the teacher — the quality gap is larger than expected for the parameter count difference.

**Root Cause:** The student architecture is too small to represent the knowledge the teacher encodes. The teacher's representations require a certain capacity to hold; below that threshold, knowledge cannot be transferred faithfully.

**Diagnostic Command / Tool:**

```python
def check_student_capacity(
    student_model,
    teacher_model,
    eval_prompts: list[str],
    generate_fn
) -> dict:
    """Compare student vs. teacher on eval set."""
    student_outputs = [
        generate_fn(student_model, p) for p in eval_prompts
    ]
    teacher_outputs = [
        generate_fn(teacher_model, p) for p in eval_prompts
    ]
    # Compare distributions
    matching = sum(
        1 for s, t in zip(student_outputs, teacher_outputs)
        if s.strip().lower() == t.strip().lower()
    )
    match_rate = matching / len(eval_prompts)
    print(f"Student-teacher agreement: {match_rate:.1%}")
    if match_rate < 0.6:
        print("WARNING: Large student-teacher gap — "
              "consider larger student or task simplification")
    return {"agreement": match_rate}
```

**Fix:** Use a larger student (reduce compression ratio); use task-specific distillation (single task, not general); apply feature distillation to better align intermediate representations.

**Prevention:** Set realistic expectations — a 3B student cannot match a 70B teacher; plan for a quality delta.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Training` — distillation requires a student training run
- `Model Weights` — distillation operates on model outputs and optionally weights
- `Fine-Tuning` — output distillation is commonly implemented as supervised fine-tuning on teacher outputs

**Builds On This (learn these next):**

- `Model Pruning` — complementary compression: combine pruning and distillation
- `Inference` — distillation enables faster inference by reducing model size
- `Foundation Models` — many deployed foundation models are distillations of larger internal models

**Alternatives / Comparisons:**

- `Model Pruning` — removes weights from existing model; distillation trains a new smaller model
- `Model Quantization` — reduces precision; orthogonal to distillation — can combine both
- `Transfer Learning` — distillation is a form of transfer from teacher to student

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Training a small student model to mimic   │
│              │ a large teacher's output distribution     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Teacher's soft label (probability over    │
│              │ all classes) is 10–100× more informative  │
│              │ than a hard correct/wrong label           │
├──────────────┼───────────────────────────────────────────┤
│ TWO MODES    │ Black-box: use teacher API outputs only   │
│              │ White-box: use teacher logits/features    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Large model too expensive to serve;       │
│              │ want small deployable model with          │
│              │ near-large-model quality                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Student capacity too small to represent   │
│              │ teacher knowledge; task requires          │
│              │ full teacher reasoning capability         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Learn from the master's thinking,        │
│              │ not just the master's answer."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Model Pruning → Foundation Models →       │
│              │ Speculative Decoding                      │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** OpenAI's terms of service prohibit using GPT-4 API outputs to train competing models. If a startup violates this and trains a 7B model on 10M GPT-4 outputs, they may produce a competitive model at low cost. Explain the technical mechanism by which this would work (what knowledge is being transferred, how the student captures it), then discuss why the legal restriction exists from a market economics perspective — and what alternative legal approaches are available to achieve the same outcome.

**Q2.** You are distilling a 70B reasoning model into a 7B student. After distillation, the student performs well on single-step reasoning tasks (95% of teacher quality) but collapses dramatically on multi-step chain-of-thought reasoning (62% of teacher quality). Diagnose the mechanistic reason for this asymmetry and design a distillation strategy specifically targeted at preserving multi-step reasoning capability — including what data you would use, what loss function, and what evaluation you would run to verify success.
