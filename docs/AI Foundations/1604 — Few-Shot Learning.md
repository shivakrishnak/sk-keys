---
layout: default
title: "Few-Shot Learning"
parent: "AI Foundations"
nav_order: 1604
permalink: /ai-foundations/few-shot-learning/
number: "1604"
category: AI Foundations
difficulty: ★★★
depends_on: In-Context Learning, Transfer Learning, Pre-training
used_by: Fine-Tuning, Benchmark (AI), Model Evaluation Metrics
related: Zero-Shot Learning, In-Context Learning, Transfer Learning
tags:
  - ai
  - llm
  - advanced
  - mental-model
  - intermediate
---

# 1604 — Few-Shot Learning

⚡ TL;DR — Few-shot learning is the ability to generalise from only a handful of examples, achieved in LLMs by providing worked examples directly in the prompt rather than retraining the model.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to extract structured data from legal contracts: party names, dates, obligations. A traditional ML approach requires: 500+ labelled examples per field, weeks of annotation, model training, deployment. For a legal startup, labelling 500 contracts costs $20,000 and six weeks. By then, the contract structure has changed and you start over.

**THE BREAKING POINT:**
Annotation-heavy machine learning doesn't work for tasks where labelled data is rare, expensive, or time-sensitive. The labelling bottleneck prevents ML from being economically viable for countless real-world applications.

**THE INVENTION MOMENT:**
This is exactly why Few-Shot Learning was identified as a key capability — the ability to generalise from 1–10 examples rather than thousands, enabling rapid deployment of new capabilities without expensive labelling pipelines.

---

### 📘 Textbook Definition

**Few-shot learning** is a learning paradigm in which a model generalises to new tasks from a very small number of labelled examples (typically 1–10). For LLMs, in-context few-shot learning (Brown et al., 2020, GPT-3) is the dominant approach: examples are provided directly in the input prompt (as input/output demonstrations) without updating model weights. Traditional few-shot learning methods (Siamese networks, prototypical networks, MAML) instead update a meta-learner to rapidly adapt to new tasks from few examples.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Few-shot learning means giving the AI 2–3 examples of what you want and having it generalise immediately — no retraining.

**One analogy:**

> Think of how a child learns to recognise a new animal. Show them one picture of a pangolin and say "that's a pangolin." Show them one more from a different angle. The child can now identify pangolins in new photos. A doctor doesn't need to see 10,000 pangolins to learn what one looks like — a few examples plus prior knowledge about animals is enough. Few-shot learning in LLMs works the same way: prior knowledge from pre-training + a few examples in the prompt = new capability.

**One insight:**
In-context few-shot learning does NOT update model weights. The model learns "in context" — it infers the task from the examples in the prompt and applies that pattern to the new input. This happens entirely through the attention mechanism over the examples in the context window.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A model pretrained on vast data develops rich general representations.
2. A few examples specify a task FORMAT and INPUT-OUTPUT PATTERN without specifying underlying knowledge.
3. Attention over in-context examples allows the model to "recognise" the task pattern and apply its pretrained knowledge to new inputs.

**DERIVED DESIGN:**
Few-shot prompt structure:

```
[Task description (optional)]
Example 1: Input → Output
Example 2: Input → Output
Example 3: Input → Output
New input: [query] → ???
```

The model attends over all three examples plus the new input. The attention pattern extracts: the structural relationship between inputs and outputs, the format of the expected output, the type of transformation being performed. The model then generates a completion that follows the extracted pattern.

Why does this work? The model has seen millions of similar "input → output" structures during pre-training (Q&A pairs, translation pairs, code comments paired with code). Few-shot examples activate these learned structural patterns.

