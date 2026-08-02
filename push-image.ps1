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
