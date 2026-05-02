---
layout: default
title: "Context Window"
parent: "AI Foundations"
nav_order: 1591
permalink: /ai-foundations/context-window/
number: "1591"
category: AI Foundations
difficulty: ★★☆
depends_on: Token, Tokenization, Transformer Architecture
used_by: In-Context Learning, Retrieval-Augmented Generation, Fine-Tuning
related: Embedding, Attention Mechanism, Hallucination
tags:
  - ai
  - llm
  - foundational
  - intermediate
  - mental-model
---

# 1591 — Context Window

⚡ TL;DR — A context window is the maximum number of tokens an LLM can "see" at once — its working memory that determines how much text it can reason over in a single interaction.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine asking a consultant to review a 500-page technical document, but they can only read one page at a time and forget the previous page the moment they turn to the next. They cannot connect an architectural decision on page 12 with its consequence on page 340. Every answer they give is dangerously local — missing the broader picture.

**THE BREAKING POINT:**
Early neural networks processed inputs of a fixed, very short length. Trying to pass a long conversation history or a multi-chapter codebase would crash or simply get silently truncated. The model had no principled way to know how much context it could handle, and engineers had no way to control it.

**THE INVENTION MOMENT:**
This is exactly why Context Window was defined — as the hard boundary on how much token history the model's attention mechanism can span, enabling engineers to manage memory, cost, and coherence explicitly.

---

### 📘 Textbook Definition

A **context window** is the maximum number of tokens — including input (prompt), retrieved context, and generated output — that a transformer-based language model can process in a single forward pass. The model has full attention over every token within this window. Tokens outside the window are not accessible to the model. Modern models range from 4K tokens (GPT-3.5 original) to over 1 million tokens (Gemini 1.5 Pro).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The context window is how much the model can read and remember at one time.

**One analogy:**
> Think of it like a desk. You can only spread out so many papers at once. Everything on the desk is available to you — you can cross-reference anything. But if you need a document that's still in the filing cabinet, you can't use it until you bring it to the desk (at the cost of removing something else).

**One insight:**
The context window is not just about length — it is about coherence. Everything within the window can attend to everything else. Once a token falls outside the window, the model has zero memory of it, no matter how important it was. This is why summarisation and RAG exist: to keep the most relevant facts on the "desk."

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Transformer attention is O(n²) in memory and time relative to sequence length.
2. A forward pass requires all input tokens to fit in GPU/TPU memory simultaneously.
3. Tokens outside the window cannot be attended to — there is no partial memory.

**DERIVED DESIGN:**
Given that attention requires all tokens to be present simultaneously and memory is finite, a hard cap must exist. This cap is the context window. The model is trained with positional encodings up to a maximum length — it cannot generalize reliably beyond that (though techniques like RoPE and sliding window attention push the boundary).

Training data shapes what the model learns about long-range dependencies. A 128K-token context window is not simply "more memory" — it requires specific architectural choices (ALiBi, RoPE, flash attention) to remain efficient and accurate at long range.

**THE TRADE-OFFS:**
**Gain:** Larger context = more coherent multi-turn reasoning, longer document processing, richer RAG retrieval.
**Cost:** Quadratic attention cost means 2× context ≈ 4× compute. At scale, a 128K-token window with 1000 concurrent users is radically more expensive than a 4K window.

Could we do this differently? Recurrent networks (RNNs/LSTMs) had theoretically infinite context, but compressed it into a fixed-size hidden state — losing exact recall of distant tokens. The attention-based window sacrifices infinite length for perfect recall within its boundary.

---

### 🧪 Thought Experiment

**SETUP:**
You have an LLM with a 4K-token context window. A user pastes a 3,000-token code file and asks: "What does this function on line 10 do?" Fine. Next they ask: "How does the function on line 200 relate to line 10?" The 4K window covers both — still fine. Now they paste a 10,000-token codebase and ask the same question.

**WHAT HAPPENS WITHOUT CONTEXT WINDOW AWARENESS:**
The model silently truncates the input to 4K tokens. Lines 150–250 (where both functions live) may or may not fit in the truncated window. If they are cut off, the model answers based on whatever DID fit — potentially fabricating a relationship based on partial context. The user receives a confident but wrong answer.

