#!/usr/bin/env python3
"""Merge v3.0/v3.1 distinction into unified v3 across interview config files."""

import sys

def apply(content, old, new, label):
    if old not in content:
        print(f"  SKIP: '{label}' - not found")
        return content
    count = content.count(old)
    if count > 1:
        content = content.replace(old, new)
        print(f"  OK: {label} ({count} occurrences)")
    else:
        content = content.replace(old, new)
        print(f"  OK: {label}")
    return content


def fix_prompt(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = len(content)

    print("=== INTERVIEW_PROMPT.md ===")

    # 1. Title + headers
    content = apply(content,
        '# Interview Mastery Dictionary - Master Prompt v3.1',
        '# Interview Mastery Dictionary - Master Prompt v3',
        'Title')

    content = apply(content,
        "| `SPEC_LABEL`   | `v3.1` | Human-readable label for headers/commits     |",
        "| `SPEC_LABEL`   | `v3`   | Human-readable label for headers/commits     |",
        'SPEC_LABEL registry')

    content = apply(content,
        'INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v3.1',
        'INTERVIEW MASTERY DICTIONARY - MASTER PROMPT v3',
        'Inner header')

    # 2. Invocation references
    content = apply(content,
        'Follow Interview Mastery Prompt v3.1 exactly.',
        'Follow Interview Mastery Prompt v3 exactly.',
        'Invocation refs')

    # 3. Remove "(v3.1)" annotations from section names
    content = apply(content, 'THE PRESSURE TEST (v3.1):', 'THE PRESSURE TEST:', 'Pressure Test label')
    content = apply(content, 'THE COLD CALL TEST (v3.1):', 'THE COLD CALL TEST:', 'Cold Call Test label')
    content = apply(content, 'INTERVIEW SIGNAL REFERENCE (v3.1)', 'INTERVIEW SIGNAL REFERENCE', 'Signal Ref label')
    content = apply(content, 'ANSWER CALIBRATION REFERENCE (v3.1)', 'ANSWER CALIBRATION REFERENCE', 'Answer Cal label')

    # 4. Merge the two checklist blocks into one
    content = apply(content,
        """NEW IN v3.0 - ADDITIONAL CHECKS:
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
       Calibration Reference in Section 5""",
        """NEW IN v3 - ADDITIONAL CHECKS:
  [ ] Mastery Checklist: 5 indicators in EXPLAIN/DEBUG/
       DECIDE/BUILD/EXTEND order, each concept-specific
  [ ] Quick Reference Card: KEY NUMBERS field present
       with 2-3 real thresholds/defaults
  [ ] Quick Reference Card: TRIGGER PHRASE field present
  [ ] Quick Reference Card: OPENING SENTENCE field present
  [ ] Quick Reference Card: AVOID WHEN and ANTI-PATTERN
       fields present (shows mastery through contrast)
  [ ] Interview Deep-Dive positioned as capstone (after
       Failure Modes, before Related Keywords)
  [ ] Interview Deep-Dive: timing guidelines table at start
  [ ] Interview Deep-Dive: *Likely follow-up:* on each Q
  [ ] Each interview question tagged [JUNIOR]/[MID]/
       [SENIOR]/[STAFF]
  [ ] Each answer ends with "What separates good from
       great" insight line
  [ ] Interview Deep-Dive: 1+ BEHAVIORAL question for
       medium/hard keywords
  [ ] Interview Deep-Dive: 1+ CROSS-CUTTING question for
       hard keywords
  [ ] Common Misconceptions: min 4 rows, ordered by danger
  [ ] Failure Modes: min 3 modes with real commands
  [ ] Failure Modes: security mode present if attack
       surface exists
  [ ] Related Keywords: all 3 categories populated
  [ ] Level 5 Gradual Depth present (expert thinking)
  [ ] Senior-to-Staff Leap present in Gradual Depth
       (required for medium/hard keywords)
  [ ] Comparison Table present if alternatives exist
  [ ] Rapid Decision Tree in Comparison Table (if present)
  [ ] Answers calibrated to "Good" or above per Answer
       Calibration Reference in Section 5""",
        'Merge v3.0+v3.1 checklists -> v3')

    # 5. Merge version detection: v3.0 + v3.1 -> unified v3
    content = apply(content,
        """A file is v3.0 (version: 3) if it ALSO has:
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
meet all v3.1 markers listed above.""",
        """A file is v3 (version: 3) if it ALSO has:
  - Mastery Checklist section with 5 indicators
    (EXPLAIN/DEBUG/DECIDE/BUILD/EXTEND)
  - KEY NUMBERS field in Quick Reference Card
  - TRIGGER PHRASE + OPENING SENTENCE in Quick Ref Card
  - Interview Deep-Dive in capstone position (after
    Failure Modes, before Related Keywords)
  - Difficulty tags on each interview question
    ([JUNIOR] [MID] [SENIOR] [STAFF])
  - "What separates good from great" line after each
    interview answer
  - *Likely follow-up:* on each Interview Deep-Dive Q
  - Senior-to-Staff Leap in Gradual Depth section
  - At least 1 BEHAVIORAL question for medium/hard keywords
  - Rapid Decision Tree in Comparison Table (if present)
  - Interview question minimums: easy 7, medium 9, hard 12
  - Section order: Quick Ref -> Mastery Checklist ->
    Surprising Truth -> Comparison -> Misconceptions ->
    Failure Modes -> Interview Deep-Dive -> Related

Set version: 3 only after ALL v3 markers are present.""",
        'Merge version detection v3.0+v3.1 -> v3')

    print(f"\nDelta: {len(content) - orig:+d} chars")
    with open(fp, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print("Written.")


def fix_instructions(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    print("\n=== interview-instructions.md ===")
    content = apply(content, '(v3.0)', '(v3)', 'v3.0 -> v3 refs')
    content = apply(content, 'v3.0 spec', 'v3 spec', 'v3.0 spec -> v3 spec')
    content = apply(content, 'v3.0 for full spec', 'v3 for full spec', 'v3.0 for full spec')
    content = apply(content, 'v3.0 to generate', 'v3 to generate', 'v3.0 to generate')
    with open(fp, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print("Written.")


def fix_registry(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    print("\n=== topic-registry.md ===")
    content = apply(content, '(v3.0)', '(v3)', 'v3.0 -> v3 refs')
    content = apply(content, 'v3.0 to generate', 'v3 to generate', 'v3.0 to generate')
    with open(fp, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    print("Written.")


def main():
    base = r'c:\ASK\MyWorkspace\sk-keys\interview\config'
    fix_prompt(f'{base}/INTERVIEW_PROMPT.md')
    fix_instructions(f'{base}/interview-instructions.md')
    fix_registry(f'{base}/topic-registry.md')

    # Final scan for any remaining v3.0 or v3.1 references
    print("\n=== REMAINING REFERENCES CHECK ===")
    import os
    for f in os.listdir(base):
        if not f.endswith('.md'): continue
        c = open(os.path.join(base, f), 'r', encoding='utf-8').read()
        for pattern in ['v3.0', 'v3.1']:
            lines = [(i+1, l.strip()) for i, l in enumerate(c.split('\n')) if pattern in l]
            for ln, txt in lines:
                print(f"  {f} L{ln}: {txt[:90]}")
    print("Done.")


if __name__ == '__main__':
    main()
