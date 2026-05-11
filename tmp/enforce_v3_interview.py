#!/usr/bin/env python3
"""Enforce v3.0 template on all interview entry files.

Changes per keyword in each file:
1. Insert ### Mastery Checklist section after Quick Reference Card
2. Move ### Interview Deep-Dive from after Surprising Truth to after Failure Modes
3. Add KEY NUMBERS field to Quick Reference Card (if missing)
4. Update frontmatter version: 2 -> 3

Does NOT touch actual content within sections - only structural reorder.
"""

import os
import re
import sys

BASE = r'c:\ASK\MyWorkspace\sk-keys\interview'
SKIP_FOLDERS = {'config'}

# --- Section identification by emoji prefix ---
SECTION_EMOJIS = {
    '\U0001f525': 'problem',       # 🔥
    '\U0001f4d8': 'textbook',      # 📘
    '\u23f1':     'understand',    # ⏱
    '\U0001f529': 'firstprinciples', # 🔩
    '\U0001f9e0': 'mentalmodel',   # 🧠
    '\U0001f4f6': 'gradual',       # 📶
    '\u2699':     'howitworks',    # ⚙
    '\U0001f504': 'completepicture', # 🔄
    '\U0001f4bb': 'codeexample',   # 💻
    '\U0001f4cc': 'quickref',      # 📌
    '\u2705':     'mastery',       # ✅
    '\U0001f4a1': 'surprising',    # 💡
    '\u2696':     'comparison',    # ⚖
    '\u26a0':     'misconceptions', # ⚠
    '\U0001f6a8': 'failuremodes',  # 🚨
    '\U0001f3af': 'interview',     # 🎯
    '\U0001f517': 'related',       # 🔗
}

# v3.0 section order (only the reorderable tail sections after code example)
V3_ORDER = [
    'quickref',
    'mastery',
    'surprising',
    'comparison',
    'misconceptions',
    'failuremodes',
    'interview',
    'related',
]

MASTERY_TEMPLATE = """---

### \u2705 Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]"""


def identify_section(header_line):
    """Given a ### header line, return the section key."""
    for emoji, key in SECTION_EMOJIS.items():
        if emoji in header_line:
            return key
    return None


def split_keyword_sections(keyword_text):
    """Split a keyword block into sections.

    Returns list of (key, text) where:
    - key is the section identifier (or 'preamble' for title+TL;DR)
    - text is the full section content including its preceding ---
    """
    # Find all ### header positions
    header_positions = []
    for m in re.finditer(r'^### ', keyword_text, re.MULTILINE):
        header_positions.append(m.start())

    if not header_positions:
        return [('preamble', keyword_text)]

    sections = []

    # Preamble: everything before the first section's ---
    first_section_start = header_positions[0]
    # Walk backwards from the ### to find the preceding ---
    dash_pos = keyword_text.rfind('\n---\n', 0, first_section_start)
    if dash_pos >= 0:
        preamble_end = dash_pos
    else:
        preamble_end = first_section_start
    sections.append(('preamble', keyword_text[:preamble_end]))

    # Each section: from its preceding --- to the next section's ---
    for i, hpos in enumerate(header_positions):
        # Find preceding ---
        dash_before = keyword_text.rfind('\n---\n', 0, hpos)
        if dash_before < 0:
            dash_before = keyword_text.rfind('---\n', 0, hpos)
            if dash_before < 0:
                section_start = hpos
            else:
                section_start = dash_before
        else:
            section_start = dash_before + 1  # skip the leading \n

        # Find the end of this section (start of next section's ---)
        if i + 1 < len(header_positions):
            next_hpos = header_positions[i + 1]
            next_dash = keyword_text.rfind('\n---\n', 0, next_hpos)
            if next_dash >= hpos:
                section_end = next_dash
            else:
                section_end = next_hpos
        else:
            section_end = len(keyword_text)

        section_text = keyword_text[section_start:section_end]
        # Get header line
        header_end = keyword_text.find('\n', hpos)
        if header_end < 0:
            header_end = len(keyword_text)
        header_line = keyword_text[hpos:header_end]
        key = identify_section(header_line)
        if key is None:
            key = f'unknown_{i}'
        sections.append((key, section_text))

    return sections


