"""
fix_crossrefs_fast.py
Fast cross-reference update using a single combined regex.
Builds old→new ID map from git status (uncommitted renames appear as D + ??)
then applies one-pass replacement per file.
"""
import re, subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"

def build_id_map_from_git():
    """Build old→new map by matching deleted (D) and untracked (??) files by title."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "-u"],
        capture_output=True, text=True,
        cwd=str(BASE.parent)
    )
    deleted = {}   # title_lower → old_id
    added   = {}   # title_lower → new_id

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2].strip()
        path = line[3:].strip().strip('"')
        fname = Path(path).name
        # Match CODE-NNN - Title.md
        m = re.match(r"^([A-Z]+-\d+)\s+-\s+(.+)\.md$", fname)
        if not m:
            continue
        fid   = m.group(1)
        title = m.group(2).lower()

        if status == "D":
            deleted[title] = fid
        elif status in ("??", "A"):
            added[title] = fid

    id_map = {}  # old_id → new_id
    for title, old_id in deleted.items():
        if title in added:
            new_id = added[title]
            if old_id != new_id:
                id_map[old_id] = new_id

    return id_map

def apply_crossrefs_fast(id_map):
    """One-pass replacement per file using a single combined regex."""
    if not id_map:
        print("  No ID renames in map - nothing to do")
        return

    # Build a combined pattern: match any old ID as a word
    # Pattern: \b(CODE-001|CODE-002|...)\b  — but IDs don't use word boundaries well
    # Use alternation with lookbehind/lookahead
    sorted_ids = sorted(id_map.keys(), key=len, reverse=True)  # longest first
    pattern = re.compile(
        r"(?<![A-Z0-9-])(" + "|".join(re.escape(oid) for oid in sorted_ids) + r")(?![A-Z0-9-])"
    )

    all_md = list(BASE.rglob("*.md"))
    print(f"  Scanning {len(all_md)} files with combined pattern "
          f"({len(id_map)} IDs to replace)...")

    changed = 0
    for f in all_md:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if not pattern.search(text):
            continue  # fast path: no match
        new_text = pattern.sub(lambda m: id_map[m.group(1)], text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"  Updated cross-references in {changed} files")

if __name__ == "__main__":
    print("Building ID map from git status...")
    id_map = build_id_map_from_git()
    print(f"  Found {len(id_map)} ID renames from uncommitted file renames")

    if id_map:
        apply_crossrefs_fast(id_map)
    else:
        # Fallback: scan all files for any non-empty cross-ref fields
        print("  No uncommitted renames found.")
        print("  Checking for non-empty cross-reference fields...")
        refs_found = 0
        for f in BASE.rglob("*.md"):
            if f.name == "index.md":
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue
            for field in ["depends_on", "used_by", "related"]:
                m = re.search(rf"^{field}:\s*(\S+)", text, re.MULTILINE)
                if m and m.group(1) not in ("", "null", "~"):
                    refs_found += 1
                    break
        print(f"  Files with non-empty cross-ref fields: {refs_found}")

    print("Done.")
