---
layout: default
title: "Self-Attention"
parent: "AI Foundations"
nav_order: 1587
permalink: /ai-foundations/self-attention/
number: "1587"
category: AI Foundations
difficulty: ★★★
depends_on: Attention Mechanism, Transformer Architecture, Embedding
used_by: GPT Architecture, BERT, Foundation Models, Multimodal Models
related: Attention Mechanism, Cross-Attention, Causal Masking
tags:
  - ai
  - advanced
  - deep-dive
  - internals
  - architecture
---

# 1587 — Self-Attention

⚡ TL;DR — Self-attention lets every token in a sequence build its contextual meaning by dynamically attending to all other tokens in the same sequence simultaneously.

| #1587           | Category: AI Foundations                                     | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Attention Mechanism, Transformer Architecture, Embedding     |                 |
| **Used by:**    | GPT Architecture, BERT, Foundation Models, Multimodal Models |                 |
| **Related:**    | Attention Mechanism, Cross-Attention, Causal Masking         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In pre-Transformer models, a word embedding was static — the vector for "bank" was identical whether the sentence was "I deposited money at the bank" or "I sat by the river bank." To understand that "bank" means financial institution in the first sentence and riverbank in the second, the model needed external context — typically from an RNN's hidden state. But the RNN had to process tokens sequentially, with context from word 1 diluting by the time it reached word 20.

No mechanism existed to allow "bank" to directly update its meaning by attending to "deposited" (financial) or "river" (geographical) simultaneously and in parallel.

**THE BREAKING POINT:**
Word meaning is contextual. Static embeddings cannot capture polysemy. Sequential models carry context with degrading fidelity. What was needed was a way for every token's representation to be simultaneously updated by every other token in the same sequence.

**THE INVENTION MOMENT:**
"This is exactly why Self-Attention was designed — allow each token to compute a _contextualised_ representation by directly attending to every other token in its own sequence."

---

### 📘 Textbook Definition

Self-attention is a variant of the attention mechanism in which queries, keys, and values are all derived from the same input sequence. For a sequence X, the projections Q = XW_q, K = XW_k, V = XW_v use the same X for all three. The output for each position is a weighted combination of the value vectors of all positions, weighted by the compatibility (dot product) between that position's query and every position's key. This allows each token to build a context-aware representation informed by the full sequence.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every token asks every other token in the same sentence "how relevant are you to me?" and updates itself accordingly.

**One analogy:**

> Imagine a round table discussion where every person can simultaneously ask everyone else a question and receive a tailored answer. Each person then updates their own understanding based on the relevance-weighted answers they received. This happens in one round — not sequentially. Self-attention is this round table, with tokens as participants and learned Q/K/V projections determining the questions and answers.

**One insight:**
The "self" in self-attention is the entire insight — the same sequence provides queries, keys, AND values. This means every token's new representation is computed from its own raw embedding plus what it learned by querying every other token in the same sequence. The result: contextualised token representations where "bank" near "deposited" has a completely different vector than "bank" near "river."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Q, K, V all derive from the same sequence — no external sequence is involved.
2. Each output position i attends to _all_ input positions (or all past positions with causal masking).
3. The output for each position is a weighted blend of all value vectors — position i "absorbs" information from positions that are semantically relevant to it.

**DERIVED DESIGN:**
Start from the need for contextualised representations: each token must be able to gather information from any other token. This requires: (a) a query vector for each token expressing "what I need," (b) a key vector for each token expressing "what I can provide," (c) a value vector for each token expressing "what I contribute when selected," (d) all three derived from the same input X, allowing the model to simultaneously learn what each token seeks and what it offers. The learned weight matrices W_q, W_k, W_v allow this decomposition to be optimised for the task.

**THE TRADE-OFFS:**
**Gain:** Contextualised token representations; parallel computation over the full sequence; O(1) distance between any two tokens.
**Cost:** O(n²) complexity in both time and memory; generates contextual representations but no memory of sequences outside the context window; sensitive to context window size.

---

### 🧪 Thought Experiment

**SETUP:**
Consider the word "it" in two sentences:

- S1: "The trophy didn't fit in the suitcase because it was too big."
- S2: "The trophy didn't fit in the suitcase because it was too small."

**WHAT HAPPENS WITHOUT SELF-ATTENTION:**
"It" has the same static embedding in both sentences. The model must use downstream layers to disambiguate — "it" = trophy in S1 and suitcase in S2. The disambiguation signal comes from "too big" vs "too small" but is far from "it" in the sequence. A sequential RNN might capture this for short sentences; for longer ones, signal degrades.

