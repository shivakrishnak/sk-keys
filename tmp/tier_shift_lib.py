# -*- coding: utf-8 -*-
"""
Shared library for all tier gap analysis scripts.
Provides process_shift() for populated categories and
process_full() for empty/sparse categories.
"""
import pathlib, re, sys, io
# Force UTF-8 stdout so Unicode in filenames/titles prints safely
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DIFF_MAP = {
    "L0":   "★☆☆", "L1": "★☆☆", "L2": "★★☆", "L3": "★★☆",
    "L4":   "★★★", "L45": "★★★", "L5": "★★★", "META": "★★★",
}
LEVEL_TAG_MAP = {
    "L0":   ["foundational", "mental-model"],
    "L1":   ["foundational", "first-principles"],
    "L2":   ["intermediate", "pattern"],
    "L3":   ["intermediate", "deep-dive", "tradeoff"],
    "L4":   ["advanced", "production", "deep-dive"],
    "L45":  ["advanced", "architecture", "bestpractice"],
    "L5":   ["advanced", "deep-dive", "first-principles"],
    "META": ["advanced", "mental-model", "bestpractice"],
}

def sanitize_filename(new_id, title):
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    return f"{new_id} \u2014 {safe}.md"

def make_permalink(code, title):
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"/{code.lower()}/{slug}/"

def build_frontmatter(new_id, title, level, code, meta):
    diff = DIFF_MAP[level]
    tags_list = [code.lower()] + LEVEL_TAG_MAP[level]
    tags_yaml = "\n".join(f"  - {t}" for t in tags_list)
    nav = int(new_id.split("-")[1])
    permalink = make_permalink(code, title)
    return (
        f"---\n"
        f"id: {new_id}\n"
        f"title: {title}\n"
        f"category: {meta['category']}\n"
        f"tier: {meta['tier']}\n"
        f"folder: {meta['folder']}\n"
        f"difficulty: {diff}\n"
        f"depends_on:\n"
        f"used_by:\n"
        f"related:\n"
        f"tags:\n{tags_yaml}\n"
        f"status: draft\n"
        f"version: 1\n"
        f"layout: default\n"
        f"parent: \"{meta['parent']}\"\n"
        f"nav_order: {nav}\n"
        f"permalink: {permalink}\n"
        f"---\n\n"
        f"# {new_id} \u2014 {title}\n\n"
        f"> Entry stub. Generate full content using Master Prompt v3.0.\n"
    )

