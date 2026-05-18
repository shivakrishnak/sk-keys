---
id: SEC-041
title: "Security Code Review Checklist"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-012, SEC-013, SEC-014, SEC-017, SEC-018, SEC-019, SEC-020, SEC-028, SEC-030, SEC-032, SEC-033, SEC-034, SEC-035, SEC-036, SEC-040
used_by: SEC-067, SEC-070, SEC-071
related: SEC-012, SEC-013, SEC-014, SEC-017, SEC-018, SEC-019, SEC-020, SEC-032, SEC-033, SEC-034, SEC-035, SEC-036, SEC-040, SEC-067, SEC-070, SEC-071
tags:
  - security
  - code-review
  - checklist
  - sast
  - secure-coding
  - owasp
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/sec/security-code-review-checklist/
---

⚡ TL;DR - Security code review is a targeted analysis of code
looking for vulnerability patterns, not just logic correctness.
It extends regular code review with a specific lens: "how
could an attacker abuse this?" The 10 highest-value areas to
check in every security-relevant PR:

**The Security Code Review Top 10:**
1. Input validation: is user input validated before use?
2. Output encoding: is data encoded for the context (HTML/JS/SQL)?
3. SQL: parameterized queries? Any string concatenation into queries?
4. Authentication: checked on every sensitive endpoint?
5. Authorization: object-level check (not just route-level)?
6. Secrets: any hardcoded credentials, API keys, passwords?
7. Cryptography: bcrypt for passwords? SHA-256 used where slow hash needed?
8. Session/cookies: HttpOnly + Secure + SameSite on session cookies?
9. Error handling: do errors expose stack traces, file paths, user data?
10. Dependencies: new library added? Check with `npm audit` / `snyk test`.

---

| #041 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | XSS, CSRF, Authentication, Crypto, Input Validation, JWT, CORS, SQL Injection, XSS Prevention, CSRF Prevention, bcrypt, Secrets Management, API Security | |
| **Used by:** | Business Logic, SAST, DevSecOps | |
| **Related:** | SAST, Secure Coding Practices, OWASP ZAP, DevSecOps | |

---

### 🔥 The Problem This Solves

**SECURITY REVIEWS HAPPEN TOO LATE OR NOT AT ALL:**
Security team reviews happen after development is complete.
Findings require expensive rework. Many teams skip formal
security review for internal tools or small features. The fix:
every developer performs a basic security review on every PR
they write or review. Not a full penetration test - a focused
checklist of the most common, highest-impact vulnerability patterns.
A 5-minute security check per PR prevents the majority of
real-world vulnerabilities before they merge.

**COMMON CODE REVIEW BLIND SPOTS:**
Developers reviewing code focus on: does it work? Is it readable?
Is it maintainable? Security adds a fourth lens: is it secure?
This lens catches things the first three miss:
- User input going directly into a query (working but injectable)
- A session cookie set without HttpOnly (works but stealable via XSS)
- A hardcoded API key (works but exposes credentials)
- An authorization check on the route but not on the specific object (works but allows IDOR)
These patterns are easy to miss without a security-specific checklist.

---

### 📘 Textbook Definition

**Security Code Review:** A manual or automated review of
source code to identify security vulnerabilities, insecure
patterns, and violation of security best practices.

**Complementary to SAST:** SAST (Static Application Security
Testing) automates pattern detection. Manual security review
adds: business logic flaws, context-specific authorization
issues, and architectural security concerns that automated
tools cannot detect. SAST catches "SQL string concatenation."
Manual review catches "this endpoint should require admin role
but only requires authentication."

**OWASP Code Review Guide:** The OWASP Code Review Guide
(owasp.org/www-project-code-review-guide/) is the reference.
Covers: scope, approach, prioritization, per-language patterns.

**Threat-Driven Review:** For each code change, ask:
"What does this code trust? What could an attacker provide
as input? What could an attacker do with the output?"
Trust boundaries are the priority review areas.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Check every PR for: unsanitized input, missing auth/authz,
hardcoded secrets, wrong crypto, missing cookie attributes,
and information leakage in errors. A 10-point checklist
catches 80% of real vulnerabilities before merge.

