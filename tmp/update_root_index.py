"""
update_root_index.py
Updates dictionary/index.md with accurate counts and ID ranges from actual files.
"""
import re
from pathlib import Path

BASE = Path(__file__).parent.parent / "dictionary"
ROOT_INDEX = BASE / "index.md"

# Category order and metadata
CATEGORIES = [
    # (row_num, display_name, folder_path, tier_label)
    ("1",   "CS Fundamentals - Paradigms",        "tier-1-foundations/CSF-cs-fundamentals"),
    ("2",   "Data Structures & Algorithms",        "tier-1-foundations/DSA-data-structures"),
    ("3",   "Operating Systems",                   "tier-1-foundations/OSY-operating-systems"),
    ("4",   "Linux",                               "tier-1-foundations/LNX-linux"),
    ("5",   "Networking",                          "tier-2-networking-security/NET-networking"),
    ("6",   "HTTP & APIs",                         "tier-2-networking-security/API-http-apis"),
    ("7",   "Security",                            "tier-2-networking-security/SEC-security"),
    ("7a",  "Identity & Access Management",        "tier-2-networking-security/IAM-iam-access"),
    ("7b",  "Cryptography",                        "tier-2-networking-security/CRY-cryptography"),
    ("8",   "Java & JVM Internals",               "tier-3-java/JVM-java-jvm-internals"),
    ("9",   "Java Language",                       "tier-3-java/JLG-java-language"),
    ("10",  "Java Concurrency",                   "tier-3-java/JCC-java-concurrency"),
    ("11",  "Spring Core",                         "tier-3-java/SPR-spring-core"),
    ("11a", "JPA & Hibernate",                    "tier-3-java/JPH-jpa-hibernate"),
    ("12",  "Database Fundamentals",              "tier-4-data/DBF-database-fundamentals"),
    ("13",  "NoSQL & Distributed Databases",      "tier-4-data/NDB-nosql-distributed"),
    ("14",  "Caching",                            "tier-4-data/CCH-caching"),
    ("15",  "Data Fundamentals",                  "tier-4-data/DAT-data-fundamentals"),
    ("16",  "Big Data & Streaming",               "tier-4-data/BIG-bigdata-streaming"),
    ("16a", "Messaging & Event Streaming",        "tier-4-data/MSG-messaging-streaming"),
    ("17",  "Distributed Systems",               "tier-5-distributed-architecture/DST-distributed-systems"),
    ("18",  "Microservices",                     "tier-5-distributed-architecture/MSV-microservices"),
    ("19",  "System Design",                     "tier-5-distributed-architecture/SYD-system-design"),
    ("20",  "Software Architecture Patterns",   "tier-5-distributed-architecture/SAP-software-architecture"),
    ("21",  "Design Patterns",                  "tier-5-distributed-architecture/DPT-design-patterns"),
    ("22",  "Async & Background Processing",    "tier-5-distributed-architecture/ASY-async-background"),
    ("23",  "Containers",                       "tier-6-infrastructure-devops/CTR-containers"),
    ("24",  "Kubernetes",                       "tier-6-infrastructure-devops/K8S-kubernetes"),
    ("25",  "Cloud - AWS",                     "tier-6-infrastructure-devops/AWS-cloud-aws"),
    ("26",  "Cloud - Azure",                   "tier-6-infrastructure-devops/AZR-cloud-azure"),
    ("27",  "Cloud - GCP",                     "tier-6-infrastructure-devops/GCP-cloud-gcp"),
    ("28",  "CI/CD",                           "tier-6-infrastructure-devops/CCD-cicd"),
    ("29",  "Git & Branching Strategy",        "tier-6-infrastructure-devops/GIT-git-branching"),
    ("30",  "Maven & Build Tools",             "tier-6-infrastructure-devops/MVN-maven-build"),
    ("31",  "Code Quality",                    "tier-6-infrastructure-devops/CDQ-code-quality"),
    ("32",  "Testing",                         "tier-6-infrastructure-devops/TST-testing"),
    ("33",  "Observability & SRE",             "tier-6-infrastructure-devops/OBS-observability-sre"),
    ("34",  "Infrastructure as Code",          "tier-6-infrastructure-devops/IAC-infrastructure-code"),
    ("35",  "Platform & Modern SWE",           "tier-6-infrastructure-devops/PLT-platform-swe"),
    ("36",  "HTML",                            "tier-7-frontend/HTM-html"),
    ("37",  "CSS",                             "tier-7-frontend/CSS-css"),
    ("38",  "JavaScript",                      "tier-7-frontend/JSC-javascript"),
    ("39",  "TypeScript",                      "tier-7-frontend/TSC-typescript"),
    ("40",  "React",                           "tier-7-frontend/RCT-react"),
    ("41",  "Angular",                         "tier-7-frontend/ANG-angular"),
    ("42",  "Node.js",                         "tier-7-frontend/NDJ-nodejs"),
    ("43",  "npm & Package Management",        "tier-7-frontend/NPM-npm-packages"),
    ("44",  "Webpack & Build Tools",           "tier-7-frontend/WBP-webpack-build"),
    ("45",  "AI Foundations",                  "tier-8-artificial-intelligence/AIF-ai-foundations"),
    ("46",  "LLMs & Prompt Engineering",       "tier-8-artificial-intelligence/LLM-llms-prompt-eng"),
    ("47",  "RAG & Agents & LLMOps",           "tier-8-artificial-intelligence/RAG-rag-agents-llmops"),
    ("48",  "AI Product Engineering",          "tier-8-artificial-intelligence/AIP-ai-product"),
    ("49",  "Behavioral & Leadership",         "tier-9-professional-domain/BHV-behavioral-leadership"),
    ("50",  "Document Generation",             "tier-9-professional-domain/DGN-document-generation"),
    ("51",  "Financial Services Domain",       "tier-9-professional-domain/FIN-financial-domain"),
]

