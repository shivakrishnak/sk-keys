"""Fix missing Jekyll frontmatter in interview files.

Adds layout, parent, grand_parent, nav_order, has_children,
and permalink fields to interview index and content files
that are missing them.
"""
import re
from pathlib import Path

ROOT = Path(r"C:\ASK\Workspace\northstar\interview")

# ── Topic index files that need fixing ──────────────────────
# Map: folder_name -> (title, nav_order, permalink_slug)
INDEX_FIXES = {
    "java":             ("Java",             1, "java"),
    "java-concurrency": ("Java Concurrency", 2, "java-concurrency"),
    "react":            ("React",           16, "react"),
}

# ── Content files nav_order within each topic ───────────────
# Map: folder_name -> { parent_title, ordered list of subtopic slugs }
CONTENT_ORDER = {
    "java": {
        "parent": "Java",
        "files": [
            ("Java - Basics.md",                    "basics",                1),
            ("Java - Collections.md",               "collections",           2),
            ("Java - Exceptions and IO.md",         "exceptions-and-io",     3),
            ("Java - Java 8 Features.md",           "java-8-features",       4),
            ("Java - Java 11 to 17.md",             "java-11-to-17",         5),
            ("Java - Java 21 and Beyond.md",        "java-21-and-beyond",    6),
            ("Java - JVM Internals.md",             "jvm-internals",         7),
            ("Java - Garbage Collection.md",        "garbage-collection",    8),
            ("Java - Diagnostics and Security.md",  "diagnostics-and-security", 9),
        ],
    },
    "java-concurrency": {
        "parent": "Java Concurrency",
        "files": [
            ("Java Concurrency - Thread Basics.md",          "thread-basics",          1),
            ("Java Concurrency - Synchronization.md",        "synchronization",        2),
            ("Java Concurrency - Concurrent Collections.md", "concurrent-collections", 3),
            ("Java Concurrency - Virtual Threads.md",        "virtual-threads",        4),
            ("Java Concurrency - Diagnostics.md",            "diagnostics",            5),
        ],
    },
    "hibernate": {
        "parent": "Hibernate",
        "files": [
            ("Hibernate - Basics.md",        "basics",        1),
            ("Hibernate - Relationships.md", "relationships", 2),
            ("Hibernate - Performance.md",   "performance",   3),
            ("Hibernate - Advanced.md",      "advanced",      4),
        ],
    },
    "react": {
        "parent": "React",
        "files": [
            ("React - Fundamentals.md",              "fundamentals",              1),
            ("React - Hooks.md",                     "hooks",                     2),
            ("React - Component Patterns.md",        "component-patterns",        3),
            ("React - State Management.md",          "state-management",          4),
            ("React - Routing and Styling.md",       "routing-and-styling",       5),
            ("React - Performance.md",               "performance",               6),
            ("React - Testing.md",                   "testing",                   7),
            ("React - Internals and Advanced.md",    "internals-and-advanced",    8),
            ("React - Server-Side and Next.js.md",   "server-side-and-nextjs",    9),
            ("React - Tooling.md",                   "tooling",                  10),
            ("React - Architecture and Production.md", "architecture-and-production", 11),
        ],
    },
}


def fix_index_file(folder: str, title: str, nav_order: int, slug: str):
    """Add Jekyll nav fields to a topic index.md."""
    path = ROOT / folder / "index.md"
    if not path.exists():
        print(f"  SKIP (not found): {path}")
        return

    text = path.read_text(encoding="utf-8")

    # Check if already has the fields
    if "has_children" in text:
        print(f"  SKIP (already fixed): {path.name}")
        return

    # Parse existing frontmatter
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        print(f"  ERROR (no frontmatter): {path}")
        return

    old_fm = m.group(0)
    body = text[len(old_fm):]

    # Build new frontmatter preserving existing fields
    fm_content = m.group(1)

    # Remove title line (we'll rewrite it)
    lines = fm_content.strip().split("\n")
    kept = []
    for line in lines:
        key = line.split(":")[0].strip() if ":" in line else ""
        if key in ("title", "layout", "parent", "nav_order",
                    "has_children", "permalink"):
            continue
        kept.append(line)

    new_fm_lines = [
        "---",
        "layout: default",
        f'title: "{title}"',
        'parent: "Interview Mastery"',
        f"nav_order: {nav_order}",
        "has_children: true",
        f"permalink: /interview/{slug}/",
    ]
    new_fm_lines.extend(kept)
    new_fm_lines.append("---")

    new_text = "\n".join(new_fm_lines) + body
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"  FIXED index: {folder}/index.md")


def fix_content_file(folder: str, filename: str, parent: str,
                     slug: str, nav_order: int):
    """Add Jekyll nav fields to a content .md file."""
    path = ROOT / folder / filename
    if not path.exists():
        print(f"  SKIP (not found): {path}")
        return

    text = path.read_text(encoding="utf-8")

    if "grand_parent" in text:
        print(f"  SKIP (already fixed): {filename}")
        return

    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        print(f"  ERROR (no frontmatter): {path}")
        return

    old_fm = m.group(0)
    body = text[len(old_fm):]

    fm_content = m.group(1)
    lines = fm_content.strip().split("\n")

    # Separate scalar fields from multi-line fields (keywords list)
    kept = []
    skip_keys = {"title", "layout", "parent", "grand_parent",
                 "nav_order", "permalink"}
    i = 0
    while i < len(lines):
        line = lines[i]
        key = line.split(":")[0].strip() if ":" in line else ""
        if key in skip_keys:
            i += 1
            continue
        kept.append(line)
        # If this is a list field (keywords:), consume indented lines
        if line.strip().endswith(":") or (": " not in line and line.strip().startswith("keywords")):
            pass  # list items handled naturally
        i += 1

    # Compute permalink folder from the topic folder name
    folder_slug = folder  # java, java-concurrency, hibernate, react

    new_fm_lines = [
        "---",
        "layout: default",
        f'title: "{filename.replace(".md", "")}"',
        f'parent: "{parent}"',
        'grand_parent: "Interview Mastery"',
        f"nav_order: {nav_order}",
        f"permalink: /interview/{folder_slug}/{slug}/",
    ]
    new_fm_lines.extend(kept)
    new_fm_lines.append("---")

    new_text = "\n".join(new_fm_lines) + body
    path.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"  FIXED content: {folder}/{filename}")


def main():
    print("=== Fixing Interview Index Files ===")
    for folder, (title, nav_order, slug) in INDEX_FIXES.items():
        fix_index_file(folder, title, nav_order, slug)

    print("\n=== Fixing Interview Content Files ===")
    for folder, info in CONTENT_ORDER.items():
        parent = info["parent"]
        for filename, slug, nav_order in info["files"]:
            fix_content_file(folder, filename, parent, slug, nav_order)

    print("\nDone!")


if __name__ == "__main__":
    main()
