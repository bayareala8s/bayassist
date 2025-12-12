import json
import os
import base64
import boto3
from typing import Any, Dict
from decimal import Decimal
from common.models import JobItem

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
stepfunctions = boto3.client("stepfunctions")

JOBS_TABLE = os.environ["JOBS_TABLE"]
INPUT_BUCKET = os.environ["INPUT_BUCKET"]
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

jobs_table = dynamodb.Table(JOBS_TABLE)


def _json_default(o):
  if isinstance(o, Decimal):
    return float(o)
  raise TypeError


def _response(status: int, body: Dict[str, Any]):
  return {
    "statusCode": status,
    "headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": "true",
      "Content-Type": "application/json",
    },
    "body": json.dumps(body, default=_json_default),
  }


def lambda_handler(event, context):
  method = event["requestContext"]["http"]["method"]
  path = event["requestContext"]["http"]["path"]

  if method == "POST" and path.startswith("/generate/diagrams"):
    return handle_generate(event, "diagrams")
  if method == "POST" and path.startswith("/generate/document"):
    return handle_generate(event, "document")
  if method == "GET" and path.startswith("/jobs/") and path != "/jobs":
    job_id = path.split("/")[-1]
    return handle_get_job(job_id)
  if method == "GET" and path == "/jobs":
    return handle_list_jobs()

  return _response(404, {"message": "Not found"})


def handle_generate(event, job_type: str):
  if event.get("isBase64Encoded"):
    body_bytes = base64.b64decode(event["body"])
    body = json.loads(body_bytes)
  else:
    body = json.loads(event["body"])

  file_content_b64 = body["fileContent"]
  filename = body.get("filename", "input.zip")
  file_bytes = base64.b64decode(file_content_b64)

  s3_key = f"inputs/{filename}"
  s3.put_object(Bucket=INPUT_BUCKET, Key=s3_key, Body=file_bytes)

  job = JobItem.new(input_s3_key=s3_key, job_type=job_type)
  jobs_table.put_item(Item=job.to_dynamo())

  stepfunctions.start_execution(
    stateMachineArn=STATE_MACHINE_ARN,
    input=json.dumps({"job_id": job.job_id}),
  )

  return _response(202, {"jobId": job.job_id, "status": job.status})


def handle_get_job(job_id: str):
  resp = jobs_table.get_item(Key={"job_id": job_id})
  if "Item" not in resp:
    return _response(404, {"message": "Job not found"})
  return _response(200, resp["Item"])


def handle_list_jobs():
  resp = jobs_table.scan(Limit=50)
  items = resp.get("Items", [])
  return _response(200, {"jobs": items})
