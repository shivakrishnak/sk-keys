# Interview Mastery Dictionary - Copilot Instructions

This workspace folder (`/interview/`) is the **Interview Mastery Dictionary** - a condensed, interview-focused technical reference with deep Q&A for every concept.

## Relationship to Main Dictionary

The main `/dictionary/` folder contains the full 24-section v4.0 Technical Dictionary entries. This `/interview/` system is **completely separate** - different prompt, different structure, different purpose. Never mix the two systems:

- Do NOT apply `GENERATOR_PROMPT.md` rules to `/interview/` files
- Do NOT apply `INTERVIEW_PROMPT.md` rules to `/dictionary/` files
- Do NOT create files in `/dictionary/` when working on interview content
- Do NOT modify `/dictionary/` files when working on interview content

## Default Behaviour

When asked to generate, create, or edit any file under `/interview/`, apply all rules from `interview/config/INTERVIEW_PROMPT.md` automatically. Do not ask for confirmation before generating.

## Prompt Files

| Prompt                                   | Purpose                                                  |
| ---------------------------------------- | -------------------------------------------------------- |
| `interview/config/INTERVIEW_PROMPT.md`   | Master generation prompt for interview mastery entries   |
| `interview/config/generate-content.ps1`  | Batch content generation script                          |
| `interview/config/generate-keywords.ps1` | Keyword generation and folder/file scaffolding           |
| `interview/config/topic-registry.md`     | Topic-to-folder mapping and dictionary category mappings |

## Folder Structure Rules

- One folder per main technology/skill/topic (lowercase, hyphens for multi-word)
- Each folder contains an `index.md` listing all sub-topic files
- Sub-topic files use format: `{Topic} - {Subtopic}.md`
- Each sub-topic file contains 5-20 related keywords
- Separator in filenames: space + HYPHEN + space (NEVER em dash)

## Content Rules Summary

Each keyword within a file has 14 required sections (see `INTERVIEW_PROMPT.md` for full spec):

1. Title (`# KEYWORD NAME`)
2. TL;DR (one sentence, 25 words max)
3. The Problem This Solves (World Without It / Breaking Point / Evolution)
4. Textbook Definition
5. Understand It in 30 Seconds (One line / One analogy / One insight)
6. First Principles (Invariants / Trade-offs / Essential vs Accidental)
7. Mental Model / Analogy (blockquote + mapping + breakdown)
8. Gradual Depth - Four Levels (Anyone / Junior / Mid / Senior+)
9. How It Works (summarized but complete mechanism)
10. Complete Picture - End-to-End Flow (normal + failure + scale)
11. Code Example (real-world, BAD then GOOD, production-grade)
12. Quick Recall (3 things + interview one-liner)
13. The Surprising Truth (one counterintuitive fact)
14. Interview Deep-Dive (min 5 Qs with COMPLETE answers - the star section)

## Interview Deep-Dive Rules (Critical)

This is the most important section. Rules:

- **No cap on question count** - more is better (minimum 5, aim for 7-10)
- Every question MUST have a **complete, detailed answer** (not bullet hints)
- Answers should demonstrate natural depth ("low-key impress the interviewer")
- Answers can be long but must have clear structure and learning progression
- Required question types: conceptual, debugging, architecture, trade-off, production, hands-on, system design, comparison
- Questions must be scenario-based, practical, and test real experience

## Encoding Rules

- All files: UTF-8 without BOM
- PowerShell scripts: always use `pwsh` (PowerShell 7+), never `powershell.exe`
- File writing: `[System.Text.UTF8Encoding]::new($false)` (no BOM)
- No emojis in YAML frontmatter (encoding safety)
- Section headers in content body may use emojis for readability
- No em dashes anywhere - use regular hyphens only

## Formatting Rules

- Code lines: max 70 characters
- ASCII diagrams: max 59 characters wide
- Paragraphs: max 5 sentences
- BAD pattern before GOOD pattern in all code examples
- Every `###` heading preceded by `---` with blank lines
- Keywords within a file separated by double horizontal rules (`---` then `---`)

## Generation Workflow

### Generate content for an existing topic

```
Generate interview mastery content:
  Topic: Java
  File: Java - Collections.md
```

### Generate a new topic from scratch

```
Create new interview mastery topic: Angular
```

This will:

1. Check `topic-registry.md` for existing mappings
2. Check if dictionary has a matching category (e.g., ANG)
3. Generate keyword list, group into sub-topic files
4. Create folder + index.md + content files

### Generate from existing dictionary tier

```
Generate interview content from: tier-3-java
```

This will scan all dictionary categories in that tier and map them to interview topic folders.

## File Frontmatter Format

```yaml
---
title: Topic - Subtopic
topic: Topic
subtopic: Subtopic
keywords:
  - Keyword One
  - Keyword Two
difficulty_range: easy | medium | hard | mixed
status: draft | in-progress | complete
version: 1
---
```

No emojis. No Unicode stars. No special characters. Plain text only in YAML.
