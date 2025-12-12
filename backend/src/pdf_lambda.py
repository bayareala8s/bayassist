import os
import boto3
from io import BytesIO
from fpdf import FPDF
from common.models import now_iso

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

JOBS_TABLE = os.environ["JOBS_TABLE"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def md_to_pdf_bytes(md_text: str) -> bytes:
  """Generate a simple, robust PDF from Markdown using pure Python (fpdf2).

  To avoid width issues in Lambda, we:
    - Render raw markdown lines (no HTML conversion).
    - Hard-wrap very long lines to a safe length.
  """

  pdf = FPDF()
  pdf.set_auto_page_break(auto=True, margin=15)
  pdf.add_page()
  pdf.set_font("Arial", size=11)

  max_line_len = 80
  max_lines = 200

  for i, raw_line in enumerate(md_text.splitlines()):
    if i >= max_lines:
      pdf.cell(0, 6, txt="...", ln=1)
      break

    line = raw_line.replace("\t", "  ")
    # Hard-wrap very long tokens to avoid FPDF width errors
    while line:
      chunk = line[:max_line_len]
      line = line[max_line_len:]
      try:
        pdf.cell(0, 6, txt=chunk, ln=1)
      except Exception:
        # If a pathological line still breaks, skip the remainder
        break

  return pdf.output(dest="S").encode("latin-1")


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
