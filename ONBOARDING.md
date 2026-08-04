# DXC AI Readiness Diagnostic MVP — Developer Onboarding

Welcome! This guide will get you up to speed on the AI Readiness Diagnostic platform. Read this end-to-end first (~20 minutes), then use it as reference as you work.

---

## Quick Start (TL;DR)

**Live app:** `https://ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com`

**Local dev:**
```bash
# Backend (Python 3.12+)
cd app
pip install -r requirements.txt
python -m uvicorn app.api:app --reload

# Frontend (Node 18+, in another terminal)
cd web
npm install
npm run dev
```

**Deploy:**
```bash
# Build Docker image
docker build -t ai-readiness-diagnostic:latest .

# Push to ECR (Bash, not PowerShell)
docker tag ai-readiness-diagnostic:latest 023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest
docker push ...

# Force ECS redeploy
aws ecs update-service --cluster ai-readiness-diagnostic-cluster --service ai-readiness-diagnostic-service --force-new-deployment --region us-east-1
```

---

## 📋 Project Overview

**What it does:**
- Comprehensive AI readiness assessment for enterprises
- Two interview modes: chat and voice
- LLM-scored dimensions (6 dimensions, 0-100 scale)
- Generates personalized executive narrative
- Stores assessments for partner review

**Current status (Aug 4, 2026):**
- ✅ Voice interview end-to-end working (ElevenLabs integration)
- ✅ LLM scoring active (Claude Opus via Bedrock)
- ✅ Executive narrative generation working
- ✅ Frontend error handling fixed
- ✅ 504 timeout issues resolved
- ✅ Deployed on AWS (ECS + ALB + HTTPS)

**Key metrics:**
- Voice assessment: ~85 seconds (LLM processing)
- 11 questions per interview
- 6 AI readiness dimensions scored
- Scorecard includes findings, quick wins, and strategic roadmap

---

## 🛠 Tech Stack

**Backend:**
- Python 3.12 (FastAPI)
- AWS Bedrock (Claude Opus + Sonnet)
- Pydantic models for validation
- SQLite for storage (in-memory in dev, file-based in production)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- ElevenLabs voice agent widget (embedded from unpkg)

**Infrastructure:**
- AWS ECS Fargate (1 task, 1024 CPU, 2048 MB)
- Application Load Balancer (ALB) with HTTPS
- Self-signed certificate (for microphone access)
- Docker multi-stage build

**Integrations:**
- ElevenLabs voice agent (`agent_0501kz1wxj5pfe39krrt9nbej8mr`)
- AWS Bedrock for LLM
- AWS IAM for authentication

---

## 🏗 Architecture

### Request Flow

```
User → ALB (HTTPS) → ECS Task → FastAPI Backend
                          ↓
                     Python Pipeline
                     (A2→C2→C3→C4→D2)
                          ↓
                    Claude Opus LLM
                          ↓
                      Scorecard JSON
                          ↓
                       Storage (SQLite)
```

### Directory Structure

```
.
├── app/                          # Backend (Python)
│   ├── api.py                    # FastAPI routes (/api/assess, /api/questions, etc.)
│   ├── agents/__init__.py        # LLM agents (A2 persona, C2 synthesis, C4 narrative, etc.)
│   ├── orchestrator.py           # run_pipeline() - orchestrates scoring
│   ├── llm.py                    # Bedrock LLM client wrapper
│   ├── models.py                 # Pydantic schemas (Session, Scorecard, DimensionScore, etc.)
│   ├── config.py                 # Settings & credential resolution
│   ├── content/                  # Question pool, fixtures, scoring rules
│   ├── scoring.py                # Deterministic scoring (fallback when LLM unavailable)
│   ├── benchmarks.py             # Peer benchmarks by industry
│   └── pdf.py                    # PDF generation (scorecards, quick wins, etc.)
│
├── web/                          # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx               # Main app component, state management
│   │   ├── constants.ts          # API endpoint, ElevenLabs agent ID, demo scorecard
│   │   ├── types.ts              # TypeScript interfaces
│   │   └── screens/
│   │       ├── Landing.tsx       # Welcome screen
│   │       ├── Assessment.tsx    # Chat interview
│   │       ├── VoiceInterview.tsx # Voice interview (ElevenLabs widget)
│   │       ├── Submitted.tsx     # Submitted, waiting for results
│   │       ├── Scorecard.tsx     # Results display
│   │       └── QuickWins.tsx     # Quick wins recommendations
│   ├── dist/                     # Built React app (served by FastAPI)
│   ├── package.json              # Dependencies
│   └── vite.config.ts            # Vite build config
│
├── Dockerfile                    # Multi-stage build (Node → Python)
├── requirements.txt              # Python dependencies
├── terraform/                    # AWS infrastructure (ECS, ALB, security groups)
└── content/                      # Question pool, fixtures, scoring tables
```

