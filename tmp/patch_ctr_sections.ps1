# patch_ctr_sections.ps1
# Adds EVOLUTION, ESSENTIAL vs ACCIDENTAL, Transferable Wisdom,
# Surprising Truth, and *Hint: to all CTR v2 entries
param([string]$BASE = "C:\ASK\MyWorkspace\sk-keys\dictionary\tier-6-infrastructure-devops\CTR-containers")

$utf8 = New-Object System.Text.UTF8Encoding $false

function Read-File($path) {
    $bytes = [System.IO.File]::ReadAllBytes($path)
    $start = if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) { 3 } else { 0 }
    $txt = [System.Text.Encoding]::UTF8.GetString($bytes, $start, $bytes.Length - $start)
    return $txt -replace "`r`n", "`n"
}

function Write-File($path, $content) {
    [System.IO.File]::WriteAllText($path, $content, $utf8)
}

function Patch-File($code, $evolution, $essential, $accidental, $wisdom, $wisdomApps, $truth, $hint1, $hint2, $hint3) {
    $f = Get-ChildItem $BASE -Filter "$code*.md" | Select-Object -First 1
    if (-not $f) { Write-Host "NOT FOUND: $code"; return }
    $n = Read-File $f.FullName

    # 1. Add EVOLUTION after THE INVENTION MOMENT block (before next ---)
    if ($n -notmatch '\*\*EVOLUTION:\*\*') {
        $evoText = "`n`n**EVOLUTION:** $evolution"
        # Find THE INVENTION MOMENT paragraph and append after it
        $n = [regex]::Replace($n, '(?s)(\*\*THE INVENTION MOMENT:\*\*.+?)(\n\n---)', { $args[0].Groups[1].Value + $evoText + $args[0].Groups[2].Value })
    }

    # 2. Add ESSENTIAL vs ACCIDENTAL after Cost: line (before next ---)
    if ($n -notmatch 'ESSENTIAL vs ACCIDENTAL') {
        $essText = "`n`n**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**`n**Essential:** $essential`n**Accidental:** $accidental"
        $n = [regex]::Replace($n, '(?s)(\*\*Cost:\*\*.+?)(\n\n---)', { $args[0].Groups[1].Value + $essText + $args[0].Groups[2].Value })
    }

    # 3. Insert Transferable Wisdom and Surprising Truth before Quick Reference Card
    if ($n -notmatch 'Transferable Wisdom') {
        $wisdomSection = @"

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** $wisdom

**Where else this pattern appears:**
$wisdomApps

---

### 💡 The Surprising Truth

$truth

"@
        $n = $n -replace '(\n---\n\n### 📌 Quick Reference Card)', ($wisdomSection + '$1')
    }

    # 4. Add *Hint: after each Think About This question if missing
    if ($n -notmatch '\*Hint:') {
        $n = [regex]::Replace($n, '(1\. \*\*\(Type [A-F][^)]*\).*?)(\n\n2\.)', { $args[0].Groups[1].Value + "`n`n   $hint1" + $args[0].Groups[2].Value })
        $n = [regex]::Replace($n, '(2\. \*\*\(Type [A-F][^)]*\).*?)(\n\n3\.)', { $args[0].Groups[1].Value + "`n`n   $hint2" + $args[0].Groups[2].Value })
        $n = [regex]::Replace($n, '(3\. \*\*\(Type [A-F][^)]*\).*?)(\s*$)', { $args[0].Groups[1].Value + "`n`n   $hint3`n" })
    }

    Write-File $f.FullName $n
    Write-Host "PATCHED: $($f.Name)"
}

