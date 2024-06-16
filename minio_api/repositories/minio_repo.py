import logging
import logging.config
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from utils.config import settings
from utils.errors import EntityDoesNotExist, UnprocessableEntity

logging.config.dictConfig(settings.LOGGING_CONFIG)

logger = logging.getLogger(__name__)


class MinioRepository:
    def __init__(
            self,
            minio_endpoint: str,
            access_key: str,
            secret_key: str,
            bucket: str,
            secure: bool = False,
    ) -> None:
        self.client = Minio(
            minio_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket = bucket

    def create_or_update(
            self,
            name: str,
            file: BinaryIO,
            length: int,
            metadata: dict | None = None,
    ) -> dict:
        try:
            self.client.put_object(self.bucket, name, file, length=length, metadata=metadata)
            obj = self.get(name)
            logger.info(f'Meme created or updated: {name}')
            return {
                'status': 'Modified',
                'name': name,
                'last_updated_at': obj.get('last_updated_at').replace(tzinfo=None),
                'description': metadata.get('description'),
            }
        except Exception as e:
            logger.error(f'Create or update image: {e}')
            raise UnprocessableEntity

    def get(self, name: str) -> dict:
        try:
            obj = self.client.stat_object(self.bucket, name)
            return {
                'name': obj.object_name,
                'last_updated_at': obj.last_modified.replace(tzinfo=None),
                'description': obj.metadata.get('x-amz-meta-description'),
            }
        except S3Error:
            logger.error(f'minio.error.S3Error: S3 operation failed, filename={name} does not exist')
            raise

    def list(self) -> list[dict]:
        objects = list(self.client.list_objects(self.bucket))
        return [self.get(i.object_name) for i in objects]

    def delete(self, name: str) -> dict:
        try:
            obj = self.get(name)
            if obj.get('last_updated_at'):
                self.client.remove_object(self.bucket, name)
                logger.info(f'Image deleted: {name}')
                return {
                    'status': 'Deleted',
                    'name': name,
                    'description': obj.get('description'),
                    'last_updated_at': obj.get('last_updated_at'),
                }
        except S3Error:
            logger.error(f'minio.error.S3Error: S3 operation failed, filename={name} does not exist')
            raise
