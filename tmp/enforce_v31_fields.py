#!/usr/bin/env python3
"""Enforce v3.1 field additions on all 85 interview entry files.

Adds to each keyword:
1. TRIGGER PHRASE + OPENING SENTENCE fields in Quick Reference Card
2. Senior-to-Staff Leap placeholder in Gradual Depth

Does NOT change version (stays at 3) or reorder sections.
"""

import os
import re
import sys

BASE = r'c:\ASK\MyWorkspace\sk-keys\interview'
SKIP_FOLDERS = {'config'}


def add_quick_ref_fields(content):
    """Add TRIGGER PHRASE and OPENING SENTENCE after KEY NUMBERS if missing."""
    if 'TRIGGER PHRASE' in content:
        return content, 0

    count = 0

    # Pattern 1: Bold field format - **KEY NUMBERS:**
    def replace_bold_kn(m):
        nonlocal count
        count += 1
        return (m.group(0) +
                '\n**TRIGGER PHRASE:** [TODO: 5-7 words activating full mental model]'
                '\n**OPENING SENTENCE:** [TODO: First sentence showing immediate depth]')

    new_content = re.sub(
        r'\*\*KEY NUMBERS:\*\*[^\n]*',
        replace_bold_kn,
        content
    )

    if count > 0:
        return new_content, count

    # Pattern 2: ASCII box format - | KEY NUMBERS |
    def replace_box_kn(m):
        nonlocal count
        count += 1
        return (m.group(0) +
                '\n| TRIGGER   | [TODO: 5-7 word mental model]  |'
                '\n| OPENING   | [TODO: First sentence depth]   |')

    new_content = re.sub(
        r'\| KEY NUMBERS[^\n]*',
        replace_box_kn,
        content
    )

    return new_content, count


def add_senior_staff_leap(content):
    """Add Senior-to-Staff Leap placeholder between L4 and L5 if missing."""
    if 'Senior-to-Staff Leap' in content:
        return content, 0

    count = 0

    leap_text = ('\n\n**The Senior-to-Staff Leap:**\n'
                 'A Senior says: "[TODO: What a competent senior would say]"\n'
                 'A Staff says: "[TODO: What demonstrates next-level abstraction]"\n'
                 'The difference: [TODO: 1 sentence - the mental model shift]')

    # Find all Level 5 headers and insert leap before each
    # Pattern: content ending L4 section, then **Level 5
    def replace_l5(m):
        nonlocal count
        count += 1
        return leap_text + '\n\n' + m.group(0)

    new_content = re.sub(
        r'\*\*Level 5 - Distinguished',
        replace_l5,
        content
    )

    return new_content, count


def process_file(filepath):
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    content, qr_count = add_quick_ref_fields(content)
    content, leap_count = add_senior_staff_leap(content)

    if content == original:
        return False, "no changes needed"

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    return True, f"{qr_count} QR fields, {leap_count} leaps"


def main():
    files = []
    for folder in sorted(os.listdir(BASE)):
        fp = os.path.join(BASE, folder)
        if not os.path.isdir(fp) or folder in SKIP_FOLDERS:
            continue
        for f in sorted(os.listdir(fp)):
            if f.endswith('.md') and f != 'index.md':
                files.append(os.path.join(fp, f))

    print(f"Processing {len(files)} files...")
    changed = 0
    skipped = 0
    errors = []

    for filepath in files:
        fname = os.path.basename(filepath)
        try:
            ok, msg = process_file(filepath)
            if ok:
                changed += 1
                print(f"  OK: {fname} - {msg}")
            else:
                skipped += 1
        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  ERROR: {fname} - {e}")

    print(f"\nDone: {changed} changed, {skipped} skipped, {len(errors)} errors")
    if errors:
        for fname, msg in errors:
            print(f"  {fname}: {msg}")
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