# --- CTR-007: OpenShift vs Kubernetes ---
Patch-File "CTR-007" `
    "OpenShift 3.x used Docker and custom SDN networking. OCP 4.x (2019) rewrote on RHCOS, CRI-O, OVN-K, and the Operator framework. OCP 4.14 deprecated DeploymentConfig. The 2024+ direction prioritises multi-cluster ACM and GitOps-first delivery via OpenShift GitOps (ArgoCD)." `
    "Comparing two Kubernetes distributions requires examining security posture, lifecycle management, extension model, and support tiers - this complexity is inherent when choosing between enterprise platforms." `
    "The oc CLI, OpenShift web console, and deprecated DeploymentConfig are implementation details of Red Hat's distribution, not requirements for any enterprise Kubernetes platform." `
    "Any product built on an open-source platform faces a permanent tension: add differentiating features vs stay close to upstream. The deprecation of DeploymentConfig shows upstream alignment usually wins long-term." `
    "- **MySQL vs MariaDB** - MariaDB forked for independence; MySQL added competing features; the two converged on compatibility while diverging internally`n- **Spring Boot vs Micronaut** - Spring Boot leads; Micronaut offers compatible APIs while differentiating on compile-time DI`n- **AWS RDS vs Aurora** - Aurora is MySQL/PostgreSQL compatible with 5x performance claims - exactly the OpenShift model applied to databases" `
    "OpenShift's oc CLI is fully backward-compatible with kubectl - every kubectl command works unchanged. Many engineers believe they need to learn a new CLI when in fact existing kubectl muscle memory transfers 100%. The only new commands are OpenShift-specific: oc new-app, oc adm, oc status. Red Hat intentionally maintains this parity to lower migration friction from vanilla Kubernetes." `
    "*Hint:* Research how OpenShift SCCs interact with OCI image build pipelines and how hadolint DL3002 maps to SCC runAsNonRoot enforcement." `
    "*Hint:* Look at OpenShift's SCC implementation - it runs as a compiled admission plugin inside the API server binary, avoiding the network hop that external webhooks require." `
    "*Hint:* Compare OCP Deployment plus ArgoCD image updater to DeploymentConfig image-change triggers; research GitOps tools that provide equivalent push-based deploy on new image push."

# --- CTR-008: Container ---
Patch-File "CTR-008" `
    "Containers evolved from Unix chroot (1979) to Solaris Zones (2004) to LXC (2008) to Docker (2013). OCI Runtime Spec (2015) standardised the container definition. Post-2017, the Kubernetes pod became the production unit. Modern additions include SBOM attestation and user namespace remapping for rootless operation." `
    "The need to isolate a process's filesystem, network, and PID view while sharing the kernel is inherent - you cannot have both full isolation AND shared kernel without namespace-style primitives." `
    "The specific implementation choices (overlayFS, runc, OCI manifests) are Docker's design, not the only possible container implementation." `
    "The most powerful abstractions give a process a consistent, isolated view of its environment while sharing underlying resources. This isolation-over-shared-resource pattern appears wherever contention meets the need for isolation." `
    "- **Virtual threads (Java 21)** - give each virtual thread the illusion of its own OS thread while multiplexing onto fewer carrier threads`n- **Browser tab sandboxing** - each tab gets an isolated security context sharing the browser engine; namespace-like boundaries prevent cross-tab XSS`n- **Python virtualenvs** - give each project an isolated package view while sharing the host Python interpreter" `
    "A container does not start a new OS - it starts a single process (PID 1 inside the container) with a restricted view of the host. This is why containers start in milliseconds: there is no boot sequence, no init system, no kernel loading. The container is just process 12437 on your host, with modified namespace visibility. This is the most important insight to understand before reasoning about container security." `
    "*Hint:* Research how ps aux on a container host shows ALL container processes with host PIDs, while ps inside the container shows only namespace-local PIDs - this reveals the kernel sharing directly." `
    "*Hint:* Investigate the /proc/1/ns/ filesystem to see how namespaces are represented as file descriptors, and how nsenter lets you enter a container's namespace from the host." `
    "*Hint:* Compare container startup time with VM boot time using time docker run vs time vagrant up - count the steps each skips and why."

