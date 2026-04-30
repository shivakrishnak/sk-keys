# 📌 Custom Instructions for GitHub Pages Markdown Automation

These instructions can be added to your GitHub repository documentation or shared with team members.

---

## For GitHub Copilot / AI Assistants

### System Instructions

When helping with markdown files in the `sk-keys` repository:

**IMPORTANT RULES:**

1. **File Naming Convention**
   - Always use format: `NNN — Title Here.md`
   - Use numeric prefix: 001, 002, 003 (3 digits)
   - Replace NNN with sequential numbers

2. **Folder Structure — One Folder Per Category**
   - Every category from `index.md → Coverage Stats` MUST have its own folder under `docs/`
   - Folder names must match exactly as listed below:

   | Folder | Category | Keyword Range |
   |---|---|---|
   | `docs/Java/` | Java & JVM Internals | 001–050 |
   | `docs/Java Language/` | Java Language | 051–065 |
   | `docs/Java Concurrency/` | Java Concurrency | 066–102 |
   | `docs/Spring/` | Spring & Spring Boot | 103–138 |
   | `docs/Distributed Systems/` | Distributed Systems | 139–194 |
   | `docs/Databases/` | Databases | 195–240 |
   | `docs/Messaging & Streaming/` | Messaging & Streaming | 241–260 |
   | `docs/Networking & HTTP/` | Networking & HTTP | 261–292 |
   | `docs/OS & Systems/` | OS & Systems | 295–315 |
   | `docs/System Design/` | System Design | 320–341 |
   | `docs/DSA/` | Data Structures & Algorithms | 358–389 |
   | `docs/Software Design/` | Software Design | 398–423 |
   | `docs/Testing/` | Testing | 412–423 |
   | `docs/Clean Code/` | Clean Code | 424–433 |
   | `docs/Cloud & Infrastructure/` | Cloud & Infrastructure | 434–449 |
   | `docs/DevOps & SDLC/` | DevOps & SDLC | 450–460 |
   | `docs/HTML/` | HTML | 461–490 |
   | `docs/CSS/` | CSS | 491–540 |
   | `docs/JavaScript/` | JavaScript | 541–620 |
   | `docs/TypeScript/` | TypeScript | 621–670 |
   | `docs/React/` | React | 671–730 |
   | `docs/Node.js/` | Node.js | 731–790 |
   | `docs/npm/` | npm | 791–820 |
   | `docs/Webpack/` | Webpack & Build Tools | 821–870 |

   - Each folder MUST contain an `index.md` listing all keywords for that category
   - Each keyword file MUST be placed in its category folder: `docs/[Category]/NNN — Title.md`
   - **Never** place keyword files in the wrong folder or in the root `docs/` directory

3. **Never Manually Add Frontmatter**
   - Instead, tell user: "Run `Update-MarkdownFrontmatter.ps1` to update navigation automatically across the entire `docs` tree"
   - If frontmatter is needed, provide the script command

4. **Entry Metadata Bar — Always Use Markdown Table**

   Every keyword file MUST include this metadata bar immediately after the TL;DR line.
   Use a **Markdown table** (NOT Unicode box-drawing characters — they misalign in browsers):

   ```markdown
   | #NNN | Category: Category Name | Difficulty: ★★☆ |
   |:---|:---|:---|
   | **Depends on:** | Concept1, Concept2 | |
   | **Used by:** | Consumer1, Consumer2 | |
   ```

   **Why it exists:** At 700+ entries, readers need instant context — what category,
   difficulty level, and which concepts to know before reading.
   
   **Rules:**
   - Row 1: keyword number, category, difficulty stars
   - Row 2: `Depends on` — prerequisite concepts
   - Row 3: `Used by` — concepts that build on this one
   - Values come from frontmatter fields: `depends_on`, `used_by`, `difficulty`, `category`, `number`
   - ❌ Never use Unicode box-drawing chars (┌─┤└) — they don't align in proportional fonts

5. **When User Asks About Adding New Files**
   
   Respond with:
   ```
   To add new markdown files to [SECTION]:
   
   1. Create file with proper naming:
      ☕ NNN — Your Title Here.md
   
   2. Run automation script:
      .\Update-MarkdownFrontmatter.ps1
   
   3. Files automatically get:
      - Jekyll YAML frontmatter
      - Proper parent-child relationships
      - Clean URLs
      - Sequential navigation order
   
   4. Commit and push:
      git add docs/
      git commit -m "Add [section] topics [number range]"
      git push origin main
   ```

5. **File Update Workflow**
   - Create content file → Run script → Commit → Push → Done!
   - No manual YAML editing needed
   - No permalink creation needed
   - No nav_order counting needed

6. **Scope of the Script**
   - It scans every folder and markdown file under `docs`
   - It updates section indexes and child pages together
   - It computes parents, nav order, `has_children`, and permalinks automatically

---

## Example Interactions

### User: "I want to add 5 new Java topics"

