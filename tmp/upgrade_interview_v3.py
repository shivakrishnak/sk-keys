#!/usr/bin/env python3
"""
Upgrade INTERVIEW_PROMPT.md from v2.0 to v3.0.

Changes:
  1. Version numbers: 2->3, v2.0->v3.0
  2. Add KEY NUMBERS field to Quick Reference Card (section 3.12)
  3. Insert new Mastery Checklist section (new section 3.13)
  4. Renumber Surprising Truth: 3.13 -> 3.14
  5. Move Interview Deep-Dive to capstone: 3.14 -> 3.18
  6. Add difficulty tags + "good from great" to Interview Deep-Dive
  7. Renumber Related Keywords: 3.18 -> 3.19
  8. Update conditional section table references
  9. Rewrite Section 6 skeleton with new order
  10. Update Section 7 invocation references
  11. Rewrite Section 8 validation checklist
  12. Rewrite Section 9 version detection
"""
import re
import sys

filepath = r"c:\ASK\MyWorkspace\sk-keys\interview\config\INTERVIEW_PROMPT.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)
errors = []

def safe_replace(text, old, new, label, count=1):
    if old not in text:
        errors.append(f"NOT FOUND: {label}: {old[:80]}...")
        return text
    actual = text.count(old)
    if count > 0 and actual != count:
        print(f"  WARNING: {label}: expected {count} occurrences, found {actual}")
    return text.replace(old, new, count if count > 0 else -1)


# ================================================================
# Phase 1: Version Number Updates
# ================================================================
print("Phase 1: Version numbers...")

content = safe_replace(content,
    "# Interview Mastery Dictionary - Master Prompt v2.0",
    "# Interview Mastery Dictionary - Master Prompt v3.0",
    "title")

content = safe_replace(content,
    "INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v2.0",
    "INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v3.0",
    "inner header")

content = safe_replace(content,
    "| `SPEC_VERSION` | `2`    | Integer written to `version:` in all entries |",
    "| `SPEC_VERSION` | `3`    | Integer written to `version:` in all entries |",
    "spec version")

content = safe_replace(content,
    "| `SPEC_LABEL`   | `v2.0` | Human-readable label for headers/commits     |",
    "| `SPEC_LABEL`   | `v3.0` | Human-readable label for headers/commits     |",
    "spec label")

content = safe_replace(content,
    "Integer matching SPEC_VERSION (currently 2)",
    "Integer matching SPEC_VERSION (currently 3)",
    "yaml version note")

content = safe_replace(content,
    "Existing v1.0 content retains version: 1 until upgraded",
    "Existing v1.0/v2.0 content retains its version until upgraded",
    "version retention note")

content = safe_replace(content,
    "Follow Interview Mastery Prompt v2.0 exactly.",
    "Follow Interview Mastery Prompt v3.0 exactly.",
    "invocation ref", count=3)

print("  Done: version numbers updated")


# ================================================================
# Phase 2: Update Conditional Section Table
# ================================================================
print("Phase 2: Conditional table...")

content = safe_replace(content,
    "All other sections (3.1-3.10, 3.12-3.14, 3.16-3.18) are\n  always required.",
    "All other sections (3.1-3.10, 3.12-3.14, 3.16-3.19) are\n  always required.",
    "conditional table range")

print("  Done: conditional table updated")


# ================================================================
# Phase 3: Section Reorder (3.12-3.18 -> 3.12-3.19)
# ================================================================
print("Phase 3: Section reorder...")

def find_section_start(text, header_text):
    """Find position of a section header block's first dash line."""
    # Section headers look like:
    # ----------------------------------------------------------------
    # 3.XX  SECTION NAME  [STATUS]
    # ----------------------------------------------------------------
    idx = text.find(header_text)
    if idx == -1:
        return None
    # Walk back to find the preceding dash line
    line_start = text.rfind('\n', 0, idx) + 1
    prev_line_end = line_start - 1
    if prev_line_end > 0:
        prev_line_start = text.rfind('\n', 0, prev_line_end) + 1
        prev_line = text[prev_line_start:prev_line_end]
        if prev_line.startswith('----'):
            return prev_line_start
    return line_start

