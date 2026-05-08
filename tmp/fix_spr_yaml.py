import os, re

SPR_DIR = r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-3-java\SPR-spring-core"
FIELDS = ("depends_on", "used_by", "related")

# Pattern: frontmatter field whose value starts with "
START_QUOTE = re.compile(r'^((?:depends_on|used_by|related)):\s+"')

fixed = 0
for fname in sorted(os.listdir(SPR_DIR)):
    if not fname.endswith(".md"):
        continue
    path = os.path.join(SPR_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    new_lines = []
    in_fm = False
    fm_count = 0
    changed = False

    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped == "---":
            fm_count += 1
            in_fm = (fm_count == 1)
        if in_fm and fm_count == 1 and START_QUOTE.match(stripped):
            key = stripped.split(":")[0]
            val = stripped[len(key)+1:].strip()
            # Remove all embedded double-quotes and wrap entire value in one pair
            cleaned = val.replace('"', '')
            new_stripped = f'{key}: "{cleaned}"'
            print(f"  {fname}: {stripped!r}")
            print(f"       -> {new_stripped!r}")
            line = new_stripped + "\n"
            changed = True
        new_lines.append(line)

    if changed:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)
        fixed += 1

print(f"\nTotal files fixed: {fixed}")
