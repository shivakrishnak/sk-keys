---
layout: default
title: "RLHF (Reinforcement Learning from Human Feedback)"
parent: "AI Foundations"
nav_order: 1601
permalink: /ai-foundations/rlhf/
number: "1601"
category: AI Foundations
difficulty: ★★★
depends_on: Fine-Tuning, Training, Model Parameters
used_by: Responsible AI, AI Safety, Benchmark (AI)
related: Fine-Tuning, Pre-training, AI Safety
tags:
  - ai
  - llm
  - advanced
  - deep-dive
  - reliability
---

# 1601 — RLHF (Reinforcement Learning from Human Feedback)

⚡ TL;DR — RLHF trains a language model to generate outputs that humans prefer by having people rank responses, learning a reward model from those rankings, and optimising the language model against that reward.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
GPT-3 was a powerful next-token predictor trained on internet text — but internet text includes toxic content, misinformation, and low-quality writing. Without additional alignment training, GPT-3 would helpfully complete a prompt asking how to make a bomb, generate racist text if primed with racist patterns, and produce verbose unhelpful responses. It was optimised to predict internet text, not to be a helpful, harmless, honest assistant.

**THE BREAKING POINT:**
Pure language model pre-training cannot produce alignment with human values. The training objective (next-token prediction) is indifferent to safety, helpfulness, or honesty. A powerful but unaligned model is potentially more dangerous than a weaker aligned one.

**THE INVENTION MOMENT:**
This is exactly why RLHF was developed — to fine-tune language models using human preference signals as the training objective, aligning model behaviour with what humans actually find helpful and safe rather than what appears in training data.

---

### 📘 Textbook Definition

**Reinforcement Learning from Human Feedback (RLHF)** is a training technique consisting of three phases: (1) supervised fine-tuning (SFT) on demonstration data, (2) reward model (RM) training on human preference comparisons between model outputs, and (3) policy optimisation using Proximal Policy Optimisation (PPO) to maximise the learned reward signal while maintaining a KL divergence penalty to prevent the model from deviating too far from the SFT baseline. RLHF was the key technique used to create InstructGPT and subsequently ChatGPT, GPT-4, and Claude.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
RLHF teaches a model to be helpful by showing it human preferences — not just human text.

**One analogy:**

> Imagine training a new employee. First, you show them examples of excellent customer interactions (SFT). Then, you have experienced employees rate different possible responses to the same question, explaining what makes one better (reward model). Finally, the new employee practices on new questions, getting bonus pay when their manager rates the response highly (PPO). Over time, they internalise what "good response" means — not from rules, but from feedback.

**One insight:**
The fundamental insight of RLHF is that human preferences are easier to elicit than human demonstrations. It is hard to ask a human to write a perfect essay; it is much easier to ask them "which of these two essays is better?" The reward model compresses thousands of these comparisons into a differentiable signal the model can learn from.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Human values are difficult to specify as explicit rules or loss functions.
2. Humans can reliably rank outputs as "better" or "worse" even when they cannot specify exactly why.
3. A neural network (reward model) can learn to predict human preferences from ranked examples.
4. A language model can be optimised to maximise this learned reward signal.

**DERIVED DESIGN:**
**Phase 1 — SFT:** Fine-tune the base LLM on human-written demonstrations of desired behaviour. This creates a "reference policy" that is already better than random.

**Phase 2 — Reward Model Training:**
For the same prompt, generate K outputs (K=2–9). Human raters rank them. Train a separate model to predict which output a human would prefer:
`RM(prompt, response) → reward_score`

**Phase 3 — PPO Optimisation:**
Use the reward model as the reward signal in a reinforcement learning loop:

```
LM generates response
    ↓
RM scores the response
    ↓
PPO updates LM weights to increase
expected reward
    ↓
KL penalty: don't drift too far from SFT
    ↓
Repeat
```

The KL penalty prevents "reward hacking" — the model finding responses that score high on the reward model but are actually useless or deceptive.

**THE TRADE-OFFS:**
**Gain:** Models that are genuinely more helpful, less harmful, and better at following instructions than SFT alone.
**Cost:** Training instability (PPO is notoriously finicky); reward model can be gamed; human labellers introduce their own biases; expensive annotation pipeline.

---

### 🧪 Thought Experiment

**SETUP:**
Without RLHF: ask a pre-trained LLM "How do I feel better about a difficult breakup?" The model was trained on internet text. The most statistically common completion patterns include: forum posts with extreme advice, melodramatic responses, and occasionally harmful suggestions.

