---
layout: default
title: "Machine Learning Basics"
parent: "AI Foundations"
nav_order: 1581
permalink: /ai-foundations/machine-learning-basics/
number: "1581"
category: AI Foundations
difficulty: ★☆☆
depends_on: Algorithm, Statistics, Data Structures
used_by: Neural Network, Deep Learning, Supervised vs Unsupervised Learning, Fine-Tuning
related: Deep Learning, Model Parameters, Model Evaluation Metrics
tags:
  - ai
  - foundational
  - mental-model
  - algorithm
---

# 1581 — Machine Learning Basics

⚡ TL;DR — Machine learning teaches computers to improve at tasks by finding patterns in data, rather than following hand-written rules.

| #1581           | Category: AI Foundations                                                        | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Algorithm, Statistics, Data Structures                                          |                 |
| **Used by:**    | Neural Network, Deep Learning, Supervised vs Unsupervised Learning, Fine-Tuning |                 |
| **Related:**    | Deep Learning, Model Parameters, Model Evaluation Metrics                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine building a spam filter using explicit rules. You write: "If subject contains 'FREE MONEY' mark as spam." Spammers adapt immediately — new phrasing, new domains, new tricks. You add more rules. They adapt again. A team of engineers plays whack-a-mole against millions of spammers worldwide, forever.

Scale this to harder problems: detecting tumours in MRI scans, recognising speech, translating between 100 languages. No human can enumerate the rules. The patterns are too subtle, too numerous, and too context-dependent for any rulebook.

**THE BREAKING POINT:**
Rule-based systems require a human to understand the pattern _first_. For high-dimensional, noisy, ever-changing real-world data, that prerequisite cannot be met.

**THE INVENTION MOMENT:**
"This is exactly why Machine Learning was created."

---

### 📘 Textbook Definition

Machine learning is a subfield of artificial intelligence in which systems learn to perform tasks by detecting statistical patterns in training data rather than through explicitly programmed rules. A model is a mathematical function with adjustable parameters tuned during training to minimise prediction error on labelled examples. Once trained, the model generalises the learned mapping to unseen inputs.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Show a computer thousands of examples and it learns the pattern itself.

**One analogy:**

> Teaching a child to recognise dogs. You never write rules like "four legs, fur, barks." You just show them thousands of dogs and non-dogs. After enough examples, they recognise even breeds they've never seen — because they learned the underlying pattern, not a list of facts.

**One insight:**
The power of ML is not the algorithm — it's that _data encodes the rules_. The human's job shifts from writing logic to curating examples. Instead of telling the computer what to do, you show it what success looks like.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Learning requires examples — a model cannot generalise from zero data.
2. The goal is generalisation — memorising training data is failure, not success.
3. All learning is optimisation — parameters are adjusted to minimise prediction error.

**DERIVED DESIGN:**
Given these invariants, three components become mandatory: a _model_ (mathematical structure mapping inputs to outputs), a _loss function_ (scalar measure of prediction error), and an _optimisation algorithm_ (method to reduce loss by adjusting parameters). Training runs optimisation until validation loss stops improving.

**THE TRADE-OFFS:**
**Gain:** Systems can solve problems where explicit rules are impossible to enumerate.
**Cost:** Requires large volumes of clean labelled data; models are opaque; performance is bounded by data quality and distribution coverage.

---

### 🧪 Thought Experiment

**SETUP:**
You have 2,000 labelled photos — 1,000 cats, 1,000 dogs. Build a classifier.

**WHAT HAPPENS WITHOUT MACHINE LEARNING:**
You manually examine photos and write rules: "If pixel region near top is pointed, probably cat." After a week of work: 50 rules, 60% accuracy. New photos break old rules. You iterate for a month: 200 rules, 75% accuracy, rules conflict, every update risks regression.

**WHAT HAPPENS WITH MACHINE LEARNING:**
Feed 2,000 labelled photos to a learning algorithm. One hour of training, millions of parameter adjustments. Test accuracy: 95%. Add 10,000 more photos: 99%. No rules were ever written by a human.

**THE INSIGHT:**
When the pattern is too complex to articulate, letting the data define the rules is not just faster — it is the only approach that scales.

---

### 🧠 Mental Model / Analogy

> A machine learning model is like a student studying with past exam papers. Each paper is a training example. Every wrong answer triggers a correction. After enough papers, the student answers questions they've never seen — not by memorising, but by learning the underlying patterns.

- "Past exam papers" → training dataset
- "Getting an answer wrong" → prediction error (loss)
- "Correcting mistakes" → gradient descent / parameter update
- "Answering new questions" → inference on unseen data
- "Exam score on new paper" → test set accuracy

