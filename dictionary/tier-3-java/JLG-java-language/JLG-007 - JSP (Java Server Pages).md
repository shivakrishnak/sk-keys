---
layout: default
title: "JSP (Java Server Pages)"
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 7
permalink: /java/jsp-java-server-pages/
id: JLG-007
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Servlet, HTML, Java EE / J2EE Overview
used_by: Spring Core, Java EE / J2EE Overview
related: Thymeleaf, FreeMarker, Java Servlet
tags:
  - java
  - jvm
  - intermediate
  - frontend
---

# JLG-007 - JSP (Java Server Pages)

⚡ TL;DR - JSP is a Java technology that lets you embed Java code inside HTML templates, compiled to Servlets at runtime by the container.

| #2101 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Java Servlet, HTML, Java EE / J2EE Overview | |
| **Used by:** | Spring Core, Java EE / J2EE Overview | |
| **Related:** | Thymeleaf, FreeMarker, Java Servlet | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Early Servlet-based web apps generated HTML by calling `out.println("<html><body>...")` hundreds of times in Java code. Changing a button label meant editing Java, recompiling, and redeploying. Designers couldn't touch the "HTML" because it was buried in Java strings.

**THE BREAKING POINT:**
Large web teams needed designers working on layout and developers working on logic simultaneously. Mixing both in Servlet `doGet()` methods was unmaintainable.

**THE INVENTION MOMENT:**
JSP inverted the model - start with HTML, embed Java where needed. The container compiles JSP to Servlet bytecode on first request. Designers own the `.jsp` file structure; developers own the Java logic within scriptlets or (better) tag libraries.

---

### 📘 Textbook Definition

JavaServer Pages (JSP) is a server-side view technology that allows embedding Java code and expression language inside HTML markup using special tags (`<% %>`, `<%= %>`, `<%! %>`). A JSP file is automatically compiled by the servlet container into a `HttpServlet` subclass the first time it is requested. JSP supports the Expression Language (EL), JSTL tag library, and custom tag libraries, enabling logic-free templates when combined with MVC patterns.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
HTML files with Java code fragments embedded inside, compiled to Servlets by the web container.

**One analogy:**
> JSP is like a mail-merge template. You write the letter layout (HTML) with placeholders (EL expressions) like `${user.name}`. The JSP engine fills in the real values from your data model when it renders.

**One insight:**
Modern Spring MVC recommends Thymeleaf or FreeMarker over JSP because JSP's compiled-Servlet approach makes it incompatible with embedded servlet containers (Spring Boot's default JAR packaging). Understanding JSP is essential for maintaining legacy enterprise applications.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A JSP is syntactic sugar over a Servlet - it compiles to a class extending `HttpJspBase`.
2. JSP mixes presentation (HTML) and logic (Java) in the same file.
3. The JSP lifecycle is: translate → compile → load → instantiate → `jspInit()` → `_jspService()` → `jspDestroy()`.

**DERIVED DESIGN:**
Because JSP compiles to a Servlet, it runs inside the same container with the same threading model. The `_jspService()` method is called per request. Static content becomes `out.write("...")` calls; expressions become `out.print(...)` calls.

**THE TRADE-OFFS:**
**Gain:** Familiar HTML-first authoring, automatic compilation, EL and JSTL for logic-free templates.
**Cost:** Difficult to unit test, mixes concerns if scriptlets are used, incompatible with embedded containers in JAR packaging.

---

### 🧪 Thought Experiment

**SETUP:**
You're building an online store product page. The Servlet fetches the product and puts it in request scope. The JSP renders it.

**WHAT HAPPENS WITHOUT JSP:**
```java
// In Servlet doGet():
out.println("<html><body>");
out.println("<h1>" + product.getName() + "</h1>");
out.println("<p>Price: $" + product.getPrice() + "</p>");
out.println("</body></html>");
```
Changing font, adding CSS class, restructuring layout - all require Java edits and recompilation.

**WHAT HAPPENS WITH JSP:**
```jsp
<html><body>
  <h1>${product.name}</h1>
  <p>Price: $${product.price}</p>
</body></html>
```
A designer can edit layout freely. The Java developer only touches the Servlet.