**WHAT HAPPENS WITH SELF-ATTENTION:**
When computing the self-attention output for "it" in S1: the query for "it" scores highly against the key for "trophy" (trophy is the subject, grammatically plausible referent), and the value for "trophy" is blended into "it"'s new representation. The word "big" also attends to "trophy" (big things don't fit), reinforcing the resolution. In S2, "small" makes "suitcase" the high-scoring key for "it." Same mechanism, opposite disambiguation.

**THE INSIGHT:**
Self-attention creates _dynamic_ context-specific embeddings. The same word has different representations in different contexts because its representation is computed fresh based on what surrounds it each time.

---

### 🧠 Mental Model / Analogy

> Self-attention is like reading your own diary entry while simultaneously cross-referencing every other entry you've ever written. Each word in today's entry becomes enriched with meaning from all the other words in the same entry that are related to it. The enrichment is dynamic — "bank" in a financial diary entry looks at "transaction" and "deposit"; "bank" in a travel diary looks at "river" and "paddle."

- "Today's diary entry" → the input token sequence
- "Each word in the entry" → each token position
- "Cross-referencing related entries" → computing attention scores to all other positions
- "Enriched word meaning" → the new contextualised token representation (attention output)
- "Deciding which entries to reference" → learned Q/K similarity scoring

Where this analogy breaks down: diary cross-referencing is a sequential, conscious act; self-attention computes all relationships simultaneously in a single matrix operation.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Self-attention means every word in a sentence looks at every other word in the same sentence to understand what it means in context. "Bank" near "river" becomes a riverbank; "bank" near "deposit" becomes a financial institution. The same word, different meaning, computed from context.

**Level 2 — How to use it (junior developer):**
Self-attention is the core operation inside every Transformer encoder and decoder. You access it through `nn.MultiheadAttention` with `query=x, key=x, value=x` (same tensor for all three). For GPT-style models, add a causal mask so each token only attends to past tokens. For BERT-style models, use bidirectional self-attention (no mask). The number of heads and hidden dimension are the key hyperparameters.

**Level 3 — How it works (mid-level engineer):**
For a sequence of L tokens, self-attention computes: Q = XW_q, K = XW_k, V = XW_v (each shape: L × d_k). The attention matrix A = softmax(QKᵀ / √d_k) is L × L — every token pair gets a score. Output = A·V blends each token's value into every other token's representation proportionally. With multi-head attention, H independent heads compute this in parallel, with separate W matrices, capturing different relationship types. Outputs are concatenated and projected: Concat(head_1,...,head_H) W_o.

**Level 4 — Why it was designed this way (senior/staff):**
The key insight behind the separate Q/K/V projection is that "what token A asks for" and "what token A can provide" are different things. Without the separation, you'd need QKᵀ = X·Xᵀ — pure cosine similarity of embeddings. But raw embedding similarity conflates syntactic and semantic relationships. The Q/K projections allow the model to learn independent subspaces for "questioning" and "answering." Empirically, BERT's attention heads have been shown to specialise: head 0 tracks direct objects, head 5 tracks coreference, head 9 tracks positional succession — each head learns a distinct relational subspace.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│             SELF-ATTENTION — FULL PASS               │
│                                                      │
│  Input sequence X: (L tokens, each d_model dims)    │
│                                                      │
│  Project to Q, K, V:                                │
│    Q = X · W_q    shape: (L, d_k)                   │
│    K = X · W_k    shape: (L, d_k)                   │
│    V = X · W_v    shape: (L, d_v)                   │
│                                                      │
│  All three from SAME X — this is "self" attention   │
│                                                      │
│  Compute attention matrix:                          │
│    A = softmax(Q · Kᵀ / √d_k)  shape: (L, L)       │
│    A[i][j] = how much token i attends to token j    │
│                                                      │
│  Compute output for each token:                     │
│    Out = A · V    shape: (L, d_v)                   │
│    Out[i] = weighted sum of V[j] by A[i][j]         │
│                                                      │
│  Each token's output = its own context-aware repr   │
└──────────────────────────────────────────────────────┘

CAUSAL MASK (GPT-style decoder):
    A[i][j] = -∞  for j > i  (future tokens masked)
    Enforces: token i can only attend to tokens 0..i
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (BERT-style encoder):**

```
Input text: "The bank is near the river"
     ↓
Tokenise → ["The", "bank", "is", "near", "the", "river"]
     ↓
Embed → 6 × 768 matrix (token embeddings)
     ↓
+ Positional Encoding → 6 × 768
     ↓
Self-Attention Layer ← YOU ARE HERE
  "bank" attends to "river" → high weight
  "bank" attends to "is" → medium weight
  Output: new "bank" embedding incorporates river context
     ↓
× 12 stacked Transformer layers
     ↓
Final contextualised embeddings
```