# --- CTR-009: Docker ---
Patch-File "CTR-009" `
    "Docker 0.1 (2013): basic run/build/push. Docker 1.0 (2014): production-ready. Docker 1.9 (2015): overlay networking. OCI formed (2015). Multi-stage builds (2017). Kubernetes deprecates Docker as runtime (2020). BuildKit stable (2021). Docker Scout supply-chain analytics (2023). Today Docker CLI is the standard interface; the backend uses BuildKit plus containerd." `
    "Developers need to build, distribute, and run containers - these three operations are inherently necessary regardless of the tool or implementation." `
    "The specific Docker CLI syntax, Docker daemon architecture, layered TAR format, and Docker Hub rate limits are Docker's implementation choices, not fundamental container requirements." `
    "When a new technology category emerges, the tool that defines the dominant CLI UX defines what 'correct' looks like for years - even after the underlying implementation is replaced. Docker's verbs became the container vocabulary." `
    "- **Git** - git's subcommand model (checkout, commit, push, pull) became the mental model for version control; even GitHub CLI follows git's verb patterns`n- **kubectl** - borrowed Docker's imperative verb style (apply, get, describe, delete); CNCF tools using different verbs have higher adoption friction`n- **npm** - npm's install/publish/run verbs defined JavaScript dependency management; yarn and pnpm remain compatible with npm's verb model" `
    "Docker's CMD and ENTRYPOINT are frequently misunderstood even by experienced engineers. ENTRYPOINT sets the executable; CMD provides default arguments. When either uses string form (shell form), Docker wraps it in /bin/sh -c - which changes SIGTERM handling: the signal goes to the shell, not the app. This is one of the most common causes of containers that silently ignore SIGTERM during rolling updates, causing in-flight requests to be dropped." `
    "*Hint:* Test signal handling by running a container with CMD node server.js (shell form) vs CMD with exec form and sending SIGTERM; observe which PID receives the signal using docker exec and ps." `
    "*Hint:* Investigate Docker BuildKit remote cache backends (--cache-from, --cache-to) and how they enable layer-level cache sharing across CI runners with no shared local cache." `
    "*Hint:* Research docker buildx multi-platform builds and how a single manifest list serves both AMD64 and ARM64 images - critical for Apple Silicon dev machines vs Graviton production nodes."

# --- CTR-010: Docker Image ---
Patch-File "CTR-010" `
    "Docker V1 format (2013) used content-addressable IDs. V2 schema (2014) introduced SHA256 manifests. OCI Image Spec (2015) formalised V2 as a standard. Multi-arch manifests (2017) enable a single tag to serve amd64/arm64. OCI Artifacts (2019+) extended registries to store Helm charts, SBOMs, and Sigstore signatures. Today images carry SLSA provenance attestations for supply-chain security." `
    "Distributing software reproducibly across machines requires a versioned, content-addressed snapshot of the filesystem and runtime configuration - this is inherent regardless of implementation." `
    "The layered TAR format, Union FS driver, manifest JSON structure, and OCI Image Config fields are Docker's design choices, not fundamental requirements for software distribution." `
    "Content-addressed storage - identifying artifacts by their hash, not their name - is the most reliable way to ensure you get exactly what you asked for. Named references are mutable aliases for human convenience; hashes are the immutable ground truth." `
    "- **Git objects** - every commit, tree, and blob is identified by SHA256; git tag is a mutable alias for a commit hash, just like Docker tag is a mutable alias for an image digest`n- **npm package-lock.json** - pins exact tarball hashes (sha512) for each dependency; the integrity field is content-addressed verification`n- **Nix package manager** - every package is named by the cryptographic hash of its build inputs; identical inputs always produce identical outputs globally" `
    "A Docker image does not contain traditional binaries in a flat filesystem - it contains a sequence of filesystem diffs (layer tarballs) that reconstruct the full filesystem when stacked. More importantly, files deleted in a later layer (RUN rm /secret) are still present in the earlier layer's tarball - they are just hidden by the overlay. Secret scanning tools must therefore analyse ALL layers, not just the final composed filesystem. This is why you cannot truly delete sensitive data from a published image without rebuilding from scratch." `
    "*Hint:* Use docker save myimage | tar -xf - to see the raw image TAR structure; examine the layer tarballs and manifest.json to understand the physical OCI format." `
    "*Hint:* Research OCI Image Index (multi-arch manifests) and how a single digest can reference different images for different platforms - critical for Apple Silicon vs production node compatibility." `
    "*Hint:* Investigate how trivy --format cyclonedx generates an SBOM from image layers, and why a deleted file still appears in the SBOM from earlier layers."

