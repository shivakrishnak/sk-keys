---
layout: default
title: "Multimodal Models"
parent: "AI Foundations"
nav_order: 1613
permalink: /ai-foundations/multimodal-models/
number: "1613"
category: AI Foundations
difficulty: ★★★
depends_on: Foundation Models, Training, Model Parameters
used_by: Vision Language Models, Foundation Models, RAG
related: Vision Language Models, Foundation Models, In-Context Learning
tags:
  - ai
  - multimodal
  - advanced
  - llm
  - vision
---

# 1613 — Multimodal Models

⚡ TL;DR — Multimodal models process and reason across multiple input modalities — text, images, audio, video — in a unified architecture, enabling tasks that require understanding relationships across data types.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A radiologist needs to describe an X-ray in plain language, cross-reference it with the patient's notes (text), and identify similar historical cases. Three separate AI systems are needed: image classification, text summarisation, and document retrieval. Each produces a separate output; integrating them requires manual work and the relationships across modalities are lost.

**THE BREAKING POINT:**
Real-world reasoning inherently involves multiple modalities. Humans naturally integrate sight, sound, and language — understanding a news clip requires hearing what's said, seeing what's shown, and reading the caption. Systems that handle only one modality cannot match this integrated understanding.

**THE INVENTION MOMENT:**
Multimodal models unify multiple input types in a single neural architecture — enabling cross-modal understanding: "what does this image say about this text?" and "what audio does this transcript describe?" This integration unlocks tasks impossible for unimodal systems.

---

### 📘 Textbook Definition

