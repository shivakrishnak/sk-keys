"""
Tier-2 Gap Analysis + Keyword Master List Generator
Categories: API (HTTP & APIs), NET (Networking), SEC (Security)

Format: (new_id, old_id_or_None, title, level, difficulty)
- old_id = None  → new keyword (stub created)
- old_id present → rename + frontmatter update
Retired/merged duplicates: API-001, API-026, API-053, API-057
(they appear as WARNINGs; deleted by post-step)
"""

import pathlib, re

BASE = pathlib.Path(
    r"c:\ASK\MyWorkspace\sk-keys\dictionary\tier-2-networking-security"
)

# ─────────────────────────────────────────────────────────────────────────────
# API — HTTP & APIs  (76 keywords)
# ─────────────────────────────────────────────────────────────────────────────
API_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("API-001", None, "What Is an API and Why It Matters",                "L0", "🌱"),
    ("API-002", None, "The Client-Server Model — A Map",                  "L0", "🌱"),
    ("API-003", None, "HTTP — The Language of the Web",                   "L0", "🌱"),
    ("API-004", None, "API Design Philosophy (REST vs RPC vs Graph)",     "L0", "🌱"),
    ("API-005", None, "The API Ecosystem Map",                            "L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("API-006", "API-005", "HTTP Methods",                                "L1", "★☆☆"),
    ("API-007", "API-006", "HTTP Status Codes",                           "L1", "★☆☆"),
    ("API-008", "API-007", "HTTP Headers",                                "L1", "★☆☆"),
    ("API-009", "API-002", "HTTP-1.1 Protocol",                           "L1", "★☆☆"),
    ("API-010", "API-009", "REST",                                        "L1", "★☆☆"),
    ("API-011", "API-037", "API Keys",                                    "L1", "★☆☆"),
    ("API-012", None,       "URL and URI Structure",                      "L1", "★☆☆"),
    ("API-013", None,       "Request / Response Lifecycle",               "L1", "★☆☆"),
    ("API-014", None,       "JSON vs XML Data Format",                    "L1", "★☆☆"),
    ("API-015", "API-044", "Content Negotiation",                         "L1", "★☆☆"),
    ("API-016", None,       "Stateless Design Principle",                 "L1", "★☆☆"),
    ("API-017", "API-023", "WebSocket",                                   "L1", "★☆☆"),

    # L2 — WORKING
    ("API-018", "API-003", "HTTP-2",                                      "L2", "★★☆"),
    ("API-019", "API-004", "HTTP-3 / QUIC",                               "L2", "★★☆"),
    ("API-020", "API-008", "Keep-Alive / Connection Pooling",             "L2", "★★☆"),
    ("API-021", "API-012", "Idempotency in HTTP",                         "L2", "★★☆"),
    ("API-022", "API-010", "RESTful Constraints (Richardson Maturity)",   "L2", "★★☆"),
    ("API-023", "API-034", "OAuth2",                                      "L2", "★★☆"),
    ("API-024", "API-035", "JWT",                                         "L2", "★★☆"),
    ("API-025", "API-039", "CORS",                                        "L2", "★★☆"),
    ("API-026", "API-045", "OpenAPI / Swagger",                           "L2", "★★☆"),
    ("API-027", "API-031", "API Versioning",                              "L2", "★★☆"),
    ("API-028", "API-030", "API Gateway",                                 "L2", "★★☆"),
    ("API-029", "API-029", "Webhook",                                     "L2", "★★☆"),
    ("API-030", "API-024", "Server-Sent Events (SSE)",                    "L2", "★★☆"),
    ("API-031", "API-025", "Long Polling",                                "L2", "★★☆"),
    ("API-032", "API-013", "GraphQL",                                     "L2", "★★☆"),
    ("API-033", "API-032", "API Rate Limiting",                           "L2", "★★☆"),

    # L3 — INTERMEDIATE
    ("API-034", "API-011", "HATEOAS",                                     "L3", "★★☆"),
    ("API-035", "API-036", "OIDC",                                        "L3", "★★☆"),
    ("API-036", "API-038", "HMAC",                                        "L3", "★★☆"),
    ("API-037", "API-018", "gRPC",                                        "L3", "★★☆"),
    ("API-038", "API-019", "Protocol Buffers",                            "L3", "★★☆"),
    ("API-039", "API-020", "gRPC Streaming",                              "L3", "★★☆"),
    ("API-040", "API-014", "GraphQL Schema",                              "L3", "★★☆"),
    ("API-041", "API-015", "GraphQL Resolvers",                           "L3", "★★☆"),
    ("API-042", "API-016", "GraphQL N+1 Problem",                         "L3", "★★☆"),
    ("API-043", "API-017", "GraphQL Subscriptions",                       "L3", "★★☆"),
    ("API-044", "API-050", "API Caching",                                 "L3", "★★☆"),
    ("API-045", "API-051", "ETag / Cache-Control",                        "L3", "★★☆"),
    ("API-046", "API-052", "Pagination — Cursor Offset Keyset",           "L3", "★★☆"),
    ("API-047", "API-049", "BFF (Backend for Frontend)",                  "L3", "★★☆"),
    ("API-048", "API-046", "API Contract Testing",                        "L3", "★★☆"),
    ("API-049", "API-047", "API Mocking",                                 "L3", "★★☆"),
    ("API-050", "API-033", "API Authentication Patterns",                 "L3", "★★☆"),
    ("API-051", "API-055", "API Documentation",                           "L3", "★★☆"),

    # L4 — EXPERT
    ("API-052", "API-021", "SOAP",                                        "L4", "★★★"),
    ("API-053", "API-022", "WSDL",                                        "L4", "★★★"),
    ("API-054", "API-048", "API Backward Compatibility",                  "L4", "★★★"),
    ("API-055", "API-054", "API Throttling",                              "L4", "★★★"),
    ("API-056", "API-059", "API Observability",                           "L4", "★★★"),
    ("API-057", "API-060", "API Security Best Practices",                 "L4", "★★★"),
    ("API-058", "API-028", "API Gateway Patterns",                        "L4", "★★★"),
    ("API-059", "API-058", "API Deprecation Strategy",                    "L4", "★★★"),
    ("API-060", "API-040", "XSS via API",                                 "L4", "★★★"),
    ("API-061", "API-041", "CSRF",                                        "L4", "★★★"),
    ("API-062", "API-043", "SSRF",                                        "L4", "★★★"),
    ("API-063", "API-042", "SQL Injection via API",                       "L4", "★★★"),
    ("API-064", "API-027", "API Management Platform",                     "L4", "★★★"),
    ("API-065", "API-056", "API Design Best Practices",                   "L4", "★★★"),

    # L4.5 — ARCHITECT (new)
    ("API-066", None, "API Strategy at Scale",                            "L45","🔥"),
    ("API-067", None, "API Platform Design",                              "L45","🔥"),
    ("API-068", None, "API Migration Strategy (REST to gRPC)",            "L45","🔥"),
    ("API-069", None, "API-First Development Culture",                    "L45","🔥"),

    # L5 — CREATOR (new)
    ("API-070", None, "HTTP Protocol Design Internals",                   "L5", "🔬"),
    ("API-071", None, "Hypermedia APIs — Deep Theory",                    "L5", "🔬"),
    ("API-072", None, "Protocol Design Trade-offs at Scale",              "L5", "🔬"),
    ("API-073", None, "API Specification Language Design",                "L5", "🔬"),

    # META (new)
    ("API-074", None, "Protocol Selection Mental Model",                  "META","🧠"),
    ("API-075", None, "API Design Trade-off Framing",                     "META","🧠"),
    ("API-076", None, "Consumer-First API Thinking",                      "META","🧠"),
]

