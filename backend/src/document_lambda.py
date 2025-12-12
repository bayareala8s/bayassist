import os
import json
import boto3
from common.models import now_iso
from common.bedrock_client import invoke_claude

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

JOBS_TABLE = os.environ["JOBS_TABLE"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def lambda_handler(event, context):
  job_id = event["job_id"]
  topology = event["topology"]

  system_prompt = (
    "You are an enterprise architect. Generate a clear, structured architecture document "
    "in Markdown including Executive Summary, Problem Statement, Architecture Overview, "
    "High-Level Design, Detailed Design, Logging & Observability, RTO/RPO, NFRs, and Security."
  )

  user_prompt = f"""Using the following topology (and assume AWS best practices), create a 10–15 page style
architecture document in Markdown.

Topology:
{json.dumps(topology, indent=2)}
"""

  markdown = invoke_claude(system_prompt, user_prompt)

  s3_key = f"outputs/{job_id}/architecture.md"
  s3.put_object(Bucket=OUTPUT_BUCKET, Key=s3_key, Body=markdown.encode("utf-8"))

  jobs_table.update_item(
    Key={"job_id": job_id},
    UpdateExpression="SET updated_at = :u, output_doc_s3_key = :d, #s = :s",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={
      ":u": now_iso(),
      ":d": s3_key,
      ":s": "COMPLETED_DOC",
    },
  )

  return {"job_id": job_id, "doc_s3_key": s3_key, "topology": topology}