# Find section boundaries
pos_312 = find_section_start(content, '3.12  QUICK REFERENCE CARD  [REQUIRED]')
pos_313 = find_section_start(content, '3.13  THE SURPRISING TRUTH  [REQUIRED]')
pos_314 = find_section_start(content, '3.14  INTERVIEW DEEP-DIVE  [REQUIRED - PRIMARY SECTION]')
pos_315 = find_section_start(content, '3.15  COMPARISON TABLE  [CONDITIONAL]')
pos_316 = find_section_start(content, '3.16  COMMON MISCONCEPTIONS  [REQUIRED]')
pos_317 = find_section_start(content, '3.17  FAILURE MODES')
pos_318 = find_section_start(content, '3.18  RELATED KEYWORDS  [REQUIRED]')
pos_s4 = content.find("================================================================\nSECTION 4: FORMATTING RULES")

positions = {
    '3.12': pos_312, '3.13': pos_313, '3.14': pos_314,
    '3.15': pos_315, '3.16': pos_316, '3.17': pos_317,
    '3.18': pos_318, 'S4': pos_s4
}
for name, pos in positions.items():
    if pos is None:
        errors.append(f"Section {name} not found")
        print(f"  ERROR: Section {name} not found!")

if errors:
    print(f"\nFATAL: {len(errors)} errors found. Aborting.")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

# Extract individual sections
sec_312 = content[pos_312:pos_313]
sec_313 = content[pos_313:pos_314]
sec_314 = content[pos_314:pos_315]
sec_315 = content[pos_315:pos_316]
sec_316 = content[pos_316:pos_317]
sec_317 = content[pos_317:pos_318]
sec_318 = content[pos_318:pos_s4]

print(f"  Extracted sections: 3.12({len(sec_312)}), 3.13({len(sec_313)}), "
      f"3.14({len(sec_314)}), 3.15({len(sec_315)}), 3.16({len(sec_316)}), "
      f"3.17({len(sec_317)}), 3.18({len(sec_318)}) chars")

# --- Modify 3.12: Add KEY NUMBERS field ---
sec_312 = sec_312.replace(
    '  **ONE-LINER:** [memorable metaphor - 1 sentence]',
    '  **ONE-LINER:** [memorable metaphor - 1 sentence]\n'
    '  **KEY NUMBERS:** [2-3 critical thresholds, defaults,\n'
    '    or limits engineers must know - e.g., "default\n'
    '    pool: 200", "99p target: <100ms"]')

sec_312 = sec_312.replace(
    '  - The 8 fields give instant recall under pressure',
    '  - The 9 fields give instant recall under pressure')

# Add KEY NUMBERS rule
sec_312 = sec_312.replace(
    '  - AVOID WHEN and ANTI-PATTERN are critical: they show\n'
    '    mastery through contrast (Principle 15)',
    '  - KEY NUMBERS must be real, verifiable values - not\n'
    '    made-up thresholds. State if default/recommended/hard\n'
    '  - AVOID WHEN and ANTI-PATTERN are critical: they show\n'
    '    mastery through contrast (Principle 15)')

print("  3.12: KEY NUMBERS field added")