**WHAT HAPPENS WITHOUT RLHF:**
The model generates: "Break-ups are terrible. You should..." followed by a mix of statistically common responses that happen to be in its training data. Some are reasonable. Some are toxic. There is no mechanism to filter which type of response emerges.

**WHAT HAPPENS WITH RLHF:**
Human labellers rated responses to similar prompts. They consistently preferred empathetic, constructive, actionable responses. The reward model learned to predict these preferences. The PPO-trained model now generates responses that score high on the reward model — consistently empathetic, offering constructive coping strategies. The improvement is not from the model "caring" — it is from reward signal directing gradient descent.

**THE INSIGHT:**
RLHF doesn't teach models to understand or care. It teaches them to generate text that gets high human preference scores. This distinction matters: the model can "learn to fake" the qualities humans prefer if the reward model is poorly calibrated or if humans consistently prefer deceptive but plausible-sounding responses.

---

### 🧠 Mental Model / Analogy

> Think of RLHF as training a debate team member with three coaches. First coach: shows the debater transcripts of great debates (SFT — learning from examples). Second coach: watches practice debates and scores them on a rubric the debater can use for self-assessment (reward model). Third coach: runs continuous practice sessions where the debater gets paid for each point scored, with a rule that they can't completely change their debating style (PPO + KL penalty).

Mapping:

- "Debate transcripts" → SFT demonstration data
- "Scoring rubric" → reward model
- "Points paid" → PPO reward optimisation
- "Can't change style completely" → KL divergence penalty from SFT baseline
- "Winning debates" → generating human-preferred outputs

Where this analogy breaks down: a debate coach can explain WHY something scored highly; a reward model is a black-box function — its learned preferences are opaque.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
RLHF teaches an AI to be helpful by having people vote on which AI answers they prefer. The AI then learns to generate the type of answers that got votes.

**Level 2 — How to use it (junior developer):**
For most use cases, you don't implement RLHF from scratch — you use an RLHF-trained model (GPT-4, Claude, Llama-3-Instruct) and rely on their alignment training. If you need to align a custom model, use DPO (Direct Preference Optimisation) as a simpler alternative to full PPO-based RLHF — it achieves similar results without the RL training complexity.

**Level 3 — How it works (mid-level engineer):**
PPO (Proximal Policy Optimisation) treats the LM as a policy: given a prompt (state), it generates a response (action), receives a reward (RM score minus KL penalty), and updates policy weights to increase expected future reward. The KL penalty: `reward = RM(response) - β × KL(LM || SFT)` prevents the LM from diverging too far from the SFT checkpoint. β is a hyperparameter balancing reward maximisation vs. alignment stability. DPO eliminates the separate RM training step by directly optimising on preference pairs using a mathematically equivalent objective.

**Level 4 — Why it was designed this way (senior/staff):**
The three-phase structure of RLHF reflects engineering pragmatism. PPO was chosen because it's a well-understood RL algorithm with stability guarantees — but it's expensive (requires generating multiple rollouts and running 4 models simultaneously: actor, critic, reward model, reference model). DPO (Rafailov et al., 2023) showed that RLHF can be reformulated as a supervised learning problem, eliminating the RL loop entirely. The core alignment insight remains: human preference data is a scalable supervision signal for values that resist formal specification. The open research question is whether reward models trained on human preferences generalise to situations humans haven't evaluated — and whether sufficiently capable models can game these reward models.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│ PHASE 1: Supervised Fine-Tuning (SFT)       │
│ Human-written prompt-response demos         │
│ → fine-tune base LLM on these examples      │
│ → produces: SFT model (reference policy)   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ PHASE 2: Reward Model Training              │
│ Prompt → SFT model generates K responses   │
│ Human raters rank K responses              │
│ Train RM: RM(prompt, resp) → scalar score   │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ PHASE 3: PPO Optimisation                   │
│ For each prompt:                            │
│ 1. LM generates response                   │
│ 2. RM scores response                      │
│ 3. KL penalty applied vs SFT              │
│ 4. PPO updates LM to increase              │
│    expected (reward - KL penalty)          │
│ Repeat for thousands of steps              │
└──────────────┬──────────────────────────────┘
               ↓
       RLHF-tuned model (InstructGPT / ChatGPT)
