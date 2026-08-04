#!/usr/bin/env bash
#
# post_destroy_validation.sh — verify AWS resources are actually gone after a teardown.
#
# READ-ONLY. Performs only describe/list/get calls. It never deletes or modifies anything.
#
# Replaces the mechanical half of the former post_destroy_validation.txt (which
# deploy/aws/destroy_terraform.sh incorrectly invoked with `bash`, since it was a prose checklist).
# The human-judgment half — billing review, backup archival, sign-off — lives in
# deploy/aws/post_destroy_validation.md.
#
# IMPORTANT: this project has two provisioning paths that name resources differently:
#   deploy/aws/config.sh  ->  ai-readiness-cluster        / ai-readiness-sessions
#   terraform/            ->  ai-readiness-diagnostic-cluster / ...-sessions
# Both name sets are checked. A resource surviving under either name is a FAIL, because
# either one keeps billing and keeps data alive.
#
# Usage:
#   bash deploy/aws/post_destroy_validation.sh [--region REGION] [--account ID] [--force] [--help]
#   (runnable from any directory — the repository root is resolved from the script location,
#    and the terraform state and backup-file checks are made relative to it)
#
# Exit codes:
#   0  every check passed (resources absent, backups present)
#   1  at least one check failed
#   2  preflight failure (aws cli missing, credentials bad, wrong account)

set -uo pipefail

# Resolve the repository root from this script's location, then work from there, so the
# ./terraform and backup-glob checks below find the same files regardless of the caller's CWD.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT" || { echo "  Could not enter repository root $REPO_ROOT" >&2; exit 2; }

REGION="${AWS_REGION:-us-east-1}"
EXPECTED_ACCOUNT="${EXPECTED_ACCOUNT:-023138541872}"
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --region)  REGION="${2:?--region needs a value}"; shift 2 ;;
    --account) EXPECTED_ACCOUNT="${2:?--account needs a value}"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    --help|-h) sed -n '3,26p' "$SCRIPT_DIR/post_destroy_validation.sh" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown argument: $1 (try --help)" >&2; exit 2 ;;
  esac
done

# Resource names — both provisioning conventions.
CLUSTERS=(ai-readiness-cluster ai-readiness-diagnostic-cluster)
TABLES=(ai-readiness-sessions ai-readiness-diagnostic-sessions)
REPOS=(ai-readiness-diagnostic)
LOG_PREFIXES=(/ecs/ai-readiness-diagnostic /ecs/ai-readiness)
ROLES=(ai-readiness-diagnostic-task-role ai-readiness-diagnostic-execution-role)
SEC_GROUPS=(ai-readiness-diagnostic-ecs-tasks ai-readiness-ecs-tasks)

PASSED=0; FAILED=0; SKIPPED=0
declare -a FAILURES=()

if [ -t 1 ]; then C_G=$'\033[32m'; C_R=$'\033[31m'; C_Y=$'\033[33m'; C_B=$'\033[1m'; C_0=$'\033[0m'
else C_G=; C_R=; C_Y=; C_B=; C_0=; fi

pass() { printf '  %sPASS%s  %s\n' "$C_G" "$C_0" "$1"; PASSED=$((PASSED + 1)); }
fail() { printf '  %sFAIL%s  %s\n' "$C_R" "$C_0" "$1"; FAILED=$((FAILED + 1)); FAILURES+=("$1"); }
skip() { printf '  %sSKIP%s  %s\n' "$C_Y" "$C_0" "$1"; SKIPPED=$((SKIPPED + 1)); }
section() { printf '\n%s%s%s\n' "$C_B" "$1" "$C_0"; }

# ---------------------------------------------------------------- preflight

section "Preflight"

if ! command -v aws >/dev/null 2>&1; then
  echo "  aws CLI not found on PATH. Install it or run this from a machine that has it." >&2
  exit 2
fi
pass "aws CLI present ($(aws --version 2>&1 | cut -d' ' -f1))"

