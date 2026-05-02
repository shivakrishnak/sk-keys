---
layout: default
title: "Vision Language Models"
parent: "AI Foundations"
nav_order: 1614
permalink: /ai-foundations/vision-language-models/
number: "1614"
category: AI Foundations
difficulty: ★★★
depends_on: Multimodal Models, Foundation Models, Training
used_by: Multimodal Models, RAG, Foundation Models
related: Multimodal Models, Foundation Models, In-Context Learning
tags:
  - ai
  - vision
  - advanced
  - llm
  - multimodal
---

# 1614 — Vision Language Models

⚡ TL;DR — Vision Language Models (VLMs) combine a visual encoder with a language model to enable tasks requiring joint image and text understanding: visual question answering, image captioning, document analysis, and more.

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A document processing pipeline needs to extract structured data from scanned PDF invoices — images, not machine-readable text. Traditional OCR extracts text but loses layout context; object detection identifies regions but cannot reason about their meaning; a text LLM can reason but cannot see. Three separate systems, manual handoff, low reliability on complex layouts.

**THE BREAKING POINT:**
A large fraction of real-world information exists in visual form: documents, charts, diagrams, screenshots, photos. Without models that natively bridge vision and language, AI cannot process this information without brittle multi-step pipelines.

**THE INVENTION MOMENT:**
VLMs directly process images as "visual tokens" alongside text, enabling a single model to read a document image, understand its layout, and answer questions about it — collapsing three-system pipelines into one.

---

### 📘 Textbook Definition

**Vision Language Models (VLMs)** are a specific class of multimodal models that process image and text inputs jointly to produce text outputs. Architecturally, VLMs consist of: (1) a **visual encoder** (typically a Vision Transformer, ViT) that converts images into patch embeddings; (2) a **projection layer** (linear or MLP) that maps visual embeddings into the language model's token embedding space; (3) a **language model backbone** (LLM) that processes the combined sequence of visual and text tokens autoregressively. VLMs are trained with image-text alignment (contrastive or generative) and instruction-following fine-tuning on visual QA, captioning, and document tasks. Examples: LLaVA, PaLM-E, GPT-4V, Claude 3.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
VLMs are LLMs that can see: they take images as input alongside text and answer questions that require understanding both.

**One analogy:**

> Think of a VLM as an AI that has both eyes and a language brain connected. A standard LLM has only the language brain. Showing a LLM an image is like trying to describe a painting to a blind person over the phone — you lose a lot. A VLM can look at the painting directly and tell you exactly what it sees, count the brushstrokes, read the title, and compare it to artworks it knows from text descriptions.

**One insight:**
The key architectural insight is that language model transformers can process "visual tokens" the same way they process "text tokens" — enabling the existing LLM machinery to reason about images without architectural changes, as long as the visual representation is projected into the same embedding space.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Vision Transformers (ViT) divide an image into fixed-size patches and produce patch embeddings — analogous to text token embeddings.
2. Projecting patch embeddings into the LLM's embedding space allows the LLM to attend to visual patches as if they were text tokens.
3. Fine-tuning on visual instruction data teaches the LLM to respond to visual queries using its existing language capabilities.

**ARCHITECTURE:**

```
VLM ARCHITECTURE (LLaVA-style):

Image (448×448 pixels)
    ↓ Split into patches (14×14 = 1024 patches)
CLIP ViT encoder
    ↓ 1024 patch embeddings [dim=1024]
MLP Projection (2 layers)
    ↓ 1024 "visual tokens" [dim=4096]  ← LLM space

User question: "What's in this image?"
Tokenizer
    ↓ [What, 's, in, this, image, ?]

Combined: [v_1][v_2]...[v_1024][What]['s][in][this][image][?]
LLM (LLaMA-based)
    ↓ Autoregressive generation
"The image shows a bar chart depicting..."
```

**TRAINING STAGES:**

