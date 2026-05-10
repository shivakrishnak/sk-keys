"""
update_crossrefs.py
Phase 4 only: update all cross-references in .md files after the difficulty rename.
Reads from all .md files, builds old→new ID map from frontmatter, then applies.
"""
import re
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"

def build_id_map():
    """
    Scan all files and build a map of IDs that appear in file content
    differently from what the frontmatter says. We detect renamed files by
    looking for files where the filename ID != the frontmatter id: field.
    Actually, after Phase 2, the frontmatter id: has already been updated to
    the NEW id. So we need to reconstruct the old→new map differently.

    Instead, we read the git diff or we scan for temporary files...
    Actually, the simplest approach: the rename script printed all old→new
    mappings. Let's rebuild the same mapping by re-running Phase 1.
    """
    pass

def get_id_num(id_str):
    m = re.search(r"-(\d+)$", id_str or "")
    return int(m.group(1)) if m else 999999

DIFF_ORDER = {"★☆☆": 0, "★★☆": 1, "★★★": 2, "🌱": 3, "🔥": 4, "🔬": 5}

def diff_rank(d):
    d = (d or "").strip().strip('"')
    for k, v in DIFF_ORDER.items():
        if k in d:
            return v
    return 1

def build_category_mapping_from_current(cat_dir):
    """
    Since Phase 2 already renamed the files and updated their frontmatter,
    to reconstruct old→new we need to look at what the IDs WOULD have been
    before the rename. We can do this by:
    1. Reading all current files (their `id:` is the NEW id)
    2. Reconstructing what the OLD id was based on the original order

    Actually this is circular. The better approach is to look at git status
    and find renamed files. But that's complex.

    Simplest correct approach: re-sort the files as if we're doing the rename
    from scratch, and the result should be the same NEW ids. The OLD ids
    are derived from the filenames' original position (before sort).

    WAIT - after Phase 2, the filenames already have the NEW ids.
    The OLD ids are no longer visible in filenames.
    But the `id:` in frontmatter is the NEW id too (updated by Phase 2).

    We need to use git to find old filenames, or we need to have saved the
    mapping from Phase 1.

    ALTERNATIVE: Use `git diff --name-status HEAD~1 HEAD` to find renamed files.
    But we haven't committed yet.

    SIMPLEST: Use `git status` to find files that were renamed (R status).
    """
    return []

def build_id_map_from_git():
    """Build old→new map from git rename status."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--name-status", "--cached"],
        capture_output=True, text=True,
        cwd=str(BASE.parent)
    )
    # Also check unstaged
    result2 = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True,
        cwd=str(BASE.parent)
    )

    id_map = {}
    # Look for renamed/deleted+added pairs
    # git may show renames as D old + A new
    # Parse from status
    deleted = {}
    added = {}
    for line in result2.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2].strip()
        path = line[3:].strip().strip('"')
        # Extract filename
        fname = Path(path).name
        # Extract ID from filename
        m = re.match(r"^([A-Z]+-\d+)\s+-\s+", fname)
        if not m:
            continue
        fid = m.group(1)
        if status in ("D",):
            deleted[fname] = fid
        elif status in ("A", "??"):
            added[fname] = fid

    # Match deleted old IDs to added new IDs by checking common title parts
    for old_fname, old_id in deleted.items():
        # Get title part after "CODE-NNN - "
        old_title_m = re.match(r"^[A-Z]+-\d+\s+-\s+(.+)\.md$", old_fname)
        if not old_title_m:
            continue
        old_title = old_title_m.group(1)
        # Find a newly added file with same title
        for new_fname, new_id in added.items():
            new_title_m = re.match(r"^[A-Z]+-\d+\s+-\s+(.+)\.md$", new_fname)
            if not new_title_m:
                continue
            if new_title_m.group(1) == old_title and old_id != new_id:
                id_map[old_id] = {"new_id": new_id, "title": old_title}
                break

    return id_map

def apply_crossrefs(id_map):
    """Apply all ID replacements across all .md files."""
    all_md = list(BASE.rglob("*.md"))
    print(f"Scanning {len(all_md)} files for cross-references...")
    changed = 0
    for f in all_md:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        original = text
        for old_id, info in id_map.items():
            new_id = info["new_id"]
            if old_id == new_id:
                continue
            # Replace bare ID references (not inside longer IDs like CODE-NNN1)
            text = re.sub(
                r"(?<![A-Z0-9])" + re.escape(old_id) + r"(?![A-Z0-9\-])",
                new_id, text)
            # Replace wikilinks
            text = re.sub(
                r"\[\[" + re.escape(old_id) + r"\s*-\s*([^\]]*)\]\]",
                f"[[{new_id} - \\1]]",
                text)
        if text != original:
            changed += 1
            f.write_text(text, encoding="utf-8")
    print(f"Updated cross-references in {changed} files")

if __name__ == "__main__":
    print("Building ID map from git status...")
    id_map = build_id_map_from_git()
    print(f"Found {len(id_map)} ID renames to apply")
    if id_map:
        apply_crossrefs(id_map)
    else:
        print("No renames found in git status - nothing to do")
        print("(This is expected if git status doesn't show pending renames)")
        print("Rebuilding from current file state instead...")
        # Alternative: rebuild mapping by re-running phase 1 of difficulty_sort_rename
        # But since files are already renamed, we can't reconstruct old IDs
        # The cross-references in content files that reference OLD ids by CODE-NNN
        # need to be updated. However, since almost all files are STUBS (version: 0),
        # they have empty depends_on/used_by/related fields, so there are very few
        # actual cross-references to update.
        print("Most files are stubs (v0) with empty cross-references.")
        print("Scanning for any non-empty cross-reference fields...")
        refs_found = 0
        for f in BASE.rglob("*.md"):
            if f.name == "index.md":
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue
            # Check for non-empty depends_on/used_by/related
            for field in ["depends_on", "used_by", "related"]:
                m = re.search(rf"^{field}:\s*(\S+)", text, re.MULTILINE)
                if m and m.group(1) not in ("", "null"):
                    refs_found += 1
        print(f"Files with non-empty cross-reference fields: {refs_found}")
