#!/usr/bin/env python3
"""
Gap-fill missing base sections in interview content files.

Adds placeholder stubs for any missing v2.0 required sections
in the correct position within each keyword.

Expected section order per keyword:
  1. # KEYWORD NAME
  2. TL;DR
  3. ### The Problem This Solves
  4. ### Textbook Definition
  5. ### Understand It in 30 Seconds
  6. ### First Principles Explanation
  7. ### Mental Model / Analogy
  8. ### Gradual Depth - Five Levels
  9. ### How It Works
 10. ### Complete Picture - End-to-End Flow
 11. ### Code Example
 12. ### Quick Reference Card
 13. ### The Surprising Truth
 14. ### Interview Deep-Dive
 15. ### Comparison Table
 16. ### Common Misconceptions
 17. ### Failure Modes and Diagnosis
 18. ### Related Keywords

Usage: python tmp/gap_fill_interview_v2.py [--dry-run] [--topic TOPIC]
"""

import os
import re
import argparse

INTERVIEW_ROOT = os.path.join("c:\\ASK\\MyWorkspace\\sk-keys", "interview")
SKIP_FOLDERS = {"config"}

# Canonical section order (what we search for / insert)
SECTION_DEFS = [
    {
        "marker": "### The Problem This Solves",
        "template": (
            "### The Problem This Solves\n\n"
            "**WORLD WITHOUT IT:**\n"
            "[TODO: Concrete pain scenario. 2-4 sentences.]\n\n"
            "**THE BREAKING POINT:**\n"
            "[TODO: Specific failure. 1-2 sentences.]\n\n"
            "**THE INVENTION MOMENT:**\n"
            '"This is exactly why {keyword} was created."\n\n'
            "**EVOLUTION:**\n"
            "[TODO: predecessor -> current form -> future.]"
        ),
    },
    {
        "marker": "### Textbook Definition",
        "template": (
            "### Textbook Definition\n\n"
            "[TODO: 2-4 sentences. Formal. Technically precise.]"
        ),
    },
    {
        "marker": "### Understand It in 30 Seconds",
        "template": (
            "### Understand It in 30 Seconds\n\n"
            "**One line:**\n"
            "[TODO: 15 words max. Zero jargon.]\n\n"
            "**One analogy:**\n"
            "> [TODO: 2-3 sentence real-world analogy.]\n\n"
            "**One insight:**\n"
            "[TODO: What separates knowing the name from "
            "understanding it.]"
        ),
    },
    {
        "marker": "### First Principles Explanation",
        "alt_markers": ["### First Principles"],
        "template": (
            "### First Principles Explanation\n\n"
            "**CORE INVARIANTS:**\n"
            "1. [TODO: Always true about this concept]\n"
            "2. [TODO: Always true about this concept]\n"
            "3. [TODO: Always true about this concept]\n\n"
            "**DERIVED DESIGN:**\n"
            "[TODO: How the invariants force the design.]\n\n"
            "**THE TRADE-OFFS:**\n"
            "**Gain:** [TODO]\n"
            "**Cost:** [TODO]\n\n"
            "**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**\n"
            "**Essential:** [TODO]\n"
            "**Accidental:** [TODO]"
        ),
    },
    {
        "marker": "### Mental Model / Analogy",
        "alt_markers": ["### Mental Model"],
        "template": (
            "### Mental Model / Analogy\n\n"
            "> [TODO: Primary analogy in blockquote.]\n\n"
            '- "[TODO: Analogy element]" -> [technical element]\n'
            '- "[TODO: Analogy element]" -> [technical element]\n'
            '- "[TODO: Analogy element]" -> [technical element]\n\n'
            "Where this analogy breaks down: [TODO: 1 sentence.]"
        ),
    },
    {
        "marker": "### Gradual Depth - Five Levels",
        "alt_markers": ["### Gradual Depth"],
        "template": (
            "### Gradual Depth - Five Levels\n\n"
            "**Level 1 - What it is (anyone can understand):**\n"
            "[TODO: Plain English. No jargon. 2-4 sentences.]\n\n"
            "**Level 2 - How to use it (junior developer):**\n"
            "[TODO: Basic usage. Common patterns. 3-5 sentences.]\n\n"
            "**Level 3 - How it works (mid-level engineer):**\n"
            "[TODO: Internals. Data structures. 4-6 sentences.]\n\n"
            "**Level 4 - Production mastery "
            "(senior/staff engineer):**\n"
            "[TODO: Design decisions. Cross-system reasoning. "
            "5-8 sentences.]\n\n"
            "**Level 5 - Distinguished (expert thinking):**\n"
            "[TODO: Cross-domain pattern recognition. "
            "Expert heuristics. 3-5 sentences.]"
        ),
    },
    {
        "marker": "### How It Works",
        "template": None,  # Already present in all files
    },
    {
        "marker": "### Complete Picture - End-to-End Flow",
        "alt_markers": ["### Complete Picture",
                        "### The Complete Picture"],
        "template": (
            "### Complete Picture - End-to-End Flow\n\n"
            "**NORMAL FLOW:**\n"
            "[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]\n"
            "       -> [TODO]\n\n"
            "**FAILURE PATH:**\n"
            "[TODO: cascade -> observable symptom]\n\n"
            "**WHAT CHANGES AT SCALE:**\n"
            "[TODO: 2-3 sentences on behaviour at "
            "10x/100x/1000x load.]"
        ),
    },
    {
        "marker": "### Code Example",
        "template": None,  # Keep existing or skip
    },
    {
        "marker": "### Quick Reference Card",
        "alt_markers": ["### Quick Recall"],
        "template": None,  # Already handled by upgrade script
    },
    {
        "marker": "### The Surprising Truth",
        "template": (
            "### The Surprising Truth\n\n"
            "[TODO: 2-4 sentences. One counterintuitive fact.\n"
            " Specific. Makes this concept permanently memorable.]"
        ),
    },
    {
        "marker": "### Interview Deep-Dive",
        "template": (
            "### Interview Deep-Dive\n\n"
            "**Q1: [TODO: Conceptual question - foundational]**\n\n"
            "*Why they ask:* [TODO]\n\n"
            "**Answer:**\n"
            "[TODO: Complete structured answer. 200-500 words.]\n\n"
            "---\n\n"
            "**Q2: [TODO: Debugging/diagnosis scenario]**\n\n"
            "*Why they ask:* [TODO]\n\n"
            "**Answer:**\n"
            "[TODO: Complete answer with diagnostic steps.]\n\n"
            "---\n\n"
            "**Q3: [TODO: Architecture/design question]**\n\n"
            "*Why they ask:* [TODO]\n\n"
            "**Answer:**\n"
            "[TODO: Complete answer with design rationale.]\n\n"
            "---\n\n"
            "**Q4: [TODO: Trade-off decision question]**\n\n"
            "*Why they ask:* [TODO]\n\n"
            "**Answer:**\n"
            "[TODO: Complete answer with decision framework.]\n\n"
            "---\n\n"
            "**Q5: [TODO: Production scenario question]**\n\n"
            "*Why they ask:* [TODO]\n\n"
            "**Answer:**\n"
            "[TODO: Complete answer with metrics/remediation.]"
        ),
    },
    # v2.0 sections handled by upgrade script already
]


