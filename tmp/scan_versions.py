#!/usr/bin/env python3
import os
import re
from pathlib import Path
import csv

DICT_ROOT = r"c:\ASK\MyWorkspace\sk-keys\dictionary"

# Required frontmatter fields
REQUIRED_FM_FIELDS = {'layout', 'title', 'parent', 'nav_order', 'permalink'}

# Required content sections
REQUIRED_SECTIONS = [
    "### 🔥 The Problem This Solves",
    "### ⏱️ Understand It in 30 Seconds",
    "### 🧪 Thought Experiment",
    "### 📶 Gradual Depth",
    "### 🔄 The Complete Picture",
    "### ⚖️ Comparison Table",
    "### 🚨 Failure Modes",
]

def parse_frontmatter(content):
    """Extract YAML frontmatter and return dict of fields"""
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return {}, content

    fm_lines = []
    body_start = 1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            body_start = i + 1
            break
        fm_lines.append(lines[i])

    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key = line.split(':')[0].strip()
            fm_dict[key] = True

    body = '\n'.join(lines[body_start:])
    return fm_dict, body

def check_required_sections(body):
    """Check which required sections are present"""
    missing = []
    for section in REQUIRED_SECTIONS:
        if section not in body:
            missing.append(section)
    return missing

def determine_version(file_path):
    """Determine correct version for a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if it's just a stub
    if "Entry stub" in content and content.count('\n') < 50:
        return 0, True, [], []

    fm_dict, body = parse_frontmatter(content)

    # Check frontmatter
    missing_fm = REQUIRED_FM_FIELDS - set(fm_dict.keys())

    # Check content sections
    missing_sections = check_required_sections(body)

    # Determine version
    if missing_fm or missing_sections:
        version = 1
    else:
        version = 2

    return version, False, list(missing_fm), missing_sections

# Get all .md files
results = []
for root, dirs, files in os.walk(DICT_ROOT):
    for file in files:
        if file.endswith('.md') and file != 'index.md':
            file_path = os.path.join(root, file)
            try:
                # Read current version
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'version:\s*(\d+)', content)
                    current_version = int(match.group(1)) if match else 0

                correct_version, is_stub, missing_fm, missing_sections = determine_version(file_path)
                needs_update = (current_version != correct_version)

                results.append({
                    'FilePath': file_path,
                    'CurrentVersion': current_version,
                    'CorrectVersion': correct_version,
                    'IsStub': is_stub,
                    'MissingFrontmatter': ','.join(missing_fm) if missing_fm else '',
                    'MissingContent': ','.join(missing_sections[:2]) if missing_sections else '',
                    'NeedsUpdate': 'YES' if needs_update else 'NO'
                })
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Write CSV
output_path = r"c:\ASK\MyWorkspace\sk-keys\tmp\version_updates.csv"
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['FilePath', 'CurrentVersion', 'CorrectVersion', 'IsStub', 'MissingFrontmatter', 'MissingContent', 'NeedsUpdate'])
    writer.writeheader()
    writer.writerows(results)

print(f"Scan complete. Results in {output_path}")
print(f"Total files: {len(results)}")
print(f"Needing updates: {sum(1 for r in results if r['NeedsUpdate'] == 'YES')}")
