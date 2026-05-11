#!/usr/bin/env python3
"""Fix interview files - comprehensive batch update:
1. Add nav fields to 7 broken index.md files
2. Add nav fields to entry files in 7 broken folders
3. Add emojis to section headers in ALL entry files
4. Add keyword TOC after frontmatter in ALL entry files
"""

import os
import re

BASE = r"c:\ASK\MyWorkspace\sk-keys\interview"

# ============================================================
# EMOJI MAPPING for section headers
# ============================================================
EMOJI_MAP = {
    "### The Problem This Solves":
        "### \U0001f525 The Problem This Solves",
    "### Textbook Definition":
        "### \U0001f4d8 Textbook Definition",
    "### Understand It in 30 Seconds":
        "### \u23f1\ufe0f Understand It in 30 Seconds",
    "### First Principles Explanation":
        "### \U0001f529 First Principles Explanation",
    "### Mental Model / Analogy":
        "### \U0001f9e0 Mental Model / Analogy",
    "### Gradual Depth - Five Levels":
        "### \U0001f4f6 Gradual Depth - Five Levels",
    "### Gradual Depth - Four Levels":
        "### \U0001f4f6 Gradual Depth - Four Levels",
    "### Gradual Depth":
        "### \U0001f4f6 Gradual Depth",
    "### How It Works":
        "### \u2699\ufe0f How It Works",
    "### Complete Picture - End-to-End Flow":
        "### \U0001f504 Complete Picture - End-to-End Flow",
    "### Code Example":
        "### \U0001f4bb Code Example",
    "### Quick Reference Card":
        "### \U0001f4cc Quick Reference Card",
    "### The Surprising Truth":
        "### \U0001f4a1 The Surprising Truth",
    "### Interview Deep-Dive":
        "### \U0001f3af Interview Deep-Dive",
    "### Comparison Table":
        "### \u2696\ufe0f Comparison Table",
    "### Common Misconceptions":
        "### \u26a0\ufe0f Common Misconceptions",
    "### Failure Modes and Diagnosis":
        "### \U0001f6a8 Failure Modes and Diagnosis",
    "### Failure Modes & Diagnosis":
        "### \U0001f6a8 Failure Modes & Diagnosis",
    "### Related Keywords":
        "### \U0001f517 Related Keywords",
}

# ============================================================
# NAV CONFIG for broken folders
# ============================================================
BROKEN_FOLDERS = {
    "containers":   {"title": "Containers",
                     "nav_order": 9,
                     "permalink": "/interview/containers/"},
    "kubernetes":   {"title": "Kubernetes",
                     "nav_order": 10,
                     "permalink": "/interview/kubernetes/"},
    "cicd":         {"title": "CI/CD",
                     "nav_order": 11,
                     "permalink": "/interview/cicd/"},
    "observability":{"title": "Observability",
                     "nav_order": 12,
                     "permalink": "/interview/observability/"},
    "cloud-aws":    {"title": "Cloud AWS",
                     "nav_order": 13,
                     "permalink": "/interview/cloud-aws/"},
    "ai-and-rag":   {"title": "AI Foundations, LLMs, RAG and Agents",
                     "nav_order": 14,
                     "permalink": "/interview/ai-and-rag/"},
    "messaging":    {"title": "Messaging and Event Streaming",
                     "nav_order": 15,
                     "permalink": "/interview/messaging/"},
}

