data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = "${var.project}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]
    resources = [
      "${aws_s3_bucket.input.arn}/*",
      "${aws_s3_bucket.output.arn}/*"
    ]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Scan",
    ]
    resources = [aws_dynamodb_table.jobs.arn]
  }

  statement {
    actions   = ["states:StartExecution"]
    resources = ["*"]
  }

  statement {
    actions   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "${var.project}-lambda-policy"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "lambda_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Lambda functions (artifacts built under backend/dist)
resource "aws_lambda_function" "api" {
  function_name = "${var.project}-api"
  role          = aws_iam_role.lambda_role.arn
  handler       = "api_handler.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/api.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/api.zip")

  timeout = 30

  environment {
    variables = {
      JOBS_TABLE        = aws_dynamodb_table.jobs.name
      INPUT_BUCKET      = aws_s3_bucket.input.bucket
      OUTPUT_BUCKET     = aws_s3_bucket.output.bucket
      STATE_MACHINE_ARN = aws_sfn_state_machine.bayassist.arn
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "preprocessor" {
  function_name = "${var.project}-preprocessor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "preprocessor_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/preprocessor.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/preprocessor.zip")

  timeout = 60

  environment {
    variables = {
      JOBS_TABLE   = aws_dynamodb_table.jobs.name
      INPUT_BUCKET = aws_s3_bucket.input.bucket
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "diagram" {
  function_name = "${var.project}-diagram"
  role          = aws_iam_role.lambda_role.arn
  handler       = "diagram_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/diagram.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/diagram.zip")

  timeout = 120

  environment {
    variables = {
      JOBS_TABLE    = aws_dynamodb_table.jobs.name
      OUTPUT_BUCKET = aws_s3_bucket.output.bucket
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "document" {
  function_name = "${var.project}-document"
  role          = aws_iam_role.lambda_role.arn
  handler       = "document_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/document.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/document.zip")

  timeout = 180

  environment {
    variables = {
      JOBS_TABLE    = aws_dynamodb_table.jobs.name
      OUTPUT_BUCKET = aws_s3_bucket.output.bucket
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "pdf" {
  function_name = "${var.project}-pdf"
  role          = aws_iam_role.lambda_role.arn
  handler       = "pdf_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/pdf.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/pdf.zip")

  timeout = 180

  environment {
    variables = {
      JOBS_TABLE    = aws_dynamodb_table.jobs.name
      OUTPUT_BUCKET = aws_s3_bucket.output.bucket
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "arc_ppt" {
  function_name = "${var.project}-arc-ppt"
  role          = aws_iam_role.lambda_role.arn
  handler       = "arc_ppt_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/arc_ppt.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/arc_ppt.zip")

  timeout = 180

  environment {
    variables = {
      JOBS_TABLE    = aws_dynamodb_table.jobs.name
      OUTPUT_BUCKET = aws_s3_bucket.output.bucket
    }
  }

  tags = local.tags
}

resource "aws_lambda_function" "confluence_exporter" {
  function_name = "${var.project}-confluence-export"
  role          = aws_iam_role.lambda_role.arn
  handler       = "confluence_exporter_lambda.lambda_handler"
  runtime       = "python3.11"

  filename         = "${path.module}/../backend/dist/confluence_exporter.zip"
  source_code_hash = filebase64sha256("${path.module}/../backend/dist/confluence_exporter.zip")

  timeout = 180

  environment {
    variables = {
      JOBS_TABLE    = aws_dynamodb_table.jobs.name
      OUTPUT_BUCKET = aws_s3_bucket.output.bucket
    }
  }

  tags = local.tags
}