def get_category_stats(folder_rel):
    """Get (count, first_id, last_id) from actual files in folder."""
    folder = BASE / folder_rel
    if not folder.exists():
        return 0, "N/A", "N/A"

    ids = []
    for f in folder.glob("*.md"):
        if f.name == "index.md":
            continue
        # CODE may contain digits (e.g. K8S)
        m = re.match(r"^([A-Z][A-Z0-9]+-\d+)\s*-", f.name)
        if m:
            ids.append(m.group(1))

    if not ids:
        return 0, "N/A", "N/A"

    # Sort by numeric part
    def id_sort_key(id_str):
        code, num = id_str.rsplit("-", 1)
        return (code, int(num))

    ids_sorted = sorted(ids, key=id_sort_key)
    return len(ids), ids_sorted[0], ids_sorted[-1]

def update_root_index():
    text = ROOT_INDEX.read_text(encoding="utf-8")

    # Update total count
    total_count = sum(get_category_stats(cat[2])[0] for cat in CATEGORIES)
    text = re.sub(
        r"\d[\d,]+\+ keyword entries",
        f"{total_count:,}+ keyword entries",
        text
    )

    # Update each row in the table
    for (num, name, folder) in CATEGORIES:
        count, first_id, last_id = get_category_stats(folder)
        if first_id == "N/A":
            continue
        range_str = f"{first_id}-{last_id}"

        # Find the row for this category number
        # Pattern: | num  | [name] | old_count | old_range |
        row_pattern = re.compile(
            r"(\|\s*" + re.escape(num) + r"\s*\|\s*\[" + re.escape(name) + r"[^\|]*\|\s*)\d+(\s*\|\s*)[^\|]+(\s*\|)",
            re.DOTALL
        )
        m = row_pattern.search(text)
        if m:
            text = text[:m.start()] + m.group(1) + str(count) + m.group(2) + range_str + m.group(3) + text[m.end():]
        else:
            print(f"  [WARN] Could not find row for {num}: {name}")

    ROOT_INDEX.write_text(text, encoding="utf-8")
    print(f"Updated root index.md: {total_count:,}+ total entries across 55 categories")

if __name__ == "__main__":
    update_root_index()
