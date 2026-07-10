output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.app.name
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.sessions.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "task_role_arn" {
  description = "IAM task role ARN"
  value       = aws_iam_role.task_role.arn
}

output "execution_role_arn" {
  description = "IAM execution role ARN"
  value       = aws_iam_role.execution_role.arn
}

output "app_url" {
  description = "Application URL (public IP will be assigned after deployment)"
  value       = "Get the public IP from ECS service network interface or load balancer"
}
