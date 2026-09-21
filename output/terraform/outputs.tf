output "alb_dns_name" {
  description = "Public DNS of Application Load Balancer"
  value       = aws_lb.external.dns_name
}

output "rds_endpoint" {
  description = "Private Endpoint for RDS PostgreSQL database"
  value       = aws_db_instance.postgres.endpoint
}

output "s3_bucket_name" {
  description = "S3 Assets Bucket Name"
  value       = aws_s3_bucket.assets.id
}
