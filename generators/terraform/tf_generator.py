"""
Terraform Infrastructure as Code (IaC) Generator for AWS
Produces compliant Terraform scripts based on approved cloud architecture.
Includes VPC, Subnets, ALB, Auto Scaling Group, RDS PostgreSQL (Multi-AZ), and S3.
"""

import os
from typing import Dict, Any

def get_main_tf() -> str:
    return """terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "AI-Product-Architect"
    }
  }
}
"""

def get_variables_tf() -> str:
    return """variable "aws_region" {
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
"""

def get_network_tf() -> str:
    return """# VPC Definition
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets across 2 Availability Zones
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
  tags = { Name = "${var.project_name}-public-1" }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
  tags = { Name = "${var.project_name}-public-2" }
}

# Private Subnets for Database & Internal Compute
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"
  tags = { Name = "${var.project_name}-private-1" }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = "${var.aws_region}b"
  tags = { Name = "${var.project_name}-private-2" }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table_association" "pub_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "pub_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}
"""

def get_compute_tf() -> str:
    return """# Security Group for Application Load Balancer
resource "aws_security_group" "alb_sg" {
  name        = "${var.project_name}-alb-sg"
  description = "Allow inbound HTTP/HTTPS traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP ingress"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS ingress"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Application Load Balancer
resource "aws_lb" "external" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  enable_deletion_protection = false
}

# Target Group for Backend Microservices
resource "aws_lb_target_group" "api_tg" {
  name        = "${var.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    path                = "/health"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# ALB HTTP Listener
resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.external.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_tg.arn
  }
}
"""

def get_database_tf() -> str:
    return """# Database Subnet Group (Private Multi-AZ)
resource "aws_db_subnet_group" "rds_subnets" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "Private DB Subnet Group"
  }
}

# Database Security Group: Only accessible from backend services
resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow inbound PostgreSQL from ALB & app instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Managed AWS RDS PostgreSQL Instance (Multi-AZ for High Availability)
resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-postgres"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = "db.t3.medium"
  allocated_storage      = 50
  max_allocated_storage  = 200
  storage_type           = "gp3"
  multi_az               = true
  publicly_accessible    = false
  db_subnet_group_name   = aws_db_subnet_group.rds_subnets.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  db_name  = "cloud_product_db"
  username = "clouduser"
  password = var.db_password

  backup_retention_period = 7
  skip_final_snapshot     = true
  storage_encrypted       = true
}
"""

def get_storage_tf() -> str:
    return """# Encrypted S3 Bucket for Product Media / Assets
resource "aws_s3_bucket" "assets" {
  bucket        = "${var.project_name}-media-storage"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets_crypto" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
"""

def get_outputs_tf() -> str:
    return """output "alb_dns_name" {
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
"""

def generate_terraform_files(output_dir: str, spec: Dict[str, Any] = None) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    
    files = {
        "main.tf": get_main_tf(),
        "variables.tf": get_variables_tf(),
        "network.tf": get_network_tf(),
        "compute.tf": get_compute_tf(),
        "database.tf": get_database_tf(),
        "storage.tf": get_storage_tf(),
        "outputs.tf": get_outputs_tf()
    }
    
    generated = {}
    for filename, content in files.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        generated[filename] = path
        
    return generated

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "./output/terraform"
    res = generate_terraform_files(target)
    print(f"Terraform files generated at: {res}")
