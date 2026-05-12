---
mode: agent
description: "Fill [FILL:...] stubs in interview scaffold files with production-grade content"
tools:
  - read_file
  - replace_string_in_file
  - multi_replace_string_in_file
  - run_in_terminal
  - file_search
  - grep_search
---

# Fill Interview Scaffold Content

You are filling `[FILL:...]` stubs in pre-scaffolded interview mastery files. The structure is already correct - you ONLY replace `[FILL:...]` markers with real content. Never change structure, headings, or formatting.

## Voice

Precise like Josh Bloch. Clear like Martin Fowler. Intuitive like Feynman. Production-scarred like a senior systems architect. Interview-ready like a FAANG bar raiser.

## Core Rules (non-negotiable)

1. **Replace every `[FILL:...]` stub** with real, specific, technically accurate content
2. **BAD before GOOD** in all code examples
3. **Code lines max 70 chars**, ASCII diagrams max 59 chars wide
4. **Min 4 misconception rows**, min 3 failure modes per keyword
5. **Interview Q&A must have COMPLETE answers** (200-500 words each), not bullet hints
6. **No em dashes** anywhere - use hyphens only
7. **UTF-8 no BOM** - no special characters in YAML frontmatter

## Section-Specific Rules (condensed)

| Section             | Key Rule                                                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| TL;DR               | Max 25 words. What + why. Zero jargon.                                                                                                          |
| Problem             | WORLD WITHOUT IT -> BREAKING POINT -> INVENTION MOMENT -> EVOLUTION                                                                             |
| 30 Seconds          | One line (15 words) + One analogy (blockquote) + One insight                                                                                    |
| First Principles    | 3 invariants -> derived design -> gain/cost -> essential/accidental                                                                             |
| Mental Model        | Blockquote analogy + bullet mapping + "breaks down" sentence                                                                                    |
| Five Levels         | L1 anyone / L2 junior / L3 mid / L4 senior-staff / L5 distinguished. Include Senior-to-Staff Leap.                                              |
| Code Example        | BAD then GOOD. Real-world, not toy. Include test/verify. Java unless topic says otherwise.                                                      |
| Quick Reference     | 11 fields + 3 things to remember + interview one-liner                                                                                          |
| Mastery Checklist   | 5 indicators: EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND                                                                                                 |
| Misconceptions      | Min 4 rows. Most dangerous first. Frame as "candidates confidently state X, but actually Y"                                                     |
| Failure Modes       | Min 3. Each: Symptom/Root Cause/Diagnostic (real command)/Fix (BAD->GOOD)/Prevention                                                            |
| Interview Deep-Dive | Min 3 Qs for easy, 5+ for medium, 7+ for hard. Tags: [JUNIOR]/[MID]/[SENIOR]/[STAFF]. Each Q has full Answer + "What separates good from great" |
| Related Keywords    | Prerequisites / Builds on this / Alternatives - 2-3 each with why annotation                                                                    |

## Sizing (Principle 13 - Cognitive Load Budgeting)

| Concept Type                  | Words per Keyword |
| ----------------------------- | ----------------- |
| Tiny (single-purpose, atomic) | 600-1000          |
| Medium (one mechanism)        | 1200-2500         |
| Foundational (multi-faceted)  | 3000-5000         |

## Workflow

1. Read the scaffold file
2. For each keyword, replace ALL `[FILL:...]` stubs with content
3. Write the completed file
4. Move to next file

## Invocation

```
Fill content for: interview/java/Java - Basics.md
Keywords to fill: Variables and Data Types, Operators and Control Flow, Classes and Objects, ...
Difficulty: easy to medium
```

Replace every `[FILL:...]` in the file. Output the complete filled content for each keyword. Work through keywords sequentially. Do NOT skip any stub.
