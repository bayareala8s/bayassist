from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


def now_iso() -> str:
  return datetime.utcnow().isoformat() + "Z"


@dataclass
class JobItem:
  job_id: str
  status: str
  created_at: str
  updated_at: str
  input_s3_key: str
  output_diagram_s3_key: Optional[str] = None
  output_doc_s3_key: Optional[str] = None
  output_pdf_s3_key: Optional[str] = None
  output_ppt_s3_key: Optional[str] = None
  output_confluence_html_s3_key: Optional[str] = None
  error_message: Optional[str] = None
  job_type: str = "architecture"
  meta: Optional[Dict[str, Any]] = None

  @staticmethod
  def new(input_s3_key: str, job_type: str = "architecture") -> "JobItem":
    job_id = str(uuid.uuid4())
    return JobItem(
      job_id=job_id,
      status="PENDING",
      created_at=now_iso(),
      updated_at=now_iso(),
      input_s3_key=input_s3_key,
      job_type=job_type,
      meta={},
    )

  def to_dynamo(self) -> Dict[str, Any]:
    item = asdict(self)
    return {k: v for k, v in item.items() if v is not None}
