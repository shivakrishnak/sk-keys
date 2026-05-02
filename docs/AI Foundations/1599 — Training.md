---
layout: default
title: "Training"
parent: "AI Foundations"
nav_order: 1599
permalink: /ai-foundations/training/
number: "1599"
category: AI Foundations
difficulty: ★★★
depends_on: Neural Network, Model Parameters, Deep Learning
used_by: Pre-training, Fine-Tuning, RLHF, Transfer Learning
related: Inference, Overfitting / Underfitting, Model Parameters
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - internals
---

# 1599 — Training

⚡ TL;DR — Training is the process of iteratively adjusting a neural network's parameters via gradient descent until the model produces outputs that match the desired behaviour on the training data.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You want to build a spam classifier. You start writing rules: "If the email contains 'Nigerian prince', mark as spam." A week later you have 10,000 rules, spammers adapt every day, the rules conflict, and your system still misses 30% of spam. Every new spam tactic requires a human to write new rules. The system cannot learn from examples — it can only do what you explicitly programme.

**THE BREAKING POINT:**
Rule-based systems cannot generalise. They can only handle cases their designers anticipated. Natural language, images, and audio contain infinitely many patterns that no human can enumerate. A system that requires explicit human rules cannot reach human-level performance on perceptual or linguistic tasks.

**THE INVENTION MOMENT:**
This is exactly why neural network Training was developed — as the mechanism by which a model automatically discovers the parameters that best map inputs to outputs, learning from examples rather than from rules.

---

### 📘 Textbook Definition

**Training** is the iterative process of minimising a loss function over a dataset by computing gradients of the loss with respect to model parameters and updating those parameters via an optimisation algorithm (typically gradient descent with momentum, e.g., Adam). A complete pass over the training dataset is called an **epoch**. Training proceeds in **minibatches** — subsets of the dataset — for computational efficiency. For LLMs, pre-training involves next-token prediction (causal language modelling) as the primary training objective on a large text corpus.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Training is the model learning from examples by repeatedly making predictions, measuring errors, and adjusting internal numbers to reduce those errors.

**One analogy:**
> Imagine learning to throw darts. You throw (forward pass), see where the dart lands (loss), feel how far off you were (gradient), and adjust your grip and release slightly (weight update). You repeat thousands of times. Eventually your throws cluster around the bullseye — not because someone told you exactly how to throw, but because you adjusted based on feedback. Training works identically.

**One insight:**
Training never tells the model what to know — it only shows it what "correct" looks like (training data) and measures how wrong its current parameters are (loss). The model discovers for itself what patterns in its parameters produce correct outputs. This is why trained models surprise their creators with emergent capabilities not explicitly programmed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A differentiable loss function measures how wrong the current parameters are.
2. Gradients tell us the direction to adjust each parameter to reduce the loss.
3. Gradient descent iteratively nudges parameters toward lower loss.
4. Given enough data and capacity, loss can be driven very low — but generalisation is not guaranteed.

**DERIVED DESIGN:**
The core training loop:

```
for each minibatch in training_data:
    # Forward pass: compute predictions
    predictions = model(inputs)
    
    # Compute loss: how wrong?
    loss = loss_fn(predictions, targets)
    
    # Backward pass: compute gradients
    loss.backward()
    
    # Update: nudge params in right direction
    optimizer.step()
    
    # Reset gradients for next batch
    optimizer.zero_grad()
```

For LLMs, the loss function is **cross-entropy** on next-token prediction:

`loss = -Σ log P(next_token | context)`

Minimising this loss means maximising the probability of the correct next token — training the model to predict text like its training corpus.

**THE TRADE-OFFS:**
**Gain:** The model automatically discovers optimal parameters for the training distribution; scales with data and compute.
**Cost:** Requires enormous compute (GPT-3 training ≈ $5M), large datasets, and careful hyperparameter tuning. The model learns to predict training data — not necessarily to be truthful, safe, or aligned with human values. Those properties require additional training phases (RLHF, DPO).

---

### 🧪 Thought Experiment

**SETUP:**
Train a minimal 1-layer linear model to predict "Is this email spam?" Binary classification on 1,000 emails.

**STEP BY STEP:**

Step 1 — Initialisation: parameters are random. Model makes ~50% random guesses.

Step 2 — First batch (100 emails): model predicts. 52 correct, 48 wrong. Loss = 0.693 (random chance).

