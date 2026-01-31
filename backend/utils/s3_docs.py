import os
from urllib.parse import urlparse

import boto3


def _bucket() -> str | None:
    return os.getenv("DOCS_S3_BUCKET")


def _prefix() -> str:
    prefix = os.getenv("DOCS_S3_PREFIX", "documents/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return prefix


def _client():
    region = os.getenv("AWS_REGION")
    if region:
        return boto3.client("s3", region_name=region)
    return boto3.client("s3")


def is_s3_uri(path: str | None) -> bool:
    return bool(path and path.startswith("s3://"))


def build_s3_key(filename: str, *, user_id: str | None = None) -> str:
    base = _prefix()
    if user_id:
        base = f"{base}{user_id}/"
    return f"{base}{filename}"


def upload_bytes(file_bytes: bytes, filename: str, *, user_id: str | None = None) -> str | None:
    bucket = _bucket()
    if not bucket:
        return None
    key = build_s3_key(filename, user_id=user_id)
    client = _client()
    client.put_object(Bucket=bucket, Key=key, Body=file_bytes)
    return f"s3://{bucket}/{key}"


def presign_url(s3_uri: str, *, expires: int = 3600, inline: bool = True) -> str | None:
    if not is_s3_uri(s3_uri):
        return None
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    client = _client()
    params = {"Bucket": bucket, "Key": key}
    if inline:
        params["ResponseContentDisposition"] = "inline"
    return client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires)