if ! ACTUAL_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
  echo "  Could not call sts:GetCallerIdentity. Credentials missing or expired." >&2
  exit 2
fi

if [ "$ACTUAL_ACCOUNT" != "$EXPECTED_ACCOUNT" ]; then
  if [ "$FORCE" -eq 1 ]; then
    printf '  %sWARN%s  account is %s, expected %s — continuing due to --force\n' \
      "$C_Y" "$C_0" "$ACTUAL_ACCOUNT" "$EXPECTED_ACCOUNT"
  else
    echo "  Account mismatch: credentials are for $ACTUAL_ACCOUNT, expected $EXPECTED_ACCOUNT." >&2
    echo "  Validating the wrong account would report false success. Aborting." >&2
    echo "  Use --account $ACTUAL_ACCOUNT if that is genuinely the target, or --force." >&2
    exit 2
  fi
else
  pass "AWS account $ACTUAL_ACCOUNT matches expected"
fi
pass "Region: $REGION"

# ------------------------------------------------------- 1. terraform state

section "1. Terraform state"

if ! command -v terraform >/dev/null 2>&1; then
  skip "terraform not on PATH — state checks skipped"
elif [ ! -d terraform ]; then
  skip "no ./terraform directory — state checks skipped"
else
  if state_out=$(cd terraform && terraform state list 2>/dev/null); then
    count=$(printf '%s' "$state_out" | grep -c . || true)
    if [ "$count" -eq 0 ]; then pass "terraform state is empty"
    else
      fail "terraform state still lists $count resource(s)"
      printf '%s\n' "$state_out" | sed 's/^/          /'
    fi
  else
    skip "terraform state list failed (not initialised?) — treat manually"
  fi
fi

for f in terraform/terraform.tfstate terraform.tfstate; do
  [ -f "$f" ] || continue
  if command -v jq >/dev/null 2>&1; then
    n=$(jq '.resources | length' <"$f" 2>/dev/null || echo unknown)
    if [ "$n" = "0" ]; then pass "$f declares 0 resources"
    elif [ "$n" = "unknown" ]; then skip "$f is not parseable JSON"
    else fail "$f still declares $n resource(s)"; fi
  else
    skip "jq not installed — cannot inspect $f"
  fi
done

if compgen -G "terraform/.terraform.tfstate.lock*" >/dev/null 2>&1; then
  fail "terraform lock file(s) present — a run may be in progress"
else
  pass "no terraform lock files"
fi

# ---------------------------------------------------- 2. AWS resources gone

section "2. AWS resources absent"

for c in "${CLUSTERS[@]}"; do
  status=$(aws ecs describe-clusters --clusters "$c" --region "$REGION" \
             --query 'clusters[0].status' --output text 2>/dev/null || echo None)
  case "$status" in
    None|""|null) pass "ECS cluster absent: $c" ;;
    INACTIVE)     pass "ECS cluster INACTIVE: $c" ;;
    *)            fail "ECS cluster still $status: $c" ;;
  esac
done

for t in "${TABLES[@]}"; do
  if out=$(aws dynamodb describe-table --table-name "$t" --region "$REGION" 2>&1); then
    items=$(aws dynamodb describe-table --table-name "$t" --region "$REGION" \
              --query 'Table.ItemCount' --output text 2>/dev/null || echo '?')
    fail "DynamoDB table STILL EXISTS: $t (ItemCount ~$items) — data is still live"
  elif grep -q 'ResourceNotFoundException' <<<"$out"; then
    pass "DynamoDB table deleted: $t"
  else
    fail "DynamoDB table $t — unexpected error: $(head -1 <<<"$out")"
  fi
done

for r in "${REPOS[@]}"; do
  if out=$(aws ecr describe-repositories --repository-names "$r" --region "$REGION" 2>&1); then
    fail "ECR repository still exists: $r"
  elif grep -q 'RepositoryNotFoundException' <<<"$out"; then
    pass "ECR repository deleted: $r"
  else
    fail "ECR repository $r — unexpected error: $(head -1 <<<"$out")"
  fi