```
Stage 1 — Feature alignment:
  Freeze: ViT + LLM
  Train: only projection layer
  Data: 600K image-text pairs
  Goal: project visual features into LLM space

Stage 2 — Visual instruction tuning:
  Freeze: ViT
  Train: projection + LLM (or LoRA adapters)
  Data: 150K visual QA instructions
  Goal: teach model to follow visual instructions
```

**THE TRADE-OFFS:**
**Gain:** Single model for all vision-language tasks; reuses pretrained LLM and ViT; strong performance on document and chart understanding.
**Cost:** High token count per image (256–4,096 image tokens); hallucination of visual content not present; poor performance on tasks requiring pixel-level precision (segmentation, counting); higher inference cost vs. text-only LLMs.

---

### 🧪 Thought Experiment

**SETUP:**
You have a LLaVA-7B (7B parameter VLM) and a GPT-4V. You run three tasks:

1. "Read the number shown on this sign." (text in image)
2. "How many people are in this photo?" (counting)
3. "Based on this financial chart, did revenue grow in Q3?" (chart reasoning)

**RESULTS:**

Task 1 (reading text): GPT-4V = 96% accuracy; LLaVA-7B = 81%. Both do well — visual token resolution is sufficient for large text.

Task 2 (counting): GPT-4V = 74%; LLaVA-7B = 55%. Both struggle — counting requires precise spatial attention that transformer attention handles poorly for large numbers of objects.

Task 3 (chart reasoning): GPT-4V = 89%; LLaVA-7B = 71%. GPT-4V's larger model and richer instruction tuning handles multi-step chart reasoning better.

**THE INSIGHT:**
VLMs are not uniformly strong across all visual tasks. They excel at semantic tasks (understanding meaning, reading text, describing relationships) and struggle at precise spatial tasks (counting, pixel-level localisation, precise measurements). Understanding this capability profile is essential for appropriate use.

---

### 🧠 Mental Model / Analogy

> A VLM is like an art historian who is also an expert reader. They can look at a painting and tell you who painted it, what era it's from, what story it depicts, and what emotions it evokes — because they can integrate visual and textual knowledge. But they would struggle to count exactly how many brushstrokes are in the painting or measure the exact dimensions of each figure — that requires different tools (precision measurement, computer vision) rather than semantic understanding.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A VLM is an AI that can see AND talk — it processes images and text together, so you can ask it questions about photos or documents.

**Level 2 — How to use it (junior developer):**
API usage: pass image URL or base64 alongside your text prompt. For document processing, use "high" detail mode (GPT-4V) to get higher resolution patch processing. For visual QA, always ask "describe what you see first" to ground the model before asking for inferences. For structured extraction (receipts, invoices), provide the expected output schema in the prompt.

**Level 3 — How it works (mid-level engineer):**
Image resolution handling: standard ViT processes 224×224 or 448×448 images as fixed patch grids. For high-resolution images, newer VLMs (LLaVA-1.6, GPT-4o) use dynamic resolution tiling — split the image into overlapping tiles, encode each tile independently, concatenate tile tokens. This increases token count (and cost) but dramatically improves fine-grained text reading. OCR-trained VLMs (Donut, Nougat) specialise in document reading by training on large document datasets — they outperform general VLMs on dense text extraction tasks.

**Level 4 — Why it was designed this way (senior/staff):**
The architectural choice to use a frozen CLIP ViT plus a projection layer (as in LLaVA) rather than training the ViT jointly with the LLM is a compute trade-off. CLIP ViT provides strong general visual representations, pre-aligned to language through contrastive training. Fine-tuning the ViT during VLM training would be expensive and potentially degrade the universal visual representations. The projection layer is a computationally cheap way to bridge the representation gap. However, using a frozen ViT locks in CLIP's biases and resolution limitations. Newer architectures (Flamingo, GPT-4o) train the vision encoder jointly or use dynamic resolution patching to escape these constraints — at significantly higher training cost.

---

### ⚙️ How It Works (Mechanism)