**One analogy:**
> Security code review is like a building inspector checking
> a new room addition. The contractor builds a working room
> (code that works). The inspector specifically looks for
> code violations that won't affect function but create risk:
> wrong wire gauge (weak crypto), no smoke detector (missing auth),
> missing firewall material between units (no authorization).
> The addition works perfectly without these - but they create
> unacceptable safety risk. Security review is the systematic
> application of safety checklists to code that works but
> may be dangerous.

---

### 🔩 First Principles Explanation

**The trust boundary concept for code review:**

```
TRUST BOUNDARIES IN A TYPICAL WEB APPLICATION:

Untrusted (attacker-controlled input):
  - HTTP request body, query params, path params, headers
  - Uploaded files (name, content, type)
  - Cookie values (despite HttpOnly: server still processes them)
  - Database values if populated from user input (second-order)
  - Third-party webhook payloads
  - Message queue messages (producer may be compromised)

Trusted:
  - Server configuration (from secrets manager)
  - Database values if populated from server-generated data
  - Signed/verified JWT claims (after signature verification)
  - Constants defined in server code

Trust boundary = any place where untrusted input crosses into trusted processing.

REVIEW CHECKLIST BY TRUST BOUNDARY:

TRUST BOUNDARY 1: HTTP Input → Application
  □ Input validated before use?
    - Type validation (int, not arbitrary string)
    - Range validation (age 0-150, not -1 or 999999)
    - Length limits (name max 255 chars, not unbounded)
    - Allowlist for enumerated values (status in [active, inactive])
  □ File upload: extension + MIME type + content validation?
    - Whitelist extensions (.pdf, .png, .jpg)
    - Validate actual content (magic bytes), not just extension
    - Store in non-executable location (not web root)
    - Rename file (don't trust user-provided filename)

TRUST BOUNDARY 2: Application → Database
  □ SQL queries use parameterized queries or ORM?
    BAD: f"SELECT * FROM users WHERE name='{name}'"
    GOOD: db.execute("SELECT * FROM users WHERE name = %s", (name,))
  □ No dynamic column/table names from user input?
    (Cannot parameterize - requires allowlist)
  □ Stored procedure calls: are inputs parameterized?
  □ ORM: any .raw() or .execute() with string format?

TRUST BOUNDARY 3: Application → HTML Page
  □ User data encoded for context (HTML, attribute, JS, URL)?
  □ Template engine auto-escaping enabled?
  □ No | safe, raw(), or dangerouslySetInnerHTML with user data?
  □ DOMPurify used if user HTML must render?

TRUST BOUNDARY 4: Application → Other Systems
  □ User-controlled URLs validated before server-side fetch?
    (SSRF: validate scheme, allowlist hosts or domains)
  □ User-controlled XML parsed safely?
    (XXE: disable external entities in XML parser)
  □ User-controlled paths used in file system access?
    (Path traversal: os.path.realpath + check prefix)
```

---

### 🧪 Thought Experiment

**SCENARIO: Security review of a file upload feature**