**Multimodal models** are neural networks designed to process and reason over inputs from multiple data modalities — most commonly text, images, audio, and video — within a unified representation space. Architecturally, multimodal models use modality-specific encoders (e.g., ViT for images, Whisper for audio, a language model for text) that project each modality into a shared embedding space, followed by a cross-modal fusion mechanism (cross-attention, concatenation, or projection layers) that enables joint reasoning. Examples include GPT-4V (vision + text), Gemini Ultra (text, image, audio, video), and DALL-E 3 (text → image generation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Multimodal models understand text AND images AND audio together — like a person who can look at a photo and describe what they see, or hear a song and write its lyrics.

**One analogy:**

> A unimodal model is like a specialist who only reads reports. A multimodal model is like a doctor who can examine the patient directly, read their chart, listen to their symptoms, and look at their X-ray — all at once, integrating everything into a single assessment.

**One insight:**
The fundamental technical challenge is not building separate encoders — it's alignment: ensuring that "a cat" in text and an image of a cat map to nearby points in the shared embedding space. Without alignment, text and image understanding cannot interact.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each modality has unique structure: text is sequential tokens; images are spatial pixel grids; audio is temporal waveforms.
2. For cross-modal reasoning, different modalities must be represented in a shared space where similar meanings are close.
3. The alignment problem: learning that text "cat" and cat image should have similar embeddings requires paired training data.

**ARCHITECTURE:**

```
MULTIMODAL ARCHITECTURE (e.g., GPT-4V):

Image Input          Text Input
     ↓                    ↓
ViT (Vision         LLM Tokenizer
Transformer)         ↓
     ↓            Text Tokens
Image Patches       [embeddings]
[embeddings]           ↓
     ↓                  ↓
Projection Layer    ←───→  Cross-modal fusion
(align image space           (attention over
 with text space)             combined sequence)
                         ↓
               Unified Transformer Backbone
                         ↓
                  Text Output (or image)
```

**TRAINING PARADIGM:**

1. Pretrain modality-specific encoders independently (ViT on ImageNet, LM on text).
2. Align the encoders via contrastive loss on image-text pairs (CLIP style): train such that paired image-text have high cosine similarity; unpaired have low similarity.
3. Fine-tune with multimodal instruction data for downstream tasks.

**THE TRADE-OFFS:**
**Gain:** Tasks that require integrated cross-modal reasoning become possible; single system instead of pipeline of specialists; emergent capabilities (image captioning, visual QA, audio transcription + understanding).
**Cost:** Significantly more expensive to train; harder to evaluate (multiple modality benchmarks needed); hallucination risks compound across modalities; privacy concerns with image/audio inputs.

---

### 🧪 Thought Experiment

**SETUP:**
You have three models: a text-only LLM, a vision-only classifier, and a multimodal model. Task: "This invoice image shows a charge of $847. Is this consistent with the purchase order in this text document? If not, explain the discrepancy."

**UNIMODAL SYSTEMS:**

- Text LLM: cannot see the invoice image.
- Vision classifier: labels the image "invoice" but cannot read specific values or compare to text.
- Both combined: require manual extraction from image, then send to text LLM — losing context about layout, formatting cues, table structure.

**MULTIMODAL MODEL:**
Receives both the image and text simultaneously. Reads specific values from the invoice image in context; cross-references with the purchase order text; identifies: "The invoice shows $847 for 'consulting services' but the purchase order was for $650 for 'technical support.' This is a discrepancy in both amount and category."

**THE INSIGHT:**
The cross-modal reasoning (reading a specific field from an image in the context of a text document) is impossible without shared representation. The emergent capability — comparing specific values across modalities — is not achievable by combining unimodal specialists.

---

### 🧠 Mental Model / Analogy

> A multimodal model is like a polyglot translator who doesn't just translate between languages — they understand the MEANING that transcends the specific language. They hear music and can describe the mood in words; they see a painting and can hum the music it evokes; they read a poem and can sketch the scene it describes. The understanding lives in a shared semantic space, not in any single modality.

Mapping:

- "Polyglot translator" → multimodal model
- "Shared meaning beyond specific language" → joint embedding space
- "Music → words" → audio to text generation
- "Painting → music" → cross-modal retrieval
- "Poem → sketch" → text to image generation

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A multimodal AI can look at pictures AND understand text at the same time — like how you can look at a chart and read its caption together, not separately.

**Level 2 — How to use it (junior developer):**
Using multimodal APIs: pass images as base64 or URL alongside text in the message. OpenAI GPT-4V, Anthropic Claude 3, Google Gemini all accept image inputs via their APIs. For audio, Whisper + GPT-4 is the pipeline; Gemini Pro handles audio natively. Key prompting tip: explicitly instruct the model to describe what it sees before reasoning — reduces hallucination by forcing grounded observation first.

**Level 3 — How it works (mid-level engineer):**
**CLIP alignment:** OpenAI's CLIP (2021) trained ViT-based image encoder and text encoder contrastively on 400M image-text pairs from the internet. After training, image and text embeddings of paired content are close in cosine space. GPT-4V uses a CLIP-like image encoder whose output is projected into the LLM's token embedding space. The image "tokens" (one per image patch) are then concatenated with text tokens and processed by the LLM as a unified sequence. The LLM's attention mechanism handles cross-modal reasoning — an image patch token can attend to a text token and vice versa.

**Level 4 — Why it was designed this way (senior/staff):**
The architectural decision to project images into the text token space (used by LLaVA, GPT-4V, and most modern VLMs) is pragmatic: it reuses the pre-trained LLM without architectural changes. The alternative — training a unified transformer from scratch on all modalities simultaneously — requires orders of magnitude more compute and data. The projection approach (add a linear/MLP projection layer between image encoder and LLM) is data-efficient and achieves near-scratch performance with far less compute. The open research question: how much shared structure do different modalities actually have in their optimal representation spaces? Evidence from joint training suggests significant shared structure — especially between text and image at semantic (not pixel) levels — which is why projection alignment works so well despite being architecturally simple.

---

### ⚙️ How It Works (Mechanism)

```
IMAGE + TEXT INPUT PROCESSING:

Image: [256x256 RGB]
    ↓ ViT encoder (patch size 16x16)
    → 256 patch embeddings [dim=768]
    ↓ Linear projection
    → 256 "image tokens" in LLM embedding space

Text: "Describe the chart"
    ↓ Tokenizer
    → [Describe, the, chart] [dim=768]

Combined sequence:
    [IMG_1][IMG_2]...[IMG_256][Describe][the][chart]
    ↓ LLM forward pass (attention over full sequence)
    → Image patches attend to text; text attends to image
    ↓
    "The chart shows a bar graph with..."
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Multimodal input:
  image + text (+ optional audio/video)
    ↓
Modality-specific encoding:
  image → ViT → patch embeddings
  text → tokenizer → token embeddings
  audio → spectrogram encoder → audio embeddings
    ↓
Projection to shared embedding space
    ↓
[FUSION ← YOU ARE HERE]
Combined token sequence (all modalities)
Unified transformer attention
    ↓
Generate text output (or other modality)
    ↓
Post-processing / structured output
```

---

### 💻 Code Example

**Example 1 — GPT-4V image + text query:**

```python
import base64
import openai

def query_image_and_text(
    image_path: str,
    text_prompt: str,
    client
) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(
            f.read()
        ).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}",
                        "detail": "high"  # high-res processing
                    }
                },
                {
                    "type": "text",
                    "text": text_prompt
                }
            ]
        }],
        max_tokens=1000
    )
    return response.choices[0].message.content
```

**Example 2 — CLIP embeddings for cross-modal retrieval:**

```python
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

def embed_image(image_path: str) -> torch.Tensor:
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        return model.get_image_features(**inputs)

def embed_text(text: str) -> torch.Tensor:
    inputs = processor(text=[text], return_tensors="pt",
                       padding=True)
    with torch.no_grad():
        return model.get_text_features(**inputs)

def text_image_similarity(
    text: str, image_path: str
) -> float:
    """Return cosine similarity between text and image."""
    t_emb = embed_text(text)
    i_emb = embed_image(image_path)
    return torch.cosine_similarity(t_emb, i_emb).item()
```

---

### ⚖️ Comparison Table

| Model               | Modalities                | Architecture                  | Best For                      |
| ------------------- | ------------------------- | ----------------------------- | ----------------------------- |
| GPT-4o              | Text, image, audio        | ViT + LLM                     | General vision-language tasks |
| Gemini Ultra        | Text, image, audio, video | Native multimodal             | Long video understanding      |
| Claude 3 Opus       | Text, image               | ViT projection + LLM          | Document analysis             |
| LLaVA (open source) | Text, image               | ViT + LLaMA                   | Self-hosted VLM               |
| DALL-E 3            | Text → image              | Diffusion + CLIP              | Image generation              |
| Whisper             | Audio → text              | Spectrogram CNN + Transformer | Audio transcription           |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                      |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Multimodal models understand images like humans do" | Models process statistical patterns in pixels; they don't have perceptual experience — they learn correlations between pixel patterns and text descriptions                                  |
| "CLIP alignment is sufficient for visual reasoning"  | Contrastive alignment learns that image and text should be close, but doesn't teach fine-grained reasoning (counting objects, reading text in images) — that requires additional fine-tuning |
| "Multimodal models can process any image resolution" | Most VLMs have fixed patch sizes; very high-resolution images are downscaled or split into tiles — which can lose detail                                                                     |
| "Adding modalities always improves performance"      | Adding poorly aligned modalities can degrade performance; multimodal training requires well-paired data across modalities                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**Cross-Modal Hallucination**

**Symptom:** The model describes details in an image that are not present — invents text that isn't there, describes objects that don't exist, or misreads numbers.

**Root Cause:** The model has strong language priors that override visual evidence. For example, seeing a blurry photo of a whiteboard, the model "reads" text based on what it expects to see rather than what the pixels actually show.

**Diagnostic:**

```python
def test_visual_grounding(
    model,
    image_path: str,
    known_facts: list[str],
    expected_absent: list[str],
    client
) -> dict:
    """Test whether model reports only what's in the image."""
    prompt = (
        "Look at this image carefully. "
        "List ONLY what you can see. "
        "Do not infer or assume anything not visible."
    )
    response = query_image_and_text(image_path, prompt, client)

    present_correct = sum(
        1 for f in known_facts if f.lower() in response.lower()
    )
    hallucinated = sum(
        1 for f in expected_absent if f.lower() in response.lower()
    )
    print(f"Correct facts: {present_correct}/{len(known_facts)}")
    print(f"Hallucinated: {hallucinated}/{len(expected_absent)}")
    return {"correct": present_correct, "hallucinated": hallucinated}
```

**Fix:** Use "describe what you see first, then reason" prompting. Use temperature=0. Verify critical values extracted from images with explicit re-confirmation prompts.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Foundation Models` — multimodal models are a class of large foundation models
- `Training` — multimodal training requires specialised paired datasets
- `Model Parameters` — multimodal models have higher parameter counts due to multiple encoders

**Builds On This (learn these next):**

- `Vision Language Models` — a specific class of multimodal models focused on vision-language tasks
- `Foundation Models` — multimodal models are the next frontier of foundation model development
- `Retrieval-Augmented Generation` — RAG can retrieve images as well as text for multimodal grounding

**Alternatives / Comparisons:**

- `Vision Language Models` — a specific subset of multimodal models (vision + language only)
- `Foundation Models` — the broader category; multimodal models are a subcategory
- `In-Context Learning` — multimodal models extend ICL to include visual demonstrations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Models that process text, images, audio   │
│              │ together in a unified architecture        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cross-modal reasoning requires alignment: │
│              │ image "cat" and text "cat" must map to    │
│              │ nearby embedding space points             │
├──────────────┼───────────────────────────────────────────┤
│ ARCHITECTURE │ Modality encoders → projection to shared  │
│              │ embedding space → unified transformer →   │
│              │ output generation                         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Tasks requiring understanding across      │
│              │ modalities: document analysis, visual QA, │
│              │ image generation from text                │
├──────────────┼───────────────────────────────────────────┤
│ FAILURE MODE │ Cross-modal hallucination: language prior │
│              │ overrides visual evidence                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The AI that can look AND read at once —  │
│              │ integrating sight and language naturally."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Vision Language Models → CLIP →           │
│              │ Gemini / GPT-4o architecture              │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** CLIP alignment trains image and text encoders contrastively on image-text pairs. However, internet-scraped image-text pairs have a systematic bias: the text accompanying an image on the web describes the image from a particular cultural perspective, uses particular languages predominantly, and tends to describe salient objects while omitting many others. Explain three specific ways these biases in CLIP training data manifest as failure modes in downstream vision-language models trained on CLIP embeddings — and for each, propose a data curation or training procedure that would mitigate it.

**Q2.** You are building a multimodal system for medical imaging analysis that must process X-ray images alongside patient records. The model must never hallucinate findings that aren't in the image. Design a system architecture that combines multimodal AI with explicit grounding verification — including what non-AI components you would add, how you would measure hallucination rate in production, and what safety threshold would trigger human review.
