import boto3
from botocore.client import BaseClient
from botocore.config import Config

from app.config import get_settings


def _client(endpoint: str) -> BaseClient:
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=s.s3_region,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


_internal: BaseClient | None = None
_public: BaseClient | None = None


def internal_client() -> BaseClient:
    """Client for server-side calls (list, head, delete)."""
    global _internal
    if _internal is None:
        _internal = _client(get_settings().s3_internal_endpoint)
    return _internal


def public_client() -> BaseClient:
    """Client used only to sign URLs that phones will call."""
    global _public
    if _public is None:
        _public = _client(get_settings().s3_public_endpoint)
    return _public


def sku_prefix(sku: str) -> str:
    return f"{get_settings().upload_prefix}/{sku}/"


def ensure_bucket() -> None:
    s3 = internal_client()
    bucket = get_settings().s3_bucket
    names = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}
    if bucket not in names:
        s3.create_bucket(Bucket=bucket)