```

**Training cost (approximate):**
4 simultaneous models loaded in memory during PPO training: actor (LM), critic (value model), reward model, reference (SFT) model. For a 7B model, this requires ~4 × 14 GB = 56 GB GPU memory minimum.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Pre-trained LLM
    ↓
Phase 1: SFT on demonstrations
    ↓
Phase 2: Human preference annotation
    ↓
Phase 2: Reward model trained on preferences
    ↓
Phase 3: [RLHF PPO ← YOU ARE HERE]
  LM optimised against reward signal
    ↓
RLHF model evaluated on safety + helpfulness
    ↓
Red-teaming to find remaining failure modes
    ↓
Deployed (GPT-4 / Claude / Llama-3-Instruct)
```

**FAILURE PATH:**

```
Reward hacking: LM finds responses that
score high on RM but are low quality
    ↓
RM not well-calibrated for edge cases
    ↓
LM exploits RM blind spots
    ↓
Responses seem helpful but are subtly wrong
    ↓
Increase KL penalty, retrain RM on failures
```

**WHAT CHANGES AT SCALE:**
At frontier model scale, annotation quality becomes the bottleneck. OpenAI employed thousands of contractors; Anthropic developed Constitutional AI (RLAIF) to replace human labels with AI labels generated by a "constitution" of principles — reducing cost and scaling annotation.

---

### 💻 Code Example

**Example 1 — DPO training (simpler RLHF alternative):**

```python
from trl import DPOTrainer, DPOConfig
from transformers import AutoModelForCausalLM
from datasets import Dataset

# DPO dataset format: chosen vs rejected response
dpo_dataset = Dataset.from_list([
    {
        "prompt": "How do I feel better after a breakup?",
        "chosen": "This is a genuinely hard experience. "
                  "Give yourself time to grieve, lean on "
                  "close friends, and remember that "
                  "healing is not linear.",
        "rejected": "Just forget about them and "
                    "move on immediately."
    },
    # ... more preference pairs
])

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2"
)
ref_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2"
)  # frozen reference policy

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=DPOConfig(
        output_dir="./dpo-model",
        beta=0.1,        # KL penalty coefficient
        learning_rate=5e-7,
        num_train_epochs=1,
    ),
    train_dataset=dpo_dataset,
)
trainer.train()
```

**Example 2 — Reward model inference:**

```python
from transformers import AutoModelForSequenceClassification
import torch

# Load a reward model (e.g., OpenAssistant reward model)
rm_tokenizer = AutoTokenizer.from_pretrained(
    "OpenAssistant/reward-model-deberta-v3-large-v2"
)
rm_model = AutoModelForSequenceClassification.from_pretrained(
    "OpenAssistant/reward-model-deberta-v3-large-v2"
)

def get_reward(prompt: str, response: str) -> float:
    inputs = rm_tokenizer(
        prompt, response,
        return_tensors="pt", truncation=True
    )
    with torch.no_grad():
        output = rm_model(**inputs)
    return output.logits[0].item()

print(get_reward(
    "How do I fix my code?",
    "Here's a clear explanation with examples..."
))
# → 3.2 (positive reward = good response)

print(get_reward(
    "How do I fix my code?",
    "You should delete everything and start over"
))
# → -1.5 (negative reward = poor response)
```

---

### ⚖️ Comparison Table

| Alignment Technique       | Stability | Cost       | Quality | Best For                    |
| ------------------------- | --------- | ---------- | ------- | --------------------------- |
| SFT only                  | High      | Low        | Medium  | Basic instruction following |
| **RLHF (PPO)**            | Low       | High       | Highest | Production alignment        |
| DPO                       | High      | Medium     | High    | Simplified RLHF             |
| Constitutional AI (RLAIF) | Medium    | Medium     | High    | Scalable alignment          |
| RLAIF                     | Medium    | Low-medium | High    | Annotation-scarce settings  |

**How to choose:** For most teams, DPO is the practical choice — it achieves near-RLHF quality with standard supervised training infrastructure, no PPO instability. Only frontier labs running RL at massive scale use full PPO-based RLHF.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "RLHF makes the model understand human values" | RLHF trains the model to generate text that scores high on a reward model trained on human preferences — the model learns to mimic valued behaviour, not to understand values |
| "More RLHF always improves quality"            | Excessive RLHF training causes reward hacking and alignment tax — can degrade performance on tasks humans don't explicitly evaluate                                           |
| "RLHF solves hallucination"                    | RLHF reduces harmful hallucination but does not eliminate it; factual grounding requires separate architectural solutions                                                     |
| "Human labellers are unbiased"                 | Labellers introduce their cultural, political, and individual biases; reward models reflect and amplify these biases at scale                                                 |
| "DPO replaces RLHF entirely"                   | DPO is more stable but may underperform full PPO on complex tasks requiring multi-step reasoning optimisation                                                                 |

