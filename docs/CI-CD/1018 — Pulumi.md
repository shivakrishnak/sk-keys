---
layout: default
title: "Pulumi"
parent: "CI/CD"
nav_order: 1018
permalink: /ci-cd/pulumi/
number: "1018"
category: CI/CD
difficulty: ★★★
depends_on: Infrastructure as Code, Terraform, Cloud, CI/CD Pipeline
used_by: GitOps, Environment Promotion
related: Terraform, Ansible, AWS CDK, OpenTofu
tags:
  - cicd
  - devops
  - cloud
  - deep-dive
  - infrastructure
---

# 1018 — Pulumi

⚡ TL;DR — Pulumi is an IaC tool that lets you provision cloud infrastructure using real programming languages (TypeScript, Python, Go) instead of a domain-specific language, enabling loops, abstractions, and unit tests.

| #1018 | Category: CI/CD | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Infrastructure as Code, Terraform, Cloud, CI/CD Pipeline | |
| **Used by:** | GitOps, Environment Promotion | |
| **Related:** | Terraform, Ansible, AWS CDK, OpenTofu | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A platform team manages 200 S3 buckets across 16 AWS accounts using Terraform. Each bucket has a unique combination of version policies, lifecycle rules, and access logs settings based on the data classification of its content. In HCL, expressing "if bucket is classified as 'sensitive', enable versioning AND object lock AND access logs" requires convoluted `for_each` with `merge()` calls and `dynamic` blocks. The resulting Terraform code is 800 lines of HCL that nobody on the team fully understands. A new platform engineer spends her first week just learning how HCL loops work.

**THE BREAKING POINT:**
HCL is designed to be simple and readable for straightforward infrastructure configurations. But real infrastructure has complexity: conditional logic, loops over heterogeneous inputs, environment-specific branching, abstraction layers. HCL handles simple cases elegantly and complex cases awkwardly. Teams find themselves wishing they could just write a function, a class, or a unit test — things that any programmer has mastered in their primary language.

**THE INVENTION MOMENT:**
This is exactly why Pulumi was created: use the programming language your team already knows — TypeScript, Python, Go, Java, C# — to define infrastructure, getting loops, conditionals, abstractions, and testing frameworks without learning a new DSL.

---

### 📘 Textbook Definition

**Pulumi** is an open-source Infrastructure as Code platform that provisions cloud resources via programs written in general-purpose languages (TypeScript, Python, Go, Java, .NET). Unlike Terraform's HCL (a declarative DSL), Pulumi programs use imperative code constructs that compile to infrastructure declarations at runtime. Pulumi maintains state in a **backend** (Pulumi Cloud, S3, Azure Blob Storage) and uses a **resource model** where each provisioned cloud resource is a programming language object (`new aws.s3.Bucket(...)`) that returns outputs as typed variables. Pulumi supports the full Terraform provider ecosystem via `@pulumi/terraform-provider` bridges and has native providers with deeper AWS/Azure/GCP API coverage than Terraform's equivalents. Pulumi's core advantage is its testing story: infrastructure programs can be unit tested, integration tested, and validated with property-based testing using standard language testing frameworks.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write cloud infrastructure using TypeScript or Python code, not a config file language.

**One analogy:**
> Pulumi is to Terraform what a high-level programming language is to assembly. You can do everything in assembly (Terraform HCL), but you can express complex logic much more naturally in Python (Pulumi). Both produce the same machine-level instructions (cloud API calls), but the development experience is radically different for complex use cases. Most people learn assembly principles first, then use Python in practice.

**One insight:**
The profound shift Pulumi enables is testing infrastructure before deploying it. In Terraform, the only way to know your configuration is correct is to `terraform apply` it (or rely on limited static analysis). In Pulumi TypeScript, you can write unit tests that mock the cloud provider and verify your S3 bucket has versioning enabled — before any cloud API is called. This moves infrastructure verification left by orders of magnitude compared to `terraform plan`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Cloud infrastructure has the same complexity drivers as application logic — branching, loops, abstraction, composition — so it should be expressible in the same languages.
2. Infrastructure changes are high-stakes — the ability to test infrastructure definitions before execution reduces error rates.
3. Type safety catches errors sooner — a TypeScript type error at compile time is cheaper than a cloud API error at apply time.

**DERIVED DESIGN:**
Pulumi's execution model: the user's program runs as a standard process. It registers resource declarations using Pulumi's SDK (`new aws.ec2.Instance(...)`) without immediately calling the cloud API. The Pulumi runtime intercepts these registrations, builds a resource dependency graph (identical to Terraform's), and then communicates with the Pulumi engine to compute the diff against stored state and apply changes. For the user, writing infrastructure looks like writing any application code — with variables, functions, loops, and imports.

