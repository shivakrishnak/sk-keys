---
id: AIF-047
title: "AI Architecture Strategy (Build vs Buy vs Fine-Tune)"
category: AI Foundations
tier: tier-8-artificial-intelligence
folder: AIF-ai-foundations
difficulty: ★★★
depends_on: AIF-001, AIF-006, AIF-019, AIF-029, AIF-042
used_by: AIF-048, AIF-056
related: AIF-048, AIF-056, AIF-057
tags:
  - ai
  - architecture
  - advanced
  - bestpractice
  - tradeoff
status: complete
version: 4
layout: default
parent: "AI Foundations"
grand_parent: "Technical Dictionary"
nav_order: 47
permalink: /aif/ai-architecture-strategy-build-vs-buy-vs-fine-tune/
---

# AIF-047 - AI Architecture Strategy (Build vs Buy vs Fine-Tune)

⚡ TL;DR - The most consequential AI decision: whether to call a third-party API (Buy), adapt an existing model (Fine-Tune), or train your own (Build) - each trades cost, latency, control, and competitive differentiation differently.

| #047 | Category: AI Foundations | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | What Is AI, Machine Learning Basics, Open Source vs Proprietary Models, Fine-Tuning, Foundation Models | |
| **Used by:** | ML Platform Engineering Design, AI Trade-off Framing | |
| **Related:** | ML Platform Engineering Design, AI Trade-off Framing, Model Selection Mental Model | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A fintech startup in 2023 needs an AI feature to classify transaction descriptions. The team debates for three months: should they train a neural network from scratch? Use GPT-4 via API? Fine-tune an open-source model? Nobody has a framework to evaluate the decision. They choose "build from scratch" because it sounds more rigorous. Six months later: $400k in ML engineer salaries, a model that is still 15% worse than GPT-4 on their task, and a competitor shipped the same feature in three weeks using an API.

**THE BREAKING POINT:**
Without a structured framework, teams make AI architecture decisions based on instinct, hype, or HN discourse rather than cost-benefit analysis. The "build" option feels rigorous but destroys timelines. The "buy" option feels fast but creates API dependency, data privacy risk, and cost at scale. The "fine-tune" option is misunderstood as always cheaper. All three are correct in the right context; most teams choose wrong by defaulting to the most familiar path.

**THE INVENTION MOMENT:**
As AI capabilities commoditized through foundation models (GPT, Llama, Gemini) and the "buy via API" path became viable for production, the build/buy/fine-tune decision became a first-class architectural concern. MLEs at major tech firms codified the decision framework around 2022-2023 as the cost of the wrong choice became measurable. This is exactly why the Build vs Buy vs Fine-Tune framework exists.

---

### 📘 Textbook Definition

**AI Architecture Strategy (Build vs Buy vs Fine-Tune)** is the systematic framework for selecting between three fundamental approaches to AI capability acquisition: **Build** (train a custom model from scratch on proprietary data), **Buy** (consume AI capabilities through third-party API or licensed model), and **Fine-Tune** (adapt a pre-trained foundation model to a specific domain using task-specific data). The decision is multidimensional, evaluated across axes including: data sensitivity, latency requirements, customization depth, cost at scale, time to market, team expertise, and competitive differentiation. Optimal strategy is context-dependent and frequently changes as a product scales from prototype to production to hyperscale.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Choose how to get AI: rent it, customize it, or build it - each is correct in different circumstances.

**One analogy:**
> Imagine you need to serve food at your event. "Buy" is ordering from a restaurant - fast, reliable, expensive per serving. "Fine-Tune" is hiring a chef who uses your recipes and ingredients - more customized, upfront training cost. "Build" is constructing your own kitchen, hiring staff, and developing recipes from scratch - maximum control, enormous investment, only worth it at restaurant scale.

**One insight:**
"Buy" (API) is almost always the right starting point - not because it is always optimal, but because it validates the use case before committing to the cost of customization or building. Most teams that jump to "Build" first are solving an infrastructure problem before they know whether the product works.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every AI capability acquisition strategy trades time, cost, control, and competitive differentiation - no option is Pareto-superior.
2. The best strategy changes as the product matures: early stage favors Buy (speed), mid-stage may favor Fine-Tune (accuracy), hyperscale may favor Build (cost efficiency).
3. Data is the moat: if your data is proprietary and differentiated, the case for Fine-Tune or Build strengthens. If your data is commodity, Buy almost always wins.