**FAILURE PATH:**
All tokens attend to [CLS] token only → representation collapse → check for positional encoding issues or normalisation problems.
Attention matrix is near-uniform → model ignores context → learning rate too high or initialisation issue.

**WHAT CHANGES AT SCALE:**
At 512-token sequences (BERT), full self-attention is fast (512² = 262K cells). At 32K tokens (modern LLMs), the matrix has 1 billion cells — FlashAttention is mandatory. At 1M tokens, sparse or linear attention variants are the only practical options.

---

### 💻 Code Example

**Example 1 — Self-attention vs cross-attention in PyTorch:**

```python
import torch.nn as nn

d_model, num_heads = 512, 8
mha = nn.MultiheadAttention(d_model, num_heads, batch_first=True)

# Self-attention: same tensor for Q, K, V
# x shape: (batch, seq_len, d_model)
x = torch.randn(2, 10, d_model)
sa_out, sa_weights = mha(query=x, key=x, value=x)
# sa_out: (2, 10, d_model) — each token now context-aware

# Cross-attention: Q from decoder, K/V from encoder
dec = torch.randn(2, 5, d_model)   # decoder sequence
enc = torch.randn(2, 10, d_model)  # encoder sequence
ca_out, ca_weights = mha(query=dec, key=enc, value=enc)
# dec tokens now attend to encoder context
```

**Example 2 — Causal self-attention (GPT-style):**

```python
def causal_self_attention(x, mha):
    """
    x: (batch, seq_len, d_model)
    Tokens may only attend to themselves and past tokens.
    """
    seq_len = x.shape[1]
    # Causal mask: upper triangle = True (masked/ignored)
    causal_mask = torch.triu(
        torch.ones(seq_len, seq_len, dtype=torch.bool),
        diagonal=1
    ).to(x.device)
    # attn_mask=True positions are ignored in PyTorch
    out, weights = mha(
        query=x, key=x, value=x,
        attn_mask=causal_mask,
        is_causal=True  # PyTorch 2.0+: enables FlashAttention
    )
    return out
```

**Example 3 — Inspecting contextualised representations:**

```python
from transformers import AutoTokenizer, AutoModel
import torch

model = AutoModel.from_pretrained("bert-base-uncased",
                                   output_hidden_states=True)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

sentences = [
    "I deposited money at the bank",
    "I sat by the river bank",
]
for sent in sentences:
    inputs = tokenizer(sent, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the embedding for "bank" (token 4 in both sentences)
    bank_embedding = outputs.last_hidden_state[0, 4, :]
    print(f"'{sent[:30]}...' bank embedding norm: "
          f"{bank_embedding.norm():.2f}")
# The two "bank" embeddings should be far apart in space
```

---

### ⚖️ Comparison Table

| Mechanism                  | Q source    | K/V source           | Direction      | Best For                           |
| -------------------------- | ----------- | -------------------- | -------------- | ---------------------------------- |
| **Self-Attention (bidir)** | Same seq    | Same seq             | Both ways      | Context understanding (BERT)       |
| Self-Attention (causal)    | Same seq    | Same seq (past only) | Past only      | Autoregressive generation (GPT)    |
| Cross-Attention            | Decoder seq | Encoder seq          | Cross-sequence | Seq2seq translation, summarisation |
| Sparse Self-Attention      | Same seq    | Local window         | Both ways      | Long-document processing           |

How to choose: use bidirectional self-attention for encoding/understanding tasks; use causal self-attention for generation; use cross-attention when query and context are different sequences.

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                             |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Self-attention and attention are the same thing                | Self-attention is a specific case of attention where Q, K, V all come from the same sequence                                                        |
| Causal masking makes GPT "unidirectional"                      | GPT processes the _entire_ context window — but for each token, only past tokens are visible; context is still rich                                 |
| Self-attention produces the same output regardless of position | Without positional encoding, self-attention is truly permutation-invariant — "dog bites man" and "man bites dog" would have identical token outputs |
| Each attention head captures one grammatical relationship      | Attention head specialisation emerges empirically; it is learned, not programmed — and may capture unexpected or mixed relationships                |

---

### 🚨 Failure Modes & Diagnosis

**1. Representation Collapse (All Tokens Attend to One Position)**

**Symptom:** Model outputs nearly identical representations for all tokens; downstream tasks show no benefit from context.

