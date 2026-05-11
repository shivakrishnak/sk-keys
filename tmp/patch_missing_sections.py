#!/usr/bin/env python3
"""
Patch pass 2: Add missing 'How It Works' and 'Quick Reference Card'
sections to interview files that lack them.

Usage:
  python tmp/patch_missing_sections.py --dry-run
  python tmp/patch_missing_sections.py
"""

import os
import re
import argparse

INTERVIEW_ROOT = os.path.join("c:\\ASK\\MyWorkspace\\sk-keys", "interview")
SKIP = {"config"}

HOW_IT_WORKS_TEMPLATE = (
    "### How It Works (Mechanism)\n\n"
    "[TODO: Internal mechanics. Data flow. Key steps.\n"
    " 4-8 sentences covering implementation details.]"
)

QUICK_REF_TEMPLATE = (
    "### Quick Reference Card\n\n"
    "```\n"
    "+-------------------------------------------+\n"
    "| WHAT IT IS  | [TODO: 1-line definition]   |\n"
    "| PROBLEM     | [TODO: What pain it solves]  |\n"
    "| KEY INSIGHT | [TODO: Core principle]       |\n"
    "| USE WHEN    | [TODO: Primary use case]     |\n"
    "| AVOID WHEN  | [TODO: When not to use]      |\n"
    "| ANTI-PATTERN| [TODO: Common misuse]        |\n"
    "| TRADE-OFF   | [TODO: What you give up]     |\n"
    "| ONE-LINER   | [TODO: Interview summary]    |\n"
    "+-------------------------------------------+\n"
    "```"
)

# Sections that come AFTER How It Works in canonical order
AFTER_HOW_IT_WORKS = [
    "### Complete Picture",
    "### The Complete Picture",
    "### Code Example",
    "### Quick Reference Card",
    "### Quick Recall",
    "### The Surprising Truth",
]

# Sections that come AFTER Quick Reference Card
AFTER_QUICK_REF = [
    "### The Surprising Truth",
    "### Interview Deep-Dive",
    "### Comparison Table",
]


def has_section(text, markers):
    """Check if any marker variant exists."""
    for m in markers:
        if m in text:
            return True
    return False


def find_insert_pos(text, after_markers):
    """Find position to insert before the first existing later section."""
    for marker in after_markers:
        for pat in [f"\n---\n\n{marker}", f"\n---\n{marker}"]:
            pos = text.find(pat)
            if pos != -1:
                return pos + 1  # skip the \n
    return len(text)


def process_file(filepath, dry_run=False):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into keyword sections
    sep_pattern = r'\n---\s*\n\s*\n---\s*\n'
    parts = re.split(sep_pattern, content)
    changes = 0
    new_parts = []

    for part in parts:
        # Check How It Works
        hw_markers = [
            "### How It Works (Mechanism)",
            "### How It Works",
            "### How Each Works",
        ]
        if not has_section(part, hw_markers):
            pos = find_insert_pos(part, AFTER_HOW_IT_WORKS)
            insert = f"---\n\n{HOW_IT_WORKS_TEMPLATE}\n\n"
            part = part[:pos] + insert + part[pos:]
            changes += 1

        # Check Quick Reference Card
        qr_markers = [
            "### Quick Reference Card",
            "### Quick Recall",
        ]
        if not has_section(part, qr_markers):
            pos = find_insert_pos(part, AFTER_QUICK_REF)
            insert = f"---\n\n{QUICK_REF_TEMPLATE}\n\n"
            part = part[:pos] + insert + part[pos:]
            changes += 1

        new_parts.append(part)

    rel = os.path.relpath(filepath, INTERVIEW_ROOT)

    if changes == 0:
        return 0

    new_content = "\n---\n\n---\n\n".join(new_parts)

    if dry_run:
        print(f"  DRY-RUN: {rel} (+{changes} sections)")
    else:
        with open(filepath, "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(new_content)
        print(f"  PATCHED: {rel} (+{changes} sections)")

    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = []
    for dirpath, dirs, filenames in os.walk(INTERVIEW_ROOT):
        rel = os.path.relpath(dirpath, INTERVIEW_ROOT)
        if rel.split(os.sep)[0] in SKIP:
            continue
        for f in sorted(filenames):
            if f.endswith(".md") and f != "index.md":
                files.append(os.path.join(dirpath, f))

    print(f"Scanning {len(files)} files")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    total = 0
    patched = 0
    for fp in files:
        c = process_file(fp, args.dry_run)
        if c > 0:
            patched += 1
            total += c

    print("=" * 60)
    print(f"Files patched: {patched}")
    print(f"Sections added: {total}")


if __name__ == "__main__":
    main()