```
FILE UPLOAD CODE (first draft):

def upload_profile_photo(file, user_id):
    # Save file with original filename
    filename = file.filename
    path = f"/var/www/app/uploads/{filename}"
    with open(path, 'wb') as f:
        f.write(file.read())
    
    # Save path to database
    db.update_user(user_id, photo_path=path)
    return {"path": f"/uploads/{filename}"}

SECURITY REVIEW FINDINGS:

Finding 1: Arbitrary file path via filename
  file.filename = "../../etc/cron.d/backdoor"
  path = "/var/www/app/uploads/../../etc/cron.d/backdoor"
  = "/etc/cron.d/backdoor"
  Attacker writes to system cron directory.
  
  Fix: os.path.basename(file.filename) to strip path separators.
    Then combine with fixed upload directory.
    os.path.realpath(path) and verify it starts with upload_dir.

Finding 2: No file type validation
  file.filename = "shell.php" (webshell)
  If uploaded to web root: directly executable via browser.
  
  Fix: Extension allowlist: if not filename.endswith(('.jpg','.png','.gif')):
         return 400
    AND check magic bytes (first bytes of file content):
         imghdr.what(file) or python-magic for MIME type
    AND: rename file to random UUID (don't trust user filename)
         server_filename = f"{uuid.uuid4()}.{allowed_ext}"

Finding 3: No file size limit
  Attacker uploads 10GB file. Server disk fills up. DoS.
  
  Fix: check content-length header and reject > MAX_SIZE.
    Also: enforce in web server config (client_max_body_size in nginx).

Finding 4: Upload directory in web root
  /var/www/app/uploads/ is served by web server.
  Uploaded files are accessible as HTTP resources.
  PHP/CGI webshells become executable.
  
  Fix: store uploads OUTSIDE web root (/var/uploads/ not /var/www/uploads/).
    Serve via application endpoint that reads file content:
    GET /api/photos/{photo_id} → read file, return with Content-Type.
    Application controls access (authentication + authorization).
    Files cannot be directly fetched by URL.

Finding 5: No authorization check
  Any user can overwrite any user's photo
  (user_id is presumably from the request, not the JWT).
  
  Fix: use user_id from authenticated session/JWT,
    not from request body.

REVIEWED CODE:
def upload_profile_photo(file, current_user):
    # Validate file type by extension AND magic bytes
    original_name = secure_filename(file.filename)  # Sanitize
    ext = original_name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "File type not allowed")
    
    mime = magic.from_buffer(file.read(2048), mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "File content type not allowed")
    file.seek(0)
    
    # Check file size
    content = file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")
    
    # Save with UUID filename (not user-provided name)
    server_filename = f"{uuid.uuid4()}.{ext}"
    upload_path = UPLOAD_DIR / server_filename  # Outside web root
    
    # Validate path (path traversal prevention)
    real_path = upload_path.resolve()
    if not str(real_path).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(400, "Invalid path")
    
    real_path.write_bytes(content)
    
    # Use current_user.id from JWT (not request body)
    db.update_user(current_user.id, photo_filename=server_filename)
    return {"photo_url": f"/api/photos/{server_filename}"}
```

---

### 🧠 Mental Model / Analogy

> Security code review is like quality control inspection at
> a factory. Normal code review = functional testing: does the
> product work? Security review = safety testing: could the
> product harm users? A knife that cuts food (works) but has
> no guard (unsafe). A toy that functions correctly but has
> small parts that children can swallow (unsafe). The product
> passes functional testing but fails safety testing.
> Security reviewers are trained to see the "small parts"
> (injection points, missing auth, leaked credentials) that
> developers focused on functionality miss. The checklist
> is the safety testing standard: specific, repeatable,
> doesn't rely on the reviewer to remember every possible hazard.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When reviewing code, there are a specific set of security
problems that are easy to miss if you're only checking
whether the code works. A security checklist reminds reviewers
to look for: dangerous patterns like SQL string concatenation,
missing password protection on pages, hardcoded passwords,
and sending too much data back to users. Five minutes with
a checklist on every PR prevents most common vulnerabilities.

**Level 2 - How to use it (junior developer):**
For every PR you write or review: run through the top-10
checklist mentally. For SQL: look for any `f"..."` or `+`
string concatenation involving request parameters going into
queries. For auth: find every route and ask "what happens if
this is called without a valid token?" For secrets: search
the diff for words like "password", "key", "token", "secret"
in assignments. For cookies: find every Set-Cookie call and
check for HttpOnly, Secure, SameSite attributes. For errors:
look at exception handlers and ensure no stack traces reach responses.

**Level 3 - How it works (mid-level engineer):**
Threat-driven review: for each function, identify what it
receives (input) and what it produces (output). Ask: "if an
attacker controls the input, what's the worst they can do?"
Trust boundary analysis: mark where user-controlled data enters
the application (HTTP input), follow it through the code,
and check every point where it influences: database queries,
file system access, HTML output, HTTP redirects, external API calls,
shell commands, XML/YAML parsing. SAST tools automate the
pattern-matching part; human reviewers add: authorization logic,
business rules, and architectural flaws.

**Level 4 - Why it was designed this way (senior/staff):**
The cost of fixing a vulnerability scales with discovery stage:
$1 in code review, $10 in QA, $100 in staging, $1000+ in
production (IBM Systems Science Institute study). Security
reviews at the PR stage are the cheapest possible intervention.
The challenge: security knowledge is not uniformly distributed
across development teams. Checklists standardize the minimum
viable security check to the level of the least security-aware
developer. Senior engineers with security knowledge can focus
on architectural and business logic issues; the checklist
handles the mechanical vulnerability patterns.