**THE INSIGHT:**
Separation of concerns in web development is not just about clean code - it's about enabling parallel work by developers and designers.

---

### 🧠 Mental Model / Analogy

> JSP is like a restaurant menu template. The menu layout (HTML) is fixed; the daily specials (Java data) are slotted into marked spaces (`${special.name}`). The kitchen (Servlet) prepares the data; the waiter (JSP engine) fills in the template and serves it.

- "Menu template" → `.jsp` file
- "Daily specials" → Java objects in request/session scope
- "Marked spaces" → EL expressions `${...}`
- "Waiter filling template" → JSP engine rendering
- "Kitchen" → Servlet business logic

Where this analogy breaks down: unlike a static menu, JSP can contain arbitrary logic in scriptlets, which breaks the separation - hence the recommendation to avoid scriptlets.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
JSP is a file that looks like HTML but has special Java placeholders. When someone visits the page, the server fills in the placeholders with real data and sends back pure HTML.

**Level 2 - How to use it (junior developer):**
Create `product.jsp`, use EL `${product.name}` to display data placed in request scope by a Servlet. Use JSTL `<c:forEach>` to loop over collections. Avoid raw Java scriptlets `<% %>` - they make JSPs untestable.

**Level 3 - How it works (mid-level engineer):**
First request to `product.jsp`: container calls the JSP compiler (Jasper in Tomcat), which translates the JSP to a Java source file (Servlet), compiles it to bytecode, loads the class, and calls `_jspService()`. Subsequent requests skip translation and compilation - the compiled Servlet handles them directly.

**Level 4 - Why it was designed this way (senior/staff):**
JSP was designed as a direct competitor to Microsoft's ASP (Active Server Pages), which embedded VBScript in HTML. Sun's approach compiled JSPs to Servlets, leveraging existing JVM performance and JIT optimization. The compile-once model avoids re-parsing overhead on every request - unlike PHP's default interpretation model.

---

### ⚙️ How It Works (Mechanism)

```
First Request to /product.jsp
         │
         ▼
┌─────────────────────────┐
│  JSP Container (Jasper) │
│  1. Translate .jsp       │
│     → product_jsp.java  │
│  2. Compile .java        │
│     → product_jsp.class │
│  3. Load & instantiate  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  _jspService(req, res)  │
│  Write HTML fragments   │
│  Evaluate EL exprs      │
│  Execute JSTL tags      │
└────────────┬────────────┘
             │
             ▼
       HTML Response
(Subsequent requests skip
 translate/compile steps)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
`Browser → HTTP GET → Servlet (sets model in request) → forward to JSP → JSP renders HTML → Response` ← YOU ARE HERE

**FAILURE PATH:**
JSP translation error → HTTP 500 with stack trace showing JSP line number. EL expression evaluates to `null` → renders as empty string (silent failure in EL). Scriptlet exception → `JspException` wraps original.

**WHAT CHANGES AT SCALE:**
At scale, JSP compilation on first deployment can cause latency spikes. Pre-compilation at build time (using `jspc` Maven plugin) eliminates cold-start translation overhead.

---

### 💻 Code Example

**BAD - Scriptlets mix logic and presentation:**
```jsp
<%
  List<Product> products = (List<Product>)
      request.getAttribute("products");
  for (Product p : products) {
%>
  <div><%= p.getName() %> - $<%= p.getPrice() %></div>
<% } %>
```

**GOOD - JSTL + EL, no Java in JSP:**
```jsp
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<c:forEach var="product" items="${products}">
  <div>
    <c:out value="${product.name}"/> -
    $<c:out value="${product.price}"/>
  </div>
