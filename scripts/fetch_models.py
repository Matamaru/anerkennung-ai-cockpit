import os
from pathlib import Path
import sys

import boto3


PASSPORT_PREFIX = os.getenv("CAESAR_S3_PASSPORT_PREFIX", "s3://anerkennung-models/models/passport/passport_layoutlmv3-token/")
DIPLOMA_PREFIX = os.getenv("CAESAR_S3_DIPLOMA_PREFIX", "s3://anerkennung-models/models/diploma/diploma_layoutlmv3-token/")

LOCAL_BASE = Path(os.getenv("CAESAR_MODEL_CACHE_DIR", "/app/models"))


def _parse_s3_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {uri}")
    parts = uri[5:].split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix


def _download_prefix(s3, uri: str, dest: Path) -> None:
    bucket, prefix = _parse_s3_uri(uri)
    dest.mkdir(parents=True, exist_ok=True)

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            rel = key[len(prefix):].lstrip("/")
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            s3.download_file(bucket, key, str(target))


def main() -> int:
    if os.getenv("CAESAR_FETCH_MODELS_ON_RELEASE", "").lower() not in ("1", "true", "yes"):
        print("CAESAR_FETCH_MODELS_ON_RELEASE is not enabled. Skipping model downloads.")
        return 0

    s3 = boto3.client("s3")

    passport_dest = LOCAL_BASE / "passport_layoutlmv3-token"
    diploma_dest = LOCAL_BASE / "diploma_layoutlmv3-token"

    if not (passport_dest / "labels.json").exists():
        print(f"Downloading passport model from {PASSPORT_PREFIX} to {passport_dest} ...")
        _download_prefix(s3, PASSPORT_PREFIX, passport_dest)
    else:
        print("Passport model already present. Skipping download.")

    if not (diploma_dest / "labels.json").exists():
        print(f"Downloading diploma model from {DIPLOMA_PREFIX} to {diploma_dest} ...")
        _download_prefix(s3, DIPLOMA_PREFIX, diploma_dest)
    else:
        print("Diploma model already present. Skipping download.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
