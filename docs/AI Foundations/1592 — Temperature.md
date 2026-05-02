---
layout: default
title: "Temperature"
parent: "AI Foundations"
nav_order: 1592
permalink: /ai-foundations/temperature/
number: "1592"
category: AI Foundations
difficulty: ★★☆
depends_on: Token, Inference, Model Parameters
used_by: Top-p / Top-k Sampling, Fine-Tuning, Hallucination
related: Top-p / Top-k Sampling, Grounding, Model Weights
tags:
  - ai
  - llm
  - intermediate
  - mental-model
  - tradeoff
---

# 1592 — Temperature

⚡ TL;DR — Temperature controls how random an LLM's output is — low values produce focused, predictable text; high values produce creative, varied, and sometimes incoherent text.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A language model always picks the single most probable next token — like an autocomplete that always completes "The capital of France is…" with "Paris" and never generates anything unexpected. For factual Q&A, that is fine. But ask it to write a poem or brainstorm product names, and it produces the same output every time, drawn from the most statistically common phrasing in training data. Every poem sounds like Wikipedia. Every brainstorm generates "Product Name Pro."

**THE BREAKING POINT:**
Without controllable randomness, creative tasks are useless (always outputs the same thing) and temperature-sensitive tasks like code generation and legal summarisation have no way to trade off determinism vs. exploration. Engineers had no knob to say: "be precise for this task, be creative for that one."

**THE INVENTION MOMENT:**
This is exactly why Temperature was introduced — as a scalar parameter that reshapes the probability distribution over the vocabulary before sampling, giving engineers direct control over the creativity-accuracy trade-off.

---

### 📘 Textbook Definition

**Temperature** is a scalar hyperparameter applied to the logits (raw output scores) of a language model's final layer before the softmax function converts them to a probability distribution. Dividing logits by temperature T reshapes the distribution: T < 1 sharpens it (concentrating probability on the top token), T > 1 flattens it (spreading probability more evenly across tokens), and T = 0 collapses to greedy (always pick the argmax). The sampled next token is drawn from this reshaped distribution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Temperature is the creativity dial — turn it down for precision, up for variety.

**One analogy:**
> Imagine choosing a restaurant from a list ranked by review score. At temperature 0, you always go to #1. At temperature 0.7, you usually go to the top 3 but occasionally try #7. At temperature 2, you spin a wheel and end up at a random place including ones you would never normally consider.

**One insight:**
Temperature does not make the model "smarter" — it only changes how it samples from what it already knows. A model with wrong beliefs will express them more confidently at T=0 and more randomly at T=2. Temperature controls variance, not correctness.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. After the final transformer layer, the model outputs one logit per vocabulary token (e.g., 50,257 logits for GPT-2).
2. Softmax converts logits to a probability distribution that sums to 1.0.
3. The next token is sampled from this distribution.

**DERIVED DESIGN:**
Temperature modifies step 2: divide every logit by T before softmax.

```
p(token_i) = exp(logit_i / T) / Σ exp(logit_j / T)
```

When T → 0: the highest logit dominates exponentially → effectively argmax.
When T = 1: standard softmax, model's native distribution.
When T > 1: all logits become more similar after division → flatter distribution → more uniform sampling.

This is borrowed directly from thermodynamics: in statistical mechanics, temperature governs how energy is distributed across states. High temperature = more states accessible. Same principle applies here.

**THE TRADE-OFFS:**
**Gain at T < 1:** Deterministic, factually consistent, less hallucination for well-trained facts.
**Cost at T < 1:** Repetitive, low-diversity output; can reinforce training biases.
**Gain at T > 1:** Diverse, novel, creative output.
**Cost at T > 1:** Incoherent, factually unreliable, grammatically unstable.

Could we do this differently? Yes — top-p and top-k sampling are complementary strategies that constrain which tokens are even in the pool before temperature is applied.

---

### 🧪 Thought Experiment

**SETUP:**
You ask an LLM: "Name a colour." The model's logit scores, after training, are: "red" = 3.2, "blue" = 3.1, "green" = 2.8, "chartreuse" = 0.4.

