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

Write-Host "MFA token acquired"
Write-Host "Deploying to ECS..."
Set-Location "terraform"
terraform apply -refresh=false -auto-approve

Write-Host "Deployment complete"