# --- Create new 3.13 Mastery Checklist ---
new_sec_313 = (
    "----------------------------------------------------------------\n"
    "3.13  MASTERY CHECKLIST  [REQUIRED]\n"
    "----------------------------------------------------------------\n"
    "\n"
    "Section header:\n"
    "  ### ✅ Mastery Checklist\n"
    "\n"
    "PURPOSE: Self-assessment before interviews. Five testable\n"
    "indicators that tell the reader \"you've truly mastered\n"
    "this concept\" - not just read about it.\n"
    "\n"
    "Structure:\n"
    "\n"
    "  **You've mastered this when you can:**\n"
    "  1. **EXPLAIN:** [Teach this to a junior in 2 minutes\n"
    "     without notes - 1 sentence describing what to explain]\n"
    "  2. **DEBUG:** [Diagnose a specific failure involving this\n"
    "     concept from symptoms alone - 1 sentence scenario]\n"
    "  3. **DECIDE:** [Choose between this and an alternative\n"
    "     under time pressure with clear rationale - 1 sentence]\n"
    "  4. **BUILD:** [Implement or configure this correctly in\n"
    "     a production context - 1 sentence deliverable]\n"
    "  5. **EXTEND:** [Apply the underlying principle to a\n"
    "     different domain or novel problem - 1 sentence]\n"
    "\n"
    "Rules:\n"
    "  - Exactly 5 indicators, always in EXPLAIN/DEBUG/DECIDE/\n"
    "    BUILD/EXTEND order\n"
    "  - Each must be specific to THIS concept (not generic)\n"
    "  - Each must be testable - reader can verify yes/no\n"
    "  - Focus on practical ability, not theoretical knowledge\n"
    "  - 50-100 words total\n"
    "\n"
)
print("  3.13: Mastery Checklist section created")

# --- Renumber 3.13 Surprising Truth -> 3.14 ---
sec_313_renum = sec_313.replace(
    '3.13  THE SURPRISING TRUTH  [REQUIRED]',
    '3.14  THE SURPRISING TRUTH  [REQUIRED]')
print("  3.13->3.14: Surprising Truth renumbered")

# --- Modify & Renumber 3.14 Interview Deep-Dive -> 3.18 ---
sec_314_mod = sec_314.replace(
    '3.14  INTERVIEW DEEP-DIVE  [REQUIRED - PRIMARY SECTION]',
    '3.18  INTERVIEW DEEP-DIVE  [REQUIRED - CAPSTONE]')

# Update PURPOSE text
sec_314_mod = sec_314_mod.replace(
    "PURPOSE: This is the STAR SECTION of every entry. Bridge the\n"
    "gap between understanding and interview excellence. Real\n"
    "questions, real scenarios, complete answers that demonstrate\n"
    "mastery. The reader should walk into any interview and own\n"
    "the room on this topic.",
    "PURPOSE: This is the CAPSTONE SECTION of every entry -\n"
    "positioned last intentionally. By the time the reader\n"
    "reaches this section, they have built complete knowledge\n"
    "through all preceding sections: understanding, mechanism,\n"
    "reference, self-assessment, pitfalls, and failure modes.\n"
    "Now they practice articulating that knowledge under\n"
    "interview pressure. The reader should walk into any\n"
    "interview and own the room on this topic.")

# Add difficulty tags to QUESTION REQUIREMENTS
sec_314_mod = sec_314_mod.replace(
    "  - Questions ordered: foundational -> advanced -> expert\n"
    "  - Every question must be realistic",
    "  - Questions ordered: foundational -> advanced -> expert\n"
    "  - Tag each question with difficulty level:\n"
    "      [JUNIOR]: foundational understanding\n"
    "      [MID]: working knowledge and trade-offs\n"
    "      [SENIOR]: production experience, system thinking\n"
    "      [STAFF]: cross-system reasoning, novel synthesis\n"
    "  - Every question must be realistic")

# Add "What separates good from great" to ANSWER REQUIREMENTS
sec_314_mod = sec_314_mod.replace(
    "  - Answers should have natural LEARNING PROGRESSION:\n"
    "    surface -> mechanism -> trade-offs -> production reality",
    "  - End every answer with:\n"
    "    *What separates good from great:* [1 sentence - the\n"
    "     specific insight that elevates this answer from\n"
    "     competent to impressive]\n"
    "  - Answers should have natural LEARNING PROGRESSION:\n"
    "    surface -> mechanism -> trade-offs -> production reality")

