---
layout: default
title: "Overfitting / Underfitting"
parent: "AI Foundations"
nav_order: 1607
permalink: /ai-foundations/overfitting-underfitting/
number: "1607"
category: AI Foundations
difficulty: ★★☆
depends_on: Training, Model Parameters, Neural Network
used_by: Model Evaluation Metrics, Fine-Tuning, Benchmark (AI)
related: Training, Bias in AI, Model Evaluation Metrics
tags:
  - ai
  - ml
  - intermediate
  - mental-model
  - fundamentals
---

# 1607 — Overfitting / Underfitting

⚡ TL;DR — Overfitting is when a model memorises training data rather than learning general patterns; underfitting is when a model is too simple to capture the patterns at all. Both degrade real-world performance.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A fraud detection model achieves 99.8% accuracy on its training set. In production it catches only 62% of fraud. The team is baffled — the training metrics looked perfect. Without understanding overfitting, they have no framework to diagnose what went wrong or how to fix it.

**THE BREAKING POINT:**
Training performance and production performance regularly diverge. Without a conceptual framework explaining WHY they diverge, engineers are left iterating blindly — adding more data, changing architectures, tuning hyperparameters — without knowing which direction to go.

**THE INVENTION MOMENT:**
The overfitting/underfitting framework, formalised in the bias-variance tradeoff, gives engineers a diagnostic lens: measure training error and validation error separately, compare them, and the gap tells you precisely where on the generalisation curve you are.

---

### 📘 Textbook Definition

**Overfitting** occurs when a model learns the training data so precisely — including its noise and idiosyncratic patterns — that it fails to generalise to new data. Training error is low; validation/test error is high. **Underfitting** occurs when the model is too simple (or undertrained) to capture the true patterns in the data. Both training error AND validation error are high. The formal framework is the **bias-variance tradeoff**: high bias = underfitting (systematic error); high variance = overfitting (sensitivity to training set noise). The optimal model minimises total error = bias² + variance + irreducible noise.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Overfitting = memorised the test answers; underfitting = didn't study enough.

**One analogy:**

> **Underfitting:** A student who studied only the chapter titles. They answer every question with a vague generic answer. Correct sometimes by accident, but never deeply right.
>
> **Overfitting:** A student who memorised every solved problem in the textbook word for word. They ace the practice exam perfectly. But when the exam changes the numbers or context, they fail — they memorised solutions, not concepts.
>
> **Good fit:** A student who understands the underlying principles and can solve novel problems they've never seen.

**One insight:**
The goal is never to minimise training error — it's to minimise generalisation error. These are different objectives, and maximising training error minimisation eventually leads to overfitting.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A model with infinite capacity and zero regularisation WILL overfit given enough training.
2. A model with insufficient capacity CANNOT fit the patterns even if trained perfectly.
3. Generalisation error = Bias² + Variance + Irreducible Noise.

**DERIVED DESIGN:**

```
               Underfitting ←───→ Overfitting

High bias                              High variance
High train error     Good fit          Low train error
High val error       ↑                 High val error
                 Optimal zone
                (low bias AND
                 low variance)

Model Complexity →→→
```

**For LLMs specifically:**
LLMs are so large that classical overfitting (memorising a small training set) is rarely the primary concern for pre-training — the training corpus is so vast that the model cannot memorise it. But fine-tuning on small datasets is a classic overfitting risk:

- Fine-tuning on 100 examples → model memorises those 100 examples
- Loss on 100 training examples → near zero
- Loss on held-out examples → high

**THE TRADE-OFFS:**
**Addressing overfitting:** Regularisation (dropout, weight decay, early stopping), more training data, simpler model, cross-validation.
**Addressing underfitting:** More capacity (larger model), more training time, feature engineering, reducing regularisation.

---

### 🧪 Thought Experiment

**SETUP:**
Three classifiers are trained on 200 customer churn examples:

- Model A: 5-parameter logistic regression
- Model B: 50-parameter neural network
- Model C: 5000-parameter neural network trained to convergence on the 200 examples

