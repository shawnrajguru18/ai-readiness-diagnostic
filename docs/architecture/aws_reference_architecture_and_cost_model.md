# AWS Reference Architecture & Cost Model

**Product:** Executive AI Diagnostic
**Author:** Chris Bryson
**Date:** 2026-06-17

## Sizing Assumptions 

50 client orgs/month  ·  ~3–4 executives each  ≈  ~175 interviews/month  ·  ~25 min/voice interview  ≈  ~4,400 voice-minutes/month  ·  Multi-tenant SaaS  

## Reference Architecture 

The platform mirrors the Azure architecture with AWS-native equivalents, maintaining the same layered SaaS structure: 

* Amazon CloudFront + AWS WAF provides TLS termination, WAF rules, and global CDN with Shield Standard DDoS protection 

* Amazon S3 (static website) hosts the multi-tenant SPA shell, served via CloudFront 

* Amazon Cognito secures executive sign-in with MFA; IAM Identity Center handles DXC advisor access 

* Amazon API Gateway (HTTP API) + AWS Lambda handle tenant-scoped endpoints, signed-URL minting, scoring, and storage writes 

* AWS Step Functions orchestrates the report-build workflow (equivalent to Azure Durable Functions) 

* Amazon Bedrock (Claude Sonnet for reports, Haiku for turns) powers report generation, chat-path interviews, and transcript synthesis 

* Amazon DynamoDB (on-demand) stores tenants, responses, scores, and benchmarks with per-tenant partition keys 

* ElevenLabs Conversational AI (external SaaS) delivers the voice interview experience — billed per minute 
 

## Component List 

|#|Component|AWS Service |Role |
|---|---|---|---|
| 1 | Edge + WAF | Amazon CloudFront + AWS WAF | TLS, global edge/CDN, WAF rules, DDoS (Shield Standard included) |
| 2 | Frontend | Amazon S3 (static SPA) | Hosts SPA shell; per-client branding; served via CloudFront |
| 3 | Identity (clients) | Amazon Cognito (User Pools) | Exec sign-in, MFA; first 50k MAU free |
| 4 | Identity (DXC) | AWS IAM Identity Center | Advisor access, RBAC, SSO; no incremental cost |
| 5 | API | Amazon API Gateway (HTTP API) | Tenant-scoped REST endpoints, JWT auth 
| 6  | Compute  | AWS Lambda  | Signed-URL minting, scoring, storage writes  |
| 7  | Orchestration  | |AWS Step Functions  | |Report-build workflow (replaces Durable Functions) |
| 8   |AI / LLM   |Amazon Bedrock — Claude (Sonnet/Haiku)   |Report generation, chat-path interview, transcript synthesis   |
| 9   |Operational DB   |Amazon DynamoDB (on-demand)   |Tenants, responses, scores, benchmarks; per-tenant partition key   |
| 10   |Object storage   |Amazon S3 (Standard; CRR for prod)   |PDF reports, transcripts, exports   |
| 11   |Secrets   |AWS Secrets Manager + KMS   |ElevenLabs/Bedrock keys, connection strings   |
| 12   |Observability   |Amazon CloudWatch + X-Ray   |Logs, metrics, tracing, usage analytics  | 
| 13   |Notifications   |Amazon SES (optional)   |Send report links to executives   |
| 14   |Security posture   |GuardDuty + Security Hub + AWS Config   |Threat detection + CSPM   |
| 15   |CI/CD + IaC   |CodePipeline/CodeBuild or GitHub Actions + Terraform/CDK   |Build/test/deploy across dev→staging→prod |
| —   |Voice agent   |ElevenLabs Conversational AI (external SaaS)   |Voice interview itself — billed per minute |


## Monthly Cost — Lean (Cost-Optimised) Baseline 

