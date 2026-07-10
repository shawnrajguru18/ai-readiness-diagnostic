#!/usr/bin/env bash
# Tear down all AWS infrastructure created by 01-bootstrap.sh and 02-deploy.sh
# This deletes: ECS service, cluster, DynamoDB table, ECR repo, CloudWatch logs, IAM roles
set -euo pipefail
cd "$(dirname "$0")"
source ./config.sh

echo "⚠️  WARNING: This will DELETE all infrastructure for ${APP_NAME}"
echo "   Cluster:     ${CLUSTER_NAME}"
echo "   DynamoDB:    ${DDB_TABLE}"
echo "   ECR repo:    ${APP_NAME}"
echo "   IAM role:    ${TASK_ROLE_NAME}"
echo ""
read -p "Type 'yes' to confirm deletion: " confirm
if [ "${confirm}" != "yes" ]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "==> Delete ECS service (forces task shutdown)"
aws ecs delete-service --region "${AWS_REGION}" \
  --cluster "${CLUSTER_NAME}" \
  --service "${APP_NAME}" \
  --force 2>/dev/null || echo "    (service not found or already deleted)"

echo "==> Delete ECS cluster"
aws ecs delete-cluster --region "${AWS_REGION}" \
  --cluster "${CLUSTER_NAME}" 2>/dev/null || echo "    (cluster not found or already deleted)"

echo "==> Delete CloudWatch log group"
aws logs delete-log-group --region "${AWS_REGION}" \
  --log-group-name "ecs-${APP_NAME}" 2>/dev/null || echo "    (log group not found)"

echo "==> Delete DynamoDB table"
aws dynamodb delete-table --region "${AWS_REGION}" \
  --table-name "${DDB_TABLE}" 2>/dev/null || echo "    (table not found)"

echo "==> Delete ECR repository (and all images)"
aws ecr delete-repository --region "${AWS_REGION}" \
  --repository-name "${APP_NAME}" \
  --force 2>/dev/null || echo "    (repo not found)"

echo "==> Delete IAM task role"
# First, delete all inline policies attached to the role
aws iam list-role-policies --role-name "${TASK_ROLE_NAME}" \
  --query 'PolicyNames[]' --output text 2>/dev/null | \
  while read -r policy; do
    [ -n "$policy" ] && aws iam delete-role-policy --role-name "${TASK_ROLE_NAME}" --policy-name "$policy" 2>/dev/null || true
  done

# Delete the role itself
aws iam delete-role --role-name "${TASK_ROLE_NAME}" 2>/dev/null || echo "    (role not found)"

echo ""
echo "✅ Teardown complete. All infrastructure for '${APP_NAME}' has been deleted."
echo ""
echo "Next step: Run terraform apply to deploy with Infrastructure-as-Code"
echo "  cd terraform"
echo "  terraform apply tfplan"
