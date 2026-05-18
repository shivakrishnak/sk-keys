---
id: SEC-042
title: "Error Handling and Information Disclosure"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: ★★☆
depends_on: SEC-014, SEC-016, SEC-020
used_by: SEC-041, SEC-063, SEC-067
related: SEC-014, SEC-016, SEC-020, SEC-041, SEC-063, SEC-067
tags:
  - security
  - error-handling
  - information-disclosure
  - stack-traces
  - debug-mode
  - owasp
status: complete
version: 4
layout: default
parent: "Security"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/sec/error-handling-and-information-disclosure/
---

⚡ TL;DR - Error handling is a security concern because error
messages reveal information about the system that helps attackers.
A stack trace in an API response reveals: framework version,
file paths, class names, library structure, and sometimes data.
An attacker uses this to target known vulnerabilities in
identified versions.

**The rule: different error messages for client vs server.**
- **Client response:** Generic, unhelpful to attacker. "An error occurred."
  "Request failed." "Invalid input." Never: stack traces, file paths,
  database errors, version information.
- **Server logs:** Full detail. Exception message, stack trace, request
  context, user ID. Everything needed for debugging.

**Two common patterns that expose information:**
1. Django/Flask `DEBUG=True` in production: full stack traces in browser
2. Spring Boot Actuator exposed without auth: /actuator/env shows all config

---

| #042 | Category: Security | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Security Fundamentals, Authentication, Security Headers | |
| **Used by:** | Security Code Review, Business Logic, DevSecOps | |
| **Related:** | Security Code Review, Security Monitoring, OWASP Top 10 | |

---

### 🔥 The Problem This Solves

**WHAT AN ATTACKER LEARNS FROM ERROR MESSAGES:**
When a web application exposes detailed errors:

```
TypeError at /api/user/profile
Django Version: 4.1.2
Python Version: 3.10.5

Exception Value:
'NoneType' object has no attribute 'email'

Exception Location:
/home/ubuntu/app/views.py, line 47, in get_profile

Local variables:
user = None
user_id = "../../etc/passwd"  (path traversal attempt!)

Traceback:
  File "/usr/local/lib/python3.10/site-packages/django/core/handlers/base.py", line 119
  File "/home/ubuntu/app/views.py", line 47
```

From this single error response, an attacker learns:
- Django version 4.1.2 → check for known CVEs
- Python 3.10.5 → check for known CVEs
- Application root: /home/ubuntu/app/ → useful for LFI/RFI
- Full file paths of framework and application code
- Variable values at time of error (including the attack payload)
- The path traversal attempt didn't work but wasn't detected

This reconnaissance accelerates the attacker's next steps.

**VERBOSE SQL ERRORS IN PRODUCTION:**
```
ProgrammingError: (1064, "You have an error in your SQL syntax; 
check the manual that corresponds to your MySQL server version 
for the right syntax to use near ''1'' LIMIT 1' at line 1")
```
This confirms: MySQL database, SQL injection is occurring,
and reveals the query structure. The attacker now knows to
target MySQL-specific injection techniques.

---

### 📘 Textbook Definition

**Information Disclosure:** Unintentional exposure of sensitive
information to parties that should not have access to it.
In the context of error handling: revealing implementation
details, server configuration, file paths, or data through
error responses.

**OWASP Top 10 - A05 Security Misconfiguration:** Covers
debug modes enabled, unnecessary features enabled, default
accounts, verbose error messages. Stack traces in production
is explicitly a security misconfiguration.

**Types of Information Disclosure via Errors:**
- **Stack traces:** Class names, file paths, line numbers,
  framework versions, library versions
- **Database errors:** DBMS type and version, table/column names,
  query fragments
- **Path disclosure:** Server file system paths (Windows: C:\\inetpub\\;
  Linux: /var/www/app/)
- **User enumeration:** Different error messages for "user not found"
  vs "wrong password" reveal whether a username exists
- **Timing information:** Response time differences reveal
  presence/absence of records (timing oracle)
- **Version information:** HTTP headers (Server: Apache/2.4.51),
  X-Powered-By header, HTML comments, robots.txt