Where this analogy breaks down: a student understands _why_ they got answers right; an ML model is a black box — high accuracy does not imply understanding or reasoning.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Machine learning is how you teach a computer to get better at something by showing it lots of examples, instead of writing step-by-step instructions for every case.

**Level 2 — How to use it (junior developer):**
Collect labelled training data, choose a model type (decision tree, neural network, etc.), train using a library like scikit-learn or PyTorch, then evaluate on a held-out test set. The critical discipline: never let test data touch training — that would make your accuracy measurement meaningless.

**Level 3 — How it works (mid-level engineer):**
Training adjusts model parameters (weights) using gradient descent to minimise a loss function. Overfitting — the model memorises training examples but fails on new data — is the central challenge. It is controlled via regularisation, dropout, validation-set early stopping, and data augmentation. The train/val/test split is not a formality; it is how you measure generalisation honestly.

**Level 4 — Why it was designed this way (senior/staff):**
The shift from symbolic AI to statistical learning reflected a pragmatic insight: for high-dimensional data, probabilistic approximation beats rule enumeration. The universal approximation theorem guarantees neural networks can represent any function — but says nothing about whether they will _learn_ it from finite data. The bias-variance tradeoff remains the central tension: models complex enough to fit training data overfit; models simple enough to generalise underfit. Modern deep learning sidesteps classical theory by using scale (data + parameters + compute) as the lever.

---

### ⚙️ How It Works (Mechanism)

The ML training loop repeats thousands of times:

```
┌─────────────────────────────────────────────┐
│           ML TRAINING LOOP                  │
│                                             │
│  1. FORWARD PASS                            │
│     Input batch → Model → Predictions       │
│                                             │
│  2. COMPUTE LOSS                            │
│     Compare predictions to true labels      │
│     Loss = scalar measure of wrongness      │
│                                             │
│  3. BACKWARD PASS (Backpropagation)         │
│     Compute gradient of loss w.r.t.         │
│     every model parameter                   │
│                                             │
│  4. UPDATE PARAMETERS                       │
│     params = params - lr * gradient         │
│     (gradient descent step)                 │
│                                             │
│  Repeat until val loss stops improving      │
└─────────────────────────────────────────────┘
```

Why each step exists:

- Forward pass: need a prediction to measure error.
- Loss: need a scalar to optimise (direction + magnitude).
- Backward pass: calculates each parameter's contribution to the error.
- Update: the actual learning — small parameter shifts toward lower loss.

At inference time, only the forward pass runs. Parameters are frozen.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Raw Data → Cleaning → Feature Engineering → Train/Test Split
  → Model Training ← YOU ARE HERE
  → Evaluation → Deployment → Inference → Monitoring
```

**FAILURE PATH:**
Model training diverges → check learning rate (too high) or data normalisation.
Production accuracy degrades → data drift: retrain on recent data.

**WHAT CHANGES AT SCALE:**
At 10x data, training time grows super-linearly without batching strategies. At 100x, single-machine training becomes infeasible — distributed training across GPU clusters is required. At 1000x, feature stores, data pipelines, and model registries become first-class infrastructure.

---

### 💻 Code Example

**Example 1 — Basic ML pipeline with proper train/test split:**

```python
# BAD: train on all data — no way to measure generalisation
from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier()
model.fit(X, y)  # will appear perfect, lies in production

# GOOD: proper split + evaluation
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = DecisionTreeClassifier(max_depth=5)  # regularise
model.fit(X_train, y_train)
preds = model.predict(X_test)
print(accuracy_score(y_test, preds))  # honest measurement
```

**Example 2 — Detecting overfitting with learning curves:**

```python
from sklearn.model_selection import learning_curve
import numpy as np

