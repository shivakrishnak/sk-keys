#!/usr/bin/env python3
"""
Upgrade all interview content files from v1.0 to v2.0 structure.

Phase 1: Mechanical upgrades
- Rename "Gradual Depth - Four Levels" -> "Gradual Depth - Five Levels"
- Add Level 5 placeholder after Level 4 content
- Rename "Quick Recall" -> "Quick Reference Card" and add 8-field structure
- Add new sections after Interview Deep-Dive:
  - Comparison Table (conditional placeholder)
  - Common Misconceptions (placeholder table)
  - Failure Modes and Diagnosis (placeholder structure)
  - Related Keywords (placeholder structure)
- Update frontmatter: version 1->2, status->in-progress

Usage: python tmp/upgrade_interview_v2.py [--dry-run] [--topic TOPIC]
"""

import os
import re
import sys
import glob
import argparse

INTERVIEW_ROOT = os.path.join("c:\\ASK\\MyWorkspace\\sk-keys", "interview")
SKIP_FOLDERS = {"config"}


def find_content_files(topic=None):
    """Find all .md content files (skip index.md and config/)."""
    results = []
    base = INTERVIEW_ROOT
    if topic:
        base = os.path.join(INTERVIEW_ROOT, topic)
        if not os.path.isdir(base):
            print(f"ERROR: Topic folder not found: {base}")
            return []

    for root, dirs, files in os.walk(base):
        # Skip config folder
        rel = os.path.relpath(root, INTERVIEW_ROOT)
        if rel.split(os.sep)[0] in SKIP_FOLDERS:
            continue
        for f in sorted(files):
            if f.endswith(".md") and f != "index.md":
                results.append(os.path.join(root, f))
    return results


def split_frontmatter(content):
    """Split content into frontmatter and body."""
    if not content.startswith("---"):
        return "", content
    end = content.index("---", 3)
    fm = content[3:end].strip()
    body = content[end + 3:].lstrip("\n")
    return fm, body


def upgrade_frontmatter(fm):
    """Update version and status in frontmatter."""
    changed = False
    # version: 1 -> version: 2
    if re.search(r'^version:\s*1\s*$', fm, re.MULTILINE):
        fm = re.sub(r'^version:\s*1\s*$', 'version: 2', fm,
                     flags=re.MULTILINE)
        changed = True
    # status: complete -> status: in-progress (until content filled)
    if re.search(r'^status:\s*complete\s*$', fm, re.MULTILINE):
        fm = re.sub(r'^status:\s*complete\s*$', 'status: in-progress',
                     fm, flags=re.MULTILINE)
        changed = True
    return fm, changed


def find_keyword_boundaries(body):
    """
    Split body into keyword sections.
    Keywords are separated by double horizontal rules:

    ---

    ---

    # Next Keyword
    """
    # Pattern: line "---" followed by blank, another "---", blank,
    # then "# " (H1 keyword title)
    # We split on the double-rule separator
    pattern = r'\n---\s*\n\s*\n---\s*\n'
    parts = re.split(pattern, body)
    return parts


def upgrade_gradual_depth(section):
    """
    Rename 'Four Levels' -> 'Five Levels' and add Level 5 placeholder.
    """
    if "### Gradual Depth - Four Levels" not in section:
        return section, False

    # Rename the header
    section = section.replace(
        "### Gradual Depth - Four Levels",
        "### Gradual Depth - Five Levels"
    )

    # Check if Level 5 already exists
    if "**Level 5" in section:
        return section, True

    # Find the end of Level 4 content - it ends at the next "---"
    # Find Level 4 start
    l4_match = re.search(
        r'(\*\*Level 4[^*]*\*\*[:\s]*\n)',
        section
    )
    if not l4_match:
        return section, True

    # Find the --- that follows Level 4 content
    l4_start = l4_match.start()
    # Look for next "---" after Level 4
    next_hr = section.find("\n---\n", l4_start)
    if next_hr == -1:
        next_hr = section.find("\n---", l4_start)
    if next_hr == -1:
        return section, True

    # Insert Level 5 placeholder before the ---
    level5_text = (
        "\n\n**Level 5 - Distinguished (expert thinking):**\n"
        "[TODO: Cross-domain pattern recognition. Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]\n"
    )
    section = section[:next_hr] + level5_text + section[next_hr:]
    return section, True


def upgrade_quick_recall(section):
    """
    Rename 'Quick Recall' -> 'Quick Reference Card' and add 8-field
    structure before '**If you remember only 3 things:**'
    """
    if "### Quick Recall" not in section:
        return section, False

    section = section.replace(
        "### Quick Recall",
        "### Quick Reference Card"
    )

    # Check if 8-field structure already exists
    if "**WHAT IT IS:**" in section:
        return section, True

    # Find "**If you remember only 3 things:**" and insert before it
    marker = "**If you remember only 3 things:**"
    idx = section.find(marker)
    if idx == -1:
        return section, True

    card_fields = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]\n\n"
    )
    section = section[:idx] + card_fields + section[idx:]
    return section, True