Step 3 — Backprop: compute ∂loss/∂weight for each weight. Gradient for "Nigerian prince" feature is -0.3 (reducing this weight reduces loss). Gradient for "invoice" feature is +0.1.

Step 4 — Update: `weight["Nigerian prince"] -= lr × (-0.3)` → weight increases. The model now considers "Nigerian prince" more suspicious.

Step 5 — Repeat for 10,000 batches: model has seen every email ~1,000 times. Loss drops to 0.15. Accuracy: 94%.

**THE INSIGHT:**
Training is a feedback loop. No one told the model that "Nigerian prince" is suspicious. The model discovered it because emails containing that phrase were labelled spam in the training data, and penalising wrong predictions pushed the weight for that feature higher. The model learns correlations, not causal rules.

---

### 🧠 Mental Model / Analogy

> Think of training as water finding its way down a mountain. The loss landscape is the mountain — a high-dimensional surface where lower altitude = lower loss. Gradient descent is the water: it always flows downhill (in the direction of steepest descent). Starting from a random location (random parameters), the water flows toward a valley (local minimum). The learning rate is how fast the water flows — too fast and it overshoots valleys; too slow and it takes forever to reach them.

Mapping:
- "Mountain surface" → loss landscape (function of all parameters)
- "Current position on mountain" → current parameter values
- "Altitude" → current loss value
- "Downhill direction" → negative gradient
- "Water flowing" → gradient descent step
- "Valley" → local minimum (low loss region)

Where this analogy breaks down: in a 2D mountain, there are few valleys. In a billion-dimensional loss landscape, there are astronomically many local minima — and counterintuitively, most are approximately as good as the global minimum for large neural networks.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Training is the AI learning phase. You show it millions of examples with correct answers. It makes guesses, sees where it was wrong, and adjusts its internal numbers. After enough examples, it learns the patterns.

**Level 2 — How to use it (junior developer):**
Training requires: a dataset, a model architecture, a loss function, and an optimiser. For LLM fine-tuning, frameworks like Hugging Face Trainer abstract the loop. Key settings: `learning_rate` (how big each update step is), `batch_size` (how many examples per update), `num_epochs` (how many full passes through data). Monitor training loss and validation loss — if they diverge, you have overfitting.

**Level 3 — How it works (mid-level engineer):**
The backward pass uses automatic differentiation (autograd) to compute gradients via the chain rule. PyTorch builds a computation graph during the forward pass; `.backward()` traverses it in reverse, computing gradients. The Adam optimiser maintains first and second moment estimates of gradients, enabling adaptive learning rates per parameter. Mixed-precision training (float16 forward pass, float32 gradient accumulation) reduces memory and speeds training by 2–3×. Gradient checkpointing trades compute for memory by recomputing activations during backward pass instead of storing them.

**Level 4 — Why it was designed this way (senior/staff):**
The choice of stochastic minibatch gradient descent over full-batch gradient descent is a deliberate trade-off: minibatches introduce noise in gradient estimates, which acts as an implicit regulariser (the noise prevents convergence to sharp, overfit minima). Large-batch training (common at LLM scale) requires careful learning rate scaling (linear or sqrt scaling with batch size) to maintain similar convergence dynamics. At LLM pre-training scale, training is distributed across thousands of GPUs using 3D parallelism: data parallelism (each GPU sees a different batch), tensor parallelism (weight matrices sharded across GPUs), and pipeline parallelism (different model layers on different GPUs). The gradient synchronisation across GPUs is the key bottleneck — techniques like ZeRO optimizer sharding reduce redundant memory across data-parallel replicas.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ DATA: Training corpus (trillions of tokens) │
│ Sampled in random minibatches each step     │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ FORWARD PASS                                │
│ Input tokens → transformer layers          │
│ → output logits                             │
│ Loss = cross-entropy(logits, next_tokens)   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ BACKWARD PASS                               │
│ Autograd traces computation graph           │
│ Computes ∂loss/∂W for every weight W       │
│ Memory: ~3× forward pass (grads + optim)   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ PARAMETER UPDATE                            │
│ Adam: W = W - lr × m̂/(√v̂ + ε)             │
│ (m̂ = bias-corrected 1st moment)            │
│ (v̂ = bias-corrected 2nd moment)            │
└──────────────┬──────────────────────────────┘
               ↓
     Repeat for billions of steps