**WHAT HAPPENS WITHOUT TEMPERATURE (T=0 / greedy):**
After softmax, "red" has probability ~0.52, "blue" ~0.47, "green" ~0.01. The model always outputs "red." Ask 100 times: 100× "red."

**WHAT HAPPENS WITH TEMPERATURE (T=1.5):**
Dividing all logits by 1.5: 3.2/1.5=2.13, 3.1/1.5=2.07, 2.8/1.5=1.87, 0.4/1.5=0.27. The distribution flattens: "red" ≈ 31%, "blue" ≈ 29%, "green" ≈ 24%, "chartreuse" ≈ 7%. Ask 100 times: varied answers including occasional "chartreuse." Brainorm is richer.

**THE INSIGHT:**
Temperature controls the shape of the probability distribution, not the model's knowledge. It shifts the output from "most probable" to "diverse sample from the distribution." The right temperature depends entirely on whether you need a single correct answer or a diverse set of plausible answers.

---

### 🧠 Mental Model / Analogy

> Imagine a symphony orchestra where each musician has a score (the logits) showing how loudly to play their note. At temperature 0, only the loudest note plays; all others are silent. At temperature 1, the orchestra plays as written. At temperature 2, every instrument plays at nearly equal volume — rich, chaotic sound where the melody is buried in noise.

Mapping:
- "Orchestra score" → logit values
- "Note volume" → logit magnitude (higher = more probable)
- "Temperature 0" → only the single best token is selected
- "Temperature 1" → model's native distribution
- "Temperature 2" → nearly uniform sampling, noise dominates
- "Melody" → coherent meaning in generated text

Where this analogy breaks down: in a real orchestra, louder notes are not necessarily "correct" — but in an LLM, higher logits reflect the model's learned belief about probability given training data.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Temperature is a knob from "always pick the obvious answer" to "pick something surprising." Low temperature = predictable; high temperature = creative but unreliable.

**Level 2 — How to use it (junior developer):**
Set temperature based on your task: T=0 for factual extraction, code generation, or structured output. T=0.3–0.7 for most conversational tasks. T=0.7–1.2 for creative writing, brainstorming, and diversity generation. Most production LLM APIs accept `temperature` as a float in [0, 2]. Test your specific task empirically — these are heuristics, not laws.

**Level 3 — How it works (mid-level engineer):**
Temperature is applied as a division of logits before softmax. This changes the effective "sharpness" of the distribution. Combined with top-p and top-k, it defines the full sampling strategy. Note: at T=0, many APIs collapse to a deterministic argmax. At T>0, even identical prompts produce varied outputs — important for reproducibility in testing. Use `seed` parameter (if available) plus T=0 for deterministic unit tests.

**Level 4 — Why it was designed this way (senior/staff):**
The choice to implement temperature as logit scaling (rather than post-hoc distribution modification) ensures the operation remains differentiable and does not change the model's internal belief structure — only the sampling strategy. This matters because temperature is applied at inference time; it does not affect the gradient flow during training. In production, the right temperature is often task-specific and should be treated as a hyperparameter tuned against human evaluation data (not just perplexity). Some systems use adaptive temperature — lower temperature for high-stakes token slots (e.g., numerical outputs) and higher for stylistic tokens.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ Final transformer layer output              │
│ Logits: [3.2, 3.1, 2.8, 0.4, ...]          │
└────────────────────┬────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ Divide by temperature T                     │
│ T=0.5: [6.4, 6.2, 5.6, 0.8, ...]           │
│ T=1.0: [3.2, 3.1, 2.8, 0.4, ...]           │
│ T=2.0: [1.6, 1.55, 1.4, 0.2, ...]          │
└────────────────────┬────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ Softmax → probability distribution          │
│ T=0.5: [0.55, 0.43, 0.02, ≈0, ...]         │
│ T=1.0: [0.35, 0.33, 0.28, 0.04, ...]       │
│ T=2.0: [0.29, 0.28, 0.25, 0.18, ...]       │
└────────────────────┬────────────────────────┘
                     ↓
        Sample next token from distribution
