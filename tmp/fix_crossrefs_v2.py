"""
fix_crossrefs_v2.py
Fast cross-reference update:
- Uses ONE simple regex pattern to find all ID-like strings
- Then does dict lookup to see if replacement needed
- O(1) per match, very fast
"""
import re, subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"

# Simple pattern that matches any CODE-NNN style ID
ID_PATTERN = re.compile(r"\b([A-Z]{2,3}-\d{3})\b")

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
        raw_path = line[3:].strip().strip('"')
        fname = Path(raw_path).name
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

def apply_crossrefs_v2(id_map):
    """One-pass replacement per file: find all IDs, replace via dict lookup."""
    all_md = list(BASE.rglob("*.md"))
    print(f"  Scanning {len(all_md)} files...")

    def replacer(m):
        old = m.group(1)
        return id_map.get(old, old)

    id_map_keys = set(id_map.keys())
    changed = 0
    skipped = 0
    for f in all_md:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            skipped += 1
            continue
        # Fast check: find all IDs in the file first (single regex scan)
        ids_in_file = set(ID_PATTERN.findall(text))
        if not ids_in_file.intersection(id_map_keys):
            continue  # no old IDs present - skip
        new_text = ID_PATTERN.sub(replacer, text)
        if new_text != text:
            f.write_text(new_text, encoding="utf-8")
            changed += 1

    print(f"  Updated cross-references in {changed} files ({skipped} read errors)")

if __name__ == "__main__":
    print("Building ID map from git status...")
    id_map = build_id_map_from_git()
    print(f"  Found {len(id_map)} ID renames from uncommitted file renames")

    if id_map:
        apply_crossrefs_v2(id_map)
    else:
        print("  No uncommitted file renames found in git status.")
        print("  Cross-references may already be up to date.")

    print("Done.")