**User Enumeration Distinction:**
`"Username or password is incorrect"` - safe (doesn't reveal which)
vs `"No account exists with this email address"` - reveals
that the attacker's email guess was wrong (helps enumerate valid emails).
vs `"Incorrect password"` - confirms the email is registered.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Never show stack traces, database errors, file paths, or
framework details to users. Log everything server-side,
show generic error messages client-side. Disable debug mode
in production.

**One analogy:**
> Verbose error messages are like a locksmith who, when you
> try the wrong key, tells you: "That key is too wide by 0.3mm,
> the third pin is also too high by 0.1mm, and the lock model
> is a Medeco Maxum with 6 pins." Instead of "that key doesn't
> work." The diagnostic detail is useful for the person with
> a legitimate key needing to make a copy. For a lockpicker:
> it's a roadmap for the exact modifications needed.
> Generic error = "key doesn't work." Verbose error = a technical
> guide to bypassing the specific lock.

---

### 🔩 First Principles Explanation

**The three information disclosure risk areas:**

```
RISK AREA 1: Debug/Development Mode in Production

DJANGO DEBUG=True in production:
  Every unhandled exception → full debug page in browser
  Debug page contains: settings.py content (shows DB credentials,
    SECRET_KEY, INSTALLED_APPS), full stack trace, request headers,
    POST data, cookies, local variables at each frame.
  
  Any unhandled exception from ANY code path exposes this.
  Attacker triggers exceptions by: sending unexpected input,
    requesting non-existent resources, sending malformed data.

SPRING BOOT ACTUATOR without authentication:
  Default endpoints accessible:
    GET /actuator/env   → ALL environment variables (inc. secrets!)
    GET /actuator/beans → All Spring beans (reveals framework structure)
    GET /actuator/health → Application status
    GET /actuator/info  → Application and version info
    GET /actuator/logfile → Application log file
    GET /actuator/heapdump → JVM heap dump (may contain credentials!)
  
  Attack: curl https://target.com/actuator/env | grep -i "password\|secret\|key"
    May find: spring.datasource.password, aws.access_key, jwt.secret

NODE.JS Express unhandled errors:
  Default error handler returns: { "error": "Internal Server Error" } (safe)
  BAD pattern: res.status(500).json({ error: err.message, stack: err.stack })
  GOOD pattern: res.status(500).json({ error: "Internal server error" })

RISK AREA 2: User Enumeration via Error Messages

LOGIN FORM:
  VULNERABLE: Two different messages
    "No account found with this email" → email not registered
    "Incorrect password" → email IS registered, wrong password
  
  Attack: enumerate email addresses by trying common emails.
    Emails that return "Incorrect password" are registered accounts.
    Use for credential stuffing with the email confirmed as valid.
  
  CORRECT: Same message regardless
    "Invalid username or password" (for BOTH cases)
  
  TIMING VULNERABILITY (subtle):
    Even with same message: if the server only computes bcrypt
    for existing users (fast path for non-existent user):
      Non-existent user: response in 5ms
      Existing user (wrong password): response in 300ms (bcrypt)
    Timing difference reveals user existence.
    
    Fix: ALWAYS compute bcrypt, even for non-existent users:
      def login(email, password):
        user = db.get_user_by_email(email)
        # Always compute bcrypt, even if user is None
        dummy_hash = DUMMY_HASH  # Precomputed at startup
        check_hash = user.password_hash if user else dummy_hash
        valid = bcrypt.checkpw(password.encode(), check_hash)
        if valid and user:
          return login_success(user)
        return login_failure()  # Same response regardless

RISK AREA 3: Server/Framework Version Disclosure via HTTP Headers

HTTP HEADERS THAT DISCLOSE VERSIONS:
  Server: Apache/2.4.51 (Ubuntu)    → Apache version + OS
  X-Powered-By: PHP/8.1.2          → PHP version
  X-Powered-By: Express            → Express framework
  X-AspNet-Version: 4.0.30319      → .NET version
  Via: 1.1 haproxy/2.4.2           → HAProxy version
  X-Generator: Drupal 9            → CMS + version

ATTACK USE: look up CVEs for the identified versions.
  Apache 2.4.51 → CVE-2021-41773, CVE-2021-42013 (path traversal)
  PHP 8.1.2 → check php-security-advisories
  Drupal 9.x → check drupal.org/security/advisories

FIX: Remove or genericize version-revealing headers
  Apache: ServerTokens Prod    (shows "Apache" not version)
  nginx: server_tokens off;   (removes Server: nginx/1.21 header)
  PHP: expose_php = Off        (in php.ini; removes X-Powered-By)
  Express: app.disable('x-powered-by');
  Spring Boot: server.server-header=  (empty in application.properties)
```

---

### 🧪 Thought Experiment

**SCENARIO: Securing error handling in a multi-tier application**

```
CONTEXT: 3-tier app: React SPA → FastAPI backend → PostgreSQL

CURRENT STATE (insecure):
  @app.exception_handler(Exception)
  async def global_exception_handler(request, exc):
      import traceback
      return JSONResponse(
          status_code=500,
          content={
              "error": str(exc),
              "traceback": traceback.format_exc(),
              "request_url": str(request.url),
          }
      )

WHAT AN ATTACKER SEES:
  Trigger: GET /api/users?sort='; DROP TABLE users; --
  Response (500):
  {
    "error": "column \"'; drop table users; --\" does not exist",
    "traceback": "sqlalchemy.exc.ProgrammingError\n  File \"/app/api/users.py\", line 34\n    .order_by(sort_column)",
    "request_url": "https://api.example.com/api/users?sort=..."
  }
  
  Attacker learns: PostgreSQL database, file path at line 34,
    query structure (order_by(sort_column)), SQL injection is occurring.
  Next step: systematic SQL injection at the sort parameter.

FIXED APPROACH:

  import logging
  import uuid
  from fastapi import Request
  from fastapi.responses import JSONResponse
  
  logger = logging.getLogger(__name__)
  
  @app.exception_handler(Exception)
  async def global_exception_handler(request: Request, exc: Exception):
      # Generate correlation ID for internal tracking
      error_id = str(uuid.uuid4())[:8]
      
      # Full details in server log (for debugging)
      logger.error(
          f"Unhandled exception [error_id={error_id}] "
          f"URL={request.url} method={request.method}",
          exc_info=True,  # Includes full traceback in log
          extra={
              "error_id": error_id,
              "url": str(request.url),
              "method": request.method,
              # Add user_id, request_id from context if available
          }
      )
      
      # Generic response to client
      return JSONResponse(
          status_code=500,
          content={
              "error": "Internal server error",
              "error_id": error_id,
              # error_id allows user to report the issue;
              # support can find the full log by this ID
              # Attacker gets nothing useful
          }
      )
  
  BENEFIT:
    Client response: {"error": "Internal server error", "error_id": "a3f9b2c1"}
    Attacker: no information about what went wrong or how to exploit it.
    User: can report error_id to support.
    Support: can find full logs by error_id.
    Developer: still has full debugging information in logs.
```

---

### 🧠 Mental Model / Analogy

> Error handling security is like hospital HIPAA compliance
> for diagnostic messages. When a doctor orders a test and
> it comes back abnormal: the doctor gets the full lab report
> (log: full detail for the authorized professional).
> The patient gets: "some values are elevated, we'll discuss
> treatment" (client: generic, actionable, no diagnostic detail).
> An unauthorized person calling the hospital asking about
> a patient gets: "I cannot confirm or deny whether that
> person is a patient here" (user enumeration protection).
> The information exists and is accessible to those who
> need it (logs for developers), but controlled disclosure
> prevents unauthorized parties from using diagnostic
> details as a roadmap for exploitation.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
When something goes wrong in your application, don't show
the technical details to the user. Show "something went wrong"
(or a friendly message). But make sure your own logs have
all the details so you can debug the problem. Same with
login: if the username or password is wrong, say exactly
that - don't say "username not found" (which tells attackers
which usernames exist).