```

**Training compute scale (rough):**
```
C ≈ 6 × N × D
Where:
  N = number of parameters (e.g., 7×10⁹)
  D = training tokens (e.g., 2×10¹²)
  C ≈ 8.4×10²² FLOPs for Llama-2-7B
At 312 TFLOPS/GPU (A100) = ~300K GPU-hours
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Random parameter initialisation
    ↓
Training data sampled (minibatch)
    ↓
[FORWARD PASS ← YOU ARE HERE]
  loss computed
    ↓
[BACKWARD PASS ← YOU ARE HERE]
  gradients computed
    ↓
[PARAMETER UPDATE ← YOU ARE HERE]
  weights adjusted
    ↓
Checkpoint saved every N steps
    ↓
Training loss decreases over steps
    ↓
Training complete → model saved
    ↓
Evaluation: measure test loss/accuracy
```

**FAILURE PATH:**
```
Loss spikes or becomes NaN
    ↓
Gradient explosion (or bad batch)
    ↓
Apply gradient clipping
If NaN persists: check for bad data (inf/NaN)
Reduce learning rate
```

**WHAT CHANGES AT SCALE:**
At frontier model scale (GPT-4, Llama-3), training runs for weeks across thousands of GPUs. Hardware failures are expected — training must be fault-tolerant via frequent checkpointing and automatic resume. Training instabilities (loss spikes) must be detected and handled automatically. Data quality becomes the dominant factor: at this scale, the training corpus composition (what data mix was used) determines model behaviour more than architecture choices.

---

### 💻 Code Example

**Example 1 — Core training loop:**
```python
import torch
import torch.nn as nn
from torch.optim import AdamW

model = MyModel()
optimizer = AdamW(model.parameters(), lr=1e-4,
                  weight_decay=0.01)
loss_fn = nn.CrossEntropyLoss()

model.train()  # enable dropout, batch norm training mode

for epoch in range(num_epochs):
    for batch in dataloader:
        inputs, targets = batch

        # Forward pass
        logits = model(inputs)
        loss = loss_fn(logits, targets)

        # Backward pass
        optimizer.zero_grad()  # clear previous gradients
        loss.backward()        # compute gradients

        # Gradient clipping (prevent explosion)
        torch.nn.utils.clip_grad_norm_(
            model.parameters(), max_norm=1.0
        )

        optimizer.step()  # update parameters

    print(f"Epoch {epoch}: loss={loss.item():.4f}")
```

**Example 2 — Mixed-precision training (faster, less memory):**
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()  # handles gradient scaling

for batch in dataloader:
    optimizer.zero_grad()

    with autocast():  # forward pass in float16
        logits = model(inputs)
        loss = loss_fn(logits, targets)

    # Scale loss for numerical stability in float16
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(
        model.parameters(), max_norm=1.0
    )
    scaler.step(optimizer)
    scaler.update()
```

**Example 3 — Monitoring training health:**
```python
import wandb

wandb.init(project="my-llm-training")

for step, batch in enumerate(dataloader):
    loss = train_step(batch)

    if step % 100 == 0:
        # Log metrics for monitoring
        wandb.log({
            "train/loss": loss.item(),
            "train/learning_rate": scheduler.get_lr()[0],
            "train/grad_norm": compute_grad_norm(model),
            "train/step": step
        })

        # Alert on training instability
        if loss.item() > 10.0:
            wandb.alert(title="Loss spike detected",
                       text=f"Step {step}: loss={loss}")
```

---

### ⚖️ Comparison Table

| Training Phase | Objective | Data Size | Compute | Best For |
|---|---|---|---|---|
| **Pre-training** | Next-token prediction | Trillions of tokens | $M–$B | Foundation model creation |
| Fine-tuning (SFT) | Supervised on demos | 1K–1M examples | $K–$M | Task specialisation |
| RLHF | Human preference ranking | 10K–100K pairs | $M | Alignment, safety |
| LoRA fine-tuning | SFT with frozen base | 1K–100K | $10–$100 | Efficient domain adaptation |
| Continual pre-training | Next-token prediction | Billions of tokens | $K–$M | Domain knowledge injection |