# Update FORMAT section with difficulty tags
sec_314_mod = sec_314_mod.replace(
    "  **Q1: [Real interview question - specific, scenario-based]**\n"
    "\n"
    "  *Why they ask:* [What the interviewer is evaluating -\n"
    "   1 sentence]\n"
    "\n"
    "  **Answer:**\n"
    "  [Complete, structured answer. Can be 200-500 words.\n"
    "   Include code, diagrams, metrics as needed.\n"
    "   Structure with sub-headers, numbered lists, or tables\n"
    "   for clarity. End with a key insight.]",
    "  **Q1 [JUNIOR]: [Interview question - scenario-based]**\n"
    "\n"
    "  *Why they ask:* [What the interviewer is evaluating -\n"
    "   1 sentence]\n"
    "\n"
    "  **Answer:**\n"
    "  [Complete, structured answer. Can be 200-500 words.\n"
    "   Include code, diagrams, metrics as needed.\n"
    "   Structure with sub-headers, numbered lists, or tables\n"
    "   for clarity. End with a key insight.]\n"
    "\n"
    "  *What separates good from great:* [1 sentence - the\n"
    "   insight that elevates this answer]")

sec_314_mod = sec_314_mod.replace(
    "  **Q2: [Next question - different category, harder]**\n"
    "\n"
    "  *Why they ask:* [What skill/depth this probes]\n"
    "\n"
    "  **Answer:**\n"
    "  [Complete answer...]\n"
    "\n"
    "  [Continue for all questions...]",
    "  **Q2 [MID]: [Next question - different category]**\n"
    "\n"
    "  *Why they ask:* [What skill/depth this probes]\n"
    "\n"
    "  **Answer:**\n"
    "  [Complete answer...]\n"
    "\n"
    "  *What separates good from great:* [1 sentence]\n"
    "\n"
    "  [Continue for all questions...]")

print("  3.14->3.18: Interview Deep-Dive renumbered + enhanced")

# --- Renumber 3.18 Related Keywords -> 3.19 ---
sec_318_renum = sec_318.replace(
    '3.18  RELATED KEYWORDS  [REQUIRED]',
    '3.19  RELATED KEYWORDS  [REQUIRED]')
print("  3.18->3.19: Related Keywords renumbered")

# --- Assemble new block in correct order ---
new_block = (
    sec_312 +           # 3.12 Quick Ref Card (+KEY NUMBERS)
    new_sec_313 +       # 3.13 Mastery Checklist (NEW)
    sec_313_renum +     # 3.14 Surprising Truth (was 3.13)
    sec_315 +           # 3.15 Comparison Table (unchanged)
    sec_316 +           # 3.16 Common Misconceptions (unchanged)
    sec_317 +           # 3.17 Failure Modes (unchanged)
    sec_314_mod +       # 3.18 Interview Deep-Dive (was 3.14, enhanced)
    sec_318_renum       # 3.19 Related Keywords (was 3.18)
)

# Replace old block with new block
old_block = content[pos_312:pos_s4]
content = content[:pos_312] + new_block + content[pos_s4:]

print(f"  Section block replaced: {len(old_block)} -> {len(new_block)} chars")


# ================================================================
# Phase 4: Rewrite Section 6 Skeleton
# ================================================================
print("Phase 4: Section 6 skeleton...")

SKELETON_START = "Below is the exact skeleton for ONE keyword within a file.\nRepeat for each keyword, separated by double horizontal rules."
SKELETON_END_MARKER = "- [Keyword] - [when to prefer it]"

skel_start = content.find(SKELETON_START)
# Find the LAST occurrence of the end marker that's in the skeleton section
# (there could be one in the section spec too, so find the one after skel_start)
skel_end_search = content.find(SKELETON_END_MARKER, skel_start)
if skel_end_search == -1:
    print("  ERROR: Could not find skeleton end marker")
    sys.exit(1)