```

**Happy path:** Temperature set appropriately → output quality matches task requirements.
**Error path:** Temperature too high → model outputs grammatically broken or semantically incoherent tokens. Temperature too low on a creative task → every user gets the same response, defeating the purpose.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Prompt tokens input to transformer
    ↓
Transformer forward pass (all layers)
    ↓
Final layer outputs raw logits (one per vocab token)
    ↓
[TEMPERATURE APPLIED ← YOU ARE HERE]
  logits = logits / temperature
    ↓
Optional: top-k / top-p filtering
    ↓
Softmax → probability distribution
    ↓
Sample next token
    ↓
Append to context; repeat until stop token
```

**FAILURE PATH:**
```
Temperature = 0 on creative brainstorm task
    ↓
Every API call returns identical output
    ↓
User reports "AI is boring / always says the same thing"
    ↓
Increase temperature to 0.7–1.0
```

**WHAT CHANGES AT SCALE:**
High temperature increases output variance — at scale, a T=1.5 response generates more unique tokens per request, increasing both compute time and token cost. For multi-user applications, temperature is often user-configurable (e.g., "Creative mode" toggles T=0.9, "Precise mode" uses T=0.1).

---

### 💻 Code Example

**Example 1 — Temperature comparison (OpenAI):**
```python
import openai

def generate(prompt: str, temperature: float) -> str:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=50
    )
    return response.choices[0].message.content

prompt = "Give me a creative name for a productivity app."

# T=0: always the same, most common answer
print(generate(prompt, temperature=0.0))
# → "TaskMaster Pro"

# T=1.0: varied, sometimes unexpected
for _ in range(3):
    print(generate(prompt, temperature=1.0))
# → "FocusForge", "MomentumHub", "ClearPath"

# T=2.0: high variance, often incoherent
print(generate(prompt, temperature=2.0))
# → "XenithFlowDash!!" (may be nonsensical)
```

**Example 2 — Deterministic testing with T=0:**
```python
def test_json_extraction():
    """Use T=0 for deterministic, testable outputs."""
    result = generate(
        prompt='Extract name from: "Hi, I am Alice." '
               'Respond with JSON: {"name": "..."}',
        temperature=0.0  # deterministic for unit tests
    )
    assert result == '{"name": "Alice"}'
```

**Example 3 — Task-appropriate temperature routing:**
```python
TASK_TEMPERATURES = {
    "code_generation": 0.0,
    "factual_qa": 0.1,
    "summarisation": 0.3,
    "conversational": 0.7,
    "creative_writing": 1.0,
    "brainstorming": 1.2,
}

def smart_generate(prompt: str, task: str) -> str:
    temperature = TASK_TEMPERATURES.get(task, 0.7)
    return generate(prompt, temperature)
```

---

### ⚖️ Comparison Table

| Sampling Strategy | Randomness | Coherence | Best For |
|---|---|---|---|
| **Temperature (T<1)** | Low | High | Factual tasks, code, structured output |
| Temperature (T=1) | Native | Native | General-purpose default |
| Temperature (T>1) | High | Low | Brainstorming, diversity testing |
| Top-k sampling | Medium | Medium | Limiting to top K tokens |
| Top-p (nucleus) | Adaptive | High | Creative tasks with coherence |
| Beam search | None | Highest | Translation, structured generation |

**How to choose:** For most production tasks, start at T=0.7 with top-p=0.9. Use T=0 for deterministic, testable outputs. Combine temperature with top-p for creative tasks that still need grammatical coherence.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Higher temperature makes the model smarter" | Temperature only changes sampling strategy; it cannot add knowledge the model doesn't have |
| "Temperature 0 is always best for accuracy" | T=0 can over-confidently output wrong answers; slight temperature with top-p often gives better calibrated responses |
| "Temperature affects the model's weights" | Temperature is applied only at inference time (logit scaling); it does not modify model parameters |
| "Temperature controls response length" | Length is controlled by `max_tokens` and stop sequences; temperature only affects token selection probabilities |
| "The same temperature works for all models" | Different models have different logit scales; T=0.7 on GPT-4 ≠ T=0.7 on Llama-3 |

