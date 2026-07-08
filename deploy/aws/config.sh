#!/usr/bin/env bash
# Shared configuration for the ECS Express Mode deploy scripts.
# Override any value by exporting it before running the scripts, e.g.:
#   AWS_REGION=us-west-2 APP_NAME=ai-readiness ./01-bootstrap.sh
set -euo pipefail

# --- tunables ---------------------------------------------------------------
export AWS_REGION="${AWS_REGION:-us-east-1}"
export APP_NAME="${APP_NAME:-ai-readiness-diagnostic}"   # ECR repo + ECS service name
export CLUSTER_NAME="${CLUSTER_NAME:-ai-readiness-cluster}"  # ECS cluster name
export DDB_TABLE="${DDB_TABLE:-ai-readiness-sessions}"    # DynamoDB table (session store)
export IMAGE_TAG="${IMAGE_TAG:-latest}"
export TASK_CPU="${TASK_CPU:-1024}"      # 1 vCPU (256, 512, 1024, 2048, 4096)
export TASK_MEMORY="${TASK_MEMORY:-2048}" # 2 GB (512, 1024, 2048, 3072, 4096, 5120, 6144, 7168, 8192)
export TASK_COUNT="${TASK_COUNT:-1}"     # desired task count

# --- derived (do not edit) --------------------------------------------------
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export ACCOUNT_ID
export ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
export ECR_URI="${ECR_REGISTRY}/${APP_NAME}"
export IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"
export TASK_ROLE_NAME="${APP_NAME}-task-role"
export TASK_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${TASK_ROLE_NAME}"
export TABLE_ARN="arn:aws:dynamodb:${AWS_REGION}:${ACCOUNT_ID}:table/${DDB_TABLE}"

echo "account=${ACCOUNT_ID} region=${AWS_REGION} cluster=${CLUSTER_NAME} app=${APP_NAME}" >&2