def extract_keyword_name(section):
    """Extract keyword name from H1 header."""
    m = re.search(r'^#\s+(.+)$', section, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "Unknown"


def add_new_sections(section):
    """
    Add new v2.0 sections after Interview Deep-Dive:
    - Comparison Table (conditional)
    - Common Misconceptions
    - Failure Modes and Diagnosis
    - Related Keywords
    """
    keyword_name = extract_keyword_name(section)

    # Check if new sections already exist
    if "### Common Misconceptions" in section:
        return section, False

    new_sections = (
        "\n\n---\n\n"
        "### Comparison Table\n\n"
        "[TODO: Include if 2+ named alternatives exist for "
        f"{keyword_name}. "
        "Otherwise remove this section.]\n\n"
        "---\n\n"
        "### Common Misconceptions\n\n"
        "| # | Misconception | Reality |\n"
        "|---|---------------|---------|"
        f"\n| 1 | [TODO] | [TODO] |"
        f"\n| 2 | [TODO] | [TODO] |"
        f"\n| 3 | [TODO] | [TODO] |"
        f"\n| 4 | [TODO] | [TODO] |\n\n"
        "---\n\n"
        "### Failure Modes and Diagnosis\n\n"
        f"**Failure Mode 1: [TODO]**\n"
        f"**Symptom:** [TODO]\n"
        f"**Root Cause:** [TODO]\n"
        f"**Diagnostic:**\n"
        f"```\n"
        f"[TODO: real diagnostic command]\n"
        f"```\n"
        f"**Fix:** [TODO: BAD then GOOD]\n"
        f"**Prevention:** [TODO]\n\n"
        f"**Failure Mode 2: [TODO]**\n"
        f"**Symptom:** [TODO]\n"
        f"**Root Cause:** [TODO]\n"
        f"**Diagnostic:**\n"
        f"```\n"
        f"[TODO: real diagnostic command]\n"
        f"```\n"
        f"**Fix:** [TODO: BAD then GOOD]\n"
        f"**Prevention:** [TODO]\n\n"
        f"**Failure Mode 3: [TODO]**\n"
        f"**Symptom:** [TODO]\n"
        f"**Root Cause:** [TODO]\n"
        f"**Diagnostic:**\n"
        f"```\n"
        f"[TODO: real diagnostic command]\n"
        f"```\n"
        f"**Fix:** [TODO: BAD then GOOD]\n"
        f"**Prevention:** [TODO]\n\n"
        "---\n\n"
        "### Related Keywords\n\n"
        "**Prerequisites (understand these first):**\n"
        "- [TODO] - [why needed]\n"
        "- [TODO] - [why needed]\n\n"
        "**Builds on this (learn these next):**\n"
        "- [TODO] - [what it adds]\n"
        "- [TODO] - [what it adds]\n\n"
        "**Alternatives / Comparisons:**\n"
        "- [TODO] - [when to prefer it]\n"
        "- [TODO] - [when to prefer it]"
    )

    # Append new sections at the end of the keyword section
    # The section text ends with trailing whitespace
    section = section.rstrip() + new_sections

    return section, True


def upgrade_file(filepath, dry_run=False):
    """Upgrade a single file to v2.0 structure."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fm, body = split_frontmatter(content)
    if not fm:
        print(f"  SKIP (no frontmatter): {filepath}")
        return 0

    # Check if already v2
    if re.search(r'^version:\s*2\s*$', fm, re.MULTILINE):
        print(f"  SKIP (already v2): {filepath}")
        return 0

    # Upgrade frontmatter
    fm, fm_changed = upgrade_frontmatter(fm)

    # Split into keyword sections
    keywords = find_keyword_boundaries(body)

    total_keywords = len(keywords)
    upgraded_keywords = []
    changes = 0

    for i, kw_section in enumerate(keywords):
        kw_name = extract_keyword_name(kw_section)

        # 1. Upgrade Gradual Depth
        kw_section, gd_changed = upgrade_gradual_depth(kw_section)
        if gd_changed:
            changes += 1

        # 2. Upgrade Quick Recall -> Quick Reference Card
        kw_section, qr_changed = upgrade_quick_recall(kw_section)
        if qr_changed:
            changes += 1

        # 3. Add new sections
        kw_section, ns_changed = add_new_sections(kw_section)
        if ns_changed:
            changes += 1

        upgraded_keywords.append(kw_section)

    # Reassemble
    separator = "\n\n---\n\n---\n\n"
    new_body = separator.join(upgraded_keywords)
    new_content = f"---\n{fm}\n---\n\n{new_body}\n"

    rel_path = os.path.relpath(filepath, INTERVIEW_ROOT)

    if dry_run:
        print(f"  DRY-RUN: {rel_path} "
              f"({total_keywords} keywords, {changes} changes)")
    else:
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print(f"  UPGRADED: {rel_path} "
              f"({total_keywords} keywords, {changes} changes)")

    return changes


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade interview files to v2.0"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing")
    parser.add_argument("--topic", type=str, default=None,
                        help="Process only this topic folder")
    args = parser.parse_args()

    files = find_content_files(args.topic)

    if not files:
        print("No files found to upgrade.")
        return

    print(f"Found {len(files)} content files to upgrade")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    total_changes = 0
    upgraded_count = 0
    skipped_count = 0

    for fp in files:
        changes = upgrade_file(fp, args.dry_run)
        if changes > 0:
            upgraded_count += 1
            total_changes += changes
        else:
            skipped_count += 1

    print("=" * 60)
    print(f"Total: {len(files)} files")
    print(f"Upgraded: {upgraded_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Total changes: {total_changes}")


if __name__ == "__main__":
    main()
