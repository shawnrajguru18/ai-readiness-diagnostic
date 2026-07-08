#!/usr/bin/env bash
# Build the container, push to ECR, and create-or-update the App Runner service.
# Repeatable — run this for every deploy. Requires ./01-bootstrap.sh to have run once.
#
# Prereqs: aws CLI v2 (authenticated) + Docker running locally.
set -euo pipefail
cd "$(dirname "$0")"
source ./config.sh
REPO_ROOT="$(cd ../.. && pwd)"

echo "==> Docker login to ECR"
aws ecr get-login-password --region "${AWS_REGION}" | \
  docker login --username AWS --password-stdin "${ECR_REGISTRY}"

echo "==> Build image (${IMAGE_URI})"
docker build -t "${IMAGE_URI}" "${REPO_ROOT}"

echo "==> Push image"
docker push "${IMAGE_URI}"

# Source config shared by create and update (App Runner reads the app's env here).
# Credentials resolved from IAM instance role (SigV4 auth for Bedrock + DynamoDB).
SRC_CONFIG=$(cat <<JSON
{
  "AuthenticationConfiguration": {"AccessRoleArn": "${ACCESS_ROLE_ARN}"},
  "AutoDeploymentsEnabled": true,
  "ImageRepository": {
    "ImageIdentifier": "${IMAGE_URI}",
    "ImageRepositoryType": "ECR",
    "ImageConfiguration": {
      "Port": "8080",
      "RuntimeEnvironmentVariables": {"AIDIAG_DDB_TABLE": "${DDB_TABLE}", "AWS_REGION": "${AWS_REGION}"}
    }
  }
}
JSON
)
INSTANCE_CONFIG=$(cat <<JSON
{"Cpu": "${APP_CPU}", "Memory": "${APP_MEMORY}", "InstanceRoleArn": "${INSTANCE_ROLE_ARN}"}
JSON
)
HEALTH_CONFIG='{"Protocol":"HTTP","Path":"/","Interval":10,"Timeout":5,"HealthyThreshold":1,"UnhealthyThreshold":5}'

SERVICE_ARN="$(aws apprunner list-services --region "${AWS_REGION}" \
  --query "ServiceSummaryList[?ServiceName=='${APP_NAME}'].ServiceArn | [0]" --output text)"

if [ "${SERVICE_ARN}" = "None" ] || [ -z "${SERVICE_ARN}" ]; then
  echo "==> Creating App Runner service: ${APP_NAME}"
  SERVICE_ARN="$(aws apprunner create-service --region "${AWS_REGION}" \
    --service-name "${APP_NAME}" \
    --source-configuration "${SRC_CONFIG}" \
    --instance-configuration "${INSTANCE_CONFIG}" \
    --health-check-configuration "${HEALTH_CONFIG}" \
    --query 'Service.ServiceArn' --output text)"
else
  echo "==> Updating App Runner service: ${APP_NAME}"
  aws apprunner update-service --region "${AWS_REGION}" \
    --service-arn "${SERVICE_ARN}" \
    --source-configuration "${SRC_CONFIG}" \
    --instance-configuration "${INSTANCE_CONFIG}" \
    --health-check-configuration "${HEALTH_CONFIG}" >/dev/null
fi

echo "==> Waiting for service to reach RUNNING (this can take a few minutes)"
while true; do
  STATUS="$(aws apprunner describe-service --region "${AWS_REGION}" --service-arn "${SERVICE_ARN}" --query 'Service.Status' --output text)"
  echo "    status=${STATUS}"
  case "${STATUS}" in
    RUNNING) break ;;
    CREATE_FAILED|DELETE_FAILED|PAUSED) echo "Service in ${STATUS}; check the App Runner console."; exit 1 ;;
  esac
  sleep 15
done

URL="$(aws apprunner describe-service --region "${AWS_REGION}" --service-arn "${SERVICE_ARN}" --query 'Service.ServiceUrl' --output text)"
echo
echo "Deployed. App URL: https://${URL}"
