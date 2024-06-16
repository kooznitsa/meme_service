from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, status, Query, UploadFile
from minio.error import S3Error

from repositories.minio_repo import MinioRepository
from routers.users import get_current_user
from schemas.files import FileRead
from schemas.users import User
from utils.config import settings
from utils.errors import EntityDoesNotExist, UnprocessableEntity

router = APIRouter(prefix='/minio')

minio_repo = MinioRepository(
    settings.MINIO_URL,
    settings.MINIO_ACCESS_KEY,
    settings.MINIO_SECRET_KEY,
    settings.MINIO_BUCKET,
    False,
)


@router.post('/create_or_update', response_model=FileRead)
async def create_or_update(
        file: Annotated[UploadFile, File()],
        description: str = Form(),
        user: User = Depends(get_current_user),
) -> dict:
    try:
        metadata = {'description': description}
        return minio_repo.create_or_update(file.filename, file.file, file.size, metadata=metadata)
    except UnprocessableEntity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f'Data is in wrong format'
        )


@router.get('/get', response_model=FileRead)
async def get(
        name: str = Query(),
        user: User = Depends(get_current_user),
) -> dict:
    try:
        return minio_repo.get(name=name)
    except S3Error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Image with name={name} not found'
        )


@router.get('/list', response_model=list[FileRead])
async def list_files(user: User = Depends(get_current_user)) -> list[dict]:
    return minio_repo.list()


@router.delete('/delete', response_model=FileRead)
async def delete(
        name: str = Query(),
        user: User = Depends(get_current_user),
) -> dict:
    try:
        return minio_repo.delete(name=name)
    except S3Error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Image with name={name} not found'
        )