def update_frontmatter(content, new_id, title):
    """Update id, title, nav_order, h1 heading in existing frontmatter."""
    nav = int(new_id.split("-")[1])
    # Update id field
    content = re.sub(r'^id:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
    content = re.sub(r'^number:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
    # Update title (quoted or unquoted)
    content = re.sub(r'^title:\s*".+"$', f'title: "{title}"', content, flags=re.MULTILINE)
    content = re.sub(r"^title:\s*'.+'$", f'title: "{title}"', content, flags=re.MULTILINE)
    # Update nav_order
    content = re.sub(r'^nav_order:\s*\d+$', f'nav_order: {nav}', content, flags=re.MULTILINE)
    # Update h1 heading (first # line)
    content = re.sub(r'^#\s+[A-Z]{2,5}-\d+.*$',
                     f'# {new_id} \u2014 {title}',
                     content, count=1, flags=re.MULTILINE)
    return content

def process_shift(code, meta, l0_titles, l45_titles, l5_titles, meta_titles,
                  retire_ids=None):
    """
    Shift all existing files up by 5 (to make room for L0 001-005),
    append L4.5/L5/META stubs at end.
    retire_ids: set of old IDs (e.g. {"JVM-001"}) to treat as WARNING/skip.
    """
    retire_ids = set(retire_ids or [])
    d = pathlib.Path(meta["dir"])
    print(f"\n{'='*60}")
    print(f"SHIFT  {code}  dir={d.name}")
    print(f"{'='*60}")

    # Collect and sort existing files by numeric ID
    existing = []
    for f in d.glob(f"{code}-[0-9]*.md"):
        if f.name == "index.md":
            continue
        m = re.match(rf"({code}-(\d+))", f.stem)
        if m:
            existing.append((int(m.group(2)), m.group(1), f))
    existing.sort(key=lambda x: x[0])

    # Split into keep / retire
    to_keep   = [(n, oid, f) for n, oid, f in existing if oid not in retire_ids]
    to_retire = [(n, oid, f) for n, oid, f in existing if oid in retire_ids]
    for _, oid, f in to_retire:
        print(f"  WARNING (retired): {f.name}")

    # Phase 1 – rename kept files to _tmp_ to avoid collisions
    tmp_map = {}   # new_id -> (tmp_path, old_id, old_title_from_stem)
    for i, (n, old_id, f) in enumerate(to_keep):
        new_num = i + 6          # 006, 007, ...
        new_id  = f"{code}-{new_num:03d}"
        tmp     = f.parent / f"_tmp_{new_id}_{f.name}"
        f.rename(tmp)
        tmp_map[new_id] = (tmp, old_id)
        print(f"  TMP: {f.name} -> {tmp.name}")

    # Phase 2 – rename _tmp_ to final name and patch frontmatter
    for new_id, (tmp, old_id) in sorted(tmp_map.items()):
        # Use original stem title if available; keep existing title in content
        # We only update the ID/nav in frontmatter, not the title text
        old_title = re.sub(rf"^{re.escape(old_id)}\s*[\u2014\-]\s*", "", tmp.stem
                           .replace(f"_tmp_{new_id}_", "").replace(f"{old_id} \u2014 ", ""))
        # Derive title from original filename stem
        stem = tmp.stem  # e.g. "_tmp_JVM-006_JVM-002 -- JRE"
        title_match = re.search(rf"{re.escape(old_id)}\s+[\u2014\-]\s+(.+)$", stem)
        title = title_match.group(1) if title_match else old_title

        new_filename = sanitize_filename(new_id, title)
        dst = d / new_filename
        tmp.rename(dst)
        print(f"  RENAME: {old_id} -> {new_id}: {title}")
        content = dst.read_text(encoding="utf-8", errors="replace")
        content = update_frontmatter(content, new_id, title)
        dst.write_text(content, encoding="utf-8")

    # Phase 3 – create L0 stubs (001–005)
    for i, title in enumerate(l0_titles):
        new_id = f"{code}-{i+1:03d}"
        fname  = sanitize_filename(new_id, title)
        dst    = d / fname
        if dst.exists():
            print(f"  SKIP (exists): {fname}")
            continue
        dst.write_text(build_frontmatter(new_id, title, "L0", code, meta),
                       encoding="utf-8")
        print(f"  CREATE L0: {fname}")

    # Phase 4 – create L4.5, L5, META stubs after last existing
    next_num = len(to_keep) + 6  # first free slot
    level_seq = (
        [("L45", t) for t in l45_titles] +
        [("L5",  t) for t in l5_titles]  +
        [("META",t) for t in meta_titles]
    )
    for level, title in level_seq:
        new_id = f"{code}-{next_num:03d}"
        fname  = sanitize_filename(new_id, title)
        dst    = d / fname
        if dst.exists():
            print(f"  SKIP (exists): {fname}")
        else:
            dst.write_text(build_frontmatter(new_id, title, level, code, meta),
                           encoding="utf-8")
            print(f"  CREATE {level}: {fname}")
        next_num += 1


def process_full(code, meta, keywords):
    """
    For empty/sparse categories: create stub files from a full keyword list.
    keywords: list of (new_id, old_id_or_None, title, level, diff)
    """
    d = pathlib.Path(meta["dir"])
    print(f"\n{'='*60}")
    print(f"FULL   {code}  dir={d.name}")
    print(f"{'='*60}")

    # Build existing file map
    old_files = {}
    for f in d.glob(f"{code}-[0-9]*.md"):
        if f.name == "index.md":
            continue
        m = re.match(rf"({code}-\d+)", f.stem)
        if m:
            old_files[m.group(1)] = f

    # Phase 1 – tmp rename
    tmp_renames = {}
    for new_id, old_id, title, level, _ in keywords:
        if old_id and old_id in old_files:
            src = old_files[old_id]
            tmp = src.parent / f"_tmp_{new_id}_{src.name}"
            src.rename(tmp)
            tmp_renames[new_id] = (tmp, old_id, title, level)
            print(f"  TMP: {src.name} -> {tmp.name}")

    # Phase 2 – rename to final
    for new_id, old_id, title, level, _ in keywords:
        if new_id in tmp_renames:
            tmp, old_id_, title_, level_ = tmp_renames[new_id]
            fname = sanitize_filename(new_id, title)
            dst   = d / fname
            tmp.rename(dst)
            print(f"  RENAME: {old_id_} -> {new_id}: {title}")
            content = dst.read_text(encoding="utf-8", errors="replace")
            content = update_frontmatter(content, new_id, title)
            dst.write_text(content, encoding="utf-8")

    # Phase 3 – create stubs for new keywords
    old_ids_used = {kw[1] for kw in keywords if kw[1]}
    for new_id, old_id, title, level, _ in keywords:
        if not old_id:
            fname = sanitize_filename(new_id, title)
            dst   = d / fname
            if dst.exists():
                print(f"  SKIP (exists): {fname}")
                continue
            dst.write_text(build_frontmatter(new_id, title, level, code, meta),
                           encoding="utf-8")
            print(f"  CREATE: {fname}")

    # Phase 4 – report retired
    for old_id, f in old_files.items():
        if old_id not in old_ids_used:
            print(f"  WARNING (retired): {f.name}")
