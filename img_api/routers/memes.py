from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, status, UploadFile

from repositories.memes import MemeRepository
from schemas.memes import Meme, MemeCreate, MemeRead, MemeUpdate
from utils.errors import EntityDoesNotExist
from utils.sessions import get_repository

router = APIRouter(prefix='/memes')


@router.post(
    '/',
    response_model=MemeRead,
    status_code=status.HTTP_201_CREATED,
    name='create_meme',
)
async def create_meme(
        file: Annotated[UploadFile, File()],
        description: str = Form(),
        repository: MemeRepository = Depends(get_repository(MemeRepository)),
) -> MemeRead:
    return await repository.create(file, description)


@router.get(
    '/',
    response_model=list[Optional[MemeRead]],
    status_code=status.HTTP_200_OK,
    name='list_memes',
)
async def list_memes(
        limit: int = Query(default=50, lte=100),
        offset: int = Query(default=0),
        repository: MemeRepository = Depends(get_repository(MemeRepository)),
) -> Optional[MemeRead]:
    return await repository.list(
        limit=limit,
        offset=offset,
    )


@router.get(
    '/{meme_id}',
    response_model=MemeRead,
    status_code=status.HTTP_200_OK,
    name='get_meme',
)
async def get_meme(
        meme_id: int,
        repository: MemeRepository = Depends(get_repository(MemeRepository)),
) -> MemeRead:
    try:
        result = await repository.get(model_id=meme_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Meme with ID={meme_id} not found'
        )
    return result


@router.delete(
    '/{meme_id}',
    status_code=status.HTTP_200_OK,
    name='delete_meme',
)
async def delete_meme(
        meme_id: int,
        repository: MemeRepository = Depends(get_repository(MemeRepository)),
) -> None:
    try:
        await repository.get(model_id=meme_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Meme with ID={meme_id} not found'
        )
    return await repository.delete(model_id=meme_id)


@router.put(
    '/{meme_id}',
    status_code=status.HTTP_200_OK,
    name='update_meme',
)
async def update_meme(
        meme_id: int,
        meme_update: MemeUpdate,
        repository: MemeRepository = Depends(get_repository(MemeRepository)),
) -> MemeRead:
    try:
        return await repository.update(model_id=meme_id, model_update=meme_update)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Meme with ID={meme_id} not found'
        )