def add_key_numbers(quickref_text):
    """Add KEY NUMBERS field to Quick Ref Card if missing."""
    if 'KEY NUMBERS' in quickref_text:
        return quickref_text  # already present

    # Insert after ONE-LINER line
    # Pattern: **ONE-LINER:** ... \n
    m = re.search(r'(\*\*ONE-LINER:\*\*[^\n]*\n)', quickref_text)
    if m:
        insert_pos = m.end()
        return (quickref_text[:insert_pos] +
                '**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]\n' +
                quickref_text[insert_pos:])
    return quickref_text


def reorder_sections(sections):
    """Reorder sections to v3.0 order and insert Mastery if missing."""
    # Separate preamble + fixed-order sections from reorderable tail
    preamble = []
    fixed_sections = []
    tail_sections = {}

    tail_keys = set(V3_ORDER)
    in_tail = False

    for key, text in sections:
        if key in tail_keys:
            in_tail = True
            tail_sections[key] = text
        elif in_tail:
            # Anything after tail starts that isn't a known tail key
            tail_sections[key] = text
        elif key == 'preamble':
            preamble.append((key, text))
        else:
            fixed_sections.append((key, text))

    # Add KEY NUMBERS to quickref if present
    if 'quickref' in tail_sections:
        tail_sections['quickref'] = add_key_numbers(tail_sections['quickref'])

    # Insert mastery checklist if not present
    if 'mastery' not in tail_sections:
        tail_sections['mastery'] = MASTERY_TEMPLATE

    # Rebuild in v3.0 order
    result = preamble + fixed_sections
    for key in V3_ORDER:
        if key in tail_sections:
            result.append((key, tail_sections[key]))

    # Add any remaining unknown tail sections
    for key, text in tail_sections.items():
        if key not in V3_ORDER:
            result.append((key, text))

    return result


def process_keyword(keyword_text):
    """Process a single keyword block: reorder sections, add mastery."""
    sections = split_keyword_sections(keyword_text)
    reordered = reorder_sections(sections)
    return ''.join(text for _, text in reordered)


def process_file(filepath):
    """Process an entire interview entry file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter
    if not content.startswith('---'):
        return False, "No frontmatter found"

    fm_end = content.find('\n---\n', 4)
    if fm_end < 0:
        return False, "No frontmatter end found"
    fm_end += 5  # include the closing ---\n

    frontmatter = content[:fm_end]
    body = content[fm_end:]

    # Update frontmatter version: 2 -> 3
    frontmatter = re.sub(r'^version:\s*2\s*$', 'version: 3',
                         frontmatter, flags=re.MULTILINE)

    # Split body into keyword blocks
    # Keywords are separated by \n\n\n---\n\n---\n\n or similar patterns
    # The separator is: blank line(s) + --- + blank line(s) + --- + blank line(s)
    keyword_separator = re.compile(r'\n\n+---\n\n---\n\n')
    parts = keyword_separator.split(body)

    if not parts:
        return False, "No content found"

    # The first part may contain the TOC before the first keyword
    # Find where the first # (H1) starts
    first_h1 = re.search(r'^# [^#]', parts[0], re.MULTILINE)
    if first_h1:
        toc = parts[0][:first_h1.start()]
        first_keyword = parts[0][first_h1.start():]
        processed_keywords = [process_keyword(first_keyword)]
    else:
        toc = parts[0]
        processed_keywords = []

    # Process remaining keywords
    for part in parts[1:]:
        processed_keywords.append(process_keyword(part))

    # Reassemble
    keyword_sep = '\n\n\n---\n\n---\n\n'
    new_body = toc + keyword_sep.join(processed_keywords)

    # Ensure file ends with single newline
    new_content = frontmatter + new_body
    new_content = new_content.rstrip('\n') + '\n'

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(new_content)

    return True, f"{len(processed_keywords)} keywords processed"


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
    success = 0
    errors = []

    for filepath in files:
        fname = os.path.basename(filepath)
        try:
            ok, msg = process_file(filepath)
            if ok:
                success += 1
                print(f"  OK: {fname} - {msg}")
            else:
                errors.append((fname, msg))
                print(f"  SKIP: {fname} - {msg}")
        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  ERROR: {fname} - {e}")

    print(f"\nDone: {success}/{len(files)} files processed")
    if errors:
        print(f"Errors ({len(errors)}):")
        for fname, msg in errors:
            print(f"  {fname}: {msg}")
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
