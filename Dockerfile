# DXC AI Readiness Diagnostic — FastAPI app with React UI (multi-stage build)

# Stage 1: Build the React UI with Node
FROM node:18-alpine AS ui-builder
WORKDIR /ui
COPY web/package*.json ./
RUN npm install --frozen-lockfile
# Copy source files needed for build
COPY web/src ./src
COPY web/tsconfig.json ./
COPY web/vite.config.ts ./
COPY web/tailwind.config.js ./
COPY web/postcss.config.js ./
COPY web/index.html ./
RUN npm run build

# Stage 2: Python FastAPI with built UI
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code + content/fixtures (FastAPI backend)
COPY app ./app
COPY content ./content

# Copy built React UI from stage 1
COPY --from=ui-builder /ui/dist ./web/dist

# Copy vendor libs and review.html for partner dashboard
COPY web/vendor ./web/vendor
COPY web/review.html ./web/review.html

# Copy DXC brand assets for PDF generation
COPY ["DXC Logo", "/app/DXC Logo"]

EXPOSE 8080

# App Runner / ECS route traffic to $PORT (defaults to 8080 here).
# Credentials (Bedrock, DynamoDB) resolved from environment or IAM instance role (SigV4).
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"]