**Level 5 - Mastery (distinguished engineer):**
Beyond pattern-matching: business logic security review
requires understanding what the application is SUPPOSED to do
and looking for ways it could be manipulated to do something
it SHOULDN'T. Examples: can a free trial user activate premium
features by replaying a subscription webhook? Can an order's
price be changed between cart and checkout? Can a user's
status be changed via a race condition? These require domain
knowledge and cannot be automated. Threat modeling during
design (STRIDE, attack trees) generates a security requirements
list that the code review validates against. The most mature
security review process is: (1) threat model at design phase,
(2) security requirements in acceptance criteria, (3) automated
SAST in CI/CD, (4) developer checklist on every PR, (5) periodic
deep-dive security review of high-risk features.

---

### ⚙️ How It Works (Mechanism)

**Security review workflow for a typical PR:**

```
SECURITY REVIEW WORKFLOW:

1. SCOPE: What changed?
   git diff main...feature-branch --stat
   Focus review time on: new API endpoints, auth changes,
     database queries, file handling, crypto, external calls.

2. AUTOMATED SCAN (run before manual review):
   sast_result = run_semgrep("--config=p/owasp-top-ten .")
   dependency_scan = run_snyk("test")
   Review results - triages obvious findings before human review.

3. MANUAL REVIEW - by category:

   INJECTION:
   □ Search: 'f"', '+', 'format(' near 'query', 'execute', 'cursor'
   □ Search: 'os.system(', 'subprocess.run(' near user input
   □ Search: any path from os.path near request parameters
   
   AUTHENTICATION:
   □ Find: new routes/endpoints
   □ Check: each has @login_required decorator or equivalent
   □ Check: there's no authentication bypass condition
   
   AUTHORIZATION:
   □ Find: any .filter(id=), .get(id=), resource lookup by ID
   □ Check: is there an ownership/permission check after the lookup?
   
   SENSITIVE DATA:
   □ Search: 'password', 'secret', 'key', 'token' in assignments
   □ Check: no literal values (only env vars or secrets manager refs)
   □ Check: logging statements don't log sensitive fields
   
   CRYPTO:
   □ Find: any password hashing → should be bcrypt/argon2
   □ Find: any random number generation → should use secrets module
   □ Find: any encryption → should use established library (cryptography)
   
   ERROR HANDLING:
   □ Find: exception handlers
   □ Check: return generic message to client (not exception details)
   □ Check: log full exception server-side (for debugging)

4. FINDINGS: Document in PR comments with:
   - Location (file:line)
   - Vulnerability type (SQL injection, missing auth)
   - Risk (what an attacker could do)
   - Fix (concrete code change)

5. DISPOSITION:
   - Block: Critical/High findings → must fix before merge
   - Comment: Medium → fix or document accepted risk
   - Suggest: Low/Informational → address in follow-up
```

---

### 💻 Code Example

**Security review checklist applied to Python code:**

```python
# ============= CODE TO REVIEW =============

import sqlite3
import logging
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
db = sqlite3.connect('app.db')

@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    # REVIEW ITEM 1: String formatting into SQL
    # FINDING: SQL INJECTION
    cursor = db.execute(
        f"SELECT * FROM users WHERE id = {user_id}"  # BAD
    )
    user = cursor.fetchone()
    
    # REVIEW ITEM 2: Authorization check missing
    # FINDING: BOLA/IDOR - no ownership check
    return jsonify(user)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # REVIEW ITEM 3: User-controlled filename in path
    # FINDING: Path traversal
    path = os.path.join('/tmp/uploads', file.filename)  # BAD
    file.save(path)
    return "OK"

@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    stored_hash = get_stored_hash(request.form.get('username'))
    
    # REVIEW ITEM 4: Timing-safe comparison
    # FINDING: Timing oracle (minor)
    if sha256(password) == stored_hash:  # BAD: fast hash + == comparison
        set_session(request.form.get('username'))
    
    return redirect('/')

@app.errorhandler(Exception)
def handle_error(e):
    # REVIEW ITEM 5: Stack trace in response
    # FINDING: Information disclosure
    logging.exception(e)
    return str(e), 500  # BAD: returns exception message to client

# ============= FIXED CODE =============

@app.route('/user/<int:user_id>/profile')  # int: type coercion
def get_profile_fixed(user_id):
    # FIX 1: Parameterized query
    cursor = db.execute(
        "SELECT id, name, email FROM users WHERE id = ?",  # GOOD
        (user_id,)
    )
    user = cursor.fetchone()
    if not user:
        return 404
    
    # FIX 2: Authorization check
    current_user = get_current_user_from_session()
    if not current_user or current_user['id'] != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    
    # Only return needed fields (not *)
    return jsonify({'id': user['id'], 'name': user['name']})

@app.route('/upload', methods=['POST'])
def upload_fixed():
    file = request.files['file']
    # FIX 3: Sanitize filename, use random name
    from werkzeug.utils import secure_filename
    import uuid
    
    # Allowlist extensions only
    ext = secure_filename(file.filename).rsplit('.', 1)[-1].lower()
    if ext not in ['jpg', 'png', 'gif']:
        return 'Invalid file type', 400
    
    # Use random filename (not user-provided)
    safe_filename = f"{uuid.uuid4()}.{ext}"
    upload_dir = '/tmp/uploads'
    path = os.path.join(upload_dir, safe_filename)
    
    # Verify path is within upload directory
    if not os.path.realpath(path).startswith(
        os.path.realpath(upload_dir)
    ):
        return 'Invalid path', 400
    
    file.save(path)
    return "OK"

@app.errorhandler(Exception)
def handle_error_fixed(e):
    # FIX 5: Log server-side, return generic message to client
    logging.exception(e)  # Full details in server log
    return jsonify({'error': 'Internal server error'}), 500
    # Client sees: generic message (no stack trace, no paths)
```