**WHAT HAPPENS WITH CONTEXT WINDOW AWARENESS:**
The application layer detects the input exceeds 4K tokens and applies a chunking/retrieval strategy: it extracts the relevant sections around line 10 and line 200, passes only those with surrounding context (< 4K tokens total). The model sees the relevant code and reasons correctly.

**THE INSIGHT:**
The context window is not a suggestion — it is a hard physical constraint. Any system built on LLMs must treat context management as a first-class architectural concern, not an afterthought.

---

### 🧠 Mental Model / Analogy

> Imagine a courtroom where the judge can only consider evidence presented in the current session. Evidence admitted in a previous session is completely off-limits — not inadmissible, just *gone*. The context window is the session length. Everything said in the current session is equally accessible to the judge (the model). Once the session exceeds its time limit, earlier evidence drops off the record.

Mapping:
- "Court session" → single LLM forward pass
- "Evidence in session" → tokens in the context window
- "Judge's reasoning" → self-attention over all tokens
- "Previous session" → tokens beyond the context window (invisible)
- "Case summary" → a summary injected to preserve prior context

Where this analogy breaks down: in a real courtroom, the judge retains memory of prior sessions; the LLM retains *nothing* — each call is stateless.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
It's the maximum amount of text an AI can read and think about at one time. Give it more text than it can handle and it starts forgetting the beginning.

**Level 2 — How to use it (junior developer):**
When building with an LLM API, always check the model's token limit. Count tokens before sending (use `tiktoken` for OpenAI models). For long documents, split into chunks and either summarise prior chunks or use RAG to retrieve only relevant parts. Never silently truncate — truncation means silent data loss.

**Level 3 — How it works (mid-level engineer):**
The transformer's attention mechanism computes query-key dot products across every token pair in the window — O(n²) in both time and memory. The model is trained with positional encodings up to a maximum position; at inference, positions beyond the trained maximum produce degraded or random outputs. Flash Attention (Dao et al., 2022) reduces memory from O(n²) to O(n) using tiling, enabling 128K+ windows without OOM. Context window length is also a fine-tuning decision: GPT-4-32K is the same base model as GPT-4 but trained with extended positional encodings.

**Level 4 — Why it was designed this way (senior/staff):**
The hard context boundary is an engineering choice, not a fundamental limitation of intelligence. Alternatives like state-space models (Mamba) use a fixed-size recurrent state that grows indefinitely without quadratic cost — but lose exact recall of specific tokens. The transformer trades efficiency for perfect within-window recall. At production scale, managing context windows is a cost-optimisation problem: billing is per-token, so an over-stuffed context window directly increases operational cost. Senior engineers design "context budgets" for each role in a multi-agent pipeline, ensuring the total token spend per request is bounded.

---

### ⚙️ How It Works (Mechanism)

When you call an LLM API, you pass a sequence of tokens. The model embeds every token into a high-dimensional vector and runs self-attention:

```
┌─────────────────────────────────────────────┐
│ Context Window = 4096 tokens                │
├────────────────┬────────────────────────────┤
│ System prompt  │ 200 tokens                 │
│ Conversation   │ 1,800 tokens               │
│ Retrieved docs │ 1,500 tokens               │
│ User question  │ 100 tokens                 │
│ Reserve output │ 496 tokens remaining       │
└────────────────┴────────────────────────────┘
```

**Step 1 — Tokenisation:** Raw text is split into tokens (subwords). "unbelievable" → ["un", "bel", "iev", "able"] = 4 tokens.

**Step 2 — Embedding:** Each token ID is looked up in an embedding matrix (e.g., 768 or 4096 dimensions per token for large models).

**Step 3 — Positional encoding:** A position vector is added to each token embedding so the model knows token order. RoPE (Rotary Position Embedding) encodes relative positions, enabling extrapolation beyond the training window.

**Step 4 — Self-attention over all positions:** Every token queries every other token within the window. This is the O(n²) step. Flash Attention optimises memory access but not the fundamental complexity.

