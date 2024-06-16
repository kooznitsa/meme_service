from collections.abc import Sequence
import logging
import logging.config
from typing import BinaryIO

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from gateway.api_gateway import APIGateway
from schemas.memes import Meme, MemeCreate, MemeRead, MemeUpdate
from utils.config import settings
from utils.errors import EntityDoesNotExist, UnprocessableEntity

logging.config.dictConfig(settings.LOGGING_CONFIG)

logger = logging.getLogger(__name__)


class MemeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._model = Meme
        self._gateway = APIGateway

    async def _add_to_db(self, new_item: Meme) -> None:
        self.session.add(new_item)
        await self.session.commit()
        await self.session.refresh(new_item)

    async def _upsert(self, name: str, model_create: MemeCreate) -> MemeRead:
        query = select(self._model).where(self._model.name == name)
        result = await self.session.scalars(query)
        result = result.first()
        model_from_orm = self._model.from_orm(model_create)

        if result is None:
            result = model_from_orm

        for k, v in model_from_orm.dict(exclude_unset=True).items():
            setattr(result, k, v)

        return result

    async def create(self, file: BinaryIO, description: str) -> MemeRead | None:
        try:
            minio_obj = await self._gateway.create_or_update(file, description)
            minio_obj.pop('status', None)
            model_create = MemeCreate(**minio_obj)
            name = minio_obj.get('name')
            new_item = await self._upsert(name, model_create)
            await self._add_to_db(new_item)
            logger.info(f'Image added: {name}')
            return new_item
        except UnprocessableEntity:
            raise

    async def get(self, model_id: int) -> MemeRead:
        query = select(self._model).where(self._model.id == model_id)
        if result := await self.session.scalars(query):
            return result.first()
        else:
            raise EntityDoesNotExist

    async def list(self, offset: int = 0, limit: int = 50) -> Sequence[MemeRead]:
        query = select(self._model).offset(offset).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def update(self, model_id: int, model_update: MemeUpdate) -> MemeRead | None:
        if item := await self.get(model_id):
            item_dict = model_update.dict(
                exclude_unset=True,
                exclude={'id'},
            )
            for key, value in item_dict.items():
                setattr(item, key, value)
            await self._add_to_db(item)
            logger.info(f'Image updated: {model_update.name}')
            return item
        else:
            raise EntityDoesNotExist

    async def delete(self, model_id: int) -> None:
        if result := await self.get(model_id):
            await self._gateway.delete_file(result.name)
            await self.session.delete(result)
            await self.session.commit()
            logger.info(f'Image deleted: {result.name}')
        else:
            raise EntityDoesNotExist
