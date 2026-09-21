# Encrypted S3 Bucket for Product Media / Assets
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