**Step 5 — Output generation:** The model generates one token at a time, appending each to the context (consuming output budget). When the window fills, older tokens either truncate or a sliding-window strategy shifts the window.

**Happy path:** Total tokens < window limit → full coherent output.
**Error path:** Total tokens > window limit → API returns `context_length_exceeded` error, or silent truncation occurs if the SDK doesn't validate. Both paths destroy information.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
User input
    ↓
Token counting (tiktoken / API estimate)
    ↓
Context assembly (system + history + docs + query)
    ↓
[CONTEXT WINDOW CHECK ← YOU ARE HERE]
    ↓ (fits)
LLM forward pass (attention over all tokens)
    ↓
Token-by-token generation
    ↓
Response returned
```

**FAILURE PATH:**
```
Context exceeds window limit
    ↓
Silent truncation OR API error
    ↓
Model reasons over incomplete context
    ↓
Hallucination / wrong answer / confused response
```

**WHAT CHANGES AT SCALE:**
At high request volume, large context windows dominate cost — every token in the window is billed on every call. A 32K-token context at $0.01/1K tokens costs 32× more than a 1K-token context. High-scale systems implement aggressive context compression: rolling summaries, KV-cache reuse, and RAG to replace verbatim history with retrieved snippets.

---

### 💻 Code Example

**Example 1 — Counting tokens before sending (Python):**
```python
# BAD — silently truncates if over limit
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": huge_document}]
)

# GOOD — count first, chunk if needed
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

MAX_TOKENS = 8192
SAFETY_BUFFER = 500  # reserve for output

def safe_send(text: str, model: str = "gpt-4") -> str:
    token_count = count_tokens(text, model)
    if token_count > MAX_TOKENS - SAFETY_BUFFER:
        raise ValueError(
            f"Input too long: {token_count} tokens. "
            f"Max: {MAX_TOKENS - SAFETY_BUFFER}"
        )
    return openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}]
    ).choices[0].message.content
```

**Example 2 — Sliding window for long conversations:**
```python
from collections import deque

class ContextManager:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.messages = deque()
        self._token_count = 0

    def add_message(self, role: str, content: str):
        tokens = count_tokens(content)
        self.messages.append({
            "role": role,
            "content": content,
            "tokens": tokens
        })
        self._token_count += tokens
        # evict oldest messages when over budget
        while self._token_count > self.max_tokens:
            removed = self.messages.popleft()
            self._token_count -= removed["tokens"]

    def get_messages(self) -> list[dict]:
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages
        ]
```

---

### ⚖️ Comparison Table

| Strategy | Context Used | Quality | Cost | Best For |
|---|---|---|---|---|
| **Full context** | All tokens verbatim | Highest | Highest | Short docs, precision tasks |
| Sliding window | Most recent N tokens | Medium | Medium | Long conversations |
| Summarisation | Summary + recent | Medium | Low | Very long sessions |
| RAG | Query-relevant chunks | High | Low | Document Q&A |
| KV-cache prefix | Shared prefix cached | High | Low | Repeated system prompts |

**How to choose:** Use full context for precision tasks under 8K tokens. For long documents or multi-session workflows, use RAG to retrieve relevant chunks rather than stuffing the full document — it's cheaper and often more accurate because irrelevant text adds noise.

---

### 🔁 Flow / Lifecycle

```
Request arrives
    ↓
[Budget allocation]
  System prompt: fixed tokens
  History: sliding/summarised
  Retrieved context: RAG chunks
  User query: variable
  Output reserve: N tokens
    ↓
[Window check]
  Total < limit → proceed
  Total > limit → truncate / error / chunk
    ↓
[LLM inference]
  Full attention over window
    ↓
[Output generation]
  Token appended to window each step
  Window shrinks by 1 output token each step
    ↓
[Response complete or context exhausted]
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More context always means better answers" | Irrelevant tokens add noise and cost; focused context often outperforms a stuffed window |
| "The model remembers previous conversations" | Each API call is stateless; conversation history must be manually re-injected into the context |
| "Context window = maximum response length" | Context window includes BOTH input AND output; the output budget is whatever remains after the input |
| "Truncation only affects the end of the input" | Many implementations truncate the beginning (older messages), not the end; strategy varies by SDK |
| "Larger window = better model" | Window size is an engineering choice; a smaller model with a larger window can underperform a larger model with a smaller window on complex reasoning |

