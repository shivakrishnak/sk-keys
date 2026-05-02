---
layout: default
title: "Top-p / Top-k Sampling"
parent: "AI Foundations"
nav_order: 1593
permalink: /ai-foundations/top-p-top-k-sampling/
number: "1593"
category: AI Foundations
difficulty: ★★★
depends_on: Token, Temperature, Inference
used_by: Hallucination, Fine-Tuning, Model Evaluation Metrics
related: Temperature, Grounding, Beam Search
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - tradeoff
---

# 1593 — Top-p / Top-k Sampling

⚡ TL;DR — Top-k and top-p are sampling filters that constrain which tokens the model can choose from, preventing both repetitive certainty and incoherent randomness in generated text.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A language model applies temperature to all 50,000+ tokens in its vocabulary. Even with temperature=0.7, there are thousands of tokens with non-zero probability after softmax — including "the" and "," but also "😈" and random Unicode characters. On rare but non-negligible occasions, the model samples one of these absurd low-probability tokens and the text derails. Multiply this over a 500-token response and random derailments become a production issue.

**THE BREAKING POINT:**
Pure temperature sampling creates a dilemma: low temperature gives coherent but repetitive text; high temperature gives varied but often grammatically broken text. There is no setting that gives both coherence and diversity at the same time.

**THE INVENTION MOMENT:**
This is exactly why Top-p and Top-k were introduced — as pre-sampling filters that truncate the vocabulary to only plausible tokens before sampling, ensuring the model never selects tokens that were never realistic candidates regardless of the temperature setting.

---

### 📘 Textbook Definition

**Top-k sampling** restricts generation to the k highest-probability tokens at each step, redistributing probability mass zero to all tokens outside the top-k before sampling. **Top-p sampling** (nucleus sampling, Holtzman et al. 2020) dynamically selects the smallest set of tokens whose cumulative probability exceeds threshold p, then samples only from that set. Both strategies operate after temperature scaling and before the final softmax, and they are composable — top-k can be applied first, then top-p on the resulting set.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Top-k and top-p filter out the "wild card" tokens so the model only picks from genuinely reasonable options.

**One analogy:**
> Imagine choosing your lunch from a restaurant menu. Top-k says "only consider the 5 most popular dishes." Top-p says "only consider dishes until you've covered 90% of what most people order." Both approaches stop you from accidentally ordering something bizarre that happens to be on the menu.

**One insight:**
The critical difference: top-k has a fixed number of candidates regardless of how peaked or flat the distribution is. Top-p adapts — when the model is very confident (peaked distribution), it might consider only 2 tokens; when it is uncertain (flat distribution), it might consider 50. This makes top-p more robust across different contexts.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. After temperature scaling, a softmax produces a probability distribution over the full vocabulary.
2. Low-probability tokens can still be sampled with non-zero probability.
3. In long sequences, even very rare events (p=0.001) happen occasionally — causing derailment.

**DERIVED DESIGN:**
**Top-k approach:**
Sort tokens by probability. Set probability of tokens ranked > k to 0. Renormalise remaining k tokens to sum to 1. Sample from renormalised distribution.

```
vocab = [A:0.40, B:0.30, C:0.20, D:0.06, E:0.04, ...]
top-3: [A:0.45, B:0.34, C:0.21]  (renormalised)
```

**Top-p (nucleus) approach:**
Sort by probability descending. Accumulate probabilities until sum ≥ p. Include all tokens in this "nucleus." Sample only from the nucleus.

```
p=0.90 nucleus:
A:0.40 → cumsum=0.40
B:0.30 → cumsum=0.70
C:0.20 → cumsum=0.90 ← stop here
nucleus = {A, B, C}, renormalise
```

**THE TRADE-OFFS:**
**Top-k:** Simple, fast. Fixed k causes problems: in high-confidence positions (k=40 but 35 tokens have near-zero probability), you still sample from 40 tokens including terrible ones. In low-confidence positions, you may exclude plausible alternatives.

**Top-p gain:** Adapts to local distribution shape — tight nucleus when confident, wider when uncertain.
**Top-p cost:** Nucleus size varies from 1 to thousands depending on the step; implementation must sort the full vocabulary each step.

Could we do this differently? Typical practice: apply both. Set top-k first (e.g., k=50) to eliminate the long tail, then top-p=0.9 on the remaining 50 to further focus the sample.

---

### 🧪 Thought Experiment