```
DYNAMIC TILING FOR HIGH-RES (LLaVA-1.6 / GPT-4o):

Full image (1024×768)
    ↓ Split into tiles
[Tile 1: 448×448] [Tile 2: 448×448]
[Tile 3: 448×448] [Tile 4: 448×448]
+ [Thumbnail: 224×224] (full image, downscaled)
    ↓ ViT encode each tile
5 × 256 patch embeddings = 1280 visual tokens
    ↓ LLM processes 1280 visual tokens + text
    → Higher resolution text/chart reading

STANDARD (LLaVA-1.5):
Single 448×448 input
    ↓ 256 patch embeddings
    ↓ LLM processes 256 visual tokens + text
    → Good for general visual understanding
      Lower cost (4× fewer visual tokens)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
Image input + text prompt
    ↓
Resolution handling:
  Standard: resize to 448×448
  High-res: tile into multiple 448×448 tiles
    ↓
ViT encoding → patch embeddings
    ↓
MLP projection → visual tokens in LLM space
    ↓
Concatenate: [visual tokens] + [text tokens]
    ↓
[VLM FORWARD PASS ← YOU ARE HERE]
LLM transformer: cross-attention between
visual and text tokens
    ↓
Autoregressive text generation
    ↓
Output: text response / structured JSON
```

---

### 💻 Code Example

**Example 1 — Document extraction with VLM:**

```python
import anthropic
import base64
from pathlib import Path

def extract_invoice_data(
    invoice_image_path: str,
    client: anthropic.Anthropic
) -> dict:
    image_data = base64.standard_b64encode(
        Path(invoice_image_path).read_bytes()
    ).decode("utf-8")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "Extract the following fields from "
                        "this invoice as JSON: "
                        "{vendor_name, date, total_amount, "
                        "line_items: [{description, amount}]}. "
                        "Return ONLY valid JSON."
                    )
                }
            ],
        }]
    )
    import json
    return json.loads(message.content[0].text)
```

**Example 2 — Open source VLM with LLaVA:**

```python
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
from PIL import Image

processor = LlavaNextProcessor.from_pretrained(
    "llava-hf/llava-v1.6-mistral-7b-hf"
)
model = LlavaNextForConditionalGeneration.from_pretrained(
    "llava-hf/llava-v1.6-mistral-7b-hf",
    device_map="auto"
)

def visual_qa(image_path: str, question: str) -> str:
    image = Image.open(image_path)
    conversation = [{
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": question}
        ]
    }]
    prompt = processor.apply_chat_template(
        conversation, add_generation_prompt=True
    )
    inputs = processor(
        images=image, text=prompt, return_tensors="pt"
    ).to(model.device)
    output = model.generate(
        **inputs, max_new_tokens=200
    )
    return processor.decode(
        output[0][2:], skip_special_tokens=True
    )
```

---

### ⚖️ Comparison Table

| Model             | Parameters      | Resolution     | Best At              | Limitation               |
| ----------------- | --------------- | -------------- | -------------------- | ------------------------ |
| GPT-4o            | Unknown (large) | Dynamic tiling | All-around VQA, OCR  | Closed, expensive        |
| Claude 3.5 Sonnet | Unknown         | Standard       | Document analysis    | Image generation N/A     |
| LLaVA-1.6-7B      | 7B              | Dynamic tiling | Open source, local   | Weaker than large models |
| PaliGemma-3B      | 3B              | 448px          | Efficient mobile VLM | Task-specific FT needed  |
| Donut             | 200M            | 1280px         | Document OCR         | Text-only understanding  |
| BLIP-2            | 3.4B            | 384px          | Zero-shot VQA        | Limited instruction FT   |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                    |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "VLMs read all text in images accurately"         | VLM OCR is substantially less accurate than dedicated OCR engines (Tesseract, AWS Textract) for dense structured documents; use VLMs for understanding, OCR for extraction |
| "VLMs understand spatial relationships precisely" | VLMs are weak at precise spatial reasoning ("Is object A to the LEFT of object B?") — language priors override visual evidence                                             |
| "Adding more image tokens always helps"           | High-res tiling produces 4–16× more tokens, proportionally increasing inference cost; diminishing returns on many tasks                                                    |
| "VLMs can count objects reliably"                 | Counting above ~5 objects is unreliable due to attention diffusion over many patches                                                                                       |