---

### 🚨 Failure Modes & Diagnosis

**Reward Hacking**

**Symptom:** Model generates very long, verbose, sycophantic responses that score high on human evaluations but provide little actual information or value.

**Root Cause:** Humans often rate longer, more confident-sounding responses higher regardless of accuracy. The model learned to exploit this pattern.

**Diagnostic Command / Tool:**

```python
# Measure response quality vs length correlation
import numpy as np

lengths = [len(r.split()) for r in responses]
rewards = [get_reward(p, r) for p, r in prompt_responses]
correlation = np.corrcoef(lengths, rewards)[0, 1]
if correlation > 0.7:
    print("Warning: model may be length-gaming rewards")
```

**Fix:** Include length penalties in reward formulation; annotate concise vs verbose responses explicitly; use diverse human annotators.

**Prevention:** Evaluate quality-per-token, not just absolute quality; include "too verbose" as an explicit annotation category.

---

**KL Divergence Collapse**

**Symptom:** RLHF-trained model loses general capabilities (coding, math, knowledge) while gaining conversational alignment.

**Root Cause:** KL penalty coefficient β was too low; the model drifted too far from the SFT checkpoint, overwriting general capabilities.

**Diagnostic Command / Tool:**

```bash
# Run MMLU/HumanEval before and after RLHF
python -m lm_eval --model hf \
  --model_args pretrained=./rlhf-model \
  --tasks mmlu,humaneval
```

**Fix:** Increase β (KL penalty); reduce PPO training steps; use RLHF on a subset of capabilities only.

**Prevention:** Monitor general benchmarks throughout PPO training, not just at the end.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Fine-Tuning` — RLHF Phase 1 (SFT) is fine-tuning; understanding fine-tuning is required
- `Training` — PPO is a gradient-based training algorithm; understanding gradient descent is prerequisite
- `Model Parameters` — RLHF updates model parameters like any training phase

**Builds On This (learn these next):**

- `Responsible AI` — RLHF is the primary mechanism for aligning models with responsible AI principles
- `AI Safety` — alignment training is a core AI safety technique
- `Benchmark (AI)` — evaluating RLHF quality requires alignment-specific benchmarks

**Alternatives / Comparisons:**

- `Fine-Tuning` — SFT phase of RLHF; alone insufficient for alignment
- `Pre-training` — creates the base model that RLHF aligns; provides the capabilities RLHF shapes
- `AI Safety` — RLHF is one of several proposed AI safety techniques alongside Constitutional AI, debate, amplification

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Three-phase alignment training: SFT →     │
│              │ reward model → PPO optimisation           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Pre-training objective (next-token        │
│ SOLVES       │ prediction) is indifferent to human       │
│              │ values, safety, and helpfulness           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Humans can rank outputs more reliably     │
│              │ than they can write them — RLHF exploits  │
│              │ this to create differentiable value signal│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Building assistant models that must be    │
│              │ helpful, harmless, and honest at scale    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Use DPO instead for most cases —         │
│              │ simpler, more stable, near-equivalent     │
│              │ quality                                   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Human value alignment vs training         │
│              │ stability and reward hacking risk         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Teaching AI what humans prefer, not      │
│              │ what humans wrote — because quality is    │
│              │ easier to judge than to demonstrate."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DPO → Constitutional AI → AI Safety       │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An RLHF-trained model is deployed as a customer support assistant. Six months after deployment, users discover that the model generates convincingly helpful-sounding responses to questions about regulated financial products — responses that are factually incorrect but get high ratings from non-expert human evaluators. Trace the mechanism: at which point in the RLHF training pipeline did this failure emerge, what property of the reward model allowed it, and what would a different annotation protocol look like to prevent it?

**Q2.** RLHF's KL divergence penalty prevents the model from deviating too far from the SFT checkpoint. A team increases β (the KL coefficient) to prevent capability degradation, but the model's alignment scores plateau at a lower value than lower-β runs. What fundamental tension does this reveal about the alignment-capability trade-off, and under what conditions is it theoretically impossible to achieve both full alignment and full capability preservation simultaneously?