**Level 2 - How to use it (junior developer):**
Django: `DEBUG = False` in production settings. Python: `logging.exception(e)` logs the full traceback to your log file; `return "Internal server error", 500` to the client. Spring Boot: `management.endpoints.web.exposure.include=health` (only expose health, not env/beans/logfile). Remove `X-Powered-By` header (Express: `app.disable('x-powered-by')`). For login: same error message for wrong username and wrong password. Use `hmac.compare_digest` (constant-time) for security-sensitive comparisons.

**Level 3 - How it works (mid-level engineer):**
Structured logging: log error events with correlation IDs, user IDs, request IDs. Correlate client-visible error IDs with server logs. Users report "error ID abc123"; support searches logs for that ID. Timing attacks on user enumeration: bcrypt is slow (~300ms). Even with same message: if the server skips bcrypt for non-existent users (fast path), response time reveals user existence. Always compute bcrypt, even for non-existent users (use a precomputed dummy hash). HTTP header hardening: nginx `server_tokens off`, Apache `ServerTokens Prod`, remove X-Powered-By. Web framework defaults are usually verbose.

**Level 4 - Why it was designed this way (senior/staff):**
The information security principle of "need to know" and
"minimum information disclosure" applies to error messages.
Developers need full diagnostic information; attackers should
receive the minimum needed to understand that an error occurred.
The challenge: developers in development environments see
full errors and become habituated to verbose messages.
Moving to production: verbose settings remain. This is a
configuration management problem: production configuration
must be explicitly hardened, not inherited from development.
Infrastructure-as-code with environment-specific configuration
management (separate production secrets, features, error verbosity).

