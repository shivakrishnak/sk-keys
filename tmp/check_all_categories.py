#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_all_categories.py
=======================
Scans ALL category folders in the sk-keys Technical Dictionary
and produces a compliance report per category and per file.

Version detection (per Master Prompt v3.0 spec):
  v1   = missing any of the 7 core v2 section headers
  v2   = all 7 core sections present
  v2.1 = v2 + Transferable Wisdom + Surprising Truth + EVOLUTION + *Hint:
  v3.0 = v2.1 + id: CODE-NNN + status: field + deps use full IDs

Usage:
  python3 check_all_categories.py [--category CODE] [--v3-only] [--csv]

  --category CODE  Only audit one category (e.g. JVM, DPT, SPR)
  --v3-only        Only show files that are NOT v3.0 compliant
  --csv            Output CSV instead of ASCII table (for spreadsheet import)
  --incomplete     Only show files where status != complete
"""

import os
import re
import sys
import argparse
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
BASE = Path(r"C:\ASK\MyWorkspace\sk-keys\dictionary")

# v2 section headers (missing any = v1)
V2_REQUIRED = [
    "### 🔥 The Problem This Solves",
    "### ⏱️ Understand It in 30 Seconds",
    "### 🧪 Thought Experiment",
    "### 📶 Gradual Depth - Four Levels",
    "### 🔄 The Complete Picture - End-to-End Flow",
    "### ⚖️ Comparison Table",
    "### 🚨 Failure Modes & Diagnosis",
]

# v2.1 additions
V21_REQUIRED = [
    "### 💎 Transferable Wisdom",
    "### 💡 The Surprising Truth",
    "**EVOLUTION:**",
    "*Hint:",        # at least one *Hint: line in Think section
]

# v3.0 YAML fields
V30_YAML = [
    r"(?m)^id:\s+[A-Z]{3}-\d{3}",   # id: CODE-NNN
    r"(?m)^status:\s+\S",           # status: <something>
    r"(?m)^tier:\s+\S",             # tier: present
    r"(?m)^folder:\s+\S",           # folder: present
]

# Checks that depends_on/used_by/related are NOT keyword-name style
# (if they have values, they must match CODE-NNN pattern)
DEP_FIELDS = ["depends_on", "used_by", "related"]
DEP_ID_RE  = re.compile(r"^[A-Z]{3}-\d{3}$")

# ── Helpers ──────────────────────────────────────────────────────────────

def read_utf8(path):
    return path.read_text(encoding="utf-8", errors="replace")

def detect_version(content):
    """Return (version_string, checks_dict)."""
    checks = {}

    # --- v2 check ---
    for header in V2_REQUIRED:
        checks[header] = header in content
    is_v2 = all(checks[h] for h in V2_REQUIRED)

    if not is_v2:
        return "v1", checks

    # --- v2.1 check ---
    for item in V21_REQUIRED:
        checks[item] = item in content
    is_v21 = all(checks[i] for i in V21_REQUIRED)

    if not is_v21:
        return "v2", checks

    # --- v3.0 check ---
    for pattern in V30_YAML:
        checks[pattern] = bool(re.search(pattern, content))
    is_v30_yaml = all(checks[p] for p in V30_YAML)

    # Check deps use full IDs (not keyword names)
    dep_ok = True
    dep_detail = {}
    for field in DEP_FIELDS:
        m = re.search(rf"(?m)^{field}:\s*(.+)$", content)
        if m:
            raw = m.group(1).strip()
            if raw and raw.lower() not in ("", "null", "~"):
                tags = [t.strip() for t in raw.split(",")]
                bad = [t for t in tags if t and not DEP_ID_RE.match(t)]
                if bad:
                    dep_ok = False
                    dep_detail[field] = bad
    checks["deps_use_ids"] = dep_ok
    if dep_detail:
        checks["deps_violations"] = dep_detail

    if not (is_v30_yaml and dep_ok):
        return "v2.1", checks

    return "v3.0", checks

def get_status(content):
    m = re.search(r"(?m)^status:\s*(\S+)", content)
    return m.group(1) if m else "MISSING"

def get_id(content):
    m = re.search(r"(?m)^id:\s*(\S+)", content)
    return m.group(1) if m else "MISSING"

def get_title(content):
    m = re.search(r"(?m)^title:\s*[\"']?(.+?)[\"']?\s*$", content)
    return m.group(1).strip('"\'') if m else "MISSING"

def section_count(content):
    return len(re.findall(r"(?m)^###\s", content))

def file_size_kb(path):
    return round(path.stat().st_size / 1024, 1)

# ── Main audit ───────────────────────────────────────────────────────────

def audit_category(cat_dir: Path):
    """Audit one category folder. Returns list of result dicts."""
    results = []
    files = sorted(
        [f for f in cat_dir.glob("*.md") if f.name != "index.md"],
        key=lambda f: f.name
    )
    for f in files:
        content = read_utf8(f)
        version, checks = detect_version(content)
        status  = get_status(content)
        entry_id = get_id(content)
        title   = get_title(content)
        secs    = section_count(content)
        size_kb = file_size_kb(f)

        # Missing section list (for non-v3.0)
        missing = []
        for h in V2_REQUIRED:
            if not checks.get(h, True):
                missing.append(h.replace("### ", ""))
        for i in V21_REQUIRED:
            if not checks.get(i, True):
                missing.append(i)
        for p in V30_YAML:
            if not checks.get(p, True):
                label = re.search(r"\^(\w+):", p)
                missing.append(label.group(1) if label else p)
        if not checks.get("deps_use_ids", True):
            missing.append("deps_use_ids")

        results.append({
            "file":     f.name,
            "id":       entry_id,
            "title":    title[:50],
            "version":  version,
            "status":   status,
            "sections": secs,
            "size_kb":  size_kb,
            "ok":       (version == "v3.0" and status == "complete"),
            "missing":  missing,
            "checks":   checks,
        })
    return results

def print_category_report(cat_dir: Path, results, v3_only=False,
                           incomplete_only=False, csv_mode=False):
    code = cat_dir.name.split("-")[0] if "-" in cat_dir.name else cat_dir.name
    total = len(results)
    ok    = sum(1 for r in results if r["ok"])
    v3cnt = sum(1 for r in results if r["version"] == "v3.0")
    v21   = sum(1 for r in results if r["version"] == "v2.1")
    v2    = sum(1 for r in results if r["version"] == "v2")
    v1    = sum(1 for r in results if r["version"] == "v1")
    draft = sum(1 for r in results if r["status"] not in ("complete",))

    if csv_mode:
        for r in results:
            if v3_only and r["version"] == "v3.0" and r["status"] == "complete":
                continue
            if incomplete_only and r["status"] == "complete" and r["version"] == "v3.0":
                continue
            print(f"{code},{r['id']},{r['title']},{r['version']},"
                  f"{r['status']},{r['sections']},{r['size_kb']},"
                  f"\"{';'.join(r['missing'])}\"")
        return

    print(f"\n{'='*70}")
    print(f"  {code}: {cat_dir.name}")
    print(f"  Total:{total}  OK:{ok}  v3.0:{v3cnt}  v2.1:{v21}  v2:{v2}  v1:{v1}  non-complete:{draft}")
    print(f"{'='*70}")

    header = f"{'ID':<12} {'Ver':<5} {'Status':<12} {'Sec':>3} {'KB':>5}  Title"
    print(header)
    print("-" * 70)

    for r in results:
        if v3_only and r["version"] == "v3.0" and r["status"] == "complete":
            continue
        if incomplete_only and r["status"] == "complete" and r["version"] == "v3.0":
            continue

        flag = " ✓" if r["ok"] else " ←"
        ver_color = r["version"]
        print(f"{r['id']:<12} {ver_color:<5} {r['status']:<12} "
              f"{r['sections']:>3} {r['size_kb']:>5}  {r['title'][:40]}{flag}")

        if r["missing"] and not r["ok"]:
            for m in r["missing"][:6]:  # show up to 6 issues
                print(f"{'':>12}   ↳ MISSING: {m}")

def print_global_summary(all_results, category_stats):
    grand_total = sum(s["total"] for s in category_stats.values())
    grand_ok    = sum(s["ok"]    for s in category_stats.values())
    grand_v3    = sum(s["v3"]    for s in category_stats.values())
    grand_draft = sum(s["draft"] for s in category_stats.values())

    print(f"\n{'#'*70}")
    print(f"  GLOBAL SUMMARY — {grand_total} entries across {len(category_stats)} categories")
    print(f"  Fully compliant (v3.0+complete): {grand_ok}/{grand_total}")
    print(f"  v3.0 YAML (any status):          {grand_v3}/{grand_total}")
    print(f"  non-complete status:             {grand_draft}/{grand_total}")
    print(f"{'#'*70}")

    print(f"\n{'CODE':<8} {'Total':>5} {'OK':>5} {'v3.0':>5} "
          f"{'v2.1':>5} {'v2':>5} {'v1':>5} {'draft':>6}  Category")
    print("-" * 70)

    for code, s in sorted(category_stats.items()):
        status_col = "✓" if s["ok"] == s["total"] else f"{s['ok']}/{s['total']}"
        print(f"{code:<8} {s['total']:>5} {status_col:>5} {s['v3']:>5} "
              f"{s['v21']:>5} {s['v2']:>5} {s['v1']:>5} {s['draft']:>6}  {s['name']}")

# ── Entry point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audit sk-keys Technical Dictionary for v3.0 compliance"
    )
    parser.add_argument("--category", "-c", metavar="CODE",
        help="Only audit this category code (e.g. JVM, DPT)")
    parser.add_argument("--v3-only", action="store_true",
        help="Only show files that are NOT v3.0 complete")
    parser.add_argument("--incomplete", action="store_true",
        help="Only show files where status != complete")
    parser.add_argument("--csv", action="store_true",
        help="Output CSV format")
    parser.add_argument("--summary-only", action="store_true",
        help="Show only the global summary table")
    args = parser.parse_args()

    if args.csv:
        print("CODE,ID,Title,Version,Status,Sections,Size_KB,Missing")

    all_results = {}
    category_stats = {}

    # Find all category folders
    tier_dirs = sorted(BASE.glob("tier-*"))
    for tier in tier_dirs:
        for cat_dir in sorted(tier.iterdir()):
            if not cat_dir.is_dir():
                continue
            cat_code = cat_dir.name.split("-")[0].upper()

            # Filter by category if specified
            if args.category and cat_code.upper() != args.category.upper():
                continue

            results = audit_category(cat_dir)
            if not results:
                continue

            all_results[cat_code] = results

            ok_count = sum(1 for r in results if r["ok"])
            category_stats[cat_code] = {
                "name":  cat_dir.name,
                "total": len(results),
                "ok":    ok_count,
                "v3":    sum(1 for r in results if r["version"] == "v3.0"),
                "v21":   sum(1 for r in results if r["version"] == "v2.1"),
                "v2":    sum(1 for r in results if r["version"] == "v2"),
                "v1":    sum(1 for r in results if r["version"] == "v1"),
                "draft": sum(1 for r in results
                             if r["status"] not in ("complete",)),
            }

            if not args.summary_only:
                show_all = (ok_count < len(results)) or not (args.v3_only or args.incomplete)
                if show_all or args.category:
                    print_category_report(
                        cat_dir, results,
                        v3_only=args.v3_only,
                        incomplete_only=args.incomplete,
                        csv_mode=args.csv
                    )

    if not args.csv:
        print_global_summary(all_results, category_stats)

    # Exit code: 0 = all ok, 1 = some not compliant
    total_not_ok = sum(
        s["total"] - s["ok"] for s in category_stats.values()
    )
    sys.exit(0 if total_not_ok == 0 else 1)

if __name__ == "__main__":
    main()