---

## 🔑 Key Files to Understand

### Backend

**`app/api.py` — FastAPI routes**
- `POST /api/assess` — Main assessment endpoint (accepts responses or voice_responses)
- `GET /api/questions` — Load question pool
- `GET /api/scorecard/{id}/pdf` — Generate PDF report

**`app/orchestrator.py` — Pipeline orchestration**
```python
def run_pipeline(session, voice_responses=None):
    # A2: Persona inference
    # C2: Synthesis (findings, recommendations)
    # C3: Quick wins
    # C4: Executive narrative (5 paragraphs)
    # D2: Validation
```

**`app/agents/__init__.py` — LLM agents**
- `a2_persona()` — Infer persona from submission
- `c2_synthesis()` — Generate findings & recommendations
- `c3_quick_wins()` — Select 3 strategic quick wins
- `c4_narrative()` — Generate 5-paragraph executive summary
- `d2_validate()` — Check for data quality issues
- `score_from_voice()` — **LLM-based voice scoring** (uses threading timeout)

**`app/models.py` — Data schemas**
- `Session` — Full assessment session
- `Scorecard` — Final results
- `DimensionScore` — One dimension (score 0-100, tier, reasoning)

### Frontend

**`web/src/App.tsx` — State & routing**
- Manages screen transitions (landing → assessment → scorecard)
- `submitVoice()` — POST voice answers to backend, show error alerts
- `submit()` — POST chat answers to backend
- Error handling: now shows actual backend errors, not just demo fallback

**`web/src/screens/VoiceInterview.tsx` — ElevenLabs widget**
- Loads widget from unpkg.com
- Listens to `elevenlabs-convai:call` events (tool callbacks from agent)
- Stores answers with question text as key
- `finish_interview()` calls `submitVoice()` with all answers

**`web/src/constants.ts` — Configuration**
- `API = ''` — Empty string = same-origin requests (production)
- `ELEVENLABS_AGENT_ID = 'agent_0501kz1wxj5pfe39krrt9nbej8mr'`
- `DEMO_SCORECARD` — Template shown when no real assessment

---

## 🚀 Deploying Changes

### Local Development

```bash
# Backend changes
cd app && python -m uvicorn app.api:app --reload

# Frontend changes
cd web && npm run dev
# Vite watches for changes and hot-reloads

# IMPORTANT: If TypeScript constants change, clear cache:
rm -rf web/.vite web/node_modules/.vite web/dist
pkill -9 node
npm run dev
```

### Building Docker Image

```bash
docker build -t ai-readiness-diagnostic:latest .
# Multi-stage build:
# Stage 1: Node → builds React app (web/dist/)
# Stage 2: Python → copies dist/ + app code → runs uvicorn
```

### Deploying Code Changes (to existing infrastructure)

**IMPORTANT: Use Bash, not PowerShell** (ForceMFA policy blocks PowerShell docker login)

