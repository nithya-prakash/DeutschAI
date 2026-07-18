"""MinIO client factory — object storage for Phase 4 speech audio blobs.

Mirrors `vector_store/qdrant_client.py`'s shape: a cached factory function,
plus a thin wrapper class so services depend on `ObjectStore` (an interface
they can fake in tests) rather than the `Minio` SDK directly.
"""
from functools import lru_cache
from io import BytesIO

from minio import Minio

from app.core.config import get_settings

settings = get_settings()


class ObjectStore:
    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(
            self._bucket, key, BytesIO(data), length=len(data), content_type=content_type
        )

    def get_object(self, key: str) -> bytes:
        response = self._client.get_object(self._bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()


@lru_cache
def get_object_store() -> ObjectStore:
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )
    store = ObjectStore(client, settings.MINIO_BUCKET)
    store.ensure_bucket()
    return store
