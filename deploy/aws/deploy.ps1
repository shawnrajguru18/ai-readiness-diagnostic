#requires -Version 5.1
<#
.SYNOPSIS
  Acquire an MFA session token, then apply the terraform/ configuration.

.DESCRIPTION
  This is the Windows counterpart to the terraform/ provisioning path — NOT to 02-deploy.sh.
  02-deploy.sh deploys the shell path (ai-readiness-cluster, see config.sh); this script
  deploys the Terraform path (ai-readiness-diagnostic-*). They are not interchangeable.

  Runnable from any directory: terraform/ is resolved from this script's location.

  Note: -refresh=false is passed to terraform apply, so state is trusted as-is. That is fast,
  but it will miss drift introduced outside Terraform. Drop the flag if you suspect manual
  changes were made in the console.

.EXAMPLE
  pwsh deploy/aws/deploy.ps1
#>

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$TfDir    = Join-Path $RepoRoot 'terraform'

if (-not (Test-Path $TfDir)) {
    throw "Terraform directory not found: $TfDir"
}

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
Write-Host "Deploying to ECS via Terraform ($TfDir)..."
Set-Location $TfDir
terraform apply -refresh=false -auto-approve

Write-Host "Deployment complete"
