# 📌 Custom Instructions for GitHub Pages Markdown Automation

These instructions can be added to your GitHub repository documentation or shared with team members.

---

## For GitHub Copilot / AI Assistants

### System Instructions

When helping with markdown files in the `sk-keys` repository:

**IMPORTANT RULES:**

1. **File Naming Convention**
   - Always use format: `☕ NNN — Title Here.md` (for Java)
   - Use numeric prefix: 001, 002, 003 (3 digits)
   - Use emoji prefix relevant to section
   - Replace NNN with sequential numbers

2. **Never Manually Add Frontmatter**
   - Instead, tell user: "Run `Update-MarkdownFrontmatter.ps1` to add frontmatter automatically"
   - If frontmatter is needed, provide the script command

3. **Emoji Prefixes by Section**
   - Java: ☕
   - Spring: 🌱
   - Distributed Systems: 🔗
   - Databases: 💾
   - Messaging & Streaming: 📨
   - Networking & HTTP: 🌐
   - OS & Systems: 🖥️
   - System Design: 🏗️
   - DSA: 🔧
   - Software Design: 🧩
   - Cloud & Infrastructure: ☁️
   - DevOps & SDLC: 🔄

4. **When User Asks About Adding New Files**
   
   Respond with:
   ```
   To add new markdown files to [SECTION]:
   
   1. Create file with proper naming:
      ☕ NNN — Your Title Here.md
   
   2. Run automation script:
      .\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\[section]" -ParentTitle "[Parent Name]"
   
   3. Files automatically get:
      - Jekyll YAML frontmatter
      - Proper parent-child relationships
      - Clean URLs
      - Sequential navigation order
   
   4. Commit and push:
      git add docs/
      git commit -m "Add [section] topics [number range]"
      git push origin main
   ```

5. **File Update Workflow**
   - Create content file → Run script → Commit → Push → Done!
   - No manual YAML editing needed
   - No permalink creation needed
   - No nav_order counting needed

6. **Supported Sections & Parent Titles**
   - docs\java → "Java Fundamentals"
   - docs\spring → "Spring"
   - docs\Distributed Systems → "Distributed Systems"
   - docs\Databases → "Databases"
   - docs\Messaging & Streaming → "Messaging & Streaming"
   - docs\Networking & HTTP → "Networking & HTTP"
   - docs\OS & Systems → "OS & Systems"
   - docs\System Design → "System Design"
   - docs\DSA → "DSA"
   - docs\Software Design → "Software Design"
   - docs\Cloud & Infrastructure → "Cloud & Infrastructure"
   - docs\DevOps & SDLC → "DevOps & SDLC"

---

## Example Interactions

### User: "I want to add 5 new Java topics"

**Your Response:**
```
Great! Here's the quickest way:

Step 1: Create your markdown files with proper naming pattern
   ☕ 012 — Garbage Collection.md
   ☕ 013 — Finalization.md
   ☕ 014 — Reference Queue.md
   ☕ 015 — Memory Leak Detection.md
   ☕ 016 — GC Tuning.md

Step 2: Add your content to each file

Step 3: Run the automation script
   .\Update-MarkdownFrontmatter.ps1 `
       -SectionPath "docs\java" `
       -ParentTitle "Java Fundamentals"

Step 4: Commit and push
   git add docs/java/
   git commit -m "Add 5 Java GC topics (012-016)"
   git push origin main

Done! Files will appear in GitHub Pages in 1-2 minutes.
```

### User: "How do I add a new markdown file?"

**Your Response:**
```
For [SECTION]:

1. Create file: [SECTION]/☕ NNN — Your Title.md
2. Run: .\Update-MarkdownFrontmatter.ps1 -SectionPath "docs\[section]" -ParentTitle "[Parent]"
3. Git: git add docs/ && git commit -m "Add [title]" && git push

The script automatically handles:
✓ YAML frontmatter
✓ Parent-child relationships
✓ Navigation ordering
✓ Clean URLs
```

### User: "Can I update all sections at once?"

**Your Response:**
```
Yes! Use the bulk update script:

.\Bulk-Update-All-Sections.ps1

This updates all 12 sections:
✓ Java Fundamentals (11 topics)
✓ Spring
✓ Distributed Systems
✓ Databases
✓ Messaging & Streaming
✓ Networking & HTTP
✓ OS & Systems
✓ System Design
✓ DSA
✓ Software Design
✓ Cloud & Infrastructure
✓ DevOps & SDLC

Then commit and push normally.
```

---

## What NOT to Do

❌ **Don't** manually add frontmatter to files  
❌ **Don't** ask me to add YAML frontmatter details  
❌ **Don't** use non-standard file naming  
❌ **Don't** use single or double-digit numbers (use 001, 002, etc.)  
❌ **Don't** push files without running automation script  

---

## What TO Do

✅ **Do** use proper file naming: `☕ 001 — Title.md`  
✅ **Do** run the automation script after creating files  
✅ **Do** commit files after automation completes  
✅ **Do** use the filename to set nav_order (numbers in filename)  
✅ **Do** test locally if possible before pushing  

---


