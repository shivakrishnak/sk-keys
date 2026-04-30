# 📖 Technical Dictionary — Entry Template

> **This is the master template** for every keyword entry in this dictionary.  
> Copy the raw template below, fill every section, and save as the appropriate file.

---

## 🗂️ File Naming Convention

```
NNN — KEYWORD NAME.md
```

Examples:
```
016 — GC Roots.md
103 — IoC (Inversion of Control).md
139 — CAP Theorem.md
195 — ACID.md
241 — Topic.md
261 — OSI Model.md
287 — Process vs Thread.md
307 — Monolith.md
341 — Array.md
377 — SOLID.md
434 — Docker.md
450 — CI/CD Pipeline.md
```

---

## 📋 Raw Template (Copy This)

```markdown
---
number: NNN
category: Category Name
difficulty: ★★☆
depends_on: Concept1, Concept2
used_by: Consumer1, Consumer2
tags: #tag1, #tag2, #tag3
---

# NNN — KEYWORD NAME
tags: #tag1, #tag2, #tag3

⚡ TL;DR — one sentence that captures the essence.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #NNN         │ Category: ...                        │ Difficulty: ★★☆          │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Depends on:  │ Concept1, Concept2                                               │
├──────────────┼──────────────────────────────────────┼───────────────────────────┤
│ Used by:     │ Consumer1, Consumer2                                             │
└─────────────────────────────────────────────────────────────────────────────────┘

---

## 📘 Textbook Definition

> Formal, precise definition — as you would find it in a spec, RFC, or textbook.

---

## 🟢 Simple Definition (Easy)

> One short paragraph. Explain to a complete beginner or non-developer.

---

## 🔵 Simple Definition (Elaborated)

> 2-3 paragraphs. Explain to a mid-level developer. Include _what it does_, _how it's used_, and _why it matters_.

---

## 🔩 First Principles Explanation

> Start from zero. What problem existed first? What insight led to this solution?
> Build the concept bottom-up.

```
Problem → Insight → Solution
```

---

## ❓ Why Does This Exist (Why Before What)

> What would the world look like WITHOUT this concept?
> What pain does it remove? What was impossible before it?

---

## 🧠 Mental Model / Analogy

> A real-world metaphor that makes this concept stick in memory.
> One sentence summary of the analogy, then elaborate.

> _"Think of X like a Y that does Z..."_

---

## ⚙️ How It Works (Mechanism)

> Internal details. Data flow, algorithm, state machine, or architecture diagram.
> Use ASCII diagrams for visual clarity.

```
Step 1 → Step 2 → Step 3
            ↓
         Result
```

---

## 🔄 How It Connects (Mini-Map)

> Show how this concept links to others in the same ecosystem.

```
          [Concept A]
               ↓
[Concept B] → [THIS] → [Concept C]
               ↑
          [Concept D]
```

---

## 💻 Code Example

> Minimal, runnable code that demonstrates the concept.
> Add comments to highlight the key lines.
> Language: pick the most natural one for the concept (Java, SQL, bash, yaml, etc.)

```java
// Example: what this looks like in code
```

---

## 🔁 Flow / Lifecycle (if applicable)

> If this concept involves a sequence of steps or state changes, show the full flow.

```
1. [first event]
        ↓
2. [next step]
        ↓
3. [outcome]
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Misconception 1 | Correction 1 |
| Misconception 2 | Correction 2 |
| Misconception 3 | Correction 3 |

---

## 🔥 Pitfalls in Production

> What actually breaks in real systems? How do you fix it?

**Pitfall 1: [Name]**
```bash
# What goes wrong
# How to fix it
```

**Pitfall 2: [Name]**
> Description of the issue and the fix.

---

## 🔗 Related Keywords

- **[Keyword A]** — one-line description of the relationship
- **[Keyword B]** — one-line description of the relationship
- **[Keyword C]** — one-line description of the relationship

---