skel_end = skel_end_search + len(SKELETON_END_MARKER)

new_skeleton = r"""Below is the exact skeleton for ONE keyword within a file.
Repeat for each keyword, separated by double horizontal rules.

# KEYWORD NAME

**TL;DR** - [One sentence. Max 25 words. Essence + WHY.]

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
[Concrete pain scenario. 2-4 sentences.]

**THE BREAKING POINT:**
[Specific failure. 1-2 sentences.]

**THE INVENTION MOMENT:**
"This is exactly why [KEYWORD] was created."

**EVOLUTION:**
[2-3 sentences: predecessor -> current form -> future.]

---

### 📘 Textbook Definition
[2-4 sentences. Formal. Technically precise. No analogies.]

---

### ⏱️ Understand It in 30 Seconds

**One line:**
[15 words max. Zero jargon.]

**One analogy:**
> [2-3 sentences. Real world. Anyone understands.]

**One insight:**
[What separates knowing the name from understanding it.
 2-3 sentences.]

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [Always true about this concept]
2. [Always true about this concept]
3. [Always true about this concept]

**DERIVED DESIGN:**
[How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [what you get]
**Cost:** [what you sacrifice]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [What no implementation can avoid]
**Accidental:** [What's hard only due to current tooling]

---

### 🧠 Mental Model / Analogy
> [Primary analogy in blockquote.]

- "[Analogy element]" -> [technical element]
- "[Analogy element]" -> [technical element]
- "[Analogy element]" -> [technical element]

Where this analogy breaks down: [1 sentence.]

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
[Plain English. No jargon. 2-4 sentences.]

**Level 2 - How to use it (junior developer):**
[Basic usage. Common patterns. 3-5 sentences.]

**Level 3 - How it works (mid-level engineer):**
[Internals. Data structures. Tuning. 4-6 sentences.]

**Level 4 - Production mastery (senior/staff engineer):**
[Design decisions. Cross-system reasoning. Novel application.
 Edge cases. At-scale behaviour. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):**
[Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale? 3-5 sentences.]

---

### ⚙️ How It Works
[Summarized but complete mechanism. Step-by-step.
 ASCII diagrams where helpful. WHY each step exists.
 Happy path + failure path.]

---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[Input] -> [Step 1] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [Output]

**FAILURE PATH:**
[THIS CONCEPT fails] -> [cascade] -> [observable symptom]

**WHAT CHANGES AT SCALE:**
[2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### 💻 Code Example
[REQUIRED if programmatic. SKIP for pure theory.]
[BAD then GOOD. Real-world examples. Max 70 chars/line.
 Minimum 2 examples. Production-grade.]

**How to test / verify correctness:**
[1-3 sentences: testing strategy.]

---

### 📌 Quick Reference Card

**WHAT IT IS:** [1 sentence]
**PROBLEM IT SOLVES:** [1 sentence]
**KEY INSIGHT:** [1 sentence]
**USE WHEN:** [conditions - 1-2 sentences]
**AVOID WHEN:** [conditions - 1-2 sentences]
**ANTI-PATTERN:** [common misuse - 1 sentence]
**TRADE-OFF:** [gain vs cost - 1 sentence]
**ONE-LINER:** [memorable metaphor - 1 sentence]
**KEY NUMBERS:** [2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**
1. [Most important insight]
2. [Key trade-off or constraint]
3. [Production gotcha]

**Interview one-liner:**
"[30-second explanation showing depth]"

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [Teach to a junior in 2 min without notes]
2. **DEBUG:** [Diagnose a specific failure from symptoms]
3. **DECIDE:** [Choose this vs alternative under pressure]
4. **BUILD:** [Implement/configure in production context]
5. **EXTEND:** [Apply principle to a different domain]

---

### 💡 The Surprising Truth
[2-4 sentences. One counterintuitive fact. Specific.
 Makes this concept permanently memorable.]

---

### ⚖️ Comparison Table
[CONDITIONAL: include only when 2+ alternatives exist.]

| Dimension    | Option A      | Option B      |
|--------------|---------------|---------------|
| [Trade-off]  | [value]       | [value]       |
| Best for     | [scenario]    | [scenario]    |

**Decision framework:**
Need [condition]? -> Choose [option].

---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [wrong belief] | [actual truth] |
| 2 | [wrong belief] | [actual truth] |
| 3 | [wrong belief] | [actual truth] |
| 4 | [wrong belief] | [actual truth] |

---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [name]**
**Symptom:** [observable behavior]
**Root Cause:** [why it happens]
**Diagnostic:**
```
[real command]
```
**Fix:** [BAD then GOOD]
**Prevention:** [how to prevent]

[Repeat for modes 2, 3+...]

---

### 🎯 Interview Deep-Dive

**Q1 [JUNIOR]: [Conceptual question - foundational]**

*Why they ask:* [What skill this probes]

**Answer:**
[Complete structured answer. 200-500 words.
 Learning progression: surface -> depth -> insight.]

*What separates good from great:* [1 sentence]

---

**Q2 [MID]: [Debugging/diagnosis scenario]**

*Why they ask:* [What this evaluates]

**Answer:**
[Complete answer with diagnostic steps, tools, commands.]

*What separates good from great:* [1 sentence]

---

**Q3 [SENIOR]: [Architecture/design question]**

*Why they ask:* [What mastery signal this tests]

**Answer:**
[Complete answer with design rationale, trade-offs.]

*What separates good from great:* [1 sentence]

---

**Q4 [SENIOR]: [Trade-off decision question]**

*Why they ask:* [What decision-making skill this probes]

**Answer:**
[Complete answer with decision framework, conditions.]

*What separates good from great:* [1 sentence]

---

**Q5 [STAFF]: [Production scenario question]**

*Why they ask:* [What operational depth this tests]

**Answer:**
[Complete answer with metrics, thresholds, remediation.]

*What separates good from great:* [1 sentence]

---

[Q6-Q10+: Continue based on difficulty scaling.
 easy: 5 min. medium: 7 min. hard: 10 min.
 Cover at least 5 of the 8 question categories.
 Must include at least 1 DEBUGGING + 1 TRADE-OFF.
 Tag each: [JUNIOR] [MID] [SENIOR] [STAFF].
 End each answer with "What separates good from great".]

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [Keyword] - [why needed]

**Builds on this (learn these next):**
- [Keyword] - [what it adds]

**Alternatives / Comparisons:**
- [Keyword] - [when to prefer it]"""