---

### ⚖️ Comparison Table

| Review Method | What It Finds | What It Misses | Time |
|:---|:---|:---|:---|
| **SAST (automated)** | Known vulnerability patterns (SQL injection, XSS sinks, insecure functions) | Business logic flaws, authorization context, architectural issues | Seconds |
| **Developer checklist** | Common patterns + context-specific auth/authz | Complex business logic, novel vulnerability classes | 5-15 min/PR |
| **Peer security review** | Architectural flaws, business logic, missed threat model | Same-team blind spots | 30-60 min/feature |
| **Penetration test** | Runtime vulnerabilities, interaction effects, real-world exploitability | Can't cover all code paths | Days/feature area |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| SAST is sufficient - no need for manual security review | SAST has both false positive rates (noise that obscures real findings) and false negative rates (misses business logic flaws, authorization issues, and contextual vulnerabilities). SAST finds: "string concatenation into SQL query." It cannot find: "this admin endpoint is accessible to regular users" - because determining that requires understanding the application's intended authorization model. Manual review and SAST are complementary, not alternatives. Combine both for maximum coverage. |
| Security review slows down development | A 5-10 minute security checklist on a PR adds negligible time compared to the cost of remediating a production security incident. The average cost of a data breach (IBM Cost of Data Breach Report): $4.45 million in 2023. A security check that prevents one vulnerability per year is easily justified. Developer resistance to security review usually stems from: unclear checklists (make them specific), false positive noise from SAST (tune the tool), and security being perceived as gatekeeping (frame it as a service). |

---

### 🚨 Failure Modes & Diagnosis

**Security review anti-patterns:**

```
ANTI-PATTERN 1: Rubber-stamping security review
  Symptom: Security checklist is on the PR template,
    but reviewers approve without checking.
  Detection: Track time between PR creation and approval.
    If reviews are approved in < 5 minutes with no security
    comments → rubber-stamping is occurring.
  Fix: Checklist items require explicit check marks or comments.
    Security items cannot be skipped without documented reason.

ANTI-PATTERN 2: Security review as gatekeeping (not collaboration)
  Symptom: Security team finds vulnerabilities and sends back
    with "this is insecure, fix it." No guidance.
  Effect: Developer adversarial relationship with security.
    Findings get closed without fixing.
  Fix: Security findings include: what is wrong, why it matters,
    and concrete code showing the fix. Collaboration, not judgment.

ANTI-PATTERN 3: Only reviewing new code, not modified code
  Symptom: Only the diff is reviewed. Pre-existing code that
    the new code interacts with (calls, depends on) is ignored.
  Example: New code calls get_user(user_id) - not checking
    that get_user has an auth check inside it.
  Fix: Review callee functions for new feature code.
    Trace data flow from input to all affected operations.

SECURITY REVIEW METRICS:
  Track:
  - Vulnerabilities found in review vs production
    (review-to-production ratio: want high review, low production)
  - Type of findings (repeated injection → training needed)
  - Time to fix security review findings
    (> 1 sprint → team is deprioritizing security)
  - SAST false positive rate (>50% → tune the tool)
```

