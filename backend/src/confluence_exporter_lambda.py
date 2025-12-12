import os
import boto3
import markdown2
from common.models import now_iso

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

JOBS_TABLE = os.environ["JOBS_TABLE"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def md_to_confluence_html(md_text: str) -> str:
  html_body = markdown2.markdown(
    md_text,
    extras=["tables", "fenced-code-blocks", "strike", "toc", "header-ids"],
  )
  html = f"""<html>
  <head>
    <meta charset="utf-8" />
    <title>BayAssist Architecture Document</title>
  </head>
  <body>
    {html_body}
  </body>
</html>
"""
  return html


def lambda_handler(event, context):
  job_id = event["job_id"]
  doc_s3_key = event["doc_s3_key"]

  obj = s3.get_object(Bucket=OUTPUT_BUCKET, Key=doc_s3_key)
  md_text = obj["Body"].read().decode("utf-8")
  html = md_to_confluence_html(md_text)

  html_key = f"outputs/{job_id}/architecture-confluence.html"
  s3.put_object(
    Bucket=OUTPUT_BUCKET,
    Key=html_key,
    Body=html.encode("utf-8"),
    ContentType="text/html",
  )

  jobs_table.update_item(
    Key={"job_id": job_id},
    UpdateExpression="SET updated_at = :u, output_confluence_html_s3_key = :h",
    ExpressionAttributeValues={
      ":u": now_iso(),
      ":h": html_key,
    },
  )

  return {"job_id": job_id, "confluence_html_s3_key": html_key}