**SETUP:**
Two positions in a generation task: Position A = after "The capital of France is" (model is highly confident). Position B = after "Once upon a time, a creative hero decided to" (model is uncertain; many valid continuations).

**WHAT HAPPENS WITH TOP-K=50:**
Position A: model assigns "Paris" p=0.97. Top-50 still includes 49 other tokens (each with tiny probability). Even with T=0.5, occasionally "Lyon" or "Berlin" is sampled.
Position B: top-50 tokens are all plausible. Sampling produces diverse, interesting story continuations.

**WHAT HAPPENS WITH TOP-P=0.95:**
Position A: "Paris" alone covers p=0.97 > 0.95. Nucleus = {"Paris"} only. Sampling is deterministic for this step — always "Paris."
Position B: many tokens each have p=0.01–0.05. Nucleus grows to 30–40 tokens. Diverse, creative sampling.

**THE INSIGHT:**
Top-p is context-aware — it produces narrow samples when the model is confident and wide samples when uncertain. This is the key property that makes it superior to fixed top-k for general use.

---

### 🧠 Mental Model / Analogy

> Think of a trivia game show where the host reads out the most popular answers in order until the total audience votes reaches 90%. When the question is "Name a European capital" — just "London" gets 95% → nucleus has 1 answer. When the question is "Name a colour" — you need "red, blue, green, yellow, purple..." to reach 90% → nucleus has many answers. The host (top-p) always stops at exactly 90%, regardless of question difficulty.

Mapping:
- "Trivia question" → each token generation step
- "Audience votes" → token probabilities
- "90% threshold" → p parameter
- "Answers in nucleus" → tokens eligible for sampling
- "Drawing a random audience member" → sampling from the nucleus

Where this analogy breaks down: the model doesn't have a fixed audience — probabilities can be near-uniform across hundreds of tokens for truly ambiguous positions, making the nucleus very large even at p=0.9.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Top-k and top-p are safety nets that stop the AI from picking a completely random, inappropriate word. They ensure only sensible options are on the table before the random selection happens.

**Level 2 — How to use it (junior developer):**
A practical starting point: `temperature=0.7, top_p=0.9, top_k=50`. This combination is robust for most tasks. For deterministic output: `temperature=0, top_p=1.0` (top-p has no effect at T=0 since softmax collapses to argmax). For creative writing: `temperature=1.0, top_p=0.95, top_k=0` (disable top-k, use only top-p). Always check your model provider's default — some apply top-p by default; others do not.

**Level 3 — How it works (mid-level engineer):**
The full sampling pipeline per token step: (1) compute logits via forward pass; (2) apply temperature scaling; (3) apply top-k filter (if k>0): zero out all but top-k; (4) apply top-p filter (if p<1): compute cumulative probabilities, zero out tokens outside nucleus; (5) renormalise remaining probabilities to sum to 1; (6) sample from the resulting distribution using multinomial sampling. Each step is deterministic given a seed — making the full pipeline reproducible if a seed is set.

**Level 4 — Why it was designed this way (senior/staff):**
Nucleus sampling was introduced in "The Curious Case of Neural Text Degeneration" (Holtzman et al., 2020) specifically in response to the observation that purely temperature-based sampling caused text degeneration at long generation lengths. The dynamic nucleus property (adapting to distribution shape) was empirically shown to match human text statistics better than fixed-k strategies. In practice, modern frontier models (GPT-4, Claude, Gemini) use a combination of top-p and fine-tuned RLHF policies that make the sampling less manual — but the top-p concept remains foundational for open models and fine-tuning workflows where you control the full inference stack.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ After temperature scaling:                  │
│ Token probabilities (sorted desc):          │
│  "Paris"    → 0.40                          │
│  "the"      → 0.18                          │
│  "London"   → 0.15                          │
│  "capital"  → 0.10                          │
│  "France"   → 0.07                          │
│  ... (50K more tokens)                      │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ TOP-K filter (k=3):                         │
│  Keep: Paris(0.40), the(0.18), London(0.15) │
│  Zero out: all others                       │
│  Renormalise: Paris=0.55, the=0.25,         │
│               London=0.20                   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ TOP-P filter (p=0.90) on k=3 result:        │
│  cumsum: 0.55 → 0.80 → 1.00                 │
│  p=0.90: all 3 included (0.80 < 0.90)       │
│  Nucleus = {Paris, the, London}             │
└──────────────┬──────────────────────────────┘
               ↓
        Multinomial sample from nucleus