**Level 5 - Mastery (distinguished engineer):**
Oracle attacks: beyond just error messages, any observable
difference between "success" and "failure" responses constitutes
an oracle that an attacker can use. Timing oracles, size oracles
(different response sizes for success vs failure), Boolean-based
blind SQL injection (error for TRUE vs FALSE conditions), and
out-of-band channels (server making DNS requests that reveal
data). Complete error handling security requires: same response
content, same response timing (constant-time operations),
same response size (padding if necessary), and same response
headers for equivalent security outcomes. This is the
"indistinguishability" principle: from an attacker's perspective,
all failure responses should be computationally indistinguishable.

---

### ⚙️ How It Works (Mechanism)

**Structured error logging and response pattern:**

```
ERROR HANDLING ARCHITECTURE:

UNHANDLED EXCEPTION FLOW:

  Exception occurs in application code
         │
         ▼
  Global exception handler
  (middleware/decorator)
         │
         ├─→ SERVER LOG:
         │     - Full exception + traceback
         │     - Request context: URL, method, user_id, IP
         │     - Correlation ID (UUID for tracking)
         │     - Timestamp
         │     - Environment (production, pod name)
         │
         └─→ CLIENT RESPONSE:
               - HTTP 500
               - JSON: {"error": "Internal server error", "error_id": "abc123"}
               - NO: stack trace, file paths, exception message,
                     library versions, DB error text

ERROR CLASSIFICATION:
  4xx (Client errors - expected, handle gracefully):
    400 Bad Request: Invalid input → log at WARNING, return validation errors
    401 Unauthorized: Not authenticated → no logging needed (expected)
    403 Forbidden: Not authorized → log at INFO (potential attack)
    404 Not Found: Resource not found → minimal logging
    429 Too Many Requests: Rate limited → log at INFO
  
  5xx (Server errors - unexpected, must log):
    500 Internal Server Error: Unhandled exception → log at ERROR with full trace
    502/503/504: Infrastructure errors → log at ERROR, check dependencies

PRODUCTION SETTINGS CHECKLIST:

  Django:
    DEBUG = False                   # No debug pages in browser
    ALLOWED_HOSTS = ['example.com'] # Strict host validation
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']  # From env, not code
  
  Spring Boot (application.properties):
    spring.profiles.active=prod
    management.endpoints.web.exposure.include=health
    management.endpoint.health.show-details=never
    server.error.include-stacktrace=never
    server.error.include-exception=false
    server.error.include-message=never
  
  Express/Node:
    app.disable('x-powered-by');
    app.use((err, req, res, next) => {
      console.error(err);  // Log to console/file
      res.status(500).json({ error: 'Internal server error' });
    });
  
  nginx:
    server_tokens off;
    # Custom error pages (not nginx default with version)
    error_page 404 /404.html;
    error_page 500 /500.html;
```

---

### 💻 Code Example

**Secure error handling across multiple languages:**