# --- CTR-011: Docker Layer ---
Patch-File "CTR-011" `
    "Docker V1 (2013) used sequential integer layer IDs. V2 (2014) switched to SHA256 content-addressed IDs enabling deduplication. AUFS was the original Union FS; overlay2 (Linux 4.0+, 2015) became the standard. OCI Distribution Spec (2017) formalised the registry layer API. BuildKit (2021+) introduces more efficient layer diffing and cache exporting for CI pipelines." `
    "To distribute a filesystem efficiently across versions, you need some form of delta/diff transmission - storing only changes is inherent if bandwidth and storage efficiency matter." `
    "The specific TAR-based layer format, overlay2 driver implementation, and blobs/sha256/ registry path format are Docker/OCI implementation choices that could be implemented differently." `
    "Break a large versioned artifact into composable, independently-versionable, deduplication-eligible layers. The most stable layer goes at the bottom; the most volatile goes at the top." `
    "- **Web CDN caching** - base JS framework (200KB, long TTL) and app bundle (20KB, short TTL) split so updates invalidate only the volatile bundle`n- **Git commit history** - each commit is a diff from the previous state; shared commits are reused across branches without duplication`n- **Terraform state layering** - separate remote state for network, compute, and application tiers; changes to the app layer do not require a network tier plan" `
    "The widely-stated advice 'put rarely-changing layers first' has a surprising consequence: cleanup operations (RUN rm largefile) create a whiteout file in a new layer but do not reclaim space from the original layer. A 500 MB binary added in layer 2 and deleted in layer 3 still occupies 500 MB in the image TAR. Multi-stage builds avoid this entirely by only copying the final needed files into a clean base layer - which is why they produce dramatically smaller images than single-stage builds with cleanup runs." `
    "*Hint:* Inspect a running container's overlay mounts with mount | grep overlay2 on the host to see the actual lowerdir, upperdir, and workdir paths that implement the Union FS stacking." `
    "*Hint:* Research overlay2 copy-on-write semantics: what happens when a container writes to a file that exists in a read-only lower layer? How does this affect performance for write-heavy workloads like databases?" `
    "*Hint:* Compare docker build --squash (merges all layers into one) with a standard build and a multi-stage build in terms of image size, layer count, and cache hit rate for iterative development."

# --- CTR-012: Dockerfile ---
Patch-File "CTR-012" `
    "Dockerfiles were introduced with Docker 0.1 (2013). Docker 17.05 added multi-stage builds. BuildKit (shipped stable 2021) added syntax directives (#syntax= at top), heredoc support (Docker 23+), and mount cache (--mount=type=cache). The Dockerfile remains the dominant image authoring format; alternatives like Buildpacks and kaniko-compatible configs remain niche." `
    "Any reproducible build system needs a declarative specification of the build environment and steps - this is inherent in reproducible software packaging." `
    "The specific Dockerfile instruction syntax (FROM, RUN, COPY, CMD, ENTRYPOINT, ENV), the build-time vs runtime instruction distinction, and the BuildKit syntax directive format are Docker's implementation choices." `
    "A build specification should be a deterministic, executable document: given the same inputs and instructions, it always produces the same output. Version-control the build spec alongside the source code it builds." `
    "- **Makefile** - deterministic build specification for C/C++ projects; targets map to build steps; dependencies define ordering, just like Dockerfile instruction order`n- **GitHub Actions workflow YAML** - CI pipeline as code; each step is a build instruction; caching mirrors Dockerfile layer caching`n- **Terraform HCL** - declarative specification of infrastructure; plan phase is analogous to docker build --dry-run; apply is docker build" `
    "The Dockerfile RUN instruction runs commands in a temporary container during build - not on your host machine. This means filesystem changes made by RUN are captured as a new image layer. But environment variables set with RUN export MY_VAR=value are NOT persisted across layers - only file changes persist. This surprises many developers who expect RUN export to set an environment variable for subsequent instructions. Use ENV MY_VAR=value (which sets build-time and runtime env vars) or ARG MY_VAR (build-time only)." `
    "*Hint:* Research the difference between ARG and ENV in Dockerfiles - specifically which is available only during build vs at container runtime, and why ARG values appear in docker history but ENV does not." `
    "*Hint:* Investigate Docker BuildKit mount cache (RUN --mount=type=cache,target=/root/.cache) and how it persists the package manager cache between builds without polluting image layers." `
    "*Hint:* Look at hadolint (Dockerfile linter) rules - specifically DL3007 (avoid latest tag), DL3008 (pin apt package versions), and DL3025 (CMD must use exec form) - and explain why each rule exists."

