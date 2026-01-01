# apps/legal_document_ingest/ocr/s3_temp_bucket.py

import uuid
import boto3
from contextlib import contextmanager


@contextmanager
def temporary_s3_bucket(
    *,
    region_name: str | None = None,
    prefix: str = "legal-doc-ingest",
):
    s3 = boto3.client("s3", region_name=region_name)

    bucket_name = f"{prefix}-{uuid.uuid4().hex[:12]}"

    try:
        if region_name and region_name != "us-east-1":
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": region_name
                },
            )
        else:
            s3.create_bucket(Bucket=bucket_name)

        yield bucket_name

    finally:
        # Empty bucket
        try:
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name):
                objs = [{"Key": o["Key"]} for o in page.get("Contents", [])]
                if objs:
                    s3.delete_objects(
                        Bucket=bucket_name,
                        Delete={"Objects": objs},
                    )
            s3.delete_bucket(Bucket=bucket_name)
        except Exception:
            # Last-resort: never mask the OCR failure
            pass
