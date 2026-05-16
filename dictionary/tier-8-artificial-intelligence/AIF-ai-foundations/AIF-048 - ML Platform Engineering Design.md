---
id: AIF-048
title: ML Platform Engineering Design
category: AI Foundations
tier: tier-8-artificial-intelligence
folder: AIF-ai-foundations
difficulty: ★★★
depends_on: AIF-006, AIF-028, AIF-029, AIF-036, AIF-047
used_by: AIF-049, AIF-062
related: AIF-047, AIF-062, AIF-056
tags:
  - ai
  - mlops
  - architecture
  - advanced
  - production
status: complete
version: 4
layout: default
parent: "AI Foundations"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /aif/ml-platform-engineering-design/
---

# AIF-048 - ML Platform Engineering Design

⚡ TL;DR - An ML platform is the internal infrastructure layer that standardizes the full ML lifecycle - data ingestion, feature engineering, training, evaluation, deployment, and monitoring - so ML engineers ship models faster without reinventing infra from scratch.

| #048            | Category: AI Foundations                                                                        | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Machine Learning Basics, Training, Fine-Tuning, Latency vs Throughput, AI Architecture Strategy |                 |
| **Used by:**    | Responsible AI and Bias Mitigation Strategy, AI System Design Patterns                          |                 |
| **Related:**    | AI Architecture Strategy, AI System Design Patterns, AI Trade-off Framing                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An ML team at a mid-size company has 8 data scientists. Each has their own Python environment, their own data loading scripts, their own model training code, their own deployment process. DS-1 trains a recommendation model on a Jupyter notebook and emails the `.pkl` file to the platform team to deploy. DS-2 wrote custom feature engineering code in a private repo. DS-3's model works on their laptop but fails in production because the inference container has a different library version. Nobody can reproduce last quarter's model. Nobody knows what data was used to train the model that's currently in production.

**THE BREAKING POINT:**
Without an ML platform, every model is a snowflake. Reproducibility is impossible. Debugging production failures is archaeology. Onboarding a new MLE takes weeks. The team spends 70% of time on infra and 30% on actual modeling. At 10 MLEs, the coordination overhead consumes the entire productivity gain of growing the team.

**THE INVENTION MOMENT:**
Google published the paper "Hidden Technical Debt in Machine Learning Systems" (2015) that catalogued the infra problems at scale. Uber built Michelangelo (2017), the first documented internal ML platform. By 2019-2022, every major tech company had built or bought an ML platform, and the concepts became standard practice. This is exactly why ML Platform Engineering Design exists as a discipline.

---

### 📘 Textbook Definition

**ML Platform Engineering Design** is the architectural discipline of building or selecting the infrastructure layer that manages the complete ML lifecycle: data management (storage, versioning, feature stores), model development (experiment tracking, reproducibility), training pipelines (distributed training, hyperparameter tuning), model serving (inference infrastructure, A/B testing), and production monitoring (drift detection, performance tracking). An ML platform transforms model development from artisanal one-off work into repeatable, scalable engineering. Major platforms include: MLflow (open-source), Kubeflow (Kubernetes-native), SageMaker (AWS), Vertex AI (GCP), Azure ML, and Weights & Biases (experiment tracking focus).

---

### ⏱️ Understand It in 30 Seconds

**One line:** An ML platform is the assembly line that lets ML engineers ship models as reliably as software engineers ship code.

**One analogy:**

> An ML platform is to model development what CI/CD is to software development. Before CI/CD, deploying code was a chaotic, manual, error-prone process. Before ML platforms, deploying models was the same. CI/CD standardized the software lifecycle; ML platforms standardize the model lifecycle.

**One insight:**
The most valuable component of an ML platform is not training infrastructure - it's the feature store and experiment tracker. Without reproducibility (what data, what features, what hyperparameters produced this model?), every production failure is a mystery and every model improvement is luck.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Models are only reproducible if the full training context (data snapshot, feature transformations, code version, hyperparameters) is captured and versioned.
2. Models degrade over time as data distributions shift - monitoring is not optional, it's load-bearing infrastructure.
3. The cost of model deployment is proportional to how standardized the deployment interface is; bespoke deployments are a linear cost scaling problem.