| Component | Service / Driver | Est. $/mo |
|---|---|---|
|CloudFront + AWS WAF |Low egress + Web ACL + 1 managed rule group |~$25 |
|S3 (frontend) |Few GB + requests |~$2 |
|Cognito |~300 MAU (free < 50k) |$0 |
|API Gateway (HTTP API) |Low request volume |~$2 |
|Lambda |Low invocations (free tier covers most) |~$3 |
|Step Functions |~175 report workflows |~$1 |
|Amazon Bedrock (Claude) |~175 interviews (report + chat + synth) |~$130 |
|DynamoDB |On-demand, low RU/WU + few GB |~$10 |
|S3 (reports/transcripts) |Few GB + requests |~$3 |
|Secrets Manager + KMS |~5 secrets + 1 key |~$4 |
|CloudWatch + X-Ray |Few GB logs + traces |~$10 |
|SES (email) |~300 emails |~$1 |
|CI/CD (CodePipeline / GH Actions) |1 pipeline / free tier |~$5 |
|AWS subtotal (lean) | |~$196 / mo |

 

External — ElevenLabs Conversational AI: ~4,400 min × ~$0.10/min ≈ ~$440/mo  

Lean all-in ≈ ~$640/month 

## Bedrock (Claude) Cost Detail 

Indicative Bedrock pricing: Claude Sonnet-class ≈ $3/1M input, $15/1M output; Claude Haiku-class ≈ $0.80/1M input, $4/1M output (verify current rates). 

 

| Use | Model | Tokens / interview | $/interview |
|---|---|---|---|
| Adaptive chat-path turns |Haiku |~80k in / ~15k out |~$0.12 |
| Report + insight generation |Sonnet |~25k in / ~15k out |~$0.30 |
| Transcript synthesis |Haiku |~20k in / ~5k out |~$0.04 
| Per interview | | | ~$0.46 |

## Environments & Cost (Dev / Staging / Prod) 

AWS best practice is a separate account per environment under AWS Organizations — clean blast-radius isolation and per-env billing. Only prod carries the headline numbers; dev/staging together add only ~20–30%. 

- Usage-based costs do not replicate. Bedrock (~$130) and ElevenLabs (~$440) dominate prod; dev/staging run a handful of test calls, so ~$570 of spend essentially does not replicate. 

- No prod hardening in non-prod. VPC/NAT, GuardDuty/Security Hub, Aurora HA, geo-DR, and expanded WAF are prod-only. 

## Indicative Monthly Cost per Environment (Lean Stack) 

|Component |Dev |Staging |Prod |
|---|---|---|---|
| CloudFront + WAF |— (S3/CF default) |~$10 |~$25 |
| S3 (frontend) |~$1 |~$2 |~$2 |
|API Gateway + Lambda |~$0 (free tier) |~$2 |~$5 |
|Bedrock (Claude) |~$10 |~$15 |~$130 |
|DynamoDB (on-demand) |~$2 |~$5 |~$10 |
|S3 / Secrets / CloudWatch |~$6 (shared) |~$9 |~$18 |
|Step Functions / SES |~$1 |~$1 |~$2 |
|ElevenLabs (test minutes) |~$10 |~$20 |~$440 |
|Per-env subtotal |~$40 |~$85 |~$640 

 

Lean total across all three environments: ~$765/mo (vs ~$640 prod-only, ~+20%) 

## Cost-Control Levers 

In priority order — biggest impact first: 

- ElevenLabs is the lever, not AWS. Cap interview length, push the chat path (no per-minute voice), negotiate committed pricing. Halving voice minutes saves more than the entire AWS bill. 

- Tiered Claude on Bedrock: Haiku for interview turns, Sonnet only for the final report — cuts Bedrock spend 40–60%. 

- Scale-to-zero compute: Lambda + API Gateway + DynamoDB on-demand; avoid always-on (Aurora min ACUs, NAT GW) unless required. 

- Single region: Cross-region for DR only if mandated — avoid premature multi-region. 

- EDP/Private Pricing discounts + Savings Plans on steady compute. 

- Don't add Shield Advanced per app. It's org-wide at ~$3,000/mo and likely already in place. 