# --- CTR-013: Docker Build Context ---
Patch-File "CTR-013" `
    "The build context concept shipped with Docker 0.1 (2013). The .dockerignore file was added in Docker 1.1 (2014) to control what is sent. BuildKit (2021) introduced lazy context loading - context files are only transferred when actually referenced by a COPY instruction, drastically reducing unnecessary transfers for large monorepos." `
    "A build tool needs to know which files are inputs to the build - the concept of a build context (the set of files available during build) is inherent in any hermetic build system." `
    "The specific mechanism of sending context as a TAR archive to the Docker daemon over a Unix socket or TCP connection is Docker's implementation choice; BuildKit's lazy context is an improvement on this model." `
    "Minimise the blast radius of changes by reducing the scope of inputs to each build step. The smaller the build context, the faster the transfer, the smaller the cache key, and the fewer irrelevant changes that invalidate the cache." `
    "- **Bazel build targets** - each BUILD target explicitly lists its inputs (srcs); no implicit access to files outside the target's declared inputs`n- **Git sparse checkout** - only checkout files needed for the current workspace; reduces clone time for large monorepos`n- **Lambda function packages** - include only the runtime code and dependencies in the ZIP; exclude test files, documentation, and dev dependencies" `
    "When you run docker build ., the entire directory tree is sent to the Docker daemon as a TAR archive BEFORE the first Dockerfile instruction executes. For a monorepo with a GB of files, this happens even if your Dockerfile only COPYs a single 10 KB file. This is why engineers working in monorepos without .dockerignore see docker build taking 30+ seconds before the first FROM instruction begins - all that time is context transfer, not actually building anything." `
    "*Hint:* Measure the context transfer time separately from the build time by watching docker build output for the 'Sending build context' line - then add a .dockerignore and compare." `
    "*Hint:* Research BuildKit lazy context loading (DOCKER_BUILDKIT=1) and how it transfers only the files referenced by COPY instructions rather than the entire context directory." `
    "*Hint:* Investigate how remote build contexts (docker build https://github.com/org/repo.git) work and when they are preferable to local context transfer for CI pipelines."

# --- CTR-014: Multi-Stage Build ---
Patch-File "CTR-014" `
    "Multi-stage builds shipped in Docker 17.05 (2017). Before this, the community workaround was the 'builder pattern': two separate Dockerfiles, a build image and a runtime image, with a shell script extracting artifacts. Multi-stage builds formalised this in a single Dockerfile. BuildKit (2021) added parallel stage execution and --target flag for building specific stages." `
    "Producing a minimal runtime artifact from a fat build environment is inherently necessary whenever the build toolchain (compiler, test runner, dev deps) must not be present in the production image." `
    "The specific Dockerfile COPY --from=stage syntax, the sequential stage naming convention, and the --target build flag are Docker's implementation choices for this pattern." `
    "Separate the build environment from the runtime environment - the tools required to build an artifact are not the tools required to run it. Only the final artifact and its runtime dependencies belong in the production package." `
    "- **Java JAR building** - JDK (build) vs JRE (runtime): compile with JDK, deploy with JRE only; same concept 20 years before multi-stage builds`n- **TypeScript compilation** - build with tsc and all devDependencies; ship only compiled JS and production dependencies`n- **Go binary building** - compile with Go toolchain (500MB); ship a single statically linked binary (5MB) in a scratch image" `
    "A Go application compiled in a multi-stage Docker build can result in an image smaller than 10 MB using FROM scratch as the final stage - an image with nothing but the compiled binary and no OS at all. This means no shell, no package manager, no /etc/passwd, no /tmp. Security scanners have nothing to scan because there are no OS packages. The attack surface is literally just the application binary. This is the logical endpoint of the minimal image philosophy, and it is achievable today with statically linked languages like Go and Rust." `
    "*Hint:* Build a Go application with FROM golang:1.22 as builder and FROM scratch as final - measure the final image size and try running a shell inside it to experience what a scratch image means." `
    "*Hint:* Research BuildKit parallel stage execution: when two FROM stages have no dependency between them, BuildKit builds them simultaneously. Map this to your own Dockerfiles and identify which stages could be parallelised." `
    "*Hint:* Investigate the --target flag for docker build and how it enables building only the test stage of a multi-stage Dockerfile in CI without building the production stage unnecessarily."

