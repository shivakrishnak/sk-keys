#!/usr/bin/env python3
"""Fix paragraph spacing in interview markdown files.

Adds blank lines between consecutive bold-label lines that
would otherwise merge into a single paragraph on GitHub Pages
(Jekyll / Just the Docs theme).

Fix categories:
  A. Any consecutive **Label:** bold-label lines (covers QRC,
     First Principles sub-labels, etc.)
  B. Senior-to-Staff Leap labels (bold them + blank lines)
  C. Failure Modes labels + BAD/GOOD patterns
  D. **Failure Mode N: Description** prefix lines

Usage:
  python fix_paragraph_spacing.py --dry-run   # preview
  python fix_paragraph_spacing.py              # apply
"""

import re
import sys
from pathlib import Path

# Regex: line starts with **SomeLabel:** (bold label with colon)
BOLD_LABEL_RE = re.compile(r'^\*\*.+?:\*\*')

# Prefix that needs spacing but doesn't match the regex
# (because the colon is inside the bold, not at the boundary)
FAILURE_MODE_PREFIX = '**Failure Mode'

# Senior-to-Staff Leap: plain -> bold replacements
LEAP_REPLACEMENTS = [
    ('A Senior says:', '**A Senior says:**'),
    ('A Staff says:', '**A Staff says:**'),
    ('The difference:', '**The difference:**'),
]

# Additional non-bold prefixes that start new semantic items
CONTENT_PREFIXES = ['BAD:', 'GOOD:']


def find_content_files(root):
    """Find interview content .md files (skip _config/, index.md)."""
    interview_dir = Path(root) / 'interview'
    files = []
    for p in interview_dir.rglob('*.md'):
        rel = p.relative_to(interview_dir)
        if rel.parts[0] == '_config':
            continue
        if p.name == 'index.md':
            continue
        files.append(p)
    return sorted(files)


def needs_blank_before(stripped):
    """Return True if this line needs a blank line before it
    when preceded by a non-blank line."""
    # Bold label: **Something:**
    if BOLD_LABEL_RE.match(stripped):
        return True
    # **Failure Mode N: Description**
    if stripped.startswith(FAILURE_MODE_PREFIX):
        return True
    # BAD: / GOOD: in Failure Modes Fix section
    for prefix in CONTENT_PREFIXES:
        if stripped.startswith(prefix):
            return True
    # Senior-to-Staff bold labels (after bolding)
    for _, bold in LEAP_REPLACEMENTS:
        if stripped.startswith(bold):
            return True
    return False


def fix_file(filepath, dry_run=True):
    """Fix paragraph spacing in a single file.

    Returns (counts_dict, changed_bool).
    """
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    lines = content.split('\n')

    result = []
    counts = {'bold_leap': 0, 'blank_added': 0}
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        # Track fenced code blocks - skip processing inside them
        if stripped.startswith('```'):
            in_code_block = not in_code_block
        if in_code_block:
            result.append(line)
            continue

        # Fix B: Bold Senior-to-Staff labels
        for plain, bold in LEAP_REPLACEMENTS:
            if stripped.startswith(plain) and \
               not stripped.startswith(bold):
                line = line.replace(plain, bold, 1)
                stripped = line.strip()
                counts['bold_leap'] += 1
                break

        # Insert blank line before label lines if preceded
        # by a non-blank line
        if result and stripped and needs_blank_before(stripped):
            prev = result[-1].strip()
            if prev:  # previous line is non-blank
                result.append('')
                counts['blank_added'] += 1

        result.append(line)

    new_content = '\n'.join(result)
    changed = new_content != content

    if changed and not dry_run:
        with open(filepath, 'wb') as f:
            f.write(new_content.encode('utf-8'))

    return counts, changed


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    root = Path(__file__).resolve().parent.parent
    files = find_content_files(root)

    print(f'Found {len(files)} interview content files')
    print(f'Mode: {"DRY RUN" if dry_run else "WRITE"}')
    print()

    total_bold = 0
    total_blanks = 0
    files_changed = 0

    for f in files:
        counts, changed = fix_file(f, dry_run=dry_run)
        if changed:
            files_changed += 1
            rel = f.relative_to(root)
            print(f'  {rel}: +{counts["blank_added"]} blanks, '
                  f'{counts["bold_leap"]} bolded')
            total_bold += counts['bold_leap']
            total_blanks += counts['blank_added']

    print()
    verb = 'would be ' if dry_run else ''
    print(f'Summary: {files_changed}/{len(files)} files '
          f'{verb}changed')
    print(f'  Blank lines added: {total_blanks}')
    print(f'  Labels bolded: {total_bold}')

    if dry_run and files_changed > 0:
        print()
        print('Run without --dry-run to apply changes.')


if __name__ == '__main__':
    main()
