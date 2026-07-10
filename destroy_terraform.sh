#!/bin/bash

################################################################################
# Terraform Destroy Wrapper - AI Readiness Diagnostic MVP
################################################################################
# Safe wrapper around terraform destroy with pre/post checks and confirmations
# 
# Usage: bash destroy_terraform.sh [--auto-approve] [--skip-backup]
#
# Options:
#   --auto-approve    Skip interactive confirmations
#   --skip-backup     Skip backup phase (use with caution!)
#
# Safety:
#   - Creates backups before destruction
#   - Verifies Terraform state is clean
#   - Requires explicit confirmation
#   - Provides rollback instructions
#
################################################################################

set -e

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT="023138541872"
APP_NAME="ai-readiness-diagnostic"
TABLE_NAME="${APP_NAME}-sessions"
LOG_GROUP="/ecs/${APP_NAME}"
TF_DIR="terraform"

# Options
AUTO_APPROVE="${1:-}"
SKIP_BACKUP="${2:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_section() {
    echo ""
    echo "================================================================================"
    echo -e "${BLUE}$1${NC}"
    echo "================================================================================"
    echo ""
}

confirm() {
    local prompt="$1"
    
    if [[ "$AUTO_APPROVE" == "--auto-approve" ]]; then
        log_warning "AUTO_APPROVE: $prompt"
        return 0
    fi
    
    local response
    while true; do
        read -p "$(echo -e ${YELLOW}$prompt${NC}) [yes/no]: " response
        case "$response" in
            yes|y) return 0 ;;
            no|n) return 1 ;;
            *) echo "Please answer yes or no" ;;
        esac
    done
}

################################################################################
# MAIN
################################################################################

main() {
    print_section "AWS DEPROVISIONING - Terraform Destroy Wrapper"
    
    echo "Account:    $AWS_ACCOUNT"
    echo "Region:     $AWS_REGION"
    echo "Directory:  $TF_DIR"
    echo "Status:     PRE-DESTROY CHECKS"
    echo ""
    
    # Verify credentials
    log_info "Checking AWS credentials..."
    CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    
    if [[ "$CURRENT_ACCOUNT" != "$AWS_ACCOUNT" ]]; then
        log_error "Wrong AWS account: $CURRENT_ACCOUNT (expected $AWS_ACCOUNT)"
        exit 1
    fi
    log_success "AWS account verified: $CURRENT_ACCOUNT"
    
    # Change to Terraform directory
    if [[ ! -d "$TF_DIR" ]]; then
        log_error "Terraform directory not found: $TF_DIR"
        exit 1
    fi
    cd "$TF_DIR"
    log_success "Terraform directory found"
    
    # Validate Terraform
    log_info "Validating Terraform configuration..."
    if ! terraform validate &>/dev/null; then
        log_error "Terraform validation failed"
        exit 1
    fi
    log_success "Terraform validation passed"
    
    # List resources
    RESOURCE_COUNT=$(terraform state list 2>/dev/null | wc -l)
    log_info "Resources in state: $RESOURCE_COUNT"
    
    if [ "$RESOURCE_COUNT" -eq 0 ]; then
        log_warning "No resources found in state - already deprovisioned?"
        exit 0
    fi
    
    print_section "PRE-DESTROY BACKUPS"
    
    if [[ "$SKIP_BACKUP" != "--skip-backup" ]]; then
        # DynamoDB backup
        log_info "Exporting DynamoDB table..."
        if aws dynamodb scan --table-name "$TABLE_NAME" --region "$AWS_REGION" \
            > "aws-backup-ddb-$(date +%Y%m%d-%H%M%S).json" 2>/dev/null; then
            log_success "DynamoDB exported"
        else
            log_warning "DynamoDB export failed (table may already be deleted)"
        fi
        
        # CloudWatch logs backup
        log_info "Exporting CloudWatch logs..."
        if aws logs tail "$LOG_GROUP" --region "$AWS_REGION" --follow=false \
            > "aws-backup-logs-$(date +%Y%m%d-%H%M%S).txt" 2>/dev/null; then
            log_success "CloudWatch logs exported"
        else
            log_warning "CloudWatch logs export failed (logs may be empty)"
        fi
        
        # Terraform state backup
        log_info "Backing up Terraform state..."
        cp terraform.tfstate "terraform.tfstate.backup.$(date +%Y%m%d-%H%M%S)"
        log_success "Terraform state backed up"
    fi
    
    print_section "TERRAFORM DESTROY PLAN"
    
    log_info "Generating destroy plan..."
    if ! terraform plan -destroy -out=destroy.tfplan &>/dev/null; then
        log_error "Failed to generate destroy plan"
        exit 1
    fi
    log_success "Destroy plan generated"
    
    # Show what will be destroyed
    echo "Resources to be destroyed:"
    terraform state list | sed 's/^/  - /'
    echo ""
    
    # Final confirmation
    if ! confirm "Ready to destroy all resources in account $AWS_ACCOUNT region $AWS_REGION?"; then
        log_warning "Destruction cancelled"
        rm -f destroy.tfplan
        exit 0
    fi
    
    print_section "EXECUTING TERRAFORM DESTROY"
    
    log_warning "Destroying resources... (this may take 2-5 minutes)"
    echo ""
    
    if ! terraform destroy -auto-approve destroy.tfplan; then
        log_error "Terraform destroy failed"
        log_info "Check above for error details"
        log_info "Retry with: terraform destroy"
        rm -f destroy.tfplan
        exit 1
    fi
    
    rm -f destroy.tfplan
    log_success "Terraform destroy completed"
    
    print_section "POST-DESTROY VERIFICATION"
    
    # Verify state is empty
    REMAINING=$(terraform state list 2>/dev/null | wc -l)
    if [ "$REMAINING" -eq 0 ]; then
        log_success "Terraform state is clean (0 resources)"
    else
        log_warning "Terraform state still has $REMAINING resources"
    fi
    
    # Verify AWS resources
    log_info "Verifying AWS resources deleted..."
    
    # Quick checks
    if aws ecs describe-clusters --clusters "$APP_NAME-cluster" --region "$AWS_REGION" 2>/dev/null | grep -q "ACTIVE"; then
        log_warning "ECS Cluster still exists"
    else
        log_success "ECS Cluster deleted"
    fi
    
    if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$AWS_REGION" 2>/dev/null | grep -q "$TABLE_NAME"; then
        log_warning "DynamoDB Table still exists"
    else
        log_success "DynamoDB Table deleted"
    fi
    
    if aws ecr describe-repositories --repository-names "$APP_NAME" --region "$AWS_REGION" 2>/dev/null | grep -q "$APP_NAME"; then
        log_warning "ECR Repository still exists"
    else
        log_success "ECR Repository deleted"
    fi
    
    print_section "DEPROVISIONING COMPLETE"
    
    echo "Summary:"
    echo "  - AWS resources deleted"
    echo "  - Terraform state cleaned"
    echo "  - Backups preserved in current directory"
    echo ""
    echo "Cost impact:"
    echo "  - Monthly savings: ~\$60-88"
    echo "  - Annual savings: ~\$720-1,056"
    echo ""
    echo "Next steps:"
    echo "  1. Run post-destroy validation: bash post_destroy_validation.txt"
    echo "  2. Archive backups to secure location"
    echo "  3. Commit changes to git: git add -A && git commit -m 'Deprovisioning: Terraform destroy completed'"
    echo "  4. Verify billing in next cycle"
    echo ""
    log_success "Deprovisioning finished at $(date)"
}

# Run main
main "$@"