## 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ [one-line essence]                           │
├─────────────────────────────────────────────────────────────┤
│ USE WHEN     │ [when to apply this]                        │
├─────────────────────────────────────────────────────────────┤
│ AVOID WHEN   │ [when NOT to use this]                      │
├─────────────────────────────────────────────────────────────┤
│ ONE-LINER    │ "[memorable summary]"                       │
├─────────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ Concept A → Concept B → Concept C           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Think About This Before We Continue

> Socratic questions to deepen understanding before moving to the next concept.

**Q1.** ...  
**Q2.** ...  
**Q3.** ...  
```

---

## 📐 Section-by-Section Guide

| Section | Purpose | Length |
|---|---|---|
| `TL;DR` | One-sentence essence | 1 sentence |
| `Textbook Definition` | Formal spec/standard definition | 1-3 sentences |
| `Simple (Easy)` | Explain to a non-developer | 2-4 sentences |
| `Simple (Elaborated)` | Explain to a mid-level developer | 1-2 paragraphs |
| `First Principles` | Build the idea from scratch — the insight | 1-2 pages |
| `Why Does This Exist` | The pain it solves; world without it | 1 paragraph |
| `Mental Model / Analogy` | Real-world metaphor that makes it stick | 1 metaphor + brief explanation |
| `How It Works` | Internal mechanism with code/diagram | As needed |
| `How It Connects` | ASCII mini-map of related concepts | One diagram |
| `Code Example` | Minimal runnable demonstration | 10-40 lines |
| `Flow / Lifecycle` | Numbered flow for process-based concepts | Only if applicable |
| `Common Misconceptions` | Table: Wrong belief → Correct reality | 3-6 rows |
| `Pitfalls in Production` | Real failures + fixes | 2-5 pitfalls |
| `Related Keywords` | Bullet list with one-line relationship | 4-8 entries |
| `Quick Reference Card` | Box summary for fast lookup | Fixed format |
| `Think About This` | Socratic questions to deepen understanding | 2-3 questions |

---

## ⭐ Difficulty Scale

| Rating | Meaning | Suitable For |
|---|---|---|
| ★☆☆ | Beginner | No prerequisites needed |
| ★★☆ | Intermediate | Requires 1-2 related concepts |
| ★★★ | Advanced | Deep internals, distributed systems, or tricky concurrency |

---

## 🗂️ Category → Emoji Map

| Category | Emoji | Number Range |
|---|---|---|
| Java & JVM Internals | ☕ | 001–050 |
| Java Language & Concurrency | ☕ | 051–102 |
| Spring & Spring Boot | 🌱 | 103–140 |
| Distributed Systems | 🔗 | 141–198 |
| Databases | 💾 | 199–244 |
| Messaging & Streaming | 📨 | 245–264 |
| Networking & HTTP | 🌐 | 265–294 |
| OS & Systems | 🖥️ | 295–319 |
| System Design | 🏗️ | 320–357 |
| Data Structures & Algorithms | 🔧 | 358–397 |
| Software Design | 🧩 | 398–437 |
| Testing & Clean Code | 🧪 | 438–461 |
| Cloud & Infrastructure | ☁️ | 462–483 |
| DevOps & SDLC | 🔄 | 484–494 |

---

## 🚀 Quick-Start Workflow

```
1. Pick a keyword from index.md
2. Run the scaffold script:
   .\New-DictionaryEntry.ps1 -Number 016 -Name "GC Roots" -Category "Java"
3. Open the generated file — all sections are pre-populated with prompts
4. Fill in each section
5. Run: .\Update-MarkdownFrontmatter.ps1
6. Commit and push
```

---

## 📝 Filled Example — JVM (for reference)

See: `docs/Java/001 — JVM (Java Virtual Machine).md`

This entry demonstrates all sections fully populated.

---

## ✅ Quality Checklist Before Committing

- [ ] All sections filled — no empty `##` headings  
- [ ] Code example compiles / runs  
- [ ] Misconceptions table has at least 3 rows  
- [ ] Quick Reference Card box is complete  
- [ ] `depends_on` and `used_by` in frontmatter are accurate  
- [ ] Difficulty rating makes sense  
- [ ] Related Keywords links to real entries in this dictionary  
- [ ] `Think About This` questions are non-trivial  