```bash
# 1. Build
docker build -t ai-readiness-diagnostic:latest .

# 2. Push to ECR (use Bash!)
ACCOUNT="023138541872"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag ai-readiness-diagnostic:latest $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest
docker push $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest

# 3. Force ECS redeploy
aws ecs update-service --cluster ai-readiness-diagnostic-cluster --service ai-readiness-diagnostic-service --force-new-deployment --region us-east-1

# 4. Wait 30 seconds for new task to start

# 5. Get new task IP
TASK=$(aws ecs list-tasks --cluster ai-readiness-diagnostic-cluster --service-name ai-readiness-diagnostic-service --region us-east-1 --query 'taskArns[0]' --output text)
NEW_IP=$(aws ecs describe-tasks --cluster ai-readiness-diagnostic-cluster --tasks $TASK --region us-east-1 --output json | grep -o '"privateIPv4Address": "[^"]*"' | head -1 | sed 's/"privateIPv4Address": "//;s/"$//')

# 6. Re-register ALB target
TG_ARN=$(aws elbv2 describe-target-groups --region us-east-1 --query 'TargetGroups[?TargetGroupName==`ai-readiness-targets`].TargetGroupArn' --output text)
# Deregister old targets, register new one...
aws elbv2 register-targets --target-group-arn $TG_ARN --targets Id=$NEW_IP,Port=8080 --region us-east-1

# 7. Wait 15 seconds, then test
curl -k https://ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com/ping
```

---

## 🏗 Creating Infrastructure from Scratch (Terraform)

If you need to set up a new environment or rebuild from scratch, use Terraform.