**DERIVED DESIGN:**
Given these invariants, an ML platform must provide: (1) a **feature store** (centralized, versioned feature computation with point-in-time correct lookups to prevent data leakage), (2) an **experiment tracker** (log every training run with its full context), (3) a **model registry** (versioned artifact store with staging/production lifecycle), (4) a **serving layer** (standardized inference APIs with autoscaling), and (5) a **monitoring layer** (data drift, model performance, data quality alerts).

**THE TRADE-OFFS:**
**Gain:** Reproducibility, speed of model iteration, reduced infra overhead per MLE, faster debugging of production failures.
**Cost:** Platform building is a 6-18 month investment; platform maintenance is a permanent team tax; over-engineering the platform before you have 5+ MLEs creates a complex system with no users.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The ML lifecycle genuinely has more moving parts than software development (data versioning, model versioning, feature consistency, training/serving skew). This complexity cannot be abstracted away.
**Accidental:** Much platform complexity comes from premature generalization - building a platform for 50 MLEs when you have 5, or supporting every possible framework when your team uses only PyTorch.

---

### 🧪 Thought Experiment

**SETUP:** A company's recommendation model accuracy dropped by 8% after a data pipeline change three weeks ago. No alerts fired. The production model was last updated two months ago. The MLE who built it left the company.

**WITHOUT AN ML PLATFORM:**
The new MLE digs through git history to find the training code. They find 4 different versions of the training script. They don't know which version produced the deployed model. The feature engineering code references a database table that was renamed six weeks ago. The training data snapshot was deleted. After two weeks of archaeology, they give up and retrain from scratch - but now the training data has three weeks of bad data in it. The fix takes 6 weeks total.

**WITH AN ML PLATFORM:**
The model registry shows: model version 3.2.1 is deployed, trained on 2024-11-15 using training pipeline run `run-abc123`. The experiment tracker shows the exact data snapshot, feature set version, and code commit hash. The monitoring layer shows data drift in the `user_session_length` feature starting 2024-12-03 - immediately after the pipeline change. Total diagnosis time: 45 minutes. Fix: retrain on pre-drift data. Total resolution: 3 days.

**THE INSIGHT:**
Observability for ML systems is the feature store + experiment tracker + model registry + monitoring layer working together. Any missing component creates a gap that turns minor incidents into multi-week investigations.

---

### 🧠 Mental Model / Analogy

> An ML platform is like a hospital's electronic medical record (EMR) system. Before EMRs, each doctor kept their own notes in their own format; getting a patient's history required calling every previous doctor. With EMR: every procedure, test result, and medication is centrally recorded, versioned, and searchable. A new doctor can understand the patient's complete history in minutes. An ML platform does the same for models: every training run, dataset, feature transformation, and deployment is centrally recorded so any engineer can understand any model's history instantly.

- "Patient record" → Model metadata in the model registry
- "Medical history" → Experiment run lineage in the experiment tracker
- "Lab test results" → Evaluation metrics and benchmark results
- "Prescriptions/treatments" → Training pipeline configurations
- "Doctor notes" → Code commits and training logs

Where this analogy breaks down: unlike medical records, ML platform data is computational and can be used to automatically retrain models, not just passively reviewed.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An ML platform is the shared tooling and infrastructure that lets a team of data scientists and ML engineers develop, track, deploy, and monitor machine learning models without each person reinventing their own workflow from scratch.

**Level 2 - How to use it (junior developer):**
A basic ML platform workflow: log your experiment with MLflow (`mlflow.log_params`, `mlflow.log_metrics`), store your trained model to the model registry (`mlflow.register_model`), promote it to production (`client.transition_model_version_stage`), and deploy via a standardized serving API. The platform handles versioning, artifact storage, and deployment boilerplate.