content = content[:skel_start] + new_skeleton + content[skel_end:]
print("  Done: skeleton rewritten")


# ================================================================
# Phase 5: Rewrite Section 8 Checklist
# ================================================================
print("Phase 5: Section 8 checklist...")

CHK_START = "Run before outputting any entry:"
CHK_END = "  [ ] Security considerations addressed where applicable"

chk_start = content.find(CHK_START)
chk_end = content.find(CHK_END) + len(CHK_END)

if chk_start == -1 or chk_end <= len(CHK_END):
    print("  ERROR: Could not find checklist markers")
    sys.exit(1)

new_checklist = """Run before outputting any entry:

FRONTMATTER:
  [ ] title matches filename (without .md)
  [ ] topic matches folder name
  [ ] keywords array lists ALL keywords in file
  [ ] No emojis in frontmatter
  [ ] No em dashes anywhere
  [ ] File starts at byte 0 with "---"
  [ ] version: 3 (SPEC_VERSION)

STRUCTURE (per keyword):
  [ ] 3.1  Title - H1 with keyword name
  [ ] 3.2  TL;DR - one sentence, max 25 words
  [ ] 3.3  Problem This Solves (all 4 parts + EVOLUTION)
  [ ] 3.4  Textbook Definition
  [ ] 3.5  Understand It in 30 Seconds (3 parts)
  [ ] 3.6  First Principles (invariants + trade-offs +
           essential/accidental)
  [ ] 3.7  Mental Model / Analogy (with breakdown note)
  [ ] 3.8  Gradual Depth - Five Levels (incl. Level 5
           with expert thinking cues)
  [ ] 3.9  How It Works (summarized but complete)
  [ ] 3.10 Complete Picture (normal + failure + scale)
  [ ] 3.11 Code Example (if programmatic, BAD then GOOD)
  [ ] 3.12 Quick Reference Card (9 fields incl KEY NUMBERS
           + 3 things + interview one-liner)
  [ ] 3.13 Mastery Checklist (5 indicators: EXPLAIN/DEBUG/
           DECIDE/BUILD/EXTEND)
  [ ] 3.14 Surprising Truth (one fact)
  [ ] 3.15 Comparison Table (if 2+ alternatives exist)
  [ ] 3.16 Common Misconceptions (min 4 rows)
  [ ] 3.17 Failure Modes and Diagnosis (min 3 modes
           with real diagnostic commands)
  [ ] 3.18 Interview Deep-Dive (capstone, scaled by
           difficulty, with difficulty tags)
  [ ] 3.19 Related Keywords (3 categories)

INTERVIEW DEEP-DIVE QUALITY:
  [ ] Question count meets difficulty minimum
       (easy: 5, medium: 7, hard: 10)
  [ ] At least 5 of 8 question categories covered
  [ ] At least 1 DEBUGGING question present
  [ ] At least 1 TRADE-OFF question present
  [ ] Every question tagged with difficulty level
       ([JUNIOR] [MID] [SENIOR] [STAFF])
  [ ] Every question has a COMPLETE answer (not bullets)
  [ ] Every answer ends with "What separates good from
       great" insight line
  [ ] Answers show learning progression
  [ ] Answers include code/commands/metrics where relevant
  [ ] Answers would impress a senior interviewer
  [ ] No duplicate questions across keywords in same file

NEW IN v3.0 - ADDITIONAL CHECKS:
  [ ] Mastery Checklist: 5 indicators in EXPLAIN/DEBUG/
       DECIDE/BUILD/EXTEND order, each concept-specific
  [ ] Quick Reference Card: KEY NUMBERS field present
       with 2-3 real thresholds/defaults
  [ ] Interview Deep-Dive positioned as capstone (after
       Failure Modes, before Related Keywords)
  [ ] Each interview question tagged [JUNIOR]/[MID]/
       [SENIOR]/[STAFF]
  [ ] Each answer ends with "What separates good from
       great" insight line
  [ ] Common Misconceptions: min 4 rows, ordered by danger
  [ ] Failure Modes: min 3 modes with real commands
  [ ] Failure Modes: security mode present if attack
       surface exists
  [ ] Related Keywords: all 3 categories populated
  [ ] Quick Reference Card: AVOID WHEN and ANTI-PATTERN
       fields present (shows mastery through contrast)
  [ ] Level 5 Gradual Depth present (expert thinking)
  [ ] Comparison Table present if alternatives exist

QUALITY GATES:
  [ ] Multi-perspective test passed (user + implementor
       + debugger angles)
  [ ] Feynman test passed (no undefined jargon)
  [ ] Contrast test passed (when NOT to use is clear)
  [ ] No deduplication violations across keywords
       in same file

FORMATTING:
  [ ] No code line exceeds 70 characters
  [ ] No ASCII diagram exceeds 59 characters wide
  [ ] No paragraph exceeds 5 sentences
  [ ] BAD pattern before GOOD pattern in all code
  [ ] Every ### preceded by --- with blank lines
  [ ] Keywords separated by double horizontal rules
  [ ] File is UTF-8 without BOM

CONTENT QUALITY:
  [ ] WHY before WHAT in every explanation
  [ ] Reader can understand fully without external lookup
  [ ] Production reality included (not just theory)
  [ ] Failure modes covered with real diagnostics
  [ ] No fabricated benchmarks or claims
  [ ] Every paragraph earns its place
  [ ] Security considerations addressed where applicable"""

