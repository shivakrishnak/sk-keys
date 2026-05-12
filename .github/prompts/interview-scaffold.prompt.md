---
mode: agent
description: "Run interview scaffold generator for a topic - creates [FILL:...] stub files"
tools:
  - run_in_terminal
  - read_file
  - list_dir
  - file_search
---

# Interview Scaffold Generator

Run the scaffold generator to create `[FILL:...]` stub files for an interview topic.
The scaffold pre-builds all 19 sections per keyword with placeholder markers, reducing
content generation token usage by ~50%.

## Usage

**Target topic:** `${input:topic:Topic name (e.g. java, hibernate, react)}`

## Workflow

1. Check `interview/_config/topic-registry.md` for the topic's folder and status
2. Verify the topic folder exists under `interview/`
3. Run the scaffold generator:

```powershell
& "$env:USERPROFILE\.local\bin\python3.14.exe" interview/_config/interview_scaffold.py ${input:topic}
```

4. Verify generated files:
   - List all `.md` files in the topic folder
   - Confirm each file has `[FILL:...]` stubs
   - Count total keywords scaffolded

5. Update `topic-registry.md` status to `scaffolded`

## Post-Scaffold

After scaffolding, use `@interview-fill-content` to replace `[FILL:...]` stubs
with real content one keyword at a time.

## Notes

- Python path: `$env:USERPROFILE\.local\bin\python3.14.exe`
- Always use `pwsh` (PowerShell 7+)
- The scaffold script reads keyword lists from `interview/<topic>/index.md`
- If index.md doesn't exist, scaffold will fail - create it first