def find_content_files(topic=None):
    """Find all .md content files."""
    results = []
    base = INTERVIEW_ROOT
    if topic:
        base = os.path.join(INTERVIEW_ROOT, topic)
        if not os.path.isdir(base):
            print(f"ERROR: Topic folder not found: {base}")
            return []
    for root, dirs, files in os.walk(base):
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


def find_keyword_boundaries(body):
    """Split body into keyword sections."""
    pattern = r'\n---\s*\n\s*\n---\s*\n'
    parts = re.split(pattern, body)
    return parts


def extract_keyword_name(section):
    """Extract keyword name from H1 header."""
    m = re.search(r'^#\s+(.+)$', section, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "Unknown"


def section_present(section_text, marker, alt_markers=None):
    """Check if a section header exists in the text."""
    if marker in section_text:
        return True
    if alt_markers:
        for alt in alt_markers:
            if alt in section_text:
                return True
    return False


def find_insertion_point(section_text, section_idx):
    """
    Find where to insert a missing section based on what
    sections exist after it in the canonical order.

    Returns (position, section_name_after) or (end, None).
    """
    # Look for the next section that exists after this one
    later_sections = [
        ("### The Problem This Solves", ),
        ("### Textbook Definition", ),
        ("### Understand It in 30 Seconds", ),
        ("### First Principles Explanation",
         "### First Principles"),
        ("### Mental Model / Analogy", "### Mental Model"),
        ("### Gradual Depth - Five Levels",
         "### Gradual Depth - Four Levels",
         "### Gradual Depth"),
        ("### How It Works",),
        ("### Complete Picture - End-to-End Flow",
         "### Complete Picture"),
        ("### Code Example",),
        ("### Quick Reference Card", "### Quick Recall"),
        ("### The Surprising Truth",),
        ("### Interview Deep-Dive",),
        ("### Comparison Table",),
        ("### Common Misconceptions",),
        ("### Failure Modes and Diagnosis",
         "### Failure Modes"),
        ("### Related Keywords",),
    ]

    # Search for the first existing section after our index
    for later_idx in range(section_idx + 1, len(later_sections)):
        for name_variant in later_sections[later_idx]:
            # Find this section header preceded by ---
            # Pattern: \n---\n\n### Section Name
            for pat in [
                f"\n---\n\n{name_variant}",
                f"\n---\n{name_variant}",
            ]:
                pos = section_text.find(pat)
                if pos != -1:
                    return pos + 1, name_variant  # +1 to skip \n

    # If no later section found, insert before first ---
    # that precedes Comparison Table or end
    for marker in ["### Comparison Table",
                    "### Common Misconceptions"]:
        for pat in [f"\n---\n\n{marker}", f"\n---\n{marker}"]:
            pos = section_text.find(pat)
            if pos != -1:
                return pos + 1, marker

    # Append at end
    return len(section_text), None


# Map section index to canonical order position
SECTION_ORDER = {
    "### The Problem This Solves": 0,
    "### Textbook Definition": 1,
    "### Understand It in 30 Seconds": 2,
    "### First Principles Explanation": 3,
    "### Mental Model / Analogy": 4,
    "### Gradual Depth - Five Levels": 5,
    "### How It Works": 6,
    "### Complete Picture - End-to-End Flow": 7,
    "### Code Example": 8,
    "### Quick Reference Card": 9,
    "### The Surprising Truth": 10,
    "### Interview Deep-Dive": 11,
}


def gap_fill_keyword(kw_section):
    """Add missing sections to a single keyword."""
    keyword_name = extract_keyword_name(kw_section)
    changes = 0

    for i, sdef in enumerate(SECTION_DEFS):
        marker = sdef["marker"]
        alt_markers = sdef.get("alt_markers", [])
        template = sdef.get("template")

        if template is None:
            continue  # Skip sections without templates

        if section_present(kw_section, marker, alt_markers):
            continue  # Already exists

        # Need to insert this section
        rendered = template.format(keyword=keyword_name)

        # Find the right position
        pos, after = find_insertion_point(kw_section, i)

        # Build insertion text with --- separator
        insert_text = f"---\n\n{rendered}\n\n"

        kw_section = (kw_section[:pos] + insert_text +
                      kw_section[pos:])
        changes += 1

    return kw_section, changes


def process_file(filepath, dry_run=False):
    """Gap-fill a single file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fm, body = split_frontmatter(content)
    if not fm:
        return 0

    keywords = find_keyword_boundaries(body)
    total_changes = 0
    filled_keywords = []

    for kw_section in keywords:
        kw_name = extract_keyword_name(kw_section)
        kw_section, changes = gap_fill_keyword(kw_section)
        total_changes += changes
        filled_keywords.append(kw_section)

    rel_path = os.path.relpath(filepath, INTERVIEW_ROOT)

    if total_changes == 0:
        print(f"  OK (no gaps): {rel_path}")
        return 0

    separator = "\n\n---\n\n---\n\n"
    new_body = separator.join(filled_keywords)
    new_content = f"---\n{fm}\n---\n\n{new_body}\n"

    if dry_run:
        print(f"  DRY-RUN: {rel_path} "
              f"({len(keywords)} keywords, "
              f"+{total_changes} sections)")
    else:
        with open(filepath, "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(new_content)
        print(f"  FILLED: {rel_path} "
              f"({len(keywords)} keywords, "
              f"+{total_changes} sections)")

    return total_changes


def main():
    parser = argparse.ArgumentParser(
        description="Gap-fill missing interview sections"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--topic", type=str, default=None)
    args = parser.parse_args()

    files = find_content_files(args.topic)
    if not files:
        print("No files found.")
        return

    print(f"Scanning {len(files)} files for missing sections")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    total = 0
    files_changed = 0
    for fp in files:
        changes = process_file(fp, args.dry_run)
        if changes > 0:
            files_changed += 1
            total += changes

    print("=" * 60)
    print(f"Files with gaps filled: {files_changed}")
    print(f"Total sections added: {total}")


if __name__ == "__main__":
    main()
