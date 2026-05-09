---
version: 1
layout: default
title: "CDK"
parent: "Cloud - AWS"
grand_parent: "Technical Dictionary"
nav_order: 57
permalink: /cloud-aws/cdk/
id: AWS-057
category: "Cloud - AWS"
difficulty: "★★★"
depends_on: ["CloudFormation", "IAM (Identity and Access Management)"]
used_by: ["AWS Cost Optimization"]
related: ["CloudFormation", "EKS", "Lambda", "ECS / Fargate"]
tags: [aws, cdk, iac, infrastructure-as-code, typescript, python, cloud]
---

# CDK

## ⚡ TL;DR

**AWS CDK (Cloud Development Kit)** lets you define AWS infrastructure using TypeScript, Python, Java, C#, or Go - instead of YAML/JSON. CDK code **synthesizes** to CloudFormation templates; all deploy via CloudFormation under the hood. Key advantage: real programming language (loops, conditionals, abstractions, type-safety, IDE completion). **Constructs** are reusable components at three levels: L1 (raw CFN resources), L2 (opinionated abstractions), L3 (complete patterns).

---

## 🔥 Problem This Solves

CloudFormation YAML: verbose, no type-checking, no reuse (copy-paste), no IDE autocomplete, hard to review. CDK: write infrastructure in TypeScript → type errors caught at compile time → reusable Construct libraries → clean diffs in PR reviews → test infrastructure with Jest.

---

## 📘 Textbook Definition

AWS CDK is an open-source software development framework that allows you to define cloud infrastructure using familiar programming languages. CDK apps contain stacks, which contain constructs (cloud components). Running `cdk synth` produces CloudFormation templates; `cdk deploy` deploys them. CDK Constructs are the building blocks, available at L1 (auto-generated from CloudFormation), L2 (opinionated defaults), and L3 (solution patterns).

---

## ⏱️ 30 Seconds

```
CDK workflow:
  1. Write TypeScript/Python/Java/Go code
  2. cdk synth      → generates CloudFormation templates
  3. cdk diff       → shows infrastructure changes (like terraform plan)
  4. cdk deploy     → deploys via CloudFormation
  5. cdk destroy    → deletes stack

Construct levels:
  L1 (CfnBucket):   Direct CloudFormation resource, all properties
  L2 (Bucket):      Opinionated with smart defaults + helper methods
  L3 (StaticWebsite): Complete pattern (S3 + CloudFront + Route53)

Languages: TypeScript, Python, Java, C#, Go
CDK Constructs Hub: community-published reusable constructs
```

---

## 🔩 First Principles

- **CDK synthesizes to CloudFormation**: CDK is a tool on top of CloudFormation; all AWS resource types supported
- **Constructs are composable**: L2 Bucket contains L1 CfnBucket + policies; L3 patterns compose multiple L2 constructs
- **Stack = deployable unit**: one CDK stack → one CloudFormation stack; multiple stacks in one CDK app
- **Environments**: `{ account: '123456789', region: 'us-east-1' }` - deploy same stack to multiple environments
- **CDK Bootstrapping**: one-time setup per account/region (`cdk bootstrap`) deploys CDK support infrastructure (S3 bucket for assets, IAM roles)
- **Escape hatches**: `CfnBucket` (L1) override any property not exposed by L2 via `addPropertyOverride`

---

## 🧪 Thought Experiment

Team building 5 microservices. Each needs: ECR repo, ECS task definition, ECS service, ALB target group, ALB listener rule. Without CDK: 5 × 100+ lines of CloudFormation YAML. With CDK: `new EcsWebService(this, 'UsersService', { serviceName: 'users', port: 8080 })` - a custom L3 construct that creates all 5 resources. 5 services = 5 lines of instantiation. Changing a default across all services: change 1 line in the construct.

---

## 🧠 Mental Model / Analogy

CDK is like **writing a program that generates an architect's blueprint**: instead of hand-drawing 100 rooms identically (YAML duplication), you write a loop. Need 10 identical buildings? A `for` loop generates 10 blueprints. Want each floor to be different? Use function parameters. Want to reuse a wing design? Create a class. The blueprints (CloudFormation) are what AWS reads; CDK is the meta-layer that makes writing blueprints productive.

---

## 📶 Gradual Depth

**Level 1 - Beginner**: `cdk init app --language typescript`. Create Stack. Add L2 constructs (Bucket, Function, Queue). Run `cdk synth` to see generated CloudFormation. Run `cdk deploy`.

**Level 2 - Practitioner**: L2 constructs with opinionated defaults: `new s3.Bucket(this, 'MyBucket', { versioned: true, encryption: BucketEncryption.S3_MANAGED })`. Cross-stack references: `bucket.bucketArn` in Stack A used in Stack B. `cdk diff` before every deploy in CI/CD.