done

for p in "${LOG_PREFIXES[@]}"; do
  n=$(aws logs describe-log-groups --log-group-name-prefix "$p" --region "$REGION" \
        --query 'length(logGroups)' --output text 2>/dev/null || echo '?')
  case "$n" in
    0)   pass "no CloudWatch log groups under $p" ;;
    '?') fail "could not query CloudWatch log groups under $p" ;;
    *)   fail "$n CloudWatch log group(s) remain under $p — may retain log data" ;;
  esac
done

for role in "${ROLES[@]}"; do
  if out=$(aws iam get-role --role-name "$role" 2>&1); then
    fail "IAM role still exists: $role"
  elif grep -q 'NoSuchEntity' <<<"$out"; then
    pass "IAM role deleted: $role"
  else
    fail "IAM role $role — unexpected error: $(head -1 <<<"$out")"
  fi
done

for sg in "${SEC_GROUPS[@]}"; do
  n=$(aws ec2 describe-security-groups --region "$REGION" \
        --filters "Name=group-name,Values=$sg" \
        --query 'length(SecurityGroups)' --output text 2>/dev/null || echo '?')
  case "$n" in
    0)   pass "security group absent: $sg" ;;
    '?') fail "could not query security group: $sg" ;;
    *)   fail "security group still exists: $sg" ;;
  esac
done

# --------------------------------------------------------- 3. backups exist

section "3. Backups present"

# Backups may sit under either of two naming schemes, and in either the repo root or
# terraform/ depending on which route produced them:
#   pre_destroy_checklist.md   ->  ai-readiness-sessions-backup-*.json / cloudwatch-logs-*.txt
#   destroy_terraform.sh       ->  aws-backup-ddb-*.json             / aws-backup-logs-*.txt
# Any one match satisfies the check.
check_globs() {
  local label=$1; shift
  local p found=()
  for p in "$@"; do
    if compgen -G "$p" >/dev/null 2>&1; then
      # shellcheck disable=SC2206
      found+=($p)
    fi
  done
  if [ "${#found[@]}" -gt 0 ]; then
    pass "$label present: ${found[*]}"
  else
    fail "$label MISSING (looked for: $*) — nothing to restore from"
  fi
}

check_globs 'DynamoDB export' \
  'ai-readiness-sessions-backup-*.json' 'aws-backup-ddb-*.json' \
  'terraform/aws-backup-ddb-*.json'
check_globs 'CloudWatch log export' \
  'cloudwatch-logs-*.txt' 'aws-backup-logs-*.txt' 'terraform/aws-backup-logs-*.txt'
check_globs 'Terraform state backup' \
  'terraform/terraform.tfstate.backup.*' 'terraform.tfstate.backup.*'

# ---------------------------------------------------------------- summary

section "Summary"
printf '  %s%d passed%s, %s%d failed%s, %s%d skipped%s\n' \
  "$C_G" "$PASSED" "$C_0" "$C_R" "$FAILED" "$C_0" "$C_Y" "$SKIPPED" "$C_0"

if [ "$FAILED" -gt 0 ]; then
  printf '\n  %sUnresolved:%s\n' "$C_R" "$C_0"
  for f in "${FAILURES[@]}"; do printf '    - %s\n' "$f"; done
  printf '\n  Deprovisioning is NOT complete. Resources may still be billing,\n'
  printf '  and any surviving DynamoDB table still holds assessment data.\n'
  printf '  Remaining manual steps: deploy/aws/post_destroy_validation.md\n'
  exit 1
fi

printf '\n  All automated checks passed.\n'
printf '  Still to do by hand (see deploy/aws/post_destroy_validation.md):\n'
printf '    - review the AWS billing console for account %s\n' "$ACTUAL_ACCOUNT"
printf '    - archive the backup files to a secure location\n'
printf '    - commit the deprovisioning change and record sign-off\n'
exit 0
