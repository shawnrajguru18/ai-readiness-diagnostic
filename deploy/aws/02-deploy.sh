#!/usr/bin/env bash
# Build the container, push to ECR, and create-or-update the ECS Express Mode service.
# Repeatable — run this for every deploy. Requires ./01-bootstrap.sh to have run once.
#
# Prereqs: aws CLI v2 (authenticated) + Docker running locally.
set -euo pipefail
cd "$(dirname "$0")"
source ./config.sh
REPO_ROOT="$(cd ../.. && pwd)"

get_default_subnet() {
  aws ec2 describe-subnets --region "${AWS_REGION}" \
    --filters "Name=default-for-az,Values=true" \
    --query 'Subnets[0].SubnetId' --output text
}

get_default_sg() {
  aws ec2 describe-security-groups --region "${AWS_REGION}" \
    --filters "Name=group-name,Values=default" \
    --query 'SecurityGroups[0].GroupId' --output text
}

echo "==> Docker login to ECR"
aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${ECR_REGISTRY}"

echo "==> Build image (${IMAGE_URI})"
docker build -t "${IMAGE_URI}" "${REPO_ROOT}"

echo "==> Push image"
docker push "${IMAGE_URI}"

echo "==> Register task definition"
TASK_DEF_JSON=$(cat <<EOF
{
  "family": "${APP_NAME}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "${TASK_CPU}",
  "memory": "${TASK_MEMORY}",
  "containerDefinitions": [
    {
      "name": "${APP_NAME}",
      "image": "${IMAGE_URI}",
      "portMappings": [{"containerPort": 8080, "hostPort": 8080, "protocol": "tcp"}],
      "environment": [
        {"name": "AIDIAG_DDB_TABLE", "value": "${DDB_TABLE}"},
        {"name": "AWS_REGION", "value": "${AWS_REGION}"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${APP_NAME}",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ],
  "taskRoleArn": "${TASK_ROLE_ARN}",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole"
}
EOF
)

TASK_DEF_ARN="$(aws ecs register-task-definition \
  --region "${AWS_REGION}" \
  --cli-input-json "${TASK_DEF_JSON}" \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)"
echo "    ${TASK_DEF_ARN}"

echo "==> Create CloudWatch log group"
aws logs create-log-group --log-group-name "/ecs/${APP_NAME}" --region "${AWS_REGION}" 2>/dev/null || true

echo "==> Create or update ECS service (Express Mode)"
SERVICE_EXISTS=$(aws ecs describe-services --region "${AWS_REGION}" \
  --cluster "${CLUSTER_NAME}" --services "${APP_NAME}" \
  --query 'services[0].serviceName' --output text 2>/dev/null || echo "")

if [ -z "${SERVICE_EXISTS}" ] || [ "${SERVICE_EXISTS}" = "None" ]; then
  echo "    Creating new service..."
  aws ecs create-service --region "${AWS_REGION}" \
    --cluster "${CLUSTER_NAME}" \
    --service-name "${APP_NAME}" \
    --task-definition "${TASK_DEF_ARN}" \
    --desired-count "${TASK_COUNT}" \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={assignPublicIp=ENABLED,subnets=[$(get_default_subnet)],securityGroups=[$(get_default_sg)]}" \
    --enable-execute-command >/dev/null
else
  echo "    Updating existing service..."
  aws ecs update-service --region "${AWS_REGION}" \
    --cluster "${CLUSTER_NAME}" \
    --service "${APP_NAME}" \
    --task-definition "${TASK_DEF_ARN}" \
    --force-new-deployment >/dev/null
fi

echo "==> Waiting for service to stabilize (this can take a few minutes)"
aws ecs wait services-stable --region "${AWS_REGION}" \
  --cluster "${CLUSTER_NAME}" \
  --services "${APP_NAME}"

echo "==> Get service details"
SERVICE_DETAILS=$(aws ecs describe-services --region "${AWS_REGION}" \
  --cluster "${CLUSTER_NAME}" --services "${APP_NAME}" \
  --query 'services[0]')

RUNNING_COUNT=$(echo "${SERVICE_DETAILS}" | jq '.runningCount')
DESIRED_COUNT=$(echo "${SERVICE_DETAILS}" | jq '.desiredCount')

echo "    running tasks: ${RUNNING_COUNT}/${DESIRED_COUNT}"

if [ "${RUNNING_COUNT}" -gt 0 ]; then
  TASK_ARN=$(echo "${SERVICE_DETAILS}" | jq -r '.taskDefinition' | rev | cut -d'/' -f1 | rev)
  TASK_ID=$(aws ecs list-tasks --region "${AWS_REGION}" \
    --cluster "${CLUSTER_NAME}" \
    --service-name "${APP_NAME}" \
    --query 'taskArns[0]' --output text | rev | cut -d'/' -f1 | rev)

  TASK_INFO=$(aws ecs describe-tasks --region "${AWS_REGION}" \
    --cluster "${CLUSTER_NAME}" \
    --tasks "${TASK_ID}" \
    --query 'tasks[0].attachments[0].details' --output json)

  IP=$(echo "${TASK_INFO}" | jq -r '.[] | select(.name=="networkInterfaceId") | .value' 2>/dev/null || echo "")
  if [ -z "${IP}" ]; then
    ENI=$(echo "${TASK_INFO}" | jq -r '.[] | select(.name=="networkInterfaceId") | .value' 2>/dev/null)
    if [ -n "${ENI}" ]; then
      IP=$(aws ec2 describe-network-interfaces --region "${AWS_REGION}" \
        --network-interface-ids "${ENI}" --query 'NetworkInterfaces[0].Association.PublicIp' --output text 2>/dev/null || echo "")
    fi
  fi

  if [ -n "${IP}" ] && [ "${IP}" != "None" ] && [ "${IP}" != "" ]; then
    echo
    echo "Deployed successfully!"
    echo "  App URL: http://${IP}:8080"
    echo "  (Note: task may still be initializing; check logs if not responding)"
    echo
    echo "To view logs:"
    echo "  aws logs tail /ecs/${APP_NAME} --follow --region ${AWS_REGION}"
  else
    echo
    echo "Deployed to ECS cluster ${CLUSTER_NAME}, service ${APP_NAME}"
    echo "Task is starting (may take 1-2 minutes)."
    echo "Check the ECS console for the service IP once the task is running."
  fi
else
  echo "WARNING: No tasks are running. Check the ECS console for errors."
  exit 1
fi