train_sizes, train_scores, val_scores = learning_curve(
    model, X, y,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5
)
# If val_scores plateau but train_scores keep rising: overfitting
# If both plateau low: underfitting (increase model complexity)
print("Val scores:", val_scores.mean(axis=1))
```

---

### ⚖️ Comparison Table

| Approach             | Needs Labels | Interpretable | Complexity Ceiling | Best For                        |
| -------------------- | ------------ | ------------- | ------------------ | ------------------------------- |
| **Machine Learning** | Yes          | Partial       | High               | General pattern recognition     |
| Rule-Based Systems   | No           | Full          | Low                | Stable, well-defined domains    |
| Statistical Models   | Yes          | Full          | Medium             | Linear relationships, inference |
| Deep Learning        | Yes (large)  | No            | Very High          | Images, language, audio         |

How to choose: use rule-based when rules are few and stable; use ML when patterns are complex and data is plentiful; use deep learning when data is massive and patterns are unstructured.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| More data always improves a model                 | More _representative_ data helps; biased or mislabelled data hurts proportionally                      |
| ML models understand concepts                     | Models are statistical pattern matchers with no understanding or intent                                |
| Training accuracy predicts production performance | Only test-set accuracy (on held-out data) predicts production; training accuracy is meaningless alone  |
| ML is always better than rules                    | For narrow, stable, well-defined problems, rule-based systems are faster, cheaper, and more debuggable |

---

### 🚨 Failure Modes & Diagnosis

**1. Data Leakage**

**Symptom:** Test accuracy is suspiciously high (95%+); production accuracy collapses immediately.

**Root Cause:** Information from the test set influenced training — e.g., normalisation computed across the full dataset before splitting.

**Diagnostic:**

```bash
# Check pipeline order — ensure fit() never sees test data
python -c "
from sklearn.pipeline import Pipeline
# Correct: pipeline fits scaler only on training fold
print('Pipeline ensures no leakage if used correctly')
"
```

**Fix:**

```python
# BAD: scaler sees all data including test
scaler = StandardScaler().fit(X)
X_scaled = scaler.transform(X)

# GOOD: scaler sees only training data
from sklearn.pipeline import Pipeline
pipe = Pipeline([('scaler', StandardScaler()),
                 ('model', LogisticRegression())])
pipe.fit(X_train, y_train)  # scaler only fits on X_train
```

**Prevention:** Always use `sklearn.pipeline.Pipeline` so transformers are fit only on training folds.

**2. Distribution Shift (Data Drift)**

**Symptom:** Model accuracy degrades progressively in production with no code changes.

**Root Cause:** Production input distribution has diverged from training distribution. Parameters remain fixed while the world has changed.

**Diagnostic:**

```bash
pip install evidently
python -c "
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=train_df, current_data=prod_df)
report.save_html('drift.html')
"
```

**Fix:** Retrain on recent data; implement continuous training pipelines.

**Prevention:** Set up automated drift detection in production monitoring with retraining triggers.

**3. Overfitting**

**Symptom:** Training accuracy 99%, validation accuracy 70% — large gap, performance gets worse with more epochs.

**Root Cause:** Model memorised training examples. Capacity is too high relative to dataset size.

**Diagnostic:**

```bash
python -c "
# Plot train vs val loss per epoch — diverging curves = overfitting
import matplotlib.pyplot as plt
plt.plot(train_loss, label='train')
plt.plot(val_loss, label='val')
plt.legend(); plt.savefig('overfitting.png')
"
```

**Fix:** Reduce model complexity, add L2 regularisation, use dropout, increase training data size.

**Prevention:** Always track train vs validation loss during training; stop when validation loss starts rising.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Algorithm` — ML training is an iterative optimisation algorithm; understanding loops and convergence is essential
- `Statistics` — probability, distributions, and expected value underpin every ML model's mathematics

**Builds On This (learn these next):**

- `Neural Network` — the dominant model architecture; applies ML principles at scale
- `Supervised vs Unsupervised Learning` — the fundamental split in how ML problems are framed
- `Model Evaluation Metrics` — how to measure whether a trained model is actually useful

**Alternatives / Comparisons:**

- `Deep Learning` — a more powerful subset of ML using multi-layer networks; requires far more data and compute
- `Rule-Based Systems` — the pre-ML approach; fully interpretable but brittle for complex domains

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Learn patterns from data, not rules       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Rules can't scale to complex, changing    │
│ SOLVES       │ real-world patterns                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Data encodes the rules; humans curate     │
│              │ examples, not logic                       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Pattern too complex for explicit rules;   │
│              │ labelled data is available                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Rules are few and stable; data is scarce  │
│              │ or heavily mislabelled                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Automation + scale vs interpretability    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Show, don't tell — the data writes       │
│              │  the rules."                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Neural Network → Deep Learning →          │
│              │ Transformer Architecture                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two spam filter teams: Team A spent 2 years hand-crafting 500 expert rules (94% accuracy); Team B trained an ML model on 1 million labelled emails (96% accuracy). A brand-new spam campaign launches using entirely novel phrasing not seen in any training data. Which team's system adapts faster, why, and what does this reveal about the fundamental limitation of each approach at scale?

**Q2.** Your ML model achieves 99% test accuracy and 99% production accuracy for 6 months. In month 7, production accuracy drops to 71% with no code changes, no new deployments, and no infrastructure changes. List the three hypotheses you would investigate first, the diagnostic command for each, and explain which is most likely given only the date changed.
