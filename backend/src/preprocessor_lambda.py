import os
import json
import boto3
from common.models import now_iso

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

JOBS_TABLE = os.environ["JOBS_TABLE"]
INPUT_BUCKET = os.environ["INPUT_BUCKET"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def lambda_handler(event, context):
  job_id = event["job_id"]

  job = jobs_table.get_item(Key={"job_id": job_id}).get("Item")
  if not job:
    raise Exception(f"Job {job_id} not found")

  s3_key = job["input_s3_key"]
  obj = s3.get_object(Bucket=INPUT_BUCKET, Key=s3_key)
  raw_content = obj["Body"].read().decode("utf-8", errors="ignore")

  topology = {
    "services": [],
    "raw_preview": raw_content[:2000],
  }

  if "aws_s3_bucket" in raw_content:
    topology["services"].append({"type": "s3", "name": "S3 Buckets"})
  if "aws_lambda_function" in raw_content:
    topology["services"].append({"type": "lambda", "name": "Lambda Functions"})
  if "aws_stepfunctions_state_machine" in raw_content:
    topology["services"].append({"type": "stepfunctions", "name": "State Machines"})

  jobs_table.update_item(
    Key={"job_id": job_id},
    UpdateExpression="SET updated_at = :u, meta.topology = :t, #s = :s",
    ExpressionAttributeNames={"#s": "status"},
    ExpressionAttributeValues={
      ":u": now_iso(),
      ":t": topology,
      ":s": "PREPROCESSED",
    },
  )

  return {"job_id": job_id, "topology": topology}
