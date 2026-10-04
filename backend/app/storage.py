import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from .config import settings


def client():
    if not all([settings.storage_bucket, settings.storage_access_key, settings.storage_secret_key]):
        raise RuntimeError("Private S3-compatible storage is not configured")
    return boto3.client("s3", endpoint_url=settings.storage_endpoint or None,
        aws_access_key_id=settings.storage_access_key, aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region, config=Config(signature_version="s3v4"))


def is_not_found(error: Exception) -> bool:
    return isinstance(error, ClientError) and (error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404 or error.response.get("Error", {}).get("Code") in {"NoSuchKey", "NotFound"})


def presign_upload(key: str, content_type: str) -> dict:
    # S3 POST policy allows the storage service to enforce a size ceiling before bytes are accepted.
    fields = {"Content-Type": content_type, "x-amz-server-side-encryption": "AES256"}
    conditions = [{"Content-Type": content_type}, {"x-amz-server-side-encryption": "AES256"}, ["content-length-range", 1, settings.upload_max_bytes]]
    return client().generate_presigned_post(settings.storage_bucket, key, Fields=fields, Conditions=conditions, ExpiresIn=300)


def head(key: str):
    return client().head_object(Bucket=settings.storage_bucket, Key=key)


def get_with_etag(key: str) -> tuple[bytes, str]:
    result = client().get_object(Bucket=settings.storage_bucket, Key=key)
    return result["Body"].read(), result.get("ETag", "").strip('"')


def get(key: str) -> bytes:
    return get_with_etag(key)[0]


def delete(key: str, etag: str | None = None):
    params = {"Bucket": settings.storage_bucket, "Key": key}
    if etag: params["IfMatch"] = f'"{etag.strip(chr(34))}"'
    client().delete_object(**params)