**Level 3 - How it works (mid-level engineer):**
The five core components interact: the **feature store** provides consistent features at training and serving time (preventing training/serving skew); the **experiment tracker** logs all training runs with their full context; the **model registry** manages model versions and their promotion lifecycle (staging → production → archived); the **serving layer** (e.g., Triton, TorchServe, Seldon) handles autoscaling, batching, and A/B testing; the **monitoring layer** (EvidentlyAI, Arize, WhyLabs) detects data drift and model performance degradation.

**Level 4 - Why it was designed this way (senior/staff):**
The hardest design problem in ML platforms is **point-in-time correctness** in the feature store. Training data must use feature values as they existed at the time of the label event - not their current values. A naive feature join uses today's feature values for historical labels, creating data leakage that makes training accuracy unrealistically high and production accuracy disappointingly low. This requires the feature store to support time-travel queries. Feast, Tecton, and Hopsworks solve this; naive Redis-based feature stores do not.

**Level 5 - Mastery (distinguished engineer):**
ML platform design decisions cascade. Choosing a feature store architecture (online vs offline, push vs pull) determines model serving latency. Choosing experiment tracking granularity (per-step vs per-epoch) determines storage costs. Choosing model packaging format (ONNX vs TorchScript vs Python serialization) determines cross-platform portability. Expert designers make these decisions explicitly and document the tradeoffs; teams that inherit platforms without documentation spend years fighting the consequences of implicit decisions. Red flag: a platform where the feature store and serving layer don't share a feature schema registry - guarantees training/serving skew in production.

---

### ⚙️ How It Works (Mechanism)

**ML PLATFORM COMPONENT INTERACTIONS:**

```
┌─────────────────────────────────────────────────────────┐
│              DATA & FEATURE LAYER                       │
│  Raw Data → Feature Engineering → Feature Store        │
│  (point-in-time correct; online + offline)             │
└────────────────────────┬────────────────────────────────┘
                         │ features
┌────────────────────────▼────────────────────────────────┐
│           TRAINING & EXPERIMENT LAYER                   │
│  Training Pipeline → Experiment Tracker → Model        │
│  (versioned code, data, params, metrics)               │
└────────────────────────┬────────────────────────────────┘
                         │ model artifact
┌────────────────────────▼────────────────────────────────┐
│               MODEL REGISTRY                            │
│  Staging → Validation → Production → Archived          │
│  (human or automated promotion gates)                  │
└────────────────────────┬────────────────────────────────┘
                         │ deploy
┌────────────────────────▼────────────────────────────────┐
│              SERVING LAYER                              │
│  Model Server → API Gateway → A/B Router → Clients     │
│  (autoscaling, canary, shadow traffic)                 │
└────────────────────────┬────────────────────────────────┘
                         │ predictions + feature values
┌────────────────────────▼────────────────────────────────┐
│             MONITORING LAYER                            │
│  Data Drift → Model Drift → Business Metrics → Alerts  │
│  (feeds back to: retrain trigger, feature store)       │
└─────────────────────────────────────────────────────────┘
```

**TRAINING / SERVING SKEW - THE MOST COMMON FAILURE:**

```
Training: feature = user_age (from db at time of training)
Serving:  feature = user_age (from db at inference time)

If the feature pipeline is different between training and
serving, the model sees different feature distributions
and performs worse than in evaluation.

Correct architecture: both training AND serving call the
SAME feature computation in the feature store.
Feature store: stores pre-computed features with timestamps.
Training: reads features at label_time (point-in-time).
Serving: reads features for current request (real-time).
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MODEL FROM IDEA TO PRODUCTION:**

```
Data Scientist → Feature Store ← YOU ARE HERE (feature dev)
    ↓ training data
Training Pipeline → Experiment Tracker ← YOU ARE HERE (exp)
    ↓ model artifact
Model Registry (Staging) → Validation Tests
    ↓ passes validation