# --- CTR-015: Docker Compose ---
Patch-File "CTR-015" `
    "Docker Compose was originally a standalone tool (docker-compose, Python-based) acquired by Docker Inc in 2014. Compose V2 (2021) rewrote it in Go as a Docker CLI plugin (docker compose). The compose.yaml specification became a CNCF-donated standard. Compose is now used as the canonical local development pattern and increasingly for simple production on single-node systems." `
    "Running multiple interdependent containers locally requires defining their relationships, startup order, networking, and volumes - this orchestration need is inherent regardless of the tool." `
    "The specific compose.yaml YAML syntax, the Docker network bridge model, service name DNS resolution, and the docker compose up command are Docker's implementation choices." `
    "Define multi-component systems declaratively as a single, version-controlled specification. Each component's dependencies, configuration, and resource requirements should be declared in one place and reproducible with a single command." `
    "- **Kubernetes Helm charts** - declarative multi-service specification for Kubernetes; values.yaml maps to compose.yaml environment substitution`n- **Vagrant + Vagrantfile** - single declarative file defines multi-VM development environments; vagrant up is the docker compose up equivalent`n- **Serverless Framework YAML** - declares multiple Lambda functions, their triggers, and resources in one specification file; deploy with one command" `
    "Docker Compose creates a private Docker network for your services automatically and uses the service name as the DNS hostname within that network. A service named db is reachable at the hostname db from other services - you do not need to know its IP address or configure any DNS. This means the same compose.yaml that provides a local database at db:5432 can be made to point to production by simply overriding the environment variable. This service-name-as-hostname convention is exactly how Kubernetes service DNS works (myservice.mynamespace.svc.cluster.local), making compose-to-kubernetes migration conceptually straightforward." `
    "*Hint:* Run docker compose up and then docker network inspect <projectname>_default to see the private DNS network Compose creates and how service names become resolvable hostnames." `
    "*Hint:* Research Docker Compose health checks and depends_on condition: service_healthy - understand how Compose waits for a database to be ready before starting the application service." `
    "*Hint:* Investigate Compose profiles (profiles: [dev]) for conditionally including services (e.g., mock servers, observability tools) in local development without running them in CI."

# --- CTR-016: Container Registry ---
Patch-File "CTR-016" `
    "Docker Hub launched in 2013 as the first public container registry. The Docker Registry HTTP API V2 (2014) became the distribution standard. OCI Distribution Spec (2017) formalised V2 as an open specification. Docker Hub introduced rate limits in 2020 (100 pulls/6h unauthenticated), driving migration to ECR, GCR, GHCR, and self-hosted Harbor. SBOMs and supply-chain attestations stored as OCI artifacts became standard practice from 2022+." `
    "Distributing immutable versioned artifacts reliably to multiple consumers at scale requires a specialised content-addressed store with access control - this need is inherent in any software distribution system." `
    "The specific registry API, the blob/manifest storage model, the tag mutable reference system, and rate limiting policies are implementation choices that differ between Docker Hub, ECR, GCR, and self-hosted registries." `
    "Provide a content-addressed, versioned artifact store with access control. Separate the mutable human-friendly reference (tag) from the immutable content reference (digest) and use digests in production to guarantee repeatability." `
    "- **npm registry** - package.json specifies a name and version range (mutable reference); npm install resolves to exact package tarballs (content-addressed); npm ci uses package-lock.json for digest-equivalent pinning`n- **Maven Central** - artifact coordinates (groupId:artifactId:version) are the tag equivalent; SHA1 checksums are the digest equivalent; corporate Nexus mirrors are the self-hosted equivalent`n- **Git remote** - remote URL is the registry; branch name is the tag; commit SHA is the digest; git fetch --depth 1 is the equivalent of docker pull" `
    "Docker Hub imposes rate limits even on authenticated free users (200 pulls/6h per account). An enterprise development team with 100 engineers sharing a few CI servers can exhaust this limit in under an hour during a busy sprint. The silent symptom is flaky CI pipelines with toomanyrequests errors that appear random but actually follow a 6-hour cycle. Many teams discover this only during a critical release cycle. The fix is a private registry with a pull-through cache, but discovering the rate limit behaviour requires understanding the 6h sliding window reset mechanism." `
    "*Hint:* Research Docker Hub's rate limit architecture - specifically how it measures pulls per 6 hours per IP (unauthenticated) vs per account (authenticated) and how shared CI egress IPs cause pool exhaustion." `
    "*Hint:* Investigate OCI Distribution Spec's manifest vs blob endpoints and how they implement content-addressed storage - why can two differently-named images share the same layers in a registry?" `
    "*Hint:* Compare self-hosted Harbor registry vs AWS ECR pull-through cache vs Docker Hub Team license for a 50-engineer team; consider cost, operational burden, and rate limit resolution."

