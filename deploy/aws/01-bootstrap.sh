#!/usr/bin/env bash
# One-time AWS setup for ECS Express Mode deployment. Idempotent — safe to re-run.
# Creates: ECR repo, DynamoDB table, ECS cluster, and IAM task role
# (task role has Bedrock + DynamoDB access; ECS task execution role created by AWS).
#
# Prereqs: aws CLI v2, authenticated (e.g. `aws sso login`) with rights to create
# ECR / DynamoDB / ECS / IAM resources and enable Bedrock model access in the target account.
set -euo pipefail
cd "$(dirname "$0")"
source ./config.sh

echo "==> ECR repository: ${APP_NAME}"
aws ecr describe-repositories --repository-names "${APP_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "${APP_NAME}" --region "${AWS_REGION}" \
    --image-scanning-configuration scanOnPush=true >/dev/null
echo "    ${ECR_URI}"

echo "==> DynamoDB table: ${DDB_TABLE} (on-demand, PK=id)"
if ! aws dynamodb describe-table --table-name "${DDB_TABLE}" --region "${AWS_REGION}" >/dev/null 2>&1; then
  aws dynamodb create-table --table-name "${DDB_TABLE}" --region "${AWS_REGION}" \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST >/dev/null
  aws dynamodb wait table-exists --table-name "${DDB_TABLE}" --region "${AWS_REGION}"
fi

echo "==> ECS cluster: ${CLUSTER_NAME} (Express Mode)"
aws ecs create-cluster --cluster-name "${CLUSTER_NAME}" --region "${AWS_REGION}" \
  --cluster-settings name=containerInsights,value=disabled >/dev/null 2>&1 || true

echo "==> IAM task role: ${TASK_ROLE_NAME} (DynamoDB + Bedrock access)"
aws iam get-role --role-name "${TASK_ROLE_NAME}" >/dev/null 2>&1 || \
  aws iam create-role --role-name "${TASK_ROLE_NAME}" \
    --assume-role-policy-document '{
      "Version":"2012-10-17",
      "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
    }' >/dev/null
aws iam put-role-policy --role-name "${TASK_ROLE_NAME}" --policy-name app-permissions \
  --policy-document "{
    \"Version\":\"2012-10-17\",
    \"Statement\":[
      {\"Effect\":\"Allow\",
       \"Action\":[\"dynamodb:GetItem\",\"dynamodb:PutItem\",\"dynamodb:UpdateItem\",\"dynamodb:DeleteItem\",\"dynamodb:Query\",\"dynamodb:Scan\"],
       \"Resource\":[\"${TABLE_ARN}\",\"${TABLE_ARN}/index/*\"]},
      {\"Effect\":\"Allow\",
       \"Action\":[\"bedrock:InvokeModel\"],
       \"Resource\":[\"arn:aws:bedrock:${AWS_REGION}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0\",\"arn:aws:bedrock:${AWS_REGION}::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0\"]}
    ]
  }" >/dev/null

echo
echo "Bootstrap complete."
echo "  ECR URI:          ${ECR_URI}"
echo "  DynamoDB table:   ${DDB_TABLE}"
echo "  ECS cluster:      ${CLUSTER_NAME}"
echo "  task role ARN:    ${TASK_ROLE_ARN}"
echo "Next: run ./02-deploy.sh"