Model Registry (Production) ← YOU ARE HERE (promotion)
    ↓ deployment
Model Server (Triton/TorchServe/FastAPI)
    ↓ real-time predictions
A/B Test Router → User Traffic
    ↓ logs
Monitoring Layer → Drift Alert → Retrain Trigger
    ↓ retrain
Back to Training Pipeline (automated retraining loop)
```

**FAILURE PATH:**
Model drift detected → alert fires → on-call MLE investigates → model registry shows last 5 versions → experiment tracker shows training data snapshot → feature store shows drift started 2024-01-15 → root cause: upstream data pipeline change → fix: retrain on post-fix data + roll back serving to v2.1 during retraining.

**WHAT CHANGES AT SCALE:**
At 10x model count, a shared feature store becomes mandatory - 10 teams cannot each maintain their own feature engineering code without consistency breaking down. At 100x request volume, the serving layer needs batch inference, caching, and hardware-accelerated inference (GPU serving). At 1000x, the platform itself needs multi-region deployment and federated model registries per business unit.

---

### 💻 Code Example

**Example 1 - Experiment tracking with MLflow:**

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

mlflow.set_experiment("customer-churn-v2")

with mlflow.start_run(run_name="rf-baseline"):
    # Log all parameters
    params = {"n_estimators": 100, "max_depth": 8,
              "min_samples_split": 10}
    mlflow.log_params(params)

    # Train
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Log metrics
    train_f1 = f1_score(y_train, model.predict(X_train))
    val_f1 = f1_score(y_val, model.predict(X_val))
    mlflow.log_metric("train_f1", train_f1)
    mlflow.log_metric("val_f1", val_f1)

    # Log model with schema
    signature = mlflow.models.infer_signature(
        X_train, model.predict(X_train))
    mlflow.sklearn.log_model(
        model, "model",
        signature=signature,
        registered_model_name="churn-classifier"
    )
    # Now: every run is reproducible. Team can compare runs.
    # Model is registered and tracked in model registry.
```

**Example 2 - Feature store pattern (preventing training/serving skew):**

```python
# BAD: compute features differently in training vs serving
# Training:
user_features = db.query(
    "SELECT age, tenure FROM users WHERE id=?", user_id)

# Serving (different code path - different logic!):
user_age = redis.get(f"user:{user_id}:age")
# SKEW: db.age and redis age may diverge

# GOOD: single feature definition used by both
# feast feature store example:
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Training: point-in-time correct historical features
training_df = store.get_historical_features(
    entity_df=entity_df_with_event_timestamps,
    features=["user_stats:age", "user_stats:tenure"]
).to_df()  # respects event_timestamp for each row

# Serving: same feature definitions, real-time lookup
online_features = store.get_online_features(
    features=["user_stats:age", "user_stats:tenure"],
    entity_rows=[{"user_id": user_id}]
).to_dict()
# Same feature logic, training and serving → no skew
```

---

### ⚖️ Comparison Table

| Platform         | Type                      | Best For                         | Key Strength                         | Main Limitation                       |
| ---------------- | ------------------------- | -------------------------------- | ------------------------------------ | ------------------------------------- |
| **MLflow**       | Open-source               | Small-mid teams, any cloud       | Simple, universal, free              | No built-in feature store             |
| Kubeflow         | Kubernetes-native         | K8s-first orgs                   | Native K8s integration               | Complex setup, steep learning curve   |
| SageMaker        | AWS managed               | AWS-committed orgs               | Full managed, feature store included | AWS lock-in, expensive at scale       |
| Vertex AI        | GCP managed               | GCP-committed orgs               | Best-in-class AutoML integration     | GCP lock-in                           |
| Weights & Biases | SaaS experiment tracker   | Experiment-heavy teams           | Best experiment UI, collaboration    | Limited pipeline/serving capabilities |
| Feast            | Open-source feature store | Teams needing feature store only | Best open-source feature store       | Serving layer not included            |

