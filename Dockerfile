# DXC AI Readiness Diagnostic — FastAPI app (as-built, container target)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# Deps first for layer caching. reportlab/svglib/lxml ship manylinux wheels,
# so no apt build toolchain is needed on slim.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App + content/fixtures/web/logo (relative paths are resolved from repo root)
COPY . .

EXPOSE 8080

# App Runner / ECS route traffic to $PORT (defaults to 8080 here).
# Credentials (Bedrock, DynamoDB) resolved from environment or IAM instance role (SigV4).
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