**DERIVED DESIGN:**
Given these invariants, a rational decision process must evaluate: what is the current stage (exploration vs. production vs. scale)? What is the quality gap between the commodity model and the task requirement? What is the cost crossover point where API fees exceed model hosting costs? What is the data sensitivity constraint (can data leave your infrastructure)?

**THE TRADE-OFFS:**

| Strategy | Gain | Cost |
|---|---|---|
| Buy (API) | Speed, no ML infra overhead | Vendor dependency, per-token cost, data privacy exposure |
| Fine-Tune | Domain accuracy lift, lower inference cost than Buy | Dataset curation, training cost, model serving infra |
| Build | Maximum control, proprietary capability, long-run cost efficiency | Enormous time/cost investment, ML research team needed |

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** AI systems genuinely have different cost, latency, and accuracy profiles that vary by approach. This tradeoff is irreducible.
**Accidental:** The difficulty of evaluating the choice comes largely from poor tooling (no standard cost modeling), unclear evaluation metrics, and AI hype biasing teams toward overcomplicated solutions.

---

### 🧪 Thought Experiment

**SETUP:** A healthcare company needs to extract medication names from clinical notes. They have 50,000 de-identified examples with annotations. GPT-4 achieves 91% F1 score zero-shot. Their regulatory requirement: no PHI can leave their infrastructure.

**WITHOUT A DECISION FRAMEWORK:**
The team defaults to "Build from scratch" because it sounds safe and rigorous. They train a BERT-based NER model. After 4 months: 87% F1 (worse than GPT-4 zero-shot). They've spent $200k. The regulatory team is satisfied because data never left. But the model underperforms, and they now have a permanent maintenance burden.

**WITH A DECISION FRAMEWORK:**
Framework analysis: data cannot leave infrastructure (Buy API is ruled out). They have 50k labeled examples (fine-tuning is viable). They need >91% F1 (GPT-4 baseline). Decision: Fine-tune a self-hosted Llama-3 or Mistral model on their 50k examples. Result: 94.3% F1, runs on-premises, inference cost is 1/20th of GPT-4 API, 6-week project vs 4-month build.

**THE INSIGHT:**
The framework eliminates Options that violate hard constraints first (Buy, due to PHI), then evaluates the remaining options against quality and cost targets. Fine-tune is often the "Goldilocks" option: faster than Build, more accurate and cheaper at scale than Buy - but only when labeled data exists.

---

### 🧠 Mental Model / Analogy

