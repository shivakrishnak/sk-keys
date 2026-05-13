"""Fix Quick Reference Card formatting in interview files.

Adds trailing two-space line breaks to key-value lines
inside Quick Reference Card sections so they render as
separate lines in Markdown instead of one paragraph.
"""
import re
import pathlib
import glob

files = glob.glob("interview/java/Java - *.md")
files += glob.glob(
    "interview/java-concurrency/Java Concurrency - *.md"
)
count = 0

for f in files:
    p = pathlib.Path(f)
    text = p.read_text(encoding="utf-8")
    lines = text.split("\n")
    in_qrc = False
    modified = False
    new_lines = []

    for line in lines:
        if (
            "Quick Reference Card" in line
            and line.startswith("### ")
        ):
            in_qrc = True
        elif line.startswith("### "):
            in_qrc = False

        if (
            in_qrc
            and line.startswith("**")
            and ":**" in line
            and not line.endswith("  ")
        ):
            m = re.match(r"\*\*[A-Z][A-Z /\-]+:\*\*", line)
            if m:
                line = line + "  "
                modified = True

        new_lines.append(line)

    if modified:
        p.write_text("\n".join(new_lines), encoding="utf-8")
        count += 1
        print(f"Fixed: {f}")

print(f"Total files fixed: {count}")