**THE TRADE-OFFS:**
**Gain:** No labelling pipeline needed; zero training cost; new tasks deployable in minutes.
**Cost:** Performance is lower than fine-tuning (examples consume context window; model doesn't update); sensitive to example selection, ordering, and formatting; performance degrades rapidly if examples are misleading or inconsistent.

---

### 🧪 Thought Experiment

**SETUP:**
Task: classify customer support emails as "billing," "technical," or "product" issues. Two approaches: Approach A = zero examples (zero-shot). Approach B = three examples (few-shot). Same prompt question: "Classify this email: 'I can't log in and I've tried resetting my password three times.'"

**WHAT HAPPENS WITH ZERO-SHOT:**
Model uses only its pretrained knowledge of what "billing," "technical," and "product" mean. Output: "technical" (correct). But for edge cases — "I was charged twice but also the app is slow" — the model guesses based on pretraining, producing inconsistent results on ambiguous cases.

**WHAT HAPPENS WITH FEW-SHOT (3 examples):**
The three examples show: billing issues = payment/refund language, technical = login/app/error, product = feature questions. The model now has your specific labelling conventions. The ambiguous "charged twice + slow app" example → model applies your convention: "billing" (billing comes first in your examples). Consistency improves from 78% to 94% on ambiguous cases.

**THE INSIGHT:**
Few-shot examples don't teach the model what billing vs. technical means — it already knows. They teach the model YOUR labelling conventions and edge case handling. The model infers your decision rules from 3 examples and applies them consistently.

---

### 🧠 Mental Model / Analogy

> Few-shot learning is like showing a new contractor your code style guide by example rather than writing one. You say: "Here's how we name functions: calculateTotalPrice, validateUserInput, fetchOrderDetails." The contractor infers your naming convention (camelCase, verb + noun, descriptive) and applies it consistently without you specifying every rule. The examples carry your implicit conventions.

Mapping:

- "New contractor" → LLM at inference time
- "Code style guide examples" → few-shot demonstrations
- "Infers naming convention" → model extracts task pattern
- "Applies consistently" → generalises to new inputs
- "Your implicit conventions" → task-specific patterns not in pretraining

Where this analogy breaks down: a contractor can ask clarifying questions; an LLM cannot — ambiguous examples get statistically averaged rather than clarified.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
You give the AI 2–3 examples of what you want, and it figures out the pattern and applies it to new inputs — without any training or coding.

**Level 2 — How to use it (junior developer):**
Structure: always include a task description, 2–5 input/output examples, then the new input. Make examples diverse (cover edge cases), consistent (same format), and representative (not cherry-picked). Avoid contradictory examples — the model averages confusing patterns. Test with different example sets — performance variance is often surprising.

**Level 3 — How it works (mid-level engineer):**
During the forward pass, the model's attention layers attend over all few-shot examples when computing the output for the new input. The examples function as an "implicit fine-tuning signal" — they shift the model's output distribution towards the demonstrated pattern. Experiments (Min et al., 2022) showed that in-context examples matter primarily for format, not label-input mapping — the model largely ignores whether example labels are correct and instead uses the structural pattern. This finding has profound implications: few-shot learning is primarily about format specification, not knowledge transfer.

**Level 4 — Why it was designed this way (senior/staff):**
The discovery of in-context few-shot learning in GPT-3 was unexpected — it emerged from scale, not explicit design. Smaller models (1B parameters) show weak few-shot ability; larger models (100B+) show dramatically better few-shot performance. This suggests few-shot learning is an emergent capability of sufficient model scale — the model has "meta-learned" to learn from examples during pre-training by exposure to millions of structured documents. The mechanism is still not fully understood. The "majority label bias" (model performs poorly when few-shot examples are disproportionately one class) is a known failure mode that limits reliability in imbalanced tasks.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ PROMPT STRUCTURE (few-shot)                 │
│                                             │
│ [System]: Classify customer emails         │
│                                             │
│ Email: "Charged twice for subscription"    │
│ Category: billing                           │
│                                             │
│ Email: "App crashes on startup"             │
│ Category: technical                         │
│                                             │
│ Email: "When will feature X be added?"     │
│ Category: product                           │
│                                             │
│ Email: "Password reset not working"        │
│ Category: ???                               │
└──────────────┬──────────────────────────────┘
               ↓ Transformer attention
┌─────────────────────────────────────────────┐
│ Model attends over all 3 examples           │
│ Extracts: format (Email: → Category:)      │
│ Extracts: label space {billing, technical, │
│          product}                          │
│ Extracts: billing = payment/subscription   │
│           technical = app/crash/login      │
│           product = features               │
│                                             │
│ New input "Password reset" → pattern match │
│ → technical                                │
└─────────────────────────────────────────────┘
```

**Performance by shot count (typical):**

```
0-shot:  ~65% accuracy (no examples)
1-shot:  ~72% accuracy
3-shot:  ~82% accuracy
5-shot:  ~87% accuracy
10-shot: ~89% accuracy
fine-tune on 1000: ~95% accuracy
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Task identified
    ↓
Select 3–5 representative examples
(cover edge cases, diverse inputs)
    ↓
Format as prompt with input/output pairs
    ↓
[FEW-SHOT INFERENCE ← YOU ARE HERE]
Prompt → LLM → output for new input
    ↓
Evaluate on held-out examples
    ↓
Iterate: add/remove/change examples
based on failure analysis
    ↓
Deploy (if quality sufficient)
OR escalate to fine-tuning (if not)
```

**FAILURE PATH:**

```
Few-shot examples are misleading or
have conflicting labelling conventions
    ↓
Model averages conflicting patterns
    ↓
Low accuracy; inconsistent outputs
    ↓
Debug: check for contradictions in examples
         ensure format is perfectly consistent
         try different example sets
```

**WHAT CHANGES AT SCALE:**
At high API call volume, few-shot prompts are longer → more tokens → higher cost. At 5 examples × 100 tokens each = 500 extra tokens per request. At $0.01/1K tokens × 1M requests/day = $5,000/day extra cost. This makes fine-tuning economically attractive at scale: pay once for fine-tuning, use shorter prompts forever.

---

### 💻 Code Example

**Example 1 — Basic few-shot prompt:**

```python
import openai

def few_shot_classify(email: str, client) -> str:
    examples = [
        ("My invoice shows a double charge",
         "billing"),
        ("The mobile app freezes when I open settings",
         "technical"),
        ("Will you add dark mode in the next update?",
         "product"),
        ("Can't reset my 2FA authenticator",
         "technical"),
    ]

    # Build few-shot prompt
    example_text = "\n".join(
        f"Email: {e}\nCategory: {label}"
        for e, label in examples
    )

    prompt = (f"{example_text}\n\n"
              f"Email: {email}\nCategory:")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # deterministic for classification
        max_tokens=10
    )
    return response.choices[0].message.content.strip()