**Output semantics** (the most important concept to understand in Pulumi): when you create a resource, attributes like `bucket.id` are not strings — they are `Output<string>` values that resolve asynchronously after the resource is created. This is the key shift from Terraform's `aws_s3_bucket.main.id` reference syntax. In Pulumi TypeScript, `bucket.arn.apply(arn => "arn is: " + arn)` operates on the future value.

**THE TRADE-OFFS:**
**Gain:** Full programming language power for infrastructure; unit testable; familiar for developers; strong typing; IDE autocomplete.
**Cost:** Smaller community than Terraform. More complex mental model (async outputs, the distinction between infrastructure runtime and program runtime). Debugging failures requires understanding both the Pulumi SDK and the cloud provider. Steeper initial learning curve for non-programmers.

---

### 🧪 Thought Experiment

**SETUP:**
You need to create 4 environments (dev, staging, pre-prod, prod) each with an S3 bucket + CloudFront distribution + Route53 record, with different configurations per environment.

**WHAT HAPPENS WITH TERRAFORM:**
```hcl
# For each environment: duplicate the resource blocks
# or use workspace + complex variable maps
# Complex for_each + merge() to handle
# per-environment config differences
# Result: 200 lines of HCL with dynamic blocks
```
Any engineer unfamiliar with HCL advanced patterns must learn before contributing.

**WHAT HAPPENS WITH PULUMI (TypeScript):**
```typescript
const envs = ["dev", "staging", "pre-prod", "prod"];
const isProd = (env: string) => env === "prod";

for (const env of envs) {
  const bucket = new aws.s3.Bucket(`${env}-assets`, {
    versioning: {
      enabled: isProd(env)  // prod only
    }
  });
  const dist = new aws.cloudfront.Distribution(
    `${env}-cdn`, { origins: [{ domainName: bucket.bucketDomainName }] }
  );
}
// 15 lines. Any TypeScript dev reads this.
```

**THE INSIGHT:**
The same infrastructure expressed in a familiar language is dramatically easier to read, write, and review. The cognitive barrier to infrastructure contribution drops — any developer on the team can contribute, not just specialists who know HCL idioms.

---

### 🧠 Mental Model / Analogy

> Pulumi is a compiler for infrastructure. You write infrastructure declarations in TypeScript (or Python, Go) — the source language your team knows. Pulumi compiles them to cloud API calls — the machine instructions that provision real resources. Just as a TypeScript-to-JavaScript compiler lets you write expressive code while getting the performance of native JS, Pulumi lets you write expressive infrastructure while getting the same cloud primitives as Terraform.

- "TypeScript source code" → Pulumi infrastructure program
- "JavaScript output" → cloud API calls (same as Terraform)
- "TypeScript compiler" → Pulumi runtime
- "Type checking" → TypeScript compile-time validation of resource types
- "Unit tests for TypeScript" → Pulumi unit tests mocking cloud providers
- "npm packages" → reusable Pulumi component resources

Where this analogy breaks down: TypeScript compiles instantly; Pulumi programs execute against live cloud APIs (which take seconds to minutes). The "compilation" phase (planning) is fast, but the "execution" phase (applying) is slow — unlike a language compiler that finishes in milliseconds.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Pulumi lets you create cloud infrastructure (servers, databases, networks) by writing normal code in TypeScript or Python instead of a special config file language. If you already know how to code, you already know most of what you need to manage infrastructure with Pulumi.

**Level 2 — How to use it (junior developer):**
Install the Pulumi CLI and run `pulumi new aws-typescript`. This scaffolds a TypeScript project. Write your resources as TypeScript objects: `const bucket = new aws.s3.Bucket("my-bucket")`. Run `pulumi preview` (equivalent of `terraform plan`) to see changes. Run `pulumi up` to apply. Use `pulumi stack` to manage multiple environments. Pulumi state defaults to Pulumi Cloud (free for individuals); for production, configure an S3 backend: `pulumi login s3://my-backend-bucket`.

**Level 3 — How it works (mid-level engineer):**
Pulumi programs are ordinary programs that run in a special "preview" or "up" context. The SDK intercepts `new ResourceType()` calls and registers them with the Pulumi engine via a gRPC channel. The engine resolves the dependency graph (based on which outputs are consumed by which resources), loads the stored stack state, calls the provider plugins (same protocol as Terraform providers — Pulumi can use Terraform providers via bridge), and executes the change plan. `Output<T>` is Pulumi's promise-like type — it represents a value that resolves after a resource is created. `pulumi.interpolate` and `.apply()` transform outputs without blocking execution. Stack references allow cross-stack output sharing (equivalent of Terraform remote state).