content = content[:chk_start] + new_checklist + content[chk_end:]
print("  Done: checklist rewritten")


# ================================================================
# Phase 6: Rewrite Section 9 Version Detection
# ================================================================
print("Phase 6: Section 9 version detection...")

V9_START = "A file is v1.0 (version: 1) if it has the original 14"
V9_END = "Set version: 2 only after ALL v2.0 markers are present."

v9_start = content.find(V9_START)
v9_end = content.find(V9_END) + len(V9_END)

if v9_start == -1 or v9_end <= len(V9_END):
    print("  ERROR: Could not find version detection markers")
    sys.exit(1)

new_v9 = """A file is v1.0 (version: 1) if it has the original 14
sections: Title through Interview Deep-Dive, with
4-level Gradual Depth and Quick Recall format.

A file is v2.0 (version: 2) if it ALSO has:
  - Gradual Depth - Five Levels (with Level 5)
  - Quick Reference Card (8-field format replacing
    Quick Recall)
  - Common Misconceptions (min 4 rows)
  - Failure Modes and Diagnosis (min 3 with commands)
  - Related Keywords (3 categories)
  - Comparison Table (if alternatives exist)
  - Interview Deep-Dive scaled by difficulty
    (easy: 5, medium: 7, hard: 10)
  - AVOID WHEN + ANTI-PATTERN in Quick Reference Card

A file is v3.0 (version: 3) if it ALSO has:
  - Mastery Checklist section with 5 indicators
    (EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
  - KEY NUMBERS field in Quick Reference Card
  - Interview Deep-Dive in capstone position (after
    Failure Modes, before Related Keywords)
  - Difficulty tags on each interview question
    ([JUNIOR] [MID] [SENIOR] [STAFF])
  - "What separates good from great" line after each
    interview answer
  - Section order: Quick Ref -> Mastery Checklist ->
    Surprising Truth -> Comparison -> Misconceptions ->
    Failure Modes -> Interview Deep-Dive -> Related

Set version: 3 only after ALL v3.0 markers are present."""