**Root Cause:** One token (often [CLS] or a separator) dominates all attention weights — all other tokens point to it. Often caused by layer normalisation issues or pathological initialisation.

**Diagnostic:**

```python
# Check max attention weight across all tokens per head
for layer_idx, attn in enumerate(outputs.attentions):
    # attn: (batch, heads, seq, seq)
    max_weight = attn[0].max(dim=-1).values  # (heads, seq)
    dominant = (max_weight > 0.9).float().mean()
    print(f"Layer {layer_idx}: "
          f"{dominant:.0%} positions have dominant token")
```

**Fix:** Check layer normalisation placement (pre-norm vs post-norm); check weight initialisation.

**Prevention:** Monitor attention entropy during training; alert when average entropy drops below threshold.

**2. Causal Mask Bug (Attending to Future Tokens)**

**Symptom:** GPT-style model achieves unrealistically high next-token prediction accuracy during training; fails completely in autoregressive generation.

**Root Cause:** Causal mask incorrectly applied — future tokens are visible during training, but not at generation time (no future tokens available).

**Diagnostic:**

```python
# Verify causal mask shape and direction
seq_len = 10
mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)
print(mask)
# Upper triangle should be 1 (masked) — verify:
assert mask[0, 5] == 1  # token 0 cannot see token 5
assert mask[5, 0] == 0  # token 5 CAN see token 0
```

**Fix:** Ensure `diagonal=1` (not 0) in `torch.triu`; use `is_causal=True` in PyTorch 2.0+.

**Prevention:** Write a unit test verifying causal mask direction before training begins.

**3. Positional Encoding Missing or Wrong**

**Symptom:** Model produces correct predictions but in the wrong order; shuffling input tokens produces identical outputs.

**Root Cause:** Positional encoding not added or incorrectly added. Self-attention is permutation-invariant without it.

**Diagnostic:**

```python
# Test: shuffle tokens and check if output changes
import torch
x = torch.randn(1, 5, d_model)
perm = torch.randperm(5)
x_shuffled = x[:, perm, :]

out_orig = model(x)
out_shuffled = model(x_shuffled)
diff = (out_orig - out_shuffled[:, perm, :]).abs().mean()
print(f"Output diff after shuffle: {diff:.4f}")
# If diff ≈ 0: positional encoding is missing or broken
```

**Fix:** Ensure positional encoding is added to embeddings before the first self-attention layer.

**Prevention:** Include this shuffle test in your model validation suite.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Attention Mechanism` — self-attention is a specialisation of the general attention mechanism; understand Q/K/V scoring first
- `Embedding` — self-attention operates on token embeddings; understanding dense vector representations is required

**Builds On This (learn these next):**

- `Transformer Architecture` — self-attention is the core operation inside every Transformer layer
- `GPT Architecture` — uses causal self-attention (masked to past positions) for autoregressive generation
- `BERT` — uses bidirectional self-attention (no mask) for deep context understanding

**Alternatives / Comparisons:**

- `Cross-Attention` — same computation but Q comes from a different sequence than K/V; used in encoder-decoder translation
- `Linear Attention` — approximates self-attention in O(n) time by changing the softmax kernel, enabling long-context processing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Attention where Q, K, V all come from     │
│              │ the same input sequence                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Static embeddings can't be contextual;    │
│ SOLVES       │ "bank" means different things in          │
│              │ different sentences                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Every token's representation is           │
│              │ dynamically computed from its context     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ You need contextualised token             │
│              │ representations (all modern NLP tasks)   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sequence is very long (>50K tokens) and   │
│              │ O(n²) cost is unacceptable                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Context-aware representations vs O(n²)    │
│              │ cost and no persistent memory             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The same sequence asks itself            │
│              │  what every word means to every other."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GPT Architecture → BERT →                 │
│              │ Foundation Models                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** BERT uses bidirectional self-attention (each token attends to all other tokens). GPT uses causal self-attention (each token attends only to past tokens). BERT was considered better for understanding tasks; GPT better for generation. Now GPT-4 outperforms BERT on understanding benchmarks too, using only causal self-attention. What architectural and scale changes allowed a causal model to match a bidirectional model on understanding tasks, and does this invalidate the original reasoning behind BERT's bidirectional design?

**Q2.** In a 12-layer BERT model, researchers find that layer 3 attention heads predominantly track syntactic dependency structures, while layer 9 heads track semantic coreference. No one programmed these specialisations — they emerged from training. Explain why deep stacking of self-attention layers causes this kind of emergent specialisation, and predict what would happen to these specialised functions if you fine-tuned the model on a new domain with a very small dataset.