</c:forEach>
```

```java
// Servlet sets model, forwards to JSP
@WebServlet("/products")
public class ProductServlet extends HttpServlet {
    protected void doGet(HttpServletRequest req,
                         HttpServletResponse res)
            throws ServletException, IOException {
        List<Product> products = productService.findAll();
        req.setAttribute("products", products);
        req.getRequestDispatcher("/WEB-INF/views/products.jsp")
           .forward(req, res);
    }
}
```

---

### ⚖️ Comparison Table

| Feature | JSP | Thymeleaf | FreeMarker |
|---|---|---|---|
| Syntax | HTML + Java tags | Natural HTML templates | Template directives |
| Spring Boot support | Limited (WAR only) | Full (JAR + WAR) | Full |
| Testability | Poor | Excellent | Good |
| Designer-friendly | Moderate | Excellent | Good |
| Performance | Fast (compiled) | Fast | Fast |
| Legacy prevalence | High | Growing | Common |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JSP is interpreted like PHP" | JSP is compiled to a Servlet on first access; subsequent requests hit bytecode. |
| "JSP and Thymeleaf are equivalent" | Thymeleaf works as natural HTML; JSP requires a container to render. |
| "Scriptlets are fine if limited" | Even one scriptlet creates untestable, unmaintainable code - use EL/JSTL always. |
| "JSP is obsolete" | Millions of enterprise apps use it; understanding JSP is essential for maintenance. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: JSP not found after packaging**
- **Symptom:** HTTP 404 for JSP paths after building JAR with Spring Boot.
- **Root Cause:** Spring Boot's embedded Tomcat doesn't support JSP in JAR packaging.
- **Diagnostic:**
```bash
# Check packaging in pom.xml
grep -A2 '<packaging>' pom.xml
# Should be <packaging>war</packaging> for JSP support
```
- **Fix:** Change to WAR packaging or migrate to Thymeleaf.
- **Prevention:** Use Thymeleaf for all new Spring Boot projects.

**Failure Mode 2: EL expressions print literally**
- **Symptom:** Page shows `${product.name}` as text rather than the product name.
- **Root Cause:** Missing `<%@ page isELIgnored="false" %>` or wrong JSP version in `web.xml`.
- **Diagnostic:**
```xml
<!-- web.xml should declare at least Servlet 2.4 -->
<web-app version="3.1">
```
- **Fix:** Add `<%@ page isELIgnored="false" %>` to the JSP or update web.xml.
- **Prevention:** Use a Maven archetype that includes a correct web.xml.

**Failure Mode 3: Stale compiled JSP after changes**
- **Symptom:** Changes to JSP don't appear in the browser after saving.
- **Root Cause:** Container serves the previously compiled class instead of re-translating.
- **Diagnostic:**
```bash
# In Tomcat, delete work directory to force recompilation
rm -rf $CATALINA_HOME/work/Catalina/
```
- **Fix:** Restart the container or configure `development=true` in Jasper.
- **Prevention:** Enable hot-reload in dev mode; use Maven Tomcat plugin's `tomcat:run`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
Java Servlet, HTML, HTTP & APIs

**Builds On This (learn these next):**
Spring MVC, Thymeleaf, JSTL, Expression Language

**Alternatives / Comparisons:**
Thymeleaf, FreeMarker, Mustache, Angular, React

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS     │ HTML templates with embedded    │
│                │ Java, compiled to Servlets      │
│ PROBLEM        │ Putting HTML in Java Servlet    │
│                │ println() calls                 │
│ KEY INSIGHT    │ JSP compiles to a Servlet;      │
│                │ no interpretation overhead      │
│ USE WHEN       │ Maintaining legacy enterprise   │
│                │ Java EE / Spring MVC (WAR)      │
│ AVOID WHEN     │ New Spring Boot JAR projects    │
│                │ (use Thymeleaf instead)         │
│ TRADE-OFF      │ Fast rendering vs poor unit     │
│                │ testability                     │
│ ONE-LINER      │ "HTML files that compile to     │
│                │ Java Servlets"                  │
│ NEXT EXPLORE   │ Java Servlet, Thymeleaf, JSTL   │
└─────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A - System Interaction)** A JSP accesses session data with `${sessionScope.cart}`. What security risk does this create if session data isn't validated, and how does a WAF help?

2. **(B - Scale)** At peak load, 10,000 users simultaneously hit a `.jsp` for the first time after a deployment. What happens to server CPU and response time, and how do you prevent it?

3. **(C - Design Trade-off)** Spring MVC supports both JSP and Thymeleaf. When would you keep JSP in a brownfield project rather than migrating to Thymeleaf, even if Thymeleaf is "better"?