**RESULTS ON TRAIN / VALIDATION:**

Model A: Train 68% / Val 67% → Underfitting (linear model can't capture churn patterns)
Model B: Train 84% / Val 82% → Good generalisation (capacity matches task complexity)
Model C: Train 99.9% / Val 71% → Overfitting (memorised 200 examples, can't generalise)

**THE INSIGHT:**
The training accuracy of Model C (99.9%) looks impressive — but it's misleading. The model "knows" the answer for every training customer because it memorised their specific feature combinations. A new customer who doesn't exactly match a memorised training case gets misclassified. The gap between train accuracy (99.9%) and validation accuracy (71%) IS the diagnosis: 28.9 percentage points of overfitting.

---

### 🧠 Mental Model / Analogy

> Think of the model's decision boundary as a line drawn through data points. Underfitting: the line is too simple (a straight line through data that has curves) — it misses many points on both sides. Overfitting: the line perfectly threads through every training point but zigzags wildly to do so — when new points arrive, they land nowhere near the erratic boundary. The right model draws a smooth curve that captures the general trend without threading every outlier.

Mapping:

- "Straight line through curved data" → underfitting (high bias)
- "Wildly zigzagging line through every point" → overfitting (high variance)
- "Smooth curve capturing the trend" → good generalisation

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Overfitting: the AI is too good at memorising your examples but can't handle new ones. Underfitting: the AI isn't learning the patterns well at all. You want the middle ground — a model that learns the real pattern, not the noise.

**Level 2 — How to use it (junior developer):**
Standard diagnostic: always split data into train / validation / test. Train on train; measure performance on validation (not used in training). If val error >> train error → overfitting. If val error ≈ train error AND both are high → underfitting. Key regularisation techniques for overfitting: dropout (randomly disable neurons during training), weight decay (penalise large weights in the loss function), early stopping (stop training when val loss starts rising).

**Level 3 — How it works (mid-level engineer):**
Bias-variance decomposition: For a model f̂ trained on a dataset D, and target function f:

E[(y − f̂(x))²] = Bias[f̂(x)]² + Var[f̂(x)] + σ²

Where σ² is irreducible noise. Bias = systematic error from wrong model assumptions; Variance = sensitivity to the specific training set sampled. Increasing model capacity reduces bias (can fit more complex patterns) but increases variance (sensitive to noise). The optimal point minimises their sum. For neural networks, double-descent complicates this: very large models can show lower test error than the bias-variance peak — an empirical finding not fully explained by classical theory.

**Level 4 — Why it was designed this way (senior/staff):**
Classical bias-variance tradeoff theory was developed for parametric models where adding parameters strictly increases variance. The discovery of "double descent" (Belkin et al., 2019) for overparameterised models challenges this. In the modern regime (models with many more parameters than training examples), variance can DECREASE after the interpolation threshold — the point where the model can exactly fit all training data. This is why GPT-4 (hundreds of billions of parameters) trained on trillions of tokens doesn't catastrophically overfit: the model is in the "second descent" of double-descent error curves. For fine-tuning scenarios on small datasets, classical overfitting theory applies fully: too many updates on too few examples → memorisation.

---

### ⚙️ How It Works (Mechanism)

```
TRAINING CURVES — THE DIAGNOSTIC SIGNAL:

Overfitting:
    Loss
    │
    │ ── Training loss
    │    (continues falling)
    │
    │          ↗ Validation loss
    │         /  (starts rising)
    │────────┬────────────
    │        ↑
    │   EARLY STOPPING POINT
    │
    └───────────────────── Epochs

Underfitting:
    Loss
    │ ── Training loss (high, not falling much)
    │ ── Validation loss (also high)
    │
    │ Both flat at high error →
    │ model lacks capacity to fit data
    │
    └───────────────────── Epochs

Good fit:
    Loss
    │ ── Training loss (falls, plateaus)
    │ ── Validation loss (falls, plateaus near train)
    │
    │ Small gap, both at low error
    │
    └───────────────────── Epochs
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Split data: 70% train / 15% val / 15% test
    ↓
Train model on train set
    ↓
Monitor train loss AND validation loss each epoch
    ↓
[DIAGNOSIS ← YOU ARE HERE]
Compare train vs. val loss:
    Gap large → overfitting → add regularisation
    Both high → underfitting → increase capacity
    Both low, small gap → good fit
    ↓
Apply fix; retrain
    ↓
Final evaluation on TEST set (held out until now)
```

**FAILURE PATH (fine-tuning LLMs):**

```
Fine-tune LLM on 200 labelled examples
    ↓
Training loss → 0.01 (near-zero)
    ↓
Assume model is great; skip validation evaluation
    ↓
Deploy; production performance poor
    ↓
Retrospective: 200 examples memorised;
               no generalisation measured
    ↓
Fix: early stopping + eval on held-out set
     during fine-tuning
```

---

### 💻 Code Example

**Example 1 — Detect overfitting with training curves:**

```python
import matplotlib.pyplot as plt

def plot_training_curves(
    train_losses: list[float],
    val_losses: list[float]
) -> None:
    """Plot train vs validation loss to diagnose fit."""
    epochs = range(1, len(train_losses) + 1)
    plt.figure(figsize=(10, 4))
    plt.plot(epochs, train_losses,
             label="Training loss", color="blue")
    plt.plot(epochs, val_losses,
             label="Validation loss", color="red")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    # Diagnose
    gap = val_losses[-1] - train_losses[-1]
    if gap > 0.05:
        print(f"WARNING: Overfitting detected. "
              f"Gap = {gap:.3f}")
    elif val_losses[-1] > 0.5:
        print(f"WARNING: Possible underfitting. "
              f"Val loss = {val_losses[-1]:.3f}")
    else:
        print(f"Good fit. Gap = {gap:.3f}")
    plt.show()
```

**Example 2 — Early stopping in PyTorch:**

```python
import torch

class EarlyStopping:
    def __init__(self, patience: int = 5,
                 min_delta: float = 0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")

    def __call__(self, val_loss: float,
                 model: torch.nn.Module) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            torch.save(model.state_dict(), "best_model.pt")
        else:
            self.counter += 1
            if self.counter >= self.patience:
                print(f"Early stopping at best val "
                      f"loss: {self.best_loss:.4f}")
                return True  # stop training
        return False
```

**Example 3 — Regularisation with weight decay:**

```python
from transformers import Trainer, TrainingArguments

# Weight decay is L2 regularisation — penalises large weights
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=10,
    learning_rate=2e-5,
    weight_decay=0.01,      # L2 regularisation coefficient
    evaluation_strategy="epoch",
    load_best_model_at_end=True,  # implicit early stopping
    metric_for_best_model="eval_loss",
    greater_is_better=False
)
```

---

### ⚖️ Comparison Table

| Symptom                                     | Diagnosis              | Fix                                                      |
| ------------------------------------------- | ---------------------- | -------------------------------------------------------- |
| Train low, val high (large gap)             | **Overfitting**        | Regularisation, more data, early stopping, simpler model |
| Train high, val high (both high, small gap) | **Underfitting**       | Larger model, more training, less regularisation         |
| Train low, val low (both low, small gap)    | **Good fit**           | None needed                                              |
| Train continues falling, val stops falling  | **Near overfitting**   | Early stopping                                           |
| Both high even with large model             | **Data quality issue** | Clean data, re-examine labels                            |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                               |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "High training accuracy = good model"               | High training accuracy with high validation loss = overfitting; training accuracy is a lagging diagnostic, not a target                                               |
| "Larger models always overfit"                      | Double-descent shows that sufficiently overparameterised models can generalise well; classical theory breaks down in the modern regime                                |
| "More data always fixes overfitting"                | More data helps, but if the model is too complex and the task is inherently noisy, more data helps less than reducing model complexity                                |
| "Dropout is always good"                            | Dropout is regularisation and reduces effective capacity — it can cause underfitting if applied too aggressively to small models                                      |
| "Validation set performance = test set performance" | Using validation performance to select hyperparameters can lead to "over-optimisation" on the validation set; always hold out a test set never used for any decisions |

---

### 🚨 Failure Modes & Diagnosis

**Silent Overfitting (Deployed Without Validation)**

**Symptom:** Model achieves high training accuracy but production metrics are significantly worse than expected. No validation split was used during development.

**Root Cause:** Training loss was used as the sole evaluation metric. Without a held-out validation set, overfitting is invisible until production.

**Diagnostic Command / Tool:**

```python
# Retrospective: check for overfitting after the fact
# by evaluating on a random held-out subset of training data
def retrospective_overfit_check(
    model,
    train_dataset,
    hold_out_fraction: float = 0.2
) -> None:
    n = len(train_dataset)
    split = int(n * (1 - hold_out_fraction))
    train_eval = train_dataset[:split]
    held_out = train_dataset[split:]

    train_acc = evaluate(model, train_eval)
    held_out_acc = evaluate(model, held_out)

    print(f"Train acc: {train_acc:.1%}")
    print(f"Held-out acc: {held_out_acc:.1%}")
    print(f"Gap: {(train_acc - held_out_acc) * 100:.1f}pp")
    if train_acc - held_out_acc > 0.10:
        print("OVERFITTING CONFIRMED")
```

**Fix:** Always split train/val before training. Use early stopping. Apply dropout or weight decay.

**Prevention:** Make train/val/test split the first step in any training pipeline — before any model decisions are made.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Training` — overfitting and underfitting are properties of the training process
- `Model Parameters` — capacity (number of parameters) determines the overfitting risk
- `Neural Network` — neural network training dynamics determine where on the bias-variance curve you land

**Builds On This (learn these next):**

- `Model Evaluation Metrics` — measuring generalisation performance requires careful metric selection
- `Fine-Tuning` — fine-tuning small datasets is the primary overfitting scenario in LLM development
- `Benchmark (AI)` — benchmark contamination is overfitting at pre-training scale

**Alternatives / Comparisons:**

- `Bias in AI` — overfitting can introduce or amplify dataset biases
- `Transfer Learning` — helps avoid overfitting by starting from a good initialisation
- `Model Evaluation Metrics` — the metrics used to detect and measure overfitting

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Overfitting = memorised training noise;   │
│              │ Underfitting = too simple to learn        │
│              │ Both degrade real-world performance       │
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSE     │ Train loss low + Val loss high →          │
│              │   Overfitting                             │
│              │ Train loss high + Val loss high →         │
│              │   Underfitting                            │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Overfitting: regularise, more data,       │
│              │   early stopping, simpler model           │
│              │ Underfitting: bigger model, more          │
│              │   training, less regularisation           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Goal is GENERALISATION error, not         │
│              │ training error — always evaluate on       │
│              │ held-out data                             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never measure model quality only on       │
│              │ training data — always hold out a         │
│              │ validation set                            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Memorising the answers ≠ learning        │
│              │ the subject — validate on unseen data."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Model Evaluation Metrics →                │
│              │ Bias in AI → Benchmark (AI)               │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Modern LLMs are dramatically overparameterised relative to any fine-tuning dataset. GPT-4 has hundreds of billions of parameters; a fine-tuning dataset might have 10,000 examples. Classical bias-variance theory predicts that models with far more parameters than data points should catastrophically overfit. Explain why this doesn't always happen in practice (with reference to double descent and implicit regularisation), and identify the conditions under which catastrophic overfitting DOES occur even for large LLMs.

**Q2.** A team fine-tunes an LLM on their company's proprietary support tickets. They use cross-validation (5-fold) and achieve consistent 91% accuracy across all folds. They deploy the model. After 6 months, accuracy has dropped to 74%. No retraining has occurred. Diagnose all possible causes of this degradation — and explain which cause would require retraining to fix, which would not, and what monitoring signal would have caught the issue earliest.