**How to choose:** For teams <10 MLEs: MLflow + Feast on any cloud (full control, open-source). For AWS teams that want managed infra: SageMaker. For teams that need best-in-class experiment tracking and don't need a full platform: Weights & Biases + separate serving.

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                            |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "MLflow is an ML platform"                                  | MLflow is an experiment tracker and model registry. It is one component of an ML platform, not a complete platform. A full platform also needs a feature store, a training pipeline orchestrator, a serving layer, and a monitoring layer.                                                                                         |
| "We need an ML platform before we build our first model"    | A team of 1-2 MLEs does not need a platform. MLflow + manual deployment is sufficient. Platforms pay off at 5+ MLEs with 3+ models in production. Building a platform before it's needed creates maintenance overhead with no users.                                                                                               |
| "The feature store is optional if we use pandas DataFrames" | The feature store is optional until your first training/serving skew incident. At that point, the cost of debugging, fixing, and retraining often exceeds the cost of building a feature store. It's optional until it's critical.                                                                                                 |
| "Model monitoring = accuracy monitoring"                    | Model monitoring requires: data drift (input feature distribution shift), prediction drift (output distribution shift), data quality (null rates, schema violations), and business metric correlation - not just accuracy. Accuracy monitoring alone is insufficient because labels are often delayed or unavailable in real-time. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Training/Serving Skew**

**Symptom:** Model performs well in offline evaluation (90% accuracy on test set) but much worse in production (75% accuracy). The gap is persistent and not explained by data volume differences.
**Root Cause:** Feature computation in training pipeline uses different logic than feature computation in the serving layer. Common causes: different data sources, different preprocessing order, different null handling, different timestamp handling.
**Diagnostic Command:**

```python
# Log and compare feature statistics at training vs serving time
import evidently
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(
    reference_data=training_features,  # training distribution
    current_data=serving_features      # production distribution
)
report.save_html("drift_report.html")
# Large drift in any feature = likely source of skew
```

**Fix:** Centralize feature computation in a feature store used by both training and serving. Delete all duplicate feature code.
**Prevention:** Feature registry (single source of truth) + automated skew detection in CI pipeline before any model promotion.

**Failure Mode 2: Model Drift Without Detection**

**Symptom:** Business metric (e.g., click-through rate, conversion rate) gradually declines over 2-3 months. Team investigates and discovers the production model was trained 8 months ago on data that no longer reflects current user behavior.
**Root Cause:** No monitoring layer; no automated retraining triggers; model staleness accumulates silently.
**Diagnostic Command:**

```python
# Check model staleness and PSI (Population Stability Index)
# PSI > 0.2 = significant distribution shift
import whylogs

profile = whylogs.log(pandas_df=current_serving_data)
profile.view().to_pandas().to_csv("drift_check.csv")
# Compare to training reference profile
# PSI > 0.2 on any key feature: model retraining required
```

**Fix:** Implement data drift monitoring with automatic retraining trigger when PSI exceeds threshold on critical features.
**Prevention:** Define retraining triggers at model deployment time (time-based: monthly; drift-based: PSI>0.2 on top-5 features; performance-based: metric drops 5% from baseline).

**Failure Mode 3: Experiment Irreproducibility**

**Symptom:** Team runs the "same" experiment twice and gets different results. A previously champion model cannot be reproduced. Production model provenance is unknown (which data, which code, which hyperparameters?).
**Root Cause:** Random seeds not fixed, data snapshots not versioned, code not pinned in experiment metadata, non-deterministic data ordering.
**Diagnostic Command:**

```bash
# Check what MLflow logged for the production model:
mlflow models describe -m models:/churn-model/Production
# Should show: run_id, source_code_commit, data_version
# If any of these are missing: reproducibility is broken

# Check git commit for the run:
mlflow runs get -r <run_id> | grep "mlflow.source.git.commit"
```

