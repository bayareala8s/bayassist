data "aws_iam_policy_document" "sf_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sf_role" {
  name               = "${var.project}-sf-role"
  assume_role_policy = data.aws_iam_policy_document.sf_assume.json
}

data "aws_iam_policy_document" "sf_permissions" {
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      aws_lambda_function.preprocessor.arn,
      aws_lambda_function.diagram.arn,
      aws_lambda_function.document.arn,
      aws_lambda_function.pdf.arn,
      aws_lambda_function.arc_ppt.arn,
      aws_lambda_function.confluence_exporter.arn,
    ]
  }

  statement {
    actions   = ["logs:*"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "sf_policy" {
  name   = "${var.project}-sf-policy"
  policy = data.aws_iam_policy_document.sf_permissions.json
}

resource "aws_iam_role_policy_attachment" "sf_attach" {
  role       = aws_iam_role.sf_role.name
  policy_arn = aws_iam_policy.sf_policy.arn
}

locals {
  sf_definition = jsonencode({
    Comment = "BayAssist Architecture Generation Flow (Diagrams + Doc + PDF + ARC PPT + Confluence HTML)"
    StartAt = "Preprocess"
    States = {
      Preprocess = {
        Type       = "Task"
        Resource   = aws_lambda_function.preprocessor.arn
        InputPath  = "$"
        ResultPath = "$"
        Next       = "GenerateDiagrams"
      }
      GenerateDiagrams = {
        Type       = "Task"
        Resource   = aws_lambda_function.diagram.arn
        ResultPath = "$"
        Next       = "GenerateDocument"
      }
      GenerateDocument = {
        Type       = "Task"
        Resource   = aws_lambda_function.document.arn
        ResultPath = "$"
        Next       = "GeneratePDF"
      }
      GeneratePDF = {
        Type       = "Task"
        Resource   = aws_lambda_function.pdf.arn
        InputPath  = "$"
        # Store PDF result under $.pdf so we keep doc_s3_key/topology at top level
        ResultPath = "$.pdf"
        Next       = "GenerateArcPPT"
      }
      GenerateArcPPT = {
        Type       = "Task"
        Resource   = aws_lambda_function.arc_ppt.arn
        InputPath  = "$"
        # Store PPT result under $.ppt so we keep previous state
        ResultPath = "$.ppt"
        Next       = "GenerateConfluenceHTML"
      }
      GenerateConfluenceHTML = {
        Type       = "Task"
        Resource   = aws_lambda_function.confluence_exporter.arn
        InputPath  = "$"
        ResultPath = "$"
        End        = true
      }
    }
  })
}


resource "aws_sfn_state_machine" "bayassist" {
  name       = "${var.project}-state-machine"
  role_arn   = aws_iam_role.sf_role.arn
  definition = local.sf_definition
}