---

### 🚨 Failure Modes & Diagnosis

**Degenerate Repetition (T too low)**

**Symptom:** Model repeats the same phrase or sentence in a loop; output gets stuck after a few sentences.

**Root Cause:** At very low temperatures, the model becomes trapped in local probability maxima — once it generates a pattern that scores high, it keeps selecting tokens that continue that pattern.

**Diagnostic Command / Tool:**
```python
# Check for repeated n-grams in output
from collections import Counter

def repetition_score(text: str, n: int = 4) -> float:
    words = text.split()
    ngrams = [tuple(words[i:i+n]) for i in range(len(words)-n)]
    if not ngrams:
        return 0.0
    counts = Counter(ngrams)
    return max(counts.values()) / len(ngrams)

score = repetition_score(output)
if score > 0.3:
    print("Warning: high repetition. Increase temperature.")
```

**Fix:** Increase temperature to 0.5+; add `frequency_penalty` or `presence_penalty` parameters.

**Prevention:** Use `repetition_penalty` (Hugging Face) or `frequency_penalty` (OpenAI) alongside low temperature.

---

**Incoherent Output (T too high)**

**Symptom:** Generated text is grammatically broken, mixes topics randomly, or is factually nonsensical.

**Root Cause:** High temperature flattens the probability distribution so heavily that low-probability (semantically unrelated) tokens are frequently selected.

**Diagnostic Command / Tool:**
```python
# Perplexity check using model's own scoring
import torch

def compute_perplexity(model, tokenizer, text: str) -> float:
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
    return torch.exp(outputs.loss).item()
```

**Fix:** Reduce temperature; add top-p=0.9 to cap the sampling pool.

**Prevention:** Never exceed T=1.5 for tasks requiring coherent text; use top-p as a ceiling.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Token` — temperature operates on per-token probability distributions
- `Inference` — temperature is an inference-time parameter, not a training parameter
- `Model Parameters` — temperature is a sampling hyperparameter, distinct from model weights

**Builds On This (learn these next):**
- `Top-p / Top-k Sampling` — complementary sampling strategies applied in conjunction with temperature
- `Hallucination` — high temperature increases hallucination risk by sampling low-probability tokens
- `Fine-Tuning` — an alternative to high temperature for domain-specific generation

**Alternatives / Comparisons:**
- `Grounding` — reduces hallucination regardless of temperature by anchoring outputs to retrieved facts
- `Model Weights` — the underlying distribution temperature reshapes; changing weights changes the base distribution
- `Beam Search` — deterministic alternative to sampling; ignores temperature entirely

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Scalar that reshapes token probability    │
│              │ distribution before sampling              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Need control over randomness vs precision │
│ SOLVES       │ across different task types               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Does NOT change what model knows —        │
│              │ only changes how it samples               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ T=0 for deterministic/testable output;    │
│              │ T=0.7 for balanced; T=1+ for creative     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never exceed T=1.5 for tasks requiring    │
│              │ factual accuracy or grammatical coherence │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Creativity and diversity vs factual       │
│              │ accuracy and determinism                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The creativity dial: turns the oracle    │
│              │ into a poet — at the cost of precision."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Top-p Sampling → Hallucination → Grounding│
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are building a medical symptom checker. A physician wants the model to suggest possible diagnoses from a list of symptoms. A junior engineer sets temperature=1.2 to "make the output more varied and helpful." Trace what happens: what types of tokens does the model now have an elevated probability of selecting, and why does this create a patient-safety risk that a lower temperature would not?

**Q2.** Both temperature scaling and top-p sampling affect the token probability distribution. What is the precise condition where they produce identical output distributions — and what is the condition where they diverge most? What does this tell you about when to use each, and why using both together is typically superior to either alone?