```

**Example 2 — Few-shot with chain-of-thought:**

```python
# Chain-of-thought few-shot — better for reasoning tasks
cot_examples = [
    {
        "question": "If a train travels 120 km in 2 hours, "
                    "what is its average speed?",
        "reasoning": "Speed = Distance / Time = "
                     "120 km / 2 hours = 60 km/h",
        "answer": "60 km/h"
    },
    {
        "question": "A shop has 45 apples. "
                    "It sells 17 and receives 30 more. "
                    "How many apples does it have?",
        "reasoning": "Start: 45. Sold: 45-17=28. "
                     "Received: 28+30=58.",
        "answer": "58 apples"
    }
]

def cot_answer(question: str, client) -> str:
    shots = "\n\n".join(
        f"Q: {e['question']}\n"
        f"Reasoning: {e['reasoning']}\n"
        f"A: {e['answer']}"
        for e in cot_examples
    )
    prompt = f"{shots}\n\nQ: {question}\nReasoning:"
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    ).choices[0].message.content
```

---

### ⚖️ Comparison Table

| Approach                    | Examples Needed | Training   | Accuracy    | Best For             |
| --------------------------- | --------------- | ---------- | ----------- | -------------------- |
| Zero-shot                   | 0               | 0          | Variable    | Widely-known tasks   |
| **1-shot**                  | 1               | 0          | Medium      | Format specification |
| **Few-shot (3–10)**         | 3–10            | 0          | Medium-high | Quick deployment     |
| Fine-tuning (SFT)           | 1K–100K         | Hours–days | High        | Production quality   |
| Few-shot + chain-of-thought | 3–5             | 0          | High        | Reasoning tasks      |

**How to choose:** Use few-shot for rapid prototyping and low-volume tasks. Use fine-tuning when volume justifies cost (> 100K daily requests) or accuracy is insufficient. Chain-of-thought few-shot dramatically improves performance on multi-step reasoning tasks at no extra training cost.

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                            |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| "Few-shot learning updates the model weights" | In-context few-shot does NOT update weights — the model infers the pattern at inference time without training                      |
| "More examples always helps"                  | Performance often plateaus at 5–10 examples; more examples consume context window without proportional benefit                     |
| "Example labels must be correct"              | Research shows models primarily learn FORMAT from examples, not label-input mapping — labels have less influence than you'd expect |
| "Few-shot is always worse than fine-tuning"   | For tasks the model already knows well, few-shot can match fine-tuning; for novel formats and strict consistency, fine-tuning wins |
| "Example order doesn't matter"                | Example order significantly affects performance — more recent examples are weighted more heavily; put hardest cases last           |

---

### 🚨 Failure Modes & Diagnosis

**Majority Label Bias**

**Symptom:** Classifier skews heavily toward one class even for clear examples of other classes; accuracy on minority classes near zero.

**Root Cause:** Few-shot examples are imbalanced — 3 billing examples and 1 technical example → model learns "billing" as the default prediction.

**Diagnostic Command / Tool:**

```python
# Check label distribution in few-shot examples
from collections import Counter

