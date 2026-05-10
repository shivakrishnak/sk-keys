"""
difficulty_sort_rename.py
Renames all category entry files so IDs are sequential sorted by difficulty:
  ★☆☆ entries get IDs 001..N
  ★★☆ entries get IDs N+1..M
  ★★★ entries get IDs M+1..K
  🔥/🔬/🌱 entries come after ★★★, sorted alphabetically by symbol

Within each difficulty tier, original ID order is preserved.

Steps:
  1. Build old→new ID mapping for every category
  2. Rename files and update their frontmatter (id:, nav_order:)
  3. Rebuild all index.md tables
  4. Update all cross-references in all .md files
     (depends_on, used_by, related, wikilinks [[CODE-NNN - Title]])

Run: python tmp/difficulty_sort_rename.py [--dry-run] [--category CODE]
"""
import os, re, sys, argparse, shutil
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent / "dictionary"

DIFF_ORDER = {"★☆☆": 0, "★★☆": 1, "★★★": 2, "🌱": 3, "🔥": 4, "🔬": 5}

def diff_rank(d):
    # Normalise and return sort rank
    d = (d or "").strip().strip('"')
    for k, v in DIFF_ORDER.items():
        if k in d:
            return v
    return 1  # default ★★☆ rank

def read_frontmatter_raw(text):
    """Return (fm_dict, fm_end_pos)."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not m:
        return {}, 0
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([\w_-]+):\s*(.*)", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"')
    return fm, m.end()

def get_id_num(id_str):
    m = re.search(r"-(\d+)$", id_str or "")
    return int(m.group(1)) if m else 999999

def build_category_mapping(cat_dir):
    """Returns list of (old_id, new_id, old_path, new_path, fm) sorted by new order."""
    entries = []
    for f in cat_dir.glob("*.md"):
        if f.name == "index.md":
            continue
        text = f.read_text(encoding="utf-8")
        fm, _ = read_frontmatter_raw(text)
        fid = fm.get("id", "")
        if not fid:
            continue
        diff = fm.get("difficulty", "★☆☆")
        entries.append({
            "old_id": fid,
            "old_path": f,
            "fm": fm,
            "diff_rank": diff_rank(diff),
            "id_num": get_id_num(fid),
            "title": fm.get("title", f.stem),
            "difficulty": diff,
        })

    if not entries:
        return []

    # Sort: difficulty first, then original ID order
    entries.sort(key=lambda x: (x["diff_rank"], x["id_num"]))

    code = entries[0]["old_id"].rsplit("-", 1)[0]  # e.g. CSF

    result = []
    for i, e in enumerate(entries, start=1):
        new_num = str(i).zfill(3)
        new_id = f"{code}-{new_num}"
        # Build new filename: keep title part after old "CODE-NNN - " prefix
        old_name = e["old_path"].name
        # Strip old ID prefix to get title part
        title_part_m = re.match(r"^[A-Z]+-\d+\s+-\s+(.*\.md)$", old_name)
        title_part = title_part_m.group(1) if title_part_m else old_name
        new_name = f"{new_id} - {title_part}"
        new_path = e["old_path"].parent / new_name
        result.append({
            "old_id": e["old_id"],
            "new_id": new_id,
            "old_path": e["old_path"],
            "new_path": new_path,
            "fm": e["fm"],
            "diff_rank": e["diff_rank"],
            "title": e["title"],
            "difficulty": e["difficulty"],
        })
    return result

def update_frontmatter_id(text, old_id, new_id, new_nav_order):
    """Replace id: and nav_order: in frontmatter."""
    # Update id field
    text = re.sub(
        r"(^---\r?\n(?:.*\r?\n)*?^id:\s*)" + re.escape(old_id),
        r"\g<1>" + new_id,
        text, count=1, flags=re.MULTILINE)
    # Update nav_order
    text = re.sub(
        r"(^nav_order:\s*)\d+",
        r"\g<1>" + str(new_nav_order),
        text, count=1, flags=re.MULTILINE)
    return text

def rebuild_index_from_mapping(index_path, mapping, cat_dir):
    """Rebuild index.md table rows from new mapping."""
    if not index_path.exists():
        return
    index_text = index_path.read_text(encoding="utf-8")

    yaml_m = re.match(r"(^---\r?\n.*?\r?\n---)", index_text, re.DOTALL)
    yaml_block = yaml_m.group(1) if yaml_m else ""
    after_yaml = index_text[len(yaml_block):]

    # Find table header row
    header_m = re.search(r"(\| *ID *\|[^\n]*\n\|[-| ]+\n)", after_yaml)
    if not header_m:
        return

    pre_table = after_yaml[:header_m.start()]
    table_header = header_m.group(1)

    # Build rows sorted by new_id
    rows = sorted(mapping, key=lambda x: get_id_num(x["new_id"]))
    new_rows = "\n".join(f"| {r['new_id']} | {r['title']} | {r['difficulty']} |"
                         for r in rows) + "\n"

    # Update Keywords count line
    first_id = rows[0]["new_id"]
    last_id  = rows[-1]["new_id"]
    count    = len(rows)
    pre_table = re.sub(
        r"\*\*Keywords:\*\*[^\n]*",
        f"**Keywords:** {first_id}–{last_id} ({count} terms)",
        pre_table)

    new_index = yaml_block + pre_table + table_header + new_rows
    index_path.write_text(new_index, encoding="utf-8")
    print(f"    index.md rebuilt: {count} rows")

def apply_global_replacements(all_files, id_map, dry_run=False):
    """Update all cross-references across all .md files."""
    total_changes = 0
    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue

        original = text
        # Replace in YAML frontmatter fields (depends_on, used_by, related)
        # and in wikilinks [[OLD-NNN - Title]]
        for old_id, new_info in id_map.items():
            new_id = new_info["new_id"]
            title  = new_info["title"]
            if old_id == new_id:
                continue
            code = old_id.rsplit("-", 1)[0]

            # Replace bare ID references in frontmatter lines
            # e.g. "depends_on: CSF-042, JVM-001" → replace CSF-042
            text = re.sub(
                r"(?<![A-Z0-9])" + re.escape(old_id) + r"(?![A-Z0-9\-])",
                new_id, text)

            # Replace wikilinks with title
            text = re.sub(
                r"\[\[" + re.escape(old_id) + r"\s*-\s*([^\]]*)\]\]",
                f"[[{new_id} - \\1]]",
                text)

        if text != original:
            total_changes += 1
            if not dry_run:
                f.write_text(text, encoding="utf-8")

    print(f"    cross-references updated in {total_changes} files")
    return total_changes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--category", default="", help="Single 3-letter CODE")
    args = parser.parse_args()

    # --- Phase 1: Build all mappings ---
    all_mappings = []  # list of per-category mapping lists
    id_map = {}        # global old_id → {new_id, title}

    print("=== Phase 1: Building ID mappings ===")
    for tier_dir in sorted(BASE.iterdir()):
        if not tier_dir.is_dir():
            continue
        for cat_dir in sorted(tier_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            if args.category:
                code = cat_dir.name.split("-")[0].upper()
                if code != args.category.upper():
                    continue

            mapping = build_category_mapping(cat_dir)
            if not mapping:
                continue
            all_mappings.append((cat_dir, mapping))

            changes = sum(1 for m in mapping if m["old_id"] != m["new_id"])
            code = mapping[0]["old_id"].rsplit("-", 1)[0]
            print(f"  {code}: {len(mapping)} entries, {changes} renames needed")

            for m in mapping:
                if m["old_id"] != m["new_id"]:
                    id_map[m["old_id"]] = {"new_id": m["new_id"], "title": m["title"]}

    print(f"\nTotal IDs to remap: {len(id_map)}")

    if not id_map:
        print("Nothing to rename. All categories already sorted by difficulty.")
        return

    # --- Phase 2: Rename files and update frontmatter ---
    print("\n=== Phase 2: Renaming files + updating frontmatter ===")
    for cat_dir, mapping in all_mappings:
        renames = [(m["old_path"], m["new_path"], m["old_id"], m["new_id"])
                   for m in mapping if m["old_id"] != m["new_id"]]
        if not renames:
            continue
        print(f"  {cat_dir.name}: {len(renames)} renames")
        if not dry_run:
            # Two-pass rename to avoid collision (e.g. CSF-002→CSF-001 then CSF-001→CSF-003)
            # First pass: rename to temp names
            temp_map = {}
            for old_p, new_p, old_id, new_id in renames:
                temp_p = old_p.parent / ("_tmp_" + old_p.name)
                old_p.rename(temp_p)
                temp_map[old_id] = (temp_p, new_p, new_id)

            # Second pass: rename from temp to final + update frontmatter
            new_nav = get_id_num
            for old_id, (temp_p, new_p, new_id) in temp_map.items():
                text = temp_p.read_text(encoding="utf-8")
                nav_order = get_id_num(new_id)
                text = update_frontmatter_id(text, old_id, new_id, nav_order)
                new_p.write_text(text, encoding="utf-8")
                temp_p.unlink()

    # --- Phase 3: Rebuild index.md files ---
    print("\n=== Phase 3: Rebuilding index.md tables ===")
    for cat_dir, mapping in all_mappings:
        rebuild_index_from_mapping(cat_dir / "index.md", mapping, cat_dir)

    # --- Phase 4: Update all cross-references ---
    print("\n=== Phase 4: Updating cross-references ===")
    all_md = list(BASE.rglob("*.md"))
    print(f"  Scanning {len(all_md)} .md files...")
    if not dry_run:
        apply_global_replacements(all_md, id_map, dry_run=False)
    else:
        print("  (dry-run: skipping cross-reference update)")

    print("\n=== Done ===")
    if dry_run:
        print("DRY RUN complete - no files written")
    else:
        print(f"Renamed {len(id_map)} IDs across all categories")

if __name__ == "__main__":
    main()
