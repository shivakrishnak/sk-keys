"""
rebuild_indexes.py
Rebuilds every category index.md table from actual file frontmatter.
- Keeps YAML block, h1, description line, and Keywords line header intact.
- Rebuilds the | ID | Keyword | Difficulty | table from file data.
- Sorts rows by numeric ID order.
- Reports mismatches between old index and files.
Run: python tmp/rebuild_indexes.py [--dry-run] [--category CODE]
"""
import os, re, sys, argparse
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"
DIFFICULTY_EMOJI = {"★☆☆": "★☆☆", "★★☆": "★★☆", "★★★": "★★★",
                    "🔬": "🔬", "🔥": "🔥", "🌱": "🌱"}

def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"')
    return fm

def get_id_num(id_str):
    m = re.search(r"-(\d+)$", id_str or "")
    return int(m.group(1)) if m else 999999

def rebuild_index(cat_dir, dry_run=False):
    index_path = cat_dir / "index.md"
    if not index_path.exists():
        print(f"  [SKIP] no index.md: {cat_dir.name}")
        return 0

    # Collect all entry files
    entries = []
    for f in sorted(cat_dir.glob("*.md")):
        if f.name == "index.md":
            continue
        fm = read_frontmatter(f)
        fid   = fm.get("id", "")
        title = fm.get("title", f.stem)
        diff  = fm.get("difficulty", "★☆☆")
        entries.append((fid, title, diff))

    entries.sort(key=lambda x: get_id_num(x[0]))

    if not entries:
        print(f"  [SKIP] no entry files: {cat_dir.name}")
        return 0

    # Read current index.md
    index_text = index_path.read_text(encoding="utf-8")

    # --- Extract parts we keep intact ---
    # 1. YAML frontmatter block
    yaml_m = re.match(r"(^---\r?\n.*?\r?\n---)", index_text, re.DOTALL)
    yaml_block = yaml_m.group(1) if yaml_m else ""

    # 2. Everything between YAML and the keyword table start
    after_yaml = index_text[len(yaml_block):]

    # Find the keyword table (| ID | Keyword | ... header row)
    table_header_m = re.search(
        r"(\n\*\*Keywords:\*\*[^\n]*\n\n\|[^\n]*ID[^\n]*\n\|[-| ]+\n)",
        after_yaml)

    if table_header_m:
        pre_table = after_yaml[:table_header_m.start()]
        table_header_text = table_header_m.group(1)
    else:
        # Fallback: look for just the table
        table_m = re.search(r"\n(\|[^\n]*ID[^\n]*\n\|[-| ]+\n)", after_yaml)
        if not table_m:
            print(f"  [SKIP] cannot find table in {cat_dir.name}")
            return 0
        pre_table = after_yaml[:table_m.start()]
        kw_count_line = f"\n**Keywords:** {entries[0][0]}–{entries[-1][0]} ({len(entries)} terms)\n\n"
        table_header_text = kw_count_line + table_m.group(1)

    # Build new table rows
    new_rows = []
    for fid, title, diff in entries:
        new_rows.append(f"| {fid} | {title} | {diff} |")

    # Update Keywords count line in table_header_text
    first_id = entries[0][0]
    last_id  = entries[-1][0]
    count    = len(entries)
    table_header_text = re.sub(
        r"\*\*Keywords:\*\*[^\n]*",
        f"**Keywords:** {first_id}–{last_id} ({count} terms)",
        table_header_text)

    new_index = yaml_block + pre_table + table_header_text + "\n".join(new_rows) + "\n"

    # Report changes
    old_table_m = re.search(r"\|[^\n]*ID[^\n]*\n(?:\|[^\n]*\n)*", index_text)
    old_rows_text = old_table_m.group(0) if old_table_m else ""
    new_rows_text = "\n".join(new_rows) + "\n"

    changed = new_rows_text != old_rows_text
    if changed:
        print(f"  [UPDATE] {cat_dir.name}: {count} entries")
    else:
        print(f"  [OK]     {cat_dir.name}: {count} entries (no change)")

    if not dry_run and changed:
        index_path.write_text(new_index, encoding="utf-8")

    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--category", default="", help="Single category CODE")
    args = parser.parse_args()

    total = 0
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
            total += rebuild_index(cat_dir, dry_run=args.dry_run)

    print(f"\nTotal entries processed: {total}")
    if args.dry_run:
        print("DRY RUN - no files written")

if __name__ == "__main__":
    main()