**Level 4 — Why it was designed this way (senior/staff):**
Pulumi's key architectural bet was that the Terraform provider ecosystem was the dominant switching cost — if Pulumi could consume Terraform providers, it could offer provider parity immediately. The `pulumi-terraform-bridge` library wraps any Terraform provider in Pulumi's SDK — this is why Pulumi supports 1000+ providers on day one. The tradeoff: bridged providers are one step removed and may lag official Pulumi native providers in API coverage. Pulumi's native providers (for AWS, Azure, GCP, Kubernetes) are generated directly from cloud provider API schemas, offering properties not available in Terraform's providers. The generative AI era has strengthened the case for Pulumi: AI code generation tools (Copilot) understand TypeScript/Python far better than HCL — infrastructure in a standard language gets better AI assist than DSL syntax.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│  PULUMI EXECUTION MODEL                     │
├─────────────────────────────────────────────┤
│                                             │
│  User program (TypeScript/Python):          │
│  import * as aws from "@pulumi/aws";        │
│  const bucket = new aws.s3.Bucket("b");     │
│                                             │
│  RUNTIME:                                   │
│  1. Node.js / Python runs the program       │
│  2. SDK intercepts resource registrations   │
│  3. Sends resource graph to Pulumi engine   │
│     via gRPC                               │
│                                             │
│  PULUMI ENGINE (pulumi CLI):                │
│  4. Loads stack state from backend (S3)     │
│  5. Calls provider plugin for each resource │
│     provider.Check() → validate config     │
│     provider.Diff() → compute changes      │
│     provider.Create/Update/Delete()        │
│  6. Updates stack state                     │
│                                             │
│  PROVIDER LAYER:                            │
│  - Pulumi native: AWS, Azure, GCP, K8s     │
│  - Bridged Terraform providers (any of     │
│    1000+ TF providers via bridge)           │
│                                             │
│  STATE BACKENDS:                            │
│  Pulumi Cloud | S3 | Azure Blob | GCS      │
└─────────────────────────────────────────────┘
```

**Output resolution example:**
```typescript
// bucket.id is Output<string> — future value
const bucket = new aws.s3.Bucket("my-bucket");

// pulumi.interpolate: combine outputs with strings
const url = pulumi.interpolate`https://${
  bucket.websiteEndpoint
}/index.html`;

// .apply(): transform an output value
const upperArn = bucket.arn.apply(
  arn => arn.toUpperCase()
);

// Export: expose values as stack outputs
export const bucketUrl = url;
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Developer writes TypeScript IaC program
  → git branch infra/add-bucket → PR
  → CI: pulumi preview [← YOU ARE HERE]
     Runs program → registers resources
     → Reads state from S3 backend
     → Shows: + Bucket "my-bucket" (create)
               + BucketPolicy (create)
     → Preview attached as PR comment
  → Team reviews, approves PR
  → Merge → CI: pulumi up --yes
  → Resources created
  → Stack outputs exported
```

**FAILURE PATH:**
```
pulumi up fails at BucketPolicy creation
  (S3 bucket created, policy resource fails)
  → State updated for bucket
  → Error: AccessDenied creating bucket policy
  → Fix: add s3:PutBucketPolicy to IAM role
  → Re-run pulumi up
  → Bucket: no diff (already in state)
  → BucketPolicy: retried → success
```

**WHAT CHANGES AT SCALE:**
At scale, Pulumi component resources become critical — they're reusable TypeScript/Python classes that encapsulate multiple cloud resources. A `ComplianceS3Bucket` component might encapsulate: bucket + versioning + access logs + inventory + KMS encryption + public block settings — all verified correct in a unit test before deployment. Teams publish these components to npm/PyPI as internal packages, creating a "platform as code" library that enforces organisation-wide security and compliance standards.

---

### 💻 Code Example

**Example 1 — Basic Pulumi TypeScript:**
```typescript
// index.ts
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const environment = config.require("environment");

const bucket = new aws.s3.Bucket("app-assets", {
  bucket: `myapp-${environment}-assets`,
  versioning: {
    enabled: environment === "prod",
  },
  tags: {
    Environment: environment,
    ManagedBy: "pulumi",
  },
});

// Export for other stacks or CI to consume
export const bucketName = bucket.bucket;
export const bucketArn  = bucket.arn;
```

**Example 2 — Unit testing infrastructure (key Pulumi advantage):**
```typescript
// __tests__/s3.test.ts
import * as pulumi from "@pulumi/pulumi";