---

### 🚨 Failure Modes & Diagnosis

**OCR Hallucination (Reading Phantom Text)**

**Symptom:** VLM reports text from an image that is not actually present — invents words, misreads numbers, or reports text from memory rather than visual parsing.

**Diagnostic:**

```python
def validate_ocr_extraction(
    extracted_text: str,
    reference_ocr: str,  # from dedicated OCR engine
    threshold: float = 0.9
) -> dict:
    """Compare VLM extraction to ground-truth OCR."""
    from difflib import SequenceMatcher
    similarity = SequenceMatcher(
        None,
        extracted_text.lower(),
        reference_ocr.lower()
    ).ratio()
    print(f"VLM-OCR agreement: {similarity:.1%}")
    if similarity < threshold:
        print("WARNING: Possible hallucination — "
              "validate manually")
    return {"similarity": similarity,
            "hallucination_risk": similarity < threshold}
```

**Fix:** For critical text extraction, use dedicated OCR followed by VLM reasoning — not VLM-only extraction.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Multimodal Models` — VLMs are a specific subset of multimodal models
- `Foundation Models` — VLMs are typically built on top of foundation LLMs and ViT encoders
- `Training` — VLM training involves two stages: alignment and instruction tuning

**Builds On This (learn these next):**

- `Multimodal Models` — VLMs are the text+image case; full multimodal models add audio/video
- `Foundation Models` — VLMs are the visual extension of foundation models
- `Retrieval-Augmented Generation` — RAG can retrieve images alongside text for VLM grounding

**Alternatives / Comparisons:**

- `Multimodal Models` — the broader category; VLMs are image+text specifically
- `Foundation Models` — VLMs build on top of foundation model infrastructure
- `In-Context Learning` — VLMs extend ICL to visual demonstrations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ LLMs that process images as visual tokens │
│              │ alongside text — enabling visual QA,      │
│              │ captioning, document analysis             │
├──────────────┼───────────────────────────────────────────┤
│ ARCHITECTURE │ ViT encoder → projection → LLM backbone   │
│              │ Image becomes "visual tokens" for the LLM │
├──────────────┼───────────────────────────────────────────┤
│ STRONG AT    │ Semantic understanding; reading text in   │
│              │ images; chart interpretation; document Q&A│
├──────────────┼───────────────────────────────────────────┤
│ WEAK AT      │ Pixel-precise counting; exact spatial     │
│              │ relationships; dense OCR on small text    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Document understanding; visual QA;        │
│              │ chart analysis; image captioning          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Images become tokens — the LLM can       │
│              │ see what it reads."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Multimodal Models → CLIP → LLaVA          │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** LLaVA's architecture freezes the CLIP ViT encoder during Stage 2 (visual instruction tuning). The reasoning is that CLIP's visual representations are general and strong, so fine-tuning would degrade them. However, this means the model's visual understanding is limited to what CLIP learned during contrastive training on internet image-text pairs. Describe three categories of visual tasks where this CLIP frozen encoder would systematically fail, and explain for each whether the failure is due to (a) resolution limitations, (b) domain shift from CLIP's training distribution, or (c) conceptual limitations of contrastive alignment.

**Q2.** You need to build a production VLM system that processes customer-submitted photos of damaged products for insurance claims. The system must: (1) extract the type of damage, (2) estimate severity (minor/moderate/severe), (3) identify the product category. The most critical failure mode is false severity inflation (claiming severe when minor — fraud risk). Design a complete production system including the VLM prompt design, output validation, confidence estimation, and human review routing logic.
