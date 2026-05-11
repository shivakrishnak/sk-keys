#!/usr/bin/env python3
"""Upgrade INTERVIEW_PROMPT.md from v3.0 to v3.1.

Changes:
1. Version labels: v3.0 -> v3.1
2. Add P16-P18 interview principles after P15
3. Add Senior-to-Staff Leap to Section 3.8
4. Add TRIGGER PHRASE + OPENING SENTENCE to Section 3.12
5. Add Rapid Decision Tree to Section 3.15
6. Enhance Section 3.18 Interview Deep-Dive
7. Add interview strategy guidance to Section 5
8. Update Section 6 skeleton
9. Update Section 8 checklist
10. Update Section 9 version detection
"""

import re
import sys

FILE = r'c:\ASK\MyWorkspace\sk-keys\interview\config\INTERVIEW_PROMPT.md'


def read_file():
    with open(FILE, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(content):
    with open(FILE, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def apply_change(content, old, new, label):
    if old not in content:
        print(f"  WARNING: '{label}' - old text not found!")
        return content, False
    count = content.count(old)
    if count > 1:
        print(f"  WARNING: '{label}' - old text found {count} times, replacing first only")
        pos = content.find(old)
        content = content[:pos] + new + content[pos + len(old):]
        return content, True
    content = content.replace(old, new)
    print(f"  OK: {label}")
    return content, True


def main():
    content = read_file()
    original_len = len(content)
    print(f"Read {original_len} chars from INTERVIEW_PROMPT.md")

    # =================================================================
    # 1. VERSION LABELS
    # =================================================================
    print("\n--- Phase 1: Version labels ---")

    # Header title
    content, _ = apply_change(content,
        '# Interview Mastery Dictionary - Master Prompt v3.0',
        '# Interview Mastery Dictionary - Master Prompt v3.1',
        'Header title')

    # SPEC_LABEL in version registry
    content, _ = apply_change(content,
        "| `SPEC_LABEL`   | `v3.0` | Human-readable label for headers/commits     |",
        "| `SPEC_LABEL`   | `v3.1` | Human-readable label for headers/commits     |",
        'SPEC_LABEL registry')

    # Inner header
    content, _ = apply_change(content,
        'INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v3.0',
        'INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v3.1',
        'Inner header')

    # All "v3.0" references in invocation section -> v3.1
    content = content.replace(
        'Follow Interview Mastery Prompt v3.0 exactly.',
        'Follow Interview Mastery Prompt v3.1 exactly.')
    print("  OK: Invocation references v3.0 -> v3.1")

    # =================================================================
    # 2. ADD P16-P18 AFTER P15
    # =================================================================
    print("\n--- Phase 2: Add P16-P18 principles ---")

    p16_18 = '''
-------------- INTERVIEW-SPECIFIC PRINCIPLES -------------------

PRINCIPLE 16: BEHAVIORAL READINESS
  Every technical concept must connect to a real experience.
  "When have you used this in production?" is asked in 90%
  of interviews. The candidate must have an answer ready -
  or an honest alternative: "I haven't used this directly,
  but here's how I'd approach it based on [related experience]."
  For every concept: map to Situation -> Task -> Action ->
  Result. If no direct experience: prepare a study-based
  answer that shows how you'd validate your approach.

PRINCIPLE 17: INTERVIEWER AWARENESS
  Every explanation must consider what the interviewer is
  silently evaluating. Candidates need to know:
    - What signals "junior" vs "senior" vs "staff" thinking
    - What phrasing triggers "this person has experience"
    - What response patterns signal depth vs memorization
  Key signals to send naturally (without showing off):
    - "In production, we saw..." (not "the docs say")
    - "Most people think X, but actually Y because..."
    - "The trade-off between A and B means..."
    - "I taught the team to avoid [mistake] by..."

PRINCIPLE 18: PRESSURE RECOVERY
  Interviews are high-pressure. Candidates WILL forget or
  get stuck. Knowing what to say when you don't know is
  AS important as knowing the answer. Recovery strategies:
    - Draw a blank: "Let me work through this from first
      principles. The problem this solves is..."
    - Realize you're wrong mid-answer: "I just realized my
      assumption about X was incorrect. The actual behavior
      is Y because Z."
    - Don't know: "I don't know the specific answer, but
      here's how I'd find out: [approach]. Based on
      [related concept], I'd expect [educated guess]."
    - Confused question: "Let me clarify - are you asking
      about [A] or [B]? I want to make sure I address
      what you're actually asking."
  Self-correction is a SENIOR signal, not a weakness.'''

    content, _ = apply_change(content,
        '''PRINCIPLE 15: MASTERY THROUGH CONTRAST
  Show the precise boundary where this concept STOPS being
  the right answer and an alternative takes over.
  "If you can't explain when NOT to use it, you don't
   truly understand it."

================================================================
SECTION 2: FILE FORMAT & FOLDER STRUCTURE''',
        '''PRINCIPLE 15: MASTERY THROUGH CONTRAST
  Show the precise boundary where this concept STOPS being
  the right answer and an alternative takes over.
  "If you can't explain when NOT to use it, you don't
   truly understand it."
''' + p16_18 + '''

================================================================
SECTION 2: FILE FORMAT & FOLDER STRUCTURE''',
        'P16-P18 insertion')

    # =================================================================
    # 3. SENIOR-TO-STAFF LEAP IN 3.8
    # =================================================================
    print("\n--- Phase 3: Senior-to-Staff Leap ---")

    content, _ = apply_change(content,
        '''  **Level 4 - Production mastery (senior/staff engineer):**
  [Design decisions. Historical context. Alternative designs
   rejected. Edge cases. Cross-system reasoning. Novel
   application. 5-8 sentences.]

  **Level 5 - Distinguished (expert thinking):''',
        '''  **Level 4 - Production mastery (senior/staff engineer):**
  [Design decisions. Historical context. Alternative designs
   rejected. Edge cases. Cross-system reasoning. Novel
   application. 5-8 sentences.]

  **The Senior-to-Staff Leap (what separates them):**
  A Senior says: "[What a competent senior would say about
   this concept - correct but conventional]"
  A Staff says: "[What demonstrates the next level of
   abstraction, cross-system thinking, or novel insight]"
  The difference: [1 sentence explaining the conceptual gap
   - what mental model shift occurs at the staff level]

  **Level 5 - Distinguished (expert thinking):''',
        'Senior-to-Staff Leap in 3.8 spec')

    # Also add to skeleton in Section 6
    content, _ = apply_change(content,
        '''**Level 4 - Production mastery (senior/staff engineer):**
[Design decisions. Cross-system reasoning. Novel application.
 Edge cases. At-scale behaviour. 5-8 sentences.]

**Level 5 - Distinguished (expert thinking):''',
        '''**Level 4 - Production mastery (senior/staff engineer):**
[Design decisions. Cross-system reasoning. Novel application.
 Edge cases. At-scale behaviour. 5-8 sentences.]

**The Senior-to-Staff Leap:**
A Senior says: "[What a competent senior would say]"
A Staff says: "[What demonstrates next-level abstraction]"
The difference: [1 sentence - the mental model shift]

**Level 5 - Distinguished (expert thinking):''',
        'Senior-to-Staff Leap in skeleton')

    # =================================================================
    # 4. QUICK REF CARD: TRIGGER PHRASE + OPENING SENTENCE
    # =================================================================
    print("\n--- Phase 4: Quick Ref new fields ---")

    # In spec section 3.12
    content, _ = apply_change(content,
        '''  **KEY NUMBERS:** [2-3 critical thresholds, defaults,
    or limits engineers must know - e.g., "default
    pool: 200", "99p target: <100ms"]

  **If you remember only 3 things:''',
        '''  **KEY NUMBERS:** [2-3 critical thresholds, defaults,
    or limits engineers must know - e.g., "default
    pool: 200", "99p target: <100ms"]
  **TRIGGER PHRASE:** [5-7 words that activate your full
    mental model of this concept - what you'd whisper to
    yourself before answering an interview question]
  **OPENING SENTENCE:** [The first sentence you'd say if
    asked "explain [CONCEPT]" - must show immediate depth,
    not a textbook definition]

  **If you remember only 3 things:''',
        'Quick Ref TRIGGER PHRASE + OPENING SENTENCE in spec')

    # In skeleton section 6
    content, _ = apply_change(content,
        '''**KEY NUMBERS:** [2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:''',
        '''**KEY NUMBERS:** [2-3 critical thresholds/defaults/limits]
**TRIGGER PHRASE:** [5-7 words activating full mental model]
**OPENING SENTENCE:** [First sentence showing immediate depth]

**If you remember only 3 things:''',
        'Quick Ref new fields in skeleton')

    # Update field count references
    content, _ = apply_change(content,
        '  - No ASCII box (encoding-safe)\n  - The 9 fields give instant recall under pressure',
        '  - No ASCII box (encoding-safe)\n  - The 11 fields give instant recall under pressure',
        '9 -> 11 fields in spec')

    # =================================================================
    # 5. RAPID DECISION TREE IN 3.15
    # =================================================================
    print("\n--- Phase 5: Rapid Decision Tree ---")

    content, _ = apply_change(content,
        '''  **Decision framework:**
  Need [condition A]? -> Choose X.
  Need [condition B]? -> Prefer Y.
  Need [condition C]? -> Avoid Z.

Rules:
  - Minimum 4 comparison dimensions''',
        '''  **Decision framework:**
  Need [condition A]? -> Choose X.
  Need [condition B]? -> Prefer Y.
  Need [condition C]? -> Avoid Z.

  **Rapid Decision Tree (30 seconds under pressure):**
  IF [primary differentiator] THEN choose [Option A]
  ELSE IF [secondary condition] THEN choose [Option B]
  ELSE [fallback heuristic] -> [default recommendation]

Rules:
  - Minimum 4 comparison dimensions''',
        'Rapid Decision Tree in 3.15 spec')

    # In skeleton
    content, _ = apply_change(content,
        '''**Decision framework:**
Need [condition]? -> Choose [option].

---

### ⚠️ Common Misconceptions''',
        '''**Decision framework:**
Need [condition]? -> Choose [option].

**Rapid Decision Tree (30 seconds):**
IF [condition] THEN choose [Option A]
ELSE IF [condition] THEN choose [Option B]
ELSE [fallback] -> [default]

---

### ⚠️ Common Misconceptions''',
        'Rapid Decision Tree in skeleton')

    # =================================================================
    # 6. INTERVIEW DEEP-DIVE ENHANCEMENTS (3.18)
    # =================================================================
    print("\n--- Phase 6: Interview Deep-Dive enhancements ---")

    # 6a. Add timing guidelines + pacing signals after PURPOSE block
    content, _ = apply_change(content,
        '''DISTINCTION:
  This section provides REAL interview Q&A with COMPLETE
  ANSWERS. Not hints, not bullet points - full structured
  answers that teach the reader how to think through problems
  and articulate solutions under pressure.

QUESTION REQUIREMENTS:''',
        '''DISTINCTION:
  This section provides REAL interview Q&A with COMPLETE
  ANSWERS. Not hints, not bullet points - full structured
  answers that teach the reader how to think through problems
  and articulate solutions under pressure.

ANSWER TIMING GUIDELINES (include at section start):

  | Question Type | Target Duration | Signals               |
  |---------------|-----------------|-----------------------|
  | Conceptual    | 45-90 seconds   | Direct, confident     |
  | Debugging     | 90-150 seconds  | Systematic diagnosis  |
  | Architecture  | 120-180 seconds | Trade-off exploration |
  | Trade-off     | 60-120 seconds  | Decision framework    |
  | Behavioral    | 60-120 seconds  | Clear STAR structure  |

  Pacing signals to teach the reader:
  - "Should I go deeper on [aspect]?" -> collaboration
  - "The key insight here is..." -> signals what matters
  - "In production, we actually saw..." -> experience

QUESTION REQUIREMENTS:''',
        'Timing guidelines in 3.18')

    # 6b. Add BEHAVIORAL as 9th category + cross-cutting requirement
    content, _ = apply_change(content,
        '''    * COMPARISON: "Compare X vs Y vs Z for use case U."
  - At least one DEBUGGING question per keyword (mandatory)
  - At least one TRADE-OFF question per keyword (mandatory)''',
        '''    * COMPARISON: "Compare X vs Y vs Z for use case U."
    * BEHAVIORAL: "Tell me about a time you used X in
      production. What went wrong? What would you do
      differently?" (STAR format: Situation -> Task ->
      Action -> Result)
  - At least one DEBUGGING question per keyword (mandatory)
  - At least one TRADE-OFF question per keyword (mandatory)
  - At least one BEHAVIORAL question for medium/hard
    keywords (mandatory) - tests real experience vs theory''',
        'BEHAVIORAL category + requirement')

    # 6c. Update question minimums (5/7/10 -> 7/9/12)
    content, _ = apply_change(content,
        '''  - Question count scales with difficulty:
      easy keywords:  minimum 5 questions
      medium keywords: minimum 7 questions
      hard keywords:  minimum 10 questions
  - Questions MUST cover these categories (at least 5
    of the 8 categories per keyword):''',
        '''  - Question count scales with difficulty:
      easy keywords:  minimum 7 questions
      medium keywords: minimum 9 questions
      hard keywords:  minimum 12 questions
  - Questions MUST cover these categories (at least 5
    of the 9 categories per keyword):''',
        'Question minimums 5/7/10 -> 7/9/12')

    # 6d. Add *Likely follow-up:* field to Q&A format
    content, _ = apply_change(content,
        '''  **Q1 [JUNIOR]: [Interview question - scenario-based]**

  *Why they ask:* [What the interviewer is evaluating -
   1 sentence]

  **Answer:**''',
        '''  **Q1 [JUNIOR]: [Interview question - scenario-based]**

  *Why they ask:* [What the interviewer is evaluating -
   1 sentence]
  *Likely follow-up:* [What they'll ask next if you
   answer well - prepares the candidate for the full
   conversation chain, not just one question]

  **Answer:**''',
        'Likely follow-up in Q&A spec format')

    # 6e. Add cross-cutting question to skeleton (after Q5)
    content, _ = apply_change(content,
        '''[Q6-Q10+: Continue based on difficulty scaling.
 easy: 5 min. medium: 7 min. hard: 10 min.
 Cover at least 5 of the 8 question categories.
 Must include at least 1 DEBUGGING + 1 TRADE-OFF.
 Tag each: [JUNIOR] [MID] [SENIOR] [STAFF].
 End each answer with "What separates good from great".]''',
        '''**Q6 [MID]: [Behavioral question - STAR format]**

*Why they ask:* [Tests real experience vs theory]
*Likely follow-up:* [Deeper probe on the action taken]

**Answer:**
[Situation -> Task -> Action -> Result with metrics.
 If no direct experience: "I haven't used this directly,
 but based on [related experience], here's how I'd
 approach it and what I'd validate first."]

*What separates good from great:* [1 sentence]

---

[Q7-Q12+: Continue based on difficulty scaling.
 easy: 7 min. medium: 9 min. hard: 12 min.
 Cover at least 5 of the 9 question categories.
 Must include: 1 DEBUGGING + 1 TRADE-OFF + 1 BEHAVIORAL.
 For hard keywords: include 1 CROSS-CUTTING question
 ("How does [CONCEPT] interact with [OTHER CONCEPT]
  under load/failure?").
 Tag each: [JUNIOR] [MID] [SENIOR] [STAFF].
 End each answer with "What separates good from great".
 Add *Likely follow-up:* to each question.]''',
        'Behavioral Q + cross-cutting + updated scaling in skeleton')

    # 6f. Add *Likely follow-up:* to Q1-Q5 in skeleton
    # Q1
    content, _ = apply_change(content,
        '''**Q1 [JUNIOR]: [Conceptual question - foundational]**

*Why they ask:* [What skill this probes]

**Answer:**
[Complete structured answer. 200-500 words.
 Learning progression: surface -> depth -> insight.]''',
        '''**Q1 [JUNIOR]: [Conceptual question - foundational]**

*Why they ask:* [What skill this probes]
*Likely follow-up:* [What they'll ask next]

**Answer:**
[Complete structured answer. 200-500 words.
 Learning progression: surface -> depth -> insight.]''',
        'Likely follow-up on Q1 skeleton')

    # Q2
    content, _ = apply_change(content,
        '''**Q2 [MID]: [Debugging/diagnosis scenario]**

*Why they ask:* [What this evaluates]

**Answer:**
[Complete answer with diagnostic steps, tools, commands.]''',
        '''**Q2 [MID]: [Debugging/diagnosis scenario]**

*Why they ask:* [What this evaluates]
*Likely follow-up:* [Next depth probe]

**Answer:**
[Complete answer with diagnostic steps, tools, commands.]''',
        'Likely follow-up on Q2 skeleton')

    # Q3
    content, _ = apply_change(content,
        '''**Q3 [SENIOR]: [Architecture/design question]**

*Why they ask:* [What mastery signal this tests]

**Answer:**
[Complete answer with design rationale, trade-offs.]''',
        '''**Q3 [SENIOR]: [Architecture/design question]**

*Why they ask:* [What mastery signal this tests]
*Likely follow-up:* [Trade-off or scale probe]

**Answer:**
[Complete answer with design rationale, trade-offs.]''',
        'Likely follow-up on Q3 skeleton')

    # Q4
    content, _ = apply_change(content,
        '''**Q4 [SENIOR]: [Trade-off decision question]**

*Why they ask:* [What decision-making skill this probes]

**Answer:**
[Complete answer with decision framework, conditions.]''',
        '''**Q4 [SENIOR]: [Trade-off decision question]**

*Why they ask:* [What decision-making skill this probes]
*Likely follow-up:* [Edge case or constraint probe]

**Answer:**
[Complete answer with decision framework, conditions.]''',
        'Likely follow-up on Q4 skeleton')

    # Q5
    content, _ = apply_change(content,
        '''**Q5 [STAFF]: [Production scenario question]**

*Why they ask:* [What operational depth this tests]

**Answer:**
[Complete answer with metrics, thresholds, remediation.]''',
        '''**Q5 [STAFF]: [Production scenario question]**

*Why they ask:* [What operational depth this tests]
*Likely follow-up:* [Scale or failure cascade probe]

**Answer:**
[Complete answer with metrics, thresholds, remediation.]''',
        'Likely follow-up on Q5 skeleton')

    # =================================================================
    # 7. INTERVIEW STRATEGY GUIDANCE (Section 5)
    # =================================================================
    print("\n--- Phase 7: Interview strategy guidance ---")

    content, _ = apply_change(content,
        '''THE DANGEROUS ENGINEER TEST:
  After reading this entry, can the reader:
  1. Use this concept correctly under production pressure?
  2. Diagnose when it breaks without Googling?
  3. Explain to someone else why NOT to misuse it?
  4. Choose between this and alternatives in <60 seconds?
  If any answer is NO: strengthen the relevant section.

TRUTHFULNESS & ANTI-HALLUCINATION:''',
        '''THE DANGEROUS ENGINEER TEST:
  After reading this entry, can the reader:
  1. Use this concept correctly under production pressure?
  2. Diagnose when it breaks without Googling?
  3. Explain to someone else why NOT to misuse it?
  4. Choose between this and alternatives in <60 seconds?
  If any answer is NO: strengthen the relevant section.

THE PRESSURE TEST (v3.1):
  Read the answer to Q1 aloud while timing yourself.
  If you can't finish in 90 seconds: the answer is too long
  or insufficiently structured.
  If you finish in 30 seconds: the answer lacks depth.
  Every answer must be deliverable under interview pressure.

THE COLD CALL TEST (v3.1):
  A candidate who hasn't reviewed this concept in a week
  should be able to use the TRIGGER PHRASE and OPENING
  SENTENCE from the Quick Reference Card to deliver a
  passing answer immediately.

----------------------------------------------------------------
INTERVIEW SIGNAL REFERENCE (v3.1)
----------------------------------------------------------------

  What interviewers silently evaluate based on response type:

  | Your Response Type               | Signal Received      |
  |----------------------------------|----------------------|
  | Textbook definition only         | "Memorized, no exp"  |
  | Includes trade-offs unprompted   | "Thinks in systems"  |
  | Mentions when it breaks          | "Production scars"   |
  | Self-corrects mid-answer         | "Intellectually      |
  |                                  |  honest, senior"     |
  | "I don't know, but here's how    | "Resourceful,        |
  |  I'd find out"                   |  hire-worthy"        |

  What your opening words signal:

  | If you start with...             | They think...        |
  |----------------------------------|----------------------|
  | "So, [CONCEPT] is..."            | Textbook learner     |
  | "The problem [CONCEPT] solves.." | Understands WHY      |
  | "Before [CONCEPT], we had to..." | Historical context   |
  | "The simplest way to think..."   | Can teach others     |

  This reference is SPEC-LEVEL guidance. Do NOT create a
  per-keyword "Interviewer Psychology" section. Instead,
  use this knowledge when crafting Interview Deep-Dive
  answers - ensure answers demonstrate experience signals,
  not textbook recall.

----------------------------------------------------------------
ANSWER CALIBRATION REFERENCE (v3.1)
----------------------------------------------------------------

  Use this scale when writing Interview Deep-Dive answers
  to ensure every answer reaches "Good" or "Excellent" level:

  | Level     | Characteristics                         |
  |-----------|-----------------------------------------|
  | Failing   | Textbook definition only. No trade-offs |
  |           | No experience signals. No depth.        |
  | Passing   | Basic knowledge. Mentions alternatives. |
  |           | No production nuance. Surface-level.    |
  | Good      | Shows decision framework. Knows when to |
  |           | use AND avoid. Mentions real trade-offs. |
  | Excellent | Production scars. Specific metrics. Has |
  |           | diagnostic approach. Cross-system view.  |
  | Mastery   | Could improve the design. Cross-domain  |
  |           | pattern. Insight others would miss.      |

  The "20-second upgrade" - if an answer is at Passing level,
  add one of these to reach Good:
    - "...but it fails when [condition]."
    - "The trade-off is [gain] vs [cost]."
    - "For example, in production we saw [specific scenario]."

  This reference is SPEC-LEVEL guidance. Do NOT create a
  per-keyword "Answer Quality Scale" section. Instead,
  ensure every Interview Deep-Dive answer is calibrated
  to at least "Good" level using this scale.

TRUTHFULNESS & ANTI-HALLUCINATION:''',
        'Interview strategy guidance in Section 5')

    # =================================================================
    # 8. UPDATE DEPTH CALIBRATION (question minimums)
    # =================================================================
    print("\n--- Phase 8: Depth calibration ---")

    content, _ = apply_change(content,
        '''  easy keywords:
    - Level 1-3 emphasis, Levels 4-5 brief
    - 2 code examples minimum
    - 3 failure modes minimum
    - 4 misconceptions minimum
    - 5 interview questions minimum
    - 5 mastery checklist indicators

  medium keywords:
    - Level 2-4 emphasis, Level 5 encouraged
    - 3 code examples minimum
    - 3 failure modes minimum
    - 5 misconceptions minimum
    - 7 interview questions minimum
    - 5 mastery checklist indicators
    - Comparison table strongly recommended

  hard keywords:
    - Level 3-5 emphasis, Level 5 required
    - 4 code examples minimum
    - 4 failure modes minimum
    - 6 misconceptions minimum
    - 10 interview questions minimum
    - 5 mastery checklist indicators
    - Comparison table required if alternatives exist''',
        '''  easy keywords:
    - Level 1-3 emphasis, Levels 4-5 brief
    - 2 code examples minimum
    - 3 failure modes minimum
    - 4 misconceptions minimum
    - 7 interview questions minimum
    - 5 mastery checklist indicators
    - Senior-to-Staff Leap encouraged

  medium keywords:
    - Level 2-4 emphasis, Level 5 encouraged
    - 3 code examples minimum
    - 3 failure modes minimum
    - 5 misconceptions minimum
    - 9 interview questions minimum (incl 1 BEHAVIORAL)
    - 5 mastery checklist indicators
    - Senior-to-Staff Leap required
    - Comparison table strongly recommended

  hard keywords:
    - Level 3-5 emphasis, Level 5 required
    - 4 code examples minimum
    - 4 failure modes minimum
    - 6 misconceptions minimum
    - 12 interview questions minimum (incl 1 BEHAVIORAL
      + 1 CROSS-CUTTING)
    - 5 mastery checklist indicators
    - Senior-to-Staff Leap required
    - Comparison table required if alternatives exist''',
        'Depth calibration question minimums')

    # =================================================================
    # 9. UPDATE SECTION 8 CHECKLIST
    # =================================================================
    print("\n--- Phase 9: Checklist updates ---")

    # Update Quick Ref checklist item
    content, _ = apply_change(content,
        '''  [ ] 3.12 Quick Reference Card (9 fields incl KEY NUMBERS
           + 3 things + interview one-liner)''',
        '''  [ ] 3.12 Quick Reference Card (11 fields incl KEY NUMBERS,
           TRIGGER PHRASE, OPENING SENTENCE + 3 things +
           interview one-liner)''',
        'Checklist Quick Ref 9->11 fields')

    # Update Gradual Depth checklist item
    content, _ = apply_change(content,
        '''  [ ] 3.8  Gradual Depth - Five Levels (incl. Level 5
           with expert thinking cues)''',
        '''  [ ] 3.8  Gradual Depth - Five Levels (incl. Level 5
           with expert thinking cues + Senior-to-Staff Leap)''',
        'Checklist Gradual Depth + Leap')

    # Update Interview Deep-Dive checklist item
    content, _ = apply_change(content,
        '''  [ ] 3.18 Interview Deep-Dive (capstone, scaled by
           difficulty, with difficulty tags)''',
        '''  [ ] 3.18 Interview Deep-Dive (capstone, scaled by
           difficulty, with difficulty tags + timing
           guidelines + likely follow-ups)''',
        'Checklist Interview Deep-Dive')

    # Update question count in checklist
    content, _ = apply_change(content,
        '''  [ ] Question count meets difficulty minimum
       (easy: 5, medium: 7, hard: 10)
  [ ] At least 5 of 8 question categories covered
  [ ] At least 1 DEBUGGING question present
  [ ] At least 1 TRADE-OFF question present''',
        '''  [ ] Question count meets difficulty minimum
       (easy: 7, medium: 9, hard: 12)
  [ ] At least 5 of 9 question categories covered
  [ ] At least 1 DEBUGGING question present
  [ ] At least 1 TRADE-OFF question present
  [ ] At least 1 BEHAVIORAL question for medium/hard''',
        'Checklist question counts + BEHAVIORAL')

    # Add new v3.1 checks
    content, _ = apply_change(content,
        '''  [ ] Comparison Table present if alternatives exist

QUALITY GATES:''',
        '''  [ ] Comparison Table present if alternatives exist

NEW IN v3.1 - ADDITIONAL CHECKS:
  [ ] Senior-to-Staff Leap present in Gradual Depth
       (required for medium/hard keywords)
  [ ] Quick Reference Card: TRIGGER PHRASE field present
  [ ] Quick Reference Card: OPENING SENTENCE field present
  [ ] Interview Deep-Dive: timing guidelines table at start
  [ ] Interview Deep-Dive: *Likely follow-up:* on each Q
  [ ] Interview Deep-Dive: 1+ BEHAVIORAL question for
       medium/hard keywords
  [ ] Interview Deep-Dive: 1+ CROSS-CUTTING question for
       hard keywords
  [ ] Rapid Decision Tree in Comparison Table (if present)
  [ ] Answers calibrated to "Good" or above per Answer
       Calibration Reference in Section 5

QUALITY GATES:''',
        'v3.1 checklist additions')

    # =================================================================
    # 10. UPDATE SECTION 9 VERSION DETECTION
    # =================================================================
    print("\n--- Phase 10: Version detection ---")

    content, _ = apply_change(content,
        '''A file is v3.0 (version: 3) if it ALSO has:
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

Set version: 3 only after ALL v3.0 markers are present.''',
        '''A file is v3.0 (version: 3) if it ALSO has:
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

A file meets v3.1 standard if it ALSO has:
  - Senior-to-Staff Leap in Gradual Depth section
  - TRIGGER PHRASE + OPENING SENTENCE in Quick Ref Card
  - *Likely follow-up:* on each Interview Deep-Dive Q
  - Rapid Decision Tree in Comparison Table (if present)
  - At least 1 BEHAVIORAL question for medium/hard keywords
  - Interview question minimums: easy 7, medium 9, hard 12
  v3.1 is a spec enhancement within SPEC_VERSION 3 - files
  do not need a version bump, but new content MUST conform
  to v3.1 standard.

Set version: 3 only after ALL v3.0 markers are present.
New content generated after v3.1 spec release must also
meet all v3.1 markers listed above.''',
        'v3.1 detection markers')

    # =================================================================
    # DONE
    # =================================================================
    print(f"\n=== SUMMARY ===")
    print(f"Original: {original_len} chars")
    print(f"Updated:  {len(content)} chars")
    print(f"Delta:    +{len(content) - original_len} chars")

    write_file(content)
    print(f"\nFile written successfully.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