```python
# Python / FastAPI - Global exception handler

import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()
logger = logging.getLogger(__name__)

# Handle validation errors (client error - 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc):
    # Validation errors are NOT security-sensitive:
    # Returning details about WHAT was invalid helps legitimate users.
    # "Field 'email' must be a valid email address" is fine.
    # Just don't include request data in the response.
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}  # Schema errors: safe to return
    )

# Handle explicit HTTP exceptions (like 404, 403)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Known errors: return the intended status/detail
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Handle ALL other (unexpected) exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())[:8]
    
    # Full details in log (for developers)
    logger.error(
        "Unhandled exception",
        exc_info=True,  # Logs full traceback
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    # Generic response to client (no useful info for attacker)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_id": error_id  # Reference for support
        }
    )

# User enumeration prevention in login:
import hmac
import bcrypt

DUMMY_HASH = bcrypt.hashpw(b"dummy", bcrypt.gensalt(12))

async def login(username: str, password: str) -> bool:
    user = db.get_user_by_username(username)
    
    # ALWAYS compute bcrypt to prevent timing oracle
    stored_hash = user.password_hash if user else DUMMY_HASH
    password_valid = bcrypt.checkpw(
        password.encode('utf-8'),
        stored_hash
    )
    
    if password_valid and user:
        return True
    
    # Same error message whether user exists or not
    raise HTTPException(
        status_code=401,
        detail="Invalid username or password"  # Not "user not found"
    )
```

---

### ⚖️ Comparison Table

| Error Mode | Attacker Value | Developer Value | Correct For |
|:---|:---|:---|:---|
| **Stack trace in response** | Very high | High | Never in production |
| **Exception message in response** | Medium | Medium | Never in production |
| **Generic 500 + error_id** | None | High (via logs) | Production |
| **Different messages for user vs password errors** | High (user enumeration) | Low | Never |
| **Same message for all auth failures** | None | Acceptable | Production |
| **Full debug page (Django DEBUG=True)** | Extremely high | High | Development ONLY |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|:---|:---|
| Showing error details helps legitimate users troubleshoot | Legitimate users cannot diagnose stack traces or database errors - they're developers' tools. What legitimate users need is: (1) whether they made a mistake they can fix ("Invalid email format") or (2) to report the problem to support ("An error occurred, reference: abc123"). Stack traces and exception messages add no value for users and significant value for attackers. Structured error IDs give users the reference they need without exposing implementation. |
| Returning a different error for non-existent vs wrong-password is a UX improvement | From a UX perspective, "user not found" helps the user correct the username. But from a security perspective, it enables attackers to enumerate valid usernames. For low-security applications (public blogs), user enumeration may be acceptable. For high-security applications (banking, healthcare, enterprise), the security risk outweighs the UX benefit. The OWASP recommendation: use the same error message for all authentication failures. Provide password reset links to help legitimate users who aren't sure if they have an account. |

---

### 🚨 Failure Modes & Diagnosis

**Finding information disclosure vulnerabilities:**

```
TESTING FOR INFORMATION DISCLOSURE:

1. Trigger server errors intentionally:
   - Send malformed JSON: Content-Type: application/json, body: {invalid
   - Send oversized input: name=A*10000
   - Send unexpected types: age=not_a_number
   - Send path traversal in string fields: name=../../etc/passwd
   
   Response: Look for stack traces, file paths, exception messages.

2. Check HTTP response headers:
   curl -I https://example.com | grep -i "server\|x-powered-by\|x-aspnet\|x-generator"
   
   Flag: Server: Apache/2.4.51 (reveals version)
   Good: Server: Apache (no version)
   Best: Server header not present

3. Check debug endpoint exposure:
   curl https://example.com/actuator/env    # Spring Boot
   curl https://example.com/debug           # Various frameworks
   curl https://example.com/info            # Spring Boot
   curl https://example.com/__debug__       # Django debug toolbar
   Expected: 404 or 401 (not JSON with config/secrets)

4. Test user enumeration on login:
   Time the response for existing vs non-existing username:
   time curl -X POST /login -d "username=admin&password=wrong"
   time curl -X POST /login -d "username=notexist@test.com&password=wrong"
   
   Flag: significant timing difference (>100ms) between responses.

5. Check error message consistency:
   POST /login {"username": "realuser@test.com", "password": "wrong"}
   POST /login {"username": "notexist@test.com", "password": "wrong"}
   
   Flag: different response messages (reveals user existence)
   Good: identical response messages for both
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Security Headers` - X-Powered-By and Server header removal
- `Authentication Fundamentals` - user enumeration via login errors
- `Security Monitoring Basics` - where error logs go

