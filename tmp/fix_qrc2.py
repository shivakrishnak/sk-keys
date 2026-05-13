"""Fix Quick Reference Card formatting in interview files.

Adds blank lines between key-value entries so each renders
as a separate paragraph in Jekyll/kramdown.
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
    prev_was_qrc_entry = False

    for line in lines:
        if (
            "Quick Reference Card" in line
            and line.startswith("### ")
        ):
            in_qrc = True
            prev_was_qrc_entry = False
        elif line.startswith("### ") or (
            line.startswith("**If you remember")
        ):
            in_qrc = False
            prev_was_qrc_entry = False

        is_qrc_entry = False
        if in_qrc and line.startswith("**"):
            m = re.match(
                r"\*\*[A-Z][A-Z /\-]+:\*\*", line
            )
            if m:
                is_qrc_entry = True
                # Remove trailing double spaces if present
                if line.endswith("  "):
                    line = line[:-2]
                    modified = True

        # Add blank line before QRC entries (except first)
        if is_qrc_entry and prev_was_qrc_entry:
            new_lines.append("")
            modified = True

        new_lines.append(line)
        prev_was_qrc_entry = is_qrc_entry

    if modified:
        p.write_text("\n".join(new_lines), encoding="utf-8")
        count += 1
        print(f"Fixed: {f}")

print(f"Total files fixed: {count}")
