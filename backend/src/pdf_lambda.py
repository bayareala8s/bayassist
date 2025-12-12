import os
import boto3
from io import BytesIO
from markdown import markdown
from xhtml2pdf import pisa
from common.models import now_iso

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

JOBS_TABLE = os.environ["JOBS_TABLE"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def md_to_pdf_bytes(md_text: str) -> bytes:
  html_body = markdown(md_text, extensions=["tables", "fenced_code"])
  html = f"""<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {{ font-family: Arial, sans-serif; font-size: 11pt; }}
      h1, h2, h3 {{ color: #0050EF; }}
      code {{ font-family: 'Courier New', monospace; font-size: 9pt; }}
      pre {{ background-color: #f4f4f4; padding: 8px; border-radius: 4px; }}
      table, th, td {{ border: 1px solid #ccc; border-collapse: collapse; padding: 4px; }}
    </style>
  </head>
  <body>
    {html_body}
  </body>
</html>
"""

  pdf_io = BytesIO()
  pisa_status = pisa.CreatePDF(html, dest=pdf_io)
  if pisa_status.err:
    raise Exception("PDF generation failed")
  return pdf_io.getvalue()


def lambda_handler(event, context):
  job_id = event["job_id"]
  doc_s3_key = event["doc_s3_key"]

  obj = s3.get_object(Bucket=OUTPUT_BUCKET, Key=doc_s3_key)
  md_text = obj["Body"].read().decode("utf-8")

  pdf_bytes = md_to_pdf_bytes(md_text)

  pdf_key = f"outputs/{job_id}/architecture.pdf"
  s3.put_object(
    Bucket=OUTPUT_BUCKET,
    Key=pdf_key,
    Body=pdf_bytes,
    ContentType="application/pdf",
  )

  jobs_table.update_item(
    Key={"job_id": job_id},
    UpdateExpression="SET updated_at = :u, output_pdf_s3_key = :p",
    ExpressionAttributeValues={
      ":u": now_iso(),
      ":p": pdf_key,
    },
  )

  return {"job_id": job_id, "pdf_s3_key": pdf_key}