**How to choose:** For most teams, LoRA fine-tuning on a pretrained base model is the practical default — it achieves strong results with minimal compute. Only frontier labs have the resources for full pre-training from scratch.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Training on more data always helps" | More data helps until diminishing returns; low-quality data actively hurts — data quality > data quantity |
| "Training teaches the model to understand" | Training minimises cross-entropy loss — it teaches statistical prediction, not comprehension |
| "Once trained, a model's behaviour is fixed" | Fine-tuning can substantially change model behaviour with relatively little data |
| "Training is reproducible" | Floating-point non-determinism on GPUs means exact reproduction is extremely difficult; same seed + config → similar but not identical results |
| "The loss must reach zero for good models" | Very low training loss often means overfitting; the goal is low validation loss, not training loss |

---

### 🚨 Failure Modes & Diagnosis

**Loss NaN / Training Collapse**

**Symptom:** Training loss becomes `nan` after several thousand steps; model outputs garbage.

**Root Cause:** Gradient explosion (unclamped gradients cause weights to overflow to ±infinity → NaN). Often triggered by a bad batch with extreme token distributions.

**Diagnostic Command / Tool:**
```python
# Check for NaN in gradients after backward()
for name, param in model.named_parameters():
    if param.grad is not None:
        if torch.isnan(param.grad).any():
            print(f"NaN gradient in: {name}")
```

**Fix:** Gradient clipping + reduce learning rate. Check training data for malformed examples (NaN/Inf values). Restore from last checkpoint.

**Prevention:** Always use gradient clipping (`clip_grad_norm_`); implement checkpoint recovery; monitor gradient norms in real time.

---

**Overfitting (Train loss low, val loss high)**

**Symptom:** Training loss ≈ 0.1 but validation loss = 2.5; model memorises training examples but fails on new inputs.

**Root Cause:** Model has too much capacity relative to dataset size; it memorises training examples instead of learning generalisable patterns.

**Diagnostic Command / Tool:**
```python
# Plot training vs validation loss
import matplotlib.pyplot as plt
plt.plot(train_losses, label="train")
plt.plot(val_losses, label="validation")
plt.xlabel("Step"); plt.ylabel("Loss")
plt.legend()
plt.show()  # Divergence = overfitting
```

**Fix:** Reduce model size; add dropout; add weight decay; increase training data; use early stopping.

**Prevention:** Always monitor validation loss independently; use early stopping with patience parameter.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Neural Network` — training adjusts the parameters of a neural network
- `Model Parameters` — training is the process that gives parameters their values
- `Deep Learning` — training deep networks requires backpropagation, not available in shallow networks

**Builds On This (learn these next):**
- `Pre-training` — large-scale training on unlabelled data to create a foundation model
- `Fine-Tuning` — continuing training on task-specific data from a pretrained checkpoint
- `RLHF` — training with human feedback as the reward signal to improve alignment

**Alternatives / Comparisons:**
- `Inference` — the production phase after training; weights are frozen
- `Overfitting / Underfitting` — the primary failure mode of training to diagnose and prevent
- `Transfer Learning` — avoids training from scratch by starting from pretrained weights

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Iterative parameter optimisation via      │
│              │ gradient descent to minimise loss         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Hand-coded rules cannot scale to natural  │
│ SOLVES       │ language — learned parameters can         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Training minimises statistical prediction │
│              │ loss — not logical correctness; alignment │
│              │ and truth must be separately engineered   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Creating a model from scratch (costly) or │
│              │ fine-tuning a pretrained model (cheap)    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never train from scratch when a           │
│              │ pretrained base model exists              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ More compute/data = better performance vs │
│              │ cost, overfitting, and alignment risk     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Throwing darts until muscle memory kicks │
│              │ in — except the muscle is 7 billion       │
│              │ numbers and the darts are gradients."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pre-training → Fine-Tuning → RLHF         │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** During LLM pre-training at scale, a team notices that training loss decreases steadily for 90% of training, then spikes sharply at step 850,000, then recovers and continues decreasing. The spike correlates with a batch containing a specific type of code file. Trace the mechanism: what happens in the forward pass, backward pass, and parameter update at that step — and what does the recovery tell you about the loss landscape's properties at frontier model scale?

**Q2.** The Chinchilla scaling law suggests that the optimal training compute allocation is approximately 50% on parameters and 50% on training data. A team has $1M of compute budget: option A is to train a 13B model on 200B tokens; option B is to train a 7B model on 400B tokens. Both cost the same. Which produces the better model according to Chinchilla, and what does this tell you about whether the industry's pre-Chinchilla approach (GPT-3: 175B params on 300B tokens) was optimal?