```

**Happy path:** Both filters narrow the vocabulary to plausible tokens → coherent, diverse output.

**Error path (k too small):** Nucleus is always size k, even when model is uncertain — undersamples diversity in ambiguous positions.

**Error path (p too high, e.g., 1.0):** Full vocabulary is included — equivalent to pure temperature sampling with no filtering.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Prompt input
    ↓
Transformer forward pass
    ↓
Raw logits (50K+ values)
    ↓
Temperature scaling
    ↓
[TOP-K filter ← YOU ARE HERE]
    ↓
[TOP-P nucleus filter ← ALSO HERE]
    ↓
Renormalise
    ↓
Multinomial sample → next token
    ↓
Append token, repeat
```

**FAILURE PATH:**
```
top_p = 1.0 and temperature = 1.5
    ↓
Full vocabulary eligible for sampling
    ↓
Occasional rare tokens selected
    ↓
Text derailment, incoherent output
    ↓
User sees: "The answer to your question is △9FBZ..."
```

**WHAT CHANGES AT SCALE:**
Sorting the full vocabulary at each token step (for top-p) is O(V log V) per step where V ≈ 50K tokens. With optimised GPU kernels (top-k is highly parallelisable), this is negligible at individual request scale. At very high concurrency with long sequences, batch token generation can make top-p sorting a meaningful portion of inference time — some optimised inference servers (vLLM, TGI) cache sorted vocabularies.

---

### 💻 Code Example

**Example 1 — Manual top-k implementation:**
```python
import torch
import torch.nn.functional as F

def top_k_sample(logits: torch.Tensor, k: int,
                 temperature: float = 1.0) -> int:
    """Sample next token using top-k filtering."""
    logits = logits / temperature
    # Zero out all but top-k
    top_k_values, _ = torch.topk(logits, k)
    threshold = top_k_values[-1]  # k-th largest value
    logits[logits < threshold] = float('-inf')
    probs = F.softmax(logits, dim=-1)
    return torch.multinomial(probs, num_samples=1).item()
```

**Example 2 — Manual top-p (nucleus) implementation:**
```python
def top_p_sample(logits: torch.Tensor, p: float,
                 temperature: float = 1.0) -> int:
    """Sample next token using nucleus (top-p) sampling."""
    logits = logits / temperature
    probs = F.softmax(logits, dim=-1)
    sorted_probs, sorted_idx = torch.sort(probs,
                                          descending=True)
    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
    # Remove tokens once cumulative prob exceeds p
    sorted_remove = cumulative_probs > p
    # Shift right: keep at least 1 token
    sorted_remove[..., 1:] = sorted_remove[..., :-1].clone()
    sorted_remove[..., 0] = 0
    # Scatter removal back to original indices
    remove = sorted_remove.scatter(-1, sorted_idx,
                                   sorted_remove)
    probs[remove] = 0.0
    probs = probs / probs.sum()  # renormalise
    return torch.multinomial(probs, num_samples=1).item()
```

**Example 3 — Combined strategy via OpenAI API:**
```python
import openai

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem."}],
    temperature=0.9,   # allow some variance
    top_p=0.95,        # nucleus: 95% cumulative probability
    # top_k is not exposed in OpenAI API directly
    # but is applied internally
    frequency_penalty=0.2,  # further reduce repetition
)
```

---

### ⚖️ Comparison Table

| Strategy | Nucleus Size | Context-Aware | Coherence | Best For |
|---|---|---|---|---|
| Greedy (T=0) | 1 | No | Highest | Deterministic, testable tasks |
| **Top-k** | Fixed k | No | High | Simple, fast filtering |
| **Top-p (nucleus)** | Dynamic | Yes | High | General production use |
| Top-k + Top-p | ≤k, dynamic | Yes | Highest | Best-practice default |
| Temperature only | Full vocab | No | Medium | Quick experiments |
| Beam search | All beams | No | Highest | Translation, structured gen |

**How to choose:** Use top-p=0.9 as your default. Add top-k=50 as an outer cap to prevent extremely large nuclei. Use beam search only for structured generation where you need the single highest-probability sequence (e.g., translation, JSON extraction).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Top-k and top-p do the same thing" | Top-k is fixed; top-p adapts to distribution shape — they solve different failure modes |
| "top_p=1.0 means no filtering" | Correct — p=1.0 disables nucleus filtering, allowing full-vocabulary sampling |
| "Higher top-p always means more creative output" | Higher top-p widens the nucleus, but if temperature is low, high-probability tokens still dominate |
| "These parameters affect model quality" | They only affect sampling strategy at inference; model weights are unchanged |
| "Setting both top-k and top-p is redundant" | They are complementary: top-k limits maximum nucleus size; top-p limits minimum quality |