> Think of it as the "make vs buy" decision in manufacturing, applied to AI. A car manufacturer doesn't build their own steel mills (that's "Build from scratch"). They don't buy pre-assembled engines with no modifications (that's "Buy"). They buy raw engine blocks and customize them for their vehicle line (that's "Fine-Tune"). The optimal strategy depends on volume (how many units?), differentiation (is the engine a competitive advantage?), and control (can you afford supply chain risk?).

- "Building your own steel mill" → Training a model from scratch (justified only at Google/OpenAI scale)
- "Buying ready-made parts" → Calling GPT-4 or Claude API (justified early-stage, prototype, low volume)
- "Customizing a base component" → Fine-tuning Llama or Mistral on your data (justified when accuracy/cost/privacy requires it)
- "Volume threshold" → The scale point where API cost exceeds hosting + fine-tuning cost

Where this analogy breaks down: unlike manufacturing, AI capabilities improve rapidly, so the "make vs buy" calculus can change year-over-year as foundation model quality and API pricing shift.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When building an AI feature, you have three choices: pay to use someone else's AI (Buy), train your own from scratch (Build), or take an existing AI and customize it for your specific job (Fine-Tune). Each has different costs, speeds, and control tradeoffs.

**Level 2 - How to use it (junior developer):**
Start with Buy (API call to OpenAI, Anthropic, or Google). Use this to validate that AI can solve your problem at all and to establish a performance baseline. Only move to Fine-Tune when you have labeled data and a clear accuracy or cost gap. Only consider Build when you have hundreds of millions of examples, need maximum IP protection, or operate at hyperscale where API costs dwarf hosting costs.

**Level 3 - How it works (mid-level engineer):**
The decision has five key axes: (1) **Data privacy** - can your data leave your infra? If no, Buy is often ruled out. (2) **Accuracy gap** - does the off-the-shelf model meet your quality bar? If yes, Buy. If no, can fine-tuning close the gap? (3) **Cost at scale** - calculate the API cost at your target volume and compare to self-hosting. (4) **Latency** - API calls add 100-2000ms network overhead; self-hosted can be <50ms. (5) **Differentiation** - if the AI is your product moat, proprietary training data and custom models are critical.

**Level 4 - Why it was designed this way (senior/staff):**
The framework reflects the economic reality of AI in 2024: foundation models have commoditized general AI capability, making "Build from scratch" economically irrational for most use cases. The innovation is in data curation, fine-tuning techniques (LoRA, QLoRA), and eval frameworks - not in reinventing transformers. The interesting design tension is between the first-mover cost of fine-tuning (dataset, training compute, serving infra) versus the ongoing variable cost of API calls. At ~1 million API calls/day to GPT-4 Turbo, the monthly cost often exceeds the one-time cost of fine-tuning a smaller model that matches quality.

**Level 5 - Mastery (distinguished engineer):**
Master-level thinking applies the framework dynamically: strategy evolves with product maturity. Prototype → Buy (move fast, establish baseline). Series A → Fine-Tune on first-party data (improve accuracy, reduce cost, build data moat). IPO-scale → Selective Build for highest-differentiation capabilities, Buy for commodity (e.g., build proprietary ranking model, buy commodity summarization). Red flag for misuse: teams that choose Build prematurely (ego-driven "we need our own model") or teams that never migrate from Buy despite API costs that dwarf engineering costs of migration. Staff engineers recognize this pattern and enforce cost modeling as a precondition to any AI architecture decision.

---

### ⚙️ How It Works (Mechanism)

**DECISION ALGORITHM:**

```
Step 1 - HARD CONSTRAINT CHECK:
  Can data leave your infrastructure?
    NO → eliminates Buy (public API)
         forces choice between Fine-Tune (self-hosted)
         or Build
  Regulatory requirement (HIPAA, GDPR data residency)?
    YES → same constraint; self-hosted only

Step 2 - BASELINE QUALITY CHECK:
  Evaluate best available off-the-shelf model on
  your task with zero-shot or few-shot prompting.
  Does it meet your quality bar (F1, accuracy,
  business metric)?
    YES + no privacy concern → BUY (proceed with API)
    NO → quantify the gap; go to Step 3

Step 3 - FINE-TUNE FEASIBILITY:
  Do you have labeled training data?
    < 1,000 examples → few-shot prompting (Buy)
    1,000 - 100,000 → fine-tuning viable
    > 100,000 → fine-tuning strongly preferred
  Can fine-tuning close the quality gap?
    YES → FINE-TUNE
    NO (gap too large, task too novel) → BUILD

Step 4 - COST CROSSOVER ANALYSIS:
  API cost per day = (requests * avg_tokens * price/token)
  Self-hosting cost = (GPU hours/day) + (engineering overhead)
  If API_cost > Self_host_cost: FINE-TUNE or BUILD
  If API_cost < Self_host_cost: BUY (unless privacy/quality)

Step 5 - TEAM CAPABILITY CHECK:
  Do you have MLEs who can maintain fine-tuned models?
    NO → Buy or defer Fine-Tune
  Do you have ML researchers for novel architecture work?
    NO → eliminate Build; Fine-Tune is your ceiling
```

**COST MODELING EXAMPLE (illustrative):**

```
Scenario: 500K API calls/day, avg 2000 tokens each

Buy (GPT-4 Turbo, ~$0.01/1K tokens input):
  500K * 2000 tokens * $0.01/1K = $10,000/day
  = $300,000/month

Fine-Tune (self-hosted Llama-3 70B on 2x A100):
  GPU: 2 * $3/hr * 24hr = $144/day
  Engineering: $500/day amortized over 2 years
  Total: ~$650/day = $19,500/month
  Quality: comparable or better for domain task

Crossover point at this volume:
  $300K/month (Buy) vs $20K/month (Fine-Tune)
  → Fine-Tune saves $280K/month
  → Fine-Tune investment (dataset + training): ~$50K one-time
  → ROI: <1 month payback
```

---

### 🔄 The Complete Picture - End-to-End Flow

**STRATEGY EVOLUTION OVER PRODUCT LIFECYCLE:**

```
STAGE 1 - EXPLORATION (Prototype)
  Goal: validate AI solves the problem
  ┌──────────────────────────────────┐
  │ Call GPT-4 API ← YOU ARE HERE   │
  │ Zero-shot or few-shot prompt     │
  │ Measure baseline quality         │
  └──────────────────────────────────┘
  Cost: $100-$1000/month
  Timeline: 1-4 weeks

STAGE 2 - PRODUCTION V1 (Launch)
  Goal: reliable, cost-managed production
  ┌──────────────────────────────────┐
  │ Buy: continue API if quality met │
  │ Fine-Tune: if gap or cost        │
  │            pressure ← YOU ARE   │
  │            HERE for many apps    │
  └──────────────────────────────────┘
  Cost: $5K-$50K/month
  Timeline: 1-3 months

STAGE 3 - SCALE (Product-Market Fit)
  Goal: cost efficiency + differentiation
  ┌──────────────────────────────────┐
  │ Fine-Tune: self-hosted           │
  │ Build: highest-value components  │
  │        only ← YOU ARE HERE       │
  │        for FAANG-scale           │
  └──────────────────────────────────┘
  Cost: $50K-$500K/month infra
  Timeline: 6-18 months per component
```

**FAILURE PATH:**
Buy-only at scale → API cost exceeds infra cost by 10x → budget crisis → emergency Fine-Tune project under pressure → rushed quality → model quality regression.

**WHAT CHANGES AT SCALE:**
At 10x volume, API costs often force Fine-Tune as the economically rational choice. At 100x volume, highly customized use cases may justify selective Build for the core IP. At 1000x (hyperscale), full Build becomes viable only for the largest tech companies; most companies still use Fine-Tune + Buy for commodity tasks.

---

### 💻 Code Example

**Example 1 - Cost modeling before committing to a strategy:**

```python
# Simple cost model: Buy vs Fine-Tune crossover analysis
# (Illustrative - actual costs vary by provider and model)

def cost_model_buy_vs_finetune(
    daily_requests: int,
    avg_tokens_per_request: int,
    api_price_per_1k_tokens: float = 0.01,  # GPT-4 Turbo
    gpu_cost_per_hour: float = 3.0,  # A100 80GB
    num_gpus: int = 2,
    engineering_daily: float = 500.0   # amortized MLE time
) -> dict:
    # Buy cost
    daily_tokens = daily_requests * avg_tokens_per_request
    buy_daily = (daily_tokens / 1000) * api_price_per_1k_tokens
    buy_monthly = buy_daily * 30

    # Fine-Tune self-host cost
    gpu_daily = gpu_cost_per_hour * 24 * num_gpus
    ft_daily = gpu_daily + engineering_daily
    ft_monthly = ft_daily * 30

    # One-time fine-tune investment (dataset + training)
    ft_one_time = 50_000  # rough estimate

    months_to_roi = ft_one_time / max(
        buy_monthly - ft_monthly, 1)

    return {
        "buy_monthly_usd": round(buy_monthly),
        "finetune_monthly_usd": round(ft_monthly),
        "monthly_savings": round(buy_monthly - ft_monthly),
        "months_to_roi": round(months_to_roi, 1),
        "recommendation": (
            "Fine-Tune" if buy_monthly > ft_monthly
            else "Buy"
        )
    }

# Example: 500K requests/day, 2K tokens each
result = cost_model_buy_vs_finetune(
    daily_requests=500_000,
    avg_tokens_per_request=2_000
)
# Result:
# buy_monthly_usd: 300000
# finetune_monthly_usd: 19500
# monthly_savings: 280500
# months_to_roi: 0.2
# recommendation: Fine-Tune
```

**Example 2 - Evaluating the quality gap before Fine-Tuning:**

```python
# Before committing to Fine-Tune:
# measure the quality gap between Buy and the threshold

# BAD: commit to fine-tuning without baseline measurement
# - No data on whether quality gap exists
# - Risk: fine-tune may not improve enough
# - Wastes weeks before discovering the task is hard

# GOOD: establish baseline with Buy before any investment
from openai import OpenAI

def measure_baseline_quality(
    test_cases: list[dict],
    task_prompt: str
) -> float:
    client = OpenAI()
    correct = 0
    for case in test_cases:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": task_prompt},
                {"role": "user",
                 "content": case["input"]}
            ]
        )
        prediction = response.choices[0].message.content
        if prediction.strip() == case["expected"]:
            correct += 1
    return correct / len(test_cases)

# If baseline >= quality_threshold: stay with Buy
# If baseline < quality_threshold: evaluate Fine-Tune
quality_threshold = 0.92
baseline = measure_baseline_quality(test_cases, task_prompt)
if baseline >= quality_threshold:
    print(f"Buy is sufficient: {baseline:.2%} >= "
          f"{quality_threshold:.2%}")
else:
    print(f"Quality gap {quality_threshold - baseline:.2%}: "
          f"evaluate Fine-Tune")
```

---

### ⚖️ Comparison Table

| Strategy | Time to Production | Quality Ceiling | Data Privacy | Cost at Scale | Best For |
|---|---|---|---|---|---|
| **Buy (API)** | Days | Foundation model cap | External API exposure | High (per-token) | Prototypes, low volume, commodity tasks |
| Fine-Tune | Weeks-months | Above Buy with domain data | Self-hosted possible | Low (fixed infra) | Domain-specific tasks with labeled data |
| Build from Scratch | Months-years | Unconstrained | Full control | Very high upfront, low per-unit at scale | Novel AI capabilities, hyperscale, maximum IP control |
| Prompt Engineering (Buy+) | Hours-days | Buy ceiling | Same as Buy | Same as Buy | Quick quality lift before committing to Fine-Tune |

**How to choose:** Start with Buy (API + prompt engineering) to validate quality and establish baselines; move to Fine-Tune when you have >1K labeled examples AND either a quality gap, data privacy requirement, or cost crossover; consider Build only for genuinely novel capabilities or hyperscale economics.

**Decision Tree:**
- Data cannot leave your infra? → Eliminate Buy; choose Fine-Tune or Build
- Fewer than 1,000 labeled examples? → Buy + few-shot prompting
- Quality gap that prompting can't close, AND >1K examples? → Fine-Tune
- Volume > 500K requests/day AND domain-specific? → Fine-Tune (cost-driven)
- Novel capability not achievable by Fine-Tune? → Build (rare case)

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Building from scratch is more rigorous and secure" | Build is only rational when you have proprietary data at scale, novel architecture needs, or hyperscale economics. For most companies, a well-fine-tuned Llama model outperforms a poorly-resourced from-scratch build and is built in 10% of the time. |
| "Fine-Tuning always improves quality over the base model" | Fine-Tuning can DEGRADE quality on tasks outside the fine-tuning domain (catastrophic forgetting) and can underperform the base model if training data is small, noisy, or misaligned with the task. Always evaluate on a held-out test set. |
| "Buy means you're not doing real AI engineering" | Buy is a rational architectural choice. Spotify uses OpenAI APIs for DJ. Notion uses Claude for AI writing features. Leveraging foundation models through APIs is production engineering, not a shortcut. |
| "Once you Fine-Tune, you're locked in forever" | Fine-Tune models should be re-evaluated on a cadence. When a new foundation model version outperforms your fine-tuned model on the target task (increasingly common), switching back to Buy may be optimal. Strategy is not a one-time decision. |
| "RAG is always cheaper than Fine-Tuning" | RAG adds retrieval infrastructure cost and latency. For tasks that require style/behavior changes (not just knowledge injection), Fine-Tuning is often more effective. RAG and Fine-Tuning solve different problems and are often used together. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Premature Build Decision**

**Symptom:** ML team has been working for 6+ months, model quality is still below the GPT-4 zero-shot baseline, engineering cost has exceeded $500K.
**Root Cause:** Team chose "Build from scratch" based on perceived rigor or competitive concern before validating that foundation models can't solve the task. Most NLP, classification, and generation tasks are now solvable by fine-tuning; building from scratch is rarely justified below research-lab scale.
**Diagnostic Command:**
```bash
# Retrospective: what was the GPT-4 zero-shot baseline?
# Run post-hoc evaluation on held-out test set
python evaluate_baseline.py \
  --model gpt-4-turbo \
  --test-set data/test.jsonl \
  --metric f1
# Compare to current custom model performance
```
**Fix:** Pivot to fine-tuning a foundation model using the data collected during the Build attempt. Transfer learning often achieves 95% of the Build quality in 10% of the time.
**Prevention:** Mandate baseline evaluation with Buy (GPT-4) before approving any Build project.

**Failure Mode 2: API Cost Explosion at Scale**

**Symptom:** Monthly AI infrastructure bill grows from $5K to $300K in 90 days as product scales. Budget alarm triggered. Emergency architecture review.
**Root Cause:** Team started with Buy (API) for the prototype - correct decision. Never modeled the cost at production scale. No migration plan defined.
**Diagnostic Command:**
```bash
# OpenAI usage dashboard: https://platform.openai.com/usage
# Or query via API:
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"date": "2024-01-15"}'
# Model: daily_tokens * price -> projected monthly cost
```
**Fix:** Emergency migration to self-hosted fine-tuned model. Identify the top-3 highest-volume use cases and prioritize fine-tuning those first.
**Prevention:** At prototype stage, build a cost projection at 10x and 100x volume. Define the migration trigger point (e.g., "when monthly API cost exceeds $50K, initiate fine-tuning sprint").

**Failure Mode 3: Fine-Tuning on Insufficient Data**

**Symptom:** Fine-tuned model has higher training accuracy than base model but lower test accuracy. Model performs well on training examples but fails on real production inputs.
**Root Cause:** Fine-tuned on fewer than 500 labeled examples, or training data doesn't represent real distribution. The model overfit to the small training set (catastrophic forgetting of general capability).
**Diagnostic Command:**
```python
# Compare fine-tuned vs base model on held-out test set
from transformers import pipeline

base = pipeline("text-classification",
    model="mistralai/Mistral-7B-Instruct-v0.2")
finetuned = pipeline("text-classification",
    model="./my-finetuned-model")

base_f1 = evaluate(base, test_set)
ft_f1 = evaluate(finetuned, test_set)
print(f"Base: {base_f1:.3f}, Fine-Tuned: {ft_f1:.3f}")
# If ft_f1 < base_f1: overfit; need more data or Buy
```
**Fix:** Collect more labeled data (target >1,000), apply data augmentation, or fall back to Buy (API) until data is sufficient.
**Prevention:** Minimum 500-1,000 high-quality labeled examples before fine-tuning; always evaluate on a held-out test set not seen during training.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Foundation Models` - you must understand what can be Fine-Tuned or used as Buy before making the Build vs Buy choice
- `Fine-Tuning` - the mechanics of customizing a pre-trained model
- `Open Source vs Proprietary Models` - frames the self-hosted (Fine-Tune) vs API (Buy) choice

**Builds On This (learn these next):**
- `ML Platform Engineering Design` - the infra required once you commit to Fine-Tune or Build
- `AI Trade-off Framing` - broader pattern of capability vs safety vs cost analysis

**Alternatives / Comparisons:**
- `Model Selection Mental Model` - the specific model-level decision within a chosen strategy
- `RAG & Agents` - alternative to Fine-Tuning for knowledge injection; often the first step before Fine-Tune
- `LLM Cost Optimization` - how to reduce Buy costs before justifying migration to Fine-Tune

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Framework for acquiring AI capability:    │
│              │ Build / Buy (API) / Fine-Tune             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Wrong strategy = 10x cost, 10x delay,     │
│ SOLVES       │ or missed quality bar                     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Buy is almost always the correct START;   │
│              │ migrate only when data/cost/privacy       │
│              │ forces it - never upfront ego             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Making any AI capability decision -       │
│              │ run the framework before committing       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Do not use Buy at hyperscale without      │
│              │ modeling crossover cost first             │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ "Build from scratch for rigor" before     │
│              │ proving Buy can't meet the quality bar    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Speed (Buy) vs Cost at scale (Fine-Tune)  │
│              │ vs Control/IP (Build)                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Start with Buy, earn the right to        │
│              │ Fine-Tune, build only when you must."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fine-Tuning → Foundation Models →         │
│              │ ML Platform Engineering Design            │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always establish a Buy baseline before committing to Fine-Tune or Build; most tasks are solvable by prompting a foundation model.
2. The cost crossover from Buy to Fine-Tune occurs around 100K-500K API calls/day for most use cases; model this at prototype stage.
3. Data privacy is the dominant hard constraint: if data cannot leave your infra, Buy (public API) is eliminated by default.

**Interview one-liner:**
"The Build vs Buy vs Fine-Tune decision is driven by four factors: data privacy (can data leave your infra?), quality gap (does the foundation model meet your bar?), cost at scale (does API cost exceed self-hosting?), and competitive differentiation (is the model your moat?). I always start with Buy to establish a baseline, then migrate to Fine-Tune when cost or quality forces it, and only consider Build for genuinely novel capabilities at hyperscale."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The make-vs-buy decision appears in every engineering domain: build a custom database vs use Postgres, run your own Kafka vs use Confluent Cloud, write a custom auth system vs use Auth0. The same framework applies: start with the commodity option to validate the need, migrate when volume, differentiation, or control requirements force it, and never build from scratch for ego or rigor theater.

**Where else this pattern appears:**
- **Infrastructure** - Run your own Kubernetes vs use EKS/GKE/AKS: exact same cost vs control vs speed tradeoff
- **Databases** - Build a custom store vs use Postgres vs use a managed cloud DB: commodity first, build for differentiation only
- **Authentication** - DIY auth vs Auth0/Cognito vs enterprise IdP: security risk of Build makes Buy even more compelling

**Industry applications:**
- **Healthcare AI** - Privacy requirements often mandate Fine-Tune on-premises; Whisper fine-tuned on medical vocabulary outperforms GPT-4 on clinical transcription at 1/50th the cost
- **Finance** - High-frequency trading requires sub-millisecond latency; API (Buy) adds 100ms+ round-trip; custom embeddings (Build) are the only viable option for real-time signal generation

---

### 💡 The Surprising Truth

The most expensive AI architecture decision most companies make is choosing Fine-Tune too early - not too late. Counter-intuitively, the rapid improvement of foundation models means that a model you fine-tuned in 2022 on a task may be outperformed by GPT-4o's zero-shot in 2024, making your Fine-Tune investment a maintenance liability. The winning strategy at many startups is to stay on Buy longer than feels comfortable, use the saved engineering time to build proprietary training data, and Fine-Tune only when the data moat is deep enough to maintain a durable advantage over the next foundation model release.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DECIDE** Given a new AI use case description (domain, data size, privacy requirement, volume), determine the correct strategy in under 10 minutes and justify it with a cost estimate.
2. **DEBUG** Given a project where Fine-Tune model quality is below the base model, diagnose whether the root cause is insufficient data, distribution mismatch, or catastrophic forgetting.
3. **BUILD** Write a cost model comparing Buy vs Fine-Tune for a given request volume, token count, and GPU configuration.
4. **EXPLAIN** Explain to a non-technical product manager why you're starting with GPT-4 API despite it costing more per request than self-hosting would.
5. **EXTEND** Apply the same framework to a non-AI decision: evaluate whether a team should build a custom search engine, use Elasticsearch, or use Algolia, using the same cost/control/quality axes.

---

### 🧠 Think About This Before We Continue

**Q1.** You're the ML lead at a startup that launched with GPT-4 API calls and now processes 2 million requests per day at an average of 1,500 tokens each. The CEO has asked you to reduce AI costs by 60% within the next quarter without reducing quality. Walk through your complete decision process, including what data you would gather in week 1, what experiments you would run, and what infrastructure you would need to stand up. What could go wrong?
*Hint: Think about the difference between replacing a Buy call with a Fine-Tuned model and the quality validation steps required before you can safely redirect production traffic.*

**Q2.** A competitor just released a foundation model that is publicly claiming 5% better F1 than your fine-tuned model on the exact benchmark your team uses to evaluate your product's core AI feature. Your model took 6 months to build and required 200K labeled examples. How do you decide whether to switch to the competitor's API, fine-tune their open-source variant, or stay the course? What questions do you need answered before making the decision?
*Hint: Consider what dimensions the benchmark measures vs. what your production task actually requires, and how switching costs interact with the claimed quality improvement.*

**Q3.** Build a simple evaluation harness for the following scenario: you have 500 production examples with human-verified correct outputs for a text classification task. Design the experiment to determine whether (a) GPT-4 zero-shot, (b) GPT-4 with 10 few-shot examples, (c) a fine-tuned Mistral-7B on 400 of the examples, correctly meets a 92% accuracy threshold. What metrics would you track beyond accuracy? How would you handle disagreements between automated eval and human eval?
*Hint: Think about the role of inter-annotator agreement, calibration, and the difference between accuracy on clean test sets vs. production distribution.*

---

### 🎯 Interview Deep-Dive

**Q1: A product manager asks you to add an AI feature to classify customer support tickets into 12 categories. You have 5,000 historical labeled tickets and access to GPT-4 API. What do you do first?**
*Why they ask:* Tests whether the candidate defaults to "build a model" or applies the decision framework systematically.
*Strong answer includes:*
- Start by evaluating GPT-4 zero-shot and few-shot (10 examples) on a held-out test set of 500 tickets
- If GPT-4 achieves the quality bar (e.g., >90% accuracy): use Buy (API) immediately - no training needed
- If GPT-4 doesn't meet the bar: fine-tune a smaller model (Mistral-7B or similar) on the 4,500 training examples
- Cost model: 5,000 support tickets/day at avg 300 tokens = ~$450/month at GPT-4 Turbo pricing; likely cheaper to stay Buy than self-host

**Q2: Your team's AI cost just hit $150K/month on a classification task. Leadership wants to reduce it. How would you approach the migration from Buy to Fine-Tune?**
*Why they ask:* Tests practical migration planning and risk management.
*Strong answer includes:*
- Step 1: Identify the highest-volume use case (likely 20% of calls = 80% of cost) and fine-tune for that specific task first
- Step 2: Build evaluation infrastructure - held-out test set, quality metrics, shadow traffic comparison
- Step 3: Fine-tune a self-hosted Llama or Mistral model on the task; target inference latency <100ms
- Step 4: Run shadow traffic (send same request to both Buy and Fine-Tune, compare outputs offline) before routing production traffic
- Risk: fine-tuned model may underperform on edge cases; define rollback criteria before launch

**Q3: When would you recommend against fine-tuning and instead stay with Buy (API), even at high volume?**
*Why they ask:* Tests nuanced judgment - the framework has exceptions.
*Strong answer includes:*
- When the quality gap can be closed by better prompting (cheaper than fine-tuning infrastructure)
- When the task requires broad, general knowledge that fine-tuning would degrade (e.g., open-ended reasoning, code generation for arbitrary languages)
- When foundation model capabilities are advancing faster than your fine-tuning cadence (you'd be re-fine-tuning every 3 months)
- When the volume doesn't justify the engineering overhead of model serving, monitoring, and retraining pipelines

**Q4: How do you know when it's time to move from Fine-Tune to Build (training from scratch)?**
*Why they ask:* Tests understanding of when the most expensive option is justified.
*Strong answer includes:*
- When you have a genuinely novel architecture need that no foundation model supports (rare: e.g., custom molecular biology prediction)
- When you have 100M+ proprietary labeled examples that give durable quality advantage over any fine-tuned public model
- When the inference scale is Google/Meta-level (billions of requests/day) where custom architecture delivers meaningful per-unit cost reduction
- When IP protection is paramount and self-hosted Fine-Tune is still insufficient (e.g., military, sovereign AI requirements)
- For most companies: never. Build is OpenAI's and Google's job. Fine-Tune is your job.