**Fix:** Enforce experiment logging standards: always log `random_seed`, `data_version`, `git_commit`, `requirements.txt`, and key hyperparameters. Use MLflow system tags `mlflow.source.git.commit` automatically.
**Prevention:** Mandatory experiment logging checklist in code review; pre-commit hook that validates MLflow run has complete metadata.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Training` - the process the platform orchestrates and tracks
- `Fine-Tuning` - a key workload the platform must support
- `AI Architecture Strategy` - determines which platform components are needed
- `Latency vs Throughput (AI)` - informs serving layer design choices

**Builds On This (learn these next):**

- `Responsible AI and Bias Mitigation Strategy` - platform monitoring enables systematic fairness tracking
- `AI System Design Patterns` - platform patterns compose into larger system designs

**Alternatives / Comparisons:**

- `LLMOps Fundamentals` - the LLM-specific specialization of ML platform concepts (prompt versioning, LLM evaluation pipelines)
- `CI/CD` - the software engineering parallel; ML platforms are "CI/CD for models"

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared infra for the full ML lifecycle:  │
│              │ data → train → evaluate → deploy →       │
│              │ monitor → retrain                        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Reproducibility, training/serving skew,  │
│ SOLVES       │ 70% infra overhead, silent model drift   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Feature store + experiment tracker are   │
│              │ the load-bearing components; serving     │
│              │ and monitoring are also non-optional     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 5+ MLEs, 3+ production models, frequent  │
│              │ retraining, compliance requirements      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Team < 3 MLEs or 1st model not yet in   │
│              │ production (over-engineering risk)       │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Building a platform before you have      │
│              │ users; adding components before needed   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reproducibility + speed vs 6-18 month    │
│              │ platform investment                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CI/CD for models - without it, every   │
│              │ production incident is archaeology."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Feature Store → Model Registry →         │
│              │ LLMOps Fundamentals                      │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Training/serving skew is the most common production failure; the feature store exists specifically to eliminate it.
2. Build platforms when you have 5+ MLEs and 3+ production models; before that, MLflow + manual deployment is sufficient.
3. Model monitoring requires data drift + prediction drift + business metric correlation - not just accuracy tracking.

**Interview one-liner:**
"An ML platform standardizes the full ML lifecycle: feature store (training/serving consistency), experiment tracker (reproducibility), model registry (versioned deployment), serving layer (scalable inference), and monitoring (drift detection). The most underrated component is the feature store - training/serving skew from inconsistent feature computation is the #1 silent production failure mode."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Platforms pay off when the per-unit cost of standardization is lower than the per-team cost of bespoke infra. This pattern applies to every internal developer platform: API gateways, auth systems, deployment platforms. Build the platform for the 80% use case; don't customize for every edge case. The platform is only valuable if teams actually use it - adoption is the key metric, not feature count.

**Where else this pattern appears:**

- **Internal developer platforms (IDPs)** - same standardization argument: build a deployment platform for teams instead of each team managing their own K8s manifests
- **Data platforms** - dbt + data warehouse + data catalog is the same pattern applied to analytics data transformation pipelines
- **Security platforms** - centralized IAM, secret management, vulnerability scanning shared across all services

**Industry applications:**

- **Financial services** - ML platforms with model risk management (MRM) integration are regulatory requirements; the model registry must record model validation, challenger models, and approval workflows
- **Healthcare AI** - FDA-regulated ML requires complete model lineage (which data, which code, which validation tests produced the deployed model); only possible with a platform

---

### 💡 The Surprising Truth

The most expensive component of an ML platform is not the GPU training infrastructure - it is the **feature store**. Building a correct feature store (with point-in-time correct lookups, online + offline consistency, and low-latency serving) requires solving hard distributed systems problems: consistent reads across replicated stores, exactly-once feature materialization, and time-travel queries on petabyte-scale datasets. Uber's Michelangelo team reported that the feature store took longer to build than all other platform components combined. Most teams underestimate this, build a naive Redis cache as their "feature store," and then spend 2 years debugging training/serving skew that the naive cache introduced.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **EXPLAIN** the difference between an experiment tracker and a model registry, and why both are required for reproducibility.
2. **DEBUG** Given a report that a production model's accuracy is 15% below offline evaluation, design a systematic investigation to determine if training/serving skew is the root cause.
3. **DECIDE** Given a team of 4 MLEs with 2 production models, recommend whether to build a feature store now or defer, with explicit criteria for when to revisit.
4. **BUILD** Configure MLflow experiment tracking for a training script, including: logging params, metrics per epoch, model artifact with signature, and git commit hash.
5. **EXTEND** Apply the ML platform concept to an LLM use case: what components change (prompt versioning, evaluation pipelines) and what stays the same (experiment tracking, monitoring, model registry)?

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing the monitoring layer for a fraud detection model that is updated weekly. The model's training data uses transactions from the past 12 months. Define three concrete drift detection signals you would monitor, their thresholds, and the action triggered when each threshold is breached. How do you distinguish between "drift that requires retraining" vs "drift that indicates a data pipeline bug"?
_Hint: Think about the difference between covariate shift (feature distribution change) and concept drift (relationship between features and label changing) and how each manifests in metrics._

**Q2.** Your company is choosing between building an ML platform on top of MLflow + Kubernetes vs adopting AWS SageMaker. You have 8 MLEs, use AWS for all infrastructure, and plan to have 20 production models within 18 months. What information do you need to make this decision? What are the specific conditions under which SageMaker's lock-in cost is acceptable?
_Hint: Consider the make vs buy framework from AIF-047, the total cost of ownership model including engineering time, and what happens if AWS changes SageMaker pricing._

**Q3.** Build a minimal experiment tracking harness for the following scenario: you are running 50 parallel hyperparameter search experiments for a gradient boosted tree model. Design the logging schema (what to log per run), the comparison mechanism (how to identify the best run), and the promotion criteria (what quality bar must be met to register a model). What metadata beyond accuracy would you require before promoting any model to the registry?
_Hint: Think about what a new MLE would need to understand this run 6 months from now, including data provenance, preprocessing decisions, and known failure modes on specific data subsets._

---

### 🎯 Interview Deep-Dive

**Q1: Explain training/serving skew - what causes it and how do you prevent it?**
_Why they ask:_ Tests whether the candidate understands the most common and most costly ML production failure mode.
_Strong answer includes:_

- Training/serving skew: the model is trained on features computed one way but served features computed a different way, causing the model to see a different data distribution in production than in training
- Common causes: different code paths for feature computation, different data sources, different null handling, different preprocessing order, time-based features computed at different points
- Prevention: single feature store used by both training and serving; automated skew detection in CI (compare feature statistics at training time vs serving time); mandatory code review for any feature that is used in both contexts

**Q2: What are the five core components of an ML platform, and what breaks without each one?**
_Why they ask:_ Tests breadth of ML platform knowledge.
_Strong answer includes:_

- Feature store: without it → training/serving skew and inconsistent feature logic
- Experiment tracker: without it → no reproducibility, no debugging history, no model comparison
- Model registry: without it → no deployment lifecycle, no rollback capability, no model governance
- Serving layer: without it → each model has a bespoke deployment with inconsistent scaling and monitoring
- Monitoring layer: without it → model drift is invisible until business metrics collapse (silent failure)

**Q3: A company has 3 data scientists and wants to "build an ML platform." What would you advise?**
_Why they ask:_ Tests judgment about when platform investment is appropriate.
_Strong answer includes:_

- For 3 data scientists with 1-2 production models: don't build a platform; use MLflow for experiment tracking + manual deployment
- Platform ROI requires: 5+ MLEs, 3+ production models, frequent retraining, OR compliance requirements
- Recommendation: adopt MLflow + Feast (feature store) as the minimal effective platform; defer serving layer and custom monitoring until scale justifies it
- The most expensive mistake: building a platform no one uses because the team outgrew the problem before the platform was ready
