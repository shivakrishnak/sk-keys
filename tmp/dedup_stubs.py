"""Remove duplicate stubs: same title, keep lowest ID."""
import re
from pathlib import Path

base = Path(__file__).parent.parent / "dictionary"
dupes = []
for tier in sorted(base.iterdir()):
    if not tier.is_dir():
        continue
    for cat_dir in sorted(tier.iterdir()):
        if not cat_dir.is_dir():
            continue
        files = sorted([f for f in cat_dir.glob("*.md") if f.name != "index.md"])
        seen = {}
        for f in files:
            try:
                txt = f.read_text(encoding="utf-8")
            except Exception:
                continue
            tm = re.search(r'^title:\s*"?([^"\n]+)"?', txt, re.MULTILINE)
            im = re.search(r"^id:\s*(\S+)", txt, re.MULTILINE)
            if not tm or not im:
                continue
            title = tm.group(1).strip()
            nid = im.group(1).strip()
            try:
                new_n = int(nid.split("-")[-1])
            except ValueError:
                continue
            if title in seen:
                old_n = int(seen[title]["id"].split("-")[-1])
                if new_n > old_n:
                    dupes.append(f)
                else:
                    dupes.append(seen[title]["path"])
                    seen[title] = {"id": nid, "path": f}
            else:
                seen[title] = {"id": nid, "path": f}

print(f"Remaining duplicates: {len(dupes)}")
for d in dupes[:5]:
    print(f"  {d.name}")
for d in dupes:
    d.unlink()
print("Done - all duplicates removed")
