#!/usr/bin/env bash
# Shared configuration for the AWS App Runner deploy scripts.
# Override any value by exporting it before running the scripts, e.g.:
#   AWS_REGION=us-west-2 APP_NAME=ai-readiness ./01-bootstrap.sh
set -euo pipefail

# --- tunables ---------------------------------------------------------------
export AWS_REGION="${AWS_REGION:-us-east-1}"
export APP_NAME="${APP_NAME:-ai-readiness-diagnostic}"   # ECR repo + App Runner service name
export DDB_TABLE="${DDB_TABLE:-ai-readiness-sessions}"    # DynamoDB table (session store)
export IMAGE_TAG="${IMAGE_TAG:-latest}"
export APP_CPU="${APP_CPU:-1024}"      # 1 vCPU
export APP_MEMORY="${APP_MEMORY:-2048}" # 2 GB

# --- derived (do not edit) --------------------------------------------------
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export ACCOUNT_ID
export ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
export ECR_URI="${ECR_REGISTRY}/${APP_NAME}"
export IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"
export INSTANCE_ROLE_NAME="${APP_NAME}-instance-role"
export ACCESS_ROLE_NAME="${APP_NAME}-ecr-access-role"
export INSTANCE_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${INSTANCE_ROLE_NAME}"
export ACCESS_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ACCESS_ROLE_NAME}"
export TABLE_ARN="arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/${DDB_TABLE}"

echo "account=${ACCOUNT_ID} region=${AWS_REGION} app=${APP_NAME}" >&2