---

### 🔗 Related Keywords

**Prerequisites:**
- All major vulnerability classes (XSS, SQLI, CSRF, etc.) from earlier entries

**Builds on this:**
- `SAST` - automated complement to manual review
- `Business Logic Vulnerabilities` - beyond checklist items
- `DevSecOps Pipeline Design` - where review fits in the pipeline

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INPUT        │ Validated? Type? Range? Length? Allowlist?│
│              │ SQL: parameterized queries ALWAYS         │
├──────────────┼───────────────────────────────────────────┤
│ OUTPUT       │ HTML context: auto-escaped or encoded?    │
│              │ User HTML: DOMPurify sanitized?           │
├──────────────┼───────────────────────────────────────────┤
│ AUTH/AUTHZ   │ Every endpoint: auth check?               │
│              │ Every resource: ownership check (BOLA)?   │
├──────────────┼───────────────────────────────────────────┤
│ SECRETS      │ No hardcoded credentials (grep 'key=',    │
│              │ 'password=', 'secret=', 'token=')         │
├──────────────┼───────────────────────────────────────────┤
│ ERRORS       │ Generic to client, full detail in logs    │
│              │ No paths, stack traces, user data exposed │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Trust boundaries are the key review targets."
Security problems occur at boundaries where data crosses
from less-trusted to more-trusted systems. HTTP input to
database (SQL injection). User-controlled HTML to browser
(XSS). User-supplied path to filesystem (path traversal).
User input to shell command (command injection). User-controlled
URL to server HTTP client (SSRF). Map the trust boundaries
in your code. Every crossing from untrusted to trusted is
a potential injection point. The security review checklist
is essentially: visit every trust boundary and verify the
crossing is safe.

---

### 💡 The Surprising Truth

The OWASP Top 10 has existed since 2003. The specific
vulnerabilities change slightly each edition. But injection
(SQL, command) and broken access control have been in EVERY
edition. Twenty years of security training, conference talks,
OWASP guides, and security tools - and the same two vulnerability
classes remain the top issues. This persistence suggests:
the problem isn't lack of knowledge about WHAT to fix, but
lack of systematic application of that knowledge during
development. Developers who know SQL injection exists still
write SQL injection vulnerabilities when they're in a hurry.
Checklists work because they create systematic prompts at
the point where code is written - not relied on memory
or vigilance. Aviation uses checklists not because pilots
don't know flight procedures, but because under cognitive
load (time pressure, complexity), memory fails. Code review
checklists serve the same purpose.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **REVIEW** a PR and identify at least SQL injection,
   missing authorization, or hardcoded credentials using
   the checklist without prompting.
2. **EXPLAIN** why each item on the top-10 checklist matters
   with a concrete attack scenario for each.
3. **CONFIGURE** semgrep or similar SAST tool to run on PRs
   and interpret its findings.
4. **DOCUMENT** a security finding in a PR comment with:
   vulnerability type, attack scenario, and concrete fix.

---

### 🎯 Interview Deep-Dive

**Q: How do you conduct a security code review?
What do you look for first?**

*Why they ask:* Tests whether the candidate has a systematic
security approach or just "looks for bugs generally." The
distinction matters: systematic security review is teachable
and repeatable; ad-hoc review misses categories.

*Strong answer includes:*
- Start with scope: what does this code touch? New API endpoints,
  auth changes, database queries, file handling get priority focus.
- Trust boundary analysis: follow user-controlled input through
  the code. Any point where it influences: queries, file paths,
  HTML output, external calls, shell commands - check that crossing.
- Top priority items: SQL injection (any string formatting into queries),
  missing authorization (object-level: does the user own this resource),
  hardcoded credentials (grep for 'password=', 'key=', 'token=' literal values).
- Complementary: run SAST (semgrep, Snyk Code) before manual review.
  Automated tools handle the mechanical patterns; manual review
  handles business logic and authorization context.
- Error handling: check that exceptions return generic messages
  to clients (not stack traces or internal paths).
- Candidate demonstrates pattern recognition by naming specific
  antipatterns (f-string in SQL, == comparison on session cookies,
  os.path.join with user input) rather than vague "check for security issues."