content = content[:v9_start] + new_v9 + content[v9_end:]
print("  Done: version detection rewritten")


# ================================================================
# Phase 7: Update depth calibration section
# ================================================================
print("Phase 7: Depth calibration updates...")

# Add mastery checklist to depth calibration
content = safe_replace(content,
    "    - 5 interview questions minimum",
    "    - 5 interview questions minimum\n"
    "    - 5 mastery checklist indicators",
    "easy depth mastery")

content = safe_replace(content,
    "    - 7 interview questions minimum\n"
    "    - Comparison table strongly recommended",
    "    - 7 interview questions minimum\n"
    "    - 5 mastery checklist indicators\n"
    "    - Comparison table strongly recommended",
    "medium depth mastery")

content = safe_replace(content,
    "    - 10 interview questions minimum\n"
    "    - Comparison table required if alternatives exist",
    "    - 10 interview questions minimum\n"
    "    - 5 mastery checklist indicators\n"
    "    - Comparison table required if alternatives exist",
    "hard depth mastery")

print("  Done: depth calibration updated")


# ================================================================
# Final: Write
# ================================================================

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(content)
print(f"\n{'='*60}")
print(f"SUCCESS: INTERVIEW_PROMPT.md upgraded to v3.0")
print(f"  Original: {original_len:,} chars")
print(f"  Updated:  {new_len:,} chars")
print(f"  Delta:    {new_len - original_len:+,} chars")

if errors:
    print(f"\n  WARNINGS ({len(errors)}):")
    for e in errors:
        print(f"    - {e}")
else:
    print(f"  No warnings or errors")