---

### 🚨 Failure Modes & Diagnosis

**Repetition Loop Despite top-p**

**Symptom:** Model repeats the same sentence pattern even with top-p=0.9 and temperature=0.8.

**Root Cause:** After RLHF or fine-tuning, the model's learned distribution may concentrate very high probability on a narrow set of tokens even with filtering. The repetition is not a sampling issue but a distribution issue.

**Diagnostic Command / Tool:**
```python
# Inspect raw logits at the problem step
import torch
with torch.no_grad():
    logits = model(input_ids).logits[0, -1, :]
top_values, top_ids = torch.topk(logits, 10)
print(tokenizer.convert_ids_to_tokens(top_ids.tolist()))
print(top_values.softmax(-1))
# If one token has >0.9 probability, top-p can't help
```

**Fix:** Increase `frequency_penalty` / `repetition_penalty`, or increase temperature. Consider fine-tuning to diversify the distribution.

**Prevention:** Monitor repetition scores (see Temperature entry) in post-generation quality checks.

---

**Too Small Nucleus (top-p too low)**

**Symptom:** Generated text is grammatically correct but semantically rigid; all responses sound identical; creative tasks produce predictable output.

**Root Cause:** top-p=0.5 on an ambiguous generation step collapses the nucleus to 1–2 tokens, forcing near-deterministic output regardless of temperature.

**Diagnostic Command / Tool:**
```python
# Log nucleus size per step during generation
cumprobs = torch.cumsum(sorted_probs, dim=-1)
nucleus_size = (cumprobs < top_p).sum().item() + 1
print(f"Nucleus size at this step: {nucleus_size}")
```

**Fix:** Increase top-p to 0.85–0.95 for creative tasks.

**Prevention:** Empirically test nucleus size distribution across representative inputs before deploying.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Token` — sampling operates at the token level; understanding token granularity is essential
- `Temperature` — top-p and top-k are applied after temperature scaling; they are part of the same pipeline
- `Inference` — these are inference-time parameters; understanding the forward pass is required

**Builds On This (learn these next):**
- `Hallucination` — understanding sampling strategies clarifies which hallucination causes are controllable at inference time
- `Model Evaluation Metrics` — diversity metrics (distinct-n, self-BLEU) measure the quality of sampling strategies
- `Fine-Tuning` — an alternative to sampling tricks for controlling output distribution

**Alternatives / Comparisons:**
- `Temperature` — the upstream step that top-p/top-k refine; they work together, not as alternatives
- `Grounding` — addresses hallucination at the context level rather than the sampling level
- `Beam Search` — deterministic alternative to sampling; does not use top-p or top-k

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Vocabulary filters applied before token   │
│              │ sampling to eliminate improbable options  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Pure temperature sampling allows          │
│ SOLVES       │ derailment via very low-prob tokens       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Top-p adapts nucleus size to the model's  │
│              │ confidence — tighter when certain,        │
│              │ wider when uncertain                      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always use top-p=0.9 as production        │
│              │ default; add top-k=50 as outer cap        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ top-p=1.0 disables filtering; only use   │
│              │ with T=0 (greedy) to avoid derailment     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Coherence and safety vs creative          │
│              │ diversity and vocabulary breadth          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Only consider plausible options —        │
│              │ but exactly how many depends on           │
│              │ how sure the model is."                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Temperature → Hallucination → Grounding   │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are generating 10,000 synthetic training examples using an LLM with top-p=0.95 and temperature=1.0. A colleague argues you should use top-p=0.6 to "increase quality." Trace the downstream effect: how does a smaller nucleus affect the diversity of your synthetic dataset, what statistical property of the training distribution does this create, and how does it propagate to model quality after fine-tuning on the synthetic data?

**Q2.** Top-p and temperature both control output diversity, yet they achieve it through different mechanisms. Design a scenario where: (a) high temperature + low top-p gives coherent, creative output; and (b) low temperature + high top-p gives incoherent output. What does this reveal about the interaction between these two parameters and the correct order of operations in the sampling pipeline?
