# app/services/minio_service.py
# pip install minio

import os
import io
from minio import Minio

_client = None


def _get_client() -> Minio:
    global _client
    if _client:
        return _client

    _client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT", "127.0.0.1:9101"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    )
    return _client


def _ensure_bucket(client: Minio, bucket: str):
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


async def upload_file(
    bucket: str,
    object_key: str,
    content: bytes,
    content_type: str = "application/octet-stream",
):
    client = _get_client()
    _ensure_bucket(client, bucket)

    data = io.BytesIO(content)
    client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=data,
        length=len(content),
        content_type=content_type,
    )