**Level 3 - Advanced**: Custom L2 Construct: extend `Construct` class, compose multiple AWS resources into a reusable component. CDK Aspects: tree visitor pattern - walk entire CDK tree and apply cross-cutting policies (e.g., enforce encryption on all buckets, add tags to all resources). CDK Pipelines: self-mutating CI/CD pipeline using CDK.

**Level 4 - Expert**: CDK Constructs Library publishing: publish to NPM/PyPI for cross-team reuse; semantic versioning for infrastructure changes. CDK Projen: project generator for CDK apps (enforces conventions). CDK testing: `assertions.Template.fromStack(stack).hasResourceProperties('AWS::S3::Bucket', {...})` - unit test CloudFormation output. AWS Solutions Constructs: official L3 patterns (SQS→Lambda→DynamoDB, etc.). CDK diff in PR: `cdk diff` output in pull request comments; infra review = code review. Escape hatches: `cfnBucket.addPropertyOverride('VersioningConfiguration.Status', 'Enabled')` for properties not exposed by L2. CDK Migrate: import existing CloudFormation templates into CDK.

---

## ⚙️ How It Works

### CDK App (TypeScript)

```typescript
// lib/vpc-stack.ts
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import { Construct } from "constructs";

export class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // L2 VPC construct: creates VPC + public/private subnets + NAT GW + route tables
    this.vpc = new ec2.Vpc(this, "AppVpc", {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          name: "Public",
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: "Private",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
        {
          name: "Isolated",
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
          cidrMask: 28, // for RDS
        },
      ],
    });
  }
}
```

```typescript
// lib/app-stack.ts - Main application stack
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as rds from "aws-cdk-lib/aws-rds";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sqs from "aws-cdk-lib/aws-sqs";
import { Construct } from "constructs";

interface AppStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
}

export class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);

    const { vpc } = props;

    // S3 Bucket with opinionated security defaults
    const assetsBucket = new s3.Bucket(this, "AssetsBucket", {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [
        {
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
          expiration: cdk.Duration.days(365),
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN, // keep bucket on stack delete
    });

    // SQS Queue with DLQ
    const dlq = new sqs.Queue(this, "OrdersDlq", {
      retentionPeriod: cdk.Duration.days(14),
    });

    const ordersQueue = new sqs.Queue(this, "OrdersQueue", {
      visibilityTimeout: cdk.Duration.minutes(5),
      deadLetterQueue: {
        queue: dlq,
        maxReceiveCount: 5,
      },
    });

    // RDS Aurora Serverless v2
    const dbCluster = new rds.DatabaseCluster(this, "Database", {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_4,
      }),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 32,
      writer: rds.ClusterInstance.serverlessV2("writer"),
      readers: [
        rds.ClusterInstance.serverlessV2("reader1", { scaleWithWriter: true }),
      ],
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_ISOLATED },
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, "Cluster", {
      vpc,
      containerInsights: true,
    });

    // Fargate Service with ALB
    const fargateService = new ecs.FargateService(this, "AppService", {
      cluster,
      taskDefinition: this.createTaskDefinition(vpc),
      desiredCount: 3,
      assignPublicIp: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    // Lambda for async processing
    const processorFunction = new lambda.Function(this, "OrderProcessor", {
      runtime: lambda.Runtime.JAVA_21,
      handler: "org.springframework.cloud.function.adapter.aws.FunctionInvoker",
      code: lambda.Code.fromAsset("target/function.jar"),
      memorySize: 1024,
      timeout: cdk.Duration.minutes(5),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      architecture: lambda.Architecture.ARM_64, // Graviton2
      snapStart: lambda.SnapStartConf.ON_PUBLISHED_VERSIONS,
    });

    // Grant permissions using L2 grant methods
    assetsBucket.grantReadWrite(processorFunction); // least privilege
    ordersQueue.grantConsumeMessages(processorFunction); // SQS consumer
    dbCluster.grantConnect(processorFunction); // RDS IAM auth

    // SQS → Lambda event source
    processorFunction.addEventSource(
      new cdk.aws_lambda_event_sources.SqsEventSource(ordersQueue, {
        batchSize: 10,
        reportBatchItemFailures: true,
      }),
    );

    // Outputs
    new cdk.CfnOutput(this, "BucketName", {
      value: assetsBucket.bucketName,
    });
  }

  private createTaskDefinition(vpc: ec2.Vpc): ecs.FargateTaskDefinition {
    const taskDef = new ecs.FargateTaskDefinition(this, "TaskDef", {
      cpu: 512,
      memoryLimitMiB: 1024,
    });

    taskDef.addContainer("app", {
      image: ecs.ContainerImage.fromEcrRepository(
        ecr.Repository.fromRepositoryName(this, "AppRepo", "my-app"),
      ),
      portMappings: [{ containerPort: 8080 }],
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: "app" }),
      healthCheck: {
        command: [
          "CMD-SHELL",
          "curl -f http://localhost:8080/actuator/health || exit 1",
        ],
      },
    });

    return taskDef;
  }
}
```