// Mocking prevents real cloud API calls in tests
pulumi.runtime.setMocks({
  newResource(type, name, inputs) {
    return {
      id: `${name}_id`,
      state: inputs,
    };
  },
  call(token, args, provider) {
    return args;
  },
});

// Import AFTER setting up mocks
import * as infra from "../index";

describe("S3 bucket", () => {
  it("should have versioning in prod", async () => {
    const name = await new Promise(resolve =>
      infra.bucketName.apply(resolve)
    );
    // Verify name contains environment
    expect(name).toContain("prod");
  });

  it("should have required tags", async () => {
    // pulumi.all resolves multiple Output values
    const tags = await new Promise(resolve =>
      pulumi.all([infra.bucketArn]).apply(resolve)
    );
    expect(tags).toBeDefined();
  });
});
```

**Example 3 — Reusable component resource:**
```typescript
// components/secureS3.ts
export class SecureS3Bucket extends pulumi.ComponentResource {
  public readonly bucket: aws.s3.Bucket;
  public readonly arn: pulumi.Output<string>;

  constructor(name: string, opts?: pulumi.ResourceOptions) {
    super("mycompany:components:SecureS3Bucket", name, {}, opts);

    this.bucket = new aws.s3.Bucket(`${name}-bucket`, {
      versioning: { enabled: true },
      serverSideEncryptionConfiguration: {
        rule: {
          applyServerSideEncryptionByDefault: {
            sseAlgorithm: "AES256",
          },
        },
      },
    }, { parent: this });

    // Block all public access
    new aws.s3.BucketPublicAccessBlock(
      `${name}-public-block`, {
        bucket: this.bucket.bucket,
        blockPublicAcls: true,
        blockPublicPolicy: true,
        ignorePublicAcls: true,
        restrictPublicBuckets: true,
      }, { parent: this }
    );

    this.arn = this.bucket.arn;
    this.registerOutputs({ arn: this.arn });
  }
}
```

---

### ⚖️ Comparison Table

| | Pulumi | Terraform | AWS CDK |
|---|---|---|---|
| Language | TS/Python/Go/Java/.NET | HCL (DSL) | TS/Python/Java/.NET |
| Unit Testing | Full support | Limited (terratest) | Full support |
| Cloud Coverage | Multi-cloud (via TF bridge) | Multi-cloud | AWS only |
| Learning Curve | Low for devs | Medium | Low for Java/TS devs |
| Community Size | Growing | Very large | Medium (AWS-only) |
| State Backend | Pulumi Cloud / S3 / self | S3 / TF Cloud | CloudFormation |
| IDE Support | Excellent (TypeScript) | Good (HCL plugin) | Excellent |

How to choose: Use **Pulumi** when your team consists predominantly of developers who are more comfortable with TypeScript/Python than HCL, or when you need unit testing of infrastructure. Use **Terraform** when you need the largest community ecosystem, most mature tooling, and your infrastructure logic is not overly complex. Use **AWS CDK** only if you're exclusively on AWS and want CloudFormation as the execution layer.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pulumi programs execute top-to-bottom sequentially | Pulumi programs register resources as a graph, not a script. The SDK buffers all registrations and the engine executes them in dependency order — not in the order they appear in code. Apparent sequential code may execute in parallel. |
| `Output<T>` is like a JavaScript Promise | `Output<T>` is similar to a Promise but runs during infrastructure execution, not during the program running phase. `.apply()` runs when the resource value is resolved — which happens during `pulumi up`, not during local program compilation. |
| Pulumi is slower than Terraform | Pulumi and Terraform call the same cloud APIs. Performance is identical for the same set of resource changes. Pulumi's preview step may be marginally slower (running a full Node.js process) for very simple configs. |
| Using TypeScript means you can import any npm package | Any module used in a Pulumi program runs "in the cloud" (provisioning context), not in the deployed application. Importing `express` in a Pulumi program to serve infrastructure is valid syntax but semantically meaningless. |

---

### 🚨 Failure Modes & Diagnosis

**1. Output Resolution Creates Confusing Async Bugs**

**Symptom:** `const url = "https://" + bucket.bucketDomainName` logs as `"https://[object Object]"` instead of the actual URL. Derived variables contain `[Output<string>]` rather than actual values.

**Root Cause:** Operators like `+` applied to `Output<string>` don't resolve the value. `Output<string>` must be composed using `pulumi.interpolate` or `.apply()`.

**Diagnostic:**
```typescript
// WRONG: string concatenation on Output
const url = "https://" + bucket.bucketDomainName;
// → url = "https://[object Object]"

