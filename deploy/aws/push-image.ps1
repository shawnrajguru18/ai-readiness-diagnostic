#requires -Version 5.1
<#
.SYNOPSIS
  Acquire an MFA session token, push the local image to ECR, and force an ECS redeploy.

.DESCRIPTION
  Targets the Terraform-provisioned resource set (ai-readiness-diagnostic-cluster / service).
  It does NOT build the image — run `docker build -t <ECR_URI>:latest .` (or `make docker-build`
  and tag it) first, or the push will send whatever `:latest` currently points at.

  Runnable from any directory: nothing here is path-relative.

.EXAMPLE
  pwsh deploy/aws/push-image.ps1
#>

$ErrorActionPreference = 'Stop'

$mfa_device = "arn:aws:iam::023138541872:mfa/AWS-Sandbox-Axis"
$mfa_code = Read-Host "Enter your MFA code"

Write-Host "Getting MFA session token..."
$session = aws sts get-session-token `
  --serial-number $mfa_device `
  --token-code $mfa_code `
  --duration-seconds 3600 `
  --output json | ConvertFrom-Json

$env:AWS_ACCESS_KEY_ID = $session.Credentials.AccessKeyId
$env:AWS_SECRET_ACCESS_KEY = $session.Credentials.SecretAccessKey
$env:AWS_SESSION_TOKEN = $session.Credentials.SessionToken

Write-Host "Credentials acquired, pushing to ECR..."
$ECR_URI = "023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$ECR_URI"
docker push "$ECR_URI`:latest"

Write-Host ""
Write-Host "Forcing ECS service redeploy..."
aws ecs update-service `
  --cluster ai-readiness-diagnostic-cluster `
  --service ai-readiness-diagnostic `
  --force-new-deployment `
  --region us-east-1

Write-Host "Deployment initiated!"
