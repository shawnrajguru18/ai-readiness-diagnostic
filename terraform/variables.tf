variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name (used for resource naming)"
  type        = string
  default     = "ai-readiness-diagnostic"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "container_image" {
  description = "Docker image URL (ECR or external)"
  type        = string
  # Set via terraform.tfvars or -var flag
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8080
}

variable "task_cpu" {
  description = "ECS task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 1024
}

variable "task_memory" {
  description = "ECS task memory in MB"
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "enable_autoscaling" {
  description = "Enable autoscaling for ECS service"
  type        = bool
  default     = false
}

variable "min_capacity" {
  description = "Minimum number of tasks for autoscaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks for autoscaling"
  type        = number
  default     = 3
}

variable "vpc_id" {
  description = "VPC ID (optional - if not provided, uses default VPC)"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for ECS tasks (optional - if not provided, uses default subnets)"
  type        = list(string)
  default     = []
}

variable "mail_from_address" {
  description = "SES sender address; its domain is the sending domain (SPEC_outbound_mail.md §6)"
  type        = string
  default     = "catalystx-support@dxc.com"
}

variable "mail_from_name" {
  description = "From display name (SPEC_outbound_mail.md §6)"
  type        = string
  default     = "DXC AI Readiness"
}

variable "mail_reply_to_address" {
  description = "Monitored reply mailbox (SPEC_outbound_mail.md §6); empty sends no Reply-To"
  type        = string
  default     = ""
}

variable "test_recipient_addresses" {
  description = "Recipients verified as SES identities so a sandboxed account can send to them. Test scaffolding; remove once the account leaves the sandbox."
  type        = list(string)
  default     = []
}

variable "anthropic_api_key" {
  description = "AWS Bedrock API key (generate in AWS Console → Bedrock → API keys)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_base_url" {
  description = "Bedrock Mantle endpoint URL (e.g., https://bedrock-mantle.us-east-1.api.aws/anthropic)"
  type        = string
  default     = ""
}