# --- CTR-017: Linux Namespaces ---
Patch-File "CTR-017" `
    "Linux namespaces were introduced incrementally: mount namespaces (kernel 2.4.19, 2002), UTS and IPC (2.6.19, 2006), PID and network (2.6.24, 2008), user namespaces (3.8, 2013). Docker (2013) was the first widely-adopted user of all six namespace types together. Kernel 5.6 (2020) added time namespaces. User namespaces enabled rootless containers - a container process runs as root inside its namespace but as an unprivileged user on the host." `
    "Isolating a process's view of the system (filesystem mounts, hostnames, process trees, network interfaces, user IDs) while sharing the kernel is an inherent requirement for multi-tenant compute isolation at the OS level." `
    "The specific six namespace types (mnt, uts, ipc, pid, net, user), the clone() syscall flags, and the /proc/PID/ns/ representation are Linux kernel implementation choices." `
    "Give each isolated unit a private, consistent view of shared system resources without copying those resources. The unit believes it owns the resource exclusively; the kernel enforces the illusion." `
    "- **Virtual memory / process address spaces** - each process believes it has exclusive access to the full memory address range; the MMU and OS enforce the illusion via page tables`n- **Database schemas** - each tenant schema provides an isolated namespace for table names; the same table name (users) can exist in multiple schemas without conflict`n- **Python virtualenvs** - each virtualenv provides an isolated view of installed packages; sys.path namespace isolation without forking a new interpreter" `
    "User namespaces allow a container process to appear as root (UID 0) inside the container while being an unprivileged user (UID 1000+) on the host. This is the technical foundation of rootless containers. The surprising implication: a rootless container can be compromised and the attacker gains root inside the container namespace - but they are still UID 1000 on the host with no elevated privileges. This is a fundamentally stronger security guarantee than a traditional root-run container where a breakout grants host root access." `
    "*Hint:* Use unshare --pid --mount --fork --mount-proc /bin/bash on a Linux host to manually create a minimal container-like namespace environment without Docker - observe what PID 1 looks like inside." `
    "*Hint:* Research how user namespaces map UIDs: run id inside a rootless Podman container and then look up the corresponding host UID in /proc/self/uid_map on the host." `
    "*Hint:* Investigate the security implications of namespace escape vulnerabilities (runc CVE-2019-5736) - what kernel mechanism did this CVE abuse, and which namespace type was the escape vector?"

# --- CTR-018: Cgroups ---
Patch-File "CTR-018" `
    "Control groups (cgroups) were developed at Google by Paul Menage and Rohit Seth, merged into Linux kernel 2.6.24 (2008). Cgroups v2 (unified hierarchy) merged in kernel 4.5 (2016) and became the systemd and Docker default from 2021. Cgroups v2 adds pressure stall information (PSI) for memory and CPU pressure monitoring and unified resource accounting." `
    "Limiting and accounting for a process group's resource consumption (CPU, memory, I/O, network) without requiring separate VMs is an inherent need for multi-tenant workloads sharing a host." `
    "The specific cgroup v1/v2 hierarchy structure, the CPU shares vs quota distinction, and the memory.limit_in_bytes interface are kernel implementation choices that evolved between v1 and v2." `
    "Set explicit resource budgets for every isolated workload. An unbounded process in a shared system is a reliability risk to its neighbours. The budget forces capacity planning and prevents accidental resource monopolisation." `
    "- **Kubernetes resource requests/limits** - Pod spec resource requests (scheduling budget) and limits (cgroup enforcement) map directly to cgroup cpu.cfs_quota_us and memory.limit_in_bytes`n- **AWS Lambda memory limit** - each Lambda invocation runs in a cgroup with the configured memory limit; exceeding it triggers OOM kill and extends cold start for the replacement`n- **Database connection limits** - max_connections in PostgreSQL is a cgroup-like resource limit at the application layer; exceeding it causes connection refusal analogous to cgroup OOM kill" `
    "Cgroups v1 and v2 handle CPU throttling very differently in a way that surprises engineers. Cgroups v1 CPU quota (cpu.cfs_quota_us) can throttle a container even when the host CPU is idle - if a container uses its allocated quota in the first 50ms of a 100ms period, it is throttled for the remaining 50ms regardless of available CPU. This causes latency spikes in bursty workloads that appear as performance problems even on underutilised hosts. Kubernetes allows cpu.cfs_period_us to be tuned to reduce this; cgroups v2 improves the scheduler fairness model." `
    "*Hint:* Observe container CPU throttling in action by running a CPU-intensive container with --cpus=0.5 and measuring its wall-clock runtime vs CPU time; check /sys/fs/cgroup/cpu/docker/<id>/cpu.stat for nr_throttled." `
    "*Hint:* Research the difference between CPU requests (Kubernetes scheduling weight) and CPU limits (cgroup hard cap) and why setting CPU limits can cause mysterious latency spikes in Java applications." `
    "*Hint:* Investigate cgroups v2 memory.pressure and cpu.pressure files (PSI - Pressure Stall Information) and how they enable Kubernetes to detect resource pressure before OOM events occur."