**Builds on this:**
- `Security Code Review Checklist` - error handling as review item
- `Business Logic Vulnerabilities` - timing oracles as logic flaws

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ NEVER in     │ Stack traces, file paths, DB error text   │
│ response     │ Exception messages, version numbers       │
├──────────────┼───────────────────────────────────────────┤
│ ALWAYS in    │ Full trace, context, correlation ID       │
│ server logs  │ Everything needed for debugging           │
├──────────────┼───────────────────────────────────────────┤
│ CLIENT RESP  │ Generic message + error_id reference      │
│              │ Same message for all auth failures        │
├──────────────┼───────────────────────────────────────────┤
│ DISABLE      │ DEBUG=True, Actuator endpoints, verbose   │
│ PROD         │ Server headers revealing version          │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ Always compute bcrypt (don't short-circuit)│
│ ORACLE       │ Normalize response times for auth paths   │
└──────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Observability for you, opacity for attackers."
The goal is not to make debugging impossible - it's to ensure
debugging information is available to YOU but not to adversaries.
This requires asymmetric information access: full detail in
server logs (you have access), generic messages in responses
(attacker sees only that an error occurred). The same principle
applies to monitoring: your dashboards show request failure rates,
latency percentiles, error logs - but an attacker probing
your API should learn nothing useful from response timing,
response size variation, or error messages. Design observability
systems with this asymmetry: maximize developer/operator visibility
while minimizing attacker reconnaissance value.

---

### 💡 The Surprising Truth

In 2012, the Ruby on Rails framework had a critical vulnerability
(CVE-2013-0156) that allowed arbitrary code execution via
crafted XML payloads. The attacker payload was published
publicly with exploit code. Many organizations remained
vulnerable for weeks because they didn't know which version
of Rails they were running. Organizations that had suppressed
version information in HTTP headers were slightly harder to
identify as targets (required probing), giving them additional
time to patch. This is "security through obscurity" - not
a defense on its own, but a tactic that reduces attacker
efficiency when applied in addition to timely patching.
The lesson isn't "obscurity is sufficient" (it isn't), but
"every bit of friction in the attacker's reconnaissance
reduces the window of exploitation." Version disclosure
removal is trivially easy and provides some reduction in
targeted attack efficiency.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** a production web framework (Django, Spring Boot,
   Express) to disable debug mode, suppress version headers,
   and return generic error messages.
2. **IMPLEMENT** a global exception handler that logs full detail
   to server logs and returns only a generic message + error ID
   to the client.
3. **TEST** for information disclosure by triggering errors and
   checking whether stack traces appear in responses.
4. **PREVENT** user enumeration by using same error messages and
   constant-time comparisons in authentication flows.

---

### 🎯 Interview Deep-Dive

**Q: How should an application handle errors from a security perspective?
What's the risk of returning detailed error messages?**

*Why they ask:* Fundamental security hygiene question. Tests
whether the candidate understands that security applies to
error handling, not just business logic.

*Strong answer includes:*
- Two audiences for error information: developers (need full detail)
  and users/attackers (should get generic information only).
- Risk of detailed errors: reveals framework versions (CVE lookup),
  file paths (LFI/RFI attacks), database type and error (SQL injection
  confirmation), class names (framework structure). Attacker uses this
  as free reconnaissance.
- Solution: global exception handler logs full detail to server
  logs with correlation ID. Returns generic message + correlation ID
  to client. Developer can find full log by correlation ID.
  User can report the ID to support.
- Production settings: DEBUG=False (Django), server.error.include-stacktrace=never
  (Spring Boot), remove X-Powered-By headers.
- User enumeration: same error message for "user not found" and
  "wrong password." Constant-time comparison to prevent timing oracle
  even with identical messages.
- Spring Boot Actuator: restrict exposed endpoints to health only
  in production. The /actuator/env endpoint has exposed credentials
  in real-world incidents.