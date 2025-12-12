terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = {
    Project = var.project
    Owner   = "BayAreaLa8s"
    Env     = "prod"
  }
}

# S3 buckets
resource "aws_s3_bucket" "input" {
  bucket = "${var.project}-input"
  tags   = local.tags
}

resource "aws_s3_bucket" "output" {
  bucket = "${var.project}-output"
  tags   = local.tags
}

# Lock down the input bucket (no public access)
resource "aws_s3_bucket_public_access_block" "input_pab" {
  bucket                  = aws_s3_bucket.input.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Output bucket: allow public read of generated artifacts under outputs/ for demo
resource "aws_s3_bucket_public_access_block" "output_pab" {
  bucket                  = aws_s3_bucket.output.id
  block_public_acls       = true
  ignore_public_acls      = true

  # Allow a bucket policy so we can grant read access on outputs/*
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "output_public_read" {
  bucket = aws_s3_bucket.output.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowPublicReadOfOutputs"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.output.arn}/outputs/*"
      }
    ]
  })
}

# DynamoDB Jobs table
resource "aws_dynamodb_table" "jobs" {
  name         = "${var.project}-jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  tags = local.tags
}