def check_example_balance(examples: list[tuple]) -> dict:
    labels = [label for _, label in examples]
    distribution = Counter(labels)
    print(f"Label distribution: {dict(distribution)}")
    if max(distribution.values()) > 2 * min(
        distribution.values()
    ):
        print("WARNING: Imbalanced few-shot examples")
    return distribution
```

**Fix:** Balance examples across classes; add more examples for underrepresented classes; use "calibration" by testing on each class separately.

**Prevention:** Always check label balance before deploying few-shot prompts; aim for equal representation.

---

**Format Inconsistency**

**Symptom:** Model sometimes produces output in the expected format, sometimes doesn't — inconsistent punctuation, extra text, missing fields.

**Root Cause:** Few-shot examples have minor format inconsistencies (trailing punctuation differs, capitalisation varies) that confuse the model's format extraction.

**Diagnostic Command / Tool:**

```python
# Validate output format consistency
import re

def validate_output_format(output: str,
                            expected_pattern: str) -> bool:
    """Check if output matches expected regex pattern."""
    match = re.fullmatch(expected_pattern, output.strip())
    if not match:
        print(f"Format mismatch: '{output}'")
    return bool(match)
```

**Fix:** Make all few-shot examples EXACTLY consistent in format, spacing, and punctuation. A single trailing space in one example can cause inconsistency.

**Prevention:** Copy-paste and validate all examples — never type them differently.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `In-Context Learning` — few-shot learning in LLMs is a form of in-context learning
- `Transfer Learning` — few-shot works because of pretrained general representations
- `Pre-training` — scale of pre-training determines the quality of few-shot performance

**Builds On This (learn these next):**

- `Fine-Tuning` — the next step when few-shot accuracy is insufficient
- `Benchmark (AI)` — few-shot benchmarks (FLAN, BIG-Bench) measure model capability
- `Model Evaluation Metrics` — evaluating few-shot generalisation requires specific metrics

**Alternatives / Comparisons:**

- `Zero-Shot Learning` — no examples at all; fewer constraints; lower accuracy
- `In-Context Learning` — the mechanism by which few-shot works in LLMs
- `Transfer Learning` — few-shot is a lightweight form of transfer learning at inference time

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Generalising to new tasks from 1–10       │
│              │ examples in the prompt — no retraining    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Labelled data is expensive; most tasks    │
│ SOLVES       │ can't justify hundreds of examples to     │
│              │ get started                               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Examples specify FORMAT and CONVENTION,   │
│              │ not underlying knowledge — model already  │
│              │ has the knowledge; examples tell it how   │
│              │ to express it for your task               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Rapid prototyping; new tasks; low volume; │
│              │ no labelled dataset available             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-volume production (cost); tasks      │
│              │ requiring strict consistency (fine-tune)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero training cost vs lower accuracy and  │
│              │ higher per-request cost (longer prompts)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Show 3 examples, the AI infers the       │
│              │ rule — no training, no labels, no delay." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Zero-Shot → In-Context Learning →         │
│              │ Chain-of-Thought                          │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A research paper shows that in-context few-shot examples with RANDOM labels (e.g., marking positive sentiment emails as "negative" and vice versa) still yield 70% of the performance of correctly labelled examples. What does this tell you about what few-shot examples actually teach the model — and what does it reveal about the limits of few-shot learning for tasks where the model's pretrained beliefs about label semantics are wrong?

**Q2.** You are deploying a few-shot classification system at 10 million requests per day. At 5 examples × 100 tokens each = 500 tokens overhead per request, the daily cost premium over zero-shot is substantial. Design a caching and routing architecture that retains few-shot quality benefits while reducing the token overhead by at least 80% — and explain what trade-off your architecture introduces versus a naive per-request few-shot approach.