# Entry file order within each broken folder (from index.md)
ENTRY_ORDER = {
    "ai-and-rag": [
        "AI - Foundations.md",
        "AI - LLMs and Prompting.md",
        "AI - RAG.md",
        "AI - Agents and Tools.md",
        "AI - LLMOps and Production.md",
    ],
    "cicd": [
        "CICD - Fundamentals.md",
        "CICD - Tools and GitOps.md",
        "CICD - Deployment Strategies.md",
        "CICD - Security and Quality.md",
    ],
    "cloud-aws": [
        "Cloud AWS - Core Services.md",
        "Cloud AWS - Compute and Networking.md",
        "Cloud AWS - Data and Storage.md",
        "Cloud AWS - Messaging and Integration.md",
        "Cloud AWS - Architecture and Security.md",
    ],
    "containers": [
        "Containers - Fundamentals.md",
        "Containers - Image Optimization.md",
        "Containers - Networking and Storage.md",
        "Containers - Security.md",
        "Containers - Runtime and Ecosystem.md",
    ],
    "kubernetes": [
        "Kubernetes - Core Concepts.md",
        "Kubernetes - Workloads.md",
        "Kubernetes - Networking.md",
        "Kubernetes - Storage and Config.md",
        "Kubernetes - Security.md",
        "Kubernetes - Operations.md",
    ],
    "messaging": [
        "Messaging - Fundamentals.md",
        "Messaging - Kafka.md",
        "Messaging - RabbitMQ and Others.md",
        "Messaging - Patterns and Production.md",
    ],
    "observability": [
        "Observability - Fundamentals.md",
        "Observability - Tools.md",
        "Observability - SRE Practices.md",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def slugify(text):
    """Convert text to URL slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s.strip('-')


def github_anchor(keyword):
    """Convert keyword name to GitHub-style heading anchor."""
    a = keyword.lower()
    a = re.sub(r'[^a-z0-9\s-]', '', a)
    a = re.sub(r'\s+', '-', a)
    return a


def get_frontmatter(content):
    """Return (fm_text, body_text, match_end).
    fm_text = text between opening and closing ---.
    body_text = everything after closing ---.
    """
    m = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if m:
        return m.group(1), content[m.end():], m.end()
    return None, content, 0


def parse_keywords_from_fm(fm_text):
    """Extract keywords list from frontmatter text."""
    keywords = []
    in_kw = False
    for line in fm_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('keywords:'):
            in_kw = True
            continue
        if in_kw:
            if stripped.startswith('- '):
                kw = stripped[2:].strip()
                # Remove surrounding quotes if present
                if kw.startswith('"') and kw.endswith('"'):
                    kw = kw[1:-1]
                if kw.startswith("'") and kw.endswith("'"):
                    kw = kw[1:-1]
                keywords.append(kw)
            elif stripped and not stripped.startswith('-'):
                in_kw = False
    return keywords


def read_file(filepath):
    """Read file with UTF-8, normalize line endings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return content.replace('\r\n', '\n')


def write_file(filepath, content):
    """Write file as UTF-8 without BOM, Unix line endings."""
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


# ============================================================
# STEP 1: Fix broken index.md files
# ============================================================

def fix_broken_index(filepath, folder):
    """Add layout/parent/nav_order/has_children/permalink."""
    cfg = BROKEN_FOLDERS[folder]
    content = read_file(filepath)

    if 'parent: "Interview Mastery"' in content:
        return False  # already fixed

    fm, body, _ = get_frontmatter(content)
    if fm is None:
        print(f"  ERROR: no frontmatter in {filepath}")
        return False

    # Collect non-nav fields from existing frontmatter
    extra_lines = []
    for line in fm.split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('title:'):
            continue  # we rebuild title
        if s.startswith('layout:'):
            continue
        if s.startswith('parent:'):
            continue
        if s.startswith('nav_order:'):
            continue
        if s.startswith('has_children:'):
            continue
        if s.startswith('permalink:'):
            continue
        extra_lines.append(line)

    nav_fields = [
        'layout: default',
        f'title: "{cfg["title"]}"',
        'parent: "Interview Mastery"',
        f'nav_order: {cfg["nav_order"]}',
        'has_children: true',
        f'permalink: {cfg["permalink"]}',
    ]

    new_fm = '\n'.join(nav_fields + extra_lines)
    new_content = '---\n' + new_fm + '\n---\n' + body
    write_file(filepath, new_content)
    return True


# ============================================================
# STEP 2: Fix broken entry files
# ============================================================

def fix_broken_entry(filepath, folder, nav_order):
    """Insert nav fields into existing frontmatter."""
    cfg = BROKEN_FOLDERS[folder]
    content = read_file(filepath)

    fm, body, _ = get_frontmatter(content)
    if fm is None:
        return False

    # Check if already fixed
    if 'grand_parent:' in fm:
        return False

    # Get subtopic for permalink
    sub_m = re.search(r'^subtopic:\s*(.+)$', fm, re.MULTILINE)
    if sub_m:
        subtopic = sub_m.group(1).strip()
    else:
        basename = os.path.splitext(os.path.basename(filepath))[0]
        parts = basename.split(' - ', 1)
        subtopic = parts[1] if len(parts) > 1 else parts[0]

    slug = slugify(subtopic)
    permalink = f"/interview/{folder}/{slug}/"
    parent_title = cfg['title']

    # Insert nav fields: layout at top, rest after title
    fm_lines = fm.split('\n')
    new_fm_lines = ['layout: default']

    for line in fm_lines:
        s = line.strip()
        if s.startswith('layout:'):
            continue  # skip existing layout (if any)
        new_fm_lines.append(line)
        if s.startswith('title:'):
            new_fm_lines.append(f'parent: "{parent_title}"')
            new_fm_lines.append(
                'grand_parent: "Interview Mastery"')
            new_fm_lines.append(f'nav_order: {nav_order}')
            new_fm_lines.append(f'permalink: {permalink}')

    new_content = '---\n' + '\n'.join(new_fm_lines) + '\n---\n'
    new_content += body
    write_file(filepath, new_content)
    return True


# ============================================================
# STEP 3: Add emojis to section headers
# ============================================================

def add_emojis(content):
    """Add emojis to section headers (line-exact match).
    Skips code fences."""
    lines = content.split('\n')
    changed = False
    in_code = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        for plain, emoji_ver in EMOJI_MAP.items():
            if stripped == plain:
                lines[i] = emoji_ver
                changed = True
                break

    return '\n'.join(lines), changed


# ============================================================
# STEP 4: Add keyword TOC after frontmatter
# ============================================================

def build_toc(keywords):
    """Build a keyword table of contents."""
    if not keywords:
        return ""
    lines = [
        "",
        "**Keywords covered in this file:**",
        "",
    ]
    for kw in keywords:
        anchor = github_anchor(kw)
        lines.append(f"- [{kw}](#{anchor})")
    lines.append("")
    return '\n'.join(lines)


def add_toc(content, keywords):
    """Insert keyword TOC after frontmatter closing ---.
    Returns (content, changed)."""
    if '**Keywords covered in this file:**' in content:
        return content, False

    toc = build_toc(keywords)
    if not toc:
        return content, False

    m = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
    if not m:
        return content, False

    pos = m.end()
    new_content = content[:pos] + toc + content[pos:]
    return new_content, True


# ============================================================
# COMBINED: process one entry file (emojis + TOC)
# ============================================================

def process_entry(filepath):
    """Add emojis and keyword TOC to a single entry file."""
    content = read_file(filepath)
    changes = []

    # Parse keywords from frontmatter
    fm, _, _ = get_frontmatter(content)
    keywords = parse_keywords_from_fm(fm) if fm else []

    # Add keyword TOC
    content, toc_added = add_toc(content, keywords)
    if toc_added:
        changes.append("TOC")

    # Add emojis to section headers
    content, emoji_added = add_emojis(content)
    if emoji_added:
        changes.append("emojis")

    if changes:
        write_file(filepath, content)
        return changes
    return []


# ============================================================
# MAIN
# ============================================================

def main():
    total = 0

    # --- STEP 1: Fix broken index.md files ---
    print("=" * 60)
    print("STEP 1: Fix broken index.md files")
    print("=" * 60)
    for folder in sorted(BROKEN_FOLDERS):
        path = os.path.join(BASE, folder, "index.md")
        if os.path.exists(path):
            if fix_broken_index(path, folder):
                print(f"  FIXED: {folder}/index.md")
                total += 1
            else:
                print(f"  SKIP:  {folder}/index.md "
                      "(already has nav)")

    # --- STEP 2: Fix broken entry files ---
    print()
    print("=" * 60)
    print("STEP 2: Fix broken entry file nav fields")
    print("=" * 60)
    for folder in sorted(ENTRY_ORDER):
        files = ENTRY_ORDER[folder]
        print(f"\n  [{folder}]")
        for i, fname in enumerate(files, 1):
            path = os.path.join(BASE, folder, fname)
            if os.path.exists(path):
                if fix_broken_entry(path, folder, i):
                    print(f"    FIXED: {fname} "
                          f"(nav_order={i})")
                    total += 1
                else:
                    print(f"    SKIP:  {fname}")
            else:
                print(f"    NOT FOUND: {fname}")

    # --- STEP 3+4: Emojis + TOC for ALL entry files ---
    print()
    print("=" * 60)
    print("STEP 3: Add emojis + keyword TOC to ALL entries")
    print("=" * 60)
    for folder in sorted(os.listdir(BASE)):
        folder_path = os.path.join(BASE, folder)
        if not os.path.isdir(folder_path):
            continue
        if folder == 'config':
            continue

        print(f"\n  [{folder}]")
        for fname in sorted(os.listdir(folder_path)):
            if fname == 'index.md' or not fname.endswith('.md'):
                continue
            fpath = os.path.join(folder_path, fname)
            changes = process_entry(fpath)
            if changes:
                print(f"    {fname}: {', '.join(changes)}")
                total += 1

    print()
    print("=" * 60)
    print(f"TOTAL FILES MODIFIED: {total}")
    print("=" * 60)


if __name__ == '__main__':
    main()
