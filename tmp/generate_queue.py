#!/usr/bin/env python3
"""generate_queue.py
===================
Finds stub / draft entries that need full v3.0 content generated.

A file is treated as a stub when ANY of these are true:
  - Body contains "> Entry stub"
  - status: draft  AND  file is < 3 KB

Usage:
  # By category code
  python3 tmp/generate_queue.py --target MSV
  python3 tmp/generate_queue.py --target JVM --batch-size 5

  # By tier number or folder name
  python3 tmp/generate_queue.py --target 3
  python3 tmp/generate_queue.py --target tier-5-distributed-architecture

  # Just list stubs (no batch formatting)
  python3 tmp/generate_queue.py --target LNX --list
"""
import re
import sys
import argparse
from pathlib import Path

# Force UTF-8 output on Windows (avoids cp1252 encode errors)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = Path(r"C:\ASK\MyWorkspace\sk-keys\dictionary")


# ── Helpers ───────────────────────────────────────────────────────────────

def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def get_category_name(cat_dir: Path) -> str:
    """Read the title from the category's index.md."""
    index = cat_dir / "index.md"
    if index.exists():
        m = re.search(
            r'(?m)^title:\s*["\']?(.+?)["\']?\s*$',
            read_utf8(index)
        )
        if m:
            return m.group(1).strip("\"'")
    # Fallback: derive from folder name
    parts = cat_dir.name.split("-", 1)
    return parts[1].replace("-", " ").title() if len(parts) > 1 else cat_dir.name


def is_stub(fp: Path) -> bool:
    """Return True if the file is a stub needing full content."""
    text = read_utf8(fp)
    if "> Entry stub" in text:
        return True
    if re.search(r"(?m)^status:\s*draft", text) and fp.stat().st_size < 3_000:
        return True
    return False


def stub_info(fp: Path) -> dict | None:
    """Extract id, title, difficulty from a stub file."""
    text = read_utf8(fp)

    m = re.search(r"(?m)^id:\s*(\S+)", text)
    entry_id = m.group(1) if m else ""

    m = re.search(r'(?m)^title:\s*["\']?(.+?)["\']?\s*$', text)
    title = m.group(1).strip("\"'") if m else ""

    m = re.search(r"(?m)^difficulty:\s*(.+)", text)
    difficulty = m.group(1).strip() if m else "★☆☆"

    if not entry_id or not title:
        return None
    return {"id": entry_id, "title": title, "difficulty": difficulty}


# ── Lookup ────────────────────────────────────────────────────────────────

def find_category_dirs(code: str) -> list[Path]:
    """Find category folder(s) matching a CODE (e.g. MSV, JVM)."""
    prefix = code.upper() + "-"
    results = []
    for tier in sorted(BASE.glob("tier-*")):
        for cat in sorted(tier.iterdir()):
            if cat.is_dir() and cat.name.upper().startswith(prefix):
                results.append(cat)
    return results


def find_tier_dirs(target: str) -> list[Path]:
    """Find tier folder(s) matching a number or folder name."""
    all_tiers = sorted(BASE.glob("tier-*"))
    if target.isdigit():
        return [d for d in all_tiers
                if d.name.startswith(f"tier-{target}-")]
    if target.startswith("tier-"):
        return [d for d in all_tiers
                if d.name == target or d.name.startswith(target)]
    return []


def collect_stubs(cat_dir: Path) -> list[dict]:
    """Return list of stub_info dicts for a category folder."""
    stubs = []
    files = sorted(
        [f for f in cat_dir.glob("*.md") if f.name != "index.md"],
        key=lambda f: f.name,
    )
    for fp in files:
        if is_stub(fp):
            info = stub_info(fp)
            if info:
                stubs.append(info)
    return stubs


# ── Output ────────────────────────────────────────────────────────────────

SEP = "-" * 62


def print_batch(batch: list[dict], cat_dir: Path, batch_num: int):
    cat_name = get_category_name(cat_dir)
    tier = cat_dir.parent.name
    folder = cat_dir.name
    ids = [s["id"] for s in batch]
    range_label = (
        f"{ids[0]} through {ids[-1]}" if len(ids) > 1 else ids[0]
    )
    print(f"\n{SEP}")
    print(f"# Batch {batch_num}  ({range_label})")
    print(f"Generate dictionary entries {range_label}:")
    for s in batch:
        print(f"  {s['id']:<12} | {s['title']:<42} | {s['difficulty']}")
    print()
    print(f"Category: {cat_name} | Tier: {tier} | Folder: {folder}")
    print("Follow Master Prompt v3.0 exactly.")


def print_list(stubs: list[dict], cat_dir: Path):
    cat_name = get_category_name(cat_dir)
    print(f"\n{SEP}")
    print(f"{cat_name}  ({len(stubs)} stubs)")
    for s in stubs:
        print(f"  {s['id']:<12} | {s['title']:<42} | {s['difficulty']}")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Find Technical Dictionary stubs and print generation batches"
    )
    parser.add_argument(
        "--target", "-t", required=True,
        help=(
            "Category code (e.g. MSV, JVM) "
            "OR tier number (e.g. 3, 5) "
            "OR tier folder (e.g. tier-3-java)"
        ),
    )
    parser.add_argument(
        "--batch-size", "-b", type=int, default=10,
        help="Entries per generation batch (default: 10)",
    )
    parser.add_argument(
        "--list", "-l", action="store_true",
        help="Just list stubs without batch formatting",
    )
    args = parser.parse_args()

    target = args.target.strip()

    # Resolve target to a list of category dirs
    cat_dirs: list[Path] = []

    if target.isdigit() or target.lower().startswith("tier-"):
        tier_dirs = find_tier_dirs(target.lower())
        if not tier_dirs:
            print(f"ERROR: No tier folder found matching '{target}'",
                  file=sys.stderr)
            sys.exit(1)
        for tier_dir in tier_dirs:
            for cat in sorted(tier_dir.iterdir()):
                if cat.is_dir():
                    cat_dirs.append(cat)
    else:
        cat_dirs = find_category_dirs(target)
        if not cat_dirs:
            print(f"ERROR: No category found matching '{target}'",
                  file=sys.stderr)
            sys.exit(1)

    # Process each category
    total_stubs = 0
    batch_num = 0

    for cat_dir in cat_dirs:
        stubs = collect_stubs(cat_dir)
        if not stubs:
            continue
        total_stubs += len(stubs)

        if args.list:
            print_list(stubs, cat_dir)
            continue

        cat_name = get_category_name(cat_dir)
        tier = cat_dir.parent.name
        folder = cat_dir.name
        print(f"\n{'='*62}")
        print(f"CATEGORY : {cat_name}")
        print(f"Tier     : {tier}")
        print(f"Folder   : {folder}")
        print(f"Stubs    : {len(stubs)}")

        for i in range(0, len(stubs), args.batch_size):
            batch_num += 1
            print_batch(stubs[i:i + args.batch_size], cat_dir, batch_num)

    print("\n" + "=" * 62)
    print(f"TOTAL STUBS FOUND: {total_stubs}")
    if total_stubs == 0:
        print("Nothing to generate — all entries are complete.")
    sys.exit(0 if total_stubs == 0 else 1)


if __name__ == "__main__":
    main()