// RIGHT: use pulumi.interpolate
const url = pulumi.interpolate`https://${bucket.bucketDomainName}`;
// → url = Output<"https://mybucket.s3.amazonaws.com">
```

**Prevention:** Enable TypeScript strict mode (`"strict": true` in tsconfig.json). TypeScript will flag direct string concatenation with `Output<string>` as a type error if types are correct.

---

**2. Stack Reference Circular Dependencies**

**Symptom:** Two Pulumi stacks reference each other's outputs. Both stacks fail to deploy: "Error: circular dependency detected."

**Root Cause:** Stack A exports `clusterEndpoint` used by Stack B, and Stack B exports `dbPassword` used by Stack A. The dependency is circular — neither can apply first.

**Diagnostic:**
```bash
# Visualise stack dependencies
pulumi stack graph --dependency-graph | dot -Tpng > graph.png

# Check which stack references which
grep -r "StackReference" .
```

**Fix:** Break the circular dependency. Common pattern: extract shared values into a third "base" stack that both A and B read from without bidirectional references.

**Prevention:** Design stack boundaries so data flows in one direction: base infrastructure → shared services → application stacks. Never create circular stack references.

---

**3. State Drift from Manual Console Changes**

**Symptom:** `pulumi preview` shows 15 resources as "needs update" even though no code changed. Manual S3 bucket ACL was changed in the console.

**Root Cause:** Same as Terraform drift — manual console changes diverge from Pulumi's stored state. On next preview/up, Pulumi observes the actual state through the provider and computes a diff to restore declared configuration.

**Diagnostic:**
```bash
# Refresh state to match current actual state
pulumi refresh

# Check what changed in actual vs state
pulumi refresh --diff
# Shows: bucket ACL changed from private to public-read
```

**Fix:**
```bash
# Option A: accept manual change, update Pulumi code to match
# Change code to match reality, run pulumi up (no-op)

# Option B: revert to declared state
pulumi up
# Pulumi will revert bucket ACL back to "private"
```

**Prevention:** Same as Terraform: enforce no-console-changes policy for Pulumi-managed resources. Use AWS Config or GCP Audit Logs to alert on manual changes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Infrastructure as Code` — Pulumi implements IaC; understanding IaC concepts (desired state, state file, idempotency) is required
- `Terraform` — understanding Terraform's model makes Pulumi's differences and advantages clear; Pulumi is often the "next step" after Terraform
- `TypeScript` — Pulumi's most popular language; TypeScript type system and async patterns are critical for using Pulumi effectively

**Builds On This (learn these next):**
- `GitOps` — Pulumi programs in Git repositories drive GitOps workflows the same way Terraform does
- `Policy as Code` — Pulumi supports CrossGuard (Pulumi's policy engine) for enforcing infrastructure policies in code

**Alternatives / Comparisons:**
- `Terraform` — domain-specific language IaC; simpler for straightforward configs, weaker for complex logic
- `AWS CDK` — AWS-only IaC in general-purpose languages; similar model to Pulumi but generates CloudFormation stacks instead of calling APIs directly
- `Ansible` — imperative configuration management for servers; not a competitor to Pulumi (different problem domain)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ IaC using TypeScript/Python/Go — real     │
│              │ programming languages, not a DSL          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ HCL's limited expressibility for complex  │
│ SOLVES       │ infrastructure logic makes code unmaint.  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Unit test infrastructure before deploying │
│              │ — no other IaC tool enables this natively │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex infrastructure logic; developer   │
│              │ teams; unit testing requirements          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple infrastructure; large team already │
│              │ invested in Terraform tooling/knowledge   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Expressiveness and testability vs smaller │
│              │ community and async Output<T> complexity  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Use the language you already know to     │
│              │  build the infrastructure you need."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pulumi CrossGuard → Component Resources  │
│              │ → Automation API → Pulumi ESC            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Pulumi unit tests mock the cloud provider, so tests pass without calling real APIs. This means a test can verify "the S3 bucket has versioning enabled" without actually creating an S3 bucket. What class of infrastructure bugs can Pulumi unit tests NOT catch, and what testing strategy would you design to catch them — without deploying to production first?

**Q2.** Your team is deciding between Terraform and Pulumi for a new multi-cloud platform (AWS + GCP + Kubernetes). Terraform has a larger community and your ops team knows HCL. Pulumi has better TypeScript support and your dev team hates learning HCL. Describe the precise technical capabilities of each tool for this specific use case, and propose a hybrid strategy that lets both teams work in their preferred tool while maintaining a consistent state and GitOps workflow.