---

### 🚨 Failure Modes & Diagnosis

**Lost System Prompt**

**Symptom:** The model stops following instructions mid-conversation; persona drift; safety guardrails ignored.

**Root Cause:** The system prompt was at the beginning of the context and was evicted by a sliding-window strategy that removes oldest tokens first.

**Diagnostic Command / Tool:**
```bash
# Log token counts per role
print(f"System: {count_tokens(system_prompt)}")
print(f"History: {sum(count_tokens(m) for m in history)}")
print(f"Total: {total_tokens}")
```

**Fix:** Always preserve the system prompt; only evict user/assistant messages. Implement a "pinned prefix" strategy.

**Prevention:** Treat system prompt as a protected budget allocation that is never evicted.

---

**Context Overflow API Error**

**Symptom:** `openai.BadRequestError: context_length_exceeded` or `400 Bad Request`.

**Root Cause:** Total token count of messages + expected output exceeds model limit.

**Diagnostic Command / Tool:**
```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4")
total = sum(len(enc.encode(m["content"]))
            for m in messages)
print(f"Total tokens: {total}")
```

**Fix:** Implement context budget management (see Code Example 2). Truncate or summarise history before sending.

**Prevention:** Always count tokens on the client side before every API call.

---

**Needle-in-a-Haystack Degradation**

**Symptom:** The model correctly answers questions about the beginning and end of a long document but misses information in the middle.

**Root Cause:** Empirical finding — LLMs attend more strongly to the beginning and end of the context window ("primacy/recency bias"). Information in the middle of a very long context is under-attended.

**Diagnostic Command / Tool:**
```python
# Test with the "needle in a haystack" benchmark:
# inject a specific fact at various positions and
# test if the model can retrieve it.
```

**Fix:** Use RAG to place the most relevant chunks at the top of the context. Avoid burying critical information in the middle of a long document.

**Prevention:** Design context layout so the most important information is at the start or end of the window.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Token` — context window is measured in tokens, not characters or words
- `Tokenization` — understanding how text maps to tokens is essential for budgeting
- `Transformer Architecture` — attention mechanism is what makes the context window a hard boundary

**Builds On This (learn these next):**
- `In-Context Learning` — few-shot examples must fit within the context window budget
- `Retrieval-Augmented Generation` — RAG exists specifically to work around context window limits
- `Fine-Tuning` — an alternative to large context when the model needs domain knowledge baked in

**Alternatives / Comparisons:**
- `Embedding` — long-term memory strategy: compress content to vectors, retrieve relevant ones into context
- `Hallucination` — context window overflow is a leading cause of LLM hallucination via truncation
- `Model Quantization` — quantized models may have smaller effective context due to precision loss

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Max tokens model can process at once      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Models need bounded memory; infinite      │
│ SOLVES       │ context = infinite compute cost           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Input + output share the same budget;     │
│              │ bigger input = less room to generate      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every LLM call has a context     │
│              │ window that must be managed               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never ignore it — silent truncation is    │
│              │ silent data loss                          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Larger window = more coherence vs         │
│              │ quadratic compute cost per request        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The desk metaphor: only what's on the    │
│              │ desk can be used — everything else is     │
│              │ invisible."                               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tokenization → RAG → In-Context Learning  │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are building a customer support chatbot that maintains conversation history. After 50 turns, the context window is full. Your sliding-window strategy evicts the oldest messages. A user in turn 51 references a specific order number they mentioned in turn 2. Trace step-by-step what happens: what does the model see, what will it say, and what architectural change would prevent this failure?

**Q2.** Two models: Model A has a 128K-token context window; Model B has a 4K-token context window but uses RAG with a vector database. For a task that requires synthesising information from a 200-page technical specification, under what conditions does Model B outperform Model A in both accuracy and cost — and what property of the task determines which approach wins?
