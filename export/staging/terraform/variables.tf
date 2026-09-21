variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Unique project identifier"
  default     = "ai-cloud-product"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "production"
}

variable "db_password" {
  type        = string
  description = "PostgreSQL root password"
  sensitive   = true
  default     = "SecurePostgres2026!#"
}

variable "monthly_budget_inr" {
  type        = number
  description = "Estimated monthly cloud budget limit"
  default     = 30000
}