**Your Response:**
```
Great! Here's the quickest way:

Step 1: Create your markdown files with proper naming pattern
   012 — Garbage Collection.md
   013 — Finalization.md
   014 — Reference Queue.md
   015 — Memory Leak Detection.md
   016 — GC Tuning.md

Step 2: Add your content to each file

Step 3: Run the automation script
   .\Update-MarkdownFrontmatter.ps1

Step 4: Commit and push
   git add docs/java/
   git commit -m "Add 5 Java GC topics (012-016)"
   git push origin main

Done! Files will appear in GitHub Pages in 1-2 minutes.
```

### User: "How do I add a new markdown file?"

**Your Response:**
```
For [SECTION]:

1. Create file: [SECTION]/NNN — Your Title.md
2. Run: .\Update-MarkdownFrontmatter.ps1
3. Git: git add docs/ && git commit -m "Add [title]" && git push

The script automatically handles:
✓ YAML frontmatter
✓ Parent-child relationships
✓ Navigation ordering
✓ Clean URLs
```

### User: "Can I update all sections at once?"

**Your Response:**
```
Yes! Use the recursive docs updater:

.\Update-MarkdownFrontmatter.ps1

This updates all folders and markdown pages under `docs`, including:
✓ Java (001–102)
✓ Spring (103–138)
✓ Distributed Systems (139–194)
✓ Databases (195–240)
✓ Messaging & Streaming (241–260)
✓ Networking & HTTP (261–292)
✓ OS & Systems (295–315)
✓ System Design (320–341)
✓ DSA (358–389)
✓ Software Design (398–423)
✓ Testing (412–423)
✓ Clean Code (424–433)
✓ Cloud & Infrastructure (434–449)
✓ DevOps & SDLC (450–460)
✓ HTML (461–490)
✓ CSS (491–540)
✓ JavaScript (541–620)
✓ TypeScript (621–670)
✓ React (671–730)
✓ Node.js (731–790)
✓ npm (791–820)
✓ Webpack & Build Tools (821–870)

Then commit and push normally.
```

---

## What NOT to Do

❌ **Don't** manually add frontmatter to files  
❌ **Don't** ask me to add YAML frontmatter details  
❌ **Don't** use non-standard file naming  
❌ **Don't** use single or double-digit numbers (use 001, 002, etc.)  
❌ **Don't** push files without running automation script  

---

## What TO Do

✅ **Do** use proper file naming: `001 — Title.md`  
✅ **Do** run the automation script after creating files  
✅ **Do** commit files after automation completes  
✅ **Do** use the filename to set nav_order (numbers in filename)  
✅ **Do** test locally if possible before pushing  

---

## 📖 Dictionary Entry Template (Technical Dictionary)

When creating any dictionary entry for this repository, **always** use the template below.
Every field is mandatory unless the concept has no code equivalent.

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

⚡ TL;DR — one sentence.

| #NNN | Category: Category Name | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Concept1, Concept2 | |
| **Used by:** | Consumer1, Consumer2 | |

---

## 📘 Textbook Definition

## 🟢 Simple Definition (Easy)

## 🔵 Simple Definition (Elaborated)

## 🔩 First Principles Explanation

## ❓ Why Does This Exist (Why Before What)

## 🧠 Mental Model / Analogy

## ⚙️ How It Works (Mechanism)

## 🔄 How It Connects (Mini-Map)

## 💻 Code Example

## 🔁 Flow / Lifecycle (if applicable)

## ⚠️ Common Misconceptions

## 🔥 Pitfalls in Production

## 🔗 Related Keywords

## 📌 Quick Reference Card

---
## 🧠 Think About This Before We Continue
Q1. ...
Q2. ...
```

### Section Purpose Guide

| Section | What to Write |
|---|---|
| `TL;DR` | One crisp sentence — what this thing IS |
| `Textbook Definition` | Formal, spec/standard definition |
| `Simple (Easy)` | Explain to a junior dev or non-programmer |
| `Simple (Elaborated)` | Explain to a mid-level developer |
| `First Principles` | Build the idea from scratch — why was it invented? |
| `Why Does This Exist` | The pain it solves; what world looks like without it |
| `Mental Model / Analogy` | Real-world metaphor that makes it stick |
| `How It Works` | Internal mechanism — data flow, algorithm, lifecycle |
| `How It Connects` | ASCII mini map showing related concepts |
| `Code Example` | Minimal, runnable code showing the concept |
| `Flow / Lifecycle` | If it's a process: numbered flow diagram |
| `Common Misconceptions` | Table: Wrong belief → Correct reality |
| `Pitfalls in Production` | What breaks in real systems; with fix |
| `Related Keywords` | Bullet list with one-line description each |
| `Quick Reference Card` | Box summary for fast lookup |
| `Think About This` | 2-3 Socratic questions to deepen understanding |

### Difficulty Scale

| Stars | Meaning |
|---|---|
| ★☆☆ | Beginner — need no prior knowledge |
| ★★☆ | Intermediate — requires prerequisites |
| ★★★ | Advanced — deep internals or distributed systems |


---

