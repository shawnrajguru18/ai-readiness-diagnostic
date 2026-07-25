# AWS Deployment Guide

Production deployment of the UI to AWS with FastAPI backend.

## Build Output

```
dist/
├── index.html              (0.47 KB)
├── assets/
│   ├── index-D6tmswAh.js   (181.55 KB → 57.58 KB gzipped)
│   └── index-lHNj7Csa.css  (14.68 KB → 3.84 KB gzipped)
```

**Total size:** ~196 KB uncompressed, ~62 KB gzipped

## Deployment Architecture

```
┌─────────────┐
│   FastAPI   │  /api/questions, /api/assess
│  (Python)   │
└──────┬──────┘
       │
       │ API calls
       │
┌──────▼──────────────────────┐
│   CloudFront (optional)      │
│   CDN + Caching              │
└──────┬──────────────────────┘
       │
       │ Static files
       │
┌──────▼────────────┐
│   S3 Bucket       │
│  (dist/ contents) │
└───────────────────┘
```

## Option 1: Serve from FastAPI (Simplest)

### Setup

Update FastAPI app to serve the built dist/ folder:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# API endpoints
@app.get("/api/questions")
async def get_questions():
    # Your implementation
    return {"questions": [...], "dimensions": {...}}

@app.post("/api/assess")
async def assess(request: dict):
    # Your implementation
    return scorecard

# Serve static files
# Important: StaticFiles with html=True serves index.html for unknown routes (SPA routing)
app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
```

### Deploy

```bash
# Copy dist/ to FastAPI directory
cp -r web/dist /path/to/fastapi/app/

# Run FastAPI with Gunicorn
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Test Locally

```bash
# Terminal 1: Start FastAPI
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Test API endpoint
curl http://localhost:8000/api/questions

# Browser: Navigate to
http://localhost:8000/
```

---

## Option 2: AWS S3 + CloudFront (Scalable)

### Step 1: Create S3 Bucket

```bash
# Create bucket
aws s3api create-bucket \
  --bucket ai-readiness-diagnostic-ui \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ai-readiness-diagnostic-ui \
  --versioning-configuration Status=Enabled

# Configure static website hosting
aws s3api put-bucket-website \
  --bucket ai-readiness-diagnostic-ui \
  --website-configuration '{
    "IndexDocument": {
      "Suffix": "index.html"
    },
    "ErrorDocument": {
      "Key": "index.html"
    }
  }'
```

### Step 2: Upload dist/ to S3

```bash
# Sync dist/ folder to S3 (with caching headers)
aws s3 sync web/dist/ s3://ai-readiness-diagnostic-ui/ \
  --delete \
  --cache-control "max-age=3600" \
  --exclude "index.html"

# Upload index.html with no cache (to ensure updates are seen)
aws s3 cp web/dist/index.html s3://ai-readiness-diagnostic-ui/index.html \
  --cache-control "max-age=0, must-revalidate" \
  --content-type "text/html"
```

### Step 3: Create CloudFront Distribution

```bash
# Create distribution with S3 origin
aws cloudfront create-distribution \
  --origin-domain-name ai-readiness-diagnostic-ui.s3.amazonaws.com \
  --default-root-object index.html \
  --default-cache-behavior '{
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "TargetOriginId": "S3Origin"
  }'
```

### Step 4: Configure Cache Behavior

CloudFront cache policy settings:

```
Assets (*.js, *.css):
  - TTL: 31536000 seconds (1 year)
  - Reason: Hashed filenames (e.g., index-D6tmswAh.js)
  - CloudFront automatically invalidates on new builds

index.html:
  - TTL: 0 (no cache)
  - Cache-Control: max-age=0, must-revalidate
  - Reason: Always get latest version
```

### Step 5: Configure API Routing

The FastAPI backend must be on the same domain or have CORS configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Or use CloudFront behaviors to proxy API calls to FastAPI:

```bash
# Behavior 1: /api/* → FastAPI backend (no caching)
Path Pattern: /api/*
Origin: api.yourdomain.com (FastAPI)
Cache Policy: Managed-CachingDisabled

# Behavior 2: /* → S3 (cache everything)
Path Pattern: Default
Origin: S3
Cache Policy: Managed-CachingOptimized
```