# --- CTR-019: Container Networking ---
Patch-File "CTR-019" `
    "Docker's networking model shipped in 2013 with a default bridge (docker0). Docker 1.9 (2015) added user-defined overlay networks for multi-host communication. CNI (Container Network Interface) spec (2015) separated network plugins from the runtime. Kubernetes adopted CNI and popularised Calico, Flannel, Cilium. Cilium's eBPF-based networking (2021+) replaced iptables rules for high-performance pod networking." `
    "Isolated processes need controlled network connectivity - both to each other and to external systems. Providing isolated network stacks with controlled routing is inherently necessary for multi-tenant containerised workloads." `
    "The specific Docker bridge networking, veth pair implementation, iptables NAT rules, and overlay network encapsulation (VXLAN/Geneve) are implementation choices. CNI plugins provide alternatives at each layer." `
    "Network isolation is a namespace concern (who can see whom) and a policy concern (who is allowed to talk to whom). These two concerns are independent: namespace isolation prevents accidental communication; network policy prevents deliberate unauthorised communication." `
    "- **AWS VPC Security Groups** - stateful firewall rules that control allowed traffic between EC2 instances; conceptually equivalent to Kubernetes NetworkPolicy enforced at the cloud infrastructure layer`n- **Linux iptables** - the kernel's packet filtering framework that Docker and Kubernetes both use under the hood for NAT, routing, and traffic control`n- **VLAN segmentation** - network-level isolation using VLAN tags; the physical network equivalent of container network namespaces" `
    "Every Docker container on the default bridge network can reach every other Docker container on the same host by IP address - there is no default isolation between containers on the same bridge. This surprises engineers who assume container isolation extends to the network layer. You must explicitly create user-defined Docker networks and assign containers to specific networks to achieve network isolation. In Kubernetes, pods in the same namespace can communicate without restriction by default; NetworkPolicy resources must be explicitly created to restrict traffic. Many production clusters have no NetworkPolicy objects at all." `
    "*Hint:* Create two Docker containers on the default bridge and observe they can ping each other by IP; then create a user-defined network for each and observe they are isolated - this reveals the bridge model." `
    "*Hint:* Research how Cilium's eBPF networking eliminates iptables for pod-to-pod routing in Kubernetes - compare the number of iptables rules in a cluster with Flannel vs Cilium at 1,000 pods." `
    "*Hint:* Investigate CNI plugin selection for Kubernetes and the trade-offs between Calico (BGP-based), Flannel (VXLAN overlay), and Cilium (eBPF) in terms of performance, features, and operational complexity."

# --- CTR-020: Volume Mounts ---
Patch-File "CTR-020" `
    "Docker volumes shipped in Docker 0.1 (2013). Named volumes (docker volume create) arrived in Docker 1.9 (2015). The Container Storage Interface (CSI) spec was donated to CNCF in 2017 and became Kubernetes's standard storage plugin API. CSI enabled cloud-provider storage (EBS, EFS, GCS) to integrate with Kubernetes through a standardised interface. NFS and hostPath volumes remain common for on-premises clusters." `
    "Containers are ephemeral but some state must persist beyond the container's lifecycle. The need to separate persistent state from ephemeral compute is inherent in stateful container workloads." `
    "The specific Docker volume driver model, Kubernetes PersistentVolume/PersistentVolumeClaim abstraction, and CSI plugin interface are implementation choices for solving the persistence requirement." `
    "Separate ephemeral compute from persistent state. A container should be disposable; its data should not be. The interface between compute and storage should be well-defined and independently lifecycle-managed." `
    "- **Twelve-factor app backing services** - databases, caches, queues are attached resources accessed via URL; the app treats them as attached, not embedded - exactly the volume mount philosophy`n- **AWS EBS volume attachment** - a persistent disk attached to (and detachable from) an EC2 instance; if the instance is terminated, the EBS volume survives and can be reattached`n- **NFS shared storage** - a network filesystem mounted into multiple servers simultaneously; the NFS server is persistent; the compute clients are disposable" `
    "Kubernetes HostPath volumes mount a directory from the Kubernetes node's filesystem directly into a pod. This creates a hidden dependency between a pod and the specific node it runs on - the pod can only run on nodes that have the required directory. This breaks the pod's mobility and makes the node stateful. Many teams use hostPath as a quick solution for sharing log directories or socket files, not realising they have effectively pinned their pod to a specific node. This is why Kubernetes marks hostPath as a security risk in Pod Security Standards and CSI ephemeral volumes are the recommended alternative." `
    "*Hint:* Create a Kubernetes pod with a hostPath volume and then delete and recreate the pod with node affinity removed - observe what happens when Kubernetes schedules it to a different node." `
    "*Hint:* Research the Kubernetes PersistentVolumeClaim lifecycle: what happens to the PV and its data when a PVC is deleted with ReclaimPolicy Retain vs Delete? When is each appropriate?" `
    "*Hint:* Investigate CSI drivers for cloud storage (aws-ebs-csi-driver, gcp-compute-persistent-disk-csi-driver) and understand how they implement dynamic provisioning, snapshots, and volume expansion."

Write-Host "=== PATCH BATCH 1 (CTR-007 to CTR-020) DONE ==="