# Retired duplicates in API (will appear as WARNINGs after script):
#   API-001 — API Keys          (duplicate of API-037, now new API-011)
#   API-026 — Apigee            (merged into API-027, now new API-064)
#   API-053 — Pagination        (duplicate of API-052, now new API-046)
#   API-057 — Hypermedia HATEOAS(duplicate of API-011, now new API-034)

# ─────────────────────────────────────────────────────────────────────────────
# NET — Networking  (64 keywords)
# ─────────────────────────────────────────────────────────────────────────────
NET_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("NET-001", None, "Why Networking Matters — The Internet as Infrastructure","L0","🌱"),
    ("NET-002", None, "How Data Travels from A to B — A Map",               "L0", "🌱"),
    ("NET-003", None, "The Internet History and Architecture",               "L0", "🌱"),
    ("NET-004", None, "Networks Engineers Encounter (LAN, WAN, Cloud)",      "L0", "🌱"),
    ("NET-005", None, "The Networking Ecosystem Map",                        "L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("NET-006", "NET-001", "OSI Model",                                      "L1", "★☆☆"),
    ("NET-007", "NET-002", "TCP/IP Stack",                                   "L1", "★☆☆"),
    ("NET-008", "NET-011", "IP Addressing",                                  "L1", "★☆☆"),
    ("NET-009", "NET-012", "Subnet and CIDR",                                "L1", "★☆☆"),
    ("NET-010", "NET-014", "DNS",                                            "L1", "★☆☆"),
    ("NET-011", "NET-003", "TCP",                                            "L1", "★☆☆"),
    ("NET-012", "NET-004", "UDP",                                            "L1", "★☆☆"),
    ("NET-013", "NET-018", "Socket, Port and Ephemeral Port",                "L1", "★☆☆"),
    ("NET-014", "NET-024", "Bandwidth vs Throughput",                        "L1", "★☆☆"),
    ("NET-015", "NET-023", "Packet Loss, Latency and Jitter",                "L1", "★☆☆"),
    ("NET-016", "NET-019", "Firewall",                                       "L1", "★☆☆"),
    ("NET-017", None,       "MAC Address and Ethernet Frame",                "L1", "★☆☆"),

    # L2 — WORKING
    ("NET-018", "NET-006", "TCP Handshake",                                  "L2", "★★☆"),
    ("NET-019", "NET-007", "TCP Teardown",                                   "L2", "★★☆"),
    ("NET-020", "NET-008", "Congestion Control",                             "L2", "★★☆"),
    ("NET-021", "NET-009", "Flow Control",                                   "L2", "★★☆"),
    ("NET-022", "NET-010", "Sliding Window",                                 "L2", "★★☆"),
    ("NET-023", "NET-013", "NAT",                                            "L2", "★★☆"),
    ("NET-024", "NET-015", "DNS Resolution Flow",                            "L2", "★★☆"),
    ("NET-025", "NET-027", "DHCP",                                           "L2", "★★☆"),
    ("NET-026", "NET-028", "ARP",                                            "L2", "★★☆"),
    ("NET-027", "NET-029", "ICMP / ping / traceroute",                       "L2", "★★☆"),
    ("NET-028", "NET-021", "Proxy vs Reverse Proxy",                         "L2", "★★☆"),
    ("NET-029", "NET-020", "VPN",                                            "L2", "★★☆"),

    # L3 — INTERMEDIATE
    ("NET-030", "NET-016", "CDN",                                            "L3", "★★☆"),
    ("NET-031", "NET-017", "Anycast",                                        "L3", "★★☆"),
    ("NET-032", "NET-022", "Load Balancer L4 and L7",                        "L3", "★★☆"),
    ("NET-033", "NET-025", "Network Latency Optimization",                   "L3", "★★☆"),
    ("NET-034", "NET-026", "BGP",                                            "L3", "★★☆"),
    ("NET-035", "NET-030", "Network Topologies",                             "L3", "★★☆"),
    ("NET-036", "NET-005", "QUIC",                                           "L3", "★★☆"),
    ("NET-037", "NET-032", "East-West vs North-South Traffic",               "L3", "★★☆"),
    ("NET-038", "NET-033", "Service Discovery",                              "L3", "★★☆"),
    ("NET-039", "NET-035", "Overlay Networks",                               "L3", "★★☆"),
    ("NET-040", "NET-036", "VLAN",                                           "L3", "★★☆"),
    ("NET-041", "NET-038", "TLS / SSL",                                      "L3", "★★☆"),
    ("NET-042", "NET-039", "Certificate Authority",                          "L3", "★★☆"),
    ("NET-043", "NET-040", "Network Observability",                          "L3", "★★☆"),

    # L4 — EXPERT
    ("NET-044", "NET-031", "Zero Trust Networking",                          "L4", "★★★"),
    ("NET-045", "NET-034", "Network Policies",                               "L4", "★★★"),
    ("NET-046", "NET-037", "mTLS",                                           "L4", "★★★"),
    ("NET-047", None,       "BGP Route Leaks and Hijacking",                 "L4", "★★★"),
    ("NET-048", None,       "DDoS Attack Patterns and Mitigation",           "L4", "★★★"),
    ("NET-049", None,       "DNSSEC",                                        "L4", "★★★"),
    ("NET-050", None,       "IPv6 and Migration Strategy",                   "L4", "★★★"),
    ("NET-051", None,       "eBPF for Networking",                           "L4", "★★★"),
    ("NET-052", None,       "Network Performance Tuning at Scale",           "L4", "★★★"),
    ("NET-053", None,       "East-West Encryption at Scale",                 "L4", "★★★"),

    # L4.5 — ARCHITECT (new)
    ("NET-054", None, "Network Architecture Design at Scale",                "L45","🔥"),
    ("NET-055", None, "Multi-Region Network Topology Strategy",              "L45","🔥"),
    ("NET-056", None, "Zero Trust Network Architecture Design",              "L45","🔥"),
    ("NET-057", None, "Service Mesh vs API Gateway Decision Framework",      "L45","🔥"),

    # L5 — CREATOR (new)
    ("NET-058", None, "TCP/IP Protocol Design Principles",                   "L5", "🔬"),
    ("NET-059", None, "BGP Internals and Internet Routing Architecture",     "L5", "🔬"),
    ("NET-060", None, "Congestion Control Algorithm Design",                 "L5", "🔬"),
    ("NET-061", None, "Future Networking — HTTP3 QUIC IPv6 at Scale",        "L5", "🔬"),

    # META (new)
    ("NET-062", None, "Network Debugging Mental Model",                      "META","🧠"),
    ("NET-063", None, "Latency vs Throughput Trade-off Thinking",            "META","🧠"),
    ("NET-064", None, "Protocol Selection Framework",                        "META","🧠"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SEC — Security  (70 keywords)
# ─────────────────────────────────────────────────────────────────────────────
SEC_KEYWORDS = [
    # L0 — ORIENTATION (new)
    ("SEC-001", None, "Why Security Matters — The Adversarial Mindset",      "L0", "🌱"),
    ("SEC-002", None, "The Security Threat Landscape — A Map",               "L0", "🌱"),
    ("SEC-003", None, "How Attackers Think — Attack Surfaces and Vectors",   "L0", "🌱"),
    ("SEC-004", None, "Defense in Depth — The Security Layering Principle",  "L0", "🌱"),
    ("SEC-005", None, "The Security Ecosystem Map (AppSec NetSec CloudSec)", "L0", "🌱"),

    # L1 — FOUNDATIONAL
    ("SEC-006", None,       "Security Principles (OWASP, CWE, CVE)",        "L1", "★☆☆"),
    ("SEC-007", "SEC-001",  "CIA Triad (Confidentiality, Integrity, Availability)","L1","★☆☆"),
    ("SEC-008", "SEC-002",  "Authentication vs Authorization",               "L1", "★☆☆"),
    ("SEC-009", None,       "Encryption Basics",                             "L1", "★☆☆"),
    ("SEC-010", None,       "Public Key Cryptography (PKI)",                 "L1", "★☆☆"),
    ("SEC-011", None,       "Hashing and Password Storage",                  "L1", "★☆☆"),
    ("SEC-012", None,       "HTTPS and TLS Basics",                          "L1", "★☆☆"),
    ("SEC-013", None,       "Principle of Least Privilege",                  "L1", "★☆☆"),
    ("SEC-014", None,       "Secure Defaults",                               "L1", "★☆☆"),
    ("SEC-015", None,       "OWASP Top 10 — Overview",                       "L1", "★☆☆"),
    ("SEC-016", None,       "Security Misconfiguration",                     "L1", "★☆☆"),
    ("SEC-017", None,       "Credentials and Secrets Management Basics",     "L1", "★☆☆"),

    # L2 — WORKING
    ("SEC-018", None, "Cross-Site Scripting (XSS)",                          "L2", "★★☆"),
    ("SEC-019", None, "CSRF (Cross-Site Request Forgery)",                   "L2", "★★☆"),
    ("SEC-020", None, "SQL Injection",                                       "L2", "★★☆"),
    ("SEC-021", None, "SSRF (Server-Side Request Forgery)",                  "L2", "★★☆"),
    ("SEC-022", None, "Session Management Security",                         "L2", "★★☆"),
    ("SEC-023", None, "Input Validation and Output Encoding",                "L2", "★★☆"),
    ("SEC-024", None, "Secure HTTP Headers (CSP, HSTS, X-Frame-Options)",   "L2", "★★☆"),
    ("SEC-025", None, "CORS — Cross-Origin Security",                        "L2", "★★☆"),
    ("SEC-026", None, "OAuth2 Security Model",                               "L2", "★★☆"),
    ("SEC-027", None, "JWT Security",                                        "L2", "★★☆"),
    ("SEC-028", None, "API Key Security Patterns",                           "L2", "★★☆"),
    ("SEC-029", None, "Certificate Management Lifecycle",                    "L2", "★★☆"),
    ("SEC-030", None, "Security Logging and Monitoring",                     "L2", "★★☆"),
    ("SEC-031", None, "Dependency and Supply Chain Security Basics",         "L2", "★★☆"),
    ("SEC-032", None, "Secure Coding Practices",                             "L2", "★★☆"),

    # L3 — INTERMEDIATE
    ("SEC-033", None, "OWASP Top 10 — Deep Dive Per Vulnerability",          "L3", "★★☆"),
    ("SEC-034", None, "Command Injection",                                   "L3", "★★☆"),
    ("SEC-035", None, "Path Traversal",                                      "L3", "★★☆"),
    ("SEC-036", None, "XXE Injection",                                       "L3", "★★☆"),
    ("SEC-037", None, "Insecure Deserialization",                            "L3", "★★☆"),
    ("SEC-038", None, "Broken Access Control and IDOR",                      "L3", "★★☆"),
    ("SEC-039", None, "Cryptographic Failures",                              "L3", "★★☆"),
    ("SEC-040", None, "Secrets Management at Scale (Vault, AWS Secrets)",   "L3", "★★☆"),
    ("SEC-041", None, "Zero Trust Security Model",                           "L3", "★★☆"),
    ("SEC-042", None, "Container Security",                                  "L3", "★★☆"),
    ("SEC-043", None, "Threat Modeling (STRIDE, PASTA)",                     "L3", "★★☆"),
    ("SEC-044", None, "Penetration Testing Fundamentals",                    "L3", "★★☆"),
    ("SEC-045", None, "Security Audit and Code Review",                      "L3", "★★☆"),
    ("SEC-046", None, "mTLS and Service-to-Service Authentication",          "L3", "★★☆"),
    ("SEC-047", None, "Privilege Escalation Patterns",                       "L3", "★★☆"),

    # L4 — EXPERT
    ("SEC-048", None, "Supply Chain Attacks (SolarWinds, XZ Utils)",         "L4", "★★★"),
    ("SEC-049", None, "Log4Shell — CVE-2021-44228",                          "L4", "★★★"),
    ("SEC-050", None, "Heartbleed — CVE-2014-0160",                          "L4", "★★★"),
    ("SEC-051", None, "Memory Safety Vulnerabilities and Exploitation",      "L4", "★★★"),
    ("SEC-052", None, "JWT Algorithm Confusion Attacks",                     "L4", "★★★"),
    ("SEC-053", None, "OAuth2 Attack Vectors",                               "L4", "★★★"),
    ("SEC-054", None, "Cryptographic Protocol Design Flaws",                 "L4", "★★★"),
    ("SEC-055", None, "Lateral Movement Techniques",                         "L4", "★★★"),
    ("SEC-056", None, "Incident Response Playbook",                          "L4", "★★★"),
    ("SEC-057", None, "Security Hardening at Scale",                         "L4", "★★★"),
    ("SEC-058", None, "SSRF at Scale — Cloud Metadata Exploitation",         "L4", "★★★"),
    ("SEC-059", None, "DDoS Attack Patterns and Defense",                    "L4", "★★★"),

    # L4.5 — ARCHITECT (new)
    ("SEC-060", None, "Security Architecture Design Patterns",               "L45","🔥"),
    ("SEC-061", None, "DevSecOps Strategy and Pipeline Security",            "L45","🔥"),
    ("SEC-062", None, "Zero Trust Architecture Design",                      "L45","🔥"),
    ("SEC-063", None, "Compliance-Driven Security (GDPR, SOC2, PCI-DSS)",   "L45","🔥"),

    # L5 — CREATOR (new)
    ("SEC-064", None, "Cryptographic Primitive Design",                      "L5", "🔬"),
    ("SEC-065", None, "Security Protocol Formal Analysis",                   "L5", "🔬"),
    ("SEC-066", None, "Formal Verification of Security Properties",          "L5", "🔬"),
    ("SEC-067", None, "SAST and DAST Pipeline Design and Automation",        "L5", "🔬"),

    # META (new)
    ("SEC-068", None, "Adversarial Thinking as Engineering Mindset",         "META","🧠"),
    ("SEC-069", None, "Security Trade-off Framing",                          "META","🧠"),
    ("SEC-070", None, "Threat Modeling as First-Principles Tool",            "META","🧠"),
]

# ─────────────────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────

DIFF_MAP = {
    "L0":   "★☆☆",
    "L1":   "★☆☆",
    "L2":   "★★☆",
    "L3":   "★★☆",
    "L4":   "★★★",
    "L45":  "★★★",
    "L5":   "★★★",
    "META": "★★★",
}

LEVEL_TAG_MAP = {
    "L0":   ["foundational", "mental-model"],
    "L1":   ["foundational", "first-principles"],
    "L2":   ["intermediate", "pattern"],
    "L3":   ["intermediate", "deep-dive", "tradeoff"],
    "L4":   ["advanced", "production", "deep-dive"],
    "L45":  ["advanced", "architecture", "bestpractice"],
    "L5":   ["advanced", "deep-dive", "first-principles"],
    "META": ["advanced", "mental-model", "bestpractice"],
}

CATEGORY_META = {
    "API": {
        "category": "HTTP & APIs",
        "tier": "tier-2-networking-security",
        "folder": "API-http-apis",
        "parent": "HTTP & APIs",
        "dir": BASE / "API-http-apis",
    },
    "NET": {
        "category": "Networking",
        "tier": "tier-2-networking-security",
        "folder": "NET-networking",
        "parent": "Networking",
        "dir": BASE / "NET-networking",
    },
    "SEC": {
        "category": "Security",
        "tier": "tier-2-networking-security",
        "folder": "SEC-security",
        "parent": "Security",
        "dir": BASE / "SEC-security",
    },
}


def make_nav_order(new_id):
    return int(new_id.split("-")[1])


def make_permalink(code, title):
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"/{code.lower()}/{slug}/"


def sanitize_filename(new_id, title):
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    safe = safe.replace("/", "-")
    return f"{new_id} — {safe}.md"


def build_frontmatter(new_id, title, level, code, meta):
    diff = DIFF_MAP[level]
    tags = LEVEL_TAG_MAP[level]
    category_tag = code.lower()
    all_tags = [category_tag] + tags
    tags_yaml = "\n".join(f"  - {t}" for t in all_tags)
    nav = make_nav_order(new_id)
    permalink = make_permalink(code, title)
    return f"""---
id: {new_id}
title: {title}
category: {meta['category']}
tier: {meta['tier']}
folder: {meta['folder']}
difficulty: {diff}
depends_on:
used_by:
related:
tags:
{tags_yaml}
status: draft
version: 1
layout: default
parent: "{meta['parent']}"
nav_order: {nav}
permalink: {permalink}
---

# {new_id} — {title}

> Entry stub. Generate full content using Master Prompt v3.0.
"""


def process_category(code, keywords):
    meta = CATEGORY_META[code]
    d = meta["dir"]
    print(f"\n{'='*60}")
    print(f"Processing {code} ({len(keywords)} keywords)")
    print(f"{'='*60}")

    # Build old_id → old file map
    old_files = {}
    for f in d.glob(f"{code}-*.md"):
        if f.name == "index.md":
            continue
        m = re.match(rf"({code}-\d+)", f.stem)
        if m:
            old_files[m.group(1)] = f

    # Phase 1: rename existing files to _tmp_ names (avoids collisions)
    tmp_renames = {}
    for new_id, old_id, title, level, diff in keywords:
        if old_id and old_id in old_files:
            src = old_files[old_id]
            tmp = src.parent / f"_tmp_{new_id}_{src.name}"
            src.rename(tmp)
            tmp_renames[new_id] = (tmp, old_id, title, level)
            print(f"  TMP: {src.name} → {tmp.name}")

    # Phase 2: rename _tmp_ files to final names, update frontmatter
    for new_id, old_id, title, level, diff in keywords:
        if new_id in tmp_renames:
            tmp, old_id_, title_, level_ = tmp_renames[new_id]
            new_filename = sanitize_filename(new_id, title)
            dst = d / new_filename
            tmp.rename(dst)
            print(f"  RENAME: {old_id_} → {new_id} — {title}")
            content = dst.read_text(encoding="utf-8", errors="replace")
            content = re.sub(r'^id:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
            content = re.sub(r'^number:\s*.+$', f'id: {new_id}', content, flags=re.MULTILINE)
            content = re.sub(r'^title:\s*".+"$', f'title: "{title}"', content, flags=re.MULTILINE)
            content = re.sub(r"^title:\s*'.+'$", f'title: "{title}"', content, flags=re.MULTILINE)
            nav = make_nav_order(new_id)
            content = re.sub(r'^nav_order:\s*\d+$', f'nav_order: {nav}', content, flags=re.MULTILINE)
            content = re.sub(
                rf'^# {re.escape(old_id_)}.*$',
                f'# {new_id} — {title}',
                content, flags=re.MULTILINE
            )
            dst.write_text(content, encoding="utf-8")

    # Phase 3: create stub files for new keywords
    for new_id, old_id, title, level, diff in keywords:
        if not old_id:
            new_filename = sanitize_filename(new_id, title)
            dst = d / new_filename
            if dst.exists():
                print(f"  SKIP (exists): {new_filename}")
                continue
            fm = build_frontmatter(new_id, title, level, code, meta)
            dst.write_text(fm, encoding="utf-8")
            print(f"  CREATE: {new_filename}")

    # Phase 4: report old files not in new list (duplicates / retired)
    old_ids_used = {kw[1] for kw in keywords if kw[1]}
    for old_id, f in old_files.items():
        if old_id not in old_ids_used:
            print(f"  WARNING (retired): {f.name}")


if __name__ == "__main__":
    process_category("API", API_KEYWORDS)
    process_category("NET", NET_KEYWORDS)
    process_category("SEC", SEC_KEYWORDS)
    print("\nDone. Delete WARNING files manually (retired duplicates).")