---

## Option 3: ECS + Fargate (Full AWS)

Deploy the entire stack (FastAPI + UI) to ECS Fargate.

### Dockerfile

```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY web/package*.json ./
RUN npm install
COPY web/src ./src
COPY web/*.* ./
RUN npm run build

FROM python:3.10
WORKDIR /app
COPY app app/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --from=builder /app/dist /app/web/dist
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy with Terraform

```bash
cd terraform
terraform plan -var="container_image=your-ecr-image:latest"
terraform apply
```

---

## Verification Checklist

### Local Testing

- [ ] `npm run build` succeeds with no errors
- [ ] `dist/` folder contains index.html + assets/
- [ ] No TypeScript errors in build output

### S3 Upload

- [ ] `aws s3 ls s3://ai-readiness-diagnostic-ui/` shows files
- [ ] Files are readable (check bucket policy)
- [ ] `index.html` has correct Cache-Control header

### CloudFront

- [ ] Distribution status is "Deployed"
- [ ] Domain name: d1234.cloudfront.net
- [ ] SSL certificate is valid (HTTPS)

### API Integration

- [ ] `/api/questions` endpoint returns 200 OK
- [ ] `/api/assess` endpoint returns scorecard data
- [ ] No CORS errors in browser console
- [ ] Network requests go to correct domain

### User Experience

- [ ] App loads at CloudFront URL
- [ ] Landing page renders correctly
- [ ] Can submit form and navigate to assessment
- [ ] Can submit assessment and see scorecard
- [ ] No 404 errors for assets
- [ ] Page load time < 3 seconds

---

## Monitoring & Maintenance

### CloudWatch

```bash
# View CloudFront metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name BytesDownloaded \
  --dimensions Name=DistributionId,Value=YOUR_DIST_ID \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

### Update Deployment

After code changes:

```bash
# 1. Build
npm run build

# 2. Upload to S3
aws s3 sync web/dist/ s3://ai-readiness-diagnostic-ui/ --delete

# 3. Invalidate CloudFront cache (optional - happens automatically for hashed files)
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/index.html" "/*"

# 4. Verify
# Wait ~60 seconds for invalidation, then refresh browser
```

### Rollback

```bash
# S3 has versioning enabled, so you can revert:
aws s3api list-object-versions \
  --bucket ai-readiness-diagnostic-ui

aws s3api get-object \
  --bucket ai-readiness-diagnostic-ui \
  --key index.html \
  --version-id PREVIOUS_VERSION_ID \
  index.html
```

---

## Estimated Costs (AWS)

- **S3 Storage**: ~1 MB = ~$0.02/month
- **CloudFront**: ~1 GB/month = ~$0.12/month
- **Data Transfer**: Included in CloudFront
- **Total**: ~$0.15/month

---

## Troubleshooting

### "403 Forbidden" when accessing S3

Check bucket policy:

```bash
aws s3api get-bucket-policy --bucket ai-readiness-diagnostic-ui
```

Should allow CloudFront origin access. If not, update:

```bash
aws s3api put-bucket-policy \
  --bucket ai-readiness-diagnostic-ui \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity YOUR_OAI_ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ai-readiness-diagnostic-ui/*"
    }]
  }'
```

### "CORS error" accessing API

Add CORS headers to FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://d1234.cloudfront.net"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### "404 Not Found" for routes like /assessment

Ensure `StaticFiles(html=True)` in FastAPI:

```python
app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
```

The `html=True` parameter makes non-existent routes serve `index.html` (SPA routing).

---

## Summary

| Method | Complexity | Cost | Performance |
|--------|-----------|------|-------------|
| FastAPI only | Low | $0 (free tier) | Good |
| S3 + CloudFront | Medium | ~$0.15/month | Excellent |
| ECS Fargate | High | ~$10-20/month | Excellent |

**Recommended for production:** S3 + CloudFront + FastAPI (separate domains)
- Static UI served from CloudFront (fast, cached)
- API served from FastAPI (dynamic, CORS configured)
- Best cost/performance ratio
