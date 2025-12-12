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
    "You are an expert cloud architect specializing in AWS and C4 diagrams. "
    "Generate high-quality Mermaid C1–C3 diagrams for the given topology. "
    "Return ONLY Mermaid code blocks."
  )

  user_prompt = f"""Generate Mermaid diagrams (C1 context + C2 container + C3 component) for this AWS topology:

{json.dumps(topology, indent=2)}
"""

  mermaid = invoke_claude(system_prompt, user_prompt)

  s3_key = f"outputs/{job_id}/diagrams.mmd"
  s3.put_object(Bucket=OUTPUT_BUCKET, Key=s3_key, Body=mermaid.encode("utf-8"))

  jobs_table.update_item(
    Key={"job_id": job_id},
    UpdateExpression="SET updated_at = :u, output_diagram_s3_key = :d, #s = :s",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={
      ":u": now_iso(),
      ":d": s3_key,
      ":s": "DIAGRAM_DONE",
    },
  )

  return {"job_id": job_id, "topology": topology, "diagram_s3_key": s3_key}