```typescript
// bin/app.ts - Entry point
const app = new cdk.App();

const vpcStack = new VpcStack(app, "VpcStack", {
  env: { account: "123456789", region: "us-east-1" },
});

new AppStack(app, "AppStack", {
  vpc: vpcStack.vpc,
  env: { account: "123456789", region: "us-east-1" },
});

// Same code, different environment
new AppStack(app, "AppStackDev", {
  vpc: devVpcStack.vpc,
  env: { account: "987654321", region: "us-west-2" },
});
```

### CDK Testing

```typescript
import { Template, Match } from "aws-cdk-lib/assertions";

test("S3 bucket has versioning enabled", () => {
  const app = new cdk.App();
  const stack = new AppStack(app, "TestStack", { vpc: mockVpc });
  const template = Template.fromStack(stack);

  template.hasResourceProperties("AWS::S3::Bucket", {
    VersioningConfiguration: { Status: "Enabled" },
    PublicAccessBlockConfiguration: {
      BlockPublicAcls: true,
      BlockPublicPolicy: true,
    },
  });
});

test("Lambda has arm64 architecture", () => {
  const template = Template.fromStack(stack);
  template.hasResourceProperties("AWS::Lambda::Function", {
    Architectures: ["arm64"],
    SnapStart: { ApplyOn: "PublishedVersions" },
  });
});
```

---

## ⚖️ Comparison Table: CDK vs Terraform vs CloudFormation

|                         | CDK                          | Terraform   | CloudFormation |
| ----------------------- | ---------------------------- | ----------- | -------------- |
| **Language**            | TypeScript/Python/Java/Go/C# | HCL         | YAML/JSON      |
| **Multi-cloud**         | ❌ (AWS)                     | ✅          | ❌ (AWS)       |
| **Type safety**         | ✅ Full                      | Partial     | None           |
| **Compile-time checks** | ✅                           | ✅          | ❌             |
| **Testing**             | ✅ Jest/pytest               | ❌ (tftest) | ❌             |
| **State management**    | CloudFormation               | State file  | CloudFormation |
| **Maturity**            | Good (v2)                    | Excellent   | Excellent      |
| **Learning curve**      | High (CDK + construct model) | Medium      | Medium         |

---

## ⚠️ Common Misconceptions

| Misconception                        | Reality                                                              |
| ------------------------------------ | -------------------------------------------------------------------- |
| "CDK replaces CloudFormation"        | CDK synthesizes TO CloudFormation; both in use simultaneously        |
| "L2 constructs cover all use cases"  | Some properties only in L1; use escape hatches when needed           |
| "cdk deploy is like terraform apply" | CDK diff ≠ terraform plan; use `cdk diff` explicitly before deploy   |
| "CDK is only for TypeScript users"   | Python, Java, Go, C# all supported; Java/TypeScript are most popular |

---

## 🔗 Related Keywords

- [CloudFormation](/cloud-aws/cloudformation/) - CDK synthesizes to CloudFormation
- [ECS / Fargate](/cloud-aws/ecs-fargate/) - L2 ECS constructs simplify container deployment
- [Lambda](/cloud-aws/lambda/) - L2 Function construct with sensible defaults

---

## 📌 Quick Reference Card

```bash
# Install CDK
npm install -g aws-cdk

# Initialize app
cdk init app --language typescript

# Install required CDK libraries
npm install aws-cdk-lib constructs

# Bootstrap account/region (one-time)
cdk bootstrap aws://ACCOUNT-ID/REGION

# Synthesize (generate CloudFormation)
cdk synth

# Diff (preview changes)
cdk diff

# Deploy
cdk deploy --all

# Deploy specific stack
cdk deploy AppStack

# Destroy
cdk destroy AppStack

# List stacks
cdk list
```

---

## 🧠 Think About This

The biggest CDK productivity gain vs raw CloudFormation comes from the L2 grant methods. In CloudFormation, granting a Lambda function access to S3 requires: IAM policy with specific S3 actions, IAM role, policy attachment - 3 resources, 30+ lines. In CDK: `bucket.grantReadWrite(lambdaFunction)` - one line. This method creates the IAM policy with correct actions, attaches it to the Lambda execution role, and handles all the cross-references. More importantly, it's hard to get wrong: the CDK authors chose the right S3 actions; you can't accidentally grant `s3:*`. This least-privilege-by-default pattern - `grantRead`, `grantWrite`, `grantReadWrite`, `grantPut`, `grantDelete` - exists across almost all L2 constructs. Using these consistently means your infrastructure-as-code is also security-as-code.