### Prerequisites
- Terraform >= 1.0 (https://www.terraform.io/downloads)
- AWS CLI v2 configured with credentials
- Docker (to build images)

### Step 1: Configure Terraform

```bash
cd terraform

# Copy example config
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values:
# - aws_region: AWS region (default: us-east-1)
# - app_name: Application name (default: ai-readiness-diagnostic)
# - container_image: ECR image URL (will update after first deploy)
# - task_cpu / task_memory: ECS task sizing
# - desired_count: Number of tasks (default: 1)
```

Example `terraform.tfvars`:
```hcl
aws_region      = "us-east-1"
app_name        = "ai-readiness-diagnostic"
environment     = "production"
container_image = "023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest"
container_port  = 8080
task_cpu        = 1024
task_memory     = 2048
desired_count   = 1
```

### Step 2: Initialize & Plan

```bash
# Initialize Terraform (downloads AWS provider)
terraform init

# Plan infrastructure
terraform plan -out=tfplan

# Review the output — this shows what will be created
```

### Step 3: Apply Infrastructure

```bash
# Create all resources
terraform apply tfplan

# This creates:
# - ECR repository (for Docker images)
# - ECS Fargate cluster & service (runs containerized app)
# - DynamoDB table (session storage)
# - IAM roles (for ECS task permissions)
# - CloudWatch log group (backend logs)
# - Security groups (networking)
# - Application Load Balancer (HTTPS, routing)
```

**Save the outputs:**
```bash
terraform output
# Note: ecr_repository_url, alb_dns_name, etc.
```

### Step 4: Push Docker Image to ECR

```bash
# Build Docker image
docker build -t ai-readiness-diagnostic:latest .

# Login to ECR (use Bash!)
ACCOUNT="023138541872"
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker tag ai-readiness-diagnostic:latest $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest
docker push $ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest
```

### Step 5: Verify

```bash
# Check ECS service is running
aws ecs describe-services --cluster ai-readiness-diagnostic-cluster \
  --services ai-readiness-diagnostic-service --region us-east-1

# Test app (may take 1-2 minutes to start)
ALB_DNS=$(terraform output -raw alb_dns_name)
curl -k https://$ALB_DNS/ping
```

---

## 💣 Destroying Infrastructure (Teardown)

**IMPORTANT: This deletes everything permanently (ECS, DynamoDB, ECR, etc.).**

```bash
cd terraform

# Show what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy

# Confirm when prompted (type 'yes')
```

**What gets deleted:**
- ECS cluster, service, tasks
- DynamoDB table (all session data)
- ECR repository (all Docker images)
- Application Load Balancer & listeners
- IAM roles & policies
- CloudWatch log group
- Security groups
- VPC resources (if created by Terraform)

**After teardown:**
```bash
# State is updated
git status  # terraform.tfstate will show changes

# Optional: Commit the destroyed state
git add terraform.tfstate terraform.tfstate.backup
git commit -m "Destroy infrastructure"
```

---

## 🔄 Updating Infrastructure

If you need to change infrastructure (scale up, change instance type, etc.):

```bash
cd terraform

# Edit terraform.tfvars (e.g., change task_cpu or desired_count)
vim terraform.tfvars

# Plan the changes
terraform plan -out=tfplan

# Apply the changes
terraform apply tfplan
```

Common changes:
```hcl
# Scale up ECS tasks
desired_count = 3  # instead of 1

# Increase resources
task_cpu    = 2048  # instead of 1024
task_memory = 4096  # instead of 2048

# Enable auto-scaling
enable_autoscaling = true
min_capacity       = 1
max_capacity       = 5
```

---

## 🔐 AWS Permissions Required

The user running Terraform needs these IAM permissions:
- `ecs:*` (ECS cluster, service, tasks)
- `ec2:*` (VPC, security groups, ENI)
- `dynamodb:*` (DynamoDB table)
- `ecr:*` (ECR repository)
- `iam:*` (IAM roles, policies)
- `logs:*` (CloudWatch logs)
- `elasticloadbalancing:*` (ALB)
- `acm:*` (SSL certificates)

**Current setup:** Uses ForceMFA policy (requires MFA for console access, but allows programmatic access via AWS CLI)

---

## ⚠️ Known Gotchas & Lessons Learned

### 1. **Fargate IPs Change on Every Redeploy**
- Every `force-new-deployment` creates a new task with a new private IP
- **Always re-register the ALB target after redeploy**
- Old target becomes unhealthy (502 errors)
- Solution: Get new IP, deregister old, register new

### 2. **Vite Cache Persistence**
- TypeScript constant changes (like API endpoint) don't pick up with simple dev restart
- **Solution:** `rm -rf web/.vite web/node_modules/.vite web/dist && pkill -9 node && npm run dev`
- This is a major time-waster; remember to clear it

### 3. **PowerShell vs Bash for Docker ECR**
- PowerShell `docker login` with ForceMFA policy returns 400 Bad Request
- **Always use Bash shell** for docker login/push
- Bash works immediately with the same credentials

### 4. **LLM Calls Can Be Slow**
- Voice assessment LLM calls take ~85 seconds
- If >45 seconds, falls back to default scores (threading timeout)
- ALB timeout is 120 seconds (enough headroom)
- If LLM is slow, consider prompt optimization or async processing

### 5. **Frontend Silent Errors**
- Previous bug: frontend caught ALL errors and showed demo scorecard
- Users had no idea what went wrong
- **Fix:** Always check HTTP status and backend error field before showing demo
- Add user-facing alerts for failures

### 6. **ALB Requires Multiple Subnets**
- "At least two subnets in two different Availability Zones must be specified"
- Use: `subnet-0ddf59a346e5b8004` (us-east-1c) + `subnet-0358e930fb37cdc52` (us-east-1e)

### 7. **Container Gets Stuck**
- If all endpoints return 504, container may be hung (not crashed)
- `docker logs` won't show the issue
- **Solution:** Restart service completely (desired-count 0→1), don't just redeploy

---

## 🔐 Authentication & Credentials

### AWS Bedrock (LLM)
- **No API key needed** — Uses IAM SigV4 auth
- Credentials auto-resolved via boto3 (env vars, IAM role, credential files)
- ECS task has IAM role with Bedrock permissions
- Environment variables: `AWS_REGION` (default: us-east-1)

### ElevenLabs Voice Agent
- **No API key in code** — Agent ID is public (`agent_0501kz1wxj5pfe39krrt9nbej8mr`)
- Agent must be set to "Public" in ElevenLabs dashboard
- Frontend loads widget from unpkg.com, all communication via browser
- Tool callbacks go to your app's `/api/assess` endpoint

### Anthropic API (not currently used)
- Optional `ANTHROPIC_API_KEY` env var
- Currently using Bedrock instead
- If needed, set env var and update `app/llm.py`

### Secrets Management
- **NO secrets in repo** — .env is in .gitignore
- All credentials come from environment
- Safe to commit to GitHub

---

## 📊 Assessment Flow

### Chat Interview Path
1. User fills out form (company, role, industry)
2. User answers 10 questions (multiple choice + scale)
3. POST `/api/assess` with `responses` dict
4. Backend runs deterministic scoring (from response mappings)
5. Backend runs full pipeline (A2→C2→C3→C4→D2)
6. Returns scorecard with scores, findings, narrative

### Voice Interview Path
1. User fills out form (same as chat)
2. ElevenLabs agent asks 10 questions, user speaks answers
3. Agent's tool callbacks capture answers in React state
4. User clicks "Submit"
5. POST `/api/assess` with `voice_responses` dict (question → answer text)
6. Backend calls `score_from_voice()` which uses LLM to score
7. LLM analyzes open-ended answers, returns dimension scores
8. Rest of pipeline runs (C2→C3→C4→D2)
9. Returns scorecard with LLM-scored dimensions

### Scoring Dimensions
1. **Data Foundation** — Data accessibility & quality
2. **Governance & Risk** — AI governance maturity
3. **AI Investment Maturity** — Budget & deployment
4. **Organizational Change Readiness** — Change management
5. **Value-Pocket Clarity** — Use case clarity
6. **Regulatory Complexity** — Regulatory exposure (informational)

Each dimension: 0-100 score + tier (Emerging/Developing/Established/Leading) + reasoning

---

## 🐛 Debugging Tips

### Check Backend Logs
```bash
# CloudWatch (may be blocked by ForceMFA)
aws logs tail /ecs/ai-readiness-diagnostic-cluster/ai-readiness-diagnostic-service --since 10m

# Or check ECS task logs directly
aws ecs describe-tasks --cluster ai-readiness-diagnostic-cluster --tasks $TASK --region us-east-1
```

### Check Frontend Errors
- Open browser DevTools (F12)
- Look for `[App]`, `[submitVoice]`, `[Voice]` console logs
- Check network tab for 504/502/400 responses
- Look for error alerts

### Test Backend Endpoints
```bash
curl -k https://ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com/ping
curl -k https://ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com/api/debug
curl -k https://ai-readiness-alb-751626769.us-east-1.elb.amazonaws.com/api/questions
```

### Test Local Backend
```bash
python -m uvicorn app.api:app --reload
curl http://localhost:8000/ping
curl http://localhost:8000/api/debug
```

---

## 📚 Git Workflow

**Three remotes:**
- `origin` — GitHub personal (`https://github.com/shawnrajguru18/ai-readiness-diagnostic.git`)
- `partner` — DXC internal (`https://partner-github.dxc.com/srajguru/ai-readiness-diagnostic.git`)
- `samprimex` — SAM Prime X (`https://partner-github.dxc.com/SAM-Prime-X/ai-readiness-diagnostic.git`)

**Push to all three:**
```bash
git push origin main
git push partner main
git push samprimex main
```

---

## 🎯 Next Steps

1. **Clone & run locally** — Get the dev server working
2. **Read `app/orchestrator.py`** — Understand the pipeline
3. **Read `app/agents/__init__.py`** — Understand LLM agents
4. **Read `web/src/App.tsx`** — Understand frontend state management
5. **Test chat interview** — Verify deterministic scoring works
6. **Test voice interview** — Verify ElevenLabs integration works
7. **Check CloudWatch logs** — Understand what's happening on the backend
8. **Deploy a test change** — Practice the full deploy workflow

---

## 📞 Questions?

Key people to ask:
- **Shawn Rajguru** (shawn.rajguru@dxc.com) — Project owner, knows all the history

Key documentation:
- `MEMORY.md` — Project history & important lessons
- This file — Technical onboarding
- Code comments — Inline documentation
- Git log — See what changed and why (`git log --oneline`)

---

**Good luck! The app is production-ready. Focus on understanding the pipeline and the gotchas above.**
